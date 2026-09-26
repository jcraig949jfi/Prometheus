# CAUSAL_LINEAGE_CONTRACT v0.1 (PORTABILITY-01)

Status: FROZEN at the commit that adds it, BEFORE any non-Archaeon adapter is written and before any native adjudication of a
foreign specimen is read. Changes after that point get a new version number and a changelog line. They never edit v0.1.
Owner: Archaeon. Realizations: `archaeon/causal_lens/schema.py` (data model + validator + invariant checks) and one adapter
per engine under `archaeon/causal_lens/adapters/`.

The contract states what a causal account of heredity must DISTINGUISH. It does not say how an engine computes anything.
Archaeon's byte-taint VM is one realization. An engine that cannot realize a distinction must say NOT_IDENTIFIABLE. It must
never pick a default.

## 1. Vocabulary (engine-neutral)

| term | meaning | NOT the same as |
|---|---|---|
| MATERIAL | a unit of state that can be carried into a later state. It may be a byte, a segment, a genome, a program, a parameter vector, a rule or a pattern. Granularity is declared per engine | an organism; a label |
| ENTITY | anything with identity over time that can act, occupy or host: an organism, cell, site, agent or process | its material |
| EXECUTION | one occurrence of an ENTITY performing an action governed by some material | the entity; the material |
| TRANSFORMATION (event node) | a state change that produces material or entities (birth, write, mutation, crossover, arrival, transfer) | a parent link |
| HERITABLE UNIT (HU) | the class of material that later ancestry follows: the thing whose persistence counts as persistence of "a lineage". Engines declare how HU membership is decided | a parent-chain label; a species tag; a slot id |
| ENVIRONMENT VARIABLE | an external condition that can enable or block a transformation | a material |

Graph, not tree. Records are nodes of kinds {MATERIAL, ENTITY, EXECUTION, TRANSFORMATION, HU, ENV} and typed edges:

| edge | from -> to | meaning |
|---|---|---|
| performed_by | EXECUTION -> ENTITY | the executor |
| governed_by | EXECUTION -> MATERIAL | the executed material / template (may be several, with shares) |
| produced | TRANSFORMATION -> MATERIAL/ENTITY | the output |
| copies_from | MATERIAL -> MATERIAL | the output material is a copy of the source material |
| contributes_material | MATERIAL -> MATERIAL/HU | the source material is part of the output's heritable state (share optional) |
| mutates_from | MATERIAL -> MATERIAL | new material replacing an old value at the same role |
| recombines_with | MATERIAL <-> MATERIAL | co-contributors to one output |
| hosts | ENTITY -> TRANSFORMATION | supplied execution, location, resources or transport WITHOUT (necessarily) material |
| transports | ENTITY/ENV -> MATERIAL | moved the material between places or worlds |
| enables | ENV -> TRANSFORMATION | the environment variable was causally required (identifiability stated) |
| member_of | MATERIAL -> HU | heritable-unit membership |
| via | TRANSFORMATION -> EXECUTION | the execution that caused the transformation |
| labelled_parent | ENTITY -> ENTITY | the engine's NATIVE parent pointer, kept verbatim and never read as heredity |

`labelled_parent` exists so native parent IDs are preserved without being promoted. No invariant, count or endpoint may read
it as `contributes_material`.

## 2. Event types
ORIGINATION, REPRODUCTION, AMPLIFICATION, MUTATION, RECOMBINATION, TRANSFER, HOSTING, MIGRATION, ESTABLISHMENT, EXTINCTION,
DEPENDENCY_ACQUISITION, DEPENDENCY_LOSS, UNCLASSIFIED. One transformation may carry several types (e.g.
REPRODUCTION+RECOMBINATION). REPRODUCTION is output material that continues an existing HU. AMPLIFICATION is REPRODUCTION
where the executor is not the HU being continued, or one HU increasing through events it did not itself execute.
ORIGINATION is output material that starts a new HU.

## 3. Per-event fields (each three-valued)
For every TRANSFORMATION the adapter states, where it can:

| field | value | allowed truth |
|---|---|---|
| material_origin | {RANDOM_INIT, RANDOM_INFLOW, INSERTED_SEED, TRANSPLANT, MUTATION, RECOMBINATION, COPY, COMPUTED, UNKNOWN} per output material (multiset) | value or NOT_IDENTIFIABLE |
| executor | ENTITY ref | ref / NONE (no individual executor exists) / NOT_IDENTIFIABLE |
| executed_material | MATERIAL refs with shares | refs / NONE / NOT_IDENTIFIABLE |
| child_contributors | MATERIAL or HU refs with shares | refs / NOT_IDENTIFIABLE |
| host | ENTITY ref | ref / NONE / NOT_IDENTIFIABLE |
| resulting_hu | HU ref | ref / NOT_APPLICABLE (no heritable unit in this substrate) / NOT_IDENTIFIABLE |
| env_dependencies | ENV refs | refs / NONE_FOUND (tested) / NOT_IDENTIFIABLE (untested) |
| basis | how each field was decided: TRACE (execution-level data flow), REPLAY (deterministic re-run), NATIVE_RECORD (engine wrote it), DERIVED (computed from native records by a stated rule), DECLARED (fixture/spec) | required on every non-missing field |

