# T#66 Z-eigenvalue distribution (random tensor spectral theory)

**Pythia queue id:** 107
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc5aDRQYXB5dktiMkktc0FQX0xibHNBYxIXOWg0UGFweXZLYjJJLXNBUF9MYmxzQWM
**Elapsed:** 311s
**Completed at:** 2026-05-21T15:09:34.472911+00:00

---

# Spectral Theory of Random Tensors: Z-Eigenvalue Distributions and Melonic Dominance

**Key Points:**
*   **Fundamental Transition from Matrices to Tensors:** While the spectral theory of random matrices (Random Matrix Theory, RMT) is a cornerstone of modern mathematical physics, generalizing these concepts to multidimensional arrays (tensors) introduces severe nonlinearities. Research has established that tensors do not possess a single, universally applicable notion of an eigenvalue, leading to specialized definitions such as Z-eigenvalues.
*   **The T#66 Milestone and Melonic Dominance:** A critical benchmark in this field—frequently denoted by its reference identifier T#66, corresponding to O. Evnin’s publication in *Letters in Mathematical Physics*, Volume 111, Article 66 (2021)—demonstrates that the largest eigenvalues of large random tensors are governed by "melonic" graphs. This indicates a dominant scaling behavior that mirrors generalized models in quantum gravity and statistical mechanics.
*   **Generalizations of the Wigner Semicircle Law:** R. Gurau and collaborators have successfully formulated a tensor resolvent trace that extends Wigner's semicircle law to symmetric tensors, yielding spectral densities characterized by Fuss-Catalan numbers. However, it is important to note that this generalized spectral density is defined on average over the ensemble and does not necessarily constitute a pointwise probability measure for any individual deterministic tensor.
*   **Quantum Field Theoretic (QFT) Methods:** Unraveling the exact distributions of tensor eigenvalues has been revolutionized by translating the problem into 0-dimensional Quantum Field Theories. By representing the Z-eigenvalue equations as critical points of a potential and expressing associated Hessian determinants via fermionic and bosonic integrals, researchers have obtained exact analytical formulas (e.g., involving confluent hypergeometric functions) for the signed and genuine eigenvalue distributions.

The study of random tensors has emerged as a rich generalization of random matrices, heavily motivated by theoretical physics, quantum gravity, and high-dimensional data analysis [cite: 1, 2]. Unlike matrices, the eigenvectors and eigenvalues of tensors are defined through systems of multivariable polynomial equations, meaning their properties are far more intricate [cite: 1, 3]. Among the most relevant definitions is the "Z-eigenvalue," which imposes a spherical normalization constraint on real or complex eigenvectors [cite: 4, 5]. This report provides an exhaustive, highly detailed examination of random tensor spectral theory, bridging exact QFT partition function methodologies, the statistical limits of spiked tensor models, the T#66 melonic large-$N$ limits, and the ongoing algorithmic quest to compute these distributions efficiently.

***

## Introduction to Random Tensor Spectral Theory

Random Matrix Theory (RMT) was largely pioneered by Eugene Wigner in the 1950s to model the excitation spectra of heavy nuclei, under the assumption that the Hamiltonian could be approximated as a large symmetric matrix with random, independent entries [cite: 2, 6]. The hallmark of RMT is Wigner's semicircle law, which dictates that as the dimension $N$ of a Gaussian orthogonal ensemble (GOE) matrix approaches infinity, its empirical eigenvalue distribution converges to a semicircular profile [cite: 7, 8]. Beyond the global density of states, RMT provides universal insights into the spacing between eigenvalues, known as the Wigner surmise, and characterizes phase transitions in disordered systems and complex networks [cite: 6, 7, 9]. 

The transition from a two-dimensional matrix $M \in \mathbb{R}^{N \times N}$ to a $p$-order tensor $T \in (\mathbb{R}^N)^{\otimes p}$ (for $p \ge 3$) represents a colossal leap in algebraic and geometric complexity [cite: 10]. Random tensors have profound applications: they represent the interactions in structural glasses (the $p$-spin spherical model), are the primary variables in tensor models of quantum gravity and string theory, and act as high-dimensional data arrays in machine learning (tensor PCA) [cite: 2, 11, 12].

However, tensors lack the straightforward spectral decomposition that symmetric matrices enjoy [cite: 13, 14]. In matrices, the eigenvalue equation $Mx = \lambda x$ is linear. For a $p$-order symmetric tensor $T$, the standard contraction with $p-1$ copies of a vector $x$ results in an inhomogeneous system of polynomial equations of degree $p-1$ [cite: 4, 15]. Consequently, the number of isolated eigenpairs $(x, \lambda)$ is no longer bound by the dimension $N$, but typically scales exponentially with $N$ [cite: 1, 14]. To make sense of the "spectrum" of a random tensor, modern research focuses on finding the distribution of these eigenvalues, characterizing their largest values (the edge of the spectrum), and understanding the analytical properties of their large-$N$ limits [cite: 3, 5, 16].

## Algebraic and Geometric Definitions of Tensor Eigenvalues

To understand the spectral distribution of random tensors, one must first establish what an eigenvalue is in this higher-order regime. Several relevant definitions exist, but the "Z-eigenvalue" is the most prominent for symmetric real tensors due to its direct connection to variational calculus and multilinear forms [cite: 1, 4].

