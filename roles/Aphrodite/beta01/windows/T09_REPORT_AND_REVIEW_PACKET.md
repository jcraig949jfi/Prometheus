# T09 -- SUBSET-BENEFIT SELECTION CRITERION (R7): REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 9, TEST window 9. Rung R7 (an improver-rule change) aimed at the R3 limit.
Evidence tier 2.

| Item | Value |
|---|---|
| Spec | beta01/windows/T09_SUBSET_SPEC.md |
| gtc.py | sha256 e097e1d4... |
| t09_subset.py | sha256 d48b8dbf... |
| Operator order | prompts/2026-10-05_t09_order/ORDER_RECORD.md |
| Receipts | beta01/runs/T09_SUBSET/{T09_RESULT.json, T09_DONORS.jsonl, T09_ROLES.json, T09_INDEX.json, T09_WALKS.jsonl}; the log beta01/runs/T09_run.log is local to M4 (gitignored) |

## 1. Dispositions

**Technical: CLEAN at attempt 2.**
- **Attempt 1:**
  - launched at 12:45Z, after the compute hold;
  - stopped at about 12:51Z by the session host's low-memory reaper, a host-level kill;
  - by then 16/60 donor rows were written (seeds 0-3, all arms);
  - no scoring had run.
- **Attempt 2:**
  - resumed with the operator's go at 12:53Z. The runner skips completed (seed, genome) pairs, and nothing else was
    changed;
  - 60/60 donors, 384 new walks;
  - exit 0 at 13:09Z.
- The 16 attempt-1 rows were produced by the same deterministic code and are kept.

**Scientific: MEASURED.** The NULL gate passed. **R7_SUBSET_POSITIVE = NO** (Outcome B).

## 2. Answers to the operator's questions (s22)

| # | Question | Answer |
|---|---|---|
| 1 | NULL10 passed? | **YES.** The planted OFF schema was selected in **0/15** seeds. NULL10 total 98 <= g10 total 98 + 2 |
| 2 | g0 total gain | **93** |
| 3 | g10 total gain | **98** |
| 4 | Paired better / worse / tied | **1 / 0 / 14** |
| 5 | Sign-test p | **0.5** |
| 6 | R7_SUBSET_POSITIVE | **NO** |
| 7 | Validation-limited seeds rescued | The reducer lists [4, 13] (g10 gain > 0). Only **seed 4 is g10-specific** (g0 0 -> g10 5, selecting (acc - {H})). Seed 13 gains 7 under g0 as well on this fresh draw. Seeds 9, 12 and 14 stay at 0 |
| 8 | ORACLE10 accepted planted G1 | **5/15** seeds (0, 1, 7, 9, 12). In the other 10 seeds an endogenous LGG candidate won, or nothing was eligible (seed 14) |
| 9 | Seed 12 | Gain 0 under g0, g10 and NULL10. **Cause: 1 observation and 0 derived candidates.** The criterion never sees a real candidate. ORACLE10 accepts G1 there, but it transfers only 2 families. This is the expected boundary; no leakage concern arises because g10 did not succeed there |
| 10 | First broken rung now | **CANDIDACY (R2 derivation, fed by observation supply), not the R3 criterion.** See s3 |
| 11 | Single T10 experiment | **OBSERVE breadth 4 -> 10 under g10** (fresh families, the T09 validation draw held fixed). See s4 |

## 3. Localisation (from existing rows; no new compute)

**g0 and g10 select the SAME schema in 14/15 seeds.** The criterion change bites only in seed 4.

The 5 seeds where g10 selects nothing (0, 7, 9, 12, 14):

| Seed | n_observed | n_derived | ORACLE10 (G1 planted) | Failure class |
|---|---|---|---|---|
| 0 | 1 | 0 | accepted, gain 11 | **candidacy: observation starvation** |
| 7 | 3 | 0 | accepted, gain 5 | **candidacy: no class certified** |
| 12 | 1 | 0 | accepted, gain 2 | **candidacy: observation starvation** |
| 9 | 6 | 1 | accepted, gain 5 | **candidacy: a wrong-class candidate**, rejected by g10 |
| 14 | 6 | 1 | rejected too | **validation content:** no VALIDATE family rewards G1 even when supplied |

Under the operator's s17 decomposition:
- **Candidacy failure: 4 seeds** (0, 7, 9, 12). g10 WOULD accept the base class if it were a candidate (ORACLE10
  accepts it in all four, for a diagnostic gain of 23).
- **Validation-content failure: 1 seed** (14).
- **Criterion failure: 0 seeds.** On this draw g10 never sees positive evidence and then chooses badly. In seed 1
  ORACLE10 prefers the planted G1 over the endogenous (acc - {H}), and its transfer falls from 10 to 5. That is a
  transfer mismatch inside an oracle arm, diagnostic only.
- **Transfer mismatch (endogenous arms): not observed.**

## 4. What this changes (honest revision of midpoint 2)

**Midpoint 2 located the limit at the R3 selection criterion, from T07 and T08. On a fresh, unexposed breadth-12
draw, I_0 (g0) already reaches 93, so the criterion is NOT the dominant limit on fresh supply.**

| Comparison | Value |
|---|---|
| T07 g0, breadth 4 | 86 |
| T08 g0, its breadth-12 draw | 76 |
| T09 g0, fresh breadth-12 draw | **93** |

g0 swings by 17 between two breadth-12 draws. Two consequences:
1. **The T08 "breadth hurts" reading is draw-dependent.** It was not a stable property of breadth. T08's label stays
   as recorded (no historical relabel). This is a revision of the interpretation only.
2. **Validation-draw variance is large relative to criterion effects.** Any further R3/R7 criterion test must hold the
   validation draw fixed (as T09 did) or average over draws.

The subset criterion is safe (0 junk acceptances) but nearly inert: it changes 1 seed. **The binding limit is
upstream: the improver does not generate the right candidate in about a quarter of natural seeds.** In 3 of those
seeds it derives nothing at all, because its 4 OBSERVE families yield 0-3 observations at escrow 30k.

## 5. Next: T10 (candidacy discriminator), drafted for DEV-10
- **Hypothesis:** endogenous candidacy is limited by how many families the improver OBSERVES.
- **Lever:** OBSERVE 4 -> 10. The 6 fresh families per seed come from the A19 floor (0 < p_PRISTINE <= .75) and
  exclude every family used in T51, T06, T08 or T09. Supply: >= 6 available in 15/15 seeds.
- **Held fixed:** the g10 rule, the T09 validation draw, TRANSFER, escrow and the endpoint.
- **Baseline:** T09 g10 rows (O4), verified by an exact continuity rerun.
- **Gate:** NULL10 at O10.
- **Scope:** this changes one thing (observation supply). It is not a second criterion change.

## 6. Attack questions
1. Is g10's single-seed effect (seed 4) a criterion effect, or a tie-break artefact (TAU fixed at 1000)? The seed-4
   selection table would answer this (it is in T09_DONORS; not yet inspected beyond the selection).
2. Is the g0 swing (76 vs 93) explained by how many of the 8 extras are PRISTINE-solvable (the T08 attack question 1)?
   This can be computed from the roles files without new compute.
3. ORACLE10's acceptance in only 5 seeds partly reflects that an endogenous LGG candidate outscores G1 under
   net-gain. Is G1 really "the" base class on natural supply, or one of several equivalent ones?
