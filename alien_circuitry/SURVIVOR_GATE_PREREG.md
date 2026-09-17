# Survivor falsification gate: preregistered thresholds (committed before any n=7 measurement)

Candidates: PC-H = full T_7 {cycle, swap01, collapse01}; U-C1 = {cycle, swap01, frozen rank-5 map} with the seed in
`universe/uc1_seed.py` (derived from a fixed string; n=6 seeds 1 and 2 are burnt).

Targets (mechanical, both universes): the 63 restricted-growth maps of rank 2 (canonical representative of every
2-block set partition of [7]).  Corpus start states: every map with rank >= 3 (so at least one rank drop is needed).
Strata by exact D: TRIVIAL <= 2, EASY 3-8, MEDIUM 9-14, HARD >= 15 (chosen from the n=7 probe histogram, mode 17).

Frozen local observation language (pairwise-free), for a state f and target t:
  rank(f); block-size multiset of f (sorted multiplicities of values); per-value counts c_v(f), v = 0..6;
  presence of values 0 and 1 in the image (from counts); action id; whether the action is a no-op;
  immediate target equality; rank(t) and block-size multiset and per-value counts of t;
  bounded-lookahead summaries (target found within h; forward region exhausted within h).
EXCLUDED: position-specific values f(i); pairwise equality f(i) = f(j); kernel blocks or ids; any canonical form
of the partition; any hash of the above.

Lookahead semantics as in gate/observation.py: graph BFS ball of depth h from a candidate successor; SAFE iff the
target is within h; TRAP iff the forward region is exhausted (eccentricity <= h); UNKNOWN otherwise.  The universe
has cycles, so tree-lookahead never exhausts; only graph semantics is reported.

Kill thresholds (fixed now):
  K1 SHALLOW      LA5 proves > 10% of genuine PC-H traps.
  K2 LEAKAGE      on collapse actions of PC-H, the best table classifier over permitted features reaches
                  PR-AUC >= 0.5 or normalised mutual information I(trap; features)/H(trap) >= 0.5 on held-out states.
  K3 RESIDUAL     in U-C1, R1 (kernel-compatible but unreachable) is < 1% of kernel-compatible pairs, or < 10,000
                  pairs in absolute terms, or R1-successor traps are < 5% of all traps.
  K4 DISTANCE     on reachable pairs, a table regressor over permitted features (plus rank difference and
                  collapse-count lower bound) reaches exact-match accuracy >= 0.9 or R^2 >= 0.95 on held-out states.
  K5 ORACLE       exact D cannot be produced at n = 7.

Headrooms, transitions examined as primary cost, states expanded secondary, per-problem means and ratio of sums:
  H0 = 1 - C_oracle / C_min(forward BFS, bidirectional BFS)
  H1 = 1 - C_oracle / C_best cheap policy (B1, B2, LA1..LA5; DFS with backtracking, 40,000-expansion budget)
  H2 = 1 - C_oracle / C_kernel-aware-residual-blind DFS
Lookahead cost in navigation is charged per call as the mean uncached ball size at that depth (sampled on 3,000
random live successors), because the exact per-call ball on this graph is too expensive to materialise inside
every search; this is stated as an approximation in the receipt.
