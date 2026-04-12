# Data Transfer Report — 2026-04-12
## Machine: M2 (SpectreX5)

### Task 1: Space group data — GENERATED + DEPLOYED

- `cartography/spacegroups/data/space_groups.json` — **generated** from spglib + pymatgen
- 230 space groups, 11 fields each (number, symbol, international_full, schoenflies, hall_symbol, point_group, point_group_order, crystal_system, is_symmorphic, lattice_type, arithmetic_crystal_class)
- Crystal system distribution: tetragonal 68, orthorhombic 59, cubic 36, hexagonal 27, trigonal 25, monoclinic 13, triclinic 2
- Generation script: `cartography/spacegroups/generate_space_groups.py`
- Copied to share: `C:\prometheus_share\cartography\spacegroups\data\space_groups.json` (81 KB)
- **Unblocks**: SG-Wyckoff correlation test, SG point group-NF degree overlap test

### Task 2: M2 data file verification

| File | Status | Size |
|------|--------|------|
| `cartography/knots/data/knots.json` | PRESENT | 2.8 MB (12,965 knots) |
| `cartography/number_fields/data/number_fields.json` | PRESENT | 1.8 MB (9,116 fields) |
| `cartography/fungrim/data/fungrim_formulas.json` | PRESENT | 1.6 MB |
| `cartography/findstat/data/findstat_enriched.json` | PRESENT | 198 KB |
| `cartography/findstat/data/findstat_index.json` | PRESENT | 40 KB |
| `charon/data/charon.duckdb` | PRESENT | 1.1 GB |

All needed data files present on M2.

### Task 3: Cross-machine data consistency

| Dataset | Expected | Actual | Status |
|---------|----------|--------|--------|
| genus2_curves_full.json | 66,158 curves | 66,158 | OK |
| isogenies/data/graphs/ | 3,240 prime subdirs | 3,240 | OK |
| maass_with_coefficients.json | 14,995 forms | 14,995 | OK |
| genocide_results.json | present | present | OK |
| genocide_r2 through r7 | present | all 6 present | OK |

All cross-machine data consistent.

### Task 4: Data copied to share for M1

**P1 — Critical (unblocks 11 scripts):**
- `3DSC/` entire tree (106 MB) -> `C:\prometheus_share\cartography\physics\data\superconductors\3DSC\`
  - Includes `3DSC_MP.csv` and `Supercon_data_by_2018_Stanev.csv`
- COD crossmatch and AFLOW CSVs were already on share (copied in earlier commit)

**P2 — Graceful degradation files pushed to share:**
- `space_groups.json` (81 KB) -> share
- `polytopes.json` (231 KB) -> share
- `fungrim_formulas.json` (1.6 MB) -> share
- `all_elements.json` (7.5 MB, NIST ASD) -> share

**Still missing on both machines:**
- `mathlib_imports.json` — not generated yet
- `mmlkg_articles.json` — not generated yet

These are P2 with fallbacks in scripts, so not blocking.
