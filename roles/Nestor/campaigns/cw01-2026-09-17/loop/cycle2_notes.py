"""Cycle-2 reconciler notes (append-only), new trajectory nodes for material anomalies, scoped stasis.
Run AFTER every driver has exited (drivers append to EVIDENCE/STATE too)."""
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
    dict(trajectory_id="T-X12", kind="anomaly", origin="cw01-arch4 P-C14 / P-D02", age="2026-09-18",
         scope="computational: integer programs on a bounded VM",
         originating_question_verbatim="(anomaly) Why does ONE inserted NOISE tick between the last PUT and the ASK make silent W0 drift loud (.001 -> .118), while NOISE words inside the same tick do not (.009), and delay-evolved programs barely react (.017) while selected W2_K2 descendants react most (.332)?",
         derived_operationalization="P-D02 grid (D073: only the global delay knob is live at K=1); per-step trace: 10/60 walkers have a distinct loud step (operators mixed, no broken references)",
         translation_loss="per-tag delays not testable at K=1", world_substrate="archaeon.wse.worlds W0/W1", representation="Proteus TT programs", search_process="C4-05 walk",
         pressure="none", ruler="displacement vs original program", compute_budget="seconds", result="the switch is an extra TICK, not extra input",
         failure_surface="cross-tick state: programs carry tape/register state across ticks; an extra tick advances it before the ask",
         anomalies=["selected descendants (C4-08) are the most timing-sensitive (.332)", "delay-general parents' walkers are nearly immune (.017)"],
         unrun_interventions=["vary the CONTENT of the inserted tick (empty / NOISE / repeated PUT)", "K=2 worlds where per-tag delays are live", "revert-and-replay of the loud step", "persist flag off"],
         fossils=["P-D02 RESULT.json per-walker traces"], assumptions_at_time=[], later_changes_relevant=[], last_perturbation="P-D02", marginal_information_history=["P-C14: switch found", "P-D02: narrowed to the inserted tick"], stasis_state="ACTIVE"),
    dict(trajectory_id="T-X13", kind="anomaly", origin="cw01-loop1 P-B03 / cw01-loop2 P-D07", age="2026-09-18",
         originating_question_verbatim="(anomaly) In e01's retention world, evolving under blind state deletion selects for holding LESS state: the intact retention margin falls to a third (.0019 vs .0061) and absolute retained computation after damage is lower at every severity. Weather selects for state AVOIDANCE, the reverse of e07's hypothesised robustness.",
         derived_operationalization="P-B03 (ratio doubled because the margin shrank) and P-D07 (absolute retained score lower at f .1/.2/.3/.45, raw differences outside the relabelling band; ancova sign flips again by covariate extrapolation, D071)",
         translation_loss="one world, one organism", world_substrate="world_e01.py", representation="5-gene retention policy", search_process="e01 GA", pressure="task score with blind deletion during evolution",
         ruler="absolute retained score above floor; intact margin", compute_budget="minutes", result="reversal: weather reduces state use",
         failure_surface="a single-parameter organism can only avoid or accept damage; no mechanism to protect state exists", anomalies=["the ratio measure and the absolute measure disagree in sign because the denominator is what evolution changed"],
         unrun_interventions=["an organism with a redundancy channel (write the same partial twice) so protection is representable", "damage severity during evolution as a dose", "damage timing relative to recurrence"],
         fossils=["P-B03, P-D07 RESULT.json"], assumptions_at_time=["robustness would be built as retention plus repair"], later_changes_relevant=[], last_perturbation="P-D07", marginal_information_history=["P-B03 material", "P-D07 material (reversal named)"], stasis_state="ACTIVE"),
    dict(trajectory_id="T-X14", kind="anomaly", origin="cw01-loop1 P-A07 / cw01-loop2 P-D05", age="2026-09-18",
         originating_question_verbatim="(anomaly) Recombination rate flips e06's invasion asymmetry rather than removing it: at rate 0.5 TAPE invades TREE (TREE invades in 4/12 cells); at rate 1.0 TREE invades TAPE (8/12) and TAPE mostly cannot; mutual invasibility appeared in 1/12 cells - P-A07's single cell was a crossing-point accident.",
         derived_operationalization="P-D05: 6 attempt ids x 2 geometries x 2 rates, corrected invasion analysis", translation_loss="two rates only", world_substrate="world_e06.py", representation="TREE vs TAPE",
         search_process="e06 GA", pressure="score with sharing", ruler="invasion when rare", compute_budget="minutes", result="direction of dominance is a function of the recombination rate; the crossing lies between 0.5 and 1.0",
         failure_surface="mutual invasibility is a measure-zero crossing, not a regime, under this price list", anomalies=["legacy geometry at rate 1.0: TREE invades in 3/6 with TAPE at 0"],
         unrun_interventions=["fine rate sweep .5-1.0 to locate the crossing", "frequency-dependent invasion at the crossing", "tournament size x rate (P-D11)"],
         fossils=["P-D05 rows"], assumptions_at_time=["rate 1.0 is a regime"], later_changes_relevant=[], last_perturbation="P-D05", marginal_information_history=["P-A07: 1 cell", "P-D05: reversal, not replication"], stasis_state="ACTIVE"),
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
            sh.write(json.dumps({"trajectory_id": n["trajectory_id"], "ts": ts, "state": "ACTIVE", "reason": "anomaly promoted to its own node in cycle 2", "marginal_information_history": n["marginal_information_history"]}, ensure_ascii=True) + "\n")
    L.append_evidence("T-ARCH4/W1", "P-D02", "RECONCILER (D073): stochastic/interleaved/random-order cells were vacuous (identical episodes at K=1). Live cells: det1/2/4 .118/.109/.108 vs det0 .001; interleaved_d1 .07; NOISE words in-tick .009 vs an inserted NOISE tick .118: the switch is an extra TICK. Delay-evolved walkers .017; C4-08 descendants .332. 10/60 walkers show a distinct loud step (mixed operators, no broken jumps). Promoted to T-X12.", True,
                      state="ACTIVE", state_reason="mechanism narrowed to cross-tick state; continuation: content of the inserted tick, K=2 worlds, persist off")
    L.append_evidence("T-ARCH4/M1", "P-D03", "RECONCILER: growth under trap-NOP (+1.80 baseline) REVERSES under no_growth (-3.1 frozen, -6.0 deletion-heavy), lencost (-1.4/-3.1), symdel+delheavy (-3.5), and under trap-HALT (-0.76); length-balanced proposals still grow (+2.35). When growth reverses, exaptation RISES (.064-.074 vs .032) and structural diversity rises (1.56-1.64 vs 1.19): length accumulation was suppressing exaptation. Acceptance rule and proposal opposition each suffice; the mechanism is confirmed and controllable.", True,
                      state="ACTIVE", state_reason="continuation: depth 32/64 under no_growth+delheavy (the highest-exaptation cell); band width; C5 representation B")
    L.append_evidence("T-E07", "P-D07", "RECONCILER: absolute retained score is LOWER under weather at every dose (.0011 vs .0032 at f=.1 ... .0001 vs .0004 at .45; raw differences outside the band); intact margin under weather is a third of static (.0019 vs .0061, outside band); the sham arm equals static exactly. The ability-adjusted contrast flips sign across doses (POSITIVE at .1, NEGATIVE at .3/.45) - covariate extrapolation again (D071). Reading: weather selects for state AVOIDANCE in this organism. Promoted to T-X13.", True,
                      state="TEMPORAL_STASIS[world=e01-retention x organism=5-gene]", state_reason="two rulers and two dose designs strike the same surface: a one-parameter retention policy can only avoid or accept damage; the next informative perturbation needs an organism that can represent protection (a redundancy channel)")
    L.append_evidence("T-E06", "P-D05", "RECONCILER: NOT_REPLICATED as mutual invasibility (1/12 cells at rate 1.0) but a REVERSAL: TREE invades TAPE in 8/12 cells at 1.0 vs 4/12 at 0.5 while TAPE's invasion collapses; the recombination rate sets the DIRECTION of dominance and mutual invasibility is a crossing point. Promoted to T-X14. P-A07's evidence is corrected: one cell at the crossing.", True)
    L.append_evidence("T-X11", "P-B10", "RECONCILER: the plateau is a SEARCH LIMIT: Bayes-optimal router precision 1.0/1.0/.96/.80 at overlap .1/.2/.35/.5 vs evolved .55/.56/.50/.43; the gap (.37-.46 at G60) shrinks only slightly by G240 (.36-.45). The linear activation policy under this GA does not approach the ceiling; continuation: population 256 / 1000 generations / a nonlinear policy.", True,
                      state="ACTIVE", state_reason="a search-limit finding with obvious continuations")
    L.append_evidence("T-E03", "P-B07", "RECONCILER: the representational tax was INERT: non-zero-weight share stays .985 at every lambda because clipped Gaussian mutation never drives a weight below the .05 threshold; MI excess, sparsity and score unchanged. Instrument fact (the burden coordinate must be attainable by the mutation operator - the e08 lesson again), not a null about burden pressure.", False,
                      state="TEMPORAL_STASIS[burden=L0-threshold on continuous weights x mutation=clipped-gaussian]", state_reason="this coordinate cannot move under this operator; a descendant needs a mutation that can zero weights or a magnitude-based burden")
    L.append_evidence("T-X05", "P-D12", "RECONCILER: amputation alone at intervals 2/5/10/20 lowers burden (scalar .81-1.52 vs 1.87) without raising held64 (139-162 vs 156, all inside the band); the TAX+AMP held64 association in e08 is not carried by structural pressure alone.", False,
                      state="ACTIVE", state_reason="one factor excluded; next: tax alone at matched burden, then tax x amputation at matched burden")
    for p in (POOL, STATE, HERE / "EVIDENCE.jsonl"):
        RS.require_ascii_safe(p)
    print("cycle-2 notes appended; nodes T-X12/T-X13/T-X14")


if __name__ == "__main__":
    main()
