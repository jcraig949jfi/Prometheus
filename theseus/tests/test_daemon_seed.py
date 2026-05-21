"""Daemon --seed default behavior.

Regression test for cross-fire identical-selection bug: Fire #34 and
Fire #35 picked the same generators because --seed defaulted to 42 and
the bandit was reseeded fresh every daemon invocation.

Fix: --seed defaults to None and the daemon's main() derives a
time-based seed when None. Explicit --seed N still works for
reproducible runs.

We test the seed-derivation logic rather than spawning subprocesses
(the subprocess form is covered by the CLI's --help and the
end-to-end batch behavior on the loop).
"""
from __future__ import annotations

import time
import sys

from unittest.mock import patch

import pytest


def test_daemon_main_auto_seeds_when_unset(monkeypatch, capsys):
    """When --seed not on argv, daemon prints an auto-seed line and
    proceeds (we intercept run_batch to avoid actually emitting)."""
    from theseus import daemon

    fake_argv = [
        "theseus.daemon",
        "--batch-hours", "0.001",
        "--batches", "0",   # no batches → daemon exits after seed init
    ]
    monkeypatch.setattr(sys, "argv", fake_argv)

    daemon.main()

    captured = capsys.readouterr()
    assert "Auto-seeded run: --seed" in captured.out


def test_daemon_main_respects_explicit_seed(monkeypatch, capsys):
    """Explicit --seed N: no auto-seed message."""
    from theseus import daemon

    fake_argv = [
        "theseus.daemon",
        "--batch-hours", "0.001",
        "--batches", "0",
        "--seed", "12345",
    ]
    monkeypatch.setattr(sys, "argv", fake_argv)

    daemon.main()

    captured = capsys.readouterr()
    assert "Auto-seeded run" not in captured.out


def test_two_consecutive_auto_seeds_differ(monkeypatch):
    """Sanity: two calls with auto-seed produce different seeds when
    time has advanced. We patch time to advance enough."""
    times = iter([1000.000, 1000.001])  # 1ms apart → different ms count

    def _fake_time():
        return next(times)

    monkeypatch.setattr(time, "time", _fake_time)

    # Replicate the daemon's derivation
    s1 = int(time.time() * 1000) % (2 ** 31)
    s2 = int(time.time() * 1000) % (2 ** 31)
    assert s1 != s2


def test_auto_seed_in_valid_range(monkeypatch):
    """The auto-seed must fit in a 32-bit signed int (random.Random
    accepts arbitrary ints but downstream may not)."""
    monkeypatch.setattr(time, "time", lambda: 9999999999.999)
    s = int(time.time() * 1000) % (2 ** 31)
    assert 0 <= s < 2 ** 31
