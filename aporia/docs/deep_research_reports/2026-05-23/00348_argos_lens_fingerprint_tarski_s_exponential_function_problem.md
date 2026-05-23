# Argos lens fingerprint: Tarski's exponential function problem

**Pythia queue id:** 348
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkZlFRYW82NUlLLVVfdU1QeDVxNjZBSRIXZGZRUWFvNjVJSy1VX3VNUHg1cTY2QUk
**Elapsed:** 250s
**Completed at:** 2026-05-23T00:31:44.720932+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem `MATH-0358`: Tarski's Exponential Function Problem

**Key Points:**
*   **The Problem:** Tarski's exponential function problem asks whether the first-order logical theory of the real numbers, expanded by the exponential function—denoted $\mathbb{R}_{\exp}$—is decidable. While the base theory of real closed fields is decidable, adding exponentiation introduces profound complexities related to transcendental numbers.
*   **Current Status:** The problem remains definitively open unconditionally. However, a landmark 1996 theorem by Macintyre and Wilkie established that $\mathbb{R}_{\exp}$ is decidable *if* Schanuel's conjecture (a profound and widely believed, yet unproven, proposition in transcendental number theory) is true. 
*   **Dynamical Systems Lens:** In computational verification, Tarski's problem acts as a bottleneck for proving the reachability or termination of linear dynamical systems. Researchers project this problem onto the task of finding "o-minimal invariants"—geometric boundaries that trap system orbits.
*   **Information Theory Lens:** In information theory, the problem intersects with defining the exact geometric bounds of entropy spaces. Determining whether arbitrary linear inequalities governing continuous entropy distributions are valid ultimately reduces to logical systems bounded by exponential and logarithmic maps.
*   **Renormalization Group Lens:** In theoretical physics, the logic of Tarski's problem is applied to the Renormalization Group (RG) via the concept of "tameness." Physicists conjecture that realistic quantum field theories must be definable in o-minimal structures (like $\mathbb{R}_{\text{an}, \exp}$), forbidding wild, undecidable oscillations in physical observables across energy scales.

This report executes a multi-perspective attack on open problem `MATH-0358`, applying the analytical lenses of Dynamical Systems, Information Theory, and Renormalization Group physics. By examining how diverse computational and physical domains project, interpret, and resolve (or bypass) the undecidability barrier of the real exponential field, we map the deep structural footprint of this problem across modern mathematics.

---

## 1. Theoretical Architecture of `MATH-0358`

To understand the interdisciplinary applications of Tarski's exponential function problem, one must first rigorously establish its formulation within mathematical logic and model theory [cite: 1, 2]. 

### 1.1 First-Order Theory of the Reals
In 1951, Alfred Tarski published a monumental result demonstrating that the first-order theory of the real closed fields (often termed Tarski arithmetic) is decidable [cite: 1, 2]. The language of this theory is $\mathcal{L}_{\text{or}} = \{+, \cdot, <, 0, 1\}$. Tarski proved that any statement formulated with these symbols, utilizing universal ($\forall$) and existential ($\exists$) quantifiers, can be algorithmically evaluated as true or false [cite: 2]. This was achieved through the method of **quantifier elimination**, specifically algorithms later refined into cylindrical algebraic decomposition. Because the primitive operations are restricted to addition and multiplication, the definable numbers within this structure are strictly the real algebraic numbers [cite: 2].

### 1.2 The Exponential Expansion and Undecidability Horizons
Tarski subsequently posed `MATH-0358`: if the language is expanded to include the exponential function, $\mathcal{L}_{\exp} = \{+, \cdot, <, 0, 1, \exp\}$, is the resulting theory, denoted $\mathbb{R}_{\exp} = (\mathbb{R}, +, \cdot, 0, 1, <, \exp)$, still decidable? [cite: 1, 3]. 

The introduction of the exponential function $x \mapsto e^x$ destroys the algebraic simplicity of the reals because it introduces transcendental elements [cite: 3, 4]. In contrast, if one were to introduce the sine function, the resulting theory $\mathbb{R}_{\sin}$ is definitively **undecidable** [cite: 2]. This is due to Richardson's theorem: the zeros of the sine function ($\pi \mathbb{Z}$) allow for the encoding of the integers, and by Gödel's incompleteness theorems and Matiyasevich's resolution of Hilbert's Tenth Problem, the first-order theory of integers (Peano arithmetic) is undecidable [cite: 2]. 

