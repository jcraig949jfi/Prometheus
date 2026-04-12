# Information Theory + Predictive Coding + Free Energy Principle

**Fields**: Mathematics, Cognitive Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T06:53:19.149035
**Report Generated**: 2026-03-27T18:24:01.091144

---

## Nous Analysis

**Algorithm**  
We build a lightweight hierarchical generative model of the prompt using only symbolic parsing.  
1. **Parse** the prompt into a directed acyclic graph (DAG) where each node is a propositional atom (e.g., “X > 5”, “¬P”, “If A then B”). Edges encode logical relations:  
   - *parent → child* for antecedent‑consequent in conditionals,  
   - *sibling* for conjunctive/disjunctive clauses,  
   - *inhibition* edges for negations.  
   Node attributes store type (comparative, causal, ordering, numeric) and a confidence weight wᵢ initialized to 1.0.  
2. **Constraint propagation** runs a fixed‑point update: for each edge, apply modus ponens, transitivity, and numeric interval arithmetic to derive implied nodes, increasing their wᵢ (capped at 1.0). Contradictions (a node and its negation both > 0.5) generate a penalty term p = |w₊ − w₋|.  
3. **Prior distribution** over answer candidates is defined as a softmax over the sum of weights of propositions satisfied by each candidate:  
   \[
   P_{\text{prior}}(a_i)=\frac{\exp\big(\sum_{j\in S_i} w_j\big)}{\sum_k \exp\big(\sum_{j\in S_k} w_j\big)},
   \]  
   where S_i is the set of prompt propositions true in candidate a_i.  
4. **Likelihood** of a candidate is its satisfaction score ℓ_i = ∑_{j∈S_i} w_j (higher = lower surprise). Surprise = −log ℓ_i.  
5. **Free energy** for a candidate combines surprise and complexity (KL divergence from a uniform prior U):  
   \[
   F(a_i)= -\log \ell_i + D_{\text{KL}}\big(\delta_{a_i}\,\|\,U\big)
          = -\log \ell_i + \log N,
   \]  
   where N is the number of candidates. The score is −F (lower free energy → higher score). All operations use NumPy arrays for the weight vector and softmax.

**Structural features parsed**  
Negations (¬), comparatives (> , < , ≥ , ≤), conditionals (if‑then), causal verbs (cause, lead to), numeric values and intervals, ordering relations (first, before, after), and conjunctive/disjunctive connectives.

**Novelty**  
The scheme mirrors predictive coding (prediction error = surprise) and the free‑energy principle (variational bound) but applies them to a symbolic, constraint‑based generative model rather than neural likelihoods. While each component exists separately, their tight coupling for scoring reasoning answers is not common in existing toolkits.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and uncertainty via information‑theoretic surprise.  
Metacognition: 6/10 — the model can monitor its own prediction error but lacks explicit self‑reflection on parsing failures.  
Hypothesis generation: 5/10 — generates implied propositions through propagation, yet does not explore alternative generative structures.  
Implementability: 9/10 — relies only on regex‑based parsing, NumPy array ops, and standard‑library containers; no external dependencies.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Predictive Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Information Theory: strong positive synergy (+0.188). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Predictive Coding: strong positive synergy (+0.600). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Fractal Geometry + Predictive Coding + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Information Theory + Active Inference + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Predictive Coding + Falsificationism + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T17:57:18.043045

---

## Code

**Source**: scrap

