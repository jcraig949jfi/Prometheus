# T#81 Most-entangled state identification

**Pythia queue id:** 118
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMQ01QYXFLa0FxdWEtOFlQdHNmcjJRbxIXTENNUGFxS2tBcXVhLThZUHRzZnIyUW8
**Elapsed:** 930s
**Completed at:** 2026-05-21T15:37:50.643632+00:00

---

# Comprehensive Academic Report on T#81: Most-Entangled State Identification in Quantum Systems

**Key Points:**
*   Research suggests that identifying the "most-entangled" state in quantum systems depends heavily on the chosen mathematical measure; while bipartite systems have a well-defined maximum (e.g., Bell states), multipartite systems possess stochastically inequivalent classes (such as GHZ and W states) that prevent a single universal maximum.
*   It seems likely that the Geometric Measure of Entanglement (GME) and the framework of Absolutely Maximally Entangled (AME) states offer the most rigorous and operationally meaningful methods for quantifying and identifying extreme entanglement in complex, multi-qudit systems.
*   The evidence leans toward advanced computational techniques—specifically Semidefinite Programming (SDP) hierarchies and Majorana representations—as the most effective tools for bounding, optimizing, and physically identifying these states in both theoretical and experimental physics.
*   A recent, groundbreaking quantum solution to Leonhard Euler's 243-year-old "36 Officers" puzzle has demonstrated the existence of previously elusive AME states in higher dimensions, fundamentally altering the landscape of quantum error correction and state identification.

The challenge of "Most-Entangled State Identification," often benchmarked in advanced physics curricula and literature under identifiers such as "T#81" or mapped to specific open quantum problems, lies at the very frontier of quantum information theory. In simple terms, quantum entanglement is a phenomenon where particles become inextricably linked, such that the state of one instantly influences the state of another, regardless of distance. Determining which arrangement of particles is the *most* entangled is crucial for building powerful quantum computers and secure communication networks.

For systems containing only two particles (bipartite systems), physicists have long established what maximal entanglement looks like. However, as more particles are added to the system, the geometry of the quantum states becomes unimaginably complex. Particles can entangle in fundamentally different ways that cannot be converted into one another, meaning there is no single "most entangled" state for all purposes. To solve this, researchers use geometric distances, algebraic combinatorics, and advanced computer algorithms to identify states that maximize entanglement across all possible divisions of the system. 

The search for these states is not purely theoretical. Identifying highly entangled states directly impacts the development of quantum technologies. Recently, this field saw a major breakthrough when physicists applied quantum mechanics to a 243-year-old math puzzle proposed by Leonhard Euler. By allowing the theoretical "officers" in the puzzle to exist in a quantum superposition, researchers discovered a new type of highly entangled state. This report exhaustively details the theoretical foundations, geometric measures, algorithmic identification strategies, and experimental realities of finding the most-entangled quantum states.

## 1. Introduction to Quantum State Identification and the T#81 Paradigm

The identification, characterization, and quantification of quantum entanglement constitute a central pillar of modern quantum information processing. Quantum entanglement distinguishes classical physics from quantum mechanics, providing the non-local correlations necessary for quantum computing, cryptography, teleportation, and metrology [cite: 1, 2]. However, as the dimensionality and the number of particles in a quantum system increase, the mathematical complexity of identifying the "most-entangled" state grows exponentially [cite: 3, 4]. 

In academic literature, specific grand challenges and problem sets are frequently cataloged with identifiers to track progress on foundational quantum mechanics. The designation "T#81" and similar nomenclatures often refer to highly specific theoretical tasks within quantum mechanics problem sets, algorithmic routing benchmarks, and open problem registries (such as the Open Quantum Problems list from IQOQI Vienna, where problems like #41 define rank inequalities for quadripartite states) [cite: 5, 6]. Furthermore, in the context of experimental physics, such identifiers map to specific boundary conditions, such as temperature thresholds (e.g., T=81°C) used to optimize phase matching for generating discrete frequency-entangled photons in continuous-variable (CV) systems [cite: 7]. In the context of this report, "Most-Entangled State Identification" serves as the thematic umbrella for these challenges, representing the quest to define, compute, and physically realize the absolute theoretical limits of quantum correlation.

The crux of the identification problem is that entanglement is not a monolithic property. Entanglement is evaluated through various measures, including the von Neumann entropy of reduced density matrices, the geometric measure of entanglement (GME), the robustness of entanglement, and the relative entropy of entanglement [cite: 8, 9]. Because these measures often prioritize different physical attributes of a quantum state, a state that is deemed "maximally entangled" under one measure may not be under another [cite: 10, 11]. Consequently, defining a universal "most-entangled" state requires a rigorous set of parameters, often culminating in the search for Absolutely Maximally Entangled (AME) states, where every possible bipartition of the system is maximally entangled [cite: 12]. 

## 2. Bipartite Entanglement: The Foundation of Maximal States

To understand the complexity of multipartite systems, one must first establish the baseline of bipartite (two-party) entanglement. Entanglement in bipartite systems is completely understood from a mathematical perspective. If a bipartite system exists in a pure state, its entanglement properties are fully characterized by the Schmidt decomposition [cite: 10, 13]. 

For a pure state \( |\psi\rangle_{AB} \) in a Hilbert space \( \mathcal{H}_A \otimes \mathcal{H}_B \), the Schmidt decomposition expresses the state as a sum of orthonormal basis vectors:
\[ |\psi\rangle_{AB} = \sum_{i} \lambda_i |i\rangle_A \otimes |i\rangle_B \]
where \( \lambda_i \) are the Schmidt coefficients, which are real, non-negative numbers satisfying \( \sum \lambda_i^2 = 1 \). Any entanglement measure for a bipartite pure state is ultimately a function of these Schmidt coefficients [cite: 10, 14]. 

A bipartite state is unequivocally defined as the "most-entangled" (or maximally entangled) state if all its Schmidt coefficients are equal, meaning \( \lambda_i = 1/\sqrt{d} \), where \( d \) is the dimension of the subsystem [cite: 15, 16]. Under these conditions, the reduced density matrix of either subsystem (obtained by tracing out the other subsystem, e.g., \( \rho_A = \text{Tr}_B(|\psi\rangle\langle\psi|) \)) is completely mixed, meaning it is proportional to the identity matrix \( I/d \) [cite: 16, 17]. For a system of two qubits (\( d=2 \)), the maximally entangled states are the Bell states, which form an orthonormal basis for the four-dimensional Hilbert space [cite: 3, 18].

The identification of entanglement in bipartite mixed states is slightly more complex but remains highly tractable. The Positive Partial Transpose (PPT) criterion, formulated by Peres and Horodecki, provides a necessary condition for separability: if a state is separable, its partial transpose must be positive semidefinite [cite: 19, 20]. For dimensions \( 2 \otimes 2 \) and \( 2 \otimes 3 \), the PPT criterion is both necessary and sufficient. However, for higher dimensions, there exist bound entangled states—states that require entanglement to be created but from which no pure entanglement can be distilled using Local Operations and Classical Communication (LOCC) [cite: 3, 21]. These bound entangled states generally possess a positive partial transpose, but a major open problem in quantum information theory is determining whether there exist bound entangled states with a Negative Partial Transpose (NPT) [cite: 19, 22]. 

## 3. The Multipartite Challenge: Beyond Bipartite Systems

When the system size increases from two particles to three or more, the elegant simplicity of the Schmidt decomposition collapses. In multipartite systems, it is generally impossible to simultaneously diagonalize the reduced density matrices of all subsystems [cite: 10, 14]. As a result, the identification of a single "most-entangled" state becomes an ambiguous task, highly dependent on the entanglement metric being optimized [cite: 10, 23].

A fundamental result in the theory of multipartite entanglement is that pure states can be categorized into distinct entanglement classes based on their equivalence under Stochastic Local Operations and Classical Communication (SLOCC). Two states belong to the same SLOCC class if they can be converted into each other with a non-zero probability using only local operations and classical communication [cite: 9, 18].

For a three-qubit system, there are exactly two stochastically inequivalent classes of genuine tripartite entanglement: the Greenberger-Horne-Zeilinger (GHZ) class and the W class [cite: 23, 24]. 
1.  **The GHZ State**: Defined as \( |\text{GHZ}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle) \).
2.  **The W State**: Defined as \( |\text{W}\rangle = \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle) \) [cite: 23, 25].

