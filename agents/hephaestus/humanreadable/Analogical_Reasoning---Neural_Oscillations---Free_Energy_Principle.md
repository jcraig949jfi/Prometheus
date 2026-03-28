# Analogical Reasoning + Neural Oscillations + Free Energy Principle

**Fields**: Cognitive Science, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:09:49.857781
**Report Generated**: 2026-03-27T06:37:29.302359

---

## Nous Analysis

Combining analogical reasoning, neural oscillations, and the free‑energy principle yields a **hierarchical predictive‑coding architecture in which cross‑frequency oscillatory coupling implements structure‑mapping and prediction‑error minimization drives analogical inference**. Concretely, imagine a deep predictive‑coding network (e.g., a variational auto‑encoder with layered Gaussian beliefs) where each layer emits rhythmic activity: low‑frequency theta (4‑8 Hz) encodes abstract relational schemas, mid‑frequency beta (15‑30 Hz) carries propositional bindings, and high‑frequency gamma (30‑80 Hz) synchronizes feature‑level details. Analogical mapping occurs when theta phases in a source domain align with theta phases in a target domain, allowing gamma‑mediated feature patterns to be bound via cross‑frequency phase‑locking (theta‑gamma coupling). The free‑energy principle governs each layer: variational free energy is minimized by updating predictions to reduce prediction error, which in turn adjusts the strength of oscillatory coupling (e.g., via synaptic plasticity rules that depend on phase‑coherence).  

**Advantage for hypothesis testing:** The system can generate an analogical hypothesis by momentarily entraining source‑domain theta to target‑domain theta, propagating the mapped structure upward. Prediction error then quantifies the mismatch between the predicted analogical output and observed data; a rapid drop in error signals a successful hypothesis, allowing the system to self‑evaluate without external labels. This provides an intrinsic, online metric for hypothesis validation that is tightly coupled to the neural substrate’s dynamics.  

**Novelty:** Predictive coding with neural oscillations is well studied (e.g., Fries’ communication‑through‑coherence, Bastos et al.’s laminar predictive coding), and analogical reasoning has been explored in neural‑symbolic models (e.g., Deep Analogical Reasoning, Neural Symbolic Machines). However, the explicit use of cross‑frequency phase alignment as the binding mechanism for structure mapping, jointly optimized by variational free‑energy minimization, has not been formalized as a unified algorithm. Thus the combination is moderately novel, extending existing frameworks rather than reproducing a known technique.  

**Ratings**  
Reasoning: 7/10 — captures relational transfer via oscillatory binding but still relies on hand‑crafted hierarchical priors.  
Metacognition: 8/10 — prediction‑error minimization supplies an intrinsic self‑monitoring signal for hypothesis quality.  
Hypothesis generation: 7/10 — phase‑alignment enables rapid analogical proposal; limited by the need for precise oscillatory control.  
Implementability: 5/10 — requires biologically plausible oscillatory dynamics and precise cross‑frequency coupling, which are challenging to engineer in current deep‑learning hardware.

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

- **Analogical Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Analogical Reasoning + Neural Oscillations: strong positive synergy (+0.207). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Analogical Reasoning + Free Energy Principle: strong positive synergy (+0.320). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neural Oscillations: strong positive synergy (+0.271). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 33% | +13% |
| Calibration | 40% | +33% |

**Forge Timestamp**: 2026-03-26T03:20:14.713178

---

## Code

**Source**: forge

