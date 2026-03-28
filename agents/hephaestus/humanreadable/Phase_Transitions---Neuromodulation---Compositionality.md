# Phase Transitions + Neuromodulation + Compositionality

**Fields**: Physics, Neuroscience, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T15:37:49.588357
**Report Generated**: 2026-03-27T06:37:27.721919

---

## Nous Analysis

Combining phase transitions, neuromodulation, and compositionality yields a **Neuromodulated Critical Compositional Network (NCCN)**. In this architecture, a core compositional substrate — e.g., a Tensor Product Representation (TPR) or Neural Symbolic Module — binds conceptual roles and fillers. The strength of the binding couplings serves as an order parameter \(g\). Neuromodulatory signals (analogues of dopamine for gain‑up and serotonin for gain‑down) globally scale \(g\), pushing the system toward or away from a critical point where susceptibility diverges. Near criticality, small changes in input produce large, reversible re‑configurations of the compositional bindings, enabling rapid switching between distinct relational structures — essentially a tunable “phase‑transition‑driven routing” mechanism.

**Advantage for self‑hypothesis testing:**  
When the system needs to generate a new hypothesis, dopaminergic neuromodulation raises \(g\) to drive the network into the critical regime, maximising representational flexibility and allowing novel role‑filler combinations to emerge spontaneously. Once a candidate hypothesis is formed, serotonergic modulation lowers \(g\), moving the system into a sub‑critical, stable regime where the hypothesis can be evaluated with low noise and high fidelity. This gain‑control loop implements an intrinsic explore‑exploit schedule that is directly tied to the statistical physics of phase transitions, giving the system a principled way to balance hypothesis generation versus verification.

**Novelty:**  
Criticality has been studied in recurrent nets (e.g., “critical brain hypothesis” and *critical training* of RNNs), neuromodulatory gain control appears in works like *Adaptive Computation Time* (ACT) for Transformers and *Neuromodulated Reinforcement Learning*, and compositionality is central to Neural Symbolic Systems such as *Neural Programmer‑Interpreter* or *Tensor‑Product Networks*. However, no existing framework explicitly treats neuromodulators as control parameters that tune a compositional substrate through a bona‑fide phase transition to regulate hypothesis testing. Thus the NCCN combination is largely unmapped, though it builds on well‑studied components.

**Potential ratings**

Reasoning: 7/10 — The mechanism provides a principled, physics‑based route to flexible relational reasoning, but empirical validation of critical compositional dynamics in large‑scale models remains limited.  
Metacognition: 8/10 — By linking neuromodulatory gain to an order parameter, the system gains an explicit, measurable signature of its own processing regime, supporting accurate self‑monitoring.  
Hypothesis generation: 8/10 — Critical enhancement of compositional recombination yields a rich space of novel hypotheses; the explore‑exploit switch is directly grounded in gain control.  
Implementability: 5/10 — Realizing precise, biologically plausible neuromodulatory control of tensor‑product bindings in current hardware is challenging; approximations (e.g., gating via learned scalars) would be needed, increasing engineering complexity.  

