# D15-B DESIGN AMENDMENTS R1 (review verdict, 2026-09-02)

Amends `D15B_DESIGN_PACKET.md` (commit `18c991cc4`, ASCII twin `955ce0f43`).
**No scientific falsifier is relaxed and no gate is loosened; every amendment
tightens.** The campaign freeze will embed the pair (packet sha, this sha).

**Sequencing accepted verbatim and binding:**
```
D15-A GEN-2.1 requalification -> D15-B crossing/provenance attack matrix
-> generator qualification -> pilot -> power freeze -> confirmatory freeze
-> campaign
```
**No confirmatory science world is created before those prerequisites pass.**

**Claim ceiling preserved exactly, and restated so it cannot drift:** diet purity
for the RAW / ABSTRACTION / OBSERVATION conditions is enforced by **experimental
construction and audit, not by GEN-2.1 semantic policy**. B-F2-1 and B-F2-2 are
accepted as real expressivity limitations, not release-blocking defects. **Those
diets are never to be described as engine-enforced, in any artifact, at any
point.** A grep-able guard is added to the report generator: the strings
"engine-enforced", "policy-enforced" and "engine enforces" may not appear within
the same section as RAW, ABSTRACTION or OBSERVATION diet results.

---

## B1 -- X-04 PROMOTED TO A BLOCKING ORIGIN-PROVENANCE GATE

X-04 is no longer one row in the matrix. It is a **gate**, split in two, and
**no primary cross-world provenance claim proceeds until it is understood.**

The question it actually asks: **does provenance mean provenance of the artifact
object, of the bytes, or of the scientific information?** GEN-2.1 appears to
guarantee the first. D15-B must discover how far the guarantee extends.

