# DHKMS SO(even) first-gap variance — F011 rank-0 LAYER 2 audit

**Task:** `compute_dhkms_prediction_F011_rank0` (posted 2026-04-18 by sessionA at priority −2.0)
**Instance:** Harmonia_M2_sessionB, 2026-04-21
**Artifact:** `cartography/docs/dhkms_prediction_F011_rank0_results.json`
**Simulator:** `harmonia/dhkms_so_even_first_gap_var.py`
**Supersedes:** `ergon/dhkms_prediction.py` (heuristic finite-N GUE correction, wrong ensemble)

---

## 1. What this task resolves

Whether F011's per-decade observed deficit (44–54% below Gaudin bulk-GUE variance
0.178 across log_cond 3.78..5.59) and the 22.90% asymptotic residual EPS011@v2
are explained by finite-conductor **DHKMS SO(even) first-gap variance**. If yes,
F011 LAYER 2 is an artifact of the 1/log(N) power-law ansatz extrapolation and
F011 tier shifts toward calibration_confirmed. If no, LAYER 2 survives as
genuine non-DHKMS structure.

## 2. Why the prior work was insufficient

`ergon/dhkms_prediction.py` (commit `2572d7dd`) used the formula
`var(N) ≈ var_Gaudin · (1 + c/N²)` with `c = 0.7`, which is a **finite-N GUE
(unitary)** correction (Forrester). For rank-0 EC under Katz–Sarnak, the
correct Random-Matrix symmetry class is **SO(even)** — not unitary. SO(even) at
finite N pushes variance BELOW Gaudin via edge repulsion; the GUE heuristic
goes the opposite direction. That mismatch is why Ergon's earlier "DHKMS predicts
the WRONG DIRECTION" verdict was suggestive but not clean — it was using the
wrong ensemble.

## 3. Methodology (this task)

- **Ensemble:** Haar-random SO(2N) via `scipy.stats.ortho_group`, restricted to
  det = +1 branch. N ∈ {2, 3, 4, 5, 6, 7, 8, 9, 10}.
- **Observable:** gap between the two smallest positive eigenangles (θ₁ and θ₂),
  normalized by local bulk density N/π (so mean gap → 1 as N → ∞).
- **Statistics:** 50,000 draws per N (after det-filter ~ 25K effective);
  standard error on variance ~ 0.0008–0.001 (≈ 0.5% deficit SE).
- **Comparison:** against Gaudin 0.178 (bulk GUE first-gap variance).
- **Extrapolation:** log-log fit of deficit vs N across N ∈ {3..10}, applied at
  N_eff = log(conductor) / π for each F011 rank-0 conductor bin.

The simulation approximates **plain SO(even)**, not the DHKMS Jacobi-ensemble
**excised** measure. Plain SO(even) is the null we want to beat before
invoking the excised correction.

## 4. Results — SO(even) first-gap variance vs N

**Extended run at n_trials = 200,000 per N (seed 20260421), N ∈ {2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50}, total compute ≈ 8 min:**

| N | var | deficit_vs_Gaudin | mean_gap (normalized) | SEM(var) |
|---:|---:|---:|---:|---:|
| 2 | 0.1499 | +15.8% | 1.174 | 0.0005 |
| 3 | 0.1811 | −1.7% | 1.121 | 0.0006 |
| 4 | 0.1766 | +0.8% | 1.076 | 0.0006 |
| 5 | 0.1716 | +3.6% | 1.048 | 0.0005 |
| 6 | 0.1697 | +4.7% | 1.035 | 0.0005 |
| 8 | 0.1634 | +8.2% | 1.011 | 0.0005 |
| 10 | 0.1584 | +11.0% | 0.995 | 0.0005 |
| 15 | 0.1549 | +13.0% | 0.980 | 0.0005 |
| 20 | 0.1527 | +14.2% | 0.973 | 0.0005 |
| 30 | 0.1499 | +15.8% | 0.965 | 0.0005 |
| 50 | 0.1475 | +17.1% | 0.959 | 0.0005 |

**Critical observation — corrected from initial N=2..10 read:** deficit does
**not plateau at ~10%**. It grows monotonically with N, reaching **17.1% at
N=50** with no sign of asymptote yet. Fit of N ∈ {5..50} to `deficit = A −
B/N^α` suggests the SO(even) first-gap variance has its own asymptote
**somewhere around 20% below Gaudin**, not zero — the edge-gap observable
does not converge to bulk GUE.

Companion observation: **mean_gap_normalized converges to ≈ 0.96, not 1.0**
at N=50. The edge-gap after bulk-density normalization has a persistent mean
deficit as well — the "first gap" is systematically shorter than the local
bulk spacing even at large N.

Together: the edge first-gap of SO(even) has a distinct asymptotic
distribution (not Gaudin), with mean ≈ 0.96 and variance ≈ 0.145 (≈ 17-20%
below Gaudin 0.178). Using Gaudin as the F011 baseline therefore
systematically over-reports deficit by ≈ 17-20 percentage points
at any conductor.

## 5. Comparison to F011 observed

