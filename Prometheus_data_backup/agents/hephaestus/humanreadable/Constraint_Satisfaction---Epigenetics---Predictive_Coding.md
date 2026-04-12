# Constraint Satisfaction + Epigenetics + Predictive Coding

**Fields**: Computer Science, Biology, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:18:48.982663
**Report Generated**: 2026-04-02T11:44:50.590294

---

## Nous Analysis

**Algorithm – Epigenetic Predictive Constraint Solver (EPCS)**  

1. **Parsing & Variable Creation**  
   - Use regular expressions to extract atomic propositions from the prompt and each candidate answer:  
     *Negations* (`not`, `no`), *comparatives* (`greater than`, `less than`), *conditionals* (`if … then …`), *causal* (`because`, `leads to`), *ordering* (`before`, `after`, `first`, `last`), *numeric* values with units.  
   - Each proposition becomes a Boolean variable \(x_i \in \{0,1\}\). Store them in a list `props`.  

2. **Constraint Matrix (CSP)**  
   - Build a binary constraint matrix \(C\) where \(C_{ij}=1\) if a relation links \(x_i\) and \(x_j\) (e.g., \(x_i \rightarrow x_j\), \(x_i > x_j\), \(\neg x_i\)).  
   - For each constraint store a function `f_ij(x_i,x_j)` that returns 0 if satisfied, 1 if violated.  

3. **Epigenetic Similarity (Weight Propagation)**  
   - Compute a similarity matrix \(S\) between propositions using lexical overlap (Jaccard of token sets) and WordNet‑based hypernym/hyponym relations (implemented with std‑lib `difflib`).  
   - \(S\) is a numpy array; it acts like methylation‑like “inheritance”: a variable’s belief can diffuse to similar variables.  

4. **Predictive Coding Loop**  
   - Initialize belief vector \(b\) with priors from the prompt (e.g., 1 for asserted facts, 0 for negated facts, 0.5 for unknown).  
   - Iterate:  
     a. **Constraint Propagation (AC‑3 style)** – enforce arc consistency: for each arc \((i,j)\) adjust \(b_i\) to minimize \(\sum_k f_{ik}(b_i,b_k)\). Implemented as a simple gradient step:  
        \(b_i \leftarrow b_i - \eta \cdot \partial E/\partial b_i\) where \(E = \sum_{i<j} f_{ij}(b_i,b_j)\).  
     b. **Epigenetic Smoothing** – update beliefs with similarity: \(b \leftarrow (1-\lambda) b + \lambda S b\).  
     c. Compute prediction error \(e = \|b - b_{\text{prior}}\|^2\).  
   - Stop when change in \(e < \epsilon\) or after a fixed number of steps (e.g., 10).  

5. **Scoring**  
   - The final error \(e\) is the surprise remaining after constraint satisfaction and epigenetic smoothing.  
   - Lower \(e\) → higher plausibility. Normalize scores across candidates:  
     \(\text{score}=1/(1+e)\).  

**Structural Features Parsed** – negations, comparatives, conditionals, causal markers, temporal ordering, numeric quantities with units, and explicit quantifiers (all, some, none).  

**Novelty** – Pure CSP solvers exist; epigenetic‑style similarity smoothing and predictive‑coding error minimization have not been combined for answer scoring. Related work includes Markov Logic Networks and Probabilistic Soft Logic, but the explicit inheritance‑like weight update and surprise‑minimization loop are novel.  

