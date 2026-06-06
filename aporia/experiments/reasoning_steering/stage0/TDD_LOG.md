# Stage 0 — TDD quality log

Format: `date | operation | A:authority P:property E:edge C:composition | commit`

2026-06-06 | hodge.hodge_decompose | A:3 P:2 E:2 C:2 | a5619bac
2026-06-06 | controls.no_cycle_graph + planted_cycle_graph | A:2 P:2 E:1 C:2 | 774ab6f5
2026-06-06 | controls.planted_hole_graph | A:1 P:1 E:1 C:1 | a1e7d500
2026-06-06 | controls.operator_artifact_graph + nulls.* | A:2 P:3 E:1 C:3 | 73e5ad49
2026-06-06 | nulls.endpoint_permutation + emitter_family_holdout | A:2 P:2 E:1 C:2 | d452c1d1
2026-06-06 | localization.localized_rank (H-R2 freeze) | A:3 P:1 E:1 C:2 | (this commit)
