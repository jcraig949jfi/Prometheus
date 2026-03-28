# Theory of Mind + Pragmatism + Maximum Entropy

**Fields**: Cognitive Science, Philosophy, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:12:02.523749
**Report Generated**: 2026-03-27T06:37:29.331356

---

## Nous Analysis

Combining Theory of Mind (ToM), Pragmatism, and Maximum Entropy (MaxEnt) yields a **Meta‑Pragmatic Maximum‑Entropy Theory‑of‑Mind Reasoner (MP‑METOM)**. The architecture consists of three coupled modules:

1. **ToM Inference Core** – a hierarchical variational auto‑encoder (VAE) with recurrent attention that learns a latent distribution over other agents’ beliefs, desires, and intentions (BDI). The encoder produces a *belief state* bₜ; the decoder predicts observable actions. Training uses a MaxEnt prior: the belief distribution is chosen to maximize entropy subject to expected‑feature constraints derived from observed behavior (Jaynes’ principle). This yields an exponential‑family posterior p(b|τ) ∝ exp(λ·ϕ(τ)), where τ is the interaction history and ϕ are sufficient statistics (e.g., frequency of goal‑directed moves).

2. **Pragmatic Utility Layer** – a reinforcement‑learning (RL) critic that assigns a *pragmatic value* U(h) to each hypothesis h about the world. U(h) is the expected cumulative reward of acting on h plus an intrinsic term measuring *workability*: how often h leads to successful predictions in simulated roll‑outs. This mirrors James’ “truth is what works” by turning pragmatic success into a learnable reward signal.

3. **Meta‑Reasoning Controller** – a shallow transformer that monitors the entropy of the ToM belief distribution and the variance of pragmatic values across hypotheses. When entropy drops below a threshold (indicating over‑commitment) or pragmatic variance rises (signal of conflicting workable accounts), the controller triggers a *hypothesis‑generation* step: it samples new constraints ϕ′ from a Dirichlet process and re‑optimizes the MaxEnt belief, effectively expanding the hypothesis space.

**Advantage for self‑testing:** The system can *self‑calibrate* its ToM beliefs by seeking the maximum‑entropy distribution that still satisfies pragmatic success criteria. When a hypothesis fails pragmatically, the MaxEnt update naturally spreads probability mass away from the falsified belief without over‑fitting, yielding a built‑in falsification mechanism that is both conservative (high entropy) and action‑oriented (pragmatic reward).

**Novelty:** While each ingredient appears separately—Bayesian ToM (e.g., Rabinowitz et al., 2018), MaxEnt inverse RL (Ziebart et al., 2008), and pragmatic utility‑based AI (e.g., Dewey‑inspired reinforcement learners)—their tight coupling via an entropy‑constrained belief optimizer guided by a pragmatic critic is not documented in the literature. Thus the intersection is novel, though it builds on well‑studied components.

**Ratings**  
Reasoning: 7/10 — combines principled inference with action‑guided feedback, improving robustness over pure Bayesian ToM.  
Metacognition: 8/10 — explicit monitoring of belief entropy and pragmatic variance gives the system genuine self‑assessment.  
Hypothesis generation: 6/10 — the Dirichlet‑process constraint sampler is functional but may be computationally heavy without further heuristics.  
Implementability: 5/10 — requires integrating VAE‑based ToM, RL critic, and transformer controller; feasible in research prototypes but non‑trivial for real‑time deployment.

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

- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatism**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Pragmatism + Type Theory (accuracy: 0%, calibration: 0%)
- Category Theory + Kolmogorov Complexity + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=33% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T05:45:39.723949

---

## Code

**Source**: scrap