Every boolean property (e.g. `spontaneous`, `executor_is_ancestor`, `established`) is a TRI: YES / NO / NOT_IDENTIFIABLE.
Missing (absent key) means "adapter says nothing". NOT_IDENTIFIABLE means "adapter asserts the engine cannot decide". NO is
a positive claim and needs a basis like YES does.

## 4. Invariants (the portable object)

| id | invariant | how it is checked (schema.py) |
|---|---|---|
| I1 | Inserted ancestry cannot become spontaneous because a label changes. | an HU with any contributes_material ancestor of origin INSERTED_SEED or TRANSPLANT may not carry spontaneous=YES |
| I2 | Ecological host identity does not imply genetic contribution. | an ENTITY that `hosts` an event is a contributor only if an explicit contributes_material edge from its material exists |
| I3 | Executor identity does not imply child-material ancestry. | same rule for performed_by: executor-owned material is a contributor only with an explicit edge |
| I4 | Descendants inherit contributor provenance unless a demonstrable ORIGINATION replaces it. | the origin set of a material = the union over its contributes_material/copies_from sources; only an ORIGINATION transformation with new material may introduce new origin classes |
| I5 | Mutation creates new material without erasing the ancestry of retained material. | a MUTATION produces a new material node linked mutates_from; retained materials of the same output keep their edges |
| I6 | Recombination can have multiple material ancestors. | child_contributors is a set; a validator rejects adapters that truncate to one when the source records more |
| I7 | Transplantation preserves donor ancestry. | TRANSFER/TRANSPLANT output material has copies_from (or identity) to the donor material, and origin TRANSPLANT is layered on the donor's origin, never replacing it |
| I8 | Establishment is persistence of a heritable unit, not repeated labels from one takeover. | ESTABLISHMENT is counted per HU; ENTITY labels or native lineage ids that share one HU count once |
| I9 | Amplification and origination are distinct. | AMPLIFICATION/REPRODUCTION never creates an HU; ORIGINATION always does |
| I10 | Ambiguity stays ambiguity. | NOT_IDENTIFIABLE is never coerced to NO; a field with basis NATIVE_RECORD of kind `parent_id` may not support child_contributors=YES at material granularity (false precision) |
| I11 | Parenthood is not heredity. | `labelled_parent` edges are never read by I1-I10 or by any count |
| I12 | Resolution cannot exceed evidence. | a claim's granularity (byte / segment / genome / entity) cannot be finer than its basis's granularity |

## 5. Identifiability rules adapters must follow
- No material provenance in the engine -> child_contributors = NOT_IDENTIFIABLE. It is NOT the parent IDs.
- No individual executor (field dynamics, a CA rule applied everywhere, a GA operator) -> executor = NONE, with basis
  stated. Never invent one.
- No meaningful HU -> resulting_hu = NOT_APPLICABLE and no ESTABLISHMENT events. Never manufacture a genome.
- An environment variable is a dependency only if an intervention (arm, ablation, replay) tested it. Otherwise
  NOT_IDENTIFIABLE.

## 6. Two modes
- LIGHT OBSERVATORY: per-event fields that come from native records only (basis NATIVE_RECORD/DERIVED), aggregated counts
  per HU, and anomaly flags. No execution-level tracing. Must run online at < 5% engine overhead (target, measured).
- FULL FORENSIC: per-specimen deterministic replay with execution-level tracing (basis TRACE/REPLAY). Only for specimens
  that the light mode flagged or that were preserved as fossils.
The pattern is: cheap online anomaly flag -> preserved evidence -> expensive causal replay.

## 7. Differential adjudication
For each specimen there are two readings. NATIVE is what the engine's own ruler says. LENS is what the adapter infers, with
the adapter frozen before the native adjudication is read. Each field is classified AGREES / DISAGREES / NATIVE_ONLY /
LENS_ONLY / NOT_IDENTIFIABLE_BOTH. Disagreements are kept as results. Neither side is edited to match the other.

## Changelog
- v0.1 (2026-09-26): initial, frozen before foreign adapters.
