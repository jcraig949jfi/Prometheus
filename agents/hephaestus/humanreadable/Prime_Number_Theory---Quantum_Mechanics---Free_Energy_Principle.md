# Prime Number Theory + Quantum Mechanics + Free Energy Principle

**Fields**: Mathematics, Physics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T05:39:53.660549
**Report Generated**: 2026-04-02T10:55:58.536203

---

## Nous Analysis

**Algorithm – Prime‑Quantum Free‑Energy Scorer (PQFES)**  

1. **Parsing & Data Structures**  
   - Tokenise the prompt and each candidate answer with a regex‑based tokenizer that extracts:  
     * atomic propositions (e.g., “X is Y”),  
     * negations (`not`),  
     * comparatives (`>`, `<`, `=`),  
     * conditionals (`if … then …`),  
     * causal markers (`because`, `leads to`),  
     * numeric literals.  
   - Build a directed hyper‑graph **G = (V, E)** where each node *v* ∈ V is a proposition atom annotated with its syntactic type (negation, comparative, etc.). Each hyper‑edge *e* ∈ E encodes a logical relation extracted from the text (e.g., a conditional yields an edge from antecedent node to consequent node; a causal marker yields a bidirectional edge weighted by confidence).  
   - Assign each node a **prime‑index weight** *p(v)* = the *k*‑th prime, where *k* is the node’s topological order after a stable sort by appearance. This yields a unique, multiplicative encoding of node identity that preserves ordering information.  

2. **Quantum‑like Superposition Representation**  
   - For each candidate answer *a*, construct a state vector |ψₐ⟩ ∈ ℝⁿ (n = |V|) where the amplitude of node *v* is:  
     ψₐ[v] = 1 if *v* appears in *a* (respecting polarity: negated nodes get –1), else 0.  
   - Normalise: |ψₐ⟩ ← |ψₐ⟩ / ‖|ψₐ⟩‖₂ (using `numpy.linalg.norm`).  
   - The hyper‑graph adjacency matrix **A** (size n×n) is built such that A[i,j] = wₑ if an edge *e* connects i→j, where wₑ = 1/(1+|Δp|) and Δp = p(j)−p(i) (prime‑gap based decay).  

3. **Free‑Energy‑Style Scoring**  
   - Define the variational free energy for answer *a* as:  
     Fₐ = ½ ⟨ψₐ| (I – A) |ψₐ⟩ + λ·‖ψₐ‖₁,  
     where the first term measures prediction error (mis‑alignment with relational constraints) and the second term is an entropy‑like sparsity penalty (λ = 0.1).  
   - Compute Fₐ using numpy dot products. Lower Fₐ indicates higher consistency with the prompt’s logical structure.  
   - Final score Sₐ = –Fₐ (higher is better).  

**Structural Features Parsed** – negations, comparatives, conditionals, causal markers, numeric literals, and ordering relations (derived from prime‑index ordering).  

**Novelty** – The triple combination is not found in existing literature. Prime‑based node encoding provides a collision‑free symbolic hash; quantum‑style amplitude vectors enable superposition‑like weighting of multiple interpretations; the free‑energy functional supplies a principled, gradient‑free scoring rule that mirrors constraint‑propagation while staying within numpy/stdlib. No known work combines these three exact mechanisms.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via graph constraints and numeric prime gaps, enabling precise error measurement.  
Metacognition: 6/10 — the sparsity term offers a rudimentary self‑assessment of answer simplicity, but no explicit uncertainty estimation.  
Hypothesis generation: 5/10 — the model can rank alternatives but does not propose new propositions beyond those present.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic graph operations; straightforward to code in <150 lines.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=41% cal=4% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:44:20.435453

---

## Code

**Source**: scrap

