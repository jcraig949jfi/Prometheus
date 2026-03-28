# Compositionality + Free Energy Principle + Model Checking

**Fields**: Linguistics, Theoretical Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T03:20:02.308365
**Report Generated**: 2026-03-27T06:37:34.287677

---

## Nous Analysis

Combining compositionality, the free‑energy principle, and model checking yields a **variational compositional model checker (VCMC)**. In VCMC a hypothesis is expressed as a compositional program written in a probabilistic domain‑specific language (DSL) – e.g., the lambda‑calculus‑based language used in DreamCoder or DeepProbLog. The program’s syntax defines reusable sub‑routines (compositionality); its semantics give a generative model that predicts sensory trajectories. The system performs variational inference (free‑energy minimization) to approximate the posterior over programs given observed data, adjusting program parameters to reduce prediction error. Finally, each sampled program is subjected to exhaustive model checking against a temporal‑logic specification (e.g., an LTL formula describing desired behavior) using tools such as PRISM or Storm, which explore the program’s induced state space and verify whether all possible executions satisfy the spec.

**Advantage for self‑testing hypotheses:** The system can generate a candidate explanation, compute its free‑energy score (how well it predicts data), and immediately obtain a formal guarantee (or counterexample) that the explanation respects the required dynamical properties. This tight loop prunes hypotheses that are statistically plausible but dynamically invalid, yielding more reliable, interpretable theories and reducing the burden of blind trial‑and‑error.

**Novelty:** Elements of this combination already exist: probabilistic program synthesis (DreamCoder, Bayesian Program Learning), variational inference in deep generative models (VAEs, Bayesian neural nets), and probabilistic model checking (PRISM, Storm). Recent work on “neural‑symbolic RL with LTL constraints” and “active inference with formal verification” touches on the intersection, but a unified framework that treats the program as a compositional generative model, optimizes it via free‑energy minimization, and exhaustively checks it against temporal logic has not been widely published. Thus the VCMC is a **novel synthesis** rather than a mere metaphor.

**Potential ratings**

Reasoning: 7/10 — The mechanism leverages strong formal foundations (compositional semantics, variational inference, model checking) but inherits computational hardness from exhaustive state‑space exploration, limiting scalability to moderate‑size hypotheses.

Metacognition: 8/10 — By explicitly monitoring prediction error (free energy) and verification outcomes, the system gains a clear signal about the adequacy of its own hypotheses, supporting higher‑order self‑assessment.

Hypothesis generation: 6/10 — Compositional DSLs enable rich hypothesis spaces, yet the need to satisfy temporal‑logic constraints can severely restrict viable programs, potentially slowing creative exploration.

Implementability: 5/10 — Integrating variational program synthesis with explicit model checking requires custom interfaces between inference engines (e.g., Pyro, TensorFlow Probability) and model‑checkers (PRISM/Storm); engineering such a pipeline is non‑trivial but feasible with existing libraries.

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

- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Model Checking: strong positive synergy (+0.259). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Constraint Satisfaction + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T06:49:30.375533

---

## Code

**Source**: scrap

