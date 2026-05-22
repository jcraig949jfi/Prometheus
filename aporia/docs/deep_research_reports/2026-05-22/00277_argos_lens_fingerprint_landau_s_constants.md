# Argos lens fingerprint: Landau's constants

**Pythia queue id:** 277
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctcU1QYXNLMkc0UGNfdU1QMHFxRWlBcxIXLXFNUGFzSzJHNFBjX3VNUDBxcUVpQXM
**Elapsed:** 559s
**Completed at:** 2026-05-22T00:41:15.014097+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem MATH-0206: Landau's Constants

**Key Points:**
*   **Problem Context:** Open problem `MATH-0206` refers to the exact determination of Landau's constant ($L$), an enduring mystery in geometric function theory describing the exact lower bound for the size of the largest schlicht (univalent) disk in the image of a normalized holomorphic function [cite: 1, 2]. 
*   **Current Bounds:** Despite nearly a century of effort, the precise mathematical value of $L$ remains unproven, with analytical bounds firmly establishing that $0.5 < L \le 0.54326$ [cite: 2, 3].
*   **Multi-Perspective Approach:** Evaluating the problem through modern multi-perspective methodologies—specifically dynamical systems, algorithmic information theory, and renormalization group theory—reveals highly divergent strategies. 
*   **Dynamical Systems Verdict:** In complex dynamics, $L$ is leveraged as a fundamental geometric boundary condition to classify the internal uniform dynamics of multiply connected wandering domains [cite: 2, 4]. Concurrently, spectral analysis connects the conjectural exact value to the cubic arithmetic-geometric mean [cite: 5].
*   **Information Theory Verdict:** Computability theory proves that Landau's (and Bloch's) constants are Turing-computable real numbers [cite: 6, 7]. However, practical algorithmic complexity remains an enormous hurdle, severely limiting arbitrary precision outputs [cite: 8].
*   **Renormalization Group Verdict:** The renormalization lens approaches Landau's principle through rescaling methods (e.g., Zalcman's Lemma) to extract normal families from diverging sequences [cite: 9]. Analogously, in weakly nonlinear physics, "Landau constants" determine bifurcation stability via structural renormalization, offering a phenomenological parallel to the geometric bounds [cite: 10, 11].
*   **Axes of Disagreement:** The core dispute among these lenses lies in the epistemological nature of the constant: dynamical systems treat $L$ as an active geometric constraint for iterative mapping; information theory treats it as an isolated, algorithmically targetable bit-stream; and renormalization treats it as a scaling threshold for structural phase transitions.

The exact calculation of Landau's constant remains an open and highly sensitive issue across theoretical mathematics and theoretical computer science. Research suggests that while algorithmic approaches prove its computability, deep geometric and lattice-theoretic methods (such as those tied to Ramanujan's theta functions) currently offer the most promising avenues for identifying its exact closed-form value. The evidence leans toward an eventual convergence between spectral lattice theories and exact real arithmetic.

***

## 1. Introduction to Open Problem MATH-0206

The open mathematical problem designated `MATH-0206` centers on the exact determination of **Landau's constant**, often denoted as $L$, and its closely related counterpart, **Bloch's constant** ($B$). Originating in the fertile mathematical period of the late 1920s, the problem was formally established following the foundational work of André Bloch (1925) and Edmund Landau (1929) [cite: 12]. 

In geometric function theory, Landau's theorem states: Let $f$ be a holomorphic function mapping the open unit disk $\mathbb{D}$ into the complex plane $\mathbb{C}$, normalized such that $f'(0) = 1$. Then there exists an absolute constant $L > 0$ such that the image $f(\mathbb{D})$ contains a schlicht (univalent and non-overlapping) open disk of radius at least $L$ [cite: 1, 12]. Landau's constant is defined as the supremum of all such constants valid for all functions in this normalized class [cite: 9]. 

To date, the exact value of Landau's constant is not known [cite: 9]. While early 20th-century mathematicians quickly established lower and upper bounds, modern analytical refinements have constrained the value to the narrow interval $0.5 < L \le 0.54326$ [cite: 3]. The analogous Bloch constant $B$ (where the function itself is not necessarily univalent, but the target disk must be the biholomorphic image of a subdomain) is constrained within $0.4332 \le B \le 0.4719$ [cite: 3].

