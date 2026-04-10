# Data Sprint — 2026-04-09

## Sources

Three acquisition channels fired simultaneously:

| Channel | Method | Yield |
|---------|--------|-------|
| Browser downloads | LMFDB search page bulk export, parsed via `parse_lmfdb_downloads.py` | 10 datasets, 1.63M records |
| API JSON | `fetch_lmfdb_frontiers.py`, `lmfdb_paginate.py` | 5 Siegel tables |
| PostgreSQL mirror | `lmfdb_postgres_dump.py` against devmirror.lmfdb.xyz:5432 | 271 files, 23 GB |

Scripts: `cartography/shared/scripts/{fetch_lmfdb_frontiers,lmfdb_paginate,lmfdb_postgres_dump,lmfdb_dump_chunk,parse_lmfdb_downloads}.py`

---

## New Datasets Ready to Wire

### Tier 1: Massive expansions of existing datasets

| Dataset | Was | Now | Expansion | Location | Format |
|---------|-----|-----|-----------|----------|--------|
| **Maass forms (rigorous)** | 300 | **35,416** | 118x | `lmfdb_dump/maass_rigor.json` + `maass/data/maass_rigor_full.json` | JSON, spectral params to 100+ digits |
| **Lattices** | 21 | **39,293** | 1,871x | `lmfdb_dump/lat_lattices.json` + `lattices/data/lattices_full.json` | JSON, dim/det/level/class_number/aut |
| **Genus-2 curves** | 100 | **66,158** | 662x | `lmfdb_dump/g2c_curves.json` + `genus2/data/genus2_curves_lmfdb.json` | JSON, full LMFDB fields |

### Tier 2: Entirely new datasets

| Dataset | Records | Location | Key Fields |
|---------|---------|----------|------------|
| **Siegel modular forms** | 129 samples + 3,094 eigenvalues + 26,212 Fourier coefficients | `genus2/data/siegel_*.json` + `lmfdb_dump/smf_*.json` | Hecke eigenvalues, q-expansion, weight, degree |
| **Hilbert modular forms** | 368,356 forms (400 fields) | `lmfdb_dump/hmf_*.json` | Level, weight, Hecke eigenvalues over real quadratic fields |
| **Bianchi modular forms** | 233,333 forms (456K dims) | `lmfdb_dump/bmf_*.json` | Level, weight over imaginary quadratic fields |
| **Hypergeometric motives** | 61,063 families + 285 motives | `lmfdb_dump/hgm_*.json` + `lmfdb_hgm_motives_0409_2058.txt` | A/B params, degree, weight, Hodge vector, monodromy |
| **Abstract groups** | 544,831 | `groups/abstract_groups.json` | Label, order, exponent, conjugacy classes, center |

### Tier 3: Significant companion data

| Dataset | Size | Location | Content |
|---------|------|----------|---------|
| Maass coefficients | 2.1 GB | `lmfdb_dump/maass_rigor_coefficients.json` | Fourier coefficients for all 35K forms |
| Maass extras | 2.1 GB | `lmfdb_dump/maass_rigor_extras.json` | Extended eigenvalue data |
| Siegel Fourier coeffs | 619 MB | `lmfdb_dump/smf_fc.json` | Full q-expansion data |
| Genus-2 endomorphisms | 37 MB | `lmfdb_dump/g2c_endomorphisms.json` | End ring classification |
| Genus-2 Galois reps | 5.1 MB | `lmfdb_dump/g2c_galrep.json` | Galois image data |
| Genus-2 rational pts | 20 MB | `lmfdb_dump/g2c_ratpts.json` | Rational point data |
| Modular Galois reps | 212 MB | `lmfdb_dump/modlgal_reps.json` | Mod-ell representations |
| Transitive groups | 534 MB | `lmfdb_dump/gps_transitive.json` | Transitive permutation groups |
| Sato-Tate groups | 10 MB | `lmfdb_dump/gps_st.json` | ST group classifications |
| Belyi maps | 7.9 MB | `lmfdb_dump/belyi_galmaps.json` | Dessins d'enfants |
| Modular curves | 80 MB models + 372 MB decomp | `lmfdb_dump/modcurve_*.json` | Models, Jacobian decomposition |
| L-functions | various | `lmfdb_dump/lfunc_*.json` | L-function instances |
| Artin representations | various | `lmfdb_dump/artin_reps*.json` | Artin L-functions |
| Siegel newforms | 42 MB | `lmfdb_dump/smf_newforms.json` | Siegel newform database |
| Siegel newspaces | 51 MB | `lmfdb_dump/smf_newspaces.json` | Dimension data |

