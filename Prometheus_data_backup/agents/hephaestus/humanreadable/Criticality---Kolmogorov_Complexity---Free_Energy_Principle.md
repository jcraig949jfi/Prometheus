# Criticality + Kolmogorov Complexity + Free Energy Principle

**Fields**: Complex Systems, Information Science, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:08:11.685511
**Report Generated**: 2026-03-27T06:37:39.457712

---

## Nous Analysis

**Algorithm**  
The scorer builds a shallow generative model of the prompt (the “Markov blanket”) and treats each candidate answer as a sensory sample whose prediction error is minimized.  

1. **Tokenization & n‑gram model** – Split prompt into lower‑cased word tokens (using `str.split()` and a regex that keeps punctuation as separate tokens). Construct a first‑order transition matrix `T` of shape `(V,V)` where `V` is vocabulary size; `T[i,j]` counts occurrences of token `j` after token `i` in the prompt. Normalize rows to obtain a predictive distribution `P(next|current)` (numpy).  

2. **Prediction error (Free Energy term)** – For each answer, tokenize similarly. Compute cross‑entropy loss:  
   `PE = - Σ log P(a_t | a_{t-1})` where missing transitions get a small epsilon (`1e-9`). Lower PE means the answer is predictable from the prompt.  

3. **Kolmogorov Complexity proxy** – Approximate algorithmic complexity with LZ78 parsing: iterate over the answer token list, maintain a dictionary of seen substrings, increment a counter each time a new substring is added. The raw count `K` is normalized by answer length `L` to get `C = K / L` (range ≈0‑1).  

4. **Criticality tuning** – Critical behavior occurs when the system is neither too ordered (low `C`) nor too disordered (high `C`). Define a critical complexity `C_crit = 0.5`. Compute a criticality weight:  
   `W = exp( -α * (C - C_crit)^2 )` with `α = 10` (tunable). `W` peaks at 1 when `C` equals the critical point and decays symmetrically.  

5. **Score** – Combine: `Score = -PE * W`. Higher scores reward answers that are both predictable from the prompt and have complexity near the critical boundary. All operations use numpy arrays for the transition matrix and vectorized log; LZ78 uses a plain dict (allowed in stdlib).  

**Structural features parsed**  
- Negations: tokens “not”, “no”, “never”.  
- Comparatives: “more”, “less”, “greater”, “fewer”, “than”.  
- Conditionals: “if”, “then”, “else”, “provided”.  
- Causal claims: “because”, “therefore”, “thus”, “hence”.  
- Numeric values: regex `\d+(\.\d+)?` extracted and converted to float for possible arithmetic checks.  
- Ordering relations: phrases “X is larger than Y”, “X precedes Y”.  

These features are captured implicitly because they affect token transitions and thus prediction error; explicit regex extraction can be added to boost PE for violations (e.g., a numeric claim contradicted in the prompt).  

**Novelty**  
Predictive‑coding scoring appears in Bayesian NLP, and Kolmogorov‑complexity regularization is known via MDL. However, explicitly enforcing operation near a critical complexity point to balance order/disorder has not been combined with a simple n‑gram blanket in a pure‑numpy scorer. The triplet is therefore novel in this context.  

**Ratings**  
Reasoning: 7/10 — captures logical predictability and complexity balance but lacks deep symbolic inference.  
Metacognition: 5/10 — the model does not monitor its own uncertainty beyond the PE term.  
Hypothesis generation: 4/10 — generates no new hypotheses; only scores given candidates.  
Implementability: 9/10 — relies solely on numpy, dicts, and regex; straightforward to code in <150 lines.  

---  
Reasoning: 7/10 — captures logical predictability and complexity balance but lacks deep symbolic inference.  
Metacognition: 5/10 — the model does not monitor its own uncertainty beyond the PE term.  
Hypothesis generation: 4/10 — generates no new hypotheses; only scores given candidates.  
Implementability: 9/10 — relies solely on numpy, dicts, and regex; straightforward to code in <150 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Kolmogorov Complexity**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Criticality + Kolmogorov Complexity: negative interaction (-0.094). Keep these concepts in separate code paths to avoid interference.
- Criticality + Free Energy Principle: strong positive synergy (+0.369). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Kolmogorov Complexity: strong positive synergy (+0.371). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: unexpected indent (line 82)

