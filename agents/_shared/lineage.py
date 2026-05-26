"""Generational lineage scaffold for SelfImprovingDaemon (v3 iter 1).

When the agent's full adaptation menu (native + compound + borrowed + void +
LLM) fails to break stagnation across repeated self-summon cycles, the
agent's last move is to author a CHILD agent with mutated charter and
retire. Substrate is the lineage, not the single agent (see
feedback_gen_30_wall.md: C# self-improving agent stalled at gen 30 because
its menu was bounded; only menu-growth or generational handoff escapes
that wall).

v3 iter 1 ships:
  - LineageEntry dataclass + JSONL persistence
  - record_lineage() / lineage_for_agent() / generation_of()
  - propose_child_scaffold() — DETERMINISTIC child template derived from
    parent's traits, failure modes, exhausted experiments, and unaddressed
    voids. No LLM call yet; iter 2 fills the charter skeleton via the
    cascade.

v3 iter 2 will add (deferred):
  - LLM-authored CHARTER and daemon.py scaffold
  - Apoptosis: parent self-deletes after child boots successfully
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LINEAGE_PATH = Path(__file__).resolve().parent / "lineage.jsonl"

log = logging.getLogger("lineage")


@dataclass
class LineageEntry:
    """One generational handoff event. Append-only — entries never edited."""
    parent_agent: str
    child_agent: str
    generation: int                              # child's generation (parent's + 1)
    retirement_reason: str                       # 'menu_exhausted_repeated_summons' | 'manual' | 'apoptosis'
    parent_traits: list[str]
    child_traits: list[str]                      # mutated from parent
    parent_failure_modes: list[str]
    child_failure_modes: list[str]               # mutated from parent
    suggested_adaptations: list[str]             # names parent tried/wanted but couldn't apply
    charter_skeleton: str                        # iter 1: template; iter 2: LLM-filled
    born_at: str
    notes: str = ""


def record_lineage(entry: LineageEntry, path: Optional[Path] = None) -> Path:
    """Append a lineage event. Returns the path written to."""
    p = path or LINEAGE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    return p


def lineage_for_agent(agent_name: str,
                      path: Optional[Path] = None) -> list[LineageEntry]:
    """Return all lineage entries where agent_name is parent OR child,
    in chronological order (file order)."""
    p = path or LINEAGE_PATH
    if not p.exists():
        return []
    out: list[LineageEntry] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("parent_agent") == agent_name or row.get("child_agent") == agent_name:
            try:
                out.append(LineageEntry(**row))
            except TypeError:
                continue
    return out


def generation_of(agent_name: str,
                  path: Optional[Path] = None) -> int:
    """Return the generation number of an agent. Agents with no lineage
    entry are gen 1 (root). If the agent appears as a child, return its
    child generation. If only as parent, return 1 less than child gen."""
    entries = lineage_for_agent(agent_name, path=path)
    if not entries:
        return 1
    for e in entries:
        if e.child_agent == agent_name:
            return e.generation
    # only appears as parent
    return min(e.generation for e in entries) - 1


# ---------------------------------------------------------------------------
# Child-authoring scaffold (iter 1 = deterministic template)
# ---------------------------------------------------------------------------

# Axis → trait the child should gain when parent failed on that axis
AXIS_TO_INHERITED_TRAIT = {
    "null_rate": "aggressive_null_avoidance",
    "diversity": "diversity_seeker",
    "downstream_consumption": "downstream_aware",
    "novelty": "novelty_seeker",
}


def _detect_axis_failures(completed_experiments: list[dict]) -> list[str]:
    """Inspect the parent's completed experiments. Return the health axes
    that NO kept experiment improved — these are the axes the child should
    be specialized to attack."""
    from collections import defaultdict
    best_improvement: dict[str, float] = defaultdict(float)
    desired_sign = {"null_rate": -1, "diversity": +1,
                    "downstream_consumption": +1, "novelty": +1}
    for exp in completed_experiments:
        if exp.get("outcome") != "kept":
            continue
        baseline = exp.get("baseline_composite", {}) or {}
        post = exp.get("post_composite", {}) or {}
        for axis in desired_sign:
            sign = desired_sign[axis]
            delta = sign * (post.get(axis, 0) - baseline.get(axis, 0))
            if delta > best_improvement[axis]:
                best_improvement[axis] = delta
    THRESHOLD = 0.05
    return [a for a, v in best_improvement.items() if v < THRESHOLD]


def _untried_high_value_adaptations(si_state: dict, max_n: int = 5) -> list[str]:
    """Adaptations the parent SAW in its effective_menu but never managed to
    apply — either approval never came, apply() raised, or the menu kept
    growing past the budget. Returns names sorted by which the parent saw
    most often (those it tried hardest to use)."""
    seen_names: dict[str, int] = {}
    for entry in si_state.get("mutation_log", []):
        name = entry.get("adaptation")
        if name and entry.get("outcome") not in ("kept", "reverted"):
            # tried but never concluded → likely apply_failed or interrupted
            seen_names[name] = seen_names.get(name, 0) + 1
    # Also include failed_adaptations
    for failed in si_state.get("failed_adaptations", []):
        name = failed.get("name")
        if name:
            seen_names[name] = seen_names.get(name, 0) + 1
    ordered = sorted(seen_names.items(), key=lambda x: x[1], reverse=True)
    return [n for n, _ in ordered[:max_n]]


def _propose_child_traits(parent_traits: list[str],
                          parent_failures: list[str],
                          axis_failures: list[str]) -> list[str]:
    """Mutate parent's traits to seed the child. Strategy: keep all parent
    traits, ADD one new trait derived from the most-stuck axis. Avoid
    duplicates."""
    child_traits = list(parent_traits)
    for axis in axis_failures:
        added = AXIS_TO_INHERITED_TRAIT.get(axis)
        if added and added not in child_traits:
            child_traits.append(added)
            break   # one mutation per generational step; resist combinatorial bloat
    if child_traits == parent_traits:
        # No axis-derived trait available — add a generic exploration tag
        if "aggressive_exploration" not in child_traits:
            child_traits.append("aggressive_exploration")
    return child_traits


def _propose_child_failure_modes(parent_failures: list[str],
                                 axis_failures: list[str]) -> list[str]:
    """Child's failure modes seed from parent's, but PRIORITIZED to the axes
    parent never improved. Strategy: child declares it's specifically here
    to attack what parent couldn't."""
    axis_to_failure = {
        "null_rate": "high_null_rate",
        "diversity": "low_diversity",
        "downstream_consumption": "no_downstream_consumption",
        "novelty": "low_novelty",
    }
    derived = [axis_to_failure[a] for a in axis_failures if a in axis_to_failure]
    if not derived:
        return list(parent_failures)
    # Child's failure modes = axis-derived first, then any parent failures not yet covered
    merged = list(derived)
    for f in parent_failures:
        if f not in merged:
            merged.append(f)
    return merged


