# S5 -- world construction, myopia definition, observable coordinate, leakage audit, exact counterexamples

Operator order: `roles/Archaeon/prompts/2026-09-12_seasons/S5_ORDER.md` (sha256 5c6c4279...2ee14a).
Preregistration: `S5_PREREG_2026-09-13.json`, commit d952f9c56 (before any batch row). Instrument repair: bcd7a40cf.

## 1. Instrument repair (phase 0, committed independently)

`archaeon/producer/work_budget.py`: a deterministic WORK budget (units = DFS nodes in the block solver, block-convolution steps in the
partition, probes scored in selection, and for O `(subset, probe)` DP evaluations) held on a context variable. Every PEW-consuming
producer runs inside `with WorkBudget(max_units)`; exceeding it raises inside the search and the producer returns an explicit
`BUDGET_EXHAUSTED` proposal (probe `None`) whose `extra["work"]` carries phase, units used, per-phase counters, elapsed seconds.
There is no post-hoc "returned after 30 minutes, therefore timeout": the bound is a property of the work, not the clock, and the
same call stops at the same unit in the same phase every time (tested). M's S4 wall-clock fallback was REMOVED (semantic change,
recorded in its docstring); the old S4 test that asserted it was rewritten. Leakage: the mechanism has no target parameter and the
provenance never contains the target (tested). 68 tests green at bcd7a40cf.

## 2. World construction (independent of every producer)

A world is an EVIDENCE STATE, not a target. Two families, every parameter combination, nothing chosen by any result:

* shell(L, m): one fossil `0^L` with exactly m mismatches (feasible set = Hamming sphere, C(L, m) targets, one unresolved block);
* prod2(L, a, uA, uB): fossils `0^L` and `1^a 0^(L-a)` with mismatch counts `uA + uB` and `(a - uA) + uB`, i.e. two independent
  count-known blocks (block A of size a with uA ones, block B of size L-a with uB ones), C(a,uA) C(L-a,uB) targets.

Eligibility: 3 <= N <= 40 at L 8 (119 states, 1828 targets) and 3 <= N <= 30 at L 9 (114 states, 1458 targets); states with identical
feasible sets are one state. The harness then enumerates EVERY feasible target (census): the expectation over targets is exact and
equals the producers' own named uniform prior. Targets never enter world construction, producer selection or routing; each arm's
fossil list is its own; the score is revealed only after the proposal is sealed (S4 separation preserved, tests unchanged).

## 3. Myopia, defined before any producer ran

Decision-state myopia (exact, target-free): for evidence state s and the chosen probe g,
`delta(s, g) = Q*(s, g) - V*(s)`, with `V*` the exact minimum expected number of further probes to identification (adaptive DP over
reachable feasible subsets, every probe in {0,1}^L, uniform prior) and `Q*` the same with g forced first. s is myopic for g iff delta > 0.
World-level: `(E_G - E_O)/E_G` over the census, O being the exact policy.

Why not the two-step gap. Exact enumeration over all shell / prod2 / prod3 states at L 6..10 (scratch `s5_explore.py`): strict
two-step myopia of the one-step count objective (no ER-optimal probe is two-step optimal) does not exist below L 8; the minimal case is
L 8, blocks 4/4 with 1 and 2 ones (N 24): the greedy class puts weight 2 in each block (partition {1:2, 3:10, 5:10, 7:2}, ER 8.667,
two-step value 3.0); the far-sighted class puts weight 2 in the one-one block and 1 or 3 in the two-one block ({2:6, 4:12, 6:6},
ER 9.0, two-step value 2.833). Mechanism: the sum oracle aliases per-block outcomes; the greedy probe buys a finer immediate partition
whose cells are unions the second probe cannot split cleanly. Frequency among two-block states: 4/245 (L 8), 36/476 (L 9), 18/84
(L 10); never in single-block or three-block states (L <= 9). BUT the exact two-step policy followed over the trajectory is WORSE than
greedy in those very states (3.083 vs 3.000 probes; scratch `s5_effect.py`): a horizon-2 count objective is itself myopic at horizon 3.
The two-step count gap is therefore not the coordinate, and M (two-step over W's one-step top-6) cannot even see the far-sighted class
(all of W's top-6 are greedy-class); this is a design property of M recorded here, not a rerun of S4.

Full-horizon mechanism (scratch `s5_trace.py`, exact): on the shell m 2 at L 8 (N 28) greedy and optimum agree at the root (weight-4
probe) and diverge at depth 1 in the N 6 cells, where the ER objective is INDIFFERENT between partitions {3,3} and {1,4,1} (both
ER 3.0) whose identification futures differ (2.667 vs 2.000 further probes); the lexicographic tie-break picks the entropy-poorer one
(1.00 vs 1.25 bits). Same on the counterexample at depth 1 (N 10 cells). ER = sum n_d^2 / N is a collision statistic (Renyi-2); its
tie classes are coarser than the identification-relevant ordering, and the loss lives in the tie-break, not in lookahead depth.

Exact attainable range at L 8 (greedy-lex = exact one-step optimum, vs optimum; `s5_opt_L8.json`): see the readout for the completed
screen; at the time of preregistration 39 of the first 80 states showed >= 2 % relative loss (mean 3.4 %, max 25 %).

## 4. The observable coordinate

Primary, kappa_H(s, g): 1 iff some probe q has ER(q) <= ER(g) and H(q) > H(g) -- the chosen probe is dominated in the
(count, entropy) order. Inputs: the fossils and the probe alphabet; one pass over the one-step partitions a producer computes anyway.
Prediction (preregistered): kappa_H = 1 predicts delta(s, g) > 0 for G's own choices; routing O only where it fires (arm RH) recovers
a material part of O's advantage at a minority of O calls. Secondary, reported: kappa_tie (ER-optimal class contains >= 2 partition
multisets), kappa_proxy (two unresolved blocks of size >= 3), pool_suboptimal (G's pool missed the exact one-step optimum), and the
root coordinates entropy_disagreement / entropy_deficit_bits / two_block_proxy / two_step_gap.

Leakage audit: every coordinate function and producer takes (fossils, seed_inputs[, bounds]); no parameter named target / hidden_target
/ t / outcome / winner (asserted in `archaeon/tests/test_s5_producers.py`); the runner computes kappa from (fossils, chosen probe)
before the score is revealed, and each decision-state row carries the evidence snapshot id it was computed from. The world generator
never sees a target (states first, census after). U's seed inputs are (lane, L, state_id, target_index, arm, step): target_index is a
census position, not target content, and U's signature carries no evidence.

## 5. Producers

U, G, W unchanged from S4 (PRODUCER_VERSION recorded on every proposal); M unchanged except the phase-0 contract. New in
`archaeon/producer/s5_producers.py`: O (exact DP; memoised across calls by feasible subset, declared; work-budgeted; SCOPE_EXCEEDED
above 64 targets or 12 bits), GH (G's pool and objective, ties broken by larger outcome entropy, then lexicographic -- the minimal
cheap consumer of the mechanism), RH (routed: G unless kappa_H fires, then O). Tests: exact values 35/12 and 97/28 reproduced by
following O over every target; O strictly better than W on the shell (97/28 vs 106/28); memo hit returns the identical proposal
with zero fresh work; budget/scope outcomes explicit; no target in provenance; GH = G where the ER class is entropy-homogeneous.
