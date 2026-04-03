# Constraint Satisfaction + Gene Regulatory Networks + Mechanism Design

**Fields**: Computer Science, Biology, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:41:42.999265
**Report Generated**: 2026-04-02T08:39:53.756555

---

## Nous Analysis

**Algorithm**  
We treat each extracted proposition \(p_i\) as a variable \(v_i\) with domain \(D_i\): Boolean for factual claims, or a continuous interval for numeric quantities.  
1. **Constraint Satisfaction layer** – From the parsed text we build a binary constraint set \(C=\{c_{ij}\}\). Each \(c_{ij}\) encodes a logical relation (e.g., \(v_i = \neg v_j\), \(v_i < v_j + k\), \(v_i \Rightarrow v_j\)). Constraints are stored as tuples \((i,j,\text{type},\text{params})\) and checked with a penalty function \(pen(c_{ij},x)\) that returns 0 if the assignment \(x\) satisfies the constraint and a positive cost otherwise (e.g., 0/1 for Boolean, squared deviation for numeric).  
2. **Gene‑Regulatory‑Network layer** – We construct an influence matrix \(W\in\mathbb{R}^{n\times n}\) where \(W_{ij}>0\) denotes activation (e.g., \(v_i\) supports \(v_j\)), \(W_{ij}<0\) inhibition (e.g., \(v_i\) contradicts \(v_j\)), and 0 no direct effect. A bias vector \(b\) encodes priors from domain knowledge. Starting from a candidate answer vector \(x^{(0)}\) (the truth‑value/numeric assignment implied by the answer), we iteratively update:  
\[
x^{(t+1)} = \operatorname{clip}\big(\sigma(W x^{(t)} + b), D\big)
\]  
where \(\sigma\) is a logistic squashing function and \(\clip\) enforces domain bounds. The iteration proceeds until \(\|x^{(t+1)}-x^{(t)}\|_1<\epsilon\); the fixed point \(x^*\) is the attractor representing the maximally coherent state under the network’s regulatory logic.  
3. **Mechanism‑Design layer** – The score for a candidate answer is designed to incentivize alignment with both the constraint set and the attractor:  
\[
S(x) = -\Big(\alpha\!\sum_{c_{ij}\in C}pen(c_{ij},x) \;+\; \beta\|x-x^*\|_2^2\Big)
\]  
with \(\alpha,\beta>0\). Lower constraint violation and proximity to the attractor yield a higher (less negative) score. All operations use NumPy arrays for \(W\), \(x\), and vectorized penalty computation.

**Parsed structural features**  
- Negations (“not”, “no”) → \(\neg\) constraints.  
- Comparatives (“greater than”, “less than”, “equal to”) → inequality constraints on numeric variables.  
- Conditionals (“if … then …”, “unless”) → implication constraints.  
- Causal claims (“because”, “leads to”, “results in”) → directed activation/inhibition edges in \(W\).  
- Quantifiers (“all”, “some”, “none”) → universal/existential constraints translated to pairwise relations.  
- Ordering relations (“before”, “after”, “precedes”) → temporal inequality constraints.  
- Numeric values with units → continuous domains and associated constraints.

**Novelty**  
Constraint satisfaction and gene‑regulatory‑network dynamics are well‑studied individually, and mechanism design is standard in economics. Their conjunction—using a GRN‑style attractor computation to define a consistency baseline, then scoring answers via a mechanism‑design‑inspired loss that penalizes both constraint violations and deviation from that attractor—has not been applied to automated answer scoring in the literature, making the combination novel for this task.

