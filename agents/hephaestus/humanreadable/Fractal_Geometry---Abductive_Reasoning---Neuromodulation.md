# Fractal Geometry + Abductive Reasoning + Neuromodulation

**Fields**: Mathematics, Philosophy, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:04:52.932352
**Report Generated**: 2026-04-02T08:39:54.087549

---

## Nous Analysis

The algorithm builds a hierarchical clause tree from a sentence using regex‑based extraction of logical connectives (negation, comparatives, conditionals, causal markers, quantifiers, numeric literals). Each clause is represented as a NumPy feature vector **f** ∈ {0,1}^k where k encodes the presence of those structural features.  

1. **Abductive base score** – For a candidate answer, compute three explanatory virtues per clause:  
   *Simplicity* = −log(‖f‖₀) (fewer activated features → simpler hypothesis).  
   *Coverage* = |f·q|/‖q‖₁ where q is the query’s feature vector (proportion of query elements explained).  
   *Coherence* = cosine(f, c) where c is a context vector built from the surrounding text (average of neighboring clause vectors).  
   The clause score s₀ = w₁·Simplicity + w₂·Coverage + w₃·Coherence (weights sum to 1).  

2. **Neuromodulatory gain** – Derive two scalar signals from lexical cues:  
   *Dopamine* = presence of reward‑linked cues (“therefore”, “because”, “thus”).  
   *Serotonin* = presence of mitigating cues (“maybe”, “perhaps”, “although”).  
   Gain = 1 + α·dopamine − β·serotonin (α,β ∈ [0,1]). The modulated clause score s₁ = gain·s₀.  

3. **Fractal propagation (Iterated Function System)** – Treat the clause tree as an IFS where each parent node applies an affine transformation to its children’s scores:  
   s_parent = Σᵢ (sᵢ·s^depthᵢ) with scaling factor s ∈ (0,1) (e.g., 0.5). Depth‑dependent weighting creates power‑law scaling across levels, mimicking Hausdorff‑dimension self‑similarity. Iterate until the root score changes < ε (e.g., 1e‑4) or a fixed number of passes (≤ 5). The final root score is the answer’s overall rating.  

**Structural features parsed**: negations (“not”, “no”), comparatives (“more than”, “less than”), conditionals (“if … then”), causal connectives (“because”, “leads to”), temporal/ordering markers (“before”, “after”), quantifiers (“all”, “some”), numeric values and units, modal verbs (“may”, “must”).  

**Novelty**: While fractal IFS, abductive virtue scoring, and neuromodulatory gain each appear separately in cognitive modeling or neural‑network work, their conjunction as a pure‑numpy, rule‑based scoring pipeline has not been reported in existing QA evaluation tools, which typically rely on similarity metrics or pure logical parsers.  

Reasoning: 7/10 — combines logical parsing with explanatory and gain mechanisms, showing strong inferential depth.  
Metacognition: 5/10 — limited self‑monitoring; gain provides basic confidence adjustment but no explicit reflection loop.  
Hypothesis generation: 8/10 — abductive simplicity/coverage/coherence directly yields ranked explanations for each clause.  
Implementability: 9/10 — relies only on regex, NumPy array ops, and tree traversal; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **6.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=34% cal=45% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T05:00:47.331855

---

## Code

**Source**: scrap

