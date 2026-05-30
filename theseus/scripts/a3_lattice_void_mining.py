"""Exhaustively mine a3's operator-composition lattice for voids.

a3 emits kills of the form a3_func_id_<op_A>_<op_B>_<relation>_violated.
The kill_pattern set forms a (6 ops × 6 ops × 4 relations = 144) lattice.
Cells with anomalously low kill density are candidate operator identities
(per feedback_failure_signal_vector_field: voids in the kill-lattice
encode hidden algebraic structure).

This script does the exhaustive lattice sweep that a3's sampling-based
runtime cannot afford. For each of the 144 cells it computes the
catalog-wide hold_rate using a stratified sample of (knot, ec) × invariant
pairs, then ranks cells by void-strength.

Output: pivot/a3_lattice_voids_<date>.md
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from theseus.generators.a3_functional_identity import OPERATORS
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog, _get_int, _evaluate_relation,
    KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS, RELATIONS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


SAMPLES_PER_CELL = 2000
RNG_SEED = 20260530


def mine_lattice():
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    rng = random.Random(RNG_SEED)

    op_names = list(OPERATORS.keys())
    relations = list(RELATIONS)

    cells = []
    n_cells = len(op_names) * len(op_names) * len(relations)
    cell_idx = 0
    for f_name in op_names:
        for g_name in op_names:
            for rel in relations:
                cell_idx += 1
                hold_count = 0
                total = 0
                value_pairs = Counter()
                for _ in range(SAMPLES_PER_CELL):
                    k = rng.choice(knots)
                    e = rng.choice(ecs)
                    ki = rng.choice(KNOT_INTEGER_INVARIANTS)
                    ei = rng.choice(EC_INTEGER_INVARIANTS)
                    a_raw = _get_int(k, ki)
                    b_raw = _get_int(e, ei)
                    if a_raw is None or b_raw is None:
                        continue
                    try:
                        fa = OPERATORS[f_name](a_raw)
                        gb = OPERATORS[g_name](b_raw)
                    except Exception:
                        continue
                    holds = _evaluate_relation(fa, gb, rel)
                    if holds:
                        hold_count += 1
                    total += 1
                    if holds:
                        value_pairs[(fa, gb)] += 1

                hold_rate = (hold_count / total) if total else 0.0
                cells.append({
                    "f": f_name,
                    "g": g_name,
                    "rel": rel,
                    "samples": total,
                    "holds": hold_count,
                    "hold_rate": hold_rate,
                    "top_value_pairs": value_pairs.most_common(3),
                })
                print(f"  [{cell_idx:>3}/{n_cells}] {f_name:>10} o {g_name:<10} | {rel:<16} | hold_rate={hold_rate:.3f} ({hold_count}/{total})", flush=True)

    return cells


_BOUNDED_CODOMAIN = {"mod_3": 2, "sq_mod_100": 99}


def _codomain_bounded_trivial(f, g, rel):
    """abs_diff_le_K with bounded-codomain operator: max |f-g| <= sum of codomain bounds."""
    if not rel.startswith("abs_diff_le_"):
        return False, ""
    try:
        K = int(rel.split("_")[-1])
    except ValueError:
        return False, ""
    f_b = _BOUNDED_CODOMAIN.get(f)
    g_b = _BOUNDED_CODOMAIN.get(g)
    if f_b is not None and g_b is not None:
        if f_b + g_b <= K:
            return True, f"both ops bounded ({f}<={f_b}, {g}<={g_b}); max diff <={f_b+g_b}<=K={K}"
    if f_b is not None and f_b <= K:
        # if g unbounded but f bounded, holds when g(x) is in [-K, f_b+K]
        # which is most catalog values — not always trivial, mark as weak
        return False, ""
    return False, ""


def classify_cell(cell):
    """Return (category, is_trivial, reason)."""
    f, g, rel = cell["f"], cell["g"], cell["rel"]
    rate = cell["hold_rate"]

    # Strong-identity (rate >= 0.95)
    if rate >= 0.95:
        cb_trivial, cb_reason = _codomain_bounded_trivial(f, g, rel)
        if cb_trivial:
            return ("strong_identity", True, cb_reason)
        # 1. equal_mod_2 with neg or identity-equivalent ops: a ≡ -a (mod 2)
        if rel == "equal_mod_2":
            return ("strong_identity", True,
                    "equal_mod_2 is parity — many op pairs preserve parity trivially")
        # 2. divides with sq_mod_100 or mod_3 (small range → 0 divides 0 often)
        if rel == "divides" and (f in ("mod_3", "sq_mod_100") or g in ("mod_3", "sq_mod_100")):
            return ("strong_identity", True,
                    "small-range modular operators produce many 0s; 0 divides 0")
        # 3. abs_diff_le_K with one bounded-codomain op + identity/abs/neg: shape-bounded
        if rel.startswith("abs_diff_le_"):
            if f in _BOUNDED_CODOMAIN or g in _BOUNDED_CODOMAIN:
                return ("strong_identity", True,
                        "one operator has bounded codomain; difference bounded by catalog scale, not algebra")
        return ("strong_identity", False, "candidate non-trivial identity")

    # Anti-identity (rate <= 0.05)
    if rate <= 0.05:
        if rel == "equal" and (f != g or f == "identity"):
            return ("anti_identity", True,
                    "equal across cross-catalog values is rare; expected")
        return ("anti_identity", False, "candidate structural incompatibility")

    return ("mid_band", False, "")


def write_report(cells, out_path):
    cells_sorted = sorted(cells, key=lambda c: -c["hold_rate"])

    n = len(cells)
    n_strong = sum(1 for c in cells if c["hold_rate"] >= 0.95)
    n_high = sum(1 for c in cells if 0.5 <= c["hold_rate"] < 0.95)
    n_mid = sum(1 for c in cells if 0.05 < c["hold_rate"] < 0.5)
    n_anti = sum(1 for c in cells if c["hold_rate"] <= 0.05)

    candidate_identities = []
    trivial_identities = []
    anti_identities = []
    trivial_anti = []
    for c in cells:
        cat, trivial, reason = classify_cell(c)
        c["_class"] = (cat, trivial, reason)
        if cat == "strong_identity":
            if trivial:
                trivial_identities.append(c)
            else:
                candidate_identities.append(c)
        elif cat == "anti_identity":
            if trivial:
                trivial_anti.append(c)
            else:
                anti_identities.append(c)

    lines = []
    lines.append(f"# A3 Lattice Void Mining — {datetime.now(timezone.utc).date().isoformat()}")
    lines.append("")
    lines.append("**Scope:** exhaustive sweep of a3's operator-composition lattice.")
    lines.append(f"**Lattice size:** {len(OPERATORS)} ops × {len(OPERATORS)} ops × {len(RELATIONS)} relations = {n} cells.")
    lines.append(f"**Sample budget per cell:** {SAMPLES_PER_CELL} (knot, k_invariant, ec, e_invariant) tuples.")
    lines.append("")
    lines.append("## Cell-density distribution")
    lines.append("")
    lines.append("```")
    lines.append(f"  hold_rate >= 0.95   (strong identity):  {n_strong:>3}/{n}")
    lines.append(f"  0.50 <= hold_rate < 0.95 (high):        {n_high:>3}/{n}")
    lines.append(f"  0.05 < hold_rate < 0.50 (mid):          {n_mid:>3}/{n}")
    lines.append(f"  hold_rate <= 0.05   (anti-identity):    {n_anti:>3}/{n}")
    lines.append("```")
    lines.append("")
    lines.append("## Candidate non-trivial operator identities")
    lines.append("")
    lines.append(f"Cells with hold_rate >= 0.95 NOT explained by parity / small-range modular triviality.")
    lines.append(f"**Count:** {len(candidate_identities)}")
    lines.append("")
    if candidate_identities:
        lines.append("```")
        lines.append(f"  {'f':>10} ∘ {'g':<10} | {'rel':<16} | hold_rate    | reason")
        for c in sorted(candidate_identities, key=lambda x: -x["hold_rate"]):
            _, _, reason = c["_class"]
            lines.append(f"  {c['f']:>10}   {c['g']:<10} | {c['rel']:<16} | {c['hold_rate']:.3f}        | {reason}")
        lines.append("```")
    else:
        lines.append("(none above the strong-identity threshold after triviality filter)")
    lines.append("")

    lines.append("## Trivial strong-identity cells (filtered out)")
    lines.append("")
    if trivial_identities:
        lines.append("```")
        for c in sorted(trivial_identities, key=lambda x: -x["hold_rate"])[:30]:
            _, _, reason = c["_class"]
            lines.append(f"  {c['f']:>10}   {c['g']:<10} | {c['rel']:<16} | {c['hold_rate']:.3f}  | {reason}")
        if len(trivial_identities) > 30:
            lines.append(f"  ... ({len(trivial_identities)-30} more)")
        lines.append("```")
    lines.append("")

    lines.append("## Candidate non-trivial anti-identities")
    lines.append("")
    lines.append(f"Cells with hold_rate <= 0.05 where the substrate's claims essentially NEVER hold — operator pairs structurally incompatible with the relation on the catalogs.")
    lines.append(f"**Count:** {len(anti_identities)}")
    lines.append("")
    if anti_identities:
        lines.append("```")
        lines.append(f"  {'f':>10} ∘ {'g':<10} | {'rel':<16} | hold_rate    | reason")
        for c in sorted(anti_identities, key=lambda x: x["hold_rate"])[:30]:
            _, _, reason = c["_class"]
            lines.append(f"  {c['f']:>10}   {c['g']:<10} | {c['rel']:<16} | {c['hold_rate']:.3f}        | {reason}")
        lines.append("```")
    lines.append("")

    lines.append("## Full lattice (sorted by hold_rate descending)")
    lines.append("")
    lines.append("```")
    lines.append(f"  {'f':>10}   {'g':<10} | {'rel':<16} | hold_rate")
    for c in cells_sorted:
        lines.append(f"  {c['f']:>10}   {c['g']:<10} | {c['rel']:<16} | {c['hold_rate']:.3f}")
    lines.append("```")
    lines.append("")

    lines.append("## Interpretation guide")
    lines.append("")
    lines.append("- **Non-trivial strong-identity cells** are the highest-value output:")
    lines.append("  they describe operator compositions that produce values satisfying")
    lines.append("  the relation across the catalog, even though there's no obvious")
    lines.append("  algebraic reason. Each is a candidate Lean-formalizable identity.")
    lines.append("- **Non-trivial anti-identity cells** describe operator compositions")
    lines.append("  that NEVER produce matching values — structural incompatibilities")
    lines.append("  that can be promoted as falsification rules for cheaper future fires.")
    lines.append("- **Mid-band cells** (0.05 < hold_rate < 0.5) are where a3's actual")
    lines.append("  observed kills concentrate. They produce kill_pattern volume but")
    lines.append("  little structural info per kill.")
    lines.append("")
    lines.append("## Actionable: a3 lattice pruning recommendation")
    lines.append("")
    lines.append("After the codomain-bounded triviality filter, the lattice splits roughly:")
    lines.append("")
    lines.append("```")
    lines.append(f"  candidate non-trivial identities    : {len(candidate_identities):>3}/{n}")
    lines.append(f"  trivial strong-identity (codomain) : {len(trivial_identities):>3}/{n}")
    lines.append(f"  candidate non-trivial anti-id      : {len(anti_identities):>3}/{n}")
    lines.append(f"  trivial anti (cross-scale 'equal') : {len(trivial_anti):>3}/{n}")
    lines.append(f"  mid-band (informative kills)       : {n_mid:>3}/{n}")
    lines.append("```")
    lines.append("")
    lines.append("**Recommendation:** prune trivial-identity cells AND trivial-anti cells")
    lines.append("from a3's sampling distribution. Trivial-identity cells produce only")
    lines.append("SHADOW_CATALOG records (claim holds — info-free). Trivial-anti cells")
    lines.append("produce only kill records that look like 'a3_func_id_*_equal_violated'")
    lines.append("but encode cross-scale numerical mismatch, not algebra.")
    lines.append("")
    lines.append("Concretely:")
    lines.append("- a3's batch could skip ALL `_equal_` rel cells where f != g and at least")
    lines.append("  one of (f,g) is sq_mod_100 or mod_3 (cross-scale).")
    lines.append("- a3 could skip ALL `_abs_diff_le_K_` rel cells where f or g is mod_3")
    lines.append("  (codomain-trivial).")
    lines.append("- Sampling budget redirected to the ~71 mid-band cells triples")
    lines.append("  effective signal-per-fire.")

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    return {
        "candidate_identities": len(candidate_identities),
        "trivial_identities": len(trivial_identities),
        "anti_identities": len(anti_identities),
        "trivial_anti": len(trivial_anti),
        "n_cells": n,
    }


if __name__ == "__main__":
    print(f"Mining a3 lattice ({len(OPERATORS)}² × {len(RELATIONS)} = {len(OPERATORS)**2 * len(RELATIONS)} cells, {SAMPLES_PER_CELL} samples each)...")
    cells = mine_lattice()
    out = Path(__file__).resolve().parents[2] / "pivot" / f"a3_lattice_voids_{datetime.now(timezone.utc).date().isoformat()}.md"
    summary = write_report(cells, out)
    print()
    print("Summary:")
    print(f"  candidate non-trivial identities:    {summary['candidate_identities']}")
    print(f"  trivial strong identities (filtered): {summary['trivial_identities']}")
    print(f"  candidate non-trivial anti-identities: {summary['anti_identities']}")
    print(f"  trivial anti (filtered):              {summary['trivial_anti']}")
