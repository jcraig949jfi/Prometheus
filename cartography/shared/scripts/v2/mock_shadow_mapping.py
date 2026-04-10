"""
Mock Shadow Mapping — Find Moonshine Shadows Without the Definition
====================================================================
Challenge: J4 / Gemini P3-8

Every mock modular form has a "shadow" — a classical modular form related to it
by the holomorphic projection operator (xi operator). Can we rediscover this
relationship from coefficient fingerprints alone?

We compute mod-p residue distributions, growth rates, zero-frequency, and sign
patterns for both mock theta sequences (from OEIS) and 102K weight-2 modular
forms (from DuckDB), then match by fingerprint distance.

Honest assessment: the shadow relationship involves a differential operator at
weight 3/2 → weight 1/2, and our modular forms are all weight 2. We do NOT
expect exact recovery. We're looking for structural echoes.
"""

import json
import time
import numpy as np
from pathlib import Path
from collections import Counter
import duckdb

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR
OEIS_PATH = Path("F:/Prometheus/cartography/oeis/data/stripped_new.txt")
DB_PATH = Path("F:/Prometheus/charon/data/charon.duckdb")

# Mock theta function A-numbers and metadata
MOCK_THETA_SEQUENCES = {
    "A003114": {"name": "Ramanujan 3rd order mock theta f(q)", "order": 3, "type": "f"},
    "A000025": {"name": "Mock theta function psi", "order": 3, "type": "psi"},
    "A053250": {"name": "M24 umbral moonshine McKay-Thompson", "order": "umbral", "type": "McKay-Thompson"},
    "A053251": {"name": "3rd order mock theta chi(q)", "order": 3, "type": "chi"},
    "A053252": {"name": "3rd order mock theta omega(q)", "order": 3, "type": "omega"},
    "A053253": {"name": "3rd order mock theta nu(q)", "order": 3, "type": "nu_unsigned"},
    "A053254": {"name": "3rd order mock theta f(q) signed", "order": 3, "type": "f_signed"},
    "A053255": {"name": "3rd order mock theta omega(q) signed", "order": 3, "type": "omega_signed"},
    "A045488": {"name": "Mock theta / Maass form coefficients", "order": "mixed", "type": "maass_related"},
}

PRIMES = [2, 3, 5, 7, 11]

def load_oeis_sequences(targets):
    """Load target OEIS sequences from stripped file."""
    found = {}
    with open(OEIS_PATH) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(' ,')
            if len(parts) < 2:
                continue
            aid = parts[0].strip()
            if aid in targets:
                vals_str = line[line.index(',') + 1:].strip().rstrip(',')
                vals = [int(x) for x in vals_str.split(',') if x.strip()]
                found[aid] = vals
    return found


