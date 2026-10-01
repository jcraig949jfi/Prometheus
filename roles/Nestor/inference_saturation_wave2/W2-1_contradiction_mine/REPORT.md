# W2-1 contradiction mine: what would make each NPE conclusion look wrong, and do we already have it?

> Saved by Nestor from the worker's returned text: the harness blocks report-file writes by subagents. Condensed lightly; all
> numbers and verdicts are kept. The 11 check scripts and their JSON outputs are in this folder.
>
> Boundaries: read-only outside this folder; no git writes; no world runs. Check E made single-interaction P-11 assays
> (~2 CPU-min). Items marked *(sub-agent read)* came from a search sub-agent and were not re-verified at the line.

**Target:** Wave-1 rev 2, in `roles/Nestor/inference_harvest_2026-09-30/`. Abbreviations: SYN (synthesis), THEO, UNM, HO.

## Summary
1. **Survives.** Of 13 conclusions, 3 survive outright:
   - C1, the base rate;
   - C2, the small core;
   - C5, first-donor prediction.

   C4 survives, but its HL = 0 geometry half is undecidable.
2. **Weakened or broken.** Seven are WEAKENED (C3, C6, C7, C8, C9, C11, C13) and C12 is UNDECIDABLE. Three parts are BROKEN:
   - C10's depth-gap premise;
   - C11's "dominate" wording and its side-0 marker;
   - C7's dismissal of the victim magnet.
3. **Largest finding: a matched no-payoff arm already exists.** X-A3-FAIR's ZERO world resets registers before every interaction.
   - State-free genomes appear and sweep there without payoff: 2/23 de novo, one of them reaching 185/187.
   - The robust share at the end is 0.70 with carried registers vs 0.11 with reset.
   - So payoff raises prevalence but is not needed.
4. **The victim-register channel was tested once, and the test was null.** X-DD-STATE-RESET was null and the reading was withdrawn. The synthesis reinstates the channel without citing it. The payoff more plausibly comes from the copier's own carried state.
5. **C11 events.**
   - Only 4/8 ever reach a state-free majority; 2/8 are single-genome blips; 2–3/8 are majority state-free at 2000.
   - In 13 runs a non-founder population is already majority state-free when first sighted, against 4 founder-lineage majorities.
6. **The side-0 switch distinguishes nothing.** The replaced genomes are side-0 copiers too (271/295 vs 432/433).
7. **C10: the depth gap premise is false.**
   - The X-ATOMIC BASE arm has runs at depths 44 and 50.
   - ATOMIC implant runs fall in the gap (8/36 X-ATOMIC, 6/47 C-ATOMIC).
   - 22/34 C-A3 runaways never had a founder takeover.
   - The turnover reading survives: depth correlates with time since the first donor (ρ = 0.74).
8. **C7: the foreign magnet is explained after all.**
   - The magnet rate (1–6/400) was dismissed as too small, but compounded over 72–431 epochs it explains 100/240.
   - The 7ae3 hijack predicts the X-TICKET epoch-1 loss (0.25 vs 0.28).
   - Side-1 copiers fail CVT-R 13/17, against 6/114 for side 0.
9. **C6: the multi-founder excess at depth ≥ 5 is real.**
   - Single-founder batches are homogeneous (p = 0.43), so the excess (k = 4: 41/80, p = 0.005) cannot be a batch effect.
   - It is the only existing data that could show a kin-context effect.
   - C8's "8x BASE miss" came from using the zero-context row; the carried-like row brackets the observed 0.03.
10. **C13 and record staleness.**
    - S3's "T4(c) DEAD" makes "T4 untested" stale.
    - The handoff (as read) still asserts claims that rev 2 retracted.
    - Three "no existing test" lines in THEO are false.

## Verdict table

| # | conclusion | status | the observation already on disk that hurts it |
|---|---|---|---|
| C1 | encoding + geometry base rate | SURVIVES (order of magnitude) | the register world moves acquisition about 1.4x |
| C2 | ~8-byte core | SURVIVES, strengthened | S3: pairwise knockouts are sub-additive (0.77x null) |
| C3 | write-back sets the regime | WEAKENED | the other 15 specimens go 1/120 vs 0/120; within ATOMIC the register world moves runaway 4x (FAIR L4: ZERO 23/48, CARRIED 6/48, 5A 3/48) |
| C4 | self-poisoning; ZERO = HL = 0 geometry | SURVIVES; geometry UNDECIDABLE | an HL ≡ 0 mod 128 constant control was never run |
| C5 | first-donor fate from single interactions | SURVIVES (qualified) | none |
| C6 | fate decided in 3–10 epochs; founders independent | WEAKENED | k = 1 batches homogeneous (p 0.43); multi-founder excess at depth ≥ 5 is real (C-CRITICAL-MASS k = 4 41/80 vs 29.3 expected, p 0.005; X-CRITICAL-MASS 32/64, p 0.020; dose k = 2 20/64, p 0.027) |
| C7 | SELF-only hijack; self-import; magnet unexplained | WEAKENED; the magnet dismissal BROKEN | 1–6/400 per pairing, compounded, explains 100/240. Side-1 copiers fail CVT-R: 4/17 pass vs 108/114 for side 0. U-W1b's own numbers have 44% partner-authored bytes for state-free side-1 copiers. In BEE, a SELF-free copier is hijacked in 13.1% of births *(sub-agent read)* |
| C8 | content sterility; "8x BASE miss" | WEAKENED | ADV2's RAND row (m 0.98, P_est 0) and ZERO row (0.26) bracket the observed 0.03 |
| C9 | label ≠ content; function kept; not imported | label SURVIVES; "function kept" WEAKENED | 4/16 takeovers end with 0 competent genomes while L = 0.66–1.0 (one of them a C-A3 event, 27000052). 5/16 takeovers happen with ≤ 10 competent genomes |
| C10 | depth bistable, gap 22–161 | premise BROKEN; turnover SURVIVES | omitted X-ATOMIC BASE runs end at 44, 50 and 641; C-NORECOMB has 126. ATOMIC runaways in the gap: 8/36 and 6/47. C-A3 21/34; FAIR-ZERO 8/23. Depth vs time since first donor: ρ 0.74 |
| C11 | state-freedom dominates after takeover (8/15), because of victim registers | "dominate" BROKEN; cause WEAKENED; side-0 marker BROKEN | the event rule needs one state-free genome; a majority is reached in 4/8; the FAIR ZERO world has sweeps without payoff; X-DD-STATE-RESET was null and withdrawn (F:459-462, G:157); replaced genomes are side-0 too; 13 non-L runs are majority state-free at first sighting |
| C12 | supply-limited (8x vs 7x) | UNDECIDABLE | with competent-genome exposure the ratio is 13x; 27000053 has P(0 events) about 0.20, not 0.055; the cell effect persists without payoff (ZERO-world ffa6 3/3 vs 7ae3 0/5) |
| C13 | T4 untested; 16000006 the strongest residue | WEAKENED | S3 found T4(c) DEAD. The 16000006 cluster's excess is 0.21–1.14 (9/10 below 1). The 6/8 regain was read with the defective ruler |

