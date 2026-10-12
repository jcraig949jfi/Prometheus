# INDEPENDENT ADVERSARIAL REVIEW: BETA-03 (C-011) RESULTS BEFORE THE CLOSE SYNTHESIS

Directive s13 deliverable: "an independent adversarial review". The reviewer was not involved in design, running or
reporting. Written 2026-10-09 at about 07:50Z, during W07.
- **Method:** read-only. I read the directive, ledger, state, close rule, preregistrations and amendments, freezes,
  reports, runners and prior reviews.
- **Independent reducers:** my own Python reducers over the frozen JSON/JSONL receipts. They do not import the
  campaign code. Total CPU was well under 3 minutes.
- **Not run:** no donor runs, walks or known-answer reruns.
- **Remit (directive s12):** a reviewer may flag a mis-implementation or an overclaim, but may NOT redefine frozen
  outcomes. Each finding below says whether it changes a label.

## 0. Verdict
- **BLOCKER: none.** Every headline number I could recompute from the receipts reproduces exactly.
- **Every frozen label re-derives** from the prereg text applied to the result JSONs, and the close-rule row (4) is
  correctly selected. The A3 technical rerun touched bookkeeping only, and I verified that from row structure.
- **MAJOR: 4.** Each concerns interpretation or wording in the reports, not a label:
  - M1: the Q6 answer breaks CLOSE_RULE's mandated wording and overstates the causal evidence;
  - M2: "SELECTION dominant" is overstated;
  - M3: every eligible promoted candidate is a re-spelling of a plain schema the same recipient also derived;
  - M4: the SHAM control is degenerate, and it exposes an interference channel the E1 wording omits.
- **MINOR: 11.**
- **W12** (selection-override oracle) was still running at review time (1014/4432 walks at 07:50Z). It is not
  assessed here except for one design note (m11).

## 1. Integrity checks (all PASS)

| Check | Result |
|---|---|
| Runner, prereg and close-rule sha256 vs freezes | All match: b03 1febd5d5, b03_e2 f9448560, b03_e5 a5047361 (post-A3), b03_e6 07ae4e43, w5p donor a5d7b755, promote 33a28d01, E1/E2/E5N/W12 preregs, CLOSE_RULE 344d08d5 |
| E1 common residual recomputed from E1_START_WALKS alone | 329 slots, identical to the frozen E1_COMMON_RESIDUAL.json per pair |
| CLOSE_RULE freeze record ("E1_RECIP.jsonl at 9 lines, sha f518dd41") | The first 9 lines of the current E1_RECIP.jsonl hash to f518dd41..., so it matches |
| W12 libraries hashed before any walk | W12_LIBRARIES.json = a715314a..., matching FREEZE_W12 |
| Walk receipts | No missing walk for any index entry in E1, E2 or E5-N, and no conflicting duplicate (lib, family, cell) across files |

## 2. Headline numbers recomputed from raw receipts

All recomputed from the walks and index files with exact sign-flip enumeration, independently of b02.flip_test.

