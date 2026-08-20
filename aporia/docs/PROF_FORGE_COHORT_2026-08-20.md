# PROF-FORGE-COHORT first light: the forged tools are surface-feature machines — and the adapter has a bias to fix
Date: 2026-08-20 (Aporia P27) | Instrument: harmonia/experiments/prof_forge_cohort.py |
Data: harmonia/experiments/prof_forge_cohort_results.jsonl (48 rows) | Consumer: germline
fitness instrument (3b/3c) + Hephaestus forge QC + adapter v2 design

## What ran
Stratified sample: 48 of 1,957 forged ReasoningTool dirs (every 40th, sorted). Phase A:
import + determinism + timing, process-isolated, 90s cap. Phase B: 20-probe answer-selection
battery (R0 x8 from reasoning_phase0; R4a/b/c x4 each from reasoning_r4), MC adapter:
candidates = [truth, surface_answer?, distractors from truth+3i], tool picks argmax
evaluate() score.

## Pre-stated readings (committed in worklog P27 before the run)
A-import: IMPORT-CLEAN >=95% / DEGRADED / BROKEN. A-det: DET-CLEAN >=90% / DET-MIXED
50-90% / DET-BROKEN. B: ADAPTER-FLOOR (vacuous, pre-committed) / TOOLS-DISCRIMINATE
(acc IQR >= 0.15 or structured surface spread) / TOOLS-FLAT.

## Results
- Import 46/48 (95.8%) -> IMPORT-CLEAN, at the boundary. The 2 failures are SyntaxError
  (walrus/comparison slips) — genuinely broken forge output, a forge-QC datapoint.
- Determinism 35/46 verified TRUE, 6 FALSE, 5 errored on the determinism call ->
  DET-MIXED (76%). Unseeded noise terms (e.g. sigma-perturbations) are in the population.
- Accuracy: median 0.10, IQR [0.05, 0.30], min 0.05, max 0.75 (chance = 0.25).
- Surface-trap capture (R4 probes carrying a precomputed surface_answer):
  iso 65/123 = 53%, adversarial 52/123 = 42%, clean 31/123 = 25% — vs 25% chance.
- R4 transfer (huge structurally-distinctive truths): 6/123 = 5% — far BELOW chance.
- Top tools: Abductive_Reasoning---Adaptive_Control---Pragmatics 0.75 (nondeterministic),
  Category_Theory---Metacognition---Criticality 0.50 (deterministic).

## Reading: TOOLS-DISCRIMINATE-WITH-ADAPTER-BIAS — partly OUTSIDE the pre-stated set, said plainly
TOOLS-DISCRIMINATE fires as pre-stated (IQR 0.25 >= 0.15; a 0.75 tool exists,
P(>=15/20 | chance) ~ 1e-6, surviving 46-way multiple testing). But the below-chance
MEDIAN (0.10 << 0.25) was not among the pre-stated outcomes and is an ADAPTER ARTIFACT,
not a tool property: distractors were derived FROM truth (truth + 3i) while truth is
structurally distinctive (R4b/R4 transfer truths have hundreds of digits; surface answers
are short). A scorer keyed to surface features (string similarity to prompt, brevity,
compressibility) systematically AVOIDS the true answer under this construction. The
control-selection lesson (a control drawn from the treatment's relation IS the treatment)
applied to MC design: distractors must be EXCHANGEABLE with truth — same generative
family, same digit-length distribution — or absolute accuracy means nothing.

What survives the bias, because it does not depend on truth's distinctiveness:
1. SPREAD is real — the instrument separates tools (that is what a fitness instrument
   needs; absolute calibration comes with adapter v2).
2. SURFACE-TRAP CAPTURE at ~2x chance on iso/adversarial R4 is the phase0 kill-pattern
   `stayed_in_surface` detected at cohort level: most forged tools score by surface/string
   features. As a population profile this is coherent with their construction (regex
   proposition extraction, NCD compression, consistency potentials over text).
3. Forge QC: ~4% syntax-broken, ~24% not-verified-deterministic.

## NOT claimed
- No claim that any tool "reasons at tier X": absolute accuracies are bias-contaminated,
  and the top tool is nondeterministic (a rerun varies). No per-tier rungs are assigned.
- No claim about the other 1,909 tools beyond the stratified sample.

## Next (adapter v2, queued as the thread's continuation)
Exchangeable distractors: draw from the probe generator's own family (other instances'
truths at matched magnitude/base/length), re-run the same sample, THEN the pre-registered
question is whether the 0.75/0.50 tools survive and whether surface-capture persists at
2x chance under a construction where surface answers have no length advantage.

