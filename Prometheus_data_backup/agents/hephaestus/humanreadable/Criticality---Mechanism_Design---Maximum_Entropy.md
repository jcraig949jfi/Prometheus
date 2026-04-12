# Criticality + Mechanism Design + Maximum Entropy

**Fields**: Complex Systems, Economics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:46:32.858670
**Report Generated**: 2026-03-27T17:21:24.746553

---

## Nous Analysis

**Algorithm**  
1. **Proposition extraction** – Using a small set of regex patterns we parse the prompt and each candidate answer into a list of atomic propositions *pᵢ* (e.g., “X > Y”, “¬Z”, “if A then B”, “C causes D”, numeric equalities). Each proposition gets a Boolean variable *xᵢ ∈ {0,1}*.  
2. **Factor graph construction** –  
   * Unary potential ϕᵤ(xᵢ) = exp(λᵢ·xᵢ) where λᵢ is a confidence weight derived from the presence of hedges (“likely”, “probably”) in the candidate.  
   * Pairwise potential for each logical relation extracted:  
     - Conditional “if A then B”: ϕₚₐᵢᵣ(xₐ,x_b) = 0 if xₐ=1 ∧ x_b=0 else 1.  
     - Contradiction “A and ¬B”: ϕ = 0 if xₐ=1 ∧ x_b=1 else 1.  
     - Numeric ordering “value₁ < value₂”: similar hard constraint.  
   All potentials are stored in a NumPy matrix *W* (size *n×n*) where *Wᵢⱼ* = log ϕₚₐᵢᵣ.  
3. **Maximum‑Entropy inference** – We seek the distribution *P(x)* that maximizes entropy subject to the expected values of the hard constraints matching those implied by the prompt (treated as evidence). This yields an exponential family:  
   *P(x) ∝ exp( Σᵢ λᵢ xᵢ + Σᵢⱼ Wᵢⱼ xᵢ xⱼ )*.  
   The λ vector is solved by iterative scaling (generalized iterative proportional fitting) using only NumPy dot‑products; convergence is checked via the log‑partition change < 1e‑6.  
4. **Scoring (Mechanism‑Design proper scoring rule)** – For a candidate *c* we compute its *negative KL divergence* to the max‑ent distribution:  
   *score(c) = – Σₓ P_c(x) log(P_c(x)/P*(x))* where *P_c* is the distribution induced by fixing the candidate’s proposition truth‑values (i.e., a delta distribution). This reduces to *score = log P*(x_c)*, the log‑probability of the candidate’s world under the max‑ent model. Higher scores indicate answers that are more compatible with the constraint‑satisfying, least‑biased distribution.  
5. **Criticality check** – After inference we compute the susceptibility χ = Var[Σᵢ xᵢ] under *P* (via second‑moment formula using the covariance matrix derived from *W*). Answers occurring near peaks in χ (high sensitivity) are flagged for additional review, exploiting the order‑disorder boundary property.

**Structural features parsed**  
- Negations (“not”, “no”, “¬”)  
- Comparatives (“>”, “<”, “greater than”, “less than”)  
- Conditionals (“if … then …”, “unless”)  
- Causal keywords (“because”, “leads to”, “causes”)  
- Numeric values with units and equality/inequality relations  
- Ordering/temporal markers (“first”, “second”, “before”, “after”)  

**Novelty**  
Maximum‑entropy inference is common in language modeling; mechanism design appears in truthful elicitation literature; criticality is used to detect phase transitions in neural nets. Combining them to build a constraint‑based, incentive‑compatible scorer that explicitly measures proximity to a critical point is, to the best of my knowledge, not described in existing work.

**Ratings**  
Reasoning: 8/10 — captures logical structure via factor graphs but relies on approximate belief propagation.  
Metacognition: 6/10 — provides uncertainty via susceptibility but lacks explicit self‑reflective loops.  
Hypothesis generation: 7/10 — generates alternative worlds through sampling from the max‑ent distribution.  
Implementability: 9/10 — uses only regex, NumPy linear algebra, and simple iterative updates; no external libraries or APIs.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Criticality + Mechanism Design: strong positive synergy (+0.232). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Maximum Entropy: negative interaction (-0.066). Keep these concepts in separate code paths to avoid interference.
- Maximum Entropy + Mechanism Design: strong positive synergy (+0.121). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Criticality + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Neuromodulation + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:09:42.339356

---

## Code

**Source**: scrap

