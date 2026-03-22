# Ignis — Log Diagnostics Guide

## 1. Log Architecture

All logs flow through the `seti_logger.py` structured logger. Two outputs:

| Output | Level | Location |
|--------|-------|----------|
| **Console** | `INFO` and above | stdout |
| **File** | `TRACE` (all) | `results/logs/ignis.log` |

Every log line is prefixed with **context markers** that identify *where* in the search the event occurred:

```
2026-03-17 14:32:05  INFO [CYCLE:001] [MODEL:qwen2.5-0.5b] [GEN:042] [GENOME:007/020] [TRAP:Decimal Magnitude] [STEP:score] target marker 'False': HIT
```

### Context Marker Hierarchy

| Marker | Set By | Meaning |
|--------|--------|---------|
| `CYCLE` | `run()` | Which model-rotation cycle (1, 2, 3…) |
| `MODEL` | `run_evolution()` | Which model is active |
| `GEN` | `run_evolution()` | Generation number (zero-padded: 001, 042) |
| `GENOME` | `run_evolution()` | Genome index / total (007/020) |
| `TRAP` | `fitness.py` | Which trap is being evaluated |
| `STEP` | Various | Phase: `inference`, `score`, `crucible`, `falsification`, `probe_*`, `inception`, `inception_pca` |

## 2. Key Signals and How to Interpret Them

### 2.1 Fitness Scoring (fitness.py)

```
TRACE [TRAP:Decimal Magnitude] [STEP:score] target marker 'False': HIT
TRACE [TRAP:Decimal Magnitude] [STEP:score] failure marker '9.11 is larger than 9.9 is correct': miss
TRACE Trap 'Decimal Magnitude': target_hits=2, failure_hits=0, score=2.00, tier=CREDIT
DEBUG Crucible result: fitness=1.2600 | Decimal Magnitude=2.00[CREDIT] | Density Illusion=0.30[BASELINE] | Spatial Inversion=1.00[CREDIT]
```

**What to look for:**
- `tier=FLOOR` (0.1): Model is actively wrong — failure markers present
- `tier=BASELINE` (0.3): Model avoided failure but didn't produce target markers
- `tier=CREDIT` (1.0+): Model hit target markers — active self-correction
- The `Crucible result` summary shows per-trap breakdown

**Known calibration artifact — Decimal Magnitude on small models:**
On 0.5B models, `[HEALTH]` consistently shows `FLOOR+Strong` for Decimal Magnitude.
This is NOT a marker gap. The logit trap (forced-choice: "Is this True or False?")
is an easier task than the free-form reasoning prompt, so the logit scores Strong
even when the full generation gives a wrong answer. Confirmed by trace log output:
the 0.5B model unsteered says "9.11 is larger than 9.9 because..." — genuine
failure on free-form, but still answers the forced-choice correctly.

`FLOOR+Strong` for **Anti-Sycophancy** is a true marker gap — the model correctly
pushes back against the professor framing but uses phrasing not in the marker list.
Use the `[HEALTH]` signal to distinguish: if adding markers resolves it, it was a
gap; if FLOOR+Strong persists across all marker additions, it's a logit/generation
discrepancy.

### 2.2 TII Engine (tii_engine.py)

```
TRACE TII generate: layer=18, vec_norm=5.0234, max_tokens=128, prompt_len=95
TRACE TII output (342 chars): Is the following statement true or false...
WARNING CUDA OOM during TII generation (retry=0/1)
INFO Retrying TII generation with max_new_tokens=64
```

**What to look for:**
- `vec_norm` — if this grows unboundedly, CMA-ES sigma may be too large
- `CUDA OOM` + retry — normal if occasional; problematic if every generation
- `TII_GENERATION_FAILED` sentinel — downstream callers will score this as floor (0.1)

### 2.3 Falsification Battery (probe_runner.py)

```
TRACE Running primary injection (+v)
TRACE Constructing noise vector (same norm, random direction)
TRACE Noise genome: norm=5.0234, cosine_with_original=0.0312
TRACE Constructing orthogonal vector via Gram-Schmidt
TRACE Ortho genome: norm=5.0234, cosine_with_original=0.000002 (should be ~0)
TRACE Constructing sign-flipped vector (-v)
DEBUG Falsification battery completed — all 4 tests produced output
```