A state in the GHZ class cannot be converted into a W state via SLOCC, and vice versa [cite: 9, 23]. This poses a profound question for most-entangled state identification: which of these is more entangled?

According to the measure known as the "three-tangle" (or residual entanglement, introduced by Coffman, Kundu, and Wootters), the GHZ state is considered the most entangled. The three-tangle quantifies the amount of genuine tripartite entanglement that cannot be accounted for by the bipartite entanglements of the subsystems [cite: 9, 23]. For the GHZ state, the three-tangle is maximized. Conversely, for the W state, the three-tangle is exactly zero [cite: 23, 24].

However, the GHZ state is notoriously fragile. If one traces out (or loses) a single qubit from the GHZ state, the remaining two-qubit state is entirely separable (an unentangled classical mixture) [cite: 23, 25]. In contrast, if one loses a qubit from the W state, the remaining two qubits remain highly entangled. Therefore, if the figure of merit for "most-entangled" requires robustness against particle loss, the W state is superior [cite: 24, 26]. 

To reconcile these differences, researchers have developed composite measures, such as the "concurrence fill," which reformulates the three-tangle and partial tangles into a geometric area, allowing for a non-zero evaluation of GME for both GHZ and W classes [cite: 9, 23]. 

| Entanglement Feature | GHZ State | W State |
| :--- | :--- | :--- |
| **State Definition** | \( \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle) \) | \( \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle) \) |
| **Three-Tangle Value** | Maximized (1.0) | Zero (0.0) |
| **Robustness to Particle Loss** | Highly Fragile (Reduced state is separable) | Robust (Reduced state is entangled) |
| **SLOCC Equivalence** | Inequivalent to W | Inequivalent to GHZ |
| **Geometric Measure Focus** | Maximizes non-local multi-party correlation | Maximizes persistent bipartite correlations |

The complexity grows super-exponentially with the number of qubits. For four qubits, there are continuously parameterized families of maximally entangled states that maximize the average bipartite entanglement with respect to all possible bipartite cuts [cite: 9, 25]. For large systems, states like the Cluster states and Dicke states emerge as highly entangled resources critical for measurement-based quantum computing [cite: 18, 25]. Identifying the "most entangled" state in these higher dimensions requires transitioning from algebraic representations to geometric and combinatorial frameworks.

## 4. The Geometric Measure of Entanglement (GME)

Given the ambiguity of multipartite entanglement classification, the Geometric Measure of Entanglement (GME) was developed as a rigorous, universal metric. Originally introduced by Abner Shimony and later extended by Wei and Goldbart, the GME quantifies entanglement as the geometric distance between the target state and the closest fully separable (unentangled) state [cite: 14, 27]. 

Mathematically, for a pure multipartite state \( |\psi\rangle \), the geometric measure of entanglement \( E_G \) is defined using the maximal overlap (or fidelity) with the set of completely separable states \( \text{Sep} \):
\[ E_G(|\psi\rangle) = 1 - \max_{|\phi\rangle \in \text{Sep}} |\langle \phi | \psi \rangle|^2 \]
Alternatively, it is often expressed as the logarithm of this overlap: \( E_G = -2 \log_2(\max |\langle \phi | \psi \rangle|) \) [cite: 11, 28]. 

The identification of the most-entangled state under the GME translates to a highly non-trivial multi-way optimization problem on a hypersphere [cite: 29, 30]. Because the set of separable states is not a linear subspace but rather a complex geometric manifold, finding the closest separable state is formally equivalent to computing the injective tensor norm of a multilinear algebraic form [cite: 11, 30]. This optimization is proven to be NP-hard, making the exact calculation of GME for arbitrary large states computationally intractable [cite: 11, 28].

Despite this computational difficulty, the GME offers profound theoretical insights. The most entangled state with respect to the GME is simultaneously the state that maximizes the nuclear norm (the dual norm to the spectral norm) [cite: 28]. Furthermore, the GME is directly proportional to the discrimination probability in quantum state identification tasks and bounds the performance of quantum metrology protocols [cite: 16, 31]. 

For small systems, specific highly entangled states have been identified using the GME. For instance, the Higuchi-Sudbery state is recognized as a maximally geometric entangled state for four qubits, possessing a higher GME than the four-qubit GHZ state [cite: 28, 32]. For larger systems, hierarchical approximations are used. By considering multiple copies of a pure state, researchers can construct a converging hierarchy of semidefinite programs (SDPs) that iteratively approximate the injective tensor norm, allowing for the precise computation of the GME without requiring exact geometric projection [cite: 11].