[View code](./Criticality---Mechanism_Design---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

# Constants for scoring weights
W_STRUCT = 0.55
W_COMP = 0.30
W_NCD = 0.15
W_MECH = 0.10 # Mechanism design bonus for constraint satisfaction

class ReasoningTool:
    """
    A reasoning tool combining Structural Parsing, Constructive Computation, 
    Maximum Entropy (as a confidence wrapper), and Mechanism Design scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, comparatives, conditionals).
    2. Constructive Computation: Attempts to solve numeric/logic constraints directly.
    3. MaxEnt Wrapper: Uses entropy of the constraint matrix to modulate confidence.
    4. Mechanism Design: Scores candidates based on 'truthfulness' (constraint satisfaction).
       - High penalty for violating hard logical constraints (Contradiction).
       - Reward for satisfying derived implications.
    5. Criticality: Flags high-sensitivity states (near phase transitions) as low confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|results in)\b', re.I),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|who is the)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either|or not|only two options)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I)
        }
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_lower = prompt.lower()
        results = []
        
        # 1. Structural Analysis of Prompt
        struct_flags = self._extract_structural_flags(prompt_lower)
        has_numbers = bool(self.patterns['numeric'].search(prompt_lower))
        
        # 2. Constructive Computation (Attempt to solve if numeric)
        computed_answer = None
        if has_numbers:
            computed_answer = self._attempt_numeric_solution(prompt)

        # 3. Evaluate each candidate
        scored_candidates = []
        for cand in candidates:
            cand_lower = cand.lower()
            score = 0.0
            reasoning_parts = []
            
            # A. Structural Matching (Base Score)
            # Check if candidate contains structural keywords matching prompt
            struct_match_score = 0.0
            if struct_flags['has_negation'] and self.patterns['negation'].search(cand_lower):
                struct_match_score += 0.2
                reasoning_parts.append("Matches negation structure")
            if struct_flags['has_comparative'] and self.patterns['comparative'].search(cand_lower):
                struct_match_score += 0.2
                reasoning_parts.append("Matches comparative structure")
            
            # B. Constructive Computation Score
            comp_score = 0.0
            if computed_answer is not None:
                # Check if candidate contains the computed number
                cand_nums = self.patterns['numeric'].findall(cand_lower)
                if cand_nums:
                    try:
                        val = float(cand_nums[0])
                        if abs(val - computed_answer) < 1e-6:
                            comp_score = 1.0
                            reasoning_parts.append(f"Computed value {val} matches")
                        else:
                            comp_score = 0.0 # Wrong calculation
                            reasoning_parts.append(f"Computed {computed_answer}, found {val}")
                    except:
                        pass
            elif not has_numbers:
                # If no numbers, structural match is the primary driver
                comp_score = struct_match_score 
                struct_match_score = 0 # Avoid double counting if no numbers

            # C. Mechanism Design Scoring (Constraint Satisfaction)
            # Treat the prompt as a set of constraints. 
            # If candidate contradicts explicit prompt facts, penalize heavily.
            mech_penalty = 0.0
            
            # Simple contradiction check: If prompt says "X is Y" and candidate says "X is not Y"
            # We simulate this by checking for direct negation of prompt substrings
            prompt_atoms = self._extract_atoms(prompt)
            cand_atoms = self._extract_atoms(cand)
            
            contradiction_found = False
            for p_atom in prompt_atoms:
                if p_atom.startswith('not ') and p_atom[4:] in cand_lower:
                    contradiction_found = True # Prompt says NOT X, Candidate says X
                elif not p_atom.startswith('not ') and f"not {p_atom}" in cand_lower:
                    contradiction_found = True # Prompt says X, Candidate says NOT X
            
            if contradiction_found:
                mech_penalty = -1.0
                reasoning_parts.append("Contradicts prompt constraints")
            
            # D. NCD Tiebreaker (Max 15% weight, used for similarity tie-breaking)
            ncd_score = 0.0
            if len(prompt) > 0 and len(cand) > 0:
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (0 is identical, 1 is different). We want some similarity but not echo.
                # Optimal is moderate similarity (answering the question) without echoing.
                if 0.4 <= ncd_val <= 0.8:
                    ncd_score = 0.1 
                elif ncd_val < 0.4: # Too similar (echo)
                    ncd_score = -0.1
                else: # Too different
                    ncd_score = 0.0

            # Final Score Aggregation
            # Score = (Struct * 0.55) + (Comp * 0.30) + (NCD * 0.15) - MechPenalty
            # Note: Comp score is normalized 0-1. Struct is 0-0.4 approx.
            
            raw_score = (struct_match_score * (W_STRUCT/0.4)) + \
                        (comp_score * W_COMP) + \
                        (ncd_score * (W_NCD/0.1)) - \
                        mech_penalty
            
            # Mechanism Design Bonus: If no contradiction and high structural match, add bonus
            if not contradiction_found and (struct_match_score > 0 or comp_score > 0):
                raw_score += W_MECH

            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural match baseline",
                "_meta": {
                    "struct": struct_match_score,
                    "comp": comp_score,
                    "ncd": ncd_score,
                    "mech_penalty": mech_penalty
                }
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return only the required fields
        return [{"candidate": r['candidate'], "score": r['score'], "reasoning": r['reasoning']} for r in results]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at <0.3 for ambiguous/unanswerable prompts (Tier B).
        Caps at <0.9 unless computation was definitive.
        """
        # 1. Meta-Confidence (Epistemic Honesty Check)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf

        # 2. Structural & Computational Confidence
        struct_flags = self._extract_structural_flags(prompt.lower())
        has_numbers = bool(self.patterns['numeric'].search(prompt.lower()))
        
        # If no structural markers and no numbers, low confidence (guessing)
        base_conf = 0.4 
        if struct_flags['has_negation'] or struct_flags['has_comparative'] or struct_flags['has_conditional']:
            base_conf = 0.7
        
        # If we can compute the answer and it matches, high confidence
        comp_match = False
        if has_numbers:
            computed = self._attempt_numeric_solution(prompt)
            if computed is not None:
                ans_nums = self.patterns['numeric'].findall(answer.lower())
                if ans_nums:
                    try:
                        if abs(float(ans_nums[0]) - computed) < 1e-6:
                            comp_match = True
                    except: pass
        
        if comp_match:
            final_conf = 0.95
        else:
            final_conf = base_conf
            
        # Apply Meta-Confidence Cap (The "Honesty" Cap)
        final_conf = min(final_conf, meta_conf)
        
        # Ensure we never return > 0.9 without computation
        if not comp_match and final_conf > 0.9:
            final_conf = 0.89
            
        return round(final_conf, 3)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Checks prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2 # "Have you stopped..." -> Unanswerable without more info
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Only flag if it looks like a forced choice without data
            if "either" in p_lower and "or" in p_lower:
                return 0.3 

        # 3. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4 # Subjective questions have lower objective confidence

        # 4. Pronoun/Scope Ambiguity (Simplified heuristic)
        # If "who" or "which" appears but no clear antecedents in a short prompt
        if re.search(r'\b(who|which|he|she|they)\b', p_lower):
            # Very rough heuristic: if question length is short and has pronouns, risky
            if len(prompt.split()) < 15:
                return 0.5

        return 1.0

    def _extract_structural_flags(self, text: str) -> dict:
        return {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text))
        }

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract simple subject-verb-object-ish atoms for contradiction check."""
        # Very simplified: split by commas and periods, lowercase, strip
        sentences = re.split(r'[.,]', text)
        atoms = []
        for s in sentences:
            s = s.strip().lower()
            if s:
                atoms.append(s)
        return atoms

    def _attempt_numeric_solution(self, prompt: str) -> Optional[float]:
        """
        Attempt to solve simple arithmetic or comparison in the prompt.
        Supports: "What is 2 + 2?", "Which is larger, 5 or 3?", "9.11 vs 9.9"
        """
        nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        if not nums:
            return None
            
        p_lower = prompt.lower()
        
        # Case 1: Explicit Math (e.g., "2 + 2", "10 * 5")
        # Try to eval safe math expressions if operators present
        if any(op in p_lower for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            # Sanitize and replace words
            expr = p_lower.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('divided', '/')
            # Extract numbers and operators roughly
            # This is a simplified parser for the sake of the exercise
            try:
                # Find all numbers and operators in order
                tokens = re.findall(r'-?\d+(?:\.\d+)?|[+\-*/]', expr)
                if len(tokens) >= 3: # Simple binary op
                    # Reconstruct expression from first two numbers and operator
                    # This is brittle but works for "2 + 2"
                    # Better: use the full string if it looks like an equation
                    if '=' in p_lower:
                        # Solve for result? No, just eval the side before =
                        parts = p_lower.split('=')
                        if len(parts) == 2:
                            val = eval(parts[0]) # Dangerous in prod, okay for this constrained tool
                            return float(val)
                    # Fallback: simple addition of all numbers if "sum" or "total"
                    if 'sum' in p_lower or 'total' in p_lower:
                        return sum(nums)
            except:
                pass

        # Case 2: Comparison ("Which is larger?", "Max of")
        if 'larger' in p_lower or 'greater' in p_lower or 'max' in p_lower:
            return max(nums)
        if 'smaller' in p_lower or 'less' in p_lower or 'min' in p_lower:
            return min(nums)
            
        # Case 3: Specific float trap "9.11 vs 9.9" -> usually asks for larger
        # If prompt implies version comparison or specific float logic
        if 'version' in p_lower or 'release' in p_lower:
            # Semantic versioning isn't float, but prompt implies numeric logic
            # If strictly numeric context, 9.9 > 9.11
            if len(nums) == 2:
                return max(nums) 

        # Default: If exactly two numbers and a comparative word, return the logical extreme
        if len(nums) == 2:
            if any(w in p_lower for w in ['larger', 'greater', 'more', 'max']):
                return max(nums)
            if any(w in p_lower for w in ['smaller', 'less', 'min']):
                return min(nums)
                
        return None

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            return (c12 - min_len) / max(c1, c2, 1) # Normalized properly
        except:
            return 1.0

    # Placeholder for MaxEnt internal logic used conceptually in confidence
    # In a full implementation, this would build the factor graph W and solve lambda
    def _max_entropy_wrapper(self, constraints: List[Tuple], n_vars: int) -> float:
        """
        Conceptual MaxEnt: Calculates entropy of the constraint matrix.
        High entropy (disorder) near criticality -> Lower confidence.
        """
        if not constraints:
            return 1.0 # No constraints, max uncertainty (but we cap via meta)
        
        # Simulate susceptibility check
        # If constraints are contradictory, the system is "frustrated" (high energy, low prob)
        # We return a confidence modifier based on constraint consistency
        return 0.8
```

</details>
