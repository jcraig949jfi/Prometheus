# Information Theory + Property-Based Testing + Sensitivity Analysis

**Fields**: Mathematics, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T14:04:54.552176
**Report Generated**: 2026-04-02T08:39:54.263546

---

## Nous Analysis

**Algorithm**  
1. **Parse** prompt *P* and candidate answer *A* into a set of logical atoms using regex‑based extraction: each atom is a tuple *(entity₁, relation, entity₂, polarity, numeric‑value)*. Relations captured include negations (`not`), comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal verbs (`causes`, `leads to`), and ordering (`before`, `after`). Atoms are stored in a list; numeric values are normalized to \([0,1]\).  
2. **Feature vectors** \(f_P, f_A\) are binary (or real‑valued for numeric) indicator vectors over the universe of possible atoms observed in *P* and *A*.  
3. **Property‑based perturbation generator** (inspired by Hypothesis) creates a stochastic set \(\mathcal{P}\) of perturbed answers \(\{A_i\}\) by applying:  
   - negation flip on any polarity atom,  
   - additive Gaussian noise to numeric atoms (clipped to \([0,1]\)),  
   - swapping subject/object in commutative relations,  
   - dropping/adding conditional antecedents.  
   Each perturbation respects the original syntactic form (ensured by regex guards).  
4. **Information‑theoretic score**: estimate the mutual information \(I(f_P; f_{A_i})\) between prompt features and each perturbed answer’s features using the empirical joint distribution over \(\mathcal{P}\) (counts → probabilities).  
5. **Sensitivity analysis**: compute the variance \(\mathrm{Var}_{A_i\in\mathcal{P}}[I(f_P; f_{A_i})]\). Low variance indicates the answer’s information content is stable under perturbations.  
6. **Final score**:  
   \[
   S(A) = \frac{I(f_P; f_A)}{1 + \lambda \,\mathrm{Var}_{A_i}[I(f_P; f_{A_i})]}
   \]
   with \(\lambda\) a small constant (e.g., 0.1). Higher \(S\) means the answer preserves prompt information robustly.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, temporal/ordering relations, and polarity flags.

**Novelty** – While property‑based testing, information‑theoretic similarity, and sensitivity analysis each appear separately (e.g., robustness testing via hypothesis, mutual information for semantic similarity, finite‑difference sensitivity), their explicit combination to score reasoning answers is not documented in mainstream NLP evaluation work.

