# LMFDB Mirror — PostgreSQL

**Database:** lmfdb  
**Host:** 192.168.1.176:5432  
**User:** lmfdb / lmfdb  
**Access:** Read-only  
**Total size:** ~350 GB  

## Tables

| Table | Rows | Size | Origin |
|-------|------|------|--------|
| lfunc_lfunctions | 24,351,376 | 341 GB | devmirror.lmfdb.xyz CSV dump |
| ec_curvedata | 3,824,372 | — | devmirror.lmfdb.xyz CSV dump |
| mf_newforms | ~1,100,000 | — | devmirror.lmfdb.xyz CSV dump |
| artin_reps | ~793,000 | — | devmirror.lmfdb.xyz CSV dump |
| g2c_curves | 66,158 | — | devmirror.lmfdb.xyz CSV dump |

**Note:** All columns are TEXT type (raw LMFDB dump format). Numerical queries require explicit casts.

## Indexes

| Index | Table | Size | Purpose |
|-------|-------|------|---------|
| idx_lfunc_conductor_numeric | lfunc_lfunctions | 523 MB | conductor::numeric for binned queries |

## Key Columns by Table

### ec_curvedata (52 columns)
Elliptic curves over Q. Key fields:
- `lmfdb_label` — unique identifier (e.g., "11.a1")
- `conductor` — (text, cast to numeric)
- `rank`, `analytic_rank` — independently computed
- `ainvs` — curve coefficients [a1,a2,a3,a4,a6]
- `regulator`, `sha`, `torsion`, `torsion_structure`
- `faltings_height`, `stable_faltings_height`, `manin_constant`
- `bad_primes`, `isogeny_degrees`, `class_size`
- `abc_quality`, `szpiro_ratio` — precomputed
- `lmfdb_iso` — isogeny class label

**Not available:** real_period (Omega), tamagawa_product, root_number

### lfunc_lfunctions (70 columns)
L-functions across all families. Key fields:
- `label` — L-function label (e.g., "2-11-11.10-c1-0-0")
- `origin` — source object (e.g., "ModularForm/GL2/Q/holomorphic/...")
- `conductor` — (text, indexed as numeric)
- `degree`, `motivic_weight` — L-function parameters
- `positive_zeros` — comma-separated zero values
- `leading_term` — L^(r)(E,1)/r! at central point
- `root_number`, `sign_arg`
- `symmetry_type`, `st_group` — Sato-Tate data

### artin_reps (22 columns)
- `Baselabel` — identifier (e.g., "2.12435.6t3.f")
- `Dim`, `Conductor`, `Galn`, `Galt`
- `Is_Even`, `Indicator` — parity and type
- **No direct linkage to lfunc_lfunctions.** Artin L-functions stored under ModularForm origins via Langlands.

### mf_newforms
- Used for Langlands GL(2) calibration (weight-1 forms ↔ odd Artin reps)
- 1.08M forms at weight ≥ 2 are untouched

### g2c_curves (genus-2)
- 66,158 curves — completely untouched by analysis so far

## Origin

All CSV dumps pulled from devmirror.lmfdb.xyz (public LMFDB development mirror).
Original files stored at `F:\lmfdb_local\` on M1.

| File | Status |
|------|--------|
| g2c_curves.csv (40 MB) | DONE |
| artin_reps.csv (445 MB) | DONE |
| mf_newforms.csv (8 GB) | DONE |
| ec_curvedata.csv (1.8 GB) | DONE |
| lfunc_lfunctions.csv (~43 GB) | DONE |
