# AC-01 Universe C design search (2026-09-12)

Status: design search only. No universe was adopted, no compression exists. Four tiny falsification probes were run
and are kept in `evidence/universe_c_probes/` (scripts + JSON), labelled diagnostic.

## 0. Record correction and preservation

The ruling cites resolution rates 89.1 / 97.6 / 99.4 / 99.9% at h = 2..5, "24 matched pairs surviving beyond h = 5",
"six-step propagation" and "maximum path depth 12". None of these are in the committed gate receipt
(`GATE_RECEIPT_UA3.md`, commit fb6f4c9). The committed values are: traps proven 71.2% at h = 2, 99.8% at h = 3,
100% at h = 4 and h = 5; 24 traps needed depth 4 and none needed more; the residual set R_5 is empty under both
semantics; the longest directed path in U-A3 is 8. The verdict NO-GO — TOO SHALLOW is unchanged and is accepted.
U-A3, its results, trap table and receipt are preserved at fb6f4c9 and untouched here.

## 1. What the four failures teach, as design constraints

- Datalog: monotone, so no action can lose the target. Constraint: actions must be able to destroy reachability.
- Reversible rewriting: undirected graph, so every mistake is undone. Constraint: some action must be irreversible.
- U-A2: irreversibility only through cancellation, and the target set made cancellation the trap. Constraint: the
  loss mechanism must be about the state, never about the target's syntax.
- U-A3: forward cones of six states, and distance a closed form in symbol counts. Constraints: bad states must keep
  large viable regions (thousands of states, eccentricity in the tens), and the distance channel must not be a
  count invariant (a healthy fraction of retained edges must lie off every shortest path).

## 2. Families examined and the theoretical kill pass

Kill names: MONO (monotone), REV (reversible), ART (target artifact), SHALLOW (bounded lookahead exposes it), TRIV
(one obvious bit), BASE (a standard algorithm is already optimal / the certificate is a textbook routine), LEAK
(corpus generation exposes the invariant to the representation), SCALE (exact truth infeasible).

### A. Permutation puzzles and group actions (15-puzzle, Rubik-like)
Every finite group action is symmetric: g^-1 is a positive power of g, so the Cayley digraph is strongly connected on
each orbit. No action can lose reachability. Kill: REV. Parity splits orbits, but that is a static class, never a
trap. Role: PC-H-static (predict the class of (s, t) pairs from raw states; no navigation content), or add
irreversibility, which turns the group into a transformation monoid (family F).

### B. Rewriting systems with long critical-pair divergence
Orthogonal (non-overlapping) systems such as Zantema's aabb -> bbbaaa are confluent, so no traps (kill: REV-like,
no loss). Non-confluent terminating systems with short rules have short divergence (U-A3: height 8), and any
length-preserving rule with a fixed count signature makes distance a count formula (U-A3 degeneracy). I found no
naturally occurring string-rewriting system with documented divergence depth above ~5 that is also small enough to
enumerate; extending rules by hand is prohibited. Kill: SHALLOW (no natural horizon source). Not pursued.

### C. Constraint prefix universes (irreversible partial assignments; target = complete solutions)
Common property: distance = number of unassigned variables (closed form), so the only consequence is extendability.
- C1 Tseitin XOR on cubic graphs (GF(2) homology invariant). Probe on the cube graph (8 vertices, 12 edges,
  531,441 partial assignments, 32 solutions): unit propagation at depth 0 catches 92,360 of 92,376 traps from
  random live states and 13,597 of 13,607 from lightly assigned states; DPLL refutation depth never exceeds 1.
  At enumerable scale the invariant is not hidden. It becomes hidden only on expanders with girth >= 6 (30+
  vertices), where the 3^45 chart cannot be enumerated. Kill: SHALLOW at scale, SCALE beyond it. Not pursued.
- C2 Horn / pebbling formulas: unit propagation is complete for Horn, so every trap is visible at depth 0. Kill: SHALLOW.
- C3 Random 3-SAT / 3-colouring prefixes: no compact certificate is believed to exist (resolution lower bounds).
  Fails C5 by construction. Role: NEGATIVE CONTROL for the hypothesis (a universe where compression should fail).
