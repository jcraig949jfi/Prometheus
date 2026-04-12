# Statistical Mechanics + Sparse Autoencoders + Mechanism Design

**Fields**: Physics, Computer Science, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T17:45:47.520818
**Report Generated**: 2026-03-31T19:09:43.856530

---

## Nous Analysis

**Algorithm**  
We build a factor‑graph energy model whose variables are the truth values of elementary propositions extracted from a prompt‑answer pair.  
1. **Feature extraction (Sparse Autoencoder‑style)** – Using only regex and a fixed dictionary of linguistic patterns (negation, comparative, conditional, numeric, causal, ordering), each sentence is converted into a high‑dimensional binary feature vector **x** ∈ {0,1}^D. A sparsity‑encouraging linear transform **W** (learned offline by minimizing ‖x‑Wᵀz‖₂² + λ‖z‖₁ with numpy’s LARS or coordinate descent) yields a low‑dimensional sparse code **z** = f(**x**) (typically 5‑20 non‑zero entries). **z** is the representation used for scoring.  
2. **Energy definition (Statistical Mechanics)** – For a candidate answer *a*, we construct a set of clauses Cₖ (e.g., “If X > Y then Z”, “¬(A ∧ B)”). Each clause contributes a penalty *wₖ·vₖ(a)* where *vₖ(a)*∈{0,1} indicates whether the clause is violated under the truth assignment implied by *a*. The total energy is  
   \[
   E(a)=\sum_{k} w_k\,v_k(a) - b^\top z(a)
   \]  
   where **w** are clause weights (learned via logistic‑loss on a small validation set) and *b* couples the sparse code to the energy, encouraging answers that align with salient features.  
3. **Scoring via Boltzmann distribution (Mechanism Design)** – The probability that *a* is correct is  
   \[
   P(a)=\frac{\exp(-E(a)/T)}{\sum_{a'}\exp(-E(a')/T)},
   \]  
   with temperature *T* fixed (e.g., 1.0). This is a proper scoring rule: reporting the true belief maximizes expected score, satisfying incentive compatibility. The final score for an answer is log P(a).  

**Parsed structural features** – negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), numeric values and units, causal claims (“because”, “leads to”), ordering relations (“before”, “after”, “first”, “last”). Each yields a binary feature in **x**.  

**Novelty** – While energy‑based models, sparse autoencoders, and proper scoring rules each exist separately, coupling a sparsely encoded linguistic feature space with a Boltzmann‑scored factor graph that is explicitly designed to be incentive‑compatible is not present in the literature to our knowledge.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on hand‑crafted patterns.  
Metacognition: 5/10 — the model does not monitor its own parsing errors; confidence derives only from energy.  
Hypothesis generation: 6/10 — sparse codes enable rapid proposal of alternative clause sets, yet generation is limited to predefined patterns.  
Implementability: 8/10 — all steps use numpy and stdlib; no external libraries or neural nets required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Statistical Mechanics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Mechanism Design + Statistical Mechanics: strong positive synergy (+0.120). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Sparse Autoencoders + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Statistical Mechanics + Wavelet Transforms + Mechanism Design (accuracy: 0%, calibration: 0%)
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=10% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-31T18:59:00.511691

---

## Code

**Source**: scrap

