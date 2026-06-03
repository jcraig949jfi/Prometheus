"""Content-aware promote-filter (F2).

A record's promotion decision based on whether the substrate's confirmation
rate for the record's relation-shape diverges meaningfully from a
random-pairing null on the same value distributions.

Calibrated in `theseus/scripts/calibration_v0_murasugi.py` (Murasugi
inequality) and `theseus/scripts/calibration_v1_ec_torsion.py` (EC
torsion divides #E(F_p)). On both synthetic-control sets, F2 with
threshold 0.10 achieves CALIBRATED outcome:
  TRUE planted -> promotes
  DECOY parity / codomain / stratified-perm / random-marginal -> rejects

Production usage:
  from theseus.scoring.content_aware_promote import (
      content_aware_promote_score,
      CONTENT_AWARE_PROMOTE_THRESHOLD,
  )
  score = content_aware_promote_score(record, value_pools)
  if score >= CONTENT_AWARE_PROMOTE_THRESHOLD:
      promote(record)

Where `value_pools` is a (a_pool, b_pool) tuple per (catalog_a,
invariant_a, catalog_b, invariant_b) — pre-computed from corpus or
catalog marginals.

Design property: F2 is INDEPENDENT of training_weight (F1). The
daemon can be configured to use F1, F2, or F1 AND F2 conjunction.

Doctrinal anchor: per `feedback_residue_must_be_navigable_not_logged`
criterion #5 (added 2026-05-30 after GPT-5 review), residue must
demonstrate measured counterfactual utility. F2's pass-rate vs F1's
pass-rate is the per-batch counterfactual delta.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.generators.a1_catalog_cross_product import _evaluate_relation


CONTENT_AWARE_PROMOTE_THRESHOLD = 0.10
DEFAULT_NULL_SAMPLES = 1000
TAUTOLOGY_DETECTION_FRACTION = 0.95

# Generators whose SHADOW/REJECTED verdict answers a META-RELATIONAL predicate
# (not "does rel(a,b) hold on the stored values"), so the raw-value F2 null is
# the WRONG basis for them. Established by calibration v3c (2026-06-03):
#   g4 reflection-duality  -> verdict = "rel is sign-reflection-invariant"
#   g5 scale-invariance    -> verdict = "rel is scale-invariant"
#   a3 functional-identity -> verdict = "rel(f(a), g(b)) holds" (transformed)
# Scoring these against a raw-value null manufactured ~all of v2's apparent
# corpus contrast (a category error, not coupling). See
# pivot/calibration_v3c_VERDICT_generator_category_error_2026-06-03.md.
META_RELATIONAL_GENERATORS = frozenset({"g4", "g5", "a3"})


def is_direct_relation_record(record: TheseusRecord) -> bool:
    """True iff this record's verdict answers the DIRECT predicate
    "does relation(value_a, value_b) hold" — the only predicate for which
    F2's raw-value null is valid.

    Resolution order (backwards-compatible):
      1. If claim_payload declares `predicate_kind`, honor it
         ('direct' -> True; anything else -> False).
      2. Else fall back to generator_id: META_RELATIONAL_GENERATORS -> False.
    """
    payload = record.claim_payload or {}
    pk = payload.get("predicate_kind")
    if pk is not None:
        return pk == "direct"
    return getattr(record, "generator_id", None) not in META_RELATIONAL_GENERATORS


def _payload_key(payload: Dict) -> Optional[Tuple[str, str, str, str, str]]:
    """Extract (catalog_a, invariant_a, catalog_b, invariant_b, relation) from
    a claim_payload. Returns None if any required field is missing."""
    ca = payload.get("catalog_a")
    cb = payload.get("catalog_b")
    ia = payload.get("invariant_a")
    ib = payload.get("invariant_b")
    rel = payload.get("relation")
    if not (ca and cb and ia and ib and rel):
        return None
    return (ca, ia, cb, ib, rel)


def _payload_values(payload: Dict) -> Optional[Tuple[int, int]]:
    """Extract (value_a, value_b) from a payload, handling both the
    value_a/value_b naming (a1/c1/f2-style) and value_a_raw/value_b_raw
    naming (a3-style)."""
    va = payload.get("value_a")
    if va is None:
        va = payload.get("value_a_raw")
    vb = payload.get("value_b")
    if vb is None:
        vb = payload.get("value_b_raw")
    if not (isinstance(va, int) and isinstance(vb, int)):
        return None
    return (va, vb)


def is_self_tautology_pair(payload: Dict) -> bool:
    """Detect a single record that compares X to itself (same object, same
    invariant, same value)."""
    return (
        payload.get("object_a") == payload.get("object_b")
        and payload.get("invariant_a") == payload.get("invariant_b")
        and payload.get("value_a") == payload.get("value_b")
        and payload.get("value_a_raw") == payload.get("value_b_raw")
    )


def content_aware_promote_score(
    record: TheseusRecord,
    a_pool: List[int],
    b_pool: List[int],
    rng: Optional[random.Random] = None,
    n_null_samples: int = DEFAULT_NULL_SAMPLES,
) -> float:
    """Compute F2 score for a single record.

    Args:
        record: the TheseusRecord to score.
        a_pool: a list of plausible value_a values to draw the null from.
                Typically: all value_a values seen in records sharing
                the same (catalog_a, invariant_a, relation).
        b_pool: same for value_b.
        rng: random source.
        n_null_samples: how many random pairs to sample for the null.

    Returns:
        A float in [0, 1]. Higher = more likely a content-bearing record.
        Threshold for promotion: CONTENT_AWARE_PROMOTE_THRESHOLD.

    Logic:
      - If record is a self-tautology (X relation X with same value),
        return 0.0 (tautologies pass shape but encode no content).
      - Compute observed = 1.0 if the relation holds on the record's
        own values, else 0.0.
      - Compute null = fraction of random-pair samples that satisfy the
        relation.
      - Score = |observed - null|. Single-record scores are 0 or
        |1 - null| for SHADOW records.

    Note: per-record scoring is noisy. Use group-level scoring
    (content_aware_promote_score_group) when N records share a key for
    a more reliable signal.
    """
    if rng is None:
        rng = random.Random()
    payload = record.claim_payload
    if is_self_tautology_pair(payload):
        return 0.0
    values = _payload_values(payload)
    key = _payload_key(payload)
    if values is None or key is None:
        return 0.0
    rel = key[4]
    a, b = values
    try:
        obs = 1.0 if _evaluate_relation(a, b, rel) else 0.0
    except Exception:
        return 0.0
    if not a_pool or not b_pool:
        return 0.0
    n_hold = 0
    for _ in range(n_null_samples):
        ai = rng.choice(a_pool)
        bi = rng.choice(b_pool)
        try:
            if _evaluate_relation(ai, bi, rel):
                n_hold += 1
        except Exception:
            continue
    null = n_hold / n_null_samples
    return abs(obs - null)


def content_aware_promote_score_group(
    records: List[TheseusRecord],
    rng: Optional[random.Random] = None,
    n_null_samples: int = DEFAULT_NULL_SAMPLES,
) -> float:
    """Compute F2 score for a group of records sharing the same (key).

    Group-level scoring is more reliable than per-record scoring because
    the null is computed from the group's own value distribution
    (matching marginals), and obs is averaged over the group.

    If 95%+ of records are self-tautologies, returns 0.0.
    Otherwise: contrast = |observed_hold_rate - null_hold_rate|.
    """
    if rng is None:
        rng = random.Random()
    if not records:
        return 0.0
    n_self = sum(1 for r in records if is_self_tautology_pair(r.claim_payload))
    if n_self >= TAUTOLOGY_DETECTION_FRACTION * len(records):
        return 0.0
    # Build pools and compute observed
    a_pool = []
    b_pool = []
    n_hold_obs = 0
    n_obs = 0
    rel = None
    for r in records:
        p = r.claim_payload
        key = _payload_key(p)
        if key is None:
            continue
        rel = key[4]
        vv = _payload_values(p)
        if vv is None:
            continue
        a, b = vv
        a_pool.append(a)
        b_pool.append(b)
        try:
            if _evaluate_relation(a, b, rel):
                n_hold_obs += 1
            n_obs += 1
        except Exception:
            continue
    if n_obs == 0 or rel is None:
        return 0.0
    obs = n_hold_obs / n_obs
    # Null from random pairing
    n_null_hold = 0
    for _ in range(n_null_samples):
        ai = rng.choice(a_pool)
        bi = rng.choice(b_pool)
        try:
            if _evaluate_relation(ai, bi, rel):
                n_null_hold += 1
        except Exception:
            continue
    null = n_null_hold / n_null_samples
    return abs(obs - null)


def content_aware_promotes(
    record: TheseusRecord,
    a_pool: List[int],
    b_pool: List[int],
    rng: Optional[random.Random] = None,
    threshold: float = CONTENT_AWARE_PROMOTE_THRESHOLD,
) -> bool:
    """Boolean wrapper: does this record pass the F2 promote gate?"""
    score = content_aware_promote_score(record, a_pool, b_pool, rng=rng)
    return score >= threshold


def build_value_pools_from_records(
    records: List[TheseusRecord],
) -> Dict[Tuple, Tuple[List[int], List[int]]]:
    """Group records by F2 key and build per-key value pools. Useful for
    a single-pass batch-level promote sweep.

    Returns: {key: (a_pool, b_pool)}.
    """
    pools: Dict[Tuple, Tuple[List[int], List[int]]] = {}
    for r in records:
        if not is_direct_relation_record(r):
            continue  # meta-relational verdicts must not pollute the raw-value null
        key = _payload_key(r.claim_payload)
        if key is None:
            continue
        values = _payload_values(r.claim_payload)
        if values is None:
            continue
        a, b = values
        if key not in pools:
            pools[key] = ([], [])
        pools[key][0].append(a)
        pools[key][1].append(b)
    return pools


def maybe_promote_by_f2(
    records: List[TheseusRecord],
    threshold: float = CONTENT_AWARE_PROMOTE_THRESHOLD,
    n_null_samples: int = DEFAULT_NULL_SAMPLES,
    rng: Optional[random.Random] = None,
) -> List[TheseusRecord]:
    """Batch-level: score each record under F2 using the batch's own
    value-pool marginals. Return the subset that passes the F2 threshold.

    Per-record promotion requires the record's verdict be SHADOW_CATALOG
    or REJECTED (i.e., the substrate emitted a confirmation/falsification
    decision the F2 metric can compare to a null). INCONCLUSIVE records
    are skipped.

    Use this from the daemon as an alternative or supplement to
    `maybe_emit_discoveries`.
    """
    if rng is None:
        rng = random.Random()
    pools = build_value_pools_from_records(records)
    promoted: List[TheseusRecord] = []
    for r in records:
        if r.verdict not in (Verdict.SHADOW_CATALOG.value, Verdict.REJECTED.value):
            continue
        if not is_direct_relation_record(r):
            continue  # g4/g5/a3 verdicts answer a different predicate (v3c)
        if is_self_tautology_pair(r.claim_payload):
            continue
        key = _payload_key(r.claim_payload)
        if key is None or key not in pools:
            continue
        a_pool, b_pool = pools[key]
        score = content_aware_promote_score(
            r, a_pool, b_pool, rng=rng, n_null_samples=n_null_samples,
        )
        if score >= threshold:
            promoted.append(r)
    return promoted
