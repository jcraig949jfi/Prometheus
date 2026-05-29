"""test_04: env IDs thread across multiple commands.

Validates the integer-state-ID pattern from the doctrine:
  - First `def f := 2` produces env=N
  - Second command using `env=N` should see `f` in scope
  - Reference to undefined symbol should produce an error message
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.subprocess_session import SubprocessSession


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


def test_04_lean_repl_env_threading():
    if not _have_repl():
        pytest.skip(f"lean-repl not built; missing {REPL_BIN}")

    with SubprocessSession(
        cmd=["lake", "exe", "repl"],
        cwd=REPL_DIR,
        env=_elan_bin_on_path(),
        timeout=120.0,
    ) as sess:
        sess.start()

        # Command 1: define f
        sess.send_json({"cmd": "def f : Nat := 2"})
        r1 = sess.recv_json_until_blank(timeout=90.0)
        env1 = r1["env"]
        assert isinstance(env1, int)
        # No errors expected
        for m in r1.get("messages", []):
            assert m.get("severity") != "error", f"def f errored: {m!r}"

        # Command 2: prove f = 2 *using* env1 — must see f in scope
        sess.send_json({"cmd": "example : f = 2 := rfl", "env": env1})
        r2 = sess.recv_json_until_blank(timeout=90.0)
        env2 = r2["env"]
        assert isinstance(env2, int)
        # No errors expected: f is reachable
        for m in r2.get("messages", []):
            assert m.get("severity") != "error", f"using f errored: {m!r}"

        # Command 3: reference undefined symbol — expect an error message
        sess.send_json({"cmd": "example : undefined_symbol_xyz = 0 := rfl", "env": env1})
        r3 = sess.recv_json_until_blank(timeout=90.0)
        errors = [m for m in r3.get("messages", []) if m.get("severity") == "error"]
        assert errors, f"expected error for undefined symbol; got: {r3!r}"