The search for the exact value, often referred to as Landau's "Weltkonstante" (universal constant), has stubbornly resisted traditional analytical techniques [cite: 13]. The schema reference `D:\Prometheus\harmonia\memory\catalogs\README.md` and the multi-perspective methodology outlined in `D:\Prometheus\harmonia\memory\methodology_multi_perspective_attack.md` mandate a departure from classical geometric function theory. Instead, this report applies three distinct analytical lenses to the problem: `STANCE_DYNAMICAL_SYSTEMS@v1`, `STANCE_INFORMATION_THEORY@v1`, and `STANCE_RENORMALIZATION_GROUP@v1`. 

For each lens, we identify the two strongest primary-literature attempts or structural analogues. We dissect the specific measurement projected by the lens, the final verdict reached regarding the nature or utility of Landau's constant, and the fundamental axis of disagreement distinguishing the lens from competing frameworks.

***

## 2. Lens 1: STANCE_DYNAMICAL_SYSTEMS@v1

The `STANCE_DYNAMICAL_SYSTEMS@v1` lens analyzes mathematical phenomena through the iterative evolution of spaces over time. In complex analysis, this translates to the study of complex dynamics—specifically, the discrete iteration of holomorphic or meromorphic functions. The phase space is typically divided into the Fatou set (the region of stable, regular dynamics) and the Julia set (the region of chaotic dynamics) [cite: 14, 15]. Within the Fatou set, components that are not eventually periodic are termed **wandering domains** [cite: 2]. 

In this lens, Landau's constant ceases to be merely a static target for numerical calculation. Instead, it becomes an active geometric constraint—a universal minimum scaling factor that bounds the expansion of the hyperbolic metric during iterative mapping [cite: 2]. 

### 2.1. Attempt 1: Uniform Internal Dynamics of Wandering Domains (Ferreira, 2022-2023)

The most rigorous modern application of Landau's constant within complex dynamical systems is found in the work of Gustavo R. Ferreira, specifically in his treatises on the internal dynamics of multiply connected wandering domains of meromorphic functions [cite: 2, 4]. 

**Summary of the Attempt:**
Ferreira investigates whether wandering domains, particularly those that are infinitely connected, exhibit uniform internal dynamics. That is, if a specific dynamic behavior (such as orbits converging or diverging in the hyperbolic metric) is observed relative to a base point in a small open subset, does it apply universally across the entire domain? [cite: 2]. Ferreira uses Landau's theorem as the core mechanism to translate infinitesimal derivative bounds into macroscopic hyperbolic disk sizes.

**(a) The Measurement Projected:**
The primary measurement is the **hyperbolic size of the image of a bounded domain** under a sequence of iterations. Ferreira lifts the meromorphic function $f$ to the universal covering space (the unit disk $\mathbb{D}$) via uniformizing maps [cite: 2]. To bound the expansion of orbits, he applies Landau's theorem. Given a normalized lift $F$ satisfying $F(0)=0$ and an initial disk $B_{\mathbb{D}}(0, r)$, Ferreira projects that the Euclidean radius of the largest schlicht disk in the image $F(B_{\mathbb{D}}(0, r))$ is strictly bounded from below by $L r^* |F'(0)|$, where $r^* = \tanh(r/2)$ and $L \in (0.5, 0.544)$ is Landau's constant [cite: 2]. By translating this Euclidean measurement back into the hyperbolic metric of the wandering domain, he projects the minimum guaranteed expansion of the Fatou component per iteration [cite: 2].

**(b) The Verdict Reached:**
The application of Landau's constant successfully bridges the gap between local derivative analysis and global topological behavior. Ferreira concludes that uniform dynamics inside any open subset of a wandering domain strictly generalizes to the whole wandering domain, effectively proving that multiply connected wandering domains of meromorphic functions possess highly structured, uniform internal behaviors [cite: 2, 16]. As a direct byproduct of projecting the dynamics via Landau's bound, Ferreira constructs the first known example of a meromorphic function with a semi-contracting, infinitely connected wandering domain [cite: 2, 16].

**(c) The Axis of Disagreement:**
This dynamical systems approach fundamentally diverges from algorithmic and numerical methods. Under the `STANCE_DYNAMICAL_SYSTEMS@v1` lens, the exact decimal value of $L$ is largely irrelevant; the mere *existence* of the strict lower bound $L > 0.5$ is sufficient to force the rigidity of the dynamical system [cite: 2]. While an information theorist seeks to compute $L$ as an output, the dynamicist uses $L$ as a structural input to rule out chaotic structural decay within the Fatou set.

### 2.2. Attempt 2: Heat Kernels, Theta Functions, and the Arithmetic-Geometric Mean (Faulhuber, 2021-2022)

