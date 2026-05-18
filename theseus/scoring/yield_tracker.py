"""YieldTracker — per-generator scoreboard during a batch."""
from __future__ import annotations

import time
from typing import Dict, List

from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.scoring.metrics_schema import GeneratorMetrics
from theseus.scoring.info_density import info_density_score
from theseus.scoring.diversity import diversity_score


class YieldTracker:
    """Tracks per-generator yield as records are emitted."""

    def __init__(self) -> None:
        self.metrics: Dict[str, GeneratorMetrics] = {}
        self.start_times: Dict[str, float] = {}
        self._recent: List[TheseusRecord] = []

    def start_generator(self, generator_id: str) -> None:
        if generator_id not in self.metrics:
            self.metrics[generator_id] = GeneratorMetrics(
                generator_id=generator_id
            )
        self.start_times[generator_id] = time.monotonic()

    def stop_generator(self, generator_id: str) -> None:
        if generator_id in self.start_times:
            m = self.metrics[generator_id]
            m.wall_seconds += time.monotonic() - self.start_times[generator_id]
            del self.start_times[generator_id]

    def record_emission(self, record: TheseusRecord) -> None:
        gid = record.generator_id
        if gid not in self.metrics:
            self.metrics[gid] = GeneratorMetrics(generator_id=gid)
        m = self.metrics[gid]
        m.records_emitted += 1

        # Verdict accounting
        if record.verdict == Verdict.REJECTED.value:
            m.kills += 1
        elif record.verdict in (Verdict.PROMOTED.value, Verdict.SHADOW_CATALOG.value):
            m.confirmations += 1
        elif record.verdict == Verdict.INCONCLUSIVE.value:
            m.inconclusive += 1

        # Info density: running mean
        d = info_density_score(record)
        prev_mean = m.info_density_mean
        m.info_density_mean = (
            (prev_mean * (m.records_emitted - 1) + d) / m.records_emitted
        )

        # Diversity: against recent global emissions
        dv = diversity_score(record, self._recent)
        prev_div = m.diversity_mean
        m.diversity_mean = (
            (prev_div * (m.records_emitted - 1) + dv) / m.records_emitted
        )

        # Throughput recomputed at finalize
        self._recent.append(record)
        if len(self._recent) > 500:
            self._recent = self._recent[-500:]

    def record_error(self, generator_id: str, msg: str) -> None:
        if generator_id not in self.metrics:
            self.metrics[generator_id] = GeneratorMetrics(
                generator_id=generator_id
            )
        m = self.metrics[generator_id]
        m.errors += 1

    def finalize(self) -> Dict[str, GeneratorMetrics]:
        """Compute final throughput / yield_score for each generator."""
        for gid in list(self.start_times.keys()):
            self.stop_generator(gid)
        for m in self.metrics.values():
            hours = max(m.wall_seconds / 3600.0, 1e-9)
            m.throughput = m.records_emitted / hours
        return dict(self.metrics)
