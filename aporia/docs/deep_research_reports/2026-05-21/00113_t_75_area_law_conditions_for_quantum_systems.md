# T#75 Area law conditions for quantum systems

**Pythia queue id:** 113
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMU0VQYXB6U0V1cWIxTWtQbVlEb3dBaxIXTFNFUGFwelNFdXFiMU1rUG1ZRG93QWs
**Elapsed:** 254s
**Completed at:** 2026-05-21T15:18:04.497451+00:00

---

# T#75 Area Law Conditions for Quantum Systems

**Key Points:**
*   The **entanglement area law** dictates that for many low-energy quantum systems, the entanglement entropy between a subsystem and its environment scales with the boundary area of the subsystem, rather than its volume.
*   In one-dimensional (1D) gapped systems, the area law is rigorously proven to hold, implying that the ground state possesses highly restricted entanglement, enabling efficient classical simulation via Matrix Product States (MPS). 
*   Violations of the area law occur under several conditions, including at quantum critical points (gapless systems) which typically exhibit logarithmic corrections, and in specially constructed models (like the colored Motzkin and Fredkin models) that demonstrate exotic square-root scaling.
*   For systems at thermal equilibrium (finite temperature), an analogous area law holds when measuring quantum and classical correlations using **mutual information**, rather than von Neumann entropy (which follows a volume law due to thermal noise).
*   Highly excited states typically break the area law entirely, following a **volume law** consistent with the Eigenstate Thermalization Hypothesis (ETH), meaning typical pure states act as their own thermal baths.

The behavior of quantum many-body systems is largely governed by how quantum entanglement is distributed across their constituents. In generic, highly excited quantum states, entanglement grows extensively with the volume of a given region. However, nature exhibits a remarkable constraint at low temperatures: the ground states of typical locally interacting quantum systems do not explore the vast theoretical Hilbert space available to them. Instead, they reside in a restricted corner characterized by relatively low entanglement that scales merely with the boundary (the "area") of a subsystem. This phenomenon, known as the area law of entanglement, serves as a cornerstone of modern condensed matter physics and quantum information theory. It bridges the gap between the theoretical complexity of quantum mechanics and the practical success of computational simulation methods. Understanding the precise mathematical and physical conditions under which this law holds, as well as the conditions that trigger its violation, is a major focus of ongoing research. While rigorous mathematical proofs exist for certain one-dimensional systems and thermal states, extending these proofs to higher dimensions and exotic Hamiltonians remains one of the most significant challenges in quantum Hamiltonian complexity.

***

## 1. Introduction to Quantum Entanglement and the Area Law

The theoretical description of quantum many-body systems involves an exponentially large Hilbert space. For a system of $N$ particles, each with a local dimension $d$, the dimension of the total Hilbert space is $d^N$. This exponential growth, often referred to as the "curse of dimensionality," suggests that calculating the properties of quantum materials should be computationally intractable [cite: 1, 2]. However, physicists have successfully simulated many such systems. The resolution to this paradox is rooted in the structure of quantum entanglement within physical ground states.

### 1.1 Entanglement Entropy and Bipartitions
To quantify entanglement, we consider a composite quantum system divided into two complementary subsystems, $A$ and $B$. If the system is in a pure state $|\Psi_{AB}\rangle$, all information about the bipartite system is known. However, if an observer only has access to subsystem $A$, their knowledge is described by the **reduced density matrix** $\rho_A$, obtained by tracing out the degrees of freedom of $B$:
\[ \rho_A = \text{Tr}_B \left( |\Psi_{AB}\rangle \langle\Psi_{AB}| \right) \]
The **entropy of entanglement** (or von Neumann entropy) of subsystem $A$ is then defined as:
\[ S(\rho_A) = -\text{Tr}(\rho_A \ln \rho_A) \]
If the initial state is a simple product state ($|\Psi_{AB}\rangle = |\phi_A\rangle \otimes |\phi_B\rangle$), the reduced density matrix is pure, and $S(\rho_A) = 0$. If the subsystems are highly entangled, the reduced state is mixed, and $S(\rho_A)$ is large [cite: 1, 2, 3].

### 1.2 Volume Law vs. Area Law
For a generic state drawn randomly from the Hilbert space, the entanglement entropy follows a **volume law**; that is, $S(\rho_A) \propto V_A$, where $V_A$ is the total number of particles (or volume) of region $A$ [cite: 2, 4]. This scaling is analogous to extensive thermodynamic entropy at infinite temperature [cite: 5].

However, for the ground states of realistic quantum systems governed by local interactions, the entanglement entropy typically scales with the size of the boundary $\partial A$ separating $A$ and $B$. This is the **entanglement area law**:
\[ S(\rho_A) \propto |\partial A| \]
In one-dimensional (1D) systems, where "volume" is length $L$ and the boundary consists of just two points, the area law implies that the entanglement entropy saturates to a constant value, $S_A = O(1)$, independent of the subsystem length [cite: 1, 6]. The area law indicates that quantum correlations are primarily localized near the boundary, providing the theoretical foundation for powerful numerical techniques like the Density Matrix Renormalization Group (DMRG) and representations via Matrix Product States (MPS) [cite: 1, 3, 7].

## 2. Rigorous Proofs of the Area Law in One Dimension

For a long time, the area law was treated as a conjecture supported by numerical evidence and exact solutions of specific models. Rigorously proving the area law for general interacting quantum systems is a central problem in quantum Hamiltonian complexity. The first major breakthrough was achieved in 1D systems.

### 2.1 Hastings' Seminal Proof and the Lieb-Robinson Bound
In 2007, Matthew Hastings provided the first general, rigorous mathematical proof that the ground state of any 1D quantum spin system governed by a gapped, local Hamiltonian satisfies the area law [cite: 2, 8, 9]. A Hamiltonian is "local" if it can be written as $H = \sum_i h_i$, where each $h_i$ acts on a bounded number of neighboring spins. It is "gapped" if there is a finite, strictly positive energy difference $\Delta$ between the ground state and the first excited state in the thermodynamic limit [cite: 2, 8].

