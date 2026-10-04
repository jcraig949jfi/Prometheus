# C-006 Tasks A + B: feedback ingestion and defect triage (Aphrodite V2-B Beta-01)

Analyst: read-only subagent, 2026-10-04. Tree: C:\Prometheus-worktrees\aphrodite-beta01 @ 698255f6c (origin/main).
Nothing was committed, edited, or posted. All paths are relative to the repo root. `E/` = roles/Aphrodite/engine/,
`S/` = roles/Aphrodite/science/. Every code claim below was checked by grep/sed or by reading a result JSON. I did not
run a search, a test, or a re-score.

Sources read:
- `docs/phase3/intake/tantalus/seats/Aphrodite.md`, in full (513 lines).
- No `docs/phase3/intake/*/_frag/Aphrodite.*` files exist (glob empty; `find -iname '*aphrodite*'` under intake/ returns
  only the seat file).
- `docs/phase3/design/ASTRA-6.0/FAILURE_TO_GATE_MAP.md`: T03, T04, T09-T12, T15 and lines 1-20.
- `docs/phase3/design/ASTRA-6.0/evidence/TANTALUS_AUDIT.md`: L29, F07 L139-144, inventory rows L214-217, and G02/G06/G07/G11
  at L249-259.
- `ops/threads/TH-018.md` to `TH-021.md`.
- `roles/Aphrodite/review/ARC3_MERGE_REVIEW_PACKET.md`, in full.
- `roles/Aphrodite/harvest_2026-09-30/evidence/findings_A1_defects.md`: Aphrodite rows D27-D33, D51, D53-D55 and the
  class rows at L188-196.

Code checked: `E/run_s3s4.py`, `E/a16.py`, `E/a17.py`, `E/run_g2.py`, `E/s2_gate.py`, `E/tribunal_t4.py`,
`E/a19_c2.py`-`E/a23_c3r2c.py`, `E/fair.py`, `E/certify_expressivity.py`, `S/compounding/rb1/ruler_v2.py`, and the
`S/arc3/w2|w3|w7` reports. Result JSONs checked: S3_ARTIFACT, S4_RESULTS, A17_E*, G2_RESULTS and A23_C3R2C_RESULT.

---------------------------------------------------------------------------------------------------------------------
## TASK A -- Source list (findings that name or plausibly affect the engine or its results)

Key: FITS = the claim matches the code or data as checked. DNF = does not fit. PART = fits with a correction.

### A.1 Tantalus seat dossier (`docs/phase3/intake/tantalus/seats/Aphrodite.md`)

