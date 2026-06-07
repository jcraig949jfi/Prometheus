"""Adapted null battery for the relational flow (Stage 0b v0.3, §5).

The operator-vs-state distinction becomes falsifier-vs-state. Nulls:
  - falsifier_column_shuffle : permute each falsifier's margins across states (the
    operator-label-shuffle analog) -- destroys cross-falsifier coupling (genuine
    non-transitivity) while preserving each falsifier's value distribution AND the
    sign-saturation baseline. The decisive null.
  - sign_permutation         : random-flip edge-flow signs.
  - degree_preserving_rewire : rewire the comparison graph (reuse stage0), reassign
    the flow multiset.
  - falsifier_family_holdout : leave-one-falsifier(-family)-out non_gradient_mass.

A relational H-R1 PASS = observed non_gradient_mass beats ALL sampling nulls (never
'> 0' -- the saturation baseline is carried by the nulls).
"""
from __future__ import annotations

import numpy as np

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0.nulls import (
    null_pvalue, NullResult, degree_preserving_rewire,
)
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow

__all__ = [
    "vectors_from_records", "non_gradient_mass_of", "falsifier_column_shuffle",
    "sign_permutation", "falsifier_family_holdout", "run_relational_null",
    "run_relational_family_holdout",
]


def vectors_from_records(records) -> list:
    return [dict(r["margins"]) for r in records]


def non_gradient_mass_of(vectors) -> float:
    G, flow = relational_flow(vectors)
    return hodge_decompose(G, flow).non_gradient_mass


def falsifier_column_shuffle(vectors, seed) -> list:
    rng = np.random.default_rng(seed)
    names = set().union(*[set(v) for v in vectors]) if vectors else set()
    new = [dict() for _ in vectors]
    for k in names:
        idxs = [i for i, v in enumerate(vectors) if k in v]
        vals = [vectors[i][k] for i in idxs]
        perm = list(vals)
        rng.shuffle(perm)
        for pos, i in enumerate(idxs):
            new[i][k] = perm[pos]
    return new


def sign_permutation(flow, seed) -> dict:
    rng = np.random.default_rng(seed)
    return {e: (val if rng.random() < 0.5 else -val) for e, val in flow.items()}


def falsifier_family_holdout(vectors, family) -> list:
    def keep(k):
        return not (k == family or k.startswith(family))
    return [{k: v for k, v in vec.items() if keep(k)} for vec in vectors]


def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def run_relational_null(records, kind: str, n_samples: int, seed: int) -> NullResult:
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")
    vectors = vectors_from_records(records)
    observed = non_gradient_mass_of(vectors)
    rng = np.random.default_rng(seed)
    masses = []
    for _ in range(n_samples):
        ss = int(rng.integers(0, 2**31 - 1))
        if kind == "falsifier_column_shuffle":
            masses.append(non_gradient_mass_of(falsifier_column_shuffle(vectors, ss)))
        elif kind == "sign_permutation":
            G, flow = relational_flow(vectors)
            masses.append(hodge_decompose(G, sign_permutation(flow, ss)).non_gradient_mass)
        elif kind == "degree_preserving_rewire":
            G, flow = relational_flow(vectors)
            H = degree_preserving_rewire(G, seed=ss)
            vals = list(flow.values())
            r2 = np.random.default_rng(ss)
            r2.shuffle(vals)
            edges = sorted(_canon(u, v) for u, v in H.edges())
            f = {e: vals[i] for i, e in enumerate(edges)}
            masses.append(hodge_decompose(H, f).non_gradient_mass)
        else:
            raise ValueError(f"unknown relational null kind {kind!r}")
    return NullResult(
        observed=observed, null_masses=masses, pvalue=null_pvalue(observed, masses),
        null_mean=float(np.mean(masses)), null_std=float(np.std(masses)), kind=kind,
    )


def run_relational_family_holdout(records) -> dict:
    """Leave-one-falsifier(-family)-out non_gradient_mass. Families: exact falsifier
    names plus catalog:* as one family. {'_full': mass, family: mass_without}."""
    vectors = vectors_from_records(records)
    result = {"_full": non_gradient_mass_of(vectors)}
    names = set().union(*[set(v) for v in vectors]) if vectors else set()
    families = sorted({("catalog:" if n.startswith("catalog:") else n) for n in names})
    for fam in families:
        held = falsifier_family_holdout(vectors, fam)
        try:
            result[fam] = non_gradient_mass_of(held)
        except Exception:
            result[fam] = None
    return result
