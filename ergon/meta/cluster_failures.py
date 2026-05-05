"""
Phase 2a failure-mode clustering — DTW on gradient-norm sequences across all
optimizer × landscape trajectories in a saved archive.

Input: a pickled archive from run_pilot.py.
Output:
  - cluster labels per (landscape_cell, optimizer) pair
  - scalar-feature summary table per cluster
  - dendrogram figure
  - example-trajectory grid per cluster (2-3 per)
"""
import pickle
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ergon.meta.trajectory import (
    cluster_trajectories, dtw_pairwise_matrix, featurize,
)


def main(archive_path: str, n_clusters: int = 4):
    with open(archive_path, 'rb') as f:
        data = pickle.load(f)
    entries = data['entries']
    print(f"Loaded archive: {len(entries)} cells")

    # Pool all trajectories (one list)
    all_trajs = []
    meta = []   # (cell, optimizer)
    for cell, e in entries.items():
        for t in e.trajs:
            if len(t.grad_norms) >= 5:
                all_trajs.append(t)
                meta.append((cell, t.optimizer, e.landscape.mode))
    print(f"Pooled {len(all_trajs)} trajectories for DTW clustering")

    # Subsample: DTW is O(n^2) on all pairs; cap at N=200 for speed
    MAX = 200
    if len(all_trajs) > MAX:
        rng = np.random.default_rng(0)
        idx = rng.choice(len(all_trajs), size=MAX, replace=False)
        all_trajs = [all_trajs[i] for i in idx]
        meta = [meta[i] for i in idx]
        print(f"Subsampled to {len(all_trajs)} for clustering")

    # DTW matrix + clustering
    print(f"Computing {len(all_trajs)}x{len(all_trajs)} DTW matrix...")
    labels = cluster_trajectories(all_trajs, n_clusters=n_clusters)

    # Per-cluster summary
    features_all = [featurize(t) for t in all_trajs]

    print(f"\n=== Clusters (n_clusters={n_clusters}) ===")
    print(f"{'cluster':>7} {'n':>5}  {'path_len':>10} {'path_curv':>10} "
          f"{'grad_dec':>10} {'stall_f':>8}  {'opt-mix':<30}  {'mode-mix':<30}")
    cluster_info = {}
    for cl in range(n_clusters):
        idx = np.where(labels == cl)[0]
        if len(idx) == 0: continue
        pl = np.array([features_all[i]['path_length']    for i in idx])
        pc = np.array([features_all[i]['path_curvature'] for i in idx])
        gd = np.array([features_all[i]['grad_norm_decay'] for i in idx])
        sf = np.array([features_all[i]['stall_fraction']  for i in idx])
        opts = [meta[i][1] for i in idx]
        modes = [meta[i][2] for i in idx]
        # counts
        from collections import Counter
        oc = Counter(opts); mc = Counter(modes)
        opt_mix = ",".join(f"{k}:{v}" for k, v in oc.most_common(3))
        mode_mix = ",".join(f"{k}:{v}" for k, v in mc.most_common(3))
        print(f"{cl:>7} {len(idx):>5}  {np.median(pl):>10.2f} {np.median(pc):>10.3f} "
              f"{np.median(gd):>+10.3f} {np.median(sf):>8.3f}  "
              f"{opt_mix:<30}  {mode_mix:<30}")
        cluster_info[cl] = {
            'n': len(idx),
            'path_length_median': float(np.median(pl)),
            'path_curvature_median': float(np.median(pc)),
            'grad_decay_median': float(np.median(gd)),
            'stall_median': float(np.median(sf)),
            'optimizers': dict(oc),
            'modes': dict(mc),
        }

    # Plot grad-norm curves per cluster (median + spread)
    out_dir = Path(archive_path).parent / "figs"
    out_dir.mkdir(exist_ok=True, parents=True)
    out_path = out_dir / f"failure_clusters_{Path(archive_path).stem}.png"

    fig, axes = plt.subplots(1, n_clusters, figsize=(4 * n_clusters, 4), squeeze=False)
    for cl in range(n_clusters):
        ax = axes[0][cl]
        idx = np.where(labels == cl)[0]
        if len(idx) == 0:
            ax.axis('off'); continue
        # Pad/trim to common length L = median
        max_len = max(len(all_trajs[i].grad_norms) for i in idx)
        L = int(np.median([len(all_trajs[i].grad_norms) for i in idx]))
        mat = np.full((len(idx), L), np.nan)
        for r, i in enumerate(idx):
            g = all_trajs[i].grad_norms
            n = min(len(g), L)
            mat[r, :n] = g[:n]
        # Plot each as faint grey, median as black
        for r in range(mat.shape[0]):
            ax.plot(mat[r], '-', color='gray', alpha=0.15, linewidth=0.5)
        med = np.nanmedian(mat, axis=0)
        ax.plot(med, 'k-', linewidth=2, label='median')
        ax.set_yscale('log')
        ax.set_title(f"cluster {cl} (n={len(idx)})\n"
                     f"{cluster_info[cl]['optimizers']}", fontsize=8)
        ax.set_xlabel("step"); ax.set_ylabel("||grad||")
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches='tight')
    print(f"\nSaved failure-mode figure to {out_path}")

    return cluster_info


if __name__ == "__main__":
    archive = sys.argv[1] if len(sys.argv) > 1 else "ergon/meta/pilot_archive_s42_g50.pkl"
    n_cl = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    main(archive, n_clusters=n_cl)