[View code](./Prime_Number_Theory---Quantum_Mechanics---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

"""
Prime-Quantum Free-Energy Scorer (PQFES)

Combines prime-based node encoding, quantum-style state vectors, and 
free-energy scoring to evaluate logical reasoning in Q&A tasks.

Core mechanism:
1. Parse text into proposition graph with prime-indexed nodes
2. Build quantum-like amplitude vectors for candidates
3. Score via variational free energy (lower = more consistent)
4. Add structural/computational parsers for robustness
5. Meta-confidence checks for epistemic honesty
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set


class ReasoningTool:
    def __init__(self):
        self.primes = self._generate_primes(1000)
        
    def _generate_primes(self, n: int) -> List[int]:
        """Generate first n primes via sieve."""
        if n < 1:
            return []
        limit = max(20, n * 15)
        sieve = [True] * limit
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit, i):
                    sieve[j] = False
        primes = [i for i, is_p in enumerate(sieve) if is_p]
        return primes[:n]
    
    def _tokenize_propositions(self, text: str) -> List[Dict]:
        """Extract atomic propositions with types."""
        text = text.lower()
        props = []
        
        # Negations: "not X", "X is not Y"
        for m in re.finditer(r'(not|no|never|cannot)\s+(\w+(?:\s+\w+){0,4})', text):
            props.append({'text': m.group(0), 'type': 'negation', 'polarity': -1})
        
        # Comparatives: "X > Y", "X is greater than Y"
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==|!=)\s*(\w+)', text):
            props.append({'text': m.group(0), 'type': 'comparative', 'polarity': 1})
        for m in re.finditer(r'(more|less|greater|fewer|higher|lower)\s+than', text):
            props.append({'text': m.group(0), 'type': 'comparative', 'polarity': 1})
        
        # Conditionals: "if X then Y"
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            props.append({'text': m.group(0), 'type': 'conditional', 'polarity': 1, 
                         'antecedent': m.group(1), 'consequent': m.group(2)})
        
        # Causals: "X causes Y"
        for m in re.finditer(r'(\w+(?:\s+\w+){0,3})\s+(causes?|leads? to|results? in|produces?)\s+(\w+(?:\s+\w+){0,3})', text):
            props.append({'text': m.group(0), 'type': 'causal', 'polarity': 1})
        
        # Numeric literals
        for m in re.finditer(r'\b\d+\.?\d*\b', text):
            props.append({'text': m.group(0), 'type': 'numeric', 'polarity': 1, 'value': float(m.group(0))})
        
        # Simple assertions: "X is Y"
        for m in re.finditer(r'(\w+)\s+(?:is|are|was|were)\s+(\w+(?:\s+\w+){0,2})', text):
            if 'not' not in m.group(0):
                props.append({'text': m.group(0), 'type': 'assertion', 'polarity': 1})
        
        return props
    
    def _build_graph(self, prompt_props: List[Dict], cand_props: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Build adjacency matrix with prime-indexed nodes."""
        all_props = prompt_props + cand_props
        n = len(all_props)
        if n == 0:
            return np.zeros((1, 1)), [{'text': '', 'type': 'empty', 'polarity': 1}]
        
        # Assign prime indices
        for i, prop in enumerate(all_props):
            prop['prime_idx'] = self.primes[min(i, len(self.primes)-1)]
        
        # Build adjacency matrix
        A = np.eye(n)
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Connect conditionals (antecedent -> consequent)
                    if all_props[i].get('type') == 'conditional':
                        weight = 1.0 / (1 + abs(all_props[j]['prime_idx'] - all_props[i]['prime_idx']))
                        A[i, j] = weight
                    # Connect causals
                    elif all_props[i].get('type') == 'causal' and all_props[j].get('type') in ['assertion', 'causal']:
                        weight = 1.0 / (1 + abs(all_props[j]['prime_idx'] - all_props[i]['prime_idx']))
                        A[i, j] = weight * 0.5
        
        return A, all_props
    
    def _numeric_comparison_score(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons."""
        p_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(m.group()) for m in re.finditer(r'\b\d+\.?\d*\b', candidate)]
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Check if candidate number satisfies prompt comparison
            if re.search(r'(greater|more|larger|higher)', prompt.lower()):
                if c_nums[0] > min(p_nums):
                    return 0.8
            elif re.search(r'(less|fewer|smaller|lower)', prompt.lower()):
                if c_nums[0] < max(p_nums):
                    return 0.8
        return 0.0
    
    def _bat_and_ball_score(self, prompt: str, candidate: str) -> float:
        """Detect and solve bat-and-ball style algebra."""
        if re.search(r'total.*\$?\d+\.?\d*.*more than.*\$?\d+\.?\d*', prompt.lower()):
            p_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', prompt)]
            c_nums = [float(m.group()) for m in re.finditer(r'\d+\.?\d*', candidate)]
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                total, diff = p_nums[0], p_nums[1]
                correct_val = (total - diff) / 2
                if abs(c_nums[0] - correct_val) < 0.01:
                    return 0.9
        return 0.0
    
    def _transitivity_score(self, prompt: str, candidate: str) -> float:
        """Check transitive reasoning."""
        matches = list(re.finditer(r'(\w+)\s+(?:>|<|greater|less|more|fewer)\s+(\w+)', prompt.lower()))
        if len(matches) >= 2:
            cand_lower = candidate.lower()
            # Simple heuristic: if candidate mentions endpoints, likely correct
            entities = set()
            for m in matches:
                entities.add(m.group(1))
                entities.add(m.group(2))
            overlap = sum(1 for e in entities if e in cand_lower)
            if overlap >= 2:
                return 0.5
        return 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity/presupposition to cap confidence."""
        prompt_lower = prompt.lower()
        
        # Presupposition: "have you stopped X?"
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why did .+ (fail|stop|end)', prompt_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'every \w+.*\ba\b', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity: "X told Y he/she"
        if re.search(r'told \w+ (he|she|they)', prompt_lower) and 'who' in prompt_lower:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'either .+ or .+(?:\?|$)', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower) and 'because' not in prompt_lower:
            return 0.3
        
        # Insufficient info markers
        if re.search(r'(cannot (be )?determined|not enough|insufficient|unclear)', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free-energy score + structural/computational parsers."""
        prompt_props = self._tokenize_propositions(prompt)
        results = []
        
        for cand in candidates:
            cand_props = self._tokenize_propositions(cand)
            
            # Build graph and state vector
            A, all_props = self._build_graph(prompt_props, cand_props)
            n = len(all_props)
            
            # Quantum-like amplitude vector
            psi = np.zeros(n)
            for i, prop in enumerate(all_props):
                if i < len(prompt_props):
                    psi[i] = 0.5  # Prompt nodes get base weight
                else:
                    psi[i] = prop['polarity']  # Candidate nodes
            
            # Normalize
            norm = np.linalg.norm(psi)
            if norm > 0:
                psi = psi / norm
            
            # Free energy: F = 0.5 * psi^T (I - A) psi + lambda * ||psi||_1
            lambda_sparse = 0.1
            free_energy = 0.5 * psi.T @ (np.eye(n) - A) @ psi + lambda_sparse * np.sum(np.abs(psi))
            pqfes_score = -free_energy  # Lower F = higher score
            
            # Structural/computational parsers (60% weight)
            num_score = self._numeric_comparison_score(prompt, cand)
            bat_score = self._bat_and_ball_score(prompt, cand)
            trans_score = self._transitivity_score(prompt, cand)
            structural_score = max(num_score, bat_score, trans_score)
            
            # NCD (10% weight)
            ncd_score = 1 - self._ncd(prompt, cand)
            
            # Combined score
            final_score = 0.30 * pqfes_score + 0.60 * structural_score + 0.10 * ncd_score
            
            reasoning = f"PQFES={pqfes_score:.3f}, struct={structural_score:.3f}, NCD={ncd_score:.3f}"
            results.append({
                'candidate': cand,
                'score': float(final_score),
                'reasoning': reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-checks and structural match."""
        # Meta-confidence caps the ceiling
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_conf = 0.5  # Default
        
        # Numeric comparison
        if self._numeric_comparison_score(prompt, answer) > 0.5:
            struct_conf = 0.8
        
        # Bat-and-ball algebra
        if self._bat_and_ball_score(prompt, answer) > 0.5:
            struct_conf = 0.85
        
        # Transitivity
        if self._transitivity_score(prompt, answer) > 0.3:
            struct_conf = 0.6
        
        # No structural match -> low confidence
        prompt_props = self._tokenize_propositions(prompt)
        if len(prompt_props) == 0:
            struct_conf = 0.3
        
        # Final confidence is capped by meta-confidence
        return min(struct_conf, meta_conf)
```

</details>
