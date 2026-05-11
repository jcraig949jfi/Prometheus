# Techne Work Queue — 2026-05-10

Status: drafted under the v3.1.0 scaffolding-landed posture. v4.0 contract-change
window is the next deliverable. All Wave items below trace to a downstream
consumer; bare scaffolding work is rejected at the door.

---

## Constraints

**Behavior-delta requirement (HARD WARNING, 2026-05-10).** Per
`feedback_substrate_passive_consumer_warning.md`, the substrate risks becoming
a beautifully-falsifying machine while the model stays passive. Every artifact
registered under this queue must trace to a downstream behavior delta —
Sigma stub tests transitioning from `SKIPPED` to `PASSED`/`FAILED`, an Ergon
typed view consuming a new dataclass, an Apollo/Rhea pipeline reading a new
field. Registering a primitive without a downstream consumer touching it
inside the same window is forbidden.

**Contract-change-window protocol** per `contracts/substrate_tier_schema.md`
§5. Outside an open window the schema is read-only. Opening requires a Techne
session note declaring `contract_change_window: open`, `wave_number`,
`expected_close`, and `predeclared_primitives`, plus a matching CHANGELOG
entry. Frozen-interface doctrine still applies inside the window; the window
is the controlled break, and once closed the new shape is the new frozen
shape.

**Source-of-truth chain.** Spec content comes from
`aporia/doctrine/substrate_vocabulary/primitives.md`, drawing from
`aporia/docs/tensor_priority_synthesis_2026-05-09.md` §3 + §8. Techne adds
inventory metadata (version, file, deps, anti-anchor pins) but does NOT
redefine semantics. Missing-from-`primitives.md` means add there FIRST;
inventory entry is downstream.

---

## Wave 1 — open contract-change window + register the 7 foundational primitives

**Window declaration (mandatory step 0).**

- Open `techne/TECHNE_SESSION_2026-05-12.md` (or earliest working day) with
  header:
  ```
  contract_change_window: open
  wave_number: 1
  expected_close: 2026-05-19
  predeclared_primitives:
    - CoordinateChart           # Tier P0
    - CanonicalizationProtocol  # Tier P0
    - TensorNetwork             # Tier A++
    - ConstructiveExistenceWitness   # Tier B parent
    - GenericityAlmostEverywhereCert # Tier D
    - RepresentationTheoreticInvariant # Tier E parent
    - MomentPolytope            # Tier C
  breaking: false
  ```
- Mirror in `CHANGELOG.md` under a new `## v4.0.0 (major) — IN PROGRESS` heading
  with the same five fields.
- Exit criterion: all seven predeclared primitives registered in
  `inventory.json`, all matching Sigma stub tests transitioning from
  `SKIPPED` to `RUNNING` (pass or fail), and a closing entry in both the
  session note and CHANGELOG. If exit criterion is not met by 2026-05-19,
  close the window AS-IS — partial registration is preferable to a window
  that drifts indefinitely.

**Step 1 — Add the missing Tier-P0 layer to the vocabulary (prerequisite).**

`coordinate_chart.py` and `CanonicalizationProtocol` already exist in
`sigma_kernel/` (Sigma defined them out-of-process because the substrate had
no slot). They are missing from `primitives.md`. Add a top-level section
`## Tier P0 — substrate infrastructure` containing:

- `CoordinateChart` — (domain, region_key)-scoped bundle of (axes,
  canonicalization, metric, equivalence relations, admissible region, valid
  ops). Substrate v2.3 §6.1. Consumed by Tier-A++ `TensorNetwork` (which
  EXTENDS CoordinateChart per Sigma stub framing), ExclusionCertificate,
  EvidenceField.
- `CanonicalizationProtocol` — typed wrapper around a canonicalizer impl
  (Aporia Study 17). Subsumes Study 07's `cohomological_functor`. Sub-types:
  `CohomologicalFunctorCanonicalizer`, `IdentityCanonicalizer`. Required
  field on every CoordinateChart.

**Step 2 — Register the 7 primitives in `inventory.json`.**

Schema diff for each (illustrative; full JSON shape per
`contracts/substrate_tier_schema.md` §3). The seven entries land as a NEW
section `substrate_primitives` parallel to `tools`. Top-level
`schema_version` bumps `4.0` → `5.0` to mark the substrate-tier section
addition. Each primitive entry takes the shape:

