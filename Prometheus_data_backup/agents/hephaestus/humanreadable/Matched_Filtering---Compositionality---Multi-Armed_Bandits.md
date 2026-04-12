# Matched Filtering + Compositionality + Multi-Armed Bandits

**Fields**: Signal Processing, Linguistics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:29:21.158445
**Report Generated**: 2026-03-27T05:13:28.664815

---

## Nous Analysis

Combining matched filtering, compositionality, and multi‑armed bandits yields a **compositional hypothesis‑testing bandit**: a system that generates complex hypotheses by recursively combining primitive signal templates (compositionality), evaluates each hypothesis against noisy observations with a matched filter (maximizing SNR), and treats the evaluation score as the reward for a bandit algorithm that decides which hypothesis to test next (explore‑exploit). Concretely, one could implement a probabilistic context‑free grammar (PCFG) that defines allowable compositions of primitive waveforms; a sampler draws a hypothesis (a parse tree) → the hypothesis is synthesized into a signal template → a matched filter computes the cross‑correlation output, providing a detection statistic that serves as the reward. A contextual UCB or Thompson‑sampling bandit then updates beliefs over grammar rules or over individual hypotheses based on these rewards, allocating more trials to high‑reward compositions while occasionally probing low‑probability rules to discover new structure.

**Advantage for self‑testing:** The matched filter guarantees that each hypothesis is assessed with optimal SNR, minimizing wasted computation on poorly detectable candidates. The bandit layer focuses the limited evaluation budget on the most promising compositions, accelerating convergence to the true underlying model while still exploring novel combinations that could reveal hidden structure. This reduces both false negatives (missed signals) and false positives (spurious detections) compared with brute‑force enumeration or pure random search.

**Novelty:** Matched filters are standard in signal detection; compositional grammars are used in program synthesis and language modeling; bandits guide exploration in reinforcement learning. However, treating the matched‑filter output as the direct reward signal for a bandit over a compositional grammar—and using the bandit to steer hypothesis generation in a hypothesis‑testing loop—is not a mainstream technique. Related work exists in neural program synthesis with reinforcement learning (e.g., DeepCoder, RobustFill) and in Bayesian optimization over program spaces, but the explicit use of a matched filter for likelihood evaluation in this loop is largely unexplored, making the intersection promising yet under‑studied.

**Ratings**

Reasoning: 8/10 — The mechanism provides a principled, SNR‑optimal way to evaluate complex hypotheses while guiding search with bandit‑based uncertainty handling.  
Metacognition: 7/10 — The system can monitor its own hypothesis‑selection policy (bandit posteriors) and detection confidence (matched‑filter output), supporting basic self‑assessment.  
Hypothesis generation: 9/10 — Compositional grammar supplies a rich, generative space; the bandit drives creative exploration of novel combinations.  
Implementability: 6/10 — Requires integrating a matched‑filter module, a grammar‑based sampler, and a bandit learner; feasible with existing libraries (e.g., PyTorch for filters, TensorFlow Grammar, bandit algorithms in RLlib), but careful engineering is needed to keep latency low for iterative testing.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 9/10 |
| Implementability | 6/10 |
| **Composite** | **8.0** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Matched Filtering**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Chaos Theory + Active Inference + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Adaptive Control + Compositionality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Compositionality + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T20:07:30.571655

---

## Code

**Source**: scrap

