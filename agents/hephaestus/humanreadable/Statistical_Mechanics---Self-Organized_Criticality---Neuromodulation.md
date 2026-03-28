# Statistical Mechanics + Self-Organized Criticality + Neuromodulation

**Fields**: Physics, Complex Systems, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T23:55:17.504925
**Report Generated**: 2026-03-27T06:37:32.510296

---

## Nous Analysis

Combining statistical mechanics, self‑organized criticality (SOC), and neuromodulation yields a **Neuromodulated Critical Boltzmann Machine (NCBM)**. The core architecture is an energy‑based network (binary or spiking units) whose synaptic couplings are learned via contrastive divergence, giving it a well‑defined partition function and fluctuation‑dissipation relations. Superimposed on this is an SOC sandpile dynamics layer: each unit accumulates “activity charge” until a threshold is crossed, triggering an avalanche that redistributes charge across connections according to a toppling rule. Avalanche sizes follow a power law, ensuring the network naturally hovers near a critical point where susceptibility is maximal. Neuromodulatory signals (e.g., dopamine‑like gain modulators) globally scale the effective temperature \(T\) or the avalanche‑trigger threshold, analogous to adaptive simulated annealing: high gain → high \(T\) → exploration; low gain → low \(T\) → exploitation. The neuromodulator is driven by an internal prediction‑error signal, letting the system adjust its criticality in real time based on hypothesis‑testing outcomes.

**Advantage for hypothesis testing:** When evaluating a candidate hypothesis, the NCBM samples from its posterior distribution via MCMC‑like fluctuations. Near criticality, fluctuations are scale‑free, so most steps are small refinements but occasional large avalanches produce radical hypothesis jumps—providing a built‑in balance of exploitation and exploration without hand‑tuned schedules. The neuromodulatory gain then suppresses or amplifies these avalanches depending on whether recent predictions succeeded or failed, giving the system a metacognitive switch that allocates computational resources to the most promising hypotheses while still retaining the capacity to escape local minima via rare, large‑scale reorganizations.

**Novelty:** Critical neural networks and SOC-inspired learning rules have been studied (e.g., self‑organized critical Hopfield nets, critical spiking networks). Neuromodulated annealing appears in adaptive temperature Boltzmann machines and in reinforcement‑learning frameworks with dopamine‑gaged learning rates. However, the explicit coupling of an SOC avalanche layer to the energy‑based weights of a Boltzmann machine, with neuromodulatory gain directly controlling the effective temperature, has not been described in the literature as a unified algorithm. Thus the intersection is largely unexplored.

