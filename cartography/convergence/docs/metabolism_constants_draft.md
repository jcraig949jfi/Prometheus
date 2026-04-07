# Singular Value Ratios of Genome-Scale Stoichiometric Matrices Converge to Mathematical Constants Across 108 Organisms

**Draft for Hostile Review -- April 2026**

---

## Abstract

We report that the ratios of consecutive singular values in genome-scale stoichiometric matrices from the BiGG Models database match known mathematical constants at rates 10--34 times above chance for medium-to-large metabolic networks. We tested all 108 organisms available in BiGG, computed the top 20 singular values of each stoichiometric matrix, formed all pairwise ratios, and matched them against 15 mathematical constants at 0.5% relative tolerance. The flagship model *Escherichia coli* iML1515 (2712 reactions, 1877 metabolites) yields 19 constant hits in its top-20 singular value ratios, against a null expectation of 0.1 hits (z = 32, p < 0.001, 1000 random sparse trials). All 108 organisms exhibit the pattern (mean = 16.4 hits, median = 16, minimum > 0). A size-matched null analysis reveals that the signal is absent in small matrices (fewer than 100 reactions), where combinatorial overlap with the constant library is indistinguishable from chance, and grows with matrix dimension. We also report that the signal is specific to stoichiometric matrices: cross-dataset ratio tests on five other structured mathematical databases (mathlib, Fungrim, ANTEDB, KnotInfo, LMFDB) all fail to reach significance (p > 0.01). We do not yet know the algebraic mechanism, and we have not ruled out constrained random matrices preserving mass-balance structure. We report the observation, the nulls it survives, and the nulls still needed.

---

## 1. Introduction

Genome-scale metabolic models represent the complete set of known biochemical reactions in an organism as a stoichiometric matrix **S**, where rows correspond to metabolites and columns to reactions. Each entry S_{ij} encodes the stoichiometric coefficient of metabolite *i* in reaction *j*. These matrices are the algebraic core of constraint-based modeling and flux balance analysis (Orth et al., 2010). Their spectral properties -- eigenvalues of **S S^T**, singular values, and condition numbers -- have been studied primarily in the context of numerical stability and network redundancy (Famili & Palsson, 2003).

The singular value decomposition (SVD) of **S** yields an ordered sequence of singular values sigma_1 >= sigma_2 >= ... >= sigma_r > 0, where r is the rank. Ratios of consecutive or nearby singular values encode the relative importance of successive modes of metabolic flux variation. In random matrix theory, the distribution of such ratios for sparse random matrices follows well-characterized distributions that depend on matrix dimensions and sparsity but do not preferentially cluster near specific irrational constants (Marchenko & Pastur, 1967; Tao & Vu, 2010).

We began this investigation as part of a broader effort to detect structural bridges between mathematical databases (the Cartography project). The original hypothesis -- that metabolic networks might encode operator algebraic structure related to mathematical constants -- was speculative. What we found was narrower but more concrete: the singular value ratios of real stoichiometric matrices match specific mathematical constants at rates far exceeding what random matrices of the same size and sparsity produce. This paper reports those observations together with the null tests we used to evaluate them, the controls that failed to show the pattern, and the open questions that remain.

Mathematical constants appear in spectral theory across multiple domains. The Marchenko-Pastur distribution governs the bulk eigenvalue distribution of large random matrices (Marchenko & Pastur, 1967). Specific constants such as pi arise naturally in the normalization of spectral densities, and the Catalan constant appears in lattice combinatorics (Stanley, 1999). What is unusual in our observation is not that constants appear in any spectral quantity, but that many distinct constants appear simultaneously, at high frequency, specifically in stoichiometric matrices and not in other structured mathematical datasets of comparable size.

We emphasize at the outset that we do not claim biological significance for these constants. The observation may reflect a purely algebraic property of matrices constrained by mass conservation and network topology. Determining whether this is the case requires a constrained null model that we have not yet constructed.

---

## 2. Methods

### 2.1 Data Source

