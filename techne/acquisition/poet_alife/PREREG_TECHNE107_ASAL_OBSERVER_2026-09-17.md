# PREREGISTRATION -- TECHNE-107: does CLIP regularise ASAL's open-endedness score, or does the metric's incentive survive the observer?

Techne[gandalf-a04f7c25], 2026-09-17, M3. Committed BEFORE any image is embedded. Operator
directive 3: "distinguish metric exploitability from CLIP-induced semantic regularization;
include cycle, noise, coherent drift, and actual Lenia."

## The instrument, frozen

- Score: ASAL calc_open_endedness_score (SakanaAI/asal@677ba0ea, asal_metrics.py:53), re-
  implemented in numpy: kernel = z z^T; lower triangle k=-1; per-frame max; mean; LOWER = more
  open-ended. T = 8 frames, D = 512.
- Observer: openai/clip-vit-base-patch32 image features, L2-normalised, exactly as
  foundation_models/clip.py embed_img() (224x224, CLIP mean/std normalisation) but through the
  PyTorch CLIPModel instead of Flax (same weights; M3 has no AVX so jaxlib cannot load).
  Torch/transformers versions and the weights' sha go in the receipt.
- Substrate for the real arm: Lenia in numpy (Chan 2019), Orbium pattern and kernel/growth
  parameters from Chakazul/Lenia@adfc5429 Python/animals.json (sha256 in the receipt), 256
  steps, frames sampled at T//8 spacing like rollout.py time_sampling=8, rendered greyscale ->
  RGB at 224. ASAL's own JAX Lenia is NOT used (no AVX on this host); the receipt says so.
- Every arm is 8 images of 224x224x3 in [0,1]; nothing else differs between arms.

## Arms (8 frames each)

  LENIA        the Orbium rollout (coherent drift of a real pattern)
  STATIC       frame 0 of LENIA repeated 8 times
  CYCLE2       two distinct LENIA frames (0 and 4) alternating
  NOISE        8 independent uniform-noise images
  GARBAGE      8 distinct synthetic scenes (random ellipses, random colours, seed-fixed):
               "novelty-looking garbage"
  HUECYCLE     LENIA frame 0 with a different hue rotation per frame (structure fixed, colour
               moving)
  DRIFT_SYN    one synthetic blob translated a few pixels per frame (coherent drift without life)

## Predictions (fixed before the run; each with its kill)

  P1  STATIC = 0.8750 exactly ((T-1)/T x 1.0). Kill: anything else means the metric port is
      wrong; stop.
  P2  NOISE scores ABOVE 0.60 (CLIP maps iid noise images to a tight cluster; the observer
      regularises the embedding-space pathology). Kill: NOISE < LENIA means CLIP does not
      regularise at all and the numpy pathology transfers whole.
  P3  GARBAGE scores BELOW LENIA (distinct scenes are "more open-ended" than a living pattern):
      metric exploitability SURVIVES the observer. Kill: GARBAGE >= LENIA means CLIP's semantic
      regularisation defeats the exploit for this class; the "novelty-looking garbage" reading
      is dead for scene-level garbage.
  P4  CYCLE2 scores BETWEEN STATIC and LENIA (recurrence masquerades as some open-endedness).
      Kill: CYCLE2 < LENIA means recurrence beats coherent life outright.
  P5  HUECYCLE scores BELOW STATIC. No prediction relative to LENIA (recorded either way).
  P6  DRIFT_SYN scores within +/-0.05 of LENIA (CLIP cannot tell a living drift from a moving
      blob at this metric). Kill: |DRIFT_SYN - LENIA| > 0.10 either way.

Eligible count: 7 arms x 1 seed for the deterministic arms; NOISE and GARBAGE get 5 seeds
each and report mean +/- sd. Indeterminate branch: if CLIP fails to load or the Orbium
pattern dies before step 256 (blank frames), the LENIA arm is INDETERMINATE and P3/P4/P6 are
not read.

## Controls

  positive  P1 (a known value the instrument must reproduce)
  cheat     an arm of 8 IDENTICAL images passed as "8 distinct" must score 0.8750; if the
            pipeline resizes or normalises per-frame in a way that breaks identity, it is caught
  negative  none beyond STATIC; a negative control on CLIP itself is out of scope

## What this does NOT test

ASAL's optimiser, its supervised/illumination scores, or any claim in the ASAL paper about what
its search finds. Only: what the open-endedness SCORE rewards once images pass through CLIP.

Conflict of interest: I wrote the numpy control that motivated this and would like it to
generalise; P2 is written to bite against that wish.
