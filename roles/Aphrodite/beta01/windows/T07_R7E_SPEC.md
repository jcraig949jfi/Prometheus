# T07 -- R7E: IMPROVER-RULE CHANGES ON THE ENDOGENOUS ROUTE (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 7. Frozen in DEV-7, 2026-10-05. Rung **R7 IMPROVER_CHANGED**. Threads TH-019 / P2.
Evidence tier 2.

## 1. Question
On natural lineage supply, a pristine improver (no inherited library) derives and reuses the base class in only about
half the seeds:
- T51: 5/8;
- T06: 3/7;
- when it succeeds, it recovers 100% of the inherited benefit (T06).

Its failures, from the traces (DEV-7):
- observation starvation: 3/15 seeds, with 0 schemas derived;
- selection failure: 4/15 seeds, where schemas were derived but none was eligible.

**Does a CONTENT-FREE change to the improver's rules, carried into the same fresh supply with NO library, raise what
it derives and reuses?** A positive is a change to the machinery that generates improvements, not to stored data,
because no library crosses (W4 P-C reset).

## 2. Design
- **Seeds:** 15. T51 roles for LIN 0-7, and T06 roles for LIN 8-15 (seed 11 unfillable). These are the already
  qualified foundry and roles, unchanged.
- **Escrow:** 30k (T51 instruments). Donor start = PRISTINE (kind P). a17.R_VAL = R_VAL_C1, as T51/T06.
- **Genomes:** gtc.py, sha256 fdfcb0a0...; runner r7e.py, sha256 42e7f387....

  | Genome | Rule | Status |
  |---|---|---|
  | g0 | I_0 | **Continuity: must reproduce T51/T06's P selections in 15/15 seeds** (spot-checked 2/2 in DEV-7) |
  | g8 | selection eligibility = mean paired saving > 0 (I_0 requires lower95 > 0) | targets selection failure |
  | g9 | LGG derivation also from VALIDATE-cell hits | more traces; targets observation starvation |
  | ORACLE | the G1 schema entry is offered as an extra candidate | **positive control** |
  | NULL | an OFF schema entry is offered as an extra candidate | **negative control** |

- **Endpoint:** gain = number of the seed's 32 TRANSFER families (T51/T06 roles) where the selected library reaches a
  T4-v1a-qualified program at <= 1M in >= 1 of 2 cells AND PRISTINE is censored in that cell. T51's transfer cell
  seeds are used.

## 3. Measurement gates (all must hold; otherwise MEASUREMENT_FAILED)
- CONTINUITY: g0 selections == T51/T06 P selections in 15/15 seeds.
- ORACLE_UPPER: total ORACLE gain >= 0.9 x the inherited-G1 reference (T51: 70; T06: 45; total 115). This shows the
  pipeline can return the positive.
- NULL_LOWER: total NULL gain <= total g0 gain + 2. A non-matching planted schema must not create gains.

## 4. Frozen readout (per rule g in {g8, g9})
**R7E_POSITIVE(g)** iff BOTH:
- a paired one-sided sign test over seeds of gain(g) vs gain(g0) gives p < 0.05;
- total gain(g) > total gain(g0).

Also reported: derivation-success seeds per genome, and per-seed gains.

## 5. Interpretation (frozen)

| Result | Reading |
|---|---|
| R7E_POSITIVE for some rule | **first experimentally observable R7 (tier 2):** a content-free improver-rule change, transplanted with no library, makes the improver derive or reuse more on fresh natural supply. It is still not compounding (R8) or recursion (R9) |
| No rule positive | rule-level changes of these kinds do not raise endogenous success. The endogenous route's limit is then not these selection or observation rules |
| g8 positive alongside more false selections | reported via gains (false selections cost charges but do not create solves) |

## 6. Compute
75 donors (about 1 min each at 30k) plus about 3.5k walks at 1M: about 4 core-h. The rolling seat total stays <= 48
core-h. M4, 4 workers.
