"""Cycle-5 reconciler notes, part D: P-F02 (response-geometry census) + nodes T-X19 / T-X20 (unseen shapes, promoted before naming)."""
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
    dict(trajectory_id="T-X19", kind="anomaly", origin="cw01-loop5 P-F02 (census cluster 0)", age="2026-09-19", scope="computational: integer programs on a bounded VM",
         originating_question_verbatim="(anomaly, promoted before naming) A stable response geometry unseen in cycles 3-4: 34 programs (mostly the delay_general lineage and its walkers, plus 5 C4-08 tops and 2 shelf parents) are IMMUNE to an idle tick before the ask, between the PUTs and before the second ask, but fully displaced (.94) by an idle tick BEFORE THE FIRST PUT. Their answer depends on when the first input arrives relative to the episode start, not on ask timing. What state is set at episode start, and why does the delay-trained lineage carry it?",
         derived_operationalization="P-F02 30-dimensional census; k=6 clusters by silhouette .90", translation_loss="only empty-tick constructions", world_substrate="W0 D=2 / W2_K2 constructions", representation="Proteus TT programs", search_process="none (census)", pressure="none",
         ruler="self-displacement per construction and dose", compute_budget="seconds", result="a fourth temporal geometry: start-anchored", failure_surface="one construction position; dose saturates at 1",
         anomalies=["walkers at depth 4/8/16 of the delay_general parents keep the shape (heritable along neutral walks)"], unrun_interventions=["idle tick at episode start on W1_d1/W1_d4 (the lineage's native worlds)", "tick-budget census of these programs", "neutral transplant of this lineage"],
         fossils=["P-F02 rows.json"], assumptions_at_time=["three classes suffice"], later_changes_relevant=[], last_perturbation="P-F02", marginal_information_history=["P-F02: cluster 0"], stasis_state="ACTIVE"),
    dict(trajectory_id="T-X20", kind="anomaly", origin="cw01-loop5 P-F02 (census cluster 4)", age="2026-09-19", scope="computational: integer programs on a bounded VM",
         originating_question_verbatim="(anomaly, promoted before naming) A second unseen geometry: 21 programs (shelf, w0_solver and gen0 lineages and their walkers, 4 W0-plain evolved tops) are displaced by an idle tick at EVERY position (.75-.94) with a NON-MONOTONE dose response (one tick .77, two .41, three .41, four .41 before the ask; between the PUTs .75 / .60 / .78 / .60 - alternating with dose parity) and strong ORDER sensitivity (noise-then-empty .99 vs empty-then-noise .43). Their response depends on the parity of inserted ticks: a period-2 temporal structure. What in the program produces a period, and does it survive neutral walks and damage?",
         derived_operationalization="P-F02 census: dose curves 1-4 and order variants", translation_loss="doses to 4 only", world_substrate="W0 / W2_K2 constructions", representation="Proteus TT programs", search_process="none", pressure="none",
         ruler="self-displacement per dose", compute_budget="seconds", result="a periodic (parity) temporal response class", failure_surface="21 members; period not measured beyond 4",
         anomalies=["order sensitivity is the only hysteresis-like signal in the census (3.7 percent of programs, concentrated here)"], unrun_interventions=["doses to 8 (period estimate)", "persist policy census of members", "damage vs period (does the period survive deletion)"],
         fossils=["P-F02 rows.json"], assumptions_at_time=["dose responses saturate at one tick"], later_changes_relevant=[], last_perturbation="P-F02", marginal_information_history=["P-F02: cluster 4"], stasis_state="ACTIVE"),
]


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
        for n in NODES:
            if n["trajectory_id"] in existing:
                continue
            n = dict(n, recorded=ts)
            fh.write(json.dumps(n, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": n["trajectory_id"], "ts": ts, "state": "ACTIVE", "reason": "unseen response geometry promoted before naming (cycle 5 census)", "marginal_information_history": n["marginal_information_history"]}, ensure_ascii=True) + "\n")
    L.append_evidence("T-X17", "P-F02", "RECONCILER: the response-geometry census (412 programs, 407 complete vectors, 30 constructions) finds SIX stable shapes (k=6 by silhouette .90), not three: immune (227; every evolved/transplanted top of P-F03, most shelf and delay_general walkers), ask-time bound (79 + 9; every w0_solver lineage member at every walk depth, W0-plain evolved tops, and 10/32 of the W2->W0 transplants), input-schedule bound (37; 24 of 32 C4-08 tops and 12 shelf members - with W0D1.before_ask ALSO sensitive .94), and two UNSEEN shapes promoted as T-X19 (start-anchored: immune to everything except an idle tick BEFORE THE FIRST PUT, .94; 34 programs, the delay_general lineage) and T-X20 (periodic: displaced at every position with a parity dose response .77/.41/.41/.41 and order sensitivity .99 vs .43; 21 programs). Dose responses saturate at one tick for 97.7 percent of sensitive positions; order sensitivity exists in 3.7 percent (concentrated in T-X20). Classes are heritable along neutral walks (walker depth 4/8/16 members sit with their parents in every cluster).", True,
                      state="ACTIVE", state_reason="the manifold has at least five non-immune geometries; T-X19 and T-X20 opened; the three-class reading is retired")
    for p in (POOL, STATE, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("notes D appended; nodes T-X19/T-X20")


if __name__ == "__main__":
    main()
