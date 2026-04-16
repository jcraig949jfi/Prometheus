# Prometheus Data Dictionary

Every column in every table across all databases. The single source of truth for what a field means, what type it is, and where it came from.

Last updated: 2026-04-15

---

## LMFDB Mirror (`lmfdb` database)

All columns are **TEXT** type in the mirror (raw CSV dump). Cast as needed.

### ec_curvedata — Elliptic Curves over Q

3,824,372 rows. Origin: devmirror.lmfdb.xyz

| Column | Semantic Type | Description |
|--------|--------------|-------------|
| id | identifier | Internal row ID |
| lmfdb_label | identifier | Unique LMFDB label (e.g., "11.a1"). Format: `{conductor}.{iso_class}{curve_number}` |
| Clabel | identifier | Cremona label |
| lmfdb_iso | identifier | Isogeny class label (e.g., "11.a"). Groups curves in same isogeny class |
| Ciso | identifier | Cremona isogeny class |
| lmfdb_number | integer | Curve number within isogeny class |
| Cnumber | integer | Cremona curve number |
| iso_nlabel | integer | Isogeny class number label |
| conductor | numeric | Conductor N. Central invariant. Indexed as numeric (idx_lfunc_conductor_numeric) |
| rank | integer | Algebraic rank (Mordell-Weil). Independently computed from analytic_rank |
| analytic_rank | integer | Order of vanishing of L(E,s) at s=1. Independently computed from rank |
| ainvs | array | Short Weierstrass coefficients [a1,a2,a3,a4,a6] |
| jinv | text | j-invariant (rational number as string) |
| cm | integer | CM discriminant (0 if no CM) |
| torsion | integer | Size of torsion subgroup |
| torsion_structure | array | Torsion group structure (e.g., [2,4] for Z/2 × Z/4) |
| torsion_primes | array | Primes dividing torsion order |
| regulator | float | Regulator (determinant of height pairing matrix) |
| sha | integer | Analytic order of Sha (Tate-Shafarevich group). **CAUTION:** For rank ≥ 2, computed ASSUMING BSD. Circular for BSD testing. |
| sha_primes | array | Primes dividing Sha order |
| signD | integer | Sign of discriminant (+1 or -1) |
| absD | numeric | Absolute value of minimal discriminant |
| bad_primes | array | List of primes of bad reduction |
| num_bad_primes | integer | Count of bad primes |
| degree | integer | Modular degree |
| class_size | integer | Number of curves in isogeny class |
| class_deg | integer | Maximal isogeny degree in class |
| isogeny_degrees | array | Degrees of isogenies to optimal curve |
| optimality | integer | Whether curve is optimal in its class |
| manin_constant | integer | Manin constant (conjectured 1 for optimal curves) |
| semistable | boolean | Whether curve has semistable reduction everywhere |
| potential_good_reduction | boolean | Whether curve has potential good reduction |
| faltings_height | float | Faltings height |
| stable_faltings_height | float | Stable Faltings height. Related to Omega via: Omega ≈ exp(-stable_faltings_height) × correction |
| faltings_index | integer | Faltings index within isogeny class |
| faltings_ratio | integer | Faltings ratio (integer, related to isogeny invariant) |
| min_quad_twist_ainvs | array | Coefficients of minimal quadratic twist |
| min_quad_twist_disc | integer | Discriminant of minimal quadratic twist |
| num_int_pts | integer | Number of known integral points |
| abc_quality | float | abc quality: q = log|Δ|/log(N). **Precomputed.** |
| szpiro_ratio | float | Szpiro ratio: log|Δ|/log(N). **Precomputed.** Same as abc_quality. |
| nonmax_primes | array | Primes where Galois representation is non-maximal |
| nonmax_rad | integer | Product of non-maximal primes |
| elladic_images | text | ℓ-adic Galois image data |
| modell_images | text | mod-ℓ Galois image labels |
| adelic_level | integer | Adelic level |
| adelic_index | integer | Adelic index |
| adelic_genus | integer | Adelic genus |
| modm_images | text | mod-m image data |
| serre_invariants | text | Serre invariants |
| intrinsic_torsion | text | Intrinsic torsion data |
| squarefree_disc | numeric | Squarefree part of discriminant |
| trace_hash | integer | Hash of Frobenius traces (for fast matching) |

**Not available:** real_period (Omega), tamagawa_product, root_number

