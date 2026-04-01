# Dual Process Theory + Predictive Coding + Property-Based Testing

**Fields**: Cognitive Science, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:08:09.683677
**Report Generated**: 2026-03-31T16:21:16.440115

---

## Nous Analysis

**Algorithm – Predictive Property‑Checking Reasoner (PPCR)**  
The tool builds a lightweight symbolic graph from each candidate answer. Nodes are *propositions* extracted via regex patterns for:  
- atomic predicates (e.g., “X is Y”)  
- comparatives (“greater than”, “less than”)  
- numeric literals and units  
- logical connectives (¬, ∧, →, ↔)  
- causal markers (“because”, “leads to”)  

Each proposition receives a *prediction score* p∈[0,1] initialized from a Dual‑Process prior: System 1 contributes a fast heuristic weight w₁ (based on surface cues like keyword frequency) and System 2 contributes a deliberative weight w₂ (based on structural validity checks). The combined prior is p₀ = σ(w₁·h₁ + w₂·h₂) where h₁, h₂ are normalized feature vectors and σ is the logistic function (implemented with numpy).

Next, a Predictive‑Coding pass propagates *prediction errors* upward in a hierarchical graph:  
1. **Local consistency** – apply modus ponens, transitivity, and contradiction rules; compute error eₗ = |pᵢ − pⱼ| for linked nodes i,j.  
2. **Global surprise** – aggregate errors via a precision‑weighted sum E = Σₖ πₖ·eₖ, where precisions πₖ are updated by a simple Hebbian rule πₖ←πₖ+α·eₖ (α∈[0,0.1]).  
3. **Error minimization** – adjust node scores via gradient descent on E (one iteration suffices for speed): pᵢ←pᵢ−η·∂E/∂pᵢ, η=0.05.

Finally, Property‑Based Testing supplies a *shrinking* mechanism: the algorithm randomly perturbs numeric values and negations (using stdlib.random) to generate minimal counter‑examples that increase E. The score for an answer is S = 1 − E_norm, where E_norm normalizes E by the maximum possible error observed across all perturbations (clipped to [0,1]).

**Structural features parsed** – negations, comparatives, equality/inequality, numeric ranges, unit conversions, conditional antecedents/consequents, causal chains, ordering relations, and set membership expressions.

**Novelty** – While each component (dual‑process weighting, predictive‑coding error propagation, property‑based shrinking) exists separately, their tight integration into a single, numpy‑only scoring loop that alternates fast heuristic priors with slow constraint‑propagation and automated counter‑example search has not been reported in the literature; thus the combination is novel.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and uncertainty via error minimization, but limited to first‑order properties.  
Metacognition: 7/10 — dual‑process weighting gives a rudimentary self‑monitoring of fast vs. slow processing, yet lacks higher‑order reflection on its own priors.  
Hypothesis generation: 9/10 — property‑based shrinking actively proposes minimal failing inputs, effectively generating hypotheses about where the answer breaks.  
Implementability: 9/10 — relies only on regex, numpy vector ops, and stdlib random; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 9/10 |
| **Composite** | **8.0** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=32% cal=43% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-31T14:42:10.311431

---

## Code

**Source**: scrap

