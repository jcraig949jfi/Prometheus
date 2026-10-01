# DRAFT: appendix for roles/Nestor/FINDINGS.md (Nestor appends at closing; not yet appended)

> Drafted by worker W2-48. Started 2026-10-01T03:05:10Z, file written 2026-10-01T03:09:55Z (both from `date -u`).
> Read-only except this file. No git writes, no world runs. About 1 CPU-min of Fisher re-computations and JSON reads.
> Line numbers refer to `roles/Nestor/FINDINGS.md` as it stands (644 lines).
> Path key: `W2/` = `roles/Nestor/inference_saturation_wave2/`; `C9X/` = `roles/Nestor/campaigns/c9x-explore-2026-09-24/`.

---

## Wave-2 audit (2026-10-01): proposed corrections — frozen verdicts NOT rewritten

Sources merged:
- W2-15 (defect × verdict matrix);
- W2-18 (17 correction proposals);
- W2-19, W2-27, W2-33, W2-34, W2-35, W2-38 (re-derivations and replays);
- W2-12, W2-22, W2-29, W2-26, W2-7;
- `W2/INFERENCE_LEDGER.md` up to its 03:04Z entry.

Where two sources disagree, the later verified result is used, and every such case is listed in §3.

### 1. Summary

**Verdict flips (2).**
- **C9-H3:** NOT_DEMONSTRATED → **INVALID / UNTESTABLE AS DESIGNED**.
- **X-H3-FLOW:** CLEAN_NULL → **UNINFORMATIVE**. This verdict is in the experiment graph only, not in FINDINGS.

**Clause-level INVALID inside a verdict that otherwise survives (2).**
- C9-H1R: "harmless when the cue is free … the price, not the ordering".
- X-H1-GRADIENT: "guessers carry ungated competence".

**Relabels (11).**

| class | verdicts |
|---|---|
| FRAGILE (5) | C-A3-INTERNALIZE; C-RUNAWAY; C-CORE ("and little else"); C-ABLATE SEARCH; X-H1-TRANSPLANT |
| DEGENERATE (1) | C9-H1R |
| INELIGIBLE (2) | ENERGY_FOR_DEPTH; C-ATOMIC C2 |
| UNDERPOWERED (2) | C-NORECOMB (uninformative); C-SWAP-ACQUIRE (near-miss) |
| CEILING NULL (1) | X-A3-WITHDRAW |

**Addition (1).** X-MAT-INTERNALIZE is not yet in FINDINGS. Proposed entry: ENDOGENOUS / ARTIFACT-RISK.

**Wording-only (23 rows).** The verdict class is unchanged. Scope, mechanism or readout wording changes.

**Stands after audit (5 rows).** These were flagged by an earlier Wave-2 source and cleared by a later one:
- A-1 / E-3 depth (D8);
- X-DOSE-CURVE and lesson 12;
- X-A3-SFLINEAGE;
- C-DENSE-COPY;
- the ATOMIC label-share verdicts (rotation leak).

The C-ATOMIC C1 verdict also stands, but its mechanism sentence is a wording row.

**No CONFIRMED verdict flips.**

### 2. Table

Classes used in the "proposed class" column:
- **FLIP:** the verdict changes class.
- **CLAUSE-INV:** one sentence is withdrawn; the verdict otherwise survives.
- **RELABEL:** the class shown replaces the recorded one.
- **WORDING:** the verdict class is unchanged.
- **STANDS:** an earlier flag is cleared.
- **ADD:** a new entry.

