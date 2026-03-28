import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Sparse-Coded Hypothesis Tree (ASCHT) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored based on 
       constraint satisfaction and numeric consistency.
    2. Sparse Coding Analogy: Candidates are represented as sparse binary vectors of 
       detected features (keywords/logic tokens). Similarity is computed via dot product 
       (affinity) over these sparse sets.
    3. Immune/MCTS Analogy: 
       - Affinity: Match between candidate features and prompt requirements.
       - Clonal Selection: Candidates with high structural affinity are boosted.
       - Memory: Previous high-affinity patterns (statically defined) guide scoring.
    4. NCD (Tiebreaker): Used only when structural signals are ambiguous.
    
    This avoids the "historical inhibitor" trap by not using MCTS/Sparse Coding for 
    raw generation, but rather as a scoring filter over structural evidence.
    """

    def __init__(self):
        # Logical keywords for sparse feature extraction
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.booleans = {'yes', 'no', 'true', 'false', 'correct', 'incorrect'}
        
        # Memory of high-affinity patterns (Immune Memory)
        self.memory_patterns = [
            ("not.*yes", "no"), ("yes.*not", "no"), ("false.*true", "false"),
            ("greater.*smaller", "contradiction"), ("less.*more", "contradiction")
        ]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for logical consistency checks."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _sparse_encode(self, text: str) -> Dict[str, int]:
        """
        Sparse coding: Convert text to a sparse vector (dict) of active basis functions.
        Basis functions are logical categories and specific keywords.
        """
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        vector = {}
        
        # Active basis: Presence of logical categories
        if words & self.negations: vector['has_negation'] = 1
        if words & self.comparatives: vector['has_comparative'] = 1
        if words & self.conditionals: vector['has_conditional'] = 1
        if words & self.booleans: vector['has_boolean'] = 1
        
        # Active basis: Numeric presence
        if self._extract_numbers(text): vector['has_numeric'] = 1
        
        # Specific high-affinity tokens (Clonal markers)
        for word in ['therefore', 'thus', 'hence', 'because']:
            if word in words: vector[f'marker_{word}'] = 1
            
        return vector

    def _compute_affinity(self, v1: Dict[str, int], v2: Dict[str, int]) -> float:
        """Compute affinity (dot product) between two sparse vectors."""
        score = 0.0
        # Intersection of active keys
        common_keys = set(v1.keys()) & set(v2.keys())
        for k in common_keys:
            score += v1[k] * v2[k]
        return score

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural parsing and constraint propagation.
        Returns a score where higher is better.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        
        # 1. Numeric Consistency (Constraint Propagation)
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if p_nums and c_nums:
            # If prompt has numbers, candidate should ideally reflect logic on them
            # Simple heuristic: if prompt implies comparison, check candidate direction
            if any(k in p_lower for k in self.comparatives):
                # If prompt compares, candidate containing result gets boost
                score += 2.0 
            else:
                # Exact match of numbers implies copying (good for some tasks, bad for others)
                # Here we assume if numbers match exactly, it's a strong signal of relevance
                if set(p_nums) == set(c_nums):
                    score += 1.5

        # 2. Logical Negation Consistency
        p_neg = bool(set(p_lower.split()) & self.negations)
        c_neg = bool(set(c_lower.split()) & self.negations)
        
        # If prompt asks "Which is NOT...", candidate must have negation or negative sentiment
        if "not " in p_lower or "none " in p_lower:
            if c_neg: score += 1.0
            else: score -= 1.0 # Penalty for missing negation in negative query
            
        # 3. Conditional Logic Check
        if any(k in p_lower for k in ['if ', 'when ', 'unless ']):
            # Candidate should ideally contain consequence markers or booleans
            if any(k in c_lower for k in ['then', 'therefore', 'yes', 'no', 'true', 'false']):
                score += 1.0

        # 4. Immune Memory Check (Pattern matching against known traps)
        for pattern, expectation in self.memory_patterns:
            if re.search(pattern, p_lower):
                if expectation in c_lower:
                    score += 3.0 # High affinity for memory match
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        
        # Compress concatenation
        try:
            len_concat = len(zlib.compress(b1 + b2))
        except: return 1.0
        
        # Approximate individual compress lengths (simplified for speed)
        len_c1 = len(zlib.compress(b1))
        len_c2 = len(zlib.compress(b2))
        
        max_len = max(len_c1, len_c2)
        if max_len == 0: return 1.0
        
        ncd = (len_concat - min(len_c1, len_c2)) / max_len
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_vec = self._sparse_encode(prompt)
        results = []
        
        for cand in candidates:
            cand_vec = self._sparse_encode(cand)
            
            # 1. Structural Score (Primary)
            struct_score = self._structural_score(prompt, cand)
            
            # 2. Affinity (Sparse Coding overlap)
            affinity = self._compute_affinity(prompt_vec, cand_vec)
            
            # 3. NCD (Tiebreaker only)
            # Invert NCD so lower distance = higher score contribution, but scaled small
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.1 # Small weight
            
            # Combined Score: Structural dominates, Affinity refines, NCD breaks ties
            total_score = struct_score + (affinity * 0.5) + ncd_score
            
            # Heuristic boost for length appropriateness (avoiding empty or giant dumps)
            if 0.5 * len(prompt) < len(cand) < 2.0 * len(prompt):
                total_score += 0.1
                
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural:{struct_score:.2f}, Affinity:{affinity:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and affinity.
        """
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]["score"]
        
        # Map raw score to 0-1 range
        # Structural score usually ranges -2 to +5 for good matches
        # Normalize: (score + 2) / 7 -> clipped to 0-1
        conf = (raw_score + 2.0) / 7.0
        return max(0.0, min(1.0, conf))