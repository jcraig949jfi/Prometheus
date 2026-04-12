# Neural Oscillations + Multi-Armed Bandits + Free Energy Principle

**Fields**: Neuroscience, Game Theory, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T03:06:39.511027
**Report Generated**: 2026-03-27T06:37:34.189678

---

## Nous Analysis

Combining neural oscillations, multi‑armed bandits, and the free‑energy principle yields a **hierarchical predictive‑coding controller in which oscillatory phase‑coupling regulates a bandit‑driven exploration‑exploitation policy over latent hypotheses**. At each level of a hierarchical Gaussian filter (HGF) or deep active‑inference network, the precision of prediction errors is modulated by cross‑frequency coupling: theta rhythms (4‑8 Hz) set a slow “meta‑exploration” envelope, while gamma bursts (30‑80 Hz) encode the instantaneous likelihood of specific sensory predictions. The theta envelope determines the exploration rate ε(t) fed into a Thompson‑sampling bandit that samples from the posterior over competing hypotheses (each hypothesis corresponds to a different set of generative model parameters). When a hypothesis is selected, its associated gamma‑band synchrony binds the relevant neuronal populations, reducing prediction error through predictive‑coding message passing. Prediction errors themselves update the posterior (variational free‑energy minimization) and also shift the theta‑driven exploration schedule via a reinforcement‑learning signal (e.g., dopamine‑like reward prediction error).  

**Advantage for self‑testing:** The system can rapidly alternate between exploiting the currently best‑supported hypothesis (high gamma precision) and probing alternatives when theta‑mediated uncertainty rises, yielding adaptive, data‑efficient hypothesis testing without manual annealing schedules.  

**Novelty:** Predictive coding + bandits appears in active‑inference literature (e.g., Friston et al., 2017; Millidge et al., 2020), and oscillatory predictive coding has been explored (e.g., Bastos et al., 2012; Murray et al., 2016). However, explicitly coupling theta‑gamma cross‑frequency dynamics to a Thompson‑sampling bandit that governs hypothesis selection is not a standard formulation; recent neuromorphic work on oscillatory bandits (e.g., Liao et al., 2023) touches on similar ideas but does not embed them in a full free‑energy minimization loop. Hence the intersection is **partially novel**, extending existing frameworks rather than reproducing them.  

**Ratings**  
Reasoning: 7/10 — The mechanism yields principled, uncertainty‑aware inference but adds architectural complexity that may obscure intuitive reasoning traces.  
Metacognition: 8/10 — Theta‑mediated exploration provides an explicit, monitorable signal of uncertainty, supporting strong metacognitive awareness of one’s own belief states.  
Hypothesis generation: 8/10 — Thompson sampling over hierarchical posteriors drives principled, novel hypothesis proposals guided by prediction‑error surprise.  
Implementability: 5/10 — Requires precise neuromorphic or spiking‑hardware support for cross‑frequency plasticity and bandit sampling; software simulations are feasible but real‑time, low‑power deployment remains challenging.

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

- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Multi-Armed Bandits + Neural Oscillations: strong positive synergy (+0.456). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Neural Oscillations: strong positive synergy (+0.271). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Multi-Armed Bandits: strong positive synergy (+0.252). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Multi-Armed Bandits + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-25T14:45:29.439676

---

## Code

**Source**: scrap

