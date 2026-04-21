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
| [Ulam spiral](ulam_spiral.md) | `ulam-spiral` | alpha | 20 lenses (1 APPLIED + 1 partial, 6 PUBLIC_KNOWN, 12 UNAPPLIED) | `map_of_disagreement` (artifact vs. algebraic rigidity vs. coordinate illusion) |
| [Brauer-Siegel](brauer_siegel.md) | `brauer-siegel` | alpha | 26 lenses (0 APPLIED, 20 PUBLIC_KNOWN, 6 UNAPPLIED; 3 blended) | `map_of_disagreement` (all lenses agree on scaling exponent 1; disagree on obstruction — Siegel zeros vs. unit lattice vs. class-group structure vs. RMT universality) |
| [Smooth knot concordance — torsion](knot_concordance.md) | `knot_concordance` | alpha | 23 lenses (0 APPLIED, 18 PROPOSED, 3 NEW, 2 BLEND, 0 SKIP) | predicted `mixed` (map_of_disagreement on stance, convergent_triangulation on measurement) |
| [Hilbert-Pólya conjecture](hilbert_polya.md) | `hilbert-polya` | alpha | 24 lenses (4 APPLIED, 12 PUBLIC_KNOWN, 8 UNAPPLIED; 3 blended) | `map_of_disagreement on "what is H" + coordinate_invariant on "something plays H's role"` |
| [Zaremba's conjecture](zaremba.md) | `zaremba` | alpha | 26 lenses (17 PROPOSED, 1 PUBLIC_KNOWN, 5 NEW, 3 BLEND, 2 SKIP) | predicted `divergent_map` / mixed (lenses triangulate δ(A) but diverge on the controlling framing) |
| [Drum-shape (internal)](drum_shape.md) | `drum-shape` | alpha | 6 lenses (1 APPLIED, 3 PUBLIC_KNOWN, 2 UNAPPLIED) | external `coordinate_invariant` (spectrum insufficient — Gordon-Webb-Wolpert + Perlis); internal `surviving_candidate` awaiting separator-scan |
| [Irrationality paradox](irrationality_paradox.md) | `irrationality-paradox` | alpha | 6 lenses (0 APPLIED, 6 PUBLIC_KNOWN) | `map_of_disagreement` — archetypal case; six lenses, six incompatible verdicts about transcendental "structure" |
| [Knot-NF lens mismatch](knot_nf_lens_mismatch.md) | `knot-nf-lens-mismatch` | alpha | 5 lenses (1 APPLIED-wrongly, 2 PUBLIC_KNOWN, 2 UNAPPLIED) | external `coordinate_invariant` (bridge is real via A-poly); internal `shadow` (we used the wrong polynomial). Seeds `LENS_MISMATCH@v1` candidate. |

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
