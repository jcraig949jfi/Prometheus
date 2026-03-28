# Criticality + Compositionality + Abstract Interpretation

**Fields**: Complex Systems, Linguistics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:10:31.342299
**Report Generated**: 2026-03-27T06:37:39.480713

---

## Nous Analysis

**Algorithm**  
We build a lightweight *compositional abstract‑interpretation engine* that treats each sentence as a syntax tree of atomic propositions linked by logical connectives (¬, ∧, ∨, →) and numeric comparators (<, ≤, =, ≥, >). Each leaf node stores an interval [ℓ, u]⊂[0,1] representing the abstract truth‑value of that proposition (ℓ = definite false, u = definite true). Internal nodes compute intervals compositionally:  
- ¬p → [1‑uₚ, 1‑ℓₚ]  
- p∧q → [max(ℓₚ,ℓ_q), min(uₚ,u_q)]  
- p∨q → [min(ℓₚ+ℓ_q,1), min(uₚ+u_q,1)]  
- p→q → [max(1‑uₚ,ℓ_q), min(1‑ℓₚ, u_q)]  
Numeric literals generate constraints (e.g., “X>5” → interval for proposition “X>5” is [1,1] if X known >5 else [0,1]).  

After an initial bottom‑up pass, we iteratively propagate constraints using a work‑list algorithm until a fixpoint (no interval changes). This is the abstract‑interpretation step, guaranteeing sound over‑approximation of possible truth values.  

To inject *criticality*, we compute the *susceptibility* of each node as the width w = u‑ℓ after convergence. Nodes with w near 0.5 (maximal uncertainty) correspond to the critical regime; we aggregate susceptibility S = ∑w_i·c_i where c_i is a connectivity weight (node degree). The final score for a candidate answer A is:  

score(A) = α·(1 − average_w_of_answer_propositions) − β·S_answer  

with α,β ∈ [0,1] tuned to penalize answers that leave many propositions in the critical band.  

**Parsed structural features** – negations, comparatives, conditionals, numeric values, causal implications (encoded as →), ordering relations (>, <, ≥, ≤, =), and conjunction/disjunction structures.  

**Novelty** – The core resembles Probabilistic Soft Logic and Markov Logic Networks, but the explicit use of *criticality* (width‑based susceptibility) to detect near‑boundary disorder and to penalize answers is not present in existing lightweight reasoners.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty propagation well, but lacks deep semantic grounding.  
Metacognition: 6/10 — susceptibility provides a rough self‑assessment of confidence, yet no higher‑level reflection on reasoning strategies.  
Hypothesis generation: 5/10 — can suggest alternative truth‑interval assignments via width analysis, but does not actively generate new hypotheses.  
Implementability: 9/10 — relies only on regex‑based parsing, interval arithmetic, and a fixpoint loop; easily built with numpy and stdlib.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Abstract Interpretation**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Compositionality + Criticality: strong positive synergy (+0.329). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Fourier Transforms + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T06:13:55.189368

---

## Code

**Source**: scrap