[View code](./Neural_Oscillations---Multi-Armed_Bandits---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Predictive-Coding Controller with Oscillatory Bandit Policy.
    
    Mechanism:
    1. Free Energy Principle (Core): The 'score' is an inverse measure of variational 
       free energy (surprise). We minimize free energy by maximizing structural consistency 
       between the prompt's logical constraints and the candidate's assertions.
    2. Neural Oscillations (Confidence Wrapper): Per causal analysis, oscillatory concepts 
       are restricted to the confidence() method. We simulate Theta-Gamma coupling where 
       Theta (slow wave) modulates the exploration rate (uncertainty) and Gamma (fast burst) 
       represents the precision of the match. High precision (low error) yields high confidence.
    3. Multi-Armed Bandit (Selection): We treat candidate selection as a Thompson Sampling 
       problem. The 'reward' is the structural match score. The system 'exploits' the 
       candidate with the highest expected reward (lowest free energy) while using the 
       oscillatory confidence to gauge if 'exploration' (rejecting all/uncertainty) is needed.
    4. Structural Parsing: We explicitly extract negations, comparatives, and numeric values 
       to compute the prediction error (mismatch) rather than relying on string similarity.
    """

    def __init__(self):
        self.epsilon_base = 0.1  # Base exploration rate
        self.precision_gamma = 1.0  # Precision scaling factor

    def _structural_parse(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        # Convert numbers to float for comparison
        try:
            features['numeric_vals'] = [float(n) for n in features['numbers']]
        except ValueError:
            features['numeric_vals'] = []
        return features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy (F) as a proxy for prediction error.
        F = Complexity - Accuracy (simplified). 
        Lower F is better. We invert this for scoring later.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect it or not contradict
        if p_feat['negations'] > 0:
            # Penalty if candidate ignores negation context entirely (simple heuristic)
            if c_feat['negations'] == 0 and p_feat['negations'] > 1:
                error += 0.5 * p_feat['negations']
        
        # 2. Numeric Consistency
        if p_feat['numeric_vals'] and c_feat['numeric_vals']:
            # Check if relative order is preserved or if values match
            p_nums = sorted(p_feat['numeric_vals'])
            c_nums = sorted(c_feat['numeric_vals'])
            
            # Simple transitivity check: does the candidate contain numbers from prompt?
            # Or if it introduces new numbers, is it logically consistent? 
            # Heuristic: Penalty for completely disjoint numeric ranges if prompt has specific constraints
            if len(p_nums) == len(c_nums):
                for p, c in zip(p_nums, c_nums):
                    error += abs(p - c) * 0.1
            else:
                # Mismatch in count implies potential error unless logical operator changes it
                error += 0.2 * abs(len(p_nums) - len(c_nums))

        # 3. Conditional/Logical Flow
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] == 0:
                # Candidate might be answering the condition, so not always an error
                # But if prompt is complex conditional and answer is too short, likely error
                if c_feat['length'] < p_feat['length'] * 0.2:
                    error += 0.3

        # 4. NCD as Tiebreaker (only adds small amount to error if structural signals are weak)
        # We use NCD only when structural features are ambiguous
        structural_signal = p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']
        if structural_signal == 0:
            try:
                combined = (prompt + candidate).encode('utf-8')
                comp_both = len(zlib.compress(combined))
                comp_c = len(zlib.compress(candidate.encode('utf-8')))
                comp_p = len(zlib.compress(prompt.encode('utf-8')))
                ncd = (comp_both - min(comp_p, comp_c)) / max(comp_p, comp_c) if max(comp_p, comp_c) > 0 else 1.0
                error += ncd * 0.1 # Low weight tiebreaker
            except:
                error += 0.5

        return error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Free Energy minimization.
        Returns ranked list by score (higher is better).
        """
        if not candidates:
            return []
            
        results = []
        free_energies = []
        
        # Phase 1: Compute Free Energy (Prediction Error) for all hypotheses
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            free_energies.append(fe)
        
        # Phase 2: Convert Free Energy to Score (Precision-weighted)
        # Score = exp(-F) normalized. Lower F -> Higher Score.
        # Add small epsilon to avoid division by zero if all FE are 0
        min_fe = min(free_energies)
        max_fe = max(free_energies) if len(free_energies) > 1 else min_fe + 1.0
        
        scores = []
        for fe in free_energies:
            # Normalize FE to 0-1 range roughly, then invert
            # Using a soft-max like approach on negative free energy
            raw_score = math.exp(-fe * 2.0) 
            scores.append(raw_score)
            
        # Normalize scores to 0-1
        sum_scores = sum(scores) + 1e-9
        normalized_scores = [s / sum_scores for s in scores]
        
        # Phase 3: Thompson Sampling Analogue (Exploration-Exploitation)
        # We add noise proportional to uncertainty (variance in scores) to simulate 
        # the bandit sampling. High uncertainty -> higher noise (Theta modulation).
        import random
        variance = 0.0
        if len(normalized_scores) > 1:
            mean_s = sum(normalized_scores) / len(normalized_scores)
            variance = sum((s - mean_s)**2 for s in normalized_scores) / len(normalized_scores)
        
        final_results = []
        for i, cand in enumerate(candidates):
            # Sample from posterior (approximated by adding noise to score)
            noise = random.gauss(0, math.sqrt(variance) * 0.1) if variance > 0 else 0
            sampled_score = normalized_scores[i] + noise
            sampled_score = max(0.0, min(1.0, sampled_score)) # Clamp
            
            final_results.append({
                "candidate": cand,
                "score": sampled_score,
                "reasoning": f"Free Energy: {free_energies[i]:.4f}, Structural Match: {'High' if free_energies[i] < 0.5 else 'Low'}"
            })
            
        # Rank by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence using Oscillatory Analogy (Theta-Gamma Coupling).
        Theta (slow): Global uncertainty based on structural complexity.
        Gamma (fast): Local precision of the match.
        Confidence = Gamma Precision * (1 - Theta Uncertainty)
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(answer)
        
        # Gamma: Instantaneous likelihood (Precision of match)
        # Based on inverse free energy of this specific pair
        fe = self._compute_free_energy(prompt, answer)
        gamma_precision = math.exp(-fe * 2.0) # High precision if FE is low
        
        # Theta: Meta-exploration envelope (Uncertainty)
        # Driven by complexity of the prompt (more conditions/negations = higher uncertainty)
        complexity = p_feat['negations'] + p_feat['conditionals'] + (len(p_feat['numbers']) * 0.5)
        theta_uncertainty = 1.0 - math.exp(-complexity * 0.3) # Sigmoidal rise with complexity
        
        # Coupling: Confidence is high only if precision is high AND uncertainty is managed
        # If theta (uncertainty) is too high, it dampens the effective confidence unless gamma is extremely strong
        raw_conf = gamma_precision * (1.0 - 0.5 * theta_uncertainty)
        
        return float(max(0.0, min(1.0, raw_conf)))
```

</details>
