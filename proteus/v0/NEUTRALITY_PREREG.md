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

---

## Run 1 — grammar v0 (`da7e2ccb…`) — FAIL. Kept as filed.

Result: `NEUTRALITY_RESULT_grammar_v0_FAIL.json`; prereg copy `NEUTRALITY_PREREG_grammar_v0.json`.
Cohort 8 grew (+0.071 instr/gen, burn-in ratio 2.77). Cohort 128 shrank (median −0.036,
last-half −0.045) and sat at its cap 8.1% of the time. Cohort 32 passed everything. Balance 1.076.

Cause, established by read-only calibration on random genomes (not on any probe result):
insertion + duplication add 0.30 instructions per generation in expectation, deletion removes
0.25, unreachable_removal 0.01–0.03; the net is +0.02 to +0.04 — a growth ratchet I had
described as "subtraction mass exceeds addition mass" because I counted operator weights, not
expected instructions. Second cause: config perturbation's tape halving clamped the tape to the
genome length, pinning genomes at their cap so insertion became a no-op while deletion did not.
Third: at start 128 the bootstrap interval half-width (0.0305) exceeded the tolerance (0.03),
so by `feedback_gate_must_exceed_measurement_error` that cohort's gate was not a gate.

## Run 2 — grammar v0.1 — preregistered here, frozen before running

Grammar changes, length behaviour only: deletion 0.10→0.11, operand_perturbation 0.20→0.19
(expected removed ≈ 0.275 + 0.01–0.03 vs. added 0.30), and tape halving is a no-op when the
genome would not fit. **Tolerances unchanged.** Lineages per cohort 30→60 so the interval
half-width falls below the tolerance at every start size. Calibrated expected drift under
v0.1 is recorded in the commit that freezes this section. Everything else identical.

If run 2 fails, the same procedure applies: keep the run, revise, re-version, re-preregister.
The number of revisions is itself reported in the packet.

## Run 2 — grammar v0.1 (`973c7c10…`) — FAIL at cohorts 8 and 128; PASS at 32. Kept as filed.

Result: `NEUTRALITY_RESULT_grammar_v0_1_FAIL.json`; prereg copy `NEUTRALITY_PREREG_grammar_v0_1.json`.
Cohort 32: slope −0.002 [−0.019, +0.014], ratio 1.015 — flat. Cohort 8: +0.041 [+0.028, +0.053].
Cohort 128: −0.028 [−0.047, −0.008], median −0.045, last-half −0.044. Balance 1.025. Every
interval half-width is now below the tolerance.

The weights are balanced away from the bounds. Both failures are bound interactions. Cohort 8
reflects off the minimum: deletion cannot go below one instruction, so near the bound expected
removal is smaller than expected insertion and a symmetric walk drifts away from a reflecting
wall. Cohort 128 sits exactly where halving a 1,024-word tape to 512 words fits its 512-word
genome exactly, so v0.1's "no-op if the genome would not fit" still lands the cap on the genome;
insertion then no-ops while deletion does not until a later doubling frees it.

## Run 3 — grammar v0.2 — preregistered here, frozen before running

One change: tape halving is a no-op unless the genome would occupy at most half of the new tape
(the cap can no longer land on the genome). Weights unchanged. **Tolerances unchanged. Design
unchanged** (60 lineages, 300 generations, starts 8/32/128).

Stated before running: cohort 8's reflection is expected to persist, because it is a property of
any bounded symmetric walk and not of these weights; a passing cohort 8 would require a
size-dependent bias, which is an authored prior. If cohort 8 alone fails, the preregistered
verdict is FAIL and the packet reports it as such; the program disposition — whether reflection
off the minimum counts as a ratchet — is the reviewer's, not this seat's. **This is the last
revision in V0.** A third failure at cohort 128 would mean the halving analysis is wrong and is
reported as such without a further fix.
