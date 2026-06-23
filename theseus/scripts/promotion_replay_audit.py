"""M0.5 — Promotion replay audit (Theseus emit corpus).

Reassessment v2 §M0.5 (`pivot/REASSESSMENT_2026-06-22_v2_enforcement.md`) and the
program-stall map (`roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`)
established — and Techne verified at the code level this session — that Theseus
"promotion" is a metadata-SHAPE filter (`training_weight >= 0.6`, top-20/batch;
see `theseus/orchestration/telemetry.py:maybe_emit_discoveries`). The filter never
inspects whether the claimed mathematical relation actually HOLDS on the stored
values. The substrate already built the CONTENT check (F2,
`theseus/scoring/content_aware_promote.py`) but it does NOT gate promotion.

This tool is the deferred-replay step the code always intended. It:

  1. Reconstructs, per batch, the historical F1-promoted population
     (top-`max_per_batch` records with `training_weight >= threshold`,
     role-included) — the exact rule that produced the lifetime "discovery" count.
  2. RE-RUNS the content check (F2 raw-value evaluation) the shape-filter skipped,
     for the DIRECT-predicate population only (per calibration v3c: F2's
     raw-value null is a category error for meta-relational g4/g5/a3 verdicts).
  3. Tallies the v2 §M0.5 replay schema.

Doctrine it enforces (v2 §4.1, "replay-or-it-didn't-promote"): no promoted claim
enters doctrine unless it is replay-verifiable from stored inputs under the
current battery.

This is a MEASUREMENT, not a re-promotion: it changes no corpus record. Output is
a single JSON artifact. Streaming + gz-aware so it runs on the ~362 GB corpus on
this host with no Postgres, no `.176`, no credits.

Usage:
    # smoke on one batch
    python -m theseus.scripts.promotion_replay_audit --limit-batches 1 \
        --out pivot/promotion_replay_audit_smoke.json
    # full sweep
    python -m theseus.scripts.promotion_replay_audit \
        --out pivot/promotion_replay_audit_<date>.json

Evidence level of the output: E4 (replayed from raw stored artifacts).
"""
from __future__ import annotations

import argparse
import dataclasses
import gzip
import heapq
import itertools
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- repo root on path (script may be run as file or module) ---
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from theseus.emit.record_schema import TheseusRecord, Verdict  # noqa: E402
from theseus.scoring.training_weight import training_weight  # noqa: E402
from theseus.scoring.content_aware_promote import (  # noqa: E402
    CONTENT_AWARE_PROMOTE_THRESHOLD,
    is_direct_relation_record,
    is_self_tautology_pair,
    _payload_key,
    _payload_values,
    content_aware_promote_score,
)
from theseus.generators.a1_catalog_cross_product import _evaluate_relation  # noqa: E402
from theseus.scoring.content_aware_promote import META_RELATIONAL_GENERATORS  # noqa: E402


def _raw_is_direct(d: dict) -> bool:
    """is_direct_relation_record on a raw corpus dict — no dataclass build.
    Mirrors content_aware_promote.is_direct_relation_record's resolution order."""
    payload = d.get("claim_payload") or {}
    pk = payload.get("predicate_kind")
    if pk is None:
        pk = d.get("predicate_kind")
    if pk is not None:
        return pk == "direct"
    return d.get("generator_id") not in META_RELATIONAL_GENERATORS


def _raw_key_values(payload: dict):
    """(_payload_key, _payload_values) on a raw payload dict — no dataclass."""
    ca, cb = payload.get("catalog_a"), payload.get("catalog_b")
    ia, ib = payload.get("invariant_a"), payload.get("invariant_b")
    rel = payload.get("relation")
    if not (ca and cb and ia and ib and rel):
        return None, None
    va = payload.get("value_a")
    if va is None:
        va = payload.get("value_a_raw")
    vb = payload.get("value_b")
    if vb is None:
        vb = payload.get("value_b_raw")
    if not (isinstance(va, int) and isinstance(vb, int)):
        return (ca, ia, cb, ib, rel), None
    return (ca, ia, cb, ib, rel), (va, vb)

DEFAULT_CORPUS_DIR = _REPO / "theseus" / "corpus"
F1_THRESHOLD = 0.6
F1_MAX_PER_BATCH = 20
# Reservoir cap per (key, side) for the F2 random-pairing null. The null only
# needs a representative sample of the value marginal; capping bounds memory on
# multi-GB batches (millions of records) to a few thousand ints per key.
POOL_RESERVOIR_CAP = 4000


