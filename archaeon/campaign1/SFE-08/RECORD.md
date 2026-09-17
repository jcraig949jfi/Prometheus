# SFE-08 -- FRANKENSTEIN CHIMERA (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-08
- question: can components (organs) from independently FAILED lineages,
  composed under explicit provenance, become useful through recombination
  -- beyond the ancestors, beyond within-lineage recombination and beyond
  random recombination? Executability alone is not synergy.
- starting commit: ac3d2d897; harness sfe08.py; organs sourced from the
  engine (SFE-01's cmp1.failures.v0 artifacts: floor genotypes of W1_d1,
  one lineage per source seed, read with the session-less reader, D-013).
- services: engine v2 (one ISOLATED world; the three composed sets as
  artifacts with per-member provenance; experiment + observation per set
  x seed).
- task T (never seen by any lineage): W2_K2, 4-bit.
- organs: aligned 2-4-instruction segments; chimera = organ(X) + organ(Y),
  X != Y (cross-lineage); shuffled_organs = same operation with X == Y
  (within-lineage); random_recomb = same operation over random genomes.
  n=100 per composed set; manifests rebuilt from genomes (L-025) with the
  same seeded ranges for every set.
- exposure: direct reuse (best member and share of members above 0.125 on
  48 held-out T episodes) and evolution seeded from the set (N=100, G=40,
  E=16, common RNG); seeds 1,2,3.
- controls: ancestors_L1/L2/L3; random_recomb; shuffled_organs (the
  cross-lineage ingredient control); executability is not scored.
- synergy rule (declared): chimera_XY exceeds max(ancestors) AND
  shuffled_organs AND random_recomb on evolved held-out in >= 2 of 3
  seeds; otherwise no synergy claim.
- assay capability: W2_K2 was reached by SFE-01's baseline in 1/3 seeds at
  N=200 G=60 and by SFE-07's failed_A-seeded search on W3_K2 in 2/3; if
  every set stays at the floor the row is INCONCLUSIVE.
- time: 18 runs x ~30 s on 12 procs; engine seconds.

## B. EXECUTION

- one engine attempt (RECEIPT.json, rows.json; 23.8 s: startup 0.54,
  exposure 17.8 on 12 procs, records 4.77, teardown 0.22; 0 errors) after a
  dry run. Lineages fetched from the TERMINATED SFE-01 source world with
  the session-less reader (D-013): L1 7, L2 64, L3 64 genotypes, hashes
  OK. Engine: 1 session, 1 world, 1 hypothesis, 3 composed-set artifacts
  (100 members each with per-member provenance: lineage, member, offset,
  length for both organs), 18 experiments + 18 observations.
- design as planned. Decisions: none new. Failures: none. Restart: n/a.

## C. SCIENCE

- primary outcomes on T = W2_K2 (direct = best member of the set on 48
  held-out episodes; evolved = elite after 40 generations seeded from the
  set; footholds = seeds with evolved >= 0.5):
    set               n    direct best per seed    evolved per seed       footholds  first-solved gen
    ancestors_L1      7    0.021 0.021 0.052       0.104 0.031 0.062      0/3        -
    ancestors_L2      64   0.094 0.073 0.073       0.104 0.500 0.292      1/3        39
    ancestors_L3      64   0.115 0.073 0.073       0.104 0.073 0.542      1/3        11
    chimera_XY        100  0.115 0.073 0.073       0.104 0.062 0.073      0/3        -
    shuffled_organs   100  0.042 0.073 0.062       0.115 0.083 0.062      0/3        -
    random_recomb     100  0.042 0.073 0.062       0.104 0.031 0.073      0/3        -
  share of members above 0.125 on direct reuse: 0.0 in every set.
- synergy rule (declared in A): chimera_XY must exceed max(ancestors) AND
  shuffled_organs AND random_recomb in >= 2/3 seeds. It exceeds none:
  chimera = shuffled = random at the floor, and the ancestors (L2, L3)
  exceed the chimeras (1/3 each).
- controls: within-lineage and random recombination (length-matched to
  the chimeras); ancestors; executability unscored.
- assay capability: YES (two ancestor sets seeded footholds; the task is
  reachable from this material at this budget).
- evidence: chimera synergy NEGATIVE. Recombining organs of failed
  lineages produced nothing beyond random recombination of random
  genomes; the useful part of the failed residue (SFE-07's finding,
  replicated here in 2 of 6 ancestor rows) is the WHOLE genotype as
  search material, not 2-4-instruction organs.
- confounders: chimeras are 4-8 instructions long while ancestors are up
  to 16 (a length confound in chimera-vs-ancestor; NOT in chimera-vs-
  shuffled-vs-random, which are length-matched and equal); the organ
  definition (aligned segments) may cut across the units that matter; n=3.
- must NOT be claimed: that recombination cannot work (only this organ
  definition on these lineages was tested); that the ancestors' footholds
  are "components" (they are whole-genome seeds).

## D. TEARDOWN

- 1 world TERMINATED (0.22 s); no orphans; clean for SFE-09: yes.

## E. BENCH IMPROVEMENT

BUGS: none. FRICTION: none new. MISSING TELEMETRY: L-027 (genome length
and opcode composition per set are not recorded beside competence, so a
length confound cannot be corrected post hoc; every set artifact should
carry a length/opcode histogram). AUTOMATION: composed sets with
per-member provenance are already machinery (24 s end to end). TO
MACHINERY: length-matched controls generated automatically for any
recombination experiment. KEEP POLICY: organ definition, task choice.
MISSING FAILURE STATE: none. MISSING RECOVERY: none. PORTABILITY: none.
OBSERVABILITY: none new.

## F. LANDSCAPE / GRADIENT NOTES

- The two ancestor footholds (L2 at generation 39, L3 at generation 11)
  vs none from any composed set is the gradient: whole failed genotypes
  carry something 2-4-instruction organs lose. An organ-length landscape
  (k = 2, 4, 8, 16 = whole) with the same controls would locate the
  length at which the useful material survives excision -- the direct
  test of "component" granularity for this substrate.
- Every direct-reuse score is at chance (share above 0.125 = 0 in all
  sets): there is no direct-reuse landscape here; only the evolved
  trajectories (trace_best per generation, recorded) carry information.

DISPOSITION: COMPLETE. Science: chimera synergy NEGATIVE (assay capable);
whole-genotype ancestors seed footholds where their organs do not.
Instrument: 0 errors.
