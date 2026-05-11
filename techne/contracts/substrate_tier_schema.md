# Substrate-Tier Schema (v3.next)

Status: scaffolding only - no Tier-A++ / Tier-B / Tier-C / Tier-D / Tier-E primitives are
registered yet. v4.0 Wave 1 (TensorNetwork + ContractionOrderWitness, CactusRankWitness
pilot, RankZooSignature) is the first scheduled contract-change-window registration.

Date: 2026-05-10
Source synthesis: `aporia/docs/tensor_priority_synthesis_2026-05-09.md` (sections 3 and 8)

---

## 1. Purpose

The 25 forged tools currently in `inventory.json` are concrete `Tier 1` Python wrappers
with frozen `interface` strings. They live below the substrate. The substrate-tier
primitives defined here live above the wrapped tools: they are typed *witness*,
*certificate*, and *invariant* records that operators emit, consume, and compose. A
substrate-tier primitive is not an executable function - it is a typed shape that
operators must produce or accept and that the calibration battery can validate.

This document defines the five tiers (A++, B, C, D, E), the required fields each
primitive must carry, the cross-tier composition flags, and the contract-change-window
protocol that controls when this schema is allowed to break. Outside windows, the
schema is frozen by the same frozen-interface doctrine that governs the Tier 1 tools.

## 2. Tier definitions

### Tier-A++ - TensorNetwork-level

Foundational structural primitives that describe the tensor object itself rather than
any property derived from it. A TensorNetwork primitive is the addressable carrier
object on which every other tier hangs witnesses. Without a registered Tier-A++
primitive, downstream tiers have nowhere to attach. This is the slot for
`TensorNetwork`, `ContractionOrderWitness`, and `RankZooSignature`. The most
foundational HARD-3 primitive (T#84, Markov-Shi 2008 NP-hardness of optimal
contraction) cannot be expressed without Tier-A++ presence.

### Tier-B - ConstructiveExistenceWitness

Constructive certificates of mathematical existence: a primitive of this tier is
produced by exhibiting a witnessing object (a degeneration sequence, an apolar
0-dimensional Gorenstein scheme, an obstruction class, an explicit decomposition).
Cluster includes `BorderRankWitness`, `LimitWitness`, `CactusRankWitness`,
`OrbitClosureNonMembershipWitness`, `WaringRankWitness`, `GCTObstructionCertificate`
(composite, with five subtypes including the `OccurrenceObstruction` anti-anchor),
and the cross-cutting sub-primitives `DualityCheck`, `PrecisionFloorCertificate`,
`ReshapingCertificate`, `MeasureZeroExceptionAnnotation`,
`ComputationalComplexityCertificate`. Tier-B is the densest cluster in the synthesis.

### Tier-C - SecantVarietyEquation

Algebraic-geometric equations cutting out secant varieties and their defective loci.
A Tier-C primitive carries the polynomial relations or scheme-theoretic data that
distinguish defective from generic strata. Cluster currently `DefectivityCertificate`
(T#26, ABGO 2024) and `MomentPolytope`. Smaller cluster than Tier-B; ABGO closure of
Segre-Veronese for `d_i >= 3` makes the parent slot useful even if subtype population
is sparse.

### Tier-D - distributional

Statistical and concentration-style primitives: phase transitions, algorithm
thresholds, generic-almost-everywhere statements, random-tensor concentration bounds.
A Tier-D primitive carries a regime annotation, a bound, and the proof technique
(Bernstein, Lindeberg, BBvH, Slepian, etc.). Cluster includes
`PhaseTransitionThreshold`, `AlgorithmThresholdCert`, `GenericityAlmostEverywhereCert`,
`RandomTensorConcentrationCert`, and the meta-warning
`AlgebraicNaturalProofsBarrier`.

### Tier-E - RepresentationTheoreticInvariant

Invariants emitted by representation theory: characters, Kronecker coefficients,
partition objects, structured equivalence classes. A Tier-E primitive is
group-theoretic in origin and carries explicit `partition`, `group`, and
`character_data` fields. Cluster includes `RepresentationTheoreticInvariant` (parent),
`KroneckerInvariant`, `PartitionObject`, `Structured-Equivalence-Class`,
`RayClassFieldFiducial`, `StarkUnitWitness`. Required prerequisite for Tier-B GCT
work (per cross-tier rule below).

## 3. Required fields per primitive (all tiers)

Every substrate-tier primitive registered in `registry/` must carry:

- `name` - code-style identifier, UpperCamelCase (e.g. `BorderRankWitness`).
- `version` - semver string, starting at `1.0.0`. Bumps follow the same minor / major
  rules as forged tools: minor for additive field changes, major for interface breaks
  and only inside an open contract-change window.
- `parent_class` - the tier-defining parent (e.g. `BorderRankWitness` for
  `CactusRankWitness`; `RepresentationTheoreticInvariant` for `KroneckerInvariant`).
  Top-level parents declare `parent_class: null`.
- `subtypes` - list of declared subtype primitive names (may be empty).
- `composition_eligibility` - object listing the tiers this primitive may compose
  with at registration time. See section 4.
- `anti_anchor_pins` - list of anti-anchor IDs (`AA-NNN` from
  `registry/anti_anchors.jsonl`) this primitive must respect. The calibration battery
  consumes this field to gate substrate-tester probes.
- `source_reports` - list of deep-research report identifiers (e.g. `T#84`, `T#92`)
  that motivate the primitive.
- `source_citations` - list of arXiv / journal citations (text strings, no HTML).

Tier-B specifics: `witness_kind` (e.g. `degeneration_sequence`, `apolar_scheme`,
`obstruction_class`, `decomposition`).

Tier-D specifics: `regime` (e.g. `p_geq_2r`, `matrix_r2`), `bound_kind`
(`upper`, `lower`, `tight`).

Tier-E specifics: `representation_data` (group, character or partition handle).

## 4. Composition eligibility

Two cross-tier composition patterns are confirmed by independent literature
(synthesis section 3.7):

- **Tier-B x Tier-D** - confirmed twice. T#73 fire #43 (`BorderRankWitness` x
  `PhaseTransitionThreshold`) and T#40 fire #45 (`BorderRankWitness` x
  `GenericityAlmostEverywhereCert` for AOP/CO-V exceptions). Both Tier-B and Tier-D
  primitives MUST declare each other as eligible composition targets in their
  `composition_eligibility` field.

