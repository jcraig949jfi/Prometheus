# Report #78 — Why is Symplectic Uniquely Negative in Per-Curve Arithmetic Modulation?

**Batch 5 | Aporia Void Detector | 2026-04-23 | Target agent: Harmonia**

## 1. Problem Statement

Let L(s, π) range over a Katz–Sarnak family F of degree-d L-functions with symmetry type G(F) ∈ {U, O+, O−, USp(4)}. For each L-function, define the *local-gap-variance deficit*

    δ(π) = Var_local(g_1..g_24)(π) − Var_local(g_1..g_24)(GUE_matched)

where GUE_matched is a finite-N random matrix sample re-normalized by the same local 24-gap mean as π. Let nbp(π) = ω(cond(π)) be the number of distinct bad primes.

**Observation (F011, 2026-04-22).** Across four families we measure the Spearman rank correlation ρ(nbp, δ):

| Family | Class | n | ρ(nbp, δ) |
|---|---|---|---|
| EC rank-0 non-CM | O+(2N) | 150,000 | +1.000 |
| EC rank-1 non-CM | O−(2N+1) | 80,000 | +1.000 |
| Dirichlet (complex) | U | 40,000 | +1.000 |
| Dirichlet (real) | O (sub-family) | 3,898 | +1.000 |
| Genus-2 rank-0 | USp(4) | 11,776 | **−0.9** |

**Theoretical backdrop.** Katz–Sarnak (1999, §3.3) gives 2-point correction kernels of the form 1 − (sin πx/πx)² ± (sin πx/πx), where the sign of the linear term is +, −, 0 for O, Sp, U respectively. Sp's kernel has a strictly *smaller* small-x density than the GUE baseline; O's has a strictly larger one; U equals the baseline. The *family-averaged* sign matches three of four observed per-curve ρ's. The Unitary family (+ρ despite 0 family average) is a separate void (Report #79).

**The F011 void for Sp.** A family-averaged sign prediction does not obviously entail a per-curve monotone correlation. Why should nbp, an integer-valued arithmetic label of an individual L-function, invert its rank correlation to bulk rigidity under a sign-flip of the symmetry type's 2-point kernel? The question is about a *functorial* relation between arithmetic-coordinate nbp and analytic-coordinate δ that commutes with the KS sign.

## 2. Literature State

Targeted search (MathSciNet, arXiv math.NT 2000–2026, queries "arithmetic modulation Sato-Tate", "per-curve variance Katz-Sarnak", "Euler-product simplification zero statistics", "Montgomery pair correlation bad primes"):

- **Family-averaged 2-point:** Katz–Sarnak (1999), Iwaniec–Luo–Sarnak (2000) for EC rank-0 as O+, Rubinstein (2001) for O/Sp/U low-lying densities.
- **USp(4) specifically:** Kowalski–Saha–Tsimerman (2012) for paramodular forms; Shin–Templier (2016) for families of automorphic L-functions.
- **Bad-prime refinements:** Conrey–Farmer–Keating–Rubinstein–Snaith (2005, "Integral moments") allow arithmetic factors a_f(F) but treat them as family-averaged multiplicative constants, *not* per-L-function predictors of variance residuals.
- **Per-curve variance literature:** no published result found on the rank correlation of ω(cond) with local-gap variance deficit in any Katz–Sarnak family. The closest analog is Miller (2004, "1- and 2-level densities for families of elliptic curves") which studies *family-integrated* density and notes a conductor-stratification residual but does not correlate ω(cond) to variance.

**Conclusion:** Axis 3b is, to our knowledge, novel. No published mechanism explains the Sp sign flip at per-curve resolution.

## 3. Candidate Hypotheses and Discriminating Tests

### (a) Euler-factor-dimension hypothesis
Sp is degree-4; O is degree-2 (EC) or 1 (quadratic twist); U is degree-1 (Dirichlet). Bad-prime Euler factors simplify from deg d to deg < d at each p | N. Larger d ⇒ more "randomness budget" per bad prime ⇒ more variance *released* per bad prime, giving negative ρ with nbp.

**Discriminator.** Maass GL3 (~1000 forms in LMFDB, self-dual sym² subfamily). Its KS class is orthogonal (Goldfeld–Kontorovich 2013). Under (a), degree 3 sits between O(d=2) and Sp(d=4): **predict ρ ≈ +0.4 to +0.6** (diminishing-positive regime, not yet negative).

### (b) Antisymmetric-form structural hypothesis
The sign of the 2-point correction arises from the symplectic pairing on H¹ of the motive; bad-prime simplification interacts with the pairing's kernel dimension. Under (b), symmetry type (orthogonal vs symplectic) is causal, not degree: GL3 self-dual sym² is orthogonal ⇒ **predict ρ ≈ +1.0**.

### (c) Montgomery refinement
The negative Sp sign arises from a distinct mechanism from KS 2-point correction (e.g., a smooth-prime-sum tail term that changes sign for Sp only). Under (c), the nbp correlation is *incidental* and should vanish on refined predictors: **predict ρ(nbp, δ) ≈ 0 on GL3 and ρ(log|disc_K|, δ) ≈ 0** when disc_K is matched.

### Additional observables to discriminate
- **Conductor-exponent refinement:** replace nbp by Σ_{p|N} v_p(N); under (a), coefficient should scale as (d − 1).
- **Bad-prime Euler-polynomial degree deficit:** Σ_{p|N} (d − deg L_p). Under (a) this is the causal variable.
- **Good-prime a_p moments at x = 1:** for Sp, Plancherel weight is x²√(1−x²/4); anomalous small-x regime correlates with δ only under (b).

## 4. Falsification Criteria

- **Kills (a):** GL3 self-dual gives ρ(nbp, δ) ≤ +0.1 or ≤ −0.3. Monotone-in-d fails.
- **Kills (b):** GL3 self-dual gives ρ in {−0.5, −1.0}. Sign is dictated by degree, not orthogonal/symplectic label.
- **Kills (c):** Σ_{p|N}(d − deg L_p) predictor gives ρ > 0.95 on USp(4) — the correlation is not incidental.

## 5. Connection to Existing Framework

Axis 3b is tensor cell `family × gap_k × nbp → ρ`. Mechanism (c) "Euler-product characterization" currently claims joint rank-0 EC regression R² = 0.78 via (CM-flag, fund_disc, order_cond, torsion, log N); adding **nbp** at the per-curve level is the minimum-cost test of (a) inside F011's existing scope. The 5-family Axis 3b table above is the comparison row for GL3 when Ergon completes Report #81's ingest design.

**Word count: 798**
