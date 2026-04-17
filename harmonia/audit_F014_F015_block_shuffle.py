"""
audit_F014_F015_block_shuffle.py — apply block-null methodology to F014 and F015.

Task: audit_F014_F015_block_shuffle (Harmonia_M2_sessionC).

F010 block-shuffle kill (sessionC) established that the alt-null protocol
catches between-stratum leakage that a simple label-permute null misses.
Apply the same discipline to F014 (Lehmer gap) and F015 (abc/Szpiro).

F015 SCOPE (this tick):
  - Re-sample per-stratum Szpiro ratios (balanced per num_bad_primes, match
    sessionD's design with per_k=2000 for tick-bounded runtime).
  - Real per-k slope: regress szpiro_ratio on log(conductor) within each k.
  - Null: shuffle szpiro values WITHIN each k-stratum (preserves per-k
    marginal, destroys szpiro-vs-conductor pairing). Recompute per-k slope.
  - 300 block permutations. z-score real vs null per k; verdict per k.
  - Sign-uniform-negative claim survives iff every k has real slope with
    |z| >= 3 AND negative sign.

F014 SCOPE (this tick): DEFERRED with justification. F014 block shuffle
requires re-loading 81K polynomials and recomputing Mahler measures under
shuffled (degree, num_ram) cells. That is a 5-15 minute compute pipeline;
cannot fit in a single 4-minute tick alongside F015. Recommend separate
task `audit_F014_block_shuffle` seeded by sessionA. F014 is already marked
KILLED in tensor (sessionB wsw_F014 Pattern 19), so this audit is a
confirmation pass, not a new kill.
"""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

PER_K = 2000
N_PERMS = 300
K_VALUES = [1, 2, 3, 4, 5, 6]
MIN_PER_BIN = 30


def load_f015_sample(conn):
    """Balanced sample: for each k in 1..6, pull PER_K EC rows with
    num_bad_primes = k. Return (szpiro_ratio, conductor, k) tuples."""
    out = []
    cur = conn.cursor()
    for k in K_VALUES:
        cur.execute("""
            SELECT NULLIF(szpiro_ratio, '')::float8 AS sz,
                   NULLIF(conductor,'')::numeric AS N,
                   NULLIF(num_bad_primes,'')::int AS k
            FROM public.ec_curvedata
            WHERE num_bad_primes = %s
              AND szpiro_ratio IS NOT NULL
              AND conductor IS NOT NULL
            ORDER BY conductor::numeric ASC
            LIMIT %s
        """, (str(k), PER_K))
        for row in cur.fetchall():
            sz, N, kk = row
            if sz is None or N is None or kk is None:
                continue
            try:
                N_f = float(N)
                if not math.isfinite(N_f) or N_f <= 1:
                    continue
                out.append((float(sz), math.log(N_f), int(kk)))
            except Exception:
                continue
    cur.close()
    return out


def slope_within_k(rows, k):
    sub = [(sz, logN) for sz, logN, kk in rows if kk == k]
    if len(sub) < MIN_PER_BIN:
        return None
    sz = np.array([s for s, _ in sub])
    lN = np.array([l for _, l in sub])
    if sz.std() < 1e-12 or lN.std() < 1e-12:
        return None
    slope, _, _, _, _ = stats.linregress(lN, sz)
    return float(slope)