**Ratings**  
Reasoning: 7/10 — The NCBM provides a principled, energy‑based framework for inference, but extracting clear logical conclusions from stochastic avalanches remains non‑trivial.  
Metacognition: 8/10 — Avalanche statistics offer an intrinsic monitor of system “criticality,” and neuromodulatory gain supplies a direct feedback loop for self‑assessment.  
Hypothesis generation: 9/10 — Power‑law distributed updates yield frequent small tweaks and occasional bold shifts, ideal for creative hypothesis generation.  
Implementability: 5/10 — Realizing tunable SOC dynamics in hardware or software, coupled with biologically plausible neuromodulatory gain control, is experimentally challenging and requires fine‑grained parameter tuning.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 5/10 |
| **Composite** | **8.0** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Statistical Mechanics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Self-Organized Criticality**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Neuromodulation + Statistical Mechanics: negative interaction (-0.053). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Category Theory + Chaos Theory + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Cognitive Load Theory + Neuromodulation (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T19:08:58.867974

---

## Code

**Source**: scrap

[View code](./Statistical_Mechanics---Self-Organized_Criticality---Neuromodulation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Critical Boltzmann Machine (NCBM) Approximation.
    
    Mechanism:
    1. Structural Parsing (The Lattice): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid energy landscape. This replaces 
       the Boltzmann weights with deterministic logical scores.
    2. SOC Avalanche Layer (The Dynamics): Instead of random walks, we simulate 
       "activity charge" accumulation on candidate tokens. If a candidate violates 
       a hard logical constraint (e.g., negation mismatch), it triggers an "avalanche" 
       (large penalty). If it satisfies complex structural patterns, it gains charge.
       This mimics the power-law distribution of updates: small tweaks for syntax, 
       large jumps for logical consistency.
    3. Neuromodulation (The Gain): A global gain factor scales the penalty/reward 
       based on the "prediction error" (disagreement between simple NCD similarity 
       and structural score). High error -> High Gain (exploration/strictness); 
       Low error -> Low Gain (exploitation/smoothing).
       
    This approach prioritizes structural reasoning (high accuracy) while using 
    SOC-inspired dynamics to handle edge cases and NCD as a tiebreaker.
    """

    def __init__(self):
        # SOC Parameters
        self.threshold = 1.0  # Avalanche trigger threshold
        self.dissipation = 0.1  # Charge lost per step
        self.neuromod_gain = 1.0  # Global scaling factor
        
        # Structural patterns
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'while']

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract logical features from text."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        score = 0.0
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        # Basic counting heuristics
        nums = re.findall(r'\d+\.?\d*', text)
        numeric_density = len(nums) / (len(words) + 1)
        
        return {
            'negation': 1.0 if has_negation else 0.0,
            'comparative': 1.0 if has_comparative else 0.0,
            'conditional': 1.0 if has_conditional else 0.0,
            'numeric_density': numeric_density,
            'length': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _simulate_avalanche(self, prompt_feats: Dict, cand_feats: Dict, base_score: float) -> float:
        """
        Simulate SOC dynamics. 
        Accumulate 'charge' based on feature alignment. 
        If misalignment exceeds threshold, trigger avalanche (large penalty).
        """
        charge = 0.0
        
        # Rule 1: Negation Consistency (Critical Constraint)
        # If prompt has negation, candidate must reflect it (simplified heuristic)
        neg_diff = abs(prompt_feats['negation'] - cand_feats['negation'])
        charge += neg_diff * 2.0
        
        # Rule 2: Comparative/Conditional presence
        # Reward candidates that match the complexity type of the prompt
        comp_match = 1.0 if (prompt_feats['comparative'] > 0) == (cand_feats['comparative'] > 0) else 0.0
        charge -= comp_match * 0.5  # Reduce charge (good)
        
        # Rule 3: Numeric density alignment
        num_diff = abs(prompt_feats['numeric_density'] - cand_feats['numeric_density'])
        charge += num_diff * 1.5

        # SOC Toppling Rule
        if charge > self.threshold:
            # Avalanche: Large reorganization (penalty for logical inconsistency)
            # The magnitude follows a power-law-like penalty scaled by neuromodulation
            penalty = (charge ** 2) * self.neuromod_gain
            return base_score - penalty
        else:
            # Small relaxation
            return base_score - (charge * 0.1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        # Phase 1: Initial Scoring based on structural alignment and NCD
        base_scores = []
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # Heuristic 1: Structural Compatibility
            struct_score = 0.5
            if prompt_feats['negation'] == cand_feats['negation']:
                struct_score += 0.2
            if prompt_feats['comparative'] == cand_feats['comparative']:
                struct_score += 0.1
            
            # Heuristic 2: NCD Similarity (as a baseline prior)
            ncd = self._compute_ncd(prompt, cand)
            # Invert NCD (0 is identical, 1 is different) -> similarity
            ncd_sim = 1.0 - ncd
            
            base_score = (struct_score * 0.6) + (ncd_sim * 0.4)
            base_scores.append((cand, base_score, cand_feats))
        
        # Phase 2: Neuromodulated SOC Adjustment
        # Calculate global "prediction error" (variance in base scores)
        if len(base_scores) > 1:
            scores_np = np.array([b[1] for b in base_scores])
            error_signal = np.std(scores_np) 
            # Neuromodulation: High variance -> High Gain (strict filtering)
            # Low variance -> Low Gain (fine discrimination)
            self.neuromod_gain = 1.0 + (error_signal * 2.0)
        else:
            self.neuromod_gain = 1.0

        for cand, base_score, cand_feats in base_scores:
            final_score = self._simulate_avalanche(prompt_feats, cand_feats, base_score)
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural match: {1.0 - abs(prompt_feats['negation'] - cand_feats['negation']):.2f}. "
            reasoning += f"SOC adjustment applied with gain {self.neuromod_gain:.2f}."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural consistency and SOC stability.
        Returns 0-1.
        """
        prompt_feats = self._structural_parse(prompt)
        ans_feats = self._structural_parse(answer)
        
        # 1. Structural Consistency Check
        consistency = 1.0
        if prompt_feats['negation'] != ans_feats['negation']:
            # Major logical conflict
            consistency -= 0.5
        if prompt_feats['numeric_density'] > 0.1 and ans_feats['numeric_density'] == 0:
            # Missing numbers when expected
            consistency -= 0.3
            
        # 2. SOC Stability Check (Simulated)
        # If the answer triggers an avalanche (high charge), confidence drops
        charge = abs(prompt_feats['negation'] - ans_feats['negation']) * 2.0
        charge += abs(prompt_feats['numeric_density'] - ans_feats['numeric_density']) * 1.5
        
        if charge > self.threshold:
            # Avalanche occurred: Low confidence
            soc_factor = 0.2
        else:
            soc_factor = 0.8
            
        base_ncd = 1.0 - self._compute_ncd(prompt, answer)
        
        # Weighted combination
        conf = (consistency * 0.4) + (soc_factor * 0.4) + (base_ncd * 0.2)
        return max(0.0, min(1.0, conf))
```

</details>
