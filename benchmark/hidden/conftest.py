"""Puts the produced workspace on sys.path so the hidden tests import the agent's code.

The evaluator sets CASE_WORKSPACE. Hidden tests never live inside the workspace and the
agent never sees this directory.
"""
import os
import sys

_ws = os.environ.get("CASE_WORKSPACE")
if _ws and _ws not in sys.path:
    sys.path.insert(0, _ws)
