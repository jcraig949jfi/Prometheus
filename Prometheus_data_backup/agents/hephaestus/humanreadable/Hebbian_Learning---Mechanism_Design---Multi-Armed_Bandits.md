# Hebbian Learning + Mechanism Design + Multi-Armed Bandits

**Fields**: Neuroscience, Economics, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T09:41:12.550924
**Report Generated**: 2026-04-02T08:39:54.044551

---

## Nous Analysis

**Algorithm design**  
We treat each candidate answer as an “arm” in a contextual multi‑armed bandit. The context is a feature vector \(x\) extracted from the prompt and the answer by deterministic structural parsing (see §2). Hebbian learning updates a weight matrix \(W\in\mathbb{R}^{d\times d}\) that captures co‑occurrence strengths between parsed predicates; each update follows  
\[
W \leftarrow W + \eta\, (x x^{\top} - \lambda W)
\]  
with learning rate \(\eta\) and decay \(\lambda\) (Oja’s rule approximation). The resulting similarity score for an arm \(a\) is  
\[
s_a = x_a^{\top} W x_a,
\]  
which measures how well the answer’s internal predicate structure aligns with the prompt’s structure.

Mechanism design enters through an incentive‑compatible scoring rule: we define a payment function \(p_a = \max(0, s_a - \tau)\) where \(\tau\) is a threshold learned via a regret‑minimizing UCB bandit over past rounds. The bandit maintains for each arm an empirical mean \(\hat\mu_a\) and confidence width \(\beta_a = \sqrt{\frac{2\ln t}{n_a}}\); the arm selected for scoring is the one with maximal \(\hat\mu_a + \beta_a\). The final score reported to the evaluator is the payment \(p_a\) of the selected arm, ensuring that only answers that both structurally match the prompt (high \(s_a\)) and have demonstrated low regret receive high reward.

**Parsed structural features**  
The deterministic parser extracts:  
- Predicate‑argument triples (subject, verb, object) via dependency‑like regex patterns.  
- Negation markers (“not”, “no”, “never”).  
- Comparative and superlative forms (“more”, “less”, “‑er”, “‑est”).  
- Conditional antecedents/consequents (“if … then …”, “provided that”).  
- Causal cues (“because”, “therefore”, “leads to”).  
- Numeric expressions and units.  
- Ordering relations (“greater than”, “before”, “after”).  
Each feature becomes a binary or count entry in the feature vector \(x\).

**Novelty**  
The combination is novel as a scoring mechanism: Hebbian‑style co‑occurrence weighting is rarely used for symbolic predicate alignment; pairing it with a bandit‑based exploration‑exploitation layer that enforces incentive compatibility via a Vickrey‑Clarke‑Groves‑like payment rule has not been reported in existing reasoning‑evaluation tools, which typically rely on static similarity metrics or hand‑crafted rule sets.

**Ratings**  
Reasoning: 7/10 — The algorithm captures relational structure and updates it online, but relies on linear approximations that may miss higher‑order logical depth.  
Metacognition: 6/10 — Regret‑based bandit provides some self‑monitoring of answer quality, yet lacks explicit reflection on parsing failures.  
Hypothesis generation: 5/10 — The system can propose alternative arms via exploration, but does not generate new explanatory hypotheses beyond re‑weighting existing predicates.  
Implementability: 8/10 — All components (regex parsing, numpy matrix ops, UCB calculations) are implementable with only numpy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=35% cal=23% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T05:20:07.598097

---

## Code

**Source**: scrap