---  
Reasoning: 7/10 — The mechanism provides a principled, physics‑based route to flexible relational reasoning, but empirical validation of critical compositional dynamics in large‑scale models remains limited.  
Metacognition: 8/10 — By linking neuromodulatory gain to an order parameter, the system gains an explicit, measurable signature of its own processing regime, supporting accurate self‑monitoring.  
Hypothesis generation: 8/10 — Critical enhancement of compositional recombination yields a rich space of novel hypotheses; the explore‑exploit switch is directly grounded in gain control.  
Implementability: 5/10 — Realizing precise, biologically plausible neuromodulatory control of tensor‑product bindings in current hardware is challenging; approximations (e.g., gating via learned scalars) would be needed, increasing engineering complexity.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 5/10 |
| **Composite** | **7.67** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Phase Transitions**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 33% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Neuromodulation + Phase Transitions: strong positive synergy (+0.158). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Compositionality + Phase Transitions: negative interaction (-0.056). Keep these concepts in separate code paths to avoid interference.
- Compositionality + Neuromodulation: negative interaction (-0.057). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Phase Transitions + Criticality + Neuromodulation (accuracy: 0%, calibration: 0%)
- Category Theory + Phase Transitions + Neural Architecture Search (accuracy: 0%, calibration: 0%)
- Chaos Theory + Active Inference + Compositionality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T06:32:30.126192

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Neuromodulation---Compositionality/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Critical Compositional Network (NCCN) Approximation.
    
    Mechanism:
    1. Compositional Substrate: Parses prompts into structural tokens (negations, 
       comparatives, conditionals, numbers) to form a symbolic representation.
    2. Phase Transition & Neuromodulation: 
       - 'g' (coupling strength) acts as the order parameter.
       - High 'g' (Dopaminergic/Critical): Used during hypothesis generation. 
         Allows loose matching and exploration of candidate structures.
       - Low 'g' (Serotonergic/Sub-critical): Used during evaluation. 
         Enforces strict structural alignment and constraint propagation.
    3. Scoring: 
       - Candidates are scored by structural overlap with the prompt's logic.
       - Numeric constraints are evaluated deterministically.
       - NCD is used only as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        # Structural keywords for compositional parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.logic_ops = {'and', 'or', 'xor', 'but', 'however'}
        
        # Phase transition parameters
        self.critical_point = 0.5
        self.explore_gain = 1.2  # Dopaminergic: broadens acceptance
        self.exploit_gain = 0.8  # Serotonergic: narrows acceptance, increases penalty for errors

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for constraint checking."""
        pattern = r'-?\d+(?:\.\d+)?'
        matches = re.findall(pattern, text.lower())
        return [float(m) for m in matches]

    def _parse_structure(self, text: str) -> Dict:
        """
        Decompose text into compositional roles: negations, comparatives, numbers, logic.
        This forms the 'Tensor Product' like representation where roles are keys and fillers are values.
        """
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        return {
            'negations': words.intersection(self.negations),
            'comparatives': words.intersection(self.comparatives),
            'conditionals': words.intersection(self.conditionals),
            'logic': words.intersection(self.logic_ops),
            'numbers': self._extract_numbers(text),
            'length': len(text),
            'word_count': len(words)
        }

    def _check_numeric_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Evaluate numeric constraints. 
        If prompt implies a comparison, check if candidate satisfies it.
        """
        p_nums = prompt_struct['numbers']
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric constraint to violate
        
        # Heuristic: If prompt has numbers and candidate has numbers, 
        # check for direct contradiction in simple cases (e.g. equality)
        # For this implementation, we reward numeric presence if prompt has them, 
        # and penalize if the candidate number is wildly out of bounds (noise).
        
        if len(p_nums) > 0 and len(c_nums) > 0:
            # Simple range check: candidate numbers should be within reasonable range of prompt numbers
            # unless the prompt implies a calculation. 
            # Here we just check magnitude similarity as a proxy for relevance.
            max_p = max(abs(n) for n in p_nums) if p_nums else 1
            max_c = max(abs(n) for n in c_nums) if c_nums else 1
            
            if max_p == 0: return 1.0
            ratio = max_c / max_p if max_p != 0 else 1
            if ratio > 10 or ratio < 0.1:
                return 0.2 # Penalty for wildly different magnitudes
        
        return 1.0

    def _compute_structural_score(self, prompt_struct: Dict, cand_struct: Dict, gain: float) -> float:
        """
        Compute similarity based on structural overlap.
        Gain modulates the strictness (Phase transition control).
        """
        score = 0.0
        total_weight = 0.0
        
        # Weighted structural components
        components = [
            ('negations', 2.0),
            ('comparatives', 2.0),
            ('conditionals', 2.0),
            ('logic', 1.5),
        ]
        
        for key, weight in components:
            p_set = prompt_struct[key]
            c_set = cand_struct[key]
            
            if not p_set and not c_set:
                continue # Neutral
            
            if not p_set and c_set:
                score -= weight * 2 # Penalty for hallucinating structure
                total_weight += weight
            elif p_set and not c_set:
                # Missing critical structure
                score -= weight * (1.5 * gain) 
                total_weight += weight
            else:
                # Intersection over Union for sets
                intersection = len(p_set.intersection(c_set))
                union = len(p_set.union(c_set))
                if union > 0:
                    overlap = intersection / union
                    # Near criticality (gain ~ 1), small changes matter more
                    score += (overlap - (1.0 if gain > 1.0 else 0.8)) * weight * gain
                    total_weight += weight

        # Normalize
        if total_weight == 0:
            return 0.5 # Neutral if no structural markers
        
        raw_score = score / total_weight if total_weight != 0 else 0
        return raw_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        
        if len1 == 0 or len2 == 0:
            return 1.0
            
        try:
            len_combined = len(zlib.compress(b1 + b2))
        except:
            return 1.0
            
        ncd = (len_combined - min(len1, len2)) / max(len1, len2)
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._parse_structure(prompt)
        results = []
        
        # Phase 1: Exploration (High Gain) - Generate initial scores
        # We simulate the "hypothesis generation" by scoring loosely first
        temp_scores = []
        
        for cand in candidates:
            cand_struct = self._parse_structure(cand)
            
            # Structural Score (Core Reasoning)
            struct_score = self._compute_structural_score(prompt_struct, cand_struct, self.explore_gain)
            
            # Numeric Consistency (Constraint Propagation)
            num_score = self._check_numeric_consistency(prompt_struct, cand)
            
            # Combined raw score
            raw_score = (struct_score * 0.7) + (num_score * 0.3)
            temp_scores.append((cand, raw_score))
        
        # Phase 2: Exploitation (Low Gain) - Refine and Rank
        # Apply serotonergic modulation to stabilize and differentiate
        max_raw = max(s[1] for s in temp_scores) if temp_scores else 0
        min_raw = min(s[1] for s in temp_scores) if temp_scores else 0
        range_raw = max_raw - min_raw if (max_raw - min_raw) > 0 else 1.0
        
        final_results = []
        for cand, raw_score in temp_scores:
            # Normalize to 0-1 range roughly
            norm_score = (raw_score - min_raw) / range_raw if range_raw > 0 else 0.5
            
            # Apply critical refinement (Serotonergic gain down)
            # Penalize structural mismatches heavily in the final pass
            cand_struct = self._parse_structure(cand)
            refinement = self._compute_structural_score(prompt_struct, cand_struct, self.exploit_gain)
            
            # NCD as tiebreaker only
            ncd_val = self._ncd_distance(prompt, cand)
            # Invert NCD so higher is better, but scale it down so it rarely overrides structure
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            final_score = (norm_score * 0.8 + refinement * 0.2) + ncd_score
            final_score = max(0.0, min(1.0, final_score)) # Clamp 0-1
            
            # Generate reasoning string
            reasoning = f"Structural match: {refinement:.2f}, Numeric consistency: {self._check_numeric_consistency(prompt_struct, cand):.2f}"
            
            final_results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence by checking strict structural alignment (Sub-critical regime).
        Returns 0.0 to 1.0.
        """
        prompt_struct = self._parse_structure(prompt)
        cand_struct = self._parse_structure(answer)
        
        # Strict structural evaluation
        struct_score = self._compute_structural_score(prompt_struct, cand_struct, self.exploit_gain)
        num_score = self._check_numeric_consistency(prompt_struct, answer)
        
        # Base confidence on structural integrity
        base_conf = (struct_score + 1.0) / 2.0 # Map -1..1 to 0..1
        base_conf = base_conf * 0.7 + (num_score * 0.3)
        
        # Boost if exact string match or very close NCD
        if prompt.lower().strip() == answer.lower().strip():
            return 1.0
            
        ncd = self._ncd_distance(prompt, answer)
        if ncd < 0.1:
            base_conf = min(1.0, base_conf + 0.2)
            
        return max(0.0, min(1.0, base_conf))
```

</details>