**What to look for:**
- `cosine_with_original` for noise should be near 0 (random direction)
- `cosine_with_original` for ortho should be ≈0 (orthogonal by construction)
- Any `FAILED` tests — check if it's OOM or a code bug

### 2.4 CMA-ES Distribution (seti_orchestrator.py)

```
TRACE Distribution updated: sigma=0.42310, mean_norm=4.8821, C_range=[1.00e-08, 3.21e+00], ps_norm=0.4210, hsig=1
INFO Geometry: manifold_dim=2.31, elite_cos=0.412, cov_ratio=321.2, cov_top5=[3.2100, 1.8400, 0.9200, 0.4100, 0.2300]
INFO Plateau decay: sigma 0.42310 → 0.35964
```

**What to look for:**
- `manifold_dim` — effective dimensionality of elite vectors. 1.0 = all elites point the same way. Higher = exploring a subspace.
- `elite_cos` — mean pairwise cosine of elites. >0.8 = converging. <0.1 = random exploration.
- `cov_ratio` — max/min of diagonal covariance. >10000 = CMA-ES is "tunneling" along a few dimensions.
- `sigma` — if it decays to 1e-5 (floor), search has stalled.
- `NaN/Inf detected in CMA-ES update` — critical error, evolution paths reset automatically.

### 2.5 Inception Protocol (inception_protocol.py)

```
INFO Inception Protocol START: layer=18, n_traps=3
TRACE Extracting contrastive delta for 'Decimal Magnitude'
TRACE Activation norms — naive: 12.4321, meta: 13.1045
DEBUG Delta captured for 'Decimal Magnitude' (norm=1.0000)
INFO PCA complete: PC1 variance explained = 72.3%, singular values = ['1.2340', '0.8120', '0.3210']
WARNING PC1 < 50% — traps may probe distinct mechanisms (still using PC1)
INFO Inception seed saved → results/qwen2-5-0-5b/gen_inception_seed.pt (blended 3/3 trap deltas)
```

**What to look for:**
- `PC1 variance explained` — >60% is good (traps share a mechanism). <40% means traps probe different circuits.
- `Delta extraction FAILED` — that trap's contrastive pair didn't produce distinguishable activations.
- `falling back to random init` — fewer than 2 deltas survived; CMA-ES starts from zero.

## 3. Error Recovery Reference

| Error | Where | Recovery | Log Signature |
|-------|-------|----------|---------------|
| CUDA OOM (generation) | `tii_engine.py` | Clear cache, retry with halved `max_new_tokens` | `WARNING CUDA OOM during TII generation (retry=…)` |
| CUDA OOM (model load) | `tii_engine.py` | Clear cache, retry once | `WARNING CUDA OOM loading …` |
| CUDA OOM (generation-level) | `seti_orchestrator.py` | Save state, skip generation, increment failure counter | `ERROR CUDA OOM at generation level` |
| TII generation failure | `tii_engine.py` | Return `TII_GENERATION_FAILED` sentinel | `ERROR TII generation FAILED (unexpected)` |
| Trap evaluation crash | `fitness.py` | Score floor (0.1), continue to next trap | `ERROR Unexpected error evaluating trap` |
| Genome evaluation crash | `seti_orchestrator.py` | Assign fitness=-1.0, continue to next genome | `ERROR Genome … evaluation FAILED` |
| Falsification test crash | `probe_runner.py` | Set test output to `TII_GENERATION_FAILED`, run remaining tests | `ERROR Null-A (noise) test failed` |
| PCA/SVD failure | `inception_protocol.py` | Return None → CMA-ES starts from zero vector | `ERROR Inception PCA/save FAILED` |
| NaN/Inf in CMA-ES | `seti_orchestrator.py` | Reset evolution paths, clamp sigma | `ERROR NaN/Inf detected in CMA-ES update` |
| State file corrupt | `seti_orchestrator.py` | Start fresh (gen 0) | `ERROR State load FAILED` |
| Drive sync failure | `seti_orchestrator.py` | Log warning, continue | `WARNING Drive sync failed (non-fatal)` |
| Consecutive failures (≥5) | `seti_orchestrator.py` | Abort current model, move to next | `CRITICAL Aborting model …` |

