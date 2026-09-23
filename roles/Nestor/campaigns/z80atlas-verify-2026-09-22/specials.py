"""Special-result flags for the Cycle-9 verification campaign. P-4.

WHAT A FLAG IS. A preservation trigger: "keep this run, look at it later." It is not a
verdict and it is not evidence of the effect it names. Adjudication is a separate,
stricter pass over the frozen record (adjudicate.py).

WHAT CHANGED FROM THE PREDECESSOR, AND WHY.

P-4. `RESERVOIR_CROSSED_A_MOAT` used to fire on `structure == RESERVOIR` and `moat` and
any historical crossing:

    if summary.get("crossed") and cell["structure"] == "RESERVOIR" and d["moat"]:

Nothing in that condition asks whether the easy niche supplied the lineage that crossed.
It fired 124 times in the 72-hour campaign; 117 of those were seeded instrument
populations, which cannot bear on what evolution finds unaided, and the remaining 7 were
exogenous controls, which are not a reservoir result at all. Every one adjudicated
INADMISSIBLE. Here the flag fires only on a complete ancestry certificate, and seeded
instruments are excluded AT THE FLAG rather than downstream, so the preserved set means
what its name says.

P-3. Each flag DECLARES which member of the historical/final-state pair it fires on, in
its `reads` field, and its `evidence` carries the numbers from that basis. The other
basis travels in a separate, labelled `other_basis` block so a reader can see both
without either being passed off as the other. The predecessor fired
`REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION` on the historical flag and then reported
final-state numbers as its evidence, which is defect Z80A-D01: of 65 instances, 4 had a
NEGATIVE margin, meaning the exogenous control finished ahead of the run flagged as
reaching what the control could not.

Pure functions of (cell, derived, summary, rec). No I/O, no mutable state.
"""
from __future__ import annotations

# Historical basis: did this ever happen at any validation pass.
HISTORICAL = "historical"
# Final-state basis: is it true of the organisms alive when the run ended.
FINAL_STATE = "final_state"

REP_LEN = {"Z8_32": 32, "Z8_64": 64, "Z8_SHARED": 64, "Z8_SEPARATED": 64, "Z8_SLOTTED": 64}


def _pair(summary, ctrl, basis):
    """The (treatment, control) held-out scores on one declared basis."""
    if basis == HISTORICAL:
        return summary.get("held_max_ever"), (ctrl or {}).get("held_max_ever")
    return summary.get("held_max_final"), (ctrl or {}).get("held_max_final")


def _crossed(summary, basis):
    return bool(summary.get("crossed_ever") if basis == HISTORICAL
                else summary.get("crossed_at_final"))


def reservoir_crossed_a_moat(cell, d, summary, rec=None):
    """P-4. Fires ONLY on a complete easy-niche ancestry certificate.

    The certificate (world.ancestry_certificate) establishes, in order: the lineage's
    founder was born in the easy niche, a logged migration carried it out, and the
    crossing happened in a hard niche. world.py already refuses to build one on a
    truncated lineage, but `lineage_complete` is re-checked here because a summary can
    reach this function from a fixture or a hand-edited record, and a certificate
    without a complete lineage must never fire whatever its provenance.
    """
    if cell.get("structure") != "RESERVOIR":
        return None
    if not d.get("moat"):
        return None
    # Excluded AT THE FLAG, not at adjudication: a seeded instrument cannot bear on
    # what evolution finds unaided, so preserving it under this name is misleading.
    if d.get("seeded_instrument"):
        return None
    if not d.get("endogenous"):
        return None
    if not summary.get("lineage_complete"):
        return None
    cert = summary.get("ancestry_certificate")
    if not summary.get("has_reservoir_certificate") or not cert:
        return None
    if cert.get("crossing_niche") in (None, cert.get("founder_niche")):
        return None
    return {"flag": "RESERVOIR_CROSSED_A_MOAT",
            "reads": HISTORICAL,
            "evidence": {"basis": HISTORICAL,
                         "held_ever": summary.get("held_max_ever"),
                         "certificate": cert,
                         "migration_events": summary.get("migration_events"),
                         "niche_occupancy": summary.get("niche_occupancy")},
            "other_basis": {"basis": FINAL_STATE,
                            "held_final": summary.get("held_max_final"),
                            "crossed_at_final": summary.get("crossed_at_final")}}