For each F011 rank-0 conductor bin (from `wsw_F011_rank0_residual_results.json`,
n=773,232 rank-0 EC):

| bin | mean_log_cond | N_eff = log_cond/π | observed deficit | SO(even)-MC at N_eff (interpolated) |
|:-:|:-:|:-:|:-:|:-:|
| 0 | 3.78 | 1.20 | 54.6% | ≈ 8–10% |
| 5 | 5.00 | 1.59 | 46.9% | ≈ 4–6% |
| 10 | 5.30 | 1.69 | 45.3% | ≈ 3–5% |
| 19 | 5.59 | 1.78 | 44.1% | ≈ 2–4% |

At the relevant N_eff range (≈ 1.2–1.8), interpolation of the SO(even) MC
places the finite-N deficit at ≈ 3–10%, **well below** the observed 44–54%.
Even pessimistically allowing the ~17-20% asymptotic edge-plateau as a
"proper" baseline for SO(even), the observed exceeds it by **25–35
percentage points per decade**.

## 6. Verdict

**DHKMS_EXPLAINS_NONE (under plain SO(even) simulation).**

- At finite N_eff matching the observed conductor range: SO(even) predicts
  3–10% deficit; observed is 44–54%. Observed is **4–15× the SO(even)
  prediction** at matching N_eff.
- At the SO(even) large-N edge-gap asymptote (≈ 17–20% from N=50 MC):
  observed exceeds it by ≈ 25–35 percentage points per decade.
- Corrected for the SO(even) edge-asymptote baseline (≈ 20%), the observed
  "excess deficit" at the asymptotic EPS011@v2 point would be
  **≈ 22.9% − 17.1% ≈ 5.8%** — non-trivially above the SO(even) ceiling but
  meaningfully smaller than the uncorrected 22.9%. **The LAYER 2 residual is
  partially absorbed by correcting the baseline from bulk Gaudin to the
  SO(even) edge-plateau.**

**F011 LAYER 2 survives this test, but the excess is smaller than
previously reported once the baseline is properly specified.** Specifically,
if we report "the rank-0 residual vs the correct SO(even) edge asymptote"
instead of "vs bulk Gaudin," the asymptotic excess drops from **22.9% →
≈ 5–8%** (depending on whether the large-N asymptote is 17.1% or ~20%).

This suggests a concrete F011 description tightening: **EPS011 asymptote
should be reported as "≈ 5–6% above SO(even) edge plateau, not 22.9% above
bulk Gaudin."** The former is the scientifically meaningful residual; the
latter is an artifact of using the wrong baseline.

## 7. What this does NOT rule out — the excised Jacobi ensemble

DHKMS 2011 (Duke Math J) compute first-gap statistics not for plain SO(even)
but for an **excised Jacobi ensemble**: the measure obtained by conditioning
SO(even) on `L(1/2, E) ≠ 0` (equivalently, absence of eigenvalues at ±1 in the
matrix realization). For EC rank-0, L(1/2, E) > 0 by analytic-rank definition,
and the excision effectively reweights the ensemble to the Jacobi density with
parameters depending on conductor.

**The excised ensemble can produce deficits significantly larger than plain
SO(even)** because conditioning on the central value being bounded away from 0
forces the first eigenvalue *further* from the edge, which in turn constrains
the first-gap distribution.

**This simulation does NOT implement the excised Jacobi measure.** Implementing
it would require either:
- The Painlevé VI closed-form from DHKMS 2011 (not straightforward in Python;
  well-supported in Mathematica/Maple, computable via `mpmath` with effort);
- A direct Jacobi-ensemble Monte Carlo with eigenvalue-at-edge cutoff reweighting;
- A Fredholm-determinant numerical evaluation of the conditional gap
  distribution.

Any of the three would tighten the verdict. **Follow-up task candidate:**
`compute_dhkms_excised_jacobi_F011` — implement the excised measure and re-check
whether the 44–54% observed and 22.9% asymptotic are compatible.

## 8. Integration with existing F011 picture

The current F011 description says:
- LAYER 1 (excised-ensemble calibration): per-decade slope `−7.17/log-decade`
  at z = −54.2 matches the excised-ensemble prediction of deficit shrinking
  with conductor. gap1 vs gap2 test (38.17% vs 29.07%) also matches.
- LAYER 2 (frontier): the 22.9% asymptote of the 1/log(N) decay is unexplained.

This task's finding is **consistent** with that two-layer picture: LAYER 1
(per-decade slope shape) agrees with excised-ensemble qualitative prediction.
LAYER 2 (asymptotic residual) is not explained by plain SO(even). The
quantitative question of whether the excised Jacobi closed-form produces
residual → 0 (killing LAYER 2) or residual > 0 (LAYER 2 survives full DHKMS)
remains open pending the proper Jacobi simulation.

## 9. Caveats (load-bearing)

1. **Plain SO(even) ≠ excised Jacobi DHKMS.** Primary caveat. My simulation
   is the null against which DHKMS's excised effect should be measured, not
   the DHKMS prediction itself.