| id | src line | claim | fit | reason / quote |
|---|---|---|---|---|
| TA-01 | :20-24, :145-147 | The improver (operators, LGG, selection) is immutable. Only the library (data) changes. BOUNDED_RSI is library inheritance. | FITS | improver.py docstring, quoted at dossier :145-147; TANTALUS S10 verified it |
| TA-02 | :134-136 | v1 lineages were clones until AMENDMENT 3 added lineage-keyed entropy | FITS | `E/engine.py:56 def dev_entropy(lineage_id: str, generation: int)` |
| TA-03 | :159-160 | run_s3s4 S4 condition 4 (L391) and condition 8 (L420) are constant True | FITS | `E/run_s3s4.py:391 c["4_hostile_evaluation"] = True  # only tribunal-qualified solutions counted`; `:420 c["8_no_donor_state"] = True  # membrane: artifacts carry module bytes only` |
| TA-04 | :161-162 | The S4 POSITIVE_CONTROL (acc + {H}) equals the derived schema, so it did not discriminate | FITS, and worse than stated (see TB-S4b) | `E/run_s3s4.py:245 pos = set(T.instantiate("(acc + {H})"))`; `:317 "POSITIVE_CONTROL": [entry("positive_control", T.instantiate("(acc + {H})"), ...`; S3_ARTIFACT `derived_schemas = ['(acc + {H})']`, `derived_equal..._REPORTED_ONLY = {'(acc + {H})': True}`; S4_RESULTS shows DERIVED and POSITIVE_CONTROL efforts identical in 7/7 families (e.g. 34180.3 / 34180.3) |
| TA-05 | :163 | a16.py L490 and a17.py L581: donor adjudication validity is constant True | PART | Real lines are `E/a16.py:489` and `E/a17.py:581`: `out["donor_adjudication_valid"] = True`. No verdict reads the field (grep finds writes only), so it is a constant *label*, not a gate input |
| TA-06 | :165-166 | The T4 query window differs from dev for ~1.7% of families; A23 ran on the unrepaired T4 | FITS | `E/tribunal_t4.py:279 bat["ce"].append(mk(xs, r.choice([1, 2, r.randint(3, 97)]), "ce", i))` vs the dev draw `E/a17.py:82 m = rng.randint(3, 97)`; W7 REPORT :13-16 (11/644 families) |
| TA-07 | :178-179 | The E2 recursion-dividend gate was barely reachable (theta moved 0.01, exploit needs 0.033) | FITS (historical) | calibration ledger; Tier-1 toy outside the engine |
| TA-08 | :189-191 | The numtheory "discovery" a*b+1 is a coprime shortcut; the aggregate test passed it | FITS (historical) | per-class test added; engine v1 only |
| TA-09 | :203-207 | The tribunal admits exactly commutative bounded folds = G1's span, so the admission ruler and the abstraction are the same object | FITS (claim) | frontier s4; not code-checked here, but consistent with S4_RESULTS: PRISTINE solves only the 2 `tc_rel_*` families |
| TA-10 | :215-220 | A23 selected composition = planted motif in 7/8; VALIDATE was built from 2 motif instances | FITS | `E/a22_c3r2.py:11 (3) VALIDATE = 2 instances of m_A (so selection can see the recurrence; W6 R2)`; A23 RESULT `PRINCIPAL_ATTACK.motif_recovery.G1 = 'selected == motif literally 7/8'` |
| TA-11 | :268-270, :374 | C2 validation rests on ONE family; P15 finals rule overfits | FITS (claim) | W4/W6; not re-checked |
| TA-12 | :274-275, :360 | Wall-clock contaminated in slice 4 and Tier 3A | FITS | charges are the primary endpoint; wall-clock is marked |
| TA-13 | :280-281 | The conformance sweep missed an output-ceiling defect that S1 found | FITS, repaired | `E/basis_v4.py:168,172 abs(acc) > CEIL`; `E/conformance.py:23 CEIL = 10 ** 40` |
| TA-14 | :283-284, :351-352 | Novelty-ruler false positives (conjugates, abs junk); base rate 16% G4, 23-25% W5 | FITS | W3 REPORT :12-45; W7 :55-59 |
| TA-15 | :286 | Holm with a ledgered floor error | FITS (Campaign 0, not engine) | `roles/Aphrodite/calibration/LEDGER.md:21` floor 1/300 x 16 = 0.053 > 0.05 |
| TA-16 | :298-299 | Tier 3C: two shams solved the unseen families 16/16 while the donor did nothing | FITS (claim) | Review 10. Same pattern in S4: SHAM_7 solves 2 unseen families at about the DERIVED cost (TB-S4c) |
| TA-17 | :353-354 | Tier 3B: 4.688 FP per recipient (gcd-final small outputs) | FITS, repaired | Tier 3C generator qualification (`E/tier3c.py:136-146`) |
| TA-18 | :361 | W8 worker claimed a running PID that did not exist | DNF to the engine | provenance, not code |
| TA-19 | :365-366 | V5 (improver change) is untestable; BRSI NO is weak evidence | FITS | follows from TA-01 |
| TA-20 | :367-368 | Supply: tribunal and init {0,1} exclude non-additive tasks | FITS (claim) | K3/K6 |
| TA-21 | :369 | Derivation starvation: median 0 schemas per donor | FITS (claim) | W4 P-A |
| TA-22 | :370-371 | The 250k escrow sits at the minimum of a U-shaped window count | FITS | `E/fair.py:21 ESCROW = 250_000`; W2 REPORT :26-35 (window count 21/22/14/**2**/21/48 at 20k..4M), reproduces 141/141 |
| TA-23 | :375 | Small n (8-12); C2 p = 0.0625 | FITS | A19 4 vs 0 |
| TA-24 | :403-407 | Library carry-over swamps the improver effect (+29..+57 inherited vs +0..+12 selected) | FITS (claim) | `S/arc3/w4_improver_transplant/REPORT.md:49-51` |
| TA-25 | :109-110 | accel/ contains azure.env | FITS | `git ls-files` lists `E/accel/azure/azure.env` (not opened). Hygiene, not science |
| TA-26 | :463-464 | No cross-seat imports (not exhaustively grepped) | FITS | grep over `E/*.py` imports: stdlib plus local modules only |
| TA-27 | :511-512 | Open: would S4 survive non-constant 4/8; does T4 1.7% change A23 | FITS (open) | see TB-S4a, TB-T4b |

### A.2 TANTALUS_AUDIT (`docs/phase3/design/ASTRA-6.0/evidence/TANTALUS_AUDIT.md`)

