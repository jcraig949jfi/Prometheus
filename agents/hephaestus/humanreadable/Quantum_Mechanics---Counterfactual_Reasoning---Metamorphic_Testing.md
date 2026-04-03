# Quantum Mechanics + Counterfactual Reasoning + Metamorphic Testing

**Fields**: Physics, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T13:43:37.597309
**Report Generated**: 2026-04-02T11:44:49.243556

---

## Nous Analysis

**Algorithm: Superposed Counterfactual Metamorphic Scorer (SCMS)**  
The scorer treats each candidate answer as a quantum‑like state vector |ψ⟩ over a basis of *metamorphic relations* (MRs) extracted from the prompt. Each basis vector corresponds to a concrete MR (e.g., “if X is doubled then Y must increase by ≥ 0”, “negation of P implies ¬Q”, “transitive chain A → B → C”). The vector’s amplitudes are initialized from the answer’s textual match to each MR using deterministic feature extraction (regex, dependency parse).  

1. **Data structures**  
   - `MR_basis: List[Tuple[str, Callable[[str], bool]]]` – each entry holds a textual pattern and a predicate that returns True when the answer satisfies the relation.  
   - `amplitudes: np.ndarray[float]` – same length as `MR_basis`; each element ∈ [0,1] reflects degree of satisfaction.  
   - `covariance: np.ndarray[float, float]` – captures entanglement between MRs (e.g., if MR_i and MR_j are logically linked via modus ponens or transitivity). Initialized as identity; updated by adding 0.2 for each detected logical dependency.  

2. **Operations**  
   - **State preparation:** For each MR, run its predicate on the candidate answer; set amplitude = 1 if satisfied, else 0.  
   - **Entanglement update:** Scan the answer for cue words (“if”, “then”, “because”, “therefore”) and apply a rule‑based linker to set off‑diagonal covariance entries.  
   - **Measurement (scoring):** Compute the expected value of the projector onto the “consistent‑world” subspace:  
     `score = amplitudes @ covariance @ amplitudes`  
     (equivalent to ⟨ψ|C|ψ⟩ where C encodes logical consistency). Higher scores indicate that the answer simultaneously satisfies many MRs and respects their inter‑dependencies.  

3. **Structural features parsed**  
   - Negations (`not`, `no`, `never`) → MRs of form ¬P.  
   - Comparatives (`more than`, `less than`, `twice`) → numeric MRs with scaling factors.  
   - Conditionals (`if … then …`, `unless`) → implication MRs.  
   - Causal verbs (`cause`, `lead to`, `result in`) → do‑calculus‑style MRs.  
   - Ordering/temporal markers (`before`, `after`, `increasing`) → transitive MRs.  
   - Quantifiers (`all`, `some`, `none`) → universal/existential MRs.  

4. **Novelty**  
   The fusion of quantum‑style superposition (simultaneous consideration of multiple MRs), counterfactual entailment (do‑calculus‑style MRs), and metamorphic relations (output‑space constraints) is not present in existing scoring tools, which typically use either similarity metrics or isolated rule checks. SCMS therefore represents a novel algorithmic combination.  

