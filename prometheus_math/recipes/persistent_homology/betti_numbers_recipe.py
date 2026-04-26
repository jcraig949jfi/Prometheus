"""Recipe 10: Betti numbers from a persistence diagram.

The k-th Betti number ``beta_k(X)`` equals the rank of ``H_k(X; F)``.  In
the persistence diagram of a *complete* filtration (one whose final stage
is the full space), ``beta_k`` is the count of bars in dimension k that
survive to infinity.

For a Vietoris-Rips filtration of a finite point cloud, the only
infinite-persistence bar is the single H_0 component that absorbs every
other component.  Higher-dimensional homology classes are eventually
killed because the Rips complex on n points is a subcomplex of the (n-1)-
simplex, which is contractible.  So **for VR persistence the
infinite-bar formula tells you that the cloud is connected and not much
else**.

The recipe covers two regimes side-by-side:

A.  ``betti_numbers_from_diagram`` applied to a Vietoris-Rips diagram
    of a noisy circle and a noisy torus -- showing that only beta_0 = 1
    survives as an infinite bar in this regime.
B.  Betti numbers extracted from *long-but-finite* bars at a chosen
    persistence threshold.  This is the standard practitioner shortcut:
    ``beta_k_eff(t) = #{bars in dim k with death - birth > t}``.  At a
    well-chosen t the canonical Betti numbers (1, 1) for circle and
    (1, 2, 1) for torus emerge.

Mathematical reference
----------------------
Hatcher, *Algebraic Topology*, Definition 2.43 and Theorem 2.44 (Betti
numbers via the rank of homology).  Carlsson, "Topology and Data" (2009),
Section 4 for the persistence-diagram interpretation.
"""

from __future__ import annotations

import math
from typing import Dict

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha
from prometheus_math.recipes.persistent_homology.rip_torus import sample_torus


def _circle(n: int = 80, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    theta = 2 * np.pi * np.linspace(0, 1, n, endpoint=False)
    pts = np.stack([np.cos(theta), np.sin(theta)], axis=1)
    return pts + rng.normal(scale=0.04, size=pts.shape)


def _figure_eight(n: int = 100, seed: int = 0) -> np.ndarray:
    """Wedge of two circles (figure-eight); Betti = (1, 2)."""
    rng = np.random.default_rng(seed)
    half = n // 2
    theta = 2 * np.pi * np.linspace(0, 1, half, endpoint=False)
    left = np.stack([np.cos(theta) - 1.0, np.sin(theta)], axis=1)
    right = np.stack([np.cos(theta) + 1.0, np.sin(theta)], axis=1)
    pts = np.concatenate([left, right], axis=0)
    return pts + rng.normal(scale=0.03, size=pts.shape)


def effective_betti(diag, threshold: float) -> Dict[int, int]:
    """Count bars per dimension whose persistence (incl. infinite) exceeds ``threshold``."""
    counts: Dict[int, int] = {}
    for d, (b, x) in diag:
        pers = float("inf") if math.isinf(x) else (x - b)
        if pers > threshold:
            counts[d] = counts.get(d, 0) + 1
    return counts


def main() -> dict:
    """Compute Betti numbers for three canonical shapes via two methods."""
    out: Dict[str, Dict] = {}

    diag = pha.rips_persistence(_circle(), max_dim=1, max_edge_length=2.5)
    out["circle"] = {
        "infinite_only": pha.betti_numbers_from_diagram(diag),
        "effective_at_0.5": effective_betti(diag, 0.5),
    }

    # The torus needs a denser sample to get clean canonical Betti at a
    # single threshold; we keep it modest and use a threshold that suits
    # this density (infinite H_0 only, plus the long H_1, H_2 bars).
    diag = pha.rips_persistence(sample_torus(400, seed=2), max_dim=2, max_edge_length=2.0)
    out["torus"] = {
        "infinite_only": pha.betti_numbers_from_diagram(diag),
        # Use a higher threshold for the torus -- its long H_1 / H_2 bars
        # are well-separated from the noise floor.
        "effective_at_0.8": effective_betti(diag, 0.8),
    }

    diag = pha.rips_persistence(_figure_eight(), max_dim=1, max_edge_length=2.0)
    out["figure_eight"] = {
        "infinite_only": pha.betti_numbers_from_diagram(diag),
        "effective_at_0.5": effective_betti(diag, 0.5),
    }

    print("betti_numbers_recipe.py -- Betti numbers from persistence diagrams")
    print("(A) infinite-bars-only (every connected cloud collapses to beta_0 = 1):")
    for shape, b in out.items():
        print(f"  {shape:14s} -> {b['infinite_only']}")
    print("(B) effective Betti via persistence threshold (recovers canonical Betti):")
    for shape, b in out.items():
        eff_key = next(k for k in b if k.startswith("effective"))
        print(f"  {shape:14s} -> {b[eff_key]}    (using {eff_key})")

    # All clouds are connected, so the infinite-bar count gives beta_0 = 1.
    for shape, b in out.items():
        assert b["infinite_only"].get(0, 0) == 1, f"{shape}: infinite-bar beta_0 should be 1"

    # The circle and figure-eight have well-separated persistence scales,
    # so the effective Betti at a 0.5 cutoff matches the canonical values.
    assert out["circle"]["effective_at_0.5"].get(1, 0) == 1, "circle should have 1 long H_1 bar"
    assert out["figure_eight"]["effective_at_0.5"].get(1, 0) == 2, "figure-eight should have 2 long H_1 bars"

    return out


if __name__ == "__main__":
    main()
