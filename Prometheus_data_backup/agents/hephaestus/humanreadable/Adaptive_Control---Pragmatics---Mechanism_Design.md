# Adaptive Control + Pragmatics + Mechanism Design

**Fields**: Control Theory, Linguistics, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T21:22:49.920751
**Report Generated**: 2026-03-27T18:24:03.184649

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a control system that adjusts its internal weight vector **w** (size = number of constraint types) to minimize the error between the answer’s logical satisfaction and a target satisfaction derived from a reference answer.  

1. **Parsing (Pragmatics + Structural extraction)** – Using only `re`, we extract:  
   - Literals with negation (`not`, `no`)  
   - Conditionals (`if … then …`, `unless`)  
   - Comparatives (`greater than`, `less than`, `>`, `<`)  
   - Numeric values and units  
   - Causal cues (`because`, `leads to`, `results in`)  
   - Ordering quantifiers (`all`, `some`, `none`, `most`)  
   Each extracted element becomes a propositional atom \(p_i\).  

2. **Constraint graph (Mechanism Design)** – Atoms are nodes; directed edges represent logical implications extracted from conditionals and causal cues. We store the adjacency matrix **A** (bool) and compute its transitive closure with a Floyd‑Warshall‑style update using NumPy boolean operations, yielding **T** (implied truths).  

3. **Scoring logic (Adaptive Control)** – For a candidate answer we build a binary vector **x** where \(x_i=1\) if the answer asserts \(p_i\) (or its negation) and 0 otherwise. The satisfied‑constraint score is  
   \[
   s = \frac{w^\top (x \odot T\mathbf{1})}{\|w\|_1}
   \]  
   where \(\odot\) is element‑wise product and \(T\mathbf{1}\) gives the set of atoms entailed by the answer’s assertions.  
   The error \(e = s_{\text{ref}} - s\) (reference score from a gold answer) updates the weights via a simple self‑tuning rule:  
   \[
   w \leftarrow w + \eta \, e \, (x \odot T\mathbf{1})
   \]  
   with learning rate \(\eta\) clamped to \([0,1]\). This is analogous to a model‑reference adaptive controller that drives the tracking error to zero.  

4. **Incentive compatibility (Mechanism Design)** – The final score is passed through a quadratic proper scoring rule \(R = 1 - (s - s_{\text{ref}})^2\), ensuring that reporting the true belief maximizes expected reward, thus making the mechanism incentive‑compatible.  

**Structural features parsed** – negations, conditionals, comparatives, numeric values, causal markers, ordering relations, and quantifiers (all/some/none).  

**Novelty** – While logical constraint propagation and proper scoring rules exist separately, the tight coupling of an adaptive‑control weight update with pragmatic implicature (soft default constraints) and a strictly proper scoring mechanism has not been described in the literature; thus the combination is novel.  

**Ratings**  
Reasoning: 7/10 — captures logical satisfaction and adapts weights, but limited to propositional level.  
Metacognition: 6/10 — weight update reflects self‑monitoring, yet no explicit higher‑order belief modeling.  
Hypothesis generation: 5/10 — generates implied truths via closure, but does not propose new hypotheses beyond entailment.  
Implementability: 8/10 — relies only on regex, NumPy matrix ops, and simple loops; readily achievable in a few hundred lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Adaptive Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Adaptive Control + Pragmatics: strong positive synergy (+0.440). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Adaptive Control + Mechanism Design: strong positive synergy (+0.444). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Mechanism Design + Pragmatics: strong positive synergy (+0.174). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Sparse Coding + Adaptive Control + Pragmatics (accuracy: 0%, calibration: 0%)
- Theory of Mind + Pragmatics + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: non-broadcastable output operand with shape (2,) doesn't match the broadcast shape (2,2,2)

**Forge Timestamp**: 2026-03-27T17:53:58.271357

---

## Code

**Source**: scrap

