"""Calibration v1 — second planted relation: EC torsion divides #E(F_p).

Tests whether the F2 framework from v0 (calibration_v0_murasugi.py)
generalizes to a SECOND known mathematical relation without re-tuning
the contrast threshold.

THE PLANTED RELATION:
  For an elliptic curve E and good prime p, the torsion order t(E)
  divides #E(F_p) = p + 1 - a_p(E). This is a consequence of the
  reduction map E(Q)_tors -> E(F_p) being injective for good p.

  Claim form:  torsion(E) divides (p + 1 - a_p(E))
  Holds always for good p.

WHY THIS IS A STRONGER TEST THAN MURASUGI:
  Murasugi was a within-object relation (same knot, two invariants).
  EC-torsion-divides is a within-object COUPLED relation: the
  relation depends on the COUPLING between t(E) and a_p(E) — break
  the coupling by permuting a_p across ECs, and the relation often
  fails (rate ~1/t per EC). For torsion=1 the relation is trivial;
  for torsion>=2 the test produces real F2 contrast.

  This means F2 must distinguish CASES WHERE COUPLING MATTERS from
  CASES WHERE IT DOESN'T — a more demanding generalization test.

============================================================
PRE-REGISTERED THRESHOLDS (locked before run)
============================================================
  F1 promote: training_weight >= 0.6
  F2 contrast: |obs_hold - null_hold| >= 0.10
  N per source: 500 records
  Null samples: 5000
  RNG seed: 20260530

  Restrict to ECs with torsion >= 2 to avoid the trivial-coupling
  case (torsion=1 means "1 divides anything" always — zero contrast
  expected).
"""
from __future__ import annotations

import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from theseus.config import BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord, ClaimKind, Verdict, StepRecord,
)
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog, _get_int, _evaluate_relation,
)
from theseus.scoring.training_weight import training_weight


N_PER_SOURCE = 500
F1_THRESHOLD = 0.6
F2_THRESHOLD = 0.10
NULL_SAMPLES = 5000
RNG_SEED = 20260530

# The first 20 primes — index aligns with a_p list in BSD-rich catalog.
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


SHARED_KIND = ClaimKind.BRIDGE_EXTENSION.value
SHARED_VERDICT = Verdict.SHADOW_CATALOG.value
SHARED_GENID = "calib_v1"
SHARED_STEP_TRACE = [
    StepRecord(
        step_id="step_0",
        step_kind="catalog_check",
        step_method="invariant_lookup",
        step_input={"calibration": True},
        step_output={"hold_observed": True},
        step_info_density=0.5,
        step_convergence="exact",
    ).to_dict()
]


def torsion(e) -> Optional[int]:
    return _get_int(e.get("rich") or {}, "torsion")


def ap_at(e, prime_idx: int) -> Optional[int]:
    ap_list = (e.get("base") or {}).get("a_p")
    if not isinstance(ap_list, list) or prime_idx >= len(ap_list):
        return None
    v = ap_list[prime_idx]
    if isinstance(v, int):
        return v
    return None


def is_good_prime(e, prime_idx: int) -> bool:
    """A prime is bad for E iff p | conductor(E)."""
    cond = _get_int(e.get("base") or {}, "conductor")
    if cond is None:
        return False
    p = PRIMES[prime_idx]
    return cond % p != 0


def ec_label(e) -> str:
    return (e.get("base") or {}).get("label") or (e.get("base") or {}).get("cremona_label") or "ec"


def build_record(
    source: str,
    e_label: str,
    t: int,
    prime: int,
    n_points: int,
    relation: str,
) -> TheseusRecord:
    canonical = (
        f"CALIB[{source}] torsion(ec:{e_label})={t} "
        f"{relation} #E(F_{prime})={n_points}"
    )
    payload = {
        "catalog_a": "ec",
        "object_a": e_label,
        "invariant_a": "torsion",
        "value_a_raw": t,
        "catalog_b": "ec",
        "object_b": e_label,
        "invariant_b": f"npoints_p{prime}",
        "value_b_raw": n_points,
        "relation": relation,
        "calibration_source": source,
        "prime": prime,
    }
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id(canonical, SHARED_GENID),
        generator_id=SHARED_GENID,
        batch_id="calib_v1",
        emitted_at=datetime.now(timezone.utc).isoformat(),
        claim_kind=SHARED_KIND,
        claim_payload=payload,
        canonical_claim_text=canonical,
        verdict=SHARED_VERDICT,
        kill_pattern=None,
        method="calibration",
        convergence_status="exact",
        step_trace=SHARED_STEP_TRACE,
    )


