# CAITL → Council Metacognition Prompt Template

*CAITL generates this prompt automatically after each improvement pass. James pastes it to the Council.*

---

## How CAITL Selects the 10 Candidates

After a CAITL improvement pass, score each tool on metacognition potential:

```python
def metacognition_potential(tool, sphinx_results):
    """Score a tool's potential for metacognition enhancement."""
    score = 0.0

    # Already handles ambiguity detection (Tier B traps)?
    tier_b_accuracy = sphinx_results.get_tier_accuracy(tool, tier="B")
    score += tier_b_accuracy * 2.0  # Existing Tier B ability is the strongest signal

    # Has a confidence() method that's non-trivial?
    conf_variance = measure_confidence_variance(tool)  # Does confidence vary across traps?
    score += conf_variance * 1.5  # Tools that already differentiate confidence are closer

    # Produces reasoning strings that mention uncertainty?
    uncertainty_mentions = count_uncertainty_language(tool)  # "ambiguous", "insufficient", "uncertain"
    score += min(uncertainty_mentions / 5.0, 1.0)

    # Uses structural features that relate to answerability?
    has_negation_scope = check_for_negation_handling(tool)
    has_presupposition = check_for_presupposition_detection(tool)
    has_quantifier = check_for_quantifier_logic(tool)
    score += (has_negation_scope + has_presupposition + has_quantifier) * 0.5

    # NOT dominated by NCD fallback?
    ncd_ratio = measure_ncd_dependency(tool)
    if ncd_ratio > 0.5:
        score *= 0.3  # Heavy NCD dependency = low metacognition potential

    return score
```

Take the top 10 by this score. These are tools that already show *some* metacognitive behavior and have the structural primitives to support more.

---

## The Generated Prompt

CAITL fills in the brackets and generates this for James to paste:

---

### For the Titan Council: Metacognition Enhancement Request

You are reviewing 10 reasoning evaluation tools from Project Prometheus. Each tool is a deterministic, numpy-only Python class that scores candidate answers to reasoning questions. Your job: enhance each tool's metacognitive capabilities.

**What metacognition means here:**

A metacognitive reasoning tool doesn't just score "is this answer correct?" — it recognizes *properties of the question itself*:
- Is this question answerable from the information given?
- Does the question contain a false presupposition?
- Are the candidates ambiguous — could multiple answers be correct?
- Is the question asking about reasoning structure (validity) vs factual truth (soundness)?
- Should the confidence be LOW because the question is genuinely uncertain?

**The Tier B challenge:**

Our Sphinx taxonomy has two tiers:
- Tier A (parsing): The answer is computable from the prompt's structure
- Tier B (judgment): The correct response requires recognizing ambiguity, insufficiency, or meta-level properties

Current tools score ~70% on Tier A but ~30% on Tier B. The gap is metacognition. A tool that can parse "Is 9.11 larger than 9.9?" (Tier A) but can't recognize "Have you stopped making errors? Yes or No" as a presupposition trap (Tier B) has no metacognitive ability.

**Tier B categories these tools must handle:**

1. **Answerability classification:** Is this computable, knowledge-required, or genuinely unanswerable?
2. **Presupposition detection:** Does the question assume something that isn't established?
3. **Scope ambiguity:** "Every student passed a test" — the same test or different tests?
4. **Argument strength:** Which of two arguments is logically stronger?
5. **Fallacy identification:** What type of reasoning error is being committed?
6. **Confidence calibration:** "It will probably rain" — how confident should you be?
7. **Validity vs truth:** "All fish can fly. Salmon is a fish. Therefore salmon can fly." — valid argument?
8. **Red herring detection:** Which information in the prompt is irrelevant?
9. **False dichotomy:** Are there options beyond the two presented?
10. **Necessary vs sufficient:** "All squares are rectangles. Is being a rectangle sufficient?"

**Constraints:**

- numpy + stdlib only (no torch, no transformers, no external APIs)
- Must be deterministic (same input → same output, always)
- Must preserve the existing evaluate() + confidence() interface
- Must be self-contained (no shared modules or imports from other tools)
- Do NOT memorize specific trap wordings — implement general structural detection
- The confidence() method is where metacognition lives: return LOW confidence when the question is ambiguous, unanswerable, or contains a presupposition

---

### Tool 1: {tool_name}

**Current performance:**
- Tier A accuracy: {tier_a_acc}%
- Tier B accuracy: {tier_b_acc}%
- Confidence variance: {conf_var} (how much confidence varies across traps)
- NCD dependency: {ncd_ratio}% (lower is better)

