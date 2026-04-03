# Renormalization + Pragmatics + Type Theory

**Fields**: Physics, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T04:57:41.111238
**Report Generated**: 2026-04-02T10:55:59.188193

---

## Nous Analysis

**Algorithm**  
We build a hierarchical type‑driven reasoner that treats a sentence as a typed abstract syntax tree (AST). Each token is first assigned a primitive type from a small signature: `Entity`, `Quantity`, `Relation`, `Predicate`, `Connective`. Using a simple type‑checking routine (unidirectional unification) we reject parses that violate typing rules (e.g., applying a comparative to non‑quantities). The AST nodes store a NumPy feature vector `f` (counts of lexical cues: negation, modal, numeric, etc.) and a type tag.

**Pragmatic enrichment**  
For each node we compute a relevance score `r = σ(w·f)` where `w` is a fixed heuristic vector derived from Grice’s maxims (e.g., high weight for informativeness, low weight for redundancy). This yields a context‑sensitive pragmatic value that propagates upward: parent `r_parent = max(r_child, α·∑r_child)` with α ∈ [0,1] controlling cooperativity.

**Renormalization (coarse‑graining)**  
We define a renormalization sweep: replace every contiguous subsequence of length k (2 ≤ k ≤ 4) that forms a well‑typed sub‑tree by a single “super‑node” whose type is the least upper bound of its children and whose feature vector is the average of the children’s `f`. The pragmatic score of the super‑node is recomputed as above. Sweeps are repeated until the vector of root scores `R = [r_root^{(scale)}]` changes less than ε (1e‑3) across iterations – a fixed point. The final answer score is a weighted sum:  
`score = β·type_consistency + γ·mean(R) + δ·(1‑std(R))`  
where `type_consistency` is 1 if the root type matches the expected answer type else 0, and β,γ,δ sum to 1.

**Parsed structural features**  
Negations (`not`, `no`), comparatives (`more than`, `less than`), conditionals (`if … then`), causal markers (`because`, `leads to`), numeric quantities, ordering relations (`first`, `last`), quantifiers (`all`, `some`), and speech‑act markers (`please`, `I promise`).

