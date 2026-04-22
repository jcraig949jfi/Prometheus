# Domain Catalog — Generator #3 Phase 1

**Generated:** 2026-04-20T23:08:35.924842+00:00
**Source:** `docs/prompts/gen_03_cross_domain_transfer.md` @ commit `ac354b26`
**Runner:** Harmonia_M2_sessionA_20260420

## Purpose

Canonical enumeration of the data domains we currently have measurement access to. Every domain has a schema, cardinality, and list of primary F-IDs that inhabit it. Phase 2 classifies each projection's applicability to each domain (the transfer matrix).

## Domains (7)

### D_EC — Elliptic curves over Q

- **Data source:** `lmfdb.ec_curvedata + lmfdb.bsd_joined + lmfdb.lfunc_lfunctions`
- **Cardinality:** ~3,824,372
- **Primary fields:** `conductor`, `rank`, `analytic_rank`, `torsion_order`, `cm_disc`, `root_number`, `regulator`, `sha_order`, `Lhash`, `class_size`, `nonmax_primes`, `semistable`, `bad_primes`, `kodaira_symbols`
- **Primary F-IDs already inhabiting this domain:** F001, F003, F004, F005, F009, F011, F013, F015, F030, F033, F041a, F042, F043, F044, F045

### D_NF — Number fields

- **Data source:** `lmfdb.nf_fields`
- **Cardinality:** ~22,000,000
- **Primary fields:** `degree`, `disc_abs`, `signature`, `galois_label`, `galois_group`, `class_number`, `regulator`, `ramified_primes`, `is_galois`
- **Primary F-IDs already inhabiting this domain:** F008, F010, F022

### D_MF — Classical modular forms (weight, level, character)

- **Data source:** `lmfdb.mf_newforms + lmfdb.mf_hecke_nf`
- **Cardinality:** ~450,000
- **Primary fields:** `weight`, `level`, `character_orbit`, `hecke_orbit`, `trace_hash`, `Lhash`, `dim`, `is_cm`, `is_rm`, `self_dual`, `analytic_rank`
- **Primary F-IDs already inhabiting this domain:** F001

### D_ARTIN — Artin representations

- **Data source:** `lmfdb.artin_reps`
- **Cardinality:** ~798,000
- **Primary fields:** `Dim`, `Conductor`, `GaloisGroup`, `Indicator`, `Is_Even`, `Baselabel`, `NFGal`
- **Primary F-IDs already inhabiting this domain:** F026

### D_G2C — Genus-2 curves over Q

- **Data source:** `lmfdb.g2c_curves`
- **Cardinality:** ~66,158
- **Primary fields:** `cond`, `disc`, `aut_grp`, `geom_aut_grp`, `torsion_grp`, `is_simple_geom`, `st_group`, `real_period`, `regulator`, `sha`, `mw_rank`
- **Primary F-IDs already inhabiting this domain:** F012

### D_KNOTS — Knot invariants and polynomials

- **Data source:** `harmonia/data/knots/ + KnotInfo mirror`
- **Cardinality:** ~12,965
- **Primary fields:** `alexander`, `jones`, `HOMFLY`, `kauffman`, `signature`, `genus`, `mahler_measure`
- **Primary F-IDs already inhabiting this domain:** F027, F032

### D_L — L-functions (cross-origin, generic)

- **Data source:** `lmfdb.lfunc_lfunctions`
- **Cardinality:** ~24,000,000
- **Primary fields:** `Lhash`, `origin`, `rational`, `gamma_factors`, `positive_zeros`, `plot_values`
- **Primary F-IDs already inhabiting this domain:** F011, F013, F031

## Transfer matrix summary

- **Projections:** 37
- **Domains:** 7
- **Total (P, D) cells:** 259
- **Verdict distribution:**
  - `applies_directly`: 120 (46.3%)
  - `inapplicable`: 115 (44.4%)
  - `applies_with_adaptation`: 24 (9.3%)

## Applies-directly breakdown by projection type

| Projection type | D_EC | D_NF | D_MF | D_ARTIN | D_G2C | D_KNOTS | D_L |
|---|---|---|---|---|---|---|---|
| categorical_object_level | 2 | 1 | 2 | 1 | 0 | 0 | 2 |
| feature_distribution | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| feature_extraction | 0 | 1 | 0 | 0 | 0 | 1 | 0 |
| magnitude_axis | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| null_model | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| preprocessing | 3 | 1 | 3 | 1 | 1 | 1 | 3 |
| stratification | 14 | 2 | 7 | 4 | 7 | 0 | 0 |

## Heuristic classification rules (v1)

See `harmonia/runners/gen_03_transfer_matrix.py::classify()`. Core logic:

- **Agnostic scorers** (null_model, preprocessing, feature_distribution, etc.) default to `applies_directly` unless the projection references a domain-specific data object (e.g., zero-spacings require L-function origin; Mahler measure requires polynomial representative).
- **Stratifications** are `applies_directly` iff the stratifying field appears in the domain's schema; `inapplicable` otherwise.
- **Ambiguous** cases resolve to `applies_with_adaptation` — these become tasks to define the adapter.

**Known limitation:** the v1 classifier is a keyword heuristic. False-positives (marked directly-applicable but actually need adaptation) and false-negatives both exist. Phase 3 audits against specimen-level runs will calibrate the classifier over time.

## Epistemic discipline

1. **An adapter is a new projection.** Any `applies_with_adaptation` run that produces a valid measurement emits a new P-ID via `reserve_p_id()`, not a re-use of the origin ID.
2. **Apparent transfers are Pattern 5 candidates.** A projection that works in two domains may be measuring shared known structure (Langlands, class field theory). Pattern 5 check required before novelty claim.
3. **Pattern 30 gate** applies to every correlation-based transfer.
4. **Null-protocol claim class** inherits with the projection.

## Next steps

1. Seeded transfer tasks: see `harmonia/memory/transfer_tasks_seeded.json` (60 tasks).
2. As each task completes, update `transfer_matrix.json` with realized verdicts.
3. New P-IDs emerging from adapters get added to the catalog.
4. Co-mined with gen_05 (attention-replay): every new P-ID triggers replays on killed F-IDs.

## Version

- **v1.0** — 2026-04-20 — initial domain catalog + transfer matrix under generator pipeline v1.0.