**What it already does well:**
{strengths — e.g., "Strong numeric comparison, catches negation, handles transitivity"}

**Where it fails on Tier B:**
{tier_b_failures — e.g., "Fails all presupposition traps, fails answerability classification, gives high confidence on unanswerable questions"}

**Concepts it claims to implement:**
{concept_names — e.g., "Ergodic Theory × Free Energy Principle × Reinforcement Learning"}

**Current code:**
```python
{full tool source code}
```

**Your task:** Rewrite this tool to handle Tier B categories. Specifically:
1. Add presupposition detection (check if the question assumes unstated facts)
2. Add answerability classification (computable / knowledge-required / unanswerable)
3. Make confidence() return <0.3 when the question is ambiguous or unanswerable
4. Preserve all existing Tier A capabilities — do not break what already works

---

### Tool 2: {tool_name}
{... same structure ...}

---

*[Tools 3-10 follow the same template]*

---

### What I'll Do With Your Response

1. Take the best metacognition implementation from each Council member for each tool
2. Cross-pollinate: if Claude's presupposition detector is better than ChatGPT's but ChatGPT's confidence calibration is better, merge both
3. Run the enhanced tools against the full Sphinx battery (Tier A + Tier B)
4. Nemesis attacks the metacognition claims with adversarial paraphrases
5. Survivors become the Tier B evaluation core in the RLVF fitness function
6. Tier B accuracy is weighted 2x higher than Tier A in fitness — judgment matters more than parsing

**The goal: tools that know when they don't know.** A tool that returns high confidence on an unanswerable question is more dangerous than one that gets a parsing trap wrong. Calibrated uncertainty is the highest-value capability for the RLVF fitness function.

---

## Council-Specific Nudges

*Optional: CAITL can add these per-member based on known strengths:*

**Claude:** Focus on the presupposition and validity/soundness distinction. Your recursive self-awareness is strong — apply it to tool design. When should a tool say "this question cannot be answered as posed"?

**ChatGPT:** Focus on the confidence calibration math. You're precise with probability. What's the right function that maps structural ambiguity signals → confidence values? Not sigmoid — something that has a sharp cliff when presupposition is detected.

**Gemini:** Focus on the red herring and false dichotomy detection. Your structural parsing is aggressive — how do you detect irrelevant information in a prompt? What regex patterns signal "this information exists to distract"?

**DeepSeek:** Focus on the answerability classification hierarchy. Your causal reasoning is strong. What features distinguish "computable from structure" from "requires world knowledge" from "genuinely unanswerable"?

**Grok:** Focus on the fallacy identification. Your pattern-matching across categories is fast. Can you build a fallacy taxonomy that maps prompt structure → fallacy type → appropriate response?

---

## CAITL's Post-Council Merge Protocol

After James collects 5 Council responses for each tool:

1. **Extract code blocks** from each response
2. **Test each independently** against Sphinx battery (Tier A + Tier B)
3. **Score matrix:** 10 tools × 5 Council members × (Tier A, Tier B, confidence calibration)
4. **For each tool, pick the best Tier B implementation** regardless of which member wrote it
5. **Merge rule:** If Member X has the best presupposition detector and Member Y has the best confidence function, combine them in a second CAITL local pass: "Here are two implementations. Merge the presupposition logic from A with the confidence function from B."
6. **Run Nemesis adversarial** on the merged tool — paraphrase every Tier B trap, verify the metacognition holds under mutation
7. **Survivors enter forge_v4/** with tag `metacognition: true`

---

## Automation Level

| Step | Automated? | Who |
|------|-----------|-----|
| CAITL improvement pass | Yes (local 7B) | Card 2 |
| Select top 10 metacognition candidates | Yes (scoring function) | Card 2 |
| Generate Council prompt | Yes (template fill) | Card 2 |
| Paste to Council | **James** (5 min) | Human |
| Read responses, pick best ideas | **James** (30-60 min) | Human |
| Merge implementations | Semi-auto (CAITL local merge pass) | Card 2 |
| Test against Sphinx | Yes | Card 2 |
| Nemesis adversarial | Yes | CPU |
| Deposit to forge_v4/ | Yes | Automatic |

James's total time investment: ~35-65 minutes per cycle. The rest is automated. One cycle produces 10 metacognition-enhanced tools that become the Tier B core of the RLVF fitness function.
