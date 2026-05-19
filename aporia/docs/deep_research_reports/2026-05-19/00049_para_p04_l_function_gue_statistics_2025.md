# PARA-P04: L-function GUE statistics 2025

**Pythia queue id:** 49
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDMEFNYXZubkVMNmFfdU1QMGUtNm9BWRIXQzBBTWF2bm5FTDZhX3VNUDBlLTZvQVk
**Elapsed:** 252s
**Completed at:** 2026-05-19T10:52:56.065982+00:00

---

# Random-Matrix-Theory Advances on L-function Zero Statistics (2024-2026): A Comprehensive Analysis

**Key Points:**
- **Random Matrix Theory (RMT) Universality:** Research suggests that, asymptotically, the local statistics of the non-trivial zeros of \( L \)-functions (such as the \( n \)-level correlation and \( n \)-level density) universally match the eigenvalue statistics of large random matrices from classical compact groups (Gaussian Unitary Ensemble, Orthogonal, and Symplectic ensembles) [cite: 1, 2].
- **Finite-N Corrections and Lower Order Terms:** To accurately model the statistics of \( L \)-functions at finite conductors, the infinite-\( N \) scaling limits of RMT are insufficient. Recent advances heavily utilize the \( L \)-functions Ratios Conjecture and the Bogomolny-Keating formula to derive lower-order terms that isolate family-dependent arithmetic factors [cite: 3, 4]. 
- **Empirical Deviations and Repulsion:** Extensive empirical observations (2024-2026) confirm deviations from asymptotic RMT predictions at finite heights and conductors. Notably, low-lying zeros in certain families of elliptic curves and modular forms exhibit a pronounced repulsion from the central point [cite: 5]. The Kohnen-Zagier theorem partially explains this via the discretization of central values, though its efficacy for higher-weight forms remains debated [cite: 5, 6]. Furthermore, novel phenomena such as "ditch avoidance" and zero rigidity have been theorized to explain spatial gaps in the distribution of zeros [cite: 7].
- **Weighted Densities:** Tilted averages—where zero statistics are weighted by central \( L \)-values—are an active area of investigation in 2024-2025, revealing shifts in symmetry types and confirming refined density conjectures for Dirichlet and Hilbert modular forms [cite: 8, 9].

The distribution of the zeros of the Riemann zeta function and generalized \( L \)-functions remains one of the most profound subjects in modern analytic number theory. Over the past five decades, the conceptual bridge between these number-theoretic zeros and the eigenvalues of random matrices has transformed the field, offering a robust heuristic and predictive framework. By modeling \( L \)-functions through the lens of Random Matrix Theory (RMT), mathematicians have generated highly accurate conjectures regarding the moments, correlations, and densities of zeros. During the 2024–2026 period, this research has advanced rapidly, moving beyond the validation of the asymptotic main terms (the infinite-\( N \) limits) to rigorously mapping out the finite-\( N \) corrections, the precise lower-order terms, and the empirical deviations that distinguish specific families of \( L \)-functions. 

This comprehensive report synthesizes the latest advances in RMT applications to \( L \)-function zero statistics, drawing significantly on recent arXiv preprints, published literature, and conference proceedings from 2024 to 2026. It will systematically cover the proven cases of the Gaussian Unitary Ensemble (GUE) predictions, the derivation and implications of finite-\( N \) corrections, the specific deviations observed empirically (including the repulsion of zeros from the central point and the phenomena of "ditch avoidance"), and the emerging study of weighted densities.

## 1. Introduction: L-functions and the Random Matrix Theory Framework

### 1.1 The Riemann Zeta Function and Generalized L-functions

An \( L \)-function is a meromorphic function on the complex plane that encodes profound arithmetic and geometric information. The prototypical example is the Riemann zeta function, defined for \( \text{Re}(s) > 1 \) by the Dirichlet series:
\[ \zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ prime}} \left( 1 - \frac{1}{p^s} \right)^{-1} \]
This Euler product establishes the fundamental link between the continuous analytic properties of the function and the discrete distribution of the prime numbers [cite: 10, 11]. The function admits an analytic continuation to the entire complex plane (with a simple pole at \( s=1 \)) and satisfies a functional equation relating its values at \( s \) and \( 1-s \). 

The Great Riemann Hypothesis (and its generalizations) posits that all non-trivial zeros of such \( L \)-functions lie precisely on the critical line \( \text{Re}(s) = 1/2 \) [cite: 11, 12]. Generalized \( L \)-functions—such as Dirichlet \( L \)-functions, automorphic \( L \)-functions, and those associated with elliptic curves or modular forms—share these core properties: an Euler product, analytic continuation, and a functional equation [cite: 13]. The non-trivial zeros of these functions dictate the error terms in prime number theorems and govern properties like the ranks of elliptic curves, as articulated by the Birch and Swinnerton-Dyer conjecture [cite: 2, 14].

### 1.2 The Montgomery-Odlyzko Law and the GUE Hypothesis

The modern era of \( L \)-function zero statistics was inaugurated by Hugh Montgomery in 1973. Montgomery investigated the pair correlation of the non-trivial zeros of the Riemann zeta function high up on the critical line [cite: 1, 15]. He found that, for restricted test functions, the Fourier transform of the pair correlation function of the normalized zeros matched the pair correlation of the eigenvalues of random Hermitian matrices from the Gaussian Unitary Ensemble (GUE) [cite: 16, 17].

Specifically, if the zeros are denoted as \( 1/2 + i\gamma_j \), they are normalized so that the average local spacing is exactly 1. Montgomery demonstrated that the probability density of finding a second zero near a given zero at a normalized distance \( x \) is asymptotically:
\[ 1 - \left( \frac{\sin(\pi x)}{\pi x} \right)^2 \]
This expression features a phenomenon known as "eigenvalue repulsion"; the probability of two zeros being arbitrarily close to each other drops to zero, starkly contrasting with the behavior of independent random variables (which would follow a Poisson distribution) [cite: 16]. 

Following Montgomery's theoretical breakthrough, Andrew Odlyzko conducted massive numerical computations of the zeros of the zeta function (initially up to the \( 10^5 \)-th zero, and later around the \( 10^{20} \)-th zero) [cite: 18, 19]. Odlyzko's numerical data exhibited a spectacular agreement with the GUE predictions, not just for the pair correlation, but for the nearest-neighbor spacing distributions as well [cite: 3, 20]. This correspondence between the local statistics of zeta zeros and the eigenvalues of random complex Hermitian matrices came to be known as the Montgomery-Odlyzko law [cite: 10].

### 1.3 The Katz-Sarnak Density Conjecture

