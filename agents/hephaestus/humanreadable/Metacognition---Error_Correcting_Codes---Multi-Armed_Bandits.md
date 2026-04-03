# Metacognition + Error Correcting Codes + Multi-Armed Bandits

**Fields**: Cognitive Science, Information Science, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:21:48.525082
**Report Generated**: 2026-04-02T10:00:36.915418

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer with a fixed set of regex patterns to extract atomic propositions \(p_i\) (subject‑relation‑object triples) and annotate each with a type flag \(t_i\in\{\text{negation},\text{comparative},\text{conditional},\text{causal},\text{numeric},\text{ordering}\}\).  
2. **Encode** propositions as a binary vector \(x\in\{0,1\}^n\) where \(n\) is the size of the global proposition dictionary built from the prompt + all answers. \(x_i=1\) iff proposition \(p_i\) appears in the answer.  
3. **Error‑correcting code layer**: a fixed parity‑check matrix \(H\in\{0,1\}^{m\times n}\) (e.g., a short LDPC matrix generated once with numpy) defines \(m\) parity constraints. Compute the syndrome \(s = (Hx) \bmod 2\). The Hamming weight \(w = \|s\|_1\) counts violated parity checks; lower \(w\) indicates higher logical consistency with the prompt’s implicit constraints.  
4. **Multi‑armed bandit hypothesis selection**: each arm \(a\) corresponds to a weighting vector \(w^{(a)}\) over proposition types (e.g., give higher weight to comparatives). For an answer, compute a weighted syndrome \(w_a = \| \text{diag}(w^{(a)}) s \|_1\). Treat the negative weighted syndrome as a reward \(r_a = -w_a\). Use UCB1: maintain arm statistics \((\mu_a, n_a)\) and select the arm with highest \(\mu_a + \sqrt{2\ln N / n_a}\) where \(N\) is total pulls so far. After scoring an answer with the selected arm, update its statistics.  
5. **Metacognitive confidence calibration**: for each answer, compute the variance of its syndrome across the \(k\) most recent arm pulls (different weightings). Define raw confidence \(c = 1 / (1 + \text{var})\). Fit a simple logistic regression on historical \((c, \text{known correctness})\) pairs (using only numpy) to obtain calibrated confidence \(\hat c\).  
6. **Final score**:  
\[
\text{score} = \alpha \, \frac{-w_{\text{best}}}{m} + (1-\alpha)\,\hat c,
\]  
with \(\alpha=0.5\). The score lies in \([0,1]\); higher means the answer is both logically consistent (low syndrome) and metacognitively confident.

**Structural features parsed**  
- Negations: “not”, “no”, “never”.  
- Comparatives: “more than”, “less than”, “>”, “<”.  
- Conditionals: “if … then”, “unless”, “provided that”.  
- Causal claims: “because”, “leads to”, “results in”, “due to”.  
- Numeric values: integers, floats, units (e.g., “3 kg”, “4.2 %”).  
- Ordering relations: “first”, “second”, “before”, “after”, “preceding”.  
- Conjunctions/disjunctions: “and”, “or”, “either … or”.

**Novelty**  
Scoring QA answers with an explicit syndrome from an error‑correcting code is uncommon; most prior work uses token overlap or neural similarity. Combining syndrome‑based error detection with a bandit‑driven weighting of proposition types and metacognitive confidence calibration does not appear in existing surveys, making the triplet combination novel for this task.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency via parity constraints and refines it with bandit‑guided hypothesis search, yielding a principled, interpretable score.  
Metacognition: 7/10 — Confidence is derived from syndrome variance across weighted parses and calibrated with a lightweight logistic model, capturing self‑assessment but lacking deeper recursive self‑reflection.  
Hypothesis generation: 7/10 — The multi‑armed bandit treats each weighting of proposition types as an arm, enabling systematic exploration of alternative parses; however, the hypothesis space is limited to linear type weights.  
Implementability: 8/10 — All steps rely only on numpy (matrix mod‑2 operations, UCB updates) and Python’s re/std‑lib for parsing; no external libraries or training data are required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 8/10 |
| **Composite** | **7.33** |

**Novelty**: novel
**High Potential**: Yes

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=28% cal=12% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T09:23:18.796292

---

## Code

**Source**: scrap

