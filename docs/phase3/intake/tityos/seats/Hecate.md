# Hecate -- Tityos Phase 3 forensic dossier

Crawler: Tityos worker g4_novelty (read-only), 2026-10-01. Worktree tityos-phase3 at origin/main.
Labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].
No holdout or nestor_secrets path was opened.

## 0. Summary

- Two unrelated seats carry the name. (1) charon/agents/hecate/ (May 2026, Charon swarm): a nightly
  daemon computing MI(kill_pattern, generator_id) with a permutation null over Theseus kill ledgers.
  (2) roles/Hecate + hecate/ (created 2026-09-29 on M1): "triplicate deep search" over the historical
  Hephaestus/Nous concept triplicates. [IMPLEMENTATION FACT] (roles/Hecate/RESPONSIBILITIES.md s2;
  charon/agents/hecate/CHARTER.md)
- The 2026-09 Hecate policed claims of the form "this concept collision yields a new mechanism /
  candidate principle", and "triplicate collision adds value over pairs/singles". It built a real
  funnel: preregistered selection, Pass 0-3 generation, control-first probe worlds (treatment, control,
  null twin, positive control, CHEAT control), Pass 4 attacks (R/ORIG/ALT), a verdict validator, an
  LLM "gravity" (prior-recognition) detector, a meta-experiment (5 arms), an alien-lawful assay, a
  novelty autopsy, and a Wave-2 audit harness (metamorphic tests, exact-arithmetic shadow evaluator,
  derived-file reproduction tests). [IMPLEMENTATION FACT]
- Result on the record: 16 triplicates, 243 mechanisms, 37 probed worlds, 5 SIGNALs, 0 survived first
  falsification; meta v1 INDETERMINATE; zero UNFAMILIAR in 399 items. [REPORTED RESULT -- UNVERIFIED]
- The novelty machinery was the weakest part. No literature, code or web corpus was ever searched: every
  prompt forbids search, the prior-art pass (HECATE-14) never ran, 394/396 hypotheses carry no prior-art
  label, and the only two KNOWN_ANALOGUE_FOUND labels come from Pass-4 experimental reduction named from
  model memory. "Novelty" was measured only by an LLM (claude-opus-5-5) recognition detector whose
  calibration gate had no coherent-unfamiliar control and did not test FAMILIAR vs COMPOSITE, the
  boundary the meta result depends on. Hecate's own autopsy showed the detector called 0/32 mechanically
  alien rules UNFAMILIAR, and withdrew LLM prior-recognition as a novelty ruler. [IMPLEMENTATION FACT /
  LATER CORRECTION]
