# Deep Research Report #158: Heegner Cycles on Shimura Sets — Yuan-Zhang-Zhang Heights at LMFDB Scale

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** Heegner / Shimura curves

## 1. Problem Statement

Gross-Zagier (1986) relates the central derivative L'(E, 1) of the L-function of an elliptic curve E/Q to the Néron-Tate height of a Heegner point P_K(E) constructed from a CM point on the modular curve X_0(N). This identity is the engine behind Kolyvagin's bounds on Sha and the rank-1 BSD theorem.

Yuan-Zhang-Zhang (*The Gross-Zagier formula on Shimura curves*, 2013) generalizes the formula to quaternionic Shimura curves X_B over a totally real number field F, where B is an indefinite quaternion algebra over F. The geometric input is no longer a CM elliptic curve but a Heegner cycle on X_B; the analytic input is a Rankin-Selberg L-derivative L'(f × theta_K, s_0) for a Hilbert modular form f and a CM character of an imaginary CM extension K/F.

Empirical question: for a sample of (E, F, K) where F is real quadratic, E/F has analytic rank 1, and a Heegner point can be constructed via X_B for an appropriate B, do measured Néron-Tate heights match the YZZ predicted RHS within the rationality controlled by the formula's explicit constants?

## 2. Literature

- **Gross-Zagier (1986), *Inventiones*:** original height formula on X_0(N).
- **Zhang (2001), *Annals*:** Heegner points on Shimura curves over Q; first quaternionic generalization.
- **Yuan-Zhang-Zhang (2013), *Annals of Math Studies* monograph:** full quaternionic generalization over totally real F, including Waldspurger constants and local archimedean factors.
- **Bertolini-Darmon-Prasanna (2013), *Duke*:** p-adic Gross-Zagier and anticyclotomic L-functions.
- **Howard (2008), *Inventiones*:** Heegner systems and Iwasawa theory over CM towers.
- **Cornut-Vatsal (2007):** non-triviality of Heegner points along Z_p-extensions, sharp test of YZZ predictions in towers.

## 3. LMFDB Data

- `ec_nfcurves`: E over number fields. Columns: `label`, `field_label`, `conductor_norm`, `rank`, `analytic_rank`, `regulator`, `heegner_index` (when present), `ainvs`, `torsion_order`. Restrict `field_label` to degree-2 totally real (use `nf_fields.degree=2 AND nf_fields.r2=0`).
- `nf_fields`: `disc`, `signature`, `class_number`, `regulator` for F real quadratic.
- `hmf_forms`: HMF over F associated to E via `related_objects`; columns `dimension`, `level_norm`, `weight=[2,2]`, `hecke_ratio`.
- `hmf_hecke`: a_P(f) by prime ideal — needed for L-value reconstruction via Euler product.
- `belyi_passports` / `shimura_curves` (where present): explicit X_B model data; otherwise X_B is implicit via the quaternion algebra ramification set.
- Sage `EllipticCurve(...).heegner_point(D)` and `HeegnerPoints` provide constructions; for F ≠ Q, fall back to Magma `ShimuraCurve` / Voight's package.

## 4. Test Design

**Step 1.** Query `ec_nfcurves` JOIN `nf_fields` WHERE degree=2 AND r2=0 AND analytic_rank=1 AND rank=1 AND regulator IS NOT NULL. Cross-match `hmf_forms.related_objects` to recover f. Random 50 (E, F) pairs, prefer small `conductor_norm` and `field_disc < 100`.

**Step 2.** For each (E, F), pick K = F(sqrt(-d)) imaginary quadratic over F satisfying the Heegner hypothesis (every prime dividing N_E splits or ramifies in K/F). Smallest valid d by absolute discriminant.

**Step 3.** Identify B/F: B ramified exactly at the archimedean place(s) of F where E is "non-split" relative to K and at finite primes from N_E^- (Jacquet-Langlands). When F is real quadratic and E is rank 1, B is typically split at one infinite place — X_B is a curve.

**Step 4.** Construct Heegner cycle / point P_K via Sage/Magma on X_B. Map to E via the modular parametrization X_B → E (Jacquet-Langlands transfer, tracked via `hmf_forms.dimension=1` and matching Hecke eigenvalues).

**Step 5.** Measure h(P_K) using the Néron-Tate `regulator` from ec_nfcurves (rank-1 case: regulator = h(generator); divide by index² if P_K = n·generator).

**Step 6.** Predicted RHS: c(E, K) · L'(E/F, 1) · L(E^{χ_K}/F, 1), where c(E, K) is the YZZ constant (involving 8π², Petersson norm, local Tamagawa-type factors). Compute L-values from `hmf_hecke` Euler product truncation + functional equation.

**Step 7.** Ratio R = h(P_K) / RHS. Predict R = 1 (or rational with denominator dividing a controlled set of bad-prime factors).

**Step 8.** Null: random pairing of (E, F) heights with mismatched (E', F') L-derivatives — R should be log-uniform across decades.

## 5. Falsification

- **Confirms YZZ:** R = 1 ± 10^-3 across 50/50 cells; calibrates LMFDB regulator + L-value pipeline.
- **Publishable deviation:** R is rational but ≠ 1 with a structured denominator → missing automorphic factor (likely a local epsilon or a Petersson normalization convention mismatch in LMFDB).
- **Strong kill:** R irrational or scattered → either Heegner construction is mis-aligned with the modular parametrization, or YZZ does not apply to the chosen (E, K, B) (Heegner hypothesis violated).
- **Null sanity:** shuffled R must show ≫1-decade scatter; otherwise the test is vacuous.

## 6. Budget

~1 day. Postgres + Sage Heegner construction (~3h). Magma fallback for true X_B cases (~2h). L-value arithmetic via Dokchitser (~2h). Stratification + writeup (~3h).

## 7. Expected Outcome

First LMFDB-scale numerical validation of the YZZ formula across real-quadratic base fields. Prior is high match: YZZ is theorem, so deviations indicate convention/normalization gaps in LMFDB columns rather than YZZ failure. **Calibration value is the headline:** once YZZ ratio R is calibrated to ≈1 across a reference set, any anomalous cell becomes a flag.

This is the Heegner-channel feed to **Aporia void-detection**: void-detection scans for absences of expected arithmetic (silent islands in `project_silent_islands.md`). Heegner cycles bridge analytic L-derivative data to curve arithmetic; a calibrated YZZ ratio turns "missing Heegner point" into a measurable void rather than a missing data field. Anomaly cells become candidate void coordinates, feeding Harmonia's adversarial battery.

**Word count: 798**
