# T10 -- OBSERVE BREADTH AS THE CANDIDACY DISCRIMINATOR (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 10. Frozen in DEV-10, 2026-10-05, before any T10 data. Rung **R2** (candidacy /
derivation, fed by observation supply). Thread TH-019. Evidence tier 2.

## 1. Question
T09 localised the remaining endogenous-route failures on fresh supply to **candidacy**:
- seeds 0, 7 and 12 derive nothing (n_observed 1 / 3 / 1, n_derived 0);
- seed 9 derives the wrong class;
- in all four, ORACLE10 shows that g10 would accept the base class if it were a candidate.

**Does observing more families (OBSERVE 4 -> 10) let the pristine improver generate the candidate it is missing?** One
lever changes (observation supply). The selection rule does not change.

## 2. Design
- **Seeds:** the 15 T51/T06 seeds.
- **Roles:**
  - T09's roles, unchanged: OBSERVE 4, the fresh breadth-12 VALIDATE draw, TRANSFER 32;
  - **plus 6 fresh OBSERVE families per seed.** They come from the A19 OBSERVE floor (0 < p_PRISTINE <= .75), are
    seeded `APHRODITE/T10/OBS/<seed>`, and exclude every family in the T51/T06 roles, T08 extras and T09 roles.
  - **Supply: 6/6 in 15/15 seeds.**
- **Fixed:** the g10 rule (TAU 1000), escrow 30k, PRISTINE start, R_VAL as T51.
- **Arms:**
  - **g10 at O10:** the treatment;
  - **NULL10 at O10:** the gate (OFF planted under g10);
  - **baseline g10 at O4:** T09's g10 rows (identical except OBSERVE).
- **Known-answer continuity (run in DEV-10, before freeze):** g10 on T09's own roles, seeds 0 and 3, must reproduce
  T09's rows exactly (selection, origin, entries, n_observed, n_derived, classes).
  **Result: 2/2 equal** (beta01/runs/T10_OBS/T10_CONTINUITY.json). This touches no T10 outcome.
- **Endpoint (as T07/T09):** gain = families of the 32 TRANSFER families where the selected library reaches a
  T4-v1a-qualified program at <= 1M in >= 1 of 2 cells AND PRISTINE is censored. PRISTINE walks are reused from T07.
- **Files:**
  - `engine/v2b/t10_observe.py` sha256 9ced6b98...;
  - gtc.py e097e1d4...;
  - r7e.py 42e7f387....

## 3. Measurement gate
All three must hold, otherwise MEASUREMENT_FAILED:
- continuity passes;
- NULL10 at O10 selects the planted OFF schema in <= 2/15 seeds;
- total NULL10 gain <= total g10 gain at O10 + 2.

## 4. Frozen readouts
- **CANDIDACY_POSITIVE:** a one-sided paired sign test over seeds of gain(g10 O10) vs gain(g10 O4) gives p < 0.05
  AND total O10 > total O4.
- **STARVATION_RESCUE:** gain(g10 O10) > 0 in >= 2 of the 3 zero-derivation seeds {0, 7, 12}.
- **Also reported:**
  - per-seed n_observed, n_derived and selection at O4 vs O10;
  - seeds harmed (O10 < O4);
  - seed 9 (the wrong-class case);
  - seed 14 (the validation-content case; no rescue is expected there).

## 5. Interpretation (frozen)

| Result | Reading |
|---|---|
| CANDIDACY_POSITIVE | observation supply is a binding endogenous limit. Watching more families raises reusable acquisition with the selection rule fixed. The next rung to test is whether the improver can CHOOSE how much to observe (an R7 lever) |
| STARVATION_RESCUE without CANDIDACY_POSITIVE | breadth fixes the starved seeds but costs elsewhere (extra observations change the candidates in success seeds) |
| Neither, gate passed | candidacy failure is not observation quantity at this scale. The derivation step (LGG / class certification) is the limit -- a representation/derivation question (W5P-adjacent; design only without authorisation) |
| Gate failed | nothing is read |

## 6. Compute
- **Donor stage:** 30 donors (15 seeds x 2 arms). The OBSERVE stage is about 2.5x T09's, so roughly 1.2 core-h.
- **Walks:** new libraries only (about 0.3 core-h).
- **Total:** about 1.5 core-h.
- **Budget:** the seat's rolling 24 h was about 45 core-h at 13:15Z and falls about 4 core-h/h until 14:43Z as the T53
  block rolls off. T10 fits under 48.
- **Host:** HARRY1, 4 workers, BLAS/OMP threads = 1.
