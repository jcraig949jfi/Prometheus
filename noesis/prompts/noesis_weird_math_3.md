

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

These are going to take some serious research.  Take your time.  See if you can get through them.  Write a document for the challenges, and suggest another structure if they don't fit cleanly into the above structure


Great instinct. The standard list is almost entirely post-Enlightenment European math. There are computable systems from other traditions that encode genuinely different structural primitives — not just "the same math with different notation" but cases where the *framing* produces operations the Western canon doesn't naturally generate.

**Ancient / Classical Systems with Computable Operations**

1. **Babylonian sexagesimal arithmetic** — Base-60 positional notation with no zero placeholder (ambiguous place value). The operations aren't just "base conversion" — their reciprocal tables and geometric algebra methods solve quadratics through a cut-and-paste geometric procedure that's structurally different from al-Khwarizmi's algebraic method. Computable: base conversion, reciprocal table generation, geometric-mean solving procedures, regular number detection (numbers whose reciprocals terminate in base 60, i.e., of the form 2ᵃ·3ᵇ·5ᶜ).

2. **Egyptian/Rhind fraction arithmetic** — All fractions expressed as sums of distinct unit fractions (1/n). Decomposition is *not unique* — the greedy algorithm (Fibonacci/Sylvester) gives one answer, the Egyptian scribes used different heuristics. Operations: greedy decomposition, 2/n table reconstruction (how the Rhind papyrus tabulates 2/n for odd n), Erdős–Straus conjecture verification (can 4/n always be written as three unit fractions?), oddness of optimal decomposition length. The *constraint* of distinct unit fractions creates a completely different algebraic structure from ordinary rationals.

3. **Chinese Remainder Theorem arithmetic (Sunzi Suanjing, ~3rd century)** — Sunzi's original formulation is a constructive algorithm, not just an existence theorem. Operations: CRT reconstruction, simultaneous congruence solving, calendar cycle computation (the original application — computing when cycles of different lengths re-synchronize). Bridge to coding theory and secret sharing schemes.

4. **Kerala school series** (Madhava, ~1350) — Power series for π, arctangent, sine, cosine developed 250 years before Newton/Leibniz, but with different convergence acceleration techniques. Madhava's correction terms for truncated series are *not* the same as European acceleration methods — they use a rational approximation to the tail that's structurally closer to Padé approximants than to Euler-Maclaurin. Operations: Madhava-Leibniz series with correction terms, Madhava's sine/cosine series, convergence acceleration comparison against European methods. The correction terms themselves are interesting objects.

