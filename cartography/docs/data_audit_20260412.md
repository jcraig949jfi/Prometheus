# Prometheus Science Data Audit — 2026-04-12

## Executive Summary

| Area | Size | Files | Primary Format |
|------|------|-------|----------------|
| **cartography/** | 152 GB | ~100K | JSON, CSV, TXT, CIF |
| **charon/** | 27 GB | ~5,500 | DuckDB, PKL, JSON |
| **Prometheus_data_backup/** | 36 GB | — | Duplicates |
| **Total science data** | **~215 GB** | **~106K** | Mixed |

Top-level storage drivers:
- `cartography/convergence/` — **125 GB** (analysis pipeline outputs)
- `charon/james_downloads/` — **23 GB** (MMLKG graph + OEIS)
- `cartography/lmfdb_dump/` — **23 GB** (253 JSON files from LMFDB)
- `Prometheus_data_backup/` — **36 GB** (full backup, overlapping)

---

## Part 1: charon/ (27 GB)

### 1.1 Primary Database

| File | Size | Format | Contents |
|------|------|--------|----------|
| `data/charon.duckdb` | 1.2 GB | DuckDB | EC, MF, L-function data ingested from LMFDB PostgreSQL mirror |

Tables: `objects`, `elliptic_curves`, `modular_forms`, `l_functions`, `known_bridges`, `landscape`, `hypothesis_queue`, `failure_log`, `ingestion_log`

Scripts that use it: All `src/*.py` modules via `config.py` (`duckdb.connect()`)

### 1.2 Cached Computations

| File | Size | Format | Contents | Source |
|------|------|--------|----------|--------|
| `data/dirichlet_raw_cache.pkl` | 1.8 GB | Pickle | Degree-1 L-function data (Dirichlet character zeros) | LMFDB PostgreSQL mirror |
| `spectral_survey/artin_cache.pkl` | 7.2 MB | Pickle | Artin L-function dimension/degree metadata | Computed from LMFDB queries |
| `data/empirical_strata_so_even.json` | 3.6 KB | JSON | 82 conductor/zero-count objects for SO(even) stratification | Generated |

### 1.3 Spectral Survey (`spectral_survey/`)

**Total: 409 MB**

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `results/maass_raw.json` | 271 MB | JSON | Raw Maass form data with zeros | **ACTIVE** — used by analysis |
| `results/maass_zeros.json` | 650 KB | JSON | Maass form zeros summary | **ACTIVE** |
| `results/artin.json` | 4.2 KB | JSON | Sign inversion analysis, Artin dims 1-4 | **ACTIVE** |
| `results/cross_family.json` | 6.9 KB | JSON | Cross-family comparative analysis | **ACTIVE** |
| `results/dirichlet.json` | 1.8 KB | JSON | Dirichlet single-family analysis | **ACTIVE** |
| `results/hilbert.json` | 14 KB | JSON | Hilbert class field L-function analysis | **ACTIVE** |
| `results/maass.json` | 13 KB | JSON | Maass form analysis | **ACTIVE** |
| `results/number_fields.json` | 3.0 KB | JSON | Number fields analysis | **ACTIVE** |
| `raw_data/dirichlet_zeros/computed_zeros.json` | 40 KB | JSON | ~100+ Dirichlet characters with zeros | Generated |
| `raw_data/dirichlet_zeros/computed_zeros_v2.json` | 397 KB | JSON | Enhanced Dirichlet zero computations | Generated |
| `raw_data/hilbert_zeros/metadata.json` | 6.6 MB | JSON | Hilbert field L-function metadata from LMFDB | Downloaded |
| `cache/number_fields/` | 121 MB | 5,467 TXT files | Per-field Artin representation cache (`artin_[label].txt`) | Generated |
| `raw_data/artin_zeros/` | empty | — | Planned for Artin representation zeros | **EMPTY** |
| `raw_data/maass_zeros/` | empty | — | Planned for Maass form zeros | **EMPTY** |
| `raw_data/nf_zeros/` | empty | — | Planned for number field zeros | **EMPTY** |

### 1.4 james_downloads/ (23 GB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `mmlkg/mmlkg.graphml` | 23 GB | GraphML | Microsoft Mathematical Language Knowledge Graph (50M+ relationships) | **DOWNLOADED, UNUSED** — no script references this |
| `mmlkg/stats.json` | 115 KB | JSON | MMLKG statistics | Downloaded |
| `names` | 37 MB | Binary | OEIS names lookup table | Downloaded |
| `stripped` | 77 MB | Binary | OEIS stripped sequence data | Downloaded |
| `oeisdata/` | 29 KB | Mixed | OEIS license + metadata, `files/` and `seq/` subdirs **EMPTY** | Partially downloaded |
| `GAP/` | 23 MB | Installer | GAP computer algebra system (Windows installer, not data) | Downloaded |

### 1.5 Other charon/ data

| Path | Size | Format | Contents |
|------|------|--------|----------|
| `reports/type_b_characterization.json` | 317 B | JSON | 27,279 modular forms cluster analysis |
| `reports/council_responses/` | ~50 KB | 12 MD files | Multi-LLM analysis responses (GPT-4, Claude, DeepSeek, Gemini) |
| `v2/oscillation_shadow_results.json` | 22 KB | JSON | Sign oscillation analysis (17,314 forms) |
| `research/_submission_status.json` | 2.4 KB | JSON | Deep research submission tracking |

---

## Part 2: cartography/ (152 GB)

### 2.1 convergence/ (125 GB) — LARGEST DIRECTORY

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `data/sleeper_fingerprints.json` | 2.1 GB | JSON | Sleeper fingerprint analysis | Generated |
| `data/abstraction_depths.json` | 5.2 MB | JSON | Mathlib module abstraction metrics | Generated |
| `data/bianchi_forms.json` | 33 MB | JSON | Bianchi modular forms | Generated |
| `data/constant_base_analysis.json` | 1.1 MB | JSON | Constant base analysis | Generated |
| `data/concept_ids.json` | 854 KB | JSON | OpenAlex concept IDs | Downloaded |
| `data/hgcwa_passports_full.json` | 61 MB | JSON | Hypergeometric Calabi-Yau passports | Downloaded/LMFDB |
| `data/hmf_forms_full.json` | 45 MB | JSON | Hilbert modular forms | Downloaded/LMFDB |
| `data/genocide_r*_results.json` | Multiple | JSON | Round 2-7 analysis results | Generated |
| `data/moonshine/` | 27 files | JSON | Moonshine analysis | Generated |
| 93+ other JSON files | Various | JSON | Analysis pipeline outputs | Generated |

**Note:** The remaining ~120 GB is unaccounted for in the file-level scan — likely large intermediate files, cached computations, or deep subdirectory content that needs manual inspection.

### 2.2 lmfdb_dump/ (23 GB, 253 JSON files)

The complete LMFDB database dump. Files >500 MB:

| File | Size | Contents |
|------|------|----------|
| `ec_nfportraits.json` | 5.1 GB | Elliptic curve number field portraits |
| `maass_rigor_portraits.json` | 3.4 GB | Rigorous Maass form portraits |
| `maass_rigor_coefficients.json` | 2.1 GB | Rigorous Maass coefficients |
| `maass_rigor_extras.json` | 2.1 GB | Rigorous Maass extras |
| `mf_gamma1_portraits.json` | 1.6 GB | Gamma1 modular form portraits |
| `modcurve_pictures.json` | 1.5 GB | Modular curve pictures |
| `g2c_plots.json` | 1.4 GB | Genus 2 curve plots |
| `maass_portraits.json` | 654 MB | Maass portraits |
| `smf_fc.json` | 619 MB | Siegel modular form Fourier coefficients |
| `gps_transitive.json` | 534 MB | Transitive permutation groups |

**Status:** Many of these appear to be portrait/image data (base64-encoded plots). The computational data files (coefficients, Fourier coeffs, modular forms) are actively used by analysis scripts. The portrait files may be dead weight unless visualization is needed.

### 2.3 physics/data/ (420 MB)

#### Superconductors (107 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `superconductors/3DSC/.../3DSC_MP.csv` | 9.1 MB | CSV | 5,773 superconductors, 92 columns (formulas, SGs, Tc, properties) | **ACTIVE** — primary SC dataset |
| `superconductors/3DSC/.../Supercon_data_by_2018_Stanev.csv` | 350 KB | CSV | Stanev dataset (formula, Tc) | **ACTIVE** — cross-match source |
| `superconductors/3DSC/.../MP_subset.csv` | 6.9 MB | CSV | Materials Project subset | Supporting |
| `superconductors/3DSC/.../ICSD_subset.csv` | 1.9 KB | CSV | ICSD structure IDs | Supporting |
| `superconductors/3DSC/.../cifs/` | ~15,621 CIF files | CIF | Crystal structure files from MP | **ACTIVE** — structure data |
| `superconductors/cod_canonical_superconductors.csv` | 54 KB | CSV | **NEW** — 446 COD entries, 61 unique SGs | **ACTIVE** — cross-validation |
| `superconductors/aflow_canonical_superconductors.csv` | 199 KB | CSV | **NEW** — 2,012 AFLOW entries, 82 unique SGs | **ACTIVE** — cross-validation |
| `superconductors/cod_spacegroup_crossmatch.csv` | 32 KB | CSV | **NEW** — 304 COD bulk crossmatch entries | **ACTIVE** — cross-validation |
| `superconductors/3DSC_nonsuperconductors.csv` | 0 B | CSV | Empty placeholder | **EMPTY** |
| `superconductors/3DSC_superconductors.csv` | 0 B | CSV | Empty placeholder | **EMPTY** |

#### NIST Atomic Spectra (7.4 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `nist_asd/` | 7.4 MB | 118 JSON files | Per-element energy levels (Ac through Zn) | Downloaded from NIST ASD |

#### Other Physics

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `basis_sets/all_basis_sets.json` | 292 MB | JSON | Quantum chemistry basis sets | Downloaded — **LARGE, possibly unused** |
| `materials_project_10k.json` | 4.4 MB | JSON | 10K crystal structures from MP | Downloaded |
| `earthquakes/quakes_197*.csv` | 1.7 MB total | CSV | 5 years of earthquake data (1970-1974) | Downloaded — **purpose unclear** |
| `codata/` | Small | JSON | Physical constants | Downloaded |
| `pdg/`, `pdg_extended/` | Small | JSON | Particle Data Group | Downloaded |
| `planck/` | Small | JSON/TXT | CMB data | Downloaded |
| `dlmf/` | Small | JSON | DLMF chapter formulas | Downloaded |
| `chaos/`, `climate/`, `finance/`, `gravitational_waves/`, `qm9/`, `ramanujan_machine/` | Various | Various | Assorted physics datasets | **STATUS UNKNOWN — check if used** |

### 2.4 OEIS (390 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `oeis/data/new_terms/` | — | 1,539 JSON files | Sequence data (A148700–A151331) | Generated |
| `oeis/data/names.txt` | 37 MB | TXT | OEIS sequence names | Downloaded |
| `oeis/data/stripped_new.txt` | 77 MB | TXT | Stripped sequence data | Downloaded |
| `oeis/data/oeis_names.json` | 39 MB | JSON | Parsed OEIS names | Generated |
| `oeis/data/stripped_full.gz` | 30 MB | GZ | Compressed full strip | Downloaded |
| `oeis/data/names.gz` | 4.5 KB | GZ | Compressed names | Downloaded |
| `oeis/data/stripped.gz` | 4.5 KB | GZ | Compressed stripped | Downloaded |

Scripts: `extract_oeis_crossrefs.py`, `extract_oeis_metadata.py`, `ingest_and_landscape.py`

### 2.5 Maass Forms (342 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `maass/data/maass_with_coefficients.json` | 335 MB | JSON | Full Maass forms with coefficients | **ACTIVE** |
| `maass/data/maass_rigor_full.json` | 6.9 MB | JSON | Rigorous Maass forms | Active |
| `maass/data/maass_forms_full.json` | 59 KB | JSON | Maass forms metadata | Active |
| `maass/data/maass_forms.json` | 11 KB | JSON | Maass forms summary | Active |
| `maass/data/maass_live.html` | 26 KB | HTML | Web scrape | **Possibly stale** |
| `maass/data/maass_sample.html` | 22 KB | HTML | Sample scrape | **Possibly stale** |
| `maass/data/maass_raw.txt` | 22 KB | TXT | Raw text data | **Possibly stale** |

Four fetch scripts (fetch_maass.py, fetch_maass_curl.py, fetch_maass_html.py, fetch_maass_simple.py) — suggests iterative debugging of LMFDB scraping.

### 2.6 Genus 2 Curves (1.1 GB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `genus2/data/siegel_fourier_coeffs.json` | 619 MB | JSON | Siegel modular form Fourier coefficients | Active |
| `genus2/data/siegel_samples.json` | 23 MB | JSON | Siegel modular form samples | Active |
| `genus2/data/genus2_curves_full.json` | 18 MB | JSON | Complete genus 2 curves | Active |
| `genus2/data/genus2_curves.json` | Small | JSON | Genus 2 curves metadata | Active |
| `genus2/data/genus2_curves_lmfdb.json` | Small | JSON | LMFDB variant | Active |
| `genus2/data/g2c-data/` | — | Git repo | Source data repo with large TXT files | Downloaded |
| `genus2/data/g2c-data/gce_1000000_ldata1.txt` | 109 MB | TXT | Genus 2 curve data | Downloaded |
| `genus2/data/g2c-data/gce_1000000_ldata1.txt.bz2` | 46 MB | BZ2 | Compressed version of above | **REDUNDANT** |
| `genus2/data/g2c-data/gce_1000000_ldata2.txt.bz2` | 57 MB | BZ2 | More genus 2 data | Downloaded |
| `genus2/data/g2c-data/gce_1000000_lmfdb.txt` | 28 MB | TXT | LMFDB format | Downloaded |
| `genus2/data/g2c-data/ucd_1000000_lmfdb.txt` | 27 MB | TXT | UCD LMFDB format | Downloaded |

### 2.7 Isogenies (662 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `isogenies/data/isogeny-database-v1-30000.zip` | 283 MB | ZIP | Isogeny database (compressed) | Downloaded |
| `isogenies/data/graphs/` | — | — | Graph data (if extracted) | **Check if extracted** |
| `isogenies/data/odc_by_1_0_public_text.txt` | 20 KB | TXT | Public text data | Downloaded |

### 2.8 OMF5 Data (447 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `omf5_data/qf5.db` | 2.5 MB | SQLite | Quadratic forms database | Active |
| `omf5_data/qf5db.sage` | 19 MB | Sage | Sage database export | **Possibly redundant with .db** |
| `omf5_data/hecke_3_0.dat` | 46 MB | DAT | Hecke matrices (level 3, weight 0) | Active |
| `omf5_data/hecke_all.dat` | 31 MB | DAT | All Hecke data | Active |
| `omf5_data/hecke_evs_3_0/data/` | ~25 DAT files | DAT | Per-eigenvalue Hecke data | Active |
| `omf5_data/newforms30_dims.txt` | 27 KB | TXT | Newform dimensions | Active |

### 2.9 Atlas / Group Theory (228 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `atlas/data/small_groups.json` | — | JSON | GAP small groups database | Active |
| `atlas/data/gap-system/` | — | Git repo | Full GAP source code | **HEAVY — is full GAP source needed?** |
| `atlas/data/smallgrp/small7/sml512.db` | 89 KB | SQLite | Groups of order 512 | Active |
| `atlas/data/smallgrp/id5/id1344.gz` | 75 KB | GZ | Group ID data | Downloaded |

### 2.10 Metabolism (256 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `metabolism/data/Recon3D.json` | 7.5 MB | JSON | Human metabolic network (Recon3D) | Active |
| `metabolism/data/RECON1.json` | 3.9 MB | JSON | First-gen human metabolic model | Active |
| `metabolism/data/STM_v1_0.json` | 2.6 MB | JSON | Tissue-specific model | Active |
| `metabolism/data/e_coli_core.json` | 170 KB | JSON | E. coli core metabolism | Active |
| Other metabolic models | ~240 MB | JSON | BiGG/AGORA models | **Check which are used** |

### 2.11 Groups (107 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `groups/data/abstract_groups.json` | 107 MB | JSON | Extracted GAP groups | Active |

### 2.12 Knots (92 MB)

| Path | Size | Format | Contents | Status |
|------|------|--------|----------|--------|
| `knots/data/knots.json` | 2.8 MB | JSON | Knot data | Active |
| `knots/data/knotinfo_3d.csv.tar.gz` | 45 MB | TAR.GZ | KnotInfo 3D data (compressed) | Downloaded |
| `knots/data/knot_polys.xlsx` | 8.5 MB | XLSX | Knot polynomials | Downloaded |
| `knots/data/knot_polys.xlsx.zip` | 7.8 MB | ZIP | Compressed duplicate of above | **REDUNDANT** |
| `knots/data/PD_3-16.txt.zip` | 29 MB | ZIP | Knot PD presentations | Downloaded |

### 2.13 Smaller Domains

| Domain | Path | Size | Files | Status |
|--------|------|------|-------|--------|
| **Mathlib** | `mathlib/data/` | 138 MB | import_graph.json + mathlib4 source | Active |
| **Metamath** | `metamath/data/` | 49 MB | set.mm (49 MB) + theorem_list.json | Active |
| **Paramodular** | `paramodular_*/` | 140 MB | Eigenvalue TXT files + Siegel data | Active |
| **Topology** | `topology/data/pi-base/` | 28 MB | Pi-Base git repo | Active |
| **Genus 3** | `genus3/` | 7.7 MB | spqcurves.txt | Active |
| **Lattices** | `lattices/data/` | 6.8 MB | lattices_full.json | Active |
| **Fungrim** | `fungrim/data/` | 5.7 MB | fungrim_index.json + source | Active |
| **Local Fields** | `local_fields/data/` | 4.5 MB | database.pdf + code | Active |
| **Antedb** | `antedb/data/` | 3.2 MB | antedb_index.json | Active |
| **Number Fields** | `number_fields/data/` | 1.8 MB | number_fields.json | Active |
| **Open Problems** | `open_problems/` | 1.5 MB | erdos_enriched.jsonl, problem_relationships.jsonl | Active |
| **Polytopes** | `polytopes/data/` | 128 KB | 19 JSON files (PolyDB) | Active |
| **FindStat** | `findstat/data/` | 244 KB | findstat_enriched.json | Active |

### 2.14 v2/ Analysis Results (32 MB)

263 JSON result files from cross-domain analysis runs:
- `bilbao_sg_analysis_results.json` (56 KB)
- `codata_compressibility_results.json` (109 KB)
- `chromatic_scaling_results.json` (37 KB)
- `map_elites_archive.json`
- Multiple `genocide_results.json` variants
- Various `*_results.json` files

### 2.15 shared/scripts/v2/ (18 MB)

146 JSON + MD files — extracted/enriched analysis results:
- `algebraic_dna_fungrim_results.json`
- Various battery and deformation results
- `generated_problems/` subdirectory

### 2.16 james_downloads/ (2.4 MB)

| Path | Size | Format | Contents |
|------|------|--------|----------|
| PDFs | Various | PDF | Academic papers (1803.04092v2.pdf, Heuristic_Table_1000.pdf) |
| `COM_PowerSpect_CMB-TT-binned_R3.01.txt` | 7.0 KB | TXT | Planck CMB power spectrum |
| HTML files | Various | HTML | Web captures |
| Markdown files | Various | MD | Sato-Tate distributions, problem frontiers |

---

## Part 3: Other Directories with Science Data

### 3.1 noesis/ (53 MB)

| Path | Size | Format | Contents |
|------|------|--------|----------|
| `v2/backups/backup_2026-03-30/*.csv` | ~10 MB | 17 CSV files | Knowledge graph backup (depth matrices, operations, chains, discoveries) |
| `dark_hub_enrichment/isolated_hubs_by_domain.csv` | 14 KB | CSV | Dark hub analysis |
| `backups/*.zip` | 2.9 MB | ZIP | Checkpoint backups |

### 3.2 agents/ (419 MB)

| Path | Size | Format | Contents |
|------|------|--------|----------|
| `aletheia/data/knowledge_graph.db` | 424 KB | SQLite | Knowledge graph |
| `clymene/data/vault_registry.db` | 36 KB | SQLite | Vault registry |
| `skopos/data/scores.db` | 24 KB | SQLite | Scoring database |

### 3.3 Prometheus_data_backup/ (36 GB)

Contains duplicates of `charon/data/`, `apollo/checkpoints/`, and other data. Five Apollo checkpoint pickle files (gen 120-160).

---

## Part 4: External API Dependencies

| API | Authentication | Scripts | Data Cached Locally? |
|-----|---------------|---------|---------------------|
| LMFDB PostgreSQL | `devmirror.lmfdb.xyz` (hardcoded creds) | `charon/src/ingest*.py`, `charon/spectral_survey/scripts/` | Yes (DuckDB + pkl) |
| LMFDB REST API | None | `cartography/shared/scripts/fetch_lmfdb_frontiers.py` | Partially |
| Materials Project | `MP_API_KEY` via keys.py | `fetch_materials_10k.py` | Yes (10K JSON) |
| COD REST API | None | `fetch_cod_spacegroups.py`, `fetch_canonical_crossmatch.py` | Yes (3 CSVs) |
| AFLOW AFLUX | None | `fetch_aflow_spacegroups.py`, `fetch_canonical_crossmatch.py` | Yes (1 CSV) |
| NIST ASD | None (HTML form) | `fetch_nist_asd*.py` (3 versions) | Yes (118 JSONs) |
| DLMF | None | `fetch_dlmf*.py` | Partially |
| OpenAlex | None | `fetch_openalex_concepts.py` | Yes |
| polyDB | None (SSL workaround) | `fetch_polydb.py` | Yes |
| FindStat | None | `fetch_findstat.py` | Yes |
| OpenAI API | `OPENAI_KEY` | `charon/scripts/fire_council*.py` | No (ephemeral) |
| Anthropic API | `CLAUDE_KEY` | `charon/scripts/fire_council*.py` | No (ephemeral) |
| Google Gemini | `GOOGLE_KEY` | `charon/scripts/fire_council*.py` | No (ephemeral) |
| DeepSeek | `DEEPSEEK_KEY` | `charon/scripts/fire_council*.py` | No (ephemeral) |

---

## Part 5: Data-Script Gap Analysis

### Data Downloaded but NOT Referenced by Any Script

| Path | Size | Notes |
|------|------|-------|
| `charon/james_downloads/mmlkg/mmlkg.graphml` | **23 GB** | Microsoft Math Knowledge Graph — no script imports or queries this |
| `charon/james_downloads/names` | 37 MB | OEIS names binary — no script references |
| `charon/james_downloads/stripped` | 77 MB | OEIS stripped binary — no script references |
| `charon/james_downloads/GAP/` | 23 MB | GAP Windows installer — not data, never executed |
| `charon/james_downloads/oeisdata/` | 29 KB | Empty `files/` and `seq/` dirs — incomplete download |
| `cartography/physics/data/earthquakes/` | 1.7 MB | Earthquake CSVs (1970-1974) — no analysis script found |
| `cartography/physics/data/chaos/` | ? | Chaotic systems data — no analysis script found |
| `cartography/physics/data/climate/` | ? | Climate data — no analysis script found |
| `cartography/physics/data/finance/` | ? | Financial data — no analysis script found |
| `cartography/physics/data/gravitational_waves/` | ? | LIGO data — no analysis script found |
| `cartography/physics/data/qm9/` | ? | Quantum molecules — no analysis script found |
| `cartography/physics/data/ramanujan_machine/` | ? | Ramanujan machine outputs — no analysis script found |
| `cartography/physics/data/basis_sets/all_basis_sets.json` | **292 MB** | Quantum chemistry basis sets — no analysis script found |

### Redundant / Duplicate Data

| Item | Size | Notes |
|------|------|-------|
| `Prometheus_data_backup/` | **36 GB** | Full backup — contains duplicates of charon/data/, apollo checkpoints |
| `knots/data/knot_polys.xlsx` + `knot_polys.xlsx.zip` | 16.3 MB | XLSX exists both compressed and uncompressed |
| `genus2/data/g2c-data/gce_1000000_ldata1.txt` + `.bz2` | 155 MB | TXT exists both compressed and uncompressed |
| `lmfdb_dump/smf_fc.json` ↔ `genus2/data/siegel_fourier_coeffs.json` | 1.2 GB | Appear to contain same Siegel modular form Fourier coefficients |
| OEIS data in `charon/james_downloads/` ↔ `cartography/oeis/data/` | ~115 MB | Two separate OEIS data pulls |
| `maass/data/maass_*.html` + `maass_raw.txt` | ~70 KB | Stale intermediate scrape artifacts |

### Empty Placeholders

| Path | Notes |
|------|-------|
| `spectral_survey/raw_data/artin_zeros/` | Planned, never populated |
| `spectral_survey/raw_data/maass_zeros/` | Planned, never populated |
| `spectral_survey/raw_data/nf_zeros/` | Planned, never populated |
| `superconductors/3DSC_nonsuperconductors.csv` | 0 bytes |
| `superconductors/3DSC_superconductors.csv` | 0 bytes |
| `charon/james_downloads/oeisdata/files/` | Empty |
| `charon/james_downloads/oeisdata/seq/` | Empty |

### Scripts with Multiple Versions (Possible Cruft)

| Pattern | Count | Notes |
|---------|-------|-------|
| `fetch_nist_asd.py`, `_v2.py`, `_v3.py` | 3 | Iterative debugging — keep only latest |
| `fetch_maass.py`, `_curl.py`, `_html.py`, `_simple.py` | 4 | Four approaches to same LMFDB scrape |
| `fetch_cod_spacegroups.py`, `fetch_canonical_crossmatch.py` | 2 | Two COD fetch approaches |

---

## Part 6: Portrait/Image Data in LMFDB Dump

Several of the largest files in `lmfdb_dump/` contain base64-encoded portrait images, not computational data:

| File | Size | Type |
|------|------|------|
| `ec_nfportraits.json` | 5.1 GB | EC number field **portraits** |
| `maass_rigor_portraits.json` | 3.4 GB | Maass **portraits** |
| `mf_gamma1_portraits.json` | 1.6 GB | Modular form **portraits** |
| `modcurve_pictures.json` | 1.5 GB | Modular curve **pictures** |
| `g2c_plots.json` | 1.4 GB | Genus 2 curve **plots** |
| `maass_portraits.json` | 654 MB | Maass **portraits** |
| `av_fq_teximages.json` | 299 MB | Abelian variety **TeX images** |
| `modcurve_images.json` | 294 MB | Modular curve **images** |
| `belyi_galmap_portraits.json` | 174 MB | Belyi **portraits** |
| `mf_newform_portraits_test.json` | 120 MB | Newform **portraits** (test) |

**Total portrait/image data: ~16.7 GB** out of 23 GB in lmfdb_dump — 73% of the dump is visualization data, not computational data.

---

## Part 7: Suggested Data Cleanup Strategy

**Do NOT execute any of these. This is a recommendation only.**

### Tier 1: Safe to Remove (~60 GB)

| Action | Savings | Risk |
|--------|---------|------|
| Remove `Prometheus_data_backup/` after verifying it's a true subset of current state | ~36 GB | Low — verify first |
| Remove portrait/image JSONs from `lmfdb_dump/` (`*portraits*`, `*pictures*`, `*plots*`, `*images*`, `*teximages*`) | ~16.7 GB | Low — these are visualizations, not computational data. Re-downloadable from LMFDB. |
| Remove `charon/james_downloads/GAP/` (Windows installer, not data) | 23 MB | None |
| Remove empty directories (artin_zeros/, maass_zeros/, nf_zeros/, empty CSVs, empty oeisdata subdirs) | ~0 | None |
| Remove `knots/data/knot_polys.xlsx.zip` (uncompressed version exists) | 7.8 MB | None |

### Tier 2: Review Before Removing (~24 GB)

| Action | Savings | Risk |
|--------|---------|------|
| Evaluate `charon/james_downloads/mmlkg/` — 23 GB GraphML with no script references. Keep if there's a future plan; remove if it was an exploratory download. | 23 GB | Medium — may have future use |
| Evaluate `physics/data/basis_sets/all_basis_sets.json` — 292 MB, no script references | 292 MB | Medium |
| Evaluate unused physics domains (earthquakes, chaos, climate, finance, gravitational_waves, qm9, ramanujan_machine) | ~500 MB? | Low — likely exploratory downloads |
| Deduplicate `lmfdb_dump/smf_fc.json` vs `genus2/data/siegel_fourier_coeffs.json` | 619 MB | Check if identical first |
| Deduplicate OEIS data between `charon/james_downloads/` and `cartography/oeis/data/` | ~115 MB | Check which is more complete |
| Consolidate Maass fetch scripts to one working version | ~0 (code, not data) | Low |
| Consolidate NIST ASD fetch scripts to one working version | ~0 (code, not data) | Low |

### Tier 3: Structural Improvements

| Action | Benefit |
|--------|---------|
| Compress `genus2/data/g2c-data/gce_1000000_ldata1.txt` (109 MB uncompressed, .bz2 already exists) — remove uncompressed if nothing reads it directly | 109 MB |
| Add a `DATA_MANIFEST.json` at repo root listing every data source, its origin URL, fetch script, and last-fetched date | Provenance tracking |
| Move all `james_downloads/` content to appropriate domain directories or remove | Organizational clarity |
| Tag each `fetch_*.py` script with `# CACHED: yes/no` and `# LAST_FETCHED: date` | Reduces re-fetch confusion |
| Consider converting the 125 GB `convergence/data/` to a more compact format (Parquet, DuckDB) if it's all JSON | Potentially massive savings |

### Priority Order

1. **Portrait purge** (Tier 1) — 16.7 GB of base64 images with no analytical use
2. **Backup audit** (Tier 1) — verify `Prometheus_data_backup/` is redundant, then remove
3. **MMLKG decision** (Tier 2) — 23 GB single file, keep or kill
4. **Convergence investigation** (Tier 3) — 125 GB needs a deep dive to understand what's actually in there
5. **Deduplication pass** (Tier 2) — OEIS, Siegel Fourier coeffs, compressed-vs-uncompressed pairs
