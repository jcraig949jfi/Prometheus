# Metacognition + Free Energy Principle + Sensitivity Analysis

**Fields**: Cognitive Science, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:45:47.111894
**Report Generated**: 2026-04-01T20:30:43.697121

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions \(p_i\) from the prompt and each candidate answer. Propositions carry a type flag: negation, comparative, conditional (antecedent → consequent), numeric equality/inequality, causal claim ( \(A\) causes \(B\) ), ordering ( \(A\) < \(B\) ). Store them in a list `props` and build a binary adjacency matrix `E` where `E[i,j]=1` if \(p_i\) and \(p_j\) share a variable or appear in the same clause (forming a Markov blanket).  
2. **Belief potentials** – Initialise a confidence vector `c = np.ones(len(props))*0.5`. For each proposition compute a prediction \(\hat{p}_i\) from its blanket using a simple logical rule:  
   - If \(p_i\) is a conditional and its antecedent is true (confidence > 0.5) then \(\hat{p}_i\)=consequent confidence, else 0.  
   - For numeric propositions, \(\hat{p}_i\) is the truth value obtained by evaluating the expression with current variable assignments (initially mid‑point).  
   Prediction error \(e_i = p_i - \hat{p}_i\) (where \(p_i\) is 1 if the proposition is asserted true in the text, 0 if asserted false, 0.5 if unknown).  
3. **Free energy** – Compute variational free energy \(F = \sum_i \frac{e_i^2}{2\sigma_i^2} + \frac{1}{2}\log\sigma_i^2\) with precision \(\sigma_i^{-2}=c_i\). This is a pure‑numpy operation.  
4. **Sensitivity‑driven weight update** – Perturb each input proposition by \(\delta=0.01\) and recompute \(F\); the finite‑difference gradient \(g_i = \partial F/\partial p_i\) estimates how sensitive the total error is to that proposition. Update confidence via metacognitive monitoring:  
   \(c_i \leftarrow \sigma(c_i - \eta \cdot g_i)\) where \(\sigma\) is a logistic squashing to \[0,1\] and \(\eta=0.1\). High sensitivity (large |g_i|) reduces confidence, reflecting unreliable input.  
5. **Strategy selection** – If the proportion of conditional/causal propositions > 0.3, activate a logical‑propagation step (apply modus ponens transitively using `E`); otherwise rely on numeric evaluation. The selected strategy influences which \(\hat{p}_i\) are recomputed in the next iteration.  
6. **Scoring** – After T = 5 iterations, the candidate’s score is \(S = -F + \lambda \sum_i c_i\) (\(\lambda=0.2\)). Lower free energy (better prediction) and higher metacognitive confidence increase the score.

**Parsed structural features** – Negations, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), numeric values and arithmetic expressions, causal claims (`causes`, `leads to`), ordering relations (`before/after`, `greater than/less than`), equality/inequality statements, and quantifiers (`all`, `some`) inferred from plural nouns.

**Novelty** – The triplet merges three well‑studied ideas: (1) Free Energy Principle as a prediction‑error objective, (2) Sensitivity analysis to dynamically weight propositions, and (3) Metacognitive confidence monitoring for error‑driven strategy selection. Existing tools (Markov Logic Networks, Probabilistic Soft Logic, or pure rule‑based solvers) use fixed weights or Bayesian inference; none combine online sensitivity‑based confidence updates with a variational free‑energy loss in a deterministic numpy‑only parser. Hence the combination is novel for lightweight reasoning evaluation.

