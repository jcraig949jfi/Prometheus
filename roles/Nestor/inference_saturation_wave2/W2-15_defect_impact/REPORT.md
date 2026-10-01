# W2-15: defect × verdict impact matrix

> Saved by Nestor from the worker's returned text, condensed with every verdict change and number kept. The harness blocks report-file writes by subagents.
> - **Full grid:** `matrix.md` and `matrix.json` (95 verdict rows × 17 defect columns, with a justification for every non-NA cell), built by `build_matrix.py`.
> - **The only computation:** `d12_sensitivity.py` → `d12_sensitivity.json`.
> - **How it was run:** read-only, `python -B`, about 1 CPU-minute, no worlds, no git writes.

**Key:**
- **NA:** the defect's mechanism is absent.
- **0:** the mechanism is present, with no effect.
- **W:** wording must change.
- **B+ / B− / B?:** a bias toward the claim, toward the null, or unknown.
- **INV:** the verdict, or the named reading, cannot stand.

## Summary

### 1. One verdict flips: C9-H3, from NOT_DEMONSTRATED to INVALID / UNTESTABLE AS DESIGNED
Three defects each invalidate it on their own:
- **D2:** arms A and B are the same simulation in 64/64 bundles.
- **D1:** every A-vs-B difference comes from cached scoring. n_cross differs in 15/64 bundles and crossed_ever in 5/64.
- **D3:** EXEC_TIME_COST and NOVELTY do nothing on the pair tape.

Knock-on effects:
- **X-H3-FLOW:** CLEAN_NULL → UNINFORMATIVE. "Transport works, about 21%" stands.
- **X-H3-EASIER:** RETIRE stands, but because no task-coupled selection channel exists, not "at this scale".

### 2. No CONFIRMED verdict flips. 22 relabels.
See §2.

### 3. D1 and D9 reach no W1, P2 or ARC3 verdict
- Those verdicts are read from P-11 assays, depth or byte tags, never from comp/held.
- In the QD pair cells, comp does nothing to the dynamics:
  - QD is aliased to no pressure (D3);
  - `qd_map` is read only by `_reap`, which pair-tape cells never reach;
  - the number of COEVO env RNG draws does not depend on comp.

### 4. D12 (noisy donor screen), recomputed
- **C-DENSE-COPY is unaffected.** With a strict L2 (rate ≥ 0.6): 36/64 vs 1/64, p = 3.5e-13.
- **C-STATELESS-FFA6 is biased toward its claim (B+), but does not flip.** "Flicker" donors pass the screen at only one checkpoint: 9 in the DENSE arm, 4 in the STATELESS arm.

  | L2 required at | p | against the frozen 0.001 |
  |---|---|---|
  | ≥ 2 checkpoints | 7.6e-4 | pass |
  | ≥ 3 checkpoints | 0.005 | fail |
  | unconditional endpoint (34/48 vs 11/48) | 2.3e-6 | pass |

  Cite the unconditional endpoint.
- **C-STATELESS:** p = 0.040 at ≥ 2 checkpoints. It stays NOT_CONFIRMED.

### 5. D4 (slotted operator) changes no verdict but forces 11 wording changes
Every 7ae3-vs-ffa6 contrast is confounded by the mutation operator:
- C-DENSE-COPY's per-cell split;
- C-STATELESS's "the effect sat entirely in ffa6";
- X-P2-BRIDGE's "mutation topology";
- C-A3's "ffa6 7, 7ae3 1": p = 0.031 as coded, but 3 vs 1 (p = 0.31) at the final checkpoint.

FINDINGS' ARC3 line "both use the OPERAND operator" is misleading in effect.

## 1. Selected matrix cells

The full grid is in `matrix.md`. Only the INV and B+ cells are listed here.

- **C9-H3:** D2, D1 and D3 each INV; D9 B?.
- **X-H3-FLOW:** D3 INV for the localization reading; D1 B−.
- **X-H1-GRADIENT:** H1-cache INV for the reading "guessers carry competence". ABR populations score about 0.9, against an expected 0.5 for blind guessing. **Not re-scored on fresh seeds** (moderate confidence).
- **C9-H1R:** H1C B+, and W29 W because the 2×2 is degenerate (M = −I/2 always).
- **C-A3-INTERNALIZE:**
  - D10 B+: 8 events as coded, 4 at the final checkpoint, 3 on a majority reading.
  - W29 W: no control.
  - W25 B?: replay that cannot refuse, label-as-content, zero-context screen (N13).
  - D4 W: the cell split becomes 3:1.
  - D3 W: "native QD" means no pressure.
  - VR W; AC W.
