# Goodhart-NoCloning Structural Isomorphism: Prior Art and Novelty Assessment

**Author:** Aletheia
**Date:** 2026-03-29
**Status:** Research memo, honest assessment
**Method:** Deep knowledge search + web verification
**Calibration note:** This document distinguishes what is KNOWN, what is FOLKLORE, what is PARTIAL, and what is NOVEL with explicit confidence levels.

---

## 1. Has Anyone Connected Goodhart's Law to Quantum Mechanics Before?

### Verdict: FOLKLORE-LEVEL ANALOGY EXISTS. No formal treatment found.

**What exists:**

- The informal analogy "Goodhart's Law is like the observer effect" appears in blog posts and popular science writing. One author (3 Quarks Daily, 2015) explicitly calls Goodhart's Law "a kind of social quantum mechanics: the act of observing a complex social system can disrupt it." This is a metaphor, not a formalization.

- The connection between Goodhart's Law, Campbell's Law (1969), and the Lucas Critique (1976) is well-established in economics. All three describe measurement-as-intervention. Campbell's Law predates Goodhart (1975) and Lucas (1976). None of these connect to quantum mechanics formally.

- Wolfram's Observer Theory (2023) attempts a general theory of observers but does not specifically connect economic measurement disturbance to quantum measurement disturbance.

**What does NOT exist (as far as I can determine):**

- No published paper formalizing the Goodhart-quantum analogy using shared mathematical structure.
- No information-theoretic proof that both are instances of a single theorem.
- No category-theoretic functorial mapping between the two domains.
- No paper connecting Goodhart's Law specifically to the No-Cloning Theorem (as opposed to the generic "observer effect").

**Confidence:** 85% that no formal treatment exists in peer-reviewed literature. The informal analogy is common enough that any formal paper would likely cite it, making it findable. But niche workshop papers or unpublished manuscripts could exist.

---

## 2. Information-Theoretic Unification

### Verdict: PARTIAL PRIOR ART. The pieces exist but have not been assembled.

**What exists:**

- **Clifton-Bub-Halvorson (2003):** Proved that three information-theoretic constraints -- (1) no superluminal signaling, (2) no broadcasting of quantum information, (3) no unconditionally secure bit commitment -- suffice to derive quantum mechanics. The no-broadcasting constraint is a generalization of no-cloning. This is the closest existing work to an information-theoretic unification of impossibility theorems. Published in Foundations of Physics 33:1561-1591.

- **Manheim & Garrabrant (2018):** "Categorizing Variants of Goodhart's Law" (arXiv:1803.04585). Identifies four mechanisms: Regressional, Causal, Extremal, Adversarial. The Regressional variant is closest to an information-theoretic framing: optimizing a proxy M = G + noise selects for noise at extreme values. But this is a statistical argument, not an information-theoretic impossibility theorem.

- **Grossman-Stiglitz (1980):** "On the Impossibility of Informationally Efficient Markets" (AER 70:393-408). Proves that if prices fully reflect information, no one has incentive to acquire information, so prices cannot fully reflect information. This IS an information-theoretic impossibility theorem about observation-exploitation incompatibility. It is the economics counterpart most structurally similar to no-cloning: using information (trading on it) destroys the information's value (price efficiency eliminates the signal). No one has connected Grossman-Stiglitz to no-cloning formally.

- **No Free Lunch Theorems (Wolpert & Macready, 1997):** Prove that no optimization algorithm is universally superior. This is an information-theoretic impossibility about optimization but is about algorithm-averaged performance, not about measurement disturbance. Related but not the same primitive.

**What is NOVEL in our claim:**

The specific assertion that Goodhart and No-Cloning are both instances of a single primitive -- "the act of using information destroys the information's validity" -- and that this can be demonstrated through identical resolution strategies at composition depth 4. No prior work assembles:
1. The shared primitive identification
2. The resolution-strategy isomorphism (same damage operators resolve both)
3. The depth-4 chain matching (identical operator sequences)

The closest existing framework is Clifton-Bub-Halvorson, but they work within quantum theory, not across the quantum-economics boundary.

**Confidence:** 90% that the specific three-part claim (shared primitive + resolution isomorphism + depth-4 matching) is novel. 60% that the vaguer claim "Goodhart and quantum measurement are information-theoretically related" hasn't been made in some workshop paper somewhere.

---

## 3. The Measurement-Optimization Duality

