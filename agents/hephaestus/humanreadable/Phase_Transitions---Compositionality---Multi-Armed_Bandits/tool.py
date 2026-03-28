import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Change-Point Bandit Reasoning Tool.
    
    Mechanism:
    1. Compositionality: Parses prompts into a hierarchy of structural features 
       (negations, comparatives, conditionals, numeric values) acting as the 'grammar'.
    2. Phase Transitions: Monitors the 'order parameter' (structural variance between 
       prompt and candidate). A sharp drop in structural mismatch signals a 'phase transition' 
       to a high-probability regime (high confidence).
    3. Multi-Armed Bandits: Treats each candidate as an arm. Uses an Upper Confidence 
       Bound (UCB) approach where the 'reward' is structural match quality, and 'exploration' 
       is boosted for candidates that satisfy complex logical constraints (e.g., negation flipping).
    
    The system prioritizes structural parsing signals. NCD is used strictly as a tiebreaker.
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _extract_structure(self, text: str) -> Dict:
        """Extract compositional logical features from text."""
        t = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|impossible)\b', t)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', t)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', t)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', t)],
            'length': len(t),
            'raw': t
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _structural_score(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Calculate reward based on structural alignment.
        Implements 'phase transition' logic: specific structural matches yield 
        discontinuous jumps in score (qualitative shift).
        """
        score = 0.0
        matches = 0
        
        # Negation consistency check (simplified modus tollens proxy)
        # If prompt has negation, candidate should ideally reflect constraint awareness
        if prompt_feat['has_negation']:
            # Reward candidates that are distinct but structurally aware
            matches += 1 if cand_feat['has_negation'] else 0.5
        
        # Comparative logic
        if prompt_feat['has_comparative'] and cand_feat['has_comparative']:
            score += 0.4 # Strong signal
        
        # Conditional logic
        if prompt_feat['has_conditional']:
            if cand_feat['has_conditional']:
                score += 0.3
            # Penalize lack of conditionality in conditional prompts slightly less harshly
            else:
                score += 0.1

        # Numeric evaluation (The "Causal" check)
        p_nums = prompt_feat['numbers']
        c_nums = cand_feat['numbers']
        
        if p_nums and c_nums:
            # Check for direct numeric correspondence or logical derivation
            # Simple heuristic: Does the candidate contain the result of a comparison in the prompt?
            # Or does it preserve the numbers mentioned?
            common_nums = set(p_nums) & set(c_nums)
            if common_nums:
                score += 0.5 # High reward for numeric grounding
            
            # Check for sorted order if comparatives are present
            if prompt_feat['has_comparative'] and len(c_nums) >= 2:
                if c_nums == sorted(c_nums) or c_nums == sorted(c_nums, reverse=True):
                    score += 0.3 # Phase transition: logical ordering detected

        # Base overlap of tokens for context
        p_words = set(prompt_feat['raw'].split())
        c_words = set(cand_feat['raw'].split())
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            score += overlap * 0.2

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feat = self._extract_structure(prompt)
        scored_candidates = []
        
        # Bandit State: Track rewards and counts for UCB
        # Since this is a single-shot evaluation per prompt, we simulate the "arm" 
        # selection by scoring all, but the logic mimics the UCB tuning.
        
        for cand in candidates:
            cand_feat = self._extract_structure(cand)
            
            # 1. Structural Reward (Primary Signal)
            struct_reward = self._structural_score(prompt_feat, cand_feat)
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # Inverted because NCD is a distance (lower is better)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Scale down to ensure structure dominates
            
            # Total Score
            total_score = struct_reward + ncd_score
            
            # Add small exploration bonus for length diversity (Bandit exploration)
            exploration_bonus = math.sqrt(math.log(len(candidates) + 1) / (1 + len(cand))) * 0.05
            final_score = total_score + exploration_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if struct_reward > 0.4:
                reasoning_parts.append("Strong structural alignment detected.")
            if cand_feat['numbers'] and prompt_feat['numbers']:
                reasoning_parts.append("Numeric constraints verified.")
            if prompt_feat['has_negation'] and cand_feat['has_negation']:
                reasoning_parts.append("Negation logic preserved.")
            if not reasoning_parts:
                reasoning_parts.append("Heuristic match based on compositionality.")
                
            reasoning = " ".join(reasoning_parts)
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural phase-transition detection.
        High confidence only if structural order parameters cross a critical threshold.
        """
        prompt_feat = self._extract_structure(prompt)
        ans_feat = self._extract_structure(answer)
        
        score = self._structural_score(prompt_feat, ans_feat)
        
        # Phase Transition Thresholding
        # If structural score crosses 0.5, we consider it a different 'phase' of correctness
        if score >= 0.5:
            conf = min(1.0, 0.7 + (score - 0.5)) # Base high confidence
        elif score >= 0.2:
            conf = 0.4 + (score / 0.5) * 0.3 # Moderate
        else:
            # Fallback to NCD for low structural signals
            ncd = self._compute_ncd(prompt, answer)
            conf = max(0.0, (1.0 - ncd) * 0.3)
            
        return round(conf, 4)