[View code](./Analogical_Reasoning---Neural_Oscillations---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical predictive-coding architecture inspired by the
    Free Energy Principle (FEP) and Neural Oscillations for analogical reasoning.
    
    Mechanism:
    1. Structural Parsing (Gamma/Beta layers): Extracts logical constraints 
       (negations, comparatives, conditionals) as high-frequency features.
    2. Analogous Mapping (Theta layer): Uses Normalized Compression Distance (NCD)
       to measure structural similarity between the prompt's logical skeleton and 
       the candidate's skeleton, acting as the "phase alignment" metric.
    3. Free Energy Minimization (Evaluation): 
       - Prediction: The candidate should structurally mirror the prompt's constraints.
       - Error: Deviation from expected logical forms (e.g., double negation failure).
       - Score: Inverse of variational free energy (minimizing error + complexity).
    
    This prioritizes structural logic over semantic overlap, beating pure NCD baselines.
    """

    def __init__(self):
        # Logical operators as "oscillatory anchors" for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most']

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer converting to lowercase and splitting by non-alphanumeric."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """
        Extracts high-frequency logical features (Gamma/Beta bands).
        Returns a dictionary representing the structural schema.
        """
        lower_text = text.lower()
        tokens = self._tokenize(text)
        
        has_neg = any(n in lower_text for n in self.negations)
        has_comp = any(c in lower_text for c in self.comparatives)
        has_cond = any(c in lower_text for c in self.conditionals)
        has_quant = any(q in lower_text for q in self.quantifiers)
        
        # Extract numeric values for comparison logic
        numbers = re.findall(r'\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers]
        
        # Structural signature vector
        return {
            'neg_count': sum(lower_text.count(n) for n in self.negations),
            'comp_count': sum(lower_text.count(c) for c in self.comparatives),
            'cond_count': sum(lower_text.count(c) for c in self.conditionals),
            'has_numbers': len(nums) > 0,
            'numbers': nums,
            'length': len(tokens),
            'unique_ratio': len(set(tokens)) / max(1, len(tokens))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def _compute_structural_error(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculates prediction error based on structural mismatch.
        Low error = high structural alignment (Analogous mapping).
        """
        error = 0.0
        
        # Constraint 1: Negation consistency (Modus Tollens check proxy)
        # If prompt has negation, valid reasoning often requires tracking it.
        # We penalize large deviations in negation density unless both are zero.
        if prompt_struct['neg_count'] > 0:
            if cand_struct['neg_count'] == 0:
                error += 0.5  # Potential failure to carry over logical constraint
        elif cand_struct['neg_count'] > 2:
            error += 0.3  # Spurious negation introduces noise

        # Constraint 2: Conditional/Comparative presence
        # Reasoning candidates often mirror the logical operators of the prompt
        if prompt_struct['cond_count'] > 0:
            if cand_struct['cond_count'] == 0:
                error += 0.2
        if prompt_struct['comp_count'] > 0:
            if cand_struct['comp_count'] == 0:
                error += 0.2

        # Constraint 3: Numeric consistency
        if prompt_struct['has_numbers'] and cand_struct['has_numbers']:
            # Check if candidate numbers are wildly different scale (heuristic)
            p_max = max(prompt_struct['numbers']) if prompt_struct['numbers'] else 0
            c_max = max(cand_struct['numbers']) if cand_struct['numbers'] else 0
            if p_max > 0 and c_max > 0:
                ratio = abs(math.log(p_max + 1) - math.log(c_max + 1))
                if ratio > 2.0: # Log scale difference
                    error += 0.3
        
        return error

    def _free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy approximation.
        F = Prediction_Error + Complexity_Penalty
        Here, Prediction Error is derived from structural mismatch and NCD.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Structural Prediction Error (Theta-Gamma coupling mismatch)
        struct_error = self._compute_structural_error(p_struct, c_struct)
        
        # 2. Analogous Mapping via NCD (Phase alignment)
        # We compare the *structural skeleton* strings to reduce semantic noise
        # Construct a skeleton string for NCD to focus on logic tokens
        def get_skeleton(text):
            t = text.lower()
            skel = []
            for word in self.negations + self.comparatives + self.conditionals + self.quantifiers:
                if word in t:
                    skel.append(word)
            return " ".join(skel)
            
        p_skel = get_skeleton(prompt)
        c_skel = get_skeleton(candidate)
        
        # If skeletons exist, measure their distance. If empty, rely on struct error.
        ncd_val = 0.0
        if p_skel and c_skel:
            ncd_val = self._compute_ncd(p_skel, c_skel)
        elif not p_skel and not c_skel:
            # Both lack specific logic tokens, neutral
            ncd_val = 0.5 
        else:
            # One has logic, other doesn't -> High error
            ncd_val = 1.0

        # Weighted combination representing Free Energy
        # Lower is better. 
        # We weight structural error heavily as it captures the "Reasoning" aspect.
        total_error = (0.6 * struct_error) + (0.4 * ncd_val)
        
        # Complexity penalty (length mismatch penalty)
        len_diff = abs(p_struct['length'] - c_struct['length']) / max(1, p_struct['length'])
        complexity = 0.1 * len_diff
        
        return total_error + complexity

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing Free Energy (maximizing structural coherence).
        Returns sorted list of dicts with candidate, score, and reasoning.
        """
        scored = []
        min_energy = float('inf')
        energies = []

        # First pass: calculate energy for all to find min for normalization
        for cand in candidates:
            e = self._free_energy(prompt, cand)
            energies.append(e)
            if e < min_energy:
                min_energy = e

        # Second pass: normalize and generate reasoning
        for i, cand in enumerate(candidates):
            energy = energies[i]
            # Convert energy to score (0-1), where 1 is best (lowest energy)
            # Using exp(-energy) to map to probability-like space
            score = math.exp(-energy)
            
            # Generate reasoning string based on dominant factor
            p_struct = self._extract_structure(prompt)
            c_struct = self._extract_structure(cand)
            reasons = []
            if p_struct['neg_count'] > 0 and c_struct['neg_count'] == 0:
                reasons.append("Missing negation tracking")
            if p_struct['comp_count'] > 0 and c_struct['comp_count'] == 0:
                reasons.append("Missing comparative logic")
            if not reasons:
                reasons.append("Structural alignment maintained")
                
            scored.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Free Energy: {energy:.2f}. {'; '.join(reasons)}"
            })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence (0-1) based on the inverse of Free Energy.
        """
        energy = self._free_energy(prompt, answer)
        conf = math.exp(-energy)
        return round(min(1.0, max(0.0, conf)), 4)
```

</details>
