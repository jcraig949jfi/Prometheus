# RPH → Ignis Integration Strategy
*Assembled from reasoning-precipitation repo + RPH v4 final + EXISTENCE_PROOF_SPEC*
*Date: 2026-03-21*

---

## Situation Summary

The `reasoning-precipitation` repo was built by Claude Code as a greenfield RPH
implementation before Ignis (then SETI v2) was discovered. Once Ignis was shown, the correct
call was made: don't rebuild, integrate. The `docs/integration.md` in that repo
already contains a complete component mapping. This document consolidates that
plan with what was actually built.

**The mechanistic gate has already been passed** (EXISTENCE_PROOF_SPEC.md):
- Genome "6,2" (qwen_seed3, fitness 0.877): path-patching recovery 30.0 at layer 27 — 7.8× enrichment
- Genome "4,3" (qwen_seed3, fitness 0.806): recovery 29.75 at layer 10
- Conclusion: behavioral divergence is tied to localized internal structure. Not bypass noise. Real.

The current 1.5B run is building the scale gradient that contextualizes everything.

---

## What to Port from reasoning-precipitation

### Keep as-is (working code, zero rework needed)

| File | What it does | Destination |
|---|---|---|
| `src/metrics/delta_cf.py` | Δ_cf via sentence-transformer semantic distance on paired outputs | `ignis/src/rph_metrics.py` |
| `src/metrics/mi_step.py` | MI_step via PCA + shuffled baseline on stacked residuals | `ignis/src/rph_metrics.py` |
| `src/metrics/delta_proj.py` | Δ_proj projection differential (self-correction vs heuristic-bypass) | `ignis/src/rph_metrics.py` |
| `src/evaluation/statistical_tests.py` | Paired t-test, bootstrap CI, permutation test, `classify_vector()` | `ignis/src/rph_metrics.py` |
| `data/prompts/*.json` | 9 prompt pairs across arithmetic / logic / counterfactual | `ignis/data/rph_counterfactual_pairs.json` |

### Discard (superseded by Ignis)

| File | Why |
|---|---|
| `src/search/vector_search.py` | Placeholder MAP-Elites — Ignis's CMA-ES is strictly better |
| `src/interventions/vector_injection.py` | Duplicate of `tii_engine.py` |
| `src/models/tl_loader.py` | Duplicate of `tii_engine.load_tii_model` |
| `scripts/run_experiment.py` | Metric calls are placeholder stubs (`fitness = np.random.random()`) |
| `scripts/run_alpha_sweep.py` | Metrics are fake (`0.2 + alpha * 0.05 + noise`) |

### Keep for reference (docs only)
- `docs/integration.md` — master component mapping, already complete
- `docs/phases.md` — phase plan with explicit go/no-go gates
- `docs/experimental_protocol.md` — if it contains more detail

---

## What Needs to Be Built in Ignis

### 1. `ignis/src/rph_metrics.py` (NEW FILE)
Consolidate the three metrics + statistical tests into one module:
```
compute_delta_cf(outputs, outputs_cf) → (mean, std)
compute_mi_step(cache) → float
compute_ecr(model, false_intermediate_prompts) → float    ← NOT YET IN REPO, needs building
classify_vector(delta_cf_result, mi_step_ci, delta_proj_result) → str
```
ECR is the one metric not yet implemented — requires generating with injected false
intermediates ("Assume temporarily 9.11 > 9.9...") and detecting self-correction via
token-level logit trajectory.

**Note:** The arithmetic.json prompt `"Assume temporarily that 9.11 > 9.9..."` directly
maps to the Decimal Magnitude trap. These aren't separate systems — the ECR test IS
a harder version of the same cognitive challenge the crucible already tests.

### 2. `genome.py` — Extend SteeringGenome (backward compatible)
Add RPH fields with defaults so old `.pt` files load cleanly:
```python
rph_delta_cf: float = 0.0
rph_mi_step: float = 0.0
rph_ecr: float = 0.0
rph_passes: int = 0          # 0–3
rph_precipitation_candidate: bool = False
```

### 3. `fitness.py` — Add `score_rph_proxies()` to MultiTaskCrucible
Optional post-scoring pass, called only when `rph_proxies.enabled: true`.
Runs on confirmed survivors (falsification-PASSED genomes), not every genome.
Outputs RPH fields in-place on the genome object and logs to `discovery_log.jsonl`.