The exponential function, however, is strictly monotonic and possesses no periodic roots over the reals, raising the possibility that $\mathbb{R}_{\exp}$ might escape Gödelian undecidability [cite: 1, 2].

### 1.3 The Macintyre-Wilkie Theorem and Schanuel's Conjecture
The most significant progress on `MATH-0358` was achieved by Angus Macintyre and Alex Wilkie in 1996 [cite: 1, 4]. They proved that Tarski's exponential function problem is decidable, *conditional* on the truth of Schanuel's conjecture [cite: 1, 5]. 

Schanuel's conjecture is a sweeping statement in transcendental number theory:
If $z_1, \dots, z_n$ are complex numbers that are linearly independent over the rational numbers $\mathbb{Q}$, then the extension field $\mathbb{Q}(z_1, \dots, z_n, e^{z_1}, \dots, e^{z_n})$ has a transcendence degree of at least $n$ [cite: 5]. 

This conjecture implies the algebraic independence of $e$ and $\pi$ and generalized forms of the Lindemann-Weierstrass theorem [cite: 5]. Macintyre and Wilkie demonstrated that only the real version of Schanuel's conjecture is strictly necessary to provide an upper bound for the search space of zeros in exponential polynomials, thereby granting an effective decision procedure for $\mathbb{R}_{\exp}$ [cite: 6]. However, unconditional decidability remains a profound open question [cite: 3, 4].

---

## 2. Lens 1: `STANCE_DYNAMICAL_SYSTEMS@v1`

The first lens applies the logic of `MATH-0358` to **Dynamical Systems**, specifically in the context of reachability, termination analysis, and the Orbit Problem in computer science and control theory [cite: 7, 8]. 

In evaluating linear loops and hybrid systems, verification algorithms must frequently determine whether a system trajectory (an orbit) will eventually enter a designated "error" or "halting" state [cite: 9, 10]. This reduces directly to determining the truth of logical formulas over real numbers involving exponential flows (for continuous time) or discrete exponentiations (for discrete time) [cite: 7, 8].

### 2.1 Primary Attempt 1: O-Minimal Invariants for Discrete-Time Systems
**Primary Source:** *O-minimal invariants for discrete-time dynamical systems* by S. Almagor, D. Chistikov, J. Ouaknine, and J. Worrell (2022) [cite: 9, 11].

#### (a) Measurement Projected
This literature attempts to project `MATH-0358` onto the synthesis of **inductive invariants** [cite: 9, 10]. A discrete-time linear dynamical system (LDS) is defined by a state space $\mathbb{R}^d$, a transition matrix $A \in \mathbb{Q}^{d \times d}$, and an initial point $s \in \mathbb{R}^d$. The orbit is $\mathcal{O} = \{A^n s \mid n \ge 0\}$ [cite: 9]. The algorithmic goal is to determine if $\mathcal{O}$ intersects a target semialgebraic set $F$.

Because the orbit is a discrete set of points, it cannot generally be captured by purely algebraic logic. The authors measure the problem by projecting it into **o-minimal structures**—specifically $\mathbb{R}_{\exp}$ [cite: 9]. An o-minimal structure acts as a "tame" geometry where subsets of $\mathbb{R}^n$ have finitely many connected components [cite: 9, 12]. The authors construct a measurement tool called an *o-minimal invariant*: a set $I \subseteq \mathbb{R}^d$ definable in $\mathbb{R}_{\exp}$ such that $s \in I$, $A I \subseteq I$, and $I \cap F = \emptyset$ [cite: 9]. To do this, they over-approximate the discrete orbit using a continuous "trajectory cone" generated by the continuous real exponential envelope of the matrix $A$ [cite: 9].

```text
// Logical schema of an o-minimal invariant search
Function SynthesizeInvariant(A, s, F):
    Define trajectory_cone C_t0 = { e^{At} x | t >= t0 }
    Let I_candidate = C_t0 U {A^0 s, A^1 s, ..., A^{t0} s}
    If I_candidate ∩ F == ∅ AND A(I_candidate) ⊆ I_candidate:
        Return I_candidate (Safe)
    Else:
        Return Unknown
```

