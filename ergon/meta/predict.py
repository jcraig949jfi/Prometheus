"""
Predictive model layer (§9 of WHITEPAPER_v2).

Question: can we predict WHICH optimizer wins on a landscape, given only the
5 structural descriptors + mode?

Interpretation:
  accuracy > 80%   -> descriptors are SUFFICIENT; project is actionable
                      (a practitioner could compute descriptors and get an
                       optimizer recommendation)
  accuracy 60-80%  -> descriptors explain most variance; residual localizes
                      MISSING AXES. Feature importance points at what helps.
  accuracy < 60%   -> either landscape parameterization is too random
                      (intra-cell heterogeneity) OR descriptors miss a
                      fundamental axis. The intra-cell variance check
                      disambiguates.

The v2a intra-cell-ranking-variance metric distinguishes these:
  - high OOB uncertainty + high intra-cell variance -> NOISE, not missing axis
  - high OOB uncertainty + low  intra-cell variance -> MISSING DESCRIPTOR

Usage:
  python predict.py <archive.pkl>
"""
import pickle
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, confusion_matrix
    from sklearn.model_selection import StratifiedKFold
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

from ergon.meta.fitness import intra_cell_ranking_variance


# ---------- feature extraction ----------------------------------------------

MODES = ["basin", "ridge", "plateau", "deceptive"]
# Optimizer indices (keep order stable)
OPTIMIZERS = ["lbfgsb", "nelder_mead", "cmaes", "random_restart"]
# cmaes_fallback treated as cmaes for classification purposes
OPT_ALIASES = {"cmaes_fallback": "cmaes"}


def feature_vector(entry) -> np.ndarray:
    d = entry.descriptor
    mode_onehot = [1 if entry.landscape.mode == m else 0 for m in MODES]
    return np.array([
        d.n_minima,
        d.minima_avg_curvature,
        d.minima_worst_conditioning,
        d.depth_range,
        d.ruggedness,
    ] + mode_onehot, dtype=float)


FEATURE_NAMES = [
    "n_minima", "minima_avg_curvature", "minima_worst_conditioning",
    "depth_range", "ruggedness",
    "mode_basin", "mode_ridge", "mode_plateau", "mode_deceptive",
]


def winning_optimizer(entry) -> str:
    """Optimizer with lowest final_value (most argmin-wise)."""
    best = min(entry.trajs, key=lambda t: t.final_value)
    name = best.optimizer
    return OPT_ALIASES.get(name, name)


# ---------- main pipeline ---------------------------------------------------

