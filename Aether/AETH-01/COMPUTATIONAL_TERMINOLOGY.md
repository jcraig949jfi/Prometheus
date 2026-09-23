# AGE / Aether — Computational Terminology Contract

Status: AUTHORITATIVE for active AGE source, tests, current requirements,
and current operator documentation.

## Agent prompt statement

> AGE models byte-valued computational sites and causal state
> transformations. Biological metaphors found in historical Aether
> documents are legacy terminology only and do not denote biological
> systems or procedures.

AGE/Aether is a synthetic computational lattice implemented entirely in
software. It contains byte-valued sites, deterministic transition rules,
resource values, state-copy operations, causal provenance, and
computational search. There is no wet-lab work, biological material,
pathogen, genetic material, culturing, laboratory protocol, or real-world
organism manipulation in scope.

This contract removes biology-inspired metaphors from the **active**
surface so generic safety filters do not misclassify pure computation,
and so scientific interpretation is not biased toward familiar biological
categories the machinery has not demonstrated.

This is nomenclature only. It is not a physics change, not a scientific
result, and not a stealth `aeth01.v2`.

## Classification of every occurrence

| Class | Meaning | Action |
| ----- | ------- | ------ |
| A. Free | Internal names, comments, docstrings, test prose, active docs | Rename to neutral term |
| B. Compatibility-sensitive | Public APIs, JSON fields, config keys, schema enums, paths tooling consumes | Neutral canonical + narrow legacy alias |
| C. Historical / immutable | Old reviews, ledgers, receipts, frozen manifests, hash-bound artifacts | Do not rewrite |

## Canonical vocabulary

| Canonical (active) | Deprecated historical metaphor | Compat retained? | Frozen in `aeth01.v1`? | Notes |
| ------------------ | ------------------------------ | ---------------- | ---------------------- | ----- |
| site / lattice site | cell | no (prose); locals free | no | Prefer "site". Keep ordinary engineering "cell" only if non-lattice. |
| assembly / component / region | organism | no | no | |
| assembly_id / component_id | organism_id | alias if ever serialized | no current wire use | |
| executable configuration / instruction state | genome | no | no | |
| configuration transmission / state transmission | heredity | path name retained | no | Active prose uses transmission. Filename `HEREDITY_REQUIREMENTS.md` retained for provenance. |
| transmissible / configuration-transmitted | heritable | no | no | |
| TRANSMITTED_VARIATION | HEREDITY_VARIATION | yes — tier alias | **yes** (claim ladder id) | Human-facing canonical = TRANSMITTED_VARIATION. Wire/tier id HEREDITY_VARIATION remains accepted equality alias. |
| recursive construction / successor construction | reproduction | no | no | |
| recursive-construction / successor-construction | reproductive | no | no | |
| predecessor | parent (lattice) | no | no | Keep OS/FS "parent process", "parent directory". |
| successor | offspring | no | no | |
| causal provenance | lineage | no | no | |
| causal provenance graph | lineage graph | no | no | |
| ensemble / instance cohort | population | no | no | |
| bit perturbation / copy perturbation | mutation | no (prose) | partial | See `MUT_NUMER` / `mut_numer` below. |
| perturbed | mutated | no | no | |
| perturbation event | mutation event | no | no | |
| inactive / latent | dormant | no | no | |
| persistence | survival | no | no | |
| persist | survive | no | no | Keep process-lifecycle "survive" only when clearly non-lattice. |
| evaluation score / performance measure | fitness | no | no | |
| dominate under the resource policy | outcompete | no | no | |
| resource regime / interaction regime | ecology / ecological | no | no | |
| resource-maintenance regime | metabolic ecology | no | no | |
| asymmetric resource dependence | parasite / parasitism | no | no | |
| state copier / constructor | copier | no | no | |
| recursive state copying | self-copying | no | no | |
| observed assembly / observed instance | specimen | no | no | |
| falsification gate / rejection gate | kill gate | path retained | no | Title/prose use falsification gate. Filename `KILL_GATES_01.md` retained. |

## Frozen `aeth01.v1` identifiers (do not silently rewrite)

These names participate in replay identity, receipts, schemas, or
published claim ladders. Behavior and serialized form stay identical.

