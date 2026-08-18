# Report #95: Hilbert's 17th Problem — Empirical Sum-of-Squares on Low-Degree Forms

**Target agent:** Ergon
**Date:** 2026-04-23

## 1. Precise Problem

Hilbert's 17th (ICM 1900): if f in ℚ[x_1,...,x_n] satisfies f(a) ≥ 0 for all a ∈ ℝ^n, is f a sum of squares of rational functions? Artin (1927) proved yes. The **quantitative refinement** is open: let p(n, d) be the minimum integer k such that every positive-semidefinite (PSD) form of degree 2d in n variables is a sum of k squares of rational functions. Pfister (1967) proved p(n, d) ≤ 2^n (independent of degree). Sharp values known only for (n,d) small: p(2,d)=2 (Landau), p(3,d)≤4 (Pfister), p(4,d)≤8.

Empirical question: at fixed (n, 2d) with 2d ≥ 2n-2 (Hilbert's "bad" degrees), **what fraction of random PSD forms admit k-square decompositions for k < 2^n**, and does the minimal k concentrate well below the Pfister ceiling?

Secondary target: **PSD-not-SOS gap**. Hilbert (1888) showed for (n, 2d) with n≥3, 2d≥4 excluding (3,4), (4,4), (n,2) there exist PSD forms not SOS of *polynomials*. Motzkin (1967), Robinson (1969), Choi-Lam (1977) constructed explicit witnesses. Count empirical density of PSD \ SOS as (n, d) grows.

## 2. Literature

- **Hilbert (1888)** Math. Ann. 32 — PSD ≠ SOS except in three cases.
- **Hilbert (1900)** ICM problem list.
- **Artin (1927)** Abh. Hamburg 5 — full solution via real-closed field theory.
- **Pfister (1967)** — 2^n bound via multiplicative quadratic forms.
- **Motzkin (1967)** — x^4 y^2 + x^2 y^4 + z^6 − 3x^2 y^2 z^2, PSD not SOS.
- **Choi-Lam (1977)** — systematic PSD/SOS gap analysis.
- **Blekherman (2006)** — "There are significantly more nonnegative polynomials than sums of squares"; volume ratio grows like n^{d/2}.
- **Scheiderer (2000, 2009)** — local-global obstructions; SOS on curves/surfaces.
- **Lasserre (2001), Parrilo (2003)** — SDP relaxations.
- **Powers-Wörmann (1998)** — algorithmic SOS via Gram matrix.

## 3. Computational Test Design

**Sampling:** for each (n, 2d) ∈ {(3,4), (3,6), (4,4), (4,6), (5,4), (5,6)}, generate 10K random PSD forms by (a) Gram sampling f = v^T M v with M ~ Wishart on Veronese basis, (b) rejection sampling from Bombieri-normalized Gaussian with PSD check on 10K random points + SDP feasibility.

**Per form f:**
1. **SOS feasibility** (k = n+1 ... 2^n): SDP with k-rank cap on Gram matrix. Use MOSEK or SDPA-GMP (rational certificates).
2. **Minimal k recovery:** binary search on rank; project to rational via LLL (De Klerk-Pasechnik rounding).
3. **Denominator capture:** if not poly-SOS, iterate f·q^2 for q ranging over low-degree Pfister multipliers (1+|x|^2)^m; record minimal m.
4. **PSD-SOS gap indicator:** fraction where (1) fails at polynomial level but (3) succeeds.

**Battery:**
- T1: density of minimal k by (n, d); histogram peak vs 2^n.
- T2: denominator degree distribution; test Pfister sharpness.
- T3: Blekherman volume ratio — SOS / PSD vs Monte Carlo.
- T4: Gram vs rejection sampling (null: identical k-distributions).
- T5: scaling with 2d at fixed n — does minimal k stabilize?
- T6: permutation null on coefficient signs (should push k to ceiling).
- T7: cross-check Choi-Lam known families for ground truth.

## 4. Falsification Criteria

- **Kill Pfister-sharp:** median minimal k at (n=4, 2d=6) at 4-5 rather than 8 ⇒ 2^n ceiling loose.
- **Kill polynomial-SOS regime:** PSD \ poly-SOS density < 1% for (3,6), (4,4) ⇒ Blekherman asymptotic slow.
- **Kill denominator universality:** Pfister multipliers (1+|x|^2)^m fail on >5% at m ≤ 4 ⇒ need new multipliers.
- **Null precondition:** T6 shuffle must show minimal k at 2^n ceiling; if not, SDP solver biased.

## 5. Expected Outcome

Blekherman predicts PSD ≫ SOS asymptotically, so at (4,6), (5,6) expect >50% of PSD forms fail polynomial-SOS. Pfister 2^n likely loose empirically; prior suggests median minimal k ~ n+1 to n+2.

**Most interesting scenario:** sharp bimodal distribution at some (n,d) — either k ≤ n+1 ("easy SOS") or k = 2^n ("hard rational") — suggesting a hidden dichotomy (Scheiderer-type geometric obstruction). A smooth unimodal distribution supports generic Pfister-looseness.

## 6. Budget

- Sampling 60K PSD forms across 6 regimes: 4 CPU-hours.
- SDP feasibility (MOSEK, k=1..16): ~2 sec/form → 30 CPU-hours.
- Rational rounding + denominator search: 10 CPU-hours.
- Null + bootstrap: 5 CPU-hours.
- **Total: ~50 CPU-hours, 2-3 wall days on Ergon.**

**Word count: 748**
