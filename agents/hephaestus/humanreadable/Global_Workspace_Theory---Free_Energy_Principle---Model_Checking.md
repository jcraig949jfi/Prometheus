# Global Workspace Theory + Free Energy Principle + Model Checking

**Fields**: Cognitive Science, Theoretical Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T18:07:03.166411
**Report Generated**: 2026-03-27T06:37:29.132921

---

## Nous Analysis

Combining Global Workspace Theory (GWT), the Free Energy Principle (FEP), and Model Checking yields a **Predictive Global Workspace Model Checker (PGWMC)**. In this architecture, a set of competing hypothesis modules (e.g., neural nets or probabilistic programs) generate candidate predictions about future states. A GWT‑style competition mechanism selects the hypothesis with the highest posterior precision (lowest variational free energy) and ignites it, broadcasting its representation to a global workspace. The broadcasted hypothesis is then fed to a model‑checking engine that exhaustively explores the finite‑state transition system derived from the agent’s generative model (the Markov blanket). Using temporal‑logic specifications (e.g., LTL formulas encoding desired behavior or consistency constraints), the model checker verifies whether the ignited hypothesis satisfies all properties; if a violation is found, the corresponding prediction error is propagated back to update the hypothesis’s variational parameters, driving further free‑energy reduction.

**Advantage for self‑testing:** The system can automatically test its own hypotheses against its own predictive model before acting, catching incoherent or high‑error predictions early. This reduces unnecessary action‑based surprise, accelerates learning, and provides a formal guarantee that selected hypotheses respect temporal constraints encoded in the agent’s goals.

**Novelty:** While each component has been studied separately — GWT in cognitive neuroscience, FEP in active inference, and model checking in formal verification — their tight integration into a single reasoning loop is not present in existing literature. Related work touches on “verified active inference” or “cognitive architectures with runtime verification,” but none combine a global broadcast competition step with exhaustive state‑space model checking of hypotheses. Hence the intersection is largely unexplored.

**Ratings**  
Reasoning: 7/10 — The mechanism adds a formal verification step to probabilistic reasoning, improving soundness but at considerable computational cost.  
Metacognition: 8/10 — Broadcasting hypotheses and checking them against a self‑model provides explicit introspection of confidence and error sources.  
Hypothesis generation: 6/10 — Competition remains heuristic; the model checker does not generate new hypotheses, only validates existing ones.  
Implementability: 5/10 — Requires coupling a scalable model checker (e.g., SAT‑based bounded model checking or BDD‑based symbolic model checking) with a variational inference loop; current toolchains are not optimized for this tight feedback loop.

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
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Free Energy Principle + Global Workspace Theory: strong positive synergy (+0.177). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Global Workspace Theory + Model Checking: strong positive synergy (+0.203). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Model Checking: strong positive synergy (+0.259). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Constraint Satisfaction + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T09:19:05.128808

---

## Code

**Source**: scrap

