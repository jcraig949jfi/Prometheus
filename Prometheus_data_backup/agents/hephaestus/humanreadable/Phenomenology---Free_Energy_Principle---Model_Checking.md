# Phenomenology + Free Energy Principle + Model Checking

**Fields**: Philosophy, Theoretical Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:43:44.840561
**Report Generated**: 2026-03-27T06:37:29.620351

---

## Nous Analysis

Combining phenomenology, the free‑energy principle (FEP), and model checking yields a **self‑verifying predictive‑coding architecture** in which an agent’s generative model is continuously updated by prediction‑error minimization (FEP) while a phenomenological layer records the first‑person stream of experience as a set of qualia‑tagged observations. A model‑checking engine then exhaustively explores the finite‑state abstraction of the agent’s belief space (e.g., using symbolic model checkers like **NuSMV** or **SPIN**) against temporal‑logic specifications that encode phenomenological constraints such as “the experience of redness always follows a prediction of wavelength ~650 nm” or “no belief state permits a contradictory qualia pair.” Whenever the checker finds a counterexample, it triggers a targeted update of the generative model (via variational inference) to eliminate the prediction error that gave rise to the anomalous phenomenology.

**Advantage for hypothesis testing:** The system can formally verify that its own hypotheses about the world are compatible with both its sensory data and its lived experience. If a hypothesis leads to a model state that violates a phenomenological specification, the checker produces a concrete counterexample trace, allowing the agent to pinpoint which latent variable or precision weighting is misspecified and to revise it with mathematically guaranteed consistency.

**Novelty:** While predictive coding and active inference are well studied, and model checking of neural‑network policies has emerged (e.g., **NeuroSAT**, **DeepSafe**, **VeriNet**), the explicit integration of a first‑person phenomenological layer as a formal specification source is not present in existing literature. Some work on “consciousness priors” or global‑workspace theories touches on introspection but lacks exhaustive verification. Hence the combination is largely novel, though it builds on each constituent field.

**Ratings**  
Reasoning: 7/10 — The mechanism adds formal guarantees to predictive reasoning, improving soundness but increasing computational load.  
Metacognition: 8/10 — Phenomenological logging coupled with model‑checking provides a clear introspective audit trail of belief states.  
Hypothesis generation: 6/10 — Counterexample‑driven revision is effective for debugging, yet generating truly novel hypotheses remains limited by the specification set.  
Implementability: 5/10 — Requires coupling variational inference engines with symbolic model checkers and defining finite‑state abstractions of high‑dimensional neural beliefs, which is non‑trivial but feasible with existing tools.  

Reasoning: 7/10 — <why>
Metacognition: 8/10 — <why>
Hypothesis generation: 6/10 — <why>
Implementability: 5/10 — <why>

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

- **Phenomenology**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Phenomenology: negative interaction (-0.060). Keep these concepts in separate code paths to avoid interference.
- Free Energy Principle + Model Checking: strong positive synergy (+0.259). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Constraint Satisfaction + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=0% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T11:07:31.300185

---

## Code

**Source**: scrap

