# External Dataset Scan — 2026-04-18
**Author:** Mnemosyne
**Purpose:** Identify datasets that would complement existing cross-domain data.

**Revision note (2026-04-18 afternoon):** The first draft of this document recommended several datasets we already have on disk but hadn't ingested. Kairos caught the mistake. This version is rewritten after a full walk of `cartography/*/data/`. The "what's on disk already" section is the important part — most of the interesting work here is cataloguing and ingestion, not external downloading.

---

## What's Actually on Disk (and not yet in Postgres)

Full walk of `cartography/*/data/` surfaced a lot I missed before. Grouped by priority.

### Topology / knots / 3-manifolds (much richer than I thought)

| Path | Size | Contents | Ingestion path |
|------|------|----------|---------------|
| `physics/data/snappy_manifolds.csv` | 20M | **223,673 3-manifolds** with volume, num_tetrahedra, homology, Chern–Simons | new table `topology.manifolds`; bridges to `nf_fields` via trace fields |
| `topology/data/pi-base/` | 28M | π-Base: topological spaces (properties + theorems) | new schema `topology.pi_base` (spaces, properties, theorems) |
| `knots/data/knot_polys.xlsx` | 8.5M | Knot polynomials (likely HOMFLY + Kauffman + Khovanov-adjacent) | augment `topology.knots` with new invariant columns |
| `knots/data/PD_3-16.txt.zip` | 29M | PD codes for all knots, 3 to 16 crossings | parseable to augment `topology.knots` with braid words |
| `knots/data/knotinfo_3d.csv.tar.gz` | 45M | **only 3D embedding coordinates** (not the full KnotInfo database) | new table `topology.knot_embeddings` (if we need 3D viz data) |
| `charon/data/mahler_measures.json` | 1.2M | 2,977 Mahler measures (computed) | `topology.mahler_measures` (already in loose_files) |

### Modular / Siegel / paramodular / Maass forms

| Path | Size | Contents | Status |
|------|------|----------|--------|
| `maass/data/maass_with_coefficients.json` | 335M | Maass forms with Fourier coefficients | unloaded — new table `analysis.maass_forms` |
| `maass/data/maass_with_fricke.json` | 335M | Maass forms with Fricke involution data | same |
| `genus2/data/siegel_fourier_coeffs.json` | 619M | Siegel modular form Fourier coefficients | unloaded — relates to `g2c_curves` |
| `genus2/data/genus2_curves_full.json` | 18M | Full genus-2 curve dataset | check vs LMFDB's 66K `g2c_curves` |
| `paramodular_level16/` | (several html + eigs files) | Paramodular forms level 16 | ad-hoc format; low priority |
| `paramodular_wt2/`, `paramodular_wt3/` | small | Paramodular forms weights 2 & 3 | same |
| `omf5_data/` | ~MBs | Orthogonal modular forms in 5 variables (OMF5) — Hecke eigenvalues | rare dataset, worth preserving |
| `convergence/data/hmf_forms_full.json` | 45M | Hilbert modular forms full | unloaded |
| `convergence/data/bianchi_forms.json` | 33M | Bianchi modular forms | unloaded |
| `convergence/data/hmf_hecke_eigenvalues.jsonl` | **69 GB** | Hilbert modular form Hecke eigenvalues | massive — ingestion cost needs triage |

### Algebra / groups / number fields

| Path | Size | Contents | Status |
|------|------|----------|--------|
| `atlas/data/small_groups.json` | 1.1M | JSON extract of GAP SmallGroups (~500 groups) | loose_files already flagged; append to `algebra.groups` |
| `atlas/data/smallgrp/` | 100M | Full GAP SmallGroups **package** (not parsed JSON) | GAP library, not directly ingestable — use for generating data on demand |
| `atlas/data/gap-system/` | 127M | Full GAP computer algebra system | tool, not data |
| `local_fields/data/` | (files) | Local number fields | unloaded |
| `number_fields/data/number_fields.json` | 1.8M | ~9K number fields (local copy) | append/intersect with `nf_fields` (22M) |

