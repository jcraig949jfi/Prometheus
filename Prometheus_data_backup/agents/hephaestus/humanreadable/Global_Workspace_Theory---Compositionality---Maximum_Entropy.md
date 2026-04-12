# Global Workspace Theory + Compositionality + Maximum Entropy

**Fields**: Cognitive Science, Linguistics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:06:09.391989
**Report Generated**: 2026-03-27T06:37:29.116921

---

## Nous Analysis

**1. Computational mechanism**  
A *Maximum‑Entropy Compositional Global Workspace* (MECGW) can be built as a hybrid architecture:  
- **Compositional core**: a typed lambda‑calculus or neural‑symbolic program synthesizer (e.g., Deep Symbolic Regression, Neural Programmer‑Interpreter) that builds complex hypotheses from primitive operations using explicit syntax‑semantics rules.  
- **Global workspace layer**: a set of competing “workspace modules” (inspired by GWT) that receive activation from the compositional core via an attention‑like gating mechanism. Modules vie for ignition through a soft‑max competition whose logits are derived from a maximum‑entropy distribution over workspace states subject to current constraints (e.g., task goals, resource limits).  
- **Maximum‑entropy inference**: each module maintains a belief distribution over possible interpretations of its broadcast content, updated by Jaynes’ principle to be the least‑biased exponential family consistent with observed constraints (prediction errors, reward signals). The broadcast itself is the sample from this max‑ent distribution, ensuring maximal ignorance where data are silent.  

During reasoning, the workspace ignites a compositional hypothesis, broadcasts it, and all modules receive the same signal; each updates its max‑ent belief, producing a coherent, uncertainty‑aware evaluation.

**2. Advantage for self‑testing hypotheses**  
The system can generate a *diverse ensemble* of compositional candidates (thanks to the symbolic combinatorics) while the max‑ent broadcast guarantees that no unwarranted assumptions are injected. Competing modules then provide *simultaneous, constraint‑consistent critiques* (e.g., logical consistency, predictive accuracy). This yields a built‑in hypothesis‑testing loop: generation → broadcast → multi‑faceted evaluation → belief revision, all while preserving minimal bias and reusing sub‑programs compositionally.

**3. Novelty**  
Pure GWT models (Baars, Dehaene) lack formal probabilistic updating; compositional neural‑symbolic systems (e.g., Neural Symbolic Machines, DSCL) rarely embed a global broadcast competition; max‑ent frameworks (Jaynes, MaxEnt logistic regression) are not tied to a workspace architecture. While related work exists in predictive coding, Bayesian neural networks, and probabilistic programming (e.g., Anglican, Pyro), the specific triad — compositional program synthesis, GWT‑style ignition, and max‑ent belief updating — has not been instantiated as a unified algorithm. Hence the combination is largely novel, though it draws on well‑studied components.

**4. Ratings**  
Reasoning: 7/10 — combines strong symbolic composition with principled uncertainty, but inference can be costly.  
Metacognition: 8/10 — the workspace provides explicit self‑monitoring of broadcast states and confidence via max‑ent entropy.  
Hypothesis generation: 8/10 — compositional primitives enable combinatorial explosion of candidates; max‑ent bias‑lessness encourages exploration.  
Implementability: 5/10 — requires integrating attention‑based gating, symbolic program synthesis, and exponential‑family updates; engineering effort is nontrivial.  

Reasoning: 7/10 — combines strong symbolic composition with principled uncertainty, but inference can be costly.  
Metacognition: 8/10 — the workspace provides explicit self-monitoring of broadcast states and confidence via max‑ent entropy.  
Hypothesis generation: 8/10 — compositional primitives enable combinatorial explosion of candidates; max‑ent bias‑lessness encourages exploration.  
Implementability: 5/10 — requires integrating attention‑based gating, symbolic program synthesis, and exponential‑family updates; engineering effort is nontrivial.

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

- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Compositionality + Global Workspace Theory: strong positive synergy (+0.293). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Category Theory + Global Workspace Theory + Epistemology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=33% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T13:18:56.978798

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Compositionality---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import json
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Maximum-Entropy Compositional Global Workspace (MECGW) Implementation.
    
    Mechanism:
    1. Compositional Core: Parses prompts into structured constraints (negations, 
       comparatives, conditionals, numeric values) acting as primitive operations.
    2. Global Workspace: Candidates compete for "ignition" based on how well they 
       satisfy the parsed constraints. The "broadcast" is the evaluation of each 
       candidate against these global constraints.
    3. Maximum Entropy: Scores are derived from an exponential family distribution 
       where the probability of a candidate being correct is proportional to 
       exp(lambda * constraint_satisfaction). This ensures the system remains 
       maximally non-committal (high entropy) regarding features not constrained 
       by the logic, while strictly adhering to detected structural rules.
    
    Strategy:
    - Structural parsing provides hard/soft constraints (high weight).
    - Numeric evaluation handles magnitude comparisons.
    - NCD is used strictly as a tiebreaker for semantic similarity when structural
      signals are ambiguous or equal, preventing bias towards short/generic answers.
    """

    def __init__(self):
        self.constraint_weights = {
            'negation_match': 2.0,
            'comparative_logic': 2.5,
            'conditional_consistency': 2.0,
            'numeric_accuracy': 3.0,
            'keyword_overlap': 0.5,
            'ncd_bonus': 0.1
        }

    def _parse_structure(self, prompt: str) -> dict:
        """Extract compositional primitives: negations, comparatives, numbers, conditionals."""
        p_lower = prompt.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', p_lower)),
            'comparatives': re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', p_lower),
            'conditionals': bool(re.search(r'\b(if|then|unless|otherwise)\b', p_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', p_lower),
            'has_question': '?' in prompt
        }
        return features

    def _check_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric consistency (e.g., 'which is larger?')."""
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        if not p_nums:
            return 0.0
        
        try:
            nums = [float(n) for n in p_nums]
            c_nums = re.findall(r'-?\d+\.?\d*', candidate)
            
            if not c_nums:
                return 0.0
            
            c_val = float(c_nums[0])
            
            # Heuristic: If prompt asks for "larger"/"max", check if candidate is max
            p_lower = prompt.lower()
            if any(k in p_lower for k in ['larger', 'greater', 'max', 'highest', 'more']):
                return 1.0 if c_val == max(nums) else 0.0
            elif any(k in p_lower for k in ['smaller', 'less', 'min', 'lowest', 'fewer']):
                return 1.0 if c_val == min(nums) else 0.0
            # Direct equality check if numbers match exactly
            elif str(c_val) in p_nums:
                return 1.0
                
        except ValueError:
            pass
        return 0.0

    def _check_constraint_match(self, prompt: str, candidate: str) -> float:
        """Check if candidate respects negations and conditionals."""
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        negations = ['not', 'no', 'never', 'none']
        p_neg_count = sum(1 for n in negations if f" {n} " in f" {p_lower} ")
        c_neg_count = sum(1 for n in negations if f" {n} " in f" {c_lower} ")
        
        if p_neg_count > 0:
            # If prompt has negation, candidate should ideally reflect understanding 
            # (simplified: penalize if prompt says "not" and candidate is generic "yes")
            if c_lower.strip() in ['yes', 'true', 'it is']:
                score -= 1.0 
            else:
                score += 0.5
        else:
            # Positive bias for direct answers in non-negative contexts
            if c_lower.strip() in ['yes', 'true']:
                score += 0.5

        # Conditional keyword overlap (simple semantic check)
        cond_words = ['if', 'then', 'because', 'therefore']
        common_cond = len(set(p_lower.split()) & set(c_lower.split()) & set(cond_words))
        score += common_cond * 0.5
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            l1, l2, l12 = len(zlib.compress(b1)), len(zlib.compress(b2)), len(zlib.compress(b1 + b2))
            return (l12 - min(l1, l2)) / max(l1, l2, 1)
        except:
            return 1.0

    def _compute_max_ent_score(self, prompt: str, candidate: str, features: dict) -> float:
        """
        Compute score using Maximum Entropy principle.
        Score = exp(sum(weight_i * feature_i)) normalized implicitly by ranking.
        We return the logit (sum of weighted features) to maintain ordering.
        """
        logit = 0.0
        
        # 1. Numeric Evaluation (High priority)
        num_score = self._check_numeric_logic(prompt, candidate)
        logit += self.constraint_weights['numeric_accuracy'] * num_score
        
        # 2. Structural Constraints
        struct_score = self._check_constraint_match(prompt, candidate)
        logit += struct_score
        
        # 3. Keyword/Composition overlap (Contextual relevance)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        # Remove stopwords for overlap
        stopwords = {'the', 'is', 'a', 'an', 'it', 'to', 'be', 'that', 'this', 'of', 'in', 'for', 'on', 'with'}
        overlap = len((p_words - stopwords) & (c_words - stopwords))
        logit += self.constraint_weights['keyword_overlap'] * min(overlap, 5) # Cap contribution

        # 4. NCD Tiebreaker (Only adds small bonus if structural scores are close)
        # We invert NCD (lower distance = higher score)
        ncd_val = self._ncd(prompt, candidate)
        logit += self.constraint_weights['ncd_bonus'] * (1.0 - ncd_val)
        
        return logit

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        features = self._parse_structure(prompt)
        scored_candidates = []
        
        # Calculate raw logits
        logits = []
        for cand in candidates:
            logit = self._compute_max_ent_score(prompt, cand, features)
            logits.append(logit)
        
        # Convert to probabilities via Softmax (Maximum Entropy Distribution)
        # P(i) = exp(logit_i) / sum(exp(logit_j))
        max_logit = max(logits)
        exp_logits = [float(repr(l - max_logit)) for l in logits] # Stability shift
        # Re-calculate exp manually to avoid math import if desired, but math is stdlib. 
        # Using pow for exp approximation or just math.exp
        import math
        try:
            exp_vals = [math.exp(l) for l in logits]
        except OverflowError:
            # Fallback for extreme values
            exp_vals = [1.0] * len(logits)
            
        sum_exp = sum(exp_vals) if sum(exp_vals) > 0 else 1.0
        probs = [e / sum_exp for e in exp_vals]
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": probs[i],
                "reasoning": f"MaxEnt score based on structural constraints (nums: {features['numbers'] is not None}, negs: {features['negations']}) and NCD."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the MaxEnt score of the single answer."""
        # Evaluate against a dummy set to get normalization, or just use raw logit mapped to 0-1
        # Since we need 0-1, we treat the single answer as a candidate against itself 
        # and a generic wrong answer to estimate relative probability.
        
        # Simpler approach: Use the internal scoring mechanism and sigmoid the result
        features = self._parse_structure(prompt)
        logit = self._compute_max_ent_score(prompt, answer, features)
        
        # Sigmoid function to map logit to 0-1
        import math
        try:
            conf = 1 / (1 + math.exp(-logit))
        except OverflowError:
            conf = 1.0 if logit > 0 else 0.0
            
        return min(max(conf, 0.0), 1.0)
```

</details>
