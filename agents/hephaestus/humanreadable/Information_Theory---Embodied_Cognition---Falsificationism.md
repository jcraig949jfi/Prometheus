# Information Theory + Embodied Cognition + Falsificationism

**Fields**: Mathematics, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T19:58:15.991392
**Report Generated**: 2026-03-27T06:37:30.477950

---

## Nous Analysis

Combining the three ideas yields a **Falsification‑Driven Embodied Active Inference** architecture. The agent maintains a hierarchical generative model \(p(s_{t+1},a_t|\theta)\) of forthcoming sensory states \(s\) given motor commands \(a\) and hypothesis parameters \(\theta\) (the “conjecture”). Using variational free‑energy minimization (a formulation of Shannon surprise), the agent computes the **expected information gain**—the mutual information \(I(\theta; s_{t+1}|a_t)\)—for each feasible action afforded by its morphology and current environment (embodied cognition’s affordance map). It then selects the action that **maximizes the expected KL‑divergence** between the predictive distribution under the current hypothesis and the distribution under its most plausible rival, i.e., the action most likely to **falsify** the conjecture if it is false. After executing the action, the agent updates its posterior over \(\theta\) via Bayes rule, thereby reducing entropy only when the hypothesis survives the test.  

**Advantage:** The system actively seeks observations that are most diagnostic, avoiding confirmation bias and converging faster than passive curiosity‑driven learners. By tying hypothesis testing to sensorimotor affordances, it restricts exploration to physically realizable experiments, saving computational effort and embodying Popper’s bold conjectures through concrete, falsifiable probes.  

**Novelty:** Active inference and Bayesian experimental design already unite information theory with embodied action, and curiosity‑reinforcement learning adds intrinsic motivation. However, making **falsification the explicit optimality criterion**—maximizing expected disproof power rather than merely surprise reduction—has not been formalized as a unified algorithmic framework. Thus the intersection is **novel in emphasis**, though it builds on well‑studied components.  

