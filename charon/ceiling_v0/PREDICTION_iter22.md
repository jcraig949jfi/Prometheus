# Pre-registered prediction — iteration 22, written BEFORE running any arm on F_M2

## Corrections carried in from re-analysis this iteration
1. Iteration 21 measured F_M at 10 seeds (+0.152). At 20 seeds it is +0.107 —
   an error larger than the standard error, so the earlier figure was noisy.
2. Measurement noise on the P3d-P3c gap was never estimated before setting bands.
   It is now: paired per-seed SD 0.186 (F_T) / 0.126 (F_M) / 0.064 (F_P),
   worst-case 95% CI half-width +/-0.082 at 20 seeds.
3. Re-scoring iteration 21 against that justified band:
     predictor A, log rule count  +0.240  band +0.158..+0.322  measured +0.107  OUT
     predictor B, ceiling         +0.122  band +0.040..+0.204  measured +0.107  IN
   Predictor A is REFUTED. Its iteration-21 "pass by 0.012" was an artifact of an
   unjustified +/-0.10 band applied to a noisy 10-seed measurement.

## This iteration's test
Second out-of-sample family F_M2 (two of four actions permute, so redundancy sits
between F_M's and F_P's). Structure measured first, arms not yet run.

  F_M2 measured ceiling: 0.360   (F_T 1.000, F_M 0.560, F_P 0.310)
  noncommuting action pairs: 8.0 of 16

## Prediction, predictor B only (A is refuted), 20-seed anchors
  gap = 0.284 + t*(0.021 - 0.284),  t = (ceiling - 1.000)/(0.310 - 1.000)
  PREDICTED F_M2 gap = +0.040
  band, noise-justified = -0.042 .. +0.122

## Falsifiers
  F1. Measured gap outside -0.042..+0.122. Predictor B fails
      out-of-sample a second time and compressibility is not quantitative.
  F2. Measured gap not ordered between F_M (+0.107) and F_P (+0.021), given
      F_M2's ceiling lies between theirs. Then even the ordering fails.

---

## VERDICT (written after running the arms)

  PREDICTED  +0.040   band -0.042..+0.122
  MEASURED   +0.019   SE 0.015, 20 seeds
  F1 outside band -> does NOT fire (error 0.021)
  F2 ordering: F_M2's point estimate (+0.019) sits 0.002 BELOW F_P's (+0.021),
     against an SE of 0.015. Statistically indistinguishable, so the ordering
     holds within noise, but it is NOT strictly monotone at the point estimate.
     Recorded as a partial pass, not a clean one.

## Honest limitation of this second test
The predicted gap is small and its noise-justified band SPANS ZERO
(-0.042..+0.122). A prediction that cannot be distinguished from "no effect" is a
weak test however well it lands. The F_M test was the discriminating one; this is
corroboration at low power.
