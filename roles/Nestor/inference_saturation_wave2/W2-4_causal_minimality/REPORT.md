# W2-4: causal minimality — what is the smallest causally sufficient reproductive mechanism in NPE?

> Saved by Nestor from the worker's returned text (the harness blocks report-file writes by subagents).
> - **Files in this folder:** w4_common.py, w4_run.py, w4_suff.py, w4_summarize.py, w4_maps.py; w4_results.json, w4_suff.json, w4_summary.json, w4_adversarial.json; class_maps.txt.
> - **How it was run:** statically. Single calls of the world's own `_pair_interact` via `map_common.Harness`: dense VM, ATOMIC `run_ds` runner, C7/CF, slice 300, P-11 assay. About 32 CPU-min, `python -B`.

## 0. Answer first

### (a) Conversion

- **The minimal mechanism** is one genome byte that invokes the VM block copy (E5/E7, or ED B0/B8 in the specimens), plus instructions that make the two 7-bit addresses differ by 64.
- **In evolved genomes** that comes to about 4 instructions (median 6.5 bytes) that must be PRESENT, plus about 2-3 bytes that must only not be CORRUPTED (deleting them is harmless).
- **The core is sufficient only on an inert background.**

  | background around the core | genomes still converting |
  |---|---|
  | NOP refill | 34/40 |
  | random refill | 8/40 |
  | every executed pre-copy instruction restored (median 37-53 bytes) | 40/40 |

### (b) Establishment

- Establishment adds one property: **the copy act must not depend on inherited registers.**
- It is usually **fused** into the conversion core: constant loads overwrite carried pointers. This holds for all 8 E700 genomes, both minimal families, and most state-free genomes.
- Otherwise there are **0-3 separable "state-washing" register moves** per genome (LD E,A / LD E,B / LD H,B / LD L,B / ADD HL,HL / XOR n).
  - Knocking one out keeps zero-context conversion but abolishes carried conversion: knockout/wild-type median 0.00, 22/22 confirmed.
- This establishment-only class has 26 confirmed positions across 46 genomes:

  | detected by | positions |
  |---|---|
  | carried conversion | 22 |
  | children's conversion | 2 |
  | retention | 1 |
  | two-step establishment | 1 |

  It is empty in 28/46 genomes and is not larger in state-free genomes.

### Supplied by physics (5) and environment (4)

- **Physics:**
  - the copy itself (the stock VM kills 38/38 dense genomes);
  - mod-128 address arithmetic (a 256-byte tape kills 26/38 evolved dense genomes and 8/8 E700);
  - stopping a 65,536-count copy (the slice budget; slice 1200 harms 9/38).
- **Environment:**
  - HL = 0 (own start), DE = 0, and a BC = 0 long count. Random entry registers kill 12/15 SD genomes and all `1E 40 E5`, but 0/23 state-free genomes.
  - Side-0 placement (33/38 genomes work from one side only).
  - A benign partner context. Random PARTNER registers kill 9/15 SD genomes and all `1E 40 E5`, but 0/23 state-free genomes.
  - ATOMIC write-back. Under BASE the donor's half stays intact about 50% of the time, against about 80% retention under ATOMIC.
- **What the genome contributes:**
  - a primitive call;
  - a few-byte address computation, whose content is mostly arbitrary;
  - for establishment, the CHOICE to take addresses from constants rather than inherited registers.

## 1. Readouts and class definitions

### Readouts

All are measured against fresh uniform random partners using the world's pair interaction.

| readout | definition |
|---|---|
| Z | Zero-context conversion: the partner is converted (a world birth with the donor as parent) and is ≥ 0.9 identical to the tested genome. Both register files are zero; sides alternate. |
| R | Retention: the donor's half is not converted by the partner (ZERO context). |
| K | Children's conversion: 5 converted children × 8 ZERO interactions (wild type 10 × 15). A child counts if ≥ 0.9 identical to the child. |
| C | Carried conversion: donor registers are carried along a chain, partner states come from S1's pool, steps 2..N. |
| P2 | Two-type extinction from `map_children`, using the Z joint law plus the K child law. |

