# Out-of-sample test of the repaired map predictor (P_run500_causal) on X-DD-ESTABLISH W1 D0 donors

Date: 2026-09-30. Static analysis (single-interaction VM calls only; no world runs, no evolution runs, no git writes).

## PRE-REGISTRATION (written verbatim before any computation)

**PRE-REGISTRATION (frozen here, before you compute anything).**
- **Predictor.** Exactly the P_run500_causal predictor as implemented in map_correlate.py / map_children.py. Read the code and reuse it unchanged. It is computed per donor under the register context matching the target experiment's world (see below). Do not tune anything. If the code has free choices, use the same values it used for panel A.
- **Out-of-sample panel.** The W1 first donors (D0) of X-DD-ESTABLISH:
  - F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/x_dd_establish/ (results/*.json; field lineage_births = causal births from the D0 lineage; outcome label ESTABLISHED/NO_COPY/...).
  - Get the D0 genome hex from those results, or from x_dd_selfstate/results or x_dd_nocopy_context/results, matching on (cell, seed). If a D0 has several genomes, use the first listed, and say so.
- **World of that experiment.** Dense VM, cells 7ae3 and ffa6 (run_dd.CELLS), ATOMIC runner (run_ds.runner_cls), CARRIED registers, random background population. Use the CARRY context of the existing harness. Check how the harness builds the runner for a given cell, and build it the way X-DD-ESTABLISH does (read its run_*.py).
- **Outcomes, both pre-declared:**
  - O1 = D0 made ≥ 1 causal birth (lineage_births ≥ 1);
  - O2 = D0 made ≥ 29 causal births (the "real establishment" split seen in dossier D U3).
- **Pass criterion (frozen).** For O1: ROC AUC ≥ 0.75 with a one-sided permutation p < 0.01. For O2: Spearman(predictor, lineage_births) ≥ 0.4 with permutation p < 0.01.
  - Both met: PASS.
  - One met: PARTIAL.
  - Neither met: FAIL.
  - Report also the specified (non-repaired) P_est as a comparator. It is not decisive.
- **Exclusions.** Exclude runs with no identifiable D0 genome (NO_D0) and report the count. Include no other exclusions.

---