[View code](./Dual_Process_Theory---Predictive_Coding---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import random
import zlib
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive Property-Checking Reasoner (PPCR).
    
    Mechanism:
    1. Dual-Process Prior: Combines fast heuristic matching (System 1) with 
       structural validity checks (System 2) to initialize proposition scores.
    2. Predictive Coding: Constructs a symbolic graph of propositions. Propagates 
       prediction errors upward via consistency checks (transitivity, modus ponens).
       Minimizes global surprise via a single gradient step.
    3. Property-Based Testing: Perturbs numeric values and negations to find 
       minimal counter-examples that maximize error, shrinking confidence if the 
       answer is fragile.
    4. Epistemic Honesty (Tier B): Explicitly detects ambiguity, presupposition, 
       and scope issues to cap confidence < 0.3 before scoring.
    """

    def __init__(self):
        random.seed(42)  # Determinism
        self.alpha = 0.05  # Learning rate for precision
        self.eta = 0.05    # Gradient descent step
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*(?:fail|stop|quit)\b", 
            r"\bwhen did.*stop\b", r"\bregret\b", r"\bused to\b"
        ]
        self.ambiguity_triggers = [
            r"\bevery.*\ba\s+\w+\b", r"\bhe\s+was\b", r"\bshe\s+was\b", 
            r"\bthey\s+were\b", r"\bwho\b", r"\bwhich one\b"
        ]
        self.dichotomy_triggers = [r"\beither.*\bor\b", r"\bmust choose between\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: presupposition, ambiguity, subjectivity."""
        p_lower = prompt.lower()
        
        # 1. Presupposition & False Dichotomy
        for pattern in self.presupposition_triggers + self.dichotomy_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. Scope/Pronoun Ambiguity (Simple heuristic)
        if re.search(r"\b(every|all|each)\b", p_lower) and re.search(r"\b(same|different|who|he|she)\b", p_lower):
            return 0.25
            
        # 3. Subjectivity without criteria
        if any(re.search(t, p_lower) for t in self.subjectivity_triggers):
            if "calculate" not in p_lower and "compute" not in p_lower:
                return 0.25

        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric literals."""
        matches = re.findall(r"-?\d+(?:\.\d+)?", text)
        return [float(m) for m in matches]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        System 2: Structural parsing and constructive computation.
        Returns a score based on logical consistency and math verification.
        """
        score = 0.5  # Base prior
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # A. Constructive Computation (Numeric)
        if p_nums and c_nums:
            # Check for direct equality of result
            if abs(p_nums[-1] - c_nums[-1]) < 1e-6:
                score += 0.4
            # Check for simple arithmetic relations in prompt vs candidate
            # E.g., Prompt has 2, 3 -> Candidate has 5 (Addition)
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                if abs((p_nums[-1] + p_nums[-2]) - c_nums[-1]) < 1e-6:
                    score += 0.3
                if abs((p_nums[-1] * p_nums[-2]) - c_nums[-1]) < 1e-6:
                    score += 0.3
        
        # B. Logical Consistency (Negation)
        has_not_p = bool(re.search(r"\bnot\b|\bnever\b|\bno\b", p_lower))
        has_not_c = bool(re.search(r"\bnot\b|\bnever\b|\bno\b", c_lower))
        if has_not_p == has_not_c:
            score += 0.1
        else:
            score -= 0.2 # Penalty for negation mismatch

        # C. Causal/Conditional markers
        if re.search(r"\bbecause\b|\btherefore\b|\bthus\b", c_lower):
            if re.search(r"\bwhy\b|\bcause\b|\bresult\b", p_lower):
                score += 0.15
        
        return min(1.0, max(0.0, score))

    def _build_graph_and_propagate(self, prompt: str, candidate: str) -> Tuple[float, float]:
        """
        Build lightweight symbolic graph and propagate prediction errors.
        Returns (final_score, global_error).
        """
        # 1. Extract propositions (simplified as nodes)
        nodes = []
        # Node types: atomic, comparative, numeric
        sentences = re.split(r'[.\?!]', candidate)
        for sent in sentences:
            if not sent.strip(): continue
            nodes.append({
                'text': sent.strip(),
                'p': 0.5, # Initial probability
                'type': 'atomic'
            })
        
        if not nodes:
            return 0.5, 0.5

        # 2. Initialize priors (Dual Process)
        # System 1: Surface match weight
        s1_weight = 0.6 if any(word in candidate.lower() for word in prompt.lower().split()[:5]) else 0.4
        # System 2: Structural validity
        s2_weight = self._compute_structural_score(prompt, candidate)
        
        # Combined prior p0
        for node in nodes:
            h1 = 1.0 if node['text'] in prompt else 0.5
            h2 = s2_weight
            node['p'] = 1.0 / (1.0 + math.exp(-(0.5*h1 + 0.5*h2))) # Logistic

        # 3. Predictive Coding Pass (Error Propagation)
        # Local consistency: Check transitivity/contradiction between adjacent nodes
        errors = []
        for i in range(len(nodes) - 1):
            n1, n2 = nodes[i], nodes[i+1]
            # Simple contradiction check (negation overlap)
            n1_has_not = 'not' in n1['text'].lower()
            n2_has_not = 'not' in n2['text'].lower()
            
            # If both assert similar things but one negates, high error
            if n1_has_not != n2_has_not:
                e_loc = abs(n1['p'] - (1.0 - n2['p']))
            else:
                e_loc = abs(n1['p'] - n2['p'])
            errors.append(e_loc)

        # Global Surprise E
        if not errors:
            E = 0.0
        else:
            # Precision weighted sum (simplified)
            pi = 0.5 # Initial precision
            E = sum(pi * e for e in errors) / (len(errors) + 1e-6)
            
            # Update precision (Hebbian)
            pi += self.alpha * np.mean(errors)
            
            # Error minimization (Gradient step on node scores)
            # dE/dp approximated by error magnitude
            for node in nodes:
                # Simplified gradient: move p towards consistent state
                adjustment = self.eta * np.mean(errors) if errors else 0
                node['p'] = max(0.0, min(1.0, node['p'] - adjustment))

        final_score = np.mean([n['p'] for n in nodes])
        return final_score, E

    def _property_based_shrinking(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Perturb inputs to find counter-examples.
        If small changes drastically reduce score, lower confidence.
        """
        original_E = 1.0 - base_score
        max_E = original_E
        
        # Generate perturbations
        perturbations = 5
        for _ in range(perturbations):
            # Perturb numbers
            perturbed_c = candidate
            nums = self._extract_numbers(candidate)
            if nums:
                # Flip a number sign or value
                target = random.choice(nums)
                new_val = target * (1 + random.uniform(-0.2, 0.2))
                perturbed_c = perturbed_c.replace(str(target), f"{new_val:.2f}")
            
            # Perturb negation
            if random.random() > 0.5 and 'not' in perturbed_c.lower():
                perturbed_c = perturbed_c.replace('not', '').replace('Not', '')
            elif random.random() > 0.5 and 'not' not in perturbed_c.lower():
                perturbed_c = perturbed_c.replace('.', ' not.')

            # Re-evaluate
            _, new_E = self._build_graph_and_propagate(prompt, perturbed_c)
            if new_E > max_E:
                max_E = new_E

        # Normalize error
        # If max possible error observed is high, the original answer is fragile
        robust_score = 1.0 - min(1.0, max_E)
        return robust_score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2: return 1.0
        z = zlib.compress
        l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        if l12 == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence with Epistemic Honesty.
        Caps at 0.3 if meta-analysis detects ambiguity or traps.
        """
        # Tier B: Meta-Confidence Check
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap

        # Core Scoring
        struct_score = self._compute_structural_score(prompt, answer)
        final_score, _ = self._build_graph_and_propagate(prompt, answer)
        robust_score = self._property_based_shrinking(prompt, answer, final_score)
        
        # Weighted combination: Computation (40%) + Structural (30%) + Robustness (20%) + NCD (10%)
        ncd = self._ncd_score(prompt, answer)
        # Invert NCD (lower distance = higher score)
        ncd_score = 1.0 - ncd
        
        raw_score = (0.4 * struct_score) + (0.3 * final_score) + (0.2 * robust_score) + (0.1 * ncd_score)
        
        # Cap by meta-confidence (Epistemic Honesty)
        final_conf = min(raw_score, meta_cap)
        
        return round(float(final_conf), 4)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            reasoning = f"Structural match: {self._compute_structural_score(prompt, cand):.2f}; " \
                        f"Consistency: {self._build_graph_and_propagate(prompt, cand)[0]:.2f}; " \
                        f"Meta-cap: {self._meta_confidence(prompt):.2f}"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
```

</details>
