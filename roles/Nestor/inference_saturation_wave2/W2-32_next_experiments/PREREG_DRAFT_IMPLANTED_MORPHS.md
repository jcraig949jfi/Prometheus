# PREREG DRAFT: X-IMPLANT-MORPH (implanted-morph founders under BASE, X-TICKET cell)

**Status:** DRAFT, written 2026-10-01T02:40Z (`date -u`). It is NOT frozen, NOT dispatched and NOT authorized. It needs operator or Aporia authorization, a canonical Fabric lease, and a freeze commit before any world run.
**Rank:** 1 of 3 (see DESIGNS.md).
**Author:** W2-32 design worker for Nestor.
**Supporting calculation:** `calc_bands.py` → `calc_bands.json`, in this folder. This is pure arithmetic with no world code. It took 14 CPU-s.

## 0. Why this experiment
The live contradiction is W2-25 F4/F5 and the ledger's "most important unresolved" item 2.
- **Supercritical reading.** The two-type reading (W2-17/N18) says side-0 morphs are supercritical (lifetime m 1.05–1.2).
- **Near-critical reading.** The per-call law against realized partners (N17e/W2-24) says the morph advantage is only about +6%. On that reading the morph is near-critical, and runaways are luck plus selection.

**Every comparison so far is observational and outcome-conditioned** (W2-25 F3). Implanting the genotype as the founder removes the conditioning. The arm set adds the two variants with the largest *static* differences:
- **43→C3**, a one-bit keep variant: keep 0.71 → 0.94 with unchanged conversion;
- **C3+AC**, the double mutant (m 1.47, keep 0.98).

These are the arms where the competing static→lifetime mappings disagree by an order of magnitude. That is the decisive lever, and it is why this draft differs from W2-25 §5 Experiment 1, which had only morph arms.

**Defect in W2-25's Experiment-1 rule (found while deriving bands).** W2-25 froze H-SUPER as "P(B≥163) for a morph founder ≥ 0.15 and ≥ 4x the founder".
- N18's own best two-type fits, run forward from a single implanted morph, predict **P(B≥163) = 0.030–0.117** for AC. See §5, model M1.
- So W2-25's rule would have killed H-SUPER even if N18's H-SUPER were exactly true.
- That rule is replaced here by bands derived from the models.

## 1. Hypotheses (each is a frozen mapping from static law to lifetime law, calibrated on the founder)
All three are calibrated so that the **founder** reproduces X-TICKET: B ≥ 27 at 4/128 and B ≥ 163 at 4/128 (Clopper–Pearson [0.0086, 0.078]).
- Offspring are negative binomial with V ∈ {3, 7, 12}.
- Type switching follows N18: s ∈ {7.5e-4, 0.01, 0.035} per birth (side-1 → side-0 type) and b = 0.07 back.
- The generation cap is G ∈ {40, 60}, standing in for 300 epochs at 5–10 epochs per generation.
- Only parameter sets that pass the founder calibration are kept: M2 115/288, M3 133/288, M1 14/14.

The static inputs come from the W2-24 trace table (N = 1,000 bank panel, side-averaged):

| genome | conv | keep | per-call m_base | conv/(1−keep) | per-call ratio | geometric ratio |
|---|---|---|---|---|---|---|
| F (7ae3) | 0.438 | 0.714 | 1.172 | 1.53 | 1.000 | 1.00 |
| AC (44 EC→AC) | 0.511 | 0.760 | 1.248 | 2.13 | 1.065 | 1.39 |
| C3 (43 C1→C3) | 0.436 | 0.940 | 1.389 | 7.27 | 1.185 | 4.75 |
| C3+AC | 0.505 | 0.981 | 1.469 | 25.9 | 1.253 | 16.9 |

- **H-SUPER-M3 (keep-leveraged lifetime law: "supercritical variant causes persistence").**
  - Model: lifetime m(g) = m0 × [conv/(1−keep)](g) / [conv/(1−keep)](F). An organism lives until it loses its half, so a gain in keep is a gain in lifetime.
  - Consistency check: with the founder at a realized 0.80–0.89, this gives AC a lifetime m of 1.11–1.24. That reproduces N18's fitted morph m1 (1.05–1.2) from static data alone, so it is the static-law form of W2-17's claim.
- **H-NEAR-M2 (per-call proportional: "near-critical plus luck").** Lifetime m(g) = m0 × m_call(g) / m_call(F). This is the "+6%" reading (N17e, W2-25 F4).
- **H-SUPER-M1 (N18-native).** The AC morph is N18's type-1 at its fitted m1. N18 has no C3 type, so M1 says nothing new about the C3 arms.
- **H-ANOMALY (W2-25 F8).** Founder persistence after 27 births, P(B≥163 | B≥27), exceeds every calibrated model: above M3's maximum of 0.544.