### 4. `configs/marathon.yaml` — Add RPH config section
```yaml
rph_proxies:
  enabled: false        # flip to true after first survivors accumulate
  counterfactual_pairs_path: "data/rph_counterfactual_pairs.json"
  min_proxy_passes: 2   # threshold for precipitation_candidate = True
```

### 5. `data/rph_counterfactual_pairs.json` (NEW FILE)
Merge the 9 pairs from reasoning-precipitation + expand with trap-aligned pairs
(the "Assume temporarily 9.11 > 9.9" ECR prompt already exists in arithmetic.json).

### 6. Analyzer / Watchman Upgrades
Once RPH fields appear in `discovery_log.jsonl`:
- **seti_log_analyzer.py** — add RPH proxy scores section, precipitation candidate count
- **night_watchman.py** — add precipitation candidate alert threshold
- **review_watchman.py** — surface RPH classification in digest

---

## What Ignis Already Has That Maps to RPH

| RPH Requirement | Ignis Implementation | Status |
|---|---|---|
| Natural occurrence test (Δ_proj seed) | `inception_protocol.py` → contrastive delta + PCA → PC1 | ✅ Running |
| Real-time Δ_proj proxy | `cos_with_residual` in ghost trap | ✅ Running |
| Falsification battery | `probe_runner.py` → noise/ortho/flip/shuffle | ✅ Running |
| Norm sweep (α sweep) | `seti_orchestrator.run_norm_sweep()` | ✅ Running |
| Scale gradient (cross-model) | 0.5B done, 3B done, 1.5B running | ✅ In progress |
| Mechanistic gate (path patching) | `EXISTENCE_PROOF_SPEC.md` — PASSED | ✅ Done |
| Δ_cf (counterfactual sensitivity) | Not in Ignis | ❌ Needs porting |
| MI_step (stepwise MI) | Not in Ignis | ❌ Needs porting |
| ECR (error correction rate) | Not in Ignis | ❌ Needs building |
| SAE mediation | Not built anywhere | ❌ Phase 2 |
| MAP-Elites archive | Placeholder stub | ❌ Phase 3 |

---

## Sequencing

### Now (safe, non-disruptive to running experiment)
1. Port `delta_cf.py`, `mi_step.py`, `delta_proj.py`, `statistical_tests.py` → `rph_metrics.py`
2. Merge prompt bank → `data/rph_counterfactual_pairs.json`
3. Extend `SteeringGenome` with RPH fields (backward compatible, zero risk)
4. Add `rph_proxies` config block to marathon.yaml with `enabled: false`
5. Upgrade analyzers to surface RPH signals (even if all zeros until enabled)

### After GEN:000 first survivors accumulate (~today, ~11:00)
6. Add `score_rph_proxies()` to MultiTaskCrucible
7. Enable `rph_proxies.enabled: true` — survivors get RPH-scored on next cycle

### After run completes (scale gradient in hand)
8. Build ECR properly (false-intermediate injection)
9. Run `classify_vector()` on all accumulated survivors
10. Compare 0.5B / 1.5B / 3B RPH classification distributions → H3 test

### Phase 2 (separate effort)
11. SAE mediation on PRECIPITATION_CANDIDATEs
12. `mech/path_patching.py` + `csi_gate.py` (spec exists, code doesn't)

---

## The Key Scientific Connection

The arithmetic prompt bank has: *"Assume temporarily that 9.11 > 9.9. Using this
assumption, compute which is larger: 9.119 or 9.91. Then explain if the assumption
was valid and correct your reasoning."*

This is the Decimal Magnitude trap reframed as an ECR test. The model that gets
steered correctly by the crucible AND shows ECR > 0 on this prompt (escaping the
false premise and self-correcting) would be the first direct evidence of precipitation:
not just pushing the right output token, but engaging the verification circuit that
knows the premise was false.

That's the result worth watching for.

---

## Repo Status
- `reasoning-precipitation` — cloned to `f:/Prometheus/reasoning-precipitation/`
- Safe to leave as-is or delete after porting. Not part of the active experiment.
