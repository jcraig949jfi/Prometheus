"""Reactivated trajectory: Archaeon Campaign 4 (damage geometry / evolvability), descended into the
Nestor pool as T-ARCH4 with SCOPED child nodes. Immutable; append only; idempotent by id.

COMPUTATIONAL SCOPE DECLARATION (verbatim from the operator directive, restated here so that no
reader depends on the prompt): this work is exclusively computational artificial-life /
algorithm-search research. Terms such as organism, genome, mutation, selection, lineage,
inheritance, recombination, population, adaptation, damage, repair and evolution refer only to
software objects: integer arrays, programs on a bounded virtual machine, graph structures,
search operators and simulated populations. There are no living organisms, no biological
materials, no wet-lab procedures, no pathogens, no genetic engineering, no biological sequence
design and no physical-world biological experimentation.

Original records are preserved unchanged at origin/main 9cd33ff1e under archaeon/campaign4/;
nothing there is edited. A safeguard refusal cannot disposition an experiment; such events are
recorded below as INFRASTRUCTURE_BOUNDARY and never as NULL / REJECTED / UNREACHABLE.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

POOL, STATE, EVID = HERE / "TRAJECTORIES.jsonl", HERE / "STATE.jsonl", HERE / "EVIDENCE.jsonl"
ORIGIN = "archaeon/campaign4 @ origin/main 9cd33ff1e (Archaeon[m2-49ee5a4d], 2026-09-17..18)"
R, E = [], []


def rec(**k):
    R.append(k)


def ev(**k):
    E.append(k)


rec(trajectory_id="T-ARCH4", kind="experiment-campaign", origin=ORIGIN, age="2026-09-18 09:40Z",
    scope="computational artificial life on the Proteus foundry VM: integer programs, a bounded interpreter, search operators; no biology",
    originating_question_verbatim="Asked: can the Foundry expose a region in which edits usually produce different, bounded, coherent computation rather than no change or catastrophe, and does access to that region improve later discovery? (CAMPAIGN_REPORT.md section 0)",
    derived_operationalization="ten preregistered slots on one frozen substrate (engine 9.0.1 / 699ca0f9, grammar proteus.grammar.v0.4, affordance table of 25 opcodes with NOP 0 / HALT 1, profile pfp1:625bc70456ebfa20, 57 starting program variants in 4 strata: gen0_random 12, w0_solver 15, shelf 19, delay_general 11): C4-01 single-edit census (12 operators x 8 draws x 57 parents, classes D0..D7 by D4-003), C4-02 radius curve (1..16 grammar applications), C4-03 local failure vs death, C4-04 addressing damage, C4-05 neutral-network walk (4 walkers x 16 steps, band 1/16 around the ORIGINAL parent, archived depths 0/2/4/8/16 exposed to held-out worlds), C4-06 recombination vs mutation-only (W2_K2 summit), C4-07 cost of insulation, C4-08 constructed robustness (selection with 1 vs 2 edits per birth), C4-09 lateral ecology (four worlds, rescue by measured reward), C4-10 held-out trial",
    translation_loss="the directive's 'invalid operation', 'fizzle event' and 'free insulation' have NO extension on a total interpreter whose modulo decode IS the instruction set (932/932 parent opcode words are outside the table); C4-03, C4-07 and C4-08's removal arm are REPRESENTATION_BLOCKED, so the fault-boundary half of the question was never posable on this substrate",
    world_substrate="archaeon.wse.worlds WorldSpec family: W0 (K=1, 4-bit), W0_heldout, W1_d1, W1_d4, W2_K2 (K=2); episodes_for(spec, 20260921, family, index, n=16); reward_per_ask, floor 3/16, band 1/16",
    representation="manifest {genome: list of 32-bit words, 4 words per instruction (opcode, a, b, c/imm), n_regs, tape_words, tick_budget, out_cap, persist, code_writable}; opcode = word mod 25; operands mod n_regs; addresses mod tape_words; jumps mod tape (proteus/foundry/vm.py)",
    search_process="grammar.mutate with 12 frozen-weight operators (insertion, deletion, duplication, movement, replacement, operand_perturbation, reference_redirection, region_swap, splice, randomization, unreachable_removal, config_perturbation; zeroing REMOVED); archaeon.wse.evolve.Evolution (tournament, N up to 200, G 100, descend_fn hook, inject); neutral walk with a proposal hook",
    pressure="reward_per_ask on the parent environment; selection slots reward W2_K2; no term names a representational property",
    ruler="D-class flow tables with Wilson bands; behavioural displacement (normalised Hamming over 16 asks); TVD between operator distributions; preregistered predictions written to be lost per slot; CAPABLE_NEGATIVE harness labels",
    compute_budget="about 22 minutes of compute across ten slots (05:54Z-09:35Z wall); 1,255 engine records, 0 errors on every attempt of record; 11 attempts for 10 slots (C4-01 a01 failed at publish, D4-005)",
    result="CAMPAIGN DISPOSITION NO_CONDITION_SELECTED (C4-10). Slots: C4-01 SUPPORTED (map), C4-02 SUPPORTED thin, C4-03 REPRESENTATION_BLOCKED, C4-04 NEGATIVE pooled (.087 < .10) with insertion +.215 / movement +.193, C4-05 NEGATIVE as written (exaptation .016 -> .043 vs .006 single edit), C4-06 INCONCLUSIVE (0/6 crossings both arms; mate-splice births 8 points less viable), C4-07 REPRESENTATION_BLOCKED, C4-08 ROBUST_WITHOUT_MECHANISM (loss .42 -> .19 -> .13 by neutrality and length 19 -> 62), C4-09 INCONCLUSIVE (rescues persist and take over, improve 1/3 seeds on one live world; 3 worlds pre-solved), C4-10 NO_CONDITION_SELECTED",
    failure_surface="(1) no fault boundary to widen: total interpreter, modulo decode; (2) cliff not slope: edits either leave the answer vector untouched or replace most of it, 1-3% between, at every radius; distance predicts P(destruction) not degree; (3) no single or multi-step random edit improved any parent (D7 0/5,472 and 0/2,280); exaptive edits 0.6% and shelf-concentrated; (4) neutral network large, connected, cheap (188/188 walkers to depth 16 at ~55% acceptance) with exaptation growing with depth but under the bars; (5) recombination adds damage without reach; (6) selection accumulates robustness as neutrality + length; (7) lateral rescue cheap and invasive without improving the live world; (8) three ecology worlds and three held-out worlds were pre-solved by the starting parents (design defect, D4-013/D4-014)",
    anomalies=["W0 solvers drift SILENTLY on W0 (behavioural diversity .002 at depth 16) and loudly elsewhere (.17 on W1_d1)", "the 10 fully degenerate gen0_random parents form a swamp by construction (acceptance 1.0 at every depth), reported apart", "insertion and movement carry a reference effect (+.215/+.193 loss when a reachable jump breaks) while deletion/splice/duplication carry ~0", "mate-splice births are 8 points LESS viable than mutation births with no novelty gain", "rescued lineages TAKE OVER receiving populations (survival .30-.55) without improving them", "C4-08 harness label CAPABLE_NEGATIVE was a sign-convention artefact kept beside the reading"],
    unrun_interventions=["a representation with a distinguishable insulation event (narrow in-table encoding; trap-and-continue on undefined words) - named by the report as Campaign 5's substrate", "deeper walks (32, 64)", "an ecology on UNSOLVED worlds at equal total budget", "checking any world family against the starting parents BEFORE choosing it", "any variation of mutation geometry other than radius (block vs distributed, operand vs opcode, length balance)", "any variation of population structure, tournament strength, deme structure", "damage families other than grammar edits (targeted vs random structural damage, timing relative to reproduction)"],
    fossils=["57 starting parents: archaeon/campaign4/STARTING_POPULATION.json (manifests, ancestries, strata)", "C4-05 walk steps (steps.json.gz): every walker regenerable from seeds and digest-verified", "per-slot attempts/aNN/ rows.json(.gz), FLOW/CURVES/PROXY/REFERENCE/ROBUSTNESS/WALK/ECOLOGY/TRIAL tables", "DAMAGE_GEOMETRY_MAP.json"],
    assumptions_at_time=["the frozen grammar's operator weights ARE the mutation geometry (radius = number of applications)", "one decode rule (modulo) is the substrate", "the neutral band is defined relative to the original parent (no ratchet)", "the four C4 worlds are the environment family; exaptation is measured against them", "16 steps is a walk; 100 generations is selection", "the starting parents' competence on candidate worlds need not be checked (falsified twice)"],
    later_changes_relevant=["CW01 loop machinery (relabelling nulls, ability-adjusted contrasts, blind rulers) and its results: hitchhiking floor = selection strength (P-A10), damage families as evolutionary pressure (e07, P-B03), burden accounting (e08)", "the report's own Campaign 5 pointers"],
    last_perturbation="C4-10 2026-09-18 09:35Z", marginal_information_history=["ten slots: the map is material; the campaign claim is not made"],
    stasis_state="ACTIVE")

# scoped child nodes: stasis, when it comes, is declared on these, never on the parent
for sid, scope, desc in (
        ("T-ARCH4/R1", "representation=modulo-decode-v0.4", "the frozen substrate as run: modulo decode, 25-opcode table, grammar v0.4 frozen weights"),
        ("T-ARCH4/M1", "mutation_family=frozen-weight-12-operators", "radius = repeated applications; no block/distributed/operand-vs-opcode/length-balance variation tried"),
        ("T-ARCH4/W1", "world=C4-four-worlds-4bit", "W0 / W1_d1 / W1_d4 / W2_K2 as the environment family; held-out = W0_heldout + others"),
        ("T-ARCH4/P1", "population=wse-Evolution-tournament", "panmictic tournament evolver, N 50-200, G 100; recombination = the evolver's mate policy"),
        ("T-ARCH4/D1", "damage_rescue=grammar-edits+lateral-by-reward", "damage = grammar edits; rescue = lateral entry by measured reward, B=24, replace worst"),
        ("T-ARCH4/S1", "search_depth=walk16-G100", "walk depth 16, 4 walkers, 32 proposals; selection 100 generations")):
    rec(trajectory_id=sid, kind="scoped-node", origin=ORIGIN, parent="T-ARCH4", scope=scope, age="2026-09-18",
        originating_question_verbatim="(scoped node of T-ARCH4) " + desc,
        derived_operationalization=desc, translation_loss="see parent", world_substrate="see parent", representation="see parent",
        search_process="see parent", pressure="see parent", ruler="see parent", compute_budget="see parent",
        result="see parent", failure_surface="the parent's findings AS MEASURED under this scope only",
        anomalies=[], unrun_interventions=[], fossils=[], assumptions_at_time=[], later_changes_relevant=[],
        last_perturbation="Campaign 4", marginal_information_history=[], stasis_state="ACTIVE")

# infrastructure boundaries: recorded, never dispositioning
ev(trajectory_id="T-ARCH4", perturbation_id="C4-REH-1", kind="INFRASTRUCTURE_BOUNDARY", status="MODEL_REFUSAL",
   summary="2026-09-17: launch-gate item G2 (integration rehearsal C4-REH-1) set aside SKIPPED_SAFEGUARD_TERMINOLOGY after roughly seven attempts were interrupted by an automated safeguard acting on the lead's own output (messages of very different length, one of eight words with no commands; tails of command sequences lost; not predictable from content). Diagnosed by the operator as vocabulary inherited from the evolutionary-computation framing. Item intact and resumable; NOT a scientific state (archaeon/campaign4/DISPOSITION_C4-REH-1.md, HANDOFF_2026-09-17.md).",
   material_change=False, detail={"what_was_not_done_then": "the deliberate interruption stage and the stages after it", "resolved": "later completed: S6 rehearsal executed through two engine kills at 87ab74a1a; G2 GREEN at 83568a0a7; campaign started on gate GREEN at 9632e95f8", "terminology_discipline": "DISPOSITION_C4-REH-1.md section 6 (prose only; no field, schema or identifier renamed)"})
ev(trajectory_id="T-ARCH4", perturbation_id="operator-directive-2026-09-18", kind="INFRASTRUCTURE_BOUNDARY", status="MODEL_REFUSAL",
   summary="The operator's reactivation directive states the trajectory 'twice encountered' safeguard interruptions. The committed artifacts document ONE episode (C4-REH-1, multiple attempts, 2026-09-17) and the handoff it forced; no second episode is recorded in archaeon/campaign4 or roles/Archaeon/journal. Recorded as reported; treated as infrastructure, never as evidence about the hypothesis.",
   material_change=False, detail={"searched": ["archaeon/campaign4/**", "roles/Archaeon/journal", "git log --all -i --grep"]})


def main():
    existing = set()
    if POOL.exists():
        for line in POOL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.add(json.loads(line)["trajectory_id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
        for r in R:
            if r["trajectory_id"] in existing:
                continue
            r = dict(r)
            r["recorded"] = ts
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": r["trajectory_id"], "ts": ts, "state": r["stasis_state"],
                                 "reason": "reactivated into the Nestor pool by operator directive; scoped nodes carry any future stasis",
                                 "marginal_information_history": r.get("marginal_information_history", [])}, ensure_ascii=True) + "\n")
            added.append(r["trajectory_id"])
    seen = set()
    if EVID.exists():
        for line in EVID.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                seen.add((e["trajectory_id"], e["perturbation_id"]))
    with EVID.open("a", encoding="utf-8") as fh:
        for e in E:
            if (e["trajectory_id"], e["perturbation_id"]) in seen:
                continue
            e = dict(e)
            e["ts"] = ts
            fh.write(json.dumps(e, ensure_ascii=True) + "\n")
    for p in (POOL, STATE, EVID):
        RS.require_ascii_safe(p)
    print("appended", added, "+ %d boundary events" % len(E))


if __name__ == "__main__":
    main()
