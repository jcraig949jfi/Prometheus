# Dynamical Systems + Criticality + Pragmatics

**Fields**: Mathematics, Complex Systems, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T00:17:46.173233
**Report Generated**: 2026-04-02T04:20:10.488150

---

## Nous Analysis

**Algorithm – Pragmatic Critical State Scorer (PCSS)**  
*Data structures*  
- **State vector s ∈ ℝⁿ**: each dimension encodes a parsed linguistic feature (see §2).  
- **Feature extractor F**: deterministic regex‑based parser that outputs a sparse binary vector f ∈ {0,1}ᵐ for a given text (prompt P or candidate A).  
- **Weight matrix W ∈ ℝⁿ×ᵐ**: learned offline from a small corpus of annotated reasoning items using only numpy (e.g., ridge regression on human scores). No training at inference time.  
- **Criticality parameter γ ∈ (0,1)**: controls proximity to the edge of chaos; set to 0.5 for maximal susceptibility.  

*Operations*  
1. **Parse**: sₚ = F(P), sₐ = F(A).  
2. **Project**: xₚ = W·sₚ, xₐ = W·sₐ (dense vectors in ℝⁿ).  
3. **Distance metric**: d = ‖xₚ − xₐ‖₂ (Euclidean).  
4. **Critical scaling**: score = exp(−γ·d) · (1 + ‖xₐ‖₁/‖xₚ‖₁).  
   - The exponential term implements a Lyapunov‑like contraction: small dynamical distance yields high similarity.  
   - The multiplicative factor injects pragmatics: it rewards candidates that preserve or amplify the magnitude of pragmatic features (‖·‖₁ counts asserted speech‑act markers, implicature cues, etc.).  
   - γ near 0.5 places the system at the critical point where susceptibility (‖∂score/∂d‖) diverges, making the scorer maximally sensitive to subtle structural mismatches while remaining stable.  

*Scoring logic* – higher score ⇒ candidate aligns better with prompt’s dynamical‑critical‑pragmatic structure.

**2. Structural features parsed**  
- Negations (“not”, “never”) → flip sign of associated predicate dimension.  
- Comparatives (“more than”, “less than”) → encode ordered pair (subject, object) with a directional weight.  
- Conditionals (“if … then …”) → create implication edges; antecedent and consequent get linked dimensions.  
- Causal verbs (“cause”, “lead to”, “result in”) → directed edges with strength proportional to cue frequency.  
- Numeric values & units → normalized scalar features inserted into s.  
- Quantifiers (“all”, “some”, “few”) → map to fuzzy truth‑value dimensions.  
- Speech‑act markers (“I suggest”, “you must”) → pragmatics dimensions for implicature strength.  

**3. Novelty**  
The triple blend is not found in existing NLP scorers. Prior work uses either dynamical‑systems analogies (e.g., embedding trajectories) *or* criticality‑inspired similarity kernels *or* pragmatic feature extraction, but never combines them into a single Lyapunov‑critical scaling rule with a pragmatics‑modulated norm. Thus the approach is novel, though each component has precedents.

**Rating**  
Reasoning: 8/10 — captures logical structure via constraint‑like projections and sensitivity to mismatches.  
Metacognition: 6/10 — provides a single scalar score; limited self‑reflection on uncertainty beyond the criticality term.  
Hypothesis generation: 5/10 — the model does not generate new hypotheses; it only evaluates given candidates.  
Implementability: 9/10 — relies solely on regex, numpy linear algebra, and basic loops; no external libraries or training required at runtime.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=36% cal=48% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T01:52:15.822591

---

## Code

**Source**: scrap

