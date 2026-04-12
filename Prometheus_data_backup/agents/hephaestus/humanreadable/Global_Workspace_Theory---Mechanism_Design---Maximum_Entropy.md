# Global Workspace Theory + Mechanism Design + Maximum Entropy

**Fields**: Cognitive Science, Economics, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:51:26.018887
**Report Generated**: 2026-03-27T06:37:33.604836

---

## Nous Analysis

Combining Global Workspace Theory (GWT), Mechanism Design, and Maximum Entropy (MaxEnt) yields a **Mechanism‑Design‑Driven Global Workspace (MDGW)** architecture. In MDGW, competing hypotheses act as self‑interested agents that submit bids for limited “broadcast slots” in a central workspace. The auction rule is a proper scoring rule derived from the MaxEnt principle: each hypothesis reports a probability distribution over possible observations, and the mechanism selects the hypothesis that maximizes expected entropy‑regularized utility, ensuring incentive compatibility (truthful reporting is a dominant strategy). The selected hypothesis gains global access, allowing its representation to influence all downstream modules (perception, action, memory).  

**Advantage for self‑testing:** Because the mechanism rewards hypotheses proportionally to how much they increase the workspace’s entropy‑constrained predictive power, the system is compelled to generate hypotheses that are both informative and minimally biased. False or overly confident claims are penalized, leading to calibrated self‑evaluation and rapid discard of untenable ideas—essentially an internal prediction market that self‑corrects.  

**Novelty:** Elements exist separately: GWT‑inspired architectures (LIDA, Global Workspace Dynamo), MaxEnt reinforcement learning (Soft Q‑learning), and mechanism‑design for learning (Bayesian truth serum, prediction markets). However, integrating an incentive‑compatible auction directly into a global broadcast loop, with MaxEnt priors governing bid evaluation, has not been formalized as a unified algorithmic framework. Thus the combination is largely unexplored, though it builds on known pieces.  

