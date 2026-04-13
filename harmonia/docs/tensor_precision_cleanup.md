# Tensor Precision Cleanup — What Changed and Why
## For M1 synchronization
## 2026-04-13

---

## What Happened

The adversarial session (your `kill_harmonia_claims.py` and `test_new_bridges.py`) killed 11/13 cross-domain claims. This triggered a precision cleanup of the entire Harmonia measurement system. Here's exactly what survived, what died, and what was fixed.

---

## The Three Metrics (only one survives)

### 1. Phoneme NN Transfer — DEAD

**What it was:** Match objects across domains by nearest neighbor in 5D phoneme space, predict arithmetic invariants.

**Reported numbers:** EC→NF rho=0.76, OOD retention 203%, Z2 alone rho=0.61.

**How it died:** Within-bin random matching (control for Megethos) gives rho=0.033 vs null=0.002. ALL the transfer signal was Megethos leakage. When you properly control for magnitude, no residual structure remains in NN matching.

**Kill tests that exposed it:** F33 (rank-sort null), F34 (trivial 1D baseline beats phonemes at rho=0.95).

**Status:** Do not use phoneme NN transfer rho as evidence of anything. It measures Megethos leakage dressed up as Arithmos signal.

### 2. Phoneme NN Distributional Coupling — DEGENERATE

**What it was:** Match RMT to MF in phoneme space, compare GUE statistics of matched vs random RMT objects.

**Reported numbers:** KS=0.997, all 14 features significant at p=0.00.

**How it broke:** ALL MF objects match to the SAME single RMT object. unique=1 in every Megethos bin. The distributional difference is real but trivial — it's just "the one nearest point has different stats than the average."

**Attempted fix:** Added Megethos (log conductor) to RMT domain. Still degenerates — unique=1.

**Root cause:** Z-score normalization makes all domain distributions identical (mean=0, std=1). NN in this normalized space collapses to a single point regardless of the features.

**Status:** Cannot use phoneme NN for distributional claims. The Montgomery-Odlyzko connection is mathematically established but our MEASUREMENT of it via phoneme NN is broken.

### 3. TT-Cross Bond Dimensions — SURVIVES ✓

**What it is:** Tensor train decomposition via TT-Cross. Bond dimension between adjacent domains measures coupling strength. Uses a coupling FUNCTION (cosine similarity in projected space), not nearest-neighbor matching.

**Precision test:** 
```
EC <-> NF TT-Cross Bond Dimensions
  Normal (baseline):         rank = 4
  Megethos zeroed out:       rank = 4  (UNCHANGED)
  Megethos shuffled:         rank = 4  (UNCHANGED)
  Validated without Megethos: rank = 2
```

**Why it survives:** TT-Cross uses a coupling function that measures distributional overlap, not point-to-point matching. It captures structure that NN collapses. Zeroing out Megethos (setting feature 0 to 0 in both domains) does NOT change the bond dimension. The rank=4 structure is in the non-Megethos features.

**Status:** Use TT-Cross bond dimensions (with Megethos-zeroed features) as the primary structural metric. Validated rank 2 is the honest signal.

---

## The Kill Tests (F33-F37)

Added by the adversarial session (`test_new_bridges.py`). These must be run on ALL future claims.

| Test | What it catches | How to run |
|------|----------------|-----------|
| **F33** | Rank-sort null: sorted small integers correlate by construction | Sort both feature vectors, compute rho. If sorted rho ≈ real rho, it's ordinal artifact. |
| **F34** | Trivial 1D baseline: nearest-value matching on target variable | For each target object, find source with closest value of the PREDICTED variable. If trivial rho > method rho, method adds no value. |
| **F35** | Megethos false positive: magnitude matching couples everything | Match by Megethos only. If Megethos-only rho ≈ full rho, coupling is in magnitude not structure. |
| **F36** | Partial correlation null: wrong null for log-partial procedure | Use permutation null on the RESIDUALIZED values, not on the raw values. |
| **F37** | Engineered universality: is universality in the code or the data? | Swap phoneme mappings between unrelated domains. If structure persists, it's in the encoding. |

---

## Mass Calibration Results

From live LMFDB Postgres (devmirror.lmfdb.xyz:5432):

| Theorem | Objects | Match Rate |
|---------|---------|-----------|
| Modularity (a_p coefficients) | 971 pairs, 450 coefficients | 100.000% |
| Parity conjecture | 20,000 | 100.0% |
| Mazur torsion | 3,824,372 | 100.000% |
| Hasse bound | 150,000 coefficients | 100.000% |
| Conductor positivity | 3,824,372 | 100.000% |
| rank = analytic_rank | 3,824,372 | 100.000% |

