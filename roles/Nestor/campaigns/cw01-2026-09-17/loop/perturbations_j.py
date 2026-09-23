"""Candidate perturbations, batch J (cycle 8): evolutionary accessibility. P-J01 (successor worlds) was
preregistered in cycle 7 and runs first. Computational scope: integer programs on a bounded VM."""
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


cand(id="P-J02", parent="T-R01", family="accessibility", axis="mutational distance measured in the VM", type="instrument-census", deformation="D", co_parents=["T-X21", "T-ARCH4/M1"],
     delta="ACTUAL MUTATIONAL DISTANCE for 6 identity-plateau genomes (P-I01 world-A tops with a regime-bearing register identified by P-I02): (1) WITNESSES - hand-constructed conditional programs: XOR-1 witness = one XOR instruction (out_reg ^= regime_reg) inserted before the reached OUT; XOR-15 witness = LDC 15 + MUL by the regime register + XOR inserted before the OUT; each VERIFIED on held-out sets (an instrument / positive control, not a discovery); (2) EXHAUSTIVE STRUCTURED ONE-EDIT CENSUS - every insertion of (op in XOR/ADD/SUB/OR/AND, a = out_reg, b = out_reg, c = any register) at every position: fitness on A' (xor 1) and A (xor 15); (3) SAMPLED GRAMMAR NEIGHBOURHOOD - 2000 one-operator mutants under the frozen grammar per genome: shares beneficial / neutral / deleterious on A' and A (p_hit = share beneficial; expected hits per generation = 96 p_hit); (4) BOUNDED TWO-EDIT - 2000 two-operator mutants on A (xor 15); (5) routes named per world: BENEFICIAL_PATH (a one-edit beneficial mutant exists and the grammar samples it, p_hit > 0), NEUTRAL_BRIDGE (two-edit beneficial via a neutral intermediate), DELETERIOUS_VALLEY (only via a deleterious intermediate), UNREACHABLE_ENCODING (no instance of any operator yields it), SEARCH_FAILURE (p_hit > 0 yet P-J01 failed).",
     unchanged="genomes, worlds, grammar", attacks="the claimed distance of the regime transform from the plateau", nonredundant="no neighbourhood census exists", cost_minutes=8,
     continuation=["census on B'/C' genomes", "three-edit neighbourhoods"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=3))

cand(id="P-J03", parent="T-X17", family="gateway", axis="scaffold stripping", type="gateway-test", deformation="G", requires=["P-J01"], co_parents=["T-X21"],
     delta="SCAFFOLD STRIPPING: the earliest crossing lineage of A' (if any; else the plateau population seeded with 8 verified XOR-1 witnesses, FLAGGED witness-seeded) is exposed to progressively harder transforms - XOR 3 then XOR 15 (the original world) - for 60 generations each (2 seeds), against (2) the matched identity-plateau lineage (P-I01 world-A final population, same 120 generations, no scaffold) and (3) a fresh walker population; crossing per stage and generation of first crossing. Then the scaffold is REMOVED: the XOR-15-crossed population evolves 60 generations in a regime-0-only world (identity is enough) and is re-tested on the XOR-15 held-out sets (persistence / decay of the machinery); then a different conditional transform (XOR 5) is posed to it and to naive controls (reuse).",
     unchanged="evolver, worlds' structure", attacks="whether prior evolution of conditional routing changes accessibility to transforms behind the zero-gradient plateau (the gateway phenomenon)", nonredundant="no lineage ever carried conditional machinery into a harder world", cost_minutes=12,
     continuation=["scaffold length dose", "gateway under B'/C'"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=3))

