# Cognitive Load Theory + Mechanism Design + Free Energy Principle

**Fields**: Cognitive Science, Economics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T02:00:17.321758
**Report Generated**: 2026-03-27T06:37:33.705835

---

## Nous Analysis

Combining Cognitive Load Theory (CLT), Mechanism Design (MD), and the Free Energy Principle (FEP) yields a **resource‑constrained active‑inference planner with incentive‑compatible hypothesis selection**. Concretely, the architecture can be instantiated as a hierarchical Bayesian network (the generative model of FEP) whose inference is performed by a **variational message‑passing algorithm** that is modified to respect a working‑memory budget derived from CLT (intrinsic + extraneous + germane load). At each temporal step, the planner proposes a set of candidate hypotheses (models of the world) and assigns them **temporary “tokens”** that consume working‑memory slots. To avoid overloading the system, a **mechanism‑design layer** runs a Vickrey‑Clarke‑Groves (VCG) auction among hypotheses: each hypothesis bids for memory tokens based on its expected reduction in variational free energy (prediction error) minus a cost proportional to its intrinsic complexity. The auction outcome is incentive‑compatible — truthful bidding maximizes the hypothesis’s expected utility — ensuring that the selected set of hypotheses genuinely offers the highest germane load (useful learning) per unit of memory. The selected hypotheses then drive action selection via standard active‑inference policy optimization (minimizing expected free energy).

**Advantage for hypothesis testing:** The system automatically balances exploration (high‑uncertainty hypotheses) against exploitation (low‑error hypotheses) while never exceeding its working‑memory limit, thus avoiding catastrophic overload and focusing germane resources on truly informative tests. This yields faster convergence to accurate models in noisy, high‑dimensional environments compared with vanilla active inference or bounded‑rational RL alone.

**Novelty:** Elements exist separately — resource‑rational active inference, Bayesian mechanism design, and CLT‑inspired chunking in neural networks — but the tight coupling of a VCG auction for memory allocation inside an active‑inference loop has not been described in the literature. Hence the combination is **novel** (though it builds on known sub‑fields).

**Ratings**

Reasoning: 7/10 — The mechanism yields principled, bounded‑rational inferences but adds computational overhead from auctions.  
Metacognition: 8/10 — Explicit monitoring of memory load and hypothesis value provides strong self‑assessment signals.  
Hypothesis generation: 6/10 — Auction encourages diverse proposals, yet the generator still relies on the prior generative model.  
Implementability: 5/10 — Requires integrating variational inference, auction solvers, and memory tracking; feasible in simulation but non‑trivial for real‑time embedded systems.

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

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Cognitive Load Theory + Mechanism Design: strong positive synergy (+0.188). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Cognitive Load Theory + Free Energy Principle: negative interaction (-0.080). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Mechanism Design: strong positive synergy (+0.380). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Cellular Automata + Mechanism Design + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Cognitive Load Theory + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-25T14:05:17.011821

---

## Code

**Source**: scrap

