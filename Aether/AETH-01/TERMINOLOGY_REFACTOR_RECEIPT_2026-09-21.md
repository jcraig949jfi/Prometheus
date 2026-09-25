# AGE / Aether — Computational Terminology Refactor Receipt

Date: 2026-09-22
Session: nomenclature/refactoring only — no physics change, no RunPod calls.

## Starting HEAD

`694440ac5f0e89d4c9e30b816bc8d430eca8bc42`
(branch `aether/base-role-adopt-2026-09-19`, verified before any edits)

---

## Stranded Review04 preservation

`Aether/AETH-01/INDEPENDENT_CLOSURE_REVIEW_04.md` was found as an
untracked (untracked = uncommitted) file. Its bytes were NOT modified by
this session. SHA-256 before and after: unchanged.

SHA-256: `C615455665627C90A886CCAA925B02A921D947E99155066212B584A1B3986BE9`
Size: 15801 bytes

The file is preserved as a new commit in this branch (untracked → added).
The scientific/engineering finding it documents (the cleanup worker
exact-owned-ID gap) is neither repaired nor altered here.

---

## Files changed

### New files added
- `Aether/AETH-01/COMPUTATIONAL_TERMINOLOGY.md` — authoritative contract
- `Aether/AETH-01/INDEPENDENT_CLOSURE_REVIEW_04.md` — stranded Review04, committed unchanged
- `Aether/test/test_aeth01_terminology_audit.py` — automated audit linter

### Modified active source (45 files in total)
- `Aether/AETH-01/ADVERSARIAL_ANALYSIS.md`
- `Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md`
- `Aether/AETH-01/CLEANUP_EVIDENCE_MODEL.md`
- `Aether/AETH-01/DECISIONS.md`
- `Aether/AETH-01/ECONOMICS.md`
- `Aether/AETH-01/EXPERIMENTS.md`
- `Aether/AETH-01/GPU_RUNPOD.md`
- `Aether/AETH-01/HABITABILITY.md`
- `Aether/AETH-01/HEREDITY_REQUIREMENTS.md`
- `Aether/AETH-01/KILL_GATES_01.md`
- `Aether/AETH-01/OBSERVATORY.md`
- `Aether/AETH-01/PHYSICS_CANDIDATES.md`
- `Aether/AETH-01/PHYSICS_SPEC_DRAFT.md`
- `Aether/AETH-01/REQUIREMENTS.md`
- `Aether/AETHER_CONCEPT.md`, `AETHER_DECISIONS.md`, `AETHER_DOCTRINE.md`
- `Aether/AETHER_OPEN_QUESTIONS.md`, `AETHER_SPEC.md`, `AETHER_TEST_PLAN.md`
- `Aether/production/aeth00.py`
- `Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py`
- `Aether/runpod/aeth01_canary/cleanup_evidence.py`
- `Aether/runpod/aeth01_canary/image_manifest.json` (regenerated after source changes)
- `Aether/runpod/aeth01_canary/README.md`
- `Aether/runpod/aeth01_canary/receipt_schema.json`
- `Aether/runpod/aeth01_canary/run_canary.py`
- `Aether/test/reference/gpu_aeth01.py`
- `Aether/test/reference/mutants.py`
- `Aether/test/reference/oracle.py`
- `Aether/test/reference/oracle_aeth01.py`
- `Aether/test/reference/scientific_aeth01.py`
- `Aether/test/test_aeth01_age_controller.py`
- `Aether/test/test_aeth01_canary_parity.py`
- `Aether/test/test_aeth01_cleanup_evidence.py`
- `Aether/test/test_aeth01_gpu_differential.py`
- `Aether/test/test_aeth01_kill_gates.py`
- `Aether/test/test_aeth01_properties.py`
- `Aether/test/test_differential_oracle.py`
- `Aether/test/test_golden_vectors.py`
- `Aether/test/test_mutants.py`
- `Aether/test/test_production_conformance.py`
- `Aether/test/test_production_differential.py`
- `Aether/test/test_properties.py`
- `Aether/test/test_spec_inventory.py`
- `Aether/test/test_statistical_diagnostics.py`

---

## Terminology mapping applied

| Was | Now (active surface) |
| --- | -------------------- |
| cell / cells | site / sites |
| organism | assembly |
| genome | executable configuration |
| heredity (prose) | configuration transmission |
| heritable | transmissible |
| HEREDITY_VARIATION | TRANSMITTED_VARIATION (canonical); see frozen aliases below |
| reproduction | recursive construction |
| offspring | successor |
| lineage | causal provenance |
| population | ensemble |
| mutation (prose) | perturbation |
| mutated | perturbed |
| dormant | inactive |
| survive / survival | persist / persistence |
| fitness | evaluation score |
| ecology | resource regime |
| metabolic ecology | resource-maintenance regime |
| parasite | asymmetric resource dependence |
| copier (deprecated standalone) | state copier |
| self-copying | recursive state copying |
| specimen | observed instance |
| kill gate (prose) | falsification gate / rejection gate |

