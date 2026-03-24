# Overnight Run Plan — March 24-25, 2026
## ~10 hours of GPU time, batched and unattended

### Priority Order (Rhea gets first 3 hours, Ignis gets the rest)

---

## RHEA BLOCK (hours 0-3, WSL)

### Job 1: Vocabulary test (20 min)
Fine-tune evolved 135M on 50 "Unknown" examples → re-run metacognition traps.
Tests whether the architecture-vocabulary gap is real.
PREDICTION: metacognition jumps to 50-70%.

### Job 2: Lean 4 install + proof corpus (40 min)
Install elan. Generate 500 simple proof attempts. Label verified/failed.
Fine-tune evolved 135M on results. Re-run full eval_v2.
PREDICTION: Tier B recovers partially, metacognition improves further.
THIS IS RHEA'S LOOP CLOSING FOR THE FIRST TIME.

### Job 3: 360M rank-8 eval_v2 (30 min)
Run the full v2 battery on the rank-8 360M genome.
Compare with 135M evolved and 1.5B baseline.
The middle data point on the scaling curve.

### Job 4: Targeted v_proj CMA-ES on 360M (2 hours)
```python
LORA_CONFIG_TARGETED = LoraConfig(
    r=8,
    target_modules=["v_proj"],  # v_proj only
    layers_to_transform=list(range(0, 10)),  # early layers only
)
```
Test whether concentrated early v_proj targeting produces faster convergence
than the current q_proj + v_proj + gate_proj configuration.
PREDICTION: faster phase transition, higher final fitness, less collateral damage.

---

## IGNIS BLOCK (hours 3-10, Windows)

### Job 5: Cross-architecture replication — Llama-3.2-1B (3 hours)
The universality test. TransformerLens supports Llama-3.2-1B-Instruct.
Run the full Ignis diagnostic suite:
```
python src/logit_lens_backward.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/llama_1b
python src/ejection_decompose.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/ejection_llama_1b
python src/vproj_diagnostic.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/vproj_llama_1b
python src/base_vs_instruct.py --base-model meta-llama/Llama-3.2-1B --instruct-model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/base_vs_instruct_llama_1b
python src/eval_v2.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/eval_v2_llama_1b
```
If the spike-and-collapse appears in Llama at analogous depth with analogous
component specialization, the universality claim is proven across model families.

### Job 6: Cross-architecture replication — Gemma-3-1B (2 hours)
Same suite on Gemma. Third model family.
```
python src/logit_lens_backward.py --model google/gemma-3-1b-it --device cuda --output-dir src/results/ignis/gemma_1b
python src/ejection_decompose.py --model google/gemma-3-1b-it --device cuda --output-dir src/results/ignis/ejection_gemma_1b
python src/vproj_diagnostic.py --model google/gemma-3-1b-it --device cuda --output-dir src/results/ignis/vproj_gemma_1b
python src/eval_v2.py --model google/gemma-3-1b-it --device cuda --output-dir src/results/ignis/eval_v2_gemma_1b
```

### Job 7: Basin escape histogram on Llama-3.2-1B (1 hour)
If the ejection exists in Llama, can CMA-ES find channels there too?
```
python src/basin_escape_histogram.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir src/results/ignis/basin_llama_1b --layer 12 --trap "Overtake" --n-directions 50
```

### Job 8: Evolve on Llama-3.2-1B (remaining time, ~2-4 hours)
If basins are ridged on Llama, start CMA-ES evolution.
This tests whether the ejection can be suppressed across model families, not just Qwen/SmolLM2.

---

## BATCH SCRIPTS

### For Rhea (WSL):
```bash
#!/bin/bash
# rhea_overnight.sh — run in WSL
set -e

echo "=== Job 1: Vocabulary test ==="
# (Rhea writes this part)

echo "=== Job 2: Lean 4 + proof corpus ==="
# Install elan if not present
which lean || (curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh)
# (Rhea writes the proof corpus generation + fine-tune)

echo "=== Job 3: 360M eval_v2 ==="
# (Rhea writes this)

echo "=== Job 4: Targeted v_proj CMA-ES ==="
# (Rhea writes the targeted evolution)

echo "=== All Rhea jobs complete. GPU free for Ignis. ==="
```

### For Ignis (Windows):
```batch
@echo off
REM ignis_overnight.bat — run after Rhea finishes

echo === Job 5: Llama-3.2-1B diagnostic suite ===
python ignis\src\logit_lens_backward.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir ignis\src\results\ignis\llama_1b --skip-preflight
python ignis\src\ejection_decompose.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir ignis\src\results\ignis\ejection_llama_1b --skip-preflight
python ignis\src\vproj_diagnostic.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir ignis\src\results\ignis\vproj_llama_1b
python ignis\src\eval_v2.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir ignis\src\results\ignis\eval_v2_llama_1b --skip-logit-lens

echo === Job 6: Gemma-3-1B diagnostic suite ===
python ignis\src\logit_lens_backward.py --model google/gemma-3-1b-it --device cuda --output-dir ignis\src\results\ignis\gemma_1b --skip-preflight
python ignis\src\ejection_decompose.py --model google/gemma-3-1b-it --device cuda --output-dir ignis\src\results\ignis\ejection_gemma_1b --skip-preflight
python ignis\src\vproj_diagnostic.py --model google/gemma-3-1b-it --device cuda --output-dir ignis\src\results\ignis\vproj_gemma_1b
python ignis\src\eval_v2.py --model google/gemma-3-1b-it --device cuda --output-dir ignis\src\results\ignis\eval_v2_gemma_1b --skip-logit-lens

echo === Job 7: Llama basin escape ===
python ignis\src\basin_escape_histogram.py --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir ignis\src\results\ignis\basin_llama_1b --layer 12 --trap "Overtake" --n-directions 50

echo === All Ignis jobs complete ===
```

---

## What We'll Have In The Morning

If everything runs:
- Rhea's loop closed (vocabulary test + Lean 4 + proof corpus)
- 360M rank-8 fully evaluated on v2 battery
- Targeted v_proj CMA-ES results on 360M
- Llama-3.2-1B full diagnostic suite (universality test)
- Gemma-3-1B full diagnostic suite (third model family)
- Basin geometry on Llama (ridged or not?)
- Possibly: first CMA-ES run on Llama (if basins are ridged)

The question the morning answers: is this universal, or Qwen-specific?
