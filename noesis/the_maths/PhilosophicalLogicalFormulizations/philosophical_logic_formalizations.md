# Mathematical Formalizations of Philosophical Logic Systems
## Reference for Noesis Concept Composition

---

## 1. Aristotelian Syllogistic Logic

The first formal reasoning system. Operates over **categorical propositions** with four forms:

| Form | Name | Structure | Set-Theoretic |
|------|------|-----------|---------------|
| A | Universal Affirmative | All S are P | S ⊆ P |
| E | Universal Negative | No S are P | S ∩ P = ∅ |
| I | Particular Affirmative | Some S are P | S ∩ P ≠ ∅ |
| O | Particular Negative | Some S are not P | S ⊄ P (equivalently S \ P ≠ ∅) |

**Valid syllogistic forms (figures)** are derivable as set-theoretic theorems. Example — Barbara (AAA-1):

```
Premise 1:  M ⊆ P       (All M are P)
Premise 2:  S ⊆ M       (All S are M)
Conclusion: S ⊆ P       (All S are P)
Proof:      Transitivity of ⊆
```

The **square of opposition** defines logical relations between A, E, I, O for fixed S, P:

```
        A ←— contraries ——→ E
        |                    |
   subalterns            subalterns
        |                    |
        I ←— subcontraries → O

A ↔ ¬O  (contradictories)
E ↔ ¬I  (contradictories)
A → I   (subalternation, requires existential import: S ≠ ∅)
E → O   (subalternation, requires existential import: S ≠ ∅)
```

**Key for Noesis**: This is a *fragment* of first-order logic restricted to monadic predicates with exactly two quantifier patterns. The restriction is what makes it decidable. The trade-off between expressiveness and decidability is itself a composable concept.

---

## 2. Boolean Algebra / Propositional Logic

**Algebraic structure**: ⟨B, ∧, ∨, ¬, 0, 1⟩ where B = {0, 1}

**Axioms** (Huntington, 1904):

```
Commutativity:   a ∧ b = b ∧ a           a ∨ b = b ∨ a
Associativity:   a ∧ (b ∧ c) = (a ∧ b) ∧ c
Distributivity:  a ∧ (b ∨ c) = (a ∧ b) ∨ (a ∧ c)
                 a ∨ (b ∧ c) = (a ∨ b) ∧ (a ∨ c)
Identity:        a ∧ 1 = a               a ∨ 0 = a
Complement:      a ∧ ¬a = 0              a ∨ ¬a = 1
```

**De Morgan's Laws** (derived):
```
¬(a ∧ b) = ¬a ∨ ¬b
¬(a ∨ b) = ¬a ∧ ¬b
```

**Functional completeness**: {¬, ∧} is functionally complete (can express all Boolean functions). So is {NAND} alone, and {NOR} alone. This means:

```
NAND(a,b) = ¬(a ∧ b)
¬a = NAND(a,a)
a ∧ b = NAND(NAND(a,b), NAND(a,b))
a ∨ b = NAND(NAND(a,a), NAND(b,b))
```

**Satisfiability** (SAT): Given formula φ in propositional logic, does there exist an assignment σ: Vars → {0,1} such that σ(φ) = 1? This is NP-complete (Cook-Levin theorem, 1971).

**Key for Noesis**: Boolean algebra is isomorphic to the powerset algebra ⟨P(U), ∩, ∪, complement, ∅, U⟩. It's also isomorphic to certain lattice structures. These cross-domain isomorphisms are exactly the kind of structural bridges Noesis should be finding.

---

## 3. First-Order Predicate Logic (Frege-Russell)

**Syntax**:
```
Terms:      t ::= x | c | f(t₁, ..., tₙ)
Formulas:   φ ::= P(t₁, ..., tₙ) | ¬φ | φ ∧ ψ | φ ∨ ψ | φ → ψ | ∀x.φ | ∃x.φ
```

