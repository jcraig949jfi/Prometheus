# Overnight Plan — 2026-03-25 (revised)

*The only question tonight: are the results real?*
*Everything else waits until morning.*

*GPU: Rhea batch 4 (1.7B targeted CMA-ES). DO NOT TOUCH.*

---

## Phase 1: Kill Shots First (45 min)

Do these before anything else. If any fails, STOP. Don't start Nous, don't start Hephaestus, don't write reports. Diagnose.

### Check A: NCD Baseline Integrity (5 min)
```bash
cd agents/hephaestus/src
python -c "
from test_harness import run_ncd_baseline
r = run_ncd_baseline()
print(f'NCD: acc={r[\"accuracy\"]:.1%} ({r[\"correct_count\"]}/{r[\"n_traps\"]})')
print(f'NCD: cal={r[\"calibration\"]:.1%} ({r[\"calibrated_count\"]}/{r[\"n_traps\"]})')
for t in r['trap_results']:
    mark = 'ok' if t.get('is_correct') else 'X '
    print(f'  [{mark}] {t[\"prompt\"][:60]:62s} -> {t.get(\"top_candidate\",\"?\")}')"
```
**Expected:** 20% accuracy (3/15), 7% calibration (1/15). If these numbers are different from what we've been reporting, we have a measurement error and nothing downstream is trustworthy.

### Check B: IBAI v2 Single Trap (5 min)
```bash
cd agents/hephaestus/src
python -c "
from test_harness import load_tool_from_file
tool = load_tool_from_file('../forge/ibai_v2.py')
r = tool.evaluate('9.11 is less than 9.9. Which number is larger?',
                   ['9.11', '9.9', 'They are equal', 'Cannot be determined'])
for item in r:
    print(f'  {item[\"candidate\"]:30s} score={item[\"score\"]:.4f}  {item[\"reasoning\"]}')"
```
**Expected:** 9.9 ranked first with positive constraint score. If it gets this wrong, the numeric eval fix isn't working and our reported 67% accuracy is inflated.

### Check C: v_proj Ablation — THE Kill Shot (30 min)

This is the causal claim. If zeroing v_proj LoRA doesn't collapse survival rate, the entire "v_proj is the circuit" narrative is wrong.

Load the evolved 135M on CPU. Zero out only the v_proj LoRA adapter weights. Run 5 traps. Does SR collapse to near zero?

```bash
# Run from WSL where the evolved model lives
python -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_path = 'path/to/evolved_135M'  # UPDATE THIS
base = AutoModelForCausalLM.from_pretrained('HuggingFaceTB/SmolLM2-135M-Instruct',
                                             torch_dtype=torch.float32, device_map='cpu')
model = PeftModel.from_pretrained(base, model_path)

# Record which params are v_proj
vproj_params = {}
for name, param in model.named_parameters():
    if 'v_proj' in name and 'lora' in name:
        vproj_params[name] = param.data.clone()
        param.data.zero_()
        print(f'Zeroed: {name} ({param.numel()} params)')

print(f'\\nZeroed {len(vproj_params)} v_proj LoRA tensors')
print('Now run eval traps on this model and check SR...')
# Run your 5 standard eval traps here
"
```

**Pass:** SR collapses from ~92% to near zero. v_proj is the circuit.
**Fail:** SR stays high. The LoRA is working through a different pathway. Stop everything and investigate.

**If Check C fails, nothing else matters.** The entire Rhea narrative rests on v_proj being the ejection circuit. If it's not, we need to go back to Ignis and figure out what's actually happening.

---

## Phase 2: Curve Integrity (30 min)

Only proceed here if Phase 1 passes.

### Check D: Phase Transition Plots
Parse the CMA-ES logs for 135M and 360M runs. Plot SR over generations.

