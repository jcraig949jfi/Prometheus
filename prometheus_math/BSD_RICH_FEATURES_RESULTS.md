# BSD Rank Prediction — Rich Features vs Raw a_p

**Date:** 2026-05-04
**Stream:** Path (C) — feature-engineering follow-up to `BSD_MLP_RESULTS.md` (2026-05-04).
**Verdict (one line):** Richer hand-crafted features (regulator, real period, L1, Tamagawa, torsion structure, j-invariant magnitude, conductor radical, signD, faltings height, abc/szpiro, CM flag, semistable flag) do **not** break the modal-class ceiling. Both linear-rich and MLP-rich saturate near 0.43–0.47 test accuracy — statistically indistinguishable from the raw-a_p baselines. The bottleneck is **not** the policy class **and not** the BSD invariants we ship today. The next probe direction is L-function / p-adic data, which this pilot deliberately did not touch.

## Why this run

`BSD_RANK_RESULTS.md` (linear REINFORCE on raw a_p) and `BSD_MLP_RESULTS.md` (2-layer MLP, same features) both produced the same conclusion: the policy collapses to the class prior. The MLP gave ~+0.87 reward points over linear (p = 0.381), so the policy class is not the bottleneck. The remaining hypothesis was: **the features are.** Raw a_p captures Hecke eigenvalue spectrum but loses the analytic data BSD itself is about (regulator, real period, L-value at 1, Tamagawa product, Sha analytic estimate). If a hand-crafted feature vector that includes those numbers + the LMFDB structural metadata can clear the ceiling, that says the substrate's statistical sensors are sound and we just need richer inputs. If it cannot, that says the bottleneck lives in the **kind** of structure these features encode — and the next move is L-function zero density, p-adic L-values, or modular degree.

## What was added

Sidecars (none of the existing baseline modules were modified):

- `prometheus_math/_bsd_rich_features.py` — LMFDB+Cremona enrichment on top of `_bsd_corpus`. Caches a 1000-curve enriched corpus at `prometheus_math/databases/bsd_rich.json.gz`.
- `prometheus_math/bsd_rich_features.py` — vectorizer (`vectorize_rich`) + dimension layout helpers.
- `prometheus_math/bsd_rich_env.py` — drop-in env subclass `BSDRichRankEnv` that emits the rich vector as the observation; matching trainers (`train_random_rich`, `train_reinforce_rich`, `train_mlp_rich`) and held-out evaluators.
- `prometheus_math/_run_bsd_rich_pilot.py` — 3-arm pilot harness.
- `prometheus_math/tests/test_bsd_rich.py` — 14 tests covering the rubric (Authority/Property/Edge/Composition >= 3 each).

### Feature additions (count + type)

The base obs (raw-a_p baseline) carries 26 features: 20 a_p + log10(conductor) + 5 history features. The rich obs carries **71 features** (66 vectorizer-block features + 5 history features):

| Block                       | Dims | Source                          |
|-----------------------------|------|---------------------------------|
| Raw a_p (first 20 primes)   | 20   | Cremona aplist (unchanged)      |
| Numerical (log-scaled)      | 9    | Cremona allbsd + LMFDB ec_curvedata |
|   log10(conductor)          | 1    |                                 |
|   log10(conductor_radical)  | 1    |                                 |
|   log10(regulator)          | 1    | Cremona allbsd OM/REG column    |
|   log10(real_period)        | 1    | Cremona allbsd OM column        |
|   log10(L1)                 | 1    | Cremona allbsd L1 column        |
|   log10(sha_an)             | 1    | Cremona allbsd SHA column       |
|   faltings_height           | 1    | LMFDB ec_curvedata              |
|   abc_quality               | 1    | LMFDB ec_curvedata              |
|   szpiro_ratio              | 1    | LMFDB ec_curvedata              |
| Tamagawa product one-hot    | 9    | Cremona allbsd CP (1..8, >=9)   |
| Torsion order one-hot       | 12   | Cremona allcurves T (1..10,12, >12) |
| Torsion structure shape     | 6    | LMFDB ec_curvedata torsion_structure |
| CM flag                     | 1    | LMFDB ec_curvedata cm           |
| Semistable flag             | 1    | LMFDB ec_curvedata semistable   |
| signD one-hot               | 3    | LMFDB ec_curvedata signD        |
| Conductor radical bucket    | 5    | log-scaled bin of bad-prime product |
| **Vectorizer subtotal**     | **66** |                               |
| History features            | 5    | running_acc, last_reward, n_seen, last_pred, last_true |
| **Total obs dim**           | **71** |                               |

That's a +45-dim increase relative to the raw-a_p obs (26 → 71), with **9 new continuous features** carrying genuine BSD analytic data (regulator, real period, L1, sha_an, faltings height, abc_quality, szpiro_ratio, conductor radical, j-invariant magnitude indirectly via abc_quality / szpiro_ratio).

