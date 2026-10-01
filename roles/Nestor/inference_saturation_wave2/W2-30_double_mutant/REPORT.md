# W2-30: double mutant C3+AC under exact identity, its one-bit neighbourhood, and sweep timescales

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run window:** 02:26:15Z–02:37:09Z. About 20 CPU-min, static only.
> - **Files:** `t1_exact_m`, `t1b_near_children`, `t1c_class_m`, `t2_neighbourhood` (~7,700 variants), `t3_analysis`, `t4_sweep_model` (each .py + .json).

## Answer

### 1. Exact m
**The ordering holds, and C3+AC remains best. Whole-genome exact identity is the wrong ruler.**

Exact BASE m:

| genome | exact m | FID m |
|---|---|---|
| F | 0.847 | 1.172 |
| C3 | 0.943 | 1.389 |
| AC | 1.175 | 1.248 |
| 5C | 1.180 | 1.240 |
| C3+AC | 1.253 | 1.469 |

- Halves that pass FID≥0.9 but are not exact differ mostly at the edge bytes 0 and 63. Only 1–8% of them touch bytes 43–45.
- These near-copies have FID m about equal to their parent's (1.17, 1.38, 1.43), so they are functionally the parent.
- **Class m** counts a half only if FID ≥ 0.9 and bytes 43, 44, 45 and 49 match the parent:

  | genome | class m (BASE) |
  |---|---|
  | F | 1.154 |
  | C3 | 1.368 |
  | AC | 1.239 |
  | 5C | 1.235 |
  | C3+AC | 1.462 |

  W2-24's ordering survives. Exact m flips C3 below AC and 5C only because of edge drift on C3's side-0 halves: exact side-0 keep is 0.519, against 0.973 under FID.
- **ATOMIC exact m:** 1.158 / 1.344 / 1.293 / 1.285 / 1.485.

### 2. Robustness to one-bit changes
- **84.4% of C3's 512 one-bit neighbours keep the protection; 82.4% of C3+AC's.**
  - Most of the failures are generic: the variant stops being a copier altogether, at bytes 23, 24, 52 and 53 among others. The founder has 66 such neighbours.
  - Neighbours that still copy but have lost the protection: C3 11, C3+AC 9.
- **Breaking bits at 43–45:**

  | byte | C3 | C3+AC |
  |---|---|---|
  | 43 | all 8 bits break it (bit 1 gives back exactly F) | all 8 bits (6 give AC-like copiers, 2 F-like) |
  | 44 | bits 2–5 give non-copiers; bit 6 gives C3+AC (a gain); bits 0, 1, 7 neutral | 7/8 bits give non-copiers; bit 6 gives C3 |
  | 45 | bit 0 gives a non-copier | bits 0 and 7 give non-copiers |

- **Bytes 44 and 45 are dual-use.** They are both the JP operand and the code at the landing site. Only 18 of 256 values at byte 44 keep the protection (6C–74, EC–F4, plus AC/EC); at byte 45 about 200 do.
- **Expected m of a copy-error child:**

  | parent | exact | class | FID |
  |---|---|---|---|
  | C3 | 0.812 | 1.306 | 1.324 |
  | C3+AC | 1.075 | 1.356 | 1.360 |
  | founder | 0.743 | 1.109 | 1.124 |

  Over all births 88% are error-free, so a C3+AC child's expected class m is 1.473 against 1.478 for the parent. The mutational load is negligible.

### 3. Rates of losing and gaining the protection
- **Per birth, by copy error:**
  - C3 loses it to a non-protected copier at 11 × 2.5e-4 = **2.75e-3**; C3+AC at **2.25e-3**.
  - Any loss, including non-copiers: 2.0e-2 (C3) and 2.25e-2 (C3+AC). The founder's generic non-copier load is 1.65e-2.
  - These loss rates are 9–24x the founder's per-birth gain rate (2.5e-4). Only exact reversion to F matches the gain rate.
- **Per interaction, by in-place mutation** (OPERAND operator at 0.002/byte, which touches operands only; world.py:484–550):
  - **Bytes 44 and 45 are opcodes in F and AC, so they are immune there. In C3 and C3+AC they are JP operands, so they become mutable in place.**
  - Protection-specific in-place loss: C3 about 2.0e-3 (44: 1.06e-3, 45: 3.2e-4, byte 2: 6.4e-4); C3+AC 2.24e-3 (44: 1.82e-3, 45: 4.2e-4).
  - Byte 43 is never mutated in place.
  - C3 → C3+AC and back both occur at 1.13e-4 per interaction.
- **Net effect:** losses are about 10x gains, but selection (about 0.07–0.27 per epoch) is about 100x any loss rate. An unprotected fraction of about μ/s ≈ 1–5% is expected.

### 4. Sweep timescales
In silico: N = 256, one interaction per organism per epoch.