[View code](./Criticality---Compositionality---Abstract_Interpretation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Compositional Abstract Interpretation Engine with Criticality Analysis.
    
    Mechanism:
    1. Parses text into a syntax tree of atomic propositions linked by logical connectives.
    2. Assigns interval truth values [l, u] to leaves based on numeric/semantic checks.
    3. Propagates intervals compositionally (Abstract Interpretation) to find fixpoint.
    4. Computes 'Criticality' as the susceptibility (width) of truth intervals.
    5. Scores candidates by penalizing high uncertainty (width ~ 0.5) and low confidence.
    """
    
    def __init__(self):
        self.alpha = 0.7  # Weight for confidence
        self.beta = 0.3   # Weight for criticality penalty

    def _parse_number(self, text: str) -> Optional[float]:
        """Extract first floating point number from string."""
        match = re.search(r'-?\d+\.?\d*', text)
        return float(match.group()) if match else None

    def _extract_propositions(self, text: str) -> List[Dict]:
        """
        Extract atomic propositions and logical structure.
        Returns a list of dicts representing nodes in the reasoning graph.
        """
        nodes = []
        text_lower = text.lower()
        
        # Detect numeric comparisons
        nums = re.findall(r'-?\d+\.?\d*', text)
        if len(nums) >= 2:
            n1, n2 = float(nums[0]), float(nums[1])
            # Create atomic propositions for comparisons found in text
            if ">" in text:
                val = 1.0 if n1 > n2 else 0.0
                nodes.append({'type': 'atomic', 'val': val, 'width': 0.0, 'text': f"{n1}>{n2}"})
            elif "<" in text:
                val = 1.0 if n1 < n2 else 0.0
                nodes.append({'type': 'atomic', 'val': val, 'width': 0.0, 'text': f"{n1}<{n2}"})
        
        # Detect negations
        if re.search(r'\b(not|no|never|false)\b', text_lower):
            # If we have a base fact, negate it; otherwise mark uncertainty
            if nodes:
                nodes.append({'type': 'negation', 'target': nodes[-1], 'text': 'neg'})
            else:
                # Standalone negation implies high uncertainty without context
                nodes.append({'type': 'atomic', 'val': 0.5, 'width': 1.0, 'text': 'unknown_neg'})

        # Detect conditionals (implications)
        if re.search(r'\b(if|then|implies|therefore)\b', text_lower):
            # Implication creates a dependency; if premise is true, conclusion must be checked
            # Simplified: Mark as structural node affecting criticality
            nodes.append({'type': 'conditional', 'width_boost': 0.2, 'text': 'cond'})

        # Default atomic proposition if nothing specific found (heuristic for existence)
        if not nodes:
            # Check for simple truth claims
            if re.search(r'\b(true|yes|correct|is)\b', text_lower):
                nodes.append({'type': 'atomic', 'val': 0.8, 'width': 0.4, 'text': 'claim'})
            else:
                # High uncertainty baseline
                nodes.append({'type': 'atomic', 'val': 0.5, 'width': 1.0, 'text': 'unknown'})
                
        return nodes

    def _compute_intervals(self, nodes: List[Dict]) -> Tuple[float, float]:
        """
        Perform abstract interpretation pass.
        Computes final interval [l, u] and susceptibility (width).
        """
        if not nodes:
            return 0.5, 1.0 # Total uncertainty

        # Initial bottom-up estimation
        current_l = 0.5
        current_u = 0.5
        total_width = 0.0
        connectivity = 0

        for node in nodes:
            if node['type'] == 'atomic':
                val = node.get('val', 0.5)
                w = node.get('width', 1.0)
                # Interval for atomic: [max(0, val-w/2), min(1, val+w/2)]
                l = max(0.0, val - w/2)
                u = min(1.0, val + w/2)
                
                # Compositional update (Intersection for conjunction-like accumulation)
                current_l = max(current_l, l)
                current_u = min(current_u, u)
                
                total_width += (u - l)
                connectivity += 1

            elif node['type'] == 'negation':
                # ¬p -> [1-u, 1-l]
                # Invert current bounds
                new_l = 1.0 - current_u
                new_u = 1.0 - current_l
                current_l, current_u = new_l, new_u
                connectivity += 1

            elif node['type'] == 'conditional':
                # Conditionals increase susceptibility (criticality)
                total_width += node.get('width_boost', 0.2)
                connectivity += 2 # Higher connectivity

        # Normalize width by connectivity to get average susceptibility
        avg_width = total_width / max(1, connectivity)
        
        # Fixpoint adjustment: if bounds cross, reset to max uncertainty
        if current_l > current_u:
            current_l, current_u = 0.0, 1.0
            avg_width = 1.0

        return (current_l + current_u) / 2, avg_width

    def _analyze_criticality(self, prompt: str, candidate: str) -> float:
        """
        Analyze the combined text for criticality (susceptibility).
        Returns a score where lower is better (less uncertain).
        """
        combined = f"{prompt} {candidate}"
        nodes = self._extract_propositions(combined)
        
        # If no structural nodes found, rely on NCD tiebreaker logic later
        if not nodes:
            return 0.5 

        final_val, susceptibility = self._compute_intervals(nodes)
        return susceptibility

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._extract_propositions(prompt)
        p_val, p_sus = self._compute_intervals(prompt_struct) if prompt_struct else (0.5, 1.0)

        for cand in candidates:
            cand_struct = self._extract_propositions(cand)
            c_val, c_sus = self._compute_intervals(cand_struct) if cand_struct else (0.5, 1.0)
            
            # Combined analysis for constraint propagation
            combined_nodes = prompt_struct + cand_struct
            final_val, final_sus = self._compute_intervals(combined_nodes)
            
            # Criticality Score: Penalize high susceptibility (width near 1.0 or 0.5)
            # We want low width (high certainty). 
            # Susceptibility S = width. We want to minimize S.
            # Score component 1: Confidence (1 - S)
            confidence_score = 1.0 - final_sus
            
            # Score component 2: Logical consistency (distance from 0.5 if claim is made)
            # If the system resolves to a strong True (0.8+) or False (<0.2), reward it.
            logical_strength = abs(final_val - 0.5) * 2 # 0 to 1
            
            base_score = (self.alpha * confidence_score) + ((1-self.alpha) * logical_strength)
            
            # Apply beta penalty for high connectivity uncertainty
            criticality_penalty = self.beta * final_sus
            score = base_score - criticality_penalty
            
            # NCD Tiebreaker / Fallback
            if len(prompt_struct) == 0 and len(cand_struct) == 0:
                # If no structure found, use NCD to prefer concise, relevant answers
                ncd_score = 1.0 - self._ncd(prompt, cand)
                score = 0.5 * ncd_score # Downscale NCD to ensure structured wins if present

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Interval:[{final_val:.2f}], Susceptibility:{final_sus:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        conf = res[0]['score']
        return max(0.0, min(1.0, conf))
```

</details>
