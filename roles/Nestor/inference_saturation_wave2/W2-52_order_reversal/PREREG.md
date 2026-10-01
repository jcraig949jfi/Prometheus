# W2-52 PREREG: call-order reversal on the W2-24 panel (test of W2-47 P2)

- **Written:** 2026-10-01T03:11:03Z (`date -u`), before any reversed-order call was computed.
- **Status:** frozen. Any later change is appended below a dated AMENDMENT line and does not replace this text.

## Question
W2-24 attributes the side-switch genomes' (AC, 5C) advantage over F to run-first protection: AC/5C convert from
side 0, which runs first, so their converting half is never pre-damaged. W2-47 P2 (frame-only) predicts that
reversing call order (side 1 runs first) erases or inverts AC's advantage over F, and that C3's ejection still acts
at the placement-0 target.

## Arms
- **STOCK:** side 0's slice runs, then side 1's slice, on one shared 2n-byte tape (= `common.pair`).
- **REVERSED:** side 1's slice runs, then side 0's slice, on the same tape. Nothing else changes: each context
  keeps its own start address, its `sense` (= its placement index), its carried state, the slice budget, the ops mask,
  the arena policy and copy errors off (cmr = 0, so the shared rng is never drawn). Implemented in the harness
  (W2-16 s4 style, explicit `order`); no campaign file is edited.

## Genomes
F (`run_ds.donor_genome()`), AC (44->AC), 5C (49->5C), C3 (43->C3), C3+AC (43->C3, 44->AC).

## Panel (paired)
The N17e / W2-24 panel exactly: `q1_trace.panel()`, rng `Random("N17e")`, W2-14 BASE bank epochs 10-299, N = 1000
(partner genome y, partner carried context cy, side s). Donor context ZERO (the primary in N17e/W2-24/W2-30/W2-41).
Every genome x arm uses the same 1000 rows, so all genome and arm differences are paired per row.

## Readouts (per call, BASE write-back)
- m_base under FID (keep = FID(x, own half) >= 0.9; conv = FID(x, partner half) >= 0.9).
- m_base under the class ruler (W2-30 t1c / W2-41 a2: FID >= 0.9 AND bytes 43, 44, 45, 49 equal x's).
- keep and conversion per side (s = 0, s = 1), both rulers. Exact ruler reported as a secondary column only.
- Mechanism readouts (W2-24): donor half intact when the donor's context starts; partner runs the donor's LDIR
  at donor position 52; partner jumps 43 -> 108 (C3 ejection); dominant keep-loss author.

## Statistic
d_i = m_i(AC) - m_i(F) per panel row (paired). Estimate = mean(d). 95% CI = percentile bootstrap over rows,
10,000 resamples, `random.Random("W2-52")`; a normal-approximation paired CI is reported alongside but the
bootstrap CI decides.

## Decision rule (applied separately under the class ruler and under FID)
Let D_stock, D_rev be the mean paired differences m(AC) - m(F) in each arm, with 95% CIs.
- **P2 CONFIRMED** if D_stock > 0 with a CI excluding 0, AND under REVERSED either D_rev <= 0 or the D_rev CI
  includes 0.
- **P2 REFUTED** if D_rev > 0 with a CI excluding 0 (the AC advantage persists under reversal).
- **UNRESOLVED** otherwise (e.g. D_stock's CI includes 0).
- **Overall verdict:** the common verdict if class and FID agree; if they disagree, UNRESOLVED (ruler-dependent),
  with both reported.

## Secondary (descriptive, no verdict attached)
- 5C - F under the same rule (side-switch twin of AC).
- C3 and C3+AC under reversal, interpreted with W2-24's mechanism (JP 22EC at 43 ejects runners only in the
  side-0 placement; C3+AC's JP 22AC lands at its own AC).
- Self-test gate (must pass before any reversed number is reported): STOCK reproduces N17e `bank_assay.json`
  (ZERO: m_base, keep, conv_side0, conv_side1) and W2-41 `a2_assay.json` (ZERO: FID and class m, keep_s0/s1,
  conv_s0/s1) exactly for every genome present there, and the order-explicit harness with order (0, 1) is
  byte-identical to `common.pair` on all 5000 stock calls. A negative control: REVERSED must differ from STOCK
  on at least one call (else the swap is a no-op).

## Budget
Static only, python -B, under 15 CPU-min. No git writes, no campaign edits.
