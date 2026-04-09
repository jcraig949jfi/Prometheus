# The Rosetta Stone: Formula Reputation Across Domains

## Discovery Date: 2026-04-09
## Status: FOUNDATIONAL — preserve and develop

---

## What We Found

While investigating cross-domain "bridges" in the OpenWebMath corpus, we discovered that apparent false positives (the same formula appearing in different domain classifications) are actually a map of **mathematical universals** — structural patterns that humanity reuses across fields.

When the formula `∫₀^{π/2} sin(φ) dφ` appears labeled "analysis" on one page and "physics" on another and "number theory" on a third, that's not noise. That's evidence of a shared mathematical verb that three different communities use independently.

## Why This Matters

### For AI Translation (symbolic math ↔ humanspeak)

A future system that needs to explain mathematics to humans needs to know:
- Which mathematical structures appear in which human contexts
- What the same formula MEANS in different fields
- Which structural patterns are universal vs domain-specific

This is exactly what our operadic skeleton → domain mapping provides:
- `multiply(V,V)` appears in 8 domains → this is a universal pattern (products are everywhere)
- `int(N,frac(V,N),multiply(sin(V),power(V,N)))` appears only in analysis → specialized pattern
- A skeleton that spans analysis + number theory + physics = a Rosetta Stone entry

### For Mathematical Discovery

Formulas that appear in many domains are the **load-bearing structures** of mathematics. They're the verbs that connect different noun-worlds. Our standing order "verbs over nouns" was exactly right — the verbs that span the most domains are the most powerful.

### For Education

Knowing that `frac(d,dx) ∫ f(x) dx = f(x)` appears in calculus, physics, probability, and engineering tells a teacher: this is a concept that MUST be understood across contexts. The reputation score of a formula = its pedagogical importance.

---

## Data We Have

From the 500K operadic signature run:
- **5,424 cross-domain operadic clusters** — skeletons appearing in 2+ domains
- **364,494 unique skeletons** from 500K formulas
- Domain distribution: 8 domain categories from OpenWebMath

From the 12.5M formula corpus:
- **27M parsed operator trees** with full structural decomposition
- **Domain labels** from OpenWebMath classification (analysis, number_theory, trigonometry, combinatorics, algebra, set_theory, logic, unclassified)

## The Rosetta Stone Structure

```
For each operadic skeleton:
  skeleton_hash: "770e75c7633f25bd"
  skeleton_str:  "multiply(V,V)"
  domains:       [analysis, number_theory, trigonometry, combinatorics, algebra, ...]
  n_domains:     8
  n_instances:   1,904
  reputation:    universal (8/8 domains)
  
  example_formulas:
    analysis:       "f(x) · g(x)"
    number_theory:  "p · q"  
    trigonometry:   "sin(θ) · cos(θ)"
    combinatorics:  "n · k"
    algebra:        "a · b"
    
  human_meaning:
    The product — combining two quantities. Universal because
    multiplication is the fundamental binary operation of mathematics.
```

## What To Build

### 1. Formula Reputation Index
For each skeleton: how many domains use it? Score from 1 (specialist) to 8 (universal).

### 2. Cross-Domain Translation Dictionary
For each universal skeleton: collect example formulas from each domain. The dictionary entries show how the same structure gets dressed in different notation:
- In analysis: ∫f dx
- In physics: ∫F·ds
- In probability: E[X]
- In number theory: Σ_{n≤x} f(n)

Same verb (sum/integrate), different nouns.

### 3. Pedagogical Importance Score
Formulas with high domain reputation AND high complexity are the most important concepts to teach. Simple universals (multiply) are trivial. Complex universals (the Euler product = product over primes of geometric series) are profound.

`importance = reputation × complexity`

### 4. Structural Translation for Future Systems
When a future AI needs to explain a number theory formula to a physicist, the Rosetta Stone provides: "this number-theoretic sum has the same operadic structure as this physics integral you already know."

This is not metaphor — it's structural isomorphism. The operadic skeleton IS the translation.

---

## Connection to Kill #12

Kill #12 was: `(a,∞)` in analysis matched `(c,γ)` in number theory. We killed it as a notation artifact. But the deeper truth: interval notation IS reused across fields. The same structural pattern `(V,V)` means "ordered pair" in set theory, "open interval" in analysis, "parameter pair" in number theory, and "coordinate" in geometry.

The kill was correct (it's not a novel discovery). But the observation that notation reuse maps mathematical conceptual structure — that's the Rosetta Stone.

---

## Preservation Note

This document captures a finding that emerged from Kill #12 investigation on 2026-04-09. The finding is:

**The cross-domain distribution of operadic skeletons in mathematical formulas is a map of how humans organize mathematical knowledge. Each skeleton that spans multiple domains is a structural universal — a mathematical verb that different communities use independently. This map is a Rosetta Stone for translating between mathematical domains and between symbolic math and human understanding.**

Do not discard the OpenWebMath domain-labeled data. The "noise" IS the signal — just a different signal than we were looking for.

---

*Discovered: 2026-04-09, during Kill #12 investigation*
*Charon, Project Prometheus*
*"The ferryman found the Rosetta Stone while looking for bridges"*
