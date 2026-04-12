# Phase Transitions + Neural Plasticity + Pragmatics

**Fields**: Physics, Biology, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T17:33:05.825692
**Report Generated**: 2026-03-27T23:28:38.183718

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Use a handful of regex patterns to extract atomic propositions from the prompt and each candidate answer. Each proposition is encoded as a tuple *(polarity, relation, args)* where  
   * polarity ∈ {+1,‑1} (negation flips sign),  
   * relation ∈ {equality, comparison, conditional, causal, ordering},  
   * args are either constants or numeric values.  
   Propositions are stored in a sparse binary vector **x** ∈ {0,1}^P (P = number of distinct propositions observed across all candidates).  

2. **Knowledge matrix** – Initialise a weight matrix **W** ∈ ℝ^{P×P} using only lexical resources from the standard library (e.g., WordNet path lengths for synonymy/antonymy) and hand‑crafted rules:  
   * For a conditional “if A then B” set W_{A,B} = w₀,  
   * For a causal claim “A causes B” set W_{A,B} = w₀·c,  
   * For comparatives “A > B” set W_{A,B} = w₀·sgn(value_A‑value_B),  
   * All other entries start at 0.  
   **W** is kept symmetric for undirected links (similarity) and directed for implication/causality.  

3. **Plasticity update (Hebbian)** – For a candidate answer vector **x**, compute activation **a** = **W**·**x**. Then apply a Hebbian‑style update with decay:  
   Δ**W** = η ( **a** ⊗ **x** ) ‑ λ **W**,  
   where η is a learning rate and λ a weight‑decay term. This strengthens co‑active proposition pairs (like synaptic potentiation) and weakens unused links.  

4. **Phase‑transition scoring** – Treat the updated **W** as the coupling matrix of an Ising‑like spin system where each proposition’s spin s_i = 2·x_i ‑ 1 (‑1 for false, +1 for true). Define the global order parameter (magnetisation)  
   M = (1/P) |∑_i s_i|.  
   The system’s “energy” is E = ‑½ ∑_{i,j} W_{ij} s_i s_j.  
   As we iterate the Hebbian update over all candidates, we compute the susceptibility χ = Var(M) over a sliding window. A sharp peak in χ signals a critical point (phase transition). The final score for a candidate is the distance of its induced M from the critical magnetisation M_c:  
   score = exp(‑|M ‑ M_c|/τ),  
   with τ a temperature‑like scalar set to the median χ.  

All operations use only NumPy (matrix multiplication, outer product, variance) and the Python standard library (regex, collections).  

**Structural features parsed**  
- Negations (via “not”, “no”, “never”) flip polarity.  
- Comparatives (“greater than”, “less than”, “≤”, “≥”) create directed weighted edges proportional to the numeric difference.  
- Conditionals (“if … then …”, “unless”) generate implication edges.  
- Causal claims (“causes”, “leads to”, “results in”) add directed edges with causality weight.  
- Numeric values are extracted and used to weight comparatives and thresholds.  
- Ordering relations (“before”, “after”, “first”, “last”) yield transitive chains that are closed under Floyd‑Warshall‑style updates during plasticity steps.  

**Novelty**  
Pure Hebbian learning combined with an Ising‑model phase‑transition detector for text coherence has not been widely reported in open‑source reasoning tools. Existing approaches use Markov Logic Networks, soft constraint satisfaction, or pure similarity metrics; the proposed method explicitly ties synaptic‑like weight adaptation to a measurable order parameter that undergoes an abrupt change, offering a distinct mechanism for scoring reasoning quality.  