| Quantity | Report | Recomputed | OK |
|---|---|---|---|
| E1 acquisition on the common residual (L_g11 / L_I0 / L_P) | 28 / 24 / 35 | 28 / 24 / 35 | yes |
| E1 inherited capability (L_g11 / L_I0) | 143 / 44 | 143 / 44 | yes |
| E1 own-start improvement (b02 cell-conditioned) | 33 / 88 / 137 | 33 / 88 / 137 | yes |
| E1 end state | 388 / 355 / 363 | 388 / 355 / 363 | yes |
| E1 interference contrast L_g11 - L_P | -7, 2/4/16, p2 0.4375, k 6 | same | yes |
| E1 own-start deficit | -104, 1/20/1, p1 (neg) 2.4e-6 | same | yes |
| E1 headroom share | 0.933 | 0.9327 | yes |
| E1 end state, is L_P better? | 3/8/11, p 0.972 | same | yes |
| E1 Holm [interference, saturation] | [F, T] | [F, T] | yes |
| E1 PC (best arm L_P) | 35 families / 12 pairs | same | yes |
| E2 totals (I_0 / g11 / g12), from E2_WALKS + E2_INDEX | 94 / 179 / 142 | 94 / 179 / 142 | yes |
| E2 g12 - I_0 | +48, 13/6/5, p1 0.0531 | same | yes |
| E2 g12 - g11 | -37, 3/11/10, p (g11 > g12) 0.0479, p2 0.0958 | same | yes |
| E2 NI margin (delta x10 = 7) | p 0.832 | same | yes |
| E2 non-eliminating | 20 vs 24 | 20 | yes |
| E5-N acquisition (A / B / C / D / E / F) | 35 / 28 / 35 / 29 / 24 / 11 | same | yes |
| E5-N P1 = D - C | -6, 3/4/15, p1 0.820, k 7, min p 0.0078 | same. Per pair: +1 (99), +3 (115), +1 (117); -5 (100), -3 (114), -2 (112), -1 (109) | yes |
| E5-N P2 = D - B | +1 (pair 99) | same | yes |
| E5-N SHAM (residual minus sham-start reach) | +25, 9/0/13, p 0.00195 | same. The sham start reaches 10 common slots | yes |
| E5-N KILL_CRITERION_HESTIA | FIRES (22 >= 20; P1 not positive; 1/22 = 0.045 < 0.10) | same | yes |

Not independently recomputed (taken from receipts):
- the E5-N cost ledgers (only spot-checked as ratios: 614M/175M = 3.5x; 6.52e9/5.42e9 = 1.20);
- E1 semantic-class medians and the ordering ratio;
- g12's internal S scores (my MEMORISE reach in m4 is an approximate reconstruction);
- all known answers (re-running them would need donor runs).

## 3. Label re-derivation against the prereg text

| Label | Re-derivation | Agrees |
|---|---|---|
| E1 disposition MEASURED | known pass, PC 35/12 >= 5/3, 22 >= 18 pairs | yes |
| E1 SATURATION_SUPPORTED = YES | PC; one-sided p 2.4e-6 < 0.05 with sum < 0; share 0.933 >= 0.5; L_P not better at end state (p 0.97) | yes |
| E1 INTERFERENCE_SUPPORTED = NO | two-sided p 0.4375 >= 0.05 | yes |
| E1 REPRESENTATION_CEILING_CONSISTENT = NO | conditions 1-3 hold (no enabling; best fraction 0.106 < 0.25); condition 4 fails (pairs 111 and 117 extend and acquire 2 each) | yes (see E1_REPORT s4 for why this is weak) |
| E2 G12_GENERAL_RULE = INCONCLUSIVE | sum vs I_0 > 0, so not NO; claim 2 PASS 18/18; claim 3 UNTESTED (0 attractive), which caps the label at INCONCLUSIVE whatever the p value | yes |
| E2 G12_VS_G11 = INFERIOR | one-sided g11 > g12, p 0.0479 < 0.05 | yes (but see m5) |
| E5-N gates | no-op 22/22 (it includes post-A3 rows for pairs 117-119); PC 35/12 with F excluded | yes |
| E5-N R8_UNDER_PROMOTION (natural) = NO | P1 sum -6, so not enabling; SECOND-LEVEL 1 < 3. The YES conjunction fails on two conjuncts | yes |
| E5-N channel = OPEN | arm D derived in 19 pairs; non-trivial depth-2 selected in 4; attributed in 1 | yes |
| E5-N P1 sign and residual | D - C on E1's frozen common residual, one-sided upper tail | yes |
| SHAM residual | C minus the families the L_SHAM START reaches; F excluded from the PC maximum | yes, as A1 specifies |
| Attributed depth-2 | non-trivial depth-2 selected AND the first qualified program's body is outside G5 AND inside a promoted-form entry's bodies | implemented as A1 states. Its scientific reading is in M1 |
| CLOSE_RULE | E5-N NO, E6 negative branch only, so no NO_AFTER_ATTACK; row 3 does not apply; **row 4 -> MIGRATE_SUBSTRATE**. Mandatory fields (BASIS, S10 NOT_MET, Hestia proxy, qualifiers) are present in STATE.close_recommendation | yes |

