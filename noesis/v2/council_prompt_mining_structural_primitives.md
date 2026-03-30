# Council Prompt: Mining the Structural Primitives of Mathematics

## Context for the Council

We are building a tensor-based discovery engine that searches for compositional bridges between mathematical concepts. In our last session, you unanimously diagnosed that our current encoding is shallow — surface features, co-occurrence, vibes. You proposed encoding "what concepts do, not what they are" — operational signatures, invariance vectors, failure fingerprints, morphism signatures.

Now we need to do the actual mining. We need you to help us extract the raw structural data from the mathematics you have encoded in your weights. This is primary research. We are not looking for summaries, overviews, or pedagogical explanations. We are looking for the actual structural relationships between equations, stated with enough precision to be computationally verified.

## IMPORTANT: What We Are NOT Asking

We are NOT asking you to:
- Describe fields of mathematics at a high level
- Recommend approaches or architectures (you already did that)
- Produce a taxonomy or classification scheme
- Write code (we'll do that ourselves)
- Tell us what's "interesting" or "important" (that's human bias talking)

## What We ARE Asking

We need you to act as a mathematical reference — a library, not an advisor. Extract from your training data the specific, verifiable structural relationships between mathematical objects. We will independently verify everything you give us using SymPy and formal references.

## Task 1: The Noether Tree

Emmy Noether proved that continuous symmetries correspond to conservation laws. We need the FULL tree, not just the famous examples.

For each entry, provide:
- The symmetry (stated precisely — what transformation group?)
- The conservation law it implies
- The equation(s) where this manifests
- The derivation pathway (which intermediate steps connect symmetry to conservation?)

Start with the standard ones we know:
- Time translation → Energy conservation
- Spatial translation → Momentum conservation
- Rotation → Angular momentum conservation

Then go DEEPER. Give us every symmetry-conservation pair you can extract:
- Gauge symmetries (U(1), SU(2), SU(3)) → what conserved quantities?
- Discrete symmetries (C, P, T, CPT) → what conservation-like constraints?
- Scale invariance / conformal symmetry → what's conserved?
- Lorentz invariance → what's the conserved current?
- Internal symmetries in condensed matter → what emerges?
- Supersymmetry (if it exists) → what would be conserved?
- Diffeomorphism invariance in GR → what's the analogue?

For each: be precise enough that we can verify with SymPy. Give us the Lagrangian, the symmetry transformation, and the Noether current.

## Task 2: Equation Derivation Chains

We need actual derivation chains — not "A is related to B" but "A derives from B via these specific steps."

Give us 20 derivation chains, each at least 3 steps deep. Format:

```
CHAIN: [Name]
Step 1: [Equation/principle]
  ↓ via [specific mathematical operation or assumption]
Step 2: [Equation/principle]
  ↓ via [specific mathematical operation or assumption]
Step 3: [Equation/principle]
  ↓ via [specific mathematical operation or assumption]
Step 4: [Equation/principle]
What breaks if you remove Step 2: [specific consequence]
What structure is preserved through the chain: [invariant]
What structure is destroyed: [what's lost]
```

Prioritize chains that cross domain boundaries (e.g., classical mechanics → quantum mechanics, thermodynamics → information theory, topology → physics).

## Task 3: Structural Isomorphisms

Give us pairs (or triples) of mathematical objects from DIFFERENT fields that have isomorphic internal structure. Not "these are analogous" — "these have a specific, named structure-preserving map between them."

For each pair:
- Object A: [precise definition]
- Object B: [precise definition]
- The map: [what specifically maps to what]
- What the map preserves: [list]
- What it forgets/destroys: [list]
- The name (if this isomorphism has one): [e.g., Curry-Howard, Stone duality, Pontryagin duality]
- Can this be computationally verified? [yes/no and how]

Give us at least 15. Start with the well-known ones (Curry-Howard, Galois connection ↔ adjoint functor) then go deeper into ones that are less famous but equally precise.

## Task 4: The Failure Fingerprint Library

When you remove a condition from a mathematical structure, the way it breaks is a structural signature. Give us a systematic catalog.

Format:
```
STRUCTURE: [e.g., Group]
REMOVE: [e.g., associativity]
RESULT: [e.g., Quasigroup]
WHAT BREAKS: [e.g., uniqueness of identity, Cayley's theorem fails]
WHAT SURVIVES: [e.g., closure, invertibility]
```

Give us at least 30 entries across:
- Algebraic structures (groups, rings, fields, modules, algebras)
- Topological structures (metric spaces, topological spaces, manifolds)
- Order structures (lattices, partial orders, well-orders)
- Logical structures (classical logic, intuitionistic logic, linear logic)
- Physical structures (Hamiltonian systems, gauge theories, quantum systems)

## Task 5: What's Primitive?

This is the hardest question. If you had to identify the 10-20 structural primitives that ALL of mathematics is built from — not mathematical objects, but the structural operations or patterns that recur everywhere — what would they be?

We're not asking for axioms (ZFC, etc.). We're asking: what are the recurring structural moves that appear across algebra, analysis, topology, physics, computation, and logic?

Candidates might include things like:
- Fixed point (appears in: Banach, Brouwer, recursion, eigenvalues, equilibria)
- Duality (appears in: Fourier, Pontryagin, Stone, electromagnetic, wave-particle)
- Composition (appears in: function composition, group operation, morphism chains)
- Symmetry breaking (appears in: phase transitions, gauge theory, bifurcation)

But don't just list our candidates back. Tell us what WE'RE MISSING. What structural primitives are so fundamental they're invisible — like water to fish?

For each primitive you identify:
- Name it (or name the closest existing concept)
- Give 5+ examples from different fields where it appears
- State what property it always has (the invariant of the primitive itself)
- State whether it can be formalized (and if so, in what framework — category theory, type theory, etc.)

## Task 6: Physical Constants as Structural Constraints

The ~25 fundamental physical constants (speed of light, Planck's constant, gravitational constant, fine structure constant, etc.) are not just numbers — they are structural constraints on how the universe works.

For each major constant:
- What equations contain it?
- What happens to those equations in the limit where the constant → 0 or → ∞?
- What structural relationship does the constant encode? (e.g., c encodes the relationship between space and time; ℏ encodes the relationship between energy and frequency)
- Which constants are independent and which derive from others?
- What is the minimal set of truly independent constants? (Dimensional analysis says ~3-4 in natural units. Which 3-4?)

## Output Format

Be exhaustive rather than selective. We will filter. Give us raw material, not curated highlights. Err on the side of too much precision rather than too little. Include the actual equations (LaTeX-style notation is fine). If you're uncertain about a claim, say so explicitly rather than hedging with soft language.

We will verify everything you give us computationally. Precision matters more than elegance.