**Predicted P(B ≥ 163 at epoch 300), as the range over calibrated parameter sets.** The frozen bands come from this table.

| arm | M1 (N18) | M2 (near-critical) | M3 (keep-leveraged) |
|---|---|---|---|
| F | 0.016–0.021 | 0.009–0.028 | 0.009–0.042 |
| AC | 0.030–0.117 | 0.009–0.046 | 0.035–0.216 |
| C3 | (M3 factors) | 0.020–0.122 | 0.865–0.990 |
| C3+AC | (M3 factors) | 0.027–0.164 | 1.000 |

**Model P(B≥163 | B≥27):**

| arm | range |
|---|---|
| F | 0.17–0.54 |
| AC | 0.23–0.49 (M2) / 0.45–0.85 (M1, M3) |
| C3 and C3+AC under M3 | 1.0 |
| C3 and C3+AC under M2 | 0.43–0.81 |

**Allowance (frozen).** Branching-process escape ignores world-specific accidents such as epoch-1 loss and reaping. M3's C3-arm floor is therefore lowered from 0.865 to **0.75**.

## 2. Arms (X-TICKET physics throughout)
- **Physics.** C9 arm-B cell for 7ae3, `atlas_axis = NONE` (splice off), tier M, BASE write-back. `world.Runner(..., implant="ACTUAL_GENOME", implant_bytes=G, max_epochs=300)`. The instrumentation subclass is the X-TICKET subclass (`x_ticket/run_tk.py`), unchanged except for the logging in §4.
- **Planted genomes.** Verified statically on 2026-10-01 against MANIFEST_FROZEN with `z8.dis`:

| arm | change from founder | hex positions 43–45 | disassembly | bit distance | sha256[:12] |
|---|---|---|---|---|---|
| F | none | `c1 ec 22` | | 0 | 42b930f55cc1 |
| AC | 44 EC→AC | `c1 ac 22` | 44 = `XOR A,H` | 1 | 65d0e50b8d2e |
| C3 | 43 C1→C3 | `c3 ec 22` | 43 = `JP 22EC` | 1 | e589ac501689 |
| C3AC | both | `c3 ac 22` | 43 = `JP 22AC` | 2 | 272f3b645ce3 |
| NC-KO | 52, 53 → 00 00 (N1 `ko_ldir`) | | LDIR → NOP NOP | 9 | 576051df4e76 |

- **n per arm:** F 256, AC 384, C3 64, C3AC 64, NC-KO 32.
- **Common random numbers.** The same seed index is used across arms, so seed s gives the same initial background and the same epoch-1 pairing order.

## 3. Seeds
- **Base: `42_000_000 + s`.**
  - F: s ∈ [0, 256).
  - AC: s ∈ [0, 384).
  - C3 and C3AC: s ∈ [0, 64).
  - NC-KO: s ∈ [0, 32).
  - Replays used only as controls: X-TICKET 9_998_000 + {0, 2, 14, 35, 59, 121}.
- **Used ranges checked** (all 7ae3 / z8 world seed bases found):
  - `roles/Nestor/**/*.py` seed constants;
  - the W2-12 `table_summary.json` seed ranges;
  - the W2-22 PREREG.

  | base / range | used by |
  |---|---|
  | 9_998_000–127 | X-TICKET; W2-14 used 0–39 |
  | 9_999_000–10_000_199 | W2-22 FIELD (s 1000–1599) and FREE (s 1000–2199) |
  | 9_996_000–079 | C-CRITICAL-MASS |
  | 9_997_000–063 | X-DOSE-CURVE |
  | 9_993_000–063 | X-CRITICAL-MASS |
  | 9_990_500–649 | C-RUNAWAY |
  | 9_985_000–023 | C-NORECOMB |
  | 9_980_000–015 | X-H2-NORECOMB |
  | 9_970_000–015 | X-H2-7AE3 |
  | 9_999_000–063 | X-DECAY |
  | 9_999_500–563 | X-STERILE |
  | 9_999_800–863 | X-ATOMIC |
  | 12_000_000–079 | C-ATOMIC |
  | 14_000_000–063 | C-CORE |

  Other bases present in Nestor scripts:
  - 1_000_000; 4_440_001; 5_550_001;
  - 9_100_000; 9_120_000; 9_130_000; 9_140_000; 9_200_000; 9_300_000; 9_400_000;
  - 9_700_000–9_740_000; 9_800_000; 9_850_000;
  - 9_900_001; 9_900_101; 9_900_500; 9_910_000;
  - 9_950_000; 9_960_000; 9_975_000; 9_988_000; 9_990_000; 9_995_000; 9_999_700;
  - 11_000_000–31_700_000 (millions); 77_190_000.