### lfunc_lfunctions — L-functions

24,351,376 rows. 341 GB. Origin: devmirror.lmfdb.xyz

| Column | Semantic Type | Description |
|--------|--------------|-------------|
| label | identifier | L-function label (e.g., "2-11-11.10-c1-0-0"). Encodes degree-conductor-character-weight |
| origin | identifier | Source object path (e.g., "ModularForm/GL2/Q/holomorphic/11/2/a/a/1/1") |
| conductor | numeric | Conductor (indexed via idx_lfunc_conductor_numeric) |
| degree | integer | Degree of the L-function (1=Dirichlet, 2=EC/MF, higher for Artin etc.) |
| motivic_weight | integer | Weight in the motivic sense |
| positive_zeros | array (text) | Comma-separated imaginary parts of non-trivial zeros on the critical line |
| leading_term | float | L^(r)(E,1)/r! — the leading Taylor coefficient at s=1 |
| root_number | complex | Root number of the functional equation |
| sign_arg | float | Argument of the root number |
| order_of_vanishing | integer | Analytic rank (order of zero at central point) |
| symmetry_type | text | Symmetry type (orthogonal/symplectic/unitary) |
| st_group | text | Sato-Tate group |
| algebraic | boolean | Whether L-function is algebraic |
| self_dual | boolean | Whether L(s) = L*(s) |
| primitive | boolean | Whether L-function is primitive |
| gamma_factors | text | Gamma factor data for functional equation |
| euler_factors | text | Euler product factors at good primes |
| bad_lfactors | text | Local factors at bad primes |
| dirichlet_coefficients | text | First few Dirichlet coefficients |
| accuracy | integer | Decimal digits of accuracy |
| precision | integer | Bits of precision |
| plot_values | text | Precomputed plot data |
| a2–a10, A2–A10 | float | Individual Dirichlet/Euler coefficients |
| z1, z2, z3 | float | First few zeros |
| coefficient_field | text | Field of definition for coefficients |
| trace_hash | integer | Hash for fast matching |
| analytic_conductor | float | Analytic conductor |
| root_analytic_conductor | float | Root of analytic conductor |
| bad_primes | array | List of bad primes |
| conductor_radical | integer | Radical of conductor |
| mu_real, mu_imag | array | Mu parameters (real/imaginary parts) |
| nu_real_doubled, nu_imag | array | Nu parameters |
| prelabel | text | Pre-assigned label |
| spectral_label | text | Spectral label |
| credit | text | Data attribution |

**Join key to ec_curvedata:** Not straightforward. `origin` field contains paths like "ModularForm/GL2/Q/holomorphic/..." for EC L-functions (via modularity), not direct EC labels. Join strategy TBD — see proposals.

### artin_reps — Artin Representations

~793,000 rows. Origin: devmirror.lmfdb.xyz

| Column | Semantic Type | Description |
|--------|--------------|-------------|
| Baselabel | identifier | Artin representation label (e.g., "2.12435.6t3.f") |
| Dim | integer | Dimension of the representation |
| Conductor | numeric | Artin conductor |
| Galn | integer | Order of Galois group |
| Galt | integer | Transitive group label (nTt format, t component) |
| Container | text | Container representation |
| Indicator | integer | Frobenius-Schur indicator (+1 orthogonal, -1 symplectic, 0 complex) |
| Is_Even | boolean | Whether the representation is even (det = trivial) |
| BadPrimes | array | Primes where rep is ramified |
| HardPrimes | array | Primes requiring special treatment |
| GaloisConjugates | array | Galois conjugate representations |
| GalConjSigns | array | Signs of Galois conjugates |
| CharacterField | integer | Degree of character field |
| NFGal | text | Associated number field Galois closure |
| Hide | boolean | Whether to hide in LMFDB display |
| Dets | text | Determinant character data |
| GaloisLabel | text | Galois group label |
| Proj_GAP | integer | Projective image GAP ID |
| Proj_nTj | text | Projective image transitive group |
| Proj_Polynomial | text | Projective image polynomial |
| NumBadPrimes | integer | Count of bad primes |

**Linkage to lfunc:** No direct Artin entries found in lfunc_lfunctions.origin. Artin L-functions stored under ModularForm origins via Langlands correspondence.

### mf_newforms — Modular Forms

~1,100,000 rows. Origin: devmirror.lmfdb.xyz. Schema not yet fully audited.

