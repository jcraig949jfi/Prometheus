# Problem-Lens Catalogs

Per-open-problem catalogs of disciplinary attack surfaces, maintained
under the `PROBLEM_LENS_CATALOG@v1` symbol. Each catalog operationalizes
`SHADOWS_ON_WALL@v1` at the problem level: which lenses have been
applied, which are public-known, which are unapplied, and what tier
the applied-lens count supports.

## Catalogs

Teeth-test column reflects `FRAME_INCOMPATIBILITY_TEST` outcome (sessionD prediction resolution 2026-04-22/23, doc at `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md`). `cnd_frame_status` per `CND_FRAME@v1` schema (promoted 2026-04-23). Sub-flavor only populated for `cnd_frame` status.

| Problem | ID | Status | Lens count | Current tier | Teeth test | cnd_frame_status (sub_flavor) |
|---|---|---|---|---|---|---|
| [Lehmer's conjecture](lehmer.md) | `lehmer` | alpha | 28 lenses (5 APPLIED, 5 PUBLIC_KNOWN, 18 UNAPPLIED) | `map_of_disagreement` | **PASS** | substrate_divergent |
| [Collatz conjecture](collatz.md) | `collatz` | alpha | ~18 lenses (5 APPLIED, 4 PUBLIC_KNOWN, 9 UNAPPLIED) | `coordinate_invariant on truth + map_of_disagreement on provability` | **PASS** | substrate_divergent |
| [P vs NP](p_vs_np.md) | `p-vs-np` | sketch | ~12 lenses (0 APPLIED, 10 PUBLIC_KNOWN, 2 UNAPPLIED) | `coordinate_invariant` (community consensus P ≠ NP) via public-known lenses only | **FAIL** | consensus_catalog |
| [Ulam spiral](ulam_spiral.md) | `ulam-spiral` | alpha | 20 lenses (1 APPLIED + 1 partial, 6 PUBLIC_KNOWN, 12 UNAPPLIED) | `map_of_disagreement` (artifact vs. algebraic rigidity vs. coordinate illusion) | **FAIL** | cnd_frame (framing_of_phenomenon) |
| [Brauer-Siegel](brauer_siegel.md) | `brauer-siegel` | alpha | 26 lenses (0 APPLIED, 20 PUBLIC_KNOWN, 6 UNAPPLIED; 3 blended) | `map_of_disagreement` (all lenses agree on scaling exponent 1; disagree on obstruction — Siegel zeros vs. unit lattice vs. class-group structure vs. RMT universality) | **FAIL** | cnd_frame (obstruction_class) |
| [Smooth knot concordance — torsion](knot_concordance.md) | `knot_concordance` | alpha | 23 lenses (0 APPLIED, 18 PROPOSED, 3 NEW, 2 BLEND, 0 SKIP) | predicted `mixed` (map_of_disagreement on stance, convergent_triangulation on measurement) | **FAIL** | cnd_frame (truth_axis_substrate_inaccessible) |
| [Hilbert-Pólya conjecture](hilbert_polya.md) | `hilbert-polya` | alpha | 24 lenses (4 APPLIED, 12 PUBLIC_KNOWN, 8 UNAPPLIED; 3 blended) | `map_of_disagreement on "what is H" + coordinate_invariant on "something plays H's role"` | **FAIL** | cnd_frame (operator_identity) |
| [Zaremba's conjecture](zaremba.md) | `zaremba` | alpha | 26 lenses (17 PROPOSED, 1 PUBLIC_KNOWN, 5 NEW, 3 BLEND, 2 SKIP) | `coordinate_invariant` (3 readers 2026-04-22: sessionB resolver + sessionC cross-resolver + sessionA third-reader; PASS_BOUNDED_RESOLVED_REPLICATED provenance qualifier) | **PASS** (forward-path live-Y measurement: sessionB 1776901713091 + A-spectrum 1776902138226; Track D byte-replication: sessionC 1776902070483 + 1776902495482) | substrate_divergent (Lens 2 Kolmogorov q^0.68 vs Lens 3 random-walk linear on good-a count scaling; bounded q ∈ [10, 1000] resolved with α=0.6801 match to 2·δ(5)−1=0.680 at 3-decimal accuracy; asymptote q→∞ remains LIVE) |
| [Drum-shape (internal)](drum_shape.md) | `drum-shape` | alpha | 6 lenses (1 APPLIED, 3 PUBLIC_KNOWN, 2 UNAPPLIED) | `coordinate_invariant` (3 readers 2026-04-22: sessionA + sessionB + sessionC) | **FAIL** (forward-path: sessionA 1776909057747; cross-resolvers: sessionB 1776909156017 + sessionC 1776909211136) | consensus_catalog (external_theorem_proven — GWW 1992 closed the external question; 6 lenses inherit uniform alignment; 2nd anchor of CONSENSUS_CATALOG@v0) |
| [Irrationality paradox](irrationality_paradox.md) | `irrationality-paradox` | alpha | 6 lenses (0 APPLIED, 6 PUBLIC_KNOWN) | `coordinate_invariant` (3 readers 2026-04-22: sessionA resolver + sessionC cross-resolver + sessionB third-reader, after tier-downgrade-then-upgrade cycle) | **FAIL** (forward-path: sessionA 1776902815444; cross-resolved: sessionC 1776906106656 + sessionB 1776909320024) | cnd_frame (framing_of_phenomenon / partition_axis_disagreement sub_flavor candidate — lenses pick different Ys without active denial) |
| [Knot-NF lens mismatch](knot_nf_lens_mismatch.md) | `knot-nf-lens-mismatch` | alpha | 5 lenses (1 APPLIED-wrongly, 2 PUBLIC_KNOWN, 2 UNAPPLIED) | `coordinate_invariant` (3 readers 2026-04-22: sessionC resolver + sessionA cross-resolver + sessionB third-reader) | **FAIL** (forward-path: sessionC 1776907566863; cross-resolved: sessionA 1776907933474 + sessionB 1776909320024) | y_identity_dispute (lens_swap_remediable — Lens 2 A-polynomial Mahler actively denies Lens 1 Alexander Mahler via 26 Chinburg verifications; 1st anchor of v2 FAIL_via_Y_IDENTITY_DISPUTE enum; seeds `LENS_MISMATCH@v1` candidate) |

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
