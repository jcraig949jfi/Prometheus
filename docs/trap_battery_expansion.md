# Trap Battery Expansion Plan

*From 15 parsing traps to 60+ reasoning categories spanning parsing, judgment, and metacognition*

---

## The Problem

The current 15-trap battery is a closed vocabulary. Every tool in the library — the 54 clones and the 239 genuine ones — has a dispatch table that maps 1:1 to these 15 categories. Scoring 100% means "has a parser for each of the 15 known patterns," not "can reason." When something falls outside the vocabulary, tools drop to NCD fallback.

For RLVF, this means the model being trained will learn to produce reasoning traces that trigger the dispatch tables — formatting output to match recognized patterns rather than learning to reason. That's Goodhart at the architectural level.

**The real metric for the library isn't "median accuracy on the trap battery" — it's "how many distinct reasoning failure modes can the ensemble collectively identify?"**

---

## Two Tiers of Traps

### Tier A: Parsing Traps (deterministic correct answer from structure)
The answer is computable if you correctly parse the prompt. The difficulty is in not being fooled by surface features. Current 15 traps are mostly this type.

### Tier B: Judgment Traps (correct response requires recognizing ambiguity, insufficiency, or meta-level reasoning)
The "right answer" requires recognizing something about the question itself — that it's ambiguous, unanswerable, contains a presupposition, or requires evaluating reasoning quality rather than factual correctness.

**Score these tiers separately in Coeus.** A tool that gets 90% parsing / 60% judgment has a different competency profile than one at 70% / 70%.

---

## Existing 15 Categories (Tier A — Parsing)

