# Prime Number Theory + Abductive Reasoning + Sensitivity Analysis

**Fields**: Mathematics, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T05:41:21.007355
**Report Generated**: 2026-04-01T20:30:43.921113

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Tokenize the prompt and each candidate answer with `str.split`. Apply a handful of regexes to extract:  
   - integers/floats (`\b\d+(\.\d+)?\b`) → `num`  
   - comparatives (`>`, `<`, `>=`, `<=`, `=`) → `comp`  
   - negations (`not`, `no`, `never`) → `neg`  
   - conditionals (`if`, `unless`, `provided that`) → `cond` (store antecedent and consequent)  
   - causal verbs (`because`, `leads to`, `results in`) → `cause`  
   - ordering markers (`first`, `then`, `before`, `after`) → `order`  
   Each extracted element becomes a **Clause** object: `{type, polarity, variables, numeric_value}` where `type ∈ {assertion, negation, conditional, causal, order}`. All clauses from a candidate are stored in a list `C`.  

2. **Weight assignment (Prime Number Theory)** – For every numeric constant `n` in a clause, compute the distance to the nearest prime: `gap = min(|n-p| for p in primes_around(n))` using a pre‑computed sieve up to the max number seen. Define a rarity weight `w_n = 1 / (gap + 1)`. The clause weight is the product of its `w_n` factors (default 1 if no numbers).  

3. **Abductive scoring** – Build a constraint graph where edges represent logical compatibility (e.g., two assertions with contradictory polarity, or a conditional whose antecedent matches an assertion). For each candidate, compute a **fit score** `F = Σ_{c∈C} w_c * satisfied(c)`, where `satisfied(c)=1` if the clause does not violate any constraint in the graph, else 0. This is inference to the best explanation: the hypothesis set (the candidate’s clauses) that maximizes explanatory weight while respecting prompt constraints.  

4. **Sensitivity analysis** – For each token `t` in the prompt, create a perturbed prompt `P_{-t}` (token removed). Re‑run steps 1‑3 to obtain `F_{-t}`. Compute sensitivity `S = std({F_{-t}})/mean({F})`. The final candidate score is `Score = F * (1 - min(S, 0.9))`, penalizing explanations that rely heavily on fragile prompt fragments.  

All operations use only Python’s `re`, `math`, and `numpy` for vectorized sums and std.

**Structural features parsed**  
- Numeric values (integers, decimals)  
- Comparatives (`>`, `<`, `=`)  
- Negations (`not`, `no`, `never`)  
- Conditionals (`if`, `unless`, `provided that`)  
- Causal claims (`because`, `leads to`, `results in`)  
- Ordering/temporal relations (`first`, `then`, `before`, `after`)  

**Novelty**  
Prime‑based rarity weighting of numeric constants is not used in existing NLP scoring tools; combining it with abductive constraint fitting and a finite‑difference sensitivity penalty yields a novel hybrid that directly ties number‑theoretic properties to explanation quality.

**Ratings**  
Reasoning: 8/10 — captures logical structure and numeric rarity but lacks deep semantic understanding.  
Metacognition: 7/10 — sensitivity provides a proxy for self‑assessment of reliance on prompt fragility.  
Hypothesis generation: 8/10 — abductive fit selects the best‑explaining clause set.  
Implementability: 9/10 — relies only on regex, numpy, and a simple sieve; easy to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.67** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=11% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-01T20:14:43.505512

---

## Code

**Source**: scrap