| id | src line | claim | fit | reason |
|---|---|---|---|---|
| TU-01 | :139-140 (F07) | The mutable library is a search-order prior, not a mutable improvement procedure | FITS | = TA-01 |
| TU-02 | :141 (F07) | S4 conditions 4 and 8 are literal True. They encode trust, not fail-able checks. This alone does not prove leakage | FITS | = TA-03 |
| TU-03 | :142 (F07) | S4 weakened by the PC = derived schema; A23 used constructed recurrence | FITS | = TA-04, TA-10 |
| TU-04 | :215 (row 21) | v1 restricted loader, reset and metering need adversarial tests | FITS (open) | `E/tests/test_membrane.py` exists (12 tests per the dossier); no escape or adversarial test was confirmed |
| TU-05 | :216 (row 22) | G4/W5 = HISTORICAL CONTROL: fixed improver, grammar/tribunal coupling, asserted gates | FITS | = TA-01/03/09 |
| TU-06 | :217 (row 23) | C0 assay is author-generated; no independent calibration | FITS | Campaign 0 only |
| TU-07 | :249 (G02) | Gate liveness: each gate must fail for a demonstrated reason; constants do not count | FITS | applies to all GENUINE rows in the grep table |
| TU-08 | :259 (G11) | Mutable-process declaration: keep fixed-meta/library language, withhold Q6 | FITS | = TA-19 |

### A.3 FAILURE_TO_GATE_MAP (`docs/phase3/design/ASTRA-6.0/FAILURE_TO_GATE_MAP.md`)

| id | src line | claim (as applied to Aphrodite) | fit | reason |
|---|---|---|---|---|
| FG-03 | :60-65 | Controls and guards that cannot fail (constant PASS) | FITS | run_s3s4 :364(cond 1, forced), :391, :420; a16/a17/run_g2 R5 |
| FG-04 | :67-72 | Positive control absent or degenerate | FITS | S4 POSITIVE_CONTROL = treatment |
| FG-09 | :102-107 | Selection changes the measured population | FITS (new) | S4 S7 admission used the PC arm, which equals the treatment (TB-S4b) |
| FG-10 | :109-114 | Statistical defects inside the gate (multiplicity, attainable tests) | PART | Holm floor (C0, repaired); validation multiplicity is a design issue, not arithmetic |
| FG-11 | :8, :116-121 | A post-data repair loses confirmatory standing; repaired old-data analysis is correction only | FITS | governs how the T4 v1a and ruler v2.1 re-scores may be labelled |
| FG-12 | :123-128 | Unreachable design / structural zero | FITS | A20/A22 UNTESTABLE; window = 2% at 250k |
| FG-15 | :150-155 | Novelty must separate retrieval, equivalence and new mechanism | FITS | ruler v2 NEW = "differs from R", not "unreachable" (W3 F7) |

### A.4 Threads TH-018..021 and the merge packet

| id | src line | claim | fit | reason |
|---|---|---|---|---|
| TH18-1 | `ops/threads/TH-018.md:15-22` | A23 YES is mechanism-only, budget-relative and motif-recovering | FITS | A23 RESULT PRINCIPAL_ATTACK |
| TH19-1 | `TH-019.md:17-18` | Recurrence lands where PRISTINE cannot reach; 250k holds ~2% of families | FITS | = TA-22 |
| TH20-1 | `TH-020.md:15-18` | G3 has no extent in W5 (depth wall); the chain breaks at representation | FITS (claim) | `S/arc3/second_gen/` |
| TH21-1 | `TH-021.md:19-20` | Bimodality is an instrument effect; use a D-stratified endpoint (T53) | FITS | W2 |
| TH21-2 | `TH-021.md:21` | W5 chance-novelty base rate 23-25%; ruler v2.1 is drafted, not adopted | FITS | `S/arc3/w7_instrument_hygiene/ruler_v21.py` exists; no engine imports it |
| TH21-3 | `TH-021.md:22` | T4 v1a drafted; freeze with v2.1 plus a bridge (T47) | FITS | `S/arc3/w7_instrument_hygiene/tribunal_t4_v1a.py`; engine still imports `tribunal_t4` |
| TH21-4 | `TH-021.md:23-24` | 3 of 4 consecutive assays failed on design or supply | FITS | A20 UNTESTABLE, A21 INVALID, A22 UNTESTABLE |
| TH21-5 | `TH-021.md:25-31` | Constant-True gates (run_s3s4 L391/L420, a16:490); PC = derived (L245, L317) | FITS (a16 is :489) | = TA-03/04/05 |
| PK-1 | `review/ARC3_MERGE_REVIEW_PACKET.md:38-39` | Motif recovery; T52 validation dose-response | FITS | = TA-10 |
| PK-2 | `...PACKET.md:40` | Budget-relativity; T53 | FITS | = TA-22 |
| PK-3 | `...PACKET.md:41-42` | E-011 ran on the unrepaired T4; T47 bridge | FITS | = TA-06 |
| PK-4 | `...PACKET.md:43-44` | Worker isolation imperfect (shared filesystem; reports deposited by the principal) | FITS | WORKER_MANIFEST; provenance only |
| PK-5 | `...PACKET.md:69-72` | s5 defect table (4 rows) | FITS | line drift a16 490 -> 489 only |
| PK-6 | `...PACKET.md:74` | "None of these touches E-008..E-011; a18 imports a17 for utilities only" | FITS | the only hits for `donor_adjudication_valid`/`R5_clean` are in a16, a17 and run_g2; the A20 stage_report verdict is computed (`E/a20_c3.py:282-286`) |

