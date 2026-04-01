# Phase Transitions + Hebbian Learning + Neuromodulation

**Fields**: Physics, Neuroscience, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T08:25:44.753472
**Report Generated**: 2026-03-31T14:34:46.982281

---

## Nous Analysis

The algorithm treats a prompt and each candidate answer as a set of propositional units extracted by regex patterns for negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal markers (“because”, “leads to”), and ordering terms (“before”, “after”). Each unit is mapped to a concept index; a binary activation vector **a** indicates which concepts appear in the text.  

A Hebbian weight matrix **W** (numpy float64, shape C×C) is initialized to zero. For every co‑occurring pair (i,j) in the same sentence we update  

```
W[i,j] += η * g_i * g_j * a[i] * a[j]
W[j,i] = W[i,j]
```

where η is a small learning rate (e.g., 0.01) and *g* is a neuromodulatory gain factor:  
- negation → g = –1 (inhibitory),  
- modal uncertainty (“might”, “could”) → g = 0.5,  
- certainty (“definitely”, “must”) → g = 1.5,  
- otherwise g = 1.  

After processing the prompt alone we compute its order parameter λ₀ = max |eig(W₀)| (largest eigenvalue magnitude). For each candidate we repeat the extraction, update **W** starting from **W₀** (so the prompt provides a prior), and compute λc. The score is  

```
s = exp( -|λc - λ₀| / σ )
```

with σ set to the standard deviation of λ₀ across a validation set. A sharp increase in λ (phase‑like transition) when the candidate aligns with the prompt’s structure yields a high score; mismatched candidates leave λ near λ₀, giving low scores.  

**Structural features parsed:** negations, comparatives, conditionals, causal statements, ordering relations, numeric constants (treated as separate concepts).  

**Novelty:** While Hebbian learning and neuromodulatory gain appear in cognitive models, coupling them with a phase‑transition order parameter (largest eigenvalue) to evaluate answer coherence is not found in existing QA or reasoning‑scoring tools, which typically rely on lexical similarity or shallow logical forms.  

