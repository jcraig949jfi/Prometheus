"""Cross-target transfer: freeze top-10 elites from phase 3B (archive_v5.json)
and re-evaluate them on a DIFFERENT target tensor. Distinguishes generalizable
skeletons from target-specific overfits.

Target A (source):
  f(x_1,...,x_6) = sin^{\otimes 6}(2*pi*x/N) + cos^{\otimes 6}(2*pi*x/N)
                   + (x/(N-1))^{2,\otimes 6}
  True TT rank = 3. Sinusoidal + polynomial basis.

Target B (transfer):
  f(x_1,...,x_6) = sum of 4 Legendre-like polynomials, outer product each.
  True TT rank = 4. Orthogonal-polynomial basis on [-1, 1].

Different basis, different true rank, same D=6, N=8 grid. Same sample
indices X_TRAIN, X_VAL used for both (only the F values differ).
"""

import json
from pathlib import Path

import numpy as np

import evolve_tt_v4 as v4

HERE = Path(__file__).parent


def build_target_B():
    ks = np.arange(v4.N, dtype=float)
    x = 2 * ks / (v4.N - 1) - 1
    g1 = x
    g2 = 0.5 * (3 * x ** 2 - 1)
    g3 = 0.5 * (5 * x ** 3 - 3 * x)
    g4 = 0.125 * (35 * x ** 4 - 30 * x ** 2 + 3)
    T = np.zeros((v4.N,) * v4.D)
    for g in (g1, g2, g3, g4):
        outer = g
        for _ in range(v4.D - 1):
            outer = np.multiply.outer(outer, g)
        T = T + outer
    return T


T_B = build_target_B()
F_TRAIN_B = T_B[v4.X_TRAIN[:, 0], v4.X_TRAIN[:, 1], v4.X_TRAIN[:, 2],
                v4.X_TRAIN[:, 3], v4.X_TRAIN[:, 4], v4.X_TRAIN[:, 5]]
F_VAL_B = T_B[v4.X_VAL[:, 0], v4.X_VAL[:, 1], v4.X_VAL[:, 2],
              v4.X_VAL[:, 3], v4.X_VAL[:, 4], v4.X_VAL[:, 5]]
F_TRAIN_B_NORM = float(np.linalg.norm(F_TRAIN_B))
F_VAL_B_NORM = float(np.linalg.norm(F_VAL_B))

print(f"Target A norm (val): {v4.F_VAL_NORM:.3f}")
print(f"Target B norm (val): {F_VAL_B_NORM:.3f}")


def evaluate_on_B(genome):
    """Re-evaluate a genome against target B by swapping F arrays in v4."""
    saved = (v4.F_TRAIN, v4.F_VAL, v4.F_TRAIN_NORM, v4.F_VAL_NORM)
    v4.F_TRAIN = F_TRAIN_B
    v4.F_VAL = F_VAL_B
    v4.F_TRAIN_NORM = F_TRAIN_B_NORM
    v4.F_VAL_NORM = F_VAL_B_NORM
    try:
        return v4.evaluate(genome)
    finally:
        v4.F_TRAIN, v4.F_VAL, v4.F_TRAIN_NORM, v4.F_VAL_NORM = saved


def reconstitute(raw):
    out = []
    for op in raw:
        name = op[0]
        params = dict(op[1]) if op[1] else {}
        for k, v in list(params.items()):
            if isinstance(v, str):
                try:
                    params[k] = int(v)
                except ValueError:
                    try:
                        params[k] = float(v)
                    except ValueError:
                        pass
        out.append((name, params))
    return out


def main():
    # Load archive_v5 (phase 3B)
    arch_path = HERE / "archive_v5.json"
    print(f"\nLoading {arch_path}")
    with open(arch_path) as f:
        data = json.load(f)
    cells = list(data["cells"].values())
    for c in cells:
        c["genome"] = reconstitute(c["genome"])
    top10 = sorted(cells, key=lambda v: v["val_err"])[:10]

    print(f"\n{'='*70}")
    print("CROSS-TARGET TRANSFER: phase 3B top-10 -> target B")
    print(f"{'='*70}")
    print(f"Source target A: sin/cos/poly, true rank 3")
    print(f"Target B:        Legendre-like, true rank 4")
    print()

    rows = []
    for i, t in enumerate(top10):
        a_redo = v4.evaluate(t["genome"])
        b_eval = evaluate_on_B(t["genome"])
        if a_redo is None or b_eval is None:
            print(f"  #{i+1:<2} FAILED")
            continue
        r_a, tr_a, va_a, _ = a_redo
        r_b, tr_b, va_b, _ = b_eval
        ratio = va_b / max(va_a, 1e-15)
        ops = [op[0] for op in t["genome"]]
        print(f"  #{i+1:<2} rank_A={r_a} len={len(ops):<2}  "
              f"val_A={va_a:.2e}  val_B={va_b:.2e}  B/A={ratio:>6.2f}  "
              f"fgr={t['fit_grad_ratio']:.2f}")
        rows.append({
            "rank_elite": i + 1, "length": len(ops),
            "val_A_archive": t["val_err"], "val_A_redo": va_a,
            "val_B": va_b, "ratio": ratio,
            "rank_tt": r_a, "fit_grad_ratio": t["fit_grad_ratio"],
            "ops": ops,
        })

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    ratios = [r["ratio"] for r in rows if np.isfinite(r["ratio"])]
    if ratios:
        print(f"  B/A ratio stats: median={np.median(ratios):.2f} "
              f"min={min(ratios):.2f}  max={max(ratios):.2f}")
        print(f"  (B/A = 1.0 means perfect transfer; higher = target-specific)")
        # How many elites beat the 'untrained' baseline on B?
        # Untrained baseline: val_B for a random TT is ~1.0
        n_beat_random = sum(1 for r in ratios if r < 50)  # arbitrary threshold
        print(f"  Elites with val_B < 0.5 (meaningful fit on B): "
              f"{sum(1 for r in rows if r['val_B'] < 0.5)}/{len(rows)}")
        print(f"  Elites with val_B < 0.1 (good fit on B): "
              f"{sum(1 for r in rows if r['val_B'] < 0.1)}/{len(rows)}")

    print(f"\n  Most transferable (lowest val_B):")
    for r in sorted(rows, key=lambda x: x["val_B"])[:5]:
        print(f"    #{r['rank_elite']} val_B={r['val_B']:.2e} "
              f"val_A={r['val_A_redo']:.2e} ratio={r['ratio']:.2f} "
              f"fgr={r['fit_grad_ratio']:.2f} ops={r['ops']}")

    print(f"\n  Least transferable (highest val_B):")
    for r in sorted(rows, key=lambda x: -x["val_B"])[:3]:
        print(f"    #{r['rank_elite']} val_B={r['val_B']:.2e} "
              f"val_A={r['val_A_redo']:.2e} ratio={r['ratio']:.2f} "
              f"fgr={r['fit_grad_ratio']:.2f} ops={r['ops']}")

    # Save
    out = {
        "source_archive": "archive_v5.json",
        "target_B_description": "Legendre-like rank-4 on [-1, 1]",
        "target_B_val_norm": F_VAL_B_NORM,
        "rows": rows,
    }
    with open(HERE / "transfer_B.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {HERE / 'transfer_B.json'}")


if __name__ == "__main__":
    main()
