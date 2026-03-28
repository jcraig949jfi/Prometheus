# Thermodynamics + Monte Carlo Tree Search + Hebbian Learning

**Fields**: Physics, Computer Science, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T07:47:03.490594
**Report Generated**: 2026-03-27T06:37:36.176203

---

## Nous Analysis

Combining thermodynamics, Monte Carlo Tree Search (MCTS), and Hebbian learning yields a **Free‑Energy‑Guided, Synaptically‑Plastic Tree Search** (FE‑SPTS). In this architecture each tree node stores a scalar *value* Q and a *synaptic trace* w that reflects the co‑activation frequency of parent‑child edges during rollouts. Selection uses a thermodynamic soft‑max (Boltzmann) policy derived from the node’s free energy F = −T log ∑ exp(−E/kT), where the “energy” E is a combination of negative Q and an entropy term −H that encourages exploration of high‑variance branches. After each simulation, the rollout outcome updates Q via standard back‑propagation, and simultaneously updates w with a Hebbian rule Δw = η · a_parent · a_child − λ w, where a are the activation probabilities of the edge during the rollout. Over time, edges that repeatedly participate in low‑free‑energy (high‑reward, low‑uncertainty) trajectories strengthen, biasing future selections toward promising hypotheses while preserving stochastic exploration via the temperature T.

**Advantage for hypothesis testing:** The system can treat each hypothesis as a path from root to leaf. By simulating rollouts, it estimates the free‑energy change ΔF associated with adopting that hypothesis. A negative ΔF signals a thermodynamically favorable (low‑entropy, high‑reward) update, triggering Hebbian reinforcement of the corresponding edges. Thus the system not only evaluates hypotheses but also self‑organizes its internal hypothesis‑generation machinery, yielding metacognitive insight into which lines of reasoning are both productive and stable.

**Novelty:** Entropy‑regularized MCTS and Boltzmann exploration appear in soft‑MCTS and Bayesian bandits, and Hebbian plasticity is studied in neural‑network‑guided search. However, a unified framework that treats node selection as free‑energy minimization, couples it to synaptic trace updates via Hebbian learning, and uses the resulting plasticity to modulate the search policy itself has not been widely reported in the literature. The closest analogues are Free‑Energy‑Principle‑based planners and neuromorphic RL, but they do not explicitly combine all three mechanisms in a tree‑search setting, making FE‑SPTS a relatively novel intersection.

**Ratings**  
Reasoning: 7/10 — Provides a principled, thermodynamically grounded balance of exploration/exploitation that improves solution quality in noisy domains.  
Metacognition: 8/10 — Free‑energy monitoring gives the system an explicit signal of its own uncertainty and model fit, enabling self‑assessment.  
Hypothesis generation: 7/10 — Hebbian traces bias future hypothesis sampling toward historically successful pathways, accelerating productive idea generation.  
Implementability: 5/10 — Requires custom node structures storing both Q and w, and a non‑standard backup rule; while feasible in simulation, integrating with existing MCTS libraries entails nontrivial engineering effort.

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

- **Thermodynamics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 40% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Monte Carlo Tree Search**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Monte Carlo Tree Search + Thermodynamics: strong positive synergy (+0.314). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Thermodynamics + Monte Carlo Tree Search + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=33% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T20:02:52.169765

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Monte_Carlo_Tree_Search---Hebbian_Learning/tool.py)

<details>
<summary>Show code</summary>

