




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


What about math in other bases?

This is a deeper question than it looks on the surface. Base choice isn't just representation — it changes which operations are cheap, which patterns are visible, and which number-theoretic structures are natural. There's real math here that most people dismiss as "just notation."

**Non-standard positional bases**

1. **Balanced ternary** (base 3 with digits {−1, 0, 1}) — The Soviets built a computer on this (Setun, 1958). No separate sign bit — negation is just flipping all digits. Rounding is truncation. Comparison is lexicographic. Operations: balanced ternary arithmetic, rounding-by-truncation (this is *not* true in any other base), multiplication via digit-sum (simpler carry propagation), representation efficiency comparison (balanced ternary is provably the most efficient integer base by radix economy — the minimum of n/ln(n) is at e, and 3 is the closest integer). The carry structure is fundamentally different from binary.

2. **Negative bases** (negabinary, base −2) — Every integer, positive and negative, has a unique representation with digits {0, 1} and no sign. Operations: negabinary addition (the carry propagation rules are wild — carries can propagate in *both directions*), negabinary multiplication, conversion between standard binary and negabinary. The fact that you get signed integers for free from unsigned digits is a structural inversion of how we normally think about representation.

3. **Complex bases** (base 2i, base −1+i) — Penney (1965) showed that base (−1+i) represents every Gaussian integer (a+bi where a,b ∈ Z) using only digits {0, 1} with no sign. Operations: complex-base arithmetic, Gaussian integer representation, fractal boundary visualization (the set of numbers representable in [0,1) in base −1+i is a fractal — the twindragon). This means you can do complex arithmetic using only real-valued digit operations. Bridges to fractal geometry and Gaussian integer theory.

4. **Fibonacci base (Zeckendorf representation)** — Every positive integer has a unique representation as a sum of non-consecutive Fibonacci numbers. Digit string over {0,1} with no adjacent 1s. Operations: Zeckendorf encoding/decoding, Fibonacci-base addition (the carry rules involve replacing "011" with "100" — a substitution system), multiplication, connection to golden ratio (the positional weights are powers of φ asymptotically). Bridges to the existing Fibonacci entry but through a radically different door — representation theory rather than recurrence.

5. **Factorial base (factoradic)** — The i-th position has weight i! and digit range [0, i]. So 3!2!1!0! with digits d₃d₂d₁d₀ where d_i ≤ i. Every integer in [0, n!−1] has a unique factoradic representation. Operations: factoradic conversion, *direct computation of permutation from Lehmer code* (the factoradic representation of k gives you the k-th permutation directly — this is the optimal encoding of permutations), factorial-base arithmetic. This is the *natural base for combinatorics* — permutations ARE factoradic numbers.

6. **Primorial base** — Positions weighted by primorials (2, 6, 30, 210, 2310, ...) with digit at position i constrained to [0, p_i − 1]. Operations: primorial encoding, digit pattern analysis (primes have specific fingerprints), relationship to Chinese Remainder Theorem (the primorial representation is essentially the CRT decomposition made positional). Bridges to your CRT entry from the cultural mathematics set.

7. **Mixed-radix / variable-base systems** — Each position has a different radix. Time is mixed-radix: 60-60-24-7-52ish. Operations: generalized mixed-radix arithmetic, optimal mixed-radix selection for a given set of moduli, combinatorial number system (a mixed-radix system for representing combinations). The Mayan calendar system you already have is an instance of this, but the *general theory* of mixed-radix is richer.

8. **Redundant representations** — Allow digits outside the normal range so that representations aren't unique. Example: signed binary (digits {−1, 0, 1}) or carry-save representation. Operations: redundant addition (constant time — no carry propagation!), canonical form extraction, conversion between redundant and non-redundant. This is how real hardware does fast arithmetic. The trade-off between uniqueness and speed of computation is a fundamental structural property. Connects to the Yoruba subtraction arithmetic from the cultural set — that's a redundant signed-digit system discovered independently.

9. **Bijective bases** — Base k using digits {1, 2, ..., k} instead of {0, 1, ..., k−1}. No zero digit. This means every positive integer has exactly one representation with no leading zeros (because there's no zero to lead with). Bijective base-1 is unary. Bijective base-26 is Excel column naming (A=1, B=2, ..., Z=26, AA=27, ...). Operations: bijective-base arithmetic, enumeration properties (there's a clean bijection between strings and positive integers), comparison to standard bases.

10. **Non-integer bases** — Base φ (golden ratio), base e, base π. In base φ, every non-negative integer has a finite representation using only {0,1} with no adjacent 1s — this is *exactly* the Zeckendorf representation. Operations: base-φ arithmetic, the "golden string" (base-φ representation of 1 = 1.0000... = 0.11111... leads to the infinite Fibonacci word), base-e representation (the most "efficient" base in information-theoretic terms), transcendental base representations. Base-φ arithmetic connects Fibonacci sequences to positional notation through the identity φ² = φ+1 which is the carry rule.

11. **p-adic expansions as infinite-left bases** — In p-adic numbers, the expansion goes infinitely to the *left* instead of the right. So ...33334 in base 5 represents −1 (because adding 1 gives ...00000). Operations: p-adic digit computation, infinite-left arithmetic, detecting which rationals have periodic p-adic expansions (all of them — p-adic rationals are eventually periodic, just like real-base rationals), p-adic interpolation. This connects to your existing p-adic entry but the *representation* angle is different from the *norm* angle.