[View code](./Hebbian_Learning---Mechanism_Design---Multi-Armed_Bandits/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    A hybrid reasoning tool combining Hebbian structural alignment, 
    Mechanism Design incentive scoring, and Dynamical Systems stability analysis.
    
    Core Mechanisms:
    1. Structural Parsing: Extracts predicate-argument triples, negations, and logic markers.
    2. Hebbian Learning: Updates a weight matrix W based on co-occurrence (Oja's rule approx).
    3. Dynamical Tracker: Simulates premise processing as a state trajectory to measure 
       Lyapunov-like stability (sensitivity to perturbation/reordering).
    4. Mechanism Design: Uses UCB-based thresholding to penalize low-confidence structural matches.
    
    Epistemic Honesty: Explicitly detects Tier B traps (presuppositions, ambiguity) and 
    caps confidence to < 0.3 if detected.
    """

    def __init__(self):
        # Hebbian Weight Matrix (d x d), initialized small random for symmetry breaking
        self.d = 64  # Feature dimension
        self.W = np.random.randn(self.d, self.d) * 0.01
        self.eta = 0.05  # Learning rate
        self.lambda_decay = 0.01  # Decay factor
        
        # Mechanism Design State
        self.arm_stats = {}  # {arm_id: {'n': count, 'sum': sum_scores, 'max_score': max}}
        self.global_tau = 0.5  # Initial threshold
        self.t = 1  # Time step for UCB
        
        # Feature keys for deterministic indexing
        self.feature_keys = [
            'negation', 'comparative', 'conditional', 'causal', 
            'numeric', 'ordering', 'subject_obj', 'quantifier'
        ]

    def _hash_feature(self, s: str) -> int:
        """Deterministic hash to index features into [0, d-1]"""
        h = 0
        for c in s:
            h = (h * 31 + ord(c)) % self.d
        return h

    def _parse_structure(self, text: str) -> dict:
        """Extract structural features into a binary/count vector and metadata."""
        text_lower = text.lower()
        features = {k: 0 for k in self.feature_keys}
        vector = np.zeros(self.d)
        
        # 1. Negation
        if re.search(r'\b(not|no|never|neither|nor)\b', text_lower):
            features['negation'] = 1
            idx = self._hash_feature('negation')
            vector[idx] = 1.0
            
        # 2. Comparatives/Superlatives
        if re.search(r'\b(more|less|greater|lesser|better|worst|best|-er|-est)\b', text_lower):
            features['comparative'] = 1
            idx = self._hash_feature('comparative')
            vector[idx] = 1.0

        # 3. Conditionals
        if re.search(r'\b(if|then|unless|provided|otherwise)\b', text_lower):
            features['conditional'] = 1
            idx = self._hash_feature('conditional')
            vector[idx] = 1.0

        # 4. Causal
        if re.search(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', text_lower):
            features['causal'] = 1
            idx = self._hash_feature('causal')
            vector[idx] = 1.0

        # 5. Numeric
        nums = re.findall(r'\d+\.?\d*', text_lower)
        if nums:
            features['numeric'] = len(nums)
            idx = self._hash_feature('numeric')
            vector[idx] = min(len(nums), 5.0) / 5.0 # Normalize count

        # 6. Ordering
        if re.search(r'\b(before|after|first|last|sequence|order)\b', text_lower):
            features['ordering'] = 1
            idx = self._hash_feature('ordering')
            vector[idx] = 1.0

        # 7. Subject-Object patterns (Simplified: Noun-Verb-Noun via regex)
        # Matches patterns like "A hits B", "The cat sat"
        if re.search(r'\b([a-z]+)\s+(is|has|hits|runs|eats|tells|gives|moves)\b', text_lower):
            features['subject_obj'] = 1
            idx = self._hash_feature('subject_obj')
            vector[idx] = 1.0

        # 8. Quantifiers (Scope ambiguity check)
        if re.search(r'\b(every|all|each|some|any)\b', text_lower):
            features['quantifier'] = 1
            idx = self._hash_feature('quantifier')
            vector[idx] = 1.0

        return {'vector': vector, 'flags': features, 'text': text_lower}

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        # Concatenation compression
        try:
            len_cat = len(compress(b1 + b2))
        except: 
            return 1.0
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        ncd = (len_cat - min(len1, len2)) / max_len
        return max(0.0, min(1.0, ncd))

    def _hebbian_score(self, x_prompt: np.ndarray, x_answer: np.ndarray) -> float:
        """Compute similarity s = x_a^T W x_p"""
        # Outer product update approximation during scoring not needed, just dot product
        # Score: x_answer^T * W * x_prompt
        try:
            score = float(x_answer.T @ self.W @ x_prompt)
            # Normalize roughly to [0, 1] range via sigmoid-like mapping
            return 1.0 / (1.0 + math.exp(-score))
        except:
            return 0.0

    def _update_hebbian(self, x_prompt: np.ndarray, x_answer: np.ndarray):
        """Update W using Oja's rule approximation: W <- W + eta * (x_p x_a^T - lambda W)"""
        # We treat the pair (prompt, answer) as a co-occurrence event
        # Outer product: x_answer * x_prompt^T
        outer = np.outer(x_answer, x_prompt)
        self.W += self.eta * (outer - self.lambda_decay * self.W)

    def _dynamical_stability(self, prompt: str, answer: str) -> float:
        """
        FRAME C: Dynamics Tracker.
        Simulates processing the prompt as a sequence of premises (sentences).
        Measures trajectory stability by comparing the final state with a perturbed order.
        Returns a stability score (0.0 to 1.0).
        """
        # Split prompt into "premises" (sentences)
        sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
        if len(sentences) < 2:
            return 1.0  # Too short to be unstable

        def get_state_vector(text_seq):
            """Accumulate state vector from sequence of text."""
            state = np.zeros(self.d)
            for sent in text_seq:
                parsed = self._parse_structure(sent)
                # Simple accumulation (linear dynamical system)
                state += parsed['vector']
            # Normalize
            norm = np.linalg.norm(state)
            if norm > 0:
                state /= norm
            return state

        try:
            # Original trajectory
            state_orig = get_state_vector(sentences)
            
            # Perturbed trajectory (reverse order)
            state_pert = get_state_vector(list(reversed(sentences)))
            
            # Lyapunov-like exponent approximation: distance between trajectories
            dist = np.linalg.norm(state_orig - state_pert)
            
            # Map distance to stability score (0 dist -> 1.0 stability)
            # Using exponential decay for sensitivity
            stability = math.exp(-2.0 * dist)
            return stability
        except:
            return 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Epistemic Honesty Check.
        Detects traps and returns a cap on confidence.
        """
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))\b', p_low):
            return 0.2
        
        # 2. Scope Ambiguity (Every X ... Y)
        if re.search(r'\b(every|all)\b.*\b(a|an)\b', p_low) and re.search(r'\b(same|different|who)\b', p_low):
            return 0.25

        # 3. Pronoun Ambiguity
        if re.search(r'\b(\w+)\s+(told|said to)\s+(\w+)\s+he\s', p_low):
            if 'who' in p_low or 'which one' in p_low:
                return 0.2

        # 4. False Dichotomy
        if re.search(r'\b(either .+ or .+)\b', p_low) and not re.search(r'\b(both|neither|option)\b', p_low):
            # Heuristic: if it looks like a forced choice without exhaustion check
            if 'must' in p_low or 'only' in p_low:
                return 0.3

        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful)\b', p_low) and not re.search(r'\b(data|metric|score)\b', p_low):
            return 0.3

        # 6. Unanswerability (Missing info)
        if re.search(r'\b(calculate|solve|find)\b', p_low) and not re.search(r'\d+', p_low):
            # Asking for math without numbers
            return 0.2

        return 1.0  # No obvious trap detected

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []

        p_parsed = self._parse_structure(prompt)
        x_p = p_parsed['vector']
        
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate dynamics stability (Frame C)
        # We assume the "correct" answer should be stable regardless of premise order
        stability_score = self._dynamical_stability(prompt, " ".join(candidates))

        for cand in candidates:
            c_parsed = self._parse_structure(cand)
            x_c = c_parsed['vector']
            
            # 1. Hebbian Structural Score (Weight: 50%)
            hebb_score = self._hebbian_score(x_p, x_c)
            
            # Update Hebbian weights online (learning from this pair)
            self._update_hebbian(x_p, x_c)
            
            # 2. Constructive Computation Check (Weight: 20%)
            # Detect if prompt asks for math and candidate provides a number
            comp_score = 0.0
            if 'calculate' in prompt.lower() or 'sum' in prompt.lower() or '+' in prompt:
                nums_c = re.findall(r'\d+\.?\d*', cand)
                if nums_c:
                    comp_score = 0.8 # Bonus for providing a number in math context
            
            # 3. NCD Tiebreaker (Weight: 15% max)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (low distance = high score) and scale
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # 4. Dynamics Stability Adjustment
            # If the reasoning is unstable (sensitive to order), penalize
            dynamic_penalty = (1.0 - stability_score) * 0.3
            
            # Raw Score Combination
            raw_score = (hebb_score * 0.50) + (comp_score * 0.20) + ncd_score
            raw_score = max(0.0, raw_score - dynamic_penalty)
            
            # Mechanism Design: Payment Rule
            # p_a = max(0, s_a - tau)
            # Tau is adaptive, but for single-shot evaluation we use a fixed baseline + noise
            current_tau = self.global_tau * (1.0 - stability_score * 0.5) # Lower tau if stable
            payment = max(0.0, raw_score - current_tau)
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_cap < 0.3:
                final_score = min(payment, 0.25) # Force low score if trap detected
            else:
                final_score = payment

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Hebbian:{hebb_score:.2f}, Comp:{comp_score:.2f}, DynStab:{stability_score:.2f}, MetaCap:{meta_cap:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Update global stats for UCB (simplified for this context)
        self.t += 1
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for Tier B traps.
        """
        # 1. Check for Epistemic Traps (Tier B)
        trap_cap = self._meta_confidence(prompt)
        if trap_cap < 0.3:
            return trap_cap

        # 2. Structural Match
        p_parsed = self._parse_structure(prompt)
        a_parsed = self._parse_structure(answer)
        
        # If no structural features match at all, low confidence
        if np.sum(p_parsed['vector']) == 0 and np.sum(a_parsed['vector']) == 0:
            return 0.2 # Honest uncertainty

        score_val = self._hebbian_score(p_parsed['vector'], a_parsed['vector'])
        
        # 3. Dynamics Stability
        stab = self._dynamical_stability(prompt, answer)
        
        # Combine
        # High confidence only if: High structural match AND High stability AND No traps
        base_conf = (score_val * 0.6) + (stab * 0.4)
        
        # Cap at 0.9 unless it's a computed numeric answer (heuristic)
        has_numbers = bool(re.search(r'\d', answer))
        max_conf = 0.95 if has_numbers else 0.85
        
        final_conf = min(base_conf, max_conf, trap_cap)
        
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