## Key details

**C11 (iii), the no-payoff arm** (`fair_payoff_check.py`/.json). FAIR's ZERO world resets both organisms before every
interaction (`reset_axis.py:44-45,63-66`), with the same runner and cells.

| world | robust share at end | de novo majority | founded robust |
|---|---|---|---|
| CARRIED | 0.70 | 3/5 | 1 |
| ZERO | 0.11 | 2/23 | 1 |
| 5A | 0.15 | 1/3 | 0 |

- In ZERO, ffa6 24000015 goes from 0 to 185/187, and 24000003 reaches 0.76.
- ENDOSTATE-R: cycle-robustness is flat (0.86 → 0.88) while state-freedom rises (0.32 → 0.65). Supply or hitchhiking both
  remain live.

**C6 founder independence** (`founder_independence_check.py`).
- 8 single-founder BASE batches (n = 630): chi2 = 6.97, df = 7, p = 0.43 (homogeneous).
- Against pooled p1 = 0.108, every multi-founder arm exceeds independence at depth ≥ 5. The excess vanishes at runaway.
- Co-founders are kin, and pairing is uniform (`world.py:769-778`). This is the only existing data relevant to T4(a).

**C7 magnet arithmetic** (`magnet_compounding.py`).
- 100/240 is the end-of-run label loss.
- At 1/400 per side-0 pairing it needs 431 intact epochs; at 6/400, 72.
- The random implant's probe is 0/400, matching its 0/240.
- Epoch-1 prediction: 0.5 × 200/400 = 0.25, against 36/128 = 0.28 observed.

**C10 depth gap** (`depth_gap_check.py`). Counterexamples are listed in the table. 22 of 34 C-A3 runaways never had a
founder takeover.

## Record defects found
- The handoff (as read) asserts claims that SYN §8 retracts.
- THEO's "no existing test" lines are false at THEO:57, 113-114 and 207-210. FAIR ZERO is an existing no-payoff test.
- The depth pool omitted the X-ATOMIC BASE arm.
- Unreconciled counts:
  - SYN's 8/15 and 8/11, vs this worker's 16 takeovers and 12 takeover + runaway;
  - SYN:109 (3/17/28) vs F:516-519 (2/1/17/37);
  - F:549's "~1700 epochs" (WITHDRAW's jump is 0.22 → 0.956 in one checkpoint).

## Ledger entry (W2-1)
- **Question.** For 13 load-bearing NPE conclusions: what observation would refute each, and do we already have it?
- **Result.**
  - SURVIVE: 3, plus C4 partly undecidable.
  - WEAKENED: 7.
  - BROKEN components: C10's premise, C11's wording and marker, C7's magnet dismissal.
  - UNDECIDABLE: C12.
  - The key correction: state-freedom sweeps without register payoff, and the only test of the victim channel was null.
- **Confidence.**
  - High: C10, C11 (i) and (iv), and the existence of the no-payoff arm.
  - Medium: C6 and the magnet.
  - Medium-low: the self-state reading of C11 (iii).
- **Strongest objection.**
  - FAIR's unit is distinct donor genomes at a 100-epoch first sighting.
  - The ZERO sweeps could be hitchhiking.
  - The magnet arithmetic assumes a constant hazard.
- **Unresolved.**
  - A victim-only removal combined with state-freedom measurement.
  - Founding vs sweep in non-L populations (E4).
  - How L takes over without copiers.
  - Whether the C6 excess is kin.
  - The HL ≡ 0 control.
- **Next questions.**
  1. A two-type Galton-Watson model for 7ae3 under BASE.
  2. A replay of FAIR-ZERO 24000015, epochs 1500–1700, with genealogy.
  3. A STATE-RESET world with STATE_FREE checkpoints.
  4. A `PATTERN:` HL ≡ 0 control.
  5. A per-run founder-overwrite epoch log in 9cba and e160.
  6. k = 4 with distinct vs identical founders.
  7. P-11 and CVT-R split by side.
  8. Fix HO, THEO, SYN:62/149/204 and SYN §5.
