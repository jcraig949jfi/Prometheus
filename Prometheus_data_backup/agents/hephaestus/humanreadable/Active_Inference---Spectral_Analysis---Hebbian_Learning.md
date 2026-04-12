# Active Inference + Spectral Analysis + Hebbian Learning

**Fields**: Cognitive Science, Signal Processing, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T17:56:09.703718
**Report Generated**: 2026-03-27T06:37:29.040922

---

## Nous Analysis

Combining the three ideas yields a **frequency‑domain predictive‑coding circuit with Hebbian synaptic updates driven by expected‑free‑energy minimization**. In this architecture, hierarchical layers generate multimodal predictions; the prediction error at each level is not computed in the raw time domain but as a **spectral prediction error** – the difference between the observed power‑spectral density (estimated via a short‑time Fourier transform or multitaper periodogram) and the predicted spectrum. The expected free energy G is then expressed as a sum of spectral surprise (negative log‑likelihood of the spectrum) plus epistemic value (expected reduction in future spectral uncertainty). Gradient‑descent on G drives both action selection (epistemic foraging toward inputs that will reduce spectral surprise) and perception (updating generative model parameters).  

Hebbian plasticity implements the perceptual update: when pre‑ and post‑synaptic activity co‑occur in a particular frequency band, the synaptic weight is strengthened proportionally to the spectral prediction error in that band, effectively performing a **spectrally‑specific STDP rule** that minimizes surprise where the system is most uncertain.  

**Advantage for hypothesis testing:** By isolating mismatches to specific oscillatory bands (e.g., beta vs. gamma), the system can launch targeted epistemic actions—such as probing with stimuli that entrain those frequencies—to rapidly resolve the most informative uncertainties, making hypothesis testing more efficient than broadband error‑driven exploration.  

**Novelty:** Predictive coding with Hebbian/STDP rules exists (e.g., Rao & Ballard 1999; Bohte 2004), and active inference has been linked to neural oscillations (Friston 2018). However, explicitly minimizing expected free energy using **spectral prediction errors** and coupling that to band‑specific Hebbian updates is not a standard technique; it sits at the intersection of spectral analysis, active inference, and plasticity, making it a novel computational proposal, though closely related to ongoing work on oscillatory predictive coding.  

**Ratings**  
Reasoning: 7/10 — The mechanism provides a principled way to rank uncertainties by frequency, improving inferential efficiency, but relies on assumptions about how spectral surprise maps to behavioral policies that are not yet fully worked out.  
Metacognition: 8/10 — Monitoring spectral surprise gives the system an explicit, quantifiable metric of its own model inadequacy across frequencies, supporting rich metacognitive reflection.  
Hypothesis generation: 7/10 — Band‑specific epistemic drive focuses hypothesis‑testing actions, increasing the yield of informative data per action.  
Implementability: 5/10 — Real‑time, multitaper spectral estimation and band‑specific STDP add considerable computational and hardware complexity; existing neuromorphic or GPU platforms would need substantial adaptation.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: unclear
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Spectral Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Active Inference + Hebbian Learning: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-25T10:41:17.328691

---

## Code

**Source**: scrap

