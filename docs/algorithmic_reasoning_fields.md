# Algorithmic Reasoning — Theoretical Foundations

*Fields of mathematics and computer science that formalize what it means to reason algorithmically, and how they connect to Prometheus's exploration architecture.*

*Source: DeepSeek consultation (2026-03-27) + Athena synthesis*

---

## The Core Question

Can a system discover that certain problem classes require fundamentally new approaches, and then invent those approaches? This is the central challenge of Prometheus's exploration velocity concept — not just solving problems, but getting better at getting better at solving them.

Seven fields formalize different aspects of this question.

---

## 1. Circuit Complexity

**What it studies:** What can and can't be computed by bounded-depth circuits with various gate types.

**Why it matters for Prometheus:** Transformers ARE bounded-depth computation graphs. The TC⁰ and AC⁰ hierarchy results tell you which problems are solvable by constant-depth circuits. The ejection mechanism is, formally, a question about whether the required computation fits within the circuit class the architecture implements.

**Key connection:** The attractor basin framework (Ignis) is empirically probing what circuit complexity studies theoretically — can the model "precipitate" into a reasoning trajectory, or is the computation too deep for the circuit?

**Key results:**
- TC⁰ (constant depth, threshold gates) captures exactly what transformers can compute in a single forward pass
- Problems requiring TC¹ or higher are fundamentally out of reach without chain-of-thought (which adds depth)
- Merrill & Sabharwal's work on transformer expressivity leans on this directly

**Open question for Prometheus:** The ejection mechanism suppresses correct answers that the model CAN compute (they appear at intermediate layers). Is the ejection a circuit-level phenomenon — the late layers implementing a different circuit class than the early layers?

**Research targets:**
- Merrill & Sabharwal (2023): "The Parallelism Tradeoff: Limitations of Log-Precision Transformers"
- Hahn (2020): "Theoretical Limitations of Self-Attention in Neural Sequence Models"
- Strobl et al. (2024): "What Can Transformers Learn In-Context?"

---

## 2. Proof Complexity

**What it studies:** Given a proof system, how long must proofs be? The formal study of proof length, proof compression, and the existence of short proofs.

**Why it matters for Prometheus:** Some reasoning tasks require genuine compositional steps that can't be shortcut. The distinction between extended Frege and bounded-depth Frege systems mirrors the gap between models that chain reasoning and those that pattern-match.

**Key connection:** The "bypass vs precipitation" finding from Ignis. Bypass vectors find shortcuts that don't generalize. Precipitation requires the model to actually execute the proof steps. Proof complexity tells you when shortcuts MUST exist (short proofs) and when they CAN'T (proof length lower bounds).

**Key results:**
- Resolution proof systems have exponential lower bounds for pigeonhole principle — no short proof exists
- Extended Frege can have polynomially short proofs for statements that require exponential proofs in bounded-depth Frege
- This hierarchy maps onto: pattern matching (bounded depth) vs genuine reasoning (extended)

**Open question for Prometheus:** When the model ejects a correct answer, is it because the proof of correctness requires more depth than the remaining layers can provide? Is L* (the ejection layer) the point where the proof complexity exceeds the circuit's remaining depth?

**Research targets:**
- Krajíček (2019): "Proof Complexity"
- Cook & Reckhow (1979): foundational — proof systems and their relative power
- Razborov (2015): "Proof Complexity and Beyond"

---

## 3. Algorithmic Information Theory (AIT)

**What it studies:** Kolmogorov complexity, Solomonoff induction, the relationship between compression and prediction.

**Why it matters for Prometheus:** The bypass circuit finding is, formally, the model preferring low-Kolmogorov-complexity solutions. The "gravitational pull" toward heuristic mimicry is a compression prior dominating over algorithmic depth. The ejection mechanism preferentially keeps the most compressible answer, not the most correct one.

