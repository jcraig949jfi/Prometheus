# Harmonia: A Data-Driven Coordinate System for Cross-Domain Mathematical Structure

**James Craig**
JFI Research
April 2026

---

## Abstract

We present Harmonia, a system that discovers and validates cross-domain structure in mathematical objects using tensor train decomposition over heterogeneous datasets. Working with 509,182 objects across 20 mathematical domains — including elliptic curves, modular forms, number fields, genus-2 curves, lattices, knot invariants, and materials — we identify a shared coordinate system with two primary axes: **Megethos** (a universal magnitude/complexity axis) and **Arithmos** (an arithmetic group structure axis measuring torsion, class number, and Selmer rank). After subjecting these axes to systematic adversarial controls — including rank-normalization, monotonic scrambling, equal-complexity slicing, and five targeted attack families — we establish that: (1) Megethos survives all controls and *strengthens* under rank-normalization (17.6% to 38.2% variance); (2) Arithmos persists as a 1.57x signal above random null after removing Megethos; (3) the two axes are near-independent (rho = 0.104); and (4) the coordinate system enables cross-domain prediction of arithmetic invariants at rho = 0.76-0.95, generalizing out-of-distribution at 114-203% retention. The transfer is directional (rich to simple, 2.36x asymmetry), rotationally symmetric in the Megethos-Arithmos plane (gauge freedom, sigma = 0.0), and purely Arithmos-driven (Z2 alone at rho = 0.61 outperforms the full 5D space at rho = 0.51). Independent verification using a 41-dimensional dissection tensor (182 features, 601K objects) confirms: Mantel r = 0.94 distance preservation, positive Ollivier-Ricci curvature in both spaces, and transfer rho = 0.95 through shared magnitude dimensions. The manifold has Euler characteristic chi = -30,687 — locally spherical but globally hyperbolic, with curvature that *facilitates* rather than obstructs transfer.

---

## 1. Introduction

Mathematical objects from different domains — elliptic curves, modular forms, number fields, knots, lattices — are typically studied independently, with cross-domain connections established through deep theorems (modularity, Langlands correspondence, BSD conjecture). We ask a computational question: *can a data-driven system discover cross-domain structure directly from invariant data, without prior knowledge of these theorems?*

We construct such a system using tensor train (TT) decomposition [1], which represents high-dimensional tensors as chains of small cores connected by bond dimensions. Each mathematical domain becomes one dimension of the tensor. The bond dimension between adjacent domains measures the strength of their coupling. TT-Cross (adaptive cross approximation) builds the tensor train by sampling a coupling function — never materializing the full tensor.

Our main contributions are:

1. A coordinate system with two verified independent axes (Megethos, Arithmos) that survives systematic adversarial controls.
2. Cross-domain prediction of arithmetic invariants (rho = 0.76-0.95) that generalizes out-of-distribution.
3. Identification of the latent object as 2-dimensional for transfer, with different domains as directional projections.
4. Independent verification from a second representation (41D dissection tensor), confirming 94% distance preservation and consistent positive curvature.
5. Characterization of the manifold geometry: Euler characteristic chi = -30,687, positive Ollivier-Ricci curvature that facilitates (not obstructs) transfer.
6. An autonomous adversarial ecosystem that continuously tests the system's claims.

---

## 2. Data and Domains

### 2.1 Datasets

We use 20 mathematical domains totaling 509,182 objects. The primary domains are:

| Domain | Objects | Features | Key Invariants |
|--------|---------|----------|---------------|
| Elliptic curves | 31,073 | 4 | Conductor, rank, analytic rank, torsion |
| Modular forms | 50,000 | 5 | Level, weight, dimension, character |
| Number fields | 9,116 | 6 | Degree, discriminant, class number, regulator |
| Genus-2 curves | 66,158 | 7 | Conductor, Selmer rank, solvability, root number |
| Lattices | 39,293 | 6 | Dimension, determinant, level, class number |
| EC with zeros | 31,073 | 16 | Above + zero locations, spacings, GUE statistics |
| Dirichlet zeros | 50,000 | 5 | Conductor, degree, rank, n zeros, motivic weight |
| Maass forms | 14,995 | 25 | Level, spectral parameter, 20 coefficients |
| Materials | 10,000 | 6 | Band gap, formation energy, space group, density |
| Knots | 12,965 | 28 | Crossing number, determinant, polynomial coefficients |

