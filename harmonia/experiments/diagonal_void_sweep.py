"""diagonal_void_sweep.py — same-object lattice mining (Harmonia D, 2026-06-10).

The a3 result proves cross-catalog (product-measure) void mining reduces to
marginal facts. THIS sweep is the live direction the adversarial panel ranked
first: rel(f(inv_i(O)), g(inv_j(O))) over the SAME object O — within-object
coupling, where the re-pairing null is informative and a D_JOINT void is a
candidate inter-invariant law of the catalog.

Runs both catalogs:
  EC side   1000 curves, invariants (rank, conductor, tamagawa_product,
            torsion): 6f x 6g x 12 ordered pairs x 4 rel = 1728 cells
  knot side 52 knots, 6 invariants: 6 x 6 x 30 x 4 = 4320 cells (THIN —
            n=52; every verdict carries the thin-support caveat)

Emits harmonia/experiments/diagonal_void_results.json (flushed from Python).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a3_functional_identity import OPERATORS                 # noqa: E402
from theseus.generators.a1_catalog_cross_product import (                       # noqa: E402
    _load_catalog, _get_int,
    KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS, RELATIONS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH                      # noqa: E402
from harmonia.primitives.lattice_void_miner import evaluate_diagonal_lattice    # noqa: E402
from theseus.generators.a1_catalog_cross_product import _evaluate_relation      # noqa: E402


def aligned_side(objects, invariants):
    """invariant -> per-object value list, None-preserving (alignment = object
    identity, which is exactly the joint signal the diagonal lattice probes)."""
    return {inv: [_get_int(o, inv) for o in objects] for inv in invariants}


def run(name, objects, invariants):
    side = aligned_side(objects, invariants)
    cells = evaluate_diagonal_lattice(
        side, dict(OPERATORS), tuple(RELATIONS), _evaluate_relation)
    voids = [c for c in cells if c["is_exact_void"]]
    joint = [c for c in voids if c.get("joint_class") == "D_JOINT"]
    marginal = [c for c in voids if c.get("joint_class") == "D_MARGINAL"]
    print(f"\n=== {name}: {len(cells)} cells over n={max(c['n_eval'] for c in cells)} "
          f"objects ===")
    print(f"  exact voids: {len(voids)}  (D_MARGINAL={len(marginal)}, "
          f"D_JOINT={len(joint)})")
    print(f"  D_JOINT voids (candidate within-catalog laws; "
          f"perm_null_void_rate = P(survives column shuffle)):")
    for c in sorted(joint, key=lambda x: x["perm_null_void_rate"]):
        print(f"    {c['f']}({c['inv_a']}) {c['rel']} {c['g']}({c['inv_b']})"
              f"  n={c['n_eval']}  perm_null={c['perm_null_void_rate']:.3f}")
    near = sorted((c for c in cells if not c["is_exact_void"]
                   and c["hold_rate"] >= 0.99),
                  key=lambda x: -x["hold_rate"])
    print(f"  near-voids >=0.99: {len(near)}")
    for c in near[:8]:
        print(f"    {c['f']}({c['inv_a']}) {c['rel']} {c['g']}({c['inv_b']})"
              f"  hold={c['hold_rate']:.5f} "
              f"({c['n_eval']-c['hold_count']}/{c['n_eval']} violations)")
    return {"name": name, "n_cells": len(cells),
            "n_voids": len(voids), "n_joint": len(joint),
            "n_marginal": len(marginal),
            "joint_voids": joint, "marginal_voids_sample": marginal[:50],
            "near_voids": near[:40]}


def main():
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    out = {
        "meta": {"date": "2026-06-10", "author": "Harmonia_M2_D",
                 "design": "same-object diagonal lattice; product-measure "
                           "theorem does NOT apply; permutation null is "
                           "informative; D_JOINT = candidate law",
                 "caveats": ["EC catalog quota-stratified (rank 500/400/100)",
                             "knot side n=52 THIN",
                             "single-catalog facts; extension untested"]},
        "ec": run("EC diagonal (n=1000)", ecs, EC_INTEGER_INVARIANTS),
        "knot": run("knot diagonal (n=52, THIN)", knots, KNOT_INTEGER_INVARIANTS),
    }
    path = Path(__file__).parent / "diagonal_void_results.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
