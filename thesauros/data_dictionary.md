# Prometheus Data Dictionary

Every table across all databases. The single source of truth for what a field means, where it came from, and what scripts use it.

Last updated: 2026-04-16 (evening — Aporia unblock: nf_fields full, 6 new indexes, lmfdb user grants)

---

## LMFDB Mirror (`lmfdb` database, M1:5432)

All columns are **TEXT** type in the mirror (raw CSV dump from devmirror.lmfdb.xyz). Cast as needed. All tables read-only except for index creation.

### Access / Permissions

| User | Password | Access |
|------|----------|--------|
| postgres | prometheus | Full superuser access across all databases |
| lmfdb | lmfdb | SELECT on all tables + `bsd_joined` view (granted 2026-04-16) |

The `lmfdb` user also has SELECT access across all schemas in `prometheus_sci` and `prometheus_fire` as of 2026-04-16.

Agent users (harmonia, ergon, charon, ingestor) exist but still have `CHANGE_ME_*` placeholder passwords from `scripts/db_setup.sql`. **Use postgres/prometheus until these are fixed.**

### Index Inventory (lmfdb database)

| Table | Index | Column(s) | Built |
|-------|-------|-----------|-------|
| lfunc_lfunctions | idx_lfunc_origin | origin | 2026-04-15 |
| lfunc_lfunctions | idx_lfunc_conductor_numeric | (conductor::numeric) | 2026-04-15 (523 MB) |
| lfunc_lfunctions | idx_lfunc_conductor | conductor | 2026-04-15 |
| lfunc_lfunctions | idx_lfunc_degree | degree | 2026-04-15 |
| lfunc_lfunctions | idx_lfunc_motivic_weight | motivic_weight | 2026-04-15 |
| lfunc_lfunctions | idx_lfunc_order_of_vanishing | order_of_vanishing | 2026-04-15 |
| ec_curvedata | idx_ec_iso | lmfdb_iso | 2026-04-16 |
| ec_curvedata | idx_ec_conductor_numeric | (conductor::bigint) | 2026-04-16 |
| mf_newforms | idx_mf_weight_level | (weight::int, level::int) | 2026-04-16 |
| mf_newforms | idx_mf_level | (level::int) | 2026-04-16 |
| artin_reps | idx_artin_dim_conductor | ("Dim"::int, "Conductor"::numeric) | 2026-04-16 |
| artin_reps | idx_artin_dim | ("Dim"::int) | 2026-04-16 |
| nf_fields | idx_nf_degree | degree | 2026-04-15 |
| nf_fields | idx_nf_disc | disc_abs | 2026-04-15 |
| bsd_joined | idx_bsd_conductor | conductor | 2026-04-16 |
| bsd_joined | idx_bsd_rank | rank | 2026-04-16 |
| bsd_joined | idx_bsd_iso | ec_iso | 2026-04-16 |

### ec_curvedata -- Elliptic Curves over Q

- **Rows:** 3,824,372
- **Source:** LMFDB devmirror (devmirror.lmfdb.xyz), table ec_curvedata
- **Loaded by:** Manual CSV dump + psql COPY (2026-04-14)
- **Indexes (built 2026-04-16):**
  - `idx_ec_iso` on lmfdb_iso (btree on TEXT, for isogeny-class joins)
  - `idx_ec_conductor_numeric` on (conductor::bigint) (functional, for range queries)

Key columns (52 total):

| Column | Description |
|--------|-------------|
| lmfdb_label | Unique label, e.g. "11.a1" = conductor.iso_class+curve_number |
| lmfdb_iso | Isogeny class label, e.g. "11.a" |
| conductor | Conductor (integer as text) |
| rank | Algebraic rank (via descent/Mordell-Weil) |
| analytic_rank | Order of vanishing of L(E,s) at s=1 |
| regulator | Regulator of Mordell-Weil group |
| sha | Analytic order of Sha (**circular at rank >= 2** -- computed assuming BSD) |
| sha_primes | Primes dividing Sha |
| torsion | Order of torsion subgroup |
| torsion_structure | Torsion group structure, e.g. "{2,4}" |
| ainvs | Weierstrass coefficients [a1,a2,a3,a4,a6] |
| cm | CM discriminant (0 if no CM) |
| bad_primes | Primes of bad reduction |
| num_bad_primes | Count of bad primes |
| isogeny_degrees | Degrees of isogenies in class |
| class_size | Number of curves in isogeny class |
| semistable | Semistability flag |
| manin_constant | Manin constant (mostly 1) |
| faltings_height | Faltings height |
| signD | Sign of discriminant |
| jinv | j-invariant (as string) |

