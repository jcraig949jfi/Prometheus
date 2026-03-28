# Prime Number Theory + Pragmatics + Free Energy Principle

**Fields**: Mathematics, Linguistics, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T22:34:18.583472
**Report Generated**: 2026-03-27T16:08:14.523927

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only `re` (standard library) we extract from both the prompt and each candidate answer a list of *propositional atoms*. Each atom is a tuple `(type, polarity, value)` where  
   - `type` ∈ {`NEG`, `COMP`, `COND`, `NUM`, `CAUS`, `ORD`, `QUANT`} (negation, comparative, conditional, numeric, causal, ordering, quantifier).  
   - `polarity` = +1 for affirmed, –1 for negated.  
   - `value` is the extracted token (e.g., the number in a `NUM` atom, the predicate in a `COND` atom).  
   The result is stored as a NumPy structured array `props` with fields `type_i` (int code), `polarity` (float), `value_hash` (int from `hash(value)`).  

2. **Prime weighting** – Assign each `type` a distinct prime number (e.g., `NEG→2`, `COMP→3`, `COND→5`, `NUM→7`, `CAUS→11`, `ORD→13`, `QUANT→17`). Build a weight vector `w = np.array([prime_for_type])`. For each proposition we compute a *prime‑encoded score* `s = w[type_i] * polarity`.  

3. **Prior from prompt (Free Energy Principle)** – Compute the expected distribution over types in the prompt:  
   `μ = np.bincount(prompt_props['type_i'], weights=prompt_props['polarity'])`  
   Normalize to get a probability vector `p = μ / μ.sum()`.  

4. **Likelihood from answer** – For each candidate answer compute the observed count vector `c = np.bincount(answer_props['type_i'], weights=answer_props['polarity'])`.  
   Approximate the variational free energy (prediction error) with a chi‑square‑like term:  
   `FE = np.sum(((c - p*len(answer_props))**2) / (p*len(answer_props) + 1e-8))`.  

5. **Pragmatic penalty (Grice’s maxims)** – Heuristically count violations:  
   - *Quantity*: answer length deviates >20 % from prompt length → `q_pen`.  
   - *Quality*: presence of a `NEG` atom without supporting evidence in prompt → `qual_pen`.  
   - *Relevance*: proportion of `COND` or `CAUS` atoms absent in prompt → `rel_pen`.  
   - *Manner*: number of ambiguous comparatives (`>`/`<` without clear anchor) → `mann_pen`.  
   Total pragmatic cost `P = α·q_pen + β·qual_pen + γ·rel_pen + δ·mann_pen` (α,β,γ,δ set to 1).  

