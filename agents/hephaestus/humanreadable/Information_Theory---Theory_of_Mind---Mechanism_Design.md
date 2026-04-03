# Information Theory + Theory of Mind + Mechanism Design

**Fields**: Mathematics, Cognitive Science, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T21:39:25.885521
**Report Generated**: 2026-04-02T10:00:36.552424

---

## Nous Analysis

**Algorithm: Belief‑Entropy VCG Scorer (BEVS)**  

1. **Parsing & Data structures**  
   - Use a handful of regex patterns to extract atomic propositions from the prompt and each candidate answer:  
     *Negation*: `not\s+(\w+)` → `(¬, p)`  
     *Comparative*: `(\w+)\s+(>|<|≥|≤)\s+(\w+)` → `(comp, left, op, right)`  
     *Conditional*: `if\s+(.+?)\s+then\s+(.+)` → `(→, antecedent, consequent)`  
     *Causal*: `(.+?)\s+causes\s+(.+)` → `(cause, effect)`  
     *Numeric/value*: `\d+(\.\d+)?` → `(val, number)`  
   - Each atom becomes a row in a NumPy boolean matrix **A** (shape = [n_agents × n_propositions]) where `A[i,j]=1` means agent *i* asserts proposition *j* is true.  
   - A parallel float matrix **P** holds the agent’s subjective probability for each proposition (initialized from linguistic cues: e.g., “likely” → 0.7, “unlikely” → 0.3).  

2. **Constraint propagation**  
   - Build a deterministic inference matrix **C** (n_propositions × n_propositions) encoding modus ponens, transitivity of comparatives, and contrapositives derived from conditionals.  
   - Iterate `A = np.clip(A @ C, 0, 1)` until convergence (≤ 5 iterations) to propagate asserted truths through logical constraints.  
   - Update **P** using Bayes’ rule on the propagated **A**: `P = (P * A) / (P * A + (1-P)*(1-A))` (element‑wise, with epsilon to avoid zero).  

3. **Information‑theoretic scoring**  
   - Compute the joint belief distribution **B** = outer product of each agent’s probability vector (size = 2^n_propositions approximated via mean‑field: `B_j = np.mean(P[:,j])`).  
   - Shannon entropy `H = -np.sum(B * np.log2(B + eps))`.  
   - Mutual information between the candidate answer’s proposition set **S** and the inferred true state: `I = H - H_cond`, where `H_cond` is entropy after conditioning on **S** (zero‑out probabilities contradicted by **S**).  

4. **Mechanism‑design (VCG) payment**  
   - Define welfare `W = -H` (lower entropy = higher welfare).  
   - For each candidate *i*, compute welfare with all answers `W_all` and welfare without *i* `W_-i` (by removing its row from **A** and recomputing **B**).  
   - VCG score: `score_i = W_-i - W_all`. Higher score means the answer contributes most to reducing uncertainty, i.e., is most informative and truth‑promoting under self‑interested reporting.  

**Structural features parsed**: negations, comparatives (> < ≥ ≤), conditionals (if‑then), causal verbs (causes, leads to), numeric values, ordering relations (more/less than), and explicit truth‑modal adjectives (likely, certainly).  

**Novelty**: While each component (logic propagation, entropy‑based uncertainty, VCG payments) exists separately, their tight coupling in a single, numpy‑only scorer that extracts logical form from raw text and rewards answers by their marginal information gain is not present in existing public reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 8/10 — captures logical inference and uncertainty quantification effectively, though scalability to deep nesting is limited.  
Metacognition: 7/10 — models others’ beliefs via probability matrices, but does not simulate higher‑order recursion beyond first‑order belief.  
Hypothesis generation: 6/10 — generates implied propositions through constraint propagation, yet lacks creative abductive leaps beyond deterministic rules.  
Implementability: 9/10 — relies only on regex, NumPy arrays, and basic linear algebra; no external libraries or APIs needed.

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
**Reason**: validation:confidence_out_of_range: -2.3348207628706317

**Forge Timestamp**: 2026-04-02T09:43:15.049541

---

## Code

**Source**: scrap

