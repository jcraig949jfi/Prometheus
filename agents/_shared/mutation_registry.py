"""Cross-agent mutation registry (SelfImprovingDaemon v2a).

A shared registry that records every kept adaptation as a directional
pointer in mutation-space. The accumulated pointers form a lattice; the
voids in that lattice (unexplored productive mutations) become candidates
for later void-detection work (v2d).

Per James 2026-05-25 epiphany: failures (and successes) should emit
directional signals, not pass/fail. The net sum maps a landscape; voids
in the landscape are the substance. This module's job is to *write the
pointers honestly* so later work can read the geometry.

Registry shape (one JSONL line per kept adaptation):

  {
    "registry_id":       "<sha256[:16] of (agent_name, adaptation_name, applied_at)>",
    "agent_name":        "Polyhymnia",
    "adaptation_name":   "DROP_MTIME_CACHE",
    "applied_at":        "2026-05-25T...",

    # The directional pointer (which health axis moved, and by how much)
    "baseline_composite":  0.20,
    "post_composite":      0.38,
    "delta_composite":     +0.18,
    "delta_per_axis": {
        "null_rate":               -0.30,   # null_rate went DOWN by 0.30
        "diversity":               +0.05,
        "downstream_consumption":   0.00,
        "novelty":                 +0.10
    },

    # Applicability — which other agents could borrow this
    "agent_traits":      ["daemon", "scour_based", "mtime_cached"],
    "stagnation_signature": {
        "primary_failure_mode": "high_null_rate",
        "preconditions": ["repository_walk", "file_extension_filter"]
    },

    # Provenance
    "snapshot_pointer":  null,
    "module_source":     "agents/polyhymnia/daemon.py:PolyhymniaSelfImprover",
    "human_approved":    false,
    "cost":              "one_tick",
    "reversibility":     "manual_via_revert"
  }

Trait taxonomy (open vocabulary — agents declare what they are):

  Structural traits:        daemon, oneshot, library, watcher
  Input shape:              scour_based, queue_consumer, eval_consumer,
                            log_reader, db_reader, http_fetcher
  Caching behavior:         mtime_cached, content_addressed, stateless,
                            cursor_based
  Output shape:             tessera_emitter, ticket_filer, dr_dispatcher,
                            corpus_builder, lens_renderer, game_generator
  Failure modes seen:       null_rate_high, recursive_drift, upstream_starvation,
                            saturation_ceiling, format_drift

Borrowing rule: a registered mutation is OFFERED to a new agent's menu if
the new agent's declared traits are a SUPERSET of the mutation's
agent_traits AND the agent's failure modes intersect the mutation's
stagnation_signature.preconditions. Otherwise it's filtered out (no point
offering a scour-based mutation to a queue-consumer).

Voids (v2d, not in this module): take the (trait-coordinate, adaptation)
matrix. Sparse cells where no kept mutation exists but neighboring cells
do are candidate void coordinates — places we should TRY an adaptation
nobody has tried in this neighborhood. The lattice tells us where to
probe next. That's the directional-pointer epiphany applied to our own
self-improvement loop.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "agents" / "_shared" / "successful_mutations.jsonl"


def _compute_registry_id(agent_name: str, adaptation_name: str,
                         applied_at: str) -> str:
    h = hashlib.sha256()
    h.update(f"{agent_name}|{adaptation_name}|{applied_at}".encode())
    return h.hexdigest()[:16]


def record_kept_mutation(
    *,
    agent_name: str,
    adaptation_name: str,
    applied_at: str,
    baseline_composite: float,
    post_composite: float,
    delta_per_axis: dict,
    agent_traits: list[str],
    addresses_failure_modes: list[str],
    stagnation_signature: dict,
    module_source: str,
    cost: str = "unknown",
    reversibility: str = "unknown",
    human_approved: bool = False,
    snapshot_pointer: Optional[str] = None,
    registry_path: Optional[Path] = None,
) -> str:
    """Append a kept-mutation row to the shared registry. Returns the
    registry_id (16-char hex). Idempotent on the same (agent, adaptation,
    applied_at) triple — re-recording is a no-op."""
    path = registry_path or DEFAULT_REGISTRY_PATH
    rid = _compute_registry_id(agent_name, adaptation_name, applied_at)
    # Idempotency: skip if same registry_id already present
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                if json.loads(line).get("registry_id") == rid:
                    return rid
            except Exception:
                continue
    record = {
        "registry_id": rid,
        "agent_name": agent_name,
        "adaptation_name": adaptation_name,
        "applied_at": applied_at,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "baseline_composite": float(baseline_composite),
        "post_composite": float(post_composite),
        "delta_composite": float(post_composite - baseline_composite),
        "delta_per_axis": dict(delta_per_axis),
        "agent_traits": sorted(set(agent_traits)),
        "addresses_failure_modes": sorted(set(addresses_failure_modes)),
        "stagnation_signature": dict(stagnation_signature),
        "snapshot_pointer": snapshot_pointer,
        "module_source": module_source,
        "human_approved": bool(human_approved),
        "cost": cost,
        "reversibility": reversibility,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return rid


def query_borrowable_mutations(
    *,
    requesting_agent: str,
    agent_traits: list[str],
    current_failure_modes: list[str],
    registry_path: Optional[Path] = None,
    exclude_self: bool = True,
    min_delta: float = 0.05,
) -> list[dict]:
    """Return registry rows the requesting agent could borrow.

    Filtering rules:
      - requesting agent's traits must be a SUPERSET of registered traits
        (the borrower must have at least all the structural properties
        the mutation was applied against)
      - if current_failure_modes is non-empty, the mutation's
        stagnation_signature.preconditions must intersect those modes
        (a borrower with no shared failure context shouldn't get the
        mutation surfaced — it's not the right tool)
      - delta_composite must be at least min_delta (default 0.05 — same
        threshold the mixin uses to decide kept vs reverted)
      - if exclude_self, mutations originally registered by the requesting
        agent are filtered out (already in own menu)

    Returns the matching rows sorted by delta_composite descending."""
    path = registry_path or DEFAULT_REGISTRY_PATH
    if not path.exists():
        return []
    agent_traits_set = set(agent_traits)
    failure_modes_set = set(current_failure_modes)
    candidates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if exclude_self and row.get("agent_name") == requesting_agent:
            continue
        if row.get("delta_composite", 0) < min_delta:
            continue
        # Applicability: borrower must have all the traits the mutation was applied against
        registered_traits = set(row.get("agent_traits", []))
        if not registered_traits.issubset(agent_traits_set):
            continue
        # Relevance: borrower's current failures should overlap the mutation's
        # claimed failure-mode coverage (if both sides have declared modes)
        if failure_modes_set:
            addressed = set(row.get("addresses_failure_modes", []))
            if addressed and not (addressed & failure_modes_set):
                continue
        candidates.append(row)
    candidates.sort(key=lambda r: r.get("delta_composite", 0), reverse=True)
    return candidates


def registry_stats(registry_path: Optional[Path] = None) -> dict:
    """Lightweight snapshot of the registry. Phase-2d void-detection will
    read this + the full file to compute the lattice's empty cells."""
    path = registry_path or DEFAULT_REGISTRY_PATH
    if not path.exists():
        return {"total_entries": 0, "by_agent": {}, "by_adaptation": {},
                "trait_universe": [], "exists": False}
    by_agent: dict = {}
    by_adaptation: dict = {}
    trait_universe: set = set()
    total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += 1
        a = row.get("agent_name", "?")
        n = row.get("adaptation_name", "?")
        by_agent[a] = by_agent.get(a, 0) + 1
        by_adaptation[n] = by_adaptation.get(n, 0) + 1
        trait_universe.update(row.get("agent_traits", []))
    return {
        "total_entries": total,
        "by_agent": by_agent,
        "by_adaptation": by_adaptation,
        "trait_universe": sorted(trait_universe),
        "registry_path": str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path),
        "exists": True,
    }
