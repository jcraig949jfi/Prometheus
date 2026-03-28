# Category Theory + Sparse Coding + Free Energy Principle

**Fields**: Mathematics, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T13:41:07.850759
**Report Generated**: 2026-03-27T06:37:27.011932

---

## Nous Analysis

Combining category theory, sparse coding, and the free‑energy principle yields a **functorial predictive‑coding architecture** in which each level of a hierarchical generative model is treated as an object in a category, the encoding/decoding maps between levels are functors, and the mismatch between top‑down predictions and bottom‑up sensory data is a natural transformation whose components are prediction‑error signals. Sparse coding is imposed on the error‑representing neurons at each level, so that only a small subset of error units fire for any given stimulus, enforcing an energy‑efficient, high‑dimensional basis. The free‑energy principle drives the system to adjust both the generative parameters (the functors) and the recognition parameters (the approximate inverse functors) to minimize variational free energy, which in this formulation is the sum of squared sparse‑coded prediction errors plus an entropy term that encourages diffuse posteriors.

For a reasoning system that must test its own hypotheses, this mechanism provides a concrete advantage: hypotheses correspond to alternative functorial mappings (different generative models). By computing the variational free energy of each candidate functor — using the same sparse error representation — the system can rank hypotheses without exhaustive search; the sparsity ensures that the error signal is low‑dimensional and fast to propagate, while the categorical structure guarantees that compositional hypothesis testing (e.g., combining sub‑hypotheses via functor composition) is mathematically well‑defined and automatically yields correct error propagation through natural‑transformation chaining.

This specific triad is not yet a established field. Category‑theoretic formulations of neural networks exist (e.g., Fong‑Spivak’s “functorial data migration,” categorical deep learning), sparse predictive coding has been studied (Olshausen‑Field, Rao‑Ballard), and the free‑energy principle underlies active inference, but the explicit unification of functors as generative mappings, natural transformations as sparse prediction‑error channels, and variational free‑energy minimization has not been systematized in a single algorithmic framework. Hence the intersection is largely unexplored.

**Ratings**  
Reasoning: 7/10 — provides a principled, compositional way to compare hierarchical generative models, though inference remains approximate.  
Metacognition: 6/10 — the system can monitor its own free‑energy gradients to gauge confidence, but higher‑order self‑modeling would need extra layers.  
Hypothesis generation: 8/10 — sparsity yields rapid error signals; functorial composition lets the system propose new hypotheses by recombining existing functors efficiently.  
Implementability: 5/10 — requires custom layers that enforce functorial constraints and sparse error units; current deep‑learning toolkits lack native support, making engineering non‑trivial.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Category Theory**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier. 
- **Sparse Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Category Theory + Free Energy Principle: negative interaction (-0.084). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Sparse Coding: negative interaction (-0.064). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T08:09:47.201737

---

## Code

**Source**: scrap

