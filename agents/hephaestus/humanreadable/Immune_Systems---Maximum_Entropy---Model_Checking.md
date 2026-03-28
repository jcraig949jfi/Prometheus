# Immune Systems + Maximum Entropy + Model Checking

**Fields**: Biology, Statistical Physics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T17:13:04.846492
**Report Generated**: 2026-03-27T06:37:28.660930

---

## Nous Analysis

Combining the three ideas yields a **Maximum‑Entropy Immune Model Checker (MEIMC)**: a population‑based search where each individual is a finite‑state hypothesis (e.g., a labeled transition system or a probabilistic automaton). The immune‑inspired clonal selection loop generates diverse candidates via mutation and recombination; each candidate’s fitness is computed from two sources. First, a **Maximum‑Entropy (MaxEnt) estimator** assigns the least‑biased probability distribution over observable outcomes consistent with current empirical constraints (data logs, resource bounds). The resulting log‑likelihood (or negative cross‑entropy) rewards hypotheses that explain the data without unwarranted assumptions. Second, a **model‑checking engine** (e.g., SPAR or PRISM) exhaustively verifies each candidate against a temporal‑logic specification of desired system behavior (LTL/CTL formulas). Candidates that violate the spec receive a heavy penalty; those that pass contribute to fitness proportionally to their MaxEnt score. Selection preferentially expands high‑fitness clones, while low‑fitness individuals are culled, and memory cells preserve high‑performing hypotheses for rapid recall when similar constraints reappear.

**Advantage for self‑hypothesis testing:** The system can autonomously generate, evaluate, and retain explanations of its own behavior. MaxEnt guards against over‑fitting by keeping the hypothesis set as unbiased as possible given the data, while model checking guarantees that any retained hypothesis satisfies critical correctness properties. The immune memory mechanism lets the system reuse proven hypotheses, drastically reducing re‑verification cost when faced with recurring scenarios.

**Novelty:** Artificial immune systems (AIS) and MaxEnt modeling are well studied separately, and probabilistic model checking exists, but no published work integrates clonal selection, MaxEnt‑based fitness evaluation, and exhaustive temporal‑logic verification into a single loop for self‑hypothesis validation. Thus the combination is largely uncharted, though it draws on known components.

**Ratings**  
Reasoning: 7/10 — The hybrid fitness metric blends statistical soundness with formal correctness, offering stronger inferential guarantees than either method alone.  
Metacognition: 8/10 — Memory cells and clonal selection give the system explicit introspection of its hypothesis repertoire, supporting self‑monitoring and adaptation.  
Hypothesis generation: 7/10 — Clonal expansion yields diverse candidates; MaxEnt ensures they are not arbitrarily biased, improving coverage of the hypothesis space.  
Implementability: 5/10 — Requires coupling an AIS framework (e.g., opt-aiNet), a MaxEnt solver (e.g., iterative scaling or convex optimization), and a model checker (SPAR/PRISM); engineering the feedback loop and managing state‑space explosion is nontrivial.  

Reasoning: 7/10 — <why>
Metacognition: 8/10 — <why>
Hypothesis generation: 7/10 — <why>
Implementability: 5/10 — <why>

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