While the GUE model accurately describes the statistics of zeros high up on the critical line for an individual \( L \)-function, a different paradigm is required to understand the low-lying zeros—the zeros located strictly near the central point \( s = 1/2 \). These low-lying zeros are of paramount arithmetic importance; for instance, the order of vanishing at the central point determines the algebraic rank of an elliptic curve [cite: 14, 21].

Because an individual \( L \)-function possesses only a few zeros very close to the central point, it is mathematically impossible to construct a meaningful statistical distribution from a single function in this regime. Instead, one must average over a "family" of \( L \)-functions [cite: 12]. In the late 1990s, Nicholas Katz and Peter Sarnak studied families of zeta functions over finite fields (the function field analogue). Utilizing Deligne's equidistribution theorem, they proved that as the conductor (or polynomial degree) and the finite field size tend to infinity, the zero statistics exactly match the eigenvalue statistics near 1 of large random matrices from specific classical compact groups [cite: 15, 20].

This led to the Katz-Sarnak Density Conjecture for number fields: For any natural family of \( L \)-functions, the distribution of the normalized low-lying zeros, as the analytic conductors tend to infinity, converges to the scaling limit of the eigenvalues near 1 of a corresponding matrix ensemble [cite: 12, 22]. Depending on the arithmetic properties of the family (such as the signs of the functional equations), the appropriate random matrix ensemble—or "symmetry type"—is typically one of the following:
- **Unitary (U):** Associated with the Gaussian Unitary Ensemble (GUE).
- **Symplectic (Sp):** Associated with the Gaussian Symplectic Ensemble (GSE).
- **Orthogonal (O):** Including the Special Orthogonal groups of even dimension \( \text{SO(even)} \) and odd dimension \( \text{SO(odd)} \).

The primary statistic used to measure this behavior is the \( 1 \)-level density (or more generally, the \( n \)-level density). For a test function \( \phi \) (usually an even Schwartz function whose Fourier transform has compact support), the \( 1 \)-level density for an \( L \)-function \( f \) is defined by summing \( \phi \) over the normalized zeros [cite: 9, 19]. The Katz-Sarnak conjecture asserts that the average of this density over the family matches the integral of \( \phi \) against the theoretical density function \( W_G(x) \) derived from the respective random matrix group [cite: 8, 9].

### 1.4 Random Matrix Ensembles: Unitary, Orthogonal, and Symplectic

To comprehend the deviations and finite-\( N \) corrections studied in recent years, one must understand the continuous limits of these matrix groups. 
In Random Matrix Theory, the \( n \)-point correlation functions of the eigenvalues of unitary matrices endowed with the Haar measure can be expressed cleanly as determinants of a sine-kernel [cite: 14, 23]. The eigenvalue repulsion differs slightly among the ensembles. For instance, the density functions \( W_G(x) \) for the 1-level density in the Katz-Sarnak limits are [cite: 24]:
- Unitary: \( W_U(x) = 1 \)
- Symplectic: \( W_{Sp}(x) = 1 - \frac{\sin(2\pi x)}{2\pi x} \)
- Orthogonal (SO(even)): \( W_{SO(\text{even})}(x) = 1 + \frac{\sin(2\pi x)}{2\pi x} \)
- Orthogonal (SO(odd)): \( W_{SO(\text{odd})}(x) = \delta_0(x) + 1 - \frac{\sin(2\pi x)}{2\pi x} \)

The Katz-Sarnak philosophy dictates that identifying the symmetry type of a family allows one to harness the vast machinery of RMT to predict complex arithmetic properties, such as the frequency of non-vanishing at the central point [cite: 8, 25]. 

## 2. Proven Cases of GUE Prediction and Asymptotic Universality

The literature spanning 2024 to 2026 reinforces the robustness of the asymptotic RMT predictions. When the analytic conductors of the \( L \)-functions in a family approach infinity (the infinite-\( N \) limit in RMT parlance), the main terms of the zero statistics converge flawlessly to the predicted universal forms.

### 2.1 The n-Level Correlation of Zeros

While Katz and Sarnak popularized the study of low-lying zeros, the \( n \)-level correlation pertains to zeros high up on the critical line. Rudnick and Sarnak (1996) achieved a monumental result by proving that the \( n \)-level correlation of the zeros of any principal automorphic \( L \)-function (attached to a cuspidal automorphic representation of \( \text{GL}_m \) over \( \mathbb{Q} \)) agrees with the GUE predictions, provided the test functions have suitably restricted support [cite: 20, 21]. 

Recent literature highlights that the \( n \)-level correlation statistic is highly universal [cite: 17]. Regardless of whether the \( L \)-function stems from a Dirichlet character, an elliptic curve, or a higher-weight modular form, the high zeros always align with the GUE [cite: 1, 20]. This universality emerges because the correlations are dominated by the first two moments of the Satake parameters; the higher moments, which encapsulate the unique arithmetic of the specific \( L \)-functions, vanish in the limit as one averages over infinitely many zeros high on the critical line [cite: 12, 26].

### 2.2 Central Moments and Higher-Level Statistics

In 2026, researchers including Miller et al. significantly extended the analysis of the \( n \)-th centered moments of the \( 1 \)-level density. By delving into the combinatorial intricacies of the explicit formulas, they generalized results from the distributions of zeros to arbitrary test functions. The Katz-Sarnak predictions were validated to hold strictly in the main terms [cite: 1, 12]. 

A central observation is that while the \( n \)-level correlation exhibits universal GUE behavior for individual \( L \)-functions, the \( n \)-level density for families breaks this universality, stratifying families by their respective symmetry groups (Orthogonal, Symplectic, etc.) [cite: 9, 17]. By analyzing the moments of these densities, researchers have achieved better bounds on the order of vanishing at the central point. For instance, Li and Miller (2024) used improved formulas for the \( n \)-level densities to obtain record-setting bounds on the order of vanishing for cuspidal newforms [cite: 12]. They proved that as the level tends to infinity, there exists at least one form in the family whose normalized lowest zero is situated within a remarkably small fraction (1/4) of the average spacing from the central point [cite: 19].

### 2.3 Spinor and Standard L-functions of Modular Forms

Another significant proven case of RMT prediction was detailed in a 2024 preprint by Zhao (arXiv:2403.19687). Zhao meticulously studied the low-lying zeros of the Spinor \( L \)-functions and the Standard \( L \)-functions associated with Siegel modular forms [cite: 20, 27]. By employing the Petersson trace formula and explicitly calculating the contributions of the Fourier coefficients, Zhao demonstrated that the \( 1 \)-level density of these families accurately aligns with the predictions of their respective symmetry groups. Such investigations expand the domain of the Katz-Sarnak conjecture from classical \( \text{GL}_2 \) forms to higher-degree automorphic representations, verifying that the RMT scaling limits remain valid for highly complex algebraic objects [cite: 20].