### g2c_curves — Genus-2 Curves

66,158 rows. Origin: devmirror.lmfdb.xyz. **Completely untouched by analysis.** Schema not yet fully audited.

---

## prometheus_sci Database

### core.data_source — Provenance Tracking

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| source_id | SERIAL PK | NO | Auto-increment ID |
| name | TEXT | NO | Human-readable source name (e.g., "materials_project_10k") |
| origin_url | TEXT | YES | URL of original data source |
| file_path | TEXT | YES | Local file path of source data |
| loaded_at | TIMESTAMPTZ | YES | When data was ingested |
| row_count | INTEGER | YES | Number of rows loaded |
| checksum | TEXT | YES | File checksum for change detection |

### topology.knots — Knot Invariants

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| knot_id | SERIAL PK | NO | Auto-increment ID |
| name | TEXT | NO | Knot name (e.g., "3_1" for trefoil) |
| crossing_number | SMALLINT | YES | Minimum crossing number |
| determinant | INTEGER | YES | Knot determinant |
| alexander_coeffs | DOUBLE[] | YES | Alexander polynomial coefficients |
| jones_coeffs | DOUBLE[] | YES | Jones polynomial coefficients |
| conway_coeffs | DOUBLE[] | YES | Conway polynomial coefficients |
| signature | SMALLINT | YES | Knot signature |
| source_id | INTEGER FK | YES | → core.data_source |

### topology.polytopes — Polytopes

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| polytope_id | SERIAL PK | NO | Auto-increment ID |
| name | TEXT | YES | Collection/source name |
| dimension | SMALLINT | YES | Ambient dimension |
| n_vertices | INTEGER | YES | Number of vertices |
| n_edges | INTEGER | YES | Number of edges |
| n_facets | INTEGER | YES | Number of facets |
| f_vector | INTEGER[] | YES | Full f-vector [f0, f1, ..., fd] |
| is_simplicial | BOOLEAN | YES | Whether all facets are simplices |
| source_id | INTEGER FK | YES | → core.data_source |

### chemistry.qm9 — Quantum Molecules

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| mol_id | SERIAL PK | NO | Auto-increment ID |
| smiles | TEXT | YES | SMILES molecular notation |
| homo | DOUBLE | YES | HOMO energy (Hartree) |
| lumo | DOUBLE | YES | LUMO energy (Hartree) |
| homo_lumo_gap | DOUBLE | YES | HOMO-LUMO gap (eV) |
| zpve | DOUBLE | YES | Zero-point vibrational energy (Hartree) |
| polarizability | DOUBLE | YES | Isotropic polarizability (Bohr³) |
| n_atoms | SMALLINT | YES | Total atom count |
| source_id | INTEGER FK | YES | → core.data_source |

### physics.materials — Materials Project

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| mat_id | SERIAL PK | NO | Auto-increment ID |
| material_id | TEXT | YES | Materials Project ID (e.g., "mp-1197903") |
| band_gap | DOUBLE | YES | Electronic band gap (eV) |
| formation_energy_per_atom | DOUBLE | YES | Formation energy per atom (eV/atom) |
| spacegroup_number | SMALLINT | YES | International space group number (1-230) |
| density | DOUBLE | YES | Density (g/cm³) |
| volume | DOUBLE | YES | Unit cell volume (ų) |
| nsites | INTEGER | YES | Number of sites in unit cell |
| source_id | INTEGER FK | YES | → core.data_source |

### physics.superconductors, physics.codata, physics.pdg_particles

Empty. Schema defined in `scripts/db_setup.sql`. See `thesauros/postgres_sci.md`.

### algebra.groups — Abstract Groups

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| group_id | SERIAL PK | NO | Auto-increment ID |
| label | TEXT | YES | GAP-style label (e.g., "60.5" for A5) |
| order_val | NUMERIC | YES | Group order. **NUMERIC** (not INT) — some orders exceed 60 digits |
| exponent | NUMERIC | YES | Group exponent. **NUMERIC** for same reason |
| n_conjugacy | INTEGER | YES | Number of conjugacy classes |
| is_abelian | BOOLEAN | YES | Whether group is abelian |
| is_solvable | BOOLEAN | YES | Whether group is solvable |
| source_id | INTEGER FK | YES | → core.data_source |

### algebra.space_groups, algebra.lattices, analysis.fungrim, analysis.oeis, biology.metabolism