- **Tier-B x Tier-E** - confirmed once but architecturally required by T#92.
  `GCTObstructionCertificate` and any other Tier-B primitive that names an orbit
  closure must declare Tier-E in `composition_eligibility`. Substrate-tester refuses
  to load a Tier-B primitive of GCT-flavour without an upstream Tier-E
  `RepresentationTheoreticInvariant` registration. T#95 cluster is a hard
  prerequisite for any T#92 work.

Default flags by tier (these are the registration-time defaults; an individual
primitive may widen but not narrow without a window):

| Tier | A++ | B | C | D | E |
|---|---|---|---|---|---|
| A++ | yes  | yes | yes | yes | yes |
| B   | yes  | yes (parent / sub) | yes (witness for Tier-C eq.) | **yes (REQUIRED for distributional)** | **yes (REQUIRED for GCT-flavour)** |
| C   | yes  | yes | yes | yes | yes |
| D   | yes  | **yes (REQUIRED for Tier-B + Tier-D pattern)** | yes | yes | conditional |
| E   | yes  | **yes (REQUIRED for GCT-flavour Tier-B)** | yes | conditional | yes (parent / sub) |

`Outside-tier` primitives (`AsymptoticSpectrumMonotone`, `RayClassFieldFiducial`,
`StarkUnitWitness`) carry an explicit `outside_tier: true` flag and do not participate
in default-tier composition - their composition rules are case-by-case and recorded
directly in `registry/compositions.jsonl`.

## 5. Contract-change-window protocol

The substrate-tier schema is FROZEN outside an open contract-change window. Frozen
means: no new Tier-A++ / Tier-B / Tier-C / Tier-D / Tier-E primitive may be
registered, no field may be removed or renamed, and no `composition_eligibility`
default may be narrowed. Frozen-interface doctrine still applies inside the window;
the window itself is the controlled break, and once it closes the new shape is the
new frozen shape.

A contract-change window opens when:

1. A Techne session note (e.g. `TECHNE_SESSION_YYYY-MM-DD.md`) declares
   `contract_change_window: open` with an explicit `wave_number`, `expected_close`
   date, and `predeclared_primitives` list.
2. An entry in `CHANGELOG.md` under the next version heading (e.g. `v4.0.0`)
   records the window open with the same fields.
3. The window closes when either the predeclared primitives are all registered,
   or the `expected_close` date is reached, whichever is first. Closing is recorded
   in both the session note and CHANGELOG.

Inside an open window:

- Additive changes (new primitives matching the predeclared list, new optional
  fields, widened `composition_eligibility`) are allowed without a separate window.
- Breaking changes (renamed fields, narrowed eligibility, removed primitives) require
  the window to be explicitly tagged `breaking: true` in the session note.
- All changes inside the window still ship with semver bumps on each affected
  primitive's `version` field.

Outside any open window:

- The schema is read-only.
- Forged tools in `inventory.json` continue to ship under their own per-tool
  versioning rules; a tool minor-bump does not require a substrate window.
- Anti-anchor entries in `registry/anti_anchors.jsonl` may be appended without a
  window only when adding a NEW anti-anchor (additive). Editing or removing an
  existing anti-anchor requires a window.
- Composition rules in `registry/compositions.jsonl` may be appended without a
  window only when `confirmed: false`. Promoting a composition to `confirmed: true`,
  or editing any existing composition, requires a window.

## 6. Wave 1 forecast (v4.0)

Per synthesis section 8, the first scheduled window opens at v4.0 with three
predeclared primitives:

1. `TensorNetwork` + `ContractionOrderWitness` (Tier-A++; T#84). Foundational; nothing
   depends on it but everything will.
2. `CactusRankWitness` (Tier-B; T#19). Pilot for Tier-B contract change - purely
   combinatorial, no degeneration sequence, no NP-hardness reduction.
3. `RankZooSignature` (Tier-A++; T#13). Tracks distinct rank coordinates
   `(R, R-bar, sr, cr, cr-bar, R_partition, R_analytic, R_geometric, R_strength,
   R_slice, ...)` as a single named tuple per tensor.

Waves 2 through 5 are scoped in synthesis section 8 and are not part of v3.next.

## 7. Source

This schema is a v3.next minor scaffold. The substantive content - tier definitions,
composition flags, anti-anchor list, wave plan - is drawn from
`aporia/docs/tensor_priority_synthesis_2026-05-09.md`, sections 3 (substrate
primitives) and 8 (forward dependencies for Techne T038). All citations there are
load-bearing for the v4.0 window.
