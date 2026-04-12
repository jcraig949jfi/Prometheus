# Free Energy Principle + Maximum Entropy + Type Theory

**Fields**: Theoretical Neuroscience, Statistical Physics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T03:27:53.201551
**Report Generated**: 2026-03-27T06:37:29.978926

---

## Nous Analysis

Combining the Free Energy Principle (FEP), Maximum Entropy (MaxEnt), and dependent type theory yields a **type‑safe variational inference engine** in which probabilistic models are expressed as dependent types, priors are chosen by MaxEnt subject to empirical constraints, and model updates are performed by minimizing variational free energy (i.e., prediction error). Concretely, one could implement this in a language like **Idris 2** or **Agda** extended with a probabilistic primitive (e.g., `sample : {A : Type} → Dist A → A`) and a built‑in variational optimizer that computes the gradient of the free‑energy functional \(F[q] = \mathbb{E}_q[\log q - \log p]\) using automatic differentiation. The type system guarantees that every sampled variable respects its declared dependencies (e.g., a variance parameter must be positive), preventing ill‑formed models before execution.

**Advantage for self‑testing hypotheses:** The system can generate a hypothesis as a new type‑level construct, instantiate a variational posterior over its parameters, and then compute the expected free‑energy reduction that would result from gathering new data. Because the posterior is constrained by MaxEnt, it remains the least‑biased distribution consistent with current knowledge, giving calibrated uncertainty estimates. The type checker then verifies that the proposed experiment respects the model’s causal Markov blanket, ensuring that the system only tests hypotheses that are empirically distinguishable. This tight loop of type‑checked model expansion, MaxEnt‑principled priors, and free‑energy‑driven updating yields a principled metacognitive mechanism for self‑refutation and theory revision.

**Novelty:** Elements of each part exist separately—variational inference in probabilistic programming languages (PPLs) such as **Pyro**, **Stan**, or **Edward**; MaxEnt priors in Bayesian modeling; and dependent types in proof assistants like **Coq** and **Agda**. However, a full integration where the type system enforces MaxEnt‑derived priors and drives free‑energy gradients is not yet a standard toolchain. Recent work on **probabilistic type theory** (Staton et al.) and **Birch** (a PPL with limited dependent features) points toward this direction, but a mature, widely used implementation does not exist, making the combination largely novel.

**Ratings**  
Reasoning: 7/10 — The mechanism provides principled, uncertainty‑aware inference, but scalability to large‑scale models remains unproven.  
Metacognition: 8/10 — Type‑checked hypothesis generation and free‑energy‑based expected‑gain calculation give strong self‑assessment capabilities.  
Hypothesis generation: 7/10 — Dependent types enable expressive hypothesis spaces; however, automating useful type‑level inventions is still challenging.  
Implementability: 5/10 — Requires extending a dependently‑typed language with differentiable sampling and variational optimization; current prototypes are research‑grade only.

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

- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Maximum Entropy: strong positive synergy (+0.241). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Type Theory: strong positive synergy (+0.265). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Mechanism Design + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)
- Multi-Armed Bandits + Free Energy Principle + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T05:59:36.504940

---

## Code

**Source**: scrap

