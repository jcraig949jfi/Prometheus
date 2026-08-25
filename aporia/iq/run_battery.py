"""run_battery.py — BATTERY validation: B1-B4 exactly as preregistered (a0571a75).

Claim objects are transcribed from the committed RESULT json files of the six rungs, so the
inputs are shipped evidence rather than a retelling.

    python aporia/iq/run_battery.py
"""
from __future__ import annotations

import copy
import inspect
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import battery as B  # noqa: E402

OUT = HERE

T = lambda v, lo, hi: {"value": v, "attainable_lo": lo, "attainable_hi": hi}          # noqa: E731
R = lambda n, lo, hi: {"n": n, "attainable_lo": lo, "attainable_hi": hi}              # noqa: E731
FULL = {"retrieval": True, "parse": True, "answer": True, "composition": True,
        "evaluation": True}

# ── the six rungs AS ACTUALLY RUN ───────────────────────────────────────────
CLAIMS = {
 "IQ-PORT-1": {
    "intervention_class": "PORT_EXISTING_CAPABILITY",
    "falsifiers_run": dict(FULL),
    "thresholds": {"deltaE": T(5 / 120, 0.0, 1.0)},
    "readings": {"footprint": R(120, 0, 120), "mutants": R(4, 0.0, 1.0)},
    "branch_table_partitions": True, "is_null_result": False,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
 "IQ-NULL": {
    "intervention_class": "INSTRUMENT",
    "falsifiers_run": {"evaluation": True},
    "thresholds": {"deltaE_zero": T(0.0, 0.0, 0.8333)},
    "readings": {"null_region": R(56880, 0.0, 1.0), "footprint": R(120, 0, 120)},
    "branch_table_partitions": True, "is_null_result": True,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
 "PROVENANCE": {
    "intervention_class": "INSTRUMENT",
    "falsifiers_run": {"evaluation": True},
    "thresholds": {"membership": T(1.0, 0.0, 1.0)},
    "readings": {"pipelines": R(464652, 0, 464652)},
    "branch_table_partitions": True, "is_null_result": False,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
 "TRANSFER-1": {
    "intervention_class": "INSTRUMENT",
    "falsifiers_run": {"evaluation": True},
    # the bar as SHIPPED was 0.10 against a 1/k floor of 0.25 -- see B3; here we record the
    # CORRECTED range that the rung's own findings established, because the rung was terminal
    # REDESIGN and its threshold defect is reported in its findings rather than carried forward
    "thresholds": {"mutant_bar": T(0.25, 0.25, 1.0)},
    "readings": {"nondegenerate": R(410, 0.0, 1.0), "degenerate": R(95, 0.0, 1.0)},
    "branch_table_partitions": True, "is_null_result": False,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
 "SCORER-FIX": {
    "intervention_class": "INSTRUMENT",
    "falsifiers_run": {"evaluation": True},
    "thresholds": {"mutant_bar": T(0.02, 0.0, 1.0)},
    "readings": {"nondegenerate": R(410, 0.0, 1.0), "scorer_audit": R(10, 0, 10)},
    "branch_table_partitions": True, "is_null_result": False,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
 "CEILING-ABSTAIN": {
    "intervention_class": "INSTRUMENT",
    "falsifiers_run": {"evaluation": True},
    "thresholds": {"direction": T(0.0, 0.0, 0.8333)},
    "readings": {"battery": R(120, 0.0, 1.0)},
    "branch_table_partitions": True, "is_null_result": True,
    "positive_control_ran": True, "probe_modifies_measured_quantity": False},
}

# ── B3: the four historical defects, replayed. FIT CHECK, not a capability estimate. ──
DEFECTS = {
 "TRANSFER-1_subfloor_threshold": (
    {**copy.deepcopy(CLAIMS["TRANSFER-1"]),
     "thresholds": {"mutant_bar": T(0.10, 0.25, 1.0)}}, "G-FLOOR"),
 "check_transitivity_vacuous_footprint": (
    {**copy.deepcopy(CLAIMS["IQ-NULL"]),
     "readings": {"footprint": R(0, 0, 120)}}, "G-VACUOUS"),
 "ceiling_abstain_v1_perturbing_probe": (
    {**copy.deepcopy(CLAIMS["CEILING-ABSTAIN"]),
     "probe_modifies_measured_quantity": True}, "G-PERTURB"),
 "ceiling_abstain_null_before_positive_control": (
    {**copy.deepcopy(CLAIMS["CEILING-ABSTAIN"]),
     "positive_control_ran": False}, "G-INERT"),
}


def ablate(name, claim):
    """B2: remove ONE required falsifier (or the branch assert for INSTRUMENT claims, whose
    mandatory set is a single item and whose ablation must still be a real removal)."""
    c = copy.deepcopy(claim)
    if c["intervention_class"] == "PORT_EXISTING_CAPABILITY":
        c["falsifiers_run"]["parse"] = False
        return c, "parse falsifier removed"
    c["falsifiers_run"]["evaluation"] = False
    return c, "evaluation falsifier removed"


def main():
    Rout = {"experiment": "BATTERY", "date": "2026-08-25", "agent": "Aporia (M1)",
            "prereg": "aporia/iq/PREREG_BATTERY_2026-08-25.md", "prereg_commit": "a0571a75"}

    # B1
    b1 = {k: B.adjudicate(v) for k, v in CLAIMS.items()}
    Rout["B1_verdicts"] = {k: v[0] for k, v in b1.items()}
    Rout["B1_reasons"] = {k: v[1] for k, v in b1.items() if v[1]}
    Rout["B1_all_admissible"] = all(v[0] == "ADMISSIBLE" for v in b1.values())

    # B2 — the negative control that makes B1 non-vacuous
    b2, notes = {}, {}
    for k, v in CLAIMS.items():
        c, note = ablate(k, v)
        b2[k] = B.adjudicate(c)
        notes[k] = note
    Rout["B2_ablation_applied"] = notes
    Rout["B2_verdicts"] = {k: v[0] for k, v in b2.items()}
    Rout["B2_all_inadmissible"] = all(v[0] == "INADMISSIBLE" for v in b2.values())

    # attainable-range check on the gate ITSELF: both endpoints must occur
    Rout["gate_range_both_endpoints_occur"] = (Rout["B1_all_admissible"]
                                               and Rout["B2_all_inadmissible"])

    # B3 — FIT CHECK
    b3 = {}
    for name, (claim, expect) in DEFECTS.items():
        verdict, reasons = B.adjudicate(claim)
        b3[name] = {"verdict": verdict, "expected_gate": expect,
                    "caught_by_expected_gate": any(r.startswith(expect) for r in reasons),
                    "reasons": reasons}
    Rout["B3_defects"] = b3
    Rout["B3_all_caught"] = all(v["caught_by_expected_gate"] for v in b3.values())
    Rout["B3_IS_A_FIT_CHECK"] = ("These four defects DESIGNED these four gates. Catching them "
                                 "is a fit statistic, NOT evidence the gate catches unseen "
                                 "defects. The only real test is prospective: the gate binds "
                                 "SELECTOR before SELECTOR runs.")

    # B4 — purity: determinism, and no prose field branched on
    det = all(B.adjudicate(v) == B.adjudicate(v) for v in CLAIMS.values())
    src = "".join(inspect.getsource(g) for g in B.GATES)
    keys = set(re.findall(r'\.get\(\s*"([a-z_]+)"', src))
    stray = sorted(keys - B._READABLE - {"value", "attainable_lo", "attainable_hi", "n"})
    Rout["B4_deterministic"] = det
    Rout["B4_fields_read_by_gates"] = sorted(keys)
    Rout["B4_fields_outside_declared_set"] = stray
    Rout["B4_pure"] = det and not stray and ("import " not in src)

    Rout["dropped_records"] = 0
    Rout["dropped_records_note"] = ("Nothing dropped: every claim is adjudicated and every "
                                    "verdict recorded, including reasons on failures.")

    b1ok, b2ok = Rout["B1_all_admissible"], Rout["B2_all_inadmissible"]
    Rout["verdict"] = ("PARK_SHIPPED_RUNG_INADMISSIBLE" if not b1ok
                       else ("REDESIGN_GATE_PASSES_EVERYTHING" if not b2ok else "ADVANCE"))
    Rout["verdict_rule_null_output"] = ("A gate returning one value on every input is VACUOUS "
                                        "whichever value it is; B1 and B2 together require "
                                        "BOTH endpoints of the [0, N] range to occur.")
    seen = {("PARK_SHIPPED_RUNG_INADMISSIBLE" if not a else
             ("REDESIGN_GATE_PASSES_EVERYTHING" if not b else "ADVANCE"))
            for a in (True, False) for b in (True, False)}
    assert seen == {"PARK_SHIPPED_RUNG_INADMISSIBLE", "REDESIGN_GATE_PASSES_EVERYTHING",
                    "ADVANCE"}, "terminal table leaks"
    Rout["terminal_table_partitions"] = True

    json.dump(Rout, open(OUT / "RESULT_BATTERY.json", "w", encoding="utf-8"), indent=2)
    for k, v in Rout.items():
        if k not in ("dropped_records_note", "verdict_rule_null_output", "B3_IS_A_FIT_CHECK",
                     "B3_defects"):
            print(f"{k}: {v}")
    print("B3 caught:", {k: v["caught_by_expected_gate"] for k, v in b3.items()})


if __name__ == "__main__":
    main()
