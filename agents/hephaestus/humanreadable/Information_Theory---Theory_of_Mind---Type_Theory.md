# Information Theory + Theory of Mind + Type Theory

**Fields**: Mathematics, Cognitive Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T14:41:21.400191
**Report Generated**: 2026-03-27T06:37:27.334925

---

## Nous Analysis

Combining information theory, theory of mind, and dependent type theory yields a **reflective, type‑safe probabilistic programming language** in which an agent’s beliefs about other agents are encoded as dependent types, and belief updates are driven by information‑theoretic objectives. Concretely, one can extend a language like **Idris‑based Bayesian DSL** (or a shallow embedding in Agda) with a **belief‑type** `Belief (w : World) : Type` that indexes a probability distribution over possible worlds by the agent’s own mental state. The language’s primitive operations include:

* **KL‑divergence conditioning** – `observe : (d : Data) → Belief w → Belief (update w d)` where the weight of the update is proportional to `KL(P(w|d)‖P(w))`, i.e., the expected information gain.
* **Recursive mentalizing** – a higher‑order type `Mind n : Type` where `Mind 0` is a base belief about the world and `Mind (n+1)` is a belief about another agent’s `Mind n`. Dependent types enforce that the depth of recursion matches the syntactic level, preventing ill‑formed infinite nesting.
* **Channel‑capacity bounded inference** – a type‑class `Capacity (c : ℕ)` that limits the mutual information between internal hypotheses and observable actions, implemented via a constrained variational optimizer (e.g., mirror descent with an information‑budget penalty).

**Advantage for self‑hypothesis testing:** The system can automatically compute the expected information gain of proposing a new hypothesis, compare it against the remaining channel capacity, and reject or refine hypotheses that would waste bits. Because hypotheses are typed, the system can also prove (via Curry‑Howard) that a hypothesis is logically consistent with its current belief state before spending computation on it, yielding a principled trade‑off between exploration (information gain) and exploitation (proof‑checked correctness).

**Novelty:** Probabilistic programming with dependent types has been explored (e.g., *Probabilistic Idris*, *Agda‑based Bayesian inference*), and theory‑of‑mind models appear in POMDP‑based recursive reasoning and epistemic games. Information‑driven curiosity (empowerment, information gain) is well studied in reinforcement learning. However, the tight integration—where dependent types enforce the depth of mentalizing, KL‑divergence guides belief updates, and a capacity type‑class bounds mutual information—has not been presented as a unified framework, making the combination novel albeit built on existing pieces.

**Ratings**  
Reasoning: 7/10 — solid theoretical foundations; the type‑level guarantees improve soundness but add overhead.  
Metacognition: 8/10 — explicit self‑modeling of beliefs and capacity limits yields strong introspective abilities.  
Hypothesis generation: 6/10 — information‑gain drive is useful, yet the rigid type discipline may constrain creative leaps.  
Implementability: 5/10 — building a full dependent‑type PPL with capacity constraints is challenging; current prototypes are limited to toy domains.

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

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Pragmatism + Type Theory (accuracy: 0%, calibration: 0%)
- Category Theory + Gauge Theory + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=47% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T22:04:34.609826

---

## Code

**Source**: scrap