## Trace-vector record
problem_id: PROF-FORGE-COHORT | tier_probe: first-light MC battery | answer_correct: n/a (instrument)
domain_constraints_detected: [distractor-truth-nonexchangeability, surface-feature-scoring-population, unseeded-noise-nondeterminism, forge-syntax-defects]
operations_used: [pre-stated-readings, process-isolation, determinism-repeat-check, per-tier-decomposition, bias-direction-diagnosis]
kill_pattern: below-chance-median = adapter self-report (candidate construction leaked truth-shape) | repair_available: exchangeable-distractor v2, specified above
residue: MC adapters obey the control-selection doctrine — distractors ARE controls; draw them from the same generative relation as truth or the instrument measures the construction, not the subject

---

# Adapter v2 addendum (P28, same day): the first light was the instrument photographing itself

v2 construction: distractors drawn from the generator's own truth pool at matched string
length (exchangeable with truth); surface answers accompanied by a LENGTH-MATCHED
surface-like control distractor (5 candidates where surface exists, 4 otherwise; mixed
chance ~0.22). Same 48-tool sample. Pre-registered Q1/Q2/Q3 in worklog P28 before the run.

## Verdicts
- Q3 CONFIRMED: median acc 0.10 -> 0.25 (~chance). v1's below-chance median was the
  truth+3i construction, as diagnosed.
- Q1 COLLAPSE for the 0.75 tool (Abductive_Reasoning---Adaptive_Control---Pragmatics:
  0.75 -> 0.15, BELOW median — its v1 score was adapter artifact + nondeterminism).
  Category_Theory---Metacognition---Criticality 0.50 -> 0.45: above the IQR, outside the
  strict top decile (tie-sensitive cutoff) — between the pre-registered buckets; reported
  as attenuated, not forced into either.
- Q2 LENGTH-ARTIFACT: R4 clean/iso/adv pooled (n=369): surface 33.1% vs surface-like
  control 27.6% vs chance 20%. The surface-over-control edge is ~1.6 sd — not the >=2x
  bar. What IS real: a generic short-string preference (both rates ~8 points above
  chance). "Stayed-in-surface reasoning" is NOT established for this population.
- Beyond the pre-registration (flagged as post-hoc): v2 accuracy spread (IQR 0.10) is
  consistent with binomial noise at n=20; the v2 max (0.50) is not significant across 46
  tools (expected count of >=0.50 under pure chance ~ 0.3). Full verdict:
  TOOLS-FLAT-AT-CHANCE — v1's TOOLS-DISCRIMINATE reading is retracted; the spread was
  construction artifact.

## What survives all rounds
1. Forge QC numbers (import 95.8%, determinism 76%, ~4% syntax-broken) — measured, stable.
2. The population profiles as surface-feature machines with a short-string preference and
   NO detectable probe-solving capability on R0+R4 answer selection.
3. The fitness-instrument implication: answer-selection MC over forged tools yields a FLAT
   fitness landscape. The foundry (3c) cannot select on this signal. Either bind tools at
   their native interface (scoring free-form claims for consistency — a different
   instrument) or accept that this population contains no ladder-relevant variation.
4. Method residue, twice-paid-for: an MC adapter's distractors ARE controls (exchangeable
   or the instrument measures its construction), and a "discriminating" first light is
   instrument calibration, not architecture measurement, until the exchangeable version
   confirms it.

## Prior-reachability note (THESIS v4 section 7 discipline)
The v1 TOOLS-DISCRIMINATE claim was exactly what my prior wanted (a fitness instrument
needs spread). The correction did not come from introspection; it came from executing the
exchangeable construction against my own preferred reading. Filed as a live instance of
"contamination is the null hypothesis," caught by the constitutional rule's mechanism
(execution certifying a consequence).