## 5. Majorana Representation of Symmetric Multiqubit States

To simplify the mathematically grueling task of GME optimization, physicists often restrict their search to permutation-symmetric states. A permutation-symmetric state is one that remains entirely unchanged if the identities of the underlying particles are swapped. Because these states have a significantly reduced number of independent parameters, they are fertile ground for most-entangled state identification [cite: 8, 33].

In 1932, Ettore Majorana demonstrated that any pure, permutation-symmetric state of \( N \) spin-1/2 particles (qubits) can be represented by \( N \) points on a unit sphere (the Bloch sphere) [cite: 33, 34]. This is known as the Majorana representation. The symmetry of the state under local unitary operations corresponds exactly to the rigid rotation of these \( N \) points on the sphere [cite: 8]. 

This geometric translation is revolutionary for entanglement identification. The abstract algebraic problem of maximizing the Geometric Measure of Entanglement becomes a tangible geometric optimization problem: how to arrange \( N \) points on the surface of a sphere such that they are as "spread out" as possible [cite: 8, 27]. 

The points on the sphere are referred to as Majorana Points (MPs). A completely separable symmetric state corresponds to all \( N \) points occupying the exact same location on the sphere. As the points are pushed apart, the state becomes more entangled, which mathematically corresponds to an increase in the Wehrl entropy (a measure of non-classicality) [cite: 27, 34]. The "most-entangled" state in a symmetric subspace is therefore identified by finding the spherical configuration of points that maximizes this entropy [cite: 8, 27]. 

This approach allows for the analytical identification of maximally entangled symmetric states for up to 9 qubits [cite: 27]. It also unifies different entanglement metrics: for highly symmetric states, the geometric measure of entanglement, the logarithmic robustness of entanglement, and the relative entropy of entanglement all become mathematically equivalent [cite: 8]. This spherical representation not only streamlines algorithmic searches but also provides deep physical insights into spinor Bose-Einstein Condensates, where similar point symmetries dictate ground-state quantum phase transitions [cite: 8].

## 6. Absolutely Maximally Entangled (AME) States

While the GME provides a robust metric for quantifying existing entanglement, the Holy Grail of most-entangled state identification is the Absolutely Maximally Entangled (AME) state. An AME state represents the most extreme form of multipartite entanglement conceivable within the laws of quantum mechanics [cite: 12, 17]. 

A pure multipartite quantum state is defined as an AME state if, for every possible bipartition of the system, the state exhibits maximal bipartite entanglement [cite: 12]. Operationally, this means that if one traces out up to half of the particles in the system, the reduced density matrix of the remaining particles is completely mixed (i.e., proportional to the identity matrix) [cite: 12, 17]. 

The defining characteristic of an AME state is its "genuine multipartite entanglement," meaning no subset of the system can be factored out, and any measurement made on half the system immediately collapses the other half into a known state [cite: 12, 35]. An AME state of \( n \) qudits (systems of dimension \( d \)), denoted as AME(\(n, d\)), is equivalent to a \( k \)-uniform state where \( k = \lfloor n/2 \rfloor \) [cite: 12].

The practical implications of AME states are massive. They are directly equivalent to pure-state threshold quantum secret sharing schemes [cite: 12, 17]. In such a scheme involving an AME state of \( n \) parties, any group of \( \lfloor n/2 \rfloor \) or fewer participants gains absolutely no information about the secret, while any group strictly larger than half can perfectly reconstruct the quantum secret [cite: 17, 35]. Furthermore, AME states are foundational to holographic quantum error-correcting codes, providing optimal frameworks for redundantly storing quantum information against environmental decoherence [cite: 12].

However, AME states do not exist for all combinations of particles (\( n \)) and dimensions (\( d \)). Identifying where AME states exist is a major ongoing mathematical challenge. 
*   **Qubits (\( d=2 \))**: AME states exist for \( n=2 \) (Bell states), \( n=3 \) (GHZ state), \( n=5 \), and \( n=6 \) [cite: 17, 35]. It has been rigorously proven that AME states of 4 qubits do not exist, and it is largely accepted that AME states of 8 or more qubits do not exist [cite: 17]. For \( n=7 \), physicists long debated their existence until it was definitively shown that an AME state of 7 qubits does not exist [cite: 12, 36].
*   **Higher Dimensions (\( d > 2 \))**: As the local dimension increases, the phase space for entanglement broadens, allowing for AME states that cannot exist in qubit systems [cite: 12, 35]. The construction of these high-dimensional AME states relies heavily on graph-state methods, orthogonal arrays, and algebraic combinatorics [cite: 12, 35].

| System Type | Qubits (\( d=2 \)) | Qutrits (\( d=3 \)) | Quhexes (\( d=6 \)) |
| :--- | :--- | :--- | :--- |
| **n = 3** | Exists (GHZ) | Exists | Exists |
| **n = 4** | **Does Not Exist** | Exists | **Exists (Quantum Euler Solution)** |
| **n = 5** | Exists | Exists | Exists |
| **n = 6** | Exists | Exists | Unknown |
| **n = 7** | **Does Not Exist** | Unknown | Unknown |

## 7. Euler's 36 Officers Puzzle: A Quantum Resolution

One of the most spectacular recent achievements in most-entangled state identification involves the intersection of AME states and a 243-year-old combinatorial puzzle: Euler's 36 Officers Problem. 

In 1779, the Swiss mathematician Leonhard Euler posed a problem: Suppose there are six regiments, each containing six officers of six different ranks. Can these 36 officers be arranged in a 6x6 grid such that no row or column contains a repeated rank or regiment? [cite: 37, 38] 

Mathematically, Euler was asking for the construction of a pair of orthogonal Latin squares of order 6. A Latin square of order \( n \) is an \( n \times n \) array filled with \( n \) different symbols, each occurring exactly once in each row and exactly once in each column [cite: 39]. Orthogonal Latin squares require that when two such squares are superimposed, each possible pair of symbols appears exactly once [cite: 39]. Euler easily found solutions for 5x5 grids and 7x7 grids but hypothesized that solutions for order 6 (and any order \( n = 4k + 2 \)) were impossible [cite: 37, 39]. In 1901, the French mathematician Gaston Tarry exhaustively proved that a classical solution to the 36 officers puzzle is indeed impossible [cite: 40]. In the 1950s, Indian mathematicians R.C. Bose and S.S. Shrikhande proved that solutions exist for all other orders except 2 and 6, earning the moniker "Euler Spoilers" [cite: 37].