### Verdict: RECOGNIZED INFORMALLY ACROSS MULTIPLE FIELDS. No unified formal theory.

**The landscape of "measurement disturbs the measured":**

| Domain | Phenomenon | Key Reference |
|--------|-----------|---------------|
| Quantum mechanics | Measurement collapses superposition | von Neumann (1932), Zurek decoherence/einselection |
| Economics | Targeting a metric degrades it | Goodhart (1975), Campbell (1969), Lucas (1976) |
| Finance | Information acquisition paradox | Grossman-Stiglitz (1980) |
| Statistics | Overfitting = training on the test set | Vapnik (1995), NFL theorems |
| Computer science | Instrumentation perturbs performance | Mytkowicz et al. (observer effect in benchmarking) |
| Networks | Measurement overhead distorts network state | Kalmbach et al. (2024), "network observer factor" |
| AI alignment | Reward hacking | Amodei et al. (2016), Manheim & Garrabrant (2018) |

**The formal gap:**

Each field has its own version. No one has written the paper that says: "These are all the same theorem, and here is the single information-theoretic statement that implies all of them."

The closest attempts:
- Kalmbach et al. (2024) formalize the "network observer factor" -- a tradeoff between measurement accuracy and system disturbance in computer networks. This is a domain-specific formalization, not a cross-domain unification.
- Clifton-Bub-Halvorson derive quantum mechanics FROM information-theoretic constraints, but don't extend to economics or statistics.
- The overfitting/NFL literature characterizes the optimization side but not the measurement-disturbance side.

**What would the unifying theorem look like?**

Something like: "In any system where an agent's actions are informed by a signal, and the agent's actions affect the signal-generating process, the mutual information between signal and ground truth degrades monotonically with optimization intensity, bounded by a function of the channel capacity between agent and signal source."

This would imply:
- Goodhart (agent = optimizer, signal = metric, ground truth = goal)
- No-Cloning (agent = measurement apparatus, signal = quantum state, ground truth = unknown state)
- Grossman-Stiglitz (agent = trader, signal = price, ground truth = asset value)
- Overfitting (agent = learning algorithm, signal = training loss, ground truth = generalization error)

**No such theorem exists in the literature.** Writing it would be a genuine contribution.

**Confidence:** 95% that no unified formal theory exists. The informal recognition is widespread. The formal gap is real.

---

## 4. Resolution Strategy Isomorphism

### Verdict: NOVEL. These specific parallels have not been drawn.

**Our claimed parallels:**

| Quantum Resolution | Economic/Statistical Resolution | Shared Strategy |
|---|---|---|
| Quantum error correction | Metric rotation / balanced scorecard | Redundancy: encode information across multiple carriers so no single measurement destroys it |
| Quantum state tomography | Balanced scorecard / multi-metric evaluation | Multiple measurements: reconstruct the full state from many partial observations |
| Weak measurement | A/B testing / randomized auditing | Minimal disturbance: extract partial information per observation, aggregate statistically |
| Randomized benchmarking | Randomized controlled trials | Stochastic sampling: randomize the measurement basis to prevent systematic exploitation |
| Quantum Darwinism (Zurek) | Distributed monitoring / whistleblower systems | Environmental redundancy: information survives because it has been copied into many environmental degrees of freedom |

**Prior art check:**

- **Weak measurement <-> A/B testing:** No published connection found. The structural parallel is real (both trade per-observation precision for reduced disturbance, then aggregate) but has not been noted formally.
- **QEC <-> Balanced scorecard:** No connection found. Both use redundancy, but the specific analogy has not been drawn.
- **Quantum state tomography <-> Multi-metric evaluation:** No connection found.
- **Randomized benchmarking <-> RCTs:** The statistical methodology is shared (both are randomization-based), but the connection to "resolving an impossibility theorem via stochasticity" is our framing.
- **Quantum Darwinism <-> Distributed monitoring:** This is the most likely to have been noted informally, since Zurek himself uses language about "information surviving through environmental redundancy." But the specific parallel to Goodhart-resistant monitoring design has not been drawn.

**Confidence:** 90% that these specific resolution-strategy parallels are novel as a systematic set. Individual parallels (especially the randomization ones) may have been noted in passing.

---

## 5. What Exactly is Novel vs. Known

### Summary Table