### The Z-Eigenvalue and Z-Eigenvector

For a symmetric real-valued tensor $T$ of order $p$ and dimension $N$, the action of $T$ on a vector $x \in \mathbb{R}^N$ is defined via multilinear contraction. Let $T[x]^{p-1}$ denote a vector in $\mathbb{R}^N$ whose $i$-th component is given by:
\[ (T[x]^{p-1})_i = \sum_{i_2, \dots, i_p = 1}^N T_{i, i_2, \dots, i_p} x_{i_2} \dots x_{i_p} \]
A scalar $\lambda \in \mathbb{R}$ and a non-zero vector $x \in \mathbb{R}^N$ are called an eigenpair of $T$ if they satisfy the tensor eigenvalue equation:
\[ T[x]^{p-1} = \lambda x \]
Because this equation is homogeneous of degree $p-1$ on the left and degree $1$ on the right, scaling $x$ by a constant $c$ alters the eigenvalue. To fix this gauge freedom, different normalization constraints are imposed [cite: 4]. 

When the Euclidean norm of $x$ is constrained to unity ($\|x\|_2 = 1$), the corresponding scalar $\lambda$ is referred to as a **Z-eigenvalue**, and $x$ is a **Z-eigenvector** [cite: 4, 17]. The prefix "Z" stems from the terminology introduced by L. Qi and others in the mid-2000s, distinguishing it from "H-eigenvalues" which utilize an $L_p$ norm constraint instead [cite: 4, 17, 18]. 

The Z-eigenvalue problem is deeply connected to variational optimization. For a symmetric tensor $T$, finding the Z-eigenvalues is mathematically equivalent to finding the critical points of the Rayleigh quotient (or the multilinear form) on the unit hypersphere:
\[ \text{Maximize/Minimize } \quad V(x) = T[x]^p = \sum_{i_1, \dots, i_p} T_{i_1, \dots, i_p} x_{i_1} \dots x_{i_p} \]
subject to the constraint $\sum_i x_i^2 = 1$ [cite: 15, 19]. The Lagrange multiplier for this constraint precisely corresponds to the Z-eigenvalue $\lambda$.

### Number of Eigenvalues and Complex Landscapes

For an $N \times N$ matrix, the Fundamental Theorem of Algebra guarantees $N$ eigenvalues (counting multiplicities). For a tensor of order $p=3$ and size $N$, the algebraic geometry of the polynomial equations dictates that there are generically $\frac{(p-1)^N - 1}{p-2}$ complex eigenpairs [cite: 15]. For a third-order tensor, this evaluates to $2^N - 1$ isolated eigenvalues [cite: 15]. 

Because there are exponentially many critical points on the unit sphere, evaluating the overall "distribution" of these eigenvalues becomes a problem of statistical mechanics [cite: 20]. As Paul Breiding established, the real Z-eigenvalues of a symmetric Gaussian tensor can be identified with the critical points of a random Kostlan polynomial on the unit sphere, leading to an exact formula for the *expected number* of real Z-eigenvalues [cite: 3, 15].

## T#66: Melonic Dominance and the Largest Eigenvalue

The user's query specifically highlights "T#66", which in the taxonomy of mathematical physics literature maps directly to a seminal paper by Oleg Evnin titled *"Melonic dominance and the largest eigenvalue of a large random tensor"*, published in *Letters in Mathematical Physics* 111, Article 66 (2021) [cite: 3, 13, 14, 18, 21].

This work serves to bridge the physics of random tensor models (originally developed to study zero-dimensional spacetime and quantum gravity) with the numerical linear algebra concept of the spectral edge. The spectral edge—the largest Z-eigenvalue of the random tensor—determines the ground state energy of generalized spin-glass systems (like the spherical $p$-spin model) and the injective norm of random multipartite quantum states [cite: 2, 16].

### The $1/N$ Expansion and Melonic Graphs

In Random Matrix Theory, computing the expected values of polynomial invariants (traces) relies on 't Hooft's $1/N$ topological expansion, where planar Feynman diagrams dominate the large-$N$ limit [cite: 8, 12]. For random tensors, the topological expansion is vastly more complex, governed by higher-dimensional simplicial structures and "colored" combinatorial graphs [cite: 12, 22]. 

Razvan Gurau and collaborators famously proved that the leading-order graphs in the large-$N$ expansion of random tensor models are not just planar, but specifically "melonic" graphs [cite: 12, 22]. A melonic graph is a specialized, recursive tree-like structure of "hourglass" diagrams that maximizes the number of internal faces for a given number of vertices [cite: 13, 14]. 

In Evnin's paper [cite: 13], the largest eigenvalue of a large random tensor is analyzed through this lens. If $C$ is a Gaussian random tensor of order $q$ (note: physics literature often uses $q$ or $p$ interchangeably for the order), the invariant observables are traces constructed by contracting the indices of multiple copies of $C$ [cite: 14]. Evnin systematically investigates the homogeneous polynomials of the tensor components and evaluates the expectations $\langle \lambda^k \rangle$ where $\lambda$ is the largest Z-eigenvalue. By categorizing the branching levels of the $(p, p')$-hourglasses, he shows that the combinatorial sum is overwhelmingly dominated by the melonic configurations [cite: 13]. 

