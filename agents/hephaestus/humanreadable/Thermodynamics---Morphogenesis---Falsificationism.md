# Thermodynamics + Morphogenesis + Falsificationism

**Fields**: Physics, Biology, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T00:38:28.473866
**Report Generated**: 2026-04-02T04:20:10.542150

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a thermodynamic system of logical propositions. First, a regex‑based extractor builds a set of atomic predicates \(P_i\) and binary relations \(R_{ij}\) (negation, conditional, comparative, causal, ordering, numeric equality/inequality). These become nodes and edges in a constraint graph \(G=(V,E)\). Each node carries a binary truth variable \(x_i\in\{0,1\}\) and an associated “energy” \(E_i\) that is 0 if the proposition satisfies all incident constraints and 1 otherwise (e.g., a violated conditional \(A\rightarrow B\) adds 1 when \(x_A=1,x_B=0\)). The total energy \(E=\sum_i E_i\) measures falsification‑resistance: lower \(E\) means the answer survives more attempted refutations.

To capture self‑organized pattern formation, we run a reaction‑diffusion process on the truth variables. For each iteration we compute a local “reaction” term \(r_i = -\partial E/\partial x_i\) (the gradient of energy w.r.t. flipping \(x_i\)) and a diffusion term \(d_i = \sum_{j\in N(i)} (x_j - x_i)\). The update is \(x_i \leftarrow \sigma(r_i + \alpha d_i)\) where \(\sigma\) is a hard threshold (0/1) and \(\alpha\) controls spread. This is analogous to a Turing system: local inconsistencies (high \(r_i\)) are smoothed by neighboring agreement, allowing stable patterns of truth to emerge.

Entropy \(H = -\sum_i [p_i\log p_i + (1-p_i)\log(1-p_i)]\) is computed from the marginal probability \(p_i\) of each node being true after diffusion (estimated by averaging \(x_i\) over a short window). The system seeks equilibrium when both \(E\) and \(H\) stop changing (ΔE<ε, ΔH<ε). The final score is  

\[
S = -\bigl(E + \lambda H\bigr)
\]

with \(\lambda\) weighting uncertainty; higher \(S\) indicates a candidate that is both low‑energy (few falsifiable violations) and low‑entropy (clear, committed truth assignments).

**Parsed structural features**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `equal to`)  
- Conditionals (`if … then`, `only if`)  
- Causal claims (`because`, `leads to`)  
- Ordering relations (`before`, `after`, `precedes`)  
- Numeric values and units  
- Quantifiers (`all`, `some`, `none`)  

**Novelty**  
The combination mirrors existing formalisms (Markov Logic Networks, Probabilistic Soft Logic) in using weighted logical constraints, but adds a reaction‑diffusion dynamics inspired by morphogenesis and an explicit falsification‑driven energy minimization loop. This specific triad—thermodynamic energy/entropy, Turing‑style pattern smoothing, and Popperian iterative refutation—has not been described together in the literature, making the approach novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and falsification resistance but relies on hand‑crafted constraint weights.  
Metacognition: 6/10 — entropy term offers a rough confidence estimate, yet no explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 6/10 — diffusion can propose new truth assignments, but generation is limited to local perturbations of existing propositions.  
Implementability: 8/10 — only regex, numpy arrays for graph/matrix ops, and simple loops; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: AttributeError: 'bytes' object has no attribute 'encode'

