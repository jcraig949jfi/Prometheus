# Dossier: alien_circuitry (AC-01, AC-01D v1/v2, nursery crucibles)

VERDICT: SALVAGE_COMPONENT -- the engine is an exact-oracle measurement programme, not a reasoning substrate; its one
"discovered" compression is a textbook symmetry quotient read off the ground-truth distance chart, but its instrument
(exact chart + trap/lookahead gate + headroom-capture harness + preregistration discipline) and the
verify-then-quotient step (NUR-001) are worth carrying forward as fixtures and as a primitive.

Auditor: Hestia audit worker, G7(c). Currency 2026-10-06. Read-only; nothing was run except side arithmetic.

## 0. Identity

- Path: `alien_circuitry/` (280 tracked files: ~60 .py, 14 top-level receipts/preregs, results JSON/CSV/logs, 11
  weight files). Worktree `C:/Prometheus-worktrees/hestia-boot-2026-10-06` at HEAD `3fed30ac9`.
- Seat: none recorded. Achilles census reconstruction lists `alien_circuitry` among "engines with recent commits and
  no recorded owner" (`roles/Achilles/RECONSTRUCTION_2026-09-30.md:96-97`). Commits are operator-session commits on
  branch `alien-circuitry/phase-ab-2026-09-12`, 2026-09-12 to 2026-09-14 (git log: 898338725 .. 93cdb3392).
- Prior external assessments found: OPUS-5.5 salvage matrix classifies it HISTORICAL_CONTROL / known-answer fixture
  (`docs/phase3/design/OPUS-5.5/SALVAGE_MATRIX.md:555-559`); NEW_DEFECTS lists "truth-side kernel invariant handed to
  searchers" and "held-out sets in-distribution after quotienting"
  (`docs/phase3/design/OPUS-5.5/salvage/NEW_DEFECTS.md:371-374`). Atlas regularities record the tie-break
  denominator artefact (`roles/Atlas/inference_harvest_2026-09-30/workers/REGULARITIES.md:443`). This dossier
  confirms both defects from code.
- Read in full: README.md, DATALOG_FAILURE.md, RECEIPT_PHASE_AB.md, GATE_RECEIPT_UA3.md (first 120 lines),
  UNIVERSE_C_DESIGN_SEARCH.md (first 80 lines), SURVIVOR_GATE_RECEIPT.md, AC01D_RECEIPT.md, AC01D_V2_RECEIPT.md,
  nursery/NURSERY.md (NUR-001 entry and index), nursery/crucibles/RESULTS_C_B.md; code: universe/directed_rewriting.py,
  universe/monoid.py, universe/uc1_seed.py, ac01d/corpus.py, ac01d/evaluate.py, ac01d/baselines.py,
  ac01d/v2/canonical.py, ac01d/v2/orbit_navigation.py, ac01d/families/c5_learned.py (1-60), c6_dsl.py (1-66).
- Result files opened and checked: results/ac01d/families/V2_orbit_table.json, results/ac01d/v2/canonical_symmetry.json,
  results/ac01d/families/C5_controls.json (head).