Similarly, in a 2025 study (arXiv:2508.18469), Zhao analyzed the one-level density of low-lying zeros of standard \( L \)-functions attached to Hilbert modular forms [cite: 9]. Here, the unweighted family exhibits an Orthogonal symmetry type. The findings confirmed that the resulting distributions perfectly match the RMT predictions, further solidifying the Katz-Sarnak Density Conjecture across diverse number fields [cite: 9].

## 3. Finite-N Corrections and Lower Order Terms

While the asymptotic agreement between RMT and \( L \)-functions is elegant, it represents only the first term in an asymptotic expansion. In practical numerical computations and real-world arithmetic scenarios, conductors are strictly finite. At finite conductors, empirical data consistently diverges from the pure infinite-\( N \) scaling limits [cite: 4, 28]. To bridge this gap, modern RMT research in number theory focuses on "lower order terms"—the finite-\( N \) corrections that account for the sub-leading deviations.

### 3.1 Limitations of the Main Term and the Infinite-N Limit

The problem with relying solely on the infinite-\( N \) RMT predictions is that the convergence is frustratingly slow. The rate of convergence to the asymptotic limit is generally logarithmic with respect to the conductor (e.g., \( O(1/\log X) \)) [cite: 15, 29]. Consequently, even for astronomically large numerical values, the infinite-\( N \) limit does not perfectly mirror the data. The random matrix theory frequently "cannot see the arithmetic of the family" in the main term, because the distinctive arithmetic factors vanish as \( N \to \infty \) [cite: 26].

To detect the arithmetic signature of a specific family (such as whether a family of elliptic curves has complex multiplication or a forced torsion point), one must scrutinize the lower order terms [cite: 22].

### 3.2 The Bogomolny-Keating Formula

The necessity of lower order terms was first recognized in the context of the Riemann zeta function. In the late 1990s, Bogomolny and Keating introduced a semi-classical trace formula from quantum chaos to model the Riemann zeros. Their framework proposed an explicit formula that incorporated finite-\( T \) corrections (where \( T \) is the height on the critical line) to the GUE pair correlation [cite: 4, 30]. 

The Bogomolny-Keating formula elegantly merges the continuous random matrix components with a discrete Euler product over the primes. The resulting expression accurately captures the fine oscillatory features observed in Odlyzko's finite-\( T \) numerical data [cite: 4]. In particular, their formula accounts for the "deviations from the GUE law" induced by the shortest periodic orbits in the corresponding quantum chaotic system, which map directly to the smallest prime numbers [cite: 4, 10].

### 3.3 The L-functions Ratios Conjecture

A major theoretical leap occurred with the formulation of the \( L \)-functions Ratios Conjecture by Conrey, Farmer, and Zirnbauer [cite: 4, 31]. Building upon ideas from the Bogomolny-Keating work and random matrix heuristics, the Ratios Conjecture provides a powerful "recipe" for calculating the average of ratios of \( L \)-functions over a family. 

By differentiating these ratios, researchers can explicitly derive the \( n \)-level densities and correlation functions, complete with all lower order terms [cite: 3, 14]. The Conrey-Snaith implementation of this conjecture (2007-2008) revolutionized the field. It allowed for the mechanical extraction of finite-\( N \) corrections for the zeros of any natural family of \( L \)-functions [cite: 3, 4]. 

Recent literature (2024-2026) heavily utilizes the Ratios Conjecture. For example, Mason and Snaith applied this methodology to families with Symplectic and Orthogonal symmetries. They demonstrated that the lower order terms derived from the Ratios Conjecture take the exact mathematical form required to match rigorous number-theoretic results (obtained via the explicit formula) for restricted test functions [cite: 14]. 

In 2024, Conrey and Snaith (arXiv:2412.11662) revisited the \( n \)-correlation of eigenvalues of random unitary matrices, framing the RMT calculations as averages of ratios of characteristic polynomials to perfectly mimic the number-theoretical methods. This allowed them to extend the support of the test functions for the \( n \)-correlation to \( (-6,6) \), an impressive analytical feat [cite: 23].

### 3.4 Explicit Formulas and Arithmetic Dependencies

When analyzing lower order terms rigorously, mathematicians utilize Riemann's explicit formula, which connects sums over the zeros of an \( L \)-function to sums over the prime numbers (via the von Mangoldt function and the Fourier coefficients of the form) [cite: 10, 15]. 

Miller and his collaborators derived alternate forms of the explicit formula for \( \text{GL}(2) \) families to highlight how lower order terms depend on the arithmetic of the family. Instead of expressing the prime sums in terms of Satake parameters, they expressed them via the moments of the Fourier coefficients \( \lambda_f(p) \) [cite: 22]. Because the distribution of these Fourier coefficients follows different laws depending on the family (e.g., the Sato-Tate distribution holds for non-CM elliptic curves, but fails for CM curves), the lower order terms explicitly inherit these differences [cite: 22, 26].

These family-dependent lower order corrections have wide-ranging applications. They effectively model the behavior of zeros near the central point for small conductors and provide a theoretical explanation for phenomena such as "excess rank" in families of elliptic curves (where the empirically observed number of curves with high rank far exceeds the asymptotic prediction) [cite: 18, 22].

### 3.5 Phase Transitions in Extended Support

A critical technical frontier in the study of lower order terms is extending the support of the test function's Fourier transform. In a pivotal study on quadratic Dirichlet \( L \)-functions, Södergren (and later elaborated on in recent literature) expanded the support of the Fourier transform of the test function \( \phi \) to \( (-2, 2) \) [cite: 15]. 

Under the Generalized Riemann Hypothesis (GRH), they derived an asymptotic expansion in descending powers of \( \log X \). Notably, they uncovered a phase transition when the supremum of the support of \( \hat{\phi} \) reaches 1 [cite: 15]. At this boundary, a novel lower order term abruptly appears. This term involves the quantity \( \hat{\phi}(1) \) and introduces a new layer of complexity to the density functions [cite: 15]. 

This phenomenon illustrates that as the test function captures longer-range interactions among the prime numbers (corresponding to broader support in the Fourier domain), the finite-\( N \) corrections exhibit abrupt, non-analytic shifts. Such phase transitions in the lower order terms are hypothesized to be a universal feature across multiple families, providing a rigorous window into the discrete arithmetic structure that underpins the continuous RMT limits [cite: 15].

## 4. Deviations Observed Empirically: Repulsion, Discretization, and Families

The period spanning 2024-2026 has witnessed an explosion of empirical investigations into the fine-grained distribution of zeros. With massive computational resources and optimized algorithms, researchers have generated high-precision data on the zeros of twists of modular forms, elliptic curves, and Dirichlet \( L \)-functions. These experiments consistently reveal deviations from the pure continuous RMT models, shedding light on the underlying discrete arithmetic.

