# T12 -- FRESH-SEED REPLICATION OF THE CUMULATIVE IMPROVER (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 12, the final TEST window. Frozen in DEV-12, 2026-10-05, before any T12 data. Rung
R7 (an improver-rule change), unexposed replication. Evidence tier 2.

## 1. Question
T09-T11 built, on 15 EXPOSED seeds, an improver that differs from I_0 by three content-free rule changes, each one
localised by the preceding test:
1. the g10 subset-benefit criterion;
2. OBSERVE breadth 10;
3. abstraction-only candidacy (g11 = g10 minus MEMORISE).

On the exposed seeds: 123 vs I_0's 93 (6 better / 2 worse / 7 tied; sign p 0.14, sign-flip p 0.051). That is not
positive under the frozen rules.

**Does the cumulative improver (g11 at O10) beat I_0 on UNEXPOSED natural supply?**

## 2. Design
- **Supply:** W8 LIN seeds 16-23, never used in any Beta-01 or ARC3 role. Their W8 supplies and X_S are committed.
  - Stage `supply` is the T51 pipeline unchanged: plan -> foundry (escrow 30k) -> roles (A19 NAT rule, OBSERVE 4 /
    VALIDATE 4 / TRANSFER 32), with the supply screen at quota 6.
  - Extras per seed: VALIDATE +8 from the head (seeded APHRODITE/T12/VAL/<s>) and OBSERVE +6 from the floor (seeded
    APHRODITE/T12/OBS/<s>), mutually exclusive.
  - A seed is used only if its roles fill AND its extras fill.
- **Arms:**

  | Arm | Content |
  |---|---|
  | g0_O4 | I_0, breadth-12 validation: the T09 g0 analogue |
  | g10_O10 | the T10 analogue |
  | **g11_O10** | the treatment: the T11 analogue |
  | NULL11_O10 | gate |

- **Endpoint (as T07):** families of the seed's 32 TRANSFER families where the selected library reaches a
  T4-v1a-qualified program at <= 1M in >= 1 of 2 cells AND PRISTINE is censored in that cell. PRISTINE is walked here
  on identical cells.
- **Known answers (checked in DEV-12, beta01/runs/T12_REPL/T12_KNOWN.json): PASS.**
  - **K1:** the runner reproduces T11's g11_O10 row for exposed seed 3.
  - **K2:** in the SAME worker, after a g11 job, g10_O10 for seed 13 reproduces T10's row (MEMORISE chosen). This
    proves the per-job selector reset.
  - The report stage gained the pooled-descriptive block after K1/K2 ran. The donor code path is unchanged.
- **Files:** `engine/v2b/t12_replicate.py` sha256 ceed378d...; t11_absonly.py f2b8442e...; t10_observe.py
  9ced6b98...; gtc.py e097e1d4...; r7e.py 42e7f387....

## 3. Gates
- **Supply:** at least 6 fresh seeds usable, otherwise **SUPPLY_LIMITED** (not NO).
- **Measurement:** all of the following, otherwise MEASUREMENT_FAILED:
  - K1 and K2 pass;
  - NULL11 selects the planted OFF schema in <= 2 seeds;
  - total NULL11 <= total g11 + 2.

## 4. Frozen readouts
- **IMPROVER_REPLICATED_POSITIVE (primary):** an exact one-sided sign-flip permutation test over fresh seeds on
  d_s = gain(g11_O10) - gain(g0_O4) gives p < 0.05 AND sum d > 0.
  - The sign-flip test uses magnitudes. The sign test is underpowered with few changed seeds (the T11 lesson).
  - The attainable minimum p (2^-#nonzero) is reported alongside.
- **ABSTRACTION_ONLY_REPLICATED_POSITIVE (secondary):** the same test on g11_O10 vs g10_O10.
- **Also reported:**
  - the sign tests;
  - the seeds where MEMORISE is selected in each arm;
  - per-seed selections;
  - **POOLED_descriptive:** the sign-flip test over the 15 exposed + fresh seeds. It is labelled EXPOSED+FRESH and is
    never a label-bearing readout.

## 5. Power (stated before data)
- About 7-8 fresh seeds.
- If the fresh seeds behave like T11 (about half of seeds change, mostly upward by 3-11 families), the expected
  sign-flip p is around 0.05-0.2.
- **The primary readout is more likely than not to be NOT positive even if the effect is real.** A NOT-positive result
  here is therefore weak evidence against the effect.
- More fresh seeds would need W8 regeneration (the genuine/cover pipeline), which is outside this window.
- This is a power limit, recorded before data. It is not to be collapsed into NO.

## 6. Interpretation (frozen)

| Result | Reading |
|---|---|
| PRIMARY positive | **first replicated R7 (tier 2):** a content-free improver-rule package, built by causal localisation on exposed supply, makes a pristine improver acquire more reusable improvement on unexposed natural supply. First-order: NOT R8, NOT RSI |
| PRIMARY not positive, same direction | not replicated at this power. The Beta-01 statement stays "mechanism-confirmed on exposed seeds; replication underpowered" |
| PRIMARY not positive, reversed | the T09-T11 package is overfit to the exposed seeds |
| SUPPLY_LIMITED / gate failed | as labelled; nothing is read |

## 7. Compute
- **Estimate:** foundry 8 x 144 families, about 1 h wall (about 4 core-h); donors 32, about 15 min; walks about 5 x
  64 cells x 8, about 15 min. **Total about 6.5 core-h.**
- **Budget:** the rolling 24 h is about 40 core-h at 14:15Z. T52's 12.3 core-h block (15:05-18:12Z on 2026-10-04)
  rolls off during the run, so usage stays below 48.
- **Host:** HARRY1, 4 workers, threads = 1. Fabric is preferred for heavy shards, but its output retrieval is still
  broken (#1404), so M4 is used.
