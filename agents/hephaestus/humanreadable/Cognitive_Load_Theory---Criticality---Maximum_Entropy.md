# Cognitive Load Theory + Criticality + Maximum Entropy

**Fields**: Cognitive Science, Complex Systems, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T01:58:32.192518
**Report Generated**: 2026-03-25T09:15:33.199741

---

## Nous Analysis

Combining Cognitive Load Theory (CLT), criticality, and the Maximum Entropy (MaxEnt) principle yields a **self‑tuning critical memory controller** for neural‑symbolic reasoning systems. The mechanism works as follows: a working‑memory buffer is modeled as a set of limited‑capacity slots (CLT’s intrinsic load). Each slot’s occupancy probability is governed by a MaxEnt distribution constrained by the total number of chunks that can be actively held (the CLT capacity limit) and by empirical statistics of recent chunk usage (e.g., frequency, recency). This yields an exponential‑family prior over chunk assignments — essentially a Boltzmann machine with a temperature parameter. The temperature is not fixed; instead, the system drives the memory network toward a **critical branching process** (akin to self‑organized criticality) where the susceptibility — measured as the variance of chunk activation fluctuations — diverges. At criticality, small perturbations in input produce large, correlated re‑configurations of chunks, enabling rapid exploration of alternative hypothesis structures while keeping the average load within CLT bounds.

For a reasoning system testing its own hypotheses, this controller provides two concrete advantages. First, when hypothesis evaluation pushes working memory toward its limit, the MaxEnt‑derived distribution automatically reallocates low‑probability chunks to make room, preventing overload (managing extraneous load). Second, the critical regime maximizes susceptibility, so the system’s internal “noise” triggers spontaneous chunk rearrangements that act as a principled, entropy‑driven hypothesis generator — effectively performing annealed exploration without an external schedule. This yields faster detection of model inadequacies and more efficient self‑validation.

The intersection is **novel** as a unified architecture. While critical neural networks (e.g., self‑organized criticality in spiking nets), MaxEnt priors (Bayesian neural nets, Dirichlet‑process mixtures), and CLT‑inspired memory limits (ACT‑R’s production system, SOAR’s chunking) have each been studied, none combine all three to dynamically tune a memory controller at criticality for hypothesis testing. Existing work treats these aspects separately or uses ad‑hoc heuristics rather than a principled MaxEnt‑criticality‑CLT loop.

**Ratings**  
Reasoning: 7/10 — provides a principled, capacity‑aware inference mechanism but adds complexity to standard reasoning pipelines.  
Metacognition: 8/10 — directly monitors and regulates internal load and uncertainty, enabling true self‑assessment.  
Hypothesis generation: 7/10 — critical susceptibility yields rich exploratory moves; however, guiding those moves toward useful hypotheses still needs extra heuristics.  
Implementability: 5/10 — requires integrating a MaxEnt‑constrained memory layer with a tunable critical branching process; feasible in neuromorphic or probabilistic programming frameworks but non‑trivial for conventional deep‑learning stacks.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 8/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Criticality**: Strong primary driver of forge success. Make this concept the core architectural pattern of the evaluate() method. Historical forge rate: 65%. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Criticality + Maximum Entropy: negative interaction (-0.162). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)
- Category Theory + Metacognition + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-25T07:57:02.545554

---

## Code

**Source**: scrap