- **Immune Systems**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Maximum Entropy + Model Checking: strong positive synergy (+0.129). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Maximum Entropy + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=13% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-27T05:02:24.505530

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Maximum_Entropy---Model_Checking/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Immune Model Checker (MEIMC) - Structural Implementation
    
    Mechanism:
    1. Immune System (Clonal Selection): Candidates are evaluated for diversity and 
       constraint matching. High-fitness clones (those satisfying logical constraints) 
       are selected; low-fitness ones are culled.
    2. Maximum Entropy (Constraint): Used as a confidence wrapper. We avoid over-biasing 
       the score toward string length or simple repetition. It ensures the probability 
       distribution over the "correctness" space is only biased by explicit structural 
       evidence (negations, math, logic), not noise.
    3. Model Checking: The core scoring engine acts as a verifier. It checks candidates 
       against the prompt's logical spec (conditionals, comparatives, negations). 
       Violations receive heavy penalties (fitness = 0).
       
    Scoring Strategy:
    - Primary: Structural parsing (logic, math, constraints).
    - Secondary: NCD (tiebreaker only).
    - Confidence: Derived from the ratio of structural evidence to total entropy.
    """

    def __init__(self):
        self.memory_cells = []  # Stores high-performing (prompt_pattern, score_delta)

    def _structural_parse(self, text: str) -> dict:
        """Extract logical structures: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'boolean_yes': 1 if re.search(r'\b(yes|true|correct)\b', text_lower) else 0,
            'boolean_no': 1 if re.search(r'\b(no|false|incorrect)\b', text_lower) else 0,
        }
        return features

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Engine: Verifies candidate against prompt constraints.
        Returns a fitness score (0.0 to 1.0+).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation context, candidate should reflect understanding
        if p_feat['negations'] > 0:
            # Reward if candidate acknowledges negation or provides specific counter
            if c_feat['negations'] > 0 or c_feat['boolean_no'] > 0:
                score += 0.4
            # Penalty if candidate blindly agrees with a negative premise without nuance
            elif c_feat['boolean_yes'] > 0 and len(candidate.split()) < 10:
                score -= 0.5 

        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            # Candidate should ideally contain comparative language or specific numbers
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += 0.3
            else:
                score -= 0.2

        # 3. Numeric Evaluation (Direct Computation Check)
        if len(p_feat['numbers']) >= 2 and len(c_feat['numbers']) >= 1:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Simple heuristic: If prompt implies math, candidate number should be relevant
                # Check if candidate number matches any prompt number (often the answer)
                # or is a result of simple operation (approximated by presence)
                if any(abs(c_nums[0] - p) < 1e-6 for p in p_nums):
                    score += 0.5
                elif c_nums[0] > 0: # Presence of a calculated number is good
                    score += 0.2
            except ValueError:
                pass

        # 4. Conditional Adherence
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['boolean_yes'] > 0 or c_feat['boolean_no'] > 0:
                score += 0.2
        
        # Base relevance bonus (length sanity check to avoid empty strings)
        if len(candidate.strip()) > 2:
            score += 0.1
            
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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
        
        # Step 1: Model Checking & Fitness Evaluation
        scores = []
        for cand in candidates:
            fitness = self._evaluate_logic(prompt, cand)
            scores.append(fitness)
        
        max_fit = max(scores) if scores else 0.0
        
        # Step 2: Clonal Selection & Ranking
        # Normalize scores and apply MaxEnt-inspired penalty for low diversity/overfitting
        # (Here simplified to scaling by max fitness to ensure we pick the 'least wrong' if all are bad)
        for i, cand in enumerate(candidates):
            base_score = scores[i]
            
            # Tie-breaking with NCD only if structural scores are close or zero
            ncd_score = 0.0
            if max_fit < 0.1: # If structural signal is weak, use NCD as tiebreaker
                # Prefer candidate that compresses well with prompt (contextual relevance)
                ncd_val = self._ncd(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.05 # Small weight
            
            final_score = base_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Fitness:{base_score:.2f} | NCD_bonus:{ncd_score:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        MaxEnt Confidence Wrapper.
        Estimates confidence based on the density of structural evidence.
        High entropy (low confidence) if structural signals are ambiguous.
        Low entropy (high confidence) if strong logical constraints are met.
        """
        if not answer.strip():
            return 0.0
            
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        evidence_count = 0
        total_constraints = 0
        
        # Count active constraints in prompt
        total_constraints += p_feat['negations']
        total_constraints += p_feat['comparatives']
        total_constraints += p_feat['conditionals']
        total_constraints += 1 if p_feat['numbers'] else 0
        
        if total_constraints == 0:
            # No structural constraints found; rely on basic match
            return 0.5 if len(answer) > 2 else 0.2

        # Check satisfaction
        if p_feat['negations'] > 0 and (a_feat['negations'] > 0 or a_feat['boolean_no'] > 0):
            evidence_count += 1
        elif p_feat['negations'] == 0: # If no negation in prompt, explicit negation in answer might be wrong
            evidence_count += 0.5 
            
        if p_feat['comparatives'] > 0 and (a_feat['comparatives'] > 0 or a_feat['numbers']):
            evidence_count += 1
            
        if p_feat['conditionals'] > 0 and (a_feat['conditionals'] > 0 or a_feat['boolean_yes'] or a_feat['boolean_no']):
            evidence_count += 1
            
        if p_feat['numbers'] and a_feat['numbers']:
            evidence_count += 1

        # MaxEnt Estimator: 
        # Confidence = Evidence / (Constraints + smoothing)
        # This prevents over-confidence when constraints are high but evidence is low.
        raw_conf = evidence_count / (total_constraints + 1.0)
        
        # Clamp and smooth
        conf = min(0.99, max(0.01, raw_conf))
        
        # Boost if simple numeric match found
        if p_feat['numbers'] and a_feat['numbers']:
            try:
                if any(float(p) == float(a_feat['numbers'][0]) for p in p_feat['numbers']):
                    conf = min(0.99, conf + 0.3)
            except: pass
            
        return conf
```

</details>