### A.5 Harvest A1 defects (`roles/Aphrodite/harvest_2026-09-30/evidence/findings_A1_defects.md`)

| id | src line | claim | fit | reason |
|---|---|---|---|---|
| D27 | :46 | Slice-2 true solution (depth 4) not in the depth-3 space | FITS (historical) | AMENDMENT_3 |
| D28 | :47 | Hidden HELPER_CANDIDATE_CAP truncated the search space | FITS, repaired | `E/engine.py:428 HELPER_CANDIDATE_CAP = 1024  # effectively "all distinct helpers"` |
| D29 | :48 | SCRATCH control contained the organ | FITS, caught pre-run | A7 Add1 |
| D30 | :49 | PC witness failed the tribunal (value ceiling) | FITS, caught pre-run | A9 Add1 |
| D31 | :50 | Tier 3A SHAM arm contained a correct solution; control invalid | FITS (historical) | A10 |
| D32 | :51 | Tier 3B zero-FP guarantee failed on fresh draws | FITS, repaired | = TA-17 |
| D33 | :52 | RNG seeded with the library NAME; byte-identical libraries scored 13,479 vs 51,018 | FITS, repaired | `E/fair.py:147-152` cell entropy keyed by label/family/r, not library; "earlier result not re-scored" stays true |
| D51 | :70 | Novelty-ruler FPs (conjugate, abs junk) | FITS, repaired by v2 | = TA-14 |
| D53 | :72 | No task-domain supply screen; shams junk-prone (C1) | FITS, repaired | A19 supply repair; A22 pre-freeze screen |
| D54 | :73 | The motif rule admitted inert wraps (C3R INVALID) | FITS, repaired | `E/a22_c3r2.py:9-10` genuine motifs, "not inert" |
| D55 | :74 | Constant-True gates plus PC = donor schema | FITS | = TA-03/04/05 |
| HV-C1 | :188 | "Gate unreachable/constant/vacuous" is the most frequent class; Aphrodite shipped constants in A14 code a day after catching D30 | FITS | new constants found below (R5_clean_transplant, cond 1) extend it |
| HV-C3 | :190 | RNG/pairing rule is seat-local; no fleet rule | FITS | D33 |

---------------------------------------------------------------------------------------------------------------------
## TASK B -- Triage table

Classes: CD = CONFIRMED_DEFECT, AR = ALREADY_REPAIRED, NA = NOT_APPLICABLE, ND = NEEDS_DISCRIMINATOR,
SL = SCIENTIFIC_LIMITATION, OP = OPEN.