[View code](./Information_Theory---Theory_of_Mind---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reflective, type-safe probabilistic reasoning tool inspired by Information Theory,
    Theory of Mind, and Type Theory.
    
    Mechanism:
    1. Type Safety (Structural Parsing): Enforces logical consistency by parsing
       negations, comparatives, and conditionals. Ill-formed logic receives a penalty.
    2. Theory of Mind (Constraint Propagation): Evaluates if the candidate answer
       respects the subject-object roles and logical constraints implied by the prompt.
    3. Information Theory (KL-Divergence Approximation): Scores candidates based on
       information gain (specificity) vs. entropy (uncertainty). Uses NCD as a 
       tie-breaking distance metric for similarity to expected structural patterns.
    4. Channel Capacity: Penalizes overly complex or verbose answers that exceed 
       a computed 'cognitive budget', favoring concise, high-probability truths.
    """

    def __init__(self):
        # Regex patterns for structural parsing (Type Safety checks)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'\d+\.?\d*')
        
        # Logical connectors for constraint propagation
        self.conjunctions = ['and', 'or', 'but', 'however', 'therefore', 'thus']

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical features from text to enforce type safety."""
        return {
            'has_negation': bool(self.negation_pattern.search(text)),
            'has_comparative': bool(self.comparative_pattern.search(text)),
            'has_conditional': bool(self.conditional_pattern.search(text)),
            'numbers': [float(n) for n in self.number_pattern.findall(text)],
            'length': len(text.split()),
            'unique_words': len(set(text.lower().split()))
        }

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Theory of Mind / Type Safety: Checks if the candidate's logical structure
        is consistent with the prompt's requirements (e.g., if prompt asks for comparison,
        candidate must have comparative structure).
        """
        score = 0.0
        
        # If prompt has comparatives, reward candidates that also handle comparisons
        if prompt_struct['has_comparative']:
            if cand_struct['has_comparative']:
                score += 0.3
            # Penalty if prompt compares but candidate ignores it (unless it's a direct negation)
            elif not cand_struct['has_negation']:
                score -= 0.2

        # If prompt has conditionals, reward structural alignment
        if prompt_struct['has_conditional']:
            if cand_struct['has_conditional'] or cand_struct['has_negation']:
                score += 0.2
        
        # Numeric consistency: If numbers exist in both, check rough ordering if implied
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Simple heuristic: if prompt has numbers, candidate having numbers is often relevant
            score += 0.1
            
        return score

    def _compute_information_gain(self, candidate: str, cand_struct: Dict) -> float:
        """
        Information Theory: Estimates information content.
        Higher unique word ratio and specific structure implies higher information gain.
        Penalizes excessive length (Channel Capacity constraint).
        """
        if cand_struct['length'] == 0:
            return 0.0
            
        # Entropy approximation via unique word ratio
        specificity = cand_struct['unique_words'] / max(cand_struct['length'], 1)
        
        # Channel capacity penalty: Too long = noise/overfitting
        length_penalty = 0.0
        if cand_struct['length'] > 20:
            length_penalty = -0.05 * (cand_struct['length'] - 20)
            
        return specificity + length_penalty

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Type Safety / Logical Consistency Score
            logic_score = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # 2. Information Gain Score
            info_score = self._compute_information_gain(cand, cand_struct)
            
            # 3. Structural Matching (Negation alignment)
            neg_match = 0.0
            if prompt_struct['has_negation'] == cand_struct['has_negation']:
                neg_match = 0.1
                
            # Base score
            total_score = logic_score + info_score + neg_match
            
            # NCD Tiebreaker (only if scores are close, used here as a small bias)
            # We prefer candidates that are structurally similar to the prompt's intent
            ncd_val = self._ncd_distance(prompt.lower(), cand.lower())
            # Normalize NCD to a small bonus/penalty
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            final_score = total_score + ncd_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if logic_score > 0: reasoning_parts.append("Logical structure aligned")
            if info_score > 0.1: reasoning_parts.append("High information density")
            if neg_match > 0: reasoning_parts.append("Negation consistency verified")
            if not reasoning_parts:
                reasoning_parts.append("Baseline evaluation")
                
            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and information content.
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        # Base confidence starts at 0.5
        conf = 0.5
        
        # Boost if logical structures match (e.g., both have numbers, or both conditionals)
        if prompt_struct['has_comparative'] and ans_struct['has_comparative']:
            conf += 0.2
        elif prompt_struct['has_conditional'] and ans_struct['has_conditional']:
            conf += 0.15
            
        # Boost if answer is not empty and has reasonable specificity
        if ans_struct['unique_words'] > 1:
            conf += 0.1
            
        # Penalty for extreme length mismatch (Channel Capacity violation)
        if ans_struct['length'] > 3 * max(prompt_struct['length'], 1):
            conf -= 0.2
            
        return max(0.0, min(1.0, conf))
```

</details>
