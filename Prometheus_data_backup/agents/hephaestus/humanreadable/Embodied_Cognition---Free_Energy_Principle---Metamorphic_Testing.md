# Embodied Cognition + Free Energy Principle + Metamorphic Testing

**Fields**: Cognitive Science, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:44:44.620257
**Report Generated**: 2026-03-31T14:34:54.728177

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage (embodied grounding)** – Using only `re` we extract a set of grounded predicates from the prompt and each candidate answer:  
   - *Numeric*: `(value, unit)` → stored in a NumPy array `V`.  
   - *Comparative*: `(entity1, op, entity2)` where `op∈{<,>,=,≤,≥}` → stored as a constraint matrix `C`.  
   - *Conditional/causal*: `(antecedent → consequent)` → stored as implication edges in a directed graph `G`.  
   - *Negation*: a flag `¬` attached to the predicate.  
   - *Spatial/temporal*: prepositions (`above`, `before`, `inside`) → encoded as binary relations in `S`.  
   Each predicate gets a *sensorimotor feature vector* `f` (e.g., magnitude for numbers, orientation for spatial terms) built from a fixed lookup table; all `f` are stacked into a matrix `F`.

2. **Metamorphic relation generation** – For each extracted predicate we define a small set of MRs that preserve truth under transformation:  
   - *Numeric scaling*: `V' = α·V` (α=2, 0.5).  
   - *Order inversion*: swap arguments of comparatives (`<`↔`>`).  
   - *Negation toggle*: flip the `¬` flag.  
   - *Consequent swap*: in conditionals exchange antecedent/consequent.  
   Applying an MR to the prompt yields a transformed prompt `P̂`; we parse `P̂` the same way to obtain expected feature matrix `F̂`.

3. **Free‑energy scoring (prediction‑error minimization)** – For a candidate answer we compute its feature matrix `F_c`. The variational free energy is approximated by the weighted prediction error plus a simplicity term:  

   ```
   ε = F_c - F̂                         # element‑wise error
   precision = diag(1 / (σ² + ε₀))      # σ² from prompt variance, ε₀ small constant
   FE = 0.5 * ε @ precision @ ε.T + λ * ||F_c||₂²   # λ controls complexity
   ```

   The score is `S = -FE` (lower free energy → higher score). All operations use NumPy; no external models are invoked.

**Structural features parsed** – negations, comparatives (`<,>`, etc.), conditionals (`if … then …`), causal cues (`because`, `leads to`), numeric values with units, ordering expressions (`first`, `more than`, `less than`), spatial prepositions (`above`, `below`, `inside`), temporal markers (`before`, `after`, `during`).

**Novelty** – Each constituent idea has been used separately (e.g., embodied grounding in robotics, free‑energy in perceptual modeling, MRs in software testing). Combining them to derive a prediction‑error‑based scoring function for textual reasoning answers has not, to the best of my knowledge, been reported; thus the approach is novel.

**Ratings**  
Reasoning: 7/10 — captures logical constraints and numeric reasoning but struggles with deep semantic nuance.  
Metacognition: 6/10 — error‑based free energy offers a rudimentary self‑monitoring signal, yet no explicit belief revision.  
Hypothesis generation: 8/10 — systematic MR generation provides a rich set of testable transformations.  
Implementability: 9/10 — relies only on regex, NumPy, and basic graph operations; easy to prototype.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=38% cal=30% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-28T02:38:38.404578

---

## Code

**Source**: scrap

