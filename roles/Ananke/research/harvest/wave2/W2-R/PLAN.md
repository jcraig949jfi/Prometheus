# W2-R plan (written 2026-10-01 ~01:40Z, BEFORE any champion was classified or evaluated)

## Task 1: does the noise-cancelling bonus (W2-A1 F4) shape real C1 champions?

Mechanism under test: search.py f = acc + .10*max(sens_act,0) + .02*sens_any; sens_act is sign(S0_lead - S0_twin)*y
averaged over readouts; twins share the payload NOISE draw (engine.py noise hash keyed on ws,t,site), and twin
inputs are negated. A readout linear in the comm path cancels the noise in the twin difference -> sens_act ~ 1
at chance accuracy. A thresholded readout gives sens_act ~ 2*acc-1. Noise is on PAYLOAD only (SENSE is clean).

Population: all 678 C1 evolve rows (waves A, B, B2, C, D, E). SIGNAL = labels.SIGNAL (held lo99 > .55);
NULL = not SIGNAL.

Static classification (no compute): unroll the readout-site program 4 ticks (S registers loop-carried, T/EMIT/PAY
zeroed each tick, as in engine.py), forward-taint registers from inputs (SENSE, IN*, CNT*), backward-slice the last
definition of S0, and keep the "signal ops" in the slice (ops with >= 1 tainted source). Per rule:
- THRESH: a signal op is GT, or SEL whose condition (old dst) is tainted;
- LINEAR: signal ops only MOV/ADD/SUB/ADDI/SHR, MULQ with exactly one tainted operand, SEL with untainted condition;
- NONLIN: MAX/XOR/MOD/RAND or MULQ with two tainted operands, no GT;
- NOINPUT: S0's slice never reaches an input.
Multi-rule genomes: classify each rule; report the set (rule at the readout site is hash-drawn per world).
Also record whether the S0 slice reaches IN/CNT (comm) or only SENSE (local).
Known blind spots: WIMM/Kp immediates, SETRULE switching, clamp saturation as an implicit threshold.

Dynamic classification: S0 at scored readouts on 8 fresh worlds: number of distinct values, mass on the top-3 values,
|S0| quantiles. Plus acc, sens_act, sens_any via an exact copy of assays.evaluate (CPU, eager), and the excess
X = sens_act - max(0, 2*acc - 1) (the bonus paid beyond what accuracy explains).

PREDICTION (registered here before looking):
- P1. Under noise > 0, NULL champions are disproportionately LINEAR (vs NULL champions at noise 0, and vs SIGNAL
  champions at the same noise), and those LINEAR NULL champions have high sens_act (>= .5) at chance accuracy,
  i.e. large X.
- P2. SIGNAL champions are predominantly THRESHOLDED, at every noise level.
- P3. At noise 0, the linear/threshold split of NULL champions does not differ from noise>0 by much (the bonus is
  only noise-blind when there is noise).
Falsifiers: P1 fails if the LINEAR fraction among NULL champions at noise 64 is not higher than at noise 0 (with a
Fisher test as a guide, not a gate), or if LINEAR NULL champions at noise > 0 do not have higher sens_act than
THRESH NULL champions. Note the champion is picked by accuracy only from the final population, so the bonus can act
only through the population; a null here does not refute F4, it bounds its effect on the recorded champions.

## Task 2: timing slack left by the GA

Champions: D-wave evolve (24) + E-wave evolve (5) + D adjudicated genomes (12, dedup by genome hash) + top 20
SIGNAL evolve champions by held acc (dedup). For each: native, lat_base -1/+1/+2 (where valid), env delta
-2/-1/+1/+2 (not HOLD: delta is inert there), one change at a time.
Discovery: 16 pairs (32 worlds) fresh seeds, paired against native on the same seeds.
Confirmation (winner's curse): the best variant per champion re-run against native on a second disjoint 16-pair set;
"out of tune" = confirmed paired gain >= .03.
Interpretation against the selector ceiling (W2-D F7: selection at M=8 cannot resolve differences below ~.57).
Note: lat_base and delta are physics/task changes, not genome changes; they measure how far the mechanism's timing
sits from the cell's timing, not a gain a single mutation is guaranteed to reach.

## Compute
Cap 0.5 CPU core-hours, CPU only, 2 threads, eager. Benchmark first; scale worlds down if needed.
