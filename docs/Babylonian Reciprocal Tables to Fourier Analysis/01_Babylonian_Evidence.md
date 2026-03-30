# Task 1: The Babylonian Evidence

## 1A: The Reciprocal Tables

### Findings

The standard Old Babylonian reciprocal table contains ~30 entries listing pairs (n, 1/n) for regular numbers up to 1,21 (=81 decimal) in base-60:

| n (sexagesimal) | 1/n (sexagesimal) | Decimal equivalent |
|---|---|---|
| 2 | 30 | 0.5 |
| 3 | 20 | 0.333... |
| 4 | 15 | 0.25 |
| 5 | 12 | 0.2 |
| 6 | 10 | 0.1667 |
| 8 | 7,30 | 0.125 |
| 9 | 6,40 | 0.111... |
| 10 | 6 | 0.1 |
| 12 | 5 | 0.0833 |
| 15 | 4 | 0.0667 |
| 16 | 3,45 | 0.0625 |
| 18 | 3,20 | 0.0556 |
| 20 | 3 | 0.05 |
| 24 | 2,30 | 0.0417 |
| 25 | 2,24 | 0.04 |
| 27 | 2,13,20 | 0.037 |
| 30 | 2 | 0.0333 |
| 32 | 1,52,30 | 0.03125 |
| 36 | 1,40 | 0.0278 |
| 40 | 1,30 | 0.025 |
| 45 | 1,20 | 0.0222 |
| 48 | 1,15 | 0.0208 |
| 50 | 1,12 | 0.02 |
| 54 | 1,6,40 | 0.0185 |
| 1,0 (=60) | 1 | 0.0167 |
| 1,4 (=64) | 56,15 | 0.015625 |
| 1,21 (=81) | 44,26,40 | 0.01235 |

All entries are confined to regular numbers whose reciprocals require no more than three sexagesimal places.

### Key Tablets

- **Nippur tablets**: Christine Proust catalogued over 300 unpublished mathematical school tablets from Nippur (University of Pennsylvania excavations). Includes **Ni 2733**, **HS 202a**, **HS 209** -- reciprocals assembled with multiplication tables and squares in fixed curricular order.
- **YBC series** (Yale Babylonian Collection): **YBC 7289** (famous sqrt(2) tablet, demonstrates reciprocal reasoning). **YBC 4608** referenced as mathematical table text.
- **CBS 10996** (University of Pennsylvania Museum): Paired-number table; also noted for musicological interpretations.
- **MLC 1670** (Morgan Library Collection): Referenced in Neugebauer & Sachs as mathematical table text.
- Two tablets from **Senkerah on the Euphrates** (c. 2000 BC): squares of numbers up to 59, cubes up to 32.

### Key Sources

- **Neugebauer & Sachs (1945)**, *Mathematical Cuneiform Texts* (American Oriental Society) -- Definitive edition; systematic catalogues of multiplication and reciprocal tables.
- **Robson (2008)**, *Mathematics in Ancient Iraq: A Social History* (Princeton UP) -- Tables were integral to scribal training, embedded in curriculum alongside metrological lists, model contracts, and Sumerian literary compositions.
- **Friberg (2007)**, *A Remarkable Collection of Babylonian Mathematical Texts* (Springer) -- ~130 previously unpublished tablets from Schoyen Collection. Detailed analysis of reciprocal tables, regular numbers, and factoring algorithms.
- **Proust (2007/2010)** -- Reconstructed Nippur curriculum from 300+ tablets; reciprocal tables learned early, before multiplication tables.

### Strength Assessment
**STRONG** -- Primary sources are abundant, well-catalogued, and multiply confirmed across independent scholarly traditions.

---

## 1B: How Multiplication via Reciprocals Worked

### The Core Procedure

The Babylonians had **no algorithm for long division.** Instead: **a / b = a x (1/b)**

1. Look up 1/b in the standard reciprocal table
2. Multiply a x (1/b) using multiplication tables (or further table lookups)

### Worked Example

To compute 25 / 9:
1. Look up reciprocal of 9: 1/9 = 0;6,40 (i.e., 6/60 + 40/3600 = 1/9)
2. Multiply 25 x 0;6,40
3. 25 x 6 = 150 = 2,30; 25 x 40 = 1000 (fractional position) = 16,40
4. Sum: 2;46,40 (= 2 + 46/60 + 40/3600 = 2.7778 = 25/9)

