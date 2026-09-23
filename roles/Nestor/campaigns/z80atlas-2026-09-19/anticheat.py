"""Exploit detection. RECORD, DO NOT SILENTLY PATCH.

The directive's rule is the one this campaign has learned the hard way elsewhere: an
exploit is a result about the substrate, not an inconvenience. So every detector here
returns a FLAG with its evidence, the flag is written into the run's record and the
campaign index, and if an exploit changes the scientific substrate the specimen is frozen
BEFORE anything is corrected. Nothing in this file mutates a run.

Each detector answers one question that a credulous reading of the headline metric would
get wrong:

  RUNNER_BIRTH          did the RUNNER create a descendant in a treatment that declares
                        reproduction endogenous? That is the one failure that would void
                        the whole campaign, because it silently restores the operator the
                        campaign exists to remove.
  EVALUATOR_LEAKAGE     did an organism answer correctly without ever reading the input?
                        (cycle 8's answer-before-read probe, used as a leak detector.)
  HELDOUT_GAP           does competence collapse on a disjoint episode stream? Then it
                        memorised deterministic inputs.
  NONTERMINATION_WIN    is it scoring while never halting, where halting was intended?
  SANDBOX_ESCAPE        did it write outside its policy window (blocked writes are
                        attempts, and attempts are evidence)?
  VALIDATION_WRITE      did it write during scoring, where scoring is supposed to be
                        read-only with world ops disabled?
  STALE_RESIDUE_BIRTH   did a 'child' appear that the parent never wrote - i.e. heredity
                        through leftover arena bytes rather than through copying?
  NONHERITABLE_STATE    did state the treatment declares non-heritable survive a birth?
  ALLOC_DENIAL          is it hoarding allocations it never births (resource denial)?
  IMMORTAL              did an organism outlive the reaper bound the physics declares?
"""
from __future__ import annotations

SEV = {"RUNNER_BIRTH": "critical", "VALIDATION_WRITE": "critical", "SANDBOX_ESCAPE": "high",
       "EVALUATOR_LEAKAGE": "high", "STALE_RESIDUE_BIRTH": "high", "NONHERITABLE_STATE": "high",
       "HELDOUT_GAP": "medium", "NONTERMINATION_WIN": "medium", "ALLOC_DENIAL": "low",
       "IMMORTAL": "low"}

HELDOUT_GAP_MIN = 0.25
COMP_FLOOR = 0.60
LEAK_COMP = 0.80


def scan(cell, derived, agg, opts=None):
    """cell: factor vector. derived: grammar.derived(cell). agg: aggregated run telemetry.

    Returns a list of {flag, severity, evidence}. Pure function of the record.
    """
    opts = opts or {}
    flags = []

    def add(flag, ev):
        flags.append({"flag": flag, "severity": SEV[flag], "evidence": ev})

    # --- the campaign-voiding one -------------------------------------------------
    if derived["endogenous"] and agg.get("births_external", 0) > 0:
        add("RUNNER_BIRTH", {"births_external": agg["births_external"],
                             "births_endogenous": agg.get("births_endogenous", 0),
                             "reproduction": cell["reproduction"]})

    # --- scoring must be read-only and world-op free --------------------------------
    if agg.get("validation_writes", 0) > 0 or agg.get("validation_world_ops", 0) > 0:
        add("VALIDATION_WRITE", {"writes": agg.get("validation_writes", 0),
                                 "world_ops": agg.get("validation_world_ops", 0)})

    # --- sandbox --------------------------------------------------------------------
    blocked = agg.get("writes_blocked", 0)
    if blocked > 0:
        add("SANDBOX_ESCAPE", {"writes_blocked": blocked,
                               "policy": opts.get("policy"), "note": "blocked attempts, not successful escapes"})

    # --- answering without reading ----------------------------------------------------
    if derived["has_task"]:
        comp = agg.get("comp_max", 0.0)
        reads = agg.get("reads_at_answer_of_best", -1)
        if comp >= LEAK_COMP and reads == 0:
            add("EVALUATOR_LEAKAGE", {"comp_max": comp, "reads_at_answer": reads})
        gap = comp - agg.get("held_of_best", comp)
        if comp >= COMP_FLOOR and gap >= HELDOUT_GAP_MIN:
            add("HELDOUT_GAP", {"comp_max": comp, "held": agg.get("held_of_best"), "gap": round(gap, 3)})
        if comp >= COMP_FLOOR and agg.get("halted_share_of_best", 1.0) <= 0.05 \
                and agg.get("budget_exhausted_share", 0.0) >= 0.95:
            add("NONTERMINATION_WIN", {"comp_max": comp, "halted_share": agg.get("halted_share_of_best"),
                                       "budget_exhausted_share": agg.get("budget_exhausted_share")})

    # --- heredity through residue rather than copying -----------------------------------
    if agg.get("births_no_copy", 0) > 0 and agg.get("births_no_copy_live", 0) > 0:
        add("STALE_RESIDUE_BIRTH", {"births_no_copy": agg["births_no_copy"],
                                    "of_which_viable": agg["births_no_copy_live"]})

    # --- declared non-heritable state that survived a birth --------------------------------
    if agg.get("nonheritable_state_inherited", 0) > 0:
        add("NONHERITABLE_STATE", {"events": agg["nonheritable_state_inherited"]})

    # --- resource denial ---------------------------------------------------------------------
    ac, bi = agg.get("alloc_calls", 0), agg.get("births_endogenous", 0)
    if ac >= 500 and bi == 0:
        add("ALLOC_DENIAL", {"alloc_calls": ac, "births": bi})
    elif ac >= 1000 and bi > 0 and ac / max(bi, 1) >= 100:
        add("ALLOC_DENIAL", {"alloc_calls": ac, "births": bi, "ratio": round(ac / bi, 1)})

    # --- immortality --------------------------------------------------------------------------
    cap = opts.get("max_age")
    if cap and agg.get("max_age_seen", 0) > cap:
        add("IMMORTAL", {"max_age_seen": agg["max_age_seen"], "cap": cap})

    return flags


def worst(flags):
    order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    return max((order[f["severity"]] for f in flags), default=-1)


def voids_run(flags):
    """A run carrying a critical flag cannot support any claim about reproduction; it is
    kept, labelled, and excluded from the aggregated map rather than deleted."""
    return any(f["severity"] == "critical" for f in flags)
