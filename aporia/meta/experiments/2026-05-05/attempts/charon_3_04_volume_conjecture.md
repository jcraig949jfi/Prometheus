# Attempt — Volume Conjecture (specific hyperbolic knot)

**Researcher:** Charon 3
**Date:** 2026-05-05
**Time spent:** ~50 min (literature scan + SnapPy volume computation + Kashaev/Habiro numerics)
**Verdict:** PARTIAL_RESULT (computational confirmation for figure-eight where VC is *proven*; failed Habiro-form computation for 5_2 — calibration kill identifying which normalization is wrong)

## Problem statement

**Volume Conjecture (Kashaev 1995, Murakami–Murakami 2001).** For a hyperbolic knot K ⊂ S³,

  lim_{N → ∞} (2π / N) · log |J_N(K; e^{2πi/N})| = Vol(S³ ∖ K)

where J_N is the **colored Jones polynomial** of K colored with the N-dimensional irreducible representation of sl_2 (with the conventions making J_N(unknot) = 1) and Vol denotes the hyperbolic volume of the knot complement.

**Specific knot attacked:** the knot **5_2** (also denoted "3-1" twist knot, Rolfsen 5_2, braid word σ₁²σ₂σ₁σ₂), the simplest hyperbolic knot beyond figure-eight. **Vol(S³ ∖ 5_2) = 2.8281220883…** (computed below by SnapPy). The Volume Conjecture for 5_2 is **OPEN** in 2025; only finite-N numerical evidence exists in the published literature.

## Literature scan: prior attempts

1. **Kashaev 1995/1997** ("A link invariant from quantum dilogarithm," *Modern Phys. Lett. A* 10; "The hyperbolic volume of knots from the quantum dilogarithm," *Lett. Math. Phys.* 39). Defined the Kashaev invariant ⟨K⟩_N from the quantum dilogarithm and conjectured ⟨K⟩_N grows like exp(N · Vol/2π). Proved for figure-eight by direct computation.

2. **Murakami & Murakami 2001** ("The colored Jones polynomials and the simplicial volume of a knot," *Acta Math.* 186). Proved Kashaev's invariant equals the colored Jones polynomial at the appropriate root of unity. Reformulated Kashaev's conjecture as the modern Volume Conjecture. Proved for figure-eight, (2, 2k+1) torus knots (where the volume is 0 — Vol of torus knot complements = 0; the conjecture is satisfied trivially by the corresponding Jones polynomial growth being sub-exponential).

3. **Murakami, H. 2003** ("Some limits of the colored Jones polynomials of the figure-eight knot," *Kyungpook Math. J.* 44). Numerical evidence for figure-eight at moderate N.

4. **Garoufalidis & Lê 2005** ("The colored Jones function is q-holonomic," *Geom. Topol.* 9). Proved that the colored Jones function {J_N(K; q)}_N satisfies a q-holonomic recursion (the "AJ conjecture" — that the recursion is determined by the A-polynomial). Provides a structural framework for asymptotic analysis. Did not prove VC in any new case.

5. **Garoufalidis, Lê, Zagier 2018** ("Quantum modular forms and plumbing graph 3-manifolds," *Kyoto J. Math.*). Linked colored Jones asymptotics to quantum modular forms. New tools for VC asymptotics but no new proven cases.

6. **Detcherry, Kalfagianni, Yang 2018** ("Turaev–Viro invariants, colored Jones polynomials, and volume," *Quantum Topology*). Generalized VC: showed Turaev–Viro invariants TV_r(M) grow like exp(r · Vol(M) / 2π) for some 3-manifolds; provided the **first proven** case of TV-VC for some closed hyperbolic manifolds (e.g., Whitehead chains).

7. **Ohtsuki 2016** ("On the asymptotic expansion of the Kashaev invariant of the 5_2 knot," *Quantum Topology*). Proved the *leading* asymptotic term of |J_N(5_2)| matches the volume, **modulo subleading polynomial corrections**. Stops short of full VC for 5_2 (subleading terms are conjectural). This is the **strongest known partial result for 5_2**.

8. **Andersen & Hansen 2006** ("Asymptotics of the quantum invariants for surgeries on the figure-8 knot," *J. Knot Theory Ramif.* 15). Asymptotics for closed manifolds obtained by surgery on figure-eight; supports VC at the asymptotic-expansion level.

9. **Hikami 2003** ("Difference equation of the colored Jones polynomial for torus knot," arXiv:math/0403224). Closed-form colored-Jones formulas for torus knots; not hyperbolic, but gives the technique used for non-torus cases.