## 4. Common Search Techniques

### Find all events for a specific generation
```bash
grep "\[GEN:042\]" ignis.log
```

### Find all scoring decisions
```bash
grep "Crucible result" ignis.log
```

### Find all errors and warnings
```bash
grep -E "ERROR|WARNING|CRITICAL" ignis.log
```

### Find OOM events
```bash
grep "OOM" ignis.log
```

### Track sigma evolution (search step-size)
```bash
grep "Distribution updated" ignis.log | grep -oP "sigma=[0-9.]+"
```

### Find potential discoveries
```bash
grep "POTENTIAL DISCOVERY" ignis.log
```

### Find falsification results
```bash
grep -E "FALSIFIED|PASSED" ignis.log
```

### Track a specific genome through its lifecycle
```bash
grep "\[GENOME:007/" ignis.log
```

### View geometry trends across generations
```bash
grep "Geometry:" ignis.log
```

### Find inception protocol results
```bash
grep -E "Inception|PCA complete|variance explained" ignis.log
```

### PowerShell equivalents
```powershell
Select-String "GEN:042" ignis.log
Select-String "ERROR|WARNING|CRITICAL" ignis.log
Select-String "Crucible result" ignis.log
Select-String "POTENTIAL DISCOVERY" ignis.log
```

## 5. Night Watchman Digest Fields

Run `python night_watchman.py --results-dir results/ignis --once` for a
one-shot digest. For continuous monitoring run without `--once`.

### digest_latest.md sections

| Section | What it tells you |
|---|---|
| **Alerts** | Actionable problems: trap specialization, expression failures, bypass dominance, fitness decline |
| **Positive Signals** | Good news: fitness climb, shared mechanism candidates, logit selectivity, `*** FIRST NATIVE CIRCUIT CANDIDATE ***` banner |
| **Fitness Trajectory** | Gen-by-gen best fitness. Decline alert fires when latest gen best < earliest by 0.05+ after 5+ gens |
| **Trap Correlation Matrix** | Pearson r between trap score vectors. `r > 0.5` = traps co-activate (shared circuit candidate). `r < -0.3` = competing heuristics. |
| **Trap Coupling Trajectory** | `mean \|r\|` across all trap pairs this cycle. Rising trend across cycles = convergence toward shared circuit. |
| **Ghost Trap** | Four-quadrant count: native circuit candidates (high fit + cos > 0.3) vs artificial bypass (high fit + low cos). Also `cosine_fitness_corr`. |
| **Layer-wise Native Density** | Per-layer: native candidates / total genomes evaluated at that layer. Identifies which depth first shows residual-aligned behavior. Only shown when at least one native candidate exists. |
| **Logit Selectivity** | Mean `max(delta_correct) - max(delta_wrong)` from `logit_shift_signature`. Positive = vectors pushing correct-answer tokens up. |
| **Vector Drift** | Cosine between inception seed and gen_N-1_best.pt. Near 1.0 = refining. Near 0 = CMA-ES drifted far. |
| **CMA-ES State** | sigma, mean_norm, plateau_count, gen_count — parsed from the PyTorch binary state.json via `torch.load` |

### alerts.log interpretation

```
[timestamp] TRAP SPECIALIZATION: Anti-Sycophancy dominates (45% CREDIT), others at 0%
```
→ Run `[HEALTH]` grep on other traps: are they FLOOR+Strong (marker gap) or FLOOR+Weak (genuine)?

```
[timestamp] High expression failure rate (28/40) — model knows answers but markers miss them.
```
→ Check `logit_by_trap` in JSONL for which traps have high logit but low marker score. Add variants.

```
[timestamp] Bypass dominance: 12 high-fitness genomes orthogonal to native computation
```
→ High/Low quadrant dominance. Not circuit evidence. This is the expected 0.5B result —
watch `cosine_fitness_corr` and `mean_abs_r` (trap coupling) for sign of phase transition
at higher scales.

### Watchman quiesce (stop_ignis.py integration)