```jsonc
{
  "name": "TensorNetwork",
  "version": "1.0.0",
  "tier": "A++",
  "parent_class": null,
  "subtypes": ["MPS", "MPO", "PEPS", "MERA", "ContractionTree", "LineGraph"],
  "composition_eligibility": {"A++": true, "B": true, "C": true, "D": true, "E": true},
  "anti_anchor_pins": ["AA-009"],          // RankZooSignature 5-rank rule
  "source_reports": ["T#84"],
  "source_citations": ["arXiv:2602.11309 (Buczynski 2026)", "Markov-Shi 2008"],
  "vocabulary_entry": "aporia/doctrine/substrate_vocabulary/primitives.md#tensornetwork",
  "sigma_stub_path": "sigma_kernel/tests/test_tensor_network_stub.py",
  "implementation_path": "sigma_kernel/tensor_network.py",
  "registered_date": "2026-05-12"
}
```

The seven entries with their distinguishing fields:

| # | Primitive | Tier | Sigma stub | Stub test count |
|---|---|---|---|---|
| 1 | `CoordinateChart` | P0 | (already lands; verify) | n/a (already passing) |
| 2 | `CanonicalizationProtocol` | P0 | (already lands; verify) | n/a (already passing) |
| 3 | `TensorNetwork` | A++ | `test_tensor_network_stub.py` | 15 tests / 6 classes |
| 4 | `ConstructiveExistenceWitness` | B (parent) | `test_constructive_existence_witness_stub.py` | 21 tests / 8 classes |
| 5 | `GenericityAlmostEverywhereCert` | D | `test_distribution_object_stub.py` | 17 tests / 7 classes (also covers `RandomTensorEnsemble`, `PhaseTransitionThreshold`, `AlgorithmThresholdCert` — see TBD below) |
| 6 | `RepresentationTheoreticInvariant` | E (parent) | `test_representation_theoretic_invariant_stub.py` | 24 tests / 8 classes |
| 7 | `MomentPolytope` | C | `test_moment_polytope_stub.py` | 17 tests / 6 classes |

Total: 94 contract tests across 35 classes flip from `SKIPPED` to `RUNNING`.

**Step 3 — Implementation files.**

For each of items 3–7, create a frozen dataclass shell at
`implementation_path`. The dataclass MUST satisfy the Sigma stub's import
names (verified by Grep). E.g. `sigma_kernel/tensor_network.py` exports
`TensorNetwork`, `NetworkVertex`, `NetworkEdge`, `ContractionPlan`,
`ContractionOrder`, `IndexLabel`, `TensorEntry`, `ContractionResult`,
`TensorNetworkRegistry`, `ContractionError`. Initial implementation does the
bare minimum to make construction/topology contract pass; behavior tests
(associativity, group-action preservation) may legitimately fail in v4.0.0
— those failures ARE the substrate-tester signal for next sprint.

**Step 4 — Anti-anchor pins.**

- `TensorNetwork` pins AA-009 (rank-zoo distinct-fifth).
- `RepresentationTheoreticInvariant` pins AA-001, AA-004, AA-008.
- `GenericityAlmostEverywhereCert` pins AA-005, AA-007, AA-010.
- `ConstructiveExistenceWitness` pins AA-003.
- `MomentPolytope` no current pin.

**Step 5 — Sigma handoff.**

After registrations land and shells exist, notify Sigma maintainer to delete
the `pytestmark = pytest.mark.skipif(...)` block from each of the five stub
files. Run `pytest sigma_kernel/tests/test_*_stub.py -v`. Whatever fails IS
the behavior-delta evidence and seeds Wave 2.

**Success criterion.** 94 contract tests transition `SKIPPED → RUNNING`.
Some pass, some fail. The fails ARE the deliverable.

---

## Wave 2 — Tier-B subtype cluster (depends on Wave 1)

Window: `wave_number: 2`, opens after Wave 1 closes AND Sigma results
triaged. Do not pre-open. Tier-B sub-types need the Tier-B parent registered.

Predeclared primitives (dependency order):

1. **`BorderRankWitness`** (Tier-B parent of rank-zoo cluster). Subtypes
   declared but registered separately: `LimitWitness`, `CactusRankWitness`,
   `BorderCactusWitness`, `WaringRankWitness`,
   `ComputationalComplexityCertificate`. Consumer: Ergon `near_miss_corpus`
   rank-zoo filtering; substrate-tester T-ST-T19-001/002.
