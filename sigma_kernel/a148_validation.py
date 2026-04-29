#!/usr/bin/env python3
"""
A148* cross-family validation of the OBSTRUCTION_SHAPE candidate.

Stoa Ask 3 from `stoa/discussions/2026-04-29-sigma-kernel-mvp.md`:
  Run the same structural-signature analysis used for A149* against the
  A148* family. If the signature transfers, the OBSTRUCTION_SHAPE
  generalizes; if not, it is family-specific.

This script does NOT promote a new symbol (per the onboarding don'ts:
SYMBOL_PROMOTED gates and second-anchor coordination belong on agora,
not in a local validation run). It is pure analysis: apply the same
signature `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}` to the
A148* family, measure the kill-rate split, and report cross-family
transfer.

Run:  python a148_validation.py
"""

from __future__ import annotations

import json
import re
import sys
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
    ny = sum(1 for s in steps if s[1] < 0)
    nz = sum(1 for s in steps if s[2] < 0)
    px = sum(1 for s in steps if s[0] > 0)
    py = sum(1 for s in steps if s[1] > 0)
    pz = sum(1 for s in steps if s[2] > 0)
    has_diag_neg = any(s == (-1, -1, -1) for s in steps)
    n_axis_aligned = sum(1 for s in steps if sum(abs(c) for c in s) == 1)
    return {
        "n_steps": n,
        "neg_x": nx, "neg_y": ny, "neg_z": nz,
        "pos_x": px, "pos_y": py, "pos_z": pz,
        "has_diag_neg": has_diag_neg,
        "n_axis_aligned": n_axis_aligned,
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
    """The exact OBSTRUCTION_SHAPE signature from a149_obstruction.py."""
    return (
        features["n_steps"] == 5
        and features["neg_x"] == 4
        and features["pos_x"] == 1
        and features["has_diag_neg"]
    )


def relaxed_match(features):
    """Relaxed neg_x>=3 variant for comparison."""
    return (
        features["n_steps"] == 5
        and features["neg_x"] >= 3
        and features["has_diag_neg"]
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
    """Run the full split analysis on a family."""
    matches = [r for r in family if signature_match(r["_features"])]
    non_matches = [r for r in family if not signature_match(r["_features"])]
    relaxed = [r for r in family if relaxed_match(r["_features"])]

    rate_m, n_m_kill, n_m_total = unanimous_kill_rate(matches, kills)
    rate_nm, n_nm_kill, n_nm_total = unanimous_kill_rate(non_matches, kills)
    rate_r, n_r_kill, n_r_total = unanimous_kill_rate(relaxed, kills)

    ratio = (rate_m + 1e-9) / (rate_nm + 1e-9) if n_nm_total > 0 else None

    return {
        "prefix": prefix,
        "n_family": len(family),
        "n_matches_strict": len(matches),
        "n_matches_relaxed": len(relaxed),
        "strict": {
            "kills_in_group": n_m_kill,
            "evaluated": n_m_total,
            "rate": rate_m,
        },
        "non_matches": {
            "kills_in_group": n_nm_kill,
            "evaluated": n_nm_total,
            "rate": rate_nm,
        },
        "relaxed": {
            "kills_in_group": n_r_kill,
            "evaluated": n_r_total,
            "rate": rate_r,
        },
        "lift_strict_vs_nonmatch": ratio,
        "matches_strict_seq_ids": [r["seq_id"] for r in matches],
        "anti_anchors": [
            r["seq_id"]
            for r in family
            if UNANIMOUS_BATTERY.issubset(kills.get(r["seq_id"], set()))
            and not signature_match(r["_features"])
        ][:10],
    }


def main():
    print("=" * 72)
    print("A148* CROSS-FAMILY VALIDATION OF OBSTRUCTION_SHAPE")
    print("=" * 72)
    print("Signature under test (transferred verbatim from A149* analysis):")
    print("  {n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}")
    print()

    kills = load_kill_verdicts()

    # Run both families for direct comparison
    a148 = load_family("A148")
    a149 = load_family("A149")

    print(f"[1] Loaded:")
    print(f"    A148*: {len(a148):4d} sequences with parseable step sets")
    print(f"    A149*: {len(a149):4d} sequences with parseable step sets")
    print(f"    Battery-sweep records: {sum(len(v) for v in kills.values())} kill events"
          f" across {len(kills)} sequences")
    print()

    rep_148 = family_report("A148", a148, kills)
    rep_149 = family_report("A149", a149, kills)

    def print_report(rep):
        print(f"[{rep['prefix']}*] family analysis")
        print(f"  family size:                 {rep['n_family']}")
        print(f"  strict-signature matches:    {rep['n_matches_strict']}")
        print(f"  relaxed-signature matches:   {rep['n_matches_relaxed']}")
        s = rep["strict"]
        nm = rep["non_matches"]
        r = rep["relaxed"]
        print(f"  strict matches  unanimous-kill: {s['kills_in_group']:>4} / {s['evaluated']:>4} "
              f"= {s['rate']:.3f}")
        print(f"  non-matches     unanimous-kill: {nm['kills_in_group']:>4} / {nm['evaluated']:>4} "
              f"= {nm['rate']:.3f}")
        print(f"  relaxed matches unanimous-kill: {r['kills_in_group']:>4} / {r['evaluated']:>4} "
              f"= {r['rate']:.3f}")
        if rep["lift_strict_vs_nonmatch"] is not None:
            print(f"  strict lift vs non-match:    {rep['lift_strict_vs_nonmatch']:.2f}x")
        if rep["matches_strict_seq_ids"]:
            print(f"  strict-match seq_ids: {rep['matches_strict_seq_ids']}")
        if rep["anti_anchors"]:
            print(f"  anti-anchors (killed but signature-missing, first 10):")
            for sid in rep["anti_anchors"]:
                rec = next((x for x in (a148 if rep['prefix'] == 'A148' else a149)
                            if x["seq_id"] == sid), None)
                if rec:
                    f = rec["_features"]
                    print(f"      {sid}  neg_x={f['neg_x']} pos_x={f['pos_x']} "
                          f"diag_neg={f['has_diag_neg']} n_steps={f['n_steps']}")
        print()

    print_report(rep_149)
    print_report(rep_148)

    # ------------------------------------------------------------------
    # Cross-family transfer adjudication
    # ------------------------------------------------------------------
    print("=" * 72)
    print("CROSS-FAMILY TRANSFER VERDICT")
    print("=" * 72)
    s_148 = rep_148["strict"]
    s_149 = rep_149["strict"]

    if s_148["evaluated"] == 0:
        verdict = "INCONCLUSIVE"
        reading = (
            "No A148* sequences match the strict signature AND have battery-sweep\n"
            "verdicts. Cannot evaluate transfer at this n. Either the signature\n"
            "really is A149*-specific, or the A148* corpus in battery_sweep_v2.jsonl\n"
            "doesn't include enough sequences with parseable step-sets matching the\n"
            "signature to test."
        )
    elif s_148["rate"] >= 0.95 and s_148["evaluated"] >= 3:
        verdict = "TRANSFERS"
        reading = (
            f"A148* matches the signature at {s_148['kills_in_group']}/{s_148['evaluated']} "
            f"(rate {s_148['rate']:.3f}) — comparable to A149* at "
            f"{s_149['kills_in_group']}/{s_149['evaluated']} (rate {s_149['rate']:.3f}).\n"
            "OBSTRUCTION_SHAPE generalizes beyond the original A149* family. The\n"
            "structural signature {n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}\n"
            "predicts unanimous-kill on F1+F6+F9+F11 across both families.\n"
            "This is the second cross-family anchor required to push the candidate\n"
            "past the OBSTRUCTION_SHAPE@v1 promotion threshold."
        )
    elif s_148["rate"] < 0.5 and s_148["evaluated"] >= 3:
        verdict = "DOES_NOT_TRANSFER"
        reading = (
            f"A148* matches at {s_148['kills_in_group']}/{s_148['evaluated']} "
            f"(rate {s_148['rate']:.3f}) — substantially below A149*'s\n"
            f"{s_149['kills_in_group']}/{s_149['evaluated']} (rate {s_149['rate']:.3f}).\n"
            "OBSTRUCTION_SHAPE is family-specific to A149*. The structural\n"
            "signature is not by itself sufficient to predict unanimous-kill;\n"
            "something A149*-specific co-occurs. The candidate is still useful\n"
            "as a substrate symbol but with narrower scope."
        )
    elif s_148["evaluated"] < 3:
        verdict = "UNDERPOWERED"
        reading = (
            f"A148* yielded only {s_148['evaluated']} signature-matching sequence(s) "
            f"with battery-sweep verdicts. Sample too small to adjudicate transfer\n"
            "either way. Consider widening corpus or relaxing battery-sweep dependency."
        )
    else:
        verdict = "PARTIAL_TRANSFER"
        reading = (
            f"A148* matches at {s_148['kills_in_group']}/{s_148['evaluated']} "
            f"(rate {s_148['rate']:.3f}) — neither cleanly transfers nor fails.\n"
            "The signature explains some but not all of the kill-rate variation in A148*."
        )
    print(f"verdict: {verdict}")
    print()
    print(reading)
    print()

    # Dump JSON for downstream consumption
    out_path = Path(__file__).parent / "a148_validation_results.json"
    out_path.write_text(json.dumps({
        "experiment": "a148_cross_family_validation",
        "signature": {
            "n_steps": 5, "neg_x": 4, "pos_x": 1, "has_diag_neg": True,
        },
        "verdict": verdict,
        "reading": reading,
        "a149_report": rep_149,
        "a148_report": rep_148,
    }, indent=2))
    print(f"Dumped {out_path}")


if __name__ == "__main__":
    main()
