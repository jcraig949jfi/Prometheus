# Charon -- forensic dossier (Tityos Phase 3, signal-vs-hallucination lane)

Crawler: Tityos worker g5_adversarial, 2026-10-01, with three read-only forks (math era; swarm/diagnostics;
Aug-Sep probe era) whose findings I spot-checked (bsd_battery.py:213, abc_battery.py:222-237/336,
known_truth_battery.py imports, stygian executor verdict mapping, north_star.md header,
v2/battery_calibration_results.json all verified by me). Worktree F:/Prometheus-worktrees/tityos-phase3 at
36ffe8073. All searches excluded **/*holdout*/** and **/nestor_secrets/**; no such path was opened.

Labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].
Commits on every Charon path are authored "James Craig" (Claude co-author); seat identity exists only in
commit subjects ("Charon:", "Charon swarm vX", "Erebos ...") [IMPLEMENTATION FACT].

---------------------------------------------------------------------------------------------------
## 0. Summary

Charon ("the ferryman") is the seat with the largest and longest-lived falsification apparatus in my
territory. It went through four distinct lives, each with its own ruler stack:

1. APRIL 2026, LMFDB / Langlands landscape (charon/src, charon/tests, charon/docs, charon/scripts): DuckDB of
   ~134K L-function zero vectors; preregistered representation batteries (Dirichlet 0.x-3.x, zeros Z.0-Z.4);
   within-conductor KMeans-ARI rank clustering; SO(2N) RMT simulation null; a 14/16-mechanism "stripping"
   ledger; an LLM "council" of four vendors. Headline "rank lives in the spectral tail; 0.05 arithmetic
   residual beyond RMT; sign inversion beyond RMT" (04-02..04-05) died within three days to Charon's own
   mean-spacing normalization test ("everything was scale") [LATER CORRECTION: charon/docs/
   journal_2026-04-05_finale.md, retrospective.md] -- but the collapse documents entered git only on
   2026-08-18 (cf2438a5d) from a stash, and north_star.md / spectral_tail_paper.md at HEAD still carry the
   dead headline with no supersession marker [IMPLEMENTATION FACT].
2. APRIL-MAY, CrossDomainCartographer battery (cartography/shared/scripts/): F1-F14 falsification_battery.py,
   battery_v2.py F15-F32, battery_nulls.py, known_truth_battery.py, m1_battery_calibration.py (the "v10
   battery", 25 tests in 4 tiers, "FROZEN"). The "known truths calibrate the pipeline" claim (39 then "180
   known truths, 100% recovery") is aimed BESIDE the instrument: known_truth_battery.py imports no battery
   module and runs its own permutation test on theorem-strength effects [IMPLEMENTATION FACT]. The only
   planted-signal calibration (1cc2e0f3d, 2026-04-12) covers battery_v2's F24 eta-squared test only: misses
   eta2=0.01, underestimates 0.10-0.14 by ~30%, false-positive on random-walk half-splits [REPORTED RESULT --
   UNVERIFIED, numbers in committed cartography/shared/scripts/v2/battery_calibration_results.json].
   Ownership shared with Harmonia (same role dir); the Harmonia crawler may cover internals.
3. MAY-JUNE, the Charon swarm (charon/agents: Stygian, Erebos, Hecate-swarm, Lethe, Acheron, Moros, Pollux,
   Nephele) and Substrate-Tester diagnostics: real permutation / Westfall-Young / degeneracy machinery, but
   closed-loop (one author lineage generates claims, falsifies them and measures the ledger), ledgers
   dominated by pipeline-state labels, Erebos "findings" reclassified as catalog artifacts, and the key
   pair-aware null later shown (Necropolis, 2026-09-11) unable to detect a planted signal (0/3 at N=699).
4. AUG-SEP, kill authority for Ergon's Metabolization Probe (charon/probe, attacks/preflight.py,
   ergon/probe/f_null.py): the methodologically strongest work -- calibrated identity nulls (R7), a
   three-valued Wilson band rule, arm-leak attacks with a planted one-character positive control,
   executable C1/C2 checks with PASS/FAIL/INDETERMINATE, eligibility counts and cheat controls (17 tests,
   reproduced by Aporia 71403839d), and refusals of unreachable protocols (M-004). Its weakness is
   conflicted authorship (Charon built F-null, F-generic, R7 and preflight, then ruled on runs using them)
   and that the decisive factorial was never run (pipeline dormant 09-11).

How strong was the machinery? Era 1: weak (no positive control anywhere in charon/; tautological passes;
label leak; council not independent). Era 2: one partial calibration of one test; the headline calibration
claim is misdirected. Era 3: real null code, but detectability unproven and later disproven for the key
statistic. Era 4: genuinely good instrument hygiene at small scale, never exercised on a completed
experiment. Charon's own CALIBRATION.md records that its errors drift toward SEVERITY INFLATION (an
adversarial seat's characteristic false-positive direction).

---------------------------------------------------------------------------------------------------
## 1. Charter and role evolution

- Name: Charon. No other aliases. Sub-agents in its tree carry their own names; NOTE two traps: (a)
  charon/agents/hecate is a Charon-swarm MI daemon (May 2026), NOT the later Hecate novelty seat; (b) Erebos
  was named "Hephaestus" until 48444edca (05-26), renamed for collision with agents/hephaestus
  [IMPLEMENTATION FACT: charon/agents/hecate/CHARTER.md; charon/agents/erebos/daemon.py header].
- Era 1 charter (March to mid-May): "cross-domain mathematical bridge discovery, falsification battery
  guardianship"; owned the v10 battery, search_engine.py, concept_index.py, tensor_bridge.py,
  shadow_tensor.py, charon/data/charon.duckdb [DESIGN INTENT / HISTORICAL CLAIM: roles/Charon/
  RESPONSIBILITIES.md, body marked HISTORICAL 09-11]. "First crossing April 1, returned April 15".
  CrossDomainCartographer role: roles/CrossDomainCartographer/CrossDomainCartographer_Charon_Role.md
  [HISTORICAL CLAIM].
- 2026-05-05 substrate pivot (roles/Charon/CHARTER.md, 223da5234): adversarial reviewer of Techne/Ergon/
  Harmonia output; standing orders incl. SO1 "convergence is signal, not validation", SO3 "the residual is
  data", SO7 "validate the validation" [DESIGN INTENT]. Cross-pollination protocol (operator pastes
  artifacts to 3-5 frontier models) as standing review; Charon later wrote it "has never had a null"
  (charon/CHARON_SESSION_2026-08-12.md s6) [HISTORICAL CLAIM].
- 2026-05-15 revival backlog (charon/BACKLOG.md, 24d3509b8); 05-19..06-03 swarm era; dormant 06-28..08-12.
- 2026-08-12 revival assessment: Harmonia's M0 result (06-27) "a verdict on my instrument" -- the
  verifier_lens certified zero novel-shaped truths (expressiveness wall); proposed Move B "decoy-calibrated
  reviewers" (planted defects in review rounds) and Move C "graveyard eval"; none found executed
  [HISTORICAL CLAIM; UNKNOWN whether executed].
- 2026-08-16..09-11: kill authority, F-generic author, F-null/R7 builder for Ergon's Metabolization Probe
  (pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md s4.1) [DESIGN INTENT]. Co-gate Harmonia B. Hosts: M1
  mainly; 09-01 session on M2 (M1 out of tokens) [HISTORICAL CLAIM: charon/CHARON_SESSION_2026-09-01.md].
- 2026-08-25 post-reset plan (roles/Charon/PLAN_2026-08-25_post_reset.md, 432eb8c48): R-A residue thesis
  RETIRED; R-B no corpus rebuild; R-C regret primary; R-D preflight FROZEN; R-E Q3 effect-signature test
  REJECTED. Class I/II/III epistemic taxonomy [DESIGN INTENT].
- 2026-09-11 base-role adoption (383818522; roles/Charon/BASE_ROLE_ADOPTION_2026-09-11.txt); STATUS,
  CALIBRATION, BACKLOG_H0H5, journal created; same day C1/C2 checks (5af5e5562), base-role self-test attack
  (88a6bab2c), H0-H5 kill list (8a7feca74) [IMPLEMENTATION FACT].
- Terminal state: last Charon-signed commit 2026-09-11 on any branch. Probe pipeline DORMANT, scheduled
  tasks disabled; step 2 built, preregistered, UNRUN with premise withdrawn (CHARON-22); Apollo E9 battery
  never confirmed used; Charon holds gates (HB3-2, HB3-3, C1, C2, F-hint >= 0.5225, leakage_gate vacuity
  stamp) "enforced by nothing but this seat" (CH-2026-09-01-A) [HISTORICAL CLAIM: roles/Charon/STATUS.md,
  CALIBRATION.md].
- Relations: Aporia (hypothesis source for frontier batches; independent re-runner of C1/C2), Ergon (ruled
  party, driver), Harmonia (co-owner of battery; Harmonia B parallel exit reviews; Harmonia C chance floor),
  Techne (sigma_kernel author; caught Hecate-swarm sampling bug; #424 canary harness rejected by Charon),
  Necropolis/Rhadamanthus (09-11 executed re-tests of Erebos/Pollux).
- Atlas: no tracked mention of Charon in atlas/ or roles/Atlas/ (case-insensitive git grep) -- Atlas is
  silent; nothing to verify or contradict [IMPLEMENTATION FACT].

---------------------------------------------------------------------------------------------------
## 2. Code / system architecture (engines)

E1 Langlands landscape pipeline [IMPLEMENTATION FACT, 9e189d683 2026-04-01]: charon/src/ingest*.py from the
LMFDB Postgres mirror (devmirror.lmfdb.xyz) into charon/data/charon.duckdb (1.18 GB; retired to Postgres
prometheus_fire.charon_duckdb on 06-24, fa8f625a1, charon/src/db.py facade); embed.py, build_graph.py
(~783K edges), disagreement_atlas.py (A/B/C/D classes; "Type B = candidate discoveries"),
characterize_type_b.py; tests charon/tests/test_03/11/13/21 + zero_battery.py; charon/scripts/full_audit.py
(clean ZEROS-ONLY rerun). Scale: ~31K EC, ~102K classical MF, conductor <= 5000.

E2 Spectral-tail research battery [IMPLEMENTATION FACT]: research_battery.py (within-conductor ARI),
rmt_simulation.py (SO(2N) naive + Metropolis), bsd_zero_experiments.py, extended_ablation.py,
conductor_scaling.py, inner_twist_analysis.py; ledger charon/docs/falsification_battery.md.

E3 Frontier/BSD/abc hypothesis scripts [IMPLEMENTATION FACT]: charon/scripts/frontier_batch1..5.py (25 Aporia
hypotheses), bsd_battery.py, bsd_at_scale.py, abc_battery.py, f011_*.py, lehmer_*.py, selmer_*.py,
artin_entireness.py, greenberg_screen.py; outputs charon/data/*.json (partly uncommitted, see s13).

E4 LLM council harness [IMPLEMENTATION FACT]: charon/src/fire_council*.py -- one prompt + one shared system
message ("world-class mathematician and hostile scientific reviewer") to gpt-4.1, claude-sonnet-4,
gemini-2.5-flash, DeepSeek; prompts charon/docs/council_prompt_*.md; responses charon/reports/
council_responses/; consensus files at charon/ root. 35 Gemini deep-research packages in charon/research/.

E5 CrossDomainCartographer v10 battery (shared with Harmonia) [IMPLEMENTATION FACT]: cartography/shared/
scripts/falsification_battery.py (F1 label permutation 10K p<0.001, F2 subset stability, F3 |d|>=0.2, F4
confound sweep, F5 alternative normalization, F6 multiple comparison, F7 dose-response, F8 direction, F9
simpler explanation, F10 outliers, F11 CV, F12 partial correlation, F13 growth-rate, F14 phase shift;
classify_kill), battery_v2.py (F15-F32), battery_unified.py (wrapper: if falsification_battery is not
importable, F1-F14 are "SKIPPED" and the verdict degrades to CONJECTURE), battery_nulls.py,
known_truth_battery.py, known_truth_expansion.py, m1_battery_calibration.py.

E6 Charon swarm [IMPLEMENTATION FACT: charon/agents/_base.py subclasses harmonia.agents._base.HarmoniaAgent;
LLM via scripts/llm_cascade.py Cerebras Qwen3-235B -> Groq Llama-3.3-70B -> NVIDIA Nemotron-120B ->
DeepSeek-V4-Flash]: design charon/agents/DESIGN_2026-05-19.md; v0.1 d67dbd8b8 (05-19) .. v0.8 48444edca;
Erebos ITER-1..84 to 06-03 (d7120eb5a). Runtime state, ledgers and artifacts were gitignored and are absent
[IMPLEMENTATION FACT per engine/necropolis/dossiers/erebos_evidence/README.md].
- Stygian (daemon 591, executor 543, 40 loaders): runs the v10 battery via battery_unified; only BL-C-001
  Lehmer and BL-C-002 BSD have real loaders; others short-circuit to UNVERIFIED; kill_pattern = the
  alphabetically FIRST failing sub-test (executor.py:100-115, verified).
- Erebos (25 rule-based generator archetypes G01-G25, 13 Layer-2 primitives, sprint1 A1-A10, phase3 nulls).
- Hecate-swarm (MI(kill_pattern, generator) + label-permutation null, mi_z alarm 2.0 x 7 ticks).
- Lethe (LLM judge of conjecture status, FALSE_FORM_THRESHOLD 0.30), Acheron (8-term coordinate-collision
  dictionary), Moros (3-provider critique convergence, Jaccard), Pollux (Spearman spacing coincidences over
  Mahler subsets), Nephele (arxiv RSS fallback).

E7 Substrate-Tester (charon/diagnostics, fires #1-#66, 05-06..05-09): a Techne instance re-roled
"Charon-aligned", testing sigma_kernel (which Techne wrote): property fuzzing, ~10-mutant/module mutation
testing, independence-smuggle attacks, Lehmer precision-gradient re-checks. Plus substrate cartography suite
(COST_TO_KILL, SURVIVING_CLAIM_MORPHOLOGY, COVERAGE_MAP, PI0_REPORT) [IMPLEMENTATION FACT / HISTORICAL
CLAIM].

E8 Metabolization-probe ruling apparatus (Aug-Sep): charon/probe/*.md rulings + run_r7_verification.py,
run_r7_d1d2_build2.py, exit_review_3_attack.py, charon_gate_fire_2026-08-25.py, residue_pool_ruling
_2026-09-01.py, c1c2_checks.py (+17 tests); attacks/preflight.py (334 lines, pre-commit hook on M1 only);
ergon/probe/f_null.py and f_generic.py (Charon-authored code inside Ergon's tree) [IMPLEMENTATION FACT].

E9 Corpus census and step 2: charon/generator_census.py (v1, killed), generator_census_v2.py (exact
byte-regex counts over 370.9 GB, 555,847,800 rows), charon/step2/ (choice-point census, regret harness,
preflight; UNRUN) [IMPLEMENTATION FACT / REPORTED RESULT -- UNVERIFIED].

E10 Cognitive Ceiling v0 (charon/ceiling_v0/, 4 unsigned commits 2026-08-23): toy hidden Z_3^3 group-action
world, frozen reasoner vs non-model proposers, environmental rule verifier, ablations A1-A8, falsifiers
F1-F8 [IMPLEMENTATION FACT for files; seat attribution UNKNOWN / AMBIGUOUS -- prometheus_llm/handoff/
M1_to_M2_20260822.md:216 calls it M1's untracked work; no doc names Charon].

E11 Side instruments: charon/playground/tt_proof_skeletons (GA + MAP-Elites over tensor-train operator
sequences, planted rank-3 target), charon/quality/generator_quality_probe.py (counter-equivalence triage),
charon/probe_seam_leak.py, roles/Charon/apollo_e9 (42-task held-out battery for Apollo), charon/v2/
oscillation_shadow.py.

---------------------------------------------------------------------------------------------------
## 3. Inputs and outputs

Inputs: LMFDB mirror (EC, MF, Dirichlet, genus-2, NF, Artin), KnotInfo, Fungrim, OEIS; Mossinghoff Mahler
catalog; Aporia hypothesis lists; Prometheus kill ledgers (Theseus corpus, 265 files, 370.9 GB); Ergon
probe manifests and ledgers; other seats' code (sigma_kernel, ergon handoff, Eos/Techne harnesses).
Outputs: kill ledgers and verdict docs (charon/docs, charon/reports, charon/probe/RULINGS_*), JSON results
(charon/data/*.json), council transcripts, Theseus-shaped kill_ledger rows (swarm; lost), pivot/erebos_* and
pivot/sprint1/* verdicts, rulings that gate Ergon (bands, admissibility, C1/C2), preflight hook, comms posts.

## 4. Claim class it was meant to police

(a) Cross-domain mathematical "bridges" and structure in LMFDB data (is a coordinate arithmetic or trivial?
is an effect beyond RMT/known theory?); (b) Aporia-sourced conjectural hypotheses against finite databases;
(c) May-June: whether LLM-composed/forged claims survive the battery (and whether the Layer-2 "substrate"
adds signal beyond a counter); (d) Aug-Sep: whether an LLM experiment's arms are fair (identity null
indistinguishable, no leakage, band leveled, inputs pinned and real) so that a residue-carry effect could be
attributed [DESIGN INTENT].

---------------------------------------------------------------------------------------------------
## 5. Measurement methodology (by era)

- Era 1: preregistered thresholds "SET BEFORE DATA" in zero_battery.py THRESHOLDS (CV>0.15, AUC ratio<0.80,
  ARI>=0.30, residual ARI>=0.15, d>0.8) [IMPLEMENTATION FACT]; KMeans k=min(n//2,5) within exact-conductor
  strata; Cohen d on gap statistics; SO(2N) simulation as quasi-null; linear partialling of candidate
  confounds; LLM council critique.
- Era 2: label-permutation F1, effect size, subset stability, normalization alternatives, partial
  correlation, FDR (F26), transportability (F25); verdict tiers KILLED / PROBABLE B+ / POSSIBLE A /
  CONJECTURE (battery_unified._classify_correlation) [IMPLEMENTATION FACT].
- Era 3: permutation nulls (binary split, WY max-T, pair-aware, triplet, cross-cell), counter-baseline
  comparisons, BOCPD, bootstrap CI, MC G-test, plug-in MI with shuffle null, LLM judge, Jaccard convergence.
- Era 4: calibrated same-distribution reference for null balance (200 disjoint pairs, p95 tolerances);
  blinded classifiers (logistic on char 1-4-grams + numeric features, GroupKFold by task uid, permutation
  refits) for arm separability; Wilson 98.75% intervals with Bonferroni for band membership; exact hashing
  for pool pinning; deterministic preflight checks; explicit eligible/fired counts and a third outcome.

## 6. Null / control generation (inventory; see ruler.jsonl for each)

Era 1: label-shuffle (rank permutation, 1000 trials, null ARI 0.006); SO(2N) RMT simulation (N_MATRIX=60,
N_TRIALS=50); 500 random dim-2 forms (genus-2 crossing baseline); Dirichlet representation as a
negative-comparison; O+ matched null (SO(80), 20K) and CUE surrogate (both NOT IN GIT); matched-GUE
multi-gap null for F011 (gap constants 0.1472/0.1741/0.1725/0.1468); mean-spacing self-normalization.
Era 2: F1 label permutation; battery_nulls.py integer/fraction nulls ("continuous nulls too lenient for
integer data"); F24 permutation-null eta2; synthetic eta2 injection + random groups + shuffled labels
(m1_battery_calibration.py).
Era 3: run_binary_split_permutation_null; run_multi_binary_westfall_young_null (c75965bb5); pair-aware and
triplet permutation nulls (d7120eb5a); cross-cell permutation null, scale stress, parent-child isolation
(36f46b97f); real_residue_smoke shuffle + per-plugin counter (fbe4f6b7a); Hecate-swarm label-permutation MI
null; synthetic smooth control (G10).
Era 4: F-null identity null (builds #0 categorical, #1 nearest-neighbour, #2 exchangeable draw); F-generic
"think harder" clean-room arm (~8,202 tokens, +/-5% token matcher); same-pool disjoint-pair calibration;
permutation refits for arm classifiers; within-record ablation comparator (R2-6); chance-floor reasoning for
heuristics (F-hint 0.5225); length-leak controls for the Apollo E9 battery (pick-shortest/longest ~0.256).

## 7. Positive controls

- charon/ (Era 1): NONE implemented. The specified "Test 3.2 Historical Test" (hold out a post-1995
  correspondence) exists only in prose (charon/docs/test battery/test battery.md:44, summary.md) -- no code
  on any branch [IMPLEMENTATION FACT per fork git grep]. Lehmer's polynomial recovered by the exhaustive
  scan acts as a known-answer check [REPORTED RESULT -- UNVERIFIED].
- Era 2: known_truth_battery.py -- 38/39 theorems "VALIDATED" (12f4403aa; results cartography/convergence/
  data/known_truth_battery_results.json, the one failure "Alexander(1) = 1" with p=0 z=999 placeholder) but
  using its OWN test() permutation function, not F1-F14 [IMPLEMENTATION FACT, verified]; all effects
  theorem-strength, none near threshold. m1_battery_calibration.py: planted eta2 0.001..0.50 (single seed,
  5 groups x 200) -- detected >= 0.02, missed 0.01 [REPORTED RESULT -- UNVERIFIED].
- Era 3: Sprint-1 A1-A10 synthetic data with planted structure (detect what they planted); G10 Salem cluster
  edge recovered as known-answer; TT playground planted rank 3 recovered (with an oracle "ansatz" operator);
  Necropolis 09-11 PLANTED partner-conditioned linkage: pair-aware null detected 0/3 [IMPLEMENTATION FACT:
  engine/necropolis/dossiers/erebos_evidence/erebos_null_instrument_calibration_result.json, per fork].
  Substrate-Tester P0 smuggle is a demonstrated defect (positive for the attack).
- Era 4: exit review #3 planted one trailing space on one arm -> caught at 1.0000; preflight --selftest
  plants a defect per check (9/9 reported); ratchet positive control added 4eccd18fb after self-catch; C1
  planted pool copy -> POOL_MOVED; C2 planted HTTP 504 row rendered 56/56 -> FAIL; census v2 re-finds c1's
  mutation_side unprompted; 8-world gate-fire (W1/W2/W4-W7 planted per-arm defects) [REPORTED RESULT --
  UNVERIFIED].

## 8. Negative controls

Era 1: Dirichlet representation failing the parallel battery; rank-label permutation. Era 2: random groups
(0/100), random cross-domain (2/100), shuffled labels (0/100) for battery_v2. Era 3: shuffle nulls;
Necropolis NULL worlds 0 FP for pair-aware null. Era 4: clean-data silence in preflight selftest; W0 clean
and W3 arm-invariant-inside-residue (over-sensitivity control) in the gate-fire; live post-fix D0 pipeline
0.5000 for the arm classifier; LOADER_ADMITS_NOTHING cheat -> INDETERMINATE in C2.

## 9. Neutral / intermediate controls

Era 4 R2-6 pre-committed a STRUCTURAL-ZERO "vacuous" reading before the within-record ablation comparator;
band ruling's UNDECIDED third value; C1/C2 INDETERMINATE outcomes (NOTHING_COULD_HAVE_FIRED,
UNATTRIBUTABLE). Era 1: "noisy ground truths" in calibration (Z->radius real, gap autocorr weak, Simpson's
paradox) [REPORTED RESULT -- UNVERIFIED].

---------------------------------------------------------------------------------------------------
## 10. Qualification criteria / gates / thresholds (selected)

- Z-battery thresholds as above; Dirichlet 0.3 "trivial explains >90% => fail", 2.1 "embedding must beat raw
  kNN by 5pp".
- F1 p<0.001 (10K perms), F3 |d|>=0.2; tiers KILLED/B+/A/CONJECTURE; "battery FROZEN at 25 tests ... Don't
  add F25" -- yet battery_v2.py added F25-F32 on 2026-04-12 (40435dd7a, 1b5e851b0, 3b42c87b6)
  [LATER CORRECTION / CONTRADICTION, per fork].
- Stygian: PROMOTED/REJECTED/UNVERIFIED; binary-split PROMOTED if observed > null p95 (one-sided).
- Hecate-swarm MI drift alarm z<2.0 for 7 ticks; Lethe emit at >=30% disagreement; Moros 0.25 (lowered from
  0.40 after 29 ticks never exceeded 0.190); degeneracy precondition n_eff>=30, entropy>=0.5 bits.
- Era 4: R7 layer (b) balanced accuracy <= 0.55; layer (a) family-wise rate <= calibrated 0.315; band
  [0.35,0.60] wholly inside Wilson 98.75%, decision-n 600/rung, UNDECIDED -> HEADROOM-FAILURE; truncation
  <= 0.02; transport >= 0.95; F-hint kill precondition 0.5225; "an amended rule is admissible only if it
  does not convert the observed result into the convenient one" (RULING_BAND_2026-08-16.md s5) [DESIGN
  INTENT].

## 11. Statistical methods

Permutation tests (label, pooled-shuffle, pair-aware, triplet), Westfall-Young max-T, Benjamini-Hochberg
style FDR (F26), bootstrap CIs, Wilson intervals with Bonferroni, McNemar (F-oracle vs F0, p=0.31),
Mann-Whitney, Spearman/Pearson with CIs, Cohen d, eta2, ARI on KMeans, DBSCAN, logistic regression
classifiers with GroupKFold, plug-in mutual information, BOCPD change points, GPD tail fits (abc), RMT
simulation. Weak spots: one-sided p95 thresholds before WY retrofit; plug-in MI over ~1,156 categories;
normal-approximation CI corrected to Wilson in ceiling_v0; single seeds (Sprint-1 A4/A7, calibration).

---------------------------------------------------------------------------------------------------
## 12. Independence assumptions

- LLM COUNCIL (Era 1) was not independent: one prompt and one system message to four vendors, prompts
  author-framed with Charon's claim list and summary numbers (reviewers never saw code or data), one
  Claude-family member while Charon is Claude, and consensus files mixing persona variants of the same model
  ("friendly claude", "claude the critic", "grumpy Claude") alongside other vendors [IMPLEMENTATION FACT:
  charon/src/fire_council.py; charon/*battery_consensus*.md]. Charon's own lesson: "The council ... amplifies
  narrative bias. Every council round demanded tests that confirmed the narrative. None demanded the
  mean-spacing test that killed it" (charon/docs/retrospective.md lesson 7) [HISTORICAL CLAIM]. Value: it did
  generate the first-zero ablation demand and the circularity critique of modularity recovery
  (charon/reports/council_review_synthesis.md).
- SWARM was closed-loop: one author lineage, shared CharonAgent/HarmoniaAgent base, one LLM cascade, one
  working tree; Erebos composes claims, Stygian (same ITER commits) falsifies them, Hecate measures the
  ledger they emit, Erebos reads Hecate. Lethe's judge and emitter can be the same model. Moros "frontier
  review" used the same cascade and mostly reviewed Charon's own docs. Self-acknowledged 8-point monoculture
  list in pivot/charon_swarm_diminishing_returns_2026-05-25.md [HISTORICAL CLAIM].
- SUBSTRATE-TESTER was a Techne instance testing Techne's sigma_kernel; two interleaved instances shared a
  role prompt [HISTORICAL CLAIM].
- ATTACKS USING TARGET CODE: charon/probe_seam_leak.py imports Ergon's own _renderable and _leak_safe_claim
  (existence-proof attack, shared code) [IMPLEMENTATION FACT per fork]; exit review #3 uses Charon's own
  stripper/classifier but Ergon's renderer to produce packets [HISTORICAL CLAIM].
- KILL AUTHORITY WAS ALSO BUILDER: Charon authored F-generic, F-null (ergon/probe/f_null.py), R7 code, band
  rule and preflight, then ruled on runs using them; RULINGS_2026-09-11.md states the conflict; mitigation =
  controls + Aporia's independent re-run of the 17 C1/C2 tests (71403839d) [HISTORICAL CLAIM].
- PARALLEL GATE (partial independence evidenced by disagreement): Harmonia B ran the same invariants blind
  of Charon (M2 vs M1). Same day (08-25) Harmonia B measured INV 7's constantize() ending in payload.strip(),
  so "a planted trailing space on one arm is caught 0/25" (cff6427b0, RE_REVIEW_SIGNOFF HB3-1), while
  Charon's W4 trailing-space world reported 40/40 caught and attributed it to INV 7
  (charon_gate_fire_2026-08-25.py:126-128). Either another check fired or the plants differ -- an attack's
  positive control may have passed for the wrong reason [UNKNOWN / AMBIGUOUS; not executed].
- Cross-pollination protocol acknowledged by Charon as never null-calibrated: "independent consequence, not
  independent intelligence" (ADJUDICATION_2026-08-25) [HISTORICAL CLAIM].
- Independence preserved by filing location: Apollo E9 and Techne #424 review filed under roles/Charon/ so
  the reviewed trees carry zero Charon commits [HISTORICAL CLAIM].

## 13. Provenance tracking

Saves:
- Techne's batch-by-batch check caught the Hecate-swarm v0.1 "monoculture" claim (alphabetical first file +
  5,000-record cap) and Charon retracted it (8b373fa9d; charon/agents/hecate/TECHNE_PROMPT_2026-05-19.md).
- M-004 full-archive scan corrected Charon's own 4,000-record sample claim the same day (35ea73809) and
  revealed 0/35,395,316 'unknown_kind' rows, refusing a protocol that would have returned a structural zero
  (charon/probe/VERDICT_M004_2026-08-18.md).
- Tier A exit review recomputed from pilot_d0_ledger.jsonl and found the deployed F-null arm separable at
  1.000 via a JSON header (.body vs .text), withdrawing a +9.6pp estimate (b3c57ffc0).
- Drip-truncation addendum: Charon withdrew its own "met" after finding the gate read a field no row
  carries (37483e68b); preflight dead_field() exists because of it.
- C1 exact-hash pool pinning; preregistration-before-run in step2 (4e412ed42) and ceiling_v0 (hash, later
  lost).
Failures:
- April-5 collapse documents (journal_2026-04-05_finale.md, retrospective.md, falsification_battery.md,
  paper_draft_v3.md) lived only in a stash for >3 months; committed 2026-08-18 (cf2438a5d "survived by
  luck"). north_star.md ("BATTERY COMPLETE. RESIDUAL SURVIVES.", verified at HEAD) and
  paper/spectral_tail_paper.md carry no supersession marker.
- 2026-04-22 data artifacts (oplus_null.json, cue_surrogate_axis3b.json, cm_24gap_scan.json, f011_*.json,
  lehmer_exhaustive_deg8_14.json) absent from every branch -- the era's only negative control (CUE
  surrogate) is unreproducible [IMPLEMENTATION FACT per fork `git log --all`].
- Swarm runtime ledgers/state gitignored and lost; all May numbers are quotes.
- frontier_batch_20260417_summary.json still reads H27 SURVIVES after 04-22 DATA-BLOCKED.
- ceiling_v0 SPEC preregistered 08-21 and hashed into manifests, destroyed in an 08-22 working-tree loss,
  reconstructed from transcript ("exploratory-with-attestation"); emission01 model transcripts lost
  (charon/ceiling_v0/RECOVERY.md).
- Campaign key ledger_id#seq collided on 200/206 records across blocks; it bit Charon's own first probe
  ("23-27% contaminated") (RULINGS_2026-09-01).
- Preflight pre-commit hook installed on M1's common gitdir only, absent on M2 (CH-2026-09-01-B).
- Index-race commits swept other seats' files on 08-25 (5d911209f, 9e93687ae) [HISTORICAL CLAIM].
- CALIBRATION.md seeded only 2026-09-11; earlier "what I got wrong" was prose only.
- Cross-seat correction lag: Charon declared F011 "DURABLE under matched-GUE" on 04-22, four days after
  Aporia's 04-18 downgrade (cartography/docs/four_paths_reflection_20260418.md).

---------------------------------------------------------------------------------------------------
## 14. Known defects (selected; full list in failures fragment)

Era 1: analytic_rank and root_number inside the clustered 24-dim zero vector, clustered against rank (label
leak; fixed in full_audit.py:1102-1108 "ZEROS-ONLY"; same commit 9e189d683, so which numbers the council saw
is UNKNOWN); zero-fill 0.0 for missing zeros; Z.4 shared-slot "fix" made true bridge pairs distance 0
(tautological pass praised by the council); Z.1 trivial baseline crippled by construction (EC-side features
constant across candidate MFs); RMT N=60 vs effective N~1.3; bsd_battery.py:213 hardcoded "verdict": "PASS"
"informational" counted in "5/5 PASS" (verified); abc_battery.py:237 and :336 hardcoded PASS inside "7/7
PASS" (verified); frontier_batch3.py H27 root-number PROXY (Frobenius-Schur indicator) produced "SURVIVES
p=5.5e-4"; untestable branch labelled KILLED (no third outcome); bsd_at_scale.py uses LMFDB sha_an which is
(by domain knowledge, not verified here) derived from the BSD quotient -> 1646/1646 near-tautological
[CODE-INFERRED CAPABILITY].
Era 2: known-truth calibration aimed beside F1-F14; v10 "FROZEN" battery silently extended to F32; random-walk
FP (no stationarity check); battery_unified silently SKIPs F1-F14 on import failure.
Era 3: generator-prefixed kill_pattern labels made MI(kill_pattern, generator) tautological (z=952);
pipeline-state labels (not_yet_implemented/no_loader) = 327/347 Stygian rows and 73.8% of G15 MI; Pollux
corr_raw = Spearman(sorted, sorted) identically 1 (a kill pattern unreachable), PROMOTED at 0.33-0.94 under
independence, truncation artifact; Lehmer infimum claim tested by distribution-shape tests on an N=200
subsample; first-alphabetical failing test as kill label; PI0_REPORT substitutes a beta-binomial random-arm
error rate and calls it pi0.
Era 4: R7 validated .text/.text while the pilot deployed .body/.text; drip truncation_rate identically 0
(dead field); leakage_gate PASS while vacuous; ATK-014 probe dead (hardcoded C:\prometheus path); ATK-013
probe "Defect ABSENT" over a live instance (tests under-reading only, globs block A only); census v1 prefix
truncation (MAXLINES 200k) and c1-shaped detector both biased toward "corpus spent"; pool unpinned (C1) and
transport failures rendered as residue (C2, 3.0% block A / 24.1% block B, arm-symmetric so invisible to all
shape gates).

## 15. Historical audits performed

By Charon (selection): council rounds (04-01..05); retrospective self-audit (04-05); 8 retractions in
CHARON_SESSION_2026-04-22.md; Erebos reclassification (05-27); Phase 3.0/3.K self-nulls (05-30, 06-03);
ERRATA on PHASE3_EFG (06-15, 7d2eacae5); SEAM_FIDELITY adversarial verdict on Ergon db4b2cac (06-17,
81c72c81d: "leak audit 0" FALSIFIED -- denylist passes CONFIRMED/REFUTED/r_raw=/p=); Harmonia reassessment
(06-23: sigma_kernel.PROMOTE "never re-runs the battery", trusts claim.verdict); COSIGN, R7, band, M-004,
Tier A exit reviews #1 and #3, RULINGS 08-23/08-25/09-01/09-11, census instrument audit (08-25),
CROSSCUT_2026-08-24 (theseus corpus = two near-disjoint populations: 100 .jsonl.gz vs 165 .jsonl, overlap
2), ORCHESTRATION_FORENSIC_MAP (08-31), Techne #424 canary harness rejection (08-27; ATK-020 "detector scored
on planted positives only", answer-key leak ATK-005), base-role self-test attack (09-11), H0-H5 kill list
(09-11: campaign_h1h0.py:356-358 S00 and S10 identical inputs; six cells are four conditions; the one
discriminating task is the planted control).
On Charon: Techne (Hecate-swarm sampling), Harmonia C (chance floor on the 57.8% regret headline,
a57fa8056/bdf6e8ff7; itself retracted 08-31, 1be87a0fe: floor was a ceiling 2p(1-p)), Harmonia B (parallel
exit reviews, HB3-1 whitespace), Aporia (independent C1/C2 re-run), Necropolis 09-11 (22a155201, 03ac0249b:
Erebos and Pollux NO_FAIR_TEST_ON_RECORD; also OVERTURNED Aporia P57's "seam never built" claim), Aporia
autopsy P46 on Acheron (LOW-BITS-PER-VERDICT-EMISSION).

## 16. Historical findings (outcome labels on the record)

- Dirichlet a_p coordinate: REPORTED NEGATIVE (battery fail) -- plausibly a straw-man FN (council: PCA
  clusters by vanishing order).
- Zero representation passes Z.0-Z.4: CONTAMINATED (label leak; tautological Z.4).
- Spectral tail encodes rank / 0.05 residual / sign inversion beyond RMT / three Neron channels / BSD wall:
  LATER OVERTURNED (scale, not shape); residual 0.74% within-conductor compression (p=1.3e-42) REPORTED
  RESULT -- UNVERIFIED.
- Type B 27,279 "candidate discoveries": INSTRUMENT FAILURE (graph incompleteness; self-corrected same day).
- 163 dim-2 forms / paramodular: INCONCLUSIVE ("kill stands, but for the wrong reason").
- Murmuration reproduction: reclassified as pipeline sanity check (proven theorem).
- Frontier batch 13 killed / 8 survived: MIXED; H27 CONTAMINATED (proxy); H40 downgraded (shared log|disc|);
  H80/H82 survive = absence of counterexample; P1.1 Mahler bridge KILL reversed (wrong polynomial) -- a
  documented FALSE NEGATIVE.
- abc 7/7 and BSD 5/5 PASS: INSTRUMENT FAILURE in part (hardcoded PASS); BSD 1646/1646 likely tautological.
- F011 multi-gap compression DURABLE (04-22): LATER OVERTURNED / downgraded (wrong ensemble; DHKMS excised).
- Lehmer F014 "PROMOTED +2": REPORTED POSITIVE as known-answer recovery; "smallest M = 1.31757" OVERTURNED.
- V-CM-Scaling "NEW LAW" (n=12): REPORTED POSITIVE, underpowered; CM gradient inversion (n=18) OVERTURNED at
  n=2134.
- A148 OBSTRUCTION_SHAPE cross-family: REPORTED NEGATIVE, but unreachable design (family max neg_x=3 vs
  required 4) -- FN.
- Hecate-swarm monoculture: INSTRUMENT FAILURE -> OVERTURNED (MI 0 -> 952 tautological -> ~0.5).
- Erebos Salem moderation PROMOTED 41.7x null; M=1.26 "phase transition": LATER OVERTURNED (catalog finding).
- G15 ledger MI 1.41 nats: CONTAMINATED (73.8% control-flow).
- Sprint-1 10/10 PASS: LATER OVERTURNED (calibration only; 8/10 synthetic).
- Phase 3.0: REPORTED NEGATIVE (z=9.80 vs shuffle, 0/13 deltas vs counter).
- Phase 3.D-E PASS -> 3.K p=0.105 underdetermined -> Necropolis: instrument cannot detect planted signal:
  INCONCLUSIVE / NO_FAIR_TEST_ON_RECORD.
- Pollux 39 PROMOTED "real signal": LATER OVERTURNED / INSTRUMENT FAILURE.
- Substrate-Tester P0 triangulation independence smuggle: REPORTED POSITIVE (defect), fix claimed VERIFIED
  (3dff7befe).
- TT proof skeletons: REPORTED NEGATIVE (eight self-recorded kills; transfer fails).
- Seam-fidelity "leak audit 0": REPORTED NEGATIVE against target (falsified).
- Pilot +9.6pp Delta_carry: CONTAMINATED / LATER OVERTURNED (withdrawn). F-oracle vs F0 +5.5pp p=0.31:
  INCONCLUSIVE.
- Tier B leveling 0.4764: REPORTED POSITIVE (stamped SCREEN-LENIENT; truncation unmeasured at first).
- C7 cold band NOT-LEVELED: INSTRUMENT FAILURE (TRUNCATION-UNMEASURED).
- D1/D2 identity null: INSTRUMENT FAILURE / INADMISSIBLE-NO-FAIR-NULL.
- M-004: refused pre-run (would have been a structural zero).
- Residue thesis: REPORTED NEGATIVE (RETIRED, R-A).
- "Corpus is spent": LATER OVERTURNED -> NOT-EARNED (census v2: 3 strict qualifiers).
- Regret non-vacuous 57.8%: LATER OVERTURNED (S2 withdrawn 09-01).
- Probe residue pool: CONTAMINATED (C1/C2 FAIL both blocks).
- ceiling_v0: P3d > P3c gap REPORTED POSITIVE (toy, |S|=27); compressibility law OVERTURNED (iter 26);
  mechanism INCONCLUSIVE (iter 28 void); LLM claims above chance FRAGILE (4/37, Wilson [0.043,0.247]).

## 17. Later corrections (timelines)

1. Spectral tail: 04-02 claim (6d6a40988) -> 04-04 "RESIDUAL SURVIVES" + paper draft -> 04-05 murder-board
   council asks for confirmatory tests -> 04-05 08:15 Charon's mean-spacing test: all d -> ~0 -> retrospective
   -> correction docs stashed -> 08-18 committed (cf2438a5d) -> HEAD north_star still unmarked.
2. F011: 04-18 Aporia downgrade (DHKMS) -> 04-21 Harmonia DHKMS audit -> 04-22 Charon "DURABLE" (did not see
   it) -> map_building_first_wave.md:125 demotion under block shuffle -> necropolis scout_table caveat.
3. Hecate-swarm: 05-19 MI=0 "monoculture" ticket -> Techne batch check -> v0.2 z=952 -> 05-23 tautology
   recognised -> 05-25 prefix-strip z=0.489.
4. Erebos: 05-26 PROMOTED -> 05-27 four-reviewer reclassification (0 mathematical) -> 05-29 Sprint-1 10/10 ->
   05-30 reframe + Phase 3.0 fail -> 05-30 3.D-E PASS -> 06-03 3.K p=0.105 -> 06-15 ERRATA -> 06-23/24 Aporia
   "realized~0" -> 08-21 P57 "seam never built" -> 09-11 Necropolis: instrument 0/3 on planted signal;
   P57 OVERTURNED; NO_FAIR_TEST_ON_RECORD.
5. Pollux: 06-10 / 06-22 "39 PROMOTED, real signal" -> 06-24 counter-claim "Learner has ZERO references"
   (also false) -> 09-11 Necropolis executed: degenerate statistic, truncation artifact, seams broken.
6. Probe Tier A: Ergon pilot +9.6pp -> 08-19 Charon TIER-A-EXIT-FAIL (header asymmetry) -> fix -> 08-21/23
   exit review #3 bounded PASS with planted control -> Tier B reachable (08-23) -> truncation addendum
   (08-23) -> 08-25 rulings / HB3-1 disagreement -> 09-01 C1/C2 -> 09-11 executable checks FAIL both blocks
   -> pipeline dormant; decisive factorial never read.
7. Regret: 08-25 57.8% divergence -> Harmonia C floor ~50% (+7.8pp) -> 08-31 Harmonia C retraction (floor was
   a ceiling) -> Charon exact D=41.1% below ceiling -> 09-01 S2 WITHDRAWN; step 2 unrun.

## 18. Pivots

bridge discovery in a tensor (March) -> LMFDB representation batteries (04-01) -> spectral tail (04-02..05)
-> CrossDomainCartographer battery owner (04-06..04-12) -> Aporia hypothesis executor (04-15..04-22) ->
"Prometheus thesis v2"/sigma-kernel (05-02) -> substrate-pivot adversarial reviewer (05-05) -> swarm
(05-19..06-03) -> adversarial audits of Ergon/Harmonia (06-17..06-23) -> dormant -> probe kill authority
(08-16..09-11) -> base role, dormant.

## 19. Journals / TODOs / backlogs

charon/docs/journal_2026-04-04.md, journal_2026-04-05*.md, exploration_state_2026-04-05.md (collapse);
charon/reports/journal_2026-04-02.md, sprint_summary_2026-04-01_02.md; CHARON_SESSION_2026-04-22 ..
2026-09-01.md (11 session logs); charon/BACKLOG.md (31 items, 05-15); charon/ROADMAP.md;
charon/research/TONIGHT_REMINDER.md, INDEX.md (35 DR packages); roles/Charon/todo_20260901.md,
BACKLOG_H0H5.md (25 rows; CHARON-21 independent-verifier lane undecided, CHARON-22 step 2 awaiting
operator), journal/2026-09-11.md, CALIBRATION.md (7 own errors; 3 of 5 on 09-01 pushed toward a BIGGER
finding), STATUS.md. charon/docs/falsification_battery.md shows many attacks left TODO (1d, 1g, 1h, 1j, 1k,
2h-2k, 3b, 4a, 4b, 4e, 5d-5f, 6c, 6e per fork).

## 20. Research reports (paths + one line)

- charon/docs/retrospective.md -- "everything was scale"; council amplified narrative.
- charon/paper/spectral_tail_paper.md, charon/docs/paper_draft_v2.md, v3.md -- drafts written before the
  decisive control.
- charon/reports/council_review_synthesis.md -- where outside review helped (circularity, ablation).
- charon/reports/type_b_characterization.md -- candidate discoveries = graph gaps.
- charon/reports/kill_tests_163_2026-04-02.md, first_zero_ablation_2026-04-02.md, genus2_crossing_2026-04-02.md.
- charon/research/package_*/ -- 35 Gemini deep-research packages (prior-art / literature), e.g. package_15
  normalization artifacts, package_8 RMT ablation (headers only read).
