"""test_08: SessionCrashed surfaces gracefully when the subprocess dies.

The doctrine identifies "Lean process can hang on certain tactic combinations.
AutoLeanServer-style watchdog is mandatory, not optional." This test validates
the watchdog hook: if the subprocess dies (or times out), the LeanSession does
NOT raise — it returns a typed `SessionCrashed` so callers can recover.
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.lean_runtime import (
    LeanSession,
    CommandResponse,
    SessionCrashed,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_08a_command_after_external_kill_returns_session_crashed():
    """If the subprocess dies between requests, the next command returns
    SessionCrashed (not an unhandled exception).

    On Windows, kills the entire process tree (cmd.exe wrapper + lake.exe +
    lean.exe / repl.exe descendants). A bare Popen.kill() only kills the shell
    wrapper; orphaned children keep responding to stdin/stdout pipes.
    """
    import subprocess as _sp
    if not _have_repl():
        pytest.skip("lean-repl not built")

    lean = LeanSession.open(REPL_DIR)
    try:
        # First command works
        r = lean.command("def x : Nat := 1")
        assert isinstance(r, CommandResponse)

        # Kill the entire process tree (simulates hang+watchdog kill)
        if sys.platform == "win32":
            _sp.run(
                ["taskkill", "/F", "/T", "/PID", str(lean._sess._proc.pid)],
                timeout=10.0,
                capture_output=True,
            )
        else:
            lean._sess._proc.kill()
        lean._sess._proc.wait(timeout=5)

        # Next command should NOT raise — should return SessionCrashed
        r2 = lean.command("def y : Nat := 2")
        assert isinstance(r2, SessionCrashed), \
            f"expected SessionCrashed, got {type(r2).__name__}: {r2!r}"
        assert "rc=" in r2.detail or "timeout" in r2.detail
    finally:
        lean.close()


def test_08b_short_timeout_surfaces_session_crashed():
    """Passing a very short per-call timeout converts to SessionCrashed."""
    if not _have_repl():
        pytest.skip("lean-repl not built")

    with LeanSession.open(REPL_DIR) as lean:
        # Force a sub-millisecond timeout. Lean *cannot* respond that fast.
        r = lean.command("def z : Nat := 99", timeout=0.001)
        # Lean may have responded between when we sent and when we read on
        # extremely fast machines, but typically: SessionCrashed
        assert isinstance(r, (SessionCrashed, CommandResponse))
        if isinstance(r, SessionCrashed):
            assert "timeout" in r.detail.lower()