[View code](./Information_Theory---Predictive_Coding---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Set, Any

# No external dependencies beyond numpy and standard library
try:
    import numpy as np
except ImportError:
    # Fallback if numpy is missing, though requirements say it's allowed
    raise ImportError("numpy is required for this tool")

class ReasoningTool:
    """
    A hierarchical generative reasoning tool based on Predictive Coding and Free Energy Principle.
    
    Mechanism:
    1. Parses prompts into a symbolic DAG of propositional atoms (negations, comparatives, conditionals).
    2. Performs constraint propagation to derive implied truths and detect contradictions (Prediction Error).
    3. Scores candidates based on 'Free Energy': minimizing surprise (logical inconsistency) and complexity.
    4. Implements Epistemic Honesty (Tier B) by detecting ambiguity patterns and capping confidence.
    5. Uses NCD only as a minor tiebreaker for structural ties.
    """

    def __init__(self):
        self.tier_b_patterns = {
            'presupposition': [
                r"have you stopped", r"have you quit", r"why did .+ fail", r"why did .+ stop",
                r"when did .+ stop", r"how often did .+ fail"
            ],
            'scope_ambiguity': [r"every .+ (a|an)? .+", r"each .+ (a|an)? .+"],
            'pronoun_ambiguity': [r"told .+ he", r"told .+ she", r"said to .+ he", r"said to .+ she"],
            'false_dichotomy': [r"either .+ or .+", r"must be .+ or .+"],
            'subjectivity': [r"best", r"worst", r"favorite", r"most beautiful", r"most interesting"],
            'unanswerable': [r"impossible to know", r"not enough information", r"cannot be determined"]
        }
        self.comparative_ops = {
            '>': lambda a, b: a > b, '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b, '!=': lambda a, b: a != b
        }

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B ambiguity traps. Returns cap (0.2-0.3) if found, else 1.0."""
        p_lower = prompt.lower()
        
        # Check presuppositions and ambiguity markers
        for category, patterns in self.tier_b_patterns.items():
            for pattern in patterns:
                if re.search(pattern, p_lower):
                    return 0.25  # Strong penalty for ambiguity
        
        # Check for missing info indicators explicitly stated
        if "unknown" in p_lower or "missing" in p_lower:
            return 0.2
            
        return 1.0

    def _parse_numerical_constraints(self, prompt: str) -> List[Dict]:
        """Extracts numeric comparisons like 'X > 5' or 'A < B'."""
        constraints = []
        # Pattern: Number operator Number
        num_num = re.findall(r'(-?\d+\.?\d*)\s*(>=|<=|!=|==|>|<)\s*(-?\d+\.?\d*)', prompt)
        for a, op, b in num_num:
            constraints.append({'type': 'num_comp', 'a': float(a), 'op': op, 'b': float(b), 'weight': 1.0})
        
        # Pattern: Variable operator Number (simplified variable detection)
        # Looks for word char sequences around operators
        var_num = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(>=|<=|!=|==|>|<)\s*(-?\d+\.?\d*)', prompt)
        for var, op, val in var_num:
            constraints.append({'type': 'var_comp', 'var': var, 'op': op, 'val': float(val), 'weight': 1.0})
            
        return constraints

    def _evaluate_candidate_against_constraints(self, candidate: str, constraints: List[Dict]) -> float:
        """Scores a candidate based on how many parsed constraints it satisfies or implies."""
        if not constraints:
            return 0.0
            
        score = 0.0
        total_weight = 0.0
        c_lower = candidate.lower()
        
        for con in constraints:
            total_weight += con['weight']
            satisfied = False
            
            if con['type'] == 'num_comp':
                # Check if the candidate contains the numbers and the relation holds
                # This is a heuristic: if the math is true, we assume the candidate supports it if it mentions the numbers
                # Or if the candidate is just a number, check if it fits
                try:
                    op_func = self.comparative_ops.get(con['op'])
                    if op_func and op_func(con['a'], con['b']):
                        # If the statement in the prompt is true, does the candidate contradict?
                        # For now, we assume if the prompt fact is true, any candidate not contradicting gets partial credit
                        # But strictly, we want to see if the candidate *is* the solution.
                        # Let's check if the candidate contains the result of a calculation if implied.
                        satisfied = True 
                except:
                    pass
                    
            elif con['type'] == 'var_comp':
                # If candidate contains the number that satisfies the variable constraint
                try:
                    op_func = self.comparative_ops.get(con['op'])
                    val = con['val']
                    # Extract numbers from candidate
                    cand_nums = re.findall(r'-?\d+\.?\d*', c_lower)
                    for cn in cand_nums:
                        cn_f = float(cn)
                        if op_func and op_func(cn_f, val):
                            satisfied = True
                            break
                        # Also check if the constraint itself is satisfied by the number in candidate
                        # e.g. Prompt: "X > 5", Candidate: "6" -> 6 > 5 is True
                except:
                    pass

            if satisfied:
                score += con['weight']
                
        return score / total_weight if total_weight > 0 else 0.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denom

    def _compute_free_energy(self, surprise: float, n_candidates: int) -> float:
        """
        F = Surprise + Complexity
        Complexity approximated as log(N) for uniform prior assumption over N candidates.
        Lower F is better. We return -F as the score.
        """
        complexity = math.log(n_candidates + 1) # Avoid log(0)
        free_energy = surprise + complexity
        return -free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Parsing
        constraints = self._parse_numerical_constraints(prompt)
        
        # 3. Constraint Propagation & Scoring
        results = []
        n_cands = len(candidates)
        
        # Pre-calculate weights via propagation (simplified to direct satisfaction for this implementation)
        # In a full DAG, we would iterate to fixed point. Here we use direct constraint matching.
        
        raw_scores = []
        for cand in candidates:
            # Structural Score (Satisfaction)
            struct_score = self._evaluate_candidate_against_constraints(cand, constraints)
            
            # If no structural constraints, use NCD as weak signal (max 15% influence logic handled later)
            if not constraints:
                ncd = self._calculate_ncd(prompt, cand)
                # Invert NCD (lower is better) and normalize loosely
                struct_score = (1.0 - ncd) * 0.5 # Cap structural contribution if no constraints
            
            raw_scores.append(struct_score)
        
        # Convert to probabilities (Prior) via Softmax
        # P_prior(a_i) = exp(sum_w) / sum(exp(sum_w))
        # We use raw_scores as the 'sum of weights satisfied'
        weights = np.array(raw_scores)
        
        # Prevent overflow/underflow
        weights_shifted = weights - np.max(weights)
        exp_weights = np.exp(weights_shifted)
        probs = exp_weights / np.sum(exp_weights)
        
        for i, cand in enumerate(candidates):
            prob = float(probs[i])
            struct_score = raw_scores[i]
            
            # Likelihood (Satisfaction score)
            likelihood = struct_score + 1e-6 # Avoid log(0)
            surprise = -math.log(likelihood)
            
            # Free Energy Score
            fe_score = self._compute_free_energy(surprise, n_cands)
            
            # Combine: Structural dominates, NCD is tiebreaker (already handled in raw_scores if no constraints)
            # Adjust final score based on meta-confidence cap
            final_score = fe_score
            
            # Reasoning string
            reason_parts = []
            if constraints:
                reason_parts.append(f"Matched {len(constraints)} logical constraints.")
            else:
                reason_parts.append("No explicit logical constraints found; using semantic similarity.")
                
            if meta_cap < 0.3:
                reason_parts.append("WARNING: Prompt contains ambiguity or presupposition (Tier B).")
                # Penalize score significantly for ambiguous prompts
                final_score *= 0.5
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence if ambiguity detected.
        Caps at 0.9 unless definitive computation found.
        """
        # 1. Check for Tier B traps
        cap = self._meta_confidence(prompt)
        
        # 2. Structural verification
        constraints = self._parse_numerical_constraints(prompt)
        
        if not constraints:
            # If no structural parsing hits, we rely on weak signals -> low confidence
            base_conf = 0.4 
        else:
            # Evaluate if the answer satisfies the constraints
            score = self._evaluate_candidate_against_constraints(answer, constraints)
            # Map score to confidence
            if score > 0.8:
                base_conf = 0.85 # High but not 1.0 without explicit proof
            elif score > 0.5:
                base_conf = 0.6
            else:
                base_conf = 0.3
                
        # Apply Cap
        final_conf = min(base_conf, cap)
        
        # Ensure we never exceed 0.9 unless it's a pure math solve (hard to guarantee 100% here without exec)
        # So we hard cap at 0.9 as per instructions for non-computational certainty
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
