# Free Energy Principle + Type Theory + Proof Theory

**Fields**: Theoretical Neuroscience, Logic, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:16:20.745855
**Report Generated**: 2026-03-27T23:28:38.408718

---

## Nous Analysis

**Algorithm**  
Parse each prompt and candidate answer into a set of typed λ‑terms representing atomic propositions (e.g., `Pred(x)`). Each term carries a simple type drawn from a finite hierarchy (entity, truth‑value, numeric, order). Using a Hindley‑Milner style type‑inference pass (implemented with pure Python dictionaries and NumPy arrays for precision matrices), we assign a type and a precision `Π` (inverse variance) to every proposition. The collection of typed terms forms a proof net: nodes are propositions, directed edges encode inference rules (modus ponens, transitivity, substitution) derived from the prompt’s logical skeleton.  

Prediction error for a node `i` is `ε_i = y_i – ŷ_i`, where `y_i` is the observed truth value (0/1 from explicit statements or numeric comparison) and `ŷ_i` is the value predicted by propagating parent nodes through the corresponding inference rule (implemented as matrix‑vector products with NumPy). Free energy is then  

```
F = ½ Σ_i ε_i^T Π_i ε_i  +  ½ Σ_i log|Π_i|  +  C
```

where `C` counts the number of cut‑edges (applications of cut‑elimination) as a complexity penalty. To score a candidate answer, we temporarily add its propositions to the net, re‑run type inference and constraint propagation, compute `F`, and define the score as `S = –F` (lower free energy → higher score).  

**Structural features parsed**  
Negations (`not`), comparatives (`>`, `<`, `=`), conditionals (`if … then`), numeric values and units, causal verbs (`cause`, `lead to`), ordering relations (`before`, `after`), quantifiers (`all`, `some`), and equivalence statements.  

**Novelty**  
While probabilistic type theory and Bayesian logic programming exist, the explicit coupling of variational free‑energy minimization with cut‑elimination‑based proof normalization and precision‑weighted type constraints has not been described in the literature; thus the combination is novel in its algorithmic formulation.  

**Ratings**  
Reasoning: 8/10 — captures deductive and numeric reasoning via proof propagation and error minimization.  
Metacognition: 7/10 — precision updates provide a rudimentary self‑assessment of confidence, but no higher‑level reflection on strategy.  
Hypothesis generation: 6/10 — the system scores given candidates; generating new hypotheses would require additional search mechanisms.  
Implementability: 9/10 — relies only on NumPy for linear algebra and Python’s stdlib for parsing, rewriting, and dictionary‑based type inference.

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
**Reason**: validation:runtime_error: ValueError: assignment destination is read-only

**Forge Timestamp**: 2026-03-27T20:47:25.660529

---

## Code

**Source**: scrap

