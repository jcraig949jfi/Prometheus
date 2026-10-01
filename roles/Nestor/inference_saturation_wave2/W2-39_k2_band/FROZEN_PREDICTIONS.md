# W2-39 FROZEN PREDICTIONS: F* kill criterion K2 (morph founders), the M* prediction bands

- **Frozen at commit:** `<COMMIT_HASH_PLACEHOLDER>` (fill with the commit that first adds this file; the bands below are valid only for world data generated after that commit)
- **Written (date -u):** 2026-10-01T02:56:37Z
- **F\* definition:** `roles/Nestor/inference_harvest_2026-09-30/NPE_COMPETING_THEORIES.md` WAVE-2 CORRECTIONS (D)-(E), commit 32135ddc5.
- **Authorization:** this file authorizes nothing. It is the pre-registration that has to exist before Experiment 1 (K2, in-world) can be authorized.

## 1. Reference process M* (as run)
- Code: `mstar.run(geno, seed)`, which equals `w22.run2("BASE", seed, "FREE", "BANK", "CARRY", True, T=300, bank=banks.pkl BASE, pool=banks.pkl POOL, mech=None, stop="xk")`. This is exactly W2-22's FREE BANK call.
- Implant: `ffield.G7` is rebound to the genotype for the duration of one call. No source file is edited.
- Self-test: the stock founder reproduces W2-22 `runs_FREE.jsonl` exactly on 5/5 seeds (all readouts plus the full trajectory). See `v0_selftest.json`.
- Genotypes (all built from `run_ds.donor_genome()`, and the original bytes are asserted before each edit):

  | name | edit |
  |---|---|
  | F | founder 7ae3 |
  | AC | byte 44 EC→AC |
  | 81 | byte 37 A5→81 |
  | C3 | byte 43 C1→C3 |
  | C3+AC | both 43 and 44 |

- Seeds: 39_390_000 + s, s = 0..799. These are fresh, disjoint from every offset used in inference_saturation_wave2, and the same seeds are used for every genotype. N = 800 per genotype.

## 2. M* estimates (Jeffreys 95% CI)
Notation:
- **cap** = the FREE `free_cap256` stop (256 members).
- **C−** counts a cap-stopped run only by the B_xk it reached.
- **C+** counts a cap-stopped run as a success.

| geno | R1 = P(B_xk≥27), C− | R1, C+ | R2 = P(maxA≥40 & B≥27) | R3 C− = P(B_xk≥163 \| B_xk≥27) | R3 C+ |
|---|---|---|---|---|---|
| F | 37/800 = 0.046 [0.033, 0.063] | 0.079 [0.062, 0.099] | 0.040 [0.028, 0.055] | 7/37 = 0.19 [0.09, 0.34] | 29/37 = 0.78 [0.63, 0.89] |
| AC | 215/800 = 0.269 [0.239, 0.300] | 0.280 [0.250, 0.312] | 0.253 [0.223, 0.284] | 171/215 = 0.80 [0.74, 0.85] | 0.93 [0.89, 0.96] |
| 81 | 237/800 = 0.296 [0.265, 0.329] | 0.308 [0.276, 0.340] | 0.279 [0.249, 0.311] | 204/237 = 0.86 [0.81, 0.90] | 0.92 [0.89, 0.95] |
| C3 | 269/800 = 0.336 [0.304, 0.370] | 0.461 [0.427, 0.496] | 0.336 [0.304, 0.370] | 30/269 = 0.11 [0.08, 0.15] | 0.99 [0.98, 1.00] |
| C3+AC | 609/800 = 0.761 [0.731, 0.790] | 0.763 [0.732, 0.791] | 0.761 [0.731, 0.790] | 594/609 = 0.975 [0.961, 0.986] | 1.00 [0.996, 1.00] |

## 3. Band construction
- **M\*'s own uncertainty:** the Jeffreys posterior p ~ Beta(x+½, N−x+½).
- **World binomial noise:** K | p ~ Bin(n, p).
- **Predictive distribution:** K ~ BetaBinomial(n, x+½, N−x+½).
- **Inside the band:** a world count k is inside iff P(K ≤ k) > 0.025 and P(K ≥ k) > 0.025. The code is in `band.py`.
- **Cap censoring is resolved against the kill.** Each band is a **hull**:
  - R1 hull = [k_lo of the C− band, k_hi of the C+ band];
  - R3 hull = [k_lo of the C− band, k_hi of the C+ band].
  - The uncensored M\* value lies between C− and C+, so a world count can kill only if no censoring resolution admits it.
- **R3 is conditional.** Its band uses n = m, the world arm's realized count of runs with B_xk ≥ 27. The m below is the expected value, m = round(n · R1_M\*). At scoring time, `k2_decide.py` recomputes the band at the realized m.

### Frozen bands (world counts, inclusive; proportions in brackets)

