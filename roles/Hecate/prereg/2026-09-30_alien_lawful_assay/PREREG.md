# PREREG -- Alien-lawful structure assay, pilot (100 systems)

Frozen: 2026-09-30Z, in the same commit as the dataset, answer key,
baselines and all scoring code, BEFORE any pilot system was shown to any
model. Author: Hecate[m1-dd0c3882]. Directive (verbatim):
roles/Hecate/prompts/2026-09-30_alien_lawful_assay/.

## 0. What was seen before freezing (declared)

- Non-LLM baselines on the pilot (hecate/alien/data/BASELINES.json).
- A shakedown on a DIFFERENT dataset (seed 7, not committed, scratchpad):
  Claude 10 calls (all task types), Gemini 3, gpt-oss up to 3. It exposed
  and led to fixing: a pair-tally double count, a bootstrap crash on empty
  groups, and recall credit for a descriptive (non-planted) property.
  Anecdote seen: Claude called both shakedown noise systems RULE/COHERENT.
  Nothing in the pilot was changed after the shakedown.
- Generator robustness: seed 4242 failed to generate one graph alien in
  400 draws; the pilot seed 20260930 is unaffected (recorded for expansion).

## 1. Ground truth and definitions (operational; no LLM involved)

Every system is a deterministic map on a finite, fully enumerated state
space (961..4096 states). Classes (hidden):
- KNOWN_LAWFUL (20): named mechanisms re-expressed in neutral notation
  (counter, shift register with feedback, compare-exchange ordering,
  median smoothing; diffusion, shortest-distance relaxation, plurality
  vote, threshold contagion; ordering, pair cancellation, bracket
  cancellation, drift rewriting; counter, Fibonacci, multiply-accumulate,
  arithmetic swap programs; rotation, cat map, integer predator-prey,
  two-phase synchronisation).
- ALIEN_LAWFUL (40): random compact rules drawn with a structural bias,
  KEPT ONLY IF the planted property verifies on EVERY state and the
  mechanical analogue check passes (not affine; < 0.5 agreement with every
  known template of the same family on the same state space; not
  near-identity; not near-constant). Alienness is operational: generator
  lineage (arbitrary tables/polynomials) + analogue check; family-level
  construction class recorded honestly (e.g. "Feistel-type" shears).
  32 standard + 8 ADVERSARIAL (lawful rule seen through a random
  invertible linear change of coordinates, or a long-cycle program).
- MATCHED_NOISE (40), each matched to one alien of the same family:
  CONJ 7 (relabelled: identical orbit structure, no compact law),
  DSCRAMBLE 11 (increment-scrambled: matched change-rate/step size),
  SCRAMBLE 4 (input-scrambled; for aliens whose planted property is
  orbit-structural), DESTROY 10 (same generator, planting constraint
  removed: a COMPACT rule without the planted property), SEDUCTIVE 8
  (small random per-state increments; matched to the 8 adversarial aliens).
  Every null is KEPT ONLY IF the matched alien's primary planted property
  FAILS on it (exhaustive).
- "Noise" for the PRIMARY lawful-vs-noise analyses = the 30 INCOMPRESSIBLE
  nulls (CONJ, DSCRAMBLE, SCRAMBLE, SEDUCTIVE). DESTROY nulls are compact
  deterministic rules, i.e. lawful in the ordinary sense; they are reported
  separately and never pooled into "noise".

Dataset: hecate/alien/data/public.json sha256 e5638500...e93e9;
answer_key.json sha256 711ea369...8f4f (LF). IDs SYS-xxxxx; subjects see
only public.json content (header, 8 runs x 10 steps, 12 T2 queries,
4 interventions). tests: hecate/tests/test_alien_generation.py (controls:
the analogue check rejects a known template and an affine map; property
checks fire both ways; every alien verifies and every null destroys it;
answers match the simulator; public.json leaks no class words).

## 2. Baselines (already run; they bound what "hard" means)

Component accuracy of next state on 100 held-out states, group means:
local-lookup program search A .632, K .655, incompressible nulls .24-.39,
ADV .288. Cue AUCs vs incompressible noise: compression .605 (A) / .665 (K),
recurrence .607 / .587 -- superficial cues are weak. The adversarial set is
at noise level for the local learner (designed). Map and graph families
are hard for every baseline.

## 3. Subjects

Family A: claude-opus-5-5 via isolated `claude -p` (no tools, no project
context; harness differs from raw API -- declared). Family B:
gemini-3.6-flash (Google, free tier). Family C: openai/gpt-oss-120b via
Groq (OpenAI open weights, free tier). Temperature 0 for B and C;
unavailable for A. Model id and UTC recorded per call.
Tasks per family: A: blind (100), fam (100), reveal (30), active (20),
pair (40), prose (30). B and C: blind (100) and pair (40); fam (100) if
free-tier quota allows (declared secondary). Retries: transport errors
only; one form-only re-ask on unparseable output; content never retried.

## 4. Scoring (hecate/alien/score.py + analyze.py; frozen)

- T1 score = confidence if RULE, 1-confidence if RANDOM, 0.5 if UNCERTAIN.
- T2: exact and component accuracy on 12 unseen query states.
  Trivial bar per system = max(identity, nearest-neighbour) component
  accuracy on the same queries (from observations only).
