# Domain Expansion Proposal
## Where to take the battery next
### 2026-04-12

---

## Selection Criteria

The battery was built on mathematical/physics data. To validate it as a general instrument, new domains should:

1. **Have different data types** — not just categorical→continuous (which we've saturated)
2. **Have known ground truths** — so we can calibrate like we did with Deuring/modularity
3. **Have the BREAK_SYMMETRY / COMPOSE primitives available** — so we can test whether the non-stationarity pattern generalizes
4. **Have public, structured databases** — immediately accessible

---

## Recommended Domains (split M1/M2)

### M2: Chemistry + Biology + Source Code (SpectreX5)

**Why:** Chemistry has the closest analogy to our SC_class→Tc finding. Molecular structure (functional groups, topology) predicts properties (solubility, toxicity, activity) — but the mapping changes across chemical families. This is BREAK_SYMMETRY in a new domain. If we find the same non-stationarity pattern, it's universal. If we don't, it's physics-specific.

**Datasets:**

| Dataset | Size | What it has | Ground truths |
|---------|------|-------------|---------------|
| **QM9** | 134K molecules | SMILES, properties (HOMO, LUMO, gap, dipole, etc.) | DFT-computed, highly accurate |
| **ChEMBL** | 2M+ bioactivities | Molecules, targets, IC50/EC50 | Measured biological activity |
| **PubChem** | 100M+ compounds | Structures, properties, bioassays | Massive but noisy |
| **UniProt** | 250M+ proteins | Sequences, structures, functions, GO terms | Curated annotations |
| **PDB** | 200K+ structures | 3D coordinates, resolution, ligands | Experimental |
| **KEGG** | 20K pathways | Metabolic networks, reactions, enzymes | Curated biochemistry |

**Key tests:**
- Functional group → solubility: does it BREAK_SYMMETRY across molecular weight bins?
- Protein family → function: SYMMETRIZE or BREAK_SYMMETRY?
- Drug scaffold → activity: same non-stationarity as SG→Tc?
- Amino acid composition → structure class: categorical→categorical (new for our battery)

**Start with:** QM9 (small, clean, DFT ground truths). Then ChEMBL for cross-domain (molecule→biology bridge).

#### Source Code (algorithmic structure → mathematical proximity)

**Why:** This is where COMPOSE should live. Algorithms that share subroutines (modular arithmetic, polynomial multiplication, FFT) bridge mathematical domains even when the theory doesn't. If cross-domain structure exists anywhere detectable, it's in implementation dependency graphs.

**Datasets:**

| Dataset | Size | What it has | Ground truths |
|---------|------|-------------|---------------|
| **FLINT** | ~9K files | C library for number theory (fast arithmetic) | Call graph = algorithmic dependency |
| **SageMath** | ~500K lines | Python/Cython math system, wraps FLINT/PARI/GAP | Import graph, module taxonomy |
| **SciPy** | ~300K lines | Scientific computing (linalg, optimize, stats) | Function call graph |
| **SymPy** | ~500K lines | Symbolic math (algebra, calculus, NT, combinatorics) | Module dependency graph |
| **mathlib** | 8.5K modules | Lean 4 formal math library | Import graph (already in our data) |

**Key tests:**
- Do algorithms for number theory and algorithms for topology share subroutines? (COMPOSE test)
- Call graph communities vs mathematical domain classification: do they align?
- Subroutine reuse across domains: which low-level operations bridge the most domains?
- mathlib import distance vs concept distance: is implementation proximity a proxy for mathematical proximity?

**Start with:** mathlib (already have 8.5K modules). Then SciPy (clean, well-structured, public).

---

### M1: Finance + Economics (Skullport, time series → regime detection)

**Why:** Finance is the ultimate adversarial domain for our battery. Markets are noisy, non-stationary BY DESIGN, and full of distributional artifacts (fat tails, volatility clustering). If the battery can separate real structure from noise here, it works anywhere. Also: finance has well-known "laws" (power-law tails, volatility clustering, mean reversion) that serve as calibration targets, plus massive public data.

**Datasets:**

| Dataset | Size | What it has | Ground truths |
|---------|------|-------------|---------------|
| **Yahoo Finance** | 50+ years daily | OHLCV for 10K+ stocks | Price is truth |
| **FRED** | 800K+ series | Macro indicators (GDP, CPI, unemployment, rates) | Official statistics |
| **Fama-French** | 50+ years | Factor returns, portfolios sorted by size/value/momentum | Academic benchmark |
| **SEC EDGAR** | 20+ years | 10-K filings, financial statements | Regulatory filings |
| **World Bank** | 60+ years | Development indicators for 200+ countries | National statistics |
| **CRSP** | 100+ years | US stock returns, delisting data | Academic standard |

**Key tests:**
- Sector → returns: SYMMETRIZE or BREAK_SYMMETRY across market regimes?
- Country → GDP growth: does the mapping change across decades? (temporal non-stationarity)
- Factor exposure → returns: do Fama-French factors transfer across countries? (F25b test)
- Volatility → tail behavior: is the fat-tail pattern universal or conditional?
- Balance sheet ratios → default: categorical (rating) → continuous (spread). Same as SC_class→Tc?

**Start with:** Fama-French factors (clean, public, 50+ years, known ground truths). Then FRED macroeconomic series for cross-domain (markets ↔ economy).

---

## Why These Three Specifically

| Property | Chemistry/Bio (M2) | Source Code (M2) | Finance/Econ (M1) |
|----------|-------------------|-----------------|-------------------|
| **Data type** | Molecular graphs, sequences | Dependency graphs, call trees | Time series, cross-sections |
| **Noise level** | Low (DFT) to moderate (bioassay) | Zero (deterministic) | Very high (markets) |
| **Non-stationarity** | Expected (across chemical families) | Unknown (new question) | Guaranteed (market regimes) |
| **Known laws** | Periodic table, Lipinski's Rule of 5 | Shared subroutines (FFT, GCD) | Fama-French, CAPM, power-law tails |
| **Cross-domain bridge** | Molecule→biology (drug activity) | Algorithm→algorithm (COMPOSE) | Markets→economy (macro-finance) |
| **Battery stress** | New data types (graphs, sequences) | Graph topology, zero noise | Extreme noise, regime changes |
| **Key primitive** | BREAK_SYMMETRY | COMPOSE | BREAK_SYMMETRY |

Chemistry tests physical science generalization. Source code is where COMPOSE should live (the missing primitive). Finance tests extreme-noise generalization.

---

## Quick Start Plan

### M2 Chemistry + Source Code Sprint (first 2 days)

**Day 1 — Chemistry:**
1. Download QM9 dataset (~134K molecules with 19 properties)
2. Parse SMILES → molecular descriptors (MW, n_atoms, n_rings, functional groups)
3. Run the battery: functional_group → HOMO-LUMO gap (our SC_class→Tc analog)
4. Test for BREAK_SYMMETRY: does the mapping change across MW bins?
5. Calibrate: Lipinski's Rule of 5 should be a known-truth rediscovery

**Day 2 — Source Code:**
1. Parse SciPy call graph (already public, well-structured)
2. Build module→function dependency matrix
3. Cluster by call graph proximity vs mathematical domain label
4. Test: do linalg and optimize share more subroutines than linalg and stats?
5. Cross-reference with mathlib import graph (already have 8.5K modules)
6. Look for COMPOSE: shared algorithmic primitives across mathematical domains

### M1 Finance Sprint (first 2 days)

1. Download Fama-French 5-factor daily returns (1963-present)
2. Download sector ETF returns (1999-present) or build from CRSP
3. Run the battery: sector → returns (the SC_class→Tc analog)
4. Test for BREAK_SYMMETRY: does the mapping change across market regimes (bull/bear)?
5. Calibrate: the size effect and value premium should be rediscoveries
6. Test F25b: do factor loadings transfer across decades?

### Both machines (day 3+)

Cross-domain bridge tests:
- Chemistry→Biology: do molecular descriptors predict biological activity? (the drug discovery question)
- Finance→Economy: do market factors predict GDP? (the macro-finance question)
- Source Code→Mathematics: does algorithmic proximity predict mathematical proximity?
- Apply the full 7-layer cross-domain falsification protocol to ALL new findings

---

## What We're Looking For

The meta-question across all domains:

> **Is BREAK_SYMMETRY (non-stationarity of categorical→continuous mappings) universal across scientific databases, or specific to mathematical/physical data?**

If chemistry and finance show the same pattern: **universal property of structured data.**
If they don't: **domain-specific to mathematical objects.**

Either answer is a publishable result.

---

## Data Availability

All proposed datasets are freely available:
- QM9: https://figshare.com/collections/Quantum_chemistry_structures_and_properties_of_134_kilo_molecules/978904
- ChEMBL: https://www.ebi.ac.uk/chembl/
- Fama-French: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- FRED: https://fred.stlouisfed.org/
- UniProt: https://www.uniprot.org/
- World Bank: https://data.worldbank.org/

No API keys needed for initial datasets. QM9 and Fama-French are single-file downloads.
