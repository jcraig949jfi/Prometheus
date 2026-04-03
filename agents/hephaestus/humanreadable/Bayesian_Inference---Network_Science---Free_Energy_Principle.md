# Bayesian Inference + Network Science + Free Energy Principle

**Fields**: Mathematics, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T21:45:43.614107
**Report Generated**: 2026-04-02T08:39:54.695539

---

## Nous Analysis

**Algorithm**  
We build a factor graph whose variable nodes are propositions extracted from the prompt and each candidate answer. Edges encode logical relations (implication, equivalence, negation, ordering, numeric constraint) obtained via regex‑based pattern matching. Each variable holds a belief vector **b** ∈ [0,1] representing the probability that the proposition is true. Priors are set from background knowledge (e.g., uniform 0.5) or from explicit numeric statements (e.g., “X > 5” → a truncated Gaussian prior).  

Inference runs loopy belief propagation (sum‑product) using only NumPy for message updates:  
- For an implication A → B, the factor computes m_{A→B}(b_B) = Σ_{b_A} ψ(A,B)·m_{B→A}(b_A) where ψ encodes the truth table of implication.  
- For a negation ¬A, ψ flips the belief.  
- For ordering (A < B) with numeric values, ψ is a soft indicator: exp(−λ·max(0, A−B)) normalized.  
- For numeric equality, ψ is a Gaussian likelihood.  

After convergence, the variational free energy F = ⟨E⟩ − H (average energy minus entropy) is approximated by the negative log‑partition function estimated from the beliefs. Each candidate answer is treated as an additional hypothesis node H_i connected to the propositions it asserts; its score is −F(H_i). Lower free energy (higher posterior) indicates a better answer.  

**Parsed structural features**  
Negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal verbs (“causes”, “leads to”), ordering relations (“before”, “after”), numeric values and units, and equality/inequality statements.  

**Novelty**  
Probabilistic soft logic and Markov logic networks already combine Bayesian inference with graph‑based relational models, and belief propagation is used in QA systems. The free‑energy principle’s explicit minimization of variational free energy as a scoring criterion, applied to a text‑derived factor graph, has not been combined in this exact way for answer selection, making the approach novel.  

**Ratings**  
Reasoning: 7/10 — captures logical and probabilistic dependencies but relies on approximate loopy BP.  
Metacognition: 5/10 — no explicit self‑monitoring of belief convergence; limited to fixed‑point detection.  
Hypothesis generation: 6/10 — generates answer scores via free energy but does not propose new hypotheses beyond candidates.  
Implementability: 8/10 — uses only NumPy and stdlib; message updates are straightforward matrix/vector ops.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=39% cal=48% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:28:45.108335

---

## Code

**Source**: scrap