**Semantics** (Tarski): A **model** M = ⟨D, I⟩ where D is a non-empty domain and I is an interpretation function:
```
I(c) ∈ D                          (constants map to domain elements)
I(f): Dⁿ → D                      (function symbols map to functions)
I(P) ⊆ Dⁿ                         (predicate symbols map to relations)
```

**Satisfaction** (M, σ ⊨ φ) where σ is a variable assignment:
```
M, σ ⊨ P(t₁,...,tₙ)   iff  ⟨⟦t₁⟧, ..., ⟦tₙ⟧⟩ ∈ I(P)
M, σ ⊨ ¬φ              iff  M, σ ⊭ φ
M, σ ⊨ φ ∧ ψ           iff  M, σ ⊨ φ and M, σ ⊨ ψ
M, σ ⊨ ∀x.φ            iff  for all d ∈ D: M, σ[x↦d] ⊨ φ
M, σ ⊨ ∃x.φ            iff  there exists d ∈ D: M, σ[x↦d] ⊨ φ
```

**Key metatheorems**:
- **Completeness** (Gödel, 1929): If Γ ⊨ φ then Γ ⊢ φ (semantic entailment implies syntactic derivability)
- **Compactness**: If every finite subset of Γ has a model, then Γ has a model
- **Löwenheim-Skolem**: If a first-order theory has an infinite model, it has models of every infinite cardinality

**Undecidability**: The set of valid first-order sentences is recursively enumerable but not decidable (Church-Turing, 1936).

**Key for Noesis**: The gap between completeness (provability = truth) and undecidability (no algorithm to determine provability) is a fundamental structural tension. This same tension appears in optimization (finding vs. verifying optima), in search (completeness vs. efficiency), and in Noesis itself (the fitness function problem).

---

## 4. Modal Logic (Kripke Semantics)

Extends propositional logic with operators □ (necessarily) and ◇ (possibly).

**Syntax**:
```
φ ::= p | ¬φ | φ ∧ ψ | □φ | ◇φ
where ◇φ ≡ ¬□¬φ  (duality)
```

**Kripke frame**: F = ⟨W, R⟩ where W is a set of "possible worlds" and R ⊆ W × W is an accessibility relation.

**Kripke model**: M = ⟨W, R, V⟩ where V: Prop → P(W) is a valuation (which propositions are true at which worlds).

**Satisfaction**:
```
M, w ⊨ p       iff  w ∈ V(p)
M, w ⊨ □φ      iff  for all v: wRv implies M, v ⊨ φ
M, w ⊨ ◇φ      iff  there exists v: wRv and M, v ⊨ φ
```

**Axiom systems** (correspond to frame conditions on R):

| System | Axiom | Frame Condition |
|--------|-------|-----------------|
| K | □(φ → ψ) → (□φ → □ψ) | None (basic distribution) |
| T | □φ → φ | Reflexive: ∀w. wRw |
| S4 | □φ → □□φ | Transitive: wRv ∧ vRu → wRu |
| B | φ → □◇φ | Symmetric: wRv → vRw |
| S5 | ◇φ → □◇φ | Equivalence relation (R, S, T) |

**S5 is critical**: In S5, every possible world can access every other. This collapses □ and ◇ to simple global quantifiers. S5 is the system used in most philosophical arguments about necessity and possibility, including the ontological argument.

**Key for Noesis**: Kripke frames are directed graphs. The accessibility relation R is just an adjacency matrix. Different modal logics correspond to different graph-theoretic constraints. This means modal reasoning can be encoded as graph operations — directly composable with anything Noesis already does on graphs.

---

## 5. Gödel's Ontological Proof (1970)

Uses **second-order modal logic** with S5 semantics. The formal system:

**Primitive**: P(φ) — "property φ is positive" (a second-order predicate over properties)