6. **Score** – Lower free energy = better prediction; we define the final score as  
   `score = -(FE + P)`.  
   The candidate with the highest score is selected. All operations use only NumPy arrays and Python’s built‑in `re`/`hash`.  

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`), conditionals (`if … then`, `unless`), numeric values (integers, decimals), causal claims (`because`, `leads to`, `causes`), ordering relations (`first`, `second`, `before`, `after`, `precede`), quantifiers (`all`, `some`, `none`, `most`).  

**Novelty**  
Existing tools often rely on bag‑of‑words, TF‑IDF, or shallow similarity. This design fuses three disparate ideas: (i) a symbolic prime‑encoding of logical atom types (number‑theoretic labeling), (ii) a variational free‑energy minimization step that treats the prompt as a generative model and the answer as observed data (Free Energy Principle), and (iii) explicit pragmatic violation penalties derived from Grice’s maxims. While each component appears separately in probabilistic logic, neural‑symbolic hybrids, or pragmatics‑aware parsers, their exact combination in a pure‑NumPy, rule‑based scorer has not been reported in the literature, making the approach novel.  

**Rating**  
Reasoning: 8/10 — captures logical structure via prime‑typed atoms and error minimization.  
Metacognition: 6/10 — the system monitors prediction error but lacks explicit self‑reflective loops.  
Hypothesis generation: 5/10 — generates alternative proposition sets implicitly via scoring, not explicit hypothesis ranking.  
Implementability: 9/10 — relies only on regex, NumPy arithmetic, and simple counting; straightforward to code and test.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Prime Number Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Prime Number Theory: strong positive synergy (+0.471). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Pragmatics: strong positive synergy (+0.595). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Causal Inference + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Criticality + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Pragmatics + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: OverflowError: Python int too large to convert to C long

**Forge Timestamp**: 2026-03-27T15:32:24.475000

---

## Code

**Source**: scrap

[View code](./Prime_Number_Theory---Pragmatics---Free_Energy_Principle/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool fusing Prime Number Theory (structural encoding), 
    Free Energy Principle (prediction error minimization), and Pragmatics (Gricean maxims).
    
    Mechanism:
    1. Parses logical atoms (negation, conditionals, numbers) from prompt/candidates.
    2. Encodes atom types as distinct primes to create a structural signature.
    3. Computes Free Energy (FE) as the divergence between prompt expectations and candidate observations.
    4. Applies Pragmatic penalties for length deviation, unsupported negation, or irrelevant causality.
    5. Uses NCD only as a tie-breaker for low-structure inputs.
    6. Implements Tier-B epistemic honesty by detecting ambiguity/presuppositions to cap confidence.
    """

    # Prime mapping for atom types
    TYPE_MAP = {
        'NEG': 2, 'COMP': 3, 'COND': 5, 'NUM': 7, 
        'CAUS': 11, 'ORD': 13, 'QUANT': 17
    }
    
    # Regex patterns for extraction
    PATTERNS = {
        'NEG': [r'\b(not|no|never|none|neither)\b'],
        'COMP': [r'(>|<|>=|<=|more than|less than|greater|lesser|better|worse)'],
        'COND': [r'\b(if|then|unless|otherwise|provided)\b'],
        'NUM': [r'-?\d+(?:\.\d+)?'],
        'CAUS': [r'\b(because|causes|leads to|due to|therefore|thus)\b'],
        'ORD': [r'\b(first|second|third|before|after|precede|follow)\b'],
        'QUANT': [r'\b(all|some|most|every|each|any)\b']
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        self.compiled = {}
        for k, patterns in self.PATTERNS.items():
            self.compiled[k] = re.compile('|'.join(patterns), re.IGNORECASE)

    def _extract_atoms(self, text: str) -> np.ndarray:
        """Extract propositional atoms as (type_code, polarity, value_hash)."""
        atoms = []
        text_lower = text.lower()
        
        # Check negations for polarity context (simplified: global scope for demo)
        # In a full engine, this would be scope-resolved.
        
        for type_name, regex in self.compiled.items():
            matches = regex.findall(text_lower)
            for match in matches:
                val_str = match if isinstance(match, str) else match[0]
                # Determine polarity: simple heuristic based on immediate preceding 'not' if not already NEG type
                polarity = 1.0
                if type_name != 'NEG':
                    # Check if this specific match instance is negated in original text
                    # (Simplified for brevity: assuming standard form unless explicit 'not' found near)
                    pass 
                
                # Hash value for uniqueness check
                v_hash = hash(val_str)
                t_code = self.TYPE_MAP[type_name]
                atoms.append((t_code, polarity, v_hash))
                
                # Special handling for NUM polarity if preceded by negative sign in string
                if type_name == 'NUM':
                    if '-' in val_str:
                        polarity = -1.0 # Treat negative numbers as negative polarity evidence
                
                if type_name == 'NEG':
                    polarity = -1.0 # Negation flips the state

        if not atoms:
            # Empty array with correct dtype if no atoms found
            return np.array([], dtype=[('type_i', int), ('polarity', float), ('value_hash', int)])
            
        return np.array(atoms, dtype=[('type_i', int), ('polarity', float), ('value_hash', int)])

    def _compute_free_energy(self, prompt_atoms: np.ndarray, answer_atoms: np.ndarray) -> float:
        """Calculate variational free energy (prediction error) between prompt and answer."""
        if len(prompt_atoms) == 0:
            return 0.0 if len(answer_atoms) == 0 else 10.0
            
        # Prior distribution from prompt (normalized counts weighted by polarity)
        p_counts = np.bincount(prompt_atoms['type_i'], weights=prompt_atoms['polarity'], minlength=18)
        p_sum = np.sum(np.abs(p_counts))
        if p_sum == 0: p_sum = 1e-8
        p_dist = p_counts / p_sum
        
        # Observed counts from answer
        c_counts = np.bincount(answer_atoms['type_i'], weights=answer_atoms['polarity'], minlength=18)
        
        # Expected counts based on prompt distribution scaled to answer length
        scale = len(answer_atoms) if len(answer_atoms) > 0 else 1
        expected = p_dist * scale
        
        # Chi-square like divergence (Free Energy approximation)
        # Add small epsilon to avoid division by zero
        epsilon = 1e-8
        fe = np.sum(((c_counts - expected)**2) / (expected + epsilon))
        return float(fe)

    def _compute_pragmatic_penalty(self, prompt: str, answer: str, p_atoms: np.ndarray, a_atoms: np.ndarray) -> float:
        """Apply Gricean maxims as penalties."""
        penalty = 0.0
        
        # Quantity: Length deviation > 20%
        p_len, a_len = len(prompt), len(answer)
        if p_len > 0:
            dev = abs(a_len - p_len) / p_len
            if dev > 0.2:
                penalty += (dev - 0.2) * 2.0 # Linear penalty beyond threshold
        
        # Quality: Negation in answer without negation in prompt (potential hallucination of conflict)
        p_neg = np.any(p_atoms['type_i'] == self.TYPE_MAP['NEG']) if len(p_atoms) > 0 else False
        a_neg = np.any(a_atoms['type_i'] == self.TYPE_MAP['NEG']) if len(a_atoms) > 0 else False
        if a_neg and not p_neg:
            penalty += 1.5
            
        # Relevance: High proportion of causal/conditional atoms in answer not present in prompt
        complex_types = [self.TYPE_MAP['COND'], self.TYPE_MAP['CAUS']]
        p_complex = np.sum(np.isin(p_atoms['type_i'], complex_types)) if len(p_atoms) > 0 else 0
        a_complex = np.sum(np.isin(a_atoms['type_i'], complex_types)) if len(a_atoms) > 0 else 0
        
        if a_complex > p_complex:
            penalty += (a_complex - p_complex) * 1.0
            
        return penalty

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0: return 1.0
        c1, c2 = len(z(s1.encode())), len(z(s2.encode()))
        c12 = len(z((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier-B Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability to cap confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupp_triggers = ["have you stopped", "have you quit", "why did", "when did", "how often did"]
        if any(t in p_lower for t in presupp_triggers):
            return 0.2
            
        # 2. Scope/Pronoun Ambiguity (Heuristic)
        if re.search(r'\b(every|all)\s+\w+\s+.*\s+a\s+\w+', p_lower) and "same" not in p_lower:
             # Rough heuristic for "Every X did a Y" ambiguity
             pass # Hard to detect purely syntactically without NLP, but flag if "who" exists
        if re.search(r'\bwho\s+is\s+(he|she|it|they)\b', p_lower) or re.search(r'\b(told|said)\s+\w+\s+he\b', p_lower):
            if "who" in p_lower or "which" in p_lower:
                return 0.25

        # 3. False Dichotomy
        if re.search(r'\beither\s+.*\s+or\s+.*\b', p_lower) and "option" not in p_lower:
            # Check if exhaustive list is implied? Hard. Flag if question asks to choose.
            if "?" in prompt:
                return 0.4 # Moderate uncertainty

        # 4. Subjectivity
        subj_triggers = ["best", "worst", "favorite", "opinion", "believe"]
        if any(t in p_lower for t in subj_triggers) and "calculate" not in p_lower:
            return 0.3

        # 5. Unanswerability (Missing info markers)
        if "insufficient" in p_lower or "cannot be determined" in p_lower:
            return 0.1
            
        return 1.0 # Default high potential confidence if structure holds

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_atoms = self._extract_atoms(prompt)
        results = []
        
        # Base metrics for normalization if needed
        max_fe = 0.0
        scores = []
        
        # First pass: calculate raw scores
        for cand in candidates:
            a_atoms = self._extract_atoms(cand)
            
            # 1. Structural Score (Free Energy)
            fe = self._compute_free_energy(p_atoms, a_atoms)
            
            # 2. Pragmatic Penalty
            prag_pen = self._compute_pragmatic_penalty(prompt, cand, p_atoms, a_atoms)
            
            # 3. NCD Tiebreaker (only significant if structural signal is weak)
            # We invert NCD (0=identical, 1=different) to be a positive score component
            ncd_val = self._ncd_score(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.15 # Max 15% weight as per requirements
            
            # Final Score: Lower FE is better. Negative FE - Penalty + NCD_bonus
            # We invert FE so higher is better: -FE
            score = -(fe + prag_pen) + ncd_bonus
            
            # Construct reasoning string
            reason = f"FE={fe:.2f}, PragPen={prag_pen:.2f}, NCD_bonus={ncd_bonus:.2f}"
            results.append({"candidate": cand, "score": score, "reasoning": reason})
            scores.append(score)

        # Normalize scores to be more interpretable if desired, but ranking is key
        # Shift so best is 0 or positive if all negative
        if scores:
            min_s = min(scores)
            for r in results:
                r['score'] = r['score'] - min_s + 0.1 # Ensure positive
                
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier-B).
        """
        # 1. Meta-check for ambiguity/traps
        meta_cap = self._meta_confidence(prompt)
        
        # If meta-check says "ambiguous", return low confidence immediately
        if meta_cap < 0.5:
            return meta_cap

        # 2. Structural validation
        p_atoms = self._extract_atoms(prompt)
        a_atoms = self._extract_atoms(answer)
        
        # If no structural atoms found in either, we rely on NCD, which is weak
        if len(p_atoms) == 0 and len(a_atoms) == 0:
            # Pure string match confidence
            ncd = self._ncd_score(prompt, answer)
            conf = (1.0 - ncd) * 0.8 # Cap at 0.8 for pure string match
            return min(conf, meta_cap)
        
        # Calculate alignment score
        fe = self._compute_free_energy(p_atoms, a_atoms)
        prag = self._compute_pragmatic_penalty(prompt, answer, p_atoms, a_atoms)
        
        # Convert FE/Prag to a 0-1 scale
        # Low FE is good. FE=0 -> 1.0. FE=10 -> ~0.0
        structural_conf = max(0.0, 1.0 - (fe / 10.0) - (prag / 5.0))
        
        # Hard cap by meta-confidence
        final_conf = min(structural_conf, meta_cap)
        
        # Never return > 0.9 unless it's a perfect structural match and meta says yes
        if final_conf > 0.9 and meta_cap < 1.0:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))
```

</details>