**Key connection:** NCD (Normalized Compression Distance) is already the quality floor for forge tools. But AIT goes deeper — it formalizes WHY compression is seductive (Solomonoff's prior weights simpler hypotheses exponentially higher) and when it misleads (when the true answer is algorithmically complex).

**Key results:**
- Kolmogorov complexity is uncomputable — you can't exactly measure algorithmic content
- But approximations (zlib, BPE token counts, description length) are practically useful
- Solomonoff induction is the theoretical ideal for prediction — but it's biased toward simple hypotheses
- The "compression as progress" heuristic from DeepSeek's analysis connects here: if a combination of techniques simplifies a problem representation, that's evidence of progress

**Open question for Prometheus:** Can we measure the Kolmogorov complexity of the ejection mechanism itself? If the suppression circuit is "simple" (low KC), it should be easy to break. If it's "complex" (high KC), it's deeply entangled with the model's other computations. The fact that 0.36% of parameters breaks it at 135M but not at 1.5B suggests the circuit's KC increases with scale.

**Research targets:**
- Li & Vitányi (2019): "An Introduction to Kolmogorov Complexity and Its Applications" (4th ed)
- Hutter (2005): "Universal Artificial Intelligence" — AIXI, the theoretical ideal
- Grünwald (2007): "The Minimum Description Length Principle" — practical applications

---

## 4. Descriptive Complexity

**What it studies:** The correspondence between computational complexity classes and logical expressibility. What can be described in which logic corresponds to what can be computed in which time.

**Why it matters for Prometheus:** The Immerman-Vardi theorem shows P = FO(LFP) — polynomial-time computation corresponds exactly to first-order logic plus least fixed-point over ordered structures. This gives a LOGICAL characterization of "reasoning" — and raises the question of which logical fragments the transformer's residual stream can express.

**Key connection:** The forge tools are deterministic reasoning evaluators — they check logical properties of candidate answers. Each forge tool is essentially a logical sentence: "this answer satisfies these constraints." The question is whether the set of all forge tools covers a complete logical fragment, or leaves gaps. Descriptive complexity tells you what a "complete" set of reasoning criteria would look like.

**Key results:**
- P = FO(LFP): polynomial-time = first-order logic + least fixed-point
- NP = existential second-order logic (Fagin's theorem)
- NL = FO(TC): nondeterministic logspace = first-order + transitive closure
- Each complexity class has a logical characterization — so "what can this model reason about" has a precise formal answer

**Open question for Prometheus:** The 105 Sphinx categories cover 14 domains of reasoning failure. Can we map each category to a logical fragment? If category X requires second-order logic to detect and our forge tools only implement first-order checks, we have a systematic gap. Descriptive complexity tells us exactly which gaps are fundamental vs fixable.

**Research targets:**
- Immerman (1999): "Descriptive Complexity"
- Grädel et al. (2007): "Finite Model Theory and Its Applications"
- Libkin (2004): "Elements of Finite Model Theory"

---

## 5. Category Theory (Applied/Compositional)

**What it studies:** How complex computations build from primitive operations via composition. Functors, natural transformations, and the algebra of composition.

**Why it matters for Prometheus:** The frame-shifting concept — where different reasoning modes require different compositional structures — has a natural categorical interpretation. Poros's chain composition is category theory in action: each organism is an object, each operation is a morphism, and type-compatible chaining is functor composition.

**Key connection:** Already partially implemented. The `compatible_chains()` method in the organism base class is computing the morphisms between objects. The composition engine is building the category of reasoning operations. What's missing is the categorical STRUCTURE — which compositions are natural (structure-preserving) vs artificial (type-compatible but semantically meaningless).

**Key results:**
- Functors preserve composition: F(g ∘ f) = F(g) ∘ F(f) — if a reasoning chain works, its image in another domain should also work
- Natural transformations = systematic ways to translate between functorial views
- Monoidal categories formalize parallel composition (doing two things at once)
- The Yoneda lemma: every object is determined by its relationships — a concept IS its interfaces

**Open question for Prometheus:** The Yoneda lemma says a concept is completely determined by its morphisms (interfaces) to all other concepts. Our Lattice is building exactly this — mapping every concept's interfaces. When the Lattice is "complete" in the Yoneda sense, we have a complete characterization of every concept. How close are we? Which concepts have the most unmapped morphisms?

**Research targets:**
- Fong & Spivak (2019): "An Invitation to Applied Category Theory: Seven Sketches in Compositionality"
- Riehl (2016): "Category Theory in Context"
- Coecke & Kissinger (2017): "Picturing Quantum Processes" — diagrammatic reasoning

---

## 6. Homotopy Type Theory (HoTT)

**What it studies:** Unifies topology, logic, and computation. Paths in a space correspond to proofs of equality. The shape of a proof IS a mathematical object.

**Why it matters for Prometheus:** If reasoning trajectories in activation space have topological structure (which RPH proposes), HoTT provides a framework where the shape of the reasoning path is a first-class object. A proof of correctness isn't just "the answer is right" — it's a specific PATH through the reasoning space, and different paths have different topological properties.

**Key connection:** The logit lens backward pass traces a path through the model's layers. That path has topological structure — monotonically increasing probability (healthy) vs spike-and-collapse (ejection). HoTT would formalize these as homotopically distinct: a monotonic path and a spike-collapse path are NOT deformable into each other. They represent fundamentally different reasoning processes.

**Key results:**
- Univalence axiom: equivalent types are equal — if two reasoning processes produce the same result via the same structure, they're the same process
- Higher inductive types: define mathematical objects by their paths, not just their points
- The connection to constructive mathematics: every proof is a program, every program is a proof

**Open question for Prometheus:** Can we classify ejection trajectories homotopically? If ejection paths and precipitation paths are in different homotopy classes, that's a topological proof that they represent different computational mechanisms. Currently we detect this empirically (monotonicity score). HoTT would give us a formal classification.

**Research targets:**
- Univalent Foundations Program (2013): "Homotopy Type Theory: Univalent Foundations of Mathematics" (free book)
- Shulman (2018): "Homotopy Type Theory: A synthetic approach to higher equalities"
- Rijke (2022): "Introduction to Homotopy Type Theory" (textbook)

---

## 7. Computational Learning Theory

**What it studies:** What can be learned algorithmically from data. PAC learning, statistical query models, sample complexity.

**Why it matters for Prometheus:** Whether reasoning can be induced from training versus requiring architectural priors. The ejection mechanism might be an inherent limitation of learning from internet text — the training distribution doesn't contain enough examples of genuine reasoning to overcome the compression prior toward heuristic mimicry.

**Key connection:** The corpus-first hypothesis (fine-tune on reasoning data before evolving) is a learning-theoretic claim: the training distribution determines what the model can learn. If the internet distribution has too many confident wrong answers and too few genuine proofs, no amount of RLHF can fix it — you need to change the distribution.

**Key results:**
- PAC learning: some concepts are efficiently learnable, others require exponential samples
- Statistical query model: limits what can be learned from aggregate statistics vs individual examples
- No-free-lunch theorems: no learner is universally best — biases are necessary
- Curriculum learning: the ORDER in which examples are presented affects what's learnable

**Open question for Prometheus:** Is "reasoning" PAC-learnable from text? If not, what additional structure (formal proofs, Lean 4 verification, self-correction loops) is needed? The ejection mechanism suggests that reasoning is NOT efficiently learnable from internet text alone — the suppressor emerges as the default because heuristic mimicry is the easier concept to learn.

**Research targets:**
- Shalev-Shwartz & Ben-David (2014): "Understanding Machine Learning: From Theory to Algorithms"
- Valiant (1984): "A Theory of the Learnable" — the PAC framework
- Vapnik (1998): "Statistical Learning Theory"

---

## The Intersection DeepSeek Flagged as Most Underexplored

**Circuit complexity × topology** — understanding not just what a bounded-depth circuit can compute, but what the GEOMETRY of its solution space looks like, and how perturbations navigate that geometry.

This is exactly what RPH (Reasoning Precipitation Hypothesis) probes empirically. The formal theory barely exists yet. Prometheus might be building toward it from the empirical side.

**What an organism for this intersection would look like:**

```python
CIRCUIT_TOPOLOGY = MathematicalOrganism(
    name="circuit_topology",
    operations={
        "circuit_depth_bound": ...,        # What's computable at depth d?
        "solution_space_betti": ...,       # Topological invariants of the solution space
        "perturbation_path_class": ...,    # Homotopy class of steering vector trajectories
        "depth_topology_tradeoff": ...,    # How topology constrains circuit depth requirements
    }
)
```

This organism doesn't exist in any library. It would need to be built from first principles. It IS the frontier.

---

## Challenges for Prometheus

### Challenge 1: The Direction-of-Solution Problem

How do you measure proximity to an answer you don't have? Three proxy signals (from DeepSeek):

1. **Constraint satisfaction as partial progress** — count how many constraints of the target problem a candidate approach satisfies. More constraints satisfied = closer to solution. Measurable without knowing the answer.

2. **Compression as heuristic** — if applying a technique simplifies the problem representation (lower description length), that's progress. We already have `zlib.compress` from NCD.

3. **Transferability as evidence of depth** — if a technique combination that partially solves problem A also helps with problem B, it's capturing genuine structure, not overfitting. Cross-problem transfer as fitness bonus.

### Challenge 2: The Representation Problem

How do you encode "a combination of mathematical techniques" in a form that's evolvable?

**Our current answer:** Typed operators with compositional signatures (the organism operations with input/output types). Poros already does this. But we need the GEOMETRIC embedding too — techniques that solve similar problem classes should cluster together, and interesting combinations bridge distant clusters.

**The hybrid approach DeepSeek recommends:** Types for structure, geometry for search guidance. We have the types (organism type system). We need the geometry (embed each operation as a vector, cluster by applicability).

### Challenge 3: The Escalation Mechanism

When the system hits a problem it can't solve with any known combination, what happens?

Three responses (from DeepSeek):
1. **Analogy formation** — notice structural similarity to a solved problem, transport the technique
2. **Abstraction lifting** — abstract from specific techniques to meta-techniques ("decompose into subproblems")
3. **Primitive invention** — create a genuinely new technique not in the library (this is theorem discovery)

### Challenge 4: The Convergence Question

Does evolutionary search over technique combinations converge to anything, or does it just churn? The geometric embedding is the hedge — it provides inductive bias. But the quality of that embedding is doing a lot of work.

**Our specific risk:** Poros found 291 "successful" chains in 6 seconds, but many were overflow garbage (tent map producing infinity). The scoring function needs to distinguish "executed without crashing" from "produced useful structure." The first run showed the engine works; the next iteration needs the fitness function to be meaningful.

### Challenge 5: The Failure Geometry

When a chain fails, HOW it fails carries information:
- Type error at step 2 → the interface between organisms A and B doesn't exist in practice
- Overflow at step 3 → the combination amplifies rather than controls
- Convergence failure → the iterative algorithm doesn't terminate on this input
- NaN propagation → numerical instability at the boundary between domains

**This IS the waste stream.** The failure trajectories contain the structure of what's missing. Arcanum should classify failure modes the same way it classifies waste stream specimens.

---

## Research Reading List (Prioritized for Prometheus)

### Immediate (connects to current Ignis/Rhea work)
1. Merrill & Sabharwal — transformer expressivity and circuit complexity
2. Li & Vitányi — Kolmogorov complexity (grounds the NCD/compression approach)
3. Fong & Spivak — applied category theory (formalizes the composition engine)

### Medium-term (connects to Poros/Apollo)
4. Ellis et al. (DreamCoder) — library learning from program primitives
5. Grünwald — minimum description length (the compression-as-progress heuristic)
6. Shalev-Shwartz & Ben-David — learning theory (is reasoning PAC-learnable?)

### Frontier (the unexplored intersection)
7. Homotopy Type Theory book — paths as proofs, topology as logic
8. Immerman — descriptive complexity (what logic corresponds to what computation)
9. Razborov — proof complexity (when must proofs be long?)

### Speculative (the North Star)
10. Hutter — AIXI and universal AI (the theoretical ideal Prometheus approximates)