**Axioms**:
```
A1: P(φ) ∧ □(∀x. φ(x) → ψ(x)) → P(ψ)
    (If φ is positive and φ necessarily entails ψ, then ψ is positive)

A2: P(¬φ) ↔ ¬P(φ)
    (A property is positive iff its negation is not positive — exactly one of each pair)

A3: P(G)  where  G(x) ≡ ∀φ. P(φ) → φ(x)
    (God-likeness — having all positive properties — is itself positive)

A4: P(φ) → □P(φ)
    (Positive properties are necessarily positive — they don't vary across worlds)

A5: P(NE)  where  NE(x) ≡ ∀φ. φ ess x → □(∃y. φ(y))
    (Necessary existence is a positive property)
```

**Definitions**:
```
D1: G(x) ≡ ∀φ. P(φ) → φ(x)
    (x is God-like iff x has every positive property)

D2: φ ess x ≡ φ(x) ∧ ∀ψ. ψ(x) → □(∀y. φ(y) → ψ(y))
    (φ is an essence of x iff x has φ and φ necessarily entails every property of x)

D3: NE(x) ≡ ∀φ. φ ess x → □(∃y. φ(y))
    (x necessarily exists iff every essence of x is necessarily exemplified)
```

**Proof sketch**:
```
T1: P(φ) → ◇(∃x. φ(x))         (Positive properties are possibly exemplified)
    Proof: If P(φ) and ¬◇(∃x.φ(x)), then □(∀x.¬φ(x)), so □(∀x.φ(x)→ψ(x))
           for any ψ, so P(ψ) for all ψ by A1, contradicting A2.

C1: ◇(∃x. G(x))                  (A God-like being is possible)
    Proof: From A3 and T1.

T2: G(x) → G ess x               (God-likeness is an essence of any God-like being)
    Proof: If G(x), then x has all positive properties. Any property ψ of x:
           either P(ψ) or P(¬ψ). If P(¬ψ), then ¬ψ(x) — contradiction.
           So P(ψ), so □P(ψ) by A4, so □(∀y. G(y) → ψ(y)).

T3: □(∃x. G(x))                  (A God-like being necessarily exists)
    Proof: From C1, ◇(∃x. G(x)). Pick such x in some world w.
           G ess x by T2. NE(x) by A5 and D1.
           So □(∃y. G(y)) by D3. In S5, ◇□φ → □φ.

∴ ∃x. G(x)                       (A God-like being exists — from T3 + T axiom □φ→φ)
```

**Known issues**: Gödel's axioms also entail **modal collapse** — that every true proposition is necessarily true (◇φ → □φ), which collapses the distinction between contingent and necessary truth. This was proven by Sobel (1987). Anderson (1990) modified the axioms to avoid this.

**Key for Noesis**: The proof structure is a composition chain: second-order quantification over properties, composed with modal operators, composed with an essence relation that links properties to their necessary entailments. The modal collapse result shows how a composition that seems valid can have unintended global consequences — analogous to the bypass circuit problem in SETI vectors.

---

## 6. Gödel's Incompleteness Theorems (1931)

### First Incompleteness Theorem

**Setup**: Let T be a consistent, recursively axiomatizable theory that extends Robinson arithmetic Q.

**Gödel numbering**: Assign a unique natural number ⌈φ⌉ to every formula φ. This is injective and computable.

**Representability**: A relation R(n₁,...,nₖ) is **representable** in T iff there exists a formula ρ(x₁,...,xₖ) such that:
```
R(n₁,...,nₖ) holds   →  T ⊢ ρ(n̄₁,...,n̄ₖ)
R(n₁,...,nₖ) fails   →  T ⊢ ¬ρ(n̄₁,...,n̄ₖ)
```
where n̄ is the numeral for n (i.e., S(S(...S(0)...)) applied n times).

**Diagonal Lemma (Fixed Point Theorem)**: For any formula ψ(x) with one free variable, there exists a sentence γ such that:
```
T ⊢ γ ↔ ψ(⌈γ⌉)
```
γ "says of itself" that it has property ψ.

