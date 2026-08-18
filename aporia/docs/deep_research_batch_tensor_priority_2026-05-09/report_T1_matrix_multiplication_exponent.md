# Report T#1 — Matrix Multiplication Exponent ω

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` #1.
**Date:** 2026-05-09.
**Channel:** Tensor-priority deep-research batch (manual Gemini-token redirect).
**Doctrine:** HARD-1 (no papers), HARD-2 (anti-gravitational-well), HARD-5 (structural-region language), HARD-6 (tools-we-need-most).
**Predecessor:** `aporia/docs/deep_research_batch9/report_176_matrix_multiplication_exponent.md` (2026-04-26). This report extends and updates that document with 2024–2025 results.
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK
**Attack vectors flagged:** P32 (Evolutionary-LLM Algorithm Synthesis), P33 (Asymmetry-as-Slack-Vector) — candidates for taxonomy

---

## Brief summary

Headline finding: the catalog entry's "current bound 2.371552" is already one frontier-step stale — the actual current bound is **ω < 2.371339** (Alman–Duan–Vassilevska Williams–Xu–Xu–Zhou, *More Asymmetry Yields Faster Matrix Multiplication*, arXiv:2404.16349, SODA 2025). Other 2024–2025 surfacings: Christandl–Hoeberechts–Nieuwboer–Vrana–Zuiddam *Asymptotic tensor rank is characterized by polynomials* (arXiv:2411.15789, STOC 2025), Briët–Christandl–Leigh–Shpilka–Zuiddam discreteness result (arXiv:2306.01718, ITCS 2024), Cohn–Umans-direction *Finite matrix multiplication algorithms from infinite groups* (arXiv:2410.14905, ITCS 2025), and AlphaEvolve's M⟨4,4,4⟩(ℂ) rank-48 decomposition (DeepMind 2025, first improvement on Strassen 4×4(ℂ) since 1969). Three patterns cited (mandatory 2; +PATTERN_RANK_PARITY_LEAK). Two attack-pattern candidates flagged for taxonomy: **P32 Evolutionary-LLM Algorithm Synthesis** (AlphaEvolve), **P33 Asymmetry-as-Slack-Vector** (the 2022→2024 Duan–Wu–Zhou → VWXXZ → ALDvWXXZ chain). One new substrate primitive proposed: **AsymptoticSpectrumMonotone** (sibling of CoordinateChart). Four substrate-tester tickets opened (T-ST-T1-001…004).

---

## 1. Problem Statement

The matrix multiplication exponent ω is

  ω = inf { τ ∈ ℝ : two n×n matrices over a field F can be multiplied in O(n^τ) arithmetic operations },

equivalently

  ω = lim_{n → ∞} log_n R(M⟨n⟩) = log_n R̃(M⟨n⟩),

where M⟨n⟩ ∈ F^{n²} ⊗ F^{n²} ⊗ F^{n²} is the matrix multiplication tensor whose (ij, jk, ki) entry is 1 (Einstein-summation convention) and R(·), R̃(·) denote tensor rank and asymptotic rank respectively. The two formulations coincide because M⟨n⟩ ⊗ M⟨n⟩ = M⟨n²⟩ as tensors, so ω = log_n R̃(M⟨n⟩) for any n ≥ 2 and ω = log_2 R̃(M⟨2⟩) is the cleanest scalar reduction.

Two output cardinality facts pin the trivial endpoints:
- ω ≥ 2 (the tensor has n² independent output entries, each of which must be touched).
- ω ≤ 3 (schoolbook).

Everything in between is a fifty-five-year-and-counting iteration of two ideas — *find better tensor decompositions* and *find better asymptotic monotones* — applied to a single tensor whose structure is too symmetric to crack and not symmetric enough to surrender.

## 2. Status & Bounds

Current frontier: **ω < 2.371339** (Alman–Duan–Vassilevska Williams–Xu–Xu–Zhou, *More Asymmetry Yields Faster Matrix Multiplication*, arXiv:2404.16349 v1 25-Apr-2024; SODA 2025). The 2.371552 bound named in the catalog entry is one frontier-step earlier (VWXXZ SODA 2024); the ALDvWXXZ result superseded it within the calendar year.

Lineage (each entry: bound, year, who, mechanism):

| Bound | Year | Who | Mechanism |
|---|---|---|---|
| 3 | trivial | — | schoolbook |
| 2.807 = log₂ 7 | 1969 | Strassen | direct rank-7 decomposition of M⟨2⟩ |
| 2.78 | 1979 | Pan | trilinear aggregation |
| ≤ 2.78 | 1979 | Bini–Capodaglio–Lotti–Romani | border rank, approximate algorithms |
| 2.522 | 1981 | Schönhage | τ-theorem (asymptotic sum inequality) |
| 2.479 | 1986 | Strassen | laser method (CW-style auxiliary tensor analysis) |
| 2.376 | 1990 | Coppersmith–Winograd | CW tensor at q = 6, optimized |
| 2.3729 | 2010 | Stothers | higher tensor powers of CW |
| 2.3727 | 2012 | Vassilevska Williams | systematic power optimization |
| 2.37286 | 2014 | Le Gall | refined power analysis |
| 2.37286 | 2021 | Alman–Vassilevska Williams | "Refined Laser Method" (arXiv:2010.05846) |
| 2.371866 | 2022 | Duan–Wu–Zhou | asymmetric hashing (arXiv:2210.10173, FOCS 2023) |
| 2.371552 | 2024 | Vassilevska Williams–Xu–Xu–Zhou | "From Alpha to Omega" (arXiv:2307.07970, SODA 2024) |
| **2.371339** | **2024** | **Alman–Duan–Vassilevska Williams–Xu–Xu–Zhou** | **More asymmetry (arXiv:2404.16349, SODA 2025)** |

Conditional / structural results worth tracking separately:

- **Laser-method barrier** (Alman–Vassilevska Williams 2018, Christandl–Vrana–Zuiddam, Conner–Gesmundo–Landsberg–Ventura 2021–2023): a wide class of laser-method instantiations on the CW tensor cannot give ω < 2.16805, regardless of which power is taken. Structural lower bound *on the technique*, not on ω itself.
- **Asymptotic rank computability** (Christandl–Hoeberechts–Nieuwboer–Vrana–Zuiddam, arXiv:2411.15789, 24-Nov-2024; STOC 2025): asymptotic tensor rank is upper-semicomputable via a polynomial functional family.
- **Asymptotic-rank discreteness** (Briët–Christandl–Leigh–Shpilka–Zuiddam, arXiv:2306.01718, ITCS 2024): over any finite field and over ℂ, asymptotic subrank and asymptotic slice rank have no accumulation points.
- **AlphaEvolve** (DeepMind, 2025): rediscovered M⟨4,4,4⟩ over ℂ at rank 48, the first improvement on Strassen's 49-multiplication count for 4×4 complex matrices since 1969.

ω = 2 conjecture: widely cited; consensus has been *softening*, not hardening, since the laser-method barrier was made explicit. Treat "ω = 2 by 2030" forecasts as folklore, not data.

## 3. Literature

2024–2025 (priority):
- **Alman, Duan, Vassilevska Williams, Xu, Xu, Zhou (2024).** *More Asymmetry Yields Faster Matrix Multiplication*. arXiv:2404.16349. SODA 2025. ω < 2.371339.
- **Vassilevska Williams, Xu, Xu, Zhou (2024).** *New Bounds for Matrix Multiplication: from Alpha to Omega*. arXiv:2307.07970. SODA 2024. ω < 2.371552.
- **Christandl, Hoeberechts, Nieuwboer, Vrana, Zuiddam (2024).** *Asymptotic tensor rank is characterized by polynomials*. arXiv:2411.15789. STOC 2025.
- **Briët, Christandl, Leigh, Shpilka, Zuiddam (2024).** *Discreteness of Asymptotic Tensor Ranks*. arXiv:2306.01718. ITCS 2024 / Discrete Analysis 2025.
- **Cohn, Shapiro, Umans, et al. (2024).** *Finite matrix multiplication algorithms from infinite groups*. arXiv:2410.14905. ITCS 2025.
- **DeepMind AlphaEvolve (2025).** Rediscovered M⟨4,4,4⟩(ℂ) at rank 48.
- **OpenTensor (2024).** arXiv:2405.20748.

Earlier load-bearing references (substrate calibration anchors):
- Strassen, *Gaussian elimination is not optimal* (1969). Numerische Mathematik 13:354–356.
- Coppersmith, Winograd (1990). *Matrix multiplication via arithmetic progressions*. J. Symbolic Computation 9:251–280.
- Cohn, Umans (2003). FOCS 2003. Triple Product Property.
- Cohn, Kleinberg, Szegedy, Umans (2005). FOCS 2005.
- Blasiak, Church, Cohn, Grochow, Naslund, Sawin, Umans (2017). Discrete Analysis 2017.
- Alman, Vassilevska Williams (2018). FOCS 2018 / arXiv:1810.08671.
- Alman, Vassilevska Williams (2021). arXiv:2010.05846. SODA 2021.
- Fawzi et al. (DeepMind), Nature 610:47–53, 2022. AlphaTensor.
- Bürgisser, Clausen, Shokrollahi (1997). *Algebraic Complexity Theory*.
- Landsberg (2017). *Geometry and Complexity Theory*.

Computational tooling:
- Macaulay2 (`SecantVarieties`, `Apolarity`); Bertini / HomotopyContinuation.jl; TensorLy / cotengra / opt_einsum; AlphaTensor reference impl + OpenTensor; SAT/SMT (CaDiCaL, Kissat, Z3).

## 4. Attack Vectors Active in the Literature

Mapped to `aporia/docs/attack_angle_taxonomy.md` paradigms P01–P31:

- **P28 — Asymptotic Spectrum (Strassen).** Primary. CHNVZ 2024 polynomial-functional characterization sits here.
- **P29 — Border Apolarity.** Buczyńska–Buczyński apolar-scheme arguments produce border-rank lower bounds on M⟨n⟩.
- **P31 — Secant Variety Geometry.** Young flattenings (Landsberg–Ottaviani); defining equations of σ_r(Seg).
- **P15 — Tensor / Multilinear Decomposition.** Brent equations, AlphaTensor / AlphaEvolve search, ALS, SAT/SMT.
- **P09 / P10 — Exhaustive Computation / Formal Verification.** SAT/SMT verification; AlphaEvolve reverification on rationals.
- **P22 — Polynomial Method.** Cohn–Umans CKSU candidates eliminated by Blasiak et al. 2017 using cap-set bounds.
- **P27 — Slice Rank / Polynomial Method on F_q.** Same machinery in different clothing.
- **P03 + P28 — Cohn–Umans Group-Theoretic Embedding.** The 2024 *Infinite groups* extension moves this toward P18 territory.

**New attack patterns not yet in the P01–P31 taxonomy — flagged for review:**

**Candidate P32 — Evolutionary-LLM Algorithm Synthesis.** AlphaEvolve (2025) uses LLM-generated code variants under a genetic-algorithm wrapper with a verifier-in-the-loop. The substrate-relevant content is *not* "LLMs are smart" — it is that the search space (programs that compute the matrix-product tensor exactly) admits a population-genetics traversal in the LLM's latent code-space with verifier-bounded acceptance. Structurally distinct from P09 (no enumeration), P15 (decomposition is a side-effect), P25 (no negative result is the lever). Distinct from MAP-Elites (deprecated P20) because the diversity is over *programs* not over quality-diversity bins.

**Candidate P33 — Asymmetry as a Slack Vector.** The 2022–2024 Duan–Wu–Zhou → VWXXZ → ALDvWXXZ chain is one paradigm executed three times: identify a symmetry assumption in a prior analysis, replace it with a parametrized asymmetric version, optimize the parameter. Not P03 (P03 *exploits* symmetry; P33 *breaks* it deliberately as a slack-finding move). Not P17 (variational) because parameter space is finite-dimensional.

## 5. Substrate Encoding

**5.1 Upper-bound certificates.** A claim "ω < 2.371339" is the conjunction of:
- A specific tensor T (here, a high power of an asymmetric CW-derived tensor).
- A rank-r decomposition of T witnessing R(T) ≤ r.
- A monotone evaluation showing r^{1/k} bounds ω for the tensor power k.

Encoding: **OperatorOutputSequence** for T; **CoordinateChart** registering the asymptotic-spectrum embedding; **ConstructiveExistenceWitness** (Tier-B meta-primitive) holding the rank-r decomposition.

**5.2 Lower-bound certificates.** A claim "asymptotic rank of CW(q) ≥ 4" (hypothetical) is the conjunction of an apolar 0-d Gorenstein scheme S realizing the obstruction (P29) and a multigraded Hilbert-function evaluation showing rank ≤ 3 incompatibility.

Encoding: **ExclusionCertificate** (Tier-C meta-primitive) holding the apolar scheme.

**5.3 Asymptotic-spectrum monotones.** *NEW PRIMITIVE PROPOSAL*: **AsymptoticSpectrumMonotone**. Signature: `Tensor → ℝ ∪ {∞}`, with a contract that monotonicity under restriction is verifiable on a registered restriction-relation substrate. Sibling of CoordinateChart, not sub-type. CHNVZ 2024 asserts asymptotic rank is the supremum of a polynomial-functional family — primitive needs to expose a *supremum-over-family* operation as first-class.

**5.4 Tensor-network representations.** Tier-A++ TensorNetwork meta-primitive. M⟨n⟩ has natural TT/MPS representations whose bond dimensions encode partial rank information.

**5.5 Gap flagged for substrate-tester.** The combination "apolar-scheme obstruction + Young-flattening rank bound + asymptotic-spectrum monotone evaluation" is the canonical evidence chain for a serious lower-bound result. The substrate currently has primitives for each piece individually, but no **CompositeRankCertificate** primitive that registers the conjunction with an audit trail. **Open ticket recommendation: T-ST-T1-001.**

## 6. Calibration Anchor Notes

ω is a *high-canonicality* topic — heavy Wikipedia / popular-press coverage. The Learner is therefore prone to **FM-08 (confused-identity) failures with confident attribution** rather than to FM-04 (ungrounded fabrication of names).

**Substrate-grade vs textbook-trivial:**
- *Textbook-trivial:* "ω is the matrix multiplication exponent; current bound is around 2.37."
- *Substrate-grade:* explicitly cites the bound *to six significant figures with the corresponding source-and-year*; states the laser-method barrier with quantitative threshold (2.16805); distinguishes ω from ω₀ from ω̃; names the asymptotic-spectrum framework.

**Canonical fabrication risks:**
1. Strassen's exponent: correct ω ≤ log₂ 7 ≈ 2.807. Risks: "ω = log₂ 8", "ω = 2.78".
2. AlphaTensor attribution: correct Fawzi et al. Nature 2022. Risks: attributing to Hassabis; conflating with AlphaEvolve.
3. AlphaEvolve 4×4 result: correct rank 48 over ℂ. Risks: "rank 47 over ℝ", "improvement over ω asymptotically".
4. ω vs ω₀ distinction.
5. Cohn–Umans / CKSU attribution; TPP vs Strong USP confusion.
6. Christandl–Vrana–Zuiddam quantum functionals — high FM-04 risk on content.
7. Bound-string fabrication: "ω < 2.37289" plausibly emitted as exact.

**Trivial-vs-open within conjecture family (FM-08):**
- ω is *open* in the strong sense.
- R(M⟨2⟩) = 7 is *closed* (Hopcroft–Kerr 1971, Winograd 1971).
- R(M⟨3⟩) is *open* in a quantitative window (19 ≤ R(M⟨3⟩) ≤ 23).
- R̃(M⟨2⟩) is *open* and is the asymptotic-rank quantity that pinpoints ω.

**Resolution-dependent truth:** Bound 2.371339 is exact-for-now; substrate must store (claim, bound, method, source, timestamp) as a unit, not just (claim, bound). PATTERN_BASE_RATE_NEGLECT applies.

## 7. Cross-References

**Within `aporia/mathematics/tensor_open_problems_v1.md`:**
- #2 Strassen's asymptotic rank conjecture; #3 T_{cw,2} asymptotic rank; #4 Exact rank M⟨3⟩; #5 Border rank M⟨n⟩; #6 Border-rank additivity; #11 Laser-method limits; #28 Asymptotic spectrum; #88 Group-algebra multiplication; #89 Cohn–Umans triple product property.

**Existing reports:**
- `deep_research_batch9/report_176_matrix_multiplication_exponent.md` (predecessor; superseded for bound + AlphaEvolve content).
- `deep_research_batch10/report_192_pit_derandomization_barriers.md` (PIT, partial-derivative methods overlap with Young-flattening).

**Substrate-tester capability-gap tickets to open or escalate:**
- **T-ST-T1-001** *CompositeRankCertificate* — Tier-B + Tier-C + AsymptoticSpectrumMonotone composition contract.
- **T-ST-T1-002** *AsymptoticSpectrumMonotone primitive* — sibling of CoordinateChart, signature `Tensor → ℝ ∪ {∞}`.
- **T-ST-T1-003** *Time-stamped frontier-bound storage* — running-best-upper-bound objects need timestamp + source axis.
- **T-ST-T1-004** *AlphaEvolve-class evolutionary-LLM search primitive* — if P32 candidate opens, substrate-tester needs evidence-trace contract for verifier-trail logging.

**Cross-reference to attack_angle_taxonomy.md:**
- P28, P29, P31, P15 confirmed-active.
- P22, P27 active in killer role (cap-set bounds eliminate CKSU).
- **P32 (Evolutionary-LLM) and P33 (Asymmetry-as-Slack-Vector) flagged as candidate additions.**

---

## Pattern citations

**PATTERN_BASE_RATE_NEGLECT.** ω-improvement headlines like "ω < 2.371339" obscure the base rate: roughly one ω-decrement per 2–3 years over the last decade, with each decrement smaller than the last. The popular-press framing "we are converging on ω = 2" is a base-rate-neglected reading.

**PATTERN_VRAM_TRUNCATION_ARTIFACT.** RL-discovered tensor decompositions (AlphaTensor 2022, AlphaEvolve 2025) are sensitive to numerical precision. AlphaEvolve's M⟨4,4,4⟩(ℂ) at rank 48 must be reverified with rational or algebraic-number arithmetic, not just floating-point checks. Generalization: "any precision-bound on a numerical certificate that hides structural information."

**PATTERN_RANK_PARITY_LEAK.** Rank decompositions over different fields (F₂, F₃, ℚ, ℝ, ℂ) are different objects. AlphaTensor's R(M⟨4,5,5⟩) ≤ 76 over F₂ does *not* lift to ℚ. Substrate's `OperatorOutputSequence` node for any rank-decomposition certificate must store the field as a first-class attribute.

---

*Aporia, 2026-05-09. Tensor-priority deep-research batch. Pattern citations: 3 (mandatory 2; PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK). Attack-vector additions flagged: P32 (Evolutionary-LLM Algorithm Synthesis), P33 (Asymmetry-as-Slack-Vector). Substrate-gap tickets flagged: T-ST-T1-001 through T-ST-T1-004. New primitive proposed: AsymptoticSpectrumMonotone.*