- NOT read: tests/*, evidence/* probe scripts and their JSON (numbers taken from receipts only), PREREGISTRATION_*.md
  and SURVIVOR_GATE_PREREG.md in full, nursery/CRUCIBLES.md, TENSION_INVENTORY.md, crucible_b/b2/c code, families
  C1/C2/C3-C4 code, interpret/dissect_c5.py, forensic/*, gate/*.py bodies (only signatures), universe/metrics.py
  bodies, the remaining results JSON (survivor, gate, C1-C6 families). Numbers from unread JSON are tiered CLAIMED.

## 1. Mechanism (what the code does)

Question as chartered (README.md:3-5): when an inference frontier is combinatorially large, does its
decision-relevant consequence structure occupy a much smaller representational space that can replace search?

The engine is a sequence of exhaustively enumerated toy universes, each with an exact ground-truth distance chart,
followed by attempts to compress that chart.

1. Universes (all fully enumerated, all exact):
   - Monotone Datalog (rejected; DATALOG_FAILURE.md).
   - Directed bounded string rewriting over {x,X,y,Y}, len <= L (`universe/directed_rewriting.py:1-25`); states are
     indexed bijectively, NS = (4^(L+1)-1)/3 (`:39-40`, `:71-84`); transitions are generated vectorised for every
     (rule, position) (`:101-151`); distances by layered BFS (`:177-195`). Presentations ABELIAN, BRAID_B3, one-way
     braid U-A3.
   - Full transformation monoid T_7 with generators {7-cycle, swap(0,1), collapse 0->1} acting on the left
     (`universe/monoid.py:44-84`, generators `universe/uc1_seed.py:32-33`); restricted variant U-C1 with a frozen
     random rank-5 map (`uc1_seed.py:10-29`). Every state is an n-digit map (NS = n^n, `monoid.py:45-48`); targets are
     the restricted-growth maps of rank 2 (`monoid.py:27-37,66`); D is computed by one reverse BFS per target
     (`monoid.py:67-69`). The kernel bitmask -- the known reachability invariant -- is computed as a truth-side array
     (`monoid.py:76-79`, `kernel_compatible` `:87-89`).
2. Gates (instrument): exact bounded lookahead (SAFE/TRAP/UNKNOWN) as a fixed BFS ball
   (`gate/observation.py:72`, `gate2/observation_monoid.py:39-49`); termination/SCC proofs (`gate/termination.py`).
   These decide whether a universe has non-trivial "delayed consequence" before any compressor is allowed.
3. AC-01D corpus and splits (`ac01d/corpus.py:43-101`): T_7, 63 rank-2 targets, rank >= 3 starts; state roles by
   sha256 bucket 60/20/20 (`:51-52`), 13 of 63 targets held out (`:53-55`), pair roles 80/20 (`:57-61`); an assert
   checks the kernel theorem against BFS reachability on every corpus pair (`:65-66`).
4. Evaluation harness (`ac01d/evaluate.py`): a representation only supplies `predict_D`; navigation is greedy
   best-first or DFS ordered by predicted D (`:83-93`). CRUCIAL: pruning of dead successors uses the truth-side
   kernel mask, `dead(s,t) = rank[s] < rank[t] or (kmask[s] & ~kmask[t]) != 0` (`evaluate.py:56`, applied `:86`;
   same in `baselines.py:72`). Reachability is therefore never learned or searched; it is handed to every policy.
   Score HC_D = 1 - (C_M - C_O)/(C_K - C_O) with C_K = kernel-aware DFS ordered by rank difference then generator
   index (`baselines.py:73-77,112-113`).
5. Representation families: C1 masked low-rank, C2 CP/TT/Tucker, C3/C4 exact quotients, C5 MLP over 14 embedded raw
   digits (`families/c5_learned.py:24-32`, two ReLU layers of 256), C6 GP over a typed expression DSL with 31
   terminals (digits, constants 0..7, per-value counts `ns0..ns6`, `nt0..nt1`, `rank`) and 9 operators, trees <= 40
   nodes (`families/c6_dsl.py:18-19,62`).
6. v2 (the "discovery"): canonicalise each (f,t) pair under domain relabelling sigma in S_7 by sorting the 7 columns
   (f(i), t(i)) lexicographically (`ac01d/v2/canonical.py:33-43`); build a lookup table orbit-id -> mean D from FIT
   rows of the exact chart (`v2/orbit_navigation.py:124-130`); fallback to a rank-difference mean on unseen orbits
   (`:115-121`). The value-relabelling symmetry search is brute force over all 5040 permutations
   (`canonical.py:24-30`).

Documented vs code. Documents describe C5 as a learned representation "on unseen targets and unseen states"
(AC01D_RECEIPT.md:9-10). The code shows (a) the kernel invariant is supplied by truth (`evaluate.py:56`), which the
receipts do state ("after exact reachability is supplied"); and (b) "unseen targets" are not unseen in the quotient
(section 3a). The v2 receipt itself retires the "alien circuitry" reading: "C5 was therefore not alien circuitry"
(AC01D_V2_RECEIPT.md:17). Documentation and code agree; the engine is unusually self-critical.

## 2. Evidence

OBSERVED (rows on main that I opened):
- Orbit table, FIT rows only: 34,800 bytes, CR 30.5, 25,363 orbits seen, 4,291,106 fit rows, 0 non-integer cells;
  on all five sets solve 1.0, 0 failures, excess 0.0, HC_D (GBFS, transitions) 0.9968-0.9995; e.g. HELD_BOTH 37.88
  transitions vs oracle 37.78, KA-DFS 88.57, KA-GBFS 122.23 (`results/ac01d/families/V2_orbit_table.json`).
- Value symmetries fixing the generator set: identity only; domain-relabelling violations 0; orbit census
  reachable pairs 11,138,190, per-target canonical orbits summed 289,247 (reduction 38.5 per target)
  (`results/ac01d/v2/canonical_symmetry.json`). The global count 25,382 (11,140,836 pairs incl. rank-2) comes from
  V2_orbit_table.json `exact_all_pairs.fit.orbits` = 25,382, rows 11,140,836: global reduction 439x.
- C5 label-permutation control collapses: HC_D -46.6 (CI [-58.8, -35.1]) on HELD_TARGETS
  (`results/ac01d/families/C5_controls.json`).

CLAIMED (receipt prose; underlying JSON exists but I did not open it):
- Datalog: 32,768 states, max proof 4, 0 reachability-changing transitions (DATALOG_FAILURE.md:20-31).
- Rewriting: genuine trap rates 0.44-2.6%, post-trap eccentricity <= 4-5, braid 93% of non-trap actions on a
  shortest path (RECEIPT_PHASE_AB.md:93-131,196-197).
- U-A3: depth-4 lookahead proves 12,191/12,191 traps; NO-GO TOO SHALLOW (GATE_RECEIPT_UA3.md:3-9,105-112).
- Survivor gate: PC-H LA5 recall 0.00004; U-C1 residual R1 = 0 on 51,716,070 pairs; NO-GO RESIDUAL TOO SMALL
  (SURVIVOR_GATE_RECEIPT.md:3-11,138-144).
- AC-01D-v1 matrix: CP r16 HC_D 0.55-0.61 at 1,708 B; C6 0.54-0.59 at 1,428 B; C5-medium 0.91 at 226,956 B; C1/C3/C4
  killed (AC01D_RECEIPT.md:35-47).
- Crucible-B: mined macros worst of 84 six-sets under DFS, every macro set increases search (RESULTS_C_B.md:48-58).
- Crucible-C (Diomedes pair-quotient): cost-to-first-break 2.69 -> 2.22, oracle 1.00, HC 0.28, p = 0.005 per seed
  (RESULTS_C_B.md:15-23).
- Tie-break artefact: KA-DFS denominator 88.6 vs 170 transitions under an arbitrary tie-break change
  (RESULTS_C_B.md:60-79).

DESIGNED (not run): rank-3 targets, n = 8 replication, equivariant compression of the 25,382-entry table, NUR-001
cousin tests (AC01D_V2_RECEIPT.md:103-110; NURSERY.md NUR-001 "cheapest kill experiment").

## 3. Matrix

### 3a Combinatorial explosion and reachability

Search spaces (scratch computation, `scratchpad/ac_scale.py`):

    rewriting universe states  NS(L) = (4^(L+1)-1)/3   L=10: 1,398,101   L=12: 22.4M   L=16: 5.7e9   L=20: 1.5e12
    T_n states                 n^n                     n=7: 823,543   n=8: 1.68e7   n=9: 3.87e8   n=10: 1.0e10
    rank-2 targets             S(n,2) = 2^(n-1)-1      n=7: 63        n=8: 127      n=10: 511
    exact D chart entries      n^n * S(n,2)            n=7: 5.2e7     n=8: 2.1e9    n=9: 9.9e10   n=10: 5.1e12
    pair orbits (upper bound)  C(3n-1, n) rank-2       n=7: 77,520 (25,382 reachable measured)
                                                       n=8: 490,314   n=10: 2.0e7   n=12: 8.3e8
                               C(4n-1, n) rank-3       n=7: 888,030   n=10: 6.4e8

Where it explodes: everything in the programme presupposes the exact chart. The receipts already say L = 12 needs
chunking to disk (RECEIPT_PHASE_AB.md:45) and runs at n = 7 were killed three times by host memory
(SURVIVOR_GATE_RECEIPT.md:30-32; AC01D_RECEIPT.md:28-30). T_8 needs 2.1e9 int16 D entries (~4.3 GB) before any
compressor exists; T_9 needs ~200 GB. The quotient helps storage (C(3n-1,n) grows like ~6.75^n versus n^n * 2^n)
but the table is BUILT FROM the exact chart (`orbit_navigation.py:142-143`), so the compression never pays the cost
it is supposed to avoid. The question "can structure replace search" is answered only after search has been done
exhaustively, on every pair.

Where it is a desert: the programme's own history is a sequence of deserts found by the gates. Datalog: zero
reachability-changing actions. Rewriting: traps 0.4-2.6% of live triples, and their consequences are visible within
4-5 steps. U-A3: depth-4 lookahead proves every trap. U-C1: reachability residual after the known invariant R1 = 0.
In T_7 the only non-trivial layer left is shortest-path distance under known reachability. In other words the space
of "decision-relevant consequence structure that is neither shallow nor a known invariant" was empty in every
universe the engine could enumerate. That is the main empirical finding of AC-01 and it is a desert result.

Hit rates and coverage: navigation evaluation used 300 problems per set x 5 sets (~57,000 oracle-level transitions)
on a graph of 1,910,756 distinct edges; fine for a known-answer test. The orbit table saw 25,363 of 25,382 orbits in
FIT (99.93%). Held targets are not out-of-distribution: the 63 rank-2 targets fall into 6 label-aware orbit types
(block containing position 0 of size k = 1..6, counts 1, 6, 15, 20, 15, 6), so every held target is a domain
relabelling of training targets and every held pair's orbit is, with 99.9% probability, a FIT orbit. "Generalisation
to unseen targets and unseen states" in v1 and v2 is lookup after an exact symmetry, which the NEW_DEFECTS entry
also flags.

### 3b Cosplay vs foundation

What does the work that gets called "compression of consequence structure":
- Reachability: a hand-supplied, truth-side kernel-refinement invariant (`evaluate.py:56`, `monoid.py:87-89`). Known
  semigroup theory; never learned.
- Distance: in v2, an exact lookup table keyed by a hand-written canonicaliser for a symmetry that follows from one
  line of algebra (left action commutes with right composition, `canonical.py:3-13`). Values are copied from the
  BFS chart. Nothing is inferred; the "discovery" is that D is constant on S_7-orbits, which is a theorem, not a
  finding.
- C5: an MLP regression on raw digits, explained 89% by the orbit table and 96% by a depth-16 tree on transparent
  coordinates (AC01D_V2_RECEIPT.md:17-21). The receipt calls it "a symbol-bound approximation". Correct.
- C6 (the only "evolved" component): GP over 9 operators and 31 terminals including hand-supplied count features
  (`c6_dsl.py:18-19`); it reaches HC_D ~0.54 and the authors "cannot read them as rules" (AC01D_RECEIPT.md:150-153).
  This is a selection loop over a small operator set approximating the coarse part of a known function.
- Navigation itself is greedy best-first or DFS with a heuristic (`baselines.py:23-42`): textbook A*-family search.
  When the heuristic is exact (the table), it trivially achieves oracle cost.

Verdict on the "reasoning" claim: there is no reasoning circuit anywhere in this engine and the engine does not
claim one -- its own README says rediscovery of known mathematics is "instrument success, not alien circuitry"
(README.md:53). The value is the honesty of the ruler. Ceiling, concretely: the method family "exact chart ->
quotient by verified symmetry -> table" has ceiling = (cost of the exact chart) and (number of orbits); it cannot go
beyond universes whose full chart fits in memory (n <= 7-8, L <= 11-12) and cannot produce structure that is not a
known group action. Wall-clock: the orbit table costs 0.11 ms per decision vs 0.56 us per raw expansion
(AC01D_V2_RECEIPT.md:13-14); at ~38 decisions that is ~4 ms versus ~0.05 ms for KA-DFS's ~89 expansions, i.e. the
"search-avoiding" representation is about 80x slower than the search it replaces at this scale.

### 3c Substrate bottlenecks

- Representation: states are integer indices into dense enumerations (`directed_rewriting.py:23-24`,
  `monoid.py:45-48`). There is no compositional state representation; nothing can be learned about an object
  that was not enumerated. Every family is a function from (state id or digits, target) to D.
- Memory: dense D charts (int16, states x targets) and per-edge x per-target tables (RECEIPT_PHASE_AB.md:183-192:
  77.7M edge-target rows at L = 10). This is the hard wall; it has already killed runs.
- Credit assignment: supervised regression on the exact D (C5, C2, C6 fitness = RMSE on D, `c6_dsl.py:7-9`). The
  learning signal IS the answer. No family is trained from navigation outcome or from failures.
- Compositionality: none of the families compose. The crucible that tested compositional reuse (mined macros as
  compiled trajectories) died: worst of 84 under DFS, every macro set increases search (RESULTS_C_B.md:48-58).
- Instrument fragility: the HC_D denominator doubles under an arbitrary tie-break change (RESULTS_C_B.md:60-79), so
  every mid-range HC_D (C5 0.91, CP 0.55, C6 0.54) has an unmeasured denominator sensitivity of order 2x. Only
  oracle-level results are robust.
- I/O: none beyond the closed universe; no agent interaction, no environment noise, deterministic generators.

## 4. Deliverable sections

### Discovery Approach

Build small worlds whose entire consequence graph is enumerable, compute exact distances and traps, use gates to
reject worlds where the consequence structure is shallow or already explained by a known invariant, then ask whether
a compact representation of the residual can replace search at oracle quality, scoring every compressor against
preregistered bands and controls. "Physics of intelligence" here means: is there decision-relevant structure in a
combinatorial frontier that is smaller than the frontier and not already textbook.

### The Brick Walls

1. Exact-oracle dependence. Every representation is fitted to, or read from, an exhaustive BFS chart. T_8 needs
   2.1e9 chart entries; T_10 needs 5.1e12. The engine cannot ask its question in any universe large enough for the
   answer to matter.
2. The desert of non-trivial consequence. Across 5 universe families, consequence structure was either impossible
   (Datalog, 0 reachability-changing actions), shallow (rewriting/U-A3: 100% of traps proven by depth-4 lookahead),
   or fully explained by a known invariant (U-C1: R1 = 0 on 51.7M pairs). The only survivor was distance under a
   group symmetry.
3. Known-symmetry ceiling. The best result is a 25,382-entry table under S_7 domain relabelling (439x global
   reduction), exact because of a one-line theorem. Held-out generalisation is guaranteed by that symmetry (63
   targets = 6 label-aware types). Nothing here would find a symmetry or invariant that is not first written by
   hand; the brute-force symmetry search is 5040 permutations (n!), which does not scale either.
4. No compositional mechanism. Macro compilation (the one compositional lever) failed: mined macros ranked 84/84.
5. Denominator fragility: KA baseline 88.6 vs 170 transitions under tie-break order; mid-range results carry ~2x
   unknown error.

### Seed Viability

Not a seed for a reasoning substrate. It is a high-quality instrument and a known-answer fixture. Two components
should be carried forward:
- The gate stack (exact trap topology, sound bounded lookahead SAFE/TRAP/UNKNOWN, residual-after-known-invariant R1,
  leakage check) as a preregistered admission test for any world that claims to need "reasoning": it would detect
  shallow or invariant-explained worlds, which is exactly where most other engines' "reasoning" lives.
- NUR-001 "verify symmetry on the chart, then quotient, then search" as a primitive, together with its coverage
  contract (the run-1 bug: a table exact on every scored row navigated at ~150x oracle cost because it lacked the
  frontier pairs). Crucible-C gives a second, weaker ecology (HC 0.28). The tensor-QD lineage shows it can be inert.
- The T_7 chart + orbit table + its non-quotient-disjoint split as a regression fixture for leakage checkers.

### Evolutionary Roadmap

The engine as built has no path past wall 1; the roadmap is for the salvaged components.

1. Remove the oracle from the loop. Replace "fit to exact D" with "discover an invariant from the agent's own search
   failures". Concretely: a learner sees only (state, action, outcome after bounded search) and must propose a
   candidate equivalence relation or invariant as a program in a small typed term language (typed lambda calculus
   over maps/words, or a graph-rewriting rule language); the candidate is verified by a sound checker on sampled
   pairs (exactly what `canonical.verify` does, `canonical.py:51-74`) and adopted only if it shrinks search. Score
   it by MDL: bits(invariant program) + bits(residual search) versus bits(raw search). This turns the quotient from
   hand-written to discovered.
2. Symmetry discovery that scales: replace brute-force n! enumeration with Schreier-Sims / stabiliser-chain
   computation from observed transition generators, or with automorphism search on the observed transition graph
   (nauty-style partition refinement). These are polynomial-ish where 5040-permutation enumeration is not.
3. Universes beyond enumeration: move to T_n with n >= 10 or rewriting with L >= 16 where the chart cannot exist, and
   judge methods by verified solve rate and expansions only (every claimed path checked by the engine; the harness
   already does this), never by agreement with a chart.
4. Composition: test the quotient primitive composed with a second, orthogonal primitive (e.g. factor-first,
   NUR-006) and measure whether the product of reductions holds (compositional credit assignment: does search cost
   factor as cost(Q1) x cost(Q2)?). Without a composition result there is no circuit, only a trick.
5. Fix the denominator before any further HC_D claim: report KA under all tie-break orders (or the expectation over
   random tie-breaks) and give HC_D an interval over that order distribution.

THE decisive experiment: "invariant discovery without the chart". On T_9 (387M states, no chart), give an agent
the three generators, a budget of B = 10^7 expansions total, and 1,000 random (f, t) navigation problems with
held-out problems whose target block-size type never appears in training. The agent may propose invariants
(reachability) and canonicalisers (distance symmetry) as programs in a fixed small term language; each proposal is
checked by a sound sampler and adopted only if it lowers expansions on training problems. Success = it recovers
kernel refinement and the S_9 domain quotient (or something equivalent) and solves held-out problems at <= 2x the
expansions of a hand-coded kernel-aware + orbit-aware searcher. KILL criterion: if within B expansions it does not
recover kernel refinement (measured as: adopted invariant prunes >= 95% of the dead successors that the true kernel
prunes, with 0 false prunes) or held-out cost exceeds 10x the hand-coded searcher, the "structure replaces search"
line is closed for non-oracle settings and AC-01 is retired to fixture status.

## 5. What would change this verdict

- Upgrade to VIABLE_SEED: any committed run in which a representation not fitted to an exact chart (no D labels,
  no truth-side kernel) discovers a reachability invariant or quotient and lowers verified search cost on held-out
  problems from a target orbit type absent from training, in a universe too large to enumerate.
- Downgrade to DEAD_END: if the gate stack fails to transfer (e.g. it cannot be computed without the full chart in
  any world of interest), and NUR-001 is inert in every non-T_7 ecology tried (the nursery's own kill condition).
- Audit-level falsifiers of this dossier: if the unread survivor/gate JSON contradicts the receipt figures I tiered
  CLAIMED; if the held-target split is in fact quotient-disjoint (I inferred non-disjointness from the 6 label-aware
  target types and the 25,363/25,382 FIT orbit coverage, not from a per-row join); if any family in C1-C6 was
  trained without D labels (I read only C5 and C6 headers, both trained on D).