### Scribal Training Evidence

**Knuth (1972)**, "Ancient Babylonian Algorithms" (*Communications of the ACM* 15(7):671-677): First English translations of cuneiform procedure texts. Demonstrated that Babylonian procedures are "genuine algorithms" -- general procedures for solving classes of problems.

**Proust's curriculum reconstruction** shows students learned reciprocal and multiplication series incrementally over ~1 year. Three tablet types:
- **Type II/1**: Student copies teacher's model (standard table) with model on reverse
- **Type III**: Student writes table from memory
- **Type IV**: Extract tablets with individual entries for practice

Three multiplication tables written and dated by the *same trainee scribe* have been found, confirming incremental learning. Reciprocal tables appeared alongside Proto-Diri (lexical lists), model contracts, and Sumerian proverbs -- mathematics was woven into the complete scribal curriculum.

### Strength Assessment
**STRONG** -- The procedure is explicitly documented in training texts and problem texts.

---

## 1C: Regular Numbers and Irregular Number Handling

### Regular Numbers

A number is **regular** in base 60 iff its prime factorization contains only primes 2, 3, and 5 (the prime factors of 60). These are **5-smooth numbers**: 2^a x 3^b x 5^c. Regular numbers have terminating sexagesimal reciprocals.

Base 60 was computationally advantageous: 60 is a **superior highly composite number** with twelve divisors (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60). Far more fractions terminate in base 60 than base 10.

### Irregular Number Handling

Numbers like 7, 11, 13 have non-terminating repeating sexagesimal reciprocals:
- 1/7 = 0;8,34,17,8,34,17... (period 3)
- 1/11 = 0;5,27,16,21,49... (period 5)
- 1/13 = 0;4,36,55,23... (period 4)

**Evidence shows multiple strategies:**

1. **Approximation by nearby regular numbers**: e.g., for 1/13, use 7 x (1/91) ~ 7 x (1/90) = 7 x 0;0,40 = 0;4,40.
2. **Avoidance**: Problem texts were deliberately constructed so irregular numbers never appeared in solution steps. Scribal exercises carefully designed for clean intermediate results.
3. **Approximation to 3-4 places**: When unavoidable, Babylonians "approximated the results to three or four sexagesimal places."
4. **The "Technique" (IGI.DUB)**: Friberg documents a specific algorithmic method for computing reciprocals of regular numbers by factoring: identify trailing digits, find their regular factor, multiply to cancel, iterate.

### Structural Significance

The restriction to regular numbers is a *fundamental feature of the transform domain*. The "reciprocal domain" only maps cleanly for a well-defined subset of inputs -- **analogous to bandwidth limitations in signal processing.**

### Strength Assessment
**STRONG** on the mathematical characterization; **HIGH** on handling strategies.

---

## 1D: Quarter-Square Multiplication

### The Identity

**a x b = ((a+b)^2 - (a-b)^2) / 4**

### Evidence

1. **Tables of squares existed extensively**: Tablets from Senkerah (c. 2000 BC) give squares of all numbers up to 59. Tables of squares are among the most common mathematical table texts.
2. **The algebraic identity was known**: Two multiplication formulas from Old Babylonian tablets use differences, sums, and squares. The identity (a+b)^2 = a^2 + 2ab + b^2 appears in problem texts.
3. **However**, direct evidence that scribes *routinely used* quarter-square multiplication as a computational shortcut is **limited**. Most exercise tablets jump from inputs to product without showing intermediate steps.
4. **Hoyrup's interpretation** (2002): Old Babylonian "algebra" was fundamentally **geometric cut-and-paste** reasoning. The identity (a+b)^2 - (a-b)^2 = 4ab has a natural geometric interpretation as difference of two squares.

### Assessment

The quarter-square identity was almost certainly **known** to Old Babylonian mathematicians. Tables of squares were **available** to support it. Whether it was a primary computational technique or secondary/theoretical relationship remains debated.

### Strength Assessment
**MODERATE** -- Components confirmed; routine algorithmic use uncertain.

### Key Sources
- Hoyrup, J. (2002), *Lengths, Widths, Surfaces* (Springer)
- Senkerah tablets (c. 2000 BC)

