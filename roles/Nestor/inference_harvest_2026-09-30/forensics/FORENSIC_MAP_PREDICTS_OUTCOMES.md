# Does the single-interaction map predict per-donor establishment? (T6 test)

Date: 2026-09-30. This is a static analysis. It uses VM and single-interaction calls only: no world run, no evolution run and no git writes. Every script ran with `python -B`. Scripts and JSON outputs are in this folder, all prefixed `map_`.

**Verdict: PARTIAL.**
- The specified predictor (the GW survival P_est of a donor's own offspring law) gets the coarse structure right. It predicts the policy main effect and it picks out the state-robust donors.
- It does **not** predict per-donor establishment inside the arm where donors differ most (ZERO, panel A: rho = 0.08, p = 0.38).
- It is badly calibrated. Its Brier score is worse than a constant.
- It cannot see the cell axis at all.
- The predictor was extended *post hoc* with two more single-interaction statistics: whether the donor's copies are themselves copiers, and a finite 500-epoch horizon. The extension reaches rho = 0.81-0.86 and beats the in-sample policy-mean baseline. It is still single-interaction physics, but it is not the specified map, and it needs an out-of-sample test.

---

## 0. Setup: what was replicated, and the choices made

**Experiments.** C-ZERO-SPECIFIC (`run_cz.py`) reuses X-P2-REGSTATE's `run_rs.job` unchanged. X-P2-REGSTATE and X-P2-BRIDGE (`run_rs.py`, `run_br.py`) have:
- VM: dense (`world.z8 = run_dc.dense_z8()`);
- base cell: 7ae3's H2 B-arm cell (`run_br.SPEC7`), `atlas_axis NONE`, tier M;
- cell CF: `representation Z8_SLOTTED`, `structure NICHES_HIGH_MIG` (= ffa6's cell). C7 is the base cell as is;
- runner: `run_ds.runner_cls` (ATOMIC write-back: a half that is not converted is restored to its pre-interaction genome, then mutated). The register policy class `run_rs.runner(world, policy, prng)` sets both organisms' registers before every pair interaction. BRIDGE STATELESS is `run_sl.runner`, identical to ZERO. PERSIST is the same as CARRY;
- implant: one ACTUAL_GENOME founder in a population of 256 uniform random 64-byte genomes (`seeding RANDOM`).

**Cell parameters, verified from the constructed runner.** L = 64, tape 128 (wrapped, 7-bit addresses), slice budget 300, ops mask 42 (SELF, SENSE, LDIR/LDDR), mutation and copy-mutation rate 0.002. `pressure QUALITY_DIVERSITY`, so every alive organism is paired once per epoch.

**Harness (`map_common.py`).**
- The runner is constructed but never `.run()`. Two organisms are placed, and each interaction is **one call of the world's own `_pair_interact`** through the policy class.
- Label transfer, the P-11 causal assay, ATOMIC write-back and post-interaction mutation are therefore the world's code, unchanged.
- The donor is anc 0 and the partner is anc 1. The donor side is drawn 50/50. The partner is a fresh uniform random genome.
- The donor genome is reset to its original bytes before every interaction, so there is no mutational drift.

**Contexts.**
- ZERO, CONST and RANDOM are applied by `run_rs`'s class, which is exact.
- CARRY: the donor's registers are carried over its own successive interactions, starting from zero as the founder does. *Choice:* the partner's registers are drawn from a pool of carried states of random genomes (2 prior random-random interactions from zero), approximating the resident population.
- CARRY_L (extra): a lineage walk in which the next focal state is taken from a random anc-0 half. Children inherit the *victim's* post-execution registers.

**Donor-like.** As specified, the donor's own half counts if it is not converted (ATOMIC keeps it). The partner half counts if it has identity >= 0.9 to the donor's pre-interaction genome on the donor's **transmitted positions**.
- Transmitted positions are the positions delivered (final byte = donor byte, and the random victim byte differed) in >= 50% of the zero-context conversions. They cover 58-64 of 64 positions per donor.
- *First version, discarded:* "donor-authored" positions (p11 `prov`). It returned 1-2 positions for B0 and B4, because the victim's own context writes the bytes while executing donor code. It was replaced by "delivered".
- Whole-genome identity (W), the world label (LABEL) and label-plus-passing-P-11 (CAUSAL) were computed alongside. T, W and LABEL agree to within noise; CAUSAL differs.

**Sample sizes.** N = 500 interactions per (donor, cell, context). The GW survival is s = 1 - min(1, p0/p2), the root of s = 1 - f(1 - s), with a bootstrap 95% CI.

**Observed outcomes (S5 = depth >= 20 by epoch 500 AND anc0 >= 0.9).**
- **A-CF:** C-ZERO-SPECIFIC, k/3 per (donor, arm).
- **B-CF:** REGSTATE CF pooled with BRIDGE CF where the physics is the same arm: ZERO = REGSTATE ZERO + BRIDGE STATELESS (k/4); CARRY = REGSTATE CARRY + BRIDGE PERSIST (k/4); CONST and RANDOM (k/2).
- **B-C7:** the same arms in cell C7.

## 1. Offspring laws (Task 1)

The full laws are in `map_offspring.json` (p0, p1, p2, m and P_est with CI for T, W, LABEL and CAUSAL, plus conversion rate by side and the donor-overwritten rate).

**Pattern 1: under ATOMIC, p0 is the hijack rate.** The founder is lost only when the partner overwrites it (side 0, "victim magnet"). ZERO p0 is 0.00-0.32.

**Pattern 2: 26 of 32 donors do not convert at all from CONST, RANDOM or carried state** (p2 <= 0.02). The exceptions are:

| panel | donor | CONST P_est | RANDOM P_est | CARRY P_est |
|---|---|---|---|---|
| A | 1 | 0.56 | 0.62 | 0.55 |
| A | 15 | 0.59 | 0.67 | 0.68 |
| B | 4 | 1.00 | 0.87 | 1.00 |
| B | 14 | 0.66 | 0.72 | 0.69 |
| B | 15 | 0.51 | 0.57 | 0.62 |
| B | 0 | label conversions at p2 ~0.3 but LABEL/T p2 ~0; its CAUSAL law gives 0.07-0.65 | | |

A few more donors convert only under CARRY: A6 (0.80), B2, B6, B12 and B13.

**Pattern 3: degeneracy.** When p0 is about 0, P_est is 1.0 even for p2 = 0.002. For example, A4 CARRY has p0 = 0 and p2 = 0.002, giving P_est = 1.00. The specified predictor cannot distinguish "never lost" from "grows". Under ATOMIC against random partners, an un-hijackable donor "survives" forever whether or not it copies.

**Sanity anchor: the 7ae3 specimen genome in its own cell (C7).**

| context | p0 | p2 | m | P_est (95% CI) | P_est, causal |
|---|---|---|---|---|---|
| ZERO | 0.18 | 0.41 | 1.23 | 0.57 (0.45-0.66) | 0.48 |
| CARRY | 0.13 | 0.34 | 1.22 | 0.63 (0.50-0.72) | 0.43 |

The earlier probe reported 0.49-0.52 against an observed 0.52. This is the same order and consistent within the CIs.

## 2. Does P_est predict establishment? (Task 2)

Per-donor table: observed k/n, then P_est (specified), P_est_causal and P_run2 (the post-hoc two-type, 500-epoch predictor, section 2.4).

**A-CF (C-ZERO-SPECIFIC)**
```
 d orig | ZERO obs Pest Pcau Prun2 | CONST obs Pest Pcau Prun2 | RANDOM obs Pest Pcau Prun2 | CARRY obs Pest Pcau Prun2
 0 7ae3 | 0/3  0.99 0.99 0.00      | 0/3  1.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
 1 7ae3 | 0/3  0.29 0.29 0.49      | 1/3  0.56 0.55 0.55       | 1/3  0.62 0.62 0.57        | 1/3  0.55 0.55 0.62
 2 7ae3 | 0/3  0.65 0.65 0.00      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
 3 7ae3 | 2/3  0.71 0.71 0.65      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
 4 7ae3 | 2/3  0.63 0.24 0.58      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  1.00 0.00 0.00
 5 7ae3 | 3/3  0.75 0.75 0.84      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
 6 7ae3 | 3/3  0.66 0.66 0.74      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 2/3  0.80 0.80 0.78
 7 7ae3 | 0/3  1.00 1.00 0.00      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  1.00 1.00 0.00
 8 ffa6 | 3/3  0.79 0.79 0.74      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 1/3  0.00 0.00 0.00
 9 ffa6 | 3/3  0.65 0.60 0.59      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
10 ffa6 | 3/3  0.97 0.97 0.95      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
11 ffa6 | 1/3  0.97 0.97 0.00      | 0/3  0.00 0.00 0.00       | 0/3  0.00 0.00 0.00        | 0/3  0.00 0.00 0.00
12 ffa6 | 1/3  0.64 0.33 0.70      | 0/3  0.00 0.00 0.00       | 0/3  1.00 1.00 0.00        | 0/3  0.00 0.00 0.00
13 ffa6 | 2/3  0.65 0.34 0.75      | 0/3  0.56 0.00 0.50       | 0/3  0.00 0.00 0.52        | 1/3  0.00 0.00 0.00
14 ffa6 | 2/3  0.61 0.30 0.67      | 0/3  0.00 0.00 0.00       | 0/3  1.00 0.00 0.00        | 0/3  0.00 0.00 0.00
15 ffa6 | 1/3  0.53 0.53 0.45      | 1/3  0.59 0.59 0.55       | 2/3  0.67 0.67 0.70        | 1/3  0.68 0.68 0.71
```
**B-CF (REGSTATE + BRIDGE panel)**
```
 d orig | ZERO obs Pest Pcau Prun2 | CONST obs Pest Pcau Prun2 | RANDOM obs Pest Pcau Prun2 | CARRY obs Pest Pcau Prun2
 0 7ae3 | 2/4  0.72 0.44 0.75      | 1/2  0.85 0.65 0.83       | 2/2  0.80 0.07 0.87        | 3/4  0.80 0.39 0.74
 1 7ae3 | 2/4  0.57 0.00 0.52      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 1/4  0.50 0.00 0.64
 2 7ae3 | 3/4  0.86 0.86 0.89      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 3/4  0.66 0.65 0.82
 3 7ae3 | 0/4  0.63 0.00 0.58      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 0/4  0.75 0.00 0.00
 4 7ae3 | 3/4  0.99 0.99 1.00      | 1/2  1.00 1.00 1.00       | 2/2  0.87 0.40 0.94        | 2/4  1.00 1.00 1.00
 5 7ae3 | 0/4  0.56 0.00 0.50      | 0/2  0.00 0.00 0.00       | 0/2  1.00 0.00 0.00        | 1/4  0.62 0.00 0.00
 6 7ae3 | 4/4  0.99 0.99 0.97      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 3/4  0.96 0.96 0.98
 7 7ae3 | 4/4  1.00 1.00 0.99      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 0/4  0.00 0.00 0.00
 8 ffa6 | 2/4  0.72 0.48 0.63      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 0/4  1.00 1.00 0.12
 9 ffa6 | 2/4  0.76 0.76 0.77      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 0/4  0.00 0.00 0.00
10 ffa6 | 3/4  0.78 0.78 0.80      | 0/2  0.00 0.00 0.00       | 0/2  1.00 0.00 0.00        | 0/4  0.00 0.00 0.00
11 ffa6 | 2/4  1.00 1.00 1.00      | 0/2  1.00 0.00 0.71       | 0/2  1.00 0.00 0.00        | 2/4  1.00 1.00 1.00
12 ffa6 | 2/4  0.59 0.20 0.58      | 0/2  0.00 0.00 0.00       | 0/2  0.00 0.00 0.00        | 1/4  0.80 0.31 0.61
13 ffa6 | 1/4  0.99 0.98 0.98      | 0/2  0.50 0.00 0.00       | 0/2  1.00 0.00 0.00        | 2/4  1.00 1.00 1.00
14 ffa6 | 2/4  0.67 0.67 0.61      | 2/2  0.66 0.66 0.73       | 2/2  0.72 0.72 0.77        | 2/4  0.69 0.69 0.67
15 ffa6 | 2/4  0.40 0.40 0.45      | 1/2  0.51 0.51 0.51       | 0/2  0.57 0.56 0.62        | 3/4  0.62 0.62 0.57
```
The B-C7 table is in `map_correlate.json` (`rows`).

### 2.1 Spearman correlation per policy
n = 16 donors per row. p is a one-sided permutation p (5,000 permutations); the brackets give the bootstrap 95% CI.

| panel / policy | P_est (specified) | P_est_causal | m | P_run2 (post hoc) |
|---|---|---|---|---|
| A-CF ZERO | **0.08** (p 0.38) [-0.48, 0.70] | 0.02 (0.48) | 0.03 (0.46) | **0.81 (<0.001)** |
| A-CF CONST | 0.65 (0.03) | 1.00 (0.009) | 0.60 (0.009) | 0.84 (0.007) |
| A-CF RANDOM | 0.54 (0.04-0.05) | 0.72 (0.02) | 0.59 (0.009) | 0.84 (0.003) |
| A-CF CARRY | 0.34 (0.10) | 0.52 (0.04) | 0.39 (0.07) | 0.76 (0.004) |
| B-CF ZERO | 0.56 (0.01) [0.12, 0.88] | 0.66 (0.004) | 0.84 (<0.001) | 0.56 (0.014) |
| B-CF CONST | 0.73 (0.005) | 0.98 (0.001) | 0.86 (<0.001) | 0.87 (0.001) |
| B-CF RANDOM | **0.28** (0.17) | 0.80 (0.005) | 0.66 (0.004) | 0.89 (0.002) |
| B-CF CARRY | 0.37 (0.08) | 0.52 (0.02) | 0.73 (0.001) | 0.73 (0.001) |
| B-C7 ZERO | 0.50 (0.03) | 0.58 (0.01) | 0.76 (0.001) | 0.42 (0.05) |
| B-C7 CONST | 0.58 (0.02) | 0.76 (0.005) | 0.66 (0.01) | 0.67 (0.009) |
| B-C7 RANDOM | 0.17 (0.27) | 0.66 (0.01) | 0.69 (0.001) | 0.75 (0.006) |
| B-C7 CARRY | 0.32 (0.10) | 0.48 (0.03) | 0.53 (0.02) | 0.38 (0.08) |

In CONST and RANDOM most donors are tied at 0 in both prediction and outcome. There, rho mostly measures whether the few state-robust donors are picked out (section 2.3).

### 2.2 Pooled over (donor, policy) cells

| pool | n cells | P_est rho [95% CI] | perm p (free / within policy) | P_est_causal | P_run2 | Brier: P_est / P_run2 / policy mean (in-sample) / grand mean |
|---|---|---|---|---|---|---|
| A-CF | 64 | 0.53 [0.31, 0.73] | <0.001 / 0.012 | 0.67 | 0.86 [0.73, 0.94] | 0.145 / **0.031** / 0.059 / 0.100 |
| B-CF | 64 | 0.53 [0.30, 0.72] | <0.001 / <0.001 | 0.78 | 0.83 [0.75, 0.89] | 0.163 / 0.074 / 0.094 / 0.118 |
| A+B-CF | 128 | 0.56 [0.41, 0.70] | <0.001 / <0.001 | 0.74 | 0.86 [0.80, 0.91] | 0.154 / 0.052 / 0.076 / 0.115 |
| all (+B-C7) | 192 | 0.49 [0.37, 0.61] | <0.001 / <0.001 | 0.70 | 0.76 [0.67, 0.83] | 0.185 / 0.096 / 0.082 / 0.114 |

"Within policy" permutes the outcomes only among donors of the same (panel, policy), so it tests the per-donor information beyond the policy main effect.

**Calibration (mean predicted vs observed share).**

| panel / policy | observed | P_est | P_est_causal | P_run2 |
|---|---|---|---|---|
| A-CF ZERO | 0.54 | 0.72 | 0.63 | 0.51 |
| A-CF CONST | 0.04 | 0.17 | 0.07 | 0.10 |
| A-CF RANDOM | 0.06 | 0.21 | 0.14 | 0.11 |
| A-CF CARRY | 0.13 | 0.25 | 0.19 | 0.13 |
| B-CF ZERO | 0.53 | 0.77 | 0.60 | 0.75 |
| B-CF CONST | 0.16 | 0.28 | 0.18 | 0.24 |
| B-CF RANDOM | 0.19 | 0.44 | 0.11 | 0.20 |
| B-CF CARRY | 0.36 | 0.65 | 0.48 | 0.51 |
| B-C7 ZERO | 0.42 | 0.77 | 0.60 | 0.75 |
| B-C7 CARRY | **0.16** | 0.58 | 0.40 | 0.51 |

- **P_est overpredicts every arm, by 0.12-0.42.** Its Brier score is worse than predicting the grand mean.
- The policy ordering ZERO >> CARRY > CONST ≈ RANDOM is reproduced by every predictor.
- **The cell axis is invisible to the map.** B-C7 and B-CF laws are nearly identical because the pair physics is the same and only the post-interaction mutation operator differs. Observed CARRY is 0.16 in C7 against 0.36 in CF, and ZERO is 0.42 against 0.53. BRIDGE's representation × structure effect acts through mutation and migration, which a single-interaction map does not contain.

### 2.3 Identification tests
- **REGSTATE donors 0, 4, 14 and 15 carry every CONST/RANDOM success in B-CF.** Their ranks (of 16) under each predictor:

  | predictor | CONST top 4 | RANDOM top 4 |
  |---|---|---|
  | P_est (specified) | 4, 11, 0, 14 (15 is 5th). Donor 11 enters on the degenerate p0 = 0, p2 = 0.004 | donors 5, 10, 11 and 13 tie at 1.00 on p2 = 0.002; ranks of 0/4/14/15 are 6/5/7/8. **Fails** |
  | P_est_causal | exactly {4, 14, 0, 15} | exactly {14, 15, 4, 0} |
  | P_run500 / P_run2 | exactly {4, 0, 14, 15} (P_run2 in CONST: 0, 4, 14, then 11 above 15) | exactly {4, 0, 14, 15} |

  The mechanism is visible directly: these are the only B donors with p2 around 0.2-0.5 from 0x5A or random registers. Everyone else has p2 <= 0.02.
- **The C-ZERO-SPECIFIC "anti-zero" donor A1 is picked out by the specified P_est.**
  - Under ZERO, A1's P_est is 0.29, the *lowest of 16* (others average 0.75), because its hijack rate is high (p0 = 0.32).
  - Under CONST, RANDOM and CARRY it is 0.56, 0.62 and 0.55, ranking 3rd-5th (others average 0.14-0.23), and it is one of only two A donors that convert from non-zero states. The other is A15, which carries the remaining A CONST/RANDOM successes.
  - The *magnitude* is weak: P_est 0.29 predicts about 0.9 successes in 3 runs, and 0/3 has probability 0.36 under it.

### 2.4 Why the specified map fails inside ZERO, and a post-hoc repair
- A0, A2, A7 and A11 have high ZERO P_est (0.99, 0.65, 1.00, 0.97) but observed 0, 0, 0 and 1 of 3.
- Their runs reach S2 (the founder makes a causal copy) but never S3 or S4.
- `map_children.py` shows why: **their converted halves are not copiers.** Child conversion rates from ZERO are 0.002, 0.033, 0.003 and 0.000, against 0.29-0.47 for the others.
- In a spot check of 5 children each of A0, A7 and A11, every child differs from the donor at byte 0 (plus 0-4 scattered bytes), and all conversions happen with the donor on side 0. The donor writes the partner's position 0, and that is the likely break. A2 was not spot-checked.
- The single-genome law counts these children as "donor-like" (identity >= 0.9).
- **Repair:**
  - a two-type law (the founder's joint kept/child law, plus the pooled law of 40 children × 25 interactions each, in the same context);
  - a finite horizon matching S5: lineage >= 230 AND copy depth >= 20 within 500 generations. This is P_run2.
- **Result:** A-ZERO rho rises from 0.08 to 0.81, and the pooled A+B-CF rho from 0.56 to 0.86, with Brier 0.052 against 0.076 for the in-sample policy means.
- **Caveat:** this was designed after seeing the ZERO failure. B-C7 CARRY stays badly overpredicted (0.51 vs 0.16).

## 3. Phase arithmetic on real donors (Task 3)

**Method (`map_phase.py`).**
- Genomes: the 32 panel donors (CF), and the 43 X-DD-NOCOPY-CONTEXT donors from `delegates/corpus/q3_reset.json` in their own cells (7ae3 in C7, ffa6 in CF).
- Each side is run for 12 chains × 8 successive interactions. The donor carries its own registers; each interaction has a fresh random partner with zero registers.
- **Prediction:** a side is self-OK iff (dE ≡ 0 mod 128 or E reloaded) and (dL ≡ 0 or L reloaded). "Reloaded" means E_after is unchanged when the start value of E is 0 versus 1.
- **Observed label:** SELF_POISON iff the conversion rate over steps 2-8 is < 0.25 × the step-1 rate. This is W1's rule.

**Observed.**
- 76 of 150 sides convert at step 1.
- The copy count is set by the budget: an LDIR with carried BC = 0 runs until the slice ends, so counts are 164-295.
- Only 4 converting sides copy a multiple of 128, and only 11 of 150 sides have dE ≡ 0.
- **The "Δ ≡ 0 mod 128" route is essentially never realized in real donors.** Self-OK sides are almost all "reload" sides.

**Prediction vs observed (one-sided Fisher p).**

| comparison | counts: predOK/OK, predOK/POISON, predPOISON/OK, predPOISON/POISON | p |
|---|---|---|
| all sides, own observation | 27, 17, 4, 28 | 1.4e-5 |
| panel donors (donor level) | 12, 9, 2, 9 | 0.04 |
| Q3 donors, own observation | 14, 8, 2, 19 | 3e-4 |
| Q3: prediction vs **W1 X-DD-SELFSTATE label** | 11, 10, 1, 19 | 9e-4 |
| Q3: my observation vs W1 label (the instrument agrees with W1) | 12, 4, 0, 25 | 2e-7 |
| Q3 `carried_states` direct check (E&127 = 0 and L&127 = 0) vs W1 label | 6, 8, 6, 21 | 0.16 (n.s.) |

- **Predicted POISON is reliable:** 28 of 32 sides are correct.
- **Predicted OK is not:** 17 of 44 predicted-OK sides poison. The static "reload" proxy is too loose: E can be reset *after* the copy has already used the carried value.
- Only B10 of the panels appears in q3 (B donor 10). W1 labels were matched through q3's hex by (cell, seed).

**Direct causal decomposition (`map_phase_decomp.py`).**
- Step 2 is re-run from parts of the carried state, with the same partner and RNG in each variant, 16 trials per side.
- 45 poisoned sides: FULL 0.05, FRESH 0.77, **PTR_ONLY (only E and L carried) 0.19**, NO_PTR (everything except E and L) 0.47, FLAGS_ONLY 0.73, NO_FLAGS 0.05.
- Of the 44 poisoned sides with FRESH >= 0.25:
  - the E/L bytes alone poison 32;
  - clearing them rescues 26 (26 satisfy both);
  - flags matter in 1-2.
- The 31 self-OK sides are insensitive to every variant (0.64-0.71).

**Reading.** The poison is mainly the carried copy pointers, as T6's mechanism says. The specific modular prediction (robust iff the copy count is ≡ 0 mod 128) has almost no instances among real donors. The static Δ/reload rule predicts poisoning well but over-predicts robustness.

## 4. Verdict and limits

**PARTIAL.**

For T6:
- The map, computed genome by genome from single interactions, gets the right direction for the policy effect.
- It identifies which donors can establish at all outside ZERO: A1 and A15, and B {0, 4, 14, 15} under the causal and finite-horizon variants.
- It predicts A1's "anti-zero" rank.
- Pointer state is shown to be the dominant self-poisoning channel.

Against T6:
- The **specified** predictor (the GW survival of the donor's own offspring law) fails within ZERO in panel A (rho 0.08). That is the arm with the most spread.
- It fails in B RANDOM (0.28).
- It is degenerate whenever the donor is un-hijackable (P = 1 at p2 = 0.002).
- It is miscalibrated: its Brier score is worse than the grand mean in every pool.
- It is blind to the cell axis (C7 vs CF).
- What rescues it is **child competence**, a property of the donor's *copies*, plus a finite horizon. That is still computable from single interactions, but it is a two-generation map chosen post hoc.
- **Out-of-sample test to run next:** freeze P_run2 exactly as coded here, and score it on a fresh implanted panel before crediting T6.

Limits:
- Partners are uniform random, so GW ignores kin pairing and saturation.
- The CARRY partner state is approximated by 2 prior interactions.
- Mutation is excluded from the founder law, though included through the world's post-interaction mutation on each call.
- Observed shares rest on 2-4 runs per cell (a coarse outcome).
- The CIs on P_est are wide (±0.1).

## 5. Compute and files

**CPU: about 14.5 min in total**, single process:
- `map_offspring.py` 192 s × 2 runs (the first run used the discarded "authored" T);
- `map_correlate.py` 125 s + 189 s;
- `map_children.py` 133 s;
- `map_phase.py` 15 s;
- `map_phase_decomp.py` 12 s;
- about 15 s of probes.

Files:
- `map_common.py` (harness);
- `map_offspring.py` → `map_offspring.json`, `map_offspring.log`;
- `map_children.py` → `map_children.json`;
- `map_correlate.py` → `map_correlate.json`;
- `map_phase.py` → `map_phase.json`;
- `map_phase_decomp.py` → `map_phase_decomp.json`.

Run order: offspring, then children, then correlate; phase, then phase_decomp.

## Summary (10 lines)
1. I replicated the implanted-panel setting with the world's own `_pair_interact`: CF/C7 cells, dense VM, ATOMIC runner, `run_rs` register policies, L = 64, slice 300, cmr 0.002. I used 500 interactions per donor × context.
2. Under ATOMIC, p0 is the hijack rate. 26 of 32 donors never convert from CONST, RANDOM or carried state, so the policy main effect falls out of the map.
3. The specified P_est pools to rho 0.53-0.56 over (donor, policy) cells (within-policy permutation p <= 0.012), but it is 0.08 (p 0.38) inside A-ZERO and 0.28 in B-RANDOM.
4. P_est overpredicts every arm by 0.12-0.42. Its Brier score (0.145-0.185) is worse than the grand mean (0.100-0.118). It is degenerate (P = 1) for un-hijackable non-copiers.
5. It picks out anti-zero donor A1: last of 16 under ZERO (0.29), 3rd-5th elsewhere. A1 and A15 are the only A donors that convert from non-zero states, and they carry all the A CONST/RANDOM successes.
6. REGSTATE donors {0, 4, 14, 15} are exactly the top 4 under the causal and finite-horizon variants. The specified P_est misses them in RANDOM, because degenerate 1.0s win the ranking.
7. The A-ZERO failures (A0, A2, A7, A11) are sterile copies: the children never convert (0.00-0.03), caused by a byte-0 defect. The post-hoc two-type, 500-epoch P_run2 gives rho 0.81 in A-ZERO and 0.86 pooled, with Brier 0.052 against 0.076 for the in-sample policy means.
8. The cell axis is invisible to the map. C7 CARRY is observed at 0.16 against 0.36 in CF, while the predictions are nearly equal.
9. Phase: the carried E and L alone poison 32 of 44 self-poisoning sides, and flags do not. But Δ ≡ 0 mod 128 almost never occurs, and the static Δ/reload rule is right on 28 of 32 predicted-POISON sides but only 27 of 44 predicted-OK sides (p = 1.4e-5; against W1 labels p = 9e-4; the carried_states check is n.s.).
10. **Verdict: PARTIAL.** CPU is about 14.5 min. Report: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`