These are the calibration anchors. Any claim must achieve comparable precision at comparable scale.

---

## What M1 Should Do

### 1. Pull latest and verify the TT-Cross precision test
```python
cd D:\Prometheus
git pull origin main

# Reproduce the Megethos-zeroed TT-Cross test
from harmonia.src.domain_index import DOMAIN_LOADERS, DomainIndex
from harmonia.src.coupling import CouplingScorer
import tntorch as tn, torch

ec = DOMAIN_LOADERS['elliptic_curves']()
nf = DOMAIN_LOADERS['number_fields']()

# Zero out Megethos
ec_resid = ec.features[:2000].clone()
nf_resid = nf.features[:2000].clone()
ec_resid[:, 0] = 0.0
nf_resid[:, 0] = 0.0

scorer = CouplingScorer([
    DomainIndex('ec', ec.labels[:2000], ec_resid),
    DomainIndex('nf', nf.labels[:2000], nf_resid),
])
grids = [torch.arange(2000, dtype=torch.float32), torch.arange(2000, dtype=torch.float32)]
def vf(*indices):
    return scorer(*[idx.long() for idx in indices])

tt = tn.cross(function=vf, domain=grids, eps=1e-3, rmax=15, max_iter=50)
print('Megethos-zeroed rank:', tt.ranks_tt[1].item())
# Should be 4 (same as with Megethos)
```

### 2. Run F33-F37 on your 41D tensor
Your dissection tensor is an independent representation. Apply the kill tests there:
- F33: sort the EC and NF features, compute correlation of sorted vectors
- F34: for each NF object, find the EC whose feature 0 is closest. Is that better than your full 41D matching?
- F35: match EC to NF by feature 0 (magnitude) only. How much of the rho=0.95 is Megethos?

### 3. Reproduce the mass calibration on your local Postgres
Once your clone is done:
```python
import psycopg2
conn = psycopg2.connect(host='localhost', dbname='lmfdb_local', user='lmfdb')
cur = conn.cursor()
cur.execute('SELECT torsion, COUNT(*) FROM ec_curvedata GROUP BY torsion ORDER BY torsion')
# Should match our results exactly
```

### 4. Build Megethos-zeroed sweeps
The only valid structural metric is TT-Cross with Megethos zeroed. Run a pairwise sweep across your top domains using this:
```python
# For each domain pair, zero out feature 0, run TT-Cross
# Report: which bonds survive Megethos removal?
# Only surviving bonds are real structure
```

---

## File Locations

| File | What it contains |
|------|-----------------|
| `harmonia/results/precision_fix_results.json` | Within-bin NN test (rho=0.033) |
| `harmonia/results/ttcross_precision.json` | TT-Cross Megethos-zeroed test (rank 4→4) |
| `harmonia/results/kill_verification.json` | F33-F37 verification of adversarial kills |
| `harmonia/results/mass_calibration.json` | 3.8M curve calibration results |
| `harmonia/results/calibration_coefficient.json` | Modularity a_p verification |
| `harmonia/results/honest_assessment_final.json` | Kill tally and precision state |
| `harmonia/results/rmt_precision.json` | RMT degenerate matching diagnosis |
| `cartography/shared/scripts/test_new_bridges.py` | F33-F37 implementation |
| `cartography/shared/scripts/kill_harmonia_claims.py` | Full adversarial kill suite |

---

## The Honest State

**What's real:**
- TT-Cross bond dimensions survive Megethos removal (rank 4→4, validated 2)
- 6 known theorems verified at 100% across 3.8M objects
- The system correctly identifies which invariants are arithmetic-type vs analytic-type
- Cross-category TT-Cross bonds exist (chemistry↔EC, RMT↔MF) — need Megethos-zeroed retest

**What's dead:**
- All phoneme NN transfer rho numbers (Megethos leakage)
- All phoneme NN distributional coupling (degenerate matching)
- 11/13 cross-domain claims from the original session

**What needs retesting:**
- Every sweep, MAP-Elites, and transfer result using Megethos-zeroed TT-Cross
- Cross-category bonds (chemistry↔EC, RMT↔MF) with F33-F37
- Montgomery-Odlyzko with properly unfolded zeros
- Sato-Tate with larger primes from Postgres
