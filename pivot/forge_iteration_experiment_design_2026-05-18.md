# Forge Iteration Experiment Design — v1 Baseline vs v2 Variants

**Filed:** 2026-05-18
**Purpose:** Structured comparison of forge parameters against the v1 control run
**Status:** Design phase — v1 control running, v2 variants to be designed

---

## 1. The v1 Control (Currently Running)

The current forge run is the control group. Its parameters are fully characterized:

### Upstream Parameters
- **Concept source:** Nous combinatorial engine, 95-concept pool, cross-field bias 0.8
- **Concept ranking:** Coeus priority (composite_score + forge_effect + pair_synergy)
- **Concept format:** Triples (3 concepts per combination)

### Generation Parameters
- **Model:** qwen/qwen3.5-397b-a17b (NVIDIA API)
- **Temperature:** 0.4
- **Max tokens:** 4096
- **Prompt template:** 8 frames (A-H) with weighted rotation
  - Frame A (Structural, weight 5): parse negations, comparatives, conditionals
  - Frame B (Constructive, weight 15): compute Bayesian posteriors, PEMDAS
  - Frame C (Dynamics, weight 10): model reasoning as state evolution
  - Frame D (Judgment, weight 10): epistemic honesty, ambiguity recognition
  - Frame E (Computational, weight 20): compute first, then score
  - Frame F (Adversarial, weight 10): attack each candidate
  - Frame G (Metacognitive, weight 10): reason about reasoning
  - Frame H (Primordial, weight 20): library-augmented computation
- **Post-generation fixers:** Unicode sanitizer, import injection, confidence wrapper, evaluate wrapper

### Evaluation Parameters
- **Battery:** 186 probes, 89 categories, mapped to R1-R6
- **NCD baseline:** ~42% accuracy, ~46% calibration
- **Admission gates:** Accuracy (beat NCD) OR Novelty (min_ncd > 0.85 + acc >= 20%)
- **Novelty computation:** Source-code NCD against forge/ library

### v1 Observed Outputs
- **Forge rate:** 4.3% (combined accuracy + novelty gates)
- **Mechanism families produced:** 5 (regex features, NCD, category parsers, meta-confidence, computation specialists)
- **Tier distribution:** R3-strong (mean 49%), R2/R4-weak (mean 25-28%)
- **Behavioral diversity:** NCD mean 0.432 (moderate)

---

## 2. The 100-Candidate Profile

Select 100 representative concept combinations from the queue with full provenance:

```json
{
  "combo_id": 1,
  "concepts": ["Active Inference", "Criticality", "Model Checking"],
  "concept_fields": ["Neuroscience", "Physics", "Formal Methods"],
  "composite_score": 6.3,
  "coeus_priority": 7.1,
  "coeus_enrichment": { "strong_drivers": [...], "inhibitors": [...] },
  "nous_response_text": "The theoretical analysis...",
  "v1_result": {
    "model": "qwen/qwen3.5-397b-a17b",
    "frame": "E",
    "status": "scrap",
    "reason": "trap_battery_failed (acc=34%)",
    "accuracy": 0.34,
    "tier_profile": {"R1": 0.42, "R2": 0.25, ...},
    "mechanism_family": "regex+ncd",
    "novelty_min_ncd": 0.72
  }
}
```

This frozen set becomes the benchmark. Every v2 variant runs against the same 100 combinations.

### Selection criteria for the 100
- 20 that forged successfully in v1 (the baseline "works")
- 30 near-misses (35-42% accuracy, almost passed)
- 30 moderate failures (20-35%)
- 20 hard failures (<20% or validation errors)

This gives a representative cross-section of difficulty.

---

## 3. Variables to Perturb (One at a Time)

### 3.1 Model (highest expected impact)

| Variant | Model | Why |
|---------|-------|-----|
| v2-M1 | Claude (Sonnet 4.5 via Augment) | Strongest structured code gen, different training |
| v2-M2 | DeepSeek-Coder-V3 | Strong algorithmic code, open-weight |
| v2-M3 | Gemini 2.5 Flash | Different architecture entirely |
| v2-M4 | qwen-397B (control) | Same model, confirms reproducibility |

**Measure:** Do different models produce different mechanism families on the same concept combinations? Or the same 5 patterns?

### 3.2 Prompt Strategy (medium-high expected impact)

| Variant | Strategy | Change |
|---------|----------|--------|
| v2-P1 | Algorithm-first | "Implement [specific algorithm] to evaluate reasoning" instead of concept-inspired |
| v2-P2 | Mechanism-targeted | "Build a tool that does [backtracking / belief propagation / structural mapping]" |
| v2-P3 | Gap-filling | "The library lacks R4 search tools. Generate one." |
| v2-P4 | Exemplar-based | "Here is an existing tool that works. Generate a DIFFERENT approach to the same problems." |
| v2-P5 | Adversarial | "Generate a tool that solves problems the following tool gets WRONG: [tool code]" |
| v2-P6 | Concept-first (control) | Same prompt as v1, confirms baseline |

### 3.3 Temperature / Sampling (medium expected impact)

