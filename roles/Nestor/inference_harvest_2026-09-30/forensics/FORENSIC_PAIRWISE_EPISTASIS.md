# FORENSIC_PAIRWISE_EPISTASIS: pairwise knockouts and synthetic lethality (theory T4(c))

## Pre-registration (verbatim, frozen before any computation)

- **Panel.** The state-free genomes in core_map.json (target 48; the 8 epoch-700 16000006 genomes form one cluster). Comparators are an equal number of state-dependent genomes, matched by origin run where possible.
- **Dispensable position.** A position whose single random-value knockout (3 draws, existing data) keeps COMPETENT and, for state-free genomes, keeps both STATE_FREE vectors ≥ 0.5 in ≥ 2 of 3 draws.
- **Treatment.** For each genome, sample 200 random pairs of dispensable positions, or all pairs if fewer. Knock out both positions jointly with random values, 3 draws. The function is:
  - state-free genomes: COMPETENT and STATE_FREE (both vectors);
  - state-dependent genomes: COMPETENT only.
  - A pair is **lethal** if the function is lost in ≥ 2 of 3 draws. Re-assay each lethal pair once with a new seed tag, and count it only if it is still lethal.
- **Additive null.** For each genome, predict pair lethality from its single-knockout loss rates. Treat the two positions' single-draw failure probabilities (p_i, p_j from the 3 single draws) as independent; the null probability of joint function loss is 1 − (1−p_i)(1−p_j), thresholded the same way as a ≥ 2/3 draw call via the binomial. The null rate is the mean over sampled pairs.
- **Ruler.** The synthetic-lethal excess: observed lethal-pair rate divided by the null rate, per genome and pooled.
- **Positive control (must PASS or the verdict is INSTRUMENT_UNREACHABLE).** A constructed genome with redundant setters: two independent `LD E,0x40` instructions at different positions before one copy op (E5), with `LD L,0` for state-freedom and random passengers elsewhere. Verify first that it is COMPETENT. Each setter alone must be dispensable, and the pair must be lethal. Construct it so that each setter really is sufficient: check by knocking out each one.
- **Negative control.** The minimal copier `2E 00 1E 40 E5` (LD L,0; LD E,40; LDIR alias) with random passengers. Passenger pairs must show a lethal rate ≤ 2x null.
- **Kill rules (frozen):**
  - "T4(c) dead": the pooled state-free excess is ≤ 1.5x null AND the state-free lethal rate is ≤ 1.2x the state-dependent rate.
  - "T3 no-organization reading dead": excess ≥ 3x null in ≥ 50% of state-free genomes.
  - Otherwise: INCONCLUSIVE.
- **Budget.** ≤ 60 CPU-min, single process, `python -B`. If the budget is short, reduce the pairs per genome to 100 before reducing genomes, and say so.

(Results below this line were computed after the block above was written.)

## Verdict: **T4(c) DEAD** (frozen rules; both controls pass)

| frozen quantity | value | threshold | met |
|---|---|---|---|
| positive control (designated construct, seed 0) | PASS | must PASS | yes |
| negative control (passenger pairs, pooled over 3 constructs) | 0 lethal / 600 pairs, null 0 | rate ≤ 2x null | yes (degenerate, see below) |
| pooled state-free excess (observed / null) | **0.774** (269/4700 = 0.0572 vs null 0.0739) | ≤ 1.5 | yes |
| state-free lethal rate / state-dependent rate | **0.560** (0.0572 vs 0.1023) | ≤ 1.2 | yes |
| state-free genomes with excess ≥ 3x | **0 / 48** (0 / 47 that have pairs) | ≥ 50% kills the T3 reading | no |

"T4(c) dead" fires: both legs hold, neither close to its threshold. The T3 rule does not fire. A bootstrap over genomes (2000 resamples, `s3_extra.py`) gives 95% intervals of [0.64, 0.91] for the pooled state-free excess and [0.37, 0.85] for the state-free / state-dependent rate ratio. Collapsing the 8 epoch-700 16000006 genomes into one cluster leaves the pooled numbers unchanged (0.774), because each genome contributes the same 100 pairs.

**One change from the pre-registration, made under its budget clause:** pairs per genome were **100, not 200**. No genome was dropped. The first 4 genomes of a 200-pair run cost about 24 s each, which projected about 58 CPU-min in total against the 60-min cap, so I stopped that run. Its log is kept as `s3_pairs_aborted200.log`; its results were discarded and not used. The projection was pessimistic: the full 100-pair run cost 888 s, so 200 pairs would have fit at about 47 min in total. Given the margins above, I judge that doubling the pairs could not move the verdict. The cut is recorded here as made.

