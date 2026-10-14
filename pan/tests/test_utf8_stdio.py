"""Controls for pan.__main__.utf8_stdio (piped CLI output on Windows).

POSITIVE  with utf8_stdio, a child process whose stdout is a pipe prints U+2011 and exits 0
NEGATIVE  without it, the same child fails with UnicodeEncodeError (skipped where the platform's
          piped default is already UTF-8, so the control could not show the defect)
CHEAT     a stream that is already UTF-8 is left alone, and a stream that cannot be reconfigured
          (io.StringIO) does not raise
"""
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pan.__main__ import utf8_stdio

ROOT = Path(__file__).resolve().parents[2]
SNIPPET = "print('a\\u2011b')"


def child(code):
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, timeout=120)


def piped_default_is_utf8():
    r = child("import sys; print(sys.stdout.encoding)")
    return r.stdout.decode().strip().lower().replace("-", "") == "utf8"


def test_positive_piped_unicode_prints():
    r = child("from pan.__main__ import utf8_stdio; utf8_stdio(); " + SNIPPET)
    assert r.returncode == 0, r.stderr.decode(errors="replace")
    assert r.stdout.decode("utf-8").strip() == "a‑b"


def test_negative_default_fails():
    if piped_default_is_utf8():
        pytest.skip("piped stdout is already UTF-8 here; the defect cannot occur")
    r = child(SNIPPET)
    assert r.returncode != 0 and b"UnicodeEncodeError" in r.stderr


class _Stream:
    def __init__(self, encoding):
        self.encoding = encoding
        self.calls = []

    def reconfigure(self, **kw):
        self.calls.append(kw)


def test_cheat_leaves_utf8_alone_and_tolerates_plain_streams():
    s = _Stream("UTF-8")
    utf8_stdio([s])
    assert s.calls == []
    c = _Stream("cp1252")
    utf8_stdio([c])
    assert c.calls == [dict(encoding="utf-8", errors="replace")]
    utf8_stdio([io.StringIO()])    # has no reconfigure: must not raise