| Variant | Temperature | Why |
|---------|-------------|-----|
| v2-T1 | 0.2 | More deterministic — fewer weird mechanisms but higher pass rate? |
| v2-T2 | 0.4 (control) | Current setting |
| v2-T3 | 0.7 | More creative — more weird mechanisms but lower pass rate? |
| v2-T4 | 0.9 | High variance — maximum novelty at cost of quality? |

### 3.4 Concept Format (medium expected impact)

| Variant | Format | Why |
|---------|--------|-----|
| v2-C1 | Single concept | "Build a tool using ONLY Bayesian Inference" — forces depth over breadth |
| v2-C2 | Pair | Two concepts instead of three |
| v2-C3 | Triple (control) | Current format |
| v2-C4 | Quintuple | Five concepts — forces more cross-domain integration |
| v2-C5 | Concept + problem type | "Using Active Inference, build a tool for constraint satisfaction problems" |

### 3.5 Evaluation Battery (low impact on generation, high impact on measurement)

| Variant | Battery | Why |
|---------|---------|-----|
| v2-B1 | 186 probes (control) | Current battery |
| v2-B2 | 186 probes + paraphrased versions | Same problems, different wording — tests surface invariance |
| v2-B3 | 186 probes + symbol-relabeled versions | Names/numbers changed — tests genuine computation |
| v2-B4 | External anchors (ARC-AGI, BIG-Bench) | Probes the model hasn't seen in training |

---

## 4. Experiment Protocol

### Phase 1: Profile the 100 (1 session)
- Select 100 candidates from queue
- Record full provenance (concepts, scores, enrichments, Nous text)
- Run v1 on all 100, store complete results
- This is the immutable baseline

### Phase 2: Single-variable sweeps (1 session each)
For each variable category, run one variant against the same 100 candidates:
- Record identical provenance metadata
- Store complete results in same schema
- Compare against v1 baseline

### Phase 3: Analysis (1 session)
For each variant, measure:
- **Forge rate change** vs v1 baseline
- **Mechanism family distribution** — did new families appear?
- **Tier profile shift** — did R4/R5 coverage improve?
- **Behavioral diversity** — NCD of output vectors across variants
- **Rarity score** — do variant tools solve different problems?
- **Mechanism knockout** — are new mechanisms genuine or decorative?

### Phase 4: Best-of-breed (1 session)
- Combine the best-performing variables (e.g., "Claude + algorithm-first + temperature 0.7 + pair concepts")
- Run full 100-candidate sweep with combined parameters
- Compare against all single-variable runs

---

## 5. What We Expect to Learn

**Most likely finding:** Model choice matters more than prompt strategy. Different models will produce different mechanism families because their training data and code-gen biases differ. qwen-397B's 5-pattern ceiling is a property of qwen, not of the task.

**Possible surprise:** Algorithm-first prompting might dramatically increase mechanism diversity even within the same model, because it bypasses the model's default "here's how I solve reasoning tasks" pattern and forces it to implement a specific algorithm it has in its weights.

**What would change the roadmap:**
- If Claude produces 10+ new mechanism families → invest in Augment API budget for Round 2
- If algorithm-first prompting works across models → redesign the Nous concept engine to output algorithm targets, not concept triples
- If temperature 0.7-0.9 produces more genuine novelty → shift the forge to high-temp + aggressive filtering
- If paraphrased batteries reveal most tools are surface-dependent → invest in invariance testing before mechanism analysis
- If nothing works → the forge paradigm (LLM code gen → evaluation) may have a ceiling, and Apollo's evolutionary approach becomes more important

---

## 6. Resource Budget

| Resource | Estimate |
|----------|----------|
| NVIDIA API (qwen, 100 candidates) | ~6 hours runtime |
| Augment API (Claude, 100 candidates) | ~4 hours + token cost |
| DeepSeek API (100 candidates) | ~4 hours + token cost |
| Gemini API (100 candidates) | ~3 hours + token cost |
| Evaluation runs (186 probes × 100 tools × N variants) | ~2 hours per variant |
| Analysis | 1 session |
| **Total** | ~2-3 days of M3 compute, spread across variants |

---

## 7. The Comparison Framework

Every result goes into a single comparison table:

```
| Variant  | Model   | Prompt    | Temp | Forge% | New Mechs | R3 Mean | R4 Mean | Rarity | BehavNCD |
|----------|---------|-----------|------|--------|-----------|---------|---------|--------|----------|
| v1-ctrl  | qwen    | concept   | 0.4  | 4.3%   | 0         | 49%     | 25%     | 0.015  | 0.432    |
| v2-M1    | claude  | concept   | 0.4  | ?      | ?         | ?       | ?       | ?      | ?        |
| v2-P1    | qwen    | algo-1st  | 0.4  | ?      | ?         | ?       | ?       | ?      | ?        |
| ...      |         |           |      |        |           |         |         |        |          |
```

The columns that matter most:
- **New Mechs** — did this variant produce mechanism families we don't have? (the primary question)
- **R4 Mean** — did it improve coverage on the weakest tier?
- **BehavNCD** — is the output behaviorally diverse or more of the same?
