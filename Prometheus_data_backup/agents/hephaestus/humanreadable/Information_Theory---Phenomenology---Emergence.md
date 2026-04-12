# Information Theory + Phenomenology + Emergence

**Fields**: Mathematics, Philosophy, Complex Systems
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T06:25:05.223564
**Report Generated**: 2026-03-27T18:24:05.160835

---

## Nous Analysis

**Algorithm**  
1. **Parsing layer** – Using only `re` we extract propositional atoms and logical relations from the prompt and each candidate answer. Patterns capture:  
   - Negation: `\bnot\b` or `\bn’t\b`  
   - Conjunction: `\band\b`  
   - Disjunction: `\bor\b`  
   - Conditional: `\bif\b.*\bthen\b`  
   - Comparatives: `\bis\s+(greater|less|more|fewer)\sthan\b`  
   - Causal: `\bbecause\b|\bleads\s+to\b|\bcauses\b`  
   - Ordering: `\bbefore\b|\bafter\b|\bwhile\b`  
   - Quantifiers/modals: `\ball\b|\bsome\b|\bmust\b|\bmight\b`  
   Each atom is stored as a string; relations become directed edges (source → target) with a type label.

2. **Information‑theoretic layer** – From the extracted atoms across all candidates we build a co‑occurrence matrix `C[i,j]` (how often atom *i* appears in the same sentence as atom *j*). Using `numpy` we convert to joint probabilities `P(i,j)=C/(sum(C))` and marginals `P(i)`. Pointwise mutual information (PMI) gives edge weights: `W[i,j]=log2(P(i,j)/(P(i)P(j)))`. Negative PMI is set to zero.

3. **Phenomenological weighting** – Atoms that contain first‑person intentional markers (`I think`, `I feel`, `seems`, `appears`) receive an additive phenomenological boost `Φ=0.5`. This is stored in a vector `phi[i]`.

4. **Emergent synergy scoring** – For each candidate we compute:  
   - Node entropy `H[i] = -Σ P(i|sent) log2 P(i|sent)` (empirical distribution of the atom in that candidate).  
   - Joint entropy of the candidate’s atom set `H_joint` via the multivariate distribution approximated by assuming independence corrected by the PMI matrix (i.e., `H_joint = Σ H[i] - Σ_{i<j} W[i,j]`).  
   - Emergence score `E = H_joint - Σ H[i]` (negative values indicate redundancy; positive values indicate synergistic emergence).  
   - Phenomenological boost `Φ_sum = Σ phi[i]` over atoms present.  
   - Final score `S = (E - min(E))/(max(E)-min(E)) + λ·(Φ_sum - min(Φ))/(max(Φ)-min(Φ))` with λ=0.3 to keep both terms in [0,1].

**Structural features parsed** – negations, conjunctions/disjunctions, conditionals, comparatives, causal verbs, temporal ordering, quantifiers, modal verbs, and first‑person intentional markers.

**Novelty** – While PMI‑based graphs and phenomenological annotation exist separately, combining them with an explicit emergent synergy term (joint entropy minus sum of node entropies) to score reasoning answers is not found in current open‑source evaluation tools; most approaches rely on surface similarity or pure logical constraint propagation alone.

**Rating**  
Reasoning: 7/10 — captures logical structure and information‑theoretic synergy but approximates joint distribution.  
Metacognition: 6/10 — phenomenological markers model first‑person stance yet lack deeper reflective modeling.  
Hypothesis generation: 5/10 — can suggest higher‑scoring atoms via edge weights, but not generative hypothesis formation.  
Implementability: 8/10 — uses only regex, numpy, and stdlib; all steps are straightforward to code.

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