def main(archive_path: str, n_folds: int = 5, n_estimators: int = 200):
    if not SKLEARN_OK:
        print("ERROR: sklearn not available. Install scikit-learn.")
        return

    with open(archive_path, 'rb') as f:
        data = pickle.load(f)

    # Use full history, not just elites (larger training set, more diverse)
    history = data.get('history', [])
    entries = [e for e in history if len(e.trajs) >= 2]
    print(f"Loaded {len(entries)} history entries")

    X = np.array([feature_vector(e) for e in entries])
    y = np.array([winning_optimizer(e) for e in entries])
    winners, counts = np.unique(y, return_counts=True)
    print(f"Class distribution (winner-optimizer):")
    for w, c in zip(winners, counts):
        print(f"  {w:<20} {c}  ({100*c/len(y):.1f}%)")
    baseline = counts.max() / len(y)
    print(f"Baseline accuracy (predict majority): {baseline:.3f}")

    # --- Stratified k-fold CV ---
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_accs = []
    importances = []
    confmats = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=None,
            random_state=42 + fold,
            oob_score=True,
            n_jobs=-1,
        )
        model.fit(X[train_idx], y[train_idx])
        y_pred = model.predict(X[test_idx])
        acc = accuracy_score(y[test_idx], y_pred)
        fold_accs.append(acc)
        importances.append(model.feature_importances_)
        confmats.append(confusion_matrix(y[test_idx], y_pred, labels=winners))
        print(f"  Fold {fold+1}: accuracy = {acc:.3f} (OOB = {model.oob_score_:.3f})")

    mean_acc = np.mean(fold_accs); std_acc = np.std(fold_accs)
    print(f"\n5-fold CV accuracy: {mean_acc:.3f} ± {std_acc:.3f}  (baseline {baseline:.3f})")
    gap = mean_acc - baseline
    if mean_acc > 0.80:
        verdict = "SUFFICIENT: descriptors predict optimizer winner > 80% — actionable."
    elif mean_acc > 0.60:
        verdict = "PARTIAL: descriptors explain most variance; feature importance points at residuals."
    elif gap > 0.05:
        verdict = "WEAK: above baseline but descriptors miss fundamental axes."
    else:
        verdict = "INSUFFICIENT: no better than majority vote."
    print(f"Verdict: {verdict}")

    # --- Feature importance (averaged across folds) ---
    mean_imp = np.mean(importances, axis=0)
    order = np.argsort(-mean_imp)
    print(f"\nFeature importance (averaged, sorted):")
    for i in order:
        print(f"  {FEATURE_NAMES[i]:<28} {mean_imp[i]:.3f}")

    # --- Confusion matrix (summed across folds) ---
    total_cm = np.sum(confmats, axis=0)
    print(f"\nConfusion matrix (rows=true, cols=pred):")
    print(f"  {'':<20}" + "".join(f"{w:>16}" for w in winners))
    for i, w in enumerate(winners):
        row = f"  {w:<20}"
        for j in range(len(winners)):
            row += f"{total_cm[i,j]:>16}"
        print(row)

    # --- OOB uncertainty vs intra-cell ranking variance ---
    # Train one full model on all data for OOB scoring per entry
    full_model = RandomForestClassifier(
        n_estimators=n_estimators, random_state=0, oob_score=True, n_jobs=-1,
    )
    full_model.fit(X, y)
    oob_proba = full_model.oob_decision_function_
    # Uncertainty = entropy of OOB class distribution (higher = less confident)
    eps = 1e-12
    oob_entropy = -np.sum(oob_proba * np.log(oob_proba + eps), axis=1)

    # Intra-cell ranking variance per cell
    by_cell = defaultdict(list)
    for e in entries:
        by_cell[e.cell].append(e.disagreement.ranking)
    cell_to_icv = {cell: intra_cell_ranking_variance(rks)
                   for cell, rks in by_cell.items() if len(rks) >= 2}
    print(f"\nIntra-cell ranking variance across {len(cell_to_icv)} cells "
          f"with >=2 entries:")
    icvs = list(cell_to_icv.values())
    print(f"  median intra-cell variance = {np.median(icvs):.3f}")
    print(f"  max    intra-cell variance = {max(icvs):.3f}")

    # Plot: OOB entropy vs intra-cell variance scatter
    out_dir = Path(archive_path).parent / "figs"
    out_dir.mkdir(exist_ok=True, parents=True)
    out_path = out_dir / f"predictive_{Path(archive_path).stem}.png"

    # Per-cell median OOB entropy
    cell_oob = defaultdict(list)
    for i, e in enumerate(entries):
        cell_oob[e.cell].append(float(oob_entropy[i]))
    cells_common = [c for c in cell_to_icv if c in cell_oob]
    xs = [cell_to_icv[c] for c in cells_common]
    ys = [np.median(cell_oob[c]) for c in cells_common]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # (a) feature importance
    ax = axes[0]
    ax.barh(range(len(order)), mean_imp[order][::-1])
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([FEATURE_NAMES[i] for i in order[::-1]], fontsize=8)
    ax.set_xlabel("Mean RF feature importance")
    ax.set_title(f"CV accuracy = {mean_acc:.3f} ± {std_acc:.3f}\n(baseline {baseline:.3f})")

    # (b) confusion matrix heatmap
    ax = axes[1]
    ax.imshow(total_cm, cmap='Blues')
    ax.set_xticks(range(len(winners))); ax.set_xticklabels(winners, rotation=30, ha='right', fontsize=8)
    ax.set_yticks(range(len(winners))); ax.set_yticklabels(winners, fontsize=8)
    ax.set_xlabel("predicted"); ax.set_ylabel("true")
    for i in range(len(winners)):
        for j in range(len(winners)):
            ax.text(j, i, total_cm[i,j], ha='center', va='center',
                    color='white' if total_cm[i,j] > total_cm.max()/2 else 'black', fontsize=8)
    ax.set_title("Confusion (summed 5-fold)")

    # (c) OOB entropy vs intra-cell variance
    ax = axes[2]
    ax.scatter(xs, ys, alpha=0.7, s=30)
    ax.set_xlabel("Intra-cell ranking variance")
    ax.set_ylabel("Per-cell median OOB entropy")
    ax.set_title("Uncertainty source diagnosis\n(high entropy + low var = missing axis)")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches='tight')
    print(f"\nSaved predictive figure to {out_path}")

    # --- Summary for v2 paper ---
    print(f"\n=== SUMMARY ===")
    print(f"  Mean CV accuracy       : {mean_acc:.3f} ± {std_acc:.3f}")
    print(f"  Baseline (majority)    : {baseline:.3f}")
    print(f"  Top-2 features         : {FEATURE_NAMES[order[0]]}, {FEATURE_NAMES[order[1]]}")
    print(f"  Cells with intra-var>0 : {sum(1 for v in icvs if v > 0.05)}/{len(icvs)}")
    print(f"  Verdict                : {verdict}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ergon/meta/pilot_archive_s42_g50.pkl"
    main(path)
