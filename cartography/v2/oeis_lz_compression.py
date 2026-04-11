"""
OEIS Lempel-Ziv Asymptotic Compression Limit (List2 #16)

Binarize integer sequences by parity, compress with zlib (LZ77-based),
regress compressed/uncompressed ratio to find asymptotic limit.
Also compares BM-recurrent vs non-recurrent parity sequences.
"""

import json
import zlib
import numpy as np
from scipy.optimize import curve_fit
from pathlib import Path
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "oeis" / "data"
STRIPPED = DATA_DIR / "stripped_new.txt"
KEYWORDS_FILE = DATA_DIR / "oeis_keywords.json"
OUT_JSON = Path(__file__).resolve().parent / "oeis_lz_compression_results.json"
MIN_TERMS = 20
MAX_SEQS = 10_000


# ── Berlekamp-Massey over GF(2) ────────────────────────────────────────
def berlekamp_massey_gf2(bits):
    """Return minimal LFSR length for binary sequence over GF(2)."""
    n = len(bits)
    s = list(bits)
    # C = current connection polynomial, B = previous
    C = [1]
    B = [1]
    L = 0  # current LFSR length
    m = 1  # shift count
    b = 1  # previous discrepancy (always 1 in GF(2))

    for N_idx in range(n):
        # discrepancy
        d = s[N_idx]
        for i in range(1, L + 1):
            if i < len(C):
                d ^= C[i] & s[N_idx - i]
        if d == 0:
            m += 1
        else:
            T = list(C)
            # C = C + x^m * B  (over GF(2))
            pad = [0] * m
            shifted_B = pad + B
            while len(C) < len(shifted_B):
                C.append(0)
            for i in range(len(shifted_B)):
                C[i] ^= shifted_B[i]
            if 2 * L <= N_idx:
                L = N_idx + 1 - L
                B = T
                b = d
                m = 1
            else:
                m += 1
    return L


def is_bm_recurrent(bits, threshold=0.5):
    """A parity sequence is BM-recurrent if LFSR length < threshold * seq_length."""
    if len(bits) < 6:
        return False
    L = berlekamp_massey_gf2(bits)
    return L < threshold * len(bits)


