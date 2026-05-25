"""SelfImprovingDaemon — a mixin for daemons that detect their own stagnation
and adapt.

Design rationale (see pivot/self_improving_daemon_design_2026-05-25.md):
  - Most self-improving agents hit a wall after N generations because their
    adaptation menu is finite. James's C# experiment stalled at gen 30.
  - This mixin ships the v1 framework (detect / propose / apply / observe /
    keep-or-revert) with reversible-by-construction adaptations.
  - v1 does NOT solve the gen-N wall. Phase 2/3 mechanisms (cross-agent
    borrowing, LLM-authored mutations, generational handoff) are
    explicitly noted as future paths the API is shaped to accept.

Usage (subclass pattern):

    from agents._shared.self_improving import (
        SelfImprovingDaemon, Adaptation, HealthSample
    )

    class MyDaemon(SelfImprovingDaemon):
        ADAPTATION_MENU = [
            Adaptation(
                name='DROP_CACHE',
                description='Clear my path-mtime cache; force rescan',
                cost='one_tick',
                reversibility='auto_one_tick',
                apply=lambda agent, state: state.pop('path_mtimes', None),
                revert=lambda agent, state, snapshot: None,
            ),
            ...
        ]

        def measure_health(self, recent_stats):
            return HealthSample(
                null_rate=...,
                diversity=...,
                downstream_consumption=...,
            )

Then inside your tick:

        self.run_self_improvement_cycle(
            tick_stats=stats,
            agent_state=state,
            shared_state_path=AGENT_DIR / 'state' / 'self_improvement.json',
        )

Hard contracts:
  - Mission lock: this mixin NEVER mutates the agent's CHARTER, name, or
    daemon.py code. Adaptations mutate tactics (config, paths, modes,
    keyword sets, cached state). Mission is constant.
  - Mutation budget: max_mutations_per_day caps the per-day burn.
  - Reward function discipline: composite health metric, never single-
    variable (NULL_RATE alone is exploitable).
  - Exhaustion = escalation: when the menu is empty AND no recent
    adaptation produced a win, the daemon fires a self-summon ticket
    instead of silently giving up.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger("self_improving")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Adaptation:
    """One atomic, reversible mutation to a daemon's tactics."""
    name: str
    description: str
    cost: str                  # 'zero' | 'trivial' | 'one_tick' | 'medium' | 'high'
    reversibility: str         # 'auto_one_tick' | 'manual_via_revert' | 'never'
    apply: Callable[[Any, dict], Any]   # (agent, agent_state) -> snapshot for revert
    revert: Optional[Callable[[Any, dict, Any], None]] = None
    requires_human_approval: bool = False
    last_applied_at: Optional[str] = None
    apply_count: int = 0


@dataclass
class HealthSample:
    """One tick's health reading. Composite by design — single metrics
    are reward-hackable (lowering filters drops NULL_RATE but produces noise)."""
    null_rate: float = 0.0           # fraction of recent ticks with no output
    diversity: float = 0.0           # diversity of new outputs (0-1)
    downstream_consumption: float = 0.0  # ratio of outputs consumed downstream (0-1)
    novelty: float = 0.0             # ratio of outputs new vs. recent history (0-1)
    extras: dict = field(default_factory=dict)

    def composite(self, weights: Optional[dict] = None) -> float:
        """Composite health score in [0, 1]. Higher = healthier.

        Default weights bias toward consumption + novelty + diversity, with
        null_rate as a penalty. Tunable per agent."""
        w = weights or {
            "null_rate": -0.3,       # penalty
            "diversity": 0.25,
            "downstream_consumption": 0.30,
            "novelty": 0.15,
        }
        score = (
            w["null_rate"] * self.null_rate
            + w["diversity"] * self.diversity
            + w["downstream_consumption"] * self.downstream_consumption
            + w["novelty"] * self.novelty
        )
        # Re-center to [0, 1] roughly
        return max(0.0, min(1.0, 0.5 + score))


@dataclass
class Experiment:
    """One adaptation attempt with baseline + outcome."""
    experiment_id: str
    adaptation_name: str
    started_at: str
    baseline_health: float
    baseline_composite: dict      # full HealthSample as dict
    snapshot: Any = None          # opaque revert payload from apply()
    post_health: Optional[float] = None
    post_composite: Optional[dict] = None
    outcome: str = "running"      # 'running' | 'kept' | 'reverted' | 'aborted'
    finished_at: Optional[str] = None
    notes: str = ""