def gen_true_ec_torsion(ecs, rng, n: int) -> List[TheseusRecord]:
    """torsion(E) divides #E(F_p) for real (E, p) pairs with torsion >= 2."""
    nontrivial = [e for e in ecs if (torsion(e) or 1) >= 2]
    out = []
    attempts = 0
    while len(out) < n and attempts < n * 100:
        attempts += 1
        e = rng.choice(nontrivial)
        p_idx = rng.randrange(len(PRIMES))
        if not is_good_prime(e, p_idx):
            continue
        ap = ap_at(e, p_idx)
        if ap is None:
            continue
        t = torsion(e)
        p = PRIMES[p_idx]
        n_pts = p + 1 - ap
        out.append(build_record("TRUE_EC_TORSION", ec_label(e), t, p, n_pts, "divides"))
    return out


def gen_decoy_parity(ecs, rng, n: int) -> List[TheseusRecord]:
    """torsion(E) equal_mod_2 torsion(E) — true self-tautology (same object,
    same invariant, same value). Should trigger the tautology detector."""
    nontrivial = [e for e in ecs if (torsion(e) or 1) >= 2]
    out = []
    while len(out) < n:
        e = rng.choice(nontrivial)
        t = torsion(e)
        canonical = (
            f"CALIB[DECOY_PARITY] torsion(ec:{ec_label(e)})={t} "
            f"equal_mod_2 torsion(ec:{ec_label(e)})={t}"
        )
        payload = {
            "catalog_a": "ec",
            "object_a": ec_label(e),
            "invariant_a": "torsion",
            "value_a_raw": t,
            "catalog_b": "ec",
            "object_b": ec_label(e),
            "invariant_b": "torsion",    # MATCHES invariant_a so detector fires
            "value_b_raw": t,
            "relation": "equal_mod_2",
            "calibration_source": "DECOY_PARITY",
        }
        out.append(TheseusRecord(
            record_id=TheseusRecord.compute_record_id(canonical, SHARED_GENID),
            generator_id=SHARED_GENID,
            batch_id="calib_v1",
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=SHARED_KIND,
            claim_payload=payload,
            canonical_claim_text=canonical,
            verdict=SHARED_VERDICT,
            kill_pattern=None,
            method="calibration",
            convergence_status="exact",
            step_trace=SHARED_STEP_TRACE,
        ))
    return out


def gen_decoy_codomain(ecs, rng, n: int) -> List[TheseusRecord]:
    """torsion=1 divides #E(F_p): '1 divides anything' is universally true.
    Both observed and null should be 100% → contrast 0 → rejects."""
    trivial = [e for e in ecs if (torsion(e) or 1) == 1]
    out = []
    attempts = 0
    while len(out) < n and attempts < n * 100:
        attempts += 1
        e = rng.choice(trivial)
        p_idx = rng.randrange(len(PRIMES))
        if not is_good_prime(e, p_idx):
            continue
        ap = ap_at(e, p_idx)
        if ap is None:
            continue
        p = PRIMES[p_idx]
        n_pts = p + 1 - ap
        out.append(build_record(
            "DECOY_CODOMAIN", ec_label(e), 1,
            p, n_pts, "divides",
        ))
    return out


def gen_stratified_perm(ecs, rng, n: int) -> List[TheseusRecord]:
    """torsion(E1) divides #E2(F_p) — t and n_pts from DIFFERENT ECs at
    the same prime. Permutes the coupling but preserves marginals."""
    nontrivial = [e for e in ecs if (torsion(e) or 1) >= 2]
    out = []
    attempts = 0
    while len(out) < n and attempts < n * 100:
        attempts += 1
        e1, e2 = rng.sample(nontrivial, 2)
        p_idx = rng.randrange(len(PRIMES))
        if not (is_good_prime(e1, p_idx) and is_good_prime(e2, p_idx)):
            continue
        t = torsion(e1)
        ap2 = ap_at(e2, p_idx)
        if ap2 is None:
            continue
        p = PRIMES[p_idx]
        n_pts = p + 1 - ap2
        out.append(build_record(
            "STRATIFIED_PERM", ec_label(e1) + "/" + ec_label(e2), t,
            p, n_pts, "divides",
        ))
    return out