**Scripts:** harmonia/src/domain_index.py, ergon/tensor_builder.py, forge/v3/executor.py, thesauros/create_bsd_joined.py, charon/src/ingest.py, aporia/scripts/triage_classifier.py, cartography/shared/scripts/oq1_spectral_tail.py, ~20 harmonia/scripts/ and cartography/ research scripts

**Data quality:** All columns TEXT. Selection bias at high conductor (prime conductor, trivial torsion dominate above 1M). Sha circular at rank >= 2.

---

### mf_newforms -- Modular Forms (Newforms)

- **Rows:** 1,141,510
- **Source:** LMFDB devmirror, table mf_newforms
- **Loaded by:** Manual CSV dump + psql COPY (2026-04-14)
- **Indexes (built 2026-04-16):**
  - `idx_mf_weight_level` on (weight::int, level::int) (composite, for Langlands matching)
  - `idx_mf_level` on (level::int)

Key columns (81 total):

| Column | Description |
|--------|-------------|
| label | Unique LMFDB label, e.g. "23.1.b.a" |
| space_label | Space label |
| level | Level N (integer as text) |
| weight | Weight k (integer as text) |
| dim | Dimension of Hecke eigenvalue field |
| hecke_orbit | Hecke orbit index |
| hecke_orbit_code | Join key to Hecke coefficient tables |
| char_order | Character order |
| char_parity | Character parity (0 or 1) |
| fricke_eigenval | Fricke eigenvalue |
| analytic_conductor | Analytic conductor |
| self_twist_type | Self-twist type |
| is_cm | Has complex multiplication |
| sato_tate_group | Sato-Tate group label |

**Scripts:** harmonia/src/domain_index.py, ergon/tensor_builder.py, forge/v3/executor.py, aporia/scripts/triage_classifier.py, ~15 harmonia/scripts/ and cartography/ research scripts

---

### lfunc_lfunctions -- L-functions

- **Rows:** 24,351,376
- **Source:** LMFDB devmirror, table lfunc_lfunctions
- **Loaded by:** Manual CSV dump + psql COPY (2026-04-14, ~6 hours)
- **Indexes:** idx_lfunc_origin, idx_lfunc_conductor_numeric (523 MB), idx_lfunc_conductor, idx_lfunc_degree, idx_lfunc_motivic_weight, idx_lfunc_order_of_vanishing
- **Size on disk:** ~341 GB (largest table)

Key columns (71 total):

| Column | Description |
|--------|-------------|
| origin | Path to source object, e.g. "EllipticCurve/Q/11/a" or "ModularForm/GL2/Q/holomorphic/23/1/b/a" |
| conductor | Conductor (text, use ::numeric for queries) |
| degree | Degree of L-function |
| motivic_weight | Motivic weight |
| order_of_vanishing | Analytic rank |
| leading_term | Leading Taylor coefficient L^(r)(s=1)/r! |
| root_number | Root number (functional equation sign) |
| sign_arg | Sign argument |
| positive_zeros | Positive zeros on critical line (text blob) |
| z1, z2, z3 | First three zeros |
| self_dual | Self-dual flag |
| symmetry_type | Symmetry type |
| analytic_conductor | Analytic conductor |

**Join to EC:** `origin = 'EllipticCurve/Q/' || conductor || '/' || iso_letter` (see bsd_joined)
**Scripts:** thesauros/create_bsd_joined.py, cartography/shared/scripts/oq1_spectral_tail.py, charon/src/ingest_dirichlet_*.py, ~10 research scripts

---

### artin_reps -- Artin Representations

- **Rows:** 798,140
- **Source:** LMFDB devmirror, table artin_reps
- **Loaded by:** Manual CSV dump + psql COPY (2026-04-14)
- **Indexes (built 2026-04-16):**
  - `idx_artin_dim_conductor` on (Dim::int, Conductor::numeric) (composite, for Langlands + Artin tests)
  - `idx_artin_dim` on (Dim::int)
  - Note: Conductor values include decimal form like "517099.0" — use ::numeric, not ::bigint

Key columns (22 total):

| Column | Description |
|--------|-------------|
| Baselabel | Base label |
| Dim | Dimension of representation |
| Conductor | Conductor |
| Galn | Galois group order n |
| Galt | Galois group transitive number t |
| Indicator | Frobenius-Schur indicator |
| Is_Even | Even representation flag |

**Scripts:** harmonia/src/domain_index.py, aporia/scripts/triage_classifier.py

---

### g2c_curves -- Genus-2 Curves

- **Rows:** 66,158
- **Source:** LMFDB devmirror, table g2c_curves
- **Loaded by:** Manual CSV dump + psql COPY (2026-04-14)

Key columns (51 total):

| Column | Description |
|--------|-------------|
| label | LMFDB label |
| abs_disc | Absolute discriminant |
| analytic_rank | Analytic rank |
| two_selmer_rank | 2-Selmer rank |
| has_square_sha | Whether Sha is a perfect square |
| locally_solvable | Locally solvable |
| globally_solvable | Globally solvable |
| root_number | Root number |
| conductor | Conductor |

