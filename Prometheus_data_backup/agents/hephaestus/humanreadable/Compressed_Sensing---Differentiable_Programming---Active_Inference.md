# Compressed Sensing + Differentiable Programming + Active Inference

**Fields**: Computer Science, Computer Science, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T00:49:29.738572
**Report Generated**: 2026-03-27T06:37:32.963287

---

## Nous Analysis

Combining compressed sensing, differentiable programming, and active inference yields a **gradient‑driven, sparse‑coding perception‑action loop** in which an agent continuously refines a latent sparse representation of the world while selecting actions that maximally reduce expected free energy. Concretely, the perception module is a differentiable unrolled optimizer (e.g., Learned ISTA or a deep equilibrium network) that solves the ℓ₁‑minimization problem ‖x‖₁ s.t. y = Φx, where the measurement matrix Φ is itself a differentiable function of the agent’s motor commands (e.g., a steerable sensor or controllable antenna array). The resulting sparse code x serves as the agent’s belief state. Action selection follows the active‑inference principle: the agent computes the expected free energy G(π) = E[ ‑log p(o|s) + KL (q(s|o)‖p(s)) ] over policies π, where the observation model p(o|s) is instantiated by the differentiable sensing front‑end and the prior p(s) encourages sparsity (an ℓ₁‑based Laplace prior). Gradients flow from G(π) back through the unrolled sparse‑coding solver to the policy network, enabling end‑to‑end learning of both sensing configurations and control policies.

For a reasoning system testing its own hypotheses, this mechanism provides the advantage of **informative, measurement‑efficient hypothesis probing**: the system can actively steer its sensors to acquire the most discriminative, low‑dimensional data needed to confirm or refute a candidate sparse explanation, while the differentiable solver guarantees rapid belief updates and the sparsity prior keeps the hypothesis space tractable.

The triple intersection is **largely novel**. Differentiable compressed sensing (Learned ISTA, deep equilibrium models) and active‑inference agents with neural networks exist separately, and some work uses sparsity priors in active inference for perceptual learning, but a fully integrated loop where the sensing matrix is policy‑dependent, the inference is a differentiable sparse coder, and action selection optimizes expected free energy has not been explicitly formulated in the literature.

**Ratings**  
Reasoning: 7/10 — The mechanism yields principled, uncertainty‑aware inference but adds non‑convex optimization challenges.  
Metacognition: 6/10 — The agent can monitor free‑energy gradients, yet true higher‑order self‑modeling remains limited.  
Hypothesis generation: 8/10 — Active epistemic foraging combined with sparse hypothesis spaces yields efficient, targeted hypothesis testing.  
Implementability: 5/10 — Requires careful tuning of unrolled solvers, differentiable sensors, and stable free‑energy gradients; still at research‑prototype stage.

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

