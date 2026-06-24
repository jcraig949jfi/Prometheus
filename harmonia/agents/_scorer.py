"""
Harmonia auto-promotion scoring primitive.

Three-tier ranking pipeline shared across the five Harmonia child-agents
(Phylax, Sophia, Iris, Argos, Telos). Per the v0.2 spec at
`D:\\Prometheus\\harmonia\\agents\\AUTOPROMOTION_TARGETS.md`.

Tier 0  Cheap hard-filter pre-filter (per-pipeline regex / type-check /
        recency-collision / template-suppression). VETO power: Tier 0
        always overrides Tier 1 + Tier 2 recommendations.

Tier 1  Transparent hand-scored rank (Phase 1) -> learned model (Phase 3+).
        Per-pipeline deterministic scoring rule in Phase 1.

Tier 2  Epsilon-greedy bandit allocation (active from Phase 1 with
        explicit risk-mitigation: high initial explore rate, multi-objective
        reward signal, per-pipeline isolation, forced exploration of
        stagnant arms, daily anchor pull-in, confidence-bound exposure,
        Tier 0 veto). Recommendation never overrides hard filters.

This module also owns the swarm-wide event-emission helper (`emit_event`)
and the yield-log writer (`append_yield_row`). Every Phase 0 tool consumes
this interface.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, Iterable

_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = _THIS_FILE.parents[2]
AGENTS_DIR = REPO_ROOT / "harmonia" / "agents"
LOGS_DIR = AGENTS_DIR / "_logs"
YIELDS_JSONL = LOGS_DIR / "yields.jsonl"
EVENTS_JSONL = LOGS_DIR / "events.jsonl"

# Ensure log dir exists at import time so subprocess writes don't race
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome classes (yield-log; 7 classes per spec §6.5)
# ---------------------------------------------------------------------------

OUTCOME_ACCEPTED_HUMAN = "accepted_human"
OUTCOME_ACCEPTED_DOWNSTREAM_USE = "accepted_downstream_use"
OUTCOME_SURVIVED_TTL_UNREVIEWED = "survived_ttl_unreviewed"
OUTCOME_DISMISSED_HUMAN = "dismissed_human"
OUTCOME_AUTO_RETRACTED = "auto_retracted"
OUTCOME_CONTRADICTED = "contradicted"
OUTCOME_STALE_UNCONSUMED = "stale_unconsumed"

OUTCOME_CLASSES = {
    OUTCOME_ACCEPTED_HUMAN,
    OUTCOME_ACCEPTED_DOWNSTREAM_USE,
    OUTCOME_SURVIVED_TTL_UNREVIEWED,
    OUTCOME_DISMISSED_HUMAN,
    OUTCOME_AUTO_RETRACTED,
    OUTCOME_CONTRADICTED,
    OUTCOME_STALE_UNCONSUMED,
}

# Per spec §6.5: scorer trains ONLY on these outcomes as positives.
POSITIVE_OUTCOMES = {
    OUTCOME_ACCEPTED_HUMAN,
    OUTCOME_ACCEPTED_DOWNSTREAM_USE,
}

# These count as losses for win/loss ratio and bandit reward.
NEGATIVE_OUTCOMES = {
    OUTCOME_DISMISSED_HUMAN,
    OUTCOME_AUTO_RETRACTED,
    OUTCOME_CONTRADICTED,
}

# TTL-survival is explicitly NOT a positive (anti-Goodhart, per spec §6.5).
NEUTRAL_OUTCOMES = {
    OUTCOME_SURVIVED_TTL_UNREVIEWED,
    OUTCOME_STALE_UNCONSUMED,
}


# ---------------------------------------------------------------------------
# Event classes (events.jsonl; 19 classes per spec §4.5)
# ---------------------------------------------------------------------------

EVENT_TICK_START = "tick_start"
EVENT_TICK_COMPLETE = "tick_complete"
EVENT_TIER0_REJECT = "tier0_reject"
EVENT_TIER1_SCORED = "tier1_scored"
EVENT_BANDIT_ARM_PULLED = "bandit_arm_pulled"
EVENT_AUTOPROMOTE_PROPOSED = "autopromote_proposed"
EVENT_AUTOPROMOTE_COMMITTED = "autopromote_committed"
EVENT_AUTOPROMOTE_ABORTED = "autopromote_aborted"
EVENT_KILL_PATH_WRITTEN = "kill_path_written"
EVENT_TAINT_SCOPE_WRITTEN = "taint_scope_written"
EVENT_OUTCOME_OBSERVED = "outcome_observed"
EVENT_MARGINAL_VALUE_ASSIGNED = "marginal_value_assigned"
EVENT_RETRACTION_TRIGGERED = "retraction_triggered"
EVENT_TAINT_SWEEP_STARTED = "taint_sweep_started"
EVENT_TAINT_SWEEP_COMPLETE = "taint_sweep_complete"
EVENT_DOCTRINE_VERSION_CHECK = "doctrine_version_check"
EVENT_CALIBRATION_RUN = "calibration_run"
EVENT_SCORER_SELF_QUIESCE = "scorer_self_quiesce"
EVENT_WEEKLY_REPORT_EMITTED = "weekly_report_emitted"

EVENT_CLASSES = {
    EVENT_TICK_START, EVENT_TICK_COMPLETE,
    EVENT_TIER0_REJECT, EVENT_TIER1_SCORED, EVENT_BANDIT_ARM_PULLED,
    EVENT_AUTOPROMOTE_PROPOSED, EVENT_AUTOPROMOTE_COMMITTED,
    EVENT_AUTOPROMOTE_ABORTED,
    EVENT_KILL_PATH_WRITTEN, EVENT_TAINT_SCOPE_WRITTEN,
    EVENT_OUTCOME_OBSERVED, EVENT_MARGINAL_VALUE_ASSIGNED,
    EVENT_RETRACTION_TRIGGERED,
    EVENT_TAINT_SWEEP_STARTED, EVENT_TAINT_SWEEP_COMPLETE,
    EVENT_DOCTRINE_VERSION_CHECK,
    EVENT_CALIBRATION_RUN, EVENT_SCORER_SELF_QUIESCE,
    EVENT_WEEKLY_REPORT_EMITTED,
}

EVENT_SCHEMA_VERSION = "events.v1"
YIELD_SCHEMA_VERSION = "yields.v1"


# ---------------------------------------------------------------------------
# Redis client (lazy, shared, optional)
# ---------------------------------------------------------------------------

_REDIS = None
_REDIS_ATTEMPTED = False
HARMONIA_EVENTS_STREAM = "agora:harmonia_events"


def _redis_client():
    global _REDIS, _REDIS_ATTEMPTED
    if _REDIS_ATTEMPTED:
        return _REDIS
    _REDIS_ATTEMPTED = True
    try:
        from thesauros.prometheus_data import get_bus  # type: ignore
        host = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
        port = int(os.environ.get("AGORA_REDIS_PORT", 6379))
        password = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
        _REDIS = get_bus(decode_responses=True)
        _REDIS.ping()
    except Exception:
        _REDIS = None
    return _REDIS


# ---------------------------------------------------------------------------
# emit_event — the swarm-wide structured-event helper
# ---------------------------------------------------------------------------

def emit_event(
    event_class: str,
    event_data: dict,
    agent: Optional[str] = None,
    tick_id: Optional[str] = None,
    artifact_id: Optional[str] = None,
    yield_id: Optional[str] = None,
    ts: Optional[str] = None,
) -> bool:
    """Write a structured event to events.jsonl AND the agora Redis stream.

    Both writes are best-effort and graceful-degrading. Returns True iff
    at least one of the two channels accepted the event.

    Any tool in the Harmonia pipeline -- current or future -- emits events
    via this helper. See spec §4.5 for the event-class catalog.
    """
    if event_class not in EVENT_CLASSES:
        # Log a warning but don't reject — better to over-record than to
        # silently drop a novel event type. The catalog is the source of
        # truth but extensibility is allowed.
        print(
            f"[emit_event] WARNING: unknown event_class '{event_class}' "
            f"(allowed: {sorted(EVENT_CLASSES)})",
            file=sys.stderr,
        )

    row = {
        "ts": ts or datetime.now(timezone.utc).isoformat(),
        "agent": agent or "unknown",
        "event_class": event_class,
        "event_data": event_data or {},
        "correlation_ids": {
            "tick_id": tick_id,
            "artifact_id": artifact_id,
            "yield_id": yield_id,
        },
        "schema_version": EVENT_SCHEMA_VERSION,
    }

    wrote_disk = False
    try:
        EVENTS_JSONL.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENTS_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
        wrote_disk = True
    except Exception as e:
        print(f"[emit_event] disk write failed: {e}", file=sys.stderr)

    wrote_redis = False
    r = _redis_client()
    if r is not None:
        try:
            # XADD with flattened payload (Redis streams don't accept nested
            # dicts directly). We keep the full row in a `_json` field so
            # consumers can reconstruct.
            r.xadd(
                HARMONIA_EVENTS_STREAM,
                {"_json": json.dumps(row, default=str)},
                maxlen=10000,  # bounded stream
                approximate=True,
            )
            wrote_redis = True
        except Exception:
            pass

    return wrote_disk or wrote_redis


# ---------------------------------------------------------------------------
# Yield-log writer + reader
# ---------------------------------------------------------------------------

def append_yield_row(
    agent: str,
    artifact_path: str,
    action: str,
    auto_promote_score: float,
    tier1_method: str,
    kill_path: str,
    taint_scope: dict,
    doctrine_version: Optional[str] = None,
    outcome: Optional[str] = None,
    outcome_observed_at: Optional[str] = None,
    marginal_substrate_value: Optional[int] = None,
    yield_id: Optional[str] = None,
    extra: Optional[dict] = None,
) -> str:
    """Append a yield row to yields.jsonl. Returns the assigned yield_id.

    Required fields are enforced. Optional fields (outcome, marginal value)
    are typically filled in retrospectively by the review tool.

    Taint-scope shape (per spec §6.4):
        {
            "readable_by_agents": [str, ...],
            "downstream_slots": [str, ...],
            "used_for_training": bool,
            "recency_keys_written": [str, ...],
            "requires_taint_sweep_on_retract": bool,
            "cross_swarm_consumers": [str, ...] (optional)
        }
    """
    yid = yield_id or f"y-{uuid.uuid4().hex[:12]}"
    if outcome is not None and outcome not in OUTCOME_CLASSES:
        raise ValueError(f"unknown outcome '{outcome}'; allowed: {OUTCOME_CLASSES}")
    if marginal_substrate_value is not None:
        if not isinstance(marginal_substrate_value, int):
            raise ValueError("marginal_substrate_value must be int 0-5")
        if not (0 <= marginal_substrate_value <= 5):
            raise ValueError("marginal_substrate_value must be in [0, 5]")

    row = {
        "yield_id": yid,
        "agent": agent,
        "artifact_path": artifact_path,
        "action": action,
        "action_at": datetime.now(timezone.utc).isoformat(),
        "auto_promote_score": float(auto_promote_score),
        "tier1_method": tier1_method,
        "kill_path": kill_path,
        "taint_scope": taint_scope,
        "doctrine_version": doctrine_version,
        "outcome": outcome,
        "outcome_observed_at": outcome_observed_at,
        "marginal_substrate_value": marginal_substrate_value,
        "extra": extra or {},
        "schema_version": YIELD_SCHEMA_VERSION,
    }
    try:
        YIELDS_JSONL.parent.mkdir(parents=True, exist_ok=True)
        with open(YIELDS_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception as e:
        print(f"[append_yield_row] disk write failed: {e}", file=sys.stderr)
    return yid


def read_yields(
    since_iso: Optional[str] = None,
    agent: Optional[str] = None,
    outcomes: Optional[Iterable[str]] = None,
) -> list[dict]:
    """Read yield rows from yields.jsonl, optionally filtered by time/agent/outcome."""
    if not YIELDS_JSONL.exists():
        return []
    out: list[dict] = []
    cutoff = None
    if since_iso:
        try:
            cutoff = datetime.fromisoformat(since_iso)
        except Exception:
            cutoff = None
    outcomes_set = set(outcomes) if outcomes else None
    try:
        with open(YIELDS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if agent is not None and r.get("agent") != agent:
                    continue
                if outcomes_set is not None and r.get("outcome") not in outcomes_set:
                    continue
                if cutoff is not None:
                    try:
                        rts = datetime.fromisoformat(r["action_at"])
                        if rts < cutoff:
                            continue
                    except Exception:
                        pass
                out.append(r)
    except Exception as e:
        print(f"[read_yields] read failed: {e}", file=sys.stderr)
    return out


def update_yield_outcome(
    yield_id: str,
    outcome: str,
    marginal_substrate_value: Optional[int] = None,
) -> bool:
    """Append a yield-update row that supersedes the original on outcome.

    yields.jsonl is append-only -- updates are new rows with the same
    yield_id, an `action` of 'outcome_update', and the new outcome field.
    The latest row per yield_id is the authoritative state. Readers
    consolidate by reading the full log and keeping the most recent
    row per yield_id.
    """
    if outcome not in OUTCOME_CLASSES:
        raise ValueError(f"unknown outcome '{outcome}'")
    if marginal_substrate_value is not None:
        if not isinstance(marginal_substrate_value, int):
            raise ValueError("marginal_substrate_value must be int 0-5")
        if not (0 <= marginal_substrate_value <= 5):
            raise ValueError("marginal_substrate_value must be in [0, 5]")
    row = {
        "yield_id": yield_id,
        "agent": None,  # filled-in retrospectively; the original row is canonical
        "action": "outcome_update",
        "action_at": datetime.now(timezone.utc).isoformat(),
        "outcome": outcome,
        "outcome_observed_at": datetime.now(timezone.utc).isoformat(),
        "marginal_substrate_value": marginal_substrate_value,
        "schema_version": YIELD_SCHEMA_VERSION,
    }
    try:
        with open(YIELDS_JSONL, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
        # Also emit structured events
        emit_event(EVENT_OUTCOME_OBSERVED, {"outcome": outcome}, yield_id=yield_id)
        if marginal_substrate_value is not None:
            emit_event(
                EVENT_MARGINAL_VALUE_ASSIGNED,
                {"value": marginal_substrate_value},
                yield_id=yield_id,
            )
        return True
    except Exception as e:
        print(f"[update_yield_outcome] failed: {e}", file=sys.stderr)
        return False


def consolidate_yields(rows: list[dict]) -> dict[str, dict]:
    """Reduce append-only log into the latest-state-per-yield-id dict.

    The original row provides canonical agent / artifact_path / kill_path /
    taint_scope etc. Subsequent outcome_update rows supersede outcome and
    marginal_substrate_value only.
    """
    by_id: dict[str, dict] = {}
    for r in rows:
        yid = r.get("yield_id")
        if not yid:
            continue
        if yid not in by_id:
            by_id[yid] = dict(r)
        else:
            if r.get("action") == "outcome_update":
                if r.get("outcome") is not None:
                    by_id[yid]["outcome"] = r["outcome"]
                    by_id[yid]["outcome_observed_at"] = r.get("outcome_observed_at")
                if r.get("marginal_substrate_value") is not None:
                    by_id[yid]["marginal_substrate_value"] = r["marginal_substrate_value"]
    return by_id


# ---------------------------------------------------------------------------
# Epsilon-greedy bandit (Tier 2)
# ---------------------------------------------------------------------------

@dataclass
class ArmStats:
    """Per-arm bandit statistics. An "arm" is a (candidate-class, key) tuple
    that an agent recognizes -- e.g., for Iris, an arm might be a candidate
    cluster fingerprint; for Argos, a (problem_domain, lens_stack) tuple.

    The arm key is opaque to the bandit; the agent decides what counts as
    an arm. The bandit tracks pull-count and reward distribution per arm.
    """
    key: str
    pull_count: int = 0
    total_reward: float = 0.0
    sum_sq_reward: float = 0.0
    last_pulled_at: Optional[str] = None
    last_reward: Optional[float] = None

    @property
    def mean_reward(self) -> float:
        return self.total_reward / self.pull_count if self.pull_count > 0 else 0.0

    @property
    def reward_std(self) -> float:
        if self.pull_count <= 1:
            return float("inf")
        mean = self.mean_reward
        return math.sqrt(max(0.0, self.sum_sq_reward / self.pull_count - mean ** 2))

    @property
    def confidence_radius(self) -> float:
        """UCB1-style confidence radius. Lower pull-count = wider radius."""
        if self.pull_count == 0:
            return float("inf")
        return 1.96 * (self.reward_std / math.sqrt(self.pull_count)
                       if self.reward_std != float("inf") else 1.0 / math.sqrt(self.pull_count))


class EpsilonGreedyBandit:
    """Per-pipeline bandit with the seven risk-mitigation behaviors from
    spec §4.1:

      1. High initial explore rate (epsilon=0.50 -> 0.10 over pull-count)
      2. Multi-objective reward signal (marginal_value - taint_cost - retraction_penalty)
      3. Per-pipeline isolation (each pipeline owns its own instance)
      4. Forced exploration of arms not pulled in 14 days
      5. Calibration anchor pull-in (daily, handled by external watchdog)
      6. Confidence-bound exposure (every pick emits a bandit_arm_pulled event)
      7. Tier 0 veto (bandit recommendation can be overridden; pick() returns
         the recommendation but the caller still gates it through Tier 0)

    State is persisted to harmonia/agents/<pipeline_name>/state/bandit.json.
    """

    EPSILON_INITIAL = 0.50
    EPSILON_FLOOR = 0.10
    EPSILON_TRANSITIONS = (
        # (pulls_total_below, epsilon)
        (50, 0.50),
        (100, 0.30),
        (200, 0.20),
        (500, 0.10),
    )
    STAGNANT_DAYS = 14
    TAINT_COST_WEIGHT = 0.10  # per (readable_by_agents x downstream_slots) cardinality
    RETRACTION_PENALTY = 2.0  # subtracted from reward on auto_retract / contradicted

    def __init__(self, pipeline_name: str, state_dir: Optional[Path] = None):
        self.pipeline_name = pipeline_name
        if state_dir is None:
            state_dir = AGENTS_DIR / pipeline_name / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        self._state_path = state_dir / "bandit.json"
        self._arms: dict[str, ArmStats] = {}
        self._load()

    def _load(self) -> None:
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            for key, stats_dict in data.get("arms", {}).items():
                self._arms[key] = ArmStats(**stats_dict)
        except Exception as e:
            print(f"[Bandit {self.pipeline_name}] load failed: {e}", file=sys.stderr)

    def _save(self) -> None:
        try:
            data = {
                "pipeline_name": self.pipeline_name,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "arms": {k: asdict(v) for k, v in self._arms.items()},
            }
            self._state_path.write_text(
                json.dumps(data, indent=2, default=str),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[Bandit {self.pipeline_name}] save failed: {e}", file=sys.stderr)

    @property
    def total_pulls(self) -> int:
        return sum(a.pull_count for a in self._arms.values())

    @property
    def epsilon(self) -> float:
        """Decay epsilon based on total pull-count across all arms."""
        t = self.total_pulls
        for cutoff, eps in self.EPSILON_TRANSITIONS:
            if t < cutoff:
                return eps
        return self.EPSILON_FLOOR

    def _stagnant_arm(self) -> Optional[ArmStats]:
        """Find an arm that hasn't been pulled in STAGNANT_DAYS, if any.

        Forced-exploration mitigation (mitigation #4). The first stagnant
        arm found is returned; the caller force-pulls it.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.STAGNANT_DAYS)
        for arm in self._arms.values():
            if arm.last_pulled_at is None:
                continue
            try:
                last = datetime.fromisoformat(arm.last_pulled_at)
                if last < cutoff:
                    return arm
            except Exception:
                continue
        return None

    def pick(
        self,
        candidates: list[dict],
        arm_key_fn,
        tick_id: Optional[str] = None,
    ) -> tuple[Optional[dict], dict]:
        """Pick one candidate per bandit policy.

        `arm_key_fn(candidate) -> str` is provided by the calling pipeline
        and defines what constitutes an arm. For Iris this might be the
        fingerprint slug; for Argos the problem-domain string; etc.

        Returns (chosen_candidate, bandit_metadata). bandit_metadata is
        suitable for inclusion in the autopromote_committed yield row and
        is also emitted as a bandit_arm_pulled event.
        """
        if not candidates:
            return None, {"reason": "empty_candidate_list"}

        # Register any new arms before deciding
        for c in candidates:
            key = arm_key_fn(c)
            if key not in self._arms:
                self._arms[key] = ArmStats(key=key)

        # (4) Forced exploration of stagnant arms
        stagnant = self._stagnant_arm()
        if stagnant is not None:
            # Pick the candidate (if any) whose arm matches the stagnant one
            for c in candidates:
                if arm_key_fn(c) == stagnant.key:
                    meta = self._record_pick(c, arm_key_fn, mode="forced_exploration", tick_id=tick_id)
                    return c, meta

        # (1) Epsilon-greedy
        if random.random() < self.epsilon:
            chosen = random.choice(candidates)
            meta = self._record_pick(chosen, arm_key_fn, mode="explore", tick_id=tick_id)
            return chosen, meta

        # Exploit: pick the candidate whose arm has highest mean reward.
        # Ties broken by UCB-style confidence boost so under-sampled arms
        # surface sooner.
        def score(c):
            key = arm_key_fn(c)
            arm = self._arms[key]
            mean = arm.mean_reward
            # UCB1-style exploration boost for low-pull-count arms
            n = arm.pull_count
            t = max(1, self.total_pulls)
            ucb_boost = math.sqrt(2 * math.log(t) / n) if n > 0 else float("inf")
            return mean + 0.5 * ucb_boost

        ranked = sorted(candidates, key=score, reverse=True)
        chosen = ranked[0]
        meta = self._record_pick(chosen, arm_key_fn, mode="exploit", tick_id=tick_id)
        return chosen, meta

    def _record_pick(self, candidate, arm_key_fn, mode: str, tick_id: Optional[str]) -> dict:
        key = arm_key_fn(candidate)
        arm = self._arms[key]
        meta = {
            "pipeline": self.pipeline_name,
            "arm_key": key,
            "mode": mode,
            "epsilon": self.epsilon,
            "arm_pull_count": arm.pull_count,
            "arm_mean_reward": arm.mean_reward,
            "arm_confidence_radius": (
                arm.confidence_radius if math.isfinite(arm.confidence_radius) else None
            ),
            "total_pulls": self.total_pulls,
        }
        emit_event(
            EVENT_BANDIT_ARM_PULLED,
            meta,
            agent=self.pipeline_name,
            tick_id=tick_id,
        )
        return meta

    def record_reward(
        self,
        arm_key: str,
        marginal_substrate_value: Optional[int],
        taint_scope: Optional[dict] = None,
        outcome: Optional[str] = None,
    ) -> float:
        """Compute multi-objective reward and update arm stats.

        Reward = marginal_substrate_value
               - taint_cost_penalty
               - retraction_penalty_if_subsequently_retracted

        (mitigation #2). Returns the actual reward applied for downstream
        observability.
        """
        # (2) Multi-objective reward signal
        if marginal_substrate_value is None:
            # No human label yet -- use a neutral prior
            base = 0.0
        else:
            base = float(marginal_substrate_value)

        taint_cost = 0.0
        if taint_scope is not None:
            readable = taint_scope.get("readable_by_agents") or []
            slots = taint_scope.get("downstream_slots") or []
            cross_swarm = taint_scope.get("cross_swarm_consumers") or []
            cardinality = len(readable) * len(slots) + 2 * len(cross_swarm)
            taint_cost = self.TAINT_COST_WEIGHT * cardinality

        retraction_penalty = 0.0
        if outcome in (OUTCOME_AUTO_RETRACTED, OUTCOME_CONTRADICTED, OUTCOME_DISMISSED_HUMAN):
            retraction_penalty = self.RETRACTION_PENALTY

        reward = base - taint_cost - retraction_penalty

        arm = self._arms.get(arm_key)
        if arm is None:
            arm = ArmStats(key=arm_key)
            self._arms[arm_key] = arm
        arm.pull_count += 1
        arm.total_reward += reward
        arm.sum_sq_reward += reward ** 2
        arm.last_pulled_at = datetime.now(timezone.utc).isoformat()
        arm.last_reward = reward
        self._save()
        return reward

    def summary(self) -> dict:
        """Per-arm summary -- consumed by the weekly maturation report."""
        return {
            "pipeline_name": self.pipeline_name,
            "total_pulls": self.total_pulls,
            "epsilon": self.epsilon,
            "n_arms": len(self._arms),
            "arms": [
                {
                    "key": a.key,
                    "pull_count": a.pull_count,
                    "mean_reward": round(a.mean_reward, 4),
                    "last_pulled_at": a.last_pulled_at,
                    "last_reward": a.last_reward,
                }
                for a in sorted(self._arms.values(), key=lambda x: -x.pull_count)[:50]
            ],
        }