| geno | n = 64: R1 | m | R3 | n = 128: R1 | m | R3 | n = 256: R1 | m | R3 |
|---|---|---|---|---|---|---|---|---|---|
| F | 0–10 [0, 0.156] | 3 | 0–3 (any) | 2–17 [0.016, 0.133] | 6 | 0–6 (any) | 5–31 [0.020, 0.121] | 12 | 0–12 (any) |
| AC | 10–25 [0.156, 0.391] | 17 | 10–17 | 24–47 [0.188, 0.367] | 34 | 22–34 | 53–88 [0.207, 0.344] | 69 | 47–68 |
| 81 | 12–27 [0.188, 0.422] | 19 | 13–19 | 27–51 [0.211, 0.398] | 38 | 28–38 | 60–96 [0.234, 0.375] | 76 | 58–75 |
| C3 | 14–38 [0.219, 0.594] | 22 | 0–22 (any) | 32–71 [0.250, 0.555] | 43 | 1–43 | 69–136 [0.270, 0.531] | 86 | 4–86 |
| C3+AC | 42–55 [0.656, 0.859] | 49 | 45–49 | 87–107 [0.680, 0.836] | 97 | 91–97 | 179–210 [0.699, 0.820] | 195 | 184–195 |

- **R3 bands by realized m (C− lo … C+ hi):** see `a1_results.json` → `R3_band_by_m`; `k2_decide.py` computes them exactly.
- **Null false-kill rate per arm** (world law equal to M\*'s; union bound over R1 and R3, worst censoring treatment) at n = 128:

  | arm | rate |
  |---|---|
  | F | 0.022 |
  | AC | 0.049 |
  | 81 | 0.047 |
  | C3 | 0.029 |
  | C3+AC | 0.062 |

  - The family-wise rate over the two mandatory morph arms is about 0.10.
  - Over all four morph arms it is about 0.19.
  - This is not corrected. The F\* text fixes 95% bands per readout, and the multiplicity is declared here instead.

## 4. World arm requirements (what the world experiment must measure)
- **Physics and setup:**
  - X-TICKET physics: 7ae3 C9 H2 arm-B cell (atlas_axis NONE), tier M, BASE write-back, splice off, stock z8.
  - Horizon: 300 epochs.
  - One implant per run: `implant="ACTUAL_GENOME"`, with `implant_bytes` set to the genotype bytes exactly as in `mstar.GENOS`.
  - Seeds: fresh, the same across arms, disjoint from 39_390_000..39_390_799 and from all earlier ranges.
- **Readouts:**
  - B_xk must be computed with W2-22's definition: causal births in the founder's causal lineage whose victim was not anc==0 before the interaction.
  - It may come from `world.Runner` plus an equivalent B_xk logger, or from `w22.run2(..., "FIELD", "FULL", ...)`. The latter is bit-exact to the world per W2-14 v0, but this must be re-verified on ≥ 3 seeds for the morph implants before use.
  - Record k27 = #runs with B_xk ≥ 27 by epoch 300 and k163 = #runs with B_xk ≥ 163 by epoch 300.
  - Record kB27 = #runs with B ≥ 27 for the founder arm.
- **Arms:** F (mandatory, positive control), AC and 81 (mandatory), C3 and C3+AC (optional). n is the same for every arm and is fixed before launch: 64, 128 or 256.

## 5. Decision rule (exact; implemented in `k2_decide.py`, frozen with this file)
1. **Positive control.**
   - Compare the founder arm's kB27 with the predictive band of the world's own historical 4/128 (BetaBinomial(n, 4.5, 124.5), equal 2.5% tails).
   - The band is 0–6 at n = 64, 0–11 at n = 128 and 1–21 at n = 256.
   - If kB27 is outside it, **K2 = VOID**. The world arm does not reproduce 0.031, so no morph comparison is scored.
2. **Per arm g.**
   - **R1 OUTSIDE** iff k27 is outside the R1 hull for n.
   - **R3 OUTSIDE** iff k27 ≥ 1 and k163 is outside the R3 hull at m = k27. If k27 = 0, R3 is NOT SCORED.
   - The arm is **OUTSIDE** if R1 or R3 is OUTSIDE.
3. **K2 verdict.**
   - **KILLED** if any morph arm (AC, 81, plus C3 and C3+AC if run) is OUTSIDE.
     - If the founder arm is also OUTSIDE, the kill is recorded as "not morph-specific". It then counts against F\* on the founder genotype as well, and the K4 residue reading becomes the default explanation.
   - **PASSED-AT-BAND** if the control passes and every morph arm is INSIDE.
   - A pass means only that the world is inside M\*'s 95% prediction band. It is not the ±0.05 / ±0.20 equivalence of the F\* claim. The equivalence reading needs world-arm CIs and is scored separately under F\* (D)'s KILLED/PASSED/UNRESOLVED rule.
4. **Timing.** World data that predate the commit filled in above can be scored only as consistent or inconsistent.

## 6. What M* predicts in words (falsifiable now)
- **Each single morph founder:**
  - reaches B_xk ≥ 27 about 6x as often as the founder (0.27–0.30 vs 0.046);
  - reaches B_xk ≥ 163 unconditionally at 0.21–0.26 vs 0.009.
  - This is W2-25's **H-SUPER** region (≥ 0.15 and ≥ 4x).
- **If the world morph arm follows H-NEAR** (R1 ≈ 0.08), the R1 band excludes it with probability ≥ 0.97 at n = 64 and ≥ 0.9999 at n = 128. **That outcome kills F\*.**
- **C3+AC** is predicted to run away in about 74% of seeds.
- **C3 alone** reaches 27 in a third of seeds. It mostly fills the 256 cap through label spread before B_xk reaches 163, so M\* cannot pin its R3 (hull 1–43 of 43).