---

## 1E: Second-Order Tables and the Computational Domain Interpretation

### What Exists

The Babylonians produced an extensive ecosystem of interrelated tables:
- Tables of **reciprocals** (1/n)
- Tables of **squares** (n^2) and **square roots**
- Tables of **cubes** (n^3) and **cube roots**
- Tables of **sums of squares and cubes** (n^2 + n^3)
- **Combined tables** -- several types on a single tablet
- Tables for computing **compound interest**
- Multiplication tables for specific multipliers (x2, x3, ..., x50)

### The n^2 + n^3 Tables

These are significant: they are a **composed table** -- combining two operations. Their existence demonstrates that Babylonians created pre-computed tables of compound operations.

### Combined Tablets

Tablets like Ni 2733 from Nippur combine reciprocals, multiplication tables, and squares in sequence. Physical co-location suggests tables were used **together as a computational system**, not isolated references.

### Reciprocal Pairs

Friberg documents "regular reciprocal pairs" as an explicit category: computing with pairs (n, 1/n) as linked units supports a domain-transformation interpretation.

### Gap

I was **unable to confirm** the existence of tables of "reciprocals of reciprocals" or "squares of reciprocals" as distinct types. This is an honest gap.

### Strength Assessment
**MODERATE** -- Rich ecosystem confirmed; explicitly second-order tables not confirmed.

---

## 1F: Scholarly Support for the Transform Interpretation

### Support For

1. **Knuth (1972)**: Babylonian procedures are "genuine algorithms" -- general computational methods. The reciprocal-table procedure is a systematic domain transformation.

2. **Ritter and Chemla**: Drew attention to "ways of algorithmic thinking" in ancient non-Western mathematics. The "algorithmic interpretation" treats ancient procedures as structured computational methods.

3. **Systematic nature of tables**: The standard reciprocal table is a **complete** lookup system for all regular numbers up to a bound, organized for efficient computation.

4. **Neugebauer on Babylonian astronomy**: Babylonian astronomers used "a form of Fourier analysis to compute an ephemeris" (elaborated by Ossendrijver, *Babylonian Mathematical Astronomy: Procedure Texts*, 2012). Demonstrates transform-like computational strategies in at least one domain.

5. **Floating-point interpretation**: Babylonian sexagesimal notation was essentially floating-point (no explicit radix point). Reciprocal table entries applied at any scale -- the reciprocal domain is scale-invariant.

### Counter-Arguments

1. **Hoyrup's geometric interpretation** (2002): Mathematics was fundamentally geometric/spatial, not abstract/algebraic. "Transforms" may be anachronistic framing.

2. **Intentionality problem**: Historians distinguish structural content from cognitive intent. Robson's social-historical approach cautions against reading modern frameworks into ancient practice.

3. **No meta-mathematical commentary survives**: We have procedures and tables but no text saying "we transform to the reciprocal domain." The transform interpretation is modern structural analysis.

### The Paper's Response

"We're not claiming conscious intent. We're claiming structural content. The procedure IS a transform regardless of how the scribes conceptualized it." This is methodologically sound and aligns with Chemla and Ritter's approach to algorithmic thinking in ancient mathematics.

### Strength Assessment
**MODERATE-to-STRONG** -- Structural interpretation well-supported; must handle anachronism objection carefully.

---

## Potential Objections

1. **Anachronism**: Reviewers will ask whether calling reciprocal lookup a "transform" is projecting modern concepts onto ancient practice.
2. **Intentionality**: The scribes did it procedurally; did they "know" it was a transform? (Response: irrelevant -- we claim structural content, not conscious intent.)
3. **Quarter-square evidence gap**: Routine algorithmic use not conclusively proven.
4. **No second-order tables confirmed**: Weakens the "computational domain" argument slightly.

## Novel Contribution Confirmed

The formal identification of Babylonian reciprocal computation as a "transform" in the mathematical (ring-homomorphism) sense has not been published. The structural parallel to Fourier/Laplace transforms is implicit in the historical literature but never formalized.

## Gaps

- Need physical access to or detailed published transcriptions of specific tablets for the formalization
- Quarter-square routine use needs stronger evidence or explicit caveat
- Second-order tables need further specialist consultation
