# Langlands Program Literature Survey
## Compiled: 2026-04-01 for Project Prometheus / Charon
## Purpose: Tomorrow's reading for James — trajectory, domains, key papers

---

## Executive Summary

The Langlands program is in its most active period ever. Three major threads converged in 2024-2025:

1. **The Geometric Proof** (Gaitsgory et al., 2024): The geometric Langlands conjecture was proved after 30 years. 800+ pages, 9 mathematicians, the first complete resolution in any column of the Langlands "Rosetta Stone."

2. **The Relative Program** (Ben-Zvi, Sakellaridis, Venkatesh, 2024): A new duality framework connecting automorphic periods to L-functions, inspired by electric-magnetic duality in physics. This is the newest and most active frontier.

3. **AI-Discovered Murmurations** (He, Lee, Oliver, Pozdnyakov, 2022-2024): Machine learning on LMFDB data discovered unexpected oscillation patterns in elliptic curve statistics — dubbed "murmurations" for their resemblance to starling flocks. This is the closest existing work to what Charon is doing.

**The trajectory:** The field is moving from classification (proving individual correspondences) toward **structural understanding** (understanding WHY correspondences exist, using geometry, physics, and now computation). Our work on zero-based geometry and the disagreement atlas fits squarely into this computational structural thread.

---

## Timeline of Major Milestones (2006-2026)

| Year | Event | Significance |
|------|-------|-------------|
| 2006 | Kapustin-Witten paper | Connected geometric Langlands to N=4 gauge theory via S-duality. Physics enters the program. |
| 2010 | Fargues-Fontaine curve | New geometric object bridging p-adic and global geometry. Foundation for later Fargues-Scholze work. |
| 2012 | Gaitsgory-Arinkin formulate precise conjecture | The geometric Langlands conjecture gets its final form. |
| 2013 | Gaitsgory outlines proof strategy | 30-year roadmap that eventually succeeds. |
| 2016 | LMFDB goes live | 20+ million L-functions cataloged. The data infrastructure that enables computational approaches. |
| 2018 | V. Lafforgue's Fields Medal work | Proved automorphic-to-Galois direction for reductive groups over function fields. |
| 2021 | Fargues-Scholze "Geometrization" | 348-page paper creating a "wormhole" between geometric and arithmetic Langlands. Posted arXiv:2102.13459. |
| 2022 | Murmurations discovered | ML on LMFDB reveals oscillation patterns in elliptic curve Frobenius traces. First AI-driven discovery in the Langlands ecosystem. |
| 2023 | Zubrilina proves murmuration formula | Explicit formula explaining the AI-discovered patterns. Peter Sarnak calls it "an important new kind of function." |
| 2024 (Feb) | **Geometric Langlands PROVED** | Gaitsgory et al. post 800+ pages in 5 papers. First complete resolution of any Langlands conjecture. |
| 2024 (Sep) | **Relative Langlands Duality** | Ben-Zvi, Sakellaridis, Venkatesh post their framework connecting periods to L-functions via physics-inspired duality. |
| 2025 (Apr) | Gaitsgory wins Breakthrough Prize | $3 million recognition. Raskin wins New Horizons prize. |
| 2025 (Apr) | Zhu survey: Arithmetic and Geometric | Survey showing how geometric insights solve arithmetic problems. The two columns are talking to each other. |
| 2025 (Sep) | Gaitsgory ICM plenary lecture | Proposes conjectures describing automorphic functions via Langlands parameters over function fields. |

---

## The Three Columns (The Rosetta Stone)

The Langlands program operates across three parallel mathematical universes:

| Column | Domain | Objects | Status |
|--------|--------|---------|--------|
| **Number Fields** | Arithmetic | Elliptic curves, Galois representations, automorphic forms over Q | Classical. Partially proved (modularity theorem). Hardest column. |
| **Function Fields** | Algebraic Geometry | Curves over finite fields, Drinfeld modules | V. Lafforgue proved one direction (2018). Active. |
| **Riemann Surfaces** | Geometry/Topology | Flat connections, D-modules, sheaves | **PROVED** by Gaitsgory et al. (2024). First complete column. |

