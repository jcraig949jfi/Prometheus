#!/usr/bin/env python3
"""
A150* and A151* cross-family validation of the OBSTRUCTION_SHAPE candidate.

Follow-through from `a148_validation.py` INCONCLUSIVE result (sync stream
1777460003906): A148 corpus had zero strict-signature matches AND zero
unanimous-kill events under battery_sweep_v2 coverage, so the transfer test
was unrunnable in that family. The recommendation was to retarget A150 (501
sequences) or A151 (332 sequences), both also octant walks present in
asymptotic_deviations.jsonl.

Same signature as a149_obstruction.py:
    {n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}

This script reuses the load/feature/report machinery from a148_validation.py
but parameterizes over a list of family prefixes and prints a side-by-side
table plus a per-family verdict. No symbol promotion (per onboarding don'ts).

Run:  python a150_a151_validation.py
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).parent.parent
DATA = REPO / "cartography" / "convergence" / "data"
ASYMPTOTIC = DATA / "asymptotic_deviations.jsonl"
BATTERY_SWEEP = DATA / "battery_sweep_v2.jsonl"


STEP_SET_RE = re.compile(r"\{([^}]+)\}")
STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")

UNANIMOUS_BATTERY = {
    "F1_permutation_null",
    "F6_base_rate",
    "F9_simpler_explanation",
    "F11_cross_validation",
}


def parse_step_set(name: str):
    m = STEP_SET_RE.search(name)
    if not m:
        return None
    body = m.group(1)
    steps = STEP_RE.findall(body)
    if not steps:
        return None
    return [tuple(int(x) for x in s) for s in steps]


def features_of(steps):
    n = len(steps)
    nx = sum(1 for s in steps if s[0] < 0)
    px = sum(1 for s in steps if s[0] > 0)
    has_diag_neg = any(s == (-1, -1, -1) for s in steps)
    has_diag_pos = any(s == (1, 1, 1) for s in steps)
    return {
        "n_steps": n,
        "neg_x": nx,
        "pos_x": px,
        "has_diag_neg": has_diag_neg,
        "has_diag_pos": has_diag_pos,
    }


def load_jsonl(path):
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def load_family(prefix):
    rows = load_jsonl(ASYMPTOTIC)
    out = []
    for r in rows:
        sid = r.get("seq_id", "")
        if not sid.startswith(prefix):
            continue
        steps = parse_step_set(r.get("name", ""))
        if not steps:
            continue
        f = features_of(steps)
        r["_steps"] = steps
        r["_features"] = f
        out.append(r)
    return out


def load_kill_verdicts():
    rows = load_jsonl(BATTERY_SWEEP)
    out = defaultdict(set)
    for r in rows:
        sid = r.get("seq_id")
        if sid:
            out[sid].update(r.get("kill_tests", []) or [])
    return out


def signature_match(features):
    return (
        features["n_steps"] == 5
        and features["neg_x"] == 4
        and features["pos_x"] == 1
        and features["has_diag_neg"]
    )


def relaxed_match(features):
    return (
        features["n_steps"] == 5
        and features["neg_x"] >= 3
        and features["has_diag_neg"]
    )


def symmetric_match(features):
    """A149499-shaped: nx/px=ny/py=nz/pz fully symmetric, both diagonals.

    This isn't the OBSTRUCTION_SHAPE signature. It is the candidate
    sister-obstruction discovered while scoping Ask 2 (Harmonia_M2_auditor,
    2026-04-29). Recorded here for cross-family count alongside the
    primary signature so we can see whether the symmetric pattern is also
    cross-family or A149*-specific.
    """
    return (
        features["n_steps"] == 5
        and features["has_diag_neg"]
        and features["has_diag_pos"]
        and features["neg_x"] == 3
        and features["pos_x"] == 2
    )


def unanimous_kill_rate(group, kills):
    present = [r for r in group if r["seq_id"] in kills]
    if not present:
        return 0.0, 0, 0
    n_unanimous = sum(
        1 for r in present
        if UNANIMOUS_BATTERY.issubset(kills[r["seq_id"]])
    )
    return n_unanimous / len(present), n_unanimous, len(present)


def family_report(prefix, family, kills):
    matches = [r for r in family if signature_match(r["_features"])]
    relaxed = [r for r in family if relaxed_match(r["_features"])]
    symmetric = [r for r in family if symmetric_match(r["_features"])]
    non_matches = [r for r in family if not signature_match(r["_features"])]

    rate_m, n_m_kill, n_m_total = unanimous_kill_rate(matches, kills)
    rate_nm, n_nm_kill, n_nm_total = unanimous_kill_rate(non_matches, kills)
    rate_r, n_r_kill, n_r_total = unanimous_kill_rate(relaxed, kills)
    rate_s, n_s_kill, n_s_total = unanimous_kill_rate(symmetric, kills)

    return {
        "prefix": prefix,
        "n_family": len(family),
        "n_matches_strict": len(matches),
        "n_matches_relaxed": len(relaxed),
        "n_matches_symmetric": len(symmetric),
        "strict": {"kills_in_group": n_m_kill, "evaluated": n_m_total, "rate": rate_m},
        "non_matches": {"kills_in_group": n_nm_kill, "evaluated": n_nm_total, "rate": rate_nm},
        "relaxed": {"kills_in_group": n_r_kill, "evaluated": n_r_total, "rate": rate_r},
        "symmetric": {"kills_in_group": n_s_kill, "evaluated": n_s_total, "rate": rate_s},
        "matches_strict_seq_ids": [r["seq_id"] for r in matches],
        "matches_symmetric_seq_ids": [r["seq_id"] for r in symmetric],
    }


def verdict_for(rep):
    s = rep["strict"]
    if s["evaluated"] == 0:
        return "INCONCLUSIVE", (
            f"No {rep['prefix']}* sequences match the strict signature AND have "
            f"battery-sweep verdicts. Cannot evaluate transfer in this family."
        )
    if s["rate"] >= 0.95 and s["evaluated"] >= 3:
        return "TRANSFERS", (
            f"{rep['prefix']}* matches at {s['kills_in_group']}/{s['evaluated']} "
            f"= {s['rate']:.3f}. Above 0.95 threshold with n>=3."
        )
    if s["rate"] < 0.5 and s["evaluated"] >= 3:
        return "DOES_NOT_TRANSFER", (
            f"{rep['prefix']}* matches at {s['kills_in_group']}/{s['evaluated']} "
            f"= {s['rate']:.3f}. Below 0.5 with n>=3 — family-specific."
        )
    if s["evaluated"] < 3:
        return "UNDERPOWERED", (
            f"{rep['prefix']}* yielded only {s['evaluated']} signature-matching "
            f"sequence(s) with battery-sweep verdicts. n too small."
        )
    return "PARTIAL_TRANSFER", (
        f"{rep['prefix']}* matches at {s['kills_in_group']}/{s['evaluated']} "
        f"= {s['rate']:.3f}. In the 0.5-0.95 ambiguous range."
    )


def main():
    print("=" * 78)
    print("A150* / A151* CROSS-FAMILY VALIDATION OF OBSTRUCTION_SHAPE")
    print("=" * 78)
    print("Signature under test (transferred verbatim from A149* analysis):")
    print("  {n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}")
    print()
    print("Also tracking sister-candidate signature (Ask 2 follow-up):")
    print("  {n_steps=5, neg_x=3, pos_x=2, has_diag_neg=True, has_diag_pos=True}")
    print("  (A149499-shaped: full 3-axis symmetric with both diagonals)")
    print()

    kills = load_kill_verdicts()

    families = {
        "A149": load_family("A149"),  # baseline reference
        "A150": load_family("A150"),
        "A151": load_family("A151"),
    }

    print("[1] Loaded:")
    for p, fam in families.items():
        print(f"    {p}*: {len(fam):4d} sequences with parseable step sets")
    print(f"    Battery-sweep records: {sum(len(v) for v in kills.values())} kill events"
          f" across {len(kills)} sequences")
    print()

    reports = {p: family_report(p, fam, kills) for p, fam in families.items()}

    def print_report(rep):
        print(f"[{rep['prefix']}*] family analysis")
        print(f"  family size:                      {rep['n_family']}")
        print(f"  strict-signature matches:         {rep['n_matches_strict']}")
        print(f"  relaxed-signature matches:        {rep['n_matches_relaxed']}")
        print(f"  symmetric-sister matches:         {rep['n_matches_symmetric']}")
        s = rep["strict"]; nm = rep["non_matches"]; r = rep["relaxed"]; sym = rep["symmetric"]
        print(f"  strict      unanimous-kill: {s['kills_in_group']:>4} / {s['evaluated']:>4} "
              f"= {s['rate']:.3f}")
        print(f"  non-matches unanimous-kill: {nm['kills_in_group']:>4} / {nm['evaluated']:>4} "
              f"= {nm['rate']:.3f}")
        print(f"  relaxed     unanimous-kill: {r['kills_in_group']:>4} / {r['evaluated']:>4} "
              f"= {r['rate']:.3f}")
        print(f"  symmetric   unanimous-kill: {sym['kills_in_group']:>4} / {sym['evaluated']:>4} "
              f"= {sym['rate']:.3f}")
        if rep["matches_strict_seq_ids"]:
            print(f"  strict-match seq_ids:    {rep['matches_strict_seq_ids']}")
        if rep["matches_symmetric_seq_ids"]:
            print(f"  symmetric-match seq_ids: {rep['matches_symmetric_seq_ids']}")
        print()

    for p in ("A149", "A150", "A151"):
        print_report(reports[p])

    print("=" * 78)
    print("CROSS-FAMILY TRANSFER VERDICTS (strict signature)")
    print("=" * 78)
    verdicts = {}
    for p in ("A150", "A151"):
        v, reading = verdict_for(reports[p])
        verdicts[p] = v
        print(f"\n  {p}*  verdict: {v}")
        print(f"    {reading}")

    print()
    print("=" * 78)
    print("OBSTRUCTION_SHAPE@v1 PROMOTION-THRESHOLD STATUS")
    print("=" * 78)
    families_supporting = sum(
        1 for p in ("A149", "A150", "A151")
        if reports[p]["strict"]["rate"] >= 0.95 and reports[p]["strict"]["evaluated"] >= 3
    )
    print(f"  Families where strict signature transfers cleanly: {families_supporting}")
    print(f"  (A149 is the baseline; need >=2 families for cross-family transfer)")
    if families_supporting >= 2:
        print(f"  STATUS: cross-family transfer EVIDENCE — second anchor identified.")
    else:
        print(f"  STATUS: still single-family. OBSTRUCTION_SHAPE@v1 promotion blocked.")

    out_path = Path(__file__).parent / "a150_a151_validation_results.json"
    out_path.write_text(json.dumps({
        "experiment": "a150_a151_cross_family_validation",
        "signature_strict": {"n_steps": 5, "neg_x": 4, "pos_x": 1, "has_diag_neg": True},
        "signature_symmetric_sister": {
            "n_steps": 5, "neg_x": 3, "pos_x": 2,
            "has_diag_neg": True, "has_diag_pos": True,
        },
        "verdicts": verdicts,
        "families_supporting_strict_transfer": families_supporting,
        "reports": reports,
    }, indent=2))
    print(f"\nDumped {out_path}")


if __name__ == "__main__":
    main()
