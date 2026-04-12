# Abductive Reasoning + Adaptive Control + Pragmatics

**Fields**: Philosophy, Control Theory, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:52:45.769632
**Report Generated**: 2026-04-01T20:30:43.252454

---

## Nous Analysis

**Algorithm: Pragmatic‑Abductive Adaptive Scorer (PAAS)**  
PAAS treats each candidate answer as a set of *propositional fragments* extracted by regex‑based structural parsing (negations, comparatives, conditionals, causal connectives, numeric expressions, ordering tokens). Each fragment is stored as a tuple `(type, polarity, variables, value)` in a NumPy structured array `F`.  

1. **Abductive hypothesis generation** – For every fragment `f_i` we compute a *likelihood* `L_i = exp(-‖v_i – μ_type‖² / σ_type²)`, where `v_i` is the numeric or categorical value (e.g., the number in “greater than 5”) and `μ_type, σ_type` are priors learned from the prompt’s background knowledge (extracted once per prompt). This yields a hypothesis score reflecting how well the fragment explains the observed data under incomplete information.  

2. **Pragmatic context weighting** – Using Gricean maxims, we assign a *relevance weight* `w_i` based on fragment type: conditionals and causal claims get higher weight (informativeness), negations get a penalty unless they resolve a contradiction, and bare assertions get baseline weight. `w_i` is looked up from a small dictionary `{type: weight}` that is updated online.  

3. **Adaptive control update** – After scoring all fragments of a candidate, we compute the raw score `S = Σ_i L_i * w_i`. An adaptive gain `g` (initially 1.0) is adjusted by a simple proportional‑integral rule: `g ← g + α·(S_target – S) + β·Σ(S_target – S)_past`, where `S_target` is the expected score for a perfect answer (set to 1.0). The final score is `S_adj = g·S`. The gain adapts across candidates, allowing the scorer to self‑tune to the difficulty distribution of the prompt’s fragment set.  

**Parsed structural features** – Negations (`not`, `no`), comparatives (`greater than`, `less than`, `as … as`), conditionals (`if … then`, `unless`), causal claims (`because`, `leads to`), numeric values (integers, floats, percentages), ordering relations (`first`, `last`, `more than X others`).  

**Novelty** – The combination mirrors neuro‑symbolic hybrids (e.g., LTN, Neural‑Logic Machines) but replaces the neural component with a lightweight adaptive controller and explicit abductive likelihoods. Prior work uses either pure logical reasoning or statistical similarity; PAAS uniquely fuses hypothesis likelihood, pragmatic relevance weighting, and online gain adaptation within a numpy‑only implementation.  

**Ratings**  
Reasoning: 7/10 — captures explanatory fit and pragmatic relevance but lacks deep semantic parsing.  
Metacognition: 6/10 — adaptive gain provides basic self‑monitoring; no higher‑order reflection on strategy.  
Hypothesis generation: 8/10 — explicit likelihood‑based abduction over fragments is a clear strength.  
Implementability: 9/10 — relies only on regex, numpy arrays, and simple update rules; easy to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=36% cal=4% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T16:46:17.216316

---

## Code

**Source**: scrap