## What the result actually says (read before quoting the ruler)

The frozen ruler is below 1 in both groups (SF 0.77, SD 0.71). That does **not** mean pairs are less lethal than independence predicts. It means the plug-in null is miscalibrated. Stratifying by the single-knockout counts (`s3_extra.json`) shows this:

| stratum (p_i + p_j from 3 single draws) | SF pairs | SF lethal rate | SD pairs | SD lethal rate | null |
|---|---|---|---|---|---|
| 0/3 + 0/3 | 3495 | **0.0375** | 2722 | **0.0371** | 0.000 |
| 0/3 + 1/3 | 1097 | 0.098 | 1462 | 0.141 | 0.259 |
| 1/3 + 1/3 | 108 | 0.278 | 519 | 0.335 | 0.583 |

- When p = 1/3, one of three *specific* replacement values broke the position, typically one destructive opcode. It is not a 1/3 per-draw failure rate that carries over to fresh random values. The binomial null therefore over-predicts in the p > 0 strata by about 2x, and this deflates the ruler equally in both groups.
- **Strict synthetic lethality exists.** These are pairs where both single knockouts kept function in 3/3 draws, so the null is exactly 0. They are lethal at about **3.7%**, and the rate is the **same in both groups**: SF 131/3495 = 0.0375 and SD 101/2722 = 0.0371. They are spread thinly: 39/48 SF and 39/48 SD genomes have at least one, and the per-genome maximum is 12 (SF) and 7 (SD). So there is multi-site interaction that single knockouts miss, but it is **generic to dense competent genomes**. Nothing here is specific to state-freedom, and no genome has a concentration of it that would read as organization.
- The overall SF/SD rate ratio of 0.56 is mostly composition. SD genomes have more marginal (p = 1/3) dispensable positions: 549 versus 365 position-draws, and 519 versus 108 pairs in the 1/3+1/3 stratum. They also sit closer to the 0.5 threshold: confirmation removed 162 of 643 raw SD lethal calls, against 2 of 271 SF. In the null-0 stratum, the like-for-like comparison, the SF/SD ratio is 1.01.

## Controls (`s3_controls.py`, `s3_controls.json`)

**Positive control.** The redundant-setter genome is `1E 40 | 2E 00 | 1E 40 | E5` followed by 57 random passengers: setter A (LD E,0x40) at 0-1, LD L,0 at 2-3, setter B (LD E,0x40) at 4-5, and the copy op E5 at 6. The knocked-out positions are the setter **opcode** bytes, 0 and 4. When one of them is replaced, the orphaned 0x40 executes as LD B,B, which is harmless. The operand of the *last* setter cannot be redundant, because a wrong value there is the final write to E. That is a property of the construction, not a failure of the instrument. Function = COMPETENT and STATE_FREE.

| seed | COMPETENT / STATE_FREE | NOP-out A kept | NOP-out B kept | NOP-out A+B kept | A kept (of 3) | B kept (of 3) | pair (0,4) lethal / confirmed | PASS |
|---|---|---|---|---|---|---|---|---|
| **0 (designated)** | yes / yes | yes | yes | **no** | 3 | 3 | yes (0/3 kept) / yes | **PASS** |
| 1 | yes / yes | yes | yes | no | 2 | 2 | yes / yes | PASS |
| 2 | yes / yes | yes | yes | no | **1** | 2 | yes / yes | fail: setter A not dispensable (random opcodes derail the path) |
| 3 | yes / yes | yes | yes | no | 3 | 2 | yes / yes | PASS |
| 4 | yes / yes | yes | yes | no | 3 | 2 | yes / yes | PASS |

The instrument detects a planted synthetic-lethal pair, so the verdict is not INSTRUMENT_UNREACHABLE. The NOP sufficiency checks pass on all 5 seeds: each setter alone suffices, and removing both kills function.

**Negative control.** `2E 00 1E 40 E5` followed by 59 random passengers, 3 constructs. All are COMPETENT and STATE_FREE, and all 59 passengers in each are dispensable. Their 200 sampled passenger pairs per construct give **0 lethal, null 0 → PASS**. This pass is degenerate: no passenger failed even one single draw, and no passenger pair failed. The control rules out the instrument manufacturing lethality from pairs of inert bytes. It cannot check calibration of the null at p > 0, which is the gap shown above. Incidentally, construct 0 drew `E5` at position 5, so its core copy op at 4 became single-knockout dispensable: a naturally occurring redundant copy op.

