"""WP-0a: a length mismatch is refused, not scored with a lowered ceiling.

Herakles F-1, the highest-severity item in that pass. `evaluate_bitstring`
accepted a candidate whose length differed from the declared `length` and
returned COMPLETED with a plausible score:

    n = min(len(bits), len(target))
    return sum(1 for i in range(n) if bits[i] == target[i]) / len(target)

It matches over the overlap and divides by the TARGET length, so a short
candidate is scored against the full target and its achievable score is capped
at len(bits)/length, with `solved` (score >= 1.0) unreachable. Measured at
target length 32, seed_root 110663:

    len(bits)   status      score    achievable ceiling
           16   COMPLETED    0.250   0.500
            8   COMPLETED    0.125   0.250
           32   COMPLETED    0.531   1.000

That is the failure shape this programme keeps being burned by: a ceiling that
hides the quantity of interest and an outcome rule that cannot fire. A template
with the defect runs, fossilizes, and contributes observations that look like
weak performance rather than a broken spec -- and it was reachable from
templates that pass every existing check.

This is an INTEGRITY REPAIR. It licenses nothing scientific: it does not make
any experiment work, it stops one from silently not working.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.executors import (BitStringExecutor, WorkPackage,        # noqa: E402
                           _deterministic_score)

# the exact parameters of Herakles's measured table
F1_SEED = 110663
F1_LENGTH = 32


def _run(length, bits, seed=F1_SEED):
    ex = BitStringExecutor(length=length)
    return ex.execute(WorkPackage(work_id="t", world_id="w", kind=ex.kind,
                                  payload={"bits": bits}, seed_root=seed))


# ---------------------------------------------------------------- 0a-a
@pytest.mark.parametrize("n", [1, 8, 16, 31])
def test_0a_a_shorter_candidates_are_refused(n):
    r = _run(F1_LENGTH, "0" * n)
    assert r.status == "FAILED", "a %d-bit candidate scored %r" % (n, r.result)
    assert r.error == "invalid candidate"
    assert r.result is None or r.result == {}


@pytest.mark.parametrize("n", [33, 40, 64])
def test_0a_a_longer_candidates_are_refused(n):
    """Longer is refused too. It was NOT capped -- the extra bits were simply
    ignored, so a 64-bit candidate scored over its first 32 and the rest of the
    string never existed. Silently discarding half a candidate is the same
    defect wearing the other sign."""
    r = _run(F1_LENGTH, "0" * n)
    assert r.status == "FAILED", "a %d-bit candidate scored %r" % (n, r.result)
    assert r.error == "invalid candidate"


def test_0a_a_exact_length_scores_exactly_as_before():
    """PAIRED, and the load-bearing half: the repair must change nothing for a
    valid candidate. The value is pinned, not merely asserted non-None."""
    r = _run(F1_LENGTH, "0" * F1_LENGTH)
    assert r.status == "COMPLETED"
    ex = BitStringExecutor(length=F1_LENGTH)
    target = ex.target_for(F1_SEED)
    expected = sum(1 for i in range(F1_LENGTH) if target[i] == "0") / F1_LENGTH
    assert r.result["score"] == expected
    assert r.result["bits"] == "0" * F1_LENGTH
    assert r.result["length"] == F1_LENGTH
    assert r.result["solved"] is (expected >= 1.0)
    assert r.reproducibility == "BIT_DETERMINISTIC"


def test_0a_a_a_solvable_candidate_still_solves():
    """The ceiling was the point: with the mismatch refused, an exact-length
    candidate can still reach 1.0 and fire an outcome rule."""
    ex = BitStringExecutor(length=16)
    target = ex.target_for(4242)
    r = ex.execute(WorkPackage(work_id="t", world_id="w", kind=ex.kind,
                               payload={"bits": target}, seed_root=4242))
    assert r.status == "COMPLETED"
    assert r.result["score"] == 1.0 and r.result["solved"] is True


# ---------------------------------------------------------------- 0a-b
@pytest.mark.parametrize("bits,why", [
    ("", "empty"),
    ("0" * 31, "one short"),
    ("0" * 33, "one long"),
    ("2" * 32, "non-binary, right length"),
    ("01" * 15 + "xy", "non-binary and right length"),
    ("abc", "non-binary and wrong length"),
    ("0b101010", "prefixed literal"),
    (" " * 32, "whitespace"),
])
def test_0a_b_invalid_candidates_fail_clearly(bits, why):
    """Every invalid combination of length/type/alphabet lands on the SAME
    established error path, so a caller has one thing to check rather than a
    taxonomy."""
    r = _run(F1_LENGTH, bits)
    assert r.status == "FAILED", "%s (%s) produced %r" % (bits[:12], why,
                                                          r.result)
    assert r.error == "invalid candidate"


def test_0a_b_a_refusal_carries_no_score_to_fossilize():
    """'No ordinary observation emitted' begins here: a FAILED result has no
    score, no solved and no bits, so there is nothing for a downstream reader
    to mistake for a measurement. The engine's own contract does the rest --
    an observation binding this work would be typed from the work's status,
    not from a number this result does not contain."""
    r = _run(F1_LENGTH, "0" * 16)
    assert r.status == "FAILED"
    assert not r.result
    for k in ("score", "solved", "bits"):
        assert k not in (r.result or {})


def test_0a_b_non_binary_refusal_is_unchanged():
    """PAIRED with the new condition: the pre-existing alphabet check must
    still behave exactly as it did."""
    r = _run(F1_LENGTH, "2" * F1_LENGTH)
    assert r.status == "FAILED" and r.error == "invalid candidate"


# ---------------------------------------------------------------- 0a-c
def test_0a_c_herakles_F1_table_now_exercises_refusal():
    """Herakles's measured table, re-run. The two rows that were the finding
    are now refusals; the coherent row is untouched, to the digit."""
    rows = {}
    for n in (16, 8, 32):
        r = _run(F1_LENGTH, "0" * n)
        rows[n] = (r.status, None if r.status == "FAILED"
                   else r.result["score"])
    assert rows[16][0] == "FAILED", rows
    assert rows[8][0] == "FAILED", rows
    assert rows[32][0] == "COMPLETED", rows
    # the previously reported score for the coherent row, unchanged
    assert round(rows[32][1], 3) == 0.531, rows


def test_0a_c_sealed_fixtures_keep_result_and_identity():
    """The repair must not move a single sealed result. Every valid-length
    candidate scores bit-for-bit as before, and the target derivation -- which
    is what a fixture's identity rests on -- is untouched."""
    for length in (8, 16, 24, 32):
        ex = BitStringExecutor(length=length)
        for seed in (0, 1, 110663, 2 ** 31):
            target = ex.target_for(seed)
            # identity: the landscape itself is unchanged
            assert len(target) == length
            assert all(c in "01" for c in target)
            # result: scoring over an exact-length candidate is unchanged, and
            # still equals the pre-repair function applied to equal lengths
            for cand in ("0" * length, "1" * length, target):
                r = ex.execute(WorkPackage(work_id="t", world_id="w",
                                           kind=ex.kind,
                                           payload={"bits": cand},
                                           seed_root=seed))
                assert r.status == "COMPLETED"
                assert r.result["score"] == _deterministic_score(cand, target)


def test_0a_c_the_lowered_ceiling_is_unreachable_now():
    """State the closed path as a property rather than as examples: for every
    accepted candidate the achievable ceiling is 1.0, because acceptance now
    implies len(bits) == length."""
    ex = BitStringExecutor(length=16)
    target = ex.target_for(99)
    for n in range(1, 33):
        r = ex.execute(WorkPackage(work_id="t", world_id="w", kind=ex.kind,
                                   payload={"bits": "0" * n}, seed_root=99))
        if r.status == "COMPLETED":
            assert n == 16, "accepted a %d-bit candidate at length 16" % n
            # ceiling reachable: the target itself scores 1.0
            best = ex.execute(WorkPackage(work_id="t", world_id="w",
                                          kind=ex.kind,
                                          payload={"bits": target},
                                          seed_root=99))
            assert best.result["score"] == 1.0