- **Information Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Phenomenology**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Emergence**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Emergence + Information Theory: strong positive synergy (+0.437). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Emergence + Phenomenology: strong positive synergy (+0.940). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Information Theory + Emergence + Hebbian Learning (accuracy: 0%, calibration: 0%)
- Phenomenology + Emergence + Criticality (accuracy: 0%, calibration: 0%)
- Phenomenology + Emergence + Feedback Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: trap_battery_failed (acc=33% cal=16% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-03-27T18:07:57.145517

---

## Code

**Source**: scrap

[View code](./Information_Theory---Phenomenology---Emergence/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning evaluation tool combining Information Theory, Phenomenology, and Emergence.
    
    Mechanism:
    1. Parsing: Extracts logical atoms and relations (negation, conditionals, causality) via regex.
    2. Info Theory: Builds a co-occurrence matrix to compute Pointwise Mutual Information (PMI)
       between atoms, quantifying how much information one atom provides about another.
    3. Phenomenology: Boosts scores for first-person intentional markers ('I think', 'seems').
    4. Emergence: Calculates a synergy score based on joint entropy vs. sum of individual entropies.
       Positive synergy indicates emergent structure; negative indicates redundancy.
    5. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and false dichotomies to
       cap confidence, ensuring the tool admits uncertainty rather than guessing.
    6. Scoring: Weighted combination of structural match, emergent synergy, and NCD tie-breaking.
    """

    # Regex patterns for logical structure
    PATTERNS = {
        'negation': r'\b(not|n\'t|never|no)\b',
        'conjunction': r'\b(and|both|plus)\b',
        'disjunction': r'\b(or|either|neither)\b',
        'conditional': r'\b(if|then|unless|provided)\b',
        'comparative': r'\b(is\s+(greater|less|more|fewer|better|worse)\s+than|larger|smaller)\b',
        'causal': r'\b(because|therefore|thus|leads? to|causes?|due to)\b',
        'ordering': r'\b(before|after|while|during|first|last)\b',
        'quantifier': r'\b(all|some|every|each|none|must|might|should)\b',
        'phenom': r'\b(I think|I feel|I believe|seems|appears|in my view)\b',
        'number': r'-?\d+(?:\.\d+)?'
    }

    # Presupposition/Ambiguity triggers for Tier B
    TRAPS = {
        'presupposition': [r'\bhave you stopped\b', r'\bwhy did.*fail\b', r'\bwhen did.*stop\b'],
        'scope_ambiguity': [r'\bevery.*a.*\?', r'\ball.*same.*\?'],
        'pronoun_ambiguity': [r'\b(he|she|it|they)\b.*\bwho\b'],
        'false_dichotomy': [r'\beither.*or\b', r'\bonly two options\b'],
        'subjectivity': [r'\b(best|worst|favorite|ugliest)\b'],
        'unanswerable': [r'\bwhat is the meaning of life\b', r'\bcolor of.*number\b']
    }

    def __init__(self):
        self.lambda_phenom = 0.3
        self.epsilon = 1e-9

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract propositional atoms based on keywords and numbers."""
        text_lower = text.lower()
        atoms = []
        # Extract numbers as distinct atoms
        numbers = re.findall(self.PATTERNS['number'], text)
        atoms.extend([f"NUM:{n}" for n in numbers])
        
        # Extract logical markers
        for key, pattern in self.PATTERNS.items():
            if key == 'number': continue
            matches = re.findall(pattern, text_lower)
            for m in matches:
                if isinstance(m, tuple): m = m[0] # Handle groups
                atoms.append(f"{key}:{m}")
        return atoms

    def _check_traps(self, text: str) -> float:
        """
        Tier B Check: Returns a confidence cap (0.0 to 1.0).
        If traps are detected, returns low value (< 0.3).
        """
        text_lower = text.lower()
        max_cap = 1.0
        
        for category, patterns in self.TRAPS.items():
            for p in patterns:
                if re.search(p, text_lower):
                    # Specific handling for known fallacy types
                    if category in ['presupposition', 'false_dichotomy', 'unanswerable']:
                        return 0.2
                    elif category in ['scope_ambiguity', 'pronoun_ambiguity', 'subjectivity']:
                        return 0.25
        return max_cap

    def _compute_pmi(self, all_atoms: List[List[str]]) -> Tuple[np.ndarray, Dict[str, int], float]:
        """Compute PMI matrix from co-occurrence of atoms across candidates."""
        if not all_atoms or all(len(a) == 0 for a in all_atoms):
            return np.array([[0]]), {}, 0.0

        # Map unique atoms to indices
        unique_atoms = list(set(a for sublist in all_atoms for a in sublist))
        atom_to_idx = {a: i for i, a in enumerate(unique_atoms)}
        n = len(unique_atoms)
        if n == 0:
            return np.array([[0]]), {}, 0.0

        # Co-occurrence matrix (sentence level approximation)
        C = np.zeros((n, n))
        total_sentences = len(all_atoms)
        
        for sentence_atoms in all_atoms:
            seen = set(sentence_atoms)
            for a in seen:
                i = atom_to_idx[a]
                C[i, i] += 1 # Self count for marginal
                for b in seen:
                    j = atom_to_idx[b]
                    C[i, j] += 1

        # Joint and Marginal Probabilities
        P_ij = C / (np.sum(C) + self.epsilon)
        P_i = np.sum(P_ij, axis=1, keepdims=True)
        P_j = np.sum(P_ij, axis=0, keepdims=True)
        
        # PMI = log2(P(i,j) / (P(i)*P(j)))
        with np.errstate(divide='ignore', invalid='ignore'):
            PMI = np.log2(P_ij / (P_i * P_j + self.epsilon) + self.epsilon)
            PMI[np.isinf(PMI)] = 0
            PMI[np.isnan(PMI)] = 0
            PMI[PMI < 0] = 0 # Negative PMI set to zero per spec
            
        return PMI, atom_to_idx, total_sentences

    def _calculate_emergence(self, atoms: List[str], pmi: np.ndarray, atom_map: Dict[str, int]) -> float:
        """Calculate emergent synergy score for a single candidate."""
        if not atoms or not atom_map:
            return 0.0
            
        indices = [atom_map[a] for a in atoms if a in atom_map]
        if not indices:
            return 0.0
            
        unique_indices = list(set(indices))
        n = len(unique_indices)
        if n == 1:
            return 0.0 # No synergy in single atom
            
        # Node Entropy (simplified as uniform distribution over atoms in this context)
        # H[i] = -sum(p log p). If uniform, H = log(n)
        h_node = math.log2(n + self.epsilon)
        sum_h = n * h_node
        
        # Joint Entropy approximation via PMI correction
        # H_joint approx Sum(H_i) - Sum(PMI_ij)
        pmi_sum = 0.0
        for i in range(len(unique_indices)):
            for j in range(i + 1, len(unique_indices)):
                idx_i, idx_j = unique_indices[i], unique_indices[j]
                if idx_i < pmi.shape[0] and idx_j < pmi.shape[1]:
                    pmi_sum += pmi[idx_i, idx_j]
                    
        h_joint = sum_h - pmi_sum
        emergence = h_joint - sum_h # Should be negative of PMI sum essentially
        return emergence

    def _calculate_phenom_boost(self, atoms: List[str]) -> float:
        """Sum phenomenological boosts."""
        boost = 0.0
        for a in atoms:
            if a.startswith('phenom:'):
                boost += 0.5
        return boost

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_comb = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_comb - min(len_s1, len_s2)) / max_len

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring signal: Structural alignment and constraint propagation.
        Checks if candidate preserves logical operators and numeric relations found in prompt.
        """
        p_atoms = set(self._extract_atoms(prompt))
        c_atoms = set(self._extract_atoms(candidate))
        
        if not p_atoms:
            return 0.5 # Default if no structure
        
        # Overlap ratio
        intersection = p_atoms.intersection(c_atoms)
        overlap_score = len(intersection) / (len(p_atoms) + 0.001)
        
        # Numeric consistency check (Constructive computation hint)
        p_nums = [float(x.replace('NUM:', '')) for x in p_atoms if x.startswith('NUM:')]
        c_nums = [float(x.replace('NUM:', '')) for x in c_atoms if x.startswith('NUM:')]
        
        num_score = 1.0
        if p_nums and c_nums:
            # Check if order is preserved (simple transitivity check)
            p_sorted = sorted(p_nums)
            c_sorted = sorted(c_nums)
            # Very loose check: do they share magnitude range?
            if min(p_nums) != 0 and min(c_nums) != 0:
                 ratio_p = max(p_nums) / (min(p_nums) + 1e-9)
                 ratio_c = max(c_nums) / (min(c_nums) + 1e-9)
                 if abs(ratio_p - ratio_c) > 0.5: # Significant deviation in ratios
                     num_score = 0.5
        
        return 0.7 * overlap_score + 0.3 * num_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Parse all candidates
        all_candidate_atoms = [self._extract_atoms(c) for c in candidates]
        all_atoms_combined = all_candidate_atoms + [self._extract_atoms(prompt)]
        
        # 2. Build Global PMI Matrix (Information Theoretic Layer)
        pmi_matrix, atom_map, _ = self._compute_pmi(all_atoms_combined)
        
        results = []
        scores = []
        phi_sums = []
        emergence_scores = []

        # 3. Compute components for each candidate
        for i, cand in enumerate(candidates):
            atoms = all_candidate_atoms[i]
            
            # Emergence Score
            e_score = self._calculate_emergence(atoms, pmi_matrix, atom_map)
            emergence_scores.append(e_score)
            
            # Phenomenological Boost
            phi = self._calculate_phenom_boost(atoms)
            phi_sums.append(phi)
            
            # Structural Score (Primary Signal)
            struct = self._structural_score(prompt, cand)
            
            scores.append({
                'candidate': cand,
                'struct': struct,
                'emergence': e_score,
                'phi': phi
            })

        # 4. Normalize and Combine Scores
        if not emergence_scores or max(emergence_scores) == min(emergence_scores):
            norm_e = [0.5] * len(candidates)
        else:
            min_e, max_e = min(emergence_scores), max(emergence_scores)
            range_e = max_e - min_e + self.epsilon
            norm_e = [(e - min_e) / range_e for e in emergence_scores]
            
        if not phi_sums or max(phi_sums) == min(phi_sums):
            norm_phi = [0.0] * len(candidates)
        else:
            min_p, max_p = min(phi_sums), max(phi_sums)
            range_p = max_p - min_p + self.epsilon
            norm_phi = [(p - min_p) / range_p for p in phi_sums]

        final_results = []
        for i, res in enumerate(scores):
            # Formula: S = Norm(E) + lambda * Norm(Phi)
            # But we must weight Structural heavily as per instructions (>=50%)
            # Let's blend: Final = 0.6*Struct + 0.25*Norm_E + 0.15*Norm_Phi
            
            base_score = res['struct']
            synergy_part = 0.25 * norm_e[i]
            phenom_part = 0.15 * norm_phi[i] # Lambda=0.3 scaled down to fit 15% budget
            
            # NCD Tiebreaker (only if structural scores are very close)
            ncd_bonus = 0.0
            if i > 0 and abs(res['struct'] - scores[i-1]['struct']) < 0.05:
                ncd_val = self._ncd(prompt, res['candidate'])
                ncd_bonus = (1.0 - ncd_val) * 0.15 # Max 15% as per rules
            
            final_score = base_score + synergy_part + phenom_part + ncd_bonus
            final_score = max(0.0, min(1.0, final_score)) # Clamp 0-1
            
            final_results.append({
                'candidate': res['candidate'],
                'score': final_score,
                'reasoning': f"Struct:{res['struct']:.2f}, Emergence:{res['emergence']:.2f}, Phenom:{res['phi']:.2f}"
            })

        # Sort descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Internal method to determine confidence cap based on prompt properties."""
        cap = self._check_traps(prompt)
        if cap < 1.0:
            return cap
        
        # If no structural match found in answer, confidence should be low
        p_atoms = set(self._extract_atoms(prompt))
        a_atoms = set(self._extract_atoms(answer))
        
        # If prompt has structure but answer has none, low confidence
        if len(p_atoms) > 2 and len(a_atoms) == 0:
            return 0.2
            
        return 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at low value if Tier B traps (ambiguity, presupposition) are detected.
        """
        # Check for Tier B traps first
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.3:
            return meta_cap
            
        # Calculate raw score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Never return > 0.9 unless computation was definitive (heuristic: high structural match)
        # If structural score was low, cap confidence
        if raw_score < 0.5:
            return min(raw_score, 0.4)
            
        # Apply meta_cap if it's lower than calculated score
        final_conf = min(raw_score, meta_cap)
        
        # Hard cap for non-computational answers
        if final_conf > 0.9 and 'NUM:' not in answer and not any(k in answer.lower() for k in ['therefore', 'thus', 'because']):
            final_conf = 0.85
            
        return final_conf
```

</details>