**Ratings**  
Reasoning: 8/10 — captures logical structure via extracted relations and a global coherence measure that shifts sharply at alignment.  
Metacognition: 6/10 — the method monitors its own order parameter but lacks explicit self‑reflection on uncertainty beyond the gain modulation.  
Hypothesis generation: 7/10 — by varying gain factors it can produce alternative weight configurations, enabling generation of competing interpretations.  
Implementability: 9/10 — uses only regex, NumPy for matrix ops and eigendecomposition, and standard‑library containers; no external APIs or neural nets required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Phase Transitions**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 33% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Neuromodulation**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Neuromodulation + Phase Transitions: strong positive synergy (+0.158). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Embodied Cognition + Hebbian Learning + Neuromodulation (accuracy: 0%, calibration: 0%)
- Phase Transitions + Criticality + Neuromodulation (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=4% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-28T01:44:02.806126

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Hebbian_Learning---Neuromodulation/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    A reasoning tool combining Phase Transitions, Hebbian Learning, and Neuromodulation.
    
    Mechanism:
    1. Structural Parsing: Extracts propositional units (negations, comparatives, conditionals, causals, ordering).
    2. Neuromodulation: Assigns gain factors (g) to units based on certainty/modality (e.g., negation=-1, certainty=1.5).
    3. Hebbian Learning: Builds a symmetric weight matrix W where co-occurring concepts strengthen connections 
       scaled by learning rate and neuromodulatory gains.
    4. Phase Transition Metric: Computes the largest eigenvalue magnitude (lambda) of W as an order parameter.
    5. Scoring: Candidates are scored by how much their structural integration (lambda_c) diverges from the 
       prompt baseline (lambda_0) in a coherent way, normalized by a sigma factor.
    6. Epistemic Honesty: Meta-checks for ambiguity/presupposition cap confidence scores.
    7. Tie-breaking: Uses Normalized Compression Distance (NCD) only when structural signals are weak.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r"\bn't\b"],
            'comparative': [r'\bgreater than\b', r'\bless than\b', r'\bmore than\b', r'\bfewer than\b', r'>', r'<'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bif\b', r'\bunless\b'],
            'causal': [r'\bbecause\b', r'\bleads to\b', r'\bcauses\b', r'\btherefore\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b'],
            'certainty': [r'\bdefinitely\b', r'\bmust\b', r'\bcertainly\b', r'\balways\b'],
            'uncertainty': [r'\bmight\b', r'\bcould\b', r'\bmaybe\b', r'\bpossibly\b'],
            'numbers': [r'\d+\.?\d*']
        }
        self.eta = 0.01
        self.sigma = 0.5  # Default scaling for phase transition sensitivity

    def _extract_units(self, text):
        """Extracts concept indices and their neuromodulatory gains from text."""
        text_lower = text.lower()
        units = []
        gains = {}
        
        # Map categories to indices
        concept_map = {}
        idx = 0
        
        # Define gains based on neuromodulation rules
        # negation -> -1, uncertainty -> 0.5, certainty -> 1.5, else -> 1.0
        
        for category, regex_list in self.patterns.items():
            for regex in regex_list:
                matches = re.finditer(regex, text_lower)
                for match in matches:
                    if category not in concept_map:
                        concept_map[category] = idx
                        idx += 1
                    
                    c_idx = concept_map[category]
                    
                    # Determine gain
                    if category == 'negation':
                        g = -1.0
                    elif category == 'uncertainty':
                        g = 0.5
                    elif category == 'certainty':
                        g = 1.5
                    else:
                        g = 1.0
                    
                    units.append((c_idx, g))
                    
        return units, len(concept_map)

    def _build_matrix(self, text, base_matrix=None, size=0):
        """Builds or updates the Hebbian weight matrix."""
        units, max_idx = self._extract_units(text)
        current_size = max(size, max_idx + 1 if units else 0)
        
        if base_matrix is None:
            W = np.zeros((current_size, current_size), dtype=np.float64)
        else:
            # Expand matrix if new concepts appear
            rows, cols = base_matrix.shape
            if current_size > rows:
                W = np.zeros((current_size, current_size), dtype=np.float64)
                W[:rows, :cols] = base_matrix
            else:
                W = base_matrix.copy()
        
        # Hebbian update: W[i,j] += eta * g_i * g_j * a[i] * a[j]
        # Since we iterate occurrences, a[i] and a[j] are effectively 1 for present units
        for i, g_i in units:
            for j, g_j in units:
                if i != j: # Skip self-connections for simplicity or include if desired
                    W[i, j] += self.eta * g_i * g_j
                    W[j, i] = W[i, j] # Symmetric
        
        return W, current_size

    def _get_order_parameter(self, W):
        """Computes the largest eigenvalue magnitude (phase transition indicator)."""
        if W.size == 0:
            return 0.0
        try:
            eigvals = np.linalg.eigvals(W)
            return float(np.max(np.abs(eigvals)))
        except np.linalg.LinAlgError:
            return 0.0

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(compress(s1.encode()))
        c2 = len(compress(s2.encode()))
        c12 = len(compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _meta_confidence(self, prompt):
        """
        Checks for Tier B traps: presupposition, ambiguity, unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did.*fail", 
            r"why did.*stop", r"when did.*stop", r"is it true that"
        ]
        for pat in presupposition_triggers:
            if re.search(pat, p_lower):
                return 0.2 # Low confidence due to presupposition

        # 2. Scope/Pronoun Ambiguity (Simplified heuristic)
        if re.search(r"every.*a.*y", p_lower) or re.search(r"who is.*he", p_lower):
             # Very rough check for "Every X did a Y" structure or pronoun queries
            if "who" in p_lower and ("he" in p_lower or "she" in p_lower or "him" in p_lower):
                return 0.3
        
        # 3. False Dichotomy
        if re.search(r"either.*or", p_lower) and not re.search(r"both", p_lower):
            # Potential false dichotomy if not exhaustive
            pass # Keep moderate, don't tank unless obvious
            
        # 4. Subjectivity
        subjective_terms = ["best", "worst", "favorite", "opinion", "beautiful"]
        if any(term in p_lower for term in subjective_terms):
            if "calculate" not in p_lower and "math" not in p_lower:
                return 0.4

        return 1.0 # No obvious traps detected

    def _compute_structural_score(self, prompt, candidate):
        """Core logic: Phase transition based scoring."""
        # 1. Process Prompt (Baseline)
        W0, size0 = self._build_matrix(prompt)
        lambda_0 = self._get_order_parameter(W0)
        
        if lambda_0 == 0 and size0 == 0:
            # No structure found in prompt
            return 0.0, False

        # 2. Process Candidate with Prompt context
        # We simulate the candidate being the "next state" or checking alignment
        # Strategy: Concatenate prompt + candidate to see if the system stabilizes or shifts coherently
        combined_text = f"{prompt} {candidate}"
        Wc, size_c = self._build_matrix(combined_text, base_matrix=W0, size=size0)
        lambda_c = self._get_order_parameter(Wc)
        
        # 3. Calculate Phase Transition Score
        # A sharp, coherent increase or specific shift indicates alignment
        # If the candidate contradicts, the eigenvalue spectrum might chaoticize or not shift as expected
        # Using the formula: s = exp(-|lambda_c - lambda_0| / sigma)
        # However, we want alignment to yield HIGH score. 
        # Interpretation: If the candidate fits the logical structure, the "phase" (eigenvalue) should 
        # stabilize or grow predictably. If it's noise, lambda might not change significantly or jump erratically.
        # Let's refine: If the candidate adds valid structural links, lambda should increase.
        # If lambda_c > lambda_0 (growth in coherence), score high. If lambda_c << lambda_0, score low.
        
        delta = lambda_c - lambda_0
        
        # Heuristic: Positive delta (increased coherence) is good. Large negative is bad.
        # We map this to 0-1.
        if delta > 0:
            score = min(1.0, 0.5 + delta) # Base 0.5, add growth
        else:
            score = max(0.0, 0.5 + delta) # Penalize reduction in coherence
            
        # Normalize with sigmoid-like behavior for smoothness
        # Re-applying the theoretical formula for strict adherence:
        # s = exp(-|diff| / sigma). This rewards similarity in phase state.
        # But the prompt says: "sharp increase ... yields high score; mismatched ... leave lambda near 0"
        # Actually, prompt says: "mismatched candidates leave lambda near lambda_0".
        # So: Match = Large Delta? Or Match = Specific Delta?
        # Let's stick to the prompt's explicit formula for the "score":
        raw_score = np.exp(-abs(lambda_c - lambda_0) / self.sigma)
        
        # Modification: We need to distinguish between "no change" (mismatch) and "resonant change".
        # If the prompt has structure (lambda_0 > 0) and candidate aligns, the system should reinforce.
        # Let's use a hybrid:
        # If lambda_c > lambda_0 * 1.1 (10% growth), it's a strong match.
        # If lambda_c is close to lambda_0, it's ambiguous/mismatch.
        
        if lambda_0 > 0.01:
            if lambda_c > lambda_0 * 1.05:
                return min(1.0, raw_score + 0.4), True # Boost for growth
            elif abs(lambda_c - lambda_0) < 0.1:
                return raw_score * 0.5, True # Penalty for no change (mismatch)
        
        return raw_score, True

    def _compute_numeric_answer(self, text):
        """Attempt to extract and solve simple numeric comparisons."""
        # Extract numbers
        nums = re.findall(r'\d+\.?\d*', text)
        if len(nums) >= 2:
            try:
                vals = [float(n) for n in nums]
                # Check for comparative keywords
                if any(k in text.lower() for k in ['greater', 'larger', 'more', '>']):
                    return max(vals)
                if any(k in text.lower() for k in ['less', 'smaller', 'fewer', '<']):
                    return min(vals)
            except ValueError:
                pass
        return None

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_numeric = self._compute_numeric_answer(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning = ""
            
            # 1. Structural/Phase Transition Score
            struct_score, has_structure = self._compute_structural_score(prompt, cand)
            
            # 2. Numeric Verification (Constructive Computation)
            cand_numeric = self._compute_numeric_answer(cand)
            numeric_match = False
            
            if prompt_numeric is not None and cand_numeric is not None:
                if abs(prompt_numeric - cand_numeric) < 1e-6:
                    score = 1.0
                    numeric_match = True
                    reasoning = "Numeric calculation confirms answer."
                else:
                    score = 0.0
                    reasoning = "Numeric calculation contradicts answer."
            elif has_structure:
                score = struct_score
                reasoning = f"Structural coherence score: {struct_score:.4f}"
            else:
                # 3. NCD Tiebreaker (only if no structure)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower distance = higher score) but keep it low weight
                score = max(0.0, 1.0 - ncd_val) * 0.15 
                reasoning = "No structural signal; using compression similarity."

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # 2. Structural Signal Check
        struct_score, has_structure = self._compute_structural_score(prompt, answer)
        
        # If no structure found in prompt, we cannot be confident
        if not has_structure:
            # Check for numeric solvability
            p_num = self._compute_numeric_answer(prompt)
            a_num = self._compute_numeric_answer(answer)
            if p_num is None or a_num is None:
                return 0.2 # Honest uncertainty
            
        # 3. Compute final confidence
        # Base it on the structural score, capped by meta-analysis
        base_conf = struct_score if has_structure else 0.5
        
        # Never exceed 0.9 unless numeric match (definitive)
        p_num = self._compute_numeric_answer(prompt)
        a_num = self._compute_numeric_answer(answer)
        if p_num is not None and a_num is not None and abs(p_num - a_num) < 1e-6:
            final_conf = min(1.0, base_conf + 0.2) # Allow up to 1.0 for math
        else:
            final_conf = min(0.9, base_conf) # Cap at 0.9 for logical/structural
            
        return float(min(final_conf, meta_cap))
```

</details>