**Regime A, partners from the background** (5-type class-m matrix):
- Growth relative to F: C3 1.19x, AC 1.07x, C3+AC 1.27x.
- Sweep time: C3 about 63 epochs; C3+AC about 46.
- C3 mutants arise at 0.029 per epoch from F. With establishment ~0.16, the first established C3 appears at about epoch 216.
- C3+AC from a C3 resident: about 278 epochs to establish plus about 170 to sweep.
- **The full path F → C3 → C3+AC takes about 500–700 epochs.**

**Regime B, partners from the lineage itself** (W2-24 winner-takes-both table, BASE):
- F, C3 and AC are mutually neutral.
- C3+AC beats F in both placements, and is neutral against C3, AC and C3+AC.
- Over 200 replicates, C3+AC holds a majority by epoch 2,000 in **87%**. Median **559** epochs (P10–P90: 141–1,443); median first appearance at epoch 504.
- **Under ATOMIC, contacts between kin are never promoted, so C3+AC's advantage comes only from background contacts** (m_atomic 1.486 vs 1.256).

**Prediction:** long, founder-dominated BASE 7ae3 runs should end up carrying 43 = C3 and 44 = AC.

## T1: m per genome
Setup: N = 1000, random side, ZERO donor context. BANK context gives identical exact m.

| genome | m_base exact | class | FID | m_atomic exact | class | FID | exact keep s0 / s1 | exact conv s0 / s1 | P(0 / 1 / 2) |
|---|---|---|---|---|---|---|---|---|---|
| F | 0.847 | 1.154 | 1.172 | 1.158 | 1.256 | 1.263 | 0.318 / 0.671 | 0.002 / 0.671 | 0.50 / 0.15 / 0.35 |
| C3 | 0.943 | 1.368 | 1.389 | 1.344 | 1.443 | 1.448 | 0.519 / 0.671 | 0.000 / 0.671 | 0.40 / 0.25 / 0.35 |
| AC | 1.175 | 1.239 | 1.248 | 1.293 | 1.301 | 1.304 | 1.000 / 0.401 | 1.000 / 0.000 | 0.31 / 0.21 / 0.48 |
| 5C | 1.180 | 1.235 | 1.240 | 1.285 | 1.287 | 1.288 | 1.000 / 0.411 | 1.000 / 0.000 | 0.30 / 0.21 / 0.48 |
| C3+AC | **1.253** | **1.462** | 1.469 | **1.485** | 1.486 | 1.487 | 1.000 / 0.547 | 1.000 / 0.006 | 0.23 / 0.28 / 0.49 |

Near-identical (non-exact) halves per interaction: F 0.325, C3 0.446, AC 0.071, 5C 0.060, C3+AC 0.214.

## T2: one-bit neighbourhoods (400 calls per variant)

| parent | protected | unprotected copier | non-copier | E[class m] of child | parent class m |
|---|---|---|---|---|---|
| F | 1 (= C3) | 445 | 66 | 1.109 | 1.168 |
| C3 | 432 (84.4%) | 11 | 69 | 1.306 | 1.383 |
| C3+AC | 422 (82.4%) | 9 | 81 | 1.356 | 1.478 |

- Thresholds were fixed before scoring.
- C3+AC has **no beneficial one-bit neighbour**, so it is a local optimum.

## Adversarial points
1. **Class m is defined by the type-distinguishing sites, not tuned.** It agrees with FID within 0.02. Under strict exact identity, F and C3 are subcritical, but the top of the ordering is unchanged.
2. **The 200-partner panel is small** (±0.05 on keep), but the protection classes are bimodal.
3. **The protection rule also requires max-side conversion ≥ 0.5**, so high-keep non-copiers are excluded.
4. **Regime A sends every copy error to "other".** This lowers each λ by about 5% uniformly, so ratios are unaffected.
5. **Regime B is idealised:** kin only, ZERO/BANK contexts, no non-copier loss, one birth per interaction.
6. **The in-place channel rests on reading the code**, not on a run.
7. **This is not a world run.**

## Ledger entry (W2-30)
- **Inference:**
  - C3+AC is top under every ruler.
  - FID inflation is neutral drift at the edges.
  - About 83% of one-bit neighbours keep the protection.
  - Bytes 44 and 45 are dual-use, so they are fragile and newly exposed to in-place mutation.
  - Losses are about 10x gains but far below selection.
  - Predicted C3+AC takeover in about 500–700 epochs under BASE (87% by epoch 2,000 in the kin model).
- **Confidence:** high for T1/T2 and the dual-use mechanism; moderate for the in-place exposure; low–moderate for absolute times.
- **Strongest objection:** no world run that stores genomes has shown this. Regime B is idealised, and under ATOMIC the contact advantage vanishes.
- **Next:**
  - scan stored runaway genomes for 43 = C3 / 44 = AC;
  - a design for an authorized mixed BASE run that stores genomes;
  - T1 with the lineage's own carried contexts.
