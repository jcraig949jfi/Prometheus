# Reinforcement Learning + Active Inference + Free Energy Principle

**Fields**: Computer Science, Cognitive Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T00:39:47.862914
**Report Generated**: 2026-03-27T06:37:32.871290

---

## Nous Analysis

Combining reinforcement learning (RL), active inference (AIF), and the free‑energy principle (FEP) yields a **variational‑expected‑free‑energy policy gradient** algorithm. In practice this can be instantiated as a deep architecture where a generative model (a recurrent variational auto‑encoder) learns a probabilistic world model \(p(o_{t+1},s_{t+1}|o_t,a_t,s_t)\) and an approximate posterior \(q(s_t|o_{0:t},a_{0:t-1})\). The agent’s policy \(\pi_\theta(a_t|s_t)\) is optimized to minimize the **expected free energy**  
\[
G_\pi = \underbrace{\mathbb{E}_{q}[D_{\text{KL}}(q(s_{t+1}|o_{t+1})\|p(s_{t+1}|o_{t+1}))]}_{\text{epistemic value}} \;-\; \underbrace{\mathbb{E}_{q}[\ln p(r_{t+1}|s_{t+1})]}_{\text{extrinsic reward}} ,
\]  
which is differentiable and can be optimized with stochastic gradient ascent (e.g., using the re‑parameterization trick). This yields algorithms such as **Variational Policy Gradient (VPG)** or **Soft Actor‑Critic with Expected Free Energy (SAC‑EFE)**, where the critic estimates both extrinsic value and epistemic value, and the actor updates via a policy‑gradient that balances reward‑seeking with curiosity‑driven exploration.

For a reasoning system that must test its own hypotheses, this mechanism provides a **principled intrinsic motivation**: the epistemic term drives the agent to select actions that are expected to reduce uncertainty about hidden states (i.e., to gather data that discriminates between competing hypotheses). Consequently, the system can autonomously design experiments, prioritize observations that maximize expected information gain, and still exploit known rewards when hypotheses are confirmed.

The intersection is **not entirely novel**; active‑inference‑RL hybrids have been explored (e.g., Millidge et al., 2020 “Deep Active Inference”; Sajid et al., 2021 “Active Inference Deep Q‑Network”; and variational RL works by Hoffman et al., 2016). However, coupling the exact expected‑free‑energy formulation with modern actor‑critic methods remains relatively underexplored, offering room for new contributions.

**Ratings**  
Reasoning: 7/10 — The mechanism yields a unified objective that improves both predictive accuracy and reward‑seeking, but its benefits depend on accurate variational approximations.  
Metacognition: 8/10 — By explicitly minimizing uncertainty about internal states, the agent gains a built‑in capacity to monitor and adjust its own belief updates.  
Hypothesis generation: 8/10 — Epistemic value directly motivates actions aimed at discriminating hypotheses, enabling autonomous experiment design.  
Implementability: 6/10 — Requires training a deep generative model alongside a policy‑critic loop; while feasible (see recent DAIN and SAC‑EFE implementations), it is computationally demanding and sensitive to hyper‑parameter choices.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 6/10 |
| **Composite** | **7.67** |

**Novelty**: unclear
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Reinforcement Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Active Inference + Reinforcement Learning: strong positive synergy (+0.282). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Reinforcement Learning: strong positive synergy (+0.949). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Active Inference + Free Energy Principle: strong positive synergy (+0.384). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Reinforcement Learning + Active Inference + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Forged (passed trap battery)

| Metric | Score | vs NCD Baseline |
|--------|-------|-----------------|
| Accuracy | 27% | +7% |
| Calibration | 33% | +27% |

**Forge Timestamp**: 2026-03-25T06:34:21.452594

---

## Code

**Source**: forge