def reached_only_under_endogenous_reproduction(cell, d, summary, rec):
    """Fires on the HISTORICAL basis and reports historical numbers as its evidence.

    The predecessor fired here and then handed the adjudicator final-state scores, so a
    run whose crossing lineage had since been reaped presented as evidence for a claim
    about reaching. Both bases are carried; neither substitutes for the other.
    """
    ctrl = (rec or {}).get("control_summary")
    if ctrl is None or (rec or {}).get("control_axis") != "reproduction":
        return None
    if not d.get("endogenous"):
        return None
    basis = HISTORICAL
    if not _crossed(summary, basis) or _crossed(ctrl, basis):
        return None
    endo, ext = _pair(summary, ctrl, basis)
    f_endo, f_ext = _pair(summary, ctrl, FINAL_STATE)
    return {"flag": "REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION",
            "reads": basis,
            "evidence": {"basis": basis, "endogenous_held_ever": endo,
                         "external_held_ever": ext},
            "other_basis": {"basis": FINAL_STATE, "endogenous_held_final": f_endo,
                            "external_held_final": f_ext,
                            "endogenous_crossed_at_final": summary.get("crossed_at_final"),
                            "external_crossed_at_final": ctrl.get("crossed_at_final")}}


def reached_only_in_incremental_representation(cell, d, summary, rec):
    sib = (rec or {}).get("sibling_atomic")
    if sib is None or d.get("constant_kind") != "INCREMENTAL":
        return None
    basis = HISTORICAL
    if not _crossed(summary, basis) or _crossed(sib, basis):
        return None
    inc, at = _pair(summary, sib, basis)
    f_inc, f_at = _pair(summary, sib, FINAL_STATE)
    return {"flag": "REACHED_ONLY_IN_INCREMENTAL_REPRESENTATION",
            "reads": basis,
            "evidence": {"basis": basis, "incremental_held_ever": inc, "atomic_held_ever": at},
            "other_basis": {"basis": FINAL_STATE, "incremental_held_final": f_inc,
                            "atomic_held_final": f_at}}


def spontaneous_replicator_from_random_bytes(cell, d, summary, rec=None):
    """Replication from an unseeded population, with the causal depth alongside.

    The predecessor's evidence was the first replicator alone, which says an event
    happened and nothing about whether a lineage followed. `max_causal_replication_depth`
    travels with it so the preserved record cannot be read as sustained propagation when
    it is a single star-shaped burst - the predecessor's actual result in 911 of 1,031
    admissible runs.
    """
    if not summary.get("replicated"):
        return None
    if d.get("seeded_instrument") or not d.get("spontaneity_test"):
        return None
    if not summary.get("replication_events"):
        return None
    return {"flag": "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES",
            "reads": HISTORICAL,
            "evidence": {"basis": HISTORICAL,
                         "first_replicator": summary.get("first_replicator"),
                         "replication_events": summary.get("replication_events"),
                         "births_similar_no_write": summary.get("births_similar_no_write"),
                         "max_causal_replication_depth": summary.get("max_causal_replication_depth"),
                         "propagating_replicators": summary.get("propagating_replicators")},
            "other_basis": None}


def reproductive_architecture_changed_under_task_demand(cell, d, summary, rec=None):
    if not (summary.get("replicated") and _crossed(summary, HISTORICAL)):
        return None
    if cell.get("pressure") not in ("TASK_GATED_INTERACTION", "RESOURCE_GATED", "MINIMAL_CRITERION"):
        return None
    sp = summary.get("span_mean_final")
    if not sp or sp >= REP_LEN.get(cell.get("representation"), 64) * 0.75:
        return None
    return {"flag": "REPRODUCTIVE_ARCHITECTURE_CHANGED_UNDER_TASK_DEMAND",
            "reads": FINAL_STATE,
            "evidence": {"basis": FINAL_STATE, "span_mean_final": sp,
                         "pressure": cell.get("pressure"),
                         "replication_events": summary.get("replication_events")},
            "other_basis": {"basis": HISTORICAL, "crossed_ever": summary.get("crossed_ever")}}


RULES = (
    reservoir_crossed_a_moat,
    reached_only_under_endogenous_reproduction,
    reached_only_in_incremental_representation,
    spontaneous_replicator_from_random_bytes,
    reproductive_architecture_changed_under_task_demand,
)


def special_flags(cell, derived, summary, rec=None):
    """Every flag this run fires. Order is the RULES order, so output is deterministic."""
    out = []
    for rule in RULES:
        got = rule(cell, derived, summary, rec)
        if got:
            out.append(got)
    return out
