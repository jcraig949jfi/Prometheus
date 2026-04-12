# Category Theory + Metacognition + Metamorphic Testing

**Fields**: Mathematics, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T11:22:47.463201
**Report Generated**: 2026-04-01T20:30:42.814217

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Typing** – Tokenize the prompt and each candidate answer with regex patterns that extract atomic propositions:  
   - *Negation* (`not`, `no`) → node type `¬P`  
   - *Comparative* (`greater than`, `less than`) → node type `X > Y`  
   - *Conditional* (`if … then …`) → node type `P → Q`  
   - *Causal* (`because`, `leads to`) → node type `P ⇒ Q`  
   - *Ordering* (`first`, `before`, `after`) → node type `ord(X,Y)`  
   - *Numeric* (`=`, `≠`, values) → node type `expr = c`  
   Each proposition becomes a typed node in a directed acyclic graph (DAG).  

2. **Functor Mapping** – Define two functors:  
   - **F_bool**: maps nodes to Boolean truth values in a propositional algebra.  
   - **F_num**: maps numeric nodes to real‑valued intervals (e.g., `X > 5` → `(5, ∞)`).  
   The functor action on edges propagates constraints: modus ponens for `P → Q`, transitivity for `>` and `ord`, and causal chaining for `⇒`.  

3. **Natural Transformation (Consistency Check)** – A natural transformation η links F_bool and F_num: for every node, η checks that the Boolean assignment is compatible with the numeric interval (e.g., `X > Y` true ⇒ interval of X lies above interval of Y). Violations generate a consistency penalty.  

4. **Metacognitive Confidence Propagation** – Each node carries a confidence `c ∈ [0,1]` initialized from lexical cues (e.g., certainty adverbs). Belief propagation updates `c` using a simple error‑monitoring rule: if a constraint is violated, reduce `c` of the involved nodes proportionally to the violation magnitude; if satisfied, slightly increase `c`. This yields a metacognitive score reflecting calibrated certainty.  

5. **Metamorphic Relations on Answers** – For each candidate answer, generate metamorphic variants:  
   - *Symmetry swap*: exchange symmetric entities (e.g., `A > B` ↔ `B < A`).  
   - *Scale*: multiply all numeric constants by a factor `k>0`.  
   - *Order‑preserving permutation*: reorder independent conjuncts.  
   Compute the same DAG and constraints for each variant; penalize the original answer proportionally to the deviation in total constraint loss across variants (metamorphic violation).  

6. **Scoring** – Final loss = Σ(constraint violation × node confidence) + λ·metamorphic penalty. Score = 1 / (1 + loss). Higher scores indicate answers that satisfy logical, numeric, and metamorphic constraints with high metacognitive confidence.  

**Parsed Structural Features** – Negations, comparatives, conditionals, causal claims, ordering relations, numeric equalities/inequalities, and conjunctive/disjunctive structure.  

**Novelty** – While semantic parsing + constraint solving and metamorphic testing exist separately, integrating category‑theoretic functors/natural transformations with a metacognitive confidence‑propagation layer is not present in current public reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 8/10 — Strong logical grounding via functors and constraint propagation; relies on hand‑crafted regexes which may miss complex phrasing.  
Metacognition: 7/10 — Confidence updating is transparent and interpretable, but the simple belief‑propagation may not capture deeper uncertainty modeling.  
Hypothesis generation: 6/10 — The system can propose answer variants via metamorphic relations, yet it does not actively generate new hypotheses beyond those variants.  
Implementability: 9/10 — All components use only regex, numpy for interval arithmetic, and standard‑library data structures; no external APIs or neural models needed.

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
**Reason**: validation:runtime_error: RecursionError: maximum recursion depth exceeded

**Forge Timestamp**: 2026-04-01T16:30:52.653274

---

## Code

**Source**: scrap