**Ratings**  
Reasoning: 8/10 — captures deep logical structure via entangled MRs but relies on hand‑crafted patterns.  
Metacognition: 6/10 — can reflect on consistency through covariance, yet lacks self‑adjustment of MR set.  
Hypothesis generation: 7/10 — generates alternative worlds by flipping MR amplitudes, enabling counterfactual exploration.  
Implementability: 9/10 — uses only numpy and std lib; all operations are linear‑algebraic or regex‑based.

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
**Reason**: trap_battery_failed (acc=36% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:07:42.572595

---

## Code

**Source**: scrap

[View code](./Quantum_Mechanics---Counterfactual_Reasoning---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Callable, Dict, Tuple

"""
Superposed Counterfactual Metamorphic Scorer (SCMS)

Treats each candidate answer as a quantum-like state vector over metamorphic relations
extracted from the prompt. Scores via entangled consistency measurement.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Callable


class ReasoningTool:
    def __init__(self):
        self.mr_extractors = self._build_mr_extractors()
    
    def _build_mr_extractors(self) -> List[Tuple[str, Callable[[str, str], float]]]:
        """Build metamorphic relation extractors with predicates."""
        return [
            ("negation", self._check_negation),
            ("comparative_numeric", self._check_comparative),
            ("conditional", self._check_conditional),
            ("causal", self._check_causal),
            ("temporal", self._check_temporal),
            ("quantifier", self._check_quantifier),
            ("numeric_compute", self._compute_numeric),
            ("probability_compute", self._compute_probability),
        ]
    
    def _check_negation(self, prompt: str, answer: str) -> float:
        """Check negation consistency."""
        neg_words = r'\b(not|no|never|neither|none)\b'
        prompt_neg = len(re.findall(neg_words, prompt, re.I))
        answer_neg = len(re.findall(neg_words, answer, re.I))
        if prompt_neg > 0:
            return 1.0 if answer_neg > 0 else 0.3
        return 0.5
    
    def _check_comparative(self, prompt: str, answer: str) -> float:
        """Check comparative/numeric constraints."""
        comp_pattern = r'\b(more|less|greater|fewer|higher|lower|twice|double|half)\b'
        if not re.search(comp_pattern, prompt, re.I):
            return 0.5
        
        # Extract numbers from prompt and answer
        p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
        
        if not a_nums:
            return 0.2
        
        # Check if answer respects comparative direction
        if re.search(r'\b(more|greater|higher|increase)\b', prompt, re.I):
            if p_nums and a_nums and max(a_nums) > min(p_nums):
                return 1.0
        elif re.search(r'\b(less|fewer|lower|decrease)\b', prompt, re.I):
            if p_nums and a_nums and min(a_nums) < max(p_nums):
                return 1.0
        
        return 0.4
    
    def _check_conditional(self, prompt: str, answer: str) -> float:
        """Check if-then logical consistency."""
        if_pattern = r'\bif\b.*\bthen\b'
        if not re.search(if_pattern, prompt, re.I):
            return 0.5
        
        # Parse if-then structure
        match = re.search(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', prompt, re.I)
        if match:
            antecedent, consequent = match.groups()
            # Check if answer contains consequent terms
            cons_words = set(re.findall(r'\w+', consequent.lower()))
            ans_words = set(re.findall(r'\w+', answer.lower()))
            overlap = len(cons_words & ans_words) / (len(cons_words) + 1)
            return min(1.0, overlap * 2)
        return 0.5
    
    def _check_causal(self, prompt: str, answer: str) -> float:
        """Check causal relation consistency."""
        causal_pattern = r'\b(cause|lead|result|because|therefore|thus)\b'
        p_causal = bool(re.search(causal_pattern, prompt, re.I))
        a_causal = bool(re.search(causal_pattern, answer, re.I))
        
        if p_causal:
            return 0.8 if a_causal else 0.4
        return 0.5
    
    def _check_temporal(self, prompt: str, answer: str) -> float:
        """Check temporal ordering consistency."""
        temp_pattern = r'\b(before|after|then|first|next|finally|earlier|later)\b'
        if not re.search(temp_pattern, prompt, re.I):
            return 0.5
        
        a_temp = bool(re.search(temp_pattern, answer, re.I))
        return 0.7 if a_temp else 0.3
    
    def _check_quantifier(self, prompt: str, answer: str) -> float:
        """Check quantifier consistency."""
        univ_pattern = r'\b(all|every|each|always)\b'
        exist_pattern = r'\b(some|any|sometimes)\b'
        none_pattern = r'\b(no|none|never)\b'
        
        if re.search(univ_pattern, prompt, re.I):
            if re.search(none_pattern, answer, re.I):
                return 0.0
            return 0.7 if re.search(univ_pattern, answer, re.I) else 0.4
        return 0.5
    
    def _compute_numeric(self, prompt: str, answer: str) -> float:
        """Compute numeric answer correctness."""
        # Extract arithmetic expressions
        expr_match = re.search(r'(\d+\.?\d*)\s*([\+\-\*/])\s*(\d+\.?\d*)', prompt)
        if expr_match:
            left, op, right = expr_match.groups()
            left, right = float(left), float(right)
            expected = {'+':-1, '-':-1, '*':-1, '/':-1}
            if op == '+': expected = left + right
            elif op == '-': expected = left - right
            elif op == '*': expected = left * right
            elif op == '/' and right != 0: expected = left / right
            
            if expected != -1:
                a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
                if a_nums:
                    closest = min(a_nums, key=lambda x: abs(x - expected))
                    if abs(closest - expected) < 0.01:
                        return 1.0
                    elif abs(closest - expected) < expected * 0.1:
                        return 0.7
        
        # Numeric comparison (e.g., "9.11 vs 9.9")
        if re.search(r'which.*(?:greater|larger|bigger|more)', prompt, re.I):
            p_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
            if len(p_nums) >= 2:
                expected_max = max(p_nums)
                a_nums = [float(x) for x in re.findall(r'\d+\.?\d*', answer)]
                if a_nums and abs(max(a_nums) - expected_max) < 0.01:
                    return 1.0
        
        return 0.5
    
    def _compute_probability(self, prompt: str, answer: str) -> float:
        """Compute Bayesian/probability answers."""
        # Detect probability questions
        if not re.search(r'\b(probability|percent|%|likely|chance)\b', prompt, re.I):
            return 0.5
        
        # Extract percentages/probabilities
        p_probs = re.findall(r'(\d+\.?\d*)%', prompt)
        a_probs = re.findall(r'(\d+\.?\d*)%', answer)
        
        if p_probs and a_probs:
            # Simple base rate check
            p_val = float(p_probs[0])
            a_val = float(a_probs[0])
            if abs(a_val - p_val) < 5:
                return 0.8
        
        return 0.5
    
    def _compute_entanglement(self, prompt: str, mr_amplitudes: np.ndarray) -> np.ndarray:
        """Build covariance matrix capturing MR dependencies."""
        n = len(mr_amplitudes)
        covariance = np.eye(n)
        
        # Detect logical connectives that create entanglement
        if re.search(r'\bif\b.*\bthen\b', prompt, re.I):
            # Conditional creates entanglement between antecedent and consequent
            covariance[2, 3] += 0.2  # conditional <-> causal
            covariance[3, 2] += 0.2
        
        if re.search(r'\b(because|therefore|thus)\b', prompt, re.I):
            # Causal reasoning entangles multiple MRs
            covariance[3, 0] += 0.15  # causal <-> negation
            covariance[0, 3] += 0.15
        
        if re.search(r'\b(before|after)\b', prompt, re.I):
            # Temporal creates ordering constraints
            covariance[4, 3] += 0.2  # temporal <-> causal
            covariance[3, 4] += 0.2
        
        return covariance
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic problems in the prompt."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|criteria)\b', p_lower):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(cannot be determined|not enough information|insufficient)\b', p_lower):
            return 0.2
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates using SCMS."""
        results = []
        
        for candidate in candidates:
            # Build state vector
            amplitudes = np.array([extractor(prompt, candidate) for _, extractor in self.mr_extractors])
            
            # Compute entanglement matrix
            covariance = self._compute_entanglement(prompt, amplitudes)
            
            # Quantum-inspired measurement: <psi|C|psi>
            structural_score = float(amplitudes @ covariance @ amplitudes) / len(amplitudes)
            
            # NCD as minor tiebreaker (max 15% contribution)
            ncd_score = self._ncd(prompt, candidate)
            
            # Final score: 85% structural + 15% NCD
            final_score = 0.85 * structural_score + 0.15 * (1 - ncd_score)
            
            # Generate reasoning
            reasoning = f"Structural consistency: {structural_score:.2f}, NCD: {ncd_score:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer (0-1)."""
        # First check meta-confidence
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # Build state vector
        amplitudes = np.array([extractor(prompt, answer) for _, extractor in self.mr_extractors])
        covariance = self._compute_entanglement(prompt, amplitudes)
        
        # Compute base confidence from structural score
        structural_score = float(amplitudes @ covariance @ amplitudes) / len(amplitudes)
        
        # Cap confidence based on structural match
        if structural_score > 0.8:
            base_conf = 0.85
        elif structural_score > 0.6:
            base_conf = 0.65
        elif structural_score > 0.4:
            base_conf = 0.45
        else:
            base_conf = 0.25
        
        # Apply meta-confidence cap
        return min(base_conf, meta_conf)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
```

</details>
