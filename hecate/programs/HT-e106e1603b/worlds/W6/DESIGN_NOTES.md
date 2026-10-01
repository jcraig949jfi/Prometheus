# HT-e106e1603b / W6 -- design notes (generator, pass P3v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: speculation, plus frozen controls. No treatment code exists.

## What the world tests

M2 (redundancy thermostat) through lens L7 (inter-failure clock). M2's
only non-trivial ingredient is that residual errors of a failed scrub
persist and couple consecutive epochs; without that it is an asymmetric
step controller parked at a failure quantile (M2's own WEAK SOC
knockout). The twin is exactly that controller: the same rule, the same
measured fresh-start failure curve, and the stored word reset after
every failure. The world fails cleanly if persistence adds no long
memory: the twin's F is about 0.09 (the controller regulates failures,
so long windows are under-dispersed), and the treatment must reach
F >= 2.

## Why it avoids the earlier failures

- W2 used bit-flip decoding and found an error floor and poorly defined
  threshold. The first W6 control run hit the same floor (Pfail 0.05-0.09
  at the highest protection level, controller pinned, positive control
  F 1.7 < 2). Revised: the protection range was extended to
  p = 0.04*0.75^s, s = 0..24 (down to 4e-5), so Pfail(s) spans about 1.0
  to 0.002 and the controller regulates inside the range.
- Protection is a noise-rate knob, not a sweep count: extra bit-flip
  sweeps stop helping after convergence, so a sweep knob gives no
  sigmoid failure curve.
- W1's integer-plateau percentile: F is a ratio of variances of counts
  over 100000 epochs, a continuous statistic.
- W1's positive control was another system. W6's positive control is
  the twin itself (same controller and curve) plus a built-in persistent
  damage state, so it must beat the same regulation the treatment faces.
- Twin needs no treatment statistic: Pfail(s) is a fresh-start substrate
  measurement with no controller and no persistence.
- The positive control was weakened from F ~32 to F ~7 so that it tests
  the thresholds with a moderate effect.

## Ambiguities resolved

1. Failure = any residual error after the scrub. After a successful
   scrub e = 0, so residue exists only after failures; the twin (reset
   after every failure) is therefore exactly Bernoulli(Pfail(s)) and is
   implemented that way.
2. Controller: +3 after a failure, -1 after 20 consecutive clean epochs,
   clipped to [0, 24]; the quiet counter resets on both. Start 12, 2000
   burn-in epochs discarded.
3. Fano windows non-overlapping, ddof=1, measured epochs only.
4. S3 compares against the FROZEN twin rows (mean 0.0854), not a rerun.
   Its treatment requirement (mean F >= 0.342) is weaker than S1's, so
   S1 is binding; S3 is kept so that "beyond the twin" is explicit.
5. The failure rate of the treatment may exceed the twin's because
   residue raises failure probability. That is part of the mechanism.
   The diagnostic arm RATE_TWIN_DIAG (memoryless, always-on added
   probability) shows a higher rate alone gives F 0.48-0.78, below S2.
   Note its rate reached ~0.021, not the positive control's ~0.03: the
   controller absorbs part of any added rate.
6. Non-stationarity and saturation are failure clauses (F2, F3), not
   silent confounds.
7. Anti-gravity: no RL agent or learned policy; the thermostat is the
   literal update rule around the literal code.

## Control results (control_rows.jsonl, 5 seeds)

| clause | threshold | positive | twin | cheat |
|---|---|---|---|---|
| S1 mean F | >= 2.0 | 7.05 | 0.085 | 10.53 |
| S2 min F | >= 1.0 | 6.41 | 0.071 | 10.03 |
| S3 mean F / twin mean F | >= 4.0 | 82.5 | 1.0 | 123 |

Frozen: yes. Revisions: see ATTAINABILITY.json (rev0-rev3; the rows
from rev0-rev2 are kept as control_rows_rev{0,1,2}.jsonl; thresholds
never changed).