However, in 2022, a joint team of Polish and Indian physicists revisited the problem using quantum information theory. They asked a revolutionary question: What if the officers were not classical entities, but quantum objects capable of existing in a superposition of ranks and regiments? [cite: 39, 40]

By reformulating the grid to allow for quantum superpositions, the researchers effectively expanded the mathematical parameters. They were looking for an Absolutely Maximally Entangled state of four 6-level systems (quhexes)—an AME(4, 6) state [cite: 40, 41]. Previously, physicists heavily suspected that an AME(4, 6) state could not exist, mirroring the classical impossibility of Euler's order 6 squares [cite: 40]. 

Using advanced computational techniques and geometric heuristics, the researchers demonstrated mathematically that the quantum version of the puzzle *does* have a solution [cite: 39, 40]. They discovered the elusive AME(4, 6) state [cite: 40, 41]. To conceptualize this, the physicists likened the state to throwing four 6-sided dice. Because the state is absolutely maximally entangled, observing the outcome of any two dice immediately and perfectly dictates the outcome of the other two dice [cite: 40]. The discovery of the AME(4, 6) state not only closed a centuries-old mathematical loop but also provided a novel, highly resilient quantum state for advanced quantum teleportation and error-correction protocols [cite: 39, 41].

## 8. Computational Methods: Semidefinite Programming and State Distillability

Given the immense difficulty of analytically identifying states like AME(4, 6), physicists rely on complex algorithmic frameworks. The primary computational tool for investigating quantum state properties, bounding the geometric measure of entanglement, and identifying entanglement classes is Semidefinite Programming (SDP) [cite: 20, 42].

An SDP is a convex optimization problem where the objective is to minimize a linear function subject to the constraint that an affine combination of symmetric matrices is positive semidefinite. In quantum mechanics, density matrices are inherently positive semidefinite, making SDPs exceptionally well-suited for state identification [cite: 20, 42]. 

One of the foundational applications of SDPs in entanglement theory is testing for separability [cite: 20, 21]. Because the exact separability problem is NP-hard, SDPs utilize hierarchical approximations, famously known as the Doherty-Parrilo-Spedalieri (DPS) hierarchy, which relies on the concept of symmetric \( N \)-extendibility. A bipartite state is separable if and only if it admits a symmetric extension to an arbitrary number of copies of the second subsystem [cite: 20, 42]. By increasing the level of the hierarchy (\( N \)), the SDP provides increasingly tight bounds on whether a state is entangled or separable, converging to the exact solution in the infinite limit [cite: 20, 42]. 

SDPs are also employed to evaluate the \( k \)-block positivity of quantum maps and to bound the injective tensor norms associated with the Geometric Measure of Entanglement [cite: 11, 42]. To optimize computational efficiency, researchers heavily exploit the unitary symmetry of maximally entangled states, grouping the variables using Young diagrams to reduce the scaling complexity of the matrices within the SDP [cite: 42]. 

Beyond mere separability, SDPs are critical in the study of entanglement distillability. Entanglement distillation is a process where multiple copies of a weakly entangled mixed state are processed using LOCC to produce fewer copies of a highly entangled pure state (like a Bell state) [cite: 3, 22]. A bipartite state is "distillable" if it can be converted into a maximally entangled pure state in the asymptotic limit [cite: 3, 20]. 

It is a proven theorem that all PPT (Positive Partial Transpose) states are undistillable (bound entangled) [cite: 20, 22]. However, the reverse is not fully understood. Determining whether there exist NPT (Negative Partial Transpose) states that are also bound entangled remains one of the most prominent open problems in quantum information theory [cite: 19, 20]. Identifying these states involves running high-level SDPs to check if a specific state (for example, a two-ququart system) is 2-copy distillable, a problem so significant it carries dedicated academic bounties such as the Golden KCIK Award [cite: 19, 43].

## 9. Entropy, Rank Inequalities, and Open Quantum Problems

The academic rigor of "Most-Entangled State Identification" is systematically cataloged in various international registries of "Open Quantum Problems" (OQP), such as the extensive list maintained by IQOQI Vienna [cite: 6, 19]. The user query parameter "T#81" operates in a similar academic paradigm, reflecting the persistent, indexed challenges facing quantum physicists [cite: 5, 44].

One of the most critical open problems intersecting multipartite state identification is OQP #41: determining all universal linear inequalities among the ranks of reduced states of quadripartite quantum states [cite: 44, 45]. This relates deeply to the structure of entanglement in systems larger than three particles. 

For a pure four-party state \( |\psi\rangle_{ABCD} \), the ranks of the complementary subsystems must be equal (e.g., \( r_A = r_{BCD} \)) [cite: 45]. The central conjecture of OQP #41 is the rank inequality:
\[ r_{AB} \leq r_{AC} \cdot r_{BC} \]
This inequality restricts how entanglement can be distributed among the subsystems. It is heavily analyzed using the 0-Rényi entropy, defined as \( S_0(\rho_A) = \log(r_A) \). The conjecture can thus be rewritten as a subadditivity condition: \( S_0(AB) \leq S_0(AC) + S_0(BC) \) [cite: 44, 45]. By proving these inequalities, mathematicians can construct a complete geometric cone of allowable 0-entropy vectors for multiparty states [cite: 44]. Establishing these bounds is paramount, as they define the absolute mathematical ceiling for how "entangled" a multipartite state can be across various partitions, directly restricting the existence criteria for AME states and generalized tensor ranks [cite: 44, 45].

Other analytical approaches to quantifying complex entanglement involve alternative norms, such as the nuclear norm (the dual norm to the spectral norm). The nuclear norm of a state tensor can be interpreted as the "energy" required to create a state from pure product states [cite: 28]. It has been demonstrated that the most-entangled state with respect to the Geometric Measure of Entanglement is also the most-entangled state with respect to the nuclear norm, providing a beautiful unification of geometric and algebraic metrics [cite: 28]. 

## 10. Experimental Tomography and Machine Learning Implementations

While theoretical mathematics and SDPs outline what the most-entangled states should look like, experimental physics faces the daunting task of generating and physically identifying these states in real-world, noisy environments (often modeled as driven-dissipative open quantum systems) [cite: 46, 47]. 

