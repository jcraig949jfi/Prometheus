# Stage 0 — TDD quality log

Format: `date | operation | A:authority P:property E:edge C:composition | commit`

2026-06-06 | hodge.hodge_decompose | A:3 P:2 E:2 C:2 | a5619bac
2026-06-06 | controls.no_cycle_graph + planted_cycle_graph | A:2 P:2 E:1 C:2 | 774ab6f5
2026-06-06 | controls.planted_hole_graph | A:1 P:1 E:1 C:1 | a1e7d500
2026-06-06 | controls.operator_artifact_graph + nulls.* | A:2 P:3 E:1 C:3 | 73e5ad49
2026-06-06 | nulls.endpoint_permutation + emitter_family_holdout | A:2 P:2 E:1 C:2 | d452c1d1
2026-06-06 | localization.localized_rank (H-R2 freeze) | A:3 P:1 E:1 C:2 | ad4745aa
2026-06-06 | runner.run_controls_0a (0a gate) | A:1 P:1 E:1 C:1 | e532d37a

# Stage 0b
2026-06-06 | stage0b.damage.Axis2DamageScorer | A:2 P:2 E:1 C:1 | dca44d22
2026-06-07 | stage0b.margins_from_kill_vector + margin_vector | A:2 P:1 E:1 C:1 | d6c625ce
2026-06-07 | stage0b.corpus.load_in_band_states | A:1 P:1 E:1 C:1 | d6c625ce
2026-06-07 | stage0b.flow.relational_flow (Condorcet keystone) | A:2 P:1 E:1 C:1 | d6c625ce
2026-06-07 | stage0b.cache.score_states | A:1 P:1 E:1 C:1 | 3d17220b
2026-06-07 | stage0b.relational_nulls.* | A:1 P:2 E:1 C:1 | 3d17220b
2026-06-07 | stage0b.runner.run_h_r1 | A:1 P:1 E:1 C:1 | 3d17220b
2026-06-07 | stage0b.g2c_corpus.load_g2c_states + criteria-adequacy guard | A:1 P:1 E:1 C:1 | 34446a19
2026-06-08 | stage0b.prescreen.signal_screen (fast curl gate) | A:2 P:1 E:1 C:1 | f37ef5d4
2026-06-08 | stage0b.calibration (relational positive control) | A:2 P:0 E:1 C:1 | (this commit)
