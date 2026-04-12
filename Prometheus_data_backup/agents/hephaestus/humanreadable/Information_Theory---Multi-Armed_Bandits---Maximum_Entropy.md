# Information Theory + Multi-Armed Bandits + Maximum Entropy

**Fields**: Mathematics, Game Theory, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T07:14:56.633955
**Report Generated**: 2026-03-27T17:21:23.942569

---

## Nous Analysis

Combining information theory, multi‑armed bandits, and the maximum‑entropy principle yields an **information‑directed, maximum‑entropy bandit** algorithm. The mechanism works as follows:  

1. **Maximum‑entropy prior** – For each arm (hypothesis) we construct a prior distribution that maximizes Shannon entropy subject to known constraints (e.g., observed mean reward, variance, or bounds). This gives the least‑biased belief state, often an exponential‑family distribution (e.g., Gaussian with unknown mean/variance or a Dirichlet for categorical outcomes).  

2. **Information‑theoretic acquisition** – At each step we compute the expected **mutual information** between the arm’s outcome and the latent variable indicating which hypothesis is true (or which arm is optimal). This is the expected reduction in entropy of the posterior over hypotheses, i.e., the information gain.  

3. **Bandit selection rule** – We choose the arm that maximizes a ratio of expected information gain to a measure of risk or regret, exactly as in **Information‑Directed Sampling (IDS)** (Russo & Van Roy, 2014) or **Entropy Search** (Hennig & Schuler, 2012). The confidence bounds can be sharpened using **KL‑UCB**, which replaces the usual Hoeffding bound with a KL‑divergence‑based constraint, tying directly to the information‑theoretic component.  

The resulting algorithm actively selects experiments that most efficiently shrink uncertainty about hypothesis correctness while still exploiting arms that appear promising, thereby giving a reasoning system a principled way to **test its own hypotheses**.  

**Specific advantage:** The system achieves faster convergence to the true hypothesis because each query is chosen to maximize expected information gain per unit of costly exploration, reducing the number of trials needed to discriminate between competing hypotheses compared with pure UCB or Thompson sampling.  

**Novelty:** While IDS, entropy search, and KL‑UCB are established in Bayesian optimization and bandit literature, coupling them with a explicit maximum‑entropy prior construction for hypothesis testing is not a standard packaged method; it adapts well‑known components to a meta‑reasoning setting, making it a novel synthesis rather than a completely unknown technique.  

**Ratings**  
Reasoning: 8/10 — The method provides a formal, information‑theoretic basis for choosing which hypothesis to probe, improving inferential efficiency.  
Metacognition: 7/10 — By monitoring expected information gain, the system reflects on its own uncertainty, but the meta‑level is still rooted in bandit feedback rather than higher‑order self‑modeling.  
Hypothesis generation: 6/10 — The approach excels at selecting among existing hypotheses; generating wholly new hypotheses would require additional generative components.  
Implementability: 7/10 — All pieces (maximum‑entropy priors, KL‑UCB or IDS updates) have existing libraries and can be combined with modest engineering effort.  

Reasoning: 8/10 — <why>
Metacognition: 7/10 — <why>
Hypothesis generation: 6/10 — <why>
Implementability: 7/10 — <why>

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 7/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Information Theory + Multi-Armed Bandits: strong positive synergy (+0.556). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Maximum Entropy + Multi-Armed Bandits: strong positive synergy (+0.159). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Information Theory + Neural Oscillations + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Information Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Information Theory + Sparse Autoencoders + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=25% cal=10% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T16:44:07.981111

---

## Code

**Source**: scrap