- C4 Bipartite matching / exact cover prefixes: extendability = Hall's condition, a compact multidimensional
  certificate, but a polynomial algorithm (augmenting paths) is the standard baseline. Kill for primary: BASE.
  Possible PC-H-static; distance trivial.

### D. Planning / Petri nets / VASS
Probe on four random bounded nets (8 places, 7 transitions, bound 3): reachable sets from the initial marking are
93 to 938 markings; trap rates 48-76%; place invariants alone catch 0 of the sampled traps but the state-equation
LP (M_t - M = C x, x >= 0) catches 400 of 400 in every net; retained edges are almost all on shortest paths.
The cheap linear certificate explains the whole phenomenon at this scale. Kill for primary: BASE (integer-linear
certificate is a textbook routine). Possible second PC-H (integer-linear hidden structure), but small reachable
sets make it a weak corpus. Not pursued as primary.

### E. Algebraic / topological obstruction
Tseitin is GF(2) homology (C1). The partition lattice of a transformation monoid (F2) is the strongest example
found: a multidimensional order-theoretic invariant that lookahead cannot see and counts do not reveal.

### F. Automata and transformation semigroups
- F1 Power automata (state = subset, letters shrink images). Probe at n = 10: Cerny C_n and every random
  permutation + random-map automaton have ZERO size-invisible traps (subsets of equal size are mutually reachable
  in 97-100% of pairs), so the whole invariant is the subset size, a count. Two random maps give reachable sets of
  32-34 subsets. Kill: TRIV (Cerny, random perm+map), SCALE-of-corpus (two maps). Cerny is a good "resource = size"
  control with a one-dimensional invariant.
- F2 Full transformation monoid T_n, generators {n-cycle, swap(0,1), collapse 0 -> 1}, action f -> g o f.
  Theorem: t reachable from f iff ker f refines ker t (f(i) = f(j) implies t(i) = t(j)); verified exhaustively at
  n = 6 (90 rank-3 targets) and n = 7 (63 rank-2 targets, 52 million pairs, 0 mismatches). Probe n = 7:

```
states 823,543   actions per state 3 (constant)   nominal edges 2,470,629
live (f, t) pairs 21.5%    traps 3,069,066 of 33,422,508 live triples (9.2%)   every trap is a collapse
traps invisible to the rank count      99.996%   (rank drops below the target rank in 126 of 3.07M)
post-trap forward region (quartiles)   49 / 2,401 / 2,401 / 16,807 / 117,649 states
post-trap BFS eccentricity             13 / 20 / 22 / 26 / 30
distance D                             max 24, mode 17; retained edges off every shortest path 55%
random trap-free walks from D >= 4     0.75% reach the target
forward BFS vs oracle (states)         32,407 vs 16.8   (oracle SA 0.9995)
```

  Kill pass: MONO no (collapses lose targets); REV no (collapse irreversible; permutations reversible, which is what
  makes the live regions large); ART no (targets are maps, traps are about which points get identified); SHALLOW no
  (exhaustion needs thousands of states, depth 13-30); TRIV no (the invariant is a set partition, 21 pairwise bits
  structured as a lattice); BASE partial (the kernel test is O(n^2) once you know it; that is exactly the known
  answer a PC-H is allowed to have, and the distance layer has no such routine); LEAK: the raw state is the map
  itself, so a representation with access to pairwise value equality can rediscover the invariant, which is the
  point of a control; the frozen local language must therefore exclude pairwise features (see section 4);
  SCALE fine (n = 7 in seconds, n = 8 = 16.7M states feasible with chunking).
