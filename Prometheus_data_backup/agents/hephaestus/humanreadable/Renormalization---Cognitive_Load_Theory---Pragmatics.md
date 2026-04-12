# Renormalization + Cognitive Load Theory + Pragmatics

**Fields**: Physics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T05:49:50.202028
**Report Generated**: 2026-03-27T06:37:35.359218

---

## Nous Analysis

Combining renormalization, Cognitive Load Theory, and pragmatics yields a **hierarchical, load‑aware hypothesis‑testing engine** that operates in three coupled layers:

1. **Renormalization‑style coarse‑graining module** – a stack of abstraction operators (e.g., hierarchical variational autoencoders or wavelet‑based pooling) that map a fine‑grained hypothesis space \(H_0\) to progressively coarser representations \(H_1, H_2, …\). Each level corresponds to a fixed point of the renormalization group, preserving universal features while discarding scale‑specific noise.

2. **Cognitive‑load controller** – a working‑memory buffer with a fixed capacity \(C\) (mirroring the 4‑±1 chunk limit). Intrinsic load is measured by the entropy of the current hypothesis representation; extraneous load is estimated from irrelevant pragmatic cues; germane load is the residual capacity allocated to hypothesis refinement. The controller dynamically selects the coarsest level \(H_k\) whose representation fits within \(C\), triggering chunking (e.g., grouping symbols into higher‑order tokens) when needed.

3. **Pragmatic filter** – a Grice‑maxim evaluator implemented as a lightweight reinforcement‑learning module that scores each hypothesis for relevance, truthfulness, informativeness, and clarity given the current discourse context. Hypotheses violating maxims are penalized, effectively increasing extraneous load and prompting the load controller to shift to a coarser scale or discard the hypothesis.

**Advantage for self‑testing:** The system can automatically zoom out to a tractable hypothesis when working memory threatens overload, while the pragmatic filter ensures that the retained hypotheses are contextually appropriate and informative. This reduces wasted computation on irrelevant detail and focuses germane resources on meaningful refinement, yielding faster convergence and more reliable self‑validation.

**Novelty:** Hierarchical Bayesian models and Rational Speech Acts treat pragmatics and multi‑scale inference, and architectures like ACT‑R or Neural Programmer‑Interpreters embed limited working memory. However, an explicit renormalization‑group‑style coarse‑graining loop coupled with a quantitative cognitive‑load budget and a Grice‑maxim‑based filter has not been instantiated as a unified algorithm. Thus the combination is largely uncharted.

**Rating**

Reasoning: 8/10 — provides principled multi‑scale hypothesis evaluation that adapts to complexity.  
Metacognition: 7/10 — adds explicit load monitoring but relies on heuristic load estimates.  
Hypothesis generation: 7/10 — prunes implausible candidates efficiently, though generation still depends on underlying proposer.  
Implementability: 5/10 — requires integrating coarse‑graining nets, a working‑memory controller, and a pragmatic RL module; non‑trivial engineering and tuning are needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 5/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Renormalization**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Cognitive Load Theory + Renormalization: strong positive synergy (+0.448). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Pragmatics + Renormalization: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Cognitive Load Theory + Pragmatics: strong positive synergy (+0.267). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Chaos Theory + Renormalization + Cognitive Load Theory (accuracy: 0%, calibration: 0%)
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Topology + Renormalization + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=27% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T09:16:32.669921

---

## Code

**Source**: scrap

