# CAUSAL_LINEAGE_CONTRACT v0.2

Status: FROZEN at the commit that adds it, BEFORE any adapter is ported to it. v0.1 (CAUSAL_LINEAGE_CONTRACT.md, frozen 13cdec715)
is historical evidence and is not edited. Realization: `archaeon/causal_lens/schema_v02.py`. Upgrader: `upgrade_v01.py`.
Changelog: `CONTRACT_v0.1_to_v0.2.md`. Ruling: roles/Archaeon/prompts/2026-09-27_contract_v02/.

## 0. Diagnosis that shaped v0.2
B1-B5 have a common root. v0.1 stored a RELATION WITH SEVERAL ROLES as ONE ATTRIBUTE:

| v0.1 singular | roles it collapsed | break |
|---|---|---|
| resulting_hu | continuity of a prior unit / identity of the output / organisation that persists | B1 |
| ENTITY | persistent locus of state (body) / engine label (identity) | B2 |
| executed_material | code that governed the heritable writes / where execution time went | B3 |
| material_origin | from what prior material (ancestry) / where it was made (location) | B4 |
| child_contributors | what actually flowed in the realized event / what would suffice or be needed under an intervention | B5 |

v0.2 separates the roles and nothing more. The test of whether role-splitting is the true repair, rather than the first patch
in an unbounded series, is whether rerunning the four PORTABILITY-01 adapters forces a NEW role. Report section 11 of the
regression answers that.

## 1. Values
- TRI (boolean properties): YES / NO / NOT_IDENTIFIABLE.
- REF fields: a node reference / NONE (a positive statement that none exists) / NOT_APPLICABLE (the concept does not exist in
  this substrate) / NOT_IDENTIFIABLE (an answer exists in principle; the evidence cannot decide it) / ILL_POSED (the requested
  SINGULAR identity is not defined under the declared rule).
- ILL_POSED is permitted ONLY in the identity-valued fields listed in section 5 (`hu_continuity`, `resulting_hu`,
  `architecture_class`, `identity_continuity`). It is never a boolean value. It must carry an `ill_posed` justification: the
  declared rule, plus the complete evidence the rule was applied to, which shows no unique answer. If that evidence is itself
  incomplete (for example, any contributor share is NOT_IDENTIFIABLE), the value must be NOT_IDENTIFIABLE. That rule is
  validator-enforced (J6).

## 2. Nodes (smallest set any specimen required)

| node | meaning | required by |
|---|---|---|
| MATERIAL | immutable carried state at a declared granularity | all |
| BODY | persistent locus carrying state through time (cell, slot, site, memory allocation) | B2 (NPE renaming) |
| IDENTITY | engine-level identifier assigned to a body over an interval | B2 |
| EXECUTION | one occurrence of a body acting | all |
| TRANSFORMATION | event node | all |
| HU | derived heritable unit (continuity class under a declared rule) | B1 |
| ARCH | declared architecture class (kind + criterion + justification) | B1 (PTE, BEE rearranged copies) |
| ENV | environment variable or intervention target | dependencies, counterfactuals |
| LOCATION | niche / world / region / chamber | B4 (NPE niche tags) |
| CF_TEST | a counterfactual test: subject, kind, intervention, outcome, result | B5 (NPE P-11) |

ENTITY is removed. Every v0.1 ENTITY becomes a BODY. Its engine id becomes an IDENTITY assigned to that body (section 8).

## 3. Relations
performed_by (EXECUTION->BODY); carries (BODY->MATERIAL); assigned (IDENTITY->BODY, attrs: from, until);
write_governed_by (EXECUTION->MATERIAL, share); execution_share (EXECUTION->MATERIAL | LOCATION, share); produced; consumes;
copies_from; contributes_material (share); mutates_from; recombines_with; hosted_by (TRANSFORMATION->BODY); transports
(BODY|ENV->MATERIAL, attrs from/to LOCATION); made_in (MATERIAL->LOCATION); located_in (BODY->LOCATION); member_of (MATERIAL->HU);
member_of_arch (MATERIAL->ARCH, basis); enables (ENV->TRANSFORMATION); via (TRANSFORMATION->EXECUTION);
tests (CF_TEST->TRANSFORMATION); labelled_parent (IDENTITY->IDENTITY, native, never heredity).

Ancestry follows ONLY copies_from and contributes_material. Nothing else is heredity: made_in, located_in, hosted_by,
assigned, labelled_parent, execution_share, member_of_arch and CF_TEST results are not.

## 4. Per-transformation fields (each with basis TRACE | REPLAY | NATIVE_RECORD | DERIVED | DECLARED)
- `ancestry_origin` (per output material; WHOSE): RANDOM_INIT, RANDOM_INFLOW, INSERTED_SEED, TRANSPLANT, MUTATION,
  RECOMBINATION, COPY, COMPUTED, UNKNOWN.
- `made_in` (WHERE; optional, via the made_in edge): independent of ancestry.
- `executor_body` / `executor_identity`: ref | NONE | NOT_IDENTIFIABLE.
- `write_governing` (B3): which material's execution governed the heritable writes, with shares; `execution_share` (B3): where
  execution steps occurred. Both are optional; neither may be derived from the other (J8).