### 4.1 Repulsion of Zeros from the Central Point

One of the most striking empirical observations is the significant repulsion of the low-lying zeros from the central point \( s=1/2 \) in certain families. Initially observed by Steven J. Miller in one-parameter families of elliptic curves, this phenomenon manifests as the first normalized zero lying systematically further away from the origin than the Katz-Sarnak density functions predict [cite: 21, 32].

For a family of elliptic curves of rank \( r \), the Birch and Swinnerton-Dyer conjecture dictates that the central point hosts exactly \( r \) "family zeros" [cite: 21]. Miller’s experiments demonstrated that these family zeros at the origin seemingly act as a repulsive force, pushing the adjacent non-trivial zeros away. The magnitude of this repulsion increases as the rank \( r \) increases [cite: 21, 33]. 

Crucially, statistical tests (such as the Pooled Two-Sample t-Procedure) provide exceptionally strong evidence (often exceeding 5 standard deviations) that this repulsion is a finite-conductor effect [cite: 21]. As the analytic conductor of the curves increases towards infinity, the repulsion gradually dissipates, and the zero distribution slowly relaxes back to the predicted RMT limit (which, in the rank 0 case, is typically the \( \text{SO(even)} \) ensemble without any anomalous origin repulsion) [cite: 21].

### 4.2 Discretization and the Kohnen-Zagier Theorem

To theoretically model this repulsion, Dueñez, Huynh, Keating, Miller, and Snaith introduced a modified random matrix model called the "excised model" [cite: 5, 25]. In pure RMT, the values of the characteristic polynomials of matrices near 1 can take any continuous value down to zero. However, for actual \( L \)-functions, the central value is not purely continuous. 

By the Kohnen-Zagier theorem, the central values of the \( L \)-functions associated with quadratic twists of a modular form are proportional to the squares of the Fourier coefficients of a corresponding half-integral weight modular form [cite: 6, 31]. Because these Fourier coefficients are integers, the central values of the \( L \)-functions are quantized or "discretized" [cite: 31]. There exists a hard mathematical gap; if the central value is non-zero, it cannot be arbitrarily small; it must be greater than or equal to a specific cutoff value [cite: 25, 31].

The excised model applies this number-theoretic constraint to the RMT side. By discarding (or "excising") random matrices whose characteristic polynomials evaluate below the analogous cutoff value at 1, the resulting modified ensemble exhibits the exact repulsion from the origin observed in the empirical \( L \)-function data [cite: 5, 31]. 

However, a highly significant 2024-2026 preprint by Coloma, Ryan, et al. (arXiv:2401.07959) tested this excised model across broader families [cite: 5, 6]. They examined the twists of \( L \)-functions of modular forms of weight greater than 2, encompassing families that follow Symplectic, Orthogonal, and Unitary symmetries [cite: 5, 6]. Their massive numerical evidence supported the expectation that repulsion decreases as the conductor increases [cite: 6, 34]. Yet, surprisingly, they found that implementing the discretization arising from the Kohnen-Zagier theorem did not accurately model the data for forms of weight 4 or higher [cite: 5, 6, 34]. The excised model, which perfectly describes the weight-2 elliptic curve scenario, appears to break down or require fundamental modifications when applied to higher-weight forms [cite: 5]. This revelation points to a subtle breakdown in the naive application of half-integral weight discretization to RMT models, presenting a major open problem for the late 2020s.

### 4.3 Fine Structure in Landscapes: Zero Rigidity and Ditch Avoidance

In 2025, David Farmer published a groundbreaking paradigm (arXiv:250124-Farmer) for visualizing and explaining the fine structure of \( L \)-function zero distributions [cite: 7]. Farmer plotted large collections of \( L \)-functions as points in a multi-dimensional parameter space, creating "landscapes" of \( L \)-functions. 

In these landscapes, Farmer observed distinct striations and empty regions, representing systemic deviations from naive RMT predictions [cite: 7]. He theorized that these anomalies result from a combination of "zero repulsion" and "zero rigidity" [cite: 7]. 
- **Zero Rigidity:** The principle that the actual zeros of an \( L \)-function do not stray far from their "predicted" locations. The predicted locations are dictated by the Gamma factors in the functional equation (the continuous, non-arithmetic part) and the sign of the functional equation. These can be computed via generalizations of the Riemann-Siegel theta function [cite: 7].
- **Ditch Avoidance:** Farmer defined "ditches" in the parameter space as loci where a predicted critical zero perfectly aligns with the height of a trivial zero (the zeros located at negative integers) [cite: 7]. By the principle of root repulsion, critical zeros repel trivial zeros. Therefore, an \( L \)-function is highly unlikely to possess parameters that place it inside a ditch [cite: 7, 35].

This "ditch avoidance" causes macroscopic voids in the landscape of \( L \)-functions. The RMT models entirely miss this fine structure because the ditches depend explicitly on the discrete analytic nature of the specific Gamma factors and the location of the trivial zeros, features that are washed out in the continuous matrix limits [cite: 7, 35]. As the conductor or the spectral parameters increase, the deviations from the standard predictions become highly structured, exhibiting what Farmer termed "congruence bias" [cite: 7, 35].

### 4.4 Unnormalized Differences Between Zeros

Another dimension of empirical deviations explores the absolute, unnormalized differences between the imaginary parts of zeros. In 2013-2016, Kevin Ford formalized an observation originally made by R. P. Marco (often referred to via the "eñe product") [cite: 13, 36]. The phenomenon highlights a subtle inequity: the unnormalized differences between the large high-lying zeros of the Riemann zeta function tend to avoid the specific locations of the small low-lying zeros [cite: 13].

Ford extended this analysis to more general \( L \)-functions. He proved that the precise location of each low-lying zero is holographically encoded in the distribution of the high zeros [cite: 13]. Even more strikingly, Ford demonstrated that the algebraic rank of an elliptic curve over \( \mathbb{Q} \) is encoded not just in its own \( L \)-function, but in the unnormalized zero sequences of entirely different \( L \)-functions [cite: 13].

This empirical reality, supported by extensive numerical computations on the first 100,000 Riemann zeros, challenges the RMT notion of statistical independence between different families [cite: 13]. When using the Ratios Conjecture to compute the two-point correlation, the explicit formula yields lower order terms involving the zeta function evaluated on the 1-line. Because the minima of \( |\zeta(1+it)| \) align with the zeros of \( \zeta(1/2+it) \), a repulsion effect manifests across different scales, imprinting the low zeros onto the gaps between the high zeros [cite: 13, 36]. 

## 5. Weighted Densities and the Influence of Central Values