- **C-ZERO-SPECIFIC:** W29 B+. The donor-level p = 0.003 fails the frozen 0.001, and 14/16 donors cannot copy from 0x5A (N11).
- **C-STATELESS-FFA6:** D12 B+; D4 W.
- **X-P2-REGSTATE:** W29 B+, because the panel was screened from zero state.
- **X-A3-SFLINEAGE:** D10 B+, the same "last checkpoint with" endpoint.
- **Z80A-72H / A-1:** D8 B+. Variable-length genomes allow padding, which can only inflate depth ≥ 2.
- **E-3 (max P-11 depth 2):** D8 B+, unverified.
- **X-TASK-GATE:** D1 INV; XTG INV (D6, D15, D14, D13, D7); W25 INV (Stage 0 CD = 0).

**33 rows are NA throughout:**
- the c9x non-pair runs;
- most X-* exploratory rows (X-RUNAWAY, X-STATE, X-CORE, X-CONTENT, …);
- the forensic and endostate rows.

## 2. Verdicts that flip or must be relabelled

| verdict | from | to |
|---|---|---|
| **C9-H3** | NOT_DEMONSTRATED | **INVALID / UNTESTABLE AS DESIGNED** (FLIP; withdraw the E-9 negative) |
| **X-H3-FLOW** | CLEAN_NULL | **UNINFORMATIVE** (the transport readout stands) |
| X-H3-EASIER | RETIRE | RETIRE, because no task-coupled selection exists on the pair tape |
| C9-H1R | COST_INTERACTION_ONLY | DEGENERATE DESIGN / ARTIFACT-RISK (robust fact: gated+VM recorded competence 0/60) |
| X-H1-GRADIENT | WEAK_SIGNAL ("guessers carry competence") | WEAK_SIGNAL for composition only (guessers carry cached scores) |
| C-A3-INTERNALIZE | CONFIRMED (8) | **CONFIRMED-FRAGILE**: 4 persistent = the bar; 3 on a majority reading; per-cell 3:1 |
| X-MAT-INTERNALIZE | ENDOGENOUS 8/8 | ENDOGENOUS (mutation counted as neutral), 4 persistent + 4 transient; ARTIFACT-RISK; no positive control |
| X-A3-WITHDRAW | CLEAN_NULL (speed) | CEILING NULL: informative against collapse (ABRUPT 12/12), blind to speed |
| C-ZERO-SPECIFIC | CONFIRMED | CONFIRMED at the run level. The donor-level test fails the frozen 0.001; read as "establishment in the world the donors were screened for". |
| C-STATELESS-FFA6 | CONFIRMED | CONFIRMED; cite the unconditional endpoint |
| C-RUNAWAY, C-CORE, C-ABLATE SEARCH | CONFIRMED | CONFIRMED-FRAGILE |
| C-DENSE | CONFIRMED | CONFIRMED as "certified replication occurs", not as heredity |
| ENERGY_FOR_DEPTH, C-ATOMIC C2 | NOT_CONFIRMED | INELIGIBLE |
| C-NORECOMB | NOT_CONFIRMED | UNDERPOWERED |
| C-SWAP-ACQUIRE | NOT_CONFIRMED | NEAR-MISS / UNDERPOWERED |
| X-DOSE-CURVE | CLEAN_NULL (independent tickets) | CLEAN_NULL on its own doses; independence UNRESOLVED (C-CRITICAL-MASS's doses reject it, p = 0.014; W2-12) |
| A-2 | HOLDS | HOLDS as deltas of a cached, single-draw metric |
| E-3 | max depth 2 | not yet checked against D8 |
| X-TASK-GATE | frozen | DO NOT DISPATCH AS FROZEN (already filed) |

## 3. FINDINGS.md lines that must change

Line numbers refer to the current FINDINGS.md. There are 23 ranges in all.

| lines | change |
|---|---|
| 15 | "0 voided": voided can never be True (D5). |
| 60-64 | A-2 scope: D3 aliasing; `d_held_max` is a maximum over cached single draws. |
| 198-201 | E-3: not yet checked against D8. |
| 236-245 | E-7: the mechanism is not separated from energy-ordered reaping. |
| 253-262 | C-DENSE: replication, not heredity. C-ABLATE SEARCH: FRAGILE. ENERGY_FOR_DEPTH: INELIGIBLE. |
| 269-279 | H1R: the design is degenerate; "recorded (cached) competence"; "guessers carry cached scores". |
| 280-282 | H2: one null of 16, not two (D24, never edited). |
| **283-284** | **H3 → INVALID.** |
| 288-296 | C-NORECOMB: UNDERPOWERED. C-RUNAWAY: FRAGILE. |
| 303-310 | Founder independence: unresolved (p = 0.014 on C-CRITICAL-MASS's doses). |
| 311-314 | X-TICKET: "extinct" means overwritten. |
| 328-334 | C-ATOMIC C1: composite wording. C2: INELIGIBLE. |
| 336-340 | X-DONOR-SWAP: "genome × cell" means genome × (representation, ops mask, copy primitive, mutation). |
| 363-365 | C-SWAP-ACQUIRE: NEAR-MISS. |
| 376-381 | C-CORE: FRAGILE ("and little else"). |
| 436-439 | Lesson 12: independence. |
| 453-462 | E-W1-2: a SLOTTED cell with an operator confound; cite the unconditional endpoint. |
| 466-471 | E-P2-1: donor-level p = 0.003 fails; "largely by construction". |
| 472-474 | X-P2-BRIDGE: drop "mutation topology". |
| 484-489 | ARC3: "both use the OPERAND operator" is false in effect (D4). |
| **524-531** | **E-A3-1: 8 as coded / 4 persistent = the bar / 3 on a majority reading; cell split 3:1 and operator-confounded; no pressure acts.** |
| 533-553 | X-A3-WITHDRAW: ceiling null. |
| new | Add X-MAT-INTERNALIZE: 4 persistent / 4 transient; ffa6 MUT share 0.19-0.56 vs 0.045 in 7ae3. |

## 4. Defects that compound on one verdict

1. **C9-H3:** D2 × D1 × D3. Nothing is left.
2. **C-A3:**
   - D10 halves the count to the bar.
   - The transient events are 4 of ffa6's 7, so the cell split falls from 7:1 to 3:1, in a cell with a different operator (D4).
   - The screen is zero-register in a victim-register world (N13).
   - There is no null arm.
3. **X-MAT:**
   - The 4 transient endpoints are ffa6 runs with 1-11 organisms.
   - The MUT asymmetry (ffa6 0.43 vs 7ae3 0.045) is D4's signature.
   - On 7ae3 alone, X-MAT is ENDOGENOUS under either convention.
4. **C9-H1R and X-H1-GRADIENT:** the cache inflates exactly the number the label reads, and the FREE arms are identical by construction.
5. **C-STATELESS-FFA6:** D12 × D4. The unconditional endpoint removes D12 but not D4.
6. **C-ZERO-SPECIFIC:** three selection effects all point toward ZERO:
   - the donor screen was run from zero state;
   - two donors carry every CONST and RANDOM success;
   - the CARRY arm means victim registers.
7. **X-TASK-GATE:** D1 × D9 × D6 × D15.
8. **X-TICKET and X-H2-TERMINATION (D3 × D9):** every "extinct" or "DIED" fate is an overwrite, the N1/N2 hijack, not a death.

## 5. Recursive check on each INVALIDATES

| verdict | outcome of the check |
|---|---|
| C9-H3 | INV survives. A test with near-zero power is INVALID, not a negative. |
| X-H3-FLOW | INV survives, narrowed to the localization reading. |
| X-H1-GRADIENT | Survives at moderate confidence. It fails if the evolved populations re-score near their recorded values on fresh seeds. |
| X-TASK-GATE | Survives for the frozen design. |
| X-A3-WITHDRAW | Downgraded from INV to B− plus a relabel. ABRUPT 12/12 contradicts the predicted collapse; only the speed comparison is blind. |

Not upgraded:
- **C-A3:** 4 persistent events still meet the bar of 4, and the events are large (84-194 state-free genomes).
- **C-ZERO-SPECIFIC:** literally true for this panel; only the generalization "zero is special" falls.
- **C-STATELESS-FFA6:** the unconditional p = 2.3e-6.

## Ledger entry (W2-15)

- **Result:**
  - 95 × 17 matrix with 8 INV cells across 4 verdicts.
  - Flips: C9-H3 → INVALID, and X-H3-FLOW → UNINFORMATIVE.
  - 22 relabels; no CONFIRMED flips; C-A3 is CONFIRMED-FRAGILE at exactly the bar.
  - D1 and D9 reach no heredity verdict.
  - D4 forces 11 wording changes; D12 biases C-STATELESS-FFA6 without a flip.
  - 23 FINDINGS ranges must change.
- **Confidence:**
  - high: the C9-H3 flip, the D10 counts, the D12 computations, and D1's limited reach;
  - moderate: X-H1-GRADIENT and the D8 bias in the 72h record.
- **Strongest objection:**
  - a matrix this wide may over-flag;
  - NA was decided by applicability rules applied while reading, so a comp/held read that was missed would be a false NA.
- **Unresolved:**
  - H1 ungated competence on fresh seeds;
  - mutual-acceptance edges in 72h replays (D8 vs E-3);
  - founder independence;
  - a null arm for C-A3;
  - a cell contrast free of D4.
- **Next:**
  - the P3-patched operator on the ffa6 > 7ae3 gaps (needs a world run);
  - other live "last checkpoint with" endpoints (X-A3-SFLINEAGE, X-DD-ESTABLISH);
  - a defect column per verdict in FINDINGS, so new defects propagate mechanically.
