# T04 -- T51 NATURAL-RECURRENCE DONOR STAGE: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 4, TEST window 4. Thread TH-019 (recurrence x visibility). Evidence tier 2.
Spec: beta01/windows/T04_T51_SPEC.md (runner 27d46868, plan c7809d25).

## 1. Dispositions
- **Technical: CLEAN.**
  - Foundry: 1,152 families qualified at escrow 30k.
  - Supply gate: roles fillable for 8/8 seeds (quota 6).
  - Donors: 56/56.
  - Transfer: 4,480 / 4,480 exact walks at cap 1M; 0 evaluator disagreements.
  - Wall time: about 2 h 16 m on 4 M4 workers.
- **Scientific: MEASURED.**

## 2. Frozen readouts

| Readout | Value |
|---|---|
| Points (8 seeds x 5 panel schemas) | 40 |
| Realised X_S range | 0.661 |
| Pooled OLS slope of normalised distinct-class reuse on X_S | **+0.107** |
| Seed-clustered permutation p (one-sided) | **0.159** |
| **NATURAL_DOSE_SLOPE** | **NOT_SHOWN** |
| G1 residuals above the pooled line | positive in 1/8 seeds |
| **G1_SPECIFIC** | **NO** |

Distinct-class reuse over own START, summed over seeds:

| Arm | Reused classes |
|---|---|
| G1 | 5 |
| PA | 14 |
| PB | 2 |
| PC | 1 |
| PD | 6 |
| **P (control)** | **37** |
| G1_NC (control) | 0 |

**Frozen-table reading:** reuse exists but does not track the natural composition-recurrence dose over the realised
range. G1 is not privileged. The live control P reuses MORE than any panel arm, so inheritance + composition is not
what produces the reuse measured this way.

## 3. Diagnosis (EXPLORATORY, post-hoc; beta01/runs/T04_T51/T51_EXPLORATORY_VS_PRISTINE.json)
**What did P select?** On natural lineage supply, the PRISTINE-start donor (no inherited schema; composition has
nothing to wrap, so its candidates are LGG-derived only) selected:
- `(acc + {H})` in seeds 3 and 6;
- `(acc - {H})` in seeds 1 and 5;
- `((acc + {H}) + v)` in seed 2;
- nothing in seeds 0, 4 and 7.

**It derived G1 itself, or a re-expression of it, from the families it observed.** Because the frozen metric counts
reuse over each arm's OWN start, arms that already inherit G1 have little left to gain.

Absolute view: families (of 256 transfer families per arm) where the library qualifies within 1M AND PRISTINE is
censored:

| Arm | START vs PRISTINE | SEL vs PRISTINE |
|---|---|---|
| G1 (inherits G1) | 70 | 77 |
| G1_NC | 70 | 70 |
| PA ({H} + v) | 48 | 68 |
| PB, PC, PD | 0-2 | 3-6 |
| **P (pristine; derives)** | **0** | **57** |

**Sharpened TH-019 statement (tier 2; exploratory analysis of a frozen run; it is a hypothesis for confirmation,
not a frozen result):**
- On LIN lineage supply, about 27% of held-out families (70/256) lie beyond PRISTINE's 1M reach but within reach of
  the additive-accumulation class (G1).
- A pristine improver DERIVES that class endogenously from 4 observed families, and recovers about 80% of the
  inherited benefit (57 vs 70).
- Composition on top of an inherited schema adds little: G1 +7, PA +20, the rest about 0.
- The per-schema composition-recurrence dose X_S does not predict reuse (slope n.s.).

In this world, natural recurrence IS present AND visible for the dominant class, but what is reused is the
endogenously derivable base class, not compositions built on an inherited stepping stone.

## 4. What this does not show
- The P-vs-panel contrast in s2 is partly a baseline artefact: each arm is measured against its own START. The
  absolute view (s3) corrects for that but is post-hoc.
- 8 seeds; permutation p = 0.16. A small dose effect is not excluded ("not detectable at this scale").
- The tier-2 local engine only.

## 5. Ladder position (TH-019)
| Rung | Status |
|---|---|
| R0-R2 | natural recurrent structure is representable and findable (P derives G1 class in 5/8 seeds) |
| R3 | selected by a pristine donor's paired selection |
| R4-R5 | reused on about 22% of held-out families (57/256) beyond PRISTINE reach |
| Compounding beyond the base class (composition on an inherited stone) | weak: +7 to +20 families |
| R7 | not addressed: the improver is immutable |

## 6. Next
- **DEV-5:** the mid-campaign synthesis (directive), and the R7 improver-mutability probe (GTC) design.
- Candidate confirmation: a frozen, pre-registered test of the s3 absolute endpoint on fresh LIN seeds 8-15. It
  would ask whether endogenous derivation recovers >= 70% of the inherited benefit.

## 7. Attack questions
1. Is the frozen metric (reuse over own START) the wrong estimand for natural supply? Should the pooled slope be
   re-specified on the absolute vs-PRISTINE endpoint (fresh seeds only)?
2. Does P's derivation of the G1 class depend on T4's G1 enrichment (W1 s5 smuggling level iv)?
3. Why does PA gain +20 from selection while G1 gains +7? Is ({H} + v) closer to the natural composition supply?

## 8. Replay
`python t51_natural.py report`, using the committed plan, foundry, roles, donors, index and walks.