| tid | finding (Task A ids) | class | evidence (code location / reproduction) | results affected; interpretation change? |
|---|---|---|---|---|
| TB-S4a | S4 conditions 4 and 8 constant True (TA-03, TU-02, TH21-5, D55) | CD | `E/run_s3s4.py:391`, `:420`. AMENDMENT_14:149 and :154 preregister condition 8 as checked by "membrane receipts", and the code reads no receipt | S4 ABSTRACTION_TRANSPLANT = YES (S4_RESULTS, `failed []`). Label unchanged: 2 of 8 conjuncts were vacuous, so S4 is effectively a 6-condition verdict. Condition 4 is enforced structurally (summarise counts only `qualified` rows), so it is a duplicate rather than a gap. Condition 8 is an untested membrane assumption. Interpretation: "YES with 6 live conditions; no-donor-state asserted, not checked". |
| TB-S4b | S4 POSITIVE_CONTROL = derived treatment (TA-04, FG-04), plus **new: the PC arm drove S7 family admission** (FG-09) | CD | `E/run_s3s4.py:317` (PC arm), `:333 ctrl = [a for a in arms if a not in ("DERIVED", "MEMORISE")]  # S7: DERIVED excluded`, `:339 "SOLVABLE": max(best.values()) >= 8`. S4_RESULTS difficulty_pilot: in 3 of the 5 unseen-body families (`sumgcdlast_minus_first`, `summod_times_first`, `sumscaled_minus_last`) PC = 16 and every other control is <= 1, so they were admitted only because the treatment-equivalent PC solved them. The "DERIVED excluded" safeguard is bypassed | S4: the PC never discriminated (efforts identical, 7/7 families), and the unseen-body n is inflated from 2 to 5 by treatment-selected admission. Re-computed from S4_RESULTS without those 3 families: 4 families remain (2 unseen + 2 rel), and all have effect = True, beats_every_sham = True and novel. So conditions 3/6/7 still hold and the **label survives**. Interpretation: the "5 unseen-body families" breadth claim shrinks to 2, and no independent positive control exists for S4. |
| TB-S4c | S4 sham proximity (TA-16, new detail) | SL | S4_RESULTS: SHAM_7 on `negmod` 34294.3 vs DERIVED 34180.3 (both 16/16); on `sumdiv` 32688.1 vs 29189.6 | "beats_every_sham" holds by a margin of 114 charges (0.3%) in one family. Not a defect, but S4 discrimination from shams is thin in exactly the 2 families that survive TB-S4b. |
| TB-S4d | S4 condition 1 cannot be False (new; grep) | CD (low) | `E/run_s3s4.py:364 c["1_expressive_equivalence"] = all(l.desugars()[0] ...)`. This is unreachable as False because `:323-325` raise `SystemExit("STOP: an arm does not desugar ...")` first | S4: no change. A failure would stop the run rather than produce NO, so it is a precondition, not a condition. Relabel it as a precondition. |
| TB-A16 | a16/a17 `donor_adjudication_valid = True` (TA-05, PK-5) | CD (cosmetic) | `E/a16.py:489`, `E/a17.py:581`. The field is only written, never read by a verdict | A16/A17: NO / UNTESTABLE (A17_E1 `BOUNDED_RSI NO`, E2 `UNTESTABLE`). No change; the constant is a misleading label in the result JSON. |
| TB-R5 | **New:** `R5_clean_transplant: True` is constant inside the BOUNDED_RSI conjunction | CD | `E/a16.py:547`, `E/a17.py:639` `"R5_clean_transplant": True}`, `E/run_g2.py:395 c["R5_clean_transplant"] = True`. All enter `"BOUNDED_RSI": "YES" if all(c.values())` | A16/A17/G2: no positive exists (A17 NO/UNTESTABLE; G2 `STOP: catalog cannot support the assay`), so no interpretation change. The constant would have been a hole in any YES. The packet and TH-021 do not record it. |
| TB-EXP | `g4_subset_of_organ: True` asserted (new; grep) | CD (low) | `E/certify_expressivity.py:61` asserts it by argument (the "falls back to full G4" note); `EQUIVALENT` checks only one direction (`mismatches == 0`) | EXPRESSIVITY_CERTIFICATE: probably true by construction, but the certificate does not test the claim. Low risk. |
| TB-T4a | T4 query window 1/2 vs dev 3..97 (TA-06, TH21-3, PK-3) | CD | `E/tribunal_t4.py:279` ce-battery queries `r.choice([1, 2, r.randint(3, 97)])` vs dev `E/a17.py:82 rng.randint(3, 97)`. Reproduced by W7: 11/644 families (1.7%), 31/2,721 programs. The v1 re-score matches frozen T4 648/648 (`S/arc3/w7_instrument_hygiene/REPORT.md:13-31, 94-103`) | A19 (C2) and A20 (C3): 3 frozen pilot p values flip (qbda, qoja, cgfa: p 0 -> 1). 12/13 PRISTINE spurious first hits at 250k are query-1/2 artifacts. A19's NO and A20's UNTESTABLE are not reported as changed by W7; fix (a) also reshuffles all 12 C2 role assignments, so a re-score is correction-only (FG-11). |
| TB-T4b | Does the T4 mismatch change A23 (E-011)? (TA-27, PK-3) | ND | W7 scored only C2/C3 rows. A23 imports `tribunal_t4` (`E/a23_c3r2c.py:92,132 T4.family_profile(p)["admissible"]`) | **Cheapest probe:** run W7's `tribunal_t4_v1a.direct_score()` (validated 60/60 against the real tribunals) on A23's foundry/role families and transfer witnesses, and count admission flips. If there are 0 flips in A23 VALIDATE/T_SAME/T_OTHER, A23 stands on T4 v1 unchanged; otherwise do the T47 bridge re-score. |
| TB-RV1 | Ruler v2 `relations()` matches the literal reference only, with no re-expression closure (TA-14, W3 F1/F2) | CD | `S/compounding/rb1/ruler_v2.py:253-270`: `_match(g, s, b)` on `_term(ref_schema)` only. The fix is drafted in `ruler_v21.py:7, :152-156` (`OR over r in reexpressions(G)`) and NOT adopted. a20_c3 patches it at the call site (`E/a20_c3.py:69-70 for ref in R.reexpressions(a18.G1): rel = R.relations(s, ref)`). A19 panel building uses raw `R.verdict_full` (`E/a19_c2.py:66`) | A19 (C2): under closure SHAM_0 = (v - (acc - {H})) COMPOSES G1, so the C2 sham panel holds a G1-relative (W3 F2), and G1 NOVELTY becomes 3/8, not 2/8 (W7 :55-59). A19 stays NO. The interpretation of the C2 "shams pass too" weakens, because SHAM_0 is not clean. A22/A23 use only EQUAL/reexpressions panel checks (`E/a23_c3r2c.py:65-66`), so they are unaffected. |
| TB-RV2 | Ruler GRID assumes acc >= 0 (W3 F5) | CD (low) | `S/compounding/rb1/ruler_v2.py:41 ACCS = (0, 1, 2, ...)`, `:46 GRID`. 18% of random W5 instances reach acc < 0 | `accumulating()` and NEW verdicts can be wrong off-grid. W3 found 0 random-schema cases, so no known result changes. |
| TB-RV3 | NEW means "differs from R", so efficiency-only schemas count as NEW; chance base rate 23-25% W5, 10-16% G4 (TA-14, FG-15, W3 F7) | SL | W3 REPORT :37-45; W7 :55-58 | Every novelty count (A16-A20) carries a 1-in-4 chance floor in W5. The interpretation needs to be relative to the floor, not to 0. |
| TB-RV4 | Original tier3e novelty key: conjugate/abs FPs, 574 removed (TA-14, D51) | AR | ruler v2 (rb1) | Pre-v2 novelty claims (Tier 3E/A15-A17 R1) were already demoted by the seat. |
| TB-ESC | Escrow 250k x init-major walk cliff makes solve probability bimodal; capability ratios are cliff ratios (TA-22, TH19-1, TH21-1, PK-2) | CD (instrument) | `E/fair.py:21 ESCROW = 250_000`; the fallback is init-major (83.9M charges per init block). W2 reproduces frozen p_PRISTINE 141/141, window count at 250k = 2 vs 21-48 elsewhere (`S/arc3/w2_learnability/REPORT.md:10-35`) | A19 CON1 ">=190x" and A23 capability ">= 345x" (A23 PRINCIPAL_ATTACK) are generic walk-cliff ratios, not G1-specific. A23's REUSED and sign tests are unaffected; CAPABILITY_SAME is budget-relative. The interpretation changes from "capability expansion" to "reordering across the cliff". |
| TB-ESC2 | Is any A23 capability left after D-stratification? | ND | — | **Cheapest probe:** T53 (`S/compounding/BACKLOG_COMPOUNDING.md:547`): re-score the existing A23 transfer rows stratified by the W2 log10 first-equivalent charge D. This needs no new search, only W2's `w2_fallback` D values for each A23 transfer family. |
| TB-VAL | A22/A23 VALIDATE = 2 instances of the planted motif; selection then returns the motif in 7/8 cases (TA-10, PK-1, TH18-1) | ND | `E/a22_c3r2.py:11`; A23 RESULT motif_recovery: G1 7/8 literal, shams 5-7 literal / 9-10 extensional | A23 G1_RECURRENT_STEPPING_STONE YES stands as recorded and is preregistered (AMENDMENT 22/23), so it is not a defect. The open question is selection-from-evidence versus planted recovery. **Cheapest probe:** T52 dose-response (`BACKLOG_COMPOUNDING.md:543`). Re-run only the donor SELECT stage at VALIDATE = 0/1/2/3 motif instances on the A23 panel and seeds; the transfer stage is unchanged. If motif selection at 0-1 instances is near chance (about 1/60), A23 measures planted recovery. |
| TB-VAL2 | C2 validation rests on one cross-group family (TA-11, TA-23) | SL | W6; A19 4 vs 0, p = 0.0625 | A19 NO is underpowered (n = 8), not a bounded negative (FG-10). |
| TB-ADM | Admission ruler = G1's own span (TA-09, TA-20, TU-05) | SL | frontier s4, K1 census (7/10,500 non-G1). Consistent with S4: PRISTINE solves only the 2 `tc_rel_*` families | S4/Tier 3 "transfer" is transfer within the class the tribunal admits. The narrow interpretation is already the seat's own. |
| TB-IMM | Improver immutable; V5 untestable; "RSI" = library inheritance (TA-01, TA-19, TU-01, TU-08) | SL | improver.py docstring | All BOUNDED_RSI labels: NO is a near-theorem of the setup, not evidence about recursion. Already the seat's position. |
| TB-STARV | Derivation starvation (median 0 schemas); inherited carry-over swamps selection (TA-21, TA-24) | SL | W4 P-A, P-C | Any lever result downstream of donors (RB-6 "levers inert") cannot be interpreted. A Beta-01 design constraint. |
| TB-DEPTH | Depth wall: G3 has no extent in W5 (TH20-1) | SL | `S/arc3/second_gen/` | Second-order compounding untestable in W5. |
| TB-SUP | Supply/design failure rate 3 of 4 (TH21-4, D53, D54) | AR | A22 pre-freeze supply screen (`E/a22_c3r2.py:3-8`); worked in A23 | A20 UNTESTABLE, A21 INVALID, A22 UNTESTABLE stay as recorded. |
| TB-CRN | RNG keyed by library name (D33) | AR | `E/fair.py:147-152` | Pre-A13 S2 result not re-scored (historical). |
| TB-CAP | Hidden helper cap (D28) | AR | `E/engine.py:428` | slice 2 only |
| TB-CEIL | Output ceiling missed by conformance (TA-13) | AR | `E/basis_v4.py:168,172`; `E/conformance.py:23` | S1 runs 1-3 FAIL stand |
| TB-3B | Tier 3B FP 4.688 per recipient (TA-17, D32) | AR | Tier 3C generator qualification | Tier 3B label stands as recorded |
| TB-CLONE | v1 lineage clones (TA-02) | AR | `E/engine.py:56` | slice 2B pseudoreplication recorded (SCAR) |
| TB-WALL | Wall-clock contamination (TA-12) | AR | charges primary | slice 4 / Tier 3A wall-clock only |
| TB-HOLM | Holm floor 0.053 > 0.05 (TA-15) | AR | `calibration/LEDGER.md:21`; `S/campaign0/sensitivity_boot_v2.py` | Campaign 0 only; NA to the engine |
| TB-MEMB | v1 membrane loader needs adversarial tests (TU-04); condition 8 rests on it | OP | `E/tests/test_membrane.py` (no escape test confirmed) | Matters only if Beta-01 relies on condition 8-style "no donor state". Folds into repair R2. |
| TB-E2 | E2 gate barely reachable (TA-07) | NA | Tier-1 toy | not the engine |
| TB-NUM | numtheory shortcut (TA-08) | AR | per-class test | engine v1 only |
| TB-ISO | Worker isolation / stale PID (PK-4, TA-18) | NA | provenance | none |
| TB-ENV | `E/accel/azure/azure.env` tracked (TA-25) | NA (to science); flag | `git ls-files` | Hygiene: someone with rights should check whether it holds secrets. Not opened. |
| TB-C0 | C0 assay author-generated (TU-06) | NA | Campaign 0 | not in Beta-01 scope |

