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

## The Fields — Go Wide and Weird

### Tier 1: Implement First (high diversity, well-defined computations)

1. **Tropical geometry** — min-plus algebra, tropical polynomials, tropical convexity
2. **p-adic numbers** — p-adic norm, p-adic expansion, Hensel's lemma approximation
3. **Ramsey theory** — Ramsey number bounds, coloring algorithms, Hales-Jewett
4. **Continued fractions** — convergents, best rational approximations, Stern-Brocot
5. **Modular forms** — q-expansions, Eisenstein series, Dedekind eta
6. **Lattice theory** — meet, join, Möbius function, lattice reduction (LLL)
7. **Combinatorial species** — generating functions, labeled/unlabeled counting
8. **Knot invariants** — Alexander polynomial, Jones polynomial (simplified), linking number
9. **Surreal numbers** — construction, addition, multiplication, comparison
10. **Cellular automata** — all 256 elementary rules, Wolfram classification, entropy of orbits
11. **Automata theory** — DFA minimization, NFA→DFA conversion, regular expression matching
12. **Lambda calculus** — Church numerals, SKI combinators, beta reduction steps
13. **Fractal dimensions** — box-counting, correlation dimension, Hausdorff estimation
14. **Möbius functions** — number-theoretic Möbius, Möbius inversion, Mertens function
15. **Elliptic curves** — point addition, scalar multiplication, j-invariant, Weierstrass form

### Tier 2: Implement Next (more exotic, still computable)

16. **Finite fields** — arithmetic in GF(p^n), polynomial multiplication, discrete log
17. **Representation theory** — character tables for small groups, tensor products of representations
18. **Homological algebra** — chain complexes, boundary operators, Betti numbers (simplicial)
19. **Spectral graph theory** — graph Laplacian eigenvalues, Cheeger inequality, Fiedler vector
20. **Extremal graph theory** — Turán numbers, Zarankiewicz problem bounds, Ramsey graph construction
21. **Diophantine approximation** — Liouville's theorem, irrationality measure, three-distance theorem
22. **Catalan combinatorics** — Dyck paths, non-crossing partitions, ballot sequences, triangulations
23. **Partition theory** — integer partitions, partition function p(n), Ferrers diagrams, conjugate partitions
24. **Coding theory** — Hamming codes, Reed-Solomon, BCH, syndrome decoding
25. **Matroid theory** — rank function, circuits, duality, greedy algorithm optimality
26. **Ergodic theory** — Birkhoff averages, mixing coefficients, entropy rate
27. **Percolation theory** — site/bond percolation on grids, cluster size distribution, critical threshold
28. **Random matrix theory** — Wigner semicircle, Tracy-Widom, eigenvalue spacing statistics
29. **Geometric algebra** — multivectors, geometric product, rotors, reflections
30. **Clifford algebra** — Cl(p,q) construction, spinors, pin groups

### Tier 3: Deep Cuts (obscure but computable)

31. **Umbral calculus** — Sheffer sequences, Appell polynomials, umbral composition
32. **q-analogues** — q-factorials, q-binomials, q-exponentials, q-series
33. **Tropical semirings** — min-plus, max-plus, shortest path algebra
34. **Valuations** — p-adic valuations, Ostrowski's theorem (discrete approximation)
35. **Operads** — composition operations, associahedra, little disks (simplified)
36. **Species arithmetic** — addition, multiplication, composition of species
37. **Rook theory** — rook polynomials, hit numbers, permutations with forbidden positions
38. **Majorization** — Schur convexity, Lorenz curves, doubly stochastic matrices
39. **Zeta functions** — Riemann, Hurwitz, Dedekind, Selberg (numerical approximations)
40. **L-functions** — Dirichlet L-functions, functional equation checks, zero finding
41. **Hypergeometric functions** — 2F1, 3F2, Pochhammer symbols, contiguous relations
42. **Orthogonal polynomials** — Chebyshev, Legendre, Hermite, Laguerre, Jacobi — evaluation and recurrence
43. **Digital root / digit sums** — digital root, multiplicative persistence, additive persistence
44. **Nim theory** — Sprague-Grundy values, nimbers, combinatorial game evaluation
45. **Fibonacci variations** — Lucas, tribonacci, Fibonacci words, Zeckendorf representation
46. **Pascal variations** — Pascal's triangle modular patterns, Sierpinski triangle, multinomial coefficients
47. **Stern's diatomic series** — Stern-Brocot construction, Calkin-Wilf enumeration
48. **Kolmogorov complexity proxies** — compression ratio, LZ complexity, entropy rate estimation
49. **Algorithmic randomness** — Borel normality tests, frequency tests, serial tests
50. **Topos theory** (simplified) — subobject classifiers, presheaves on finite categories (toy models)

### Tier 4: Applied/Cross-Domain (bridges between fields)

51. **Information geometry** — Fisher information metric, geodesics on statistical manifolds
52. **Optimal transport** — Wasserstein distance, Sinkhorn algorithm, earth mover's distance
53. **Persistent homology** — Vietoris-Rips complex, persistence diagrams, bottleneck distance
54. **Topological data analysis** — mapper algorithm, nerve theorem, simplicial complexes from data
55. **Symbolic dynamics** — shift spaces, sofic shifts, entropy of symbolic systems
56. **Arithmetic geometry** — height functions, Mordell-Weil (toy), rational points on conics
57. **Analytic combinatorics** — singularity analysis, transfer theorems, asymptotic enumeration
58. **Probabilistic combinatorics** — Lovász local lemma (constructive), random graphs, threshold functions
59. **Additive combinatorics** — sumset bounds, Freiman's theorem (estimates), Roth's theorem (verification)
60. **Computational algebra** — Gröbner bases (toy), polynomial ideals, elimination theory

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