Sample sizes: knockouts Z 60 and C 60; the wild type was assayed twice at Z 200 and C 200, and averaged.

### Classes

One random replacement value per position, keyed as in `core_map`.

1. **Transmitted:** the donor byte is delivered (child = donor where the victim differed) in ≥ 50% of wild-type conversions. This is a flag, orthogonal to the other classes.
2. **CONV_NEC:** Z_KO ≤ 0.25 Z_WT. **(2′) partial:** 0.25 < ratio < 0.6.
3. **EST_ONLY:** Z ratio ≥ 0.6, AND any of:
   - C_KO ≤ 0.25 C_WT (with C_WT ≥ 0.1);
   - K_KO ≤ 0.25 K_WT;
   - hijack rate up by 0.25;
   - P2_KO ≤ 0.5 P2_WT.
4. **Position-level tests:**
   - *Deletion test:* every byte of an executed pre-copy instruction is set to 00 (NOP). If corruption kills Z but deletion does not, the environment default (or the remaining chain) supplies that function.
   - *Operand-supply rescue:* the knockout is run with entry registers set to the wild type's registers at the copy.
5. **Genome-level perturbations:**
   - environment: one entry register random; flags set; all donor registers random; all partner registers random; side 0 only or side 1 only; BASE write-back;
   - physics: stock VM; 256-byte tape; slice 150 / 600 / 1200.

### Controls

- **Repeatability:** every EST or partial call was re-assayed with the same value and fresh seeds at 2× N, and again with a second replacement value.
- **Null:** 12 wild-type pseudo-knockouts per genome, scored by the same rule.
- **Sufficiency:** keep S_conv, S_est or S_exec, and refill the rest (random × 2, NOP × 1).

## 2. Panel

- **SF 15 and SD 15:** stratified from core_map.json, 8 × 7ae3 + 7 × ffa6 each. SD genome cf974a34 was drawn twice (duplicate corpus rows), which gives a free replicate.
- **E700:** 8 epoch-700 genomes from run 16000006.
- **Specimens:** 7ae3, cb7f, c2a8.
- **Minimal copiers:** `1E40E5` and `2E001E40E5`, each with 3 random paddings.
- **Excluded:** c2a8 has Z = 0.013 but C = 0.41 (an anti-zero donor), so its classes are undefined.

## 3. Results

### Class sizes

Per-genome median, with IQR and range in brackets.

| group | CONV_NEC | partial | EST first call | EST confirmed (total) | deletion-necessary instructions | transmitted | passengers |
|---|---|---|---|---|---|---|---|
| SF | 8 (6-11, 3-19) | 0 | 1 | 0 (total 9) | 3 | 63 | 53 |
| SD | 8 (6-9, 5-20) | 0 | 1 | 0 (total 13) | 4 | 63 | 54 |
| E700 | 9 | 1 | 1.5 | 0 (total 1) | 5 | 63 | 52.5 |
| SPEC (7ae3, cb7f) | 13, 6 | 0 | 0 | 0 | 3, 3 | | |
| MIN3 | 3 | 0 | 0 | 0 | 2 | | |
| MIN5 | 4 | 0 | 1 | 1 (byte 0 = 2E) | 2 | | |

- FOR's collapse positions agree: 268/293 are CONV_NEC here.
- E700 genomes are near-identical across all 8: LD HL,4BBF (positions 14-16), INC HL (17), LD DE,32xx (20-21), E7 (24). Their EST set is empty because establishment is fused.
- **Confirmed carried-context (C) washers** are all executed register/ALU moves feeding E, D, L or H, or their sources A, B, C. They are 3 ∩ 4: the environment does the same job at birth.
- **SF vs SD:**
  - The number of EST positions does not differ (MWU p = 0.71).
  - SD genomes instead rely on the environment: zero entry registers (12/15) and a zero partner (9/15). The second is the T5 execution field.