12. **Symmetric representations** — Base 2k+1 with digits {−k, ..., −1, 0, 1, ..., k}. Balanced ternary is the simplest case. Operations: symmetric-base rounding (always truncation), signed-digit multiplication algorithms, redundancy analysis for different base/digit-set combinations. The general theory covers balanced ternary as a special case.

**Base-dependent number theory**

13. **Digit-sum dynamics in arbitrary bases** — Digital root in base b is the iterative digit sum until you reach a single digit. This computes n mod (b−1). Operations: digital root computation, multiplicative digital root (iterate digit *product*), additive/multiplicative persistence (how many iterations to reach a fixed point), persistence records by base. The multiplicative persistence problem is *unsolved* — it's conjectured that no number has multiplicative persistence > 11 in base 10, but nobody can prove it. Different bases have different persistence landscapes.

14. **Automata-theoretic properties of base representations** — A set S of integers is *b-automatic* if the base-b representations of elements of S are recognized by a finite automaton. Cobham's theorem (1969): if S is both b-automatic and c-automatic for multiplicatively independent b and c, then S is ultimately periodic. Operations: automaton construction for number-theoretic sets (powers of 2 in base 10, etc.), Cobham's theorem verification, base-dependent regularity testing. This connects automata theory to number theory through base representation — a bridge the tensor probably doesn't have.

15. **Normal numbers and digit frequency** — A number is normal in base b if every digit (and every k-digit block) appears with equal frequency in its base-b expansion. Almost all real numbers are normal in every base (Borel), but proving normality for specific constants is extremely hard. π is believed normal but this is unproven. Champernowne's number (0.123456789101112...) is provably normal in base 10 but NOT proven normal in base 2. Operations: digit frequency analysis, normality testing (chi-squared on digit blocks), base-dependent normality comparison for mathematical constants, Champernowne construction in arbitrary bases. Bridges to your algorithmic randomness and Kolmogorov complexity entries.

16. **Smith numbers / base-dependent coincidences** — A Smith number is a composite where the digit sum equals the sum of digits of its prime factors. These are entirely base-dependent — 22 is Smith in base 10 (2+2 = 2+2 from 2×11) but not in other bases. Operations: Smith number detection in arbitrary bases, Niven/Harshad numbers (divisible by their digit sum — base-dependent), repunit properties (111...1 in base b = (bⁿ−1)/(b−1) — primality depends on both b and n). The entire zoo of "digit-defined" number classes shifts with base.

17. **Carries as cocycles** — Holte (1997) and others showed that the *carry sequence* when adding two numbers in base b is a cocycle in group cohomology. The probability that adding two random n-digit base-b numbers produces a carry at position k converges to a distribution involving the Bernoulli numbers. Operations: carry sequence extraction, carry correlation computation, carry-as-cocycle construction, connection to H²(Z/bZ, Z). This is a genuinely surprising bridge — *the elementary school operation of carrying digits is secretly a cohomological computation*.

18. **Rauzy fractals and beta-expansions** — For algebraic integers β > 1, the beta-expansion generalizes base representation. The set of numbers with zero fractional part under beta-expansion forms a fractal (Rauzy fractal for the tribonacci constant). Operations: beta-expansion computation, Rauzy fractal boundary generation, Pisot number detection (beta-expansions behave especially well for Pisot numbers), tiling property verification. Bridges number theory to fractal geometry to dynamical systems through base representation.

19. **Two-dimensional / matrix bases** — Represent Gaussian integers in a base that's itself a Gaussian integer. Or represent elements of Z² using a 2×2 matrix as the "base" — the radix is a linear transformation. Operations: matrix-base expansion, digit set tiling (the digits must tile the plane under the matrix action), Haar wavelet connection (Haar wavelets are a base-2 matrix representation), self-affine tile construction. Bridges linear algebra to number representation to wavelet theory.

20. **Residue number systems** — Represent integers by their remainders modulo a set of coprime moduli {m₁, m₂, ..., mk}. Addition and multiplication are *parallel* and *carry-free* — each channel is independent. Division and comparison are *hard*. Operations: RNS encoding/decoding, parallel addition/multiplication, base extension (adding a new modulus channel), overflow detection (this is the hard part), mixed-radix conversion from RNS. This is the CRT turned into a computational architecture. It's actually used in signal processing hardware.

**The meta-mathematical angle**

21. **Base-invariant vs. base-dependent properties** — Some number-theoretic properties are base-invariant (primality, divisibility) and others are base-dependent (palindromicity, digit sum, repunit structure). The *boundary* between these categories is itself interesting. Operations: invariance testing (is property P preserved under base change?), minimal base for a given property (smallest base where n has property P), base-independent canonical forms.

The highest-value entries for Noesis composition: **carries as cocycles** (connects elementary arithmetic to group cohomology — that's a bridge nobody would expect), **complex bases** (fractal boundaries from number representation — connects to fractal dimensions entry), **automata-theoretic properties** (Cobham's theorem connects automata theory to number theory through base representation — a three-way bridge), **factoradic** (the natural encoding of permutations — connects combinatorics to positional notation), and **Rauzy fractals** (base representation → dynamical systems → fractal geometry → algebraic number theory, all in one object).

The carries-as-cocycles result is the one I'd flag especially. If Noesis finds that connection independently — that the carry operation in elementary addition is a group cohomology cocycle — that would be a strong validation that it's surfacing real mathematical structure rather than statistical correlation.



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
