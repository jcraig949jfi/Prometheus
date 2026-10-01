# HT-974471f045 / W6 probe round 3 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v3.md (sha256 a34a8c61...1685).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md and
roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Frozen and not edited: spec.json, controls.py, ATTAINABILITY.json, control_rows.jsonl.
All output is in probe/ (rows.jsonl, OUTCOME.json). Bytecode writing is disabled
so importing controls.py writes nothing into the world directory.

## Code path

world.py imports controls.py (constants, sample_reservoir, run, corr2,
invariance, gen0_genome, constructed_genome, mutate, drift_population,
arm_stats, clause_values, THRESH) and writes probe/rows.jsonl, one flushed row
per (arm, seed). controls.main() is NOT called (it would append to the frozen
control_rows.jsonl); its per-seed body is re-executed verbatim in world.py with
the same RNG streams, so the control rows must reproduce exactly.

Arms, seeds 0..5 (the spec's 6 seeds):
- POSITIVE_CONTROL, CHEAT, NULL_TWIN: exactly controls.main's per-seed body
  (rng = default_rng(s): 5 constructed genomes then 5 gen-0 genomes; CHEAT on
  the gen-0 genomes; NULL_TWIN = drift_population(default_rng(1000+s))).
- CONTROL (spec "control"): the same 5 unevolved gen-0 genomes CHEAT uses,
  measured normally with the same instrument.
- TREATMENT: evolution under selection, rng default_rng(2000+s).
- PERMUTED_TWIN (diagnostic only, not used by any clause): the treatment code
  with a random ranking each generation (fitness still computed, ignored),
  rng default_rng(3000+s). The frozen clause S3/F2 uses NULL_TWIN, as in
  ATTAINABILITY.json.

## Treatment as implemented (spec "mechanism")

Gen 0: 20 genomes from controls.gen0_genome. Birth = controls.sample_reservoir
(fresh W at spectral radius 0.9, W_in = M_in + 0.3 xi). Life = 300 steps of
fresh U[-1,1] input (8 channels), controls.run, washout 50; fitness =
corr2(X @ w, u1 - u2). Then 60 generations: rank by fitness (descending,
stable argsort), keep the top 4 unchanged (genome, reservoir and fitness),
16 offspring each copy a parent drawn uniformly from the top 8, mutate
(controls.mutate), are re-sampled at birth and live one life. After the 60th
generation the population is ranked and the top 5 by lifetime fitness are the
measured elites; instrument = controls.arm_stats (measurement seeds
10000+100*seed+k, k = elite rank 0..4, common across arms).

## Ambiguities and readings chosen (no threshold changed)

1. Elite fitness across generations: "they are NOT re-born; their reservoir is
   kept" and fitness is "over one life". Reading: a kept elite keeps its
   recorded fitness (it is not re-evaluated on new input). Consequence: a lucky
   single life can persist; the instrument re-measures on 20 fresh resamples,
   so luck cannot enter the clause values.
2. "60 generations": gen 0 evaluated, then 60 selection+reproduction rounds
   (same count as drift_population's loop); final elites from the population
   after round 60.
3. Ranking ties: numpy stable argsort on -fitness.
4. Twin for S3/F2: NULL_TWIN (neutral drift, equal in distribution to the
   permuted-fitness twin), since ATTAINABILITY was frozen against it.
5. Outcome rule (round-1 classes, decided in evaluate.py):
   reproducibility failure -> INSTRUMENT_FAIL; positive control or cheat not
   meeting all S clauses -> INSTRUMENT_FAIL; null twin meeting all S clauses ->
   CONFOUNDED; treatment meeting S1, S2, S3 and no F clause -> SIGNAL;
   otherwise NULL (failing any S clause, or meeting F1/F2).
   Reproducibility = for each clause, attainable and discriminating recomputed
   from probe rows equal the frozen booleans (values also reported with their
   absolute difference).

## Diagnostics recorded (not clauses)

- template-to-noise ratio rms(M_in)/0.3 of the elites (spec asks for it),
  also for CONTROL and NULL_TWIN genomes;
- no-recurrence I_perp: elites re-measured on the same measurement streams
  with W set to 0 (stupid explanation 2);
- largest single-unit share of w_perp^2 (stupid explanation 3), and per-seed
  spread of I_perp;
- best/mean fitness per generation (summary) for TREATMENT and PERMUTED_TWIN.

Budget: <= 10 CPU core-minutes; threads pinned to 1 by controls.py.
