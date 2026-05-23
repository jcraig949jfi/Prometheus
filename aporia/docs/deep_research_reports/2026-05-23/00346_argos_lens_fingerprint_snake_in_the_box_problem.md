# Argos lens fingerprint: Snake-in-the-box problem

**Pythia queue id:** 346
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFUElRYXB1bEdjaW9qTWNQeWRpMHVRZxIXRVBJUWFwdWxHY2lvak1jUHlkaTB1UWc
**Elapsed:** 427s
**Completed at:** 2026-05-23T00:24:28.722190+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem MATH-0357 (Snake-in-the-Box)

**Key Points:**
*   The Snake-in-the-Box (SITB) problem, fundamentally a quest to find the longest induced path in an \(n\)-dimensional hypercube, remains an unsolved NP-hard challenge in discrete mathematics.
*   Research suggests that applying a **Dynamical Systems** lens allows for the mapping of discrete topological nodes onto continuous relaxation spaces, yielding efficient heuristic approximations but generally struggling to prove absolute combinatorial bounds.
*   The **Information Theory** perspective, which originally motivated the problem, leans heavily toward evaluating asymptotic code rates and error-detection bounds under various noise metrics rather than strictly maximizing path length for a specific dimension.
*   Emerging quantum and statistical mechanics approaches under the **Renormalization Group** lens provide a novel framework, mapping the problem to Ising spin-glass Hamiltonians and fitness distribution renormalizations, though physical hardware limitations currently restrict exact solutions to low dimensions.

**Introduction**
The Snake-in-the-Box problem (`MATH-0357`) was first articulated in the late 1950s and asks a deceptively simple question: what is the maximum length of a chord-free path (a "snake") or cycle (a "coil") along the edges of an \(n\)-dimensional hypercube? While seemingly a straightforward exercise in graph theory, it serves as a critical model for error-correcting codes, analog-to-digital signal quantization, and network topology design. Due to a severe combinatorial explosion as dimensions increase, exact solutions are only known up to \(n=8\). 

**Methodological Approach**
To investigate this open problem through multi-perspective analysis, we project three distinct analytical lenses onto the existing primary literature: Dynamical Systems, Information Theory, and the Renormalization Group. For each lens, we identify the two most rigorous or representative primary-literature attempts, extracting their projected measurements, ultimate verdicts, and the fundamental axes of disagreement with competing mathematical philosophies.

***

## Lens 1: `STANCE_DYNAMICAL_SYSTEMS@v1`

The Dynamical Systems lens attempts to transcend the discrete, combinatorial rigidities of the hypercube graph by embedding the problem into continuous time or continuous state spaces. By formulating the search for a maximal snake as the evolution of a system governed by differential equations or complex state transitions, this lens leverages the physics of attractors, stability, and chaotic dynamics to traverse the search space.

### Attempt 1: Continuous Hopfield Neural Networks and Chaotic Simulated Annealing

The first major application of this lens relies on the continuous approximation of the discrete graph topology using neural dynamics. Rather than discretely branching through valid hypercube vertices, the problem constraints (chord-free paths) are encoded into the continuous energy function of a Hopfield Neural Network or an Asymptotically Stable Dynamical Policy (ANDP) [cite: 1, 2].

**Measurements Projected**
Researchers have formulated the search for the longest snake by gradually reducing the time step in the Euler approximation of the differential equations that describe continuous Hopfield neural networks [cite: 2]. The primary measurement projected is the **asymptotic stability** and the **Lyapunov energy minimization** of the network state. The state variables of the neurons represent the probability of a specific vertex being included in the path at a specific sequence position, evolving continuously over time \(t\).
\[ \frac{du_i}{dt} = - \frac{u_i}{\tau} + \sum_{j} W_{ij} V_j + I_i \]
Here, \(W_{ij}\) encodes the hypercube adjacency and the strict "no-chord" penalties.

**Verdict Reached**
The application of chaotic simulated annealing within these differential equations eliminates the need to carefully tune discrete heuristic parameters and guarantees convergence to local energy minima [cite: 2]. Furthermore, combining generic dynamical system-based policies with Monte Carlo Search paradigms (like Nested Monte Carlo Search, or NMCS) has yielded highly competitive lower bounds for higher dimensions, sometimes outperforming pure genetic algorithms [cite: 1]. However, because the system fundamentally seeks local minima in a non-convex landscape, it cannot provide mathematically rigorous proof of a global maximum (the absolute longest snake).

