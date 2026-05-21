"""Unit tests for theseus.scripts._backoff helpers."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from theseus.scripts._backoff import (
    is_rate_limited,
    sleep_for_retry,
    with_429_retry,
)


class _FakeResponse:
    def __init__(self, status_code: int, retry_after: str | None = None):
        self.status_code = status_code
        self.headers = {"Retry-After": retry_after} if retry_after else {}


class _FakeHTTPError(Exception):
    def __init__(self, status_code: int, retry_after: str | None = None):
        self.status_code = status_code
        self.response = _FakeResponse(status_code, retry_after)


def test_is_rate_limited_detects_429_via_status_code_attr():
    exc = _FakeHTTPError(429)
    is_rl, ra = is_rate_limited(exc)
    assert is_rl is True
    assert ra is None


def test_is_rate_limited_detects_503_via_response_attr():
    class _Wrapped(Exception):
        def __init__(self):
            self.response = _FakeResponse(503)
    is_rl, ra = is_rate_limited(_Wrapped())
    assert is_rl is True


def test_is_rate_limited_extracts_retry_after():
    exc = _FakeHTTPError(429, retry_after="42")
    is_rl, ra = is_rate_limited(exc)
    assert is_rl is True
    assert ra == 42.0


def test_is_rate_limited_returns_false_for_other_codes():
    exc = _FakeHTTPError(500)
    is_rl, _ = is_rate_limited(exc)
    assert is_rl is False


def test_is_rate_limited_returns_false_for_unrelated_exception():
    is_rl, _ = is_rate_limited(ValueError("nope"))
    assert is_rl is False


def test_sleep_for_retry_honors_retry_after(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    delay = sleep_for_retry(attempt=0, base_delay=30.0, retry_after=7.5)
    assert delay == 7.5
    assert slept == [7.5]


def test_sleep_for_retry_exponential_when_no_header(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    # attempt=2 → 30 * 2^2 = 120
    delay = sleep_for_retry(attempt=2, base_delay=30.0, cap=600.0)
    assert delay == 120.0
    assert slept == [120.0]


def test_sleep_for_retry_caps_at_max(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", lambda s: slept.append(s))
    # attempt=10 → 30 * 2^10 = 30720 → capped at 600
    delay = sleep_for_retry(attempt=10, base_delay=30.0, cap=600.0)
    assert delay == 600.0


def test_with_429_retry_succeeds_on_first_call(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    calls = []

    @with_429_retry(max_attempts=3, base_delay=1.0)
    def f():
        calls.append(1)
        return "ok"

    assert f() == "ok"
    assert len(calls) == 1


def test_with_429_retry_retries_on_429_then_succeeds(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    calls = []

    @with_429_retry(max_attempts=4, base_delay=1.0)
    def f():
        calls.append(1)
        if len(calls) < 3:
            raise _FakeHTTPError(429)
        return "ok"

    assert f() == "ok"
    assert len(calls) == 3


def test_with_429_retry_propagates_non_rate_limit_error(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)

    @with_429_retry(max_attempts=3, base_delay=1.0)
    def f():
        raise ValueError("bad")

    with pytest.raises(ValueError):
        f()


def test_with_429_retry_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    calls = []

    @with_429_retry(max_attempts=3, base_delay=1.0)
    def f():
        calls.append(1)
        raise _FakeHTTPError(429)

    with pytest.raises(Exception):
        f()
    assert len(calls) == 3