Additional domains include space groups (230), polytopes (980), Fungrim formulas (3,130), OEIS sequences (50,000), abstract groups (50,000), Bianchi forms (50,000), Belyi maps (1,111), Charon embedding landscape (50,000), and two meta-domains: falsification battery results (97) and equation dissection strategies (34).

### 2.2 Phoneme Projection

Each domain's features are projected into a shared 5-dimensional "phoneme" space via explicit, interpretable mappings:

- **Megethos** (complexity): log N where N is conductor, discriminant, etc.
- **Bathos** (depth): rank, degree, dimension
- **Symmetria** (symmetry): point group order, automorphism order
- **Arithmos** (arithmetic): torsion, class number, Selmer rank
- **Phasma** (spectral): spectral parameter, zero spacings

### 2.3 Independent Representation: Dissection Tensor

A second, independently constructed representation uses 182-dimensional equation dissection signatures (modular arithmetic projections, spectral decompositions, p-adic evaluations, operadic structure, etc.) computed over 601,033 objects across 19 domains. After filtering to 41 high-fill dimensions, this tensor provides an independent "camera" on the same mathematical objects, enabling cross-validation of geometric claims.

---

## 3. Methods

### 3.1 Tensor Train Decomposition

Given N domains with object counts n1, ..., nN, we define a coupling function f(i1, ..., iN) in [0,1] that measures statistical similarity between objects across domains. The TT-Cross algorithm [2] approximates this function as:

f(i1, ..., iN) ~ sum_{alpha} G1(i1, alpha1) G2(alpha1, i2, alpha2) ... GN(alpha_{N-1}, iN)

where the bond dimension rk = dim(alpha_k) measures coupling strength between domains k and k+1. We use the tntorch library [3] with epsilon = 10^-3 and r_max = 20.

### 3.2 Coupling Scorers

We developed four coupling functions of increasing sophistication:

1. **Cosine**: cosine similarity in random-projected shared space.
2. **Distributional**: cosine + M4/M2^2 kurtosis deviation.
3. **Alignment**: quantile-rank co-extremity with null-corrected interactions.
4. **Phoneme**: L2 distance in the 5D phoneme space.

### 3.3 Tensor-Speed Falsification Battery

We implement six falsification tests as tensor operations:

