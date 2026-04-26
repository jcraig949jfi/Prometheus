"""Recipe 1: Vietoris-Rips persistence on a 2D random point cloud.

Computes the persistence diagram of a random 200-point planar cloud, prints
the longest H_0 and H_1 bars, and (if matplotlib is available) saves a
persistence diagram plot to ``outputs/rip_basic_diagram.png``.

Mathematical reference
----------------------
Vietoris-Rips filtration, see Edelsbrunner & Harer,
*Computational Topology: An Introduction* (AMS 2010), Chapter VII.

Usage
-----
    python rip_basic.py
"""

from __future__ import annotations

import os
import math

import numpy as np

from prometheus_math.recipes.persistent_homology import api as pha


def _outputs_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "outputs")
    os.makedirs(out, exist_ok=True)
    return out


def main(seed: int = 7, n: int = 200, save_plot: bool = False) -> dict:
    """Run the basic Vietoris-Rips recipe.

    Parameters
    ----------
    seed : int
        Random seed for reproducibility.
    n : int
        Number of points in the planar cloud.
    save_plot : bool
        If True, attempts to render and save the persistence diagram via
        matplotlib.  Optional dependency, never required for the recipe to
        return a result.
    """
    rng = np.random.default_rng(seed)
    # Uniform sample in the unit square -- generic 2D cloud.
    pts = rng.uniform(low=-1.0, high=1.0, size=(n, 2))

    # Vietoris-Rips up to H_1 (loops). max_edge_length defaults to 2 * diameter,
    # which is enough to merge every connected component.
    diag = pha.rips_persistence(pts, max_dim=1)

    # Separate finite H_0 and H_1 bars by persistence (death - birth).
    h0 = [(b, x) for d, (b, x) in diag if d == 0 and not math.isinf(x)]
    h1 = [(b, x) for d, (b, x) in diag if d == 1 and not math.isinf(x)]
    h0.sort(key=lambda bx: -(bx[1] - bx[0]))
    h1.sort(key=lambda bx: -(bx[1] - bx[0]))

    betti = pha.betti_numbers_from_diagram(diag)

    print("rip_basic.py -- Vietoris-Rips on a random 2D cloud")
    print(f"  n_points        = {n}")
    print(f"  total bars      = {len(diag)}")
    print(f"  betti numbers   = {betti}")
    print(f"  longest H0 bar  = {h0[0] if h0 else None}")
    print(f"  longest H1 bar  = {h1[0] if h1 else 'none'}")

    artifact = None
    if save_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(5, 5))
            for d, (b, x) in diag:
                if math.isinf(x):
                    continue
                ax.scatter(b, x, c="C0" if d == 0 else "C1", s=10)
            lim = max((x for _, (_, x) in diag if not math.isinf(x)), default=1.0)
            ax.plot([0, lim], [0, lim], "k--", linewidth=0.5)
            ax.set_xlabel("birth")
            ax.set_ylabel("death")
            ax.set_title("rip_basic: random 2D cloud (n=200)")
            fig.tight_layout()
            artifact = os.path.join(_outputs_dir(), "rip_basic_diagram.png")
            fig.savefig(artifact, dpi=120)
            plt.close(fig)
        except Exception as e:  # pragma: no cover
            print(f"  (matplotlib plot skipped: {e})")
            artifact = None

    return {
        "diagram": diag,
        "betti": betti,
        "longest_H0": h0[0] if h0 else None,
        "longest_H1": h1[0] if h1 else None,
        "artifact": artifact,
    }


if __name__ == "__main__":
    main(save_plot=True)
