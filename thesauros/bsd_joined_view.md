# bsd_joined — Materialized View Documentation

## Location
Database: `lmfdb` on M1 (localhost:5432)  
Type: Materialized view  
Created: 2026-04-16  
Script: `thesauros/create_bsd_joined.py`

## Purpose
Joins EC algebraic invariants (ec_curvedata) with L-function analytic data (lfunc_lfunctions) into a single queryable table. Unblocks BSD Phase 2, parity test, spectral analysis, and any EC↔L-function query.

## Join Key
```sql
lf.origin = 'EllipticCurve/Q/' || ec.conductor || '/' || split_part(ec.lmfdb_iso, '.', 2)
```
- Join is at the **isogeny class level**: all curves in class `11.a` share L-function `EllipticCurve/Q/11/a`
- This means multiple EC rows can join to the same lfunc row

## Coverage
- **2,481,157 rows** (of 3,824,372 total EC = 64.9%)
- Max conductor with L-function data: ~400,000
- Curves above 400K conductor have no lfunc match (0% coverage at 1M+)

| Conductor Range | Coverage |
|----------------|----------|
| <1K | 93% |
| 1K-100K | 83% |
| 100K-400K | 66% |
| 400K+ | 0% |

## Row Counts by Rank
| Rank | Curves | BSD Status | Sha Provenance |
|------|--------|-----------|----------------|
| 0 | 953,895 | Proven (Kolyvagin) | Independent |
| 1 | 1,244,889 | Proven (Gross-Zagier) | Independent |
| 2 | 275,644 | **UNPROVEN** | Circular (assumes BSD) |
| 3 | 6,728 | **UNPROVEN** | Circular |
| 4 | 1 | **UNPROVEN** | Circular |

**WARNING**: Sha at rank >= 2 is computed by LMFDB assuming BSD. Do NOT use it to test BSD. See Mnemosyne's circularity catch (2026-04-15 session).

## Columns

### EC Identity
| Column | Type | Source |
|--------|------|--------|
| `ec_label` | TEXT | ec_curvedata.lmfdb_label (e.g. '11.a1') |
| `ec_iso` | TEXT | ec_curvedata.lmfdb_iso (e.g. '11.a') |
| `conductor` | BIGINT | ec_curvedata.conductor |

### EC Algebraic Invariants (BSD Ingredients)
| Column | Type | Notes |
|--------|------|-------|
| `rank` | INT | Algebraic rank (Mordell-Weil, via descent) |
| `analytic_rank` | INT | Order of vanishing of L(E,s) at s=1 |
| `regulator` | DOUBLE | Regulator of Mordell-Weil group |
| `sha` | INT | Analytic order of Sha (**circular at rank >= 2**) |
| `sha_primes` | TEXT | Primes dividing Sha (e.g. '{2}') |
| `torsion` | INT | Order of torsion subgroup |
| `torsion_structure` | TEXT | Structure (e.g. '{2,4}') |
| `manin_constant` | INT | Manin constant (mostly 1) |
| `faltings_height` | DOUBLE | Faltings height |

### EC Structural Data
| Column | Type | Notes |
|--------|------|-------|
| `cm` | INT | CM discriminant (0 if no CM) |
| `class_size` | INT | Isogeny class size |
| `class_deg` | INT | Isogeny class degree |
| `semistable` | TEXT | Semistability flag |
| `bad_primes` | TEXT | List of primes of bad reduction |
| `num_bad_primes` | INT | Count of bad primes |
| `isogeny_degrees` | TEXT | Degrees of isogenies in class |
| `sign_disc` | TEXT | Sign of discriminant |

### L-function Analytic Data
| Column | Type | Notes |
|--------|------|-------|
| `lfunc_origin` | TEXT | L-function LMFDB path |
| `leading_term` | DOUBLE | L^(r)(E,1)/r! — the BSD left-hand side |
| `root_number` | TEXT | Root number (functional equation sign) |
| `sign_arg` | DOUBLE | Sign argument |
| `lfunc_analytic_rank` | INT | Analytic rank from L-function side |
| `analytic_conductor` | DOUBLE | Analytic conductor |
| `positive_zeros` | TEXT | Positive zeros of L(E,s) (text blob) |
| `z1` | DOUBLE | First zero |
| `z2` | DOUBLE | Second zero |
| `z3` | DOUBLE | Third zero |
| `symmetry_type` | TEXT | Symmetry type of L-function |

## Indexes
| Index | Column | Purpose |
|-------|--------|---------|
| `idx_bsd_conductor` | conductor | Conductor-binned queries |
| `idx_bsd_rank` | rank | Rank-stratified analysis |
| `idx_bsd_iso` | ec_iso | Isogeny class grouping |

## Example Queries

### BSD Parity Test (non-circular, runnable now)
```sql
-- Check: (-1)^rank should equal root_number for all curves
SELECT rank, root_number, count(*)
FROM bsd_joined
WHERE rank >= 2
GROUP BY rank, root_number
ORDER BY rank, root_number;
```

### BSD Phase 2 Calibration (rank 0-1, independent Sha)
```sql
-- For proven BSD: leading_term should ≈ Omega * Sha * Reg * Tam / Tor^2
-- (Omega and Tam not available — but ratios within isogeny classes are testable)
SELECT ec_iso, count(*), min(sha), max(sha), min(regulator), max(regulator)
FROM bsd_joined
WHERE rank <= 1
GROUP BY ec_iso
HAVING count(*) > 1
LIMIT 20;
```

### Spectral Analysis (zero spacing by rank)
```sql
SELECT rank, avg(z2 - z1) AS avg_first_gap, stddev(z2 - z1) AS std_first_gap, count(*)
FROM bsd_joined
WHERE z1 IS NOT NULL AND z2 IS NOT NULL
GROUP BY rank ORDER BY rank;
```

## Refresh
```sql
REFRESH MATERIALIZED VIEW bsd_joined;
```
Run after any update to ec_curvedata or lfunc_lfunctions.

## Missing Data (Not in View)
- **Omega (real period)**: not in ec_curvedata, needs computation from ainvs
- **Tamagawa product**: not in ec_curvedata, needs local Tate algorithm on bad primes
- **Rank 5 curves**: all 19 have conductor > 400K, no lfunc match