- **Passengers:**
  - Transmission is near-total (median 63/64).
  - Passengers are a median of 53/64 positions, and about half of them are executed.

## 4. Sufficiency

Z ratio to wild type; genomes count as sufficient at ratio ≥ 0.5.

| kept core | fill | SF | SD | E700 | SPEC | MIN3 | MIN5 |
|---|---|---|---|---|---|---|---|
| S_conv | random | 1/15 | 2/15 | 5/8 | 0 | 3/3 | 3/3 |
| S_conv | NOP | 34/40 evolved genomes keep Z (groups pooled) | | | | | |
| S_exec (median 37-53 bytes) | random | 40/40 evolved genomes keep Z; C ratio 0.91-1.03 | | | | | |

- **MIN5:** S_conv alone gives C ratio 0.00. S_est (which adds the 2E byte) gives 0.89, in 3/3 paddings.
- **NOP fill fails in 6 genomes,** where the core reads background bytes as data.
- **The missing ingredient is path permissivity,** an accumulation of small, nearly additive risks. It is not organization. This is consistent with S3 and W2-13.

## 5. Adversarial loop

- **Noise:**
  - 0/540 null pseudo-knockouts were called EST, against a 1.7% first-call rate.
  - C-readout kills reproduce 22/24.
  - P2-only kills reproduce 1/22, so drop P2 as a readout.
  - Only 12/26 confirmed calls stay EST under a second value, so the class is a property of (position, value), not of the position.
- **Overlaps:**
  - 2 ∩ 3 is pleiotropic: constant loads both build addresses and wash state.
  - Only 64% of CONV_NEC bytes lie in deletion-necessary instructions. The other 36% are corruption-only.
  - So a random-value knockout is a **corruption screen, not a function screen.**
- **The five-class split fails** in three places:
  - transmission is near-total;
  - conversion and establishment fuse in constant loads;
  - corruption and deletion disagree.
- **Proposed replacement:** (A) a quantity-supply table, and (B) readout-indexed necessity sets under both deletion and corruption.

## 6. Direct answers

- **(a) Conversion** = a primitive byte + a 1-4-instruction address computation + a traversable path.
  - Constructed minimum: `1E 40 E5`.
  - Evolved: about 4 instructions, with ~6.5 function bytes plus 2-3 corruption-sensitive bytes, which matches FOR's ~8.
- **(b) Establishment** = (a) + independence from inherited registers.
  - Minimal case: one instruction (`2E 00`), shown to be sufficient.
  - It is exactly what the environment stops supplying after birth: **an internalized environmental function.**

## Ledger entry (W2-4)

- **Result:**
  - Conversion core: median 8 corruption-necessary bytes, ~6.5 function-necessary (~4 instructions, copy op included).
  - Establishment-only: 26 confirmed positions (22 carried-state washers); empty in 28/46 genomes; fused in E700 and most SF.
  - SF vs SD: no difference in class 3. SD needs zero entry registers (12/15) and a zero partner (9/15).
  - Passengers are jointly required as an inert path (random fill 8/40, NOP fill 34/40).
  - The copy primitive, the wrap, the budget stop, placement and ATOMIC retention are all supplied.
- **Confidence:**
  - high: C-type EST, the deletion/corruption split, insufficiency on a random background;
  - medium: the genome-level environment and physics attributions;
  - low: the K/R/P2 calls.
- **Strongest objection:**
  - Classes depend on the operator and the replacement value (12/26 survive a second value).
  - Establishment is proxied by single-interaction readouts, not measured in the world.
- **Unresolved:**
  - separating fused 2 ∩ 3 bytes;
  - whether NOP-fill sufficiency is partly zero-painting;
  - c2a8;
  - the specimens in their native cells.
- **Next:**
  1. Readout-indexed deletion necessity with K at N ≥ 200, with P2 dropped.
  2. An in-world scramble of passengers outside S_exec (T3's falsifier).
  3. A source-swap screen for washers.
  4. Block partner execution of the donor half, to measure T5's share of SD conversion.
