# PREREG DRAFT: X-HARV-INWORLD (Harvard confinement, in-world, X-TICKET cell)

**Status:** DRAFT, written 2026-10-01T02:40Z (`date -u`). It is NOT frozen, NOT dispatched and NOT authorized. It needs operator or Aporia authorization, a Fabric lease and a freeze commit.
**Rank:** 2 of 3.
**Source of the prediction:** W2-23 (P3: static side-0 hijack 0.224 → 0/750 under HARV_HALT and HARV_WRAP), N2 (the X-TICKET epoch-1 loss of 36/128 = 0.28 vs a hijack prediction of 0.21), and W2-7.
**What it upgrades.** W2-25's top handoff candidate is "partner execution of a donor's own code after the pc wrap is the dominant loss mechanism". It is currently "one harness, static, not shown in-world" (W2-25 F12). This is the in-world test.

## 1. Hypotheses
- **H-HIJACK (W2-23/N2).**
  - Most of the epoch-1 founder loss in X-TICKET is the side-1 partner wrapping 127 → 0 and running the founder's own SELF + LDIR.
  - Under Harvard confinement the epoch-1 loss falls to the **non-hijack remainder**: p_H = p_S − ½·h_S.
  - Here p_S is the in-batch stock epoch-1 loss and h_S is the in-batch stock side-0 hijack-loss rate, both measured on the same seeds by counterfactual attribution (§4, R1c).
  - Numerically, from history: 0.28 − ½ × (0.35–0.45) ≈ **0.06–0.11**.
- **H-HIJACK-SIDE.** Side-0 epoch-1 founder loss collapses: from ≥ 0.30 under STOCK to ≤ 0.08 under HARV_HALT.
- **H-CONFINE (W2-23).** Confinement, not the terminator, is active: HARV_WRAP ≈ HARV_HALT on side-0 loss.
- **Null (H-OTHER).** The in-world epoch-1 loss is mainly a route that HARV does not touch (data-path writes, reaping, the pairing structure). Then p_H ≥ p_S − 0.10.

## 2. Arms
X-TICKET physics: 7ae3 arm-B cell, splice off, tier M, BASE, single implanted founder. The arms differ **only** in the VM module used for pair execution **and** for P-11 re-execution.

| arm | VM build | role |
|---|---|---|
| STOCK | the `plain("STOCK")` module from `W2-23/_harv.py`, i.e. the unpatched z8 source executed as a module | stock control |
| HARV_HALT | `plain("HARV_HALT")`: a pc leaving the context's own half halts the context | test |
| HARV_WRAP | `plain("HARV_WRAP")`: the pc wraps inside its own half; confinement without a terminator | mechanism control |

**Injection.** Use a Runner subclass whose `_pair_interact` and P-11 assay both resolve `z8` to the arm's module.
- This is done by binding module globals at construction, not by editing frozen files.
- `track_material` is False in this cell (WELL_MIXED), so the `z8taint` path is never used. This is asserted.

## 3. Seeds
- **Base: `42_200_000 + s`.**
  - Stage A: s ∈ [128, 384), horizon 20 epochs.
  - Stage B: s ∈ [0, 128), horizon 300 epochs.
  - Each seed runs in all three arms (paired).
- **Pairing guarantee.** The epoch-0 population hash and the founder's epoch-1 partner and side must be identical across arms on every seed. Initial seeding and the epoch-1 shuffle happen before any execution. This is asserted per seed.
- **Used ranges checked:** the same inventory as PREREG_DRAFT_IMPLANTED_MORPHS §3. `42_2xx_xxx` is unused as a seed base. Re-check at freeze.
- **Defect found in that inventory.**
  - W2-22's "fresh" seeds (9_998_000 + 1000..2199 = 9_999_000..10_000_199) **overlap** X-DECAY (9_999_000–063), X-STERILE (9_999_500–563) and X-ATOMIC (9_999_800–863).
  - W2-22's verdict is internal (FIELD vs FREE), so it is not biased. But its PREREG's "fresh" holds only against W2-14. Record as a minor defect.