[View code](./Theory_of_Mind---Pragmatism---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import json
import zlib
import math

class ReasoningTool:
    """
    MP-METOM Implementation Strategy:
    Given the constraints against using Pragmatism/MaxEnt for direct scoring, this tool
    implements a 'Structural Causal Parser' that mimics the ToM/Pragmatic flow via:
    1. ToM Core (Structural Parsing): Extracts logical constraints (negations, comparatives,
       conditionals) to form a 'belief state' about the prompt's requirements.
    2. Pragmatic Utility (Constraint Satisfaction): Candidates are scored by how well
       they satisfy these structural constraints (workability).
    3. MaxEnt Controller (Calibration): Uses NCD as a tie-breaking entropy term only when
       structural signals are ambiguous, preventing over-commitment to noisy strings.
    """
    
    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'higher', 'lower'}
        self.conditionals = {'if', 'unless', 'provided', 'when', 'then'}

    def _normalize(self, text):
        return text.lower().strip()

    def _extract_structural_beliefs(self, prompt):
        """ToM Inference Core: Extracts latent logical constraints from the prompt."""
        p_lower = self._normalize(prompt)
        beliefs = {
            'has_negation': False,
            'has_comparative': False,
            'has_conditional': False,
            'needs_number': False,
            'target_value': None,
            'logic_op': None
        }
        
        # Detect Negation
        if any(w in p_lower.split() for w in self.negation_words):
            beliefs['has_negation'] = True
            
        # Detect Comparatives
        if any(w in p_lower for w in self.comparatives):
            beliefs['has_comparative'] = True
            
        # Detect Conditionals
        if any(w in p_lower.split() for w in self.conditionals):
            beliefs['has_conditional'] = True
            
        # Detect Numeric Constraints (Simple extraction)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", p_lower)
        if numbers:
            beliefs['needs_number'] = True
            try:
                beliefs['target_value'] = float(numbers[-1])
            except: pass

        # Detect Logic Keywords
        if 'must' in p_lower or 'required' in p_lower: beliefs['logic_op'] = 'must'
        if 'cannot' in p_lower or 'impossible' in p_lower: beliefs['logic_op'] = 'cannot'
        
        return beliefs

    def _pragmatic_utility_score(self, candidate, beliefs, prompt):
        """Pragmatic Utility Layer: Scores candidate based on 'workability' against beliefs."""
        c_lower = self._normalize(candidate)
        score = 0.0
        checks = 0
        
        # Check 1: Negation Consistency
        has_c_neg = any(w in c_lower.split() for w in self.negation_words)
        if beliefs['has_negation']:
            # If prompt has negation, valid answer often acknowledges it or flips logic
            score += 0.5 if has_c_neg else 0.0
        else:
            score += 0.5 if not has_c_neg else 0.0
        checks += 0.5

        # Check 2: Comparative/Number Logic
        if beliefs['needs_number']:
            # Try to extract number from candidate
            c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", c_lower)
            if c_nums:
                try:
                    c_val = float(c_nums[0])
                    # Heuristic: If prompt asks for "larger", candidate should be large? 
                    # Without full semantic parse, we check if candidate contains A number.
                    score += 1.0 
                except: pass
            else:
                # If prompt needs number but candidate is text-only (e.g. "Yes"), penalize slightly
                if not any(k in c_lower for k in ['yes', 'no', 'true', 'false']):
                    score += 0.2
        checks += 1.0

        # Check 3: Conditional/Logic Op
        if beliefs['logic_op'] == 'must':
            if 'must' in c_lower or 'yes' in c_lower or 'true' in c_lower:
                score += 1.0
        elif beliefs['logic_op'] == 'cannot':
            if 'cannot' in c_lower or 'no' in c_lower or 'false' in c_lower:
                score += 1.0
        checks += 1.0

        # Base relevance (simple overlap to ensure topic match)
        p_words = set(self._normalize(prompt).split())
        c_words = set(c_lower.split())
        overlap = len(p_words & c_words)
        score += min(overlap * 0.1, 1.0)
        checks += 1.0

        return score / checks if checks > 0 else 0.0

    def _max_ent_calibration(self, prompt, candidate, base_score):
        """Meta-Reasoning Controller: Applies NCD only as a tie-breaker/calibrator."""
        # NCD Calculation
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        len_s1 = len(s1)
        len_s2 = len(s2)
        if len_s1 == 0 or len_s2 == 0:
            ncd = 1.0
        else:
            len_combined = len(zlib.compress(s1 + s2))
            max_len = max(len_s1, len_s2)
            if max_len == 0: ncd = 1.0
            else: ncd = (len_combined - min(len_s1, len_s2)) / max_len
        
        # MaxEnt adjustment: If base_score is ambiguous (near 0.5), let NCD influence.
        # If base_score is strong, NCD is ignored (prevents overfitting to string length).
        if 0.4 <= base_score <= 0.6:
            # Invert NCD (lower distance = higher score)
            calibration_bonus = (1.0 - ncd) * 0.1
            return base_score + calibration_bonus
        return base_score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        beliefs = self._extract_structural_beliefs(prompt)
        results = []
        
        for cand in candidates:
            # 1. Pragmatic Utility Score (Primary Signal)
            util_score = self._pragmatic_utility_score(cand, beliefs, prompt)
            
            # 2. MaxEnt Calibration (Secondary Signal)
            final_score = self._max_ent_calibration(prompt, cand, util_score)
            
            # Reasoning trace
            reason_parts = []
            if beliefs['has_negation']: reason_parts.append("negation detected")
            if beliefs['has_comparative']: reason_parts.append("comparative logic")
            if beliefs['needs_number']: reason_parts.append("numeric constraint")
            reason_str = f"Structural checks: {', '.join(reason_parts) if reason_parts else 'none'}. Utility match: {util_score:.2f}."
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment."""
        beliefs = self._extract_structural_beliefs(prompt)
        score = self._pragmatic_utility_score(answer, beliefs, prompt)
        # Normalize to 0-1 strictly
        return min(1.0, max(0.0, score))
```

</details>
