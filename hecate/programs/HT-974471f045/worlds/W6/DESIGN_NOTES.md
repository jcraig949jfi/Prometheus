# HT-974471f045 / W6 design notes (Pass 3 v2)

Generator prompt hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461),
bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.

## What the world tests

M14 (eidetic variation over reservoirs) through L5 (noematic invariance
under resampling) and L7 (permuted-fitness twin). This mechanism had no world
before. The readout and an input template are heritable, but the reservoir
itself is resampled at every birth (fresh recurrent W, noisy W_in), and
nothing is learned in life. If M14 holds, selection keeps readouts that
decode the target across reservoir realisations, and, because the target is
the contrast u1 - u2, the all-ones mean-field direction (the trivial
invariant the program names as the simpler alternative) cannot do it. The
observable is the L5 decomposition: a fixed readout evaluated on 20 fresh
resamples, split into its all-ones part and the rest.

It can fail cleanly: evolution may find no invariant readout (S1, F1), only
single-channel decoding (capped at corr^2 0.5, below S1), or only the mean
field (S2).

## Why it avoids the earlier failures

- W1 (SPEC_UNATTAINABLE): the positive control could not reach the
  threshold. Here it was run first: I_perp = 0.928 against thresholds 0.60,
  0.30 and 0.25 over the twin, with per-resample sd 0.024.
- W3 (NULL): its success was a contrast between two conditions that both
  carried the same pressure. W6 has no two-condition contrast; its clauses
  compare against the twin and against the trivial invariant, both measured
  in the controls (twin I_perp 0.04, twin I_ones 0.11; positive control
  I_ones 0.006).
- W1 and W3 also had clauses that referred to arms not built in the pilot.
  Here every clause is computed by `clause_values` in controls.py from rows
  of the same instrument, and the twin needs no fitness (it is neutral
  drift, equal in distribution to permuted fitness), so no treatment code
  was needed to measure it.

## Ambiguities resolved

1. "Heritable distribution": the heritable part is the input template M_in;
   the recurrent W is always fresh; the noise scale 0.3 is fixed, not
   heritable (keeps the world minimal; a heritable noise scale would let the
   distribution collapse trivially).
2. "Useful fraction outside all-ones": read as corr^2 of w_perp . x with the
   target, averaged over resamples, reported beside corr^2 of the all-ones
   readout. corr^2 is scale-free, which is needed because nothing fits an
   output scale in life.
3. Fitness uses the same scale-free corr^2 on the individual's own sampled
   reservoir for one life.
4. Elites keep their reservoir across generations (they are not re-born);
   offspring are re-sampled at birth. The instrument always resamples.
5. CHEAT: the readout output is replaced by the target (corr^2 = 1) for w
   and w_perp; the all-ones readout is measured normally. All clauses pass
   (detected).
6. The template-collapse reading (M_in grows until noise is negligible) is
   not excluded by any clause; the spec asks the implementer to record
   rms(M_in)/0.3 beside the outcome.

## Revisions before freezing

1. S1 threshold 0.40 -> 0.60 after r1, on analytic grounds: single-channel
   decoding reaches corr^2 0.5 with u1 - u2. Same rows re-evaluated.

Control CPU 2.0 s (budget 5 core-minutes).
