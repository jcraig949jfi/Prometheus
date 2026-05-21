# Argos lens fingerprint: Discrete logarithm in P

**Pythia queue id:** 259
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlM1lQYW9QaExNZlJfdU1QNGRLTG1ROBIXZTNZUGFvUGhMTWZSX3VNUDRkS0xtUTg
**Elapsed:** 368s
**Completed at:** 2026-05-21T21:23:57.394150+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem CS-0013 (Discrete Logarithm in P)

*   **Key Points:**
    *   Current evidence strongly leans toward the Discrete Logarithm Problem (DLP) remaining outside the complexity class P for classical computers, primarily supported by information-theoretic lower bounds in generic group models.
    *   Approaches leveraging the `STANCE_DYNAMICAL_SYSTEMS@v1` lens attempt to linearize the nonlinear modular exponentiation function using techniques like Koopman operator theory; however, findings suggest that the necessary dimensional lifting suffers from an exponential scaling curse, reflecting the underlying hardness of the problem.
    *   Analyses under the `STANCE_INFORMATION_THEORY@v1` lens conclusively demonstrate that algorithms treating group operations as a black box must perform $\Omega(\sqrt{p})$ operations. Any prospective polynomial-time solution must fundamentally exploit specific non-generic structural properties of the target group.
    *   The `STANCE_RENORMALIZATION_GROUP@v1` lens introduces novel cross-disciplinary tactics. These include Tensor Network representations for cryptographic sieving and the "renormalization" of constants in algebraic descent methods. While yielding quasi-polynomial breakthroughs in small-characteristic fields and promising polynomial scaling for small instances of lattice-based optimization, these methods have not yet generalized to a universal polynomial-time algorithm for standard cryptographic fields.

**Overview of the Open Problem**
Open Problem `CS-0013`, commonly known as the "Discrete Logarithm in P" problem, asks whether there exists a classical, deterministic (or bounded-error probabilistic) polynomial-time algorithm capable of solving the discrete logarithm problem across arbitrary finite cyclic groups. Formally, given a finite cyclic group $G$ of order $N$, a generator $g \in G$, and an element $h \in G$, the challenge is to find an integer $x \in [0, N-1]$ such that $g^x = h$ [cite: 1, 2]. The presumed intractability of the DLP forms the foundational security assumption for highly deployed public-key cryptographic protocols, including the Diffie-Hellman key exchange, the ElGamal encryption scheme, and Elliptic Curve Cryptography (ECC) [cite: 3, 4]. Despite the existence of Shor's quantum algorithm—which solves the DLP in polynomial time using quantum Fourier transforms [cite: 5, 6]—the existence of a classical polynomial-time algorithm remains one of the most rigorously studied open problems in computational complexity.

**Scope of the Multi-Perspective Analysis**
This exhaustive academic report applies a multi-perspective fingerprinting methodology to problem `CS-0013`. It evaluates three specific analytical lenses—Dynamical Systems, Information Theory, and the Renormalization Group—as proposed by the Argos schema. By identifying the two strongest primary-literature attempts within each lens, this report synthesizes the projected measurements, the verdicts reached, and the fundamental axes of disagreement that define the current theoretical boundaries of the Discrete Logarithm Problem.

***

## Lens 1: `STANCE_DYNAMICAL_SYSTEMS@v1`

The dynamical systems lens recontextualizes cryptographic exponentiation not as static algebraic equivalence, but as the evolution of a discrete, nonlinear dynamical system. By translating discrete logarithms into problems of trajectory tracking, Poincaré recurrence, and orbit identification, this lens attempts to utilize continuous and discrete chaos theories to evaluate computational hardness.

### Attempt 1.1: Koopman Operator Theory and Cryptosystem Linearization

**Primary Literature:** Schlor et al. (2023, 2025) exploring the Koopman interpretation and analysis of public-key cryptosystems [cite: 7].

**Context and Application:** 
Recent works by Schlor, Strässer, and Allgöwer have reconceptualized the Diffie-Hellman key exchange and the RSA cryptosystem as nonlinear dynamical systems [cite: 8]. Because modular arithmetic introduces severe nonlinearities that make system analysis intractable, these researchers applied Koopman operator theory. First introduced in 1931, the Koopman operator allows a nonlinear system defined on a state space to be represented as a globally linear, albeit infinite-dimensional, operator acting on a space of observable functions [cite: 7, 9]. By lifting the finite-field encryption maps into a higher-dimensional observable space, they construct an equivalent linear system where recovering the secret integers translates to solving linear equations.