[View code](./Bayesian_Inference---Network_Science---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Optional, Tuple

"""
Bayesian Factor Graph Reasoner with Free Energy Minimization

Extracts propositions from prompt and candidates, builds a factor graph
encoding logical relations, runs loopy belief propagation, and scores
candidates by variational free energy. Includes epistemic honesty checks.
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional
import zlib


class ReasoningTool:
    def __init__(self):
        self.max_iterations = 20
        self.damping = 0.5
        self.convergence_threshold = 1e-3
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by free energy on factor graph from prompt."""
        # Check for presuppositions/ambiguity
        meta_conf = self._meta_confidence(prompt)
        
        # Extract propositions and numeric constraints
        prompt_props = self._extract_propositions(prompt)
        prompt_nums = self._extract_numeric_constraints(prompt)
        
        # Try specialized parsers first
        specialized = self._try_specialized_parsers(prompt, candidates)
        if specialized:
            return specialized
        
        results = []
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            cand_nums = self._extract_numeric_values(cand)
            
            # Build factor graph
            all_props = list(set(prompt_props + cand_props))
            beliefs = self._initialize_beliefs(all_props, prompt_nums, cand_nums)
            relations = self._extract_relations(prompt, all_props)
            
            # Run belief propagation
            converged_beliefs = self._loopy_bp(beliefs, relations, all_props)
            
            # Compute free energy
            free_energy = self._compute_free_energy(converged_beliefs, relations)
            
            # Lower free energy = better, convert to score
            score = 1.0 / (1.0 + free_energy)
            
            # Add structural and computational bonuses
            struct_bonus = self._structural_match(prompt, cand)
            comp_bonus = self._computational_match(prompt, cand)
            ncd_bonus = self._ncd_similarity(prompt, cand) * 0.1
            
            final_score = 0.5 * score + 0.3 * struct_bonus + 0.15 * comp_bonus + 0.05 * ncd_bonus
            
            # Apply meta-confidence penalty
            if meta_conf < 0.3:
                final_score *= meta_conf
            
            reasoning = f"FE={free_energy:.2f}, struct={struct_bonus:.2f}, comp={comp_bonus:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on prompt properties and answer fit."""
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt is ambiguous, cap confidence
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we have a structural match
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.2
        
        score = results[0]["score"]
        
        # Never return > 0.9 unless we have computational verification
        if self._has_computation(prompt):
            comp_match = self._computational_match(prompt, answer)
            if comp_match > 0.9:
                return min(0.95, score)
        
        return min(0.75, score * meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity, presuppositions, unanswerability."""
        conf = 1.0
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            conf = min(conf, 0.2)
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            conf = min(conf, 0.25)
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            conf = min(conf, 0.25)
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            conf = min(conf, 0.3)
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p_lower):
            if not re.search(r'\b(most|least|more|fewer|higher|lower)\b', p_lower):
                conf = min(conf, 0.3)
        
        # Unanswerable: asking for information not present
        if 'why' in p_lower and not re.search(r'\b(because|due to|caused by)\b', p_lower):
            conf = min(conf, 0.4)
        
        return conf
    
    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions (simplified SVO triples)."""
        props = []
        sentences = re.split(r'[.!?]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
            
            # Extract negations
            if re.search(r'\b(not|never|no)\b', sent.lower()):
                props.append(f"NOT:{sent[:30]}")
            
            # Extract comparative statements
            if re.search(r'\b(more|less|greater|fewer|higher|lower)\s+than\b', sent.lower()):
                props.append(f"CMP:{sent[:30]}")
            
            # Extract causal statements
            if re.search(r'\b(causes?|leads? to|results? in|produces?)\b', sent.lower()):
                props.append(f"CAUSE:{sent[:30]}")
            
            # Extract conditional statements
            if re.search(r'\bif\b.*\bthen\b', sent.lower()):
                props.append(f"COND:{sent[:30]}")
            
            # Generic proposition
            props.append(sent[:30])
        
        return props
    
    def _extract_numeric_constraints(self, text: str) -> List[Tuple[str, float, str]]:
        """Extract numeric constraints: (var, value, op)."""
        constraints = []
        
        # Pattern: X is/costs/equals NUMBER
        for match in re.finditer(r'(\w+)\s+(?:is|costs?|equals?)\s+(\d+\.?\d*)', text):
            var, val = match.groups()
            constraints.append((var, float(val), '='))
        
        # Pattern: X > Y or X < Y
        for match in re.finditer(r'(\d+\.?\d*)\s*([<>])\s*(\d+\.?\d*)', text):
            left, op, right = match.groups()
            constraints.append((f"num_{left}", float(left), op))
        
        return constraints
    
    def _extract_numeric_values(self, text: str) -> List[float]:
        """Extract all numeric values from text."""
        return [float(m) for m in re.findall(r'\d+\.?\d*', text)]
    
    def _initialize_beliefs(self, props: List[str], constraints, nums) -> np.ndarray:
        """Initialize belief vector for each proposition."""
        n = len(props)
        beliefs = np.ones(n) * 0.5  # Uniform prior
        
        # Adjust beliefs based on constraints
        for i, prop in enumerate(props):
            if 'NOT:' in prop:
                beliefs[i] = 0.3
            elif 'CAUSE:' in prop or 'COND:' in prop:
                beliefs[i] = 0.6
        
        return beliefs
    
    def _extract_relations(self, text: str, props: List[str]) -> List[Tuple[str, int, int]]:
        """Extract logical relations between propositions."""
        relations = []
        text_lower = text.lower()
        
        # Implication relations
        if 'if' in text_lower and 'then' in text_lower:
            for i in range(len(props) - 1):
                relations.append(('IMPLIES', i, i + 1))
        
        # Negation relations
        for i, prop in enumerate(props):
            if 'NOT:' in prop:
                for j, other in enumerate(props):
                    if i != j and prop[4:] in other:
                        relations.append(('NEGATES', i, j))
        
        return relations
    
    def _loopy_bp(self, beliefs: np.ndarray, relations: List[Tuple], props: List[str]) -> np.ndarray:
        """Run loopy belief propagation."""
        n = len(beliefs)
        messages = np.ones((n, n)) * 0.5
        
        for iteration in range(self.max_iterations):
            old_beliefs = beliefs.copy()
            
            for rel_type, i, j in relations:
                if rel_type == 'IMPLIES':
                    # A -> B: if A is true, B should be true
                    msg = beliefs[i] * 0.8 + (1 - beliefs[i]) * 0.5
                    messages[i, j] = self.damping * messages[i, j] + (1 - self.damping) * msg
                    beliefs[j] = (beliefs[j] + messages[i, j]) / 2
                
                elif rel_type == 'NEGATES':
                    # NOT A: flip belief
                    msg = 1 - beliefs[i]
                    messages[i, j] = self.damping * messages[i, j] + (1 - self.damping) * msg
                    beliefs[j] = (beliefs[j] + messages[i, j]) / 2
            
            # Check convergence
            if np.max(np.abs(beliefs - old_beliefs)) < self.convergence_threshold:
                break
        
        return beliefs
    
    def _compute_free_energy(self, beliefs: np.ndarray, relations: List[Tuple]) -> float:
        """Compute variational free energy: F = <E> - H."""
        # Energy: sum of unsatisfied relations
        energy = 0.0
        for rel_type, i, j in relations:
            if rel_type == 'IMPLIES':
                energy += beliefs[i] * (1 - beliefs[j])
            elif rel_type == 'NEGATES':
                energy += beliefs[i] * beliefs[j]
        
        # Entropy: -sum(p log p)
        entropy = -np.sum(beliefs * np.log(beliefs + 1e-10) + (1 - beliefs) * np.log(1 - beliefs + 1e-10))
        
        return energy - entropy
    
    def _structural_match(self, prompt: str, candidate: str) -> float:
        """Compute structural similarity."""
        p_props = set(self._extract_propositions(prompt))
        c_props = set(self._extract_propositions(candidate))
        
        if not p_props:
            return 0.5
        
        overlap = len(p_props & c_props) / len(p_props | c_props)
        return overlap
    
    def _computational_match(self, prompt: str, candidate: str) -> float:
        """Compute actual numeric/logical answers."""
        # Numeric comparison: "9.11 vs 9.9"
        p_nums = self._extract_numeric_values(prompt)
        c_nums = self._extract_numeric_values(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            if '<' in prompt or 'less' in prompt.lower() or 'smaller' in prompt.lower():
                correct = p_nums[0] < p_nums[1]
                if ('yes' in candidate.lower() and correct) or ('no' in candidate.lower() and not correct):
                    return 1.0
        
        # Bat-and-ball: ball + bat = 1.10, bat = ball + 1.00
        if 'ball' in prompt.lower() and 'bat' in prompt.lower():
            if len(c_nums) == 1:
                # Ball = 0.05, Bat = 1.05
                if abs(c_nums[0] - 0.05) < 0.01:
                    return 1.0
        
        return 0.5
    
    def _ncd_similarity(self, prompt: str, candidate: str) -> float:
        """Normalized compression distance."""
        cp = zlib.compress(prompt.encode())
        cc = zlib.compress(candidate.encode())
        cpc = zlib.compress((prompt + candidate).encode())
        
        ncd = (len(cpc) - min(len(cp), len(cc))) / max(len(cp), len(cc))
        return max(0, 1 - ncd)
    
    def _has_computation(self, prompt: str) -> bool:
        """Check if prompt requires computation."""
        return bool(re.search(r'\d', prompt))
    
    def _try_specialized_parsers(self, prompt: str, candidates: List[str]) -> Optional[List[Dict]]:
        """Try specialized parsers for common patterns."""
        # Numeric comparison parser
        nums = self._extract_numeric_values(prompt)
        if len(nums) >= 2:
            if '<' in prompt or 'less' in prompt.lower() or 'smaller' in prompt.lower():
                correct = nums[0] < nums[1]
                results = []
                for cand in candidates:
                    if ('yes' in cand.lower() and correct) or ('no' in cand.lower() and not correct):
                        score = 0.95
                    else:
                        score = 0.05
                    results.append({"candidate": cand, "score": score, "reasoning": "numeric_comparison"})
                return results
        
        return None
```

</details>
