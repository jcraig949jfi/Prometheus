# Ergon -- seat dossier

Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

## Summary

Ergon is one of the oldest Prometheus seats and has worn at least five identities, each with its
own code in ergon/ (~2,490 tracked files, most of them ledgers and per-lineage result rows). (1)
April 2026: a "tensor-native hypothesis search engine" -- MAP-Elites over a fixed-schema hypothesis
genome (domain_a, feature_a, domain_b, feature_b, coupling method, conditioning) scored as a
correlation statistic between two columns of a precomputed numeric tensor of LMFDB-style catalog
features (58K x 28, later 4.76M x 208), followed by a falsification battery [IMPL]. Alongside it,
ad hoc number-theory scans (gap_k, NBP, murmurations, Scholz reflection). (2) May: "the Learner" --
a typed-DAG genome over prometheus_math arsenal atoms with a MAP-Elites archive and mutation
operator classes (trials 1-3), plus an ingest pipeline (Penelope daemon) that turned Theseus
handoff bundles (theseus/handoff/ergon_outbox/) and Aporia-staged blocks into a LearnerRecord
corpus intended for LoRA training [IMPL]. (3) June: LoRA experiments on Qwen2.5-Math-1.5B whose
"+0.68" headline the seat itself decomposed into format + prior + template (negative), a
worked-trace experiment, and one positive "routing" result on an 80 x 84 scrap/probe solve matrix
[RESULT-UNVERIFIED]. (4) August: the "metabolization probe" -- frontier/free-host LLM solvers
counting primes among five integers with and without "residue" packets from prior failed
attempts; it was gated, contaminated (Charon 849cacfa1), beaten by a one-line coprime-to-30
heuristic, and closed with annotation; its three scheduled tasks then looped 584 times with zero
rows until disabled at 772edf15e [IMPL + CORRECTION]. (5) From 2026-08-30: the "memory-metabolism"
seat, running preregistered retention-policy experiments (Gen-0..Gen-3) on the frozen D-5
register-machine substrate (agent_d5_blind/, built by an independent "Agent D-5"); every between-arm
retention contrast replicated as a bounded null at n 100 [RESULT-UNVERIFIED]. Side threads: Avida
2003 and Kouvaris 2017 historical forensics, a substrate-independent "latent-neighbourhood
detector" contract. The smallest real computational mechanism across all eras is either
column-pair correlation on a fixed table (April) or a genetic algorithm over <=24-instruction
programs for 8-register 16-bit machines with a 64-genotype FIFO-like library (August-September).

## 1. Identity, charter and pivots

- Name: Ergon ("work"). Host M1 (SKULLPORT) for most work; some Gen-1 work on M2 [CLAIM].
- April body (roles/Ergon/superseded/RESPONSIBILITIES_pre_2026-09-11_superseded.md): "Autonomous
  Hypothesis Engine", run at scale (hundreds of thousands of hypotheses/session), feed survivors
  to Kairos via agora:discoveries [INTENT].
- 2026-05 Learner branch: ergon/learner/ MVP per pivot/ergon_learner_proposal_v8.md; substrate-
  first stand-down 2026-05-11; Penelope ingest 2026-05-18 (ergon/STATUS.md, 2026-05-18) [CLAIM].
- 2026-06-03..09: greedy LoRA, training-data survey, compute traces, routing eval; 06-22..24 infra
  (seam allowlist, DB diagnosis, DuckDB retirement, Redis->Postgres) [CLAIM].
- ~7 weeks dormant to 2026-08-12 (REVIVAL_ASSESSMENT_2026-08-12.md).
- 2026-08-13..30: driver of the metabolization probe under R12 with Charon (kill authority),
  Harmonia B (exit review), Techne (attacks measurement) [CLAIM].