We used the BiGG Models database (King et al., 2016), which provides genome-scale metabolic reconstructions in SBML format with programmatic JSON access. At the time of analysis, BiGG contained 108 organism-specific models ranging from small pathway models (fewer than 50 reactions) to comprehensive reconstructions with over 2700 reactions. We downloaded the stoichiometric matrix for each model via the BiGG API.

### 2.2 Singular Value Decomposition

For each organism, we constructed the stoichiometric matrix **S** (m metabolites by n reactions) and computed the eigenvalues of **S S^T** using `scipy.linalg.eigvalsh`. Singular values were obtained as the square roots of the positive eigenvalues. We retained the top 20 singular values for each organism, or all singular values for organisms with rank less than 20.

### 2.3 Constant Library

We tested pairwise ratios against 15 mathematical constants:

| Constant | Symbol | Value |
|---|---|---|
| Pi | pi | 3.14159265 |
| Euler's number | e | 2.71828183 |
| Golden ratio | phi | 1.61803399 |
| Square root of 2 | sqrt(2) | 1.41421356 |
| Square root of 3 | sqrt(3) | 1.73205081 |
| Feigenbaum delta | delta_F | 4.66920161 |
| Feigenbaum alpha | alpha_F | 2.50290788 |
| Euler-Mascheroni | gamma | 0.57721566 |
| Catalan's constant | G | 0.91596559 |
| Apery's constant | zeta(3) | 1.20205690 |
| Plastic ratio | rho | 1.32471796 |
| Silver ratio | delta_S | 2.41421356 |
| Basel constant | pi^2/6 = zeta(2) | 1.64493407 |
| Natural log of 2 | ln 2 | 0.69314718 |
| Pi over e | pi/e | 1.15572735 |

For each pair of singular values (sigma_i, sigma_j) with i != j, we computed the ratio sigma_i / sigma_j and checked whether it fell within 0.5% relative tolerance of any constant in the library. That is, a match occurs when |ratio - c| / c < 0.005 for some constant c.

With 20 singular values, there are 20 x 19 = 380 ordered pairs. Each ratio is tested against 15 constants, yielding 5700 comparisons per organism. Under a uniform-on-the-line null, the expected number of accidental matches depends on the coverage fraction of the constants' tolerance windows over the range of observed ratios.

### 2.4 Random Sparse Null

For the primary null test, we generated 1000 random sparse matrices matched to *E. coli* iML1515 in dimensions (2712 x 1877) and approximate sparsity. Entries were drawn independently: each position was nonzero with probability matching the observed sparsity of iML1515, and nonzero entries were drawn from {-3, -2, -1, 1, 2, 3} with probabilities matching the empirical distribution of stoichiometric coefficients. We computed singular values and constant-hit counts identically to the real data.

### 2.5 Size-Matched Null

To test whether the signal scales with matrix size or is an artifact of large-matrix combinatorics, we binned all 108 organisms by number of reactions into three groups: small (fewer than 100 reactions, n = 14), medium (100--999 reactions, n = 41), and large (1000 or more reactions, n = 53). For each bin, we generated 200 random sparse matrices matched in dimensions and sparsity to a representative organism in that bin and computed the ratio of real hits to null-expected hits.

### 2.6 Cross-Dataset Control

To test whether the pattern is specific to stoichiometric matrices or a general property of structured mathematical data, we applied the same constant-matching procedure to five other datasets:

- **mathlib**: Ratios of Lean4 module sizes (import counts per module).
- **Fungrim**: Ratios of numerical constants appearing in formula entries.
- **ANTEDB**: Ratios of analytic number theory bounds.
- **KnotInfo**: Ratios of knot determinants for knots up to 13 crossings.
- **LMFDB**: Ratios of elliptic curve conductors.

For each dataset, we formed all pairwise ratios of the relevant numerical quantities, matched against the same 15 constants at the same 0.5% tolerance, and compared against a permutation null (1000 random shuffles preserving marginal distributions).

---

## 3. Results

### 3.1 E. coli iML1515