**Construction**: Let Prov_T(x) represent the provability predicate "x is the Gödel number of a theorem of T." Apply the Diagonal Lemma with ψ(x) = ¬Prov_T(x) to obtain the **Gödel sentence** G:
```
T ⊢ G ↔ ¬Prov_T(⌈G⌉)
```
G says: "I am not provable in T."

**Result**:
```
If T is consistent:     T ⊬ G    (G is not provable — otherwise T proves G, so G is false, contradiction)
If T is ω-consistent:   T ⊬ ¬G   (¬G is not provable either — otherwise T proves there's a proof of G, but no individual proof works)
```

Therefore G is **independent** of T: true (in the standard model) but unprovable.

### Second Incompleteness Theorem

**Con(T)** is the sentence ¬Prov_T(⌈0=1⌉) — "T does not prove 0=1."

```
If T is consistent: T ⊬ Con(T)
```

No consistent sufficiently strong theory can prove its own consistency.

**Proof idea**: Within T, one can formalize the argument "if T is consistent, then G is not provable, therefore G." This gives T ⊢ Con(T) → G. Since T ⊬ G, it follows T ⊬ Con(T).

**Key for Noesis**: The Diagonal Lemma is a *self-referential construction*. It's structurally identical to the fixed-point combinator Y in lambda calculus: Y(f) = f(Y(f)). This connects to Cantor's diagonalization, the halting problem, Russell's paradox, and Lawvere's fixed-point theorem in category theory. All of these are instances of the same abstract pattern: a system powerful enough to represent itself will generate undecidable/paradoxical self-referential statements. This is one of the deepest cross-domain bridges in mathematics.

---

## 7. Aquinas's Cosmological Arguments (Formalized)

### First Way: Argument from Motion

```
Let M(x) = "x is in motion" (changing state)
Let A(x,y) = "x actuates y" (x causes y's motion)

P1: ∃x. M(x)                                  (Something is in motion)
P2: ∀x. M(x) → ∃y. (y ≠ x ∧ A(y,x))         (Nothing moves itself)
P3: ¬∃ infinite chain c₁, c₂, c₃, ... such that A(cᵢ₊₁, cᵢ) for all i
    (No infinite regress of movers)

From P1-P3:
∃u. (∀x. M(x) → u is in the causal ancestry of x's motion) ∧ ¬M(u)
(There exists an unmoved mover)
```

The key logical move is P3 — the rejection of infinite causal regress. This is a **well-foundedness assumption**: requiring the "moved-by" relation to be well-founded (every non-empty subset has a minimal element).

**Set-theoretic parallel**: This is equivalent to the Axiom of Foundation in ZF set theory (no infinite descending ∈-chains). The existence of an unmoved mover is structurally identical to the existence of the empty set as the foundation of the cumulative hierarchy.

### Second Way: Efficient Causation (same structure, replace motion with causation)

### Third Way: Contingency and Necessity

```
Let C(x) = "x is contingent" (could fail to exist)
Let N(x) = "x exists necessarily"
Let E(x,t) = "x exists at time t"

P1: ∀x. C(x) → ◇¬E(x,t) for some t           (Contingent things can fail to exist)
P2: ∀x. C(x) → ∃y. y causes E(x,t)            (Contingent things require a cause)
P3: If everything is contingent, then ◇(∀x.¬E(x,t₀)) for some t₀
    (If everything is contingent, it's possible that nothing exists at some time)
P4: If at t₀ nothing exists, then nothing exists for all t > t₀
    (Ex nihilo nihil fit — nothing comes from nothing)
P5: ∃x. E(x, now)                              (Something exists now)

From P3-P5: ¬∀x.C(x)                           (Not everything is contingent)
Therefore:  ∃x. N(x)                            (Something exists necessarily)
```

**Modal reformulation** (in S5):
```
P1: ∀x. C(x) ↔ ◇¬∃y(y=x)
P2: ∃x.∃y(y=x)                                 (Something exists — non-negotiable)
Assume: ∀x.C(x)
Then:   ∀x.◇¬∃y(y=x)
Claim:  This leads to ◇¬∃x.∃y(y=x) under composition assumptions
But:    P2 is necessarily true (or at least true)
Contradiction. Therefore ∃x.N(x) where N(x) = □∃y(y=x)
```

