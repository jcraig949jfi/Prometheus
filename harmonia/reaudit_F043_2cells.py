"""Re-auditor — F043 x P020, P023 under NULL_BSWCD@v1.

F043 = BSD-Sha anticorrelation with period. Claim: corr(log Sha, log A)
= -0.520 at rank 0 decade [1e5, 1e6), where A := Omega_real * prod_p c_p
(inverted from BSD formula as L * tors^2 / Sha, since we lack Omega_real
and c_p directly).

Test: run NULL_BSWCD@v1 with conductor decile stratifier, statistic =
Pearson corr(log Sha, log A). If block-shuffle destroys the anti-
correlation (observed -0.52 → null ~0), the signal is real within-decile
structure. If the null also hits ~ -0.52, the correlation is driven by
between-decile drift (conductor-mediated).

Cells: F043 x P020 (conductor) and F043 x P023 (rank stratification).
Both stratified on rank-0 only; P023 cell is vacuous for rank subset
but we can still test conductor-stability of the claimed signal.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from harmonia.nulls import bswcd_null, bswcd_signature  # noqa: E402

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
PG_FIRE = dict(PG, dbname="prometheus_fire")

DECADE_LO, DECADE_HI = 100_000, 1_000_000
N_PERMS = 300
SEED = 20260417
N_BINS = 10
WORKER = "Harmonia_M2_sessionD_reauditor"
OUTDIR = Path("cartography/docs")
SIG_DIR = OUTDIR / "signatures"


def fetch():
    # rank-0 L values in decade
    lt_by_label = {}
    with psycopg2.connect(**PG_FIRE) as c:
        cur = c.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
              FROM zeros.object_zeros
             WHERE object_type='elliptic_curve'
               AND analytic_rank = 0
               AND conductor >= %s AND conductor < %s
               AND leading_term IS NOT NULL
               AND leading_term > 0
        """, (DECADE_LO, DECADE_HI))
        for lbl, cond, lt in cur.fetchall():
            lt_by_label[lbl] = (int(cond), float(lt))
    labels = list(lt_by_label.keys())
    print(f"[fetch] {len(labels)} rank-0 curves in decade [{DECADE_LO},{DECADE_HI})")

    # arithmetic fields via temp table join
    arith = {}
    with psycopg2.connect(**PG) as c:
        cur = c.cursor()
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS _tmp_labels(lmfdb_label text PRIMARY KEY)")
        cur.execute("TRUNCATE _tmp_labels")
        chunk = 5000
        for i in range(0, len(labels), chunk):
            execute_values(
                cur,
                "INSERT INTO _tmp_labels VALUES %s ON CONFLICT DO NOTHING",
                [(l,) for l in labels[i:i+chunk]],
                page_size=2000,
            )
        cur.execute("""
            SELECT lmfdb_label,
                   NULLIF(torsion,'')::int AS torsion,
                   NULLIF(sha,'')::int AS sha
              FROM public.ec_curvedata
             WHERE lmfdb_label IN (SELECT lmfdb_label FROM _tmp_labels)
        """)
        for lbl, tors, sha in cur.fetchall():
            if tors is None or sha is None or tors <= 0 or sha <= 0:
                continue
            arith[lbl] = (int(tors), int(sha))

    rows = []
    for lbl, (cond, lt) in lt_by_label.items():
        if lbl not in arith:
            continue
        tors, sha = arith[lbl]
        A = lt * tors * tors / sha  # inverted BSD geometric factor
        if A <= 0:
            continue
        rows.append({
            "lmfdb_label": lbl, "conductor": float(cond),
            "leading_term": lt, "torsion": tors, "sha": sha,
            "log_A": float(np.log(A)), "log_sha": float(np.log(sha)),
        })
    df = pd.DataFrame(rows)
    return df


def corr_logsha_logA(df):
    if len(df) < 100:
        return 0.0
    return float(np.corrcoef(df["log_sha"].values, df["log_A"].values)[0, 1])


