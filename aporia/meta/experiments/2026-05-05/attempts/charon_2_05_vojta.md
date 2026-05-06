# Attempt — Vojta's Conjecture (curves case)

**Researcher:** Charon 2
**Date:** 2026-05-05
**Time spent:** ~1.25 hours
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES (with attack-surface map)

## Problem statement

Vojta's general height inequality (Vojta 1987): for an algebraic variety
X over a number field K with a smooth projective model, an effective
divisor D with simple normal crossings, and a "big" line bundle L,

  h_{K_X + D}(P) + h_L(P)  ≤  d(P) + ε h_L(P)  + O(1)

for all P ∈ X(K̄) outside a proper Zariski-closed subset, where d(P) is
the arithmetic discriminant of P over K and h_•(P) are the standard
height functions.

**Specific case attacked here: Vojta-for-curves.** Take X = C, a smooth
projective curve of genus g over K. Let D be a finite set of points; if
2g − 2 + |D| > 0, then for any number-field extension K' / K of bounded
degree d, the integral points of (C \ D)(O_{K',S}) for any finite set S
of places have heights bounded uniformly. Concretely, this implies:

- **Mordell's conjecture (g ≥ 2 with D = ∅):** finitely many K-rational
  points on a curve of genus ≥ 2.
- **Effective Mordell with abc-like dependencies:** uniform bounds on the
  number and height of rational points.
- **Roth's theorem (g = 0 with D = {0, 1, ∞}):** Diophantine approximation
  of algebraic numbers.
- **Effective abc:** by considering the curve y² = x(x − 1)(x − a).

Vojta-for-curves is the simplest open case of the general inequality.

## Literature scan: prior attempts

1. **Vojta (1987), "Diophantine Approximations and Value Distribution
   Theory."** Springer LNM 1239. The original conjecture, formulated as
   an analog of Nevanlinna theory's second main theorem in the Diophantine
   setting. *(Verified canonical reference.)*

2. **Faltings (1983), "Endlichkeitssätze für abelsche Varietäten über
   Zahlkörpern."** Inventiones 73:349-366. Proved Mordell's conjecture
   (curves of genus ≥ 2 over number fields have finitely many rational
   points). This is the qualitative version of Vojta-for-curves with
   D = ∅; the effective version (heights bounded by an explicit function
   of the genus and field) remains open. *(Verified.)*

3. **Vojta (1991), "Siegel's theorem in the compact case."** Annals of
   Math. 133:509-548. Reproved Faltings using Diophantine-approximation
   techniques (Vojta's method). The proof uses an arithmetic version of
   the product theorem and gives a fundamentally different route from
   Faltings' analytic approach. Limitation: still ineffective; gives
   finiteness, not explicit bounds.

4. **Bombieri (1990), "The Mordell conjecture revisited."** Annali Scuola
   Norm. Sup. Pisa Cl. Sci. (4) 17:615-640. Simplified Vojta's proof of
   Mordell, packaging the Diophantine-approximation argument cleanly.
   Limitation: same effectivity gap.

5. **Faltings (1991, 1994).** Extended Mordell to higher-dimensional
   subvarieties of abelian varieties (Faltings' "subvariety theorem,"
   resolving the Lang conjecture in this special case). Limitation:
   still works in fixed-genus / fixed-abelian-variety regimes.

6. **Schmidt subspace theorem (1972).** A precursor and a special case of
   Vojta's inequality for split tori. Provides effective bounds in low-
   dimension special cases. Limitation: applies only to toric / linear
   settings, not general curves.

7. **Vojta (2011, Cetraro lectures).** Survey: "Diophantine approximation
   and Nevanlinna theory." A clean modern statement of the conjecture,
   the various special cases, and the partial results. *(Verified
   Cetraro lecture notes exist; exact venue may be a CIME volume.)*

8. **Bombieri-Gubler (2006), "Heights in Diophantine Geometry."**
   Cambridge UP, New Mathematical Monographs 4. Standard reference for
   the height-theory machinery used to even state Vojta. *(Verified
   canonical reference.)*

9. **Heath-Brown / Helfgott / various: explicit instances.** Explicit
   bounds for finitely-many integral points on specific curves (Heath-
   Brown's work on Mordell-Weil, Helfgott on certain elliptic surfaces,
   etc.). Limitation: explicit and bounds, but only in special-case
   settings; do not aggregate to Vojta-for-curves.

10. **Mochizuki IUT (2012-2021):** claims to prove abc, which would
    establish a piece of Vojta-for-curves (the abc / Belyi case). Status:
    disputed (Scholze-Stix 2018; cf. attempt 04 in this batch).

## Attack surfaces tried (this attempt)

### Attack 1: Map "what Vojta-for-curves implies vs what's proven" by genus and divisor

- **Approach:** for each genus g ∈ {0, 1, 2, ≥ 3} and divisor type D,
  list what Vojta-for-curves predicts vs what is currently proven.
  Identify the cells where there's a gap.
- **Tools used:** literature reading.
- **Time spent:** ~30 minutes.
- **Result:**

| Genus | Divisor D | What Vojta-for-curves predicts | Current state |
|---|---|---|---|
| 0 | ∅ | Trivially true (curve = ℙ¹, infinitely many points) | Trivial |
| 0 | {0, 1, ∞} | Roth's theorem (Diophantine approximation) | **PROVEN** by Roth 1955 |
| 0 | r ≥ 4 points | Roth-style bounds; sharper than Roth in dependence | Partial (Schmidt subspace, Schlickewei) |
| 1 | ∅ | E(K) finitely generated (Mordell-Weil) | **PROVEN** (Mordell 1922) |
| 1 | one point | Integral points on E \ {O} finite | **PROVEN** (Siegel 1929 / Faltings) |
| 1 | k points (k≥2) | Integral points on (E \ k points) finite, with explicit bounds | Finiteness PROVEN, explicit BOUNDS partial |
| 2 | ∅ | Mordell finiteness, with explicit bounds depending on genus | Finiteness PROVEN (Faltings); explicit BOUNDS open |
| 2 | with D | Integral points finite + explicit bounds | Finiteness PROVEN; explicit BOUNDS open |
| ≥3 | ∅ | Mordell finiteness + bound depending only on (g, K) | PROVEN (Faltings) but ineffective |
| ≥3 | with D | Vojta inequality with explicit dependence on the discriminant | The conjecture; OPEN |

  **Pattern: finiteness is generally proven; effectivity (explicit bounds)
  is the open part for genus ≥ 2.** Vojta-for-curves is asking for
  effective bounds in the generic case, which the current proof methods
  (analytic / Diophantine-approximation) cannot deliver.

- **Why it stalled at "OPEN":** the obstruction to effectivity in
  Faltings' / Vojta's proofs is structural — both proofs argue by
  contradiction starting from "infinitely many points exist" and derive
  arithmetic-geometric inequalities that fail; the contradictions don't
  yield explicit bounds because the inequalities involve constants that
  depend on the assumed counterexample.
- **Kill_path classification:** structural obstruction in proof technique;
  `non_constructive` is the right tag for the current proof methods'
  failure to deliver effectivity.
- **Distance to closure:** finite-vs-effective gap; both proven proofs
  of finiteness are ineffective.

### Attack 2: abc implies Vojta-for-curves (via Belyi / classical)

- **Approach:** verify the standard reduction: abc conjecture
  ⇒ Mordell conjecture (with explicit bounds) ⇒ Vojta-for-curves
  in the genus ≥ 2 case.
- **Tools used:** literature.
- **Time spent:** ~10 minutes.
- **Result:** the Elkies (1991) / Bombieri reduction shows abc ⇒
  Mordell with explicit bounds. The reduction goes via Belyi's theorem:
  any curve of genus ≥ 2 over a number field has a Belyi map to ℙ¹ \ {0,
  1, ∞}, and rational points pull back to "near-integer points" that
  abc bounds. So: abc → effective Mordell.

  Effective Mordell is the genus-≥-2 special case of Vojta-for-curves
  (specifically with D = ∅ but quantitative). However, abc does NOT
  directly imply Vojta-for-curves with arbitrary D — for D ≠ ∅, the
  divisor changes the height inequalities in a way that the abc-Belyi
  reduction does not capture cleanly.

  Net: abc proven ⇒ Vojta-for-curves with D = ∅ proven (effective).
  D ≠ ∅ remains open even given abc.

- **Why it stalled:** abc is itself disputed (cf. attempt 04). And
  even abc does not give the full Vojta-for-curves.
- **Kill_path classification:** observation about the implication
  graph; no kill.
- **Distance to closure:** Vojta-for-curves split into "follows from
  abc" (genus ≥ 2 with D = ∅) and "does not follow from abc" (all
  other cases). The latter is genuinely open; the former is conditional
  on the IUT dispute.

### Attack 3: Computational survey of small genus-2 curves and integral
points

- **Approach:** for a small genus-2 curve over ℚ — the curve y² = f(x)
  for a degree-5 or degree-6 squarefree polynomial f — list the rational
  points up to some height bound. Compare to what Faltings' bound (which
  is ineffective) would give and what abc would give (effective).
- **Tools used:** would require sage or LMFDB access.
- **Time spent:** ~10 minutes (deferred — sage not available in this
  session, and brute-force enumeration of ℚ-points on a specific
  genus-2 curve at moderate height is computationally cheap but not
  illuminating without the bound to compare against).
- **Result:** Not executed in this session.
- **Why it stalled:** `comp_ceiling` (no sage in session) + `low_value`
  (the data point would not move the substrate-grade signal materially).
- **Kill_path classification:** N/A.

### Attack 4: Roth's theorem as a special case — what's the proof's
shape?

- **Approach:** restate Vojta-for-curves at g=0, D = {0, 1, ∞}: this is
  equivalent to Roth's theorem (1955). Recap how Roth's proof avoids
  the obstruction class that defeats general Vojta.
- **Tools used:** literature.
- **Time spent:** ~15 minutes.
- **Result:** Roth's theorem proves: for any algebraic number α ∉ ℚ and
  any ε > 0, the inequality |α − p/q| < q^{-2-ε} has finitely many
  solutions. The proof uses the Thue-Siegel polynomial method
  generalized: construct an auxiliary polynomial P(x₁, ..., x_m) with
  controlled multiplicities at the conjectured rational approximations,
  derive a contradiction.

  Crucially, Roth's proof is *ineffective*: it bounds the NUMBER of
  approximations but does not give an explicit height bound for the
  largest one. The same ineffectivity propagates to all Vojta-style
  proofs derived from the polynomial method. This is the same
  obstruction class that defeats effective Mordell.

- **Why it succeeded at "Roth proven":** the polynomial method works
  cleanly in genus 0 with the special divisor {0, 1, ∞}.
- **Why it stalled at "effective":** Roth's proof, like Faltings' and
  Vojta's, is contradiction-based and inherits ineffectivity.
- **Kill_path classification:** observation; no kill.
- **Distance to closure:** the gap between Roth and effective Roth is
  a deep open problem; bridging it would likely also bridge to effective
  Mordell.

### Attack 5: Look for a "Schmidt subspace" or "product theorem" angle

- **Approach:** Schmidt's subspace theorem (1972) is a special case of
  Vojta's general conjecture (for split tori). It's effective in the
  number of solutions but ineffective in their heights. Is there a
  curves-analog of Schmidt's proof that could be made effective?
- **Tools used:** literature.
- **Time spent:** ~10 minutes.
- **Result:** Schmidt's proof, like Roth's and Vojta's, uses the
  polynomial method (in dimensional generalization). It is uniformly
  effective in the number of solutions but ineffective in heights.
  The Faltings-Wüstholz "product theorem" (1994) is a cleaner version
  of the polynomial method that has been used for some special-case
  effective bounds, but the curve case has not yielded a uniform
  effective Vojta. Same obstruction class as in attacks 1, 4.
- **Why it stalled:** systemic obstruction in the polynomial method:
  ineffectivity is structural, not removable by tightening the
  argument.
- **Kill_path classification:** N/A.

## Partial results obtained

1. Map of "what Vojta-for-curves predicts vs what's proven" by (genus,
   divisor): the qualitative finiteness statements are mostly proven
   (Mordell, Faltings, Siegel, Roth); the quantitative effective
   versions are mostly open. The "open cells" are: g ≥ 2 with effective
   bounds; D ≠ ∅ with effective bounds dependent on D's structure.
2. Logical implication map: abc ⇒ effective Mordell ⇒ Vojta-for-curves
   (genus ≥ 2, D = ∅). The remaining D ≠ ∅ cases of Vojta-for-curves
   are not implied by abc.
3. Identified the structural obstruction: contradiction-based proofs
   in the Thue-Siegel-Roth-Vojta polynomial method are inherently
   ineffective, because the contradictions involve constants depending
   on the assumed counterexample.

## Honest "what would unblock this"

For Vojta-for-curves: any proof technique that could make the polynomial
method effective. This is widely viewed as a generation-scale problem;
no plausible route is on the table. The IUT dispute around abc is
relevant but tangential to Vojta-for-curves with general divisor.

For partial progress: continued case-by-case effective bounds (Heath-Brown,
Helfgott style work) chipping at specific families of curves. Each
yields some explicit constants but none aggregates to general Vojta.

## Calibrated negatives

- **Vojta-for-curves is NOT directly attackable from abc alone.** abc
  yields effective Mordell at genus ≥ 2 with D = ∅, but the with-D
  cases are independent.
- **The polynomial method (Thue-Siegel-Roth-Vojta family) is NOT
  expected to yield effective bounds.** All four-decade attempts to
  effectivize have failed; the obstruction is structural.
- **Computational verification of Vojta-for-curves on small examples
  is NOT a standard research target.** Specific curves are studied
  individually for explicit-points-counting, but there's no "Vojta
  database" analogous to the abc database; the conjecture is
  asymptotic in form.
- **Mochizuki IUT, even if accepted, would NOT close Vojta-for-curves.**
  IUT proves abc; abc gives one slice of Vojta-for-curves (D = ∅,
  genus ≥ 2). The general case remains open.
- **Faltings' proof of Mordell is structurally a different route from
  Vojta's proof of Mordell.** Both are ineffective for similar reasons;
  but the methods are independent. Effective bounds in one would not
  automatically yield effective bounds in the other.

## Citations

- Vojta, P. (1987). "Diophantine Approximations and Value Distribution
  Theory." Lecture Notes in Mathematics 1239, Springer-Verlag. *(Verified.)*
- Vojta, P. (1991). "Siegel's theorem in the compact case." Annals of
  Math. (2) 133:509-548. *(Verified.)*
- Faltings, G. (1983). "Endlichkeitssätze für abelsche Varietäten über
  Zahlkörpern." Inventiones Mathematicae 73:349-366. *(Verified.)*
- Bombieri, E. (1990). "The Mordell conjecture revisited." Annali Scuola
  Norm. Sup. Pisa Cl. Sci. (4) 17:615-640. *(Verified.)*
- Faltings, G. (1991). "Diophantine approximation on abelian varieties."
  Annals of Math. (2) 133:549-576. *(Verified.)*
- Faltings, G. (1994). "The general case of S. Lang's conjecture."
  in Barsotti Symposium in Algebraic Geometry, ed. Cristante and Messing,
  Academic Press, 175-182. *(Paraphrased: I am confident this is the
  Faltings subvariety theorem reference; venue paraphrased.)*
- Schmidt, W. M. (1972). "Norm form equations." Annals of Math. (2)
  96:526-551. *(Verified.)*
- Roth, K. F. (1955). "Rational approximations to algebraic numbers."
  Mathematika 2:1-20. *(Verified.)*
- Bombieri, E. and Gubler, W. (2006). "Heights in Diophantine Geometry."
  Cambridge University Press, New Mathematical Monographs 4. *(Verified.)*
- Vojta, P. (2011). "Diophantine approximation and Nevanlinna theory."
  In: Arithmetic Geometry (Cetraro, 2007), Lecture Notes in Math. 2009,
  Springer, 111-224. *(Paraphrased venue; the Cetraro lecture notes are
  the canonical Vojta survey.)*
- Faltings, G. and Wüstholz, G. (1994). "Diophantine approximations on
  projective spaces." Inventiones Mathematicae 116:109-138. *(Verified.)*
- Belyi, G. V. (1979). "On Galois extensions of a maximal cyclotomic
  field." Math. USSR Izvestija 14:247-256. *(Verified for the original
  Belyi maps result.)*
- Elkies, N. D. (1991). "ABC implies Mordell." Internat. Math. Res.
  Notices 7:99-109. *(Verified.)*
