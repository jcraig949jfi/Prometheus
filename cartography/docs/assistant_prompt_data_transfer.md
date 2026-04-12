# Assistant Task: Data Transfer + Verification for Blocked Tests
## Machine: Whichever has access to C:\prometheus_share (M2) or Z:\ drive (M1)
## Priority: MEDIUM — unblocks 2 tests, verifies data completeness

---

## Context

Project Prometheus runs on two machines:
- **M1 (Skullport):** `F:\Prometheus`, share mount at `Z:\` (maps to `\\SPECTREX5\prometheus_share`)
- **M2 (SpectreX5):** `D:\Prometheus`, share at `C:\prometheus_share`

Some datasets exist on the share but aren't in the right place on M2. Your job is to copy specific files and verify data integrity.

**Read `CLAUDE.md` at the repo root for security rules (never read key files).**

---

## Task 1: Copy space group data to M2

**Problem:** `cartography/spacegroups/` directory is completely empty on M2. Tests need `space_groups.json` with fields like `number`, `symbol`, `point_group_order`, `wyckoff_positions`, `crystal_system`.

**What to do:**
1. Check if `C:\prometheus_share\cartography\spacegroups\` has the data (on M2)
2. If not, check if there's a space group JSON anywhere in the share or repo under different names (`space_groups.json`, `spacegroups.json`, `bilbao_*.json`)
3. If found: copy to `D:\Prometheus\cartography\spacegroups\data\space_groups.json`
4. If not found: the data may need to be generated. Check `cartography/shared/scripts/` for any script that fetches or generates space group data. The Bilbao Crystallographic Server is the source.
5. Verify: print the number of space groups (should be 230), sample of fields

**Unblocks:** 2 cross-domain tests (SG-Wyckoff correlation, SG point group-NF degree overlap)

---

## Task 2: Verify M2 has all datasets M1 needs

**Problem:** M1 is running 28 tests that need knot, EC, number field, and Fungrim data. We need to confirm M1 has all the data files it needs.

**What to do:**
1. On the machine you're running on, check that these files exist and have content:
   - `cartography/knots/data/knots.json` (should be ~2.8MB, 12,965 knots)
   - `cartography/number_fields/data/number_fields.json` (should be ~1.8MB, 9,116 fields)
   - `cartography/fungrim/data/fungrim_formulas.json` (may not exist yet — Task 3 of the other assistant creates it)
   - `cartography/findstat/data/findstat_index.json` or `findstat_enriched.json`
   - `charon/data/charon.duckdb` (should be ~1.2GB, contains EC + MF tables)
2. For any missing file, check if it exists on the share and copy it
3. Report what's present and what's missing with file sizes

---

## Task 3: Verify cross-machine data consistency

**What to do:**
1. Check that `cartography/genus2/data/genus2_curves_full.json` exists and has 66,158 curves
2. Check that `cartography/isogenies/data/graphs/` has 3,240 prime subdirectories
3. Check that `cartography/maass/data/maass_with_coefficients.json` has 14,995 forms
4. Check that `cartography/convergence/data/` has the genocide result JSONs (genocide_results.json through genocide_r7_results.json)
5. Report any files that are missing or suspiciously small (may indicate incomplete copies)

---

## Task 4: Check what data M1 is missing that M2 has

**What to do:**
1. Read `cartography/docs/m1_data_needs_20260412.md` if it exists — this may already list what M1 needs
2. On M2, check these specific data files that M1's tests may need:
   - `cartography/physics/data/superconductors/3DSC/superconductors_3D/data/source/SuperCon/raw/Supercon_data_by_2018_Stanev.csv` (16K rows)
   - `cartography/physics/data/superconductors/cod_spacegroup_crossmatch.csv` (304 rows — COD replication data)
   - `cartography/physics/data/superconductors/aflow_canonical_superconductors.csv` (2012 rows — AFLOW data)
3. If these exist on M2 but not on the share, copy them to `C:\prometheus_share\cartography\physics\data\superconductors\` so M1 can access them
4. Report what was copied and sizes

---

## Where to put results

- Space groups: `cartography/spacegroups/data/space_groups.json` on whichever machine you're on
- Cross-validation data: `C:\prometheus_share\cartography\physics\data\superconductors\` (for M1 to pick up)
- No need to commit data files to git (they're gitignored). Just place them in the right directories.
- **Do commit** any scripts you write to fetch/transform data.

**Report:** Write a brief summary of what you found/copied to `cartography/docs/data_transfer_report_20260412.md` and commit+push it so both machines know the state.