## 4. Readouts (matched; same code in all arms)
- **R1 (primary).** Epoch-1 founder loss: the founder's causal set has no live member at the end of epoch index 0. This is X-TICKET's `traj[0][0] == 0`, the readout behind 36/128.
- **R1a.** The founder's epoch-1 side (0, 1, or unpaired), logged.
- **R1b.** R1 split by side.
- **R1c (counterfactual attribution, exact).**
  - For each seed, capture the founder's epoch-1 pair pre-state: both genomes, registers and flags, and the `st0` that the world already builds.
  - Re-execute that one pair statically through `p11.interact` under STOCK, HARV_HALT and HARV_WRAP.
  - Classify each stock loss as:
    - **hijack**: lost under STOCK, kept under both HARV builds;
    - **data-path**: lost under all three;
    - **other**.
  - h_S = the stock side-0 hijack-loss share, from R1c.
  - This readout uses no wrapped execution trace; it is a pure counterfactual on the exact state.
- **R2 (stage B, secondary).** B ≥ 27, B ≥ 163 and P(163|27) at 300, plus final genomes stored per run, as in the X-IMPLANT-MORPH R6.
- **R3 (instrument).**
  - The HARV hit counter (`_HITS`) per run: it must be > 0 in the HARV arms and exactly 0 in STOCK.
  - The module identity used by P-11, asserted at every certification.
- **Not used:** any max-of-draws score, and occupancy.

## 5. Ruler-under-same-physics requirement (gate)
Every ruler that touches a HARV-arm outcome must run under that arm's physics:
1. **P-11 causal certification** re-executes under the same HARV module (asserted per call; the count is reported). A stock-physics certification of a HARV birth would be a mismatched ruler.
2. **The overwrite / fidelity / provenance accounting** in `_pair_interact` is unchanged code. Its inputs (`prov`) come from the arm's VM.
3. **Self-test ST1** (as W2-23 ST1, but in-world):
   - On 8 seeds, a HARV-arm world run in which HARV never fires is bit-identical to STOCK.
   - The STOCK module world run is bit-identical to unpatched `world.Runner` on 8 seeds.
   - It also reproduces X-TICKET seeds 0, 2, 35 and 59 for 300 epochs. 35 and 59 are positive B ≥ 163 runs, so this also demonstrates that B ≥ 163 can be reached in this harness.
4. **Self-test ST2.** Stage-A runs truncated at 20 epochs equal the first 20 epochs of stage-B runs on 4 seeds.

## 6. Planted controls with demonstrated reachability (each in all three physics)
All controls use 20 fixtures each through `Runner._pair_interact`, the real code path with bank partners from W2-14 `banks.pkl`.

| control | pair | STOCK | HARV_HALT / HARV_WRAP | what it proves |
|---|---|---|---|---|
| **PC-H (P-11 positive)** | 7ae3 founder at side 1 vs a bank partner at side 0 | certified causal birth ≥ 15/20 | ≥ 15/20 (W2-23 ST4: side-1 copiers stay P-11 competent under HARV) | the birth ruler can fire under HARV |
| **PC-L (loss positive, non-hijack route)** | founder at side 0 vs the **43→C3 variant** at side 1. C3 at side 1 is a converter (conv 0.87) whose own LDIR, run from its own half, writes over absolute 0 | founder loss ≥ 15/20 | ≥ 15/20 (data path, untouched by HARV) | the loss ruler can fire under HARV |
| **NC-H (hijack negative)** | founder at side 0 vs the **LDIR-knockout founder** at side 1 (positions 52–53 → 00). It has no copier of its own and can damage the founder only by wrapping into the founder's code | founder loss ≥ 5/20 (manipulation reachable) | 0/20 | HARV removes exactly the hijack route |
| **NC-P11 (certification negative)** | LDIR-KO founder as donor in either side | 0 certified births | 0 certified births | no crediting without authorship |

- **Eligibility pre-check (lesson: multi-seed CVT-R).**
  - Founder CVT-R under each physics, with ≥ 5 independent seeds of W2-23's `p1_cvtr` harness (60 victims per seed).
  - If the founder is not side-1 competent under HARV in at least 4 of 5 seeds, stage B is INELIGIBLE. Stage A, which needs no births, is unaffected.

## 7. Decision rules (frozen)
Let p_S, p_H and p_W be the epoch-1 loss under STOCK, HARV_HALT and HARV_WRAP. Let s0_X be side-0 loss in arm X. Stages A and B are pooled for R1: n = 384 seeds per arm.

0. **Validity (stock control).**
   - p_S must lie in [0.18, 0.38]: X-TICKET's 0.28, CI widened by the n = 384 binomial.
   - s0_S must be ≥ 0.30.
   - STOCK side-0 losses must number ≥ 30 (eligibility).
   - If any of these fails: INVALID (the harness or this seed block does not reproduce the phenomenon). No verdict.
