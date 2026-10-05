# T08 -- VALIDATION BREADTH ON THE ENDOGENOUS ROUTE: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 8, TEST window 8. Rung R3 on natural supply. Evidence tier 2.
Spec: beta01/windows/T08_VB_SPEC.md (runner 22893f93).

## 1. Dispositions
- **Technical: CLEAN.** 15 donors; 512 new walks (the rest reused from T07); about 11 min.
- **Scientific: MEASURED.**

## 2. Frozen readouts

| Readout | Result |
|---|---|
| **VB_POSITIVE** | **NO**: total gain 86 (breadth 4) -> **76** (breadth 12). Better in 1 seed, worse in 4 (sign p = 0.97) |
| **RESCUES_VALIDATION_LIMITED** | **NO**: 1 of 5 rescued (seed 13: 0 -> 7, by selecting (v - {H})). Seeds 4, 9, 12 and 14 stay at 0 |

Per seed (gain of 32):

| Seed | B4 | B12 | B12 selection change |
|---|---|---|---|
| 2 | 5 | 3 | ((acc + {H}) + v) -> (acc - {H}) |
| 6 | 8 | 0 | (acc + {H}) -> **none** |
| 8 | 4 | 0 | (acc - {H}) -> **none** |
| 10 | 13 | 10 | (acc + {H}) -> (acc - {H}) |
| 13 | 0 | 7 | none -> (v - {H}) |
| others | unchanged | unchanged | -- |

## 3. Reading
**More validation evidence from the natural pool HURTS endogenous selection.**
- The I_0 selector requires a reliably positive paired saving (lower 95% bound > 0) across all validation cells.
- The base class helps only a subset of natural families: about 27% of held-out families, beyond PRISTINE.
- Adding 8 heterogeneous natural families therefore dilutes the base class's saving, and the selector REJECTS an
  abstraction it accepted at breadth 4 (seeds 6, 8).

The 5 validation-limited seeds are not sample-size limited.

**Reframing of the natural-supply R3 limit (TH-019):** the binding constraint is the SELECTION CRITERION, not the
quantity of validation evidence. Average-saving criteria (lower95 > 0, and even mean > 0 under g8, which did not
rescue in T07) are mismatched to natural supply. There, a reusable abstraction helps a SUBSET of families strongly
and costs little elsewhere. This sharpens T52 and T07: selection reproduces structure that is shown CONSISTENTLY
across validation, and natural structure is shown INCONSISTENTLY.

## 4. Next (DEV-9)
- **Midpoint synthesis 2** (directive, after TEST 8).
- **A candidate R7 lever:** a subset-benefit selection criterion. Accept a candidate if it yields a qualified saving
  on >= k validation families with bounded total loss, rather than an average-saving bound. It is content-free and
  targets exactly the diagnosed mismatch. Its test needs a frozen design with an oracle-library reference, and a
  false-acceptance check from the NULL plant.

## 5. Attack questions
1. Is the breadth-12 harm caused by the extra families being drawn from the p <= .75 head (many of them
   PRISTINE-solvable, which gives a negative saving for any extra entry)? A head restricted to PRISTINE-censored
   families would test this.
2. Does seed 13's (v - {H}) selection transfer for a different reason (a different base class)?
