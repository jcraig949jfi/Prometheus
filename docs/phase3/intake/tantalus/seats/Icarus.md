# Icarus -- Phase 3 intake dossier

Seat: Icarus
Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

Summary. Icarus (agents/icarus/, 25 commits 2026-05-25..2026-08-12; seat
folder roles/Icarus/ created 2026-09-11) is an LLM-in-the-loop "self-improving
reasoner" [INTENT]. What was BUILT and RUN [IMPL]: a cycle daemon that clones
the last STABLE snapshot of a hand-seeded Python+sympy file `reasoner.py`, asks
an LLM generator (Claude API, later the Claude Code subscription CLI) for a
full-file rewrite, applies it, runs pytest plus an adversarial battery plus a
falsifier on a different model, and marks the cycle STABLE or PARKED; a
multi-lens LLM panel turns each failure into a typed JSON object
(agents/icarus/daemon.py, improve.py, lenses/, tier_oracle.py). The ruler is
Harmonia's procedurally generated reasoning ladder (harmonia/experiments/
reasoning_phase0.py) with a deterministic sympy/z3 verifier. 22 cycles ran on
the operator's M2 machine; the stable pointer reached cycle 018, which
"cleared R5" on 2026-06-10 [RESULT-UNVERIFIED] (96814789f). The organism is an
LLM writing code; the "reasoner" is a hand-dispatch program over probe kinds.
"R5" in the oracle means deciding domino tileability of an n x n board with
corners removed (a parity check) and a Harmonia audit records a 75% chance
floor and a payload-label reader scoring 100% on it [CORRECTION]
(roles/Harmonia/REVIEW_20260812_program_and_instrument_audit.md s2(c)-(d)).
Its durable residue is instrumentation: typed failure objects (8 rows), kill
clusters, a tier-calibration matrix that diagnosed its own early rungs as
"too_weak_all_pass" and "vacuous". Daemon DISABLED since 2026-06-15.

## 1. Identity, charter and pivots

- First commit 364d5a31a 2026-05-25 "Icarus Phase 0 scaffold: self-improving
  reasoning-ladder climber"; design docs pivot/icarus_design_v01/v02
  (2026-05-25), icarus_v3_design_pressure_2026-05-28.md, frontier verdict
  synthesis 05-29, whitepapers/icarus_synthetic_reasoning_v01_2026-05-27.md
  [CLAIM: cited by roles/Icarus/ARCHAEOLOGY_2026-09-11.md; not opened here].
- Pivots [IMPL] (git log): 05-25 Phase 0-2.1 (own toy tier tests, lens
  panel); 05-27 15-cycle R1->R2 run; 05-28 typed residue, debt ledger, kill
  clusters, holdout, ablation, tier calibration (e35847693, cc507ffcd);
  05-29 rewired to "climb Harmonia B's real reasoning ladder" (5e93378bd,
  04e743646) after the operator ruled the external ladder be used; 05-29
  "stop surfacing ground_truth in probe schema (cheat-vector)" (52a10049f);
  06-09/10 subscription-CLI backend and sentinel output contract; 06-10 R5
  CLEARED; 06-15 R6 wall, cycle 20 PARK; 08-12 catch-up commit of state;
  09-11 base-role adoption (d7fee8a26): 5 SUPERSEDED, 1 NEEDS_REPREMISE.
- Host: M2 (D:\Prometheus) for all cycles; cycle dirs 001-020 exist only on
  M2 (gitignored) [CLAIM] (STATUS; README layout).
- Relationships: Harmonia (ladder and verifier lens author; auditor 06-15 and
  08-12), James routes "Chimera" requests [INTENT] (README).
- Seat state 2026-09-11: BLOCKED on ICARUS-XL-1 (retire/re-premise) [CLAIM].

## 2. Engine/system inventory

