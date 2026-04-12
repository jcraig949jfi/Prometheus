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

### M1: Chemistry + Biology (molecular structure → properties)

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

---

### M2: Finance + Economics (time series → regime detection)

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

## Why These Two Specifically

| Property | Chemistry/Bio (M1) | Finance/Econ (M2) |
|----------|-------------------|-------------------|
| **Data type** | Molecular graphs, sequences | Time series, cross-sections |
| **Noise level** | Low (DFT) to moderate (bioassay) | Very high (markets) |
| **Non-stationarity** | Expected (across chemical families) | Guaranteed (market regimes) |
| **Known laws** | Periodic table, Lipinski's Rule of 5, VSEPR | Fama-French, CAPM, power-law tails |
| **Cross-domain bridge** | Molecule→biology (drug activity) | Markets→economy (macro-finance) |
| **Battery stress** | New data types (graphs, sequences) | Extreme noise, regime changes |
| **BREAK_SYMMETRY test** | Functional group × scaffold → property | Sector × regime → return |

Chemistry tests whether our findings generalize to another physical science. Finance tests whether they generalize to a fundamentally different kind of data.

---

## Quick Start Plan

### M1 Chemistry Sprint (first 2 days)

1. Download QM9 dataset (~134K molecules with 19 properties)
2. Parse SMILES → molecular descriptors (MW, n_atoms, n_rings, functional groups)
3. Run the battery: functional_group → HOMO-LUMO gap (our SC_class→Tc analog)
4. Test for BREAK_SYMMETRY: does the mapping change across MW bins?
5. Calibrate: Lipinski's Rule of 5 should be a known-truth rediscovery

### M2 Finance Sprint (first 2 days)

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
- Apply the full 7-layer cross-domain falsification protocol

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
