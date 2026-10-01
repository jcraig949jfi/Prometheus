# HT-71b65251aa / W3 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...ea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Sources read: PREREG, program.json experiment W3, mechanism M2, lenses L5, L2.

## World (mechanism field)

- Lexicon: 4 predicates forming two scalar pairs, "some" style and "all" style:
  SOME_A, ALL_A, SOME_B, ALL_B, with ALL_X entailing SOME_X (literal semantics).
- Object: a level on each scale in {none, some-not-all, all}. Features:
  SOME_X true iff level >= some; ALL_X true iff level == all. 3x3 = 9 types;
  the (none, none) type is excluded (no true utterance), leaving 8 types.
- Context: 3 or 4 objects (size uniform in {3,4}), drawn as DISTINCT types
  (duplicate objects would make items unsolvable by construction), target
  uniform among them.
- RSA levels, exact normalized tables (uniform prior over objects, uniform
  utterance prior, zero cost, rationality alpha = 1):
  L0(o|u) ∝ [[u]](o); S_k(u|o) ∝ L_{k-1}(o|u)^alpha (over utterances with
  L_{k-1}(o|u) > 0); L_k(o|u) ∝ S_k(u|o). Levels L0..L3 computed.
- Speaker: fixed S2 ("speakers are fixed S2"): the utterance for each item is
  SAMPLED from S2(u|target) (soft, alpha = 1). Reading chosen: sampling rather
  than argmax, since RSA speakers are stochastic by default; recorded here.
- Depth / recursion steps: listener level k counts k recursion steps (L0 = 0).
- Answer and accuracy: at a level, the answer is argmax of L_k(.|u) with
  uniform tie breaking; per-item accuracy is the exact expected value
  1/|argmax set| if the target is in the argmax set, else 0 (no rng in scoring).
- Ambiguity (L5 "number of literal candidates") = |[[u]]| in the context.

## Arms

- TREATMENT (intervention): adaptive listener, theta in {0.6, 0.7, 0.8, 0.9}.
  Compute L0; if max_o L_k(o|u) >= theta stop at k; else go to k+1; stop at
  k = 3 regardless ("depth up to 3").
- CONTROL: fixed-depth L2 and fixed-depth L3 on the same items.
- NULL_TWIN: for each theta, depths are a random permutation (per seed) of the
  adaptive listener's per-item depths across that seed's items -- this
  reproduces the empirical depth distribution exactly (same mean and
  variance) while ignoring uncertainty. The twin answers at its assigned depth.
- POSITIVE_CONTROL: the subset of items with a unique literal referent
  (ambiguity = 1). Detected iff, for every theta and every seed, all such
  items are stopped at depth 0 AND answered correctly, and there is >= 1 such
  item per seed.
- CHEAT: bypasses the mechanism and writes the observable directly on the
  same items: correctness := 1 for every item, depth := 0 if ambiguity == 1
  else 1. Detected iff the evaluator's success criterion fires on it.

## Observables and criteria

- Per (arm, seed): accuracy (mean expected accuracy), mean depth,
  Spearman(depth, ambiguity) (scipy.stats.spearmanr; NaN if depth constant,
  and NaN is treated as failing ">= 0.4").
- Aggregation (ambiguity recorded): each statistic is computed per seed, then
  averaged over the 10 seeds; the criterion is applied to the seed means.
  acc(L2) is the fixed-L2 accuracy seed mean on the same items.
- Success, as written: exists theta with
  acc(theta) >= acc(L2) - 0.01 AND mean_depth(theta) <= 0.7*2 = 1.4 AND
  Spearman(theta) >= 0.4.
- Failure, as written: no theta meets all three, OR the random-depth twin
  with matched mean depth meets the accuracy criterion too. Reading chosen:
  the twin clause is applied per theta -- a theta that meets success counts
  for SIGNAL only if its own twin FAILS acc_twin >= acc(L2) - 0.01.
- Outcome (code, PREREG order): INSTRUMENT_FAIL if positive control or cheat
  not detected; else CONFOUNDED if any theta's null twin meets the full
  success criterion (all three clauses); else SIGNAL if some theta meets
  success and its twin fails the accuracy criterion; else NULL.

## Parameters and seeds (all from the spec, none from results)

- 2000 contexts per seed, 10 seeds (seed = 0..9, numpy default_rng(seed));
  twin permutation rng = default_rng(10_000 + seed).
- 4 predicates, context size 3-4, depth up to 3, thetas {0.6,0.7,0.8,0.9}.
- alpha = 1, zero cost, uniform priors: not given by the spec; standard RSA
  defaults, fixed here before any run.

## Diagnostics for stupid explanations (reported, not used in outcome)

1. size confound: Spearman(depth, ambiguity) within size-3 and size-4 items
   separately, and Spearman(depth, size).
2. deeper levels rarely change answer: fraction of items whose L0 / L1 argmax
   set differs from L2's; accuracies of fixed L0, L1, L2, L3.
3. S2 makes task trivial at L1: acc(L1) vs acc(L2).
Alternative explanation (item distribution): fraction of items with
ambiguity 1. L2 lens: implicature rate = fraction of items where the L2
answer set is strictly smaller than the literal candidate set, and success
of those departures.

## Compute

Expected well under 1 core-minute; measured with time.process_time in
world.py and evaluate.py and recorded in OUTCOME.json.

## Post-run record (attempt 1; nothing changed after the run)

- attempts = 1; no crash, no bug, no rerun; core-minutes 0.045 (world 2.7 s CPU).
- Evaluator outcome SIGNAL at theta 0.6 only (acc 0.7427 = acc(L2) 0.7427,
  mean depth 1.305 <= 1.4, rho 0.739; twin acc 0.697 fails the accuracy clause,
  twin rho ~0). Thetas 0.7-0.9 fail the depth clause (1.88-2.34).
- Not ruled out, from the rows: stupid explanation 3 (S2 makes the task
  solvable at L1). Fixed L1 accuracy 0.7427 vs L2 0.742725; L1 argmax differs
  from L2 on 0.4% of items; L3 identical to L2. A fixed-depth-1 listener meets
  the accuracy and depth clauses at mean depth 1.0 < 1.305; it fails only the
  Spearman clause because its depth is constant. The adaptive gain is mostly
  depth 0 on the 21.6% unambiguous items plus depth 1 elsewhere.
- Size confound partly addressed: within-size rho 0.81 (size 3) and 0.60
  (size 4) at theta 0.6; rho(depth, size) 0.27.
