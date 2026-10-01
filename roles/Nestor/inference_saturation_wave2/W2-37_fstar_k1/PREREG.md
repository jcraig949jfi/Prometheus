# W2-37 PREREG: F\* kill criterion K1 (density + kin, population level) at frozen tolerance

Written 2026-10-01T02:39:27Z (`date -u`), before any simulation in this folder. The only computation run before this
file is `e0_eligibility.py` (exact binomial enumeration on W2-22's logged runs; no simulation) and the arithmetic check
in `newcombe.py`.

## Frozen rule (not chosen here)
- Source: `roles/Nestor/inference_harvest_2026-09-30/NPE_COMPETING_THEORIES.md`, WAVE-2 CORRECTIONS block (D)-(E),
  inserted at **commit 32135ddc5**. Tolerances are frozen as of that commit; this test's data are all generated after it.
- **K1:** FIELD BANK - FREE BANK on **R2 = P(maxA >= 40 and B >= 27)** at horizon 300 epochs. Tolerance **0.05**.
- **Decision:** KILLED if the 95% CI of the difference lies wholly outside +-0.05; PASSED if wholly inside;
  UNRESOLVED otherwise.

## Process (identical to W2-22's FIELD BANK / FREE BANK arms)
- `w22.run2` (W2-22, imported unedited; W2-22 v1 verified it equals `ffield.run`), W2-14 `ffield.py` and
  `banks.pkl` (imported unedited). sha256 at 02:39Z: banks.pkl bbc4b7a1..., w22.py b63458db..., ffield.py 127a73e4...;
  all three clean vs HEAD 32135ddc5.
- Rule BASE, 7ae3 arm-B cell (atlas_axis NONE), tier M, PARTNER BANK, CTX CARRY, MUT ON, T = 300, `stop="xk"`,
  mech None, `bank=BANKS["BASE"], pool=BANKS["POOL"]` - exactly `W2-22/p1_run.py`'s call.
- The runaway stop requires maxA >= 40 and B >= 163, so it fires only after R2 is already decided (cannot censor R2).

## Seeds (fresh)
- BASE seed = 9_998_000 + s, **s = 50000..** (seeds 10_048_000+).
- Used ranges checked (all disjoint): X-TICKET s < 128 (`x_ticket/run_tk.py`); W2-14 s = 0..39; W2-22 s = 1000..2199
  (+ ATOMIC base 12_000_000 + 0..29); W2-29 s = 1000..1599 (bank_seeds subset of the same); W2-29 timing pilot
  s = 5000/5001; neighbouring campaign bases 9_999_000 / 9_999_500 / 9_999_700 / 9_999_800 use s < 128.
  No seed base in campaigns/ or wave-2 reaches 10_0xx_xxx.
- **FIELD BANK: s = 50000..50599 (n = 600). FREE BANK: s = 50000..51199 (n = 1200).**
- Validation seeds (not scored): s = 49990..49993 (fresh), plus replays of logged W2-22 seeds.

## Validation before production (nothing runs if it fails)
- V1: `run2(stop="orig")` == `ffield.run` on all output fields for s = 49990..49993, both arms.
- V2: `run2(stop="xk")` reproduces W2-22's logged records exactly for 4 FREE seeds (incl. free_cap256) and 3 cheap
  FIELD seeds with B >= 27.

## FREE 256-cap: censoring of R2 (checked on W2-22 data before writing this)
- The brief asserts the FREE cap does not affect R2. **It can.** In W2-22's FREE BANK, 55/1200 runs stopped at
  `free_cap256`; **25 of the 55 had B < 27 at the stop** (label floods). Their maxA = 256 >= 40 is settled, but B >= 27
  is censored: had the run continued, B could have reached 27.
- Treatments (by analogy to block (D)'s R3 rule and W2-22's C+/C-):
  - **C-**: a cap256 run with B < 27 counts as R2 = 0 (this is how 45/1200 was scored).
  - **C+**: a cap256 run with B < 27 counts as R2 = 1.
  - Cap runs with B >= 27 are R2 = 1 under both.
- **Verdict must hold under the treatment least favourable to it:** PASSED iff PASSED under both C- and C+;
  KILLED iff KILLED under both; otherwise UNRESOLVED. FIELD has no cap (no censoring).

## CI method (fixed)
Newcombe (1998) hybrid score interval, method 10: Wilson 95% interval per arm, combined as
L = d - sqrt((p1-l1)^2 + (u2-p2)^2), U = d + sqrt((u1-p1)^2 + (p2-l2)^2), d = p_FIELD - p_FREE. `newcombe.py`
reproduces Newcombe's worked examples (56/70 vs 48/80 -> 0.0524, 0.3339; 9/10 vs 3/10 -> 0.1705, 0.8090).

## Eligibility / power (`e0_eligibility.json`, from W2-22 rates)
- Rates: FIELD 23/600 = 0.038; FREE 45/1200 = 0.0375 (C-), 70/1200 = 0.058 (C+).
- Normal approximation, equal n, p = 0.038, half-width <= 0.035: **n >= 232 per arm** (required n).
- Exact enumeration, expected Newcombe half-width / P(PASS):
  - 230/230: hw 0.038 (C-) / 0.041 (C+); P(PASS both) 0.10 -> the nominal 0.035 target is not met under C+ at n = 232.
  - 400/800: hw 0.024 / 0.026; P(PASS both) 0.66.
  - **600/1200: hw 0.019 / 0.021; P(PASS both) 0.85**; P(KILL) ~0 at these rates.
  - 700/1400: hw 0.018 / 0.019; P(PASS both) 0.90.
- **Chosen: 600 FIELD / 1200 FREE** (expected half-width <= 0.021 under both treatments, well under 0.035).
  ELIGIBLE within budget.

## Budget
<= 75 CPU-min, <= 6 processes, `python -B`. W2-22 per-seed cost resampled: 600/1200 median 42.7, p95 53.7 CPU-min;
validation ~3 CPU-min. **Hard stop:** FREE runs first (all 1200, ~7 min). FIELD runs in seed order in batches of 60
(ordered map); dispatch stops once cumulative production CPU exceeds 68 min. If stopped early, the analysed FIELD set is
the contiguous completed prefix s = 50000..S, FREE stays at 1200, the realized n and half-width are reported, and the
verdict is computed by the same rule (no other change).

## Readouts
- **K1 (rule-bearing):** R2 difference, FIELD - FREE, C- and C+.
- **Descriptive only (not K-criteria here):** R1 = P(B_xk >= 27); R3 = P(B_xk >= 163 | B_xk >= 27), each with Newcombe
  CI; FREE cap runs treated C-/C+ (C+: a cap run counts as B_xk >= 27 for R1, and a cap run with B_xk >= 27 counts as
  reaching 163 for R3). Also: maxA >= 40 alone, label-flood share, stop-reason mix.

## Not done here
No mechanism arms, no world runs, no K2-K5. No look at production data before all seeds of an arm are complete.