**Ratings**  
Reasoning: 8/10 — The mechanism provides a principled, information‑theoretic basis for selecting tests that most efficiently discriminate hypotheses.  
Metacognition: 7/10 — The agent can monitor its own surprise and expected falsification power, but higher‑order reflection on the testing process itself remains limited.  
Hypothesis generation: 7/10 — New conjectures arise from posterior updates; however, generating radically novel hypothesis spaces still relies on external priors or mutation‑like mechanisms.  
Implementability: 6/10 — Requires integrating deep predictive coding, affordance‑aware action selection, and KL‑based planning; feasible in simulation but challenging for real‑time robotic deployment.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 6/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Embodied Cognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Falsificationism**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Embodied Cognition + Information Theory: strong positive synergy (+0.295). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Falsificationism + Information Theory: negative interaction (-0.067). Keep these concepts in separate code paths to avoid interference.
- Embodied Cognition + Falsificationism: negative interaction (-0.076). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Information Theory + Sparse Autoencoders + Embodied Cognition (accuracy: 0%, calibration: 0%)
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Predictive Coding + Falsificationism (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=20% cal=7% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T08:02:00.792006

---

## Code

**Source**: scrap

[View code](./Information_Theory---Embodied_Cognition---Falsificationism/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Falsification-Driven Embodied Active Inference Tool.
    
    Mechanism:
    1. HYPOTHESIS (Conjecture): Treats each candidate answer as a provisional hypothesis 
       about the correct completion of the prompt.
    2. EMBODIED AFFORDANCE (Structural Parsing): Instead of physical sensors, the agent 
       uses structural parsing (negations, comparatives, conditionals, numeric logic) 
       as its "sensory affordances." These are the only valid probes into the problem space.
    3. FALSIFICATION (KL-Divergence Approximation): 
       - The agent constructs a "rival" hypothesis by logically inverting the structural 
         constraints found in the prompt (e.g., if prompt says "A > B", the rival assumes "B >= A").
       - It scores the candidate by how well it survives this falsification test. 
       - Candidates that contradict the parsed structural constraints receive a heavy penalty 
         (high expected KL-divergence from reality), effectively falsifying them.
       - Candidates consistent with constraints gain score based on NCD (compression) as a 
         secondary measure of coherence (low surprise).
    
    This implements Popperian falsification by actively seeking to disprove candidates 
    via logical constraint violation rather than just matching patterns.
    """

    def __init__(self):
        self.constraints = []
        self.numeric_baseline = 0.0

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical affordances: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'logic_ops': len(re.findall(r'\b(and|or|but|however|therefore)\b', text_lower))
        }
        return features

    def _check_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Falsification Step: Checks if the candidate contradicts explicit structural 
        constraints in the prompt. Returns a penalty score (0.0 = no violation, 1.0 = falsified).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Falsification
        # If prompt says "X is not Y" and candidate implies "X is Y"
        neg_matches = re.findall(r'(\w+)\s+is\s+not\s+(\w+)', p_lower)
        for subj, obj in neg_matches:
            if subj in c_lower and obj in c_lower:
                # Simple heuristic: if both subject and object appear in candidate without 'not',
                # it might be a contradiction. 
                # Refinement: Check if 'not' is absent in candidate near these words.
                if re.search(rf'{subj}.*{obj}', c_lower) and 'not' not in c_lower:
                    penalty += 0.5

        # 2. Comparative Falsification
        # If prompt says "A > B" and candidate suggests "B > A" or "A < B"
        comp_patterns = [
            (r'(\w+)\s+is\s+greater\s+than\s+(\w+)', lambda a, b: (a, b, 'gt')),
            (r'(\w+)\s+is\s+less\s+than\s+(\w+)', lambda a, b: (a, b, 'lt')),
            (r'(\w+)\s+>\s+(\w+)', lambda a, b: (a, b, 'gt')),
            (r'(\w+)\s+<\s+(\w+)', lambda a, b: (a, b, 'lt')),
        ]
        
        for pattern, extractor in comp_patterns:
            matches = re.findall(pattern, p_lower)
            for m in matches:
                a, b, op = extractor(*m) if len(m) == 2 else (*m, 'gt') # Simplified extraction
                
                # Check candidate for reverse logic
                if op == 'gt': # Prompt: A > B. Falsified if candidate says B > A or A < B
                    if re.search(rf'{b}.*{a}', c_lower) and re.search(r'(greater|more|>)', c_lower):
                        penalty += 0.4
                    if re.search(rf'{a}.*{b}', c_lower) and re.search(r'(less|smaller|<)', c_lower):
                        penalty += 0.4
                elif op == 'lt': # Prompt: A < B. Falsified if candidate says A > B
                    if re.search(rf'{a}.*{b}', c_lower) and re.search(r'(greater|more|>)', c_lower):
                        penalty += 0.4

        # 3. Numeric Consistency (Basic)
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if p_nums and c_nums:
            # If prompt defines a range or limit, check candidate
            # Example heuristic: If prompt has "max 10" and candidate has "15"
            if 'max' in p_lower or 'limit' in p_lower:
                try:
                    limit = float(p_nums[-1])
                    cand_val = float(c_nums[-1])
                    if cand_val > limit:
                        penalty += 0.6
                except ValueError:
                    pass

        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if c1 == 0 or c2 == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        prompt_features = self._parse_structure(prompt)
        
        # Calculate baseline NCD among candidates to normalize scores slightly
        # This acts as the "prior" distribution over the hypothesis space
        
        for cand in candidates:
            # 1. Falsification Test (Primary Driver)
            # How much does this candidate violate the structural constraints?
            falsification_penalty = self._check_constraint_violation(prompt, cand)
            
            # 2. Information Gain / Coherence (Secondary)
            # Low NCD between prompt and candidate suggests high relevance (low surprise)
            # We invert NCD so higher is better. 
            ncd_val = self._compute_ncd(prompt, cand)
            coherence_score = 1.0 - ncd_val
            
            # 3. Structural Alignment Bonus
            # Does the candidate share structural features (e.g. numbers, logic words)?
            cand_features = self._parse_structure(cand)
            struct_match = 0.0
            if prompt_features['numbers'] and cand_features['numbers']:
                struct_match += 0.1
            if prompt_features['negations'] > 0 and cand_features['negations'] > 0:
                struct_match += 0.05
            if prompt_features['comparatives'] > 0 and cand_features['comparatives'] > 0:
                struct_match += 0.05

            # Final Score: Coherence - Falsification Penalty + Structural Bonus
            # Falsification is the hard filter (multiplicative or heavy subtractive)
            base_score = coherence_score + struct_match
            final_score = base_score * (1.0 - falsification_penalty * 0.8) # Strong penalty
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Falsification penalty: {falsification_penalty:.2f}, Coherence: {coherence_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on falsification survival.
        If the answer is falsified by structural parsing, confidence is near 0.
        Otherwise, it scales with NCD coherence.
        """
        penalty = self._check_constraint_violation(prompt, answer)
        if penalty >= 0.5:
            return 0.05 # Strongly falsified
        
        ncd_val = self._compute_ncd(prompt, answer)
        coherence = 1.0 - ncd_val
        
        # Adjust coherence by penalty
        conf = coherence * (1.0 - penalty)
        return round(max(0.0, min(1.0, conf)), 4)
```

</details>
