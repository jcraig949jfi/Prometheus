# Rankin-Selberg L-functions GL(n) x GL(m) explicit formulas (Kwan 2024-25 extensions)

**Pythia queue id:** 138
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcteXdQYXNELU5LRG1fdU1QcDQyNXdRNBIXLXl3UGFzRC1OS0RtX3VNUHA0MjV3UTQ
**Elapsed:** 311s
**Completed at:** 2026-05-21T16:09:24.392067+00:00

---

# Comprehensive Analysis of Rankin-Selberg L-functions for GL(n) x GL(m): Explicit Formulas and the 2024-2025 Extensions by Kwan

**Key Points:**
*   Recent breakthroughs in 2024 and 2025 by Chung-Hang (Kevin) Kwan and collaborators have drastically advanced the analytic theory of automorphic L-functions, shifting the paradigm from classical trace formula techniques to systematic period integral evaluations and spectral reciprocity.
*   Kwan's series of papers (*Spectral Moment Formulae for GL(3) × GL(2) L-functions I, II, III*) successfully bypasses the notoriously complex Kuznetsov and Voronoi formulas globally by utilizing the GL(3) period integral method, uncovering exact Motohashi-type identities for higher-rank groups.
*   A major milestone was achieved in late 2024 with a new subconvexity bound for GL(2) × GL(2) Rankin-Selberg L-functions in the level aspect (\( p^{1/2 - 1/524 + \epsilon} \)), using a refined delta-symbol method that remarkably avoids the spectral theory of automorphic forms entirely.
*   Parallel investigations have expanded the Rankin-Selberg convolution beyond the general linear group, most notably establishing integral representations for GSpin × GL groups (Asgari, Cogdell, Shahidi, 2024).
*   The broader "Period Reciprocity" framework is bridging the gap between moments of L-functions, Braverman-Kazhdan generalized Fourier transforms, and the Conrey-Farmer-Keating-Rubinstein-Snaith (CFKRS) moment conjectures.

**Executive Summary**
The study of Rankin-Selberg L-functions is a cornerstone of the Langlands program, providing a powerful analytic tool for understanding the arithmetic of automorphic forms on higher-rank groups. Historically, the pursuit of explicit formulas, subconvexity bounds, and exact moment evaluations has been hindered by formidable technical obstacles inherent in multidimensional harmonic analysis and complicated geometric trace formulas. Over the period of 2024–2025, an extensive body of work led by Chung-Hang Kwan has fundamentally altered this landscape. By pioneering advanced Fourier-analytic frameworks and exploiting the geometry of period integrals, Kwan has generalized the classical Motohashi spectral identities to the GL(3) × GL(2) setting and beyond. Furthermore, collaborative efforts utilizing the delta-symbol method have yielded unprecedented uniform subconvexity bounds. This report comprehensively details these advancements, synthesizing the latest literature on Rankin-Selberg convolutions, exact spectral moment formulas, character sums, and the Braverman-Kazhdan program. 

---

## 1. Foundations of the Rankin-Selberg Method and Explicit Formulas

### 1.1 Historical Context and the Classical Construction
The Rankin-Selberg method is one of the most powerful and enduring techniques in analytic number theory and the Langlands program for directly constructing and analytically continuing automorphic L-functions. Introduced independently by Robert Alexander Rankin (1939) and Atle Selberg (1940), the method originated as a mechanism to study the tensor product of the standard representation of GL(2) with itself [cite: 1]. The conceptual basis of the theory traces back to Bernhard Riemann, who originally constructed his zeta function as the Mellin transform of Jacobi's theta function, utilizing the automorphy of the theta function to establish the functional equation [cite: 1].

Erich Hecke and Hans Maass subsequently applied this Mellin transform method to modular forms on the upper half-plane. Rankin and Selberg extended this by integrating the product of two modular forms \( f \) and \( g \) of weight \( k \) against a real analytic Eisenstein series \( E(\tau, s) \) over a fundamental domain \( D \) of the modular group \( SL_2(\mathbb{Z}) \) acting on the upper half-plane [cite: 1]. The classical integral takes the form:
\[ \int_{D} f(\tau) \overline{g(\tau)} E(\tau, s) y^{k-2} dx dy \]
This integral representation reveals the analytic continuation and functional equation of the convolution L-function \( L(s, f \times g) \). 

### 1.2 Adelic Theory and Local-Global Principles
While the classical formulation is elegant, the modern understanding of the Rankin-Selberg method relies on the adelic framework developed by Hervé Jacquet, Robert Langlands, Ilya Piatetski-Shapiro, and Joseph Shalika. Jacquet and Langlands provided adelic integral representations for standard and tensor product L-functions, elucidating formulas for all local factors, stating the functional equation in a precise form, and providing sharp analytic continuations [cite: 1]. 

