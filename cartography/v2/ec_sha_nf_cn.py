"""
EC Sha vs NF Class Number Coupling (ChatGPT #12)
==================================================
Correlate analytic Sha size with class number via conductor matching
between elliptic curves and number fields.

Two approaches:
  A. Aggregated: mean(sha) per conductor <-> mean(class_number) per |disc|
     (avoids pair explosion from many-to-many matching)
  B. Raw pairs: degree-2 exact match only (manageable count)

Matching strategies (aggregated):
  1. Within-10%: |disc| within 10% of conductor
  2. Divisibility: |disc| divides conductor or vice versa (capped at 10x)
  3. Degree-2 exact: quadratic fields, |disc| == conductor
  4. Union of above

Null: 1000 random shuffles.
"""

import json
import sys
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# ── paths ──────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DUCKDB_PATH = REPO / "charon" / "data" / "charon.duckdb"
NF_PATH = REPO / "cartography" / "number_fields" / "data" / "number_fields.json"
OUT_JSON = REPO / "cartography" / "v2" / "ec_sha_nf_cn_results.json"

N_NULL = 1000
RNG = np.random.default_rng(42)


def load_ec():
    """Load EC data from DuckDB: conductor, sha (analytic)."""
    import duckdb
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    rows = con.sql(
        "SELECT conductor, sha FROM elliptic_curves WHERE sha IS NOT NULL AND sha > 0"
    ).fetchall()
    con.close()
    return [(int(r[0]), int(r[1])) for r in rows]


def load_nf():
    """Load NF fields: |disc|, class_number, degree."""
    with open(NF_PATH) as f:
        data = json.load(f)
    out = []
    for rec in data:
        disc = abs(int(rec["disc_abs"]))
        cn = int(rec["class_number"])
        deg = int(rec["degree"])
        if disc > 0 and cn > 0:
            out.append((disc, cn, deg))
    return out


def aggregate_ec(ec_list):
    """Mean sha per conductor."""
    by_cond = defaultdict(list)
    for cond, sha in ec_list:
        by_cond[cond].append(sha)
    return {c: np.mean(v) for c, v in by_cond.items()}


def aggregate_nf(nf_list, degree_filter=None):
    """Mean class_number per |disc|, optionally filtered by degree."""
    by_disc = defaultdict(list)
    for disc, cn, deg in nf_list:
        if degree_filter is not None and deg != degree_filter:
            continue
        by_disc[disc].append(cn)
    return {d: np.mean(v) for d, v in by_disc.items()}


# ── Matching (aggregated) ──────────────────────────────────────────────

def match_within_10pct(ec_agg, nf_agg):
    """Match conductor to |disc| within 10%."""
    nf_sorted = sorted(nf_agg.items())
    nf_discs = np.array([d for d, _ in nf_sorted])
    nf_cns = np.array([cn for _, cn in nf_sorted])

    pairs = []
    for cond, mean_sha in ec_agg.items():
        lo, hi = cond * 0.9, cond * 1.1
        idx_lo = np.searchsorted(nf_discs, lo, side="left")
        idx_hi = np.searchsorted(nf_discs, hi, side="right")
        for i in range(idx_lo, idx_hi):
            pairs.append((mean_sha, nf_cns[i]))
    return pairs


def match_divisibility(ec_agg, nf_agg):
    """Match where |disc| divides conductor or conductor divides |disc|, capped at 10x."""
    nf_discs_sorted = sorted(nf_agg.keys())
    pairs = []
    for cond, mean_sha in ec_agg.items():
        for disc in nf_discs_sorted:
            if disc > cond * 10:
                break
            if (disc <= cond and cond % disc == 0) or \
               (disc > cond and disc % cond == 0):
                pairs.append((mean_sha, nf_agg[disc]))
    return pairs


def match_exact(ec_agg, nf_agg):
    """Exact conductor == |disc| match."""
    pairs = []
    common = set(ec_agg.keys()) & set(nf_agg.keys())
    for key in common:
        pairs.append((ec_agg[key], nf_agg[key]))
    return pairs


# ── Raw pair matching for degree-2 exact ───────────────────────────────

def match_degree2_raw(ec_list, nf_list):
    """Raw pairs: degree-2 NF, |disc| == conductor."""
    nf_deg2 = defaultdict(list)
    for disc, cn, deg in nf_list:
        if deg == 2:
            nf_deg2[disc].append(cn)
    pairs = []
    for cond, sha in ec_list:
        if cond in nf_deg2:
            for cn in nf_deg2[cond]:
                pairs.append((sha, cn))
    return pairs