See `thesauros/postgres_sci.md` for column definitions. All either empty or small.

---

## prometheus_fire Database

### xref.object_registry — Universal Object Index

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| object_id | BIGSERIAL PK | NO | Universal object ID (preserves DuckDB IDs) |
| source_db | TEXT | NO | Origin database ("charon_duckdb", "lmfdb", "sci") |
| source_table | TEXT | NO | Origin table within source_db |
| source_key | TEXT | NO | Primary key in source table (label or ID) |
| object_type | TEXT | NO | Domain type (matches DOMAINS enum: "EC", "MF", etc.) |

### xref.bridges — Known Cross-Domain Correspondences

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| bridge_id | BIGSERIAL PK | NO | Auto-increment ID |
| source_object_id | BIGINT FK | YES | → object_registry |
| target_object_id | BIGINT FK | YES | → object_registry |
| bridge_type | TEXT | NO | Type of correspondence (e.g., "modularity", "L-function") |
| evidence_grade | TEXT | YES | "verified" or "unverified" |
| confidence | DOUBLE | YES | 0.0-1.0 confidence score |
| provenance | TEXT | YES | Source reference or method |
| created_at | TIMESTAMPTZ | YES | When bridge was recorded |

### results.hypotheses, results.ergon_runs, results.harmonia_bonds

See `thesauros/postgres_fire.md`. All empty — awaiting Ergon/Harmonia integration.

### kill.taxonomy, kill.shadow_cells

See `thesauros/postgres_fire.md`. Empty — shadow archive currently in Redis.

### tensor.domain_features, tensor.domain_metadata

See `thesauros/postgres_fire.md`. Empty — tensor data currently in .npz files.

### meta.ingestion_log

4 rows from M2 migration. Tracks what was loaded, when, how many rows, success/failure.

### agora.messages, agora.decisions, agora.open_questions, agora.agent_sessions

Communication persistence. See `thesauros/postgres_fire.md`.

---

## DuckDB Legacy (charon.duckdb)

See `thesauros/duckdb_legacy.md` for full table schemas. Key tables not yet migrated:

| Table | Rows | Key Columns |
|-------|------|-------------|
| elliptic_curves | 31K | object_id, lmfdb_label, conductor, rank, ainvs, torsion, regulator, sha, faltings_height, trace_hash |
| modular_forms | 102K | object_id, lmfdb_label, level, weight, dim, hecke_orbit, analytic_conductor, traces, field_poly |
| dirichlet_zeros | 185K | lmfdb_url, conductor, degree, rank, zeros_vector, motivic_weight |
| object_zeros | 121K | object_id, zeros_vector, root_number, analytic_rank |
| landscape | 119K | object_id, coordinates[], local_curvature, nearest_neighbors[], cluster_id |
| disagreement_atlas | 119K | object_id, label, jaccard, precision_score, recall_score, zero_coherence, graph_degree |
| graph_edges | 396K | source_id, target_id (k-NN knowledge graph) |

---

## Redis

No persistent schema — see `thesauros/redis.md` for namespace documentation.

---

## Known Data Quality Issues

1. **LMFDB all-text columns**: Every column in the LMFDB mirror is TEXT. Numerical queries require explicit casts (`conductor::numeric`). The conductor index mitigates this for one column.

2. **Sha circularity at rank ≥ 2**: `ec_curvedata.sha` for rank ≥ 2 is computed by assuming BSD. Cannot be used to test BSD independently. Rank 0-1 Sha is independently computed.

3. **Missing EC ingredients**: `real_period` (Omega), `tamagawa_product`, and `root_number` are not columns in ec_curvedata. Needed for full BSD formula.

4. **EC ↔ lfunc join key**: No direct label match. `lfunc_lfunctions.origin` uses ModularForm paths, not EC labels. Join strategy needed.

5. **Artin ↔ lfunc linkage**: No Artin-labeled entries in lfunc origin field. Linkage goes through ModularForm paths via Langlands.

6. **abc_quality vs szpiro_ratio**: Both columns exist in ec_curvedata and appear to store the same value (log|Δ|/log(N)). Verify before using both.

7. **groups.order_val**: Widened from INTEGER to NUMERIC because some group orders exceed 60 digits. Queries should cast appropriately.

8. **LMFDB selection effects**: High-conductor EC curves are biased toward prime conductors with fewer bad primes. Stratify by bad_primes count for unbiased analysis.
