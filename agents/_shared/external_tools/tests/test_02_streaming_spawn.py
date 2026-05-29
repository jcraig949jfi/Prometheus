"""test_02: SubprocessSession streaming mode — spawn, send, receive lines.

Uses Python itself as a deterministic echo subprocess to exercise streaming
I/O without depending on Lean availability.

Tests:
  - start() spawns process with stdin/stdout pipes
  - send_line() writes to subprocess stdin
  - recv_line() reads from subprocess stdout
  - is_alive() reports correctly
  - close() shuts down cleanly
"""
from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from agents._shared.external_tools.subprocess_session import (
    SubprocessSession,
    SubprocessTimeout,
)


# Python script that reads lines from stdin and echoes them with a prefix.
# Uses explicit readline() to avoid stdin block buffering on Windows.
ECHO_SCRIPT = (
    "import sys\n"
    "while True:\n"
    "    line = sys.stdin.readline()\n"
    "    if not line: break\n"
    "    sys.stdout.write('echo:' + line)\n"
    "    sys.stdout.flush()\n"
)


def test_02a_streaming_echo_roundtrip():
    """Spawn python -c echo script, send a line, receive its echo."""
    with SubprocessSession(
        cmd=[sys.executable, "-u", "-c", ECHO_SCRIPT],
        timeout=10.0,
    ) as sess:
        sess.start()
        assert sess.is_alive()
        sess.send_line("hello")
        reply = sess.recv_line(timeout=5.0)
        assert reply == "echo:hello\n", f"got {reply!r}"


def test_02b_streaming_multiple_roundtrips():
    """Multiple send/recv exchanges through same subprocess."""
    with SubprocessSession(
        cmd=[sys.executable, "-u", "-c", ECHO_SCRIPT],
        timeout=10.0,
    ) as sess:
        sess.start()
        for i in range(5):
            sess.send_line(f"line{i}")
            reply = sess.recv_line(timeout=5.0)
            assert reply == f"echo:line{i}\n", f"iteration {i}: got {reply!r}"


def test_02c_recv_timeout_on_silent_subprocess():
    """SubprocessTimeout when nothing arrives within window."""
    # Sleep script: stay alive but never write to stdout
    SLEEP_SCRIPT = "import time, sys; sys.stdin.read(); time.sleep(60)"
    with SubprocessSession(
        cmd=[sys.executable, "-c", SLEEP_SCRIPT],
        timeout=10.0,
    ) as sess:
        sess.start()
        with pytest.raises(SubprocessTimeout):
            sess.recv_line(timeout=1.0)


def test_02d_close_kills_process():
    """close() terminates subprocess that would otherwise run forever."""
    LOOP_SCRIPT = "import time\nwhile True: time.sleep(1)"
    sess = SubprocessSession(
        cmd=[sys.executable, "-u", "-c", LOOP_SCRIPT],
        timeout=10.0,
    )
    sess.start()
    assert sess.is_alive()
    sess.close()
    assert not sess.is_alive()