## Where the lethal pairs sit (`s3_summary.json` loc_*, `s3_zero_stratum.json`)

Classes come from the donor's zero-state trace on its passing side (`core_map.analyse_trace`). EXEC_PRE means executed before the main copy. NOT_EXEC means executed by neither donor nor partner in the traced draw. DEST, SRC and COUNT are the last setters of the copy operands.

- **SF, all 269 confirmed lethal pairs:** EXEC_PRE+EXEC_PRE 176, EXEC_PRE+NOT_EXEC 48, COUNT+EXEC_PRE 14, EXEC_PRE+SRC 8, DEST+EXEC_PRE 8, NOT_EXEC+NOT_EXEC 6, other 9. Compared with the sampled pairs, positions in lethal pairs are enriched for EXEC_PRE (1.36x), DEST (1.81x), COUNT (1.46x) and SRC (1.36x). They are depleted for NOT_EXEC (0.37x), and none are EXEC_POST or COPY. SD shows the same shape (EXEC_PRE 1.35x, NOT_EXEC 0.58x).
- **Strict synthetic lethals (null-0 stratum):** EXEC_PRE+EXEC_PRE 88/131 (pair-class lethal rate SF 0.073 vs SD 0.092), EXEC_PRE+NOT_EXEC 27 (0.025 vs 0.023), COUNT+EXEC_PRE 8 (0.11 vs 0.094). Nearly all of these pairs are ≥ 4 bytes apart (SF 127/131, SD 94/101), so they are **not** adjacent bytes fusing into a new instruction. The dominant mechanism is two separately tolerable perturbations of the **pre-copy executed path**, for example the opcode `FF` at 8 with `F2` at 35, or `DB` at 27 with `F2` at 35. The EXEC_PRE+NOT_EXEC pairs fit path redirection: an executed byte changes and execution falls into a previously dead byte, for example `C2` at 44 with a byte at 62.
- Lethal executed positions are mostly opcode bytes, spread over many instructions with no recurring motif. The top SF contexts are `29` (ADD HL,HL) 10, and `E0`, `E9`, `88`, `2E` and `18`-argument at 6 each.

## Per-genome rates (100 pairs each; rate = confirmed lethal / pairs; excess = rate / null)

State-free panel (48; idx = core_map row; `e700` = the 16000006 epoch-700 cluster):

