"""Layer 0: generic stateful subprocess client.

Driven by the TDD cascade in `tests/test_01_*` through `tests/test_12_*`.
Generalizes across Lean, Isabelle, Coq, Z3 — any JSON-over-stdio tool.

Phase 1 (test_01): one-shot execution, capture all output. DONE.
Phase 2 (test_02+): persistent streaming, send-then-receive, JSON-RPC.

Cross-platform-safe lifecycle: no tempdir cloning, kill on shutdown with
timeout-fallback wait, no rmtree calls that fail on Windows file locks.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SubprocessTimeout(Exception):
    """Raised when a streaming send/receive exceeds its timeout."""


class SubprocessCrashed(Exception):
    """Raised when the subprocess exits unexpectedly during streaming."""


class SubprocessSession:
    """Stateful subprocess wrapper. Cross-platform-safe lifecycle.

    Two modes:
      - One-shot: `run_to_completion()` — for short commands like `--version`.
      - Streaming: `start()` then `send_line()` / `recv_line()` / `send_json()`
        / `recv_json()` — for persistent JSON-RPC servers like `lake exe repl`.

    Lifecycle: use as context manager. `__exit__` kills the process if alive,
    waits up to 5s, drops the handle. No tempdir cleanup (we never create one).
    """

    def __init__(
        self,
        cmd: list[str],
        cwd: str | Path | None = None,
        env: dict[str, str] | None = None,
        timeout: float = 60.0,
        shell: bool | None = None,
    ):
        self.cmd = list(cmd)
        self.cwd = str(cwd) if cwd is not None else None
        self.env = env if env is not None else None
        self.timeout = float(timeout)
        # `shell` auto-detect: on Windows, use shell=True only for known shims
        # (lake.cmd, lake.exe with no path) where the shim needs cmd.exe lookup.
        # For direct executables like python.exe, shell=False keeps the pipe
        # connection direct, which is required for streaming stdin/stdout.
        if shell is None:
            first = self.cmd[0].lower() if self.cmd else ""
            self._shell = sys.platform == "win32" and (
                first in ("lake", "lean", "elan")  # bare-name shims
                or first.endswith(".cmd") or first.endswith(".bat")
            )
        else:
            self._shell = shell
        self._proc: subprocess.Popen | None = None
        self._stdout_queue: queue.Queue[str] | None = None
        self._stderr_buf: list[str] = []
        self._reader_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None
        self._stopped = threading.Event()

    # --------------------------------------------------------------------- #
    # Lifecycle
    # --------------------------------------------------------------------- #

    def __enter__(self) -> "SubprocessSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _spawn(self) -> subprocess.Popen:
        """Spawn the subprocess. Cross-platform: on Windows uses cmd.exe shim
        so shims like `lake.exe` (elan shim) resolve correctly."""
        kwargs: dict[str, Any] = dict(
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered (only meaningful in text mode)
            # Lean (and most modern theorem provers) emit unicode (∀, ∃, →, λ).
            # Force UTF-8 on every pipe; never inherit cp1252 from Windows locale.
            encoding="utf-8",
            errors="replace",
        )
        if sys.platform == "win32" and self._shell:
            cmdline = subprocess.list2cmdline(self.cmd)
            return subprocess.Popen(cmdline, shell=True, **kwargs)
        else:
            return subprocess.Popen(self.cmd, shell=False, **kwargs)

    # --------------------------------------------------------------------- #
    # One-shot mode (test_01)
    # --------------------------------------------------------------------- #

    def run_to_completion(self) -> tuple[str, str, int]:
        """Run the command to completion, return (stdout, stderr, returncode)."""
        proc = self._spawn()
        self._proc = proc
        try:
            stdout, stderr = proc.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return stdout or "", (stderr or "") + "\n[SubprocessSession: TIMEOUT]", -1
        return stdout or "", stderr or "", proc.returncode

    # --------------------------------------------------------------------- #
    # Streaming mode (test_02+)
    # --------------------------------------------------------------------- #

    def start(self) -> None:
        """Spawn process and start background reader threads.

        After start(), use send_line/recv_line for line-based stdio or
        send_json/recv_json for JSON-RPC.
        """
        if self._proc is not None:
            raise RuntimeError("SubprocessSession already started")
        self._proc = self._spawn()
        self._stdout_queue = queue.Queue()
        self._stopped.clear()

        def _reader_stdout():
            try:
                for line in self._proc.stdout:  # type: ignore[union-attr]
                    if self._stopped.is_set():
                        break
                    self._stdout_queue.put(line)  # type: ignore[union-attr]
            except Exception:
                pass

        def _reader_stderr():
            try:
                for line in self._proc.stderr:  # type: ignore[union-attr]
                    if self._stopped.is_set():
                        break
                    self._stderr_buf.append(line)
            except Exception:
                pass

        self._reader_thread = threading.Thread(target=_reader_stdout, daemon=True)
        self._reader_thread.start()
        self._stderr_thread = threading.Thread(target=_reader_stderr, daemon=True)
        self._stderr_thread.start()

    def send_line(self, line: str) -> None:
        """Send a single line (with newline appended). Subprocess must be started."""
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("SubprocessSession not started (call .start())")
        if self._proc.poll() is not None:
            raise SubprocessCrashed(
                f"subprocess exited rc={self._proc.returncode}; "
                f"stderr={''.join(self._stderr_buf[-5:])!r}"
            )
        text = line if line.endswith("\n") else line + "\n"
        self._proc.stdin.write(text)
        self._proc.stdin.flush()

    def recv_line(self, timeout: float | None = None) -> str:
        """Receive one line from stdout. Blocks until line available or timeout."""
        if self._stdout_queue is None:
            raise RuntimeError("SubprocessSession not started")
        try:
            line = self._stdout_queue.get(timeout=timeout if timeout is not None else self.timeout)
            return line
        except queue.Empty:
            # Distinguish "subprocess crashed" from "subprocess just slow"
            if self._proc is not None and self._proc.poll() is not None:
                raise SubprocessCrashed(
                    f"subprocess exited rc={self._proc.returncode}; "
                    f"stderr={''.join(self._stderr_buf[-5:])!r}"
                )
            raise SubprocessTimeout(
                f"no output within {timeout if timeout is not None else self.timeout}s"
            )

    def send_json(self, payload: dict, terminator: str = "\n\n") -> None:
        """Send a JSON payload. Default terminator is blank line (lean-repl convention).

        Raises SubprocessCrashed if the subprocess has already died or the
        stdin pipe is broken.
        """
        text = json.dumps(payload, ensure_ascii=False)
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("SubprocessSession not started")
        if self._proc.poll() is not None:
            raise SubprocessCrashed(
                f"subprocess exited rc={self._proc.returncode}; "
                f"stderr={''.join(self._stderr_buf[-5:])!r}"
            )
        try:
            self._proc.stdin.write(text + terminator)
            self._proc.stdin.flush()
        except (OSError, BrokenPipeError) as e:
            # Pipe broke mid-write — process died between poll() and write()
            raise SubprocessCrashed(
                f"stdin write failed ({type(e).__name__}: {e}); "
                f"rc={self._proc.poll()}; "
                f"stderr={''.join(self._stderr_buf[-5:])!r}"
            )

    def recv_json_until_blank(self, timeout: float | None = None) -> dict:
        """Receive lines until a blank-line terminator, parse the accumulated text as JSON.

        This matches the lean-repl output convention: response is JSON
        followed by a blank line.
        """
        deadline = time.monotonic() + (timeout if timeout is not None else self.timeout)
        accumulated: list[str] = []
        while True:
            remaining = max(0.05, deadline - time.monotonic())
            try:
                line = self.recv_line(timeout=remaining)
            except SubprocessTimeout:
                raise SubprocessTimeout(
                    f"timed out waiting for JSON response; partial: {''.join(accumulated)!r}"
                )
            if line.strip() == "":
                # Blank line = response terminator
                if accumulated:
                    break
                # Otherwise eat leading blank lines
                continue
            accumulated.append(line)
        joined = "".join(accumulated)
        return json.loads(joined)

    def drain_stderr(self) -> str:
        return "".join(self._stderr_buf)

    # --------------------------------------------------------------------- #
    # Shutdown
    # --------------------------------------------------------------------- #

    def close(self) -> None:
        """Cross-platform-safe shutdown. No tempdir cleanup (we never create one).

        On Windows with shell=True, `Popen.kill()` only kills the cmd.exe wrapper;
        descendants (lake.exe, lean.exe, repl.exe) survive and keep responding.
        Use `taskkill /F /T /PID` to kill the entire process tree.
        """
        if self._proc is None:
            return
        self._stopped.set()
        if self._proc.poll() is None:
            try:
                if self._proc.stdin is not None and not self._proc.stdin.closed:
                    self._proc.stdin.close()
            except Exception:
                pass
            if sys.platform == "win32" and self._shell:
                # Tree-kill: kills cmd.exe AND every descendant (lake → repl chain)
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self._proc.pid)],
                        timeout=10.0,
                        capture_output=True,
                    )
                except Exception:
                    pass
            else:
                self._proc.kill()
            try:
                self._proc.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                pass
        # Reader threads are daemon=True; they'll exit on process death
        self._proc = None
        self._stdout_queue = None
        self._reader_thread = None
        self._stderr_thread = None

    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None
