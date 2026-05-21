# T#82 Geometry of tensor network manifolds (Quantum Fisher info)

**Pythia queue id:** 119
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMQ01QYXFMZklmZVctOFlQNDRyYzRBNBIXTENNUGFxTGZJZmVXLThZUDQ0cmM0QTQ
**Elapsed:** 370s
**Completed at:** 2026-05-21T15:28:30.933975+00:00

---

# T#82: Geometry of Tensor Network Manifolds and Quantum Fisher Information

### Leading Paragraph
The study of quantum many-body systems and quantum information theory has been revolutionized by the application of Tensor Networks (TNs), which provide a computationally tractable framework for representing highly entangled quantum states. This report provides an exhaustive analysis of the geometry of tensor network manifolds, with a specialized focus on the Quantum Fisher Information (QFI) and its computation within these geometric spaces. The notation "T#82" serves as a dual signifier in this context: it references the precise tracking of individual tensor nodes (e.g., "Tensor #82") within large-scale computational graphs (such as TensorFlow Lite and deep tensor neural networks) [cite: 1, 2], while simultaneously aligning with theoretical identifiers in the literature concerning the metrological limits of quantum states. 

**Key Points:**
*   **Geometric Foundations:** Tensor networks, including Matrix Product States (MPS), Tree Tensor Networks (TTNS), and the Multiscale Entanglement Renormalization Ansatz (MERA), parameterize complex quantum states by forming a substantially reduced set of effective degrees of freedom. These parameter spaces can be rigorously understood as algebraic varieties and Riemannian manifolds [cite: 3, 4].
*   **Topological Closedness:** Research demonstrates that while MPS with open boundary conditions and TTNS form Zariski-closed sets, translation-invariant MPS with periodic boundary conditions and Projected Entangled-Pair States (PEPS) are generally not closed. This geometric property is crucial for algorithmic stability, as non-closedness can lead to divergent tensor elements during optimization [cite: 3, 5].
*   **Riemannian Optimization:** The optimization of isometric tensor networks (such as MERA and canonical MPS) is naturally formulated on Stiefel and Grassmann manifolds. Exploiting this quotient geometry allows for the application of advanced Riemannian gradient descent and quasi-Newton methods, circumventing issues like barren plateaus [cite: 4, 6].
*   **Quantum Fisher Information:** QFI is a geometric measure of state distinguishability that plays a central role in quantum metrology, forming the basis of the Bures metric [cite: 7]. For mixed states, the traditional eigendecomposition required to compute QFI becomes intractable for large systems.
*   **Lyapunov Integration Breakthrough:** Recent novel approaches evaluate the QFI for mixed many-body states by framing the Symmetric Logarithmic Derivative (SLD) through Lyapunov integrals. This allows the integration to be efficiently computed using Matrix Product Operators (MPO), drastically reducing computational complexity [cite: 7, 8].

While the exact nature of quantum advantage remains a heavily researched and debated topic, the intersection of differential geometry, information geometry, and tensor networks provides a robust mathematical framework that appears highly promising for scaling quantum simulation and sensing. The evidence leans toward tensor network manifolds being an indispensable tool for characterizing both ground-state physics and non-equilibrium dynamics.

## 1. Introduction to Tensor Network States

The theoretical modeling of quantum many-body systems suffers from the so-called "curse of dimensionality," where the dimension of the Hilbert space grows exponentially with the number of constituent particles [cite: 5]. For a system of $N$ particles, each with a local Hilbert space of dimension $d$, the total state vector resides in a space of dimension $d^N$. Tensor Network States (TNS) provide a powerful approach to circumvent this exponential bottleneck by parameterizing the many-body wave function as a network of partially contracted tensors [cite: 3, 5].

### 1.1 The Architecture of Tensor Networks
In a tensor network, the global quantum state is broken down into local tensors associated with the physical sites (particles) of the system. These tensors contain "physical indices," which correspond to the observable degrees of freedom, and "virtual indices" (or "bond indices"), which are contracted to capture the entanglement between different regions of the system [cite: 5]. The size of these virtual indices is bounded by a parameter known as the "bond dimension," often denoted by $D$, $m$, or $\chi$. The bond dimension effectively controls the maximum amount of entanglement that the tensor network can accurately represent [cite: 9]. 

By capping the bond dimension, the number of parameters required to describe the state is reduced from $O(d^N)$ to a polynomial scaling, such as $O(N d D^2)$ for a standard one-dimensional Matrix Product State (MPS) [cite: 10]. Prominent classes of tensor networks include:
*   **Matrix Product States (MPS):** Used primarily for 1D systems, capturing states with area-law entanglement entropy [cite: 4, 11].
*   **Tree Tensor Networks (TTNS):** Loop-free architectures where tensors are arranged in a hierarchical tree. These are particularly useful for representing systems with hierarchical correlation structures and certain 2D models [cite: 5].
*   **Projected Entangled-Pair States (PEPS):** The natural generalization of MPS to 2D and 3D lattices, capable of representing volume-law and 2D area-law entanglement [cite: 5, 12].
*   **Multiscale Entanglement Renormalization Ansatz (MERA):** A tensor network explicitly designed to implement real-space renormalization group transformations, exceptionally well-suited for capturing scale-invariant critical systems [cite: 5].