| idx | run | cell | disp | lethal raw/conf | rate | null | excess |
|---|---|---|---|---|---|---|---|
| 5 | 17000009 | 7ae3 | 58 | 3/3 | 0.03 | 0.119 | 0.25 |
| 6 | 17000009 | 7ae3 | 55 | 5/5 | 0.05 | 0.036 | 1.38 |
| 17 | 17000028 | 7ae3 | 56 | 3/3 | 0.03 | 0.067 | 0.45 |
| 26 | 16000006 | 7ae3 | 56 | 1/1 | 0.01 | 0.029 | 0.34 |
| 27 | 16000006 | 7ae3 | 58 | 1/1 | 0.01 | 0.016 | 0.64 |
| 38 | 16000021 | 7ae3 | 58 | 2/2 | 0.02 | 0.051 | 0.40 |
| 40 | 16000026 | 7ae3 | 55 | 11/11 | 0.11 | 0.076 | 1.44 |
| 41 | 16000026 | 7ae3 | 59 | 0/0 | 0.00 | 0.052 | 0.00 |
| 46 | 16000033 | 7ae3 | 50 | 8/8 | 0.08 | 0.129 | 0.62 |
| 49 | 16000036 | 7ae3 | 50 | 10/9 | 0.09 | 0.078 | 1.16 |
| 54 | 16000046 | 7ae3 | 55 | 9/9 | 0.09 | 0.089 | 1.01 |
| 55 | 16000046 | 7ae3 | 52 | 11/11 | 0.11 | 0.142 | 0.78 |
| 56 | 17000000 | ffa6 | 54 | 3/3 | 0.03 | 0.103 | 0.29 |
| 57 | 17000000 | ffa6 | 56 | 4/4 | 0.04 | 0.041 | 0.96 |
| 58 | 17000001 | ffa6 | 52 | 9/9 | 0.09 | 0.098 | 0.92 |
| 59 | 17000001 | ffa6 | 55 | 1/1 | 0.01 | 0.029 | 0.35 |
| 60 | 17000003 | ffa6 | 53 | 6/6 | 0.06 | 0.026 | 2.31 |
| 61 | 17000003 | ffa6 | 56 | 1/1 | 0.01 | 0.029 | 0.35 |
| 64 | 17000005 | ffa6 | 57 | 4/4 | 0.04 | 0.050 | 0.80 |
| 69 | 17000009 | ffa6 | 53 | 13/13 | 0.13 | 0.121 | 1.08 |
| 70 | 17000009 | ffa6 | 53 | 2/2 | 0.02 | 0.058 | 0.35 |
| 71 | 17000010 | ffa6 | 51 | 11/11 | 0.11 | 0.099 | 1.12 |
| 72 | 17000010 | ffa6 | 52 | 12/12 | 0.12 | 0.092 | 1.30 |
| 75 | 17000015 | ffa6 | 56 | 2/2 | 0.02 | 0.045 | 0.45 |
| 76 | 17000015 | ffa6 | 57 | 0/0 | 0.00 | 0.023 | 0.00 |
| 79 | 17000017 | ffa6 | 56 | 0/0 | 0.00 | 0.031 | 0.00 |
| 80 | 17000017 | ffa6 | 55 | 16/16 | 0.16 | 0.127 | 1.26 |
| 89 | 17000023 | ffa6 | 59 | 4/4 | 0.04 | 0.029 | 1.40 |
| 90 | 17000023 | ffa6 | 57 | 6/6 | 0.06 | 0.040 | 1.52 |
| 94 | 17000025 | ffa6 | 56 | 14/14 | 0.14 | 0.178 | 0.79 |
| 99 | 17000028 | ffa6 | **1** | no pairs | – | – | – (*) |
| 115 | 16000007 | ffa6 | 55 | 24/24 | 0.24 | 0.167 | 1.44 |
| 116 | 16000007 | ffa6 | 56 | 5/5 | 0.05 | 0.031 | 1.61 |
| 117 | 16000008 | ffa6 | 53 | 15/15 | 0.15 | 0.091 | 1.64 |
| 118 | 16000008 | ffa6 | 55 | 8/8 | 0.08 | 0.123 | 0.65 |
| 121 | 16000012 | ffa6 | 57 | 2/2 | 0.02 | 0.036 | 0.55 |
| 122 | 16000012 | ffa6 | 52 | 6/6 | 0.06 | 0.114 | 0.53 |
| 137 | 16000026 | ffa6 | 53 | 2/2 | 0.02 | 0.100 | 0.20 |
| 141 | 16000030 | ffa6 | 55 | 6/6 | 0.06 | 0.087 | 0.69 |
| 143 | 16000032 | ffa6 | 53 | 3/3 | 0.03 | 0.060 | 0.50 |
| 161 | 16000006 e700 | 7ae3 | 56 | 1/1 | 0.01 | 0.031 | 0.32 |
| 162 | 16000006 e700 | 7ae3 | 55 | 6/6 | 0.06 | 0.052 | 1.14 |
| 163 | 16000006 e700 | 7ae3 | 51 | 4/4 | 0.04 | 0.126 | 0.32 |
| 164 | 16000006 e700 | 7ae3 | 55 | 5/4 | 0.04 | 0.084 | 0.47 |
| 165 | 16000006 e700 | 7ae3 | 57 | 1/1 | 0.01 | 0.047 | 0.21 |
| 166 | 16000006 e700 | 7ae3 | 56 | 3/3 | 0.03 | 0.039 | 0.77 |
| 167 | 16000006 e700 | 7ae3 | 55 | 3/3 | 0.03 | 0.097 | 0.31 |
| 168 | 16000006 e700 | 7ae3 | 56 | 5/5 | 0.05 | 0.086 | 0.58 |

(*) Row 99 is marginally state-free: 53 of its 54 non-NECESSARY positions break STATE_FREE in ≥ 2/3 draws, which leaves 1 dispensable position and no pairs. In the T3 rule it counts as "not ≥ 3x" (0/48); dropping it gives 0/47.

SF summary: median excess 0.64, max 2.31, 15/47 genomes ≥ 1, 4/47 ≥ 1.5. The e700 cluster pools to 27/800 = 0.034, below the panel pooled rate of 0.057.