The Jacquet-Piatetski-Shapiro-Shalika (JPSS) theory established the global theory of newforms for automorphic representations of GL(n) over number fields [cite: 2, 3]. A critical component of this theory involves computing the local Rankin-Selberg integrals of Whittaker functions. Over non-archimedean fields, this theory is well-established, but over archimedean local fields, extracting explicit formulas and propagation formulas for Whittaker functions is highly non-trivial. Traditionally, two main approaches have been used to establish explicit formulas over Archimedean fields: one based on Jacquet integrals, and another relying on generalized Barnes integrals as pioneered by Eric Stade [cite: 2]. Stade's explicit formulas are crucial because they evaluate the local factors \( L(s, \pi_v \times \pi_v') \) on GL(n) × GL(n) directly as local integrals of Whittaker functions [cite: 2].

Despite these successes, having an integral representation for an L-function by no means implies that its analytic properties are entirely resolved. Significant analytic issues often remain, particularly concerning the bounds in the critical strip and the calculation of local integrals after the unfolding stage [cite: 1]. In many situations, researchers rely on the complementary Langlands-Shahidi method or period integral techniques to extract further arithmetic information.

---

## 2. The Spectral Theory of Moments of L-Functions

### 2.1 The Arithmetic Significance of Central Values
The values of L-functions at the central point of the critical strip, \( s = 1/2 \), encode profound arithmetic, algebraic, and geometric information. A fundamental problem in analytic number theory is to determine the statistics of these central values, specifically their non-vanishing and their size [cite: 4]. A primary objective is the Generalized Lindelöf Hypothesis (GLH), which predicts that \( L(1/2 + it, \pi) \ll_\epsilon (1 + |t|)^\epsilon Q(\pi)^\epsilon \), where \( Q(\pi) \) is the analytic conductor.

Short of proving the GLH, mathematicians strive for "subconvexity" bounds. The convexity bound, derived directly from the Phragmén-Lindelöf principle and the functional equation, states that \( L(1/2, \pi) \ll Q(\pi)^{1/4 + \epsilon} \). A subconvexity bound improves this exponent to \( 1/4 - \delta \) for some \( \delta > 0 \). Establishing subconvexity has far-reaching consequences, including Quantum Unique Ergodicity (QUE), equidistribution of arithmetic objects, and solutions to Hilbert's 11th problem concerning representations by quadratic forms [cite: 5, 6].

### 2.2 Moments and the CFKRS Conjectures
An effective methodology for establishing both non-vanishing results and subconvexity bounds is the computation of *moments* of L-functions averaged over specific families. Moments can be continuous (integrating over the critical line) or discrete (summing over a basis of automorphic forms). 

The structures underlying the full set of main terms in these moment calculations are famously intricate. The Conrey-Farmer-Keating-Rubinstein-Snaith (CFKRS) conjectures—often referred to as the "recipes"—provide remarkably precise predictions for the asymptotics of moments based on shifted moments and approximate functional equations, drawing on analogies with Random Matrix Theory [cite: 7]. 

For instance, the recipe accurately models the cubic moment of GL(2) L-functions. Owing to the differences in families and their underlying arithmetic, the CFKRS recipe predicts eight distinct main terms for this cubic moment. In their landmark year 2000 paper, Conrey and Iwaniec successfully located only the diagonal term using approximate functional equations and the Kuznetsov trace formula, leaving the remaining seven off-diagonal terms as an open challenge due to the massive combinatorial and analytic complexity of classical techniques [cite: 7].

### 2.3 The DGH Multiple Dirichlet Series
Another major approach to moments is the Diaconu-Goldfeld-Hoffstein (DGH) method, which utilizes Multiple Dirichlet Series. Their framework derives moment predictions from the conjectural analytic continuation, polar divisors, and the group of functional equations of these series [cite: 7]. While powerful, the exact analytic continuation of higher-rank Multiple Dirichlet Series remains largely conjectural and analytically daunting.

---

## 3. Motohashi's Identity and the Rise of Spectral Reciprocity

### 3.1 Motohashi's Fourth Moment Identity
A "crowning achievement" in the analytic theory of the Riemann zeta function is Motohashi's identity, established in the 1990s [cite: 7, 8]. Motohashi discovered a deep spectral identity that establishes an exact duality between the continuous fourth moment of the Riemann zeta function and the discrete third moment of central values of GL(2) Hecke L-functions [cite: 7, 9]. In its most basic schematic form, Motohashi's identity can be written as:
\[ \int_{-\infty}^{\infty} |\zeta(1/2+it)|^4 w(t) dt = \sum_{f} L(1/2, f)^3 \widetilde{w}(t_f) + (\text{polar/continuous contributions}) \]
where \( w \) is a suitable weight function and \( \widetilde{w} \) is a highly complex integral transform involving hypergeometric functions [cite: 7, 8, 9].

