#!/usr/bin/env python3
"""
A148* cross-family validation of the OBSTRUCTION_SHAPE candidate.

Sibling of a149_obstruction.py. The A149 script anchored the candidate
boundary_dominated_octant_walk_obstruction with structural signature
{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True} and showed 5/5 = 100%
unanimous-kill within the A149 family vs 1/54 = 1.9% on non-matches
(54x predictive lift).

This script tests whether the SAME signature transfers to the A148xxx
family — also octant walks (3-D first-octant lattice walks), also present
in asymptotic_deviations.jsonl, but a different OEIS block. If the kill
prediction holds, OBSTRUCTION_SHAPE@v1 generalizes (second cross-family
anchor → promotion-threshold material per the Ask 3 ask in
stoa/discussions/2026-04-29-sigma-kernel-mvp.md). If it fails, the
obstruction is family-specific (still a useful typed substrate citizen,
but narrower).

This script DOES NOT promote anything new — only observes and reports.
Promotion of OBSTRUCTION_SHAPE@v1 is gated on a second-agent reference
per the harmonia promotion workflow.

Run:  python a148_obstruction.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

# Reuse the parsing/feature/loading helpers from a149_obstruction.
from a149_obstruction import (
    UNANIMOUS_BATTERY,
    features_of,
    load_jsonl,
    load_kill_verdicts,
    parse_step_set,
    signature_match,
)

REPO = Path(__file__).parent.parent
DATA = REPO / "cartography" / "convergence" / "data"
ASYMPTOTIC = DATA / "asymptotic_deviations.jsonl"


def load_family(prefix: str):
    """Subset of asymptotic_deviations whose seq_id starts with `prefix`."""
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


def unanimous_kill_rate(group, kills):
    present = [r for r in group if r["seq_id"] in kills]
    if not present:
        return 0.0, 0, 0
    n_unanimous = sum(
        1 for r in present
        if UNANIMOUS_BATTERY.issubset(kills[r["seq_id"]])
    )
    return n_unanimous / len(present), n_unanimous, len(present)


def relaxed_match(features):
    """Relaxed signature: n_steps=5, neg_x>=3, has_diag_neg."""
    return (
        features["n_steps"] == 5
        and features["neg_x"] >= 3
        and features["has_diag_neg"]
    )


def analyze_family(prefix: str, kills):
    print()
    print("=" * 72)
    print(f"FAMILY {prefix}xxx")
    print("=" * 72)

    family = load_family(prefix)
    print(f"\n[1] Loaded {len(family)} sequences with parseable step sets.")

    matches = [r for r in family if signature_match(r["_features"])]
    non_matches = [r for r in family if not signature_match(r["_features"])]
    print(f"\n[2] Strict signature {{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}}:")
    print(f"    matches:     {len(matches)} sequences")
    print(f"    non-matches: {len(non_matches)} sequences")

    rate_match, n_match_kill, n_match_total = unanimous_kill_rate(matches, kills)
    rate_nonmatch, n_nm_kill, n_nm_total = unanimous_kill_rate(non_matches, kills)
    print(f"\n[3] Unanimous-kill rate (F1+F6+F9+F11):")
    print(f"    matches:     {n_match_kill:>4} / {n_match_total:>4} = {rate_match:.3f}")
    print(f"    non-matches: {n_nm_kill:>4} / {n_nm_total:>4} = {rate_nonmatch:.3f}")
    if n_nm_total > 0:
        ratio = (rate_match + 1e-9) / (rate_nonmatch + 1e-9)
        print(f"    ratio:       {ratio:.2f}x")

    relaxed = [r for r in family if relaxed_match(r["_features"])]
    rate_relaxed, n_r_kill, n_r_total = unanimous_kill_rate(relaxed, kills)
    print(f"\n[4] Relaxed signature (n_steps=5, neg_x>=3, has_diag_neg):")
    print(f"    matches:     {len(relaxed)} sequences")
    print(f"    unanimous-kill rate: {n_r_kill:>4} / {n_r_total:>4} = {rate_relaxed:.3f}")

    # Anti-anchors: killed but NOT matching the strict signature
    kill_seqs = {
        r["seq_id"] for r in family
        if UNANIMOUS_BATTERY.issubset(kills.get(r["seq_id"], set()))
    }
    matched_seqs = {r["seq_id"] for r in matches}
    unmatched_kill = kill_seqs - matched_seqs
    print(f"\n[5] {prefix}* sequences killed unanimously: {len(kill_seqs)}")
    print(f"    of which signature-matching: {len(kill_seqs & matched_seqs)}")
    print(f"    of which signature-missing:  {len(unmatched_kill)}")
    if unmatched_kill:
        print(f"    Sample unmatched-kill (anti-anchors):")
        for sid in sorted(unmatched_kill)[:5]:
            rec = next((r for r in family if r["seq_id"] == sid), None)
            if rec:
                f = rec["_features"]
                print(f"      {sid}  neg_x={f['neg_x']} pos_x={f['pos_x']} "
                      f"diag_neg={f['has_diag_neg']} n_steps={f['n_steps']}")

    # Sample of matches if any
    if matches:
        print(f"\n[6] Sample of strict signature matches:")
        for r in matches[:5]:
            sid = r["seq_id"]
            f = r["_features"]
            n_kills = len(kills.get(sid, set()))
            killed = UNANIMOUS_BATTERY.issubset(kills.get(sid, set()))
            print(f"    {sid}  neg_x={f['neg_x']} pos_x={f['pos_x']} "
                  f"diag_neg={f['has_diag_neg']} kills={n_kills} unanimous={killed}")

    return {
        "family": prefix,
        "n_total": len(family),
        "n_matches_strict": len(matches),
        "n_nonmatches_strict": len(non_matches),
        "rate_match_strict": rate_match,
        "rate_nonmatch_strict": rate_nonmatch,
        "n_match_kill_total": (n_match_kill, n_match_total),
        "n_nm_kill_total": (n_nm_kill, n_nm_total),
        "n_matches_relaxed": len(relaxed),
        "rate_relaxed": rate_relaxed,
        "n_relaxed_kill_total": (n_r_kill, n_r_total),
        "n_unanimous_kills_in_family": len(kill_seqs),
        "n_anti_anchors": len(unmatched_kill),
        "anti_anchors": sorted(unmatched_kill),
    }


def main() -> None:
    print("=" * 72)
    print("CROSS-FAMILY VALIDATION: OBSTRUCTION_SHAPE on A148 vs A149")
    print("=" * 72)
    print(f"\nSource: {ASYMPTOTIC.relative_to(REPO)}")
    print(f"Battery sweep: cartography/convergence/data/battery_sweep_v2.jsonl")
    print(f"Strict signature: {{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}}")
    print(f"Battery: F1+F6+F9+F11 unanimous-kill")

    kills = load_kill_verdicts()

    a148 = analyze_family("A148", kills)
    a149 = analyze_family("A149", kills)

    # Side-by-side comparison
    print()
    print("=" * 72)
    print("CROSS-FAMILY COMPARISON")
    print("=" * 72)
    print()
    print(f"  {'Metric':<45} {'A148':>10} {'A149':>10}")
    print(f"  {'-'*45} {'-'*10} {'-'*10}")
    print(f"  {'Total sequences in family':<45} {a148['n_total']:>10} {a149['n_total']:>10}")
    print(f"  {'Strict signature matches':<45} {a148['n_matches_strict']:>10} {a149['n_matches_strict']:>10}")
    print(f"  {'Strict matches with kill data':<45} "
          f"{a148['n_match_kill_total'][1]:>10} {a149['n_match_kill_total'][1]:>10}")
    print(f"  {'Strict-match unanimous-kill rate':<45} "
          f"{a148['rate_match_strict']:>10.3f} {a149['rate_match_strict']:>10.3f}")
    print(f"  {'Non-match unanimous-kill rate':<45} "
          f"{a148['rate_nonmatch_strict']:>10.3f} {a149['rate_nonmatch_strict']:>10.3f}")
    print(f"  {'Relaxed signature matches':<45} {a148['n_matches_relaxed']:>10} {a149['n_matches_relaxed']:>10}")
    print(f"  {'Relaxed unanimous-kill rate':<45} "
          f"{a148['rate_relaxed']:>10.3f} {a149['rate_relaxed']:>10.3f}")
    print(f"  {'Unanimous kills in family (any reason)':<45} "
          f"{a148['n_unanimous_kills_in_family']:>10} {a149['n_unanimous_kills_in_family']:>10}")
    print(f"  {'Anti-anchors (killed but unmatched)':<45} "
          f"{a148['n_anti_anchors']:>10} {a149['n_anti_anchors']:>10}")

    # Verdict
    print()
    print("=" * 72)
    print("READING")
    print("=" * 72)
    THRESHOLD = 0.95
    a148_above = a148["rate_match_strict"] >= THRESHOLD and a148["n_match_kill_total"][1] > 0
    a149_above = a149["rate_match_strict"] >= THRESHOLD and a149["n_match_kill_total"][1] > 0

    if a148["n_matches_strict"] == 0:
        print(f"""
    A148 contains ZERO sequences matching the strict signature
    {{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}}.

    Interpretation: the signature does not naturally arise in A148.
    OBSTRUCTION_SHAPE@v1 cannot be falsified or confirmed on A148 with
    its current strict form. Two follow-ups:
      (a) The relaxed signature (n_steps=5, neg_x>=3, has_diag_neg)
          finds {a148['n_matches_relaxed']} matches with kill rate
          {a148['rate_relaxed']:.3f} — informative but the relaxed form
          was already weak on A149 ({a149['rate_relaxed']:.3f}).
      (b) The {a148['n_unanimous_kills_in_family']} A148 sequences killed
          unanimously by F1+F6+F9+F11 represent a separate cluster — they
          may anchor a SISTER OBSTRUCTION_SHAPE candidate with a different
          structural signature. Anti-anchors listed above are starting
          points.

    Conclusion: A148 does not supply the second cross-family anchor for
    OBSTRUCTION_SHAPE@v1. The signature appears to be A149-specific in its
    strict form. This is a calibrated negative result — the kernel
    discipline working as designed.
        """)
    elif a148_above and a149_above:
        print(f"""
    Strict signature predicts unanimous-kill at {a148['rate_match_strict']:.3f}
    on A148 ({a148['n_match_kill_total'][0]}/{a148['n_match_kill_total'][1]})
    AND {a149['rate_match_strict']:.3f} on A149
    ({a149['n_match_kill_total'][0]}/{a149['n_match_kill_total'][1]}).

    Both above threshold {THRESHOLD}. The OBSTRUCTION_SHAPE candidate
    GENERALIZES across families — the second cross-family anchor that
    Ask 3 in stoa/discussions/2026-04-29-sigma-kernel-mvp.md was after.

    Forward path: Harmonia session can post the SYMBOL_PROPOSED message
    from harmonia/memory/symbols/agora_drafts_20260429.md citing this
    cross-family confirmation.
        """)
    elif a148["n_matches_strict"] > 0:
        print(f"""
    Strict signature matches {a148['n_matches_strict']} A148 sequences
    with unanimous-kill rate {a148['rate_match_strict']:.3f}
    ({a148['n_match_kill_total'][0]}/{a148['n_match_kill_total'][1]}).
    Compare A149: {a149['rate_match_strict']:.3f}
    ({a149['n_match_kill_total'][0]}/{a149['n_match_kill_total'][1]}).

    A148 rate is BELOW the {THRESHOLD} threshold. The signature partially
    transfers but is not as predictive on A148 as on A149.

    Two readings:
      (a) The A149 signature is empirically over-fit to its anchor cluster;
          A148 reveals the true population behavior with more variance.
      (b) The structural signature is correct but A148 has a different
          obstruction-mix; matched A148 sequences include true positives
          AND a sister-obstruction class with overlapping signature.

    Either way, this is a calibrated empirical result. The strict
    signature does not survive cross-family at the strong-promotion bar.
    Promotion of OBSTRUCTION_SHAPE@v1 should wait for a refined signature
    that includes the family-distinguishing feature (or the candidate
    splits into two sister obstructions).
        """)


if __name__ == "__main__":
    main()
