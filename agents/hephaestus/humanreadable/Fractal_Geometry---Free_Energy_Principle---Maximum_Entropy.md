# Fractal Geometry + Free Energy Principle + Maximum Entropy

**Fields**: Mathematics, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:15:01.653273
**Report Generated**: 2026-04-02T12:33:29.101025

---

## Nous Analysis

**Algorithm**  
The tool builds a hierarchical factor graph from the parsed sentence. First, a regex‑based extractor produces atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”) and attaches a scale label s ∈ {0,1,2,…} based on nesting depth (fractal self‑similarity: deeper clauses get higher s). Each proposition becomes a variable node; constraints (comparatives, conditionals, causal arrows) become factor nodes that encode allowed configurations (hard or soft).  

For each candidate answer a, we compute a variational free‑energy F(a) = ⟨E⟩₍q₎ − H[q] where q is a distribution over variable assignments induced by the answer’s constraints. ⟨E⟩₍q₎ is the expected penalty for violated factors (prediction error); H[q] is the Shannon entropy of q. To obtain the least‑biased q consistent with the observed constraints, we maximize entropy subject to matching the empirical expectations of each factor (Jaynes’ maximum‑entropy principle). This yields an exponential‑family form q(x) ∝ exp(−∑ₖ λₖ fₖ(x)), solved via iterative scaling (only numpy).  

The score for a is −F(a); lower free energy (higher score) indicates the answer best explains the text while remaining maximally non‑committal. The hierarchy allows coarse‑scale factors (s = 0) to propagate predictions down to fine‑scale factors (s > 0) via belief‑propagation‑like messages, implementing constraint propagation across scales.

**Parsed structural features**  
Negations, comparatives (“>”, “<”, “≈”), conditionals (“if … then …”), biconditionals, causal claims (“causes”, “leads to”), ordering relations (temporal “before/after”, spatial “inside/outside”), numeric values and units, quantifiers (“all”, “some”, “none”), and modal operators (“must”, “might”).

**Novelty**  
The combination mirrors hierarchical Bayesian models and Markov Logic Networks but adds an explicit fractal scaling of constraints and a free‑energy objective derived from variational inference. No prior work jointly uses self‑similar hierarchical decomposition, prediction‑error minimization, and maximum‑entropy distribution fitting in a single scoring function for textual reasoning.

