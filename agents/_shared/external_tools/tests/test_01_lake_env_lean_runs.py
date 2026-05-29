"""test_01: `lake env lean --version` runs cleanly under SubprocessSession.

Foundational test. Verifies that:
  - SubprocessSession can spawn a process
  - The process exits cleanly
  - Stdout is captured

This is the bedrock for everything else. If Lean toolchain isn't on PATH or
the SubprocessSession class doesn't work, every later test fails too.
"""
from __future__ import annotations

import os
import shutil
import sys
import pytest

# Ensure repo root on sys.path so `agents._shared` resolves
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.subprocess_session import SubprocessSession


def _elan_bin_on_path():
    """Inject ~/.elan/bin into PATH for the test's subprocess child."""
    elan_bin = os.path.expanduser("~/.elan/bin")
    env = dict(os.environ)
    if os.path.isdir(elan_bin) and elan_bin not in env.get("PATH", ""):
        env["PATH"] = f"{elan_bin}{os.pathsep}{env.get('PATH', '')}"
    return env


def test_01_lake_env_lean_runs():
    """Foundational: lake env lean --version succeeds, prints version string."""
    if shutil.which("lake") is None and not os.path.isfile(os.path.expanduser("~/.elan/bin/lake.exe")):
        pytest.skip("lake not available; install elan + lean toolchain")

    env = _elan_bin_on_path()
    with SubprocessSession(
        cmd=["lake", "--version"],
        cwd=os.getcwd(),
        env=env,
        timeout=30.0,
    ) as sess:
        stdout, stderr, rc = sess.run_to_completion()

    assert rc == 0, f"lake --version exited {rc}; stderr={stderr!r}"
    assert "Lake" in stdout or "Lean" in stdout, f"expected 'Lake' or 'Lean' in stdout, got: {stdout!r}"