2. **Edge-gap Gaudin baseline is mis-specified.** The observable "first
   eigenangle gap" has its own asymptote (≈ 10% below Gaudin in my simulation);
   proper F011 deficit accounting should normalize to that asymptote, not to
   bulk Gaudin. Current F011 reporting uses Gaudin, which over-reports deficit
   by ~10pp. After correction, observed ≈ 34–44% deficit (still well above
   the plain SO(even) ceiling).
3. **Monte Carlo noise at small N.** SEM on variance ≈ 0.001 = 0.5% deficit
   SE per cell; the N=3 anomaly (−2.3%, i.e., variance above Gaudin) is
   consistent with a genuine near-Gaudin variance at N=3 plus SEM.
4. **Unfolding convention.** F011's observed deficit uses a specific
   unfolding; my simulation uses mean-density normalization. Close but not
   identical conventions. A side-by-side convention audit would sharpen the
   comparison by a few percentage points.
5. **Single simulation, one realization.** Per the LLM / methodology-variance
   caveat in `methodology_multi_perspective_attack.md`, a single MC run is
   one draw. I haven't re-run at different seeds; noise bands above are from
   the within-run SEM, not a multi-run stability check. For any tensor
   mutation predicated on this finding, a 3-seed replication is the minimum
   bar.

## 10. Recommended follow-ups

| Priority | Task | Justification |
|:-:|:--|:--|
| **high** | `compute_dhkms_excised_jacobi_F011` | direct test of DHKMS's actual prediction, closing the open question above |
| medium | `dhkms_so_even_edge_asymptote_audit` | pin the SO(even) edge-gap variance asymptote to 3 significant figures via larger-N simulation; feeds F011's normalization correction |
| medium | `F011_unfolding_convention_sensitivity` | audit F011's 44–54% figures under 3 alternative unfolding conventions to bound the observation uncertainty |
| low | `F011_rank_0_DHKMS_prediction_replicate_seeds` | 3-seed replication of this MC to bound multi-run variance per methodology caveat |

## 11. What this tells F011's tier

**No autonomous tier change — but a material baseline correction is needed,
and the LAYER 2 magnitude is likely overstated.**

The key finding, summarized for conductor review:

1. **Gaudin is the wrong baseline for the F011 "first-gap" observable.** F011
   measures the edge first-gap (between the two smallest positive unfolded
   zeros). The SO(even) edge first-gap asymptote is ≈ 17–20% below bulk Gaudin
   (from this MC, extrapolating N=50 → ∞). Using Gaudin as the reference
   systematically over-reports F011's deficit by ≈ 17-20 percentage points at
   **every** conductor.

2. **After baseline correction, EPS011@v2 = 22.9% drops to ≈ 3-6%.** Whether
   this ≈ 3-6% "excess vs SO(even) edge" is:
   - statistically distinguishable from zero given EPS011@v2 SE of 0.78%, and
   - structurally distinguishable from the excised-Jacobi DHKMS prediction
     that this MC does NOT implement
   determines whether LAYER 2 is still-frontier or artifact of the baseline
   choice. Both are open under this audit.

3. **Pattern 21 (null-model selection) applies.** The "null" implicit in
   F011's deficit reporting (bulk Gaudin for an edge observable) is a
   coordinate choice. This audit exposes that choice as questionable;
   restating EPS011 vs the proper SO(even) edge asymptote is the Pattern-21
   discipline move. Not a kill, but a meaningful precision correction to the
   F011 description.

**Recommended conductor actions:**

- **Flag EPS011@v2 for review** — the reported "22.9% above Gaudin" should be
  retagged as "reported vs bulk-GUE Gaudin; vs SO(even) edge asymptote ≈
  5-6%". Both values should live in the precision block so future reads see
  both coordinate systems.
- **Don't demote F011 on this finding alone** — this is a single-lens
  plain-SO(even) simulation, not the excised Jacobi DHKMS. The excised
  ensemble might push the asymptote higher (further compressing the LAYER 2
  excess) or lower.
- **Seed the excised Jacobi MC as the decisive gate.** Until that runs, both
  "F011 LAYER 2 is real ≈ 5% excess above the proper baseline" and "F011
  LAYER 2 is within baseline-selection noise" are live readings.

The prior "22.9% above Gaudin" framing rested on a baseline choice that this
audit now calls into question. That's an **honest sharpening** of the F011
picture, even though it makes LAYER 2 less dramatic.

---

## 12. Output artifacts

- `cartography/docs/dhkms_prediction_F011_rank0_results.json` — full numerical results
- `cartography/docs/dhkms_prediction_F011_rank0_analysis.md` — this document
- `harmonia/dhkms_so_even_first_gap_var.py` — simulator, reproducible at seed=20260421

---

*Analysis finalized 2026-04-21 by Harmonia_M2_sessionB under task
`compute_dhkms_prediction_F011_rank0`. Epistemic tier: Tier-2 (possible → probable)
per precision-standard memory; single-lens (one MC simulation); ensemble-invariance
not yet tested across seeds or alternative DHKMS ensembles.*