**Rating**  
Reasoning: 8/10 — The algorithm explicitly models logical and numeric dependencies, capturing multi‑step reasoning through constraint propagation and attractor convergence.  
Metacognition: 6/10 — While the method detects internal inconsistencies, it does not explicitly monitor confidence or uncertainty about its own inferences.  
Hypothesis generation: 5/10 — The framework evaluates given candidates but does not generate new hypotheses; it only scores supplied answers.  
Implementability: 9/10 — All components (regex parsing, NumPy matrix ops, fixed‑point iteration) rely solely on NumPy and the Python standard library, making straightforward implementation feasible.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=8% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T04:51:50.408441

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Gene_Regulatory_Networks---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Constraint Satisfaction, Gene Regulatory Networks (GRN),
    and Mechanism Design to evaluate answer candidates.
    
    Mechanism:
    1. Parsing: Extracts variables, numeric values, and logical relations (negation, implication).
    2. CSP Layer: Defines hard constraints between variables.
    3. GRN Layer: Uses an influence matrix to propagate truth values to a fixed-point attractor.
    4. Mechanism Design: Scores candidates based on constraint violation penalty and distance to the GRN attractor.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 50
        # Weights for the scoring mechanism
        self.alpha = 1.0  # Constraint violation penalty weight
        self.beta = 0.5   # Attractor deviation weight
        
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _parse_text(self, text: str) -> Dict:
        """Extracts variables, numeric values, and logical markers."""
        text_lower = text.lower()
        data = {
            "variables": [],
            "numbers": [],
            "negations": 0,
            "conditionals": 0,
            "comparatives": 0,
            "has_presupposition": False,
            "has_ambiguity": False,
            "raw_text": text
        }
        
        # Extract numbers (integers and floats)
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        data["numbers"] = [float(n) for n in nums]
        
        # Detect logical markers
        if any(w in text_lower for w in ["not", "no ", "never", "none"]):
            data["negations"] = 1
        if any(w in text_lower for w in ["if", "then", "unless", "implies"]):
            data["conditionals"] = 1
        if any(w in text_lower for w in ["greater", "less", "more", "fewer", "equal", "than"]):
            data["comparatives"] = 1
            
        # Meta-confidence checks (Tier B)
        # 1. Presupposition
        presup_patterns = [r"have you stopped", r"why did.*fail", r"why.*stop", r"when did.*stop"]
        if any(re.search(p, text_lower) for p in presup_patterns):
            data["has_presupposition"] = True
            
        # 2. Scope/Pronoun Ambiguity (Simplified heuristics)
        if re.search(r"every.*a\s+\w+", text_lower) and "same" not in text_lower:
            data["has_ambiguity"] = True # Potential scope ambiguity
        if re.search(r"told.*he\s+was|told.*she\s+was", text_lower):
            data["has_ambiguity"] = True # Pronoun ambiguity
            
        # 3. False Dichotomy
        if re.search(r"either.*or", text_lower) and "only" not in text_lower:
             # Heuristic: if "either/or" exists but doesn't explicitly say "only two options"
             # We flag it cautiously.
             pass # Keeping strictness low to avoid false positives on valid dichotomies
             
        # 4. Subjectivity
        subj_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in text_lower for w in subj_words) and "measure" not in text_lower:
             data["has_ambiguity"] = True

        return data

    def _build_grn(self, n: int, prompt_data: Dict, candidate_data: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Constructs the influence matrix W and bias vector b.
        Activation (+) supports, Inhibition (-) contradicts.
        """
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        # Initialize biases from candidate extraction (prior belief)
        # If candidate has numbers matching prompt, strong prior
        p_nums = set(prompt_data.get("numbers", []))
        c_nums = set(candidate_data.get("numbers", []))
        
        # Simple heuristic: If candidate repeats prompt numbers, slight activation
        # This is a placeholder for more complex semantic extraction
        overlap = len(p_nums.intersection(c_nums))
        if overlap > 0:
            b[:] = 0.1 * overlap
            
        # Construct edges based on logical parsing
        # If prompt has negation and candidate implies affirmation, inhibit
        if prompt_data["negations"] > 0:
            # Inhibit variables that look like direct affirmations of the negated concept
            # Since we don't have full NLP, we apply a global inhibition to 'truth' if negation is detected 
            # but the candidate looks positive (heuristic)
            if "not" not in candidate_data["raw_text"].lower() and "no" not in candidate_data["raw_text"].lower():
                # If prompt says "X is not Y" and candidate says "X is Y", inhibit.
                # We simulate this by adding negative self-loops or cross terms if we had explicit vars.
                # Here we assume a single aggregated variable for simplicity in this abstract implementation
                if n > 0:
                    W[0, 0] = -0.5 # Self-inhibition if logic conflicts
                    
        # Comparative logic: If prompt has "A > B" and candidate has numbers, check consistency
        if prompt_data["comparatives"] > 0 and len(candidate_data["numbers"]) >= 2:
            nums = sorted(candidate_data["numbers"])
            # Enforce ordering constraint via mutual inhibition if out of order? 
            # Instead, we let the CSP layer handle the hard math, GRN handles coherence.
            # Add activation between consistent numeric claims
            if n >= 2:
                W[0, 1] = 0.5 # Assume first two vars support each other if consistent
                W[1, 0] = 0.5

        # Normalize W to ensure stability (spectral radius < 1 roughly)
        if n > 0:
            row_sums = np.abs(W).sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            W = W / row_sums * 0.9
            
        return W, b

    def _run_grn_dynamics(self, W: np.ndarray, b: np.ndarray, x0: np.ndarray) -> np.ndarray:
        """Iterates the GRN to a fixed point attractor."""
        x = x0.copy()
        for _ in range(self.max_iter):
            x_new = self._sigmoid(W @ x + b)
            # Clip to domain [0, 1] (Boolean/Probability)
            x_new = np.clip(x_new, 0, 1)
            if np.linalg.norm(x_new - x, 1) < self.epsilon:
                break
            x = x_new
        return x

    def _compute_constraints_penalty(self, prompt_data: Dict, candidate_data: Dict) -> float:
        """
        Calculates penalty based on logical and numeric constraints.
        Returns 0 if satisfied, positive cost otherwise.
        """
        penalty = 0.0
        p_nums = prompt_data["numbers"]
        c_nums = candidate_data["numbers"]
        
        # 1. Numeric Consistency (Constructive Computation)
        # If prompt implies a calculation (e.g., "2+2"), check if candidate matches
        # Simple heuristic: If prompt has 2 nums and candidate has 1, check if it's a sum/prod
        if len(p_nums) == 2 and len(c_nums) == 1:
            expected_sum = p_nums[0] + p_nums[1]
            expected_prod = p_nums[0] * p_nums[1]
            val = c_nums[0]
            # Allow small float error
            if abs(val - expected_sum) > 0.1 and abs(val - expected_prod) > 0.1:
                # If it's not a simple arithmetic relation, maybe it's a comparison
                # Check comparatives
                if "greater" in prompt_data["raw_text"] or "more" in prompt_data["raw_text"]:
                    if val <= max(p_nums): # Should be greater than max? Or specific?
                         # Hard to know exact relation without full NLP, so small penalty
                         penalty += 0.5
                elif "less" in prompt_data["raw_text"]:
                    if val >= min(p_nums):
                        penalty += 0.5
            else:
                # Match found
                pass 
        elif len(p_nums) > 0 and len(c_nums) > 0:
            # Check if candidate number exists in prompt (for factual retrieval)
            # If candidate introduces a completely new number unrelated to prompt math, slight penalty?
            # No, that's too aggressive. 
            # Instead, check explicit contradictions if we can infer them.
            pass

        # 2. Logical Negation
        # If prompt has "not" and candidate is a direct affirmative repetition without qualification
        if prompt_data["negations"] > 0:
            p_words = set(re.findall(r'\w+', prompt_data["raw_text"].lower()))
            c_words = set(re.findall(r'\w+', candidate_data["raw_text"].lower()))
            # Remove stop words
            stops = {'the', 'a', 'an', 'is', 'are', 'was', 'were'}
            p_core = p_words - stops
            c_core = c_words - stops
            
            # If candidate is almost identical to prompt but lacks negation words
            if len(p_core) > 3 and len(c_core) > 3:
                overlap = len(p_core.intersection(c_core)) / len(p_core.union(c_core))
                if overlap > 0.8: # High similarity
                    # Check if candidate contains negation
                    if not any(w in candidate_data["raw_text"].lower() for w in ["not", "no", "never"]):
                        penalty += 2.0 # Strong penalty for missing negation

        return penalty

    def _meta_confidence(self, prompt: str) -> float:
        """Checks prompt for ambiguity, presupposition, or unanswerability."""
        data = self._parse_text(prompt)
        
        if data["has_presupposition"]:
            return 0.1
        if data["has_ambiguity"]:
            return 0.2
        
        # Check for unanswerable patterns (e.g. missing info)
        if "who" in prompt.lower() or "when" in prompt.lower() or "where" in prompt.lower():
            if "context" not in prompt.lower() and len(prompt.split()) < 20:
                # Short question with no context provided in prompt string itself
                # We assume the prompt includes context if it's long enough
                if len(prompt) < 50: 
                    return 0.2 # Suspiciously short for a WH question
                    
        return 1.0 # Default high confidence if no red flags

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_data = self._parse_text(prompt)
        n_vars = max(1, len(prompt_data["numbers"]) + 2) # Ensure minimal dimension
        results = []
        
        # Pre-compute GRN structure based on prompt
        # We treat the "truth" as a variable influenced by the prompt
        W, b_base = self._build_grn(n_vars, prompt_data, {"numbers": [], "raw_text": ""})
        
        scores = []
        
        for cand in candidates:
            cand_data = self._parse_text(cand)
            
            # 1. Constraint Satisfaction Penalty
            pen = self._compute_constraints_penalty(prompt_data, cand_data)
            
            # 2. GRN Attractor Computation
            # Initialize state: 0.5 (uncertain) + bias from candidate presence
            x0 = np.ones(n_vars) * 0.5
            if cand_data["numbers"]:
                # Inject candidate numbers as initial bias for the first few vars
                for i, val in enumerate(cand_data["numbers"][:n_vars]):
                    # Normalize number to [0,1] roughly for the network
                    x0[i] = min(1.0, max(0.0, val / 10.0)) 
            
            # Dynamic bias based on candidate content
            b = b_base.copy()
            if prompt_data["negations"] and "not" not in cand.lower():
                # Reduce bias if candidate ignores negation
                b *= 0.5
                
            x_star = self._run_grn_dynamics(W, b, x0)
            
            # 3. Mechanism Design Score
            # Distance to attractor (assuming ideal attractor is close to x0 if consistent)
            # Actually, we score based on how stable the network is with this candidate
            # and how little it violates constraints.
            # Score = - (alpha * penalty + beta * deviation_from_coherence)
            
            # Heuristic for deviation: If the network settles to a state very different from input, it's incoherent
            deviation = np.linalg.norm(x_star - x0)
            
            raw_score = -(self.alpha * pen + self.beta * deviation)
            
            # Boost if numeric calculation matches exactly (Constructive)
            if len(prompt_data["numbers"]) == 2 and len(cand_data["numbers"]) == 1:
                if abs(cand_data["numbers"][0] - sum(prompt_data["numbers"])) < 1e-5:
                    raw_score += 5.0 # Strong reward for correct addition
                elif abs(cand_data["numbers"][0] - (prompt_data["numbers"][0] * prompt_data["numbers"][1])) < 1e-5:
                    raw_score += 5.0 # Strong reward for correct multiplication

            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"Penalty: {pen:.2f}, Deviation: {deviation:.2f}"
            })
            scores.append(raw_score)

        # Normalize scores to be more interpretable if needed, but ranking is key
        # Sort descending
        sorted_indices = np.argsort(scores)[::-1]
        ranked_results = [results[i] for i in sorted_indices]
        
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at < 0.3 if meta-analysis detects ambiguity or presupposition.
        Caps at < 0.9 unless computation produced a definitive answer.
        """
        # 1. Meta Confidence Check (Tier B)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
            
        # 2. Structural/Computation Check
        prompt_data = self._parse_text(prompt)
        answer_data = self._parse_text(answer)
        
        base_conf = 0.5
        
        # If we have numbers and the answer provides a computed result
        if len(prompt_data["numbers"]) >= 2 and len(answer_data["numbers"]) >= 1:
            # Check for exact arithmetic match
            p_nums = prompt_data["numbers"]
            a_num = answer_data["numbers"][0]
            
            is_sum = abs(a_num - sum(p_nums)) < 1e-5
            is_prod = abs(a_num - np.prod(p_nums)) < 1e-5
            is_diff = abs(a_num - (p_nums[0] - p_nums[1])) < 1e-5 if len(p_nums)>=2 else False
            
            if is_sum or is_prod or is_diff:
                base_conf = 0.95 # Definitive computational answer
            else:
                # If numbers exist but don't match simple math, lower confidence
                base_conf = 0.6
        
        # If no numbers, rely on structural match (negation handling)
        elif prompt_data["negations"] > 0:
            if "not" in answer.lower() or "no" in answer.lower():
                base_conf = 0.8
            else:
                base_conf = 0.4 # Likely wrong if missing negation
                
        # Cap at 0.9 if not a definitive computation (as per instructions)
        # "NEVER return > 0.9 unless computation produced a definitive answer"
        has_definitive_comp = (len(prompt_data["numbers"]) >= 2 and 
                               (abs(answer_data["numbers"][0] - sum(prompt_data["numbers"])) < 1e-5 if answer_data["numbers"] else False))
        
        if not has_definitive_comp:
            base_conf = min(base_conf, 0.89)
            
        # Final cap by meta confidence
        final_conf = min(base_conf, meta_conf)
        
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
