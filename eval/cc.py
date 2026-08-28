"""Driver for the Claude Code CLI in headless mode.

Both arms go through this one function, so neither can quietly get different tooling,
a different model or different permissions. The only thing an arm chooses is the prompt
and how many times it calls.

The CLI reports duration, turns, token usage and an equivalent API cost per call, so the
metrics table is metered rather than estimated. Running on a Claude subscription costs
nothing incremental; `total_cost_usd` is what the same work would cost at API rates.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

# Tools the agent may use inside its sandbox: read, write, search, run tests. Nothing else
# is needed to implement a ticket.
ALLOWED_TOOLS = ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "TodoWrite"]

# Denied outright, for both arms equally, in three groups:
#   - network: the experiment must not depend on what a web search returned on the day
#   - delegation: "one coding agent" must stay true of the baseline
#   - anything that can act outside the sandbox (schedules, messages, notifications,
#     worktrees). Ground rule 4: consequential actions stay sandboxed.
# Verified absent from the session's tool list at run time; MCP servers are excluded
# separately with --strict-mcp-config.
DENIED_TOOLS = [
    "WebSearch", "WebFetch",
    "Task", "Skill", "Workflow", "ToolSearch", "ListAgents", "TaskOutput", "TaskStop",
    "SendMessage", "PushNotification", "RemoteTrigger", "Monitor", "DesignSync",
    "CronCreate", "CronDelete", "CronList", "ScheduleWakeup",
    "EnterWorktree", "ExitWorktree", "ReportFindings", "NotebookEdit", "PowerShell",
]

DEFAULT_TIMEOUT = 900


def claude_executable() -> str:
    """Resolve the CLI, preferring the real binary over a shell shim.

    On Windows npm installs `claude.CMD`, and cmd.exe re-parses the command line: an
    argument containing a newline is truncated at the first newline and every flag after
    it is silently dropped. Our prompts are multi-line, so going through the shim loses
    --output-format, --allowedTools and --strict-mcp-config without any error -- the run
    still appears to work while producing no telemetry and no sandbox. Call the native
    executable directly instead, where argv is passed through intact.
    """
    found = shutil.which("claude")
    if found and os.path.splitext(found)[1].lower() in (".cmd", ".bat", ".ps1"):
        native = os.path.join(
            os.path.dirname(found),
            "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe",
        )
        if os.path.exists(native):
            return native
    if not found:
        raise RuntimeError(
            "the `claude` CLI is not on PATH. Install Claude Code, or see REPRODUCTION.md "
            "for the API-key route."
        )
    return found


@dataclass
class AgentCall:
    """One headless agent invocation, with everything needed to reproduce and audit it."""

    step: str
    prompt: str
    system_prompt: str
    cwd: str
    model: str
    result: str = ""
    is_error: bool = False
    num_turns: int = 0
    duration_ms: int = 0
    cost_usd: float = 0.0
    usage: dict = field(default_factory=dict)
    stream: list = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "step": self.step,
            "model": self.model,
            "is_error": self.is_error,
            "num_turns": self.num_turns,
            "duration_ms": self.duration_ms,
            "cost_usd": self.cost_usd,
            "usage": self.usage,
        }


def run_agent(
    step: str,
    prompt: str,
    system_prompt: str,
    cwd: str,
    model: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> AgentCall:
    """Run one headless Claude Code session with `cwd` as its whole world."""
    call = AgentCall(
        step=step, prompt=prompt, system_prompt=system_prompt, cwd=cwd, model=model
    )

    cmd = [
        claude_executable(),
        "-p",
        prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--append-system-prompt", system_prompt,
        "--permission-mode", "bypassPermissions",
        "--allowedTools", " ".join(ALLOWED_TOOLS),
        "--disallowedTools", ",".join(DENIED_TOOLS),
        # Do not inherit the operator's personal settings, hooks, plugins or MCP servers:
        # a judge on a clean machine has none of them, and the run must not depend on them.
        "--setting-sources", "",
        "--strict-mcp-config",
    ]

    env = dict(os.environ)
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            # Without this the CLI waits on inherited stdin, and on Windows the event
            # stream never reaches us -- a run that looks like it cost nothing.
            stdin=subprocess.DEVNULL,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        call.is_error = True
        call.result = "TIMEOUT after %ds" % timeout
        return call

    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        call.stream.append(event)
        if event.get("type") == "result":
            call.result = str(event.get("result", ""))
            call.is_error = bool(event.get("is_error")) or event.get("subtype") != "success"
            call.num_turns = int(event.get("num_turns") or 0)
            call.duration_ms = int(event.get("duration_ms") or 0)
            call.cost_usd = float(event.get("total_cost_usd") or 0.0)
            call.usage = event.get("usage") or {}

    if not call.stream:
        call.is_error = True
        call.result = (proc.stderr or "no output from claude CLI")[:2000]

    return call


def extract_json(text: str) -> dict | None:
    """Pull the first JSON object out of a model's final message.

    Models sometimes wrap JSON in a fence or add a sentence around it. Being tolerant here
    is not the same as being tolerant about the content: a call whose output cannot be
    parsed is recorded as a parse failure, never silently treated as "no findings".
    """
    if not text:
        return None
    fenced = text.split("```")
    candidates = [text] + [
        block[4:] if block.lower().startswith("json") else block for block in fenced
    ]
    for candidate in candidates:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end <= start:
            continue
        try:
            parsed = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def write_stream(call: AgentCall, path: str) -> None:
    """Persist the raw event stream -- this is the trajectory evidence."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for event in call.stream:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
