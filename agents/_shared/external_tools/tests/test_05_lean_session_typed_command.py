"""test_05: LeanSession.command() returns typed CommandResponse.

Reuses the same lean-repl backend as test_03/04 but goes through the typed
Layer 1 API. Validates:
  - LeanSession.open() returns a started session
  - command() returns CommandResponse with parsed env / messages / sorries
  - env-threading via env= kwarg works through typed path
  - has_errors flag correctly identifies error messages
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.lean_runtime import (
    LeanSession,
    CommandResponse,
    Message,
    LeanError,
    SessionCrashed,
)


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPL_DIR = os.path.join(REPO_ROOT, "external_deps", "repl")
REPL_BIN = os.path.join(REPL_DIR, ".lake", "build", "bin", "repl.exe")


def _have_repl() -> bool:
    return os.path.isfile(REPL_BIN) or os.path.isfile(REPL_BIN.replace(".exe", ""))


def test_05a_typed_command_returns_command_response():
    if not _have_repl():
        pytest.skip(f"lean-repl not built; missing {REPL_BIN}")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("def f : Nat := 2")
        assert isinstance(r, CommandResponse), f"expected CommandResponse, got {type(r).__name__}: {r!r}"
        assert isinstance(r.env, int) and r.env >= 0
        assert not r.has_errors, f"unexpected errors: {r.messages!r}"


def test_05b_typed_command_threads_env():
    if not _have_repl():
        pytest.skip(f"lean-repl not built; missing {REPL_BIN}")

    with LeanSession.open(REPL_DIR) as lean:
        r1 = lean.command("def g : Nat := 7")
        assert isinstance(r1, CommandResponse)
        r2 = lean.command("example : g = 7 := rfl", env=r1.env)
        assert isinstance(r2, CommandResponse), f"got {type(r2).__name__}: {r2!r}"
        assert not r2.has_errors, f"using g via env={r1.env} errored: {r2.messages!r}"


def test_05c_typed_command_surfaces_error():
    if not _have_repl():
        pytest.skip(f"lean-repl not built; missing {REPL_BIN}")

    with LeanSession.open(REPL_DIR) as lean:
        r = lean.command("example : nonexistent_xyz = 0 := rfl")
        assert isinstance(r, CommandResponse), f"got {type(r).__name__}: {r!r}"
        assert r.has_errors, f"expected error, got: {r!r}"
        errs = [m for m in r.messages if m.severity == "error"]
        assert errs, "no error-severity message found"
        assert isinstance(errs[0], Message)