**Scripts:** aporia/scripts/triage_classifier.py, cartography/shared/scripts/dissection_tensor.py, ~15 cartography/v2/ genus2 analysis scripts

---

### nf_fields -- Number Fields

- **Rows:** 22,178,569 (FULL pull complete as of 2026-04-16)
- **Source:** LMFDB devmirror, table nf_fields
- **Loaded by:** Mnemosyne streaming pull (started 2026-04-15, completed 2026-04-16)
- **Indexes:** idx_nf_degree, idx_nf_disc
- **Unblocks:** Lehmer, Brumer-Stark, Leopoldt tests

Key columns (43 total):

| Column | Description |
|--------|-------------|
| label | LMFDB label |
| degree | Extension degree [K:Q] |
| disc_abs | Absolute discriminant |
| disc_sign | Sign of discriminant |
| class_number | Class number h(K) |
| regulator | Regulator |
| class_group | Class group structure |

**Scripts:** thesauros/migrate_p6_nffields.py, cartography/v2/nf_*.py (3 scripts)

---

### bsd_joined -- Materialized View (EC + L-function)

- **Rows:** 2,481,157
- **Source:** JOIN of ec_curvedata and lfunc_lfunctions
- **Created by:** thesauros/create_bsd_joined.py (2026-04-16)
- **Join key:** `lf.origin = 'EllipticCurve/Q/' || ec.conductor || '/' || split_part(ec.lmfdb_iso, '.', 2)`
- **Coverage:** 64.9% of EC (conductor up to ~400K)
- **Indexes:** idx_bsd_conductor, idx_bsd_rank, idx_bsd_iso
- **Refresh:** `REFRESH MATERIALIZED VIEW bsd_joined;`

Combines EC algebraic invariants with L-function analytic data. See `thesauros/bsd_joined_view.md` for full column reference.

**WARNING:** Sha is circular at rank >= 2. Do not use for BSD testing at higher rank.

**Scripts:** prometheus_data/__init__.py, thesauros/create_bsd_joined.py

---

## prometheus_sci Database (M1:5432)

Normalized scientific data from external sources. 1,142,469 total rows.

### core.data_source -- Provenance Tracking

- **Rows:** 6
- **Source:** Internal (tracks data ingestion provenance)
- **Schema:** source_id (serial PK), name, origin_url, file_path, loaded_at, row_count, checksum

---

### topology.knots -- Knot Invariants

- **Rows:** 12,965
- **Source:** KnotInfo database (knotinfo.math.indiana.edu)
- **Source file:** `cartography/knots/data/knots.json` (2.7 MB)
- **Loaded by:** mnemosyne/ingest_priority1.py, cartography/knots/scripts/ingest_knotinfo.py

| Column | Type | Description |
|--------|------|-------------|
| knot_id | serial PK | Internal ID |
| name | text UNIQUE | Knot name, e.g. "3_1" (trefoil) |
| crossing_number | smallint | Minimum crossing number |
| determinant | integer | Knot determinant |
| alexander_coeffs | double[] | Alexander polynomial coefficients |
| jones_coeffs | double[] | Jones polynomial coefficients |
| conway_coeffs | double[] | Conway polynomial coefficients |
| signature | smallint | Knot signature |
| source_id | integer FK | References core.data_source |

**Scripts:** harmonia/src/domain_index.py (load_knots), mnemosyne/ingest_priority1.py, cartography/knots/scripts/ingest_knotinfo.py

---

### topology.polytopes -- Polytopes

- **Rows:** 980
- **Source:** Polymake / polytope databases
- **Loaded by:** mnemosyne/migrate_m2.py

| Column | Type | Description |
|--------|------|-------------|
| polytope_id | serial PK | Internal ID |
| name | text | Polytope name |
| dimension | smallint | Dimension |
| n_vertices | integer | Number of vertices |
| n_edges | integer | Number of edges |
| n_facets | integer | Number of facets |
| f_vector | integer[] | f-vector [f0, f1, ...] |
| is_simplicial | boolean | Whether simplicial |
| source_id | integer FK | References core.data_source |

**Scripts:** harmonia/src/domain_index.py (load_polytopes), mnemosyne/migrate_m2.py

---

### chemistry.qm9 -- Quantum Molecules (QM9 Dataset)

- **Rows:** 133,885
- **Source:** QM9 dataset (Ramakrishnan et al. 2014, rdkit.org/docs/GettingStartedInPython.html)
- **Source file:** `cartography/chemistry/data/qm9.csv` (29 MB)
- **Loaded by:** mnemosyne/ingest_priority1.py
- **URL:** https://figshare.com/collections/Quantum_chemistry_structures_and_properties_of_134_kilo_molecules/978904