**Forge Timestamp**: 2026-03-26T10:12:24.579073

---

## Code

**Source**: scrap

[View code](./Criticality---Kolmogorov_Complexity---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    A reasoning scorer combining Criticality, Kolmogorov Complexity, and Free Energy Principle.
    
    Mechanism:
    1. Free Energy (Prediction Error): Builds a first-order Markov model (n-gram) from the prompt.
       Candidates are scored by how well their token transitions fit this model (lower cross-entropy = better).
    2. Kolmogorov Complexity: Approximated via LZ78 parsing. Measures the compressibility/complexity
       of the candidate. 
    3. Criticality: Applies a Gaussian weight centered at a critical complexity (C=0.5). 
       Answers that are too simple (ordered) or too random (disordered) are penalized.
    4. Structural Parsing: Explicitly extracts negations, comparatives, conditionals, and numeric values.
       Matches between prompt and candidate structural features boost the score, acting as the primary
       signal for logical consistency, while NCD serves as a tiebreaker for ambiguous cases.
    """
    
    def __init__(self):
        self.epsilon = 1e-9
        self.alpha = 10.0
        self.c_crit = 0.5
        # Structural keywords
        self.negations = {"not", "no", "never", "none", "neither"}
        self.comparatives = {"more", "less", "greater", "fewer", "than", "larger", "smaller", "higher", "lower"}
        self.conditionals = {"if", "then", "else", "provided", "unless", "when"}
        self.causals = {"because", "therefore", "thus", "hence", "so", "since"}
        self.number_regex = re.compile(r'-?\d+(?:\.\d+)?')

    def _tokenize(self, text):
        """Lowercase split keeping punctuation as separate tokens."""
        text = text.lower()
        # Keep words and punctuation
        tokens = re.findall(r"[\w]+|[^\w\s]", text)
        return tokens

    def _build_markov_blanket(self, prompt_tokens):
        """Construct first-order transition matrix and vocab mapping."""
        if not prompt_tokens:
            return {}, {}
        
        counts = defaultdict(lambda: defaultdict(int))
        total_counts = defaultdict(int)
        
        for i in range(len(prompt_tokens) - 1):
            curr, next_t = prompt_tokens[i], prompt_tokens[i+1]
            counts[curr][next_t] += 1
            total_counts[curr] += 1
            
        # Normalize to probabilities
        prob_matrix = {}
        for curr, nexts in counts.items():
            prob_matrix[curr] = {k: v / total_counts[curr] for k, v in nexts.items()}
            
        return prob_matrix, total_counts

    def _calc_prediction_error(self, candidate_tokens, transition_probs):
        """Calculate cross-entropy loss (Free Energy term)."""
        if not candidate_tokens:
            return 0.0
            
        pe = 0.0
        count = 0
        for i in range(len(candidate_tokens) - 1):
            curr, next_t = candidate_tokens[i], candidate_tokens[i+1]
            # Get probability, fallback to epsilon
            p = transition_probs.get(curr, {}).get(next_t, self.epsilon)
            if p == 0: p = self.epsilon
            pe -= np.log(p)
            count += 1
            
        return pe / max(count, 1)

    def _calc_kolmogorov_proxy(self, tokens):
        """LZ78-based complexity proxy."""
        if not tokens:
            return 0.0
        dictionary = set()
    current_substring = ""
        complexity = 0
        
        for token in tokens:
            current_substring += " " + token
            if current_substring not in dictionary:
                dictionary.add(current_substring)
                complexity += 1
                current_substring = ""
        
        # Normalize by length
        return complexity / max(len(tokens), 1)

    def _extract_features(self, tokens):
        """Extract structural features: negations, comparatives, conditionals, causals, numbers."""
        features = {
            'negations': 0,
            'comparatives': 0,
            'conditionals': 0,
            'causals': 0,
            'numbers': []
        }
        for t in tokens:
            if t in self.negations: features['negations'] += 1
            if t in self.comparatives: features['comparatives'] += 1
            if t in self.conditionals: features['conditionals'] += 1
            if t in self.causals: features['causals'] += 1
        
        # Extract numbers from original string representation if needed, 
        # but here we just check token match for simplicity or re-regex on joined string
        # For robustness, let's re-regex the joined tokens to catch numbers split by spaces weirdly
        text = " ".join(tokens)
        features['numbers'] = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', text)]
        
        return features

    def _structural_match_score(self, prompt_features, cand_features):
        """Score based on structural consistency."""
        score = 0.0
        
        # Logic: If prompt has a conditional, good answers often reflect that structure or answer directly.
        # Heuristic: Reward candidates that share specific structural markers with the prompt
        # unless the prompt implies a negation of the candidate's structure.
        
        # Simple overlap boost for structural tokens
        for key in ['negations', 'comparatives', 'conditionals', 'causals']:
            if prompt_features[key] > 0 and cand_features[key] > 0:
                score += 2.0 # Boost for matching structural complexity
            elif prompt_features[key] > 0 and cand_features[key] == 0:
                # Penalty if prompt has structure but candidate ignores it completely (might be too simple)
                score -= 0.5
                
        # Numeric consistency check (simplified)
        # If prompt has numbers, candidate having numbers is often good (unless it's a yes/no question)
        if len(prompt_features['numbers']) > 0:
            if len(cand_features['numbers']) > 0:
                score += 1.0
            # Check magnitude consistency if both have exactly one number (heuristic)
            if len(prompt_features['numbers']) == 1 and len(cand_features['numbers']) == 1:
                p_num = prompt_features['numbers'][0]
                c_num = cand_features['numbers'][0]
                if p_num == c_num:
                    score += 3.0 # Exact match boost
                elif abs(p_num - c_num) < 1e-6:
                    score += 3.0
                    
        return score

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_tokens = self._tokenize(prompt)
        transition_probs, _ = self._build_markov_blanket(prompt_tokens)
        prompt_features = self._extract_features(prompt_tokens)
        
        results = []
        
        for cand in candidates:
            cand_tokens = self._tokenize(cand)
            
            # 1. Free Energy (Prediction Error)
            pe = self._calc_prediction_error(cand_tokens, transition_probs)
            
            # 2. Kolmogorov Complexity Proxy
            K = self._calc_kolmogorov_proxy(cand_tokens)
            
            # 3. Criticality Weight
            # W = exp(-alpha * (C - C_crit)^2)
            W = np.exp(-self.alpha * (K - self.c_crit) ** 2)
            
            # Base Score: Negative PE * Weight (Lower PE is better, so -PE)
            # We scale PE to be comparable to structural scores
            base_score = -pe * W * 10.0 
            
            # 4. Structural Parsing Boost
            cand_features = self._extract_features(cand_tokens)
            struct_score = self._structural_match_score(prompt_features, cand_features)
            
            # 5. NCD Tiebreaker (only if structural score is neutral)
            ncd_score = 0.0
            if abs(struct_score) < 0.1:
                # Invert NCD (lower distance = higher score) and scale down
                ncd_val = self._ncd_distance(prompt, cand)
                ncd_score = (1.0 - ncd_val) * 0.5
            
            final_score = base_score + struct_score + ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"PE={pe:.2f}, Complexity={K:.2f}, Criticality_W={W:.2f}, Struct={struct_score:.1f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the top candidate score relative to a baseline."""
        # Evaluate single candidate against itself to get a relative sense? 
        # No, confidence usually implies certainty of correctness.
        # We simulate by checking if this answer ranks highly if we assume it's the only one?
        # Instead, we map the internal score to 0-1 based on heuristics.
        
        # Re-run evaluation with a dummy set to normalize? Too expensive.
        # Use the raw components to estimate confidence.
        
        prompt_tokens = self._tokenize(prompt)
        cand_tokens = self._tokenize(answer)
        transition_probs, _ = self._build_markov_blanket(prompt_tokens)
        
        pe = self._calc_prediction_error(cand_tokens, transition_probs)
        K = self._calc_kolmogorov_proxy(cand_tokens)
        W = np.exp(-self.alpha * (K - self.c_crit) ** 2)
        
        prompt_feats = self._extract_features(prompt_tokens)
        cand_feats = self._extract_features(cand_tokens)
        struct = self._structural_match_score(prompt_feats, cand_feats)
        
        # Heuristic mapping to 0-1
        # Low PE is good (negative), High Struct is good
        raw = (-pe * 5.0) + struct + (W * 2.0)
        
        # Sigmoid-like mapping
        conf = 1 / (1 + np.exp(-raw))
        return float(np.clip(conf, 0.0, 1.0))
```

</details>