This formula completely bypasses the error terms inherent in approximate functional equations, transforming an analytic question into a spectral one. The exploitation of Motohashi's formula directly enabled the best known asymptotic formulas for the fourth moment of the Riemann zeta function, and later provided the foundation for the uniform Weyl-type subconvex bounds for Dirichlet characters achieved by Petrow and Young [cite: 9, 10].

### 3.2 The Shift to Spectral and Period Reciprocity
Motohashi's formula is fundamentally the first instance of *Spectral Reciprocity*. In recent years, researchers such as Michel, Venkatesh, Nelson, Blomer, and Khan have sought to generalize this reciprocity to higher rank groups. The classical approach to proving Motohashi's formula relied on the Kuznetsov trace formula and intricate manipulations of Kloosterman sums [cite: 9, 11, 12].

However, the "Period Reciprocity" framework, originally proposed by Michel and Venkatesh and made fully rigorous by Nelson through regularized period integrals, suggests that Motohashi-type identities are manifestations of a much deeper representation-theoretic structure [cite: 7, 9]. In this view, one evaluates a period integral—such as the integral of an automorphic kernel against a minimal parabolic Eisenstein series—in two distinct ways using spectral decompositions [cite: 4, 13].

This methodology leads directly to families of GL(n) × GL(m) L-functions. For example, a spectral reciprocity formula was discovered linking a GL(2) moment of GL(3) × GL(2) Rankin-Selberg L-functions to a GL(1) moment of GL(4) × GL(1) Rankin-Selberg L-functions [cite: 14, 15]. This higher-rank analogue acts as a cuspidal generalization of Motohashi's formula, providing a robust pathway to subconvexity bounds for higher-rank groups [cite: 14, 15].

---

## 4. Kwan's 2024-2025 Breakthroughs: Exact Spectral Moment Formulae

Between 2024 and 2025, Chung-Hang (Kevin) Kwan published a monumental three-part series titled *Spectral Moment Formulae for GL(3) × GL(2) L-functions*. This series rigorously executes the period integral method to establish exact, Motohashi-type formulas for GL(3) × GL(2) families, fundamentally solving several major open problems in the literature without ever relying on the Kuznetsov trace formula or the Voronoi summation formula [cite: 4, 16].

### 4.1 Part I: The Cuspidal Case
In *Spectral Moment Formulae for GL(3) × GL(2) L-functions I: The Cuspidal Case* (Algebra Number Theory, 2024), Kwan focuses on the spectral first moment of GL(3) × GL(2) Rankin-Selberg L-functions, where the GL(3) automorphic form is a fixed Hecke-Maass cusp form [cite: 7, 17, 18]. 

A major conceptual leap in this paper is the total avoidance of the standard tools in analytic number theory: the Kuznetsov formula, the Voronoi formula, and the approximate functional equation [cite: 4]. Instead, Kwan utilizes the period integral method. Since the GL(3) × GL(2) L-functions on the spectral side are interpreted directly as period integrals, there is no need to open the L-functions into Dirichlet series. Consequently, averaging over the Hecke eigenvalues using the Kuznetsov formula becomes unnecessary [cite: 4]. 

The paper works directly with the GL(3) Whittaker function associated with the automorphic form, yielding an approach that is inherently local and readily generalizable via the adelic language [cite: 4]. The main result is a Motohashi-type moment identity that underpins Li's celebrated convexity-breaking results for GL(3), formulated as an exact equality involving explicit integral transforms of the moment weight functions [cite: 4, 7]. To extract the analytic properties of these integral transforms, Kwan heavily utilizes archimedean Rankin-Selberg-type calculations and establishes the regions of holomorphy and growth for the transforms [cite: 4].

### 4.2 Part II: The Eisenstein Case
In *Part II: The Eisenstein Case* (Submitted 2023, prepublished 2024), Kwan continues this investigation by examining the case where the GL(3) automorphic form is a minimal parabolic Eisenstein series [cite: 7, 19].

Using an identity between two distinct periods for the GL(3) Eisenstein series, Kwan establishes an exact Motohashi-type identity that links the *shifted* cubic moment of GL(2) L-functions to the *shifted* fourth moment of GL(1) L-functions [cite: 7]. This achieves a long-sought goal: the exact spectral inversion of Motohashi's identity. Previous attempts at spectral inversion, such as those by Ivic and the formal sketches by Motohashi himself, encountered extreme technical obstacles related to smoothing, regularization, and the interchange of limits [cite: 7]. 

By employing the GL(3) period integral method, Kwan surmounts these obstacles and offers a fresh perspective on the reciprocity phenomenon [cite: 7]. Furthermore, this exact formula allows Kwan to directly address the Moment Conjectures of CFKRS [cite: 7]. Specifically, Kwan successfully isolates and proves the existence of the eight distinct main terms for the cubic moment of GL(2) L-functions—terms that Conrey and Iwaniec had originally hypothesized but could not extract due to the limitations of their approximate functional equation approach [cite: 7]. Kwan achieves this by proving three new Mellin-Barnes identities that capture the intrinsic symmetries and archimedean Rankin-Selberg characteristics of the off-diagonal terms [cite: 7].