| Column | Type | Description |
|--------|------|-------------|
| mol_id | serial PK | Internal ID |
| smiles | text | SMILES string (molecular structure) |
| homo | double | Highest occupied molecular orbital energy (eV) |
| lumo | double | Lowest unoccupied molecular orbital energy (eV) |
| homo_lumo_gap | double | HOMO-LUMO gap (eV) |
| zpve | double | Zero-point vibrational energy (eV) |
| polarizability | double | Isotropic polarizability (Bohr^3) |
| n_atoms | smallint | Number of atoms |
| source_id | integer FK | References core.data_source |

**Scripts:** harmonia/src/domain_index.py (load_qm9), mnemosyne/ingest_priority1.py

---

### algebra.space_groups -- Crystallographic Space Groups

- **Rows:** 230
- **Source:** International Tables for Crystallography (all 230 space groups)
- **Source file:** `cartography/spacegroups/data/space_groups.json` (80 KB)
- **Loaded by:** mnemosyne/ingest_priority1.py
- **URL:** https://www.cryst.ehu.es/ (Bilbao Crystallographic Server)

| Column | Type | Description |
|--------|------|-------------|
| sg_id | serial PK | Internal ID |
| number | smallint UNIQUE | Space group number (1-230) |
| symbol | text | Hermann-Mauguin symbol |
| point_group_order | smallint | Order of point group |
| crystal_system | text | Crystal system (triclinic, monoclinic, ..., cubic) |
| lattice_type | text | Bravais lattice type (P, I, F, C, R) |
| is_symmorphic | boolean | Whether symmorphic |

**Scripts:** harmonia/src/domain_index.py (load_space_groups), mnemosyne/ingest_priority1.py

---

### algebra.lattices -- Mathematical Lattices

- **Rows:** 39,293
- **Source:** LMFDB lattice database (lmfdb.org/Lattice)
- **Source file:** `cartography/lattices/data/lattices_full.json` (6.8 MB, key: "records")
- **Loaded by:** thesauros/ingest_empty_tables.py (reload from 26 to 39,293)

| Column | Type | Description |
|--------|------|-------------|
| lattice_id | serial PK | Internal ID |
| label | text UNIQUE | LMFDB label, e.g. "1.2.4.1.1" |
| dimension | smallint | Lattice dimension |
| determinant | double | Determinant of Gram matrix |
| level | integer | Level |
| class_number | integer | Class number |
| kissing_number | integer | Kissing number (from minimal_vector in source) |
| source_id | integer FK | References core.data_source |

**Scripts:** harmonia/src/domain_index.py (load_lattices), thesauros/ingest_empty_tables.py, mnemosyne/ingest_priority1.py

---

### algebra.groups -- Abstract Groups

- **Rows:** 544,831
- **Source:** LMFDB abstract groups database (lmfdb.org/Groups/Abstract)
- **Source file:** `cartography/groups/data/abstract_groups.json` (107 MB)
- **Loaded by:** mnemosyne/ingest_priority1.py

| Column | Type | Description |
|--------|------|-------------|
| group_id | serial PK | Internal ID |
| label | text UNIQUE | LMFDB label |
| order_val | numeric | Group order |
| exponent | numeric | Group exponent |
| n_conjugacy | integer | Number of conjugacy classes |
| is_abelian | boolean | Whether abelian |
| is_solvable | boolean | Whether solvable |
| source_id | integer FK | References core.data_source |

**Scripts:** harmonia/src/domain_index.py (load_groups), mnemosyne/ingest_priority1.py

---

### physics.codata -- NIST Physical Constants (CODATA 2022)

- **Rows:** 355
- **Source:** NIST CODATA Fundamental Physical Constants (2022 adjustment)
- **Source file:** `cartography/physics/data/codata_constants.json` (52 KB)
- **Loaded by:** thesauros/ingest_empty_tables.py
- **URL:** https://physics.nist.gov/cuu/Constants/

| Column | Type | Description |
|--------|------|-------------|
| constant_id | serial PK | Internal ID |
| name | text UNIQUE | Constant name, e.g. "speed of light in vacuum" |
| value | double | Numerical value |
| uncertainty | double | Standard uncertainty |
| unit | text | SI unit |
| source_id | integer FK | References core.data_source |

**Scripts:** thesauros/ingest_empty_tables.py, cartography/v2/codata_*.py (6 analysis scripts)

---

### physics.superconductors -- Superconductor Materials

- **Rows:** 2,012
- **Source:** AFLOW Superconductor Database (aflow.org)
- **Source file:** `cartography/physics/data/superconductors/aflow_canonical_superconductors.csv` (500 KB)
- **Loaded by:** thesauros/ingest_empty_tables.py
- **URL:** https://aflow.org/

