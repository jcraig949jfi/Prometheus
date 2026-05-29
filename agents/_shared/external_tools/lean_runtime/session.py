"""LeanSession — typed Lean client over SubprocessSession.

Single per-process state. Use as context manager:

    with LeanSession.open(project_dir=REPL_DIR) as lean:
        r = lean.command("def f : Nat := 2")
        assert isinstance(r, CommandResponse)
        r2 = lean.command("example : f = 2 := rfl", env=r.env)
        ...

`open()` blocks until the Lean process is responsive (validated by a no-op
command). Crashes during interaction surface as `SessionCrashed`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from agents._shared.external_tools.subprocess_session import (
    SubprocessSession,
    SubprocessCrashed,
    SubprocessTimeout,
)
from agents._shared.external_tools.lean_runtime.types import (
    Command,
    ProofStep,
    FileCommand,
    LeanRequest,
    CommandResponse,
    ProofStepResponse,
    ProofFinished,
    ProofGivenUp,
    LeanError,
    SessionCrashed,
    LeanResponse,
)


def _elan_bin_on_path() -> dict[str, str]:
    """Inject ~/.elan/bin into PATH (cross-platform; no-op if absent)."""
    elan_bin = os.path.expanduser("~/.elan/bin")
    env = dict(os.environ)
    if os.path.isdir(elan_bin) and elan_bin not in env.get("PATH", ""):
        env["PATH"] = f"{elan_bin}{os.pathsep}{env.get('PATH', '')}"
    return env


class LeanSession:
    """Typed Lean-repl client.

    Owns one SubprocessSession + the lean-repl protocol on top of it.
    """

    def __init__(self, sess: SubprocessSession):
        self._sess = sess
        self._closed = False

    @classmethod
    def open(
        cls,
        project_dir: str | Path,
        timeout: float = 120.0,
        extra_env: dict[str, str] | None = None,
    ) -> "LeanSession":
        """Spawn `lake exe repl` in `project_dir` and start streaming.

        `project_dir` must contain a `lakefile.toml` or `lakefile.lean`
        and `lean-toolchain`. The caller owns the build (we don't run `lake
        build` here — that's a one-time setup, not per-session).
        """
        env = _elan_bin_on_path()
        if extra_env:
            env.update(extra_env)
        sess = SubprocessSession(
            cmd=["lake", "exe", "repl"],
            cwd=str(project_dir),
            env=env,
            timeout=timeout,
        )
        sess.start()
        return cls(sess)

    # ------------------------------------------------------------------ #
    # Context manager
    # ------------------------------------------------------------------ #

    def __enter__(self) -> "LeanSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._sess.close()

    @property
    def is_alive(self) -> bool:
        return not self._closed and self._sess.is_alive()

    # ------------------------------------------------------------------ #
    # Public typed API
    # ------------------------------------------------------------------ #

    def command(
        self, cmd: str, env: int | None = None, timeout: float | None = None
    ) -> CommandResponse | LeanError | SessionCrashed:
        """Send a top-level Lean declaration; parse response."""
        req = Command(cmd=cmd, env=env)
        return self._send(req, timeout=timeout)

    def apply_tactic(
        self, tactic: str, proof_state: int, timeout: float | None = None
    ) -> ProofStepResponse | ProofFinished | ProofGivenUp | LeanError | SessionCrashed:
        """Send a single tactic against a proof state; parse response."""
        req = ProofStep(tactic=tactic, proof_state=proof_state)
        resp = self._send(req, timeout=timeout)
        if isinstance(resp, ProofStepResponse):
            # Promote terminal states to sentinels for cleaner caller code
            if resp.is_finished and not resp.has_errors:
                return ProofFinished(proof_state=resp.proof_state)
        return resp

    def load_file(
        self, path: str | Path, timeout: float | None = None
    ) -> CommandResponse | LeanError | SessionCrashed:
        """Load a `.lean` file; parse response."""
        req = FileCommand(path=Path(path))
        return self._send(req, timeout=timeout)

    def run_raw(self, payload: dict, timeout: float | None = None) -> dict:
        """Escape hatch: send arbitrary JSON, return raw response dict."""
        self._sess.send_json(payload)
        return self._sess.recv_json_until_blank(timeout=timeout)

    def drain_stderr(self) -> str:
        return self._sess.drain_stderr()

    # ------------------------------------------------------------------ #
    # Internal
    # ------------------------------------------------------------------ #

    def _send(
        self, req: LeanRequest, timeout: float | None = None
    ) -> LeanResponse:
        """Send a typed request; parse response into typed variant."""
        try:
            self._sess.send_json(req.to_payload())
            raw = self._sess.recv_json_until_blank(timeout=timeout)
        except SubprocessCrashed as e:
            return SessionCrashed(detail=str(e))
        except SubprocessTimeout as e:
            return SessionCrashed(detail=f"timeout: {e}")

        return self._parse(req, raw)

    @staticmethod
    def _parse(req: LeanRequest, raw: dict[str, Any]) -> LeanResponse:
        """Discriminate response variant based on request type and raw shape."""
        # Top-level lean-repl error (no env / no proofState in response)
        if "message" in raw and "env" not in raw and "proofState" not in raw:
            from agents._shared.external_tools.lean_runtime.types import Pos
            return LeanError(
                message=raw.get("message", ""),
                pos=Pos.from_dict(raw.get("pos")),
            )

        if isinstance(req, ProofStep):
            return ProofStepResponse.from_dict(raw)
        # Command and FileCommand both return CommandResponse shape
        return CommandResponse.from_dict(raw)
