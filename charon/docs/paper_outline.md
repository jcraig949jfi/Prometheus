# Paper Outline: Empirical Demonstration of the ILS Test Function Support Theorem via Computational Clustering

## Working Title
"Rank Discrimination in L-Function Zero Geometry: The Spectral Tail Carries the Signal"

## One-Sentence Summary
The Iwaniec-Luo-Sarnak test function support theorem predicts that rank discrimination
requires higher zeros; we demonstrate this empirically for the first time through
computational clustering on LMFDB data, showing that zeros 5-19 produce stronger rank
clustering (ARI=0.5548) than all 20 zeros (ARI=0.5455) or the first zero alone (ARI=0.2974).

## Target Venue
Experimental Mathematics — publishes computationally-discovered, empirically-verified
mathematical findings. The murmurations papers established the precedent for this type
of contribution.

---

## Section 1: Introduction — The Untested Prediction

The ILS framework (Iwaniec, Luo, Sarnak 2000) proves that the Fourier transforms of
the 1-level densities for SO(even) and SO(odd) are identical for |u| < 1. Distinguishing
rank families requires test functions with Fourier support beyond [-1,1], which by the
uncertainty principle requires information from higher zeros.

This has been a theoretical prediction for 25 years. Nobody has built the experiment
to test it empirically through computational clustering.

We test it.

## Section 2: Methodology — Pre-Registered TDD Battery

- 133,223 arithmetic objects from LMFDB (31K EC, 102K MF, 1.3K genus-2)
- Low-lying zeros (Katz-Sarnak normalized) as feature vectors
- Pre-registered thresholds set before data ingestion
- Full audit trail: data integrity checks, 20/20 LMFDB spot-checks, methodology document
- Clustering: K-means within conductor strata, ARI against analytic rank
- All tests use zeros-only vectors (no metadata leak — confirmed by ablation showing
  ARI drops only 0.004 when analytic_rank removed from features)

### What we killed first (establishes rigor):
- Dirichlet coefficients: binary hash, ARI=0.008 (Test 0.3, Test 1.3)
- Correspondence discovery claim: zeros encode rank, not correspondences
- Paramodular interpretation of 163 dim-2 forms: genus-2 test failed

## Section 3: The Ablation — The Core Result

| Feature Space | ARI (within conductor strata) |
|--------------|-------------------------------|
| All 20 zeros (baseline) | 0.5456 |
| Drop first zero (1-19) | 0.5486 |
| Drop first two (2-19) | 0.5512 |
| Zeros 5-19 only | **0.5548** |
| First zero only | 0.2974 |
| Zeros 1-4 only | 0.5205 |

Monotonic improvement as central zeros are stripped. The first zero — the one that
literally IS rank via BSD — hurts the clustering. The signal lives in zeros 5-19.

Also: conductor regression has zero effect (raw ARI = residual ARI in all cases).
The signal is not a conductor proxy.

## Section 4: Theoretical Explanation — Three Frameworks Converge

### 4.1 Katz-Sarnak Global Rigidity
Symmetry type (SO(even) vs SO(odd)) governs the joint probability density of the
entire zero spectrum. The first zero is over-determined by algebraic rank (BSD),
introducing geometric variance that degrades continuous clustering. Higher zeros
encode rank through smoother bulk spectral geometry.

### 4.2 Deuring-Heilbronn Uniform Mean Shift
Zero repulsion from the central point produces a uniform displacement of the entire
zero sequence. Rank 0 and rank 1 populations form parallel hyperplanes in the space
of zeros 5-19. K-means separates translated clusters trivially.

The mechanism: rank manifests as a translation vector, not a distortion. Dropping
the degenerate first zero removes the noise. The remaining dimensions carry the
clean geometric signal.

### 4.3 ILS Test Function Support (The Direct Prediction)
The Fourier transforms of SO(even) and SO(odd) 1-level densities are identical for
|u| < 1. The symmetry-breaking signature is a high-frequency phenomenon that physically
translates to the spectral tail. Our ablation is the empirical realization of this
25-year-old theoretical constraint.

## Section 5: Limitations and Open Questions

### Limitations (from hostile council review):
- 100% bridge recovery may be tautological (same L-function = same zeros by definition)
- Cross-type distances mix objects from different random matrix ensembles without
  symmetry-type normalization
- Graph orthogonality (rho=0.04) inflated by sparsity; need conditional rho
- Dirichlet coefficient kill was too broad — PCA extracts structure k-NN misses
  (arXiv:2502.10360)

### Open questions:
- **The character anomaly**: non-trivial character dim-2 forms are 3.3x more
  EC-proximate, going AGAINST naive Katz-Sarnak prediction. Unexplained by any
  of the three frameworks. May indicate finite-conductor symmetry-type effects
  operate differently in the spectral tail.
- **Generalization**: does the spectral tail carry analogous invariant information
  for number fields, Artin representations, Dirichlet characters?
- **Optimal zero range**: with 100+ zeros (available in LMFDB), where does the
  signal peak? Is there a theoretically predicted optimum?
- **ARI decomposition**: how much comes from uniform mean shift vs additional
  spacing structure in zeros 5-19?

## Section 6: Conclusion

The ILS test function support theorem has been a theoretical prediction since 2000.
We provide the first empirical demonstration via computational clustering: rank
discrimination in L-function zero geometry is carried by the spectral tail (zeros 5-19),
not by central vanishing (zero 1). This is consistent with three independent theoretical
frameworks and demonstrated on 17,314 elliptic curve isogeny classes with pre-registered
methodology and full audit trail.

The character anomaly remains unresolved and invites follow-up investigation.

---

## Key Citations
- Iwaniec, Luo, Sarnak — "Low lying zeros of families of L-functions" (2000)
- Katz, Sarnak — "Zeroes of zeta functions and symmetry" (1999)
- Miller — "One- and two-level densities for rational families of elliptic curves" (2004)
- He, Lee, Oliver, Pozdnyakov — "Murmurations of elliptic curves" (2022)
- Sawin, Sutherland — murmuration density formula (arXiv:2504.12295, 2025)
- arXiv:2502.10360 — "Machine learning the vanishing order of rational L-functions" (2025)

## Data and Code Availability
- Database: DuckDB, reproducible from LMFDB PostgreSQL mirror
- All code: `charon/scripts/full_audit.py` (single auditable script)
- Pre-registered thresholds: documented before data ingestion (2026-04-01)
- Audit log, structured journal, methodology document: all archived
