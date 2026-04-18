# Missing Data Registry

**Purpose:** Datasets confirmed absent from M2 (`D:\Prometheus\cartography\*\data\`) after a full directory walk on 2026-04-18. First stop before downloading: **check M1** — the machines haven't been audited against each other, and anything listed here may already exist there.

**Scope:** only datasets with a concrete cross-domain use in Project Prometheus. Not a general "things I'd like" list.

**How to use:**
- Each row has a suggested M1 search path and filename pattern to probe first.
- If found on M1: copy to matching path on M2 and add an entry in `thesauros/loose_files.md`.
- If not found on M1: the row lists the upstream source for fresh download.

---

## Confirmed Gaps (verified absent from M2, 2026-04-18)

### G-01 — Full KnotInfo invariant table
**What we want:** signature, 4-genus (smooth/topological), 3-genus, slice genus, braid index, HOMFLY-PT polynomial, **Khovanov homology ranks and torsions**, concordance invariants. Per-knot rows.

**What we have:** only `cartography/knots/data/knotinfo_3d.csv.tar.gz` (45M) — **just 3D embedding coordinates**, not the invariant table.

**Directly blocks:** Proposal P-011 (knot signature backfill) — signatures are 0 / 12,965 in `topology.knots`.

**M1 search:**
- `cartography/knots/data/knotinfo_invariants*.csv`
- `cartography/knots/data/knotinfo_full*`
- anywhere containing filenames like `knotinfo*.csv` with size >50 MB
- anywhere with `khovanov*.csv` or `*.json`

**Source if not on M1:** [knotinfo.math.indiana.edu](https://knotinfo.math.indiana.edu/) — bulk CSV downloads available from the site's download page. ~100 MB expected.

**Priority:** HIGH — directly unblocks an open proposal.

---

### G-02 — Graph databases
**What we want:** House of Graphs (curated interesting graphs) and Brouwer's strongly regular graphs.

**What we have:** `cartography/graph/data/` directory exists but is **empty**. Script `graph_exploration.py` and log from 2026-04-05 exist but no underlying data.

**M1 search:**
- `cartography/graph/data/`
- anywhere with `*.graph6`, `*.g6`, `*.sparse6`, `*.mc` (multicode)
- files matching `houseofgraphs*`, `brouwer*`, `strongly_regular*`, `srg_*`

**Source if not on M1:**
- [houseofgraphs.org](https://houseofgraphs.org/meta-directory) — graph6 / multicode downloads
- [Brouwer SRG via Sage](https://doc.sagemath.org/html/en/reference/graphs/sage/graphs/strongly_regular_db.html) — generate via Sage `graphs.strongly_regular_graph(v,k,lambda,mu)`

**Bond candidates:** connects to `algebra.groups` (automorphism groups, Cayley graphs) and to the codes→lattices chain.

**Priority:** MEDIUM — new domain, currently zero rows.

---

### G-03 — ATLAS of Finite Group Representations (Wilson / QMUL)
**What we want:** the ATLAS of Sporadic Simple Groups and their representations — character tables, maximal subgroups, explicit representations. Distinct from GAP SmallGroups.

**What we have:** `cartography/atlas/data/smallgrp/` (100M) is the **GAP SmallGroups package** (groups-by-order up to ~2000), not the ATLAS of Finite Group Representations. Directory name is misleading.

**M1 search:**
- anywhere with `AtlasRep*`, `atlas_reps*`
- GAP package named `atlasrep` (not `smallgrp`)
- character table files (.ctbl format from GAP CTblLib)
- files matching `ctbl*`, `character_tables*`

**Source if not on M1:** [brauer.maths.qmul.ac.uk/Atlas/v3](https://brauer.maths.qmul.ac.uk/Atlas/v3/) — the AtlasRep GAP package is a 2.3 MB gzipped tar, plus optional 22 MB starter archive of small representations. Full database accessed on-demand via GAP.

**Bond candidates:** bridges `algebra.groups` ↔ `artin_reps` (798K Artin reps in LMFDB).

**Priority:** MEDIUM.

---

### G-04 — CodeTables.de linear codes
**What we want:** Grassl's database of best-known linear codes over GF(q) for q = 2, 3, 4, 5, 7, 8, 9. Parameters: (n, k, d) = (length, dimension, minimum distance).

**What we have:** nothing. No coding-theory data anywhere in `cartography/`.

**M1 search:**
- `cartography/codes/`, `cartography/coding_theory/`
- files matching `codetables*`, `bklc*`, `best_known*`, `linear_codes*`
- Magma BKLC database file formats

**Source if not on M1:** [codetables.de](https://codetables.de/) — HTML-scrapable tables + Magma-readable format.

**Bond candidates:** Construction A maps codes → lattices; we have 39,293 lattices in `algebra.lattices`. Extremal self-dual codes connect to modular forms (1.14M in `mf_newforms`).

**Priority:** MEDIUM.

---

### G-05 — Arithmetic dynamics (rational maps / preperiodic points)
**What we want:** Silverman/Morton-style arithmetic dynamics data — rational maps f: ℙ¹ → ℙ¹ over ℚ with their preperiodic point counts, canonical heights, periods.

**What we have:** `convergence/data/arithmetic_dynamics_signatures.jsonl` (11M) exists but is **NOT** this data — it's Lyapunov exponents and orbit-type signatures computed from **OEIS sequences** treated as dynamical systems. Structurally unrelated.

**M1 search:**
- `cartography/arithmetic_dynamics/`, `cartography/dynamics/`
- files matching `rational_maps*`, `preperiodic*`, `canonical_heights*`, `morton_silverman*`
- Silverman's ArithmeticDynamics LaTeX tables

**Source if not on M1:** No single canonical database exists. Closest available:
- [arXiv:2601.11482](https://arxiv.org/html/2601.11482) — genetic-algorithm-generated extreme examples, degree 2–13 polynomials and degree 2–5 rational functions
- Silverman's book tables
- SageMath's `dynamical_systems` module can generate

**Bond candidates:** Uniform Boundedness Conjecture (Morton-Silverman) for dynamics is the direct analog of Mazur's torsion theorem for EC. We have 3.8M EC with torsion structure; this would be a literal cross-domain analog.

**Priority:** LOW — literature-driven, no canonical source.

---

### G-06 — Full Materials Project
**What we want:** The full MP (~150K materials), not just our 10K subset.

**What we have:** `cartography/physics/data/materials_project_10k.json` loaded as 10,000 rows in `physics.materials`.

**M1 search:**
- `cartography/physics/data/materials_project*.json` with size > 100 MB
- `cartography/physics/data/mp_full*`
- any Materials Project API bulk dump

**Source if not on M1:** [materialsproject.org](https://materialsproject.org/) — bulk download via their REST API with an API key.

**Priority:** LOW — materials currently don't participate in strong cross-domain bonds (per `noesis.cross_domain_edges`); no research driver.

---

### G-07 — Gaia stellar catalog / astronomical catalogs
**What we want:** Any curated astronomical source catalog — Gaia DR3 stars, SDSS galaxies, Fermi gamma-ray sources, Planck CMB source catalog.

**What we have:** `physics/data/exoplanets/`, `gravitational_waves/`, `pulsars/` (all unloaded, in loose_files queue). No general stellar / galactic catalogs.

**M1 search:**
- `cartography/astronomy/`, `cartography/physics/data/gaia*`, `sdss*`, `fermi*`, `planck*`

**Source if not on M1:**
- [gea.esac.esa.int](https://gea.esac.esa.int/archive/) — Gaia archive
- [sdss.org](https://www.sdss.org/) — SDSS/DR bulk data

**Priority:** LOW — no stellar-data use case identified in current research.

---

### G-08 — Congruent numbers / extended BSD data
**What we want:** Tunnell's congruent number database + extended rank tables, Cremona curve database auxiliary invariants not in LMFDB.

**What we have:** LMFDB `ec_curvedata` has rank, sha (circular at rank ≥ 2), regulator. No dedicated congruent-number table.

**M1 search:**
- `cartography/number_theory/`, `cartography/congruent_numbers/`
- files matching `tunnell*`, `congruent*`, `cremona_extended*`

**Source if not on M1:** no single canonical source; data scattered across literature. Tunnell's original tables in his 1983 paper; more recent computations by Poonen, Watkins.

**Priority:** LOW — directly adjacent to our BSD work but no immediate researcher need.

---

### G-09 — Full KnotInfo: concordance / signature tables separately
**Sub-item of G-01**, but worth calling out: the signature-specific table at [knotinfo.math.indiana.edu/descriptions/signature.html](https://knotinfo.math.indiana.edu/descriptions/signature.html) is the minimal download that would unblock P-011. Covers all prime knots up to 13 crossings. ~1 MB.

**M1 search:**
- `cartography/knots/data/signature*.csv`
- `cartography/knots/data/knotinfo_signature*.csv`

**Priority:** HIGH (cheaper version of G-01 — if the full KnotInfo is hard to find, just the signature table suffices).

---

## Not Recommended

Listed so nobody re-suggests these:

| Dataset | Reason to skip |
|---------|---------------|
| AlphaFold / PDB full | Scale (200M structures); no biology research driver yet |
| Full AFLOW bulk (millions of materials) | Superset of what we have; no active materials bond |
| Lean Mathlib full history | We have a snapshot (138M); history not needed |
| Generic ML datasets (CIFAR, MNIST, ImageNet) | No mathematical structure of interest |
| Social network graphs (Facebook, Twitter, Reddit) | No math invariants; out of project scope |
| Generic bioinformatics (GenBank, RefSeq bulk) | No project driver |

---

## Format for Adding New Gaps

When documenting a new gap, include:

1. **ID** — next sequential `G-NN`
2. **What we want** — specific data, not vague category
3. **What we have** — explicit "we checked this path, it contains X, not Y"
4. **Directly blocks** — what proposal / finding is stuck without it
5. **M1 search path** — concrete file patterns someone can grep for
6. **Upstream source** — URL + expected size
7. **Bond candidates** — which existing tables would this join with?
8. **Priority** — HIGH / MEDIUM / LOW with justification

The rule: a gap is only worth filing if it has a bond candidate. Data for its own sake is Tier-3 deferral.
