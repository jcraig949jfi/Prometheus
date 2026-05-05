#!/usr/bin/env python3
"""
Assemble paper artifacts for F011 paper-drafting cycle (per Aporia 1776921390195).

Outputs: ergon/results/paper_artifacts/
  - figure1_family_deficit_curves.csv  (24-gap deficit per family per k)
  - figure3_nbp_vs_k_deficit.csv       (nbp x k matrix of deficits)
  - table2_nbp_by_symmetry.csv         (6 rows: family, symmetry, n, rho_g1, rho_g24)
  - table2.tex                         (LaTeX version of table 2)
  - supplement_seed2.csv               (49K-curve gap-k scan deficits)
  - supplement_seed13.csv              (Dirichlet nbp breakdown + split)
"""
import json
import csv
from pathlib import Path

RESULTS = Path("F:/prometheus/ergon/results")
OUT = RESULTS / "paper_artifacts"
OUT.mkdir(exist_ok=True, parents=True)


def _load(p):
    with open(p) as f:
        return json.load(f)


def figure1():
    """3-family deficit curves at 24-gap norm."""
    ec = _load(RESULTS / "gap_k_scan.json")
    cm = _load(RESULTS / "cm_gap_k.json")
    g2c = _load(RESULTS / "g2c_gap_k.json")

    ec_def = ec["deficit_pct_per_k"]
    cm_def = cm["pooled_deficits_pct"]
    g2c_def = g2c["deficits_pct"]

    rows = []
    for k in range(min(len(ec_def), len(cm_def), len(g2c_def))):
        rows.append({
            "k": k + 1,
            "EC_rank0_nonCM_OPlus": ec_def[k],
            "EC_rank0_CM": cm_def[k],
            "G2C_rank0_USp4": g2c_def[k],
        })
    with open(OUT / "figure1_family_deficit_curves.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["k", "EC_rank0_nonCM_OPlus", "EC_rank0_CM", "G2C_rank0_USp4"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"figure1: {len(rows)} rows -> {OUT / 'figure1_family_deficit_curves.csv'}")


def figure3():
    """nbp x bulk-k deficit matrix for non-CM EC."""
    d = _load(RESULTS / "nbp_bulk_k.json")
    per_nbp = d["per_nbp"]
    with open(OUT / "figure3_nbp_vs_k_deficit.csv", "w", newline="") as f:
        w = csv.writer(f)
        nbps = sorted(per_nbp.keys(), key=int)
        w.writerow(["k"] + [f"nbp_{n}" for n in nbps])
        n_k = len(per_nbp[nbps[0]]["deficits_pct"])
        for k in range(n_k):
            row = [k + 1]
            for n in nbps:
                row.append(round(per_nbp[n]["deficits_pct"][k], 2))
            w.writerow(row)
    print(f"figure3: {n_k} rows x {len(nbps)} nbp cols -> {OUT / 'figure3_nbp_vs_k_deficit.csv'}")


def table2():
    """6-row Axis 3b family-vs-nbp-rho table."""
    rows = [
        ("EC rank-0 non-CM",     "O+",            150_000, "+1.000", "+1.000", "bulk k=8 at +16.8%"),
        ("EC rank-1 non-CM",     "O-",             80_000, "+1.000", "+0.660", "consistent with O family"),
        ("CM EC rank-0",         "mixed/U(1)^h",    2_134, "-0.50",  "+0.50",  "INCONCLUSIVE at n=2K; needs ingest"),
        ("Dirichlet complex",    "U (unitary)",    40_000, "+1.000", "+1.000", "per-curve signal beyond KS 2-point (0)"),
        ("Dirichlet real",       "O+ subfamily",    3_898, "+1.000", "+1.000", "same direction as complex, higher intercept"),
        ("Genus-2 rank-0",       "USp(4)",         11_856, "-0.900", "-0.900", "UNIQUE negative"),
    ]
    with open(OUT / "table2_nbp_by_symmetry.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Family", "Symmetry Class", "n", "Spearman rho (gap1)", "Spearman rho (gap24)", "Notes"])
        for r in rows:
            w.writerow(r)
    with open(OUT / "table2.tex", "w") as f:
        f.write(r"""\begin{table}[h]
\centering
\caption{Spearman correlation of num\_bad\_primes (nbp) with local-gap variance deficit, by L-function family. The Symplectic family uniquely shows negative direction.}
\label{tab:nbp_by_symmetry}
\begin{tabular}{lllccl}
\toprule
Family & Symmetry & $n$ & $\rho_{\mathrm{gap1}}$ & $\rho_{\mathrm{gap24}}$ & Notes \\
\midrule
""")
        for r in rows:
            f.write(f"{r[0]} & {r[1]} & {r[2]:,} & ${r[3]}$ & ${r[4]}$ & {r[5]} \\\\\n")
        f.write(r"""\bottomrule
\end{tabular}
\end{table}
""")
    print(f"table2: 6 rows -> {OUT / 'table2.tex'} + .csv")


def supplement_seed2():
    """Raw 24-gap deficit curve for EC rank-0 non-CM (Seed 2 scan)."""
    d = _load(RESULTS / "gap_k_scan.json")
    with open(OUT / "supplement_seed2.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "data_var", "null_var", "deficit_pct"])
        for k, (dv, nv, dp) in enumerate(zip(d["data_var_per_k"], d["null_var_per_k"], d["deficit_pct_per_k"])):
            w.writerow([k + 1, round(dv, 6), round(nv, 6), round(dp, 4)])
    print(f"supplement_seed2: 24 rows -> {OUT / 'supplement_seed2.csv'}")


def supplement_seed13():
    """Dirichlet nbp breakdown — pooled + real/complex split."""
    pooled = _load(RESULTS / "dirichlet_nbp.json")
    split = _load(RESULTS / "dirichlet_real_complex.json")

    rows = []
    for nbp, data in sorted(pooled.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 99):
        if not isinstance(data, dict) or 'deficits_pct' not in data:
            continue
        d_k = data.get("deficits_pct") or data.get("deficits")
        if not d_k: continue
        rows.append(["pooled", int(nbp), data["n"], round(d_k[0], 2), round(d_k[3], 2), round(d_k[7], 2), round(d_k[23], 2)])

    for subset_name in ("complex", "real"):
        subset = split.get(subset_name, {})
        for nbp, data in sorted(subset.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 99):
            if not isinstance(data, dict) or 'deficits' not in data:
                continue
            d_k = data["deficits"]
            rows.append([subset_name, int(nbp), data["n"], round(d_k[0], 2), round(d_k[3], 2), round(d_k[7], 2), round(d_k[23], 2)])

    with open(OUT / "supplement_seed13.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subset", "nbp", "n", "deficit_k1", "deficit_k4", "deficit_k8", "deficit_k24"])
        for r in rows:
            w.writerow(r)
    print(f"supplement_seed13: {len(rows)} rows -> {OUT / 'supplement_seed13.csv'}")


def main():
    figure1()
    figure3()
    table2()
    supplement_seed2()
    supplement_seed13()
    print(f"\nAll artifacts in {OUT}")


if __name__ == "__main__":
    main()