cand(id="P-J04", parent="T-X21", family="accessibility", axis="forensics after a crossing", type="mechanism-forensics", deformation="M", requires=["P-J01"],
     delta="FORENSICS AFTER A CROSSING (crossed tops of P-J01; NOT_APPLICABLE per world if none crossed): A' - corrupt the regime-bearing register at the ask and disable each control instruction (JZ / JNZ / JMP -> NOP) in turn: the answer must depend causally on the current regime; B' - identical decision-time observations reached through different histories (cue flipped), the candidate persistent register erased / overwritten between cue and ASK: a history-dependent lineage must lose the behaviour under the right intervention; C' - against the CUE-FOLLOW ceiling: cue reliability .6 / .9, block 3 / 5 / 8, shuffled histories, state reset mid-block, unexpected transitions (irregular blocks), held-out sequences; immediate cue following vs evidence accumulation vs hysteresis vs prediction named only from interventions.",
     unchanged="P-J01 organisms", attacks="mechanism naming without intervention", nonredundant="new organisms", cost_minutes=6,
     continuation=["register-level lesion series"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-J05", parent="T-X21", family="accessibility", axis="first-crossing genealogy", type="genealogy", requires=["P-J01"], co_parents=["T-R01"],
     delta="FIRST-CROSSING GENEALOGY: every generation's population of the P-J01 plain runs is stored with parent pointers and operator records; the crossing generation g* is the first at which the best-by-training individual scores >= threshold on held-out sets; the lineage is reconstructed 10 generations before and 5 after g* with fitness and operator at every step; the route is named from the chain: ONE_BENEFICIAL_MUTATION, NEUTRAL_PRECURSOR_THEN_BENEFICIAL, RECOMBINATION (n/a: mutation only), DELETERIOUS_INTERMEDIATE_RESCUED, or OTHER; the genomes along the chain are preserved for forensic replay. NOT_APPLICABLE per world if no crossing.",
     unchanged="P-J01 populations", attacks="the assumption that the final organism is the object; the path is", nonredundant="no genealogy was ever stored", cost_minutes=3,
     continuation=["replay the crossing under other seeds"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=3))

cand(id="P-J06", parent="T-X17", family="gateway", axis="gateway structure: novel transforms", type="gateway-test", requires=["P-J03"], co_parents=["T-X21"],
     delta="GATEWAY STRUCTURE: descendants that carry conditional machinery (P-J03's XOR-15-crossed lineage, or the witness-seeded lineage, flagged) are given NOVEL conditional transforms never used in their evolution - regime 1 expects (v + 1) mod 16 (a different operator) and v XOR 5 (a different constant) - for 60 generations, 2 seeds, against the identity-plateau lineage and a fresh population: generations to first crossing; REUSE read by intervention: does the same regime-bearing register control the new answer (register transplant) and does the same control path carry it (control-instruction knockouts). A mechanism that changes the accessible neighbourhood is a candidate evolutionary primitive; one that solves only XOR 1 is local.",
     unchanged="evolver, worlds' structure", attacks="whether acquired machinery alters what can evolve next", nonredundant="no descendant of a crossing was ever exposed to a novel transform", cost_minutes=8,
     continuation=["transform families beyond XOR / ADD"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=3))

cand(id="P-J07", parent="T-X21", family="accessibility", axis="selection dynamics of a beneficial mutant", type="anti-gravity", anti_gravity=True, requires=["P-J02"], co_parents=["T-X01"],
     delta="INVASION OF A SINGLE WITNESS: the identity-plateau population (P-I01 world A, final) with ONE verified XOR-1 witness inserted (1/96) evolves in A' for 40 generations under tournament 3 with 16 asks per generation (the P-I01 regime) vs 64 asks (less fitness noise) vs tournament 2, 4 seeds each; the witness lineage's frequency every generation (ancestor tag), fixation / loss, generations to fixation. If a beneficial one-edit mutant exists (P-J02) but is lost by noise or drift at 16 asks, P-J01's failure is a SEARCH_FAILURE of selection dynamics, not of encoding.",
     unchanged="plateau population, world A'", attacks="cycle 8's assumption that accessibility is about encoding distance rather than selection dynamics", nonredundant="the fate of a single beneficial mutant was never tracked", cost_minutes=6,
     continuation=["population size dose only if dynamics are the limit"], scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=3, cost_now_lower=3, null_becomes_contrast=2, inconclusive_now_posable=3, underexplored_hard_to_operationalise=2))

cand(id="P-J08", parent="T-ARCH5", family="representation", axis="grammar B neighbourhood", type="serendipity-representation", serendipity=True, requires=["P-J02"], co_parents=["T-R01"],
     delta="REPRESENTATION AS AN ACCESSIBILITY COORDINATE: the sampled one-operator neighbourhood (2000 mutants per plateau genome) under grammar B vs grammar v0.4 on A' and A: p_hit (share beneficial), shares neutral / deleterious; if grammar B reaches the XOR-1 witness class more often (or never), the operator set is an accessibility coordinate.",
     unchanged="plateau genomes, worlds", attacks="nothing yet: an unexplained dependence hunt", nonredundant="grammar B's neighbourhood was never censused", cost_minutes=3,
     continuation=["grammar-B evolution in A'"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=2, underexplored_hard_to_operationalise=2))

cand(id="P-J09", parent="T-X20", family="temporal_semantics", axis="witness geometry", type="serendipity-cross", serendipity=True, requires=["P-J02"], co_parents=["T-X17"],
     delta="GEOMETRY OF CONDITIONAL MACHINERY: the P-F02 curve set of the XOR-1 and XOR-15 witnesses and of every crossed organism (P-J01 / P-J03 / P-J06, if any) against their plateau parents: does acquiring conditional routing change the temporal response geometry (a shape outside the manifold, or a move between attractors), i.e. are context computation and temporal geometry coupled in this substrate?",
     unchanged="constructions", attacks="the separateness of the temporal manifold and context computation", nonredundant="no conditional program was ever read on the constructions", cost_minutes=2,
     continuation=["geometry along the crossing genealogy"], scores=dict(attacks_old_assumption=2, failure_surface_perturbable=2, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=2, information_gain=3, delta_novelty=3, mechanism_discrimination=2, cost_now_lower=3, null_becomes_contrast=1, inconclusive_now_posable=1, underexplored_hard_to_operationalise=2))


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
            c["batch"] = "J"
            fh.write(json.dumps(c, ensure_ascii=True) + "\n")
            added.append(c["id"])
        fh.write(json.dumps({"id": "P-J01", "amend": True, "recorded": ts, "delta_addendum": "CYCLE 8 (runs FIRST): every generation's population stored with parent pointers and operator records (genealogy); worlds read SEPARATELY (A' immediate conditional; B' recruiting existing persistent state; C' exceeding cue-following); crossing generation per run"}, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(OUT)
    print("appended", added, "+ P-J01 amended")


if __name__ == "__main__":
    main()