| Column | Type | Description |
|--------|------|-------------|
| sc_id | serial PK | Internal ID |
| material_formula | text | Chemical formula / compound name |
| tc | double | Critical temperature Tc (K) |
| spacegroup | text | Space group |
| sc_class | text | Superconductor class |
| source_id | integer FK | References core.data_source |

**Scripts:** thesauros/ingest_empty_tables.py

---

### physics.materials -- Materials Project Compounds

- **Rows:** 10,000
- **Source:** Materials Project (materialsproject.org)
- **Source file:** `cartography/physics/data/materials_project_10k.json` (4.5 MB)
- **Loaded by:** mnemosyne/migrate_m2.py
- **URL:** https://materialsproject.org/

| Column | Type | Description |
|--------|------|-------------|
| mat_id | serial PK | Internal ID |
| material_id | text UNIQUE | Materials Project ID |
| band_gap | double | Electronic band gap (eV) |
| formation_energy_per_atom | double | Formation energy per atom (eV/atom) |
| spacegroup_number | smallint | Space group number |
| density | double | Density (g/cm^3) |
| volume | double | Unit cell volume (A^3) |
| nsites | integer | Number of sites in unit cell |
| source_id | integer FK | References core.data_source |

**Scripts:** mnemosyne/migrate_m2.py, harmonia/src/domain_index.py (load_materials)

---

### physics.pdg_particles -- Particle Data Group

- **Rows:** 226
- **Source:** Particle Data Group (pdg.lbl.gov), 2024 review
- **Source file:** `cartography/physics/data/pdg/particles.json` (100 KB)
- **Loaded by:** thesauros/ingest_empty_tables.py
- **URL:** https://pdg.lbl.gov/

| Column | Type | Description |
|--------|------|-------------|
| particle_id | serial PK | Internal ID |
| name | text | Particle name |
| pdg_id | integer | MC particle ID (first from mc_ids list) |
| mass_gev | double | Mass in GeV |
| charge | double | Electric charge |
| spin | double | Spin |
| lifetime_s | double | Lifetime in seconds (derived from width) |
| is_stable | boolean | Whether stable (width = 0 or null) |
| source_id | integer FK | References core.data_source |

**Scripts:** thesauros/ingest_empty_tables.py, cartography/v2/fricke_pdg_parity.py, cartography/v2/pdg_*.py

---

### analysis.fungrim -- Fungrim Mathematical Formulas

- **Rows:** 3,130
- **Source:** Fungrim project (fungrim.org) -- a database of mathematical formulas
- **Source file:** `cartography/fungrim/fungrim_formulas.json` (1.6 MB)
- **Loaded by:** thesauros/ingest_empty_tables.py
- **URL:** https://fungrim.org/

| Column | Type | Description |
|--------|------|-------------|
| formula_id | serial PK | Internal ID |
| fungrim_id | text UNIQUE | Fungrim ID, e.g. "4a2e64" |
| formula_type | text | Formula type (e.g. "Entry") |
| module | text | Module/topic category |
| n_symbols | smallint | Number of symbols in formula |
| formula_text | text | LaTeX or text representation of formula |
| source_id | integer FK | References core.data_source |

**Scripts:** thesauros/ingest_empty_tables.py, harmonia/src/domain_index.py (load_fungrim), cartography/fungrim/scripts/ingest_fungrim.py

---

### analysis.oeis -- Online Encyclopedia of Integer Sequences

- **Rows:** 394,454
- **Source:** OEIS (oeis.org) bulk download
- **Source files:** `cartography/oeis/data/oeis_names.json` (40 MB), `cartography/oeis/data/stripped_new.txt` (81 MB), `cartography/oeis/data/oeis_keywords.json` (10 MB)
- **Loaded by:** thesauros/ingest_oeis.py
- **URL:** https://oeis.org/

| Column | Type | Description |
|--------|------|-------------|
| seq_id | serial PK | Internal ID |
| oeis_id | text UNIQUE | OEIS ID, e.g. "A000001" |
| name | text | Sequence name/description |
| first_terms | bigint[] | First 20 terms of sequence |
| growth_rate | double | log(last_nonzero/first_nonzero) -- computed |
| entropy | double | Shannon entropy of term frequencies -- computed |
| is_monotone | boolean | Whether terms are non-decreasing -- computed |
| source_id | integer FK | References core.data_source |

**Additional data files not yet loaded:**
- `oeis_crossrefs.jsonl` (62 MB) -- cross-reference graph between sequences
- `oeis_formulas.jsonl` (60 MB) -- formula text per sequence
- `oeis_programs.jsonl` (73 MB) -- program code per sequence

**Scripts:** thesauros/ingest_oeis.py

---