[View code](./Adaptive_Control---Pragmatics---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Adaptive Control, Pragmatics, and Mechanism Design.
    
    Mechanism:
    1. Pragmatics (Parsing): Extracts logical atoms (negations, conditionals, comparatives, 
       numerics, causal cues, quantifiers) from text using regex.
    2. Mechanism Design (Constraint Graph): Builds an adjacency matrix of implications.
       Computes transitive closure (Floyd-Warshall) to find all entailed truths.
    3. Adaptive Control (Scoring): Treats candidate answers as control systems adjusting 
       weights to minimize error against a reference (gold) satisfaction score.
       Uses a quadratic proper scoring rule for incentive compatibility.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and unanswerability 
       to cap confidence, ensuring the tool admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        # Regex patterns for pragmatic extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|else|provided)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|better|worse)\b|[><]', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|most|every|each|any)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'presupposition': re.compile(r'\b(stopped|quit|failed|regret)\b.*\?\s*$', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every|all)\s+\w+.*\b(a|an)\s+\w+', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(told|said|asked)\b.*\b(he|she|him|her|they)\b.*\?', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|but)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
        }
        self.eta = 0.1  # Learning rate for adaptive control

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract propositional atoms based on pragmatic categories."""
        atoms = []
        text_lower = text.lower()
        
        # Extract specific matches
        for key, pattern in self.patterns.items():
            if key in ['presupposition', 'scope_ambiguity', 'pronoun_ambiguity', 'false_dichotomy', 'subjectivity']:
                continue # These are for meta-confidence, not logic atoms
            matches = pattern.findall(text_lower)
            atoms.extend([f"{key}:{m}" for m in matches])
            
        # Extract numeric comparisons as atoms
        nums = self.patterns['numeric'].findall(text)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                atoms.append(f"numeric_cmp:{n1 < n2}")
            except: pass
            
        return list(set(atoms))

    def _build_constraint_graph(self, text: str, atoms: List[str]) -> np.ndarray:
        """Build adjacency matrix A and compute transitive closure T."""
        n = len(atoms)
        if n == 0:
            return np.array([])
            
        A = np.zeros((n, n), dtype=bool)
        text_lower = text.lower()
        
        # Simple heuristic: if a conditional keyword exists, assume some implication structure
        # In a full system, this would map specific atoms to edges. 
        # Here we simulate structure by linking sequential logical cues if conditionals exist.
        has_conditional = bool(self.patterns['conditional'].search(text_lower))
        
        if has_conditional and n > 1:
            # Chain atoms loosely to simulate dependency if conditionals are present
            for i in range(n - 1):
                # Heuristic: Connect negation/comparative cues to subsequent cues
                if 'negation' in atoms[i] or 'comparative' in atoms[i]:
                    A[i, i+1] = True
        
        # Self-loops for identity
        np.fill_diagonal(A, True)
        
        # Floyd-Warshall for transitive closure
        T = A.copy()
        for k in range(n):
            # T[i, j] = T[i, j] or (T[i, k] and T[k, j])
            T = T | (T[:, k:None, None] & T[None, k:, :]) # Vectorized update
            
        return T

    def _compute_score(self, prompt: str, candidate: str, ref_candidate: Optional[str] = None) -> Tuple[float, float]:
        """
        Compute structural score and adaptive weight update.
        Returns (score, meta_confidence_cap)
        """
        # 1. Parse Prompt and Candidate
        prompt_atoms = self._extract_atoms(prompt)
        cand_atoms = self._extract_atoms(candidate)
        
        # If no structural features found, rely on NCD later
        if not prompt_atoms:
            return 0.5, 1.0

        # 2. Build Constraint Graph from Prompt
        T = self._build_constraint_graph(prompt, prompt_atoms)
        if T.size == 0:
            return 0.5, 1.0

        # 3. Map Candidate atoms to Prompt atoms (Vector x)
        # x[i] = 1 if prompt_atoms[i] is asserted or implied by candidate
        n = len(prompt_atoms)
        x = np.zeros(n, dtype=float)
        
        # Simple matching: if a prompt atom substring appears in candidate, mark as asserted
        for i, p_atom in enumerate(prompt_atoms):
            # Check direct match or logical negation match
            key = p_atom.split(':')[0]
            val = p_atom.split(':')[1]
            
            # Check if candidate contains the specific pattern
            if key in candidate.lower() or val in candidate.lower():
                x[i] = 1.0
            # Handle negation flip
            elif 'not' in candidate.lower() and 'negation' in key:
                x[i] = 0.0 # Explicitly false
                
        # 4. Calculate Entailed Truths (T * x)
        # T is boolean, x is float. Convert T to float for dot product
        entailed = (T @ x) > 0 # Boolean vector of entailed truths
        
        # 5. Adaptive Control Scoring
        # Initialize weights w uniformly
        w = np.ones(n)
        
        # Calculate satisfaction score s
        # s = (w . (x AND entailed)) / sum(w)
        # Note: x AND entailed -> we only count atoms asserted by x that are entailed
        satisfied = np.logical_and(x > 0, entailed)
        s = np.sum(w * satisfied.astype(float)) / np.sum(w)
        
        # Reference score (Self-consistency or Gold)
        # If ref_candidate provided, calculate s_ref. Otherwise assume ideal s_ref = 1.0 for perfect match
        if ref_candidate:
            ref_atoms = self._extract_atoms(ref_candidate)
            x_ref = np.zeros(n, dtype=float)
            for i, p_atom in enumerate(prompt_atoms):
                key = p_atom.split(':')[0]
                val = p_atom.split(':')[1]
                if key in ref_candidate.lower() or val in ref_candidate.lower():
                    x_ref[i] = 1.0
            entailed_ref = (T @ x_ref) > 0
            satisfied_ref = np.logical_and(x_ref > 0, entailed_ref)
            s_ref = np.sum(w * satisfied_ref.astype(float)) / np.sum(w)
        else:
            # Heuristic: Assume high structural overlap implies correctness for s_ref estimation
            s_ref = min(1.0, s + 0.1) if s > 0.5 else s 

        # Weight Update (Adaptive Control)
        error = s_ref - s
        # w <- w + eta * e * (x AND entailed)
        # Only update weights for atoms that were active and satisfied
        update_mask = satisfied.astype(float)
        w += self.eta * error * update_mask
        w = np.clip(w, 0.1, 2.0) # Clamp weights
        
        # Recalculate score with updated weights
        s_final = np.sum(w * satisfied.astype(float)) / np.sum(w)
        
        # 6. Mechanism Design: Proper Scoring Rule
        # R = 1 - (s - s_ref)^2
        score = 1.0 - (s_final - s_ref)**2
        
        return max(0.0, min(1.0, score)), 1.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. Scope ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.3
            
        # 3. Pronoun ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.3
            
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.4
            
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.5
            
        # 6. Unanswerability (Heuristic: very short prompt with no numbers/logic)
        if len(prompt.split()) < 4 and not self.patterns['numeric'].search(p_lower):
            return 0.4

        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Check for structural content in prompt
        prompt_atoms = self._extract_atoms(prompt)
        has_structure = len(prompt_atoms) > 0
        
        # Determine reference (best candidate by initial heuristic or first one)
        # For adaptive control, we need a target. We use the first candidate as a provisional reference
        # or assume the "most structured" one is the reference.
        ref_candidate = candidates[0] if candidates else ""

        for cand in candidates:
            if has_structure:
                score, _ = self._compute_score(prompt, cand, ref_candidate)
                # Blend with NCD only if structure is weak (max 15% NCD influence)
                # But requirement says: Structural >= 50%, Computation >= 20%, NCD <= 15%
                # Our score is structural/computational. 
                final_score = score
            else:
                # Fallback to NCD if no structure found (Tier A failure mode)
                # Compare candidate to prompt (similarity) vs random noise
                ncd = self._ncd_score(prompt, cand)
                # Invert NCD (lower distance = higher score)
                final_score = 1.0 - ncd
            
            # Apply Epistemic Honesty Cap
            if meta_cap < 0.3:
                final_score = min(final_score, 0.3)
            elif meta_cap < 0.6:
                final_score = min(final_score, 0.6)
                
            # Generate reasoning string
            reasoning = f"Structural match: {has_structure}. Meta-cap: {meta_cap:.2f}. "
            if has_structure:
                reasoning += f"Logic satisfaction derived from {len(prompt_atoms)} atoms."
            else:
                reasoning += "Fallback to NCD compression similarity."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate structural score
        prompt_atoms = self._extract_atoms(prompt)
        if not prompt_atoms:
            # No structure, low confidence unless NCD is very high (but we cap for honesty)
            base_conf = 0.5 
        else:
            score, _ = self._compute_score(prompt, answer)
            base_conf = score
            
        # Apply cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 without definitive computation (heuristic check)
        # If we have numeric evaluation, we can be more confident
        has_numeric = bool(self.patterns['numeric'].search(prompt))
        if has_numeric and meta_cap == 1.0:
            return min(0.95, final_conf)
        else:
            return min(0.9, final_conf)
```

</details>
