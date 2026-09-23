"""Trajectory records for e05-e09 and the cross-cutting anomalies they exposed (immutable; append-only).

Run once to append to TRAJECTORIES.jsonl (idempotent by trajectory_id). Records describe what
happened under that world, representation, search, pressure, ruler and budget; they never
resolve the hypothesis. Evidence appended later goes to EVIDENCE.jsonl, never here.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

POOL = HERE / "TRAJECTORIES.jsonl"
STATE = HERE / "STATE.jsonl"

R = []


def rec(**k):
    R.append(k)


rec(trajectory_id="T-E05", kind="experiment", origin="cw01-e05", age="2026-09-18 03:26",
    originating_question_verbatim="Do mixtures of individually marginally useful organisms outperform their parts (superadditivity), and is the composition law load-bearing?",
    derived_operationalization="8-gene real-valued inclusion vector over a capability pool; conjunctive vs disjunctive composition laws; DiD of normalised information superadditivity BEST vs WORST sets; 4 attempt-stable latent worlds; 12 replicates after replication lane",
    translation_loss="an 8-gene inclusion vector, not a rich program; the 'organism' is a set membership",
    world_substrate="campaign toy world world_e05.py (composition economics)", representation="8 real genes",
    search_process="tournament GA, attempt-seeded", pressure="task score with carry cost stored separately",
    ruler="DiD nsa(BEST,conj)-nsa(BEST,disj) - (WORST...) vs 8-block sham null (contract c80b5bfd)",
    compute_budget="30 s per attempt; 726 rows",
    result="NULL: beats-best-single 12/12, interaction positive 11/12, superadditivity clears null 7/12, ablation load-bearing 7/12; sa==load-bearing 12/12",
    failure_surface="superadditivity is a property of the DRAWN WORLD (r03/r04 sub-additive), not of measurement; canonical a01 alone read COMPLETE",
    anomalies=["superadditivity and full load-bearing fail in EXACTLY the same replicates (12/12 correlation)", "r10 returns did_points -14.45 (negative interaction)", "disjunctive term stable (-22..-27) across worlds because it is coverage overlap; conjunctive term swings 33 points"],
    unrun_interventions=["conjunctive_fraction sweep declared in WORLD.json, never run", "predicting composability from capability structure BEFORE running (needs a new preregistration)"],
    fossils=["rows/cw01-e05-a01.jsonl 726 rows b942af7aa", "REPLICA lane 8 extra seeds, CROSS_LANE_COMPARISON 381 leaf comparisons"],
    assumptions_at_time=["a world either composes or does not, independent of which set is chosen", "4 replicates suffice"],
    later_changes_relevant=["e08 burden accounting (per-organism resource vector) exists", "12-replicate dataset exists for a predictor test"],
    last_perturbation="replication lane 2026-09-18 (8 extra seeds)", marginal_information_history=["a01 -> NULL at 4 replicates: material", "12 replicates: rate 7/12, r10 negative: material"],
    stasis_state="ACTIVE")

rec(trajectory_id="T-E06", kind="experiment", origin="cw01-e06", age="2026-09-18 07:23",
    originating_question_verbatim="Do representational forms acquire different ecological roles under shared environmental pressure - persistence, invasion, displacement, coexistence, specialization, frequency dependence?",
    derived_operationalization="TREE (expression tree, subtree crossover) vs TAPE (register program, one-point crossover) on a substrate-neutral operation-graph target with a reuse axis; resource sharing per item; Q16 gate: non-degenerate, two-sided Delta(r), mutual invasibility",
    translation_loss="two small substrates, four reuse bands, one price list; 'ecological role' reduced to invasion/frequency dependence",
    world_substrate="world_e06.py (operation-graph targets, resource sharing)", representation="tree vs tape programs",
    search_process="tournament GA with assortative recombination by label", pressure="output score with resource splitting",
    ruler="beta = slope of interaction(f) = r_A(f) - s_solo vs control A relabelling band (never reached)",
    compute_budget="minutes per gate run",
    result="INCONCLUSIVE / DESIGN UNREACHABLE: mutual invasibility never held in 4 world iterations; TAPE invades TREE, TREE cannot invade TAPE",
    failure_surface="under this price list TAPE is universally at least as compact as TREE (n instructions vs ~2n+1 nodes); TREE's only plausible advantage is dynamic (subtree crossover) and never materialised; control A fixes at gen 26 vs drift ~96 (hitchhiking)",
    anomalies=["invasion direction REVERSES between the legacy tree-native target and the redesigned generator (target geometry controls who invades)", "Delta(r) changes sign across reuse bands but measured reuse is 0.00/0.07/0.17/0.07 vs requested 0/0.25/0.5/0.75", "D053: niche structure exists (Jaccard 0.531, 23 TREE-only / 15 TAPE-only items) and sharing reorders fitness (rho 0.629)"],
    unrun_interventions=["a price list or variation regime in which TREE has a genuine mechanical advantage", "control A hitchhiking fix (population structure)", "M3 cross-substrate recombination at equal yield"],
    fossils=["legacy tree-native target generator retained as adversarial fixture in world_e06.py", "QUALIFY_GATE.json two runs"],
    assumptions_at_time=["TREE compact and cheap (never measured; false under the price list)", "generation-zero fitness predicts invasibility (mis-aimed, replaced by evolved-resident invasion)"],
    later_changes_relevant=["e08's real TT organism with evolvable per-bond ranks is a third substrate", "e07 showed diagonal vs full recurrence does not change evolvability there"],
    last_perturbation="D056 reuse-realisation correction 2026-09-18 07:20", marginal_information_history=["4 world iterations: same P3 boundary each time: diminishing"],
    stasis_state="ACTIVE")

rec(trajectory_id="T-E07", kind="experiment", origin="cw01-e07", age="2026-09-18 08:00",
    originating_question_verbatim="Under bounded, representation-blind computational disruption, do lineages evolved under computational weather preserve or recover useful computation better than matched lineages evolved without that disruption?",
    derived_operationalization="464-parameter linear recurrent organism with 16 persistent memory cells on an accumulate-and-report task (theta rotated by an attempt-stable Q); transient deletion of a uniform random fraction of cells; STATIC/WEATHER/SHAMWEATHER arms; AURC normalised by own intact capability; ANCOVA with exact relabelling",
    translation_loss="a linear recurrent net, not a rich program; one damage family; no genome damage; recovery within lifetime only",
    world_substrate="world_e07.py", representation="A(16x16) B C b W = 464 reals (diagonal variant also built)",
    search_process="tournament GA, 2 (then 8) lifetimes per evaluation", pressure="task score only; weather is pressure not reward",
    ruler="c in AURC_l = a + b I_l + c[WEATHER], 12870 relabellings (never reached)",
    compute_budget="2 s per gate run; 96-lineage EXECUTE never run",
    result="INCONCLUSIVE / DESIGN UNREACHABLE: gate refused twice (P1 magnitude unattainable at f=0.20; P4 no separability because state use never evolved)",
    failure_surface="evolution never reaches state-dependent computation (intact 0.35-0.45 vs hand-built 0.74, state dependence ~0.05-0.09 at pilot and real budget); mutation scale x4 and init scale x5 collapse the population; 8 lifetimes/eval helps slightly",
    anomalies=["immediate retention rho0 0.80 at k=3 but AURC 0.944: fast re-accumulation hides damage under an area measure", "hand-built accumulator ridge needs coordinated moves (a up, B down) that mutation does not find", "the fitness trajectory swings 0.31->0.08->0.35 by theta-draw noise (floor is 0 when |theta|>1) - misread once as meltdown"],
    unrun_interventions=["P1 on rho0 or f>=0.44 with the attainability curve on record", "persistence as a bounded per-cell gene with input gain tied to (1-a)", "the damage family applied to an organism that HAS evolved state (e01's retention organism)"],
    fossils=["GATE_E07_run1.json, GATE_E07.json, PROBE_E07.json, PROBE2/3", "world_e07.py with lesion and diagonal paths"],
    assumptions_at_time=["state use would evolve in 40-120 generations from a 0.1-scale random genome", "AURC threshold 0.90 attainable at f=0.20 (false: needs f>=0.44)"],
    later_changes_relevant=["e01 DID evolve state retention (p_write 0.87, persist 45.6 steps) in its own world: a substrate where e07's question is posable", "e08 accounting shows how to freeze thresholds with attainability curves"],
    last_perturbation="lifetimes_per_eval 2->8 (Amendment 2) 2026-09-18", marginal_information_history=["run1 refusal: material (two defects found)", "probes A-G: material (evolvability boundary mapped)", "run2 refusal: not material (predicted)"],
    stasis_state="ACTIVE")

rec(trajectory_id="T-E08", kind="experiment", origin="cw01-e08", age="2026-09-18 10:16",
    originating_question_verbatim="Can evolution discover cheaper computational geometry when representational burden itself is costly?",
    derived_operationalization="the substrate's real tt_digits tensor-train policy on w13 with evolvable per-bond ranks and read mask; burden vector (bond, params, flops, bits); 2x2 tax x amputation; blinded held64 assay; capability-adjusted scalar burden with stratified randomisation",
    translation_loss="one world, one organism family; rank machinery joined to evolution for the first time; no crossover; 200 generations",
    world_substrate="w13 (wforge, the only R4 survivor) via primordial.soup.b1", representation="ragged TT: alpha, 20 cores at R_max 5, Wo, codebook, ranks, mask",
    search_process="tournament GA 128 x 200, substrate jitter + rank step + mask flip", pressure="charge minus lambda*scalar(B) in TAX arms; widest-bond truncation every 5 gens in AMP arms",
    ruler="c_tax in scalar(B)_l = a + b C_l + c_tax TAX + c_amp AMP, TAX labels permuted within AMP strata (contract 607f4671)",
    compute_budget="554 s EXECUTE, 960 rows",
    result="INCONCLUSIVE: 4 competent lineages per TAX level vs frozen minimum 6; no common support. Descriptive: scalar burden CONTROL 1.725 / TAX 0.834 / AMP 0.926 / TAX+AMP 0.512 at mean held64 156/155/156/171; params 2943/1199/768/377",
    failure_surface="held64 competence is a minority outcome in every arm (train8 selection overfits); the minimum count was frozen against a pilot that predicted marginal attainability (D066)",
    anomalies=["burden fell 2-3x under tax and under amputation at unchanged mean capability across ALL representatives, competent or not", "TAX+AMP has the HIGHEST mean held64 (171.2) and the lowest burden (0.512)", "non-competent excess rule passed: the tax did not remove competence relative to control"],
    unrun_interventions=["representatives selected on a disjoint held-out selection set", "minimum count from the pilot's competent RATE with margin", "lambda at 0.25x lambda_max (the sweep qualified from 0.125 up)", "mechanism archaeology on the 256 fossil genomes (forbidden pre-verdict)"],
    fossils=["fossils/representatives.json: 256 packed genomes (zlib+base64, sha256) with arm/lineage/rep", "rows/cw01-e08-a01.jsonl 809ab352f"],
    assumptions_at_time=["train8 fitness tracks held64 capability well enough for 6/16 lineages per level to be competent", "the largest qualifying lambda is the right one"],
    later_changes_relevant=["e09 probe: train8/held64 decoupling holds for three organism families (T-X02)"],
    last_perturbation="EXECUTE 2026-09-18 10:10", marginal_information_history=["EXECUTE: material (burden drop observed; eligibility surface found)"],
    stasis_state="ACTIVE")

rec(trajectory_id="T-E09", kind="experiment", origin="cw01-e09", age="2026-09-18 10:40",
    originating_question_verbatim="Can evolution exploit a heterogeneous repertoire of individually modest computational operations by discovering compositions and reuse patterns that outperform what evolution can obtain from the same representational budget without compositional access?",
    derived_operationalization="none frozen: reconcile answered the seven composition questions from code; one probe of the substrate's native straight-line chain form (c3_ecology 'program') in w13",
    translation_loss="not translated: the substrate has no organism-side composition mechanism to translate into",
    world_substrate="w13 / TT organism (no composition); c3 chain probe", representation="4 digit args + 3 op ids (probe only)",
    search_process="probe GA 128 x 150", pressure="charge",
    ruler="none frozen",
    compute_budget="32 s probe",
    result="INCONCLUSIVE / DESIGN UNREACHABLE at RECONCILE: organism's only act is one 3-bit nudge into one register per tick; single-op ceiling on held64 = abstain floor; chains 145-166 on held64 while overfitting train8; scrambled op tables equal arithmetic",
    failure_surface="no composition mechanism exists organism-side; exposing one requires a program representation with an owned workspace (forbidden inside e09); on w13 nothing program-like generalises to held64",
    anomalies=["depth buys train fitness (1386 -> 1868) and none survives held64", "scrambled random op tables perform as well as arithmetic ones"],
    unrun_interventions=["an organism family with selectable, chainable operations over an owned workspace with two-consumer reuse", "a world screen selecting on generalisation"],
    fossils=["PROBE_E09.json"],
    assumptions_at_time=["the brief's constraint: no VM, no invented workspace"],
    later_changes_relevant=[],
    last_perturbation="probe 2026-09-18", marginal_information_history=["reconcile+probe: material (boundary located in the substrate, not the idea)"],
    stasis_state="TEMPORAL_STASIS", stasis_reason="the next informative perturbation requires machinery not yet available (an organism with selectable chainable operations over an owned workspace); every currently available intervention strikes the same surface (no composition mechanism)")

# ---- cross-cutting anomalies and unexplained phenotypes -----------------------------
rec(trajectory_id="T-X01", kind="anomaly", origin="cw01-e02, cw01-e06", age="2026-09-17 / 2026-09-18",
    originating_question_verbatim="(anomaly) Why do neutral genes and neutral labels fix an order of magnitude faster than drift predicts under elite copying?",
    derived_operationalization="e02: neutral_a travelled -0.399 despite zero phenotype; e06 control A (two labels, one substrate) fixed 6/6 at generation ~26 against a neutral-drift expectation ~96",
    translation_loss="never operationalised as its own experiment; treated as a noise floor in both",
    world_substrate="world_e02.py, world_e06.py", representation="any", search_process="tournament/truncation GA with elite copying",
    pressure="n/a", ruler="fixation generation vs drift expectation", compute_budget="none allocated",
    result="unexplained phenotype: lineage hitchhiking dominates the ecological noise floor",
    failure_surface="population structure (elite copying, tournament) was never varied",
    anomalies=["same phenomenon in two unrelated worlds"],
    unrun_interventions=["vary population structure (islands, no elitism, fitness sharing) holding world fixed; measure the neutral fixation time"],
    fossils=[], assumptions_at_time=["drift floor ~N generations"], later_changes_relevant=["lineage.py fixation_order + neutral_drift_floor exist as rulers"],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE",
    anti_gravity="historically deprioritised: no familiar ruler, treated as nuisance")

rec(trajectory_id="T-X02", kind="anomaly", origin="cw01-e08, cw01-e09", age="2026-09-18",
    originating_question_verbatim="(anomaly) In w13, train-seed fitness is a weak proxy for held-out capability across three organism families; what does selection on train8 actually select?",
    derived_operationalization="e08: 2/4 pilot and 8/32 production lineages competent on held64 despite train fitness ~2000 vs abstain 1272; e09: single-op and 3-op chains at/below floor on held64 while train rises with depth",
    translation_loss="none yet", world_substrate="w13", representation="TT, single-op, chain", search_process="GA on 8 train seeds",
    pressure="charge on train8", ruler="held64 per-seed mean", compute_budget="none allocated as its own question",
    result="D065/D069: decoupling observed three times",
    failure_surface="the substrate's own screen (train128_held64) chose w13; the campaign selected on train8",
    anomalies=["TAX+AMP lineages (lowest burden) have the HIGHEST held64 - low burden may generalise better"],
    unrun_interventions=["select on train128 or on a rotating seed schedule; measure held64 competence rate vs number of train seeds"],
    fossils=["e08 fossils/representatives.json"], assumptions_at_time=["8 train seeds suffice (E5 precedent)"], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE",
    anti_gravity="a substrate screening question, not a hypothesis; easy to skip")

rec(trajectory_id="T-X03", kind="hypothesis", origin="cw01-e05", age="2026-09-18",
    originating_question_verbatim="(from e05 limitations) Whether a world composes may be predictable from its capability structure BEFORE running it.",
    derived_operationalization="not yet; 12 replicate worlds exist with known superadditivity and load-bearing outcomes (7/12)",
    translation_loss="none yet", world_substrate="world_e05.py", representation="capability pool geometry", search_process="none (predictor over drawn worlds)",
    pressure="n/a", ruler="to be preregistered: a pre-run predictor's accuracy over held-out drawn worlds", compute_budget="seconds per world",
    result="untested", failure_surface="needs a new preregistration; never allocated", anomalies=["sa == load-bearing 12/12 suggests one underlying world property"],
    unrun_interventions=["draw 48 new worlds, compute candidate pre-run predictors (coverage overlap, conjunctive demand spread), preregister a threshold, then run and score"],
    fossils=["e05 12-replicate outcomes"], assumptions_at_time=[], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE")

rec(trajectory_id="T-X04", kind="anomaly", origin="cw01-e06", age="2026-09-18",
    originating_question_verbatim="(anomaly) Target geometry controls invasion direction: the tree-native target lets TREE invade TAPE, the operation-graph target lets TAPE invade TREE.",
    derived_operationalization="observed in the Q16 gate on legacy vs redesigned generators",
    translation_loss="none yet", world_substrate="world_e06.py", representation="tree vs tape", search_process="e06 GA",
    pressure="score with sharing", ruler="invasion when rare against evolved resident", compute_budget="minutes",
    result="reversal observed once, in one direction each", failure_surface="never varied continuously",
    anomalies=["a substrate-neutral generator produced the OPPOSITE asymmetry, not neutrality"],
    unrun_interventions=["interpolate target geometry between tree-native and graph-native and locate the crossing where mutual invasibility might exist"],
    fossils=["legacy_tree_target in world_e06.py"], assumptions_at_time=[], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE",
    anti_gravity="hard to name; a boundary between two failures rather than a result")

rec(trajectory_id="T-X05", kind="anomaly", origin="cw01-e08", age="2026-09-18",
    originating_question_verbatim="(anomaly) Under tax and under amputation, burden fell 2-3x at unchanged mean capability across all representatives, and the lowest-burden arm had the highest held-out capability.",
    derived_operationalization="descriptive table of e08 (not a verdict)",
    translation_loss="the frozen contract could not test it (eligibility)", world_substrate="w13", representation="ragged TT",
    search_process="e08 GA", pressure="tax/amputation", ruler="none verified", compute_budget="10 min per run",
    result="unverified", failure_surface="eligibility (D066)",
    anomalies=["TAX+AMP: scalar 0.512, held64 171.2"],
    unrun_interventions=["re-pose with a held-out selection set and a rate-derived minimum count", "ablate the fossils: replace evolved ranks by random ranks of equal burden"],
    fossils=["e08 fossils/representatives.json"], assumptions_at_time=[], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE")

rec(trajectory_id="T-X06", kind="anomaly", origin="cw01-e07", age="2026-09-18",
    originating_question_verbatim="(anomaly) A fast re-accumulator loses 20% immediately and recovers almost fully within two windows; the area measure hides damage that the immediate measure shows.",
    derived_operationalization="probe A attainability curve (AURC vs k) for the hand-built accumulator",
    translation_loss="none", world_substrate="world_e07.py", representation="hand-built", search_process="none",
    pressure="none", ruler="AURC vs rho0", compute_budget="seconds", result="curve on record",
    failure_surface="instrument choice", anomalies=[],
    unrun_interventions=["a damage ruler on rho0 with recovery time as a separate coordinate"],
    fossils=["PROBE_E07.json"], assumptions_at_time=[], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="TEMPORAL_STASIS",
    stasis_reason="an instrument fact, fully mapped by the probe curve; the next informative step is its use inside a reposed T-E07, not further probing")

rec(trajectory_id="T-X07", kind="hypothesis", origin="cw01-e09", age="2026-09-18",
    originating_question_verbatim="(from e09) Does composition depth buy anything on a task where capability generalises, once an organism can chain operations over inputs it chooses?",
    derived_operationalization="the c3 chain organism exists as probe code; a generalising task exists in e03/e05 toy worlds",
    translation_loss="reuse (two consumers) not representable in the chain", world_substrate="candidate: world_e03 or world_e05 tasks", representation="3-op chain",
    search_process="probe GA", pressure="task score", ruler="held-out capability above single-op ceiling", compute_budget="minutes",
    result="untested", failure_surface="e09 was bound to w13 and the TT organism",
    anomalies=[], unrun_interventions=["chain organism vs single-op ceiling on a campaign toy task with held-out draws"],
    fossils=["probe_e09.py chain organism"], assumptions_at_time=[], later_changes_relevant=[],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE",
    anti_gravity="an operator hypothesis repeatedly translated into narrower proxies (e03 coalitions, e05 mixtures, e09 soup)")


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
                                 "reason": r.get("stasis_reason", "initial record"),
                                 "marginal_information_history": r.get("marginal_information_history", [])},
                                ensure_ascii=True) + "\n")
            added.append(r["trajectory_id"])
    RS.require_ascii_safe(POOL)
    RS.require_ascii_safe(STATE)
    print("appended", added)


if __name__ == "__main__":
    main()