def gen_random_marginal(ecs, rng, n: int) -> List[TheseusRecord]:
    """torsion sampled from torsion marginal; n_pts sampled from n_pts marginal."""
    nontrivial = [e for e in ecs if (torsion(e) or 1) >= 2]
    tor_pool = [torsion(e) for e in nontrivial]
    npts_pool = []
    for e in nontrivial:
        for p_idx in range(len(PRIMES)):
            if is_good_prime(e, p_idx):
                ap = ap_at(e, p_idx)
                if ap is not None:
                    npts_pool.append(PRIMES[p_idx] + 1 - ap)
    out = []
    while len(out) < n:
        t = rng.choice(tor_pool)
        n_pts = rng.choice(npts_pool)
        out.append(build_record(
            "RANDOM_MARGINAL", "synthetic", t,
            PRIMES[0], n_pts, "divides",
        ))
    return out


# ============================================================
# F2 — content-aware contender (same shape as v0)
# ============================================================
def _is_self_tautology(records: List[TheseusRecord]) -> bool:
    n_self = 0
    for r in records:
        p = r.claim_payload
        if (p.get("object_a") == p.get("object_b")
            and p.get("invariant_a") == p.get("invariant_b")
            and p.get("value_a_raw") == p.get("value_b_raw")):
            n_self += 1
    return n_self >= 0.95 * len(records)


def F2_null_hold_rate(records, rng, n_samples: int = NULL_SAMPLES) -> float:
    """For divides relation: pool value_a (left side) and value_b (right side)
    from the source's records; sample random pairs; check divides."""
    if not records:
        return 0.0
    a_pool = [r.claim_payload["value_a_raw"] for r in records]
    b_pool = [r.claim_payload["value_b_raw"] for r in records]
    rel = records[0].claim_payload["relation"]
    n_hold = 0
    for _ in range(n_samples):
        a = rng.choice(a_pool)
        b = rng.choice(b_pool)
        if _evaluate_relation(a, b, rel):
            n_hold += 1
    return n_hold / n_samples


def F2_score_source(records, rng) -> Tuple[float, float, float, bool]:
    if not records:
        return (0.0, 0.0, 0.0, False)
    if _is_self_tautology(records):
        return (1.0, 1.0, 0.0, False)
    rel = records[0].claim_payload["relation"]
    n_hold = 0
    for r in records:
        a = r.claim_payload["value_a_raw"]
        b = r.claim_payload["value_b_raw"]
        if _evaluate_relation(a, b, rel):
            n_hold += 1
    obs = n_hold / len(records)
    null = F2_null_hold_rate(records, rng)
    contrast = abs(obs - null)
    return (obs, null, contrast, contrast >= F2_THRESHOLD)