- T3: intervention accuracy (clamp; link removal for graph).
- T4: every claim evaluated EXHAUSTIVELY on the full state space ->
  TRUE / FALSE / TRIVIAL (constant quantity, identity symmetry, k<=1) /
  UNTESTABLE (prose, unparseable, crashing). Precision = TRUE/(TRUE+FALSE).
  Planted recall = fraction of primary planted properties captured by a
  TRUE claim (a conserved/advancing quantity whose value determines the
  planted quantity on every state; one_predecessor for bijective; settles
  for all-orbits-fixed; symmetry for commutes-with-swap).
- T5: subject step(s) run in a sandbox on 200 held-out states (exact,
  component), description length (chars, comments/blank lines removed),
  intervention accuracy under the clamp interventions.
- LEARNED(system) := (T2 comp >= bar + 0.15 AND T2 exact >= 0.25) OR
  T5 held-out exact >= 0.5. Behavioural score = max(T2 comp - bar,
  T5 comp - eval bar).
- T6 analogy class: NO_ANALOGY (none or confidence < 0.3); CORRECT_ANALOGY
  (analogy code exact >= 0.9); USEFUL_PARTIAL_ANALOGY (analogy code comp >=
  eval bar + 0.2); FALSE_COLLAPSE_TO_FAMILIAR (confidence >= 0.6 and
  claimed EXACT or PARTIAL, but neither of the above); else
  SUPERFICIAL_ANALOGY.
- T9: pair accuracy, reported for incompressible pairs (30) and DESTROY
  pairs (10) separately.

## 5. Metrics reported separately (never one score)

Per group (K, A, ADV, each null type): lawful-vs-noise discrimination
(AUC of T1 score and of behavioural score), T2/T3/T5 accuracy, invariant
precision and planted recall, executable-model generalisation and length,
false familiar-collapse rate, false incoherence/noise rate, benefit from
active experimentation, benefit from revealed rule; confusion matrices of
T1 verdict, coherence and familiarity labels against class (behavioural
outputs, not truth); pair accuracy; prose vs tuple T2 (secondary).

## 6. Hypotheses and decision rules (bootstrap 2000, seed 20260930)

Decisions: SUPPORTED if estimate >= threshold AND 95% CI lower > 0;
NOT_SUPPORTED if estimate <= 0 AND CI upper < threshold/2; else
INDETERMINATE; NOT_ELIGIBLE if a group is empty.
H1   AUC(K vs incomp noise) - AUC(A vs incomp noise) >= 0.10, on the T1
     score (H1_t1) and on the behavioural score (H1_behav).
H2   false-noise/incoherence rate (T1 RANDOM or coherence INCOHERENT)
     A - K >= 0.15; also reported within family (complexity control).
H3   active experimentation: on the active subset (10 A, 4 K, 6 noise),
     (K-A learned-rate gap passive) - (gap active) >= 0.10 -> SUPPORTED,
     else INDETERMINATE. Underpowered by design; descriptive primarily.
     The active arm has a matched information budget (2 runs + up to 10
     experiments of <= 6 steps vs 8 runs of 10 steps).
H4   revealed rule: (A-K false-noise/incoherence gap blind) - (gap with
     rule revealed) >= 0.10 on the reveal subset (15 A, 10 K, 5 DESTROY).
H5   FALSE_COLLAPSE_TO_FAMILIAR rate A - K >= 0.15.
H6   >= 2 aliens that are LEARNED yet verbally judged RANDOM (T1) or
     INCOHERENT (T6) -> SUPPORTED (dissociation). A softer list including
     UNCERTAIN / UNCLEAR is reported beside it.

## 7. Critical control: detector validation

NOVELTY_DETECTOR_VALIDATED iff T1 AUC(A vs incompressible noise) >= 0.80
with bootstrap CI lower >= 0.65 AND incompressible pair accuracy >= 0.80.
Otherwise NOVELTY_DETECTOR_NOT_VALIDATED, and no Hecate result may use
that model's classification to conclude "no unfamiliar mechanisms were
generated". Meta v1 rows are NOT reinterpreted.

## 8. Reading guide (descriptive, not a verdict machine)

Outcome A: detector validated. B: blind discrimination weak (AUC < 0.70)
but reveal coherence >= 0.9 on A and reveal T2 exact >= 0.75, or active
restores learning. C: behavioural A within 0.10 of K but verbal false
noise/incoherence or false collapse elevated (H2 or H5 SUPPORTED, or H6).
D: behavioural and verbal both worse on A than K by >= 0.15. E: baselines
and all models near noise level on a group -> "too hard", not LLM-specific
(ADV and the map/graph families are candidates; stated in advance).

## 9. Failure taxonomy (every alien miss; rules in analyze.taxonomy)

Primary tag in priority: PREDICTIVE_WITHOUT_EXPLANATION (learned but
verbally negative), FALSE_FAMILIAR_COLLAPSE, FALSE_NOISE, FALSE_INCOHERENT,
EXPLANATORY_WITHOUT_PREDICTION (planted property captured, not learned),
PARTIAL_STRUCTURE, RIGHT_STRUCTURE_WRONG_MECHANISM, NO_STRUCTURE_DETECTED;
secondary tags RECOVERED_AFTER_EXPERIMENTATION, RECOVERED_AFTER_RULE_REVEAL.

## 10. Order and budget

Family A all tasks, then B, then C (directive steps 8-9); score only
with the frozen code (step 10); read qualitative explanations only after
scoring (step 11). No compute to speak of; model calls are subscription /
free tier. Deviations are recorded beside results, never silently fixed.

## 11. Phase 2 (Visual Cortex) and 3 (chimera): prepared, not run

After scoring, export unlabeled matched K / ALIEN / NOISE trajectory sets
(hecate/alien/visual/) with the property-to-channel mapping; a human's
calls are scored against the same hidden key.