- `factual_contributors` (B5): materials or HUs that flowed into the realized output, with shares and granularity.
- `host_body` (B2): the BODY that supplied locus, execution opportunity or scaffold without (necessarily) contributing material.
- `hu_continuity` (B1): which prior HU the output CONTINUES under the declared rule: ref | NONE (a new unit) | NOT_APPLICABLE |
  NOT_IDENTIFIABLE | ILL_POSED.
- `resulting_hu` (B1): the HU the output belongs to (a continued HU, a newly originated HU, or the special values).
- `architecture_class` (B1): ARCH ref | NOT_APPLICABLE | NOT_IDENTIFIABLE | ILL_POSED.
- `env_dependencies`: ENV refs | NONE_FOUND (tested) | NOT_IDENTIFIABLE (untested).
- Counterfactual results live ONLY in CF_TEST nodes linked by `tests`, never in a field (J10).

Autonomy is defined per role and never bare:
- AUTONOMY_WRITE: write_governing is the executor body's own carried material (share >= the declared threshold).
- AUTONOMY_EXEC: execution_share is majority own.
- AUTONOMY_MATERIAL: factual_contributors majority own.
A property named `autonomous` without a role suffix is rejected (J9).

## 5. Declared rules (per adapter; part of the graph's meta)
- `hu_rule`: how continuity is decided. Examples: `MAJORITY(threshold=0.5, tie=ILL_POSED, no_majority=ILL_POSED | ORIGINATE)`,
  or `PRIVILEGED_PARENT` (the engine names a mother). hu_continuity and resulting_hu are computed from factual_contributors
  under this rule, never from resemblance.
- `arch_rules`: for each ARCH kind used: `exact | equivalence | behavioral | structural`, the criterion (a function name), and a
  justification. Sequence similarity is never a default criterion.
- `granularity`: of material claims.

## 6. Establishment
An ESTABLISHMENT transformation must carry `persisting_object` = an HU, an ARCH, or a declared other heritable object (with its
kind). A bare "established" is rejected (J13). Counting is per persisting object (J12).

## 7. Counterfactual tests (B5)
CF_TEST {subject: MATERIAL | BODY | HU | ENV ref, kind: SUFFICIENCY | NECESSITY, intervention: {name, params}, outcome: {predicate},
result: TRI, basis: REPLAY, draws?}. The intervention and the outcome are REQUIRED (J11). A factual contributor may fail a
SUFFICIENCY test, and a non-contributor may pass one. Neither is a contradiction, and the validator never "resolves" one.

## 8. Body and identity (B2)
IDENTITY -assigned-> BODY over [from, until) events. A rename is a new IDENTITY assigned to the SAME BODY. A replacement body gets a
new BODY. An identity inherited by a new body is representable (the same IDENTITY assigned to a second BODY). host_body,
executor_body and carries always reference BODY. IDENTITY is for labels, native parents and cross-reference only (J14, J15).

## 9. Invariants v0.2
Carried from v0.1 (I-number in brackets), then new ones.

| id | invariant |
|---|---|
| J1 [I1] | inserted or transplanted ancestry never becomes spontaneous by relabelling |
| J2 [I2] | host_body is a contributor only through an explicit contributes/copies edge from material it carries |
| J3 [I3] | executor_body is a contributor only through such an edge |
| J4 [I4] | ancestry_origin of an output is inherited from its heritable sources unless this transformation originates, mutates, computes or transplants it |
| J5 [I5,I6,I7] | mutation = new material with mutates_from; recombination keeps every native contributor; transplant keeps donor ancestry |
| J6 [B1] | ILL_POSED only in identity-valued fields, only with an `ill_posed` justification whose evidence is complete; incomplete evidence must be NOT_IDENTIFIABLE |
| J7 [B1] | when hu_continuity is ILL_POSED, no singular continuity may be asserted: resulting_hu must not name a PRE-EXISTING HU, and no heritable edge may be labelled as "the" continuation |
| J8 [B3] | write_governing is never derived from execution_share (basis source may not be `execution_share`) |
| J9 [B3] | no bare `autonomous`; a role suffix is required |
| J10 [B5] | factual_contributors never has a counterfactual basis; counterfactual claims exist only as CF_TEST nodes |
| J11 [B5] | a CF_TEST without a named intervention and outcome is invalid; bare sufficient/necessary properties are rejected |
| J12 [I8] | establishment is counted once per persisting object |
| J13 [B1] | ESTABLISHMENT requires persisting_object of kind HU, ARCH or declared-other |
| J14 [B2] | host_body / executor_body / carries reference BODY, never IDENTITY |
| J15 [B2] | identity reassignment never breaks body continuity: a body that is renamed keeps one BODY node across the rename |
| J16 [B4] | made_in / located_in never support ancestry: no heritable edge has basis `location`, and origins() never reads LOCATION |
| J17 [B1] | architecture continuity never substitutes for HU continuity: hu_continuity / resulting_hu may not reference an ARCH |
| J18 [I10,I12] | NOT_IDENTIFIABLE is never coerced to NO; claim granularity is never finer than the basis granularity; parent ids never support material-granularity contributors |
| J19 [I9] | AMPLIFICATION/REPRODUCTION never create an HU; ORIGINATION does |
| J20 [I11] | labelled_parent is never read by any query or count |

## 10. Modes
LIGHT / FULL unchanged in principle (OBSERVATORY_DESIGN.md, v0.2 section). FULL is the only mode that may emit CF_TEST nodes
with basis REPLAY.