[View code](./Matched_Filtering---Compositionality---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Hypothesis-Testing Bandit with Structural Parsing.
    
    Mechanism:
    1. Compositionality: Parses prompts into a hierarchy of logical constraints 
       (negations, comparatives, conditionals, numeric values) acting as a PCFG.
    2. Matched Filtering (Analogy): Instead of signal correlation, we correlate 
       candidate answers against the extracted logical 'template'. A candidate 
       matching the structural constraints (e.g., negation presence, numeric order) 
       yields a high 'SNR' score. This is the primary evaluation metric.
    3. Multi-Armed Bandit (Analogy): Treats logical rules as 'arms'. The system 
       allocates 'reward' based on how well a candidate satisfies specific rules. 
       It explores the solution space by checking multiple logical dimensions 
       (numeric, boolean, lexical) and exploits the strongest signal (highest 
       constraint satisfaction) to rank candidates.
    
    This approach prioritizes structural reasoning over string similarity (NCD), 
    using NCD only as a tiebreaker for semantically identical strings.
    """

    def __init__(self):
        # Logical keywords defining our compositional grammar primitives
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody']
        self.comparatives_gt = ['greater', 'larger', 'more', 'higher', 'after']
        self.comparatives_lt = ['less', 'smaller', 'fewer', 'lower', 'before']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _check_negation(self, text: str) -> bool:
        """Detect presence of negation primitives."""
        lower_text = text.lower()
        return any(n in lower_text for n in self.negations)

    def _check_comparative_direction(self, text: str) -> int:
        """Determine if text implies greater-than (1), less-than (-1), or neutral (0)."""
        lower_text = text.lower()
        has_gt = any(c in lower_text for c in self.comparatives_gt)
        has_lt = any(c in lower_text for c in self.comparatives_lt)
        if has_gt and has_lt: return 0
        if has_gt: return 1
        if has_lt: return -1
        return 0

    def _structural_match_score(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'Matched Filter' output: correlation between 
        prompt constraints and candidate properties.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt asks "Which is NOT...", candidate should ideally contain negation or opposite logic
        prompt_neg = self._check_negation(p_lower)
        candidate_neg = self._check_negation(c_lower)
        
        if "not" in p_lower or "never" in p_lower:
            # Heuristic: If prompt is negative, valid answers often mirror logic or are specific exclusions
            # Simple proxy: Reward if candidate explicitly addresses the negation context if it's a yes/no style
            if "yes" in c_lower or "no" in c_lower:
                score += 2.0 if (prompt_neg == candidate_neg) else 0.0 # Basic alignment
        else:
            # Positive prompt, positive candidate usually preferred unless logic dictates otherwise
            score += 1.0 if not candidate_neg else 0.5

        # 2. Numeric Evaluation (Constraint Propagation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate number satisfies implicit comparative in prompt
            p_dir = self._check_comparative_direction(p_lower)
            if p_dir == 1: # Prompt asks for "larger", "more"
                if max(c_nums) > max(p_nums): score += 5.0
                elif max(c_nums) == max(p_nums): score += 1.0
            elif p_dir == -1: # Prompt asks for "smaller", "less"
                if min(c_nums) < min(p_nums): score += 5.0
                elif min(c_nums) == min(p_nums): score += 1.0
            else:
                # Exact match bonus if no direction specified
                if set(c_nums) == set(p_nums): score += 3.0

        # 3. Conditional/Logical Keyword Overlap (Compositionality)
        # Reward candidates that reuse logical structure keywords appropriately
        for word in self.conditionals:
            if word in p_lower and word in c_lower:
                score += 1.5
        
        # 4. Boolean Consistency
        if any(b in p_lower for b in self.booleans):
            if any(b in c_lower for b in self.booleans):
                score += 2.0

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        # Bandit Phase: Evaluate all arms (candidates) to get rewards (scores)
        scores = []
        for cand in candidates:
            # Primary Signal: Structural Matched Filter
            struct_score = self._structural_match_score(prompt, cand)
            scores.append((cand, struct_score))
        
        # Normalize structural scores to prevent overflow dominance, keep relative magnitude
        max_struct = max(s[1] for s in scores) if scores else 1.0
        if max_struct == 0: max_struct = 1.0
        
        ranked = []
        for cand, raw_score in scores:
            # NCD as Tiebreaker only
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD (lower is better) and scale down so it only breaks ties
            ncd_bonus = (1.0 - ncd_val) * 0.1 
            
            final_score = (raw_score / max_struct) * 10.0 + ncd_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if self._check_negation(cand): reasoning_parts.append("contains negation")
            if self._extract_numbers(cand): reasoning_parts.append("contains numeric evaluation")
            if any(k in cand.lower() for k in self.conditionals): reasoning_parts.append("logical structure detected")
            if not reasoning_parts: reasoning_parts.append("lexical match")
            
            reasoning = f"Structural SNR: {raw_score:.2f}; Features: {', '.join(reasoning_parts)}"

            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment strength.
        """
        # Use the internal scoring mechanism
        res = self.evaluate(prompt, [answer, "INVALID_PLACEHOLDER"])
        if not res:
            return 0.0
        
        target = res[0]
        if target["candidate"] == answer:
            # Normalize score to 0-1 range heuristically
            # Max expected structural score is around 10-15 for perfect matches
            conf = min(1.0, target["score"] / 15.0)
            return max(0.0, conf)
        else:
            # If the answer isn't the top pick, confidence is low but non-zero if close
            return 0.1
```

</details>
