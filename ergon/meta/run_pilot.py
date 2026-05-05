"""
Phase 2a pilot: run MAP-Elites on 2D landscapes with 4-optimizer panel.

Default configuration: SMALL first (5 gen x 10 children = 50 + 40 pilot = 90
evaluations) for debugging. Scale up once pipeline is verified.

Outputs:
  - archive entries saved as pickle
  - summary printed: coverage, best fitness per cell, disagreement histogram
  - figure: archive mosaic (5x5 sample of elites with optimizer trajectories)
"""
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ergon.meta.evolve import run_evolution, MAPEliteArchive


def summarize(archive: MAPEliteArchive, total_cells: int):
    entries = list(archive.entries.values())
    if not entries:
        print("EMPTY ARCHIVE"); return
    fits = np.array([e.fitness for e in entries])
    print(f"\n=== PILOT SUMMARY ===")
    print(f"  cells filled: {len(entries)}/{total_cells} ({100*len(entries)/total_cells:.1f}%)")
    print(f"  fitness range: {fits.min():.3f} -- {fits.max():.3f}  (median {np.median(fits):.3f})")
    print(f"  history total: {len(archive.history)} landscapes evaluated")

    # Disagreement component breakdown on top 10
    top = sorted(entries, key=lambda e: -e.fitness)[:10]
    print(f"\nTOP 10 ELITES by fitness:")
    print(f"  {'cell':>20} {'mode':>10} {'fitness':>9} "
          f"{'val_std':>8} {'dtw':>7} {'bH':>6} {'spdV':>8} {'ranking':>30}")
    for e in top:
        dc = e.disagreement
        rank = "/".join(dc.ranking[:3])
        print(f"  {str(e.cell):>20} {e.landscape.mode:>10} {e.fitness:>9.3f} "
              f"{dc.value_stdev:>8.3f} {dc.traj_divergence:>7.3f} "
              f"{dc.basin_entropy:>6.3f} {dc.speed_variance:>8.2f} {rank:>30}")


def plot_mosaic(archive: MAPEliteArchive, out_path: Path, n_show: int = 12):
    """Plot top-disagreement elites with their optimizer trajectories overlaid."""
    entries = sorted(archive.entries.values(), key=lambda e: -e.fitness)[:n_show]
    if not entries: return

    ncols = 4
    nrows = (len(entries) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows), squeeze=False)

    box = 4.0
    grid = np.linspace(-box, box, 100)
    X, Y = np.meshgrid(grid, grid)
    pts = np.stack([X.ravel(), Y.ravel()], axis=1)

    opt_colors = {'lbfgsb': 'red', 'nelder_mead': 'orange',
                  'cmaes': 'blue', 'cmaes_fallback': 'blue',
                  'random_restart': 'magenta'}

    for i, e in enumerate(entries):
        r, c = i // ncols, i % ncols
        ax = axes[r][c]
        L = e.landscape
        Z = L.evaluate(pts).reshape(X.shape)
        ax.contourf(X, Y, Z, levels=18, cmap='viridis', alpha=0.7)
        ax.contour(X, Y, Z, levels=18, colors='k', alpha=0.12, linewidths=0.4)

        # Plot each trajectory
        for traj in e.trajs:
            col = opt_colors.get(traj.optimizer, 'white')
            if len(traj.positions) >= 2:
                ax.plot(traj.positions[:, 0], traj.positions[:, 1],
                        '-', color=col, alpha=0.7, linewidth=1.2, label=traj.optimizer)
                ax.plot(traj.positions[-1, 0], traj.positions[-1, 1],
                        marker='o', color=col, markersize=6,
                        markeredgecolor='k', markeredgewidth=0.8)

        for (xm, _) in e.descriptor.minima:
            ax.plot(xm[0], xm[1], 'y*', markersize=11, markeredgecolor='k')

        dc = e.disagreement
        ax.set_title(f"{L.mode} fit={e.fitness:.2f}\n"
                     f"val_std={dc.value_stdev:.2f} dtw={dc.traj_divergence:.2f}\n"
                     f"bH={dc.basin_entropy:.2f} cell={e.cell}",
                     fontsize=7)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(-box, box); ax.set_ylim(-box, box)

    # Blank unused
    for i in range(len(entries), nrows * ncols):
        r, c = i // ncols, i % ncols
        axes[r][c].axis('off')

    # Single legend at figure level
    handles = [plt.Line2D([0], [0], color=c, label=n, linewidth=2)
               for n, c in opt_colors.items() if n in {'lbfgsb', 'nelder_mead', 'cmaes', 'random_restart'}]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(out_path, dpi=110, bbox_inches='tight')
    print(f"Saved mosaic to {out_path}")


def main(n_gen: int = 5, children: int = 10, seed: int = 42,
         pilot: int = 40, budget: int = 300, save_archive: bool = True):
    t0 = time.time()
    archive = run_evolution(
        n_generations=n_gen,
        children_per_gen=children,
        seed=seed,
        pilot_sample_size=pilot,
        d=2,
        budget=budget,
    )
    dt = time.time() - t0
    print(f"\n[pilot] wall-clock: {dt:.1f}s")

    total_cells = 3 ** 5
    summarize(archive, total_cells)

    out_dir = Path(__file__).resolve().parent / "figs"
    out_dir.mkdir(exist_ok=True, parents=True)
    plot_mosaic(archive, out_dir / f"pilot_mosaic_s{seed}_g{n_gen}.png")

    if save_archive:
        pkl_path = out_dir.parent / f"pilot_archive_s{seed}_g{n_gen}.pkl"
        with open(pkl_path, 'wb') as f:
            pickle.dump({
                'entries': archive.entries,
                'edges': archive.edges,
                'history': archive.history,
            }, f)
        print(f"Saved archive to {pkl_path}")


if __name__ == "__main__":
    n_gen = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    children = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
    main(n_gen=n_gen, children=children, seed=seed)
