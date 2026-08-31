# Video script — 5 minutes, keyed to the deck

Source on screen: `ops/slides/deck.html`. 16 slides. Nothing to run, no terminal, no live demo.
You scroll and you talk. **The words on screen carry the detail — you say less than you think.**

Measured at speaking pace: **4:34**, pauses included. That leaves 26 seconds of slack against
the 5:00 cap, which is your margin for breathing and stumbling. The cuts are already made, not offered.

_Was 4:29. The 30 Aug ablation added about five seconds — one extra line on slide 12 and a longer
closing number on slide 16. If you run long, slide 16's "twelve to fifteen" clause is the one to
drop; the pooled range is in the README and the changelog either way._

---

## Set up before you record

1. Open `ops/slides/deck.html` in Chrome.
2. Zoom until exactly one slide fills the window (`Ctrl` and `-`, usually two or three presses at 1080p).
3. Scroll with **Page Down** — one press per slide. Don't drag the scrollbar, it wobbles.
4. Start the recording on slide 1 already in frame. Don't film yourself finding it.

Do a silent scroll through all 16 first so your hand knows the rhythm.

## Four slides are real files. Do not read them out.

Slides **3, 6, 10 and 13** put a real artifact on screen. Let people read. Never read a table
aloud, and never say a percentage that's sitting in a cell — the screen has already said it.
On slide 6 don't read the row names (one is `002-idempotency-key`, which you'd trip on).
On slide 13 don't read the percentages. It's "fourteen out of eighteen", every time.

## Words that are banned

You never have to say any of these: *idempotency, assertion, harness, ablation, invariant.*
And never say **baseline** — it's "the normal way" or "one AI on its own".

**Two names, and only these two.** The bug is **the double charge**. The thing you removed is
**the gate**. Don't call it a rule, a check, or a safeguard — "rule" means one of the eighteen
and nothing else, all the way through.

---

# Part 1 — the problem, and what one AI on its own does
**Slides 1 to 7 · 1:39**

### Slide 1 — me, no other developer, no tester · 13s
- "I build software on my own. No other developer, no tester."
- "AI writes most of my code now. And the only thing telling me it's done is the AI that just wrote it."

### Slide 2 — three jobs, and where this ends up · 15s
- "Three jobs for one AI. A password page, a payment page, one that imports a spreadsheet."
- "Where it ends up: a second AI that finds bugs but can't touch the code, and a third that fixes them."

### Slide 3 — the real ticket · 13s + 3s pause
*Real file. Stop talking and let them read it.*
- "A real ticket, the way I'd write one. People forget their password, we reset it by hand, four a week."
- "Three steps. Not a word about what could go wrong. That's normal."

### Slide 4 — the 18 rules · 12s
- "Before any of that I wrote eighteen rules the code has to obey. Links expire. Two payments at once, only one goes through."
- "I'll call that last one the double charge."

### Slide 5 — never said, never shown · 16s
- "I never showed them to it. Hand an AI the marking scheme and it just does the marking scheme."
- "And that's not me being unfair. Somebody says 'build me a login page', and every rule stays in their head."

### Slide 6 — the real run, 11 of 18 · 15s + 4s pause
*Real file. Don't read the rows.*
- "One AI, one go, no review. What most people are doing right now."
- "Three jobs. Under thirty seconds and about eight cents each."
- "It did everything the ticket asked. Eleven of the eighteen rules pass. Seven are broken."

### Slide 7 — the three you just read · 8s
- "All three you just read, including the double charge. Two payments land together, both go through."
- "And four more underneath."

---

# Part 2 — what I built
**Slides 8 to 10 · 0:45**

### Slide 8 — the checker · 13s
- "So I added a second AI. I call it the checker, and its only job is to attack that code."
- "It can't touch anything. All it can do is write a list."

### Slide 9 — the fixer · 12s
- "The list goes to a third AI. That's the fixer, and that one changes the code."
- "Finding the problem and fixing it are two jobs, so they're two AIs."

### Slide 10 — the report · 17s + 3s pause
*Real file. Let them read before you speak.*
- "What comes back isn't a tick. It's this."
- "Four problems raised. Five still open after the repair. It went up, not down, and it says so."
- "And the top line: this is a recommendation, not an approval. It doesn't decide. I do."

---

# Part 3 — the numbers, and what's underneath them
**Slides 11 to 12 · 0:47**

### Slide 11 — the comparison · 24s
*Real file. Don't read the table.*
- "Same three jobs both ways, same model writing the code. A script scores both, and it can't see which version it's grading."
- "One AI passes eleven. Three AIs pass fourteen."
- "Four runs of the normal one, three of mine. Eleven every time on the left."
- "That's the change: a reviewer that isn't allowed to edit, a repair step, and a second look."

### Slide 12 — same total, different behaviour · 23s
*Slow down. This is the one nobody else will have.*
- "This is the bit I nearly missed."
- "Fourteen, three times. But it isn't the same fourteen."
- "Two runs fix four and break one. The third fixes three, breaks nothing."
- "So I ran the same pipeline three more times. Twelve. And fifteen."
- "It doesn't reliably fix four. It reliably fixes two — and the total was luck."

---

# Part 4 — the log, and the one I threw away
**Slides 13 to 16 · 1:18**

### Slide 13 — the changelog · 14s + 3s pause
*Real file. Don't read the percentages.*
- "The only reason I found that is I'd written every run down as I went."
- "Every experiment I ran is in there. The last one is me pulling a step out to see if it was doing anything. It wasn't."

### Slide 14 — the gate · 24s
- "Sometimes the checker is certain about a problem that isn't there, and the fixer believes it. So: prove it first."
- "Four broken became five, six and eight. Same setup, three runs. It stopped being a number I could trust."
- "It blocked two findings that were right. And it hadn't stopped the wrong one either. One in three, both ways."

### Slide 15 — a repair can break a working rule · 20s
- "Here's what I got wrong. The gate was grading how well the checker argued."
- "That's the one thing AI is brilliant at faking."
- "And the finding that hurt me was wrong in a completely different way. Acting on it broke this rule. And breaking this rule is a double charge."

### Slide 16 — the checker looks again · 17s
- "So don't grade the argument. After every repair, look at the code again."
- "That version passes fourteen, up from eleven. Run the scoring six times and it lands between twelve and fifteen — every one of them above eleven. It still breaks one, in two runs out of three."
- "Three jobs isn't many. That's the first thing I'd change."

---

## Three things not to say

- Don't say it "works" or is "production ready". It **passes** fourteen of the eighteen, up from eleven, and in two runs out of three it breaks one that was already working. Say that.
- Don't say "on average" about the normal way — the baseline really does hit eleven every run, and that's stronger. **Do** say it about mine: twelve to fifteen across six runs. The flat fourteen was three lucky draws and the repo now proves it. **Do** say it about the gate — five, six and eight are three real runs.
- Don't pretend three jobs is enough. Say you spent the time running them over and over instead of adding more.

## If you still run long

You have 22 seconds in hand, so you probably won't need these. In order:

1. Slide 15's second line
2. Slide 11's third line
3. Slide 5's second line
4. Slide 7's second line

**Never cut:** slide 10, slide 12, or slide 14. Those three are what the entry is.
