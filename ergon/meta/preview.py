"""
Quick preview: generate N random 2D landscapes, compute descriptors, plot a
4x3 grid of contours with basin endpoints overlaid.

Purpose: verify the generator produces visually distinct landscape types
(basin-dominated, ridge-dominated, plateau, deceptive) BEFORE wiring optimizers
and evolutionary machinery.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ergon.meta.landscape import random_landscape
from ergon.meta.descriptors import compute_descriptors


def main(n_samples: int = 12, seed: int = 7, out_path: str = None):
    rng = np.random.default_rng(seed)
    landscapes = [random_landscape(d=2, n_ridges=1, n_gmm=4, rng=rng) for _ in range(n_samples)]
    descs = [compute_descriptors(L, n_starts=40, rng=rng) for L in landscapes]

    # Grid
    box = 4.0
    grid = np.linspace(-box, box, 120)
    X, Y = np.meshgrid(grid, grid)
    pts = np.stack([X.ravel(), Y.ravel()], axis=1)

    ncols = 4
    nrows = (n_samples + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows), squeeze=False)

    for i, (L, d) in enumerate(zip(landscapes, descs)):
        r, c = i // ncols, i % ncols
        ax = axes[r][c]
        Z = L.evaluate(pts).reshape(X.shape)
        lev = 20
        cs = ax.contourf(X, Y, Z, levels=lev, cmap='viridis', alpha=0.8)
        ax.contour(X, Y, Z, levels=lev, colors='k', alpha=0.2, linewidths=0.5)

        # Endpoints of multi-start LBFGS, colored by basin label
        ep = d.endpoints
        ax.scatter(ep[:, 0], ep[:, 1], c=d.labels, cmap='tab10', s=30,
                   edgecolor='w', linewidth=0.6)

        # Annotate found minima
        for (x_mean, v_mean) in d.minima:
            ax.plot(x_mean[0], x_mean[1], 'r*', markersize=12, markeredgecolor='k')

        title = (f"#min={d.n_minima}  curv={d.mean_curvature:+.2f}\n"
                 f"logκ={d.log_conditioning:+.2f}  H={d.basin_entropy:.2f}")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(-box, box); ax.set_ylim(-box, box)
        ax.set_xticks([]); ax.set_yticks([])

    # Blank out unused cells
    for i in range(n_samples, nrows * ncols):
        r, c = i // ncols, i % ncols
        axes[r][c].axis('off')

    plt.tight_layout()
    if out_path is None:
        out_path = Path(__file__).resolve().parent / "figs" / f"preview_{seed}.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=110, bbox_inches='tight')
    print(f"Saved {out_path}")

    # Summary table (using depth_range as 4th axis; cell_key needs edges but for
    # preview we just show descriptors without binning)
    print(f"\n{'#':>3} {'n_min':>5} {'curv':>7} {'log_k':>7} {'dRng':>7}")
    for i, d in enumerate(descs):
        print(f"{i:>3} {d.n_minima:>5} {d.mean_curvature:>+7.3f} "
              f"{d.log_conditioning:>+7.3f} {d.depth_range:>+7.3f}")


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    main(n_samples=n, seed=seed)