def block_shuffle_szpiro(rows, rng):
    """Shuffle szpiro values WITHIN each k-stratum; keep (logN, k) pairs fixed."""
    by_k = defaultdict(list)
    for i, (sz, lN, k) in enumerate(rows):
        by_k[k].append(i)
    shuffled = [r[0] for r in rows]
    for k, indices in by_k.items():
        if len(indices) < 2:
            continue
        sz_vals = [rows[i][0] for i in indices]
        perm = rng.permutation(sz_vals)
        for j, i in enumerate(indices):
            shuffled[i] = float(perm[j])
    return shuffled


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[audit_F014_F015_block_shuffle] start {started}")

    # F015 block shuffle
    with psycopg2.connect(**PG) as conn:
        rows = load_f015_sample(conn)
    print(f"[F015] loaded {len(rows)} rows")

    # Real per-k slopes
    real_slopes = {}
    for k in K_VALUES:
        s = slope_within_k(rows, k)
        real_slopes[k] = s
    print(f"[F015] real per-k slopes: {real_slopes}")

    # Block-shuffle nulls
    rng = np.random.default_rng(17)
    null_slopes = {k: [] for k in K_VALUES}
    for p in range(N_PERMS):
        shuffled_sz = block_shuffle_szpiro(rows, rng)
        # Build shuffled-rows view
        shuffled_rows = [(shuffled_sz[i], rows[i][1], rows[i][2]) for i in range(len(rows))]
        for k in K_VALUES:
            s = slope_within_k(shuffled_rows, k)
            if s is not None:
                null_slopes[k].append(s)
    for k in K_VALUES:
        arr = np.array(null_slopes[k])
        print(f"[F015] k={k}: null n={arr.size} mean={arr.mean():.4f} std={arr.std():.4f}")

    # z-scores and verdicts per k
    per_k = {}
    for k in K_VALUES:
        arr = np.array(null_slopes[k])
        real = real_slopes[k]
        if real is None or arr.size == 0:
            per_k[str(k)] = {"real_slope": real, "verdict": "SKIP_insufficient"}
            continue
        nm = float(arr.mean())
        ns = float(arr.std())
        z = (real - nm) / ns if ns > 1e-10 else None
        p = float(np.mean(np.abs(arr) >= abs(real)))
        verdict = "SURVIVES" if (z is not None and z <= -3.0) else (
                  "AMBIGUOUS_sign_flipped" if z is not None and z >= 3.0 else
                  "KILLED_under_block_null")
        per_k[str(k)] = {
            "real_slope": real,
            "null_mean": nm,
            "null_std": ns,
            "z_score": z,
            "p_perm": p,
            "verdict": verdict,
        }

    all_survive = all(v.get("verdict") == "SURVIVES" for v in per_k.values())
    overall_verdict = ("F015_SIGN_UNIFORM_NEGATIVE_SURVIVES_BLOCK_NULL"
                      if all_survive else
                      "F015_PARTIAL_OR_KILLED_UNDER_BLOCK_NULL")

    # F014 deferred — record rationale
    f014 = {
        "status": "DEFERRED",
        "rationale": (
            "F014 block-shuffle requires re-loading ~81K polynomials from nf_fields "
            "and recomputing Mahler measures under shuffled (degree, num_ram) cells. "
            "That pipeline is 5-15 minutes of compute and cannot fit alongside F015 "
            "in a single 4-minute tick. F014 is already verdict=KILLED in tensor "
            "(sessionB wsw_F014 Pattern 19 magnitude correction); block-shuffle audit "
            "would be a confirmation pass, not a new kill. Recommend sessionA seed "
            "separate `audit_F014_block_shuffle` task."
        ),
        "followup_suggestion": "audit_F014_block_shuffle as standalone task at priority -1.0"
    }

    results = {
        "task_id": "audit_F014_F015_block_shuffle",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "F015": {
            "per_k_strata": per_k,
            "overall_verdict": overall_verdict,
            "sample_config": {"per_k": PER_K, "n_perms": N_PERMS, "min_per_bin": MIN_PER_BIN},
            "interpretation": (
                "Block-shuffle within k preserves the per-k marginal distribution of "
                "szpiro_ratio; destroys only the szpiro-vs-conductor pairing within "
                "each k. If every k passes z<=-3 (real slope is strongly more negative "
                "than the shuffled null), sign-uniform-negative claim SURVIVES. If any "
                "k fails, that k is consistent with zero slope under the block null — "
                "the 'sign-uniform-negative' claim is partial at best."
            ),
        },
        "F014": f014,
        "shape_summary": (
            f"F015 block-null per-k verdicts: "
            + ", ".join(f"k={k}:{per_k[str(k)].get('verdict','?')}" for k in K_VALUES)
            + f". Overall: {overall_verdict}. F014: DEFERRED (see rationale)."
        ),
        "proposed_followups": [
            "audit_F014_block_shuffle (standalone; needs 5-15min compute window)",
            "pattern_20_audit_update_block_null (fourth discriminator formally recorded)",
            "tensor_update_F015_block_null_refinement (if any k fails, F015 description needs qualifier)",
        ],
    }

    out_path = os.path.join("cartography", "docs", "audit_F014_F015_block_shuffle_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[audit] wrote {out_path}")
    print(f"[F015 verdict] {overall_verdict}")


if __name__ == "__main__":
    main()