Hastings' proof relied on sophisticated analytical tools, particularly the **Lieb-Robinson bound**, which establishes a maximum finite velocity (the Lieb-Robinson velocity) for the propagation of information in non-relativistic quantum lattice models [cite: 5, 9]. By combining the Lieb-Robinson bound with Fourier analysis, Hastings showed that correlation functions in gapped systems decay exponentially with distance, which strictly bounds the entanglement entropy [cite: 8, 10]. 
However, Hastings' bound on the entanglement entropy was extremely loose, scaling exponentially with the inverse of the spectral gap $\Delta$: $S \leq e^{O(1/\Delta)}$ [cite: 8, 11]. This exponential dependence raised questions about the tightness of the bound and whether systems close to quantum criticality (where $\Delta \to 0$) could still be simulated efficiently.

### 2.2 Combinatorial Proofs and the Detectability Lemma
To improve upon Hastings' result and simplify the analytical machinery, researchers turned to combinatorial approaches. Aharonov, Arad, Landau, and Vazirani developed a new proof framework using the **Detectability Lemma (DL)** [cite: 8, 12]. The DL was initially introduced in the context of quantum gap amplification, but when applied to 1D area laws, it provided a purely combinatorial mechanism to bound ground-state correlations [cite: 8, 12].

For the special case of **frustration-free** systems—where the ground state simultaneously minimizes the energy of every individual local term $h_i$ (e.g., the AKLT model)—the combinatorial approach exponentially improved the entropy bound [cite: 6, 12]. Frustration-free systems act analogously to classical Constraint Satisfaction Problems (CSPs), where the ground state satisfies all local constraints perfectly [cite: 2].

### 2.3 Approximate Ground State Projectors (AGSPs)
The modern framework for proving area laws relies heavily on the construction of an **Approximate Ground State Projector (AGSP)** [cite: 13, 14, 15]. An AGSP is a specifically designed operator $K$ that fulfills three main criteria:
1.  **Ground Space Invariance**: It preserves the ground state exactly, i.e., $K|\Omega\rangle = |\Omega\rangle$ [cite: 13, 15].
2.  **Shrinking**: It dampens the amplitude of any state orthogonal to the ground state, $\| K|\Gamma^\perp\rangle \|^2 \leq \Delta_{shrink}$ [cite: 15, 16].
3.  **Low Entanglement Rank**: Applying the operator does not increase the entanglement across a bipartite cut by too much (bounded Schmidt rank) [cite: 15, 16].

By iteratively applying an AGSP to an initial unentangled product state, one can converge to the true ground state while strictly controlling the accumulation of entanglement [cite: 15]. 

To optimize the AGSP, researchers employ **Chebyshev polynomials**. Because Chebyshev polynomials $T_n(x)$ grow rapidly outside the range $[-1, 1]$ while remaining bounded inside, they can be utilized to aggressively suppress the high-energy spectrum of the Hamiltonian while keeping the degree of the polynomial (and thus the entanglement rank) minimal [cite: 2, 15, 16]. Using this Chebyshev-based AGSP framework, Arad, Kitaev, Landau, and Vazirani generalized the proof to all 1D gapped systems (including frustrated ones) and established a much tighter bound:
\[ S \leq O\left( \frac{\log^3 d}{\Delta} \right) \]
where $d$ is the local Hilbert space dimension and $\Delta$ is the spectral gap [cite: 14, 16]. This bound is considered nearly tight up to polynomial factors [cite: 6].

### 2.4 Infinite-Dimensional Hilbert Spaces
Standard area law proofs explicitly depend on the local dimension $d$, making them inapplicable to systems where $d \to \infty$, such as bosonic models (e.g., the Hubbard-Holstein model) and lattice gauge theories (LGTs) [cite: 17, 18]. 
Recent advancements have successfully extended the 1D area law to these infinite-dimensional systems by demonstrating the robustness of the ground state and spectral gap under the truncation of the Hilbert space. By systematically truncating the local degrees of freedom and applying the AGSP framework, researchers proved that the entanglement entropy in 1D gapped bosonic systems and LGTs remains bounded independently of the local system size, thereby justifying the use of tensor networks in these regimes [cite: 17, 18].

## 3. The Quest for Higher-Dimensional Area Laws

While the 1D case is well-understood, generalizing rigorous area law proofs to two dimensions (2D) and beyond remains one of the most prominent open questions in many-body physics [cite: 2, 8]. In 2D, the boundary of a region of linear size $L$ is a perimeter scaling as $O(L)$, so the area law posits that $S_A = O(L)$ rather than the volume $O(L^2)$ [cite: 4].

### 3.1 Challenges in 2D Systems
The difficulty in proving the 2D area law lies in the geometry of entanglement. In 1D, a bipartite cut only severs a constant number of local interactions. In 2D, a cut severs $O(L)$ interactions. If one simply applies 1D proof techniques to 2D by grouping columns of a 2D lattice into super-sites to form a 1D chain, the effective local dimension of the super-sites grows exponentially with $L$. Because existing 1D proofs have an entanglement bound that depends on $\log^3(d)$ or worse, substituting $d \to e^{O(L)}$ yields an entropy bound of $O(L^3)$ or worse, failing to produce a strict $O(L)$ area law [cite: 8, 11].

### 3.2 Proofs for Frustration-Free Locally Gapped 2D Systems
A major breakthrough occurred when Anshu, Arad, and Gosset proved the area law for a specific subset of 2D systems: **locally gapped, frustration-free spin systems** [cite: 13, 19, 20]. A system is "locally gapped" if not only the global Hamiltonian has a spectral gap, but there is also a strictly positive lower bound on the spectral gap of any subset of the local Hamiltonian terms [cite: 13].

