"""Cross-catalog H4 audit — test whether the parity > divides > equal
hierarchy replicates beyond knot × EC.

Per James's Fire #23 redirect: the only validation we have for the H4
finding is internal (two-seed replication on the SAME catalog pair). A
much stronger test: do the same rates hold on a DIFFERENT catalog pair?

If knot × genus-2 (or another pair) shows parity ~65%, divides ~30-50%,
equal ~2-3%, the hierarchy is general structure of integer-relation
cross-catalog tests. If rates DIFFER significantly, the hierarchy is
catalog-pair-specific and we shouldn't generalize.

Either outcome is informative.

Methodology:
  1. Sample N (obj_A, obj_B) random pairs from two catalogs
  2. For each pair × (invariant_A, invariant_B) × (relation) tuple,
     test whether the relation holds
  3. For SHADOW (=hold) cases, test categorical extensibility:
     does the relation hold with the SAME obj_A but 2 OTHER
     ec_invariants? (the H4 multi-arrow test)
  4. Report per-relation extensibility rates with stratification
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from theseus.config import REPO_ROOT, THESEUS_ROOT


# -------- Catalog loaders --------

def _load_catalog_entries(path: Path) -> List[Dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get("entries", []))


# Per-catalog integer-invariant lists. Fire #24 filtered out
# `disc_sign` (∈ {-1, 0, +1}) from genus-2 since its 3-value range
# inflated equality+parity rates artifactually.
CATALOG_INVARIANTS = {
    "knot": (
        "crossing_number",
        "signature",
        "determinant",
        "three_genus",
        "trace_field_class",
        "nf_class_number",
    ),
    "ec": (
        "rank",
        "conductor",
        "tamagawa_product",
        "torsion",
    ),
    "genus2": (
        "conductor",
        "abs_disc",
        "analytic_rank",
        "mw_rank",
        "torsion_order",
    ),
    "modular_forms": (
        "level",
        "weight",
        "char_order",
        "a_p_2",  # coefficient at p=2 (synthesized from a_p[0])
        "a_p_3",  # coefficient at p=3 (a_p[1])
        "a_p_5",  # coefficient at p=5 (a_p[2])
    ),
    "oeis_sleeping": (
        "a_number_int",  # numeric part of A-number (e.g., 45 for A000045)
        "first_value",   # data[0]
        "second_value",  # data[1]
        "seq_len",       # len(data) at time of dump
    ),
}


_MF_AP_INDEX = {"a_p_2": 0, "a_p_3": 1, "a_p_5": 2}


def _get_invariant(obj: Dict[str, Any], catalog: str, inv: str) -> Optional[int]:
    """Fetch an integer invariant from an object dict, handling nested schemas."""
    if catalog == "knot":
        v = obj.get(inv)
    elif catalog == "ec":
        v = obj.get(inv)
        if v is None:
            v = obj.get("base", {}).get(inv)
        if v is None:
            v = obj.get("rich", {}).get(inv)
    elif catalog == "genus2":
        v = obj.get(inv)
    elif catalog == "modular_forms":
        if inv in _MF_AP_INDEX:
            ap = obj.get("a_p") or []
            idx = _MF_AP_INDEX[inv]
            v = ap[idx] if idx < len(ap) else None
        else:
            v = obj.get(inv)
    elif catalog == "oeis_sleeping":
        if inv == "a_number_int":
            num_str = obj.get("a_number", "")
            try:
                v = int(num_str[1:]) if num_str.startswith("A") else None
            except (ValueError, IndexError):
                v = None
        elif inv == "first_value":
            data = obj.get("data") or []
            v = data[0] if len(data) >= 1 else None
        elif inv == "second_value":
            data = obj.get("data") or []
            v = data[1] if len(data) >= 2 else None
        elif inv == "seq_len":
            v = len(obj.get("data") or [])
        else:
            v = obj.get(inv)
    else:
        v = obj.get(inv)
    if isinstance(v, (int, float)) and v == int(v):
        return int(v)
    return None


# -------- Relation evaluator (mirrors a1's, including divides-on-zero fix) --------

def evaluate_relation(a_val: int, b_val: int, relation: str) -> bool:
    if relation == "equal":
        return a_val == b_val
    if relation == "equal_mod_2":
        return (a_val % 2) == (b_val % 2)
    if relation == "divides":
        if a_val == 0:
            return b_val == 0
        return (b_val % a_val) == 0
    if relation.startswith("abs_diff_le_"):
        try:
            k = int(relation.split("_")[-1])
            return abs(a_val - b_val) <= k
        except ValueError:
            return False
    return False


RELATIONS = ("equal", "equal_mod_2", "divides", "abs_diff_le_3")


# -------- H4 categorical-bridge test --------

def _h4_extension_test(
    obj_a: Dict[str, Any],
    obj_b: Dict[str, Any],
    catalog_a: str,
    catalog_b: str,
    parent_inv_a: str,
    parent_inv_b: str,
    relation: str,
    rng: random.Random,
    n_extensions: int = 3,
) -> Optional[bool]:
    """For a parent claim that held, test whether 2 of 3 OTHER b-invariants
    also hold. Returns True if ≥2 hold (categorical), False if <2.
    None if can't test (not enough valid extensions)."""
    b_invs = CATALOG_INVARIANTS[catalog_b]
    candidates = [i for i in b_invs if i != parent_inv_b]
    if len(candidates) < n_extensions:
        return None
    new_invs = rng.sample(candidates, n_extensions)
    n_held = 0
    n_tested = 0
    parent_a_val = _get_invariant(obj_a, catalog_a, parent_inv_a)
    if parent_a_val is None:
        return None
    for ni in new_invs:
        new_b = _get_invariant(obj_b, catalog_b, ni)
        if new_b is None:
            continue
        n_tested += 1
        if evaluate_relation(parent_a_val, new_b, relation):
            n_held += 1
    if n_tested < 2:
        return None
    return n_held >= 2