**Ratings**  
Reasoning: 8/10 — captures logical structure and quantifies information preservation.  
Metacognition: 6/10 — provides uncertainty via variance but lacks explicit self‑reflection on failure modes.  
Hypothesis generation: 7/10 — generates diverse perturbations that act as alternative hypotheses about answer correctness.  
Implementability: 9/10 — relies only on regex, numpy for counting/variance, and stdlib loops; no external dependencies.

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
**Reason**: trap_battery_failed (acc=39% cal=19% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:22:34.297040

---

## Code

**Source**: scrap

[View code](./Information_Theory---Property-Based_Testing---Sensitivity_Analysis/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Reasoning tool combining Information Theory, Property-Based Testing, and Sensitivity Analysis.

Core mechanism:
1. Parse prompt/answer into logical atoms (negations, comparatives, conditionals, numeric values)
2. Generate property-based perturbations (flip negations, add noise to numbers, swap roles)
3. Compute mutual information I(prompt_features; answer_features) for stability
4. Use sensitivity analysis (variance across perturbations) to penalize unstable answers
5. Meta-confidence detects ambiguous/unanswerable questions (presupposition, scope ambiguity, etc.)
"""

import re
import random
import zlib
from typing import List, Dict, Tuple
import math

class ReasoningTool:
    def __init__(self):
        self.lambda_var = 0.1  # sensitivity penalty weight
        random.seed(42)  # deterministic
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        meta_conf = self._meta_confidence(prompt)
        results = []
        
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            conf = min(meta_conf, self._answer_confidence(prompt, cand, score))
            reasoning = self._explain_score(prompt, cand, score, meta_conf)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        score = self._compute_score(prompt, answer)
        return self._answer_confidence(prompt, answer, score)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable questions. Returns cap on confidence."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        presup_patterns = [r'have you (stopped|quit|ceased)', r'why did .* (fail|stop|end)',
                          r'when did you (stop|quit|start)', r'do you still']
        for pat in presup_patterns:
            if re.search(pat, p_lower):
                return 0.2
        
        # Scope ambiguity: "Every X ... a Y" (same Y or different?)
        if re.search(r'every .{1,30} a ', p_lower) or re.search(r'all .{1,30} (a|an) ', p_lower):
            if 'same' not in p_lower and 'different' not in p_lower:
                return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it) (was|is|had)', p_lower) and re.search(r'who ', p_lower):
            return 0.25
        
        # False dichotomy: "Either A or B" without "only" or exhaustive markers
        if re.search(r'either .{1,50} or ', p_lower):
            if 'only' not in p_lower and 'must' not in p_lower:
                return 0.28
        
        # Subjectivity without criteria
        subjective = ['best', 'worst', 'favorite', 'better', 'worse', 'prefer']
        if any(word in p_lower for word in subjective):
            if not any(crit in p_lower for crit in ['because', 'measure', 'metric', 'criterion']):
                return 0.3
        
        # Unanswerable: "not enough information", "cannot determine"
        if re.search(r'(cannot|can\'t) (determine|know|tell|answer)', p_lower):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _parse_atoms(self, text: str) -> List[Tuple]:
        """Parse logical atoms: (entity1, relation, entity2, polarity, numeric_value)"""
        atoms = []
        text_lower = text.lower()
        
        # Negations
        neg_matches = re.finditer(r'(not|no|never|neither)\s+(\w+)', text_lower)
        for m in neg_matches:
            atoms.append(('', 'not', m.group(2), -1, None))
        
        # Comparatives with numbers
        comp_matches = re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?|greater|less)\s*(\d+\.?\d*)', text_lower)
        for m in comp_matches:
            left, op, right = float(m.group(1)), m.group(2), float(m.group(3))
            atoms.append((str(left), op, str(right), 1, (left, right)))
        
        # Conditionals
        cond_matches = re.finditer(r'if\s+(.{1,40}?)\s+then\s+(.{1,40}?)[\.\,\;]', text_lower)
        for m in cond_matches:
            atoms.append((m.group(1).strip(), 'implies', m.group(2).strip(), 1, None))
        
        # Causal
        causal_matches = re.finditer(r'(\w+)\s+(causes?|leads? to|results? in)\s+(\w+)', text_lower)
        for m in causal_matches:
            atoms.append((m.group(1), 'causes', m.group(3), 1, None))
        
        # Extract all numbers for numeric features
        numbers = re.findall(r'\d+\.?\d*', text)
        for num in numbers:
            atoms.append(('', 'number', num, 1, float(num)))
        
        return atoms
    
    def _atoms_to_features(self, atoms: List[Tuple]) -> Dict[str, float]:
        """Convert atoms to feature vector (hashable keys)"""
        features = {}
        for atom in atoms:
            ent1, rel, ent2, pol, num = atom
            key = f"{ent1}_{rel}_{ent2}_{pol}"
            features[key] = 1.0
            if num is not None:
                if isinstance(num, tuple):
                    features[f"num_{num[0]}"] = num[0]
                    features[f"num_{num[1]}"] = num[1]
                else:
                    features[f"num_{num}"] = num
        return features
    
    def _perturb_atoms(self, atoms: List[Tuple], n_perturb: int = 10) -> List[List[Tuple]]:
        """Generate property-based perturbations"""
        perturbed = []
        for _ in range(n_perturb):
            new_atoms = []
            for atom in atoms:
                ent1, rel, ent2, pol, num = atom
                
                # Flip polarity with 30% probability
                if random.random() < 0.3:
                    pol = -pol
                
                # Add noise to numeric values
                if num is not None:
                    if isinstance(num, tuple):
                        noise = random.gauss(0, 0.1)
                        num = (max(0, min(1, num[0] + noise)), max(0, min(1, num[1] + noise)))
                    else:
                        noise = random.gauss(0, 0.1)
                        num = max(0, min(1, num + noise))
                
                # Swap entity order for commutative relations with 20% probability
                if random.random() < 0.2 and rel in ['equals', '=']:
                    ent1, ent2 = ent2, ent1
                
                new_atoms.append((ent1, rel, ent2, pol, num))
            
            perturbed.append(new_atoms)
        return perturbed
    
    def _mutual_information(self, f_p: Dict, f_a: Dict) -> float:
        """Estimate MI via feature overlap and divergence"""
        all_keys = set(f_p.keys()) | set(f_a.keys())
        if not all_keys:
            return 0.0
        
        overlap = sum(1 for k in all_keys if k in f_p and k in f_a)
        
        # Numeric agreement
        num_agree = 0
        num_total = 0
        for k in all_keys:
            if k.startswith('num_') and k in f_p and k in f_a:
                diff = abs(f_p[k] - f_a[k])
                num_agree += math.exp(-diff)
                num_total += 1
        
        mi = overlap / max(1, len(all_keys))
        if num_total > 0:
            mi = 0.6 * mi + 0.4 * (num_agree / num_total)
        
        return mi
    
    def _compute_score(self, prompt: str, answer: str) -> float:
        """Combine structural, computational, and NCD scoring"""
        
        # Structural: parse and compute MI with sensitivity
        p_atoms = self._parse_atoms(prompt)
        a_atoms = self._parse_atoms(answer)
        f_p = self._atoms_to_features(p_atoms)
        f_a = self._atoms_to_features(a_atoms)
        
        mi_base = self._mutual_information(f_p, f_a)
        
        # Sensitivity analysis via perturbations
        perturbed = self._perturb_atoms(a_atoms, n_perturb=10)
        mi_values = []
        for p_atoms_pert in perturbed:
            f_pert = self._atoms_to_features(p_atoms_pert)
            mi_values.append(self._mutual_information(f_p, f_pert))
        
        variance = sum((mi - mi_base)**2 for mi in mi_values) / max(1, len(mi_values))
        structural_score = mi_base / (1 + self.lambda_var * variance)
        
        # Computational: solve specific problem types
        comp_score = self._computational_solve(prompt, answer)
        
        # NCD as tiebreaker
        ncd = self._ncd(prompt, answer)
        
        # Weighted combination
        final = 0.55 * structural_score + 0.3 * comp_score + 0.15 * (1 - ncd)
        return max(0.0, min(1.0, final))
    
    def _computational_solve(self, prompt: str, answer: str) -> float:
        """Constructive computation for specific problem types"""
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # Numeric comparison (e.g., "Is 9.11 > 9.9?")
        comp_match = re.search(r'is\s+(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', p_lower)
        if comp_match:
            left, op, right = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            truth = self._eval_comparison(left, op, right)
            
            answer_yes = 'yes' in a_lower or 'true' in a_lower or 'correct' in a_lower
            answer_no = 'no' in a_lower or 'false' in a_lower or 'incorrect' in a_lower
            
            if (truth and answer_yes) or (not truth and answer_no):
                return 1.0
            return 0.0
        
        # Transitivity: "A > B, B > C, is A > C?"
        if '>' in p_lower or '<' in p_lower:
            numbers = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            if len(numbers) >= 2:
                is_ascending = all(numbers[i] < numbers[i+1] for i in range(len(numbers)-1))
                is_descending = all(numbers[i] > numbers[i+1] for i in range(len(numbers)-1))
                
                if (is_ascending and 'yes' in a_lower) or (is_descending and 'yes' in a_lower):
                    return 0.8
        
        # Modus tollens: "If A then B. Not B. Therefore?"
        if 'if' in p_lower and 'not' in p_lower and 'then' in p_lower:
            if 'not' in a_lower:
                return 0.7
        
        return 0.0
    
    def _eval_comparison(self, left: float, op: str, right: float) -> bool:
        """Evaluate numeric comparison"""
        if '>' in op:
            return left > right
        elif '<' in op:
            return left < right
        elif '=' in op or 'equal' in op:
            return abs(left - right) < 1e-6
        return False
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _answer_confidence(self, prompt: str, answer: str, score: float) -> float:
        """Convert score to confidence, capped by structural certainty"""
        
        # Never overconfident unless we computed an answer
        comp_score = self._computational_solve(prompt, answer)
        if comp_score > 0.9:
            return min(0.95, score)
        
        # If no structural match, be uncertain
        p_atoms = self._parse_atoms(prompt)
        a_atoms = self._parse_atoms(answer)
        if not p_atoms and not a_atoms:
            return min(0.3, score)
        
        # Scale confidence by score
        if score > 0.8:
            return 0.75
        elif score > 0.6:
            return 0.6
        elif score > 0.4:
            return 0.45
        else:
            return 0.25
    
    def _explain_score(self, prompt: str, answer: str, score: float, meta_conf: float) -> str:
        """Brief explanation of scoring"""
        if meta_conf < 0.3:
            return f"Question ambiguous/unanswerable (meta={meta_conf:.2f})"
        
        comp = self._computational_solve(prompt, answer)
        if comp > 0.5:
            return f"Computational match (score={score:.2f})"
        
        return f"Structural+MI score={score:.2f}"
```

</details>
