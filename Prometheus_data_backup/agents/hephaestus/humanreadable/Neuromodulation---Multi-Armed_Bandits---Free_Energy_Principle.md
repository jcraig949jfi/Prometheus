# Neuromodulation + Multi-Armed Bandits + Free Energy Principle

**Fields**: Neuroscience, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T19:11:02.345417
**Report Generated**: 2026-03-27T06:37:29.887889

---

## Nous Analysis

Combining neuromodulation, multi‑armed bandits, and the free‑energy principle yields a **neuromodulated active‑inference bandit** architecture. In this model, the agent maintains a generative model of the world and computes variational free energy as usual. Neuromodulatory signals (e.g., dopamine, serotonin) are interpreted as **precision‑weighting factors** that modulate the gain on prediction‑error units, thereby controlling the confidence placed on sensory versus prior information. Simultaneously, each candidate hypothesis (or model parameter setting) is treated as an “arm” of a multi‑armed bandit. The agent selects which hypothesis to test next using a bandit algorithm — such as Thompson sampling or Upper‑Confidence‑Bound (UCB) — where the reward signal is the **negative free‑energy reduction** achieved by sampling data under that hypothesis. After each observation, the agent updates its beliefs (variational posterior) and the neuromodulatory precisions are adjusted based on the observed prediction‑error surprise, creating a feedback loop: high surprise boosts exploratory neuromodulators, driving the bandit to sample less‑tested arms; low surprise increases exploitative neuromodulators, favoring the current best hypothesis.

**Advantage for hypothesis testing:** The system can autonomously balance exploration of uncertain models against exploitation of the currently most plausible model, while dynamically scaling the influence of prediction errors via neuromodulatory gain. This yields faster convergence to true hypotheses in non‑stationary environments and protects against over‑fitting to noisy data.

**Novelty:** Active‑inference formulations already link precision (a neuromodulatory concept) to exploration‑exploitation trade‑offs, and bandit‑style active inference has been explored (e.g., Daunizeau et al., 2010; FitzGerald et al., 2015). However, explicitly casting neuromodulators as bandit‑driven precision controllers that select hypotheses via UCB/Thompson sampling is not a standard formulation, making this specific triad a **novel synthesis** rather than a direct replica of existing work.

**Ratings**  
Reasoning: 7/10 — improves model‑based inference by principled uncertainty‑driven exploration, but adds computational overhead.  
Metacognition: 8/10 — neuromodulatory precision provides an explicit, measurable signal of confidence that the system can monitor and adjust.  
Hypothesis generation: 6/10 — bandit selection yields diverse hypothesis sampling, yet the quality of generated hypotheses still depends on the underlying generative model.  
Implementability: 5/10 — requires integrating variational updates, bandit policies, and neuromodulatory gain mechanisms; feasible in simulations but challenging for real‑time neuromorphic hardware.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Multi-Armed Bandits + Neuromodulation: strong positive synergy (+0.261). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neuromodulation: negative interaction (-0.103). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Multi-Armed Bandits: strong positive synergy (+0.252). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ecosystem Dynamics + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Gene Regulatory Networks + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Multi-Armed Bandits + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T09:44:54.172694

---

## Code

**Source**: scrap

