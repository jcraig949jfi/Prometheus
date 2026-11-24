"""Unified work meter and 4-row Cognitive Accounting Ledger (frozen from line 1).

Records exact computational work across phases and enforces:
  - All failed LLM proposals are included in fixed crystallization cost F.
  - Break-even workload N* = F / (v_naked - v_unplugged) reported as a function,
    never cherry-picked at a single N.
  - CPU seconds converted to USD at a frozen rate for apples-to-apples accounting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PhaseBucket:
    eval_units: int = 0
    sat_calls: int = 0
    sat_seconds: float = 0.0
    cpu_seconds: float = 0.0
    llm_usd: float = 0.0
    llm_proposals_total: int = 0
    llm_proposals_accepted: int = 0


@dataclass
class WorkMeter:
    cpu_usd_per_core_hour: float = 0.05
    phases: Dict[str, PhaseBucket] = field(default_factory=dict)

    def _bucket(self, phase: str) -> PhaseBucket:
        if phase not in self.phases:
            self.phases[phase] = PhaseBucket()
        return self.phases[phase]

    def charge_evals(self, count: int, phase: str = "offline_eval") -> None:
        if count < 0:
            raise ValueError("count must be non-negative")
        self._bucket(phase).eval_units += int(count)

    def charge_sat_call(self, seconds: float, phase: str = "offline_eval") -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        b = self._bucket(phase)
        b.sat_calls += 1
        b.sat_seconds += float(seconds)
        b.cpu_seconds += float(seconds)

    def charge_cpu(self, seconds: float, phase: str = "offline_eval") -> None:
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        self._bucket(phase).cpu_seconds += float(seconds)

    def charge_llm_proposal(
        self,
        usd: float,
        accepted: bool,
        phase: str = "sleep_propose",
    ) -> None:
        if usd < 0:
            raise ValueError("usd must be non-negative")
        b = self._bucket(phase)
        b.llm_usd += float(usd)
        b.llm_proposals_total += 1
        if accepted:
            b.llm_proposals_accepted += 1

    def cpu_usd(self, seconds: float) -> float:
        return (seconds / 3600.0) * self.cpu_usd_per_core_hour

    def snapshot(self) -> Dict[str, object]:
        eval_units = sum(b.eval_units for b in self.phases.values())
        sat_calls = sum(b.sat_calls for b in self.phases.values())
        sat_seconds = sum(b.sat_seconds for b in self.phases.values())
        cpu_seconds = sum(b.cpu_seconds for b in self.phases.values())
        fixed_llm_usd = sum(b.llm_usd for b in self.phases.values())
        props_total = sum(b.llm_proposals_total for b in self.phases.values())
        props_acc = sum(b.llm_proposals_accepted for b in self.phases.values())
        return {
            "cpu_usd_per_core_hour": self.cpu_usd_per_core_hour,
            "eval_units": eval_units,
            "sat_calls": sat_calls,
            "sat_seconds": sat_seconds,
            "cpu_seconds": cpu_seconds,
            "cpu_usd": self.cpu_usd(cpu_seconds),
            "fixed_llm_usd": fixed_llm_usd,
            "total_usd": fixed_llm_usd + self.cpu_usd(cpu_seconds),
            "llm_proposals_total": props_total,
            "llm_proposals_accepted": props_acc,
            "by_phase": {
                k: {
                    "eval_units": b.eval_units,
                    "sat_calls": b.sat_calls,
                    "sat_seconds": b.sat_seconds,
                    "cpu_seconds": b.cpu_seconds,
                    "llm_usd": b.llm_usd,
                    "llm_proposals_total": b.llm_proposals_total,
                    "llm_proposals_accepted": b.llm_proposals_accepted,
                }
                for k, b in sorted(self.phases.items())
            },
        }

    @staticmethod
    def break_even_n(
        fixed_f: float,
        v_naked: float,
        v_unplugged: float,
    ) -> Optional[float]:
        """Compute N* = F / (v_naked - v_unplugged). Returns None if v_naked <= v_unplugged."""
        diff = v_naked - v_unplugged
        if diff <= 0.0:
            return None
        return fixed_f / diff
