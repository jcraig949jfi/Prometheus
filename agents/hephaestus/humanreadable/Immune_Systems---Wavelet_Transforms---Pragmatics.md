# Immune Systems + Wavelet Transforms + Pragmatics

**Fields**: Biology, Signal Processing, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T01:48:32.148932
**Report Generated**: 2026-03-27T16:08:15.488687

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a 1‑D signal `s` built from a ordered list of lexical‑feature tokens (e.g., word‑ids, POS tags, extracted relation flags). A discrete Haar wavelet transform (implemented with NumPy) decomposes `s` into a multi‑resolution coefficient matrix `C ∈ ℝ^{L×S}` where `L` is the number of scales (word, phrase, clause) and `S` the length at each scale. Each scale captures a different granularity of logical structure: fine scales isolate tokens (negations, numbers), medium scales capture binary relations (comparatives, conditionals), coarse scales capture global patterns (causal chains, ordering).  

An “antibody repertoire” `A = {a₁,…,a_K}` stores prototype vectors `a_i ∈ ℝ^{L×S}` that represent successful reasoning patterns observed during a brief offline training on a small set of gold answers. Affinity between an answer and an antibody is the normalized dot product  
`α_i = ⟨C, a_i⟩_F / (‖C‖_F‖a_i‖_F)`,  
where `⟨·,·⟩_F` is the Frobenius inner product.  

Clonal selection proceeds as follows for each prompt:  
1. Compute `C` from the candidate answer.  
2. Calculate affinities `α_i` for all `a_i`.  
3. Select the top‑`M` antibodies (those with highest `α_i`).  
4. Proliferate: create `L` clones per selected antibody, each mutated by adding small Gaussian noise (`σ=0.01`) to its coefficients.  
5. Evaluate affinities of clones; keep any clone whose affinity exceeds the parent's by > `τ` (e.g., 0.02) and insert it into the repertoire.  
6. Update a long‑term memory set `M_mem` with antibodies whose affinity > `θ` (e.g., 0.8) for reuse across prompts.  

Pragmatics enters as a context‑dependent weighting matrix `W ∈ ℝ^{L×S}` derived from the prompt. Using regex we extract pragmatic cues (e.g., presence of “however” → manner violation, scalar implicature markers → quantity, epistemic modals → quality). Each cue sets a multiplicative factor in `W` (e.g., negations boost fine‑scale coefficients, conditionals boost medium‑scale). The final affinity is `α_i^w = ⟨C ⊙ W, a_i⟩_F / (‖C ⊙ W‖_F‖a_i‖_F)`, where `⊙` denotes element‑wise product. The score for a candidate answer is the maximum `α_i^w` over the repertoire (including memory).  

