# D07 -- DEV WINDOW 7 REPORT

C-006 (C-P2B-APH-BETA-01), cycle 7, DEV. Evidence tier 2.

## 1. Bottleneck after TEST-6
T06 did not confirm T51's endogenous-derivation finding at the frozen thresholds (ratio 0.644; base class derived in
3/7 seeds). It did show a sharp structure: derivation is all-or-nothing, and recovers 100% of the inherited benefit
when it occurs. The failure modes come from the donor traces of all 15 pristine donors (T51 + T06):

| Outcome | Seeds |
|---|---|
| success | 8 |
| observation starvation (1-3 families observed, 0 derived) | 3: LIN0, LIN7, LIN12 |
| selection failure (1-2 derived, none eligible) | 4: LIN4, LIN9, LIN13, LIN14 |

Both failure modes are properties of the improver's RULES. That gives a sharper and much cheaper R7 target than the
two-class world drafted in D07_R7V2_DESIGN_DRAFT.md, which stays queued.

## 2. Changes
- `gtc.py`: genomes g8 (selection eligibility mean > 0), g9 (derive also from VALIDATE hits), and the ORACLE / NULL
  planted controls. g0 path unchanged.
- `r7e.py`: the TEST-7 runner (reuses T51/T06 roles), with frozen gates and readouts. R_VAL is set to R_VAL_C1 for
  continuity with the a18_c1 donor path.

## 3. Qualification
- g0 continuity spot check: seed 3 -> (acc + {H}) and seed 12 -> None. Both are identical to T51/T06.
- The g0 conformance gate from DEV-5 (donor_g g0 == a18.donor) still holds: the g0 branch is untouched.

## 4. Next frozen experiment
TEST-7 = R7E: `beta01/windows/T07_R7E_SPEC.md`.
