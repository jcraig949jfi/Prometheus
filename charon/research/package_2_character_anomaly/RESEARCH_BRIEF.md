# Research Package 2: The Character Anomaly
## For: Google AI Research Mode
## Priority: HIGH — unexplained finding, contradicts naive theory

---

## What We Found

Among weight-2, dimension-2 modular forms in LMFDB (conductor ≤ 5000),
those with non-trivial nebentypus character are 3.3x more likely to have
zero distributions resembling elliptic curves compared to trivial character forms.

- Non-trivial character dim-2 wt-2: 15.7% have EC in top-10 zero-neighbors
- Trivial character dim-2 wt-2: 4.7% have EC in top-10 zero-neighbors

## Why This Is Puzzling

Under the Katz-Sarnak framework:
- Elliptic curve L-functions have **orthogonal** symmetry (SO(even) or SO(odd))
- Modular forms with trivial character also have orthogonal symmetry
- Modular forms with non-trivial character shift toward **unitary** symmetry (U(N))

Therefore non-trivial character forms should have zero distributions that are
**LESS similar** to elliptic curves, not MORE similar. The 3.3x enrichment
goes in the WRONG direction from naive Katz-Sarnak prediction.

## What We Need From This Research

1. **Is there a known finite-conductor effect where non-trivial character
   modular forms have zero distributions that mimic orthogonal symmetry?**
   At finite conductor, pre-asymptotic effects can dominate. Is this documented?

2. **Do non-trivial character weight-2 dim-2 forms have specific zero repulsion
   patterns near the central point that happen to look like rank-0 EC zeros?**
   The functional equation involving the conjugate character might create
   spacing patterns that accidentally align.

3. **Symmetry type transitions at low conductor:** At conductor ≤ 5000, are
   symmetry type predictions even reliable for dim-2 forms? How many zeros
   are needed before the asymptotic Katz-Sarnak predictions kick in?

4. **The Iwaniec-Luo-Sarnak framework for non-trivial nebentypus:** Do they
   explicitly compute 1-level densities for non-trivial character families?
   What test function support is needed to distinguish these from orthogonal families?

5. **Character twists and zero movement:** When you twist an L-function by a
   character, how do the zeros move? Is there a systematic shift pattern
   that could explain the EC-proximity effect?

## Key Papers to Start From

- Iwaniec, Luo, Sarnak — "Low lying zeros of families of L-functions" (2000)
- Shin, Templier — "Sato-Tate theorem for families" (2016)
- Ricotta, Royer — "Statistics for low-lying zeros of symmetric power L-functions" (2011)
- Any recent work on symmetry type determination at finite conductor

## Attach These Files

- `charon/reports/kill_tests_163_2026-04-02.md` (the character enrichment data)
- `charon/reports/council_review_synthesis.md` (Claude's identification of the anomaly)