---------------------------------------------------------------------------------------------------------------------
## Constant-gate grep table

Scope: `E/**/*.py` (including accel/ and the A19-A23 subdirectories, which have no .py hits) and `S/**/*.py`, excluding
tests/. Patterns:
- `<valid|gate|cond|ok|pass|PASS...> = True`
- `["...valid|ok|hostile|no_|clean|pass..."] = True`
- dict `"...": True`
- `if True`
- `or True`
- `>= 0` tautologies

`mkdir(exist_ok=True)`-style keyword arguments are omitted. "Cannot-be-False" cases were found by reading the context.

| path:line | text | verdict | note |
|---|---|---|---|
| E/run_s3s4.py:391 | `c["4_hostile_evaluation"] = True` | GENUINE_CONSTANT_GATE | in the S4 conjunction; structurally duplicated by `qualified` filtering |
| E/run_s3s4.py:420 | `c["8_no_donor_state"] = True` | GENUINE_CONSTANT_GATE | in the S4 conjunction; the prereg asked for membrane receipts |
| E/run_s3s4.py:364 | `c["1_expressive_equivalence"] = all(l.desugars()[0] ...)` | GENUINE_CONSTANT_GATE (cannot be False) | `:323-325` SystemExit first |
| E/a16.py:489 | `out["donor_adjudication_valid"] = True` | GENUINE_CONSTANT_GATE (label only) | never read by a verdict |
| E/a17.py:581 | same | GENUINE_CONSTANT_GATE (label only) | copied from a16 |
| E/a16.py:547 | `"R5_clean_transplant": True}` | GENUINE_CONSTANT_GATE | in the `BOUNDED_RSI` all() conjunction; not previously recorded |
| E/a17.py:639 | same | GENUINE_CONSTANT_GATE | not previously recorded |
| E/run_g2.py:395 | `c["R5_clean_transplant"] = True` | GENUINE_CONSTANT_GATE | not previously recorded |
| E/certify_expressivity.py:61 | `"g4_subset_of_organ": True,` | GENUINE_CONSTANT_GATE (asserted by construction, low) | EQUIVALENT tests one direction only |
| E/organ_extract.py:154 | `"unique_without_human_choice": True,` | GENUINE_CONSTANT_GATE (asserted claim, low) | an asserted property in the organ certificate; not a run verdict |
| E/s2_gate.py:123 | `"PASS": True}` (G-S2.5) | FALSE_ALARM | excluded from the S2 gate list (`:141-144`); prereg A13:81 "reported, not thresholded" |
| E/run_s3s4.py:196 | `"certified": True` | FALSE_ALARM | inside the certificate-split branch; describes the sub-bucket |
| E/a16.py:495, E/a17.py:587 (`R1_failure_is_novelty = True`) | — | FALSE_ALARM | label on the failure path |
| E/a18_c1.py:23 | `COMPOSE = {"G1": True, ...}` | FALSE_ALARM | arm configuration |
| E/tier3c.py:144, E/tier3d.py:119, E/tier3e.py:173, E/accel/fasteval.py:304 | `"QUALIFIED": True` | FALSE_ALARM | returned only inside `if upper < THRESHOLD`; the else branch returns False |
| E/a16.py:293, a17.py:385, a18.py:280, a18.py:320, accel/fasteval.py:138/183/223, basis_v2.py:190, basis_v3.py:114, basis_v4.py:257, fair.py:129, improver.py:139, run_g2.py:96, run_tier3b.py:54, run_tier3c.py:86, tier3d.py:138 | `ok = True` | FALSE_ALARM | loop accumulator, set False on the first mismatch |
| E/a18_c1.py:158 | `ok = True` then `ok &= take(...)` | FALSE_ALARM | accumulated |
| S/arc3/w2_learnability/w2_coverage.py:62, S/arc3/w6_c2_rivals/w6_common.py:76, S/compounding/rb2/rb2_common.py:351 | `ok = True` | FALSE_ALARM | loop accumulator |
| S/campaign0/summarize_c0b.py:24 | `passed = True` | FALSE_ALARM | `&=` at :42, :44 |
| S/benchmark/bench.py:167 | `"ok_call": True` | FALSE_ALARM | success-path record |
| S/compounding/rb1/ruler_v2.py:180, :331; S/arc3/second_gen/pkg5_promoted.py:38 | `len(novel) >= 0.10 * max(1, ...)` | FALSE_ALARM | computed threshold |
| S/campaign0/sensitivity_boot_v2.py:38 | `(reps >= 0).mean()` | FALSE_ALARM | bootstrap tail |
| (none) | `if True` / `or True` | — | 0 hits |