# ---------------------------------------------------------------------------
# HarmoniaScorer base class
# ---------------------------------------------------------------------------

@dataclass
class CandidateVerdict:
    """Output of HarmoniaScorer.evaluate() for one candidate."""
    candidate: dict
    tier0_pass: bool
    tier0_reject_reason: Optional[str]
    tier1_score: Optional[float]
    auto_promote: bool
    metadata: dict = field(default_factory=dict)


class HarmoniaScorer(ABC):
    """Three-tier ranking pipeline base class. Each agent's auto-promotion
    pipeline subclasses this to define its own Tier 0 hard-filter rules
    (tier0_filter) and Tier 1 transparent scoring rule (tier1_score).
    Tier 2 (bandit) is shared via composition.

    Subclasses must declare:
        name: str          # pipeline name, used for state dir + emit_event agent
        promote_threshold: float  # Tier 1 score >= threshold -> auto-promote

    Subclasses must implement:
        tier0_filter(candidate) -> (pass: bool, reject_reason: Optional[str])
        tier1_score(candidate) -> float
        arm_key(candidate) -> str  # for the bandit

    Subclasses get for free:
        evaluate_batch(candidates, k=1) -> list[CandidateVerdict]
            Applies Tier 0 (vetoes) -> Tier 1 (scores) -> Tier 2 (bandit pick
            among Tier 1 survivors). Returns up to k promote-eligible verdicts.
        emit_event(...)
        record_outcome(arm_key, outcome, marginal_value, taint_scope)
    """

    name: str = "BaseScorer"
    promote_threshold: float = 1.0

    def __init__(self):
        self.bandit = EpsilonGreedyBandit(self.name)

    @abstractmethod
    def tier0_filter(self, candidate: dict) -> tuple[bool, Optional[str]]:
        """Hand-crafted hard filters. Returns (pass, reject_reason)."""
        raise NotImplementedError

    @abstractmethod
    def tier1_score(self, candidate: dict) -> float:
        """Transparent hand-scored rank. Higher is better."""
        raise NotImplementedError

    @abstractmethod
    def arm_key(self, candidate: dict) -> str:
        """Bandit arm-key for this candidate."""
        raise NotImplementedError

    def evaluate_batch(
        self,
        candidates: list[dict],
        k: int = 1,
        tick_id: Optional[str] = None,
    ) -> list[CandidateVerdict]:
        """Apply Tier 0 -> Tier 1 -> Tier 2 in order. Returns up to k
        promote-eligible verdicts (those with auto_promote=True)."""
        if not candidates:
            return []
        if tick_id is None:
            tick_id = f"tick-{uuid.uuid4().hex[:12]}"

        # Tier 0
        survivors: list[CandidateVerdict] = []
        for c in candidates:
            t0_pass, t0_reason = self.tier0_filter(c)
            if not t0_pass:
                emit_event(
                    EVENT_TIER0_REJECT,
                    {"reason": t0_reason, "candidate_summary": _candidate_summary(c)},
                    agent=self.name,
                    tick_id=tick_id,
                )
                continue
            survivors.append(CandidateVerdict(
                candidate=c, tier0_pass=True, tier0_reject_reason=None,
                tier1_score=None, auto_promote=False,
            ))

        # Tier 1
        for v in survivors:
            score = self.tier1_score(v.candidate)
            v.tier1_score = score
            emit_event(
                EVENT_TIER1_SCORED,
                {"score": score, "candidate_summary": _candidate_summary(v.candidate)},
                agent=self.name,
                tick_id=tick_id,
            )

        # Filter to threshold-passing candidates
        promote_eligible = [v for v in survivors if v.tier1_score >= self.promote_threshold]
        if not promote_eligible:
            return []

        # Tier 2 (bandit)
        picks: list[CandidateVerdict] = []
        pool = list(promote_eligible)
        for _ in range(min(k, len(pool))):
            chosen, meta = self.bandit.pick(
                [v.candidate for v in pool],
                arm_key_fn=self.arm_key,
                tick_id=tick_id,
            )
            if chosen is None:
                break
            # Locate the CandidateVerdict for the chosen candidate
            for i, v in enumerate(pool):
                if v.candidate is chosen:
                    v.auto_promote = True
                    v.metadata["bandit"] = meta
                    picks.append(v)
                    pool.pop(i)
                    break
        return picks

    def record_outcome(
        self,
        arm_key: str,
        outcome: str,
        marginal_substrate_value: Optional[int] = None,
        taint_scope: Optional[dict] = None,
    ) -> float:
        """Forward an observed outcome to the bandit so future picks
        reflect the reward signal. Returns the actual reward applied."""
        return self.bandit.record_reward(
            arm_key=arm_key,
            marginal_substrate_value=marginal_substrate_value,
            taint_scope=taint_scope,
            outcome=outcome,
        )

    def quiesce(self, reason: str) -> None:
        """Pause this pipeline's auto-promotion until conductor review.
        Called by the daily calibration watchdog when drift is detected."""
        quiesce_flag = AGENTS_DIR / self.name / "state" / "quiesced.json"
        quiesce_flag.parent.mkdir(parents=True, exist_ok=True)
        quiesce_flag.write_text(json.dumps({
            "quiesced_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }, indent=2), encoding="utf-8")
        emit_event(EVENT_SCORER_SELF_QUIESCE, {"reason": reason}, agent=self.name)

    def is_quiesced(self) -> bool:
        flag = AGENTS_DIR / self.name / "state" / "quiesced.json"
        return flag.exists()


def _candidate_summary(c: dict) -> dict:
    """Strip a candidate dict down to safe-to-log fields (no big blobs)."""
    summary = {}
    for k in ("id", "slug", "name", "fingerprint", "problem_id", "fid",
              "operator", "specimen", "anchor"):
        if k in c:
            summary[k] = c[k]
    return summary


# ---------------------------------------------------------------------------
# Self-test (run with: python -m harmonia.agents._scorer)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Tiny smoke test: define a dummy scorer, evaluate a batch, record outcomes
    class DummyScorer(HarmoniaScorer):
        name = "dummy_smoketest"
        promote_threshold = 1.0

        def tier0_filter(self, c):
            if c.get("banned"):
                return False, "banned_keyword"
            return True, None

        def tier1_score(self, c):
            return float(c.get("score", 0.0))

        def arm_key(self, c):
            return c.get("category", "default")

    s = DummyScorer()
    candidates = [
        {"id": "a", "score": 2.5, "category": "alpha"},
        {"id": "b", "score": 0.5, "category": "alpha"},
        {"id": "c", "score": 3.0, "category": "beta", "banned": True},
        {"id": "d", "score": 1.2, "category": "gamma"},
    ]
    picks = s.evaluate_batch(candidates, k=2)
    print(f"picks: {[(p.candidate['id'], p.tier1_score) for p in picks]}")
    for p in picks:
        if p.metadata.get("bandit"):
            print(f"  bandit meta for {p.candidate['id']}: mode={p.metadata['bandit']['mode']} epsilon={p.metadata['bandit']['epsilon']:.2f}")
    # Simulate outcome
    if picks:
        s.record_outcome(
            arm_key=s.arm_key(picks[0].candidate),
            outcome=OUTCOME_ACCEPTED_HUMAN,
            marginal_substrate_value=3,
            taint_scope={"readable_by_agents": ["dummy"], "downstream_slots": ["test.md"]},
        )
        print(f"bandit summary: {s.bandit.summary()}")
    print(f"epsilon now: {s.bandit.epsilon}")
    # Smoke-test the yield + event log
    yid = append_yield_row(
        agent=s.name,
        artifact_path="smoketest/artifact.md",
        action="auto_promoted_to_test",
        auto_promote_score=2.5,
        tier1_method="rule-based-v0.2",
        kill_path="smoketest/kill.md",
        taint_scope={
            "readable_by_agents": ["dummy"],
            "downstream_slots": ["test.md"],
            "used_for_training": False,
            "recency_keys_written": ["dummy:smoketest"],
            "requires_taint_sweep_on_retract": False,
        },
        doctrine_version=None,
    )
    print(f"yield row written: {yid}")
    update_yield_outcome(yid, OUTCOME_ACCEPTED_HUMAN, marginal_substrate_value=3)
    rows = read_yields(agent=s.name)
    print(f"read back {len(rows)} yield rows for {s.name}")
    consolidated = consolidate_yields(rows)
    print(f"consolidated: {len(consolidated)} distinct yield_ids")
    for yid, row in consolidated.items():
        print(f"  {yid}: outcome={row.get('outcome')} mv={row.get('marginal_substrate_value')}")