# -------- Main audit loop --------

def audit_catalog_pair(
    catalog_a_name: str,
    catalog_a_entries: List[Dict[str, Any]],
    catalog_b_name: str,
    catalog_b_entries: List[Dict[str, Any]],
    n_samples: int = 5000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run cross-catalog H4-style audit. For each random (obj_A, obj_B,
    inv_A, inv_B, relation) tuple where the parent claim holds, test
    extensibility to 2 of 3 other inv_B."""
    rng = random.Random(seed)
    a_invs = CATALOG_INVARIANTS[catalog_a_name]
    b_invs = CATALOG_INVARIANTS[catalog_b_name]

    # Per-relation totals
    parent_held: Dict[str, int] = defaultdict(int)  # SHADOW parents
    categorical: Dict[str, int] = defaultdict(int)  # H4 SHADOW
    inconclusive: Dict[str, int] = defaultdict(int)
    # Stratified by parent_inv_b
    per_inv_b_held: Dict[tuple, int] = defaultdict(int)
    per_inv_b_cat: Dict[tuple, int] = defaultdict(int)

    n_attempts = 0
    while n_attempts < n_samples:
        obj_a = rng.choice(catalog_a_entries)
        obj_b = rng.choice(catalog_b_entries)
        inv_a = rng.choice(a_invs)
        inv_b = rng.choice(b_invs)
        rel = rng.choice(RELATIONS)
        a_val = _get_invariant(obj_a, catalog_a_name, inv_a)
        b_val = _get_invariant(obj_b, catalog_b_name, inv_b)
        if a_val is None or b_val is None:
            continue
        n_attempts += 1
        if not evaluate_relation(a_val, b_val, rel):
            continue
        # Parent held → test extension
        parent_held[rel] += 1
        per_inv_b_held[(inv_b, rel)] += 1
        ext = _h4_extension_test(
            obj_a, obj_b, catalog_a_name, catalog_b_name,
            inv_a, inv_b, rel, rng,
        )
        if ext is None:
            inconclusive[rel] += 1
        elif ext:
            categorical[rel] += 1
            per_inv_b_cat[(inv_b, rel)] += 1

    # Aggregate rates
    relation_rates = {}
    for rel in RELATIONS:
        total = parent_held[rel]
        cat = categorical[rel]
        relation_rates[rel] = {
            "parent_held": total,
            "categorical": cat,
            "inconclusive": inconclusive[rel],
            "rate": cat / total if total else 0,
        }

    # Stratified by parent_inv_b
    stratified = []
    for (inv_b, rel), n_held in per_inv_b_held.items():
        n_cat = per_inv_b_cat.get((inv_b, rel), 0)
        if n_held < 20:
            continue
        stratified.append({
            "parent_inv_b": inv_b,
            "relation": rel,
            "categorical": n_cat,
            "parent_held": n_held,
            "rate": n_cat / n_held if n_held else 0,
        })
    stratified.sort(key=lambda x: (x["relation"], -x["rate"]))

    return {
        "catalog_a": catalog_a_name,
        "catalog_b": catalog_b_name,
        "n_samples": n_samples,
        "relation_aggregate": relation_rates,
        "stratified": stratified,
    }


# -------- Comparison reporter --------

REPORT_PATH = THESEUS_ROOT / "cross_catalog_h4_report.md"


def render_comparison(audits: List[Dict[str, Any]], reference: Dict[str, Any]) -> str:
    lines = [
        "# Cross-Catalog H4 Audit Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Reference (knot × EC, from corpus_health Fire #19)",
        "",
        "| relation | rate |",
        "|---|---|",
    ]
    for rel, r in reference.items():
        lines.append(f"| {rel} | {100*r:.1f}% |")

    for audit in audits:
        lines += [
            "",
            f"## Audit: {audit['catalog_a']} × {audit['catalog_b']} "
            f"(n={audit['n_samples']:,})",
            "",
            "### Aggregate rates",
            "",
            "| relation | categorical / held | rate |",
            "|---|---|---|",
        ]
        for rel, r in audit["relation_aggregate"].items():
            rate_pct = 100 * r["rate"]
            lines.append(
                f"| {rel} | {r['categorical']} / {r['parent_held']} | {rate_pct:.1f}% |"
            )
        lines += [
            "",
            "### Stratified by parent_inv_b",
            "",
            "| parent_inv_b | relation | rate |",
            "|---|---|---|",
        ]
        for r in audit["stratified"]:
            lines.append(
                f"| {r['parent_inv_b']} | {r['relation']} | "
                f"{r['categorical']}/{r['parent_held']} = {100*r['rate']:.1f}% |"
            )

    lines += ["", "## Replication verdict", ""]
    # Compute drift between catalog pairs for parity / divides / equal
    if audits:
        new_pair = audits[0]
        for rel in ("equal_mod_2", "divides", "equal"):
            ref_rate = reference.get(rel, 0)
            new_rate = new_pair["relation_aggregate"].get(rel, {}).get("rate", 0)
            drift = (new_rate - ref_rate) * 100
            verdict = (
                "REPLICATES" if abs(drift) < 10
                else "DIFFERS"
            )
            lines.append(
                f"- **{rel}**: ref {100*ref_rate:.1f}% vs new {100*new_rate:.1f}% "
                f"(drift {drift:+.1f}pp) → {verdict}"
            )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.scoring.cross_catalog_h4_audit")
    parser.add_argument("--n-samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    # Load catalogs
    knots = _load_catalog_entries(REPO_ROOT / "prometheus_math/databases/knots.json.gz")
    genus2 = _load_catalog_entries(REPO_ROOT / "prometheus_math/databases/genus2.json.gz")
    mf = _load_catalog_entries(REPO_ROOT / "prometheus_math/databases/modular_forms.json.gz")
    oeis = _load_catalog_entries(REPO_ROOT / "prometheus_math/databases/oeis_sleeping.json.gz")

    # Reference: from Fire #19 corpus_health
    reference = {
        "equal": 0.026,
        "equal_mod_2": 0.672,
        "divides": 0.507,  # aggregate; conductor-anchored ~0.33
        "abs_diff_le_3": 0.65,  # using abs_diff_le_* aggregate as proxy
    }

    audits = []
    for cat_b_name, cat_b_entries in (
        ("genus2", genus2),
        ("modular_forms", mf),
        ("oeis_sleeping", oeis),
    ):
        print(f"[cross-cat] Auditing knot × {cat_b_name} (n={args.n_samples})...")
        audit = audit_catalog_pair(
            "knot", knots, cat_b_name, cat_b_entries,
            n_samples=args.n_samples, seed=args.seed,
        )
        audits.append(audit)
        for rel, r in audit["relation_aggregate"].items():
            print(f"[cross-cat] {cat_b_name:<14} {rel:<15} held={r['parent_held']:<6} cat={r['categorical']:<6} rate={100*r['rate']:5.1f}%")

    report = render_comparison(audits, reference)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"[cross-cat] Wrote {args.output}")


if __name__ == "__main__":
    main()
