# W2-26: source of W2-17's 3.5% side switches, and morph timing

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Written:** 2026-10-01 02:54Z.
> - **Files:** `s1_replay.py`/`s1_out/`, `s2_switch_diffs.*`, `s3_assay.*`, `s4_birth_rates.py` + `s4_partial.log`, `s5_timing.*`, `s6_tables.*`.
> - **CAP BREACH:** about 36 CPU-min used against a cap of 30. The worker stopped its own `s4` task with TaskStop at 19 of 23 runs, so CRW_107, CRW_66, CRW_91 and CRW_85 are missing. No other process was killed and there were no git writes.
> - **Replays:** all 23 W2-17 runs were re-replayed with byte provenance. They are bit-exact against `r3_out` and reproduce a4's counts exactly: 36/1018 control switches and 366/2644 runaway switches.

## Answer

### 1. The 3.5% is mostly not a 7ae3 genotype switch
- **Foreign parents.** 26 of 36 control switch edges (72%) have a parent that is not 7ae3: fewer than 51 of its 64 bytes match the implant.
  - In 13 of these the parent is a foreign copier that already converts from side 0.
  - In 3 there is no genotype change.
  - In 7 the parent converts only with its own carried registers.
- **Surviving labels.** 6 edges keep a 7ae3 label on a slot whose content was replaced in place (61–63 bytes differ, no relabel).
- **Small-diff derivatives.** 4 edges are 7ae3 genomes that differ by 4–8 bytes.
- **Copy errors at birth.** 0 control edges.
- W2-17's S0/S1 tag is an event-side tag. It is inherited through oid labels that survive replacement of the content.

### 2. N17d's 7.5e-4 per birth is roughly right for its route, but its route is minor
Within the 7ae3 family:

| route | rate |
|---|---|
| single-bit copy error at birth | 2/790 = 2.5e-3 per birth |
| **in place, over the child's lifetime** (execution writes into an unrelabelled slot; self-copy or hijack copy errors; partner writes) | **16/790 = 2.0e-2** |

**The carried register state also turns some side-1 genomes into side-0 converters.** This contradicts N17e and W2-24's "register-robust", which was tested only with bank and ZERO contexts.

### 3. Timing
- **5 of 12** runaways have a genotype-confirmed side-0 converter before 27 founder-family causal births. **7 of 12** get it after.
- **5 of 12** runaways never contain a 7ae3 side-0 morph. Their side-0 converters are foreign.
- In **12 of 12**, some side-0 converter appears before depth 20.

### 4. Verdicts
| claim | verdict | basis |
|---|---|---|
| "A morph is necessary for crossing ~27" | **REFUTED** | 11/11 controls and 7/12 runaways crossed without one; it is not sufficient either (3 controls with an early morph died) |
| "A 7ae3 morph is necessary for persistence" | **REFUTED** | 5/12 runaways have none |
| "Some side-0 converter precedes depth 20 in every runaway" | **SUPPORTED as an association only** | 12/12 vs 4/11 (p ≈ 1.4e-3); confounded by reverse causation |

## T1: sources of switch edges

Setup: static assay with W2-3 common against the W2-14 BASE bank, N = 400 per side. "P" is the parent at the child's birth; "k@E2" is the genome at the switch interaction.

| category | CTL (36) | RUN window (366) | RUN all (569) |
|---|---|---|---|
| A: no genotype change (all P non-7ae3) | 3 | 84 | 152 |
| B: P already a side-0 converter (non-7ae3) | 13 | 199 | 320 |
| C: context-dependent conversion (7ae3 / non-7ae3) | 2 / 7 | 7 / 33 | 7 / 37 |
| D: multi-byte, no single causal byte | 4 / 1 | 13 / 4 | 13 / 4 |
| E: single-bit copy error at birth | **0** / 0 | 4 / 2 | 4 / 6 |
| F: `_mutate` | 0 | 1 | 1 |
| G: in-place execution write, no relabel | 4 / 1 | 8 / 7 | 8 / 11 |
| H: partner-constructed or donor-offset write | 1 | 4 | 6 |