# ── Load sequences ─────────────────────────────────────────────────────
def load_sequences():
    """Load sequences from stripped_new.txt, return list of (seq_id, terms)."""
    seqs = []
    with open(STRIPPED, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            term_str = parts[1].strip().strip(",")
            if not term_str:
                continue
            try:
                terms = [int(x) for x in term_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= MIN_TERMS:
                seqs.append((seq_id, terms))
            if len(seqs) >= MAX_SEQS:
                break
    return seqs


# ── Compression analysis ───────────────────────────────────────────────
def compress_parity(terms):
    """Convert to parity bits, compress, return (uncompressed_len, compressed_len, ratio, bits)."""
    bits = [t % 2 for t in terms]
    # Pack into bytes for compression
    parity_str = "".join(str(b) for b in bits).encode("ascii")
    compressed = zlib.compress(parity_str, level=9)
    uncomp_len = len(parity_str)
    comp_len = len(compressed)
    ratio = comp_len / uncomp_len if uncomp_len > 0 else 1.0
    return uncomp_len, comp_len, ratio, bits


def asymptotic_model(n, a, b, c):
    """ratio(n) = a + b / n^c"""
    return a + b / np.power(n, c)


def fit_asymptotic(lengths, ratios):
    """Fit ratio = a + b/n^c model. Returns (a, b, c) and R^2."""
    lengths = np.array(lengths, dtype=float)
    ratios = np.array(ratios, dtype=float)

    try:
        popt, pcov = curve_fit(
            asymptotic_model, lengths, ratios,
            p0=[0.4, 5.0, 0.5],
            bounds=([0, -100, 0.01], [2, 100, 3.0]),
            maxfev=10000,
        )
        residuals = ratios - asymptotic_model(lengths, *popt)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((ratios - np.mean(ratios)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return tuple(popt), r_squared
    except Exception as e:
        print(f"  Fit failed: {e}")
        return (np.median(ratios), 0.0, 1.0), 0.0


# ── Binned analysis ────────────────────────────────────────────────────
def binned_stats(lengths, ratios, n_bins=20):
    """Bin by length, return bin centers and mean ratios."""
    lengths = np.array(lengths)
    ratios = np.array(ratios)
    bins = np.linspace(lengths.min(), lengths.max(), n_bins + 1)
    centers, means, stds, counts = [], [], [], []
    for i in range(n_bins):
        mask = (lengths >= bins[i]) & (lengths < bins[i + 1])
        if i == n_bins - 1:
            mask = (lengths >= bins[i]) & (lengths <= bins[i + 1])
        if mask.sum() > 0:
            centers.append((bins[i] + bins[i + 1]) / 2)
            means.append(ratios[mask].mean())
            stds.append(ratios[mask].std())
            counts.append(int(mask.sum()))
    return centers, means, stds, counts


# ── Main ───────────────────────────────────────────────────────────────
def main():
    print("Loading OEIS sequences...")
    seqs = load_sequences()
    print(f"  Loaded {len(seqs)} sequences with >= {MIN_TERMS} terms")

    # Load keywords for enrichment
    print("Loading keywords...")
    try:
        with open(KEYWORDS_FILE, "r") as f:
            keywords = json.load(f)
    except Exception:
        keywords = {}

    print("Compressing parity sequences...")
    records = []
    bm_recurrent_ids = []
    bm_nonrecurrent_ids = []

    for seq_id, terms in seqs:
        uncomp_len, comp_len, ratio, bits = compress_parity(terms)
        bm_rec = is_bm_recurrent(bits)

        kw = keywords.get(seq_id, [])
        records.append({
            "seq_id": seq_id,
            "n_terms": len(terms),
            "uncompressed_bytes": uncomp_len,
            "compressed_bytes": comp_len,
            "ratio": ratio,
            "bm_recurrent": bm_rec,
            "bm_lfsr_length": berlekamp_massey_gf2(bits),
            "keywords": kw,
        })
        if bm_rec:
            bm_recurrent_ids.append(len(records) - 1)
        else:
            bm_nonrecurrent_ids.append(len(records) - 1)

    lengths = [r["n_terms"] for r in records]
    ratios = [r["ratio"] for r in records]

    # ── Global fit ──
    print("\nFitting asymptotic model: ratio(n) = a + b/n^c ...")
    (a_global, b_global, c_global), r2_global = fit_asymptotic(lengths, ratios)
    print(f"  Global asymptotic limit a = {a_global:.6f}")
    print(f"  b = {b_global:.4f}, c = {c_global:.4f}, R² = {r2_global:.4f}")

    # ── BM-recurrent vs non-recurrent ──
    rec_lengths = [records[i]["n_terms"] for i in bm_recurrent_ids]
    rec_ratios = [records[i]["ratio"] for i in bm_recurrent_ids]
    nonrec_lengths = [records[i]["n_terms"] for i in bm_nonrecurrent_ids]
    nonrec_ratios = [records[i]["ratio"] for i in bm_nonrecurrent_ids]

    print(f"\nBM-recurrent: {len(bm_recurrent_ids)} sequences")
    print(f"BM-non-recurrent: {len(bm_nonrecurrent_ids)} sequences")

    if len(rec_ratios) > 10:
        (a_rec, b_rec, c_rec), r2_rec = fit_asymptotic(rec_lengths, rec_ratios)
        print(f"  Recurrent asymptotic limit a = {a_rec:.6f}, R² = {r2_rec:.4f}")
    else:
        a_rec, b_rec, c_rec, r2_rec = None, None, None, None
        print("  Too few recurrent sequences for fit")

    if len(nonrec_ratios) > 10:
        (a_nonrec, b_nonrec, c_nonrec), r2_nonrec = fit_asymptotic(nonrec_lengths, nonrec_ratios)
        print(f"  Non-recurrent asymptotic limit a = {a_nonrec:.6f}, R² = {r2_nonrec:.4f}")
    else:
        a_nonrec, b_nonrec, c_nonrec, r2_nonrec = None, None, None, None
        print("  Too few non-recurrent sequences for fit")

    # ── Binned convergence ──
    centers, means, stds, counts = binned_stats(lengths, ratios)

    # ── Summary statistics ──
    ratios_arr = np.array(ratios)
    lengths_arr = np.array(lengths)

    # Quartile analysis by length
    q25, q50, q75 = np.percentile(lengths_arr, [25, 50, 75])
    long_mask = lengths_arr >= q75
    short_mask = lengths_arr <= q25

    summary = {
        "n_sequences": len(records),
        "min_terms": MIN_TERMS,
        "global_fit": {
            "asymptotic_limit_a": round(float(a_global), 6),
            "b": round(float(b_global), 4),
            "c": round(float(c_global), 4),
            "r_squared": round(float(r2_global), 4),
        },
        "global_stats": {
            "mean_ratio": round(float(ratios_arr.mean()), 6),
            "median_ratio": round(float(np.median(ratios_arr)), 6),
            "std_ratio": round(float(ratios_arr.std()), 6),
            "min_ratio": round(float(ratios_arr.min()), 6),
            "max_ratio": round(float(ratios_arr.max()), 6),
            "mean_length": round(float(lengths_arr.mean()), 1),
            "max_length": int(lengths_arr.max()),
        },
        "length_quartile_means": {
            "short_q25_mean_ratio": round(float(ratios_arr[short_mask].mean()), 6) if short_mask.sum() > 0 else None,
            "long_q75_mean_ratio": round(float(ratios_arr[long_mask].mean()), 6) if long_mask.sum() > 0 else None,
        },
        "bm_recurrent": {
            "count": len(bm_recurrent_ids),
            "mean_ratio": round(float(np.mean(rec_ratios)), 6) if rec_ratios else None,
            "median_ratio": round(float(np.median(rec_ratios)), 6) if rec_ratios else None,
            "fit": {
                "asymptotic_limit_a": round(float(a_rec), 6) if a_rec is not None else None,
                "b": round(float(b_rec), 4) if b_rec is not None else None,
                "c": round(float(c_rec), 4) if c_rec is not None else None,
                "r_squared": round(float(r2_rec), 4) if r2_rec is not None else None,
            },
        },
        "bm_non_recurrent": {
            "count": len(bm_nonrecurrent_ids),
            "mean_ratio": round(float(np.mean(nonrec_ratios)), 6) if nonrec_ratios else None,
            "median_ratio": round(float(np.median(nonrec_ratios)), 6) if nonrec_ratios else None,
            "fit": {
                "asymptotic_limit_a": round(float(a_nonrec), 6) if a_nonrec is not None else None,
                "b": round(float(b_nonrec), 4) if b_nonrec is not None else None,
                "c": round(float(c_nonrec), 4) if c_nonrec is not None else None,
                "r_squared": round(float(r2_nonrec), 4) if r2_nonrec is not None else None,
            },
        },
        "binned_convergence": {
            "bin_centers": [round(c, 1) for c in centers],
            "mean_ratios": [round(m, 6) for m in means],
            "std_ratios": [round(s, 6) for s in stds],
            "counts": counts,
        },
    }

    # ── Most/least compressible ──
    sorted_by_ratio = sorted(records, key=lambda r: r["ratio"])
    summary["most_compressible"] = [
        {"seq_id": r["seq_id"], "ratio": round(r["ratio"], 6), "n_terms": r["n_terms"]}
        for r in sorted_by_ratio[:10]
    ]
    summary["least_compressible"] = [
        {"seq_id": r["seq_id"], "ratio": round(r["ratio"], 6), "n_terms": r["n_terms"]}
        for r in sorted_by_ratio[-10:]
    ]

    # ── Keyword enrichment: do certain keyword classes compress differently? ──
    kw_ratios = defaultdict(list)
    for r in records:
        for kw in r["keywords"]:
            kw_ratios[kw].append(r["ratio"])

    kw_summary = {}
    for kw, rats in sorted(kw_ratios.items()):
        if len(rats) >= 20:
            kw_summary[kw] = {
                "count": len(rats),
                "mean_ratio": round(float(np.mean(rats)), 6),
                "median_ratio": round(float(np.median(rats)), 6),
            }
    summary["keyword_compression"] = kw_summary

    # ── Save ──
    print(f"\nSaving results to {OUT_JSON}")
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n== RESULTS ==")
    print(f"  Sequences analyzed: {len(records)}")
    print(f"  Global asymptotic compression limit: {a_global:.6f}")
    print(f"  Global mean ratio: {ratios_arr.mean():.6f}")
    print(f"  BM-recurrent: {len(bm_recurrent_ids)} (mean ratio {np.mean(rec_ratios):.4f})" if rec_ratios else "")
    print(f"  BM-non-recurrent: {len(bm_nonrecurrent_ids)} (mean ratio {np.mean(nonrec_ratios):.4f})" if nonrec_ratios else "")
    print(f"  Short seqs (Q25) mean ratio: {ratios_arr[short_mask].mean():.4f}")
    print(f"  Long seqs (Q75) mean ratio: {ratios_arr[long_mask].mean():.4f}")
    print(f"\n  Expected ~0.42, got: {a_global:.4f}")


if __name__ == "__main__":
    main()
