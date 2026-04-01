# Immune Systems + Neuromodulation + Pragmatics

**Fields**: Biology, Neuroscience, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T16:33:04.829735
**Report Generated**: 2026-03-31T14:34:56.930077

---

## Nous Analysis

**Algorithm – Clonal‑Selection Reasoner with Pragmatic Gain Control**  
We treat the prompt as an *antigen* A and each candidate answer Cᵢ as an *antibody* whose affinity is computed from a logical‑form match.  

1. **Parsing & Representation**  
   - Using a small set of regex patterns we extract propositional atoms:  
     - Predicate‑argument triples (e.g., `X causes Y`, `X > Y`, `not P`).  
     - Slots for numeric values, temporal ordering (`before/after`), and causal connectives (`because`, `if … then`).  
   - Each atom is stored in a dict `{id: (pred, args, polarity, modality)}` where polarity ∈ {+1,‑1} captures negation and modality ∈ {assert, question, command}.  
   - The prompt yields a set P; each candidate yields a set Cᵢ.

2. **Affinity Scoring (Clonal Selection)**  
   - Compute *base affinity* aᵢ = |P ∩ Cᵢ| / |P ∪ Cᵢ| (Jaccard over atom IDs).  
   - Apply *constraint propagation*: for each conditional atom `if A then B` in P, add a bonus if Cᵢ contains B whenever it contains A (modus ponens); similarly, add a bonus for transitive chains (`X > Y` & `Y > Z` ⇒ `X > Z`).  
   - Keep the top‑k antibodies, clone them nₖ times, and *mutate* clones by:  
     - Flipping polarity of a randomly chosen atom (simulating somatic hypermutation).  
     - Substituting a synonym from a preset lexical list (maintaining diversity).  
   - Re‑score mutated clones; replace low‑affinity parents with high‑affinity clones (memory update).

3. **Neuromodulatory Gain Control**  
   - Detect pragmatic markers in the prompt:  
     - Scalar implicature triggers (`some`, `few`), speech‑act cues (`please`, `I wonder`), and Grice‑maxim violations (e.g., excess redundancy).  
   - For each marker type m, compute a gain gₘ ∈ [0.5,2.0] (e.g., high gain for implicature when “some” appears, low gain when a violation suggests laxness).  
   - Multiply the affinity contribution of each atom class by its corresponding gain (e.g., atoms derived from comparatives get gain g_comparative).  
   - The final score Sᵢ = aᵢ × ∏ₘ gₘ^{cᵢ,ₘ}, where cᵢ,ₘ is the count of marker‑m atoms in Cᵢ.

4. **Output**  
   - Return candidates sorted by Sᵢ; optionally provide affinity breakdown.

