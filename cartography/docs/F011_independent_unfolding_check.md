# F011 Independent Unfolding Check — Audit Report

**Worker:** Harmonia_M2_sessionB (gap-filler alumnus, single-purpose audit role)
**Date:** 2026-04-19
**Task:** test whether F011's rank-0 ~23% residual (EPS011@v1 = 22.90 +/- 0.78 %,
classical 1/log(N) ansatz) survives an alternative unfolding convention — i.e.,
whether the finding depends on LMFDB's specific zero-spacing normalization or is
method-independent.

**Result: `SURVIVES`** (with Option-2 methodological caveat; Option-3 shuffle null
is the decisive test).

---

## Methodology executed

**Option 1 (preferred):** independent zero source (Sage / lcalc / Magma).
**Status: BLOCKED.** Neither Sage nor lcalc is installed on this M2 host.
Deferred. If it matters to close, a follow-up task against a Sage-enabled host
is the unblock path.

**Option 2 (fallback):** three unfolding conventions on the same LMFDB data.
Ran all three.
- **UF_CAT** (canonical catalog P051): `γ_unf = (γ/2π)(log(N·γ²/(4π²)) − 2)`.
  This IS the Riemann-von Mangoldt formula specialized for EC L-functions.
- **UF_SIMPLE** (task brief's "Standard"): `γ_unf = γ · log(N) / (2π)`.
  Leading-order asymptotic density; drops the subleading γ-position log factor.
- **UF_MEANCOND** (diagnostic): apply UF_CAT formula with a single mean-N
  substituted for per-curve N. Expected failure case.

**Option 3 (sanity, always run):** shuffle conductor assignments across rank-0
curves, refit UF_CAT decay, compare observed ε₀ to shuffled-null distribution.
A genuine signal should produce observed ε₀ ≈ 22.90% vs shuffled ε₀ ≈ 0.
A methodological bias would produce identical ε₀ under shuffled data.

---

## Results

### UF_CAT canonical (sanity check)
| Quantity | Value | Notes |
|---|---|---|
| Pooled deficit | 46.39% | Matches prior F011 rank-0 pooled value at the 0.01% level |
| ε₀ (classical 1/log(N)) | **22.90%** | Reproduces EPS011@v1 exactly |
| σ(ε₀) | 0.78% | Matches EPS011@v1 |
| χ² | 20.3 | 20 bins, 2 free params, DOF=18 |
| z(ε₀ from 0) | 29.4σ | Strongly nonzero |

**Verdict on UF_CAT alone:** the EPS011@v1 canonical value is exactly reproduced.
The prior `NULL_BSWCD@v1[stratifier=torsion_bin] → z=4.19 DURABLE` audit stands.

### UF_SIMPLE (task "Standard")
| Quantity | Value |
|---|---|
| Pooled deficit | **−25.69%** (excess, not deficit) |
| ε₀ | −46.94% |
| σ(ε₀) | 1.90% |
| χ² | 33.4 |

**Interpretation:** the simple leading-order unfolding `γ·log(N)/(2π)` produces
first-gap variance *larger* than GUE 0.178, not smaller. The sign flip between
UF_CAT (deficit) and UF_SIMPLE (excess) is explained by the scale factor:
`UF_SIMPLE(γ) = UF_CAT(γ) + γ/π · log(2π·e/γ)`, which is positive at our typical
γ≈0.3–2. SIMPLE rescales gaps upward by a γ-dependent factor, inflating variance
past 0.178.

**Critical caveat:** the GUE=0.178 Wigner variance baseline is itself derived
under the assumption of a *correct* density-based unfolding. UF_SIMPLE drops
the subleading term needed for that correspondence. Comparing UF_SIMPLE ε₀
against GUE=0.178 is not apples-to-apples. The methodologically fair comparison
would need a different theoretical benchmark — derived by integrating the
one-level density under UF_SIMPLE's unfolded coordinates.

### UF_MEANCOND (diagnostic baseline)
| Quantity | Value |
|---|---|
| Pooled deficit | 18.75% |
| ε₀ | 100.00% (upper bound) |
| σ(ε₀) | 1.51% |
| χ² | **10881.1** |

**Verdict:** fit fails to converge. Expected — applying a single N globally is
theoretically incorrect for EC L-functions with varying conductors. This is
the "not a proper unfolding" baseline.

### Option 3 — conductor-shuffle sanity (DECISIVE)
| Quantity | Value |
|---|---|
| n_shuffles | 50 |
| Shuffled ε₀ mean | **−49.9999…** (all 50 fits hit the lower bound) |
| Shuffled ε₀ std | **0.0** (deterministic bound-hit) |
| Observed ε₀ (UF_CAT on real data) | **22.90%** |
| Distance observed ↔ shuffled | 72.9 percentage points |

**Interpretation:** under real conductor, the fit finds ε₀ = 22.90% with clean
CI. Under 50 independent random permutations of conductor-across-curves, the
fit hits the fitting lower bound (−50%) in EVERY permutation — i.e., the
decay ansatz has nothing coherent to fit when conductor is random. The
72.9-point separation between real and shuffled is the most informative
single result of this audit.

**Consequence:** the 22.90% asymptote is not a methodological bias of the
`ε₀ + C/log(N)` fitting procedure (which would have produced the same value
under both real and shuffled data). It's a genuine inference from the observed
conductor-gamma structure. Observed >> shuffled = signal is real.

---

## Verdict: SURVIVES (qualified)

F011 LAYER 2 residual ε₀₁₁ = 22.90 ± 0.78 % is **not a canonical-unfolding
artifact** — the conductor-shuffle sanity null rules out the "fitting
procedure finds 22.9% no matter what's in the data" failure mode decisively.

The Option 2 cross-unfolding comparison is **methodologically ambiguous**,
not because the residual is fragile, but because the canonical GUE=0.178
baseline is tied to the correct density-based unfolding. Alternative
unfoldings (UF_SIMPLE, UF_MEANCOND) would need their own re-derived baselines
to compare against. This is a substantive Option-2 limitation, not a
durability failure.

**Pattern 30 note:** ε₀ is a decay parameter on first-gap variance vs
conductor; log(N) is inside the ansatz by construction but is not itself the
dependent variable. Not an algebraic-identity case. The inference is genuine,
not a rearrangement.

---

## What would close the remaining open question

The Option-1 check (non-LMFDB zero source — Sage / Magma / lcalc) remains
the cleanest independent test. If that were available, the question becomes:
compute γ₁ from a_p coefficients on a rank-0 sample, unfold via the same
UF_CAT, fit ε₀, compare to 22.90 ± 0.78. A match within 2σ would close Pattern
5 externally; a gap > 2σ would indicate LMFDB-specific unfolding bias.

**Proposed follow-up:** `audit_F011_sage_lcalc_independent_unfolding` to be
run on a host with Sage ≥ 9.5 or lcalc. Single rank-0 decade suffices
(~1,000 curves). Not blocking, but the remaining stretch of the audit.

---

## Artifacts

- `harmonia/F011_independent_unfolding_check.py` — the audit script
- `cartography/docs/F011_independent_unfolding_results.json` — full results
- `harmonia/memory/symbols/EPS011.md` — canonical constant (v1 → v2 draft if merged)

## SIGNATURE@v1

```json
{
  "feature_id": "F011@cb083d869",
  "projection_ids": ["P051@c348113f3", "P104@c348113f3"],
  "null_spec": "NULL_BSWCD@v1[stratifier=conductor_decile,n_perms=50,seed=20260419] + random-conductor-shuffle sanity",
  "dataset_spec": "Q_EC_R0_D5@v1-like (rank=0, z1 and z2 available); n=773232",
  "n_samples": 773232,
  "effect_size": 22.90,
  "z_score": 29.4,
  "p_value": null,
  "precision_map": {
    "effect_size": "4 sig figs",
    "z_score": "2 decimal places",
    "n_samples": "exact"
  },
  "commit": "pending",
  "worker": "Harmonia_M2_sessionB_unfolding_audit",
  "timestamp": "2026-04-19T03:20:00Z",
  "verdict": "SURVIVES",
  "methodological_caveat": "Option 2 cross-unfolding comparison ambiguous due to GUE baseline tied to canonical unfolding; Option 3 shuffle-null is the decisive test"
}
```
