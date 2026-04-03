import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Falsificationism (core scorer), Criticality (sensitivity analysis),
    and Compressed Sensing (structural parsing support only, per safety constraints).
    
    Mechanism:
    1. Parses propositions (negations, comparatives, numerics, etc.) from reference and candidates.
    2. Falsification Score: Penalizes direct contradictions between candidate and reference propositions.
    3. Criticality Score: Measures the 'susceptibility' of the logical structure. Uses a sparse dictionary
       approach (inspired by compressed sensing) to model the proposition space, then computes the 
       inverse of the max singular value of the active set. High susceptibility = near critical point = 
       fine-grained discrimination capability.
    4. Structural Overlap: Rewards matching logical forms.
    5. NCD Tiebreaker: Used only if structural signals are weak.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|>\|<)\b', re.I),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|thus|hence|leads to|results in|causes)\b', re.I),
            'ordering': re.compile(r'\b(before|after|precede|follow)\b', re.I),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*')
        }
        self.pred_types = list(self.patterns.keys())
        self.n_types = len(self.pred_types)

    def _hash_arg(self, s: str) -> int:
        """Simple hash for arguments mod 10000."""
        return hash(s.lower().strip()) % 10000

    def _extract_props(self, text: str) -> List[Tuple[str, int, bool]]:
        """
        Extracts propositions as (pred_type, arg_hash, polarity).
        Polarity is True for positive assertion, False for negation.
        """
        props = []
        text_lower = text.lower()
        
        # Check negations first to toggle polarity context if needed, 
        # but here we treat 'negation' as a specific proposition type.
        
        for p_type, regex in self.patterns.items():
            matches = regex.findall(text)
            for match in matches:
                # Determine polarity: if the match itself is a negation word, polarity is False
                # Otherwise, check if it's preceded by a negation word in a simple window
                is_neg_word = p_type == 'negation' or match in ['not', 'no', 'never', 'none', 'neither']
                
                # Simple local context check for negation preceding other types
                polarity = True
                if not is_neg_word:
                    # Check if "not" appears within 3 words before the match
                    idx = text_lower.find(match)
                    if idx != -1:
                        prefix = text_lower[max(0, idx-30):idx]
                        if re.search(r'\b(not|no|never)\b', prefix):
                            polarity = False
                
                props.append((p_type, self._hash_arg(match), polarity))
        
        return props

    def _build_dictionary_matrix(self, all_props: List[Tuple]) -> np.ndarray:
        """
        Builds a dictionary matrix D where columns represent proposition types.
        Adds small Gaussian noise to avoid collinearity (Compressed Sensing inspiration).
        """
        n_cols = self.n_types
        # Rows: distinct argument hashes encountered (simplified to fixed size for stability or dynamic)
        # To keep it simple and deterministic without global state explosion, we map types to vectors
        # and perturb them. 
        # Actual CS implementation: D is m x n. m = slots, n = vocab.
        # Here, we simulate the "active set" logic using type presence.
        
        D = np.zeros((self.n_types, self.n_types))
        for i in range(self.n_types):
            # One-hot with noise
            col = np.zeros(self.n_types)
            col[i] = 1.0
            col += np.random.normal(0, 0.01, self.n_types)
            D[:, i] = col
        return D

    def _compute_criticality(self, ref_props: List, cand_props: List) -> float:
        """
        Computes susceptibility S = 1 / (sigma_max + delta).
        Uses the intersection of proposition types as the 'active set'.
        """
        if not ref_props or not cand_props:
            return 0.0
            
        # Identify active types
        ref_types = set(p[0] for p in ref_props)
        cand_types = set(p[0] for p in cand_props)
        active_types = list(ref_types.intersection(cand_types))
        
        if not active_types:
            return 0.0
            
        # Build sub-matrix for active types
        D_sub = []
        for t in active_types:
            idx = self.pred_types.index(t)
            vec = np.zeros(len(active_types))
            # Simulate the column from the theoretical D restricted to active set
            # In a full CS implementation, this would be the actual dictionary atoms.
            # Here we approximate with identity + noise structure for the active subset.
            local_idx = active_types.index(t)
            vec[local_idx] = 1.0
            vec += np.random.normal(0, 0.005, len(active_types))
            D_sub.append(vec)
            
        if not D_sub:
            return 0.0
            
        J = np.array(D_sub)
        try:
            # SVD to find largest singular value
            sigma_max = np.linalg.svd(J, compute_uv=False)[0]
            delta = 1e-6
            S = 1.0 / (sigma_max + delta)
            return S
        except Exception:
            return 0.0

    def _compute_falsification_score(self, ref_props: List, cand_props: List) -> float:
        """
        Calculates penalty for contradictions.
        Matches propositions by type and argument hash. If polarity differs, it's a falsification.
        """
        if not ref_props:
            return 0.0
            
        ref_map = {}
        for p_type, arg_h, polarity in ref_props:
            key = (p_type, arg_h)
            # Store polarity; if multiple, store list (simplified to last for now)
            ref_map[key] = polarity
            
        mismatches = 0
        total_checked = 0
        
        for p_type, arg_h, polarity in cand_props:
            key = (p_type, arg_h)
            if key in ref_map:
                total_checked += 1
                if ref_map[key] != polarity:
                    mismatches += 1
        
        # Avoid division by zero, but if no overlap, falsification is 0 (no claim to contradict)
        if total_checked == 0:
            return 0.0
            
        falsification_ratio = mismatches / total_checked
        return -1.0 * falsification_ratio # Negative penalty

    def _compute_structural_overlap(self, ref_props: List, cand_props: List) -> float:
        if not ref_props:
            return 0.0
        ref_set = set((p[0], p[1], p[2]) for p in ref_props)
        cand_set = set((p[0], p[1], p[2]) for p in cand_props)
        intersection = ref_set.intersection(cand_set)
        # Jaccard-like score
        union = ref_set.union(cand_set)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Extract reference propositions from prompt (assuming prompt contains the ground truth context)
        # In many QA setups, the 'prompt' includes the context/reference. 
        # If the prompt is just a question, we treat the candidate's alignment to the prompt's constraints.
        # For this tool, we assume the prompt contains the reference logic to check against.
        ref_props = self._extract_props(prompt)
        
        results = []
        scores = []
        
        for cand in candidates:
            cand_props = self._extract_props(cand)
            
            # 1. Falsification Core (Popperian)
            falsification_score = self._compute_falsification_score(ref_props, cand_props)
            
            # 2. Criticality (Susceptibility)
            criticality_score = self._compute_criticality(ref_props, cand_props)
            
            # 3. Structural Overlap
            overlap_score = self._compute_structural_overlap(ref_props, cand_props)
            
            # 4. NCD Tiebreaker (only if structural signals are low)
            ncd_score = 0.0
            if overlap_score < 0.1 and falsification_score == 0:
                ncd_score = -self._ncd(prompt, cand) # Lower NCD is better, so negate
            
            # Combined Score
            # Weights: Falsification is critical (-1 to 0), Criticality adds bonus, Overlap is base
            score = (2.0 * overlap_score) + (1.5 * falsification_score) + (0.5 * criticality_score) + (0.1 * ncd_score)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Falsification:{falsification_score:.2f}, Criticality:{criticality_score:.2f}, Overlap:{overlap_score:.2f}"
            })
            scores.append(score)
        
        # Rank by score descending
        sorted_indices = np.argsort(scores)[::-1]
        return [results[i] for i in sorted_indices]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score normalized.
        Uses the same logic as evaluate but for a single candidate.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Normalize heuristic: 
        # Overlap is 0-1, Falsification is -1 to 0, Criticality is small positive.
        # Max theoretical score approx 2.0 (perfect overlap) + 0 (no falsification) + bonus.
        # Min theoretical score approx -1.5 (total contradiction).
        # Map [-2, 3] roughly to [0, 1]
        
        confidence = (raw_score + 2.0) / 5.0
        return max(0.0, min(1.0, confidence))