def _can_possibly_promote(d: dict) -> bool:
    """Cheap raw-dict pre-filter: skip the expensive weight computation for the
    ~99% of records that cannot reach the 0.6 threshold under the CURRENT
    formula.

    Justification (training_weight = base × verdict_mult × triangulation_bonus,
    clamped): the max non-a1 base is bridge_extension=0.55; a1 bases are
    deliberately calibrated below 0.33 (info-content multiplier). For corpus
    verdicts (SHADOW/REJECTED, verdict_mult ≤ 1.0) the only routes over 0.6 are
    triangulation (step_trace → ×1.3, e.g. 0.55×1.3=0.715) or a PROMOTED verdict
    (×1.5). Anything lacking BOTH maxes at base×1.0 ≤ 0.55 < 0.6.
    """
    if d.get("step_trace"):
        return True
    if d.get("verdict") == "PROMOTED":
        return True
    return False

_FIELDS = {f.name for f in dataclasses.fields(TheseusRecord)}


def _record_from_dict(d: dict) -> Optional[TheseusRecord]:
    """Reconstruct a TheseusRecord from a corpus JSONL dict, tolerating
    extra/missing fields. Returns None if the required identity fields are
    absent."""
    kw = {k: v for k, v in d.items() if k in _FIELDS}
    # Required positional-ish fields; bail if the line is not a record.
    for req in ("record_id", "generator_id", "batch_id", "claim_kind"):
        if req not in kw:
            return None
    kw.setdefault("emitted_at", "")
    kw.setdefault("claim_payload", {})
    kw.setdefault("canonical_claim_text", "")
    kw.setdefault("verdict", Verdict.UNVERIFIED.value)
    try:
        return TheseusRecord(**kw)
    except Exception:
        return None


def _non_discovery_gids() -> set:
    try:
        from theseus.registry import REGISTRY
        from theseus.generators.base import NON_DISCOVERY_ROLES
        return {
            gid for gid, cls in REGISTRY.items()
            if getattr(cls, "role", None) in NON_DISCOVERY_ROLES
        }
    except Exception:
        return set()


def _f1_promoted_in_batch(
    records: List[TheseusRecord],
    non_discovery_gids: set,
    threshold: float = F1_THRESHOLD,
    max_per_batch: int = F1_MAX_PER_BATCH,
) -> List[Tuple[float, TheseusRecord]]:
    """Reconstruct the historical F1 promote decision for one batch:
    top-`max_per_batch` records with training_weight >= threshold, role-included.
    Mirrors theseus.orchestration.telemetry.maybe_emit_discoveries exactly."""
    weighted: List[Tuple[float, TheseusRecord]] = []
    for r in records:
        if r.generator_id in non_discovery_gids:
            continue
        try:
            w = training_weight(r)
        except Exception:
            continue
        if w >= threshold:
            weighted.append((w, r))
    weighted.sort(key=lambda x: -x[0])
    return weighted[:max_per_batch]


def _iter_batch_paths(corpus_dir: Path) -> List[Path]:
    paths = list(corpus_dir.glob("*.jsonl")) + list(corpus_dir.glob("*.jsonl.gz"))
    paths = [p for p in paths if "annotated" not in p.name]
    return sorted(paths, key=lambda p: p.name)


def _open_batch(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "rt", encoding="utf-8")


def _reservoir_add(pools, seen, key, value, rng):
    """Reservoir-sample (value_a, value_b) into per-key pools, bounded at
    POOL_RESERVOIR_CAP per side. Keeps a uniform sample of the value marginal
    so the F2 null is representative without unbounded memory."""
    a, b = value
    if key not in pools:
        pools[key] = ([], [])
        seen[key] = 0
    seen[key] += 1
    n = seen[key]
    a_pool, b_pool = pools[key]
    if n <= POOL_RESERVOIR_CAP:
        a_pool.append(a)
        b_pool.append(b)
    else:
        j = rng.randint(0, n - 1)
        if j < POOL_RESERVOIR_CAP:
            a_pool[j] = a
            b_pool[j] = b


