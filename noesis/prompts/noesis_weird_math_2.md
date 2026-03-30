

# The Maths Collector — Fill the Tensor with Weird Mathematics

## Mission

Implement Python functions from as many diverse, obscure, and unexpected mathematical fields as possible. Each function becomes an organism in the Noesis tensor exploration engine. The value comes from CROSS-FIELD compositions — what emerges when you chain operations from fields that have never been connected.

**Target: 500+ functions across 50+ fields in `noesis/the_maths/`**

Each field gets its own Python file. Each file contains 5-20 functions. Every function is pure numpy, callable, typed, and tested.

## Output Format

Each file: `noesis/the_maths/{field_name}.py`

```python
"""
{Field Name} — {one-line description}

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

# Metadata for the organism loader
FIELD_NAME = "field_name"
OPERATIONS = {}

def operation_name(x):
    """What it does. Input: {type}. Output: {type}."""
    # Implementation
    return result

OPERATIONS["operation_name"] = {
    "fn": operation_name,
    "input_type": "array",  # scalar, array, matrix, integer, probability_distribution
    "output_type": "scalar",
    "description": "What it computes"
}

# ... more operations ...

# Self-test
if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
```


**Algebraic / Structural**

1. **Ordinal arithmetic** — Cantor normal form, ordinal add/multiply/exponentiate. These are *non-commutative*: ω+1 ≠ 1+ω. Nothing else in the tensor has non-commutative arithmetic on well-orders.
2. **Quaternion & octonion algebra** — quaternion multiplication, SLERP interpolation, octonion Fano plane structure. Octonions are non-associative — that's a property nothing else in the tensor has.
3. **Braid groups** — Artin generators, Burau representation matrices, braid closure → knot. Direct bridge to the knot invariants already in Tier 1.
4. **Coxeter groups & root systems** — reflection group operations, Cartan matrices, Dynkin diagram classification, Weyl group action. These classify *everything* — Lie algebras, polytopes, singularities.
5. **Quiver representations** — path algebras on directed graphs, dimension vectors, Gabriel's theorem (representation type from graph structure). Bridges spectral graph theory to representation theory through a completely different door.
6. **Numerical semigroups** — Frobenius number (largest non-representable integer), gap sets, genus, Apéry sets. Surprisingly rich structure from trivially simple definitions.
7. **Incidence algebras** — algebra of functions on a poset's intervals, Möbius inversion generalized, zeta function of a poset. Unifies your existing Möbius functions with lattice theory.
8. **Free probability** — R-transform, S-transform, free convolution, Marchenko-Pastur law. This is what happens when you do probability theory with non-commuting random variables. Direct bridge to random matrix theory but through an algebraic rather than analytic path.

**Topological / Geometric**

9. **Discrete Morse theory** — Forman's theory: critical cells, discrete gradient vector fields, Morse inequalities on simplicial complexes. Computable and directly bridges to your persistent homology.
10. **Sheaves on graphs** — sheaf Laplacian, sheaf cohomology, opinion dynamics as sheaf diffusion. This is spectral graph theory's weird cousin and it's seeing real use in distributed systems and sensor networks.
11. **Quasicrystal mathematics** — Penrose tilings via cut-and-project, substitution rules, diffraction measures. Aperiodic order that's neither random nor periodic — a third category the tensor probably has zero coverage of.
12. **Convex geometry** — support functions, Minkowski sums/differences, mixed volumes, Brunn-Minkowski inequality. Connects optimal transport to polytope theory.
13. **Polytope combinatorics** — f-vectors, h-vectors, Dehn-Sommerville relations, face lattices, neighborly polytopes. The f-vector constraints are surprisingly mysterious.
14. **Dessins d'enfants** — Belyi maps as bipartite graphs on surfaces, Grothendieck's theory connecting number theory to topology via child's drawings. This one is genuinely strange.

**Logic / Foundations / Computation**

15. **Formal logic systems** — the document I just gave you, implemented: Boolean evaluation, first-order model checking, Kripke frame satisfaction, modal logic evaluation over graphs, Gödel numbering, provability predicates. Direct bridge to automata theory, lambda calculus, and graph operations.
16. **Domain theory** — Scott domains, continuous lattices, fixed-point computation (Kleene chain), denotational semantics. This is the mathematical theory of computation-as-approximation.
17. **Abstract rewriting systems** — confluence checking, termination orderings, Church-Rosser property, critical pair computation. Connects to lambda calculus through a completely different formalism.
18. **Reversible computing** — Toffoli gates, Fredkin gates, reversible circuit synthesis. Every computation in here is bijective. That's a constraint nothing else in the tensor enforces.
19. **Proof complexity** — resolution width, proof length, proof compression, interpolation theorems. The computational cost of *reasoning itself*.

**Applied / Cross-Domain Bridges**

