"""Ladder liveness audit — the POSITIVE control, dual to ladder_leakage_audit.py.

    ladder_leakage_audit : can a candidate that reads ONLY the payload pass?   want NO
    ladder_liveness_audit: can a candidate HANDED THE GROUND TRUTH pass?       want YES

Both are required. A metric with only a negative control is unfalsifiable in the
flattering direction: a tier on which nothing has ever scored above zero has never
demonstrated that its grading predicate ACCEPTS a correct answer. Its 0% may be
measuring the grader rather than the candidate.

Motivating case (2026-08-12): R7 and R8 score 0.0% for all four reference
baselines, and `verify:unknown_kind` fires on 160/160 probes at R5/R7/R8. That is
consistent with two very different worlds -- honestly-hard tiers, or broken ones.
This control separates them. Result: all 8 tiers are LIVE, so R7/R8 are genuinely
unclimbed.

CALIBRATION REQUIREMENT (learned the hard way, see test_r0_container_regression):
this control must be calibrated on tiers already known to be climbable (R0-R3)
before its verdict on unclimbed tiers means anything. The first version of this
file reported "R0 BROKEN 0.0%" -- which was a bug in the CONTROL (it returned a
bare scalar where the `linear` tier's answer protocol is a singleton list), not a
defect in R0. That is failure mode #4 in retraction_registry.md (specification
mismatch). A positive control needs its own positive control.

Run:  PYTHONPATH=. python harmonia/diagnostics/ladder_liveness_audit.py
Exit: 0 if every tier accepts its own ground truth, 1 otherwise.
"""
from __future__ import annotations

import random
import sys

from harmonia.services.grading_oracle import ALL_TIERS
from harmonia.experiments import reasoning_phase0 as rp

SEED = 20260527

# Every trace field asserted true. The omniscient candidate is allowed to lie about
# process -- we are testing the ANSWER channel only. (That the trace fields are
# credited on assertion is a separate, already-reported defect.)
_ALL_TRACE = {f: True for f in rp.TRACE_FIELDS}


def omniscient(probe):
    """Return the harness's own recorded ground truth, in the shape the tier expects.

    Any special-casing here is a statement about the tier's ANSWER PROTOCOL, not a
    concession to the tier. Each branch below is a documented protocol difference.
    """
    gt = probe.ground_truth
    if probe.kind == "rational":
        # protocol: a sentinel string, not a root list
        return "all_x_except_excluded", dict(_ALL_TRACE)
    if probe.kind == "conjecture":
        # protocol: the boolean verdict (== ground_truth; R6 also leaks it into data)
        return probe.data["truth"], dict(_ALL_TRACE)
    if probe.kind == "linear":
        # protocol: a LIST of roots; ground_truth is stored as a bare scalar
        return [gt], dict(_ALL_TRACE)
    return gt, dict(_ALL_TRACE)


def audit_tier(tier: str) -> dict:
    gen = getattr(rp, f"gen_{tier}")
    probes = gen(random.Random(SEED))
    n = ok = 0
    for p in probes:
        ans, _tr = omniscient(p)
        n += 1
        ok += 1 if rp._ans_correct(p, ans) else 0
    rate = ok / n if n else 0.0
    return {
        "tier": tier,
        "n": n,
        "kinds": sorted({p.kind for p in probes}),
        "omniscient_rate": rate,
        "verdict": "LIVE" if rate == 1.0 else ("BROKEN" if rate == 0.0 else "PARTIAL"),
    }


def main(argv=None) -> int:
    rows = [audit_tier(t) for t in ALL_TIERS]

    print(f"Ladder liveness audit  (seed={SEED})")
    print("=" * 70)
    print(f"{'tier':<6}{'kind':<16}{'n':>5}{'omniscient':>13}   verdict")
    print("-" * 70)
    for r in rows:
        print(f"{r['tier']:<6}{'/'.join(r['kinds']):<16}{r['n']:>5}"
              f"{r['omniscient_rate']*100:>12.1f}%   {r['verdict']}")
    print("-" * 70)

    dead = [r for r in rows if r["verdict"] != "LIVE"]
    if dead:
        print("FAIL: tier(s) reject their own ground truth: "
              + ", ".join(f"{r['tier']} ({r['omniscient_rate']*100:.1f}%)" for r in dead))
        print()
        print("A 0% score on such a tier measures the GRADER, not the candidate.")
        print("Do not report a capability gap on a tier that fails this control.")
        return 1

    print("PASS: every tier accepts its own ground truth.")
    print()
    print("Tiers are gradeable. A 0% here is therefore a real capability gap --")
    print("but see ladder_leakage_audit.py: a tier can be LIVE and still LEAK.")
    return 0


# --------------------------------------------------------------------------- #
# Regression: the control's own historical bug.
# --------------------------------------------------------------------------- #
def test_r0_container_regression() -> None:
    """The `linear` tier stores ground_truth as a scalar but grades a singleton list.

    A control that returns the bare scalar reports R0 as BROKEN -- a false positive
    against a tier all four reference baselines demonstrably climb. Pin the protocol
    so a future edit cannot silently reintroduce it.
    """
    probes = rp.gen_R0(random.Random(SEED))
    p = probes[0]
    assert p.kind == "linear", f"R0 protocol changed: kind={p.kind}"
    assert not rp._ans_correct(p, p.ground_truth), \
        "R0 now accepts a bare scalar; update omniscient() and delete this regression"
    ans, _ = omniscient(p)
    assert rp._ans_correct(p, ans), "omniscient() no longer satisfies the R0 protocol"


def test_all_tiers_live() -> None:
    """The 2026-08-12 measurement, pinned."""
    for r in (audit_tier(t) for t in ALL_TIERS):
        assert r["verdict"] == "LIVE", f"{r['tier']} regressed to {r['verdict']}"


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_r0_container_regression()
        test_all_tiers_live()
        print("2 passed, 0 failed")
        raise SystemExit(0)
    raise SystemExit(main())
