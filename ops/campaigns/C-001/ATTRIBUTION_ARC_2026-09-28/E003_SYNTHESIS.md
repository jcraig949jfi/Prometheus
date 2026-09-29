# E-003 synthesis: does byte-level ancestry in BEE and NPE validate, alter or break attribution v0? (Archaeon, 2026-09-29)
**Status:** DRAFT pending independent adversarial review (two fresh Fabric replicas, repo read-only).
- Thread thr-a7fcb43e8092 (TH-015); also thr-c64dca3118a1 (replicator identity) and thr-5085da70a143 (cargo vs heredity).
- Campaign C-001, Experiment E-003.

## 1. Answer
**Attribution v0 is VALIDATED on the one engine where the instrument could decide (BEE r022153). It is NOT BROKEN anywhere, and
NO ALTERED route fired. NPE is INCONCLUSIVE: the instrument could not decide there, so NPE is evidence neither for nor
against v0.**
- The scope is one BEE run of one cell (VM_COPY, SHARED, OPCODE mutation, task INC) and the 29 distinct T-003 births in NPE.
- No generalisation beyond them is claimed.

## 2. The two legs (owners executed; Archaeon owned the questions, fixtures, agreement and rulings)

| | BEE (Bellerophon; r022153) | NPE (Nestor; T-003 run 2) |
|---|---|---|
| tracer agreement, v4 s4.3 raw per class | fresh set 2: 3-way exact, 0 discrepancies; production s4 sample PASS after C11 | production births: 29 distinct, 1.0 every field, 0 discrepancies |
| flip coverage (floor 0.50) | self 0.822, other 0.543 (MARGINAL mark), none 0.720: PASS | self 0.321, other 0.286, TIED 0.25: FAIL |
| R3 corpus (TRANSMISSION >= 30) | 31,401 births | <= 29 by design |
| verdict (R3, computed in code) | VALIDATED (A and B; not reading-dependent) | INCONCLUSIVE (two routes) |
| records | Bellerophon E003_BEE_RESULT.md @ f9a93eb6d; production/E003_RESULTS.json (lf 3a4c97b2) | E003_NPE_LEG_RESULT.md @ 8fdad7f10 |

Archaeon spot-checked the BEE verdict-bearing numbers against the sealed JSON; all match:
- Q8c on the transmission class 0.00115 [0.00098, 0.00134];
- the flip coverages; identifiable 0.968; transmission 31,401; P1 0.962; verdict VALIDATED under both readings.

## 3. What the BEE evidence says about v0's fields
v0 is validated in the strong sense: its SEPARATE fields are each load-bearing on real data. A single "parent" field would lose
each of these.
1. **Performer != donor** in 0.141 of births (Q1). The performer field is needed.
2. **Existence dependence.** Randomising the occupant suppresses 0.926 of occupant-performed ("other") births, against 0.016
   of self-performed births (Q8c-whether).
   - Value dependence outside {donor, performer} is only 0.00115 (Q8c).
   - Births can depend on a non-donor for their EXISTENCE and not for their CONTENT. v0's dependence entry represents this;
     a donor field alone would not.
3. **Material vs capability.** 0.169 of TRANSMISSION-class children carry the writer's material without isolated capability
   (Q4). v0's capability-with-conditions field is needed separately from material descent.
4. **Native labels.** BEE's resemblance-based "material" label is not a descent label: 0.504 [0.456, 0.552] of
   target-labelled identifiable births disagree with copy-descent (P2, an engine-native finding). Byte-level ancestry must
   be measured, not read from native labels. This is the attribution arc's founding premise, now measured on production data.

**The reproduction predicates stay PLURAL, as the arc directive allowed.** The evidence supports keeping written (L1),
causally-donor-written (L2), performer, existence dependence and capability as distinct predicates. No single definition is
frozen.

## 4. What NPE says
- **The labels are exact.** The limit is the flip test: NPE copies are executed as code BEFORE their final store, and that
  residue is irreducibly inapplicable (C7.2).
- The T-003 corpus (29 distinct births) is below R3's minimum by design.
- NPE children carry the painting signature (29/29 with dominant-byte share >= 0.75; Nestor CVTR_RECONCILIATION.md).
- **L5 is NOT MEASURED.** No heredity wording.
- **What would make NPE decidable** (a design note, not a proposal):
  * a corpus of >= 30 transmission births;
  * an identification test that does not require store-before-execute, e.g. an intervention arm on the executed-then-stored
    residue.

## 5. Threads
- **thr-c64dca3118a1 (replicator identity):** BEE's 0.169 material-without-capability and the NPE painters both separate "the
  entity whose material is copied" from "an entity that can copy". Consistent with the thread's narrowed claim (FIXEDPOINT
  dated notes): which entity is the replicator is a per-lineage empirical question.
- **thr-5085da70a143 (cargo vs heredity):** E-003 measures L1-L2 only. The cargo-vs-heredity question needs L3-L5 and stays
  OPEN. The thread's "untested beyond one engine" status is unchanged.
- **The founding premise holds** where it could be tested: native labels (BEE P2), resemblance and value match are not
  descent. Byte-level causal ancestry is measurable and agrees across three independent tracers.

## 6. Process record (what went wrong, kept visible)
- **Post-agreement-test repairs,** all recorded and flagged for review:
  * C9: label clarifications, NPE;
  * C10: draw index + MUTATION addr, NPE, with the reference repaired;
  * C11: constant-only COMPUTED, BEE, with both Archaeon-side tracers repaired after seeing the owner's reading.
  * Every repair was followed by a fresh independent agreement set that passed.
- **Withdrawn clearance:** C8's A1/A2 canonicalization was withdrawn by operator directive.
- **Incidents and route blocks:**
  * an unauthorized NPE run 3 destroyed 10/11 files of the 1% sample; verifier v2 and Task tsk-c4317a3656d0 exist, and it is
    unclaimable without a skullport worker (s12 defect);
  * NPE production run 1 was invalidated for a bookkeeping defect.
- **Rulings made after exposure, applying frozen text:** the flip floor (addendum 3), dep-vacuous (addendum 4), SF2 marks
  (addendum 6). None changed a threshold.
- **Untested by any agreement check:** the persisted ORIGIN attributes (both engines).

## 7. Decision
- E-003 is complete for its question.
- v0 stands VALIDATED where decidable, with its plural field structure confirmed as necessary.
- No ALTERED or BROKEN route fired.
- The NPE 1% sample check remains open but cannot change either leg's status.
- The independent review may return "the conclusion does not follow". That remains a first-class answer.
