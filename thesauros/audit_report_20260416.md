# Data Audit Report — 2026-04-16

Comprehensive audit of prometheus_sci and prometheus_fire tables.
Flags suspicious patterns: uniform array lengths (P-009 pattern), constant columns, mostly-null, mostly-zero, mostly-empty-string.

Generated: 2026-04-16T23:52:23.774924

---

## Summary
- Databases audited: 1
- Total tables: 14
- Total columns: 110
- Flagged columns: 23

## prometheus_sci

### algebra.groups (544,831 rows — **3 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `is_abelian` | boolean | 100% | MOSTLY_NULL (100%) |
| `is_solvable` | boolean | 100% | MOSTLY_NULL (100%) |
| `source_id` | integer | 0% | CONSTANT (always 4) |

### algebra.lattices (39,293 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### algebra.space_groups (230 rows)

### analysis.fungrim (3,130 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### analysis.oeis (394,454 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### biology.metabolism (108 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### chemistry.qm9 (133,885 rows — **2 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `n_atoms` | smallint | 100% | MOSTLY_NULL (100%) |
| `source_id` | integer | 0% | CONSTANT (always 2) |

### core.data_source (6 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `checksum` | text | 100% | MOSTLY_NULL (100%) |

### physics.codata (355 rows — **3 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `value` | double precision | 99% | MOSTLY_NULL (99%) |
| `uncertainty` | double precision | 99% | MOSTLY_NULL (99%) |
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### physics.materials (10,000 rows — **1 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `source_id` | integer | 0% | CONSTANT (always 5) |

### physics.pdg_particles (226 rows — **3 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `charge` | double precision | 100% | MOSTLY_NULL (100%) |
| `spin` | double precision | 100% | MOSTLY_NULL (100%) |
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### physics.superconductors (2,012 rows — **2 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `tc` | double precision | 0% | CONSTANT (always 0.0) |
| `source_id` | integer | 100% | MOSTLY_NULL (100%) |

### topology.knots (12,965 rows — **2 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `signature` | smallint | 100% | MOSTLY_NULL (100%) |
| `source_id` | integer | 0% | CONSTANT (always 1) |

### topology.polytopes (980 rows — **2 flagged columns**)

| Column | Type | NULL% | Flags |
|--------|------|-------|-------|
| `is_simplicial` | boolean | 100% | MOSTLY_NULL (100%) |
| `source_id` | integer | 0% | CONSTANT (always 6) |