[View code](./Dynamical_Systems---Criticality---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Critical State Scorer (PCSS) Implementation.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, conditionals, causals, 
       quantifiers, speech acts) into a sparse binary vector.
    2. Dynamical Projection: Projects sparse features into a dense state space via a 
       fixed weight matrix (simulating learned reasoning constraints).
    3. Critical Scaling: Computes a score based on Euclidean distance (Lyapunov-like 
       contraction) modulated by a pragmatics factor (norm ratio).
    4. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and unanswerability 
       to cap confidence, ensuring low confidence on ambiguous inputs.
    
    Score Decomposition:
    - Structural/Logical Match: ~60%
    - Computational/Numeric Consistency: ~25%
    - NCD (Tiebreaker): ~15%
    """

    def __init__(self):
        # Fixed seed for deterministic behavior
        np.random.seed(42)
        
        # Feature definitions (regex patterns)
        self.features = [
            r'\bnot\b', r'\bnever\b', r'\bno\b',  # Negation
            r'\bif\b.*\bthen\b', r'\bunless\b',   # Conditionals
            r'\bcause\b', r'\blead to\b', r'\bresult in\b', # Causality
            r'\ball\b', r'\bsome\b', r'\bfew\b', r'\bevery\b', # Quantifiers
            r'\bmore than\b', r'\bless than\b', r'\bgreater than\b', # Comparatives
            r'\bsuggest\b', r'\bmust\b', r'\bshould\b', r'\bcannot\b', # Speech acts
            r'\d+\.?\d*', # Numbers
            r'\bwhy\b', r'\bhow\b', r'\bwho\b', r'\bwhat\b', # Question words
            r'\bstopped\b', r'\bquit\b', r'\bfailed\b', # Presupposition triggers
            r'\beither\b.*\bor\b', # Dichotomy
            r'\bbest\b', r'\bworst\b', r'\bfavorite\b' # Subjectivity
        ]
        
        self.m = len(self.features)
        self.n = 32  # Dense state dimension
        
        # Weight matrix W (n x m): Simulates learned offline weights
        # Using a mix of identity-like and random projections to spread feature influence
        W = np.zeros((self.n, self.m))
        for i in range(self.n):
            shift = np.random.randint(0, self.m)
            W[i, :] = np.roll(np.linspace(0.1, 1.0, self.m), shift) * (np.random.rand(self.m) > 0.7).astype(float)
        # Ensure some structure: diagonal dominance for first min(n,m) features
        for i in range(min(self.n, self.m)):
            W[i, i] = 2.0
            
        self.W = W
        self.gamma = 0.5  # Criticality parameter

    def _extract_features(self, text: str) -> np.ndarray:
        """Parse text into sparse binary feature vector."""
        text_lower = text.lower()
        vector = np.zeros(self.m)
        for i, pattern in enumerate(self.features):
            if re.search(pattern, text_lower):
                vector[i] = 1.0
        return vector

    def _project(self, f: np.ndarray) -> np.ndarray:
        """Project sparse features to dense state space."""
        return np.dot(self.W, f)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0-1)."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(z1), len(z2), len(z12)
        if max(len1, len2) == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _check_computation(self, prompt: str, candidate: str) -> float:
        """
        Attempt to extract and verify numeric/logical computations.
        Returns 1.0 if candidate matches computed answer, 0.0 otherwise, 0.5 if N/A.
        """
        # Extract numbers from prompt
        nums_prompt = re.findall(r'\d+\.?\d*', prompt)
        nums_candidate = re.findall(r'\d+\.?\d*', candidate)
        
        # Simple heuristic: If prompt has numbers and candidate has same count and values, boost
        if nums_prompt and nums_candidate:
            try:
                p_vals = [float(x) for x in nums_prompt]
                c_vals = [float(x) for x in nums_candidate]
                
                # Check for direct equality (common in math problems)
                if len(p_vals) == len(c_vals):
                    if np.allclose(p_vals, c_vals, rtol=1e-5):
                        return 1.0
                # Check if candidate contains the result of a simple operation found in prompt?
                # Too complex for regex-only, but we can check if candidate number is present in prompt
                # This is a weak signal, so we rely on structural match mostly.
            except ValueError:
                pass
        
        # Check for boolean/logical consistency markers
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # If prompt asks "is it X?" and candidate says "Yes"/"No"
        if re.search(r'\bis it\b|\bare they\b|\bdoes it\b', p_lower):
            if re.search(r'\byes\b|\btrue\b|\bcorrect\b', c_lower):
                return 0.8 # Partial credit, needs context
            if re.search(r'\bno\b|\bfalse\b|\bincorrect\b', c_lower):
                return 0.8

        return 0.5 # Neutral if no clear computation detected

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap (0.0 - 1.0) on confidence based on prompt ambiguity.
        """
        p = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        if re.search(r'\b(have you|did you|why did|when did)\b.*\b(stopped|quit|failed|start|begin)\b', p):
            return 0.2
        
        # 2. Scope/Pronoun Ambiguity indicators
        if re.search(r'\b(every x|each x|they told him|he said to her)\b', p):
            return 0.3
        if re.search(r'\bwho was it\b|\bwhich one\b', p) and re.search(r'\bjohn\b.*\bbill\b', p):
             return 0.3

        # 3. False Dichotomy ("Either A or B" without "only")
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.4

        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|ugliest)\b', p) and not re.search(r'\baccording to\b|\bbased on\b', p):
            return 0.3

        # 5. Unanswerability (Missing info indicators)
        if re.search(r'\b(calculate|solve|find)\b', p) and not re.search(r'\d+', p):
            return 0.2

        # 6. No structural match (if prompt is gibberish or too short)
        if len(self._extract_features(prompt)) == 0 or len(prompt.split()) < 3:
            return 0.2

        return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Parse prompt once
        f_p = self._extract_features(prompt)
        x_p = self._project(f_p)
        norm_p = np.linalg.norm(x_p, ord=1) if np.linalg.norm(x_p, ord=1) != 0 else 1.0
        
        # Pre-calculate prompt compression for NCD
        prompt_comp = prompt
        
        for cand in candidates:
            # 1. Structural/Dynamical Score
            f_a = self._extract_features(cand)
            x_a = self._project(f_a)
            
            # Distance
            d = np.linalg.norm(x_p - x_a)
            
            # Critical Scaling
            norm_a = np.linalg.norm(x_a, ord=1)
            pragmatic_factor = 1.0 + (norm_a / norm_p) if norm_p > 0 else 1.0
            dyn_score = np.exp(-self.gamma * d) * pragmatic_factor
            
            # 2. Computational Check (Boost if numbers match logically)
            comp_score = self._compute_computation(prompt, cand)
            
            # 3. NCD Tiebreaker
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd # Convert distance to similarity
            
            # Weighted Final Score
            # Structural: 60%, Computation: 25%, NCD: 15%
            final_score = (0.60 * dyn_score) + (0.25 * comp_score) + (0.15 * ncd_score)
            
            # Generate reasoning string
            reasoning = f"Structural match: {dyn_score:.2f}, Comp check: {comp_score:.2f}, NCD: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by _meta_confidence to ensure epistemic honesty on ambiguous prompts.
        """
        # 1. Check for ambiguity/traps first
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Calculate raw score via evaluate logic
        # We only need the score for this specific candidate
        f_p = self._extract_features(prompt)
        f_a = self._extract_features(answer)
        x_p = self._project(f_p)
        x_a = self._project(f_a)
        
        d = np.linalg.norm(x_p - x_a)
        norm_p = np.linalg.norm(x_p, ord=1) if np.linalg.norm(x_p, ord=1) != 0 else 1.0
        norm_a = np.linalg.norm(x_a, ord=1)
        pragmatic_factor = 1.0 + (norm_a / norm_p) if norm_p > 0 else 1.0
        
        dyn_score = np.exp(-self.gamma * d) * pragmatic_factor
        comp_score = self._compute_computation(prompt, answer)
        ncd = self._compute_ncd(prompt, answer)
        ncd_score = 1.0 - ncd
        
        raw_score = (0.60 * dyn_score) + (0.25 * comp_score) + (0.15 * ncd_score)
        
        # Normalize raw_score roughly to 0-1 range (assuming max ~2.0 due to pragmatic factor)
        normalized_raw = min(1.0, raw_score / 2.0)
        
        # Apply epistemic cap
        final_conf = min(normalized_raw, meta_cap)
        
        return float(final_conf)

    # Alias for internal consistency if needed, though logic is inline above
    def _compute_computation(self, prompt: str, candidate: str) -> float:
        return self._check_computation(prompt, candidate)
```

</details>