[View code](./Statistical_Mechanics---Sparse_Autoencoders---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Statistical Mechanics (Energy models), 
    Sparse Autoencoders (Feature selection), and Mechanism Design (Proper scoring).
    
    Mechanism:
    1. Feature Extraction: Parses text into binary features (negation, numeric, conditional).
    2. Sparse Coding: Selects salient features via hard-thresholding (simulating L1 sparsity).
    3. Energy Model: Computes energy E(a) = Clause_Penalties - Feature_Alignment.
    4. Scoring: Boltzmann distribution P(a) ~ exp(-E/T).
    5. Epistemic Honesty: Meta-checks for ambiguity/presupposition cap confidence.
    """

    def __init__(self):
        # Linguistic patterns for feature extraction
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r"\bn't"],
            'comparative': [r'\bgreater\s+than\b', r'\bless\s+than\b', r'\bmore\s+than\b', r'\bfewer\s+than\b', r'>', r'<'],
            'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bleads\s+to\b', r'\bcauses\b'],
            'ordering': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', r'\bnext\b'],
            'presupposition': [r'\bhave\s+you\s+(stopped|quit)\b', r'\bwhy\s+did\s+\w+\s+(fail|stop)\b'],
            'false_dichotomy': [r'\beither\s+.*\bor\b', r'\bmust\s+be\s+either\b'],
            'subjectivity': [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bopinion\b']
        }
        self.T = 1.0  # Temperature
        
        # Weights (Learned offline conceptually, hardcoded for implementation)
        self.w_clause = 2.0
        self.w_feature = 0.5
        self.w_ncd = 0.15

    def _extract_features(self, text: str) -> Dict[str, bool]:
        """Extract binary linguistic features."""
        text_lower = text.lower()
        features = {}
        for key, regexes in self.patterns.items():
            match = False
            for rgx in regexes:
                if re.search(rgx, text_lower):
                    match = True
                    break
            features[key] = match
        return features

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for constructive computation."""
        # Matches integers and floats
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(n) for n in nums]

    def _sparse_code(self, features: Dict[str, bool], threshold: int = 1) -> List[str]:
        """
        Simulate Sparse Autoencoder output.
        Keeps only 'salient' features (those that are True). 
        In a real SAE, this would be z = ReLU(Wx - bias).
        Here, we treat active boolean flags as the sparse code 'z'.
        """
        return [k for k, v in features.items() if v]

    def _compute_clause_violations(self, prompt: str, answer: str) -> float:
        """
        Check logical consistency between prompt constraints and answer.
        Returns penalty score (higher = more violations).
        """
        penalty = 0.0
        p_low = prompt.lower()
        a_low = answer.lower()
        
        # 1. Negation consistency
        # If prompt says "X is not Y", and answer implies "X is Y"
        # Simple heuristic: if prompt has 'not' and answer lacks negation words where expected
        if any(re.search(r, p_low) for r in self.patterns['negation']):
            # If prompt negates, but answer is affirmative and short (risky heuristic)
            # More robust: Check if answer contradicts a specific extracted fact
            pass 

        # 2. Numeric consistency (Constructive Computation)
        # If prompt asks for comparison, check if answer aligns with numbers
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        
        if len(p_nums) >= 2 and len(a_nums) >= 1:
            # Heuristic: If prompt compares A and B, and answer is a number,
            # check if it matches the logical result (e.g., max, min, sum)
            # This is a simplified proxy for full symbolic math
            if 'greater' in p_low or 'max' in p_low or 'larger' in p_low:
                if a_nums and max(p_nums) not in a_nums:
                     # If the answer doesn't contain the max number, slight penalty
                     # (Only if answer is numeric)
                     penalty += 0.5
            elif 'less' in p_low or 'min' in p_low or 'smaller' in p_low:
                if a_nums and min(p_nums) not in a_nums:
                    penalty += 0.5

        # 3. Conditional logic
        if any(re.search(r, p_low) for r in self.patterns['conditional']):
            # If prompt is conditional, answer should ideally reflect conditionality or result
            # Hard to verify without NLI, so we rely on feature alignment mostly
            pass
            
        return penalty

    def _calculate_energy(self, prompt: str, answer: str) -> float:
        """
        Calculate Energy E(a) = Sum(w_k * v_k) - b^T z
        Lower energy = Better answer.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        # Sparse codes
        z_prompt = self._sparse_code(p_feats)
        z_answer = self._sparse_code(a_feats)
        
        # 1. Clause Violation Penalty (v_k)
        # Does the answer violate the structural constraints of the prompt?
        violation_penalty = self._compute_clause_violations(prompt, answer)
        
        # 2. Feature Alignment Term (-b^T z)
        # Encourage answers that share salient structural features with the prompt
        # Intersection of sparse codes
        alignment = len(set(z_prompt) & set(z_answer))
        
        # Energy formula
        # High alignment reduces energy (good)
        # High violation increases energy (bad)
        energy = (self.w_clause * violation_penalty) - (self.w_feature * alignment)
        
        return energy

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_low = prompt.lower()
        
        # 1. Presupposition traps
        for rgx in self.patterns['presupposition']:
            if re.search(rgx, p_low):
                return 0.2  # Low confidence on loaded questions
        
        # 2. False Dichotomy
        if re.search(r'\beither\s+.*\bor\b', p_low):
            # Check if options are exhaustive (hard to know), but flag as risky
            return 0.5 
            
        # 3. Subjectivity
        for rgx in self.patterns['subjectivity']:
            if re.search(rgx, p_low):
                return 0.4  # Subjective questions have no single truth
        
        # 4. Pronoun/Scope Ambiguity (Heuristic)
        # If "who" or "which" appears but no clear antecedents in a short context
        if re.search(r'\b(who|which|he|she|it)\b', p_low):
            # Very rough check: if length is short and has pronouns, maybe ambiguous
            if len(prompt.split()) < 15:
                return 0.6

        return 1.0  # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        max_len = max(len(z1), len(z2))
        if max_len == 0: return 0.0
        return (len(z12) - min(len(z1), len(z2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        energies = []
        scores = []
        
        # Step 1: Calculate raw energies
        for cand in candidates:
            e = self._calculate_energy(prompt, cand)
            energies.append(e)
        
        # Step 2: Convert to Boltzmann probabilities
        # P(a) = exp(-E/T) / Z
        try:
            exp_vals = [math.exp(-e / self.T) for e in energies]
            Z = sum(exp_vals)
            probs = [v / Z if Z > 0 else 1.0/len(candidates) for v in exp_vals]
        except OverflowError:
            # Fallback if energies are extreme
            probs = [1.0/len(candidates)] * len(candidates)

        # Step 3: Combine with NCD (max 15% weight) and apply Meta-Cap
        results = []
        for i, cand in enumerate(candidates):
            # Structural score (from energy model)
            struct_score = probs[i]
            
            # NCD Tiebreaker/Modifier
            # We want high NCD similarity to imply higher score? 
            # Actually, NCD measures distance. Low distance = high similarity.
            # But for reasoning, similarity to prompt isn't always truth.
            # We use NCD only as a tiny tiebreaker for "relevance".
            ncd_val = 1.0 - self._ncd_score(prompt, cand) # Convert to similarity 0-1
            
            # Weighted combination: 85% Structural, 15% NCD
            # Note: If structural signal is weak (uniform probs), NCD helps slightly
            final_score = (0.85 * struct_score) + (0.15 * ncd_val * struct_score)
            
            # Apply Epistemic Cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Energy={energies[i]:.2f}, MetaCap={meta_cap:.2f}, NCD_sim={ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Capped by meta-analysis of the prompt.
        """
        # 1. Meta Check (Traps)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural Evaluation
        energy = self._calculate_energy(prompt, answer)
        
        # Convert energy to a pseudo-probability/confidence
        # Low energy -> High confidence. 
        # Using sigmoid-like mapping: 1 / (1 + exp(energy))
        # Adjusted so that energy=0 gives 0.5, negative energy gives >0.5
        raw_conf = 1.0 / (1.0 + math.exp(energy))
        
        # 3. Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Ensure bounds
        return max(0.0, min(1.0, final_conf))
```

</details>
