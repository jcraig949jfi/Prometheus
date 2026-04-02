# New Rig Setup — Ignis Experiments
**For:** Athena instance on second machine
**Purpose:** Run Phi-2 architecture sweep in parallel with M1's Llama batch
**Date:** 2026-04-02

---

## Step 1: Install Python 3.11

Download and install Python 3.11 from https://www.python.org/downloads/
- Check "Add python.exe to PATH" during install
- Verify: `python --version` should show 3.11.x

## Step 2: Clone the repo

```powershell
cd F:\
git clone <your-remote-url> Prometheus
cd F:\Prometheus\ignis
```

## Step 3: Install dependencies

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install transformer-lens transformers tokenizers huggingface-hub
pip install cma numpy scipy scikit-learn pandas matplotlib
pip install duckdb networkx
```

**Verify CUDA:**
```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0)}')"
```

Should print: `CUDA: True, Device: NVIDIA GeForce RTX 5060 Ti`

**Verify TransformerLens:**
```powershell
python -c "from transformer_lens import HookedTransformer; print('TL OK')"
```

## Step 4: HuggingFace login (for Llama access later)

```powershell
pip install huggingface-cli
huggingface-cli login
```

Paste the HF token when prompted. Token is in James's HuggingFace settings at https://huggingface.co/settings/tokens.

## Step 5: Pre-download the Phi-2 model

The first run will download ~5.5GB of weights. Better to do this explicitly:

```powershell
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/phi-2'); print('Phi-2 downloaded')"
```

This caches the model in `~/.cache/huggingface/`. Takes a few minutes on decent internet.

## Step 6: Run the Phi-2 batch

```powershell
cd F:\Prometheus\ignis
.\run_batch_phi2.bat
```

**Expected runtime:** ~10 hours total.
**Expected VRAM:** ~12-14GB. Tight but should fit. If P1 (baseline) OOMs, the batch auto-aborts.
**Popsize reduced to 24** (from 32) to save ~1GB VRAM during evolution.

## What this batch does

| Job | Time | What |
|-----|------|------|
| P1 | 5m | Baseline eval — how many traps does Phi-2 solve unsteered? |
| P2 | 3h | L12 evolution (38% depth) — early-mid layer |
| P3 | 3h | L20 evolution (63% depth) — mid-late layer |
| P4 | 3h | L28 evolution (88% depth) — late layer |
| P5 | 30m | Multi-layer combo — does L12+L20+L28 beat single layers? |
| P6 | 5m | Ghost trap — bypass or amplification? (expect bypass) |
| P7 | 2m | v3 battery baseline — harder traps on Phi-2 |

## Monitoring

Check progress anytime:
```powershell
type CURRENT_JOB.txt                          # What's running now
type results\queue_log.jsonl                   # Job start/end times
Get-Content results\batch_phi2\*_stdout.log -Tail 20  # Latest output
```

Look for held-out evals every 25 generations:
```powershell
Select-String "Correct:|FLIP" results\batch_phi2\P2_phi2_L12_stdout.log
```

## Skip/Kill

- Create `KILL_QUEUE` file in ignis/ to abort after current job
- Create `SKIP_P3`, `SKIP_P4`, etc. to skip specific jobs
- If P1 OOMs, the batch stops automatically

## After Phi-2 finishes

Push results back:
```powershell
git add results/batch_phi2/
git commit -m "Phi-2 architecture sweep results"
git push
```

Then pull on M1 so Athena there can analyze cross-architecture.

## Context: What we're building

This is part of a 3-week architecture × scale matrix sweep. We're testing whether epistemic suppression (models knowing the right answer but outputting the wrong one) is universal across transformer families.

**So far:**
- Qwen 1.5B: 30/30 steered (corpus-first + early layers), bypass confirmed
- Pythia 1.4B: 29/30 steered (L8 at eps×2.0), bypass confirmed
- Gemma 2B: impenetrable (21/30 baseline, zero flips at any layer)
- Llama 1B: running on M1 right now

**Phi-2 is the 4th/5th architecture family.** At 2.7B it's also our largest local model. If it shows the same bypass pattern, that's 3 architectures confirming universality. If it's impenetrable like Gemma, that's an architecture-dependent finding.

The key metrics to watch:
- **Baseline SR**: how many traps does unsteered Phi-2 solve?
- **Best steered SR**: how many after evolution?
- **Flip count and break count**: which traps flip, do any break?
- **Ghost trap cos_with_residual**: bypass (near 0) or amplification (>0.3)?
