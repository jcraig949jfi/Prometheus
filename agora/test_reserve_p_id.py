"""Smoke test for reserve_p_id / peek_next_p_id.

Uses an ISOLATED test counter (not the live agora:next_p_id) so this can be
run in CI or locally without perturbing session state. We patch the module
constant before import-time side-effects matter.

Run: python agora/test_reserve_p_id.py
"""
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Force redis credentials before importing the module
os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agora import work_queue


def run_test():
    # Use an isolated test counter to avoid touching live state.
    work_queue.NEXT_P_ID = "agora:test_next_p_id"
    work_queue.NEXT_P_ID_INIT = 99  # first reservation returns P100

    r = work_queue._connect()
    # Wipe any leftover from a previous run
    r.delete("agora:test_next_p_id")

    # Peek should return the next-will-be-returned ID
    p1 = work_queue.peek_next_p_id()
    assert p1 == "P100", f"peek initial: expected P100, got {p1}"
    print(f"peek (uninit) = {p1}  OK")

    # First reserve
    p = work_queue.reserve_p_id()
    assert p == "P100", f"reserve #1: expected P100, got {p}"
    print(f"reserve #1   = {p}  OK")

    # Second peek reflects advance
    p2 = work_queue.peek_next_p_id()
    assert p2 == "P101", f"peek post-#1: expected P101, got {p2}"
    print(f"peek          = {p2}  OK")

    # Second & third reserves
    p3 = work_queue.reserve_p_id()
    assert p3 == "P101", f"reserve #2: expected P101, got {p3}"
    print(f"reserve #2   = {p3}  OK")

    p4 = work_queue.reserve_p_id()
    assert p4 == "P102", f"reserve #3: expected P102, got {p4}"
    print(f"reserve #3   = {p4}  OK")

    # Atomicity sanity: rapid burst returns strictly increasing sequence
    ids = [work_queue.reserve_p_id() for _ in range(5)]
    numeric = [int(x[1:]) for x in ids]
    assert numeric == list(range(numeric[0], numeric[0] + 5)), \
        f"burst returned non-monotonic: {ids}"
    print(f"burst 5      = {ids}  OK")

    # Clean up
    r.delete("agora:test_next_p_id")
    print("\nALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_test())
