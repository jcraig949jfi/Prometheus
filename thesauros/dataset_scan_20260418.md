# External Dataset Scan — 2026-04-18
**Author:** Mnemosyne
**Purpose:** Identify datasets we don't yet have that would complement existing cross-domain data and open new cross-domain bond candidates.

---

## Current Coverage (live row counts, 2026-04-18)

| Domain | Strength | Weakness |
|--------|----------|----------|
| Number theory / L-functions | **Strong** — 24M lfuncs, 3.8M EC, 1.1M modular forms, 22M number fields, 2.48M bsd_joined | `object_zeros` rebuild pending (P-009) |
| Algebra — finite groups | **Strong** — 544K groups, 39K lattices, 230 space_groups | No character tables, no Lie theory, no representations |
| Topology | **Weak** — 12,965 knots, 980 polytopes; no 3-manifolds, no graphs, no simplicial complexes | Knot signatures empty (P-011); Mahler measures computed but unloaded |
| Chemistry | **Thin** — 134K QM9 molecules | No dynamics, no reactions, no inorganics beyond AFLOW subset |
| Physics | **Thin** — 10K materials, 16K superconductors, 226 particles, 355 constants | No exoplanets/GW/pulsars (on disk, unloaded); no astronomical catalogs |
| Biology | **Very thin** — 108 BiGG metabolism models | No proteins, no expression, no phylogeny |
| Combinatorics | **Empty** — FindStat on disk, unloaded | Entire domain missing |
| Dynamical systems | **Empty** | Arithmetic dynamics directly adjacent to our EC/lfunc work |
| Logic / formal math | **Empty** — 187 MB mathlib + metamath on disk, unloaded | Proof graphs unexplored |

---

## Tier 0 — Already On Disk, Just Needs Ingestion

Should be finished before scouting outward. All listed in `thesauros/loose_files.md` with verified file paths.

| Dataset | Target | Rows | Effort |
|--------|-------|------|--------|
| NASA Exoplanet Archive | `physics.exoplanets` | 6,158 | 1 hour |
| Gravitational wave events (GWTC) | `physics.gw_events` | 219 | 30 min |
| ATNF Pulsar Catalogue | `physics.pulsars` | 4,351 | 1 hour |
| Mahler measures (precomputed) | `topology.mahler_measures` | 2,977 | 30 min |
| FindStat | `analysis.findstat` | ~500 | 1 hour |
| OEIS crossrefs / formulas | `analysis.oeis_crossrefs`, `analysis.oeis_formulas` | ~375K each | 2 hours |
| Small groups (atlas) append | `algebra.groups` | ~500 | 30 min |

**Recommendation:** clear this queue before pulling any new external source. Cheap, de-risks later work, and every one of these opens a join that isn't currently possible.

---

## Tier 1 — Direct Augmentation of Strong Domains

Highest leverage because they plug into tables that already see heavy cross-domain traffic.

### 1.1 Knot invariants beyond what we have
**Gap:** `topology.knots` has Alexander, Jones, Conway, determinant (partial), and now crossing_number (fixed 2026-04-16). Missing: signature (P-011 open), genus, slice genus, braid index, HOMFLY-PT polynomial, **Khovanov homology**.