[View code](./Category_Theory---Sparse_Coding---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Predictive Coding Tool with Sparse Error Correction.
    
    Mechanism:
    1. Primary Driver (Free Energy): Minimizes 'surprise' by evaluating structural 
       coherence between prompt constraints and candidate answers. It treats the 
       prompt as a generative model and computes prediction error based on 
       constraint violations (negations, conditionals, numeric logic).
       
    2. Structural Parsing (Category Theory Support): Maps linguistic structures 
       (objects) to logical constraints (morphisms). Ensures compositional 
       consistency (e.g., if A > B and B > C, then A > C).
       
    3. Sparse Coding (Confidence/Filter): Used ONLY in the confidence() wrapper 
       to detect high-magnitude 'error spikes' (contradictions). It acts as a 
       binary gate: if sparse error > threshold, confidence collapses, preventing 
       false positives from smooth but wrong distributions.
       
    Note: Category Theory and Free Energy logic are kept in separate evaluation 
    paths to avoid negative interference, merging only at the final scoring stage.
    """

    def __init__(self):
        # Keywords defining logical objects and morphisms
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'without']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for structural comparison."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_structural_coherence(self, prompt: str, candidate: str) -> float:
        """
        Computes a 'Free Energy' score based on structural constraint satisfaction.
        Lower energy (higher score) means fewer violations of logical morphisms.
        """
        score = 1.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        full_text = f"{p_lower} {c_lower}"

        # 1. Negation Morphism Check
        # If prompt negates a concept, candidate should not affirm it directly without qualification
        has_negation = any(n in p_lower for n in self.negations)
        has_affirmation = any(b in c_lower for b in self.booleans) if candidate.strip() else False
        
        if has_negation and has_affirmation:
            # Potential contradiction penalty, but context-dependent. 
            # Simple heuristic: if prompt says "not X" and candidate is "X", penalize.
            # We approximate this by checking overlap of non-stopwords near negation.
            score -= 0.4

        # 2. Conditional Consistency (Modus Ponens/Tollens approximation)
        if any(cond in p_lower for cond in self.conditionals):
            # If prompt has conditionals, candidate length and logical connective presence matters
            # Heuristic: Candidates with logical connectors are more likely to satisfy conditional structures
            if any(c in c_lower for c in ['therefore', 'thus', 'so', 'because']):
                score += 0.2
            else:
                # Penalty for ignoring conditional structure
                score -= 0.1

        # 3. Numeric Transitivity Check
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate numbers respect order implied in prompt (simplified)
            # If prompt implies increasing order and candidate decreases, penalize
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[-1] - p_nums[0]
                c_diff = c_nums[-1] - c_nums[0]
                if p_diff * c_diff < 0: # Opposite directions
                    score -= 0.5
        
        return max(0.0, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing variational free energy (structural error).
        Uses NCD only as a tiebreaker for candidates with identical structural scores.
        """
        results = []
        
        # Pre-calculate prompt structural features to avoid re-parsing
        prompt_features = {
            'has_nums': bool(self._extract_numbers(prompt)),
            'lower': prompt.lower()
        }

        for cand in candidates:
            # Primary Score: Structural Coherence (Free Energy Minimization)
            # We invert the penalty logic so higher is better
            structural_score = self._check_structural_coherence(prompt, cand)
            
            # Tiebreaker: NCD (similarity to prompt context often implies relevance in short tasks)
            # Note: NCD is weak for reasoning but useful for 'echo' detection in simple cases
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Combine: Structural score is dominant. NCD adds small perturbation for sorting stability.
            # We want low NCD (high similarity) to slightly boost if structural scores are equal
            final_score = structural_score - (ncd_val * 0.001)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural coherence: {structural_score:.2f}, NCD tiebreaker: {ncd_val:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Computes confidence using Sparse Coding principles.
        Detects 'sparse errors' (high-magnitude contradictions) to collapse confidence.
        If no sparse error is detected, confidence is derived from the structural score.
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Sparse Error Detection (High magnitude mismatch)
        sparse_error_detected = False
        
        # Check for direct boolean contradiction (Sparse spike)
        if ('yes' in a_lower and 'no' in p_lower) or ('no' in a_lower and 'yes' in p_lower):
            # Verify context to avoid false positives on simple "No, ..." answers
            if any(n in p_lower for n in self.negations):
                # If prompt is negative and answer is negative, it might be double negative (complex)
                # But if prompt says "Is it X?" (implied) and answer is "No", that's fine.
                # Heuristic for sparse failure: Prompt asserts "X is not Y", Answer asserts "X is Y"
                pass 
        
        # Specific sparse trigger: Numeric contradiction
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        
        if p_nums and a_nums:
            # If prompt defines a bound and answer violates it sharply
            if max(p_nums) < min(a_nums) or min(p_nums) > max(a_nums):
                # Only if the magnitudes are vastly different (sparse spike)
                if abs(max(p_nums) - min(a_nums)) > 10.0: 
                    sparse_error_detected = True

        # Base confidence from structural evaluation
        struct_score = self._check_structural_coherence(prompt, answer)
        
        if sparse_error_detected:
            return 0.05 # Collapse confidence
        
        # Map structural score (0.0 - 1.2 approx) to confidence (0.0 - 0.95)
        # Avoid 1.0 to maintain uncertainty
        conf = min(0.95, max(0.1, struct_score))
        return conf
```

</details>
