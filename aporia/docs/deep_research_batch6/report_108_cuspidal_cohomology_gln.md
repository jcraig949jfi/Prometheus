# Deep Research Report #108: Cuspidal Cohomology of GL(n,Z) for n=5,6

**Target Agent:** Harmonia
**Tier:** Deferred (~3 days)
**Date:** 2026-04-23

## 1. Problem Statement

Let Γ_n = GL(n, Z) act on symmetric space X_n = GL(n, R) / O(n) · R^×. Group cohomology H^*(Γ_n; C) decomposes via Franke (1998) into automorphic pieces:

    H^*(Γ_n; C) = H^*_cusp ⊕ H^*_Eis

where H^*_cusp corresponds to cuspidal automorphic representations of GL(n, A_Q) with cohomological infinitesimal character, and H^*_Eis is built from Eisenstein series induced from proper parabolics.

- n=2: relates to classical weight-2 cusp forms — vanishes for SL(2, Z).
- n=3: Ash-Grayson-Green (1984) — first cuspidal class at level 1 in H^5 is zero in char 0, but mod-p torsion appears.
- n=4: van Geemen-Top et al. identified Siegel-modular-form origin.
- **n=5,6 at level 1:** cuspidal cohomology conjectured to vanish, empirical verification incomplete, Eisenstein contribution rank unsettled.

**Question:** can we numerically confirm dim H^*_cusp(GL(n, Z); C) = 0 for n=5,6 via sharbly/Voronoi computations, and quantify Eisenstein-cohomology dimension against Harder's formula?

## 2. Literature

- **Borel-Serre (1973):** corners compactification; H^*(Γ; C) finite-dim; Eisenstein boundary contribution.
- **Harder (1987)** "Eisenstein cohomology of arithmetic groups": explicit H^*_Eis from Levi subgroups; "Harder conjecture" on Hecke congruences.
- **Franke (1998)** Ann. Sci. ENS: decomposition theorem proving automorphic forms compute H^*(Γ; C).
- **Ash-Rudolph (1979):** modular symbols and sharbly complex for GL(n); computational backbone n ≤ 4.
- **van Geemen-van der Kallen-Schwarz-Top (1997):** H^5(SL(4, Z); C); cuspidal class = Siegel form.
- **Bergström-Faber-van der Geer (2008+):** Siegel modular forms of genus 2,3 via ℓ-adic cohomology of A_g.
- **Elbaz-Vincent–Gangl–Soulé (2013), Dutour Sikirić et al. (2019):** perfect-form Voronoi reduction for n ≤ 7; landmark integral cohomology H^*(GL_n(Z); Z), n ≤ 7.

## 3. Data Availability

- **LMFDB:** sparse; GL(2), GL(3) fully tabulated; growing GL(4); essentially nothing n ≥ 5 level 1.
- **PARI/GP, Magma:** partial Voronoi.
- **Dutour Sikirić `polyhedral_common`** (GitHub): perfect-form enumeration n ≤ 8.
- **CoHomology (SAGE):** sharbly n ≤ 4.
- **Cohen-Lenstra heuristics:** torsion-density predictions for H^*(Γ_n; Z) — distinguish small-prime torsion from genuine cuspidal rank.

## 4. Test Design

1. Pull Voronoi cell complex for GL_5(Z) and GL_6(Z) from Dutour Sikirić (222 and ~7000 perfect forms).
2. Compute H^*(Γ_n; Q) via equivariant chain complex. n=5 tractable (Elbaz-Vincent); n=6 at frontier.
3. Subtract Harder's Eisenstein prediction: dim H^*_Eis = sum over parabolic associate classes of dimensions of induced discrete-series from GL_k, k < n.
4. Residual = cuspidal rank. Compare to zero.
5. Cross-validate via T_2, T_3 Hecke: cuspidal dimension d → d simultaneous eigenvectors orthogonal to Eisenstein subspace.

## 5. Falsification

- **Falsified** if residual cuspidal rank ≠ 0 after Harder subtraction — discovery (first level-1 cuspidal class for GL(5) or GL(6)).
- **Null confirmed** if residual = 0 within precision and Hecke spectrum matches induced-from-Levi eigenvalues.
- **Ambiguous** if Voronoi fails to close at n=6 (memory/time blowup) — fallback: n=5 full, n=6 at reduced level Γ_0(2).

## 6. Budget

~3 days. D1: ingest Dutour Sikirić, reproduce n=4 sanity. D2: run n=5 chain-complex, Harder formula, residual. D3: attempt n=6 (likely partial), Hecke cross-check, writeup.

## 7. Expected Outcome

High probability null holds: dim H^*_cusp(GL_n(Z); C) = 0 for n=5,6 at level 1. Value from (a) quantifying exact Eisenstein dimension (publishable number), (b) empirical Harder's formula verification in n=6 regime, (c) identifying torsion primes in H^*(Γ_6; Z) for Cohen-Lenstra comparison. Non-null = headline discovery.

**Word count: 748**