| verdict id | FINDINGS line(s) | recorded verdict | proposed class | one-line reason | evidence path(s) |
|---|---|---|---|---|---|
| A header "0 voided" | 15 | 0 voided | WORDING | The void guards cannot fire (D5), so "0 voided" carries no information | W2/W2-15_defect_impact/REPORT.md §3; W2/W2-18_findings_corrections/CORRECTION_PROPOSALS.md P08, 1b |
| A-1 / E-3 depth vs D8 | 27-31, 198-201 | NARROWED; max P-11 depth 2 | STANDS | Both depth-2 chains are distinct consecutive-epoch interactions. D8 fires once in 1,031 runs, on predecessor depth only | W2/W2-19_rescore/REPORT.md (B); d8_vs_e3.json |
| A-2 pressure row | 55, 60-64 | HOLDS (EXTERNAL-scoped) | WORDING | A delta of `d_held_max`, a maximum over cached single draws. The sign holds in both subsets (513 pairs +0.3036; COEVO +0.205, others +0.331) | W2-15 §3; W2-18 1b; W2-19 instrument note (ledger 01:44Z) |
| A-2 / A-3 read-order rows | 57-58, 66-69 | HOLDS / OPEN | WORDING | 171 of 638 pairs sit in COEVO_ENV cells, where the declared read_order is unwired after the first validation (effect ≈ 0). In the 467 wired pairs: +0.129 / −0.098. ABR is still favoured, more strongly | W2-18 P01 |
| E-2 status word | 194 | HOLDS as an instrument | WORDING | NARROWED: P-11 certifies construction, not heredity (already recorded at 510-515 and 595-614; status word never updated) | W2-18 P09 |
| E-4 narrative | 204-206 | A-4 WITHDRAWN | WORDING | Crossing epochs 48 vs 636 are genome-cached cross-niche scores (D1). The withdrawal rests on 0 births and is unaffected | W2-18 P10 |
| E-7 / C-ENERGY | 236-245 | HOLDS (CONFIRM) | WORDING | The effect is robust. Newborn starvation is not separated from energy-ordered reaping | W2-15 §3; W2/W2-9_stats_review row 2 |
| C-DENSE | 254 | CONFIRMED | WORDING | Read as "certified replication occurs", not heredity (P-11 = construction) | W2-15 §2 |
| C-ABLATE SEARCH | 258-260 | CONFIRMED | RELABEL: FRAGILE | Needed exactly 10 up-cells and got 10. 10 of 40 single-cell deletions flip it. Holm-adjusted 0.035 | W2-9 rows 4b and 126; W2-15 §2 |
| ENERGY_FOR_DEPTH | 260-262 | NOT_CONFIRMED | RELABEL: INELIGIBLE | Unattainable once FULL D2 = 3 (best possible p = 0.125). A non-result, not a negative | W2-9 row 4c; W2-15 §2 |
| C9-H1R | 269-273 | COST_INTERACTION_ONLY | RELABEL: DEGENERATE / ARTIFACT-RISK, plus CLAUSE-INV | M = −I/2 by construction (−0.10 / +0.20). The FREE arms are one simulation (0.1972 = 0.1972), so "harmless when the cue is free / price, not ordering" is untested. On true scores I = 0.125–0.142, below the 0.15 threshold. Robust fact: gated + VM 0/60 | C9X/c9_h1r/VERDICT.json; W2-18 P02; W2-19 (A); W2-15 §2 |
| X-H1-TRANSPLANT | 274-276 | EXPLORE SIGNAL | RELABEL: FRAGILE | Strict I ≥ 0.15 in only 2 of 4 transforms. What transplants is "the gate removes the 0.5 echo floor" | W2-19 (A), I-bounds table |
| X-H1-GRADIENT mechanism | 276-279 | WEAK_SIGNAL ("guessers carry ungated competence") | CLAUSE-INV (composition reading stands) | Re-scored ABR genomes: recorded held 1.000, fresh 0.496, exact 0.495 (the echo floor). reader_share 0 at all 240 checkpoints | W2-19 (A); rescore_h1.json |
| C9-H2 wording | 280-282 | REPLICATION_EVENTS_WITHOUT_PROPAGATION; 7ae3 WEAK_SIGNAL | WORDING | "Random 0/16, in situ 0/16" is ONE null of 16 runs (D24; the erratum at 586-587 never reached this line). The 4/16 is the specimen-selection seed, so winner's-curse inflated | W2-15 §3; W2/W2-33_splice_on/REPORT.md |
| **C9-H3** | **283-284** | NOT_DEMONSTRATED | **FLIP: INVALID / UNTESTABLE AS DESIGNED** | Three defects each suffice. D2: arms A ≡ B in 64/64 bundles. D1: every A–B difference is cached scoring. D3: EXEC_TIME_COST and NOVELTY are inert on the pair tape. Withdraw the E-9 negative; C9-D11 and C9-D13 (220, 222) become moot | W2-15 §1, §5; W2-18 1b (re-verified at `world.py:1070-1078`) |
| X-H3-FLOW | — (graph only) | CLEAN_NULL | FLIP: UNINFORMATIVE | The localization reading is invalid (D3). "Transport works, ~21%" stands | W2-15 §1-2 |
| X-H3-EASIER | — (graph only) | RETIRE | WORDING | Retire because no task-coupled selection channel exists on the pair tape, not "at this scale" | W2-15 §2 |
| C-NORECOMB | 288 | NOT_CONFIRMED (5/48 vs 5/48) | RELABEL: UNDERPOWERED / UNINFORMATIVE | Power ≈ 0.08. The c2a8 specimen is 0/24 in both arms. The 7ae3 BASE block (5/24 at depth ≥ 5) is the outlier among five identical-physics blocks. Cite the splice effect from C-RUNAWAY's own arms instead: depth ≥ 5, BASE 4/150 vs NO_RECOMB 20/150 (one-sided Fisher 4.9e-4; two-sided 9.9e-4). Do not cite pooled cross-block figures | C9X/c_norecomb_confirm/VERDICT.json; C9X/c_runaway_confirm/VERDICT.json; W2-33; W2-9 row 7; ledger W2-33 (02:33Z) |
| X-RUNAWAY "70-97% descend" | 289-290 | SIGNAL (descriptive) | WORDING | Read it as a lower bound: in BASE, unlabelled rotated-frame copies carry founder code (up to 0.85 of the population in CRW_1) | W2/W2-35_rotation_leak/REPORT.md §4 |
| C-RUNAWAY | 291-296 | CONFIRMED (7/150 vs 0/150) | RELABEL: FRAGILE | 7/150 is exactly the minimum passing count; prior power 0.05–0.56; second attempt; Holm-adjusted 0.036. Unaffected by splice-on heterogeneity (0/222 at depth ≥ 20) | W2-9; W2-15 §2; W2-33 |
| X-TICKET | 311-314 | WEAK_SIGNAL | WORDING | "Lose / extinct" means overwritten (hijack), not death. Lineage size counts inactive labels. The epoch-1 loss (0.28) is predicted at 0.21-0.25 by partners running the founder's SELF + LDIR. "Causal lineage lost" can miss a rotated-frame lineage | W2-18 P06; W2-15 §4.8; W2-35 §4 |
| X-STALL / X-STALL-F0 erosion | 316-324 | SIGNAL | WORDING | "Erosion ~5%/byte/epoch, ~25x nominal" is not an extra mutation process: a one-sided copy op unmakes its carrier (m_BASE ≈ 1). Rotated sterile frames (11–40) inflate "members" slightly; direction unchanged | W2-18 P07; W2-35 §4 |
| C-ATOMIC C1 mechanism sentence | 328-330 | CONFIRMED (46/80 vs 1/80) | WORDING (verdict STANDS) | ATOMIC is composite. About 75% of its effect is the world's fidelity clause (N9/N10), so "erosion stops heredity" should read "the world's detector maintains copy fidelity under ATOMIC" | W2-18 P07; ledger N9/N10 |
| C-ATOMIC C2 | 330-334 | NOT_CONFIRMED | RELABEL: INELIGIBLE | 13 of 15 specimens reach depth 5 in neither arm (2/15 capable) | W2-15 §2; W2-18 1b |
| X-DONOR-SWAP | 336-340 | WEAK_SIGNAL | WORDING | 7ae3 and ffa6 also differ in effective mutation operator (D4: SLOTTED offsets 1-3 hit opcodes 87% of the time) | W2-15 §2; W2-18 P05c |
| C-SWAP-ACQUIRE | 363-365 | NOT_CONFIRMED (9/240 vs 0/240) | RELABEL: UNDERPOWERED (NEAR-MISS) | The rule needed 10. Flips at depth ≥ 10 (11 vs 0, p = 4.3e-4). Power at the observed rate 0.41 | W2-9 row 9; W2-15 §2 |
| C-CORE | 376-381 | CONFIRMED (17/27, bar 16.2) | RELABEL: FRAGILE ("and little else"), plus WORDING | One classification flip fails it. Second bytes 24 and 53 are mutable yet retained (0.86). Essential position 34 is at background tag retention (0.04). The readout is tags, not byte values. "Conserves SELF + LDIR" stays ROBUST | W2-9 row 10; W2-18 P05a; ledger N17 |
| C-CORE interpretation note | 382-385 | steward note | WORDING | Compatible with purifying selection, but does not test it: the tag ruler cannot see value conservation at essential non-ED positions | W2-18 P05b |
| X-DOSE-CURVE / lesson 12 | 303-310, 436-439 | CLEAN_NULL ("independent lottery tickets") | STANDS (optional wording) | Common p1 fits (p = 0.31); no block heterogeneity (p = 0.64); β = 1.13 [0.98, 1.29], p = 0.095. The 0.0013 excess is a plug-in artifact. C-CRITICAL-MASS alone rejects independence (p = 0.014) through its low k = 1 arm (5/80 vs 11.1 expected). Optional addition: "β up to about 1.3 is not excluded" | W2/W2-12_founder_independence/REPORT.md; models.json |
| Lesson 1 | 408-410 | lesson | WORDING | "Every test now ships with an injected-defect negative control" is false as a description: the cannot-fire class recurred 15 times after it | W2-18 P08 (W2-5) |
| C-DENSE-COPY (E-W1-1) | 443-451 | CONFIRMED (1/64 vs 39/64) | STANDS, plus the rarity scope note (§4.1) | With strict L2 (≥ 0.6): 36/64 vs 1/64, p = 3.5e-13 (D12 has no effect) | W2-15 §4; d12_sensitivity.json |
| E-W1-2 C-STATELESS-FFA6 | 453-462 | CONFIRMED (11/33 vs 34/42) | WORDING | Cite the unconditional endpoint: 34/48 vs 11/48 (one-sided 2.3e-6; two-sided 4.6e-6). The conditional p is biased toward the claim by flicker donors (D12). The ffa6 vs 7ae3 contrast is operator-confounded (D4). C-STATELESS stays NOT_CONFIRMED (p = 0.040 at ≥ 2 checkpoints) | W2-15 §1.4; d12_sensitivity.json |
| X-DD-ESTABLISH | 457 | SIGNAL (80% of stalled donors never copy) | WORDING (B+ on the donor reading) | ESTABLISHED = world causal depth ≥ 20 in ANY lineage. The D0 lineage has a live competent member at the end in 0/23 ESTABLISHED runs, and 8/23 have zero D0 causal births. Under a donor-persists reading: NO_COPY 28/48 = 0.58, i.e. WEAK_SIGNAL (the worker's extension) | W2/W2-34_ruler_persistence/REPORT.md §4; q4_reading_b.json |
| E-P2-1 C-ZERO-SPECIFIC | 466-472 | CONFIRMED (26/48 vs 2/48) | WORDING (run-level only) | The donor-level p = 0.003 fails the frozen 0.001. 14/16 donors cannot copy from 0x5A. Within the 2 that can: ZERO 1/6, CONST 2/6, RANDOM 3/6. Read as "establishment in the entry state the donors were screened for" | W2-15 §2; W2-18 P11; ledger N11 |
| X-P2-BRIDGE | 472-474, 488-489 | CLEAN_NULL | WORDING | Restore "mutation topology" as a confound: the cells differ in mutational access to opcodes (D4). The BRIDGE effect is at the noise floor | W2-18 1b, P05c |
| ARC3 operator correction | 484-489 | CORRECTION | WORDING | "Both use OPERAND; in 7ae3 opcode bytes never mutate" is false in effect. In 7ae3, second bytes of prefixed instructions (24, 53) and operands mutate. ffa6 (SLOTTED) ignores the operator, giving about 8x the opcode supply. Copy errors flip any byte | W2-15 §1.5; W2-18 P05c |
| X-A3-FORENSIC-16000006 | 505-509 | KILLED as a single change; distributed change real | WORDING | The route ("lost and regained on 6/8 paths") is read from single 20-draw screens that flicker, and the first robust member was found with the defective SELF1 rule. The endpoint stands (8/8 CVT-R) | W2-18 P04 |
| **C-A3-INTERNALIZE** | **524-531** | CONFIRMED (8; bar 4; ffa6 7, 7ae3 1) | **RELABEL: FRAGILE** | 8 as coded / 4 at the final checkpoint (= the bar) / 3 robust under every strict reading (7ae3 23, ffa6 46, ffa6 48). Cell split two-sided p 0.063 as coded and 0.62 at the final checkpoint; it is an eligibility effect (22 vs 4 eligible, p = 1.4e-4; 7/22 vs 1/4, p = 1.0). Persistent sizes 84, 13, 41, 194 genomes. "Last checkpoint with" is the frozen design: a validity weakness, not a bug. The transient ends are real (world P-11 events → 0). No null arm. Zero-context screen | W2/W2-27_d10_rederive/REPORT.md; rederive.json; W2/W2-38_replay_dumps/REPORT.md; W2-15; W2-18 P12 |
| X-A3-SFLINEAGE | 528 (path) | SIGNAL (3/5) | STANDS | 3/3 under every reading, including reading (b) | W2-34 §4; q4_reading_b.json |
| X-MAT-INTERNALIZE | new (after 531) | ENDOGENOUS 8/8 | ADD: ENDOGENOUS / ARTIFACT-RISK | ENDOGENOUS at all 55 tagged checkpoints (max X 0.14, attributed share ≥ 0.405), so it does not depend on the endpoint. No positive control. Copy-error bytes take the executor's tag (a small bias toward L) | W2-27 Table 3; W2-15 §3 "new"; W2-18 P17 |
| X-A3-WITHDRAW | 533-553 | CLEAN_NULL (speed) | RELABEL: CEILING NULL, plus WORDING | PERSISTS is 12/12 in every arm: informative against collapse, blind to speed. ABRUPT robust share went 0.22 → 0.96 within ≤ 100 epochs, so "change within the lineage, not sorting" and "~1700 epochs" are unresolved (a sweep of members already present is not excluded) | W2-15 §5; W2-18 P03 |
| Rarity claims | 247-257, 443-451, 495-500 | various | WORDING (scope) | The base rate is a property of the encoding and geometry; see §4.1 | W2/W2-7_alien_physics/REPORT.md |
| ATOMIC label-share verdicts (X-ATOMIC-RANDOM 353, X-SWAP-ANCESTRY 360, C-SWAP-ACQUIRE 363, X-CONTENT 368, C-CORE 376, X-CORE-TIME 386, X-CERT-BREAK 389, C-A3 524, X-A3-WITHDRAW 533) | as listed | various | STANDS against the rotation leak | A rotated copy fails positional fidelity, is never promoted, and is restored. Bound: 0 runs mis-scored. The check is thin (2 seeds × 80 epochs) | W2-35 §4; s2_atomic.json |

**Row counts.**
- 43 rows in all.
- 2 FLIP.
- 2 CLAUSE-INV. One of these is combined with a relabel in the C9-H1R row.
- 11 RELABEL.
- 1 ADD.
- 5 STANDS.
- 23 WORDING-only. This counts the C-ATOMIC C1 row, whose verdict stands, and the X-H3-EASIER row. It does not count the relabel rows that also change wording.
- Check: 2 + 1 (the CLAUSE-INV-only row) + 11 + 1 + 5 + 23 = 43.

### 3. Conflicts resolved (the later verified source wins)

1. **X-H1-GRADIENT.** W2-15 marked the competence reading INV without a re-score. W2-18 P14 called that an over-flag and proposed NEEDS-RERUN.
   - **W2-19 re-scored the genomes and confirms W2-15.** Recorded held 1.000, true held 0.496; 0 readers.
   - It is stronger than W2-15 stated: 5 of 11 ABR-dominated runs record 0.72-0.91, not "about 0.9" across all.
2. **E-3 / A-1 depth vs D8.** W2-15 marked these B+. W2-18 P15 proposed NEEDS-RERUN.
   - **W2-19 settles it: E-3 stands.** D8 is negligible in A-1: 1 same-interaction double birth in 1,031 runs, on predecessor depth only.
   - W2-15's proposed change to range 198-201 is dropped.
3. **Founder independence.** W2-15 had it UNRESOLVED (p = 0.014). W2-18 P13 proposed DOWNGRADE, citing the then-unreported W2-12 draft.
   - **The final W2-12 report wins.** X-DOSE-CURVE's CLEAN_NULL and lesson 12 stand. Independence fits pooled data. The rejection belongs to C-CRITICAL-MASS's low k = 1 arm alone.
   - W2-18's objection ("the single-founder batches are homogeneous, so 'noisy single-founder rate' is not the explanation") is answered: the batches are homogeneous (p = 0.53/0.64) and the C-CRITICAL-MASS k = 1 arm sits at the low end of that spread (5/80 vs 11.1 expected).
4. **C-A3 p values.** W2-15 quoted 0.031 and 0.31. **W2-27:** those were one-sided. With no preregistered direction (`run_ci.py:28`), the right values are two-sided: 0.063 and 0.62. Recomputed here: 0.0627 and 0.6197.
5. **C-A3 cell split.** W2-15 read it as operator-confounded, 3:1. **W2-27:** the split is an eligibility effect (22 vs 4 eligible runs). Among eligible runs it is 7/22 vs 1/4 (p = 1.0), so the D4 confound acts upstream, on eligibility.
6. **C-A3 genome sizes.** W2-15 and W2-18 P12 said "84-194". **W2-27:** 84, 13, 41 and 194.
7. **D10 premise.** W2-25 (red-team) said W2-8's "L_share ∈ {0, 0.664, 1}" is false on disk (84 values), which would put the C-A3 relabels in doubt.
   - **W2-27:** the premise holds at the endpoint of the 26 eligible runs. The 8/4/3 counts never depended on it.
8. **N13 and C-A3 transience.** N13 and W2-18 P12 suggested the zero-context screen might hide carried-state copiers, so the true count could be higher.
   - **W2-34**, then **W2-38** (bit-exact replays with dumps): both collapses are real. World P-11 events fall to 0; 0008 has one lag-artifact checkpoint at 900.
   - N13(iii) is refuted and N13(ii) is unsupported. FRAGILE is not upgraded.
9. **X-MAT qualifier.** W2-15 said "4 persistent + 4 transient; ARTIFACT-RISK". **W2-27:** X-MAT is ENDOGENOUS at every tagged checkpoint, so the transience qualifier belongs to C-A3, not X-MAT. ARTIFACT-RISK stays.
10. **X-P2-BRIDGE "mutation topology".** W2-15 said drop it. **W2-18 P05c**, the later source with code evidence, says restore it as a confound (D4). Restore it.
11. **C-NORECOMB.** W2-15 and W2-9 had it UNDERPOWERED. **W2-33** adds that the null rests on one outlier BASE block, and that dropping the block gives a splice p of 0.0018.
    - **The ledger's Nestor ruling (02:33Z) is adopted.** Record "C-NORECOMB's null is uninformative". Do NOT cite the post-hoc 0.0018. Cite C-RUNAWAY's own arms: 4/150 vs 20/150 at depth ≥ 5.
    - **The sidedness of that figure is corrected here.** p = 5e-4 is one-sided (4.9e-4). Two-sided it is 9.9e-4.
12. **"Second regime" / persistence anomaly** (W2-22 → W2-29). W2-22 reported the world above FIELD BANK (4/4 vs 9/33, p = 0.011).
    - **W2-29**, on 600 seed-matched seeds, finds 8/22 vs 5/33 (p = 0.069) on B_xk, and 9/22 vs 9/33 (p = 0.22) on B.
    - No FINDINGS line carries this claim, so there is no table row. Any later citation should use W2-29's UNRESOLVED / underpowered status, not W2-22's p = 0.011.
13. **W2-17 two-type mixture** (outside FINDINGS). **W2-26:** W2-17's S0/S1 "types" are event-side tags; 72% of control switch edges have a non-7ae3 parent.
    - "A morph is necessary for crossing ~27" and "a 7ae3 morph is necessary for persistence" are both REFUTED.
    - No FINDINGS line changes. This feeds scope note 4.2 and lesson 3.

### 4. Cross-cutting scope notes

**4.1 Rarity claims are scoped to stock Z8 physics.**
- Stock Z8 physics here means: 128-byte ring, 7-bit address wrap, block op LDIR/LDDR, slice 300, zero entry registers.
- W2-7 shows that physics alone moves the random-genome copier rate by more than 3 orders of magnitude, from 0/12,000 under NOWRAP, NOBLOCK, ROTATE and REGRAND to 702/3,000 under SELFCOPY:
  - STOCK 2/12,000;
  - RING192 90/12,000 (about 40x).

  Both figures were checked in `PROBE_random.json`. Stock pooled with FOR gives 5/26,024 ≈ 1.9e-4.
- So every quantitative rarity or accessibility statement should carry the clause "under stock Z8 physics". This covers:
  - E-W1-1's encoding-accessibility reading (443-451);
  - the ARC3 acquisition landscape "0/6,400" (495-500);
  - Wave-1 minimal_prior.
- **Not checked:** E-8 (247-257) is the c9x non-pair FREE physics, which W2-7 did not probe. The same scoping principle applies, but no number was measured there.

**4.2 Label-share readouts in BASE.**
- Every FINDINGS verdict that reads anc0_share or L_share runs under ATOMIC, so it is immune to the BASE rotation leak (W2-35; 0 mis-scored).
- In BASE the label is neither necessary nor sufficient for descent:
  - unlabelled rotated frames carry founder code (0.25 rotated halves per founder birth; 0.043 viable and unlabelled);
  - labels survive wholesale in-place content replacement (W2-26).
- Affected readouts are descriptive only: X-RUNAWAY "70-97%" (a lower bound), X-TICKET lineage-loss wording, and X-STALL membership.
- **Separate caveat that applies under ATOMIC too:** on a closed 256-site tape, L = 1.0 is absorbing (0/11 drops; W2-34), and it labelled populations that had stopped copying (W2-38: world P-11 events 0 after the collapse).
  - "L stays at 1.0" / "the lineage still holds the population" is never evidence of heredity.
  - **Worker's extension, not verified on X-A3-WITHDRAW data:** this applies to the X-A3-WITHDRAW wording at 547.

**4.3 Zero-context screens.**
- `run_de.competent` screens from a zero entry state with a blank partner, and it is used inside CARRIED worlds. Affected:
  - C-A3's competent / free counts;
  - the C-ZERO-SPECIFIC donor panel (N11: 14/16 donors cannot copy from 0x5A);
  - X-P2-REGSTATE.
- The C-A3 collapses were checked against carried and realized contexts and are real (W2-38). Carried-state copiers invisible to the zero screen do exist, briefly (0008 at epoch 900: zero screen 1/64, 29 hidden).
- Self-carried contexts convert some side-1 7ae3 genomes at side 0: 0.91-1.0 vs 0.13-0.18 under ZERO (W2-26).
- **Rule proposed:** the world's own P-11 event count per checkpoint (exhaustive, carried registers) is the persistence ruler. A zero-context count may be shown beside it, never alone.

**4.4 Max-of-cached readouts.**
- `held_max_final` / `d_held_max` is a maximum over genome-cached single 6-episode draws.
- A 0.5 coin-flip guesser:
  - reaches 1.0 on one draw with P = 1/64;
  - crosses at least once in 100 validation epochs with P = 0.79;
  - reaches an expected max of 0.86 over 20 draws (W2-19; checked in `rescore_h1.json`).
- Affected:
  - A-2 (delta stands);
  - A-3 read order;
  - E-4 crossing epochs;
  - the C9-H1R / X-H1-* family;
  - X-TASK-GATE (already blocked).
- Not affected: W1, P2 and ARC3 verdicts, which are read from P-11 assays (D1 and D9 reach none; W2-15 §1.3, W2-18 §2.2).

### 5. Proposed new lessons (13-18; deduplicated against D.1-12)

13. **A ruler's context must be the world's reproductive context, and a panel screened in one context cannot show that context is special.**
    - Before any static-to-world inference, read from the world's own code which ruler it uses. Three mismatches occurred in Wave 2:
      - zero vs carried registers (N11, N13, W2-26, W2-34);
      - FID vs exact identity (W2-40);
      - event-side tag vs genotype (W2-26).
14. **A maximum over, or a cached copy of, a noisy single-draw score is a selection amplifier.** Re-score fresh before reading it as competence; report the estimator beside the number (W2-19). Lesson 4 covers event vs state, not estimator choice.
15. **A lineage label is not descent.** On a closed tape a full label is absorbing, labels survive in-place replacement, and rotated copies escape the label. Measure persistence with the world's exhaustive event counter, and membership with content- or frame-keyed provenance (W2-34, W2-35, W2-26, W2-38). Lesson 2 covers similarity, not labels.
16. **Store genome bytes and registers at every checkpoint.** Five Wave-2 questions were blocked by tag-only records:
    - C-CORE 34/49;
    - the H1 re-score;
    - run 52;
    - run 0008;
    - W2-17 genotypes.

    The cost is about 256 × 64 bytes per checkpoint (W2-34).
17. **A base rate is a property of the physics that produced it.** State every rarity number with its encoding, geometry and slice (W2-7).
18. **Extends lesson 12. Pooling or dropping blocks that are not exchangeable creates or erases effects.**
    - Test homogeneity first, and use block-stratified exact tests.
    - Never strengthen a claim by dropping a block identified post hoc (W2-12, W2-33).
    - State the sidedness of every p value (two corrections in this appendix).

**Considered and folded into existing lessons rather than added:**
- P01's "declared factor must reach the scorer" goes under lesson 9.
- P08's "cannot-fire recurred" goes into the lesson-1 wording row.
- "Aggregate trajectories cannot carry per-site claims" (W2-18 P16/N16) and "a tolerance must be sized against its base rate" (W2-37) were left out to keep the cap. They stay in the ledger.

### 6. Status statement

- **None of these entries rewrites a frozen verdict, a frozen file or a preregistered rule.**
- Every row above is a **proposal pending operator or steward review**. The frozen texts stay as written.
- If a proposal is accepted, it is applied as a dated addendum beside the frozen text, never as an edit to it.
- Verdict classes in the frozen record (REPORT_C9.md, the VERDICT.json files and the FINDINGS entries) remain the record of what was decided at the time.

---

### Verification log (W2-48)

**Recomputed here (scipy Fisher exact, read-only):**
- C-RUNAWAY depth ≥ 5: BASE 4/150 vs NO_RECOMB 20/150, tallied from `C9X/c_runaway_confirm/RESULTS.json`. One-sided 4.9e-4; two-sided 9.9e-4.
- C-NORECOMB per specimen: 7ae3 5/24 vs 5/24, c2a8 0/24 vs 0/24 (`VERDICT.json`).
- C-A3:
  - 7/72 vs 1/72: two-sided 0.0627, one-sided 0.0314;
  - 3/72 vs 1/72: two-sided 0.620;
  - eligibility 22/72 vs 4/72: 1.43e-4;
  - 7/22 vs 1/4: 1.0.
- D12 unconditional 34/48 vs 11/48: one-sided 2.3e-6.
- W2-29 figures:
  - 8/22 vs 5/33: one-sided 0.069;
  - 9/22 vs 9/33: 0.22;
  - 9/22 vs 4/4: 0.096.
- W2-22's 4/4 vs 9/33: 0.011.

**Checked against the workers' JSON:**
- `rederive.json`: 8/4/3 runs and p values.
- `d12_sensitivity.json`: 36/64 vs 1/64, p 3.5e-13; 7.6e-4, 0.005 and 0.040.
- W2-12 `models.json`: 0.31, 0.64, β 1.13 (p 0.095), 0.014; drop-one β 1.06 and 1.45.
- `q4_reading_b.json`: 0/23, 8/23, 28/48 and 20/25.
- `s2_atomic.json`: 315 and 923 transients, 0 alive.
- `rescore_h1.json`: 0.496, 0.495, 0.0003, 1/64, 0.79, 0.86 and generous 0.1417.
- `PROBE_random.json`: 2/12,000 and 90/12,000.
- `C9X/c9_h1r/VERDICT.json`: 0.1972 = 0.1972; I 0.20, M −0.10.

**Not independently verified (taken from report text only):**
- W2-19's strict I bound 0.125 and X-H1-GRADIENT's "11/20 runs, 5 at 0.72-0.91";
- W2-18 P01's 171/638 split and +0.129 / −0.098;
- P03's 0.219 → 0.956;
- P05a's retention values 0.86 and 0.04;
- P07's "about 75%" (N9/N10);
- P11's 1/6, 2/6, 3/6;
- W2-22's C− Koopman 1.31 [0.60, 2.80] (only the C+ figures were found in `a1_analysis.json`);
- W2-35's rates.