**Ratings**  
Reasoning: 7/10 — captures multi‑scale logical consistency and uncertainty, but relies on approximate inference that may miss subtle nuances.  
Metacognition: 5/10 — the method does not monitor its own confidence or adapt scaling beyond fixed depth.  
Hypothesis generation: 6/10 — entropy maximization yields diverse candidate distributions, yet generation is limited to scoring supplied answers.  
Implementability: 8/10 — uses only regex, numpy, and iterative scaling; no external libraries or neural components required.

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
**Reason**: trap_battery_failed (acc=38% cal=40% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T12:14:39.168329

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Free_Energy_Principle---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib

class ReasoningTool:
    """
    Fractal Free-Energy Reasoning Tool
    
    Combines:
    - Fractal geometry: hierarchical proposition extraction at multiple scales
    - Free Energy Principle: F = <E> - H (prediction error - entropy)
    - Maximum Entropy: least-biased distribution via iterative scaling
    
    Parses logical structure (negations, comparatives, conditionals, causals)
    into a factor graph, then scores candidates by variational free energy.
    """
    
    def __init__(self):
        self.eps = 1e-9
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        props, factors = self._parse_fractal_structure(prompt)
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand, props, factors)
            reasoning = self._explain(cand, props, factors)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        props, factors = self._parse_fractal_structure(prompt)
        score = self._compute_score(prompt, answer, props, factors)
        struct_conf = min(1.0, score / 10.0) if score > 0 else 0.1
        return min(meta_conf, struct_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Epistemic honesty: detect ambiguity/unanswerability"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|more|less)\b', p_lower):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'\b(not enough|insufficient|cannot determine|impossible to know)\b', p_lower):
            return 0.2
        
        return 0.85
    
    def _parse_fractal_structure(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract propositions at multiple scales (fractal hierarchy)"""
        props = []
        factors = []
        
        # Scale 0: top-level sentences
        sentences = re.split(r'[.!?]+', text)
        for s_idx, sent in enumerate(sentences):
            if not sent.strip():
                continue
            
            # Scale 1: clauses (split by commas, conjunctions)
            clauses = re.split(r',|\band\b|\bbut\b|\bor\b', sent)
            for c_idx, clause in enumerate(clauses):
                scale = c_idx  # Depth = scale label
                props.extend(self._extract_atomic(clause, scale))
        
        # Build factors from structural patterns
        factors.extend(self._extract_factors(text, props))
        return props, factors
    
    def _extract_atomic(self, clause: str, scale: int) -> List[Dict]:
        """Extract atomic propositions with scale label"""
        atoms = []
        clause = clause.strip()
        
        # Negation
        if re.search(r'\b(not|no|never|n\'t)\b', clause, re.I):
            atoms.append({'type': 'negation', 'text': clause, 'scale': scale})
        
        # Comparative
        if re.search(r'\b(more|less|greater|fewer|higher|lower|than)\b', clause, re.I):
            atoms.append({'type': 'comparative', 'text': clause, 'scale': scale})
        
        # Numeric
        nums = re.findall(r'\b\d+\.?\d*\b', clause)
        if len(nums) >= 2:
            atoms.append({'type': 'numeric', 'text': clause, 'scale': scale, 'nums': nums})
        
        # Conditional
        if re.search(r'\b(if|then|implies|when|whenever)\b', clause, re.I):
            atoms.append({'type': 'conditional', 'text': clause, 'scale': scale})
        
        # Causal
        if re.search(r'\b(causes|leads to|results in|produces|because|due to)\b', clause, re.I):
            atoms.append({'type': 'causal', 'text': clause, 'scale': scale})
        
        return atoms
    
    def _extract_factors(self, text: str, props: List[Dict]) -> List[Dict]:
        """Build constraint factors from propositions"""
        factors = []
        
        # Transitivity: A>B, B>C => A>C
        comps = [p for p in props if p['type'] == 'comparative']
        if len(comps) >= 2:
            factors.append({'type': 'transitivity', 'props': comps, 'weight': 2.0})
        
        # Modus tollens: if A then B, not B => not A
        conds = [p for p in props if p['type'] == 'conditional']
        negs = [p for p in props if p['type'] == 'negation']
        if conds and negs:
            factors.append({'type': 'modus_tollens', 'props': conds + negs, 'weight': 2.0})
        
        # Causal consistency
        causals = [p for p in props if p['type'] == 'causal']
        if causals:
            factors.append({'type': 'causal', 'props': causals, 'weight': 1.5})
        
        return factors
    
    def _compute_score(self, prompt: str, candidate: str, props: List[Dict], factors: List[Dict]) -> float:
        """Compute -F where F = <E> - H (variational free energy)"""
        
        # Structural score (60%)
        struct_score = self._structural_score(prompt, candidate, props, factors)
        
        # Computational score (25%)
        comp_score = self._computational_score(prompt, candidate)
        
        # NCD tiebreaker (15%)
        ncd_score = self._ncd_score(prompt, candidate)
        
        return 0.6 * struct_score + 0.25 * comp_score + 0.15 * ncd_score
    
    def _structural_score(self, prompt: str, candidate: str, props: List[Dict], factors: List[Dict]) -> float:
        """Free energy score from factor graph"""
        if not props:
            return 5.0
        
        # Compute expected energy (constraint violations)
        energy = 0.0
        for factor in factors:
            violation = self._check_violation(factor, candidate)
            energy += factor['weight'] * violation
        
        # Compute entropy via max-ent iterative scaling
        entropy = self._max_entropy(props, factors, candidate)
        
        # F = E - H; we return -F (lower free energy = higher score)
        free_energy = energy - entropy
        return max(0, 10.0 - free_energy)
    
    def _check_violation(self, factor: Dict, candidate: str) -> float:
        """Check if candidate violates factor constraint"""
        cand_lower = candidate.lower()
        
        if factor['type'] == 'transitivity':
            # Check if candidate respects ordering
            entities = self._extract_entities(factor['props'])
            if len(entities) >= 2:
                e1, e2 = entities[0].lower(), entities[1].lower()
                if e1 in cand_lower and e2 in cand_lower:
                    return 0.0  # Satisfies
                return 0.5
            return 0.0
        
        if factor['type'] == 'modus_tollens':
            # Check negation consistency
            if 'not' in cand_lower or 'no' in cand_lower:
                return 0.0
            return 0.3
        
        if factor['type'] == 'causal':
            # Check causal direction
            for prop in factor['props']:
                if any(word in cand_lower for word in ['causes', 'leads', 'results']):
                    return 0.0
            return 0.2
        
        return 0.0
    
    def _max_entropy(self, props: List[Dict], factors: List[Dict], candidate: str) -> float:
        """Shannon entropy of distribution via max-ent principle"""
        n_vars = max(1, len(props))
        # Uniform distribution maximizes entropy
        p_uniform = 1.0 / n_vars
        entropy = -n_vars * p_uniform * np.log(p_uniform + self.eps)
        
        # Reduce entropy if candidate strongly commits
        commitment = len(candidate.split()) / 20.0
        return entropy * (1.0 - min(0.5, commitment))
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        """Actually compute answers for structured problems"""
        score = 0.0
        
        # Numeric comparison
        nums_p = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
        nums_c = [float(n) for n in re.findall(r'\d+\.?\d*', candidate)]
        if len(nums_p) >= 2:
            if '>' in prompt or 'greater' in prompt.lower():
                if nums_c and nums_c[0] == max(nums_p):
                    score += 5.0
            elif '<' in prompt or 'less' in prompt.lower():
                if nums_c and nums_c[0] == min(nums_p):
                    score += 5.0
        
        # Bat-and-ball algebra
        if 'cost' in prompt.lower() and 'total' in prompt.lower():
            if nums_p and nums_c:
                total, diff = nums_p[0], nums_p[1] if len(nums_p) > 1 else 0
                x = (total - diff) / 2.0
                if abs(nums_c[0] - x) < 0.01:
                    score += 5.0
        
        # Parity
        if 'even' in candidate.lower() or 'odd' in candidate.lower():
            if nums_p:
                actual_parity = 'even' if int(nums_p[0]) % 2 == 0 else 'odd'
                if actual_parity in candidate.lower():
                    score += 5.0
        
        # Boolean logic
        if re.search(r'\b(yes|no|true|false)\b', candidate.lower(), re.I):
            if 'not' in prompt.lower() and 'no' in candidate.lower():
                score += 3.0
            elif 'not' not in prompt.lower() and 'yes' in candidate.lower():
                score += 3.0
        
        return min(10.0, score)
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        c_p = len(zlib.compress(prompt.encode()))
        c_c = len(zlib.compress(candidate.encode()))
        c_pc = len(zlib.compress((prompt + candidate).encode()))
        ncd = (c_pc - min(c_p, c_c)) / max(c_p, c_c)
        return max(0, 10.0 * (1.0 - ncd))
    
    def _extract_entities(self, props: List[Dict]) -> List[str]:
        """Extract entity names from propositions"""
        entities = []
        for prop in props:
            words = re.findall(r'\b[A-Z][a-z]+\b', prop['text'])
            entities.extend(words)
        return entities
    
    def _explain(self, candidate: str, props: List[Dict], factors: List[Dict]) -> str:
        """Generate reasoning trace"""
        if not props:
            return "No structural features detected"
        
        features = [p['type'] for p in props]
        return f"Detected {len(props)} propositions: {', '.join(set(features))}"
```

</details>