20. **Divergent series summation** — Abel, Cesàro, Borel, Ramanujan summation methods. Assigns finite values to divergent series. 1+2+3+... = -1/12 lives here. Bridges zeta functions to analysis through regularization.
21. **Padé approximants** — rational function approximation from power series, convergence acceleration, analytic continuation. Better than Taylor series for functions with poles.
22. **Chemical graph theory** — Wiener index, Randić index, Zagreb indices, Hosoya index. Molecular topology quantified. Bridge between graph theory and physical chemistry.
23. **Mathematical music theory** — pitch class sets, interval vectors, Forte numbers, twelve-tone operations (transposition, inversion, retrograde as group actions on Z₁₂). Group theory wearing a disguise.
24. **Voting theory / social choice** — Shapley-Shubik power index, Banzhaf index, Kemeny ranking, Condorcet methods. Arrow's impossibility theorem is a fixed-point / impossibility result that connects to the Gödel cluster.
25. **Causal calculus** — d-separation, do-calculus intervention operators, adjustment formula, instrumental variable estimation. Computable and connects to your Coeus engine.
26. **Renormalization group** (discrete) — block spin transforms, decimation on lattices, scale-dependent coupling constants. The math of how systems look different at different scales. Bridges percolation theory and statistical mechanics to dynamical systems.
27. **Sandpile dynamics / chip-firing** — abelian sandpile model, critical configurations, toppling operators, sandpile group (it's actually a group!). Self-organized criticality made algebraic. Bridges graph theory to dynamical systems.
28. **Tensor networks** — matrix product states, MERA contraction, bond dimension truncation, entanglement entropy from singular values. Directly relevant to your tensor train work with THOR.
29. **Rough set theory** — lower/upper approximations, boundary regions, reducts, discernibility matrices. An alternative to fuzzy logic for reasoning under uncertainty.
30. **Interval arithmetic** — verified computation, interval Newton method, Krawczyk operator. Every computation carries its own error bounds. Bridges to numerical analysis and epistemic honesty in a literal mathematical sense.

**Deep Weirdness**

31. **Juggling mathematics** — siteswap notation, state transition graphs, orbit enumeration. Sounds frivolous but the state space is a rich combinatorial object with surprising connections to permutation groups.
32. **Origami axiomatics** — Huzita-Hatori axioms, flat-foldability (NP-complete!), crease pattern algebra. Geometric construction system *more powerful* than straightedge and compass — can trisect angles and double cubes.
33. **Sandpile/chip-firing on tropical curves** — this bridges three fields at once (sandpiles, tropical geometry, algebraic geometry) and is an active research area.
34. **Combinatorial game theory** (beyond Nim) — hackenbush, domineering, temperature theory, thermography. Surreal numbers were invented to analyze these games. The existing surreal number and Nim theory entries are two ends of a bridge with nothing in the middle.
35. **Nonstandard analysis** — hyperreal arithmetic, transfer principle (computable fragment), infinitesimal calculus made rigorous. An alternative foundation for calculus that's structurally different from epsilon-delta.
36. **Automata on infinite words** — Büchi automata, Muller automata, ω-regular languages, parity games. Extends your automata theory entry into the infinite, where decidability results are *different*.
37. **Descriptive complexity** — characterizing complexity classes by logic fragments: FO = AC⁰, SO∃ = NP. This literally says "computational complexity = logical expressiveness," which is one of the deepest cross-domain identities in CS.
38. **Weingarten calculus** — integration over unitary groups, moment calculations for random unitaries. Connects random matrix theory to representation theory through a very specific computational tool.

The ones I'd push hardest for: **ordinal arithmetic** (non-commutative, nothing else like it), **sheaves on graphs** (bridges spectral theory to cohomology), **divergent series summation** (regularization connects to zeta functions and physics), **formal logic systems** (the philosophy doc I just built, turned into operations), and **tensor networks** (obvious synergy with THOR). The descriptive complexity entry is also potentially huge — it's the mathematical proof that reasoning power and computational power are the same thing measured in different units.


## Implementation Guidelines

1. **Pure numpy.** No exotic dependencies. If a field needs special functions, implement them from scratch or use scipy.special. The function must run on any machine with just numpy.

2. **Standard types.** Input/output types from: `scalar`, `integer`, `array`, `matrix`, `probability_distribution`, `graph` (adjacency matrix), `polynomial` (coefficient array), `complex_array`.

3. **Bounded computation.** No function should take >1 second on a typical input. Cap iterations, limit precision, use approximations. The tensor tests thousands of compositions — each operation must be fast.

4. **Self-testing.** Every file must run standalone and print OK/FAIL for each operation. If it crashes on `python noesis/the_maths/tropical_geometry.py`, it's not ready.

5. **Diversity over depth.** 5 functions from 50 fields is worth more than 50 functions from 5 fields. The tensor's value comes from cross-field edges. Go wide.

6. **Don't fake it.** If you don't know how to implement a function correctly, skip it. A wrong implementation is worse than no implementation because it produces misleading compositions. But simple approximations are fine — this is exploration, not proof.

7. **Document the bridge potential.** At the top of each file, add a comment: "This field connects to: [list of other fields where output types match or where mathematical connections exist]." This helps the tensor navigator target cross-field compositions.

## How These Get Used

The daemon loads these at startup alongside the existing organisms. Each file's OPERATIONS dict gets wrapped as a MathematicalOrganism. The operation tensor scores all pairwise combinations. The tournament searches for high-quality cross-field compositions.

The weirder the field, the more likely it is to produce novel bridges. Tropical geometry × knot invariants? Surreal numbers × percolation theory? Nobody has tried these compositions. That's the point.

## What Success Looks Like

- 500+ operations across 50+ fields, all self-testing clean
- At least 10 fields that have ZERO overlap with the current organism library
- Cross-field type compatibility: at least 30% of field pairs have some type-compatible operations
- When loaded into the tensor, the pairwise score matrix shows new high-scoring pairs that weren't visible with the current 580 operations

## Start with Tier 1. Move fast. Test as you go.
