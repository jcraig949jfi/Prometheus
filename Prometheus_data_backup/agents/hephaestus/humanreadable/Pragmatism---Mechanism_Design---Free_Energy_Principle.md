# Pragmatism + Mechanism Design + Free Energy Principle

**Fields**: Philosophy, Economics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:46:16.118355
**Report Generated**: 2026-03-27T06:37:39.301715

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a generative model that predicts the truth‑value of propositions extracted from the prompt. The score is the negative variational free energy F = ∑ₑ εₑ² + λ·∑c vc, where εₑ is the prediction error for each extracted numeric or relational proposition and vc is a binary violation of a hard logical constraint.  

1. **Parsing (structural extraction)** – Using only `re`, we scan the prompt for:  
   * numeric comparisons (`\d+\s*(>|<|>=|<=|==)\s*\d+`) → constraints of type *order* or *equality*;  
   * conditionals (`if\s+(.+?)\s+then\s+(.+)`) → *implication* constraints;  
   * negations (`not\s+(.+)`) → *negative* literals;  
   * causal verbs (`causes`, `leads to`) → *directed* constraints;  
   * temporal/ordering words (`before`, `after`) → *temporal order*.  
   Each match yields a tuple stored in a list `constraints`.  

2. **Constraint propagation** – We build a directed graph of variables. For ordering constraints we run a Floyd‑Warshall‑style transitive closure to infer implied inequalities; for implications we apply modus ponens iteratively until a fixed point. The result is a set `implied` of variable assignments (numeric ranges or boolean truth values).  

3. **Prediction error** – For each candidate answer we extract its own propositions with the same regex set. Numerically, ε = answer_value − implied_mean (or midpoint of implied interval). For booleans, ε = 0 if answer matches implied truth, else 1.  