[View code](./Renormalization---Cognitive_Load_Theory---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hierarchical, load-aware hypothesis tester combining:
    1. Renormalization: Coarse-graining text to universal structural tokens.
    2. Cognitive Load: Penalizing hypotheses that exceed complexity budgets relative to the prompt.
    3. Pragmatics: Scoring based on Gricean maxims (Relevance, Clarity, Truthfulness via logic).
    
    Strategy:
    - Structural parsing (negations, comparatives, numerics) forms the primary signal.
    - NCD is used only as a tie-breaker for structural equivalence.
    - 'Renormalization' is implemented as recursive token abstraction.
    - 'Cognitive Load' limits the depth of comparison to high-salience chunks.
    - 'Pragmatics' filters candidates that fail logical consistency or relevance checks.
    """

    def __init__(self):
        # Gricean weights
        self.w_relevance = 0.4
        self.w_clarity = 0.3
        self.w_truth = 0.3
        
        # Cognitive load capacity (arbitrary units of complexity)
        self.max_load = 50.0 

    def _coarse_grain(self, text: str) -> List[str]:
        """
        Renormalization step: Map fine-grained text to coarse structural tokens.
        Preserves logic operators, numbers, and negations; discards noise.
        """
        if not text:
            return []
        
        t = text.lower()
        tokens = []
        
        # Extract numeric values for magnitude comparison
        nums = re.findall(r'-?\d+\.?\d*', t)
        for n in nums:
            tokens.append(f"<NUM:{n}>")
            
        # Extract logical operators
        if re.search(r'\b(not|no|never|neither)\b', t):
            tokens.append("<OP:NEG>")
        if re.search(r'\b(if|then|unless|provided)\b', t):
            tokens.append("<OP:COND>")
        if re.search(r'\b(and|both|plus)\b', t):
            tokens.append("<OP:AND>")
        if re.search(r'\b(or|either)\b', t):
            tokens.append("<OP:OR>")
        if re.search(r'\b(more|less|greater|smaller|larger|fewer|better|worst)\b', t):
            tokens.append("<OP:COMP>")
        if re.search(r'\b(equal|same|identical)\b', t):
            tokens.append("<OP:EQ>")
            
        # If no structural tokens, keep raw length as a coarse feature
        if not tokens:
            tokens.append(f"<LEN:{len(text.split())}>")
            
        return tokens

    def _calculate_load(self, prompt: str, candidate: str) -> float:
        """
        Cognitive Load Controller:
        Estimates intrinsic load via entropy of coarse-grained representation.
        Extraneous load estimated by noise ratio.
        """
        p_tokens = self._coarse_grain(prompt)
        c_tokens = self._coarse_grain(candidate)
        
        # Intrinsic load: complexity of the candidate's structure
        intrinsic = len(c_tokens) * 2.0 + len(candidate) * 0.05
        
        # Extraneous load: mismatch in structural density (noise)
        # If candidate has way more tokens than prompt, it's likely hallucinated noise
        extraneous = max(0, (len(c_tokens) - len(p_tokens)) * 3.0)
        
        return intrinsic + extraneous

    def _pragmatic_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Pragmatic Filter (Gricean Maxims):
        1. Relevance: Overlap of structural tokens.
        2. Clarity: Simplicity (inverse of load).
        3. Truthfulness: Logical consistency (heuristic: negation matching).
        """
        p_struct = set(self._coarse_grain(prompt))
        c_struct = set(self._coarse_grain(candidate))
        
        # Relevance: Jaccard similarity of structural tokens
        if not p_struct and not c_struct:
            relevance = 0.5 # Neutral if no structure
        else:
            intersection = p_struct.intersection(c_struct)
            union = p_struct.union(c_struct)
            relevance = len(intersection) / len(union) if union else 0.0
            
        # Clarity: Penalize excessive length relative to prompt
        load = self._calculate_load(prompt, candidate)
        clarity = 1.0 / (1.0 + math.exp((load - self.max_load) / 10.0)) # Sigmoid penalty
        
        # Truthfulness heuristic: 
        # If prompt has negation and candidate lacks it (or vice versa) in a short answer, penalize?
        # Instead, we check if candidate contradicts prompt structure explicitly
        truth_penalty = 0.0
        p_neg = "<OP:NEG>" in p_struct
        c_neg = "<OP:NEG>" in c_struct
        
        # Simple contradiction detection for short answers
        if len(candidate.split()) < 5:
            if p_neg != c_neg and ("<OP:COMP>" in p_struct or "<OP:COND>" in p_struct):
                # Potential contradiction in logic flow
                truth_penalty = 0.2

        score = (self.w_relevance * relevance) + (self.w_clarity * clarity) - truth_penalty
        reason = f"Rel:{relevance:.2f}, Clr:{clarity:.2f}, Load:{load:.1f}"
        return score, reason

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._coarse_grain(prompt)
        prompt_load = self._calculate_load(prompt, prompt) # Baseline load

        for cand in candidates:
            # 1. Pragmatic Score (Primary Signal)
            prag_score, prag_reason = self._pragmatic_score(prompt, cand)
            
            # 2. Structural Parsing Bonus (Explicit checks)
            struct_bonus = 0.0
            
            # Numeric evaluation
            p_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', prompt.lower())]
            c_nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', cand.lower())]
            
            if p_nums and c_nums:
                # Check if candidate preserves numeric magnitude order if comparatives exist
                if "<OP:COMP>" in prompt_struct:
                    # Rough heuristic: if prompt compares, candidate should likely reflect numbers
                    struct_bonus += 0.1 if len(c_nums) > 0 else -0.2
            
            # Negation check
            if "<OP:NEG>" in prompt_struct:
                if "<OP:NEG>" in self._coarse_grain(cand):
                    struct_bonus += 0.15 # Reinforces matching negation
            
            # 3. Cognitive Load Check
            cand_load = self._calculate_load(prompt, cand)
            load_penalty = 0.0
            if cand_load > self.max_load * 1.5:
                load_penalty = 0.2 # Heavy penalty for overload

            # 4. NCD Tiebreaker (Only if structural signals are weak)
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_bonus = 0.0
            if abs(prag_score) < 0.1: # If pragmatic signal is noise
                ncd_bonus = (1.0 - ncd_val) * 0.1 # Low weight
            
            final_score = prag_score + struct_bonus + ncd_bonus - load_penalty
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"{prag_reason}; StructBonus:{struct_bonus:.2f}; NCD:{ncd_val:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score normalized."""
        # Evaluate single candidate against itself to get relative score
        # We simulate a dummy competitor to get a range, but simpler:
        # Use the internal scoring mechanism directly
        prag_score, _ = self._pragmatic_score(prompt, answer)
        load = self._calculate_load(prompt, answer)
        
        # Normalize pragmatic score (theoretically -0.2 to 1.0 range roughly)
        # Map to 0-1
        conf = (prag_score + 0.5) / 1.5 
        conf = max(0.0, min(1.0, conf))
        
        # Apply load penalty to confidence
        if load > self.max_load:
            conf *= 0.5
            
        return float(conf)
```

</details>