---

## Compatibility aliases retained (Category B)

| Identifier | Role | Status |
| ---------- | ---- | ------ |
| `MUT_NUMER` / `mut_numer` | Python param + receipt JSON key | Unchanged wire name |
| `HEREDITY_VARIATION` | claim-tier string in `CLAIM_TIERS` | Frozen; equality alias = `TRANSMITTED_VARIATION` |
| `cell_starved` | engine trace event token | Unchanged |
| `mutation_applied` | engine trace event token | Unchanged |
| `HEREDITY_REQUIREMENTS.md` | filename | Retained; title neutralized |
| `KILL_GATES_01.md` | filename | Retained; title notes falsification gates |
| `semantics_id = "aeth01.v1"` | receipt identity | Unchanged |

`scientific_aeth01.py` now exports both `TRANSMITTED_VARIATION` and
`HEREDITY_VARIATION` constants plus `CLAIM_TIER_ALIASES` dict.
`CLAIM_TIERS[4]` is `"TRANSMITTED_VARIATION"`. No wire representation
changed; `image_manifest.json` regenerated to reflect source-hash updates.

---

## Historical / immutable files — intentionally untouched

- `ASTRA_REVIEW_01.md`, `ASTRA_CLOSURE_REVIEW_02.md`, `ASTRA_REVIEW_PACKET.md`
- `REPAIR_LEDGER_01.md`
- `REVIEW_PACKET_AGE_CLOSURE_2026-09-21.md`
- `REVIEW_PACKET_CLEANUP_EVIDENCE_2026-09-21.md`
- `REVIEW_PACKET_CLEANUP_REVIEW03_2026-09-21.md`
- `REVIEW_PACKET_R1_ADMISSION_2026-09-21.md`
- `REVIEW_PACKET_REPAIR_01.md`
- `AETH-00_REVIEW.md`, `AETH-00A_RECEIPT.md`, `AETH-00B_RECEIPT.md`
- `INDEPENDENT_CLOSURE_REVIEW_04.md` — committed unchanged; SHA preserved
- `Aether/notes/2026-09-20_raw_notes.md`

---

## Frozen `aeth01.v1` identifiers — intentionally retained

`MUT_NUMER`, `mut_numer`, `cell_starved`, `mutation_applied`,
`HEREDITY_VARIATION` (ladder alias), `semantics_id = "aeth01.v1"`,
receipt field `mut_numer`, `aeth01_cpu_oracle.py` hash fields.

No transition equations, byte layout, arbitration logic, energy
accounting, Mu-trigger behavior, or scientific thresholds were changed.
This is nomenclature only.

---

## Automated audit result

`Aether/test/test_aeth01_terminology_audit.py`

violations: **0** (zero unallowlisted deprecated-metaphor hits on active surface)
allowed: 11 (all `line-allow`; frozen identifiers + preferred phrase uses)

---

## Test results

Full Aether suite: `python -m pytest Aether/test -q --tb=line`

```
982 passed, 5 skipped, 92 subtests passed in 559.67s
```

`git diff --check`: no whitespace errors

Deployment-package manifest regenerated and verified by
`test_aeth01_deployment_package.py`: **7 passed, 2 skipped**.

No semantic behavior change detected. Replay identity unchanged.
GPU/CPU-shaped differential tests: passed (no GPU, numpy_fallback path
exercised, as before this refactor).

---

## Review04 preservation status

SHA-256 before session: `C615455665627C90A886CCAA925B02A921D947E99155066212B584A1B3986BE9`
SHA-256 after session: `C615455665627C90A886CCAA925B02A921D947E99155066212B584A1B3986BE9`
Status: UNCHANGED — committed to branch without modification.
The cleanup-worker exact-ID gap documented therein is neither repaired
nor altered. Review04 closure remains open for the next engineering round.

---

## Remaining terminology debt

None identified on the active surface. The automated audit enforces
forward hygiene: new commits introducing unapproved metaphors will fail
`test_aeth01_terminology_audit.py`.

`AETHER_RUNPOD.md` had no deprecated metaphor hits and was not changed.

---

## Disposition

**TERMINOLOGY_REFACTOR_COMPLETE**