[View code](./Information_Theory---Theory_of_Mind---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Belief-Entropy VCG Scorer (BEVS)
    
    Combines Information Theory, Theory of Mind, and Mechanism Design:
    1. Parses logical structures into belief matrices
    2. Propagates constraints via logical inference
    3. Scores candidates by their marginal information gain (entropy reduction)
    4. Uses VCG mechanism to reward truth-revealing answers
    """
    
    def __init__(self):
        self.eps = 1e-9
        self.linguistic_probs = {'likely': 0.7, 'unlikely': 0.3, 'certain': 0.95, 
                                'possible': 0.5, 'probably': 0.7, 'maybe': 0.4}
    
    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Extract atomic propositions from text"""
        props = []
        text_lower = text.lower()
        
        # Negation
        for m in re.finditer(r'not\s+(\w+)', text_lower):
            props.append(('neg', m.group(1)))
        
        # Numeric comparisons
        for m in re.finditer(r'(\d+\.?\d*)\s*([<>]=?)\s*(\d+\.?\d*)', text):
            props.append(('comp', float(m.group(1)), m.group(2), float(m.group(3))))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text_lower):
            props.append(('cond', m.group(1).strip(), m.group(2).strip()))
        
        # Causal
        for m in re.finditer(r'(.+?)\s+(causes?|leads?\s+to)\s+(.+?)(?:\.|$)', text_lower):
            props.append(('cause', m.group(1).strip(), m.group(3).strip()))
        
        # Extract all words as base propositions
        words = re.findall(r'\b\w+\b', text_lower)
        for w in words[:20]:  # Limit to avoid explosion
            props.append(('word', w))
        
        return props
    
    def _compute_numeric(self, prompt: str, candidates: List[str]) -> Tuple[int, float]:
        """Compute numeric comparisons and arithmetic"""
        # Bat-and-ball style problems
        m = re.search(r'(\w+)\s+and\s+(\w+)\s+cost\s+\$?(\d+\.?\d*).+\1.+more.+\$?(\d+\.?\d*)', prompt, re.I)
        if m:
            total, diff = float(m.group(3)), float(m.group(4))
            lesser = (total - diff) / 2
            greater = lesser + diff
            for i, c in enumerate(candidates):
                nums = re.findall(r'\d+\.?\d*', c)
                if nums and abs(float(nums[0]) - lesser) < 0.01:
                    return i, 0.9
        
        # Simple comparisons
        m = re.search(r'(\d+\.?\d*)\s+([<>])\s+(\d+\.?\d*)', prompt)
        if m:
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            result = (a < b) if op == '<' else (a > b)
            for i, c in enumerate(candidates):
                if ('yes' in c.lower() and result) or ('no' in c.lower() and not result):
                    return i, 0.85
        
        return -1, 0.0
    
    def _constraint_propagation(self, A: np.ndarray, props: List[Tuple]) -> np.ndarray:
        """Propagate logical constraints through belief matrix"""
        n = len(props)
        C = np.eye(n)
        
        # Build constraint matrix from conditionals and transitivity
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if i == j:
                    continue
                # Modus ponens: if p1 is conditional with consequent matching p2
                if p1[0] == 'cond' and p2[0] == 'word':
                    if p2[1] in p1[2]:
                        C[i, j] = 1.0
                # Transitivity for comparisons
                if p1[0] == 'comp' and p2[0] == 'comp':
                    if abs(p1[3] - p2[1]) < self.eps:  # Chain comparisons
                        C[i, j] = 0.5
        
        # Iteratively propagate
        A_new = A.copy()
        for _ in range(3):
            A_new = np.clip(A_new @ C, 0, 1)
        
        return A_new
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, and epistemic issues"""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why (did|does|is).+(fail|stop|wrong)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ \w+ a \w+', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+who', prompt_lower):
            if re.search(r'told|said|asked', prompt_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+[?]', prompt_lower):
            if 'only' not in prompt_lower:
                return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', prompt_lower):
            if not re.search(r'(most|least|faster|slower|cheaper|expensive)', prompt_lower):
                return 0.35
        
        # Insufficient information
        if re.search(r'what is the.+of \w+[?]', prompt_lower):
            if len(prompt.split()) < 15:  # Too short to contain needed info
                return 0.3
        
        return 1.0  # No epistemic issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using BEVS algorithm"""
        n_candidates = len(candidates)
        
        # Try computational methods first
        num_idx, num_conf = self._compute_numeric(prompt, candidates)
        if num_idx >= 0:
            results = []
            for i, c in enumerate(candidates):
                score = num_conf if i == num_idx else (1 - num_conf) / max(1, n_candidates - 1)
                results.append({
                    'candidate': c,
                    'score': score,
                    'reasoning': f'Numeric computation: {"match" if i == num_idx else "non-match"}'
                })
            return sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Parse prompt and candidates
        prompt_props = self._parse_propositions(prompt)
        cand_props = [self._parse_propositions(c) for c in candidates]
        
        # Build unified proposition vocabulary
        all_props = prompt_props.copy()
        for cp in cand_props:
            for p in cp:
                if p not in all_props:
                    all_props.append(p)
        
        n_props = len(all_props)
        if n_props == 0:
            # Fallback to NCD
            return self._ncd_fallback(prompt, candidates)
        
        # Build belief matrix A: [n_agents x n_props]
        n_agents = 1 + n_candidates  # prompt + candidates
        A = np.zeros((n_agents, n_props))
        P = np.ones((n_agents, n_props)) * 0.5
        
        # Encode prompt
        for i, prop in enumerate(all_props):
            if prop in prompt_props:
                A[0, i] = 1.0
                P[0, i] = 0.8
        
        # Encode candidates
        for agent_idx, (cand, cp) in enumerate(zip(candidates, cand_props), start=1):
            for i, prop in enumerate(all_props):
                if prop in cp:
                    A[agent_idx, i] = 1.0
                    # Check for linguistic probability markers
                    for word, prob in self.linguistic_probs.items():
                        if word in cand.lower():
                            P[agent_idx, i] = prob
                            break
                    else:
                        P[agent_idx, i] = 0.75
        
        # Constraint propagation
        A_prop = self._constraint_propagation(A, all_props)
        
        # Update probabilities using propagated beliefs
        P_updated = np.clip((P * A_prop + 0.3 * (1 - A_prop)) / (P * A_prop + (1 - P) * (1 - A_prop) + self.eps), 0, 1)
        
        # Compute base entropy
        B = np.mean(P_updated, axis=0)
        B = np.clip(B, self.eps, 1 - self.eps)
        H_base = -np.sum(B * np.log2(B) + (1 - B) * np.log2(1 - B))
        
        # VCG scoring
        scores = []
        for agent_idx in range(1, n_agents):
            # Entropy without this candidate
            B_without = np.mean(np.delete(P_updated, agent_idx, axis=0), axis=0)
            B_without = np.clip(B_without, self.eps, 1 - self.eps)
            H_without = -np.sum(B_without * np.log2(B_without) + (1 - B_without) * np.log2(1 - B_without))
            
            # VCG score: marginal contribution to uncertainty reduction
            vcg_score = H_without - H_base
            scores.append(vcg_score)
        
        # Normalize and add small NCD component
        scores = np.array(scores)
        if scores.max() > scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min() + self.eps)
        
        # Add minor NCD tiebreaker (max 10%)
        ncd_scores = self._compute_ncd(prompt, candidates)
        final_scores = 0.9 * scores + 0.1 * ncd_scores
        
        results = []
        for i, c in enumerate(candidates):
            results.append({
                'candidate': c,
                'score': float(final_scores[i]),
                'reasoning': f'VCG info-gain: {scores[i]:.3f}, NCD: {ncd_scores[i]:.3f}'
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer given prompt"""
        # Meta-confidence check
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate against single candidate
        results = self.evaluate(prompt, [answer])
        base_conf = results[0]['score']
        
        # Cap confidence based on structural match
        if 'Numeric computation: match' in results[0]['reasoning']:
            return min(0.9, base_conf * meta_conf)
        
        # Cap at 0.7 for non-computational matches
        return min(0.7, base_conf * meta_conf)
    
    def _compute_ncd(self, prompt: str, candidates: List[str]) -> np.ndarray:
        """Normalized Compression Distance using zlib"""
        import zlib
        
        scores = []
        c_prompt = len(zlib.compress(prompt.encode()))
        
        for cand in candidates:
            c_cand = len(zlib.compress(cand.encode()))
            c_combined = len(zlib.compress((prompt + cand).encode()))
            ncd = (c_combined - min(c_prompt, c_cand)) / max(c_prompt, c_cand)
            scores.append(1 - ncd)  # Invert so higher = more similar
        
        scores = np.array(scores)
        if scores.max() > scores.min():
            scores = (scores - scores.min()) / (scores.max() - scores.min() + self.eps)
        
        return scores
    
    def _ncd_fallback(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Fallback to NCD when no structure parsed"""
        ncd_scores = self._compute_ncd(prompt, candidates)
        results = []
        for i, c in enumerate(candidates):
            results.append({
                'candidate': c,
                'score': float(ncd_scores[i] * 0.5),  # Cap at 0.5 for low confidence
                'reasoning': 'NCD fallback (low structural match)'
            })
        return sorted(results, key=lambda x: x['score'], reverse=True)
```

</details>
