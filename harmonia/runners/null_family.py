"""gen_02 executor: null-family SIGNATURE@v2 builder.

Given a (feature_id, projection_ids, dataset_spec, claim_class) tuple,
dispatches every applicable null from the promoted family, collects
z-scores, computes `family_verdict` and `discordance_flag`, returns a
SIGNATURE@v2 record.

This is a TIER-1 SCAFFOLD. It does NOT recompute observed statistics
from scratch — the per-cell statistic function is supplied by the
caller (or, for re-audit tasks, encoded in the task payload's
`statistic_hint`). A full fleshing-out requires the sampling of per-
claim statistics from the live dataset; for the smoke test we drive
with a synthetic DataFrame.

Usage:
    from harmonia.runners.null_family import run_family, smoke_test
    smoke_test()  # F011:P020 with synthetic data

Spec: docs/prompts/gen_02_null_family.md
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Callable, Optional

import numpy as np
import pandas as pd

os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")

from harmonia.nulls.block_shuffle import bswcd_null
from harmonia.nulls.plain import plain_null
from harmonia.nulls.bootstrap import boot_null
from harmonia.nulls.frame import frame_null  # noqa: F401 — scaffold
from harmonia.nulls.model import model_null  # noqa: F401 — scaffold


# ---------------------------------------------------------------------------
# Applicability table — mirrors null_protocol_v1.md
# ---------------------------------------------------------------------------

CLAIM_CLASS_APPLICABILITY = {
    1: {"NULL_PLAIN": True,  "NULL_BSWCD": True,  "NULL_BOOT": True,
        "NULL_FRAME": False, "NULL_MODEL": "sometimes"},
    2: {"NULL_PLAIN": True,  "NULL_BSWCD": True,  "NULL_BOOT": True,
        "NULL_FRAME": False, "NULL_MODEL": "rarely"},
    3: {"NULL_PLAIN": True,  "NULL_BSWCD": True,  "NULL_BOOT": True,
        "NULL_FRAME": False, "NULL_MODEL": "rarely"},
    4: {"NULL_PLAIN": False, "NULL_BSWCD": False, "NULL_BOOT": False,
        "NULL_FRAME": True,  "NULL_MODEL": "sometimes"},
    5: {"NULL_PLAIN": False, "NULL_BSWCD": False, "NULL_BOOT": False,
        "NULL_FRAME": False, "NULL_MODEL": False},
}

NA_REASON = {
    1: {"NULL_FRAME": "not_class_4"},
    2: {"NULL_FRAME": "not_class_4"},
    3: {"NULL_FRAME": "not_class_4"},
    4: {"NULL_PLAIN": "sample_not_representative",
        "NULL_BSWCD": "shuffle_preserves_construction_bias",
        "NULL_BOOT":  "resample_preserves_construction_bias"},
    5: {"NULL_PLAIN": "algebraic_identity_refuses_null",
        "NULL_BSWCD": "algebraic_identity_refuses_null",
        "NULL_BOOT":  "algebraic_identity_refuses_null",
        "NULL_FRAME": "algebraic_identity_refuses_null",
        "NULL_MODEL": "algebraic_identity_refuses_null"},
}


# ---------------------------------------------------------------------------
# Family dispatch
# ---------------------------------------------------------------------------

def run_family(
    data: pd.DataFrame,
    claim_class: int,
    stratifier: str = "conductor",
    statistic: Optional[Callable] = None,
    shuffle_col: str = "value",
    n_perms: int = 300,
    n_boot: int = 1000,
    model: Optional[str] = None,
    model_params: Optional[dict] = None,
    model_sampler: Optional[Callable] = None,
    observed_for_model: Optional[float] = None,
    frame: Optional[str] = None,
    frame_resampler: Optional[Callable] = None,
    seeds: Optional[dict] = None,
) -> list[dict]:
    """Run every applicable null for the given claim class. Returns the
    `null_family_result` list (SIGNATURE@v2 schema)."""
    if claim_class not in CLAIM_CLASS_APPLICABILITY:
        raise ValueError(f"claim_class must be in {list(CLAIM_CLASS_APPLICABILITY)}, got {claim_class}")

    app = CLAIM_CLASS_APPLICABILITY[claim_class]
    na = NA_REASON.get(claim_class, {})
    seeds = seeds or {}
    results = []

    # --- NULL_PLAIN ---
    if app["NULL_PLAIN"] is True:
        seed = seeds.get("NULL_PLAIN", 20260420)
        r = plain_null(data=data, n_perms=n_perms, seed=seed,
                       statistic=statistic, shuffle_col=shuffle_col)
        results.append({
            "null": f"NULL_PLAIN@v1[n_perms={n_perms},seed={seed}]",
            "z_score": r["z_score"], "applicability": "applies",
            "raw": r,
        })
    else:
        results.append({
            "null": "NULL_PLAIN@v1", "z_score": None,
            "reason": na.get("NULL_PLAIN", "not_applicable"),
            "applicability": "n_a",
        })

    # --- NULL_BSWCD ---
    if app["NULL_BSWCD"] is True:
        seed = seeds.get("NULL_BSWCD", 20260417)
        r = bswcd_null(data=data, stratifier=stratifier, n_perms=n_perms,
                       seed=seed, statistic=statistic, shuffle_col=shuffle_col)
        results.append({
            "null": f"NULL_BSWCD@v2[stratifier={stratifier},n_perms={n_perms},seed={seed}]",
            "z_score": r["z_score"], "applicability": "applies",
            "raw": r,
        })
    else:
        results.append({
            "null": "NULL_BSWCD@v2", "z_score": None,
            "reason": na.get("NULL_BSWCD", "not_applicable"),
            "applicability": "n_a",
        })

    # --- NULL_BOOT ---
    if app["NULL_BOOT"] is True:
        seed = seeds.get("NULL_BOOT", 20260420)
        r = boot_null(data=data, stratifier=stratifier, n_boot=n_boot,
                      seed=seed, statistic=statistic)
        results.append({
            "null": f"NULL_BOOT@v1[stratifier={stratifier},n_boot={n_boot},seed={seed}]",
            "z_score": r["z_score"], "applicability": "applies",
            "raw": r,
        })
    else:
        results.append({
            "null": "NULL_BOOT@v1", "z_score": None,
            "reason": na.get("NULL_BOOT", "not_applicable"),
            "applicability": "n_a",
        })

    # --- NULL_FRAME ---
    if app["NULL_FRAME"] is True and frame and frame_resampler:
        seed = seeds.get("NULL_FRAME", 20260420)
        r = frame_null(data=data, frame=frame, resampler=frame_resampler,
                       n_perms=n_perms, seed=seed, statistic=statistic)
        results.append({
            "null": f"NULL_FRAME@v1[frame={frame},n_perms={n_perms},seed={seed}]",
            "z_score": r["z_score"], "applicability": "applies",
            "raw": r,
        })
    else:
        reason = na.get("NULL_FRAME", "not_class_4")
        if app["NULL_FRAME"] is True and (not frame or not frame_resampler):
            reason = "frame_spec_required_but_not_supplied"
        results.append({
            "null": "NULL_FRAME@v1", "z_score": None,
            "reason": reason, "applicability": "n_a",
        })

    # --- NULL_MODEL ---
    if app["NULL_MODEL"] in (True, "sometimes") and model and model_sampler and observed_for_model is not None:
        seed = seeds.get("NULL_MODEL", 20260420)
        r = model_null(observed_statistic=observed_for_model, model=model,
                       model_params=model_params or {}, n_samples=10000,
                       seed=seed, statistic_sampler=model_sampler)
        results.append({
            "null": f"NULL_MODEL@v1[model={model},n_samples=10000,seed={seed}]",
            "z_score": r["z_score"], "applicability": "applies",
            "raw": r,
            "semantics": "observed rejects model — signal OR model-mismatch",
        })
    else:
        reason = na.get("NULL_MODEL", "no_model_claim")
        if app["NULL_MODEL"] in (True, "sometimes", "rarely") and not model:
            reason = "no_model_specified"
        results.append({
            "null": "NULL_MODEL@v1", "z_score": None,
            "reason": reason, "applicability": "n_a",
        })

    return results


# ---------------------------------------------------------------------------
# SIGNATURE@v2 builder
# ---------------------------------------------------------------------------

def compute_family_verdict(family_result: list[dict]) -> tuple[str, bool]:
    """Return (family_verdict, discordance_flag)."""
    applicable = [e for e in family_result if e.get("applicability") == "applies"]
    if not applicable:
        return "no_applicable_nulls", False
    zs = [e["z_score"] for e in applicable if e.get("z_score") is not None]
    if not zs:
        return "no_z_scores_computed", False
    passed = sum(1 for z in zs if abs(z) >= 3.0)
    verdict = f"{passed}/{len(applicable)} applicable nulls at z >= 3"

    # Discordance: sign flip or >10x spread in |z|
    signs = {(1 if z > 0 else (-1 if z < 0 else 0)) for z in zs}
    sign_flip = (1 in signs and -1 in signs)
    abs_zs = [abs(z) for z in zs if abs(z) > 0]
    spread_flag = False
    if len(abs_zs) >= 2:
        spread_flag = (max(abs_zs) / max(min(abs_zs), 1e-12)) > 10.0

    # Don't call NULL_MODEL sign-flip discordance: negative z there is
    # legitimate "rejects-model" semantics, not a Pattern 21 trigger.
    has_model_entry = any("NULL_MODEL" in e["null"] for e in applicable)
    if has_model_entry and sign_flip:
        # Check if the ONLY negative-z is a NULL_MODEL entry
        non_model_signs = {
            (1 if e["z_score"] > 0 else (-1 if e["z_score"] < 0 else 0))
            for e in applicable
            if "NULL_MODEL" not in e["null"] and e.get("z_score") is not None
        }
        if not (1 in non_model_signs and -1 in non_model_signs):
            sign_flip = False

    return verdict, (sign_flip or spread_flag)


def build_signature_v2(
    feature_id: str,
    projection_ids: list[str],
    claim_class: int,
    dataset_spec: str,
    n_samples: int,
    effect_size: float,
    family_result: list[dict],
    worker: str,
    commit: str = "pending",
    timestamp: Optional[str] = None,
) -> dict:
    """Assemble a SIGNATURE@v2 record with reproducibility hash."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    verdict, disc = compute_family_verdict(family_result)

    # Strip `raw` before hashing — it's debug-only.
    family_for_hash = [
        {k: v for k, v in e.items() if k != "raw"} for e in family_result
    ]

    sig = {
        "feature_id": feature_id,
        "projection_ids": list(projection_ids),
        "claim_class": int(claim_class),
        "null_family_result": family_for_hash,
        "family_verdict": verdict,
        "discordance_flag": bool(disc),
        "dataset_spec": dataset_spec,
        "n_samples": int(n_samples),
        "effect_size": float(effect_size),
        "precision_map": {
            "effect_size": "4 sig figs",
            "z_score": "2 decimal places",
            "n_samples": "exact",
        },
        "commit": commit,
        "worker": worker,
        "timestamp": timestamp,
    }
    hashable = json.dumps(
        {k: sig[k] for k in sorted(sig) if k != "reproducibility_hash"},
        sort_keys=True, default=str,
    )
    sig["reproducibility_hash"] = hashlib.sha256(hashable.encode()).hexdigest()
    # Re-attach raws for debugging but not hashed
    sig["null_family_result_raw"] = family_result
    return sig