- **Distinct switching nodes:** 21 in controls, 195 in the runaway window. XTK_14 node 316 alone gives 5 edges.
- **Control edges with a 7ae3 parent:** all 10 convert at side 0 with their actual carried context; only 8 of 10 do with ZERO.
- **The 9 control C-edges:** 0.91–1.0 with their own carried registers, against 0.13–0.18 with ZERO.
- **Single causal bytes in the runaways:**
  - 37 a5→81 (an in-place two-bit change, 6 edges, which is how **W2-17's morph arises**);
  - 0 00→40;
  - 39 27→26;
  - 43 c1→81;
  - 41 c1→81;
  - 44 ec→ac (copy error, 2 edges).

## T2: the control 3.5% decomposed

| component | edges | per 1018 |
|---|---|---|
| non-7ae3 parent | 26 | 2.55% |
| 7ae3 label over a wholesale in-place rewrite | 6 | 0.59% |
| small-diff 7ae3 derivative | 4 | 0.39% |
| single-bit copy error at birth | 0 | 0 (about 0.3 expected) |

## T3: per-birth genotype-switch rates within the 7ae3 family (19 of 23 runs)

| route | events | rate (per 790) |
|---|---|---|
| birth: single-bit copy error | 2 | 2.5e-3 |
| in place: one-bit execution write | 5 | 6.3e-3 |
| in place: multi-byte execution write | 6 | 7.6e-3 |
| in place: multi-byte, no single causal byte | 5 | 6.3e-3 |
| **total** | **18** | **2.3e-2** |

In-world conversion per interaction, 7ae3 family at side 0, controls: 13/660 = 0.020, against 0.002 static. The exact founder converted 0/11.

## T4: timing

Columns: e27 = epoch of the 27th family birth; M7 = first 7ae3-family static side-0 converter birth; MA = any genotype; ep/nB = epoch / family births before it; d20 = first epoch with depth 20.

| run | e27 | M7 (ep / nB) | MA (ep / nB) | d20 | vs 27 |
|---|---|---|---|---|---|
| XTK_59 | 12 | 7/17 | 7/17 | 46 | before |
| XTK_35 | 12 | 9/10 | 9/10 | 35 | before |
| CRW_48 | 9 | 9/25 | 9/25 | 38 | before |
| CRW_126 | 14 | 3/2 | 3/2 | 37 | before |
| CRW_145 | 21 | 18/19 | 18/19 | 59 | before |
| XTK_121 | 9 | 14/78 | 14/78 | 43 | after |
| XH2N_s1 | 13 | 27/55 | 21/45 | 80 | after |
| CNR_s22 | 13 | none | 16/32 (foreign) | 54 | after |
| CRW_1 | 15 | none | 36/186 (foreign) | 67 | after |
| CRW_103 | 15 | none | 30/125 (foreign) | 43 | after |
| CRW_75 | never | none | 47 (foreign) | 77 | after |
| CRW_78 | 24 | none | 27/34 (foreign) | 79 | after |
| controls XH2N_s9, CRW_91, CRW_85 | 8/13/10 | 3/5, 10/12, 9/24 | same | never | early morph, then died |
| control XTK_14 (s14) | 15 | none | 46/88 (foreign) | 69 | after |
| other 7 controls | 10–22 | none | none | never | — |

This agrees with the red-team: s121 has its first S0 edge at e10 and its morph at e14 after 78 births; s14's first converter comes at e46 after 88 births.

## Adversarial points
1. **The family threshold (≥ 51/64 at shift 0) is arbitrary.** If the 32–50-byte matches are drifted 7ae3 genomes, the 7ae3 share rises. The control finding "no birth copy-error route" still holds.
2. **The static converter cutoff is a proxy.** The C-class in-world contexts give 0.91–1.0, so context is a real mechanism. The contexts come from the same interaction's input, though, so they are not independent.
3. **The in-place route is per child lifetime**, not per birth.
4. **s4 is incomplete and its counts are tiny.** Rates are good to within about 2–3x.
5. **The replays stop at depth 24/27 or epoch 130.**
6. **The 12/12 vs 4/11 association is outcome-conditioned**: runaways have 5–30x more births.
7. **In-place self-copy errors cannot be separated from partner writes.**

## Ledger entry (W2-26)
- **Inference.**
  - W2-17's S0/S1 "types" are mostly genotype heterogeneity **outside 7ae3**: foreign side-0 copiers, plus oid labels that survive in-place replacement.
  - Within 7ae3, side-0 converters arise mainly **in place** and through the **carried register state**. Copy errors at birth contribute 2.5e-3 per birth.
  - Morph necessary for crossing 27: refuted. 7ae3 morph necessary for persistence: refuted. Side-0 converter before depth 20: an association only.
- **Confidence.** High for the decomposition and timing; moderate for the internal rates; low for any causal reading.
- **Strongest objection.** The family threshold and the static-converter proxy drive the split.
- **Next.**
  1. Implant 37→81, 44→AC, and a foreign side-0 copier from CRW_1 or CRW_78 (needs authorization).
  2. Rerun N17e with self-carried contexts.
  3. Retype W2-17 by parent genotype.
  4. A replay hook on the copy-error branch at z8.py:415–417.
