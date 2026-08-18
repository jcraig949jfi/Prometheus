# Deep Research Report #140: Mazur-Galois Deformation Ring Local Components at LMFDB Scale

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** Galois deformation theory
**Predecessors:** Reports #118 (operator correlation), #119 (Hecke-Frobenius transport)

## 1. Problem Statement

Mazur (1989) attached to a continuous residual representation ρ̄: G_Q → GL_2(F_p) a universal deformation ring R^univ_{ρ̄} that pro-represents the functor of lifts to complete Noetherian local W(F_p)-algebras with residue field F_p, modulo a chosen deformation condition (flat at p, ordinary, semistable, fixed determinant, prescribed ramification). The Hecke ring T_{ρ̄}, cut out from the localization at the maximal ideal associated to ρ̄, parameterizes the modular lifts. The Wiles–Taylor–Wiles "R = T" theorem, extended by Diamond, Kisin, Khare–Wintenberger, and Calegari–Geraghty, asserts that under suitable conditions every lift is modular.

The conceptual statement is settled in many cases; the **empirical** structure of R_{ρ̄} at small primes is not. Question: for ρ̄ ranging over residual representations attached to LMFDB weight-2 newforms reduced mod p ∈ {2,3,5,7}, what is the distribution of (i) component count of Spec R^univ, (ii) Krull dimensions of components, (iii) intersection scheme of modular vs putative non-modular components, (iv) ramification type strata (Steinberg vs principal-series vs supercuspidal at auxiliary primes)?

## 2. Literature

- **Mazur (1989)**, *Deforming Galois representations*, Galois Groups over Q proceedings — foundational definition and tangent-space H¹(G_Q,Σ, ad ρ̄) computation.
- **Wiles (1995); Taylor–Wiles (1995)** — semistable case, patching argument.
- **Diamond (1997)** — multiplicity-one and refined R = T for non-minimal level.
- **Böckle (2001)** — explicit presentations of R_{ρ̄} via generators-and-relations; basis for our computational approach.
- **Kisin (2009)** — moduli of finite flat group schemes; flat deformation rings have good reduction strata indexed by Breuil–Kisin modules.
- **Snowden (2018)** — mod-p geometry of deformation rings, components in residue characteristic.
- **Calegari–Geraghty (2018)** — patching beyond Taylor–Wiles regime; predicts when extra non-modular components appear.

## 3. LMFDB Data

- `mf_newforms`: ~2.1M classical newforms; we restrict weight = 2, dim ≤ 4, level ≤ 5000. Reduce attached λ-adic Galois rep mod p via `traces` (a_ℓ mod p for many ℓ).
- `mf_galois_reps` (where present) and `mf_hecke_nf` for Hecke field structure; fall back to on-the-fly reduction in Sage if absent.
- `nf_fields`: splitting field of ρ̄ via the kernel field; needed for ramification at p and at level primes.
- `lfunc_lfunctions`: L-functions of candidate lifts when we want to check modularity of a numerically constructed deformation.
- Use Sage's `ModularForm.modp_galois_representation()` and Magma's `GaloisRepresentations` package; Böckle's algorithm for R-presentations is implemented in `ModFrmGaloisReps` (Magma) and a thin Sage wrapper in `charon/scripts/`.
- Filter to ρ̄ **absolutely irreducible** (Wiles hypothesis) and non-dihedral; this drops ~20% of candidates.

## 4. Test Design

**Step 1.** Sample ~50 ρ̄ stratified by (p, ramification type at p): ordinary / flat / semistable / Steinberg, p ∈ {3,5,7}. Defer p=2 to a second pass — its deformation theory is genuinely harder (no liftable ramification at 2 sometimes obstructs).

**Step 2.** For each ρ̄, compute via Böckle's presentation algorithm:
(a) tangent space d = dim H¹(G_{Q,Σ}, ad ρ̄) where Σ = {p} ∪ ramification primes;
(b) obstruction r = dim H²(G_{Q,Σ}, ad ρ̄);
(c) presentation R^univ ≃ W(F_p)⟦x_1,…,x_d⟧ / (f_1,…,f_r) and component decomposition of Spec R^univ via Newton stratification on the coefficient ring (Kisin's flat strata when applicable).

**Step 3.** Compute T_{ρ̄} from the localized Hecke algebra acting on weight-2 cuspforms of the corresponding level / character; record its component decomposition and Krull dimension.

**Step 4.** Compare component counts and dimensions; record intersection multiplicities along the modular component.

**Null:** swap ρ̄ between forms of same conductor; presentation should change, R/T agreement should not be preserved.

## 5. Falsification

- **Confirm:** R = T at all 50 cases (component count, dimension, intersection scheme match) → first LMFDB-scale empirical confirmation of Wiles / Khare–Wintenberger across mixed deformation conditions.
- **Strong publishable:** R has a component not in T whose generic point gives a Galois representation passing local–global compatibility checks at 50 split primes → candidate non-modular lift; report to Calegari–Geraghty patching framework.
- **Debug outcome:** extra component fails local condition at Σ → deformation condition mis-specified; fix and rerun.
- **Sanity:** Steinberg cases must show 1-dimensional component along the ordinary line (Mazur).

## 6. Budget

~1 day. Sage/PARI Galois cohomology (~3h), Magma Böckle presentation extractor over 50 cases (~4h on M2), Hecke algebra cross-check (~2h), writeup (~3h). Cache intermediate H¹/H² to `charon/playground/`.

## 7. Expected Outcome

Prior: R = T on all 50 (the theorems are strong); value is **calibration** of the R/T machinery on real data and the **first published distribution** of component counts and tangent-space dimensions across small p. Connects directly to Aporia void-detection: deformation rings are the Galois-side complement to operator transport (#118–119) — where transport measures whether two domains see the same operator, deformation components measure whether two lifts see the same Galois representation. Both feed Harmonia's V4 spectral-gap phoneme: gaps in the component lattice of R^univ are the natural void-coordinate on the Galois side, dual to spectral gaps on the automorphic side.

**Word count: 798**