# ---------------------------------------------------------------------------
# The mixin
# ---------------------------------------------------------------------------

class SelfImprovingDaemon:
    """Mixin. Subclasses inherit + provide ADAPTATION_MENU + measure_health()."""

    # Subclasses override:
    ADAPTATION_MENU: list[Adaptation] = []
    HEALTH_WINDOW_TICKS: int = 10
    STAGNATION_THRESHOLD: float = 0.35           # composite below this = stagnant
    EXPERIMENT_OBSERVATION_TICKS: int = 3
    MAX_MUTATIONS_PER_DAY: int = 5
    HEALTH_WEIGHTS: Optional[dict] = None        # passed to HealthSample.composite

    # Self-summon target inbox (for escalation when menu exhausted)
    SELF_SUMMON_INBOX_PATH: Optional[Path] = None
    AGENT_NAME_FOR_TICKETS: str = "unknown_agent"

    # ---- subclass surface ---------------------------------------------------

    def measure_health(self, tick_stats: dict, agent_state: dict) -> HealthSample:
        """REQUIRED. Compute a HealthSample from recent tick activity."""
        raise NotImplementedError

    def detect_stagnation(self, health: HealthSample) -> bool:
        """OPTIONAL override. Default: composite < STAGNATION_THRESHOLD."""
        return health.composite(self.HEALTH_WEIGHTS) < self.STAGNATION_THRESHOLD

    # ---- driver -------------------------------------------------------------

    def run_self_improvement_cycle(
        self,
        tick_stats: dict,
        agent_state: dict,
        shared_state_path: Path,
    ) -> dict:
        """Call this from inside your tick. Returns a dict describing what
        the self-improvement layer did this tick (or skipped)."""
        result = {"action": "skipped", "reason": None}
        si_state = _load_si_state(shared_state_path)

        # Measure health every tick
        health = self.measure_health(tick_stats, agent_state)
        composite = health.composite(self.HEALTH_WEIGHTS)
        si_state["health_history"].append({
            "at": datetime.now(timezone.utc).isoformat(),
            "composite": composite,
            "raw": asdict(health),
        })
        # Keep only the last HEALTH_WINDOW_TICKS samples
        si_state["health_history"] = si_state["health_history"][-self.HEALTH_WINDOW_TICKS:]

        # If an experiment is in flight, observe it
        if si_state.get("running_experiment"):
            result = self._observe_running_experiment(
                si_state, composite, asdict(health), agent_state)
            _save_si_state(shared_state_path, si_state)
            return result

        # No experiment in flight — should we start one?
        if not self.detect_stagnation(health):
            result = {"action": "skipped", "reason": "healthy"}
            _save_si_state(shared_state_path, si_state)
            return result

        # Stagnant. Check mutation budget.
        if self._mutations_today(si_state) >= self.MAX_MUTATIONS_PER_DAY:
            result = {"action": "skipped",
                      "reason": "daily_mutation_budget_exhausted"}
            _save_si_state(shared_state_path, si_state)
            return result

        # Pick an adaptation
        adaptation = self._pick_next_adaptation(si_state)
        if adaptation is None:
            # Menu exhausted (gen-N wall). Self-summon.
            self._emit_self_summon_ticket(si_state)
            si_state["last_escalation_at"] = datetime.now(timezone.utc).isoformat()
            result = {"action": "self_summon_emitted",
                      "reason": "adaptation_menu_exhausted_under_stagnation"}
            _save_si_state(shared_state_path, si_state)
            return result

        if adaptation.requires_human_approval:
            self._emit_approval_request_ticket(adaptation, si_state)
            result = {"action": "approval_requested",
                      "adaptation": adaptation.name}
            _save_si_state(shared_state_path, si_state)
            return result

        # Apply the adaptation
        snapshot = None
        try:
            snapshot = adaptation.apply(self, agent_state)
        except Exception as e:
            log.error(f"adaptation {adaptation.name} failed to apply: {e}")
            si_state["failed_adaptations"].append({
                "name": adaptation.name, "error": str(e),
                "at": datetime.now(timezone.utc).isoformat(),
            })
            _save_si_state(shared_state_path, si_state)
            return {"action": "apply_failed", "adaptation": adaptation.name,
                    "error": str(e)}

        experiment = Experiment(
            experiment_id=f"exp_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
            adaptation_name=adaptation.name,
            started_at=datetime.now(timezone.utc).isoformat(),
            baseline_health=composite,
            baseline_composite=asdict(health),
            snapshot=snapshot,
        )
        si_state["running_experiment"] = asdict(experiment)
        si_state["mutation_log"].append({
            "applied_at": experiment.started_at,
            "adaptation": adaptation.name,
            "baseline_health": composite,
        })
        adaptation.last_applied_at = experiment.started_at
        adaptation.apply_count += 1

        _save_si_state(shared_state_path, si_state)
        return {
            "action": "experiment_started",
            "adaptation": adaptation.name,
            "experiment_id": experiment.experiment_id,
            "baseline_health": composite,
        }

    # ---- internals ----------------------------------------------------------

    def _observe_running_experiment(
        self, si_state: dict, current_composite: float,
        current_raw: dict, agent_state: dict,
    ) -> dict:
        exp = si_state["running_experiment"]
        exp.setdefault("observation_ticks", 0)
        exp["observation_ticks"] += 1
        if exp["observation_ticks"] < self.EXPERIMENT_OBSERVATION_TICKS:
            return {"action": "observing",
                    "experiment_id": exp["experiment_id"],
                    "ticks_remaining": self.EXPERIMENT_OBSERVATION_TICKS - exp["observation_ticks"]}

        # Done observing. Compare.
        exp["post_health"] = current_composite
        exp["post_composite"] = current_raw
        exp["finished_at"] = datetime.now(timezone.utc).isoformat()
        delta = current_composite - exp["baseline_health"]
        # Find the adaptation object
        adaptation = next((a for a in self.ADAPTATION_MENU
                           if a.name == exp["adaptation_name"]), None)
        keep = delta > 0.05  # require meaningful improvement
        if keep:
            exp["outcome"] = "kept"
        else:
            exp["outcome"] = "reverted"
            if adaptation and adaptation.revert:
                try:
                    adaptation.revert(self, agent_state, exp.get("snapshot"))
                except Exception as e:
                    exp["outcome"] = "revert_failed"
                    exp["notes"] = f"revert raised: {e}"

        # Update mutation log
        for entry in si_state["mutation_log"]:
            if entry.get("applied_at") == exp["started_at"]:
                entry["outcome"] = exp["outcome"]
                entry["delta"] = delta
                entry["finished_at"] = exp["finished_at"]
                break

        # Archive + clear
        si_state.setdefault("completed_experiments", []).append(exp)
        si_state["running_experiment"] = None

        return {"action": "experiment_concluded",
                "experiment_id": exp["experiment_id"],
                "adaptation": exp["adaptation_name"],
                "outcome": exp["outcome"],
                "delta": delta}

    def _pick_next_adaptation(self, si_state: dict) -> Optional[Adaptation]:
        """Pick the next adaptation to try.

        Strategy: prefer never-tried; then prefer cheap; then prefer
        not-recently-applied. Returns None if the menu is fully exhausted
        recently (gen-N wall hit)."""
        tried_recently: set = set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        for entry in si_state.get("mutation_log", [])[-50:]:
            try:
                applied_dt = datetime.fromisoformat(entry["applied_at"].replace("Z", "+00:00"))
                if applied_dt > cutoff:
                    tried_recently.add(entry["adaptation"])
            except Exception:
                continue

        cost_order = {"zero": 0, "trivial": 1, "one_tick": 2,
                      "medium": 3, "high": 4}
        # Prefer untried + cheap
        candidates = [a for a in self.ADAPTATION_MENU if a.name not in tried_recently]
        if candidates:
            candidates.sort(key=lambda a: cost_order.get(a.cost, 99))
            return candidates[0]
        # All tried recently. Wall.
        return None

    def _mutations_today(self, si_state: dict) -> int:
        today = datetime.now(timezone.utc).date()
        n = 0
        for entry in si_state.get("mutation_log", []):
            try:
                dt = datetime.fromisoformat(entry["applied_at"].replace("Z", "+00:00"))
                if dt.date() == today:
                    n += 1
            except Exception:
                continue
        return n

    def _emit_self_summon_ticket(self, si_state: dict) -> None:
        """When the menu is exhausted under stagnation, file a ticket to
        the configured inbox. This is the agent saying:
            'I tried everything I know; I'm still stagnant; here's the
             evidence; please intervene or retire me.'"""
        if not self.SELF_SUMMON_INBOX_PATH:
            log.warning(f"{self.AGENT_NAME_FOR_TICKETS}: menu exhausted but "
                        f"no SELF_SUMMON_INBOX_PATH configured")
            return
        ticket = {
            "id": f"T-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{self.AGENT_NAME_FOR_TICKETS}-self-summon",
            "source": self.AGENT_NAME_FOR_TICKETS,
            "target": "aporia",
            "type": "self-improvement-menu-exhausted",
            "priority": "P2-medium",
            "title": f"{self.AGENT_NAME_FOR_TICKETS}: adaptation menu exhausted under stagnation",
            "payload": {
                "agent": self.AGENT_NAME_FOR_TICKETS,
                "health_history": si_state.get("health_history", [])[-10:],
                "completed_experiments": si_state.get("completed_experiments", [])[-20:],
                "current_menu_size": len(self.ADAPTATION_MENU),
                "ask": (
                    "I have run through my adaptation menu without breaking stagnation. "
                    "Options for the next move: (a) extend my menu with new adaptations, "
                    "(b) author a child agent with mutated charter (generational handoff), "
                    "(c) retire me. Decide and reply via this inbox."
                ),
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.AGENT_NAME_FOR_TICKETS,
            "status": "OPEN",
        }
        try:
            self.SELF_SUMMON_INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
            with self.SELF_SUMMON_INBOX_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ticket, ensure_ascii=False) + "\n")
            log.warning(f"{self.AGENT_NAME_FOR_TICKETS}: self-summon ticket filed "
                        f"to {self.SELF_SUMMON_INBOX_PATH}")
        except Exception as e:
            log.error(f"self-summon ticket emission failed: {e}")

    def _emit_approval_request_ticket(self, adaptation: Adaptation,
                                      si_state: dict) -> None:
        """For adaptations marked requires_human_approval. Same shape as
        self-summon but a different type."""
        if not self.SELF_SUMMON_INBOX_PATH:
            return
        ticket = {
            "id": f"T-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{self.AGENT_NAME_FOR_TICKETS}-approval-{adaptation.name}",
            "source": self.AGENT_NAME_FOR_TICKETS,
            "target": "aporia",
            "type": "self-improvement-approval-request",
            "priority": "P2-medium",
            "title": f"{self.AGENT_NAME_FOR_TICKETS}: requesting approval to apply {adaptation.name}",
            "payload": {
                "agent": self.AGENT_NAME_FOR_TICKETS,
                "adaptation": adaptation.name,
                "description": adaptation.description,
                "cost": adaptation.cost,
                "reversibility": adaptation.reversibility,
                "recent_health": si_state.get("health_history", [])[-5:],
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.AGENT_NAME_FOR_TICKETS,
            "status": "OPEN",
        }
        try:
            self.SELF_SUMMON_INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
            with self.SELF_SUMMON_INBOX_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ticket, ensure_ascii=False) + "\n")
        except Exception as e:
            log.error(f"approval-request ticket emission failed: {e}")


# ---------------------------------------------------------------------------
# State persistence (kept separate from the agent's own state.json)
# ---------------------------------------------------------------------------

def _default_si_state() -> dict:
    return {
        "schema_version": 1,
        "first_si_cycle_at": datetime.now(timezone.utc).isoformat(),
        "health_history": [],          # list of {at, composite, raw}
        "mutation_log": [],            # list of {applied_at, adaptation, outcome, delta}
        "running_experiment": None,    # active Experiment dict or None
        "completed_experiments": [],   # archived Experiment dicts
        "failed_adaptations": [],      # adaptations whose apply() raised
        "last_escalation_at": None,    # when self_summon was last fired
    }


def _load_si_state(path: Path) -> dict:
    if not path.exists():
        return _default_si_state()
    try:
        s = json.loads(path.read_text(encoding="utf-8"))
        for k, v in _default_si_state().items():
            s.setdefault(k, v)
        return s
    except Exception:
        return _default_si_state()


def _save_si_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)