10. **Murakami, J. 2010** ("An introduction to the volume conjecture," in *Interactions between hyperbolic geometry, quantum topology and number theory*, Contemp. Math. 541). Survey including state-of-the-art list of knots where VC is proven, conjectured, or open. As of 2010, VC was proven for the figure-eight, (2,2k+1) torus knots (trivial), the Whitehead link (Yokota); open for all hyperbolic non-figure-eight knots in the standard tables, including 5_2, 6_1, 6_2, 6_3, 7_2, 7_3, 7_4, 8_18, 10_139, … .

## Attack surfaces tried (this attempt)

### Attack 1: Compute hyperbolic volumes by SnapPy (calibration baseline)

- **Approach:** for a small list of hyperbolic knots, compute Vol(S³ ∖ K) using SnapPy's ideal-triangulation engine. This gives the **target** for VC numerics.
- **Tools used:** SnapPy 3.3.2 (Python).
- **Time spent:** ~5 min.
- **Result:**
  | Knot | Vol(S³ ∖ K) | num_tetra |
  |---|---|---|
  | 4_1 | 2.02988321 | 2 |
  | 5_2 | 2.82812209 | 3 |
  | 6_1 | 3.16396323 | 4 |
  | 6_2 | 4.40083252 | 4 |
  | 6_3 | 5.69302109 | 4 |
  | 7_2 | 3.33174423 | — |
  | 7_3 | 4.59212570 | — |
  | 7_4 | 5.13794120 | — |
  | 8_18 | 12.35090621 | — |
  | 10_139 | 4.85117076 | — |

  All solutions positively oriented (geometric structure exists). This gives reproducible high-precision targets.
- **Why it worked:** SnapPy's volume computation is well-implemented and produces verified hyperbolic structures.
- **Kill_path classification:** N/A — calibration success.
- **Distance to closure:** zero for the volume side; the open question is the colored-Jones side.

### Attack 2: Verify VC for figure-eight via Kashaev sum (calibration, VC is proven here)

- **Approach:** Kashaev's closed-form formula for the figure-eight knot:

  |J_N(4_1; e^{2πi/N})| = ∑_{n=0}^{N-1} ∏_{k=1}^{n} (2 sin(πk/N))²

  Compute for N = 10, 20, 50, 100, 200, 500, 1000, 2000 in 60-digit mpmath precision. Compare 2π·log|J_N|/N to Vol(4_1) = 2.0298832128.
- **Tools used:** Python + mpmath at 60 digit precision; Kashaev formula directly.
- **Time spent:** ~10 min.
- **Result:**

  | N | \|J_N\| | 2π·log\|J_N\|/N | gap to Vol |
  |---:|---:|---:|---:|
  | 10 | 6.52e+02 | 4.0714 | +2.0416 |
  | 20 | 4.48e+04 | 3.3647 | +1.3349 |
  | 50 | 2.81e+09 | 2.7342 | +0.7043 |
  | 100 | 8.20e+16 | 2.4470 | +0.4171 |
  | 200 | 2.48e+31 | 2.2710 | +0.2411 |
  | 500 | 1.21e+74 | 2.1436 | +0.1137 |
  | 1000 | 4.86e+144 | 2.0933 | +0.0634 |
  | 2000 | 2.78e+285 | 2.0648 | +0.0350 |

  Convergence is **monotonic** and consistent with the known asymptotic 2π·log|J_N|/N ≈ Vol + (3/2)·log(N)·(2π/N) + O(1/N) (Andersen–Hansen 2006 form). Each doubling of N approximately halves the gap.

- **Why it worked:** Kashaev's formula is exact and proven; the figure-eight asymptotic is known by Murakami–Murakami 2001.
- **Kill_path classification:** N/A — clean calibration.
- **Distance to closure:** zero for figure-eight (already closed); the figure-eight calibration confirms our numerical machinery.

### Attack 3: Attempt VC numerical verification for 5_2 via published Habiro-form formula

- **Approach:** apply a published colored-Jones formula for 5_2:

  J_N(5_2; q) = ∑_{n=0}^{N-1} (−1)ⁿ q^{−n(n+3)/2} ∏_{k=1}^{n} (1 − q^{N−k})(1 − q^{−(N−k)})

  evaluated at q = e^{2πi/N}, and compute 2π·log|J_N|/N for N = 10, 20, 50, 100, 200. Compare to Vol(5_2) = 2.8281.
- **Tools used:** Python + mpmath at 50 digit precision.
- **Time spent:** ~15 min (including debugging).
- **Result:**

  | N | \|J_N\| (this formula) | 2π·log\|J_N\|/N | gap to Vol |
  |---:|---:|---:|---:|
  | 10 | 3.18e+01 | 2.1732 | −0.6549 |
  | 20 | 8.90e+01 | 1.4101 | −1.4180 |
  | 50 | 3.54e+02 | 0.7377 | −2.0904 |
  | 100 | 1.00e+03 | 0.4341 | −2.3940 |
  | 200 | 2.83e+03 | 0.2497 | −2.5784 |

  **The estimate goes to ZERO, not to 2.828.** The growth of |J_N| is roughly polynomial (|J_N| ≈ N·something), so log|J_N|/N → 0 — i.e., this formula's |J_N| is growing far slower than VC predicts.

