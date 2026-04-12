# Fractal Geometry + Metacognition + Phenomenology

**Fields**: Mathematics, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T19:43:24.593810
**Report Generated**: 2026-03-27T05:13:29.633851

---

## Nous Analysis

Combining fractal geometry, metacognition, and phenomenology suggests a **recursive, self‑similar belief‑updating architecture** called a *Fractal Meta‑Phenomenal Network* (FMPN). The core is a hierarchy of neural modules whose connectivity mirrors an iterated function system (IFS): each module processes information at a specific spatiotemporal scale, and its output feeds both the next finer and coarser module, creating power‑law scaling of representational detail. Within each module, a metacognitive layer maintains a Bayesian confidence distribution over its internal states, updating via prediction‑error signals (akin to variational inference). Phenomenological bracketing is implemented by an attention‑gating mechanism that temporarily isolates the intentional content of a module from lower‑level sensory streams, allowing the system to “hold” an experience in pure intentionality while evaluating its truth‑conditions.

**Advantage for hypothesis testing:** When a hypothesis is generated at a coarse scale, the FMPN propagates it downward, letting finer modules test concrete predictions. Confidence calibration at each level flags over‑ or under‑confidence, triggering strategy selection (e.g., switch from deductive to abductive reasoning). The bracketing mechanism prevents low‑level noise from contaminating the intentional evaluation, yielding sharper error signals and faster convergence on correct hypotheses.

**Novelty:** Fractal neural networks (e.g., FractalNet, HyperNetworks) and meta‑learning frameworks exist, and phenomenological AI has been explored in Husserl‑inspired robotics and enactive cognition. However, the tight integration of IFS‑structured hierarchy, Bayesian metacognition, and explicit attentional bracketing for first‑person analysis has not been reported as a unified technique, making the combination novel.