# ── Correlation ────────────────────────────────────────────────────────

def correlate(pairs, label, subsample=None):
    """Spearman + Pearson on log-log, with null shuffle distribution."""
    if len(pairs) < 10:
        return {
            "method": label,
            "n_pairs": len(pairs),
            "status": "too_few_pairs",
        }

    sha_vals = np.array([p[0] for p in pairs], dtype=float)
    cn_vals = np.array([p[1] for p in pairs], dtype=float)

    # Subsample if too large
    if subsample and len(pairs) > subsample:
        idx = RNG.choice(len(pairs), subsample, replace=False)
        sha_vals = sha_vals[idx]
        cn_vals = cn_vals[idx]

    log_sha = np.log1p(sha_vals)
    log_cn = np.log1p(cn_vals)

    r_obs, p_obs = stats.spearmanr(log_sha, log_cn)
    r_pearson, p_pearson = stats.pearsonr(log_sha, log_cn)

    # Null: shuffle cn_vals
    null_rs = np.empty(N_NULL)
    for i in range(N_NULL):
        shuffled = RNG.permutation(cn_vals)
        null_rs[i], _ = stats.spearmanr(log_sha, np.log1p(shuffled))

    null_mean = float(np.mean(null_rs))
    null_std = float(np.std(null_rs))
    z_score = (r_obs - null_mean) / null_std if null_std > 1e-12 else 0.0

    return {
        "method": label,
        "n_pairs": len(pairs),
        "unique_sha_values": len(set(sha_vals.tolist())),
        "unique_cn_values": len(set(cn_vals.tolist())),
        "spearman_r": round(float(r_obs), 6),
        "spearman_p": float(p_obs),
        "pearson_r": round(float(r_pearson), 6),
        "pearson_p": float(p_pearson),
        "null_mean": round(null_mean, 6),
        "null_std": round(null_std, 6),
        "z_vs_null": round(z_score, 3),
        "null_5th": round(float(np.percentile(null_rs, 5)), 6),
        "null_95th": round(float(np.percentile(null_rs, 95)), 6),
    }


# ── Restricted analysis: sha > 1 only ─────────────────────────────────

def filter_sha_gt1(ec_list):
    """Keep only curves with sha > 1 for dynamic range."""
    return [(c, s) for c, s in ec_list if s > 1]