def commit_short():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def main():
    SIG_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[reaudit_F043] start {started}")
    df = fetch()
    print(f"[data] n={len(df)} rows with A > 0")
    print(f"  sha distribution: {df['sha'].value_counts().sort_index().head(10).to_dict()}")

    # Statistic: corr(log sha, log A). Shuffle the log_A within conductor deciles.
    # (Shuffling log_sha would produce the same Pearson under random relabeling,
    # but log_A is the 'response' in the observed claim, so shuffle that.)
    df["value"] = df["log_A"]

    def stat(d):
        if len(d) < 100:
            return 0.0
        return float(np.corrcoef(d["log_sha"].values, d["value"].values)[0, 1])

    observed = stat(df)
    print(f"[observed] corr(log sha, log A) = {observed:+.4f}")

    # F043 x P020 — full conductor block-shuffle
    print("\n[F043 x P020] block-shuffle within conductor decile")
    r1 = bswcd_null(df, stratifier="conductor",
                    n_bins=N_BINS, n_perms=N_PERMS, seed=SEED,
                    statistic=stat, shuffle_col="value")
    print(f"  z={r1['z_score']:.2f} verdict={r1['verdict']} "
          f"observed={r1['observed']:+.4f} null_mean={r1['null_mean']:+.4f} "
          f"null_std={r1['null_std']:.4f}")

    # F043 x P023 — rank stratification is degenerate (rank=0 only subset)
    # Test: does the anticorrelation persist across conductor subsets
    # (say, decile halves)? Equivalent to a broader-grain conductor stratum.
    # Alternative: check consistency per-bin.
    print("\n[F043 x P023] rank-0 subset only → conductor-halves cross-check")
    df_low = df[df["conductor"] < 500_000].copy()
    df_high = df[df["conductor"] >= 500_000].copy()
    c_low = float(np.corrcoef(df_low["log_sha"].values, df_low["log_A"].values)[0, 1]) if len(df_low) > 100 else 0
    c_high = float(np.corrcoef(df_high["log_sha"].values, df_high["log_A"].values)[0, 1]) if len(df_high) > 100 else 0
    print(f"  low-half conductor corr: {c_low:+.4f}  (n={len(df_low)})")
    print(f"  high-half conductor corr: {c_high:+.4f}  (n={len(df_high)})")

    # For the P023 cell judgment: F043 is rank-0-defined; rank-stratification
    # is vacuous. Inherit the P020 verdict (same mechanism).
    commit = commit_short()
    sig1 = bswcd_signature(
        feature_id=f"F043@{commit}",
        projection_ids=[f"P020@{commit}"],
        result=r1,
        n_samples=len(df),
        dataset_spec=f"EC rank-0 conductor in [{DECADE_LO},{DECADE_HI})",
        commit=commit, worker=WORKER,
        timestamp=datetime.now(timezone.utc).isoformat(),
        effect_size=observed,
    )
    (SIG_DIR / "SIG_F043_P020.json").write_text(json.dumps(sig1, indent=2, default=str), encoding="utf-8")

    sig2 = {
        "feature_id": f"F043@{commit}",
        "projection_ids": [f"P023@{commit}"],
        "null_spec": f"NULL_BSWCD@v1[stratifier=conductor,n_bins={N_BINS},n_perms={N_PERMS},seed={SEED}]",
        "dataset_spec": f"EC rank-0 conductor in [{DECADE_LO},{DECADE_HI})",
        "n_samples": int(len(df)),
        "effect_size": float(observed),
        "z_score": round(float(r1["z_score"]), 2),
        "precision": {"effect_size": "4 sig figs", "z_score": "2 decimal places", "n_samples": "exact"},
        "commit": commit, "worker": WORKER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": r1["verdict"],
        "description": (
            "F043 is rank-0-defined; P023 (rank stratification) is vacuous for "
            "this feature. Verdict inherits from F043 x P020 block-shuffle. "
            f"Consistency across conductor halves: low={c_low:+.4f}, high={c_high:+.4f}."
        ),
        "consistency_checks": {"corr_low_half": c_low, "corr_high_half": c_high},
    }
    h = json.dumps({k: sig2[k] for k in sorted(sig2)}, sort_keys=True, default=str)
    sig2["reproducibility_hash"] = hashlib.sha256(h.encode()).hexdigest()
    (SIG_DIR / "SIG_F043_P023.json").write_text(json.dumps(sig2, indent=2, default=str), encoding="utf-8")

    verdict_target = 2 if r1["verdict"] == "DURABLE" else -1
    report = {
        "task": "reaudit_F043_2cells",
        "worker": WORKER,
        "operator": "NULL_BSWCD@v1",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "n_samples": len(df),
        "observed_corr": observed,
        "bswcd_result": r1,
        "consistency": {"low_half": c_low, "high_half": c_high},
        "tensor_diff": {
            "F043:P020": {"from": 1, "to": verdict_target, "z_block": r1["z_score"], "verdict": r1["verdict"]},
            "F043:P023": {"from": 1, "to": verdict_target, "z_block": r1["z_score"], "verdict": r1["verdict"],
                          "note": "rank-stratification vacuous; inherits P020 verdict"},
        },
    }
    out = OUTDIR / "reaudit_F043_2cells_results.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n[reaudit_F043] wrote {out}")
    print(f"\n=== SUMMARY ===")
    print(f"  F043:P020: z={r1['z_score']:+.2f} -> {r1['verdict']} -> {verdict_target}")
    print(f"  F043:P023: (vacuous, inherits P020) -> {verdict_target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