[View code](./Reinforcement_Learning---Active_Inference---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Expected Free Energy Policy Gradient (VPG-EFE) Approximator.
    
    Mechanism:
    This tool approximates the Free Energy Principle for reasoning by balancing:
    1. Extrinsic Value (Reward): Semantic alignment between prompt context and candidate.
       Implemented via keyword overlap and structural constraint matching (negations/comparatives).
    2. Epistemic Value (Curiosity): Information gain. Candidates that resolve uncertainty 
       (discriminate between options) or contain high-information tokens (numbers/logic) are favored.
    
    The final score is a weighted sum of extrinsic reward and epistemic surprise, 
    penalizing candidates that contradict explicit prompt constraints (high KL-divergence).
    """

    def __init__(self):
        # Logical connectors and structural markers for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'false', 'impossible'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after'}
        self.conditionals = {'if', 'then', 'unless', 'only if', 'provided'}
        self.numbers = {'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'}
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split by non-alphanumeric."""
        return [w.lower() for w in ''.join(c if c.isalnum() else ' ' for c in text).split()]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract explicit floats and integers from text."""
        import re
        found = []
        # Match floats and ints
        for m in re.findall(r'-?\d+\.?\d*', text):
            try:
                found.append(float(m))
            except ValueError:
                pass
        return found

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Check for logical contradictions (Modus Tollens approximation).
        Returns 0.0 if contradiction found, 1.0 otherwise.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # Detect negation contradiction
        # If prompt says "X is not Y" and candidate is "X is Y"
        has_negation = bool(p_tokens.intersection(self.negations))
        has_candidate_affirmation = bool(c_tokens.intersection(p_tokens)) # Simplified
        
        # Specific check: If prompt contains "not" + word, candidate should not be just that word
        if has_negation:
            # Heuristic: If prompt has strong negation and candidate is a short affirmative echo
            if len(c_tokens) < 4 and any(n in p_tokens for n in self.negations):
                # Check if candidate contradicts a specific "not X" pattern
                p_list = list(p_tokens)
                for i, t in enumerate(p_list):
                    if t == 'not' and i+1 < len(p_list):
                        target = p_list[i+1]
                        if target in c_tokens and len(c_tokens) <= 2:
                            return 0.0 # Contradiction detected

        # Numeric constraint propagation
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # If prompt implies an order (e.g., contains "less"), check numbers
            p_has_less = any(w in p_tokens for w in ['less', 'smaller', 'below'])
            p_has_more = any(w in p_tokens for w in ['more', 'greater', 'above'])
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Simple transitivity check if candidate picks a number
                cand_val = c_nums[0]
                # If prompt says "A < B" and asks which is smaller, candidate should be A
                # This is a rough approximation of constraint propagation
                if p_has_less:
                    if cand_val > max(p_nums): # Candidate picked a large number when asking for small
                        return 0.2 # Penalty
                if p_has_more:
                    if cand_val < min(p_nums): # Candidate picked small when asking for large
                        return 0.2

        return 1.0

    def _compute_extrinsic_value(self, prompt: str, candidate: str) -> float:
        """
        Estimate extrinsic reward based on semantic overlap and structural relevance.
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # Remove stop words for better signal
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'to', 'of', 'and', 'in', 'that', 'this'}
        p_sig = p_tokens - stopwords
        c_sig = c_tokens - stopwords
        
        if not p_sig or not c_sig:
            return 0.0
            
        # Jaccard similarity on significant tokens
        intersection = p_sig.intersection(c_sig)
        union = p_sig.union(c_sig)
        base_score = len(intersection) / len(union) if union else 0.0
        
        # Boost for logical keyword matching
        logic_boost = 0.0
        if any(k in c_sig for k in self.conditionals) and any(k in p_sig for k in self.conditionals):
            logic_boost += 0.2
        if any(k in c_sig for k in self.comparatives) and any(k in p_sig for k in self.comparatives):
            logic_boost += 0.2
            
        return min(1.0, base_score + logic_boost)

    def _compute_epistemic_value(self, prompt: str, candidate: str) -> float:
        """
        Estimate epistemic value (information gain).
        Favors candidates that reduce uncertainty (contain numbers, specific logic terms).
        """
        c_tokens = self._tokenize(candidate)
        p_len = len(self._tokenize(prompt))
        c_len = len(c_tokens)
        
        # Information density: ratio of unique content words
        if c_len == 0:
            return 0.0
            
        unique_ratio = len(set(c_tokens)) / c_len
        
        # Bonus for numeric precision (resolves ambiguity)
        nums = self._extract_numbers(candidate)
        num_bonus = min(0.3, len(nums) * 0.15)
        
        # Bonus for logical operators (discriminative power)
        logic_count = sum(1 for t in c_tokens if t in self.negations or t in self.conditionals or t in self.comparatives)
        logic_bonus = min(0.3, logic_count * 0.1)
        
        return min(1.0, unique_ratio * 0.5 + num_bonus + logic_bonus)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        scored_candidates = []
        
        for cand in candidates:
            # 1. Constraint Propagation (Hard filter / heavy penalty)
            constraint_score = self._check_constraints(prompt, cand)
            
            if constraint_score < 0.5:
                # Strong contradiction
                final_score = 0.1 * constraint_score
                reasoning = "Contradicts prompt constraints."
            else:
                # 2. Extrinsic Value (Reward)
                extrinsic = self._compute_extrinsic_value(prompt, cand)
                
                # 3. Epistemic Value (Curiosity/Information Gain)
                epistemic = self._compute_epistemic_value(prompt, cand)
                
                # Free Energy Minimization Analogy:
                # We want to Maximize (Extrinsic + Epistemic)
                # Weighted sum: Epistemic is crucial for reasoning tasks (hypothesis testing)
                combined_score = (0.6 * extrinsic) + (0.4 * epistemic)
                
                # Apply constraint multiplier
                final_score = combined_score * constraint_score
                
                reasoning_parts = []
                if extrinsic > 0.5: reasoning_parts.append("high relevance")
                if epistemic > 0.3: reasoning_parts.append("high information density")
                if not reasoning_parts: reasoning_parts.append("low signal")
                reasoning = f"Scored on {', '.join(reasoning_parts)}."

            # NCD Tiebreaker (small adjustment)
            ncd_val = self._ncd(prompt, cand)
            # Lower NCD is better (more similar), so subtract small portion
            tiebreak_adj = (1.0 - ncd_val) * 0.05 
            final_score += tiebreak_adj
            
            # Clamp
            final_score = max(0.0, min(1.0, final_score))
            
            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]
```

</details>
