# D15-B DESIGN AMENDMENTS R2 (B13 review verdict, 2026-09-02)

Amends `D15B_DESIGN_PACKET.md` (`18c991cc4`) and `D15B_AMENDMENTS_R1.md`
(`164562d98`). **No falsifier relaxed; every amendment tightens.** Design
identity becomes the triple (packet sha, R1 sha, R2 sha), journaled at issuance.

**Standing instructions adopted, and binding now:**
- **No informal repro is sent to Harmonia A at this stage.**
- **A's frozen Phase-0 record is not modified.**
- Let the evidence create the message if there is a real disagreement.

---

## B14 -- X-14 REQUIRED STRUCTURE: POSITIVE CONTROLS BEFORE ADVERSARIAL CLAIMS

X-14 may not return PASS unless it has **first observed, from fresh isolated test
worlds**, at least one genuine `CLAIM_SURVIVED` transition **and** at least one
genuine `CLAIM_FALSIFIED` transition, each produced through the **intended
prospective experiment path**. Only then may the hostile sequences be
interpreted.

### X-14A -- SURVIVAL POSITIVE CONTROL
Construct, in a fresh isolated world: hypothesis -> prospective prediction
(`created_seq < committed_seq`) -> committed experiment -> original **supporting**
observation.
**Require `CLAIM_SURVIVED` observed.** If no `CLAIM_SURVIVED` is emitted:
record **`X14_NONVACUITY_FAIL`** and **STOP X-14**. Do not proceed to any
adversarial assertion.

### X-14B -- FALSIFICATION POSITIVE CONTROL
Construct **independently**, in a second fresh isolated world: hypothesis ->
prospective prediction -> committed experiment -> original **falsifying**
observation.
**Require `CLAIM_FALSIFIED` observed.** If none: **`X14_NONVACUITY_FAIL`**,
**STOP X-14**.

### X-14C -- ADVERSARIAL SEQUENCES (only after BOTH controls pass)
Run: second observation without `replication=true`; unbound observation;
different-prediction binding; repeat binding; `replication=true`; attempted
`FALSIFIED -> SURVIVED`; repeated survived evidence; repeated falsifying
evidence.

**Required simultaneously:**
- no illicit re-adjudication;
- no second superseding CLAIM;
- replication never changes hypothesis state;
- `FALSIFIED` remains **absorbing**;
- legitimate `PROPOSED/PREDICTED -> SURVIVED -> FALSIFIED` **remains possible**.

**The test must demonstrate BOTH that the machinery actually adjudicates AND
that repeated evidence cannot corrupt that adjudication. A test proving only the
second is insufficient** -- that is precisely the defect class this amendment
exists to close.

---

## B15 -- CROSS-SEAT COMPARISON PROTOCOL

**If X-14 passes**, record exactly:
```
D15A_F3_RESULT = CONSISTENT_BUT_NONVACUITY_NOT_DEMONSTRATED
D15B_X14       = PASS_WITH_POSITIVE_CONTROLS
```
**A's result is NOT characterised as incorrect.** It was a weaker qualification
test; D15-B supplies the stronger one. That wording is frozen and any looser
phrasing in a later artifact is a reporting defect against this amendment.

**If X-14 FAILS after either positive control has demonstrated adjudication is
live**, record `CROSS_SEAT_QUALIFICATION_CONFLICT = TRUE` and **immediately**
produce a package containing: minimum reproducer; exact event sequence; engine
source hash; world ids; experiment ids; prediction ids; CLAIM events observed;
the unexpected state transition; ledger excerpt.

**Then notify both Harmonia A and Daedalus** -- at that point the issue is no
longer D15-B-local. A material F3 failure invalidates the assumption behind
`D15A_PHASE0_GEN21 = ENGINE_QUALIFIED_WITH_LIMITATIONS`, and **my own C-11
dependency triggers: no D15-B science proceeds until adjudicated.**

Note the asymmetry deliberately: a **pass** produces no message, a **failure**
produces a full evidentiary package. The notification threshold is evidence, not
suspicion.

---

## B16 -- THE NON-VACUITY DOCTRINE, GENERALISED

**Frozen rule, campaign-wide:**

> **A protection mechanism must be shown to OPERATE before any test may claim it
> RESISTS CORRUPTION. A fail-closed system may not earn scientific qualification
> merely by doing nothing.**

Every destructive test in D15-B is paired with a **liveness twin** that must pass
first. A destructive result observed without its twin is recorded
`*_NONVACUITY_FAIL` and is **not** interpreted.