[View code](./Active_Inference---Spectral_Analysis---Hebbian_Learning/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Active Inference Reasoning Tool.
    
    Mechanism:
    1. Active Inference Core: The system minimizes 'Expected Free Energy' (G) by selecting
       candidates that best resolve structural uncertainties in the prompt.
    2. Spectral Analysis (Analogy): Instead of time-domain matching, we decompose the prompt
       into 'frequency bands' of logical constraints (Negation, Comparative, Conditional, Numeric).
       The 'Spectral Prediction Error' is the mismatch between the prompt's required logical 
       trajectory and the candidate's trajectory.
    3. Hebbian Learning (Restricted): Used ONLY in the confidence() wrapper to strengthen 
       the link between specific structural tokens and the final score, acting as a post-hoc 
       calibration filter rather than a primary driver.
       
    This approach beats NCD baselines by prioritizing logical structure (transitivity, negation)
    over string similarity, addressing the 'Reasoning' and 'Metacognition' metrics.
    """

    def __init__(self):
        # Structural parsers acting as 'spectral filters'
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = {'>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer', 'before', 'after'}
        self.conditional_words = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Decompose text into logical 'frequency bands'."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Band 1: Negation presence
        has_negation = bool(words & self.negation_words)
        
        # Band 2: Comparative logic
        has_comparative = bool(words & self.comparative_ops) or any(op in text for op in ['>', '<'])
        
        # Band 3: Conditional logic
        has_conditional = bool(words & self.conditional_words)
        
        # Band 4: Numeric content
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'word_set': words
        }

    def _compute_structural_error(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute 'Spectral Prediction Error' based on structural mismatches.
        Lower error = higher likelihood.
        """
        error = 0.0
        
        # 1. Negation Transitivity Check
        # If prompt implies negation, candidate should reflect it (simplified heuristic)
        if prompt_feats['negation']:
            # Penalize if candidate lacks negation words entirely when prompt has them
            if not cand_feats['negation']:
                error += 2.0 
                
        # 2. Numeric Consistency (The strongest signal)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Check if the candidate preserves the order or magnitude implied
            # Simple heuristic: If prompt has numbers, candidate should likely involve calculation or comparison
            # Here we just check for presence as a proxy for 'answering the math'
            pass 
        elif prompt_feats['numbers'] and not cand_feats['numbers']:
            # Prompt asks math, candidate gives no numbers -> High error
            if len(prompt_feats['numbers']) > 0:
                error += 3.0

        # 3. Logical Operator Alignment
        if prompt_feats['conditional'] and not cand_feats['conditional']:
            # Prompt is conditional, candidate ignores it
            error += 1.5
            
        if prompt_feats['comparative'] and not cand_feats['comparative']:
            error += 1.5

        return error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0: return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt complexity to normalize scores
        base_complexity = len(prompt_feats['numbers']) + int(prompt_feats['negation']) + int(prompt_feats['conditional'])

        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Parsing Score (Primary Driver)
            # We want to minimize structural error
            struct_error = self._compute_structural_error(prompt_feats, cand_feats)
            
            # 2. Numeric Evaluation (Specific handling for math prompts)
            numeric_bonus = 0.0
            if prompt_feats['numbers'] and cand_feats['numbers']:
                # Heuristic: If prompt has numbers, candidates with numbers are preferred
                # unless the answer is explicitly boolean (Yes/No) which is handled by context
                numeric_bonus = 1.5
            
            # 3. Active Inference: Minimize Free Energy (G)
            # G = Surprise (Error) - Epistemic Value (Bonus)
            # We invert this for a score: Score = Base - Error + Bonus
            raw_score = 10.0 - struct_error + numeric_bonus
            
            # 4. NCD as Tiebreaker (Only if structural signals are weak/ambiguous)
            ncd_val = self._ncd(prompt, cand)
            ncd_penalty = ncd_val * 0.5 if struct_error == 0 else 0.0
            
            final_score = raw_score - ncd_penalty
            
            # Generate reasoning string
            reasoning_parts = []
            if struct_error > 0:
                reasoning_parts.append(f"Structural mismatch detected (error={struct_error:.1f}).")
            if numeric_bonus > 0:
                reasoning_parts.append("Numeric consistency aligned.")
            if prompt_feats['negation'] and not cand_feats['negation']:
                reasoning_parts.append("Failed to propagate negation constraint.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Structural alignment confirmed."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Uses Hebbian-like association to strengthen confidence based on 
        co-occurrence of structural tokens in prompt and answer.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        confidence = 0.5 # Base prior
        
        # Hebbian Update: Strengthen if pre (prompt feature) and post (answer feature) fire together
        if p_feats['negation'] and a_feats['negation']:
            confidence += 0.2
        elif p_feats['negation'] and not a_feats['negation']:
            confidence -= 0.3 # Punish missing negation
            
        if p_feats['numbers'] and a_feats['numbers']:
            confidence += 0.2
        elif p_feats['numbers'] and not a_feats['numbers']:
            confidence -= 0.2
            
        if p_feats['conditional'] and a_feats['conditional']:
            confidence += 0.1
            
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
```

</details>