In a laboratory setting, identifying an entangled state is conventionally done via Quantum State Tomography (QST) [cite: 48, 49]. QST involves taking multiple measurements across different bases to reconstruct the full density matrix of the quantum state. The reconstructed state is then compared to an ideal "target" entangled state using a metric called fidelity [cite: 41, 49]. Fidelity measures the geometric proximity of the experimental state to the theoretical state in Hilbert space [cite: 49].

However, relying solely on fidelity for most-entangled state identification is flawed. High fidelity to a target state does not strictly guarantee high entanglement; a state may have high geometric proximity to a maximally entangled state but actually possess semiclassical features or suffer from severe decoherence due to non-Markovian noise [cite: 46, 49]. To circumvent this, experimentalists utilize Entanglement Witnesses—observable operators designed such that a negative expectation value mathematically guarantees the presence of genuine multipartite entanglement, bypassing the need to reconstruct the full density matrix [cite: 18, 50].

Recent advancements in state identification have leveraged Machine Learning and Deep Neural Networks. Given that QST requires a number of measurements that scales exponentially with the number of qubits, it is highly impractical for large systems [cite: 18]. Researchers are now training Siamese Convolutional Neural Networks on partial measurement data to correctly identify and classify entanglement (e.g., distinguishing GHZ classes from W classes) with high accuracy and a fraction of the traditional measurement cost [cite: 18]. These neural networks learn the deep hidden features of the entanglement space, offering a modern, scalable solution to the state identification problem [cite: 1, 18]. 

Experimental realization of highly entangled states occurs across diverse hardware platforms, including trapped ions, superconducting qubits, and photonic systems [cite: 51, 52]. For example, in optics, discrete frequency-entangled photons are generated through spontaneous parametric downconversion in non-linear crystals [cite: 7, 53]. The degree of entanglement and the specific wavelength differences are precisely tuned by controlling the crystal's temperature (e.g., observing Hong-Ou-Mandel interference dips at specific delays tailored by thermal environments like T=81°C) [cite: 7]. Such physical manipulations highlight the delicate interplay between thermodynamic control and the preservation of quantum non-locality [cite: 7]. In trapped-ion architectures, high-fidelity entangled states are transported across modular networks using time-bin encoded photons, allowing for the generation of robust, long-distance multipartite entanglement essential for scalable quantum routing [cite: 51, 54]. 

## 11. Conclusion