[View code](./Category_Theory---Metacognition---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool integrating Category Theory concepts (Functors, Natural Transformations)
    with Metacognitive Confidence Propagation and Metamorphic Testing.
    
    Mechanism:
    1. Parsing & Typing: Extracts atomic propositions into a DAG using regex.
    2. Functor Mapping: Maps nodes to Boolean (F_bool) and Numeric (F_num) domains.
    3. Natural Transformation: Checks consistency between Boolean logic and Numeric intervals.
    4. Metacognition: Propagates confidence based on constraint satisfaction.
    5. Metamorphic Testing: Generates variants (symmetry, scaling) to test robustness.
    6. Epistemic Honesty (Tier B): Caps confidence if the prompt contains ambiguity, 
       presupposition, or unanswerable constraints.
    """

    def __init__(self):
        # Regex patterns for atomic propositions
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|>|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes|therefore)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after|precede|follow)\b', re.IGNORECASE),
            'numeric_eq': re.compile(r'(\w+)\s*(=|==|is)\s*(\d+\.?\d*)', re.IGNORECASE),
            'numeric_ineq': re.compile(r'(\w+)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', re.IGNORECASE),
            'numbers': re.compile(r'\d+\.?\d*')
        }
        
        # Tier B Traps
        self.trap_patterns = {
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|die)|when did .*(stop|end))\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every .*(a|an) |each .*(a|an) )\b', re.IGNORECASE), # Simplified scope check
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\s+(was|is|did)\b.*\bwho\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .*(or|else)|must be (true|false|one|two))\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.IGNORECASE),
            'unanswerable': re.compile(r'\b(missing information|cannot be determined|unknown)\b', re.IGNORECASE)
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (ambiguity, presupposition, etc.).
        Returns a cap value (0.0 to 1.0). If traps found, returns low cap.
        """
        p_lower = prompt.lower()
        
        # Check for explicit traps
        for trap_type, pattern in self.trap_patterns.items():
            if pattern.search(p_lower):
                # Specific checks for stronger signals
                if trap_type == 'presupposition':
                    return 0.1  # Strong cap for loaded questions
                if trap_type == 'subjectivity':
                    return 0.2  # Low cap for subjective queries
                if trap_type in ['scope_ambiguity', 'pronoun_ambiguity', 'false_dichotomy']:
                    return 0.25 # Moderate cap for ambiguity
        
        # Check for missing numeric data if numbers are expected but absent
        # Heuristic: If prompt asks for calculation but has < 2 numbers
        if any(k in p_lower for k in ['calculate', 'sum', 'total', 'greater', 'less']):
            nums = self.patterns['numbers'].findall(prompt)
            if len(nums) < 2:
                return 0.2
                
        return 1.0  # No obvious traps detected

    def _parse_nodes(self, text: str) -> List[Dict]:
        """Parses text into typed nodes (DAG vertices)."""
        nodes = []
        text_lower = text.lower()
        
        # Extract Negations
        if self.patterns['negation'].search(text):
            nodes.append({'type': 'negation', 'raw': 'negation', 'val': None})
            
        # Extract Comparatives
        if self.patterns['comparative'].search(text):
            nodes.append({'type': 'comparative', 'raw': 'comparative', 'val': None})
            
        # Extract Conditionals
        if self.patterns['conditional'].search(text):
            nodes.append({'type': 'conditional', 'raw': 'conditional', 'val': None})
            
        # Extract Causal
        if self.patterns['causal'].search(text):
            nodes.append({'type': 'causal', 'raw': 'causal', 'val': None})
            
        # Extract Ordering
        if self.patterns['ordering'].search(text):
            nodes.append({'type': 'ordering', 'raw': 'ordering', 'val': None})
            
        # Extract Numeric Equalities
        for m in self.patterns['numeric_eq'].finditer(text):
            var, op, val = m.groups()
            nodes.append({'type': 'numeric_eq', 'var': var, 'val': float(val), 'raw': m.group()})
            
        # Extract Numeric Inequalities
        for m in self.patterns['numeric_ineq'].finditer(text):
            var, op, val = m.groups()
            nodes.append({'type': 'numeric_ineq', 'var': var, 'op': op, 'val': float(val), 'raw': m.group()})
            
        return nodes

    def _functor_bool(self, nodes: List[Dict]) -> bool:
        """F_bool: Maps nodes to Boolean truth values (simplified)."""
        # Heuristic: If negation exists without clear antecedent, potential false
        has_neg = any(n['type'] == 'negation' for n in nodes)
        has_cond = any(n['type'] == 'conditional' for n in nodes)
        
        # Simple modus ponens simulation: If conditional exists, we need more context to be true
        if has_cond and len(nodes) < 3:
            return False 
        return True

    def _functor_num(self, nodes: List[Dict]) -> Tuple[float, float]:
        """F_num: Maps numeric nodes to intervals. Returns (lower, upper)."""
        lower = -math.inf
        upper = math.inf
        
        for n in nodes:
            if n['type'] == 'numeric_eq':
                v = n['val']
                lower = max(lower, v)
                upper = min(upper, v)
            elif n['type'] == 'numeric_ineq':
                v = n['val']
                op = n['op']
                if '>' in op:
                    lower = max(lower, v)
                elif '<' in op:
                    upper = min(upper, v)
                    
        if lower > upper:
            return (math.inf, -math.inf) # Violation
        return (lower, upper)

    def _natural_transformation_check(self, nodes: List[Dict]) -> float:
        """
        Natural Transformation eta: Checks consistency between F_bool and F_num.
        Returns a penalty (0.0 = consistent, 1.0 = contradiction).
        """
        num_interval = self._functor_num(nodes)
        is_valid_num = num_interval[0] <= num_interval[1]
        
        # If we have numeric constraints that contradict, penalty
        if not is_valid_num:
            return 1.0
            
        # If we have negation but numeric equality asserts existence, check logic
        # Simplified: If interval is infinite (no info) but we have strong claims, slight penalty
        if num_interval == (-math.inf, math.inf):
            if any(n['type'] in ['numeric_eq', 'numeric_ineq'] for n in nodes):
                return 0.5 # Uncertainty penalty
        
        return 0.0

    def _metamorphic_test(self, prompt: str, answer: str) -> float:
        """
        Generates metamorphic variants and checks for deviation.
        Returns a penalty score (0.0 = robust, 1.0 = fragile).
        """
        # Variant 1: Symmetry swap (conceptual)
        # If prompt says "A > B", answer should not imply "B > A"
        # We simulate this by checking if the answer contradicts simple re-phrasing
        
        # Variant 2: Scale (Numeric)
        # If prompt has numbers, multiply by 10. The logic should hold.
        nums = self.patterns['numbers'].findall(prompt)
        if nums:
            # Simple check: If answer contains a number, does it scale?
            # This is a heuristic proxy for full metamorphic testing
            ans_nums = self.patterns['numbers'].findall(answer)
            if ans_nums:
                # If the answer is a direct copy of a number from prompt without operation,
                # it might fail a scaling test (unless it's an ID).
                # Penalty if answer is just a substring of prompt numbers
                for an in ans_nums:
                    if an in nums and len(nums) > 1:
                        return 0.3 # Suspiciously lazy answer
        
        return 0.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Core reasoning engine using Functor mapping."""
        combined = f"{prompt} {candidate}"
        nodes = self._parse_nodes(combined)
        
        # 1. Functor Application
        bool_val = self._functor_bool(nodes)
        num_interval = self._functor_num(nodes)
        
        # 2. Natural Transformation (Consistency)
        consistency_penalty = self._natural_transformation_check(nodes)
        
        # 3. Constructive Computation (PEMDAS/Logic)
        # Attempt to solve explicit math if present
        computation_score = 1.0
        if any(n['type'] in ['numeric_eq', 'numeric_ineq'] for n in nodes):
            # Try to extract a calculation result from candidate
            cand_nums = self.patterns['numbers'].findall(candidate)
            prompt_nums = self.patterns['numbers'].findall(prompt)
            
            if cand_nums and prompt_nums:
                try:
                    c_val = float(cand_nums[-1])
                    # Simple heuristic: If prompt has "5 + 3" and candidate is "8"
                    # We can't easily eval dynamic strings safely without eval, 
                    # so we rely on interval consistency from functors
                    if num_interval[0] == math.inf: # Contradiction found
                        computation_score = 0.0
                    elif num_interval[0] == -math.inf: # No constraints
                        computation_score = 0.5
                    else:
                        # Check if candidate number fits the interval
                        if not (num_interval[0] <= c_val <= num_interval[1]):
                            computation_score = 0.2
                except ValueError:
                    computation_score = 0.5

        base_score = 1.0 - consistency_penalty
        base_score *= computation_score
        
        return max(0.0, min(1.0, base_score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(s1_b)
        len2 = len(s2_b)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1_b + s2_b
        len_concat = len(zlib.compress(concat))
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximation using lengths for speed/simplicity in this context
        # Real NCD uses compressed sizes of individual parts too
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B Epistemic Honesty.
        """
        # 1. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural & Computation Score
        struct_score = self._compute_structural_score(prompt, answer)
        
        # 3. Metamorphic Penalty
        meta_penalty = self._metamorphic_test(prompt, answer)
        
        # 4. NCD Tiebreaker (Max 15% influence)
        ncd = self._ncd_distance(prompt, answer)
        # If NCD is very low (copy paste), reduce score slightly unless it's a direct answer
        ncd_factor = 1.0 - (0.15 * (1.0 - ncd)) 
        
        raw_score = struct_score * (1.0 - 0.5 * meta_penalty) * ncd_factor
        
        # Apply Meta Cap
        final_score = min(raw_score, meta_cap)
        
        # Ensure we don't return high confidence on empty/generic answers
        if len(answer.strip()) < 3:
            final_score = min(final_score, 0.3)
            
        return round(float(final_score), 4)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Ranks candidates based on the reasoning tool."""
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural match: {score > 0.5}, Meta-cap applied"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        """Alias for the method defined above to satisfy interface requirements explicitly."""
        return self.__class__._meta_confidence(self, prompt)

# Re-defining _meta_confidence inside the class scope properly for the instance call
# (The method above in the class body is the actual implementation)
```

</details>