## 4. Amendment A3 (technical rerun after a partial run): verified bookkeeping-only

| Check | Evidence |
|---|---|
| Row structure | E5N_RECIP.jsonl rows 0-72 (73 rows, pre-A3) have 17 keys and no `unpromotable_selected`. Rows 73-87 (15, post-A3: 116 L_g11 / L_I0 / L_SHAM and 117-119 x4) have 18 keys. The `w5p` block has 14 keys in every row. This matches "73 kept, 15 resumed" |
| Rows the stand-in actually touched | **Only row 73** (pair 116, arm D): `U_9e3357f56402`, schema `(acc - gcd(|gcd(|H|,|H|)|,|v|))`, deps [], depth 1. The other 14 post-A3 rows have an empty list, so the code path is identical to pre-A3 |
| Could A3 change selection or transfer? | No. The patch only wraps `Promoted.from_schema(kind == "selected_entry")` and re-raises every other error. Transfer is walked later (`stage_score`) from `selected_entries` |
| Could it change a label? | No. Pair 116 arm D has dag_depth_selected 1, so it is not in the depth-2 set, and its common acquisition is **0**. Even if it were re-classified as depth 2 it could not add a SECOND-LEVEL pair or change P1 |
| Exposure | The D2_chain.log traceback (line 96) directly follows 73 selection log lines, including arm-D `depth=` / `usesP=` fields. The disclosure says one line was seen; I cannot verify that. Because A3 is outcome-independent (above), exposure could not have steered it |

## 5. Findings

### M1 (MAJOR, wording; no label change): the Q6 answer breaks CLOSE_RULE and overstates the depth-2 evidence
- **What CLOSE_RULE requires.** "Q5 and Q6 must be answered 'not established in this engine', unless row 1 applies."
  Row 4 applies.
- **What E5N_REPORT s5 says instead:** "Q6 (maximum clean dependency depth): 2, in a single pair." The directive's
  Q6 asks for depth "supported by clean causal evidence". The pre-registered causal tests (E6 PLAIN control, SHAM
  primitive swap) ran only on the YES branch, so the depth-2 attribution for pair 99 was **never causally ablated**.
  It rests on bookkeeping: the body lies outside G5, inside a promoted-form entry.
- **Q4 wording.** "reached 1 family that only a promotion-built body solves" is not supported. W8 endpoint families
  have G5 witnesses by design (W5P_DESIGN s6(a)), so the attribution only says that **arm D's first qualified
  program** was a promotion-built body.
- **Evidence that cuts the other way (in fairness).** E1 arm B (ordinary, same pair 99) selected the plain twin
  `(acc - ({H} - v))`.
  - That twin has the same expansion as D's `P_d58d7c2969b5(({H} - v))`, but instantiates only **6** atom-filled
    bodies, against **167** for the promoted form.
  - B censored on `waoqfa`. D solved it at charge 22,769 with `(acc - (gcd(|acc|,|first|) - v))`.
  - So the out-of-G5 body really does exist only through W5P's promoted-form instantiation: deeper hole fills past
    W5 depth 3.
  - It is still one family in one pair, with no ablation.
- **Required:** the synthesis should answer Q6 as "not established in this engine". It may add, as a qualifier: one
  pair (99) where a selected depth-2 promoted schema produced one EXTEND acquisition; not causally ablated; the
  ordinary plain twin did not reach it.

### M2 (MAJOR, interpretation; no label change): "SELECTION 15/22, often ELIGIBLE" is overstated, and one example is wrong
Source: E6_NEGATIVE_DIAGNOSIS.json per_pair, `selection.kind`. The 15 SELECTION pairs split into:
- **ELIGIBLE_REJECTED: 6** (96, 110, 114, 115, 116, 118);
- **NONE_ELIGIBLE: 8** (97, 101, 104, 106, 107, 112, 113, 119);
- **ONLY_BARE_REEXPRESSIONS: 1** (108).