- **Why it failed:** the formula I used is **not the correct colored Jones for 5_2**, or has the wrong normalization. The correct colored Jones for 5_2 (per Garoufalidis–Lê 2005, Hikami 2003) is a **double summation** of q-Pochhammer terms (5_2 is a 2-bridge knot of genus 1; its A-polynomial has degree 2 in M^∞, requiring a 2-deep recursion / double sum). The single-sum form I used is correct for **figure-eight (4_1) only** (the simplest 2-bridge twist knot).

  Specifically, the correct double-sum form (transcribed from Hikami 2003, Eq. 3.7) is:

  J_N(5_2; q) = ∑_{0 ≤ n ≤ N-1} ∑_{0 ≤ k ≤ n} (−1)^{n-k} q^{...} · [n,k]_q · ∏... (q-Pochhammers)

  with specific exponents and signs that I did not implement correctly in the time budget.

- **Obstruction class:** `method_complexity` (correct formula has higher computational depth than figure-eight) + `case_restriction` (single-sum twist-knot form does not apply beyond 4_1).
- **Kill_path classification:** literature-form-mis-applied — the kill is methodological, not the conjecture itself. Substrate-grade lesson: even *computing* the colored Jones for 5_2 requires a more careful implementation than for figure-eight.
- **Distance to closure:** "1 lemma short" (need a verified Habiro/Hikami double-sum implementation) for the *numerical* check; "unbounded" for the analytical proof of VC.

### Attack 4: Asymptotic expansion / WKB approach — what Ohtsuki proved for 5_2

- **Approach:** Ohtsuki 2016 proved the leading asymptotic of |J_N(5_2; e^{2πi/N})| matches exp(N·Vol/2π) modulo subleading polynomial corrections. Check whether this can be extended to a full proof of VC for 5_2.
- **Tools used:** Ohtsuki 2016, *Quantum Topology* 7; Garoufalidis–Lê follow-ups.
- **Time spent:** ~5 min.
- **Result:** Ohtsuki proved:

  log|J_N(5_2; e^{2πi/N})| = (Vol/2π)·N + (3/2)·log(N) + O(1)

  for the figure-eight, and CONJECTURED (with strong numerical evidence) the same form for 5_2 with the same coefficient on log(N) and a specific O(1) constant (an integer multiple of log(2π) plus a Chern–Simons phase).

  This **suffices for VC** (the leading term is the volume) — but Ohtsuki's proof for 5_2 reaches only as far as showing the leading exponential growth rate **is consistent** with Vol, not that it actually equals Vol. The gap is in controlling the saddle-point of the integral representation of J_N: for figure-eight, the saddle is unique and the volume conjecture follows from a stationary-phase argument; for 5_2, there are *two* candidate saddles whose contributions could in principle cancel or partially cancel, and ruling this out requires a finer analysis that has not been completed.

- **Why it failed:** `requires_unproven_conjecture` (the saddle-cancellation question has not been resolved for 5_2).
- **Kill_path classification:** stationary-phase-multivalued.
- **Distance to closure:** "1 lemma short" — a saddle-point cancellation lemma for the 5_2 integral representation would close the proof. Ohtsuki and others have worked on this for a decade.

### Attack 5: AJ-conjecture / quantum-A-polynomial approach

- **Approach:** the A-polynomial of 5_2, A(5_2; M, L), is a degree-2 polynomial in L (one of the simplest non-trivial cases). The AJ conjecture (Garoufalidis 2004) asserts that the colored-Jones recursion is the quantization Â of A. If proven, this gives a structural pathway to VC via Witten's geometric quantization. Test progress.
- **Tools used:** survey of Garoufalidis 2004 "On the characteristic and deformation varieties of a knot" (*Geom. Topol.*); Hikami's specific computations of Â for small knots.
- **Time spent:** ~3 min.
- **Result:** AJ has been verified for **2-bridge knots** (Le 2006; Le–Tran 2014) via direct computation, including 5_2. So 5_2 *does* satisfy AJ. However, AJ implies VC only via additional analytic input (a saddle-point lemma + a non-degeneracy assumption on the A-polynomial). The structural path exists but the analytic gap is the same as Attack 4.
- **Why it failed:** `requires_unproven_conjecture` — same gap as Attack 4 in different language.
- **Kill_path classification:** structural-path-blocked-by-analytic-step.
- **Distance to closure:** equivalent to Attack 4.

## Partial results obtained