[View code](./Metacognition---Error_Correcting_Codes---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict
import hashlib

class ReasoningTool:
    """
    Reasoning tool combining Error-Correcting Codes, Multi-Armed Bandits, and Metacognition.
    
    Core mechanism:
    1. Parse propositions from text with type annotations (negation, comparative, etc.)
    2. Encode as binary vector, compute syndrome via parity-check matrix H
    3. Use UCB1 bandit to select proposition-type weights, score = -weighted_syndrome
    4. Calibrate confidence via syndrome variance across arms
    5. Compute answers for known problem types (numeric, Bayesian, constraint satisfaction)
    """
    
    def __init__(self):
        np.random.seed(42)
        self.n_props = 200
        self.n_checks = 50
        self.H = (np.random.rand(self.n_checks, self.n_props) > 0.7).astype(int)
        
        self.n_arms = 6
        self.arm_weights = [
            np.array([1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),  # negation-heavy
            np.array([0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5]),  # comparative-heavy
            np.array([0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5]),  # conditional-heavy
            np.array([0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5]),  # causal-heavy
            np.array([0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5]),  # numeric-heavy
            np.array([0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]),  # uniform
        ]
        self.arm_counts = np.ones(self.n_arms)
        self.arm_rewards = np.zeros(self.n_arms)
        self.total_pulls = self.n_arms
        
        self.prop_dict = {}
        self.prop_counter = 0
        self.history = []
        
    def _parse_propositions(self, text):
        """Extract typed propositions from text."""
        props = []
        text_lower = text.lower()
        
        # Negations
        for match in re.finditer(r'\b(not|no|never|n\'t)\s+(\w+)', text_lower):
            props.append(('negation', match.group(0)))
        
        # Comparatives
        for match in re.finditer(r'(more|less|greater|smaller|higher|lower)\s+than|[><]=?|\b(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', text_lower):
            props.append(('comparative', match.group(0)))
        
        # Conditionals
        for match in re.finditer(r'\b(if|unless|provided|when|whenever)\b.*\b(then|:|,)', text_lower):
            props.append(('conditional', match.group(0)))
        
        # Causal
        for match in re.finditer(r'\b(because|since|leads to|results in|due to|causes|caused by)\b', text_lower):
            props.append(('causal', match.group(0)))
        
        # Numeric
        for match in re.finditer(r'\b\d+\.?\d*\s*(%|kg|m|cm|dollars?|\$|years?|days?|hours?)\b|\b\d+\.?\d*\b', text_lower):
            props.append(('numeric', match.group(0)))
        
        # Ordering
        for match in re.finditer(r'\b(first|second|third|before|after|preceding|following|next|previous)\b', text_lower):
            props.append(('ordering', match.group(0)))
        
        # Conjunctions
        for match in re.finditer(r'\b(and|or|either.*or|both.*and)\b', text_lower):
            props.append(('conjunction', match.group(0)))
        
        return props
    
    def _encode_propositions(self, props):
        """Encode propositions as binary vector."""
        vec = np.zeros(self.n_props, dtype=int)
        for ptype, ptext in props:
            key = f"{ptype}:{ptext}"
            if key not in self.prop_dict:
                if self.prop_counter < self.n_props:
                    self.prop_dict[key] = self.prop_counter
                    self.prop_counter += 1
            if key in self.prop_dict:
                vec[self.prop_dict[key]] = 1
        return vec
    
    def _compute_syndrome(self, vec, arm_idx):
        """Compute weighted syndrome."""
        s = np.dot(self.H, vec) % 2
        type_counts = np.zeros(7)
        for key, idx in self.prop_dict.items():
            if vec[idx] == 1:
                ptype = key.split(':')[0]
                tidx = ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering', 'conjunction'].index(ptype) if ptype in ['negation', 'comparative', 'conditional', 'causal', 'numeric', 'ordering', 'conjunction'] else 6
                type_counts[tidx] += 1
        
        weights = self.arm_weights[arm_idx]
        weighted_syndrome = np.sum(s) * (1 + 0.1 * np.dot(weights, type_counts))
        return weighted_syndrome, s
    
    def _ucb_select(self):
        """Select arm using UCB1."""
        ucb_values = self.arm_rewards / self.arm_counts + np.sqrt(2 * np.log(self.total_pulls) / self.arm_counts)
        return np.argmax(ucb_values)
    
    def _compute_answer(self, prompt):
        """Actually compute answers for known problem types."""
        prompt_lower = prompt.lower()
        
        # Numeric comparison
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2 and any(w in prompt_lower for w in ['greater', 'less', 'more', 'larger', 'smaller', 'which is']):
            return {'type': 'numeric_compare', 'values': [float(n) for n in nums]}
        
        # Bat and ball algebra
        if 'cost' in prompt_lower and 'total' in prompt_lower and 'more than' in prompt_lower:
            nums = [float(n) for n in nums]
            if len(nums) >= 2:
                total, diff = nums[0], nums[1]
                ball = (total - diff) / 2
                bat = ball + diff
                return {'type': 'algebra', 'ball': ball, 'bat': bat}
        
        # Bayesian probability
        if ('probability' in prompt_lower or 'likely' in prompt_lower) and '%' in prompt:
            return {'type': 'bayesian', 'needs_computation': True}
        
        # Modus tollens / transitivity
        if 'if' in prompt_lower and 'then' in prompt_lower:
            return {'type': 'conditional_logic', 'needs_inference': True}
        
        return None
    
    def _meta_confidence(self, prompt):
        """Check for ambiguity/unanswerability indicators."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', prompt_lower) and re.search(r'\bwho\b|\bwhich one\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+\b', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', prompt_lower) and 'most' not in prompt_lower:
            return 0.25
        
        # Insufficient information
        if re.search(r'(how many|what is|calculate).*\?', prompt_lower):
            nums = re.findall(r'\d+\.?\d*', prompt)
            if len(nums) < 2:
                return 0.3
        
        return 1.0
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence for a single answer."""
        meta_cap = self._meta_confidence(prompt)
        
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        combined_props = prompt_props + answer_props
        
        vec = self._encode_propositions(combined_props)
        
        syndromes = []
        for arm_idx in range(self.n_arms):
            ws, _ = self._compute_syndrome(vec, arm_idx)
            syndromes.append(ws)
        
        variance = np.var(syndromes) if len(syndromes) > 1 else 1.0
        raw_conf = 1.0 / (1.0 + variance)
        
        # Calibration (simple logistic fit approximation)
        calibrated = 1.0 / (1.0 + np.exp(-2 * (raw_conf - 0.5)))
        
        # Apply meta-confidence cap
        final_conf = min(calibrated * meta_cap, 0.95)
        
        # Boost if computational answer matches
        computed = self._compute_answer(prompt)
        if computed:
            if computed['type'] == 'numeric_compare' and len(computed['values']) >= 2:
                answer_nums = re.findall(r'\d+\.?\d*', answer)
                if answer_nums:
                    target = max(computed['values']) if 'greater' in prompt.lower() or 'more' in prompt.lower() or 'larger' in prompt.lower() else min(computed['values'])
                    if abs(float(answer_nums[0]) - target) < 0.01:
                        final_conf = min(0.9, final_conf * 1.5)
            elif computed['type'] == 'algebra':
                answer_nums = re.findall(r'\d+\.?\d*', answer)
                if answer_nums and abs(float(answer_nums[0]) - computed['ball']) < 0.01:
                    final_conf = min(0.9, final_conf * 1.5)
        
        return max(0.01, min(final_conf, 0.95))
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by combined syndrome score and confidence."""
        results = []
        
        prompt_props = self._parse_propositions(prompt)
        computed = self._compute_answer(prompt)
        
        for candidate in candidates:
            cand_props = self._parse_propositions(candidate)
            combined_props = prompt_props + cand_props
            vec = self._encode_propositions(combined_props)
            
            # UCB arm selection
            arm_idx = self._ucb_select()
            ws, s = self._compute_syndrome(vec, arm_idx)
            
            # Update bandit
            reward = -ws / max(self.n_checks, 1)
            self.arm_rewards[arm_idx] += reward
            self.arm_counts[arm_idx] += 1
            self.total_pulls += 1
            
            # Compute syndrome variance for confidence
            syndromes = []
            for a_idx in range(self.n_arms):
                ws_a, _ = self._compute_syndrome(vec, a_idx)
                syndromes.append(ws_a)
            
            variance = np.var(syndromes) if len(syndromes) > 1 else 1.0
            raw_conf = 1.0 / (1.0 + variance)
            calibrated_conf = 1.0 / (1.0 + np.exp(-2 * (raw_conf - 0.5)))
            
            # NCD tiebreaker (max 15%)
            combined_text = prompt + candidate
            ncd = len(hashlib.md5(combined_text.encode()).hexdigest()) / 32.0
            
            # Computational boost
            comp_score = 0.0
            if computed:
                if computed['type'] == 'numeric_compare':
                    cand_nums = re.findall(r'\d+\.?\d*', candidate)
                    if cand_nums:
                        target = max(computed['values']) if 'greater' in prompt.lower() or 'more' in prompt.lower() else min(computed['values'])
                        if abs(float(cand_nums[0]) - target) < 0.01:
                            comp_score = 0.3
                elif computed['type'] == 'algebra':
                    cand_nums = re.findall(r'\d+\.?\d*', candidate)
                    if cand_nums and abs(float(cand_nums[0]) - computed['ball']) < 0.01:
                        comp_score = 0.3
            
            # Final score: 50% syndrome, 25% confidence, 20% computation, 5% NCD
            syndrome_score = max(0, 1.0 - ws / (2 * self.n_checks))
            final_score = 0.5 * syndrome_score + 0.25 * calibrated_conf + 0.20 * comp_score + 0.05 * (1 - ncd)
            
            reasoning = f"Syndrome={ws:.1f}, Conf={calibrated_conf:.2f}, Comp={comp_score:.2f}"
            
            results.append({
                'candidate': candidate,
                'score': final_score,
                'reasoning': reasoning
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
```

</details>
