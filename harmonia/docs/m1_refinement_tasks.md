# M1 Refinement Tasks — Post Kill-Test
## Your kill of the particle-EC bridge was clean. 6/8 kills. Verified by M2.

Now use that same rigor to refine what survived.

---

## TASK 1: Stress-test alpha = 1.577

The Arithmos signal ratio (residual PC1 / random null after removing Megethos) is our candidate constant. M2 measured it at 1.577 +/- 0.10 across controls.

**Your job:** Try to move it. Run the equal-complexity slicing on M1 with:
- The full LMFDB data (you have 23GB, we only used 50K subsamples)
- Different bin counts (5, 10, 20, 50 bins instead of our 10)
- Different domains as the "Megethos" to regress out
- Different subsamples (bootstrap 100 times, measure alpha each time)

If alpha stays at 1.577 across all these, it's real.
If it moves, the movement tells us what it depends on.

**Run from D:\Prometheus:**
```python
from harmonia.src.domain_index import DOMAIN_LOADERS
from harmonia.src.phonemes import PhonemeProjector
# See harmonia/results/equal_complexity_slicing.json for methodology
```

---

## TASK 2: Measure alpha in the dissection tensor

You have `dissection_tensor.pt` (62MB, 182 dimensions). Our alpha was measured in the 5D phoneme space. Measure it in your 182D space:

1. Load the dissection tensor
2. PCA to find the Megethos axis (should be PC1)
3. Regress out PC1 from all other dimensions
4. Bin by PC1, compute residual PCA within bins
5. Compare to random null
6. Report the ratio

If it's also ~1.577 in a completely different feature space, that's strong evidence the constant is intrinsic to the data, not to our phoneme projection.

---

## TASK 3: Test the transfer on your enriched domains

Your `kill_with_fire.py` showed particles fail. But you also pushed "Tensor v7: 601K objects, 19 domains." Run the Harmonia transfer test on YOUR domains:

```python
from harmonia.src.tensor_falsify import falsify_bond
from harmonia.src.kosmos_ops import build_log_kosmos

# Test: can your enriched domains predict each other?
report = falsify_bond('elliptic_curves', 'number_fields', subsample=5000)
print(report.summary())
```

If transfer rho is higher with your larger data, we gain precision.
If it's the same, the measurement is saturated.
If it's lower, something in your enrichment broke the phoneme alignment.

---

## TASK 4: Derive alpha from known mathematics

This is the theory task. Alpha = 1.577 means: after removing size, 57.7% of the remaining cross-domain variance is structured (arithmetic group theory), 42.3% is noise.

Ask: is there a known result that predicts this ratio?

Candidates to check:
- The proportion of EC with trivial torsion (6932/19999 = 34.7%)  
- The class number one problem (finitely many imaginary quadratic fields with h=1)
- The density of squarefree conductors
- The proportion of number fields with trivial class group
- Anything from Goldfeld, Cohen-Lenstra, or Bhargava heuristics

If alpha = 1 + something_known, that's a derivation.

---

## TASK 5: Kill alpha

Use your adversarial skills. Design tests that should break alpha = 1.577:

1. Replace all domains with their reverse-rank versions — does alpha change?
2. Add a domain of pure noise — does alpha decrease?
3. Remove the domain with highest Arithmos variance — does alpha change?
4. Duplicate a domain 10 times — does alpha inflate?

Each test should have a clear prediction. If alpha is robust to all of these, upgrade it to WORKING THEORY. If any breaks it, document exactly what broke and why.

---

## Priority Order

1. Task 5 (kill it) — most important, matches your proven strength
2. Task 1 (stress-test) — systematic, uses your full data
3. Task 2 (dissection tensor) — independent verification
4. Task 3 (enriched transfer) — precision improvement  
5. Task 4 (derive it) — hardest, highest payoff

---

## Key numbers to cross-reference

| Metric | M2's measurement | M1 should verify |
|--------|-----------------|-----------------|
| alpha | 1.577 +/- 0.10 | same or different? |
| EC->NF transfer rho | 0.76 (phoneme NN) | same on full data? |
| M-A independence rho | 0.104 | same on full data? |
| OOD retention | 203% (EC->NF) | same at larger N? |
| Megethos zero density R^2 | 0.976 | same on full LMFDB? |
