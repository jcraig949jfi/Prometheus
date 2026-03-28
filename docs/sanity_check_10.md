# The 10-Point Sanity Check

*Target: complete by morning. No GPU disruption to Rhea batch 4.*
*All checks use CPU, saved logs, or lightweight 135M inference.*

---

## Check 1: Hand-Verify 10 Metacognition Examples (30 min)
**What:** Take 10 examples where the 135M evolved model said "I don't know" or expressed uncertainty. Read them. Are they genuinely uncertain cases? Then take 10 where it was confident. Is it right?

**Pass if:** The uncertain cases are actually hard/ambiguous. The confident cases are actually correct. No pattern of "I don't know" being used as a generic cop-out.

**How:** Pull from the eval logs. No model loading needed.

---

## Check 2: Check the 135M and 360M Curves (30 min)
**What:** Plot survival rate over generations for both scales. Look for the phase transition — flat near zero for many generations, then a sudden jump.

**Pass if:** Both curves show a discontinuous jump, not a smooth climb. The 135M transition is around gen 60-70. The 360M transition is around gen 21 (rank-8).

**How:** Parse the CMA-ES logs. Matplotlib or just eyeball the numbers. No GPU.

---

## Check 3: Re-run One Tool on One Trap (15 min)
**What:** Run IBAI v2 on the "9.11 is less than 9.9. Which number is larger?" trap manually in a Python REPL.

**Pass if:** It returns 9.9 as the top candidate with positive structural score.

**How:**
```python
import sys; sys.path.insert(0, 'agents/hephaestus/src')
from test_harness import load_tool_from_file
tool = load_tool_from_file('agents/hephaestus/forge/ibai_v2.py')
print(tool.evaluate("9.11 is less than 9.9. Which number is larger?",
                     ["9.11", "9.9", "They are equal", "Cannot be determined"]))
```
CPU only.

---

## Check 4: Check the NCD Baseline (15 min)
**What:** Run NCD on the full 15-trap battery. Verify it scores ~20% accuracy, ~7% calibration.

**Pass if:** Numbers match within 1-2 percentage points of reported values. NCD gets the "easy" ones right (0.999=1, pigeonhole) and fails the traps (bat-and-ball, 9.11 comparison).

**How:**
```python
from test_harness import run_ncd_baseline
r = run_ncd_baseline()
print(f"acc={r['accuracy']:.1%} cal={r['calibration']:.1%}")
```
CPU only.

---

## Check 5: Verify the Provenance Gate (30 min)
**What:** Search training logs and data pipelines for any path where eval trap answers could have leaked into training data. Check that the self-corpus generation pipeline filters out any exact matches with the trap battery prompts.

**Pass if:** No eval trap prompt or answer appears in any training corpus. The Lean 4 verification step only sees arithmetic proofs, not trap battery content.

**How:** Grep through corpus files and training scripts. No GPU.

---

## Check 6: v_proj Ablation Spot-Check (20 min)
**What:** Load the evolved 135M model. Zero out v_proj LoRA weights only. Run 5 traps. Does SR collapse?

**Pass if:** SR drops to near zero when v_proj is zeroed. This confirms v_proj is carrying the ejection suppression, not some other component.

**How:** Load model on CPU (135M fits). Manually zero the v_proj adapter weights, run a handful of traps. This is the causal claim — if zeroing v_proj doesn't collapse performance, the ablation story is wrong.

```python
# Pseudocode
model = load_evolved_135M()
for name, param in model.named_parameters():
    if 'v_proj' in name and 'lora' in name:
        param.data.zero_()
# Run 5 traps, check SR
```

---

## Check 7: Same Traps, Both Scales (20 min)
**What:** Compare which specific traps the 135M and 360M evolved models get right. Are they solving the same traps? Different ones?

**Pass if:** Substantial overlap (>60% of correct traps are the same at both scales). This confirms the suppression mechanism is similar, not that two different lucky hacks happened at different scales. Some divergence is fine — larger models should get harder traps.

**How:** Load eval results from both runs. Build a 2x36 matrix of (trap, correct/wrong). Count agreement. No GPU needed — just parse logs.

---

## Check 8: Logit Lens Eyeball on One Trap (20 min)
**What:** Pick one trap where the evolved 135M gets the right answer. Run logit lens on the BASE (pre-evolution) 135M on the same trap. Visually confirm the correct answer appears at intermediate layers and then gets ejected at the output.