- 2026-08-30: re-chartered as the memory-metabolism seat (CHARTER_2026-08-30_memory_metabolism.md):
  "What should persist from experience so that future reasoning is cheaper?"; seat boundary by
  provenance (endogenous artifacts produced by Prometheus's own search); admission criterion
  "executable and measurable by exact execution under a metered budget against a frozen
  comparator" [INTENT].
- 2026-09-11: base-role adoption (772edf15e): scheduled tasks disabled, RESPONSIBILITIES rewritten,
  workspace_guard on entry points; P3 run; Aporia rules probe CLOSED WITH ANNOTATION (5e3e4e07d)
  [IMPL from git].
- Relationships: consumes Theseus (corpus scan, handoff bundles), agent_d5_blind (substrate),
  Hephaestus failure_mining_results.json (routing eval); reviewed by Charon, Harmonia B, Aporia,
  Archaeon (rulings inbox); Avida/Kouvaris threads handed to Herakles; Diomedes used its corpus
  scan.

## 2. Engine/system inventory

| Engine | Paths | Purpose / era | Key modules | Scale |
|---|---|---|---|---|
| E1 Tensor hypothesis engine | ergon/tensor_builder.py, tensor_executor.py, autonomous_explorer.py, shadow_archive.py, constrained_operators.py, harmonia_bridge.py, monitor.py, run_overnight.bat, tensor*.npz | April screening of cross-domain feature couplings | Hypothesis genome from forge/v3/gene_schema; coupling = spearman/pearson/MI/KS/wasserstein on two aligned columns; F35 "megethos" magnitude kill; kill_taxonomy prefilter; F1-F38 battery | tensor 58,111 x 28 (README) then 4,755,770 x 208 over 23 domains (STATUS 05-18); ~5 hyp/s claimed [IMPL + CLAIM] |
| E1b Number-theory scans | ergon/*_gap_k_scan.py, nbp_*.py, murmuration_isogeny.py, scholz_reflection.py, dhkms_prediction.py, lehmer_mahler_scan.py, flajolet_odlyzko.py, etc. | one-off statistical tests on LMFDB data | scripts | per-script [IMPL, not read in detail] |
| E2 Learner (MAP-Elites over typed DAGs) | ergon/learner/{genome,archive,descriptor,scheduler,reward,triviality,stability,engine,genome_evaluator}.py, operators/, trials/ | May "Learner" MVP | Genome = typed DAG over prometheus_math arsenal atoms (depth <=8, width <=5), 8 mutation operator classes incl. uniform and structured_null nulls | Trial 2: 1000 episodes x 5 seeds; Trial 3: 5000 x 3 [IMPL + RESULT] |
| E2b Learner corpus + Penelope | ergon/learner/corpus/, ergon/learner/scripts/ingest_training_anchors.py, ergon/penelope/ | LearnerRecord corpus for LoRA from Theseus / Aporia / Techne blocks | SHA-keyed processed ledger, daemon modes | 1,486 records as of 06-03 audit (79% promoted, 1.4% rejected); 49 consumed Theseus bundles in theseus/handoff/ergon_outbox/consumed [RESULT + IMPL] |
| E2c LoRA / greedy / traces / routing | ergon/learner/greedy/, ergon/learner/eval/routing_eval.py, pipeline_d/ | June training experiments | Qwen2.5-Math-1.5B LoRA rank 16; routing = matrix completion on solve matrix | 1,200 held-out claims; 80 scraps x 84 probe slots [RESULT] |
| E3 Metabolization probe | ergon/probe/ (task_gen v1-v3, solver.py, packet_render.py, packet_invariants.py, f_null.py, f_generic.py, campaign.py, drip_coldband.py, coldband_m30_free.py, channel_capacity.py, adversarial_leakage.py, corpus_scan_full.py; tests/ 226 tests), ergon/probe/ledgers/ (47 MB) | does in-context residue from prior failures help an LLM solve? | arms F0, F-prom (residue), F-null (mismatched residue), F-generic (prose); exact gold by Miller-Rabin | pooled n 405 tasks (block A 194, block B 211); free-host models e.g. nvidia nemotron-super-49b-v1, gpt-oss-120b [IMPL] |
| E3b Scheduled probe tasks | ergon/run_campaign.cmd, run_coldband_drip.cmd, run_coldband_m30.cmd (+ run_diurnal_probe.cmd, run_m20_watcher.cmd) | autonomous campaign/drips | Windows scheduled tasks PrometheusCampaign (PT30M), PrometheusColdbandDrip (PT3H), PrometheusColdbandM30 (PT30M) | 199 + 96 + 289 = 584 ticks, 0 rows, 2026-09-05..09-11 [IMPL from roles/Ergon/STATUS.md and ops file] |
| E4 Retention-policy lineages (Gen-0..Gen-3) | ergon/gen0, gen1, gen1a, gen1b, gen2, gen3 (+ results dirs: gen1b/gen1_results 240, gen2/p1_results 400, gen3/p3_results 400, gen3/cheat_results 520 files) | memory metabolism: does what is retained/evicted matter? | frozen runner ergon/gen1b/gen1_run.py (blob 5771258...), PolicyLibrary arms I0 MRU / I1 MUT_REDUNDANT / I2 EFFECTIVE_USAGE / I3 RANDOM; p3_common.run_lineage_planted cheat arm | 42 tasks x 30,000 evals x n lineages (30 Gen-1B, 100 P1, 100 P3) [IMPL] |
| E4 substrate (not Ergon's build) | agent_d5_blind/ (substrate/rm_vm.py, rm_fast.py Numba, mutation/physics.py, learner/m1.py, navigators/m0.py, task_generators/families.py) | "Agent D-5 blind hard-task findability", 2026-08-27 | register machine: 8 regs, 16-bit, 14 opcodes, MAX_LEN 24, STEP_BUDGET 512, palette of 10 constants; GA pop 32, tournament 3, crossover, 10% immigrants (50% from library) | 78 tasks (58 dev + 20 alien), 42 non-control evidence tasks [IMPL] |
| E5 Historical forensics | ergon/avida2003/ (deep dive V0, A..V docs, provenance_gates.py, collision analysis), ergon/kouvaris2017/ (A..P docs, original/, work/) | recover Lenski et al. 2003 Avida lineage and Kouvaris et al. 2017 "How evolution learns to generalise" as prior art/detectors | document + small scripts | Avida: 105 lineage rows transcribed; Kouvaris: 19 artifacts [CLAIM] |
| E6 Detector transfer contract | ergon/detector_transfer/01..10 + build.py | substrate-independent latent-neighbourhood detector (does the one-mutation neighbourhood reorganise before the scalar selection channel shows it?) | contract only | blocked on seam S1 (world-applied selection rule for stackvm-v1) [INTENT] |
| E7 Misc | ergon/diagnostic_c/synthetic_env.py, ergon/repair/, ergon/scripts/, ergon/meta/ (MAP-Elites pilot archive) | various | -- | not read |

## 3. Code architecture and dataflow

- E1: tensor_builder loads domain tables into a float32 matrix; a Hypothesis picks two feature
  columns (possibly different domains, aligned by some join) and a coupling method;
  tensor_executor computes the coupling (e.g. spearmanr) and runs battery tests; autonomous_
  explorer mixes 40% random / 30% mutation / 20% crossover / 10% "void-targeted" hypotheses per
  generation into a MAP-Elites archive [IMPL]. Code-vs-doc disagreement: the void-targeted branch
  computes void_cells but then calls random_hypothesis(gen, rng) without using them
  (autonomous_explorer.py run_generation), so "targeted void filling" is plain random sampling
  [IMPL].
- E3: task generator -> manifest (pinned by sha) -> pre-pass attempts (rep-1 records) -> residue
  pool built from prior attempts' method text -> packet_render builds per-arm prompts (all end
  with the F0 prompt byte-for-byte) -> solver via API with pacing/backoff -> exact gold scoring ->
  block-scoped pooling [IMPL/CLAIM]. Charon C1: residue pool not pinned and moving, F-null
  selection normalised by pool extrema so pool growth moves controls; C2: load_prepass never reads
  status, so HTTP 504 failures became residue ("prior attempt recorded no recognizable method
  vocabulary"), 3.0% of block A tasks vs 24.1% of block B [CORRECTION].
- E4: for each lineage, for each of 42 tasks in fixed order: m1_rx GA search with library
  (budget 30,000 evaluations), then admissions = solver + up to 4 behaviour-distinct best of last
  generation; PolicyLibrary admits and, over cap 64, evicts per arm policy. CFR = fraction of
  tasks solved within budget [IMPL]. Paired seeds nav_base = 200000 + 1000 L per lineage; disjoint
  lineage index spaces per experiment [IMPL].

## 4. Claimed computational primitive vs actual mechanism

| Engine | Label | Smallest actual mechanism | Could express | Ruler targeted | Organism could do it? | Ruler vs shortcut? |
|---|---|---|---|---|---|---|
| E1 tensor engine | "tensor-native hypothesis search", "coupling", "bond dimensions" (Harmonia TT-Cross) | bivariate correlation / MI / KS between two precomputed feature columns, MAP-Elites archive of (pair, method) | pairwise marginal dependence between catalog features | cross-domain structure | It enumerates pairs; no reasoning organism | Battery + megethos kill + kill taxonomy target known confounds (magnitude/conductor). Shortcut: any monotone size proxy; the F35 kill is exactly a hand rule against one [CODE-INFERRED] |
| E2 Learner | "evolutionary engine", "obstruction discovery" | typed DAG composition of arsenal atoms + MAP-Elites descriptor; Trial 2 scoring uses an MVPSubstrateEvaluator stub with promote_rate 0.0001 | compositional programs over math library calls | archive fill vs null operators; "high-lift predicates" in Trial 3 | Trial 2: 0 substrate-passed in 5000 episodes (stub); Trial 3 found planted obstruction discriminators | Trial 2's primary metric (structural fills >= 1.5x uniform) measures operator diversity, not discovery; Trial 1 showed the residual classifier had 80% FP on structured noise [RESULT-UNVERIFIED] |
| E2c LoRA | "learning from failure" | LoRA rank 16 on 1.5B model, verdict-format completions | verdict classification on templated claims | gold True/False accuracy | -- | Own decomposition: base 0.228 -> 0.907; shuffled-label control 0.681 (format); later "gains were format + prior + template" (CHARTER S1) [CORRECTION] |
| E2c Routing | "residue is navigable" | logistic/collaborative filtering on an 80 x 84 binary solve matrix (top-10 truncated) | co-solve structure | warm-start vs cold-start routing | -- | Warm COLLAB 0.829 vs POP 0.754 (+0.075); cold FEATURE 0.744 vs POP 0.753 (null); probe identities unverifiable, in-distribution only [RESULT-UNVERIFIED] |
| E3 probe | "metabolization of residue" | LLM prompt with/without a bracketed record of prior attempts' method vocabulary; count primes among 5 integers | in-context hinting | does residue raise accuracy beyond F-null/F-generic | LLMs compute exactly at any operand magnitude; v2 depth 1-20 solved ~94% | One-line coprime-to-30 count scores 0.5225 fresh-seed vs solver 0.4794; residue vocabulary names the trivial filter; F-generic envelope differs from F-null/F-prom (shape-separable) [CORRECTION] |
| E4 retention | "memory metabolism", "endogenous capability" | which 64 genotypes stay in a GA's immigrant pool (50% of 10% immigrants) | caching of partial solutions across tasks | does eviction policy change CFR | the library is a seed pool, not a reusable abstraction (no calls, no composition between artifacts) | Cheat control plants an oracle witness: +3.38 pp at n 100 (detectable), +3.33 pp at n 30 failed the SE branch [RESULT-UNVERIFIED]; the channel itself is thin (immigrant draws only) [CODE-INFERRED] |
| D-5 (substrate, other agent) | "accumulated executable history" | same GA with library on vs off | -- | CFR vs frozen M0c-RX | yes for library content | Shuffled-order retains 100%; random-walk library retains 39% => content effect, not developmental; R == E theorem makes reachability uninformative [RESULT-UNVERIFIED] |
| E6 detector contract | "latent neighbourhood reorganisation" | contract text; s must be the world's own selection projection | counterfactual one-mutation neighbourhoods | pre-phenotypic change | not built | design requires world-applied s to avoid trivial "projection loses information" [INTENT] |

## 5. Representation/state architecture

- E1: flat float32 table; hypothesis is a fixed-schema record (controlled vocabularies). No
  learned representation [IMPL].
- E2: typed DAG over arsenal callables, content-hashed; behaviour descriptor with 5 axes [IMPL].
- E3: text prompts; residue is a census of METHOD_VOCAB tokens from prior attempts [IMPL/CLAIM].
- E4: genotype = tuple of (op, a, b) instructions; library = ordered list of <= 64 genotypes,
  genotype-deduped; artifact identity by hash; per-artifact credit counters in I2 [IMPL].
  Registers 8 x 16-bit, palette constants [0,1,2,3,5,7,11,13,16,255], jumps (JNZ) and skips
  (SKG, SKZ) give bounded loops within STEP_BUDGET 512 [IMPL].

## 6. Organism/player architecture

- E3: external LLMs (free-host NVIDIA models; "M20/M30" are task-mix labels) [CLAIM]. Not Ergon's.
- E4: the D-5 register-machine program evolved by a GA (pop 32, tournament of 3, crossover 50%,
  mutation classes OP_REPLACE, ARG_TWEAK, INSERT, DELETE, SWAP, DUP_BLOCK) [IMPL]. Programs can
  express loops and conditionals (JNZ, SKZ, SKG) within 24 instructions; no memory beyond 8
  registers; no inter-artifact calls; the "library" is only a source of mutated immigrants [IMPL].
  A successful organism could at most compute a fixed function on 64 inputs (or 8x8 for ALIEN).

## 7. World/environment architecture (toy scale)

- E1: static catalog data (LMFDB EC, MF, NF, G2C, Maass, knots, superconductors ...). No dynamics.
- E3: five-integer prime-count tasks; v1 operand magnitude (dead axis: accuracy non-monotone
  72.6/53.6/64.3/59.5), v2 compositional depth 1-20 (dead: ~94% solved, 20-step chain 40/40), v3
  adversarial near-misses (semiprimes with large factors, base-2 pseudoprimes, Carmichael
  numbers); answer space {1,2,3,4} [IMPL]. 126-task manifests; usable N 66 after screen [CLAIM].
- E4: D-5 battery: F1 AFFMOD (composition of 1-5 hidden unary primitives on x in 0..63), F2 PIECE
  (if p(x) then gA else gB), F3 ITER (g^k), F4 BIT (bit-flavoured primitives), CTRL-RAND
  (random lookup tables on 2-4 inputs), NEGXFER (poisoned constants), ALIEN (f(x,y) =
  combiner(hA(x), hB(y)) on 8x8) [IMPL]. Each task is a single input-output table of 64 rows;
  objective is bitwise Hamming distance to the table; 42 non-control evidence tasks in fixed
  order. This is a small, fully observable, deterministic, single-agent toy; tasks are
  independent tables generated from one hidden primitive library H [IMPL].

## 8. Search/training/adaptation mechanism

- E1: MAP-Elites mutation/crossover over hypothesis fields; survivors -> Harmonia bridge.
- E2: MAP-Elites with operator-class scheduler with minimum share; reward agreement-weighted
  (designed), stub evaluator in MVP trials [IMPL/CLAIM].
- E2c: supervised LoRA, one epoch, 1.5B model; capacity confound declared by the seat
  (REVIVAL_ASSESSMENT S2) [CLAIM].
- E4: GA per task, library persists across tasks within a lineage. Bottleneck: library influence
  limited to immigrant draws (10% of children, half from library); budget 30,000 evals; cap 64
  never reached "as a choice" in D-5 (CHARTER S4.1) [IMPL/CLAIM]. Collapse mode: 44% of artifacts
  never earn a first credit; usefulness does not decay (Gen-1B hazard rows) [RESULT-UNVERIFIED].

## 9. Measurement/ruler stack

- E4 (the most disciplined): per-lineage CFR over 42 tasks; paired lineages; preregistered T =
  2.00 pp meaningfulness threshold inherited from P1; MDE under the frozen rule (MDE80 1.22 pp at
  n 100); five constructed gate-fire worlds through the exact decide() path (5/5); cheat control
  planting the oracle witness (n 30 failed SE branch, kept; n 100 +3.38 pp p 0.00002); Holm
  correction in Gen-1B; persistence validation and replay (D-5 290/290 rows reproduced, 5/5
  final libraries byte-exact) [IMPL + RESULT-UNVERIFIED].
- E3: packet_invariants.py decidable checks (base_identical, no_forbidden_tokens,
  no_verbatim_gold, envelope_identical FALSE), task_controls.py heuristic floors, R7 static leakage
  classifier (D0 pass 0.383; D1 0.967 and D2 0.917 fail vs 0.55 ceiling), power analysis (whole-
  arm power 0.14 at +8 pp, N=60), headroom band [0.35, 0.60] [IMPL/RESULT].
- E2c: shuffled-label control; per-source accuracy; positive/negative controls in routing eval.
- E1: falsification battery F1-F38 (external module), megethos kill, kill-taxonomy prefilter.
- Known blind spots (seat's own list): checks that strip/normalise exactly where a caller label
  goes (five instances in the probe); a lookup that finds zero rows returning a renderable value;
  a transport failure counted as residue; parity of an instrument is not capture
  (RESPONSIBILITIES.md constraints 3-5) [CLAIM].

## 10. Baselines and controls

- E3: majority chance 0.25; coprime-to-30 heuristic 0.5225; F-null and F-generic arms;
  deterministic solver gold recovery 1.0000; uid-index correlation r = -0.0072.
- E4: I0 MRU (inherited D-5 rule) vs I3 RANDOM vs I1/I2 selective; D-5 comparators M0c-RX,
  M0b-POP; random-library and shuffled-history ablations.
- E2c: base model, shuffled-label LoRA, popularity prior (routing).
- Missing: E4 never varied the cap or the library's channel strength (ERGON-06/07 now
  NEEDS_REPREMISE toward "does the CAP matter"); E3 never had a matched-envelope F-generic.

## 11. Historical experiment campaigns

| Id | Date | Question | Organism / world | Arms, scale | Reported result | Reinterpretation | Paths / commits | Label |
|---|---|---|---|---|---|---|---|---|
| April overnight runs | 2026-04 | which cross-domain couplings survive the battery? | hypothesis genome / catalog tensor | 10K-generation batches; 21 overnight survivors (Apr 13-14) | survivors to Kairos/Harmonia | April body superseded; survivors' status not checked here | ergon/results/, ergon/logs/, run_overnight.bat | UNKNOWN |
| Math scans | 04-18..05-03 | murmuration by isogeny, Scholz p=3, DHKMS, knot silence | scripts / LMFDB | e.g. 344,130 NF pairs | Scholz zero violations; murmuration 5/21 primes significant; knot silence holds | not audited | ergon/HANDOFF.md, ergon/STATUS.md | REPORTED POSITIVE (unaudited) |
| Learner Trial 1 | 05-04 | can the residual classifier be a reward? | sigma_kernel residual classifier | 200 samples | 80% FP on structured noise; FAIL | -- | ergon/learner/trials/TRIAL_1_REPORT.md | REPORTED NEGATIVE/NULL |
| Learner Trial 2 | 05-04 | do structural operators fill the archive more than uniform? | typed DAG, stub evaluator | 1000 ep x 5 seeds | ratio 5.58x, PASS; 0 substrate-passed | metric is diversity, evaluator a stub | TRIAL_2_PRODUCTION_REPORT.md | INSTRUMENT FAILURE (stub scoring) |
| Learner Trial 3 | 05-04 | 5K scaling; obstruction discovery | same | 5000 ep x 3 seeds | obstruction found 3/3 seeds; 2,203 high-lift predicates | planted obstruction; not re-audited | TRIAL_3_5K_SCALING_REPORT.md | UNKNOWN |
| Greedy LoRA | 06-03 | does substrate as LoRA data move reasoning? | Qwen2.5-Math-1.5B r16 | base / real / shuffled; 1,200 held-out | 0.228 -> 0.907; content +0.226 over shuffled | 06-07: format + prior + template, no transfer | roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md, GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md | LATER OVERTURNED |
| Compute traces | 06-08 | do worked traces teach computation? | same | WORK vs NO-WORK | in-op +0.164; cross-op ~ format | capacity confound | COMPUTE_TRACE_RESULT_2026-06-08.md | MIXED |
| Routing eval | 06-09 | is mined residue navigable? | matrix completion | 80 scraps x 45 active probes, LOSO, 5 seeds | warm +0.075 (survives tail); cold null | probe identities unverifiable; in-distribution | ROUTING_EVAL_2026-06-09.md | MIXED |
| Corpus value audit | 06-03 | what reached the consumer? | -- | LearnerRecord corpus | 1,486 records, 79% confirmations | -- | CORPUS_VALUE_AUDIT_2026-06-03.md | REPORTED NEGATIVE/NULL |
| Probe pre-pass + gates | 08-16 | can the pilot run? | LLM solvers / prime counting | levels L0-L3, n 84/126 | HEADROOM-FAILURE; R7 D1/D2 fail | -- | PROBE_EXECUTION_2026-08-16.md | INSTRUMENT FAILURE |
| Probe campaign blocks A/B | 08-19..09-01 | does residue raise accuracy? | LLM / v3 near-miss tasks | pooled n 405 | heuristic floor unbeaten; solver 0.4900 vs 0.5225 | Charon 849cacfa1: both pools contaminated (C1 unpinned pool, C2 504s as residue); Aporia 5e3e4e07d: CLOSED WITH ANNOTATION | ergon/probe/STATE_2026-08-25.md, FINDING_*.md | CONTAMINATED |
| Scheduled drips | 08-21..09-11 | keep campaign/coldband running | -- | 584 ticks 09-05..09-11 | exit 0, 0 rows | disabled 772edf15e; D-23 s6 and base rule 7 violations | roles/Ergon/ops/SCHEDULED_TASKS_DISABLED_2026-09-11.txt | INSTRUMENT FAILURE |
| D-5 (Agent D-5, consumed by Ergon) | 08-27 | does executable history improve findability? | RM-D5 GA | M1 vs M0c-RX, 42 tasks | +10.95 pp CFR p 0.0007; shuffled retains 100%, random library 39% | Ergon: freeze record unverified, analysis script never committed (reproducibility, not validity) | agent_d5_blind/VERDICT.md; ergon/gen1/FINDING_d5_reproducibility_2026-09-01.md | REPORTED POSITIVE |
| Gen-0 | 08-31 | structural determination of consumer interface | source reading | 7 gate-fire worlds | structural claims (not read in detail) | freeze order admitted not preregistered | ergon/gen0/ | UNKNOWN |
| Gen-1/1A | 09-01 | persistence, attainable range, MDE | D-5 | replay | 290/290 rows reproduced | -- | ergon/gen1, gen1a | REPORTED POSITIVE (instrument) |
| Gen-1B | 09-01 | does selective retention beat MRU? | D-5 | 4 arms x 30 lineages | I1 - I0 +2.78 pp Holm 0.0040; I1 - I3 +1.51 pp | falls by annotation 09-11 after P1 and P3 | ergon/gen1b/ANNOTATION_2026-09-11_headline_falls.md | LATER OVERTURNED |
| Project 1 | 09-02 | selection vs churn | D-5 | I1 vs I3 x 100 | -0.31 pp CI [-1.12, +0.55] | -- | ergon/gen2/p1_results.json | REPORTED NEGATIVE/NULL |
| Project 2 | 09-02 | trajectory instrument | D-5 | parity check | TRAJECTORY_INSTRUMENT_CLEAN; parity alone would pass a broken instrument | -- | ergon/gen2/p2_parity.json | REPORTED POSITIVE (instrument) |
| Project 3 | 09-11 | is MRU harmful vs random? | D-5 | I0 vs I3 x 100 fresh | +0.55 pp CI [-0.24, +1.33], p 0.178: RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER | -- | ergon/gen3/p3_results.json, PREREG_P3_MRU_VS_RANDOM.txt | REPORTED NEGATIVE/NULL |
| Avida 2003 forensics | 09-0x | recover 2003 lineage as prior/detector | document | 105 rows | V0.1 "7 damaged genomes" | corrected: blue-asterisk deletion marker, zero damaged; frozen 09-04 | ergon/avida2003/, ergon/detector_transfer/08_AVIDA_CORRECTION.md | LATER OVERTURNED |
| Kouvaris 2017 forensics | 09-03 | is Kouvaris 2017 a prior solution to HC-T01? | document | 19 artifacts | KOUVARIS_STRONGER_BUT_DIFFERENT | ancestor Parter 2008 had a local detector the seat first missed | ergon/kouvaris2017/P_EXTERNAL_REVIEW_PACKET.txt | MIXED |

## 12. Reported results and later corrections (timelines)

1. Greedy LoRA "needle moved hard" (06-03) -> shuffled-label control isolates format -> 06-07
   follow-up: format >> False prior >> template; no cross-source transfer -> charter 08-30 cites it
   as the contestant that lost [CORRECTION].
2. Probe residue effect: never measured cleanly -> heuristic floor 0.5225 above solver (08-24) ->
   transport failures as residue (08-25) -> Charon contamination ruling (09-01) -> Aporia closes
   with annotation (09-11) [CORRECTION].
3. Gen-1B +2.78 pp -> P1 null on I1 - I3 (09-02) -> P3 null on I3 - I0 (09-11) -> headline falls by
   annotation; hazard-structure rows retained [CORRECTION].
4. Avida V0.1 damage diagnosis (two extractors agree) -> archived 2003 legend shows deletion marker
   -> zero damaged; lineage-repair justification withdrawn [CORRECTION].
5. Kouvaris genealogy "ancestor has no local element" -> another seat found Parter et al. 2008
   Text S1 with an exhaustive local accessibility detector -> genealogy corrected [CORRECTION].
6. Probe drips "running" -> 584 zero-row ticks discovered 09-11 -> disabled [CORRECTION].
7. RESUME_ergon_2026-08-25.md carries its own CORRECTION BANNER (not read in full).
8. Seat's self-reported misreading: "misread the same instrument three times in one day"
   (SESSION_2026-08-25_part2_review_cycle.md S3, per superseded body) [CLAIM].

## 13. False-positive archaeology

- Format acquisition read as reasoning (LoRA).
- Marginal contrast at n 30 (Gen-1B) under Holm, not replicated at n 100 on either leg.
- Residue packets whose shape (envelope, lead line, numeric slug band, payload.strip()) leaked
  arm identity; five instances, the fifth inside the fix for the fourth (superseded RESPONSIBILITIES
  "defect class") [CLAIM].
- Two extractors agreeing taken as semantic evidence (Avida).
- Transport-failure rows (HTTP 504) rendered as residue content.
- D-5's +10.95 pp is a library-content effect (39% from any executable random-walk genotypes);
  it is not developmental and not transfer (G6, G7 fail) [RESULT-UNVERIFIED].

## 14. Likely false-negative regimes

- E4: library influence is confined to immigrant sampling in a 32-member GA with 30,000-eval
  budget; tasks are independent tables from one hidden primitive library; with cap 64 and 42 tasks,
  eviction rarely bites. A null on "retention policy" here is a null for a very weak memory channel,
  not for memory. No artifact composition, calling, or abstraction (library learning in the
  DreamCoder sense) is possible.
- E2c: 1.5B model, rank 16, one epoch: capacity confound declared by the seat.
- E3: the task family's difficulty axes kept dying (magnitude, depth); the solver computes
  arithmetic exactly, so residue could only matter on recognition errors; the population was
  then contaminated before a clean read.
- Routing: cold-start null used concept labels on unverifiable probes.
- E1: correlation-of-columns cannot express structural (categorical) bridges; the "knot silence"
  result explicitly concluded the bridge is categorical, not numerical.

## 15. Phase 3 audit (per engine)

### 15.1 E1 Tensor hypothesis engine
a. hierarchy NO; compositional PARTIAL (crossover of hypothesis fields); variable binding NO;
   memory PARTIAL (MAP-Elites archive, shadow archive of kills); recurrence NO; counterfactual NO;
   latent variables NO; temporal NO; spatial NO; reusable substructure NO; dynamic routing NO;
   self-reference NO.
b. No: lookup of precomputed columns and a correlation statistic.
c. Size/magnitude proxies, shared conductor ordering, sample-size p-values, database join
   artifacts; F35 kill handles one of these by rule.
d. Battery resolves statistical artifacts of pairs; cannot resolve mechanism.
e. Up to 4.76M objects x 208 features, 23 domains; ~5 hyp/s claimed; static.

### 15.2 E2 Learner (typed-DAG MAP-Elites)
a. hierarchy PARTIAL (DAG depth <= 8); compositional YES (typed composition of atoms); variable
   binding PARTIAL (arg bindings); memory PARTIAL (archive); recurrence NO; counterfactual NO;
   latent NO; temporal NO; spatial NO; reusable substructure PARTIAL (archive elites); dynamic
   routing NO; self-reference NO.
b. Unknown in practice: MVP trials used a stub evaluator or planted obstructions.
c. Operator-diversity metrics reward filling cells; stub promote rate.
d. Weak: primary acceptance metrics measure archive fill.
e. 1000-5000 episodes, archive 57-701 cells, ~85 arsenal atoms.

### 15.3 E2c LoRA / routing
a. Neural weights (latent YES, others not inspectable); routing model is matrix completion.
b. Verdict classification on templated claims; no multi-step requirement.
c. Format, True/False prior, per-template classes; probe popularity.
d. Shuffled-label control resolved format vs content; could not resolve reasoning vs template.
e. 1.5B model, 1,200 eval claims; 80 x 84 matrix.

### 15.4 E3 Metabolization probe
a. External LLM (opaque); residue representation is a token census.
b. Prime counting over five integers; adversarial near-misses demand choosing a correct test,
   otherwise lookup/arithmetic.
c. Coprime-to-30 filter (0.5225); envelope/shape differences between arms; residue that names
   the cheap filter; transport failures.
d. Decidable packet invariants are strong for byte-level leakage, blind to content reality
   (INV 7 passed a population with 43/220 fabricated residue arms) [CLAIM].
e. n 405 tasks pooled; 4-way answers; free-host API lanes ~30 RPM.

### 15.5 E4 Retention lineages on D-5
a. hierarchy NO; compositional PARTIAL (crossover of instruction sequences, not of library
   artifacts); variable binding NO (fixed register indices); memory YES at the lineage level
   (64-genotype library) and 8 registers within a program; recurrence PARTIAL (JNZ loops bounded
   by 512 steps); counterfactual NO; latent NO; temporal abstraction NO; spatial NO; reusable
   substructure PARTIAL (library genotypes mutated into immigrants; DUP_BLOCK); dynamic routing NO;
   self-reference NO.
b. No: each task is an independent 64-row function table; interpolation/memorization of partial
   genotypes suffices; no environment dynamics.
c. Planting witnesses (the cheat control); library content from the same hidden primitive pool H;
   CTRL delta +6 pp shows nonzero lift on structureless tasks.
d. Good for detecting a planted retention effect of ~3 pp at n 100; MDE80 1.22 pp; cannot resolve
   effects below ~1 task in 42 per lineage (2.38 pp granularity per lineage).
e. 42 tasks, 30,000 evals/task, pop 32, cap 64, programs <= 24 instructions, 8 x 16-bit registers,
   100 lineages/arm; compute: CPU process pool.

### 15.6 E5/E6 Forensics and detector contract
a-e: documents and a contract; no executable organism. The detector contract's requirement that
the scalar channel be the world's own projection of a phenotype vector is a reusable ruler idea.

## 16. Research reports and substantial documents

- roles/Ergon/CHARTER_2026-08-30_memory_metabolism.md -- memory-metabolism charter, admission rule.
- roles/Ergon/REVIVAL_ASSESSMENT_2026-08-12.md -- four kills and one positive; frontier-model rule.
- roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md, GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md -- LoRA.
- roles/Ergon/TRAINING_DATA_SURVEY_2026-06-07.md -- verdicts vs derivations.
- roles/Ergon/COMPUTE_TRACE_RESULT_2026-06-08.md, ROUTING_EVAL_2026-06-09.md.
- roles/Ergon/CORPUS_VALUE_AUDIT_2026-06-03.md -- 1,486-record corpus.
- roles/Ergon/PROBE_EXECUTION_2026-08-16.md, TASK_FAMILY_V2_2026-08-17.md, API_PREFLIGHT_2026-08-13.md.
- roles/Ergon/SESSION_2026-08-25_packet_leak_and_block_b.md, SESSION_2026-08-25_part2_review_cycle.md.
- ergon/probe/FINDING_heuristic_floor_2026-08-24.md, FINDING_transport_failures_as_residue_2026-08-25.md,
  FINDING_packet_arm_labels_2026-08-25.md, FINDING_pooled_population_single_block_residue_2026-08-30.md,
  STATE_2026-08-25.md, CORPUS_CHARACTERIZATION_FOR_R2-6_2026-08-22.md, SPEC_channel_capacity_2026-08-24.md.
- ergon/gen3/PREREG_P3_MRU_VS_RANDOM.txt, REVIEW_PACKET_P3_2026-09-11.txt; gen1b/PREREG_GEN1;
  gen2/PREREG_P1; gen1/FINDING_d5_reproducibility_2026-09-01.md; gen1/RULING_2026-09-02_external_review.md.
- ergon/avida2003/ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0/ (A..V); ergon/kouvaris2017/ (A..P).
- ergon/detector_transfer/01..10 -- detector contract, world API, baselines, negatives.
- ergon/SESSION_2026-09-04_damage_recovery_and_seat_comparison.md -- recovery of the "damage
  algebra" thread (Noesis, agents/arachne/damage.py).
- ergon/README.md, ergon/HANDOFF.md (2026-04-18), ergon/STATUS.md (2026-05-18) -- April/May eras.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Ergon/journal/2026-09-11.md; SESSION_JOURNAL_2026042x-0504 (April-May); BACKLOG_H0H5.md
(ERGON-NN rows; 06/07 NEEDS_REPREMISE; 13 void); ergon/BACKLOG.md (BL-E-001..034, May roadmap,
capstone BL-E-030 first training run, never reached); todo_20260901.md (kill-taxonomy migration
blocked on Mnemosyne); WORK_QUEUE_2026-05-10.md; PROMPT_2026-05-11_substrate_first.md. Abandoned:
April engine, Learner LoRA line, Penelope ingest (last activity 05-18), probe (closed), Avida
(frozen), detector transfer (blocked on Daedalus seam S1).

## 18. Dependencies on other engines and seats

forge/v3 gene_schema, kill_taxonomy, falsification_battery, battery_v2 (E1); Harmonia TT-Cross
bridge; prometheus_math arsenal registry (E2); sigma_kernel residual classifier (Trial 1); Theseus
handoff bundles and corpus (E2b, corpus scan); Techne stager envelopes; Hephaestus failure mining
(routing); NVIDIA free-host API lanes (E3); agent_d5_blind (E4); Charon, Harmonia B, Aporia,
Archaeon rulings; Herakles (inherits Avida/Kouvaris as organisms); Daedalus/SFE (seam S1).

## 19. Scaling limitations

E4 granularity 2.38 pp per lineage; per-task GA cost dominates; library channel strength fixed by
the frozen D-5 runner (cannot be changed without breaking the freeze). E3 bounded by API rate
(~30-60 RPM) and by the heuristic floor. E1 static data; MI with fixed bins.

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: E4 register-machine GA (agent_d5_blind) with an exact oracle, Numba fast path
  verified bit-identical to a reference VM, deterministic seeds, replay verified 290/290.
- Organisms: <=24-instruction programs; external LLMs (E3).
- Worlds: 64-row function tables from a hidden primitive library; prime-count prompts.
- Pressures: per-task GA fitness (Hamming), library eviction policy.
- Phenomenon family: accumulation and forgetting of endogenous executable artifacts; in-context
  use of failure residue.
- Current resolving mechanism: paired CFR, preregistered T, MDE, gate-fire worlds, planted-witness
  cheat control.
- Likely resolution ceiling: ~1-2 pp CFR at n 100; effects of library CONTENT detectable, policy
  effects not at this channel strength.
- Noise sources: GA stochasticity per task, task order, lineage seeds; API transport errors (E3).
- Architectural limit: library is an immigrant pool, not callable abstractions; tasks independent;
  no environment state.
- Reusable parts: the E4 inference path (decide(), gate-fire worlds, cheat plant), D-5 E/R/F
  split (expressible/reachable/findable), packet_invariants decidable leakage checks, detector
  contract's world-applied projection requirement, the probe's heuristic-floor control habit.
- Toy-grade parts: D-5 battery scale, prime-count task family, April correlation engine.
- Unknowns: whether a stronger memory channel (calls, composition, larger cap pressure) changes
  the null; status of April survivors; Trial 3 obstruction semantics.

## 21. Open questions / coverage gaps

Read: roles/Ergon STATUS, RESPONSIBILITIES, superseded RESPONSIBILITIES (most), CHARTER (first
150 lines), REVIVAL_ASSESSMENT (first 80), PROBE_EXECUTION (first 120), GREEDY_LORA (first 60),
ROUTING_EVAL (grep), CORPUS_VALUE_AUDIT and COMPUTE_TRACE (grep), ops file; ergon/README (head),
STATUS (05-18), HANDOFF (04-18), SESSION_2026-09-04 (head), probe FINDING_heuristic_floor and
task_gen_v3 header, gen3 PREREG and p3_common.py, gen1b annotation, gen1 FINDING header, gen0
freeze header, avida correction, kouvaris packet header, detector contract header, learner
README/genome header and trial reports, tensor_executor/autonomous_explorer excerpts, agent_d5_blind
MANIFEST, VERDICT, m1.py, families.py excerpts, rm_fast.py head. Not read: SESSION_JOURNAL files
(April-May, 58 KB for 05-04 alone), RESUME_ergon_2026-08-25 and its correction banner, D23
compliance, DB/infra docs, TASK_FAMILY_V2, API_PREFLIGHT, the probe's campaign.py/solver.py/
packet_render.py bodies, gen0/gen1a/gen2 code, every ledger row (inventoried and sampled only:
probe ledgers 47 MB; campaign_log.jsonl 1,318 lines, drip_log 233), learner corpus contents,
pipeline_d, penelope code, math scan scripts, Avida/Kouvaris bodies. No tests or runs executed.
Note: the operator's canonical checkout (F:\prometheus, branch vivarium/v0-2026-09-05) showed
uncommitted modifications to ergon/probe/ledgers/campaign/* and coldband_* at crawl start; whether
any scheduled task was re-armed after 2026-09-11 is UNKNOWN (not inspected). Atlas holds no
Ergon-specific dossier: only the ERGON-NN id regex (atlas/classify.py), a SOURCES.md mention, and
an Avida ecosystem entry.