**Axis of Disagreement**
The primary axis of disagreement between the Dynamical Systems lens and pure combinatorial/graph-theoretic approaches lies in **state space relaxation**. Combinatorialists argue that continuous relaxation inevitably explores "invalid" sub-states (fractional vertex inclusion) that have no physical meaning in hypercube topology. Dynamical systems theorists contend that allowing the system to temporarily traverse through mathematically invalid, high-energy states via chaotic tunneling is the only computationally feasible way to escape deep local optima in high-dimensional hypercubes [cite: 1, 2].

### Attempt 2: Dynamical Systems Modeling of Evolutionary Algorithms

The second attempt abstracts the search process itself into a dynamical system. Rather than modeling the snake, researchers model the evolutionary heuristics (Genetic Algorithms) used to hunt for snakes.

**Measurements Projected**
Using formalisms like Vose's dynamical systems model of the simple genetic algorithm, researchers map the transition equations between the density functions of consecutive candidate populations [cite: 3, 4]. The measurement projected is the **trajectory of the population density function** over discrete generational time, often approximated by finite Gaussian mixtures. The state space is not the hypercube itself, but the simplex representing all possible populations of snakes.

**Verdict Reached**
By treating the search heuristic as a positive dynamical system in discrete time, researchers observed that while the transition equations govern the probability distribution of finding longer snakes, these equations usually lack closed-form solutions [cite: 3]. Nonetheless, this formulation has successfully identified long snakes (e.g., length 97 or 98 in \(Q_8\)) by utilizing custom operators that respect the system's dynamics, proving that heuristic search traverses the space in a predictable, dynamically stable orbit toward near-optimal attractors [cite: 5, 6]. 

**Axis of Disagreement**
This lens clashes with the Information Theory lens regarding the nature of the solution limit. The dynamical model of heuristics evaluates the **probabilistic expectation** of convergence over time, whereas coding theorists require absolute deterministic bounds. The dynamical stance assumes the maximum snake length is simply the global attractor of a well-tuned Markov chain or differential equation [cite: 1, 2], an assertion that pure mathematics considers incomplete without constructive proof.

| Attempt | Primary Formulation | Measurement Projected | Key Limitation |
| :--- | :--- | :--- | :--- |
| **Hopfield / ANDP** | Continuous energy landscape via ODEs | Asymptotic stability; Lyapunov energy | Struggles to guarantee global optimality due to chaotic local minima. |
| **Vose's GA Model** | Population state transitions over time | Density function trajectories | Lacks exact closed-form analytical bounds for absolute maximum lengths. |

***

## Lens 2: `STANCE_INFORMATION_THEORY@v1`

The Snake-in-the-Box problem was originally conceived by W. H. Kautz in 1958 purely within the realm of information theory and coding [cite: 7]. Under this lens, a snake is a type of Gray code capable of detecting single-bit errors. Therefore, the problem is not viewed as path-finding, but as the maximization of channel capacity and error robustness under specific noise models.

### Attempt 1: Rank Modulation Codes for Flash Memory

A modern adaptation of the SITB problem involves its application to rank modulation schemes in non-volatile flash memory, a domain where cell charge levels represent information.

**Measurements Projected**
Yehezkeally and Schwartz (2011) recontextualized snake-in-the-box codes using permutation metrics rather than standard hypercube Hamming distances [cite: 8, 9]. The projected measurements are **Kendall's \(\tau\)-metric** (which corresponds to charge-constrained errors where adjacent cell charges swap) and the **\(\ell_\infty\)-metric** (limited magnitude errors). The performance metric is the asymptotic code rate:
\[ R = \lim_{n \to \infty} \frac{\log_2(M)}{n \log_2(n)} \]
where \(M\) is the size of the snake-in-the-box code within the symmetric group \(S_n\) (the permutations) [cite: 8, 10].

