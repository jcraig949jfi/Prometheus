# HT-5b0b3ebb8d / W4 -- implementation notes (written before any run)

Implementer prompt: hecate/programs/_prompts/probe_impl_v1.md
(sha256 cf4bd374bce1b817a12d3607063278183ce0a8b7c4a7b771061dc8ce133bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec read: program.json experiment W4, mechanisms M11 and M13, lenses L6 and L2.

## World (spec "size": 16-state true structure, 2 redundant goal mechanisms,
## 80 training traces of length 20, 30 reachability formulas, 60 seeds)

States 0..15. Start state 0, goal state 15.
- Mechanism A: chain 0 -> 1 -> 2 -> 3 -> 15.
- Mechanism B: chain 0 -> 4 -> 5 -> 6 -> 15. Interior states of A and B are
  disjoint, so the two chains are "disjoint paths making EF goal true".
  Interior states have exactly one out-edge (the next chain state); the only
  edges into the goal are the two chain exits, so EF goal from 0 is supported
  by exactly A and B (redundant).
- Background states 7..14: ring 0 -> 7 -> 8 -> ... -> 14 -> 0, plus one extra
  random edge per background state (to a random state in {0, 7..14}, not self,
  not duplicate) and one extra random edge from 0 into the background.
- Goal reset 15 -> 0 (so traces do not stall in an absorbing goal).
- Transition probabilities: per state, Dirichlet(1) weights over its out-edges
  (drawn per seed). Chain edges out of interior states have probability 1.
Traces: 80 random walks from state 0, each of 20 transitions (21 states).
These choices are mine (the spec gives only the sizes); they were fixed here
before any run and are not tuned afterwards.

## Agent model and abductive completion (mechanism field; M11)

Agent model = observed transitions (every consecutive pair in traces) UNION
abduced transitions. Abduction rule (my reading of "abductive completion of
unobserved transitions"): reversibility abduction -- for every observed s->t
whose reverse t->s was never observed, the agent abduces t->s ("the best
explanation of passage s->t is a corridor"). Some abduced edges are real
(the world has t->s), others are fabricated. This is the single simplest
abduction rule I could state without adding structure the spec does not
mention. It is an invented detail, and I flag it as such; the spec does not
name any other rule.

M13 (skeptic-believer game) is listed in mechanism_ids but W4's mechanism
field only needs model-checked beliefs; no skeptic search is implemented.
"Verified" = the formula is true in the agent's (single) learned model. L2
(knows-frontier) is not used by W4's observable.

## Formulas, beliefs, witnesses, grounding (L6)

- 30 reachability formulas per seed: "s |= EF t", with (s, t) drawn uniformly
  without replacement from ordered pairs s != t of the 16 states.
- A belief = a formula true in the TRUE pre-shift world AND true in the
  agent model (spec: "true, model-checked beliefs"). Only beliefs are analysed.
- Witness path: BFS shortest path from s to t in the agent model, neighbours
  expanded in increasing state index (deterministic tie-break).
- Grounded (my reading of "the path appears in traces"): the witness state
  sequence occurs as a CONTIGUOUS subsequence of at least one observed trace.
  Otherwise lucky. (Literal reading of M11 "certificate never realized in
  observed traces". Consequence: a witness made only of observed edges that
  were never traversed consecutively is still lucky.)
- Visit covariate: mean visit count (occurrences in all 80 traces) over the
  states on the witness path, s and t included.
- Visit deciles: pooled over all beliefs of the arm across seeds; edges =
  np.quantile(values, [0.1..0.9]); decile = np.searchsorted(edges, v,
  side="right") (ties may merge deciles).

## Intervention (mechanism shift)

Per seed, one of A or B is chosen at random (rng) and its four chain edges
are removed from the true world. The agent model is not updated.
Observable: a belief FAILS iff s |= EF t is false in the shifted world.

## Arms (60 seeds each, seeds 0..59, rng = default_rng(1000 + seed))

- TREATMENT: lucky flag from the witness grounding audit.
- CONTROL: spec "beliefs grouped by visit-count deciles, ignoring grounding".
  Same beliefs as TREATMENT; its reported statistic is the failure rate per
  visit decile and the crude (unstratified) lucky-vs-grounded odds ratio,
  i.e. what one sees from visit counts alone / without stratification. It is
  descriptive and does not enter the outcome class.
- NULL_TWIN: same beliefs and failures as TREATMENT; the lucky flags are
  permuted WITHIN each pooled visit decile (across seeds), rng
  default_rng(777). Same lucky rate, same visit distribution per stratum,
  grounding information destroyed.
- POSITIVE_CONTROL: same world/traces/shift as TREATMENT plus 5 planted
  cases per seed: a background source s (distinct, from 7..14) and a target
  t drawn from the interior states of the mechanism that will be disabled;
  a fabricated edge s -> t is added to the agent model and formula s |= EF t
  is added to the formula set. In the true world s reaches t only via the
  disabled chain (interior states are entered only from the chain), so the
  disabled mechanism is the only real support. The pipeline (BFS witness,
  grounding audit, shift) is run unchanged.
  Detected iff >= 90% of planted beliefs are flagged lucky by the audit AND
  the failure rate of flagged planted beliefs is >= 0.9 (spec threshold).
- CHEAT: same beliefs as TREATMENT; failure overwritten to 1 for lucky and 0
  for grounded (bypasses the mechanism). Detected iff it meets the success
  criterion.

## Criteria (thresholds unchanged)

- Statistic: Mantel-Haenszel common odds ratio of failure (lucky vs grounded)
  stratified by visit decile, pooled over 60 seeds x 30 formulas; p from the
  Cochran-Mantel-Haenszel chi-square (1 df) WITH the 0.5 continuity
  correction (classic form). Strata lacking either lucky or grounded beliefs
  contribute nothing. Two-sided p.
- Success: OR_MH >= 1.5 AND p < 0.01.
- Failure criterion: OR_MH < 1.2 OR p > 0.1. The zone between is "not
  success"; per PREREG, "treatment fails the criterion" -> NULL (if controls
  detected). Whether failure_criterion itself is met is reported.
- If OR_MH is undefined (zero denominator), success is False.
- Outcome decided in code: CONFOUNDED if NULL_TWIN meets success; else
  INSTRUMENT_FAIL if positive or cheat not detected; else SIGNAL if
  TREATMENT meets success; else NULL. (Order: PREREG says CONFOUNDED when the
  null twin also meets success; INSTRUMENT_FAIL means no reading of treatment
  is made. If controls fail AND null twin meets success I report
  INSTRUMENT_FAIL, since no reading is made; order therefore:
  INSTRUMENT_FAIL, CONFOUNDED, SIGNAL, NULL.)

## Prespecified diagnostics (not used for the outcome)

- Stupid explanation 1 (lucky beliefs concentrate on the disabled mechanism):
  fraction of lucky and of grounded beliefs whose witness touches an interior
  state of the disabled mechanism.
- Stupid explanation 2 (shortest-path witnesses use abduced edges): fraction
  of lucky witnesses that use at least one abduced (unobserved) edge, and
  fraction that use a fabricated edge (same for grounded). Only one witness
  rule is run, so this is described, not controlled.
- Planted pair that coincides with a regular formula: the planted one
  replaces it (marked planted) so the formula count stays 30 + 5 distinct.
- Stupid explanation 3 (strata too coarse): MH OR and p with 20 pooled
  quantile strata of the same covariate.

## Compute

Expected << 1 core-minute. Measured with time.process_time in world.py and
evaluate.py and recorded in OUTCOME.json.

## Post-run record (attempt 1, no rerun, nothing tuned)

One run of world.py + evaluate.py; outcome SIGNAL by code (OR_MH 1.580,
p 1.8e-4; null twin OR 0.998; cheat and positive control detected);
0.02 core-minutes. A descriptive check made after the run (appended to
OUTCOME.json anomalies, outcome unchanged): failure is fully determined by
whether s or t lies in the disabled mechanism's interior, and such beliefs
are lucky more often (0.77 vs 0.62). Stupid explanation 1 is therefore live
and must be tested first in Pass 4 (e.g. stratify by endpoint location).
