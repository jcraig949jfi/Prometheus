# W2-23: Harvard confinement as a causal test of the wrap / partner-execution field

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Timeline (all `date -u`):** PREREG frozen 2026-10-01T01:43:03Z. Amendment A1 (P3 stock control) at 01:47:40Z, after P1 was scored and before P2/P3 ran. Scoring at 01:57:57Z.
> - **Compute:** about 17 CPU-min.
> - **Files:** `PREREG.md`, `RESULTS.json`, `SELFTEST.json`, `_harv.py`, `st_selftest.py`, `p1_cvtr`, `p1b_residual`, `p2_k3`, `p2b_residual`, `p3_n2` (.py/.json/.log).

## Answer
**1 of 3 pre-registered predictions PASS.**

The wrap / partner-execution route is real and causal:
- it removes the N2 hijack completely;
- it cuts the K3 relabel share 3–24x;
- it more than triples side-1 CVT-R acceptance.

It is not the *whole* cause of the side-1 CVT-R failure or of the K3 magnet:
- **P1 residual:** the side-0 partner still damages the copier through the data path, with its own LDIR and byte stores. HARV cannot touch this.
- **P2 residual:** about half is copy-back by partners the implant had converted. That is heredity, not hijack.

Confinement vs terminator:
- HARV_WRAP has confinement without a terminator, and it removes P3 equally (0/750) and P2 nearly equally. **Confinement is the active ingredient for hijack.**
- The terminator matters only for P1: HALT 10/17 vs WRAP 7/17.

## Prediction table

| # | criterion | STOCK | HARV_HALT | HARV_WRAP | verdict |
|---|---|---|---|---|---|
| P1 | side-1 CVT-R ≥ 14/17 | 3/17 (17/17 identical to Artemis record) | **10/17** (vs stock p = 0.032; vs no-partner 17/17 p = 0.007) | 7/17 | **FAIL** |
| P2 | K3 relabel ≤ 0.10 in both cells | 9cba 24/40, e160 17/40 (exact repro) | 9cba **1/40** (p = 1.4e-8); e160 **5/40 = 0.125** (Wilson 0.055–0.26; p = 0.005) | 3/40, 5/40 | **FAIL** (e160 misses by 1 chain) |
| P3 | 0.5 × side-0 hijack ≤ 0.05 | zero 336/750 → 0.224; random 261/750 → 0.174 (inside N1's CI) | **0/750** in both contexts | 0/750 | **PASS** |

Note: the brief's "4/17" counts either side. Side 1 alone is 3/17.

## Mechanism

**P1 (60 victims × 17 copiers, world order):**

| arm | good | clean (all good) | partner-block pre-damage | byte-only pre-damage |
|---|---|---|---|---|
| STOCK | 628/1020 | 492 | 432 | 96 |
| HALT | 895/1020 | 759 | 114 | 147 |
| WRAP | 811/1020 | | | |

- Block pre-damage falls 74%. The residual 114 are the partner's own LDIR.
- No-partner CVT-R is 17/17 in all three arms.
- The compounding model predicts 12.7/17; 10 observed.

**P2 residual (6 HALT relabels):**
- 3 are copy-backs from a slot the implant had converted. This is heredity.
- 3 come from never-converted partners, often onto an eroded implant (fidelity 0.34–0.98).
- Post hoc, excluding the copy-backs gives 3/80. Not used for the verdict.

**P3:** HARV fired in 1301/1500 interactions. Partner-authored founder bytes fell from 21,145 to 0.

**Side-0 copiers (not scored):**
- CVT-R: 12/18 stock → 13/18 HALT → 12/18 WRAP.
- q1_competent:13 drops from 35/60 to 0/60, because its pc leaves its half before the LDIR.

## Self-tests (all pass)

| test | result |
|---|---|
| ST1: HARV build vs stock z8 | identical where HARV never fired (92/92, 104/104); changes 1403/1408 and 1396/1396 where it fires; STOCK rebuild 300/300 |
| ST2: vs W2-7 `alien_vm` | 1000/1000 per arm |
| ST3: `p11.assay(vm=HARV)` vs `alien_pair.assay` | 12/12 per arm. The P-11 re-execution runs under HARV; K3 routes through `r._vm` (asserted) |
| ST4: 17 side-1 copiers P-11 competent | all 17 under both HARV arms (stock 10/17) |

- P1 and P2 reproduce stock exactly.
- P3 is statistical only: N1 seeded with `hash()`, which changes per process (recorded in A1).

## Adversarial round
1. **HARV is blunt.** True for side-0 q1:13. The no-partner 17/17 shows the 17 copiers were not damaged.
2. **P2 missing by one chain could be noise.** FAIL is kept as pre-registered. Effect size and direction are clear.
3. **"The terminator does the work."** Refuted for P2 and P3; partly true for P1.
4. **Operand fetch across the edge is unconfined.** A small leak, biased against P3's PASS.
5. **All static.** Correct; in-world behaviour is untested.
6. **Single-seed CVT-R.** Even the compounding model gives 12.7 < 14.

## Ledger entry (W2-23)
- **Inference.**
  - Partner execution of the donor's or copier's code is causal and confinement-specific:
    - N2 hijack: 0.224 → 0;
    - K3: 0.60/0.43 → 0.025/0.125;
    - side-1 per-interaction good: 0.62 → 0.88.
  - It is the whole of N2, and most but not all of K3 and W2-16.
  - The residuals are data-path writes by the partner's own code, plus copy-back by descendants.
- **Confidence.** High for P3 and for the direction. Moderate for residual attribution (n = 6 for K3).
- **Next.**
  1. A combined BLOCK_OWN × HARV arm: does P1 reach 17/17?
  2. HARV_HALT in-world on X-TICKET (needs authorization).
  3. Rescore Wave-1 claims that read side-1 P-11 rates as competence.