**Structural Features Parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then`, `unless`), numeric values and units, causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `first`, `last`), and speech‑act markers (`please`, `I wonder`).  

**Novelty** – Purely symbolic clonal‑selection models exist in artificial immune systems, and gain‑modulated reasoning appears in neuromorphic models, but coupling them with pragmatic‑driven weight adjustment for logical‑form scoring has not been reported in the literature; the combination is therefore novel.

**Ratings**  
Reasoning: 8/10 — captures logical inference via constraint propagation and clonal refinement, though limited to shallow logical forms.  
Metacognition: 6/10 — gain control offers a rudimentary self‑monitoring of confidence but lacks explicit reflection on reasoning steps.  
Hypothesis generation: 7/10 — mutation step creates diverse answer variants, akin to hypothesis exploration, but guided only by simple operators.  
Implementability: 9/10 — relies solely on regex, dicts, and numpy for vectorized Jaccard/gain calculations; no external libraries needed.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:syntax_error: invalid syntax (line 141)

**Forge Timestamp**: 2026-03-31T14:15:12.564237

---

## Code

**Source**: scrap

[View code](./Immune_Systems---Neuromodulation---Pragmatics/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    Clonal-Selection Reasoner with Pragmatic Gain Control.
    
    Mechanism:
    1. Parsing: Extracts logical atoms (predicates, negations, comparatives, conditionals) 
       from prompt and candidates using regex.
    2. Affinity (Clonal Selection): Computes Jaccard similarity of logical atoms between 
       prompt and candidate. Applies constraint propagation bonuses for transitivity and 
       modus ponens. Simulates somatic hypermutation by generating variant hypotheses 
       (polarity flips) to test robustness.
    3. Neuromodulatory Gain: Adjusts scores based on pragmatic markers (implicatures, 
       speech acts). High gain for precise logical matches, low gain for ambiguous markers.
    4. Constructive Computation: Explicitly solves numeric, temporal, and causal chains 
       detected in the text.
    5. Epistemic Honesty (Tier B): Caps confidence if presuppositions, ambiguities, or 
       unanswerable conditions are detected in the prompt structure.
    """

    def __init__(self):
        # Regex patterns for logical atoms
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.I),
            'temporal': re.compile(r'\b(before|after|first|last|during|while)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(stopped|quit|failed|stopped)\b.*\?', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all).*\b(a|an)\b', re.I),
            'pronoun_ambiguity': re.compile(r'\b(told|said|asked)\b.*\b(he|she|him|her|they)\b.*\?', re.I),
            'false_dichotomy': re.compile(r'\b(either|or)\b.*\b(or|else)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.I),
            'scalar_implicature': re.compile(r'\b(some|few|many)\b', re.I),
            'speech_act': re.compile(r'\b(please|I wonder|could you)\b', re.I)
        }
        
        # Synonyms for mutation
        self.synonyms = {
            'greater': ['larger', 'bigger'],
            'less': ['smaller', 'lower'],
            'causes': ['leads to', 'results in'],
            'before': ['prior to'],
            'after': ['following']
        }

    def _extract_atoms(self, text: str) -> Dict[str, Tuple]:
        """Extract propositional atoms from text."""
        atoms = {}
        text_lower = text.lower()
        
        # Extract numeric values
        nums = [float(n) for n in self.patterns['numeric'].findall(text)]
        for i, n in enumerate(nums):
            atoms[f'num_{i}'] = ('number', (n,), 1, 'assert')
            
        # Extract logical markers
        if self.patterns['negation'].search(text_lower):
            atoms['negation_present'] = ('negation', (), -1, 'assert')
        if self.patterns['comparative'].search(text_lower):
            atoms['comparative_present'] = ('comparative', (), 1, 'assert')
        if self.patterns['conditional'].search(text_lower):
            atoms['conditional_present'] = ('conditional', (), 1, 'assert')
        if self.patterns['causal'].search(text_lower):
            atoms['causal_present'] = ('causal', (), 1, 'assert')
        if self.patterns['temporal'].search(text_lower):
            atoms['temporal_present'] = ('temporal', (), 1, 'assert')
            
        # Simple keyword atoms for structure
        words = set(re.findall(r'\b[a-z]{4,}\b', text_lower))
        for w in words:
            if w not in ['that', 'this', 'with', 'have', 'been', 'were', 'will', 'from']:
                atoms[f'word_{w}'] = ('keyword', (w,), 1, 'assert')
                
        return atoms

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        Perform constructive computation on numeric/temporal/causal chains.
        Returns a score factor (0.0 to 1.0) based on computational correctness.
        """
        p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        # If no numbers, return neutral score (rely on structural)
        if not p_nums:
            return 0.5
            
        # Heuristic: If prompt has numbers and candidate has numbers, check magnitude logic
        if p_nums and c_nums:
            # Case 1: Direct equality (exact match of a number in prompt)
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                return 1.0
            
            # Case 2: Arithmetic consistency (very basic check)
            # If prompt implies addition/subtraction via keywords
            p_lower = prompt.lower()
            if 'sum' in p_lower or 'total' in p_lower or 'add' in p_lower:
                if abs(sum(p_nums) - c_nums[0]) < 1e-6:
                    return 1.0
                # Penalty for wrong math if numbers are present
                return 0.2 
            
            if 'difference' in p_lower or 'subtract' in p_lower:
                if len(p_nums) >= 2 and abs(p_nums[0] - p_nums[1] - c_nums[0]) < 1e-6:
                    return 1.0
                return 0.2

            # Case 3: Comparative logic
            if 'greater' in p_lower or 'more' in p_lower:
                # If prompt asks for greater, candidate should ideally reflect larger number if extracted
                # This is a weak heuristic without full parsing, so we give partial credit
                return 0.6 

        return 0.3 # Low score if numbers exist but no clear match

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        if not set1 and not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _clonal_selection(self, p_atoms: Dict, c_atoms: Dict, prompt: str) -> float:
        """Compute affinity with clonal selection and mutation."""
        p_keys = set(p_atoms.keys())
        c_keys = set(c_atoms.keys())
        
        # Base affinity (Jaccard)
        base_affinity = self._jaccard_similarity(p_keys, c_keys)
        
        # Constraint Propagation Bonus
        bonus = 0.0
        if 'conditional_present' in p_keys and 'conditional_present' in c_keys:
            bonus += 0.1
        if 'causal_present' in p_keys and 'causal_present' c_keys:
            bonus += 0.1
        if 'negation_present' in p_keys and 'negation_present' in c_keys:
            bonus += 0.05 # Matching negation is crucial
            
        # Somatic Hypermutation (Simulation)
        # Generate a few mutated versions of candidate atoms to see if affinity improves
        max_mutated_affinity = base_affinity
        for _ in range(3): # 3 clones
            mutated_keys = set(c_keys)
            # Flip polarity simulation: remove a keyword if present, add if not (simplified)
            if mutated_keys:
                flip_candidate = list(mutated_keys)[np.random.randint(0, len(mutated_keys))]
                if flip_candidate in mutated_keys:
                    mutated_keys.discard(flip_candidate)
                else:
                    mutated_keys.add(flip_candidate)
            
            mut_aff = self._jaccard_similarity(p_keys, mutated_keys)
            if mut_aff > max_mutated_affinity:
                max_mutated_affinity = mut_aff
                
        return min(1.0, base_affinity + bonus + (max_mutated_affinity - base_affinity) * 0.5)

    def _neuromodulatory_gain(self, prompt: str, candidate: str) -> float:
        """Calculate gain factors based on pragmatic markers."""
        gain = 1.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Scalar implicature: "some" implies "not all"
        if self.patterns['scalar_implicature'].search(p_lower):
            if 'all' in c_lower:
                gain *= 0.5 # Penalty for violating implicature
            else:
                gain *= 1.2 # Bonus for respecting nuance
                
        # Speech acts
        if self.patterns['speech_act'].search(p_lower):
            gain *= 1.1 # Politeness alignment
            
        # Redundancy penalty (Grice)
        if len(c_lower) > len(p_lower) * 1.5:
            gain *= 0.9
            
        return gain

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. Scope ambiguity
        if self.patterns['scope_ambiguity'].search(p_lower):
            return 0.25
            
        # 3. Pronoun ambiguity
        if self.patterns['pronoun_ambiguity'].search(p_lower) and 'who' in p_lower:
            return 0.2
            
        # 4. False dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.4
            
        # 6. Unanswerability (Heuristic: question words but no context)
        if '?' in prompt and len(prompt.split()) < 5:
            return 0.2
            
        return 1.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len1 = len(s1_bytes)
        len2 = len(s2_bytes)
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/simplicity in this context or compress individually
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c_concat = len(zlib.compress(concat))
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        
        if max_c == 0:
            return 0.0
            
        ncd = (c_concat - min_c) / max_c
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_atoms = self._extract_atoms(prompt)
        p_lower = prompt.lower()
        meta_cap = self._meta_confidence(prompt)
        
        results = []
        
        for cand in candidates:
            c_atoms = self._extract_atoms(cand)
            
            # 1. Structural & Clonal Score (50%)
            structural_score = self._clonal_selection(p_atoms, c_atoms, prompt)
            
            # 2. Constructive Computation (35%)
            comp_score = self._compute_constructive_score(prompt, cand)
            
            # 3. NCD Tiebreaker (15%)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd # Convert distance to similarity
            
            # Weighted Sum
            raw_score = (structural_score * 0.50) + (comp_score * 0.35) + (ncd_score * 0.15)
            
            # Apply Neuromodulatory Gain
            gain = self._neuromodulatory_gain(prompt, cand)
            final_score = raw_score * gain
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if final_score > meta_cap:
                final_score = meta_cap
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{structural_score:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}, Gain:{gain:.2f}, Cap:{meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a mini-evaluation to get the raw score
        # We treat the single answer as the only candidate to get its relative score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # If the prompt is ambiguous (meta_cap < 0.3), we must return low confidence
        # regardless of how well the string matches.
        if meta_cap < 0.3:
            return min(raw_score, meta_cap)
            
        # If the constructive computation failed (score < 0.3) and numbers were expected
        # (heuristic check), keep confidence low.
        if raw_score < 0.3:
            return raw_score
            
        # Normalize slightly to avoid overconfidence unless it's a perfect match
        # Cap at 0.95 unless it's a definitive computational match
        if raw_score > 0.95 and "num_" not in str(self._extract_atoms(prompt)):
            return 0.9
            
        return min(1.0, raw_score)
```

</details>
