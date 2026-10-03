# Nemesis -- forensic dossier (Tityos Phase 3, signal-vs-hallucination lane)

Crawler: Tityos worker g5_adversarial, 2026-10-01. Worktree F:/Prometheus-worktrees/tityos-phase3 at
36ffe8073 (origin/main lineage 5c98f59f1). Read-only. All searches excluded **/*holdout*/** and
**/nestor_secrets/**. No holdout or secret path was opened.

Epistemic labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].
Where I re-measured something myself from a committed blob I say "(re-measured here)"; that is still a
reading of a committed artifact, not a re-run of the science.

---------------------------------------------------------------------------------------------------
## 0. Summary

Nemesis had two lives.

Nemesis 1.0 (2026-03-25 .. 2026-04-02, agents/nemesis/) was a pure-algorithmic "adversarial co-evolution
engine" aimed at the March forge pipeline: it mutated seed reasoning traps with 12 regex metamorphic
relations (MRs), placed mutated tasks in a 10x10 MAP-Elites grid (logical complexity x linguistic
obfuscation), ran every Hephaestus-forged "ReasoningTool" on them, shrank failures, and fed per-tool
survival to Coeus (dual causal graph) and RLVF weighting [IMPLEMENTATION FACT: agents/nemesis/src/*.py,
1c4e1a38d..fbb92a11a; agents/coeus/src/coeus.py:112-160]. Its attacks were never themselves validated:
no fixture showed a SAME-expected MR preserves ground truth or a FLIP-expected MR inverts it; two MRs
hard-code the answer "Not enough information", producing a 62/92 majority class on which a constant
string beats almost every tool; the blind-spot detector (all tools wrong) could essentially never fire
over a ~150-294 tool library; and the ground-truth validator was itself one of the evaluated tools
(execution_evaluator) -- the attacker shared code with its target. 97.3% of 3,013 cycles placed nothing
while writing a report every cycle. Its README headline ("Goodhart table") is not reconstructable from
any committed row [LATER CORRECTION: roles/Nemesis/ARCHAEOLOGY_2026-09-11.md; engine/ledger/
AGENT_AUTOPSIES.jsonl (Aporia P69, 2026-08-21)].

Nemesis 2.0 (re-seated 2026-09-11, roles/Nemesis/) inverted the lane into "construct the input an
instrument cannot survive": cheat controls (constant / majority / payload-reader responders), mechanical
forgeries, chance floors, shrinking to a minimal crossing fraud. It shipped one small, self-tested library
(roles/Nemesis/science/cheatlib.py, 12 self-controls), one preregistered attack (NEMESIS-01 on the Eos
intake gate, with positive controls that fired, and two of its own generator defects caught and
preserved), a re-attack after repair (NEMESIS-01c), a second opinion on Eos's refusal corpus
(NEMESIS-01b: 49/51 refusals determined by one constructor defect), and a hand-read "chance floor census"
of 53 tier-1 instruments (NEM-14: 12 of 37 scoring instruments publish a chance floor). All of it is one
day's work (2026-09-11); NEMESIS-02 (attack Harmonia's conformance_check.py) was selected and never run;
a later assignment to PLANT blind fixtures for Archaeon Campaign 6 (2026-09-18) has no delivery on record.
Strength: 2.0's machinery is methodologically the best adversarial practice in my territory but has a
sample size of one target. 1.0's machinery was cosmetic as a measurement instrument.

---------------------------------------------------------------------------------------------------
## 1. Charter and role evolution

- Canonical name Nemesis; no aliases found. Pipeline position (March): NOUS -> COEUS -> HEPHAESTUS ->
  NEMESIS -> COEUS [DESIGN INTENT: agents/nemesis/README.md "Pipeline Position"].
- Original charter (2026-03-25, 1c4e1a38d, cb534552c): "Are our evaluators measuring reasoning, or have
  they learned to pass tests?" Three questions: what breaks, what is invisible (blind spots), are we
  Goodharting [DESIGN INTENT: agents/nemesis/README.md].
- Build history: v1 1c4e1a38d (03-25); Phase 2b dual graph / lineage / per-tool difficulty fbb92a11a;
  Phase 3-4 RLVF fitness + provenance gate 2a186ba24; "Batch 4: 63/100 Nemesis grid" 45f225f51; hardening
  923d11c66; last real touch b674a9976 (04-03); incidental ba34f1ca4 (04-08, a Charon commit)
  [IMPLEMENTATION FACT: git log -- agents/nemesis].
- Runtime: first log line 2026-03-25 11:22:35, last 2026-04-02 12:44:13 "Shutdown requested"
  [HISTORICAL CLAIM: ARCHAEOLOGY s1, from untracked agents/nemesis/nemesis.log -- not in git, not read by me].
- Dormant 162 days. Autopsied externally 2026-08-21 by Aporia P69 (engine/ledger/AGENT_AUTOPSIES.jsonl
  line for agent_id Nemesis: failure_class BOUNDED-MENU-SATURATION + STRUCTURAL-ZERO-DETECTOR)
  [HISTORICAL CLAIM].
- Re-seated 2026-09-11 (a95d67ed8) under the base role, with operator hard rule "NO INSTRUMENT EARNS TRUST
  MERELY BECAUSE IT REJECTS NEGATIVES. NEMESIS MUST ATTEMPT TO MAKE IT ACCEPT A FRAUD."
  [DESIGN INTENT: roles/Nemesis/RESPONSIBILITIES.md s0]. Worktree D:\Prometheus-worktrees\nemesis-adopt,
  host not stated beyond that path [HISTORICAL CLAIM: roles/Nemesis/STATUS.md].
- Same day: NEMESIS-01 prereg 73e6f46c1 -> finding 72bf820ab -> 01b b973987a8 -> NEM-14 prereg 0548bde84
  -> census 385049114 -> 01c c17267a41 [IMPLEMENTATION FACT: git log].
- 2026-09-18: Archaeon Campaign 6 asks Nemesis to PLANT blind fixtures with a sealed registry; operator
  ruling R1-R9 "Harmonia and Nemesis may author fixtures" (roles/Archaeon/prompts/2026-09-18_campaign6/
  01_CAMPAIGN_6_OPENING_ASKS.md:27, 04_OPERATOR_RULINGS_R1-R9.md:63-67) [DESIGN INTENT]. No Nemesis commit
  after 2026-09-11 found via `git log --all --grep` [UNKNOWN / AMBIGUOUS: delivery not on record].
- Terminal state: ACTIVE per STATUS (09-11) but no activity after 09-11; April loop registered DEAD in
  roles/base-role/MONITORS.md [HISTORICAL CLAIM].
- Relations: consumed Hephaestus forge (agents/hephaestus/forge/, 734 files, frozen since 04-03); fed Coeus
  and RLVF; 2.0 boundaries vs Kairos (claims), Harmonia (qualification), Charon (rulings), Elenchus
  (passes), Nyx (organs) [DESIGN INTENT: RESPONSIBILITIES s3]. Commissioned by Eos (EOS-30, C4).
- Atlas: no mention of Nemesis in atlas/ or roles/Atlas/ (git grep, exclusions applied) -- Atlas is silent
  on this seat [IMPLEMENTATION FACT].

---------------------------------------------------------------------------------------------------
## 2. Code / system architecture

Nemesis 1.0 -- agents/nemesis/src (1,859 lines) [IMPLEMENTATION FACT]:
- nemesis.py (413): cycle loop; seeds from Hephaestus test_harness SEED_TRAPS + trap_generator
  generate_trap_battery (lines 57-83); three generators: random (50), targeted to empty cells (30),
  boundary per tool (20); --runonce, --poll-interval 120, --seed.
- metamorphic.py (502): 12 MRs as regex rewrites with expected "same|flip|computed"; compose_mrs,
  random_mr_chain, targeted_mr_chain (20 random chains, keep closest).
- map_elites.py (353): 10x10 grid, cell keeps max-"disagreement" task; NCD novelty threshold 0.15.
- evaluator.py (135): loads every *.py in forge dir exposing ReasoningTool; disagreement =
  (#distinct non-error answers)/(#tools) (NOT the variance the README describes); blind_spot = all tools
  wrong; overconfident = conf_wrong > 0.7.
- validators.py (76): structural checks + "question detected" + cross-check by
  agents/hephaestus/forge/execution_evaluator.py, rejecting a task when that evaluator confidently
  disagrees with the stated answer.
- shrink.py (124): 7 regex simplifications, max 5 rounds, keep if tool still fails.
- reporter.py (256): per-cycle markdown + adversarial_results.jsonl + targeted_forge_requests.jsonl.
- Persistence: grid/grid.json, adversarial/adversarial_results.jsonl (92 records, 294 tools, 12,713
  evaluations; tracked although .gitignore:170 names it), untracked nemesis.log (101,126 lines) and
  reports/ (3,014 files) [HISTORICAL CLAIM for untracked counts].
- Consumers: agents/coeus/src/coeus.py:112-160 load_adversarial_results / compute_adversarial_survival
  (splits tool name on "_x_" into concepts and averages "correct") [IMPLEMENTATION FACT];
  agents/hephaestus/src/reasoning_episode.py:114 training_gate [IMPLEMENTATION FACT exists; never tested per
  ARCHAEOLOGY NEM-A6].

Nemesis 2.0 -- roles/Nemesis/science [IMPLEMENTATION FACT]:
- cheatlib.py: Responder interface; DegenerateConstant, MajorityClass, PayloadReader; chance_floor
  (uniform + majority floor); score_responder; forgeries borrow_real_path, token_from_file, filler,
  absent_marker; shrink (greedy to fixpoint, max_steps guard). tests/test_cheatlib.py: 12 tests in
  NEGATIVE / POSITIVE / CHEAT groups, incl. a pinned firing fixture on the April ledger.
- attacks/2026-09-11_eos_intake_gate/attack.py, refusal_audit.py; attacks/2026-09-11_eos_gate_repaired/
  reattack.py. Executes agents/eos/src/intake.py classify path; never edits it.
- census/floor_census.py (screen; _forbid_filesystem() raises if membership is taken from disk rather than
  the git index) + classify.py (hand-read classification recorded as a dict, 53 rows).
- Scale: one host, seconds-scale runs; no GPU, no model in any path.

---------------------------------------------------------------------------------------------------
## 3. Inputs and outputs

1.0 inputs: forged tools (agents/hephaestus/forge/*.py), seed traps (hephaestus test_harness /
trap_generator). Outputs: grid.json, adversarial_results.jsonl, targeted_forge_requests.jsonl (never
populated: blind_spots=0 always), per-cycle reports [IMPLEMENTATION FACT / HISTORICAL CLAIM].
2.0 inputs: a target instrument's real scoring path + git index; the April ledger as a fixture. Outputs:
rows.jsonl (271 verdicts), results*.json, FINDING*.md, classification.json (53), census_screen.json,
reports via comms to Eos/Harmonia [IMPLEMENTATION FACT: roles/Nemesis/attacks/**, science/census/**].

---------------------------------------------------------------------------------------------------
## 4. Claim class it was meant to police

1.0: "this evaluator tool measures reasoning rather than trap-pattern-matching" (Goodhart on static
batteries) [DESIGN INTENT]. 2.0: "this instrument's number/state is produced for the reason it names" --
specifically acceptance boundaries of gates and the presence of chance floors beside headline numbers
[DESIGN INTENT: RESPONSIBILITIES s1-s2].

---------------------------------------------------------------------------------------------------
## 5. Measurement methodology

1.0: metamorphic testing without an oracle in principle, but in practice the MR code COMPUTES the new
"correct" answer itself (flip: Yes<->No; computed: hard-coded "Not enough information"), so the task's
ground truth is generator output, not an independent oracle [IMPLEMENTATION FACT: metamorphic.py
_negation_inject 75-110, _conditional_weaken 268-286, _affirm_consequent 289-300]. Accuracy = top-ranked
candidate == stated correct. Survival rate per tool/concept = mean correct.
2.0: construct an incapable population, run it through the target's real path, report crossing rate with
eligible count and positive controls (POP-NULL must be refused; POP-B_POS genuine markers must be refused),
shrink the cheapest crossing member; preregister predictions in their own commit before code
[IMPLEMENTATION FACT: 73e6f46c1 precedes 72bf820ab; PREREGISTRATION.md].
NEM-14: screen by keyword over git index, then hand-read classification F0-F3 x KIND
(CHANCE/CHANNEL/RELEVANCE/ANALYTIC/WITHDRAWN/NONE) [IMPLEMENTATION FACT: classify.py docstring].

---------------------------------------------------------------------------------------------------
## 6. Null / control generation

1.0: none for the instrument itself. No constant/majority responder, no shuffled-label null, no random
grid partition. The "Goodhart gap" compared a static column with no committed source to adversarial
survival [LATER CORRECTION: ARCHAEOLOGY s4].
2.0: cheatlib responders are the nulls -- DegenerateConstant, MajorityClass (the population's majority
answer), PayloadReader (answer read from a carried field); chance_floor computes uniform and majority
floors from the population (not from summary statistics, after L-05) [IMPLEMENTATION FACT].
Forgery nulls for gates: random absent marker (zero hits by construction), 1-char token from a real
file, 20 filler chars [IMPLEMENTATION FACT].

## 7. Positive controls

1.0: none found. No planted "known-broken tool" to show the grid/blind-spot detector can fire
[IMPLEMENTATION FACT: no fixture in agents/nemesis].
2.0: POP-NULL (0/30 crossed) and POP-B_POS (0/3 crossed) show the Eos gate CAN refuse; cheatlib
test_positive_shrink_reaches_the_known_minimum (caught the first shrink under-reducing 28 vs 5);
test_positive_payload_reader_ties_the_answer_when_the_leak_is_real; test_positive_majority_class_finds
_the_real_imbalance [IMPLEMENTATION FACT: tests/test_cheatlib.py; REPORTED RESULT -- UNVERIFIED for the
attack counts; I did not re-run].
assert_builder_built_something: proves the adversary populated the fields before execution -- added after
run 2 reported 0.00 from a builder that emitted empty claims [HISTORICAL CLAIM: FINDING.md "My own
instrument failed twice"].

## 8. Negative controls

2.0: test_negative_constant_responder_scores_near_zero_on_a_flat_population; test_negative_chance_floor
_reports_the_flat_case_honestly; test_negative_payload_reader_returns_none_when_there_is_no_leak; shrink
refuses a non-crossing candidate; chance_floor refuses empty population [IMPLEMENTATION FACT].
1.0: validators reject structurally broken tasks; that is input hygiene, not a negative control on the
measurement.

## 9. Neutral / intermediate controls

none found as a designed class. NEMESIS-01c effectively uses a "repaired-instrument" re-run as an
intermediate comparison (same seed 20260911, same construction) [IMPLEMENTATION FACT: FINDING_REPAIRED.md].

---------------------------------------------------------------------------------------------------
## 10. Qualification criteria / gates / thresholds

1.0: NCD novelty < 0.15 rejects; grid cell keeps max disagreement; overconfident if conf_wrong > 0.7;
lineage depth > 2 flagged [IMPLEMENTATION FACT / DESIGN INTENT].
2.0: verdict vocabulary DEATH CERTIFICATE / BOUNDED STATEMENT / ATTACK FAILED, with preconditions
(positive control must hold for any kill); P1/P3 crossing >= 0.90; P6 enumerable >= 10,000 members.
NEM-14 states F0..F3 + NA. Nemesis "proposes, does not adjudicate" [DESIGN INTENT: PREREGISTRATION.md,
RESPONSIBILITIES s4.8].

## 11. Statistical methods

Counting and rates only. No confidence intervals on crossing rates; POP-B n=8 (each member a 19 s git grep);
one seed (20260911) for all attacks [REPORTED RESULT -- UNVERIFIED; FINDING.md and FINDING_REPAIRED.md say
so themselves]. NEM-14 is a hand-read census, not a statistical estimate. 1.0 used NCD (compression
distance) for novelty and simple means.

---------------------------------------------------------------------------------------------------
## 12. Independence assumptions

- 1.0 ATTACKER SHARED CODE WITH TARGET: the ground-truth cross-check is
  agents/hephaestus/forge/execution_evaluator.py (validators.py:17-24), which is also one of the 294
  evaluated tools in the ledger (re-measured here: present, accuracy 0.37 over 92 tasks, rank 210 by
  own-denominator accuracy). Tasks on which execution_evaluator confidently disagreed with the generated
  answer were DROPPED before evaluation, so admission was filtered by a member of the population under
  test [IMPLEMENTATION FACT + CODE-INFERRED CAPABILITY for the selection effect's direction].
- 1.0 SHARED DATA: seeds came from the same Hephaestus test_harness / trap_generator that defined the
  forge's own static battery (nemesis.py:57-83) -- "adversarial" tasks are mutations of the training-like
  distribution, so "static vs adversarial" was not two independent populations [IMPLEMENTATION FACT].
- 1.0 SHARED AUTHORSHIP: one author for forge, traps, Nemesis and Coeus (all commits "James Craig" in the
  March batch commits) [IMPLEMENTATION FACT: git log author field; the role-level "seat" authorship is not
  recoverable for March].
- 2.0: target executed, never reimplemented (independent of target's internals); but predictions were
  written after reading intake.py in full -- declared "informed, not blind" [HISTORICAL CLAIM:
  PREREGISTRATION.md]. Nemesis declares itself conflicted on its own April corpus and on inherited MRs
  (CALIBRATION "Standing conflicts"). ARCHAEOLOGY is self-assessment; the only independent read of 1.0 is
  Aporia P69 (engine/ledger/AGENT_AUTOPSIES.jsonl), which reached a different but compatible diagnosis
  (blind-spot detector cannot fire at library scale; grid saturation) without the constant-responder
  analysis [HISTORICAL CLAIM].
- NEM-14 classification is a single hand-read by the attacker seat; no second rater [IMPLEMENTATION FACT].

## 13. Provenance tracking

Wins: preregistration commits precede attack commits (73e6f46c1 -> 72bf820ab; 0548bde84 -> 385049114)
[IMPLEMENTATION FACT]. Run-1 defect rows preserved (results_run1_generator_defect.json,
rows_run1_generator_defect.jsonl) [IMPLEMENTATION FACT]. floor_census._forbid_filesystem() makes the
census take membership from the git index; Nemesis measured 376 instrument-shaped modules in the index vs
40 on disk in its sparse worktree, i.e. a filesystem auditor would have reported 89.4% absent
[REPORTED RESULT -- UNVERIFIED]. Discovered that Eos capability_absent grepped the working tree (43 vs 97
files) [REPORTED RESULT -- UNVERIFIED; Eos later switched to --cached per FINDING_REPAIRED.md].
Provenance-tag invariant: all output "provenance: adversarial", training_gate() raises ValueError --
code exists, never exercised by a test [HISTORICAL CLAIM: ARCHAEOLOGY NEM-A6].
Failures: README Goodhart table had no committed rows for 162 days (L-02); the tool carrying the central
claim (info_theory_x_criticality_x_pragmatics) is absent from the ledger [LATER CORRECTION]. nemesis.log and
3,014 reports never committed.

## 14. Known defects

1.0 [LATER CORRECTION: ARCHAEOLOGY s2-s4, CALIBRATION L-01..L-04; AGENT_AUTOPSIES Nemesis]:
- Label imbalance by construction: 62/92 tasks answer "Not enough information" (two MRs hard-code it);
  constant responder 0.674.
- 88/294 tools are constant responders; 74 of those return the majority string.
- blind_spot detector requires ALL tools wrong; structurally near-impossible over 150-294 tools; fired 0 of
  3,013 cycles.
- "disagreement" spans 0.0127..0.0410 across 92 cells -- no gradient to maximise.
- confidence_correct == confidence_wrong on 15.1% of evaluations.
- 97.3% no-op cycles with a report per cycle.
- README describes disagreement as variance; code computes distinct-answers/n_tools [IMPLEMENTATION FACT].
- Validator shares code with the target (s12).
NEW, found in this crawl (re-measured here from the committed ledger blob):
- DENOMINATOR CHOICE IN THE 2.0 FIRING FIXTURE. Only 122 of the 294 tools were evaluated on all 92 tasks;
  58 tools appear on exactly one task. test_cheat_the_april_tool_population_mostly_loses_to_the_constant
  (tests/test_cheatlib.py:130-143) computes each tool's accuracy as correct/92, counting a missing
  evaluation as wrong. Under that convention 292/294 are at or below 0.674 (reproduced). Under
  own-denominator accuracy, 100 of 294 exceed 0.674 (mostly tools with 1-9 evaluations). Restricted to the
  122 full-coverage tools, 120 are at or below the floor and 2 exceed it (0.728). The qualitative finding
  survives on the full-coverage subset; the "292 of 294" headline and the "mean accuracy 0.175" are partly
  a missing-as-wrong artifact [LATER CORRECTION / CONTRADICTION, raised here; not previously recorded that I
  found].
2.0: shrink under-reduced (fixed to fixpoint); generator run 1 falsifier 19 chars; run 2 dropped
referent line -> 0.00 masquerading as a strong gate [HISTORICAL CLAIM, self-reported, fixed].

## 15. Historical audits performed

By Nemesis: NEMESIS-01 (Eos intake gate), NEMESIS-01b (Eos refusal corpus second opinion, commissioned as
EOS-30), NEMESIS-01c (repaired gate, Eos C4), NEM-14 (floor census of 53 tier-1 instruments), self-audit
ARCHAEOLOGY_2026-09-11.md. Selected not run: NEMESIS-02 on roles/Harmonia/contracts/conformance_check.py.
On Nemesis: Aporia P69 autopsy 2026-08-21 (engine/ledger/AGENT_AUTOPSIES.jsonl); Nemesis self-archaeology.
No independent re-check of 2.0's findings found (ARCHAEOLOGY invites one) [UNKNOWN / AMBIGUOUS].

## 16. Historical findings (outcome labels on the record)

- 1.0 "Goodhart gap: ibai_v2 67->46, efme_v2 60->51, info_theory... 47->85 (+38)" -- LATER OVERTURNED
  (not reconstructable; ledger 0.283 / 0.543 / absent).
- 1.0 "blind_spots = 0" (no reasoning region uncovered) -- INSTRUMENT FAILURE (detector could not fire).
- 1.0 grid 63/100 (03-25, 45f225f51) -> 92/100 -- REPORTED POSITIVE as coverage; reclassified as
  uncalibrated decoration (RESPONSIBILITIES s4.4).
- 1.0 per-concept adversarial survival -> Coeus dual graph -> Goodhart demotions -- CONTAMINATED (inputs
  dominated by majority-class artifact; Coeus scores later called a "forge-calendar fingerprint",
  ARCHAEOLOGY NEM-A7) [HISTORICAL CLAIM].
- NEMESIS-01: RESOURCE path crossed 30/30 on a self-asserted observed_by string; ANCHOR 200/200; ACQUIRE
  8/8; positive controls 0/30, 0/3 -- REPORTED POSITIVE (BOUNDED STATEMENT + scoped DEATH CERTIFICATE).
- NEMESIS-01b: 49/51 Eos refusals decided by a missing referent path derived from the item id --
  REPORTED POSITIVE (instrument-error finding about Eos's constructor).
- NEMESIS-01c: RESOURCE 30/30 -> 0/30 after repair; ANCHOR unchanged 200/200 -- MIXED (repair works on
  RESOURCE; ANCHOR hole explicitly unrepaired). Eos fired its own precommitment: KEEP_DARK (54a1f97cc).
- NEM-14: 12/37 scoring instruments have a CHANCE floor; Q1 LOST, Q2 LOST, Q3 HELD -- REPORTED RESULT,
  MIXED vs predictions.

## 17. Later corrections (timelines)

1. Goodhart table: claim 03-25 (README) -> no challenge for 162 days -> 09-11 measured against ledger ->
   RETRACTED, README annotated in place -> status: not reconstructable, failed closed.
2. Blind-spot null: 3,013 zero readings 03-25..04-02 -> Aporia P69 08-21 "STRUCTURAL-ZERO-DETECTOR" ->
   Nemesis L-03 09-11 -> status: PARKED until shown able to fire.
3. Eos RESOURCE terminal: Eos design (self-settled) -> NEMESIS-01 30/30 forged settle -> falsifier tested
   (upstream authentication of observed_by) did not fire -> Eos repair (reads committed probe artifact) ->
   01c 0/30 -> status: repaired, one seed, ANCHOR open (EOS-31).
4. 292/294 headline: 09-11 pinned in test -> (this crawl) denominator convention identified -> status:
   holds on 122 full-coverage tools (120/122), overstated on the full 294.

## 18. Pivots

Pipeline adversary for forged reasoning tools (March) -> dormant -> cheat-control supplier aimed at
INSTRUMENTS, program-wide on commission (proposed NEM-XL-1, operator decision outstanding)
-> fixture author for Archaeon C6 (assigned 09-18; undelivered on record).

## 19. Journals / TODOs / backlogs

- roles/Nemesis/journal/2026-09-11.md, 2026-09-11_NEMESIS-01.md, 2026-09-11_NEM-14.md: order of work,
  self-caught defects.
- roles/Nemesis/BACKLOG_H0H5.md: NEM-01..18 + NEM-XL-1..4. Notable open: NEM-04 re-validate the 12 MRs
  (never done), NEM-16 do grid axes separate instruments better than random partition (never done),
  NEM-17 the 15.1% equal-confidence rows, NEM-18 automatic constant-responder detection. XL decisions:
  program-wide mandate, consent vs notification, disposition of 3,014 reports, dead lineage as fixture.
- roles/Nemesis/CALIBRATION.md: L-01..L-08 wrong calls, incl. two lost preregistered predictions.

## 20. Research reports

- agents/nemesis/README.md -- 1.0 design + retracted table (annotated head).
- roles/Nemesis/ARCHAEOLOGY_2026-09-11.md -- self-autopsy of 1.0.
- roles/Nemesis/attacks/2026-09-11_eos_intake_gate/FINDING.md, SECOND_OPINION_EOS30.md, PREREGISTRATION.md.
- roles/Nemesis/attacks/2026-09-11_eos_gate_repaired/FINDING_REPAIRED.md.
- roles/Nemesis/science/census/ATTACK_SURFACE.md + PREREGISTRATION_NEM14.md.
- roles/Nemesis/prompts/*/REPORT_TO_EOS*.md, REPORT_TO_HARMONIA.md.

