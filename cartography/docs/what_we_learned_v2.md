# What We Learned v3: After the Effect Geometry Correction
## Project Prometheus — Charon Cartography Pipeline
## 2026-04-12 — Revised after F24 (variance decomposition) + council stress tests
## Supersedes all prior "what we learned" documents

---

## Part I: The Instrument Upgrade

### What changed
The battery went from 23 tests to 25 (F24 + F24b). More importantly, we added a missing axis:

**Before:** "Is it real? Is it robust?"
**After:** "Is it real? Is it robust? How big is it? Is the big-looking number a tail artifact?"

This caught a systematic bias: **M4/M2² is a contrast amplifier, not a magnitude measure.** It detects tail differences with extreme sensitivity but says nothing about how much variance a grouping variable explains. Several findings that looked dramatic (3.7× M4/M2² ratios) turned out to explain <5% of variance.

### The new ontology
Findings are no longer just PROBABLE. They are classified by **effect geometry**:

| Type | Definition | What it means |
|------|-----------|---------------|
| **LAW** | eta² > 0.14, not tail-driven | Dominant organizing principle |
| **CONSTRAINT** | Tail-driven signal (any eta²) | Boundary condition / rare configuration effect |
| **TENDENCY** | Small eta², not tail-driven | Weak but consistent background structure |

### New battery tests
- **F24 (Variance Decomposition):** eta² classification. Mandatory annotation, not a kill gate.
- **F24b (Metric Consistency):** Cross-metric sanity check. Flags TAIL_DRIVEN when M4/M2² contrast is high but eta² is low. Includes tail localization (% of deviation from top 10% of data).

---

## Part II: The Findings — Reclassified

### LAW: Space group constrains Tc (eta² = 0.457)
- Space group explains **46% of the variance** in superconducting critical temperature.
- Also constrains cell volume (eta² = 0.40) through an **independent pathway** — controlling for volume, SG→Tc strengthens to eta² = 0.51.
- Band gap weakly predicted (eta² = 0.095).
- F24b: CONSISTENT (not tail-driven). The effect is in the bulk of the distribution.
- **This is a dominant organizing principle.** If you removed the space group, your understanding of Tc would collapse.

### CONSTRAINT: Endomorphism algebra constrains conductor factorization (eta² = 0.050, tail-driven)
- Specialized Sato-Tate groups have more uniform conductor exponents than generic (USp(4)).
- **But:** eta² = 0.050. ST group explains only 5% of exponent variance. Within-group CV = 0.92.
- **F24b: EXTREME_TAIL_DRIVEN** (tail contribution = 69%). The M4/M2² ratio of 2.69 between groups comes from tail differences, not bulk separation.
- **Council stress tests:** Q2 confirmed small effect. Q5 (null model) showed USp(4) exponents are indistinguishable from random — only G_{3,3} deviates from the null. Q3 (label permutation) survived (p < 0.001). Q7 (scaling) converges cleanly.
- **Honest statement:** "Specialized ST groups show a tail constraint on conductor exponents. The effect is real but small — a boundary condition, not a bulk driver."

### TENDENCY: ST group determines conductor/discriminant fiber ratio (eta² = 0.027)
- The ratio log(conductor)/log(discriminant) varies weakly by ST group.
- eta² = 0.027. F24b: CONSISTENT (not tail-driven, tail contribution = 24%).
- **Honest statement:** "A diffuse weak signal across the entire distribution. Background structural tendency, not a strong organizing principle."

### EXACT IDENTITY: E_6 forces root number = +1
- 51/51 E_6 curves. P(null) = 2^{-51}. Variance = 0.
- Does NOT generalize to genus-1 CM curves (tested, null).
- Specific to genus-2 E_6 component group.

### Validated (exact mathematical identities, from previous sessions)
- Euler relation: chi = 1 + (-1)^(d+1)
- S_n character formula: M4/M2^2 = p(n)/n

---

## Part III: What M4/M2² Actually Measures

The council stress tests revealed:

> **M4/M2² is a sensitive detector of tail structure, not a measure of effect strength.**

Every measurement tool has a geometry of attention:
- M4/M2² → looks at tails
- eta² → looks at variance explained
- Correlation → looks at linear structure
- Median difference → looks at bulk separation

The battery is now a **multi-perspective observer**: F1-F23 test reality and robustness, F24 measures magnitude, F24b diagnoses distributional shape. A finding characterized by all four axes is much harder to misinterpret.

### The trap we fell into
A weak effect (eta² = 0.05) + large sample (66K curves) + tail-sensitive statistic (M4/M2²) = dramatic-looking result (3.7× ratio). The system correctly detected the signal, correctly verified it was robust, but failed to contextualize its magnitude. F24 fixes this permanently.

---

## Part IV: What We Don't Know Yet

1. **Why SG→Tc is so strong (eta² = 0.46).** This is a dominant effect — nearly half the variance in Tc is explained by crystal symmetry alone. What physical mechanism makes symmetry so predictive of superconductivity?
2. **Whether the endomorphism constraint generalizes beyond the LMFDB sample.** It replicated in genus-1 (CM vs non-CM), but the effect is small. Is it a deep arithmetic phenomenon or a database selection artifact?
3. **Whether there are other LAW-level findings hiding in the data.** The pipeline was built around M4/M2², which biases toward tail-driven effects. A eta²-first search strategy might find different (stronger) structure.
4. **Layer 3 (transformation detection)** — still unexplored.
5. **Cross-domain novel connections** — still zero confirmed.

---

## Part V: Battery Architecture (current)

**25 tests, 3 tiers + effect geometry:**

| Tier | Tests | Purpose |
|------|-------|---------|
| A (Detection) | F1, F3, F5, F6, F8, F10, F18 | Is there signal? |
| B (Structure) | F2, F4, F7, F9, F11, F12, F13, F14, F17, F21, F23 | Is it real? |
| C (Ensemble) | F15, F16, F19, F20, F22 | What's the simplest description? |
| **D (Magnitude)** | **F24, F24b** | **How big? What shape?** |

**Acceptance:** Tier A + Tier B = real and robust. Tier D classifies as LAW / CONSTRAINT / TENDENCY.

**Finding types:**
- **LAW:** eta² > 0.14, F24b CONSISTENT → dominant structure
- **CONSTRAINT:** F24b TAIL_DRIVEN → boundary condition
- **TENDENCY:** small eta², F24b CONSISTENT → background effect

---

*v3 revised: 2026-04-12*
*After: council stress tests, F24+F24b, effect geometry reclassification*
*Before: 3 PROBABLE (all looked the same). After: 1 LAW + 1 CONSTRAINT + 1 TENDENCY.*
*The instrument now measures magnitude, not just existence.*
