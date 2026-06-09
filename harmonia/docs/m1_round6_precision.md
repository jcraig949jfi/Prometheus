# M1 Round 6 — Precision Era
## Everything from here is precision, not exploration.

The landscape phase is over. 11/13 claims killed. The only surviving metric is TT-Cross bond dimensions with Megethos zeroed. Here's what needs doing.

---

## TASK 1: Megethos-Zeroed Pairwise Sweep

The ONLY valid structural metric is TT-Cross with feature 0 (Megethos) zeroed out in both domains. Every previous sweep used uncontrolled features.

Rerun the pairwise sweep for the top 15 domains:
```python
# For each pair: zero feature 0, run TT-Cross, report rank
# Only bonds with rank > 1 after Megethos zeroing are real
```

Domains to include: elliptic_curves, number_fields, genus2, modular_forms, lattices, ec_zeros, dirichlet_zeros, rmt, dynamics, chemistry, spectral_sigs, operadic_sigs, groups, oeis, bianchi

Report a clean bond matrix where every entry has Megethos controlled for.

---

## TASK 2: Montgomery-Odlyzko with Unfolded Zeros

The adversarial session flagged this: our stored zeros need unfolding. Raw zeros have non-uniform density; normalized gaps require density estimation.

Steps:
1. Load the 31K EC zero vectors from Charon DuckDB
2. For each curve, unfold zeros: s_n = N(gamma_n) where N(T) = (T/2pi) * log(T/(2pi*e))
3. Compute spacing statistics on the UNFOLDED zeros
4. Compare to GUE predictions: variance=0.18, P(s)=(32/pi^2)*s^2*exp(-4s^2/pi)
5. Report with proper null (Poisson) and proper normalization

This is the Montgomery-Odlyzko test done RIGHT. If the unfolded zeros match GUE, it's a precision anchor. If they don't match after unfolding, our raw-zero results were artifacts.

---

## TASK 3: Sato-Tate with Large Primes from Postgres

The adversarial session found Sato-Tate variance is 24% low using small primes (p=2-23). Fix this by using larger primes from the Postgres MF traces.

```python
import psycopg2
conn = psycopg2.connect(host='localhost', dbname='lmfdb_local', user='lmfdb')
# or: host='devmirror.lmfdb.xyz' if local clone isn't ready
cur = conn.cursor()
cur.execute('''
    SELECT label, level, traces FROM mf_newforms 
    WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
    LIMIT 5000
''')
# traces[p-1] = a_p. Use primes p = 100-997 for asymptotic convergence.
# Compute a_p / (2*sqrt(p)), check if distribution matches semicircle.
```

Target: Sato-Tate variance within 5% of 1.0 (currently 24% off at small primes).

---

## TASK 4: Brauer-Siegel from High-Discriminant NF

The adversarial session found Brauer-Siegel goes the WRONG direction in LMFDB because high-degree fields have small discriminants (database bias).

Fix: query high-discriminant fields from Postgres.
```python
cur.execute('''
    SELECT degree, disc_abs, regulator, class_number 
    FROM nf_fields
    WHERE degree = 2 AND disc_abs > 1000000
    ORDER BY disc_abs DESC
    LIMIT 10000
''')
# Compute log(h*R) / log(sqrt(d)) for each field
# Should approach 1 as disc -> infinity (Brauer-Siegel)
```

---

## TASK 5: Knot GUE Verification (Clean Roots)

M2 found Alexander root spacings match GUE variance at 0.180 = exact. But the roots were computed from Z-scored coefficients, which may distort them.

Verify with CLEAN root computation:
1. Load raw Alexander polynomial coefficients (not Z-scored) from knots.json
2. Compute roots using numpy.roots on the actual integer coefficients
3. Project onto unit circle, compute angular spacings
4. Normalize by mean spacing
5. Report variance, skewness, kurtosis, P(s<0.1)

If variance is still 0.18 ± 0.01 with clean coefficients, the GUE connection is real.

Also: compute for Jones and Conway polynomials separately. If ALL three knot polynomials show GUE spacing, it's universal to knot topology, not specific to Alexander.

---

## TASK 6: BSD Calibration from Postgres

We verified rank = analytic_rank for 3.8M curves (100%). Now test the full BSD formula:

```python
cur.execute('''
    SELECT e.conductor, e.rank, e.torsion, e.regulator,
           m.special_value, m.real_period, m.sha_an, m.tamagawa_product
    FROM ec_curvedata e
    JOIN ec_mwbsd m ON e.lmfdb_label = m.lmfdb_label
    WHERE e.rank = 0 AND m.special_value IS NOT NULL
    LIMIT 50000
''')
# For rank-0 curves: L(E,1) = Omega * |Sha| * prod(c_p) / |torsion|^2
# Verify this ratio is 1.0 (or close) across 50K curves
```

This is the BSD formula at scale. If the ratio is consistently 1.0, BSD is verified computationally for rank-0 curves.

---

## TASK 7: Load the Sleeping Beauty Data

High-value files we've never loaded:
- `g2c_endomorphisms.json` (37.8MB) — endomorphism ring structure for all 66K genus-2 curves
- `smf_fc.json` (648MB) — 26K Siegel modular form Fourier coefficients
- `hmf_forms.json` (130MB, full version) — 368K Hilbert modular forms with all fields

Each of these could be a new domain with native invariants. The endomorphism data especially — it adds Arithmos-type features to genus-2 that might survive the Megethos-zeroed test.

---

## TASK 8: Cross-Validate Knot GUE against L-Function GUE

If both knot root spacings AND L-function zero spacings show GUE, are they the SAME GUE?

1. Compute spacing statistics for the 31K EC zeros (properly unfolded from Task 2)
2. Compute spacing statistics for the 5K knot roots (clean from Task 5)
3. KS test: are the two spacing distributions drawn from the same distribution?
4. If KS fails to reject: knots and L-functions share the same GUE universality class
5. If KS rejects: they're in different universality classes (GUE vs GOE vs GSE?)

This is the deepest cross-domain test we can run. Two completely different mathematical objects (knot polynomials and L-functions) producing the same random matrix statistics.

---

## Priority

1. Task 5 (clean knot GUE) — validates/kills the hottest finding
2. Task 1 (Megethos-zeroed sweep) — the new clean bond matrix
3. Task 2 (unfolded Montgomery-Odlyzko) — precision calibration
4. Task 8 (cross-validate knot vs L-function GUE) — the deepest test
5. Task 6 (BSD at scale) — another calibration anchor
6. Task 3 (Sato-Tate large primes) — fixes known calibration gap
7. Task 4 (Brauer-Siegel) — fixes database bias
8. Task 7 (load sleeping beauty data) — new domains for precision sweep