#### (b) Verdict Reached
The authors conclude that the existence and algorithmic synthesis of such o-minimal invariants for discrete-time LDS is **decidable**, provided that `MATH-0358` is affirmatively resolved [cite: 9, 10]. Because Macintyre-Wilkie established that $\mathbb{R}_{\exp}$ is decidable modulo Schanuel's conjecture, the synthesis of these continuous invariant bounds is conditionally computable [cite: 9]. They bypass the severe number-theoretic intractability of the Skolem Problem (which asks precisely if $A^n s \in F$) by bounding the orbit within a tame, continuous geometric volume definable in Tarski's exponential language [cite: 9, 10]. 

#### (c) Axis of Disagreement
The dynamical systems lens fundamentally disagrees with strict algebraic and discrete lenses (such as Information Theory) on the necessity of point-by-point exactness. The DS lens accepts that the exact discrete orbit $\mathcal{O}$ might be too "wild" to analyze directly. Instead, it relies on topological over-approximation—encasing the discrete infinity within a continuous, finite-complexity o-minimal boundary [cite: 9]. Disagreement centers on **asymptotic tolerance**: DS focuses on infinite-time continuous limits and topological containment rather than exact combinatorics.

### 2.2 Primary Attempt 2: Reachability in Continuous LDS and the Black-Box Reduction
**Primary Source:** *On the decidability of reachability in continuous time linear time-invariant systems* by M. Dantam and A. Pouly (2020) [cite: 8], and extended by *On the Existential Theory of the Reals with Integer Powers of a Computable Number* by J. Gallego-Hernández and A. Mansutti (2025) [cite: 4, 13].

#### (a) Measurement Projected
This literature projects `MATH-0358` onto continuous-time reachability, asking if $\exists t \in \mathbb{R}_{\ge 0}$ such that $e^{At}x_0 \in U$ [cite: 7]. Gallego-Hernández and Mansutti precisely measure how much of the full power of $\mathbb{R}_{\exp}$ is actually needed for these dynamical models [cite: 4, 13]. They project the problem not into the full exponential field, but into a specific fragment: the existential theory of the reals enriched with a predicate for the integer powers of a computable real number $\xi$, denoted $\exists\mathbb{R}(\xi^\mathbb{Z})$ [cite: 4, 13]. 

#### (b) Verdict Reached
Dantam, Pouly, and subsequent works established that continuous reachability relies on $\mathbb{R}_{\exp}$ as a "black-box" to achieve conditional decidability [cite: 4, 8]. However, Gallego-Hernández and Mansutti achieved a powerful unconditional breakthrough: they proved that if $\xi$ is an algebraic number (or has computable root barriers), the satisfiability of $\exists\mathbb{R}(\xi^\mathbb{Z})$ is unconditionally decidable in 2ExpTime or 3ExpTime, effectively detaching specific dynamical systems applications from the conditional reliance on Schanuel's conjecture [cite: 4, 13]. They demonstrated a "small witness property" where only finitely many integer powers must be checked [cite: 13].

#### (c) Axis of Disagreement
This approach disagrees with the general application of the Macintyre-Wilkie theorem. While mainstream model theorists treat `MATH-0358` holistically, this subset of the DS lens argues that treating $\mathbb{R}_{\exp}$ as a generic "black-box" is computational overkill for physical and engineered systems [cite: 4]. They diverge by strictly limiting the analytic depth of the problem, proving that physical verification often requires only a highly restricted, unconditionally decidable fragment of the exponential field [cite: 4, 13].

---

## 3. Lens 2: `STANCE_INFORMATION_THEORY@v1`

The second lens translates `MATH-0358` into the combinatorial and geometric domains of **Information Theory**, specifically addressing the Information Inequality Problem, entropy cones, and the polymatroidal axioms [cite: 14, 15].

The entropy of discrete random variables is defined using logarithms ($H(X) = -\sum p(x) \log p(x)$) [cite: 14]. Identifying the complete set of valid inequalities that govern these entropies requires translating discrete joint probabilities into continuous vectors, forming topological closures that implicitly rely on exponential and logarithmic mappings to define their geometric boundaries [cite: 15, 16].