The critical result of this framework is the precise scaling and asymptotic upper bound of the largest eigenvalue (the spectral edge) [cite: 13, 23]. Evnin demonstrated that the asymptotic properties of the largest eigenvalue can be deterministically extracted because the "melonic dominance" strictly restricts the quantum fluctuations in the $N \to \infty$ limit [cite: 3, 13]. The variance of the distribution becomes highly concentrated, a hallmark of random tensor limits [cite: 8, 14].

## Generalizing the Wigner Semicircle Law to Tensors

Wigner's semicircle law describes the bulk distribution of eigenvalues for matrices. A highly non-trivial question is: *Does a universal shape exist for the bulk distribution of the Z-eigenvalues of a Gaussian random tensor?*

This question was affirmatively tackled by Razvan Gurau, who extended the concept of the Wigner semicircle law to real symmetric tensors of order $p \ge 3$ [cite: 10, 15, 22]. To do so, a new analytical tool had to be defined, as the traditional matrix resolvent trace, $\frac{1}{N} \text{Tr}(H - zI)^{-1}$, does not map linearly to tensors [cite: 10, 24].

### The Tensor Resolvent and the Spectral Density

Gurau defined a "tensor resolvent" which acts as an integral representation for a specific class of tensor invariants. The singular locus of this resolvent perfectly encodes the real Z-eigenvalues of the tensor [cite: 10]. 

When analyzing a real symmetric Gaussian tensor in the large $N$ limit, Gurau showed that the expected resolvent exhibits a finite branch cut in the complex plane [cite: 10]. The discontinuity across this cut defines the **"spectral density"**, representing the generalized eigenvalue distribution [cite: 10].

Remarkably, the moments of this generalized distribution do not yield the standard Catalan numbers found in RMT (which generate the semicircle) [cite: 8, 25]. Instead, the moments of the contracted $p$-order random tensor converge toward the **Fuss-Catalan numbers** [cite: 1]. The Fuss-Catalan numbers natively describe the enumeration of $p$-ary trees (the specific geometric objects that arise from melonic graph contractions at order $p$) [cite: 1]. Thus, Wigner's theorem for random tensors manifests as a dilated Wigner-Gurau law governed by Fuss-Catalan combinatorics [cite: 1].

### Nuances of the Pointwise Probability Measure

While Gurau's result represents a massive leap in random tensor spectral theory, it sparked mathematical scrutiny regarding the interpretation of the "spectral density." In a subsequent critique, it was demonstrated that Gurau's spectral density, derived from the tensor resolvent trace, is valid *only on average* across the entire Gaussian ensemble [cite: 25].

For matrices, the empirical spectral density of an *individual* large matrix almost surely converges to the Wigner semicircle (self-averaging) [cite: 8]. For tensors, researchers constructed deterministic individual tensors such that the coefficients of the series expansion of Gurau's resolvent trace do not correspond to the moment sequence of any valid probability measure [cite: 25]. Consequently, Gurau's spectral density is not defined pointwise (as a positive probability measure) for all individual symmetric tensors [cite: 25]. It functions strictly as a global ensemble average or potentially as a signed measure in the deterministic case [cite: 25].

## Quantum Field Theoretic Formulations of Z-Eigenvalue Distributions

The most explicit analytical computations of Z-eigenvalue distributions for random tensors have emerged not from combinatorics alone, but from zero-dimensional Quantum Field Theory (QFT). This methodology, primarily developed and refined by Naoki Sasakura, involves translating the counting of tensor eigenvectors into partition functions of field theories featuring fermionic and bosonic fields with quartic (four-fermi) interactions [cite: 2, 18, 26].

### Genuine vs. Signed Eigenvalue Distributions