Their proof constructed a novel 2D AGSP by taking advantage of approximation theory. They showed that the ground state projector of a 1D spin system can be approximated by a multivariate polynomial in the Hamiltonian interaction terms with a degree of $O(\sqrt{n \log(\epsilon^{-1})})$. This represents a quantum generalization of the optimal degree bound for approximating the classical boolean AND function [cite: 13, 19, 20]. By applying this optimal 1D approximation selectively in the vicinity of the boundary of a vertical bipartition on the 2D lattice, they constructed an AGSP with sufficiently low error and entanglement rank to conclusively establish the 2D area law for this restricted class of models [cite: 13, 19, 21]. 
While this is a profound step, the general 2D area law for frustrated or globally gapped (but not locally gapped) systems remains an open challenge [cite: 2].

## 4. Long-Range Interactions

The standard area law is intimately tied to the locality of interactions. However, many physical systems (such as trapped ions, Rydberg atoms, and frustrated magnets) exhibit long-range interactions that decay algebraically as $1/r^\alpha$, where $r$ is the distance between spins and $\alpha$ is a decay exponent [cite: 5]. Does the area law survive the introduction of non-local interactions?

Theoretical work indicates that the area law remains stable in long-range systems if the interactions decay sufficiently fast. By generalizing the Lieb-Robinson bound for algebraically decaying potentials, it was proven that the ground state of a $D$-dimensional lattice Hamiltonian with $1/r^\alpha$ interactions satisfies the area law if $\alpha > 2D + 2$, provided the system can be adiabatically connected to a known area-law state without closing the energy gap [cite: 5].
For systems with $\alpha$ between $D$ and $2D+2$, the long-range interactions can potentially induce violations of the area law without destroying the spectral gap, pointing toward exotic quantum phase transitions that challenge the traditional paradigm of gapped adiabatic evolution [cite: 5]. Furthermore, the entanglement entropy of any initial state undergoing time evolution under a $1/r^\alpha$ Hamiltonian cannot grow faster than the boundary area if $\alpha > D + 1$, confirming that tensor network methods remain efficient for short-time quench dynamics in these long-range systems [cite: 5].

## 5. Violations of the Area Law in Ground States

The area law is not absolute; it is a feature of specifically gapped, local phases. Violations of the area law serve as vital diagnostic signatures for exotic quantum phenomena, quantum criticality, and complex long-range entanglement structures [cite: 1, 4].

### 5.1 Gapless Systems and Conformal Field Theory
When a 1D quantum system undergoes a continuous phase transition, the spectral gap closes ($\Delta \to 0$), and the correlation length diverges [cite: 10, 22]. In these **gapless** or critical states, the area law is typically violated by a subtle logarithmic correction.

Conformal Field Theory (CFT) dictates that the entanglement entropy of a contiguous block of length $L$ in a 1D critical system scales as:
\[ S_A \propto \frac{c}{3} \ln(L) \]
where $c$ is the central charge of the underlying CFT [cite: 22, 23]. This scaling has been widely verified in critical spin chains, such as the transverse-field Ising model and the XXZ model at criticality [cite: 4, 23]. A similar logarithmic divergence occurs in free fermionic systems (such as the Fermi liquid), where the prefactor is related to the geometry and topology of the Fermi surface (a phenomenon linked to the Widom conjecture) [cite: 23, 24]. In contrast, critical bosonic systems (like a massless Klein-Gordon field) in dimensions $D > 1$ often still obey an area law [cite: 23].

### 5.2 Hyperscaling Violations in Gapless Matter
In higher-dimensional gapless matter, the scaling of entanglement can be captured by the framework of local entanglement thermodynamics using a hyper-scaling violation exponent, $\theta$. It has been shown that systems in $d$ spatial dimensions obey the area law if $\theta < d - 1$. If $\theta = d - 1$, the system violates the area law by at most a logarithmic factor ($S_A \propto L^{d-1} \ln L$), which frequently occurs in metallic states with extended Fermi surfaces [cite: 25].

### 5.3 Exotic "Square-Root" Violations: Motzkin and Fredkin Models
For decades, it was widely believed that any "physically reasonable" translationally invariant local Hamiltonian with a unique ground state could violate the area law by *at most* a logarithmic factor ($\ln L$) [cite: 4, 24]. However, recent exactly solvable models—specifically the **colored Motzkin and Fredkin spin chains**—have upended this belief.

These models feature local, frustration-free Hamiltonians with unique ground states constructed as uniform superpositions of colored random walks (Motzkin paths for integer spins, Dyck paths for half-integer spins) [cite: 26, 27]. In the colorless versions (spin-1 Motzkin, spin-1/2 Fredkin), the entanglement entropy violates the area law logarithmically, $S \propto \ln N$ [cite: 4, 27, 28]. 
However, when an internal "color" degree of freedom is introduced (such that the local spin dimension $s \geq 3/2$ or $q \geq 2$ colors), the combinatorial vastness of matching colored paths pushes the system into a phase of **supercritical entanglement** [cite: 26]. For these colored models, the entanglement entropy exhibits a massive, non-logarithmic **square-root violation** of the area law:
\[ S_A = O(\sqrt{L}) \]
[cite: 24, 26, 28, 29]. 
This extraordinary entanglement scaling is accompanied by a severe violation of the Cluster Decomposition Property (CDP), meaning that correlations between distant parts of the system do not decay, and excitations exhibit extreme, non-light-cone spreading (violating the Lieb-Robinson bound effectively) after a quantum quench [cite: 28, 29, 30]. These models prove that simple, frustration-free local Hamiltonians can generate vastly more ground-state entanglement than previously thought possible [cite: 24].