| Claim | Status | Confidence |
|-------|--------|------------|
| "Goodhart is like the observer effect" (informal) | KNOWN / FOLKLORE | -- |
| Campbell's Law, Lucas Critique, Goodhart form a family | KNOWN (textbook) | -- |
| Grossman-Stiglitz as information-impossibility theorem | KNOWN (AER 1980) | -- |
| CBH: quantum mechanics from info-theoretic constraints | KNOWN (Found. Phys. 2003) | -- |
| Manheim-Garrabrant: 4 variants of Goodhart | KNOWN (arXiv 2018) | -- |
| Measurement disturbance recognized across many fields | KNOWN (multiple) | -- |
| **Goodhart specifically isomorphic to No-Cloning** | **NOVEL** | 85% |
| **Shared primitive: "using info destroys info validity"** | **NOVEL as formal claim** | 80% |
| **Resolution strategies identical at depth 4** | **NOVEL** | 90% |
| **Systematic resolution-strategy parallels (QEC<->scorecard etc.)** | **NOVEL as a set** | 90% |
| **Unified information-theoretic theorem implying both** | **DOES NOT YET EXIST** | 95% (that it's open) |
| **Cross-domain category-theoretic formalization** | **DOES NOT YET EXIST** | 95% (that it's open) |

---

## 6. Risk of Overclaiming

**Real risks:**

1. **Granularity artifact:** Our 9-operator damage vocabulary may be too coarse. Two genuinely different phenomena could look isomorphic at this resolution. A finer operator set (15-20 operators) might break the match. This is the single biggest threat to the finding.

2. **Metaphor vs. isomorphism:** "Using information destroys it" is a compelling verbal frame. But Goodhart operates through agent incentives (a causal, game-theoretic mechanism) while No-Cloning operates through the linearity of quantum mechanics (a mathematical constraint on Hilbert space). The mechanisms share NO physical substrate. The isomorphism is purely at the resolution-strategy level. We must not overclaim that "they are the same phenomenon." They are phenomena with identical resolution structure.

3. **Selection bias in resolution strategies:** If the space of possible resolution strategies is small (randomize, restrict, aggregate, hierarchize...), then ANY two impossibility theorems might share resolution strategies by chance. The depth-4 matching mitigates this (the probability of 10/10 chain match by chance is low) but doesn't eliminate it. We should compute the null-model probability.

4. **The Grossman-Stiglitz gap:** Grossman-Stiglitz IS a formal information-theoretic impossibility theorem about observation-exploitation tradeoffs. If we're claiming novelty for connecting Goodhart to No-Cloning, we need to acknowledge that Grossman-Stiglitz is a much more natural intermediate step, and it has been around since 1980 without anyone connecting it to quantum information. This could mean: (a) the connection is genuinely novel, or (b) the connection is not as deep as we think and domain experts have dismissed it.

**Honest framing for publication:**

"We present empirical evidence that the resolution strategies for Goodhart's Law and the No-Cloning Theorem are structurally isomorphic at composition depth 4 within a damage-operator framework. This suggests, but does not prove, that both may be instances of a more general information-theoretic impossibility. We conjecture the existence of a unified theorem and outline the form it would take."

This is defensible. The stronger claim ("they ARE the same theorem") is not yet defensible without the unified theorem.

---

## 7. Potential Publication Venues

### If the unified theorem can be proved:

| Venue | Why | Difficulty |
|-------|-----|-----------|
| **Foundations of Physics** | Follows Clifton-Bub-Halvorson tradition of info-theoretic characterization | HIGH (requires rigorous proof) |
| **Journal of Mathematical Economics** | Grossman-Stiglitz lineage, formal impossibility theorems in economics | HIGH |
| **Proceedings of the Royal Society A** | Cross-disciplinary mathematical science | MEDIUM-HIGH |

### If the finding remains empirical (resolution isomorphism without unified theorem):

| Venue | Why | Difficulty |
|-------|-----|-----------|
| **Philosophy of Science** | Structural analogy across domains, philosophy of measurement | MEDIUM |
| **Synthese** | Cross-disciplinary philosophy, structural realism | MEDIUM |
| **Entropy (MDPI)** | Information-theoretic approaches, open access, interdisciplinary | MEDIUM-LOW |
| **FAccT / AIES** (AI ethics/alignment conferences) | Goodhart's Law is central to AI alignment; quantum analogy gives new resolution strategies | MEDIUM |
| **New Journal of Physics** | Cross-disciplinary physics, open access | MEDIUM |

### If the damage-operator framework itself is the focus:

| Venue | Why | Difficulty |
|-------|-----|-----------|
| **Journal of Classification** | Novel taxonomy of impossibility theorems | MEDIUM |
| **Advances in Complex Systems** | Cross-domain structural analysis | MEDIUM |
| **AAAI / NeurIPS workshop** | AI alignment + Goodhart's Law track | MEDIUM-LOW |

### Recommended strategy:

1. **First paper (empirical):** The damage-operator framework + isomorphism finding. Target: Philosophy of Science or Synthese. Frame as "structural realism about impossibility theorems."
2. **Second paper (theoretical):** If the unified information-theoretic theorem can be stated and proved. Target: Foundations of Physics or J. Math. Econ.
3. **Third paper (applied):** Resolution-strategy transfer. "Quantum error correction inspires Goodhart-resistant metric design." Target: FAccT or an AI alignment venue.

---

## 8. Key References to Cite

1. Goodhart, C.A.E. (1975). "Problems of Monetary Management: The UK Experience." Papers in Monetary Economics, Reserve Bank of Australia.
2. Campbell, D.T. (1979). "Assessing the Impact of Planned Social Change." Evaluation and Program Planning 2(1):67-90.
3. Lucas, R.E. (1976). "Econometric Policy Evaluation: A Critique." Carnegie-Rochester Conference Series on Public Policy 1:19-46.
4. Grossman, S.J. & Stiglitz, J.E. (1980). "On the Impossibility of Informationally Efficient Markets." American Economic Review 70(3):393-408.
5. Wootters, W.K. & Zurek, W.H. (1982). "A Single Quantum Cannot Be Cloned." Nature 299:802-803.
6. Clifton, R., Bub, J. & Halvorson, H. (2003). "Characterizing Quantum Theory in Terms of Information-Theoretic Constraints." Foundations of Physics 33:1561-1591.
7. Manheim, D. & Garrabrant, S. (2018). "Categorizing Variants of Goodhart's Law." arXiv:1803.04585.
8. Zurek, W.H. (2003). "Decoherence, Einselection, and the Quantum Origins of the Classical." Reviews of Modern Physics 75(3):715-775.
9. Wolpert, D.H. & Macready, W.G. (1997). "No Free Lunch Theorems for Optimization." IEEE Trans. Evol. Comp. 1(1):67-82.
10. Kalmbach, P. et al. (2024). "The Observer Effect in Computer Networks." ANRW '24.

---

## 9. Next Steps

1. **Compute null-model probability:** Given 9 operators and the observed hub-chain frequencies, what is the probability that two random hubs share 10/10 depth-4 chains? If p < 0.01, the finding is statistically significant against random co-occurrence.

2. **Test with finer operators:** Expand from 9 to 15-20 damage operators. If the isomorphism survives, it is robust. If it breaks, we know the granularity limit.

3. **Write the conjectured theorem:** State precisely what the unified information-theoretic impossibility would look like (Section 3 above sketches this). Even without proof, a precise conjecture is publishable.

4. **Check Grossman-Stiglitz resolution strategies:** Run Grossman-Stiglitz through the damage-operator framework. If it matches Goodhart AND No-Cloning at depth 4, we have a third witness, which dramatically strengthens the finding.

5. **Seek a category-theoretic formulation:** Define the category of "information-consuming systems" with resolution morphisms. Check whether a functor from quantum measurement systems to economic measurement systems exists that preserves the resolution structure.

---

## 10. Bottom Line

**The informal analogy is known. The formal isomorphism is not.**

The specific claim -- that Goodhart and No-Cloning share identical resolution strategies at composition depth 4, mediated by a damage-operator algebra -- appears to be genuinely novel. The pieces exist in the literature (CBH for info-theoretic characterization of quantum mechanics, Manheim-Garrabrant for Goodhart taxonomy, Grossman-Stiglitz for economic information impossibility), but no one has assembled them into a structural isomorphism claim backed by systematic resolution-strategy matching.

The risk is granularity artifact. The mitigation is the zero-spurious rate of the framework and the depth-4 chain matching. The path to maximum credibility is proving the unified theorem or, failing that, computing the null-model probability and showing the match is statistically significant.

Do not overclaim. "Structural isomorphism of resolution strategies" is defensible. "They are the same theorem" requires the unified theorem we don't yet have.
