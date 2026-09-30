# Rollout fossils, tranche 2 (cross-observer) -- selection and disposition, 2026-09-30

Techne[gandalf-4c0c7e64]. Operator directive 6 s3 (2026-09-19). Input: Harmonia's native Flax column
`HARM55_FLAX_NATIVE_2026-09-30.json` (committed blob sha256 10f714c8...fbc1; HARM-55/56 closed at
68036a8ae). Selector: `techne/scripts/harm55_tranche2_select.py`, frozen at 4bdd8adc8 on 2026-09-19,
eleven days before any native score existed; one commit in its history, blob sha256 d338ecf0eabf974a...; run once,
unmodified. Output, verbatim: `ROLLOUT_FOSSILS_TRANCHE2_2026-09-30.json`.

## What the frozen rules selected

    category                                        selected   note
    D1 largest observer disagreements (top 8)          8       see below: selected by rule, not by signal
    D2 crossing -> non-crossing flips                  0       none exist
    D3 non-crossing -> crossing flips                  0       none exist
    D4 class flips                                     0       none exist
    D5 genuine organisms low under BOTH observers      8
    D6 exploits that become ordinary                   0       none exist
    D7 catalogue crossings that survive                4
    D8 catalogue crossings that disappear              0       none exist
    P1 nearest behaviour, far metric (5 pairs)         9 keys
    P2 nearest metric, far behaviour (5 pairs)         9 keys
    total distinct keys                               38       n_alive_compared 333

Every category that asks "does the observer change the answer" (D2, D3, D4, D6, D8) is EMPTY. That is
the result: across 333 alive rollouts no crossing, no class and no exploit status changes between
the original (torch) observer and ASAL's native (Flax) observer.

## D1 fired by construction, not by signal

D1 is "top 8 by |signed_diff|" with no minimum effect. The largest |signed_diff| over all 395 rows is
4.76837158203125e-07 -- float32 rounding. The 8 rollouts D1 names differ between observers in the
seventh decimal place. The rule had no INDETERMINATE branch; it should have had one ("if the largest
disagreement is below X, select nothing"). I do not add one now: the selector is frozen and its
output stands as written. I record instead that D1 carries no information on this input.

## Disposition

    already preserved (tranches 1 and 1b, 2026-09-19)   31 of 38   every D5, D7, P1 and P2 key
    new keys                                             7 of 38   all seven are D1 picks:
                                                                   S0_179 S0_222 S0_55 S1_55 S2_186 S2_187 S2_71

DEVIATION, DISCLOSED: the 7 new keys are NOT preserved as fossils in this pass. Reason: their only
selection reason is a disagreement at rounding level, so a fossil labelled "largest observer
disagreement" would assert a property that does not exist. Nothing is lost by waiting: their frames
are in both verified copies of the 395-frame set, and preserving them later is one command:

    python -m techne.fossils.preserve_rollouts --from-json <a {key: reason} file for the 7> --write --acquire

If Harmonia or the operator wants the frozen selection executed to the letter, that command does it
and I will run it; the reason string should then carry the measured magnitude.

Tranche 2 therefore adds NO new fossil. What the native column did change: the 39 existing capsules
now carry native_observer scores (`python -m techne.fossils.capsule fill-native`), where they said
PENDING since 2026-09-19. Over those 39: max |native - original| 3.5762786865234375e-07, 0 class
flips, crossings identical in 39 of 39.
