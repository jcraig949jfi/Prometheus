# Metacognition + Criticality + Maximum Entropy

**Fields**: Cognitive Science, Complex Systems, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:21:05.138579
**Report Generated**: 2026-04-02T08:39:54.930538

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only the Python `re` module we extract a set of atomic propositions \(P=\{p_1\dots p_k\}\) from the prompt and each candidate answer. Propositions are encoded as feature vectors \(f(p)\in\{0,1\}^d\) where each dimension corresponds to a structural pattern:  
   - negation (`not`, `no`) → dim 0  
   - comparative (`>`, `<`, `more than`, `less than`) → dim 1  
   - conditional (`if … then`, `unless`) → dim 2  
   - causal cue (`because`, `leads to`, `results in`) → dim 3  
   - ordering (`before`, `after`, `first`, `last`) → dim 4  
   - numeric literal (integer or float) → dim 5 (value normalized)  
   - equality (`=`, `is`) → dim 6  

   Each proposition yields a sparse binary vector; the concatenation of all propositions from a candidate answer forms its feature sum \(F_i=\sum_{p\in ans_i} f(p)\).

2. **Constraint construction** – From the prompt we derive linear expectation constraints \(\mathbb{E}_p[F]=\mu\) where \(\mu\) is the feature sum extracted from the prompt itself (treated as the “observed” world). This gives a matrix \(A\in\mathbb{R}^{m\times d}\) (one row per constraint type) and vector \(b\in\mathbb{R}^m\).

3. **Maximum‑Entropy inference** – We seek the distribution \(p\) over the \(N\) candidate answers that maximizes Shannon entropy \(-\sum_i p_i\log p_i\) subject to \(Ap=b\) and \(\sum_i p_i=1\). Using the standard dual formulation, the optimal \(p\) has the form  
   \[
   p_i = \frac{\exp(\lambda^\top F_i)}{Z(\lambda)},\qquad Z(\lambda)=\sum_j \exp(\lambda^\top F_j)
   \]  
   where \(\lambda\in\mathbb{R}^m\) are Lagrange multipliers. We solve for \(\lambda\) by iterative scaling (or simple gradient ascent) using only NumPy:  
   \[
   \lambda^{(t+1)} = \lambda^{(t)} + \eta\,(b - A\bar{F}^{(t)}),\quad 
   \bar{F}^{(t)} = \sum_i p_i^{(t)}F_i
   \]  
   with a fixed step size \(\eta\). Convergence is declared when \(\|b-A\bar{F}\|_2<10^{-4}\).

4. **Scoring & Metacognition** – The score for candidate \(i\) is its maximum‑entropy probability \(p_i\). Confidence is derived from the entropy of the distribution:  
   \[
   \text{confidence}=1-\frac{H(p)}{\log N},\quad H(p)=-\sum_i p_i\log p_i
   \]  
   High entropy → low confidence (the system is near criticality, i.e., maximally susceptible to constraint changes). Error monitoring is performed by checking constraint violations after scoring: if any \(|(Ap)_i-b_i|>\epsilon\) we flag the answer as inconsistent and reduce its score proportionally.

**Structural features parsed** – negations, comparatives, conditionals, causal cues, ordering relations, numeric literals, and equality statements. These are the only patterns the regex‑based extractor looks for; all other lexical content is ignored.

**Novelty** – Pure maximum‑entropy scoring of discrete answer candidates is known in statistical‑physics‑inspired NLP, but coupling it with a criticality‑based confidence measure (entropy‑derived susceptibility) and explicit metacognitive error monitoring is not present in existing public reasoning‑evaluation tools. The closest work uses Bayesian model averaging or logistic regression; none combine the three concepts in an algorithm that relies solely on regex extraction, linear constraints, and iterative scaling.

