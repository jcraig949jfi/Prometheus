# HT-8a87057933 / W4 -- implementation notes (written before any code)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and round-1 PREREG.

## Spec field -> code

| spec field | code |
|---|---|
| 64 candidate automata, 6 states, 2 inputs | `make_family(seed)`: table T[m,s,a] i.i.d. uniform over 6 states, m=0..63 (spec says "random automata"; no other structure given) |
| one forbidden, one goal, shared start | shared by all 64 models: START=0, FORBIDDEN=4, GOAL=5 (labels arbitrary: tables are exchangeable) |
| true plant drawn uniformly | per episode, index drawn uniformly from 0..63; the list of true indices per seed is precomputed from `seed` and is IDENTICAL across all arms (common random numbers) |
| agent keeps the consistent set | fully observed state; after (s,a)->s' every model with T[m,s,a]!=s' is removed. Version space resets to all 64 at each episode start (new plant per episode) |
| safe actions | a is safe at s iff T[m,s,a]!=FORBIDDEN for every consistent m |
| "progress" | robust AND-OR value V(s): V(GOAL)=0, V(s)=min over safe a of 1+max_m V(T[m,s,a]) (fixed point over current version space). "Progress exists" iff V(s) finite; then the agent takes the argmin safe action (ties -> lower action index) |
| probe trigger | no safe action at s, OR V(s)=inf ("none progress") |
| allowed actions at a trigger | the safe actions if any exist, else both actions |
| limit-seeking skeleton | shared by NULL_TWIN, POSITIVE_CONTROL and (phase 2) TREATMENT: non-trigger steps use the robust argmin action |
| intervention (refutation probe) | PHASE 2 ONLY: allowed action maximising the split (entropy of the partition of the consistent set by predicted next state) |
| control (CE) | lowest-index consistent model; BFS shortest path to GOAL avoiding FORBIDDEN in that model; if none, BFS allowing FORBIDDEN; if GOAL unreachable, an action not entering FORBIDDEN in that model, else action 0. Replan every step |
| positive control ("agent given the true model") | non-trigger steps: first action of the true model's shortest FORBIDDEN-avoiding path to GOAL (fallback as CE, using the true model). Trigger steps (same trigger rule on its own version space, so bits-per-probe is defined on the same trigger rule as the null twin): oracle probe -- among allowed actions prefer those not entering FORBIDDEN in the true model, then maximise REALISED bits removed (computable because the true model is known), then true-model progress, then lower index. This is the one-step upper bound on bits per probe and on safety |
| null twin | limit-seeking skeleton; at a trigger, action uniform among allowed actions (separate rng stream) |
| cheat | NULL_TWIN rows with success injected into the observables: forbidden entries := 0, steps := CE reference steps of the same episode, bits removed per probe := 2 x null twin's |
| observable: forbidden entries | count of steps whose next state is FORBIDDEN; the episode CONTINUES from FORBIDDEN (count, not flag) |
| observable: steps to goal | steps until GOAL; episodes not reaching GOAL within 30 steps are censored at 30 |
| observable: bits per probe (L3) | per probe step: log2|V_before| - log2|V_after|; arm statistic = total bits over probe steps / number of probe steps, pooled |
| size | 10 seeds (0..9) x 1000 episodes x max 30 steps, every arm |

## Criterion as applied (pooled over all seeds x episodes; thresholds verbatim)

Success for arm X:
 (a) 1 - mean_forbidden(X)/mean_forbidden(CE) >= 0.50 (undefined -> false if CE mean is 0)
 (b) median_steps(X) <= 1.5 * median_steps(CE)
 (c) bits_per_probe(X) / bits_per_probe(NULL_TWIN) >= 1.5 (undefined -> false if X never probes)
Failure: forbidden reduction < 0.20 OR bits ratio < 1.1.
Per-seed pass fractions are reported as statistics, not used for the decision.

## Ambiguities and chosen readings

1. CE reference in the pilot. The criterion is defined relative to CE, so
   "positive control meets success" cannot be evaluated without a CE
   baseline. The pilot therefore computes CE as a REFERENCE only
   (ce_reference_rows.jsonl, not an arm under test). CE is the CONTROL arm,
   not treatment; no treatment code or statistic exists in phase 1. In
   phase 2 CE is rerun in world.py as the CONTROL arm by the same code path.
2. Null twin vs part (c). Part (c) compares an arm to the null twin; applied
   to the null twin itself the ratio is identically 1.0, so the literal
   criterion can never be met by the null twin. I apply the criterion
   literally (null_twin_meets_success uses (a)(b)(c)) and ALSO report
   null_twin_meets_a_and_b as a disclosed statistic. This makes the
   pilot's null-twin check vacuous by construction -- recorded as an
   anomaly, not hidden.
3. Null twin "identical probe triggers and count" as treatment: in the
   pilot there is no treatment; the null twin uses the identical
   deterministic trigger rule. Probe-count matching to treatment is
   reported in phase 2 (probes per episode of each arm).
4. Cheat detected := the evaluator, applying the criterion, reports the
   cheat arm as meeting success (round-1 definition: "to show the
   evaluator can see success").
5. Positive control is "given the true model" for control; for the L3
   observable it uses the true model to pick the probe with the largest
   realised refutation. If even this oracle cannot reach a 1.5x bits
   ratio over random choice among (at most) 2 actions, no one-step probe
   policy can, and the spec is unattainable on this substrate.

## Parameters (from the spec)
N_MODELS=64, N_STATES=6, N_INPUTS=2, START=0, FORBIDDEN=4, GOAL=5,
EPISODES=1000, MAX_STEPS=30, SEEDS=0..9.
rng: family = np.random.default_rng([seed, 1]); true indices =
default_rng([seed, 2]); null-twin choices = default_rng([seed, 3]).

## Log
- attempt 1: pilot as above.
- attempt 1 RESULT (PILOT_attempt1.json): pilot FAILED. Positive control
  met (a) 0.688 and (b) 1.25 but not (c): bits ratio 0.914 vs null twin.
  Cheat detected; null twin did not meet success (a=0.324).
  Diagnosis (controls only, no treatment exists): ~14-15 trigger steps per
  episode, most of them AFTER the consistent set is a singleton (true model
  has no forbidden-free path to goal, or both actions enter forbidden), so
  the agent keeps "probing" with 0 bits available. Total bits per episode
  are ~4.5 of a 6-bit cap for both arms, so bits/probe is set by how many
  dead triggers occur, not by probe choice.
- REPAIR (the one allowed, applied to the controls' probe accounting,
  symmetric for every arm, thresholds unchanged, decided with no treatment
  statistic in existence): a PROBE is a trigger step taken while the
  consistent set has more than one model (|V|>1). A trigger on a singleton
  set cannot refute anything and is not a probe; the action rule at such
  steps is unchanged (so forbidden/steps observables are unchanged). The
  same definition will bind TREATMENT in phase 2. The positive-control
  oracle ordering (true-safe first, then realised bits) is NOT changed.
- attempt 2: rerun of pilot with the repair.
- attempt 2 RESULT: pilot FAILED again (PC bits ratio 0.843). OUTCOME.json = SPEC_UNATTAINABLE. Stopped; no treatment code written.