def compute_fingerprint(seq, max_terms=100):
    """
    Compute fingerprint vector from a coefficient sequence.

    Returns dict with:
      - mod_p_dist: for each prime p, distribution of residues (normalized)
      - growth_class: 0=constant, 1=sublinear, 2=linear, 3=polynomial, 4=exponential
      - growth_alpha: estimated polynomial exponent
      - zero_frac: fraction of terms that are 0
      - pos_frac: fraction positive
      - neg_frac: fraction negative
      - sign_changes: fraction of consecutive pairs with sign change
      - max_abs: maximum absolute value
    Also returns a flat numpy vector for distance computation.
    """
    arr = np.array(seq[:max_terms], dtype=float)
    n = len(arr)
    if n < 5:
        return None, None

    # --- mod-p residue distributions ---
    mod_p = {}
    int_arr = np.array(seq[:max_terms], dtype=int)
    for p in PRIMES:
        residues = int_arr % p
        counts = np.zeros(p)
        for r in residues:
            counts[r % p] += 1
        counts /= n
        mod_p[p] = counts.tolist()

    # --- growth classification ---
    abs_arr = np.abs(arr)
    nonzero_mask = abs_arr > 0
    if nonzero_mask.sum() >= 5:
        idx = np.arange(1, n + 1)
        # Fit log(|a_n|) ~ alpha * log(n) + c
        log_idx = np.log(idx[nonzero_mask])
        log_val = np.log(abs_arr[nonzero_mask])
        if len(log_idx) >= 3:
            try:
                alpha, c = np.polyfit(log_idx, log_val, 1)
            except:
                alpha = 0.0
        else:
            alpha = 0.0

        # Check for exponential growth
        max_val = abs_arr.max()
        if max_val > 1e10 and alpha > 5:
            growth_class = 4  # exponential
        elif alpha > 1.5:
            growth_class = 3  # polynomial
        elif alpha > 0.5:
            growth_class = 2  # linear
        elif alpha > 0.1:
            growth_class = 1  # sublinear
        else:
            growth_class = 0  # constant
    else:
        alpha = 0.0
        growth_class = 0

    # --- zero/sign fractions ---
    zero_frac = np.mean(arr == 0)
    pos_frac = np.mean(arr > 0)
    neg_frac = np.mean(arr < 0)

    # --- sign changes ---
    nonzero_vals = arr[arr != 0]
    if len(nonzero_vals) >= 2:
        signs = np.sign(nonzero_vals)
        sign_changes = np.mean(signs[1:] != signs[:-1])
    else:
        sign_changes = 0.0

    # --- build flat vector for matching ---
    # Concatenate: mod-p distributions + growth features + structural features
    vec_parts = []
    for p in PRIMES:
        vec_parts.extend(mod_p[p])
    vec_parts.extend([
        growth_class / 4.0,  # normalized
        alpha / 5.0,         # normalized
        zero_frac,
        pos_frac,
        neg_frac,
        sign_changes,
    ])
    vec = np.array(vec_parts)

    fp = {
        "mod_p": {str(p): mod_p[p] for p in PRIMES},
        "growth_class": growth_class,
        "growth_alpha": round(float(alpha), 3),
        "zero_frac": round(float(zero_frac), 4),
        "pos_frac": round(float(pos_frac), 4),
        "neg_frac": round(float(neg_frac), 4),
        "sign_changes": round(float(sign_changes), 4),
        "n_terms": n,
    }
    return fp, vec


def compute_mod_p_overlap(seq1, seq2, primes=PRIMES):
    """
    Compute mod-p structural overlap between two sequences.
    For each prime, check if the residue distributions match.
    Also check direct mod-p congruence rate.
    """
    n = min(len(seq1), len(seq2))
    if n < 5:
        return {}
    a = np.array(seq1[:n], dtype=int)
    b = np.array(seq2[:n], dtype=int)

    results = {}
    for p in primes:
        ar = a % p
        br = b % p
        # Direct congruence rate
        match_rate = np.mean(ar == br)
        # Expected under independence
        expected = 1.0 / p
        enrichment = match_rate / expected if expected > 0 else 0
        results[p] = {
            "match_rate": round(float(match_rate), 4),
            "expected_random": round(expected, 4),
            "enrichment": round(float(enrichment), 3),
        }
    return results


