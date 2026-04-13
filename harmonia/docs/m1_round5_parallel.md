# M1 Round 5 — 8 Cores, 8 Tasks
## M2 has 8 threads running. M1 has 8 cores idle. Use them all.

M2 is expanding domains (29→35+) and running sweeps. M1 should do what M2 CAN'T: work in the 41D dissection tensor space, run the adversarial machine on your data, and test things that need the full LMFDB dump (23GB) that M2 doesn't have.

---

## TASK 1: Adversarial overnight results analysis
The 5000-attack adversarial run should have finished. Pull from remote:
```
git pull origin main
```
Check `harmonia/results/adversarial_report.json`. Read the top 20 most damaging attacks. Run the top 5 in your 41D space — do they damage your representation too?

---

## TASK 2: Full Dirichlet zeros (184K)
M2 caps at 50K (now 100K). You have access to the full 184K. Load them ALL into your tensor and measure:
- Does alpha change with the full dataset?
- Does the Megethos-Arithmos decomposition hold at 184K?
- Any new structure visible only at full scale?

---

## TASK 3: Hilbert Modular Forms
You have `hmf_hecke_eigenvalues.jsonl` (74GB!) and `hmf_forms.json` / `hmf_fields.json`. These are automorphic forms over REAL quadratic fields — the complement to Bianchi (imaginary quadratic). Load them as a Harmonia domain. This would give us:
- Bianchi = imaginary quadratic (Iris)
- HMF = real quadratic (new island?)
Together they cover ALL quadratic extensions. If both couple to the same phonemes, quadratic field structure is universal.

---

## TASK 4: 41D transfer with new physics domains
M2 just loaded chemistry (50K QM9 molecules), CODATA (286 constants), PDG particles (226). If M1 can compute dissection signatures for these objects and add them to the 41D tensor, we get cross-validation: does chemistry couple to math in the 41D space the same way it does in 5D phoneme space?

---

## TASK 5: Transition function refinement
Your Round 3 found the linear map is 71.6% with 29% nonlinear. Try:
- Kernel PCA (RBF kernel) instead of linear PCA
- UMAP embedding of both 5D and 41D spaces
- Does the nonlinear correspondence improve beyond 78.7% (your quadratic)?

---

## TASK 6: Known truth expansion
M2's calibration uses only 5 truths + 3 falsehoods. You have `known_truth_battery.py` with 100 proven facts. Run the top 30 through Harmonia:
```python
from harmonia.src.tensor_falsify import falsify_bond
# For each known truth pair, run falsify_bond
```
More truths = better sensitivity/specificity measurement. Target: 30 truths, 10 falsehoods.

---

## TASK 7: Genus-2 full precision
M2 loads 66K genus-2 curves but only uses 7 features. The actual genus2_curves_full.json likely has more invariants (igusa invariants, endomorphism ring, etc.). Load ALL numerical features and see if the transfer to NF improves beyond rho=0.80.

---

## TASK 8: Bridge hunter cross-check
`cartography/convergence/data/bridge_hunter_results.jsonl` (135MB) contains previously discovered cross-domain bridges. Cross-check: do the bridges Harmonia finds (via tensor coupling) match the bridges the bridge hunter found (via different methods)? Agreement = mutual validation. Disagreement = one system found something the other missed.

---

## Priority
All 8 are independent — run them all. If you have to triage:
1. Task 3 (HMF) — biggest new data source
2. Task 6 (more known truths) — directly improves calibration
3. Task 2 (full Dirichlet) — precision at scale
4. Task 8 (bridge cross-check) — mutual validation
5-8: everything else

---

## Git discipline
Pull before starting. Commit after each task. Push frequently. M2 is also pushing — expect merge conflicts on domain_index.py and phonemes.py. Resolve by keeping both sets of changes.