- **F1**: Permutation null (score variance + rank correlation under shuffling)
- **F1b**: Phoneme specificity (coupling without complexity axis)
- **F2**: Subset stability (rank consistency across 50% splits)
- **F3**: Effect size (Cohen's d between top/bottom quartiles)
- **F8**: Direction consistency (deviation magnitude from population mean)
- **F17**: Confound residual (rank survival after removing top-variance feature)

### 3.4 Calibration

We calibrate against 5 known mathematical truths (e.g., modularity theorem: MF level = EC conductor) and 3 known falsehoods (e.g., knot invariants vs. material band gaps). The phoneme scorer achieves 100% sensitivity (all truths detected) and 75% accuracy.

---

## 4. Results

### 4.1 Megethos: The Magnitude Axis

PCA on the combined phoneme vectors of 9 L-function domains reveals a first principal component with 0.995 loading on the complexity phoneme, explaining 44.2% of cross-domain variance.

**Observation (Megethos Equation).** For objects in arithmetic domains, M(x) = log N(x) = sum_p f_p(x) log p, where N(x) is the conductor and f_p(x) is the local exponent at prime p.

The zero density relationship N_zeros = 3.117 * M + 1.503 holds with R^2 = 0.976 across 10,000 elliptic curves, consistent with known explicit formulas at height T ~ 19.6.

#### Adversarial Controls for Megethos

| Control | PC1 Variance | Status |
|---------|-------------|--------|
| Original (baseline) | 17.6% | --- |
| Rank-normalized | **38.2%** | Survives (stronger) |
| Size feature removed | 19.5% | Survives |
| Size shuffled within domains | 17.2% | Unchanged |
| Random null | 3.7% | Null baseline |
| No zero-padding | 25.8% | Survives (stronger) |

Rank-normalization, which destroys scale information, *strengthens* PC1 from 17.6% to 38.2%. This rules out raw magnitude dominance and establishes that Megethos captures ordinal cross-domain structure that is more regular than the metric structure.

Monotonic scrambling (random power-law transforms) changes PC1 significantly (z = -2.28), establishing that the signal depends on *specific functional form*, not just ordering. Cross-domain Spearman correlation of Megethos quantile distributions is rho > 0.9999 for all 21 domain pairs tested.

### 4.2 Arithmos: The Irreducible Kernel

#### Equal-Complexity Slicing

After binning objects by Megethos decile and computing PCA on the non-Megethos phonemes within each bin, we find PC1 = 47.9% versus a random null of 30.4%, giving a signal ratio of 1.57x (z = 149). Structure beyond complexity is real but modest.

#### Identifying the Driver

Correlating the residual PC1 scores with raw invariants reveals the driver:

| Domain | Invariant | Spearman rho |
|--------|-----------|-------------|
| Elliptic curves | Torsion | -0.926 |
| Number fields | Class number | -0.853 |
| Number fields | Regulator | +0.814 |
| Genus-2 curves | Selmer rank | -0.815 |
| Modular forms | (none) | 0.000 |
| Dirichlet zeros | (none) | 0.000 |

The residual axis aligns with measures of finite arithmetic group structure (torsion, class number, Selmer rank) in arithmetic-geometric domains, and is *absent* in purely analytic domains (modular forms, Dirichlet zeros). The class number-regulator anti-correlation (h ~ -0.85, R ~ +0.81) is consistent with the analytic class number formula hR = (w sqrt(|d|)) / (2^r1 (2pi)^r2) * L(1, chi_d).

#### Independence

Megethos and Arithmos have Spearman rho = 0.104 combined across domains, confirming near-independence.

#### Representation Dependence

The Arithmos signal ratio is representation-dependent: 1.57x in the 5D phoneme space, 1.07x in the 41D dissection tensor with explicit Megethos regression. The *phenomenon* (structured residual after magnitude removal) is real in both spaces, but the specific ratio depends on the projection. This establishes that the Arithmos signal is a property of the data, not a universal constant; its magnitude reflects the degree to which a given feature space concentrates arithmetic structure.

### 4.3 Cross-Domain Transfer

#### Forward Transfer

Matching objects by nearest neighbor in phoneme space, we predict arithmetic invariants across domains:

| Transfer | Megethos-only | 5D Phoneme | 41D Tensor |
|----------|--------------|------------|------------|
| EC torsion -> NF class number | 0.12 | 0.76 | **0.95** |
| G2 Selmer -> NF class number | --- | **0.80** | --- |

Full phoneme matching gives 6.3x improvement over Megethos-only matching. The 41D dissection tensor achieves rho = 0.95 through 4 shared magnitude dimensions (all s13/discriminant-conductor features), confirming the translation layer is representation-robust.

#### Out-of-Distribution Generalization

Training on low-Megethos objects and testing on high-Megethos objects yields:

| Transfer | In-distribution rho | OOD rho | Retention |
|----------|-------------------|---------|-----------|
| EC -> NF | 0.44 | **0.90** | 203% |
| G2 -> NF | 0.74 | **0.84** | 114% |

Transfer performance *improves* out-of-distribution, consistent with asymptotic regularity of arithmetic invariants at large conductor.

#### Directionality

Transfer is asymmetric: EC -> NF (rho = 0.63) is 2.36x stronger than NF -> EC (rho = 0.30). This is consistent with EC being a richer projection of the latent object (more observable dimensions).

### 4.4 The Latent Object

#### Minimum Dimensionality

| Latent dims | 1 | 2 | 3 | 4 | 5 |
|-------------|---|---|---|---|---|
| Mean transfer rho | -0.02 | **0.50** | 0.45 | 0.45 | 0.39 |

The latent object is **exactly 2-dimensional** for cross-domain transfer. One dimension fails. Three or more dimensions do not improve.

#### Domain Projections

Each domain observes different coordinates of the latent object:

- EC sees Z1 (conductor) + Z2 (torsion -> Arithmos phoneme, R^2 = 1.0)
- NF sees Z1 (discriminant) + Z2 (class number, R^2 = 0.84) + Z5 (regulator, R^2 = 1.0)
- G2 sees Z1 (conductor) + Z3 (Selmer rank -> Bathos phoneme, R^2 = 1.0)
- MF sees Z1 only (level) — no independent arithmetic coordinate

Notably, Selmer rank projects onto Z3 (Bathos/depth), not Z2 (Arithmos). Torsion and Selmer rank live on *different latent axes*, explaining why G2 -> EC transfer fails (rho = -0.004).

### 4.5 Structural Properties

#### Gauge Freedom

The Megethos-Arithmos plane is rotationally symmetric: all rotations of the (Z1, Z2) plane yield identical transfer performance (sigma = 0.0 across 20 random rotations). This is a gauge symmetry — the coordinate choice within the plane is arbitrary; the geometry is what is real.

#### Degeneracy

Alternative invariants (rank/regulator instead of torsion/class number) achieve 85% of the transfer signal. The geometry works with multiple invariant choices, suggesting the structure is in the space, not in the specific coordinates.

#### Compression

Z2 alone (Arithmos phoneme) achieves rho = 0.61 — *better* than the full 5D phoneme space (rho = 0.51). Adding Megethos *degrades* cross-domain arithmetic prediction. The transfer signal is purely Arithmos-driven.

### 4.6 Geometry of the Manifold

#### Two-Camera Verification

The 5D phoneme projection and the 41D dissection tensor provide independent views of the same objects. The Mantel test on pairwise distance matrices yields r = 0.94 (z = 118, p = 0.001), confirming that 94% of the pairwise distance structure is preserved across representations.

The two cameras have *different dominant axes*: PC1 in the phoneme space is Megethos (magnitude, 44% variance), while PC1 in the dissection tensor aligns with Phasma (spectral content, rho = 0.80, 41% variance). Megethos is orthogonal to the tensor's PC1 (r = 0.017). The transition function between the two spaces is a rotation-plus-scaling that explains 71.6% of variance linearly, with a 7.3x singular value spread (anisotropic). The remaining 28.4% is nonlinear.

#### Curvature

We measure curvature using Ollivier-Ricci curvature (ORC) on k-nearest-neighbor graphs in both representations:

| Space | Mean ORC | Fraction positive | k |
|-------|----------|-------------------|---|
| 5D phonemes | 0.713 | 98.8% | 10 |
| 41D tensor | 0.596 | 99.7% | 10 |

Both representations show strongly positive Ollivier-Ricci curvature (> 98% of edges positive), confirming that the data occupies a genuinely positively-curved submanifold regardless of the ambient embedding.

#### Curvature and Transfer

Contrary to our initial prediction that curvature would *obstruct* transfer (via lossy parallel transport), local curvature and transfer performance are *positively* correlated (Spearman r = +0.271, p = 0.004, n = 110 pairs). Curved regions transfer *better*, not worse. This is consistent with positive curvature reflecting tight clustering of objects with shared arithmetic structure: denser neighborhoods enable more accurate nearest-neighbor prediction.

#### Topology

The Euler characteristic of the nearest-neighbor graph is chi = -30,687 (V = 5,000, E = 35,687, beta_0 = 5, beta_1 = 30,692). This is far from a sphere (chi = 2) or torus (chi = 0). The manifold is locally spherical (positive ORC everywhere) but globally hyperbolic, with approximately 30,000 independent cycles. We describe this informally as a "coral reef" topology: smooth at each point, enormously tangled in aggregate.

#### Geodesic Deviation

EC-to-NF geodesics on the nearest-neighbor graph deviate from straight-line paths by a factor of 0.91 (mean deviation relative to endpoint distance). This confirms substantial curvature in the primary translation channel.

### 4.7 Spectral Features and the Residual

Loading the full 31,073 elliptic curves with 16-dimensional spectral features (including GUE-sensitive statistics: normalized spacing variance, skewness, kurtosis, and nearest-neighbor spacing ratios at 6-8 digit precision), we test whether spectral data cracks the residual unexplained variance.

Within EC, spectral features add +5.9% R^2 for predicting torsion beyond Megethos (from R^2 = 0.000 to R^2 = 0.059). GUE statistics correlate with Arithmos at |rho| = 0.09-0.14 (significant at p < 0.001 but weak). The spectral phoneme sees arithmetic structure dimly — through a narrow window. The ~21% residual between the two camera representations remains unexplained by spectral summary statistics and likely resides in the nonlinear manifold topology (chi = -30,687) or in the raw zero locations themselves.

---

## 5. Discussion

### 5.1 Interpretation

Our results are consistent with the following interpretation: *arithmetic-geometric mathematical objects are lossy, directional projections of a shared latent structure, with Megethos and Arithmos as its primary coordinates.*

The evidence for this:

1. Projections are directional (rich -> simple stronger than reverse, 2.36x).
2. Projections preserve neighborhoods (cross-domain prediction at rho = 0.76-0.95).
3. Projections stabilize at scale (OOD improves to 203%).
4. Different domains see different subsets of the latent object.
5. The geometry has gauge freedom (rotationally symmetric in the M-A plane).
6. Two independent representations confirm the same geometry (Mantel r = 0.94).
7. The manifold is positively curved in both representations (ORC = 0.60-0.71).

The *coral reef* topology (chi = -30,687) and the finding that curvature *facilitates* transfer (positive correlation, r = +0.27) suggest that the manifold's structure is not an obstruction to cross-domain translation but rather a resource: dense, curved neighborhoods are precisely where shared arithmetic structure concentrates.

### 5.2 Relationship to Known Mathematics

The Megethos axis for L-function domains corresponds to the analytic conductor of Iwaniec and Sarnak [4]. The extension to knots, polytopes, and materials is empirical and not previously established.

The Arithmos axis captures the relationship between torsion, class number, and Selmer rank — invariants connected through BSD, the analytic class number formula, and descent theory. Our contribution is showing these collapse onto a single latent axis that enables cross-domain prediction.

The class number-regulator anti-correlation is a statistical manifestation of the analytic class number formula hR = (w sqrt(|d|)) / (2^r1 (2pi)^r2) * L(1, chi_d), which constrains h and R to trade off at fixed discriminant.

The finding that modular forms and Dirichlet zeros have *zero* Arithmos residual — their cross-domain structure is entirely Megethos — is consistent with these being purely analytic objects whose arithmetic content is encoded *within* the L-function rather than as an independent invariant.

### 5.3 Negative Results

1. **Physics-math bridge:** Particle masses and EC conductors do not share genuine geometric structure (6/8 adversarial kills). The apparent 3.7 degree Grassmannian angle is an artifact of sparse, high-dimensional data (225 particles in 13/182 active dimensions). Math-to-physics bridges require native spectral/automorphic signatures, not proxied formula features.

2. **Alpha is not universal:** The Arithmos signal ratio depends on the representation (1.57x in 5D phonemes, 1.07x in 41D tensor). The phenomenon is real; the specific number is not an invariant.

3. **Spectral features do not crack the residual:** High-precision L-function zero statistics (6-8 digit) add only +5.9% R^2 within EC. Summary statistics of zero distributions see arithmetic structure weakly (|rho| < 0.14). The full zero vectors (not summary statistics) may carry more information.

4. **The curvature prediction was wrong:** We predicted curvature would obstruct transfer; it facilitates it (r = +0.27). The parallel transport model is incorrect; nearest-neighbor clustering in curved regions is the mechanism.

### 5.4 Limitations

1. The 1.57x signal-to-null ratio for Arithmos, while statistically significant (z = 149), is modest. The secondary structure is real but not dominant.
2. Calibration specificity is 33% (1/3 known falsehoods rejected). The system is more permissive than desired.
3. The phoneme projection is hand-designed, not learned. Different projection choices yield different signal ratios, though the gauge freedom result suggests the underlying geometry is robust.
4. All results are on LMFDB and related datasets. Generalization to other mathematical databases is untested.
5. The Euler characteristic is computed from a k-NN graph, which is a combinatorial approximation of the underlying smooth manifold. The true topology may differ.

### 5.5 The Adversarial Ecosystem

To continuously stress-test these claims, we built an autonomous adversarial system with four components: a Generator that invents attacks from 5 families (data, representation, structural, cross-domain, metric) with 20+ mutation operators; an Executor that runs the full measurement battery; a Judge that scores damage to core invariants; and an Archivist that logs and prioritizes the most damaging attacks. This system runs at 1.7 attacks/second and produces a daily report of what almost broke.

---

## 6. Conclusion

We have identified a two-dimensional coordinate system — Megethos (magnitude) and Arithmos (arithmetic group structure) — that provides a shared language for arithmetic-geometric mathematical objects across domains. The system enables cross-domain prediction at rho = 0.76-0.95, generalizes out-of-distribution, and survives systematic adversarial testing in two independent representations.

The strongest defensible claim is: *there exists a stable, low-dimensional coordinate system over arithmetic-geometric objects in which known invariants align and become mutually predictive across domains. The coordinate system is confirmed by two independent representations (94% distance preservation), sits on a positively-curved manifold with coral-reef topology, and enables directional transfer where curvature facilitates rather than obstructs prediction.*

Whether this coordinate system is canonical, or merely one chart among many, remains open. The gauge freedom in the Megethos-Arithmos plane and the representation dependence of the signal ratio suggest that while the *geometry* is intrinsic, the *coordinates* are not. Different mathematical "cameras" — invariant-level and formula-level — see the same manifold from different angles, with different dominant axes but the same pairwise distances and the same curvature sign. The manifold is what is real.

---

## References

[1] I. V. Oseledets, "Tensor-train decomposition," *SIAM J. Sci. Comput.*, 33(5):2295-2317, 2011.

[2] I. V. Oseledets and E. E. Tyrtyshnikov, "TT-cross approximation for multidimensional arrays," *Linear Algebra Appl.*, 432(1):70-88, 2010.

[3] R. Ballester-Ripoll, Y. Lindstrom, and R. Pajarola, "tntorch: Tensor network learning with PyTorch," *J. Mach. Learn. Res.*, 23(208):1-6, 2022.

[4] H. Iwaniec and P. Sarnak, "Perspectives on the analytic theory of L-functions," *Geom. Funct. Anal.*, Special Volume, Part II:705-741, 2000.

[5] The LMFDB Collaboration, "The L-functions and modular forms database," https://www.lmfdb.org, 2024.

[6] C. Livingston and A. H. Moore, "KnotInfo: Table of knot invariants," https://www.indiana.edu/~knotinfo, 2024.

[7] A. Jain et al., "The Materials Project: A materials genome approach to accelerating materials innovation," *APL Materials*, 1(1):011002, 2013.

[8] N. J. A. Sloane, "The On-Line Encyclopedia of Integer Sequences," https://oeis.org, 2024.

[9] T. Dokchitser and V. Dokchitser, "On the Birch-Swinnerton-Dyer quotients modulo squares," *Ann. of Math.*, 172(1):567-596, 2010.