5. **Plimpton 322 / Babylonian Pythagorean generation** — Not a trig table (that interpretation is contested). More likely a systematic procedure for generating Pythagorean triples using the parametrization (p²−q², 2pq, p²+q²) with specific regularity constraints on p and q. Operations: regular-number-constrained triple generation, comparison of generation methods, gap analysis (which triples the procedure *can't* find).

6. **Rod calculus / Chinese counting rods (Suanzi)** — A physical positional decimal system where orientation encodes odd/even place. The mechanical procedure for polynomial root extraction (Horner-like method, but developed by Jia Xian ~1050, centuries before Horner) and the Tian Yuan Shu algebraic notation system for polynomial manipulation. Operations: Horner-scheme evaluation, polynomial GCD via rod procedures, matrix methods for simultaneous linear equations (Fangcheng, in the Nine Chapters — this is Gaussian elimination ~2000 years before Gauss).

7. **Vedic square / Vedic mathematics operations** — The Vedic square (digital roots of multiplication table) has genuine group-theoretic structure: it's the Cayley table of Z₉ under multiplication. The "sutras" are mostly 20th century (Tirthaji, 1965), but the digital root structure itself connects to modular arithmetic, magic squares, and Latin square theory in ways that are non-obvious. Operations: Vedic square generation, digital root multiplication tables for arbitrary bases, nilpotent/idempotent detection in these reduced algebras.

8. **Incan quipu arithmetic** — Not just record-keeping. Recent research (Urton, Hyland) suggests quipus encode information through knot type, cord color, ply direction, and attachment position. The *positional* encoding system along a cord is base-10, but the *hierarchical* structure (subsidiary cords hanging from subsidiary cords) is a tree. Operations: tree-structured hierarchical summation, pendant-group aggregation, cross-cord consistency checking (some quipus have built-in checksums). The tree structure makes this a different computational model from flat positional notation.

9. **Mayan vigesimal arithmetic** — Base-20 with a modified base-18 layer for calendrical computation (so the third position is 18×20 = 360 rather than 20×20 = 400). This means the positional system is *not* a pure polynomial base — it's a mixed-radix system. Operations: mixed-radix arithmetic, Long Count date computation, Calendar Round cycle analysis (260 × 365 = 18,980 day cycle, which is an LCM computation). The mixed-radix structure is the interesting primitive here.

10. **Japanese wasan geometry** (Sangaku tradition) — Geometric problems posed as temple offerings, often involving chains of tangent circles (Descartes Circle Theorem extensions), ellipses inscribed in triangles, and optimization problems with no Western parallel. The Descartes Circle Theorem: if four mutually tangent circles have curvatures k₁,k₂,k₃,k₄, then (k₁+k₂+k₃+k₄)² = 2(k₁²+k₂²+k₃²+k₄²). Operations: Apollonian gasket generation, inversive distance computation, Soddy circle chains, nested tangency optimization. The inversive geometry framework is distinct from Euclidean or projective.

**Non-Western Logical / Combinatorial Systems**

11. **Sanskrit prosody combinatorics** (Pingala, ~300 BCE) — Pingala's Chandahśāstra contains the first known binary enumeration system (laghu/guru = short/long syllables), the first known description of what's now called Pascal's triangle (Meru Prastāra), and a recursive algorithm for computing powers of 2 that's structurally identical to fast exponentiation. Operations: Meru Prastāra generation, binary meter enumeration, Pingala's fast-power algorithm, prosodic pattern counting (which is Fibonacci numbers — Hemachandra discovered them before Fibonacci).

12. **Jain combinatorics and transfinite arithmetic** — Jain mathematicians (~500 BCE – 500 CE) classified infinities into enumerable, innumerable, and infinite categories, with *operations* on these classes. They also computed permutations and combinations independently, including the formula for ⁿCᵣ. The transfinite classification is genuinely different from Cantor's — it's a *three-tier* system rather than a cardinality hierarchy. Operations: Jain infinity class operations (addition/multiplication of classes), Jain factorial/combination formulas, Lokavibhāga calculations.

13. **Catuskoti / Tetralemma logic** (Nagarjuna, ~150 CE) — Four-valued logic from Buddhist philosophy: a proposition can be (1) true, (2) false, (3) both true and false, (4) neither true nor false. This is NOT metaphysical hand-waving — it maps to a specific algebraic structure. The four truth values form a lattice under conjunction/disjunction that is *not* Boolean. It's closer to Belnap's four-valued logic (1977) used in computer science for reasoning with incomplete and inconsistent information. Operations: four-valued truth tables, Catuskoti lattice operations (meet, join, negation), Belnap bilattice construction, evaluation over knowledge states. This connects to paraconsistent logic and database theory.

14. **Navya-Nyāya logic** (Gangesa, ~1300 CE India) — A formal logic system with sophisticated handling of negation, quantification, and property relations. Uses *absence* (abhāva) as a first-class logical object with four subtypes: prior absence, posterior absence, absolute absence, mutual absence. Computable: absence-type classification, property-relation graphs, the Navya-Nyāya negation operator (which is structurally different from both classical and intuitionistic negation), qualifier-qualified relational structures. The treatment of absence as typed and structured has no Western equivalent until much later.

15. **African Sona / Lusona sand drawings** (Chokwe tradition) — Continuous closed curves drawn around grid points that must visit every region exactly once. These are Eulerian paths on dual graphs, but the classification system and construction algorithms developed by Chokwe mathematicians are independent of graph theory. Operations: Sona pattern generation from grid size, Eulerian path construction on dual lattice, monolinearity testing (can the pattern be drawn in one stroke?), symmetry classification. The constraint structure (continuous, closed, visiting all regions) defines a different computational problem from standard Euler paths.

16. **Islamic geometric pattern algebra** — Not just decoration. The classification of planar symmetry groups (all 17 wallpaper groups appear in Islamic art, centuries before the mathematical classification). The *construction algorithms* — using compass and straightedge to generate quasi-crystalline patterns with 5-fold and 10-fold symmetry that were proven to be quasi-periodic only in the 1970s (Penrose). Operations: wallpaper group detection, girih tile operations (the five girih tiles and their substitution rules), quasi-crystalline pattern generation, symmetry group classification from a tiling. Bridges to your quasicrystal entry but from a constructive-geometric rather than algebraic direction.

17. **Yoruba base-20 subtraction arithmetic** — The Yoruba counting system uses both addition and subtraction within place values: 45 is expressed as (60−10−5), i.e., "five taken from ten taken from three twenties." Operations: Yoruba representation computation (expressing any integer as a minimal sum/difference of multiples of 20), comparison of representational efficiency against pure positional systems, minimal-operation decomposition. The *signed-digit representation* is what's interesting — it's structurally related to non-adjacent form (NAF) used in elliptic curve cryptography for efficient scalar multiplication.

18. **Warlpiri kinship algebra** (Australian Aboriginal) — Kinship systems that are formally described as group actions on a set of kin categories. The Warlpiri system forms a dihedral group D₄. Marriage rules define which category pairings are permitted, creating a constraint satisfaction structure. Operations: kinship group multiplication tables, section system composition, moiety/section/subsection classification, marriage rule constraint checking. This is abstract algebra that was being lived as social structure — the group operations are real and computable.

19. **Inka yupana computation** — The yupana is a computational device (not fully decoded but multiple working hypotheses exist) potentially using Fibonacci-base or irregular-base arithmetic. Operations under the Laurencich-Minelli hypothesis: Fibonacci-base representation, Zeckendorf decomposition, irregular-base arithmetic. Even if the historical interpretation is uncertain, Fibonacci-base arithmetic is itself a legitimate and underexplored system with different carry propagation than standard bases.

20. **Bambara divination mathematics** (West Africa) — Binary string generation and transformation (4-bit strings, similar to the 16 figures of geomancy which traveled from West Africa to Europe). The *transformation rules* between figures form a group isomorphic to (Z₂)⁴. Operations: figure generation, XOR-based figure combination (this is literally GF(2)⁴ arithmetic), parity-based classification, transformation group orbit computation. The mathematical content is real — it's computation in a 4-dimensional vector space over GF(2).

The ones with the highest Noesis bridge potential: **Catuskoti/Belnap logic** (connects to paraconsistent reasoning, database theory, and your epistemic honesty problem — what do you do when evidence is contradictory?), **Islamic geometric pattern algebra** (bridges to quasicrystals, wallpaper groups, and substitution tilings), **Egyptian fraction decomposition** (unique constraint structure connecting to additive combinatorics and approximation theory), **Yoruba signed-digit arithmetic** (connects to elliptic curve cryptography and redundant number systems), and **Navya-Nyāya absence logic** (typed negation is structurally distinct from anything in Western logic and connects to the formal logic systems document).

The Catuskoti one in particular — four-valued logic where "both true and false" is a legitimate truth value — might be directly relevant to the epistemic honesty scoring problem in Forge. When a tool encounters contradictory evidence, the correct answer isn't "true" or "false" — it's the third truth value.