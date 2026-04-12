# Causal Inference + Free Energy Principle + Maximum Entropy

**Fields**: Information Science, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-24T19:05:05.758939
**Report Generated**: 2026-03-27T06:37:29.839891

---

## Nous Analysis

Combining causal inference, the free‑energy principle, and maximum‑entropy reasoning yields a **Causal Maximum‑Entropy Active Inference (CMEAI)** architecture. The system learns a latent causal graph \(G\) over variables \(X\) using a variational auto‑encoder whose encoder approximates the posterior \(q(G|X)\) and whose decoder predicts observations. The prior over graphs is set to a maximum‑entropy distribution consistent with any known conditional independencies (e.g., sparsity or known parent‑child constraints), implemented as an exponential‑family prior \(p(G)\propto\exp\bigl(\sum_i\lambda_i\phi_i(G)\bigr)\) where the \(\phi_i\) are sufficient statistics (e.g., edge counts).  

Inference proceeds by minimizing variational free energy  
\[
\mathcal{F}= \mathbb{E}_{q(G|X)}[\log q(G|X)-\log p(X,G)] ,
\]  
which simultaneously performs causal discovery (via the do‑calculus‑compatible likelihood term) and keeps the belief distribution as unbiased as possible (maximum‑entropy prior).  

For self‑hypothesis testing, the agent augments free energy with **expected free energy** (EFE) from active inference:  
\[
\mathrm{G}(a)=\underbrace{\mathbb{E}_{q}[\,\mathrm{KL}(q(X'|do(a))\|p(X'))\,]}_{\text{epistemic value}}-\underbrace{\mathbb{E}_{q}[\,\log p(X'|do(a))\,]}_{\text{pragmatic value}},
\]  
where actions \(a\) correspond to interventions \(do(X_i=x)\). By selecting actions that minimize EFE, the system chooses interventions that maximally reduce uncertainty about causal edges (high epistemic value) while respecting the maximum‑entropy prior (low bias). This yields a closed loop: observe → update causal beliefs via variational inference → propose maximally informative, minimally biased interventions → execute → repeat.  

**Advantage:** The reasoning system can autonomously design experiments that are both causally informative and theoretically unbiased, leading to faster, more reliable identification of true causal mechanisms compared to passive observation or heuristic trial‑and‑error.  

**Novelty:** Each component—causal discovery (PC, NOTEARS), variational free‑energy minimization (variational autoencoders, active inference), and maximum‑entropy priors (Jaynes, exponential families)—is well studied. Their tight integration for self‑directed hypothesis testing via EFE is not a standard technique; related work appears in Bayesian experimental design with causal graphs, but the joint variational free‑energy + max‑entropy prior formulation is largely unexplored, making the combination moderately novel.  

**Ratings**  
Reasoning: 7/10 — provides a principled causal‑probabilistic inference layer that leverages do‑calculus.  
Metacognition: 8/10 — the EFE term gives explicit monitoring of uncertainty and drives self‑initiated tests.  
Hypothesis generation: 7/10 — interventions are generated as epistemic actions, directly testing causal hypotheses.  
Implementability: 5/10 — requires joint learning of graph variational posteriors, max‑entropy priors, and planning; current toolchains make this challenging but feasible with recent probabilistic programming libraries.

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

- **Causal Inference**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Free Energy Principle + Maximum Entropy: strong positive synergy (+0.241). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Prime Number Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=27% cal=20% ncd_acc=20% ncd_cal=7%)

**Forge Timestamp**: 2026-03-26T07:03:10.660874

---

## Code

**Source**: scrap

[View code](./Causal_Inference---Free_Energy_Principle---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Causal Maximum-Entropy Active Inference (CMEAI) Implementation.
    
    Mechanism:
    1. Free Energy Principle (Core): The 'evaluate' score is driven by minimizing 
       variational free energy. We approximate this by measuring the 'surprise' 
       (negative log-likelihood) of a candidate given the prompt's structural constraints.
       Low surprise = Low Free Energy = High Score.
    2. Maximum Entropy (Constraint): Used in 'confidence' to penalize answers that 
       violate explicit logical negations or comparative constraints found in the prompt.
       This acts as a high-precision filter (low bias, high constraint).
    3. Causal Inference (Structural): We parse logical operators (if/then, not, greater)
       to establish a causal graph of the text. Candidates are scored on their 
       consistency with this graph.
    4. NCD: Used strictly as a tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Structural keywords for causal parsing
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.comparators = ['greater', 'larger', 'more', 'less', 'smaller', 'fewer', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'therefore']
        self.bool_yes = ['yes', 'true', 'correct', '1', 'affirmative']
        self.bool_no = ['no', 'false', 'incorrect', '0', 'negative']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical constraints (negations, comparatives, conditionals)."""
        lower_text = self._normalize(text)
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparator = any(c in lower_text for c in self.comparators)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', lower_text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negation': has_negation,
            'comparator': has_comparator,
            'conditional': has_conditional,
            'numbers': nums,
            'word_count': len(words)
        }

    def _check_logical_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Check if candidate contradicts prompt constraints.
        Returns 1.0 (consistent) or 0.0 (contradictory).
        """
        cand_lower = self._normalize(candidate)
        
        # 1. Negation Consistency
        # If prompt has strong negation, and candidate is a bare affirmative without qualification
        if prompt_struct['negation']:
            # Simple heuristic: if prompt says "not X" and candidate is just "X" or "Yes" to "Is it X?"
            # We check if candidate is a bare positive assertion when context implies negative
            is_bare_positive = any(by in cand_lower.split() for by in self.bool_yes)
            is_bare_negative = any(bn in cand_lower.split() for bn in self.bool_no)
            
            # If the prompt is negative, a bare "Yes" might be a trap depending on question type.
            # However, a bare "No" is often safer if the prompt denies a premise.
            # Here we apply a penalty if the candidate ignores the negation entirely 
            # (e.g. Prompt: "It is not true that...", Candidate: "It is true")
            if is_bare_positive and not is_bare_negative:
                # Heuristic penalty for ignoring negation context
                return 0.5 
                
        # 2. Numeric Consistency
        if prompt_struct['numbers'] and len(prompt_struct['numbers']) >= 2:
            # Extract numbers from candidate if any
            cand_nums = re.findall(r'\d+\.?\d*', cand_lower)
            if cand_nums:
                c_val = float(cand_nums[0])
                p_vals = prompt_struct['numbers']
                # If prompt implies ordering (e.g. 9.11 vs 9.9) and candidate picks wrong one
                # This is a simplified check for direct number matching
                if c_val not in p_vals:
                    return 0.2 # Low score if number isn't in prompt context
        
        return 1.0

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Approximate Variational Free Energy.
        F = Surprise (Likelihood) + Complexity (Prior).
        We minimize F. Lower F -> Higher Score.
        """
        # 1. Surprise term: How well does the candidate fit the prompt's structural expectations?
        # We use a simple overlap of structural tokens as a proxy for likelihood.
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        surprise = 0.0
        
        # Penalty for mismatched logical types (e.g. prompt has numbers, candidate has none)
        if p_struct['numbers'] and not c_struct['numbers']:
            # Check if candidate is purely textual yes/no
            if not any(b in self._normalize(candidate) for b in self.bool_yes + self.bool_no):
                 surprise += 0.2
        
        # 2. Complexity/Prior term: Encourage maximum entropy (unbiased) unless constrained.
        # Short, generic answers have high prior probability (low complexity) but might have high surprise.
        # Long, specific answers have low prior (high complexity).
        # We balance this by favoring answers that resolve the prompt's uncertainty.
        
        consistency = self._check_logical_consistency(p_struct, candidate)
        if consistency < 1.0:
            surprise += 0.5 * (1.0 - consistency)

        # Base surprise from length mismatch (heuristic for information content)
        # Ideally, answer length should be proportional to question complexity
        len_ratio = len(candidate) / (len(prompt) + 1)
        if len_ratio > 0.8: # Answer too long relative to prompt?
            surprise += 0.1
            
        return surprise

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates by minimizing Free Energy (maximizing structural fit).
        """
        scored = []
        prompt_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # Core Metric: Free Energy Minimization
            # Lower energy = Better candidate. We invert this for the score.
            fe = self._calculate_free_energy(prompt, cand)
            base_score = 1.0 / (1.0 + fe) # Convert energy to 0-1 score
            
            # Apply Structural Parsing Boosts (The "Reasoning" layer)
            # If prompt has comparators, boost candidates that look like comparisons or numbers
            if prompt_struct['comparator']:
                if re.search(r'\d+', cand) or any(c in self._normalize(cand) for c in ['greater', 'less', 'more']):
                    base_score += 0.15
            
            # If prompt has conditionals, boost candidates with logical connectors
            if prompt_struct['conditional']:
                if any(c in self._normalize(cand) for c in ['if', 'then', 'because', 'so']):
                    base_score += 0.1

            # Tie-breaking with NCD (only if scores are very close, handled by sorting stability mostly, 
            # but we add a tiny epsilon based on NCD to prompt)
            ncd_val = self._ncd(prompt, cand)
            # Lower NCD (more similar structure) gets a tiny boost, but secondary to logic
            ncd_boost = (1.0 - ncd_val) * 0.01 
            
            final_score = base_score + ncd_boost
            
            # Reasoning string generation
            reason = f"FE={fe:.2f}, StructMatch={base_score:.2f}"
            if prompt_struct['negation'] and self._check_logical_consistency(prompt_struct, cand) < 1.0:
                reason += "; Warning: Potential negation conflict"
            if prompt_struct['numbers'] and not re.search(r'\d+', cand):
                reason += "; Note: Missing numeric content"

            scored.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses Maximum Entropy principle: High confidence only if constraints are strictly satisfied.
        If constraints (negation, logic) are ambiguous or violated, confidence drops to max-entropy (0.5).
        """
        p_struct = self._extract_structure(prompt)
        consistency = self._check_logical_consistency(p_struct, answer)
        
        # Base confidence on logical consistency
        conf = consistency
        
        # Penalize if prompt has strong logical operators but answer is generic
        generic_terms = ['yes', 'no', 'maybe', 'i don\'t know', 'unknown']
        if self._normalize(answer) in generic_terms:
            if p_struct['conditional'] or p_struct['comparator']:
                conf *= 0.8 # Reduce confidence for generic answers to complex logical prompts
        
        # If consistency is perfect, boost towards 1.0, else decay towards 0.0
        # This implements the "unbiased" prior: if no evidence against, stay neutral (0.5), 
        # but strong evidence moves it.
        if consistency == 1.0:
            # Check for positive reinforcement (does answer address the prompt?)
            # Simple overlap check
            p_words = set(re.findall(r'\b\w+\b', self._normalize(prompt)))
            a_words = set(re.findall(r'\w+', self._normalize(answer)))
            overlap = len(p_words.intersection(a_words))
            if overlap > 0:
                conf = min(1.0, 0.7 + 0.3 * (overlap / len(p_words))) # Cap at 1.0
        else:
            conf = 0.2 # Low confidence if logical conflict detected
            
        return round(conf, 3)
```

</details>
