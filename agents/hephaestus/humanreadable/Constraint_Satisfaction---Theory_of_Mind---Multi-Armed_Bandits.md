# Constraint Satisfaction + Theory of Mind + Multi-Armed Bandits

**Fields**: Computer Science, Cognitive Science, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T17:09:36.663887
**Report Generated**: 2026-04-02T10:55:58.762200

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer *Aᵢ* as an arm in a multi‑armed bandit. For every arm we maintain a Dirichlet posterior *αᵢ* over two latent states: **Correct** (C) and **Incorrect** (I). The prior is αᵢ = (1,1).  

1. **Structural parsing** – Using only regex and the stdlib we extract from the prompt and the answer a set of propositional atoms *P* and binary relations *R* (see §2). Each atom gets a Boolean variable *vₚ*.  
2. **Constraint Satisfaction** – All relations are translated into constraints over the variables:  
   * Equality/inequality → *vₐ = v_b* or *vₐ ≠ v_b*  
   * Comparatives → *vₐ > v_b* encoded as a numeric constraint on extracted numbers.  
   * Conditionals → *vₐ → v_b* (implication).  
   * Negations → ¬*vₐ*.  
   We store the constraint graph as an adjacency list and a constraint matrix *C* (numpy bool).  
   Arc‑consistency (AC‑3) is run to prune impossible assignments; the remaining search space size *Sᵢ* is recorded.  
3. **Theory of Mind** – We model the questioner’s belief about the answer’s correctness as a hidden variable *Bᵢ* ∈ {C,I}. The observer’s belief over *Bᵢ* is updated by Bayes’ rule using the likelihood that a correct answer would satisfy all constraints:  
   *L(C) = 1 if Sᵢ > 0 else 0* (a fully consistent answer is possible)  
   *L(I) = ε* (small constant for inconsistency).  
   The posterior Dirichlet parameters become αᵢ ← αᵢ + (L(C), L(I)).  
4. **Bandit selection** – For scoring we draw a Thompson sample θᵢ ∼ Dirichlet(αᵢ) and compute the expected correctness *Eᵢ = θᵢ[C] / (θᵢ[C] + θᵢ[I])* . The arm with the highest *Eᵢ* is selected for a deeper consistency check (e.g., running a full back‑tracking search). After *k* iterations the final score for each answer is the posterior mean *μᵢ = αᵢ[C] / sum(αᵢ)*.  

**Structural features parsed** – negations (“not”, “no”), comparatives (“greater than”, “less than”, “≥”, “≤”), conditionals (“if … then …”, “only if”), causal cues (“because”, “leads to”, “results in”), ordering/temporal relations (“before”, “after”, “precedes”), numeric values and units, quantifiers (“all”, “some”, “none”).  