**Verdict Reached**
In this context, researchers constructed permutation-based snake-in-the-box codes with an asymptotic rate tending toward 1 [cite: 8, 9]. The verdict is that utilizing "push-to-the-top" transitions (analogous to moving along a modified graph structure) allows for highly efficient single-error detecting codes that avoid the asymmetric wear-out problems of traditional flash memory programming [cite: 9, 11]. 

**Axis of Disagreement**
The primary divergence here is the **shift in the underlying metric space**. Traditional graph theory evaluates SITB strictly under the \(L_1\) Hamming distance in a binary vector space (\(Z_2^n\)). Information theorists applied to rank modulation reject the utility of the traditional binary hypercube, arguing that permutation spaces under Kendall's \(\tau\)-metric provide a more physically accurate model for modern electronic wear [cite: 8, 9]. They prioritize maximizing the asymptotic communication rate over finding the longest absolute path in the standard \(Q_n\) topology.

### Attempt 2: Robust Quantizer Index Assignments

Another classical application within information theory applies SITB to signal compression and quantization.

**Measurements Projected**
Kim and Neuhoff (2000) investigated snake-in-the-box codes for assigning binary codewords to scalar quantizer cells [cite: 12, 13]. The measurement projected is the **mean squared distortion** of an analog signal transmitted over a noisy binary channel. Because adjacent code words in a snake have a Hamming distance of 1, and non-adjacent words have a distance of at least 2, small bit errors cause only local index shifts rather than catastrophic signal distortion [cite: 12, 14].

**Verdict Reached**
The research demonstrated that redundant index assignments using SITB codes offer a highly desirable distance-preserving property [cite: 12]. When a quantizer utilizes these codes, it possesses significantly superior robustness to channel errors compared to traditional natural binary or standard Gray coding assignments, particularly when the channel noise is high [cite: 12, 13].

**Axis of Disagreement**
This application disagrees with traditional algorithmic complexity lenses on the concept of **optimality criteria**. While computer scientists focus on solving the NP-hard problem of finding the longest possible snake to claim a mathematical breakthrough, information theorists in quantization focus on the tradeoff between code length (redundancy) and the resulting distortion tolerance. A shorter, suboptimal snake may actually be preferred if it perfectly maps to a specific signal resolution, showing that practical utility does not always require solving the absolute maximal length [cite: 12, 14].

| Attempt | Application Domain | Metric/Measurement | Objective |
| :--- | :--- | :--- | :--- |
| **Rank Modulation** | Flash Memory storage | Kendall \(\tau\)-metric; \(\ell_\infty\)-metric | Maximize asymptotic rate tending to 1. |
| **Quantizer Indexing** | Analog-to-Digital Signal Conversion | Mean Squared Signal Distortion | Minimize channel noise impact via distance preservation. |

***

## Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

The Renormalization Group (RG) lens, historically rooted in quantum field theory and statistical mechanics, deals with changes in a physical system as viewed at different scales. When applied to optimization problems like SITB, this lens reformulates the discrete geometry into multi-scale energy models (Ising models) or relies on macro-scale adjustments of phase spaces (fitness renormalization) to "integrate out" localized complexity.

### Attempt 1: Density Matrix Renormalization Group (DMRG) on QUBO Formulations

Recent breakthroughs (Fuidio, Canale, and Sotelo, 2024) have formally translated the SITB and CITB (Coil-in-the-Box) problems into Quadratic Unconstrained Binary Optimization (QUBO) models [cite: 15, 16]. This is the mathematical prerequisite for embedding the problem into quantum processing units or simulating it via Matrix Product States (MPS).

**Measurements Projected**
The projected measurement is the **ground-state energy of an Ising spin-glass Hamiltonian**. The QUBO formulation maps vertices of the hypercube and their sequence positions to binary spin variables \(x_{u,i}\), where \(x_{u,i} = 1\) if node \(u\) is at position \(i\) in the snake. The energy function includes terms enforcing path continuity (\(H_P\)) and chord-free constraints (\(H_C\)):
\[ E(x) = -\sum_{u} \alpha p_u + \beta H_P + \gamma H_C \]
The MPS is updated using the Density Matrix Renormalization Group (DMRG) method, which iteratively traces out non-relevant degrees of freedom (spins) and minimizes the system's energy via multiple sweeps across the spin chain [cite: 15, 16, 17]. 

