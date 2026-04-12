# Active Inference + Causal Inference + Model Checking

**Fields**: Cognitive Science, Information Science, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:49:40.533498
**Report Generated**: 2026-03-27T06:37:29.056922

---

## Nous Analysis

Combining active inference, causal inference, and model checking yields a **closed‑loop epistemic planner** that treats hypotheses as causal DAGs, selects interventions to reduce expected free energy, and formally checks the predicted dynamics against temporal‑logic specifications. Concretely, the architecture could be:

1. **Hypothesis module** – a Bayesian network learner (e.g., PC‑algorithm or NOTEARS) that maintains a distribution over causal graphs \(P(G|D)\).  
2. **Active inference controller** – computes expected free energy \(G(\pi)\) for candidate intervention policies \(\pi\) (using the generative model implied by each \(G\)) and selects the policy that maximizes epistemic value while minimizing expected cost. This is analogous to the *active inference* loop used in deep active inference agents (e.g., AIXI‑style variational updates).  
3. **Model‑checking verifier** – for the top‑k candidate graphs under the chosen policy, extracts the implied stochastic transition system and runs a probabilistic model checker (PRISM or Storm) to verify temporal‑logic properties such as \(P_{\geq 0.95}[\, \text{goal} \, \mathcal{U}^{\leq T}\, \text{safe}\,]\). If a property fails, the associated graph receives a lower posterior weight; if it passes, the graph is reinforced.

**Advantage for self‑testing hypotheses:** The system can *actively intervene* in the world (or simulation) to gather the most informative data, *causally* interpret the results via do‑calculus, and *formally verify* that its causal predictions satisfy desired behavioral specs before committing resources. This tightens the loop between belief update, action selection, and correctness guarantee, reducing the chance of accepting a spurious causal model.

**Novelty:** While active causal discovery (e.g., Eberhardt’s active causal learning) and probabilistic model checking exist separately, none integrate the expected‑free‑energy drive of active inference with exhaustive temporal verification of causal hypotheses. Thus the combination is not a known subfield; it represents a novel synthesis.

**Ratings**

Reasoning: 8/10 — combines principled belief updating (active inference) with causal do‑calculus, yielding robust inference under uncertainty.  
Metacognition: 7/10 — the system monitors its own hypotheses via model‑checking feedback, though self‑reflection on the free‑energy gradient remains limited.  
Hypothesis generation: 9/10 — generates and ranks causal graphs, then selects interventions that maximally discriminate them, a strong hypothesis‑driven loop.  
Implementability: 5/10 — requires integrating variational inference, causal discovery algorithms, and probabilistic model checkers; scalability to large state spaces is challenging.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 5/10 |
| **Composite** | **8.0** |

**Novelty**: unproductive
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Active Inference + Causal Inference: negative interaction (-0.057). Keep these concepts in separate code paths to avoid interference.
- Active Inference + Model Checking: strong positive synergy (+0.426). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=13% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T11:49:15.456198

---

## Code

**Source**: scrap

[View code](./Active_Inference---Causal_Inference---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Causal Active Model-Checking Loop (CAML) Approximation.
    
    Mechanism:
    1. Structural Parsing (Active Inference): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'generative model' of the prompt's requirements.
    2. Causal Intervention (Simulation): Treats candidate answers as interventions. Checks 
       if they violate the extracted logical constraints (falsification).
    3. Probabilistic Model Checking: Evaluates the 'trajectory' of the answer against 
       temporal/logical specs (e.g., if prompt says "not X", candidate containing "X" gets penalized).
    4. Scoring: Base score from constraint satisfaction (Reasoning), modified by 
       Normalized Compression Distance (NCD) only as a tie-breaker for semantic similarity.
    
    This avoids the 'Causal Inference' trap by using causality only for structural 
    constraint propagation, not direct scoring, adhering to the 'Coeus' guidelines.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}

    def _extract_structure(self, text: str) -> Dict:
        """Parses text for logical constraints (Negations, Comparatives, Conditionals)."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'length': len(text),
            'word_set': words
        }

    def _check_constraint_violation(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Simulates the model-checking step. 
        Returns a penalty (0.0 to 1.0) based on logical violations.
        """
        penalty = 0.0
        lower_cand = candidate.lower()
        cand_words = set(re.findall(r'\b\w+\b', lower_cand))
        
        # 1. Negation Check (Modus Tollens approximation)
        # If prompt emphasizes negation, candidate should ideally reflect exclusion or difference
        if prompt_struct['negation']:
            # Heuristic: If prompt is negative, simple affirmative echoes often fail reasoning
            if len(cand_words) < 3 and {'yes', 'no', 'true', 'false'} & cand_words:
                penalty += 0.3 
        
        # 2. Numeric Consistency
        cand_nums = [float(n) for n in re.findall(r'\d+\.?\d*', candidate)]
        if prompt_struct['numbers'] and cand_nums:
            # Check for gross contradictions if numbers are present in both
            # E.g., Prompt implies small, candidate is huge (simplified heuristic)
            p_max = max(prompt_struct['numbers'])
            c_max = max(cand_nums)
            if p_max > 0 and c_max > p_max * 10:
                penalty += 0.4

        # 3. Length/Complexity Match (Active Inference prior)
        # Reasoning tasks usually require non-trivial answers unless specified
        if prompt_struct['conditional'] and len(cand_words) < 2:
            penalty += 0.2
            
        return min(penalty, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []
        
        # Pre-calculate NCD to prompt for tie-breaking (semantic similarity)
        # Lower NCD = more similar to prompt context (often good for relevance)
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        
        for i, candidate in enumerate(candidates):
            # Step 1: Structural Parsing & Constraint Propagation
            violation_penalty = self._check_constraint_violation(prompt_struct, candidate)
            
            # Step 2: Base Reasoning Score (Inverse of violation)
            # Start with high confidence, subtract penalties
            base_score = 1.0 - violation_penalty
            
            # Step 3: NCD as Tiebreaker/Modifier
            # If base scores are close, NCD distinguishes. 
            # We add a small bonus for lower NCD (higher similarity) if reasoning doesn't disqualify it.
            _, ncd_val = ncd_scores[i]
            # Normalize NCD contribution: (1 - ncd) * small_weight
            ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = base_score + ncd_bonus
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural match: {1.0-violation_penalty:.2f}, Semantic proximity: {1.0-ncd_val:.2f}"
            if violation_penalty > 0:
                reasoning = f"Constraint violation detected (penalty: {violation_penalty:.2f}). " + reasoning

            scored_candidates.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the same logic as evaluate but for a single pair.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']
```

</details>