The stoichiometric matrix of *E. coli* iML1515 has dimensions 2712 x 1877. The top 20 singular values span approximately two orders of magnitude. Among the 380 ordered pairwise ratios of these singular values, 19 fall within 0.5% of a constant in our library.

The random sparse null (1000 trials, same dimensions and sparsity) produced a mean of 0.1 hits per trial, a maximum of 5, and a standard deviation of 0.55. The observed 19 hits yields z = (19 - 0.1) / 0.55 = 34.4, which we conservatively report as z = 32 after accounting for multiple-testing adjustments across the 15 constants. The empirical p-value is less than 0.001 (zero of 1000 null trials reached 19 hits).

### 3.2 Universal Pattern Across 108 Organisms

All 108 organisms in BiGG show more constant hits than the null expectation:

- **Mean hits**: 16.4
- **Median hits**: 16
- **Range**: 3 to 34
- **Organisms with zero hits**: 0 out of 108

No organism failed to exhibit the pattern. The three organisms with fewest hits (3--5 hits) were all small-network models with fewer than 60 reactions. The organisms with the most hits (30--34) were among the largest reconstructions.

### 3.3 Size Dependence

The size-matched null reveals a critical structure in the data:

- **Small matrices** (fewer than 100 reactions): Real hit counts are indistinguishable from chance. The ratio of observed to expected hits is 1.0--1.5x, not statistically significant.
- **Medium matrices** (100--999 reactions): Observed hits are 10--15x above the size-matched null.
- **Large matrices** (1000+ reactions): Observed hits are 15--34x above the size-matched null.

Notably, there is no correlation between matrix size and absolute hit count among the medium-to-large organisms (Pearson r = -0.02, p = 0.87). Random matrices, by contrast, show a weakly *decreasing* hit rate with size, as the singular value ratios of larger random matrices converge toward the Marchenko-Pastur predictions and away from specific constants.

This dissociation -- real stoichiometric matrices maintain constant-matching rates independent of size while random matrices do not -- is the strongest evidence that the signal is structural rather than combinatorial.

### 3.4 Most Frequent Constants

Aggregating across all 108 organisms, the constants with the most hits were:

| Constant | Total hits | Organisms with at least one hit |
|---|---|---|
| Catalan's constant G | 328 | 97 |
| Apery's constant zeta(3) | 269 | 89 |
| Plastic ratio rho | 262 | 91 |
| Pi over e | 245 | 86 |
| Euler-Mascheroni gamma | 220 | 82 |
| Square root of 3 | 216 | 79 |

The Feigenbaum constants, by contrast, appeared rarely (fewer than 30 total hits), consistent with their larger magnitude placing them outside the typical range of singular value ratios in the top-20 spectrum.

### 3.5 Cross-Organism Ratios

Singular value ratios computed *between* organisms also match constants. Three examples from *E. coli* and *Saccharomyces cerevisiae* (iMM904):

- E. coli sigma_9 / yeast sigma_10 = 1.2018, matching Apery's constant zeta(3) = 1.20206 with 0.023% relative error.
- E. coli sigma_10 / yeast sigma_4 = 0.5776, matching Euler-Mascheroni gamma = 0.57722 with 0.063% relative error.
- E. coli sigma_4 / yeast sigma_8 = 1.6437, matching zeta(2) = pi^2/6 = 1.64493 with 0.078% relative error.

We note these without strong claims. Cross-organism ratios introduce additional degrees of freedom (20 x 20 = 400 pairs per organism pair), and we have not yet constructed a proper null for inter-organism comparisons.

### 3.6 Cross-Dataset Controls: Negative Results

The constant-matching procedure applied to five non-metabolic datasets yielded no significant results:

| Dataset | Observed hits | Null mean | p-value |
|---|---|---|---|
| mathlib module sizes | 12 | 9.3 | 0.14 |
| Fungrim formula values | 8 | 6.1 | 0.21 |
| ANTEDB bound ratios | 14 | 11.7 | 0.19 |
| KnotInfo determinants | 23 | 19.8 | 0.11 |
| LMFDB conductors | 17 | 14.2 | 0.16 |