### 3.1 Primary Attempt 1: The Information Inequality Problem and Polymatroid Axioms
**Primary Source:** *Information Inequality Problem over Set Functions* by Khamis et al. (2024) [cite: 15], building on the foundational work of Pippenger (1986) [cite: 17] and Zhang & Yeung (1998) [cite: 18, 19].

#### (a) Measurement Projected
In 1986, Pippenger posited that the laws of information theory were completely described by the polymatroidal axioms (Shannon-type inequalities): $H(\emptyset) = 0$, $H(X) \le H(X \cup Y)$ (monotonicity), and $H(X) + H(Y) \ge H(X \cap Y) + H(X \cup Y)$ (submodularity) [cite: 14, 17]. The measurement projected here is the exact geometry of the **entropic region** $\Gamma_n^*$ [cite: 18, 19]. Researchers attempt to measure whether an arbitrary linear information inequality is valid by determining if it bounds the topological closure of the entropic cone $\bar{\Gamma}_n^*$ [cite: 16, 18]. 

#### (b) Verdict Reached
Zhang and Yeung famously proved Pippenger wrong by discovering non-Shannon information inequalities, proving that the polymatroidal axioms do not perfectly bound the entropy cone [cite: 15, 19]. Khamis et al. examined the computational complexity of the Information Inequality Problem (deciding if a linear inequality holds over all entropies). They reached the verdict that while restricted cases (like normal polymatroids) are coNP-complete, the general decidability of the Information Inequality Problem remains a massive open question [cite: 15]. The precise geometry of the boundary involves transcendental gaps; identifying if a point lies in the closure $\bar{\Gamma}_n^*$ relies on limits of probabilities mapped through the continuous logarithm function, tying the ultimate decidability of the entropy cone back to the decidability of exponential polynomials [cite: 16, 20].

#### (c) Axis of Disagreement
Information Theory fundamentally disagrees with the Renormalization Group (Lens 3) regarding the utility of "tameness." In IT, the discovery of non-Shannon inequalities implies that the space of valid distributions is profoundly complex, highly constrained, and possibly computationally irreducible (untame) at higher dimensions [cite: 15, 19]. IT insists on exact, rigid linear inequality boundaries mapped from discrete finite systems (matroids), disagreeing with both the continuous flow approximations of DS and the scale-integrations of RG.

### 3.2 Primary Attempt 2: First-Order Probabilistic Logic and Definability
**Primary Source:** *First-order Probabilistic Logic* studies (e.g., Li et al., 2021) focusing on the arithmetical definability of distribution regions [cite: 20].

#### (a) Measurement Projected
This literature attempts to project `MATH-0358` into the realm of First-Order Theory of Probabilistic Inequalities (FOTPI). The measurement involves encoding properties like mutual information and conditional independence ($I(X;Y|Z) \ge 0$) as first-order logical formulas over real-valued probability distributions [cite: 20]. The goal is to determine if sets of probability distributions bounded by specific entropy limits are definable and decidable. Because entropy definitions involve $\sum x \log x$, determining the truth of these bounds logically invokes the real exponential function [cite: 20].

