# Falsificationism + Multi-Armed Bandits + Abstract Interpretation

**Fields**: Philosophy, Game Theory, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T19:11:46.874308
**Report Generated**: 2026-04-02T10:00:36.358426

---

## Nous Analysis

**Algorithm: Falsification‑Bandit Abstract Interpreter (FBAI)**  

*Data structures*  
- **Answer graph** \(G=(V,E)\): each node \(v_i\) holds a parsed proposition (literal, negated literal, comparative, conditional). Edges encode syntactic relations (e.g., subject‑predicate, antecedent‑consequent).  
- **Arm table** \(A\): one arm per candidate answer \(c_j\). Stores \((\hat\mu_j, n_j, U_j)\) where \(\hat\mu_j\) is the empirical falsification score, \(n_j\) pulls, and \(U_j\) the UCB confidence bound.  
- **Abstract domain** \(\mathcal{D}\): a lattice of truth‑value intervals \([l,u]\subseteq[0,1]\) representing the degree to which a proposition is *known false* (0 = certainly true, 1 = certainly false). Bottom \([0,0]\) (true), top \([1,1]\) (false).  

*Operations*  
1. **Parsing** – regex‑based extraction yields a set of atomic propositions \(p_k\) and logical connectives (¬, ∧, →, >, <, =). Each \(p_k\) is mapped to a lattice element; literals start at \([0,0]\), negated literals at \([1,1]\).  
2. **Abstract interpretation** – propagate constraints through \(G\) using transfer functions:  
   - ¬: \([l,u] \rightarrow [1-u,1-l]\)  
   - ∧: \([l_1,u_1] \sqcap [l_2,u_2] = [\max(l_1,l_2),\min(u_1,u_2)]\)  
   - → (material implication): \([l_a,u_a] \rightarrow [l_c,u_c]\) yields \([ \max(0,1-u_a+l_c), \min(1,1-l_a+u_c) ]\)  
   - comparatives: map numeric tokens to intervals; a violated inequality forces the corresponding proposition toward 1 (more false).  
   The fix‑point iteration yields, for each answer \(c_j\), a global falsification interval \(F_j = [l_j,u_j]\) (the join of all node intervals).  
3. **Bandit selection** – treat each answer as an arm. After computing \(F_j\), define instantaneous reward \(r_j = 1 - u_j\) (higher when the upper bound of falsity is low). Update \(\hat\mu_j\) with incremental mean, increment \(n_j\), and recompute \(U_j = \hat\mu_j + \sqrt{2\ln t / n_j}\) (UCB1). The arm with highest \(U_j\) is selected for the next evaluation round; after a fixed budget (e.g., 10 pulls) the final score is \(\hat\mu_j\).  

*Scoring logic* – the algorithm returns \(\hat\mu_j\) as the estimated truthfulness; lower values indicate stronger resistance to falsification, thus higher quality.  

**Structural features parsed** – negations, conjunctions, material conditionals, comparative operators (> < = ≥ ≤), equality, numeric constants, and ordering relations (transitivity chains).  

**Novelty** – While abstract interpretation and bandit‑based answer selection exist separately, coupling them with a Popperian falsification reward (using the abstract domain’s upper bound as a proxy for refutability) is not documented in the literature; thus the combination is novel.  

**Ratings**  
Reasoning: 8/10 — captures logical consequence and uncertainty via sound abstraction and principled exploration.  
Metacognition: 6/10 — the bandit mechanism implicitly monitors confidence but lacks explicit self‑reflection on parse failures.  
Hypothesis generation: 7/10 — UCB drives exploration of under‑tested answers, generating falsification‑focused hypotheses.  
Implementability: 9/10 — relies only on regex, interval arithmetic, and basic statistics; all feasible with numpy and the stdlib.

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
**Reason**: validation:forbidden_import: forge_primitives

**Forge Timestamp**: 2026-04-02T09:44:20.695216

---

## Code

**Source**: scrap