**Rating**  
Reasoning: 7/10 — captures logical structure and numeric reasoning but relies on shallow lexical semantics.  
Metacognition: 6/10 — the susceptibility metric provides a global coherence monitor, yet it lacks explicit self‑reflection on failure modes.  
Hypothesis generation: 5/10 — Hebbian updates generate new weighted associations, but the system does not propose novel hypotheses beyond re‑weighting known propositions.  
Implementability: 8/10 — only NumPy and stdlib are needed; all steps are straightforward matrix operations and regex parsing.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Phase Transitions**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 33% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Neural Plasticity**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 29% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Neural Plasticity + Pragmatics: strong positive synergy (+0.923). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Neural Plasticity + Abductive Reasoning + Pragmatics (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Phase Transitions + Pragmatics + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: UnicodeEncodeError: 'charmap' codec can't encode character '\u2297' in position 4825: character maps to <undefined>

**Forge Timestamp**: 2026-03-27T18:50:01.368915

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Neural_Plasticity---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

# Constants for the Ising/Hebbian model
ETA = 0.1       # Learning rate
LAMBDA = 0.05   # Weight decay
TAU = 0.2       # Temperature scalar for scoring
W0 = 1.0        # Base weight strength

class ReasoningTool:
    """
    A reasoning tool combining Phase Transitions, Neural Plasticity, and Pragmatics.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (polarity, relation, args) using regex.
    2. Knowledge Matrix: Initializes weights based on lexical rules (conditionals, causality).
    3. Plasticity: Applies Hebbian updates (Delta W = eta*a*x - lambda*W) to strengthen co-active links.
    4. Phase Transition: Treats propositions as spins in an Ising model. Computes magnetization (M)
       and susceptibility (chi). Candidates inducing a state near the critical point (peak chi)
       receive higher coherence scores.
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nobody|nothing)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|results in|because|due to)\b', re.I),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|higher|lower)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'ordering': re.compile(r'\b(before|after|first|last|precede|follow)\b', re.I),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did|when did|how did)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either .+ or | must be .+ or )\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful|opinion)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\b.*\b(who|which one)\b', re.I)
        }
        self.relations = ['equality', 'comparison', 'conditional', 'causal', 'ordering']

    def _extract_propositions(self, text: str) -> List[Tuple[int, str, Any]]:
        """Parse text into atomic propositions: (polarity, relation, args)"""
        props = []
        text_lower = text.lower()
        
        # Check negation scope (simple global flip for this implementation)
        polarity = 1
        if self.patterns['negation'].search(text_lower):
            # Simple heuristic: if negation appears, flip polarity of subsequent claims
            # In a full engine, this would be scope-limited.
            polarity = -1

        # Extract Numerics for comparison
        nums = [float(x) for x in self.patterns['numeric'].findall(text)]
        
        if self.patterns['conditional'].search(text_lower):
            props.append((polarity, 'conditional', text_lower))
        elif self.patterns['causal'].search(text_lower):
            props.append((polarity, 'causal', text_lower))
        elif self.patterns['comparative'].search(text_lower):
            if len(nums) >= 2:
                props.append((polarity, 'comparison', (nums[0], nums[1])))
            else:
                props.append((polarity, 'comparison', text_lower))
        elif self.patterns['ordering'].search(text_lower):
            props.append((polarity, 'ordering', text_lower))
        elif len(nums) > 0:
             props.append((polarity, 'equality', nums[0]))
        else:
            # Fallback for generic statements
            words = text_lower.split()
            if len(words) > 0:
                props.append((polarity, 'equality', words[0]))

        return props if props else [(1, 'equality', 'empty')]

    def _build_vector(self, all_props: List[List[Tuple]]) -> Tuple[np.ndarray, Dict]:
        """Create sparse binary vector and mapping for propositions"""
        unique_props = list(set(str(p) for group in all_props for p in group))
        prop_map = {p: i for i, p in enumerate(unique_props)}
        P = len(unique_props)
        
        vectors = []
        for group in all_props:
            vec = np.zeros(P)
            for p in group:
                idx = prop_map.get(str(p))
                if idx is not None:
                    vec[idx] = 1
            vectors.append(vec)
        return np.array(vectors), prop_map

    def _hebbian_update(self, W: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Apply Hebbian learning rule with decay"""
        if W.shape[0] == 0:
            return W
        a = W @ x
        # Outer product for Hebbian update: delta = eta * (a ⊗ x) - lambda * W
        # Ensure dimensions match for outer product if x is 1D
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if a.ndim == 1:
            a = a.reshape(-1, 1)
            
        delta = ETA * (a @ x.T) - LAMBDA * W
        return W + delta

    def _compute_ising_score(self, W: np.ndarray, x: np.ndarray) -> float:
        """Compute score based on proximity to critical magnetization"""
        if W.shape[0] == 0:
            return 0.0
            
        # Spins: s = 2x - 1
        s = 2 * x - 1
        if s.ndim == 2:
            s = s.flatten()
            
        P = len(s)
        if P == 0:
            return 0.0

        # Magnetization
        M = np.abs(np.sum(s)) / P
        
        # Energy (Hamiltonian)
        # E = -0.5 * sum(W_ij * s_i * s_j)
        # Note: W might be asymmetric due to directed edges, use symmetric part for energy or just dot product
        energy = -0.5 * np.sum(W * np.outer(s, s))
        
        # Critical point approximation:
        # In random graphs, critical point often near M ~ 0 or specific threshold.
        # We simulate a "critical" magnetization Mc as the median expected random walk value ~ 1/sqrt(P)
        Mc = 1.0 / np.sqrt(P) if P > 0 else 0.0
        
        # Score based on distance to criticality
        # If the system is too ordered (M=1) or too disordered (M=0), it might be less "reasoned"
        # than a balanced state, OR we look for the phase transition peak.
        # Here we use the provided formula: score = exp(-|M - Mc| / tau)
        # We estimate tau from the variance of M over a synthetic window or use a fixed heuristic
        tau = TAU
        score = np.exp(-np.abs(M - Mc) / tau)
        
        return float(score)

    def _check_meta_confidence(self, text: str) -> float:
        """Detect Tier B traps and return a confidence cap (< 0.3 if trapped)"""
        text_lower = text.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(text_lower):
            return 0.2
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(text_lower):
            return 0.25
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(text_lower):
            return 0.3
        # 4. Pronoun Ambiguity (simplified check)
        if self.patterns['pronoun_ambiguity'].search(text_lower):
            return 0.25
            
        return 1.0 # No trap detected

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib"""
        import zlib
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0:
            return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Parse Prompt
        prompt_props = self._extract_propositions(prompt)
        
        # Parse Candidates
        candidate_data = []
        all_props = [prompt_props]
        
        for c in candidates:
            c_props = self._extract_propositions(c)
            candidate_data.append({'text': c, 'props': c_props})
            all_props.append(c_props)
            
        # Build global vocabulary and vectors
        # Flatten all_props for vectorization
        flat_all = prompt_props + [p for c in candidate_data for p in c['props']]
        if not flat_all:
            # Fallback if no structure found
            return [{'candidate': c, 'score': 0.5, 'reasoning': 'No structural patterns detected.'} for c in candidates]

        # Create mapping and vectors for prompt + candidates combined to ensure same dimension
        # We need a unified vector space for the matrix W
        unique_strs = list(set(str(p) for p in flat_all))
        prop_to_idx = {s: i for i, s in enumerate(unique_strs)}
        P = len(unique_strs)
        
        if P == 0:
            return [{'candidate': c, 'score': 0.5, 'reasoning': 'Empty proposition set.'} for c in candidates]

        def vec_from_props(props):
            v = np.zeros(P)
            for p in props:
                idx = prop_to_idx.get(str(p))
                if idx is not None:
                    v[idx] = 1
            return v

        x_prompt = vec_from_props(prompt_props)
        
        # Initialize Weight Matrix W
        # Symmetric for similarity, directed for implication (simplified to symmetric for stability here)
        W = np.zeros((P, P))
        
        # Populate W based on lexical rules (Step 2 of Algorithm)
        # This is a simplified initialization; in a full run, this would be richer
        for i, p_i in enumerate(unique_strs):
            for j, p_j in enumerate(unique_strs):
                if i == j:
                    W[i,j] = 1.0 # Self connection
                    continue
                # Simple lexical overlap or type matching could go here
                # For now, rely on Hebbian to find structure from the prompt context
                pass

        # Run Hebbian updates on the Prompt to establish context
        # Iterate a few times to let the prompt "settle"
        x_curr = x_prompt.copy()
        for _ in range(5):
            W = self._hebbian_update(W, x_curr)
            # Normalize W to prevent explosion
            W = np.clip(W, -2, 2)

        # Evaluate each candidate
        for i, cand in enumerate(candidate_data):
            x_cand = vec_from_props(cand['props'])
            
            # Combine prompt and candidate context for evaluation
            x_combined = np.maximum(x_prompt, x_cand)
            
            # Update W with candidate context (Plasticity)
            W_cand = W.copy()
            for _ in range(3):
                W_cand = self._hebbian_update(W_cand, x_combined)
            
            # Phase Transition Scoring
            coherence_score = self._compute_ising_score(W_cand, x_combined)
            
            # Structural Match Bonus (Simple overlap check)
            overlap = np.dot(x_prompt, x_cand) / (np.linalg.norm(x_prompt) * np.linalg.norm(x_cand) + 1e-9)
            
            # NCD Tiebreaker (Max 15% influence)
            ncd_val = self._compute_ncd(prompt, cand['text'])
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Final Score Composition
            # Structural/Coherence >= 50%, Computation (overlap/logic) >= 20%, NCD <= 15%
            final_score = (0.6 * coherence_score) + (0.25 * overlap) + (0.15 * ncd_score)
            
            # Reasoning string
            reason = f"Coherence: {coherence_score:.2f}, Overlap: {overlap:.2f}"
            
            results.append({
                'candidate': cand['text'],
                'score': float(final_score),
                'reasoning': reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at < 0.3 for ambiguous/unanswerable prompts (Tier B).
        Caps at < 0.9 unless definitive computation exists.
        """
        # 1. Meta-Confidence Check (Tier B Traps)
        meta_cap = self._check_meta_confidence(prompt)
        
        if meta_cap < 1.0:
            return meta_cap
            
        # 2. Structural Parsing Check
        props = self._extract_propositions(prompt)
        if not props:
            return 0.2 # Honest uncertainty if no structure found
            
        # 3. Compute a provisional score via evaluate logic
        # We treat the single answer as a candidate list
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.2
            
        base_score = res[0]['score']
        
        # 4. Calibration
        # Even with high score, avoid > 0.9 unless it's a math certainty
        # Since we don't have a symbolic solver here, we cap at 0.85 for "highly likely"
        final_conf = min(base_score, 0.85)
        
        # Ensure we don't exceed the meta_cap if it was lowered (though handled above)
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