### 4.3 Part III: The Twisted Case
In *Part III: The Twisted Case* (Math Annalen 2025), Kwan extends the framework to twisted moments [cite: 17]. The Hecke combinatorics of GL(3) associated with twisting and ramification are vastly more complicated than their classical GL(2) counterparts [cite: 9]. By successfully tracking the ramification through the period integral geometries, Kwan provides explicit twisted fourth moment formulas for GL(2) L-functions over totally real fields, achieving sharp upper bounds for the fifth moment and deriving new subconvexity estimates for triple product L-functions [cite: 20].

### 4.4 Synthesis: The Fourier-Analytic Framework
Simultaneously, Kwan's 2024–2025 preprints (such as the comprehensive *Fourier-analytic framework* working paper) establish a generalized methodology that treats Motohashi-type (spectral) and Blomer-Khan-type (level) reciprocities in a parallel, uniform manner [cite: 20]. This framework applies uniformly to cuspidal and non-cuspidal GL(3) representations over arbitrary number fields. The explicit weight transforms are computed in the analytic newvector and spherical cases, paving the way for broad arithmetic applications, including simultaneous non-vanishing results and optimal error terms in the Hardy-Ramanujan-Rademacher formula [cite: 8, 20].

---

## 5. Subconvexity via the Delta-Symbol Method: The GL(2) x GL(2) Breakthrough

While exact spectral formulas provide structural perfection, bounding the error terms and proving subconvexity in the level aspect often requires specialized techniques. In December 2024, Kwan—alongside Keshav Aggarwal, Sumit Kumar, Wing Hong Leung, Junxian Li, and Matthew P. Young—released a landmark result: *Level aspect subconvexity for GL(2) × GL(2) L-functions* [cite: 17, 21, 22].

### 5.1 The Subconvexity Problem for Rankin-Selberg L-functions
Let \( f \) be a newform of prime level \( p \) with any central character \( \chi \pmod p \), and let \( g \) be a fixed cusp form or Eisenstein series for \( SL_2(\mathbb{Z}) \). The goal is to obtain a subconvex bound for the Rankin-Selberg L-function \( L(1/2, f \otimes g) \) as \( p \to \infty \) [cite: 6, 22, 23].

Previously, this problem was addressed using the moment method by Michel, Harcos-Michel, and Michel-Venkatesh [cite: 6, 23]. However, the moment method inherently relies on embedding the target L-function into a carefully chosen family and analyzing the spectral decomposition. If a suitable family cannot be constructed, or if the spectral theory is too unwieldy, the moment method fails.

### 5.2 The Delta-Symbol Innovation
To circumvent the limitations of the moment method, Ritabrata Munshi pioneered the application of the delta-symbol method for subconvexity around 2010. The delta method dispenses with averaging over a family, addressing subconvexity for individual L-functions [cite: 21].

The classical delta-symbol method, refined from the work of Duke, Friedlander, and Iwaniec (DFI, 1997), provides an exact analytic expansion for the Kronecker delta function [cite: 24, 25]. By injecting this smooth delta symbol into a shifted convolution sum associated with the approximate functional equation of \( L(1/2, f \otimes g) \), researchers can separate the oscillating variables and extract cancellation [cite: 25].

### 5.3 The \( p^{1/2 - 1/524 + \epsilon} \) Bound
Kwan and his collaborators pushed the delta-symbol method to its absolute limits for the GL(2) × GL(2) case. They proved the uniform subconvexity bound:
\[ L(1/2, f \otimes g) \ll p^{1/2 - 1/524 + \epsilon} \]
where the implied constant depends on \( g \), \( \epsilon \), and the archimedean parameters of \( f \) [cite: 22].

This strictly improves upon the best-known results by Harcos and Michel [cite: 21, 22]. Crucially, their method ultimately relies on highly non-trivial bounds for bilinear sums of Kloosterman fractions, drawing upon innovations by Bettin and Chandee [cite: 21, 22]. 

The most remarkable feature of this 2024 proof is that **it does not rely on the spectral theory of automorphic forms** [cite: 21, 23]. Previous delta-method approaches heavily invoked the spectral decomposition of \( L^2 \) to bound off-diagonal terms. By relying entirely on GL(1) harmonic analysis and bilinear Kloosterman estimates, Kwan et al.'s argument works equally well for holomorphic cusp forms of small weights, including weight 1 forms, which are notoriously difficult to capture using classical spectral theory [cite: 21].

---

## 6. Voronoi Formulas, Character Sums, and Braverman-Kazhdan Theory