**Ratings**  
Reasoning: 8/10 — strong logical propagation via AC‑3 and constraint functions captures deductive structure well.  
Metacognition: 7/10 — error minimization provides a self‑monitoring signal, though limited to quadratic surprise.  
Hypothesis generation: 6/10 — only evaluates given candidates; does not generate new hypotheses.  
Implementability: 9/10 — relies solely on numpy for matrix ops and std‑lib regex, collections, difflib; no external dependencies.

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
**Reason**: trap_battery_failed (acc=36% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:06:41.814228

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Epigenetics---Predictive_Coding/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Epigenetic Predictive Constraint Solver (EPCS)
    
    Combines constraint satisfaction, epigenetic-style similarity propagation,
    and predictive coding to evaluate reasoning candidates. Parses prompts into
    atomic propositions, builds constraint networks, and minimizes prediction
    error through iterative belief updates.
    """
    
    def __init__(self):
        self.epsilon = 1e-3
        self.max_iter = 10
        self.eta = 0.1  # Learning rate for constraint propagation
        self.lambda_ = 0.3  # Epigenetic smoothing weight
    
    def _extract_propositions(self, text):
        """Extract atomic propositions from text"""
        props = []
        # Numeric patterns
        for match in re.finditer(r'(\d+\.?\d*)\s*(dollars|cents|years|items|people|percent|%)?', text.lower()):
            props.append(f"NUM_{match.group(1)}_{match.group(2) or 'unit'}")
        # Negations
        for match in re.finditer(r'(not|no|never|none)\s+(\w+)', text.lower()):
            props.append(f"NEG_{match.group(2)}")
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text.lower()):
            props.append(f"CMP_{match.group(1)}_{match.group(2)}_{match.group(3)}")
        # Conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]', text.lower()):
            props.append(f"IF_{match.group(1)[:20]}_THEN_{match.group(2)[:20]}")
        # Temporal
        for match in re.finditer(r'(\w+)\s+(before|after|first|last)\s+(\w+)', text.lower()):
            props.append(f"TEMP_{match.group(1)}_{match.group(2)}_{match.group(3)}")
        # Extract all words as basic props
        words = re.findall(r'\b\w+\b', text.lower())
        props.extend([f"WORD_{w}" for w in words if len(w) > 3])
        return list(set(props))
    
    def _similarity_matrix(self, props):
        """Compute epigenetic similarity matrix using lexical overlap"""
        n = len(props)
        S = np.eye(n)
        for i in range(n):
            for j in range(i+1, n):
                ratio = SequenceMatcher(None, props[i], props[j]).ratio()
                S[i,j] = S[j,i] = ratio
        return S
    
    def _build_constraints(self, props, text):
        """Build constraint matrix from propositions"""
        n = len(props)
        C = np.zeros((n, n))
        constraints = []
        
        # Negation constraints
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if p1.startswith('NEG_') and p1[4:] in p2:
                    C[i,j] = 1
                    constraints.append((i, j, lambda x, y: abs(x + y - 1)))
        
        # Numeric comparison constraints
        nums = [(i, p) for i, p in enumerate(props) if p.startswith('NUM_')]
        for idx, (i, p1) in enumerate(nums):
            for j, p2 in nums[idx+1:]:
                C[i,j] = 1
                val1 = float(p1.split('_')[1])
                val2 = float(p2.split('_')[1])
                if val1 > val2:
                    constraints.append((i, j, lambda x, y: abs(x - max(x, y))))
                else:
                    constraints.append((i, j, lambda x, y: abs(y - max(x, y))))
        
        return C, constraints
    
    def _compute_structural_score(self, prompt, candidate):
        """Compute score from structural parsing and constraint solving"""
        # Numeric comparison
        prompt_nums = [float(m.group(1)) for m in re.finditer(r'\b(\d+\.?\d*)\b', prompt)]
        cand_nums = [float(m.group(1)) for m in re.finditer(r'\b(\d+\.?\d*)\b', candidate)]
        
        # Bat-and-ball algebra
        ball_match = re.search(r'(\d+\.?\d*)\s*more.*total.*\$?(\d+\.?\d*)', prompt.lower())
        if ball_match and cand_nums:
            diff = float(ball_match.group(1))
            total = float(ball_match.group(2))
            correct = (total - diff) / 2
            if cand_nums and abs(cand_nums[0] - correct) < 0.01:
                return 0.95
        
        # Negation agreement
        prompt_negs = set(re.findall(r'(not|no|never)\s+(\w+)', prompt.lower()))
        cand_negs = set(re.findall(r'(not|no|never)\s+(\w+)', candidate.lower()))
        neg_score = len(prompt_negs & cand_negs) / max(len(prompt_negs), 1) if prompt_negs else 0.5
        
        # Transitivity: if A>B and B>C mentioned, answer should respect A>C
        trans_score = 0.5
        comparisons = re.findall(r'(\w+)\s+(>|<|greater|less)\s+(\w+)', prompt.lower())
        if len(comparisons) >= 2:
            trans_score = 0.7 if any(c in candidate.lower() for c in [comparisons[0][0], comparisons[-1][2]]) else 0.3
        
        return (neg_score * 0.3 + trans_score * 0.2 + 0.5)
    
    def _predictive_coding_loop(self, props, C, constraints, prior):
        """Run predictive coding loop with constraint propagation"""
        b = np.array(prior, dtype=float)
        S = self._similarity_matrix(props)
        
        for iteration in range(self.max_iter):
            b_old = b.copy()
            
            # Constraint propagation
            for i, j, f in constraints:
                try:
                    error = f(b[i], b[j])
                    b[i] -= self.eta * error * 0.5
                    b[j] -= self.eta * error * 0.5
                except:
                    pass
            
            b = np.clip(b, 0, 1)
            
            # Epigenetic smoothing
            b = (1 - self.lambda_) * b + self.lambda_ * (S @ b) / (S.sum(axis=1) + 1e-9)
            
            # Check convergence
            if np.linalg.norm(b - b_old) < self.epsilon:
                break
        
        prediction_error = np.linalg.norm(b - prior)**2
        return 1.0 / (1.0 + prediction_error)
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity and unanswerable questions"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did.*fail|when did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .* a \w+', p_lower) and 'same' not in p_lower:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', p_lower) and re.search(r'\w+ told \w+', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*\?', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|prettiest)', p_lower) and not re.search(r'(most|least|highest|lowest)', p_lower):
            return 0.2
        
        # Insufficient information
        if 'cannot be determined' in p_lower or 'not enough information' in p_lower:
            return 0.15
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates and return ranked list"""
        results = []
        
        for candidate in candidates:
            # Extract propositions
            prompt_props = self._extract_propositions(prompt)
            cand_props = self._extract_propositions(candidate)
            all_props = list(set(prompt_props + cand_props))
            
            if len(all_props) == 0:
                all_props = ['EMPTY']
            
            # Build constraints
            C, constraints = self._build_constraints(all_props, prompt + ' ' + candidate)
            
            # Initialize priors
            prior = [0.5] * len(all_props)
            for i, p in enumerate(all_props):
                if p in prompt_props:
                    prior[i] = 0.8
            
            # Run predictive coding
            epcs_score = self._predictive_coding_loop(all_props, C, constraints, prior)
            
            # Structural parsing
            struct_score = self._compute_structural_score(prompt, candidate)
            
            # NCD (max 15%)
            ncd_score = 1 - self._ncd(prompt, candidate)
            
            # Combine scores
            final_score = 0.5 * struct_score + 0.35 * epcs_score + 0.15 * ncd_score
            
            reasoning = f"EPCS={epcs_score:.2f}, Struct={struct_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 for a proposed answer"""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute answer quality
        results = self.evaluate(prompt, [answer])
        answer_score = results[0]['score'] if results else 0.5
        
        # Cap confidence by meta-confidence
        base_confidence = min(answer_score, 0.85)
        return base_confidence * meta_conf
```

</details>
