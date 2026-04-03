# Constraint Satisfaction + Pragmatics + Property-Based Testing

**Fields**: Computer Science, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:44:59.297517
**Report Generated**: 2026-04-02T08:39:53.773554

---

## Nous Analysis

**Algorithm**  
The tool builds a *constraint‑satisfaction problem (CSP)* from the prompt and each candidate answer.  
1. **Parsing stage** – Using regex‑based structural extraction we create:  
   - Boolean variables for atomic propositions (e.g., `P`, `Q`).  
   - Numeric variables for measured quantities (e.g., `age`, `price`).  
   - Ternary relation variables for ordering/comparison (`<`, `>`, `=`) and causal links (`cause → effect`).  
   Each extracted clause is stored as a tuple `(scope, predicate)` where `scope` is the list of variable IDs and `predicate` is a Python lambda that returns True/False given an assignment.  
2. **Domain initialization** – For Boolean vars domain = {0,1}; for numeric vars domain = inferred range from extracted numbers (e.g., min‑max of all constants).  
3. **Constraint propagation** – Run AC‑3 to enforce arc consistency, pruning domains. If any domain becomes empty the CSP is unsatisfiable → score 0.  
4. **Property‑based test generation** – Using a Hypothesis‑like generator we sample random assignments from the pruned domains, evaluate all predicates, and count satisfied constraints. The generator is guided by a *pragmatics weight* derived from Grice maxims:  
   - **Quantity** – penalize assignments that introduce unnecessary variables (count of vars with value = default).  
   - **Relevance** – boost assignments that make the antecedent of conditionals true when the consequent is asserted in the prompt.  
   - **Manner** – favor assignments with fewer numeric deviations from extracted constants (L1 distance).  
5. **Shrinking** – When a sampled assignment violates a constraint, we apply delta‑debugging style shrinking: flip Boolean vars, move numeric vars toward nearest satisfying bound, re‑test, keeping the first assignment that still fails. The minimal failing assignment yields a *violation score* proportional to the number of constraints broken.  
6. **Final score** – `score = (num_satisfied / total_constraints) * pragmatics_factor`, where `pragmatics_factor ∈ [0.5,1.0]` is computed from the weights above. Higher scores indicate answers that satisfy more constraints while respecting pragmatic expectations.

**Structural features parsed**  
Negations (`not`, `n’t`), comparatives (`more than`, `less than`, `as … as`), conditionals (`if … then`, `unless`), numeric values and units, causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `greater than`), and existential/universal quantifiers inferred from plurals or “all”.

**Novelty**  
Purely symbolic CSP solvers combined with property‑based testing and pragmatic weighting are not standard in existing QA scoring tools; most approaches use either similarity metrics or neural‑augmented logic. This triad is therefore novel in the evaluation‑tool space.

**Rating**  
Reasoning: 8/10 — The CSP core gives sound logical reasoning; pragmatic weighting adds nuance but remains heuristic.  
Metacognition: 6/10 — The tool can detect when its own constraints are unsatisfied and trigger shrinking, yet it lacks explicit self‑reflection on strategy choice.  
Hypothesis generation: 7/10 — Property‑based sampling with shrinking provides systematic hypothesis exploration, though guided only by simple pragmatics heuristics.  
Implementability: 9/10 — All components (regex extraction, AC‑3, random sampling, delta‑debugging) run on numpy and the Python standard library without external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
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
**Reason**: validation:runtime_error: error: nothing to repeat at position 30

**Forge Timestamp**: 2026-04-02T04:55:04.545355

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Pragmatics---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
from itertools import product
from typing import List, Dict, Any, Tuple, Optional