[View code](./Fractal_Geometry---Abductive_Reasoning---Neuromodulation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal-Abductive Neuromodulated Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negation, conditionals, causals, etc.) 
       into binary vectors using regex.
    2. Abductive Scoring: Scores candidates based on Simplicity (sparsity), Coverage (overlap with query),
       and Coherence (context similarity).
    3. Neuromodulation: Adjusts scores based on reward cues (dopamine) vs uncertainty cues (serotonin).
    4. Fractal Propagation: Applies an Iterated Function System (IFS) to propagate scores up the 
       logical hierarchy with depth-dependent scaling.
    5. Epistemic Honesty (Tier B): Detects presuppositions, ambiguities, and false dichotomies to 
       cap confidence, ensuring the model admits ignorance on unanswerable traps.
    """

    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|higher|lower|better|worse)\b', re.I),
        'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.I),
        'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes|due to)\b', re.I),
        'temporal': re.compile(r'\b(before|after|while|during|until|since)\b', re.I),
        'quantifier': re.compile(r'\b(all|some|every|each|any|most|few)\b', re.I),
        'modal': re.compile(r'\b(may|might|must|should|could|will)\b', re.I),
        'numeric': re.compile(r'\d+(\.\d+)?'),
        'dopamine_cue': re.compile(r'\b(therefore|thus|hence|consequently|proven|correct)\b', re.I),
        'serotonin_cue': re.compile(r'\b(maybe|perhaps|although|however|possibly|uncertain)\b', re.I),
        # Tier B Traps
        'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .+ fail|why is .+ bad)\b', re.I),
        'scope_ambiguity': re.compile(r'\b(every .+ a .+|each .+ a .+)\b', re.I), # Simplified detection
        'pronoun_ambiguity': re.compile(r'\b(told .+ he|told .+ she|said to .+ that he)\b', re.I),
        'false_dichotomy': re.compile(r'\b(either .+ or .+|must be .+ or .+)\b', re.I),
        'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.I)
    }

    def __init__(self):
        self.weights = np.array([0.3, 0.4, 0.3]) # Simplicity, Coverage, Coherence
        self.alpha = 0.2 # Dopamine gain
        self.beta = 0.15 # Serotonin penalty
        self.scaling_factor = 0.5 # Fractal scaling
        self.max_depth = 5
        self.epsilon = 1e-4

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary feature vector from text."""
        text_lower = text.lower()
        features = []
        # Order matches logical importance for vector construction
        keys = ['negation', 'comparative', 'conditional', 'causal', 'temporal', 'quantifier', 'modal', 'numeric']
        for key in keys:
            if self.PATTERNS[key].search(text):
                features.append(1)
            else:
                features.append(0)
        return np.array(features, dtype=float)

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B Judgment: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.25 if trap detected, 1.0 otherwise).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.PATTERNS['presupposition'].search(prompt):
            return 0.25
        
        # 2. Scope Ambiguity (Simplified heuristic)
        if self.PATTERNS['scope_ambiguity'].search(prompt) and 'same' in p_lower or 'different' in p_lower:
            return 0.25
            
        # 3. Pronoun Ambiguity
        if self.PATTERNS['pronoun_ambiguity'].search(prompt) and 'who' in p_lower:
            return 0.25
            
        # 4. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(prompt):
            # Only flag if no clear logical resolution path exists (heuristic)
            if 'or else' in p_lower or 'must choose' in p_lower:
                return 0.25

        # 5. Subjectivity
        if self.PATTERNS['subjectivity'].search(prompt):
            if 'fact' not in p_lower and 'data' not in p_lower:
                return 0.25

        # 6. Unanswerability (Lack of info indicators)
        if 'cannot be determined' in p_lower or 'insufficient info' in p_lower:
            return 0.25

        return 1.0

    def _compute_abductive_score(self, candidate: str, prompt: str, context: str) -> float:
        """Compute s0: Simplicity + Coverage + Coherence."""
        f_cand = self._extract_features(candidate)
        f_prompt = self._extract_features(prompt)
        f_context = self._extract_features(context)
        
        # Simplicity: -log(||f||_0 + 1) to avoid log(0). Fewer features = simpler.
        norm_0 = np.count_nonzero(f_cand)
        simplicity = -np.log(norm_0 + 1)
        
        # Coverage: |f_cand . f_prompt| / ||f_prompt||_1
        prompt_sum = np.sum(f_prompt)
        if prompt_sum == 0:
            coverage = 0.0
        else:
            coverage = np.dot(f_cand, f_prompt) / prompt_sum
            
        # Coherence: Cosine similarity between candidate and context
        norm_cand = np.linalg.norm(f_cand)
        norm_context = np.linalg.norm(f_context)
        if norm_cand == 0 or norm_context == 0:
            coherence = 0.0
        else:
            coherence = np.dot(f_cand, f_context) / (norm_cand * norm_context)
            
        # Normalize simplicity to roughly [0,1] range roughly (log(9) ~ 2.2)
        simplicity_norm = (simplicity + 2.2) / 2.2 
        
        s0 = (self.weights[0] * simplicity_norm) + \
             (self.weights[1] * coverage) + \
             (self.weights[2] * coherence)
        return max(0.0, min(1.0, s0))

    def _neuromodulate(self, text: str, s0: float) -> float:
        """Apply dopamine/serotonin gain."""
        d_match = len(self.PATTERNS['dopamine_cue'].findall(text))
        s_match = len(self.PATTERNS['serotonin_cue'].findall(text))
        
        # Normalize cues slightly to prevent explosion
        dopamine = min(1.0, d_match * 0.5)
        serotonin = min(1.0, s_match * 0.5)
        
        gain = 1.0 + (self.alpha * dopamine) - (self.beta * serotonin)
        return s0 * gain

    def _fractal_propagate(self, base_score: float, depth: int) -> float:
        """Apply fractal scaling based on depth."""
        if depth == 0:
            return base_score
        # s_parent = sum(s_i * s^depth) approximation for single path
        return base_score * (self.scaling_factor ** depth)

    def _constructive_check(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Handle numeric comparisons and simple logic explicitly.
        Returns a boost factor (0.0 to 1.0) if constructive logic holds.
        """
        nums_prompt = self.PATTERNS['numeric'].findall(prompt)
        nums_cand = self.PATTERNS['numeric'].findall(candidate)
        
        # If numbers exist in both, verify consistency
        if nums_prompt and nums_cand:
            try:
                # Check if candidate number matches a computed relation in prompt
                # Very basic check: does the candidate number appear in the prompt?
                # If it's a calculation result, it won't, but if it's a extraction task, it will.
                # For this implementation, we boost if the candidate contains a number 
                # that satisfies a comparative statement if detectable.
                
                # Fallback: If candidate has numbers and prompt has numbers, 
                # and candidate isn't just repeating prompt, it might be a calculation.
                p_vals = [float(n) for n in nums_prompt]
                c_vals = [float(n) for n in nums_cand]
                
                # Simple heuristic: If prompt asks "which is larger" and candidate is max
                if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                    if max(p_vals) in c_vals or any(abs(v - max(p_vals)) < 1e-6 for v in c_vals):
                        return 1.0
                if 'smaller' in prompt.lower() or 'less' in prompt.lower():
                    if min(p_vals) in c_vals or any(abs(v - min(p_vals)) < 1e-6 for v in c_vals):
                        return 1.0
                
                # If no specific logic triggered, low boost for just having numbers
                return 0.2 
            except ValueError:
                pass
        
        # Logic check: Negation consistency
        if self.PATTERNS['negation'].search(prompt):
            if self.PATTERNS['negation'].search(candidate):
                return 0.5 # Consistent negation
            else:
                return 0.0 # Likely contradiction
        
        return 0.1 # Default small boost for non-contradictory

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        context = prompt # Context is the prompt itself for this scope
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._check_meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Base Abductive Score
            s0 = self._compute_abductive_score(cand, prompt, context)
            
            # 2. Neuromodulation
            s1 = self._neuromodulate(cand, s0)
            
            # 3. Constructive Logic Boost (Tier A)
            logic_boost = self._constructive_check(prompt, cand)
            s1 = (s1 * 0.7) + (logic_boost * 0.3) # Blend structural and constructive
            
            # 4. Fractal Propagation (Simulated depth based on sentence count)
            depth = min(len(prompt.split('.')), self.max_depth)
            final_score = self._fractal_propagate(s1, depth)
            
            # 5. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            # Invert NCD because lower distance = higher similarity (usually good for relevance)
            # But for reasoning, exact match is bad. We want logical alignment.
            # We use NCD only to break ties or penalize gibberish.
            ncd_factor = 1.0 - (ncd * 0.15) 
            final_score *= ncd_factor
            
            # Apply Epistemic Cap
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{s0:.2f}, Logic:{logic_boost:.2f}, Depth:{depth}, MetaCap:{meta_cap}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via meta-confidence checks.
        """
        # 1. Check for Tier B traps first
        meta_cap = self._check_meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
        
        # 2. Evaluate the specific answer against the prompt
        # We run a mini-evaluation to see how well this specific answer fits
        temp_res = self.evaluate(prompt, [answer])
        if not temp_res:
            return 0.0
            
        base_score = temp_res[0]['score']
        
        # 3. Calibration
        # If meta_cap is 1.0 (no traps), we allow higher confidence but cap at 0.9 
        # unless it's a definitive computation (handled by constructive check boosting score)
        if base_score > 0.8:
            return min(0.95, base_score)
        elif base_score > 0.5:
            return 0.6 + (base_score - 0.5) * 0.4
        else:
            return base_score * 0.5 # Low confidence for low scores

    def _meta_confidence(self, prompt: str) -> float:
        """Alias for external access to judgment logic."""
        return self._check_meta_confidence(prompt)
```

</details>