**Ratings**  
Reasoning: 8/10 — captures logical and numeric constraints via prediction error minimization, yielding nuanced scores beyond simple similarity.  
Metacognition: 7/10 — confidence updates driven by sensitivity provide error monitoring, though limited to a scalar heuristic.  
Hypothesis generation: 6/10 — the method evaluates given candidates but does not generate new hypotheses; it only selects between deduction and numeric strategies.  
Implementability: 9/10 — relies solely on regex, numpy array ops, and basic control flow, fitting the constraint of no external models or APIs.

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
**Reason**: trap_battery_failed (acc=33% cal=32% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T15:43:16.265879

---

## Code

**Source**: scrap

[View code](./Metacognition---Free_Energy_Principle---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool implementing the Free Energy Principle (FEP) with Sensitivity Analysis
    and Metacognitive Monitoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (numeric, conditional, causal, negation) via regex.
    2. Belief Potentials: Initializes confidence and computes prediction errors based on logical blankets.
    3. Free Energy: Calculates variational free energy as a loss function (prediction error + complexity).
    4. Sensitivity Analysis: Perturbs inputs to estimate gradient of error w.r.t. propositions.
    5. Metacognition: Updates confidence scores based on sensitivity (high sensitivity -> low confidence).
    6. Strategy: Selects between logical propagation and numeric evaluation based on proposition types.
    
    Epistemic Honesty: Explicitly checks for Tier B traps (presuppositions, ambiguity) and caps confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'comparative': re.compile(r'(greater|less|more|fewer|larger|smaller|higher|lower)\s*(?:than)?|([<>]=?)'),
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then\s+)?(.+?)(?:\.|$)', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|none|most)\b', re.IGNORECASE),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+? (fail|stop|die)|when did .+? stop)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|them)\s+(was|is|were|are)\s+(wrong|right|guilty|told)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+? or .+?|must be .+? or .+?)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|ugliest)\b', re.IGNORECASE)
        }
        self.eta = 0.1
        self.lambda_score = 0.2
        self.iterations = 5

    def _extract_props(self, text: str) -> List[Dict]:
        """Extract atomic propositions with type flags."""
        props = []
        text_lower = text.lower()
        
        # Numeric extraction
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        for i, n in enumerate(nums):
            props.append({'type': 'numeric', 'value': n, 'text': str(n), 'idx': i})
            
        # Structural flags (boolean presence)
        if self.patterns['conditional'].search(text):
            props.append({'type': 'conditional', 'value': 1.0, 'text': 'conditional_clause', 'idx': len(props)})
        if self.patterns['causal'].search(text):
            props.append({'type': 'causal', 'value': 1.0, 'text': 'causal_claim', 'idx': len(props)})
        if self.patterns['negation'].search(text):
            props.append({'type': 'negation', 'value': 1.0, 'text': 'negation_found', 'idx': len(props)})
        if self.patterns['comparative'].search(text):
            props.append({'type': 'comparative', 'value': 1.0, 'text': 'comparative_found', 'idx': len(props)})
            
        # Default if nothing found
        if not props:
            props.append({'type': 'unknown', 'value': 0.5, 'text': text[:20], 'idx': 0})
            
        return props

    def _build_adjacency(self, props: List[Dict]) -> np.ndarray:
        """Build binary adjacency matrix E (Markov blanket approximation)."""
        n = len(props)
        E = np.zeros((n, n), dtype=int)
        if n == 0: return E
        
        # Simple connectivity: share variable type or adjacent in list
        for i in range(n):
            for j in range(i+1, n):
                if props[i]['type'] == props[j]['type']:
                    E[i, j] = E[j, i] = 1
                if abs(i - j) == 1:
                    E[i, j] = E[j, i] = 1
        return E

    def _compute_numeric_truth(self, prompt: str, answer: str) -> float:
        """Constructive computation for numeric/comparative questions."""
        # Extract numbers from prompt and answer
        p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        a_nums = [float(x) for x in self.patterns['numeric'].findall(answer)]
        
        if not p_nums and not a_nums:
            return 0.5 # No numeric content to evaluate
            
        # Heuristic: If prompt has 2 numbers and answer has 1, check basic ops
        if len(p_nums) >= 2 and len(a_nums) == 1:
            target = a_nums[0]
            n1, n2 = p_nums[0], p_nums[1]
            
            # Check sum, diff, prod, ratio
            ops = [n1+n2, n1-n2, n2-n1, n1*n2, n1/n2 if n2!=0 else 0, n2/n1 if n1!=0 else 0]
            # Check simple comparisons if answer is text like "greater"
            if any(word in answer.lower() for word in ['greater', 'larger', 'more']):
                return 1.0 if n1 > n2 else 0.0
            if any(word in answer.lower() for word in ['less', 'smaller', 'fewer']):
                return 1.0 if n1 < n2 else 0.0
                
            # Check if answer matches a calculation result (within tolerance)
            if any(abs(target - op) < 1e-6 for op in ops):
                return 1.0
            # Penalty for wrong number
            return 0.2
            
        # If answer repeats prompt numbers exactly, it might be echo (low score) or correct extraction
        if len(a_nums) > 0 and len(p_nums) > 0:
            if a_nums[0] in p_nums:
                return 0.6 # Plausible but needs verification
                
        return 0.5

    def _check_meta_confidence(self, text: str) -> Tuple[float, str]:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns (cap_value, reason_string).
        """
        text_lower = text.lower()
        
        if self.patterns['presupposition'].search(text):
            return 0.2, "Presupposition detected (unanswerable)"
        if self.patterns['false_dichotomy'].search(text) and 'or' in text_lower:
            # Only flag if it looks like a forced choice without exhaustiveness
            if 'either' in text_lower or 'must' in text_lower:
                return 0.3, "False dichotomy suspected"
        if self.patterns['subjectivity'].search(text):
            return 0.4, "Subjective criteria detected"
        if self.patterns['pronoun_ambiguity'].search(text) and 'who' in text_lower:
            return 0.3, "Pronoun ambiguity"
            
        return 1.0, "OK"

    def _run_fep_cycle(self, prompt: str, answer: str) -> float:
        """
        Core FEP + Sensitivity Analysis loop.
        Returns the final score S = -F + lambda * sum(c).
        """
        combined = f"{prompt} {answer}"
        props = self._extract_props(combined)
        if not props:
            return -10.0 # Penalty for no structure
            
        n = len(props)
        E = self._build_adjacency(props)
        
        # 1. Initialize confidence vector c
        c = np.ones(n) * 0.5
        
        # Initial truth values p_i (1 if asserted, 0.5 if unknown/implicit)
        # For this implementation, we assume the text asserts its own content as true (1.0)
        # unless it's a numeric proposition that needs evaluation.
        p_vals = np.array([1.0 if prop['type'] != 'numeric' else 0.5 for prop in props])
        
        # If numeric props exist, try to evaluate them constructively
        numeric_truth = self._compute_numeric_truth(prompt, answer)
        for i, prop in enumerate(props):
            if prop['type'] == 'numeric':
                p_vals[i] = numeric_truth

        # Strategy selection
        cond_count = sum(1 for p in props if p['type'] in ['conditional', 'causal'])
        use_logic = (cond_count / max(1, len(props))) > 0.3
        
        sigma_sq = np.ones(n) # Variance, initially 1
        
        for t in range(self.iterations):
            # 2. Prediction \hat{p}_i from blanket
            p_hat = np.zeros(n)
            for i in range(n):
                neighbors = np.where(E[i, :] == 1)[0]
                if len(neighbors) == 0:
                    p_hat[i] = 0.5 # Prior
                else:
                    # Simple logical rule: average neighbor confidence weighted by type match
                    neighbor_vals = p_vals[neighbors]
                    if use_logic and props[i]['type'] == 'conditional':
                        # Modus ponens approximation: if antecedent (neighbor) is high, consequent is high
                        p_hat[i] = np.max(neighbor_vals) 
                    else:
                        p_hat[i] = np.mean(neighbor_vals)
            
            # Prediction error e_i
            e = p_vals - p_hat
            
            # 3. Free Energy F
            # F = sum(e^2 / (2*sigma^2) + 0.5*log(sigma^2))
            # Avoid log(0)
            sigma_sq_safe = np.clip(sigma_sq, 1e-6, None)
            F = np.sum((e**2) / (2 * sigma_sq_safe) + 0.5 * np.log(sigma_sq_safe))
            
            # 4. Sensitivity-driven weight update
            # Perturb p_vals slightly to estimate gradient dF/dp
            delta = 0.01
            gradients = np.zeros(n)
            for i in range(n):
                p_perturbed = p_vals.copy()
                p_perturbed[i] += delta
                # Recompute error for this specific perturbation (simplified local gradient)
                # Note: Full re-run of prediction is expensive, approximating via local error change
                # d(e^2)/dp = 2*e * de/dp. Since e = p - p_hat, de/dp = 1.
                # So d(F)/dp ~ e / sigma^2
                gradients[i] = e[i] / sigma_sq_safe[i]
            
            # Update confidence: c_new = sigmoid(c_old - eta * gradient)
            # High gradient (sensitivity) reduces confidence if error is high
            c = 1 / (1 + np.exp(-(c - self.eta * gradients)))
            c = np.clip(c, 0.01, 0.99)
            
            # Update variance based on confidence (high confidence -> low variance)
            sigma_sq = (1 - c) + 0.1

        # 6. Scoring
        score = -F + self.lambda_score * np.sum(c)
        return float(score)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 1.0
        return (combined - max_len) / max_len

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive checks for ambiguity/traps.
        """
        # 1. Meta-confidence check (Tier B)
        cap, reason = self._check_meta_confidence(f"{prompt} {answer}")
        
        # 2. Structural/Computation Score
        fep_score = self._run_fep_cycle(prompt, answer)
        
        # Normalize FEP score to roughly 0-1 range (heuristic mapping)
        # FEP can be negative. Let's map [-10, 10] to [0, 1]
        base_conf = 1 / (1 + np.exp(-fep_score / 2))
        
        # 3. NCD Tiebreaker (Max 15% influence)
        # If FEP is uncertain, NCD might help slightly, but capped.
        ncd = self._ncd_score(prompt, answer)
        # Low NCD means similar. We want high score for good match.
        # But NCD is unreliable for reasoning. Use only if base_conf is middling.
        if 0.3 < base_conf < 0.7:
            base_conf = 0.8 * base_conf + 0.2 * (1 - ncd)
            
        final_conf = base_conf
        
        # Apply Cap
        if final_conf > cap:
            final_conf = cap
            
        return max(0.0, min(1.0, final_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by score."""
        results = []
        for cand in candidates:
            conf = self.confidence(prompt, cand)
            # Decompose score for transparency
            reasoning = "Structural match and numeric consistency evaluated via FEP."
            if conf < 0.3:
                reasoning = "Low confidence due to ambiguity, trap detection, or poor structural fit."
            elif conf > 0.8:
                reasoning = "High confidence: Strong numeric/logical alignment and no detected traps."
                
            results.append({
                "candidate": cand,
                "score": conf,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
```

</details>