def _replay_content(
    rec: TheseusRecord,
    batch_pools: Dict[Tuple, Tuple[List[int], List[int]]],
    rng: random.Random,
    n_null_samples: int,
) -> dict:
    """Run the content check the shape-filter skipped on one promoted record.

    Returns a dict with the per-record replay outcome. Classification:
      missing_features    — payload lacks the values/key needed to replay.
      not_direct          — meta-relational verdict (g4/g5/a3); F2 raw-value
                            null is the wrong basis (calibration v3c). Not a
                            failure of the record; a limit of THIS replay.
      self_tautology      — passes shape but compares X to itself (no content).
      content_mismatch    — relation does NOT hold on the record's own values
                            (the record asserts confirmation it cannot support).
      still_valid         — relation holds AND F2 score beats the content
                            threshold vs the batch random-pairing null.
      content_weak        — relation holds but F2 score below threshold
                            (indistinguishable from random pairing — survives
                            shape but the content carries no signal over null).
    """
    payload = rec.claim_payload or {}
    if not is_direct_relation_record(rec):
        return {"class": "not_direct"}
    # Missing-features takes precedence over the tautology check: a payload
    # lacking the catalog/invariant/value fields trips is_self_tautology_pair's
    # all-None==all-None branch as a false positive, but it is really a
    # provenance gap. Real tautologies always carry the key fields, so they are
    # still caught below.
    key = _payload_key(payload)
    values = _payload_values(payload)
    if key is None or values is None:
        return {"class": "missing_features"}
    if is_self_tautology_pair(payload):
        return {"class": "self_tautology"}
    a, b = values
    rel = key[4]
    try:
        holds = bool(_evaluate_relation(a, b, rel))
    except Exception as e:
        return {"class": "replay_failed", "error": repr(e)}
    if not holds:
        return {"class": "content_mismatch", "relation": rel, "a": a, "b": b}
    # Relation holds — now does it beat the random-pairing null?
    a_pool, b_pool = batch_pools.get(key, ([], []))
    score = content_aware_promote_score(
        rec, a_pool, b_pool, rng=rng, n_null_samples=n_null_samples
    )
    if score >= CONTENT_AWARE_PROMOTE_THRESHOLD:
        return {"class": "still_valid", "relation": rel, "f2_score": round(score, 4)}
    return {"class": "content_weak", "relation": rel, "f2_score": round(score, 4)}