#### (b) Verdict Reached
The verdict reached is that generalized FOTPI is not arithmetically definable due to Tarski's undefinability theorem [cite: 20]. However, the specific subset of formulas concerning cardinality bounds and entropy regions inherently depends on Tarski's exponential function problem. If $\mathbb{R}_{\exp}$ is decidable, then certain geometric regions of entropy vectors without auxiliary random variables might be algorithmically computable [cite: 20]. The literature effectively suspends judgment, citing the unresolved status of `MATH-0358` (and Schanuel's conjecture) as the hard barrier preventing the automated verification of generalized network information theories [cite: 17, 20].

#### (c) Axis of Disagreement
This approach disagrees with the Dynamical Systems black-box reduction. While DS attempts to carve out unconditionally decidable fragments (like $\xi^{\mathbb{Z}}$), FOTPI researchers recognize that information geometry heavily relies on the full continuous spectrum of the base-$2$ or base-$e$ logarithm applied to arbitrary probability masses [cite: 14, 20]. Consequently, Information Theory cannot easily truncate the exponential function to integer powers; it must confront the full weight of Tarski's problem head-on.

---

## 4. Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

The third lens views `MATH-0358` through the paradigm of theoretical physics—specifically, the **Renormalization Group (RG)** and Quantum Field Theory (QFT). Here, mathematical logic is used not to build software algorithms, but to formulate universal constraints on the laws of physics [cite: 12, 21].

### 4.1 Primary Attempt 1: Tameness of Perturbative QFT Amplitudes
**Primary Source:** *Tameness of Quantum Field Theory* by M. R. Douglas, T. W. Grimm, and L. Schlechter (2022) [cite: 12, 21].

#### (a) Measurement Projected
Douglas, Grimm, and Schlechter project the logic of Tarski's problem onto the calculation of Feynman amplitudes [cite: 12]. In QFT, physical observables (like scattering cross-sections) are calculated via integrals over loop momenta. The authors measure whether these resulting functions of external momenta and coupling constants are "tame" [cite: 12, 21]. 

In this context, **tameness is precisely defined as definability in an o-minimal structure**, specifically $\mathbb{R}_{\text{an}, \exp}$ (the expansion of the real field by restricted analytic functions and the global exponential function) [cite: 12, 22]. Tarski's problem and the o-minimality of $\mathbb{R}_{\exp}$ (proved by Wilkie following Macintyre's work) provide the mathematical guarantee that tame functions cannot exhibit infinite discrete oscillations or undecidable Gödelian geometries [cite: 12, 21].

\[
\mathcal{S} = \{S_n\}_{n \ge 1} \text{ is o-minimal if every definable subset of } \mathbb{R} \text{ is a finite union of points and intervals.}
\]

#### (b) Verdict Reached
The authors reach the definitive verdict that for any renormalizable QFT, amplitudes at any fixed, finite order in the loop expansion are tame functions [cite: 12, 21]. Because Feynman integrals can be expressed as periods and mapped into $\mathbb{R}_{\text{an}, \exp}$, they inherit the logical finiteness of Tarski's expanded field [cite: 12, 22]. This proves that physical observables at the perturbative level will never suffer from infinite, chaotic zero-crossings or mathematical undecidability; they are bounded by the rigid topology of o-minimality [cite: 21, 22].

#### (c) Axis of Disagreement
This lens represents a monumental shift in perspective. While DS and IT view `MATH-0358` as an algorithmic hurdle (a question of *computability*), the RG lens views o-minimality and the decidability of $\mathbb{R}_{\exp}$ as a **fundamental law of nature** [cite: 12, 23]. The physicists disagree with the pure mathematicians' view of arbitrary functions; they assert that the universe actively avoids structures that fall outside of Tarski's decidable geometries [cite: 22, 23].

### 4.2 Primary Attempt 2: Tameness of Exact RG Flows and Swampland Conjectures
**Primary Source:** Subsequent research on *Tameness and Complexity in QFTs* / *Tameness of CFTs* by Douglas, Grimm, and Schlechter (2023) [cite: 22, 23].

#### (a) Measurement Projected
The authors extend the application of $\mathbb{R}_{\exp}$ to the non-perturbative regime and the flow of the Renormalization Group itself [cite: 22, 23]. As a theory changes energy scales (from UV to IR), its coupling constants follow RG flow equations. The authors measure whether the trajectory of these exact RG flows, and the broader space of all Conformal Field Theories (CFTs), remain definable within tame, o-minimal structures [cite: 22, 23].

#### (b) Verdict Reached
The verdict here is highly nuanced and borders on a new physical postulate. The authors show that *exact*, unconstrained RG flows can theoretically exhibit non-tame behaviors, such as infinite discrete limit cycles, which violate the finiteness axioms of o-minimality [cite: 12, 22]. However, they introduce a "Swampland Conjecture": any Effective Field Theory (EFT) that can be consistently coupled to quantum gravity must be tame [cite: 21, 22]. Therefore, physical RG flows operating within realistic bounds (with finite cutoffs) preserve tameness. Tarski's logical limits are weaponized to distinguish physically valid theories from mathematical "swampland" [cite: 12, 23].

