"""test_03: SubprocessSession drives `lake exe repl` for one JSON round-trip.

This is the bridge from generic streaming (test_02) to actual Lean interaction.
Spawns `lake exe repl` from the cloned lean-repl repo, sends one command
(`def f := 2`), parses the JSON response, asserts `env` returned.

Generous timeout: Lean cold-start can take 10s+; first run may pull toolchain.
"""
from __future__ import annotations

import os
import shutil
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.subprocess_session import (
    SubprocessSession,
    SubprocessCrashed,
    SubprocessTimeout,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _elan_bin_on_path():
    elan_bin = os.path.expanduser("~/.elan/bin")
    env = dict(os.environ)
    if os.path.isdir(elan_bin) and elan_bin not in env.get("PATH", ""):
        env["PATH"] = f"{elan_bin}{os.pathsep}{env.get('PATH', '')}"
    return env


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_03_lean_repl_handshake():
    """Send `def f := 2` to `lake exe repl`; receive JSON with env id."""
    if not _have_repl():
        pytest.skip(f"lean-repl not built; missing {REPL_BIN}")

    env = _elan_bin_on_path()
    with SubprocessSession(
        cmd=["lake", "exe", "repl"],
        cwd=REPL_DIR,
        env=env,
        timeout=120.0,  # cold start can be slow
    ) as sess:
        sess.start()
        assert sess.is_alive(), f"repl process died on spawn; stderr={sess.drain_stderr()!r}"

        sess.send_json({"cmd": "def f := 2"})
        try:
            response = sess.recv_json_until_blank(timeout=90.0)
        except (SubprocessCrashed, SubprocessTimeout) as e:
            stderr = sess.drain_stderr()
            pytest.fail(f"lean-repl handshake failed: {e}; stderr={stderr!r}")

    # `def f := 2` should produce an env id and no errors
    assert "env" in response, f"expected 'env' in response, got: {response!r}"
    assert isinstance(response["env"], int), f"expected int env, got: {response['env']!r}"
    # No error severity messages
    for msg in response.get("messages", []):
        assert msg.get("severity") != "error", f"unexpected error: {msg!r}"