A major focus of theoretical research from 2022 to 2026 has been the "weighted" or "tilted" one-level density. In this framework, the sum over the zeros in the 1-level density is weighted by a power of the central value of the \( L \)-function itself (e.g., \( L(1/2)^k \)). This approach artificially amplifies the contribution of \( L \)-functions that possess exceptionally large central values, illuminating how extreme central values distort the statistics of nearby zeros [cite: 8, 24].

### 5.1 Fazzari's Conjecture and Tilted Averages

In 2022, Fazzari investigated this tilted average and proposed a profound conjecture. He posited that for a family of \( L \)-functions belonging to a specific symmetry type (Unitary, Symplectic, or Orthogonal), the one-level density weighted by central \( L \)-values should exactly mirror the density of eigenvalues of random matrices weighted by the corresponding power of their characteristic polynomials evaluated at 1 [cite: 8].

For example, when evaluating the weighted density for a family of continuous shifts of the Riemann zeta function, \( \{\zeta(s+ia)\}_{a \in \mathbb{R}} \), or for families of quadratic Dirichlet \( L \)-functions \( \{L(s, \chi_d)\}_d \), Fazzari utilized the generalized Riemann Hypothesis and the Ratios Conjecture to extract the exact functional forms [cite: 8]. 

The presence of the central-value weight alters the effective symmetry type of the family. As discovered in these works, the resulting weighted density functions diverge from the standard Katz-Sarnak distributions [cite: 8]. A weight introduces a "repulsion" or "attraction" at the origin analogous to shifting the symmetry group from, say, Orthogonal to Symplectic, depending on the exponent of the weight [cite: 24]. This demonstrates that the local spacing of zeros is intimately coupled with the global magnitude of the \( L \)-function at the central point [cite: 8].

### 5.2 Hilbert Modular Forms and Central Value Weights

Fazzari's conjecture received robust confirmation in a 2025 preprint by Zhao (arXiv:2508.18469). Zhao investigated the set of primitive Hilbert modular forms of weight \( k \) and prime level \( q \), with a trivial central character [cite: 9]. The unweighted family of these standard \( L \)-functions exhibits orthogonal symmetry [cite: 9]. 

Zhao studied the one-level density of the low-lying zeros weighted by powers of the central values, \( L(1/2, \pi)^r \). For the exponents \( r = 1, 2, 3 \), Zhao rigorously computed the resulting probability distributions \( W_r(x) \) via explicit formulas and the Petersson trace formula. He demonstrated an exact match with the predictions derived from Random Matrix Theory for matrices weighted by their characteristic polynomials [cite: 9]. Furthermore, Zhao established a comprehensive conjectural framework based on the Conrey-Farmer-Keating-Rubinstein-Snaith (CFKRS) "recipe" to predict the shape of the density functions for any general integer \( r \ge 1 \) [cite: 9]. 

These findings indicate that the RMT models possess an extraordinary elasticity; they do not merely describe the baseline zero distributions, but correctly predict the heavily skewed distributions that arise when forcing the system into extreme arithmetical configurations [cite: 9].

### 5.3 Moments and Large Deviations

The study of weighted densities is mathematically equivalent to analyzing the moments of \( L \)-functions evaluated over their zeros [cite: 37]. In another 2022 paper (arXiv:2208.08421), Fazzari considered the average behavior of the test function evaluated over the zeros of the zeta function, weighted by the central value [cite: 37]. 

By pushing the moments to their extremes, researchers probe the "large deviations" regime. Soundararajan and others have explored these extremes, noting that the values of \( L(1/2, \chi_d) \) can be accurately modeled by random Euler products. However, unconditional theorems still lag far behind the probabilistic models concerning the absolute maximum and minimum possible values of the \( L \)-functions [cite: 38]. 

When analyzing the large deviations from the Gaussian behavior, the RMT models predict specific constants that govern the tails of the distribution. Unconditionally understanding these extreme values, and how they dictate the frequency of zeros that cluster anomalously close to the origin, remains a primary objective. The weighted 1-level density provides the sharpest analytic tool to dissect these rare events [cite: 37, 38].

## 6. Applications to Elliptic Curves, Modular Forms, and Number Fields

The overarching RMT framework serves as a vital tool to answer deep arithmetic questions across diverse geometric and algebraic objects. The literature of 2024-2026 places special emphasis on families characterized by subtle arithmetic properties.

### 6.1 One-Parameter Families of Elliptic Curves and Excess Rank

As previously noted, one-parameter families of elliptic curves over \( \mathbb{Q}(T) \) form an ideal laboratory for RMT investigations. According to Silverman's Specialization Theorem, for a sufficiently large parameter \( t \), every curve in a family with generic rank \( r \) will have an \( L \)-function with at least \( r \) zeros at the central point [cite: 21]. 

The Katz-Sarnak conjecture predicts that all such families with the same distribution of functional equation signs should exhibit the exact same universal limiting behavior for their main term [cite: 22]. However, empirical calculations of the ranks of elliptic curves often reveal a significant "excess rank"—the percentage of curves possessing rank \( r+2 \) is drastically higher than asymptotic models suggest [cite: 18, 21]. 

This anomaly is explained through the lens of lower order terms. The specific biases in the Fourier coefficients of the elliptic curves (as described by the work of Rosen and Silverman) manifest as massive finite-\( N \) corrections that temporarily inflate the probability of multiple central zeros for small conductors [cite: 22]. The detailed 1-level density expansions generated in recent years successfully trace how these lower order biases decay, quantitatively explaining the transient phenomenon of excess rank [cite: 22].

### 6.2 Higher Weight Modular Forms

The investigation by Coloma et al. (2024-2026) deliberately shifted focus from elliptic curves (which correspond to weight-2 modular forms via the Modularity Theorem) to higher-weight modular forms [cite: 5, 6, 25]. By analyzing the twists of these higher-weight forms, they categorized them into specific RMT symmetry groups [cite: 5]. For instance, self-dual newforms with real Fourier coefficients partition into Orthogonal or Symplectic families based on their root numbers [cite: 5].

Their experiments involved computing the zeros of hundreds of thousands of twists. While the fundamental Katz-Sarnak main terms held firm, the breakdown of the Kohnen-Zagier excised model for weights \( \ge 4 \) highlighted a fundamental disconnect [cite: 6, 34]. The mechanism that discretizes the central values of weight-2 forms does not neatly translate to the repulsion profiles of weight-4 zeros [cite: 6, 34]. This suggests that the arithmetic geometry governing the central values of higher-weight forms interacts with the local zero statistics in a manner currently opaque to standard RMT modeling.

### 6.3 Quadratic Dirichlet L-functions and Number Fields

Dirichlet \( L \)-functions, being the most structurally straightforward generalization of the Riemann zeta function, provide the strictest tests for RMT. The family of Dirichlet \( L \)-functions attached to real primitive quadratic characters exhibits a Symplectic symmetry type [cite: 15]. 