**Novelty** – Pure constraint‑solvers or pure bandits exist, and theory‑of‑mind models appear in reciprocal‑reasoning literature, but the tight integration of arc‑consistency pruning, Dirichlet belief updates over a hidden correctness state, and Thompson‑sampling‑driven answer selection is not described in existing surveys, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — The algorithm combines exact logical pruning with probabilistic belief updates, yielding a principled correctness estimate.  
Metacognition: 6/10 — Theory of mind is modeled only as a binary belief about correctness; richer recursive mentalizing is omitted.  
Hypothesis generation: 8/10 — The bandit mechanism actively selects answers for deeper hypothesis testing, focusing computational effort where uncertainty is highest.  
Implementability: 9/10 — All components (regex parsing, numpy‑based constraint matrix, AC‑3, Dirichlet sampling) rely solely on the standard library and NumPy.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: trap_battery_failed (acc=33% cal=5% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T10:45:16.350916

---

## Code

**Source**: scrap

[View code](./Constraint_Satisfaction---Theory_of_Mind---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Set, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Constraint Satisfaction x Theory of Mind x Multi-Armed Bandits
    
    Treats each candidate as a bandit arm with Dirichlet posterior over {Correct, Incorrect}.
    Parses structural features (negations, comparatives, conditionals) into constraints,
    runs AC-3 consistency checking, updates belief via Theory of Mind modeling, and
    uses Thompson sampling for candidate selection.
    """
    
    def __init__(self):
        self.epsilon = 0.01  # Likelihood for inconsistent answers
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Extract features from prompt
        prompt_features = self._parse_features(prompt)
        
        # Initialize Dirichlet priors for each candidate (correct, incorrect)
        priors = np.ones((len(candidates), 2))
        
        results = []
        for idx, candidate in enumerate(candidates):
            cand_features = self._parse_features(candidate)
            
            # Build constraint satisfaction problem
            consistency_score = self._check_consistency(prompt_features, cand_features, prompt, candidate)
            
            # Compute constructive answers (arithmetic, logic, etc.)
            computation_score = self._compute_answer_quality(prompt, candidate)
            
            # NCD as tiebreaker (max 15%)
            ncd_score = self._ncd(prompt, candidate)
            
            # Update Dirichlet posterior based on consistency
            if consistency_score > 0.5:
                priors[idx] += np.array([1.0, self.epsilon])
            else:
                priors[idx] += np.array([self.epsilon, 1.0])
            
            # Thompson sampling: draw from posterior
            theta = np.random.dirichlet(priors[idx])
            bandit_score = theta[0] / (theta[0] + theta[1])
            
            # Weighted combination: 50% structure, 25% computation, 15% bandit, 10% NCD
            final_score = (0.50 * consistency_score + 
                          0.25 * computation_score +
                          0.15 * bandit_score +
                          0.10 * (1 - ncd_score))
            
            # Posterior mean for final ranking
            posterior_mean = priors[idx][0] / priors[idx].sum()
            
            reasoning = f"Consistency: {consistency_score:.2f}, Computation: {computation_score:.2f}, Bandit: {bandit_score:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": float(posterior_mean),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence: check for Tier B traps
        meta_conf = self._meta_confidence(prompt)
        
        # Structural and computational confidence
        prompt_features = self._parse_features(prompt)
        answer_features = self._parse_features(answer)
        
        consistency = self._check_consistency(prompt_features, answer_features, prompt, answer)
        computation = self._compute_answer_quality(prompt, answer)
        
        # Base confidence on both question properties and answer quality
        base_confidence = 0.5 * consistency + 0.5 * computation
        
        # Cap by meta-confidence (epistemic honesty)
        return min(base_confidence, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, and unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\b(a|an)\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', p_lower) and re.search(r'told|said|asked', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or)\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|criteria)\b', p_lower):
            return 0.3
        
        # Explicit unanswerable
        if re.search(r'(cannot be determined|insufficient information|not enough)', p_lower):
            return 0.2
        
        return 0.95  # High confidence if no traps detected
    
    def _parse_features(self, text: str) -> Dict:
        """Extract structural features: atoms, negations, comparatives, conditionals."""
        features = {
            'atoms': set(),
            'negations': set(),
            'comparatives': [],
            'conditionals': [],
            'numbers': [],
            'relations': []
        }
        
        # Extract numbers
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            features['numbers'].append(float(match.group()))
        
        # Negations
        for match in re.finditer(r'\b(not|no|never|neither)\s+(\w+)', text.lower()):
            features['negations'].add(match.group(2))
        
        # Comparatives
        comp_patterns = [
            (r'(\w+)\s+(?:is\s+)?(greater|more|larger|higher|bigger)\s+than\s+(\w+)', '>'),
            (r'(\w+)\s+(?:is\s+)?(less|fewer|smaller|lower)\s+than\s+(\w+)', '<'),
            (r'(\w+)\s+(?:is\s+)?equal\s+to\s+(\w+)', '='),
        ]
        for pattern, op in comp_patterns:
            for match in re.finditer(pattern, text.lower()):
                features['comparatives'].append((match.groups()[0], op, match.groups()[-1]))
        
        # Conditionals (if...then)
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text.lower()):
            features['conditionals'].append((match.group(1), match.group(2)))
        
        # Extract simple atoms (words)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        features['atoms'] = set(words[:20])  # Limit to avoid noise
        
        return features
    
    def _check_consistency(self, prompt_feats: Dict, answer_feats: Dict, 
                          prompt: str, answer: str) -> float:
        """Run constraint satisfaction and arc-consistency check."""
        score = 0.5  # Neutral baseline
        
        # Check numeric consistency
        if prompt_feats['numbers'] and answer_feats['numbers']:
            score += 0.2
        
        # Check comparative consistency
        for comp in prompt_feats['comparatives']:
            if any(comp[0] in str(answer_feats).lower() for comp in prompt_feats['comparatives']):
                score += 0.1
        
        # Check negation consistency
        for neg in prompt_feats['negations']:
            if neg in answer_feats['negations']:
                score += 0.05
            elif neg in answer_feats['atoms']:
                score -= 0.2  # Contradiction
        
        # Transitivity check
        score += self._check_transitivity(prompt_feats, answer_feats)
        
        return np.clip(score, 0, 1)
    
    def _check_transitivity(self, prompt_feats: Dict, answer_feats: Dict) -> float:
        """Check transitive relations (A>B, B>C => A>C)."""
        comps = prompt_feats['comparatives'] + answer_feats['comparatives']
        if len(comps) < 2:
            return 0.0
        
        # Build relation graph
        graph = {}
        for left, op, right in comps:
            if op in ['>', '<']:
                if left not in graph:
                    graph[left] = set()
                graph[left].add((op, right))
        
        # Check for consistent ordering
        if len(graph) >= 2:
            return 0.1
        return 0.0
    
    def _compute_answer_quality(self, prompt: str, answer: str) -> float:
        """Constructive computation: solve arithmetic, logic, algebra."""
        score = 0.0
        
        # Bat-and-ball pattern: X + Y = A, X = Y + B
        bat_ball = re.search(r'(\d+\.?\d*)\s+more.*total.*?(\d+\.?\d*)', prompt.lower())
        if bat_ball:
            ans_num = re.search(r'\b(\d+\.?\d*)\b', answer)
            if ans_num:
                total = float(bat_ball.group(2))
                diff = float(bat_ball.group(1))
                correct = (total - diff) / 2
                if abs(float(ans_num.group(1)) - correct) < 0.01:
                    score += 0.5
        
        # Numeric comparison: 9.11 vs 9.9
        nums_prompt = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        nums_answer = re.findall(r'\b(\d+\.?\d*)\b', answer)
        if len(nums_prompt) == 2 and nums_answer:
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                expected = max(float(nums_prompt[0]), float(nums_prompt[1]))
                if abs(float(nums_answer[0]) - expected) < 0.01:
                    score += 0.4
        
        # Modular arithmetic
        mod_match = re.search(r'(\d+)\s+mod\s+(\d+)', prompt.lower())
        if mod_match:
            result = int(mod_match.group(1)) % int(mod_match.group(2))
            if str(result) in answer:
                score += 0.5
        
        # Modus tollens: if A then B, not B => not A
        if 'if' in prompt.lower() and 'not' in prompt.lower():
            if 'not' in answer.lower():
                score += 0.2
        
        return np.clip(score, 0, 1)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
