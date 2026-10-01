# HT-5b0b3ebb8d / W4 -- Pass 4 (first falsification) notes, written BEFORE any run

Implementer prompt: hecate/programs/_prompts/pass4_impl_v1.md
(sha256 77ff9e2d04f990b18d049dcf86bf70e10246b171cb4445cc8b34bebbcecece6e),
{TID}=HT-5b0b3ebb8d, {W}=W4.
Bound by roles/Hecate/prereg/2026-09-30_pass4_round1/PREREG.md (section
"HT-5b0b3ebb8d W4") and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: those two PREREGs, the round-1 W4 directory (IMPLEMENTATION_NOTES.md,
world.py, evaluate.py, OUTCOME.json, rows.jsonl), program.json experiment W4
and M11, M13, L6, L2. Nothing else.

Thresholds (fixed by PREREG, not changed): MH OR >= 1.5 AND p < 0.01;
positive-control rate 0.9 (round-1 spec).

## Shared machinery (reused, not re-implemented)

attack.py imports the round-1 `world.py` (run_seed, build_world,
sample_traces, reachable, bfs_path, contiguous_in, chain_edges, PARAMS) and
evaluate.py imports the round-1 `evaluate.py` (cmh, strata). Importing has
no side effects (both have __main__ guards); nothing in the round-1
directory is written. So the world, abduction rule (reverse-of-observed),
witness rule (BFS shortest, lowest index), grounding (contiguous in some
trace), visit covariate (mean visits over witness states), deciles (pooled
per arm, np.quantile + searchsorted right) and the CMH statistic (0.5
continuity correction, strata lacking lucky or grounded skipped, two-sided
chi2 1 df) are byte-identical to round 1.

## R (replication)

- 60 fresh seeds 100..159. round-1 rng = default_rng(seed_base + seed) with
  seed_base 1000, so R uses rng 1100..1159, disjoint from round 1's
  1000..1059. All other parameters are round-1 PARAMS unchanged.
- Arms per seed: TREATMENT, POSITIVE_CONTROL (5 planted cases, as round 1),
  CHEAT (fail := lucky), NULL_TWIN (lucky flags permuted within pooled visit
  decile across seeds, default_rng(777), exactly the round-1 procedure).
  CONTROL (descriptive only in round 1) is not rerun.
- Reproduced iff TREATMENT MH OR >= 1.5 AND p < 0.01 (visit-decile strata),
  AND the null twin does not meet that (round-1 SIGNAL requires it), with
  positive and cheat controls detected (round-1 rules: >= 90% of planted
  beliefs flagged lucky and flagged-planted failure rate >= 0.9; cheat meets
  success).

## ORIG (re-analysis stratified by endpoint-in-disabled-region x visit decile)

- endpoint_in_disabled = 1 iff s or t is an interior state of the disabled
  mechanism for that seed (A: 1,2,3; B: 4,5,6). Computed from the row's
  `disabled` field and the belief's s, t.
- Strata: (endpoint_in_disabled, visit decile), deciles pooled over the arm
  as in round 1 (the decile is computed first on all beliefs, then crossed
  with the endpoint flag -> up to 20 strata).
- Ambiguity: which rows? "re-analysis" reads as the existing round-1
  TREATMENT rows. Reading chosen: PRIMARY = round-1 rows (seeds 0..59);
  ORIG.fired is decided on them. The same analysis is also run on the R
  rows (seeds 100..159) and reported; a disagreement is recorded as an
  anomaly, it does not change the primary.
- Kill (fires) iff ANY of: (a) no stratum has outcome variance (every
  stratum has fail all-0 or all-1); (b) stratified MH OR < 1.5, where an
  undefined OR (0/0) counts as not >= 1.5; (c) p >= 0.01, where undefined p
  counts as >= 0.01.
- ORIG control (analysis-level, since ORIG is not a new world): the CHEAT
  rows (fail := lucky) under the same stratification must show outcome
  variance in some stratum and meet OR >= 1.5, p < 0.01 -- i.e. the
  re-analysis can see a signal when one is there.

## ALT (transition-removal world)

PREREG: "a shift that removes TRANSITIONS on paths (not states at
endpoints), so failure is not decided by endpoint location: a belief fails
iff a transition on its supporting path is removed. Pass iff MH OR (lucky
vs grounded) >= 1.5, p < 0.01, stratified by visit decile AND path length,
over 60 seeds, with a null twin that removes transitions uniformly at
random from the same count."

ALT requires a new world, because in the round-1 world each mechanism
interior state has exactly one in-edge and one out-edge (both chain edges),
so removing the chain's transitions isolates those states and ANY
supporting path touching them loses a transition -- failure would again be
decided by endpoint location. What changed, and only this:

