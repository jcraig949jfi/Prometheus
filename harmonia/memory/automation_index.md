---
name: Automation modules index
purpose: Single table of runners (first-pass executors) + sweeps (automated epistemic discipline). Closes axis-6 sprawl observation (runners/ and sweeps/ as parallel automation systems with no consolidated index).
owner: sessionA (axis-6 strawman) — happy to hand off to Ergon/Techne on claim
status: v1.0 — regenerate when new runners or sweeps ship; current as of 2026-04-23
---

# Automation modules index

Two parallel automation systems ship under `harmonia/`:

- **`harmonia/runners/`** — reusable first-pass executors for generator work, audits, probes, and regeneration tasks
- **`harmonia/sweeps/`** — automated epistemic-discipline modules (Pattern 30/20/19 auto-sweeps + override protocol)

Runners produce substrate content (new tensor cells, registry entries, probe outputs); sweeps filter substrate content (block/warn/clear verdicts on promoted content). Both emit sync events to `agora:harmonia_sync` — future consolidation (axis-6 #10) proposes dedicated streams per event class.

---

## `harmonia/runners/` — first-pass executors (13 modules)

### Generator runners

| Module | Purpose | Events emitted | Status |
|---|---|---|---|
| `gen_03_transfer_matrix.py` | Cross-domain projection transfer matrix (P × D cells as tasks) | `TRANSFER_MATRIX_SHIPPED` | First pass shipped 2026-04-20; 30 tasks seeded |
| `gen_05_attention_replay.py` | Re-test every killed F-ID against every new projection | `ATTENTION_REPLAY_SHIPPED` | First pass shipped 2026-04-20; 30 tasks seeded |
| `gen_07_literature_diff.py` | Measured-vs-claimed delta per incoming paper | `LITERATURE_DIFF_SHIPPED` | First pass shipped 2026-04-20; 8 tasks seeded |
| `gen_log_builder.py` | Compact generator activity log builder | — | Utility module; used by other runners |
| `null_family.py` | gen_02 null-family seed + family-vector schema | `NULL_FAMILY_SEED_COMPLETE` | Ran 2026-04-20; 4 `NULL_*` operators + SIGNATURE@v2 promoted |

### Audit runners

| Module | Purpose | Results path | Status |
|---|---|---|---|
| `audit_F041a_euler_deflation.py` | F041a Euler-product deflation audit | `cartography/docs/audit_F041a_*.json` | Auditor 2026-04-22 |
| `audit_F045_multiple_testing.py` | F045 multiple-testing + independence check | `cartography/docs/audit_F045_*.json` | Auditor 2026-04-22 |

### Probe runners

| Module | Purpose | Model | Result path |
|---|---|---|---|
| `probe_gemini_lens_candidates.py` | Brainstorm cross-disciplinary lens candidates for methodology_toolkit | gemini-2.5-flash | `cartography/docs/probe_gemini_lens_candidates_results.md` |
| `probe_gemini_v11_definitions.py` | Stress-test v2 classifier definitions | gemini-2.5-flash | `cartography/docs/probe_gemini_v11_definitions_results.md` |
| `probe_gemini_scorer_tractability.py` | Scorer-tractability check for 4 STRONG lens candidates | gemini-2.5-flash → gpt-4o-mini fallback | `cartography/docs/probe_gemini_scorer_tractability_results.md` |

See `harmonia/memory/probes_register.md` for the full probe inventory.

### Regeneration runners

| Module | Purpose | Target artifact | Re-run trigger |
|---|---|---|---|
| `regen_audit_results_index.py` | Auto-generate audit results index | `harmonia/memory/audit_results_index.md` | When new `cartography/docs/audit_*` artifacts land |
| `regen_pattern_library_tier_index.py` | Auto-generate Pattern library tier-index table | `harmonia/memory/pattern_library.md` top table | When new Patterns are drafted or promoted |
| `regen_decisions_index.py` | Auto-generate decisions_for_james tagged-index | `harmonia/memory/decisions_for_james.md` top table | When new entries land |

All regeneration runners are idempotent + fast; safe to re-run on each tick if desired.

---

## `harmonia/sweeps/` — automated epistemic discipline (6 modules + tests)

### Pattern sweep modules

| Module | Purpose | Graded-level schema | Events emitted |
|---|---|---|---|
| `pattern_30.py` | Algebraic-identity coupling detection (F043-class failure mode filter) | 0 CLEAN / 1 WEAK_ALGEBRAIC / 2 SHARED_VARIABLE / 3 REARRANGEMENT / 4 IDENTITY | `PATTERN_30_BLOCK`, `PATTERN_30_WARN` |
| `pattern_20.py` | Pooled-vs-stratified divergence + sign agreement + small-n | CLEAR / WARN / BLOCK | `PATTERN_20_WARN`, `PATTERN_20_BLOCK` |
| `pattern_19.py` | Stale/irreproducible tensor entry — symmetric effect-size ratio + z sign flip | CLEAR / WARN | `PATTERN_19_WARN` |

### Runner + infrastructure

| Module | Purpose | Called by |
|---|---|---|
| `runner.py` | Composite verdict (BLOCK > PROVISIONAL > WARN > CLEAR); override with recorded justification | `agora.register_specimen.register()` + `agora.tensor.push.push_tensor()` |
| `retrospective.py` | LINEAGE_REGISTRY (4-type taxonomy: algebraic_lineage / frame_hazard / killed_no_correlation / non_correlational) + retrospective runner | Pre-promotion audit; regenerates `lineage_registry_view.md` per auditor consolidation |
| `__init__.py` | Package init | |

### Override discipline

- `harmonia/sweeps/OVERRIDE_PROTOCOL.md` — 4 legitimate override reasons; recorded-justification discipline (silent bypass forbidden)
- Override events currently post to `agora:harmonia_sync`; dedicated `agora:override_log` stream is candidate consolidation per axis-6 #10 + auditor axis-1 #8

### Test coverage

- `test_sweeps.py` — 14 tests, all green as of 2026-04-20 commit `751dfc64`
- F043 is the headline BLOCK regression test

---

## Composition map

- **`agora.register_specimen.register()`** → `sweeps.runner.run_all()` → BLOCK raises `SweepBlocked`; WARN/CLEAR proceed
- **`agora.tensor.push.push_tensor()`** → on cell promotion (0 → +1/+2), checks LINEAGE_REGISTRY → pattern_30.classify_entry → emits BLOCK events on PROVISIONAL/WARN/BLOCK without halting the batch
- **`retrospective.py::resolve_entry()`** → returns per-F-ID classification; used by auditor's `regen_audit_results_index.py` + sessionA's `anchor_progress.py` future extension
- **`agora.symbols.anchor_progress`** (sessionA 2026-04-23) — adjacent mutable sidecar pattern; composes with sweeps at the symbol-metadata layer rather than the specimen-content layer

## Promotion criterion (harmonia/tmp → harmonia/runners)

Per axis-6 consolidation #6 (proposed): if a `harmonia/tmp/` script is (a) imported by another file, OR (b) executed > 2 times, OR (c) produces a tensor/symbol mutation, it is promoted to `runners/` by its author with a header block naming its intended reuse pattern. Not yet formalized as written rule; add to `harmonia/memory/promotion_workflow.md` or similar when next tmp→runners promotion happens.

---

## Related files

- `harmonia/memory/generator_pipeline.md` — 11-generator DAG + Tier status (source-of-truth for generator roster)
- `docs/prompts/README.md` — generator spec index (16 prompt files)
- `harmonia/memory/probes_register.md` — external-LLM probe register (source-of-truth for probe runs)
- `harmonia/memory/pattern_library.md` — Pattern 1-30 (source-of-truth for pattern definitions; sweeps operationalize)
- `harmonia/sweeps/OVERRIDE_PROTOCOL.md` — override discipline
- `agora/README.md` — agora package function index (sweep modules call into agora helpers)

---

## Version history

- **v1.0** 2026-04-23 (sessionA axis-6 strawman, consolidation #5) — initial index. 13 runners + 6 sweep modules + 1 test file indexed with purpose + events + status per module. Closes axis-6 sprawl observation about runners/sweeps/ no consolidated index. Regenerable by re-globbing + re-reading docstrings.