Beyond explicit moment evaluations and subconvexity bounds, the underlying mechanism of L-function transformations relies heavily on summation formulas. A generalized Voronoi formula serves as a dual analog to the Poisson summation formula for Fourier coefficients of automorphic forms [cite: 3, 26].

### 6.1 The New Spectral Proof of the Voronoi Formula
In their 2025 publication *Character sum, reciprocity and Voronoi formula* (Bulletin of the London Mathematical Society), Kwan and Wing Hong Leung present a new spectral proof of the Voronoi formula for classical modular forms [cite: 17, 19, 27].

Historically, Voronoi formulas for GL(n) were proven via the analytic properties of Rankin-Selberg convolutions or through the Godement-Jacquet adelic theory (as executed by Ichino and Templier) [cite: 3, 26]. Kwan and Leung take a completely novel approach by discovering a four-variable character sum identity that acts as a twisted, non-archimedean counterpart to Weber's integrals for Bessel functions [cite: 27]. Combining this identity with ideas from Venkatesh's thesis, they bypass the traditional ad hoc geometric trace methods, establishing a clean, spectral derivation of the Voronoi summation formula [cite: 27]. 

This 4-variable identity is an essential arithmetic input that mirrors the symmetries of the functional equation of automorphic L-functions [cite: 27, 28]. The ability to structurally map non-archimedean character sums to classical Bessel integrals highlights the deep symmetries captured by the recent wave of spectral reciprocity research.

### 6.2 The Braverman-Kazhdan Program and Non-abelian Fourier Transforms
These character sum identities and spectral reciprocities tie directly into the "Beyond Endoscopy" and Braverman-Kazhdan programs [cite: 28]. The Braverman-Kazhdan conjecture posits that for any split reductive group \( G \) and a representation \( \rho \) of its Langlands dual group, one can construct a generalized Schwartz space \( \mathcal{S}_\rho(G(F)) \) and a non-abelian Fourier transform (a "Hankel transform") that yields the functional equation of the associated automorphic L-function—generalizing Tate's thesis and Godement-Jacquet theory [cite: 28, 29].

Kwan and Leung (2024) have investigated the role of spectral reciprocity within this program. They proved summation formulas for spaces of test functions on the zero locus of quadratic forms, explicitly building these functions from the Whittaker coefficients of automorphic representations on GL(n) [cite: 29]. For \( G = SL_2 \) or \( GL_2 \), they provided explicit formulas for the nonabelian Fourier kernels conjectured by Braverman and Kazhdan, as well as explicit formulas for the orbital Hankel transform [cite: 29]. 

Furthermore, to count integral quaternion zeros, Kwan and Leung introduced a **new, nonabelian delta symbol method**, obtaining asymptotics at height \( X \) of the form \( c X^{4n-8} + O(X^{3n+\epsilon}) \) [cite: 28]. This nonabelian delta method is of independent interest and represents a significant structural leap over the classical Duke-Friedlander-Iwaniec delta symbol.

---

## 7. Parallel Advancements: GSpin x GL Groups

While Kwan's work has radically optimized the GL(n) × GL(m) theory via period integrals and delta methods, the explicit construction of Rankin-Selberg integrals for other reductive groups continues concurrently. 

In a significant September 2024 preprint, Mahdi Asgari, James W. Cogdell, and Freydoon Shahidi successfully constructed an integral representation for the global Rankin-Selberg partial L-function \( L(s, \pi \times \tau) \), where \( \pi \) is an irreducible globally generic cuspidal automorphic representation of a general spin group (GSpin) over an arbitrary number field, and \( \tau \) is a representation of a general linear group [cite: 30]. 

This achievement generalizes the foundational works of Gelbart, Piatetski-Shapiro, Rallis, Ginzburg, Soudry, and Kaplan [cite: 30]. The construction considers all ranks and encompasses both even and odd general spin groups, including their quasi-split forms [cite: 30]. The extraction of explicit facts concerning the location of poles of \( L(s, \pi \times \tau) \) in this work yields crucial consequences for describing the image of the Langlands functorial transfer from general spin groups to general linear groups [cite: 30]. This demonstrates that the Rankin-Selberg unfolding machinery—though highly complex—remains functionally indispensable for establishing Langlands functoriality where spectral reciprocity formulas are not yet available.

---

## 8. Summary of Methodological Shifts in GL(n) x GL(m) Theory

To fully appreciate the gravity of the 2024-2025 developments, it is useful to contrast the traditional methodologies with Kwan's contemporary framework:

| Feature | Classical/Traditional Approach | Kwan's Modern Framework (2024-2025) |
| :--- | :--- | :--- |
| **Moment Evaluation** | Approximate functional equations, Kuznetsov trace formula, Voronoi summation (e.g., Conrey-Iwaniec 2000). [cite: 7] | **Period Integral Method**: Evaluates period integrals in multiple ways. Completely avoids Kuznetsov/Voronoi. [cite: 4] |
| **Motohashi's Identity** | Proved via intricate Kloosterman sum manipulations. Spectral inversion historically incomplete. [cite: 7, 9] | Exact spectral inversion achieved for GL(3) × GL(2) vs GL(4) × GL(1) using GL(3) Whittaker functions. [cite: 7] |
| **Main Terms of GL(2) 3rd Moment** | Found only the diagonal term. [cite: 7] | Discovered and proved all 8 predicted off-diagonal main terms via new Mellin-Barnes identities. [cite: 7] |
| **Subconvexity Bounding** | Relied on embedding into spectral families (moment method) or spectral theory inside the delta method. [cite: 6, 23] | **Refined Delta-Symbol Method**: Relies *only* on GL(1) harmonic analysis and bilinear Kloosterman fractions. Applies to weight 1 forms. [cite: 21, 22] |
| **Voronoi Formulas** | Adelic derivation (Ichino-Templier) or complex Rankin-Selberg analysis. [cite: 3, 26] | Spectral derivation using a novel 4-variable character sum identity (non-archimedean Weber integral). [cite: 27] |

## 9. Conclusion and Future Directions

The integration of spectral reciprocity, period integrals, and refined delta-symbol methods by Chung-Hang Kwan and his collaborators in 2024 and 2025 has effectively solved several of the most technically demanding problems in the analytic theory of GL(n) × GL(m) L-functions. 

By avoiding the restrictive and highly complex global trace formulas (Kuznetsov and Voronoi) in favor of the more geometrically natural period integral method, Kwan has generalized the exact Motohashi identities to higher-rank groups (GL(3) and GL(4)) [cite: 4, 16]. This has not only validated the intricate predictions of the CFKRS moment conjectures (uncovering all 8 main terms for the cubic moment) but has also provided robust new formulas for twisted moments and generalized functional equations [cite: 7]. 

Simultaneously, the joint development of a spectrally-independent delta-symbol method has pushed subconvexity bounds for GL(2) × GL(2) to \( p^{1/2 - 1/524 + \epsilon} \), setting a new standard for level-aspect analytic bounds [cite: 22]. Coupled with breakthroughs in the Braverman-Kazhdan program via nonabelian Fourier kernels [cite: 28, 29] and the parallel Rankin-Selberg constructions for GSpin groups by Asgari et al. [cite: 30], the current era of analytic number theory is undergoing a rapid, structural renaissance.

