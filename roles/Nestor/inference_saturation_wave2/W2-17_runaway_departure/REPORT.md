# W2-17: why BASE 7ae3 departs from criticality near depth 20

> Saved by Nestor from the worker's final message; condensed. The worker could not write this file itself.
> About 23 CPU-min. Bit-exact replays of existing runs; no new world runs; no git writes.
> Data: a1–a9 JSON and the r3_out/ and r7_out/ replay logs, all in this folder.

**Answer: the departure is a two-type mixture, not a density switch.**
- The founder type copies from side 1 and is subcritical: static m ≈ 0.85, realized 0.80–0.89.
- Rare heritable morphs copy from side 0 and are supercritical: static m 1.2–1.3, realized 1.08 in runaways.
- In the world the morphs arise through single-byte switches: 44 ec→ac (one bit flip) and 37 a5→81.

**Evidence that the morph drives the runaways**
- 11 of 12 runaway deep chains are side-0 copiers. 10 of 11 controls are pure side-1 copiers (p ≈ 1e-4).
- Unselected X-TICKET seeds 0–63: 2 of the 2 morph runs became runaways vs 0 of 61 runs without a morph (p = 0.0015).
- Copy side is heritable: 0.93 between parent and child.
- About 3.5% of causal births switch from side 1 to side 0.
- The one exception, CRW_75, carries a frameshifted side-1 morph with high keep_wrong. That is the profile W2-3 predicted in P6.
- 3 of 12 runaways root outside the founder's labelled family, a label leakage caused by frameshift.

**Depth tail**
- Observed: 3 runs at depth 14–21, against 9.5–12 predicted by every smooth single-process model.
- Observed P(≥161 | ≥22) = 0.84, against 0.137 predicted by 1/d.

**Kin effects**
- Kin repair accounts for 60–75% of conversions once at least 30% of the population has been recently copied (q ≥ 0.3).
- Kin repair does not rescue the founder type. Net per interaction: side-0 type +0.11, side-1 type −0.01.

**Verdicts**

| Hypothesis | Verdict |
|---|---|
| H-MORPH | supported |
| H-P6 | partly supported |
| H-KIN | rejected as the cause of the departure |
| H-FIELD | not supported |
| H-SELECTION-ARTIFACT | rejected |

**Answers to the N17 questions**
- No runaway uses 49→59 or 49→5C.
- The 49→5C variant has m_BASE 1.20 under RAND, against 0.85 for the founder.
- When kin of the two types meet, the outcome is a placement lottery (2.0 / 2.0).

**Confidence**
- Moderate-high that a morph is necessary for a runaway.
- Moderate that the morph's realized m is above 1.
- Low-moderate that the mixture explains the exact shape of the valley.

**Next**
1. Two-type branching fit (Nestor N18 has started this).
2. Implant the 44→ac and 37→81 morphs as founders.
3. A kin re-conversion ablation.