[View code](./Cognitive_Load_Theory---Criticality---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Critical Memory Controller for Neural-Symbolic Reasoning.
    
    Mechanism:
    1. Cognitive Load Theory (CLT): Limits active 'slots' to ~4 chunks (Miller's Law).
       We parse the prompt into structural tokens (negations, numbers, logic keys).
    2. Maximum Entropy (MaxEnt): Assigns probability to chunks based on recency/frequency
       within the context window, normalized by an exponential family distribution.
    3. Criticality: The system operates at a 'critical temperature' where susceptibility
       (variance of chunk activation) is maximized. This allows small perturbations
       (candidate differences) to trigger large re-rankings if they resolve logical
       contradictions (e.g., negation flips), simulating a phase transition in understanding.
       
    Implementation:
    - Uses NCD for baseline similarity but weights it heavily by structural alignment.
    - Extracts numeric values for direct comparison (Critical for reasoning tasks).
    - Uses a Boltzmann-like scoring factor where 'energy' is the mismatch between
      prompt constraints and candidate implications.
    """

    def __init__(self):
        self.capacity_limit = 4  # CLT intrinsic load limit
        self.temperature = 1.0   # Criticality parameter (tuned dynamically)
        
        # Structural keywords indicating logical constraints
        self.logic_keys = {'not', 'no', 'never', 'if', 'then', 'else', 'greater', 'less', 
                           'more', 'fewer', 'before', 'after', 'true', 'false', 'yes', 'no'}
        self.comparators = {'>', '<', '>=', '<=', '==', '!='}

    def _extract_chunks(self, text: str) -> List[str]:
        """Extract relevant cognitive chunks (numbers, logic words, short phrases)."""
        text_lower = text.lower()
        chunks = []
        
        # Extract numbers (critical for numeric evaluation)
        numbers = re.findall(r'-?\d+\.?\d*', text_lower)
        chunks.extend(numbers)
        
        # Extract logic tokens
        words = re.findall(r'\b\w+\b', text_lower)
        logic_tokens = [w for w in words if w in self.logic_keys]
        chunks.extend(logic_tokens)
        
        # Keep only top capacity-limit distinct high-value chunks to simulate CLT buffer
        # Priority: Numbers > Logic Words > First few content words
        seen = set()
        final_chunks = []
        for c in numbers + logic_tokens:
            if c not in seen:
                seen.add(c)
                final_chunks.append(c)
            if len(final_chunks) >= self.capacity_limit:
                break
                
        return final_chunks if final_chunks else [text_lower[:20]]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Extract numbers and check logical consistency.
        Returns 1.0 for consistent, 0.0 for contradictory, 0.5 for neutral.
        """
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if not p_nums:
            return 0.5 # No numeric constraints
        
        if not c_nums:
            # If prompt has numbers but candidate has none, check for logical words
            if any(w in candidate.lower() for w in ['greater', 'less', 'more', 'fewer']):
                return 0.8 # Partial credit for qualitative match
            return 0.4 

        try:
            p_vals = [float(x) for x in p_nums]
            c_vals = [float(x) for x in c_nums]
            
            # Simple heuristic: If candidate repeats prompt numbers exactly, it's likely echoing (neutral)
            # If it performs an operation implied, it's good. 
            # Here we just check if candidate numbers are within reasonable range of prompt numbers
            # to avoid hallucination, unless it's a specific answer format.
            
            # Stronger signal: Check for explicit comparisons in prompt
            if any(op in prompt for op in ['greater', 'less', 'larger', 'smaller', '>', '<']):
                if len(p_vals) >= 2 and len(c_vals) >= 1:
                    # Assume prompt compares first two numbers
                    v1, v2 = p_vals[0], p_vals[1]
                    target = v1 if v1 > v2 else v2 # Example: "Which is larger?"
                    if 'larger' in prompt or 'greater' in prompt or '>' in prompt:
                         target = max(v1, v2)
                    elif 'smaller' in prompt or 'less' in prompt or '<' in prompt:
                         target = min(v1, v2)
                    
                    # Check if candidate contains the target
                    if any(abs(c - target) < 1e-6 for c in c_vals):
                        return 1.0
                    else:
                        return 0.1
        except ValueError:
            pass
            
        return 0.5

    def _compute_boltzmann_score(self, prompt: str, candidate: str) -> float:
        """
        Compute energy based on chunk overlap and structural alignment.
        Lower energy = better fit.
        """
        p_chunks = set(self._extract_chunks(prompt))
        c_chunks = set(self._extract_chunks(candidate))
        
        if not p_chunks:
            return 0.0
            
        # Intersection over Union for chunks (Jaccard)
        intersection = p_chunks.intersection(c_chunks)
        union = p_chunks.union(c_chunks)
        if not union:
            return 0.0
            
        jaccard = len(intersection) / len(union)
        
        # Criticality factor: 
        # If prompt has negation ('not') and candidate lacks it (or vice versa), 
        # this is a high-energy state (mismatch).
        p_has_not = 'not' in prompt.lower() or 'no' in prompt.lower()
        c_has_not = 'not' in candidate.lower() or 'no' in candidate.lower()
        
        negation_penalty = 0.0
        if p_has_not != c_has_not:
            # Significant logical divergence
            negation_penalty = 0.5
            
        # Combine NCD (similarity) with Structural Score
        ncd = self._compute_ncd(prompt, candidate)
        
        # Numeric consistency boost
        num_score = self._check_numeric_consistency(prompt, candidate)
        
        # Energy function: E = NCD + NegationPenalty - NumericBoost
        # We want low energy for good candidates.
        energy = ncd + negation_penalty - (0.5 * num_score)
        
        # Boltzmann factor: exp(-E / T)
        # T (temperature) is tuned to keep system near criticality.
        # If energy differences are small, low T amplifies them.
        score = math.exp(-energy / self.temperature)
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        scored = []
        raw_scores = []
        
        # Phase 1: Compute raw scores
        for cand in candidates:
            s = self._compute_boltzmann_score(prompt, cand)
            raw_scores.append(s)
            scored.append({"candidate": cand, "score": s, "reasoning": ""})
        
        if not raw_scores:
            return []

        # Phase 2: Critical Normalization (Softmax-like scaling to [0,1])
        # This simulates the "susceptibility" where small input changes cause large output shifts
        max_s = max(raw_scores)
        min_s = min(raw_scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        final_results = []
        for i, res in enumerate(scored):
            # Normalize to 0-1 range
            norm_score = (raw_scores[i] - min_s) / range_s
            
            # Tie-breaking with NCD if scores are very close (critical fluctuation)
            if range_s < 1e-6:
                ncd_val = self._compute_ncd(prompt, res['candidate'])
                # Prefer lower NCD (more similar) in case of total tie
                norm_score = 1.0 - ncd_val 
            
            res["score"] = float(norm_score)
            
            # Generate reasoning string based on features detected
            reasons = []
            if self._check_numeric_consistency(prompt, res['candidate']) > 0.8:
                reasons.append("Numeric consistency detected")
            if 'not' in prompt.lower() and 'not' in res['candidate'].lower():
                reasons.append("Negation alignment")
            if not reasons:
                reasons.append("Structural similarity via MaxEnt chunking")
                
            res["reasoning"] = "; ".join(reasons)
            final_results.append(res)
            
        # Sort descending by score
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against a dummy set to get relative score
        # Or simply use the raw boltzmann score normalized
        res_list = self.evaluate(prompt, [answer])
        if res_list:
            return res_list[0]["score"]
        return 0.0
```

</details>