Future research will likely focus on extending Kwan's period integral framework to even higher rank groups, applying the nonabelian delta method to generalized counting problems, and fully establishing the Braverman-Kazhdan Schwartz spaces over Archimedean fields to construct a universal, geometry-first approach to L-function functional equations.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXuZUPz3xRhfpZiSqpEuUF5zWfbdsIErlVtq93_qUge4Hf9K35ys6wKIQjybxMJWhvwRPTZei7WGuvXSjLCHw23WFmCG7aa5TLXfGgL4spR_x4XL6nopI1e2xeX9J-WQ9t8sFd6QRmHcQ5rti7Nc06)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7-E8m5GSlKulL45_7cAqUMoI3a3Izv946JOs9czwrNB-CULoBBo_FgGw7FjFXwNQzSJpHXDVyatyJPAQOG3GHFpROESgXgrh6LfMICC34_VU58qyShY3nbIPl9d_5dyD9da3LxmfV0WjBXC0QxWXFALS244cRZwyW4euRCy4jw1EqYA==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaZSRFah8cO8z6_x2jLk05GMCcafE3O7PgPS0FtKXtJR6rkQRrUb-BoJb57matoD5SzEjtHcYLJMqjuzHLhAYJn6kVEHsLTMoXAdoc0U5KZtQYcjrD9f2HTSgyYYILsP5wq7WytjS_47Td3bldBi-KajgrspIoGPVd9tETuVCJpcAWcOQ-wQ==)
4. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjaDImm-Xu9CYENCKAuVRjV2NpTKziqhkIRxv82n86u0f9pGuJ0HN0PEsEe-XY7KJox2kVaCuTz1T9tEpRPYB-AV5bkSr8-2X5BA0GN_Y4bhqTN0RXAx9NY57sIdn0wvJDVRLET3oNTOs=)
5. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE992M8As6u9gsbpmqY8Emks9mo29oWCrmExUcUuUra8_f1llwD1pjZXKT4QbWkyCeNAoeUP3Ewkm9RICSlL5LBfmd3lcwWC43-4r3t2VrDNiIL_lNlt7vDUWh6_CdnlGBPOE1om44TXZ4w-vGq)
6. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3ao3o3wyRxQPEaRFyd7Jt-PrPxeQ2yIKyvh9n7vrbmqXIMLwry3PFWxsjNbnIeBrSLJL-r7oONtXPBrfE9LxRFEM7mnmHMmc9qYWMmsbWd_mnDOlnXYiiKLpcRk8WefIjBHHli_E=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxaPi_cpNn2uG0tJ7tAWklSRUHXTzBX8rB4B8tqCTxhL0NS7rqikJ4Ys4J1hZKNtKhudhJREsfmW3JZ7_s8MpEyzmngbI9zTptKRWA2181HCdGjbJy)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGexxkUmssPD5BfNkuFpUo0lrcBBeY_tLE0rPR1wFVHk7T6O9fmnEuKxJy1l9SOqnK-LNrhAiEx_R0G75qbAiCEKGWzihQ-OJPYxtRsZB6j75SMJPesw3eEcDTwYV36BqOH1CYymUjbCXeccXkMQUtL63p5XAX6oaFnDnjeR6A=)
9. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhznxKpV19aqoQ7PUqtLApbjvtv5SUeKPFUK0EmqNb0ePxlmFx0-qe9YQiCAjLAdSQB03f19IqzhV83KZMJcbB3ZKlM0AnW6WjayxF063e588kgzwwWgOWjNb4YtaOTkuqqA6kBZq9PrU=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEndSAbd9kLBOiZfvzTh4X2MoVGDu5ij7b3LYtF_Mqx49gWTBWsZ5exytaxU0-0sp6KMuAa-g7iAMWzQbNwpnxRKvlvBU5_1u-L8zlUv4_bXibR-tBi)
11. [uab.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRCRXRRFUNozzG35J80vDQGbqEGubK_2F5zMpOm8AODB0NAEeoX_xsnnBfCXhn_HSPeJ9GOsQ6YsMg-5ipGm9_fU8LJ20ht-HDLvoFuEDwTLuS4xeZYDB6dDUvgLBT8Rw30SQJLd6fU6xFcajArKAaFdA_yaoe5W4pMiL9veUs)
12. [raco.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHVIxfIoo5eezztbC7JPPcj8WJKLQ2g8Z2dP-YTYn7GTDzFDM_LV9Nrp2870vKieEk0h-qI8Bk_s_YrfMIcOe1zGRTBsvpmUNBqYkSgvvxcmLS1jicK-2ZayqpDw1JPvG7LiqLtmGuD4_sLViFXRpuDluhLBr4h3hGv9rC_MPcRA==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpwj2YQv6llZchQoDieOQbfsHdUJpzr8NtN3wiwI4L8jsO80Y0TLP92jHLSaePaObjsdU845icSVnN_4UzgCDpDn9SDNIKBAsmZ1n7tCNNEsaKX5lXTQ7U8GmGOntpcLV8r-p4PXjKvq6q_GNjBMq2iIxrT7PdI3eMQcOVbtYRZrurWw6gv4c7FKJEmi3JICBAJbgiqLg0JrKJuHa2qVaG1xhTZqRHcsk=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBwIyAApvd89w2HvQRa4Ps498tjzqwJpUTOIjihb9pg3Z_1Wdi-DN3dEyFU8qorpxhg9X2QEPtOGTyU08qo8EBf4ygz44b6p1VTHr2tXEF_Rqmsf3q4SbotGDYLsC08-R1i5Vu_f3RQKW9fZO3KcNM_h1CQuA0NyEh076i1kFV0qJE4rcOAtPVDFZjeeMGswLHpfTW6tT1lI0NaA==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUU4P4kCnxrebgu9WEVsa_8oY80Es4tsu3LMEj95CO7DitiVHXXNvx66xJy8T14OOFdTfyMRRtpt2SkdTku6MCTN2cs8NKobM-AhqsdwWDksGtWEuf2NiiHdcYDkCZtLKsBPy59rgsTbabEtbPd6r32q2haKXakl75rFcoYp9A5Fa3yShEHcyWqgw5ZDNOzaVq9Yq9qCQfCmroPwk=)
16. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOenD2YKqH8cAloaP1sI6yopgDmYE2qx1YI7W3PBoz70WcDDlMlLecrN4NFJpGOw8tK2l4oLlQeVI6IKC0cC7Yx9Nb5lqVZRE5C5q_yAcmppfdPsSCtzOZJjWKOEg=)
17. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVaf6RnKL7At4L35mIW4r-9woDS0pU8IVewkNGSoB5KTB1IZZtprR07S7-tEOTi_JejRatxi4SbpfOdy1oZuq9JqVVoV5DaKCw6IOfkPgyTKMfdxkHjCT0kb9KzeiAaqrSsrwvpMfn_iXBSRrUE-9A)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERfu0RUAZwhrp5qvW2GnVOGMgawcpkcQtDy1jJvpTFoZnjb-C8PlHvww6eGcE_Oe5FLO1AbQuiX7U3hGPk-A5mrjdCcP4CVK0lhgtzqlwN9Y_o3HEPAW_4euYsps_nsA1CFs2ZGFq8RbZlLUtcBr2Nh59StZtWaAn4yG8ma8qvsKgLdp_vRHXP2XZutsWDL7-T0jg9Qbiay3z0geGY-Fxn7cpOeZxrAqSO7Mo=)
19. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2SscxBMlly7hv0De-aTCNhoOgf7Ibk1nMaGY_ypksPyJwFazcqh6SuVEu0ienK0-ejyiERkOzvY7p9Gi30rhmr9V96RtSCy4k3TArFAnFuKSJKRABoU4nyRC3NA4D58keCH96JNAcef5PGA0HxubdpA==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWOpx5PAdcrXKFUVRJ56pqQSlO4T0El0_WNqAVSuX1lwZmCMaUbtKGjTDBpeW9qheXIrVU-kZYjDohB1u3aYFX84Ptm-D8tAoy_GlEzy_Iwfo5S8CR)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZ9FHVx9oudAxWcNGNOzsmCR3VxalZLq-0GyLlc6W6jEYIRPNf5679sPo3cHenMgGxawYcW2tMx34i2kH_hhz4Aq9wX66Myu7aIVdCtGoXZ-eWKL4gL3Z3)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJqU9uLzHpgZwT41ZPKu4WXs3Nx0n84kNjmkwXlyku2XtuFxuibJBaoNnHwnjcdYt24f623XT56lFfxdYTH_Hwu8sYKsDoGpDyL6cNttd6JEnVmmvb)
23. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHelvpoddXJtBESdRXHqBEznsDK71sd4ixInhwgZWhatOzq0O-2ZwtMblqtatk7ftQ_hDPgZ6C7J1plczCkbiUASqQoIchAjerMS77gkCruDGtpjRa8SmHhpd5zgZjRx1Ymase9fZoXEobvTTIRF-swXcziI9U=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOxHTXUEHnEOhzWw1deWIGupHsBR7IrXIqQbTklMMJvQh1QGaMIMvGvhJAY8ttfNHLd7-uiFM9f9xWhAKCe3RqKbVxis-8HAld7f1vCAGkx5ZTFmv21BKjdShp_O3A9_GqtLqmZeXoBF9cq36yWTHvwMvdDrIZXstA6Vu-5fHfggqZsw==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdOSWVFuafx8cPTtVQx8jem-2csOVB5mkF4JvFWpzdb3tjDkq6lAaCo07NylaiHGTMw5TU24t-5sZlee4uJJ62olgvwFwO0L8xAcj9-g1WVWh7Iis5)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4wy7P8RDL6i8OVq7G_EXgacbhZOquaWkqmzLccgLt-FrGazSnPilk1URO3bx2_g07U_ZwJnia3mTGmiGdF9tpEfegwlPArfcPGJpBZYjHdzwCZoT0_Z--KIDJ0XRpnn8R6kxay-gc9f2Dmhi4o3YqLcfsiHJRmGJyVcX6CHj62iSvtcsaF8mnOjYdThOBrF36cKZSYYon)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFylxVnlGGXd_hrmrys_0Z7k3UvnHiLtx79rYX2MnwHutb1VfzWVZ3p4eYUDp5e_MURBQLfrHAGBvv8-4QdNr066HXJYiiW5KMa4IxUjyP3Vh4zUmws)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3BG9emr3YI3QEyj79WuqeHKfIzFilxuFS3QAPZ4vYQxOeNoh72KDugRjE4i7JBAtTnHaavS8y6whnfKPC5H3dw75-y_qFHbOSTHLq1r-nJzcRT-ARBuvs0rkKNpiuvipJodMrVhNA1W7k9s_oX1fcHkdN3s168yHjeyKThc0qHHL2pZ3gLVL7mxDNnK0Ka5dMoS9M)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHX_l7ENc1KNUIi6XHeZBHdA-NjlQRXN36QA_dqPAXpDJXdw0J2H777n5iD8B8Ch6Y5F7ezuoMe83BfJm_4CKqOFCCS9TN_EU-DKFvh8eC2jLyibblkv5h0encveVJJrT1l6-ktufSnDOZqSKFpmiQgsIWlsXfcKoWb8-s1NU8QH_BMqq1uP1UPAeeZwRwJESUF-r0N6XzCaSBKdkkoRBCX7GU6DAD3NVOJH4krVwxAGmjVn_5zxK7IqydioR1JcVGGHyC5)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEAMF5Vv949OOYNA0xuGPAVc-wqumo-EO0izFwcNuTl5f_jTwqdF17TXv9JqA5FeU-ZRC2N0diZ8vAbU3m_eSEmkV-EoKncqSSvdTLhA6Pxfqput9_)