- Strength: unusually dense self-correction (18 K-corrections, 8 contested items, a red-team that found
  the corrections biased in Hecate's favour). Weakness: nearly all generation, implementation, attack,
  detection and audit used the same model family (Claude), so "independent" mostly means "fresh
  session". [IMPLEMENTATION FACT]

## 1. Charter and role evolution

- Name prior use: charon/agents/hecate/ (2026-05-19, commit d67dbd8b8), "continuous gradient
  archaeology": MI between kill_pattern and operator class with N=200 permutation null and a
  SELF_AUDIT_ALARM if mi_z < 2.0 for 7 ticks. [IMPLEMENTATION FACT] (CHARTER.md, daemon.py 823 lines).
  Recorded as namesake, not predecessor (roles/Hecate/RESPONSIBILITIES.md s2). [HISTORICAL CLAIM]
- Creation 2026-09-29 (203fb3342): seat on M1 (SKULLPORT), base role, charter PENDING, "NO science".
  Pre-charter body: roles/Hecate/superseded/RESPONSIBILITIES_pre_charter_2026-09-29.md.
- Charter adopted same day (3cd459f84): operator charter verbatim at
  roles/Hecate/prompts/2026-09-29_charter/01_OPERATOR_CHARTER_verbatim.md -- 10 passes, ENGINE/FOSSIL/
  REJECT, "CRITICAL ANTI-GRAVITY RULE", PRIOR ART section (INDEPENDENTLY_GENERATED / KNOWN_ANALOGUE_FOUND
  / PARTIAL_PRIOR_ART / LIKELY_REDIRECT / POSSIBLY_NOVEL; "Do not claim novelty without evidence"),
  meta-lens "triplicate ecology". [DESIGN INTENT]
- 2026-09-30 operator directive: alien-lawful structure assay (e778cf000; roles/Hecate/prompts/
  2026-09-30_alien_lawful_assay/). [DESIGN INTENT]
- CWO-2026-09-30 (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md s3): CURRENT "Explain the novelty failure"
  with six named causes; NEXT alien Phase 2; RESERVE generator interventions. "Tyche should complement
  Hecate: Hecate attacks generated candidate mechanisms. Tyche searches the garbage pile." [DESIGN INTENT]
- CWO-2026-09-30B (finish-in-place) withdrew the promoted "mechanical novelty ruler" (journal
  roles/Hecate/journal/2026-09-30.md 13:18Z update; WORK_STATE.json line 80; TODO.md line 11). CWO-C:
  BLOCKED on free-tier quota for alien Families B/C. [HISTORICAL CLAIM]
- Terminal state at crawl: BLOCKED (quota), Wave-2 inference-saturation audits closed 2026-10-01
  (84518fffb, bb70ad7f4), ruling request on C1-C8 pending (roles/Hecate/harvest_w2/RULING_REQUEST_C1_C8.md,
  comms #1213). [HISTORICAL CLAIM]
- Relations: source seats Hephaestus/Nous (read-only); Collider (Cyclops) survey reused by citation;
  Hephaestus 2.0 Gravity Pilot (roles/Hephaestus/HEPHAESTUS_2_0_GRAVITY_PILOT.md, operator 2026-09-20)
  is the design source of the gravity detector; Harmonia audited it (#1037); Artemis routed residual
  reports to "Tyche, Hecate" (#1121, #1133; unread under finish-in-place); Lexis/Rhadamanthus named as
  possible Pass-10 reviewers, never engaged. [IMPLEMENTATION FACT / HISTORICAL CLAIM]

## 2. Code/system architecture

[IMPLEMENTATION FACT] unless marked. hecate/ has 590 tracked files.
- hecate/schema.py: record types, four honesty layers, PRIOR_ART enum, verdict validator (PROMISING/EXPAND
  need a preregistered deterministic predicate; upper layers need evidence rows). Tests in hecate/tests/.
- hecate/corpus.py: normalises Nous responses (agents/nous/runs/*/responses.jsonl) joined to
  agents/hephaestus/ledger.jsonl -> corpus/historical_triplicates.jsonl (gitignored, receipt hash).
  6,939 triples, 95 concepts. hecate/select.py: stratified seeded selector (seed 20260929; 5 strata).
- hecate/programs/HT-<id>/: program.json, pass files, worlds/W*/ (spec, evaluate.py, rows, OUTCOME.json,
  pass4/), DOSSIER.md (rendered by hecate/dossier.py). 16 programs.
- hecate/probe_select.py, probe_report.py, probe_round3.py, pass4_report.py: round orchestration and
  verdict application. Prompts: hecate/programs/_prompts/ (pass0_3_v1, pass3_v2, pass3_v3_DRAFT,
  probe_impl_v1..v3, pass4_impl_v1..v2).
- hecate/llm.py: isolated `claude -p` wrapper (empty cwd, no tools/MCP/settings, model pinned, prompt
  sha256 recorded; residue still reaches the model: SDK identity line, account email reminder, env
  block -- AUDIT_X). extract_json() first-object parser (defect, see s14).
- hecate/gravity/: detector_v1.md (prompt), run.py (one call per item, scrub, calibrate), controls_v1.json
  (14 controls), calibration_rows_v1.jsonl, gate_v1.json, calibration_v1.json.
- hecate/meta/: meta-experiment v1 (run_arms.py, scrub.py, scrub_v2_proposal.py, analyze.py, arms/,
  detector/, matcher/, REPORT_v1.md, RESULTS_v1.json, template_v1.md).
- hecate/alien/: alien-lawful assay (systems.py, generate.py, rules.py, dataset.py, tasks.py, runner.py,
  sandbox.py, score.py, analyze.py, baselines.py, verify.py, shadow_decisions.py, coverage_family_DRAFT.py,
  visual/, runs/claude|gptoss|gemini, REPORT_pilot.md). 100 systems.
- hecate/autopsy/: flow.py (Part A mechanism flow), reach.py (Part B detector reachability), FLOW.json,
  FLOW_postK4.json, REACH.json, reach_rows.jsonl, AUTOPSY.md.
- hecate/metamorphic/harness.py (Wave-2 INV_F: corrupts evaluator inputs); hecate/programs/_lib/
  evaluator_contract.py; hecate/tests/test_derived_reproduce.py, test_llm_isolation.py,
  test_shadow_decisions.py (suite 202 pass per 2dc4fbb01 [HISTORICAL CLAIM]).
- hecate/index/: discovery index nodes.jsonl/edges.jsonl/SUMMARY.json (derived_from 814, observed_under
  498, implemented_as 132, falsified_by 40 edges).
- Scale: compute 32.5 core-minutes over all probes and attacks (REVIEW_PACKET s5) [REPORTED RESULT --
  UNVERIFIED]; model calls on subscription claude -p; Groq/Gemini free tiers for alien B/C.
- Charon Hecate: charon/agents/hecate/daemon.py: _harvest_records (mtime-sorted stratified sampling after
  v0.2), _analyze (raw MI and cross-generator MI), permutation null, artifact emit.

## 3. Inputs and outputs

- Inputs: Hephaestus ledger + git-tracked Nous runs (11 gitignored Nous runs, 4,187 responses, excluded
  without disclosure -- AUDIT_Z5); operator charter/directives; model outputs. Outputs: program records,
  world rows, OUTCOME.json, dossiers, discovery index, meta rows, alien rows, reports, comms.
  [IMPLEMENTATION FACT / LATER CORRECTION]
- Charon Hecate: theseus/corpus/*.jsonl.gz + Stygian kill_ledger -> gradient_archaeology_<utc>.md.

## 4. Claim class it was meant to police

- "A collision of three distant concepts yields a mechanism that survives hostile tests" (charter).
- "Triplicates add value over pairs, singles, single-discipline and concept-free prompts" (meta).
- "This mechanism is novel / known" (PRIOR ART; gravity detector; anti-gravity rule).
- "An LLM can tell lawful-but-alien structure from noise and from familiar structure" (alien assay).
- Charon Hecate: "operator classes shape kill patterns" (emergent structure in the kill ledger).
[DESIGN INTENT]

## 5. Measurement methodology

- Probe worlds: small executable simulations; success clauses decided in code (evaluate.py) against
  treatment vs control, null twin, positive control (effect present by construction), CHEAT control;
  >= 5 seeds. Classes SIGNAL / NULL / CONFOUNDED / INSTRUMENT_FAIL / NOT_BUILT / SPEC_UNATTAINABLE.
  Pass 3 v2 freezes a spec only after its own controls show every clause attainable and discriminating
  (prereg 2026-09-30_pass3_v2). [IMPLEMENTATION FACT]
- Pass 4: R replication on fresh seeds; ORIG = implement the trivial/known explanation and see if it
  reproduces the effect (if it fires, label KNOWN_ANALOGUE_FOUND); ALT = alternative implementation.
  (prereg 2026-09-30_pass4_round1 lines 55-62). [IMPLEMENTATION FACT]
- Novelty: gravity detector (LLM classification FAMILIAR/COMPOSITE/UNFAMILIAR/INCOHERENT + prior_fit) on
  scrubbed text; meta M1 = FAMILIAR fraction; M2 = 4-way blinded matcher (can the concept set be
  recovered from the output); M3 deterministic structure checks; M4 distinct nearest families.
- Alien assay: model sees transitions of 100 finite systems (20 KNOWN, 40 ALIEN incl. 8 adversarial,
  30 incompressible nulls in classes CONJ/DSCRAMBLE/SCRAMBLE/SEDUCTIVE, 10 DESTROY); T1 rule/noise label,
  T2 predictions, code held-out exactness; scorer compares to simulator over full state space.
- Autopsy: Part A counts mechanism flow from committed records (no model); Part B runs the meta detector
  unchanged on KNOWN/ALIEN/DESTROY rule texts.

## 6. Null/control generation

- Probe worlds: null twin (same world with the mechanism removed), negative control, CHEAT control
  (an evaluator-gaming input); twin construction under-specified in ~11 worlds ("null-twin drift",
  AUDIT_Z2). [IMPLEMENTATION FACT / LATER CORRECTION]
- Alien assay: 30 incompressible nulls constructed to preserve visible regularities (+-1 steps,
  increment distributions, fixed points) while destroying the compact law; SEDUCTIVE nulls matched to
  adversarial aliens; DESTROY items. Answer key separate (hecate/alien/data/answer_key.json). Strongest
  null design in the seat. [IMPLEMENTATION FACT]
- Meta: arms S/O/G act as nulls for the triplicate arm; P (pair) is the decisive comparator.
- Gravity calibration: 4 hand-written nonsense controls (C11-C14), lexically separable from coherent
  controls by 17 mentalistic words (AUDIT_W s4). [LATER CORRECTION]
- Charon: permutation null over generator labels; later "cross-generator MI" restricted to kill patterns
  under >= 2 generators (1aaad0277).

## 7. Positive controls

- Probe worlds: positive control on every measured world (REVIEW_PACKET s7). But K4: HT-a9e2ba7618 W3's
  pilot checked only absolute ARI; the deciding clause was unattainable even for the PC. Ledger rule
  "pilots evaluate EVERY success clause on the positive control". [LATER CORRECTION]
- Gravity detector: 8 disguised knowns (PID, AIMD, Hebbian, Kalman, Turing RD, stigmergy, FSM,
  autocatalysis) 8/8 FAMILIAR; 2 composites (both called FAMILIAR, tallied as "2/2 detected"). NO
  coherent-unfamiliar positive control -> UNFAMILIAR detectability never demonstrated (AUDIT_W W6, W10;
  Harmonia EVIDENCE_AUDIT B; RULER_QUALITY s3). [IMPLEMENTATION FACT / LATER CORRECTION]
- Autopsy Part B used 32 mechanically alien rules as a de-facto UNFAMILIAR positive control: 0/32
  called UNFAMILIAR (Wilson upper 0.107) -> R1 "DETECTOR_CANNOT_REACH_UNFAMILIAR". Harmonia: shows only
  "this detector did not call these 32 UNFAMILIAR"; Hecate K6: inputs were scrubbed (rewrite rules
  erased) and R1 reflects the definition (C6). [REPORTED RESULT -- UNVERIFIED / LATER CORRECTION]
- Alien assay: KNOWN systems (20) learned 20/20; meets "ruler fires on known".
- DESIGN_K (draft, not run): code-certified coherent-unfamiliar (CU) controls from >= 2 authors incl. a
  non-Hecate author, plus a "claim audit" that implements the detector's own named priors.

## 8. Negative controls

- Nonsense controls 0/4 FAMILIAR (one-sided clause: nonsense called UNFAMILIAR would pass -- W4).
- Alien incompressible nulls: Claude labelled 19/30 RULE and 24/30 COHERENT (over-attribution); behaviour
  discriminated (AUC 0.98). Labels are not negative-control-clean. [REPORTED RESULT -- UNVERIFIED]
- CHEAT controls per world; INV_F: 4 cheat checks read cheat-only fields; 47f4/W1 all() over empty arm
  passes vacuously (latent). [LATER CORRECTION]
- Verdict validator: 13 cheat-control tests (REVIEW_PACKET s3).

## 9. Neutral/intermediate controls

- COMPOSITE class as intermediate; composites ungated. DESTROY items (lawful system with law partly
  destroyed) collected but ungated (RULER_QUALITY s3 R2). INCONCLUSIVE band in some frozen specs not
  honoured by round-1 classes (contested C1). [IMPLEMENTATION FACT / LATER CORRECTION]

## 10. Qualification criteria / gates / thresholds

- Gravity gate: PASS iff all_calls_ok and knowns >= 7/8 and nonsense FAMILIAR <= 1/4 (run.py:94).
- Meta M1: sign test over 8 units, ADDS_VALUE at >= 7/8 (p <= 0.035, actually 9/256 = 0.0352 -- K15);
  overall needs S, P, O. M2 LABELS_SHAPE_OUTPUT vs chance 0.25.
- Alien detector: T1 AUC >= 0.80 with CI-low >= 0.65 AND pair accuracy >= 0.80 (PREREG s7). Harmonia:
  AUC leg saturated (score is confidence), pair leg has a structural ceiling from 8 SEDUCTIVE pairs.
- Autopsy R1: UNFAMILIAR rate on ALIEN <= 0.10. Probe consequence tables per round; PROMISING requires a
  preregistered predicate. Charon: SELF_AUDIT_ALARM if mi_z < 2.0 for >= 7 ticks.

## 11. Statistical methods

Sign tests (meta), Wilson intervals (autopsy), bootstrap and Clopper-Pearson (alien; H2 zero-variance
bootstrap -- C7), Mann-Whitney (Q5 cheap-world cliff, one-sided p 0.006 later corrected to two-sided
0.012), within-program permutation tests with Bonferroni (INV_H), Mantel-Haenszel matching (INV_S),
ARI, Lyapunov exponents, AUC. Float threshold defect: H3 0.2 - 0.1 = 0.0999... (C5); exact shadow
evaluator built in response (264854c4b). [IMPLEMENTATION FACT / LATER CORRECTION]

## 12. Independence assumptions

- Generators (Pass 0-3: claude-opus-5-5; meta arms: claude-sonnet-5), probe implementers, Pass-4
  attackers, gravity detector, matcher (claude-opus-5-5), alien Family A subject (claude-opus-5-5), and
  Wave-2 auditors ("Hecate subagent") are all Claude-family sessions. Independence = fresh context +
  no search + forbidden reading lists. Shared model priors are the dominant non-independence: the same
  family that generates a mechanism judges its familiarity. [IMPLEMENTATION FACT]
- Charter s3.4 claims scorer is "a deterministic rubric or a different model from the generator": true
  only at the level of model size (Sonnet vs Opus) in meta v1. [DESIGN INTENT vs IMPLEMENTATION FACT]
- Harness asymmetry: only Claude subjects receive SDK residue (AUDIT_X). [LATER CORRECTION]
- External checks: Harmonia #1037 (roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30.md,
  RULER_QUALITY_2026-09-30.md) -- also LLM audit agents; REDTEAM_Y was a Hecate-commissioned red team
  and found the corrector biased (corrector = rule author). Alien Families B (gpt-oss-120b) and C
  (gemini-3.6-flash) were the only cross-family arms; both incomplete. [IMPLEMENTATION FACT]
- Same author wrote prereg, scorer, and corrections; ledger Q27 names this explicitly.

## 13. Provenance tracking

- Saved the day: K3 (gravity controls lost by a case-insensitive filename collision before b15a475b8,
  whose message claimed "+14 controls") was found by code reading and restored byte-verifiably from
  blind texts; AUDIT_Z5 confirmed 16/16 programs match source ledger lines; prompt sha256 per call made
  AUDIT_L able to reproduce RESULTS byte-for-byte; corpus rebuild receipt hash. [LATER CORRECTION]
- Failed: corpus boundary undisclosed (gitignored Nous runs); 6/16 historical "scrap" verdicts were
  API/forge failures not evaluations; a per-mechanism familiarity self-assessment existed only in chat
  replies, never committed (AUTOPSY Part A); derived files not reproducible from generators (K16:
  hand-appended notes in OUTCOME.json); gate_v1.json has a hand-added note key; 14 STALE prose claims
  after corrections without propagation (K15); DOSSIER.md for HT-55162c0ac0 still says "the author's
  prediction was wrong" after K1 reversed it. [LATER CORRECTION]
- Charon Hecate v0.2 added sampling_context to artifacts after the alphabetical-sampling artifact.

## 14. Known defects

See CORRECTIONS_2026-10-01.md K1-K18, C1-C8 and calibration/LEDGER.md (12 rows). Highlights:
gravity gate cannot fail on composites, has no CU control, substring family match ("ACO" in "Jacobson");
extract_json accepted inner objects of truncated replies; T1 question conflated regularity and law;
analogy classifier scores formalism naming; sandbox rejected valid lambdas; scorer crashed on vector
claims (filed UNTESTABLE); scrubber erased rewrite rules ("YZ -> XW" -> "[X] -> [X]") and literal
"novel/new/unique"; 32/42 evaluators accept copied seeds silently; both round-3 SIGNALs pass by
construction (INV_J); Pass-4 ORIG attacks decided by construction (8a87, 321a; Z1); ALT for 321a fixed
by counting (ledger row 2); refused detector call not retried and denominator policy unstated (C8).

## 15. Historical audits performed (by and on this seat)

- On: Harmonia EVIDENCE_AUDIT_2026-09-30 (3 MAJOR on Hecate: W6 ORIG under-read; zero-UNFAMILIAR
  uncalibrated; affine-vs-Claude mismatched); Harmonia RULER_QUALITY_2026-09-30 (alien rule MAJOR x2;
  autopsy R1 MAJOR; flow has no null MAJOR); REDTEAM_Y (bias in corrections).
- By (Wave 2, roles/Hecate/harvest_w2/): AUDIT_A, AUDIT_B (42 evaluators), ATTACK_C, ATTACK_D, AUDIT_L,
  AUDIT_M, AUDIT_O (242 prose claims: 196 MATCH, 14 STALE, 5 MISMATCH, 10 UNSOURCEABLE), AUDIT_W (gravity
  gate), AUDIT_X (call isolation), AUDIT_Z1/Z2/Z3/Z5, INV_E/F/G/H/J/N/S/Z4/Z8, DESIGN_K, DESIGN_P.
- Charon: Techne caught Hecate v0.1's alphabetical-sampling MI=0 artifact within hours (8b373fa9d).

## 16. Historical findings (outcome labels on the record)

- 16 programs, 0 survivors of Pass 4; PARK 14, PROBING 1 (HT-321a8fd8e0 = minimum-distance decoding),
  SPECULATIVE 1 after K4 -- REPORTED NEGATIVE/NULL (contested C1, C2).
- 5 SIGNALs: 71b6 (fixed shallow listener ties), 321a (textbook decoding radius), 5b0b (endpoint
  confound, ALT reversed sign), 8a87 (channel reset), 5516 (carrier amplitude, not chaos) -- LATER
  OVERTURNED (Pass 4) and INSTRUMENT FAILURE in part (INV_J: both round-3 SIGNALs pass by construction).
- Meta v1: M1 INDETERMINATE; T not distinguishable from P; zero UNFAMILIAR -- INSTRUMENT FAILURE for the
  zero (AUTOPSY R1, Harmonia B).
- Alien pilot (Claude): aliens learned 28/32 vs known 20/20; detector NOVELTY_DETECTOR_NOT_VALIDATED --
  MIXED (C6 contested: standard-only consistent set -> VALIDATED); INV_E: learning mostly table coverage.
- Novelty autopsy: C4 rulers mislabelled novelty SUPPORTED, C6 definition made target unreachable
  SUPPORTED; C1/C2 not discriminated -- MIXED; Part A LATER CORRECTED (K5, K14).
- Charon: "Theseus corpus is a monoculture" (MI = 0) -- LATER OVERTURNED (sampling artifact, 8b373fa9d);
  "mi_z = 946 emergent operator structure" -- LATER OVERTURNED (100% generator-prefix tautology,
  1aaad0277).

## 17. Later corrections (timelines)

- Gravity controls: b15a475b8 claims "+14 controls" -> file overwritten by gate output (case-folding) ->
  Hecate W2 code reading -> K3 restored controls_v1.json, test forbids case-colliding paths (684ffbbd1).
- Zero UNFAMILIAR: d80c5cc4c "zero UNFAMILIAR in any arm" -> REPORT_v1 itself flags no CU control ->
  Harmonia #1037 B MAJOR -> autopsy R1 (e4a05ba3b) "instrument result" -> Harmonia RULER_QUALITY: R1 also
  uncalibrated -> K6: Part B inputs scrubbed, R1 is the definition (C6) -> status: zero is uninformative.
- W6 ORIG: "did not fire" + ledger row 4 "my prediction was wrong" -> Harmonia #1037 A -> K1 ORIG FIRED in
  substance, ledger row 4 revised -> K18 R also wrong-in-substance -> PARK stands on failed ALT.
- Affine vs Claude: REPORT_pilot "affine 0.44 beats Claude 0.33" -> Harmonia C -> K2 KILLED (0.51 vs 0.49)
  -> INV_Z8: structured polynomial solver cracks adversarial maps, so "hard, not LLM-specific" is wrong
  for maps (contested).
- K4 (a9e2 W3 NULL -> SPEC_UNATTAINABLE, PARK -> SPECULATIVE) -> REDTEAM_Y: stated cause false, moved
  without ruling -> treated as contested.
- Corrections themselves -> REDTEAM_Y: readings biased toward Hecate -> APPLY recommendations withdrawn
  (2dc4fbb01, K17).

## 18. Pivots

Charter program -> (CWO) novelty autopsy -> alien-lawful assay -> mechanical novelty ruler promoted then
withdrawn (CWO-B) -> Wave-2 self-audit. No Pass 5-10 ever exercised.

## 19. Journals / TODOs / backlogs

roles/Hecate/journal/2026-09-29.md, 2026-09-30.md (restart handoffs, CWO adoption, pause points);
TODO.md ("Prior-art rule PREREG (general), apply to HT-321a8fd8e0" unchecked; mechanical ruler
WITHDRAWN); BACKLOG_H0H5.md (HECATE-14 prior-art pass, never run); WORK_STATE.json;
harvest_w2/LEDGER.md (Q1-Q32 inference ledger -- the most informative file for Phase 3);
harvest_w2/INFERENCE_SATURATION_WAVE2_HANDOFF.md.

## 20. Research reports

- roles/Hecate/REVIEW_PACKET_2026-09-30_first_cycle.txt -- first-cycle packet (pre-correction).
- hecate/meta/REPORT_v1.md -- meta-experiment v1 with v2 proposals.
- hecate/alien/REPORT_pilot.md -- alien assay Family A, correction header.
- hecate/autopsy/AUTOPSY.md -- six-cause novelty autopsy, mechanical ruler sketch.
- hecate/gravity/detector_v1.md -- detector prompt and definitions.
- roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md, RULING_REQUEST_C1_C8.md, AUDIT_W_gravity_gate.md,
  DESIGN_K_prose_detector_test.md, DESIGN_P_coverage_controlled_family.md, INV_H, INV_J, INV_N, INV_S.
- hecate/programs/PROBE_ROUND{1,2,3}_REPORT.json, PASS4_ROUND{1,2}_REPORT.json.
- roles/Hephaestus/HEPHAESTUS_2_0_GRAVITY_PILOT.md (design source, operator proposal).

## 21. Failure cases

False positives: 5/5 SIGNALs reduced to trivial or known explanations; both round-3 SIGNALs pass by
construction; signals cluster in the cheapest worlds (5/9 valid worlds < 0.05 core-min vs 0/16 above,
p 0.012 two-sided; INV_N: cheap worlds pass by degenerate construction); generators' own
"simpler_alternative" field named the Pass-4 killer in >= 2/5 (Q6) but was never built as an arm;
321a PROBING rests on a tie-breaking convention (AUDIT_Z2); Charon MI tautology (prefix-tagged kill
patterns). Over-attribution: Claude RULE on 19/30 noise.
Plausible false negatives (FN): 126/243 mechanisms never placed in any world; world selection predicted
by list position (M1-M3 0.83 vs M4+ 0.39; INV_H) not strangeness; lowest-cost selection plus
"effect present by construction" PC requirement favours mechanisms the generator already knows how to
build (autopsy C5); UNFAMILIAR unreachable by definition (C6) so any genuinely new mechanism would read
COMPOSITE; scrubber erased symbolic rules; entropy observable saturated (C3 INSTRUMENT-WEAK NULL); 4-word
world too simple for depth to matter (71b6); 8/16 verdicts rest on one probed world; alien B/C
underpowered (cannot reach NOT_SUPPORTED, INV_Z4).

## 22. Mechanism archaeology

- Mechanism = a Pass-1 record with form (14 forms, index SUMMARY), state/update/observable; reduced to a
  world spec. Decomposition by the generator, not by lesion. Causal lesions: null twin removes the
  mechanism; Pass 4 ORIG substitutes the known mechanism (a transplant test of the trivial explanation).
  Transplantability: Pass 6 cross-substrate transfer never run. Correlation-only risk: SIGNAL decided by
  thresholds on one world. Donor selection: stratified seeded sample of 16 historical triples (5 strata;
  4 random). Prior-art corpus: none. Families represented: error-correction, dynamical law, interaction
  law, learning pressure, representation, etc.; admission skewed toward error-correction/dynamical law
  (K5: skew not significant, p ~ 0.18). [IMPLEMENTATION FACT / REPORTED RESULT -- UNVERIFIED]

## 23. Novelty / prior-art audit

Definition of novelty.
- Charter: five-label prior-art scale, "Do not claim novelty without evidence", prior art AFTER
  generation. [DESIGN INTENT]
- Operational: (a) gravity detector classification -- FAMILIAR if one known mechanism "at most renamed or
  reparameterised" accounts for state, update rule and behaviour; COMPOSITE if two or three combined in a
  known way; UNFAMILIAR if no combination accounts for a central part (hecate/gravity/detector_v1.md).
  (b) Pass-4 ORIG reduction: if the trivial/known mechanism reproduces the effect, KNOWN_ANALOGUE_FOUND.
  (c) research_state.novelty field in pass records: 99 "unknown", 15 "low", never higher (computed from
  hecate/programs/HT-*/program.json). [IMPLEMENTATION FACT]

Corpora actually searched.
- NONE. pass0_3_v1.md line 29 "No search of any kind: no web, no literature"; pass3_v2, probe_impl_v1..v3,
  pass4_impl_v1..v2 all forbid search. HECATE-14 (prior-art pass) never ran (AUTOPSY Part A: "There was no
  novelty stage in this pipeline"). Of 396 hypotheses, 2 carry a prior_art label (both
  KNOWN_ANALOGUE_FOUND; evidence = Pass-4 rows, named "minimum-distance decoding" and "perturbation-
  response network inference" from model memory, no citation); DOSSIER "PRIOR ART" sections otherwise
  "_none yet_". [IMPLEMENTATION FACT]
- The only "searcher" was claude-opus-5-5 parametric memory via the gravity detector (399 meta items,
  14 controls, 62 autopsy items). No literature database, no code search, no external model family.
- Upstream: Nous's historical "novel" label (5,462/5,918 responses "novel", 4 "existing"; all 16 selected
  triples "novel" -- AUDIT_Z5) came from agents/nous/src/scorer.py assess_novelty(): substring counting
  over the generator's own self-assessment ("novel", "original", "unexplored" vs "already known"...). A
  model asked "Is this combination novel?" answered, and keywords in its answer became the label.
  Hecate dropped this field correctly (it carried no signal) but it is the clearest historical instance
  of "unfamiliar to the generator" stored as "novel". [IMPLEMENTATION FACT]

Blind spots.
- Universal formalisms: any finite rule fits "cellular automaton on a graph", "register machine",
  "semi-Thue system" -> FAMILIAR (AUTOPSY Part B). The definition makes UNFAMILIAR unreachable (C6).
- COMPOSITE absorbs everything multi-concept; gate never tested FAMILIAR vs COMPOSITE (0/2 evidence).
- Controls off-distribution (free prose vs field-formatted, masked arm items); scrubber no-op on controls.
- Same model family generates and judges; "familiar to Claude" is the measured quantity.
- No external literature means "known" claims (Pass 4) are also unverified by citation.

Effect on interpretation.
- The zero-UNFAMILIAR result was first reported as a property of the arms (d80c5cc4c), then re-read as an
  instrument result (e4a05ba3b), then as a definition property (K6). Hecate then withdrew LLM
  prior-recognition as a novelty ruler and proposed a mechanical template-reducibility ruler (AUTOPSY),
  which CWO-B withdrew before it started. Pass-4 reductions to known mechanisms (decoding radius etc.) are
  the only cases where "prior art" changed a program verdict. [LATER CORRECTION]

"Unfamiliar to Prometheus" vs "new to science".
- Hecate never claimed novelty to science; the schema refuses it without evidence and research_state
  never exceeded "low". Rule s5: never "call a low-gravity result novel". [IMPLEMENTATION FACT]
- Reverse direction (familiar-to-model treated as known-to-science): FAMILIAR at formalism level was
  read as "known"; 16/32 operationally alien systems called FAMILIAR by Claude in the assay; R1 0/32
  UNFAMILIAR. Mechanisms labelled KNOWN_ANALOGUE_FOUND without a citation. This is the dominant error
  direction in this seat: absence of an UNFAMILIAR call was briefly treated as absence of novelty
  (CWO-2026-09-30 framed it as "the novelty failure"). [LATER CORRECTION]
- Upstream Nous: unfamiliar-to-the-generator recorded as "novel" for 92% of responses. [IMPLEMENTATION FACT]

## 24. Lens inventory (descriptive)

- Control-first world generator + evaluator contract + metamorphic harness: reusable for any "does this
  toy mechanism do what it claims" lens; resolution limited by tiny worlds (signals live in near-
  deterministic cheap worlds). Reusable-grade (tests exist).
- Alien-lawful assay (100 systems with mechanical alienness certificates, matched nulls, answer key):
  the strongest instrument for "can an observer tell alien law from noise"; small n; coverage confound
  (INV_E) and DESIGN_P proposes a coverage-controlled family.
- Gravity detector: toy-grade as a novelty ruler (NOT_VALIDATED); possibly reusable as a
  "nearest-prior naming" aid if paired with a claim audit (DESIGN_K).
- Exact shadow evaluator for preregistered decision rules: reusable infrastructure.
- Charon MI-with-permutation-null: instructive negative (instrument tautology).
- Unknowns: behaviour of any of these on non-Claude subjects; mechanical novelty ruler never built.

## 25. What I did not read / open questions

Not read: individual world evaluate.py files beyond audit summaries; hecate/alien/systems.py internals;
INV_E/INV_G/INV_Z8 scripts; meta arms rows; charon daemon.py beyond commits; RULING_REQUEST full text;
Harmonia SAMPLE2-4 audits. Open: was any ruling on C1-C8 issued after 2026-10-01? Did Tyche's
dark-residual lens ever consume Artemis #1121/#1133 residuals jointly with Hecate (no Hecate artifact
found)? Would a non-Claude detector also return zero UNFAMILIAR?