Problems:
- **The prereg's definition is narrower than the runner's.** E5N_PREREG s6 (NO branch, step 2) defines SELECTION as
  "derived, were they **eligible and rejected** by g11?". The frozen runner (`pair_link`) assigns SELECTION to every
  derived-but-not-selected pair, whether or not anything was eligible. For 9 of the 15 pairs, nothing promoted
  passed g11's eligibility gate. That is a candidate-quality or validation failure, not "selection rejects
  legitimate improvements".
  - The runner is frozen and its histogram stands. The INTERPRETATION should report the split.
- **Pair 116 is a tie-break artifact.**
  - The selected plain `SCHEMA_41` and the eligible promoted `P_ba25626777b7(gcd(|H|,|H|))` have the identical
    expansion and the identical mean paired saving (4112.27).
  - The plain spelling won. Under the other spelling, pair 116 would have been "depth-2 selected" (it would become a
    TRANSFER link, with 0 acquisitions).
- **Factual error.** E5N_REPORT s3 says of pair 96 that "Both were eligible". In fact `P(gcd(|H|,|v|))` was
  **INELIGIBLE**; only `P(({H} - v))` was eligible (saving 257.9 vs the selected `(acc + {H})` at 561.6).
- **Consequence for Q7.** "The dominant obstacle is SELECTION" should read: SELECTION 6/22 (eligible promoted
  candidate outscored); no eligible promoted candidate 8/22; CANDIDACY 3; TRANSFER 3; complete chain 1.

### M3 (MAJOR, interpretation of Q4/Q7; no label change): every eligible promoted candidate is a re-spelling of a plain schema derived in the same recipient
- **Method.** For arm D, each non-trivial promoted candidate eligible in the recorded selection_table was expanded
  using the row's `promoted_in` registry and compared with the row's `derived_schemas` (A2 receipt).
- **Result: 23 of 23 eligible promoted candidates, across 8 pairs** (96, 99, 102, 110, 114, 115, 116, 118), have an
  expansion that the same recipient ALSO derived as a plain schema. That includes the two selected depth-2 schemas
  (99, 102).
- **What promotion adds in natural W8.** It contributes no candidate MECHANISM that plain LGG did not also propose.
  Its only extra is extent: promoted-form instantiation admits depth-1 fillers past G5 (pair 99: 167 vs 6 bodies).
- **Consequence.** Q4 ("genuinely new attainable second-order structure") should say so explicitly. Q7 should place
  the binding limit upstream of selection: the supply or representation of structure that is not already
  plain-derivable. That is consistent with E5-H's CANDIDACY failure and with Hestia's one-hole finding.
- This was computed from the receipts only and is reproducible. It needs no new runs.

### M4 (MAJOR, interpretation; no label change): the SHAM control is degenerate and exposes an interference channel
- **The sham recipient barely learns.** Arm F (L_SHAM, promotable):
  - observes **0 programs in 19/22 pairs**;
  - derives nothing in 20/22;
  - selects INHERITED in 20/22.
- **On the SHAM residual,** F acquires **1** family where the pristine promotable arm C acquires **33**: F - C = -32,
  0/10/12, p2 = 0.002. Arm F's headline 11 is 10 sham-start slots plus 1.
- **Therefore the significant D - F = +25 measures "the g11 recipient learns at all".** It does not show that the
  g11 library carries information a matched library lacks. Had P1 been positive, SHAM would have passed almost
  automatically. The report's sentence ("the g11 library is a better inheritance than a frequency-matched sham") is
  true but uninformative, and should say this.
- **Underclaim in E1/Q1.** INTERFERENCE_SUPPORTED = NO is specific to g11 libraries on the common residual. The same
  engine shows catastrophic interference from a non-solving inherited library.
