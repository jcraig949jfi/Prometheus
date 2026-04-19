"""Re-auditor batch 2 — remaining 11 +1 cells.

Categorization based on feature semantics:

  THEOREM (NULL_BSWCD inapplicable — constant statistic, null_std=0):
    F001 x P020 (Modularity): a_p agreement = 100% by Wiles et al.
    F002 x P001, P024 (Mazur torsion): torsion in list of 15 by Mazur.
    F005 x P024 (High-Sha parity): BSD parity proven conditionally.

    For these: annotate as TAUTOLOGICAL; retain at +1 with note, do NOT
    promote. NULL_BSWCD degenerates on constant statistic.

  NEAR-IDENTITY (violates non-tautological admission gate):
    F028 x P001 (Szpiro * Faltings): both sides encode log|Disc|.
      Demote per feature_meta description.

  LITERATURE-DOWNGRADED:
    F042 x P020, P025 (CM disc=-27): per sessionC literature scan,
      F042 is Deuring non-maximal-order character-sum compression
      (known qualitative effect). Novel quantitative precision but
      no new structural claim. Demote to 0 (retain as documented,
      no longer +1).

  DEFERRED (need per-cell audit, not run this iteration):
    F014 x P040 (Lehmer / F1 permutation null)
    F043 x P020, P023 (BSD-Sha anticorrelation)
    F045 x P023 (isogeny-class murmuration)

    Retain at +1 with 'DEFERRED' annotation.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKER = "Harmonia_M2_sessionD_reauditor"
OUTDIR = Path("cartography/docs")
SIG_DIR = OUTDIR / "signatures"


def commit_short():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def build_sig(feature, projection, effect, z, n, description, verdict, category):
    commit = commit_short()
    null_spec = "NULL_BSWCD@v1[stratifier=conductor,n_bins=10,n_perms=300,seed=20260417]"
    sig = {
        "feature_id": f"{feature}@{commit}",
        "projection_ids": [f"{projection}@{commit}"],
        "null_spec": null_spec,
        "dataset_spec": "Q_EC@lmfdb.ec_curvedata",
        "n_samples": int(n),
        "effect_size": float(effect),
        "z_score": round(float(z), 2),
        "precision": {
            "effect_size": "4 sig figs",
            "z_score": "2 decimal places",
            "n_samples": "exact",
        },
        "commit": commit,
        "worker": WORKER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "category": category,
        "description": description,
    }
    h = json.dumps({k: sig[k] for k in sorted(sig)}, sort_keys=True, default=str)
    sig["reproducibility_hash"] = hashlib.sha256(h.encode()).hexdigest()
    return sig


def main():
    SIG_DIR.mkdir(parents=True, exist_ok=True)
    records = [
        # Theorems (retain at +1, not durable via block-shuffle)
        ("F001", "P020", 1.0, 0.0, 3800000,
         "Modularity: a_p(EC)=a_p(MF) 100%. Wiles et al. NULL_BSWCD degenerate (constant stat).",
         "DEGENERATE", "THEOREM"),
        ("F002", "P001", 1.0, 0.0, 3800000,
         "Mazur: torsion in list of 15, 100%. NULL_BSWCD degenerate (constant stat).",
         "DEGENERATE", "THEOREM"),
        ("F002", "P024", 1.0, 0.0, 3800000,
         "Mazur torsion × torsion stratification: tautological pairing. NULL_BSWCD degenerate.",
         "DEGENERATE", "THEOREM"),
        ("F005", "P024", 1.0, 0.0, 230000,
         "(-1)^rank = root_number among sha≤9. BSD parity. NULL_BSWCD degenerate.",
         "DEGENERATE", "THEOREM"),
        # Near-identity (demote)
        ("F028", "P001", 0.97, None, 3800000,
         "F028 Szpiro×Faltings ρ=0.97: both encode log|Disc|. Near-identity, not cross-domain. "
         "Violates non-tautological admission gate.",
         "TAUTOLOGICAL", "NEAR_IDENTITY"),
        # Literature-downgraded (demote to 0)
        ("F042", "P020", 6.66, None, 5500,
         "F042 CM disc=-27 L-depression 6.66x: per sessionC literature scan (c9a7543a), this is "
         "Deuring non-maximal-order character-sum compression (Gross LNM). Known qualitative effect, "
         "no novel structure. Downgraded 2026-04-18.",
         "LITERATURE_DOWNGRADED", "DOWNGRADED"),
        ("F042", "P025", 6.66, None, 5500,
         "Same F042 CM-disc-27 effect under CM-vs-non-CM projection. Literature-downgraded.",
         "LITERATURE_DOWNGRADED", "DOWNGRADED"),
        # Deferred (need real audit)
        ("F014", "P040", None, None, 81000,
         "Lehmer spectrum × F1 permutation null: needs Mahler-measure-table audit. Not run this iteration.",
         "DEFERRED", "DEFERRED"),
        ("F043", "P020", -0.520, None, 200000,
         "F043 BSD-Sha anticorrelation with period: corr(log Sha, log A)=-0.520 at rank-0 "
         "decade [1e5,1e6). U_D 2026-04-18 (111d6288). Per-cell block-shuffle audit deferred.",
         "DEFERRED", "DEFERRED"),
        ("F043", "P023", -0.520, None, 200000,
         "F043 under rank stratification: anchor is rank-0 decade. Cross-rank differentiation not "
         "yet audited. Deferred.",
         "DEFERRED", "DEFERRED"),
        ("F045", "P023", 6.6, None, 3800000,
         "F045 isogeny-class murmuration: 5/21 primes, F=6.6 at p=79. Ergon 2026-04-18 (7e68116c). "
         "Per-cell block-shuffle audit deferred.",
         "DEFERRED", "DEFERRED"),
    ]

    diffs = {}
    for feature, p_id, effect, z, n, desc, verdict, cat in records:
        e = 0.0 if effect is None else float(effect)
        z_val = 0.0 if z is None else float(z)
        sig = build_sig(feature, p_id, e, z_val, n, desc, verdict, cat)
        path = SIG_DIR / f"SIG_{feature}_{p_id}.json"
        path.write_text(json.dumps(sig, indent=2, default=str), encoding="utf-8")
        # Verdict mapping: THEOREM stays +1, DEFERRED stays +1,
        # NEAR_IDENTITY/DOWNGRADED demote.
        if cat in ("THEOREM", "DEFERRED"):
            target = 1
        elif cat == "NEAR_IDENTITY":
            target = -1
        elif cat == "DOWNGRADED":
            target = 0
        else:
            target = 1
        diffs[f"{feature}:{p_id}"] = {
            "from": 1, "to": target,
            "category": cat, "verdict": verdict,
            "signature_path": str(path),
        }
        print(f"  {feature}:{p_id}: {cat} -> {target}")

    report = {
        "task": "reaudit_batch_remaining",
        "worker": WORKER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator": "NULL_BSWCD@v1",
        "diffs": diffs,
        "categories": {
            "THEOREM": "Known theorem; NULL_BSWCD degenerate; retain at +1 with annotation.",
            "NEAR_IDENTITY": "Fails non-tautological admission gate; demote.",
            "DOWNGRADED": "Literature correspondence demotes to 0 (retain as documented).",
            "DEFERRED": "Needs proper per-cell audit; retain at +1 with DEFERRED flag.",
        },
    }
    out = OUTDIR / "reaudit_batch_remaining_results.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n[reaudit_batch_remaining] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
