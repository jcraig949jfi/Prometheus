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
from theseus.bandit.epsilon_greedy import EpsilonGreedyBandit
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
from theseus.registry import REGISTRY, get_generator_class
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
    CONSECUTIVE_NONE_THRESHOLD = 100
    exhausted = {g.generator_id: False for g in instances}
    consecutive_nones = {g.generator_id: 0 for g in instances}
    tick_count = 0
    while time.monotonic() - started_mono < budget_s:
        if all(exhausted.values()):
            break
        for g in instances:
            if exhausted[g.generator_id]:
                continue
            if time.monotonic() - started_mono >= budget_s:
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
            writer.write(rec)
            tracker.record_emission(rec)
            _wire_feedback(instances, rec)
            if (
                emit_telemetry
                and len(telemetry_record_sample) < TELEMETRY_SAMPLE_CAP
            ):
                telemetry_record_sample.append(rec)
        tick_count += 1

    ended_at = datetime.now(timezone.utc).isoformat()
    duration_hours = (time.monotonic() - started_mono) / 3600.0

    per_gen = tracker.finalize()
    bm = BatchMetrics(
        batch_id=batch_id,
        started_at=started_at_iso,
        ended_at=ended_at,
        duration_hours=duration_hours,
        active_generators=list(generator_ids),
    )
    for m in per_gen.values():
        bm.add(m)

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
        default=42,
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
        help="After each batch, let the bandit pick the next active set.",
    )
    args = p.parse_args()

    gids = [g.strip() for g in args.generators.split(",") if g.strip()]
    bandit = EpsilonGreedyBandit(epsilon=DEFAULT_BANDIT_EPSILON, seed=args.seed)
    history: Dict[str, List[GeneratorMetrics]] = {}

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
                available=list(REGISTRY.keys()),
                history=history,
                n=len(gids),
            )
            print(f"[theseus] Bandit selected next active set: {gids}")


if __name__ == "__main__":
    main()