def main():
    rng = random.Random(RNG_SEED)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    nontrivial = [e for e in ecs if (torsion(e) or 1) >= 2]
    print(f"Loaded {len(ecs)} ECs; {len(nontrivial)} have torsion >= 2.\n")

    sources: Dict[str, List[TheseusRecord]] = {}
    sources["TRUE_EC_TORSION"] = gen_true_ec_torsion(ecs, rng, N_PER_SOURCE)
    sources["DECOY_PARITY"] = gen_decoy_parity(ecs, rng, N_PER_SOURCE)
    sources["DECOY_CODOMAIN"] = gen_decoy_codomain(ecs, rng, N_PER_SOURCE)
    sources["STRATIFIED_PERM"] = gen_stratified_perm(ecs, rng, N_PER_SOURCE)
    sources["RANDOM_MARGINAL"] = gen_random_marginal(ecs, rng, N_PER_SOURCE)

    print("Scoring F1 (existing training_weight)...")
    f1_results = {}
    for src, recs in sources.items():
        if not recs:
            f1_results[src] = {"n": 0, "n_promoted": 0, "rate": 0.0, "mean_w": 0.0}
            continue
        weights = [training_weight(r) for r in recs]
        n_prom = sum(1 for w in weights if w >= F1_THRESHOLD)
        f1_results[src] = {
            "n": len(recs),
            "n_promoted": n_prom,
            "rate": n_prom / len(recs),
            "mean_w": sum(weights) / len(weights),
        }

    print("Scoring F2 (content-aware contrast)...")
    f2_results = {}
    for src, recs in sources.items():
        obs, null, contrast, promotes = F2_score_source(recs, rng)
        f2_results[src] = {
            "obs": obs, "null": null, "contrast": contrast, "promotes": promotes,
        }

    out = []
    out.append(f"# Calibration v1 — EC torsion divides #E(F_p)")
    out.append(f"")
    out.append(f"**Date:** {datetime.now(timezone.utc).date().isoformat()}")
    out.append(f"**Pre-registered thresholds:** F1 promote ≥ {F1_THRESHOLD}, F2 contrast ≥ {F2_THRESHOLD}")
    out.append(f"**N per source:** {N_PER_SOURCE}    **F2 null samples:** {NULL_SAMPLES}    **Seed:** {RNG_SEED}")
    out.append(f"**Restriction:** ECs with torsion >= 2 (n={len(nontrivial)} of {len(ecs)})")
    out.append(f"")
    out.append(f"## F1 — existing training_weight")
    out.append(f"")
    out.append(f"```")
    out.append(f"  {'source':<20} {'n':>5} {'n_promoted':>11} {'rate':>7} {'mean_w':>8}")
    for src, r in f1_results.items():
        out.append(f"  {src:<20} {r['n']:>5} {r['n_promoted']:>11} {r['rate']:>7.2%} {r['mean_w']:>8.3f}")
    out.append(f"```")
    out.append(f"")
    out.append(f"## F2 — content-aware (observed vs random-pairing null)")
    out.append(f"")
    out.append(f"```")
    out.append(f"  {'source':<20} {'observed':>9} {'null':>7} {'contrast':>9} {'promotes':>9}")
    for src, r in f2_results.items():
        out.append(f"  {src:<20} {r['obs']:>9.2%} {r['null']:>7.2%} {r['contrast']:>9.3f} {str(r['promotes']):>9}")
    out.append(f"```")
    out.append(f"")
    out.append(f"## Verdict")
    out.append(f"")

    # Verdict computation
    true_r = f2_results["TRUE_EC_TORSION"]
    decoys_promote = sum(1 for src, r in f2_results.items()
                         if src != "TRUE_EC_TORSION" and r["promotes"])
    n_decoys = sum(1 for src in f2_results if src != "TRUE_EC_TORSION")

    if true_r["promotes"] and decoys_promote == 0:
        f2_verdict = "CALIBRATED — F2 generalizes from Murasugi to EC torsion without re-tuning"
        f2_detail = (
            f"F2 promoted TRUE_EC_TORSION (contrast {true_r['contrast']:.3f}) and "
            f"rejected all {n_decoys} non-TRUE sources. The contrast metric and "
            f"threshold (0.10) work for a second, structurally different relation "
            f"without modification. The substrate's claim ecology supports content-"
            f"aware filtering on at least two distinct mathematical structures."
        )
    elif true_r["promotes"]:
        f2_verdict = f"MIXED — F2 catches TRUE but leaks {decoys_promote}/{n_decoys} decoys"
        f2_detail = "The contrast metric needs refinement for divides-relation."
    else:
        f2_verdict = "FAILED — F2 did not recover TRUE_EC_TORSION"
        f2_detail = (
            f"F2 contrast on TRUE = {true_r['contrast']:.3f}, below threshold {F2_THRESHOLD}. "
            f"Either the relation's coupling is too weak to surface from the marginal "
            f"distributions, or the v0 threshold doesn't generalize."
        )

    out.append(f"**{f2_verdict}**")
    out.append(f"")
    out.append(f"{f2_detail}")
    out.append(f"")

    out_path = (
        Path(__file__).resolve().parents[2] / "pivot" /
        f"calibration_v1_ec_torsion_{datetime.now(timezone.utc).date().isoformat()}.md"
    )
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print("\n--- F1 ---")
    for src, r in f1_results.items():
        print(f"  {src:<20} rate={r['rate']:.2%}  mean_w={r['mean_w']:.3f}")
    print("\n--- F2 ---")
    for src, r in f2_results.items():
        print(f"  {src:<20} obs={r['obs']:.2%}  null={r['null']:.2%}  contrast={r['contrast']:.3f}  promotes={r['promotes']}")
    print(f"\nVerdict: {f2_verdict}")


if __name__ == "__main__":
    main()