A20-A23 verdicts: `E/a20_c3.py:282-286` `verdict()` is computed (n >= 8, REUSED_SAME >= 5, CAPABILITY_SAME >= 5, sign
tests). No constant was found on the E-008..E-011 path.

---------------------------------------------------------------------------------------------------------------------
## Prioritised repair list for the Beta-01 bootstrap (DEV-1)

These are proposals only. Under FG-11, any re-score of old data is CORRECTION-ONLY and never a new confirmation.

1. **R1 Gate liveness harness (FG-03/G02).** Replace every GENUINE_CONSTANT_GATE with a computed predicate or rename it
   as a precondition or assumption that is outside the conjunction:
   - `run_s3s4.py:364/391/420`;
   - `a16.py:489/547`, `a17.py:581/639`, `run_g2.py:395`;
   - `certify_expressivity.py:61`.

   Add a mutation test that flips each required invariant and asserts the verdict changes. Beta-01's own verdict code
   should get the grep above as a CI check.
2. **R2 A real condition-8 / no-donor-state check.** Hash the recipient loader namespace and the artifact bytes at
   transplant and assert that no donor-run state (escrow, caches, RNG) is reachable. This closes TB-S4a and TB-MEMB.
   Without it, "no donor state" remains an assumption.
3. **R3 An independent positive control and treatment-blind admission (TB-S4b, FG-04/FG-09).**
   - The PC must be a schema that differs from any candidate treatment, ideally with a planted delta.
   - Family admission (S7-style) must exclude every arm that is byte- or instantiation-equal to the treatment. Assert
     `set(instantiate(PC)) != set(instantiate(DERIVED))` before running.
   - A correction-only S4 note: the label survives on 2 unseen + 2 rel families. Report that number.
