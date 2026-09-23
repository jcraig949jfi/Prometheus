"""Candidate perturbations, batch E (cycle 3): descendants of the cycle-2 continuation manifolds.
Three directions carry deliberate depth (T-X12 temporal semantics; the T-ARCH4/M1 deformation
surface; the T-E06 ecology as a coupled system) without owning the batch; at least two slots are
reserved for candidates whose purpose is neither confirmation nor parameter refinement. Scores are
opportunity judgements (0-3) recorded before any run. Computational scope for every item: integer
programs on a bounded VM, GA policies and tree/tape genomes in software worlds; nothing biological."""
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


# ---------------------------------------------------------------- T-X12: temporal semantics, not another delay experiment
cand(id="P-E01", parent="T-X12", family="temporal_semantics", axis="tick_content x lineage", type="parameterized-response-map", deformation="B",
     delta="TICK-CONTENT RESPONSE MAP at the PROGRAM level (self-displacement: a program's answers on episodes that are identical except for the inserted material) and at the walker level. Variants built from the W0 episodes by construction, not by knob: (a) one EMPTY tick before the ask; (b) one NOISE tick; (c) 2/3/4 NOISE ticks; (d) a REPEATED last-PUT tick; (e) the same NOISE words appended to the last PUT tick (no tick boundary); (f) a NOISE tick BEFORE the first PUT; (g) an empty tick before the first PUT; (h) NOISE-then-EMPTY vs EMPTY-then-NOISE (order); (i) persist policy forced to 'none' with and without the NOISE tick. Lineages: viable parents of all four strata, their walker-16 descendants, C4-08 selected tops. Per program a response class (immune / boundary-sensitive / content-sensitive / threshold / non-monotone) from the displacement curve; walker-level loud-step trace on w0_solver walkers with a REVERT test where the loud step preserved length (the differing words restored in the depth-16 final)",
     unchanged="programs, W0 episode content (tags, values), displacement ruler, walk seeds", attacks="P-D02's reading that the switch is 'an extra tick': which property of the tick (boundary, content, position, order, persistence) carries it, and whether susceptibility is a lineage phenotype",
     nonredundant="every variant is a construction P-D02 could not express through WorldSpec knobs; program-level self-displacement is a new ruler", cost_minutes=5,
     continuation=["tick budget as a dose", "state-word census at the loud step", "C5 representation B programs", "programs evolved under inserted ticks"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=3))

