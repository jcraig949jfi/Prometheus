"""Candidate perturbations, batch I (cycle 7): worlds where the invariance escape is impossible; what
evolves under them; the prefix as a control interface; recombination under pressure; bounded secondary
threads; two anti-gravity attacks. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

OUT = HERE / "PERTURBATIONS.jsonl"
C = []


def cand(**k):
    C.append(k)


cand(id="P-I01", parent="T-X21", family="context_worlds", axis="regime changes the answer", type="world-construction", deformation="W",
     delta="CONTEXT WORLDS A / B / C (ctxworlds.py): regime 0 expects v, regime 1 expects 15 - v. A OBSERVABLE: [PUT tag v] then [ASK tag r]. B REMEMBERED: [CUE 1 c] [PUT tag v] [ASK tag] - decision-time observation identical across regimes. C PREDICTIVE: one lifetime of 16 trials, regime held for 4 trials then flipped, cue noisy (c = r with p .7). FORMAL CEILINGS computed on 200 episode sets before execution (invariant policy: A .5, B .5, C .5; cue-follow: A 1.0, B .5, C .7; tracker with known block length: C ~.85-.9) and written to PREREG. Evolution: N 96 from the walkers, tournament 3, mutation only, 120 generations, fresh episodes every generation, 3 seeds per world; CONTROLS evolved: B-destroyed and C-destroyed cues (2 seeds each); B-shuffled and B-nocue evaluated on B tops. Held-out: 4 fresh episode sets; for C also block 3 and 5 and other phases. Thresholds (promotion): A >= .90, B >= .80, C >= .80 on held-out sets (all above every invariant ceiling with margin). Tops (16 per run) saved with lifetime traces on held-out sets.",
     unchanged="VM, grammar, evolver, tournament", attacks="the invariance attractor (P-H03): whether evolution crosses from fixed response to context-dependent computation when no invariant policy can score", nonredundant="no world in the campaign ever made the ANSWER depend on regime", cost_minutes=10,
     continuation=["successor worlds closing any loophole found", "p_cue and block-length doses", "longer lifetimes"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=2, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-I02", parent="T-X21", family="context_worlds", axis="behavioural forensics of what evolved", type="mechanism-forensics", deformation="M", requires=["P-I01"],
     delta="IDENTIFY WHAT EVOLVES, behaviour first: for the top-4 organisms of every P-I01 run, on held-out lifetimes: (a) immediate stimulus dependence (answer vs v); (b) cue causality - the earlier cue overwritten at its tick with the decision-time observation unchanged: share of asks whose answer flips; (c) adaptation after a regime switch in C: accuracy by trials-since-switch; (d) anticipation: accuracy on switch trials whose cue is misleading, against the cue-follow expectation; (e) state corruption: registers and tape cleared at a trial boundary, recovery curve of accuracy; (f) transfer to held-out regime sequences (block 3 / 5, other phases, p_cue .6 / .9); (g) candidate internal quantities: registers whose values predict the regime across asks, then OVERWRITTEN at the ask with their other-regime value (transplant of the candidate quantity) - does the answer follow the register? Names from behaviour only: CONTEXT_DETECTOR (A), HISTORY_DEPENDENT (B: cue causality >= .5), ADAPTIVE_STATE (C: adaptation + recovery), PREDICTIVE (C: above cue-follow with anticipation), UNCLASSIFIED (success without these signatures -> its own node). Loophole audit: if a world was not crossed, the tops' strategy is named from the traces (identity, complement, cue-follow, silence).",
     unchanged="P-I01's organisms and worlds", attacks="the assumption that a mechanism can be read from instruction motifs", nonredundant="no lifetime trace or state intervention exists", cost_minutes=6,
     continuation=["register-level lesion series", "transplant of the regime register between organisms"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-I03", parent="T-X17", family="prefix", axis="prefix as control interface", type="dissection", deformation="P", co_parents=["T-X19", "T-ARCH4/M1"],
     delta="PREFIX DISSECTION with geometry and competence measured apart: donors = ask-time (W0-competent) and start-anchored (W1_d4-competent) representatives, hosts = immune naive programs; prefix length k in {1, 2, 4, 8}: (1) donor prefix(k) + host body; (2) donor prefix(k) + a JMP into the host body at offset 0 or mid (entry rewired); (3) host prefix(k) + donor body; (4) truncation series: donor prefix(k) alone; (5) relocation: donor with its prefix moved to its end; (6) same prefix reached through a jump: [JMP over filler] + filler + donor. Per variant: curve set (geometry transfer by the distinctive-component test, D088), reward on the donor world and the host world. Reading: SEQUENCE_CONTENT (truncations keep geometry/competence regardless of position), ENTRY_ROUTING (relocation / jump-entry change them), EARLY_STATE (prefix + any body works, prefix alone does not), REACHABILITY (rewiring decides), or an interaction.",
     unchanged="constructions, VM", attacks="P-H02's prefix dominance vs P-H04's span failure", nonredundant="no prefix manipulation exists", cost_minutes=6,
     continuation=["prefix length dose on competence", "prefix swap between two competent donors"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-I04", parent="T-X20", family="recombination", axis="recombination under context pressure", type="recombination-under-selection", deformation="X", co_parents=["T-X17", "T-X21"],
     delta="RECOMBINATION UNDER PRESSURE in world B (and C): the evolver with the grammar's splice operator and a tournament mate at rate .3 vs mutation only, from a MIXED initial population of geometry representatives (8 each of start-anchored, periodic, ask-time, schedule, immune, cycled to 96), 100 generations, 2 seeds per world; every generation the top-8 curve sets are computed and any NEW response surface (> .3 from every known centroid and from the five donor shapes) is archived with its genome, generation and reward before selection can remove it; NEW surfaces with reward above the world's threshold are followed at once (cue-causality and state-corruption tests inside the run). Compare final reward, shape shares and the NEW-surface count between splice and mutation-only arms.",
     unchanged="worlds (P-I01's), evolver", attacks="P-H02's dominance reading (neutral splicing) - selection may expose combinations the neutral assay hid", nonredundant="no recombination under selection in any world", cost_minutes=10,
     continuation=["follow every NEW surface as its own node", "splice rate dose"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=2, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-I05", parent="T-X17", family="temporal_semantics", axis="secondary threads, bounded", type="bounded-bundle",
     delta="BOUNDED BUNDLE: (a) periodic's attractor world - 60-generation selection from the walkers in W1_d1, W2_K2 and W7-like ASK2 (K=2, ask_kind ASK2) with the shape shares of the tops; (b) periodic doses 1-8 at every position for the 21 periodic members (period estimate); (c) longer neutral windows - depth 64 in W2 and W1_d4 for 8 ask-time and 8 start-anchored representatives (keep-shape by depth 16 / 32 / 64).",
     unchanged="constructions, walks, evolver", attacks="open secondary questions of cycle 6", nonredundant="none of the three was run", cost_minutes=6,
     continuation=[], scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=2, independent_intersection=1, regime_newly_reachable=2, information_gain=2, delta_novelty=1, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=0, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-I06", parent="T-ARCH5", family="representation", axis="grammar-B evolution in a context world", type="serendipity-representation", serendipity=True, co_parents=["T-X21"],
     delta="GRAMMAR-B EVOLUTION in world B (remembered regime): the evolver with mutate_b as the birth operator, 120 generations, 2 seeds, N 96 from the walkers; final held-out reward against the threshold and against the grammar-v0.4 runs of P-I01; tops' geometry census.",
     unchanged="world B, evolver otherwise", attacks="whether the representation (operator set) changes whether the boundary is crossed", nonredundant="grammar B never evolved anything in this campaign", cost_minutes=4,
     continuation=["grammar B in world C"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-I07", parent="T-X12", family="temporal_semantics", axis="persist channel knockouts", type="anti-gravity", anti_gravity=True, co_parents=["T-X21"],
     delta="IS REMEMBERED CONTEXT CARRIED BY THE PERSIST POLICY? World B evolution (120 generations, 2 seeds) with the persist policy LOCKED to none / regs / tape / all (config mutation of the policy suppressed) and INHERITED (each lineage keeps its initial policy): which channels allow the threshold to be crossed. If B is crossed under persist=none, remembered context is carried by something other than the documented state channels (a loophole to record); if only some channels allow it, the channel is the causal seat of the context.",
     unchanged="world B, evolver otherwise", attacks="cycle 7's implicit assumption that the state channel is where context lives", nonredundant="the persist policy was never locked during evolution", cost_minutes=6,
     continuation=["channel knockout at test time on evolved organisms"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-I08", parent="T-ARCH4/W1", family="census", axis="geometry of context-evolved organisms", type="serendipity-census", serendipity=True, requires=["P-I01"], co_parents=["T-X17", "T-X21"],
     delta="GEOMETRY CENSUS of the P-I01 tops (every world, every seed, top-16): the full curve set, nearest known shape, and any shape outside the known manifold (> .3 from every centroid) reported raw with genomes; shape shares per world; whether crossing the threshold coincides with a particular geometry.",
     unchanged="P-I01 tops, constructions", attacks="nothing yet: do the context worlds produce shapes the manifold does not contain", nonredundant="no context-evolved organism was ever read on the constructions", cost_minutes=3,
     continuation=["new shapes as nodes"], scores=dict(attacks_old_assumption=1, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-I09", parent="T-ARCH4/W1", family="context_worlds", axis="cue-reliability and block-length dose", type="anti-gravity", anti_gravity=True, co_parents=["T-X21"],
     delta="IS THE PREDICTIVE WORLD ESCAPED BY CUE-FOLLOWING? World C evolved (120 generations, 2 seeds each) at cue reliability p in {.55, .7, .9} with block 4, and at block 8 with p .7; the tops' held-out reward against the cue-follow ceiling (p) and the tracker ceiling at each dose: if reward tracks p, the world is solved by remembered cue-following (a B-level policy) and the predictive pressure is a loophole; if reward exceeds p toward the tracker, integration or anticipation is present.",
     unchanged="world C construction, evolver", attacks="cycle 7's assumption that world C forces more than remembered context", nonredundant="p and block were never dosed", cost_minutes=8,
     continuation=["successor worlds with p near .5 and long blocks"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=2, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))


def main():
    existing = set()
    for line in OUT.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing.add(json.loads(line)["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with OUT.open("a", encoding="utf-8") as fh:
        for c in C:
            if c["id"] in existing:
                continue
            c = dict(c)
            c["recorded"] = ts
            c["batch"] = "I"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
