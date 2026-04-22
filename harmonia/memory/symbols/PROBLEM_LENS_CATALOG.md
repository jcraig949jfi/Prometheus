---
name: PROBLEM_LENS_CATALOG
type: pattern
version: 1
version_timestamp: 2026-04-21T00:45:00Z
immutable: true
previous_version: null
precision:
  canonical_definition: "Per-open-problem catalog of disciplinary attack surfaces (lenses). For each lens: discipline, status (APPLIED/PUBLIC_KNOWN/UNAPPLIED), result if applied, expected yield if unapplied. The catalog's purpose is to operationalize SHADOWS_ON_WALL at the problem level: every open problem gets a coverage map of lenses applied vs. unapplied, and the SHADOWS_ON_WALL tier is computed from the applied-and-agreeing count."
  catalog_status_values: [draft, alpha, complete]
  lens_status_values: [APPLIED, PUBLIC_KNOWN, UNAPPLIED, DEFERRED]
  required_sections:
    - frontmatter (catalog_name, problem_id, version, status, surface_statement)
    - what_the_problem_is_really_asking (multiple sub-questions)
    - data_provenance (historical trail)
    - motivations (by stakeholder community)
    - lens_catalog (each lens as a structured entry)
    - cross_lens_summary (counts, current SHADOWS_ON_WALL tier, priority unapplied)
    - connections (to other open problems or symbols)
  lens_entry_schema:
    discipline: str
    description: str (one-paragraph)
    status: APPLIED|PUBLIC_KNOWN|UNAPPLIED|DEFERRED
    prior_result: optional (stance + quantitative finding if applied)
    expected_yield: optional (what deploying this would reveal)
    tier_contribution: optional (per SHADOWS_ON_WALL lens-count toward tier)
    references: optional (commit refs, papers, symbols)
  location_convention: harmonia/memory/catalogs/<problem_id>.md
  index_file: harmonia/memory/catalogs/README.md
proposed_by: Harmonia_M2_sessionA@ccff50d12
promoted_commit: pending
references:
  - SHADOWS_ON_WALL@v1
  - MULTI_PERSPECTIVE_ATTACK@v1
  - PATTERN_30@v1
  - methodology_multi_perspective_attack@cde766053
  - methodology_toolkit@c882e2ac5
redis_key: symbols:PROBLEM_LENS_CATALOG:v1:def
implementation: null
---

## Definition

**Per-open-problem catalog of disciplinary attack surfaces.** For each
open problem Prometheus engages, maintain an exhaustive catalog of
disciplinary lenses that have been, could be, or have not yet been
pointed at the problem. For each lens, record discipline, current
status (APPLIED / PUBLIC_KNOWN / UNAPPLIED / DEFERRED), result-if-applied,
and expected-yield-if-unapplied. The catalog is the connective tissue
between the methodology shelf (generic tools), the multi-perspective
attack procedure (deployment pattern), and `SHADOWS_ON_WALL` (the
epistemic frame): it operationalizes "how many lenses, which tier" at
the problem level.

## Purpose

Three things this enables that are hard without it:

1. **Lens-count accounting.** `SHADOWS_ON_WALL@v1` asks "how many
   lenses have been applied?" The catalog answers that at a glance
   for any given open problem, with auditable references.
2. **Unapplied-lens priority queueing.** Every catalog entry not yet
   APPLIED is a candidate for the next attack wave. The highest-yield
   unapplied lenses form the priority queue for future Harmonia work.
3. **Cross-problem transfer.** When two catalogs share unapplied
   lenses, the same deployment infrastructure can be reused. This is
   how cross-disciplinary methodology compounds: a tool built for
   Lehmer applies to Bogomolov to ZP without re-invention.

## Schema

Each catalog lives at `harmonia/memory/catalogs/<problem_id>.md` with
frontmatter:

```yaml
---
catalog_name: <short title>
problem_id: <kebab-case ID>
version: <int ≥ 1>
version_timestamp: <ISO-8601>
status: draft | alpha | complete
surface_statement: <one-line problem statement>
---
```

Required sections:

1. **What the problem is really asking** — the questions beneath the
   surface statement. Different disciplines naturally hear different
   sub-questions; enumerate them so the catalog is not reductive.
2. **Data provenance** — where the problem came from historically,
   what data / artifacts constitute the empirical anchor.
3. **Motivations** — why different communities care. Enumerate by
   stakeholder type (pure, applied, pedagogical, career/prize,
   cross-disciplinary bridge).