### X-04A -- DIRECT TRANSITIVE RE-EXPORT
`A` creates `X`; `B` imports `X`; `C` attempts to import `B`'s imported `X`.
Run **both** paths and report them separately, because the documented contract
differs between them:
- **same-client** (the D15-B configuration by construction),
- **cross-client** (where H6's NATIVE-origin requirement is documented).

### X-04B -- NATIVE REPUBLICATION LAUNDERING
`A` creates `X`; `B` imports `X`; `B` reads `X` legally; `B` creates `X'` as a
**new NATIVE artifact**; `C` imports `X'` from `B`. Four cases, run as a ladder
because they probe successively weaker notions of identity:

| case | `X'` content | probes |
|---|---|---|
| 1 | exact bytes of `X` | byte-identity provenance |
| 2 | same semantic content, changed metadata | object-identity provenance |
| 3 | canonically equivalent content, changed serialization | content-hash provenance |
| 4 | derived abstraction carrying the same scientific claim | information provenance |

**Adjudication, and both outcomes are explicit:**
- If exact imported bytes (case 1) can be trivially reissued as NATIVE and thereby
  acquire fresh export rights, **and this violates the documented H6 contract**,
  issue defect **`B-X04-ORIGIN-LAUNDERING`** with severity classified against the
  contract text.
- If the contract **technically permits** it, it is **not** an implementation
  defect merely because the science dislikes it. Issue instead:
  **`SUBSTRATE_SEMANTIC_GAP: INFORMATION_ORIGIN_NOT_PRESERVED_ACROSS_REPUBLICATION`**.

Cases 2-4 are expected to be permitted under any reading; their value is
**locating the boundary** at which the guarantee stops, not scoring a defect.
The boundary itself is the deliverable, recorded as
`origin_guarantee_extends_to in {bytes, object, content, information}`.

**Blocking:** the D15-B provenance claim, the duplicate-evidence model (packet
s7), and every T2/T3 verdict depend on the answer. None issue before it.

---

## B2 -- X-15 PROMOTED TO A BLOCKING EVIDENCE-SEMANTICS GATE

`evidence_role in {ORIGINAL, REPLICATION}` answers a **within-world experimental**
question. `origin in {NATIVE, IMPORTED}` answers an **artifact-provenance**
question. Neither answers the one a transfer campaign needs: *is this hypothesis
supported by locally generated evidence, by imported evidence, or by an
independent replication?*

X-15 must establish whether D15-B can reconstruct these five categories
**without ambiguity**:

```
LOCAL_ORIGINAL_EVIDENCE
LOCAL_REPLICATION
IMPORTED_REPORT_OF_FOREIGN_EVIDENCE
IMPORTED_DERIVED_ABSTRACTION
DUPLICATE_REPORT_OF_SAME_NATIVE_EVIDENCE
```

If the engine cannot encode them first-class, determine whether they are
nevertheless **deterministically reconstructible** from: artifact lineage,
observation ledger, source world, experiment id, native ancestor, import history.

**Two outcomes, both explicit:**
- **YES** -> `GEN21_LIMITATION: EVIDENCE_SEMANTICS_DERIVED_NOT_NATIVE`.
  D15-B proceeds **with the limitation declared in every dependent claim.**
- **NO** -> `SUBSTRATE_GAP: EVIDENCE_INDEPENDENCE_NOT_RECONSTRUCTIBLE`.
  **Any result depending on independent-evidence counts, replication counts,
  confidence aggregation, or meta-analysis is VOID.** Accuracy-only transfer
  results may still survive, provided they demonstrably do not rely on those
  quantities -- and that non-reliance is itself audited, not asserted.

**Explicit prohibition, adopted:** D15-B may not build a parallel shadow ontology
that makes the substrate appear stronger than it is. The five categories, if
derived, are labelled **DERIVED** in every artifact that carries them, with the
reconstruction rule attached, so no reader can mistake a D15-B inference for an
engine guarantee. This is the same discipline as the s0 diet-purity ceiling.

---

## B3 -- STRUCTURAL TRANSFER MUST BE STRONGER THAN PREDICTIVE TRANSFER

Balanced accuracy on prospective repair-success predictions is retained as the
primary endpoint. It establishes only that **imported information improved
prediction**. That is weaker than **a transferred abstraction captured reusable
structure**, and the packet is amended so the two can never be conflated.

Every claimed STRUCTURAL_TRANSFER result in **Regime D** must pass a
**causal certificate test**: four interventions, all at matched delivery.

| arm | construction |
|---|---|
| **CERTIFICATE-TRUE** | the learned obstruction certificate |
| **CERTIFICATE-SHUFFLED** | existing S1: certificates from other targets' sources |
| **CERTIFICATE-STRUCTURE-DAMAGED** | **preserve** byte size, number of cores, support counts, confidence distribution, vocabulary, marginal FAIL rate; **alter** the incidence-structure descriptors / WL hashes. Implementation: each `wl_hash` is recomputed from a randomly rewired core of the **same size and same arity multiset**, so every non-structural field is bit-identical in distribution and only structural identity is destroyed |
| **CERTIFICATE-STRUCTURE-ONLY** | **remove** source identity, confidence, support frequency; **retain only** the structural core descriptors (`size`, `arity_multiset`, `wl_hash`) |

**Frozen interpretation:**
- `TRUE > SHUFFLED` **and** `TRUE > STRUCTURE-DAMAGED` -> evidence for
  **structure-specific** transfer.
- `TRUE ~= STRUCTURE-DAMAGED` -> the certificate helps, **but not for the
  explanation claimed**. Reported as such; the structural reading is withdrawn.
- `STRUCTURE-ONLY` retains substantial gain -> **strong** evidence that the
  invariant abstraction itself transfers.
- Gain exists **only** with support/confidence/source metadata -> **statistical
  transfer, not structural transfer.** That is the verdict wording.

**Adopted as a naming rule:** the word STRUCTURAL is not licensed merely because
Regime D changes surface encoding. It requires the certificate test above.

---

## B4 -- OMEGA FIREWALL: ADD AN IMPOSSIBILITY CANARY

"Omega never enters any world" is necessary and insufficient. A **planted oracle
canary** is added -- maximally predictive, scientifically forbidden, and
underivable from legitimate source failures.

**Construction.** Each generator instance holds a secret key `S_inst` (generator
side only, never serialised into any world). For each query `q` the canary token
is `t(q) = HMAC(S_inst, q)`, whose low bit **equals the true label**. Possession
of the tokens gives near-perfect classification; they cannot be derived from
legitimate failures because `S_inst` is never exposed. Access exists **only**
inside the quarantined ORACLE_LEAK control (packet s3.4).

**Three-layer firewall, all three required:**
1. **STATIC detection.** Mechanically scan certificate payloads, artifacts,
   hypotheses, metadata, learner logs, feature matrices and cached datasets for
   any occurrence of `S_inst`, any `t(q)`, or any value with the token's
   distributional signature. Any hit is a contamination stop (C-3/C-4).
2. **PROVENANCE reconstruction.** Every certificate must be rebuildable from its
   source world's own recorded failures (existing C-4), so an oracle path has no
   legitimate ancestry to hide behind.
3. **BEHAVIOURAL positive control.** Replace the legitimate source evidence with
   **matched noise** while leaving any accidental oracle path intact. If
   performance remains high, an oracle path exists and **the leak audit must
   fire**. If the audit does not fire on this arm, the audit is unqualified and
   every leak-freedom claim in the campaign is void (existing C-10, now with a
   behavioural trigger rather than only a planted-content one).

The behavioural layer is the one that catches leakage the static scanner cannot
name in advance, and it is the reason all three are warranted given how much of
this campaign rests on generator-held Omega.

---

## B5 -- THREE TRANSFER OBJECTS, REPORTED SEPARATELY

The single word "transfer" is retired from D15-B's headline. Three phenomena are
reported separately and never collapsed into one mean TRANSFER_GAIN.

| object | definition | primarily attacked by |
|---|---|---|
| **T1 PRIOR TRANSFER** | foreign worlds improve base-rate estimates, family frequencies, generic repair priors. No target-specific structural correspondence required | **Regime C** (family shift), **S6** (marginal only) |
| **T2 CLASS TRANSFER** | foreign information narrows the obstruction family / repair family / candidate class, without instance-specific identification | **S4** (irrelevant swap), **S3** (rank randomized) |
| **T3 STRUCTURAL TRANSFER** | a representation-invariant abstraction learned elsewhere improves prediction because the same underlying structural relation applies to the held-out target | **Regime D** (surface shift) + the **B3 certificate test**; **Regime B** attacks coordinate dependence |

Each is reported with its own effect size, CI, and controls.

### Decision ladder (predeclared; each level REQUIRES the levels below it)
```
H0  Foreign information provides no prospective benefit.
H1  PRIOR TRANSFER            -- improves only generic marginal prediction.
H2  CLASS TRANSFER            -- narrows obstruction/repair classes beyond
                                 marginal priors.
H3  REPRESENTATION-ROBUST     -- gain survives independent recoordination.
H4  STRUCTURAL TRANSFER       -- an invariant learned abstraction improves
                                 held-out targets under surface-generator
                                 shift AND fails the structure-damaged control.
H5  ECOLOGICALLY ROBUST       -- benefit survives dosage, irrelevant-source,
                                 anti-transfer, duplicate-evidence and
                                 provenance audits without uncontrolled
                                 negative transfer.
```
**`H4` is not promoted because one Regime-D number is significant.** Outcomes of
the form `T1_SUPPORTED / T2_SUPPORTED / T3_NOT_SUPPORTED` are first-class and are
more informative than "transfer works".

---

## B6 -- PRIMARY COMPARATOR: S1 MAY NOT CARRY THE CAUSAL CONCLUSION ALONE

The primary contrast is retained:
```
TRANSFER_GAIN = BalAcc(FOREIGN_ABSTRACTIONS) - BalAcc(S1_SHUFFLED_PAIRING)
```
**But a T3 structural verdict additionally requires the positive arm to
outperform ALL of:** `S4 IRRELEVANT_SWAP`, `S6 MARGINAL_ONLY`, and
`CERTIFICATE-STRUCTURE-DAMAGED`.

This is adopted directly against my own stated risk: a weak S1 would flatter the
result, and my Gen-3B campaign closed on exactly the finding that a designed
control can look adequate while being defeated. Requiring three independent lower
bounds makes that failure **impossible to hide** rather than merely disclosed.

---

## B7 -- INFORMATION-DIET COMPARISON: TWO MATCHING BASES

The `FOREIGN_FAILURES` / `FOREIGN_SUCCESSES` / `FOREIGN_MIXED` comparison is
preserved at matched volume, with one interpretive safeguard added.

A failure artifact and a success artifact may carry very different information
density per byte. Therefore **both** matchings are reported:
1. **matched artifact/byte volume** (as designed), and
2. **matched number of underlying experimental events represented** -- defined as
   the count of distinct source-world experiment/observation events the artifact
   summarises, recovered from the source ledger, not from the artifact's own
   self-description.

**If failures win only because each failure artifact encodes substantially more
observations, the report says so in the verdict sentence, not in a footnote.**
Semantic parity is not forced where none exists; the asymmetry is measured and
reported as a property of the diets.

---

## B8 -- K7 DECISION REPLAY (added to the KnowledgeSet audit)

K1-K6 approved unchanged. **K7 is added, and it is the strongest gate in the
audit.**

For a sample of target predictions -- **all of them if tractable**:
1. record the prediction seq;
2. **terminate the client process**;
3. reconstruct the target frontier from engine state;
4. recover every imported artifact legally available at that seq;
5. rebuild the feature representation;
6. reproduce the exact prediction.

Where the pipeline is deterministic, **exact output is required**. The objective:
**no scientific decision depends on ambient client state that F10 cannot
reconstruct.** A K7 failure is C-1 (whole-campaign stop), not a warning.

This is the same standard D15-A's A3 applies to its synthesis warrant, adopted
here by the same argument.

---

## B9 -- CROSS-SEAT IMPORTS: ADAPTER FROZEN BEFORE INSPECTION

`D15B-X` remains **non-load-bearing**; A's and C's schedules must not determine
whether D15-B completes. Their artifacts are scientifically interesting precisely
because they were generated for independent experiments.

**Added constraint:** the adapter schema is **frozen and hashed before any A or C
artifact content is inspected.** The adapter may not be redesigned after seeing
their contents -- that would make `D15B-X` post-hoc feature engineering. If the
frozen adapter cannot consume their artifacts, the arm is **skipped and recorded
as skipped**, and the incompatibility is reported as a finding about
cross-seat interoperability rather than repaired.

---

## B10 -- POWER ON RETAINED VALID UNITS

The **+0.08 MDE stands as a frozen scientific-importance threshold** and is not
lowered after observing a reproducible smaller effect. A smaller effect may be
**reported** -- it does not pass the strong gate. The distinction between a
statistically nonzero effect and scientifically meaningful transfer is preserved
in the verdict wording.

**Amended power procedure:** the pilot additionally estimates the expected
exclusion / contamination rate from
```
invalid certificates | failed imports | audit stops | generator census rejection
```
and the confirmatory sample is powered on **retained valid units**, not nominal
generated worlds. `N_generate = N_required / (1 - expected_exclusion_rate)`, with
the rate frozen from the pilot and the realised rate reported beside it.

---

## B11 -- ENGINE ATTACK ORDER (frozen)

Executed **after** D15-A returns GEN-2.1 qualification. Provenance semantics come
first because they determine whether the later scientific ecology can be
interpreted at all.

```
1.  X-04A  direct transitive re-export
2.  X-04B  native-republication laundering (cases 1-4)
3.  X-15   evidence provenance / replication distinction
4.  X-11   exact-copy / global-id behaviour
5.  X-12   documented artifact-id squat
6.  X-01 / X-02 / X-03   content access attacks
7.  X-05 / X-06          ontology attacks
8.  X-07 / X-08 / X-09 / X-10   KnowledgeSet attacks
9.  X-13   idempotency
10. X-14   F3 re-adjudication regression
```

---

## B12 -- PHASE-0 / PRE-PILOT DELIVERABLES

Produced **before** any pilot science return:
```
D15B_SUBSTRATE_ATTACK_REPORT.md
D15B_CROSSING_QUALIFICATION.json
D15B_PROVENANCE_QUALIFICATION.json
D15B_GENERATOR_CENSUS.json
D15B_ENGINE_DEFECTS.jsonl
D15B_SCIENCE_DEFECTS.jsonl
```

Each must explicitly answer, with the answer machine-readable:

1. Can information be re-exported directly through an imported copy?
2. Can imported knowledge be laundered by native republication?
3. Is evidence independence reconstructible?
4. Can local replication be distinguished from imported foreign evidence?
5. Does artifact-id / global-id behaviour silently suppress valid science
   artifacts?
6. Can every target decision be replayed from its legal frontier?
7. Does the abstraction certificate contain actual transferable structural
   information?
8. Does the generator contain marginal-prior or master-key shortcuts?
9. Can the planted oracle leak be detected statically **and** behaviourally?
10. Is GEN-2.1 qualified for a provenance-clean D15-B campaign?

**If not, stop.** A dead transfer hypothesis is a valid scientific outcome. A
broken crossing substrate is a valid engineering outcome. **A positive transfer
number produced through ambiguous provenance is neither.**

---

## B13 -- DECLARED DEPENDENCY RISK ON D15-A PHASE 0 (mine to state, not to fix)

B11 makes my entire attack sequence gate on A's `ENGINE_QUALIFIED` verdict, and
A is the party that verdict unblocks. That structure is the one this seat exists
for, so the risk is declared here rather than discovered later.

Reviewing A's committed-but-unexecuted `phase0_engine_attack.py` (`bc2cc3dd8`)
against my own dependency, three concerns were checked and two cleared: `RUNID`
is defined (line 69), and the shipped client **does** support `idem_key` on
`hypothesis` -- only `experiment()` lacks it, which A already filed as
`P0-client-idemkey`.

**One did not clear.** A's F3 monotonicity gate returns True when **either**
CLAIM list is empty, so an engine emitting **no CLAIM events at all** reads PASS;
and `x.get("seq", x.get("world_index"))` yields `None` when neither key exists,
which makes `max()` raise `TypeError` mid-run against the production engine.
That is the same vacuity shape filed against Ergon's INV 7, against my own E6
permutation null, and hit by A themselves at Gen-3H.

**Disposition:** I have not touched A's file and will not. This is recorded as a
D15-B **inherited risk**: if `ENGINE_QUALIFIED` is issued on a gate that cannot
fire, D15-B inherits an unqualified substrate while believing otherwise, which is
precisely C-11. **Mitigation within my own scope:** X-14 re-fires the F3
re-adjudication sequences independently (already in B11 step 10) and reports its
own monotonicity result with a **non-vacuity precondition** -- my check asserts
that at least one CLAIM_SURVIVED **and** at least one CLAIM_FALSIFIED were
actually observed before it is allowed to return PASS. If A's Phase 0 and my
X-14 disagree, that disagreement is a first-class finding and is reported to both
seats.

---

## AMENDED DESIGN IDENTITY

```
packet      D15B_DESIGN_PACKET.md      commit 18c991cc4
packet ascii D15B_DESIGN_PACKET.txt    commit 955ce0f43
amendments  this document
```
The campaign freeze embeds the pair (packet sha256, amendments sha256). Both
shas are journaled at issuance in `d15b/JOURNAL.jsonl`.

**STOP.** No confirmatory science world is created. The next action is D15-A's
Phase-0 verdict, then B11 step 1.

-- Harmonia B, M2, 2026-09-02