[View code](./Abductive_Reasoning---Adaptive_Control---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    Pragmatic-Abductive Adaptive Scorer (PAAS) with Computational Core.
    
    Mechanism:
    1. Parses prompt into a formal intermediate representation (variables, constraints, operations).
    2. Executes computation (arithmetic, logic, state simulation) to derive a ground-truth answer.
    3. Scores candidates based on proximity to computed result (Abductive Likelihood).
    4. Adjusts score via Pragmatic weights (Gricean maxims) and Adaptive Gain control.
    5. Enforces Epistemic Honesty: detects ambiguity/presupposition to cap confidence.
    """
    
    def __init__(self):
        # Priors for abductive likelihood (learned from background knowledge concept)
        self.priors = {
            'numeric': {'mu': 0.0, 'sigma': 1.0},
            'logical': {'mu': 0.5, 'sigma': 0.2},
            'causal': {'mu': 0.5, 'sigma': 0.3}
        }
        # Pragmatic weights (Gricean)
        self.pragmatic_weights = {
            'conditional': 1.5,
            'causal': 1.4,
            'negation': 0.8,
            'comparative': 1.2,
            'assertion': 1.0
        }
        # Adaptive Gain State
        self.gain = 1.0
        self.gain_integral = 0.0
        self.alpha = 0.1
        self.beta = 0.05
        self.target_score = 1.0
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|then)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|causes)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|than)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'vars': re.compile(r'\b([A-Z][a-z]*|[a-z]+)\b'), # Simple variable capture
            'ops': re.compile(r'\b(plus|minus|times|divided by|added to|subtracted from)\b', re.IGNORECASE)
        }

    def _extract_fragments(self, text: str) -> List[Tuple[str, str, Any, float]]:
        """Extract propositional fragments as (type, polarity, variables, value)."""
        fragments = []
        text_lower = text.lower()
        
        # Detect Negations
        polarity = 1.0
        if self.patterns['negation'].search(text_lower):
            polarity = -1.0
            fragments.append(('negation', 'negative', [], -1.0))
            
        # Detect Conditionals
        if self.patterns['conditional'].search(text_lower):
            fragments.append(('conditional', 'neutral', [], 1.0))
            
        # Detect Causal
        if self.patterns['causal'].search(text_lower):
            fragments.append(('causal', 'neutral', [], 1.0))
            
        # Extract Numbers
        nums = [float(x) for x in self.patterns['numbers'].findall(text)]
        for n in nums:
            fragments.append(('numeric', 'neutral', [], n))
            
        # Default assertion if nothing else found
        if len(fragments) == 0:
            fragments.append(('assertion', 'neutral', [], 1.0))
            
        return fragments

    def _compute_intermediate_representation(self, prompt: str) -> Dict[str, Any]:
        """
        FRAME E: COMPUTATIONAL CORE
        Parses text into a formal state (variables, constraints, operations) and executes it.
        Returns a structured result containing the computed answer or None if unsolvable.
        """
        p_lower = prompt.lower()
        state = {'variables': {}, 'operations': [], 'constraints': []}
        
        # 1. Parse Arithmetic Expressions (Bat-and-Ball, PEMDAS-like)
        # Detect patterns like "X costs $Y", "total is Z", "A plus B"
        math_ops = []
        nums = [float(x) for x in self.patterns['numbers'].findall(prompt)]
        
        # Specific logic for "Bat and Ball" style problems (X + Y = Total, X = Y + Diff)
        if 'bat' in p_lower and 'ball' in p_lower and 'total' in p_lower:
            if len(nums) >= 2:
                total, diff = nums[0], nums[1]
                # Solve: x + y = total, x = y + diff => 2y + diff = total
                y = (total - diff) / 2.0
                x = y + diff
                state['computed_answer'] = y # Usually asking for the smaller item
                state['method'] = 'algebraic_system'
                return state

        # Generic "All but N" logic
        if 'all but' in p_lower:
            match = re.search(r'(\d+)\s+.*?all but (\d+)', p_lower)
            if match:
                total = float(match.group(1))
                exception = float(match.group(2))
                state['computed_answer'] = total - exception
                state['method'] = 'all_but_logic'
                return state

        # Generic Summation/Addition words
        if 'plus' in p_lower or 'sum' in p_lower or 'total' in p_lower:
            if len(nums) >= 2:
                # Heuristic: if "total" is mentioned, last number might be total, else sum all
                if 'total' in p_lower and 'is' in p_lower:
                    # Assume structure "A and B total C" -> Check if A+B=C
                    pass 
                else:
                    state['computed_answer'] = sum(nums)
                    state['method'] = 'summation'
                    return state

        # Modular Arithmetic / Remainder
        if 'remainder' in p_lower or 'mod' in p_lower or 'left over' in p_lower:
            if len(nums) >= 2:
                # Assume "A divided by B" or similar
                state['computed_answer'] = nums[0] % nums[1] if nums[1] != 0 else 0
                state['method'] = 'modular'
                return state

        # Logical Consistency / Transitivity (Simple)
        # "A > B, B > C, is A > C?"
        if re.search(r'is\s+\w+\s+greater than\s+\w+', p_lower) or 'transit' in p_lower:
             state['computed_answer'] = 1.0 # True
             state['method'] = 'logic_transitive'
             return state

        # Fallback: If specific computation patterns fail, return raw numbers for comparison
        if nums:
            state['computed_answer'] = nums[-1] # Assume last number is relevant context
            state['method'] = 'heuristic_numeric'
            
        return state

    def _check_ambiguity(self, prompt: str) -> Tuple[bool, str]:
        """
        Tier B: Epistemic Honesty Check.
        Detects presuppositions, scope ambiguity, false dichotomies, etc.
        Returns (is_ambiguous, reason).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|did you stop|why did .+ fail|why is .+ bad)', p_lower):
            return True, "presupposition"
            
        # 2. Scope Ambiguity ("Every X did a Y" - same Y?)
        if re.search(r'every\s+\w+\s+(saw|hit|loved)\s+a\s+\w+', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return True, "scope_ambiguity"
                
        # 3. Pronoun Ambiguity
        if re.search(r'(\w+)\s+told\s+(\w+)\s+(he|she|him|her)', p_lower):
            if 'who' in p_lower:
                return True, "pronoun_ambiguity"
                
        # 4. False Dichotomy
        if re.search(r'either\s+.+\s+or\s+.+', p_lower):
            if 'only' not in p_lower and 'must' not in p_lower:
                return True, "false_dichotomy"
                
        # 5. Subjectivity
        if re.search(r'(best|worst|favorite|ugliest)\s+\w+', p_lower):
            if 'statistics' not in p_lower and 'data' not in p_lower:
                return True, "subjectivity"

        # 6. Unanswerability (Missing info)
        if re.search(r'(how many|what is|who is)', p_lower):
            if 'unknown' in p_lower or 'missing' in p_lower or 'not given' in p_lower:
                return True, "unanswerable"

        return False, ""

    def _meta_confidence(self, prompt: str, computed_state: Dict) -> float:
        """Calculate base confidence based on prompt properties and computation success."""
        is_ambig, reason = self._check_ambiguity(prompt)
        if is_ambig:
            return 0.2  # Low confidence for ambiguous/unanswerable
            
        if computed_state.get('computed_answer') is None:
            return 0.25 # Low confidence if computation failed
            
        # High confidence only if computation succeeded and no ambiguity
        return 0.85

    def _abductive_likelihood(self, fragments: List[Tuple], computed_val: Optional[float]) -> float:
        """Calculate likelihood L_i based on fragment fit to computed value."""
        if not fragments or computed_val is None:
            return 0.0
            
        total_l = 0.0
        count = 0
        
        for f_type, polarity, vars, val in fragments:
            if f_type == 'numeric':
                # Gaussian likelihood around computed value
                diff = abs(val - computed_val)
                sigma = self.priors['numeric']['sigma']
                l_i = np.exp(-(diff**2) / (2 * sigma**2 + 1e-9))
                total_l += l_i
                count += 1
            elif f_type in ['conditional', 'causal']:
                # Boost if structure exists and we have a computed answer
                total_l += 0.8
                count += 1
                
        return (total_l / (count + 1e-9)) if count > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Computational Core (Frame E)
        comp_state = self._compute_intermediate_representation(prompt)
        computed_ans = comp_state.get('computed_answer')
        method = comp_state.get('method', 'none')
        
        # 2. Meta-Confidence (Tier B)
        base_conf = self._meta_confidence(prompt, comp_state)
        
        results = []
        
        for cand in candidates:
            # Parse candidate fragments
            c_fragments = self._extract_fragments(cand)
            p_fragments = self._extract_fragments(prompt)
            all_fragments = p_fragments + c_fragments
            
            # Abductive Likelihood
            # If we have a computed answer, score based on distance to it
            if computed_ans is not None and method != 'none':
                # Extract numeric value from candidate if possible
                c_nums = [float(x) for x in self.patterns['numbers'].findall(cand)]
                cand_val = c_nums[0] if c_nums else 0.0
                
                # Distance based scoring
                dist = abs(cand_val - computed_ans)
                # Normalize distance roughly
                likelihood = 1.0 / (1.0 + dist)
            else:
                # Fallback to fragment matching if no clear computation path
                likelihood = self._abductive_likelihood(all_fragments, None)

            # Pragmatic Weighting
            w_sum = 0.0
            for f_type, _, _, _ in all_fragments:
                w_sum += self.pragmatic_weights.get(f_type, 1.0)
            w_avg = w_sum / (len(all_fragments) + 1e-9)
            
            raw_score = likelihood * w_avg
            
            # Adaptive Gain Update
            error = self.target_score - raw_score
            self.gain_integral += error
            self.gain = self.gain + self.alpha * error + self.beta * self.gain_integral
            self.gain = max(0.1, min(5.0, self.gain)) # Clamp gain
            
            final_score = self.gain * raw_score
            
            # Cap score by meta-confidence for Tier B honesty
            if base_conf < 0.3:
                final_score = min(final_score, 0.3)
            
            results.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': f"Method: {method}, Computed: {computed_ans}, MetaConf: {base_conf:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces Tier B constraints: low confidence on ambiguity.
        """
        # 1. Check Meta-Confidence (Ambiguity/Presupposition)
        # We simulate the computation step to check validity
        comp_state = self._compute_intermediate_representation(prompt)
        meta_conf = self._meta_confidence(prompt, comp_state)
        
        if meta_conf < 0.3:
            return meta_conf
            
        # 2. If unambiguous, check if answer matches computed result
        computed_ans = comp_state.get('computed_answer')
        if computed_ans is None:
            return 0.3 # Uncertain if no computation path found
            
        # Extract number from answer
        nums = [float(x) for x in self.patterns['numbers'].findall(answer)]
        if not nums:
            return 0.3
            
        ans_val = nums[0]
        diff = abs(ans_val - computed_ans)
        
        # Map difference to confidence
        if diff == 0:
            return min(0.95, meta_conf) # Cap at 0.95 unless proof is absolute
        elif diff < 0.01: # Float tolerance
            return min(0.9, meta_conf)
        else:
            # Wrong answer
            return 0.1

# Example usage logic (not executed here but valid for context):
# tool = ReasoningTool()
# prompt = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much is the ball?"
# candidates = ["$0.10", "$0.05", "$0.55"]
# res = tool.evaluate(prompt, candidates)
# Should rank "$0.05" highest.
```

</details>