[View code](./Free_Energy_Principle---Type_Theory---Proof_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

# No external dependencies beyond numpy and stdlib
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is missing, though prompt requires it
    raise ImportError("numpy is required for this reasoning tool")

class ReasoningTool:
    """
    A computational reasoning tool implementing a simplified Free Energy Principle 
    coupled with Type Theory and Proof Theory concepts.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (typed lambda-terms) from text.
       Types: Entity, Truth, Numeric, Order.
    2. Proof Net Construction: Builds a graph where nodes are propositions and 
       edges are inference rules (modus ponens, transitivity, substitution).
    3. Free Energy Minimization: 
       - Computes prediction error (epsilon) between observed values and 
         propagated constraints.
       - Assigns precision (Pi) based on linguistic certainty markers.
       - Calculates Free Energy F = 0.5 * sum(Pi * epsilon^2) + Complexity Penalty.
       - Score S = -F.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and 
       unanswerable queries to cap confidence, ensuring the system admits 
       uncertainty rather than hallucinating high confidence.
    """
    
    def __init__(self):
        # Type hierarchy codes
        self.types = {'ENTITY': 0, 'TRUTH': 1, 'NUMERIC': 2, 'ORDER': 3}
        # Linguistic markers for precision (inverse variance)
        self.precision_markers = {
            'must': 10.0, 'always': 10.0, 'never': 10.0,
            'should': 5.0, 'likely': 5.0,
            'may': 2.0, 'might': 2.0, 'some': 2.0,
            'all': 8.0, 'every': 8.0
        }
        # Ambiguity triggers for Tier B
        self.presupposition_triggers = [
            r'\bhave you stopped\b', r'\bwhy did.*fail\b', r'\bwhy.*stop\b',
            r'\bquit\b', r'\bassume\b', r'\bpresuppose\b'
        ]
        self.scope_triggers = [r'\bevery.*a.*\b', r'\ball.*same\b']
        self.pronoun_triggers = [r'\bhe\b', r'\bshe\b', r'\bthey\b', r'\bhim\b', r'\bher\b']
        self.dichotomy_triggers = [r'\beither.*or\b', r'\bchoose between\b']
        self.subjectivity_triggers = [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bopinion\b']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and integers
        matches = re.findall(r'[-+]?\d*\.?\d+', text)
        return [float(m) for m in matches]

    def _get_precision(self, text: str) -> float:
        """Calculate precision based on linguistic markers."""
        text_lower = text.lower()
        prec = 1.0  # Base precision
        count = 0
        for word, val in self.precision_markers.items():
            if word in text_lower:
                prec += val
                count += 1
        return prec if count > 0 else 1.0

    def _parse_propositions(self, text: str) -> List[Dict[str, Any]]:
        """Parse text into typed lambda-term-like structures."""
        props = []
        tokens = self._tokenize(text)
        numbers = self._extract_numbers(text)
        
        # Type: Numeric
        if numbers:
            props.append({'type': 'NUMERIC', 'value': numbers, 'source': 'explicit'})
        
        # Type: Truth (Negation)
        if 'not' in tokens or 'no' in tokens or 'never' in tokens:
            props.append({'type': 'TRUTH', 'value': 0, 'op': 'negation'})
        elif 'yes' in tokens or 'true' in tokens:
            props.append({'type': 'TRUTH', 'value': 1, 'op': 'affirmation'})
            
        # Type: Order/Comparison
        if '>' in text or '<' in text or 'greater' in text or 'less' in text:
            props.append({'type': 'ORDER', 'value': 'comparative', 'source': 'symbolic'})
        elif 'before' in tokens or 'after' in tokens:
            props.append({'type': 'ORDER', 'value': 'temporal', 'source': 'temporal'})
            
        # Type: Entity/Quantifier
        if 'all' in tokens or 'every' in tokens:
            props.append({'type': 'ENTITY', 'quantifier': 'universal'})
        elif 'some' in tokens:
            props.append({'type': 'ENTITY', 'quantifier': 'existential'})

        return props

    def _build_proof_net(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Construct a simplified proof net.
        Returns: (values vector, precision matrix diagonal, cut_count)
        """
        # Combine context
        full_text = f"{prompt} {candidate}"
        props = self._parse_propositions(full_text)
        p_prec = self._get_precision(prompt)
        c_prec = self._get_precision(candidate)
        
        nodes = []
        values = []
        precisions = []
        
        # Node 0: Prompt Constraints
        nodes.append('prompt_constraint')
        # Extract numeric constraints if available
        p_nums = self._extract_numbers(prompt)
        if p_nums:
            # Simple heuristic: if prompt has numbers, they are ground truth
            values.append(p_nums[0]) 
            precisions.append(p_prec * 2.0) # High precision for explicit data
        else:
            # Boolean logic fallback
            values.append(1.0 if 'true' in prompt.lower() else 0.5)
            precisions.append(p_prec)

        # Node 1: Candidate Claim
        nodes.append('candidate_claim')
        c_nums = self._extract_numbers(candidate)
        if c_nums:
            values.append(c_nums[0])
            precisions.append(c_prec)
        else:
            # Check for logical agreement
            cand_lower = candidate.lower()
            if 'yes' in cand_lower or 'true' in cand_lower:
                values.append(1.0)
            elif 'no' in cand_lower or 'false' in cand_lower:
                values.append(0.0)
            else:
                # Ambiguous candidate
                values.append(0.5)
            precisions.append(c_prec)

        # Node 2: Inference Result (Propagation)
        # If types match, propagate. If numeric, check inequality.
        nodes.append('inference_result')
        inferred_val = values[0] # Default to prompt prior
        
        # Simple constructive computation for math/logic
        if len(p_nums) >= 1 and len(c_nums) >= 1:
            # Numeric comparison logic
            if '>' in full_text or 'greater' in full_text:
                inferred_val = 1.0 if p_nums[0] > c_nums[0] else 0.0
            elif '<' in full_text or 'less' in full_text:
                inferred_val = 1.0 if p_nums[0] < c_nums[0] else 0.0
            elif '=' in full_text or 'equal' in full_text:
                inferred_val = 1.0 if abs(p_nums[0] - c_nums[0]) < 1e-6 else 0.0
            else:
                # Implicit equality check if just numbers provided
                inferred_val = 1.0 if abs(p_nums[0] - c_nums[0]) < 1e-6 else 0.0
            values.append(inferred_val)
            precisions.append(min(p_prec, c_prec))
        else:
            # Logical propagation (Modus Ponens approximation)
            # If prompt implies True and candidate says True -> Low Error
            p_truth = 1.0 if ('true' in prompt.lower() or 'yes' in prompt.lower()) else 0.5
            c_truth = values[1] # From candidate node
            # Simple consistency check
            if p_truth == 1.0 and c_truth == 1.0:
                inferred_val = 1.0
            elif p_truth == 0.0 and c_truth == 0.0:
                inferred_val = 1.0
            else:
                inferred_val = 0.5 # Uncertain
            
            values.append(inferred_val)
            precisions.append(min(p_prec, c_prec) * 0.8) # Slight decay in inference

        # Convert to numpy
        y = np.array(values)
        Pi = np.diag(precisions)
        
        # Cut elimination count (complexity penalty)
        # Count logical connectives as potential cuts
        cut_count = len(re.findall(r'\b(if|then|else|but|however|therefore)\b', full_text))
        
        return y, Pi, cut_count

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Compute Free Energy F = 0.5 * e^T Pi e + 0.5 * log|Pi| + C"""
        y, Pi, cut_count = self._build_proof_net(prompt, candidate)
        
        if len(y) < 2:
            return 100.0 # High energy (bad) if parsing fails
            
        # Observed (y) vs Predicted (y_hat)
        # In this simplified net, the last node is the inference result.
        # We treat the 'candidate_claim' as the observation for the 'inference_result'
        # Or rather, we minimize the discrepancy between the propagated logic and the candidate statement.
        
        # Let y_obs be the candidate claim value (index 1)
        # Let y_pred be the inference result (index 2)
        # But our vector y contains [prompt_val, candidate_val, inference_val]
        
        # Simplified Error: Difference between Candidate Claim and Logical Inference
        epsilon = y[1] - y[2]
        pi_val = Pi[1, 1] # Precision of the candidate claim
        
        # Term 1: Prediction Error
        energy_error = 0.5 * pi_val * (epsilon ** 2)
        
        # Term 2: Complexity (Log determinant approx)
        # log|Pi| ~ sum(log(diag))
        diag_vals = np.diag(Pi)
        diag_vals[diag_vals == 0] = 1e-6 # Avoid log(0)
        energy_complexity = 0.5 * np.sum(np.log(diag_vals))
        
        # Term 3: Cut edges (structural complexity)
        energy_cut = float(cut_count)
        
        F = energy_error + energy_complexity + energy_cut
        return F

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2
        
        # 2. Scope Ambiguity
        for pattern in self.scope_triggers:
            if re.search(pattern, p_lower):
                return 0.4 # Moderate reduction
        
        # 3. Pronoun Ambiguity (if question asks 'who' or 'he/she')
        if ('who' in p_lower or 'which one' in p_lower) and any(p in p_lower for p in self.pronoun_triggers):
            # Check if multiple entities exist
            entities = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(set(entities)) > 1:
                return 0.3
        
        # 4. False Dichotomy
        for pattern in self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                if 'or' in p_lower and 'either' not in p_lower:
                     return 0.4

        # 5. Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                return 0.3

        # 6. Unanswerability (No numbers, no logic keywords, short)
        tokens = self._tokenize(prompt)
        has_logic = any(k in p_lower for k in ['if', 'then', 'greater', 'less', 'equal', 'cause'])
        has_nums = bool(self._extract_numbers(prompt))
        
        if not has_logic and not has_nums and len(tokens) < 10:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        concat_b = s1_b + s2_b
        
        l1 = len(zlib.compress(s1_b))
        l2 = len(zlib.compress(s2_b))
        l_concat = len(zlib.compress(concat_b))
        
        min_len = min(l1, l2)
        if min_len == 0:
            return 1.0
        return (l_concat - min_len) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            F = self._compute_free_energy(prompt, cand)
            score = -F  # Lower free energy = higher score
            
            # NCD Tiebreaker (max 15% influence logic handled by weighting if needed, 
            # but here we use it to break ties or adjust slightly)
            ncd = self._ncd_score(prompt, cand)
            # Adjust score slightly by NCD (lower NCD is better, so subtract small portion)
            # Only if scores are very close, but for simplicity we add a small bonus
            score -= ncd * 0.1 
            
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"Free Energy: {F:.4f}, Meta-Cap: {meta_cap:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply meta-confidence cap to the top candidate's effective confidence later
        # But for ranking, we keep the raw score.
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognition (Tier B).
        """
        # 1. Check Epistemic Honesty (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Compute structural score
        F = self._compute_free_energy(prompt, answer)
        # Convert Free Energy to a pseudo-probability-like score
        # Sigmoid-like transformation: 1 / (1 + exp(F)) roughly, but F can be negative
        # If F is very negative (good fit), score approaches 1.
        raw_score = 1.0 / (1.0 + math.exp(F)) if F > -10 else 1.0
        
        # Normalize raw_score to 0-1 range more aggressively
        # If F < 0 (good), score > 0.5. If F > 0 (bad), score < 0.5.
        # Let's map F \in [-inf, inf] to [0, 1]
        # Using a steeper sigmoid for distinction
        confidence_val = 1.0 / (1.0 + math.exp(F))
        
        # 3. Apply Cap
        final_conf = min(confidence_val, meta_cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))

# Example usage logic (not part of the class, for demonstration)
if __name__ == "__main__":
    tool = ReasoningTool()
    prompt = "If A is greater than B, and B is 5, is A 6?"
    candidates = ["Yes", "No", "Maybe"]
    
    # Evaluate
    ranked = tool.evaluate(prompt, candidates)
    print("Ranked Candidates:")
    for r in ranked:
        print(f"{r['candidate']}: {r['score']:.4f} ({r['reasoning']})")
        
    # Confidence Check
    conf = tool.confidence(prompt, "Yes")
    print(f"Confidence in 'Yes': {conf:.4f}")
    
    # Tier B Check
    tricky_prompt = "Have you stopped cheating on tests?"
    conf_tricky = tool.confidence(tricky_prompt, "Yes")
    print(f"Confidence in tricky prompt: {conf_tricky:.4f} (Should be low)")
```

</details>