### 5.4 Volume Law Violations in 1D
While the Motzkin and Fredkin models display sub-extensive fractional polynomial scaling ($\sqrt{L}$), it is possible to construct local 1D Hamiltonians that force a strict **volume law** ($S_A \propto L$) in their ground states. However, these models require spatially varying, non-translationally invariant interactions [cite: 31, 32]. Such models are mathematically contrived to act as "singlet accumulators," forcing maximally entangled pairs to span across the center of the chain [cite: 31]. The existence of these volume-law 1D systems is intimately related to the computational complexity class QMA; ground states of certain 1D local Hamiltonians that are QMA-complete can exhibit volume-law entanglement, ensuring they cannot be efficiently simulated classically [cite: 31, 33].

## 6. Area Laws at Finite Temperature (Thermal States)

While ground states are central to zero-temperature physics, real-world systems exist at finite temperatures, where they are described by thermal equilibrium Gibbs states. 
A Gibbs state is defined by the density matrix:
\[ \rho_G(\beta) = \frac{e^{-\beta H}}{Z_\beta} \]
where $\beta = 1/T$ is the inverse temperature and $Z_\beta = \text{Tr}(e^{-\beta H})$ is the partition function [cite: 34]. 

### 6.1 The Transition to Mutual Information
At finite temperatures, the von Neumann entropy $S(\rho_A)$ is no longer a valid measure of quantum entanglement, because it primarily captures extensive classical thermal noise, thereby strictly obeying a volume law [cite: 7, 32, 35]. To isolate meaningful correlations (both quantum and classical) at finite temperature, researchers utilize the **Mutual Information** between two disjoint subsystems $A$ and $B$:
\[ I(A:B) = S(A) + S(B) - S(AB) \]
Mutual information measures the total correlation between $A$ and $B$. It is strictly positive, and it vanishes if and only if the thermal state factorizes completely [cite: 36, 37].

### 6.2 The Thermal Area Law
Wolf, Verstraete, Hastings, and Cirac rigorously established a general **thermal area law**, proving that for any system defined by a local Hamiltonian on a finite-dimensional lattice at finite temperature $\beta = O(1)$, the mutual information is strictly bounded by the boundary area separating the subsystems [cite: 34, 36, 38]. Specifically:
\[ I(A:B) \leq O(\beta \cdot |\partial A|) \]
[cite: 34, 36]. 
This is a profound result. It shows that while the information per unit area in classical thermal systems is strictly bounded by the number of microscopic degrees of freedom, the bound in quantum systems diverges as the temperature approaches zero ($\beta \to \infty$) [cite: 36, 38]. Because this theorem applies generally, it implies that the logarithmic violations seen at zero-temperature quantum critical points are "smoothed out" and disappear at any strictly finite temperature, reverting the system to an area law [cite: 36, 38].

### 6.3 Recent Improvements and Bosonic Thermal States
The original $O(\beta)$ dependence implies that as the temperature decreases (large $\beta$), the correlations grow linearly. Recent breakthroughs have improved this bound. By mapping imaginary-time evolution (which generates the Gibbs state) to classical random walks via polynomial approximations of the exponential function, Kuwahara and colleagues improved the temperature dependence of the thermal area law to:
\[ I(A:B) = \tilde{O}(\beta^{2/3} |\partial A|) \]
[cite: 39]. This sub-linear scaling suggests that entanglement propagates diffusively in imaginary time, fundamentally differing from real-time evolution, which generates linear ballistic entanglement growth [cite: 39].

Furthermore, while thermal area laws were well-established for finite-dimensional spin systems, they traditionally failed for bosonic systems because the unbounded interactions in bosonic Hamiltonians (like the Bose-Hubbard model) break standard trace inequalities [cite: 40]. Recently, by utilizing a "double Peierls-Bogoliubov estimate" and artificially introducing a quasi-free reference state, a rigorous thermal area law was successfully derived for interacting bosonic lattice systems in any dimension [cite: 40]. 
Additionally, computable metrics like the **Rényi mutual information** have been developed to bypass the numerical difficulty of calculating standard mutual information, preserving the area-law bounds while remaining efficiently computable via tensor networks [cite: 37, 40].

## 7. Excited States and the Volume Law

While low-energy states and thermal states are bound by area laws, typical highly excited pure states—those sitting in the middle of the Hamiltonian's spectrum—exhibit radically different behavior.

### 7.1 The Eigenstate Thermalization Hypothesis (ETH)
The **Eigenstate Thermalization Hypothesis (ETH)** provides the quantum mechanical foundation for statistical mechanics [cite: 41, 42]. ETH postulates that generic, isolated, interacting quantum many-body systems act as their own thermal baths. Consequently, if one looks at any generic highly excited pure energy eigenstate, the reduced density matrix of a small subsystem will appear effectively thermal, perfectly matching the canonical Gibbs ensemble at the corresponding energy [cite: 41, 42, 43].

Because a thermal Gibbs state possesses extensive thermodynamic entropy (a volume law), ETH demands that the entanglement entropy of a highly excited pure state must also obey a **volume law**:
\[ S_A \propto V_A \]
[cite: 41, 43, 44]. This volume law indicates that information is thoroughly scrambled across the entire quantum system. In such states, an observation of a local region yields maximum ignorance (maximum entropy), matching the statistical expectations of thermal equilibrium [cite: 41, 44].

### 7.2 The Area-to-Volume Crossover
For systems obeying ETH, the entanglement entropy of all energy eigenstates is governed by a universal crossover scaling function. At low energies (near the ground state) or for small subsystem sizes, the entanglement follows the area law (or log-area law for critical systems). As the energy density of the state increases toward the middle of the spectrum, or as the subsystem size grows, the entanglement scales aggressively, transitioning into the extensive volume-law regime [cite: 45]. The exact proportionality constant (the coefficient of the volume law) can serve as an indicator of the system's dynamics: non-integrable (chaotic) systems typically exhibit a maximal, density-of-states-dependent volume law coefficient, whereas integrable systems show smaller coefficients due to local conserved quantities restricting the scrambling of information [cite: 44, 46, 47].

