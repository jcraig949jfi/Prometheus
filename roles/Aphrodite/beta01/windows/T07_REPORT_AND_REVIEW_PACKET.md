# T07 -- R7E IMPROVER RULES ON THE ENDOGENOUS ROUTE: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 7, TEST window 7. Rung R7. Evidence tier 2. Spec: beta01/windows/T07_R7E_SPEC.md.

## 1. Dispositions
- **Technical: CLEAN.** 75 donors; 1,984 walks; about 41 min.
- **Scientific: MEASUREMENT_FAILED.** The ORACLE_UPPER gate failed: total ORACLE gain 102 < 0.9 x 115 = 103.5.
  - CONTINUITY passed (g0 reproduced T51/T06 P selections in 15/15 seeds).
  - NULL_LOWER passed (NULL 86 = g0 86).
- **Per the frozen rule, g8 and g9 are NOT read.**

**Readouts printed by the runner (NOT RESULTS; disclosed):**

| Arm | Total gain |
|---|---|
| g0 | 86 |
| g8 | 89 (sign p 0.5) |
| g9 | 74 |
| ORACLE | 102 |
| NULL | 86 |

## 2. Why the control failed: a diagnostic, and the run's main information
ORACLE offered the G1 schema as an extra candidate. Per seed (gain over PRISTINE, of 32 families):

| Seed group | ORACLE outcome |
|---|---|
| g0 starvation seeds 0, 7 (g0 derived nothing) | the planted G1 IS selected: gains 11, 5. Candidacy repaired, so the starvation limit is CANDIDACY |
| g0 success seeds (1, 2, 3, 5, 6, 8, 10, 15) | same as g0 |
| **g0 selection-failure seeds 4, 9, 12, 13, 14** | **even the planted G1 is NOT selected: gain 0 in all 5.** Yet the INHERITED G1 helps on those seeds' transfer families (T06: seeds 9, 12, 13, 14 gain 5, 2, 5, 4) |

**Reading (diagnostic, from a control arm of a frozen run):**
- In a third of natural seeds, the 4 VALIDATE families give the base class no paired saving.
- So the selector rejects even the CORRECT abstraction, while the transfer families would benefit from it.
- **The binding R3 limit on natural supply is the representativeness of the validation sample. It is not
  derivation, and it is not the selection rule's threshold:** g8's relaxed threshold (mean > 0) rescued nothing in
  those seeds.
- This is T52's finding ("selection reproduces structure shown in validation") observed in the wild.

The ORACLE gate assumed that selection would accept a correct candidate. That is false exactly where validation is
unrepresentative. **The known answer was mis-specified** (T02's lesson again): an oracle CANDIDATE is not an oracle
LIBRARY.

## 3. Endogenous-route failure anatomy (15 natural seeds; T51 + T06 + T07)

| Mode | Seeds | Lever that fixes it |
|---|---|---|
| success | 8 | -- |
| candidacy (observation starvation) | 2-3 | an oracle candidate fixes it, so better proposal or observation should |
| validation unrepresentative | 5 | not fixed by a correct candidate, nor by a relaxed threshold. It needs DIFFERENT EVIDENCE (validation breadth/content) |

## 4. Next (DEV-8)
- Repair the control: the oracle known answer becomes the oracle LIBRARY (inherited start), which already exists as
  the T51/T06 G1 START reference. An oracle CANDIDATE is reported as a diagnostic, not a gate.
- **The natural next experiment is validation breadth.** Does giving the selector more validation families (4 -> 8
  -> 12) rescue the 5 validation-limited seeds? It is improver-level (how much evidence before committing), cheap,
  and directly on the binding limit.

## 5. Attack questions
1. Are the 5 validation-limited seeds the ones whose VALIDATE families have a different top-level operator mix?
   Checkable from the roles.
2. Would a selection rule using OBSERVE plus VALIDATE evidence (g9) help? Its readout (74 < 86) was printed but is
   not readable. A post-hoc look suggests that deriving from VALIDATE hits CHANGES selections for the worse.