**What you're looking for:**
- Flat near zero for many generations → sudden jump → plateau at high SR
- NOT a smooth sigmoid climb (that's gradient descent, not a phase transition)
- NOT a noisy random walk (that's CMA-ES not converging)

The 135M transition should be around gen 60-70. The 360M (rank-8) should be around gen 21.

**If the curves are smooth:** The "phase transition" language in our findings is wrong. Still might be a valid result (gradual improvement is still improvement), but the narrative needs to change.

**If the curves are noisy with no clear transition:** CMA-ES might be finding lucky genomes that don't generalize. Check if the best genome from gen 113 is the same genome that caused the "transition," or if it's a different one.

### Check E: Cross-Scale Trap Agreement
Compare which specific traps the 135M and 360M evolved models get right.

**Pass:** >60% overlap in which traps are solved. Same mechanism, same traps.
**Partial:** 40-60% overlap. Similar mechanism, different expression at different scales. Publishable but weaker.
**Fail:** <40% overlap. Two different lucky hacks. The "universal mechanism" claim is overstated.

---

## Phase 3: Metacognition Reality Check (45 min)

Only proceed here if Phases 1-2 pass.

### Check F: Hand-Verify 10 Metacognition Examples
Pull 10 cases where the evolved 135M said "I don't know" or expressed uncertainty. Read them. Are these genuinely uncertain cases where hedging is appropriate?

Then pull 10 cases where it was confident. Is it correct?

**Red flags:**
- "I don't know" as generic cop-out on easy questions
- High confidence on questions it gets wrong
- Identical hedging language on every uncertain case (template, not genuine reasoning)

### Check G: Confidence Calibration
For every trap: plot (model confidence, actual correctness). Does confidence correlate with correctness?

**Pass:** Positive correlation. Higher confidence → more likely correct.
**Fail:** Flat line or negative correlation. The model's confidence is decorrelated from its accuracy. The 75% metacognition number might be measuring the wrong thing.

### Check H: Logit Lens Eyeball
Pick one trap where the evolved 135M gets the right answer. Run logit lens on the BASE 135M (pre-evolution) on the same trap.

**What you need to see:** The correct answer token probability rises in middle layers and falls in late layers. That's the ejection. If the correct answer was never computed internally, "ejection" is the wrong word — you can't eject something that was never there.

---

## Phase 4: Generalization (30 min)

Only if Phases 1-3 pass. This is the "are we overfitting" check.

### Check I: Held-Out Novel Traps
5 questions NOT in the trap battery, using different numbers but same reasoning patterns:
```
"Is 7.22 larger than 7.3?"                                    → No
"A shirt and tie cost $12. Shirt costs $10 more. Tie costs?"   → $1
"Bob is faster than Carol. Carol is faster than Dave. Slowest?" → Dave
"You have 20 marbles. All but 5 are blue. How many blue?"      → 5
"Two fair dice. First shows 6. Does that affect the second?"   → No
```

**Pass:** ≥3/5 correct. The model learned reasoning patterns, not trap text.
**Fail:** 0-1 correct. Memorization, not generalization. The 92% SR and 75% metacognition may only apply to the specific traps in the battery.

### Check J: Provenance Gate
Grep through every training corpus file for any exact match with trap battery prompts or answers.

```bash
# Search all training data for trap contamination
grep -r "9.11" path/to/training/corpus/ | grep -i "larger\|greater\|bigger"
grep -r "bat and ball" path/to/training/corpus/
grep -r "overtake.*2nd\|overtake.*second" path/to/training/corpus/
```

**Pass:** Zero hits. The eval traps never entered the training pipeline.
**Fail:** Any hit. Contamination. That specific result is invalidated.

---

## Phase 5: Fire and Forget (start ONLY after Phase 1 passes)

These run in the background and don't need attention until morning.

### Terminal 1: Nous continuous
```bash
cd agents/nous && python src/nous.py --unlimited 2>&1 | tee runs/overnight_0325.log
```

### Terminal 2: Hephaestus continuous
```bash
cd agents/hephaestus && python src/hephaestus.py 2>&1 | tee runs/overnight_0325.log
```

### Terminal 3: Full leaderboard re-eval
```bash
cd agents/hephaestus/src
python -c "
from test_harness import load_tool_from_file, run_trap_battery
from pathlib import Path
results = []
for py in sorted(Path('../forge').glob('*.py')):
    if py.stem.startswith('__'): continue
    try:
        tool = load_tool_from_file(py)
        r = run_trap_battery(tool)
        results.append((py.stem, r['accuracy'], r['calibration'], r['passed'],
                        r.get('margin_accuracy',0), r.get('margin_calibration',0)))
        status = 'PASS' if r['passed'] else 'FAIL'
        print(f'{py.stem:55s} acc={r[\"accuracy\"]:.0%} cal={r[\"calibration\"]:.0%} [{status}]')
    except Exception as e:
        print(f'{py.stem:55s} ERROR: {e}')
results.sort(key=lambda x: (x[1]+x[2]), reverse=True)
print('\n=== TOP 10 ===')
for name, acc, cal, passed, ma, mc in results[:10]:
    print(f'{name:55s} acc={acc:.0%} cal={cal:.0%}')
" 2>&1 | tee ../runs/full_leaderboard_0325.txt
```

---

## Sequencing

```
PHASE 1 — KILL SHOTS (45 min, stop if any fails)
  A: NCD baseline              [5 min]
  B: IBAI v2 single trap       [5 min]
  C: v_proj ablation           [30 min]  ← THE kill shot

PHASE 2 — CURVES (30 min)
  D: Phase transition plots    [20 min]
  E: Cross-scale agreement     [10 min]

PHASE 3 — METACOGNITION (45 min)
  F: Hand-verify 10 examples   [20 min]
  G: Confidence calibration    [10 min]
  H: Logit lens eyeball        [15 min]

PHASE 4 — GENERALIZATION (30 min)
  I: Novel held-out traps      [15 min]
  J: Provenance search         [15 min]

PHASE 5 — FIRE AND FORGET (after Phase 1 clears)
  Nous + Hephaestus continuous
  Full leaderboard re-eval

BACKGROUND (don't touch):
  Rhea batch 4 on GPU
  Nemesis build (engineer)
```

**Total active time: ~2.5 hours.**
**By morning you know one of two things:**
1. All 10 checks pass → the results are real, proceed with full confidence
2. Something broke → you know exactly what, and you stopped before building more on a cracked foundation

---

## Decision Tree

```
Phase 1 fails → STOP. Diagnose. Everything downstream is suspect.
Phase 2 fails → Results might be real but narrative needs revision.
                 "Phase transition" → "gradual improvement"
                 Still publishable, weaker claim.
Phase 3 fails → Metacognition metric needs redefinition.
                 Core ejection finding may still hold.
Phase 4 fails → Overfitting to trap battery.
                 Need to expand eval before making claims.
All pass      → Ship it. The fire is real.
```