**Key for Noesis**: The Third Way is essentially a **fixed-point argument in modal logic**. It says: take the contingency operator, iterate it across all entities, and show the result is inconsistent with the existence of anything. This forces a fixed point — a necessarily existing thing. The mathematical structure is: iterating an operator over a domain requires a fixed point under certain closure conditions (Knaster-Tarski theorem in lattice theory).

---

## 8. The Logicism Program (Frege → Russell → Gödel)

The attempt to reduce all mathematics to pure logic.

**Frege's system** (Grundgesetze, 1893): Introduced **Basic Law V**:
```
{x : F(x)} = {x : G(x)}  ↔  ∀x. F(x) ↔ G(x)
```
(Two sets are equal iff they have the same members — the comprehension principle.)

**Russell's Paradox** (1901): Let R = {x : x ∉ x}. Then R ∈ R ↔ R ∉ R. Contradiction. Basic Law V is inconsistent.

**Russell's fix (Type Theory)**: Stratify the universe into types:
```
Type 0: individuals
Type 1: sets of individuals
Type 2: sets of sets of individuals
...
Type n+1: sets of elements of type n

Rule: x ∈ y is only well-formed if type(y) = type(x) + 1
```
This prevents self-reference. R = {x : x ∉ x} is ill-formed because x ∈ x requires type(x) = type(x) + 1.

**Principia Mathematica** (Russell & Whitehead, 1910-1913): Derived arithmetic from type theory + axiom of infinity + axiom of reducibility. Required ~362 pages to prove 1+1=2.

**Gödel's response** (1931): Even if the derivation succeeds, the resulting system is incomplete (First Incompleteness Theorem). The logicist program can't capture all mathematical truth.

**Key for Noesis**: Type theory is alive and well — it's the foundation of modern proof assistants (Coq, Lean, Agda) and the Curry-Howard correspondence: **proofs = programs, propositions = types**. This means:

```
Logical deduction    ↔    Program composition
Proving A → B        ↔    Writing a function A → B  
Proving A ∧ B        ↔    Constructing a pair (a, b)
Proving A ∨ B        ↔    Tagged union / Either type
Proving ∀x.P(x)     ↔    Polymorphic function
Proving ∃x.P(x)     ↔    Dependent pair (witness + proof)
```

This is potentially huge for Noesis: every chain of logical reasoning corresponds to a program, and vice versa. Composing reasoning steps IS function composition.

---

## 9. Intuitionistic Logic (Brouwer, Heyting)

Rejects the **law of excluded middle** (LEM): ¬(φ ∨ ¬φ) is consistent in intuitionistic logic.

**Heyting algebra**: Like Boolean algebra but without the complement law a ∨ ¬a = 1.

```
Classical:       ¬¬φ → φ        (double negation elimination — VALID)
Intuitionistic:  ¬¬φ → φ        (NOT generally valid)
                 φ → ¬¬φ        (still valid)
```

**BHK interpretation** (Brouwer-Heyting-Kolmogorov): A proof of φ is:
```
Proof of φ ∧ ψ:    a pair (p, q) where p proves φ and q proves ψ
Proof of φ ∨ ψ:    either (left, p) where p proves φ, or (right, q) where q proves ψ
Proof of φ → ψ:    a function transforming any proof of φ into a proof of ψ
Proof of ∀x.P(x):  a function giving a proof of P(a) for any a
Proof of ∃x.P(x):  a pair (a, p) where p proves P(a)
Proof of ¬φ:        a function transforming any proof of φ into a proof of ⊥ (absurdity)
```

