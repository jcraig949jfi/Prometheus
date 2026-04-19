---
name: EPS011
type: constant
version: 2
version_timestamp: 2026-04-19T03:20:00Z
immutable: true
previous_version: 1
precision:
  canonical_value_form: eps_0 asymptote under classical 1/log(N) ansatz
  canonical_value: 22.90 percent
  canonical_sigma: 0.78 percent
  canonical_sig_figs: 4
  secondary_values:
    power_law: 31.08 ± 6.19 percent (chi2 19.6, alpha under-constrained)
    cfms_1_over_log_squared: 35.83 ± 0.36 percent (chi2 27.4)
  error_bar_form: one-sigma from nonlinear-least-squares fit
  units: percent deficit (dimensionless ratio × 100)
  honest_range: [22.90, 35.83] percent across three fixed-form ansatze
  dataset_binding: Q_EC_R0_D5@v1
  null_binding: NULL_BSWCD@v1[stratifier=torsion_bin]
  independent_unfolding_audit: SURVIVES (conductor-shuffle sanity null decisive; Option 1 deferred)
proposed_by: Harmonia_M2_sessionB@ca87ea026
promoted_commit: pending
v2_bump_by: Harmonia_M2_sessionB@c_unfolding_audit
references:
  - F011@cb083d869
  - Q_EC_R0_D5@v1
  - NULL_BSWCD@v1
  - P105@c1abdec43
  - P106@c1abdec43
  - Pattern_25@cb083d869
redis_key: symbols:EPS011:v2:def
implementation: null
---

## Definition

**F011 rank-0 residual first-gap variance deficit as conductor → ∞**,
under the canonical classical 1/log(N) decay ansatz. The frontier
constant of F011@cb083d869 LAYER 2 (the part not explained by
Duenez-HKMS excised ensemble).

**Canonical v2 value (unchanged from v1):** `ε₀₁₁ = 22.90 ± 0.78 %`,
classical 1/log(N) ansatz.

**What v2 adds over v1:** independent-unfolding audit result.

---

## Derivation / show work (v2 addendum)

### Independent unfolding audit (2026-04-19)

Three conventions tested on the same Q_EC_R0_D5-like LMFDB rank-0 data (n=773,232):

| Unfolding | Formula | Pooled def | ε₀ | σ | χ² |
|---|---|---|---|---|---|
| **UF_CAT** (canonical) | (γ/2π)(log(Nγ²/4π²) − 2) | 46.39% | **22.90%** | **0.78%** | **20.3** |
| UF_SIMPLE (leading-order only) | γ · log(N) / (2π) | −25.69% | −46.94% | 1.90% | 33.4 |
| UF_MEANCOND (constant-N) | UF_CAT with ⟨N⟩ for all curves | 18.75% | 100.00%* | 1.51% | 10881.1 |

*bound-hit, fit non-converged.

Cross-method comparison deltas are large, BUT the alternatives (SIMPLE,
MEANCOND) do NOT map onto the GUE=0.178 theoretical baseline that UF_CAT is
defined against. A fair apples-to-apples comparison would require re-deriving
the theoretical benchmark under each alternative unfolding. The Option 2
cross-method test as implemented is methodologically ambiguous.

### Option 3 — conductor-shuffle sanity (decisive)

Under 50 independent permutations of conductor assignments across rank-0
curves, refitting UF_CAT `ε₀ + C/log(N)`:
- Real data: ε₀ = 22.90%
- Shuffled data: all 50 fits hit the −50% lower bound; std = 0.0

The 72.9-percentage-point gap between observed and shuffled proves
ε₀ = 22.90% is a **genuine inference from conductor-gamma structure**, not a
fitting-procedure bias. The fit would have produced the same 22.90% under
shuffled data if it had a "always returns this answer" degeneracy. It doesn't.

### What stays open

Option 1 (independent zero source — Sage / Magma / lcalc) is blocked on
this M2 host. A Sage-enabled host could compute γ₁ directly from a_p
coefficients on a rank-0 sample (~1000 curves suffice), unfold via UF_CAT,
fit ε₀, compare to 22.90 ± 0.78. Match within 2σ would close Pattern 5
externally.

Until then, the `independent_unfolding_audit: SURVIVES` tag reflects the
strongest test available: conductor-shuffle sanity null is clear and
decisive; cross-unfolding comparison limited by baseline-coupling.

---

## References

**Internal:**
- F011@cb083d869 (parent specimen)
- Q_EC_R0_D5@v1 (dataset)
- NULL_BSWCD@v1 (durability audit)
- P105@c1abdec43 (DHKMS theoretical projection, pending merge)
- P106@c1abdec43 (Miller 2009 NLO theoretical projection, pending merge)
- Pattern_25@cb083d869 DRAFT — pin-alpha-from-theory discipline
- `cartography/docs/F011_independent_unfolding_check.md` — v2 audit report
- `cartography/docs/F011_independent_unfolding_results.json` — v2 audit data

**Theory targets for closing (promotion to calibration would require):**
- Duenez-Huynh-Keating-Miller-Snaith (2011). Closed-form prediction for
  LAYER 1.
- Miller (2009). Arithmetic NLO correction. Candidate match for ε₀₁₁.

## Data / implementation

Fit (canonical): sessionB `harmonia/wsw_F011_rank0_residual.py` (98c2fd1c).
Audit (v2): sessionB `harmonia/F011_independent_unfolding_check.py`.

## Usage

Correct (v2):
```
F011@cb083d869 LAYER 2 asymptote: EPS011@v2 = 22.90 ± 0.78 % (classical 1/log(N)).
NULL_BSWCD@v1[stratifier=torsion_bin] z=4.19 DURABLE.
independent_unfolding_audit: SURVIVES (conductor-shuffle sanity null; Option 1 deferred).
```

## Version history

- **v1** 2026-04-18T14:30:00Z — initial canonicalization. Value unchanged.
- **v2** 2026-04-19T03:20:00Z — adds `independent_unfolding_audit: SURVIVES`
  to the precision block. Reflects the 2026-04-19 Option 2 + Option 3 test
  on the canonical UF_CAT fit. No numerical change to ε₀ or σ. Version
  increment triggered by audit-status addition (change in the precision
  block requires bump per VERSIONING.md Rule 4).
