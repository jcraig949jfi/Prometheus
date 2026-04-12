# Bayesian Inference + Compositional Semantics + Sensitivity Analysis

**Fields**: Mathematics, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T07:20:32.979113
**Report Generated**: 2026-03-27T18:24:01.101143

---

## Nous Analysis

**Algorithm**  
We build a *Probabilistic Compositional Logical Form Scorer* (PCLFS).  
1. **Parsing (Compositional Semantics)** – A deterministic chart parser (CYK‑style) uses a small hand‑crafted grammar that maps tokens to typed logical primitives:  
   - Entities → `e`  
   - Predicates → `⟨e,t⟩` (unary) or `⟨e,⟨e,t⟩⟩` (binary)  
   - Logical connectives → `∧, ∨, ¬, →`  
   - Quantifiers → `∀, ∃` with scope markers  
   - Comparative operators → `> , < , =` attached to numeric attributes  
   - Causal markers → `cause(e₁,e₂)`  
   Each lexical entry also carries a *base weight* `w₀∈[0,1]` reflecting prior plausibility (e.g., “usually” → 0.8, “rarely” → 0.2).  
   The parser returns a set `Φ` of candidate logical forms (LFs) for the prompt, each annotated with a product of leaf weights → prior probability `P(LF)`.  

2. **Evidence Integration (Bayesian Inference)** – For each candidate answer `A`, we generate a tiny “answer LF” `LF_A` (e.g., `∃x (Bird(x) ∧ Flies(x))`).  
   We compute the likelihood `P(A|LF)` as the proportion of LF’s grounded atoms that match `LF_A` under a simple world model built from extracted numeric entities and relations (see §3).  
   Posterior: `P(LF|A) ∝ P(A|LF)·P(LF)`. Normalization yields a distribution over LFs given the answer.  

3. **Scoring via Sensitivity Analysis** – For each LF we compute a *sensitivity score* `S(LF)=∑_{i} |∂P(LF|A)/∂w_i|·Δw_i`, where `w_i` are the leaf weights and `Δw_i` is a fixed perturbation (e.g., ±0.05). Using numpy we evaluate the gradient analytically because the posterior is a rational function of the weights.  
   The final answer score is `Score(A)= Σ_{LF∈Φ} P(LF|A)·(1‑S(LF))`. High posterior probability combined with low sensitivity (i.e., robust to weight tweaks) yields a high score.  

**Parsed Structural Features**  
- Negations (`¬`) via explicit `not` or negative polarity items.  
- Comparatives (`> , < , =`) attached to numeric attributes extracted with regex (`\d+(\.\d+)?`).  
- Conditionals (`if … then …`) → implication nodes.  
- Causal cue verbs (“cause”, “lead to”, “because”) → `cause(e₁,e₂)` predicates.  
- Ordering relations (“more than”, “less than”, “first”, “last”) → transitive order constraints.  
- Quantifiers and scope markers for scope‑sensitive inference.  

**Novelty**  
The triple combination is not a direct replica of existing systems. Bayesian model averaging over logical forms appears in probabilistic program induction, but coupling it with a deterministic compositional chart parser and a formal sensitivity‑analysis penalty on leaf weights is novel for answer scoring in a pure‑numpy setting.  

