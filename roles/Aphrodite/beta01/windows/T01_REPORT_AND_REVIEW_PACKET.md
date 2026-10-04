# T01 -- KNOWN-ANSWER APPARATUS ASSAY: REPORT + EXTERNAL-REVIEW PACKET

C-006 (C-P2B-APH-BETA-01), cycle 1, TEST window 1. Thread TH-P2B-APHRODITE-V2B (active sub-thread TH-021).
Evidence tier 2 (apparatus calibration). It is NOT evidence about any mechanism, and NOT evidence about real models.

## 1. Question and rung
Can the repaired v2b pipeline return PASS, NO, NOT_A_SHAM, REPRESENTATION_LIMITED, INVALID_DESIGN, SUPPLY_LIMITED,
and an instrument-version difference, each for the declared reason, on cases with answers known by construction?

Rungs exercised:
- R0 (representable);
- R2/R4 (findable, solved within the cap);
- R6 (causal knockout: the sibling composition);
- the measurement layer (tribunal, ruler, D endpoint, gates, supply).

## 2. Frozen identities
- Spec: beta01/windows/T01_KNOWN_ANSWER_SPEC.md (frozen in DEV-1, committed in 7620143dd before any T01 walk).
- Runner: engine/v2b/t1_known_answer.py, sha256 e5853caf... (unchanged since freeze).
- Plan: beta01/runs/T01/T01_PLAN.json, sha256 f698991a... (the supply screen ran pre-freeze).
- Apparatus v2b-1. Tribunal T4 v1a, ruler v2.1, world W5, cap 2,000,000, 4 cells per family.

## 3. Supply and world
| Item | Value |
|---|---|
| Motif M | (v * (acc + {H})), a G1 composition chosen in seeded order |
| Transfer families (4) | toaa (v*(acc+(last-1))), tcnb (v*(acc+(v+v))), tvzc (v*(acc+(1+1))), twme (v*(acc+(first+first))) |
| Supply screen | 32 candidates screened. 4 DEEP_OK (T4-admissible and PRISTINE-censored at 2M on cell 0), 6 PRISTINE_SOLVES, 22 T4_INADMISSIBLE |
| Inherited entries | 161 instantiations each (equal expressivity across T, SIBLING, SHAM_X, SHAM_EQ, NULL) |
| Distinctness (ruler v2.1, computed) | SIBLING / SHAM_X / NULL DISTINCT; SHAM_EQ NOT_DISTINCT |

## 4. Execution receipts
- 120 exact walks, 3 local workers on M4, about 2 min of wall time. 0 technical failures, 0 evaluator disagreements.
- Every DIRECT-positive was confirmed through the emitted-artifact tribunal path.
- Files: beta01/runs/T01/T01_WALKS.jsonl, T01_RESULT.json; log beta01/runs/T01_run.log.
- Full-size conformance: engine/v2b/receipts/CONFORMANCE_V2B_2026-10-04.json = **GREEN**:
  - walker == fast_cost, 200/200;
  - fast_cost == reference, 200/200;
  - artifact == direct, 48/48 under v1 and under v1a;
  - ruler v2.1 == W7, 47/47;
  - v2b lint-clean.
  It took 373 s.

## 5. Results

| Case | Expected | Got | Reason held | Detail |
|---|---|---|---|---|
| K1 planted abstraction | PASS | PASS | yes | T solved 4/4 families (16/16 cells). CENSORED-stratum excess over the best control = 16 cells (threshold 6). Median delta D = 2.09 decades |
| K1b knockout (sibling composition) | NO | NO | yes | 0 families; censored 16/16 |
| K2 null (OFF_0) | NO | NO | yes | 0 |
| K3a equal-expressivity sham | NO | NO | yes (DISTINCT) | 0 |
| K3b re-expression | NOT_A_SHAM | NOT_A_SHAM | yes | ruler refused it as a sham. It solved 16/16, identical to T (as expected for an extensional equal) |
| K4 memorisation cheat | NO | NO | yes | literal sibling programs: 0 |
| K5 unrepresentable probe | REPRESENTATION_LIMITED | same | yes | not in W5, not in any library |
| K6 constant-gate design | INVALID_DESIGN | same | yes | GateUnreachable at qualify |
| K7 supply shortfall | SUPPLY_LIMITED | same | yes | 4/6 fillable |
| K8 tribunal version (qbda) | V1_BLIND_V1A_SOLVES | same | yes | v1: 0/4 cells, 32 spurious hits walked past. v1a: 4/4 cells (charges 26k-138k, COVERED stratum) |