#### (c) Axis of Disagreement
This physical lens disagrees sharply with Dynamical Systems. In DS, infinite limit cycles and chaotic orbits are standard features to be bounded or avoided using o-minimal invariants [cite: 7, 9]. In the RG Swampland perspective, such infinite limit cycles in fundamental coupling space are deemed physically impossible or unnatural if gravity is involved [cite: 12, 22]. The axis of disagreement lies in the ontological status of untame geometries: DS seeks to contain them computationally, IT relies on them to bound complex entropies, but RG physics conjectures they simply do not exist in the true vacuum structure of the universe [cite: 22, 23].

---

## 5. Synthesis: The Multi-Perspective Footprint of `MATH-0358`

The fingerprint of Tarski's exponential function problem reveals a fundamental mathematical boundary where continuous geometric flow meets discrete computational logic. 

### 5.1 The Geometry of Infinity
At the heart of the disagreement across the three lenses is how each field manages **infinity**.
*   **Dynamical Systems** encounters infinity through *time* ($t \to \infty$ or $n \to \infty$). It relies on the Macintyre-Wilkie theorem conditionally to draw finite, continuous o-minimal boundaries (trajectory cones) around infinite discrete orbits [cite: 9]. 
*   **Information Theory** encounters infinity through *dimensional limits and continuous distributions*. The topological closure of the entropy cone requires mapping discrete, finite probabilities into continuous space via the exponential/logarithmic bijection [cite: 16, 20]. Here, the undecidability barrier of `MATH-0358` manifests as the ultimate limit of our ability to write automated geometric proofs for network capacity [cite: 20].
*   **Renormalization Group** encounters infinity through *energy scales and loop integrals*. It utilizes the concept of o-minimality (the geometric counterpart to Tarski's decidable logic) to enforce global finiteness [cite: 12, 22]. Tameness acts as a cosmological censor, forbidding the infinite discrete oscillations that cause Gödelian undecidability in physical observables [cite: 21, 23].

### 5.2 Conditional vs. Unconditional Thresholds
A fascinating methodological divergence is how fields treat Schanuel's conjecture. Model theorists and information theorists largely wait for Schanuel's conjecture to be proven to unlock $\mathbb{R}_{\exp}$ [cite: 1, 5, 20]. However, computational disciplines are actively routing around it. The DS lens (via Gallego-Hernández and Mansutti) has successfully isolated fragments like $\exists\mathbb{R}(\xi^\mathbb{Z})$ that are unconditionally decidable, proving that physical dynamics rarely require the full transcendental weight of $\mathbb{R}_{\exp}$ [cite: 4, 13]. Meanwhile, the RG lens bypasses computational verification entirely, elevating the tameness of $\mathbb{R}_{\text{an}, \exp}$ into an axiomatic necessity for quantum gravity [cite: 22, 23].

## Conclusion

Tarski's exponential function problem (`MATH-0358`) is not merely an esoteric puzzle in model theory. As demonstrated by this multi-lens analysis, it is the foundational logical bedrock governing what is knowable across the quantitative sciences. Whether attempting to prove that a software loop will terminate (Dynamical Systems) [cite: 9], calculating the ultimate limits of data compression (Information Theory) [cite: 15], or mapping the fundamental coupling constants of the universe (Renormalization Group) [cite: 12], researchers inevitably collide with the decidability horizon of the real exponential field. The problem dictates the strict geometric boundaries where computational logic, transcendental number theory, and physical reality align.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcRrw-7yAAENaqGoL8i0GdM8O1Dm9KAZ5k_L4fV4BqnWgvEak1zymCvvj4rMNCoSgDKyHBal0vBaHIFn8qB-gNzc10OAQ8o5Y-NsKcCDUY4PogKqnJidAndSUBLwMW6G6g4Xbo1b5u6qTOSKkIqcoG-nT5FbW9UZSZUz0=)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfzOrOdeLh1X8UOmKBWw6x3Av06SXtR8E3HdpNIIwWa9aqUkF8ncPKwLaoSKJjtY4t6co4IddgsV1DgVY-H-F6Eg6e16XbQw-FwIwaoT4zNMrF_7CkI1tQgc0ZN9iy5Dg1QCdmdOuhzvHz2n7ePQFI6mlW5QyOS50Qm8H14KCAIj2WVLjXwKyvxf3HHQ==)
3. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBUGA4hP2q7dh2PVfqqbuAgA31IIDbeCGN129p60jmin52Necbd8YT3kw0l8reh3Z8EZu8zXTYn1CgaZ6vEAh8vnE_5iauuj2le6yc5hk5QUGRKF8R4mXsZkMv3LkJSlP09HaljaSGSmzp6NjTzdjIqkS_0_5SCzOV0Q==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGimuo4CpKJMaNHpg0-eqxJPIN1TSmoe002vumz9CtaXryCehdBuUZSh2Z8v2I7lIlaOm8rD12vRHPr49yrAis2K1PrKIdgkgYegZSsPg4UN9uX7-ccpg==)
5. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2RzzsfuEQmRF5VBWekSSmdUDY0QrwPRULBe69-A7jOQYGLRODxyawxLmeFCEqDEXEXQyVaAhuSNz1Aan2OAOqZM9IT1vDfbzwdV51gIe1TW8GMNpmBiyp86zY4kuzxSuXJ8fcR29B3b89JQ==)
6. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHchWdqKn--NhqgTlgk_8-7JDKqNoEMlf2wwSEyLuGHZTiYXm-OGQHMyqisaVip79CjaKNHNiha8ur790ZQSV8JWoqvweorX3bhtaxSvQHOO4u0OQEzhcbO8IIzdEXYTuWj)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqFuwWKATFC76sxeHcLoqlW7-KSXnrr9Vv_fHp9wUtOSlgr6dMcyshkxlS7W7-ANcFS_u-jnCR3Sx3EXU4CBXrxzoL7ab3qP26q1lGkx-sjCCOTePmXA==)
8. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbdr3sH2I6IFDr3U0SOQAwZBHchpREUJkbESU1GrG5DzGk9IUmnJmfe83sg_iAdyxqGbJdZAot7yPdTz0Avn-4yjhsxolBjoB3QhZ9Ku4BqtFjSWqwMmoadtaM7a0STXFz_PCDNbzQniFcN-3YUfA4xtYtDPldcN3QiPOHSRHcnIrd7hhEDff9NSvmOEDeFFWkfH7DMrMT4YZ1DDLKFJ6xYxtVp-eJLZ4GhjXqMLI1sAVJLaUt-_KSNocZFROirGT1EZMe)
9. [mpi-sws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdvrpK8U95wPy5lz25GuMTE6Gn04pV_DhbdjRYisYJem5XIFFYDRubCXwI7Q_qWh1UwAVPeX0jksFMb8DGhUjzuMrPTrdiOxERefmkV80nFowHqcpqbjI9PBJie5DhBTO5Fpcf68Wc5UW8QrsXF--Cviuin-LekJnIMSA=)
10. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2XUYs1PgV8VoVLZizw8SOXgSC_zzBICVBK0OsYkJIMecsH7FktH7P0E_pNJmpMotgWdDZrSjuX_1OoSYq8fsg9n1OepCRG2ww8vZdvij6EYN9OwSLeZHYRTPZSPXcvNvJS5SxyWSgdax6mflCzuikdzxHFIbcK0mgan7vQEVn)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9M8IL7XQxMCAd96mK6wpSzDRqPWKa7LRa5ZZBmlPKDVpshfdm7JC7-nFiJhDVBtRS9HUfmkGyd0PLx--kt9FGyn917uqfaMv7psVuavRhx2dNEObmNzrlX4ecE0kY-g6gQtmN-zsrzMGx5IEkGle2aE5M2FSnvqZiQbXfzjYebwNPdDoWqW75UYNOCd3v6DeAgWQIYlvTvj_3EXKyg_57PA==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZr_GaVDQZ52IB51D22C3n0YLolGtMRixa1ax0jEq4hOXtObFDUepsMogdGfY9d0DZ9Xl9Qio6RDcAFfkYVAbzLWmJWqRmTeWBoLNTm-AIcxbh2bLjgw==)
13. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn4MAYYIvLqQTJxqHE0rcMEmXtmQ0FFFrThdQP-xujFs2KkLk0-6iLB8jGTY7qMb3xmzgT0dS2I1LkDj-kIxh3cbs7lZrPU1HHFU3edTSmGBcdrVJYe7k8vQC_NgBHewRKWKNgsGYquM7MKxNmaFj6z2Kd_TAyYiGWmWLKe47tDo3MfgDUvE4il2_aj68DxzAxfYf88y91Mw0QLDFHoqIgnKr0w924)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR29ehu6VuKmqB5hlSBGVCuD-z7nYzmTVMn_jIx_BcuvFCi5to-c6qh5Frue4XO93dx4r68-V0bCh-rvCImZ4tk8xLNDmdT5toMyiSzStcjwWSc5DuRg==)
15. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEspeEyaERCF4n_7QfWkBiRnoYeRYQsAGANK4KIKAYldQU0gMXbwoUBAYXQoTUNdpv49jv7hJtsVn3XnbR24YcAg-pzlofYLTXnsuCbEvDKE70gG3jTE0dwzOVabt4noDjr55SsOvNT5ZiD1-MDZTczQoGwTqQkchmt3jLlU-rkjJkT8eKjNlRHSs0ooOXgdq218d2a_dJwzWoEBzwi-_MiflmN)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoL7YmNYlY9vP5JW8hl-PFzpW-N8DKfBlhPyUT9bzFpq_L8rDDprVqNja5OuojCdsWpa4mxkCCBRPzuMSbg324i2AeojQVRwOUOZ0aB8i_OhjO_WXa0RhBxFlBMbnadzSSe3PPb_PO2xKyiTNL3QyZs682wLQIZwsHL6zijtVd5to-PmAtTcTIEW8ovkXjkLBM00utCw==)
17. [cuhk.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHULCzWenC6s9_KGIzVTnfjAWloVjKKQ3QHtP5oDBewAYo7tJum9qUAz0w5FxBdJdplUpowUI6mpIqSjhKGIeuBzGA-u58XZMzETnOEP-So7L8NyC6c_-HnApAARY4xRqeNC20ZHGDu_5HzYs7R2JbS_07KxD6t6rT5_PDF)
18. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK6EKFQ22IEFugh1TVdC5whFyxuyeOxuRppKq-msCMh8O6-XFv4ii1_gsKqWz0tylpJpfhFb6PTDsNf3JhrCeBVNq6NdKSlxnwm71L8sg3tFdezsjD-RX_yqU0nrPa7KO0S2X_eic=)
19. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaoZDyiapZ0jUdQxz-64NeCiQAVESc3HXViq9O2KE_y4upMnEa_oRJsbf8t6g_oy911bRDRhv-UKduxcmjSq0IDmcNpoo7ni3aNH8UyFEisOLrXt_rrfEx-sAlZA==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_N4AyNuPKgyndyz2fgwEg0n719eAw_Ix-ehyA3JPomQLVCTddPEcMupuLmG0WzAhiHJjE40KQ76_UAUwhUS-q1WcKYn2uqh6LIZ7396UNzcc5U0mkoA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGerSvugADryi3HmubzKYlxUZAw6IKrumXjeKr7FnLNZUT73-Pm7jj53nSE-nKRkdF7J-ITMOaFaJuWXx0N7lxwRhHN8fczwjJ0L2FD8031oeC9cDcTw3u3dA==)
22. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq94athbEtUyzDCewvllSuHsvqNqeoarO0OweUEV8L7-ObT6QKM4CzBPuRlzoUT1Ve4smu_WSJq1x5DMcjk6PtBP55ED3oyVJLvYdMaP3TtIiZUoZucmmkG271gGH9K3blPKldxdqEibtCB9phbeyHeKP1fnz2kInS3asxB75VXKl4zmELUyq8Jn31dlnVEsUfrrJm2j00FlZUykvnnzk=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNtAUcoqfBFsANrF_CJtHVB34ibHYaRkxahw_NtOQKQq6QzZL4ndC-vRCocstqn6rOIbW16O-Z93ZTEPl3hg_8ETQxHJxhg0i5yOMx-XlvQ9oXX6uM-g==)

