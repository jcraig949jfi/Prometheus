"""Compositional mutations (SelfImprovingDaemon v2b).

When an agent's atomic menu is exhausted, auto-generate compound
adaptations: apply A1 then A2 as a single step; revert runs revert(A2)
then revert(A1) in reverse order. Polynomial growth from a finite atomic
menu.

Per the gen-N wall memory: compositional growth defers the wall but
doesn't break it. v2b is a cheap intermediate before v2c (LLM-authored)
and v3 (generational handoff).

Design rules:
  - Only compose adaptations that HAVE a revert (compositional only
    works if both atoms are reversible).
  - Skip pairs where either atom is itself a compound (no compound-of-
    compounds in v1; chain length cap = 2).
  - Skip pairs where either atom is borrowed or void-derived (they're
    placeholders that raise NotImplementedError on apply — composing
    them produces compounds that can't run).
  - apply() stores snapshots as a tuple; revert() unpacks in reverse.
  - If A1.apply succeeds but A2.apply raises, the compound fails midway;
    revert(A1) is run immediately to restore baseline. The compound is
    marked as failed (not kept).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .self_improving import Adaptation


def generate_compound_adaptations(
    atomic_menu,
    max_chain: int = 2,
    exclude_atoms_with_prefix: tuple = ("BORROWED__", "VOID__", "COMPOUND__"),
) -> list:
    """Build compound Adaptations from atomic ones.

    Args:
      atomic_menu: list[Adaptation] — the native ADAPTATION_MENU
      max_chain: int — currently must be 2; future v2b.2 will support 3+
      exclude_atoms_with_prefix: tuple of name-prefixes to skip (won't
        compose these — they're typically placeholders that can't run)

    Returns:
      list[Adaptation] — compound adaptations, each with apply/revert
      composed sequentially.
    """
    if max_chain != 2:
        raise NotImplementedError("v2b v1 supports max_chain=2 only")

    # Filter eligible atoms
    eligible = []
    for a in atomic_menu:
        if any(a.name.startswith(p) for p in exclude_atoms_with_prefix):
            continue
        if a.revert is None:
            continue
        eligible.append(a)

    # Need the Adaptation class at runtime
    from .self_improving import Adaptation

    cost_order = {"zero": 0, "trivial": 1, "one_tick": 2,
                  "medium": 3, "high": 4, "unknown": 5}

    def _max_cost(a, b):
        ca = cost_order.get(a.cost, 99)
        cb = cost_order.get(b.cost, 99)
        # The compound's cost is at least the max of the two
        return max(ca, cb)

    def _cost_label(rank):
        for k, v in cost_order.items():
            if v == rank:
                return k
        return "unknown"

    compounds = []
    for i, a1 in enumerate(eligible):
        for j, a2 in enumerate(eligible):
            if i == j:
                continue
            # Compose A1 then A2
            def _make_apply(atom1, atom2):
                def _compound_apply(agent, agent_state):
                    snap1 = atom1.apply(agent, agent_state)
                    try:
                        snap2 = atom2.apply(agent, agent_state)
                    except Exception:
                        # Roll back atom1 immediately on midway failure
                        if atom1.revert:
                            try:
                                atom1.revert(agent, agent_state, snap1)
                            except Exception:
                                pass
                        raise
                    return (snap1, snap2)
                return _compound_apply

            def _make_revert(atom1, atom2):
                def _compound_revert(agent, agent_state, snapshot):
                    if not snapshot:
                        return
                    snap1, snap2 = snapshot
                    # Revert in reverse order
                    if atom2.revert:
                        try:
                            atom2.revert(agent, agent_state, snap2)
                        except Exception:
                            pass
                    if atom1.revert:
                        try:
                            atom1.revert(agent, agent_state, snap1)
                        except Exception:
                            pass
                return _compound_revert

            compounds.append(Adaptation(
                name=f"COMPOUND__{a1.name}__{a2.name}",
                description=(f"Compound: {a1.name} then {a2.name}. "
                             f"Both reversible; reverts run in reverse order "
                             f"on revert/failure."),
                cost=_cost_label(_max_cost(a1, a2)),
                reversibility="manual_via_revert",
                apply=_make_apply(a1, a2),
                revert=_make_revert(a1, a2),
                # Compositions inherit human-approval requirement only if
                # either atom requires it. Pure native composes are auto-runnable.
                requires_human_approval=(
                    a1.requires_human_approval or a2.requires_human_approval
                ),
            ))
    return compounds