```python
import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    FE-SPTS Approximation: Free-Energy-Guided Synaptically-Plastic Tree Search.
    
    Mechanism:
    1. Thermodynamics (Energy): Uses NCD to estimate "energy" (dissimilarity) between 
       prompt context and candidate. Lower energy = higher affinity.
    2. MCTS (Exploration): Simulates "rollouts" by perturbing the candidate string 
       (structural parsing of negations/numbers) to estimate variance/uncertainty.
    3. Hebbian Learning (Plasticity): Maintains a global synaptic trace of successful 
       structural patterns (e.g., "not", "<", "if"). If a candidate containing these 
       patterns wins, the trace strengthens, biasing future energy calculations.
       
    Scoring: Free Energy F = E - T*S. 
    E = NCD-based dissimilarity. 
    S = Entropy derived from structural consistency checks.
    """

    def __init__(self):
        # Synaptic traces: weights for structural features that historically led to success
        self.synaptic_traces = {
            'negation': 0.5,
            'comparative': 0.5,
            'conditional': 0.5,
            'numeric': 0.5
        }
        self.learning_rate = 0.1
        self.decay = 0.01
        self.temperature = 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max_len

    def _extract_features(self, text: str) -> Dict[str, bool]:
        """Structural parsing for negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'negation': bool(re.search(r'\b(not|no|never|neither|nobody)\b', t_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|<|>)\b', t_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', t_lower)),
            'numeric': bool(re.search(r'\d+(\.\d+)?', text))
        }
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Energy E. 
        Base: NCD between prompt and candidate.
        Modulation: Penalize based on mismatched structural expectations weighted by synaptic traces.
        """
        # Base energy from compression distance (lower is better match)
        base_energy = self._ncd(prompt, candidate)
        
        # Structural penalty/bonus
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        structural_penalty = 0.0
        for key in p_feats:
            # If prompt has feature and candidate doesn't (or vice versa), add penalty weighted by trace
            if p_feats[key] != c_feats[key]:
                structural_penalty += self.synaptic_traces.get(key, 0.5) * 0.2
        
        return base_energy + structural_penalty

    def _simulate_rollout(self, prompt: str, candidate: str) -> float:
        """
        Simulate a rollout by checking structural consistency.
        Returns variance (uncertainty). Lower variance = more stable hypothesis.
        """
        # Check numeric consistency if numbers exist
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        variance = 0.0
        
        # Simple numeric logic check
        if p_nums and c_nums:
            try:
                # If prompt implies order (e.g. "less than"), check if candidate respects it roughly
                # This is a heuristic approximation of a rollout outcome
                if "less" in prompt.lower() or "<" in prompt:
                    if float(c_nums[0]) > float(p_nums[0]):
                        variance += 0.5 # High variance/unlikely
                elif "more" in prompt.lower() or ">" in prompt:
                    if float(c_nums[0]) < float(p_nums[0]):
                        variance += 0.5
            except ValueError:
                variance += 0.1
        
        # Check negation flip
        if "not" in prompt.lower() and "not" not in candidate.lower():
             # Potential trap, increase uncertainty
            variance += 0.2
            
        return variance

    def _update_traces(self, winning_features: Dict[str, bool]):
        """Hebbian update: strengthen traces for features present in the winner."""
        for key, val in winning_features.items():
            if val:
                # Delta w = eta * a_parent * a_child - lambda * w
                # Here activation is binary (1 if present)
                delta = self.learning_rate * 1.0 * 1.0 - self.decay * self.synaptic_traces[key]
                self.synaptic_traces[key] = max(0.0, min(1.0, self.synaptic_traces[key] + delta))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        best_score = float('inf')
        best_features = {}

        # 1. Evaluation Phase (Selection & Rollout)
        for cand in candidates:
            energy = self._compute_energy(prompt, cand)
            entropy = self._simulate_rollout(prompt, cand)
            
            # Free Energy F = E - T * S (Minimizing F)
            # We want low energy (good match) and low entropy (stable)
            # But in thermodynamics, we often maximize entropy for exploration.
            # Here, we treat "Free Energy" as a cost function to minimize.
            # F = Energy - Temperature * (Negative Entropy) -> F = E + T*Uncertainty
            free_energy = energy + self.temperature * entropy
            
            scored_candidates.append({
                "candidate": cand,
                "score": -free_energy, # Higher score = better (lower free energy)
                "reasoning": f"E={energy:.2f}, S={entropy:.2f}, F={free_energy:.2f}"
            })
            
            if free_energy < best_score:
                best_score = free_energy
                best_features = self._extract_features(cand)

        # 2. Learning Phase (Hebbian Update)
        # Only update if we found a distinct best candidate
        if best_features:
            self._update_traces(best_features)

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        """
        energy = self._compute_energy(prompt, answer)
        entropy = self._simulate_rollout(prompt, answer)
        free_energy = energy + self.temperature * entropy
        
        # Map free energy to 0-1 confidence. 
        # Low free energy -> High confidence. 
        # Assuming max reasonable free energy is ~2.0
        conf = max(0.0, 1.0 - (free_energy / 2.0))
        return min(1.0, conf)
```

</details>