**Verdict Reached**
By applying the DMRG methodology and quantum annealing on D-Wave hardware, the researchers established rigorous correctness for the QUBO formulations [cite: 15, 16]. The quantum and hybrid classical-quantum solvers were able to successfully find the theoretically optimal paths (global minimum energy states) for dimensions up to \(n=5\) [cite: 15, 16]. However, physical qubit limitations and embedding failures currently restrict the mapping of the highly dense QUBO graph to real quantum architectures for \(n > 5\) [cite: 18].

**Axis of Disagreement**
The RG and quantum mechanics lens disagrees fundamentally with classical computing lenses over **determinism and state representation**. While classical tree-search algorithms evaluate one defined graph state at a time, the DMRG/QUBO approach represents the path search as a coherent superposition of all possible states (represented compactly via tensors), iteratively shrinking the Hilbert space. The primary friction is hardware scalability: classical methods currently hold the record for \(n=8\), while the "structurally superior" quantum RG methods are hardware-constrained to \(n=5\), raising debates over practical vs. theoretical algorithmic supremacy [cite: 15, 16, 18].

### Attempt 2: Histogram-Assisted Renormalization of Fitness Distributions

In stochastic combinatorial optimization (such as hunting for snakes with genetic algorithms), the search space is often riddled with deceptive local optima. Researchers have applied a technique directly analogous to RG flow: renormalizing the fitness landscape at macroscopic scales.

**Measurements Projected**
The core measurement involves taking the raw fitness distribution of candidate snakes and applying a **histogram-assisted adjustment** to create a renormalized probability density function [cite: 4]. By dynamically grouping population fitness scores into bins and mapping them to a transformed scale, the algorithm effectively "integrates out" micro-fluctuations in the energy landscape, mirroring the block-spin decimation in classical Renormalization Group theory. 

```python
# Conceptual representation of fitness renormalization
def renormalize_fitness(population_fitnesses, num_bins):
    histogram = build_histogram(population_fitnesses, num_bins)
    cumulative_density = compute_cdf(histogram)
    renormalized_fitness = [cumulative_density[f] for f in population_fitnesses]
    return renormalized_fitness
```

**Verdict Reached**
Empirical and numerical tests demonstrated that the algorithm's performance is insensitive to the exact number of histogram bins (scaling invariance), provided the bins are an order of magnitude smaller than the population size [cite: 4]. This renormalization of the fitness distribution proved highly advantageous for multi-modal function optimization, substantially enhancing the probability of escaping local minima and contributing to the discovery of new record-length snakes (e.g., 98 edges) by smoothing the hypercube's complex landscape [cite: 5, 19].

**Axis of Disagreement**
This approach disagrees with purely exact enumerative methods (like exhaustive depth-first search) regarding the **preservation of microscopic information**. Exact methods require the strict preservation of every discrete path constraint at all times. The renormalization approach argues that microscopic details (exact relative lengths of mediocre candidate paths) are noise that actively hinders the discovery of the macroscopic optimum [cite: 4, 5]; thus, discarding relative micro-state differences via binning is mathematically optimal for global convergence.

| Attempt | Mechanism | Measurement Projected | State of Application |
| :--- | :--- | :--- | :--- |
| **DMRG on QUBO** | Matrix Product States; Spin-glass energy | Ground state of Hamiltonian spectrum | Proven optimal for \(n \le 5\); limited by QPU hardware density. |
| **Fitness Renormalization** | Histogram-assisted density scaling | Macroscopic fitness transformations | Highly successful in heuristic searches, yielding historical upper bounds. |

***

### Conclusion

The Snake-in-the-Box problem (`MATH-0357`) serves as a unique topological bridge between disparate fields. The `STANCE_DYNAMICAL_SYSTEMS` lens projects the discrete graph into a continuous relaxation manifold, utilizing differential flow to bypass combinatorial roadblocks. The `STANCE_INFORMATION_THEORY` lens, staying true to the problem's origins, maps the hypercube onto channel models and alternate permutation metrics to secure optimal communication rates. Finally, the `STANCE_RENORMALIZATION_GROUP` lens re-encodes the constraints into spin-glass energy Hamiltonians and coarse-grained fitness landscapes, utilizing the physics of superposition and scale-invariance to locate global optima. Each lens ultimately sacrifices one aspect of the problem—discrete exactness, topological tradition, or computational scalability, respectively—to gain traction on this notoriously intractable puzzle.