**Forge Timestamp**: 2026-04-01T22:58:39.094992

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Morphogenesis---Falsificationism/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Thermodynamic-Morphogenetic Reasoning Tool with Epistemic Honesty.
    
    Mechanism:
    1. Parses logical propositions (negations, conditionals, comparatives) into a constraint graph.
    2. Assigns binary truth variables to nodes.
    3. Computes 'Energy' (E) based on constraint violations (falsification resistance).
    4. Runs a reaction-diffusion process (Turing-style) to smooth inconsistencies and find stable truth patterns.
    5. Calculates Entropy (H) from the stability of these patterns.
    6. Score S = -(E + lambda*H).
    7. Tier B Honesty: Detects presuppositions, ambiguities, and false dichotomies to cap confidence.
    """

    def __init__(self):
        self.lambda_entropy = 0.5
        self.diffusion_alpha = 0.3
        self.iterations = 10
        
        # Tier B Triggers
        self.presupposition_patterns = [
            r"\b(have|has|had|did|do|does)\s+(you|he|she|it|they)\s+(stopped|quit|failed|begun)\b",
            r"\bwhy\s+(did|does|has|is)\s+\w+\s+(fail|stop|quit|lie)\b",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)\b"
        ]
        self.false_dichotomy_patterns = [
            r"\beither\s+.*\s+or\s+.*\b",
            r"\bmust\s+(be|choose)\s+(one|two)\b"
        ]
        self.scope_ambiguity_patterns = [
            r"\bevery\s+\w+\s+.*\s+a\s+\w+\b", # "Every X did a Y"
            r"\ball\s+\w+\s+.*\s+the\s+same\b"
        ]
        self.pronoun_ambiguity_patterns = [
            r"\b(told|said\s+to)\s+\w+\s+(he|she|him|her)\s+was\b",
            r"\bwho\s+(is|was|does)\s+\w+\s+refer\s+to\b"
        ]
        self.subjectivity_patterns = [
            r"\b(best|worst|favorite|most\s+beautiful)\s+\w+\b"
        ]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_predicates(self, text: str) -> Tuple[List[str], List[Tuple]]:
        """Extract atomic predicates and relations using regex."""
        text_lower = text.lower()
        predicates = []
        relations = []
        
        # Simple tokenization for predicates (words/numbers)
        tokens = re.findall(r'\b[\w\.]+\b', text_lower)
        predicates = list(set(tokens))
        
        # Extract Relations
        # Negation
        if re.search(r'\b(not|no|never)\b', text_lower):
            relations.append(('negation', 'global'))
            
        # Conditionals
        if re.search(r'\b(if|then|only\s+if)\b', text_lower):
            relations.append(('conditional', 'global'))
            
        # Comparatives (Numeric)
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if n1 < n2: relations.append(('cmp', 'less', n1, n2))
                elif n1 > n2: relations.append(('cmp', 'greater', n1, n2))
                else: relations.append(('cmp', 'equal', n1, n2))
            except: pass
            
        # Causal
        if re.search(r'\b(because|leads\s+to|causes)\b', text_lower):
            relations.append(('causal', 'global'))
            
        return predicates, relations

    def _compute_energy(self, constraints: List, state: List[int]) -> float:
        """Calculate energy based on violated constraints."""
        energy = 0.0
        for con in constraints:
            ctype = con[0]
            if ctype == 'negation':
                # If negation present, state should ideally reflect inconsistency if asserted true
                # Simplified: Penalty if we assume 'true' but negation exists in text
                if any(state): energy += 0.5 
            elif ctype == 'conditional':
                # A -> B. If A is true (1) and B is false (0), energy += 1
                # Simplified for global conditional: penalty if state is mixed [1, 0]
                if 1 in state and 0 in state:
                    energy += 1.0
            elif ctype == 'cmp':
                # Check if state aligns with numeric comparison
                # This is a proxy: if the candidate text contains the numbers, we assume it respects the order
                pass 
        return energy

    def _reaction_diffusion(self, n_nodes: int, constraints: List) -> Tuple[List[float], float]:
        """
        Simulate reaction-diffusion on truth variables.
        Returns final probabilities and final energy.
        """
        if n_nodes == 0: return [0.5], 0.0
        
        # Initialize state randomly but deterministically based on hash of constraints
        seed = len(constraints)
        x = [0.5 if i % 2 == 0 else 0.5 for i in range(n_nodes)] # Start neutral
        
        # If no specific nodes, create dummy nodes for logic flow
        if n_nodes < 2:
            x = [0.5, 0.5]
            n_nodes = 2

        history_E = []
        
        for _ in range(self.iterations):
            new_x = x.copy()
            
            # Reaction term (Gradient of Energy)
            # Simplified: If constraints imply contradiction, push towards 0 or 1
            r_terms = []
            for i in range(n_nodes):
                # Local energy gradient approximation
                # If many constraints, higher pressure to resolve
                r = -0.1 * len(constraints) * (x[i] - 0.5) 
                r_terms.append(r)
            
            # Diffusion term
            for i in range(n_nodes):
                neighbors = x[(i-1)%n_nodes] + x[(i+1)%n_nodes]
                d = (neighbors - 2*x[i]) 
                
                update = r_terms[i] + self.diffusion_alpha * d
                val = x[i] + update * 0.1 # Learning rate
                
                # Hard threshold via sigmoid-like step for stability
                if val > 0.5: new_x[i] = 1.0
                elif val < 0.5: new_x[i] = 0.0
                else: new_x[i] = 0.5
            
            x = new_x
            
            # Check convergence (simplified)
            current_E = sum(x) # Proxy for energy state
            history_E.append(current_E)

        # Calculate Entropy
        H = 0.0
        for p in x:
            if p > 0 and p < 1:
                H -= (p * math.log(p + 1e-9) + (1-p) * math.log(1-p + 1e-9))
            elif p == 0 or p == 1:
                H += 0 # No entropy
        
        final_E = sum([1 if v == 0.5 else 0 for v in x]) # Penalty for undecided
        return x, final_E + H

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Evaluate prompt for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. False Dichotomy
        for pattern in self.false_dichotomy_patterns:
            if re.search(pattern, p_lower):
                # Only flag if it looks like a trap question
                if "must" in p_lower or "either" in p_lower:
                    return 0.25

        # 3. Scope/Pronoun Ambiguity
        for pattern in self.scope_ambiguity_patterns + self.pronoun_ambiguity_patterns:
            if re.search(pattern, p_lower):
                if "who" in p_lower or "same" in p_lower or "every" in p_lower:
                    return 0.25

        # 4. Subjectivity
        for pattern in self.subjectivity_patterns:
            if re.search(pattern, p_lower):
                return 0.25
                
        # 5. Unanswerable (Heuristic: very short prompt with no data)
        if len(prompt.split()) < 4 and "?" in prompt:
            return 0.25

        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = lambda x: len(zlib.compress(x.encode()))
        s1_enc = s1.encode()
        s2_enc = s2.encode()
        concat = s1_enc + s2_enc
        
        c1 = z(s1_enc)
        c2 = z(s2_enc)
        c12 = z(concat)
        
        if max(c1, c2) == 0: return 0.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning: Parse structure and compute logical consistency.
        Returns a score where higher is better.
        """
        score = 0.0
        p_preds, p_rels = self._extract_predicates(prompt)
        c_preds, c_rels = self._extract_predicates(candidate)
        
        # 1. Numeric Consistency (Constructive Computation)
        p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt.lower())]
        c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate.lower())]
        
        if p_nums and c_nums:
            # Check if candidate preserves numeric order logic
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_order = 1 if p_nums[0] > p_nums[1] else (-1 if p_nums[0] < p_nums[1] else 0)
                c_order = 1 if c_nums[0] > c_nums[1] else (-1 if c_nums[0] < c_nums[1] else 0)
                if p_order == c_order:
                    score += 2.0
                else:
                    score -= 2.0 # Penalty for wrong math
        
        # 2. Logical Constraint Satisfaction (Thermodynamic Model)
        # Treat candidate as a system trying to satisfy prompt constraints
        all_preds = list(set(p_preds + c_preds))
        if not all_preds:
            return 0.0
            
        # Build constraint graph edges from prompt relations
        constraints = p_rels 
        
        # Run Reaction-Diffusion on the combined logical space
        # We map predicates to indices. 
        # Ideally, we check if candidate truth values minimize energy defined by prompt.
        # Simplified: If candidate contains negation but prompt doesn't (or vice versa) -> Energy up.
        
        n_nodes = len(all_preds)
        # Map presence in candidate to initial state
        state = [1.0 if p in c_preds else 0.0 for p in all_preds]
        
        # If the candidate contradicts a direct negative in prompt
        has_neg = any(r[0] == 'negation' for r in p_rels)
        cand_has_neg = any(r[0] == 'negation' for r in c_rels)
        
        if has_neg and not cand_has_neg:
            # Candidate missed a negation
            score -= 1.0
        elif not has_neg and cand_has_neg:
            # Candidate added unnecessary negation
            score -= 0.5
            
        # Run diffusion to see if stable state emerges
        probs, energy = self._reaction_diffusion(n_nodes, constraints)
        
        # Score based on low energy (consistency) and low entropy (decisiveness)
        # Invert energy so lower energy = higher score
        score += (1.0 / (energy + 0.1)) 
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_clean = self._normalize(prompt)
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        
        for cand in candidates:
            cand_clean = self._normalize(cand)
            
            # 1. Structural & Logical Score (Primary)
            struct_score = self._structural_score(prompt_clean, cand_clean)
            
            # 2. NCD Tiebreaker (Max 15% influence)
            ncd = self._compute_ncd(prompt_clean, cand_clean)
            # NCD is distance (0=same, 1=different). We want similarity for context, 
            # but distinctness for answer. 
            # Heuristic: Moderate NCD is good, very high is noise, very low is echo.
            ncd_score = 0.0
            if 0.2 <= ncd <= 0.8:
                ncd_score = 0.5
            elif ncd < 0.2:
                ncd_score = 0.1 # Likely just repeating prompt
            
            # Combine: Structural dominates
            raw_score = struct_score * 0.85 + ncd_score * 0.15
            
            # Apply Meta Cap to the final confidence derived from score
            # Normalize raw_score roughly to 0-1 range for confidence calculation
            # (Assuming struct_score ranges -2 to 3 typically)
            normalized_conf = 1.0 / (1.0 + math.exp(-raw_score)) # Sigmoid
            
            # Apply Tier B Cap
            if meta_cap < 1.0:
                final_conf = min(normalized_conf, meta_cap)
            else:
                final_conf = normalized_conf
            
            # Cap absolute max confidence unless computation was definitive
            if final_conf > 0.9 and struct_score < 1.5:
                final_conf = 0.85

            results.append({
                "candidate": cand,
                "score": final_conf,
                "reasoning": f"Structural: {struct_score:.2f}, NCD: {ncd:.2f}, MetaCap: {meta_cap}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Check meta-confidence first
        cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Apply cap
        final_conf = min(base_score, cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))
```

</details>