- **Compressed Sensing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Differentiable Programming**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Compressed Sensing + Differentiable Programming: strong positive synergy (+0.457). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Active Inference + Compressed Sensing: negative interaction (-0.080). Keep these concepts in separate code paths to avoid interference.
- Active Inference + Differentiable Programming: strong positive synergy (+0.438). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Compressed Sensing + Differentiable Programming + Falsificationism (accuracy: 0%, calibration: 0%)
- Differentiable Programming + Gene Regulatory Networks + Active Inference (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T04:51:10.628749

---

## Code

**Source**: scrap

[View code](./Compressed_Sensing---Differentiable_Programming---Active_Inference/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a gradient-driven, sparse-coding perception-action loop analogy.
    
    Mechanism:
    1. Active Inference (Core): The 'evaluate' loop minimizes Expected Free Energy (G).
       G is approximated by balancing 'Surprise' (structural mismatch with prompt constraints)
       and 'Complexity' (deviation from sparse priors).
    2. Compressed Sensing Analogy: Candidates are treated as measurements. We seek the 
       'sparsest' explanation that satisfies the prompt's logical constraints. 
       Structural features (negations, comparatives) act as the measurement matrix Phi.
    3. Differentiable Programming Analogy: We simulate gradient flow by propagating 
       constraint satisfaction scores. If a candidate violates a hard constraint (e.g., 
       negation), the 'error' signal is high, reducing the score.
       
    This approach prioritizes structural parsing and constraint propagation over 
    simple string similarity, using NCD only as a tie-breaking regularizer.
    """

    def __init__(self):
        # Sparse prior weight (Laplace-like penalty for complexity)
        self.sparse_prior_weight = 0.2
        # Structural constraint weight
        self.struct_weight = 0.6
        # NCD tiebreaker weight
        self.ncd_weight = 0.2

    def _extract_structural_features(self, text: str) -> dict:
        """Extracts logical operators, negations, and comparatives."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'quantifiers': len(re.findall(r'\b(all|some|none|every|each|most)\b', text_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', text_lower),
            'length': len(text)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode('utf-8')))
            c2 = len(zlib.compress(s2.encode('utf-8')))
            c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Simulates the 'gradient' of constraint satisfaction.
        Returns a score between 0 (violation) and 1 (satisfied).
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has 'not', candidate should ideally reflect understanding or not contradict
        if p_feat['negations'] > 0:
            # Heuristic: If prompt negates, and candidate is extremely short (like "Yes"), 
            # it might be ambiguous. We check for explicit contradiction patterns if possible.
            # For this implementation, we penalize if the candidate ignores the negation context
            # by lacking similar logical depth when the prompt is complex.
            if p_feat['negations'] > c_feat['negations'] and c_feat['length'] < 10:
                score -= 0.2 # Penalty for oversimplification in negative contexts

        # 2. Number Consistency (Numeric Evaluation)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Check if numbers in candidate are consistent with prompt logic (simplified)
                # If prompt asks for "smaller", and candidate has numbers, check magnitude
                if 'smaller' in p_lower or 'less' in p_lower:
                    p_nums = [float(x) for x in p_feat['numbers']]
                    c_nums = [float(x) for x in c_feat['numbers']]
                    if p_nums and c_nums:
                        # If prompt implies reduction, candidate number should ideally be smaller 
                        # than the max in prompt (heuristic approximation)
                        if max(c_nums) > max(p_nums) * 1.5: # Arbitrary threshold for "reduction"
                            score -= 0.3
                elif 'greater' in p_lower or 'more' in p_lower:
                    p_nums = [float(x) for x in p_feat['numbers']]
                    c_nums = [float(x) for x in c_feat['numbers']]
                    if p_nums and c_nums:
                        if min(c_nums) < min(p_nums) * 0.5:
                            score -= 0.3
            except ValueError:
                pass

        # 3. Keyword Overlap with Logical Operators (Constraint Propagation)
        # Ensure candidate shares key logical operators if present in prompt
        logical_ops = ['if', 'then', 'not', 'all', 'some', 'none']
        p_ops = [w for w in logical_ops if w in p_lower]
        if p_ops:
            c_ops = [w for w in logical_ops if w in c_lower]
            # Jaccard similarity of logical operators
            if len(p_ops) > 0:
                intersection = len(set(p_ops) & set(c_ops))
                union = len(set(p_ops) | set(c_ops))
                if union > 0:
                    op_sim = intersection / union
                    score = score * (0.7 + 0.3 * op_sim) # Boost if logical structure matches

        return max(0.0, min(1.0, score))

    def _compute_expected_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes a proxy for Expected Free Energy (G).
        G = Surprise (Mismatch) + Complexity (Prior violation)
        We return negative G so higher is better (minimizing free energy).
        """
        # 1. Surprise term: Structural mismatch
        constraint_score = self._check_constraint_satisfaction(prompt, candidate)
        surprise = 1.0 - constraint_score
        
        # 2. Complexity term: Length deviation (Sparsity prior)
        # Ideal candidate is concise but complete. 
        # Penalize extreme verbosity relative to prompt
        p_len = len(prompt)
        c_len = len(candidate)
        ratio = c_len / (p_len + 1)
        # Sparsity penalty: penalize if candidate is too long (verbose) or too short (missing info)
        # Optimal ratio around 0.1 to 0.8 depending on task, but let's penalize extremes
        complexity_penalty = 0.0
        if ratio > 2.0: # Too verbose
            complexity_penalty = 0.3
        elif ratio < 0.01 and p_len > 50: # Too short for complex prompt
            complexity_penalty = 0.2
            
        # NCD as regularizer (Tiebreaker)
        ncd = self._compute_ncd(prompt, candidate)
        
        # Free Energy approximation
        # Lower G is better. We want to maximize ( -G )
        # G ~ surprise + complexity - (1-ncd) [ncd helps if relevant]
        # Actually, let's just construct a score:
        # Score = (Structural Fit * Weight) + (Sparsity Bonus) - (NCD Penalty if irrelevant)
        
        structural_bonus = constraint_score * self.struct_weight
        sparsity_bonus = (1.0 - complexity_penalty) * self.sparse_prior_weight
        
        # NCD is tricky. High NCD means dissimilar. 
        # In QA, answer should be semantically similar but structurally distinct?
        # Let's use NCD only to break ties or penalize gibberish.
        # If NCD is very high (>0.9), it might be noise.
        ncd_penalty = 0.0
        if ncd > 0.95:
            ncd_penalty = 0.1
            
        total_score = structural_bonus + sparsity_bonus - ncd_penalty
        return total_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Compute scores
        scores = []
        for cand in candidates:
            score = self._compute_expected_free_energy(prompt, cand)
            scores.append(score)
        
        # Normalize scores to 0-1 range for consistency (Softmax-like normalization)
        min_s = min(scores)
        max_s = max(scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        normalized_scores = []
        for s in scores:
            # Scale to [0.1, 0.9] to avoid absolute 0/1 unless extreme
            norm_s = 0.1 + 0.8 * ((s - min_s) / range_s)
            normalized_scores.append(norm_s)
        
        # Rank and format
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": normalized_scores[i],
                "reasoning": f"Structural fit: {normalized_scores[i]:.2f}, based on constraint satisfaction and sparsity prior."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        # Reuse the energy minimization logic
        # A high score in evaluate corresponds to low free energy -> high confidence
        raw_score = self._compute_expected_free_energy(prompt, answer)
        
        # Map raw score (approx -0.2 to 1.2) to 0-1
        # Based on weights: max possible ~ 1.0 (struct) + 0.2 (sparse) = 1.2
        # Min possible ~ -0.3 (penalties)
        confidence = (raw_score + 0.3) / 1.5
        return max(0.0, min(1.0, confidence))
```

</details>