`stop_ignis.py` now writes a `WATCHMAN_STOP` semaphore file to `results/ignis/` after
the pipeline exits. The Watchman detects this at the next interval boundary, runs one
final wake cycle to capture terminal state, then exits cleanly. No manual Ctrl+C needed.

### New JSONL fields (added for 3.0B run)

| Field | Location | What it measures |
|-------|----------|-----------------|
| `min_trap_score` | root | Minimum score across all traps — passive indicator of trap balance; watch this rise if a shared circuit emerges |
| `norm_ratio` | `injection_snapshot` | `post_norm / pre_norm` — ratio near 1.0 = gentle steering; >> 1.0 = brute force injection |

## 6. Config Loading — Important

The pipeline loads hardcoded defaults if `--config` is not passed or the path doesn't
resolve. The configs directory is **one level above `src/`**, so the correct invocation
from `src/` is:

```powershell
python main.py --config ../configs/marathon.yaml
```

Using `configs/marathon.yaml` (without `../`) silently fails — the file doesn't exist
at `src/configs/marathon.yaml`, so `IgnisConfig.load()` returns defaults: 0.5B model,
sigma=0.1, population=20. The pre-flight will confirm which config loaded:
- `mutation_rate=0.03, population=40` → marathon.yaml loaded correctly
- `mutation_rate=0.1, population=20` → fell back to defaults, fix the path

## 7. Hard Reset / Clean Start Procedure

**Preferred method:** Use `archive_run.py` (in `src/`). It archives all run
artifacts, deletes `state.json`, and cleans up semaphores in one step:

```powershell
python archive_run.py restart "reason for restart"
```

**Manual method** (only needed if `archive_run.py` itself fails):

When you need a completely fresh run (e.g., after changing `seed_norm`, fixing a bug,
or when stale CMA-ES state is restoring incorrect parameters), follow this procedure.

### Why a hard reset is needed

The orchestrator restores CMA-ES state from `state.json` on startup. If the saved state
contains a `mean_vector` at norm 5.0 but your config says `seed_norm: 3.0`, the restored
state *overrides* the config. The mismatch detection only catches inception seed files,
not the full CMA-ES state. A hard reset forces a truly fresh start.

### Files to delete

From the `ignis` directory, with the run stopped:

```powershell
# 1. Stop the running process (Ctrl+C in the terminal)

# 2. Delete CMA-ES state (per-model subfolder AND top-level)
Remove-Item "src\results\ignis\qwen_qwen2_5-0_5b-instruct\state.json" -ErrorAction SilentlyContinue
Remove-Item "src\results\ignis\state.json" -ErrorAction SilentlyContinue

# 3. Delete inception seed (forces regeneration at current seed_norm)
Remove-Item "src\results\ignis\gen_inception_seed.pt" -ErrorAction SilentlyContinue

# 4. Delete best genome checkpoints
Remove-Item "src\results\ignis\best_genome.pt" -ErrorAction SilentlyContinue
Remove-Item "src\results\ignis\gen_*_best.pt" -ErrorAction SilentlyContinue

# 5. (Optional) Archive old logs before starting fresh
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Move-Item "src\results\ignis\logs\ignis.log" "src\results\ignis\logs\ignis_$ts.log" -ErrorAction SilentlyContinue
```

### What NOT to delete

- `src\results\ignis\archives\` — historical data from previous experiments
- `src\results\ignis\logs\` — move/rename, don't delete (useful for analysis)

### Verification

After cleanup, verify no stale files remain:

```powershell
Get-ChildItem -Path "src\results\ignis" -File -Recurse -Exclude "*.log" |
    Where-Object { $_.FullName -notlike "*archives*" } |
    Select-Object FullName
```

This should return empty output. Then restart with `python .\main.py`.

### Post-start log checks

Confirm the fresh start in the log:

```powershell
Select-String -Path "src\results\ignis\logs\ignis.log" -Pattern "starting fresh|mean_norm|vec_norm" |
    Select-Object -First 5 Line
```

You should see:
- `"No state file...starting fresh"` (not `"State restored"`)
- `mean_norm=3.0000` (not 5.0)
- `vec_norm=3.0000` on the inception seed