- F3 Restricted submonoids (n-cycle plus one or two random non-injective maps, or cycle + swap + one random map).
  Probe n = 6, three generator sets: kernel refinement stays necessary (0 reachable pairs violate it) but is not
  sufficient: 2.1-4.7% of kernel-compatible pairs are unreachable; traps 27-42% of live triples, 91-94% invisible
  to rank; post-trap regions 216-1,296 (median), eccentricity 12-13 (median), max distance 16-21, 30-48% of
  retained edges off every shortest path; random walks 0-0.75%; BFS 1,400-5,000 expansions vs oracle 7.5-13.6.
  The Green (R/L-class) structure of the generated submonoid is the reachability certificate; no closed form.

## 3. Scores (ranked by experimental cleanliness)

```
candidate                 scale      oracle   branch  loss mechanism        horizon   cheap local   best symbolic    hidden coord        dim     leak  artifact  known sol.   role
T_n full (F2)             n^n, 823k  BFS      3       collapse (kernel)     13-30     rank: no      kernel test      partition lattice   21 bit  med   none      yes (theorem) PC-H
T_n restricted (F3)       n^n        BFS      3       rank-dropping maps    12-13+    rank: no      Green structure  R-classes + D       many    med   none      partial      U-C1
Cerny power automaton     2^n        BFS      2       merge letter          9-87      size: YES     size count       |S|                 1       high  none      yes          control
random Petri / VASS       B^p        BFS      2.6-3.7 consumption           1-17      enabled set   state-eqn LP     P-inv + LP          few     high  none      yes (LP)     PC-H(2)
Tseitin XOR (small)       3^m        enum/GE  2-24    implied literal       0-1       UP: YES       UP/Gauss         GF(2) coset         m-n+1   high  none      yes          killed (scale)
matching / exact cover    3^m        matching 2-m     wrong commitment      ?         alt. path     augmenting path  Hall sets           many    high  none      yes (poly)   PC-static
random 3-SAT prefix       2^n        enum     2       implied literal       long      UP: partial   DPLL             none believed       -       -     none      no           NC
15-puzzle / Rubik         n!/2       BFS      2-4     none (reversible)     -         -             -                parity              1       -     -         yes          PC-static
rewriting (natural)       4^L        BFS      2-6     rule orientation      <= 8      length bound  lookahead        count vector        -       -     U-A2 art  -            killed
```

## 4. Recommended pair

### PC-H: full transformation monoid T_7, rank-2 canonical targets

- States: maps [7] -> [7] encoded as 7 digits; actions: cycle, swap(0,1), collapse 0 -> 1 applied on the left.
- Targets (mechanical): the 63 restricted-growth maps of rank 2 (one canonical representative per 2-block set
  partition). Rank-3 (301 targets) is the fallback if 63 is too few; both are mechanical.
- Known hidden invariant: kernel refinement. Prediction: R[f, t] = [ker f <= ker t]. Withheld from every
  compressor and from every baseline. Success = a representation that separates live from dead pairs at the
  kernel-lattice level, and can be compared against the known answer afterwards.
- Frozen local observation language: rank (number of distinct values), value histogram, immediate target
  equality, out-degree (constant 3), bounded lookahead. Pairwise equality f(i) = f(j) is EXCLUDED, because it is
  the invariant; including it would make the control solvable at depth 0.
- Why it survives the four failures: collapse is irreversible and non-monotone (Datalog, reversible-rewriting);
  the loss is about which points are identified, not about target syntax (U-A2); post-trap regions are thousands
  of states with eccentricity 13-30 and distance is not a count formula, 55% of retained edges are off-shortest
  (U-A3).
- Expected observability horizon: exhaustion depth 13-30 with region sizes 2,401-117,649; the target is never seen
  from a dead state, so lookahead of any depth below the region size cannot prove a trap. H_obs > 5 for
  essentially all traps (to be measured exactly with the existing gate machinery).
- Exact oracle: reverse layered BFS per target over the explicit graph (as in `universe/enumerate.py`), plus the
  theorem as an independent check (0 mismatches at n = 6 and 7 already).
- Strongest cheap baseline: bounded lookahead (LA1-5) and the rank heuristic, both measured useless here; the
  per-problem min of forward/bidirectional BFS is the exact uninformed reference (tens of thousands of
  expansions). The kernel-aware searcher is reported as the UPPER reference (what knowing the invariant buys), not
  as a baseline.
