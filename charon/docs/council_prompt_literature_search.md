# Council Prompt: Targeted Literature Search — Faltings Height & Spectral Tail
## For: Perplexity, Gemini Deep Research, Grok
## Context: Pre-publication novelty check, Project Prometheus, 2 April 2026

---

## Purpose

We have two empirical findings that may be novel. Before claiming novelty in a council session or any publication framing, we need to know whether anyone has already reported these results. This is a literature search, not a review. We need citations or their confirmed absence.

---

## Finding 1: Faltings Height Correlates with First L-Function Zero

**Our result:** For 6,036 rank-0 elliptic curves over Q with conductor ≤ 5,000, the partial correlation between Faltings height and the first normalized low-lying zero (γ₁ / log N), after controlling for log(conductor), is r = −0.168 (p = 2.3 × 10⁻³⁹).

The Faltings height is the dominant BSD-adjacent predictor for the first zero's position, exceeding Sha (r = +0.062) and modular degree (r = −0.107).

**Search queries:**
1. Has anyone published a partial correlation between Faltings height and L-function zero positions, for elliptic curves or any family?
2. Watkins (2008), "Some heuristics about elliptic curves" — does this paper or its data tables include Faltings height vs first-zero statistics?
3. Cremona's elliptic curve tables — has the Cremona group published any analysis of Faltings height vs zero distribution statistics?
4. Any paper (2000–2026) that regresses L-function zero positions against arithmetic invariants of elliptic curves, controlling for conductor
5. The Faltings height appears in the BSD formula through the real period Ω (via h_F = (1/2)log(Ω² · Disc)). Has anyone noted that the Ω component of the BSD formula predicts first-zero displacement?
6. arXiv search: "Faltings height" AND ("first zero" OR "low-lying zero" OR "zero distribution")

**What we need:** Either a citation that reports this correlation (in which case we cite it and don't claim novelty) or confirmation that no such measurement appears in the published literature (in which case we flag it as a minor novel finding with appropriate hedging).

---

## Finding 2: The BSD/Tail Wall

**Our result:** BSD invariants (Sha, Faltings height, modular degree, regulator) explain 6.1% of variance in the first L-function zero beyond conductor, but explain 0.01% of variance in zeros 5–20 beyond conductor. The transition is sharp: zero 1 has BSD increment +0.061, zero 2 has +0.001, zeros 3–20 have +0.000.

**Search queries:**
1. Has anyone decomposed L-function zero variance into arithmetic invariant components on a per-zero-index basis?
2. Has anyone demonstrated that BSD invariants predict the first zero but not higher zeros (or vice versa)?
3. Is there a theoretical prediction that BSD invariants should affect only the first zero? The BSD formula connects L'(1) (or L(1)) to the invariants, and the first zero's height determines L(1)'s value. Is this trivially expected?
4. Wachs (2026), "BSD Invariants and Murmurations" — does this paper measure BSD invariant influence on individual zero indices, or only aggregate murmuration statistics?
5. Any paper on "per-eigenvalue" or "per-zero" influence of arithmetic data in random matrix theory or analytic number theory
6. arXiv search: ("BSD invariants" OR "Birch Swinnerton-Dyer") AND ("zero index" OR "individual zeros" OR "zero-by-zero" OR "per-eigenvalue")

---

## Finding 3 (Bonus): Spectral Tail Independence from BSD

**Our result:** After stripping conductor, Sha, Faltings height, modular degree, and regulator, zeros 5–19 still cluster by rank at ARI = 0.55 (z = 74.8 vs permutation null). The spectral tail encodes rank through a mechanism independent of all standard BSD invariants.

**Search queries:**
1. Has anyone claimed or demonstrated that higher L-function zeros carry rank information independent of the BSD formula?
2. The ILS (Iwaniec-Luo-Sarnak 2000) test function support theorem predicts that higher zeros distinguish SO(even) from SO(odd). Has anyone tested this computationally on specific families? Has anyone connected ILS to BSD independence?
3. Has anyone measured "residual rank information" in L-function data after removing known arithmetic invariants?
4. arXiv search: "spectral tail" AND ("rank" OR "L-function" OR "elliptic curve")
5. arXiv search: "ILS" AND ("computational" OR "empirical" OR "test function support") AND ("rank" OR "family discrimination")

---

## Output Format

For each finding, provide one of:
- **KNOWN:** [citation] reports this result. Summary of what they found.
- **PARTIALLY KNOWN:** [citation] reports a related but distinct result. Key differences.
- **NOT FOUND:** No published result matching this description found in the literature as of April 2026.

We will adjust our novelty claims accordingly before the main council session.