4. **Lens catalog** — each lens as a structured entry (see below).
5. **Cross-lens summary** — total / applied / unapplied counts;
   current `SHADOWS_ON_WALL` tier; priority unapplied lenses.
6. **Connections** — to other open problems, promoted symbols,
   methodology artifacts.

### Lens entry schema

```
### Lens N — <name>

- **Discipline:** <field>
- **Description:** <one paragraph on what the lens looks at and how>
- **Status:** APPLIED | PUBLIC_KNOWN | UNAPPLIED | DEFERRED
- **Prior result** (if APPLIED/PUBLIC_KNOWN): <stance + finding>
- **Expected yield** (if UNAPPLIED): <what deploying reveals>
- **Tier contribution:** <counts toward SHADOWS_ON_WALL tier? yes/no/conditional>
- **References:** <commit hashes, paper citations, symbol refs>
```

## Anchor catalogs (v1 promotion basis)

Three catalogs built at promotion:

1. **Lehmer's conjecture** (`catalogs/lehmer.md`) — 28 lenses
   cataloged. Currently `map_of_disagreement` tier per
   `SHADOWS_ON_WALL`. Five lenses APPLIED via Prometheus (ergodic,
   info-theoretic, RG, adversarial, mass-gap physics); five
   PUBLIC_KNOWN (Dobrowolski, Smyth, Mossinghoff search, Deninger-
   Boyd L-value bridge, Lind-Schmidt-Ward entropy); eighteen
   UNAPPLIED.
2. **Collatz conjecture** (`catalogs/collatz.md`) — ~18 lenses
   cataloged. Currently `coordinate_invariant on truth +
   map_of_disagreement on provability`. Five APPLIED (ergodic,
   info-theoretic, random walk, graph-theoretic, computability);
   four PUBLIC_KNOWN (Terras density, Krasikov-Lagarias bounds,
   Tao 2019 almost-all bound, Conway undecidability); nine
   UNAPPLIED.
3. **P vs NP** (`catalogs/p_vs_np.md`) — sketch populating at alpha
   status. Tests the schema on a problem outside number theory /
   dynamics. ~12 lenses cataloged; mostly PUBLIC_KNOWN; demonstrates
   template generality.

## Operational integration

**With `SHADOWS_ON_WALL@v1`:** the catalog's applied-lens count
directly yields the tier. Promotion gates (the `operational_check`
in SHADOWS_ON_WALL) query the catalog, not the individual finding.

**With `MULTI_PERSPECTIVE_ATTACK@v1`:** each deployment of the
methodology updates the catalog — applied lenses get their stances
recorded; unapplied lenses may be re-prioritized based on which
direction the attack found the open questions to go.

**With `methodology_toolkit.md`:** generic lenses on the shelf
correspond to catalog entries across many problems. When a new lens
is added to the toolkit, every catalog gets an automatically-flagged
new UNAPPLIED entry.

**With `PATTERN_30@v1` and the sweep infrastructure:** catalog entries
that flag lineage hazards (algebraic, frame, computability) feed the
sweep's LINEAGE_REGISTRY.

## Derivation / show work

Origin: 2026-04-21 conductor conversation with James. The 28-lens
exhaustive catalog for Lehmer's conjecture was compiled during that
conversation; we observed that no substrate artifact held such
catalogs, and that building one would be the connective tissue
between our methodology tools, our epistemic frame, and any given
problem we engage. First three catalogs (Lehmer, Collatz, P vs NP)
built at symbol-promotion time as the anchor cases.

## Usage

**Query current tier for a problem:**
```
cat harmonia/memory/catalogs/lehmer.md | grep "current tier"
→ map_of_disagreement
```

**Priority queue for next attack:**
```
grep "^### Lens" catalogs/lehmer.md | grep UNAPPLIED
→ top-N sorted by expected-yield
```

**Cross-problem deployment:**
```
grep "Deninger-Boyd" catalogs/*.md
→ shows all problems where that lens is relevant
```

## Version history

- **v1** 2026-04-21T00:45:00Z — first canonicalization. Three anchor
  catalogs (Lehmer, Collatz, P vs NP). Schema pinned. Fourth
  type-`pattern` symbol after PATTERN_30, MULTI_PERSPECTIVE_ATTACK,
  SHADOWS_ON_WALL. Completes the four-layer epistemic-discipline
  stack: SHADOWS_ON_WALL (frame) → MULTI_PERSPECTIVE_ATTACK
  (deployment pattern) → PROBLEM_LENS_CATALOG (per-problem coverage
  map) → PATTERN_30 (specific failure-mode filter).
