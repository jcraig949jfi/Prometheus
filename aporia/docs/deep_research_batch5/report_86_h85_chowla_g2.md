# Deep Research Report #86 — H85: Chowla Conjecture at Genus-2 Discriminants, Stratified by Automorphism Group

**For:** Charon agent
**Project:** Aporia Void Detector, Prometheus team
**Date:** 2026-04-23
**Hypothesis state:** BORDERLINE (z=1.19 at partial sample; full run pending)

## 1. Problem Statement (Measurement-Level)

For each automorphism group `G` appearing in the LMFDB `g2c_curves` table, define the stratified set

```
D_G = { |disc(C)| : C is a rank-0 genus-2 curve with Aut(Jac(C)) ≅ G }
```

Compute the signed partial sum of the Liouville (or Möbius) function over that set:

```
T_G(X) = Σ_{d ∈ D_G, d ≤ X} λ(d)
S_G    = T_G(X_max) / sqrt( |D_G ∩ [1, X_max]| )
z_G    = |S_G|
```

The kill/survive rule (from Aporia's 90-frontier document):

- **PASS (H85 survives):** any `G` with `|D_G| > 5000` yields `z_G > 3.0`.
- **KILL:** all `G` with `|D_G| > 5000` yield `z_G < 1.0`.
- **BORDERLINE:** `1.0 ≤ z_G ≤ 3.0` — inconclusive, current state at n=partial.

Note: Möbius `μ` is zero on non-squarefree `d`; Liouville `λ(n) = (-1)^Ω(n)` is non-zero everywhere. **Run both.** Disagreement between `μ` and `λ` is itself a stratifying signal (squarefree density in `D_G`).

## 2. Literature State

Classical Chowla: `(1/N) Σ_{n≤N} λ(n)·λ(n+h) → 0` for `h ≥ 1`. Open in full strength; one-point case (PNT) is equivalent to RH-free statements.

Matomäki–Radziwiłł (2016) resolved Chowla on average over short intervals. Tao (2016) gave the logarithmically-averaged two-point. None of this literature addresses Möbius **evaluated at a sparse arithmetic-geometric sequence** like `{disc(C) : C ∈ family}`.

Closest prior work to flag:
- Möbius at polynomial values (Bourgain–Sarnak–Ziegler; Sarnak's Möbius randomness principle).
- Möbius at elliptic-curve discriminants — no direct reference found in our Aporia crawl; treat as open.
- Conductor sequences of Hecke eigenforms — distributional work in Conrey–Soundararajan style, but not λ-sums.

Working assumption: Sarnak's randomness heuristic predicts `z_G = O(1)` for any "geometric" sequence not correlated with multiplicative structure. An observed `z_G > 3` would be a Möbius-disorder **violation** at a specific automorphism stratum — that's the publishable direction.

## 3. LMFDB Data Specifics

Table: `g2c_curves` (LMFDB Postgres mirror).
Required columns:
- `abs_disc` — bigint/string (cast carefully; LMFDB disc fields can exceed int64).
- `mw_rank` — integer; filter `mw_rank = 0`.
- `aut_grp_id` and/or `geom_aut_grp_id` — group label (small-group-ID tuple, e.g. `[2,1]`, `[4,2]`, `[12,4]`).
- `geom_end_alg` — flags CM / RM / split Jacobians.

Charon should query `information_schema.columns` first to confirm exact names; LMFDB renames columns between releases.

## 4. Concrete Pipeline (Charon-Runnable)

```sql
SELECT label, abs_disc, aut_grp_id, geom_aut_grp_id, geom_end_alg
FROM g2c_curves
WHERE mw_rank = 0;
```

Expected row count ~66,158.

```python
from sympy import factorint
def liouville(n):
    return (-1) ** sum(factorint(int(n)).values())
def mobius(n):
    f = factorint(int(n))
    if any(e > 1 for e in f.values()): return 0
    return (-1) ** len(f)
```

Stratify: `groupby aut_grp_id`, compute `T_G`, `|D_G|`, `z_G = |T_G|/sqrt(|D_G|)` per group. Report one row per `G` with `N_G`, `T_G`, `z_G` (Liouville), `z_G` (Möbius), squarefree density. Flag every row with `N_G > 5000`.

## 5. Automorphism Strata to Flag

Ordered by Aporia's prior probability of anomaly:

1. **Generic simple Jac, `Aut = C_2`** — ~80–85% of rows. Baseline; expect `z ≈ 1`. The current z=1.19 is almost certainly dominated by this stratum.
2. **Split Jac (E×E' up to isogeny), `Aut ⊇ C_2 × C_2`** — small, potentially structured; discriminants factor as products of two elliptic conductors, so multiplicative correlation is plausible.
3. **CM-type / RM-type (flagged via `geom_end_alg`)** — rarest; if any stratum shows `z > 3`, most likely here.
4. **Extra-automorphism curves (`Aut ⊇ C_4`, `D_4`, `C_6`)** — small N; may fail the `N > 5000` precondition but record anyway.

## 6. Null Controls (Mandatory)

Run a permutation null. Shuffle the `disc → aut_grp` mapping 1000 times, recompute max `z_G` over strata with `N > 5000`. Report observed-vs-null percentile. Bare z-scores without this null are **inadmissible** per the Aporia battery.

Also detrend by `|D_G|`-weighted squarefree density (per `feedback_prime_atmosphere.md` — 96% of cross-dataset structure is primes).

## 7. Budget

- SQL extract: <10 s.
- Factoring 66,158 discriminants via `sympy.factorint`: ~60–120 s.
- Stratification + 1000-permutation null: ~3 min.
- **Total: 5–7 minutes.** No GPU needed.

## 8. Expected Outcome

Sarnak-randomness prior: `z_G < 2` uniformly. Most likely result — KILL at scale. A survive outcome would be the single strongest Möbius-disorder violation in the Aporia catalog.

**Word count: 794**