4. **R4 Freeze T4 v1a (query 3..97 in the ce battery, `tribunal_t4.py:279`) as a versioned instrument, plus a bridge.**
   - First run the TB-T4b probe (`direct_score` v1a on the A23 families). That is cheap and decides whether A23 needs
     the T47 bridge.
   - Use fix (a), not fix (b): W7 shows (b) re-draws every dev set and fails on qbda.
5. **R5 Adopt ruler v2.1 (closure of relations over re-expressions).**
   - Remove the call-site patch divergence (a19 raw vs a20 patched).
   - Report all novelty counts against the W5 chance floor (23-25%).
   - Correction note for C2: SHAM_0 is G1-relative; novelty is 3/8.
6. **R6 Budget-free capability endpoint (TB-ESC/ESC2).**
   - Report capability D-stratified (T53) on existing A23 rows.
   - Never score at 250k alone: either use an escrow ladder (20k..4M), or move the escrow off the window-count minimum.
7. **R7 Validation dose-response (TB-VAL).** T52: SELECT-stage-only re-runs at VALIDATE = 0/1/2/3 motif instances. This
   gives A23's selection claim a chance baseline (about 1/60).
8. **R8 TEST-1 known-answer assay.** It must include the following:
   - a planted positive that is not the treatment;
   - a null where the gate must return NO;
   - a broken-gate twin from R1, so the apparatus is shown to fail before any science.
9. Low priority:
   - check whether `E/accel/azure/azure.env` contains secrets (owner action);
   - relabel `donor_adjudication_valid` as asserted in the A16/A17 JSONs (note only; no label change).

Historical labels: none flips under the evidence gathered here.
- S4 YES survives the recomputation without PC-admitted families.
- A16/A17/G2 have no positive that rests on R5.
- A19 NO and A20-A22 are unchanged by W7.
- A23 YES is pending TB-T4b (cheap) and TB-VAL/T53 (interpretation, not label).