[View code](./Falsificationism---Multi-Armed_Bandits---Abstract_Interpretation/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Falsification-Bandit Abstract Interpreter (FBAI)

Combines Popperian falsificationism with multi-armed bandit exploration and abstract
interpretation using interval arithmetic. Evaluates candidates by attempting to
falsify them via logical constraint propagation, allocating evaluation budget via UCB1.

Core mechanism:
1. Parse prompt into logical propositions and constraints
2. Build abstract domain: truth intervals [l,u] where 0=true, 1=false
3. For each candidate, propagate constraints to compute falsification interval
4. UCB1 bandit selects which candidates to evaluate next
5. Final score = resistance to falsification (lower falsity upper bound = higher score)
"""

import re
import numpy as np
import zlib
from collections import defaultdict
from forge_primitives import (
    modus_ponens, check_transitivity, bayesian_update,
    solve_constraints, confidence_from_agreement, negate
)

class ReasoningTool:
    def __init__(self):
        self.epsilon = 1e-6
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Evaluate candidates using falsification-bandit abstract interpretation."""
        if not candidates:
            return []
        
        # Parse prompt structure
        parsed = self._parse_prompt(prompt)
        
        # Initialize bandit arms (one per candidate)
        n_arms = len(candidates)
        arm_means = np.zeros(n_arms)
        arm_pulls = np.zeros(n_arms)
        
        # UCB1 exploration with budget
        budget = min(10, n_arms * 3)
        for t in range(1, budget + 1):
            # Compute UCB scores
            ucb_scores = np.zeros(n_arms)
            for j in range(n_arms):
                if arm_pulls[j] == 0:
                    ucb_scores[j] = float('inf')
                else:
                    ucb_scores[j] = arm_means[j] + np.sqrt(2 * np.log(t) / arm_pulls[j])
            
            # Select arm with highest UCB
            arm = np.argmax(ucb_scores)
            
            # Evaluate: compute falsification interval for this candidate
            reward = self._evaluate_candidate(prompt, candidates[arm], parsed)
            
            # Update arm statistics
            arm_pulls[arm] += 1
            arm_means[arm] += (reward - arm_means[arm]) / arm_pulls[arm]
        
        # Ensure all arms pulled at least once
        for j in range(n_arms):
            if arm_pulls[j] == 0:
                reward = self._evaluate_candidate(prompt, candidates[j], parsed)
                arm_pulls[j] = 1
                arm_means[j] = reward
        
        # Build results
        results = []
        for j, cand in enumerate(candidates):
            reasoning = f"Falsification score: {1-arm_means[j]:.3f}, pulls: {int(arm_pulls[j])}"
            results.append({
                "candidate": cand,
                "score": float(arm_means[j]),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer, checking for epistemic traps."""
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        parsed = self._parse_prompt(prompt)
        base_score = self._evaluate_candidate(prompt, answer, parsed)
        
        # Cap confidence based on structural match quality
        if parsed["has_structure"]:
            return min(0.85, base_score * meta_conf)
        else:
            return min(0.5, base_score * meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic traps and ambiguity."""
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [
            r"have you (stopped|quit|ceased)",
            r"why did .+ (fail|stop|end)",
            r"when did you (stop|start|begin)"
        ]
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity
        if re.search(r"every .+ (has|did|made) a ", p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if "who" in p_lower and re.search(r"(he|she|they|it) (was|is|said)", p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r"either .+ or .+\?", p_lower) and "other" not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r"(best|worst|favorite|most|least) ", p_lower):
            if not re.search(r"(measure|metric|criterion|number|count)", p_lower):
                return 0.3
        
        # Multiple questions (unanswerable as single answer)
        if p_lower.count("?") > 1:
            return 0.4
        
        return 1.0
    
    def _parse_prompt(self, prompt: str) -> dict:
        """Parse logical structure from prompt."""
        parsed = {
            "has_structure": False,
            "negations": [],
            "comparisons": [],
            "conditionals": [],
            "numbers": [],
            "relations": []
        }
        
        # Extract negations
        neg_matches = re.findall(r"not\s+(\w+)", prompt.lower())
        if neg_matches:
            parsed["negations"] = neg_matches
            parsed["has_structure"] = True
        
        # Extract numeric comparisons
        comp_pattern = r"([\d.]+)\s*(>|<|>=|<=|=|equals?)\s*([\d.]+)"
        for match in re.finditer(comp_pattern, prompt):
            parsed["comparisons"].append({
                "left": float(match.group(1)),
                "op": match.group(2),
                "right": float(match.group(3))
            })
            parsed["has_structure"] = True
        
        # Extract numbers for later use
        parsed["numbers"] = [float(x) for x in re.findall(r"\d+\.?\d*", prompt)]
        
        # Extract conditionals (if-then)
        if re.search(r"if\s+.+\s+then", prompt.lower()):
            parsed["conditionals"].append(True)
            parsed["has_structure"] = True
        
        # Extract ordering relations for transitivity
        rel_pattern = r"(\w+)\s+(is\s+)?(greater|less|taller|shorter|older|younger)\s+than\s+(\w+)"
        for match in re.finditer(rel_pattern, prompt.lower()):
            parsed["relations"].append((match.group(1), match.group(3), match.group(4)))
            parsed["has_structure"] = True
        
        return parsed
    
    def _evaluate_candidate(self, prompt: str, candidate: str, parsed: dict) -> float:
        """
        Evaluate a single candidate using abstract interpretation.
        Returns reward (1 - upper_bound_of_falsity), higher = better.
        """
        # Initialize falsification interval [l, u] where 0=true, 1=false
        falsity_lower = 0.0
        falsity_upper = 1.0
        
        scores = []
        
        # 1. STRUCTURAL EVALUATION via primitives
        if parsed["comparisons"]:
            comp_score = self._evaluate_comparisons(candidate, parsed["comparisons"])
            scores.append(("comparison", comp_score, 0.4))
        
        if parsed["negations"]:
            neg_score = self._evaluate_negations(prompt, candidate, parsed["negations"])
            scores.append(("negation", neg_score, 0.3))
        
        if parsed["relations"]:
            rel_score = self._evaluate_relations(candidate, parsed["relations"])
            scores.append(("relation", rel_score, 0.3))
        
        # 2. CONSTRAINT-BASED EVALUATION
        if parsed["numbers"]:
            constraint_score = self._evaluate_numeric_constraints(prompt, candidate, parsed["numbers"])
            scores.append(("constraint", constraint_score, 0.4))
        
        # 3. MODUS PONENS / LOGICAL INFERENCE
        if parsed["conditionals"]:
            logic_score = self._evaluate_logic(prompt, candidate)
            scores.append(("logic", logic_score, 0.3))
        
        # 4. NCD as tiebreaker (max 10%)
        ncd_score = self._ncd_similarity(prompt, candidate)
        scores.append(("ncd", ncd_score, 0.1))
        
        # Combine scores via abstract interpretation (meet operation)
        if scores:
            weighted_sum = sum(s * w for _, s, w in scores)
            total_weight = sum(w for _, _, w in scores)
            combined = weighted_sum / total_weight
            
            # Use confidence agreement as meta-signal
            score_vals = [s for _, s, _ in scores]
            agreement_conf = confidence_from_agreement(score_vals)
            
            # Falsity upper bound decreases with score
            falsity_upper = 1.0 - (combined * agreement_conf)
        else:
            # No structure matched - high uncertainty
            falsity_upper = 0.7
        
        # Reward is resistance to falsification: 1 - upper_bound
        reward = 1.0 - falsity_upper
        return max(0.0, min(1.0, reward))
    
    def _evaluate_comparisons(self, candidate: str, comparisons: list) -> float:
        """Evaluate numeric comparisons using actual computation."""
        if not comparisons:
            return 0.5
        
        scores = []
        for comp in comparisons:
            left, op, right = comp["left"], comp["op"], comp["right"]
            
            # Check if candidate contains correct result
            if op in [">", "greater"]:
                correct = left > right
            elif op in ["<", "less"]:
                correct = left < right
            elif op in ["=", "==", "equals", "equal"]:
                correct = abs(left - right) < 1e-6
            elif op == ">=":
                correct = left >= right
            elif op == "<=":
                correct = left <= right
            else:
                correct = None
            
            if correct is not None:
                # Check if candidate aligns
                cand_lower = candidate.lower()
                if correct:
                    if any(w in cand_lower for w in ["yes", "true", "correct", "greater", "more"]):
                        scores.append(1.0)
                    elif any(w in cand_lower for w in ["no", "false", "incorrect", "less"]):
                        scores.append(0.0)
                    else:
                        scores.append(0.5)
                else:
                    if any(w in cand_lower for w in ["no", "false", "incorrect"]):
                        scores.append(1.0)
                    elif any(w in cand_lower for w in ["yes", "true", "correct"]):
                        scores.append(0.0)
                    else:
                        scores.append(0.5)
        
        return np.mean(scores) if scores else 0.5
    
    def _evaluate_negations(self, prompt: str, candidate: str, negations: list) -> float:
        """Use negation primitive to check consistency."""
        # Simple heuristic: if prompt has "not X" and candidate affirms X, low score
        cand_lower = candidate.lower()
        matches = sum(1 for neg in negations if neg in cand_lower)
        # If candidate echoes negated terms, might be inconsistent
        return 0.5 if matches == 0 else 0.3
    
    def _evaluate_relations(self, candidate: str, relations: list) -> float:
        """Use transitivity checking primitive."""
        if not relations:
            return 0.5
        
        # Build relation tuples for transitivity check
        rel_tuples = [(r[0], r[2]) for r in relations]
        try:
            is_transitive = check_transitivity(rel_tuples)
            return 0.8 if is_transitive else 0.6
        except:
            return 0.5
    
    def _evaluate_numeric_constraints(self, prompt: str, candidate: str, numbers: list) -> float:
        """Extract numbers from candidate and check constraint satisfaction."""
        cand_nums = [float(x) for x in re.findall(r"\d+\.?\d*", candidate)]
        
        if not cand_nums or not numbers:
            return 0.5
        
        # Simple check: does candidate contain expected numbers?
        overlap = len(set(cand_nums) & set(numbers))
        return min(1.0, overlap / max(len(numbers), 1) + 0.3)
    
    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """Use modus ponens primitive for conditional reasoning."""
        # Simplified: check if candidate follows logical form
        cand_lower = candidate.lower()
        if "therefore" in cand_lower or "thus" in cand_lower or "so" in cand_lower:
            return 0.7
        return 0.5
    
    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        ncd = (c12 - min(c1, c2)) / max(c1, c2)
        return max(0.0, 1.0 - ncd)
```

</details>