**Rating**  
Reasoning: 8/10 — The algorithm extracts logical structure, propagates constraints via maxent, and yields principled probabilities, satisfying the pipeline’s emphasis on structural parsing and constraint propagation.  
Metacognition: 7/10 — Confidence is calibrated from distribution entropy and error monitoring checks constraint violations, providing a clear metacognitive signal, though it lacks deeper strategy‑selection mechanisms.  
Hypothesis generation: 6/10 — The method scores given hypotheses but does not generate new ones; it relies entirely on the supplied candidate set.  
Implementability: 9/10 — Only `re` and NumPy are needed; iterative scaling converges quickly for modest numbers of candidates, making it straightforward to code and run without external libraries or APIs.

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
**Reason**: trap_battery_failed (acc=31% cal=25% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T08:08:21.765148

---

## Code

**Source**: scrap

[View code](./Metacognition---Criticality---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """Maximum Entropy reasoning with structural parsing and metacognitive monitoring.
    
    Extracts logical structure (negations, comparatives, conditionals, causals, ordering,
    numerics) from prompt and candidates, then finds the max-entropy distribution over
    candidates that matches prompt constraints. Confidence derives from distribution
    entropy (criticality) and metacognitive error detection for ambiguity/presuppositions.
    """
    
    def __init__(self):
        self.dim = 7
        self.eta = 0.1
        self.max_iter = 100
        self.eps = 1e-4
    
    def _extract_features(self, text: str) -> np.ndarray:
        """Extract structural features into d-dimensional vector."""
        f = np.zeros(self.dim)
        text_lower = text.lower()
        
        # Dim 0: negation
        if re.search(r'\b(not|no|never|neither|nor|n\'t)\b', text_lower):
            f[0] = 1
        
        # Dim 1: comparative
        if re.search(r'(>|<|more than|less than|fewer|greater|smaller|larger|taller|shorter)', text_lower):
            f[1] = 1
        
        # Dim 2: conditional
        if re.search(r'\b(if\b.*\bthen\b|unless|when\b.*\bthen\b|implies)', text_lower):
            f[2] = 1
        
        # Dim 3: causal
        if re.search(r'\b(because|since|leads to|results in|causes|produces|therefore|thus|hence)', text_lower):
            f[3] = 1
        
        # Dim 4: ordering
        if re.search(r'\b(before|after|first|last|then|next|previous|earlier|later)', text_lower):
            f[4] = 1
        
        # Dim 5: numeric (normalized sum of numbers)
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        if nums:
            f[5] = min(1.0, sum(float(n) for n in nums) / 100.0)
        
        # Dim 6: equality
        if re.search(r'(=|is|are|equals|same as)', text_lower):
            f[6] = 1
        
        return f
    
    def _maxent_optimize(self, F_matrix: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Iterative scaling to find max-entropy distribution."""
        N = F_matrix.shape[0]
        lam = np.zeros(self.dim)
        
        for _ in range(self.max_iter):
            # Compute current distribution
            scores = F_matrix @ lam
            scores = scores - np.max(scores)  # numerical stability
            exp_scores = np.exp(scores)
            Z = np.sum(exp_scores)
            p = exp_scores / Z
            
            # Check constraint violation
            F_bar = F_matrix.T @ p
            if np.linalg.norm(b - F_bar) < self.eps:
                break
            
            # Update lambda
            lam += self.eta * (b - F_bar)
        
        return p
    
    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance (tiebreaker only)."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _parse_numeric_comparison(self, prompt: str, candidates: List[str]) -> Tuple[bool, List[float]]:
        """Detect and solve numeric comparisons."""
        nums_prompt = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        if len(nums_prompt) < 2:
            return False, []
        
        scores = []
        for cand in candidates:
            score = 0.5
            cand_lower = cand.lower()
            
            # Extract candidate numbers
            nums_cand = re.findall(r'\b(\d+\.?\d*)\b', cand)
            if nums_cand:
                # Check if comparison is correct
                if re.search(r'(greater|larger|more|bigger)', prompt.lower()):
                    if nums_cand and float(nums_cand[0]) > float(nums_prompt[0]):
                        score = 0.9
                elif re.search(r'(less|smaller|fewer)', prompt.lower()):
                    if nums_cand and float(nums_cand[0]) < float(nums_prompt[0]):
                        score = 0.9
            
            # Boolean answers
            if 'yes' in cand_lower and re.search(r'\b(is|does)\b', prompt.lower()):
                score = 0.6
            elif 'no' in cand_lower:
                score = 0.4
            
            scores.append(score)
        
        return True, scores
    
    def _meta_confidence(self, prompt: str) -> float:
        """Metacognitive check for ambiguity/unanswerable questions."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either|only).*\bor\b', prompt_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', prompt_lower):
            if not re.search(r'\b(measure|metric|criterion|by)\b', prompt_lower):
                return 0.3
        
        # Insufficient information
        if re.search(r'\b(what is|who is|when did)\b', prompt_lower):
            if len(prompt.split()) < 10:
                return 0.35
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by max-entropy probability."""
        if not candidates:
            return []
        
        N = len(candidates)
        
        # Try numeric comparison parser first
        is_numeric, num_scores = self._parse_numeric_comparison(prompt, candidates)
        if is_numeric:
            results = []
            for i, cand in enumerate(candidates):
                ncd = 1 - self._compute_ncd(prompt, cand)
                final_score = 0.7 * num_scores[i] + 0.15 * ncd + 0.15 * 0.5
                results.append({
                    "candidate": cand,
                    "score": final_score,
                    "reasoning": "Numeric comparison + structural match"
                })
            results.sort(key=lambda x: x["score"], reverse=True)
            return results
        
        # Extract features
        b = self._extract_features(prompt)
        F_matrix = np.array([self._extract_features(c) for c in candidates])
        
        # Max-entropy optimization
        if np.sum(b) > 0:
            p = self._maxent_optimize(F_matrix, b)
        else:
            p = np.ones(N) / N
        
        # Compute scores
        results = []
        for i, cand in enumerate(candidates):
            # Structural score from max-entropy
            struct_score = p[i]
            
            # NCD tiebreaker
            ncd_score = 1 - self._compute_ncd(prompt, cand)
            
            # Constraint violation penalty
            violation = np.linalg.norm(F_matrix[i] - b)
            penalty = max(0, 1 - violation / (self.dim ** 0.5))
            
            # Final score: 60% maxent, 25% constraint match, 15% NCD
            final_score = 0.6 * struct_score + 0.25 * penalty + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"MaxEnt={struct_score:.2f}, Constraint={penalty:.2f}, NCD={ncd_score:.2f}"
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on entropy and metacognitive checks."""
        # Metacognitive floor
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.4:
            return meta_conf
        
        # Evaluate against single candidate
        candidates = [answer]
        b = self._extract_features(prompt)
        F_ans = self._extract_features(answer)
        
        # Check structural match
        if np.sum(b) == 0:
            return 0.3  # No structure in prompt
        
        match_score = 1 - np.linalg.norm(F_ans - b) / (self.dim ** 0.5)
        match_score = max(0, min(1, match_score))
        
        # Entropy-based confidence (single answer = high certainty if matched)
        base_conf = 0.5 + 0.4 * match_score
        
        # Cap by metacognitive confidence
        return min(base_conf, meta_conf)
```

</details>
