# W2-29: is the world's post-27 persistence explained by background residue, by morphs, or by neither?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run:** 02:26:02Z–02:57:43Z. About 67 CPU-min of the 90 allowed (FULL 49.7, BANK replay 13.7, genotyping 2.4, gate 0.75), with at most 6 processes.
> - **Files:** PREREG.md, `runs_FULL.jsonl`, `a1_analysis.json` (pre-registered result), `a2_ring.json` / `a2_func.json` (deviation variants), `a3_extra.json`.

## Answer
**UNRESOLVED**, under the pre-registered rule and under both sensitivity variants.

**The test reframes the question.** On 600 seed-matched seeds, the world (FIELD FULL) persists after B ≥ 27 in only **8/22 = 0.36** runs on B_xk, or **9/22 = 0.41** on B.
- **W2-22's "4/4" was the top of a small sample:** 9/22 vs 4/4 gives p = 0.096.
- **The world-vs-BANK gap shrinks.** It was 4/4 vs 9/33 (p = 0.011). Now:
  - on B_xk: 8/22 vs 5/33, one-sided p = 0.069, ratio 2.4 [0.94, 6.24];
  - on B: 9/22 vs 9/33, p = 0.22.
- **Morph-stratified, the direction is FULL > BANK** (Mantel-Haenszel OR 3.8, CMH p = 0.051). It is not significant in any pre-registered test.

**Morphs are not necessary.** Three B_xk successes have **no side-0 genome anywhere in the causal lineage**:
- FULL s1438 (B 347);
- FULL s1469 (B 296), where 78% of births are the W2-24 keep variant 43→C3;
- BANK s1505 (B 327).

## Eligibility
- Prior 4/128 predicts 18.6 conditioned runs at 600 seeds; P(≥ 10) = 0.99.
- Realized: FULL 22/600, BANK 33/600 (W2-22's runs on the same seeds, 1000–1599). **ELIGIBLE.**
- Equivalence: `run3` = `w22.run2` = `ffield.run` on 12/12. All 33 BANK replays match W2-22's B and B_xk.

## Results

**P(≥ 163 | B ≥ 27)**

| arm | n | E27 | B_xk ≥ 163 | B ≥ 163 |
|---|---|---|---|---|
| FIELD FULL (world) | 600 | 22 | 8 (0.36) | 9 (0.41) |
| FIELD BANK | 600 | 33 | 5 (0.15) | 9 (0.27) |
| one-sided p | | | 0.069 | 0.22 |

**Morph strata (success/n)**

Three morph definitions:
- **literal:** the pre-registered definition, first own LDIR with DE == 0x40.
- **ring:** a declared deviation, since z8 masks addresses to 127. Under the literal definition, 7,869 side-0 genomes with DE ≡ 64 mod 128 were missed.
- **func:** conversion only.

| definition | FULL morph | FULL none | BANK morph | BANK none | RESIDUE p | MORPH p (FULL / BANK) | verdict |
|---|---|---|---|---|---|---|---|
| literal | 4/7 | 4/15 | 2/11 | 3/22 | 0.28 | 0.18 / 0.55 | UNRESOLVED |
| ring | 6/11 | 2/11 | 4/18 | 1/15 | 0.38 | 0.091 / 0.23 | UNRESOLVED |
| func | 6/12 | 2/10 | 4/18 | 1/15 | 0.35 | 0.16 / 0.23 | UNRESOLVED |
| ring, morph by B ≤ 27 | 4/9 | 4/13 | 4/13 | 1/20 | 0.066 | 0.42 / 0.066 | UNRESOLVED |

**Controls passed:**
- the founder is negative (c1 0.875, DE 0);
- 44→AC and 49→5C are positive (c0 1.0, DE 64);
- 43→C3 is negative.

**Composition of the 13 successes**

| side-0 share of B births | runs |
|---|---|
| 0.81–0.93 (side-0 dominated) | FULL 1068, 1460, 1468; BANK 1346, 1357, 1577, 1579 |
| 0.43–0.48 (mixed) | FULL 1125, 1519 |
| 0.04 | FULL 1303 |
| none | FULL 1438, FULL 1469 (C3 0.78), BANK 1505 |

C3-rich failures: FULL s1427 (C3 0.82) and BANK s1100 (C3 0.51). Both saturated the field below B_xk 163.

## Adversarial round
1. **Power.** With 11–22 runs per stratum, only large odds ratios are detectable. The MH OR of 3.8 (p = 0.051) is a hint toward RESIDUE. **Read UNRESOLVED as underpowered, not as no effect.**
2. **The morph definition was mis-specified** (the ring mask). The deviation is declared, and the verdict is the same either way.
3. **Reverse causation.** Stratifying by when the morph appeared (B ≤ 27) removes the FULL morph effect (4/9 vs 4/13).
4. **The xk163 stop truncates late morphs.** This is conservative for MORPH.
5. **The 3 morph-free successes.** s1469 is C3. s1438 and s1505 were not fully genotyped. All three still falsify "a morph is necessary".
6. **W2-22's 4/4 was on B**, which includes kin re-conversions. On B, FULL vs BANK is 9/22 vs 9/33.

## Ledger entry (W2-29)
- **Inference.** UNRESOLVED.
  - W2-22 overstated the world-vs-BANK gap.
  - Side-0 morphs are not necessary for persistence. The 43→C3 keep variant and plain founder-type lineages also persist.
  - A residue effect of OR about 2–4 is neither shown nor excluded.
- **Confidence.**
  - High that the gap shrank.
  - High that a morph is not necessary.
  - Low on the direction of residue.
- **Strongest objection.** The test is underpowered for OR < about 5, and the morph definition needed a post-hoc ring correction.
- **Next.**
  1. FULL vs BANK at about 2,000 seeds each (about 170 CPU-min).
  2. Genotype s1438 and s1505.
  3. Treat C3 as a third stratum.
  4. Correct the morph notes: DE ≡ 64 mod 128, not literal 0x40.