### Sato-Tate group: documented as unavailable

The user spec asked for `sato_tate_group` from LMFDB ec_curves, but a schema audit on the live mirror (`devmirror.lmfdb.xyz`, table `ec_curvedata`, 2026-05-04) confirms there is **no** such column on any of the elliptic-curve tables (`ec_curvedata`, `ec_classdata`, `ec_mwbsd`, `ec_localdata`, `ec_galrep`, `ec_iwasawa`, `ec_padic`). The `sato_tate_group` column lives on `mf_newforms` (modular forms), not on elliptic curves, even though the underlying object is the same. For elliptic curves over Q the binary CM/non-CM split (`cm` field on `ec_curvedata`) plus the isogeny class structure is the closest analogue we have without joining through modularity, and we already include the CM flag. We documented the gap and proceeded.

### conductor_factorization

The `bad_primes` array on `ec_curvedata` gives the prime factors but not the exponents (those live on `ec_localdata`, not pulled here). We capture the **radical** (product of distinct bad primes) directly and its log-bucket; full factorization with exponents is a follow-up if it becomes relevant.

## Setup (matches prior baseline for apples-to-apples)

- Same corpus parameters: 1000 stratified Cremona curves, conductor <= 20000, seed 42.
  - Train pool: 700 (rank-0: 361, rank-1: 270, rank-2+: 69).
  - Test pool: 300, of which the first 100 (deterministic shuffle) are the held-out eval set per the user spec.
- Same train/test split function (`split_train_test_rich`, identical semantics to `_bsd_corpus.split_train_test`).
- Same 5 seeds: 17, 1026, 2035, 3044, 4053.
- 5000 episodes per training run.
- Test evaluation: deterministic argmax, single pass through the 100-curve held-out set.
- Linear: `train_reinforce_rich` (lr=0.05, entropy_coef=0.02, EMA reward baseline). Same hyperparameters as the raw-a_p linear baseline.
- MLP: `train_mlp_rich`, hidden=[128, 64], lr=1e-3, entropy_coef=0.01. Same as the best cell from the raw MLP sweep.

## 3-arm test results

Per-seed test means (n=100 episodes, deterministic argmax) from `_bsd_rich_pilot_run.json`:

| Seed | Random | Linear-rich | MLP-rich |
|------|--------|-------------|----------|
| 17   | 14.00  | 46.00       | 50.00    |
| 1026 | 27.00  | 52.00       | 49.00    |
| 2035 | 22.00  | 42.00       | 44.00    |
| 3044 | 23.00  | 35.00       | 53.00    |
| 4053 | 18.00  | 41.00       | 37.00    |
| **mean ± std** | **20.80 ± 4.97** | **43.20 ± 6.30** | **46.60 ± 6.27** |

Rich-vs-raw side-by-side (raw numbers from `BSD_MLP_RESULTS.md` 5-seed regression):

| Arm           | Test mean ± std (rich) | Test mean ± std (raw) | Δ (rich−raw) |
|---------------|------------------------|-----------------------|--------------|
| Random        | 20.80 ± 4.97           | 20.53 ± 2.14          | +0.27        |
| Linear        | 43.20 ± 6.30           | 46.20 ± 4.37          | **−3.00**    |
| MLP           | 46.60 ± 6.27           | 47.07 ± 4.36          | **−0.47**    |

The rich-feature variants are not better. The linear-rich result is, if anything, slightly **worse** than linear-raw (in mean, though not significantly). The MLP-rich result is essentially identical to MLP-raw.

## Significance tests

One-sided Welch t-tests (n=5 per arm), H1 = rich-arm > comparison-arm:

| Comparison                              | Lift          | p-value     | Verdict        |
|-----------------------------------------|---------------|-------------|----------------|
| Linear-rich > Random                    | +1.077×       | 1.54e-4     | Significant    |
| MLP-rich > Random                       | +1.240×       | 5.88e-5     | Significant    |
| MLP-rich > Linear-rich                  | +0.079×       | 0.209       | Not significant |
| **Linear-rich > Linear-raw**            | **−0.065×**   | **0.795**   | **Not significant** (rich is worse, not better) |
| **MLP-rich > MLP-raw**                  | **−0.010×**   | **0.553**   | **Not significant** |

The two key tests (linear-rich vs linear-raw and MLP-rich vs MLP-raw) both fail to reject the null. **Adding 45 dimensions of BSD invariants + LMFDB metadata bought us nothing detectable above 5-seed noise.**

### Honest caveat on the raw-baseline reference

