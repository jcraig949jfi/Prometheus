# Worker Prompts

Persistent record of task prompts delegated to worker sessions. Each file is a self-contained role specification that can be pasted into a fresh Claude Code session on any machine.

Committed so that:
1. The delegation record is auditable (who was asked to do what, when)
2. Prompts become re-runnable if a worker instance is lost
3. External reviewers can see the full task spec, not just the resulting commit
4. The prompt itself is a versioned artifact; edits create a new file

**Note:** the `docs/` tree is globally gitignored. New prompt files require `git add -f`. This convention preserves rapid iteration on drafts while committing finalized prompts explicitly.

**Naming conventions:**
- `gen_NN_<short_name>.md` — generator specs (NN = two-digit index in `generator_pipeline.md`)
- `track_<letter>_<short_name>.md` — track-level research/methodology prompts
- `<descriptive_name>.md` — sprint-level multi-sub-task prompts (e.g., `materialization_sprint_*`)

---

## Generator specs (from `harmonia/memory/generator_pipeline.md`)

| # | File | Role | Tier | Status |
|---|---|---|---|---|
| 1 | [gen_01_map_elites_on_probes.md](gen_01_map_elites_on_probes.md) | Meta-allocator (quality-scoring across probes) | Tier 2 | Spec shipped; waits on gen_02 + gen_06 live + ≥50 probes corpus |
| 2 | [gen_02_null_family.md](gen_02_null_family.md) | Filter+Enricher (add 3–4 nulls to catalog; family-vector schema) | Tier 1 | First pass shipped 2026-04-20; 4 NULL_* operators + SIGNATURE@v2 promoted |
| 3 | [gen_03_cross_domain_transfer.md](gen_03_cross_domain_transfer.md) | Producer (port each projection to every other domain) | Tier 0 | First pass shipped 2026-04-20; 30 tasks queued |
| 4 | [gen_04_representation_invariance.md](gen_04_representation_invariance.md) | Enricher (representation invariance matrix per object class) | Tier 2 | Spec pending |
| 5 | [gen_05_attention_replay.md](gen_05_attention_replay.md) | Producer (every killed F-ID re-tested against every new projection) | Tier 0 | First pass shipped 2026-04-20; 30 tasks queued |
| 6 | [gen_06_pattern_autosweeps.md](gen_06_pattern_autosweeps.md) | Filter MANDATORY — auto Pattern 30/20/19 sweeps | Tier 1 | LIVE 2026-04-20 commit `751dfc64`; rides along every other generator |
| 7 | [gen_07_literature_diff.md](gen_07_literature_diff.md) | Producer (measured-vs-claimed delta per incoming paper) | Tier 0 | First pass shipped 2026-04-20; 8 tasks queued |
| 8 | [gen_08_synthetic_data_sensitivity.md](gen_08_synthetic_data_sensitivity.md) | Enricher (detection-rate profiling infra) | Tier 2 | Spec pending |
| 9 | [gen_09_cross_disciplinary_transplants.md](gen_09_cross_disciplinary_transplants.md) | Producer (physics/CS/stats vocabulary imports) | Tier 1* | Spec shipped 2026-04-20 commit `d9bb706b`; seed at priority −1.6; methodology_toolkit.md is the shelf |
| 10 | [gen_10_composition_enumeration.md](gen_10_composition_enumeration.md) | Producer (operator composition with info-gain scoring) | Tier 1 | First pass shipped 2026-04-20 evening; 36 compositions, top-10 seeded |
| 11 | [gen_11_coordinate_invention.md](gen_11_coordinate_invention.md) | Producer (axis-space — proposes new P-IDs from tensor demand signals) | Tier 2 | DRAFT shipped 2026-04-20; blocked on Definition DAG Phase 0 + AXIS_CLASS tagging audit |

See `harmonia/memory/generator_pipeline.md` (v1.1) for the full dependency DAG and the substrate-primitive Definition DAG spec.

---

## Track-level prompts

| File | Track | Status |
|---|---|---|
| [track_A_methodology_tightener.md](track_A_methodology_tightener.md) | Null-protocol + algebraic-identity audit discipline | Completed 2026-04-19; led to PATTERN_30 graded severity |
| [track_B_F011_unfolding.md](track_B_F011_unfolding.md) | F011 rank-0 residual independent-unfolding check | Completed 2026-04-19; EPS011@v2 shipped with `independent_unfolding_audit: SURVIVES` |
| [track_D_replication.md](track_D_replication.md) | NULL_BSWCD@v2 clean-room reimplementation + F011 replication pilot | Zaremba Track D success 2026-04-22 (sessionC re-impl of sessionB measurement); F011 Track D deferred pending Sage host |
| [track_E_snapshot_Q_EC_R0_D5.md](track_E_snapshot_Q_EC_R0_D5.md) | Capture `Q_EC_R0_D5@v2` snapshot per `dataset_snapshot_v1.md` | Spec ready; needs LMFDB credentials |

---

## Sprint-level prompts

| File | Scope | Required qualification | Status |
|---|---|---|---|
| [materialization_sprint_kodaira_moddeg_euler.md](materialization_sprint_kodaira_moddeg_euler.md) | Materialize 3 LMFDB-derivable quantities (Kodaira per prime, `modular_degree`, truncated Euler product p≤200) into prometheus-side shadow schema | `ergon_or_techne` | Seeded on Agora at priority −1.5 by sessionD 2026-04-22 |

---

## Retirement policy

Completed tracks/sprints stay in this directory for the audit trail. If a prompt is reassigned with a new spec, preserve the original:
1. Add `SUPERSEDED_BY: <new_file>.md` at the top of the original
2. Add `SUPERSEDES: <old_file>.md` at the top of the new file
3. Optionally move the superseded file to `archive/` once the successor ships

Sprint-level prompts may add a `COMPLETED_AT: <commit>` or `CLAIMED_BY: <worker>` header as they progress; per-sub-task status within a sprint lives in the sprint body.

---

## Re-use as Agora task payloads

Prompts here are designed to be compatible with `agora.helpers.seed_task()` — the spec MD's frontmatter + body map cleanly to the `spec` / `goal` / `acceptance` / `required_qualification` fields the helper enforces. See `agora/helpers.py::seed_task` for the schema.

---

## Version history

- **v2.0** 2026-04-23 (sessionA axis-6 strawman, consolidation #4) — expanded stub (gen specs + track + sprint index) with status per file. Closes axis-6 sprawl observation #1 (generator specs in gitignored docs/prompts; cold-start discoverability).
- **v1.0** 2026-04-17 — initial stub covering track_A + track_B only.
