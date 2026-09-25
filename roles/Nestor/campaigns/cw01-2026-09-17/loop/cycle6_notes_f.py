"""Cycle-6 reconciler notes, part F: P-H01 (transplant map) and the node T-X21 (world attractors of temporal geometry)."""
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
NODE = dict(trajectory_id="T-X21", kind="mechanism-candidate", origin="cw01-loop6 P-H01, P-H03 (with P-G05, P-F03, P-G11, P-H08, P-H10)", age="2026-09-19", scope="computational: integer programs on a bounded VM",
            originating_question_verbatim="(mechanism candidate, promoted under the cycle-6 standard) Temporal geometries are WORLD ATTRACTORS of selection, carried by lineages between selections: W0 selection builds ask-time (from any competent lineage: schedule .73/.61/.57, start-anchored .57/.48/.45, periodic .94/1.0/.93 in 20 generations), W1_d4 selection builds START-ANCHORED (schedule lineage acquires before_first_put .75, periodic .54, start-anchored keeps .85), W2_K2 selection keeps whatever arrives (start-anchored .85, periodic and ask-time unchanged) and its native product is immune, and any delay-varying pressure builds IMMUNITY that generalises to unseen delays. Under neutral walks a geometry travels unless the host's neutral band admits the host attractor (W0 erodes immunity and start-anchoring by drift; W2 and W1_d4 do not). Which property of a world sets its attractor, and can a world be built whose attractor is a switching or predictive geometry?",
            derived_operationalization="transplant map (4 shapes x 3 worlds x neutral / selection), nonstationary worlds (6 regimes), neutral transplant (P-G05), evolution under idle ticks (P-F03)", translation_loss="20-60 generations; three worlds; four lineages",
            world_substrate="W0 / W1_d4 / W2_K2 / nonstationary W0", representation="Proteus TT programs", search_process="Nestor evolver (tournament 3), C4-05 neutral walks", pressure="reward on the selecting world", ruler="P-F02 curve set (convention-invariant, P-G11); reward on three worlds",
            compute_budget="minutes", result="attractors: W0 -> ask-time; W1_d4 -> start-anchored; W2 -> immune (C4-08 lineage: schedule); delay variability -> immune with generalisation", failure_surface="periodic's attractor world not identified (its members are W2 programs; W2 keeps it, W0 rebuilds ask-time, W1_d4 mixes)",
            anomalies=["ask-time programs moved to W2 keep their geometry AND fail to gain reward in 20 generations (reward .14): geometry can be conserved without competence", "the schedule lineage is competent on W0 (1.0) yet W0 rebuilds ask-time over it"],
            unrun_interventions=["worlds where invariance cannot solve the task (delay changes the expected answer) to force switching / prediction", "prefix-only transplants as the causal unit (P-H02)", "attractor identification for periodic (which world selects a parity response)", "longer neutral windows in W2 / W1_d4"],
            fossils=["P-H01 rows.json", "P-H03 tops.json", "P-G05 rows.json", "P-F03 tops.json"], assumptions_at_time=["geometries are lineage organs"], later_changes_relevant=[], last_perturbation="P-H01",
            marginal_information_history=["P-F03: selection removes/rebuilds", "P-G05: neutral erosion in W0", "P-H01: three-world map", "P-H03: invariance attractor"], stasis_state="ACTIVE",
            promotion_standard={"ruler_change": "P-G11: convention-invariant; shapes split by the reward ruler", "neutral_transplant": "P-G05 / P-H01: travels or erodes predictably by host band", "causal_intervention": "the selecting world (P-H01, P-H03, P-F03)", "held_out_or_nonstationary_function": "immune attractor solves unseen delay 2 (.77 / 1.0)", "raw_geometry_provenance_genomes": "curves + PREREG provenance + tops.json / rows.json genomes"})


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["trajectory_id"] for l in POOL.read_text(encoding="utf-8").splitlines() if l.strip()}
    if NODE["trajectory_id"] not in existing:
        with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
            fh.write(json.dumps(dict(NODE, recorded=ts), ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": "T-X21", "ts": ts, "state": "ACTIVE", "reason": "mechanism candidate promoted under the cycle-6 standard (ruler, neutral transplant, causal intervention, held-out function, raw geometry)", "marginal_information_history": NODE["marginal_information_history"]}, ensure_ascii=True) + "\n")
    L.append_evidence("T-X17", "P-H01", "RECONCILER (transplant map, 8 representatives x 4 shapes x 3 worlds; geometry, reward and ancestry tracked apart): START-ANCHORED representatives are competent on W0 (1.0) and W1_d4 (1.0): in W1_d4 the geometry is kept through the neutral walk (d .03) and selection (.01, before_first_put .85); in W2 kept under selection (.04); in W0 it ERODES by drift (.36) and selection rebuilds ask-time over it (.57/.48/.45 with a residual .36). PERIODIC representatives are W2 programs (W2 .69, silent on W0 and W1_d4): W2 selection keeps the shape exactly (d 0), W0 selection rebuilds ask-time (.94/1.0/.93, reward .83), W1_d4 selection mixes (.73/.54, reward .52). ASK-TIME representatives keep their geometry unchanged in W2 through neutral walk and selection (d .001 / 0) while gaining NO reward (.22 -> .14): geometry conserved without competence; in W1_d4 they are silent and selection dissolves the shape (reward .02). SCHEDULE (C4-08) representatives are competent on W0 (1.0): W0 drift moves them (.46) and W0 selection rebuilds ask-time (.73/.61/.57); W2 keeps them (.06); W1_d4 selection turns them START-ANCHORED (before_first_put .75, reward .76). Native products: W0 -> ask-time (.70/.75/.71), W2 -> immune, W1_d4 -> immune-with-a-trace (.06). Reading: the selecting world sets the geometry within 20 generations regardless of ancestry; neutral walks conserve it except where the host band admits drift (W0). Promoted with P-H03 as node T-X21 (world attractors).", True,
                      state="ACTIVE", state_reason="the manifold survives; its dynamics are world attractors; T-X21 opened")
    L.append_evidence("T-X19", "P-H01", "cross: start-anchored is the W1_d4 ATTRACTOR - W1_d4 selection builds it in the schedule lineage (.75) and partly in periodic (.54); it is kept in W2 and eroded in W0. Competent on W0 and W1_d4.", True)
    L.append_evidence("T-X20", "P-H01", "cross: periodic is kept exactly by W2 selection, rebuilt into ask-time by W0, mixed by W1_d4; its attractor world is not yet identified.", True)
    for p in (POOL, STATE, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("notes F appended; node T-X21")


if __name__ == "__main__":
    main()
