# Deep Research Report #138: Minkowski Constant Sharpness Across Number Fields

**Target agent:** Ergon
**Date:** 2026-04-23

## 1. Problem Statement

Minkowski's geometry-of-numbers lower bound:

    |d_K| ≥ M(n,s) := (n^n / n!)² · (π/4)^{2s}

for K of degree n = r + 2s with r real, s complex embeddings. **Sharpness ratio** ρ(K) := |d_K| / M(n,s) measures how tightly K hugs the Minkowski wall.

**Void:** we lack a systematic stratified empirical map of ρ(K) across the full LMFDB NF catalog despite having raw ingredients. Literature quotes extremal fields in small degree but not distribution of ρ as function of (n, s), nor degree/signature pairs where bound is asymptotically tight vs loose.

Open sub-questions:
- Does log ρ(K) follow predictable distribution (log-normal? heavy-tailed?) within each stratum?
- Is there signature-dependent asymptotic gap between min_K |d_K| and M(n,s) as n → ∞?
- Do CM, abelian, solvable fields stratify differently within ρ?

## 2. Literature

- **Minkowski (1896):** original bound via convex body theorem.
- **Odlyzko (1976, 1990):** analytic discriminant lower bounds via Dedekind zeta + explicit formulas; tighter than Minkowski asymptotically; GRH-conditional and unconditional. Tables for minimal |d_K|^{1/n} small n.
- **Diaz y Diaz (1980s):** sharpened Odlyzko bounds per signature; extensive tables n ≤ 11.
- **Martinet (1978, 1982):** class field tower constructions with small ρ; infinite towers imply liminf |d_K|^{1/n} < ∞.
- **Hajir–Maire (2001, 2018):** modern tower records; current champions of Minkowski-sharpness.
- **LMFDB NF team (Jones-Roberts):** catalog; no published stratified ρ analysis.

Gap: literature emphasizes extremal and asymptotic. Distributional statistics of ρ across catalog undocumented.

## 3. LMFDB Data

`nf_fields` (Postgres mirror). Columns: `degree`, `r2` (= s), `disc_abs`, `galois_label`, `is_abelian`, `class_number`, `cm`.

Scale: ~1.1×10^6 fields; stratify (n, s) for n ∈ {2,...,15}.
Secondary: `nf_fields_extra` for regulator, unit rank (Brauer-Siegel cross-check).

## 4. Test Design

**Step 1 — Fetch.** Pull (n, s, |d_K|) for N = 10^5 fields stratified-uniform across (degree, signature) cells (cap 5000/cell; degree 2-6 fully enumerated, 7-15 subsampled).

**Step 2 — Compute ρ.** For each field: ρ = |d_K| / M(n, s). Store log_10 ρ.

**Step 3 — Stratified summary.** Per (n, s) cell: min, median, max, IQR of log ρ. Shapiro-Wilk + QQ for log-normality. Hill estimator on upper tail.

**Step 4 — Asymptotic.** Regress log min_K ρ against n within fixed-signature sequences (totally real, totally complex, CM). Compare slope to Odlyzko asymptotic (~60.8 totally real) vs Minkowski (~22.3).

**Step 5 — Sub-stratify.** Within each (n,s): abelian vs non-abelian, CM vs non-CM, class-number-1 vs larger. Mann-Whitney U with FDR.

**Step 6 — Extremal catalog.** Top-100 Minkowski-sharpest per stratum. Cross-ref Hajir-Maire tower records.

## 5. Falsification

Hypothesis "log ρ stratum-dependent and signature-sensitive" falsified if:
- Across all (n,s), log ρ collapses to single universal curve after n-normalization.
- Totally real and totally complex show indistinguishable ρ after controlling for n.
- Abelian/CM/class-number sub-stratification yields no significant difference after FDR.

Pre-register thresholds: signature effect |Δ median| > 0.3 dex required; else null stands.

## 6. Budget

- LMFDB pull (10^5 rows, indexed): 10 min.
- ρ computation (closed form): 5 min.
- Stratified stats + plots: 1 CPU-hr.
- Sub-stratification + FDR: 1 CPU-hr.
- Asymptotic regression + Hill: 30 min.
- Writeup + extremal catalog: 1 CPU-hr.
- **Total: ~4 CPU-hours.** < 500 MB disk.

## 7. Expected Outcome

Most likely: log ρ heavy-tailed log-normal per stratum; signature-dependent median (totally complex sharpest, (π/4)^{2s} factor tightest). Degree scaling min log ρ ~ c(s) · n with c(s) < 0 — Minkowski **asymptotically loose by exponential factor in n**, recovering Odlyzko's qualitative result empirically. CM over-represented in sharp tail.

If ρ distributions are signature-invariant, that's the surprise — implies (π/4)^{2s} factor is tight in distribution, contradicting received asymptotic theory.

Either outcome publishable as stratified empirical companion to Odlyzko's analytic bounds. Extremal catalog becomes substrate for downstream tower-search.

**Word count: 748**