### 7.3 Exceptions to ETH: Many-Body Localization and Scars
Not all excited states follow the volume law. Two prominent exceptions stand out:
1.  **Many-Body Localization (MBL)**: In the presence of strong disorder, closed interacting systems can fail to thermalize. MBL phases are characterized by the breakdown of ETH, and all their eigenstates—even those at highly excited energies—exhibit an area law for entanglement entropy [cite: 1, 5, 43].
2.  **Quantum Many-Body Scars**: In certain non-integrable systems, there exists a bulk of chaotic spectrum that obeys ETH and the volume law, intermixed with a rare set of highly structured, low-entanglement excited states that violate ETH [cite: 41, 43]. Some of these scars obey area laws, while specifically constructed states, like "rainbow scars" or "Entangled Antipodal Pair (EAP)" states, explicitly yield volume-law scaling in otherwise unexpected geometries by maintaining Bell pairs across macroscopic distances [cite: 43].

## 8. Computational Implications of the Area Law

The academic interest in the area law is not merely taxonomic; it is deeply tied to computational complexity and our ability to simulate quantum systems. 
The dimension of the Hilbert space for $N$ particles is $d^N$. However, the set of states that satisfy the area law occupies an infinitesimally small corner of this space [cite: 1]. 

### 8.1 Tensor Networks: MPS and PEPS
States possessing low entanglement can be efficiently factorized using **Tensor Networks**. In 1D, a state satisfying an area law has bounded Schmidt rank, meaning it can be highly accurately represented as a **Matrix Product State (MPS)** with a polynomial bond dimension [cite: 7, 10, 16]. This explains the spectacular success of the **Density Matrix Renormalization Group (DMRG)** algorithm, which is fundamentally a variational search within the MPS manifold. DMRG can efficiently find the ground state of 1D gapped Hamiltonians in polynomial time strictly *because* the underlying physics obeys the area law [cite: 1, 11, 17].
When 1D combinatorial AGSPs prove the area law, they simultaneously prove that an MPS representation of the ground state exists with a sublinear bond dimension $B = e^{\tilde{O}(\log^{3/4}n / \Delta^{1/4})}$, leading to subexponential time algorithms for approximating the ground energy [cite: 14, 16]. Furthermore, 1D Gibbs states can be approximated by Matrix Product Operators (MPOs) in quasi-linear time due to the thermal area law [cite: 39].

In 2D, the natural generalization of an MPS is a **Projected Entangled Pair State (PEPS)** [cite: 33, 36]. The 2D area law conjecture strongly implies that 2D gapped ground states admit efficient PEPS representations, an ongoing quest that drives algorithm development for 2D quantum matter [cite: 33].

### 8.2 Hamiltonian Complexity
Conversely, systems that explicitly violate the area law (such as the volume-law specific 1D non-translational models) encode computationally hard problems. Finding the ground state of such Hamiltonians falls into the complexity class **QMA-complete** (Quantum Merlin Arthur), the quantum analog of NP-complete [cite: 31, 33]. The fact that physically relevant, naturally occurring gapped systems obey the area law provides a physical mechanism that circumvents worst-case QMA-complete complexity, offering a tractable path forward for numerical condensed matter physics [cite: 16, 33].

## 9. Conclusion

The entanglement area law is a foundational organizing principle of the quantum world. Under normal conditions—specifically, zero temperature, finite spectral gap, and local interactions—the quantum correlations of a subregion scale purely with its geometric boundary.
Rigorous combinatorial proofs via Approximate Ground State Projectors have cemented the area law in 1D gapped systems and specific 2D frustration-free models, directly mapping the physical presence of a spectral gap to the tractability of tensor network simulations. However, the quantum landscape is rich with exceptions: 
*   **Gapless/critical systems** invoke conformal field theory to append logarithmic corrections.
*   **Highly connected exotic models** (Motzkin/Fredkin) force massive square-root area law violations. 
*   **Thermal states** transition the scaling limit from von Neumann entropy to mutual information, restoring an area law governed by temperature ($\beta$). 
*   **Highly excited states** surrender to the Eigenstate Thermalization Hypothesis, erupting into a purely extensive volume law that mimics classical macroscopic thermodynamics.

As physicists push to prove the 2D area law for frustrated systems and explore the frontiers of non-equilibrium dynamics and long-range interactions, the entanglement area law remains the vital compass guiding our understanding of what makes a quantum system stable, structured, and simulatable.

***
**Table 1: Summary of Entanglement Scaling Laws**

| System Condition / State Type | Dimension | Entanglement Metric | Scaling Behavior ($L$ = linear size) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Gapped Local Ground State** | 1D | Von Neumann Entropy | $O(1)$ (Area Law) | Rigorously proved (Hastings, AGSP) [cite: 6, 8, 16]. |
| **Gapped Local Ground State** | $D > 1$ | Von Neumann Entropy | $O(L^{D-1})$ (Area Law) | Conjectured; proven for 2D frustration-free locally gapped [cite: 19]. |
| **Critical / Gapless (CFT)** | 1D | Von Neumann Entropy | $O(\ln L)$ | Standard logarithmic violation [cite: 22]. |
| **Fermionic (Extended Fermi Surface)**| $D > 1$ | Von Neumann Entropy | $O(L^{D-1} \ln L)$ | Logarithmic violation via hyperscaling exponent $\theta$ [cite: 25]. |
| **Colored Motzkin/Fredkin Models** | 1D | Von Neumann Entropy | $O(\sqrt{L})$ | Supercritical entanglement; square-root violation [cite: 26, 29]. |
| **Thermal Equilibrium (Gibbs State)**| Any $D$ | Mutual Information | $O(\beta^{2/3} L^{D-1})$ | Rigorously proven; thermal area law bounds classical & quantum correlations [cite: 39]. |
| **Highly Excited (ETH-obeying)** | Any $D$ | Von Neumann Entropy | $O(L^D)$ (Volume Law) | Typical states act as their own thermal bath [cite: 41, 44]. |
| **Many-Body Localized (MBL)** | Any $D$ | Von Neumann Entropy | $O(L^{D-1})$ | Fails to thermalize; area law persists in excited states [cite: 1]. |

