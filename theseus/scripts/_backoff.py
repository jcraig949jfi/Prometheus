"""Exponential backoff helpers for rate-limited fetchers.

429 = Too Many Requests; some upstreams (Wikipedia, arxiv) issue these
with Retry-After headers, others (arxiv) just hard-ban for several
minutes. The arxiv `num_retries` default of 3 with 3s delays is far
too short for their cooldown window — we wrap with our own retry loop.

Wikipedia honors Retry-After (in seconds); we sleep that long.
arxiv doesn't usually return Retry-After; we fall back to exponential.

Usage:
    from theseus.scripts._backoff import sleep_for_retry, with_429_retry

    @with_429_retry(max_attempts=6, base_delay=30.0)
    def fetch_one(...):
        ...
"""
from __future__ import annotations

import functools
import sys
import time
from typing import Callable, TypeVar


T = TypeVar("T")


def sleep_for_retry(
    attempt: int,
    base_delay: float = 30.0,
    cap: float = 600.0,
    retry_after: float | None = None,
) -> float:
    """Compute and sleep for the appropriate delay.

    If `retry_after` is provided (from a Retry-After header), honor it
    (clamped to `cap`). Otherwise: exponential base_delay * 2^attempt,
    clamped to cap.

    Returns the actual seconds slept (useful for logging).
    """
    if retry_after is not None:
        delay = min(float(retry_after), cap)
    else:
        delay = min(base_delay * (2 ** attempt), cap)
    print(
        f"[backoff] 429 backoff: attempt={attempt} sleeping {delay:.1f}s",
        file=sys.stderr,
    )
    time.sleep(delay)
    return delay


def is_rate_limited(exc: BaseException) -> tuple[bool, float | None]:
    """Detect whether an exception represents a rate-limit response.

    Returns (is_429, retry_after_seconds_or_None).

    Supports:
      - arxiv.HTTPError with status_code 429
      - requests.HTTPError / requests.Response with status_code 429
      - generic exceptions with a `.status_code` attribute
    """
    # arxiv.HTTPError carries .status_code directly
    code = getattr(exc, "status_code", None)
    if code is None:
        # Some libs wrap the response on .response
        resp = getattr(exc, "response", None)
        if resp is not None:
            code = getattr(resp, "status_code", None)

    if code != 429 and code != 503:
        return False, None

    # Try to extract Retry-After
    retry_after = None
    resp = getattr(exc, "response", None)
    if resp is not None:
        headers = getattr(resp, "headers", None)
        if headers is not None:
            ra = headers.get("Retry-After") or headers.get("retry-after")
            if ra:
                try:
                    retry_after = float(ra)
                except (TypeError, ValueError):
                    retry_after = None

    return True, retry_after


def with_429_retry(
    max_attempts: int = 6,
    base_delay: float = 30.0,
    cap: float = 600.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: catch 429/503 exceptions, sleep with backoff, retry.

    Non-rate-limit exceptions propagate immediately. After `max_attempts`
    rate-limit hits, the last exception propagates.
    """
    def deco(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    is_rl, retry_after = is_rate_limited(exc)
                    if not is_rl:
                        raise
                    last_exc = exc
                    if attempt + 1 >= max_attempts:
                        break
                    sleep_for_retry(
                        attempt=attempt,
                        base_delay=base_delay,
                        cap=cap,
                        retry_after=retry_after,
                    )
            # Exhausted retries
            if last_exc is not None:
                raise last_exc
            # Unreachable; max_attempts >= 1 always returns or raises
            return None  # type: ignore[return-value]
        return wrapper
    return deco