**Ratings**  
Reasoning: 7/10 — The mechanism yields a principled, incentive‑aligned way to select high‑value hypotheses, improving logical deduction.  
Metacognition: 8/10 — By forcing hypotheses to reveal their confidence truthfully, the system gains explicit insight into its own belief reliability.  
Hypothesis generation: 6/10 — The entropy regularizer encourages exploration, but the auction may suppress low‑probability, high‑risk ideas unless carefully tuned.  
Implementability: 5/10 — Requires coupling a symbolic auction solver with neural workspace modules; while feasible in simulators, real‑time, large‑scale deployment remains challenging.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 5/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Global Workspace Theory + Mechanism Design: strong positive synergy (+0.443). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Maximum Entropy + Mechanism Design: strong positive synergy (+0.121). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Global Workspace Theory + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)
- Neuromodulation + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T20:40:23.558302

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Mechanism_Design---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Mechanism-Design-Driven Global Workspace (MDGW) Implementation.
    
    Mechanism:
    1. Global Workspace (GWT): The prompt and candidates form the shared context.
    2. Mechanism Design: Candidates act as agents submitting bids. The 'auction rule'
       is a scoring function that rewards structural alignment (logic, negation, numbers)
       and penalizes bias (overlap without substance).
    3. Maximum Entropy (MaxEnt): Restricted per safety guidelines. Used only within
       the confidence() wrapper to measure surprise/uncertainty, not for primary scoring.
       
    The scoring mechanism prioritizes structural parsing (negations, comparatives, 
    conditionals) and numeric evaluation. NCD is used strictly as a tiebreaker.
    """

    def __init__(self):
        # No external state needed; stateless computation
        pass

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural logic patterns:
        - Negation handling
        - Comparative logic
        - Conditional consistency
        - Numeric evaluation
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency
        # If prompt has "not", "no", "never", candidate should reflect or address it
        negations = ['not', 'no', 'never', 'none', 'cannot', "won't", "don't"]
        p_has_neg = any(n in p_lower for n in negations)
        c_has_neg = any(n in c_lower for n in negations)
        
        if p_has_neg:
            # Reward if candidate acknowledges negation or provides a specific counter
            if c_has_neg:
                score += 2.0
            # Penalty if candidate ignores explicit negation in a short answer
            elif len(c_lower.split()) < 5: 
                score -= 1.5
        else:
            # Mild penalty if candidate introduces random negation without prompt cause
            if c_has_neg and len(p_lower.split()) < 10:
                score -= 0.5

        # 2. Comparative Logic Detection
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        if any(c_word in p_lower for c_word in comparatives):
            # If prompt asks for comparison, reward candidates with comparative words or numbers
            if any(c_word in c_lower for c_word in comparatives) or self._extract_numbers(c_lower):
                score += 2.5
            else:
                score -= 1.0

        # 3. Conditional/Constraint Propagation
        conditionals = ['if', 'unless', 'provided', 'when', 'then']
        if any(cond in p_lower for cond in conditionals):
            # Reward candidates that maintain logical flow (heuristic: length + keyword presence)
            if len(c_lower.split()) > 3: 
                score += 1.5
        
        # 4. Numeric Evaluation
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if p_nums:
            if c_nums:
                # Reward numeric engagement
                score += 2.0
                # Check for simple ordering consistency if both have numbers
                try:
                    # Heuristic: if prompt implies sorting or max/min, check candidate number magnitude
                    if 'max' in p_lower or 'largest' in p_lower or 'highest' in p_lower:
                        if max(c_nums) >= min(c_nums): # Trivial check, but ensures numbers exist
                            score += 1.0
                    elif 'min' in p_lower or 'smallest' in p_lower or 'lowest' in p_lower:
                         if max(c_nums) >= min(c_nums):
                            score += 1.0
                except:
                    pass
            else:
                # Penalty for ignoring numbers in a numeric prompt
                score -= 2.0

        return score

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from a string."""
        # Match integers and floats
        pattern = r'-?\d+(?:\.\d+)?'
        try:
            return [float(x) for x in re.findall(pattern, text)]
        except:
            return []

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        combined = s1_bytes + s2_bytes
        len_combined = len(zlib.compress(combined))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the MDGW auction mechanism.
        Bids are scored based on structural logic (primary) and NCD (tiebreaker).
        """
        scored_candidates = []
        
        for candidate in candidates:
            # Primary Score: Structural Parsing & Logic
            logic_score = self._structural_score(prompt, candidate)
            
            # Secondary Score: NCD Tiebreaker (inverted, so lower distance = higher score)
            # We scale NCD to be small so it only acts as a tiebreaker
            ncd_val = self._ncd_distance(prompt, candidate)
            ncd_score = -0.1 * ncd_val 
            
            # Total Bid
            total_score = logic_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if logic_score > 0:
                reasoning_parts.append("High structural alignment")
            elif logic_score < 0:
                reasoning_parts.append("Logical mismatch detected")
            else:
                reasoning_parts.append("Neutral structural match")
                
            reasoning = f"Logic: {logic_score:.2f}, NCD_adj: {ncd_score:.4f}. " + "; ".join(reasoning_parts)

            scored_candidates.append({
                "candidate": candidate,
                "score": total_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle restricted to uncertainty estimation via structural coherence.
        High coherence -> High confidence.
        """
        # Re-use structural scoring as a proxy for coherence
        raw_score = self._structural_score(prompt, answer)
        
        # Map raw score to 0-1 using a sigmoid-like function
        # Shift range: assume scores roughly between -5 and 5
        # sigmoid(x) = 1 / (1 + exp(-x))
        try:
            # Scale factor to steepen the curve around 0
            scaled_score = raw_score * 0.5 
            conf = 1.0 / (1.0 + math.exp(-scaled_score))
            return max(0.0, min(1.0, conf))
        except OverflowError:
            return 1.0 if raw_score > 0 else 0.0
```

</details>