---

## Data Format

All PostgreSQL dumps follow a consistent JSON envelope:
```json
{
  "source": "LMFDB PostgreSQL mirror",
  "table": "<table_name>",
  "columns": ["col1", "col2", ...],
  "fetched": "2026-04-09T17:XX:XX",
  "total_records": N,
  "records": [{"col1": val1, ...}, ...]
}
```

Browser downloads were parsed by `parse_lmfdb_downloads.py` from tab-separated LMFDB text format into the same JSON structure.

---

## Wiring Priority

### Sprint 1: Wire the three massive expansions (Maass, Lattices, Genus-2)
These replace existing small datasets with orders-of-magnitude more data. The search functions already exist — they just need to point at the larger files and handle the new field names.

- **Maass**: 300 -> 35,416. Spectral parameter analysis becomes statistically meaningful. Gap distributions, level correlations, Fricke eigenvalue patterns all become testable.
- **Lattices**: 21 -> 39,293. Was too small for any statistical test. Now large enough for genuine cross-dataset comparison.
- **Genus-2**: 100 -> 66,158. The GSp_4 congruence machinery already exists. Full dataset enables conductor-level statistics, rank distributions, torsion patterns.

### Sprint 2: Wire the new automorphic forms
- **Siegel modular forms**: Direct comparison target for genus-2 congruences. The 3,094 eigenvalues and 26,212 Fourier coefficients are the "other side" of paramodular congruences.
- **Hilbert modular forms**: 368K forms over real quadratic fields. Bridge to number fields, base change, Langlands functoriality.
- **Bianchi modular forms**: 233K forms over imaginary quadratic fields. Same bridge, different arithmetic.

### Sprint 3: Wire the new arithmetic datasets
- **Hypergeometric motives**: 61K families. Connects to L-functions, Galois representations, and special values of zeta functions. Rich structure in the Hodge vectors.
- **Abstract groups**: 545K groups. Connects to Galois groups in number fields, automorphism groups in lattices, and symmetry classifications everywhere.

### Sprint 4: Deep companion data
- Maass coefficients (2.1 GB) for coefficient-level probes
- Genus-2 endomorphisms + Galois reps for the depth layer
- Siegel Fourier coefficients for q-expansion comparison
- Modular Galois representations for the GL_2/GSp_4 congruence story

---

## Post-Wiring Checklist

After each sprint, run:
```bash
cd cartography/shared/scripts
python realign.py          # inventory -> concept index -> tensor bridges -> 180-test battery
```

If the 180-test known truth battery drops below 100%, STOP and investigate.

---

## Companion Data Not Yet Prioritized

The 23 GB dump contains ~271 files. Most are portraits/visualizations (5.1 GB EC portraits, 3.4 GB Maass portraits, 1.5 GB modular curve pictures, 1.4 GB genus-2 plots). These are not useful for the search engine but could feed future visualization tools.

Metadata tables (`meta_*.json`, `kwl_*.json`, `test_*.json`) are system tables, not mathematical content.

---

*Sprint started: 2026-04-09*
*Data pulled by: parallel Claude Code instance via PostgreSQL mirror + browser downloads + API*
*Total new cargo: ~25 GB raw, ~1.7M searchable records across 8 new/expanded datasets*