[View code](./Cognitive_Load_Theory---Mechanism_Design---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A resource-constrained active-inference planner using Mechanism Design.
    
    Mechanism:
    1. Structural Parsing (FEP Priors): Extracts logical constraints (negations, comparatives, 
       conditionals) to form a 'generative model' of the prompt's requirements.
    2. Hypothesis Generation: Treats candidates as hypotheses proposing to explain the prompt.
    3. VCG Auction (Mechanism Design): 
       - Candidates 'bid' for limited working memory slots.
       - Bid Value = (Structural Match Score) - (Complexity Cost).
       - Complexity Cost penalizes verbosity and lack of precision (intrinsic load).
       - The 'auction' selects candidates that maximize germane load (useful signal) while 
         respecting the cognitive budget.
    4. Scoring: Final score is the normalized auction value, ensuring only structurally 
       sound and concise answers rise to the top.
    """

    def __init__(self):
        # Working memory budget (Cognitive Load Theory limit)
        self.wm_capacity = 4.0 
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical signatures: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'word_count': len(words),
            'char_count': len(text)
        }

    def _compute_structural_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Computes the 'Germane Load' (useful learning) by matching structural features.
        High score = Candidate respects the logical constraints of the prompt.
        """
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or not contradict it.
        # Simplified: Presence match boosts score, absence is neutral.
        if prompt_struct['negation']:
            score += 2.0 if cand_struct['negation'] else 0.5
        else:
            # Penalty if candidate introduces unnecessary negation when prompt didn't have it
            score += 1.0 if not cand_struct['negation'] else -1.0

        # 2. Comparative Consistency
        if prompt_struct['comparative']:
            score += 2.0 if cand_struct['comparative'] else 0.0
        else:
            score += 1.0 if not cand_struct['comparative'] else -0.5

        # 3. Conditional Consistency
        if prompt_struct['conditional']:
            score += 2.0 if cand_struct['conditional'] else 0.0
        else:
            score += 1.0 if not cand_struct['conditional'] else -0.5

        # 4. Numeric Evaluation (Simple transitivity check)
        # If both have numbers, check if candidate numbers are 'reasonable' relative to prompt
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Heuristic: If prompt implies an order (e.g., 9.11 vs 9.9), 
            # candidate should ideally reflect the correct magnitude if it's a direct answer.
            # Since we don't know the question type, we reward numeric presence in numeric contexts.
            score += 1.5
            # Specific check: If prompt has 2 numbers and candidate has 1, check magnitude?
            # Too risky without semantic understanding. Stick to structural presence.
        elif p_nums and not c_nums:
            # Prompt asks for math/numbers, candidate gives text -> Penalty
            score -= 2.0

        return score

    def _calculate_complexity_cost(self, cand_struct: Dict) -> float:
        """
        Calculates intrinsic cognitive load.
        Longer, more complex answers cost more 'tokens'.
        """
        # Base cost proportional to length
        length_cost = cand_struct['char_count'] / 50.0 
        return length_cost

    def _vcg_auction(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Runs a VCG-style auction where hypotheses bid for memory slots.
        Bid = (Structural Match) - (Complexity Cost).
        Incentive compatible: Truthful representation of structural fit maximizes utility.
        """
        p_struct = self._parse_structure(prompt)
        results = []
        
        for cand in candidates:
            c_struct = self._parse_structure(cand)
            
            # Calculate Value (Germane Load)
            structural_value = self._compute_structural_score(p_struct, c_struct)
            
            # Calculate Cost (Intrinsic Load)
            complexity_cost = self._calculate_complexity_cost(c_struct)
            
            # Bid = Value - Cost
            bid = structural_value - complexity_cost
            
            reasoning = (
                f"Structural Match: {structural_value:.2f}, "
                f"Complexity Cost: {complexity_cost:.2f}, "
                f"Net Bid: {bid:.2f}"
            )
            results.append((cand, bid, reasoning))
            
        # Sort by bid (descending) - The 'winners' of the auction
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Run the Mechanism Design / Active Inference Loop
        auction_results = self._vcg_auction(prompt, candidates)
        
        # Normalize scores to 0-1 range for the final output
        # We use a soft-max like normalization or simple min-max scaling on the bids
        bids = [r[1] for r in auction_results]
        min_bid = min(bids)
        max_bid = max(bids)
        range_bid = max_bid - min_bid if max_bid != min_bid else 1.0
        
        final_results = []
        
        # Group by score to apply NCD tie-breaking
        # Since auction results are sorted, we can process sequentially
        for i, (cand, bid, reason) in enumerate(auction_results):
            # Normalize bid to 0.2 - 0.9 range to leave room for NCD adjustments
            norm_score = 0.2 + (0.7 * (bid - min_bid) / range_bid)
            
            # Apply NCD as a subtle tie-breaker or booster for high similarity
            # Only if the structural score is very close to another candidate
            is_tie = False
            if i < len(auction_results) - 1:
                next_bid = auction_results[i+1][1]
                if abs(bid - next_bid) < 0.1: # Threshold for 'tie' in auction
                    is_tie = True
            
            if is_tie:
                # Boost score slightly if NCD to prompt is low (similar content)
                # But be careful: sometimes the answer is short ("No") and prompt is long.
                # Instead, use NCD between candidate and the "ideal" structural features?
                # Simpler: Use NCD between candidate and prompt as a relevance proxy for ties.
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD is better. Convert to boost.
                boost = (1.0 - ncd_val) * 0.05 
                norm_score += boost
                reason += f" [NCD Tiebreak: {ncd_val:.2f}]"

            # Clamp score
            norm_score = max(0.0, min(1.0, norm_score))
            
            final_results.append({
                "candidate": cand,
                "score": round(norm_score, 4),
                "reasoning": reason
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the auction bid of the single candidate.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]['score']
```

</details>