**Sources:**
1. [bohrium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnIDv6JmjpLb5HqZeyq09tYwsvpjJY8kLV4cmDMGTi2rPZ90Fmg4L--XyrHayWh7AKmk_gGbFaY3BIlmIfhqjSo9IuXDEJhzWgCfG0qq4tLNKioiD2H98_vsZ8nPcqF6UJzFvOtuUI5s9LO40mYN4LJlP1LNhoX3qzfGfpEFMQkfZVKaEZ)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcukZsszMmuoBbLWA02kOCi5pa2W9iyW8AeQgsz-JWNENf6Vhx3wDKcGOmWsk46dAprsxG3SPQE4D2rcLg7cFuITbWAQyFfJnMBxq75HLuiy2_HxiXv55iKxXV2mvT-lV6XQ==)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpRzMXxu7-ZACtP23rOR2esi3mvmHngCTSBrfjbVPkGYI47iWWwHAuRaKG9napM2KFvKW6Vn_KKsW-Jc1Z34EJMB1JtX028dDV45FIL-wXmguXAHNaf1JeKWV8sYT57j-3yg2P2apEZ07O)
4. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzUuxoZdlhbhmizXirEOBceb3Oypz-co3fdkOrPexpSuZnHFMMR2osYTtjwr1Sa1AJcubKk0ss3bHJkovN4dBkx447rlEOjTV7dT6HSgOeOewdjuvQW3fJSWq3u9lzgRCJMqspjw==)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMXsjrflMvR2x8t0FGq7OcpG2GhBhslKNwNJXcS69X_IIxexN_kDEe8JQc_mHzuJ0Wf8fblheilbPZQa0o67cz8YdTveDwugGO32hJfn8pT9HHerfSTOzP8y2dOFreimhQmgIPzq4=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiFsqH88Dh52p02LBgK9AMlzHj40H8050gVwYoNfNkvS7VRUotFwDVFIHuWMj7MCqmJ1SB6c4iWaHci3cXveuBg_uJPTtOxcG492P9dFh2fC1sLIiA-NBNsanUnNZAT6mcVjyj9NPBUD43euxdTDb7BUAXjI5O8djswx51SuG7lg0L59jJi-LNWfDaSzi0OqRp9Xdy0WUc9JlZvnQd201v9c3Qb4vQoisfwLwOolNy8AAW8BfS4g==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE82A3AYS5LGuWIlf9EpsrEnSWmdvSHHBAHHFAJ_26c0lhdpGVizJ8UAHSwazKkx-W7xYaPkMLg4dXSnTcjVpM1pNXQ6QWAFVLqW2JhpNR985BMmtI=)
8. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6zKR06tVoFrmcIOtbRrV4C-fQy7m-8OlqADWgRfWnt2gb1nxL0FFjvKP4ZgYpoN7i_6-6cgVpTJOCoI21FBCQ5hBIkDSjjSGPB_xL23loYRUVxpuZs_F14lYNAs2IV56oKx6PQoQ8MVOtwgf0)
9. [aau.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT1PMu3lwFvPThOyP1S9QhWpy12Z_Zy9Isn-XKFS_cx7UhBROoLi8m5DvwpqLq96nTaQzBzqdgD5Kupiia-P6Yn8nIH_3fwI8_GtRQh-yU_ydEq9mMyhEyxQU3MtW6SwLJWpfxSiBW1Q==)
10. [esi.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZCBQeYVPuxaA-8bb-tXRozwCRasrH2hCPeqFGsZ0Q7dAvSZynzgYGQgdK_7mJS3HSjZWS8kEmLHQDwUAbtGZs7d9YJJ06sBHEPY-5OIOmGBzGVgef-c9EAtG2ZU6fcUQ=)
11. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHblDzjeWj_yi1ePoaLcfXdDTcjPcmhBsG7Qm25qtcWI-ij6WNfTMijOtTMUZm2551VqJ2dkYVl55mnU-0n8O-Lef4WA8llnqQCvGccEDk1FSlf7a0plwoGH1qLnt4RGzJE4_CvEnFmvhQXY9pjoypP_av9On9-t3f7dySPKxM4SdKa3NHRZA==)
12. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCuTd8K9ohnG3AikPB-TuW1KfPr9hl73WvXfGODmxq3ZohUcI6d5CsHeIpuXXeqbYcYzUbFTvayhBwmo2ql_znylHEHaDiQyAWYp8hO5mNLYdg1XoG3qUbc0aTjlykz8WF)
13. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuNcIk9qqVKz_CaxRnAwHoR7YRCFTsklFEKqYHS5sF6oFomGaQkFt6ci5sXjaVbr2WoOTImXW-njCzdl1N0w5SyDx_EE2hv9p1gnJtHpXCc0Ni_DBgO8OycNFq2TKAsOFZFB3gpusbWNMV14Svzez4K7dd-Yz_vQDf_SFT8Gie3JhVHQprBQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu93TIBnNFFYIcGrtL8ssjdgr0WovKKCe2RDsZk_GmOP2LIUX_9MJgT67uceN6brI3LEkX0mZyxNtmbbjLpt-PtbrnH4PdgfsFMDqdRgJWuRmatX0=)
15. [windowsontheory.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxW6TG2hVVAizCUZG0ycDuYLESX3ER2ZFCV-J_TIWdrFdU5mWhh1GvzFQbxejo1e_3sAe7g9wFS_CsXLuEZr_-F6iFx-UgrccLi8Nlts1LIra-Ww9_Rug2kCYzM_gpunXX5TwdllOWb0H1yHp_dSmTbHWTGfmGu-ZjzLVNas8g0ac-4dUXX7xx)
16. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDKKFLaDstNPSd1u71RNCTwHb-QfybI5uXGydM9TaCkw3HX1v_SXsuJ6u3ufDxDJQewg5oj7U0Da49qGX8QSCBGj3CP4agAbDVKQYvcoIXSyzCUlJke9UqGYtfEE1kOiYwRNpk0VQB2B-S5-vtXnseK8Q=)
17. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUIR1EcYm3HbJPd5uDRAzCQUw9DJ_WJj-CPoP2FjJZ2J2spr-oDqL1xsSr4pcjS5b55iDmTFGJ9gI1Ul672an_H2HwYrmO7lmOeeqBO7baliPC5bNujLZBcfDgSTE2A==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDxQZ5lu6P91IITsiaqSZVuE2hbgxUtIfqxqNjtly_mSQ40wEP-bJBphCySFkBy8MKdEhL0EMyXdZcRYKrwUE0Z7OR51q9pkIjjM5hXpL1v8905Swv)
19. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEK0MLkPjU79e4h5B9HVzKkpY7VBCknzvAalwkyk3m73-acHe2QfIwWW4kmoRDdLGkpHsABqzwy0iOyrPZ5Gs2AOBChg9rSWKEkFY8t-ggdFn0c5CN-DXi8QQauY_66SokHnLO3JAELi7D4CTs5KXN_JgFVzVHqNVYyC_oOdf7rIkhJUV871I4WA6aVWeSmEmI=)
20. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX1_keYk5QyYAbGHNGI9UQ2QTW11Gy8VOEYmLpk_fGk4hETHaNBl11WR9iMMMOfg-B6vstbAvUKVgrO1ZHxXnxXaRXouUCaF5JH74BVcU_Xrc-sTC8ABJn0C6gYRFwVLB5PMQ2l6jDMqRHo5Q1sAH1kz44IeoO6HnPM9iPl1gjiwPtWaAoqhA=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq5mX7l27sZlasa6YKyL38kd_C7POUxfjEPlGPa3KZcAKexuHtim7LeKm2kv2G27vkueaAnBo6nPYB_wR7sYKv8TcxkX1g0aorxAuqe-vGP3SYA4mB)
22. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCxjg2DXNiwdFSlzx5mp8MWBV_edhkvoe4e8dmR4UarpMp_XiyRrmKZNAo7vgt-RgwFA_57ktbMzVmDDu5UXJyBr3ZUoaGYeDEFkMYcGc210ID0Ff9maQcBAHMJ19Sy8KGnuL5ldE1IzSanN0wjA6qcXtz_V5vxfczhrrs5ugOLM-OGjGLHEJ0iPrWXAiQ_Wqqh-m80g==)
23. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGZk_Poi7kqyoC8P_99jBSHnmB33LqC4f5H35nyLijsgzdazOiarnPFifsT6wOjOlLVdzGfYCA3tRlbJvhJ1cS6Zu1R1EnoO6296tCAhT5i8Ept94DwhLXOycVAG_9qQf8iG_UcNW3vfTIL9nsj6QnoSMZIw5qZ8Lpc-rslQgEIv1jFQ8eoF6Epg==)
24. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKkqHSIbyFppmsZEbyYJEteYoaxeifAViCD60NPx4a5ne2BIujPKTzYhnkS7uIh3uitAgUJ_GwxRK_Ac6ISYnZdfiMClr1K3iVAnPtMS6n2YVDFBvFj9FHawj8A-c8h87Q02jh-gc=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEom-6ETnrhu6DvXFZ5S-mTHw4hAkThbBXvd7DPR3EURrO6NLrMZA1EnttWiKj1eTt4mPcPtOeRJtNvfGai5YobuKN-hO-W7U2DcfHp787QEpFfjwK_)
26. [ipb.ac.rs](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFCeKbTqltOBRvIQ8wzPb2w0xIbWq8_BrPSIvrccfloIX1MbbJa9pEy9ehF-E6RXWMnbfPQZVqAgvLlnVo2QMYLfV36DmWOU36TYiCLvAKh-NDF4n5ZYwi2Ljck_0Qkrkg94EyIimornwx)
27. [gu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOE6dkHD-0uNP7ilxuryt4RHhM5fIPYaAU-xRMLMA7HTnzZ4NGtbggtbM1RM9UNQMOdmDAne07N6M6lZXPsuoH_TiiGsIyk25U8kI7AXBEnfe5d9XMoywbNfFGru_VnQ9YkW0IcvVkksNBCU0eOw==)
28. [sissa.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXz3YIJZCSkUNEHCL3I44ITa3tgNEku0E69bokSHjVmEXMZ_VtQFhxKkKbjb2NlIq494YhprcRf5YldrGSj7VcZ_YcKuEk9sCg9VhrCdD0pjqX_pigSvpjKY3xtvEMq43tlGn_2yCHWW9gd4MKb7vDwVG9xoA0fEjeJ16aEDetZE6N)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0NN1GmEl59TkEPzOdSoDIw0vtgrtwABSIEWmF7PUZHNpeOdLw-qZsnqGEuzHqeegnk_8vTm9tPe2iDEyOuktEZmS3pchc0gfv1up1QbV32ufxSwm7)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGGSejAfSjwxREMVrOXGqWPj0TUXb83bwGnrZM5-ru-h6izEGp7UzrWFAyDb_8eRG81uiPxhhoSLaGRtT5m_SO0ZiiPlg92dw4ZWsplq-lv38F8_-1)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaNoOD02fGTIpyEPIfN4Nbak4s4s9CfRUhcGlp02Fr2dml9wCHCY38eCrNq0NFKIdVw25SlJTuQ1hKGX9Lqx6KlWZ4VZpNYb4F-tc5PdjE5afC3BA=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBIWE0KkuuYUi95V0FB3f9GZ-aIHzQIsTHOE6twl3m_-vR2sewhaC6skE2MrcELeetW_ZHY6uQHZWC_UJg0E113Vf8yziG9yXN5NMU4wqt3FnT7i68WwOBBVrBv4I0ZEg=)
33. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN3_ANVS1AxhVpI-8wd4SWNncnWsCbok9n8HDiEK5Lw5aSrvQIEz4F9azcxg_cJ4fUXcUsw6vWwAptj2i1a6h2QAAk7mNQgjMc6F-TPHCUs4njJpgsp0UTeLRhkqNYaLfIyuT1xYSkdgexgxFGHE9WXe3Ha3JtmPGB6dlxqy6o8OmignT54HwNS51cRC9Zlls=)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK5NP9RcdO4g2T2gYZHKXTPbXIOAGeJptHUusPTUo0EKLyTOCfhwyQVDs8-PZuZKUAkdKa3pPRcFsoNMHlvr1pe2VHPOn0F1Vl2TLE5SO9I5Wcm2iQueEsh54G-KHZb2rTgvVNdzMCfX_gAdN4dQTtghalQY7jekCkcHQxHsfolEWjvbQIPM064LRCFzUN08goBmbWLZqSPhcJqJLPUUuW-BEouJN_)
35. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmlBBEIXQRwBU90iLvmP6A_29zX3zp95waphDDjCKq6p16nmJVZz1MXGD3QmSxy-1SD-ioOnhhxhBoTwollFOx5qVxEiuHPVFOlxGd7IU8q011wqgG9qpRUCXahEs5JimFsSg8FUzMUNpCvaAHLO10xke2MMd6Q07LuN21wHMfv-IKqyBonmcaC4TUDMTee2s=)
36. [esi.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJJSJz6HtmOq0xZnpEi2OI_d_KhP7dxjRboLJRXGU1o7RiqnzlaKuS-GprmzH7sEtAP3wrAc5OQ4GI2pA2uzdgUb9Q7hQTcDR_TtO9jPQ8eHdAeKZ4mIgHhh_2x_tIt7k=)
37. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGco2itvWtnS6y1Sx_mrm0NH2lvN026JzF2Iogn1rEMkbA4s9_T-FBDA4N4bTqCNRJS2RLlQ5BR7BjTrmYBz5zqhpyQQTW_8SH26qg9C2u-S5d7pNZ87DN_soEvDRLDCZAacAqm4hhytwA=)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExIRz-7xW1AAMcC9fnPjx5EY3Nb8E6PrFrXfXvpiieWAyNBzUJ2muT18BKMLcS6Fm9piWbyd3ZxD-5nBQF5ltHDYmzWc4R_fFG9TzJ5ZWpCq-I93bAGc8VnWYx7zTiX-0=)
39. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3cI2LJLacX2QzwnyA-E3q1ytCnyQtj9lU_nSuKBf85R_KLtlZjuOwYHtD9Lyn9MrveWaJGjBj3oBVmePnCJR1QY7Xyn5AfzlXJltsl2jFL-dN6-Inep3kU7Wwg_dI1dxB5IGyKR5SB1pugcEJ5ONPd82IFAyZLrvr53xIBJfowGl86yHHdpEKDs3dNifsJozAfZGSwQhVQBOGJXjBvN-ijvIig6xh)
40. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF5eTGvvN9l24CzL1kZI_M5bJOWAHRlUBVXBgg5kxmYzrQckp8alEGeGwmXde0raOhxTQrMhbm5vwYDbps68e8lBY5ToaOKNUtLLm91bqPEUUu9gqQZPVGz2aQoO8Ens2iifwD65KO3_YX)
41. [blogspot.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyFHZuTKDuUf65xgKCNu0gDWGsW2Hdxr09vvFKoui3_wi4HGf8-Mf-69Sa-AawjYm-XIhmqK--GuVuTTncha6F4VMfQUSKv1Uxe_mXjV8oRiIk35g4GcqCCw17GADzKohbA-XjhAz2ifNnxQUBcN012DWFhm9dJWd_XYKdyIYMTnAxLm4XRQ==)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFi5Dp0UWQJ8qAh-GpW24Au7q9l8kW3EV5OV4RGAWD8luxDmnWdc8t3h2qt-CQh0ma9zbKaSd499gS5aA6SjB_BorSVB3tEIOdFxFAmpZesk3afU2fzeTr)
43. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_Kv2aDFgadskjJ5UYq0LcVgnYZqINGQVShc_YKJs5uYWVyg2oQcdUwMtezKrwFJT9r_MzaWPRKnWhXVmTK-GnoMotObbGvIfk_h2uMmnImb4_I5hhMjfDJYCKyzUNKqA=)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR6Qcq9cgkkIgKpWNdGYDsg2qFlDl2RixkW0USSK-9WfwwzSOvzHl2oAJ2ytYmgJM7yqmBdUlbCQDYp5Z9PXbkJe9yWi1_2hoJIHi7QGhcJo9l_qLcZWIi)
45. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTA3kBezF7H3tm6N3UwVCS9H4NsEcjhfqynj9SM5tV7Mx3bDBMnB66Nd_VGow2A1yyDJzxkUuZom-GyDaUx0cUX-N-fgWc34WWb1NjEaz78_xXCiqLdre2Q1WVIXsG)
46. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0_0nN6I3B9vAi2o8JZn47uZHhHEyHvCP_BHOInagHw-PNIRiW-wYrduIC4byDCFqeNUzd3fuQ2yqF0Uj7Q08QeGJuVghb_yct_PCyuTi6EViXzN7EJ7LXUiMfVzJOO6MsbH7ICk_ChiZOcGKkLrin-04UDS_YsD6hUEs3cDbq676Ldlr4Ssv7phcTAWY=)
47. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDCGaBWKacwH8T7v2hoaFdtzcrrx0wnGlaRA_Lsk09hZyHsHetHMENE_ryG_DvnT1HzmZo1j7VxZofhCKT6aR5KjS3o7pLlDxcgygqPvEk5DM_qk6Rh8hy)