The second strongest application within the dynamical and physical systems lens originates from spectral analysis and the dynamics of heat propagation on topological tori, pioneered by M. Faulhuber and colleagues [cite: 5, 12].

**Summary of the Attempt:**
Faulhuber investigates the extremal behavior of the heat kernel (the fundamental solution to the heat equation, a continuous-time dynamical system) on rectangular and hexagonal tori [cite: 13]. The heat kernel's spatial and temporal evolution is governed by lattice theta functions. Faulhuber discovers a profound connection between the minimum problem for the heat kernel on tori of fixed surface area and Landau's geometric "Weltkonstante" [cite: 13]. 

**(a) The Measurement Projected:**
The lens measures the **spectral bounds of Gaussian Gabor systems** and the minimization of lattice energy models over continuous time [cite: 5, 17]. By formulating the heat distribution as a convolution kernel of a dynamical process, Faulhuber measures the extremization of the Jacobi theta functions subject to the geometric constraints of a discrete lattice (which mathematically mirrors the universal cover of a punctured complex torus) [cite: 12, 13].

**(b) The Verdict Reached:**
Faulhuber's work yields a striking, potentially field-altering verdict: the conjectured exact analytical value of Landau's constant is intrinsically linked to the extremal configurations of heat propagation on a hexagonal lattice. Specifically, Faulhuber proves that the conjectural value of Landau's constant is obtained exactly as the **cubic arithmetic-geometric mean of $3\sqrt{2}$ and 1** [cite: 5]. Furthermore, this spectral connection allows the constant to be mapped to the properties of Ramanujan's hypergeometric functions, suggesting that Landau's geometric constant is actually a thermodynamic extremum of a dynamical heat process [cite: 13, 18].

**(c) The Axis of Disagreement:**
This perspective disagrees sharply with classical complex analysts who view Landau's constant purely as an artifact of the Cauchy-Riemann equations and polynomial mapping. Here, $L$ is recast as a thermodynamic baseline—a spectral bound defining the most efficient possible distribution of heat (or information density) across a symmetric lattice space. It argues that the true nature of `MATH-0206` is not topological, but spectral.

***

## 3. Lens 2: STANCE_INFORMATION_THEORY@v1

The `STANCE_INFORMATION_THEORY@v1` lens, overlapping heavily with theoretical computer science and computability theory, strips mathematical constants of their geometric meaning. Instead, it views a constant as an infinite string of information (a real number) and asks: is there a Turing machine capable of producing this string to arbitrary precision in finite time? [cite: 19]. 

Within algorithmic information theory, mathematical constants range from easily computable (like $\pi$ or $e$) to fundamentally uncomputable (such as Chaitin's constant $\Omega$, which represents the probability that a randomly chosen Turing machine will halt) [cite: 19, 20]. The exact computational status of Landau's and Bloch's constants remained an open question until the late 2000s, because the supremum definition of the constants involves quantifying over an uncountably infinite functional space (the set of all normalized holomorphic functions on the unit disk) [cite: 6, 7].

### 3.1. Attempt 1: The Computability of Bloch's and Landau's Constants (Rettinger, 2008-2012)

The definitive breakthrough under the information-theoretic lens was achieved by Robert Rettinger, who published proofs establishing the rigorous computability of Bloch's constant (2008) and subsequently Landau's constant (2012) [cite: 7, 21].

**Summary of the Attempt:**
Rettinger set out to resolve whether the geometric suprema defining $B$ and $L$ could be effectively approximated by a digital algorithm. Since searching the entire infinite-dimensional space of holomorphic functions is impossible, Rettinger had to design a method to finite-ize the problem without losing the absolute analytical guarantees of the bounds [cite: 7].

**(a) The Measurement Projected:**
The measurement is the **algorithmic approximation error $\epsilon$**. Rettinger's algorithms project the generation of $\epsilon$-covering grids [cite: 7]. To compute Landau's constant $L$, the algorithm bounds the coefficients of the corresponding power series of a class of holomorphic functions $F_\lambda$. By utilizing the compactness of the infinite product space of these functions, the algorithm maps out an $\epsilon$-dense finite grid of functions [cite: 7]. It then evaluates the maximum schlicht disk for each function in this finite grid, yielding an upper and lower algorithmic bound for $L$ [cite: 7].

**(b) The Verdict Reached:**
The verdict is a definitive proof of computability. Rettinger establishes that Bloch's and Landau's constants are formally computable real numbers [cite: 7, 21]. The algorithms guarantee that for any rational error bound $\epsilon > 0$, the Turing machine will halt and output a rational number $L'$ such that $|L - L'| < \epsilon$ [cite: 7]. Rettinger successfully translates a continuous topological boundary problem into a discrete, finite algorithmic halting problem.

**(c) The Axis of Disagreement:**
The information theory lens completely disregards the physical or geometric utility of $L$. Where the dynamical systems lens views $L$ as a tool for restricting iterative orbits [cite: 2], Rettinger's work treats $L$ as the end product. Furthermore, this lens inherently disputes the "necessity" of finding a closed-form analytical expression (such as Faulhuber's arithmetic-geometric mean [cite: 5]). In the eyes of computability theory, possessing an algorithm that can arbitrarily approximate the constant is mathematically synonymous with "knowing" the constant.