**(a) Measurement Projected:**
The primary measurement projected by this attempt is the **minimum lifting dimension** required to achieve a linear representation of the cryptographic mapping with perfect accuracy [cite: 7]. This dimension corresponds to the number of observable functions required in the Koopman invariant subspace to fully capture the dynamics of the modular exponentiation $x_{k+1} = a \cdot x_k \pmod p$.

**(b) Verdict Reached:**
The research concludes that while the nonlinear cryptosystem can be perfectly represented as a linear system, the Koopman operator cannot be effectively truncated without massive approximation errors [cite: 7, 10]. The required lifting dimension scales exponentially with the size of the key, exactly matching the complexity of a brute-force attack. Thus, the verdict reached is that the DLP remains intractable in P; the mathematical impossibility of dimensionality reduction in the Koopman space mathematically reflects the hardness of the discrete logarithm [cite: 7, 10].

**(c) Axis of Disagreement:**
The Koopman approach fundamentally diverges from pure algebraic lenses. While index calculus or generic group models analyze static properties of prime fields and collision probabilities [cite: 11], the Koopman lens views encryption as a kinematic flow. Its disagreement lies in the methodology of attack: rather than attempting to factor the group order or sieve for smooth numbers, it attempts to bypass nonlinearity by trading it for dimensionality, positing that cryptographic hardness is intrinsically tied to the irreducibility of functional state spaces.

### Attempt 1.2: Chaotic Orbits and Poincaré Recurrence Times

**Primary Literature:** Chirikov and Vivaldi (1999) [cite: 12]; Schmitz (2001, 2008) [cite: 13].

**Context and Application:** 
A separate sub-lens within dynamical systems maps the DLP to the behavior of discretely chaotic orbits. Chirikov and Vivaldi analyzed discrete dynamical systems (such as the Arnold cat map and modular exponentiation) to understand pseudo-random phenomena, defining the discrete logarithm dynamically: it is the exact discrete "time" $t$ required for an initial state $x_0 = 1$ to reach a specific point $x$ in a periodic orbit governed by $x \equiv b^t \pmod N$ [cite: 12]. Schmitz extended this by formalizing the necessary algebraic requirements of cryptosystems as properties of discrete chaotic iterations with maximum Lyapounov exponents [cite: 13].

**(a) Measurement Projected:**
The measurement projected here involves evaluating the **maximal and average period functions** $P(N)$ of the orbits and the **discrete Lyapounov exponent** $L$ [cite: 12, 13]. The objective is to measure the Poincaré recurrence time—the iterations required for a chaotic orbit to return to a given neighborhood—and determine if asymptotic bounds can be established that would allow predicting the orbit trajectory faster than step-by-step iteration.

**(b) Verdict Reached:**
The dynamical analysis reveals that for these specific chaotic maps, the discrete logarithm is associated with violent fluctuations in spectral and Poincaré recurrence times. The period function $P(N)$ requires knowing the prime decomposition of $N$, linking the orbit length directly to integer factorization [cite: 12]. Because the Lyapounov exponent $L$ (often $L = \ln(a)$ for a base $a$) ensures rapid separation of adjacent trajectories, short-cutting the orbit is impossible. The verdict is that the system acts as a true trapdoor function; finding the discrete logarithm iteratively scales exponentially, $\mathcal{O}(N)$, proving non-polynomial time under this specific mechanical mapping [cite: 12].