- Interior states 1..6 each get ONE extra out-edge to a background state
  (uniform over 7..14) and ONE extra in-edge from a background state
  (uniform over background states lacking that edge). Draws come from
  the per-seed rng after build_world's draws. Out-probabilities of interior
  states are then Dirichlet(1) over their two out-edges (drawn per seed).
  Everything else of round-1 build_world is unchanged (mechanism chains
  A: 0-1-2-3-15, B: 0-4-5-6-15, background ring 0,7..14 with one extra
  random edge each and one from 0, goal reset 15->0, Dirichlet(1)). The
  goal is still entered only by the two chain exits, so the two mechanisms
  remain the two redundant supports of EF goal.
  Implementation: call round-1 build_world(rng) for the base world, then,
  for i = 1..6 in order: extra out-edge i -> uniform choice over 7..14;
  extra in-edge b -> i with b uniform over the background states that do
  not already have an edge to i. The in-edges change background states'
  out-lists, so after all edges are added, Dirichlet(1) weights are
  redrawn (in state order) for every state whose out-list changed.
- Traces, abduction, formulas, witnesses, grounding, visit covariate: as
  round 1 (80 traces x 20, reverse abduction, 30 formulas drawn from
  ordered pairs, BFS witness, contiguous grounding).
- Shift (TREATMENT): one of A or B chosen at random (rng.random() < 0.5 ->
  A, as round 1); its four chain transitions are removed. States are NOT
  removed; interior states keep their extra in/out edges.
- Supporting path (ambiguity; reading chosen): the belief's witness in the
  agent model can contain fabricated transitions that do not exist in the
  world and so cannot be "removed". The path that actually makes the belief
  TRUE is a path in the true pre-shift world. Reading: supporting path =
  BFS shortest path from s to t in the TRUE pre-shift world, neighbours in
  increasing index (the same deterministic rule the agent uses for its
  witness). fail = 1 iff any transition of the supporting path is in the
  removed set. Path length (for stratification) = number of transitions of
  the supporting path. Also recorded, NOT used for the predicate:
  reach_fail (s |= EF t false after the shift), witness_hit (witness uses a
  removed real transition), witness length, endpoint_in_mech_interior.
- NULL_TWIN: same world, traces, beliefs, lucky flags; the shift removes 4
  transitions (the same count as the treatment) drawn uniformly without
  replacement from ALL true transitions, rng default_rng(900000 + seed).
  fail computed by the same supporting-path rule.
- Strata: (visit decile, supporting-path length); decile pooled per arm as
  round 1. Strata lacking lucky or grounded beliefs contribute nothing
  (round-1 cmh).
- Seeds 200..259 (rng default_rng(1000 + seed) = 1200..1259), disjoint from
  round 1 and from R.
- POSITIVE_CONTROL: 5 planted cases per seed: candidate (s, t), s != t,
  (s, t) not a true transition, whose supporting path contains a transition
  of the disabled mechanism; 5 drawn without replacement (fewer if fewer
  exist; count recorded). A fabricated edge s->t is added to the agent
  model and the formula added (replacing a coinciding regular formula), the
  pipeline run unchanged. Detected iff >= 90% of planted beliefs flagged
  lucky AND flagged-planted fail rate >= 0.9 (round-1 rule).
- CHEAT: TREATMENT beliefs with fail := lucky; detected iff it meets the
  ALT criterion (OR >= 1.5, p < 0.01 under the ALT strata).
- ALT status (computed only after all controls are detected):
  NOT_ELIGIBLE iff the treatment OR or p is undefined (no stratum with
  both lucky and grounded beliefs and nonzero variance); PASS iff treatment
  OR >= 1.5 AND p < 0.01 AND the null twin does NOT meet that criterion
  (reading of "with a null twin": the round-1 rule that a null twin meeting
  success means CONFOUNDED, which counts as not passing); else FAIL.

## Predicate (computed in code)

- controls_ok = R positive & cheat detected AND ALT positive & cheat
  detected AND ORIG cheat control detected. One repair allowed before any
  treatment statistic is printed (PREREG); if still not ok -> PARK.
- ALT FAIL or NOT_ELIGIBLE -> PARK.
- ALT PASS: if R reproduced and ORIG did not fire -> SURVIVES; otherwise
  (ORIG fired, or R did not reproduce, which also removes the original-world
  claim) -> ORIG_FOSSIL_ALT_PASS.

## Seeds / compute

R 100..159, ALT 200..259, null-twin rngs 777 (R) and 900000+seed (ALT).
Expected well under 1 core-minute (round 1 took 0.02). Measured with
time.process_time and recorded.

## Post-run record (attempt 1, no rerun, nothing tuned)

One run of attack.py + evaluate.py, 0.037 core-minutes. All controls
detected (R and ALT planted 300/300 flagged, fail 1.0; all cheats detected).
R reproduced (OR 2.06, p 2.2e-9; null twin OR 1.08). ORIG fired on round-1
rows (0/20 strata with outcome variance; also on R rows). ALT FAIL
(OR 0.44, p 6.5e-5, i.e. lucky beliefs fail LESS once supporting-path
length is stratified; null twin OR 1.11, p 0.65). Predicate PARK (by code).
Descriptive anomalies appended to PASS4_OUTCOME.json after the run.
