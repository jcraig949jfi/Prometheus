# HT-e106e1603b / W5 -- design notes (generator, pass P3v2)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: speculation, plus frozen controls. No treatment code exists.

## What the world tests

M8 (critical slowing down as a noise estimator), through lens L2's idea
of an external reference. The question: does an iterative decoder's
iteration count t carry information about the realised error weight w
that the syndrome weight s does not already carry? M8's own simpler
alternative is "syndrome weight already carries everything". The world is
built so that this alternative fails cleanly if it is true: G (the share
of syndrome-only residual variance of w explained by t, out of sample)
has an honest zero (twin, measured 0.0003-0.0102) and a ceiling of 1
(cheat, 0.9996).

## Why it avoids the earlier failures

- W2 (INSTRUMENT_FAIL): its reference p* came from bit-flip decoding
  on small blocks, which has no clean threshold (per-seed p* ranged
  0.0013-0.0087, outside the spec's own window). W5 needs no threshold
  estimate: the reference is w itself, known exactly per block. It uses
  min-sum, not bit-flip.
- W2's treatment went to density 0 because single injected errors are
  always cleaned, so the dynamics never reached the regime in question.
  W5 samples p uniformly over [0.02, 0.12], so every block is drawn
  from the regime of interest.
- W1 (NULL, s95 on an integer plateau of 2): W5's statistic is a
  continuous cross-validated variance ratio, not a percentile of small
  integers.
- W1's positive control was a different system (BTW sandpile). W5's
  positive control goes through the same graph, channel, feature and
  regression code path as the treatment, with only t replaced.
- W1's twin was calibrated on a treatment statistic. W5's twin needs no
  treatment quantity: it is built from s alone.
- Positive control deliberately moderate (G ~0.28 against a threshold of
  0.20) so that attaining the threshold is shown for an effect of
  plausible size, not only for an overwhelming one.

## Ambiguities resolved

1. Target p or w? w. Under an iid channel w is sufficient for p, so any
   information t has about p passes through w; with w as the target the
   oracle MSE is 0 and G has a clean ceiling.
2. Decoder knowledge of p: forbidden. A per-block LLR set from p would
   make t leak p directly. Min-sum with a fixed LLR magnitude is
   scale-invariant, so it runs without any noise knowledge.
3. t when the received syndrome is already zero: t = 0 (features use
   log1p t). Non-convergence: t = 60.
4. Regressor: cubic polynomial in standardised s (base) plus cubic
   terms and interactions in standardised log1p t (full), least squares,
   5-fold CV with a seeded fold assignment. Chosen for determinism and
   cost; the twin value (~0.005) shows that polynomial misfit in s is
   not absorbed by a correlated second feature to any material degree.
5. "Could fail cleanly": both failure clauses are stated as numbers;
   G in [0.05, 0.20) is NULL (weak), not SIGNAL.
6. Pairing: the treatment must use make_graph(seed) and channel(cv,
   seed) from controls.py, so treatment and twin rows share graphs and
   channel draws.
7. Anti-gravity: no learned model; the "reader" of t is a fixed
   low-order regression used only to measure information, and the
   substrate is the literal code and decoder.

## Control results (control_rows.jsonl, 5 seeds)

| clause | threshold | positive | twin | cheat |
|---|---|---|---|---|
| S1 mean G | >= 0.20 | 0.280 | 0.005 | 0.9996 |
| S2 min G | >= 0.10 | 0.262 | 0.0003 | 0.9996 |

Frozen: yes. Revisions: see ATTAINABILITY.json (one, positive-control
jitter 0.10 -> 0.40; thresholds never changed).