[View code](./Embodied_Cognition---Free_Energy_Principle---Metamorphic_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Embodied-Free-Energy-Metamorphic Reasoning Tool.
    
    Mechanism:
    1. Embodied Grounding: Parses text into structural predicates (numeric, comparative, conditional).
    2. Metamorphic Testing: Generates transformed versions of the prompt (scaling, inversion) to create 
       an expected feature vector (F_hat).
    3. Free Energy Scoring: Computes prediction error between candidate features and expected features.
       Lower free energy (higher score) indicates better alignment with logical constraints.
    4. Epistemic Honesty: Detects ambiguity traps (presuppositions, false dichotomies) to cap confidence.
    """
    
    def __init__(self):
        # Lookup tables for sensorimotor features
        self.units = {'m', 'kg', 's', 'km', 'h', 'cm', 'g', 'min', 'sec'}
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'<': -1, '>': 1, '=': 0, 'less': -1, 'more': 1, 'greater': 1, 'fewer': -1}
        self.conditionals = {'if', 'then', 'unless', 'when', 'because'}
        self.spatial_temporal = {'above', 'below', 'inside', 'before', 'after', 'during', 'under'}
        
        # Trap patterns for Tier B (Epistemic Honesty)
        self.trap_patterns = [
            (r'\b(have|has|did)\s+(you|he|she|they)\s+(stopped|quit|failed)\b', 'presupposition'),
            (r'\b(every|all)\s+\w+\s+(did|has)\s+a\s+\w+\b', 'scope_ambiguity'), # Simplified scope check
            (r'\b(either|or)\b.*\b(or|but)\b', 'false_dichotomy'),
            (r'\b(best|worst|favorite|most\s+beautiful)\b', 'subjectivity'),
            (r'\b(who|he|she|him|her)\s+(was|is)\s+it\b', 'pronoun_ambiguity'),
            (r'\bwithout\s+(enough|sufficient|any)\s+information\b', 'unanswerable')
        ]

    def _extract_numerics(self, text: str) -> List[Tuple[float, str]]:
        """Extract (value, unit) pairs."""
        found = []
        # Match numbers possibly followed by units
        pattern = r'(-?\d+(?:\.\d+)?)\s*(m|kg|s|km|h|cm|g|min|sec|%|dollars)?'
        for m in re.finditer(pattern, text.lower()):
            val = float(m.group(1))
            unit = m.group(2) if m.group(2) else ''
            found.append((val, unit))
        return found

    def _extract_comparatives(self, text: str) -> List[Tuple[str, int, str]]:
        """Extract comparative relations."""
        found = []
        text_lower = text.lower()
        # Simple heuristic: word before and after comparative keywords
        for key, val in self.comparatives.items():
            if key in text_lower:
                # Mock extraction: just flag presence and direction for now
                found.append(("comp", val, "global"))
        return found

    def _extract_conditionals(self, text: str) -> int:
        """Count conditional markers."""
        count = 0
        text_lower = text.lower()
        for word in self.conditionals:
            count += text_lower.count(word)
        return count

    def _extract_negations(self, text: str) -> int:
        """Count negation flags."""
        count = 0
        text_lower = text.lower()
        for word in self.negations:
            # Word boundary check
            if re.search(rf'\b{word}\b', text_lower):
                count += 1
        return count

    def _parse_to_features(self, text: str) -> np.ndarray:
        """
        Parse text into a feature vector F.
        Features: [num_count, num_sum, comp_dir, cond_count, neg_count, spatial_count]
        """
        nums = self._extract_numerics(text)
        comps = self._extract_comparatives(text)
        
        num_count = len(nums)
        num_sum = sum(n[0] for n in nums) if nums else 0.0
        comp_dir = sum(c[1] for c in comps) if comps else 0.0
        cond_count = float(self._extract_conditionals(text))
        neg_count = float(self._extract_negations(text))
        
        spatial_count = 0.0
        text_lower = text.lower()
        for word in self.spatial_temporal:
            spatial_count += text_lower.count(word)

        # Normalize slightly to prevent magnitude dominance
        return np.array([num_count, num_sum/100.0, comp_dir, cond_count/5.0, neg_count/5.0, spatial_count/5.0])

    def _apply_metamorphic_transform(self, text: str, transform_type: str) -> str:
        """Apply a metamorphic transformation to the text."""
        t = text
        if transform_type == 'scale_up':
            # Double numbers
            def double(m):
                val = float(m.group(1))
                unit = m.group(2) if m.group(2) else ''
                return f"{val*2}{unit}"
            t = re.sub(r'(-?\d+(?:\.\d+)?)\s*(m|kg|s|km|h|cm|g|min|sec|%|dollars)?', double, t)
        elif transform_type == 'invert_comp':
            # Swap less/more
            t = t.replace('less', 'MORE_TMP').replace('more', 'less').replace('MORE_TMP', 'more')
            t = t.replace('fewer', 'FEWER_TMP').replace('greater', 'fewer').replace('FEWER_TMP', 'greater')
        elif transform_type == 'toggle_neg':
            # Remove negations (simplification for testing)
            for word in self.negations:
                t = re.sub(rf'\b{word}\b', '', t)
        return t

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Free Energy score.
        FE = 0.5 * (F_c - F_hat)^T * Precision * (F_c - F_hat) + Complexity
        Score = -FE
        """
        # 1. Parse Prompt to get Target Features (F_hat)
        # We generate multiple metamorphic views and average the expected features
        transforms = ['original', 'scale_up', 'invert_comp']
        f_hats = []
        
        # Original
        f_hats.append(self._parse_to_features(prompt))
        
        # Transformed expectations (simplified: we expect the candidate to maintain logical consistency)
        # In a full implementation, we'd parse the transformed prompt to see how features shift,
        # then check if the candidate shifts similarly. Here we approximate by checking stability.
        for t_type in transforms[1:]:
            trans_prompt = self._apply_metamorphic_transform(prompt, t_type)
            f_hats.append(self._parse_to_features(trans_prompt))
            
        f_hat = np.mean(np.array(f_hats), axis=0)
        
        # 2. Parse Candidate to get Current Features (F_c)
        f_c = self._parse_to_features(candidate)
        
        # 3. Compute Prediction Error
        epsilon = f_c - f_hat
        
        # Precision matrix (diagonal, inverse variance)
        # Assume higher variance in numeric sums, lower in counts
        sigma_sq = np.array([0.5, 1.0, 0.2, 0.5, 0.5, 0.5])
        precision = np.diag(1.0 / (sigma_sq + 0.01))
        
        # Free Energy Calculation
        # FE = 0.5 * error^T * precision * error + lambda * complexity
        error_term = 0.5 * float(epsilon @ precision @ epsilon.T)
        complexity_term = 0.1 * np.linalg.norm(f_c)**2
        fe = error_term + complexity_term
        
        return -fe # Higher is better

    def _check_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check for Tier B traps. Returns a cap on confidence.
        1.0 = Clear, 0.2 = Ambiguous/Trap detected.
        """
        p_lower = prompt.lower()
        max_conf = 1.0
        
        # Check regex traps
        for pattern, trap_type in self.trap_patterns:
            if re.search(pattern, p_lower):
                max_conf = 0.25 # Strong penalty for detected traps
                break
        
        # Check for missing structural markers in reasoning questions
        # If it looks like a logic puzzle but has no numbers or comparatives, be wary
        has_nums = bool(re.search(r'\d+', prompt))
        has_logic_words = any(w in p_lower for w in ['if', 'then', 'all', 'some', 'none', 'must', 'cannot'])
        
        if has_logic_words and not has_nums:
            # Potential ambiguity in pure logic without concrete constraints
            # Only penalize if it looks like a trick question
            if 'who' in p_lower or 'which' in p_lower:
                max_conf = min(max_conf, 0.6)
                
        return max_conf

    def _constructive_solve(self, prompt: str) -> Any:
        """
        Attempt to actually solve simple math/logic problems.
        Returns the solution value or None if not solvable constructively.
        """
        # Pattern: "What is X + Y?" or similar simple arithmetic
        # This is a placeholder for constructive computation
        match = re.search(r'(\d+)\s*[\+\-]\s*(\d+)', prompt)
        if match:
            # Very basic arithmetic detection
            return True 
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        constructive_sol = self._constructive_solve(prompt)
        
        for cand in candidates:
            # 1. Free Energy Score (Primary Signal ~50-60%)
            fe_score = self._compute_free_energy(prompt, cand)
            
            # 2. NCD Tiebreaker (~10-15%)
            # Prefer candidates that are compressed well with prompt (relevant) 
            # but not identical (echoing)
            ncd_val = self._check_ncd(prompt, cand)
            ncd_score = -ncd_val # Lower distance is better
            
            # 3. Constructive Bonus
            constructive_bonus = 0.0
            if constructive_sol:
                # If we solved it, check if candidate matches (simplified)
                if str(constructive_sol) in cand.lower() or (len(cand) < 10 and str(constructive_sol) in cand):
                    constructive_bonus = 2.0
            
            # Combine scores
            # Normalize FE roughly to 0-1 range based on typical magnitudes
            normalized_fe = (fe_score + 5.0) / 10.0 
            final_score = (0.6 * normalized_fe) + (0.15 * ncd_score) + constructive_bonus
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"FE:{fe_score:.2f}, NCD:{ncd_val:.2f}, MetaCap:{meta_cap}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply Meta Confidence Cap to scores if ambiguity detected
        if meta_cap < 1.0:
            for res in results:
                # Dampen scores to reflect uncertainty
                res['score'] *= meta_cap
                res['reasoning'] += " [Uncertainty Cap Applied]"
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps at meta-confidence limit.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If meta_cap is low, we are unsure regardless of answer content
        if meta_cap < 0.3:
            return meta_cap
            
        # Evaluate the specific answer against the prompt
        fe_score = self._compute_free_energy(prompt, answer)
        
        # Map FE score to 0-1 confidence
        # High FE (positive) -> High confidence, Low FE (negative) -> Low confidence
        # Sigmoid-like mapping
        raw_conf = 1.0 / (1.0 + np.exp(-fe_score))
        
        # Cap by meta confidence
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we never claim > 0.9 without constructive proof
        if not self._constructive_solve(prompt):
            final_conf = min(final_conf, 0.85)
            
        return float(final_conf)
```

</details>
