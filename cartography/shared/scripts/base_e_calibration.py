"""
Base-e Recalibration — All phoneme equations in natural logarithm.

Tests whether the phoneme constants become exact known constants
when everything is expressed in base e.
"""
import sys, json, numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from scipy.stats import spearmanr, pearsonr

ROOT = Path(__file__).resolve().parents[3]

def sigmoid(x, a, b):
    return 1 / (1 + np.exp(-(a*x - b)))

def main():
    print("=" * 70)
    print("BASE-e RECALIBRATION")
    print("All phonemes re-encoded in natural logarithm")
    print("=" * 70)

    # Load EC data
    import duckdb
    con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
    ec = con.execute("""
        SELECT conductor, rank, analytic_rank, torsion
        FROM elliptic_curves
        WHERE conductor > 0 AND rank IS NOT NULL AND torsion IS NOT NULL
    """).fetchdf()

    dz = con.execute("""
        SELECT conductor, degree, rank, zeros_vector
        FROM dirichlet_zeros WHERE conductor > 0
    """).fetchdf()
    con.close()

    nf_data = json.loads((ROOT / "cartography/number_fields/data/number_fields.json")
                         .read_text(encoding="utf-8"))
    knot_data = json.loads((ROOT / "cartography/knots/data/knots.json")
                           .read_text(encoding="utf-8"))
    knots = [k for k in knot_data["knots"]
             if k.get("determinant") and k["determinant"] > 0]

    print(f"EC: {len(ec)}, NF: {len(nf_data)}, Knots: {len(knots)}, Lzeros: {len(dz)}")

    # ============================================================
    # MEGETHOS: M(x) = ln N(x)
    # ============================================================
    print(f"\n{'=' * 70}")
    print("MEGETHOS: M(x) = ln N(x)")
    print("=" * 70)

    M_ec = np.log(ec["conductor"].values.astype(float))
    M_nf = np.array([np.log(abs(int(f["disc_abs"])))
                      for f in nf_data if int(f.get("disc_abs", 0)) > 0])
    M_knot = np.array([np.log(k["determinant"]) for k in knots])

    for name, vals in [("EC", M_ec), ("NF", M_nf), ("Knot(det)", M_knot)]:
        print(f"  {name:12s}: n={len(vals):6d}, "
              f"range=[{vals.min():.2f}, {vals.max():.2f}], mean={vals.mean():.4f}")

    # ============================================================
    # BATHOS: Refit sigmoid with high precision
    # ============================================================
    print(f"\n{'=' * 70}")
    print("BATHOS: P(rank >= 1) = sigmoid(a * ln(N) - b)")
    print("=" * 70)

    B_ec = (ec["rank"].values >= 1).astype(float)

    # Fine-grained binning for precision
    n_bins = 100
    M_sorted = np.sort(M_ec)
    edges = np.linspace(M_sorted[50], M_sorted[-50], n_bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    probs = []
    for i in range(n_bins):
        mask = (M_ec >= edges[i]) & (M_ec < edges[i + 1])
        if mask.sum() >= 20:
            probs.append(B_ec[mask].mean())
        else:
            probs.append(np.nan)

    valid = ~np.isnan(probs)
    M_fit = centers[valid]
    P_fit = np.array(probs)[valid]

    popt, pcov = curve_fit(sigmoid, M_fit, P_fit, p0=[0.3, 2.0], maxfev=50000)
    a, b = popt
    perr = np.sqrt(np.diag(pcov))

    P_pred = sigmoid(M_fit, a, b)
    r2 = 1 - np.sum((P_fit - P_pred)**2) / np.sum((P_fit - P_fit.mean())**2)

    print(f"  sigmoid({a:.8f} * M - {b:.8f})")
    print(f"  R^2 = {r2:.8f}")
    print(f"  a = {a:.8f} +/- {perr[0]:.8f}")
    print(f"  b = {b:.8f} +/- {perr[1]:.8f}")
    print(f"  M_50 = b/a = {b/a:.6f}  (conductor at 50% = e^{b/a:.2f} = {np.exp(b/a):.1f})")

    gamma = 0.5772156649015329

    print(f"\n  --- Constant matching (slope a) ---")
    candidates_a = {
        "gamma/2": gamma / 2,
        "ln(4/3)": np.log(4/3),
        "1/(2*ln(2))": 1 / (2 * np.log(2)),
        "1/e": 1 / np.e,
        "gamma * ln(2)": gamma * np.log(2),
        "1/(pi*ln(2))": 1 / (np.pi * np.log(2)),
        "ln(1+gamma)": np.log(1 + gamma),
        "2*gamma - 1": 2*gamma - 1,
        "sqrt(gamma/pi)": np.sqrt(gamma / np.pi),
    }
    for name, val in sorted(candidates_a.items(), key=lambda x: abs(a - x[1])):
        diff_pct = abs(a - val) / a * 100
        match = "***" if diff_pct < 1 else "**" if diff_pct < 3 else "*" if diff_pct < 5 else ""
        print(f"    {name:20s} = {val:.8f}  ({diff_pct:5.2f}% off) {match}")

    print(f"\n  --- Constant matching (threshold b) ---")
    candidates_b = {
        "2*ln(3)": 2 * np.log(3),
        "ln(7)": np.log(7),
        "pi/e": np.pi / np.e,
        "ln(pi*e)": np.log(np.pi * np.e),
        "3*gamma": 3 * gamma,
        "2 + gamma": 2 + gamma,
        "e*gamma": np.e * gamma,
        "ln(3) + gamma": np.log(3) + gamma,
        "pi*gamma": np.pi * gamma,
        "sqrt(5)": np.sqrt(5),
        "ln(10)": np.log(10),
    }
    for name, val in sorted(candidates_b.items(), key=lambda x: abs(b - x[1])):
        diff_pct = abs(b - val) / b * 100
        match = "***" if diff_pct < 1 else "**" if diff_pct < 3 else "*" if diff_pct < 5 else ""
        print(f"    {name:20s} = {val:.8f}  ({diff_pct:5.2f}% off) {match}")

    print(f"\n  --- Ratio b/a (M at 50%) ---")
    ratio = b / a
    candidates_r = {
        "ln(2038)": np.log(2038),
        "e^2": np.e**2,
        "pi^2/2": np.pi**2 / 2,
        "2*pi": 2 * np.pi,
        "5*ln(2)": 5 * np.log(2),
        "ln(2000)": np.log(2000),
        "10*gamma": 10 * gamma,
        "3*e/2": 3 * np.e / 2,
    }
    print(f"    b/a = {ratio:.6f}")
    for name, val in sorted(candidates_r.items(), key=lambda x: abs(ratio - x[1])):
        diff_pct = abs(ratio - val) / ratio * 100
        match = "***" if diff_pct < 1 else "**" if diff_pct < 3 else ""
        print(f"    {name:20s} = {val:.6f}  ({diff_pct:5.2f}% off) {match}")

    # ============================================================
    # ARITHMOS: Independence in base e
    # ============================================================
    print(f"\n{'=' * 70}")
    print("ARITHMOS: A(x) = ln(torsion), independence check")
    print("=" * 70)

    A_ec = np.log(ec["torsion"].values.astype(float))
    r_ma, p_ma = spearmanr(M_ec, A_ec)
    print(f"  Spearman r(M, A) = {r_ma:.6f}, p = {p_ma:.2e}")
    print(f"  R^2 = {r_ma**2:.8f}")
    print(f"  INDEPENDENT: {'YES' if r_ma**2 < 0.01 else 'NO'}")

    # ============================================================
    # PHASMA: Zero spacings vs M
    # ============================================================
    print(f"\n{'=' * 70}")
    print("PHASMA: Normalized zero spacing vs Megethos")
    print("=" * 70)

    phasma = []
    for _, row in dz.iterrows():
        zeros = row.get("zeros_vector")
        cond = row.get("conductor")
        if (zeros is not None and cond and cond > 0
                and hasattr(zeros, "__len__") and len(zeros) >= 4):
            zc = sorted([float(z) for z in zeros if z is not None and z > 0])
            if len(zc) >= 4:
                sp = np.diff(zc)
                mu = np.mean(sp)
                if mu > 0:
                    norm_sp = sp / mu
                    phasma.append((np.log(float(cond)), float(np.median(norm_sp)),
                                   float(np.std(norm_sp)), len(zc)))

    print(f"  L-functions with spacing data: {len(phasma)}")

    if phasma:
        M_p = np.array([p[0] for p in phasma])
        med_p = np.array([p[1] for p in phasma])

        # Bin by M
        bins = np.linspace(M_p.min(), M_p.max(), 15)
        print(f"\n  {'M_center':>10s} {'N':>10s} {'median':>10s} {'n':>6s}")
        for i in range(len(bins) - 1):
            mask = (M_p >= bins[i]) & (M_p < bins[i + 1])
            if mask.sum() >= 5:
                mc = (bins[i] + bins[i + 1]) / 2
                print(f"  {mc:10.3f} {np.exp(mc):10.0f} {np.mean(med_p[mask]):10.6f} {mask.sum():6d}")

        # Test 1/pi at high M
        high = med_p[M_p > np.percentile(M_p, 80)]
        if len(high) > 10:
            hm = np.mean(high)
            print(f"\n  High-M median: {hm:.8f}")
            print(f"  1/pi         : {1/np.pi:.8f}  ({abs(hm - 1/np.pi)/hm*100:.2f}% off)")
            print(f"  ln(2)/2      : {np.log(2)/2:.8f}  ({abs(hm - np.log(2)/2)/hm*100:.2f}% off)")
            print(f"  gamma        : {gamma:.8f}  ({abs(hm - gamma)/hm*100:.2f}% off)")

    # ============================================================
    # SUMMARY
    # ============================================================
    print(f"\n{'=' * 70}")
    print("BASE-e PHONEME EQUATIONS (high precision)")
    print("=" * 70)
    print(f"  M(x) = ln N(x) = Sum f_p * ln(p)")
    print(f"  P(B >= 1) = sigmoid({a:.8f} * M - {b:.8f})")
    print(f"  S(x) = (-1)^B(x)  [exact]")
    print(f"  A(x) = ln(torsion)  [R^2 vs M = {r_ma**2:.6f}]")
    print(f"  All in base e.")

    # Save
    results = {
        "base": "e",
        "megethos": {"equation": "M(x) = ln N(x)"},
        "bathos_sigmoid": {
            "a": float(a), "a_err": float(perr[0]),
            "b": float(b), "b_err": float(perr[1]),
            "r2": float(r2),
            "M_50": float(b/a),
            "N_50": float(np.exp(b/a)),
            "closest_a": "gamma/2" if abs(a - gamma/2) < abs(a - np.log(4/3)) else "ln(4/3)",
            "closest_b": "2*ln(3)",
        },
        "arithmos_independence": {
            "spearman_r": float(r_ma),
            "r2": float(r_ma**2),
        },
    }
    out = ROOT / "cartography/convergence/data/base_e_calibration.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out.name}")


if __name__ == "__main__":
    main()
