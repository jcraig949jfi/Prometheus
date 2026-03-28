# Noesis Data Sources — Comprehensive Density Plan

*The tensor's value is proportional to its density. 555 operations in 240D space is sparse. This document catalogs every viable data source for increasing density, organized by accessibility and expected yield.*

*Priority: Eos intelligence pipeline should add these to its crawl targets.*

---

## Current State

| Source | Count | Status |
|--------|-------|--------|
| Hand-crafted organisms | 81 ops | Loaded |
| Auto-wrapped libraries | 474 ops | Loaded |
| Mass embedder (library functions) | 2,236 of 2,970 | 75% done |
| OEIS sequences | 10K target (of 390K) | Downloading |
| **Total in tensor** | **~555 operations** | **Sparse** |

**Target:** 50,000+ embeddable objects for meaningful spatial clustering in 240D.

---

## Tier 1 — Download Now (bulk files, no API, free)

These are static datasets that can be downloaded as single files and processed locally.

| Dataset | URL / Source | Size | Yield | Format | Notes |
|---------|-------------|------|-------|--------|-------|
| **OEIS stripped** | oeis.org/stripped.gz | 30 MB | 390K sequences | `A-number, comma-separated values` | Already downloading. Each sequence = lookup function. Use `oeis_integer` type. |
| **OEIS names** | oeis.org/names.gz | 5 MB | 390K names | `A-number, description` | Metadata for OEIS sequences. Enables semantic search. |
| **Project Euler solutions** | projecteuler.net (community solutions on GitHub) | ~5 MB | 800+ problems | Python scripts | Each solution is a verified composition chain. Ground truth for scoring. Repos: `nayuki/Project-Euler-solutions`, `lucky-bai/projecteuler`. |
| **Rosetta Code tasks** | rosettacode.org/wiki/Category:Programming_Tasks | Scrape | ~1,000 tasks | Python implementations | Same algorithm, multiple implementations. Download Python versions only. Repo mirror: `acmeism/RosettaCodeData`. |
| **Mathlib4 declarations** | github.com/leanprover-community/mathlib4 | ~500 MB | 150K+ lemmas | Lean 4 source | Parse declaration names + dependency graph. Each lemma = typed operation with input/output theorems. NOT executing Lean — just extracting the dependency structure. |
| **DLMF (Digital Library of Mathematical Functions)** | dlmf.nist.gov | Scrape | ~1,000 identities | LaTeX + metadata | NIST's curated mathematical function reference. Each identity can be converted to a testable assertion. |
| **Wolfram MathWorld formulas** | mathworld.wolfram.com | Scrape | ~5,000 entries | HTML + formulas | Curated mathematical definitions. Extract the computable ones. |

### How to download

```bash
# OEIS (already have stripped.gz)
curl -o vault/data/oeis_names.gz "https://oeis.org/names.gz"

# Project Euler solutions
git clone https://github.com/nayuki/Project-Euler-solutions vault/data/euler_solutions

# Rosetta Code
git clone https://github.com/acmeism/RosettaCodeData vault/data/rosetta_code

# Mathlib4 (large — clone shallow)
git clone --depth 1 https://github.com/leanprover-community/mathlib4 vault/data/mathlib4
```

---

## Tier 2 — API Access (free tier, rate-limited)

These require API calls but have free tiers sufficient for our needs.

| Dataset | API | Free Tier | Yield | What We Get |
|---------|-----|-----------|-------|-------------|
| **Semantic Scholar** | api.semanticscholar.org | 100 req/5 min | Millions of papers | SPECTER v2 embeddings, citation graphs, abstracts. Already have key in `.env` (`S2_API_KEY`). |
| **OpenAlex** | api.openalex.org | Unlimited (polite) | 250M+ works | Concepts, topics, citation chains. No key needed. |
| **arXiv** | arxiv.org/api | No limit (polite) | 2M+ papers | Metadata, abstracts, categories. Free. |
| **Crossref** | api.crossref.org | Unlimited (polite) | 130M+ works | DOIs, references, subjects. No key needed. |
| **zbMATH** | api.zbmath.org | Free | 4M+ math papers | Math-specific classification (MSC codes), reviews. |

### Recommended API strategy

Don't crawl everything. Use targeted queries:
1. **Semantic Scholar**: Query for papers citing our 7 algorithmic reasoning fields. Download abstracts + SPECTER embeddings for the top 10K most-cited.
2. **OpenAlex**: Query for works tagged with concepts matching our 95 Lattice concepts. Download concept co-occurrence matrix.
3. **arXiv**: Download metadata for cs.AI, cs.LG, math.CO, math.NT, math.AT categories from last 5 years. ~200K papers.

---

## Tier 3 — Pip-Installable Libraries (scan and wrap)

The library scanner (`agents/eos/src/library_scanner.py`) currently scans 18 packages. There are more installable libraries with wrappable mathematical functions:

| Library | `pip install` | Category | Est. Functions | Notes |
|---------|--------------|----------|---------------|-------|
| **mpmath** | `mpmath` | Arbitrary precision math | ~300 | Special functions at arbitrary precision. Zeta, gamma, Bessel, etc. |
| **primesieve** | `primesieve` | Prime number generation | ~20 | Ultra-fast prime sieves. Complements sympy.ntheory. |
| **gmpy2** | `gmpy2` | Multi-precision arithmetic | ~100 | Fast GCD, modular arithmetic, primality testing. |
| **numba** | `numba` | JIT-compiled numerics | N/A | Not functions to wrap — use for speeding up organism execution. |
| **cvxpy** | `cvxpy` | Convex optimization | ~50 | Optimization problem solving. Different from scipy.optimize. |
| **pgmpy** | `pgmpy` | Probabilistic graphical models | ~100 | Bayesian networks, Markov chains. Bridges probability + graphs. |
| **hmmlearn** | `hmmlearn` | Hidden Markov models | ~30 | Sequence modeling. Temporal structure. |
| **pywt** | `PyWavelets` | Wavelet transforms | ~50 | Already installed. Verify it's in the scanner. |
| **deap** | `deap` | Evolutionary algorithms | ~50 | Already installed. GA operators as organisms. |
| **igraph** | `python-igraph` | Graph algorithms | ~200 | Faster than networkx for many operations. Different algorithm set. |
| **sage-math** | (heavy) | Everything | ~10,000 | Nuclear option. Contains almost all computable math. Very heavy install. |

### Quick wins (already installed, not in scanner)

Check if these are installed and add to `SCAN_TARGETS` in library_scanner.py:
- `PyWavelets` (pywt)
- `deap`
- `galois` (already in scanner)
- `powerlaw`
- `tensorly` (already in scanner)

---

## Tier 4 — Generated / Synthetic Data

These don't require downloading — they're generated from what we already have.

| Source | Method | Yield | Notes |
|--------|--------|-------|-------|
| **Composition outputs as new organisms** | Execute top chains, wrap outputs as callable functions | Hundreds | The system bootstraps itself. A chain that produces a useful array becomes an organism that other chains can use. |
| **Forge tool internals** | Extract sub-functions from the 344 forge tools | ~500 | Each forge tool has internal methods (`_parse_negations`, `_compute_bayesian_posterior`, etc.) that are individually wrappable. |
| **Random polynomial generators** | `np.polynomial.polynomial.Polynomial(random_coefficients)` | Unlimited | Parameterized functions. Different coefficients = different behavioral fingerprints. |
| **Parameterized ODE systems** | `scipy.integrate.solve_ivp` with random parameters | Unlimited | Each parameter set produces a different dynamical system. |
| **Cellular automata rules** | All 256 elementary CA rules as functions | 256 | Each rule is a function: state → next_state. Different rules cluster differently in embedding space. |

---

## Tier 5 — Specialized Databases (high value, more effort)

| Dataset | Source | Yield | What It Contains |
|---------|--------|-------|-----------------|
| **Lean Mathlib dependency graph** | Parse Lean 4 source | 150K nodes, ~500K edges | Which theorems depend on which. The structure IS the math. |
| **LMFDB (L-functions and Modular Forms)** | lmfdb.org/api | ~1M objects | Number theory database. Elliptic curves, modular forms, L-functions with computable properties. |
| **FindStat** | findstat.org | ~1,200 statistics | Combinatorial statistics on permutations, graphs, posets. Each is a computable function. |
| **House of Graphs** | houseofgraphs.org | ~1,000 special graphs | Named graphs with known properties. Each graph is an adjacency matrix = embeddable. |
| **Sloane's Gap data** | OEIS b-files | Varies | Extended sequence data (up to 10K terms per sequence vs 30 in stripped). Richer behavioral fingerprints. |
| **GAP (Groups, Algorithms, Programming)** | gap-system.org | ~1,000 group libraries | Finite groups with computable properties. Group theory as organisms. |

---

## Density Projections

| Milestone | Operations | OEIS | Papers | Other | Total | Status |
|-----------|-----------|------|--------|-------|-------|--------|
| **Current** | 555 | 0 | 0 | 0 | 555 | Sparse |
| **After Phase 1** | 555 | 10K | 0 | 0 | 10.5K | Light |
| **After Tier 1** | 555 | 390K | 0 | 2K (Euler+Rosetta) | 393K | **Dense** |
| **After Tier 2** | 555 | 390K | 10K | 2K | 403K | Dense+ |
| **After Tier 3** | 1,500 | 390K | 10K | 2K | 404K | Rich |
| **After Tier 4** | 2,500 | 390K | 10K | 3K | 406K | Rich+ |
| **Full vision** | 5,000 | 390K | 100K | 10K | 505K | **Saturated** |

The critical density threshold is ~10K objects — enough for k-NN to be statistically meaningful in 240D. OEIS alone gets us there. Everything else increases resolution.

---

## Eos Intelligence Pipeline — Priority Crawl Targets

Update `agents/eos/src/eos_daemon.py` to add these to the scan schedule:

### Immediate (add to next crawl cycle)
1. **Semantic Scholar**: Query for papers matching our 95 Lattice concepts. Top 1000 per concept. Download SPECTER embeddings.
2. **arXiv**: Download cs.AI + cs.LG + math.CO + math.NT metadata from 2024-2026. Abstracts + categories.
3. **OpenAlex**: Concept co-occurrence matrix for our 95 concepts. Which concepts appear together in papers?

### Weekly crawl additions
4. **zbMATH**: Math-specific paper discovery. MSC codes map to our concept taxonomy.
5. **GitHub code search**: `language:python topic:number-theory`, `topic:signal-processing`, etc. Find repos with mathematical function libraries we haven't discovered.

### Monthly deep dives
6. **LMFDB API**: Download elliptic curve data, L-function data for number theory organisms.
7. **FindStat**: All combinatorial statistics as wrappable functions.

---

## For the Noesis Engineer

The immediate priority for the current sprint is OEIS (already downloading) + finishing the mass embedder. Everything else in this document is for FUTURE sprints.

However: if the tournament shows that density is the bottleneck (strategies improve but plateau because the search space is too small), then Tier 1 downloads should be the next action. The engineer has autonomy to download Project Euler solutions or Rosetta Code if they determine density is limiting results.