**Sources:**
- **KnotInfo** — [knotinfo.math.indiana.edu](https://knotinfo.math.indiana.edu/) — canonical table for all prime knots up to 13 crossings. Contains Khovanov homology ranks and torsions computed via KnotJob (Schütz). Downloadable CSV.
- **Knot Atlas** — [katlas.org/wiki/Khovanov_Homology](https://katlas.org/wiki/Khovanov_Homology) — community wiki with Khovanov polynomials for small knots.
- **khoca** — [github.com/LLewark/khoca](https://github.com/LLewark/khoca) — C++/Python tool for computing Khovanov–Rozansky homology if we ever need to go beyond 13 crossings.

**Why it matters for us:** Khovanov homology categorifies the Jones polynomial. We already have Jones coefficients, so this is structurally adjacent — and Khovanov ranks give new numerical invariants that could participate in cross-domain bonds (already seen plausible knot↔L-function links in noesis.cross_domain_edges).

### 1.2 SnapPy 3-manifold census with hyperbolic volumes
**Gap:** we have knots but no 3-manifolds. Knot complements in S³ are 3-manifolds; hyperbolic volume of a knot complement is a classical invariant.

**Source:** [snappy.computop.org/censuses.html](https://snappy.computop.org/censuses.html)
- `OrientableCuspedCensus` — all cusped hyperbolic 3-manifolds triangulated with ≤9 ideal tetrahedra; recently extended to 10 tets (adds ~150,000 manifolds)
- `OrientableClosedCensus` — 11,031 closed hyperbolic 3-manifolds (Hodgson-Weeks)
- Platonic manifold census

**Why it matters for us:** Hyperbolic volume and trace fields bridge topology ↔ number theory directly. Trace fields are number fields (already in `nf_fields` — 22M rows); hyperbolic volumes relate to special values of L-functions. This is a potential Tier-3 ensemble invariance candidate.

### 1.3 ATLAS of Finite Group Representations + character tables
**Gap:** we have 544,831 abstract groups but no representations or character tables. Representation theory links groups to their L-functions (Artin reps, already partially in LMFDB with 800K rows).

**Source:** [brauer.maths.qmul.ac.uk/Atlas/v3](https://brauer.maths.qmul.ac.uk/Atlas/v3/) — 5,215 representations of 716 groups. GAP's `AtlasRep` package and `CtblLib` character table library cover the full ATLAS character tables.

**Why it matters for us:** `artin_reps` (~800K) is the bridge. ATLAS character tables + Artin reps would let us test conjectures like Dedekind's Zeta quotient decomposition, or connect finite-group classification to L-function L-values.

---

## Tier 2 — New Domains with Clear Cross-Domain Links

### 2.1 Graph databases — House of Graphs + Brouwer strongly regular
**Gap:** no graph table at all. Cayley graphs of our 544K groups have been computed nowhere; interesting families (strongly regular, distance-regular, cages) are directly adjacent to combinatorial designs and codes.

**Sources:**
- **House of Graphs** — [houseofgraphs.org](https://houseofgraphs.org/meta-directory) — curated database of "interesting" graphs and counterexamples. Downloadable in graph6 / multicode format.
- **Brouwer's strongly regular graphs** — existence results up to 1300 vertices, full SageMath implementation ([doc.sagemath.org/.../strongly_regular_db.html](https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/strongly_regular_db.html))

**Candidate table:**
```sql
CREATE SCHEMA graphs;
CREATE TABLE graphs.strongly_regular (
    g_id SERIAL PRIMARY KEY, v INT, k INT, lambda INT, mu INT,
    is_primitive BOOLEAN, family TEXT, source TEXT,
    graph6 TEXT, automorphism_order BIGINT
);
```

**Why it matters for us:** SRGs are specified by 4 parameters (v, k, λ, μ); known families include Paley graphs (which tie to quadratic characters of number fields), Johnson/Kneser graphs (combinatorics), and incidence graphs of designs (codes).

### 2.2 CodeTables — Best-known linear codes
**Gap:** no coding-theory table. Linear codes over GF(q) are the algebraic-combinatorial bridge to lattices (Construction A: codes → lattices).

**Source:** [codetables.de](https://codetables.de/) — Markus Grassl's regularly-updated tables of best-known linear codes over GF(2,3,4,5,7,8,9).

**Why it matters for us:** we already have 39,293 lattices. Linear codes yield lattices via Construction A; comparing code minimum distance with lattice minimum norm is a direct cross-domain test. Extremal self-dual codes connect to modular forms (we have 1.14M of those).

### 2.3 Arithmetic dynamics data
**Gap:** dynamical systems entirely absent. Yet arithmetic dynamics is the closest sibling to our EC/lfunc work — canonical heights, preperiodic points, boundedness conjectures, all structurally parallel to Mordell-Weil.

**Sources:**
- Recent computational work on [extreme examples in arithmetic dynamics](https://arxiv.org/html/2601.11482) — datasets of polynomials up to degree 13, rational functions up to degree 5, with preperiodic-point counts.
- No canonical "database" yet exists; this is more literature-driven than catalog-driven.

**Candidate table:**
```sql
CREATE TABLE analysis.arith_dynamical_systems (
    id BIGSERIAL PRIMARY KEY,
    map_type TEXT, degree INT, coefficients NUMERIC[],
    n_preperiodic INT, n_periodic INT, min_cycle_length INT,
    canonical_height_leading_coeff NUMERIC, source TEXT
);
```

**Why it matters for us:** Uniform Boundedness Conjecture (Morton-Silverman) for dynamics is the analog of Mazur's torsion theorem for EC. We have 3.8M EC with torsion data; cross-referencing with bounded preperiodic point counts would be a literal analog across domains.

---

## Tier 3 — Larger Efforts, Domain-Creating

### 3.1 AlphaFold / PDB protein structures
**Gap:** biology is one table with 108 rows. AlphaFold DB has ~200M predicted structures; the PDB has ~200K experimental ones.

**Cost:** very large ingestion, storage concerns. Not recommended unless a specific bio-adjacent research direction opens.

### 3.2 Materials Project (full) + AFLOW full
**Gap:** `physics.materials` is capped at 10,000 rows; full MP has ~150K materials. AFLOW canonical database is millions.

**Cost:** moderate (~GB of JSON per 100K entries). Worthwhile if we pivot to materials bonds; currently materials don't participate in strong bonds per our noesis.cross_domain_edges.

### 3.3 Lean Mathlib + Metamath
**Gap:** 187 MB of formal math on disk, unloaded. No schema yet exists. Mathlib alone has ~200K declarations.

**Schema to design if we want this:**
```sql
CREATE SCHEMA formal;
-- declarations, dependencies (DAG), tactic use, import graph
```

**Why it matters:** gives us a proof dependency graph that's structurally a DAG on mathematical concepts — a native cross-domain bridge, already labeled by the authors.

---

## Explicit Non-Recommendations

| Skip | Reason |
|------|--------|
| CIFAR / MNIST / generic ML benchmarks | Not structural data; no math invariants |
| Full Materials Project / AFLOW bulk | Only justified if a materials bond emerges in Tier-3 bonds |
| PDB/AlphaFold | Too large for current infra; unclear cross-domain payoff |
| Generic social-network graphs (Facebook, Twitter) | No mathematical invariants of interest |
| Full NCBI GenBank | Out of scope |

---

## Recommended Sequencing

1. **Clear Tier 0** (Exoplanets, GW, Pulsars, Mahler measures, FindStat, OEIS aux). ~1 day of work. Everything already on disk.
2. **KnotInfo Khovanov + extended knot invariants** (Tier 1.1) — direct patch to a table with known gaps (signature P-011 already open).
3. **SnapPy 3-manifold census** (Tier 1.2) — opens topology ↔ number theory via trace fields.
4. **ATLAS character tables** (Tier 1.3) — bridges groups ↔ Artin reps.
5. **Graphs + SRG + codes** (Tier 2.1 + 2.2) — combinatorial bridge; codes→lattices→modular forms chain.
6. **Arithmetic dynamics** (Tier 2.3) — literature-driven for now; wait for a research direction.
7. **Mathlib / PDB / full MP** (Tier 3) — deferred unless a specific bond demands them.

Total new data volume for Tier 0 + Tier 1: <5 GB. Storage is not a constraint.

---

## Open Questions for Agora

- Does anyone currently need any of these? (Harmonia's battery, Aporia's triage, Kairos's kill-tests — do any want new substrate?)
- Ranking: is topology ↔ number theory (SnapPy) more interesting than algebra ↔ rep theory (ATLAS)?
- For codes → lattices: do we have any researcher who cares? If no, defer.