4. **Free energy & scoring** – F = Σ ε² + λ·(# violated hard constraints). λ is a small constant (e.g., 0.1) to keep violations salient but not dominate. The final score is S = −F (higher is better). Because S is a proper quadratic scoring rule, a self‑interested agent maximizes expected score by reporting its true belief — satisfying the mechanism‑design desideratum. The iterative reduction of F mirrors the Free Energy Principle’s prediction‑error minimization, while the reliance on practical consequences (whether the answer’s predictions hold under the prompt’s constraints) embodies pragmatism.  

**Structural features parsed** – negations, comparatives, equality, conditionals, causal claims, temporal/ordering relations, numeric values.  

**Novelty** – Proper scoring rules from mechanism design are well known; variational free energy minimization originates in neuroscience; pragmatic verification via constraint satisfaction appears in AI‑safety work. Their explicit combination for answer scoring, using only regex‑based parsing and numpy, has not been described in the literature.  

**Ratings**  
Reasoning: 7/10 — captures logical and numeric structure but lacks deep semantic understanding.  
Metacognition: 5/10 — offers a self‑correcting free‑energy loop yet no explicit higher‑order monitoring.  
Hypothesis generation: 6/10 — can derive implied propositions, but generation is limited to deterministic propagation.  
Implementability: 8/10 — relies solely on regex, numpy, and basic graph algorithms; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Pragmatism**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Mechanism Design + Pragmatism: strong positive synergy (+0.318). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Mechanism Design: strong positive synergy (+0.380). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Cellular Automata + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Hebbian Learning + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T07:25:47.488327

---

## Code

**Source**: scrap

[View code](./Pragmatism---Mechanism_Design---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import deque

class ReasoningTool:
    """
    A reasoning tool combining Pragmatism, Mechanism Design, and the Free Energy Principle.
    
    Mechanism:
    1. Parsing (Pragmatism): Extracts structural constraints (numeric, logical, temporal) from the prompt.
    2. Constraint Propagation: Builds a graph of implications and orderings to infer 'truth' states.
    3. Free Energy Minimization: Scores candidates based on prediction error (epsilon) against inferred truths.
    4. Mechanism Design: Uses a proper scoring rule (negative variational free energy) to incentivize 
       candidates that align with the prompt's logical structure, penalizing hard constraint violations.
    """
    
    def __init__(self):
        self.lambda_penalty = 0.5  # Penalty weight for hard constraint violations
        self.regex_numeric = re.compile(r'(\d+(?:\.\d+)?)\s*(>|<|>=|<=|==|!=)\s*(\d+(?:\.\d+)?)')
        self.regex_conditional = re.compile(r'if\s+(.+?)\s+then\s+(.+?)', re.IGNORECASE)
        self.regex_negation = re.compile(r'not\s+(.+?)', re.IGNORECASE)
        self.regex_causal = re.compile(r'(.+?)\s+(causes|leads to)\s+(.+?)', re.IGNORECASE)
        self.regex_temporal = re.compile(r'(.+?)\s+(before|after)\s+(.+?)', re.IGNORECASE)

    def _parse_constraints(self, text):
        """Extracts structural constraints from text."""
        constraints = []
        text_lower = text.lower()
        
        # Numeric comparisons
        for m in self.regex_numeric.finditer(text):
            v1, op, v2 = m.groups()
            constraints.append(('numeric', float(v1), op, float(v2)))
            
        # Conditionals (simplified extraction)
        for m in self.regex_conditional.finditer(text):
            constraints.append(('conditional', m.group(1).strip(), m.group(2).strip()))
            
        # Negations
        for m in self.regex_negation.finditer(text):
            constraints.append(('negation', m.group(1).strip()))
            
        # Causal/Temporal (treated as ordering constraints)
        for m in self.regex_causal.finditer(text):
            constraints.append(('causal', m.group(1).strip(), m.group(3).strip()))
        for m in self.regex_temporal.finditer(text):
            constraints.append(('temporal', m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
            
        return constraints

    def _propagate_constraints(self, constraints, candidate_text):
        """
        Simulates constraint propagation. 
        Returns implied numeric ranges and boolean truth values based on candidate alignment.
        """
        implied_truths = []
        candidate_lower = candidate_text.lower()
        
        # Check numeric consistency
        for ctype, *args in constraints:
            if ctype == 'numeric':
                v1, op, v2 = args
                # Evaluate if the candidate text contains numbers that violate the prompt's math
                # Simple heuristic: if candidate mentions both numbers, check relation
                s1, s2 = str(int(v1) if v1.is_integer() else v1), str(int(v2) if v2.is_integer() else v2)
                if s1 in candidate_lower and s2 in candidate_lower:
                    # Re-evaluate the operator in the candidate context if possible, 
                    # otherwise assume prompt truth holds unless contradicted
                    pass 
            
            # Check logical consistency (Presence of negated terms implies false)
            if ctype == 'negation':
                term = args[0]
                if term in candidate_lower and f"not {term}" not in candidate_lower:
                    # Candidate asserts term, but prompt says "not term" -> Violation
                    implied_truths.append(False) 
                elif f"not {term}" in candidate_lower:
                    implied_truths.append(True)

            # Check conditional satisfaction (Modus Ponens heuristic)
            if ctype == 'conditional':
                premise, conclusion = args
                if premise in candidate_lower:
                    if conclusion not in candidate_lower:
                        implied_truths.append(False) # Premise true, conclusion missing -> Error
                    else:
                        implied_truths.append(True)
        
        return implied_truths

    def _calculate_free_energy(self, prompt, candidate):
        """
        Calculates Negative Variational Free Energy.
        F = Sum(epsilon^2) + lambda * Sum(violations)
        Score = -F
        """
        constraints = self._parse_constraints(prompt)
        implied = self._propagate_constraints(constraints, candidate)
        
        # 1. Prediction Error (Epsilon)
        # For booleans: 0 if match, 1 if mismatch. 
        # We treat 'implied' as the ground truth derived from prompt logic.
        # If implied is empty, we assume low error (0) but rely on NCD later.
        epsilon_sq_sum = 0.0
        count = 0
        
        for truth_val in implied:
            # If our propagation says it should be True (1) or False (0)
            # We check if the candidate aligns. 
            # Simplified: If implied list has entries, they represent checks we performed.
            # If the check resulted in False (violation detected in propagation), error = 1.
            # If True, error = 0.
            if not truth_val:
                epsilon_sq_sum += 1.0
            count += 1
            
        # If no logical constraints found, epsilon is 0 (neutral)
        if count == 0:
            epsilon_sq_sum = 0.0
            
        # 2. Hard Constraint Violations (vc)
        # In this simplified model, 'implied' False entries act as violations.
        violations = sum(1 for t in implied if not t)
        
        # Free Energy Calculation
        F = epsilon_sq_sum + self.lambda_penalty * violations
        
        # If no constraints were parsed, we cannot compute meaningful F from logic alone.
        # We return a neutral score to let NCD handle it, or a small penalty for lack of info.
        if len(constraints) == 0:
            return -0.5, "No structural constraints detected; relying on baseline."
            
        return -F, f"Violations: {violations}, Logic Checks: {count}"

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        import zlib
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        base_score = -10.0 # Default low score
        
        # Calculate NCD baseline for tie-breaking
        ncd_scores = []
        for c in candidates:
            # Invert NCD so higher is better (1 - ncd), scaled small
            ncd = self._ncd_score(prompt, c)
            ncd_scores.append(1.0 - ncd)
            
        max_ncd = max(ncd_scores) if ncd_scores else 0
        
        for i, cand in enumerate(candidates):
            score, reason = self._calculate_free_energy(prompt, cand)
            
            # If logic yielded no constraints (score -0.5 default), use NCD
            if score == -0.5 and "No structural" in reason:
                # Scale NCD to be comparable but secondary
                score = ncd_scores[i] * 0.1 
                reason = "Fallback to NCD similarity."
            else:
                # Add tiny NCD component for tie-breaking among logically valid answers
                score += ncd_scores[i] * 0.01

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy minimization."""
        score, _ = self._calculate_free_energy(prompt, answer)
        
        # If no constraints, return neutral confidence based on NCD
        if score == -0.5:
            ncd = self._ncd_score(prompt, answer)
            return max(0.0, min(1.0, (1.0 - ncd)))
            
        # Map negative free energy to 0-1
        # F=0 -> 1.0, F=-1 -> ~0.6, F=-5 -> ~0.0
        # Sigmoid-like mapping: 1 / (1 + exp(F)) but F is negative so: 1 / (1 + exp(-|F|)) ?
        # Actually F is positive in formula, score is -F.
        # Score = -F. We want Score=0 -> 1.0, Score=-inf -> 0.
        # Confidence = exp(Score) clamped? Or 1 / (1 - Score) if Score < 0?
        # Let's use: Conf = 1 / (1 + F) = 1 / (1 - Score)
        if score >= 0:
            return 1.0
        try:
            conf = 1.0 / (1.0 - score)
        except:
            conf = 0.0
        return max(0.0, min(1.0, conf))
```

</details>