def main():
    t0 = time.time()
    print("=== Mock Shadow Mapping ===")
    print()

    # 1. Load mock theta sequences from OEIS
    print("[1] Loading mock theta sequences from OEIS...")
    mock_seqs = load_oeis_sequences(set(MOCK_THETA_SEQUENCES.keys()))
    print(f"    Found {len(mock_seqs)}/{len(MOCK_THETA_SEQUENCES)} sequences")
    for aid, vals in mock_seqs.items():
        meta = MOCK_THETA_SEQUENCES[aid]
        print(f"    {aid} ({meta['name']}): {len(vals)} terms, first 10: {vals[:10]}")

    # 2. Compute fingerprints for mock theta sequences
    print()
    print("[2] Computing mock theta fingerprints...")
    mock_fps = {}
    mock_vecs = {}
    for aid, vals in mock_seqs.items():
        fp, vec = compute_fingerprint(vals)
        if fp is not None:
            mock_fps[aid] = fp
            mock_vecs[aid] = vec
            print(f"    {aid}: growth={fp['growth_class']} alpha={fp['growth_alpha']} "
                  f"zero={fp['zero_frac']} pos={fp['pos_frac']} neg={fp['neg_frac']} "
                  f"sign_chg={fp['sign_changes']}")

    # 3. Load modular form traces and compute fingerprints
    print()
    print("[3] Loading modular forms from DuckDB and computing fingerprints...")
    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Process in batches for memory efficiency
    batch_size = 5000
    total = conn.execute("SELECT count(*) FROM modular_forms").fetchone()[0]
    print(f"    Total forms: {total}")

    mf_labels = []
    mf_vecs = []
    mf_fps = []
    mf_traces_cache = {}  # cache traces for top matches

    offset = 0
    while offset < total:
        rows = conn.execute(
            f"SELECT lmfdb_label, level, traces FROM modular_forms LIMIT {batch_size} OFFSET {offset}"
        ).fetchall()
        for label, level, traces in rows:
            if traces is None or len(traces) < 10:
                continue
            int_traces = [int(round(t)) for t in traces[:100]]
            fp, vec = compute_fingerprint(int_traces)
            if fp is not None:
                mf_labels.append(label)
                mf_vecs.append(vec)
                mf_fps.append(fp)
                # Don't cache all traces - too much memory
        offset += batch_size
        if offset % 20000 == 0:
            print(f"    Processed {offset}/{total}...")

    print(f"    Computed fingerprints for {len(mf_labels)} modular forms")
    mf_vecs_matrix = np.array(mf_vecs)  # shape: (N, D)

    # 4. Match each mock theta to closest modular forms by fingerprint
    print()
    print("[4] Matching mock theta fingerprints to modular forms...")
    TOP_K = 10
    match_results = {}

    for aid in sorted(mock_vecs.keys()):
        mvec = mock_vecs[aid]
        # Euclidean distance to all modular forms
        dists = np.linalg.norm(mf_vecs_matrix - mvec[None, :], axis=1)
        top_idx = np.argsort(dists)[:TOP_K]

        matches = []
        for rank, idx in enumerate(top_idx):
            matches.append({
                "rank": rank + 1,
                "label": mf_labels[idx],
                "distance": round(float(dists[idx]), 6),
                "mf_fingerprint": mf_fps[idx],
            })

        match_results[aid] = {
            "meta": MOCK_THETA_SEQUENCES[aid],
            "mock_fingerprint": mock_fps[aid],
            "top_matches": matches,
            "median_distance": round(float(np.median(dists)), 6),
            "min_distance": round(float(dists[top_idx[0]]), 6),
            "mean_distance": round(float(np.mean(dists)), 6),
        }

        meta = MOCK_THETA_SEQUENCES[aid]
        print(f"    {aid} ({meta['type']}): "
              f"best={matches[0]['label']} d={matches[0]['distance']:.4f} "
              f"median_d={np.median(dists):.4f}")

    # 5. Coefficient-level comparison for top matches
    print()
    print("[5] Coefficient-level mod-p comparison for top-5 matches...")

    for aid in sorted(mock_vecs.keys()):
        mock_seq = mock_seqs[aid]
        top5_labels = [m["label"] for m in match_results[aid]["top_matches"][:5]]

        # Fetch traces for top-5 matches
        placeholders = ",".join(f"'{l}'" for l in top5_labels)
        rows = conn.execute(
            f"SELECT lmfdb_label, traces FROM modular_forms WHERE lmfdb_label IN ({placeholders})"
        ).fetchall()
        label_to_traces = {r[0]: [int(round(t)) for t in r[1][:100]] for r in rows}

        coeff_comparisons = []
        for m in match_results[aid]["top_matches"][:5]:
            label = m["label"]
            if label in label_to_traces:
                mf_seq = label_to_traces[label]
                overlap = compute_mod_p_overlap(mock_seq, mf_seq)
                coeff_comparisons.append({
                    "label": label,
                    "rank": m["rank"],
                    "mod_p_overlap": {str(p): v for p, v in overlap.items()},
                })

                # Check scaling law: does enrichment grow with prime?
                enrichments = [overlap[p]["enrichment"] for p in PRIMES if p in overlap]
                if len(enrichments) >= 3:
                    # Linear fit of enrichment vs prime
                    primes_arr = np.array(PRIMES[:len(enrichments)])
                    enr_arr = np.array(enrichments)
                    if len(primes_arr) >= 2:
                        slope, intercept = np.polyfit(primes_arr, enr_arr, 1)
                        coeff_comparisons[-1]["enrichment_slope"] = round(float(slope), 6)
                        coeff_comparisons[-1]["enrichment_values"] = [round(e, 3) for e in enrichments]

        match_results[aid]["coeff_comparisons"] = coeff_comparisons

    # 6. Blind test: A003114 and A045488
    print()
    print("[6] Blind test on known mock-shadow cases...")
    blind_results = {}

    for aid in ["A003114", "A045488"]:
        if aid not in mock_seqs:
            continue
        mock_seq = mock_seqs[aid]
        mvec = mock_vecs[aid]
        dists = np.linalg.norm(mf_vecs_matrix - mvec[None, :], axis=1)
        top_idx = np.argsort(dists)[:5]

        # For the blind test, do deeper coefficient analysis
        top_labels = [mf_labels[i] for i in top_idx]
        placeholders = ",".join(f"'{l}'" for l in top_labels)
        rows = conn.execute(
            f"SELECT lmfdb_label, level, traces FROM modular_forms WHERE lmfdb_label IN ({placeholders})"
        ).fetchall()

        blind_matches = []
        for row in rows:
            label, level, traces = row
            mf_seq = [int(round(t)) for t in traces[:100]]
            overlap = compute_mod_p_overlap(mock_seq, mf_seq)

            # Compute correlation of absolute values
            n = min(len(mock_seq), len(mf_seq), 50)
            mock_abs = np.abs(np.array(mock_seq[:n], dtype=float))
            mf_abs = np.abs(np.array(mf_seq[:n], dtype=float))
            if np.std(mock_abs) > 0 and np.std(mf_abs) > 0:
                corr = float(np.corrcoef(mock_abs, mf_abs)[0, 1])
            else:
                corr = 0.0

            # Compute difference sequence and check if it has structure
            diff = np.array(mock_seq[:n]) - np.array(mf_seq[:n])
            diff_zero_frac = float(np.mean(diff == 0))

            rank = top_labels.index(label) + 1
            blind_matches.append({
                "label": label,
                "level": level,
                "rank": rank,
                "distance": round(float(dists[top_idx[rank - 1]]), 6),
                "abs_correlation": round(corr, 4),
                "diff_zero_frac": round(diff_zero_frac, 4),
                "mod_p_overlap": {str(p): v for p, v in overlap.items()},
            })

        blind_results[aid] = {
            "meta": MOCK_THETA_SEQUENCES[aid],
            "matches": sorted(blind_matches, key=lambda x: x["rank"]),
        }

        print(f"    {aid} ({MOCK_THETA_SEQUENCES[aid]['name']}):")
        for m in sorted(blind_matches, key=lambda x: x["rank"]):
            print(f"      #{m['rank']} {m['label']} (N={m['level']}): "
                  f"d={m['distance']:.4f} corr={m['abs_correlation']:.3f} "
                  f"mod2_enr={m['mod_p_overlap'].get('2', {}).get('enrichment', '?')}")

    # 7. Cross-mock-theta clustering: do mock thetas of the same order cluster?
    print()
    print("[7] Cross-mock-theta structural clustering...")
    mock_aids = sorted(mock_vecs.keys())
    n_mock = len(mock_aids)
    mock_dist_matrix = np.zeros((n_mock, n_mock))
    for i in range(n_mock):
        for j in range(n_mock):
            mock_dist_matrix[i, j] = np.linalg.norm(mock_vecs[mock_aids[i]] - mock_vecs[mock_aids[j]])

    print("    Distance matrix between mock theta functions:")
    print(f"    {'':>10}", end="")
    for aid in mock_aids:
        print(f"  {aid[-4:]:>6}", end="")
    print()
    for i, aid in enumerate(mock_aids):
        print(f"    {aid:>10}", end="")
        for j in range(n_mock):
            print(f"  {mock_dist_matrix[i,j]:6.3f}", end="")
        print()

    # Group by order
    order_groups = {}
    for aid in mock_aids:
        order = str(MOCK_THETA_SEQUENCES[aid]["order"])
        order_groups.setdefault(order, []).append(aid)

    intra_dists = []
    inter_dists = []
    for i in range(n_mock):
        for j in range(i + 1, n_mock):
            oi = str(MOCK_THETA_SEQUENCES[mock_aids[i]]["order"])
            oj = str(MOCK_THETA_SEQUENCES[mock_aids[j]]["order"])
            d = mock_dist_matrix[i, j]
            if oi == oj:
                intra_dists.append(d)
            else:
                inter_dists.append(d)

    clustering = {
        "intra_order_mean": round(float(np.mean(intra_dists)), 4) if intra_dists else None,
        "inter_order_mean": round(float(np.mean(inter_dists)), 4) if inter_dists else None,
        "separation_ratio": round(float(np.mean(inter_dists) / np.mean(intra_dists)), 3) if intra_dists and inter_dists and np.mean(intra_dists) > 0 else None,
    }
    print(f"    Intra-order mean dist: {clustering['intra_order_mean']}")
    print(f"    Inter-order mean dist: {clustering['inter_order_mean']}")
    print(f"    Separation ratio: {clustering['separation_ratio']}")

    # 8. Summary statistics and honest assessment
    print()
    print("[8] Summary and assessment...")

    # Check if top matches are significantly closer than median
    significance = {}
    for aid in mock_aids:
        min_d = match_results[aid]["min_distance"]
        med_d = match_results[aid]["median_distance"]
        mean_d = match_results[aid]["mean_distance"]
        # z-score approximation
        all_dists = np.linalg.norm(mf_vecs_matrix - mock_vecs[aid][None, :], axis=1)
        std_d = float(np.std(all_dists))
        z = (min_d - mean_d) / std_d if std_d > 0 else 0
        significance[aid] = {
            "min_d": round(min_d, 4),
            "median_d": round(med_d, 4),
            "z_score": round(z, 3),
            "percentile": round(float(np.mean(all_dists >= min_d) * 100), 2),
        }
        print(f"    {aid}: z={z:.2f}, min_d/median_d={min_d/med_d:.3f}, "
              f"best match is top {100 - significance[aid]['percentile']:.1f}%")

    # Check enrichment across all top matches
    all_enrichments = {p: [] for p in PRIMES}
    for aid in mock_aids:
        for comp in match_results[aid].get("coeff_comparisons", []):
            for p in PRIMES:
                sp = str(p)
                if sp in comp.get("mod_p_overlap", {}):
                    all_enrichments[p].append(comp["mod_p_overlap"][sp]["enrichment"])

    enrichment_summary = {}
    for p in PRIMES:
        vals = all_enrichments[p]
        if vals:
            enrichment_summary[str(p)] = {
                "mean": round(float(np.mean(vals)), 3),
                "std": round(float(np.std(vals)), 3),
                "max": round(float(np.max(vals)), 3),
                "n": len(vals),
            }
            print(f"    mod-{p} enrichment across top matches: "
                  f"mean={np.mean(vals):.3f} +/- {np.std(vals):.3f}, max={np.max(vals):.3f}")

    conn.close()
    elapsed = time.time() - t0

    # --- Build output ---
    output = {
        "meta": {
            "challenge": "Mock Shadow Mapping (J4/P3-8)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 1),
            "n_mock_theta": len(mock_seqs),
            "n_modular_forms": len(mf_labels),
            "fingerprint_dim": len(mock_vecs[mock_aids[0]]),
        },
        "mock_theta_fingerprints": {
            aid: mock_fps[aid] for aid in mock_aids
        },
        "fingerprint_matches": {
            aid: {
                "meta": match_results[aid]["meta"],
                "top_10": match_results[aid]["top_matches"],
                "stats": {
                    "min_distance": match_results[aid]["min_distance"],
                    "median_distance": match_results[aid]["median_distance"],
                    "mean_distance": match_results[aid]["mean_distance"],
                },
                "significance": significance[aid],
                "coeff_comparisons": match_results[aid].get("coeff_comparisons", []),
            }
            for aid in mock_aids
        },
        "blind_test": blind_results,
        "mock_theta_clustering": {
            "distance_matrix": {
                mock_aids[i]: {
                    mock_aids[j]: round(float(mock_dist_matrix[i, j]), 4)
                    for j in range(n_mock)
                }
                for i in range(n_mock)
            },
            "order_groups": order_groups,
            "clustering_stats": clustering,
        },
        "enrichment_summary": enrichment_summary,
        "assessment": {
            "shadow_recovery": "NOT ACHIEVED — weight mismatch is fundamental",
            "structural_echo": None,  # will be filled
            "fingerprint_discrimination": None,
            "scaling_law": None,
            "honest_summary": None,
        },
    }

    # Fill in assessment
    # Can the fingerprint discriminate at all?
    best_z = min(significance[aid]["z_score"] for aid in mock_aids)
    best_percentile = min(100 - significance[aid]["percentile"] for aid in mock_aids)

    if best_z < -3:
        output["assessment"]["fingerprint_discrimination"] = (
            f"YES: best z-score = {best_z:.2f}, top match in top {best_percentile:.1f}% — "
            "fingerprint identifies structurally similar forms"
        )
    elif best_z < -2:
        output["assessment"]["fingerprint_discrimination"] = (
            f"WEAK: best z-score = {best_z:.2f} — marginal discrimination"
        )
    else:
        output["assessment"]["fingerprint_discrimination"] = (
            f"NO: best z-score = {best_z:.2f} — matches not significantly closer than random"
        )

    # Is there a structural echo?
    mean_enrichments = [enrichment_summary[str(p)]["mean"] for p in PRIMES if str(p) in enrichment_summary]
    if mean_enrichments and max(mean_enrichments) > 1.5:
        output["assessment"]["structural_echo"] = (
            f"POSSIBLE: max mean enrichment = {max(mean_enrichments):.2f} at some prime — "
            "above random expectation"
        )
    elif mean_enrichments and max(mean_enrichments) > 1.1:
        output["assessment"]["structural_echo"] = (
            f"MARGINAL: max mean enrichment = {max(mean_enrichments):.2f} — barely above noise"
        )
    else:
        output["assessment"]["structural_echo"] = (
            "NONE: enrichment levels consistent with random matching"
        )

    # Scaling law check
    scaling_slopes = []
    for aid in mock_aids:
        for comp in match_results[aid].get("coeff_comparisons", []):
            if "enrichment_slope" in comp:
                scaling_slopes.append(comp["enrichment_slope"])
    if scaling_slopes:
        mean_slope = np.mean(scaling_slopes)
        if mean_slope > 0.01:
            output["assessment"]["scaling_law"] = (
                f"POSITIVE TREND: mean enrichment slope = {mean_slope:.4f} — "
                "enrichment grows with prime (consistent with structural relationship)"
            )
        elif mean_slope < -0.01:
            output["assessment"]["scaling_law"] = (
                f"NEGATIVE TREND: mean enrichment slope = {mean_slope:.4f} — "
                "enrichment decreases with prime (opposite of scaling law)"
            )
        else:
            output["assessment"]["scaling_law"] = (
                f"FLAT: mean enrichment slope = {mean_slope:.4f} — no scaling trend"
            )
    else:
        output["assessment"]["scaling_law"] = "INSUFFICIENT DATA"

    # Honest summary
    output["assessment"]["honest_summary"] = (
        "The mock-shadow relationship is mediated by the xi operator, which maps "
        "weight 1/2 harmonic Maass forms to weight 3/2 cusp forms. Our database "
        "contains only weight-2 newforms. The fingerprint matching therefore cannot "
        "recover the actual shadow — it can only detect whether mock theta functions "
        "share distributional properties (mod-p, growth, sign patterns) with any "
        "weight-2 forms. This is a test of STRUCTURAL SIMILARITY across weight spaces, "
        "not a test of the shadow map itself. "
        f"Results: fingerprint discrimination is {'present' if best_z < -2 else 'absent'}, "
        f"meaning the mock theta functions {'do' if best_z < -2 else 'do not'} look like "
        "a subset of the weight-2 landscape from the fingerprint perspective."
    )

    # Save results
    out_path = DATA_DIR / "mock_shadow_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n    Results saved to {out_path}")
    print(f"    Elapsed: {elapsed:.1f}s")

    # Print final assessment
    print()
    print("=" * 70)
    print("ASSESSMENT")
    print("=" * 70)
    for k, v in output["assessment"].items():
        print(f"  {k}: {v}")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