### 3.2. Attempt 2: Complexity on the Reals and Reliable Computations (Dagstuhl Seminar 17481, 2017)

While Rettinger proved that Landau's constant *can* be computed, the practical reality of extracting its information content is entirely different. This harsh reality was a focal point of the 2017 Dagstuhl Seminar 17481, titled "Reliable Computation and Complexity on the Reals," organized by N. Müller, S. Rump, K. Weihrauch, and M. Ziegler [cite: 8, 22].

**Summary of the Attempt:**
The seminar brought together experts in reliable computing and Type-2 Theory of Effectivity (TTE) to assess the gap between theoretical computability and actual algorithmic complexity [cite: 8]. The researchers scrutinized transcendental numbers and constants like Bloch's and Landau's to benchmark the limits of exact real arithmetic [cite: 8].

**(a) The Measurement Projected:**
The primary metric projected here is **computational complexity (bit-cost) as a function of precision**. The lens measures the time and space complexity required asymptotically as $n \to \infty$ to approximate the output up to an absolute error of $2^{-n}$ [cite: 8]. The researchers map the continuous analogues of discrete complexity classes (P, NP, #P, PSPACE) onto the real numbers to determine how fast the computation of $L$ degrades as precision requirements scale [cite: 8, 22].

**(b) The Verdict Reached:**
The verdict is highly pessimistic regarding the immediate extraction of the exact digits of `MATH-0206`. The seminar concluded that while constants like $\pi$ can be computed to billions of digits within minutes using the Bailey-Borwein-Plouffe formula, Bloch's and Landau's constants suffer from exponential (or worse) bit-cost scaling [cite: 8]. The official report explicitly noted that "Bloch's constant, although proven computable, is still not known up to error $2^{-5}$" [cite: 8, 22]. The complexity required to parse the $\epsilon$-covering grids introduced by Rettinger explodes so rapidly that, practically speaking, the exact decimal expansion of $L$ remains effectively trapped behind a computational wall [cite: 7].

**(c) The Axis of Disagreement:**
This perspective highlights a severe rift between classical mathematical proofs and algorithm engineering. A classical mathematician might consider the bounds $0.5 < L \le 0.54326$ a satisfying enclosure [cite: 3]. Computable analysts agree it is theoretically solved [cite: 6]. However, the computational complexity lens asserts that unless the bit-cost can be reduced to polynomial time, the constant remains functionally unknown. This lens actively searches for new data types and continuous structure handling (such as the EU-funded NFFC project) to bypass these barriers [cite: 23].

***

## 4. Lens 3: STANCE_RENORMALIZATION_GROUP@v1

The `STANCE_RENORMALIZATION_GROUP@v1` (RG) lens evaluates systems across varying scales, observing how parameters change (flow) as the scale of observation is modified. In mathematical physics, the RG systematically integrates out high-frequency (short-scale) degrees of freedom to identify macroscopic universalities [cite: 10, 24]. 

When applied to the mathematics of open problem `MATH-0206`, the RG lens manifests in two distinct but philosophically aligned ways. First, in pure complex analysis, the RG methodology is expressed through **rescaling lemmas** (most notably Zalcman's Renormalization Lemma), which zoom in on the singularities of functional spaces to extract macroscopic geometric constants like Landau's radius [cite: 9]. Second, we examine the closest-analogue application: the **Stuart-Landau constant** in weakly nonlinear hydrodynamics, where an entirely different "Landau constant" operates as the renormalized saturation parameter for phase transitions in turbulent systems [cite: 10, 11].

### 4.1. Attempt 1: Zalcman's Renormalization Lemma and the Rescaling Method (Berteloot, 2025)

In pure mathematics, the closest analogue to a physical renormalization group flow is the study of **Normal Families**, a concept pioneered by Paul Montel. A family of holomorphic functions is "normal" if every sequence contains a subsequence that converges uniformly on compact subsets [cite: 1]. If a family is not normal, it exhibits a structural instability that can be "renormalized" via rescaling. 

**Summary of the Attempt:**
Lawrence Zalcman introduced a heuristic principle (now known as Zalcman's Lemma) which states that a family of functions is not normal if and only if one can extract a sequence of functions, rescale their domains (zooming in infinitely fast), and yield a non-constant entire function as a limit [cite: 1, 9]. F. Berteloot (2025) and others apply this renormalization technique to revisit Bloch's principle and Landau's theorem [cite: 9]. 

**(a) The Measurement Projected:**
The lens measures the **asymptotic scaling limits of divergent function sequences**. Given a non-normal sequence $f_n$, the method projects an affine rescaling $f_n(a_n + \rho_n z)$, where $\rho_n \to 0$ acts as the scaling parameter (the inverse of the RG momentum cutoff) [cite: 1]. The measurement focuses on the derivative at the origin of the surviving limit function. If the sequence is carefully calibrated, the renormalization process forces the target space to inflate, guaranteeing the existence of a schlicht disk whose radius corresponds directly to Landau's constant [cite: 9].

**(b) The Verdict Reached:**
The renormalization verdict establishes that Landau's constant is not merely a static geometric feature, but a **universal threshold for normality**. If the image of a function fails to contain a disk of Landau's radius, the function family undergoes a structural phase transition, losing local compactness [cite: 1, 9]. The use of Zalcman's renormalization lemma directly proves the complete Kobayashi hyperbolicity of certain complex manifolds (like the plane minus two points) without relying on heavy topological machinery [cite: 9]. 

**(c) The Axis of Disagreement:**
The RG lens fundamentally contradicts the static topological approach. It disagrees with the Information Theory lens by demonstrating that $L$ is a byproduct of scaling flows, not a discrete bit-string. Furthermore, unlike the Dynamical Systems lens which iterates a single function forward in time, the RG lens iterates the *function space itself* across spatial scales, looking for invariant entire functions at the infinite zoom limit [cite: 1]. 

### 4.2. Attempt 2: Closest-Analogue Application — The Stuart-Landau Equation in Hydrodynamic Instabilities (Vallis 1996, Ushakov 2005)

To fully capture the `STANCE_RENORMALIZATION_GROUP@v1` perspective on "Landau constants", one must address the profound structural analogue found in weakly nonlinear physics. In the study of fluid turbulence, the "Landau constant" ($l$ or $\Lambda$) determines the nonlinear saturation of an unstable wave [cite: 10, 25]. 

**Summary of the Attempt:**
When a laminar flow becomes unstable (e.g., crossing a critical Reynolds number or Rayleigh number), linear analysis dictates that the perturbation grows exponentially [cite: 10, 25]. However, real physical systems cannot grow infinitely; they undergo a Hopf bifurcation. The Stuart-Landau equation models this transition, using renormalization group arguments and amplitude equations to describe the slow-time macroscopic evolution of the system [cite: 10, 26]. 

**(a) The Measurement Projected:**
The projected measurement is the **nonlinear stabilization saturation frequency and amplitude** of the system near the threshold of instability [cite: 25, 27]. The amplitude $A$ of the perturbation evolves according to $dA/dt = \sigma A - l |A|^2 A$, where $\sigma$ is the linear growth rate and $l$ is the complex Landau constant [cite: 25, 28]. Researchers measure the real part of $l$ across varying fluid regimes (Poiseuille flow, Rayleigh-Bénard convection) to determine the topological nature of the bifurcation [cite: 26, 28].

**(b) The Verdict Reached:**
The RG analysis yields a binary structural verdict dependent on the sign of the Landau constant. If $Re(l) > 0$, the bifurcation is **supercritical**; the nonlinearities act to saturate the exponential growth, stabilizing the fluid into a steady limit cycle (weak turbulence) [cite: 10, 26]. If $Re(l) < 0$, the bifurcation is **subcritical**, meaning the system is unstable even to finite-amplitude perturbations, requiring higher-order (quintic) nonlinear terms for stabilization [cite: 10, 26]. Ushakov et al. further demonstrated that this renormalized Landau constant also universally dictates "coherence resonance" (CR), where intermediate noise optimally amplifies deterministic dynamics in a nonlinear system [cite: 11].

**(c) The Axis of Disagreement:**
While this is a physical analogue to the complex analytical $L$, the underlying philosophy of the RG lens remains identical: the "Landau constant" is the parameter that survives the coarse-graining of a highly complex system (whether it is an infinite-dimensional space of holomorphic maps, or a high-dimensional Navier-Stokes fluid flow) [cite: 1, 10]. The disagreement with other lenses is rooted in phenomenology. The physical RG lens accepts that "weak turbulence is the exception rather than the rule" and focuses on modeling the transition space [cite: 10]. It prioritizes parameterization and universality classes over exact digit calculation, directly opposing the precision-obsessed Information Theory lens [cite: 7, 10].

***

## 5. Cross-Lens Synthesis and Conclusion

The open problem `MATH-0206` serves as a masterclass in how a single mathematical parameter can act as a Rosetta Stone across highly disparate theoretical frameworks. 

1.  **The Information Theory framework** successfully isolated Landau's constant $L$ into a purely algorithmic domain. By proving it is a computable real number [cite: 6, 7], it mathematically guarantees that $L$ is not fundamentally unknowable. However, the exact complexity bounds discussed at Dagstuhl 17481 [cite: 8] prove that our current computational architectures are insufficient to extract this value using brute-force $\epsilon$-grids.
2.  **The Dynamical Systems framework** bypasses the need for arbitrary numerical precision by focusing on exactly what the constant *does*. In the hands of Ferreira [cite: 2], $L$ enforces uniformity in the chaotic environment of multiply connected wandering domains. Even more profoundly, Faulhuber's spectral analysis [cite: 5] provides a concrete mathematical hypothesis for the exact value of $L$ (the cubic arithmetic-geometric mean of $3\sqrt{2}$ and 1), connecting the complex geometry of the unit disk directly to the thermodynamics of hexagonal tori.
3.  **The Renormalization Group framework**, through Zalcman's Lemma and the structural analogue of hydrodynamic bifurcations, contextualizes the constant as a phase-transition boundary [cite: 9, 10]. Just as the physical Landau constant dictates whether a fluid stabilizes into a limit cycle or collapses into subcritical chaos [cite: 26], the complex analytical Landau constant acts as the strict threshold for geometric normality.

**Final Verdict on `MATH-0206`:**
The primary-literature fingerprint strongly suggests that the definitive resolution to the exact value of Landau's constant will not come from traditional geometric function theory, nor will it be generated by a brute-force Turing algorithm. The evidence leans toward a cross-pollination of **spectral lattice theory** and **computable analysis**. If the arithmetic-geometric mean hypothesis proposed by Faulhuber [cite: 5] can be rigorously linked to the infinite-dimensional topological compactness mapped by Rettinger's algorithms [cite: 7], open problem `MATH-0206` may finally be closed.

**Sources:**
1. [unife.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFygmG7W_P11xA8COA8xAFO3oX9xjTF5PRjEPQ4RBy73y3TZE-e1Zqus9SLFC1mCzH82HleN1onU8TW15QURHu0tjuyHOzrrh35vz0ZFagutbjjWV_5ViOlAqWAj0E8jeYffO4D5KdN)
2. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNYmi-Oio4c8gz7KPkQDzLDMi_nDLrLwSVcWPcn9wiqek-WJhq51_nPFWaShUuLu6MBWbZhQbgLP9o5WtzCvFB_k8MWWyV_23vZMY2g2RkMyzXZr24dVbqB0xxgk3TK1Oc1605tuESpt42RFqMWwn42BUFX3gghPKAOHpmWxwuL6PGiqR9rVtzQzi07vHS2L2WNQptO2FmxHa10wnvB-Zc-E8_L0scKzS3aYX0PqhEDUZ5ar20QobJ7ipfmWlCJCkcTqhRPZ4qbmJoBBqEjZom11h3IiqIdV7Eh3oreFtV2eexwPHT-FAINLv7ystnE0QdXsGDaL8hOofizhKJWA3FwYUzwTLDqIHznw2Nz_6oMikL)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdVEWB146SRoQ7HkeGVwQaF-YG3M27RIBCMWh49gWzKqWV8RqOwb8hmz4Qx00YmryPoNcCDKCnt-YmxfAKy4NDWAVClpmfpl-qcuM9TosLWN5X8r-NrKiDsYXABzivmGmu2bfwB3fsje98JqbLR_aWKQ==)
4. [open.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHztjouLDJYHt30QhzKkAvbnQfONor5dDh0b2dE70YrRiToY3eX7932WmTzoXUjckfDpLL5oJ8yeNS6WlneuCjOBVLM4pSO9zO0y9JPEneS3R8sJrbrrWdptharXNsKxrFoEA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRafVtTHxZK8Ulkj7GcGyNK0JiyuFhGR2SFkZdVcc8VQDc0_1dlcBqJs8vQbMdg_N686VgT52wkGh72B2zi_SgXj0Q1iVogXSl6kF_6j-8K1bs7rBz)
6. [jucs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZbT4ud8wz432-yft51AKloqIjEFNIfkYWEBpjJYKGqsv9RXccIJgF0Wyc7rUcMWIy-b3O6a4mb3NF69Qp3StyHR3JrBwXzR6aFbwYEbyix-aKnqV-5M8jKo51ki2HdPqgdBB2GbezbaU7F4xkV6UdGLg=)
7. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhGlmAjrjQ4xQNeqKlrUIc6cny5NhtTYrceP_EUxNolEI_64E3CxGWVc6M6mEbAlaA_v8MK2KxtcAzBtf_tD2I8WmenbesdwiI_ueOjKKr4crrJYpCz_FGCPE=)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU1-wIrWo2tVvdlHSx5l1xk-E8PAWacZl9Y6qDG5EgEhz2QJO7OrWoIXpdFat019VLq9fdXCTDlcznELlSE7_ESpjrWOgErAreqAqnW20PDxuD3Q==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9vywZgRfojkTaKL6VR9lIvHJVxalOuDQQnqU_AUl8_v_s5ngw4rFEv9_dJN604KkGmUMfVYU4PRtVXMQ-qvb4wM4URRe4dpSepevwC_-Qcg23tI7Y)
10. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRvCFyfVipix3UONIlj8GmDZavA7_0bQqhc2cu9nQtNwy20qD3NFRhqpC1rXRNk5813UC89pUhX9Qa6mzGOvnbBn1UhBDxW85YDlkkRoTwEMwZielMd-JP-B9VqgyKM74mtvyADgex0fiOi7Qni9r9-mMomzNF-v3WXy5EOg==)
11. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL38nBGAnEFtNRBGs1OeEFhPkTAuJCH9DieYoe7IJ18noqvCrzxmaTlWl3edLXWXc1V4_GsBVB4FRsbHwE_CtbMe3WNt9lo07wfv2JNT8iBuSeaA5Vyd7CztGIBJ2a775syN_1AI3ny3AwRLrGyPNR0SoESJrGsBBl9CEhPlF3aeuFupft4kd86A1RDk9JE6WKxlHrWwRcqPaKb1xF2A0iGtIXYxslcnb5Hk2aAydO1xhpesFd7yuh5kdA2e7WSoI8vC17yC_NJw==)
12. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAM41-BJS_2p9ZGwvtqHNQ9SbY68XPPGies-XGcyttpD02gtUaFDWRc8J6q73RscdHkHwgA5rXEYMrsaTak_J3lIoMcOPvGDosjv3dGwpRrsX-2on_sWTDoNNPI-VvATep3tDPG-VDJ95UhmEC2bqmbjqYF907vDf-cGaNiG-l8Gb9LMbje02bWn5-PMFLXg==)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELVY0lO-W7dU2TT5TUmItWytjnMIwGs2RkK3gnZqDYPePCurOUXXjj-DU-oZxY_-F0_i-KFhJB2VsUG9RXoz8Yk4FjIfHekCzdVYw9Y8z_8DVMrmu28-wDOVgupNTW5QOZjcPOOLk=)
14. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGea4pQHmdjNP3HrvrkK2_hJAyT41oyXWKqg_wygMn60dNHEt-001y_r_ZlhrniqvVi7qTISmVeeXei6me2mcGsikQkAcanIq87qjrIiXh9ERPgFVEtVJSBuN3Xjr2AvJUV7APwlk7osZkrxfmvAPA9TUm4uciVJcJ0q2K-tnikW0RN62V_ODX-xZCw3Ancxgm-N-5ay40=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqJQSoWKz1PQc0hRbznsmsXsx8WrMxw2j7JpqK8x84Y9vvMpLoOZ7KQ8ZnMNzEK7JYrwqRA5QMdQl1OkJshCEfzXRGUQLt29VuJaV14Imd3xmHkCFn5D8=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyrKXaJEHfHeGOLV256CMd2ewweIB2BDnwuBjKKLjOms4N6siOLvVQsBIL6m3_0DIGMdqpGBUMJti0LjH71VnSPtU0YvkF8dDfMlSqmTUi6EIsYfA-)
17. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkGhvzxG48vQfEhieZswbzg6ol-A-hhTfkpI-uOEuGJPkdkMf6tNLnIiiusNGIlR2Db4GcH3Aa3Za-wi6_5rF4A00YNTOYKa2qQcog8WArlQ9KeOBKf9k9tKmk6Ian_3NHMw==)
18. [oeis.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpl11HQdVSOqtPE0i9eSDS73W24iJwT2_Gjyl2xls-RPc9kQFZR5B-fuyePVcDSLKWtHAD-8dIM0FB9_IrmBSasHQOavNPIUjChkpd7A==)
19. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-rfa_q7_Xjc7fCk_tJzkK7XQfhSjOscbqJmZUAqBFz7QcX-KKdefmzppCylORTHrPz3n8qrimGx0dsLKQs7u2XETayXEfE0LVwq8_DKntnjksQXDqgucHrEX7EXL9lLuc04dB7ltIGj3FteKQ8gcfBN5RiA==)
20. [pageplace.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwKDS0L2yQEJww1Rs1m4i2YSdZbq_aR4bkEfI-3L3KcIuw8otbe7gDG4DIlR3wmKrTG1VOs5T1yQEx80FH7VRx5QEwaKJkLxZsw28Rme2nkiFfnnjSKa4iSJObw8No26AzYJSFPqA69HMl4UhN5h_s6Gz09Zjj0flbh3a063gRSpVuJCTCP-iF9Na2GBLGxAEY-Wmw-c2MVg==)
21. [jucs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGYntpeAo01X0aVHr44FK_ZGmfo4GUfEzMhEzL4xUGkS3RYWgB18g1NydMyPc33fKR0ChGMdDWDxPCZR2O59VWcnf20lr3iwIUp_ZTZw5s8jtDmtbioCxm)
22. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY2CJXCJwFjJRdfTYDLRwDb6d0ljxDflwisSelEoV8oQC6A2mTga8wTnxagte-ndAZV6hjWdUslf86WJjjYqliyFtbpRJ4QiYifnLKFbfmJTJLizKNcKnAgwli9wUyaiy-heP4BRTOdPVI3YZ3QDOb0lizGy4xQwVrm0-yZVUF1dD7EGOicTS9eMlrheH_iCbBhz8P1Bbfcw==)
23. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDLd3bXB1_mNZ28Wy0mmzQEahoFjqyYGG4cTo-sSEK6QYokBX1CzIZaw8soyO4VSICvqpQGNwo1fFs3NJnxKlKWjBAsrsh99wZie7jE3Keel77LDa31MugftgzBE8amHVG0g==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvMS_RlIZFo03d6NghkbedSF9g6U3LFdXg9oq-OzcrjTrSwBKCj-4uGeS9ofWZpSYpSjn9pde4r6BitZs_IzW2shx9rwxueqzGwmf4n_5QW49hXp3Wkb9OtBkPmvBIfl-OAL92ULHggtKVpC03a0YXxJtDniW9-mPnkeQadwwBJDFDP7PvvA==)
25. [ufn.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXmjvvmayBk4iXyhngjBbyd5hAni6WWqHoIdXlqvirnuqrsdfueqWJAMLn8TAK2G3Gpud43rrgBOT0LrAkaO54vsNwKjvU8rVxEK3IjZ1_8yNLE6FgtGhpl5dY9v4=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5iOZ_RTO1ZEupPG_rHdp-qop_MvisXQom62rWsKw2p_kQkkjjCs0tR7d-vPAsMN_c9ZAsxX-cyAle-bc8zbJWk0oqhLTJPh8XJSLa_7HX-VFamJuc)
27. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8KZ7dSkXAmxvwmDv9yHmBxJnsmyOPgz3xaOoWX4fciWp8_vxLuEoM2cNJz98JaJctNWm5rWKIf2FjmNDBPUVMuSb69w_xH7VggXboCbipxxf_6_4Q4dAZZuCSNezr8gXLci0urGUNND1ckNOATdyF4Srwc197fhWTZ5az5cS2T66Zf8J77OvA7RRRSApEXlzzTi7dvaR9Dh2EHgU3n43eDLyt8uXnrYw5JTKIm1lyhP4FK2qElPNDkSTvbNdUKZM=)
28. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEX70BkFcOiO8BHWpkdMsKIB5X1jR4QUfDkAccZq_icrXcIoqutISM7HiJmIVSO-jTrdnB3o-fuukftFvEyQD7gCPgy-vCcDl1WPL-tum921BrIF9UkjpUtRiwhzr23GWtBGiXQZAsyyqBOrstIydurUr9MUAuZFIdsLXVRNPGkAwVKEIl18aIBOxsnN4x9ew==)