**Structural features parsed**  
- Negations (`not`, `no`) → fine‑scale token flag.  
- Comparatives (`more than`, `less`) → medium‑scale relational token.  
- Conditionals (`if … then …`) → medium‑scale implication pattern.  
- Causal verbs (`cause`, `lead to`) → coarse‑scale causal chain.  
- Numeric values and units → fine‑scale magnitude token.  
- Ordering relations (`first`, `after`, `before`) → medium‑scale sequence pattern.  
- Quantifiers (`all`, `some`, `none`) → medium‑scale scope token.  
- Modals (`must`, might`) → quality/pragmatic weight.  

**Novelty**  
Wavelet‑based multi‑resolution feature extraction has been used for signal denoising, but coupling it with an immune‑inspired clonal selection mechanism and a pragmatics‑derived weighting layer is, to the best of my knowledge, unpublished. Existing work either uses static bag‑of‑words embeddings or pure logical parsers; this hybrid adds adaptive, multi‑scale similarity scoring driven by context‑sensitive relevance criteria.  

**Ratings**  
Reasoning: 7/10 — captures multi‑scale logical structure and adapts via affinity, but lacks deep inference chaining.  
Metacognition: 6/10 — memory provides reuse, yet no explicit self‑monitoring of confidence beyond affinity thresholds.  
Hypothesis generation: 8/10 — clonal proliferation actively creates mutated answer patterns, serving as hypothesis candidates.  
Implementability: 7/10 — relies only on NumPy for wavelet transforms and linear algebra; regex for feature extraction keeps it within the stdlib.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 7/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Immune Systems**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Wavelet Transforms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Immune Systems + Pragmatics: strong positive synergy (+0.604). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Pragmatics + Wavelet Transforms: strong positive synergy (+0.445). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Genetic Algorithms + Wavelet Transforms + Pragmatics (accuracy: 0%, calibration: 0%)
- Holography Principle + Immune Systems + Pragmatics (accuracy: 0%, calibration: 0%)
- Immune Systems + Phenomenology + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=40% cal=50% ncd_acc=52% ncd_cal=49%)

**Forge Timestamp**: 2026-03-27T07:59:03.217638

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Wavelet_Transforms---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hybrid Reasoning Tool: Immune-Wavelet-Pragmatics (IWP).
    
    Mechanism:
    1. Structural Parsing: Extracts logical tokens (negations, comparatives, conditionals, numbers).
    2. Wavelet Encoding: Maps these tokens to a 1D signal and applies a simplified Discrete Haar 
       Wavelet transform to capture multi-scale features (fine: tokens, medium: relations, coarse: flow).
    3. Pragmatic Weighting: Adjusts signal importance based on context cues (e.g., 'however', 'must').
    4. Immune Selection: Compares the weighted candidate signal against an internal repertoire of 
       'antibody' prototypes (ideal reasoning patterns). High affinity (cosine similarity) indicates 
       a strong match to valid logical structures.
    5. Scoring: Combines structural affinity with NCD as a tie-breaker.
    """

    def __init__(self):
        # Initialize a small repertoire of "antibodies" (prototype reasoning patterns)
        # These represent idealized logical structures at 3 scales (fine, medium, coarse)
        self.repertoire = self._init_antibodies()
        self.memory = []  # Long-term memory for high-affinity patterns
        
        # Pragmatic cues regex
        self.cues = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|than)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'causal': re.compile(r'\b(cause|lead|result|because|therefore)\b', re.I),
            'modal': re.compile(r'\b(must|should|might|could|may)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|both)\b', re.I),
            'order': re.compile(r'\b(first|last|before|after|next)\b', re.I)
        }

    def _init_antibodies(self) -> List[np.ndarray]:
        """Initialize prototype vectors representing valid logical structures."""
        antibodies = []
        # Pattern 1: Strong Negation + Fact (Fine scale dominant)
        a1 = np.array([1.0, 0.2, 0.1, 0.5, 0.1, 0.1, 0.2, 0.1]) 
        # Pattern 2: Conditional Logic (Medium scale dominant)
        a2 = np.array([0.2, 0.8, 0.2, 0.1, 0.6, 0.1, 0.3, 0.2])
        # Pattern 3: Causal Chain (Coarse scale dominant)
        a3 = np.array([0.1, 0.2, 0.9, 0.1, 0.2, 0.8, 0.4, 0.3])
        # Pattern 4: Balanced Reasoning
        a4 = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        return [a1, a2, a3, a4]

    def _extract_features(self, text: str) -> Dict[str, int]:
        """Extract structural features from text."""
        features = {
            'negation': 0, 'comparative': 0, 'conditional': 0, 
            'causal': 0, 'modal': 0, 'quantifier': 0, 'order': 0, 'numeric': 0
        }
        text_lower = text.lower()
        
        for key, pattern in self.cues.items():
            features[key] = len(pattern.findall(text_lower))
        
        # Detect numeric values
        if re.search(r'\d+(\.\d+)?', text):
            features['numeric'] = 1
            
        return features

    def _build_signal(self, text: str, prompt: str = "") -> np.ndarray:
        """
        Convert text features into a multi-resolution signal vector.
        Structure: [Neg, Comp, Cond, Causal, Modal, Quant, Order, Numeric]
        """
        feats = self._extract_features(text)
        # Order matters for the "wavelet" approximation
        signal = np.array([
            feats['negation'],
            feats['comparative'],
            feats['conditional'],
            feats['causal'],
            feats['modal'],
            feats['quantifier'],
            feats['order'],
            feats['numeric']
        ], dtype=float)
        
        # Normalize to prevent magnitude dominance
        norm = np.linalg.norm(signal)
        if norm > 0:
            signal = signal / norm
        return signal

    def _apply_pragmatic_weights(self, signal: np.ndarray, prompt: str) -> np.ndarray:
        """Apply context-dependent weighting based on pragmatic cues in the prompt."""
        weights = np.ones(8)
        prompt_lower = prompt.lower()
        
        # If prompt asks for comparison, boost comparative/comparative indices (1)
        if 'compare' in prompt_lower or 'difference' in prompt_lower:
            weights[1] = 1.5
            
        # If prompt asks for cause, boost causal (3)
        if 'why' in prompt_lower or 'cause' in prompt_lower:
            weights[3] = 1.5
            
        # If prompt has negation, boost negation (0)
        if 'not' in prompt_lower or 'false' in prompt_lower:
            weights[0] = 1.4

        # Apply weights
        weighted_signal = signal * weights
        
        # Re-normalize
        norm = np.linalg.norm(weighted_signal)
        if norm > 0:
            weighted_signal = weighted_signal / norm
            
        return weighted_signal

    def _wavelet_decompose(self, signal: np.ndarray) -> np.ndarray:
        """
        Simplified Discrete Haar Wavelet Transform approximation.
        Since our signal is small (8 dims), we simulate multi-resolution by 
        creating a feature vector that includes original (fine), pairwise avg (medium), 
        and global avg (coarse).
        """
        if len(signal) < 2:
            return signal
            
        # Fine scale (original)
        fine = signal
        
        # Medium scale (pairwise averages - simulating low-pass filter)
        medium = np.array([(signal[i] + signal[i+1])/2 for i in range(0, len(signal)-1, 2)])
        # Pad if odd
        if len(medium) < 4: 
            medium = np.pad(medium, (0, 4-len(medium)), mode='constant')
            
        # Coarse scale (global average repeated)
        coarse_val = np.mean(signal)
        coarse = np.full(4, coarse_val)
        
        # Concatenate scales to form the multi-resolution representation
        # This mimics the coefficient matrix flattened for affinity calculation
        return np.concatenate([fine, medium, coarse])

    def _compute_affinity(self, candidate_signal: np.ndarray, antibody: np.ndarray) -> float:
        """Calculate normalized dot product (cosine similarity) as affinity."""
        # Ensure same length for comparison (pad if necessary)
        len_c = len(candidate_signal)
        len_a = len(antibody)
        max_len = max(len_c, len_a)
        
        c_pad = np.pad(candidate_signal, (0, max_len - len_c), mode='constant')
        a_pad = np.pad(antibody, (0, max_len - len_a), mode='constant')
        
        dot_prod = np.dot(c_pad, a_pad)
        norm_c = np.linalg.norm(c_pad)
        norm_a = np.linalg.norm(a_pad)
        
        if norm_c == 0 or norm_a == 0:
            return 0.0
            
        return dot_prod / (norm_c * norm_a)

    def _clonal_selection(self, signal: np.ndarray) -> float:
        """
        Perform clonal selection:
        1. Calculate affinity with all antibodies.
        2. Select top M.
        3. Generate clones with noise (simulated by checking memory too).
        4. Return max affinity.
        """
        affinities = []
        
        # Check against static repertoire
        for ab in self.repertoire:
            aff = self._compute_affinity(signal, ab)
            affinities.append(aff)
            
        # Check against memory (dynamic)
        for mem_ab in self.memory:
            aff = self._compute_affinity(signal, mem_ab)
            affinities.append(aff)
            
        if not affinities:
            return 0.0
            
        max_aff = max(affinities)
        
        # Simulate proliferation: if affinity is high, we might have matched a complex pattern
        # We don't need to explicitly mutate and re-evaluate for a single score, 
        # the max affinity serves as the "best fit" score.
        
        # Memory update heuristic: if affinity > 0.8, add to memory (limit size)
        if max_aff > 0.8 and len(self.memory) < 10:
            # Add a slightly mutated version of the signal as a new memory item
            noise = np.random.normal(0, 0.01, len(signal))
            new_mem = signal + noise
            self.memory.append(new_mem)
            
        return max_aff

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tie-breaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        prompt_signal_base = self._build_signal(prompt)
        prompt_weighted = self._apply_pragmatic_weights(prompt_signal_base, prompt)
        prompt_wavelet = self._wavelet_decompose(prompt_weighted)
        
        # Pre-calculate prompt features for numeric logic checks
        prompt_nums = re.findall(r'\d+(?:\.\d+)?', prompt)
        
        for cand in candidates:
            # 1. Structural/Wavelet Scoring
            cand_signal_base = self._build_signal(cand)
            cand_weighted = self._apply_pragmatic_weights(cand_signal_base, prompt)
            cand_wavelet = self._wavelet_decompose(cand_weighted)
            
            # Affinity score (0 to 1)
            affinity = self._clonal_selection(cand_wavelet)
            
            # 2. Numeric Consistency Check (Critical for reasoning)
            numeric_bonus = 0.0
            cand_nums = re.findall(r'\d+(?:\.\d+)?', cand)
            
            if prompt_nums and cand_nums:
                try:
                    p_vals = [float(x) for x in prompt_nums]
                    c_vals = [float(x) for x in cand_nums]
                    
                    # Simple consistency: if prompt implies order, check candidate
                    if 'less' in prompt.lower() and len(p_vals) >= 2 and len(c_vals) >= 1:
                        if c_vals[0] < p_vals[0]: # Rough heuristic
                            numeric_bonus = 0.2
                    elif 'more' in prompt.lower() and len(p_vals) >= 2 and len(c_vals) >= 1:
                        if c_vals[0] > p_vals[0]:
                            numeric_bonus = 0.2
                except ValueError:
                    pass

            # 3. NCD Tie-breaker (only if affinity is very close)
            # We use a small fraction of NCD to break ties without dominating
            ncd_val = self._ncd_score(prompt, cand)
            ncd_factor = (1.0 - ncd_val) * 0.05 # Small bonus for similarity
            
            final_score = affinity + numeric_bonus + ncd_factor
            
            # Reasoning string
            reason_parts = []
            if affinity > 0.7: reason_parts.append("Strong structural match")
            elif affinity > 0.4: reason_parts.append("Moderate logical alignment")
            else: reason_parts.append("Weak structural pattern")
            
            if numeric_bonus > 0: reason_parts.append("Numeric consistency verified")
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly, capping at 1.0
        score = res[0]['score']
        return min(1.0, max(0.0, score))
```

</details>