def run_audit(
    corpus_dir: Path,
    limit_batches: Optional[int] = None,
    n_null_samples: int = 500,
    seed: int = 0,
    stride: int = 1,
) -> dict:
    rng = random.Random(seed)
    non_discovery_gids = _non_discovery_gids()
    all_paths = _iter_batch_paths(corpus_dir)
    paths = all_paths[::stride] if stride > 1 else all_paths
    if limit_batches is not None:
        paths = paths[:limit_batches]

    tally = {
        "total_promoted": 0,
        "replayable_promoted": 0,   # had values+key+direct predicate to re-run
        "replay_failed": 0,         # evaluator raised
        "missing_features": 0,      # provenance gap
        "not_direct": 0,            # meta-relational; F2 null invalid (v3c)
        "self_tautology": 0,        # shape-passing tautology, no content
        "content_mismatch": 0,      # relation does NOT hold — invalidated
        "content_weak": 0,          # holds but indistinguishable from null
        "still_valid": 0,           # holds AND beats the content null
    }
    by_kind: Dict[str, Dict[str, int]] = {}
    examples: Dict[str, List[dict]] = {"content_mismatch": [], "content_weak": []}

    batches_seen = 0
    for path in paths:
        # --- single streaming pass: never hold the whole batch in memory ---
        # (1) running top-K promoted heap, (2) reservoir-sampled value pools.
        promoted_heap: List[Tuple[float, int, TheseusRecord]] = []  # min-heap by weight
        tiebreak = itertools.count()
        batch_pools: Dict[Tuple, Tuple[List[int], List[int]]] = {}
        pool_seen: Dict[Tuple, int] = {}  # per-key count for reservoir sampling
        try:
            with _open_batch(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    # --- pool accumulation (direct records only), raw-dict
                    # fast path: no dataclass build for the bulk of records ---
                    payload = d.get("claim_payload")
                    if payload and _raw_is_direct(d):
                        k, v = _raw_key_values(payload)
                        if k is not None and v is not None:
                            _reservoir_add(batch_pools, pool_seen, k, v, rng)
                    # --- promote-candidate path (cheap pre-filter first) ---
                    if not _can_possibly_promote(d):
                        continue
                    rec = _record_from_dict(d)
                    if rec is None or rec.generator_id in non_discovery_gids:
                        continue
                    try:
                        w = training_weight(rec)
                    except Exception:
                        continue
                    if w < F1_THRESHOLD:
                        continue
                    if len(promoted_heap) < F1_MAX_PER_BATCH:
                        heapq.heappush(promoted_heap, (w, next(tiebreak), rec))
                    elif w > promoted_heap[0][0]:
                        heapq.heapreplace(promoted_heap, (w, next(tiebreak), rec))
        except Exception as e:
            print(f"[replay-audit] batch read failed {path.name}: {e}", file=sys.stderr)
            continue
        batches_seen += 1

        promoted = [(w, rec) for w, _, rec in promoted_heap]
        for w, rec in promoted:
            tally["total_promoted"] += 1
            out = _replay_content(rec, batch_pools, rng, n_null_samples)
            cls = out["class"]
            tally[cls] = tally.get(cls, 0) + 1
            if cls in ("still_valid", "content_weak", "content_mismatch", "replay_failed"):
                tally["replayable_promoted"] += 1
            kd = by_kind.setdefault(rec.claim_kind, {})
            kd[cls] = kd.get(cls, 0) + 1
            if cls in examples and len(examples[cls]) < 10:
                examples[cls].append({
                    "record_id": rec.record_id,
                    "generator_id": rec.generator_id,
                    "claim_kind": rec.claim_kind,
                    "training_weight": round(w, 4),
                    "text": rec.canonical_claim_text[:200],
                    **{k: v for k, v in out.items() if k != "class"},
                })

        print(
            f"[replay-audit] {path.name}: keys={len(batch_pools)} "
            f"promoted={len(promoted)} cum_total={tally['total_promoted']} "
            f"mismatch={tally['content_mismatch']} weak={tally['content_weak']} "
            f"valid={tally['still_valid']}",
            file=sys.stderr,
        )

    # Derived headline: of the promotions we COULD content-check, what fraction
    # survives as genuine signal (still_valid) vs is invalidated/weak?
    checkable = tally["still_valid"] + tally["content_weak"] + tally["content_mismatch"]
    tally["content_checkable"] = checkable
    tally["fraction_still_valid_of_checkable"] = (
        round(tally["still_valid"] / checkable, 4) if checkable else None
    )
    tally["fraction_invalidated_or_weak_of_checkable"] = (
        round((tally["content_mismatch"] + tally["content_weak"]) / checkable, 4)
        if checkable else None
    )

    return {
        "audit": "M0.5_promotion_replay",
        "scope": "theseus_emit_corpus",
        "promote_rule": {
            "filter": "training_weight >= %.2f, top-%d per batch, role-included"
                      % (F1_THRESHOLD, F1_MAX_PER_BATCH),
            "source": "theseus/orchestration/telemetry.py:maybe_emit_discoveries",
        },
        "replay_check": {
            "primitive": "content_aware_promote (F2) + _evaluate_relation raw-value",
            "f2_threshold": CONTENT_AWARE_PROMOTE_THRESHOLD,
            "n_null_samples": n_null_samples,
            "direct_predicate_only": True,
            "v3c_note": "meta-relational g4/g5/a3 verdicts classified not_direct "
                        "(raw-value null is a category error for them)",
        },
        "corpus_dir": str(corpus_dir),
        "batches_total": len(all_paths),
        "stride": stride,
        "batches_audited": batches_seen,
        "tally": tally,
        "by_claim_kind": by_kind,
        "examples": examples,
        "generated_by": "theseus/scripts/promotion_replay_audit.py",
    }


DEFAULT_SIGNATURE_INDEX = _REPO / "theseus" / "orchestration" / "signature_index.sqlite"


def run_ledger_census(signature_index: Path) -> dict:
    """Charon's scoped M0.5: census the Theseus signature_index ledger — the
    actual per-agent promotion/verdict surface — rather than the near-empty
    sigma_kernel DB (Charon C-2026-06-23-A/B, charon/CHARON_SESSION_2026-06-23.md).

    Finding this surfaces (verified E3): the ledger is SHAPE-KEYED with the
    verdict baked into the dedup key (e.g. `c1:equal_mod_2:ec.rank|knot.three_genus:CONFIRM`).
    Each of the ~3,311 rows is a shape×verdict class collapsing up to millions of
    raw records (seen_count). It carries NO raw values/relation columns, so it is
    NOT content-replayable on its own — replay requires a join back to the corpus
    by signature. That is Charon's predicted provenance gap, quantified."""
    import sqlite3
    conn = sqlite3.connect(str(signature_index))
    cols = [r[1] for r in conn.execute("PRAGMA table_info(signatures)")]
    by_verdict = {}
    for vc, classes, seen in conn.execute(
        "SELECT verdict_class, COUNT(*), SUM(seen_count) FROM signatures "
        "GROUP BY verdict_class ORDER BY SUM(seen_count) DESC"
    ):
        by_verdict[vc] = {"shape_classes": classes, "raw_records": int(seen)}
    by_kind = dict(conn.execute(
        "SELECT claim_kind, COUNT(*) FROM signatures GROUP BY claim_kind "
        "ORDER BY 2 DESC"
    ).fetchall())
    top_confirm = [
        {"signature": s, "generator_id": g, "seen_count": int(sc)}
        for s, g, sc in conn.execute(
            "SELECT signature, generator_id, seen_count FROM signatures "
            "WHERE verdict_class='CONFIRM' ORDER BY seen_count DESC LIMIT 10"
        )
    ]
    total_classes = conn.execute("SELECT COUNT(*) FROM signatures").fetchone()[0]
    total_raw = conn.execute("SELECT SUM(seen_count) FROM signatures").fetchone()[0]
    conn.close()
    return {
        "audit": "M0.5_ledger_census",
        "scope": "theseus_signature_index",
        "signature_index": str(signature_index),
        "ledger_columns": cols,
        "content_replayable_from_ledger": False,
        "content_replayable_reason": (
            "shape-keyed: signature encodes generator:relation:invariant-pair:verdict; "
            "no raw value/relation columns; verdict baked into the dedup key. "
            "Content-replay requires a join to the corpus by signature."
        ),
        "total_shape_classes": total_classes,
        "total_raw_records_indexed": int(total_raw),
        "by_verdict_class": by_verdict,
        "by_claim_kind": by_kind,
        "top_confirm_classes_by_volume": top_confirm,
        "generated_by": "theseus/scripts/promotion_replay_audit.py --ledger",
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="M0.5 promotion replay audit (Theseus corpus + ledger)")
    ap.add_argument("--ledger", action="store_true",
                    help="census the signature_index ledger (Charon scoped M0.5) "
                         "instead of the corpus replay")
    ap.add_argument("--signature-index", type=Path, default=DEFAULT_SIGNATURE_INDEX)
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR)
    ap.add_argument("--limit-batches", type=int, default=None,
                    help="audit only the first N batches (smoke mode)")
    ap.add_argument("--stride", type=int, default=1,
                    help="audit every Nth batch (stratified cross-timeline sample)")
    ap.add_argument("--n-null-samples", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    if args.ledger:
        result = run_ledger_census(args.signature_index)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print("\n=== M0.5 ledger census (Theseus signature_index) ===")
        print(f"shape classes       : {result['total_shape_classes']:,}")
        print(f"raw records indexed : {result['total_raw_records_indexed']:,}")
        print(f"content-replayable from ledger alone: {result['content_replayable_from_ledger']}")
        for vc, d in result["by_verdict_class"].items():
            print(f"  {vc:<12}: {d['shape_classes']:>5} classes  {d['raw_records']:>14,} raw records")
        print(f"wrote {args.out}")
        return 0

    t0 = time.time()
    result = run_audit(
        args.corpus_dir,
        limit_batches=args.limit_batches,
        n_null_samples=args.n_null_samples,
        seed=args.seed,
        stride=args.stride,
    )
    result["wall_seconds"] = round(time.time() - t0, 1)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    t = result["tally"]
    print(f"\n=== M0.5 promotion replay audit ===")
    print(f"batches audited     : {result['batches_audited']}")
    print(f"total F1-promoted   : {t['total_promoted']}")
    print(f"  not_direct (v3c)  : {t['not_direct']}")
    print(f"  self_tautology    : {t['self_tautology']}")
    print(f"  missing_features  : {t['missing_features']}")
    print(f"  content-checkable : {t['content_checkable']}")
    print(f"    still_valid     : {t['still_valid']}")
    print(f"    content_weak    : {t['content_weak']}")
    print(f"    content_mismatch: {t['content_mismatch']}")
    print(f"  replay_failed     : {t['replay_failed']}")
    print(f"fraction still_valid of checkable    : {t['fraction_still_valid_of_checkable']}")
    print(f"fraction invalidated/weak of checkable: {t['fraction_invalidated_or_weak_of_checkable']}")
    print(f"wrote {args.out}  ({result['wall_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
