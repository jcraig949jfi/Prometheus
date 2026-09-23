"""Candidate perturbations, batch F (cycle 4): tests of whether cycle 3's newly exposed coordinates
(T-X15 length / carried state, T-X16 damage as pruning, T-X17 temporal response class, the P-E03
selection effect) are PORTABLE CAUSAL STRUCTURE: separations, transplants, economics reversals and
cross-substrate reads that could break them. Scores are opportunity judgements (0-3) recorded before
any run. Computational scope for every item: integer programs on a bounded VM, GA policies and
tree/tape genomes in software worlds; nothing biological."""
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


# ---------------------------------------------------------------- PRIORITY 1: T-X15 length / carried state
cand(id="P-F01", parent="T-X15", family="carried_state", axis="length x state x structure separation", type="causal-separation", deformation="A",
     delta="FOUR MANIPULATIONS of one program, each moving one candidate coordinate while holding the others: (i) NOP-PAD - append NOP instructions to double the length (length up, executable structure and carried state unchanged; behaviour identity verified by displacement 0 on the base episodes, else the variant is dropped); (ii) DUPLICATE - append a full copy of the genome (length up, redundant executable structure up); (iii) PERSIST-NONE - persist policy forced to none (carried state down, length and structure unchanged; loss measured against the transformed program's own baseline); (iv) original. Each under FIXED-k damage (delete k=4, one site) and FRACTION-MATCHED damage (delete round(.15 n)), operand k=4 and operand fraction .15; modulo decode; 4 draws; on parents, walker-16 descendants and C4-08 tops. Predictions written before the run: DILUTION -> pad and duplicate both lower fixed-k loss, neither changes fraction-matched loss; REDUNDANCY -> duplicate lowers fraction-matched loss, pad does not; CARRIED STATE -> persist-none raises loss with length fixed and pad/duplicate move nothing; a pattern outside these three breaks the factorisation. Plus the PERSISTENT-WORDS CENSUS along orig-rule walks (depth 64, archived 16/32/64; loss regressed on log length AND persistent words per depth).",
     unchanged="damage kinds, classification constants, episodes (CRN), walk seeds", attacks="T-X15's reading that length accumulation IS damage robustness; the correlation cannot say which of dilution / redundancy / carried state / topology is the causal object",
     nonredundant="the first manipulations of a single coordinate at a time; fraction-matched damage was never run", cost_minutes=8,
     continuation=["pad at random positions vs at the end", "duplicate half the genome", "persist=regs vs tape vs all as a dose", "jump-topology census (reference facts) of the loud sites"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

# ---------------------------------------------------------------- PRIORITY 2: T-X17 temporal response class
cand(id="P-F02", parent="T-X17", family="temporal_semantics", axis="response geometry x lineage x depth", type="parameterized-response-map", deformation="B",
     delta="RAW RESPONSE GEOMETRY per program across three constructions, kept as a vector, not a label: W0 D=2 (two PUTs to one tag, then the ask): idle tick BETWEEN the two PUTs, before the ask, before the first PUT; W2_K2: idle tick between the PUTs, before the first ask, before the second ask (P-E02); W0 D=1: empty tick before the ask (P-E01). Programs: viable parents of all strata, their walkers archived at depth 4 / 8 / 16 (class ALONG the neutral walk), C4-08 tops. Cross-world read: every program is read on every construction regardless of its native world, so a lineage's geometry travels or does not. Distances between response vectors within lineage (parent vs walker depths) and between strata; a clustering of the 7-dimensional vectors with the number of clusters chosen by a gap statistic, so the two classes named in cycle 3 can be refuted by a third.",
     unchanged="episode content, programs, displacement ruler, walk seeds", attacks="the two-class reading (ask-time bound vs input-schedule bound) and its heritability along neutral walks; whether the class is a property of the organism or of the world it is read in",
     nonredundant="D=2 same-tag idle tick never built; class along walks never read; cross-world reads never done on one vector", cost_minutes=5,
     continuation=["K=3 constructions", "idle tick inside a PUT tick's payload", "class after damage"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=3))

cand(id="P-F03", parent="T-X17", family="temporal_semantics", axis="evolution under idle ticks x transplant", type="evolution-transplant", deformation="B",
     delta="EVOLUTION UNDER IDLE TICKS in the Nestor evolver: selection on W0 and on W2_K2, each with the generation's episodes carrying an idle tick at a random position (before an ask / between PUTs / before the first PUT, each with probability 1/3) in half of the episodes, versus plain episodes; 40 generations, 2 seeds, N 96 from the walkers. Read the response geometry (P-F02's vector) of the top-32 of every arm. TRANSPLANT: the W0-idle-evolved top-32 seeded into W2_K2 selection (plain) for 20 generations and the W2-idle-evolved top-32 into W0 selection for 20 generations; the geometry read again after transplant. Does the class travel with the organism (unchanged after 20 generations elsewhere) or is it reconstructed by the world (converges to the host world's class)?",
     unchanged="grammar, worlds, displacement ruler, evolver births", attacks="whether the temporal response class is heritable structure or a world-imposed read-out",
     nonredundant="no lineage was ever evolved under idle ticks; no transplant exists", cost_minutes=10,
     continuation=["longer transplant", "idle-tick probability dose", "transplant of single programs without selection (neutral walk in the host world)"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=3))

# ---------------------------------------------------------------- PRIORITY 3: T-X16 damage as pruning
cand(id="P-F04", parent="T-X16", family="representation_ecology", axis="price x damage x fraction x rate window", type="economics-reversal", co_parents=["T-E06", "T-E07"],
     delta="DAMAGE_EFFECT vs PRICE_MEDIATED_PRUNING: structural price {0.01 (as e06), 0} x damage {none, tape, tree, both} x fraction {.05, .1, .2} x rate {.55, .6, .65, .7, .75} (the exclusion window at .05 steps) x f0 .1 x 3 attempt ids, 240 generations (longer inside the window); draw-matched by construction (separate damage rng; none == sham check retained on one fraction). Read: final TREE at 160 and 240, coexistence, extinction, units per label, per price. Prediction written before the run: if the benefit of damage to the damaged substrate vanishes at price 0, the cycle-3 effect is PRICE_MEDIATED_PRUNING; if it persists at price 0, DAMAGE_EFFECT proper; if it reverses sign, the economics hide a further coordinate.",
     unchanged="e06 world otherwise, sharing, item streams, mutation, graph targets", attacks="the pruning reading of P-E06 and the sign of 'damage robustness' under a price",
     nonredundant="price 0 was never run; the window was never resolved; fraction never dosed", cost_minutes=10,
     continuation=["price dose", "damage to registers only (TAPE) vs nodes only (TREE)", "heritable vs non-heritable damage"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-F05", parent="T-E06", family="representation_ecology", axis="resident pre-adaptation x geometry x rate", type="protocol-separation", co_parents=["T-X14", "T-X04", "T-X16"],
     delta="PRE-ADAPTED vs FROM-SCRATCH residents across the window: e06's invasion protocol (resident alone 40 generations, invader at 10 percent for 80 generations) in both directions at rates {.5, .55, .6, .65, .7, .75, .8} x 3 ids, beside from-scratch mixing at f0 .1 / .9 at the same rates (P-E06's protocol, 120 generations); and GEOMETRY x RATE: phi {0, .5, 1} (P-A08's mixture) x rate {.5, .6, .7, .8, .9, 1.0} x f0 .1 x 2 ids, 160 generations. Read: does the exclusion window exist under pre-adapted residents; does it move with geometry; is P-D05's rate-set direction a protocol effect.",
     unchanged="e06 world, sharing, prices, mutation", attacks="T-X14 (rate sets direction) vs P-E06 (a window): which protocol the pool should believe; T-X04's geometry axis crossed with rate for the first time",
     nonredundant="the two protocols were never run side by side; geometry x rate never run", cost_minutes=8,
     continuation=["resident adaptation dose (gens_resident)", "invader fraction dose"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

# ---------------------------------------------------------------- PRIORITY 4: P-E03 replication with a viable drift control
cand(id="P-F06", parent="T-ARCH4/M1", family="arch4", axis="selection vs neutral drift x seeds x generation dose", type="replication-confirmatory", deformation="A",
     delta="P-E03 REPLICATED over 6 seeds with the failed drift arm REPLACED by a NEUTRAL-BAND DRIFT control: parent chosen uniformly (same draws as selection), the child replaces its parent only if its reward lies within the equivalence band of the parent's (else the parent is copied) - competence is retained without a fitness ordering; generation dose: the population archived at G 20 / 40 / 60 and the damage assay (P-D01 cells) applied to the top-32 (selection) / a 32-sample (drift) at each archive and to their ancestors, paired by ancestor. Reading rules as P-E03; promotion only if the selected contrast survives against the competent control at G60 in >= 4/6 seeds.",
     unchanged="grammar, worlds, damage cells, evolver births", attacks="P-E03's SELECTED reading (one seed pair; run 1 read INHERITED) and D082",
     nonredundant="the drift contrast was never valid; generation dose never read", cost_minutes=12,
     continuation=["selection on W0 / W1_d4", "n_ops 2 births", "band width of the drift control"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=2, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=1, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

# ---------------------------------------------------------------- secondary manifolds
cand(id="P-F07", parent="T-X13", family="robustness_cross", axis="damage probability x generation dose x fraction-matched assay", type="parameterized-dose",
     delta="Weather in Proteus (P-E09) with damage probability {.25, .5, .75} x generations {60, 120}, 2 seeds; sham arm at each; assay on top-32 with FIXED-k and FRACTION-MATCHED damage and the persistent-words / length trajectories; does the extra carried state selected under weather become protective under fraction-matched damage, and at which dose?",
     unchanged="evolver, grammar, worlds", attacks="P-E09's NEITHER reading (state up, loss unchanged at 60 generations)", nonredundant="dose never varied; fraction-matched assay never applied", cost_minutes=10,
     continuation=["operand weather", "persist frozen per arm"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=2,
                 regime_newly_reachable=2, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=1))

cand(id="P-F08", parent="T-E03", family="coalitions", axis="mask gene x burden", type="stasis-escape", anti_gravity=True,
     escapes_stasis="the refined escape: an operator whose zeros PERSIST across births - a heritable binary mask gene (effective weight = w * mask; mask bits flip with probability .02 per birth); attainability check first",
     delta="ATTAINABILITY FIRST: 30 generations of selection-free drift with the mask gene, 4 ids: the effective non-zero share must move by >= .10 or the candidate closes INSTRUMENT_UNATTAINABLE. If attainable: e03 treatment under sel = score - lambda * nz_share(effective), lambda {0, H}, 4 ids, MI excess / sparsity / precision / coverage.",
     unchanged="e03 world, organism otherwise, selection, 60 generations, MI ruler", attacks="T-E03's stasis scope through its recorded escape", nonredundant="a persistent zero was never representable", cost_minutes=4,
     continuation=["mask flip dose", "magnitude burden"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=1, independent_intersection=2,
                 regime_newly_reachable=3, information_gain=2, delta_novelty=2, mechanism_discrimination=2, cost_now_lower=3,
                 null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=1))

# ---------------------------------------------------------------- anti-gravity: attempts to break the new coordinates from outside
cand(id="P-F09", parent="T-X15", family="cross_substrate", axis="length x robustness in another representation", type="serendipity-cross", serendipity=True, co_parents=["T-E06", "T-E07"],
     delta="T-X15 READ IN e06's TAPE and TREE genomes: evolved bodies (final populations of e06 runs at rates .5 and 1.0, 3 ids, 80 generations, single-substrate arms) damaged blind at FIXED k (2 instructions / 2 internal-node contractions) and FRACTION-MATCHED (.15); score loss vs body size and vs live registers (TAPE's carried state) and vs tree depth (TREE's structure); the same NOP-pad manipulation on TAPE bodies (append inert instructions) and DUPLICATE (append a copy). If loss falls with length under fixed k in TAPE as in Proteus and the pad/duplicate pattern matches P-F01's, the coordinate is cross-substrate; if TAPE and TREE disagree, representation is a coordinate.",
     unchanged="e06 world, evaluation, price list", attacks="T-X15's portability beyond Proteus programs", nonredundant="no damage-vs-length read exists in e06; the pad/duplicate manipulations never applied there", cost_minutes=5,
     continuation=["registers-only damage", "depth-matched trees"],
     scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))

cand(id="P-F10", parent="T-X16", family="cross_substrate", axis="price-mediated pruning in Proteus", type="serendipity-cross", serendipity=True, anti_gravity=True, co_parents=["T-ARCH4/M1", "T-X13", "T-X05"],
     delta="T-X16 TRANSPLANTED INTO PROTEUS: the Nestor evolver with fitness = reward - lambda * n_instr (lambda {0, 1/128, 1/32}) x weather {off, on (p=.5, 2 instructions)} x 2 seeds, 60 generations on W2_K2; sham at lambda 0. Under a price, does weather become NEUTRAL or BENEFICIAL (final reward and length under weather vs sham at each lambda) as in e06, or does it stay a cost? If the price flips the sign of weather's effect on the population in Proteus too, price-mediated pruning is cross-substrate; if not, it is an e06 economics artefact.",
     unchanged="evolver, grammar, worlds, damage assay", attacks="T-X16's generality and T-X13 (weather's effect on state under a price)", nonredundant="length was never priced in the Proteus evolver", cost_minutes=8,
     continuation=["price on persistent words instead of length", "tax x weather dose"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2,
                 null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-F11", parent="T-X17", family="cross_substrate", axis="temporal response after damage", type="deformation-cross", anti_gravity=True, co_parents=["T-X15", "T-ARCH4/M1"],
     delta="DOES DAMAGE CHANGE THE TEMPORAL CLASS? P-F02's response vector read on every program before and after fixed-k and fraction-matched damage (the draws of P-F01), and after the NOP-pad / duplicate / persist-none manipulations: if the class survives damage that destroys reward (D3 outcomes), it is a property of the surviving structure, not of the function; if pad or duplicate change the vector, length is entangled with timing; if persist-none collapses every vector to immunity (P-E01 said it does), carried state is the timing coordinate and T-X15 and T-X17 are one node.",
     unchanged="constructions, damage draws", attacks="the separateness of T-X15 and T-X17; whether the temporal class is functional or structural", nonredundant="temporal response was never read after damage", cost_minutes=4,
     continuation=["class of D7 (improved) children", "class along P-E05's no_growth walks"],
     scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3,
                 regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3,
                 null_becomes_contrast=0, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))


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
            c["batch"] = "F"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
    RS.require_ascii_safe(OUT)
    print("appended", added)


if __name__ == "__main__":
    main()