2. **`LimitWitness`** (subtype). Independent of cactus subtree. Consumer:
   substrate-tester de Silva-Lim probes.
3. **`ComputationalComplexityCertificate`** (subtype, cross-cutting tag).
   Sub-types `NPHardClass`, `ExistsRHardClass`, `UndecidableClass`. Consumer:
   Ergon near-miss-corpus complexity filter; enforces AA-003 (Shitov 2016).
4. **`WaringRankWitness`** (subtype). Consumes
   `DefectivityCertificate.fat_point_witness` (Tier-C, Wave 3) — forward
   dependency; either defer to Wave 3 or scope-creep a minimal
   DefectivityCertificate into Wave 2. Consumer: substrate-tester
   T-ST-T22-001..003.
5. **`CactusRankWitness`** + **`BorderCactusWitness`** (the v3.1.0
   foreshadowed pilot). Consumer: T-ST-T19-001, T-ST-T19-002.

Cross-cutting (annotation-style, `parent_class: null`):

6. **`DualityCheck`** — annotates BorderRankWitness families.
7. **`PrecisionFloorCertificate`** — mandatory on numerical witnesses;
   already referenced by `TestPrecisionFloorAnnotation`.
8. **`ReshapingCertificate`** — AOP/CO-V identifiability claims.
9. **`MeasureZeroExceptionAnnotation`** — REQUIRED on Tier-B + Tier-D
   composites with explicit exception lists (e.g. AOP/CO-V
   `(6,2,9), (4,3,8), (3,5,9)`). Consumer: C-002 promotion.

Exit: all nine entries land; corresponding Sigma sub-class tests flip to
RUNNING. Window closes 2026-05-26 latest.

---

## Wave 3 — Tier-D + cross-tier composition ratification (depends on Waves 1–2)

Window `wave_number: 3` opens after Wave 2 evidence on which Tier-B subtypes
actually compose with Tier-D in Sigma runtime.

Primitives:

1. **`PhaseTransitionThreshold`** (Tier-D; bundled in
   `test_distribution_object_stub.py`). Promote from Wave 1 implicit to
   first-class.
2. **`AlgorithmThresholdCert`** (Tier-D sibling). Pairs with a specific
   algorithm to certify threshold achievement.
3. **`RandomTensorConcentrationCert`** (Tier-D). Records the long
   `(order_r, dim_d, p_norm, n_summands, ...)` tuple. Consumer: Ergon F011
   retroactive rank-parity audit.

Composition promotions in `registry/compositions.jsonl`:

- **C-001** + **C-002** (already `confirmed: true`): add
  `substrate_test_evidence` pointer to the Sigma test exercising each.
- **C-006** (`TierD × TierD RandomTensor × PhaseTransition`): promote
  `confirmed: false → true` IF Wave 2 evidence shows it fires in Sigma.

Consumer: Ergon F011 audit + T-ST-T72-001. Without this wave the F011
rank-parity audit stays hand-rolled per session — the exact failure mode
REQ-030 was filed against.

Exit: Tier-D triple registers; two composition rules acquire substrate-test
evidence; third promotes iff evidence exists. Window closes 2026-06-02 latest.

---

## Wave 4 — Tier-E + GCT cluster (depends on Waves 1–3)

Deepest layer. Do not rush. Wave 4 must wait for Wave 1–3 evidence — the
Tier-B + Tier-E architectural requirement (GCTObstructionCertificate refuses
to load without upstream RepresentationTheoreticInvariant) is load-bearing
and premature design mistakes propagate.

Primitives:

1. **`KroneckerInvariant`** (Tier-E sub). Kronecker-coefficient data +
   positivity certificates. Consumer: C-007.
2. **`PartitionObject`** (Tier-E sub). Young-diagram with staircase /
   hook-length data. Consumer: KroneckerInvariant + AA-004 enforcement.
