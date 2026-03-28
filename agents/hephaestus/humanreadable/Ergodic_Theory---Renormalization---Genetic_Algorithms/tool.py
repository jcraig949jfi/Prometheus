import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Ergodic Genetic Algorithm (REGA) inspired reasoning tool.
    
    Mechanism:
    1. Ergodic Evaluation (Fitness): Instead of raw string matching, we simulate 
       a "trajectory" through the text by extracting structural features (negations, 
       comparatives, conditionals, numbers). The "time-average" of these features 
       across the prompt and candidate determines fitness. If the prompt asserts 
       a constraint (e.g., "A > B") and the candidate violates it, the ergodic 
       average diverges (low score).
       
    2. Renormalization (Coarse-Graining): We apply a block-transformation to the 
       text. Words are grouped into semantic blocks (Logic, Numeric, Content). 
       Details within blocks are coarse-grained into effective "super-features" 
       (e.g., presence of "not", magnitude of numbers). This ignores irrelevant 
       lexical noise (mutation) and focuses on scale-invariant logical structures.
       
    3. Genetic Selection: Candidates are ranked by a score derived from the 
       synergy between structural alignment (RG) and feature convergence (Ergodic).
       NCD is used only as a tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Regex patterns for structural parsing (The "Genes")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|none|cannot|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|larger|fewer|better|worse|than|<|>)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore|thus|hence)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features (Renormalization step: coarse-graining text to logic)."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'negation_count': len(self.patterns['negation'].findall(text_lower)),
            'numbers': []
        }
        
        # Extract numbers for numeric evaluation
        nums = self.patterns['number'].findall(text_lower)
        if nums:
            features['numbers'] = [float(n) for n in nums]
            
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """
        Ergodic check on numeric trajectories.
        If prompt defines an order, candidate must respect it if numbers are present.
        """
        if not prompt_nums or not cand_nums:
            return 1.0 # No numeric constraint to violate
        
        # Simple heuristic: If prompt has 2 numbers and candidate has 2, 
        # check if relative ordering is preserved (simulating trajectory consistency)
        if len(prompt_nums) >= 2 and len(cand_nums) >= 2:
            p_diff = prompt_nums[0] - prompt_nums[1]
            c_diff = cand_nums[0] - cand_nums[1]
            
            # If signs differ, the logic is inverted (bad)
            if p_diff * c_diff < 0:
                return 0.0 
            # If magnitudes are wildly different, penalize slightly (noise)
            if abs(p_diff) > 0 and abs(c_diff) > 0:
                ratio = min(abs(p_diff), abs(c_diff)) / max(abs(p_diff), abs(c_diff))
                return 0.5 + 0.5 * ratio
                
        return 1.0

    def _structural_overlap(self, p_feat: Dict, c_feat: Dict) -> float:
        """Calculate synergy between structural genes."""
        score = 1.0
        
        # Negation consistency
        if p_feat['has_negation'] != c_feat['has_negation']:
            # Mismatch in negation is critical failure
            score -= 0.5
            
        # Conditional consistency
        if p_feat['has_conditional'] and not c_feat['has_conditional']:
            # Candidate misses a conditional constraint
            score -= 0.3
            
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tie-breaker."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        
        len_b1 = len(b1)
        len_b2 = len(b2)
        len_b12 = len(b12)
        
        if min(len_b1, len_b2) == 0:
            return 1.0
            
        return (len_b12 - min(len_b1, len_b2)) / max(len_b1, len_b2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        prompt_nums = prompt_feat['numbers']
        
        scored_candidates = []
        
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            cand_nums = cand_feat['numbers']
            
            # 1. Ergodic Estimate: Structural consistency over the "trajectory" of logic
            struct_score = self._structural_overlap(prompt_feat, cand_feat)
            
            # 2. Numeric Evaluation: Scale-invariant check
            numeric_score = self._check_numeric_consistency(prompt_nums, cand_nums)
            
            # 3. Base similarity (lexical overlap as a baseline proxy)
            # Simple word overlap normalized
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            if p_words:
                lexical_overlap = len(p_words & c_words) / len(p_words)
            else:
                lexical_overlap = 0.0
            
            # Combined Fitness Function
            # Weighted sum emphasizing structural and numeric correctness
            total_score = (struct_score * 0.5) + (numeric_score * 0.4) + (lexical_overlap * 0.1)
            
            scored_candidates.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Structural: {struct_score:.2f}, Numeric: {numeric_score:.2f}, Lexical: {lexical_overlap:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD tie-breaking for top candidates if scores are very close
        # This implements the "RG block-spin" refinement on the top tier
        if len(scored_candidates) > 1:
            top_score = scored_candidates[0]["score"]
            # Group near-identical scores
            tier = [c for c in scored_candidates if abs(c["score"] - top_score) < 0.01]
            
            if len(tier) > 1:
                # Re-rank tier by NCD to prompt (lower NCD = better match in tie)
                tier.sort(key=lambda x: self._ncd(prompt, x["candidate"]))
                
                # Merge back
                final_list = tier + [c for c in scored_candidates if c not in tier]
                # Re-calculate ranks to ensure order is preserved
                # Note: Since tier is sorted by NCD (lower is better) and others by score,
                # we just need to make sure the tier replaces the top N items.
                # Actually, simple replacement works if we assume tier items were the top ones.
                # But to be safe and deterministic:
                scored_candidates = final_list

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and numeric alignment."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        # Structural max is ~1.0, min is 0.0
        raw_score = res[0]["score"]
        
        # Boost if structural features match perfectly
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        bonus = 0.0
        if p_feat['has_negation'] == a_feat['has_negation']:
            bonus += 0.1
        if p_feat['has_conditional'] == a_feat['has_conditional']:
            bonus += 0.1
            
        conf = min(1.0, max(0.0, raw_score + bonus))
        return conf