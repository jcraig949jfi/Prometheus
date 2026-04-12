"""
M33: Prime atmosphere residual rank
======================================
After detrending the K1 scalar (prime-count proximity) from all 210
cross-domain concept links, what is the rank of the residual matrix?
Low rank = prime count explains most structure.
High rank = there is genuine cross-domain signal beyond primes.
"""
import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
LINKS = V2.parents[3] / "cartography" / "convergence" / "data" / "detrended_links.jsonl"
OUT = V2 / "m33_prime_atmosphere_results.json"

def main():
    t0 = time.time()
    print("=== M33: Prime atmosphere residual rank ===\n")

    print("[1] Loading detrended links...")
    links = []
    with open(LINKS) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: links.append(json.loads(line))
            except: pass
    print(f"  {len(links)} links loaded")

    # Extract score fields
    sample = links[0] if links else {}
    print(f"  Fields: {list(sample.keys())[:15]}")

    # Build a matrix: rows = source domains, cols = target domains, values = link strength
    # First find unique domains
    sources = set()
    targets = set()
    for l in links:
        src = l.get("source", l.get("from", l.get("domain_a", "")))
        tgt = l.get("target", l.get("to", l.get("domain_b", "")))
        if src and tgt:
            sources.add(src); targets.add(tgt)

    all_domains = sorted(sources | targets)
    n = len(all_domains)
    print(f"  Unique domains: {n}")

    if n == 0:
        # Try alternative structure
        print("  Trying alternative link structure...")
        # Maybe it's concept-level, not domain-level
        concepts = set()
        for l in links:
            for k in ["concept_a", "concept_b", "source_concept", "target_concept"]:
                if k in l: concepts.add(l[k])
        print(f"  Unique concepts: {len(concepts)}")
        if len(concepts) > 200:
            concepts = sorted(concepts)[:200]  # Cap for performance
        n = len(concepts)
        all_domains = sorted(concepts) if concepts else []

    if n < 3:
        print("  Not enough structure for matrix analysis")
        output = {
            "probe": "M33", "title": "Prime atmosphere residual rank",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(time.time() - t0, 1),
            "n_links": len(links),
            "assessment": "BLOCKED: link structure could not be parsed into domain matrix",
        }
        with open(OUT, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nASSESSMENT: {output['assessment']}")
        return

    # Build adjacency matrix
    dom_idx = {d: i for i, d in enumerate(all_domains)}
    M = np.zeros((n, n))
    score_key = None
    for k in ["score", "strength", "weight", "detrended_score", "residual", "value"]:
        if k in sample:
            score_key = k; break

    if score_key is None:
        # Use count
        for l in links:
            src = l.get("source", l.get("from", l.get("domain_a", l.get("concept_a", ""))))
            tgt = l.get("target", l.get("to", l.get("domain_b", l.get("concept_b", ""))))
            if src in dom_idx and tgt in dom_idx:
                M[dom_idx[src], dom_idx[tgt]] += 1
                M[dom_idx[tgt], dom_idx[src]] += 1
    else:
        for l in links:
            src = l.get("source", l.get("from", l.get("domain_a", l.get("concept_a", ""))))
            tgt = l.get("target", l.get("to", l.get("domain_b", l.get("concept_b", ""))))
            val = l.get(score_key, 0)
            if src in dom_idx and tgt in dom_idx and isinstance(val, (int, float)):
                M[dom_idx[src], dom_idx[tgt]] = val
                M[dom_idx[tgt], dom_idx[src]] = val

    print(f"\n[2] Matrix shape: {M.shape}, non-zero entries: {np.count_nonzero(M)}")
    print(f"  Score field used: {score_key or 'count'}")

    # SVD
    print("\n[3] Computing SVD...")
    U, S, Vt = np.linalg.svd(M)
    total_var = np.sum(S**2)
    cum_var = np.cumsum(S**2) / total_var

    # Effective rank (number of singular values needed for 90% variance)
    rank_90 = int(np.searchsorted(cum_var, 0.90) + 1)
    rank_95 = int(np.searchsorted(cum_var, 0.95) + 1)
    rank_99 = int(np.searchsorted(cum_var, 0.99) + 1)

    print(f"  Top 10 singular values: {[round(float(s), 2) for s in S[:10]]}")
    print(f"  Rank for 90% variance: {rank_90}/{n}")
    print(f"  Rank for 95% variance: {rank_95}/{n}")
    print(f"  Rank for 99% variance: {rank_99}/{n}")

    # Spectral gap
    spectral_gap = float(S[0] / S[1]) if len(S) > 1 and S[1] > 0 else float('inf')
    print(f"  Spectral gap (σ₁/σ₂): {spectral_gap:.2f}")

    elapsed = time.time() - t0
    output = {
        "probe": "M33", "title": "Prime atmosphere residual rank",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "n_links": len(links),
        "n_domains": n,
        "matrix_nonzero": int(np.count_nonzero(M)),
        "singular_values_top10": [round(float(s), 4) for s in S[:10]],
        "cumulative_variance_90": rank_90,
        "cumulative_variance_95": rank_95,
        "cumulative_variance_99": rank_99,
        "spectral_gap": round(spectral_gap, 4),
        "full_rank": n,
        "assessment": None,
    }

    rank_ratio = rank_90 / n
    if rank_ratio < 0.1:
        output["assessment"] = f"LOW RANK: {rank_90}/{n} dimensions explain 90% — primes/K1 explain most structure"
    elif rank_ratio < 0.3:
        output["assessment"] = f"MODERATE RANK: {rank_90}/{n} — some genuine cross-domain signal beyond K1"
    else:
        output["assessment"] = f"HIGH RANK: {rank_90}/{n} — residual matrix is near-full-rank, rich structure beyond primes"

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