3. **`Structured-Equivalence-Class`** (Tier-E meta, T#79). Unifies
   `OrbitWitness` + `HomotopyWitness` + `ArityGradedOperationFamily`.
4. **`OrbitClosureNonMembershipWitness`** (Tier-B base for GCT composite).
5. **`GCTObstructionCertificate`** (Tier-B + Tier-E composite). Five subtypes:
   `OccurrenceObstruction` (KILLED, AA-001), `MultiplicityObstruction`,
   `VanishingIdealObstruction`, `OutsideOrbitObstruction`,
   `EquivariantObstruction` (restricted-model only, AA-008). Substrate
   rejects `OccurrenceObstruction` for `(det_m, padded_perm_{n,m},
   m=poly(n))` as sentinel violation.
6. **`BorderComplexitySeparator`** (Tier-B HARD-5 separator).
7. **`EquivariantComplexityCertificate`** (Tier-B restricted-model). Mandatory
   `restricted_to: SymmetryGroup`; WARNs on unrestricted extrapolation.

Outside-tier (conditional):

- **`RayClassFieldFiducial`** + **`StarkUnitWitness`** (T#85 AFK 2025).
  `outside_tier: true`, mandatory
  `conditional_on: [stark_conjectures, shintani_faddeev_modularity]`. AA-002.

Composition promotions: **C-003** (TierB × TierE GCT) on Sigma evidence;
**C-004** (TensorNetwork × BorderRank); **C-005** (Defectivity × Waring);
**C-007** (Kronecker × Partition).

Consumer: T-ST-T92-001..005 (GCTObstruction + BorderComplexitySeparator +
EquivariantComplexityCertificate + AlgebraicNaturalProofsBarrier + P32
synthesis). Gemini Deep Research Wave 2 (Prompts 4–6) feeds here.

Exit: Tier-E triple + `OrbitClosureNonMembershipWitness` +
`GCTObstructionCertificate` register; ≥1 composition promotes. Closes
2026-06-23 latest. If Wave 1–3 evidence is thin, defer one cycle and document
the deferral.

---

## Wave 5 — open REQ closures + maintenance

**REQ-029 SDP — CLOSE.** Fulfilled externally via `pm.optimization.solve_sdp`
(commit b58d6bfb, wave-15, 6 ops, 20 tests, SCS backend with optional Mosek).
Update `queue/requests.jsonl` status `open → fulfilled`, add
`tool: "pm.optimization.solve_sdp"`, `fulfilled_date: "2026-04-29"`,
`fulfilled_note`. Document in CHANGELOG that this REQ was fulfilled
externally — useful cross-team precedent.

**REQ-028 operator portability — STATUS TBD.** Recon did not surface current
status. Poll Aporia / substrate-tester loop. Spec composes REQ-027 TT_SPLICE
+ signature canonicalizer; needed by P19/P21/P04/P15. If open, queue for
Cycle 34 forge; if fulfilled, close per REQ-029 pattern; if blocked on
canonicalizer, escalate to Stoa.

**REQ-008 Khovanov — DECISION REQUIRED.** Still blocked on heavyweight
install (JavaKh / KhoHo / Sage). Options:

- A. Wait for Gemini Deep Research Wave 3 (Knots/Khovanov 2024–2026 frontier
  survey, scheduled, not yet fired). May surface lightweight alternative.
- B. Defer with `status: "deferred"`,
  `deferred_reason: "no lightweight backend available 2026-05"`.
- C. Force-install via apt/conda. Discouraged — single-tool environment
  commitment.

Recommendation: A first, B as fallback at Wave 5 end if A hasn't fired by
2026-06-30.

**Maintenance:**

- **Catalog stale-anchor mirroring.** Per synthesis §2, five
  `aporia/mathematics/tensor_open_problems_v1.md` entries were edited (T#1,
  T#13, T#56, T#92, T#95). Verify; mirror in `inventory.json`
  `source_citations` for any registered primitive pointing at them (Wave 1–4
  primitives will).
- **Anti-anchor verification cycle.** Gemini Deep Research Wave 1 (Prompts
  1–3) currently firing — verifies AA-001 through AA-010 against primary
  literature. When responses return: update `last_verified`, add additive
  `verified_against_primary: true` (no window needed). Any contradiction
  requires a separate window — that's a falsification event.

---

## Wave 6 — introspection + observability

1. **Per-primitive version-history log.** Per-tool `version` is in place
   (v3.1.0); no history yet. Deliverable: append-only
   `techne/registry/version_history.jsonl`, one entry per semver bump.
   Owner: Techne. Independent of Wave 1–5.
2. **Introspection callable.** No `techne.find(query)` answers "which
   primitives apply to this kind of object." Deliverable: `techne/find.py`
   exposing `find_by_input_type`, `find_by_output_type`, `find_by_tier`.
   Owner: Techne. Depends on Wave 1 substrate-primitive section.
3. **Consumption metric.** No instrumentation tracks Sigma/Ergon/Apollo/Rhea
   primitive consumption. Deliverable: call-counter to
   `techne/registry/usage_counts.jsonl`, appended on `find()` calls and
   primitive constructors. Owner: Techne (schema); consumer agents wire the
   import-side hook. HARD-warning-aligned: no behavior delta if no consumer
   adopts.
4. **CI for contract tests.** `sigma_kernel/tests/` is not auto-run.
   Deliverable: workflow running `pytest sigma_kernel/tests/` on every
   commit touching `techne/` or `sigma_kernel/`. Owner: shared with Sigma.
   No technical blocker.

Wave 6 ships in parallel with Waves 2–4 (no schema touch). Ship item 1
first (cheapest, unblocks 2 and 3).

---

## What's NOT in scope

- Do NOT proactively register Wave 5+ primitives without downstream-consumer
  evidence (HARD WARNING, binding).
- Do NOT bump schema version again without reason. v3.1.0 just shipped;
  next bump is v4.0.0 (Wave 1 window).
- Do NOT modify the existing 25 forged-tool interfaces. Metadata edits OK;
  interface-string edits are not.
- Do NOT generate vocabulary scaffolding without a behavior-delta trace.
  `primitives.md` entries are fine (Tier-P0 backfill required) but each
  must point at a Sigma stub or Ergon typed view exercising it in the same
  window.
- Do NOT collapse tier sub-types (HARD-5). The 5+ rank invariants
  `(R, R-bar, sr, cr, cr-bar, ...)` and four complexity coordinates
  `(dc, underline-dc, L, B, dc_equiv)` each get their own field. AA-009
  enforces.
- Do NOT publish-frame anything (HARD-1). No drafts, targets, manuscripts.

---

## Sequencing recommendation (2–3 weeks)

| Week | Wave | Action |
|---|---|---|
| Week 1 (2026-05-12 → 05-19) | Wave 1 | Open v4.0.0 window. Register 7 primitives. Sigma flips 94 skip-marks. Triage failures. Close window. |
| Week 1 parallel | Wave 5 maintenance | Close REQ-029 inventory-side. Poll REQ-028 status. Decide REQ-008. |
| Week 1 parallel | Wave 6 item 1 | Version-history log shipped (no schema dependency). |
| Week 2 (2026-05-19 → 05-26) | Wave 2 | IF Wave 1 Sigma failures justify (i.e. Tier-B subclass tests are running but failing on subtype-specific assertions): open Wave 2 window, register Tier-B subtype cluster. ELSE: hold for one cycle. |
| Week 2 parallel | Wave 6 item 2 | Introspection `find()` callable shipped against Wave 1 inventory. |
| Week 3 (2026-05-26 → 06-02) | Wave 3 | IF Wave 2 closed cleanly: open Wave 3 window, register Tier-D triple, promote Tier-B + Tier-D composition rule with substrate-test evidence. |
| Week 3 parallel | Wave 5 anti-anchor | Gemini Deep Research Wave 1 responses ingested; `last_verified` + `verified_against_primary` updated. |
| Week 4+ | Wave 4 | Defer until Wave 1–3 evidence fully informs GCT composite design. |

If Wave 1 closes with substantially fewer than 94 tests transitioning to
RUNNING, STOP and re-plan. The behavior-delta evidence is the gating
signal — paper progress (registrations without consumer activity) is forbidden.

---

## Update protocol

After each registration:

1. Update `inventory.json` (per-primitive entry; schema_version bump if
   needed).
2. Update `CHANGELOG.md` under the active version heading.
3. Update this file with a date-stamped note in the relevant Wave section:
   e.g. `[2026-05-12] CoordinateChart registered, Sigma stub passing.`
4. If a Sigma test transitions SKIPPED → PASSED/FAILED, record the transition
   in the same note. This IS the behavior-delta evidence — without it the
   registration does not count under the HARD WARNING.
5. At Wave close, update `inventory.json` `stats` block with new totals
   (`substrate_primitives_total`, `tier_a_count`, `tier_b_count`, ...).