- **Hypothesis to record (not verified by a run):**
  - Every L_SHAM library, and 21 of 22 L_g11 libraries, put a prefix of **>= 57,960 candidates** (one one-hole
    schema entry) ahead of the pristine `organ_fold`. That is larger than the **30k observation escrow**.
  - If observation walks entries in order (as b03_e6._span_to_promoted assumes), an inherited recipient can only
    observe programs inside its inherited prefix. That would explain both the sham starvation and why arm D's
    derived promoted schemas are re-spellings of the inherited schema (M3).
  - Same mechanism as red team M6 (gen-1 observation starvation), here on natural W8.
- **TFS-1 obligation:** measure escrow vs inherited-prefix size.

### Minor findings
- **m1. E1 residual construction vs the directive's "BOTH".**
  - Directive s4.B asks for mechanisms "unsolved by BOTH starting libraries" (pairwise). E1 used the union of three
    starts, including L_I0. This was frozen pre-data and is legitimate, but 10 slots are excluded that only L_I0's
    start reaches: there the L_P recipient acquired 6 and the L_g11 recipient 0.
  - On the pairwise (L_g11, L_P) residual (339 slots): L_g11 28 vs L_P 41, **-13** (2/5/15, p2 0.17).
  - INTERFERENCE stays NO, but "-7" is the most favourable of the two constructions. Report both.
- **m2. Headroom share units.**
  - With family-level own-start improvement (L_g11 29, L_P 93, deficit -64), the share is **0.891**. On the pairwise
    residual it is 0.80 at family level, or 0.875 with the cell-level deficit.
  - SATURATION is robust (>= 0.5 everywhere). Quote "about 80-93%" rather than "93%".
  - A direct reading: 52 of L_P's 93 family-level gains (56%) lie inside L_g11's start reach.
- **m3. Selection-gate saturation is not discussed.** L_g11 recipients select INHERITED (nothing new) in 5/22 E1
  pairs, against L_P in 1/22. Pair 100 accounts for the largest single common-residual loss: L_P 5, L_g11 0. This is
  the "selection-gate saturation" channel raised by red team E1-6. Mention it in Q1.
- **m4. E2 claim 2 wording.**
  - g12 is a designed endpoint-aligned rule. Nothing was evolved or learned (directive objective 1 asked for an
    "evolved, generalizable acceptance rule"). "g12 learns to reject memorisation" should read "a reach-scored
    acceptance rule, with no type ban, rejects memorisation".
  - Approximate reconstruction from g12 `programs` / `folds`: in about 10 of the 18 attractive seeds, MEMORISE reaches
    **0** validation families in both folds. The fold minimum matters in at most about 8.
  - Attractiveness is defined by I_0's saving table, not g12's metric. The result shows that reach scoring makes
    memorisation unattractive, which is valid for "without a ban", but nearly by construction.
- **m5. G12_VS_G11 = INFERIOR** is a one-sided p of 0.048. Paired SUPERIOR/INFERIOR one-sided tests at 0.05 amount to
  a two-sided test at 0.10 (two-sided p 0.096; Holm n.s.). The synthesis must keep "frozen one-sided rule; not
  Holm-significant" attached to it.
- **m6. Cost attribution (E5N s4).** The 3.5x search charges and the "+1 family for 4.4e8 charges" compare D with C.
  That conflates the cost of walking an inherited library with promotion overhead. The promotion-specific overhead is
  the 1.20 expanded/promoted ratio. D vs B is not on the same ledger.
- **m7. Count.** "Pairs deriving promoted-constituent schemas 19/22" includes pair 108 (bare re-expressions only).
  Non-trivial derivation: 18/22.
- **m8. BASIS framing.** BASIS = OUTCOME_C_APPARATUS_LIMIT is mandated and correct for the recommendation. The
  synthesis should add that the natural-world assay itself was VALID (no-op 22/22, PC, attainable P1) and returned NO.
  The evidence is not only an apparatus limit; W5P worked technically, close to the operator's Outcome B.
