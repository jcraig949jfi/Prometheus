# Synthetic Env (W3.1) — Acceptance Criteria

**Module:** `ergon/diagnostic_c/synthetic_env.py`
**Locked by:** Aporia W2.5 sign-off (2026-05-05; cleared/conditional on these 3 criteria being met before any tire-kick training run)
**Acceptance gate:** `validate_acceptance_criteria(corpus) -> {criterion_1_pass, criterion_2_pass, criterion_3_pass, all_pass}`
**Test files:**
- `ergon/learner/tests/test_synthetic_env.py` — 18 unit tests covering criteria + edge cases
- `ergon/learner/tests/test_synthetic_env_acceptance.py` — thin gate-level test that ticks the 3 boxes (E002 ticket-specific name)

---

## Why these criteria

The synthetic env is the only NON-CONTAMINATED training source for v0.5 / v0.5b LoRA tire-kicks (per Aporia's sharpened gating constraint: "defer cross-domain Ergon training until ≥100 per-claim kill records exist in ≥2 domains"). If the env doesn't meet these criteria, the verdict from any tire-kick on it is uninterpretable — either the env was trivially solvable (yielding fake PASS), or it sat at the modal-collapse boundary (yielding spurious FAIL), or it tested a different feature space than the corpus we want to generalize to.

## The 3 criteria

### 1. LSQ-baseline recoverability > 85% on held-out clean data

**Why:** the latent rule must be recoverable by a documented closed-form baseline (`numpy.linalg.lstsq`) at meaningfully-above-chance accuracy. If LSQ hits ~50% the rule isn't actually in the features; if LSQ hits ~100% the env is too easy and any model "passes" trivially.

**Current default (snr_db=10, seed=42):** LSQ baseline = **0.940** (>0.85 floor cleared with margin; <0.99 trivial avoided).

**Verified by:** `test_acceptance_criterion_1_lsq_above_85` and `test_synthetic_env_acceptance.py::test_criterion_1`.

### 2. SNR in documented range (5–20 dB)

**Why:** at modal-collapse-V3 SNR (signal:noise ~10⁴:1; sigma=0.01 over standardized inputs) REINFORCE/PPO collapsed despite trivial LSQ recoverability — that's a known pathological regime we must not replicate. At trivial SNR (≥30 dB) the env is too clean to require actual learning. The 5–20 dB window sits on the elbow of the LSQ-accuracy curve where >85% becomes achievable but degrades visibly with noise.

**Current default:** SNR (empirical) = **9.97 dB** (one notch above the >85% elbow at 3–8 dB; well clear of "too clean" 15+ dB and modal-collapse-V3 profile).

**Verified by:** `test_acceptance_criterion_2_snr_in_range` and `test_synthetic_env_acceptance.py::test_criterion_2`.

### 3. Feature-space qualitative similarity to the 17-entry boundary-layer fixture

**Why:** the synthetic env exists as a non-contaminated proxy for the Lehmer corpus. Features must live in the same R^d neighborhood as the 17-entry fixture's `poly_coefficients` + `mahler_measure_dps*` + `n_irreducible_factors` — i.e., a polynomial-coefficient vector with scalar invariants (NOT arbitrary regression features).

**Current implementation:** integer palindromic deg-14 polynomial coefficients (8 free, range [-5, +5]) + 3 Mahler-style derived invariants (`height = Σ|c_i|`, `nnz_free`, `mahler_proxy = log(1 + height/(1+|c_0|))`). Honest disclaimer documented in `_FEATURE_SPACE_CLAIM`: similarity is on record-shape + feature-vector geometry, NOT arithmetic content (`mahler_proxy` is a cheap proxy, not real Mahler measure).

**Verified by:** `test_acceptance_criterion_3_feature_space_claim` (string-keyword match on the claim) and `test_synthetic_env_acceptance.py::test_criterion_3`.

---

## How to verify

```python
from ergon.diagnostic_c.synthetic_env import generate_synthetic_corpus, validate_acceptance_criteria
corpus, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, snr_db=10.0, seed=42)
result = validate_acceptance_criteria(corpus)
assert result["all_pass"], result
```

Or run the acceptance test:

```
python -X utf8 -m pytest ergon/learner/tests/test_synthetic_env_acceptance.py -q
```

## What FAILS this gate

- LSQ < 0.85 → criterion 1 fail (rule not recoverable; env is too noisy or wrong)
- SNR < 5 dB or > 20 dB → criterion 2 fail (modal-collapse risk OR trivially clean)
- Feature space changed to non-polynomial-coefficient form → criterion 3 fail (no longer a proxy for the Lehmer corpus)

If the gate fails, fall back to **17-entry-only training** per James's escalation path on 2026-05-06 ("data issue: drop synthetic env; ship 17-entry-only result"). Do NOT silently train on a failing env; the verdict is uninterpretable.
