# W6: design notes (Pass 3 v2 generator, HT-faa9277e02)

Prompt: hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...bd461).
Bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.
Layer: implemented candidate design only. No treatment (plastic) code exists
and none was run. Every number below is from control constructions.

## What the world tests

M6 (neighbour-consensus repair) via lens L5 (wound-bit accounting), with M1
supplying the Hebbian coupling rule. The medium's activator couplings were
shaped by Hebbian co-activity while the spot pattern formed. The question is
whether that medium regrows the original pattern inside a large lesion better
than two comparisons do:
- the same medium with the couplings inside the lesion scrambled (the null
  twin: border intact, coupling values intact, stored arrangement destroyed);
- an unwritten uniform medium (the control: pure border pinning).

This attacks directly the program's standing anomaly, "border pinning may
explain both recall and repair". Of the two new worlds, it is the one that
could fail most cleanly. The Hebbian rule of M1 raises g on hot-hot edges and
drives cold-cold edges toward the clip. That is not the carving that worked
as a positive control (only boundary edges cut, everything else 1). So a NULL
is a live possibility and would be informative.

## Why it avoids the earlier failures

- **W1 (full-field recall from fresh noise; positive control r = 0.28 < 0.7).**
  W6 does not ask the medium to re-create a pattern from nothing. It asks for
  repair with the rest of the pattern intact, and the positive control was run
  through the real dynamics before any threshold was set:
  - positive control RIF 0.381, against a threshold of 0.25;
  - twin 0.056;
  - FIXED 0.145.
- **W1 "boundary pinning makes any run reproduce stripes".** A torus (no edges)
  replaces the open grid. Rev 0 showed that border pinning from the lesion
  rim is strong: a 16x16 lesion with 0.01 noise was repaired better by the
  unwritten medium (r = 0.86) than by the positive control. The lesion was
  enlarged to 24x24 (about 3.6 wavelengths) and the lesion noise raised to 0.3,
  so the interior nucleates before the rim front arrives. FIXED then drops to
  RIF 0.145. A treatment-vs-FIXED clause (S3) makes border pinning an explicit
  competitor, not a hidden floor.
- **W1 A1 (cheat undetected because a positive-control clause was folded into
  success).** No clause mentions the positive control. The cheat passes S1-S4
  and fires no failure clause.
- **W2 (twin already near the bound).** Discrimination is measured, not
  assumed. Twin values are 0.056 RIF and 0.013 for twin-minus-its-twin, and it
  beats its twin in only 5 of 10 seeds.
- **Pearson r inflated by the shared wavelength (W1).** The observable is
  RIF = I(O_bin; R_bin) / H(O_bin) inside the lesion. It is normalized by the
  entropy of the original inside the lesion, so sparse maps cannot score by
  agreement alone. Raw agreement stays high (0.79) for the twin and is kept
  only as a diagnostic.

## Revisions before freezing (full detail in ATTAINABILITY.json; rows in revisions/)

| Rev | Change | Result | Why changed |
|---|---|---|---|
| 0 | L = 16, noise 0.01, core_low carving, raw bits | Border pinning dominates | Enlarge lesion, raise noise |
| 1 | RIF observable; grid of L x noise; core_high | Too little separation from FIXED | Try carving strength |
| 2 | Carving variants | Boundary-only cut (0.1) best | Frozen |
| 3 | Final file, second twin draw, evaluator | Frozen | |

Thresholds were set after rev 2 from the control values, strictly between the
positive control and the twin and FIXED. No treatment value exists, so no
threshold could have been fitted to one.

## Ambiguities resolved

1. **Plasticity schedule.** Plasticity is on only in Phase A (3000 steps). It
   is off during settle and regrowth, so the couplings act purely as memory
   and the lesioned pattern cannot rewrite them during repair.
2. **Original O.** The settled map after 1500 non-plastic steps on the final
   couplings. This is the same step for the treatment and the positive
   control, so O is consistent with the couplings it is compared under.
3. **Lesion.** 24x24 at a seed-random position, wrapping on the torus. a and h
   are reset to 1 + 0.3*N(0,1) (floored), with a fresh RNG stream. All arms of
   a seed share the lesion and its noise.
4. **Null twin scope.** Only edges with both endpoints inside the lesion are
   permuted; border-crossing edges are kept. This makes the twin a pure test of
   stored arrangement inside the lesion, with border pinning fully present.
5. **Control pairing.** FIXED shares the seed's initial noise, lesion and
   lesion noise, but its original pattern formed on g = 1. So its O differs
   from the treatment's O. S3 is paired by seed and lesion, not by pattern.
6. **Binarization.** Each map is binarized at its own whole-field mean (not
   lesion-only), so the threshold is not affected by the lesion content.
7. **Twin in the arm slot.** For relative clauses, a second independent
   permutation (NULL_TWIN_B) serves as the twin's twin.
8. **Seeds.** 10, paired. Clauses use seed means and seed counts, with no
   p-values.

## Budget

Control runs took about 122 CPU-seconds in total over revs 0-3 (4 exploratory
variants were run in parallel). This is under the 5 core-minute cap.