## 21. Failure cases

False positives / cosmetic: README Goodhart table (unreconstructable); grid coverage as progress; per-tool
"survival" fed to selection while a constant beat 120/122 full-coverage tools.
False negatives (plausible, FN):
- blind_spot=0 forever: a reasoning region nobody handles would have read as "none" (detector cannot fire).
- Validator filtering by execution_evaluator: tasks that would expose execution_evaluator-style errors
  were removed before evaluation -> under-reports failures of that tool family.
- NEMESIS-01 run 2: a broken builder produced 0.00 crossing -- would have certified the Eos gate as
  strong had assert_builder_built_something not been added (caught by self, same day).
- NEM-14: an F3 row means a floor is published, not that it is correct; no floor was attacked; tier-1 only
  (~14% of instrument-shaped modules); legacy agents/ excluded -> census can miss floorless instruments.
- MR flip logic (Yes<->No) applied to non-binary answers: cases silently dropped by the validator
  (correct not in candidates), so negation coverage of multi-choice items is unknown.

## 22. Mechanism archaeology -- n/a (seat attacks instruments, not mechanisms).

## 23. Novelty / prior-art audit -- n/a. (1.0 "novelty" = NCD between task strings for grid admission, not
scientific novelty.)

## 24. Lens inventory

- cheatlib (2.0): a reusable acceptance-boundary probe for any gate or scorer with a callable path;
  resolution = can show a gate accepts frauds and compute floors; ceiling = cannot test ABOUTNESS,
  only existence/format predicates, and depends on the attacker imagining the cheat. Small, tested,
  toy-to-moderate grade; reusable.
- Metamorphic relation table (1.0): concept reusable, code UNVERIFIED (regex, English-template-specific,
  answers computed by the generator).
- Shrinker (both): reusable, cheap, produces minimal failing handles.
- NEM-14 census rubric (F0-F3 x KIND): reusable audit vocabulary; hand-read, single rater.
- MAP-Elites over (complexity, obfuscation): axes never validated; toy-grade as a measurement.

## 25. What I did not read / open questions

Not read: map_elites.py, reporter.py, shrink.py bodies (only signatures/README); attack.py,
refusal_audit.py, reattack.py bodies; rows.jsonl content; census_screen.json; Eos's side
(agents/eos/src/intake.py) beyond what FINDING quotes; grid/grid.json. Untracked nemesis.log and reports/
are not in git and were not opened. Did not re-run any test or attack.
Open: Did Nemesis plant the Campaign-6 blind fixtures (no commit found)? Was NEMESIS-02 ever run? Where did
the README "static accuracy" column come from? Did the RLVF fitness weighting ever ship weights derived
from this ledger into a training/selection run?