**Sources:**
1. [intelligent-optimization.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxNHvUZco9_1VhXUPMVbOOolJSOGq7KrCVZOsZskNSYu3ievVBt0r85KIa_QQEPyB87ZAjVnmR3oIoSrN_kTEyjaUkQBwF2DjG56eaJT5qFJgitAx-5aUYoqIsqH0iEhqlgg7tzQ7Xk7YL0MIMvPYmQ8BLaqqQZJzrGZ14m1x5Ezu_lGk=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHb2SpWRRWHtPOehffOGNGBJSyJEXjpMhO2taz7z2ohri95g0O9yC23LwmVKeZYOKEBy58Z6C9siSnGcFIVkJp0EtIHacFb944Uk5_hm7gpFPvlgmYALqa5-eVPvWpJUj2D2WWDUo0sq1lx8G2rAlmz8zvYuRi28863FdGmqgaKQHe4pxOSu1naBHRBjEkPPDAeFlGrpKr3f3uoGrrtFbn0yqEuhlkuavZEA==)
3. [sigevo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFUqoHyJoDVOYqwda0EcEPmblsbY4EZbMg53gYBDLZz4Bjbr5adNX2hVvgTVCsMqsSZtBKwurwdSv5DScZlVbV9JnYWWI72ibF0nzWICSeoo5pMO154ruGmiku7q8nU2dGP2FUihzk8dcIqJjWLzuzrCU=)
4. [sigevo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ22xxbMvNR4dqHZ9gHftcy2GKP8eNpN8FV1UgGvzTLnaDdFPkK5VaxHEB-eJPx5VS8xih-bpyxmftIP-2P5-kYg0bCcLMpDmR4p9jchhRufJO8hnpdBR4v0DbDRQ_ukShjrWbT9h-mkEIFuC8ZsT_f67JJ4YENA==)
5. [sigevo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG33QX0XGGzA1mX0qPpXkrRlPEbUBMgmplHY7d1-mJ0TPy8tmsAHm8xGgrRLD9TktQuXTDSGmXJYeSvw1xMnzM_zFU1SKGdAiQ60piwulxq0V23UsNr8Zfc2ohFOdF7GCpxmpvbTnc2g1RuFXaSdeuqfTO-ywhw4g==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2ntxGfxxY-r-f4BQLijS_B0sfl-e02j2MTDH5rm23VOyUbHLBISSjJjfTOcO34lRG-rPpaMPnUtuUdBJzmUL5wD217BxpsfnnAJNyLDg9CGpk5JRKdBMMhV4bMn5yulQR58IRrYZuSVb3Da9tabndtcGAXWEHSCru_l9nhBPN5fdcVGTpqkFpmPcT5mkkTwx9gITF7WIKpE-qfRFE5bC-hv85f2ELpVwtQlU1pgx9UwTbKEt3VjMzG2bDIWIdq2sANVbx40PZ_Bk9JMMoWiyHr5TG6A==)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF16P5Q6HVwSqrtdUbHP4vNIGh1xSnCJNVEKYTc2Jfg947se1Da3_-MLSMSnL6UDwRCyi5ECQrkH1nQpWVr1hiwQ81aiORKUq4r7kxXHZmilFX8tI4a6TRxlbOWxWHkMyWBg1t8)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5fmTcyLqVlOpKpN8ZgtquyZ7kvH_3NXdmGK1Cf1agUcOhIefoSitbTIOXldjqtX1aCV51P0YE1EVPd1rVTYyuckxMYA9diwjPJ3soUsXqbyBVRd7o)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrQrHD7hiNa0H54rr6lSXFi9TFPriubW1M_D2fFScIYrHQubwnjVI9pW2BQUAqQ7Ps2prSiS3wXwMvagabJHg1fcADGGOnVQtWTDDnOdLv4l8o_U2D)
10. [mcmaster.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_OV2Wpk0uZ9N9bF3CNZp3n1bHmZoR2jOYaU8Mo26iY_fr6PGWai9kUJzfK9r_u_hOcZrjqrsM1GDDoJm4QxJTrMYGl6FDQh7MCDyCNMY706nRKsoyM2iYdBU2HwSYZjpzcDyIYPsxtMIVkQItnHEIB1BPSvY=)
11. [microsoft.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGrcVLGiH5RqByFSXnxfzzPIaT5LxlMvj86YWHH4AJVq22SYY_r0IIFPh-POFHQZtQoh9pZcWDFOaTmWMGoWNlP_EIAzOUJTofTjrKFcmvTenv8tPKdbLj48YNMBV-8vE_dDHbXKsYFpfVu1PUAFnZpdFHlcYes1d9IhyNAalfBK9KGBniQQUBeg0PnmnOBueZCLO0)
12. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-Yqnqd0EcWl1T4zYveuTES2YcoSKlzSxMPg4YN397ugShb8GvEFDU1SMf0XGL0ULkYd0aXOi1ENIVlahRTXO5nCE4YGpbpBmpnPvzUqzEzRH1d5QoFgTGz11SupWNXk9Hpg==)
13. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGahSaO-79I8vwAfIq6AEziPhpp-XEnDEOZs4zicxDASz2XEnFqBKlOR9no6XWB4Dq2dtVmjwA0K9DiF0Gom0BF8_K68oJbfvmNdNPv0aYgiAYi8WHytG5vk_0KZj8OOaCtIJCh)
14. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESWHEmY6eiJItzY8B5sRKnzC8dFiFVY5UXpSmMa2x_4eVbk1YbP5imfEkBUBdifqagDwgRZ-FeNrmblJFI4dWx3z0CBYvPUaFoBoUw14U1ttPiB_elNVkh-5iWvvgrq2RyElsrKtSuaSgsHL2MJAqCxwQ4RO9mrKlbS-7I3Q1sKEzv4W4T5Ug1)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgoy_oSuB8hwB12vZc9Cx2BbKQ4dtEXRzOs7BojhNh-JGZgvPtGNz41MhuxC7PJvQB0H-ag0Pz1vcn-KZ0GcigvuEehFyTCGdMgL9-P8ec5Fh2mLTaED1aCQ==)
16. [udelar.edu.uy](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXFAtaU8wVL2pUYZVTfPCQWlX900P5uPh88mU8KSpKs1CwHBdfGSSH25lnk6NPkpbW9RkdjSPKCFZbOZd7F14UwwF46MQlQFQDM6VSfLk9l3zw2w9CUTaZ7XlpU1Vvezte04-YrfDuKzmuP5umtKXVYjwAq20hbtCh58oQt2txCY86GvpiWA==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjx0Vfpb_zTwnrK5mCr5lwZTppRlXL4L7peQR1zPLN13atHVez-6zVo0zMnKWKH9kE7sGp73JyemNn104SKM5cZCbxRcW89CzFgvEuDCwaGrmVYKYdRQF9z5iYnaA3a3zspxPs7DmgxDBVBsBn3SI4Ik9p3cG0r03YclI_d9cPweTbzwaQAFWlK95V2g==)
18. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOgV2s16La-fLfQSrDKyEIub0Z0xK-VCiK_fPFws0A_xOe997CpqM9O4O3up1o36qxyitdwOVB_O6LtqmPq6KO8nIZpnCB_QToQ--fuZ9DfpGXKEHeSfCioc-_f_mnRL89SNOnZ3Jbux5lPFf-48XvgHV0rzG3Q0EbW8s=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjAvEIy9-ZIc9jTepoj4lV6Y2jOtSU0XfjbH8gnXp6EcQBEz_IiwY95BGE2DBaxTMMxhpROxlWwxyZSeS8QMZiw0Fzp7T3TLgQVm-acGYgfVqLxbGhzvKedOoWMuX9mTIXkjCDdPjVxUmTYdu6JxeO-5RN0C-15AXQw4AfjbtDnsFycxsaDGchNJFqK5jC6s_zlZNM2GD71sOd9ug-2pO4K6042HSXge_QO3-vSvpNz8Gdi3T4Us3TBGZvnzMi0Az9RMWeIp8pX4oehw==)