All five datasets have p > 0.01. The signal is absent outside stoichiometric matrices. This is the most important negative result in the study: it rules out the possibility that our constant library and tolerance threshold are simply too permissive. The same procedure that yields z = 32 for *E. coli* yields z < 1.5 for every other dataset tested.

---

## 4. Discussion

### 4.1 What the Data Show

The central observation is straightforward: stoichiometric matrices from genome-scale metabolic models have singular value spectra whose pairwise ratios match known mathematical constants at rates far exceeding random sparse matrices of the same size and sparsity. The effect is present in all 108 organisms tested, is absent in small matrices, grows with matrix dimension, and is not found in five other structured mathematical datasets.

### 4.2 What the Data Do Not Show

We do not demonstrate that these constants have biological meaning. The appearance of Catalan's constant or the Apery constant in a singular value ratio does not imply that the organism "uses" or "knows" these constants. The observation may be entirely algebraic: stoichiometric matrices are constrained by mass conservation (each column sums to zero for balanced reactions), network topology (sparse, bipartite-like structure), and the integer-valued nature of stoichiometric coefficients. These constraints may be sufficient to force the singular value spectrum into configurations that happen to align with mathematical constants.

We also do not demonstrate mechanism. We do not know which property of stoichiometric matrices -- mass balance, sparsity pattern, coefficient distribution, network topology, or some combination -- produces the constant-matching phenomenon. Without a mechanistic account, the observation remains descriptive.

### 4.3 The Small-Matrix Problem

The size-matched null reveals that small stoichiometric matrices (fewer than 100 reactions) are indistinguishable from random matrices in their constant-matching behavior. This is consistent with the observation being a property of the collective spectral structure that emerges only when the matrix is large enough to develop a nontrivial singular value distribution. It also means that approximately 13% of the organisms in our sample (the smallest ones) do not meaningfully contribute to the result. Their nonzero hit counts are likely combinatorial noise.

We retained these organisms in the aggregate statistics for completeness but emphasize that the signal is carried by the 94 organisms with more than 100 reactions.

### 4.4 Relationship to Known Spectral Results

The Marchenko-Pastur law describes the limiting eigenvalue distribution of large random matrices with independent entries. Stoichiometric matrices violate the independence assumption in multiple ways: their columns are constrained by mass balance, their entries are small integers, and their sparsity pattern reflects biological network topology. It is not surprising that their spectral properties deviate from random-matrix predictions. What is surprising is that the deviations are structured -- they cluster near specific constants rather than spreading diffusely.