For an order-3 real symmetric Gaussian tensor $C_{abc}$, the unnormalized critical points satisfy:
\[ C_{abc} v_b v_c = v_a \]
where $v_a \in \mathbb{R}$ [cite: 27]. The density of these solutions across an ensemble of random tensors $C$ can be written using a Dirac delta function:
\[ \rho(v) = \frac{1}{\mathcal{Z}_C} \int dC \ e^{-\alpha C^2} \sum_{i=1}^{\#\text{sol}(C)} \delta^{(N)}(v - v^{(i)}) \]
where the integration is over all independent components of $C$ with a Gaussian weight $\exp(-\alpha C^2)$, and $v^{(i)}$ are the real solutions [cite: 27]. 

Using the standard properties of the delta function under a change of variables, this sum can be rewritten by inserting the Jacobian determinant of the transformation, which is the absolute value of the Hessian matrix at the critical point:
\[ \rho(v) = \left\langle |\det M(v, C)| \, \delta^{(N)}(v_a - C_{abc}v_b v_c) \right\rangle_C \]
Here, the matrix $M_{ab} = \delta_{ab} - 2C_{abc} v_c$ is the Hessian [cite: 27]. Because $\rho(v)$ computes the absolute number of solutions, it is termed the **genuine distribution** [cite: 16, 27]. Once $\rho(v)$ is found, the proper Z-eigenvalue distribution $\rho_{\text{eigenvalue}}(\zeta)$ is obtained simply by mapping $\zeta = 1/|v|$ and integrating out the angular degrees of freedom [cite: 5, 21].

However, analytically performing the ensemble average over the non-analytic absolute value $|\det M|$ is notoriously difficult [cite: 5]. To circumvent this, Sasakura introduced the **signed distribution**, denoted $\tilde{\rho}(v)$, which drops the absolute value:
\[ \tilde{\rho}(v) = \left\langle \det M(v, C) \, \delta^{(N)}(v_a - C_{abc}v_b v_c) \right\rangle_C \]
In this signed distribution, each real tensor eigenvector contributes with a weight of $+1$ or $-1$, depending strictly on the sign of the determinant of its associated Hessian matrix [cite: 3, 18]. While $\tilde{\rho}(v)$ is distinct from the genuine distribution in the bulk, the two distributions heavily coincide at the "edge" of the spectrum (the largest eigenvalues), because the Hessian is overwhelmingly positive-definite for the most extreme critical points [cite: 23, 27]. Furthermore, the signed distribution contains rich topological significance: viewing the Rayleigh quotient as a random Morse function, the signed summation over critical points calculates a form of the Euler characteristic [cite: 3].

### The Four-Fermi QFT Partition Function

The brilliance of the signed distribution is that $\det M(v, C)$ can be elegantly represented using Grassmann (fermionic) variables [cite: 5]. Using the formula for fermionic integrals, the determinant of the $N \times N$ matrix $M$ is:
\[ \det M = \int d\bar{\psi} d\psi \ e^{\bar{\psi}_a M_{ab} \psi_b} \]
where $\bar{\psi}, \psi$ are anticommuting Grassmann numbers [cite: 5]. 

Simultaneously, the delta function $\delta^{(N)}(v_a - C_{abc}v_b v_c)$ can be exponentiated using purely imaginary auxiliary bosonic fields or standard integration techniques. Since the tensor components $C_{abc}$ appear linearly in the arguments of the exponentials, the Gaussian integration over $C$ can be performed exactly [cite: 20].

After integrating out the random tensor $C$, one is left with an effective 0-dimensional QFT described by a partition function:
\[ \tilde{\rho}(v) \propto \int d\bar{\psi} d\psi \, d\bar{\phi} d\phi \ e^{S_{\text{eff}}(v, \psi, \phi)} \]
where $S_{\text{eff}}$ contains quadratic terms and precisely **quartic interactions** (four-fermi interactions) such as $(\bar{\psi} \psi)^2$ and mixed bosonic-fermionic interactions [cite: 5, 18, 23, 26]. 

This procedure is completely general and has been successfully applied across different Lie-group invariances, including $O(N, \mathbb{R})$ for real symmetric tensors, $O(N, \mathbb{C})$ for complex symmetric, and $U(N, \mathbb{C})$ for general complex random tensors [cite: 23, 28]. The QFT method allows the exact calculation of the signed distribution at finite $N$ [cite: 23]. 

### Exact Solutions via Confluent Hypergeometric Functions

For the $O(N, \mathbb{R})$ real symmetric tensor of order 3, Sasakura successfully integrated the QFT exactly. By decomposing the fermionic fields into components parallel and transverse to the vector $v$, the four-fermi interactions miraculously decouple [cite: 2, 20]. The transverse fermionic partition function maps onto standard solvable integrals. 

The resulting exact formula for the signed Z-eigenvector distribution is expressed elegantly in terms of $U(a, b, z)$, the **confluent hypergeometric function of the second kind** (which is closely related to Hermite polynomials) [cite: 3, 5, 18, 20]. Because the distribution $\tilde{\rho}(v)$ exhibits $O(N)$ symmetry, it depends only on the norm $|v|$ [cite: 3]. Converting to the Z-eigenvalue parameter $h = 1/|v|$, the signed eigenvalue distribution $\tilde{\eta}(h)$ takes the form:
\[ \tilde{\eta}(h) = \tilde{\rho}(1/h) \, S_{N-1} \, h^{-N-1} \]
where $S_{N-1}$ is the surface area of the unit $N$-dimensional hypersphere [cite: 3, 5]. This exact formula preserves characteristic oscillatory behavior at finite $N$, which has been tightly confirmed against numerical Monte Carlo simulations utilizing polynomial system solvers [cite: 5, 18, 20]. 

## Universality and the Large-$N$ Limit

While finite-$N$ formulas are mathematically beautiful, the statistical physics of random tensors—akin to string theory and complex systems—is primarily interested in the thermodynamic limit where $N \to \infty$ [cite: 3, 18]. 

To handle the large-$N$ limit of these QFTs, one typically employs the **Schwinger-Dyson equations** or saddle-point approximations [cite: 5, 26, 27]. The Schwinger-Dyson equations enforce self-consistency on the two-point Green's functions of the interacting fields. Under these approximations, researchers observed a striking **large-$N$ universality** across diverse tensor ensembles [cite: 28].

For complex, complex symmetric, real symmetric, and real antisymmetric random tensors of order $p$, the large-$N$ asymptotic forms of the Z-eigenvalue distributions universally scale as:
\[ \exp \left( N B \, h_p(z_c^2 / z^2) + o(N) \right) \]
where $h_p(\cdot)$ is a master function dependent only on the tensor order $p$, while $B$ and the critical phase transition point $z_c$ act as ensemble-dependent constants [cite: 28]. The value $z_c$ marks the emergence of the spectral edge, matching the ground-state values computed using melonic dominance limits [cite: 23, 28].

### Outliers, Deviations, and Phase Transitions

Recent literature has expanded this framework to models that are not purely Gaussian centered at zero, but feature a deterministic "background" or "signal" tensor with random Gaussian deviations (noise) [cite: 16, 26]. These are equivalent to the "spiked" random tensor models [cite: 10, 11].

By introducing a variance parameter for the noise, QFT methods and resolvent frameworks reveal multiple critical phase transitions. As the noise variance decreases (or signal increases), two critical values emerge [cite: 16]:
1.  **First Critical Point:** An "outlier" eigenvalue escapes from the bulk continuous spectrum (the generalized Wigner semicircle) [cite: 16]. This precisely mirrors the Baik-Ben Arous-Péché (BBP) transition seen in RMT [cite: 24].
2.  **Second Critical Point:** The outlier merges with the largest bulk eigenvalue, inducing a transition where they both move into the complex plane (if strictly real symmetric systems are perturbed) [cite: 16]. 

These findings set the theoretical groundwork for defining the "pseudospectrum" of random tensors based strictly on Z-eigenvalues, tracking how the spectrum morphs under deterministic deformations [cite: 16].

## Spiked Tensor Models and Algorithmic Thresholds

The theoretical derivations of the Z-eigenvalue spectral edge are highly relevant to data science and machine learning via the "Spiked Tensor Model" [cite: 11, 19]. 

In a spiked tensor model, one observes a tensor $Y \in (\mathbb{R}^N)^{\otimes p}$ which is the sum of a rank-one "spike" (a signal) and a random Gaussian noise tensor $T$:
\[ Y = \lambda v^{\otimes p} + T \]
where $v$ is a deterministic unit vector, and $\lambda$ is the signal-to-noise ratio [cite: 11, 24]. The fundamental goal of tensor PCA is to recover the spike $v$ given $Y$.

As established by Gurau's expected resolvent studies [cite: 10], the expected spectral density undergoes a sharp transition at a specific threshold of $\lambda$ [cite: 10]. For symmetric rank-one models with Gaussian noise, studying the random matrices that arise from the $(p-2)$-times contraction of the tensor (i.e., contracting $Y \cdot (v)^{p-2}$) reveals that the spectrum possesses a "bulk" obeying a semicircle law, and a single isolated spike that moves away from the bulk toward the local maximum eigenvalue [cite: 11].

### The Information-Computation Gap

Spiked tensor models present a fascinating phenomenon absent in standard RMT: an information-computation gap [cite: 24].
*   **Information-Theoretic Limit:** An ideal estimator can detect the spike (achieving strictly positive correlation with $v$) if $\lambda > O(1)$ [cite: 24]. This limit is inherently tied to the largest Z-eigenvalue of the pure noise tensor $T$. Once $\lambda$ exceeds the spectral edge of the noise, the global maximum of the Z-eigenvalue Rayleigh quotient shifts toward the spike $v$ [cite: 11].
*   **Computational Limit:** While the spike exists mathematically at $\lambda = O(1)$, finding it is NP-hard. No known polynomial-time algorithm can recover the spike unless the signal is immensely stronger, specifically $\lambda \ge \mathcal{O}(N^{(p-2)/4})$ [cite: 24]. 

### Algorithms: SS-HOPM and Dynamical Systems

To compute the largest Z-eigenvalues and their corresponding eigenvectors in practice, researchers rely on iterative algorithms. The most famous is the **Shifted Symmetric Higher-Order Power Method (SS-HOPM)** [cite: 4, 19]. 

For a matrix, the power method involves repeatedly multiplying the matrix by a vector. For a tensor $T$, one iterates the contraction $x_{k+1} = T[x_k]^{p-1}$, followed by normalization [cite: 11]. However, because the tensor eigenvalue problem is non-convex, the standard power method is notoriously slow, fails to converge, or oscillates [cite: 17, 19]. SS-HOPM introduces a shift parameter to enforce monotonicity of the Rayleigh quotient, guaranteeing convergence to a local Z-eigenvalue [cite: 19].

Modern research has cast these iterative methods as continuous-time dynamical systems:
\[ \frac{dx}{dt} = T[x]^{p-1} - \|x\|_2^{p-2} x \]
When this system evolves, any stable attractor $x$ satisfies the Z-eigenvalue condition $T[x]^{p-1} = \lambda x$ [cite: 4]. The convergence rate of this system is governed by the second dominant eigenvalue of the contracted matrix $T[x]^{p-2}$ [cite: 4, 17]. Recently, advanced extrapolation techniques (like Nesterov momentum, forming the ES-SHOPM and NS-SHOPM) have been developed to accelerate this notoriously slow convergence for massive tensors [cite: 19]. 

Interestingly, these optimization landscapes—full of local minima and saddle points corresponding to the exponentially many Z-eigenvalues—share mathematical geometry with the loss landscapes of deep neural networks. In fact, data-driven emergence of convolutional structures in initially fully-connected neural networks has been linked to the higher-order tensor decomposition of the input data's correlations [cite: 29]. The localized "receptive fields" form as the network learns to isolate the largest Z-eigenvalues of the input's higher-order non-Gaussian statistic tensor [cite: 29].

## Hierarchical Tensors and Tensor Networks

As the order $p$ and dimension $N$ grow, the $N^p$ entries of a full random tensor become computationally intractable to store or process. To navigate this, the fields of physics and numerical analysis employ Tensor Networks and the Hierarchical Tucker (HT) format [cite: 30, 31]. 

The set of tensors with a fixed tree dimension $T$ and hierarchical rank $k$, denoted $\mathcal{H}\mathcal{T}_k$, forms a smooth quotient manifold [cite: 30]. Algorithms can approximate time-varying or random tensors by integrating a gradient flow strictly along the tangent space of this manifold [cite: 30]. In quantum mechanics, similar structured "random tensor networks" (like random unitary circuits) are used to study operator spreading, entanglement growth, and the Out-of-Time-Order Correlator (OTOC) [cite: 31]. The statistical bounds on the largest eigenvalues derived in T#66 [cite: 13] act as universal constraints on the entanglement entropy and partition function weights within these higher-dimensional hierarchical structures.

## Conclusion

The spectral theory of random tensors is a vibrant, mathematically rigorous discipline bridging theoretical physics, combinatorics, and high-dimensional statistics. The study of Z-eigenvalue distributions reveals that while tensor spaces lack the strict linearity of matrix spaces, they harbor profound universal geometries. 

From the $1/N$ expansion and melonic dominance analyzed by Evnin in T#66 [cite: 13, 14], to Gurau's Fuss-Catalan generalization of Wigner's semicircle [cite: 1, 10], the structure of the tensor spectrum is fundamentally unique. Crucially, the utilization of 0D QFT partition functions by Sasakura and others has allowed for exact representations of signed Z-eigenvalue distributions, circumventing algebraic intractability using the elegant mechanics of fermionic integrals and confluent hypergeometric functions [cite: 5, 20, 26].

As research continues, particularly mapping the spectral edge in spiked tensor models [cite: 11] and developing accelerated algorithms like NS-SHOPM [cite: 19], the insights drawn from random tensor Z-eigenvalues will remain pivotal. They provide the keys to bounding the capacities of complex systems—from uncovering hidden clusters in blockchains [cite: 32] to defining the energetic ground states of quantum spin glasses [cite: 2]. The QFT framework, robust and highly adaptable [cite: 23], ensures that the exploration of tensor spectra will remain an exceptionally productive frontier in theoretical and mathematical physics.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmlT2pRXlKniRn3nlojf33clNx1vpFc0dmwSfqPmssawiLa8ATGVNpvkbQw4wYRIcz4v4OayzhqzhlKDPo69mkqj_4Z3-jfcbPLhtlzd8rKX2D_OI8zw==)
2. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ7psYhhja5dEsuNEWEevY7b8l__qEunHzZnAewt_ZLSp_Xz2bqB9AaK0SjQtmAoCUPDm3zSlueRaWpcoywxUMTSpQhPtgOt0u4gX0jkpnpkprdrc-N_jKQTf-SZxduTfwbeujEpx2_VOBt0t3k6y1kVpOfRilFQvO8gaij1ciW5n32VO3mz6zug==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN4BrNjR6gBokuNQovdYQhaE-qOpNRy98wGWbwMW06korR9PIawM0-wcOq8uDRVHBRemPi7hPOoB6fLratY7foDlPs9dLSnCnAP0BRF1CTSF4HSmNGjw==)
4. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh76C1zzyPj-VLvlkUlJgoLJ6Hiy16TXU0ngkXlXNlaxKE8tqRgd4iFrggBtbtdGufjd2LCPlGScFW-h6SZmH0OOYw84Qo0zusA9pjJc2o9rLVp3jz7RhtLAhMiOnqqBal-gmNBdeghCfsZxn1a2k2cQTnoTd9C_xPnxt1ZRlvWUt6LNsqfUMhFgLFFq_kxrbnURcLvMDljnYp4lvAIDl7AWhTaZXLrGv4K51CDQ==)
5. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBBmoqr6448Hdz8DIP8VAdWlmlHC2j-pkPlxaUNOKnAgOTwd8YVFdDf-AikkgiPWWsYuUXZW0bNINWHE0zhp1u9d-cV6OVI5rMKzxfKoGxL9ooZtEvnamT_X6XGg2vUd2d-xR2LJDAFzdozKZSfifMZpDMnOShUYxonaice_5igQ0k4KUPpnqiZQ==)
6. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElIoX7GCt6VSm6kLeb_H4NHdShAP8GV8kchUcMCnBA3pzpxzSkTHJSb8t9Hqrq89tq2bEOFIf8f8FMQjE99Xp0-35rkby13UCLtkRjtIo35VkahCoiFRq2k9GK-hohNHvOTmHbb8FLqdl-9YGs)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHth7lr1VZ_QHtF-lmgiUyykuIQaHI1qpSEBdxRi3pqAb7Fs9oMKwglcmVP0GuZv8Lk0dF8ZKAEIdM_TK80l9AQiryH1ZTII1shqgXDCaPJtmREyKYE33pMGD2A22f3gY3yz1kqqQVoITa6lU7l3J3fkPQ=)
8. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5UH53WN3s2PkqP887pSsdV1rEZDav8CkrJnwQAWjqdcT3cx7WS2Fs_eXcrwRGikIulLekgt_gfPUcYHSp0dGvTgNVqa37ctmtgB2RbJv5XNeDrTRGFLVw1QlecpyKF9u2-6Lyh-QJNuS6tLQjJrwiQZ-aDzAPrSCA)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnwxyMWXFmswspiVVmZOiS38JRNJi4AeKqbQcYxi84GW-02z5FIp5tEYiNFlDT1IyiGUh38Kr5lwdVtTj7NUlRCnWENy1WqPEFo_hfJIoelMjZEmjFb0FZnS6V7jCWv5GSlKwojCGwRt-R5FbLtqj4FB0AZjFFJOQX0oz9gEF2-R35XZaz_jkrKdrsivKpwScxtKvnVfqNPv8HEjxFVQ==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT8RujVcgXQuFLxWSGsu0f4MuprZ12pfqwIK_5TEldoUzYOW0lSJz765hezPkjm95TfO8VowtoUe8Zyx8_ko0-YJDYT2aabygst0W_iGuUoTTTZCwMOA==)
11. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsDOjwt3N7oYojqIPviA7e-mbhz9dvEERbuGOanlQz9QA3qbSMkDMaA6d-mVXsakGZ1JfWR2CZzBG_23uJoai-LiIXidmvoo7PErz3cYJ1xwMTqdlRq-4-w6lZI5HXQjkyzQTKZMS6HAmN6GeNig==)
12. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpt9aVwE8fmGtL_jqe8Oq9Ll7dgdsdZkN8hnj-Wv43zF4gISNVuIyLnGLYBvq891wwHUH0t_YcPcjtui7HHaHWh0eYUZ-MGwSCiMWjoKacV_nzMu1yq9fBIZwiXurHH_-GsoQjm1fqUg==)
13. [vub.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7XApGYiSotnpQtsBlU4XOOo-unMeNzY-vumR-VjkyM1AO4SuBh5wWUO7wixJsYVJaT_Tx2ckm43LaYcb90BEN05dVGdhH11CyUoYAvA_5k_nuqpUczOKocQIaEVoNZeC74JqW-fQswfHRrrA=)
14. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFt_T1-GZUUf2hygHOK6Zs9Z6Eabc0yfZZ4CuobbX6ctRI3jZaGsB73baY08KJo3hND9RzvvvzzAfU3zy58Q1AgSy6IQfZpqz69eUvpi8Okr4FfUM4E6S1eM5cPUg9zOfgu5QciVZuWI3UPMJnhPlNX1DchD9b2__lrp6Pb)
15. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1UBhqbm8fIt9e-Ctj8rHkAy_oemDmWD6_i_EaXKlsXQpTmfcWXmAiwdoNu-KDsq7-ry4gIFCmxP6r7snRloUVg4g0TQjLu7FrPHNT4lml3xNoeTF2muDcH0Eo82Dp5XJmXf8eEXNedYw9ws3OaOajphwdOYuDoMEbQaFKNK3FtZHTJHgba_HI8E5AV5E=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeCtnWTawCZTQmwWpPQauMme0qqd8a-hZMnj7EDG1P9jjaBuxJ30YwW0Reb1ZfvKEO5JskYLlecK-S55sAm7OZCK60OI3_sFBPGLOEj9Yp39hjXSoFUw==)
17. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL6u00Je2asL43azGBDVoaxnYjrfzrP31IJSocK9r7TNrMAVVtlA8F7TF6U2-dCwRRLRaqhIPlp0T7nOzHmP-fsdnWI_8vSib9lKXwl024AtBKdHNNpi3gNZ2FiYGIEjs2IwBeASIjMU1ZZL0dYf2sFZc=)
18. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuDTb-l_GLsQ6WUv_6EZsx4CcHXd9zd1NV5UPvDDK5K9RQRomqRDa7rtNeDWTRbvJhOyaEGf5CaPOcJyQNiwuYO7jCIaUCE0F1s73LLJYEocPuPwjCNPNUTgboV6jszhWv5aXo-ifY8auwWurBUI-j190wTl53OBqNqGlp6XnYviqNC9caRE3Z9yu1vr5FtmQl)
19. [ufl.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcBtPCQD6QSSDUORajyZdxF4E6zGKEzbyG9zcXGMrtt1AAU6dhmuT5Tg--YBqD4udSDCIaYgIGnhFhX79oGOq__l3kHIk71FNF4qIZJ6PLQJRXUJ2BjTDJsZr5RIAi5SNW6SajN8Da5ME7FqCvYuuL64HtL6sCmbE=)
20. [univ-lyon1.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRWVE-T2s_BpG2WJQpOUNdJS8WY2PDfuGi517tTTQuKaDpgyOvZzwfqn7B_-3FhnbWVA1WsvCexhjdIZ_YAdcw6NJloxO1jIRPuqI1YEjUMUyZkY190QIwHpQ-FwpuFpLlELlMgN_j8qGjtc7OtjSBdXKeNh_4H_s2XclG6EyL8Qj2MBMfIISKMTg=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg_gfPJMQkIF35JIVleKZwmOJjt-8qWiyDgl3djsNuA-ySzd61Z0c19zmG73sJAcSA0CObGPh-epr-i2HvpcEB86X4BjdBn2I5N2cVmbm9f0BEjbqSSg==)
22. [research.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJxN-6pzl_hwUSE7maMrinTh2JERrXrFk0x3V0r6Epms62JBmxErrVyWrpS3NwoSY9iVopYqPw6Oa5N9Y31ALUSRAipCBSAIx4Ka2VC5kxHOfRp9926DFXfw==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEspOWbXtrJPY2XDKs2fR1FsUEohoSdUw5nXIHrRKC2vHjT3Cd9AJP_QRfPUNI7NEwit8hClaxkUHKn__5iDKk6wfkKrQWXlQPZO1-_YjBnAUEnTLxJxVubJtiSGNf2QvsENnL4gR24E5JGgQsY9Sm6tn__ruu7HSAr8QMbXf18ZPHD3aiE06MwPb2o99V5MlRfmkmUnG_tbhXZKUKd2pJnpMf6D8vDtf5Ta1h7Lss=)
24. [indico.global](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zOfzsxN6bbdWk3ljU3JlIOjDHjUuwzUWQKB2ALjSIpXZxLXjWREBkBNzQ5l1bivzc5vCF9z8FkAhgJ3dHizqkdvcpub2nDqlHQuVV7n6AEO7W_nd6m1FmP_gSekaiLa0Xb1Jr7qXgyBLLdbpJMbPDTaNJVMvYiIqJKa6nNNWGHTAd7WBib2hOrCsxsW6KQlzNq2ffLuJYyDJU1gqSH9VOBrU8kpjHFAvqDQ39kSmO5U=)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5boNjCSWTHT-c_cvuBoN3CKg5SlR5fKUnJKhY6LzRwOL-Cd8CTd6Y-COrL31GhOnVBuTQZmRNTL8TO5gcUt13l03_9U3vmP4ZQWAlR88mFdQDq-muLdhIne14KgxTfLEstlJMJ6WNDxy9dsAUBMaMhcJmnE_i-93VZEQHl1lbyn6ujgKSDywDfKcTQP9A0k4DCMHQyDM7NKxJSK_m2vgap4Q0a05nRGrZ9JOI2RXowLUXUWnDMF__DgwUa1IGdM5t5TPvig==)
26. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvmOS01XKMjqK098mdL4-UxhvwrIlFUqTiDMHbFrPhUaMSTlFx0XNO66pbQeQ_YFyuOgxxBA92_QrgA32QltoE-0GBmUbhp8wWFlxfn2fwmquWj1ekMqA6vQu8EYvSOzdxcZn22ebgWDV20Cn8DjetnP_tNt_TkB8ZNWvo1UwA2M-041pOkclEQw==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFghKTh6SqBj6WV1YRpPNDe8SFNUzqTtToUTc6Ou8au2rf3QOUVoZ1uO0mtdeKiECns4E8G7QPEO83FIalY5ZTBEsDbRXLOkiPmeaA5oLoNz2h0WOZwPw==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgNJrnshb2Xl2wJUgdkwSllI0EkWBvzO_iaOGws-iQ1n7wiVtxvEKDQhnA98H-yfbl2M6H7SoiOgd4bpKXJZS4YnJBmK6Ad3BXHieuhzI0qSzoc52khrzMIm-s05Vyhr-L_pIIHskHziwHnIg_ZIeSLAPBLXDPLxa3Pos8t4UY7dQ3Of2cqPX5mV8olDs=)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUwkaXDOvKkIpNFxYY_Sxgw0p185EJVX71On379YNFlC-XyApWxexhiuKIXD1qS9dVeGUqHNLPbYLms2GVdIodrG40Nv-Xoxgxky7whquZ_DUL0BiVrdgmkJlStSVyfIEKPaF4y8y6XSCPJGHsOBnsoixHZc6JCFBi3GJoS081FKjAGX9MWwqrnIq0zMpj0KtyJi3s70eWm1kQqDWbyLXqbnnvSxTR8KLUuZab)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1uCRRtktvAAQ2S2dpi56AqCiz2uknDyF99__oTtkZaEHv2amvKdBRnHOKAcipCYADmfHsWi_CtXhebImLM5M_x8JP6Rb7aHZ7Bx6Ed3odlLcybikIlWJ9iGlXDx8T57h4WMFzveYln_hFyYP8D-BxjO9Nvb-p_-V6MICs3DV71F4Kr_FTrIN7XRJEu4J1mXHl2StZIEuDL2D6S6qq9Q==)
31. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDJsalflRN_hpYFSTsZZelGygVc4aNmX2JqfLnhNlwU5C-ftSFHxh9LSoGUFdfqdFnBk0DflxNTDbMdk7wOByCzswzewS8LgExWcyF4Wj226FZ1unpS-aYQYyqmhqzVglEl3eVaA-j-XcytHs=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMbQNMEvcU3d39oANo00V_aZkFpp-P2FJ-Xa8ansBaIKWm6nN4hIH5faL8ClnPPjm29dp5Mo6M4CZl9GRkcK0uSM8wQHUseAL_HSgTLkdXKNAd98dWMw==)