**Pass if:** You can literally see the correct token probability rise in middle layers and fall in late layers. This is the ejection mechanism in action. If the correct answer was never there in the first place, the "ejection" narrative is wrong.

**How:** Load base 135M on CPU. Run `logit_lens_backward.py` on one trap. Plot or print the per-layer probability of the correct answer token. 135M fits in CPU RAM (~600MB).

---

## Check 9: Held-Out Generalization (20 min)
**What:** Write 5 novel reasoning questions that are NOT in the 36-trap battery or the self-corpus. Different phrasing, different numbers, same reasoning patterns. Run the evolved 135M on them.

**Pass if:** It gets at least 3/5 right. The model learned the reasoning pattern, not the specific trap answers.

**Suggested novel traps:**
```
"Is 7.22 larger than 7.3?"  → No (numeric comparison, different numbers)
"A shirt and a tie cost $12. The shirt costs $10 more. How much is the tie?"  → $1 (bat-and-ball variant)
"If Bob is faster than Carol, and Carol is faster than Dave, who is slowest?"  → Dave (transitivity variant)
"You have 20 marbles. All but 5 are blue. How many are blue?"  → 5 (all-but-N variant)
"Two fair dice are rolled. The first shows a 6. Does that affect the second?"  → No (independence variant)
```

**How:** Load evolved 135M on CPU. Generate answers. Manual inspection.

---

## Check 10: Confidence Calibration Scatter (15 min)
**What:** For every trap in the eval battery, plot (model confidence, actual correctness) as a scatter. Does the evolved model express high confidence when right and low confidence when wrong?

**Pass if:** Positive correlation. The model shouldn't be maximally confident on everything — it should know what it knows. A perfectly flat line (same confidence regardless of correctness) means metacognition is fake.

**How:** Parse eval logs for confidence scores and correctness. Scatter plot. No GPU.

---

## Summary

| # | Check | Tests | Time | GPU? |
|---|-------|-------|------|------|
| 1 | Hand-verify metacognition | Quality of uncertainty expressions | 30 min | No |
| 2 | Phase transition curves | Evolution dynamics | 30 min | No |
| 3 | Single tool single trap | IBAI v2 correctness | 15 min | No |
| 4 | NCD baseline | Baseline integrity | 15 min | No |
| 5 | Provenance gate | No data leakage | 30 min | No |
| 6 | v_proj ablation spot-check | Causal claim | 20 min | CPU (135M) |
| 7 | Cross-scale trap agreement | Mechanism consistency | 20 min | No |
| 8 | Logit lens eyeball | Ejection visualization | 20 min | CPU (135M) |
| 9 | Held-out generalization | Not overfitting to traps | 20 min | CPU (135M) |
| 10 | Confidence calibration | Metacognition quality | 15 min | No |

**Total: ~3.5 hours.** Three checks need the 135M model on CPU. Everything else is log parsing and numpy. Nothing touches the GPU.

---

## If any check FAILS

| Check | Failure means | Action |
|-------|-------------|--------|
| 1 | "I don't know" is a cop-out, not real uncertainty | Re-examine metacognition metric definition |
| 2 | Smooth curve, no phase transition | Evolution may be gradient descent in disguise — check CMA-ES config |
| 3 | IBAI v2 gets the trap wrong | Structural parser has a bug — debug before trusting trap battery |
| 4 | NCD baseline is different from reported | Test harness has been modified — check git history |
| 5 | Eval answers in training data | Contamination. Results invalid until clean run. |
| 6 | v_proj zeroing doesn't collapse SR | The circuit isn't in v_proj — ablation claim is wrong |
| 7 | No trap overlap across scales | Different mechanisms, not a universal circuit |
| 8 | Correct answer never appears in middle layers | "Ejection" is a misnomer — the model never had the answer |
| 9 | 0-1 on novel traps | Overfitting to specific trap text, not learning reasoning |
| 10 | Flat confidence regardless of correctness | Metacognition metric is measuring something else |

**Check 5 and 6 are the kill shots.** If provenance is contaminated or v_proj ablation doesn't replicate, stop everything and investigate. The others are gradations of "how real is this" — failing them reduces confidence but doesn't invalidate the program.