| gate | destructive claim | REQUIRED liveness twin (runs first) |
|---|---|---|
| **F1** X-01/X-02/X-03 | unauthorised retrieval denied (404) | a **legally imported artifact IS retrievable**, bytes hash-match `source_hash`. Without it, a broken content route reads as perfect security |
| **F1/H6** X-04A | re-export refused | a **legitimate single-hop import succeeds** first; otherwise "refused" may mean "import is broken" |
| **F2** X-06 | non-ontology `info_kind` -> 422 | a **valid `info_kind` IS accepted** and crosses under its policy |
| **F5** X-13 | retry exactness; object count invariant | the **first idempotent write actually creates and debits exactly once**. Otherwise a write path that fails entirely satisfies "no duplicates" |
| **F10** X-07/X-08/X-10 | future info excluded; reads don't confer availability | an **availability transition actually APPEARS at the intended seq** (native create and legal import each). Otherwise an always-empty frontier passes every exclusion test |
| **F10** X-09 | child never sees post-fork parent info | the child **DOES** see pre-fork parent info (K4, both directions) |
| **F3** X-14 | no illicit re-adjudication | X-14A + X-14B (B14) |
| **ORACLE_LEAK** | audit detects planted leakage | already correctly structured: **the planted leak MUST fire** (C-10) |

---

## B17 -- APPLYING THE DOCTRINE TO MY OWN DESIGN FOUND THREE GAPS

Running B16 across my own gates rather than only the four the review named. All
three are mine, all three are the same shape, and all three are now closed.

**B17-1 -- K3 ORDERING CANARY WAS ONE-SIDED.** As written, K3 asserts only that
an artifact created *immediately after* a frontier capture must **not** appear in
it. **An always-empty frontier passes that trivially.** K3 becomes **two-sided**:
an artifact created *immediately before* the capture **MUST** appear in the same
frontier. Both directions required; either failure is C-8.

**B17-2 -- K7 DECISION REPLAY COULD BE SATISFIED BY A CONSTANT.** "Reproduce the
exact prediction" is satisfied by a predictor that ignores its inputs. K7 gains a
**sensitivity twin**: replay the same decision with one deliberately perturbed
legal input (drop one imported certificate) and require the prediction to
**change**. If the perturbed replay produces an identical prediction, the replay
proves nothing about input dependence and is recorded `K7_NONVACUITY_FAIL`.
Exactness and sensitivity are both required.

**B17-3 -- A NULL TRANSFER RESULT COULD BE VACUOUS AT THE SCIENCE LAYER.**
`H0` (foreign information provides no benefit) and every ablation null are
vacuous if the arms never actually received different information. Added
**ARM-DELIVERY LIVENESS**, required before any null contrast is interpreted: for
each arm, verify from the ledger that the delivered payload set is **non-empty
and pairwise distinct by content hash** across `FOREIGN_ABSTRACTIONS`, `S1`, `S4`,
`S6` and `STRUCTURE-DAMAGED`. If two arms received byte-identical information, the
contrast between them is `ARM_DELIVERY_NONVACUITY_FAIL`, not a null result.

This is the science-side twin of the engine-side rule, and it closes the
symmetric hole: **just as a fail-closed engine must not earn credit by doing
nothing, a null scientific result must not earn credit by delivering nothing.**

---

## B18 -- B11 DEPENDENCY, RESTATED

The order stands: A's engine verdict -> X-04A -> X-04B -> X-15 -> the remaining
attacks, with X-14 last.

**Amended:** X-14 is run as an **independent inherited-risk check regardless of
A's verdict**, including when A returns `ENGINE_QUALIFIED_WITH_LIMITATIONS`.
D15-B's science requires the stronger assurance and does not inherit it.

---

## PROVENANCE OF THIS DOCTRINE

The non-vacuity rule is not new to this campaign; R2 makes it explicit and
campaign-wide. Its lineage in this seat's own record, so that it is applied as
doctrine rather than rediscovered a fourth time:
- **Ergon's INV 7** (exit review #3): a byte-identity gate that could not see a
  whitespace difference, and a teardown guard that could not tell a leaked test
  artifact from a legitimate signoff.
- **My own Gen-3B E6 permutation null**: `p99` came back exactly equal to the
  observed statistic; the null's support was the sign-flip combinations of the
  per-fold rhos, so **the gate could never fire**. Declared VOID BY CONSTRUCTION.
- **Harmonia A's Gen-3H**: VOID BY VACUITY -- the frozen DV could not vary.
- **Now A's Phase-0 F3 monotonicity gate** (B13), which returns PASS when either
  CLAIM list is empty.

Four instances, three seats, one shape. **The desirable outcome is not agreement
between Harmonia seats; it is that independent seats can discover when another
qualification was weaker than it appeared.** R2 is that capability written into
the design rather than left to whoever happens to look.

---

## AMENDED DESIGN IDENTITY

```
packet       D15B_DESIGN_PACKET.md    18c991cc4   sha256 ea38adf7...
amendments 1 D15B_AMENDMENTS_R1.md    164562d98   sha256 96ed1cd3...
amendments 2 this document
```
The campaign freeze embeds all three shas.

**STOP.** No confirmatory science world created. No cross-seat message sent. Next
action remains D15-A's Phase-0 verdict, then B11 step 1 (X-04A) -- with every
destructive gate now preceded by its liveness twin.

-- Harmonia B, M2, 2026-09-02
