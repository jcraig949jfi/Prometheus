# T06 -- T51-C FROZEN CONFIRMATION (FRESH LIN SEEDS 8-15): REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 6, TEST window 6. Threads TH-019 / TH-018. Evidence tier 2.
Spec: beta01/windows/T06_T51C_SPEC.md (runner aced4a1a, analysis 85ade3cb, plan 35dabe7f).

## 1. Dispositions
- **Technical: CLEAN.**
  - Foundry: 1,152 families qualified.
  - Roles: 7/8 seeds fillable (seed 11 unfillable; quota 6).
  - Donors: 28.
  - Transfer: 2,240 walks.
  - 0 failures; about 1 h 33 m.
- **Gate PASSED:** inherited G1 gave a positive gain over PRISTINE in 7/7 seeds.
- **Scientific: MEASURED.**

## 2. Frozen readouts

| Readout | Result |
|---|---|
| **H1 ENDOGENOUS_DERIVATION** | **NO**: sum gain(SEL, P) = 29 vs inherited sum gain(START, G1) = 45 (ratio **0.644** < 0.70); P gain > 0 in only 3/7 seeds |
| **H2 DERIVES_BASE_CLASS** | **NO**: P selected a G1-class schema in **3/7** seeds (< 5) |
| **H3 COMPOSITION_SMALL** | **YES**: G1 SEL - START = +5 on 45 (11%) |

Per seed (gain = held-out families beyond PRISTINE, of 32):

| Seed | P selected | P SEL gain | G1 START gain | G1 SEL gain |
|---|---|---|---|---|
| 8 | (acc - {H}) | 4 | 4 | 4 |
| 9 | None | 0 | 5 | 5 |
| 10 | (acc + {H}) | 13 | 13 | 13 |
| 12 | None | 0 | 2 | 5 |
| 13 | None | 0 | 5 | 6 |
| 14 | None | 0 | 4 | 5 |
| 15 | (acc + {H}) | 12 | 12 | 12 |

- PA: SEL = START in every seed.
- G1_NC: SEL = START in every seed.

## 3. Reading
**T51's exploratory finding does NOT replicate at the frozen thresholds.** The structure behind the miss is sharp:
- **When the pristine donor derives the base class, it recovers 100% of the inherited benefit** (seeds 8, 10, 15:
  4/4, 13/13, 12/12).
- When it does not derive it (4/7 seeds), it gains nothing.

The endogenous route is all-or-nothing, and it is UNRELIABLE from 4 observed families: 3/7 fresh seeds here, versus
5/8 in T51's seeds 0-7, so 8/15 pooled (descriptive).

TH-019 (sharpened):
- Natural recurrence of the base class is present (inherited G1 helps in 15/15 seeds across T51 and T06), and it is
  visible enough to be derived about half the time.
- The limit on the endogenous route is DERIVATION RELIABILITY from small observation sets (R2/R3 for the
  endogenous route), not recurrence and not visibility at the 30k escrow.
- Composition beyond the base class is small (H3).

## 4. What this does not show
- Whether more OBSERVE families, or the adaptive observation allocation (R7 v2 genome g7), would raise derivation
  reliability. That is the obvious next lever, and it IS an improver-level (R7) change.
- n = 7 seeds.

## 5. Attack questions
1. Is derivation failure a supply property (some seeds' OBSERVE families do not share a body class) or an improver
   property (LGG needs >= 2 certified members of one class)? The trace data (n_derived, classes) can answer this
   cheaply.
2. Should the confirmation threshold have been stated conditionally ("given derivation")? It was not. The
   unconditional NO stands.

## 6. Replay
`V2B_T51_DIR=T06_T51C V2B_T51_SEEDS=8,...,15 V2B_T51_ARMS=P,G1,G1_NC,PA python t51_natural.py ...`, then
`python t06_confirm.py`.