CHARTER_TEMPLATE = """\
# {child_agent_name} — Charter (gen {generation})

## Lineage
- Parent: {parent_agent} (gen {parent_generation})
- Born: {born_at}
- Retirement reason for parent: {retirement_reason}

## Mission (immutable)
{mission_block}

## Inherited traits (from parent)
{inherited_traits_block}

## NEW traits (mutated from parent's lineage)
{new_traits_block}

## Failure modes this generation is specifically here to attack
(parent could not improve these axes despite full menu exhaustion)
{failure_modes_block}

## Suggested adaptations to seed the menu
(adaptations parent encountered but could not apply — child's first menu)
{suggested_adaptations_block}

## Constraints (inherited from substrate; never mutate)
- Mission lock: charter mission section is immutable; tactics mutate.
- Reward function: composite health metric, never single-variable.
- Mutation budget: MAX_MUTATIONS_PER_DAY caps daily burn.
- Reversibility: every adaptation must declare revert (or none == manual).
- Generational handoff: when this child also exhausts its menu under
  sustained stagnation, it authors gen {next_generation} and retires.

## What parent learned that this child should NOT relitigate
(adaptations parent tried + reverted — the child's menu should not re-try
these without first mutating them via compositional, void, or LLM tier)
{relitigated_block}

---
[ITER 1 SCAFFOLD: charter mission block is a placeholder. v3 iter 2 will
fill it via LLM cascade given the parent's mission + failure analysis.]
"""


def propose_child_scaffold(
    parent_agent: str,
    parent_traits: list[str],
    parent_failure_modes: list[str],
    parent_generation: int,
    si_state: dict,
    parent_mission: str = "[parent mission to be ported by iter 2 LLM call]",
) -> dict:
    """Build a complete child-agent scaffold (deterministic, iter 1).

    Returns a dict ready to be persisted via record_lineage() and rendered
    into a CHARTER.md draft. iter 2 will replace the deterministic charter
    template with LLM-authored mission re-statement."""
    completed = si_state.get("completed_experiments", []) or []
    axis_failures = _detect_axis_failures(completed)
    child_traits = _propose_child_traits(parent_traits, parent_failure_modes,
                                         axis_failures)
    child_failures = _propose_child_failure_modes(parent_failure_modes,
                                                   axis_failures)
    suggested = _untried_high_value_adaptations(si_state)
    next_gen = parent_generation + 1
    child_name = f"{parent_agent}_g{next_gen}"

    relitigated = sorted(set(
        exp.get("adaptation_name", "?") for exp in completed
        if exp.get("outcome") == "reverted"
    ))[:10]

    def _bulletize(items, empty_msg):
        if not items:
            return f"- {empty_msg}"
        return "\n".join(f"- {x}" for x in items)

    new_traits = [t for t in child_traits if t not in parent_traits]

    charter = CHARTER_TEMPLATE.format(
        child_agent_name=child_name,
        generation=next_gen,
        parent_agent=parent_agent,
        parent_generation=parent_generation,
        born_at=datetime.now(timezone.utc).isoformat(),
        retirement_reason="menu_exhausted_repeated_summons",
        mission_block=parent_mission,
        inherited_traits_block=_bulletize(parent_traits, "(none declared)"),
        new_traits_block=_bulletize(new_traits, "(no axis-derived mutation)"),
        failure_modes_block=_bulletize(child_failures,
                                       "(parent declared no failure modes)"),
        suggested_adaptations_block=_bulletize(
            suggested, "(parent never encountered un-applied adaptations)"),
        relitigated_block=_bulletize(
            relitigated, "(parent has no reverted experiments yet)"),
        next_generation=next_gen + 1,
    )

    return {
        "child_name": child_name,
        "generation": next_gen,
        "parent_agent": parent_agent,
        "parent_generation": parent_generation,
        "child_traits": child_traits,
        "child_failure_modes": child_failures,
        "suggested_adaptations": suggested,
        "axis_failures_addressed": axis_failures,
        "charter_skeleton": charter,
        "retirement_reason": "menu_exhausted_repeated_summons",
    }
