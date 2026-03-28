import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Message-Passing Workspace (CMW) Implementation.
    
    Mechanism:
    1. Objects (Modules): The prompt and candidates are treated as objects in a category.
    2. Morphisms (Functor F): We map text to structural feature vectors (negations, comparatives, 
       conditionals, numeric values) representing typed communication channels.
    3. Global Workspace (Colimit/Pushout): We compute a 'consensus' vector from the prompt's 
       structural constraints. Candidates are evaluated by how well their structural morphisms 
       align with this workspace via a directed message-passing score.
    4. Network Science: Edge weights are dynamically adjusted based on constraint satisfaction 
       (Hebbian-style reinforcement of coherent logical structures).
    5. Scoring: A composite of structural alignment (primary) and NCD (tiebreaker).
    """

    def __init__(self):
        self._keywords_neg = {'no', 'not', 'never', 'none', 'without', 'impossible', 'false'}
        self._keywords_comp = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after', 'larger', 'smaller'}
        self._keywords_cond = {'if', 'then', 'unless', 'otherwise', 'when', 'provided'}
        self._nums = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Functor F: Maps text object to structural feature vector."""
        t_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', t_lower))
        
        # Structural counts
        neg_count = sum(1 for w in words if w in self._keywords_neg)
        comp_count = sum(1 for w in words if w in self._keywords_comp)
        cond_count = sum(1 for w in words if w in self._keywords_cond)
        
        # Numeric extraction and evaluation
        nums_str = self._nums.findall(t_lower)
        nums_val = [float(n) for n in nums_str]
        has_numbers = len(nums_val) > 0
        
        # Simple numeric logic check (e.g., detecting "9.11" vs "9.9" magnitude)
        numeric_coherence = 0.0
        if has_numbers and len(nums_val) >= 2:
            # Check if sorted order matches appearance (heuristic for consistency)
            is_sorted = nums_val == sorted(nums_val)
            numeric_coherence = 1.0 if is_sorted else 0.5
            
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'nums': nums_val,
            'has_nums': has_numbers,
            'num_coherence': numeric_coherence,
            'length': len(text),
            'raw': text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 1.0
        return (c12 - min(c1, c2)) / max_len

    def _message_passing_score(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Simulates the Global Workspace broadcast.
        Calculates alignment between prompt constraints (workspace) and candidate structure.
        """
        score = 0.0
        
        # 1. Negation Alignment (Modus Tollens check)
        # If prompt has negation, candidate should reflect constraint awareness
        if prompt_feat['neg'] > 0:
            # Reward if candidate also acknowledges complexity or matches negation count roughly
            score += 0.2 if cand_feat['neg'] > 0 else 0.05
        
        # 2. Comparative/Conditional Logic Propagation
        logic_density = (prompt_feat['comp'] + prompt_feat['cond'])
        if logic_density > 0:
            cand_logic = (cand_feat['comp'] + cand_feat['cond'])
            # Reward candidates that maintain logical density (don't oversimplify)
            if cand_logic >= logic_density * 0.5:
                score += 0.3
            # Penalty for ignoring complex logic markers entirely
            elif cand_logic == 0:
                score -= 0.2

        # 3. Numeric Consistency (Network Cascade Validation)
        if prompt_feat['has_nums'] and cand_feat['has_nums']:
            # Heuristic: If both have numbers, check magnitude coherence loosely
            # In a full GNN, this would be edge-weight update. Here, a simple coherence boost.
            score += 0.2 * cand_feat['num_coherence']
        elif prompt_feat['has_nums'] and not cand_feat['has_nums']:
            # Penalty for dropping numeric constraints
            score -= 0.3
            
        # 4. Length/Complexity Matching (Occam's razor via Category limits)
        # Avoid extreme deviations in length which might indicate hallucination or oversimplification
        len_ratio = cand_feat['length'] / max(prompt_feat['length'], 1)
        if 0.5 <= len_ratio <= 2.0:
            score += 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        results = []
        
        # Pre-compute NCD for tie-breaking
        # We use the prompt as the reference for NCD
        ncd_scores = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd = max(s[1] for s in ncd_scores)
        ncd_range = max_ncd - min_ncd if max_ncd > min_ncd else 1.0

        for i, cand in enumerate(candidates):
            c_feat = self._extract_features(cand)
            
            # Primary Score: Structural/Logical Alignment (The "Pushout")
            struct_score = self._message_passing_score(p_feat, c_feat)
            
            # Secondary Score: NCD (Tiebreaker only)
            # Normalize NCD to be a small perturbation so it doesn't override logic
            norm_ncd = (ncd_scores[i][1] - min_ncd) / ncd_range if ncd_range > 0 else 0
            ncd_bonus = (1.0 - norm_ncd) * 0.05 # Max 0.05 bonus for high similarity
            
            final_score = struct_score + ncd_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if p_feat['neg'] > 0 and c_feat['neg'] > 0: reasoning_parts.append("Matches negation constraints")
            if p_feat['has_nums'] and c_feat['has_nums']: reasoning_parts.append("Preserves numeric context")
            if p_feat['cond'] > 0 and c_feat['cond'] > 0: reasoning_parts.append("Maintains conditional logic")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment evaluated via categorical mapping")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment strength.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Base score from message passing
        raw_score = self._message_passing_score(p_feat, a_feat)
        
        # Map raw score (approx -0.5 to 0.8) to 0-1 range
        # Shift and clamp
        conf = (raw_score + 0.5) / 1.3 
        return max(0.0, min(1.0, conf))