### biology.metabolism -- Genome-Scale Metabolic Models (BiGG)

- **Rows:** 108
- **Source:** BiGG Models database (bigg.ucsd.edu)
- **Source files:** `cartography/metabolism/data/*.json` (109 individual model files, 256 MB total)
- **Loaded by:** thesauros/ingest_empty_tables.py
- **URL:** http://bigg.ucsd.edu/

| Column | Type | Description |
|--------|------|-------------|
| model_id | serial PK | Internal ID |
| bigg_id | text UNIQUE | BiGG model ID, e.g. "e_coli_core" |
| n_reactions | integer | Number of metabolic reactions |
| n_metabolites | integer | Number of metabolites |
| n_genes | integer | Number of genes |
| n_compartments | smallint | Number of cellular compartments |
| frac_reversible | double | Fraction of reactions that are reversible |
| source_id | integer FK | References core.data_source |

**Scripts:** thesauros/ingest_empty_tables.py

---

## prometheus_fire Database (M1:5432)

Working data: research results, cross-references, tensor data, signals. 598,606 total rows.

### xref.object_registry -- Universal Object Index

- **Rows:** 134,475
- **Source:** Migrated from charon.duckdb `objects` table (2026-04-15)
- **Loaded by:** mnemosyne/migrate_m2.py

| Column | Type | Description |
|--------|------|-------------|
| object_id | bigserial PK | Object ID (preserved from DuckDB) |
| source_db | text | Source database ("charon_duckdb") |
| source_table | text | Source table name |
| source_key | text | LMFDB label (join key to lmfdb tables) |
| object_type | text | "elliptic_curve", "modular_form", or "genus2_curve" |
| invariant_vector | double[] | Universal coordinates: a_p for first 50 primes |
| properties | jsonb | Type-specific metadata |
| conductor | bigint | Conductor |
| coefficient_completeness | double | Fraction of 50 primes with known a_p |

**UNIQUE:** (source_db, source_table, source_key)

**Scripts:** harmonia/src/domain_index.py (load_lmfdb_objects, load_ec_zeros, load_raw_zeros, etc.), thesauros/migrate_p3_duckdb.py, mnemosyne/migrate_m2.py

---

### xref.bridges -- Known Cross-Domain Correspondences

- **Rows:** 17,314
- **Source:** Migrated from charon.duckdb `known_bridges` table (2026-04-15)
- **Also in Redis:** bridge:{source_id}:{target_id} hashes + bridges:by_source/target/type set indexes
- **Loaded by:** mnemosyne/migrate_m2.py, thesauros/migrate_p3_duckdb.py (Redis)

| Column | Type | Description |
|--------|------|-------------|
| bridge_id | bigserial PK | Bridge ID |
| source_object_id | bigint FK | Source object (references object_registry) |
| target_object_id | bigint FK | Target object (references object_registry) |
| bridge_type | text | "modularity", "langlands", "galois", etc. |
| evidence_grade | text | Evidence quality |
| confidence | double | Confidence score |
| provenance | text | Source reference |
| created_at | timestamptz | When recorded |