**Terminology correction:** `cartography/atlas/` is the **GAP SmallGroups** library, not the **ATLAS of Finite Group Representations** (Wilson/QMUL Monster-family sporadics). Different databases. The distinction matters for bond candidates — SmallGroups catalogues every group up to order ~2000; the ATLAS has deep representation-theoretic data on specific simple groups.

### Formal mathematics

| Path | Size | Contents | Status |
|------|------|----------|--------|
| `mathlib/data/mathlib4` | 138M | Full Lean Mathlib4 snapshot | unloaded — schema needs designing |
| `metamath/data/set.mm` | 49M | Metamath set.mm proof database | unloaded — proof DAG |

### Physics (beyond what's in `physics.*`)

| Path | Size | Contents | Status |
|------|------|----------|--------|
| `physics/data/basis_sets/` | 292M | Quantum chemistry basis sets | specialized, defer |
| `physics/data/nist_asd/` | 16M | NIST Atomic Spectra Database | unloaded — new table |
| `physics/data/superconductors/` | 107M | More superconductor data beyond the 16K in `physics.superconductors` | check for delta |
| `physics/data/exoplanets/` | 700K | Confirmed exoplanets (6,158) | loose_files — ingest |
| `physics/data/gravitational_waves/` | 13K | GWTC parameters (219) | loose_files — ingest |
| `physics/data/pulsars/` | 5.3M | ATNF pulsars (4,351) | loose_files — ingest |
| `physics/data/pubchem_50k.csv` | ? | PubChem 50K compounds | loose_files — ingest |
| `physics/data/cod_crystals_bulk.json` | ? | COD crystal structures | loose_files — ingest |
| `isogenies/data/graphs/` | 380M | Isogeny graph data | specialized |
| `isogenies/data/isogeny-database-v1-30000.zip` | 283M | Isogeny database | specialized |

### Convergence signatures (research outputs, not raw data)

Per `loose_files.md`, everything under `convergence/data/*_signatures.jsonl` is **derived research output**, not source data. But two exceptions that are effectively source-quality:

| Path | Size | Notes |
|------|------|-------|
| `convergence/data/hmf_hecke_eigenvalues.jsonl` | 69 GB | Canonical computed HMF Hecke eigenvalues — source-quality |
| `convergence/data/bianchi_forms.json` | 33M | Source-quality Bianchi forms |
| `convergence/data/arithmetic_dynamics_signatures.jsonl` | 11M | **NOT an arithmetic-dynamics database** — it's Lyapunov/orbit-type signatures computed from OEIS sequences treating them as dynamical systems |

### Open problems

| Path | Contents |
|------|----------|
| `cartography/open_problems/` | Problem registry + enrichment script — worth integrating with `prometheus_fire.agora.open_questions` |

---

## Real External Gaps (confirmed not on disk)

After the walk, these are genuine gaps:

### 1. Graph databases
`cartography/graph/data/` is **empty**. Exists as a scaffolded directory with `graph_exploration.py` and a 2026-04-05 log but zero data files.

