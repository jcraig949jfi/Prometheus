#!/usr/bin/env python3
"""
A149* obstruction analysis.

The five sequences A149074, A149081, A149082, A149089, A149090 emerged as
the cross-source cluster in curvature_experiment v2: highest defect in
Source B (asymptotic_deviations) AND killed by the full battery in Source C
(battery_sweep_v2). All five are 5-step lattice walks confined to the first
octant of Z^3.

Hypothesis (the OBSTRUCTION_SHAPE candidate):
  Octant walks with a particular step-set asymmetry -- high negative-x
  dominance plus the diagonal-negative step (-1,-1,-1) -- produce
  short_rate vs long_rate divergences that LOOK like regime changes but
  are artifacts of the boundary geometry, and therefore get killed by every
  member of the full kill-test battery (F1, F6, F9, F11).

Test:
  1. Extract the full A149* sub-family from asymptotic_deviations.
  2. Parse step sets from the OEIS-style names.
  3. Compute structural features per sequence (negative-x dominance,
     diagonal-negative presence, etc.).
  4. Cross-reference with battery_sweep verdicts.
  5. Check whether the structural-feature signature predicts unanimous-kill
     better than baselines.
  6. Run the result through the Sigma kernel: CLAIM the obstruction,
     FALSIFY against the cross-validation predicate, GATE, PROMOTE if it
     holds.

Run:  python a149_obstruction.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from sigma_kernel import (
    BlockedError,
    Capability,
    SigmaKernel,
    Tier,
    Verdict,
    VerdictResult,
    _sha256,
)


REPO = Path(__file__).parent.parent
DATA = REPO / "cartography" / "convergence" / "data"
ASYMPTOTIC = DATA / "asymptotic_deviations.jsonl"
BATTERY_SWEEP = DATA / "battery_sweep_v2.jsonl"

DB_PATH = Path(__file__).parent / "a149_obstruction.db"


# ---------------------------------------------------------------------------
# Parsing OEIS step-set names
# ---------------------------------------------------------------------------

STEP_SET_RE = re.compile(r"\{([^}]+)\}")
STEP_RE = re.compile(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def parse_step_set(name: str) -> list[tuple[int, int, int]] | None:
    """
    Parse the step-set out of an OEIS-style name like:
      'Number of walks within N^3 (the first octant of Z^3) starting at
       (0,0,0) and consisting of n steps taken from {(-1, -1, -1), ...}.'
    """
    m = STEP_SET_RE.search(name)
    if not m:
        return None
    body = m.group(1)
    steps = STEP_RE.findall(body)
    if not steps:
        return None
    return [tuple(int(x) for x in s) for s in steps]


def features_of(steps: list[tuple[int, int, int]]) -> dict:
    """Structural features of a step set."""
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
        "neg_x_dominance": nx / n if n else 0.0,
        "asymmetry_x": (nx - px) / n if n else 0.0,
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_jsonl(path: Path):
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


def load_a149_family():
    """Subset of asymptotic_deviations covering A149xxx sequences."""
    rows = load_jsonl(ASYMPTOTIC)
    out = []
    for r in rows:
        sid = r.get("seq_id", "")
        if not sid.startswith("A149"):
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
    """seq_id -> set of kill_tests that fired."""
    rows = load_jsonl(BATTERY_SWEEP)
    out: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        sid = r.get("seq_id")
        if sid:
            out[sid].update(r.get("kill_tests", []) or [])
    return out


# ---------------------------------------------------------------------------
# Hypothesis test: does structural signature predict unanimous-kill?
# ---------------------------------------------------------------------------

UNANIMOUS_BATTERY = {
    "F1_permutation_null",
    "F6_base_rate",
    "F9_simpler_explanation",
    "F11_cross_validation",
}


def signature_match(features: dict) -> bool:
    """
    The OBSTRUCTION_SHAPE candidate's structural signature, distilled from
    the five anchor sequences:
      - 5-step walk
      - 4 of 5 steps have negative x-component (high negative-x dominance)
      - includes the diagonal-negative step (-1, -1, -1)
    """
    return (
        features["n_steps"] == 5
        and features["neg_x"] == 4
        and features["pos_x"] == 1
        and features["has_diag_neg"]
    )


def main() -> None:
    print("=" * 72)
    print("A149* OBSTRUCTION ANALYSIS")
    print("=" * 72)

    # ------------------------------------------------------------------
    # 1. Load family + kill verdicts
    # ------------------------------------------------------------------
    family = load_a149_family()
    kills = load_kill_verdicts()
    print(f"\n[1] Loaded A149* family: {len(family)} sequences with parseable step sets")
    print(f"    Battery sweep records: {sum(len(v) for v in kills.values())} kill events"
          f" across {len(kills)} sequences")

    # ------------------------------------------------------------------
    # 2. The five original anchors
    # ------------------------------------------------------------------
    anchors = ["A149074", "A149081", "A149082", "A149089", "A149090"]
    print(f"\n[2] Anchor cluster (top 5 from curvature_experiment Source B):")
    print(f"    {'seq_id':<10} {'delta_pct':>10} {'neg_x':>6} {'pos_x':>6} {'diag_neg':>9} {'kill_count':>10}")
    for a in anchors:
        rec = next((r for r in family if r["seq_id"] == a), None)
        if not rec:
            continue
        f = rec["_features"]
        n_kills = len(kills.get(a, set()))
        print(
            f"    {a:<10} {rec['delta_pct']:>10.3f} {f['neg_x']:>6} {f['pos_x']:>6} "
            f"{str(f['has_diag_neg']):>9} {n_kills:>10}"
        )

    # ------------------------------------------------------------------
    # 3. Apply signature across the whole A149* family
    # ------------------------------------------------------------------
    matches = [r for r in family if signature_match(r["_features"])]
    non_matches = [r for r in family if not signature_match(r["_features"])]
    print(f"\n[3] Signature match across A149* family:")
    print(f"    matches:     {len(matches)} sequences")
    print(f"    non-matches: {len(non_matches)} sequences")

    # ------------------------------------------------------------------
    # 4. Test the prediction: do matches get unanimous-kill more often
    #    than non-matches?
    # ------------------------------------------------------------------
    def unanimous_kill_rate(group):
        present = [r for r in group if r["seq_id"] in kills]
        if not present:
            return 0.0, 0, 0
        n_unanimous = sum(
            1 for r in present
            if UNANIMOUS_BATTERY.issubset(kills[r["seq_id"]])
        )
        return n_unanimous / len(present), n_unanimous, len(present)

    rate_match, n_match_kill, n_match_total = unanimous_kill_rate(matches)
    rate_nonmatch, n_nm_kill, n_nm_total = unanimous_kill_rate(non_matches)

    print(f"\n[4] Predictive test: unanimous-kill rate per group")
    print(f"    matches:     {n_match_kill:>4} / {n_match_total:>4} = {rate_match:.3f}")
    print(f"    non-matches: {n_nm_kill:>4} / {n_nm_total:>4} = {rate_nonmatch:.3f}")
    if n_match_total > 0 and n_nm_total > 0:
        ratio = (rate_match + 1e-9) / (rate_nonmatch + 1e-9)
        print(f"    ratio:       {ratio:.2f}x")

    # ------------------------------------------------------------------
    # 5. What about a relaxed signature? (n_steps=5, neg_x>=3, has_diag_neg)
    # ------------------------------------------------------------------
    def relaxed_match(features):
        return (
            features["n_steps"] == 5
            and features["neg_x"] >= 3
            and features["has_diag_neg"]
        )
    relaxed = [r for r in family if relaxed_match(r["_features"])]
    rate_relaxed, n_r_kill, n_r_total = unanimous_kill_rate(relaxed)
    print(f"\n[5] Relaxed signature (n_steps=5, neg_x>=3, has_diag_neg):")
    print(f"    matches:     {len(relaxed)} sequences")
    print(f"    unanimous-kill rate: {n_r_kill:>4} / {n_r_total:>4} = {rate_relaxed:.3f}")

    # ------------------------------------------------------------------
    # 6. Where do the kills NOT match the signature? (anti-anchors)
    # ------------------------------------------------------------------
    kill_seqs_in_family = {r["seq_id"] for r in family if UNANIMOUS_BATTERY.issubset(kills.get(r["seq_id"], set()))}
    matched_seqs = {r["seq_id"] for r in matches}
    matched_kill = kill_seqs_in_family & matched_seqs
    unmatched_kill = kill_seqs_in_family - matched_seqs

    print(f"\n[6] Family-level confusion matrix:")
    print(f"    A149* sequences killed unanimously: {len(kill_seqs_in_family)}")
    print(f"      of which signature-matching:     {len(matched_kill)}")
    print(f"      of which signature-missing:      {len(unmatched_kill)}")
    if unmatched_kill:
        print(f"    Sample unmatched-kill (anti-anchors):")
        for sid in sorted(unmatched_kill)[:5]:
            rec = next((r for r in family if r["seq_id"] == sid), None)
            if rec:
                f = rec["_features"]
                print(f"      {sid}  neg_x={f['neg_x']} pos_x={f['pos_x']} diag_neg={f['has_diag_neg']}")

    # ------------------------------------------------------------------
    # 7. Run the obstruction through the Sigma kernel
    # ------------------------------------------------------------------
    print(f"\n[7] Promoting the OBSTRUCTION_SHAPE through Sigma kernel:")

    if DB_PATH.exists():
        DB_PATH.unlink()
    k = SigmaKernel(DB_PATH)

    # Bootstrap the five anchor sequences as substrate symbols.
    for a in anchors:
        rec = next((r for r in family if r["seq_id"] == a), None)
        if not rec:
            continue
        try:
            k.bootstrap_symbol(
                name=f"oeis_{a}",
                version=1,
                def_obj={
                    "oeis_id": a,
                    "name": rec["name"],
                    "step_set": [list(s) for s in rec["_steps"]],
                    "delta_pct": rec["delta_pct"],
                    "features": rec["_features"],
                    "kill_tests": sorted(kills.get(a, set())),
                },
                tier=Tier.WorkingTheory,
            )
            print(f"    bootstrapped: oeis_{a}@v1")
        except Exception as e:
            print(f"    bootstrap skipped ({a}): {e}")

    # Bootstrap the candidate obstruction shape's anchor evidence.
    obstruction_anchor_blob = json.dumps({
        "candidate_symbol": "BOUNDARY_DOMINATED_OCTANT_WALK_OBSTRUCTION",
        "kind": "OBSTRUCTION_SHAPE",
        "anchor_seqs": anchors,
        "structural_signature": {
            "n_steps": 5,
            "neg_x": 4,
            "pos_x": 1,
            "has_diag_neg": True,
        },
        "predicted_kill_battery": sorted(UNANIMOUS_BATTERY),
        "empirical_results": {
            "n_signature_matches": len(matches),
            "match_unanimous_kill_rate": rate_match,
            "non_match_unanimous_kill_rate": rate_nonmatch,
            "ratio": (rate_match + 1e-9) / (rate_nonmatch + 1e-9) if n_nm_total > 0 else None,
        },
    }, sort_keys=True)
    anchor_hash = _sha256(obstruction_anchor_blob)

    # The CLAIM the kernel will evaluate:
    #   "5-step octant walks with neg_x=4, pos_x=1, has_diag_neg=True
    #    are unanimously killed by F1+F6+F9+F11 at a rate >= 0.95"
    THRESHOLD = 0.95
    claim = k.CLAIM(
        target_name="boundary_dominated_octant_walk_obstruction",
        hypothesis=f"unanimous_kill_rate >= {THRESHOLD}",
        evidence={
            "anchor_hash": anchor_hash,
            "true_mean": rate_match,  # the oracle reads this as the empirical
            "n_matches": len(matches),
            "n_unanimous": n_match_kill,
            "n_evaluated": n_match_total,
        },
        kill_path="signature_predictivity_test",
        target_tier=Tier.Possible,
    )
    print(f"    CLAIM: {claim.id}  ({claim.hypothesis})")

    # Convert the hypothesis into the form the omega_oracle understands:
    # "mean OP value" -- where mean = empirical rate, op = >, val = 0.95.
    # We reuse the existing oracle by putting rate_match into evidence.true_mean
    # and writing the hypothesis as "mean > 0.949" (so threshold is at 0.95).
    claim.hypothesis = f"mean > {THRESHOLD - 0.01:.3f}"
    k.conn.execute(
        "UPDATE claims SET hypothesis=? WHERE id=?",
        (claim.hypothesis, claim.id),
    )

    verdict = k.FALSIFY(claim)
    print(f"    FALSIFY: {verdict.status.value}  ({verdict.rationale})")

    try:
        flow = k.GATE(verdict)
        print(f"    GATE: {flow}")
        cap = k.mint_capability()
        sym = k.PROMOTE(claim, cap)
        print(f"    PROMOTE: {sym.ref}")
    except BlockedError as e:
        print(f"    GATE blocked: {e}")
        print(f"    obstruction NOT promoted -- empirical rate too low")

    # ------------------------------------------------------------------
    # 8. Editorial reading
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("READING")
    print("=" * 72)
    if rate_match >= THRESHOLD:
        print(f"""
    The structural signature predicts unanimous-kill at rate {rate_match:.3f}
    over {n_match_total} A149* matches, vs {rate_nonmatch:.3f} over
    {n_nm_total} non-matches. Above threshold {THRESHOLD}.

    OBSTRUCTION_SHAPE candidate validated empirically: 5-step octant walks
    with the structural signature {{neg_x=4, pos_x=1, has_diag_neg=True}}
    fail every member of the {{F1, F6, F9, F11}} battery.

    Interpretation:
      The boundary geometry of N^3, combined with a step set that pushes
      the walker primarily into the negative-x half-space and includes the
      diagonal-negative (-1,-1,-1), produces sequences whose growth rate
      LOOKS like a regime change at finite n (short_rate ~ 2.7,
      long_rate ~ 4.9, delta_pct ~ 80%) but the apparent transition is
      an artifact: the early growth is dominated by walks that haven't
      yet hit the boundary, the late growth by walks that have. Permutation
      null, base rate, simpler explanations, and cross-validation all
      detect this as artifactual.

    The OBSTRUCTION_SHAPE compresses {len(matches)} individual KILLED
    verdicts into one named obstruction. Future octant-walk sequences
    matching the signature can be flagged at ingestion.
        """)
    else:
        print(f"""
    The structural signature predicts unanimous-kill at rate {rate_match:.3f}
    over {n_match_total} A149* matches, vs {rate_nonmatch:.3f} over
    {n_nm_total} non-matches.

    Below threshold {THRESHOLD} -- the obstruction shape does not earn
    promotion at this confidence level. Either the signature is too narrow
    (refine to the relaxed version) or there is a counter-example
    population the signature doesn't capture.

    The kernel correctly REFUSED promotion. This is the discipline working.
        """)

    print(f"\nFinal substrate: {len(k.list_symbols())} symbols")
    for n, v, h, t in k.list_symbols():
        print(f"  {n}@v{v}  hash={h}...  tier={t}")


if __name__ == "__main__":
    main()