**Scripts:** harmonia/src/domain_index.py (load_bridges), charon/src/build_graph.py, charon/tests/*.py

---

### zeros.object_zeros -- L-function Zeros per Object

- **Rows:** 120,649
- **Source:** Migrated from charon.duckdb `object_zeros` table (2026-04-16)
- **Loaded by:** thesauros/migrate_p3_duckdb.py

| Column | Type | Description |
|--------|------|-------------|
| object_id | bigint PK | References xref.object_registry |
| zeros_vector | double[] | Positive zeros on critical line |
| root_number | double | Root number (+1 or -1) |
| analytic_rank | smallint | Analytic rank |

**Scripts:** harmonia/src/domain_index.py (load_ec_zeros, load_raw_zeros, load_zeros_anchored, load_rmt_ensemble), ~40 charon/ and harmonia/ research scripts

---

### zeros.dirichlet_zeros -- L-function Zeros by Conductor

- **Rows:** 184,830
- **Source:** Migrated from charon.duckdb `dirichlet_zeros` table (2026-04-16)
- **Loaded by:** thesauros/migrate_p3_duckdb.py
- **Indexes:** idx_dirichlet_conductor, idx_dirichlet_url

| Column | Type | Description |
|--------|------|-------------|
| id | bigserial PK | Internal ID |
| lmfdb_url | text | LMFDB URL path for this L-function |
| conductor | bigint | Conductor |
| degree | smallint | Degree of L-function |
| zeros_vector | double[] | Positive zeros on critical line |
| n_zeros_stored | smallint | Number of zeros in vector |
| motivic_weight | smallint | Motivic weight |

**Scripts:** harmonia/src/domain_index.py (load_dirichlet_zeros), charon/src/ingest_dirichlet_*.py

---

### zeros.object_zeros_ext -- Extended Zero Data

- **Rows:** 17,313
- **Source:** Migrated from charon.duckdb `object_zeros_ext` table (2026-04-16)
- **Loaded by:** thesauros/migrate_p3_duckdb.py

| Column | Type | Description |
|--------|------|-------------|
| id | bigserial PK | Internal ID |
| lmfdb_url | text UNIQUE | LMFDB URL path |
| conductor | bigint | Conductor |
| rank | smallint | Rank |
| zeros_vector | double[] | Extended zeros |
| n_zeros_raw | smallint | Number of zeros before filtering |
| n_zeros_stored | smallint | Number of zeros stored |

---

### analysis.disagreement_atlas -- Embedding Disagreement Map

- **Rows:** 119,397
- **Source:** Migrated from charon.duckdb `disagreement_atlas` table (2026-04-16)
- **Originally computed by:** charon/src/disagreement_atlas.py
- **Loaded by:** thesauros/migrate_p3_duckdb.py

| Column | Type | Description |
|--------|------|-------------|
| object_id | bigint PK | References object_registry |
| label | text | LMFDB label |
| object_type | text | Object type |
| conductor | bigint | Conductor |
| rank | smallint | Rank |
| torsion | smallint | Torsion order |
| cm | smallint | CM discriminant |
| jaccard | double | Jaccard similarity (embedding vs zero neighbors) |
| precision_score | double | Precision of embedding neighbors |
| recall_score | double | Recall of zero-based neighbors |
| zero_coherence | double | Coherence between zero and graph structure |
| graph_degree | integer | Degree in knowledge graph |
| component_size | integer | Connected component size |
| n_zero_nn | integer | Number of zero-based nearest neighbors |
| n_graph_nn | integer | Number of graph nearest neighbors |
| n_overlap | integer | Overlap between neighbor sets |
| disagreement_type | text | Type classification (A/B/C/D) |

**Scripts:** harmonia/src/domain_index.py (load_disagreement), charon/src/disagreement_atlas.py, charon/src/inner_twist_*.py

---

### noesis.* -- Noesis Research State (19 tables)

- **Total rows:** 51,992
- **Source:** Migrated from noesis/v2/noesis_v2.duckdb (2026-04-16)
- **Loaded by:** thesauros/migrate_noesis_v2.py

| Table | Rows | Description |
|-------|------|-------------|
| cross_domain_edges | 20,502 | Cross-domain operator connections |
| depth2_matrix | 19,049 | Depth-2 operator composition status |
| composition_instances | 4,962 | Instances of compositions in traditions |
| tradition_hub_matrix | 2,213 | Tradition-to-hub mappings |
| floor1_matrix | 2,120 | Floor 1 operator resolution evidence |
| operations | 1,714 | Mathematical operations catalog |
| chain_steps | 400 | Steps within operator chains |
| transformations | 295 | Operator transformations |
| abstract_compositions | 236 | Abstract composition patterns |
| cross_domain_links | 185 | Cross-domain link metadata |
| ethnomathematics | 131 | Ethnomathematical systems catalog |
| chains | 100 | Operator chains with verification status |
| discoveries | 35 | Discovered patterns/structures |
| depth3_probes | 19 | Depth-3 composition probes |
| tradition_multi_hub | 10 | Multi-hub tradition mappings |
| damage_operators | 9 | Damage operator definitions |
| prime_landscape | 6 | Prime landscape features |
| validation_pairs | 6 | Cross-domain validation pairs |
| reclassification_log | 0 | Reclassification audit trail |

---

### signals.specimens -- Signal/Hypothesis Tracking

- **Rows:** 0 (schema only, ready for population)
- **Created:** 2026-04-16
- **Purpose:** Track discovered signals, their battery results, and kill status

| Column | Type | Description |
|--------|------|-------------|
| specimen_id | bigserial PK | Internal ID |
| claim | text | What the signal claims |
| status | text | ALIVE, KILLED, MARGINAL |
| interest | double | Interest score |
| kill_test | text | Which test killed it |
| domain_a, domain_b | text | Domain pair |
| created_at, killed_at | timestamptz | Timestamps |

### signals.battery_results -- Battery Test Results per Specimen

- **Rows:** 0 (schema only)

| Column | Type | Description |
|--------|------|-------------|
| id | bigserial PK | Internal ID |
| specimen_id | bigint FK | References specimens |
| test_name | text | Battery test name |
| result | text | passed, failed, not_run |
| z_score | double | z-score |
| p_value | double | p-value |
| detail | jsonb | Full test output |
| run_at | timestamptz | When run |

---

### agora.messages -- Multi-Agent Communication Log

- **Rows:** 107
- **Source:** Agora Redis streams, persisted by agora/client.py
- **Also in Redis:** agora:main, agora:challenges, agora:discoveries, agora:tasks streams

| Column | Type | Description |
|--------|------|-------------|
| id | serial PK | Internal ID |
| stream_id | text | Redis stream message ID |
| stream | text | Which stream (main, challenges, discoveries, tasks) |
| sender | text | Agent name (Agora, Kairos, Harmonia, etc.) |
| machine | text | M1 or M2 |
| msg_type | text | announce, challenge, share, kill, etc. |
| subject | text | Message subject line |
| body | text | Full message body |
| confidence | real | Confidence score (0.0-1.0) |
| evidence | text | Supporting evidence |
| reply_to | text | Message ID being replied to |
| created_at | timestamptz | Timestamp |

### agora.decisions -- Team Decisions

- **Rows:** 3

### agora.open_questions -- Open Research Questions

- **Rows:** 1

---

### Empty Tables (Schema Ready, No Data)

| Table | Purpose |
|-------|---------|
| results.ergon_runs | Ergon evolutionary run metadata |
| results.hypotheses | Generated hypotheses with z-scores |
| results.harmonia_bonds | TT-Cross bond decomposition results |
| kill.taxonomy | Kill classification system |
| kill.shadow_cells | Shadow archive (dead zone tracking) |
| tensor.domain_features | Per-object feature values |
| tensor.domain_metadata | Domain metadata (feature names, counts) |
| meta.calibration | Calibration test results |

---

## Redis (M1:6379, password: prometheus)

### Agora Communication (existing)
| Key Pattern | Type | Count | Description |
|-------------|------|-------|-------------|
| agora:main | Stream | ~120 msgs | General communication |
| agora:challenges | Stream | ~15 msgs | Adversarial challenges |
| agora:discoveries | Stream | ~25 msgs | Shared findings |
| agora:tasks | Stream | ~6 msgs | Task coordination |
| agent:{name} | Hash | ~8 agents | Agent state (status, heartbeat, machine) |

### Knowledge Graph (migrated from DuckDB 2026-04-16)
| Key Pattern | Type | Count | Description |
|-------------|------|-------|-------------|
| graph:neighbors:{id} | Set | 96,210 | Adjacency list per object (undirected, 396K edges) |

### Landscape (migrated from DuckDB 2026-04-16)
| Key Pattern | Type | Count | Description |
|-------------|------|-------|-------------|
| landscape:{id} | Hash | 119,464 | {coordinates, curvature, cluster_id, version} |
| landscape:by_curvature | Sorted Set | 119,464 | Score=curvature, member=object_id |
| landscape:by_cluster:{id} | Set | varies | Object IDs per cluster |

### Bridges (migrated from DuckDB 2026-04-16)
| Key Pattern | Type | Count | Description |
|-------------|------|-------|-------------|
| bridge:{src}:{tgt} | Hash | 17,314 | {type, verified, source_reference} |
| bridges:by_source:{id} | Set | varies | Bridge keys by source |
| bridges:by_target:{id} | Set | varies | Bridge keys by target |
| bridges:by_type:{type} | Set | varies | Bridge keys by type |

### Hypothesis Queue (migrated from DuckDB 2026-04-16)
| Key Pattern | Type | Count | Description |
|-------------|------|-------|-------------|
| hypothesis:queue | Sorted Set | 100 | Score=priority, member=hypothesis JSON |

### Other State
| Key Pattern | Type | Description |
|-------------|------|-------------|
| hypotheses:alive | Set | Active hypotheses |
| hypotheses:killed | Set | Killed hypotheses |
| leaderboard:kills | Sorted Set | Kill count per agent |
| leaderboard:discoveries | Sorted Set | Discovery count per agent |

---

## Known Data Quality Issues

1. **LMFDB all-text columns** -- every column is TEXT. Use explicit casts (::int, ::bigint, ::double precision) in queries.
2. **Sha circularity at rank >= 2** -- LMFDB computes Sha by assuming BSD. Cannot use for independent BSD testing. See bsd_joined_view.md.
3. **Missing EC ingredients** -- real_period (Omega) and tamagawa_product not in ec_curvedata. Needed for full BSD formula.
4. **LMFDB selection effects** -- high-conductor ECs biased toward prime conductors. Stratify by num_bad_primes.
5. **lfunc coverage gap** -- bsd_joined has 0% coverage above conductor 400K. 747K EC curves have no L-function data.
6. **Isogeny-level join** -- bsd_joined joins at isogeny class level. Multiple EC rows share one lfunc row.
7. ~~**nf_fields partial**~~ -- FULLY LOADED as of 2026-04-16 (22,178,569 rows). Lehmer, Brumer-Stark, Leopoldt tests unblocked.
8. **Noesis data is research state** -- not validated scientific data. Treat as exploratory.
