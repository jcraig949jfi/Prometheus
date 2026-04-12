# Skullport (M1) Data Needs — 2026-04-12

Files missing on M1 that scripts from v10 depend on. Please push to Z:\ (prometheus_share).

## Priority 1 — Blocks 11 scripts (CRITICAL)

```
cartography/physics/data/superconductors/3DSC/   (entire tree)
```

Specifically `3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv` and `Supercon_data_by_2018_Stanev.csv`.

Scripts blocked: `final_classification.py`, `interaction_analysis.py`, `law_deep_analysis.py`, `law_independence.py`, `reaudit_20_findings.py`, `reaudit_genocide_f24.py`, `retest_all_findings.py`, `sg_decomposition.py`, `sg_dimensionality.py`, `stanev_replication.py`, `stress_test_interaction.py`

## Priority 2 — Graceful degradation (scripts have existence checks)

```
cartography/spacegroups/data/space_groups.json
cartography/polytopes/data/polytopes.json
cartography/fungrim/data/fungrim_formulas.json
cartography/mathlib/data/mathlib_imports.json
cartography/mmlkg/data/mmlkg_articles.json
cartography/physics/data/nist_asd/all_elements.json
```

Used by `reaudit_genocide_f24.py` and `reaudit_20_findings.py` with fallbacks.

## Priority 3 — Can regenerate locally (low urgency)

```
cartography/convergence/data/hmf_forms.json
cartography/convergence/data/hmf_fields.json
cartography/convergence/data/hgcwa_passports.json
cartography/convergence/data/hgcwa_passports_g4plus.json
cartography/convergence/data/hgcwa_groups.json
cartography/shared/scripts/known_truth_expansion_results.json
```

These are output targets of `fetch_lmfdb_frontiers.py` or battery runs — can re-fetch. The `_full.json` variants already exist on M1.

## What's fine on M1

- `charon/data/charon.duckdb` — present
- All v2/ intermediate result JSONs — present
- All core datasets (knots, number_fields, genus2, maass, OEIS, lattices, groups, fungrim, etc.) — present
- `cartography/lmfdb_dump/` — present (23 GB)
- AFLOW/COD crossmatch CSVs — present (just committed)