1. Numeric float comparison
2. Equal-weight trick question
3. Positional logic (overtake)
4. Algebraic word problem (bat-and-ball)
5. Universal quantifier converse error
6. Mathematical identity (0.999...=1)
7. Pigeonhole principle
8. Statistical independence (gambler's fallacy)
9. Number parity (odd+odd=even)
10. "All but N" survivor counting
11. Transitive ordering
12. Negation scope insufficiency
13. Stated premise usage
14. Subject-object verb parsing
15. Modus tollens (contrapositive)

---

## Expansion Phase 1: Temporal + Probabilistic (Categories 16-24)

*Goal: Check whether dynamics-first tools (Oscillations, SOC, Immune) wake up.*

### Tier A (Parsing — deterministic answers)

**16. Temporal ordering**
"Event A happened before B. Event B happened before C. Did A happen before C?"
candidates: ["Yes", "No", "Cannot determine"] correct: "Yes"
Parametric: Yes (infinite entity/event combos)
Self-contained: Yes

**17. Parallel vs sequential processes**
"It takes 5 minutes to toast one slice of bread. How long to toast 3 slices if you have a 3-slot toaster?"
candidates: ["15 minutes", "5 minutes"] correct: "5 minutes"
Parametric: Yes (vary items, times, slot counts)
Self-contained: Yes

**18. Rate/inverse proportion**
"6 workers finish a job in 12 days. How many days for 9 workers?"
candidates: ["8", "18", "6", "12"] correct: "8"
Parametric: Yes (vary workers, days)
Self-contained: Yes
*Note: answer = (workers1 × days1) / workers2*

**19. Base rate neglect (Bayesian)**
"A disease affects 1 in 1000 people. A test is 99% accurate (1% false positive). You test positive. What's the probability you actually have the disease?"
candidates: ["About 99%", "About 9%", "About 50%"] correct: "About 9%"
Parametric: Yes (vary prevalence, accuracy)
Self-contained: Yes
*Note: P(disease|positive) = P(pos|disease)×P(disease) / P(pos) ≈ 0.99×0.001 / (0.99×0.001 + 0.01×0.999) ≈ 9%*

**20. Conjunction fallacy**
"Linda is 31, outspoken, and was a philosophy major who cared about social justice. Which is more likely: (A) Linda is a bank teller, or (B) Linda is a bank teller who is active in the feminist movement?"
candidates: ["A", "B"] correct: "A"
Parametric: Partially (vary name, description, occupations)
Self-contained: Yes
*Note: P(A∩B) ≤ P(A) always*

**21. Conditional probability asymmetry**
"80% of dogs are friendly. 60% of friendly animals are dogs. Is the probability that a friendly animal is a dog the same as the probability that a dog is friendly?"
candidates: ["Yes", "No"] correct: "No"
Parametric: Yes (vary percentages, categories)
Self-contained: Yes

**22. Expected value vs probability**
"Game A: win $100 with 10% chance. Game B: win $20 with 60% chance. Which game has higher expected value?"
candidates: ["Game A", "Game B", "They're equal"] correct: "Game B"
Parametric: Yes (vary amounts, probabilities)
Self-contained: Yes
*Note: EV(A) = $10, EV(B) = $12*

### Predicted Dynamics-First Tool Response

| Tool Family | Expected Jump | Why |
|------------|--------------|-----|
| Neural Oscillations | Traps 16-18 | Phase relationship tracking maps to temporal ordering |
| Statistical Mechanics | Traps 19-22 | Ensemble averaging maps to probabilistic reasoning |
| Ergodic Theory | Traps 19, 21 | Time-averaging vs space-averaging distinction |

---

## Expansion Phase 2: Causal + Linguistic (Categories 23-32)

*Goal: Differentiate the middle tier — FEP vs Mechanism Design vs Falsificationism.*

### Tier A (Parsing)

**23. Correlation ≠ causation**
"Cities with more hospitals have more crime. Do hospitals cause crime?"
candidates: ["Yes", "No, correlation is not causation", "Possibly"] correct: "No, correlation is not causation"
Parametric: Yes (vary correlated variables)
Self-contained: Yes

**24. Simpson's paradox**
"Treatment A cures 80% of mild cases and 50% of severe cases. Treatment B cures 70% of mild cases and 40% of severe cases. A seems better. But if 90% of A's patients were mild and 90% of B's were severe, which treatment has a higher overall cure rate?"
candidates: ["Treatment A", "Treatment B"] correct: "Treatment B"
Parametric: Yes (vary rates and group sizes)
Self-contained: Yes
*SOC tools should excel: different behavior at local vs global scale*

**25. Post hoc ergo propter hoc**
"I wore my lucky socks and won the game. Did the socks cause the win?"
candidates: ["Yes", "No, coincidence after does not imply causation"] correct: "No, coincidence after does not imply causation"
Parametric: Yes (vary superstitions)
Self-contained: Yes

**26. Confounding variables**
"Students who eat breakfast score higher on tests. Does eating breakfast improve test scores?"
candidates: ["Yes", "Not necessarily — a confounding variable may explain both"] correct: "Not necessarily — a confounding variable may explain both"
Parametric: Yes
Self-contained: Yes
*Immune System tools should detect: foreign variable in the reasoning context*

### Tier B (Judgment — ambiguity/insufficiency)

**27. Scope ambiguity**
"Every student passed a test. Did all students pass the same test?"
candidates: ["Yes", "Not necessarily — the sentence is ambiguous"] correct: "Not necessarily — the sentence is ambiguous"
Parametric: Partially
Self-contained: Yes

**28. Presupposition failure**
"Have you stopped making errors in your reasoning? Answer yes or no."
candidates: ["Yes", "No", "The question contains a false presupposition"] correct: "The question contains a false presupposition"
Parametric: Yes (vary presupposed actions)
Self-contained: Yes
*Immune tools: self/non-self — the presupposition is a "foreign" assumption*

**29. Garden path reparse**
"The complex houses married and single soldiers and their families. What does 'complex' mean here?"
candidates: ["Complicated", "A group of buildings"] correct: "A group of buildings"
Parametric: Limited (garden paths are hard to generate)
Self-contained: Yes

**30. Pronoun reference resolution**
"John told Bill that he was wrong. Who was wrong?"
candidates: ["John", "Bill", "Ambiguous — 'he' could refer to either"] correct: "Ambiguous — 'he' could refer to either"
Parametric: Yes (vary names, pronouns)
Self-contained: Yes

**31. Percentage change asymmetry**
"A stock rises 50% then falls 50%. What is the net change?"
candidates: ["No change (back to original)", "Down 25%"] correct: "Down 25%"
Parametric: Yes (vary percentages)
Self-contained: Yes
*Note: 100 × 1.5 × 0.5 = 75, so -25%*

**32. Unit conversion chain**
"How many seconds are in 2.5 hours?"
candidates: ["9000", "15000", "2500"] correct: "9000"
Parametric: Yes (vary units, quantities)
Self-contained: Yes
*Note: 2.5 × 60 × 60 = 9000*

### Predicted Tool Response

| Tool Family | Expected Jump | Why |
|------------|--------------|-----|
| SOC | Traps 24, 31, 43 | Scale-dependent behavior is SOC's domain |
| Immune Systems | Traps 26, 28, 41 | Self/non-self: detecting foreign elements in reasoning |
| Falsificationism | Traps 23, 25 | Testing causal claims against counterexamples |

---

## Expansion Phase 3: Meta-Reasoning (Categories 33-42)

*Goal: Calibrate the RLVF signal. Highest-value category for the actual use case.*

### Tier B (Judgment — meta-level)

**33. Answerability classification (Level 1: computable)**
"What is the sum of 347 and 528?"
candidates: ["875", "865", "Cannot be computed"] correct: "875"
Parametric: Yes
Self-contained: Yes

**34. Answerability classification (Level 2: knowledge-required)**
"Is the speed of light faster than the speed of sound?"
candidates: ["Yes", "No", "Cannot be determined without more information"] correct: "Yes"
Parametric: Limited
Self-contained: No (requires world knowledge)

**35. Answerability classification (Level 3: genuinely unanswerable)**
"Is the universe finite or infinite?"
candidates: ["Finite", "Infinite", "Currently unknown — no definitive answer exists"] correct: "Currently unknown — no definitive answer exists"
Parametric: Limited
Self-contained: No

**36. Argument strength evaluation**
"Argument 1: All mammals are warm-blooded. Dogs are mammals. Therefore dogs are warm-blooded. Argument 2: Most mammals are warm-blooded. Dogs are probably mammals. Therefore dogs are probably warm-blooded. Which argument is logically stronger?"
candidates: ["Argument 1", "Argument 2", "They're equal"] correct: "Argument 1"
Parametric: Yes (vary premises and conclusions)
Self-contained: Yes
*This is the highest-value category for RLVF: scoring reasoning traces, not answers.*

**37. Fallacy identification**
"Everyone I know who exercises is healthy. Therefore exercise causes health. What type of reasoning error is this?"
candidates: ["No error", "Correlation assumed as causation", "Hasty generalization", "Both B and C"] correct: "Both B and C"
Parametric: Yes (vary fallacies)
Self-contained: Yes

**38. Confidence calibration**
"You are told: 'It will probably rain tomorrow.' How confident should you be that it will rain?"
candidates: ["Very confident (>90%)", "Moderately confident (50-70%)", "Not very confident (<30%)"] correct: "Moderately confident (50-70%)"
Parametric: Yes (vary hedging words)
Self-contained: Yes

**39. Recursive self-reference**
"Alice says Bob is lying. Bob says Carol is lying. Carol says Alice is telling the truth. If exactly one person is telling the truth, who is it?"
candidates: ["Alice", "Bob", "Carol", "None"] correct: "Bob"
Parametric: Yes (vary number of people, truth assignments)
Self-contained: Yes
*Note: If Bob tells truth → Carol lies → Alice lies → Bob lies (contradiction). Work through each.*

**40. Distinguishing validity from truth**
"All fish can fly. Salmon is a fish. Therefore salmon can fly. Is this argument valid?"
candidates: ["No, because fish can't fly", "Yes, the conclusion follows from the premises"] correct: "Yes, the conclusion follows from the premises"
Parametric: Yes (vary false premises with valid structure)
Self-contained: Yes

**41. Red herring detection**
"A train leaves Station A at 60 mph. A bird is sitting on the platform. Another train leaves Station B at 80 mph toward Station A. The stations are 280 miles apart. When do the trains meet?"
candidates: ["2 hours", "3 hours", "Cannot determine because of the bird"] correct: "2 hours"
Parametric: Yes (vary irrelevant details)
Self-contained: Yes
*Note: 280 / (60+80) = 2 hours. The bird is irrelevant.*

**42. Necessary vs sufficient conditions**
"All squares are rectangles. Is being a rectangle sufficient to be a square?"
candidates: ["Yes", "No — it is necessary but not sufficient"] correct: "No — it is necessary but not sufficient"
Parametric: Yes (vary category relationships)
Self-contained: Yes

---

## Expansion Phase 4: Remaining Categories (43-60+)

### Tier A (Parsing)

**43. Framing effect detection**
"A medical procedure has a 90% survival rate. The same procedure has a 10% mortality rate. Are these equivalent?"
candidates: ["No, survival rate is better", "Yes, they describe the same outcome"] correct: "Yes, they describe the same outcome"
Parametric: Yes

**44. Semantic trap (lateral thinking)**
"How many months have 28 days?"
candidates: ["1 (February)", "All 12 months"] correct: "All 12 months"
Parametric: Limited

**45. Category error detection**
"What does the number 7 smell like?"
candidates: ["Sweet", "Numbers don't have smells — this is a category error", "Metallic"] correct: "Numbers don't have smells — this is a category error"
Parametric: Yes (vary nonsensical questions)

**46. Proportional analogy**
"Hand is to glove as foot is to ___"
candidates: ["Shoe", "Sock", "Leg"] correct: "Shoe"
Parametric: Yes (vary analogy pairs)
Self-contained: No (requires world knowledge)
*Analogical Reasoning tools' home trap*

**47. Double negation resolution**
"It is not the case that the statement 'it will not rain' is false. Will it rain?"
candidates: ["Yes", "No"] correct: "No"
Parametric: Yes (vary depth of negation)
Self-contained: Yes

**48. Exclusive vs inclusive OR**
"You can have soup or salad. Can you have both?"
candidates: ["No", "Ambiguous — depends on whether 'or' is exclusive"] correct: "Ambiguous — depends on whether 'or' is exclusive"
Parametric: Yes

**49. Vacuous truth**
"All unicorns can fly. Is this statement true?"
candidates: ["No, unicorns don't exist", "Yes, it is vacuously true"] correct: "Yes, it is vacuously true"
Parametric: Yes (vary nonexistent subjects)
Self-contained: Yes

**50. Sunk cost fallacy**
"You've spent $500 on concert tickets but you're sick on the day of the concert. Should you go because you already paid?"
candidates: ["Yes, to get your money's worth", "The $500 is a sunk cost and shouldn't affect the decision"] correct: "The $500 is a sunk cost and shouldn't affect the decision"
Parametric: Yes

**51. Survivor bias**
"All successful entrepreneurs dropped out of college. Should you drop out to be successful?"
candidates: ["Yes", "No — this ignores the many dropouts who failed"] correct: "No — this ignores the many dropouts who failed"
Parametric: Yes

**52. Regression to the mean**
"A student scores 98% on one test, then 85% on the next. Did they get worse?"
candidates: ["Yes", "Not necessarily — extreme scores tend to regress toward the average"] correct: "Not necessarily — extreme scores tend to regress toward the average"
Parametric: Yes (vary scores)

**53. Monty Hall problem**
"You pick door 1. Host opens door 3 (goat). Should you switch to door 2?"
candidates: ["It doesn't matter", "Yes, switching gives 2/3 chance"] correct: "Yes, switching gives 2/3 chance"
Parametric: Limited (fixed structure)
Self-contained: Yes

**54. Ecological fallacy**
"Countries with higher average income have lower crime. Does this mean rich individuals commit fewer crimes?"
candidates: ["Yes", "Not necessarily — group-level patterns don't apply to individuals"] correct: "Not necessarily — group-level patterns don't apply to individuals"
Parametric: Yes

**55. Affirming the consequent**
"If it rains, the ground is wet. The ground is wet. Did it rain?"
candidates: ["Yes", "Not necessarily — something else could have made the ground wet"] correct: "Not necessarily — something else could have made the ground wet"
Parametric: Yes (vary conditionals)
Self-contained: Yes
*Note: differs from modus tollens — this is the INVALID direction*

**56. Anchoring bias resistance**
"The population of Uruguay is more or less than 200 million. Estimate the actual population."
candidates: ["About 150 million", "About 3.5 million", "About 50 million"] correct: "About 3.5 million"
Parametric: Limited
Self-contained: No (requires world knowledge)

**57. Composition fallacy**
"Every part of the machine is light. Is the whole machine light?"
candidates: ["Yes", "Not necessarily — many light parts can make a heavy whole"] correct: "Not necessarily — many light parts can make a heavy whole"
Parametric: Yes

**58. Division fallacy**
"The team has a high average score. Does every member score high?"
candidates: ["Yes", "Not necessarily — averages can be skewed by outliers"] correct: "Not necessarily — averages can be skewed by outliers"
Parametric: Yes

**59. False dichotomy detection**
"You're either with us or against us. Are there other options?"
candidates: ["No, those are the only options", "Yes, this is a false dichotomy"] correct: "Yes, this is a false dichotomy"
Parametric: Yes

**60. Bayesian updating with new evidence**
"A bag has 3 red and 7 blue balls. You draw one ball and it's red. What's the probability the next ball is red?"
candidates: ["3/10", "2/9", "3/9"] correct: "2/9"
Parametric: Yes (vary counts)
Self-contained: Yes
*Note: after removing one red, 2 red remain out of 9 total*

---

## Build Order (Athena's Recommendation)

| Phase | Categories | Count | Goal | Coeus Rebuild After |
|-------|-----------|-------|------|-------------------|
| **1** | Temporal (16-18) + Probabilistic (19-22) | 7 | Do dynamics-first tools wake up? | Yes |
| **2** | Causal (23-26) + Linguistic (27-32) | 10 | Differentiate middle tier | Yes |
| **3** | Meta-reasoning (33-42) | 10 | Calibrate RLVF signal | Yes |
| **4** | Remaining (43-60) | 18 | Fill coverage gaps | Yes |

Each phase adds categories, triggers a Coeus rebuild, and tests the prediction that dynamics-first tools improve on their home turf.

---

## Implementation Notes

### Parametric Generation
Each category needs a generator function in `trap_generator.py` that produces infinite variants with different numbers, names, and surface features. The correct answer must be computable from the parameters alone.

### Tier Tagging
Each trap carries a `tier: "A"` or `tier: "B"` tag. Coeus tracks accuracy separately per tier. The RLVF fitness function can weight Tier B tools differently (judgment accuracy is harder-won and more valuable).

### Adversarial Paraphrasing
For each category, generate at least 2 surface variants that test the same reasoning with completely different framing. This prevents dispatcher-style tools from pattern-matching category keywords.

### Fallback Rate Tracking
New metric: for each tool, what percentage of the expanded battery triggers an actual parser vs falling through to NCD fallback? A tool with 30% parser coverage but well-calibrated fallback (low confidence on unrecognized patterns) is more valuable for RLVF than one with 80% parser coverage and overconfident fallback.

### World Knowledge Constraint
Categories marked "Self-contained: No" should be used cautiously — they test knowledge, not reasoning structure. Keep them in the battery but flag them separately. A tool that fails on "speed of light > speed of sound" might still be an excellent reasoning evaluator.

---

## Research Survey Results: 90 Additional Categories

A deep research survey identified 90 additional categories across 14 domains, bringing the total taxonomy to **105 reasoning categories**. 94% are parametrically generatable, 97% are self-contained (no world knowledge required).

### Domain Summary

| Domain | New Categories | Parametric | Self-Contained |
|--------|---------------|------------|----------------|
| A: Formal Logic | 13 (affirming consequent, denying antecedent, undistributed middle, illicit major, existential fallacy, exclusive disjunction, biconditional, contrapositive vs inverse, quaternio terminorum, double negation, De Morgan, vacuous truth, material conditional) | 12/13 | 13/13 |
| B: Probabilistic/Statistical | 11 (base rate neglect, conjunction fallacy, disjunction fallacy, regression to mean, sample size neglect, prosecutor's fallacy, Monty Hall, independence confusion, conditional probability reversal, expected value, survivorship bias) | 11/11 | 11/11 |
| C: Arithmetic/Math | 10 (order of operations, modular arithmetic, fencepost, percentage change, distribution over operators, zero handling, negative numbers, set membership vs subset, inclusion-exclusion, infinite series) | 9/10 | 10/10 |
| D: Temporal | 5 (temporal ordering, duration calculation, relative time reference, rate-time-distance, calendar arithmetic) | 5/5 | 5/5 |
| E: Linguistic/Semantic | 9 (scope ambiguity, presupposition, referential ambiguity, comparative vs superlative, collective vs distributive, garden path, intensional vs extensional, pragmatic implicature, numeral-word mismatch) | 8/9 | 9/9 |
| F: Causal/Counterfactual | 6 (post hoc, correlation≠causation, necessary vs sufficient, counterfactual evaluation, Simpson's paradox, causal chain) | 6/6 | 6/6 |
| G: Set Theory/Quantifier | 5 (empty set, subset inversion, universal vs existential, intersection vs union, power set cardinality) | 5/5 | 5/5 |
| H: Spatial/Relational | 5 (left-right reversal, direction composition, relative position, containment, triangle inequality) | 5/5 | 5/5 |
| I: Meta-Reasoning | 5 (confidence calibration, validity vs soundness, is-ought gap, epistemic closure, self-referential consistency) | 5/5 | 5/5 |
| J: Common Sense | 4 (unit conversion, part-whole, composition fallacy, false dichotomy) | 4/4 | 4/4 |
| K: Multi-Step Chain | 5 (multi-hop deduction, information sufficiency, irrelevant premise, premise contradiction, chained conditional) | 5/5 | 5/5 |
| L: Uncertainty | 4 (closed world assumption, default reasoning override, ambiguity tolerance, absence of evidence) | 3/4 | 3/4 |
| M: Social/Theory of Mind | 4 (false belief task, knowledge attribution, second-order belief, intention vs outcome) | 4/4 | 4/4 |
| N: Analogical/Abstract | 4 (false analogy, pattern extrapolation trap, category boundary, hasty generalization) | 3/4 | 3/4 |
| **TOTAL NEW** | **90** | **85/90** | **87/90** |

### Revised Build Order (4 Phases + Research Categories)

| Phase | Categories | Count | Goal |
|-------|-----------|-------|------|
| **1** | Temporal (D) + Probabilistic Tier 1 (base rate, conjunction, independence) | 12 | Wake up dynamics-first tools |
| **2** | Causal (F) + Linguistic (E) + Formal Logic Tier 1 (affirming consequent, denying antecedent, De Morgan, double negation, vacuous truth) | 20 | Differentiate middle tier |
| **3** | Meta-Reasoning (I) + Theory of Mind (M) + Multi-Step Chain (K) | 14 | Calibrate RLVF signal |
| **4** | Arithmetic (C) + Spatial (H) + Set Theory (G) + remaining | 44 | Full coverage |

### Key Implementation Notes from Research

1. All generators follow existing signature: `def _category_name(rng: random.Random) -> dict` returning `{"prompt", "candidates", "correct", "category"}`
2. Existing Nemesis metamorphic relations (comparison_flip, negation_inject, premise_shuffle, distractor_add) compose with all new categories: **105 base categories × 12 MRs × parametric variation = effectively unbounded test space**
3. Deterministic grading is possible for all Tier 1 and 2 categories — correct answers computed from generation parameters
4. Probabilistic categories (base rate, prosecutor's fallacy, expected value) need numeric answers as multiple-choice options to keep evaluation deterministic

### Full Category List: `docs/trap_battery_expansion.md` + `forge_v3/all_scores.json`

See the research output at the task transcript for complete category specifications with example prompts, candidates, and correct answers for all 90 new categories.