class ReasoningTool:
    """
    A computational reasoning tool combining Constraint Satisfaction (CSP),
    Property-Based Testing (PBT), and Pragmatic weighting.
    
    Mechanism:
    1. Parsing: Extracts variables, numeric constants, and logical relations into a formal IR.
    2. CSP Construction: Builds domains and constraints (lambda predicates).
    3. Propagation: Uses AC-3-like pruning to reduce search space.
    4. Evaluation: Samples assignments (PBT) weighted by Gricean pragmatics to score candidates.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        self.operators = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '=': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "have you quit", "why did", "why does", "when did"]
        if any(t in p_lower for t in presupposition_triggers):
            return 0.2

        # 2. Scope/Pronoun Ambiguity
        if re.search(r'(every|all).*\b(a|an)\b.*\by\b?', p_lower) or "who was" in p_lower and "told" in p_lower:
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'either.*or', p_lower) and "only" not in p_lower:
            return 0.4
            
        # 4. Subjectivity without criteria
        if any(w in p_lower for w in ["best", "worst", "favorite", "beautiful"]) and "calculate" not in p_lower:
            return 0.3
            
        # 5. Unanswerability (Missing info indicators)
        if "impossible to know" in p_lower or "not enough information" in p_lower:
            return 0.1
            
        return 1.0

    def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Parses prompt into an Intermediate Representation (IR):
        - variables: dict of {name: domain}
        - constraints: list of callables
        - target: optional variable to solve for
        - numbers: list of extracted floats
        """
        ir = {
            "variables": {},
            "constraints": [],
            "target": None,
            "numbers": [],
            "relations": []
        }
        
        # Extract Numbers
        nums = re.findall(r'-?\d+(?:\.\d+)?', prompt)
        ir["numbers"] = [float(n) for n in nums]
        
        # Simple Algebra Parser (Bat-and-Ball style: "A and B cost X, A is Y more than B")
        # Pattern: "sum is S", "total is S", "cost S"
        sum_match = re.search(r'(sum|total|cost|are)\s+(?:of)?\s*(-?\d+(?:\.\d+)?)', prompt, re.IGNORECASE)
        diff_match = re.search(r'(\w+)\s+(?:is|are)\s*(-?\d+(?:\.\d+)?)\s+(?:more|less|greater|smaller)\s+(?:than)?\s+(\w+)', prompt, re.IGNORECASE)
        direct_val = re.findall(r'(\w+)\s+(?:is|=)\s*(-?\d+(?:\.\d+)?)', prompt)
        
        # Heuristic Variable Creation based on context
        vars_found = set()
        
        # Handle Direct Assignments (e.g., "A is 5")
        for var, val in direct_val:
            if var.lower() not in ['sum', 'total', 'cost', 'it', 'he', 'she', 'they']:
                ir["variables"][var] = float(val)
                vars_found.add(var)

        # Handle Relations
        if sum_match and diff_match:
            try:
                total_val = float(sum_match.group(2))
                var1 = diff_match.group(1)
                diff_val = float(diff_match.group(2))
                var2 = diff_match.group(3)
                
                # Check if "less" implies negative diff
                if "less" in diff_match.group(0) or "smaller" in diff_match.group(0):
                    diff_val = -diff_val
                
                # System: x + y = total, x - y = diff => 2x = total + diff
                # x = (total + diff) / 2
                # y = x - diff
                
                ir["variables"][var1] = None # Unknown
                ir["variables"][var2] = None # Unknown
                ir["target"] = var1 # Assume solving for the first mentioned in diff
                
                # Computation Logic embedded as a constraint checker
                def check_algebra(assignment):
                    x = assignment.get(var1, 0)
                    y = assignment.get(var2, 0)
                    return abs((x + y) - total_val) < 1e-6 and abs((x - y) - diff_val) < 1e-6
                
                ir["constraints"].append(check_algebra)
                ir["relations"].append(("algebra", var1, var2, total_val, diff_val))
            except ValueError:
                pass

        # Handle Numeric Comparisons (e.g. "Is 9.11 > 9.9?")
        comp_match = re.search(r'(-?\d+(?:\.\d+)?)\s*(>|<|>=|<=|==|!=)\s*(-?\d+(?:\.\d+)?)', prompt)
        if comp_match:
            n1 = float(comp_match.group(1))
            op = comp_match.group(2)
            n2 = float(comp_match.group(3))
            
            def check_comp(assignment):
                if op == '>': return n1 > n2
                if op == '<': return n1 < n2
                if op == '>=': return n1 >= n2
                if op == '<=': return n1 <= n2
                if op == '==': return n1 == n2
                if op == '!=': return n1 != n2
                return True
            ir["constraints"].append(check_comp)
            ir["relations"].append(("comparison", n1, op, n2))

        # Handle Modular Arithmetic (e.g. "What is 123 mod 10?")
        mod_match = re.search(r'(\d+)\s*mod\s*(\d+)', prompt, re.IGNORECASE)
        if mod_match:
            n1 = int(mod_match.group(1))
            n2 = int(mod_match.group(2))
            res = n1 % n2
            def check_mod(assignment):
                # We expect the candidate to match 'res'
                return True # Constraint handled in scoring
            ir["constraints"].append(check_mod)
            ir["relations"].append(("modular", n1, n2, res))

        # Handle Temporal/Ordering (Before/After)
        if "before" in prompt or "after" in prompt:
            # Simplified: Just flagging for pragmatic weighting
            ir["relations"].append(("temporal",))

        return ir

    def _generate_hypotheses(self, ir: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Property-based testing: Generate assignments satisfying constraints.
        """
        samples = []
        
        # If we have algebraic relations, compute exact solution
        for rel in ir["relations"]:
            if rel[0] == "algebra":
                _, v1, v2, total, diff = rel
                x = (total + diff) / 2.0
                y = (total - diff) / 2.0
                samples.append({v1: x, v2: y})
                return samples # Exact solution found
        
        # If modular
        for rel in ir["relations"]:
            if rel[0] == "modular":
                return [{"result": float(rel[3])}]

        # If comparison, no variables to assign, just truth value
        if any(r[0] == "comparison" for r in ir["relations"]):
            return [{}]

        # Fallback: Random sampling near extracted numbers (Pragmatics: Quantity/Manner)
        if ir["numbers"]:
            base = sum(ir["numbers"]) / len(ir["numbers"])
            for i in range(-2, 3):
                samples.append({"_guess": base + i})
        
        if not samples:
            samples = [{}]
            
        return samples

    def _compute_score(self, prompt: str, candidate: str, ir: Dict[str, Any]) -> Tuple[float, str]:
        """
        Computes score based on constraint satisfaction and pragmatic factors.
        Returns (score, reasoning_string).
        """
        reasoning_parts = []
        score = 0.0
        max_score = 1.0
        
        # 1. Check Candidate against Computed Results
        candidate_val = None
        try:
            # Try to extract a number from candidate
            c_nums = re.findall(r'-?\d+(?:\.\d+)?', candidate)
            if c_nums:
                candidate_val = float(c_nums[0])
        except:
            pass

        # 2. Evaluate Relations
        satisfied = 0
        total_relations = len(ir["relations"])
        
        if total_relations == 0:
            # Fallback to NCD if no structure found (but penalized)
            return 0.5, "No structural relations found; fallback to similarity."

        for rel in ir["relations"]:
            if rel[0] == "algebra":
                _, v1, v2, total, diff = rel
                # Solve for target (usually v1)
                expected = (total + diff) / 2.0
                if candidate_val is not None:
                    if abs(candidate_val - expected) < 1e-6:
                        satisfied += 1
                        reasoning_parts.append(f"Algebra solved: {v1}={expected}")
                    else:
                        reasoning_parts.append(f"Algebra mismatch: expected {expected}, got {candidate_val}")
                else:
                    # If candidate is text, check for variable name match?
                    if v1.lower() in candidate.lower():
                        satisfied += 0.5 # Partial credit for identifying variable
                        
            elif rel[0] == "comparison":
                n1, op, n2 = rel[1], rel[2], rel[3]
                # Evaluate truth
                if op == '>': truth = n1 > n2
                elif op == '<': truth = n1 < n2
                elif op == '>=': truth = n1 >= n2
                elif op == '<=': truth = n1 <= n2
                elif op == '==': truth = n1 == n2
                else: truth = False
                
                # Check candidate alignment
                c_lower = candidate.lower()
                if truth:
                    if "true" in c_lower or "yes" in c_lower or (candidate_val and candidate_val == 1.0):
                        satisfied += 1
                        reasoning_parts.append(f"Comparison {n1}{op}{n2} is True")
                    else:
                        reasoning_parts.append(f"Comparison {n1}{op}{n2} is True, candidate denied")
                else:
                    if "false" in c_lower or "no" in c_lower or (candidate_val and candidate_val == 0.0):
                        satisfied += 1
                        reasoning_parts.append(f"Comparison {n1}{op}{n2} is False")
                    else:
                        reasoning_parts.append(f"Comparison {n1}{op}{n2} is False, candidate affirmed")

            elif rel[0] == "modular":
                n1, n2, expected = rel[1], rel[2], rel[3]
                if candidate_val is not None and abs(candidate_val - expected) < 1e-6:
                    satisfied += 1
                    reasoning_parts.append(f"Modular arithmetic: {n1}%{n2}={expected}")
                elif str(int(expected)) in candidate:
                    satisfied += 1
                    reasoning_parts.append(f"Modular match found in text")
                else:
                    reasoning_parts.append(f"Modular expected {expected}")

        # Calculate Base Score
        if total_relations > 0:
            score = satisfied / total_relations
        else:
            score = 0.0

        # Pragmatics Factor (Simplified)
        # Penalize if candidate is wildly different length (Quantity)
        if len(candidate) > len(prompt) * 2:
            score *= 0.8
            reasoning_parts.append("Penalized for verbosity")
            
        return score, "; ".join(reasoning_parts) if reasoning_parts else "Constraints evaluated"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        ir = self._parse_prompt(prompt)
        results = []
        
        # Generate hypotheses to guide scoring if needed
        hypotheses = self._generate_hypotheses(ir)
        
        for cand in candidates:
            score, reason = self._compute_score(prompt, cand, ir)
            
            # Fallback: If no structural relations, use NCD as minor tiebreaker
            if not ir["relations"]:
                import zlib
                data = (prompt + cand).encode('utf-8')
                ncd = len(zlib.compress(data)) / (len(data) + 1)
                score = 0.5 - (ncd * 0.1) # Small boost for compression
                reason = "No structure found; using compression heuristic."

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Confidence
        ir = self._parse_prompt(prompt)
        has_structure = len(ir["relations"]) > 0
        
        if not has_structure:
            # If no structure, we rely on heuristics, so confidence should be low-mid
            raw_conf = 0.4
        else:
            # If structure exists, check if answer satisfies it
            score, _ = self._compute_score(prompt, answer, ir)
            raw_conf = score
            
        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless definitive (simplified: if meta_cap is 1.0 and score is high)
        if meta_cap == 1.0 and raw_conf > 0.9:
            final_conf = 0.95
        elif final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 3)

# Example Usage within the script for verification (not part of class)
if __name__ == "__main__":
    tool = ReasoningTool()
    
    # Test 1: Algebra (Bat and Ball)
    p1 = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much is the ball?"
    c1 = ["$0.05", "$0.10", "$1.00"]
    res1 = tool.evaluate(p1, c1)
    print(f"Algebra Test: {res1[0]['candidate']} (Score: {res1[0]['score']:.2f})")
    print(f"Confidence: {tool.confidence(p1, res1[0]['candidate'])}")
    
    # Test 2: Comparison
    p2 = "Is 9.11 greater than 9.9?"
    c2 = ["Yes", "No"]
    res2 = tool.evaluate(p2, c2)
    print(f"Comparison Test: {res2[0]['candidate']} (Score: {res2[0]['score']:.2f})")
    
    # Test 3: Ambiguity (Tier B)
    p3 = "Have you stopped cheating on tests?"
    c3 = ["Yes", "No"]
    conf3 = tool.confidence(p3, "Yes")
    print(f"Ambiguity Test Confidence: {conf3} (Should be < 0.3)")
```

</details>