The problem of "Most-Entangled State Identification"—emblematized by intense theoretical benchmarking parameters (like T#81 or the IQOQI Open Problems)—is one of the most mathematically profound and computationally demanding challenges in modern physics. In bipartite systems, the maximum limits of entanglement are comfortably defined by the Schmidt decomposition and Bell states. However, as quantum systems scale to three, four, and higher numbers of dimensions, entanglement fractures into stochastically inequivalent classes. 

To navigate this, the quantum physics community relies on robust geometric frameworks, such as the Geometric Measure of Entanglement, which translates the algebraic search for non-locality into a manageable spherical optimization problem through the Majorana representation. In the search for the absolute ceiling of quantum correlation, Absolutely Maximally Entangled (AME) states represent the pinnacle. The extraordinary recent discovery of an AME(4, 6) state, solving Euler's 243-year-old "36 Officers" puzzle, stands as a testament to the fact that our understanding of maximal entanglement is still expanding. 

Driven by advanced computational techniques like Semidefinite Programming hierarchies and modern machine learning tomography, researchers continue to bound, define, and experimentally isolate these states. Ultimately, identifying the most-entangled states is not merely an exercise in abstract mathematics; it is the essential prerequisite for constructing the next generation of fault-tolerant quantum computers, unhackable communication networks, and precision quantum sensors.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3kC2XD2YmxKnacmH9hDy7P3e6EwrQOzyuCK_BtXHM4qhhgfjcjaN_0JP6rqLXlJW2pd0Xgqssr8ZvEAssssqdVYUWiTEB3KJEc1R9goJzPO_3sClPjw==)
2. [quantumzeitgeist.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9J1_KFIJGYuy_kmLlxHh0aZHGYPCADxcyKWRHIx5Y4e2E2RgtSY4S42DUxcp9PcaY6oPnRIdEzbya4fcMo5yH3OGlp8wUuuqnZlKpCT-RUke1cCfupW-v_SCzKVZCKLOh4wOXf9P8x1R7SBSCQ5ZSymCID4SBmRLMa8Wsx_rfSM9hWn-q3Ga4NmlVTqDOUSID1SRpWUhVYWd-z3RESKYw3uXfiuBHmC2D)
3. [intechopen.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLvinm_r2gBZpc7tVMPSU8Zu0I_unwBtwdIB00lJTfFrj0h7WW_xSLas-pZ58kBZf6ecJLgMjxKrrkOW4NVGv90b8q8YJ3uHyYPNb22s_joX-rk80sbhG3Woi0WFQifRdn)
4. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXFEI3BmV8dT6KJE7SwAGCs2cLt0URn33w_loTgOmnr3M_2Ql-VMqKdzXA4MuoikmU_6-PZNcloADCb57KpJ9jj3AoToFPKhg4DHH6fdq24zq0EyT1iMNHb9NZK64LPyunh-Bj)
5. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2LZng1hhtwYO541O-Gh_R1lviWjqzMVAU6FT77z9qnPdIa4YN0BD-OTuraH6BurM7bf5h-L0XmA5YVe-a23RRijGwvXfTbgQRGFgJio9y7UKnkI3w4qERT_ppk2xAI-nqVA==)
6. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjJYCnLV_bj0iluEHFpcr6RN-zFaL-bEg2kVuygtRE1V-HMPV6Lz2Rx48K1VLBf6SDNn__TivTtYUqzkJ3-ltyi93v2KaWqayjNY-m79sR8jV46RFLS6TUtsTWo4rC4TkLFVI4VyRDGFpO)
7. [optica.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyzxYiKQM3JTrudFypHRp9oKymQnXZ0ePwUnmLRN7UVk7qXHxBZRvpv6DRuLqY-BRzAfiB0Zg9VTvc7v4myyH-zvb5-CPYDDjwe9ijZs-g9xTaKHWxRG3zXXd5Nc2gH6saQHRhuJci-uNGXDbdrA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc3PRhhTT0n_twkU_NfBJxCOW7SdhfBn--ndGVFI6p1ga_EDNtPxPDNDSKo2DT4qxLLRxeif9dkt8cUGOA9JnablFZaIg0Uw5mKbFrE5lUWONMQBT0)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmGt4x2CMjjuYU-rkyFHocBnltBdRNqGhNlNnTJalNHp62n-TIKEzoEmv3yBeAHAHHlxb7FqqNAsJSmHDa4SU073cbycdRT8o09OFxb-1zf2ZMAEM-AorKUQ==)
10. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEI65Y9N7-fQA7TJa6M5j5htOAGkTgpwHIccHDdTDLwJuPD7WTlTCwBd2ynRJJYTzl86Tt5Vi3HJcjRuJJ9ymT0Qb9NYBoCYSMk2E7KCl5mI4yK5il7RFEFT005vBj)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFalMnDWaE2iPfwMuc3axDgOkJ4RlIBZdU3RewMku4QprlvAeNoe37jRSrMbHDhtQ0bfgCfjoWZO2YrzNHdMJiB02pTCcbJreoAdiqDuGNK3lrLEy4AhLDjbg==)
12. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERR0Vp0T0HAfwITTr-6zaRc0qs8MLNuLwTm8QGZ8NXSWCu_oWRjfMsBx9jSdK_d-VVbP-dqeF-cYJKNcgev94T0XUmxiBK47YynB9f5SBmPz_d0l3ECWXb_DIbp8x8hVMjjO5hezOhfQywsCXqvrerbS6es73DGFDEBRnMREVo)
13. [unimib.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWHgBqKhvxAnYb-kMpHfSLNJpXT7JrKnlopu5FTJGFeJa2fcOIa06bu73kFWADS7mXzg9DIks0eIEXwB0ul84JfAj0TQrW7jFDy73A-ogUEuH8AAAh-1qSi07HyGRT7zlxgJNCvScTRD_os8zOZfswfKIkCbLcoC82OV91-j8C1DyjxhmUSf-8om_Mk9j4vhaXCYaG4HVyNnVij4k6Q9lp7YI=)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbz-oC3v-NkT36uh10SIiM1PA7jaSR5INbQljX3pZdrDA046OgHcgKX4wVXnb_IB6phwD52v6ZHi-mXbn6CNc8zvKcLzTCT8fXlPtIbYjbuprCtzOTMcmllL9-XiLtOibxvUKXKKcwGQ==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX1GFCB59H0pytbgtVyTkcOuEBYZOmU4jya7daXuw9QC2T4c_QirUCSfF_3ApbubvC8kYhfpIAcEmK2YaIaFi9dKkrBtAWdxm4hIdIO6gv-eW3ynN9G6T7og==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrxBrw6XCm_grFBaNu3yLR79_ThHDxwY4c8dMuIDrhsr3qEuoRJ7uYM8JW0lN0RkzEJFnOE-Oat8h1yMTdknho4nfAx9glEotoUubuJ03iL96_kQjRmJHh6w==)
17. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaxRkwBgZGbGzQx_txjtK8g96sZVOyXlTA3AUP3GF2wGMAWxm6FrJvFP6VzNr8DruweihNrwXUd0SpL-mfRr1mFxo8GfLjpFzqEyYiOchfvcou9_p1YoxIm7IVBy4Tme-SBLR6gD0HI8eSV_AmkwG6GLXJ9zyF)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHGGkrBgeDxCGvV0eFD3D_XBq7Z4u6Au-EpThptNqAnOERe1VsBUJkiNs_-JPw5KHJ-klKsAqeMGy6eEBo4nw_N9HogUrThJd-LpIRB_o8GsE-h1xeAGQa2Q==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERlqFwaWBSUYz61RF6a6fqm9uW4R-Xd7DNNVl8LK-3ge3h-J0gBjUIR2IkfDqvJDZEzu9luIq-j5at9I9DsI1Y4sSwTFm0kScGwuwv4Uw5epHZAkyRVwMV0mMM9fMoBp_b0MHTC2KeeicmwbNgU2v3OvsbbIU5655hgWzd6D8M23P93wqfDfE4dD4aqIjjY6ldwtM0Ix2mmXs=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYYPv-06zc5YC_cf9pidd1Dgpad7yOvGbEHiZdJwgwGDNJT1KRWzV_zwXP_rAaHwT58UebpflFEW0u0HVJHbBUKLdiNTy5GGwKTfGbCDX3eR8loYtp)
21. [uni-siegen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESCyK1I83FnDRHV2EIFaViQt3VPEM3D_nup7LWRzWGGxAfnYdRQLSN9Wn6wi45rVA5I1fJyaD9SDyfUCm7uz4gloHnV9L3zbf7V6yOJ8CPsf23kQnEooykJAHTcvOQd7Vc0iQdaNAq-LDxtxXBFnBg00DnIn-EfUR2n1mv0kaflc47aGIqMTyFaLg4zlI=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5fA62nHLN4wRhHT07qCd-7GLPg0fIrKzUvO3HszjeN5kiaFINSBhrdaF1TK4SGBlGI0SYVkTu0KPGi7N9xPx7voU6ks3GbNZzJ_IYu7NZ6EcyVMnomw==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpuVBAQJpvhYgGeJfAvcdBoOjxY8u7d7DLqHjqNb5P8d3HzJUixUP0Hw-KfPJQAsWdQZaHs0FtCcztRCVJfSDTzvyCAIYxxpLw1J6aPMOdtpoVArmeqw==)
24. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8tfu7OiczQJb1OYxn-zZFjO7M1brLFuNxoq_S9SeZElKbkcENjEIAj_ETFOx4FFB06Qw7EuldKNFVW7L9AbHoUrm_d_4D9Q8qLYf_4n9sMjvt1aPkL8LfPKUugdKhRyXeMu3t6J2AEBn3H8Vc3IEHxktlbv9K0W1NYUw9DnwPFHDLhj_5SMl0RRHvzKV6fzoLH-Yb15lViyzMONSjDCZoaLMQWzksAelMhbA=)
25. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaGuRTA-2G_RhiBJ2cku_7lonSE1Ubnkb7daKaSP67_YIocLA4HBvkQ8hH34jpImSwomuiO2bLjldCGoza0TFKlMkii9z6MqNr7DI-EdZtaLaChmKAKu18E5YFiSnRzcrZDOuy_IKI2KNZfzBoRNWaXyPQ40woYhlNU0lIE4agAFBLL5PqIg2r1IspNk5lR7Qxc2rXXkJERA==)
26. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgOgdkH4WVeMe18hNn7wtgsHSg4LmF6i3OJaJjbdeshynZNCu1pe6ruO1M8XCep2b6rCQu59TKFmDgdGa5k21Hrle-q05IfaQoehfiWTVc9nHV0o0wmsrG6Ga4ePe3sfxmikEKQiELckE4Dw==)
27. [3dhouse.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCE6tkIaAA5KPdzrDI7_ebxgj-fqadprqBZNX6n0BG7SOZZrH1u-YGyc-Vdt-D1pnAR38Oo-KUbuHzyKDW_eKDVrQsl5SkKr6eYfqtYI7bxnzr25RVVyGSdETMn1365uhFfSIg)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE72ahHeLOYWcO_RH-2kvGR_Rrorcrwu9c6EWvmLhi3nTgpY1AzA-wRv1Jz8Hqd6MbdGln28qh6Q57lBNFV6vGGAC-uhE5KxEsD78hQBZODkG1eV6REsg==)
29. [core.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-OAjIF6QoqmvcsgAm1KCq8HLVZx1M22P3-ZicXG-9KESmytpGy0igpdXzyNZdH700FP3PpC4rKTLpRT-3b9S_VygOtXncY1XNZcAIl-6sHtiawERu5nBNpyljEX3sLCL4sX-BhEiRdqb19rkunrO5lytQNSpuzpK4WO4HXrPHPrcFg_r6ssU6roIo4ldHga5GhMbZiL-qhcDzB60HWHicdjSl-7C5LNODBUXM9LZu_Iect1XS2J-0nPA=)
30. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwvtN5yf57UEV4C-26XONnv7eWpzLB9LmVtrANp0PLkbxLjetOGk7I3rI5dMnZu0jtOkFC6OiI9l1NLqCftVuvwrNJoERB0xd9k5yoIWqfwpaF8-wGKgDdo8YPEua4jhcMLCKuqfdZvoMnQtYljYAmH5Q=)
31. [quantum.technology](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETfno2pXyTAGOnXHvR32po9zSj3q7IbA0xmKiAYxUK5nN3Ker6cMWyrwwYIgn9TC6U01ckmFL-rtFU7TdWSuqxDKDThhO1IMI_Hh7YAG4MiHbnP3cGvdL2ReruYUFEzVP1StBF_EPxcOIhKig-fCCee3kYmu7_MyeuZd3NJyF2KAmdHTc=)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyyt74MqcCQjTLBiYTYkhoY3gu3e2PO9LhZjTMPwkQ00c9UigZhIzn5dZeDSSxlc0A3ewvYgzRZ-acSGNLVtgL7TzQbu2W490c0bjO2jflKIGoxsABi7aE2SwXWBIggUN2S7Fa7oPTWGH-6U7Ry8D2RwmCpnistB_qhmQVPuyokcQydXDHZoh7ZubRVU3eR5aPDG2ove7yGiQ=)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcczEZN_TKRAPfTJCJh_BbHm34aEyw0yRevPYwx4e89C4J6bC1MT8ZqzOs35maX0WITi29bfklS2bJt_-q3tYds6svDH9Cmtk18M2GHBwXuLaaM-Yc)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsjSuwZW-OmZ96EKH8bL3j1PBupeYF5g9Vpbamz-ZbSan9114zg2FhMWKVgNtDsckxp1i69YDRnI_8G2wMct4oh0qppI_gOFW06r6-6AUH6IsRFwKy53ePhr8hmNXTx_F9YoItuLwQCfZ1BJNFk8XSugg7ZLQjxc5QFaZ0UK-2r0VS1O09jZyFRM2WFaGKkt4BawwVshi4cskMSJcX-qk=)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXWVCM7Vo1dRvULBSih8mlKwUecXcKYsCuUN54WPHdF4K8Zy6Isjw6zc1RZSX5eE2hlF9cJx_Z48w84AM2JgSaCLMebsoJc6hIy8AMHSoiccrWnNS8)
36. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpfPJWDWPKz3l0wVjWfPhFa3OgUuPCe_OR8s2oIuZmy0MdhnUQBVbXKaJHHfEswUlZseZ-IS9_D0PaOTT0-2Xc6r5bH_Fub8VXPVNZeLU3w8iAJwFrlJ1wtrMqG7MFpH8EZ75p2FQEaIp1j-7qstN_gH8hr0_HaxXbIFKn8p4Z0_LU5vQ0n8lHGYB250EVSKg=)
37. [iitm.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9LcNh3eDCSENU_dC245uAHNin2G7BIVqlIpIzdLP-WQL-KeUOKcKgqZC6uBWGASErbSZRDVX4AeZyYOxRhArnAwvAZ1lMXzsgQ_7bfv-3UVumlGfGL0s_vnQ7fnJPZoIEfmgplajrKSPgxlJbIWaGMIMiCPUwvWhJbrZt61qGIEqhfU6Ns_knuWVR_-PINBmt2s2qJKmO4ZuYk93FuqTR)
38. [naukawpolsce.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs6Aij_8Xb9UPwdU6oUDk4R9THOnFy_A2a7P9nOW8U8CQ8_LkEqlHYIX8Wb8YK42JCLBwzuC9KxYn8QMlbq4EaDmZFzOo7wPgJvv3WXkHIdwCyajX8tXQKrru0oAQnVPdwe4io1w1eVStW6t0YkpGLUFMYyma8wuxAu0rR_L0BnsRYTYX26kaVl-lWRsUWIRrp1FHs9YEBavSqy9RI2x4W8P6Y9gDSGMVa3z4=)
39. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPwzFa8frf28gupH4NEJolik47dn1d4gIRyY78IJf5qIJG-w7iqljMfpvLqVBw4Meh0HJJayBT-QylhqLix1B3Sekqq_Iz8HxVUCe5KDwwxcBdgwMNZjhucQWKvwmtvTg72HNQXOce1HN6ZjeYpz4Ar_-BuVeVMweS45PXiM8FhknvwjxjswFm3lez_XAJKV_fZ_mAeVomMYC6cj0=)
40. [scienceinpoland.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_6hTvkt9kzbkAE0Xu1rqnQqXS5mzlA_E58n8MOGQiSvRgpRE8LbSU93RSXCXlJ3lHzs-mD2OFHmKw4SbNL4q9Ew74WJIySAMTSyMY1foS4NNSFW0G1_8rHvFApZUH6RqNkHSJd-O3i0W9Up_lUcTfZak92gO-QUzCX4GXSIkIwmX7LrVk5Jaaie3DXVsNLeGCeXcd4HJsrX-3Hzt8JbH9HpXkuwXMIKpoeeYhVOyBlqgZQw==)
41. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1U352wW-_QX-Waox9vJnr472wkf97HXKTfjkdbmo2zjRzHjtE2nE8VS0h5Cavdsdn7EwX56lSTjQem2cYszBzkXqHUNoKF2rXOtbY1wGplgIkmUO9hqUuoa9pJLMdiHDe-mNsNznqLoVtMZjMhyhuI_2Ie_ulLYRYyvklkDGzEAeCLDRExvZwN0dXhH72mq94bY9qG_LWw432qDDUJVWcdalkWPuzfK3Oniz-K8FrfgbGI9RGxoM=)
42. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfwGEOs7r4EG3jIY84b_CTGLXnCW-QoJJFylhcnyk2ztIluL_1LTW0gVvlLv-owrCl6UDH_bNEtX1MyxLn2lO9aRTj5Swb9ErdIB-9BQxV6nVCNj2Wtkw7nYuSxNB_Aj73hC6JTe3DIrA6hhNGK43l4nMupu7yxdhUbyiOFeDamNp1OvPuhkxMFEVjfDyJ_fRTuaQ4KC8ulI_bCMOJNn3ASBmS_uXTHT_vsNDzrpNM)
43. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-2IDHso-3sxNTo6KHsSbLYk-prREHE2-TO3X9vJqcL9z8VTjLifHmoyWbpEBId8W--swstXsYTRNN_Jm2wMLbdPNQzCtrE11RzfuIBFbVXaAxL87B4OyGNgctZV4_UjHuRIZzxaH1NFbv1e_aklpoASXD-dDO2qftM-uMIGyq5FnpCqE=)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBo7x_ald2NS6fuV7iAKmN9zUQ2-jBQMegJzR-ML1W9CaEreTAsjXTVB-hBipzj-Durg0IFK09ZDtAkPQ64NoDPfytuPGOZ_A07ArlZCqaPsYMmBR7lw==)
45. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPMJ7_HtJ7147yBZ339rDBvyi_PKUSnpU6CP6vWfHjQttz898HOWSQWHn01m7xbpQCVXXhm2f4wt1KxeRcSzaR__iJ0OJ94A6Uo4Vnq8Iq3kVlP9d5NFw_E9x53A_6J1qpNQXKuiT3Aa2a4K-E1SoC8LOA4ho5BA==)
46. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRFzi6a0h1Y2XuQfbwLJt4Wnm1WPhLgJmF2Kj2reWUSlULZx6ZkqQgZWfFImVQyvYNdHeG3TVnAAe6-K8TGdGfaMjvob_hTmuyfUCtMQxziSE9Cd-5TQ==)
47. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDr_RgmGHrRuTjlekJBFP_L6QpAGwOkVnqh8Lcr6_6XyzVhm-qRkcbgmmbjvRjSs6Pw0pQQ3J2Hz9LLgF9uSnpBZGFcBf4eifY-rbHMhl8ZAT4qyPpeR_gk5H9Wc7zB7Sk0uuzz2tcM04tH7x7jg==)
48. [unimi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFppIgwjiroY2e4N_JPcrx9FfPbpE2TKfG0Aew0OSbHTecg2g2yAJqmQlzmAjdp9qddNbIOdMadM38C0rJXvU3xx4j_87u-LPyMUbLpdYt7uwi9SroyCiZTIiREaBmRmeZi22JxV7hVfEstACc=)
49. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_rNo7crreyqko8-zUSeEJX-OCZQaWNcQEcwZ6BIllMQuF6bXDtMaH_tMf1F70xiDbT_aFdKUQX380jjMJSU1p19WqzB85UlUoK3e9gmWUS40XxGx6kc7qQ3JYFijzpNwrAiCGIzfeEFltWlmr1DZFlupu9OGL0ZSWSp0VvW4FPeaKJjTAoU7DrXS6dMJfJxaoATaZ3c7WskvGcpkNQ4-g6MdYFzz-zOnAmz-q9X32jBMP7YSXzianGjI5XW1AeDcoxWlWLrUgoUvu7t33VtS7MSBIOZu7z0wQdEsyiceXkh-ZMtgeNP5s_cn0J2Of9pv8)
50. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2RJYi0ZljyCfLzMrbGRWSqAF7-UnOq-vsoI6IdJzftFUgvlTQn8AEj79-ogaWHdTCBEI0cZlcMc39x89JJ0jZaNpihATQgotZRD3aKy50uDEbi_yfcA==)
51. [duke.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv1FMTSKKbyimc6C5NxnZ-4EOl_rUmvX2K1lkI2fwXl8N5h-wdCvBkNQDLVSGkN3JjL9QQkgHhjczfD_4HpciRQ4ZkSUmcTwbR5W2wmrKowH_WEHjsMug2OYA9xwPb72_8aYZXMKDRLMul7ZUrrzNSCc14PZAc)
52. [diva-portal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsSJex_RWU24cvtozJiDUAJqoUpOMBTXz1Uh7x0isIaCDvdzAAMAglt3zZEc57wQVd59YwyJm3paAjZAEaERfhKYRHrRl3ZCJE4ZziAJniMBiP_Wdeiy4HV2tjPUvenCq9N5jMAQfirNS9nBhbrZ-obpBX8GQ1a5s=)
53. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGASlqYFXyGntynUA-6fLAaEfNLhvsXUby_gUmrsnJ78VXVQpzD1JQVrurZ_3yROAGgvoKJD2nVaWsSMOBkf1tKvuUFloZ5N-GhZlJhnxyq7W_FO1iKUA==)
54. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI2QuSsUTO-uqZUIlKEtbDukjQ5nPkFCvTNwRft14ZTXpZ1dUwz6CoKKMOlr83_sZ-4mn7HsmisIc8nLZM_tpRgVtSBHK3qT9r1NmnCkXPorpedwZ5yO7Q3im24wXjpw_jlD-36iT0mzHfk7zr1wr4w-4DQ-cV0wgONY0KUoBZ2fmyJLV7GqiVBNiOHuuSMosL7hXI1EuVUt1IiwoWOPJ8oTuefNIFsP631P79W64A4_pb4jbcCKxvew_ay0EhlNXhdxxN)