[View code](./Prime_Number_Theory---Abductive_Reasoning---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A hybrid reasoning tool combining Prime Number Theory rarity weighting,
    Abductive constraint satisfaction, and Sensitivity analysis.
    
    Mechanism:
    1. Parsing: Extracts numeric, logical, and causal clauses via regex.
    2. Prime Weighting: Assigns higher weights to numbers closer to primes (rarity).
    3. Abductive Fit: Scores candidates based on logical consistency with the prompt.
    4. Sensitivity: Penalizes scores if the result depends heavily on fragile token removal.
    5. Meta-Confidence: Detects ambiguity/presuppositions to enforce epistemic honesty.
    """

    def __init__(self):
        # Precompute primes up to 10000 for gap calculation
        self.max_prime = 10000
        self.primes = self._sieve(self.max_prime)
        
        # Regex patterns
        self.patterns = {
            'num': re.compile(r'\b-?\d+(?:\.\d+)?\b'),
            'comp': re.compile(r'(>=|<=|!=|==|>|<|=)'),
            'neg': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|unless|provided that|when)\b', re.IGNORECASE),
            'cause': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'order': re.compile(r'\b(first|then|before|after|next|finally)\b', re.IGNORECASE)
        }

    def _sieve(self, limit: int) -> List[int]:
        """Simple sieve of Eratosthenes."""
        if limit < 2:
            return []
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(math.sqrt(limit)) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [i for i, p in enumerate(is_prime) if p]

    def _get_prime_gap(self, n: float) -> int:
        """Calculate distance to nearest prime."""
        if n < 0:
            n = abs(n)
        if n > self.max_prime:
            # Approximate for large numbers: check around n
            return 1 # Default small gap for out-of-bounds to avoid crash
        
        n_int = int(round(n))
        # Find closest prime
        min_gap = float('inf')
        for p in self.primes:
            gap = abs(p - n_int)
            if gap < min_gap:
                min_gap = gap
            if gap == 0:
                break
        return int(min_gap) if min_gap != float('inf') else 1

    def _parse_clauses(self, text: str) -> List[Dict]:
        """Tokenize and extract structured clauses."""
        clauses = []
        tokens = text.split()
        text_lower = text.lower()
        
        # Extract Numbers
        for match in self.patterns['num'].finditer(text):
            val = float(match.group())
            gap = self._get_prime_gap(val)
            weight = 1.0 / (gap + 1)
            clauses.append({
                'type': 'numeric',
                'value': val,
                'weight': weight,
                'polarity': 1
            })
            
        # Extract Logic Markers (simplified presence detection with weights)
        marker_map = [
            ('neg', self.patterns['neg'], -1.0),
            ('cond', self.patterns['cond'], 0.8),
            ('cause', self.patterns['cause'], 0.9),
            ('order', self.patterns['order'], 0.7),
            ('comp', self.patterns['comp'], 0.6)
        ]
        
        for m_type, regex, base_w in marker_map:
            if regex.search(text):
                # Weight by rarity of concept? For now, fixed structural weight
                clauses.append({
                    'type': m_type,
                    'value': 0,
                    'weight': base_w,
                    'polarity': -1 if m_type == 'neg' else 1
                })
                
        return clauses

    def _check_constraints(self, prompt_clauses: List[Dict], cand_clauses: List[Dict]) -> float:
        """
        Abductive scoring: Check logical compatibility.
        Returns a fit score (0.0 to 1.0).
        """
        if not prompt_clauses:
            return 0.5 # Neutral if no structure
        
        matches = 0
        total_weight = 0
        
        # Simple heuristic: Does the candidate contain the critical numeric/logic constraints?
        # We look for numeric proximity and negation alignment
        
        p_nums = [c['value'] for c in prompt_clauses if c['type'] == 'numeric']
        c_nums = [c['value'] for c in cand_clauses if c['type'] == 'numeric']
        
        # Numeric Fit
        if p_nums and c_nums:
            # Check if candidate numbers satisfy prompt comparisons if present
            # Simplified: Reward if candidate numbers are "close" to prompt numbers or derived logically
            # Since we can't solve algebra symbolically here, we check for exact matches or direct results
            fit_sum = 0
            for pn in p_nums:
                best_dist = float('inf')
                for cn in c_nums:
                    dist = abs(cn - pn)
                    # Also check simple operations (pn+1, pn*2 etc) to catch constructive computation
                    ops = [pn, pn+1, pn-1, pn*2, pn/2, pn**2]
                    for op in ops:
                        if abs(cn - op) < 1e-6:
                            dist = 0
                            break
                    if dist < best_dist:
                        best_dist = dist
                # Convert distance to fit (exponential decay)
                fit_sum += math.exp(-best_dist)
            matches += fit_sum / max(len(p_nums), 1)
            total_weight += 1.0
            
        # Logic Fit (Negation/Conditionals)
        p_neg = any(c['type'] == 'neg' for c in prompt_clauses)
        c_neg = any(c['type'] == 'neg' for c in cand_clauses)
        if p_neg == c_neg:
            matches += 1.0
        else:
            matches += 0.2 # Penalty for missing negation
        total_weight += 1.0
        
        return min(matches / total_weight, 1.0) if total_weight > 0 else 0.5

    def _compute_sensitivity(self, prompt: str, candidates: List[str]) -> Tuple[List[float], float]:
        """
        Perturb prompt by removing tokens and re-evaluating fit.
        Returns original scores and sensitivity metric (std/mean).
        """
        original_scores = []
        perturbed_scores = []
        
        # 1. Get original scores
        for cand in candidates:
            pc = self._parse_clauses(prompt)
            cc = self._parse_clauses(cand)
            fit = self._check_constraints(pc, cc)
            # Weight by sum of clause weights
            w_sum = sum(c['weight'] for c in cc) if cc else 1
            score = fit * (1 + math.log1p(w_sum)) # Boost by complexity
            original_scores.append(score)
            
        if len(original_scores) == 0 or max(original_scores) == 0:
            return original_scores, 0.0

        # 2. Sensitivity Analysis (Sampled for performance)
        tokens = prompt.split()
        if len(tokens) > 20:
            # Subsample tokens for sensitivity to save time
            step = len(tokens) // 10
            test_tokens = tokens[::step]
        else:
            test_tokens = tokens
            
        if not test_tokens:
            return original_scores, 0.0

        std_devs = []
        
        for i, cand in enumerate(candidates):
            f_perturbed = []
            base_fit = original_scores[i]
            
            for t in test_tokens:
                # Remove one instance of token
                perturbed_prompt = prompt.replace(f" {t} ", " ", 1).replace(f"{t} ", "", 1).replace(f" {t}", "", 1)
                if perturbed_prompt == prompt: # Token not found as word
                    continue
                    
                pc_p = self._parse_clauses(perturbed_prompt)
                cc_p = self._parse_clauses(cand)
                fit_p = self._check_constraints(pc_p, cc_p)
                w_sum_p = sum(c['weight'] for c in cc_p) if cc_p else 1
                score_p = fit_p * (1 + math.log1p(w_sum_p))
                f_perturbed.append(score_p)
            
            if len(f_perturbed) > 1:
                std_dev = np.std(f_perturbed)
                mean_val = np.mean(f_perturbed) if np.mean(f_perturbed) != 0 else 1e-6
                sens = std_dev / mean_val if mean_val != 0 else 0
                std_devs.append(sens)
            else:
                std_devs.append(0.0)

        avg_sens = np.mean(std_devs) if std_devs else 0.0
        return original_scores, avg_sens

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "why did", "why does", "when did", "quit ", "stopped "]
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                # Check if it's a question
                if "?" in prompt:
                    return 0.2
        
        # 2. Scope/Pronoun ambiguity (Heuristic)
        if re.search(r'\b(every|each|all)\b.*\b(a|an)\b', p_lower) and "?" in prompt:
            # Potential scope ambiguity
            if "same" in p_lower or "different" in p_lower:
                return 0.3
                
        if re.search(r'\b(he|she|him|her|they)\b.*\b(who|which one)\b', p_lower):
            return 0.3
            
        # 3. False Dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and "only" in p_lower:
            return 0.4
            
        # 4. Subjectivity
        subjective_words = ["best", "worst", "favorite", "opinion", "think"]
        if any(w in p_lower for w in subjective_words) and "calculate" not in p_lower:
            return 0.4
            
        # 5. Unanswerability (Missing info)
        if "insufficient" in p_lower or "not enough" in p_lower:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def _constructive_compute(self, prompt: str, candidate: str) -> Optional[float]:
        """
        FRAME B: Attempt to constructively solve numeric/logic problems.
        Returns a computed value if possible, else None.
        """
        # Extract all numbers from prompt
        nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        
        # Heuristic: If prompt asks for sum/avg/product and candidate is a number
        p_lower = prompt.lower()
        
        if len(nums) >= 2:
            target = None
            if "sum" in p_lower or "total" in p_lower or "add" in p_lower:
                target = sum(nums)
            elif "average" in p_lower or "mean" in p_lower:
                target = sum(nums) / len(nums)
            elif "product" in p_lower:
                target = np.prod(nums)
            elif "difference" in p_lower:
                target = abs(nums[0] - nums[1])
                
            if target is not None:
                # Check if candidate contains this target
                cand_nums = re.findall(r'-?\d+(?:\.\d+)?', candidate)
                for cn in cand_nums:
                    if abs(float(cn) - target) < 1e-5:
                        return 1.0 # Found constructive match
                return 0.0 # Constructive attempt failed
        
        # Bayesian / Probability simple check
        if "probability" in p_lower or "chance" in p_lower:
            # Very basic: if prompt has "50%" and candidate says "0.5" or "1/2"
            if "0.5" in candidate or "1/2" in candidate or "50%" in candidate:
                 if "50" in prompt:
                     return 1.0
                     
        return None # Could not compute

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Sensitivity Analysis (runs parsing internally)
        base_scores, sensitivity = self._compute_sensitivity(prompt, candidates)
        
        # 2. Meta-Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        for i, cand in enumerate(candidates):
            base_score = base_scores[i]
            
            # Apply Sensitivity Penalty
            # Score = F * (1 - min(S, 0.9))
            penalized_score = base_score * (1.0 - min(sensitivity, 0.9))
            
            # Constructive Computation Override (Frame B)
            # If we can compute the answer, trust computation over pattern matching
            comp_result = self._constructive_compute(prompt, cand)
            if comp_result is not None:
                if comp_result == 1.0:
                    penalized_score = 1.0 + 0.1 # Boost definitive correct computation
                else:
                    penalized_score = 0.1 # Penalize wrong computation
            
            # Apply Meta-Confidence Cap
            if meta_cap < 0.5:
                # If ambiguous, cap the score regardless of pattern match
                penalized_score = min(penalized_score, meta_cap)
            
            # Normalize to 0-1 roughly
            final_score = max(0.0, min(1.0, penalized_score))
            
            # Generate Reasoning String
            reasoning = f"Prime-weighted fit: {base_score:.3f}; Sensitivity penalty: {sensitivity:.3f}; "
            if comp_result is not None:
                reasoning += f"Constructive check: {'Pass' if comp_result==1 else 'Fail'}; "
            if meta_cap < 1.0:
                reasoning += f"Ambiguity detected (Cap: {meta_cap}); "
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check for ambiguity first
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return 0.1 # Definitely unsure on ambiguous prompts
            
        # 2. Run evaluation on single candidate
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]['score']
        
        # 3. Apply Cap
        final_conf = min(score, meta_cap)
        
        # 4. Never return > 0.9 unless constructive computation was perfect
        # (Handled implicitly if meta_cap is low, but explicit check for safety)
        if "Constructive check: Pass" not in res_list[0]['reasoning']:
            final_conf = min(final_conf, 0.85)
            
        return round(final_conf, 4)

# Example usage logic (not part of class):
# tool = ReasoningTool()
# print(tool.evaluate("What is 2 + 2?", ["4", "5"]))
# print(tool.confidence("Have you stopped cheating?", "Yes")) # Should be low
```

</details>