1. **P1 (primary, H-HIJACK-SIDE).**
   - PASS if the CP 95% upper bound of s0_H is ≤ 0.10.
   - FAIL if s0_H ≥ 0.20.
   - Otherwise PARTIAL.
2. **P2 (remainder).**
   - PASS if |p_H − (p_S − ½·h_S)| ≤ 0.06, where h_S comes from R1c in-batch.
   - The **null H-OTHER is supported** if p_H ≥ p_S − 0.10. Then partner execution is *not* the main in-world epoch-1 route, which kills N2's in-world reading.
   - If p_H < p_S − ½·h_S − 0.06, HARV removes more than the hijack: an unmodelled terminator or confinement side effect. Compare with WRAP.
3. **P3 (confinement vs terminator).**
   - PASS if |s0_W − s0_H| ≤ 0.08 and s0_W's upper bound is ≤ 0.12.
   - If WRAP fails while HALT passes, the terminator does the work in-world, contradicting W2-23.

**Stage B is secondary and not decisive.** HARV changes the whole background's physics. Only the direction is pre-registered: HARV_HALT P(B ≥ 27) ≥ STOCK's, because of fewer early losses and the gain in side-1 copiers.

**Power** (calc_bands.json `exp3_epoch1`, one-sided α 0.01, unpaired; pairing only helps):

| n per arm | HARV loss 0.07 vs stock 0.28 | HARV loss 0.12 vs stock 0.28 | HARV loss 0.17 vs stock 0.28 |
|---|---|---|---|
| 128 | 0.99 | 0.83 | 0.42 |
| 384 | 1.00 | 1.00 | 0.91 |

- For P1, with about 190 side-0 founders per arm and an expected s0_H ≤ 0.05, the upper bound falls below 0.10 with high probability.

## 8. Eligibility count (pre-run)
- Seeds per arm: 384.
- Side-0 founders: about 190, minus unpaired.
- Expected STOCK side-0 losses: 190 × (0.32–0.45) ≈ **61–86**. The gate is ≥ 30.
- Expected HARV_HALT side-0 losses: ≤ 10.
- R1c attribution needs ≥ 30 stock losses, the same gate.

## 9. CPU estimate
| stage | runs × cost | core-h |
|---|---|---|
| A | 3 arms × 256 seeds × 20 epochs × ~3 s | 0.65 |
| B | 3 × 128 × ~32 s × 1.2 (HARV check overhead) | 4.1 |
| R1c counterfactuals | 1,152 pairs × 3 builds, static, under 1 CPU-min | ~0 |
| Controls + CVT-R (5 seeds × 3 builds) + ST1/ST2 | | 0.4 |
| **Total** | | **≈ 5.2** |

- Plan 6.5 with margin; hard cap 10.
- **Cheaper decisive core:** stage A alone (plus controls) decides P1–P3 for about **1.1 core-h**.

## 10. Envelope check (MWO-0004 R2)
- Under 16 core-h per item.
- Seat 24 h: see DESIGNS.md.
- Fabric lease required.
- New preregistration, so authorization is required.
- No packages.

## 11. Failure modes
1. **The prior is already near-certain for P1** (static 0/750). The information is the in-world *remainder* (P2) and the validity of the N2 bridge, not P1. That is why this experiment ranks below X-IMPLANT-MORPH despite costing less.
2. **Operand fetch across the half edge is not confined** (W2-23 adversarial 5). This is a small leak, biased against P1 PASS.
3. **HARV makes side-0 copiers incompetent** (q1:13 35/60 → 0/60) and changes background dynamics. That affects stage B only. Stage A's epoch-1 partner set is identical across arms (asserted).
4. **The epoch-1 founder may be unpaired** (an odd count). Unpaired founders are counted and excluded from side-resolved rates.
5. **Seeding by `hash()`** (W2-23 P3's seeding changed per process) is FORBIDDEN. All draws use integer seeds or `random.Random(repr(tuple))`.
6. **Module leakage.** If `world` and `p11` resolve different `z8` objects in any HARV run, abort. R3 assertions catch this.
7. **BASE vs ATOMIC criterion** (N2 caveat). R1 is the world's own BASE loss readout, not the ATOMIC predecessor criterion. The counterfactual R1c uses the world's BASE criterion too.
