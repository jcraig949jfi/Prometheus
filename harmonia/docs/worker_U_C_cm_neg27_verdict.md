# Harmonia worker U_C — CM disc=-27 low-L investigation

**Verdict:** `CM_DISC_m27_REAL_SUB_FAMILY`

**Date:** 2026-04-18

## Provenance note

Due to concurrent-staging races on the shared tree, the two artefacts of this
investigation,

- `harmonia/cm_disc_neg27_investigation.py`
- `cartography/docs/cm_disc_neg27_low_L_investigation_results.json`

were bundled into worker U_D's commit (`ec699fe6` / `6ab62b20`, "Harmonia worker
U_D (BSD-Sha paradox)") instead of my own commit. This file exists to attribute
the authorship of those two artefacts to worker U_C and record the U_C verdict
in its own commit.

## Verdict summary

Investigating T4's (commit `cbe7b623`) 6.66× enrichment of CM discriminant −27
in the rank-0 low-L-tail at conductor decade [1e5, 1e6).

- cm=−27 decade cohort = 14 curves, of which 10 are low-L (71.4%).
- Enrichment vs baseline (10.73% overall) = 6.66×.
- One-sided binomial p-value against baseline = 1.34 × 10⁻⁷.

**Not a generic CM phenomenon.** Max enrichment among other CM discs = 2.15× (cm=−16). Mean of other CMs = 1.61×. cm=−27 is 3.1× above the max of the rest.

| cm  | enrichment |
|-----|-----------:|
| −3  | 1.71×      |
| −4  | 1.27×      |
| −7  | 1.86×      |
| −8  | 1.86×      |
| −11 | 1.33×      |
| −12 | 0.85×      |
| −16 | 2.15×      |
| −27 | **6.66×**  |
| −28 | 1.86×      |

**Not a torsion artefact.** T4 reports torsion=1 general low-L enrichment = 0.96 (null). cm=−27 is 97% torsion=1 (forced by Z[3ω] having ±1 as roots of unity only), but torsion=1 is not itself low-L-enriched, so torsion cannot drive the 6.66×.

## Mechanism

All cm=−27 curves in the scan (32/32 = 100%):

- conductor divisible by 27
- 3 ∈ bad_primes
- torsion = 1

Low-L cm=−27 curves appear only as 3-isogenous pairs — all 10 low-L hits are pair members (286443.d1/d2, 223587.bf1/bf2, 121203.b1/b2, 254043.d1/d2, 155952.bm1/bm2).

| cohort       | leading_term mean | median |
|--------------|------------------:|-------:|
| cm = −27     | 0.79              | 0.54   |
| cm = −3      | 2.00              | 1.74   |
| cm = 0 (non-CM) | 2.90           | 2.26   |

The cm=−27 leading_term distribution is systematically compressed to small values.

## Literature anchoring

The task spec said "disc=−27 corresponds to j=0"; that is wrong. The correct correspondence is:

- cm = −3 → j = 0 (maximal order **Z[ω]**, the canonical y² = x³ + D family)
- cm = −27 → j = −12288000 (non-maximal order **Z[3ω]** of index 3 in Z[ω])

Both share the CM field Q(√−3); their L-functions are Deuring Hecke L-functions of Größencharaktere of Q(√−3).

Relevant anchors:

- Gross, *Arithmetic on elliptic curves with complex multiplication*, LNM 776 (1980).
- Rodriguez-Villegas & Zagier, *Square roots of central values of Hecke L-series* (1993). Treats j=−12288000 explicitly.
- Miller & Yang, *Nonvanishing of family L-functions associated to Hecke Größencharaktere* (2000).

**Mechanism hypothesis.** For the non-maximal order Z[3ω], the real period Ω is larger than for Z[ω] by a factor related to Chowla–Selberg for the non-maximal order. Since LMFDB's `leading_term` is analytically normalized, BSD gives
```
leading_term = Ω · ∏ c_p · |Ш| / |tors|²
```
with tors = 1 for cm = −27 and c₃ typically larger when the cond-3 valuation is large. The net effect on the *analytic* value of L(1, E) — i.e. the quantity reported here — is not uniformly predictable from Ω alone, but the consistent compression of the cm = −27 distribution is consistent with the Hecke-character sum being systematically small for this family (as predicted for a non-maximal-order Hecke L).

## Artefacts

- `harmonia/cm_disc_neg27_investigation.py`
- `cartography/docs/cm_disc_neg27_low_L_investigation_results.json`