**Technical disposition: CLEAN. Scientific (apparatus) disposition: QUALIFIED.**

## 6. What this does and does not show
**Shows:**
- the D endpoint distinguishes a planted abstraction from its sibling, from a size-matched sham, from a null and from
  literal memory;
- the ruler refuses a re-expression as a sham (the CON1/SHAM_0 confound class);
- a representation limit is reported as such, not as NO;
- constant gates cannot be sealed;
- supply shortfalls close as SUPPLY_LIMITED;
- the tribunal repair changes outcomes exactly where W7 predicted.

**Does not show (known limits, to be addressed in the battery's next version):**
1. **Every positive here is all-or-nothing** (16/16 vs 0/16). The assay does not test SENSITIVITY to graded or partial
   effects (an entry covering only some instances, or an equivalent placed late in the entry). The planned battery
   extension is to add graded known-answer cases at 25/50/75% coverage.
2. One motif, one seed, one cap (2M). There is no replication across motifs.
3. The tribunal case is a single family (qbda).
4. "No donor state" (S4 condition-8 class) is still not receipt-checked (TRIAGE R2). TEST-1 did not exercise
   transplant/reset.
5. Selection (R3) was not exercised: libraries were planted, not selected. Selection known-answers are needed before
   T52.
6. Reporting defect (minor, non-verdict): the K1 detail field `pristine_all_censored` mixes in the qbda PRISTINE walks
   and reads false. The verdict uses the CENSORED-stratum excess, which is correct (PRISTINE censored 16/16 on the
   transfer families). It will be fixed in DEV-2 with a test.

## 7. Alternative explanations considered
- **T passes because the entry is simply first in walk order.** True by construction. That IS the planted mechanism,
  and the sibling/sham/null entries are also first in order and fail. The comparison is order-matched.
- **Tribunal leakage (T accepted because the tribunal is lenient).** Checked in DEV-1 smoke: a non-syntactic
  qualified program agreed with the witness on 500/500 random inputs. Artifact and DIRECT agree. THRESH = 0.99.
- **Memorisation passing by luck.** It did not pass; and it would have been caught only if siblings shared
  init/final. They share init/final by construction (worst case for the cheat), so memory was given its best chance.

## 8. Replay
```
cd roles/Aphrodite/engine/v2b
python t1_known_answer.py plan    # deterministic; must reproduce T01_PLAN.json byte-for-byte modulo the apparatus timestamp-free hash
python t1_known_answer.py run 3
python t1_known_answer.py report
```

## 9. External-review attack questions
1. Is the D endpoint's CENSORED stratum too easy a place to show capability? Every family here is PRISTINE-censored
   at 2M by selection. Would a WINDOW-stratum known-answer behave as cleanly?
2. Do the controls share a structure with T that makes their failure guaranteed rather than informative? (SIBLING and
   SHAM_X are both G1 compositions with 161 instantiations; NULL is OFF_0.)
3. Is K3b's NOT_A_SHAM rule too strong? It would also refuse a sham that is extensionally equal on the training domain
   but differs off-domain, which is exactly the case that matters.
4. The supply screen admitted 4 of 32 candidates. Is "deep and admissible" a biased subset? For example, are deep
   families those whose witnesses the tribunal happens to profile strictly?
5. Can any v2b instrument be gamed by a treatment that knows the cap (2M)?
6. What known-answer case would show that the apparatus FAILS where it should (sensitivity), not just that it
   separates extremes?

Shared-filesystem disclosure: the DEV-1 triage worker and the earlier W2/W7 workers had repository access. No
independent replication of T01 exists yet.
