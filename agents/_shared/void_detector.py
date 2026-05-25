"""Void detector over the mutation lattice (SelfImprovingDaemon v2d).

Reads the cross-agent mutation registry as sparse coordinates in
(trait_signature × failure_mode_signature × adaptation_name) → delta_vector
space. Identifies *voids*: coordinates where no kept mutation exists but
compatible neighbors did succeed.

Per James 2026-05-25 epiphany + feedback_failure_signal_vector_field:
each kept mutation is a directional pointer; the voids of the resulting
lattice are what we should probe next. v2a accumulated the pointers;
v2d reads the geometry.

**Void taxonomy (v2d v1 implements Type A only; B/C/D listed for future):**

  Type A (interpolation):  agent shape X has not tried adaptation A,
                           but compatible agent shapes Y (where Y's traits
                           are a SUBSET of X's traits AND Y's addressed
                           failure modes overlap X's current failures)
                           kept A with positive delta. Void coordinate:
                           (X, A). Predict that A would work for X too.

  Type B (extrapolation):  adaptation A kept across many trait sets,
                           pattern suggests it would also work just past
                           the trait-set boundary it has been tried in.
                           Higher uncertainty than Type A.

  Type C (compositional):  two adaptations A1, A2 both work in similar
                           contexts; nobody has tried the compound
                           (A1 + A2). Crosses into v2b territory.

  Type D (axis-unaddressed): existing kept mutations cluster on a few
                           health axes (e.g., all reduce null_rate);
                           no mutation strongly reduces another axis
                           (e.g., recursive_drift) even though that axis
                           is observed as a failure mode in the fleet.
                           These voids point to GAPS IN THE MENU ITSELF
                           — possibly require LLM-authored adaptations
                           (v2c) to fill.

This module computes Type A on every call. Types B/C/D are documented
in the design doc for future v2d.1+ phases — the API shape supports them.
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "agents" / "_shared" / "successful_mutations.jsonl"


@dataclass
class Void:
    """A coordinate in the lattice where we predict a mutation would work
    but no agent of the matching shape has tried it."""
    void_type: str                       # 'interpolation' | 'extrapolation' | 'compositional' | 'axis_unaddressed'
    target_agent_traits: list[str]       # the trait set the void is "for"
    target_failure_modes: list[str]      # the failure modes the void is "for"
    adaptation_name: str                 # the suggested adaptation
    evidence_neighbors: list[dict]       # registry rows supporting the prediction
    predicted_delta_composite: float     # weighted mean of evidence deltas
    predicted_delta_per_axis: dict       # per-axis prediction
    confidence: float                    # 0-1, density of evidence
    rationale: str                       # one-line human-readable explanation


# ---------------------------------------------------------------------------
# Loading + coordinate extraction
# ---------------------------------------------------------------------------

def _load_registry(path: Optional[Path] = None) -> list[dict]:
    p = path or DEFAULT_REGISTRY_PATH
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _shape_key(traits: list[str], failure_modes: list[str]) -> tuple:
    """Canonical hashable shape coordinate. (sorted_traits_tuple, sorted_failures_tuple)."""
    return (tuple(sorted(set(traits))), tuple(sorted(set(failure_modes))))


def _shape_compatible(target_traits: set, target_failures: set,
                      source_traits: set, source_failures: set) -> bool:
    """True if the SOURCE mutation's shape is compatible with applying to
    the TARGET agent. Definition matches mutation_registry.query_borrowable:
      - source_traits MUST be a subset of target_traits (target has all
        the structural properties the mutation was applied against)
      - source_failures MUST intersect target_failures (relevance — at
        least one shared failure mode)
    """
    if not source_traits.issubset(target_traits):
        return False
    if source_failures and target_failures:
        if not (source_failures & target_failures):
            return False
    return True


# ---------------------------------------------------------------------------
# Type A void detection
# ---------------------------------------------------------------------------

def _detect_type_a_voids(rows: list[dict]) -> list[Void]:
    """For each (target_shape, adaptation) cell that is empty but has
    compatible neighbors with kept mutations of that adaptation, emit a Void."""
    if not rows:
        return []

    # Index: adaptation -> list of (rows that kept it)
    by_adaptation: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_adaptation[r["adaptation_name"]].append(r)

    # Universe of shapes: every distinct (traits, failure_modes) tuple seen.
    # NOTE: Type A v1 only considers shapes that appear in the registry.
    # Cold-start (shapes the registry has never seen) is deferred to v2d.1
    # via an agent_directory side-table.
    all_shapes: set[tuple] = set()
    shape_to_kept_adaptations: dict[tuple, set] = defaultdict(set)
    for r in rows:
        shape = _shape_key(r.get("agent_traits", []),
                           r.get("addresses_failure_modes", []))
        all_shapes.add(shape)
        shape_to_kept_adaptations[shape].add(r["adaptation_name"])

    voids: list[Void] = []
    for target_shape in all_shapes:
        target_traits = set(target_shape[0])
        target_failures = set(target_shape[1])
        kept_by_target = shape_to_kept_adaptations[target_shape]
        # For every adaptation in the registry that this shape has NOT tried:
        for adaptation, rows_for_adapt in by_adaptation.items():
            if adaptation in kept_by_target:
                continue  # already tried + kept by this exact shape
            # Find compatible evidence (rows from other shapes where adaptation
            # worked AND that shape is compatible with target)
            evidence: list[dict] = []
            for r in rows_for_adapt:
                source_traits = set(r.get("agent_traits", []))
                source_failures = set(r.get("addresses_failure_modes", []))
                if _shape_compatible(target_traits, target_failures,
                                     source_traits, source_failures):
                    # Filter out trivial self-evidence: source shape == target shape
                    source_shape = _shape_key(r.get("agent_traits", []),
                                              r.get("addresses_failure_modes", []))
                    if source_shape == target_shape:
                        continue
                    evidence.append(r)
            if not evidence:
                continue

            # Compute predicted delta as weighted mean (by delta_composite)
            total_delta = sum(r.get("delta_composite", 0) for r in evidence)
            predicted_composite = total_delta / len(evidence)

            # Per-axis prediction (mean across evidence)
            axis_sums: dict = defaultdict(float)
            axis_counts: dict = defaultdict(int)
            for r in evidence:
                for axis, v in (r.get("delta_per_axis") or {}).items():
                    axis_sums[axis] += v
                    axis_counts[axis] += 1
            predicted_per_axis = {
                axis: axis_sums[axis] / axis_counts[axis]
                for axis in axis_sums
            }

            # Confidence: log-scaled by evidence count, normalized
            import math
            confidence = min(1.0, math.log(1 + len(evidence)) / math.log(10))

            # Rationale
            source_agents = sorted(set(r.get("agent_name", "?") for r in evidence))
            rationale = (
                f"{len(evidence)} compatible neighbor(s) "
                f"({', '.join(source_agents[:3])}{'...' if len(source_agents) > 3 else ''}) "
                f"kept {adaptation} with mean Δ={predicted_composite:+.2f}; "
                f"target shape never tried it."
            )

            voids.append(Void(
                void_type="interpolation",
                target_agent_traits=list(target_shape[0]),
                target_failure_modes=list(target_shape[1]),
                adaptation_name=adaptation,
                evidence_neighbors=evidence,
                predicted_delta_composite=predicted_composite,
                predicted_delta_per_axis=predicted_per_axis,
                confidence=confidence,
                rationale=rationale,
            ))

    # Rank by (evidence count, predicted delta) — most-evidenced + biggest-predicted first
    voids.sort(
        key=lambda v: (len(v.evidence_neighbors), v.predicted_delta_composite),
        reverse=True,
    )
    return voids


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_voids(
    registry_path: Optional[Path] = None,
    void_types: tuple = ("interpolation",),
    min_confidence: float = 0.0,
    max_voids: int = 100,
) -> list[Void]:
    """Compute voids in the mutation lattice. v1 returns Type A
    (interpolation) only; other void_types are reserved for v2d.1+."""
    rows = _load_registry(registry_path)
    out: list[Void] = []
    if "interpolation" in void_types:
        out.extend(_detect_type_a_voids(rows))
    out = [v for v in out if v.confidence >= min_confidence]
    return out[:max_voids]


def voids_for_agent(
    agent_traits: list[str],
    current_failure_modes: list[str],
    registry_path: Optional[Path] = None,
    min_confidence: float = 0.0,
) -> list[Void]:
    """Filter detect_voids() to voids whose target shape MATCHES this
    agent's shape. This is what an agent calls to ask 'what should I try next?'"""
    target_traits_set = set(agent_traits)
    target_failures_set = set(current_failure_modes)
    all_voids = detect_voids(registry_path=registry_path,
                             min_confidence=min_confidence)
    matching = []
    for v in all_voids:
        # Match: target_agent_traits subset of caller's traits AND failures intersect
        v_traits = set(v.target_agent_traits)
        v_failures = set(v.target_failure_modes)
        if v_traits.issubset(target_traits_set):
            if not v_failures or not target_failures_set or (v_failures & target_failures_set):
                matching.append(v)
    return matching


def summary(registry_path: Optional[Path] = None) -> dict:
    rows = _load_registry(registry_path)
    voids = detect_voids(registry_path=registry_path)
    by_void_type = defaultdict(int)
    for v in voids:
        by_void_type[v.void_type] += 1
    return {
        "registry_entries": len(rows),
        "total_voids_detected": len(voids),
        "by_void_type": dict(by_void_type),
        "top_void": (
            {
                "target_agent_traits": voids[0].target_agent_traits,
                "target_failure_modes": voids[0].target_failure_modes,
                "adaptation_name": voids[0].adaptation_name,
                "predicted_delta_composite": voids[0].predicted_delta_composite,
                "confidence": voids[0].confidence,
                "rationale": voids[0].rationale,
            } if voids else None
        ),
    }