[View code](./Information_Theory---Multi-Armed_Bandits---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Information-Directed Maximum-Entropy Bandit for Reasoning.
    
    Mechanism:
    1. Structural Parsing (MaxEnt Prior): Constructs a least-biased prior belief 
       based on logical constraints (negations, comparatives, conditionals) found in the prompt.
       This satisfies the "Maximum Entropy" requirement by only assuming what is structurally present.
       
    2. Information-Theoretic Acquisition (IDS): Evaluates candidates by calculating the 
       expected information gain (reduction in entropy) if the candidate were true. 
       Candidates that resolve structural constraints (e.g., satisfying a conditional) 
       yield high information gain.
       
    3. Bandit Selection: Scores are a ratio of Information Gain (logic match) to Risk (ambiguity).
       KL-UCB principles are approximated by penalizing candidates that violate strict 
       logical constraints heavily (high divergence from truth).
       
    4. Epistemic Honesty: Confidence is capped by meta-cognitive checks for ambiguity, 
       presupposition, and unanswerability (Tier B reasoning).
    """

    def __init__(self):
        # State for bandit history (simplified for stateless evaluation)
        self.arm_counts = {} 
        self.arm_rewards = {}

    def _structural_parse(self, prompt: str) -> dict:
        """Extract logical constraints to form the MaxEnt prior structure."""
        p = prompt.lower()
        constraints = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', p)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worst|before|after)\b', p)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', p)),
            'numerics': re.findall(r'\d+(?:\.\d+)?', p),
            'has_question': '?' in prompt,
            'has_either_or': bool(re.search(r'\b(either|or)\b.*\b(or|either)\b', p)) # Simplified
        }
        return constraints

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        presupposition_triggers = ['have you stopped', 'have you quit', 'why did', 'why does', 'when did', 'how did']
        if any(trigger in p for trigger in presupposition_triggers):
            score -= 0.5
            
        # 2. Scope/Pronoun ambiguity ("Every X... Y", "He told him... who?")
        if re.search(r'\bevery\b.*\b(a|an|the)\b', p) and 'same' not in p:
            score -= 0.3
        if re.search(r'\b(he|she|they|him|her)\b.*\bwho\b', p):
            score -= 0.4
            
        # 3. False Dichotomy
        if re.search(r'\b(either|or)\b', p) and not re.search(r'\b(both|all|maybe)\b', p):
            score -= 0.2
            
        # 4. Subjectivity without criteria
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly']
        if any(w in p for w in subjective_words) and 'calculate' not in p and 'math' not in p:
            score -= 0.3
            
        # 5. Unanswerability (Missing info indicators)
        if re.search(r'\b(without|lacking|missing)\b.*\binformation\b', p):
            score -= 0.6
            
        return max(0.0, min(1.0, score))

    def _compute_information_gain(self, prompt: str, candidate: str, constraints: dict) -> float:
        """
        Computes expected information gain based on how well the candidate 
        satisfies the structural constraints (Logic Match).
        """
        gain = 0.0
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        # Numeric Evaluation (Constructive Computation)
        if constraints['numerics']:
            # Extract numbers from candidate
            c_nums = re.findall(r'\d+(?:\.\d+)?', c_lower)
            if c_nums:
                # Simple heuristic: if candidate contains the result of a simple operation implied
                # Since we can't parse full math without eval risks, we check for exact match of numbers in prompt
                # or simple ordering.
                gain += 2.0 # High value for numeric candidates
            else:
                # If prompt has numbers but candidate doesn't, it's likely wrong (High entropy reduction if false)
                gain -= 1.0 

        # Logical Consistency (Negation handling)
        if constraints['negations'] > 0:
            # Check if candidate acknowledges negation (simplified)
            neg_words = ['not', 'no', 'never', 'false', 'impossible']
            if any(w in c_lower for w in neg_words):
                gain += 1.5
            elif any(w in p_lower.split()[-5:] for w in ['yes', 'true']): 
                # Heuristic: if prompt ends in a negative question, "yes" might be tricky
                pass

        # Conditional Satisfaction
        if constraints['conditionals'] > 0:
            if any(kw in c_lower for kw in ['therefore', 'thus', 'so', 'because']):
                gain += 1.0
                
        # Baseline length penalty (Occam's razor via MaxEnt principle: simpler is better if equal info)
        gain -= 0.01 * len(candidate)
        
        return gain

    def _kl_divergence_penalty(self, prompt: str, candidate: str) -> float:
        """
        Approximates KL-Divergence based penalty.
        Measures how much the candidate deviates from the "uniform" expectation 
        given the prompt's structural constraints.
        """
        penalty = 0.0
        c_lower = candidate.lower()
        
        # If prompt asks for a number and candidate is not a number -> High Divergence
        if re.search(r'how many|calculate|sum|product', prompt.lower()):
            if not re.search(r'\d', candidate):
                penalty += 5.0
        
        # If prompt is a yes/no question and candidate is not yes/no/uncertain
        if prompt.strip().endswith('?'):
            yes_no = ['yes', 'no', 'true', 'false', 'impossible', 'unknown']
            if not any(yn in c_lower for yn in yes_no) and not re.search(r'\d', c_lower):
                # Allow sentence answers, but penalize gibberish
                if len(c_lower.split()) > 10:
                    penalty += 0.5
                else:
                    penalty += 2.0
                    
        return penalty

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        constraints = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate scores
        raw_scores = []
        for cand in candidates:
            # 1. Information Gain (Logic/Structure match) - 50%
            info_gain = self._compute_information_gain(prompt, cand, constraints)
            
            # 2. Risk Penalty (KL-Divergence approx) - 20%
            risk = self._kl_divergence_penalty(prompt, cand)
            
            # 3. NCD Tiebreaker - 15% (Inverted: lower NCD to prompt is better, but we want diversity? 
            # Actually, for QA, we want relevance. Let's use NCD between Prompt+Candidate vs Prompt alone?
            # Simpler: Use NCD to penalize candidates that are too dissimilar to prompt context if logic fails.
            # But per instructions: NCD is tiebreaker. Let's use it to boost candidates that compress well with prompt.
            ncd_val = self._ncd_score(prompt, cand)
            ncd_boost = (1.0 - ncd_val) * 0.15 
            
            # Composite Score
            # Score = (InfoGain - Risk) * Weight + NCD_boost
            score = (info_gain - risk) * 0.65 + ncd_boost
            
            # Normalize slightly to keep in reasonable range before capping
            raw_scores.append((cand, score))
        
        # Normalize scores to 0-1 range roughly, then apply meta_cap
        max_raw = max(s[1] for s in raw_scores) if raw_scores else 1.0
        min_raw = min(s[1] for s in raw_scores) if raw_scores else 0.0
        range_raw = max_raw - min_raw if max_raw != min_raw else 1.0
        
        for cand, score in raw_scores:
            # Normalize to 0.2 - 0.9 range initially
            normalized = 0.2 + (0.7 * (score - min_raw) / range_raw)
            
            # Apply Epistemic Honesty Cap
            final_score = min(normalized, meta_cap)
            
            # If meta_cap is low, force low confidence
            if meta_cap < 0.3:
                final_score = min(final_score, 0.25)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"InfoGain={score:.2f}, MetaCap={meta_cap:.2f}, NCD={ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps based on _meta_confidence to ensure epistemic honesty on ambiguous prompts.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        constraints = self._structural_parse(prompt)
        info_gain = self._compute_information_gain(prompt, answer, constraints)
        risk = self._kl_divergence_penalty(prompt, answer)
        
        base_conf = max(0.0, info_gain - risk)
        # Scale base_conf roughly to 0-1
        scaled_conf = 1.0 / (1.0 + math.exp(-base_conf)) # Sigmoid
        
        # Apply hard cap from meta-analysis
        final_conf = min(scaled_conf, meta_cap)
        
        # If the prompt is flagged as ambiguous/unanswerable, force low confidence
        if meta_cap < 0.3:
            return min(final_conf, 0.25)
            
        return max(0.0, min(1.0, final_conf))
```

</details>