**(c) Axis of Disagreement:**
This approach disagrees with algorithmic lenses (such as those using Pollard's rho or kangaroo methods) which exploit random-walk collisions (the birthday paradox) [cite: 14, 15]. While Pollard's methods treat the sequence as a memoryless random walk to find a cycle [cite: 15], the chaotic dynamics perspective treats the sequence as a strictly deterministic, area-preserving chaotic system where the "hardness" is a physical property of the space-filling nature of the orbit itself, rather than just a probabilistic collision bound.

***

## Lens 2: `STANCE_INFORMATION_THEORY@v1`

The information theory lens evaluates the absolute bounds of computation by analyzing what information is available to an algorithm, what information is required to solve the problem, and the minimum number of logical operations necessary to bridge the gap. In the context of the DLP, it abstracts away specific algorithmic tricks and looks at the mathematical limits of extracting the exponent $x$ from the distribution of elements.

### Attempt 2.1: The Generic Group Model (GGM) Lower Bounds

**Primary Literature:** Shoup (1997) [cite: 2, 16]; Nechaev (1994) [cite: 11, 17].

**Context and Application:** 
To definitively answer whether a "universal" fast algorithm exists for the DLP, Nechaev and subsequently Shoup established the Generic Group Model (GGM). In this model, algorithms are not given the actual binary representations of group elements (e.g., integers modulo $p$). Instead, the group elements are encoded by a random injective function $\sigma: \mathbb{Z}_p \to S$, where $S$ is a set of opaque bitstrings [cite: 18]. The algorithm can only interact with the group via a black-box oracle that performs group additions and inversions [cite: 11].

**(a) Measurement Projected:**
The primary measurement is **query complexity**: the number of oracle calls $m$ an algorithm must make to determine $x = \log_g h$ with a non-negligible probability of success [cite: 18]. The model calculates the maximum probability of an algorithm forcing a collision between two internally tracked group representations.

**(b) Verdict Reached:**
The GGM provides an airtight, information-theoretic lower bound. It proves that any generic algorithm must perform $\Omega(\sqrt{p})$ group operations, where $p$ is the largest prime dividing the order of the group [cite: 2, 19]. Because $\sqrt{p} = p^{1/2} = 2^{\frac{1}{2}\log_2 p}$, this time complexity is strictly exponential relative to the bit-length of the input. Thus, the verdict reached is that no generic classical algorithm can solve the DLP in polynomial time. Existing algorithms like Baby-Step-Giant-Step and Pollard's Rho exactly match this theoretical optimum for generic groups [cite: 2, 11].

**(c) Axis of Disagreement:**
The GGM explicitly limits itself by assuming the attacker cannot exploit the specific encoding of the group elements. This forms a hard axis of disagreement with index calculus methods (used in multiplicative groups of finite fields) which absolutely require specific group encodings (e.g., treating elements as integers that can be factored into smooth primes) to achieve sub-exponential time $L_p(1/3)$ [cite: 1, 20]. The GGM asserts that the DLP is generally hard, meaning that any instance of CS-0013 being "in P" must come from the algebraic structure of the specific group, not from group theory itself.

### Attempt 2.2: Structured Generic Group Models and Entropy Leakage

**Primary Literature:** Maurer and Wolf (1998) [cite: 16, 18, 21]; Wu et al. on Structured Generic Group Models [cite: 19].

**Context and Application:** 
Recognizing the limitations of the pure GGM (since real-world cryptosystems like RSA and finite-field Diffie-Hellman have distinct mathematical structures), researchers expanded the lens into the Structured Generic Group Model (SGGM) and analyzed entropy relationships between related problems. Maurer and Wolf explored whether breaking the computational Diffie-Hellman (CDH) protocol is information-theoretically equivalent to computing discrete logarithms [cite: 21]. More recent extensions incorporate auxiliary functions, measuring how much entropy is lost when attackers have access to side-channel structures like polynomial evaluations or smooth numbers [cite: 19].

**(a) Measurement Projected:**
The measurements here project **conditional entropy** and **computational equivalence**. Specifically, the models calculate the probability of recovering the discrete logarithm when the algorithm is granted structured advice—such as access to an oracle that exploits the multiplicative structure of smooth integers over a $\delta$ fraction of group elements [cite: 19].

**(b) Verdict Reached:**
Maurer and Wolf proved that a generic reduction from the discrete logarithm problem to the Diffie-Hellman problem is impossible if the group order contains multiple large prime factors [cite: 17, 18]. In the SGGM, Wu et al. proved a tight subexponential-time lower bound against algorithms that exploit the structure of smooth integers but are otherwise generic, confirming a time complexity of $\Omega(\min\{\sqrt{q}, 1/\delta\})$ [cite: 19]. The verdict remains that even with substantial structural entropy leakage, the DLP resists polynomial-time solutions, effectively capping the performance of index calculus methods at subexponential limits rather than polynomial ones.

**(c) Axis of Disagreement:**
This approach bridges a gap but disagrees with both pure GGM proponents and practical cryptanalysts. It disagrees with the pure GGM by insisting that side-information and algebraic structure *must* be accounted for to model real-world hardness [cite: 19]. Simultaneously, it disagrees with optimists looking for polynomial-time index calculus variants, mathematically proving that unless the "smoothness" fraction $\delta$ is absurdly large, index-calculus style attacks hit an information-theoretic asymptote that prevents them from crossing into the complexity class P.

***

## Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

The Renormalization Group (RG) lens, originally native to quantum field theory and statistical mechanics, deals with how the parameters of a system change across different scales of observation. Applied to computer science and cryptography, RG techniques are used to coarse-grain state spaces, reduce dimensionality in combinatorial optimization, and manage exponential scaling through tensor networks and descent algorithms.

### Attempt 3.1: Tensor Network Schnorr's Sieving & DMRG for Optimization

**Primary Literature:** Tesoro, Montangero, Grebnev et al. (2023, 2024, 2026) applying Tensor Networks to Integer Factorization and Lattice Sieving [cite: 22, 23, 24].

**Context and Application:** 
While integer factorization is formally distinct from the DLP, the two are deeply connected via their reliance on index calculus and finding smooth numbers [cite: 6, 25]. Schnorr's algorithm reduces these problems to a Closest Vector Problem (CVP) in a lattice. Recent attempts map this CVP onto a spin-glass Hamiltonian, making it a combinatorial optimization problem. Researchers then apply Density-Matrix Renormalization Group (DMRG) concepts—specifically using Tree Tensor Networks (TTN) and the OPES algorithm—to efficiently sample low-energy eigenstates of this physical system, effectively sieving for candidate congruence relations without brute-forcing the entire lattice [cite: 22].

**(a) Measurement Projected:**
The critical measurement is the **scaling of computational resources** (number of virtual qubits $n$, smoothness basis size $\pi_2$, and tensor contraction overhead) relative to the bit-length of the target key [cite: 22]. The framework tests whether the coarse-graining properties of the Tree Tensor Network can suppress the exponential explosion of states found in classical lattice sieving.

**(b) Verdict Reached:**
The research presents numerical evidence of *polynomial scaling* for small instances, successfully factoring RSA numbers up to 100 bits using simulated quantum systems of up to 256 qubits [cite: 22, 23]. The algorithm's effectiveness stems from the TTN's ability to avoid resampling bit-strings. However, the verdict is highly nuanced: while scaling is polynomial within the tested bounds, it is a *high-order polynomial* that ultimately limits the factorization (and by extension, related DLP sieving) of practical 2048-bit numbers on classical hardware [cite: 22]. The conclusion is that while RG-inspired tensor networks provide a massive heuristic speedup, they do not strictly place the general problem in P for cryptographically relevant sizes due to overhead constraints.

**(c) Axis of Disagreement:**
The RG-Tensor Network approach heavily diverges from the Information Theory (GGM) lens. Where GGM asserts exponential scaling based on zero-knowledge assumptions, the TNSS approach shows that by mapping the problem to statistical mechanics and treating number-theoretic variables as interacting spins, exponential scaling can be temporarily broken (or heavily suppressed) via entanglement-based compression (tensor networks) [cite: 22, 23]. It challenges the assumption that combinatorial optimization inherently requires exponential resources if the "physical" structure of the solution space allows for RG-style coarse-graining.

### Attempt 3.2: Renormalization Constants in Quasi-Polynomial Descent Algorithms

**Primary Literature:** Joux, Lercier, Pierrot (2014, 2016) advancing discrete logarithm records in small-characteristic fields [cite: 1, 25, 26, 27, 28].

**Context and Application:** 
In the domain of small-characteristic finite fields (e.g., $\mathbb{F}_{p^n}$ where $p$ is small), the DLP has suffered catastrophic algorithmic breakthroughs resulting in quasi-polynomial time algorithms of complexity $n^{\mathcal{O}(\log n)}$ [cite: 27, 29]. In the descent phase of these index calculus algorithms, elements are represented as polynomials. If the primary multiplicative generator $g$ lies outside the small factor base $F$, researchers must perform an individual logarithm step to obtain a **"renormalization constant"** [cite: 25]. This renormalization mathematically projects the target equation back onto the solved factor base, adjusting the matrix linear algebra step to yield the correct final logarithms.

**(a) Measurement Projected:**
The measurement focuses on the **computational complexity (heuristic runtime) of the linear algebra and descent phases** [cite: 25, 26]. Specifically, it measures the cost of multiplying large constants $q^{n^2}$ caused by the renormalization step, and whether the sparse matrix relations can be resolved in quasi-polynomial time as $n \to \infty$.

**(b) Verdict Reached:**
The application of these descent techniques and precise renormalization constants yielded discrete logarithms in record-sized fields (e.g., a 3796-bit field $\mathbb{F}_{3^{5 \cdot 479}}$) [cite: 20, 27]. The verdict is that for fields of small characteristic, the DLP is heuristically solved in quasi-polynomial time, placing it agonizingly close to the complexity class P [cite: 27, 29]. However, because the algorithm critically depends on the existence of a highly specific polynomial representation $f(\beta)$ that completely splits over the factor base, the verdict reached is that this quasi-polynomial time cannot currently be transferred to large-characteristic fields (prime fields), which are standard in modern cryptography [cite: 1, 25].

**(c) Axis of Disagreement:**
This lens creates a stark contrast with the `STANCE_DYNAMICAL_SYSTEMS@v1` approach. While dynamical systems view the DLP as a strictly chaotic, non-reducible orbit, the success of the Joux-Pierrot algorithm relies on the fact that within specific algebraic geometries, the orbit *is* highly structured and reducible via systematic algebraic descent [cite: 12, 25]. The disagreement is fundamental: is the DLP inherently a chaotic function, or is it merely an algebraic lattice waiting for the correct mapping to be unwound? The small-characteristic breakthrough proves that, under the right algebraic conditions, the chaotic nature is entirely circumvented.

***

## Multi-Perspective Synthesis and Analytical Intersections

Evaluating open problem `CS-0013` (Discrete Logarithm in P) through these three distinct lenses reveals a profound stratification in how computational hardness is generated and perceived.

1.  **The Dimensional vs. Algebraic Barrier (Lens 1 vs. Lens 3):**
    The Dynamical Systems lens (Koopman operator) and the Renormalization Group lens (Tensor Networks) both attempt to linearize the nonlinear nature of modular arithmetic. The Koopman approach lifts the state into an infinite-dimensional functional space, concluding that the necessary truncation results in exponential error [cite: 7, 10]. Conversely, the Tensor Network approach lifts the problem into a Hilbert space (as a spin-glass Hamiltonian) but applies Density-Matrix Renormalization Group (DMRG) techniques to aggressively truncate the space [cite: 22]. The axis of tension here is whether physical approximation techniques (DMRG) can effectively bypass the mathematical limits of functional linearization (Koopman). While TNSS shows promise, its high-order polynomial scaling ultimately aligns with the Koopman prediction of state-space explosion at cryptographic sizes.

2.  **Generic Absolutes vs. Structural Exploitation (Lens 2 vs. Lens 3):**
    Information Theory asserts a strict $\Omega(\sqrt{p})$ bound for generic groups, establishing that a universal solution to `CS-0013` that operates purely on group theory is impossible [cite: 2]. The dramatic success of quasi-polynomial algorithms in small-characteristic fields (Lens 3 - Descent Renormalization) perfectly respects this boundary by entirely abandoning generic group operations in favor of deep structural exploitation of polynomial rings [cite: 1, 25]. The Information Theory lens acts as a theoretical backstop, confirming that the DLP's hardness relies entirely on the mathematical representation of the group.

3.  **Entropy and Chaos as Cryptographic Shields (Lens 1 vs. Lens 2):**
    Both the Chaotic Orbits approach and the Generic Group Model reach similar practical conclusions regarding algorithmic intractability, but from different directions. Information Theory bases its bounds on the maximum entropy available from black-box oracle queries [cite: 30]. Dynamical Systems bases its bounds on the inherent deterministic chaos (Lyapounov exponents) of the exponentiation map, generating pseudo-randomness that mimics high entropy [cite: 12, 13]. Together, they validate the Diffie-Hellman assumption: without a structural backdoor, the orbit of a generator is indistinguishable from a uniform random distribution, enforcing exponential search times.

## Conclusion

Based on the multi-perspective fingerprint derived from primary literature, the verdict for open problem `CS-0013` is heavily skewed toward the negative: **the general Discrete Logarithm Problem is almost certainly not in P.** 

While the `STANCE_RENORMALIZATION_GROUP@v1` lens has yielded spectacular algorithmic advancements—compressing the complexity from exponential to quasi-polynomial in small-characteristic fields via algebraic renormalization and demonstrating low-bit polynomial scaling in lattice sieving via tensor networks—these solutions are intensely reliant on specific mathematical structures that do not exist in general prime fields or elliptic curves [cite: 22, 29]. 

Simultaneously, the `STANCE_DYNAMICAL_SYSTEMS@v1` and `STANCE_INFORMATION_THEORY@v1` lenses provide rigorous mechanical and information-theoretic frameworks explaining exactly *why* the general problem resists polynomial bounds. The curse of dimensionality in the Koopman operator representation, the violent fluctuations of Poincaré recurrence times in chaotic maps, and the strict oracle collision bounds of the Generic Group Model all converge on a singular consensus: absent the discovery of an entirely new, structurally exploitable property in prime number theory, classical computation cannot collapse the exponential difficulty of the discrete logarithm into polynomial time.

**Sources:**
1. [loria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6_1N4b03o5BkEQHYSGhW8tp23mxjpTs1auUhv60ZaXjPfzNb8mI6R558HHe0NVbliyysLlArA8shYzWqBOdr0HVg5GSL3SiyvGG_oJ0CneF7yHW7V_COnHsm35l3twauyubzmFfB0vdh7_ija)
2. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0Zafz_unO-e0E1nlcVCXbSj7QzDkSvNNsR5CRRfkUSAWNhU_9qC9lK1yC0-IXDmAyxvWrPZgWq_Hq3-Edr1FZ57lXhjYUK5bjIINUUi4Ey1BQDRZCS2d8BFetlAHfSO_cgLnk9Q_Xv8D_g1J9wG3tc8swSF52RbL_cDyROCTd9JzpL5wL9SvCUucfHObi4FEeSaolEkQ7-6jIxmg9rx2PARfD6eDRPSqm7VZiVw8sbE5au3x-IU0DO7yEzlVK_bruPg==)
3. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP-0J01sL93FWO-_azQYfCxBt07ZqkpngxCFQIOwvJMvFmw7mJCi8jk3PFwVWS2oE5nBNlDpy1GzOHzs8wpPiL8WK_mkgBP13kJYEiPsMzQQtmSsvjpP8oL947MBXvJWU178EkVdA-JNJS-aei6ZrPYaSFw6mZ4g==)
4. [hawaii.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3nRB0ghu4TrAt-Meycpqt-LgCd5_2JEHQylDFegBmUKulYvJoIlQWDaujrR9KSy_fJDvE3VTLnBrpo_2-UJJUCO0dbKToA7Nubn7jF_nkOjAA2QwWf4XWgOJjYldDI0AxjbWaN2z67UoPt3htnq57HC_nxxBdSr6dqhdjx_jHwi3wlXXt7Cru3BOW63QAFWLcfhRl)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc2HmSOC8JXg820jQkoyt9cqoIAx-SW5MTcxcJf_kAlr9S_jjb77vDuAyStdeBewoRDAWSHmcQBxmmbM2YLbWL2PCky8RCn1iCPTItMNy4Av2sfagYdBPqi3J9ZCXCdiwi-WzI2aVxG8hTZp9bfs0GQcaQDQMhPhOzJneLlPs9NH2aOyhN-wUltUFgA4WzlpC_epcyNJshZtfnF8e-)
6. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvNIL-thQa2nPKxY0RxNZYM0U8FrBvoqY3qoTWWWp3g-svud4gk54SLDMakg69IMqBdUWiL2LlwrZsaxWcN2jgdfShkXVRMks8fW2HDLFfl8X6ptuV_iDfg6Eq8l6pfFCjV7O9Q1WMJVDA)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpuzmnY2lR8EVhrkS2EaJ2RI3SPHBS13mRE4MOydVt_UZTaoVmmYG2vnCyhSSiU74W85mW5KJRziTezlU_X2GyyyEb7Ng_1YbFjHrBtqjA-HDO3K3zZA==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-zfUfqT-uEtR1h98VVxoROZttPuUuhp5X9tPHxqis0_ZCxydgPs3_Dnt2SEpxRdjbTravUgyWPdCvVlmfKtpNgiiniLTVkWaEBxJbdIsKQgDCvsBbJ4t8i4tes4udjY8nj674ROxeRfD61qZ8I7Fz0wYnEL4NqTfegj5G0R4evTDUu9OZZiM_kGWJCSj3C6qflKCkRTobn-bxaCoh6QqjEG-A1biyk8ez9v5fZvOTaDDIoTleY-WZ1w1MAfW57F2TMkss-KA=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkliSd9YVL7SpQqgyFf5EQiZrEPOIfuRPVw-q7CUZmYvglNfw4NljwUn_OMuo7ZAdujO0bQjZrbYbnfFgvjUEalY_HCgn2ZK4pfXNfkEK3w70QwHAWrA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyHWdiFdFztPDVoGTBpR6WaSP6c7mq1HVIx-etHUVVUDP_LgAZn-6p7F5ErW2pUfCqYLmsyIXh2TtTgVKj8SBllJASlDv7Zw-E6zNjVQ8pUUaZ1vKRSA==)
11. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6BgTnnCshB6PqoNtACn6VkRyOTBWGpa-0BUtnJ-cd_k9Rq6Htwqv0kWzROdFyOjhOILnhEpXIfFpmM79l39YwqdQFZzbcQ-Nn3wACPkN4QPZxtha0k4Fza9x-U1BrJn3LhO8or-CjGbwcPqO3wQmQ)
12. [ups-tlse.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhBErWyWmt3Oc-YREg7ZKpR7rldFRPg6BDhq7eAKi6FrH9hyHKRh3guSL3zxzOqk4Nh1CBQTxiIDaD8CeGEmLxECBkAj2e4w6IzrGtVDWzu7IIlrqpJx6AMQnhPhphBEvbEyLlycNnXCdUzAQTX1Hk1rQ=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiCOx6pERTzXijt4g_A9Drs3NLXY5-at2mMygPh0ijQL784Z5Xcn3eVyBhEgk16KPHNuKXS8iGznB0J2Ep_EZJHm47SjeLz1tYoP3-ryUpLSOhqKQGDerNZEQ4OHV-Hd32eL_A8031X91EJseYsp-gw190JKYA9-GT5TV-ndnbgvXwYLweEctsKHnJYOYhC3Q0GNfHwltNSLobHWdhPQ==)
14. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC66KhVUy85fGMJ1U3ve8NVfoOhdg6zvBBuJYaUAf2HPdchHXjRl2ulYEor1MCyV7aicIXHQDvI_Nnu1OPVAKVHB9FKsi8aL9ouoXdwmHoxjFEecAqVar-M9PKVp4qJwbXGHPUA1BIXh-EgbwpLX6_RcfJ6iijRg==)
15. [embeddedrelated.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYUNR4UBThGVjxeIS2TgbskX5oHVUGT41txzC1dB0wYa2Y2YxZueAy_k0TgpGsKSam5-EXD5aytNybxCC9PwoHnjlX2g83haLHoSvcMY0qYaiw8Xx2C0bDa1NMR9rY9bdlXQbi5l9vzg44)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtCZpjx5vxl476UUanFewh5n_MpevE5dMugDZiMyukVmVhTP1J6sSKFFkuIEgbaZsUxLoxWZQC-RBQ13B5mIph6nIXJlXcbVdIo8Buoo6AiByr8iaba0Pq42ulrJjhbE_HW4JMBOGQQbY8OoT3Rusdu4bPnScrP7PWjYCOhQcN7HF6kmqKkhj2HTUTlsypO3AD18o=)
17. [sspddp.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERlsQPJBZlyZ4hmujx_rRac2VapTTQoK92KtSVb9B1YZKIqbD_-Jj7g0bRbEYdMAYurhHeDF89Y_lkNlV5iOGprMX7YPqPw-6FrIhidjHxmyK5dvqldWe_dztyJJI6Q5j1ihCqYk0=)
18. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPP1t89O4EXsAX77ZUkxi2QxbPsujQG0ZUEhsEe7Wix8j4Aviy4ZzUx86YWOlzdEcdkh3AZe90HemqbJSQoS7P6SVx8pZRaACNFJEXvz--4rzwYYprfePl7rZhISDwrcwFXhmlBCzxiCprQWOi)
19. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHA_1F1GLPIxIvhmpxoASBIUlzEV6SqBiGD1_RCDqJBspWLUAl9ee1vMN9uKrBubFO2JDzLTnNdzLzx8H1nYiXTbdEEu82a_yUHLJIqxOavv0kAMgM6ITT3B2WMu3Hz1zyYMhWPA==)
20. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZxNA0AS_gM-8bMDV8SyFPkm7PrBNToSLjTZh2pxqO6864zj1TGHSTzNa4wdrCV1Tb1v7yXiNOgavpN4xP1weKJ8TeAsDckvneFNVu-rKr2-N0vmCkJvNl6uYNpdZ1skgA0fbjxig3nkao_kAK7w==)
21. [uow.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSfIRL25sy-nAfF4ICniweyEzBnOrL4pbZA1i6OtSDAFl8OpUDxVvnl1NKHYAcj_hkoLmCdTCzMbsRIOEi-SMB3GA5EyOkyXKEh7oqaid_gLwaxWLTCrH_WimZnnYV1dUcqq8ANRzJ6Q==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-XF3C_FD3TPGW9HrKw4Z5Jqp3Q1A0uTrdIX9Vgr3O3k5YAQ04Wb6vwS1YWh1oYGQyZGRfSYUBy3ASUR_-ctTCsAc6fTtQMAXZpu5mrGrxsvYCGqq6PTSnhQ==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW-Ngvaey5HtErAEJyKenbFwNXKbKltlE-RnxtuCZHovENHKLaa3HtfcIOl0f5_wyTOcfXoAMckeOLDt1f523xqBJRlJe7iuCPZnvzRDaglpSOxulEtYFW3sIyg3sABhAaQ1zdGBECblXBh7e2lOrUWG9iQ68CWqBOaGOD6Zra-xGp-HqaoZ8uqhLW8eBygd0VachigbWyfHdXlx28KCHwuHcUZKFGqRX_s3AqUkcFmH5KSA==)
24. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPh05SZe4QkqA8g_Ss3C3c_hmzl075yjMbY6v0q5zOWcoE426uJM8kRZ_hjoRqQofQ9qU-jdRwDlTDWepggYzoLuCSfsBCQy9fVb97uMJgaW6ExVyFteJyId8vaVp5i0hcAY5RpMqTqd-3w1MhCrnMaPLr9P93bzSlLKVkrWR9lD2rmvs=)
25. [loria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5h_Kp1ux8qtdHNQwtlUutjR5ib_K-lp6vfwV2cG-ELuW-Q4HvFKJm3TrgYXBuuPZmpAIfZqmiQznf83NOOhPxzptN_2mpVwFThCW8XHmv2jNta3E3UOXBTtjQ_6VJtZ0lh3BYr-WWV9HYOOnF)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsx8t32D-rkMoB8e4LGuz0BFxC9Bax4bIW-emLx7emENL-5NzsOwVC7j-jX7l1Z01R4RZNh8HP-7YGo0DWdgBnHmsP9SsNrqzu-ZlQ1y-_gJn9DmQlSiz5HUE=)
27. [qucosa.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd7rIXAlK7fm9BSFIf2-tqaJrQwCEADTaDXO4lXucJ-Ccxsh0A9mrqKnvQnd_m4441sw8p16ZbbffQsx4Cek7SIx6sUNWapewj9GKp-7DtrbnjDps4ZxsXyUCs6zsDx0e2L6hJJ8syUJiSZ3nbfE3C)
28. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs3NupWbFFUwS3cwuf9XXTQyCc9lxD6CD4iQ54jOQLKuJ7FySOF4OqdDgVSKQdhJ7KzHT8qAYQxTUOz9ThvPH5BN64DY5O_Lp7HwvQ0c99nWeeW5-kVn9-LiU6BUvqBl22WY6euqiFfEQmv2M5dt_oaSk=)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHpSW3AP33R7EcsQu5qmVg93InlJJ1rqaKpojRTgDes8_ZPmIUgGvOnyO6J9gvh2Ykj79MBRTF3qPVCNxeA905n2tsGZN-5h_uEOFxql5lk466XDvsMd7_sUIkYN1Z0DC1ufTRnhqpnGxmvxUtYJBxCkwvXsCEI33eiQDb2pJGmLnf6L3RJNStHawaP1QYIHRQyfZmqBHyBDfyY6syUNxOVSObS1FTjm1X_GAL1cuiJf4UtmeVuGFqEM2kw_A=)
30. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT1bWItEUdvmktgLvWNFTgR3v4puDJwo4vAHLr3Ym2dW2B2h2tUq2oEhcIB37iaLsl_XN7T4JYB30-UU4Iq2jt8BIOxzy3MJGxiZnHQvD6TEjGaHWPDrUQscg=)