cand(id="P-E02", parent="T-X12", family="temporal_semantics", axis="per_tag_timing x cross_tag", type="parameterized-switch-probe", deformation="B",
     delta="PER-TAG TIMING made live by construction on the K=2 world (W2_K2, two streams, two asks): a NOISE tick inserted before tag A's ask only, before tag B's ask only, before both, and 2 ticks before A only; per program and per ASK POSITION the self-displacement - does delaying one tag's ask displace the OTHER tag's answer (cross-tag interference through carried state) or only its own? Programs: shelf parents (W2_K2 natives), C4-08 selected tops, w0_solver parents; plus the same construction on W0_heldout as a one-stream control",
     unchanged="episode content, programs, displacement ruler", attacks="D073 left per-tag timing untested; the P-D02 switch was observed only where one stream exists, so 'timing' and 'state across streams' were confounded",
     nonredundant="per-tag timing was never live in any cell; cross-tag displacement is a new observable", cost_minutes=3,
     continuation=["K=3", "delay between the two PUTs rather than before the asks", "programs evolved under W2 with inserted ticks"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

# ---------------------------------------------------------------- T-ARCH4/M1: the surface acquires coordinates
cand(id="P-E03", parent="T-ARCH4/M1", family="arch4", axis="selection_vs_inheritance", type="required-comparison", deformation="A",
     delta="SELECTED TOPS vs THEIR OWN ANCESTORS vs DRIFT: a Nestor evolver (mutation-only, frozen grammar, W2_K2 reward, E=16, N=96 from the depth-16 walkers of every viable parent, each individual carrying its ancestor id) run 60 generations under (i) tournament-3 selection and (ii) DRIFT (uniform parent choice, same births, same operator), 2 seeds; then the P-D01 damage assay (delete k=2/4 one site, delete k=4 four sites, operand k=4, opcode k=4; modulo decode; 4 draws) on the selected top-32, a drift sample of 32, and the ancestor walker and original parent of each - paired by ancestor - scored on W2_K2 and on W1_d1; loss regressed on arm with length and ancestor loss as covariates; ancestor-lineage survival tracked per generation in both arms (T-X01's hitchhiking floor in this evolver, free)",
     unchanged="grammar, worlds, classification constants, P-D01 damage kinds", attacks="P-D01's reading that C4-08 selected tops are ~.20 more robust: selected, inherited from the walkers, or a drift by-product (length)?",
     nonredundant="the required comparison before 'selected robustness' can be said; drift arm is the discriminating control", cost_minutes=10,
     continuation=["selection on W0 / W1_d4", "generation dose (robustness vs G)", "n_ops 2 births (C4-08 perturbed arm)"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=1))

cand(id="P-E04", parent="T-ARCH4/M1", family="arch4", axis="surface_coordinates", type="parameterized-dose-surface", deformation="A",
     delta="NEW COORDINATES for the damage surface: (i) OPERAND ROLE MAP - a single operand hit (k=2 instructions, one site) by operand SLOT (a: register field; b; c) x opcode CATEGORY of the hit instruction x whether the instruction is executed (dynamic reach from the meter) - loss and displacement per cell; (ii) FIXED-k PAIRWISE SITE INTERACTION - k=4 as two 2-instruction windows at sites i,j (6 pairs per program): loss(i+j) against the independence prediction 1-(1-loss(i))(1-loss(j)); an epistasis index per program; (iii) HELD-OUT FAMILIES - delete k=4 at 1 and 4 sites scored on W0_heldout, W1_d1, W1_d4, W2_K2d1 (reward change and exaptation); programs: viable parents, walker-16 descendants, C4-08 tops; modulo decode; 4 draws",
     unchanged="classification constants, episodes (CRN), programs' behaviour", attacks="P-D01's factorisation (k, s, kind, placement, decode, set): the operand softness and the small locality term are unexplained; the surface may hold coordinates (role, reach, epistasis) the current axes cannot express",
     nonredundant="none of the three coordinates exists in any cell yet", cost_minutes=8,
     continuation=["triples of sites", "role map on trap-NOP decode", "reach-weighted damage dose"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-E05", parent="T-ARCH4/S1", family="arch4", axis="search_depth x acceptance_rule x damage", type="stasis-escape-cross", deformation="C",
     escapes_stasis="S1 froze walk depth because deeper walks under the original rule accumulate length and nothing else (P-C16); P-D03 showed the no-growth rule removes the accumulation and raises exaptation, so DEPTH is re-posable under that rule - a different search rule is the recorded escape condition",
     delta="DEPTH 64 under {orig, no_growth} x {frozen, deletion-heavy} proposals (trap-NOP), 2 walkers x viable parents, archived at 16/32/64: exaptation, length, acceptance and structural diversity BY DEPTH; then the P-D01 damage assay (delete k=4 at 1 and 4 sites, operand k=4) on the depth-16 and depth-64 finals of each cell - does the acceptance rule (C) change the damage surface (A) of what it produces?",
     unchanged="band, seeds, parents, environments", attacks="S1's stasis reason and the independence of deformations A and C",
     nonredundant="depth beyond 16 was never run under any rule but the original; A x C never met", cost_minutes=8,
     continuation=["depth 128", "lencost rule", "band width x depth"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

# ---------------------------------------------------------------- T-E06: one coupled ecology
cand(id="P-E06", parent="T-E06", family="representation_ecology", axis="rate x frequency x damage", type="integrated-factorial", co_parents=["T-X14", "T-X04", "T-X01", "T-E07"],
     delta="ONE FACTORIAL over the e06 ecology: recombination rate {.5,.6,.7,.8,.9,1.0} x seeded TREE frequency {.1,.5,.9} x damage {none, sham, TAPE-only f=.1, TREE-only f=.1, both f=.1} x 3 attempt ids, 160 generations (twice the minimal form), tournament 3. Damage draws come from a SEPARATE rng keyed (attempt, generation) in every arm so the sham is draw-matched by construction and none==sham is a fail-closed harness check (D076). Telemetry: full frequency / units / registers / lineage-count / recombination-yield trajectories per run. Read-outs as a coupled system: phase map of final TREE over (rate, f0) per damage regime; the crossing rate per f0 where the invasion direction flips; coexistence at 80 and 160; extinction generation; body-size response by label; lineage collapse (T-X01)",
     unchanged="e06 world, sharing, prices, item streams, mutation", attacks="P-D05 (direction set by rate; crossing between .5 and 1.0), P-D11 (parity coexistence), P-D13 (damage tilt, sham defect D076), T-X04 (target geometry is fixed here: graph)",
     nonredundant="the three cycle-2 findings share a world and were never posed together; every prior cell was a scalar endpoint", cost_minutes=8,
     continuation=["target geometry x rate", "damage dose f", "240 generations at the crossing", "tournament 2"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

# ---------------------------------------------------------------- exploration: crosses that never met
cand(id="P-E07", parent="T-X12", family="cross", axis="temporal_sensitivity x damage_robustness", type="serendipity-cross", serendipity=True, co_parents=["T-ARCH4/M1"],
     delta="PROGRAM-LEVEL CROSS of two anomalies: each program's tick sensitivity (P-E01 self-displacement under one NOISE tick) against its damage loss (P-D01 rows, per program) and its state-use descriptors (persist policy, tape writes, persistent words, tick budget): is there one coordinate (carried state) beneath 'selected tops are the most timing-sensitive AND the most damage-robust'? Rank correlation with a permutation null; partial on length and set",
     unchanged="both rulers as recorded", attacks="the assumption that timing sensitivity and damage robustness are separate properties of a program", nonredundant="two nodes that never met; no run cost beyond P-E01", cost_minutes=1,
     continuation=["persist policy forced across the whole set", "the same cross on drift descendants (P-E03)"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=1, information_gain=2, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=0, underexplored_hard_to_operationalise=2))

cand(id="P-E08", parent="T-E03", family="coalitions", axis="mutation_operator x burden", type="stasis-escape", anti_gravity=True,
     escapes_stasis="the recorded escape is a mutation operator that can zero a weight; this candidate adds a ZEROING kick (each weight set to exactly 0 with probability .05 per birth, on top of the clipped Gaussian) and runs the MANDATORY attainability check first",
     delta="ATTAINABILITY FIRST: 30 generations of selection-free drift with the zeroing operator, 4 ids; the L0 coordinate (non-zero share) must move by >= .10 from its start or the candidate is closed INSTRUMENT_UNATTAINABLE without running the tax. If attainable: e03 treatment under sel = score - lambda * nz_share, lambda in {0, H} (H the measured headroom), 4 ids each, MI excess / sparsity / precision / coverage as in P-B07",
     unchanged="e03 world, organism, selection, 60 generations, MI ruler", attacks="P-B07's inert coordinate; T-E03's stasis scope [burden=L0 x mutation=clipped-gaussian] through its recorded escape only",
     nonredundant="the operator is new; the check is the standing rule applied before any pressure is frozen", cost_minutes=4,
     continuation=["zeroing probability dose", "magnitude-based burden", "tax x activation cost"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=2,
                 regime_newly_reachable=3, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))


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
            c["batch"] = "E"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