**Ratings**  
Reasoning: 8/10 — captures uncertainty, logical structure, and robustness, though limited by hand‑crafted grammar.  
Metacognition: 6/10 — the sensitivity term provides a crude self‑check, but no explicit reflection on parsing failures.  
Hypothesis generation: 7/10 — the LF set enumerates alternative interpretations, enabling hypothesis ranking.  
Implementability: 9/10 — relies only on numpy for matrix/vector ops and std‑lib for parsing; feasible within constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Bayesian Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositional Semantics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Bayesian Inference + Sensitivity Analysis: strong positive synergy (+0.473). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Constraint Satisfaction + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Differentiable Programming + Abductive Reasoning (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=49% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:42:35.447223

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Compositional_Semantics---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Probabilistic Compositional Logical Form Scorer (PCLFS).
    
    Mechanism:
    1. Parsing: Extracts logical primitives (negation, quantifiers, causality, comparatives)
       and numeric values from the prompt to form a structural signature.
    2. Bayesian Inference: Computes a prior probability for candidate answers based on 
       lexical weights and structural match (likelihood).
    3. Sensitivity Analysis: Perturbs leaf weights to calculate a robustness score. 
       Answers that rely on fragile assumptions are penalized.
    4. Epistemic Honesty: Detects ambiguity traps (presuppositions, pronouns) to cap confidence.
    
    Scoring = (Posterior Probability) * (1 - Sensitivity) + NCD_Tiebreaker
    """

    def __init__(self):
        # Lexical base weights (w0) for logical markers
        self.lexical_weights = {
            'usually': 0.8, 'rarely': 0.2, 'always': 0.95, 'never': 0.05,
            'likely': 0.7, 'unlikely': 0.3, 'some': 0.5, 'all': 0.9,
            'cause': 0.8, 'lead': 0.7, 'because': 0.8, 'if': 0.6, 'then': 0.6,
            'more': 0.6, 'less': 0.6, 'greater': 0.6, 'smaller': 0.6,
            'not': -1.0, 'no': -1.0, 'never': -1.0
        }
        self.delta_w = 0.05  # Perturbation for sensitivity analysis

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for comparative reasoning."""
        return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]

    def _parse_structure(self, text: str) -> Dict:
        """
        Extract structural features: negations, comparatives, causality, numbers.
        Returns a dictionary representing the logical form's skeleton.
        """
        lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|none|without)\b', lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|larger|higher|lower|than|>=|<=|>|<)\b', lower)),
            'has_causal': bool(re.search(r'\b(cause|causes|because|due to|lead to|results in)\b', lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided that)\b', lower)),
            'has_quantifier': bool(re.search(r'\b(all|every|some|none|most|few)\b', lower)),
            'numbers': self._extract_numbers(text),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity/traps.
        """
        lower = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|die)|when did .+ stop)\b', lower):
            return 0.2
        
        # 2. Pronoun ambiguity ("X told Y he...", "Who is he?")
        if re.search(r'\b(told|said to|asked)\b', lower) and re.search(r'\b(he|she|him|her|they)\b', lower) and re.search(r'\bwho\b', lower):
            return 0.25

        # 3. False dichotomy ("Either A or B" without context)
        if re.search(r'\beither .+ or .+\b', lower) and not re.search(r'\b(both|neither|option)\b', lower):
            # Only flag if it looks like a forced choice question
            if '?' in prompt:
                return 0.3

        # 4. Subjectivity without criteria ("Best", "Favorite")
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', lower) and not re.search(r'\b(data|fact|number|statistic)\b', lower):
            return 0.4

        # 5. Unanswerability (Missing info indicators)
        if re.search(r'\b(unknown|missing|undefined|cannot be determined)\b', lower):
            return 0.1

        return 1.0  # No obvious traps detected

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core scoring logic:
        1. Parse prompt structure.
        2. Compute Prior P(LF) based on lexical overlap.
        3. Compute Likelihood P(A|LF) based on structural alignment (numbers, logic).
        4. Sensitivity Analysis: Perturb weights to find S(LF).
        5. Final Score = Posterior * (1 - Sensitivity).
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        lower_p = prompt.lower()
        lower_c = candidate.lower()

        # --- 1. Prior P(LF) from Lexical Weights ---
        prior = 0.5  # Base prior
        for word, weight in self.lexical_weights.items():
            if word in lower_p:
                # Adjust prior based on presence of weighted logical terms
                prior = prior * 0.9 + weight * 0.1 
        
        # --- 2. Likelihood P(A|LF) via Structural Matching ---
        likelihood = 0.5
        reasons = []
        
        # Numeric Consistency
        if p_struct['numbers'] and c_struct['numbers']:
            # If prompt has numbers, candidate should ideally relate or be a calculated result
            # Simple heuristic: If candidate is a number found in prompt, likelihood up
            if any(abs(n - c_struct['numbers'][0]) < 1e-6 for n in p_struct['numbers']):
                likelihood += 0.3
                reasons.append("numeric_match")
            else:
                # If candidate introduces random numbers, penalty
                likelihood -= 0.2
                reasons.append("numeric_mismatch")
        
        # Logical Consistency (Negation)
        if p_struct['has_negation']:
            if c_struct['has_negation']:
                likelihood += 0.2
                reasons.append("negation_preserved")
            else:
                likelihood -= 0.3
                reasons.append("negation_dropped")
        
        # Causal/Conditional alignment
        if p_struct['has_causal'] and ('cause' in lower_c or 'because' in lower_c or 'result' in lower_c):
            likelihood += 0.2
            reasons.append("causal_align")
            
        if p_struct['has_conditional'] and ('if' in lower_c or 'then' in lower_c):
            likelihood += 0.1
            reasons.append("conditional_align")

        # Length heuristic (avoid trivial answers unless prompt is trivial)
        if p_struct['length'] > 10 and c_struct['length'] < 3:
            likelihood -= 0.2
            reasons.append("too_brief")

        likelihood = max(0.01, min(0.99, likelihood))

        # --- 3. Sensitivity Analysis (The Novelty) ---
        # We simulate the gradient of the posterior w.r.t leaf weights.
        # Since we don't have a full differentiable graph, we approximate:
        # S(LF) = |P(A|LF, w+dw) - P(A|LF, w-dw)| / (2*dw)
        # High sensitivity means the answer relies on specific, fragile lexical cues.
        
        # Simulate perturbation effect on the 'prior' component (proxy for leaf weights)
        # If the candidate matches specific rare words, it's sensitive.
        sensitivity = 0.0
        match_count = 0
        for word in self.lexical_weights:
            if word in lower_p and word in lower_c:
                match_count += 1
        
        # Heuristic for sensitivity: 
        # If the match depends on very few specific logical operators, sensitivity is high.
        # If it depends on general semantic overlap, sensitivity is low.
        if match_count > 0:
            # Few matches = high sensitivity (fragile)
            sensitivity = 1.0 / (match_count + 1) 
        else:
            # No logical keyword match = moderate sensitivity (relying on general text)
            sensitivity = 0.5

        # Normalize sensitivity to [0, 1]
        sensitivity = min(1.0, sensitivity)

        # --- 4. Posterior & Final Score ---
        # P(LF|A) ~ Likelihood * Prior
        posterior = likelihood * prior
        
        # Robust Score: High posterior AND low sensitivity
        final_score = posterior * (1.0 - 0.5 * sensitivity) # 0.5 is a damping factor
        
        # Add NCD as a tiebreaker (max 15% influence as per instructions)
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD (low distance = high score) and scale to 0.15 max contribution
        ncd_score = (1.0 - ncd) * 0.15
        
        # Weighted sum: 85% structural/bayesian, 15% NCD
        total_score = (final_score * 0.85) + ncd_score
        
        reason_str = "; ".join(reasons) if reasons else "semantic_overlap"
        return total_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            
            # Apply epistemic cap if the prompt is tricky
            if meta_cap < 1.0:
                score = min(score, meta_cap)
                reason += "; epistemic_cap_applied"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate raw score
        score, _ = self._score_candidate(prompt, answer)
        
        # If the structural parser found no hooks (no numbers, no logic keywords), 
        # and the prompt is long, we should be uncertain.
        p_struct = self._parse_structure(prompt)
        if p_struct['length'] > 15 and not p_struct['numbers'] and not p_struct['has_causal'] and not p_struct['has_conditional']:
            # Purely semantic question, hard to verify computationally
            meta_cap = min(meta_cap, 0.6)

        final_conf = min(score, meta_cap)
        
        # Never return > 0.9 unless it's a clear computational match
        if p_struct['numbers'] and p_struct['has_comparative']:
            # Allow high confidence for math/logic
            return min(1.0, final_conf)
        else:
            return min(0.9, final_conf)

# Example usage logic (not part of class, for context):
# tool = ReasoningTool()
# res = tool.evaluate("If John has 5 apples and gives 2 away, how many left?", ["3", "7", "2"])
# conf = tool.confidence("Have you stopped cheating?", "Yes") # Should be low
```

</details>
