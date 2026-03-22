# Ignis / RPH Master Plan
*Date: 2026-03-21*
*Status: 1.5B run live (GEN:000 in progress)*

---

## The Science We're Building Toward

Five nested claims, each independently falsifiable. We build bottom-up:

| Layer | Claim | Status | Gate |
|---|---|---|---|
| 1 | Behavioral: steering vectors improve reasoning on traps | ✅ Running | fitness > 0.7 survivors |
| 2 | Geometric: vectors align with endogenous reasoning states (Δ_proj > 0) | 🔨 Phase 1 | rph_metrics.py built |
| 3 | Mechanistic: effect routed through native features (SAE mediation ≥ 30%) | ❌ Phase 2 | SAE available for target model |
| 4 | Structural: reasoning vectors form a sparse structured manifold (~8%) | ❌ Phase 3 | MAP-Elites extension |
| 5 | Scale: cosine-fitness zero-crossing 0.5B→3B marks circuit threshold | 🔨 1.5B run | Scale gradient complete |

The current run answers Layer 5 (H3). The work below answers Layer 2.

---

## Current Run Status

- **Model:** Qwen/Qwen2.5-1.5B-Instruct, Layer 21, pop=40, 30 gens/cycle
- **Purpose:** H3 bridge — does cosine-fitness zero-crossing happen 0.5B→1.5B or 1.5B→3B?
- **Prior data:** 0.5B (r=−0.032, bypass-dominated), 3B (r=+0.037, sign change)
- **Do not:** restart, modify configs, or move files while this run is live

---

## VRAM / Parallel Runs

**Can we run two instances simultaneously?**

No — not the same config. Two instances of 1.5B on one GPU would:
- Each need ~3GB model weights in VRAM = 6GB just for models
- Each need ~4-8GB runtime (pop=40 eval, residual capture) = likely OOM on 16GB
- Serialize anyway: one GPU runs one kernel at a time, so no speed gain

**What DOES work in parallel:**

`eval_rph_survivors.py` — a background CPU-only worker that:
- Loads existing 0.5B and 3B best genome .pt files
- Runs inference on CPU (slow but non-blocking for GPU)
- Computes Δ_cf and MI_step via SBERT + PCA stats
- Produces RPH classification for already-completed survivors
- **Gives early Layer 2 signal without waiting for the current run**

**After 1.5B completes:** Start 7B run (marathon.yaml already has it configured,
flagged as "tight VRAM on 16GB" — test with one genome first).

---

## Phase 1: Build Now (Safe While Run Is Live)

All of these are additive-only, touch no running code paths, and are gated by
`rph_proxies.enabled: false` until explicitly enabled.

### Step 1 — `data/rph_counterfactual_pairs.json` ✅ DONE
Merged 9 prompt pairs from reasoning-precipitation:
- 3 arithmetic (including the Decimal Magnitude ECR test)
- 3 logic (including the div-by-4 logical trap)
- 3 counterfactual

### Step 2 — `src/genome.py` ✅ DONE
Added 5 RPH fields with defaults. Backward compatible: old .pt files load with
`.get()` defaults, all existing saves unaffected.

### Step 3 — `src/rph_metrics.py` ✅ DONE
New module consolidating:
- `compute_delta_cf()` — SBERT semantic distance on paired outputs
- `compute_mi_step()` — PCA + shuffled baseline on stacked resid_post
- `compute_delta_proj()` — projection differential (SC vs HB states)
- `compute_rph_proxies()` — orchestration: run model → collect residuals → all metrics
- `classify_vector()` — PRECIPITATION_CANDIDATE / WEAK_SIGNAL / NULL

### Step 4 — `src/fitness.py` ✅ DONE
Added `score_rph_proxies()` to `MultiTaskCrucible`.
Called only when `rph_proxies.enabled: true`. Does nothing until then.

### Step 5 — `configs/marathon.yaml` ✅ DONE
Added `rph_proxies` config block with `enabled: false`.

### Step 6 — `eval_rph_survivors.py` ✅ DONE
Background evaluation script for existing survivor .pt files.
Run independently, uses CPU for inference, no GPU competition.

---

## Phase 1b: Analyzer Upgrades (After Phase 1 Code Verified)

These surface RPH signals in the existing monitoring tools.
Safe to do while run is live — they only read log files, never write to pipeline.

- [ ] `seti_log_analyzer.py` — add RPH proxy scores section, precipitation candidate count
- [ ] `night_watchman.py` — add precipitation candidate alert threshold
- [ ] `review_watchman.py` — surface RPH classification in digest

---

## Phase 2: After 1.5B Run Completes

1. **Enable RPH scoring** on next cycle: `rph_proxies.enabled: true` in marathon.yaml
2. **Run eval_rph_survivors.py** on 0.5B + 1.5B + 3B best genomes
3. **Analyze H3**: plot cosine-fitness correlation across scale gradient
4. **Analyze H4**: compare trap dominance (Density Illusion vs Anti-Sycophancy) across scales
5. **Structural move**: already completed — `ignis/` is now at project root
   (See `docs/REPO_STRUCTURE_PROPOSAL.md` for the original plan)

---

## Phase 3: Layer 3 — SAE Mediation

Requires:
1. Pretrained SAE for Qwen 2.5 target layers (check EleutherAI/SAEBench, TransformerLens releases)
2. `mech/src/sae_mediation.py` — ablate_features, mediation_drop metric
3. Apply to PRECIPITATION_CANDIDATE genomes from Phase 2
4. Gate: ≥ 30% drop → mechanistic claim confirmed

---

## Phase 4: Layer 4 — MAP-Elites Extension

Requires:
1. Extend seti_orchestrator to optionally run MAP-Elites in place of CMA-ES
2. Behavior space: Δ_cf × MI_step × Δ_proj (10×10×10 archive)
3. Run on survivors from Phase 2/3 as parent population
4. Target: map the manifold of precipitation vectors across scales

---

## The Key Scientific Connection (Don't Lose This)

The arithmetic.json prompt — *"Assume temporarily that 9.11 > 9.9..."* — is not
just an ECR test. It **is** the Decimal Magnitude trap reframed with an escape route.

A genome that:
- Passes the crucible Decimal Magnitude trap (Layer 1)
- Shows Δ_proj > 0 on the ECR prompt (Layer 2)
- Shows ECR > 0 (self-corrects the false premise) (Layer 2/3 boundary)

...would be the first direct evidence of precipitation: not just pushing the right
output token, but engaging the verification circuit that *knows* the premise was false.

That's the result worth watching for.

---

## Open Questions

| Question | Hypothesis | Test |
|---|---|---|
| H3 | Zero-crossing occurs 0.5B→1.5B | Compare cosine-fitness r at 1.5B |
| H4 | Trap dominance is non-monotonic | Compare trap breakdown 0.5B/1.5B/3B |
| H5 | RPH classification improves with scale | Compare PRECIPITATION_CANDIDATE rate across sizes |
| H6 | ECR > 0 requires Layer 1 gate first | Correlate crucible fitness with ECR score |
