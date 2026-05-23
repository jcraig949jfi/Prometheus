"""Theseus daemon — batch loop.

Runs N active generators in sequential round-robin within a wall-time
budget. After each batch, writes a journal entry (human-readable +
structured JSONL) and updates the bandit.

CLI:
    python -m theseus.daemon --batch-hours 0.05 --generators a1,b5,c1,d1,e1

For v0.1, generators run sequentially in round-robin. Tier-1 will swap
to ThreadPoolExecutor parallelism with a shared writer lock.
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from theseus import config as cfg
from theseus.config import (
    DEFAULT_ACTIVE_GENERATORS,
    DEFAULT_BANDIT_EPSILON,
    DEFAULT_BATCH_HOURS,
)
from theseus.orchestration import (
    register_theseus,
    log_batch_work,
    maybe_emit_discoveries,
    update_lifetime_after_batch,
)
from theseus.orchestration.bandit_state import hydrate_bandit, persist_bandit
from theseus.orchestration.signature_index import INSTANCE as SIGNATURE_INDEX
from theseus.scoring.demand_signals import INSTANCE as DEMAND_LOG
from theseus.bandit.epsilon_greedy import EpsilonGreedyBandit
from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.emit.corpus_writer import CorpusWriter
from theseus.emit.record_schema import TheseusRecord, Verdict
from typing import List as _List_for_typing
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.c1_claim_mutation import C1ClaimMutationGenerator
from theseus.generators.c2_threshold_mutation import C2ThresholdMutationGenerator
from theseus.generators.c3_region_slide import C3RegionSlideGenerator
from theseus.generators.c4_generalization import C4GeneralizationGenerator
from theseus.generators.c5_specialization import C5SpecializationGenerator
from theseus.generators.d1_kill_neighborhood import D1KillNeighborhoodGenerator
from theseus.generators.d2_margin_bracket import D2MarginBracketGenerator
from theseus.generators.d3_triangulation_seeds import D3TriangulationSeedsGenerator
from theseus.generators.d4_boundary_crossing import D4BoundaryCrossingGenerator
from theseus.generators.h1_self_play_hunter import H1SelfPlayHunterGenerator
from theseus.generators.h2_triangulation_protocol import H2TriangulationProtocolGenerator
from theseus.generators.h4_bridge_extension import H4BridgeExtensionGenerator
from theseus.registry import REGISTRY, get_generator_class, list_active
from theseus.scoring.metrics_schema import BatchMetrics, GeneratorMetrics
from theseus.scoring.yield_tracker import YieldTracker


def _new_batch_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"batch-{ts}-{uuid.uuid4().hex[:6]}"


def _instantiate_generators(
    gids: List[str], batch_id: str, seed: int
) -> List[Generator]:
    insts: List[Generator] = []
    for i, gid in enumerate(gids):
        cls = get_generator_class(gid)
        try:
            inst = cls(batch_id=batch_id, seed=seed + i)
        except TypeError:
            # Some generators don't take seed kwarg
            inst = cls(batch_id=batch_id)
        insts.append(inst)
    return insts


def _wire_feedback(
    generators: List[Generator], record: TheseusRecord
) -> None:
    """Route a newly emitted record to downstream generators that
    consume it as parent input (C1, D1)."""
    for g in generators:
        if isinstance(
            g,
            (
                C1ClaimMutationGenerator,
                C2ThresholdMutationGenerator,
                C3RegionSlideGenerator,
                C4GeneralizationGenerator,
                C5SpecializationGenerator,
                D3TriangulationSeedsGenerator,
                D4BoundaryCrossingGenerator,
                H1SelfPlayHunterGenerator,
                H2TriangulationProtocolGenerator,
                H4BridgeExtensionGenerator,
            ),
        ):
            g.add_parent(record)
        elif isinstance(g, D1KillNeighborhoodGenerator):
            g.add_kill(record)
        elif isinstance(g, D2MarginBracketGenerator):
            g.add_parent(record)


def run_batch(
    generator_ids: List[str],
    batch_hours: float,
    seed: int = 42,
    batch_id: Optional[str] = None,
    corpus_dir: Optional[Path] = None,
    emit_telemetry: bool = True,
) -> BatchMetrics:
    """Run one batch. Returns BatchMetrics.

    If `emit_telemetry` is True (default), calls into the orchestration
    layer at batch start + end: register_theseus, log_batch_work, and
    maybe_emit_discoveries for high-training-weight records.
    """
    if batch_id is None:
        batch_id = _new_batch_id()

    # Per-batch demand-signal log; generators record missing-primitive
    # events into this sink for the weekly "wanted primitives" report.
    DEMAND_LOG.reset(batch_id)

    started_at_iso = datetime.now(timezone.utc).isoformat()
    started_at_dt = datetime.now(timezone.utc)
    started_mono = time.monotonic()
    budget_s = batch_hours * 3600.0

    if emit_telemetry:
        register_theseus(
            target_generators=list(generator_ids),
            triggered_by="schedule",
            last_cycle_id=batch_id,
            errors_this_cycle=[],
        )

    # Filter out stubs that can't emit
    runnable = []
    for gid in generator_ids:
        cls = get_generator_class(gid)
        status = getattr(cls, "status", GeneratorStatus.STUB)
        if status == GeneratorStatus.ACTIVE:
            runnable.append(gid)

    if not runnable:
        # Nothing to do; emit empty batch
        bm = BatchMetrics(
            batch_id=batch_id,
            started_at=started_at_iso,
            ended_at=datetime.now(timezone.utc).isoformat(),
            duration_hours=0.0,
            active_generators=list(generator_ids),
        )
        _journal_batch(bm, generator_ids, [])
        return bm

    instances = _instantiate_generators(runnable, batch_id, seed)
    writer = CorpusWriter(batch_id=batch_id, corpus_dir=corpus_dir)
    tracker = YieldTracker()
    # Track records for telemetry discovery emission (cap at 2000 to bound memory)
    telemetry_record_sample: List[TheseusRecord] = []
    TELEMETRY_SAMPLE_CAP = 2000

    # Round-robin tick loop. Generators that return None on a single
    # tick are NOT marked exhausted — they may have hit a transient
    # parent-shortage. Only after CONSECUTIVE_NONE_THRESHOLD consecutive
    # Nones do we mark exhausted (true exhaustion, e.g. E1 finishes
    # mining).
    # Consecutive-None exhaustion threshold. Set high so cache-based
    # gens (E1/E2/E4/E5) survive race conditions where the cache file
    # gets populated mid-batch (e.g. user runs fetcher in parallel
    # with the batch). At ~1k ticks/sec, 100k = 100 seconds of pure
    # Nones before exhaustion — long enough for any realistic cache
    # fetch to complete. Fire #37 surfaced this race: e2 emitted 0
    # despite the arxiv fetcher cache showing up 30 sec into the run.
    CONSECUTIVE_NONE_THRESHOLD = 100_000
    exhausted = {g.generator_id: False for g in instances}
    consecutive_nones = {g.generator_id: 0 for g in instances}
    tick_count = 0
    total_records_written = 0
    while time.monotonic() - started_mono < budget_s:
        if all(exhausted.values()):
            break
        if total_records_written >= cfg.PER_BATCH_RECORD_CAP:
            break
        for g in instances:
            if exhausted[g.generator_id]:
                continue
            if time.monotonic() - started_mono >= budget_s:
                break
            if total_records_written >= cfg.PER_BATCH_RECORD_CAP:
                break
            tracker.start_generator(g.generator_id)
            try:
                rec = g.next()
            except Exception as exc:
                tracker.record_error(g.generator_id, repr(exc))
                tracker.stop_generator(g.generator_id)
                continue
            tracker.stop_generator(g.generator_id)
            if rec is None:
                consecutive_nones[g.generator_id] += 1
                if consecutive_nones[g.generator_id] >= CONSECUTIVE_NONE_THRESHOLD:
                    exhausted[g.generator_id] = True
                continue
            consecutive_nones[g.generator_id] = 0
            if writer.write(rec):
                total_records_written += 1
                tracker.record_emission(rec)
                _wire_feedback(instances, rec)
                # Cross-batch signature index — tracks whether this
                # record's CLAIM SHAPE has been seen before. Penelope's
                # 90% downstream dup report reflects shape repetition,
                # not record_id repetition.
                try:
                    SIGNATURE_INDEX.record(rec)
                except Exception:
                    pass  # best-effort; never break the loop
                if (
                    emit_telemetry
                    and len(telemetry_record_sample) < TELEMETRY_SAMPLE_CAP
                ):
                    telemetry_record_sample.append(rec)
        tick_count += 1

    ended_at = datetime.now(timezone.utc).isoformat()
    duration_hours = (time.monotonic() - started_mono) / 3600.0

    per_gen = tracker.finalize()
    # Fold writer's per-gen dup_rate into the metrics so downstream
    # consumers (journal, dashboard, bandit history) see saturation.
    dup_rates = writer.dup_rate_by_gen()
    for gid, m in per_gen.items():
        m.dup_rate = dup_rates.get(gid, 0.0)

    bm = BatchMetrics(
        batch_id=batch_id,
        started_at=started_at_iso,
        ended_at=ended_at,
        duration_hours=duration_hours,
        active_generators=list(generator_ids),
    )
    for m in per_gen.values():
        bm.add(m)

    # Saturation warning: gens with dup_rate > 0.70 within a batch are
    # exhausting their claim space. Per persona_seed_prompts_2026-05-21.md
    # Techne idea #4: makes the saturation Penelope reports (90% dups
    # downstream) visible from the Theseus side too.
    saturated = [
        (gid, m.dup_rate) for gid, m in per_gen.items()
        if m.dup_rate >= 0.70 and m.records_emitted + writer.duplicates_by_gen.get(gid, 0) >= 100
    ]
    if saturated:
        print(
            f"[theseus] SATURATION WARNING: "
            + ", ".join(f"{gid}@{rate*100:.0f}%" for gid, rate in saturated)
            + " — claim space exhausted; bandit should downweight."
        )

    # Flush demand-signal log to per-batch JSONL.
    demand_path = DEMAND_LOG.flush()
    if demand_path is not None:
        total_signals = len(DEMAND_LOG)
        print(
            f"[theseus] Demand signals logged: {total_signals} events -> "
            f"{demand_path.name}"
        )
        # Fire #63: surface the substrate's top-3 wanted primitives
        # in every fire's output. The substrate-shouting-for-X signal
        # was previously only visible via the demand_report CLI; now
        # it lands in the journal automatically.
        try:
            top = []
            for rec in DEMAND_LOG.summary()[:3]:
                sig = "/".join(rec["signature"]) if rec["signature"] else "(empty)"
                top.append(f"{rec['count']:,}× {sig}")
            if top:
                print(f"[theseus] Top demand: " + " | ".join(top))
        except Exception:
            pass  # best-effort; never break the loop

    # Flush signature index buffer in single transaction (hot-path
    # buffer was in-memory; sqlite write happens here).
    try:
        n_novel, n_total = SIGNATURE_INDEX.flush()
        # Fire #59: route per-gen novelty back into BatchMetrics so
        # yield_score is novelty-aware on the next bandit pick.
        try:
            novel_by_gen = SIGNATURE_INDEX.last_flush_novel_by_gen()
            for gid, n in novel_by_gen.items():
                if gid in bm.per_generator:
                    bm.per_generator[gid].novelty_signatures = n
        except Exception:
            pass  # best-effort; never break the loop
        # Fire #62: populate lifetime_saturation per gen so the bandit
        # sees a stable accumulated exploration signal instead of
        # single-batch novelty rates (which Fire #61 falsified as
        # too noisy). Probe is read after flush so it reflects this
        # batch's contribution too.
        try:
            for gid in bm.per_generator.keys():
                sat = SIGNATURE_INDEX.saturation_score(gid)
                if sat is not None:
                    bm.per_generator[gid].lifetime_saturation = sat
        except Exception:
            pass  # best-effort; never break the loop
        if n_total > 0:
            # Also compute discovery-role-only novelty (exclude
            # TAUTOLOGY_CONTROL, NULL_BASELINE, INFRA_DIAGNOSTIC per
            # Fire #55 advisory).
            try:
                from theseus.registry import REGISTRY
                from theseus.generators.base import NON_DISCOVERY_ROLES
                non_discovery_gids = {
                    gid for gid, cls in REGISTRY.items()
                    if getattr(cls, "role", None) in NON_DISCOVERY_ROLES
                }
                novel_disc = SIGNATURE_INDEX.count_unique_signatures_for_roles(
                    non_discovery_gids
                )
                print(
                    f"[theseus] Signature index: {n_novel} novel shapes / "
                    f"{n_total} unique-in-batch (cross-batch novelty); "
                    f"{novel_disc} lifetime shapes from DISCOVERY roles"
                )
            except Exception:
                print(
                    f"[theseus] Signature index: {n_novel} novel shapes / "
                    f"{n_total} unique-in-batch"
                )
        # Fire #60: surface LIFETIME signature-saturation per gen
        # used this fire. Lifetime sat = 1 - (unique_sigs / total_seen)
        # in the cross-batch index. Probe of current index showed
        # most gens at ~100% sat (shape-recycling) while c5 sits at
        # ~9% (genuinely exploring). Printing all picked gens sorted
        # ascending makes the structural-saturation pattern visible
        # per-fire — bandit can't fix what isn't surfaced.
        try:
            pairs = []
            for gid in generator_ids:
                sat = SIGNATURE_INDEX.saturation_score(gid)
                if sat is not None:
                    pairs.append((gid, sat))
            if pairs:
                pairs.sort(key=lambda x: x[1])  # ascending: explorers first
                print(
                    f"[theseus] Lifetime saturation (picked gens): "
                    + ", ".join(f"{gid}@{sat*100:.0f}%" for gid, sat in pairs)
                )
        except Exception:
            pass
    except Exception as e:
        print(f"[theseus] signature flush failed (non-fatal): {e}")

    _journal_batch(bm, generator_ids, instances)

    # Orchestration layer: log work, emit discoveries, update lifetime stats.
    if emit_telemetry:
        n_discoveries = maybe_emit_discoveries(telemetry_record_sample)
        log_batch_work(
            batch_metrics=bm,
            requested_generators=list(generator_ids),
            n_discoveries_emitted=n_discoveries,
            started_at=started_at_dt,
        )
        update_lifetime_after_batch(bm, n_discoveries_emitted=n_discoveries)
        # Re-register with refreshed status_json now that the batch is done
        register_theseus(
            target_generators=list(generator_ids),
            triggered_by="schedule",
            last_cycle_id=batch_id,
        )

    return bm


def _journal_batch(
    bm: BatchMetrics,
    requested_gids: List[str],
    instances: List[Generator],
) -> None:
    cfg.JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    # Structured log
    with cfg.BATCHES_JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "batch_id": bm.batch_id,
                    "started_at": bm.started_at,
                    "ended_at": bm.ended_at,
                    "duration_hours": bm.duration_hours,
                    "requested_generators": requested_gids,
                    "active_generators": [g.generator_id for g in instances],
                    "total_records": bm.total_records,
                    "total_kills": bm.total_kills,
                    "total_confirmations": bm.total_confirmations,
                    "total_inconclusive": bm.total_inconclusive,
                    "total_errors": bm.total_errors,
                    "per_generator": {
                        gid: asdict(m) for gid, m in bm.per_generator.items()
                    },
                },
                sort_keys=True,
                default=str,
            )
            + "\n"
        )
    # Human-readable append
    with cfg.BATCH_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(_render_batch_md(bm, requested_gids, instances))


def _render_batch_md(
    bm: BatchMetrics,
    requested_gids: List[str],
    instances: List[Generator],
) -> str:
    lines = [
        f"\n## {bm.batch_id}\n",
        f"- Started: {bm.started_at}",
        f"- Ended:   {bm.ended_at}",
        f"- Duration: {bm.duration_hours:.4f} h",
        f"- Requested: {','.join(requested_gids)}",
        f"- Active:    {','.join(g.generator_id for g in instances)}",
        f"- Records: {bm.total_records} "
        f"(kills={bm.total_kills}, "
        f"confirmations={bm.total_confirmations}, "
        f"inconclusive={bm.total_inconclusive}, "
        f"errors={bm.total_errors})",
        "",
        "### Per-generator yield",
        "",
    ]
    for gid, m in sorted(bm.per_generator.items()):
        lines.append(
            f"- **{gid}** — records={m.records_emitted}, "
            f"throughput={m.throughput:.1f}/h, "
            f"info_density={m.info_density_mean:.3f}, "
            f"diversity={m.diversity_mean:.3f}, "
            f"yield_score={m.yield_score:.4f}, "
            f"dup_rate={m.dup_rate:.3f}, "
            f"kills={m.kills}, conf={m.confirmations}, errs={m.errors}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(prog="theseus.daemon")
    p.add_argument(
        "--batch-hours",
        type=float,
        default=DEFAULT_BATCH_HOURS,
        help="Wall-time budget for this batch (hours).",
    )
    p.add_argument(
        "--generators",
        type=str,
        default=",".join(DEFAULT_ACTIVE_GENERATORS),
        help="Comma-separated generator_ids to run.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Random seed for generator sampling AND bandit selection. "
            "If unset, derived from the current time so consecutive "
            "daemon invocations rotate the active set. Pass an explicit "
            "integer for reproducible cross-invocation runs."
        ),
    )
    p.add_argument(
        "--batches",
        type=int,
        default=1,
        help="Number of consecutive batches to run.",
    )
    p.add_argument(
        "--bandit",
        action="store_true",
        help=(
            "Use the bandit to select the active generator set. When set, "
            "the bandit picks the FIRST batch's set too (UCB explores "
            "actives uniformly with empty history); --generators is "
            "ignored. Without --bandit, --generators is the literal set "
            "and the bandit only picks between subsequent batches."
        ),
    )
    p.add_argument(
        "--bandit-policy",
        choices=("epsilon_greedy", "yield_proportional"),
        default="yield_proportional",
        help="Bandit policy. Default: yield_proportional (GFlowNet-spirit).",
    )
    p.add_argument(
        "--inject-explorer-priors",
        action="store_true",
        help=(
            "Before hydrating bandit history, inject synthetic priors for "
            "gens whose lifetime_saturation is below 50%%. Bootstraps "
            "exploration when UCB+softmax aren't strong enough to surface "
            "low-history explorers (e.g., c5 at 9%% sat with n=2 history). "
            "Synthetic scores reflect what the lifetime-saturation yield "
            "formula would produce given the gen's actual sat. "
            "See theseus.scripts.bandit_priors_inject for the standalone CLI."
        ),
    )
    args = p.parse_args()

    # Default seed to a time-based value so consecutive daemon
    # invocations rotate the active set instead of picking the same
    # generators every fire. Without this, --seed 42 → identical
    # bandit picks across Fire #N and Fire #N+1.
    if args.seed is None:
        args.seed = int(time.time() * 1000) % (2 ** 31)
        print(f"[theseus] Auto-seeded run: --seed {args.seed}")

    gids = [g.strip() for g in args.generators.split(",") if g.strip()]
    if args.bandit_policy == "yield_proportional":
        bandit = YieldProportionalBandit(seed=args.seed)
    else:
        bandit = EpsilonGreedyBandit(epsilon=DEFAULT_BANDIT_EPSILON, seed=args.seed)
    history: Dict[str, List[GeneratorMetrics]] = {}

    # Hydrate bandit history from prior daemon invocations. This makes
    # cross-fire learning real: Fire #N+1's bandit knows yield curves
    # from Fires #1..N. Without this, every invocation starts with
    # empty history and the bandit can't actually prefer high-yield
    # gens over low-yield ones across fires.
    if args.bandit:
        # Fire #65: optionally inject explorer priors BEFORE hydration
        # so the synthetic scores land in the disk history first, then
        # get loaded together with the real history.
        if args.inject_explorer_priors:
            try:
                from theseus.scripts.bandit_priors_inject import inject
                n_explorers = inject(
                    threshold=0.5, base=0.003, n_copies=3, dry_run=False,
                )
                if n_explorers > 0:
                    print(
                        f"[theseus] Injected explorer priors for {n_explorers} gens"
                    )
            except Exception as e:
                print(f"[theseus] explorer priors injection failed (non-fatal): {e}")
        n_hydrated = hydrate_bandit(bandit)
        if n_hydrated > 0:
            print(
                f"[theseus] Hydrated bandit history: "
                f"{n_hydrated} yield-score entries from prior fires"
            )

    # When --bandit is set, the bandit picks the FIRST batch's set too.
    # Previously this was a no-op with --batches 1 because selection was
    # gated on i+1<args.batches. With empty history, the bandit's UCB
    # exploration bonus treats never-fired actives uniformly. With
    # hydrated history, yield-driven selection kicks in immediately.
    if args.bandit:
        gids = bandit.select(
            available=list_active(),
            history=history,
            n=len(gids),
        )
        print(f"[theseus] Bandit bootstrap selected: {gids}")

    for i in range(args.batches):
        print(f"[theseus] Starting batch {i + 1}/{args.batches} with {gids}")
        bm = run_batch(
            generator_ids=gids,
            batch_hours=args.batch_hours,
            seed=args.seed + i,
        )
        print(
            f"[theseus] Batch {bm.batch_id} done: "
            f"{bm.total_records} records "
            f"(kills={bm.total_kills}, conf={bm.total_confirmations})"
        )
        for gid, m in bm.per_generator.items():
            history.setdefault(gid, []).append(m)
            bandit.update({gid: m})

        if args.bandit and i + 1 < args.batches:
            gids = bandit.select(
                available=list_active(),
                history=history,
                n=len(gids),
            )
            print(f"[theseus] Bandit selected next active set: {gids}")

    # Persist bandit history for the next daemon invocation.
    if args.bandit:
        persist_bandit(bandit)


if __name__ == "__main__":
    main()