Södergren's rigorous extraction of the lower order terms for these quadratic families illuminated how the discrete conductor \( X \) impacts the continuous integral. The discovery of the phase transition when the Fourier support \( \sigma = 1 \) proves that the zeros possess "hidden" non-local correlations that only become visible when test functions span a sufficiently wide spectral range [cite: 15]. 

Furthermore, an innovative 2025 preprint (arXiv:2507.0274) introduced a novel "extreme value parameter" \( E(p) \) to quantify the behavior of quadratic \( L \)-functions. By defining this parameter through the empirical logarithmic means of the extreme values of the characteristic polynomials of random orthogonal matrices, researchers cross-validated the \( L \)-functions against the Riemann zeta function itself [cite: 39]. This provided robust, cross-family statistical diagnostics that verified internal consistency with RMT to an unprecedented degree of statistical correlation (\( R^2 = 0.9312 \)) [cite: 39].

## 7. Ongoing Research and Future Directions (2024-2026)

As the limits of the asymptotic theory are reached, the focus of the mathematical community has firmly pivoted to understanding the microscopic deviations and the intricate interplay of discrete arithmetic with continuous ensembles.

### 7.1 Methodological Shifts: Ratios of Characteristic Polynomials

A prevailing theme in the recent literature (such as the 2024 paper by Conrey and Snaith) is the methodological shift away from standard determinantal forms in Random Matrix Theory [cite: 23]. The traditional \( n \)-point correlation functions for groups like \( U(N) \) are written elegantly as \( n \times n \) determinants of the sine kernel. However, this form is completely intractable when attempting to align it with the number-theoretical explicit formulas [cite: 23]. 

Instead, the modern approach derives the RMT statistics explicitly via averages of ratios of characteristic polynomials. This produces complex, non-determinantal algebraic expressions that exactly mirror the structure generated by the \( L \)-functions Ratios Conjecture [cite: 14, 23]. This parallel methodology not only proves that RMT correctly models the zero statistics, but explicitly shows *how* the continuous matrices emulate the discrete prime sums [cite: 14, 23]. Extending these ratio calculations to wider supports (e.g., from \( (-2,2) \) to \( (-6,6) \)) represents the cutting edge of RMT analytics [cite: 23].

### 7.2 Major Upcoming Workshops and Conferences

The intense interest in these topics is reflected in the schedule of premier mathematical institutes over the 2024-2026 horizon:

- **Clay Mathematics Institute (September-October 2025):** The University of Oxford will host a major CRC Workshop on "Zeta and L-functions," organized by Blomer, Keating, and Soundararajan. The agenda explicitly highlights connections between probability theory, random matrix theory, new zero density estimates, and progress on the sub-convexity problem [cite: 40].
- **American Institute of Mathematics (AIM) (December 2025):** A highly specialized workshop in Pasadena, California, organized by Rubinstein, Snaith, and Turnage-Butterbaugh, will focus strictly on "Moments of the derivative of characteristic polynomials and L-functions." Topics include the distribution of zeros of the derivative, non-integer exponents on the derivative, and the varying rates at which evaluation points approach the unit circle [cite: 41]. These inquiries are explicitly designed to refine our understanding of the exact zero distributions and the lower-order deviations [cite: 41].

## 8. Conclusion

Between 2024 and 2026, the application of Random Matrix Theory to the zero statistics of \( L \)-functions has matured significantly. The field has moved beyond merely marveling at the asymptotic universality of the GUE, Orthogonal, and Symplectic ensembles. Today, researchers utilize RMT as a precision tool to dissect the finite-\( N \) anatomy of \( L \)-functions. 

The successful deployment of the Bogomolny-Keating formula and the \( L \)-functions Ratios Conjecture has enabled the exact derivation of lower order terms. These corrections prove that the arithmetic signature of a family—whether dictated by the signs of functional equations, complex multiplication, or prime biases—is permanently inscribed in the sub-leading deviations of the zero densities. 

Simultaneously, empirical experiments of unparalleled scale have unveiled striking localized phenomena. The repulsion of zeros from the central point in modular forms, the systemic failure of the Kohnen-Zagier discretization in higher weights, and the existence of topological "ditches" in \( L \)-function landscapes all demonstrate that while RMT provides an exceptionally accurate global framework, the discrete, rigid nature of prime numbers fundamentally resists a purely continuous description at finite scales. 

Through the ongoing synthesis of quantum chaos traces, weighted densities, and massive computational data, the grand mathematical endeavor to decode the spectral nature of the Riemann zeta function and its generalized relatives continues to drive the frontiers of both analytic number theory and mathematical physics.