### 1.2 Computational Graphs and the T#82 Identifier
When tensor networks are implemented in modern computational frameworks—whether for quantum simulation or classical machine learning—the underlying code compiles the network into a directed acyclic computational graph. In software environments like TensorFlow Lite or specialized tensor contraction libraries, individual tensors and operations are assigned sequential identifiers [cite: 1, 2]. 

For instance, debugging a deeply nested tensor network or a deep tensor neural network often requires analyzing specific nodes, such as "T#82" (Tensor #82), to monitor the flow of bond dimensions, identify rank-deficiencies, or resolve shape mismatches during contraction operations [cite: 1, 2]. In a complex graph, T#82 might represent an intermediate Matrix Product Operator (MPO) contraction or a specific isometric restriction on a Stiefel manifold constraint [cite: 2, 11]. While T#82 is a literal graph index in classical debugging, the precise tracking of individual tensor topologies underscores the mathematical necessity of understanding the strict geometrical boundaries of the entire tensor manifold.

## 2. Information Geometry and the Quantum Fisher Information

Information geometry provides a geometric framework for understanding the structure of statistical models by treating probability distributions—and, by extension, quantum states—as points on a differentiable manifold [cite: 13, 14]. This geometric perspective is crucial for understanding model expressivity, algorithmic optimization, and the fundamental bounds of parameter estimation [cite: 13, 15].

### 2.1 Classical and Quantum Fisher Information
In classical statistics, a parameterized family of probability distributions $p(x|\theta)$ forms a statistical manifold. The natural Riemannian metric on this manifold is the Fisher Information Matrix (FIM), whose entries are defined as:
\[ I(\theta)_{ij} = E_{\theta} \left[ \left( \frac{\partial}{\partial \theta_i} \log p(x|\theta) \right) \left( \frac{\partial}{\partial \theta_j} \log p(x|\theta) \right) \right] \]
This metric governs the distinguishability of adjacent distributions [cite: 13].

The Quantum Fisher Information (QFI) is the quantum analogue of the classical Fisher Information. Instead of characterizing the sensitivity of a classical probability distribution to parameter changes, the QFI characterizes the sensitivity of a parameterized quantum state $\rho(\theta)$ to infinitesimal changes in $\theta$ [cite: 16, 17]. In quantum metrology, the QFI is linked to the fundamental limit on the precision of parameter estimation through the quantum Cramér-Rao bound, which states that the variance of any unbiased estimator $\hat{\theta}$ is bounded by the inverse of the QFI [cite: 7].

### 2.2 The Bures Metric and Fubini-Study Metric
The geometry of quantum states is defined by distance measures such as the Bures metric (for mixed states) and the quantum Fubini-Study metric (which simplifies the geometry for pure states) [cite: 13, 14]. The QFI is mathematically proportional to the Bures metric [cite: 7]. When the statistical manifold is pulled back to a complex projective Hilbert space for pure states, the Fisher information metric corresponds exactly to the Fubini-Study metric [cite: 14].

For a parameterized pure quantum state $|\psi(\theta)\rangle$, the Quantum Fisher Information Matrix (QFIM) elements can be derived from the Hessian of the state distance expansion [cite: 16]. Specifically, the matrix elements can be approximated via finite differences or exact analytical derivatives, and the QFIM is seen as the real part of the complex quantum geometric tensor [cite: 16]. 

### 2.3 The Symmetric Logarithmic Derivative (SLD)
To generalize QFI to mixed quantum states $\rho$, one must define the Symmetric Logarithmic Derivative (SLD). The SLD, denoted as $L_\theta$, is a Hermitian operator defined implicitly by the Lyapunov-like equation:
\[ \frac{\partial \rho(\theta)}{\partial \theta} = \frac{1}{2} \left( L_\theta \rho(\theta) + \rho(\theta) L_\theta \right) \]
Once the SLD is found, the QFI is computed as $\mathcal{F}(\theta) = \text{Tr}(\rho(\theta) L_\theta^2)$ [cite: 7, 18]. 

The evaluation of the SLD is a major bottleneck in quantum information geometry. Solving the implicit equation typically requires the exact eigendecomposition of the density matrix $\rho(\theta)$ [cite: 7]. Because the dimension of $\rho$ grows exponentially with the number of qubits, this standard numerical procedure quickly becomes impractical for large many-body systems, making the exact calculation of QFI notoriously difficult due to its non-linear mathematical form [cite: 7, 15].

## 3. Algebraic and Differential Geometry of Tensor Network States

To rigorously optimize quantum states and calculate geometric properties like the QFI, the sets of Tensor Network States (TNS) must be understood as geometric objects. Research into the algebraic geometry of TNS seeks to answer fundamental questions about the structure, closure, and topological properties of these parameterized sets [cite: 5, 19].

### 3.1 Zariski Closure and the Geometry of Varieties
A critical question in the mathematical physics of tensor networks, initially posed by L. Grasedyck, is whether the set of tensor network states associated with a given graph and bond dimension is Zariski closed [cite: 12]. Closedness is vital for algorithmic stability. When optimizing an energy functional (like the Rayleigh quotient for a Hamiltonian) over a TNS manifold, if the infimum of the functional lies on the boundary of the set but outside the set itself, the optimization algorithm will attempt to approach this boundary point. This causes the individual tensor elements to diverge to infinity, destabilizing the algorithm [cite: 3, 5].

The geometric complexity of these sets has been extensively analyzed by Landsberg, Qi, Ye, and independently by Barthel, Lu, and Friesecke [cite: 5, 9]. Their findings dictate that:
*   **Closed Sets:** Sets of MPS with Open Boundary Conditions (OBC) and Tree Tensor Network States (TTNS) are always closed [cite: 3, 5]. The closedness of OBC-MPS is intimately related to the geometry of direct products of Grassmann manifolds [cite: 5]. Similarly, the MERA states form closed sets because their definition relies on strictly isometric tensors [cite: 5].
*   **Non-Closed Sets:** Conversely, sets of translation-invariant MPS with Periodic Boundary Conditions (PBC), heterogeneous MPS with PBC, and PEPS are generally *not* closed [cite: 3, 5]. For instance, it has been mathematically proven that when the tensor network graph forms a cycle (loop) of length $N \ge 3$, the resulting space of states is not closed [cite: 9, 19]. 

This distinction implies that algorithms operating on PEPS or PBC-MPS must employ regularization techniques to prevent tensor element divergence when the target state lies in the closure of the manifold but not within the manifold itself [cite: 3, 5]. 

### 3.2 Grassmann and Stiefel Manifolds in Isometric Networks
Many advanced tensor networks rely heavily on isometric tensors to maintain computational tractability and physical constraints (such as unitarity in quantum circuits). An isometric tensor $W$ satisfies the condition $W^\dagger W = I$ [cite: 4, 20]. The geometry of these isometric tensors forms distinct, well-studied Riemannian manifolds.

The set of all complex isometric matrices of a fixed size forms a Riemannian manifold known as the **complex Stiefel manifold** [cite: 11]. Optimization directly on the Stiefel manifold ensures that the isometric constraints are strictly preserved without the need for computationally expensive penalty terms or Lagrange multipliers [cite: 11, 21].

Furthermore, in many tensor network architectures (like canonical MPS or MERA), there is a gauge freedom. A gauge transformation $U$ can be applied to the virtual bonds without changing the physical quantum state [cite: 4]. When we consider equivalence classes of isometric tensors up to these unitary gauge transformations, the quotient manifold $St(n, p) / U(p)$ defines the **Grassmann manifold** [cite: 4]. The geometry of Grassmann and Stiefel manifolds serves as the foundation for modern gradient-based optimization on tensor networks [cite: 4, 20].

## 4. Riemannian Optimization on Tensor Network Manifolds

Exploiting the intrinsic differential geometry of tensor network manifolds leads to optimization algorithms that are vastly superior to flat-space Euclidean optimization. Variational optimization problems for quantum many-body systems can be translated into the language of continuous optimization on smooth manifolds [cite: 4, 6].

### 4.1 Gradient Descent and Retractions
In Riemannian optimization, the gradient of a cost function (such as the expectation value of a Hamiltonian, $E = \langle \psi | H | \psi \rangle$) is computed within the tangent space of the manifold at the current point [cite: 4]. For the Stiefel manifold, the tangent space consists of matrices that preserve the isometric constraint to first order [cite: 4, 11].

Because moving along a straight line in the tangent space will generally pull the state off the curved manifold, a mathematical mapping called a **retraction** is required. A retraction maps a tangent vector back onto the manifold [cite: 4, 11]. For isometric tensors, common retractions include the polar decomposition or the Cayley transform [cite: 11]. This allows the implementation of sophisticated state-of-the-art algorithms—such as nonlinear conjugate gradient descent and quasi-Newton methods (e.g., L-BFGS)—directly on the tensor network manifolds [cite: 4, 20].

### 4.2 Application to MERA and MPS
Applying Riemannian optimization to the Multiscale Entanglement Renormalization Ansatz (MERA) and infinite Matrix Product States (iMPS) yields state-of-the-art performance, outperforming previously known optimization methods tailor-made for those specific variational classes [cite: 4, 20]. By formulating the energy minimization problem on the Cartesian product of Stiefel and Grassmann manifolds, the algorithms naturally navigate the curvature of the state space [cite: 4, 22].

Moreover, recent formal analysis has extended these differential geometry frameworks to Tree Tensor Networks (TTNs), developing efficient first- and second-order optimization algorithms that exploit the intrinsic quotient structure of TTNs [cite: 22].

### 4.3 Overcoming Barren Plateaus
A significant challenge in variational quantum algorithms and deep neural networks is the phenomenon of "barren plateaus," where the gradient variance vanishes exponentially with system size, rendering random initializations un-trainable. Notably, it has been mathematically proven that the variational optimization problems for matrix product states, tree tensor networks, and MERA are *free* of barren plateaus [cite: 6, 23]. The scaling properties of the gradient variance on these specific TNS manifolds provide an analytical guarantee for the trainability of randomly initialized tensor network states [cite: 6, 23]. 

## 5. Computing Quantum Fisher Information via Tensor Networks

As established, the exact calculation of the QFI for mixed many-body states is hindered by the necessity to compute the Symmetric Logarithmic Derivative (SLD) via eigendecomposition, which is exponentially hard [cite: 7, 15]. However, a major breakthrough was recently introduced by Wójtowicz, Huelga, Rams, and Plenio (2025), who developed a novel numerical approach that combines the concepts of Lyapunov integrals with tensor networks [cite: 7, 8].

### 5.1 The Lyapunov Integral Approach to the SLD
Instead of exact diagonalization, the SLD can be expressed as an exact integral solution to the Lyapunov equation:
\[ L_\theta = 2 \int_0^\infty e^{-\rho(\theta) x} \frac{\partial \rho(\theta)}{\partial \theta} e^{-\rho(\theta) x} dx \]
This integral form eliminates the need for matrix inversion or diagonalization [cite: 8, 24]. While directly exponentiating the density matrix $\rho(\theta)$ is still exponentially hard in the full Hilbert space, this mathematical structure is remarkably well-suited for tensor network approximations [cite: 8].

### 5.2 Tensor Network Integration
In this novel framework, the mixed quantum state $\rho(\theta)$ is encoded as a Matrix Product Operator (MPO) [cite: 7, 18]. The time-evolution operator $e^{-\rho(\theta) x}$ within the Lyapunov integral is simulated using standard time-evolution algorithms for MPOs (such as Trotter-Suzuki decomposition or Krylov subspace methods), treating $x$ as an imaginary time variable [cite: 8]. 

Because the entire calculation is executed within the tensor network formalism, the computational complexity scales polynomially rather than exponentially. The integral is evaluated numerically up to a finite upper cutoff limit, and the tensors are truncated at each step to maintain a tractable bond dimension [cite: 8, 25]. This approach requires only the elementary matrix product states algorithm for time-evolution, opening the door for broad usage and application to strongly correlated many-body systems in quantum metrology [cite: 7].

### 5.3 The TN4QM Software
To operationalize this theory, the researchers released the open-source Python library `TN4QM` (Tensor Networks for Quantum Metrology) [cite: 25, 26]. Based on the underlying `YASTN` package (which supports Abelian symmetries like $U(1)$ particle number conservation and $\mathbb{Z}_2$ parity), TN4QM evaluates the QFI using MPOs for one-dimensional open-boundary systems [cite: 25]. The software supports both the variational optimization of the SLD and the novel Lyapunov integration scheme, marking a significant step forward in applied quantum information geometry [cite: 25, 26].

## 6. Applications in Quantum Metrology and Condensed Matter

The ability to compute the QFI efficiently on tensor network manifolds has profound implications for multiple domains in physics, ranging from precision sensing to the characterization of complex phases of matter.

### 6.1 Quantum Metrology and Sensing
Quantum metrology leverages quantum entanglement to achieve measurement precisions that surpass the classical shot-noise limit. The QFI sets the ultimate bound on this precision via the Cramér-Rao bound [cite: 7]. 

For example, tensor network methods have been used to analyze the thermal state of the transverse-field Ising model to measure magnetic field amplitudes [cite: 7, 8]. By utilizing Infinite MPO (iMPO) techniques, researchers can compute the QFI directly in the thermodynamic limit (infinite particle numbers) [cite: 18, 27]. This allows for the identification of optimal probe states and optimal metrological protocols even in the presence of short-range correlated environmental noise, which was previously an inaccessible regime [cite: 18, 27].

### 6.2 Witnessing Quantum Phase Transitions and Non-Markovianity
The QFI is highly sensitive to the geometric structure of the quantum state. At a quantum phase transition, the state undergoes a macroscopic deformation in response to a microscopic change in the Hamiltonian parameter. Consequently, the QFI diverges or exhibits sharp peaks at criticality, acting as a robust witness for quantum phase transitions [cite: 7, 28]. 

Furthermore, the dissipative dynamics of QFI in open quantum systems (modeled via MPOs) can reveal non-Markovian dynamics. In regimes where classical stochastic processes fail to describe time-correlated noise (such as a qubit coupled to a bosonic bath with dephasing noise), the exact dynamics of the QFI display oscillatory behavior. These oscillations indicate an information backflow from the environment to the system, serving as a clear signature of non-Markovianity that cannot be replicated by standard Markovian Lindblad approximations [cite: 7, 28].

### 6.3 2D Open Quantum Systems and Topology
While 1D systems are effectively modeled by MPS, extending these tools to 2D has historically been challenging. However, recent algorithms based on the infinite Projected Entangled-Pair Operator (iPEPO) ansatz have found success in simulating 2D many-body open quantum systems [cite: 29]. 

Moreover, tensor network representations are highly effective for modeling intrinsically mixed-state topological phases, which exhibit nontrivial topological phenomena under strong decoherence [cite: 30]. By utilizing anyon condensation in Choi states, fixed-point tensor network representations can capture the topological order and geometric deformations inherent in these 2D quantum structures [cite: 30].

## 7. Advanced Geometries: Holography and Spin Networks

The geometric interpretation of tensor networks extends beyond the parameter space of the tensors themselves, providing deep connections to the geometry of spacetime in quantum gravity and string theory [cite: 31, 32].

### 7.1 Spin Network States and Entanglement Graphs
In Loop Quantum Gravity (LQG), space is quantized into discrete building blocks (e.g., tetrahedra), and the kinematic quantum states are represented by spin networks [cite: 32]. The entanglement structure of these many-body states can be identified directly with a tensor network graph. By mapping the intertwiner spaces and representation spins to the tensors and bond dimensions of a TN, spin networks are evaluated as superpositions of tensor networks [cite: 32]. This allows researchers to use tensor network techniques to probe the holographic features of quantum spacetime and the modeling of quantum black holes [cite: 32].

### 7.2 AdS/CFT and Discretized Bulk Geometries
The Multi-scale Entanglement Renormalization Ansatz (MERA) has been famously proposed as a discrete realization of the AdS/CFT correspondence (Anti-de Sitter/Conformal Field Theory) [cite: 33]. The hierarchical, tree-like structure of MERA constructs a discrete geometry that mimics a hyperbolic space (the bulk), whose boundary represents a scale-invariant quantum field theory [cite: 33]. 

Further research integrates $p$-adic numbers and the Bruhat-Tits tree to create a fully consistent discrete holographic bulk geometry. In this formulation, geodesics in the discrete tree graph reproduce calculations of entanglement entropy, perfectly mirroring the Ryu-Takayanagi formula from continuous AdS/CFT models [cite: 31]. Tensor networks are thus not only computational tools but fundamental geometric architectures that reflect the underlying fabric of spacetime.

## 8. Computational Paradigms: From Machine Learning to Quantum Physics

The mathematical machinery developed for quantum physics is increasingly cross-pollinating with classical machine learning [cite: 13]. The foundational architecture of probability distributions in machine learning and quantum states in quantum mechanics share the same information geometry [cite: 13].

### 8.1 Tensor Networks in Machine Learning
Tensor networks are now extensively deployed to parameterize highly complex classical machine learning models. Deep Tensor Neural Networks (DTNNs) utilize structures like TTNS and MPS classifiers [cite: 34, 35]. Unlike deep traditional neural networks that suffer from the vanishing gradient problem, tensor network classifiers mostly consist of linear elements and avoid vanishing gradients (as proven by the absence of barren plateaus) [cite: 6, 35]. 

For example, low-rank TTN classifiers with canonical polyadic (CP) rank constraints have been shown to drastically reduce parameter counts while outperforming traditional tensor-network-based methods in image classification tasks (like Fashion-MNIST) [cite: 35]. The algorithms used to backpropagate through these structures rely on the exact same differential geometry and Riemannian quotient structures developed for quantum mechanics [cite: 22].

### 8.2 The Convergence of Classical and Quantum Optimization
Whether minimizing a cost function in classical Bayesian networks, navigating the Quantum Natural Gradient (QNG) via the QFIM, or tracking a specific node like `T#82` in a TensorFlow Lite graph [cite: 1, 13], the underlying geometry remains consistent. Natural gradient descent uses the inverse of the Fisher Information Matrix (or its quantum equivalent) to precondition gradient updates. By following the steepest descent path along the curved statistical manifold—rather than Euclidean parameter space—these algorithms achieve significantly faster and more stable convergence [cite: 13].

In hybrid quantum-classical algorithms (Variational Quantum Eigensolvers), classical optimization routines directly manipulate the parameterized quantum circuits (PQCs). Understanding the topology, closedness, and Riemannian metrics of the associated tensor manifolds is what makes these modern computational paradigms viable for noisy intermediate-scale quantum (NISQ) devices [cite: 13, 36].

## 9. Conclusion

The geometry of tensor network manifolds provides a profound and unifying mathematical framework that bridges quantum many-body physics, information geometry, and computational optimization. As this report details, the parameter spaces of Tensor Network States (such as MPS, MERA, and TTNS) are not merely abstract algebraic constructs but strictly defined geometric manifolds (Stiefel and Grassmann quotient spaces) whose topological closedness governs algorithmic stability [cite: 3, 4, 5].

By leveraging Riemannian optimization on these manifolds, modern techniques can navigate complex quantum landscapes without falling victim to barren plateaus [cite: 4, 6]. Concurrently, the Quantum Fisher Information—a crucial geometric metric of state distinguishability—has seen a revolution in its calculation methodology. The integration of Lyapunov equations with Matrix Product Operators entirely sidesteps the exponential barrier of exact diagonalization, allowing for the characterization of mixed states in large-scale quantum metrology and open quantum systems [cite: 7, 8].

Ultimately, the precise mapping of tensor network geometry remains at the bleeding edge of both theoretical physics (e.g., holographic dualities and quantum phase transitions) and applied computational science (e.g., machine learning classifiers and quantum sensing). As the scale of trackable tensors (from `T#1` to `T#82` and beyond) continues to expand, the synergy between differential geometry and tensor networks will undoubtedly remain a cornerstone of next-generation quantum and classical computation.

**Sources:**
1. [tensorflow.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKsISiP2gGc__ZNtE1-SId3ibxK8xouijRdvII5tw5P1zFrsL-WvN-y5fAFplAwrBH4fWLm6no65XbJjv_LIevYBCWoUQGzb8pWcCcaG7PBa2ZgsnpB8bVMyrkXUgvHRQJsbCpaYbhGoBLkbhJxJXix7DZ)
2. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeKSpRlEV_ESA5EIL7WbD4SrAcax6M7qmktt07JR6uhP2QtIe3aZcCFDCzSG1m5t3DLvdzV_aNXOzuCPqgdL5qQJ9rfpXiaot_tVGg2T4RrbQDDuUuM0iAyp1QVyUGLCYelLXxh7Rywu8rjw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWDPpHo1OdnlnLtxLC7cvE7g0C9De668CnwHHzF1a-P1RzGB16WhB5JyxA8BvBxQ1uDguJ7U2a10-SnYKSMOJuxR__xJvTAWMvFTdx-p0Hs0XQkICY9w==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSOtLRU3OB7sgZLPZh3AB_84aCqlk8AoaJPrQCD7Y93FKfP8pQBMNR_mLCMOSiLovSsWLLEbomqAYhTTdrwsapgAmELw4JppERXJ7muag98wX3wWfr8w==)
5. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSz9qB1t5gKXP_TcRDLTRVhtQp6eGhw1WsK39zE1d52rWKsJB6U2IuggDa42X9dBLlWnGt0EcEiP6VQsHUH1iUGkQD_hvOiHLQ8P15KOYI6CFeddCu40jelHjC4vywa5I=)
6. [manyparticle.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRwRpNLxMAAWML_o_lWQH_Sw6nlMrNWinOaTcxjLF5H439jBYECPl3gW1d4F9lq5bmOmymN6U1-oPgu-qE7VIGYAch87j3aAmhquIBEsk_CsCMTKFtIwBEJsXgfRtxBgN7Y6jXlOTYTv5YUjrNBYtY9UZS81OE9DUDrtYlT0snfJdl2BXJK1cRzm05P2ZkcnSPgUvXoJqw8ow0iFpaNroV9Sn9HEEULrmMCvyYEkpLz3rggYi54GCO0SX2BEjioba8D59NMWf7M74_qalE1hTfNnYUcYMl114=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn8q50kOHuaBk607Jeb8JjQarCVM1iS0a__1jXfsz7f8WzhxZbSkri4m4kU6ixWc2kqxQ0CTS4iiWuW0tNSMvaTC09CGoDji00d1bDHoHgceeML7GmpBzfjg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgj0w16gKjyyh-FRhvBMz0V6o-UPnIHZJkcAm33v7Jqk_HxmOgcBSTnXBzHuNZRmuSxRgkMYSvgsEUkaLFU916h0A0HanA-3lXKyQZyi66Sd8PaQFKAw==)
9. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJnXz1s05e0QAOAY_hr5kosoNGoo_T6xIwVsQh3F-iqGyjHmmCnS8-ruN2y37_wwP2qcjuTd4pt2Yq6iLFC3noAVYYgx8wsOdkXwhGsdo15TVycZ4_JnUJUmWOutMnnN-lMV54NVR1wIupT8pDjGgbBvVHXA==)
10. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1ivBZh0JrMpoaer1jHsP_ly9RFZEENbhPX-iNbpLqLdp_B4YCf_qF0bgDSHVxTox1mjNo4oxX9ofC1qY_69PhgW9C1UmlrbTQ0Jd4dmEz7rGwemx3yBkqglSSfeCrxFoQHTfFM8__Y_2tb_9-dx1CYaNkQUyDbigo0isHG0trxKvV)
11. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPhHHrkj0wIO7gmSNlE9n93XqXVOFwqTvYkzWFm5asiMipCD0yr_w2V_ocxE5_lIP3oFWySCSZK6qMZwoctOznMMaqf_f4AGXXHxHj7-7VCuWkkILclpp4s8ELFPw5PHn5Bg==)
12. [rintonpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPJoVisQWPYtx_CWFmNnyB90tgFuWRYs1ESKT2WGWhLRyIqBYFHsLCLQdw4NSsw-gIrRqeT-6dfgW0g6z5XLcp9E2XYjIcrBweaVhG92H9qhnrVZY63hDVhUZaMl0np5Xuze1BbNerm3OuvJ0AZnxdJA==)
13. [apxml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQZXl24N0IZDqmO8jF2VahxdxkTe4U1iwziu6rvni4SYXZkmrhDcL4OVi2-2yAt-tUfn652bBjm3eBavOCwj6NzTHyCOs14jzbGbUyXOLYVDg31SuLA1g3gk-BFk5kcQ1-f90vpXR_CUSsjtYzQnthMbdDx1PHL90bLXpiCzXx0vjSKPb34GcxgJNLS7iD7pCdkkd62BS-IFYIh_SxS6Jw12Bn4XUhY5Bxu4-2DY3BLBtcZNiqUFlWCC5BzvNlQrA9YebB8YHeGg==)
14. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOvZajugKvGQSPM5R98hy1Di6DFcoH6zCwXSKO858gCeON-8qu6GZnAvNSushejuZWSPPgBoRRvL4HYZXwPapY25IsdqpMmWxK6u3XB_nQ_fiDKCp7QwfdH0nNCmJWZjZvogMJIUSOqaHf_f-X)
15. [fuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvqHpNeTnYd6pr6ohAybPrWaB5Bt9972_r6jDADnxm8WuiqxCA3Zkmiz3i8ngHUndK-l8jsu1MORxQzj6jmihJSm6jVv7IOsaRPS56Us0WkGnw4ulwXHWSjlS-tGwS-XENLG5n45z5)
16. [quair.group](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEO6jt8tDCfWIzTnU5QawoxbAjpMV9KtXBCufNIb0x9-1O31ue6u1m31JCvgw1HbSjENnEXZTvEUZC6fz58NBQYDPcWqdh8N5rCeMBJJXCCGcq2rqsuoSsCNFMGj98puE90iqgfLb0lIJo-BSLYisEXuz4RI9Eeu-B32A==)
17. [science.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBatXdB2cIshjpEk-j9mQb3dgfLXNCDB4x5LcJEvMYPQMDNjsViwo1u-fPOFvBkyRGhgtUA1sEo1oIuO5oT9v2cYuOnYiBtMsE077yJTeywwAQaqpPS6sXK52fn-nsZhjlhHt3nu8jFjCjFZAihPMiyef2YSA=)
18. [uni-hannover.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXs0ghAUAMq5HyywzUkeK9xNSgVAmfguFUm7qvogQI0U1kCWkyT5QcBfq3UU6J8wklg9R3WqFJRriSOScD9pGA24ir7Y3oFc0h-lXZGyQXP2Vb97vn8g-4MsJ_cM9Jw2oGJRWHSpVJ2excDY1_Uoyrq6C1BhPohC32Z1wvGmj0ce2kZgoItZ1wBZFA)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXJSv0Oh5Pn9uy5uqs2_5whtTjl_dxatrGOPQeTk05gKhVjxixIIrKDPaAT_qvdnDuzp6OsKJNpewY1xjCGmiYH_KlqfodhavX2C1GXHH5UNI_eDdn)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi94nF27wgjRyoZ9ikJtrH9PSzWXWHiBW9PcA9XbPgYJ6VO91sXc62zfbUnxhETDNbF39QOl-lMJIX-qUbbjmiddtPl_sr3dLQDLIiTAPCHJLkC-vUJw==)
21. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz4NDnlQuiqXbkBoWSiCXoXfMxgcgaBztbOdT4-_HIWEyE0Pvv4DLbKnIY9w5gP12qG-sIjA-JxSwoOoxHXoVUbxv3Q-d32SWfpb6gVVU8Z8zvlUIHiWXFTIUYGbVoYIpAejI=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2IcTb2fu0DHW2aVZpLxn9PqvY_8ZmWv02QUScKRm9NqYRqFiRto_jQlX0xZFiH-_JcdRE_jTPObqODNWXgk_QwjqXbVv4Zm3PZSLdYuH63ISq03djUfzIHA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbP-mojlHtv1HjlsaA1M1iqJZ_C3EPKAlv5_SiygNgIfMjkooZxp37AW3l1WqEh7uiZKoJ0zgqAfVXchx5FfKppb-Y_tQBczZEcdQseyz9lH4xXZMxNg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL6C3Szsd_rW6Btld4BaTvdZJ6P_PBWym7fCl9MY6YlTtfvB58lJYV6NL04ecKUiKNJCXJEoOZEGnDwDwsA8U-GcBYKvsXwLqOx8-hxc2YxyWFohQsKQ==)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSqkLW6mSQJP1kGZsOtpQcDhFVIl88POiH79rn0T3z2i_ihe7HVQ93EeCc-017pbKqA8TvV25PGyo3sSC34dRoO2afLIxiYvkuHs2CB6e-G6Yf4g4CG7kzvxfdObfIgWZnOPQkTCeq)
26. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeTc72BxdJXTp9KOVNGJQIYJM-eFXsoNCCsv3z_mgj2FsHFO2a8T4QF83PLskGBRutRbEvgNHb5toFMKmQA1RUMQcFrzOp-OzHMW0xCrKLaDaobZB33anm9Q==)
27. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF25Lb7-XnV7HiVk-BdrQkYTmsak7B0IM3539fpB3h5HgeaGDn3UVwh4dzqUPYHPXvRA64pLf3JX_tpltqqX0WCicTTAvrqW1xFx6JqS6XEZAo_fV-8hJq0V1zP6p69eo9GD9QQeo5N)
28. [nqsti.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH2qkdNSswneg7I4vghwnA6jXVCktFcq1YI0Sv6htisJUezrcvrQfgcYs-BTxVpd6HW_OMw4KJMA1jTiGkcSqwqlpKZ9XnQvgKTavyIWx9I2hpwiZsBuX0HdrT2Z1-oH7fDy5pewCl5Xz6X50WAOyrLnNg38svInKLyR5KTUee1Ke4uvgprhD7QiFFOghqvQyaNsOo3drltDLACeAl4llBdgyAailipGOHNk7oM6onxEZe22WySk2x2a4Hg9u9MP3C84Qq)
29. [aps.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbjP5m3A_LK_smcKf-XvDtiQcBlgZuEfp5QktpAXCZqfiKDgEdk_oeuiovQcZcaRvqTbQlWF3h_QxYenGFAdOV_kyytX91a9vXB61tO2UNE41WM4PiZfiYKfxCtQg8enbNVx13GWGoAOCb)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF9yC648guWhrQd1_U88lLErJ4yViuiu_iq8gX6hVp_WVTuDe1O4t3YdHO3Rl2DHDbzdfE5_OeYl659EI4bZr0SfKYFrzmfA-EsBZFEzFcpSYXyd6VY4ri_g==)
31. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa-zxf0kP6X40GPsa_jv0fuNIMgPxxGEOgOLwEFjeP54rnbkHlaS0ooCqUFvUa79YvRmo5L3fce_oS7FFRlJrIDgcXJ-btPPXYG5gM_DQ_5MsqIGZwd73qwETYCB6WDySF2C31WdVGsCq17sGNUUe0)
32. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVVGU2fPVfUguDGQUR6gqd8nfVLQSZB29dWz-dfcTtR6hdL2_DH-4Ho_2jGBUY2WRZFlSkatJuJ-Bcd3KlDLiMl1xIq6TlMxKGPuYEVedT4BcHi2rpVVb0QMW02wNkDeircQUEWBDopcwjWrkxr1q3-MoeCkKwVu6l8WCZIsha0D7ILS-1NRAvXMfK-ObZXDQ_Lj4me3zAxKvLjtWM-rw=)
33. [mtak.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJMJSHwo7UfjYiUOnjQKoRU2eaWnbs8EFaH1qo6xW60wUKvovmsKGNM1f3kfrQeMYhNrxSNh18MLpu8xx5WH1S0PwzzfutZT8RsFh2BWLzJRDLxgjNCYbA0Cy3eBYmCgtKOQW5)
34. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDKUXHZ2GyP1fRLfO9_uTttqj7TzCIo83zXXLESN_3X68LHnM3TP3P0j-BcJAsMxXF3HX-5QLvKNqtOhnQahukGpfWvFUy4RliSKXsiZvPkIcahjQT1Lr2AoirQ9ky54N3tcftMzI=)
35. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnfSGQaQemTr1dodE6pHgbctsdBvowNkfgeiSAJprgBRxVTQs4ZmUABErEhVOGGJKaCiGHLDx89Xd0TvCzOPWFbDe1MfjfsslrKyNZmyfZBhBPyRPDl36JQg-eS6kZWBquLuP5SxAKBXsTMFiRweH8xwSZE26wg4PJHfM=)
36. [ibm.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFJRQ50Ebu50bkWS9uyfrrjkmlvwdoUwVRBaLnCT70Z-wAD51wCh2ePGI97HXEc5l4bUalwmbzLkC88DxFDpDdf-733eJDRkK6gQfFX8W8iwz7keVqbmVaRgDn-vwGiTVZha9JO3rLz4rXbI-dSO6Cy_JxVlC9x7uOFpnobKmfLD3CRRgts2SHlAmu78VnQTtdMnvp5PWKldpB7zjgpybc7zOVpURCDYpIzQ==)