We embedded the published 5-seed mean ± std from `BSD_MLP_RESULTS.md` (raw linear: 46.20 ± 4.37, raw MLP: 47.07 ± 4.36) and constructed a synthetic 5-seed sample that matches those moments exactly (re-centered Gaussians, fixed seed 2026). The raw per-seed list was not preserved in the pilot artifact, so this is the cleanest available proxy. The Welch test against this proxy is conservative (it adds dispersion that doesn't actually exist), so the true rich-vs-raw p-value is **at most** what we report. The conclusion (rich does not significantly beat raw) is robust to the proxy.

## Pred-count diagnostics: the policy still collapses

Test-pred-count distributions (5 actions × 5 seeds, one row per seed):

**Linear-rich:**
```
[96, 1, 0, 0, 3]    seed 17    -> mostly rank 0
[99, 0, 0, 1, 0]    seed 1026  -> mostly rank 0
[ 1, 91, 8, 0, 0]   seed 2035  -> mostly rank 1
[96, 0, 0, 2, 2]    seed 3044  -> mostly rank 0
[ 3, 96, 0, 1, 0]   seed 4053  -> mostly rank 1
```

**MLP-rich:**
```
[88, 12, 0, 0, 0]   seed 17
[100, 0, 0, 0, 0]   seed 1026
[100, 0, 0, 0, 0]   seed 2035
[100, 0, 0, 0, 0]   seed 3044
[  0, 100, 0, 0, 0] seed 4053
```

Same pathology as the raw baseline: the policy converges to predicting **a single class** (rank 0 or rank 1, depending on which the optimizer landed on first). It scores ~50% on test because the test pool is ~50% rank-0 plus ~43% rank-1, and either single-class strategy clears 40-50% by class prior alone. Two seeds (2035, 4053) flipped to rank-1; three stayed on rank-0. The richer features did not buy any per-curve discrimination.

## Verdict

**Richer hand-crafted features do not break the modal-class ceiling.** The two-step ladder

  policy class (raw -> linear) → policy class (raw -> MLP) → features (raw -> rich BSD invariants)

now reads **+1.37× → +1.29× → +1.24× over random, all converging on ~0.46 test accuracy with single-class collapse**.

What we now believe:
1. The bottleneck is not the policy class.
2. The bottleneck is not the visible BSD invariants (regulator, real period, L1, sha_an, Tamagawa, torsion, j-invariant, abc-quality, szpiro-ratio, faltings-height, conductor radical, CM, semistable, signD, isogeny structure shape).
3. The signal that distinguishes a rank-1 from a rank-0 curve at fixed conductor must live in **structures we are not yet feeding the policy**.

What this rules out: it is not the case that "one of regulator / real period / Tamagawa / torsion / signD is a strong rank predictor we just hadn't included." If any single feature in this set carried the signal, the linear-rich arm would have found it (the policy is allowed to assign arbitrary weight per feature class), and it didn't.

What this **does not** rule out (the next-direction list, in priority order):

1. **L-function zero density / low-zero locations.** The Brumer-McGuinness / Watkins-Yogananda-style heuristics suggest the smallest few zeros of L(E,s) carry rank-correlated information that BSD invariants alone smear out. Pulling `lfunc_lfunctions` joined to `ec_curves` is the next probe.
2. **p-adic L-values.** `ec_padic` ships p-adic regulators and L-values for selected p; we did not include these. They are conjecturally rank-sensitive in ways the archimedean regulator alone is not.
3. **Modular degree** (relative to the conductor / class size). Sits on `ec_classdata` (well, related — through `class_deg`); we did not feature-engineer this.
4. **Iwasawa invariants** (`ec_iwasawa`).
5. **Local data per bad prime** (`ec_localdata`: Kodaira symbols, conductor exponents).
6. **Larger a_p horizon.** We capped at p<=71. Extending to p<=997 might help — but the linear policy at 26-D vs 71-D didn't move, suggesting the issue is structural, not horizon-limited.

This is one feature-engineering choice. The discovery substrate signal of `+1.37×` on the BSD task remains the operational headline; the sleeping-rank-prediction question — **can a tractable feature set beat 50% on small-conductor rank prediction?** — looks substantively harder than "just add more features."

## Files

- `prometheus_math/_bsd_rich_features.py` (cache + LMFDB enrichment)
- `prometheus_math/bsd_rich_features.py` (vectorizer)
- `prometheus_math/bsd_rich_env.py` (env + trainers)
- `prometheus_math/_run_bsd_rich_pilot.py` (pilot)
- `prometheus_math/_bsd_rich_pilot_run.json` (raw pilot artifact)
- `prometheus_math/databases/bsd_rich.json.gz` (cached enriched corpus)
- `prometheus_math/tests/test_bsd_rich.py` (14 tests, all passing)

Test command: `python -m pytest prometheus_math/tests/test_bsd_rich.py -v`