**Sources:**
1. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5lHppJDytYdhBXmg_35HoOoNDkddFCNua8nJ8OqIw7ogBozZj8Uy7y82jCg4gP-ZG6DaUNIn6TKXXLjGTgVPX7jvzH3DJTLMX2kFPrDcy3avfJgCtVCS2W1YZg6v4ucJYA1Jid2YRbUm4fyN5iZB-FPf0QEpx_mP_0MXp8DvwJ-Pnv5VSb237RWtkZiQO2N_aUjpsvnd-WSNG5xpd)
2. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXPP-FhGu5JjB2ZyI-NpLod3YxA6_9iy3BmS3Bf4E2nhZlXLdYzImv3gQ7toAEHWkF7bQ1X7aDeK2_NW7_QKcZ8wJUdsxtO_9keeNJPWvhnHwMWLIk0VAAWvVgiK_P)
3. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI-4OxC90sUD-Xy_xoTDTPrjIV2QVL62I-TCM93ls_o9cl_CE8TQ3IOUfh9WeQSqbdTOAod0Cpg_DhFoOGl54smyVlnrYWuvzDXl_34ZJ-Z5Xr7J7Bggr2AVcnSLe9nNAMR0trGnreDSSotd7o1qLUaHx0hqvhB-9sWEjf8cD5E5E9_z-yCxkyLKd2NhJfVQMjYcU864rkXKeNNMpGiGGKHY-tiik4tKvUsg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpEdVv6ahZmNieEc7HmUzxiaWZTwFasa-kvKDbCYKZxWsUXFzODppp_oQnW-lwXf9zP7rtrlCsfwXxF8DSqfRTToBEVRY8GtaBLjvwrM_iu7df7cPh)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLypo4Bq_C_Ee8h_mDLTb7p88IG3vDIr7OcyDiqwDpwXszce9ZrHNbuQBQNV8OcgTYXbm9EVIRvVX_fs28P3umZhXAg7r3ka4hHkNYqoIY9gUplIpYuQ==)
6. [jexpmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrRQguWfKY93E2mP3Vkp9AHbUF4FkepVMINh8PjZtVcXwJ4yvUuy0Mk2kgfLtIzgCf-7bfsX0OKYMnVMpAkMvfIe-XS4DAzKnpcf8fp21Ts41Z-GaABz2LUX5-gbnaYHZptcGOrbVXYZB9fCuRFfBGPEimTqXL7ltA)
7. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ6yORWeeP7Dy2qcsEhkvv2ArwhfUSGf5xDJLhjMtvYAKdbSsYFPRWC5Dnamcd2R_J3SjPG7RUV1iGXp8ijkVwpsqdapTXMbJThKwsFxWayAkMTHdxTg7ZgI7VlRLx4fuW-EzCcG8=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdMXjtvdh0Hsd9mqdI6jFat4nU4VkjRcugqGKhnlgO1oiEgjleljfk1GGiUW5A31gfM3HrEq3RyEDYg315yX00awfnyBqgj7GmtaKLV5JdBuHxf6hlwA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBYJSymFZ9JsmKk28GuUOT81aUsJyqqTPi7Wd37t4yIePuTYGQULZMzKdJX0opzEXtSvE_1l6XNB-yTIPLgn-wrFeT83ghL8HQ9xH4JgUMuliG2HEOlA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz2FzjJS21mkgdBej-ntRKN1NM-QphynnvzoopDdEC3XPH8p4bf02H1JqmcmERqE7uN5ZFDjbubiz8yX40iO1nGCmyMKt4fzkfd0p97Z_qiOcmMOV_)
11. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENjOSkkQkQSRZdinBS9mofJb0pPJ7Y80se78R7VLCodfLnD0_5BLcpJi0pLY653OMGsG8o_j94vB9uyJ81OsEIUAivW_mvAi0-qvvyis-YYNdy39qmfAxGw0SIWX0W)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJB5HY2SWAQuyrUoMkuE0809RKZLu98Vegfbf2iVRV1U7EFuuzz4J1XLVK27qAmXKAfmgl5ZhDQELi_mJy-47pITej19037t3RQZzb1KIblaVbfUBtAg==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvKdsITatst7j6Sb_MBvGrA0JLfi_rGZnd5gZAnj0cAlHFCPnKJWHM7rwHpiBXlTsJHeshhtzr4tPxM5mO1Q-w6pquQE300T7a-R1fmA0fXa6pld2J0cnPxkBppGXh-4_NFFGFM0rTrmkznXdYxiCZwgFvTFrBpv0UQVPt6gXbuRzPR2TteXKo2s_HwZUOeTKiFRIgBD6iK6Q9LmRcxQ==)
14. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWTezZgktKYDQEv_EV3kxbdqZtfdchw00vz6wnzlZ3U0I3vOISG0VeuxdOCesulXvo-FhNurpkP0wSm8LGrdFvv7rEU_8wUBjH_isEtYuHul_vhTzcC_D3E55n0QjSvDx60sSB)
15. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMFtKRRQr7j5Q8ZAJYq0FZDwwkHC1QYFlesCB42bQOUyVVMNlpnEmBejF8gWEUnaFhizy6x7Z989USQL_3-sbMuBCKYRyLFrfFx2dHW1SxF8HmA51X3ct0xF-bhwyXgrDpYCDREtGbje83-RXkvHau9s2br6hNhO3CInkMCbunXIB6qpbx2k5VkHEmDghsnD9k4c69TPoA7sDLoT2-1Rf0eVKG1MXeMUls4WXgXTtcYsUj16LxDAZFt3I3NpkkIZOXPslR1dqzTBR7sXsXDMN6evV3U1mFVtBL25DHZygBLQ9RNxtjElg_e1lmhHlFECFjEcRcABzk)
16. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgAfG14iKQ4kQZzFdH86Hzd0yd2ZGHuBUD-zuCca_IdMmL5o2KGC4bnqnGdvKeAyO_HDFLSOpNKsmSUsP2Y5qF1COsrj5QqX3I0NSBUgAFkCxJPO2XnZDdgT_LYEhYMtTbpeEL4Nmb3M_cT1vWreYzOMy2CUP1Gjk=)
17. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwNyCuGYOzYaBOnCRB71HqevfQjRA2RwzDch1tH7RR0gnj6e8ejjOTVTxC-dNd5_lCDKk78NVCATOPER62HovvocJVomt7q3YzzlemcAf9150coYe4u7LJc-oh0MPiGSXl8e2J5irZufdf)
18. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQXstwG3x61mRlVNOhtf0kl5xw5MA2oCxuAsusy-DTew7sIlZ4BUIeSQaDyTGavA3LylMu0o1H2d67XUmjpU08u5glW8MiJOCzjOC2OOT1eXGysbcQjmf4FEbKAOnXt94YhCrq96QpEMzrjRG2crjltcSSg4WehQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuVksScz7_pt9nGzQpBQhTmROFjfvNSzX8YooOdmmnBnF77GgZ-AU_sl-sn00WmirDSU11CDq1nQaFVbofGFkcVt5UYSvS7GCDE2pYfmp8AvG6J21fXw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIyz7Ya1ECHP5tFWgizycEe4tu6tt1mY5PjFete5kTccqvw4ERxe-_18DOwBc_MBKuIj0QwqIO3Mwz1bndhcy2wWDzsO7_bKrRnFBtYv-eSF1hItFLUA==)
21. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPkAQYPcoNS0_nJ79HMEWpNOUZaQO1ZJiQzN24E114a2ZABUOT4sdSh_IEv5S3QZcSSw1RW97aVa5hwWBoU35sKoS0hAB8ZJv-pCbOLQDExCKyECN0Yz9SjGAQT0ChntmAiU744yMfqyViQydg3M3ejWOkbYW-Nrib-heaJTG3CDSo40BXEkj7qdL3QQ==)
22. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_9PZ68bRQ-r9_UAr6Nl2Ah5Atj2olVkKvUrdFl_n12HqbEi6kGe9kS7G-f5D-k1yYnHCZrfjLIo5hzSP7CxWua5z6ST8bOmMqMX6Tx6ll_dadxbMR3n1X-Fq5QdL_UdTBjUZnornKbSe2Dy3Hp8O0IYx_FD3g_Q0MCmv6SVJK48eId6x4d4wGBCxMfQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF61gAeWKocgrn4eQwU0d-rMB_kYDeVFoCYzH4Xfo7pRS5S_A6Fr_dwkxvpyvd9wjlRDaF1-ASFtxHvJzh7Pt1d5eA0niZ6ic1tlJRIVXti7U5vVX6emg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-mXsQFpTAPvu6esQ64OlWKfmRafJFHKBVA6fXDADfE54AOe956AFtffTUn--tIRIsOrbGQj___woo6jfsa78jFSEVlQhDCy8bjR7ZKcwgApoO7PJZyA==)
25. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEURk3aX_xyHHuiMUvBorQICtFwSP1Jpb7Egr3GdlbpxP2GVfSkpqfP68skHjx-YFdk1fEeZNQ-Ob0PZjATgL1ETwX9MaNsnGin-P6By9K5D3CMzAG-_ufB11GkQc1-RU1BSmXoXyFOkKU9NsY1M0nhA5qbGyyz_vs=)
26. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJKzScVkJi52Z381EgZwZhzGL5aj59xtcJZzhi0HOOuLVBMObnr4yv5utulg59XSx-baL4P3usJJYRJwceIRdNsiOK4vqbXf98lz81a221C_L9u6Up5vXg-HOaGyHFfA32iqI57256moaWhsSlsJkmj9jj_ENKwUDL0guoq8RJj37T8uIyOT0QqAIjuvHcddGKAICcfhyt63xegjs=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFDzqwZHx2jvbgJeVFqS1R9YLuDPKSCPWZP6w-lT93jY0AuANextzMCJq5j9ObtH0k815fj_xOaRrz8hmMoA2BqG4zqmmTDQ4QISW21LKUh3LARbu52T_ujQ==)
28. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA-vnl2vaOtHSRui2H1D8EgvJcDrxQBvr-dirK-lEMGIHMz5AfSEOIL983I-pDdQhTjNtoeRCEl0veCY6zouvODp4VOUIOTsbv9292zz9eCcCGW-cijfQac5L-gVgNuCvwvy9qzYYWZWvid42r8jd0NLU9rkYB)
29. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4YgIgvFf0l88kGICvyzQMpOewaYkbRuqRItv7Nt3O6povSQhvIDVn-lL0RbFgQeNwtZnnLraUtkV7T9yd20_urPlytN83vIyBS6k_CjCNGP8JL8JolIQzCySQv9xWCNrPZ1IP0po41nbTRPW60NC0u7w0RoC8HdkV_wNBHRy6qO--SOND)
30. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzUXHdzem2lPM8HobcvfKYg0TW0jcOYAFPRA2ZqnmCRJbo8CBkUDdXamT9K_iKEFWA7p0t_SkVv4jzE_Ymq4mNdYcoiB_ZSfZpO6Vs1pABjcTLgFCkMPwAkUudwA7iOGxDyAn-HSm_OJgnQBcO2Ro2S2VxSy3tphbXhfu0yjSmzfkQP2VZ_2dX9GM7JGuMDxWmu9NM)
31. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJOs2_cDN_iNRGvj0cQr3nQuySKb7f7HIlXgv7h1XHOBW-I50LfSC2w9uU9LXFiGKFxOHNue42tI0ksrlRDWjnT79L8VeIeFDpscwt8eMSi01Hp_Ijif61TpqbTGXMEAv6OV2kruXcIkEYimazojQ9Fzl8IEk9fAKG6EWjLHWfLJ49lxlnOtAH1ZaC4iyTyZj6LevNDoeyA2b0Mv2z)
32. [bucknell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdRdMC2m_NmMo5-VbbsMII95eeGqNbGzvvftNgD6tZkPpqEHvo3zsKO-4cXPH2SU8K3Joc8Ag5rYl1wqKOacURcfHdiGJZ6ujRaGcaTIAdhH0LV_Zm5tn3quQQ-ZifPtn0C_GXWPZJC9wd4cY-HLxHY1SMbGHvN_Ik_oNLRwhOzXYRm4caDDK9qAtT7_EutKc=)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhR8E-Aasv96wVRITuZjjW3sIo6311Zwz6Eal1jMvjOIJSAFmqwgK5pbH-py8EkHt_pQtGafBC-syrItDWBAG4xakiZXd-aECoFQKnzpMfBTUDCsv4xk9WD_YSgVs2S9XMJ4_2--t5T4qAqxzIxc5Ave2kkZ16EN3foUuGQ-AsEi7Ut9KwIbm06cIq)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEexWgKgGRSu0V_GyaWs2A6_sd9dXVcuNmT4OcymWIO426TKt8S6gK3aqQAl9kmdCT5Hwrakxy0t6VomAcAK1IPpQustD6tVG9hZP_MUBY4AGaP9nfjRw==)
35. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxVnIma33jjTdg1yTq_zhuBGFj5QhtDYSYKx4tTsoXEBnzX6TQAtW4Wa92dHhVTHARiTUMhq04iPLpNRi26G7JaGNTu0pOOtLS2TmoAR-IZ3Iijow1F02YuAE4j83mCCPGENZASbl6SAmo)
36. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPUy7QoNoolV8wO0DI0kGTa1QFornt35u-iD-VEEAsmbi57O2rHhdHU185iauph0-Ff1Tx7wfVzqqHvl5yoVR3F5SeceUGU2u93FlbtX52aTsw2koMndbb16w32oOUk4rOkGZR30yCFApGwtHhoqDVfOfUCjNPOERsc36HVUp_KQEujPWX--j15kmwvZRWqzngE-XI5x9Fu_t52GbP_FOt902AVHupeLpmCGP7vHFElIVIRjDF6rdm)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgXGU8rHHrzsJ71Rn8NkaUwkVXaOnppqCV9s_NOjhgy0ad3OJZp_BhJP6EbMN8kiWCfiU3LLNb19bPbtyE8sRr2oDn6cDvBNvOQi0t4LUdGZXoPhfChw==)
38. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUdg6AvcjV06xufNk4oLvvboCfC9ylkjqWCmc34J5EEfuo0oGXKg-lxeqRZ78n_4XuFvKxo3EoL_PMWSNtpIm-RVjPS5JRrF_UICFWWJwNYX9PFTJ_EXys5y9nWEITYlTcfo4-7LAxWw==)
39. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOkdPUp9hKelrxEeaifyH8wXnc0zFN9-2ywE02C-k0P6j4I85fe3mtihll42WBGYEuh96vHKh1eEI6KOnAoGatA3ZUWucwoQliTfzIIUJ5m9ByZElgEoRbJDxNDpv-pZVMVwrLzj1rykvyrT0X670dyHcUASTf5WXFkQ==)
40. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAQGqj8ctzgySzLEQ8JaKse_304jzZHGhjNLuiiRxcs4pf0zkT5AcT2J6DjJ2R7dZLOYMg_IJ9FovQDDpPAmonpbxrQ2IhnKJa7kdKRLtLTgLzU9Jk6fSWGdkNJouGsXwZq3sMqeKlOSbcZw==)
41. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5Pt4M3giAd2fjL4oeQKoHKc5VHYErR-NfUJCSJjc8XWg-uI7M_NdIOyJH_G1NDI6TqyqjivK0T20j-dusA3OI8bPsJ0Fi6kl-neVdWSE6tEbr2KV9J0KNjY3_5bsAeBsYTRw=)