State-dependent comparators (48) were matched as follows: 6 at the same (cell, origin run), 5 at the same origin run in the other cell, 36 at the same cell and campaign family, 1 at the same cell only. Pooled: 481/4703 = 0.1023, null 0.1449, excess 0.706. Median per-genome excess 0.70, max 1.72 (row 31, which has only 3 dispensable positions and 3 pairs). Six SD genomes have fewer than 40 dispensable positions and confirmed rates of 0.10-0.60; they carry most of the SD lethal mass. The full per-genome table is in `s3_summary.json` (`per_genome_SD`).

## Method, as implemented

- **Screens.** `fsetup.py` is reused unchanged for the runner and cell. `s3_common.py` re-implements `run_de.competent` and the `run_fair.fair_assay` STATE_FREE call with **exact early stopping**: the same p11 seeds and tags, stopping once the ≥ 0.5 boolean is decided, and skipping the second side once a seed passes. `s3_equiv.py` checked this against `fsetup.competent` / `fsetup.state_free` on 132 genomes and mutants: **0 mismatches** (105 competent, 51 state-free), 2.6x faster.
- **Dispensable sets and p_i** (`s3_singles.py`). These use core_map's own knockout values for each position (the same RNG). For SD genomes the existing `ko_detail` is used; the third value was assayed where only 2 had been tried, so p_i = lost/3 everywhere. For SF genomes, the function (COMPETENT and both STATE_FREE vectors) was assayed on all 3 values at every non-NECESSARY position. The COMPETENT component reproduced the existing `ko_detail` counts at **2692/2692** positions. Mean dispensable positions: SF 54.9 (excluding row 99), SD 51.2.
- **Pairs** (`s3_pairs.py`). There were 100 sampled dispensable pairs per genome (all pairs if fewer). Each draw sets both positions to values from a separate RNG stream, distinct across the 3 draws. A pair is lethal when function is lost in ≥ 2/3 draws, with the third draw run only on a split, which is exact. Re-assay uses the same 3 mutants with new seed tags (`X-DD-ESTABLISH/S3R`, `SFL<hex>/S3R`), and a pair is counted only if still lethal. The null per pair is P(Binom(3, q) ≥ 2) with q = 1 − (1−p_i)(1−p_j). Pooled rates and nulls are pair-weighted. Per-genome excess is +inf when the null is 0 and the rate is > 0 (never occurred, since every genome with pairs had null > 0).
- **Panel.** These are the **48 DENSE** state-free genomes. The single PLAIN state-free genome in core_map.json (15000022) is excluded because the question concerns the dense VM. Comparators are 48 of the 80 dense state-dependent genomes, chosen by greedy matching with a seeded tie-break.
- **Ruler asymmetry (disclosed).** Observed calls pass a confirmation filter, but the null does not. This biases the excess down. Using raw calls instead, the pooled excess is SF 0.780 and SD 0.943, and the verdict is unchanged: the raw SF/SD rate ratio is 271/643 = 0.42 against 1.2.

## CPU (single process, `python -B`, `time.process_time`)

| step | CPU s |
|---|---|
| s3_timing_probe.py (cost probe) | ~5 |
| s3_equiv.py | 26.2 |
| s3_controls.py | 90.1 |
| s3_singles.py | 490.8 |
| s3_pairs.py, 200-pair attempt, stopped and discarded | ~100 (98.0 at its last checkpoint) |
| s3_pairs.py --npairs 100 | 888.5 |
| s3_summarize.py, s3_extra.py, s3_zero_stratum.py | < 10 |
| **total** | **≈ 1610 s ≈ 27 CPU-min** (cap 60) |

There were no world or evolution runs. All writes are confined to this forensics folder, and there were no git writes.

## Files (this folder)

`s3_common.py` (screens, RNG, null), `s3_pipeline.py`, `s3_equiv.py` → `s3_equiv.json`, `s3_controls.py` → `s3_controls.json`, `s3_singles.py` → `s3_singles.json` / `.log`, `s3_pairs.py` → `s3_pairs.json` / `.log` (+ `s3_pairs_aborted200.log`), `s3_summarize.py` → `s3_summary.json`, `s3_extra.py` → `s3_extra.json`, `s3_zero_stratum.py` → `s3_zero_stratum.json`, `s3_timing_probe.py`.