- **Freshness.** No `42_0xx_xxx` constant appears in any Nestor script. The only 8-digit 42xxxxxx strings in the worktree are scores or IDs in CW01/observatory JSON, from a different world.
- **Re-check at freeze** against EXPERIMENT_GRAPH.jsonl and LEASES.jsonl.

## 4. Readouts
Matched definitions: the same code in every arm, and identical to X-TICKET.
- **R1 (primary).** B ≥ 163 at epoch 300.
  - B is the X-TICKET `cbirths`: causal births whose parent is in the founder's causal set, closed under causal births.
  - It is a cumulative count, not a maximum of noisy draws.
- **R2.** B ≥ 27 (E27, "reach").
- **R3.** P(B ≥ 163 | B ≥ 27), per arm.
- **R4.** Epoch-1 founder loss: the causal set has no live member at the end of epoch index 0. This is `traj[0][0] == 0`.
- **R5 (genotype, not event side; W2-25 F3).**
  - Every causal birth in the family is logged as: epoch, parent oid, child oid, parent side, child bytes 37 and 41–52, child sha256, fid.
  - The genotype class comes from a frozen static classifier on bytes:
    - F-like;
    - AC (44 = AC);
    - C3 (43 = C3);
    - C3AC;
    - other side-switch (49 ∈ {5C, 59}, 37 = 81, or any A ← f(A, C|H) at 37–47 from the N17d list of 170);
    - other.
  - Switch provenance (W2-25 F5) is classified as single-bit copy error, multi-byte change, or partner-authored (prov).
- **R6 (genome storage, mandatory for every run).** At the end of the run, or at the stop, write `final/<arm>_<s>.json.gz` containing every live organism: oid, anc, slot, genome hex, regs, fz, fc, causal-set flag, birth epoch, parent. This applies to extinct-stopped runs too.
- **Excluded readouts.**
  - maxA and occupancy, which are label-flood contaminated (W2-14).
  - Any max over noisy re-scored values (W2-19).
  - depth_world is reported as secondary only, and never as decisive (W2-25 F10: it is a record statistic).
- **Stop rule.** The run reaches epoch 300, or stops earlier if the founder-ancestry count A = 0 and the causal set is empty. There is no `runaway_decided` early stop, because final genomes and persistence must be read at epoch 300.

## 5. Decision rules (frozen as numbers)
The bands are unions of central 95% binomial intervals over each model's calibrated range, at the arm's n.

| arm (n) | M2 band (count) | M3 band | M1 band |
|---|---|---|---|
| F (256) | 0–13 | 0–17 | 1–10 |
| AC (384) | **0–26** | **7–99** | 6–58 |
| C3 (64) | **0–13** | **≥ 41** (floor 0.75) | n/a |
| C3AC (64) | **0–17** | **≥ 41** (floor 0.75) | n/a |

**D1. The mapping test, decided by C3 and C3AC jointly.**
- **NEAR-CRITICAL MAPPING HOLDS** (kills H-SUPER-M3): both counts ≤ the M2 upper bound (C3 ≤ 13 and C3AC ≤ 17).
  - Static per-call gains then translate roughly proportionally into lifetime fecundity, and a +45% lifetime contrast cannot come from one-bit variants.
- **KEEP-LEVERAGED MAPPING HOLDS** (kills H-NEAR-M2): both counts ≥ 41/64.
- **STATIC LAW FAILS**: either count lies in the gap (C3 in 14–40, or C3AC in 18–40), or the two arms disagree.
  - This kills **F\* kill criterion 2** (an implanted founder outside its static-law band), whichever mapping is used. Report it as F\* FALSIFIED AT RUNG 3 (BASE).

**D2. The W2-17 morph (AC).**
- AC count ≥ 27/384 kills "AC is near-critical plus luck" (M2).
- AC count < 6/384 kills H-SUPER-M1 and M3 for AC.
- A count in 6–26 is UNRESOLVED for AC. This is expected with probability about 0.37 if M1's midpoint is true.
- Note: if D1 says the mapping is keep-leveraged but AC lands at ≤ 26, then "supercritical variants exist" survives while **W2-17's specific morph headline is killed**.