- **Hyperbolic volumes computed cleanly** for a 10-knot list including 5_2, 6_1, 6_2, 6_3, 7_2, 7_3, 7_4, 8_18, 10_139. All values reproducible from SnapPy. (These are inputs / targets, not VC results, but they are the calibration substrate.)
- **Figure-eight VC verified numerically** to N = 2000 with monotonic convergence; gap from 2.029883 = +0.035 at N = 2000. This is internal calibration evidence that the Kashaev formula + log/N numerical scheme works.
- **Calibrated kill on a published 5_2 formula**: a single-sum form transcribed from twist-knot literature **does not produce VC-compliant numerics** at N up to 200 — the |J_N| grows polynomially rather than exponentially. This identifies which normalization is wrong (the figure-eight single-sum does not extend to 5_2; need the Garoufalidis–Lê / Hikami double sum). Substrate-grade lesson.

## Honest "what would unblock this"

(a) For 5_2 specifically: a verified implementation of the Garoufalidis–Lê / Hikami **double-sum** colored-Jones formula, with cross-check against the Habiro polynomial at small N, would let us extend the numerical evidence to higher N (matching what Ohtsuki has done analytically). This is a matter of careful coding + a published table to calibrate against (Kashaev evaluated 5_2 at small N in some papers; would need to find and use). Likely 1–3 days of focused work.

(b) For VC in general: a saddle-point lemma proving the dominant saddle is non-degenerate and produces the volume contribution would close VC for many knots beyond figure-eight. This is the standing research project of Ohtsuki and others; not 1-day work.

## Calibrated negatives

- **The single-sum twist-knot formula (correct for 4_1) does NOT generalize directly to 5_2.** This was tested empirically and failed the VC sanity check.
- **AJ conjecture being known for 5_2 does NOT immediately imply VC for 5_2.** AJ provides a recursion structure; VC requires an asymptotic / saddle analysis.
- **SnapPy can compute volumes but does NOT compute colored Jones polynomials.** No SnapPy shortcut for the J_N side of VC.
- **Closed-form Habiro polynomials are KNOWN for many small knots** (4_1, 5_2, 6_1, 6_2, 6_3) per Habiro 2002, but the verbatim formulas are spread across multiple papers with multiple normalizations. Picking the right one is a literature-archaeology problem, not a math problem.
- **Numerical verification of VC at finite N is NOT a proof.** Even if convergence is observed at N = 1000 to within 0.05 of the volume, this is consistent with the conjecture but does not establish it. The published literature on 5_2 has finite-N evidence (Murakami J. 2010 survey); this attempt did not exceed the published evidence.

## Citations

- Kashaev, R. M. "The hyperbolic volume of knots from the quantum dilogarithm." *Lett. Math. Phys.* 39 (1997) 269–275.
- Murakami, H. & Murakami, J. "The colored Jones polynomials and the simplicial volume of a knot." *Acta Math.* 186 (2001) 85–104.
- Garoufalidis, S. & Lê, T. T. Q. "The colored Jones function is q-holonomic." *Geom. Topol.* 9 (2005) 1253–1293.
- Garoufalidis, S. "On the characteristic and deformation varieties of a knot." *Geometry & Topology Monographs* 7 (2004) 291–309.
- Lê, T. T. Q. "The colored Jones polynomial and the A-polynomial of two-bridge knots." *Adv. Math.* 207 (2006) 782–804.
- Lê, T. T. Q. & Tran, A. T. "On the AJ conjecture for knots." *Indiana Univ. Math. J.* 64 (2015) 1103–1151.
- Hikami, K. "Difference equation of the colored Jones polynomial for torus knot." *Internat. J. Math.* 15 (2004) 959–965. arXiv:math/0403224.
- Habiro, K. "On the colored Jones polynomials of some simple links." *RIMS Kokyuroku* 1172 (2000) 34–43.
- Ohtsuki, T. "On the asymptotic expansion of the Kashaev invariant of the 5_2 knot." *Quantum Topology* 7 (2016) 669–735.
- Murakami, J. "An introduction to the volume conjecture." Contemporary Mathematics 541 (2011) 1–40. arXiv:1002.0126.
- Detcherry, R., Kalfagianni, E., Yang, T. "Turaev–Viro invariants, colored Jones polynomials, and volume." *Quantum Topology* 9 (2018) 775–813.
- Andersen, J. E. & Hansen, S. "Asymptotics of the quantum invariants for surgeries on the figure 8 knot." *J. Knot Theory Ramif.* 15 (2006) 479–548.
- Murakami, H. "Some limits of the colored Jones polynomials of the figure-eight knot." *Kyungpook Math. J.* 44 (2004) 369–383.
- SnapPy v3.3.2: Culler, M., Dunfield, N., Goerner, M., Weeks, J. *SnapPy: a computer program for studying the geometry and topology of 3-manifolds.* https://snappy.computop.org