- **m9. Compute ledger.**
  - STATE.compute.ledger has no entry after 2026-10-08T14:19Z (44.5 est), even though day-2 jobs ran 05:15-07:34Z
    and W12 has run from 07:37Z.
  - "Roll-off at 05:15Z" is imprecise: the Oct-8 foundry (05:10-11:44Z, about 26 core-h) rolls off progressively
    until 11:44Z Oct 9.
  - At 4 workers, new consumption roughly equals the roll-off rate, so the cap was very likely respected, but this is
    not documented. Add a measured entry before close.
- **m10. Pre-freeze visibility.**
  - When CLOSE_RULE A1 was frozen (13:19:59Z), E12_chain.log already held the E2 donor selections (12:02-12:35Z,
    including I_0's MEMORISE picks, from which claim-2 attractiveness can be read) and E1 recipient selection lines.
  - These are not transfer outcomes, and E1/E2 are qualifier-only under the rule, so they could not have steered
    anything. The claim "frozen before any outcome was read" is accurate in the strict sense; disclose the log
    visibility.
- **m11. W12 design (running).**
  - The oracle maximises over arm D's promoted candidates but compares with arm C's ACTUAL selection, not with an
    oracle over C's candidates. A YES is inflated beyond best-of-k by this asymmetry.
  - Given M3, a YES also could not separate promotion from picking a better plain-twin schema.
  - The prereg's asymmetric reading (YES weak, NO strong) already limits the damage. Keep W12 qualifier-only.

## 6. Answers to Q1-Q8 as drafted: assessment

| Q | Draft (reports) | Assessment |
|---|---|---|
| Q1 | "yes ... mostly unequal residual headroom" (E1) | **Supported.** Robust under the pairwise residual (-13, n.s.) and the family-level share (0.80-0.89). Add m3 and M4: interference is real for non-solving libraries and through the selection gate, but not shown for g11 libraries |
| Q2 | "partly; YES rejects memorisation without a ban" | **Supported with wording fixes (m4, m5).** "Learns" overclaims. Preference for transferable abstraction is not established (INFERIOR, one-sided) |
| Q3 | YES (exact semantics, hashed, transplantable) | **Supported** as a capability claim. Add that, in natural W8, the derived promoted schemas re-spell plain-derivable schemas (M3) |
| Q4 | "MARGINALLY: 1/22 ... only a promotion-built body solves" | **Overclaimed wording (M1, M3).** 1 EXTEND acquisition in 1 pair; promotion adds hole-fill extent but no new candidate mechanisms; E5-H INSTRUMENT_UNVALIDATED |
| Q5 | "NOT ESTABLISHED in this engine" | **Correct and compliant** |
| Q6 | "2, in a single pair" | **Non-compliant with CLOSE_RULE and overclaimed (M1).** Must be "not established in this engine", with the pair-99 qualifier |
| Q7 | "dominant obstacle SELECTION" | **Overstated (M2, M3, M4).** Better: SELECTION 6/22, no eligible promoted candidate 8/22, CANDIDACY 3, TRANSFER 3. All eligible promoted candidates are plain re-spellings. A plausible observation-escrow starvation sits upstream. E5-H known-positive control fails |
| Q8 | MIGRATE_SUBSTRATE (row 4; BASIS Outcome C; S10 NOT_MET; Hestia proxy FIRES) | **Correctly derived and appropriately qualified.** Banned wordings are absent from the reports. Add m8 |

## 7. Bottom line
- **The frozen labels stand:**
  - E1 SATURATION_SUPPORTED / INTERFERENCE no / CEILING_CONSISTENT no;
  - E2 INCONCLUSIVE / INFERIOR;
  - E5-N NO;
  - Hestia proxy FIRES;
  - MIGRATE_SUBSTRATE.
- **A3 is clean.**
- **What must change before the close synthesis is interpretive:**
  - Q6 wording (mandatory under CLOSE_RULE);
  - the SELECTION narrative (6, not 15, eligible-rejected; the pair-96 example error);
  - the plain re-spelling finding (M3);
  - the degenerate sham and the interference channel it reveals (M4);
  - the residual and share sensitivities (m1, m2).