def migrate_v1_to_v2(v1_sig: dict) -> dict:
    """Wrap a SIGNATURE@v1 record into SIGNATURE@v2 with partial family."""
    family = [{
        "null": v1_sig.get("null_spec", "unknown@v?"),
        "z_score": v1_sig.get("z_score"),
        "applicability": "applies",
        "reason": "migrated_from_v1",
    }]
    for sym in ("NULL_PLAIN@v1", "NULL_BOOT@v1", "NULL_FRAME@v1", "NULL_MODEL@v1"):
        if sym.split("@")[0] not in v1_sig.get("null_spec", ""):
            family.append({"null": sym, "z_score": None,
                           "applicability": "n_a",
                           "reason": "migrated_from_v1_not_rerun"})
    return build_signature_v2(
        feature_id=v1_sig["feature_id"],
        projection_ids=v1_sig.get("projection_ids", []),
        claim_class=v1_sig.get("claim_class", 1),
        dataset_spec=v1_sig.get("dataset_spec", "unknown"),
        n_samples=v1_sig.get("n_samples", 0),
        effect_size=v1_sig.get("effect_size", 0.0),
        family_result=family,
        worker=v1_sig.get("worker", "unknown"),
        commit=v1_sig.get("commit", "pending"),
        timestamp=v1_sig.get("timestamp"),
    )