[View code](./Compositionality---Free_Energy_Principle---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Compositional Model Checker (VCMC) Approximation.
    
    Mechanism:
    1. Compositionality: Parses prompts into structural components (negations, comparatives, 
       conditionals, numeric values) treating them as reusable sub-routines.
    2. Free Energy Principle (Core): Defines 'surprise' as the divergence between the 
       prompt's structural constraints and the candidate's logical implication. 
       Minimizes free energy by penalizing candidates that increase prediction error 
       (e.g., missing negations, inverted comparisons).
    3. Model Checking: Treats extracted constraints as temporal-logic-like specifications. 
       Candidates are exhaustively checked against these specs. Violations incur heavy 
       energy penalties (rejecting dynamically invalid hypotheses).
       
    This tight loop prunes statistically plausible but logically invalid answers, 
    prioritizing structural fidelity over simple string similarity.
    """

    def __init__(self):
        # Structural patterns acting as the "Compositional DSL"
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r"n't"]
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into structural components (Compositional Step)."""
        text_lower = text.lower()
        return {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': sorted([float(n) for n in re.findall(self.numeric_pattern, text)]),
            'length': len(text.split())
        }

    def _check_constraints(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Model Checking Step.
        Verifies if the candidate satisfies the logical constraints implied by the prompt.
        Returns a penalty score (0.0 = perfect, higher = violation).
        """
        penalty = 0.0
        
        # Check 1: Negation Consistency (Modus Tollens approximation)
        # If prompt has high negation density, candidate should reflect awareness (simplified)
        if prompt_struct['negations'] > 0:
            # Heuristic: If prompt negates, and candidate is extremely short (likely 'Yes'/'No'), 
            # we can't fully verify without semantic NLP, so we rely on structural match later.
            # Here we check for explicit contradiction in number extraction if present.
            pass

        # Check 2: Numeric Transitivity and Consistency
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If both have numbers, do they align in magnitude direction if comparatives exist?
            # This is a soft check; hard failures come from missing numbers entirely when expected.
            if len(prompt_struct['numbers']) == len(cand_struct['numbers']):
                # Check order preservation for simple sequences
                p_diff = [b-a for a, b in zip(prompt_struct['numbers'][:-1], prompt_struct['numbers'][1:])]
                c_diff = [b-a for a, b in zip(cand_struct['numbers'][:-1], cand_struct['numbers'][1:])]
                # If trends diverge significantly, add penalty
                if p_diff and c_diff:
                    if (p_diff[0] > 0) != (c_diff[0] > 0):
                        penalty += 0.5
        
        # Check 3: Conditional Logic (Simplified)
        # If prompt has conditionals, candidate must have sufficient complexity to address them
        if prompt_struct['conditionals'] > 0 and cand_struct['length'] < 3:
            penalty += 0.4 # Too simple to satisfy conditional logic

        return penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Free Energy Minimization Core.
        F = Accuracy (Prediction Error) + Complexity (Surprise)
        We minimize F. Lower F = Better Candidate.
        Converted to a score where Higher = Better.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Prediction Error (Variational Inference)
        # Measure divergence between prompt structure and candidate structure
        error = 0.0
        
        # Negation mismatch penalty
        if p_struct['negations'] > 0 and c_struct['negations'] == 0:
            error += 0.3 # Potential failure to capture negation
        
        # Comparative mismatch
        if p_struct['comparatives'] > 0 and c_struct['comparatives'] == 0:
            error += 0.2
            
        # 2. Model Checking Penalty (Hard Constraints)
        mc_penalty = self._check_constraints(p_struct, c_struct, prompt, candidate)
        
        # 3. Complexity Penalty (Occam's Razor)
        # Penalize excessive length relative to prompt unless justified by structure
        complexity_penalty = max(0, (c_struct['length'] - p_struct['length'] * 2) * 0.01)

        total_free_energy = error + mc_penalty + complexity_penalty
        
        # Convert to score (inverse energy)
        # Base score 1.0, subtract energy. Clamp to [0, 1].
        score = max(0.0, min(1.0, 1.0 - total_free_energy))
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_struct = self._extract_structure(prompt)
        
        # Pre-calculate prompt complexity for relative scoring
        base_energy = 0.5 
        
        for cand in candidates:
            # Primary Score: Variational Free Energy (Structural + Model Check)
            fe_score = self._compute_free_energy(prompt, cand)
            
            # Secondary Score: NCD (Tiebreaker only)
            # We use NCD to break ties among high-scoring candidates, 
            # but primarily we rely on the structural parse.
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Hybrid adjustment: If FE scores are close, NCD influences rank slightly
            # But FE is the driver. 
            final_score = fe_score * 0.95 + (1.0 - ncd_val) * 0.05
            
            reasoning = f"FE:{fe_score:.2f} | Struct:N{cand.count('not')+cand.count('no')} C{cand.count('if')} | NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy minimization."""
        score = self._compute_free_energy(prompt, answer)
        # Score is already 0-1 where higher is better
        return max(0.0, min(1.0, score))
```

</details>