def main():
    print("Loading EC data from DuckDB...")
    ec_list = load_ec()
    print(f"  {len(ec_list)} curves with sha > 0")

    print("Loading NF data...")
    nf_list = load_nf()
    print(f"  {len(nf_list)} fields with disc > 0 and cn > 0")

    # Aggregate
    ec_agg = aggregate_ec(ec_list)
    nf_agg_all = aggregate_nf(nf_list)
    nf_agg_deg2 = aggregate_nf(nf_list, degree_filter=2)
    print(f"  {len(ec_agg)} unique conductors, {len(nf_agg_all)} unique |disc|, {len(nf_agg_deg2)} degree-2 |disc|")

    # ── Aggregated matching ─────────────────────────────────────────────
    print("\n--- Aggregated matching (mean sha per cond, mean cn per disc) ---")

    strategies = {}
    print("Strategy 1: within 10% ...")
    strategies["agg_within_10pct"] = match_within_10pct(ec_agg, nf_agg_all)
    print(f"  {len(strategies['agg_within_10pct'])} pairs")

    print("Strategy 2: divisibility (capped 10x) ...")
    strategies["agg_divisibility"] = match_divisibility(ec_agg, nf_agg_all)
    print(f"  {len(strategies['agg_divisibility'])} pairs")

    print("Strategy 3: exact conductor == |disc| (all degrees) ...")
    strategies["agg_exact_all"] = match_exact(ec_agg, nf_agg_all)
    print(f"  {len(strategies['agg_exact_all'])} pairs")

    print("Strategy 4: exact conductor == |disc| (degree-2 only) ...")
    strategies["agg_exact_deg2"] = match_exact(ec_agg, nf_agg_deg2)
    print(f"  {len(strategies['agg_exact_deg2'])} pairs")

    # Union
    all_agg = list(set(
        [tuple(p) for p in strategies["agg_within_10pct"]] +
        [tuple(p) for p in strategies["agg_divisibility"]] +
        [tuple(p) for p in strategies["agg_exact_all"]]
    ))
    strategies["agg_union"] = all_agg
    print(f"Union: {len(all_agg)} unique pairs")

    # ── Raw degree-2 exact pairs ────────────────────────────────────────
    print("\n--- Raw pair matching (degree-2 exact) ---")
    raw_deg2 = match_degree2_raw(ec_list, nf_list)
    print(f"  {len(raw_deg2)} raw pairs")
    strategies["raw_deg2_exact"] = raw_deg2

    # ── sha > 1 restricted ──────────────────────────────────────────────
    print("\n--- Restricted: sha > 1 only ---")
    ec_gt1 = filter_sha_gt1(ec_list)
    print(f"  {len(ec_gt1)} curves with sha > 1")
    ec_agg_gt1 = aggregate_ec(ec_gt1)
    strategies["agg_exact_all_sha_gt1"] = match_exact(ec_agg_gt1, nf_agg_all)
    print(f"  exact match: {len(strategies['agg_exact_all_sha_gt1'])} pairs")
    strategies["raw_deg2_sha_gt1"] = match_degree2_raw(ec_gt1, nf_list)
    print(f"  raw deg2: {len(strategies['raw_deg2_sha_gt1'])} pairs")

    # ── Correlations ────────────────────────────────────────────────────
    print("\n--- Correlations ---")
    results = []
    for label, pairs in strategies.items():
        print(f"\n{label} ({len(pairs)} pairs) ...")
        # Subsample large sets for null computation speed
        sub = 50000 if len(pairs) > 50000 else None
        res = correlate(pairs, label, subsample=sub)
        results.append(res)
        if "spearman_r" in res:
            print(f"  r_spearman = {res['spearman_r']:.4f} (p={res['spearman_p']:.2e})")
            print(f"  r_pearson  = {res['pearson_r']:.4f} (p={res['pearson_p']:.2e})")
            print(f"  z_vs_null  = {res['z_vs_null']:.2f}")
        else:
            print(f"  {res['status']}")

    # ── sha distribution ────────────────────────────────────────────────
    sha_counts = defaultdict(int)
    for cond, sha in ec_list:
        sha_counts[sha] += 1
    sha_dist = {str(k): v for k, v in sorted(sha_counts.items())}

    # ── verdict ─────────────────────────────────────────────────────────
    # Only count exact/degree-2 strategies as clean tests;
    # divisibility inflates pair count for disc=1,2,3 etc. which is structural bias
    clean = [r for r in results if r.get("z_vs_null") and "divisib" not in r["method"] and "union" not in r["method"]]
    sig_clean = [r for r in clean if abs(r["z_vs_null"]) > 2.0]
    sig_all = [r for r in results if r.get("z_vs_null") and abs(r["z_vs_null"]) > 2.0]

    if sig_clean:
        methods = [r["method"] for r in sig_clean]
        best_z = max(abs(r["z_vs_null"]) for r in sig_clean)
        verdict = f"SIGNAL: {len(sig_clean)} clean strategies exceed |z|>2 (best |z|={best_z:.1f}): {methods}"
    elif sig_all:
        verdict = ("NULL (artifact): divisibility/union show |z|>2 but driven by structural bias "
                    "(small disc values divide many conductors); clean exact-match tests all |z|<2")
    else:
        verdict = "NULL: no matching strategy exceeds |z| = 2 vs random pairing"

    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")

    # ── save ────────────────────────────────────────────────────────────
    output = {
        "investigation": "EC Sha vs NF Class Number Coupling (ChatGPT #12)",
        "ec_count": len(ec_list),
        "ec_sha_gt1_count": len(ec_gt1),
        "nf_count": len(nf_list),
        "unique_conductors": len(ec_agg),
        "unique_nf_discs": len(nf_agg_all),
        "sha_distribution": sha_dist,
        "matching_results": results,
        "null_shuffles": N_NULL,
        "verdict": verdict,
        "notes": [
            "sha = analytic Sha (integer) from LMFDB EC database",
            "class_number from LMFDB number fields",
            "97% of EC have sha=1 — severely limits correlation dynamic range",
            "Aggregated strategies: mean(sha) per conductor vs mean(cn) per |disc|",
            "Raw pairs only for degree-2 exact (manageable pair count)",
            "sha>1 restricted tests isolate the non-trivial Sha tail",
            "Divisibility capped at disc/cond ratio <= 10x",
        ],
    }

    with open(OUT_JSON, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {OUT_JSON}")


if __name__ == "__main__":
    main()