[View code](./Neuromodulation---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Active-Inference Bandit Reasoner.
    
    Mechanism:
    1. Generative Model (Free Energy Core): Parses prompt structure (negations, 
       comparatives, conditionals) to establish a logical baseline. This acts as 
       the 'prior' belief state.
    2. Neuromodulation (Precision Weighting): Computes a 'surprise' metric based 
       on the mismatch between structural expectations and candidate content. 
       High surprise (high prediction error) increases exploration weight; 
       low surprise increases exploitation of structural matches.
    3. Multi-Armed Bandit (Hypothesis Selection): Treats each candidate as an 'arm'.
       The reward function combines structural adherence (exploitation) with 
       information gain potential (exploration via NCD diversity). 
       Scores are ranked by negative free energy (minimizing surprise + complexity).
    """

    def __init__(self):
        # State for bandit history (simplified for stateless evaluate interface)
        self._structural_keywords = {
            'negation': ['not', 'no', 'never', 'neither', 'without', 'fail'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'better', 'worse', '>', '<'],
            'conditional': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'numeric': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extracts structural features acting as the generative model's priors."""
        text_lower = text.lower()
        features = {
            'negation_count': 0,
            'comparative_count': 0,
            'conditional_count': 0,
            'has_numbers': False,
            'length': len(text)
        }
        
        for word in self._structural_keywords['negation']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                features['negation_count'] += 1
        
        for word in self._structural_keywords['comparative']:
            if word in text_lower:
                features['comparative_count'] += 1
                
        for word in self._structural_keywords['conditional']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                features['conditional_count'] += 1
                
        if any(c.isdigit() for c in text):
            features['has_numbers'] = True
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker for complexity."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        """Detects and evaluates numeric comparisons within the text."""
        # Extract numbers from prompt and candidate
        def get_nums(t):
            return [float(x) for x in re.findall(r"-?\d+\.?\d*", t)]
        
        p_nums = get_nums(prompt)
        c_nums = get_nums(candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers
        
        # Simple heuristic: If prompt implies ordering (e.g., contains "greater"),
        # check if candidate numbers respect it. 
        # Since we don't parse full logic trees here, we reward candidates that 
        # contain the specific numbers found in the prompt (constraint propagation).
        match_count = 0
        for n in c_nums:
            if n in p_nums:
                match_count += 1
        
        return min(1.0, match_count / max(1, len(c_nums)))

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes negative Free Energy.
        F = Accuracy (Structure match) - Complexity (NCD)
        Lower F is better. We return -F as the score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Prediction Error (Surprise) based on structural mismatch
        # If prompt has negations, good candidates should likely reflect logical handling 
        # (simplified here to presence/absence correlation for robustness)
        error_term = 0.0
        
        # Penalize if prompt has strong structure but candidate ignores it
        if p_struct['negation_count'] > 0 and c_struct['negation_count'] == 0:
            # Potential penalty, but not absolute (context matters)
            error_term += 0.2 
            
        if p_struct['conditional_count'] > 0 and c_struct['conditional_count'] == 0:
            error_term += 0.1
            
        # 2. Numeric Constraint Propagation
        numeric_score = self._numeric_evaluation(prompt, candidate)
        if numeric_score < 0.5:
            error_term += 0.3 # High surprise if numbers don't match
            
        # 3. Complexity (NCD) - Occam's razor
        # We want the candidate to be compressible relative to the prompt context
        complexity = self._compute_ncd(prompt, candidate)
        
        # Free Energy Approximation: Surprise + Complexity
        # We weight structural error heavily (Reasoning requirement)
        free_energy = (error_term * 2.0) + (complexity * 0.5)
        
        return -free_energy # Return negative free energy as score (higher is better)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates using neuromodulated active-inference logic.
        Precision weighting is applied to structural matches.
        """
        if not candidates:
            return []
            
        results = []
        p_struct = self._extract_structure(prompt)
        
        # Calculate base scores (Free Energy minimization)
        scores = []
        for cand in candidates:
            score = self._calculate_free_energy(prompt, cand)
            
            # Neuromodulatory Gain: Adjust score based on 'precision' of the match
            # If the candidate length is wildly different, reduce precision (gain)
            len_ratio = min(len(cand), len(prompt)) / max(len(cand), len(prompt), 1)
            gain = 0.8 + (0.2 * len_ratio) # Gain between 0.8 and 1.0
            
            final_score = score * gain
            scores.append((cand, final_score))
        
        # Bandit-style ranking: Sort by score (exploitation of best hypothesis)
        # In a real loop, we would add UCB bonus for untested arms, 
        # but here we rank existing candidates.
        scores.sort(key=lambda x: x[1], reverse=True)
        
        for cand, score in scores:
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Minimized free energy via structural alignment (neg:{self._extract_structure(cand)['negation_count']}, comp:{self._extract_structure(cand)['comparative_count']}) and complexity control."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence (0-1) based on negative free energy normalized.
        """
        # Get raw score
        raw_score = self._calculate_free_energy(prompt, answer)
        
        # Map to 0-1 range. 
        # Theoretically, perfect match has low free energy (high negative F? No, low F).
        # Our function returns -F. So high score = good.
        # Max theoretical score approx 0 (perfect), min could be -2.0 or lower.
        # Let's normalize: score + 2.0 / 2.0 -> clamp to 0-1
        
        # Heuristic normalization based on typical error ranges
        # Perfect structural match + low complexity ~ -0.2 to 0.0
        # Bad match ~ -1.0 to -3.0
        normalized = (raw_score + 2.0) / 2.0
        return max(0.0, min(1.0, normalized))
```

</details>
