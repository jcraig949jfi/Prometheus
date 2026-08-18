# Deep Research Report #101: p-adic Uniformization Rank for Shimura Curves — Drinfeld Level Structures

**Target Agent:** Harmonia
**Date:** 2026-04-23

## 1. Problem Statement

Let B be an indefinite quaternion algebra over Q of discriminant D = p · D' with p ∤ D', O ⊂ B an Eichler order of level N coprime to D. The Shimura curve X^D_0(N) has canonical integral model whose special fiber at p admits **p-adic uniformization** (Cerednik-Drinfeld): there exists B' swapping invariants at ∞ and p such that

    X^D_0(N)(C_p)^an ≅ Γ \ (H_p × P^1(Ẑ^{(p)})^× / Ô^×)

where H_p is Drinfeld's p-adic upper half plane and Γ ⊂ B'^× arithmetic.

**Question:** Does the **p-adic uniformization rank** r_p(X) := rk_Z H^1(Γ, Z)^new, equivalently the toric-part character-lattice rank of Jac(X) at p, correlate with global arithmetic invariants (analytic rank, MW rank of Jacobian factors, Tamagawa products) beyond what genus alone predicts?

Layer 3 test: probing whether Drinfeld level structure statistics encode a bridge absent from the scalar genus layer.

## 2. Literature

- **Cerednik (1976)** Mat. Sb. 100: original p-adic uniformization for Shimura curves at bad primes.
- **Drinfeld (1976)** Funct. Anal. Appl. 10: H_p as formal scheme moduli of special formal O_B-modules.
- **Boutot-Carayol (1991)** Astérisque 196-197: rigorous proof via formal schemes, moduli interpretation of Drinfeld level structures.
- **Teitelbaum (1993)** modular symbols + p-adic L-function via Drinfeld symbols: bridge from Γ-cohomology to L-values.
- **Yang (2013)** Hilbert modular surface arithmetic intersection: rank-height coupling.

Supporting: Greenberg-Stevens (Hida families on Shimura curves), Longo-Vigni (Heegner via p-adic uniformization), Molina (explicit Eichler orders).

## 3. LMFDB Data

LMFDB `shimura_curves` sparse (few dozen tabulated). Generate corpus from Eichler orders:

- Quaternion disc D = p·q for primes p,q < 500, pq < 2000 (~20K candidates, ~1K after genus filter).
- For each (D,N), construct Eichler order via Magma `QuaternionAlgebra` or Sage `BrandtModule`.
- Genus g via Eichler mass formula; keep 2 ≤ g ≤ 20 (1K-curve target).
- For each curve and p | D, compute Drinfeld level structure.

## 4. Test Design

Per ~1K Shimura curves X^D_0(N):

1. **r_p** via Brandt matrix kernel: r_p = dim ker(T_p − (p+1)) ∩ S_2(D,N)^{p-new}.
2. Genus g and new-subspace dimension g^new.
3. Analytic rank r_an of Jacobian via LMFDB cross-ref on isogeny decomposition, or modular symbol pairing on Bruhat-Tits tree Γ \ T_p.
4. Tamagawa product ∏_{ℓ | DN} c_ℓ (Mumford-Kurihara for p ∤ D, Cerednik for p | D).

**Primary:** partial correlation ρ(r_p, r_an | g, g^new). Detrend by genus (Megethos prior: 96%+ of naive correlation is genus-driven).

**Secondary:** MI between Drinfeld orbit sizes and Tamagawa factors; r_p distribution p-new vs p-old.

## 5. Falsification

Kill conditions (any triggers kill-report):
- Partial |ρ| < 0.1 after genus detrend.
- Permutation null (5K shuffles) p > 0.01.
- Fails to replicate across 5 random 200-curve subsamples.
- Signal vanishes restricted to D' > 1 (D = p prime-disc is classical modular curve artifact).

Pre-register: mean-spacing normalization on r_p before any gap claims.

## 6. Budget

- Eichler order enum: 3h (Sage/Magma).
- Brandt matrix + Hecke diagonalization: 6h parallel.
- Drinfeld level tabulation: 4h.
- Correlation + null + 5 seeds: 3h.
- Writeup: 2h.
- **Total: ~18h wall, one compute day on SpectreX5.**

## 7. Expected Outcome

Prior (calibrated): 70% kill, 20% weak signal (|ρ| ∈ [0.1, 0.2] post-detrend), 10% strong signal.

Survivors: mechanism almost certainly **toric rank = character lattice rank**. r_p is literally Grothendieck monodromy pairing dimension; coupling to r_an instantiates p-adic BSD shadow visible before any L-function computation. Layer 3 bridge candidate alongside genus-2 Rosetta.

Kill sharpens `project_silent_islands`: Shimura curves join knots and NF as arithmetically-rich but tensor-isolated islands — strengthens claim that p-adic invariants don't naively project onto Megethos substrate.

**Word count: 748**
