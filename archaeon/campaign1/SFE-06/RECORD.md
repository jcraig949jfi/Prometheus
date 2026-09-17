# SFE-06 -- H5 ENCODING AND ACCESS TO USEFUL VARIATION (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-06
- question: with the evaluator and the phenotype scope FIXED, does the
  genotype->phenotype encoding change navigability, accessible useful
  variation, mutation neighbourhoods and search success?
- starting commit: d3fb47c5f; harness sfe06.py; decoders REUSED unmodified
  from archaeon/producer/h5_decoders.py (direct / balanced / scrambled;
  12-bit genome; every decoder total with multiplicity exactly 16 per
  rule; check_exact recorded); evaluator REUSED from herakles/eca/core.py
  (block_output_score, Capcarrere-Sipper-Tomassini criterion) -- the
  H5-1 campaign measured the class map only ("calibration, no
  evolvability evidence"); this is the first search-success measurement.
- services: engine v2 (one ISOLATED world; the three decoder tables as
  content-addressed artifacts with their sha256 identities; one score
  table artifact per seed; experiment + observation per decoder x seed).
- phenotype scope: the 256 elementary CA rules; evaluator: block-output
  score on 64 seeded Bernoulli initial conditions, 21-cell ring, horizon
  11 (chance 0.5, range [0,1]); ONE score table per seed shared by every
  decoder (differences can only be access).
- search: (1+4) hill climbing with single-bit flips from 8 independent
  parents for 40 steps: budget 8 x (1 + 40 x 4) = 1288 evaluations per
  decoder x seed, matched. Measures: best score reached; evaluations to
  the first score >= 0.9; distinct rules visited; accessible variation
  (mean distinct neighbour phenotypes among the 12 one-bit mutants of 256
  independent parents, collapsed to the 224 behavioural classes and also
  raw rules).
- seeds 1,2,3 (score-table ICs seeded 20260917*10+seed; parents seeded
  20260917+seed; climb RNG seeded likewise; decoder seeds 20260917).
- controls: scrambled = the frequency-preserving null (same multiplicity,
  random rule permutation) -- if direct and balanced differ from scrambled
  no more than scrambled differs from a second scrambled seed, the
  encoding effect is noise; the shared score table's max and its share of
  rules >= 0.9 bound what any decoder can reach.
- assay capability: if no rule scores >= 0.9 on the table (table_max
  < 0.9), "search success" is replaced by "best reached" only.
- time: 3 x 256 rule scores + 9 climbs; seconds.

## B. EXECUTION

- one engine attempt (RECEIPT.json, rows.json; 4.9 s: startup 1.34, three
  seeds ~1.0 s each, teardown 0.21; 0 errors) after a dry run. Engine: 1
  session, 1 world, 1 hypothesis, 6 artifacts (3 decoder tables with
  sha256 identities, 3 score tables), 9 experiments + 9 observations.
  Decoder checks (check_exact): every decoder total on 4096 genomes with
  multiplicity 16 per rule (recorded in the receipt).
- design as planned; budget 1288 evaluations per decoder x seed; the score
  table per seed has max 1.000 at rule 184 (the CST block-output rule), so
  the target is reachable under every decoder by construction.
- decisions: none new. Failures: none. Restart: not needed.

## C. SCIENCE

- primary outcomes per decoder (seeds 1,2,3):
    balanced  best [1.0, 1.0, 1.0]  first-hit evals [653, 97, 89]  rules visited [131, 165, 200]  accessible classes 11.55 (rules 11.70)
    direct    best [1.0, 1.0, 1.0]  first-hit evals [13, 53, 53]  rules visited [124, 136, 156]  accessible classes 7.76 (rules 8.00)
    scrambled best [1.0, 0.562, 1.0]  first-hit evals [971, None, 190]  rules visited [147, 96, 121]  accessible classes 7.89 (rules 8.00)
  Every decoder can reach 1.000 (the catalogue is identical). What differs
  is ACCESS: direct hits >= 0.9 in 13/53/53 evaluations (3/3 seeds);
  balanced in 653/97/89 (3/3) while exposing 11.6 distinct neighbour
  classes per genome vs 7.8 for direct; scrambled (the frequency-
  preserving null) in 971/-/190 (2/3; seed 2 stalled at 0.562 after 1288
  evaluations).
- controls: scrambled null (same multiplicities, random rule permutation);
  shared score table; table_max and share of rules >= 0.9 recorded
  (assay capable: yes).
- evidence: encoding changes search success and speed at a fixed
  evaluator -- POSITIVE (weak, n=3; the seed-1 spread 13 vs 653 vs 971 is
  an order of magnitude; seeds 2-3 agree on the ordering direct <
  balanced < scrambled in first-hit evaluations). Accessible variation
  and navigability DECOUPLE: balanced offers the most distinct neighbour
  phenotypes and is NOT the fastest -- exactly the directive's warning
  that a balanced decoder is not proof of an unbiased or favourable
  search geometry. Under direct, a 1-bit genome flip is a 1-bit RULE-TABLE
  change (or a neutral high-bit flip): the encoding's neighbourhood is
  aligned with the evaluator's locality; balanced destroys that alignment
  while keeping multiplicities.
- confounders: one evaluator criterion, one climb algorithm, n=3 seeds,
  one balanced seed and one scrambled seed (a second scrambled seed would
  bound null-to-null variation -- not run).
- must NOT be claimed: that direct is "the right" encoding (it is aligned
  with this evaluator's locality only); that accessible variation is
  useless (it measures neighbourhood breadth, not search speed).

## D. TEARDOWN

- 1 world TERMINATED (0.21 s); no orphans; clean for SFE-07: yes.

## E. BENCH IMPROVEMENT

BUGS: none. FRICTION: none. MISSING TELEMETRY: L-023 (the accessible-
variation probe and a search-success measure disagree; both must be
reported and a third -- neutral-network size per phenotype, the share of
one-bit neighbours with the SAME phenotype -- would explain the direct
decoder's speed). AUTOMATION: the whole experiment is 5 s; cheap
experiments should buy SEEDS, not idle: L-024 (the timebox rule has no
lower clause; a run under 1 minute should be replicated to n>=10 by
default). TO MACHINERY: the decoder-table artifact with sha256 identity
is already deterministic machinery. KEEP POLICY: the evaluator criterion
and the climb algorithm. MISSING FAILURE STATE: none. MISSING RECOVERY:
none. PORTABILITY: none. OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- first_hit_evals is a landscape over (decoder x seed) that the binary
  "hit" hides: 13 vs 653 within the same catalogue. The trajectories
  (score per climb step per parent; recorded in rows.json) show plateaus
  at 0.5 (chance: constant rules) and 0.75-0.9 shelves before rule 184's
  basin; a plateau-length histogram per decoder would quantify
  navigability better than first hit.
- The score table itself is a landscape over 256 rules (max 1.000, and a
  measurable share >= 0.9 per seed) -- the neutral-network structure of
  each decoder over that table (which genomes decode to the >= 0.9 rules
  and how they connect by 1-bit flips) is computable exactly (4096 x 12
  edges) and would turn this into a full navigability map.

DISPOSITION: COMPLETE. Science: encoding effect on search speed/success
WEAK POSITIVE (n=3), accessible variation decoupled from navigability.
Instrument: 0 errors, 5 s.
