# TECHNE-107 results -- ASAL's open-endedness score through CLIP

Techne[gandalf-a04f7c25], 2026-09-17, M3. Preregistration: PREREG_TECHNE107_ASAL_OBSERVER_2026-09-17.md
(on main at 7f4f51f6a BEFORE the run). Receipt: TECHNE107_RECEIPT_2026-09-17.json. Instrument:
techne/scripts/techne107_asal_observer.py. Evidence frames: techne107/*_contact.png (sha256 in the
receipt). Run time 55.9 s on CPU.

## Instrument as run (deviations from the preregistration, stated)

- Observer: OpenAI CLIP ViT-B/32 via the `clip` package on torch 2.14.0+cpu (weights sha256
  40d36571..950af), not Flax: no AVX on this host. Same weights, same 224 normalisation.
- Substrate: numpy Lenia ported from Chakazul/Lenia@adfc5429 (LeniaND.py quad4 kernel and growth,
  FFT convolution, clip update), Orbium unicaudatus O2u from animals.json (sha256 09cf0a83..8d206),
  128x128 world, 256 steps, 8 frames at steps 0,32,...,224. Not ASAL's JAX Lenia.
- HUECYCLE: the preregistered "hue rotation" is a no-op on a greyscale frame, so the frame is TINTED
  with a rotating pure hue instead (structure fixed, colour moving). Recorded as a deviation.
- Orbium alive throughout: mass per sampled frame 76.9, 73.5, 73.7, 73.5, 73.4, 73.6, 73.8, 73.8,
  final 73.3; the contact sheet shows the glider crossing the world. No arm indeterminate.

## Scores (LOWER = "more open-ended"; NOISE and GARBAGE are mean of 5 seeds)

    GARBAGE     0.8167  (sd 0.0084)   8 distinct random-ellipse scenes
    HUECYCLE    0.8369               one Lenia frame, tinted with 8 hues
    LENIA       0.8472               the living Orbium rollout
    CYCLE2      0.8547               two Lenia frames alternating
    NOISE       0.8663  (sd 0.0021)  8 iid uniform-noise images
    DRIFT_SYN   0.8730               one Gaussian blob translated 6 px per frame
    STATIC      0.8750               one frame repeated (= (T-1)/T exactly)
    cheat       0.8750  8 identical images passed as distinct -> PASS (pipeline preserves identity)

Compare the embedding-space control of the morning (unit vectors, no observer): static 0.8750,
coherent drift 0.8654, two-frame cycle 0.7500, iid noise 0.0390.

## Preregistered predictions

    P1  STATIC = 0.8750                      PASS  (0.874999)
    P2  NOISE > 0.60                         PASS  (0.866); kill "NOISE < LENIA" did not fire
    P3  GARBAGE < LENIA                      PASS  (0.817 < 0.847)
    P4  STATIC >= CYCLE2 >= LENIA            PASS  (0.855); kill "CYCLE2 < LENIA" did not fire
    P5  HUECYCLE < STATIC                    PASS  (0.837); and HUECYCLE < LENIA (recorded, not predicted)
    P6  |DRIFT_SYN - LENIA| <= 0.05          PASS  (delta +0.026)
    6 of 6 pass; no kill fired; eligible arms 7 of 7.

## Reading (the distinction directive 3 asked for)

1. OBSERVER REGULARISATION is real and large for pixel noise. In embedding space iid frames
   scored 0.039; through CLIP they score 0.866, within 0.009 of a frozen image. CLIP maps noise
   images to one neighbourhood, and the score cannot see past the observer.
2. METRIC EXPLOITABILITY SURVIVES the observer for scene-level and colour-level garbage. Eight
   unrelated ellipse scenes beat the living Orbium by 0.031 (3.6 sd of the garbage arm's spread),
   and a single Lenia frame with its colour cycled beats the same frame's real dynamics by 0.010.
   The score cannot distinguish "the pattern lived and moved" from "the picture changed".
3. The whole dynamic range through CLIP is 0.817-0.875: 0.058 wide. The embedding-space range
   was 0.836 wide. CLIP compresses the metric's incentive by an order of magnitude but does not
   remove its direction: dissimilar-looking frames win, whatever produced them.
4. Recurrence (CYCLE2) scores WORSE than life through CLIP (0.855 vs 0.847), the reverse of the
   embedding-space control (0.750 vs 0.865): two alternating frames keep re-hitting an earlier
   frame with similarity ~1, which the max-over-earlier-frames term punishes. The numpy
   "recurrence masquerades as open-endedness" reading therefore does NOT transfer; it was an
   artefact of orthogonal synthetic vectors.
5. A moving blob and the Orbium are within 0.026 (P6): the score does not know life from
   translation.

What this does NOT show: anything about ASAL's optimiser or its published discoveries; whether
an optimiser driving Lenia parameters would find garbage or life (ASAL's search space is Lenia
parameters, not free images, so scene-level garbage may be unreachable there -- that is the
substrate-side control the morning packet named and it remains open). One pattern, one world
size, one seed for the deterministic arms.

## Falsifiers left standing

- The same seven arms under ASAL's Flax CLIP on a host with AVX, different by more than 0.01
  on any arm: the torch port is not the observer ASAL used.
- A Lenia PARAMETER search (ASAL's actual search space) that never produces a rollout scoring
  below the Orbium: exploitability is a property of free images, not of the substrate ASAL
  searches.
- Orbium at a larger world or another pattern scoring below GARBAGE: one pattern is not Lenia.

Cost: one isolated env (torch 2.14 CPU, clip, ~1 GB with weights), 56 s of compute, no operator
decision consumed. Conflict of interest: unchanged from the preregistration; P2 bit against my
wish and passed, P4's kill reversed my morning reading and is reported as such.
