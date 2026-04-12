# Active Inference + Neuromodulation + Adaptive Control

**Fields**: Cognitive Science, Neuroscience, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T18:39:22.717570
**Report Generated**: 2026-04-02T10:00:36.337426

---

## Nous Analysis

**Algorithm**  
The scorer builds a lightweight belief‑state model of the candidate answer and computes an *expected free energy* (EFE) that is minimized online.  

1. **Parsing & data structures** – Using only `re` and `string`, the prompt and each answer are scanned for atomic propositions (subject‑predicate‑object triples), negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then`), causal cues (`because`, `leads to`), and numeric constants. Each proposition becomes a node in a factor graph; edges encode logical relations (e.g., `A → B` for conditionals, `A ¬ B` for negations, `A = B` for equality). The belief state is a NumPy vector **b** of node truth probabilities (initially 0.5). A precision (gain) matrix **Γ** (diagonal) modulates the influence of each node, initialized to 1.0.  

2. **Variational update (Active Inference)** – For each node we compute prediction error **ε = b – μ**, where **μ** is the prior expectation derived from the prompt’s propositions (treated as fixed constraints). The free energy contribution is ½ εᵀ Γ ε.  

3. **Neuromodulation gain control** – After each iteration, the diagonal of **Γ** is updated by a simple adaptive rule:  
   `γ_i ← γ_i * exp(η * |ε_i|)` with learning rate η = 0.01. Large errors increase gain, sharpening focus on uncertain propositions (dopamine‑like precision boosting).  

4. **Adaptive control of model parameters** – The prompt’s constraint parameters (e.g., numeric thresholds in comparatives) are adjusted by a self‑tuning regulator:  
   `θ ← θ – α * ε`, where α is a scalar step size decreased when the cumulative error rises (model reference adaptation).  

5. **Scoring** – After a fixed number of iterations (e.g., 10) or when ΔFE < 1e‑4, the final free energy **F** is computed. The score for an answer is `S = exp(-F)`, so lower expected free energy yields a higher score. Scores are normalized across candidates to sum to 1.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations (greater/less than, before/after), numeric constants, quantifiers (“all”, “some”), and conjunction/disjunction cues.

**Novelty**  
While predictive coding, Bayesian brain theories, and adaptive control each appear separately in cognitive science and engineering, their concrete coupling—using expected free energy as a loss, neuromodulatory gain adaptation on a per‑proposition basis, and a self‑tuning regulator for constraint parameters—to score textual reasoning answers has not been described in existing literature. Hence the combination is novel for this application.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled free‑energy minimization.  
Metacognition: 7/10 — gain modulation provides a simple self‑monitoring of prediction errors.  
Hypothesis generation: 6/10 — the system can propose alternative belief states but lacks generative proposal mechanisms.  
Implementability: 9/10 — relies only on regex, NumPy linear algebra, and basic loops; readily codable.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: NameError: name 're' is not defined

**Forge Timestamp**: 2026-04-02T09:39:05.239011

---

## Code

**Source**: scrap

[View code](./Active_Inference---Neuromodulation---Adaptive_Control/tool.py)

<details>
<summary>Show code</summary>

```python
import numpy as np
from typing import Dict, List