**D3. Does the morph CAUSE persistence?** This is decided only if the arm has E27 ≥ 8.
- "A supercritical morph causes persistence" is SUPPORTED only if all of the following hold:
  1. AC's P(163|27) has its CP lower bound > 0.45;
  2. AC's P(163|27) exceeds the founder's (Fisher one-sided p < 0.05);
  3. in ≥ 80% of AC-arm runs with B ≥ 163, ≥ 80% of the family's live members at epoch 300 carry a side-0 genotype (R5/R6).
- It is KILLED if AC's P(163|27) ≤ the founder's, or if AC-arm runaways are carried by reverted or non-side-0 genotypes.

**D4. The anomaly (founder arm).** This needs E27 ≥ 8.
- H-ANOMALY is CONFIRMED if the CP lower bound of the founder's P(163|27) is > 0.544, the maximum over the calibrated models. Persistence is then not explained by the static law under any mapping.
- It is WITHDRAWN if the CP upper bound is < 0.8; X-TICKET's 4/4 was then luck.

**D5. Timing (re-tests W2-25 F2 on fresh seeds).** In founder-arm runs with B ≥ 163, compare the epoch of the first side-0 *genotype* birth with the epoch of the 27th causal birth.
- If ≥ 50% have the side-0 genotype arriving after the 27th birth: "the morph is not necessary for crossing 27" is CONFIRMED.