**Kripke semantics for intuitionistic logic**: Use *partially ordered* Kripke frames (W, ≤) where truth is **monotone** — once true at a world, true at all later worlds:
```
w ⊨ p  and  w ≤ v  implies  v ⊨ p
```
This models the growth of mathematical knowledge: you can learn new things but can't unlearn them.

**Key for Noesis**: Intuitionistic logic is the internal logic of **topoi** (categories that generalize the category of sets). The fact that classical and intuitionistic logic differ means there are *multiple valid logical substrates*, not just one. This is directly relevant to the "frozen vs. dynamic frames" insight — different logical frames aren't just different viewpoints on one truth, they're genuinely different mathematical universes.

---

## 10. Cross-Domain Bridge Map

These are the structural isomorphisms Noesis should be hunting:

```
SELF-REFERENCE CLUSTER:
  Gödel's Diagonal Lemma ≅ Y combinator ≅ Cantor's diagonal
  ≅ Halting problem ≅ Russell's paradox ≅ Lawvere's fixed-point theorem
  Common structure: f(x) = ¬g(x, x) for suitable g and ¬

WELL-FOUNDEDNESS CLUSTER:
  Aquinas's First Way ≅ Axiom of Foundation ≅ Well-ordering principle
  ≅ Structural induction ≅ Noetherian rings ≅ Descending chain condition
  Common structure: no infinite descending chain in relation R

DUALITY CLUSTER:
  □/◇ duality ≅ ∀/∃ duality ≅ ∧/∨ duality ≅ De Morgan's laws
  ≅ sup/inf in lattices ≅ limit/colimit in categories
  Common structure: ¬Q¬ where Q is a quantifier/operator

COMPLETENESS-DECIDABILITY GAP:
  Gödel completeness vs. undecidability (FOL) ≅ NP verification vs. P solving
  ≅ Noesis fitness evaluation vs. search ≅ Checking proofs vs. finding proofs
  Common structure: verification is strictly easier than discovery

FIXED POINT CLUSTER:
  Aquinas's Third Way ≅ Knaster-Tarski theorem ≅ Brouwer fixed point theorem
  ≅ Nash equilibrium existence ≅ Diagonal lemma ≅ Kleene's recursion theorem
  Common structure: continuous/monotone map on complete structure has fixed point

TYPE STRATIFICATION CLUSTER:
  Russell's type theory ≅ Cumulative hierarchy of sets ≅ Curry-Howard correspondence
  ≅ Stratified programming (no self-modifying code) ≅ Logical frameworks
  Common structure: prevent self-reference via hierarchical stratification

FRAME PLURALITY:
  Classical vs. intuitionistic logic ≅ Different Kripke frame constraints
  ≅ Different topoi ≅ Different model categories
  ≅ Frozen vs. dynamic frames in transformer inference
  Common structure: the rules of reasoning are parameters, not constants
```

---

## 11. Computability Connections

For encoding as Noesis operations:

```
BOOLEAN OPERATIONS: Direct — these are primitive operations on {0,1}
  AND, OR, NOT, NAND, XOR, IMPLIES
  Compose to: SAT solvers, circuit evaluation

PREDICATE LOGIC: Functions over domains
  ∀x.P(x) ≡ fold(AND, map(P, domain))
  ∃x.P(x) ≡ fold(OR, map(P, domain))
  These are aggregation operations — composable with any map-reduce structure

MODAL OPERATORS: Graph operations
  □φ at w ≡ all(φ(v) for v in neighbors(w, R))
  ◇φ at w ≡ any(φ(v) for v in neighbors(w, R))
  Composable with: PageRank, graph neural networks, belief propagation

PROOF SEARCH: Tree search with unification
  Resolution: given (A ∨ B) and (¬A ∨ C), derive (B ∨ C)
  This is composable with: constraint propagation, SAT solving, ATP

FIXED POINTS: Iterative computation
  lfp(F) = ⊔{Fⁿ(⊥) : n ∈ ℕ}  (least fixed point as limit of iteration)
  Composable with: dataflow analysis, abstract interpretation, iterative deepening
```