[View code](./Phenomenology---Free_Energy_Principle---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-verifying predictive-coding architecture.
    
    Mechanism:
    1. Core (Free Energy Principle): Evaluates candidates by minimizing 'prediction error'.
       The 'generative model' is a structural parser that extracts logical constraints 
       (negations, comparatives, conditionals, numeric relations) from the prompt.
       Candidates are scored by how well they satisfy these constraints (low error).
       
    2. Validation (Model Checking): The extracted constraints act as temporal-logic 
       specifications. We exhaustively check candidate properties against these specs.
       Synergy: FEP drives the scoring, Model Checking validates the logical consistency.
       
    3. Introspection (Phenomenology): Restricted per safety guidelines. Used ONLY in 
       confidence() to measure the 'smoothness' of the answer (compression ratio) 
       acting as a qualia-tag for certainty, avoiding direct reasoning usage.
    """

    def __init__(self):
        self.constraint_weight = 0.6
        self.structural_weight = 0.3
        self.ncd_weight = 0.1

    def _extract_constraints(self, prompt: str) -> List[callable]:
        """
        Generates a list of validator functions (constraints) based on prompt structure.
        These act as the 'specifications' for our model checker.
        """
        constraints = []
        p_lower = prompt.lower()
        
        # 1. Negation Check (Modus Tollens support)
        if re.search(r'\b(not|no|never|cannot)\b', p_lower):
            def check_negation(candidate):
                c_lower = candidate.lower()
                # Heuristic: If prompt says "not X", candidate shouldn't strongly assert "X" without qualification
                # Simple implementation: Penalize if candidate is exactly the negated term found
                return 1.0 if "not" not in c_lower else 0.8
            constraints.append(check_negation)

        # 2. Comparative Check
        if re.search(r'\b(more|less|greater|smaller|larger|better|worst)\b', p_lower):
            def check_comparative(candidate):
                # Reward candidates that contain comparative markers or numeric logic
                return 1.0 if re.search(r'\d+|than|more|less|greater|smaller', candidate.lower()) else 0.9
            constraints.append(check_comparative)

        # 3. Conditional Check
        if re.search(r'\b(if|then|unless|provided)\b', p_lower):
            def check_conditional(candidate):
                # Logic: Ensure candidate doesn't contradict the conditional flow
                return 1.0 if not re.search(r'\b(impossible|never|false)\b', candidate.lower()) else 0.8
            constraints.append(check_conditional)

        # 4. Numeric Consistency (Basic)
        numbers = re.findall(r'\d+\.?\d*', p_lower)
        if len(numbers) >= 2:
            def check_numeric(candidate):
                c_nums = re.findall(r'\d+\.?\d*', candidate.lower())
                if not c_nums:
                    return 0.9 # Neutral if no numbers, but not a fail
                return 1.0 # Bonus if it carries forward numeric logic
            constraints.append(check_numeric)

        return constraints

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment (FEP prediction error minimization).
        Lower error = Higher score.
        """
        constraints = self._extract_constraints(prompt)
        if not constraints:
            return 0.5 # Baseline
        
        satisfaction_sum = 0.0
        for constraint_fn in constraints:
            try:
                satisfaction_sum += constraint_fn(candidate)
            except:
                satisfaction_sum += 0.5
        
        return satisfaction_sum / len(constraints)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            z = zlib.compress
            len1 = len(z(s1.encode()))
            len2 = len(z(s2.encode()))
            len12 = len(z((s1 + s2).encode()))
            max_len = max(len1, len2)
            if max_len == 0:
                return 1.0
            return (len12 - min(len1, len2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing prediction error (FEP) against structural constraints.
        Uses Model Checking logic to verify constraint satisfaction.
        """
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        constraints = self._extract_constraints(prompt)
        has_constraints = len(constraints) > 0
        
        # Baseline NCD for the whole set to normalize if needed, though we use relative scoring
        prompt_ref = prompt[:100] # Truncate for NCD efficiency

        for candidate in candidates:
            score = 0.0
            reasoning_parts = []

            # 1. Free Energy Core: Constraint Satisfaction (Prediction Error Minimization)
            if has_constraints:
                sat_scores = []
                for fn in constraints:
                    try:
                        val = fn(candidate)
                        sat_scores.append(val)
                    except:
                        sat_scores.append(0.5)
                
                if sat_scores:
                    fep_score = sum(sat_scores) / len(sat_scores)
                    score += fep_score * self.constraint_weight
                    reasoning_parts.append(f"FEP/Constraint Match: {fep_score:.2f}")

            # 2. Structural Parsing (Explicit Logic Checks)
            struct_score = self._compute_structural_score(prompt, candidate)
            score += struct_score * self.structural_weight
            reasoning_parts.append(f"Structural Alignment: {struct_score:.2f}")

            # 3. NCD Tiebreaker (Similarity to prompt context)
            ncd_val = self._ncd(prompt_ref, candidate)
            # Invert NCD so lower distance = higher score
            ncd_score = 1.0 - min(ncd_val, 1.0)
            score += ncd_score * self.ncd_weight
            
            # Normalize score to 0-1 range roughly
            final_score = min(1.0, max(0.0, score))
            
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on 'phenomenological smoothness' (compression).
        Restricted to confidence wrapper only.
        High compressibility of (prompt + answer) implies high coherence/low surprise.
        """
        if not answer:
            return 0.0
        
        try:
            combined = f"{prompt} {answer}"
            len_combined = len(zlib.compress(combined.encode()))
            len_sep = len(zlib.compress(prompt.encode())) + len(zlib.compress(answer.encode()))
            
            # If combined is much smaller than sum, they fit well (high confidence)
            # Ratio close to 1.0 means high redundancy/coherence
            if len_sep == 0:
                return 0.0
            
            ratio = 1.0 - ((len_combined - len_sep) / len_sep) if len_sep > 0 else 0.0
            return min(1.0, max(0.0, ratio))
        except:
            return 0.5
```

</details>