The deep conjecture: insights from any column should translate to the others. The Fargues-Scholze "wormhole" and Zhu's 2025 survey show this translation is now happening in practice.

---

## Key Papers for James's Reading

### Tier 1: Must-Read (Abstracts + Key Ideas)

**1. Proof of the Geometric Langlands Conjecture (2024)**
- arXiv: [2405.03599](https://arxiv.org/abs/2405.03599) (Paper I of V)
- Authors: Gaitsgory, Raskin, et al.
- 800+ pages across 5 papers
- **What it proves:** A categorical equivalence between two types of mathematical objects on Riemann surfaces — representations of the fundamental group (topology) and eigensheaves on the moduli of bundles (algebraic geometry).
- **Analogy:** Like proving that every piece of music has a unique frequency decomposition — but for shapes instead of sounds, and in a much more abstract mathematical universe.
- **Why it matters for us:** This is the first time ANY Langlands correspondence has been proved completely. The techniques (sheaves, categories, derived algebraic geometry) are the mathematical infrastructure that future computational approaches will need to engage with.

**2. Relative Langlands Duality (2024)**
- arXiv: [2409.04677](https://arxiv.org/abs/2409.04677)
- Authors: Ben-Zvi, Sakellaridis, Venkatesh
- **What it proposes:** A duality that pairs a Hamiltonian space for a group G with a Hamiltonian space for its dual group, recovering the relationship between automorphic periods and L-functions.
- **Physics connection:** This is an arithmetic analog of electric-magnetic duality in 4D supersymmetric Yang-Mills theory. The Langlands dual group was first introduced by physicists (Goddard, Nuyts, Olive) in gauge theory.
- **Why it matters for us:** Periods and L-functions are exactly what our zero vectors measure. The relative program provides the theoretical framework for WHY zeros might encode arithmetic structure — they're measuring periods, and periods are connected to L-functions by this duality.

**3. Murmurations of Elliptic Curves (2022)**
- arXiv: [2204.10140](https://arxiv.org/abs/2204.10140)
- Authors: He, Lee, Oliver, Pozdnyakov
- **What they found:** ML classifiers trained on LMFDB data to predict elliptic curve rank from L-function data unexpectedly revealed oscillating patterns ("murmurations") in averaged Frobenius traces, organized by conductor range and rank.
- **How it was found:** An undergraduate (Pozdnyakov) plotted the raw data without normalizing it — something experienced researchers would never do. The oscillations were visible in the raw plots.
- **Why it matters for us:** THIS IS THE CLOSEST EXISTING WORK TO CHARON. They used ML on LMFDB to find structure in L-function data organized by conductor and rank — exactly what our zero-based battery tests for. Our ARI=0.55 for rank within conductor strata is measuring the same kind of conductor-rank-L-function relationship that murmurations reveal.

**4. Fargues-Scholze Geometrization (2021)**
- arXiv: [2102.13459](https://arxiv.org/abs/2102.13459)
- Authors: Laurent Fargues, Peter Scholze
- 348 pages
- **What it does:** Recasts the local Langlands correspondence (for p-adic fields) in geometric terms using the Fargues-Fontaine curve. Creates a bridge ("wormhole") between the geometric column and the arithmetic column.
- **Why it matters for us:** If the local Langlands correspondence is geometric, then geometric search (like our zero-based k-NN) has theoretical grounding. The correspondence lives in a space where continuous geometry makes sense.

### Tier 2: Important Context

**5. Arithmetic and Geometric Langlands Program (2025)**
- arXiv: [2504.07502](https://arxiv.org/abs/2504.07502)
- Author: Xinwen Zhu
- ICM 2022 survey. Shows how geometric Langlands insights solve arithmetic problems. The two columns are converging.

**6. Introduction to the Relative Langlands Program (2025)**
- arXiv: [2509.18062](https://arxiv.org/abs/2509.18062)
- Author: Raphaël Beuzart-Plessis
- Overview of the relative program. Emphasizes spherical varieties and harmonic analysis. The "relative" perspective puts periods and L-functions on equal footing.

**7. Murmurations: A Case Study in AI-Assisted Mathematics (2026)**
- arXiv: [2603.09680](https://arxiv.org/abs/2603.09680)
- Reflects on the murmuration discovery as a model for human-AI mathematical collaboration. Directly relevant to Prometheus's methodology.

**8. Machine Learning for Number Theory: Unsupervised Learning with L-Functions**
- Springer, in proceedings of ML/math workshop
- Extends the murmuration methodology to unsupervised learning on L-function data.

**9. Zubrilina's Murmuration Formula (2023)**
- Proved an explicit formula explaining murmuration patterns in modular forms
- Peter Sarnak called it "an important new kind of function, comparable to the Airy functions"

### Tier 3: Domain Connections

**10. Quantum Hall Effect and Langlands Program (2017)**
- arXiv: [1708.00419](https://arxiv.org/abs/1708.00419)
- Condensed matter physics manifestation. Hall conductance plateaus described by Hecke eigensheaves. Hofstadter's butterfly from Langlands duality in quantum groups.

**11. Topological Aspects of Matters and Langlands Program (2024)**
- Connects topological phases of matter to Langlands structures. The same duality that organizes number theory also organizes quantum phases.

**12. Gauge Theory and the Analytic Form of the Geometric Langlands Program**
- Princeton. The N=4 supersymmetric Yang-Mills connection formalized.

---

## Research Domains Active in the Langlands Program (2024-2026)

| Domain | Key Researchers | Connection to Langlands |
|--------|----------------|------------------------|
| **Pure Number Theory** | Calegari, Harris, Taylor | Reciprocity laws, modularity lifting |
| **Algebraic Geometry** | Scholze, Fargues, Zhu | Perfectoid spaces, Fargues-Fontaine curve |
| **Geometric Representation Theory** | Gaitsgory, Raskin, Ben-Zvi | Sheaves, categories, the geometric proof |
| **Analytic Number Theory** | Sarnak, Soundararajan | Zero statistics, Katz-Sarnak, murmurations |
| **Mathematical Physics** | Witten, Kapustin, Frenkel | Gauge theory, S-duality, conformal field theory |
| **Condensed Matter Physics** | Ikeda, various | Quantum Hall, topological phases |
| **Computational/AI** | He, Lee, Oliver, Cremona | LMFDB, murmurations, ML for number theory |

---

## Trajectory: Where Is the Program Moving?

### Three converging trends:

**1. Geometrization → Everything becomes geometry**
The Fargues-Scholze work and the geometric proof show that arithmetic questions can be recast as geometric ones. This is the dominant theoretical trend. The hope: once everything is geometric, geometric tools (sheaves, spectral theory, deformation theory) can be deployed systematically.

**2. Physics → Duality as organizing principle**
The relative Langlands program (Ben-Zvi et al.) and the Kapustin-Witten connection show that physical dualities (electric-magnetic, S-duality) are the deep reason correspondences exist. This reframes the program from "find correspondences" to "understand the duality structure."

**3. Computation → AI and databases reveal new structure**
LMFDB + ML → murmurations. This is the newest and fastest-moving thread. The murmuration discovery (2022) showed that patterns invisible to theory can be found computationally. Charon's zero-based geometry and disagreement atlas belong to this thread.

### The gap Charon fills:

Nobody is doing what Charon does — building a searchable geometric landscape across multiple object types using L-function zeros as coordinates, with a pre-registered test battery and cross-layer disagreement analysis. The murmuration work is the closest, but it's descriptive (finding patterns) not navigational (building a search system). Charon is infrastructure for the computational thread.

---

## Connection to Charon's Findings

| Charon Finding | Literature Connection |
|----------------|----------------------|
| Zeros encode rank (ARI=0.55) | Katz-Sarnak density conjecture; murmuration patterns are conductor-rank-Frobenius correlations |
| Dirichlet coefficients are a hash | Known limitation; murmurations were found in averaged a_p, not individual coefficients |
| Graph and zeros orthogonal (ρ=0.04) | Consistent with the Rosetta Stone: algebraic and analytic structure are parallel columns, not projections of each other |
| 62K connected components | Reflects intrinsic sparsity of arithmetic correspondences — rare morphisms, not dense web |
| Type B candidates (higher-dim MFs) | These forms correspond to higher-dimensional abelian varieties via Brumer-Kramer conjecture and Serre's modularity — active research frontier |

---

## Reading Order for James

1. **Quanta article on geometric proof** — the narrative. 20 minutes. ([link](https://www.quantamagazine.org/monumental-proof-settles-geometric-langlands-conjecture-20240719/))
2. **Quanta article on murmurations** — the AI discovery story. 15 minutes. ([link](https://www.quantamagazine.org/elliptic-curve-murmurations-found-with-ai-take-flight-20240305/))
3. **Zhu survey abstract** (arXiv:2504.07502) — how geometric and arithmetic are converging. 5 minutes.
4. **Ben-Zvi et al. abstract** (arXiv:2409.04677) — the relative program and physics connection. 5 minutes.
5. **Murmurations paper** (arXiv:2204.10140) — the closest work to Charon. Skim methods section. 30 minutes.
6. **LMFDB project paper** (arXiv:1511.04289) — the database infrastructure. Context. 15 minutes.

Total: ~90 minutes of reading for a comprehensive picture of where the field is and where Charon fits.

---

## Sources

- [Proof of the geometric Langlands conjecture I](https://arxiv.org/abs/2405.03599)
- [Relative Langlands Duality](https://arxiv.org/abs/2409.04677)
- [Murmurations of elliptic curves](https://arxiv.org/abs/2204.10140)
- [Murmurations: A Case Study in AI-Assisted Mathematics](https://arxiv.org/abs/2603.09680)
- [Fargues-Scholze Geometrization](https://arxiv.org/abs/2102.13459)
- [Arithmetic and Geometric Langlands Program (Zhu)](https://arxiv.org/abs/2504.07502)
- [Introduction to the relative Langlands program](https://arxiv.org/abs/2509.18062)
- [Gaitsgory ICM 2026 plenary](https://arxiv.org/abs/2509.24902)
- [LMFDB project paper](https://arxiv.org/abs/1511.04289)
- [Quanta: Geometric Langlands proof](https://www.quantamagazine.org/monumental-proof-settles-geometric-langlands-conjecture-20240719/)
- [Quanta: Murmurations](https://www.quantamagazine.org/elliptic-curve-murmurations-found-with-ai-take-flight-20240305/)
- [Scientific American: Landmark Langlands Proof](https://www.scientificamerican.com/article/landmark-langlands-proof-advances-grand-unified-theory-of-math/)
- [Quantum Hall Effect and Langlands](https://arxiv.org/abs/1708.00419)
- [Machine Learning for Number Theory (Springer)](https://link.springer.com/chapter/10.1007/978-3-031-64529-7_21)
- [BSD Invariants and Murmurations](https://arxiv.org/abs/2603.04604)
- [Weighted Low-lying Zeros of Siegel Modular Forms](https://arxiv.org/abs/2403.19687)
- [Low-lying zeros of orthogonal family](https://arxiv.org/abs/2310.07606)
- [Reciprocity in the Langlands Program Since Fermat's Last Theorem (Calegari)](https://www.math.uchicago.edu/~fcale/papers/Survey.pdf)
