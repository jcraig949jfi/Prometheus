"""Genus-2 curve corpus loader for the Stage 0b relational EXPANSION (v0.3).

The H-R1 NULL on in-band Mahler polynomials was corpus-limited (criteria barely varied
across 21 near-identical states). Genus-2 curves give a large, HETEROGENEOUS corpus
(66k curves) with many trading-off invariants -- a mix of arithmetic-hardness
(analytic_rank, mw_rank, analytic_sha, two_selmer_rank) and structural (cond, abs_disc,
torsion_order, tamagawa_product, num_rat_pts). The comparison criteria are ALL numeric
scalar fields except the row id (no cherry-pick); the Condorcet sign-flow is
scale-invariant so no normalization is needed.

This produces records with a `margins` key (the criteria vector) so they feed directly
into the existing `runner.run_h_r1` / relational pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path

__all__ = ["load_g2c_states", "G2C_SOURCE", "EXCLUDED_FIELDS"]

G2C_SOURCE = "cartography/lmfdb_dump/g2c_curves.json"
EXCLUDED_FIELDS = {"id"}            # row id is not a mathematical criterion


def _numeric_criteria(rec: dict) -> dict:
    out = {}
    for k, v in rec.items():
        if k in EXCLUDED_FIELDS:
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            out[k] = float(v)
    return out


def load_g2c_states(n: int = 40, source: str = G2C_SOURCE) -> list:
    """Return n genus-2 curve states, deterministically STRATIFIED across the table
    (every floor(total/n)-th record, so the sample spans the conductor/disc range
    rather than an id-prefix window). Each state: {label, margins: {criterion: value}}.
    """
    if n < 2:
        raise ValueError("need n >= 2 states")
    obj = json.loads(Path(source).read_text(encoding="utf-8"))
    recs = obj["records"]
    total = len(recs)
    if n > total:
        raise ValueError(f"n={n} exceeds available {total} curves")
    stride = total // n
    picked = [recs[i * stride] for i in range(n)]
    states = []
    for r in picked:
        states.append({
            "label": str(r.get("label") or r.get("id")),
            "margins": _numeric_criteria(r),
        })
    return states