| Identifier | Role | Human-facing description |
| ---------- | ---- | ------------------------ |
| `semantics_id = "aeth01.v1"` | receipt / engine identity | unchanged |
| `MUT_NUMER` / `mut_numer` | config + receipt JSON field + Python parameter | legacy serialized name for the copy-coupled single-bit perturbation probability numerator over `2^32` |
| `HEREDITY_VARIATION` | formal claim-tier identifier | compatibility alias equal to canonical `TRANSMITTED_VARIATION` |
| `cell_starved` | engine trace event token | historical trace label; denotes a starved lattice site that emits nothing |
| `mutation_applied` | engine trace event token | historical trace label; denotes a Mu bit-perturbation application |
| receipt field `mut_numer` | mismatch records in `receipt_schema.json` | unchanged wire key |

Python may expose neutral module-level aliases (for example
`PERTURB_NUMER =` documentation constant, or
`TRANSMITTED_VARIATION` alongside `HEREDITY_VARIATION`) **only if**
serialized behavior, default parameter names consumed by current tooling,
and hash domains remain unchanged.

## Active vs historical document surface

**Active (must follow this contract):**

- `Aether/AETH-01/PHYSICS_SPEC_DRAFT.md`, `REQUIREMENTS.md`, `ECONOMICS.md`,
  `OBSERVATORY.md`, `HEREDITY_REQUIREMENTS.md`, `KILL_GATES_01.md`,
  `EXPERIMENTS.md`, `HABITABILITY.md`, `GPU_RUNPOD.md`, `DECISIONS.md`,
  `PHYSICS_CANDIDATES.md`, `ADVERSARIAL_ANALYSIS.md`,
  `AETH01_REPAIRED_FREEZE_CANDIDATE.md`, `CLEANUP_EVIDENCE_MODEL.md`,
  `COMPUTATIONAL_TERMINOLOGY.md` (this file)
- `Aether/AETHER_SPEC.md`, `AETHER_CONCEPT.md`, `AETHER_DOCTRINE.md`,
  `AETHER_DECISIONS.md`, `AETHER_OPEN_QUESTIONS.md`, `AETHER_RUNPOD.md`,
  `AETHER_TEST_PLAN.md`
- Active production / reference / canary Python and current operator README
- Active tests under `Aether/test/` (prose, docstrings, names)

**Historical / immutable (do not terminology-edit):**

- `ASTRA_REVIEW_*.md`, `ASTRA_CLOSURE_REVIEW_*.md`, `ASTRA_REVIEW_PACKET.md`
- `REPAIR_LEDGER_01.md`, `REVIEW_PACKET_*.md`
- `AETH-00_REVIEW.md`, `AETH-00A_RECEIPT.md`, `AETH-00B_RECEIPT.md`
- `INDEPENDENT_CLOSURE_REVIEW_04.md` and any stranded Review04 draft
- `Aether/notes/**` raw notes
- Committed experiment receipts, image manifests, hash-bound freezes

When active docs must cite historical vocabulary, mark it explicitly as
historical legacy terminology.

## Path retention policy

| Path | Disposition |
| ---- | ----------- |
| `HEREDITY_REQUIREMENTS.md` | Retain filename (tooling + tests cite it). Neutralize title and body. |
| `KILL_GATES_01.md` | Retain filename. Title becomes falsification/rejection gates. |
| Historical packet filenames | Never rename solely for aesthetic consistency. |

## Preferred descriptive phrasing (bias removal)

Prefer machinery-true descriptions:

- "configuration values are causally transmitted to a successor region"
  — not "offspring inherits a genome"
- "one assembly receives resource from another without measured reciprocal
  structural contribution" — not "parasite"
- "an inactive site's instruction byte persists" — not "dormant machinery
  survives"
- "ensemble-level transmitted variation" — not "population heredity"

## Enforcement

`Aether/test/test_aeth01_terminology_audit.py` scans the active AGE surface
for newly introduced deprecated metaphors and fails on unallowlisted hits.
Allowlists cover historical documents, frozen identifiers, explicit
migration notes, and ordinary engineering senses (`SIGKILL`, `lifecycle`,
`parent directory`, `parent process`).

## Migration notes for implementers

1. Do not change transition equations, byte layout, arbitration, energy
   accounting, Mu trigger behavior, replay identity, or scientific
   thresholds while renaming.
2. New output and new prose use canonical terms.
3. Legacy input aliases remain only where compatibility is required.
4. Quote historical documents unchanged; do not "fix" their wording.