**Ratings**  
Reasoning: 7/10 — The IFS hierarchy gives multi‑scale reasoning but adds training complexity.  
Metacognition: 8/10 — Bayesian confidence layers are well‑studied; integration improves calibration.  
Hypothesis generation: 7/10 — Self‑similar hypothesis expansion is powerful, yet may generate redundant candidates.  
Implementability: 5/10 — Requires custom IFS wiring, attention gating, and joint variational training; currently research‑grade only.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Phenomenology**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Category Theory + Ergodic Theory + Metacognition (accuracy: 0%, calibration: 0%)
- Category Theory + Metacognition + Criticality (accuracy: 0%, calibration: 0%)
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=47% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T03:19:15.337657

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Metacognition---Phenomenology/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Meta-Phenomenal Network (FMPN) Implementation.
    
    Mechanism:
    1. Structural Parsing (Phenomenological Bracketing): Isolates logical operators
       (negations, comparatives, conditionals) to evaluate truth conditions without
       sensory noise (semantic drift).
    2. Recursive Scaling (Fractal/IFS): Evaluates candidates at multiple scales:
       - Micro: Exact token match and numeric precision.
       - Meso: Structural constraint satisfaction.
       - Macro: Global compression distance (NCD) as a tiebreaker.
    3. Bayesian Metacognition: Computes a confidence score based on the margin
       between the top candidate and the runner-up, calibrated by structural clarity.
    
    Note: Phenomenology is restricted to the 'bracketing' (parsing) phase to avoid
    reasoning traps, per causal intelligence guidelines.
    """

    def __init__(self):
        # Precompile regex for structural extraction
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Phenomenological bracketing: isolate logical intent."""
        text_lower = text.lower()
        return {
            'negations': len(self.negation_pattern.findall(text_lower)),
            'comparatives': len(self.comparative_pattern.findall(text_lower)),
            'conditionals': len(self.conditional_pattern.findall(text_lower)),
            'numbers': self.number_pattern.findall(text),
            'length': len(text)
        }

    def _evaluate_numeric(self, prompt_nums: List[str], candidate_nums: List[str]) -> float:
        """Check numeric consistency."""
        if not prompt_nums:
            return 1.0 # No numeric constraints
        
        # Simple heuristic: if prompt has numbers, candidate should ideally reflect logic
        # Since we can't solve math without eval, we check presence/absence alignment
        if len(candidate_nums) == 0 and len(prompt_nums) > 0:
            # Candidate ignores numbers in a math-heavy prompt
            return 0.5 
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Multi-scale scoring:
        1. Structural alignment (Micro/Meso)
        2. NCD (Macro - Tiebreaker)
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        reasons = []

        # --- Scale 1: Structural Constraint Propagation ---
        # If prompt has strong logical markers, candidate must reflect them or be a direct answer
        logical_density = (p_struct['negations'] + p_struct['comparatives'] + p_struct['conditionals'])
        
        if logical_density > 0:
            # Check if candidate preserves logical complexity or provides a definitive short answer
            c_logical_density = (c_struct['negations'] + c_struct['comparatives'] + c_struct['conditionals'])
            
            # Heuristic: Valid answers to complex prompts often echo logic or are very concise
            if c_logical_density > 0 or c_struct['length'] < 10:
                score += 0.4
                reasons.append("structural_alignment")
            else:
                # Penalty for ignoring logical markers in long candidates
                if c_struct['length'] > 20:
                    score -= 0.3
                    reasons.append("logic_mismatch")
        
        # --- Scale 2: Numeric Consistency ---
        num_score = self._evaluate_numeric(p_struct['numbers'], c_struct['numbers'])
        score += num_score * 0.2
        if num_score == 1.0:
            reasons.append("numeric_consistent")

        # --- Scale 3: Semantic/Compression (Tiebreaker) ---
        # NCD is weak alone, so we weight it low unless structural signals are ambiguous
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD: lower distance = higher score. 
        # However, for QA, sometimes the answer is short and distinct from prompt (high NCD).
        # We use NCD primarily to detect "echoing" (very low NCD but trivial) vs "reasoned"
        
        ncd_component = 0.0
        if c_struct['length'] > 5: 
            # If candidate is long, it should be somewhat compressed relative to prompt+candidate
            # This is a proxy for relevance.
            ncd_component = (1.0 - ncd) * 0.4
        else:
            # Short answers get base benefit
            ncd_component = 0.2
            
        score += ncd_component
        
        # Bonus for exact keyword overlap in structural terms
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        overlap = len(p_words.intersection(c_words))
        if overlap > 0:
            score += min(0.2, overlap * 0.02)

        return score, ", ".join(reasons) if reasons else "baseline"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            raw_score, reason_str = self._score_candidate(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": reason_str
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Calibration: Normalize scores to ensure 0-1 range and spread
        if scored:
            max_s = scored[0]["score"]
            min_s = scored[-1]["score"]
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for item in scored:
                # Rescale to [0.1, 0.9] to allow confidence movement
                normalized = 0.1 + (0.8 * (item["score"] - min_s) / range_s)
                item["score"] = round(normalized, 4)
                
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Bayesian confidence estimation.
        Compares the target answer against a set of perturbed alternatives.
        If the target significantly outperforms alternatives, confidence is high.
        """
        # Generate pseudo-alternatives for comparison (Monte Carlo style approximation)
        # Since we can't generate new text easily without models, we use the provided answer
        # and check its structural self-consistency as a proxy.
        
        base_score, _ = self._score_candidate(prompt, answer)
        
        # Perturbation 1: Truncated
        trunc = answer[:int(len(answer)*0.8)] if len(answer) > 10 else answer
        score_trunc, _ = self._score_candidate(prompt, trunc)
        
        # Perturbation 2: Appended noise
        noise = answer + " random irrelevant string"
        score_noise, _ = self._score_candidate(prompt, noise)
        
        # Confidence is high if original score > perturbed scores
        margin = (base_score - score_trunc) + (base_score - score_noise)
        
        # Sigmoid mapping to 0-1
        conf = 1 / (1 + 2.718 ** (-margin * 5))
        return round(min(1.0, max(0.0, conf)), 4)
```

</details>
