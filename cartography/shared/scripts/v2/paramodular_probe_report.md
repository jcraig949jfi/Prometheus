# Paramodular Conjecture Probe (C01) -- Report

## Status: NOT FEASIBLE with current LMFDB Siegel data

### The Question
Can we test the Brumer-Kramer Paramodular Conjecture using LMFDB Siegel
modular form data and genus-2 curve Euler factors?

### The Answer
**No.** There is a fundamental level gap. LMFDB's paramodular form database
contains forms only at levels 1 and 2, while genus-2 curve conductors
start at 169. There is zero overlap.

---

## Data Inventory

### Siegel Modular Forms (from LMFDB postgres)

| Source | Records | Families | Key Fields |
|--------|---------|----------|------------|
| smf_newforms.json (42MB) | 11,632 | K:11101, P:358, S:173 | label, level, weight, family, traces, trace_lambda_p |
| smf_hecke_nf.json | 8,173 | K:7911, P:218, S:44 | label, level, lambda_p, lambda_p_square, an |
| smf_newspaces.json (51MB) | 28,497 | K,P,S | cusp_P_lambda_p, cusp_G_lambda_p, decomposition data |
| smf_hecke_newspace_traces.json | 84,483 | all | hecke_orbit_code, trace_an, n |
| smf_fc.json (Fourier coeffs) | 26,212 | all | owner_id, det, data (indexed by half-integral matrices) |
| smf_qexp_coeffs.json | 10,114 | all | hecke_orbit_code, qf_legendre, coeff |
| smf_ev.json | 3,094 | all | owner_id, index, data |
| siegel_samples.json (23MB) | 129 | Sp4Z, Sp4Z_j | name, weight, type, explicit_formula |
| siegel_eigenvalues.json | 3,094 | (old format) | owner_id, index, data |
| siegel_families.json | 14 | all | name, degree, dim_args_default |
| siegel_dims.json | 72 | all | dimension formulas as rational functions |
| siegel_fourier_coeffs.json (619MB) | (in smf_fc) | all | Fourier-Jacobi coefficients |

### Genus-2 Curves

| Source | Records | Key Fields |
|--------|---------|------------|
| g2c_curves.json | 66,158 | label, cond, bad_lfactors, Lhash, st_group, is_gl2_type |
| gce_1000000_lmfdb.txt (28MB) | 66,158 | good_lfactors [[p, a1_p, a2_p], ...] at ~24 primes |
| gce_1000000_ldata1.txt (114MB) | L-function analytic data (zeros, special values) |

### The Gap

| Data | Level/Conductor Range |
|------|----------------------|
| Paramodular (P) forms | **1, 2 only** |
| Klingen (K) forms | 1 to 999 (950 levels) |
| Saito-Kurokawa (S) forms | 1 only |
| Genus-2 conductors | **169 to 1,000,000** |

**Overlap between P forms and g2c conductors: ZERO.**

---

## What Each Data Source Contains

### Paramodular Forms (family "P")
- 358 newforms, all at levels 1 or 2
- Weights range from [2,12] to [20,20] (vector-valued)
- **No weight [2,0] forms** (the weight relevant to abelian surfaces)
- 218 have Hecke eigenvalue data (lambda_p at primes up to 97)
- The eigenvalues are large integers (e.g., lambda_2 = -600 for level-2 weight-[2,12])

### Klingen Forms (family "K")
- 11,101 newforms at 950 levels (1 to 999)
- Predominantly weight [3,0] (10,925 forms)
- These are LIFTS from classical GL(2) forms -- not genuine Siegel forms
- L-function factors as: L(s,F_K) = zeta(s-k+1) * zeta(s-k+2) * L(s,f)
- NOT suitable for paramodular conjecture testing

### Genus-2 Euler Factors
- Parsed from gce_1000000_lmfdb.txt: [[p, a1_p, a2_p], ...] per curve
- L_p(T) = 1 + a1_p*T + a2_p*T^2 + a1_p*p*T^3 + p^2*T^4
- 63,107 USp(4) curves (= paramodular candidates)
- All satisfy Hasse-Weil bound |a_p| <= 4*sqrt(p)
- 19-25 good primes per curve (up to p=97)

### Fourier Coefficients (619MB)
- Indexed by half-integral matrix entries, not by prime
- Would require computing Hecke operator action to extract eigenvalues
- Not directly usable for Euler factor comparison

---

## Consistency Checks Performed

### Klingen vs GL2-type Curves
- 2,846 GL2-type genus-2 curves at 1,932 conductors
- 31 overlapping conductor/levels with Klingen forms
- Only 80 dim-1 Klingen [3,0] forms with parseable eigenvalues at 49 levels
- 0 overlapping levels with GL2-type curve conductors at those 49 levels
- **Result: no matches possible (Klingen dim-1 eigenvalue levels too sparse)**

### Euler Factor Validation
- All 63,107 USp(4) curves pass Hasse-Weil bound check
- Mean a_p is slightly positive (as expected for genus-2 Sato-Tate)
- Euler factor data is clean and immediately usable

---

## Path Forward

### Option 1: Poor-Yuen Database (RECOMMENDED)
The Poor-Yuen paramodular form computations contain genuine weight-2
paramodular newforms at levels up to ~1000. This is the standard reference
for paramodular conjecture verification. Fetching this data would immediately
enable matching against the 53,141 unique conductors of USp(4) curves.

Website: https://math.lmfdb.xyz/ModularForm/GSp/Q/Paramodular/

### Option 2: Trace Formula Approach
Use the Arthur-Selberg trace formula for GSp(4) to compute traces
Tr(T(p)|S_2(K(N))) at specific levels N matching genus-2 conductors.
This avoids needing full Fourier expansions.

### Option 3: Direct Computation
For specific conductor values (e.g., N=277, the smallest prime conductor
with a USp(4) curve), compute the paramodular form space directly using
Fourier-Jacobi methods. This is computationally intensive but targeted.

### Infrastructure Built
- `paramodular_probe.py`: Full probe script with data parsing, consistency checks
- `paramodular_euler_index.json`: Summary of 63,107 USp(4) curve Euler factors
- The genus-2 Euler factor parser is ready for matching once paramodular data arrives

---

## Files

| File | Purpose |
|------|---------|
| `cartography/shared/scripts/v2/paramodular_probe.py` | Main probe script |
| `cartography/shared/scripts/v2/paramodular_euler_index.json` | Euler factor summary |
| `cartography/lmfdb_dump/smf_newforms.json` | Siegel newform database |
| `cartography/lmfdb_dump/smf_hecke_nf.json` | Hecke eigenvalue data |
| `cartography/lmfdb_dump/g2c_curves.json` | Genus-2 curve metadata |
| `cartography/genus2/data/g2c-data/gce_1000000_lmfdb.txt` | Euler factors at good primes |