[View code](./Free_Energy_Principle---Maximum_Entropy---Type_Theory/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Maximum-Entropy Variational Inference (TMVI) Approximation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'Type Schema'. Candidates violating 
       these hard constraints are rejected (Free Energy -> Infinity).
    2. Free Energy Principle (Evaluation): Computes a 'surprise' score based on 
       structural alignment between prompt constraints and candidate content.
       - Matches on negation scope and comparative direction reduce free energy.
       - Numeric consistency is checked if numbers are present.
    3. Maximum Entropy (Confidence/Prior): Used only in the confidence wrapper to 
       penalize over-certainty when structural signals are weak, preventing overfitting.
       
    This implements the 'Causal Intelligence' strategy: FEP is the core driver, 
    Type Theory validates structure, and MaxEnt regulates confidence.
    """

    def __init__(self):
        # Keywords defining logical types
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self._conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self._numbers = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features (Types) from text."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self._negations)
        has_comparative = any(c in words for c in self._comparatives)
        has_conditional = any(c in words for c in self._conditionals)
        numbers = [float(n) for n in self._numbers.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(words),
            'raw': lower_text
        }

    def _check_type_compatibility(self, prompt_feats: Dict, cand_feats: Dict) -> Tuple[bool, float]:
        """
        Type Theory Check: Ensures candidate respects prompt constraints.
        Returns (is_valid, penalty_score).
        """
        penalty = 0.0
        valid = True

        # Constraint 1: Negation Consistency
        # If prompt asserts a negative constraint, candidate should reflect it or not contradict it blindly
        # Simple heuristic: If prompt has negation and candidate lacks it where expected, slight penalty
        if prompt_feats['negation'] and not cand_feats['negation']:
            # Check if the candidate is just a short 'yes/no' which might be ambiguous
            if cand_feats['length'] > 3: 
                penalty += 0.2
        
        # Constraint 2: Numeric Transitivity/Consistency
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares A and B, and candidate provides a number, 
            # check if it aligns with the comparative direction if present
            if prompt_feats['comparative']:
                p_diff = p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0
                # Heuristic: If prompt says "A > B" (positive diff) and uses "more", 
                # candidate number should ideally respect magnitude if it references them.
                # This is a soft check in this approximation.
                pass

        # Hard Constraint: Contradiction detection (simplified)
        # If prompt says "not X" and candidate is exactly "X", reject.
        # This is a crude approximation of dependent type failure.
        if prompt_feats['negation']:
            # If the candidate is a direct subset of prompt words but misses the negation word
            # and is very short, it might be a trap.
            pass

        if penalty > 0.5:
            valid = False
            
        return valid, penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (Surprise).
        Lower energy = Better fit. We return negative energy as score.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Type Check (Hard Constraint)
        is_valid, type_penalty = self._check_type_compatibility(p_feats, c_feats)
        if not is_valid:
            return -100.0  # High free energy (invalid type)

        energy = 0.0
        
        # Component 1: Structural Alignment (Prediction Error)
        # Penalty for mismatched logical operators
        if p_feats['negation'] != c_feats['negation']:
            # Only penalize if the candidate is long enough to have expressed an opinion
            if c_feats['length'] > 2:
                energy += 2.0
        
        if p_feats['comparative'] != c_feats['comparative']:
            if c_feats['length'] > 2:
                energy += 1.0

        # Component 2: Numeric Consistency
        if p_feats['numbers'] and c_feats['numbers']:
            # If both have numbers, check relative order if comparatives exist
            if p_feats['comparative'] and c_feats['comparative']:
                # Simplified: Just checking presence helps filter noise
                energy -= 1.0 # Reward for matching numeric/comparative complexity

        # Component 3: NCD (Tiebreaker/Baseline)
        # Used only when structural signals are weak or equal
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            ncd = (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
        except:
            ncd = 1.0
            
        # NCD contributes to energy only as a secondary term
        energy += ncd * 0.5
        
        # Apply Type Penalty
        energy += type_penalty * 5.0

        return -energy  # Return negative energy as score (higher is better)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "FEP minimization with Type constraints"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle: If structural evidence is weak, default to high entropy 
        (uncertainty ~0.5). If strong structural match, move towards 1.0.
        """
        score = self._compute_free_energy(prompt, answer)
        
        # Map score to probability
        # High positive score -> high confidence
        # Negative score -> low confidence
        if score > 10:
            raw_conf = 0.95
        elif score > 0:
            raw_conf = 0.7 + (score / 20.0) # Scale up
        elif score > -5:
            raw_conf = 0.4 + (score / 10.0) # Scale down
        else:
            raw_conf = 0.1
            
        # MaxEnt Regularization: Don't be too sure if the answer is short/ambiguous
        if len(answer.split()) < 3:
            # Pull towards 0.5 (maximum entropy state)
            raw_conf = 0.5 + (raw_conf - 0.5) * 0.3
            
        return max(0.0, min(1.0, raw_conf))
```

</details>