Engine I1: Icarus cycle daemon.
- Paths: agents/icarus/daemon.py (28 KB), lineage.py (clone/freeze),
  improve.py (3 backends: Claude API, Chimera human relay, Ollama stub),
  patcher.py, tdd_runner.py, falsifier.py (different-model probes),
  adversarial.py (8 probes), ladder.py (frozen R0-R12 text), tier_oracle.py
  (adapter to Harmonia ladder), tier_calibration.py, ablation.py,
  robustness.py, complexity.py, debt_ledger.py, kill_clusters.py,
  taxonomy.py, wisdom.py, lenses/{_base,_llm,_panel,contract,diagnostician,
  generator,historian,integrator,skeptic}.py, tests_harness/ (caliber suite
  with fixtures contract_breaker, genuine_r1, goodhart_r1) [IMPL].
- State: agents/icarus/state/*.json (tier_target R6, tier_currently_passing
  R5, debt_ledger, kill_clusters, tier_calibration, training_stream.jsonl 8
  rows, claude_daily_cap) [IMPL].
- Mutable organism: cycles/cycle_N/code/reasoner.py + strategy.py; only
  cycle_000 is in git (2.4 KB reasoner) [IMPL].
- Deps: sympy, z3 (via Harmonia verifier), anthropic / Claude CLI,
  google.generativeai (falsifier; deprecated warning in the last log) [IMPL]
  (cycles/_last_run_020.log).
- Execution: `daemon.py --loop --interval 90`; cycle 20 took 442 s [IMPL]
  (_last_run_020.log).
- Scale: 22 cycles; tests_run 32 per cycle (training_stream rows) [IMPL].

## 3. Code architecture and dataflow

clone stable -> generator lens builds a prompt from the parent source, probe
schema, tier description, failure direction, wisdom -> LLM returns full file
in sentinel blocks -> patcher writes it -> pytest + tier_oracle battery on
held-out seeds -> falsifier (other model) -> lens panel (skeptic, historian,
integrator, diagnostician, contract) emits a typed failure object -> STABLE
(advance pointer) or PARK [IMPL] (daemon.py, lenses/generator.py,
tier_oracle.py, commit messages 2883cffd3, 96814789f).

Code-vs-doc disagreements:
- ladder.py names R5 "Counterfactual control ... Holds branches; answers
  'what changes if X changes'" [IMPL] (ladder.py TierDef R5). The ruler
  actually used since 05-29 is Harmonia's gen_R5: "invariant detection
  (parity) -- parity-DECIDABLE instances only", domino tiling of an n x n
  board, n in {4,6,8} [IMPL] (harmonia/experiments/reasoning_phase0.py:141-157).
  "R5 cleared" therefore does not mean what ladder.py's label says.
- Same for R6: ladder.py "Error detection + local repair" vs oracle R6
  "conjecture: search counterexamples" (reasoner.py docstring; tier_oracle.py
  TIER_TRACE_KEYS R6) [IMPL].
- README "Falsifier probe execution (returns inconclusive)", "Adversarial
  probes (all return passed=True until reasoner exists)" -- Phase 0 stubs; 
  11695a754 says "real Falsifier" [CLAIM]; this crawl did not verify which
  stubs remained live in cycles 13-20 [UNKNOWN].

## 4. Claimed computational primitive vs actual mechanism

- Label: "self-improving reasoning-ladder climber"; "synthetic reasoning".
- Smallest actual mechanism: LLM full-file rewrite of a Python dispatch
  function `reason(probe) -> (answer, trace)` that branches on `probe.kind`
  and `probe.version`, accepted by test pass [IMPL] (cycle_000 reasoner.py;
  generator.py). The "reasoning" is whatever the LLM writes; the loop is
  hill-climbing on a test suite with the LLM as mutation operator.
- What it could express: any Python program the LLM can write per probe kind.
- Phenomenon targeted: a ladder of reasoning capabilities (R0 paraphrase
  robustness ... R5 invariant detection ... R6 counterexample search).
- Could the organism perform it: the reasoner is a program, so "R5" is a
  parity count; Harmonia: "A four-line parity count clears the tier the
  ladder documents as an 'open frontier'" [CORRECTION] (REVIEW_20260812 s2(c)).
  The cycle-14 typed object's nearby_survivor already reads "blacks, whites =
  color_counts(board); return blacks == whites for the 'color_parity' case"
  [IMPL] (state/training_stream.jsonl row cycle 14) -- i.e. a branch keyed by
  the handed-over invariant label.
- Could the ruler tell it from a shortcut: gen_R5 puts the label in
  probe.data["invariant"] with values color_parity (False), area_parity
  (False), none (True) [IMPL] (reasoning_phase0.py:146-156). Answer =
  (invariant == "none") solves every R5 probe [CODE-INFERRED]. Commit
  96814789f surfaced exactly this enum to the generator ("Now aggregates
  DISTINCT values across all 4 versions") [IMPL]. Harmonia's audit tested a
  label-reader and a blind deriver: both 100%; ruled the leak "present but
  not load-bearing" and R5 CLEAN on its field-equality payload test
  [CORRECTION]. That audit's payload_reader checks whether a field reproduces
  ground_truth; a mapping from a label to the boolean is not a field equal to
  it, so CLEAN on that test does not exclude the label shortcut
  [CODE-INFERRED]. Whether cycle 018's reasoner read the label is UNKNOWN
  (its code lives only on M2). trace["invariant_named"] scores 1.0 for any
  truthy string and is never compared to the label [IMPL per Harmonia
  quoting the grader at reasoning_phase0.py:485].
- R6: probe payload ships `truth`; payload reader 100% -> LEAKS [CORRECTION]
  (REVIEW_20260812 s2(d)). Icarus never cleared R6.

## 5. Representation/state architecture

Organism state = source text of reasoner.py/strategy.py. Loop state =
pointer files, debt ledger, kill clusters, typed failure objects with fields
failure_class, failure_subclass, nearby_survivor, regression_test_to_write,
representation_change_hint, improvement_kind [IMPL] (training_stream.jsonl).
Only 8 typed objects exist for 22 cycles (cycles 0-12 emitted none) [CLAIM]
(ARCHAEOLOGY C11).

## 6. Organism/player architecture

One lineage, one individual per cycle; parent = last STABLE; no population,
no crossover [IMPL] (lineage.py, daemon.py). Mutation = LLM rewrite.

## 7. World/environment architecture

Probe batteries: R0-R3 algebra (linear, quadratic, sqrt with extraneous
roots, rational with excluded value), R5 domino-parity boards n in {4..10},
R6 conjecture counterexamples, R7 numbered proof steps; 4 versions each
(clean/iso/adversarial/transfer) [IMPL] (tier_oracle.py TIERS;
reasoning_phase0.py). Toy scale: boards up to 10 x 10, single-variable
algebra; chance floors measured 3.8%-75% per tier [RESULT-UNVERIFIED]
(REVIEW_20260812 table).

## 8. Search/training/adaptation mechanism

LLM proposal + test acceptance, with "failure emits direction" (the typed
object's hint fed back into the next prompt) [IMPL]. Bottlenecks recorded:
diff apply failures and syntax errors (cycles 13-14 diff_apply_failed),
serialization wall (fixed by sentinel blocks 2883cffd3), edit-interface wall
(f82cfabe1), lens source-blindness when the reasoner grew large (98f95a22d)
[IMPL commit subjects]. Doctrine extracted: "a plateau is an interface bug
until an interface audit clears it" [CLAIM] (ARCHAEOLOGY B). Every recorded
wall was an interface wall; none was a capability wall of the organism
[CODE-INFERRED from commit subjects].

## 9. Measurement/ruler stack

Pytest on own tests; tier oracle on held-out seeds; deterministic verifier
lens (sympy/z3) for linear/quadratic/sqrt/rational/conjecture, harness
grade() for invariant/proof_repair [IMPL] (tier_oracle.py:53-55). Promotion
gate parameters in ladder.py (min 5 cycles, 100 perturbation trials,
p < 0.01) [IMPL]; whether the daemon enforced them is UNKNOWN. Tier
calibration matrix 2026-05-28 over 5 versions: R0/R1 too_weak_all_pass, R2
vacuous, holdout_R1 unreached_all_fail, holdout_R2 discriminating (bootstrap
passes, later cycles fail: "bootstrap_overreach") [IMPL]
(state/tier_calibration.json). Not re-run after the switch to Harmonia's
ladder [CLAIM] (ARCHAEOLOGY C5).

## 10. Baselines and controls

Harmonia reference reasoners (template, procedural, careful, falsifier) as
staircase baselines; all four score 0 on R5 [CLAIM] (REVIEW_20260812 s2(c)).
Caliber fixtures contract_breaker / genuine_r1 / goodhart_r1 as meta-tests of
the harness [IMPL] (tests_harness/). No constant-answer control was run by
Icarus; Harmonia measured R5 constant-False = 75% [RESULT-UNVERIFIED].

## 11. Historical experiment campaigns

C-I1 Toy-tier climb R0->R2. 2026-05-25..05-27 (ec43509b2, 15 cycles).
Reported: R1->R2 movement; later calibration showed R0/R1 all-pass and R2
vacuous. Label: LATER OVERTURNED.

C-I2 Harmonia-ladder climb R3->R5. 2026-05-29..06-10 (cycles ~13-18).
Reported: R5 CLEARED cycle 18, delta +1 (96814789f). Later: Harmonia 08-12
"real capability relative to four reference baselines" but chance floor 75%
and a four-line parity check suffices; label-leak present. Label: MIXED.

C-I3 R6 attempt. 2026-06-15 cycles 19-20; cycle 20 PARK tdd_failed (596edeb0d).
Later: R6 payload leaks truth (REVIEW_20260812). Label: INCONCLUSIVE
(abandoned; ruler later shown to leak).

C-I4 Tier calibration / holdout / ablation. 2026-05-28 (cc507ffcd). Reported:
matrix above. Label: REPORTED NEGATIVE/NULL (on the ruler).

## 12. Reported results and later corrections

- "R1->R2 climb" -> tier calibration -> rungs too weak/vacuous -> switch to
  external ladder [CORRECTION] (tier_calibration.json; 5e93378bd).
- "ground_truth surfaced in probe schema" -> removed as cheat vector
  (52a10049f) [CORRECTION].
- "R5 CLEARED" -> Harmonia attack: leak present, not load-bearing; chance
  floor 75%; no baseline exercised the tier [CORRECTION]. Current status:
  a measured pass on a parity-decision task with a label in the payload.
- Atlas digest records "R5 not broken; leak scoped to one tier"
  (roles/Atlas/inference_harvest_2026-09-30/workers/digests/
  harmonia_rulers_and_satellites.md:89). This crawl agrees R5 is not leaky
  by field-equality, and disagrees that the ruler can distinguish label
  dispatch from derivation [CODE-INFERRED].

## 13. False-positive archaeology

- Toy tiers that every version passed (R0/R1) read as rungs.
- R5: a 75%-floor boolean task with the decisive invariant named in the
  payload; the generator was explicitly shown the enum.
- trace credit for "invariant_named" given to any truthy string.
- "Reasoning (the parity argument) was always left to the generator" (commit
  96814789f) -- the generator is an LLM that knows the mutilated-chessboard
  argument; the capability observed is the LLM's, not the loop's
  [CODE-INFERRED].

## 14. Likely false-negative regimes

R6/R7 walls were interface/contract walls (cid-family surfacing, answer
contract); parking at cycle 20 says little about capability. 22 cycles is
tiny. The lens panel itself was blind to oversized sources (98f95a22d).

## 15. Phase 3 audit (engine I1)

a. Representation richness (of the organism = Python program): hierarchy
   PARTIAL (functions call strategy.py primitives); compositional structure
   PARTIAL (e72c492bb nudged reuse of strategy.py); variable binding YES
   (Python); memory NO (stateless per probe); recurrence NO; counterfactual
   state NO (ladder's R5 label claims it, the task does not require it);
   latent variables NO; temporal abstraction NO; spatial abstraction PARTIAL
   (board colouring); reusable substructure PARTIAL (strategy.py);
   dynamic routing YES but hand-coded (dispatch on probe.kind); self-reference
   NO (the loop edits the program, the program does not edit itself).
b. Reasoning opportunity: tasks are single-step decisions or textbook
   algebra; R5 is a lookup on a payload label or a parity count. Nothing
   requires more than fixed heuristics per probe kind.
c. Shortcut surface: payload labels (R5), payload truth (R6), any-truthy
   trace keys, constant answers near the chance floor, LLM prior knowledge
   of textbook problems.
d. Ruler resolving power: low at R5 (75% floor, binary answer, 160 probes);
   deterministic and fail-closed for algebra tiers.
e. Scale: 1 lineage, 22 cycles, ~32 tests per cycle, probes 160 per tier per
   audit; boards <= 10 x 10; ~7 minutes per cycle.

## 16. Research reports and substantial documents

- agents/icarus/README.md -- architecture; annotated HISTORICAL 2026-09-11.
- roles/Icarus/ARCHAEOLOGY_2026-09-11.md -- queue classified, frame vs north
  star.
- roles/Icarus/calibration/CALIBRATION.md -- 8 rows.
- agents/icarus/wisdom/kill_clusters.md -- 3 clusters, 6 failures.
- roles/Harmonia/REVIEW_20260812_program_and_instrument_audit.md s2 -- ladder
  leakage audit incl. R5/R6.
- roles/Harmonia/RESUME_20260615_icarus_ladder.md [cited, not read].

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Icarus/journal/2026-09-11.md; BACKLOG_H0H5.md (24 rows, 3 XL;
ICARUS-01 copy M2 cycle dirs; ICARUS-XL-1 retire vs re-premise); open debts
3 in state/debt_ledger.json. Abandoned: Q1 typed operator DAG, Q20 kill
criterion (200 R5 cycles), seeded-primitive diagnostic, Ollama backend.

## 18. Dependencies on other engines and seats

Harmonia (ladder generator reasoning_phase0.py, verifier_lens.py, audits);
Claude API/CLI; Gemini (falsifier); James as Chimera relay [IMPL/INTENT].

## 19. Scaling limitations

One LLM call chain per cycle (~7 min), daily token cap 200k (README), single
lineage, M2-only residue. Ladder generators exist only for R0-R3, R5-R7
[IMPL] (tier_oracle.py TIERS comment).

## 20. Lens potential for Phase 3 (descriptive)

Substrate: Python source edited by an LLM. Organism: one program lineage.
World: procedurally generated toy reasoning probes. Pressure: test pass.
Phenomenon family: tiered reasoning capability. Resolving mechanism:
deterministic verifier + per-tier chance floors (post 08-12). Ceiling: the
LLM's prior knowledge of the task families. Reusable: typed failure-object
schema, kill clusters, tier-calibration matrix (rungs every version passes),
harness caliber fixtures (genuine vs goodhart vs contract breaker). Toy
grade: tiers, boards, single lineage. Unknowns: cycle 001-020 code (M2 only).

## 21. Open questions / coverage gaps

Read: README, STATUS, ARCHAEOLOGY sections A-C11, ladder.py, tier_oracle.py
head, cycle_000 reasoner.py, tier_calibration.json, training_stream row 13-14
heads, _last_run_020.log, git log, commit 96814789f, gen_R5 in Harmonia,
Harmonia REVIEW_20260812 s2(c)-(d). Not read: daemon.py, improve.py,
falsifier.py and lens bodies; tests_harness; whitepaper and pivot design
docs; Harmonia RESUME 06-15; CALIBRATION.md; journal; BACKLOG. Cycle dirs
001-020 are not in the tree (M2 only) -- the decisive R5 reasoner was not
inspectable.
