# Problem-Lens Catalogs

Per-open-problem catalogs of disciplinary attack surfaces, maintained
under the `PROBLEM_LENS_CATALOG@v1` symbol. Each catalog operationalizes
`SHADOWS_ON_WALL@v1` at the problem level: which lenses have been
applied, which are public-known, which are unapplied, and what tier
the applied-lens count supports.

## Catalogs

| Problem | ID | Status | Lens count | Current tier |
|---|---|---|---|---|
| [Lehmer's conjecture](lehmer.md) | `lehmer` | alpha | 28 lenses (5 APPLIED, 5 PUBLIC_KNOWN, 18 UNAPPLIED) | `map_of_disagreement` |
| [Collatz conjecture](collatz.md) | `collatz` | alpha | ~18 lenses (5 APPLIED, 4 PUBLIC_KNOWN, 9 UNAPPLIED) | `coordinate_invariant on truth + map_of_disagreement on provability` |
| [P vs NP](p_vs_np.md) | `p-vs-np` | sketch | ~12 lenses (0 APPLIED, 10 PUBLIC_KNOWN, 2 UNAPPLIED) | `coordinate_invariant` (community consensus P ≠ NP) via public-known lenses only |

## Adding a new catalog

1. Copy the structure from `lehmer.md` (the most fully populated).
2. Fill in frontmatter (catalog_name, problem_id, version, status,
   surface_statement).
3. Populate the six required sections (see `PROBLEM_LENS_CATALOG.md`
   spec).
4. Update this index.
5. When a new Prometheus attack applies a lens, update the lens entry
   from UNAPPLIED → APPLIED with the result and commit reference.

## Integration

- `SHADOWS_ON_WALL@v1` resolves the lens-count tier by querying these.
- `MULTI_PERSPECTIVE_ATTACK@v1` runs produce updates to relevant
  catalog entries.
- `methodology_toolkit.md` is the shelf of generic lenses; catalog
  entries reference shelf items where applicable.
- `PATTERN_30@v1` sweep consults catalog hazard annotations.