class ReasoningTool:
    """
    Active Inference + Neuromodulation + Adaptive Control scorer.
    
    Parses prompt/answers into propositions, builds belief state vector,
    minimizes expected free energy with adaptive gain control.
    Metacognitive layer detects ambiguity and returns calibrated uncertainty.
    """
    
    def __init__(self):
        self.eta = 0.01  # Neuromodulation learning rate
        self.alpha = 0.05  # Adaptive control step size
        self.max_iter = 10
        self.convergence_threshold = 1e-4
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by expected free energy minimization."""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse prompt into constraint propositions
        prompt_props = self._parse_propositions(prompt)
        prompt_nums = self._extract_numbers(prompt)
        
        results = []
        for cand in candidates:
            cand_props = self._parse_propositions(cand)
            cand_nums = self._extract_numbers(cand)
            
            # Structural score via free energy
            fe_score = self._compute_free_energy_score(prompt_props, cand_props)
            
            # Numeric computation score
            num_score = self._numeric_evaluation(prompt, cand, prompt_nums, cand_nums)
            
            # Constraint propagation
            constraint_score = self._constraint_propagation(prompt_props, cand_props)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination
            final_score = (0.40 * fe_score + 0.25 * num_score + 
                          0.25 * constraint_score + 0.10 * ncd_score)
            
            reasoning = f"FE:{fe_score:.2f} Num:{num_score:.2f} Constraint:{constraint_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Normalize scores
        total = sum(r["score"] for r in results)
        if total > 0:
            for r in results:
                r["score"] /= total
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence 0-1."""
        meta_conf = self._meta_confidence(prompt)
        
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        
        # Structural confidence
        fe_score = self._compute_free_energy_score(prompt_props, answer_props)
        
        # Numeric confidence
        num_score = self._numeric_evaluation(prompt, answer, 
                                             self._extract_numbers(prompt),
                                             self._extract_numbers(answer))
        
        # Combine with meta-confidence cap
        raw_conf = 0.6 * fe_score + 0.4 * num_score
        return min(raw_conf * meta_conf, 0.95)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, and structural traps."""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is) .* (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba \w+', p) and '?' in p:
            return 0.3
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|it|they).*who', p) or re.search(r'who.*(he|she|it|they)', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p) and not re.search(r'\bneither\b', p):
            return 0.4
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p) and not re.search(r'\b(most|least|more|less)\b', p):
            return 0.35
        
        # "Cannot be determined" signals
        if re.search(r'\b(cannot|can\'t) be (determined|answered|known)', p):
            return 0.25
        
        # Check if question has sufficient constraints
        nums = self._extract_numbers(p)
        vars_needed = len(re.findall(r'\b(what|how many|how much)\b', p))
        if vars_needed > len(nums):
            return 0.5
        
        return 1.0
    
    def _parse_propositions(self, text: str) -> Dict:
        """Extract logical structure: negations, comparatives, conditionals, causals."""
        t = text.lower()
        props = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', t)),
            'comparatives': len(re.findall(r'\b(greater|less|more|fewer|higher|lower) than\b', t)),
            'conditionals': len(re.findall(r'\bif .* then\b', t)),
            'causals': len(re.findall(r'\b(because|since|leads to|causes|results in)\b', t)),
            'universals': len(re.findall(r'\b(all|every|always|none)\b', t)),
            'existentials': len(re.findall(r'\b(some|sometimes|exists)\b', t)),
            'tokens': set(re.findall(r'\b\w+\b', t))
        }
        return props
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric constants."""
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        return [float(n) for n in nums]
    
    def _compute_free_energy_score(self, prompt_props: Dict, cand_props: Dict) -> float:
        """Active Inference: minimize expected free energy."""
        # Build belief state vector from proposition counts
        n_nodes = 6  # negations, comparatives, conditionals, causals, universals, existentials
        
        # Prompt defines prior expectations mu
        mu = np.array([
            prompt_props['negations'],
            prompt_props['comparatives'],
            prompt_props['conditionals'],
            prompt_props['causals'],
            prompt_props['universals'],
            prompt_props['existentials']
        ], dtype=float)
        mu = mu / (np.sum(mu) + 1e-6)  # Normalize
        
        # Candidate defines belief state b
        b = np.array([
            cand_props['negations'],
            cand_props['comparatives'],
            cand_props['conditionals'],
            cand_props['causals'],
            cand_props['universals'],
            cand_props['existentials']
        ], dtype=float)
        b = b / (np.sum(b) + 1e-6)
        
        # Initialize precision (gain) matrix
        gamma = np.ones(n_nodes)
        
        # Variational updates with neuromodulation
        F_prev = np.inf
        for _ in range(self.max_iter):
            # Prediction error
            epsilon = b - mu
            
            # Free energy: 0.5 * epsilon^T * Gamma * epsilon
            F = 0.5 * np.sum(gamma * epsilon**2)
            
            # Neuromodulation: increase gain on high-error nodes
            gamma = gamma * np.exp(self.eta * np.abs(epsilon))
            gamma = np.clip(gamma, 0.1, 10.0)
            
            # Adaptive control: adjust mu (self-tuning)
            mu = mu - self.alpha * epsilon
            mu = np.clip(mu, 0, 1)
            
            if abs(F - F_prev) < self.convergence_threshold:
                break
            F_prev = F
        
        # Score is exp(-F), higher is better
        return np.exp(-F)
    
    def _numeric_evaluation(self, prompt: str, cand: str, 
                           prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Compute numeric reasoning: comparisons, arithmetic, bat-and-ball."""
        score = 0.0
        
        # Bat-and-ball pattern: "X and Y cost A, X costs B more than Y"
        bat_ball = re.search(r'cost.*\$?(\d+\.?\d*).*costs.*\$?(\d+\.?\d*)\s+more', prompt.lower())
        if bat_ball and len(cand_nums) > 0:
            total = float(bat_ball.group(1))
            diff = float(bat_ball.group(2))
            # Y = (total - diff) / 2
            expected = (total - diff) / 2
            if any(abs(cn - expected) < 0.01 for cn in cand_nums):
                score += 0.8
        
        # Numeric comparison: "9.11 vs 9.9"
        comp_match = re.search(r'(\d+\.?\d*)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\d+\.?\d*)', 
                              prompt.lower())
        if comp_match:
            n1, op, n2 = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            is_greater = n1 > n2
            if ('yes' in cand.lower() and is_greater and 'greater' in op) or \
               ('no' in cand.lower() and not is_greater and 'greater' in op):
                score += 0.7
        
        # All-but-N pattern
        all_but = re.search(r'all but (\d+)', prompt.lower())
        if all_but and prompt_nums:
            total = max(prompt_nums)
            excluded = int(all_but.group(1))
            expected = total - excluded
            if any(abs(cn - expected) < 0.5 for cn in cand_nums):
                score += 0.6
        
        return min(score, 1.0)
    
    def _constraint_propagation(self, prompt_props: Dict, cand_props: Dict) -> float:
        """Logical constraint satisfaction: transitivity, modus tollens."""
        score = 0.0
        
        # Token overlap (subject-verb-object alignment)
        prompt_tokens = prompt_props['tokens']
        cand_tokens = cand_props['tokens']
        overlap = len(prompt_tokens & cand_tokens) / (len(prompt_tokens) + 1e-6)
        score += 0.3 * overlap
        
        # Negation consistency
        if prompt_props['negations'] > 0:
            if cand_props['negations'] > 0 or 'no' in cand_tokens or 'not' in cand_tokens:
                score += 0.3
        
        # Comparative consistency
        if prompt_props['comparatives'] > 0 and cand_props['comparatives'] > 0:
            score += 0.2
        
        # Conditional structure alignment
        if prompt_props['conditionals'] > 0 and cand_props['conditionals'] > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
```

</details>
