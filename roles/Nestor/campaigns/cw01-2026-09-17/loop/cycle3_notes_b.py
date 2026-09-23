"""Cycle-3 reconciler notes, part B: P-E06 (coupled ecology) and the new trajectory nodes T-X15/T-X16/T-X17.
Run after every driver has exited."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

POOL, STATE = HERE / "TRAJECTORIES.jsonl", HERE / "STATE.jsonl"
NODES = [
    dict(trajectory_id="T-X15", kind="anomaly", origin="cw01-loop3 P-E01 / P-E05 (with P-D01, P-D03)", age="2026-09-18", scope="computational: integer programs on a bounded VM",
         originating_question_verbatim="(anomaly) Length and carried state are ONE coordinate beneath three separate findings: damage loss falls with length (rho -.76) and with persistent state words (-.51); tick sensitivity rises with persistent words (+.39) and correlates negatively with loss (-.43, -.29 partial); and neutral length accumulation under the original acceptance rule lowers damage loss with depth (.60 -> .50) while the no-growth rule raises it (.67 -> .84). Is the robustness dilution (fixed k over more instructions), redundancy (duplicated computation), or state carriage?",
         derived_operationalization="P-E01 cross (126 programs), P-E05 depth-64 walks x 2 rules x damage assay", translation_loss="damage k fixed in units, never as a fraction of length",
         world_substrate="archaeon.wse.worlds W0/W2_K2", representation="Proteus TT programs", search_process="C4-05 walk (orig / no_growth)", pressure="none (neutral band)", ruler="P-D01 loss; self-displacement", compute_budget="minutes",
         result="the acceptance filter's junk accumulation IS the damage-robustness mechanism at fixed k; whether it is dilution or redundancy is open",
         failure_surface="fixed-count damage confounds dilution with redundancy", anomalies=["no_growth products lose +.27 more than orig products at depth 64", "tick-sensitive programs are damage-robust"],
         unrun_interventions=["fraction-matched damage (k proportional to n)", "duplicate-then-damage vs pad-with-NOP-then-damage (redundancy vs dilution directly)", "persistent-words census along the walk"],
         fossils=["P-E01 rows.json", "P-E05 RESULT.json"], assumptions_at_time=["A and C were independent deformations"], later_changes_relevant=[], last_perturbation="P-E05", marginal_information_history=["P-D01: length sets loss", "P-E01: shared correlates", "P-E05: rule x depth x loss"], stasis_state="ACTIVE"),
    dict(trajectory_id="T-X16", kind="anomaly", origin="cw01-loop3 P-E06 (with P-D13)", age="2026-09-18", scope="computational: tree/tape genomes in a software ecology",
         originating_question_verbatim="(anomaly) Under a per-structural-unit price, blind damage acts as PRUNING that subsidises the damaged substrate: damaging TAPE bodies only lowers TREE's final share (mean .58 vs .76 undamaged) and lets TAPE hold rare TREE out; damaging TREE only raises TREE's share (.87) with trees half the size (6-9 units vs 13-14); damaging both gives the most coexistence (14/54 runs at 160 vs 10/54). Is damage-as-cost-reduction the mechanism behind P-D13's tilt, and does it hold when the price is zero?",
         derived_operationalization="P-E06 factorial rate x f0 x damage regime, draw-matched sham (none == sham verified)", translation_loss="one damage fraction (.1), one price list",
         world_substrate="world_e06.py", representation="TREE vs TAPE", search_process="e06 GA", pressure="score with sharing minus structural cost", ruler="final share, coexistence at 80/160, units", compute_budget="minutes",
         result="damage direction is set by whose bodies shrink; body size collapses under damage", failure_surface="cost and damage are coupled by the price list; a zero-price arm is needed",
         anomalies=["coexistence at 80 resolves by 160 in ~40 percent of runs (delayed exclusion)", "lineage collapse to <= 2 ancestors by generation ~39 in every regime"],
         unrun_interventions=["price 0 with damage", "damage fraction dose", "damage after evaluation (non-heritable) vs before (heritable, as here)"],
         fossils=["P-E06 runs.json (full trajectories)"], assumptions_at_time=["damage is a cost to the damaged substrate"], later_changes_relevant=[], last_perturbation="P-E06", marginal_information_history=["P-D13: tilt toward TAPE (sham defect)", "P-E06: pruning reading"], stasis_state="ACTIVE"),
    dict(trajectory_id="T-X17", kind="anomaly", origin="cw01-loop3 P-E02 (with P-E01)", age="2026-09-18", scope="computational: integer programs on a bounded VM",
         originating_question_verbatim="(anomaly) Temporal response is a LINEAGE PHENOTYPE with at least two classes: W0-evolved programs are ASK-TIME BOUND (an idle tick before an ask displaces that ask only, an idle tick between the PUTs displaces nothing), W2-evolved selected tops are INPUT-SCHEDULE BOUND (an idle tick between the PUTs displaces every answer, an idle tick before either ask displaces none). Which class does selection build under which world, and is the class heritable across neutral walks?",
         derived_operationalization="P-E02 per-tag constructions on W2_K2; P-E01 idle-tick map", translation_loss="two worlds, one idle-tick content", world_substrate="archaeon.wse.worlds W0 / W2_K2", representation="Proteus TT programs", search_process="none (census)", pressure="none", ruler="per-tag self-displacement", compute_budget="seconds",
         result="two classes; shelf parents intermediate", failure_surface="only idle ticks tested; K=2 only", anomalies=["W2 tops are immune to ask-timing yet fully sensitive to input spacing"],
         unrun_interventions=["idle tick between the two PUTs of one tag (D=2)", "evolve under idle ticks in W0 and W2 and read the class", "class along the neutral walk"],
         fossils=["P-E02 rows.json", "P-E01 rows.json"], assumptions_at_time=["timing sensitivity is one thing"], later_changes_relevant=[], last_perturbation="P-E02", marginal_information_history=["P-D02: switch", "P-E01: idle tick", "P-E02: two classes"], stasis_state="ACTIVE"),
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
        for n in NODES:
            if n["trajectory_id"] in existing:
                continue
            n = dict(n)
            n["recorded"] = ts
            fh.write(json.dumps(n, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": n["trajectory_id"], "ts": ts, "state": "ACTIVE", "reason": "anomaly promoted to its own node in cycle 3", "marginal_information_history": n["marginal_information_history"]}, ensure_ascii=True) + "\n")
    L.append_evidence("T-E06", "P-E06", "RECONCILER (none == sham verified; D076's design flaw is closed by construction): the ecology read as one system. (1) Undamaged, TREE invades from .1 at every rate EXCEPT a window at .6-.7 where rare TREE goes extinct in 3/3 ids at .7 (final .81 / .33 / .00 / .69 / .62 / .54 for rates .5-1.0); TAPE never invades from .1 (f0 .9 -> TREE 1.0 at every rate). The rate acts through a non-monotone WINDOW, not a monotone crossing; P-D05's direction flip was a protocol effect (pre-adapted resident) or sits inside this window. (2) Damage = PRUNING under the price list: TAPE-only damage lowers TREE's share (.58) and holds rare TREE out at every rate; TREE-only damage raises it (.87) with trees at 6-9 units; both-damage gives the most coexistence (14/54 at 160; 4 cells with majority coexistence) -> T-X16. (3) Delayed exclusion is real: coexistence 17/54 at 80 -> 10/54 at 160 undamaged. (4) Lineages collapse to <= 2 ancestors by generation ~39 in every regime (T-X01).", True,
                      state="ACTIVE", state_reason="continuation: rate window resolved at .05 steps with pre-adapted vs from-scratch residents; price 0 x damage; 240 generations inside the window")
    L.append_evidence("T-X14", "P-E06", "RECONCILER: the rate does not set a monotone direction; from-scratch mixing shows a WINDOW (.6-.7) where rare TREE is excluded and TREE dominance on both sides. T-X14's crossing is re-posed as a window whose edges depend on the resident's pre-adaptation (P-D05 protocol) - continuation recorded on T-E06.", True)
    L.append_evidence("T-X01", "P-E06", "RECONCILER: ancestor lineages collapse to <= 2 by generation ~39 (all regimes, 270 runs) under tournament 3 with N 96 - the same order as P-A10's hitchhiking floor; damage does not change it (38-41).", False)
    L.append_evidence("T-X04", "P-E06", "RECONCILER: at fixed graph geometry the direction map over (rate, f0) is TREE-dominant with a rare-TREE exclusion window; geometry x rate remains the open map.", False)
    L.append_evidence("T-E07", "P-E06", "cross: in e06 blind damage is subsidised by the structural price (T-X16); T-X13's state avoidance in e01 may likewise be a cost effect of the holding price - a candidate connection, not verified.", False)
    for p in (POOL, STATE, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("notes B appended; nodes T-X15/T-X16/T-X17")


if __name__ == "__main__":
    main()
