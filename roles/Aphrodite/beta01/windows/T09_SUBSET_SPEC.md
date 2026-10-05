# T09 -- SUBSET-BENEFIT SELECTION CRITERION (R7) ON THE ENDOGENOUS ROUTE (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 9. Frozen in DEV-9, 2026-10-05. Rung **R7** (an improver-rule change), aimed at the
R3 limit diagnosed in T07/T08. Threads TH-019 / P2. Evidence tier 2.

## 1. Question
I_0 selects a candidate only if its paired saving has lower95 > 0 pooled over ALL validation cells. On natural supply
a reusable abstraction helps a SUBSET of heterogeneous families. T07 showed a correct candidate rejected in 5/15
seeds; T08 showed more validation making this worse.

**Does a content-free SUBSET-BENEFIT criterion (g10), applied by a pristine improver with no library carried, raise
endogenous reuse on fresh natural supply?**

g10 (gtc._select_subset): per VALIDATE family f, s_f = the mean paired saving over f's cells; G = sum of positive
s_f; L = -(sum of negative s_f). A candidate is eligible iff some s_f >= 1000 charges AND L <= G. The choice is the
max (G - L). The rule is unit-tested on synthetic cells: a large single-family saving outweighed by larger losses is
rejected, and a sub-threshold saving is rejected.

## 2. Design
- **Seeds:** the 15 T51/T06 seeds, with OBSERVE 4 and TRANSFER 32 unchanged. Escrow 30k; PRISTINE start (kind P);
  R_VAL as T51.
- **VALIDATE:** a FRESH breadth-12 draw: the original 4 + 8 extras, seeded `APHRODITE/T09/VAL/<seed>`.
  - The extras EXCLUDE all T51/T06 role families AND T08's extras.
  - **Disclosure:** a DEV-9 diagnostic computed G1-vs-PRISTINE per-family savings on T08's breadth-12 families.
    Those families are excluded here so that T09's validation draw is unexposed. Supply: 8/8 fresh extras in 15/15
    seeds.
- **Arms:**
  - g0 (I_0);
  - g10;
  - ORACLE10 (G1 planted under g10): DIAGNOSTIC ONLY (T07 lesson: an oracle candidate is not an oracle library);
  - NULL10 (OFF planted under g10): GATE.
- **Endpoint:** gain = families of the 32 TRANSFER families where SEL reaches a T4-v1a-qualified program at <= 1M in
  >= 1 of 2 cells AND PRISTINE is censored. T07's cells are used, and PRISTINE walks are reused.
- **Files:** gtc.py sha256 e097e1d4...; t09_subset.py sha256 d48b8dbf....

## 3. Measurement gate
NULL10's planted OFF schema must be selected in <= 2/15 seeds, AND total NULL10 gain <= total g10 gain + 2.
Otherwise MEASUREMENT_FAILED (g10 accepts junk).

## 4. Frozen readout
**R7_SUBSET_POSITIVE:** a one-sided paired sign test over seeds of gain(g10) vs gain(g0), both at the fresh breadth
12, gives p < 0.05 AND total gain(g10) > total gain(g0).

Also reported:
- the validation-limited seeds rescued by g10;
- the number of seeds where ORACLE10 accepts the planted G1;
- descriptively, the g10 total vs T07's g0 total at breadth 4 (86).

## 5. Interpretation (frozen)

| Result | Reading |
|---|---|
| R7_SUBSET_POSITIVE | **first observable R7 (tier 2):** a content-free change to the improver's SELECTION RULE, carried into fresh natural supply with no library, makes it acquire more reusable improvement. It is still first-order (not R8) |
| NOT positive, gate passed | the selection criterion is not the only limit. Remaining limits are candidacy (starvation) and validation content (e.g. seed 12: no validation family rewards the base class even at breadth 12) |
| Gate failed | the subset criterion admits junk; nothing is read |

## 6. Compute and scheduling
60 donors (about 3 min each at breadth 12) plus new walks: about 4 core-h. **The seat's rolling 24 h usage is about 47.8
core-h at 01:35Z.** TEST-9 therefore opens with a COMPUTE HOLD and launches once the 12:01-14:43Z (2026-10-04) T53
block rolls off: from about 12:45Z, 2026-10-05. This is a resource cap (R2), not a scientific gate.
