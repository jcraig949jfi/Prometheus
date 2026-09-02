# Neutrality gate — PREREGISTRATION (amendment A6). Frozen before any run.

**Question.** Under mutation WITHOUT selection, does the grammar carry an implicit complexity
ratchet in either direction? A grammar that grows organisms by default is an authored ladder; a
grammar that collapses them is one too, pointed the other way.

**Design.** Three cohorts by starting genome size: 8, 32, 128 instructions. Every lineage starts
with a uniformly random genome of that size on a 1024-word tape (cap 256 instructions), 8
registers, persist `none`, code not writable, tick budget 64, out cap 4. Thirty independent
lineages per cohort; 300 generations; exactly one operator per generation, chosen by the frozen
weights; splice mates are the current organism of a uniformly chosen other lineage in the same
cohort. No probe is run and nothing is scored. Config perturbation is part of the grammar and is
allowed to run.

**Measured, per cohort** (lengths in instructions):
- `slope_mean`: OLS slope of the cohort mean length over generations 0..300
- `slope_median`: OLS slope of the cohort median length over generations 0..300
- `slope_mean_last_half`: OLS slope of the cohort mean over generations 150..300
- `final_variance`: variance of lineage lengths at generation 300
- `min_occupancy`: fraction of (lineage, generation) pairs with length at the minimum bound (1)
- `max_occupancy`: fraction of (lineage, generation) pairs with length at the current cap
- `burnin_mean_ratio`: mean length over generations 150..300 divided by the start size
- pooled across cohorts, `ins_del_balance`: instructions added / instructions removed by all
  length-changing operators (insertion, duplication, splice, deletion, unreachable_removal)

**Uncertainty.** Every slope carries a 95% interval from a lineage-level (cluster) bootstrap,
2000 resamples, seeded. Per `feedback_gate_must_exceed_measurement_error`, a tolerance is only a
gate if it exceeds the interval half-width; both are reported side by side.

**Gates. All must hold for PASS. Tolerances frozen here.**
- G1 ratchet: for every cohort, `|slope_mean| <= 0.03` and `|slope_median| <= 0.03` instr/gen.
- G2 balance: pooled `ins_del_balance` in `[0.67, 1.50]`.
- G3 envelope: for cohorts 32 and 128, `burnin_mean_ratio` in `[0.5, 2.0]`, `max_occupancy <= 0.05`,
  `min_occupancy <= 0.05`. For cohort 8, `max_occupancy <= 0.05` only; `min_occupancy` is
  reported and NOT gated, because the minimum bound (1) sits within one diffusion standard
  deviation of the start and bound contact there is a property of a symmetric walk, not of a
  ratchet. Stated now so it cannot be invented after the numbers arrive.
- G4 stationarity: for every cohort, `|slope_mean_last_half| <= 0.03`.

**Interpretation, fixed in advance.**
- PASS: the grammar has no measurable ratchet at this horizon. It does NOT mean the grammar is
  neutral under selection, and nothing here says anything about diversity.
- FAIL on G1/G4 with positive slope: growth ratchet. FAIL with negative slope: collapse
  ratchet. Either way the grammar is revised, re-versioned (new `GRAMMAR_HASH`), re-preregistered
  and re-run; the failed run is kept in `proteus/v0/` and cited in the packet.
- FAIL on G2 alone: the operator weights are unbalanced even if the walk looks flat at this
  horizon; treated as a FAIL, not a note.

**What this gate cannot show.** A grammar can be ratchet-free in length and still be an authored
ladder in CONTENT (which opcodes it favours). Length is the only axis this gate measures. The
opcode-frequency drift under no selection is reported as a diagnostic without a gate.

Grammar under test: `GRAMMAR_HASH` recorded in `NEUTRALITY_PREREG.json` beside this file; the
runner refuses to run against any other grammar.
