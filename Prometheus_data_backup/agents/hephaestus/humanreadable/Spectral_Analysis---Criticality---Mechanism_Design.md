# Spectral Analysis + Criticality + Mechanism Design

**Fields**: Signal Processing, Complex Systems, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T20:04:34.119194
**Report Generated**: 2026-03-27T23:28:38.241718

---

## Nous Analysis

The algorithm builds a weighted directed graph from the logical structure of each candidate answer and scores it by combining a spectral‑gap measure (criticality) with a penalty for violated incentive‑compatibility constraints (mechanism design).

**Data structures**  
- `stmt_list`: list of parsed atomic propositions (strings).  
- `rel_dict`: {(i,j): w} where i→j is a directed edge extracted from the text; w∈{+1,−1} indicates support (+1) or contradiction (−1).  
- `A`: numpy adjacency matrix (|stmt|×|stmt|) built from `rel_dict`.  
- `D`: degree matrix (diagonal of row sums of |A|).  
- `L = I − D^{-1/2} A D^{-1/2}`: normalized Laplacian (symmetric).  
- `penalty_vec`: numpy array of length |stmt|, each entry = 1 if the statement asserts a self‑interested claim without justification, else 0 (derived from simple pattern matching for “I want”, “I prefer”, “maximize my”).  

**Operations**  
1. **Parsing** – Apply a fixed set of regexes to extract: negations (`not`, `no`), comparatives (`more than`, `less than`, `>`, `<`), conditionals (`if … then`, `unless`), causal claims (`because`, `leads to`, `results in`), numeric values, and ordering relations (`greater than`, `rank`, `first`, `last`). Each match creates a directed edge with weight +1; a match that also contains a negation flips the weight to −1.  
2. **Graph construction** – Fill `A` with the edge weights.  
3. **Spectral criticality** – Compute eigenvalues of `L` with `np.linalg.eigvalsh`. The spectral gap γ = λ₂ (second smallest eigenvalue). Small γ indicates the statement set is near a critical point (high susceptibility to inconsistency).  
4. **Mechanism‑design penalty** – Compute p = np.mean(penalty_vec).  
5. **Score** – `score = −γ + α·p`, where α∈[0,1] balances criticality versus incentive compatibility (chosen a priori, e.g., 0.5). Lower scores denote better reasoning (small gap, low penalty). The final value is normalized to [0,1] for comparison across answers.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, numeric values, and ordering relations (including transitive chains like “A > B > C”).

**Novelty**  
Spectral graph methods have been used for text similarity and community detection, and criticality concepts appear in dynamical‑systems analyses of language, but coupling the spectral gap with an explicit incentive‑compatibility penalty to evaluate reasoning answers is not present in the literature; thus the combination is novel.

Reasoning: 7/10 — captures logical consistency via spectral gap but misses deeper semantic nuance.  
Metacognition: 5/10 — no explicit self‑monitoring or reflection on the reasoning process.  
Hypothesis generation: 6/10 — can generate alternative graphs by flipping edge weights, but hypothesis space is limited to edge‑level changes.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and standard containers; straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Spectral Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Spectral Analysis: strong positive synergy (+0.401). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Mechanism Design + Spectral Analysis: strong positive synergy (+0.181). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Criticality + Mechanism Design: strong positive synergy (+0.232). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Criticality + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Spectral Analysis + Criticality (accuracy: 0%, calibration: 0%)
- Reinforcement Learning + Spectral Analysis + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=42% cal=4% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T18:39:32.761609

---

## Code

**Source**: scrap