# ---------------------------------------------------------------------------
# Smoke test — F011:P020 with synthetic data
# ---------------------------------------------------------------------------

def _synthetic_f011_data(seed: int = 20260420, n: int = 2000) -> pd.DataFrame:
    """Tiny synthetic dataset that mimics F011-style per-curve statistics.
    conductor and value are coupled so stratified nulls detect signal."""
    rng = np.random.default_rng(seed)
    conductor = rng.uniform(1e5, 1e6, size=n)
    # Construct `value` with a genuine within-decile trend: magnitude
    # depends on conductor-decile so NULL_BSWCD will see structure.
    decile_effect = (conductor - 5e5) / 5e5  # [-1, 1]
    noise = rng.normal(0, 0.5, size=n)
    value = 0.3 * decile_effect + noise
    return pd.DataFrame({"conductor": conductor, "value": value})


def smoke_test() -> dict:
    """Run the family on F011:P020-style synthetic data. Used by the
    acceptance criterion: 'runner runs on smoke test'."""
    df = _synthetic_f011_data()
    # Statistic: regression slope of value vs conductor.
    def slope(data: pd.DataFrame) -> float:
        c = data["conductor"].values
        v = data["value"].values
        c_ = c - np.mean(c)
        v_ = v - np.mean(v)
        denom = float(np.sum(c_ * c_))
        if denom == 0:
            return 0.0
        return float(np.sum(c_ * v_) / denom)

    observed = slope(df)

    family = run_family(
        data=df, claim_class=1,
        stratifier="conductor", statistic=slope,
        n_perms=100,  # smoke test: keep it fast
        n_boot=200,
        seeds={"NULL_PLAIN": 20260420, "NULL_BSWCD": 20260417,
               "NULL_BOOT": 20260420},
    )

    sig = build_signature_v2(
        feature_id="F011@smoke",
        projection_ids=["P020@smoke"],
        claim_class=1,
        dataset_spec="synthetic_smoke@v1",
        n_samples=len(df),
        effect_size=observed,
        family_result=family,
        worker="Harmonia_M2_sessionA",
        commit="smoke",
    )

    return sig


if __name__ == "__main__":
    import sys
    sig = smoke_test()
    print("SIGNATURE@v2 smoke test (F011:P020 synthetic):")
    print("  feature_id       :", sig["feature_id"])
    print("  claim_class      :", sig["claim_class"])
    print("  family_verdict   :", sig["family_verdict"])
    print("  discordance_flag :", sig["discordance_flag"])
    print("  effect_size      :", round(sig["effect_size"], 6))
    print("  null_family_result:")
    for e in sig["null_family_result"]:
        z = e.get("z_score")
        if z is None:
            print(f"    {e['null']:62s}  n/a  ({e.get('reason','')})")
        else:
            print(f"    {e['null']:62s}  z={z}")
    print("  reproducibility_hash:", sig["reproducibility_hash"][:24], "...")