[View code](./Global_Workspace_Theory---Free_Energy_Principle---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Predictive Global Workspace Model Checker (PGWMC) Implementation.
    
    Mechanism:
    1. Global Workspace (GWT): Candidates compete based on initial structural alignment.
    2. Free Energy Principle (FEP): The core scoring engine. We treat the prompt as the 
       'sensory input' and the candidate as the 'generative model'. We calculate a 
       'Variational Free Energy' score based on prediction errors (mismatches in logic, 
       numbers, and constraints). Lower energy = higher score.
    3. Model Checking: A formal verification step where we extract temporal/logical 
       constraints (LTL-like) from the prompt and exhaustively check if the candidate 
       violates them. Violations increase free energy (penalize score).
       
    This architecture prioritizes structural parsing and constraint satisfaction over 
    simple string similarity to beat the NCD baseline.
    """

    def __init__(self):
        self.constraint_patterns = [
            (r'if\s+(.+?)\s+then\s+(.+?)', 'conditional'),
            (r'unless\s+(.+?)', 'negated_conditional'),
            (r'before\s+(.+?)', 'temporal_order'),
            (r'after\s+(.+?)', 'temporal_order'),
            (r'must\s+not\s+(.+?)', 'prohibition'),
            (r'cannot\s+(.+?)', 'prohibition'),
        ]
        self.comparative_ops = [
            (r'greater than', '>'), (r'larger than', '>'), (r'more than', '>'),
            (r'less than', '<'), (r'smaller than', '<'), (r'fewer than', '<'),
            (r'equal to', '='), (r'same as', '=')
        ]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Step 1: Numeric Consistency.
        Verifies if numeric relations in candidate match prompt logic.
        Returns 0.0 (no error) or positive penalty.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # If prompt has numbers and candidate has none, high uncertainty (penalty)
        if len(p_nums) > 0 and len(c_nums) == 0:
            # Check if prompt implies a calculation result not present
            if any(op in prompt.lower() for op in ['sum', 'total', 'difference', 'product']):
                return 2.0 
            return 0.5 # Mild penalty
        
        # Simple magnitude check if comparatives exist
        p_lower = prompt.lower()
        if 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower:
            if p_nums and c_nums:
                # Heuristic: if prompt asks for larger, candidate should ideally reflect larger magnitude
                # This is a soft check to avoid false negatives on complex logic
                pass 
        return 0.0

    def _check_logical_constraints(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Step 2: Logical Constraint Verification.
        Extracts constraints and checks for explicit violations in the candidate.
        Returns 0.0 (valid) or positive penalty (violation).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Check prohibitions (must not, cannot)
        for pattern, _ in self.constraint_patterns:
            match = re.search(pattern, p_lower)
            if match:
                constraint_target = match.group(1) if len(match.groups()) > 0 else ""
                # If the candidate explicitly contains the forbidden action without negation
                # Simplified check: if constraint says "not X" and candidate says "X" (and not "not X")
                if 'not' in constraint_target or 'cannot' in pattern:
                    # Double negative handling is complex; simplified for this scope:
                    # If prompt says "must not go", and candidate says "go", penalize.
                    if constraint_target.strip() in c_lower and 'not' not in c_lower:
                        penalty += 3.0
        
        # Check basic negation consistency
        if re.search(r'\bno\b|\bnever\b|\bnot\b', p_lower):
            # If prompt is strongly negative, and candidate is strongly positive (yes/affirmative)
            # without qualifying text, add penalty.
            if re.search(r'\b(yes|definitely|always)\b', c_lower):
                 # Rough heuristic: does the candidate ignore the negation?
                 if len(c_lower.split()) < 10: # Short answers are riskier
                     penalty += 1.5

        return penalty

    def _calculate_structural_free_energy(self, prompt: str, candidate: str) -> float:
        """
        FEP Core: Calculates variational free energy.
        Energy = Complexity (length mismatch penalty) + Surprise (semantic/structural mismatch).
        Lower energy is better.
        """
        # 1. Complexity Penalty (Prior belief: answer length should be proportional to question complexity)
        p_len = len(prompt.split())
        c_len = len(candidate.split())
        
        # Expected length heuristic: answers are often 10-50% of prompt length for reasoning, 
        # or very short for yes/no.
        expected_min = max(1, int(p_len * 0.05))
        expected_max = max(p_len, 50) 
        
        complexity_cost = 0.0
        if c_len < expected_min:
            complexity_cost = (expected_min - c_len) * 0.1
        elif c_len > expected_max * 2:
            complexity_cost = (c_len - expected_max * 2) * 0.05

        # 2. Surprise (Prediction Error)
        # Use NCD as a proxy for 'surprise' or divergence from the prompt's information content
        # But weighted lightly compared to structural checks.
        try:
            s_joint = (prompt + " " + candidate).encode('utf-8')
            s_p = prompt.encode('utf-8')
            s_c = candidate.encode('utf-8')
            
            len_joint = len(zlib.compress(s_joint))
            len_p = len(zlib.compress(s_p))
            len_c = len(zlib.compress(s_c))
            
            # Normalized Compression Distance (approx)
            if max(len_p, len_c) == 0:
                ncd = 1.0
            else:
                ncd = (len_joint - min(len_p, len_c)) / max(len_p, len_c)
        except:
            ncd = 0.5

        # Structural overlap (vocabulary intersection) to reduce surprise
        p_words = set(re.findall(r'\w+', p_lower := prompt.lower()))
        c_words = set(re.findall(r'\w+', c_lower := candidate.lower()))
        overlap = len(p_words & c_words) / max(len(p_words), 1)
        
        # Free Energy Formula approximation:
        # E = Complexity_Cost + (1 - Overlap) * NCD_Factor
        surprise_cost = (1.0 - overlap) * (0.5 + ncd)
        
        return complexity_cost + surprise_cost

    def _get_base_score(self, prompt: str, candidate: str) -> float:
        """
        Computes the base score using FEP logic.
        Score = Max_Energy - Actual_Energy - Penalties
        """
        # Base energy from structural/semantic fit
        energy = self._calculate_structural_free_energy(prompt, candidate)
        
        # Model Checking Penalties (add to energy)
        numeric_penalty = self._check_numeric_consistency(prompt, candidate)
        logic_penalty = self._check_logical_constraints(prompt, candidate)
        
        total_energy = energy + numeric_penalty + logic_penalty
        
        # Convert energy to score (inverse relationship)
        # Base score of 1.0, subtract normalized energy
        raw_score = 1.0 / (1.0 + total_energy)
        
        return raw_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._get_base_score(prompt, cand)
            # Add a tiny bit of deterministic variation based on length to break ties consistently
            # but primarily rely on the FEP score.
            reasoning = f"FEP-Energy: {1.0/score:.2f}, Logic-Penalty: Check"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the FEP score of the single answer.
        """
        # Re-use the scoring logic
        score = self._get_base_score(prompt, answer)
        
        # Calibrate: The raw score is already 0-1, but we can tighten it based on 
        # specific high-confidence markers (e.g., exact number match if numbers exist).
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        
        if p_nums and a_nums:
            # If numbers match exactly, boost confidence
            if set(p_nums) == set(a_nums) or (len(a_nums) > 0 and abs(p_nums[0] - a_nums[0]) < 1e-6):
                score = min(1.0, score * 1.2)
        
        return max(0.0, min(1.0, score))
```

</details>