[View code](./Spectral_Analysis---Criticality---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Spectral Analysis, Criticality, and Mechanism Design.
    
    Mechanism:
    1. Structural Parsing: Extracts logical relations (support/contradiction) via regex to build
       a directed graph of statements.
    2. Spectral Criticality: Computes the normalized Laplacian of the graph. The spectral gap
       (lambda_2) measures connectivity/consistency. A small gap indicates fragility (criticality).
    3. Mechanism Design Penalty: Detects self-interested claims ("I want", "maximize my") lacking
       justification, applying a penalty to the score.
    4. Scoring: Combines spectral gap and penalty. Lower raw score = better reasoning.
    5. Epistemic Honesty: Meta-analyzes the prompt for ambiguity/traps to cap confidence.
    """

    def __init__(self):
        self.alpha = 0.5  # Balance between criticality and mechanism penalty
        self.regex_patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|results in|causes)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after|next|previous|rank)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'self_interest': re.compile(r'\b(I want|I prefer|my goal|maximize my|benefit me|I gain)\b', re.IGNORECASE)
        }

    def _parse_statements(self, text: str) -> List[str]:
        """Split text into atomic propositions based on delimiters."""
        # Simple split by sentence endings or conjunctions for atomicity
        raw = re.split(r'[.;!?]', text)
        return [s.strip() for s in raw if s.strip()]

    def _extract_relations(self, stmts: List[str]) -> Dict[Tuple[int, int], int]:
        """Build edge list (i, j, weight) based on logical flow and negations."""
        relations = {}
        n = len(stmts)
        if n == 0:
            return relations

        for i, stmt in enumerate(stmts):
            has_neg = bool(self.regex_patterns['negation'].search(stmt))
            has_comp = bool(self.regex_patterns['comparative'].search(stmt))
            has_causal = bool(self.regex_patterns['causal'].search(stmt))
            has_cond = bool(self.regex_patterns['conditional'].search(stmt))
            has_ord = bool(self.regex_patterns['ordering'].search(stmt))
            
            # Determine edge weight based on content
            # Default support (+1), flip if negation present in a specific logical context
            base_weight = 1
            if has_neg and (has_comp or has_causal):
                base_weight = -1
            
            # Connect to next statement (sequential logic) or self-loop for strong claims
            if i < n - 1:
                # If current statement has causal/conditional, it strongly points to next
                if has_causal or has_cond:
                    relations[(i, i+1)] = base_weight
                # If comparative/ordering, implies relation to context (simplified to next)
                elif has_comp or has_ord:
                    relations[(i, i+1)] = base_weight
                else:
                    # Weak support by proximity
                    relations[(i, i+1)] = 1
            
            # Self-loops for strong assertions (increases degree, affects spectral props)
            if has_causal or has_cond:
                relations[(i, i)] = 1

        return relations

    def _build_matrices(self, stmts: List[str], rel_dict: Dict[Tuple[int, int], int]) -> Tuple[np.ndarray, np.ndarray]:
        """Construct Adjacency (A) and Degree (D) matrices."""
        n = len(stmts)
        if n == 0:
            return np.array([[0]]), np.array([[0]])
        
        A = np.zeros((n, n))
        for (i, j), w in rel_dict.items():
            if 0 <= i < n and 0 <= j < n:
                A[i, j] = w
        
        # D is diagonal of row sums of |A|
        row_sums = np.sum(np.abs(A), axis=1)
        D = np.diag(row_sums)
        return A, D

    def _compute_spectral_gap(self, A: np.ndarray, D: np.ndarray) -> float:
        """Compute lambda_2 of the normalized Laplacian."""
        n = A.shape[0]
        if n < 2:
            return 0.0
        
        # Avoid division by zero
        d_inv_sqrt = np.zeros_like(D)
        diag_vals = np.diag(D)
        for i in range(n):
            if diag_vals[i] > 0:
                d_inv_sqrt[i, i] = 1.0 / np.sqrt(diag_vals[i])
        
        # L = I - D^-1/2 A D^-1/2
        L = np.eye(n) - d_inv_sqrt @ A @ d_inv_sqrt
        
        # Ensure symmetry for eigvalsh
        L = (L + L.T) / 2
        
        try:
            eigenvalues = np.linalg.eigvalsh(L)
            # Sort ascending
            eigenvalues = np.sort(eigenvalues)
            # Lambda_2 is the second smallest (index 1)
            gamma = float(eigenvalues[1]) if n > 1 else 0.0
            return max(0.0, gamma) # Ensure non-negative
        except Exception:
            return 0.0

    def _compute_mechanism_penalty(self, stmts: List[str]) -> float:
        """Calculate mean penalty for unjustified self-interest."""
        if not stmts:
            return 0.0
        penalties = []
        for stmt in stmts:
            if self.regex_patterns['self_interest'].search(stmt):
                # Check for justification keywords nearby (simplified)
                if not re.search(r'\b(because|since|due to|reason)\b', stmt, re.IGNORECASE):
                    penalties.append(1.0)
                else:
                    penalties.append(0.2) # Reduced penalty if justified
            else:
                penalties.append(0.0)
        return float(np.mean(penalties))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ["have you stopped", "why did", "why does", "when did", "who is the liar"]
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                return 0.2
        
        # 2. Scope/Pronoun ambiguity
        ambiguity_triggers = ["every x", "he told", "she told", "they said", "who is", "which one"]
        for trigger in ambiguity_triggers:
            if trigger in p_lower:
                # Only flag if question asks for resolution
                if "?" in prompt:
                    return 0.3
        
        # 3. False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) or re.search(r'\bis it .+ or .+\?', p_lower):
            if "other" not in p_lower and "both" not in p_lower:
                return 0.3

        # 4. Subjectivity without criteria
        subjective_triggers = ["best", "worst", "favorite", "most beautiful"]
        for trigger in subjective_triggers:
            if trigger in p_lower and "calculate" not in p_lower and "logic" not in p_lower:
                return 0.4

        return 1.0  # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_stmts = self._parse_statements(prompt)
        
        # Baseline NCD for tie-breaking
        ncd_scores = []
        if candidates:
            avg_candidate = " ".join(candidates[:3]) # Use first few as reference
            ncd_scores = [self._ncd_distance(prompt, c) for c in candidates]

        for idx, candidate in enumerate(candidates):
            # 1. Structural Parsing & Graph Construction
            stmts = self._parse_statements(candidate)
            # Combine prompt and candidate for context-aware graph (optional, but here we focus on candidate logic)
            # To capture prompt-candidate consistency, we could prepend prompt statements, 
            # but the spec says "graph from logical structure of each candidate answer".
            # We will assume the candidate must stand on its own logical merit or consistent with prompt structure.
            # Let's parse candidate primarily.
            
            rel_dict = self._extract_relations(stmts)
            A, D = self._build_matrices(stmts, rel_dict)
            
            # 2. Spectral Criticality
            gamma = self._compute_spectral_gap(A, D)
            
            # 3. Mechanism Design Penalty
            penalty = self._compute_mechanism_penalty(stmts)
            
            # 4. Scoring
            # Score = -gamma + alpha * penalty
            # Lower is better. 
            # If gamma is small (fragmented/inconsistent), score increases (bad).
            # If penalty is high (selfish), score increases (bad).
            raw_score = -gamma + (self.alpha * penalty)
            
            # Add NCD component (max 15% influence as per instructions)
            # We want high similarity to prompt logic, so low NCD is good.
            # But NCD is a tiebreaker. 
            ncd_component = 0.0
            if idx < len(ncd_scores):
                ncd_component = 0.15 * ncd_scores[idx] # Penalty for dissimilarity
            
            final_raw = raw_score + ncd_component
            
            # Normalize to [0, 1] roughly (assuming gamma in [0,2] and penalty in [0,1])
            # Transform so higher is better for the final output
            # Raw score range approx: -2 (good) to 1 (bad). 
            # Let's invert: Score = 1.0 - (normalized_raw)
            normalized_score = 1.0 / (1.0 + np.exp(final_raw * 2)) # Sigmoid mapping
            
            results.append({
                "candidate": candidate,
                "score": float(normalized_score),
                "reasoning": f"Spectral Gap: {gamma:.4f}, Mechanism Penalty: {penalty:.4f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural signal strength
        stmts = self._parse_statements(answer)
        if not stmts:
            return 0.1
            
        rel_dict = self._extract_relations(stmts)
        structural_density = len(rel_dict) / (len(stmts) + 1e-6)
        
        # If no structural relations found, low confidence
        if structural_density < 0.1:
            base_conf = 0.2
        else:
            # Base confidence derived from structural richness
            base_conf = min(0.95, 0.5 + structural_density * 0.4)
        
        # Apply cap
        final_conf = min(base_conf, cap)
        
        # Never return > 0.9 unless computation was definitive (hard to verify generically, so strict cap)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