**Power** (from calc_bands.json, at each model's midpoint):

| arm | test | power |
|---|---|---|
| C3 | M3-true falls outside the M2 band | 1.00 |
| C3 | M2-true falls outside the M3 band | 1.00 |
| C3AC | either direction | 1.00 |
| AC | M3-mid falls outside M2 | 1.00 |
| AC | M1-mid falls outside M2 | 0.63 |
| AC | M2-mid falls outside M1 | 0.05 |

So **D1 is decisive with near certainty. D2 is decisive only if the truth is at the M3 end.**

## 6. Eligibility count (computed before the run)
**Expected events (n × model range):**

| arm | E27 | B ≥ 163 |
|---|---|---|
| F | 7.3–20.0 | 2.3–10.8 |
| AC (M2) | 12.5–39.1 | |
| AC (M1, M3) | 26–98 | |
| C3 / C3AC (M2) | 2.8–12.9 | |
| C3 / C3AC (M3) | 55–64 | |

**Rules:**
- D3 and D4 each need ≥ 8 E27 events in the arm. Otherwise that rule is INELIGIBLE, not a null.
- If the founder arm's E27 falls below 8, D4 is INELIGIBLE. The model probability of this is ≤ 0.35 at the low end of the range.
- D1 and D2 need no conditioning and are always eligible.

## 7. Planted controls with demonstrated reachability (gates; all must pass before any data are read)
- **PC1. The positive outcome is reachable in this exact harness.**
  - Replay X-TICKET seeds 14, 35, 59 and 121 (B ≥ 163 at epochs 72, 29, 33 and 27), seed 2 (a near miss, B = 26) and seed 0 (a loss) with the founder arm's harness, max_epochs = 300.
  - The full 300-epoch `traj` (N, A, B) must equal `x_ticket/results/*.json` **bit-for-bit**.
  - Feasibility is already demonstrated: W2-14 v0 matched 4/4 seeds over 40 epochs.
  - This also tests that `max_epochs = 300` does not perturb the first 300 epochs. The cell is COEVO_ENV, not NONSTATIONARY_SHIFT; the self-test confirms it.
- **PC2. Implant integrity.** At epoch 0, the implanted organism's bytes hash to the arm's sha256 in §2, in every run (asserted).
- **NC1. The ruler cannot credit non-authored copies.**
  - Plant NC-KO (LDIR knocked out; N1 showed 0/1,500 overwrites) on fresh seeds 42_000_000 + [0, 32).
  - Required: B = 0 in 32/32. If any B > 0, STOP. That would be an instrument defect ("similarity is not copying").
- **NC2 / PC3. The genotype classifier (static).**
  - Classify the 5 planted genomes, plus all 8×64 one-bit neighbours of each.
  - Labels must be exact.
  - For PC3, a synthetic final-population dump with known composition must be recovered exactly.
- **Eligibility of the instrument for the C3 arms.** Before the run, re-assay C3 and C3AC under *exact-identity* scoring (W2-24 next question 1; W2-24 adversarial 2: exact side-0 keep is 251/484, against FID 0.97).
  - This is about 2 CPU-min, static.
  - If exact keep removes the C3 keep gain, the M3 prediction for C3 must be **re-derived before freeze**, never after.

## 8. CPU estimate
**Per-run costs:**
- A full 300-epoch BASE world run costs about 32 CPU-s. X-TICKET took 128 × 2,000 epochs in 45 min wall on 10 processes, about 211 s per run; W2-25 quotes about 25 s.
- A runaway (saturated field, heavy P-11) costs about 85–100 s (W2-14 max 84.5; W2-22 ATOMIC world 60–96).
- Early-extinct runs cost about 1–5 s.

**Arm costs:**

| arm | runs × cost | core-h |
|---|---|---|
| F | 256 × ~21 s | 1.5 |
| AC | 384 × ~25 s | 2.7 |
| C3 | 64 × ≤ 90 s (worst case, M3 true) | 1.6 |
| C3AC | 64 × ≤ 90 s (worst case, M3 true) | 1.6 |
| PC1 | 6 × 90 s | 0.15 |
| NC1 | 32 × 21 s | 0.2 |
| self-tests | | 0.1 |
| **Total** | | **≈ 7.9** |

- **Plan:** 10 core-h including a 25% margin.
- **Checkpoint.** After the first 32 runs per arm, project the total. If the projection exceeds 15 core-h, stop and report with no verdict. Data read at the checkpoint are not used for any decision.
- **Optional cheaper core.** F + C3 + C3AC only (D1 and D4) is about 5 core-h.

## 9. Envelope check (MWO-0004 R2)
- Local, unpaid compute.
- ≤ 16 core-h per item: **10 planned, 15 hard cap.**
- ≤ 48 core-h per seat per rolling 24 h: **before dispatch, sum Nestor's Wave-2 compute over the trailing 24 h.**
  - Wave-2 workers so far are several core-h: W2-22 66 min, W2-14 45, W2-21 about 35, W2-17 23, W2-12 25, W2-23 17, and so on.
  - So this item plus Exp 3 fits. **All three items together (about 28 core-h) fit only if the trailing usage is ≤ 20 core-h.**
- A canonical Fabric lease is required (substantial use).
- No new packages.
- This IS a new preregistration, so it needs authorization (R2's last clause).

## 10. Failure modes
1. **The static bank panel is not the in-world partner distribution** (W2-14's single largest lever).
   - Mitigation: the bands are calibrated on the founder in-world, and only *ratios* are imported.
   - Residual risk: if C3's keep gain is specific to the bank (for example, kin-dominated partners after saturation), M3 over-predicts. D1 then lands in the gap, and F\* is correctly charged.
2. **Mutation erodes the implant.**
   - Bytes 43–45 are reachable by single-bit copy errors (a JP retarget, W2-24 adversarial 1). C3's protection can be lost by descendants.
   - R5 measures this. It is not a design flaw, but it lowers M3's realized rate. Hence the 0.75 floor.
3. **The generation cap stands in for the 300-epoch horizon.**
   - This mainly affects near-critical (M2) tails. Both G = 40 and G = 60 are inside the bands.
4. **B counts kin re-conversions after saturation** (W2-14: B exceeds label growth by 719–2,284 in big runaways).
   - This inflates B ≥ 163 *after* saturation only, which affects all arms equally.
   - B_xk (births onto non-members, W2-22) is reported as a secondary.
5. **Outcome-dependent run cost:** the C3 arms are expensive only if M3 is true. The budget covers the worst case.
6. **A seed-index pairing artifact.** Shared seeds share the initial background.
   - The analysis is per arm (unpaired). A paired analysis is secondary only.
7. **Readout drift.** Any change to the X-TICKET subclass beyond logging fails PC1. PC1 is the guard.


---

## NESTOR AMENDMENT A (2026-10-01, before freeze; this draft is still NOT frozen and NOT dispatched)

**Source.** W2-40 (`inference_saturation_wave2/W2-40_c3_bands/`).

**Why the bands change.** Keep and m are re-derived on the **class ruler**: FID ≥ 0.9, plus bytes 43, 44, 45 and 49 equal to the parent. W2-40 shows from `world.py` that births are counted by FID and that BASE write-back has no keep test. Exact identity would therefore misdescribe the world.

**Replacement count bands for §5:**

| arm | NEAR-CRITICAL (M2) | KEEP-LEVERAGED (M3) | static law fails |
|---|---|---|---|
| C3, n = 64 | ≤ 14 | ≥ 32 | 15–31 |
| C3+AC, n = 64 | ≤ 17 | ≥ 41 | 18–40 |
| AC, n = 384 | — | — | a count ≥ 28 kills M2 (was ≥ 27); a count < 6 kills M1 and M3 |
| F, n = 256 | 0–13 | 0–17 | M1 1–10 |

**Open condition.** W2-41 is re-measuring the static inputs with **self-carried in-world donor contexts**. W2-26 found that these flip some side-1 7ae3 genomes to side-0 conversion. If W2-41 changes the per-genome inputs materially, the bands must be re-derived again before freeze.