- Scale: 823,543 states, 2.47M edges, seconds to enumerate; D chart 823,543 x 63 int16 = 104 MB dense, far
  smaller sparse. n = 8 (16.7M states) is available for OOD.
- Post-implementation kills: (i) the gate's LA5 proves more than 10% of traps, or the rank/histogram language
  predicts trap status above chance; (ii) a count-based closed form reproduces D; (iii) the kernel-aware searcher
  already reaches oracle cost (then the distance layer is empty and the universe is one-layered); (iv) trap
  prevalence collapses under the chosen target set.

### U-C1: restricted transformation submonoid, n = 7, mechanical rank-k targets

- Same substrate and instrument; generators = n-cycle, swap(0,1), and one random map of rank n - 2, seed fixed and
  committed before any measurement of that seed's consequence structure (the seed-1 and seed-2 nets in the probe
  are burnt: they were inspected).
- Two discovery layers, preregistered separately: (a) residual reachability beyond kernel refinement
  (2-5% of kernel-compatible pairs at n = 6; to be measured at n = 7); (b) the distance / shortest-path layer,
  which has no known closed form (word length in a transformation semigroup) and where 30-55% of retained edges
  are off every shortest path. The kernel invariant is NOT the answer key for layer (b), and only a partial key
  for layer (a); the full key is the Green structure of an unnamed submonoid, which nobody has written down.
- Honest statement of what is and is not known: reachability is mostly (95-98%) the known kernel order; the
  primary discovery question is therefore the distance geometry, with the residual reachability as a smaller
  second question. If the operator wants a primary universe with NO known component at all, none passed the kill
  pass in this search (random CSP fails C5; every other candidate has a textbook certificate).
- Why it survives: as PC-H, plus the certificate is not a one-line invariant.
- Horizon: eccentricity 12-13 median at n = 6 with regions in the hundreds to thousands; larger at n = 7.
- Exact oracle: reverse BFS; the kernel criterion as a necessary-condition check.
- Strongest cheap baseline: LA1-5, rank heuristic, BFS min; plus the kernel-aware searcher as the reference that
  isolates layer (b): headroom for compression = oracle versus kernel-aware search.
- Scale: as PC-H.
- Post-implementation kills: (i) kernel-aware search reaches within 5% of oracle cost (layer (b) empty);
  (ii) layer (a) residual under 1% at n = 7; (iii) a formula in (rank, kernel, cyclic offset) reproduces D within
  +-1 on 95% of pairs (then the "unknown" is known); (iv) LA5 resolves more than 10% of traps.

### Controls to carry alongside

- Cerny power automaton C_10: one-dimensional invariant (subset size), long reset words (distance to the singleton
  up to 90): a TRIV control. Any method that "discovers" more than the size there is fitting noise.
- Random 3-SAT prefixes (n ~ 20): negative control for the hypothesis; compression is expected to fail.
- Tseitin on the cube graph: a control where unit propagation is the whole story (SHALLOW control).

## 5. What a tiny probe would still have to falsify before implementation

1. At n = 7 with the frozen seed, the beyond-kernel residual and the off-shortest-path fraction (layer sizes).
2. The gate's H_obs distribution on T_7 (expected > 5 for nearly all traps; the probe measured eccentricities,
   not the exact lookahead verdicts).
3. That a frozen local language without pairwise features cannot predict trap status above the 9% base rate.

Everything else in this document is either a theorem, a probe result, or a documented judgement.

## 6. Recommendation

Adopt the transformation-monoid substrate. Build PC-H = full T_7 first, run the existing gate on it (termination is
not required there: the universe has cycles by design, and the gate's SCC test will say so), and require H_obs > 5
for most traps and lookahead headroom near zero before anything else. Then freeze one restricted submonoid as
U-C1 with two preregistered layers. Do not build compression until both pass their post-implementation kills.
