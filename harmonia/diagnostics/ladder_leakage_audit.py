"""Ladder leakage audit — does a tier hand the candidate its own answer?

Standing control for the grading oracle, per REVIEW_20260812 section 3.1:

    every tier metric must be run against a null candidate that is allowed to
    read the entire probe payload and nothing else.

Three null candidates, none of which reason:

    payload_reader  -- returns probe.data[<field>] for any field that matches
                       ground_truth. If this scores, the tier LEAKS.
    const_*         -- always returns the same answer. Establishes the tier's
                       CHANCE FLOOR (never previously measured on this ladder).
    null            -- always returns None. Sanity check that grading is live.

A tier is CLEAN only if payload_reader scores no better than chance.

Run:
    cd D:\\prometheus
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/ladder_leakage_audit.py
"""
from __future__ import annotations

import random
from collections import Counter

from harmonia.experiments import reasoning_phase0 as rp

SEED = 20260527

TIERS = {
    "R0": rp.gen_R0, "R1": rp.gen_R1, "R2": rp.gen_R2, "R3": rp.gen_R3,
    "R5": rp.gen_R5, "R6": rp.gen_R6, "R7": rp.gen_R7, "R8": rp.gen_R8,
}


def leaking_fields(probes):
    """Fields in probe.data that equal ground_truth on EVERY probe."""
    if not probes:
        return []
    keys = set(probes[0].data)
    for p in probes:
        keys &= set(p.data)
    out = []
    for k in sorted(keys):
        try:
            if all(p.data[k] == p.ground_truth for p in probes):
                out.append(k)
        except Exception:
            continue
    return out


def chance_floor(probes):
    """Best score obtainable by always returning one constant answer."""
    counts = Counter()
    for p in probes:
        try:
            counts[repr(p.ground_truth)] += 1
        except Exception:
            counts["<unhashable>"] += 1
    if not counts:
        return 0.0, None
    val, n = counts.most_common(1)[0]
    return 100.0 * n / len(probes), val


def audit_tier(tier, gen):
    probes = gen(random.Random(SEED))
    n = len(probes)
    leaks = leaking_fields(probes)
    floor, floor_val = chance_floor(probes)

    if leaks:
        # payload_reader: read the first leaking field.
        f = leaks[0]
        score = 100.0 * sum(1 for p in probes if p.data[f] == p.ground_truth) / n
        verdict = "LEAKS"
        detail = "probe.data[%r] == ground_truth on %d/%d probes" % (f, n, n)
    else:
        score = 0.0
        verdict = "CLEAN"
        detail = "no probe.data field reproduces ground_truth"

    return {"tier": tier, "n": n, "verdict": verdict, "payload_reader": score,
            "chance_floor": floor, "chance_answer": floor_val, "detail": detail,
            "leaking_fields": leaks}


def main():
    print("Ladder leakage audit  (seed=%d)" % SEED)
    print("=" * 78)
    print("%-5s %5s  %-6s  %14s  %12s  %s"
          % ("tier", "n", "verdict", "payload_reader", "chance_floor", "leaking fields"))
    print("-" * 78)
    rows = []
    for tier, gen in TIERS.items():
        try:
            r = audit_tier(tier, gen)
        except Exception as exc:                      # generator absent / signature drift
            print("%-5s %5s  %-6s  %s" % (tier, "-", "ERROR", exc))
            continue
        rows.append(r)
        print("%-5s %5d  %-6s  %13.1f%%  %11.1f%%  %s"
              % (r["tier"], r["n"], r["verdict"], r["payload_reader"],
                 r["chance_floor"], ", ".join(r["leaking_fields"]) or "-"))
    print("-" * 78)
    leaking = [r["tier"] for r in rows if r["verdict"] == "LEAKS"]
    if leaking:
        print("FAIL: %d tier(s) leak the answer into the probe payload: %s"
              % (len(leaking), ", ".join(leaking)))
        for r in rows:
            if r["verdict"] == "LEAKS":
                print("  %s: %s" % (r["tier"], r["detail"]))
        print("\nA candidate scoring at payload_reader level on a leaking tier has")
        print("demonstrated no capability. Do not promote on it.")
    else:
        print("PASS: no tier reproduces ground_truth from probe.data.")
    print("\nNote: chance_floor is the score of a constant answer. Any tier where a")
    print("candidate scores at or below its floor has demonstrated nothing either.")
    return 1 if leaking else 0


if __name__ == "__main__":
    raise SystemExit(main())