- charon/SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17.md -- denylist leak.
- charon/probe/*.md -- rulings (see s15).
- charon/CENSUS_INSTRUMENT_AUDIT_2026-08-25.md, charon/step2/CHOICE_POINT_FINDINGS_2026-08-25.md.
- charon/ORCHESTRATION_FORENSIC_MAP_2026-08-31.md -- reporter runs, executor does not.
- charon/ceiling_v0/RESULTS.md, ITERATION_LOG.md, PREDICTION_iter19..28.md.
- charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md -- "data-rich, trace-poor"; anti-calibration set
  (would F1/F6/F9/F11 kill Cantor or Galois?) admitted absent.
- charon/playground/tt_proof_skeletons/whitepaper_v1..v6 -- self-falsification ledger.

## 21. Failure cases

False positives: spectral tail; three channels; Type B; Z.4 / modularity recovery; H27 proxy; abc/BSD
hardcoded passes; F011 DURABLE; Erebos Salem / M=1.26; G15 MI; Sprint-1 10/10; Phase 3.D-E PASS; Pollux 39
PROMOTED; pilot +9.6pp; 57.8% regret headline; Moros threshold fitted to output; census-free "corpus spent"
reading (by others, overturned by Charon).
Plausible false negatives (FN): Dirichlet "straw man" kill; P1.1 Mahler bridge wrong polynomial; A148
unreachable design; mean-spacing as a universal first test can erase genuine scale-coupled arithmetic
structure (the 0.74% compression may be under-pursued); KMeans-ARI insensitivity and linear-only partialling;
Hecate-swarm v0.1 MI=0; pair-aware null with zero resolution at N=699 ("underdetermined" is a property of
the instrument); Lethe/Acheron saturation from stale catalog / 8-term dictionary; M-004 structural zero (caught
pre-run); 34 parentless generators (67.7% of corpus) cannot show transition structure by construction;
v10 battery "certified zero novel-shaped truths" (expressiveness wall, Harmonia M0); no anti-calibration set
(true-but-surprising mathematics) ever run against F1-F14; ATK-013 probe silent on a live instance; W4
attribution.

## 22. Mechanism archaeology

Partially relevant. Charon's 14/16-mechanism "stripping" ledger is correlational (linear partialling of
candidate invariants against ARI), not causal lesioning; ceiling_v0 iter 27 is the closest to a causal
lesion (enlarging the candidate pool halves the P3d-P3c gap, 2.7 SE) and iter 28's confirmatory lesion was
VOID because the lever emptied the pool. Erebos "mechanisms" were rule-based composition archetypes whose
"findings" decomposed into catalog construction. No transplantation tests. Correlation-only throughout Era 1.

## 23. Novelty / prior-art audit

Partially relevant. Novelty-adjacent machinery: council "literature search" prompt and 35 Gemini
deep-research packages (charon/research/); Erebos 05-27 four-tier taxonomy (substrate / catalog /
mathematical / literature-grade) -- the most explicit "unfamiliar to Prometheus vs new to science" guard in
my lane (0 mathematical, 0 literature-grade after review). Murmuration "reproduction" reclassified as a
proven theorem (Zubrilina; Sawin-Sutherland) only after council input. Type B "candidate discoveries" were an
absence-of-edge-in-our-own-graph novelty claim (blind spot = the graph). The spectral-tail paper targeted
Experimental Mathematics before the decisive control. No systematic prior-art corpus or search log found.

## 24. Lens inventory

- C1/C2 executable checks + preflight: reusable, small, positive/negative/cheat controlled; resolution =
  exact (hash, row-level); pipeline-specific schemas.
- Arm-separability classifier with planted 1-char positive control: reusable leakage lens for any
  multi-arm LLM experiment; surface-only (semantic leaks out of scope).
- Three-valued Wilson band rule: reusable decision gate for noisy estimates.
- R7 calibrated identity null: reusable pattern (same-distribution reference calibration); cannot see
  relation identity without layer (c).
- Permutation/WY/degeneracy/selection-discipline library (charon/agents/stygian/loaders/_*.py): reusable null
  generators; detectability unproven except synthetic; one catalog.
- battery_v2 F24 with its synthetic calibration: the only calibrated test; known bias and FP modes.
- RMT SO(2N) simulator and LMFDB zero pipeline: reusable data/simulation substrate; mis-sized null.
- ceiling_v0: toy accumulation world with exemplary falsifier discipline; resolution ceiling |S|=27.
- Council harness: idea generator, not adjudicator.
- Generator census v2: reusable corpus-forensics lens with positive control.

## 25. What I did not read / open questions

Not read by me or forks: battery_v2 F15-F32 internals and falsification_battery F4-F14 internals (headers
only); most council transcripts (third_complete_responses.md 1,931 lines); research packages beyond INDEX;
25 Erebos generator bodies and most of the 29 composition loaders; individual substrate_tester fire JSONs;
pivot/* Erebos design/review docs (~35) and Moros outputs; ceiling_v0 *.py, step2/*.py, census v2 code,
exit_review_3_attack.py (only rulings text); COSIGN, EXTERNAL_REVIEW, CROSSCUT ss2-5 bodies; comms posts
#149-159; Atlas DB rows. No test re-run.
Open: Did Harmonia B and Charon ever reconcile the band ruling? Which check caught W4? Were HB3-1/2/3, C1,
C2, F-hint, leakage stamp ever cleared? Who authored ceiling_v0? Which zero-battery numbers did the council
see (leaky or clean)? Was the "180 known truths" expansion (known_truth_expansion.py, results not tracked)
ever run through F1-F14? Was the "0.725-bit MI over 314K kills" thesis checked for the prefix tautology?