**Candidates:**
- [House of Graphs](https://houseofgraphs.org/meta-directory) — curated "interesting" graphs, downloadable in graph6
- Brouwer strongly regular graph database (implemented in [SageMath](https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/strongly_regular_db.html))

**Why it matters:** connects to `algebra.groups` (automorphism groups, Cayley graphs) and to codes→lattices→modular forms chain.

### 2. ATLAS of Finite Group Representations (Wilson / QMUL)
Confirmed absent — our `atlas/` is GAP SmallGroups, not the ATLAS. [brauer.maths.qmul.ac.uk/Atlas/v3](https://brauer.maths.qmul.ac.uk/Atlas/v3/) has 5,215 representations of 716 groups including character tables and subgroup structure for sporadic simples.

**Why it matters:** bridge from `algebra.groups` to `artin_reps` (798K Artin reps in LMFDB). Character tables + Artin rep L-functions is a direct cross-domain test.

### 3. CodeTables.de
No coding-theory data on disk. [codetables.de](https://codetables.de/) (Grassl) has best-known linear codes over GF(2,3,4,5,7,8,9).

**Why it matters:** Construction A maps codes → lattices. We have 39,293 lattices; extremal self-dual codes connect to modular forms (1.14M of those). Direct cross-domain bond candidate.

### 4. Full KnotInfo database
We only have 3D coordinates, not the main invariant table. [knotinfo.math.indiana.edu](https://knotinfo.math.indiana.edu/) has signature, genus, slice genus, Khovanov ranks, HOMFLY-PT — the signature backfill (P-011) was asking for exactly this.

### 5. Arithmetic dynamics (rational map data)
Confirmed: our `arithmetic_dynamics_signatures.jsonl` is OEIS-sequence orbit-type signatures, not actual rational-map preperiodic-point data. No canonical database exists yet; literature-driven if we want it.

### 6. Classical physics tables
- **AFLOW** — we have the superconductor subset; full AFLOW covers millions of inorganic materials
- **Materials Project** (full, ~150K) — we have the 10K subset
- **Gaia stellar catalog** — no astronomical catalogs at all

### 7. Congruent number database / extended BSD data
Directly adjacent to our EC work; scattered in papers, no single database.

---

## Revised Sequencing

Given the size of the "already on disk but unloaded" queue, that's the first thing to clear — not external scouting.

### Priority 0 (no download, pure ingestion)

**Sub-queue A — quick wins (< 1 hour each):**
- `physics/data/exoplanets/` → `physics.exoplanets` (6,158)
- `physics/data/gravitational_waves/` → `physics.gw_events` (219)
- `physics/data/pulsars/` → `physics.pulsars` (4,351)
- `charon/data/mahler_measures.json` → `topology.mahler_measures` (2,977)
- `cartography/findstat/` → `analysis.findstat` (~500)
- `atlas/data/small_groups.json` append → `algebra.groups` (~500)

**Sub-queue B — larger, higher impact:**
- `physics/data/snappy_manifolds.csv` → `topology.manifolds` (**223,673 rows**) — this alone is a new domain
- `topology/data/pi-base/` → new schema `topology.pi_base`
- `knots/data/knot_polys.xlsx` + `PD_3-16.txt.zip` → augment `topology.knots`
- `maass/data/maass_with_coefficients.json` → `analysis.maass_forms`
- `cartography/open_problems/` → integrate with `agora.open_questions`

**Sub-queue C — needs schema design:**
- `genus2/data/siegel_fourier_coeffs.json` (619M) — coefficient schema
- `convergence/data/hmf_forms_full.json` + `bianchi_forms.json` — HMF/Bianchi schemas
- `mathlib/data/mathlib4/` — proof-graph schema (declarations + deps)
- `metamath/data/set.mm` — same
- `convergence/data/hmf_hecke_eigenvalues.jsonl` (69 GB) — needs triage, probably Postgres partitioning + Redis summary

### Priority 1 (external — only after P0 clear)

- **Full KnotInfo** (signature/genus/Khovanov) — fixes P-011 directly
- **Graph databases** (House of Graphs + Brouwer SRG)
- **ATLAS of Finite Group Representations** — groups ↔ Artin reps bridge
- **CodeTables.de** — codes → lattices → modular forms chain

### Priority 2 (deferred)

Everything else. No concrete research driver yet.

---

## Lesson

The embarrassment was real: more than half of my original recommendations were for data already on disk. Process fix: before any future "we should get X" recommendation, grep `cartography/*/data/` for the keyword and size-check any hits. `loose_files.md` is a useful start but has gaps of its own; the directory walk is authoritative.
