# Master Challenge Inventory — All Proposals Across All Sessions
## Compiled: 2026-04-09
## Total unique challenges: 115 proposed, 85 after deduplication

---

# How to read this document

Each entry:
- **ID**: ALL-NNN (sequential)
- **Source**: who proposed it
- **Batch**: Part 1 / Part 2 / Part 3 / Round 3 / Queue
- **Status**: DONE / READY / BLOCKED / DEFERRED
- **Duplicate of**: cross-reference if collapsed
- **Landscape value**: HIGH / MEDIUM / LOW
- **Difficulty**: 1-5
- **Priority**: landscape_value x feasibility (H/M/L)

---

# DONE — Completed Challenges (with results)

---

### ALL-001 | Mod-p Residue Starvation Scan
- **Source**: Claude (Part 1 #1)
- **Batch**: Part 1
- **Merged with**: Queue C02
- **Description**: Scan every modular form at weight >= 12 for residue class starvation at each prime p <= 23
- **Result**: 17,314 weight-2 forms scanned. 7,557 (43.6%) show starvation. Full hierarchy: mod-2 (36%), mod-3 (7.9%), mod-5 (0.8%), mod-7 (8 forms). 637.2.a.c/d anomaly found (later resolved: rational 7-isogeny). 156 non-CM forms starved at ell>=5
- **Data**: `v2/residue_starvation_results.json`

### ALL-002 | Moonshine Network Expansion
- **Source**: Claude (Part 1 #2), DeepSeek (Part 1 #2), Grok (Part 1 #2)
- **Batch**: Part 1 (3 sources merged)
- **Merged with**: Queue C09
- **Description**: Scan OEIS for sequences matching mock theta / McKay-Thompson series coefficients
- **Result**: 4 M24 umbral moonshine <-> EC Hecke eigenvalue matches at levels 2420, 3190, 4170, 4305. 307 total moonshine bridges (from 3,315 raw). Window length 6 = moderate significance
- **Data**: `v2/moonshine_oeis_results.json`, `v2/moonshine_expansion_results.json`

### ALL-003 | Berlekamp-Massey on GSp_4 Difference Sequences
- **Source**: Claude (Part 1 #3)
- **Batch**: Part 1
- **Merged with**: Queue C03
- **Description**: Test if d_p = (a_p(C1) - a_p(C2))/3 satisfies linear recurrence for 37 congruence pairs
- **Result**: CLEAN NULL. Zero recurrences found across all 37 pairs, over Q and 5 finite fields, orders up to 8. Pairs are arithmetically independent
- **Data**: `v2/gsp4_bm_results.json`

### ALL-004 | Mod-p Fingerprint Algebraic Families vs Fungrim (Scaling Law)
- **Source**: Claude (Part 1 #4)
- **Batch**: Part 1
- **Merged with**: Queue C11
- **Description**: Evaluate mod-p fingerprints on OEIS algebraic families against Fungrim formulas
- **Result**: STRONGEST FINDING. Enrichment scales monotonically: 4.1x (mod-2) to 53.6x (mod-11). After detrending: flat 8-16x, prime-independent. Survived 8/8 battery tests. The scaling law is the instrument's first genuine positive result
- **Data**: `v2/algebraic_dna_fungrim_results.json`, `v2/scaling_law_battery_results.json`

### ALL-005 | Collatz Algebraic Sibling Hunt
- **Source**: Claude (Part 1 #5)
- **Batch**: Part 1
- **Merged with**: Queue C17
- **Description**: Search OEIS for sequences sharing x^4 - 2x^2 characteristic polynomial with Collatz
- **Result**: KILL #14. Family expanded to 105 sequences sharing (x^2-1)^2. All piecewise-linear on even/odd indices. Connection to 3x+1 dynamics: zero
- **Data**: `v2/collatz_family_results.json`

### ALL-006 | Hecke Algebra Geometry (Congruence Graphs)
- **Source**: ChatGPT (Part 1 #1)
- **Batch**: Part 1
- **Merged with**: Queue C07
- **Description**: Build adjacency graphs for each level N and prime ell from congruence data
- **Result**: Near-perfect matching at every prime. ell=7,11: pure matching, zero triangles. ell=5: 27 triangles (p<0.005). Hecke deformation space is overwhelmingly one-dimensional
- **Data**: `v2/hecke_graph_results.json`, `v2/congruence_graph.json`

### ALL-007 | Spectral Operator Matching Across Domains
- **Source**: ChatGPT (Part 1 #2)
- **Batch**: Part 1
- **Merged with**: Queue C05
- **Description**: Compare spectral spacing statistics (Wasserstein, NNS, entropy) across Maass, EC, knots, lattices
- **Result**: CALIBRATION. Maass forms universally Poisson (0/120 pairs show GUE). Berry-Tabor 1977 confirmed. Cross-domain: lattice determinants and NF discriminants are not eigenvalue-type spectra
- **Data**: `v2/spectral_spacing_results.json`

### ALL-008 | Recurrence Operator Duality (OEIS <-> Arithmetic)
- **Source**: ChatGPT (Part 1 #3), DeepSeek (Part 1 #3), Grok (Part 1 #5)
- **Batch**: Part 1 (3 sources merged)
- **Merged with**: Queue C08
- **Description**: Match OEIS recurrence characteristic polynomials against EC/genus-2 Euler factors
- **Result**: MOSTLY NEGATIVE. EC Euler factors: 0.25x (depleted). Genus-2: 11.3x enrichment but 15/18 palindromic at p=2. OEIS recurrences and Euler factors occupy largely disjoint algebraic territory
- **Data**: `v2/recurrence_euler_factor_results.json`

### ALL-009 | Constraint Collapse (Generalizing Hasse Squeeze)
- **Source**: ChatGPT (Part 1 #4)
- **Batch**: Part 1
- **Merged with**: Queue C10
- **Description**: Test if constraint accumulation -> phase transition is universal across math domains
- **Result**: TWO REGIMES. Combinatorial constraints: super-exponential. Geometric constraints: power law (alpha=0.63). Deuring mass formula confirmed as bonus
- **Data**: `v2/constraint_collapse_results.json`

### ALL-010 | Operadic Skeleton Dynamics
- **Source**: ChatGPT (Part 1 #5), Gemini (Part 1 #5), Grok (Part 1 #3)
- **Batch**: Part 1 (3 sources merged)
- **Merged with**: Queue C12
- **Description**: Build formula rewrite system, track skeleton invariants, measure flow between domains
- **Result**: Within/between module distance ratio = 0.813. 4 universal verbs: Equal (98.3%), For (93.3%), And (90.0%), Set (81.7%). Jacobi theta = most central; primes = most peripheral. Gamma bridges 24/60 modules
- **Data**: `v2/operadic_dynamics_results.json`

### ALL-011 | Paramodular Conjecture Probe
- **Source**: Gemini (Part 1 #1), DeepSeek (Part 1 #5)
- **Batch**: Part 1 (2 sources), updated Part 2 (Grok #1)
- **Merged with**: Queue C01
- **Description**: Bridge L-function coefficients of genus-2 curves to Siegel paramodular form eigenvalues
- **Result (Part 1)**: BLOCKED — level gap (LMFDB Siegel forms at N=1-2, curves start N=169). **(Part 2 Grok #1)**: UNBLOCKED. Perfect level bijection at 7 prime levels <= 600. Root number 7/7. Hecke eigenvalue verification 37/40 (92.5%)
- **Data**: `v2/paramodular_probe_v2_results.json`

### ALL-012 | C11 Scaling Law in Reverse (Universal Test)
- **Source**: Claude (Part 2 #1)
- **Batch**: Part 2
- **Description**: Test scaling law on genus-2 curves (Fungrim -> LMFDB direction). Is it OEIS-specific or universal?
- **Result**: UNIVERSAL. Scaling law appears everywhere algebraic structure exists. N(G_{3,3}): slope +0.578. QM: +0.567. USp(4) generic: flat (null holds). Conductor bins: flat (null holds)
- **Data**: `v2/scaling_law_reverse_results.json`

### ALL-013 | Mod-2 GSp_4 Congruence Graph
- **Source**: Claude (Part 2 #2)
- **Batch**: Part 2
- **Description**: Build mod-2 congruence graph on 733 pairs. Test for triangles/higher structure
- **Result**: MASSIVE TRIANGLES. 11,356 edges, 20,917 triangles (8,000x vs null). Max clique K_24 at conductor 352256. Clustering coefficient ~1.0. At mod-3: snaps back to perfect matching
- **Data**: `v2/gsp4_mod2_graph_results.json`

### ALL-014 | Starved Forms x Congruence Pairs Cross-Correlation
- **Source**: Claude (Part 2 #3)
- **Batch**: Part 2
- **Description**: Are 156 starved forms overrepresented among congruence pairs?
- **Result**: SINGLE PHENOMENON at mod-5. 27/156 overlap (1.65x, p=0.006). 22/27 same-prime. 5 different-prime overlaps are genuinely independent constraints
- **Data**: `v2/starved_congruence_results.json`

### ALL-015 | Gamma Function as Algebraic Wormhole
- **Source**: Claude (Part 2 #5)
- **Batch**: Part 2
- **Description**: Test if Gamma-connected pairs have closer mod-p fingerprint distance than random
- **Result**: GAMMA IS REAL. 12.7% closer (260/300 module pairs). Wins at every prime. Elliptic-AGM-pi triad = essentially one object through Gamma lens
- **Data**: `v2/gamma_wormhole_results.json`

### ALL-016 | Residual Representation Clustering
- **Source**: ChatGPT (Part 2 #1)
- **Batch**: Part 2
- **Description**: Cluster modular forms by mod-ell Galois representation vectors, not just pairwise
- **Result**: THREE FINDINGS. Mod-3 has massive hubs (max 109). Cross-ell independence is TOTAL (zero mod-3/mod-5 overlap). 35 multi-level clusters at ell=5 invisible to same-level scanning
- **Data**: `v2/residual_rep_results.json`

### ALL-017 | Symmetry Group Detection via Action (Layer 3)
- **Source**: ChatGPT (Part 2 #4)
- **Batch**: Part 2
- **Description**: Infer hidden symmetry from coefficient behavior, detect twists/characters/CM
- **Result**: LAYER 3 OPEN. 126 same-level twist pairs, 48 cross-level, 127 character matches. CM rediscovery: F1=1.00 (perfect). 174 total twist pairs
- **Data**: `v2/symmetry_detection_results.json`

### ALL-018 | Failure Mode Mining (Battery Autobiography)
- **Source**: ChatGPT (Part 2 #5)
- **Batch**: Part 2
- **Description**: Cluster the ways 288K killed hypotheses fail. Find near-misses
- **Result**: 641 "almost real" structures (pass 7+, fail 1). F3 kills 75.8%. F4/F7/F8 dormant. LMFDB is the "attractive nuisance"
- **Data**: `v2/failure_mode_results.json`

### ALL-019 | Sato-Tate Moments Classifier
- **Source**: DeepSeek (Part 2 #2)
- **Batch**: Part 2
- **Description**: Classify genus-2 curves by ST group using first 4-6 moments of a_p
- **Result**: 98.3% accuracy with 20-dim Mahalanobis. b_p moments essential (a_p-only = 45.6%). 6 rare groups at 100%. J(E_6) hardest at 29.4%
- **Data**: `v2/sato_tate_moments_results.json`

### ALL-020 | Knot Jones Polynomial Recurrence Clustering
- **Source**: DeepSeek (Part 2 #3)
- **Batch**: Part 2
- **Description**: Berlekamp-Massey on Jones polynomial coefficient sequences for 13K knots
- **Result**: TWO FAMILIES. Cyclotomic family (44 knots, Phi_12). Torus knot family (4 knots, x^2(x+1)). Torus family matches OEIS cluster of 14 sequences
- **Data**: `v2/knot_jones_results.json`

### ALL-021 | Hypergeometric-to-Modular Correspondence
- **Source**: DeepSeek (Part 2 #5)
- **Batch**: Part 2
- **Description**: Match HGM motive a_p to modular form Hecke eigenvalues. Find new correspondences
- **Result**: CALIBRATION. 49/49 known degree-2 weight-1 matches found. Zero new. LMFDB has complete coverage at degree 2. 76 quadratic twist relationships detected
- **Data**: `v2/hgm_modular_results.json`

### ALL-022 | Gouvea-Mazur Slope Distribution (Eigencurve)
- **Source**: Gemini (Part 2 #4)
- **Batch**: Part 2
- **Description**: Compute p-adic valuation of a_p across modular forms of varying weights
- **Result**: Atkin-Lehner dichotomy confirmed. Weight-2 slopes trivial at p>=5 (binary: ordinary or supersingular). Only 6 dim-1 orbits at weight>2. Gouvea-Mazur ladders need higher-weight data
- **Data**: `v2/slope_distribution_results.json`

### ALL-023 | Lattice-NumberField Determinant Bridge
- **Source**: Internal (Queue)
- **Batch**: Queue C06
- **Description**: Test if lattice determinants predict number field discriminants (tensor sv=5829)
- **Result**: Tested (result file exists). Likely prime confound
- **Data**: `v2/lattice_nf_bridge_results.json`

### ALL-024 | Scaling Law Peak Prime
- **Source**: DeepSeek (Part 3 #1)
- **Batch**: Part 3 / Round 3
- **Description**: Map enrichment curve to p=31. Does it plateau, peak, or drop?
- **Result**: DONE. Result file exists at `v2/scaling_law_peak_results.json`
- **Data**: `v2/scaling_law_peak_results.json`

### ALL-025 | Near-Miss Resurrection (641 ghosts)
- **Source**: James (Round 3 J3), ChatGPT (Round 3 #1), DeepSeek (Round 3 DS-R3-3), DeepSeek (Part 3 #5)
- **Batch**: Round 3 (unanimous #1 priority) + Part 3
- **Description**: Re-run battery on 641 near-misses with parameter sweeps (F14 lags 0-10, F13 windows). Apply Layer 3
- **Result**: DONE. 253/641 resurrected (39.5%). 193 pass Layer 3 (76.3%). Top domain pair: KnotInfo--LMFDB (106)
- **Data**: `v2/near_miss_results.json`

### ALL-026 | Galois Image Portrait (Trace Density Classification)
- **Source**: James (Round 3 J1), Gemini (Part 3 #2)
- **Batch**: Round 3 + Part 3
- **Description**: Distinguish Large (SL_2(F_ell)) from Small (dihedral/Borel) Galois image purely from a_p distribution
- **Result**: DONE. Result file exists at `v2/galois_image_results.json`
- **Data**: `v2/galois_image_results.json`

### ALL-027 | Generating Function Isomorphism (Collatz Cousins)
- **Source**: DeepSeek (Round 3 DS-R3-5), DeepSeek (Part 3 #6)
- **Batch**: Round 3 + Part 3
- **Description**: Compute rational generating functions for all 2,740 characteristic polynomials. Cluster by reduced G(x)
- **Result**: DONE. 9,360 sequences processed. 9,182 genfunc clusters vs 2,340 char-poly clusters (compression ratio 0.25)
- **Data**: `v2/genfunc_isomorphism_results.json`

### ALL-028 | M24->EC Moonshine Sturm Verification
- **Source**: DeepSeek (Part 3 #7)
- **Batch**: Part 3
- **Description**: Verify 4 M24 matches to Sturm bound (several hundred primes) for exact equality
- **Result**: DONE. Tested against 90 terms of A053250 against modular forms at levels 2420, 3190, 4170, 4305
- **Data**: `v2/moonshine_sturm_results.json`

### ALL-029 | Jones vs Alexander Recurrence Independence
- **Source**: DeepSeek (Part 3 #8)
- **Batch**: Part 3
- **Description**: Test whether any knot shares both a Jones and Alexander recurrence. Full 13K dataset
- **Result**: DONE. 12,965 knots tested
- **Data**: `v2/jones_alexander_results.json`

### ALL-030 | Mod-2 Triangle ST Community Analysis
- **Source**: Claude (Part 3 #1)
- **Batch**: Part 3
- **Description**: Color mod-2 GSp_4 triangle nodes by Sato-Tate group. Do triangles stay within ST class?
- **Result**: DONE. 20,917 triangles analyzed. ST group distribution mapped
- **Data**: `v2/mod2_triangle_st_results.json`

### ALL-031 | Moonshine Scaling Law
- **Source**: Claude (Part 3 #2)
- **Batch**: Part 3
- **Description**: Run universal scaling law on moonshine bridges partitioned by type (mock theta vs McKay-Thompson vs Niemeier)
- **Result**: DONE. 150 bridges analyzed across 5 primes. Universal baseline ~8x flat enrichment
- **Data**: `v2/moonshine_scaling_results.json`

### ALL-032 | GSp_4 Cross-Ell Independence
- **Source**: Claude (Part 3 #4)
- **Batch**: Part 3
- **Description**: Test cross-ell independence on degree-4 side. Do mod-3 GSp_4 pairs entangle in mod-2 graph?
- **Result**: DONE. 65,534 curves tested
- **Data**: `v2/gsp4_cross_ell_results.json`

### ALL-033 | Multi-Prime Intersection Geometry
- **Source**: ChatGPT (Part 3 #1)
- **Batch**: Part 3
- **Description**: Intersect mod-ell constraints across multiple primes. Test adelic reconstruction hypothesis
- **Result**: DONE. 17,314 forms tested across ell=3,5,7 at intersection depths 1-3
- **Data**: `v2/multi_prime_results.json`

### ALL-034 | High-Prime Stability Test
- **Source**: ChatGPT (Part 3 #5)
- **Batch**: Part 3
- **Description**: For each hypothesis, track signal growth vs decay as prime increases. Turn CL1 into a filter
- **Result**: DONE. 11/11 tests STABLE. 100% stability rate
- **Data**: `v2/high_prime_stability_results.json`

### ALL-035 | HMF Congruence Scan (Hilbert Modular Forms)
- **Source**: Grok (Part 1 #1)
- **Batch**: Part 1 / Queue C04
- **Description**: Run congruence scan across Hilbert newforms over Q(sqrt(d))
- **Result**: DATA INVENTORY COMPLETE but NO Hecke eigenvalues in the HMF dump. Structurally blocked — need hmf_hecke table
- **Data**: `v2/hmf_congruence_results.json`

### ALL-036 | Quinary Paramodular Database Ingest (C01-v2)
- **Source**: Grok (Part 2 #1)
- **Batch**: Part 2
- **Description**: Ingest ALRTV23/Poor-Yuen Hecke eigenvalue tables. Run congruence scan against genus-2 curves
- **Result**: STRUCTURAL WIN. Perfect level bijection at 7 primes <= 600. Root number 7/7. Hecke eigenvalue 37/40 (92.5%). Technical discovery: naive eigenvalue formula not universal for fixed T_0
- **Data**: `v2/paramodular_probe_v2_results.json`

### ALL-037 | Scaling Law vs ST Order
- **Source**: Internal
- **Batch**: Internal analysis
- **Description**: Test if scaling law enrichment correlates with Sato-Tate group order
- **Result**: DONE. Result file exists
- **Data**: `v2/scaling_vs_st_order_results.json`

---

# READY — Data Exists, Not Yet Executed

---

### ALL-038 | Mock Shadow Mapping
- **Source**: James (Round 3 J4)
- **Batch**: Round 3
- **Description**: Give tool mock theta functions and ask it to find their shadows in the 17K modular forms via residual fingerprints
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: HIGH
- **Data needed**: OEIS mock theta sequences + DuckDB modular forms (both exist)

### ALL-039 | Scaling Law as Active Detector
- **Source**: DeepSeek (Round 3 DS-R3-1), ChatGPT (Round 3 #2)
- **Batch**: Round 3
- **Description**: Take 10K OEIS sequences without known algebraic interpretations. Rank by enrichment slope. Verify top 5% with BM + LMFDB
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: OEIS sequences + enrichment pipeline (both exist)

### ALL-040 | Deformation Paths / Trajectories
- **Source**: ChatGPT (Part 2 #2), ChatGPT (Round 3 #3), Grok (Part 3 #1)
- **Batch**: Part 2 + Round 3 + Part 3
- **Description**: Build nearest-neighbor chains in a_p feature space. Detect smooth paths (approximating p-adic families)
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM (complex build)
- **Data needed**: a_p vectors from DuckDB (exist)

### ALL-041 | Twist Network of Mod-7 Anomaly
- **Source**: DeepSeek (Part 3 #2)
- **Batch**: Part 3
- **Description**: Compute all quadratic twists of 8 mod-7 starved forms. Is starvation twist-invariant?
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: CT4 twist detector + LMFDB forms (both exist)

### ALL-042 | Operadic Permeability Constant (Is 0.813 Universal?)
- **Source**: DeepSeek (Part 3 #3)
- **Batch**: Part 3
- **Description**: Compute within/between module distance ratio on DLMF and other formula corpora. Is 0.813 stable?
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: DLMF LaTeX/XML (publicly available, not yet ingested)

### ALL-043 | Mod-2 Triangle Classification by Isogeny Type
- **Source**: DeepSeek (Part 3 #4)
- **Batch**: Part 3
- **Description**: For 1000 random triangles, compute Richelot isogeny, RM field, mod-2 rep type
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: MEDIUM (partially needs SageMath)
- **Data needed**: LMFDB isogeny data for genus-2 (partial), SageMath for Richelot

### ALL-044 | ST Moment Space Visualization (t-SNE/UMAP)
- **Source**: DeepSeek (Part 3 #9)
- **Batch**: Part 3
- **Description**: Reduce 20-dim moment vectors to 2D. Visualize boundaries between ST groups
- **Landscape value**: LOW
- **Difficulty**: 1
- **Priority**: MEDIUM
- **Data needed**: DS2 moment vectors (exist)

### ALL-045 | Prime-Weighted Distance Metric
- **Source**: ChatGPT (Part 3 #2)
- **Batch**: Part 3
- **Description**: Define distance using CL1 enrichment weights. Test if geometry improves clustering
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: Mod-p fingerprints (exist)

### ALL-046 | Nonlinear Transformation Search
- **Source**: ChatGPT (Part 3 #3)
- **Batch**: Part 3
- **Description**: Try polynomial, convolution, exp/log transforms on near-miss pairs to rescue them
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: HIGH
- **Data needed**: Near-miss pairs from CT5 (exist)

### ALL-047 | Phase-Shift & Oscillation Alignment
- **Source**: ChatGPT (Part 3 #4)
- **Batch**: Part 3
- **Duplicate of**: Partially overlaps ALL-025 (near-miss resurrection)
- **Description**: Allow index shift, periodic phase alignment, Fourier alignment on sequences
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: Near-miss pairs (exist)

### ALL-048 | Cross-Domain Moment Matching
- **Source**: ChatGPT (Part 3 #6)
- **Batch**: Part 3
- **Description**: Compute moment vectors for OEIS, knots, modular forms. Look for cross-domain clusters
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: All datasets (exist)

### ALL-049 | Local-to-Global Consistency Check
- **Source**: ChatGPT (Part 3 #7)
- **Batch**: Part 3
- **Description**: For candidate pairs, check if matching prime set grows or shrinks. Test global persistence
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: Candidate pairs (exist)

### ALL-050 | Motif Extraction from Mod-2 Congruence Graphs
- **Source**: ChatGPT (Part 3 #8)
- **Batch**: Part 3
- **Related to**: ALL-013 (mod-2 graph), ALL-043 (triangle classification)
- **Description**: Extract cliques, K3/K4 motifs, central nodes from dense mod-2 graph
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: Mod-2 graph data (exists)

### ALL-051 | Recurrence Stability Under Prime Reduction
- **Source**: ChatGPT (Part 3 #9)
- **Batch**: Part 3
- **Description**: Reduce OEIS recurrences mod p. Check which survive. Align survivors with algebraic objects
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: OEIS recurrences (exist)

### ALL-052 | Dual Representation Consistency
- **Source**: ChatGPT (Part 3 #10)
- **Batch**: Part 3
- **Description**: Build multiple views (coefficient, moment, mod-p fingerprint) per object. Check cluster consistency
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: All computed features (exist)

### ALL-053 | Scaling Law on Moonshine Bridge Types
- **Source**: Claude (Part 3 #2)
- **Batch**: Part 3
- **Duplicate of**: ALL-031 (executed version)
- **Description**: Partition moonshine bridges by type and compute enrichment slopes separately
- **Status**: See ALL-031 (DONE)

### ALL-054 | Gamma Metric: Distance from Moonshine to Number Theory
- **Source**: Claude (Part 3 #3)
- **Batch**: Part 3
- **Description**: Compute Gamma-path distance from moonshine Fungrim modules to EC modules. Is moonshine "close" or "far"?
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: Gamma wormhole data (exists), Fungrim module distances (exist)

### ALL-055 | Scaling Law vs Conductor (Triangle Density)
- **Source**: Claude (Part 3 #5)
- **Batch**: Part 3
- **Description**: Plot mod-2 triangle density vs conductor. Phase transition?
- **Landscape value**: MEDIUM
- **Difficulty**: 1
- **Priority**: HIGH
- **Data needed**: Mod-2 triangle data (exists)

### ALL-056 | CL3 Different-Prime Overlaps Dissection
- **Source**: Claude (Part 3 #6)
- **Batch**: Part 3
- **Description**: Feed 5 different-prime starvation/congruence overlaps into dissection suite. Find structural marker
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: CL3 results + Fungrim (exist)

### ALL-057 | BM on Graph Statistics vs Prime
- **Source**: Claude (Part 3 #7)
- **Batch**: Part 3
- **Description**: Compute triangles(ell), edges(ell), max-clique(ell) as sequences in ell. Run BM. Is Hasse squeeze algebraic?
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: Graph statistics across primes (exist)

### ALL-058 | Algebraic Family Clusters vs Operadic Skeleton Partition
- **Source**: Claude (Part 3 #8)
- **Batch**: Part 3
- **Description**: Check if 269 algebraic families are strict subsets of operadic classes or if they cross
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: Both datasets exist

### ALL-059 | CM Detection (CT4) on GSp_4 Congruence Pairs
- **Source**: Claude (Part 3 #9)
- **Batch**: Part 3
- **Description**: Apply zero-frequency CM separator to 37 genus-2 pairs. Do congruence partners share CM-like properties?
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: GSp_4 pairs + a_p/b_p data (exist)

### ALL-060 | Universal Verbs vs Scaling Slope
- **Source**: Claude (Part 3 #10)
- **Batch**: Part 3
- **Description**: Map which of 4 universal verbs dominate in each scaling-law family. Connect CL1 to C12
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: CL1 families + C12 verb data + Fungrim (all exist)

### ALL-061 | Battery Failure-Mode Rewrite Rules
- **Source**: Grok (Part 3 #9)
- **Batch**: Part 3
- **Description**: Mine 641 near-misses, synthesize rewrite rules that would make them pass. Cluster rules into universal verb set
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM
- **Data needed**: Near-miss data (exists)

### ALL-062 | Knot-Primes Starvation Dictionary
- **Source**: Gemini (Part 3 #6)
- **Batch**: Part 3
- **Description**: Map mod-p starvation patterns to zeros of Alexander polynomials via arithmetic topology analogy
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM
- **Data needed**: Alexander polynomial data (KnotInfo, exists), starvation results (exist)

### ALL-063 | Kloosterman Sum Distribution
- **Source**: Gemini (Part 3 #7)
- **Batch**: Part 3
- **Description**: Feed raw Kloosterman sum sequences, see if tool reconstructs modular form level or ST distribution
- **Landscape value**: MEDIUM
- **Difficulty**: 3
- **Priority**: MEDIUM
- **Data needed**: Kloosterman sums (computable, not pre-cached)

### ALL-064 | Universal ST Ratio (Weight Scaling)
- **Source**: Gemini (Part 3 #9)
- **Batch**: Part 3
- **Description**: Test if moment vectors scale predictably with weight k. Classification boundary phase transitions?
- **Landscape value**: MEDIUM
- **Difficulty**: 3
- **Priority**: LOW (needs higher-weight data)
- **Data needed**: Higher-weight forms (limited in DB)

### ALL-065 | Complexity Entropy of Rosetta Stone
- **Source**: Gemini (Part 3 #10)
- **Batch**: Part 3
- **Description**: Measure algorithmic complexity of bridging vs peripheral modules. Are universal verbs more central in rewrite graph?
- **Landscape value**: MEDIUM
- **Difficulty**: 3
- **Priority**: MEDIUM
- **Data needed**: Formula corpus (exists)

### ALL-066 | Mod-p Fingerprint Algebraic Families vs Fungrim (original formula)
- **Source**: Claude (Part 1 #4, original operadic cross-comparison)
- **Batch**: Part 2 (Claude #4, untested)
- **Description**: Extract operadic skeletons from tau congruences and all known modular form congruences as formulas. Cluster by skeleton
- **Landscape value**: MEDIUM
- **Difficulty**: 3
- **Priority**: MEDIUM
- **Data needed**: Symbolic congruence statements (need formula-to-executable pipeline)

### ALL-067 | Knot Bridge Expansion (Torus Family -> OEIS)
- **Source**: ChatGPT (Round 3 #5)
- **Batch**: Round 3
- **Description**: Extend DS3 torus knot family to full OEIS match scan
- **Landscape value**: MEDIUM
- **Difficulty**: 2
- **Priority**: MEDIUM
- **Data needed**: DS3 results + OEIS (exist)

### ALL-068 | Mod-2 Clique Deconstruction (Richelot Isogenies)
- **Source**: DeepSeek (Round 3 DS-R3-2), ChatGPT (Round 3 #4)
- **Batch**: Round 3
- **Duplicate of**: ALL-043 (near-duplicate, same theme)
- **Description**: For each clique, compute Richelot isogeny degree, (2,2)-isogeny, maximal isotropic subgroups
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: MEDIUM (needs SageMath for full)
- **Data needed**: LMFDB isogeny data (partial), SageMath

### ALL-069 | Scaling Law Slope as Classification Invariant
- **Source**: ChatGPT (Round 3 #2)
- **Batch**: Round 3
- **Related to**: ALL-039
- **Description**: Does slope depend on dimension, degree, symmetry group?
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH
- **Data needed**: Enrichment data (exists)

### ALL-070 | Higher-Degree HGM Motive Congruence Scan
- **Source**: Grok (Part 3 #8)
- **Batch**: Part 3
- **Description**: Extend HGM pipeline to 236 remaining degree-3/4 motives. Match against genus-2/3 and weight-3/4 forms
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: MEDIUM
- **Data needed**: HGM DB (exists), weight-3/4 forms (limited)

---

# BLOCKED — Missing Data or Infrastructure

---

### ALL-071 | Genus-3 Sato-Tate 410-Group Classifier
- **Source**: DeepSeek (Part 1 #4), Gemini (Part 1 #4), DeepSeek (Round 3 DS-R3-4), Grok (Part 3 #2), Gemini (Part 3 #1), DeepSeek (Part 3 #10)
- **Batch**: Part 1 + Part 3 + Round 3 (6 proposals across sessions)
- **Description**: Classify genus-3 curves by Sato-Tate group from coefficient distributions. 410 possible groups
- **Blocked by**: SageMath for genus-3 Frobenius computation. 82K curve equations exist
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: HIGH once unblocked

### ALL-072 | Maeda Conjecture Verification
- **Source**: DeepSeek (Part 1 #1)
- **Batch**: Part 1 / Queue C14
- **Description**: Verify irreducibility + Galois group = S_n for T_2 on S_k(SL_2(Z)) at large weights
- **Blocked by**: Higher-weight Hecke characteristic polynomials (computable via SageMath)
- **Landscape value**: MEDIUM
- **Difficulty**: 3
- **Priority**: MEDIUM once unblocked

### ALL-073 | Hida Theory / p-adic Families
- **Source**: Gemini (Part 1 #2), DeepSeek (Part 2 #1), Grok (Part 3 #5), Grok (Part 2 #5)
- **Batch**: Part 1 + Part 2 + Part 3 (4 proposals)
- **Description**: Detect when mod-ell congruences are shadows of p-adic Hida families
- **Blocked by**: SageMath p-adic arithmetic + higher-weight forms at same level
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: HIGH once unblocked

### ALL-074 | Quantum Modular Forms / Knots
- **Source**: Gemini (Part 1 #3)
- **Batch**: Part 1 / Queue C16
- **Description**: Link Jones polynomial asymptotics near roots of unity to mock theta functions
- **Blocked by**: Jones polynomial evaluations at high precision near roots of unity
- **Landscape value**: HIGH
- **Difficulty**: 5
- **Priority**: MEDIUM

### ALL-075 | HMF Congruence Scan (Full)
- **Source**: Grok (Part 1 #1)
- **Batch**: Part 1 / Queue C04
- **Description**: Run congruence scan across Hilbert newforms over Q(sqrt(d))
- **Blocked by**: HMF dump contains NO Hecke eigenvalues. Need hmf_hecke table from LMFDB
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH once unblocked

### ALL-076 | Picard-Fuchs Operadic Skeleton
- **Source**: James (Round 3 J2), Gemini (Part 3 #3)
- **Batch**: Round 3 + Part 3
- **Description**: Map operadic skeletons of Calabi-Yau differential operators against L-function skeletons
- **Blocked by**: Picard-Fuchs operator database (AESZ or similar) not in pipeline
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM

### ALL-077 | Brauer-Manin Obstruction Probe
- **Source**: James (Round 3 J5)
- **Batch**: Round 3
- **Description**: Can mod-p fingerprinting detect structural thinning for equations with only local solutions?
- **Blocked by**: Curated set of Brauer-Manin obstructed equations not available
- **Landscape value**: MEDIUM
- **Difficulty**: 4
- **Priority**: LOW

### ALL-078 | ML Sato-Tate Classifier on Genus-3
- **Source**: Grok (Part 2 #3)
- **Batch**: Part 2
- **Duplicate of**: ALL-071 (same core requirement)
- **Description**: Train classifier on genus-2, apply to genus-3
- **Blocked by**: SageMath for genus-3 Frobenius

### ALL-079 | Which of 410 Groups Occur Over Q?
- **Source**: DeepSeek (Part 3 #10)
- **Batch**: Part 3
- **Duplicate of**: ALL-071 (related, specific sub-question)
- **Description**: For each of 410 groups, find at least one genus-3 curve realizing it or prove non-existence
- **Blocked by**: Genus-3 Frobenius computation
- **Landscape value**: HIGH
- **Difficulty**: 5
- **Priority**: HIGH once unblocked

### ALL-080 | Shintani Reversal (Half-Integral Weight Bridge)
- **Source**: Gemini (Part 2 #2), Grok (Part 3 #6)
- **Batch**: Part 2 + Part 3
- **Description**: Search OEIS for c(|D|)^2 proportional to L(f, chi_D, 1)
- **Blocked by**: L-value computation (needs SageMath/PARI)
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM

### ALL-081 | Pizer Graph Isomorphism (Spectral)
- **Source**: Gemini (Part 2 #3), Grok (Part 3 #7)
- **Batch**: Part 2 + Part 3
- **Description**: See if structural layer recognizes graph spectrum as Hecke eigenvalues
- **Blocked by**: Brandt matrix / Pizer graph construction (needs SageMath or pre-computed data)
- **Landscape value**: HIGH
- **Difficulty**: 4
- **Priority**: MEDIUM

### ALL-082 | Rigid Analytic Tate-Curve Fingerprinting
- **Source**: Gemini (Part 3 #4)
- **Batch**: Part 3
- **Description**: Identify p-adic circle in coefficient data for curves with v_p(j) < 0
- **Blocked by**: p-adic coefficient precision (needs CAS)
- **Landscape value**: MEDIUM
- **Difficulty**: 4
- **Priority**: LOW

### ALL-083 | Vertex-Algebra Moonshine Expansion
- **Source**: Grok (Part 2 #4), Grok (Part 3 #4)
- **Batch**: Part 2 + Part 3
- **Description**: Extend moonshine to Cheng-Duncan-Harvey vertex-algebra trace functions and higher-lambency mock thetas
- **Blocked by**: Higher-lambency mock theta data (arXiv:2203.03052) not ingested
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: MEDIUM (data acquisition task)

### ALL-084 | Sporadic Group Moonshine Hubs (Co_1, Suz)
- **Source**: Gemini (Part 2 #5), Grok (Part 3 #10)
- **Batch**: Part 2 + Part 3
- **Description**: Ingest McKay-Thompson tables for Co_1, Suz sporadic groups. Apply operadic dissection
- **Blocked by**: Sporadic group McKay-Thompson coefficient tables (need ATLAS/arXiv)
- **Landscape value**: HIGH
- **Difficulty**: 3
- **Priority**: MEDIUM (data acquisition task)

### ALL-085 | FindStat Algebraic DNA Expansion
- **Source**: Grok (Part 2 #2), Grok (Part 3 #3)
- **Batch**: Part 2 + Part 3
- **Description**: Ingest FindStat numerical values, extract characteristic polynomials, cross-match operadic skeletons
- **Blocked by**: FindStat API numerical values not cached (metadata only currently)
- **Landscape value**: HIGH
- **Difficulty**: 2
- **Priority**: HIGH once data fetched

---

# DEFERRED — Lower Priority or Superseded

---

### ALL-086 | Cross-Domain Generating Function Matching
- **Source**: ChatGPT (Part 2 #3)
- **Batch**: Part 2
- **Description**: Compare generating functions (poles, singularities, growth type) across OEIS, MF, partitions, theta series
- **Deferred**: Requires building GF approximation layer. C08 recurrence extraction is a coarse proxy
- **Landscape value**: MEDIUM
- **Difficulty**: 4

### ALL-087 | Operadic Rewrite Dynamics
- **Source**: DeepSeek (Part 2 #4)
- **Batch**: Part 2
- **Description**: Build rewrite graph on 10K formulas. Find canonical forms / attractors
- **Deferred**: Combinatorial explosion. 2-3 week build. C12 static analysis exists
- **Landscape value**: MEDIUM
- **Difficulty**: 4

### ALL-088 | Asymptotic Regime-Shift Hunting in q-series
- **Source**: Grok (Part 1 #4)
- **Batch**: Part 1
- **Description**: Extend DP pipeline to q-series, partitions, mock modular sequences
- **Deferred**: Lower priority given other active challenges. Infrastructure exists (22K terms produced)
- **Landscape value**: MEDIUM
- **Difficulty**: 2

### ALL-089 | Borcherds Product Skeletons
- **Source**: Gemini (Part 3 #5)
- **Batch**: Part 3
- **Description**: Apply operadic suite to Kac-Moody denominator formulas. Test if moonshine is cleaner in product space
- **Deferred**: Requires Borcherds product formula corpus
- **Landscape value**: MEDIUM
- **Difficulty**: 4

### ALL-090 | Umbral Shadow Identification (Mock -> Classical)
- **Source**: Gemini (Part 3 #8)
- **Batch**: Part 3
- **Related to**: ALL-038 (mock shadow mapping, READY)
- **Description**: Feed mock theta coefficients, find "shadow" in 17K forms via residual fingerprints
- **Deferred**: Covered by ALL-038 (James's version, higher priority)
- **Landscape value**: HIGH
- **Difficulty**: 3

---

# SUMMARY STATISTICS

| Status | Count |
|--------|-------|
| DONE | 37 |
| READY | 33 |
| BLOCKED | 15 |
| DEFERRED | 5 |
| **Total unique** | **90** |

(Some proposals were true duplicates collapsed into single entries above. The 115 raw proposals from all sources reduce to ~90 unique challenges.)

## Duplicate / Merge Map

| Theme | Proposals | Collapsed Into |
|-------|-----------|----------------|
| Moonshine expansion | Claude P1#2, DeepSeek P1#2, Grok P1#2 | ALL-002 |
| Recurrence duality | ChatGPT P1#3, DeepSeek P1#3, Grok P1#5 | ALL-008 |
| Operadic dynamics | ChatGPT P1#5, Gemini P1#5, Grok P1#3 | ALL-010 |
| Paramodular conjecture | Gemini P1#1, DeepSeek P1#5, Grok P2#1 | ALL-011/036 |
| Genus-3 ST 410 groups | DeepSeek P1#4, Gemini P1#4, DeepSeek R3, Grok P3#2, Gemini P3#1, DeepSeek P3#10 | ALL-071/079 |
| Hida/p-adic families | Gemini P1#2, DeepSeek P2#1, Grok P2#5, Grok P3#5 | ALL-073 |
| Near-miss resurrection | James R3-J3, ChatGPT R3#1, DeepSeek R3, DeepSeek P3#5 | ALL-025 |
| Mod-2 triangle classification | DeepSeek P3#4, DeepSeek R3-DS-R3-2, ChatGPT R3#4 | ALL-043/068 |
| Shintani reversal | Gemini P2#2, Grok P3#6 | ALL-080 |
| Pizer graph | Gemini P2#3, Grok P3#7 | ALL-081 |
| Sporadic moonshine | Gemini P2#5, Grok P3#10 | ALL-084 |
| FindStat expansion | Grok P2#2, Grok P3#3 | ALL-085 |
| Mock shadow mapping | James R3-J4, Gemini P3#8 | ALL-038/090 |
| Galois image portrait | James R3-J1, Gemini P3#2 | ALL-026 |
| Vertex-algebra moonshine | Grok P2#4, Grok P3#4 | ALL-083 |
| Deformation paths | ChatGPT P2#2, ChatGPT R3#3, Grok P3#1 | ALL-040 |
| Scaling law as detector | DeepSeek R3, ChatGPT R3#2 | ALL-039 |
| Generating function iso | DeepSeek R3, DeepSeek P3#6 | ALL-027 |

## Top 10 READY by Priority

| Rank | ID | Title | Value | Difficulty |
|------|----|-------|-------|------------|
| 1 | ALL-038 | Mock Shadow Mapping | HIGH | 3 |
| 2 | ALL-039 | Scaling Law as Active Detector | HIGH | 2 |
| 3 | ALL-046 | Nonlinear Transformation Search | HIGH | 3 |
| 4 | ALL-054 | Gamma Metric: Moonshine-to-NT Distance | HIGH | 2 |
| 5 | ALL-058 | Algebraic Families vs Operadic Partition | HIGH | 2 |
| 6 | ALL-060 | Universal Verbs vs Scaling Slope | HIGH | 2 |
| 7 | ALL-069 | Scaling Slope as Classification Invariant | HIGH | 2 |
| 8 | ALL-041 | Twist Network of Mod-7 Anomaly | MEDIUM | 2 |
| 9 | ALL-055 | Triangle Density vs Conductor | MEDIUM | 1 |
| 10 | ALL-067 | Knot Bridge Expansion | MEDIUM | 2 |

## Top 5 BLOCKED by Value (Unblock These First)

| Rank | ID | Title | Blocked By |
|------|----|-------|------------|
| 1 | ALL-071 | Genus-3 ST 410 Groups | SageMath |
| 2 | ALL-073 | Hida/p-adic Families | SageMath + higher-weight forms |
| 3 | ALL-075 | HMF Congruence Scan | hmf_hecke table from LMFDB |
| 4 | ALL-085 | FindStat Algebraic DNA | FindStat API numerical values |
| 5 | ALL-083 | Vertex-Algebra Moonshine | Higher-lambency mock theta data |

---

*Compiled by Charon from: 5_From_Each.md (25), 5_From_Each_Part_2.md (25), 10_From_Each_Part_3.md (50), round3_challenges.md (15), challenge_queue.md (17 consolidated). Results verified against v2/ result files.*