**Novelty**  
Type‑theoretic semantic parsing and pragmatic enrichment have been studied separately; applying renormalization‑style coarse‑graining to logical forms is uncommon in pure‑symbolic NLP. The triple combination is not present in existing surveys, making it novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure, context, and multi‑scale stability.  
Metacognition: 6/10 — limited self‑monitoring; relies on fixed heuristics rather than learned reflection.  
Hypothesis generation: 5/10 — generates candidate parses but does not propose new hypotheses beyond given answers.  
Implementability: 9/10 — uses only regex‑based parsing, NumPy arrays, and simple loops; no external libraries needed.

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
**Reason**: trap_battery_failed (acc=37% cal=41% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:42:24.849533

---

## Code

**Source**: scrap

[View code](./Renormalization---Pragmatics---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Renormalization x Pragmatics x Type Theory Reasoning Tool

Combines type-theoretic semantic parsing, Gricean pragmatic enrichment,
and renormalization-style coarse-graining for multi-scale reasoning.
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple


class ReasoningTool:
    def __init__(self):
        # Type system
        self.types = ['Entity', 'Quantity', 'Relation', 'Predicate', 'Connective']
        
        # Pragmatic weights (Gricean maxims: informativeness, clarity, relevance)
        self.w = np.array([2.0, 1.5, -1.0, 1.8, 1.2, 1.0, 0.8])  # 7 features
        
        # Renormalization params
        self.alpha = 0.6  # cooperativity
        self.epsilon = 1e-3
        self.max_sweeps = 5
        
        # Score weights
        self.beta = 0.50  # type consistency
        self.gamma = 0.35  # mean relevance
        self.delta = 0.15  # stability (1-std)

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b|[.,!?;]', text.lower())

    def _extract_features(self, tokens: List[str]) -> np.ndarray:
        """Extract 7 pragmatic features from tokens."""
        negations = sum(1 for t in tokens if t in ['not', 'no', "n't", 'never', 'none'])
        comparatives = sum(1 for t in tokens if t in ['more', 'less', 'greater', 'fewer', 'than'])
        conditionals = sum(1 for t in tokens if t in ['if', 'then', 'unless', 'when'])
        causals = sum(1 for t in tokens if t in ['because', 'since', 'therefore', 'thus', 'leads'])
        numerics = sum(1 for t in tokens if re.match(r'\d+\.?\d*', t))
        quantifiers = sum(1 for t in tokens if t in ['all', 'some', 'every', 'any', 'each'])
        redundancy = max(0, len(tokens) - len(set(tokens)))  # duplicate words
        
        return np.array([negations, comparatives, conditionals, causals, 
                        numerics, quantifiers, redundancy], dtype=float)

    def _assign_type(self, tokens: List[str]) -> str:
        """Heuristic type assignment based on token patterns."""
        text = ' '.join(tokens)
        
        # Quantity: numbers, measurements
        if re.search(r'\d+\.?\d*', text) or any(w in tokens for w in ['sum', 'total', 'count']):
            return 'Quantity'
        
        # Connective: logical operators
        if any(w in tokens for w in ['and', 'or', 'if', 'then', 'not', 'but']):
            return 'Connective'
        
        # Relation: comparatives, possessives
        if any(w in tokens for w in ['more', 'less', 'than', 'has', 'is', 'are']):
            return 'Relation'
        
        # Predicate: verbs, questions
        if any(w in tokens for w in ['does', 'did', 'can', 'will', 'should', 'would']):
            return 'Predicate'
        
        return 'Entity'

    def _compute_relevance(self, features: np.ndarray) -> float:
        """Compute pragmatic relevance score using Gricean weights."""
        raw = np.dot(self.w, features)
        return 1.0 / (1.0 + np.exp(-raw))  # sigmoid

    def _renormalize(self, features_list: List[np.ndarray], scores_list: List[float]) -> List[float]:
        """Apply renormalization sweeps until convergence."""
        R_history = []
        
        for sweep in range(self.max_sweeps):
            if len(features_list) <= 1:
                break
            
            # Coarse-grain: merge adjacent pairs
            new_features = []
            new_scores = []
            
            i = 0
            while i < len(features_list):
                if i + 1 < len(features_list):
                    # Merge two nodes
                    merged_f = (features_list[i] + features_list[i+1]) / 2.0
                    merged_r = max(scores_list[i], self.alpha * (scores_list[i] + scores_list[i+1]))
                    new_features.append(merged_f)
                    new_scores.append(merged_r)
                    i += 2
                else:
                    new_features.append(features_list[i])
                    new_scores.append(scores_list[i])
                    i += 1
            
            features_list = new_features
            scores_list = new_scores
            R_history.append(scores_list[0] if scores_list else 0.0)
            
            # Check convergence
            if len(R_history) >= 2 and abs(R_history[-1] - R_history[-2]) < self.epsilon:
                break
        
        return R_history if R_history else [0.5]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0

    def _numeric_check(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Check numeric comparisons in prompt."""
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        
        if len(nums_p) >= 2 and any(w in prompt.lower() for w in ['greater', 'less', 'more', 'larger', 'smaller']):
            try:
                a, b = float(nums_p[0]), float(nums_p[1])
                if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'more' in prompt.lower():
                    expected = str(max(a, b))
                else:
                    expected = str(min(a, b))
                
                if any(expected in candidate for expected in [str(max(a,b)), str(min(a,b))]):
                    return True, 0.9
            except:
                pass
        
        return False, 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """Epistemic honesty: detect unanswerable/ambiguous questions."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* fail|why did .* stop)\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or \b', p) and not re.search(r'\b(only|just these)\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|greatest)\b', p) and not re.search(r'\b(most|highest|lowest)\b', p):
            return 0.3
        
        # Unanswerable patterns
        if re.search(r'\b(cannot determine|insufficient|not enough information)\b', p):
            return 0.2
        
        return 1.0  # No meta-issues detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using type theory + pragmatics + renormalization."""
        prompt_tokens = self._tokenize(prompt)
        prompt_type = self._assign_type(prompt_tokens)
        
        results = []
        
        for candidate in candidates:
            cand_tokens = self._tokenize(candidate)
            
            # Build feature vectors for each token
            features_list = [self._extract_features([t]) for t in cand_tokens]
            if not features_list:
                features_list = [np.zeros(7)]
            
            # Compute initial relevance scores
            scores_list = [self._compute_relevance(f) for f in features_list]
            
            # Renormalization sweeps
            R_history = self._renormalize(features_list.copy(), scores_list.copy())
            
            # Type consistency
            cand_type = self._assign_type(cand_tokens)
            type_consistency = 1.0 if cand_type == prompt_type else 0.0
            
            # Multi-scale score
            mean_R = np.mean(R_history)
            std_R = np.std(R_history) if len(R_history) > 1 else 0.0
            
            base_score = self.beta * type_consistency + self.gamma * mean_R + self.delta * (1.0 - std_R)
            
            # Numeric check bonus
            num_match, num_bonus = self._numeric_check(prompt, candidate)
            if num_match:
                base_score = 0.85 * base_score + 0.15 * num_bonus
            
            # NCD tiebreaker (max 10%)
            ncd_val = 1.0 - self._ncd(prompt, candidate)
            final_score = 0.90 * base_score + 0.10 * ncd_val
            
            reasoning = f"Type:{cand_type}={'==' if type_consistency else '!='}{prompt_type}, R_scales:{len(R_history)}, mean_R:{mean_R:.2f}"
            
            results.append({"candidate": candidate, "score": float(final_score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty."""
        # Meta-confidence check first
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate the answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        base_conf = results[0]['score']
        
        # Cap confidence based on question properties
        if '?' not in prompt:
            base_conf *= 0.8  # Lower confidence for non-questions
        
        # Never exceed 0.9 unless numeric match
        num_match, _ = self._numeric_check(prompt, answer)
        max_conf = 0.9 if num_match else 0.85
        
        return min(base_conf * meta_conf, max_conf)
```

</details>