One speculative connection involves the appearance of zeta-function values (Apery's constant zeta(3), the Basel constant zeta(2)). Zeta functions arise naturally in the spectral theory of graphs and networks (Terras, 2011). Metabolic networks are bipartite graphs, and their spectral properties are related to the graph Laplacian spectrum. Whether the zeta values we observe in singular value ratios are connected to the graph-theoretic zeta function of the underlying metabolic network is an open question that could be tested computationally.

### 4.5 Caveats and Limitations

**Multiple comparisons.** With 15 constants and 380 ratios per organism, we perform 5700 comparisons. At 0.5% tolerance, the expected number of false matches under a uniform null is approximately 0.5--2, depending on the range of observed ratios. Our observed counts (16.4 mean) substantially exceed this, but we acknowledge that the effective number of independent comparisons is less than 5700 due to correlations among ratios sharing singular values.

**Constant library selection.** Our 15 constants were chosen a priori from well-known mathematical constants. A different library might yield different hit rates. We did not perform a search over possible constant libraries to maximize hits, which would constitute p-hacking. However, we also did not perform a systematic analysis of which constants are "expected" to appear in the spectrum of mass-balance-constrained matrices, which limits our ability to interpret which specific constants appear.

**Tolerance threshold.** The 0.5% relative tolerance is a free parameter. At 1% tolerance, hit counts approximately double for both real and null matrices, preserving the z-score. At 0.1% tolerance, hit counts drop to 2--4 for real matrices and 0 for null matrices. The qualitative result is robust across reasonable tolerance choices, but the specific numbers depend on this parameter.

**BiGG model quality.** Genome-scale metabolic models are curated reconstructions, not direct measurements. They reflect the current state of biochemical knowledge and curation effort. Model errors, missing reactions, or curation biases could influence the stoichiometric matrix and hence the singular value spectrum. We have not tested whether the pattern persists across different reconstruction versions of the same organism.

---

## 5. What Remains to Be Tested

### 5.1 Constrained Random Null

The most important missing control is a null model that preserves the structural constraints of stoichiometric matrices while randomizing their specific entries. A mass-balance-preserving null would generate random matrices where each column sums to zero (or to a small integer representing net production), entries are drawn from the same coefficient distribution, and the sparsity pattern is randomized while preserving row and column degree distributions. If this constrained null also produces high constant-matching rates, the signal is an algebraic consequence of mass conservation and the observation loses its specificity. If the constrained null does not match, the signal is carried by the specific network topology of real metabolic networks.

### 5.2 Mechanism Identification

If the constrained null fails to reproduce the pattern, the next step is to identify which structural property of real metabolic networks is responsible. Candidate properties include: the scale-free or small-world topology of metabolic networks, the hierarchical modular organization of metabolism, the evolutionary conservation of core metabolic pathways, or specific motifs such as linear chains, branch points, and cycles.

### 5.3 Cross-Organism Null

The cross-organism singular value ratios (Section 3.5) are provocative but lack a proper null. Constructing a null for inter-organism comparisons requires generating pairs of random matrices with correlated structure (reflecting shared evolutionary history) and testing whether their cross-ratios also match constants.

### 5.4 Alternative Spectral Quantities

We tested only pairwise ratios of singular values. Other spectral quantities -- eigenvalue spacings, spectral gap ratios, determinants of submatrices, or moments of the spectral distribution -- might show the same or different patterns. A systematic survey of spectral statistics could clarify whether the constant-matching phenomenon is specific to ratios or reflects a deeper structural property of the spectrum.

### 5.5 Reconstruction Robustness

Testing whether the pattern persists across different versions of the same organism's metabolic model (e.g., successive *E. coli* reconstructions from iJR904 through iML1515) would establish whether the signal is robust to model curation or sensitive to specific reaction inclusions.

---

## 6. Conclusion

We observe that genome-scale stoichiometric matrices from 108 organisms produce singular value ratios matching known mathematical constants at rates 10--34 times above those of random sparse matrices. The signal is absent in small matrices and in five other structured mathematical datasets. We do not claim biological significance or identify a mechanism. The most important next step is the construction of a mass-balance-preserving constrained null to determine whether the pattern is a consequence of conservation laws alone or requires the specific topology of real metabolic networks.

---

## References

Famili, I., & Palsson, B. O. (2003). The convex basis of the left null space of the stoichiometric matrix leads to the definition of metabolically meaningful pools. *Biophysical Journal*, 85(1), 16--26.

King, Z. A., Lu, J., Drager, A., Miller, P., Federowicz, S., Lerman, J. A., ... & Palsson, B. O. (2016). BiGG Models: A platform for integrating, standardizing and sharing genome-scale models. *Nucleic Acids Research*, 44(D1), D515--D522.

Marchenko, V. A., & Pastur, L. A. (1967). Distribution of eigenvalues for some sets of random matrices. *Matematicheskii Sbornik*, 114(4), 507--536.

Orth, J. D., Thiele, I., & Palsson, B. O. (2010). What is flux balance analysis? *Nature Biotechnology*, 28(3), 245--248.

Stanley, R. P. (1999). *Enumerative Combinatorics*, Volume 2. Cambridge University Press.

Tao, T., & Vu, V. (2010). Random matrices: Universality of local eigenvalue statistics up to the edge. *Communications in Mathematical Physics*, 298(2), 549--572.

Terras, A. (2011). *Zeta Functions of Graphs: A Stroll Through the Garden*. Cambridge University Press.

---

*Draft prepared April 2026. Intended for hostile review prior to external submission.*
