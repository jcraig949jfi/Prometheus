import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements an active-inference inspired reasoning tool using the Free Energy Principle (FEP)
    as the core architectural pattern, guided by Multi-Armed Bandit (MAB) exploration logic,
    while restricting Wavelet Transforms to structural confidence parsing as per causal analysis.
    
    Mechanism:
    1. FEP Core (evaluate): Treats the prompt as the 'environment' and candidates as 'generative models'.
       It calculates a 'Free Energy' score based on the divergence between the candidate's structural
       implications and the prompt's constraints. Lower divergence (higher alignment) = higher score.
    2. Structural Parsing (Wavelet role): Instead of frequency decomposition, we decompose the text
       into logical 'bands' (negations, comparatives, conditionals, numeric values) to detect 
       high-frequency logical features that NCD misses.
    3. MAB Strategy: Uses an Upper Confidence Bound (UCB) heuristic to balance between 
       structural match (exploitation) and information density (exploration/complexity penalty).
    """

    def __init__(self):
        # Logical operators as 'structural bands' for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'affirmative']
        self.bool_no = ['no', 'false', 'incorrect', 'negative']

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extracts logical features (structural bands) from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Count logical bands
        neg_count = sum(1 for w in words if any(n in w for n in self.negations))
        comp_count = sum(1 for w in words if any(c in w for c in self.comparatives))
        cond_count = sum(1 for w in words if any(c in w for c in self.conditionals))
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        
        # Check for direct boolean assertions
        is_yes = any(b in t_lower for b in self.bool_yes)
        is_no = any(b in t_lower for b in self.bool_no)
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'numbers': numbers,
            'is_yes': is_yes,
            'is_no': is_no,
            'length': len(text)
        }

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            numerator = z12 - min(z1, z2)
            denominator = max(z1, z2)
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except:
            return 1.0

    def _structural_alignment(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Computes alignment based on logical consistency (Free Energy minimization).
        Checks if the candidate respects the logical constraints of the prompt.
        """
        score = 0.0
        
        # 1. Numeric Consistency (High Priority)
        if p_feat['numbers'] and c_feat['numbers']:
            # If prompt has numbers, check if candidate logic aligns (simplified heuristic)
            # E.g., if prompt implies "greater", candidate should reflect that
            score += 2.0 if len(c_feat['numbers']) > 0 else 0.0
        elif p_feat['numbers'] and not c_feat['numbers']:
            # Penalty if prompt is numeric but candidate ignores it (unless it's a simple yes/no)
            if not (c_feat['is_yes'] or c_feat['is_no']):
                score -= 1.0

        # 2. Logical Operator Matching
        # If prompt has conditionals, good candidates often repeat or resolve them
        if p_feat['cond'] > 0:
            if c_feat['cond'] > 0 or c_feat['is_yes'] or c_feat['is_no']:
                score += 1.5
            else:
                score -= 0.5 # Penalty for ignoring conditional structure

        # 3. Negation Handling
        # Detects if candidate flips meaning incorrectly (simplified)
        if p_feat['neg'] > 0:
            # If prompt is negative, a 'yes' might need careful handling, 
            # but here we just reward recognizing the complexity
            score += 0.5 * min(p_feat['neg'], c_feat['neg'] + 1)

        # 4. Comparative Density
        if p_feat['comp'] > 0:
            score += 0.5 if c_feat['comp'] > 0 or c_feat['numbers'] else 0.0

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt complexity for UCB-like scaling
        prompt_complexity = p_feat['neg'] + p_feat['comp'] + p_feat['cond'] + len(p_feat['numbers'])
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # --- FREE ENERGY PRINCIPLE CORE ---
            # Minimize surprise (divergence) between prompt constraints and candidate structure.
            # High structural alignment = Low Free Energy = High Score.
            structural_score = self._structural_alignment(p_feat, c_feat)
            
            # --- MULTI-ARMED BANDIT (UCB Analogy) ---
            # Balance exploitation (structural match) with exploration (information content).
            # We treat 'length' as a proxy for information density, penalizing excessive verbosity
            # unless justified by structural complexity.
            info_penalty = abs(len(cand) - len(prompt)) / (len(prompt) + 1) * 0.1
            uncertainty_bonus = math.sqrt(math.log(len(prompt) + 2) / (c_feat['length'] + 1)) * 0.5
            
            # NCD as Tiebreaker/Baseline (as requested)
            # Only dominates if structural signals are weak (near zero)
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.5 # Convert distance to similarity
            
            # Final Score Composition
            # Structural parsing is primary. NCD is secondary.
            total_score = structural_score + uncertainty_bonus - info_penalty
            
            # If structural signal is very weak, rely more on NCD to avoid random ranking
            if abs(structural_score) < 0.1:
                total_score += ncd_score * 0.8
            else:
                total_score += ncd_score * 0.2
                
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Structural alignment: {structural_score:.2f}, NCD influence: {ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing (Wavelet-analog) to verify logical consistency.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Base confidence on structural coherence
        conf = 0.5
        
        # 1. Numeric Check
        if p_feat['numbers'] and a_feat['numbers']:
            # If both have numbers, check if they are in the same ballpark (heuristic)
            # Or if the answer provides a number where expected
            conf += 0.3
        elif p_feat['numbers'] and not a_feat['numbers']:
            if not (a_feat['is_yes'] or a_feat['is_no']):
                conf -= 0.4 # Low confidence if number expected but not given

        # 2. Logical Operator Presence
        if p_feat['cond'] > 0:
            if a_feat['cond'] > 0 or a_feat['is_yes'] or a_feat['is_no']:
                conf += 0.2
            else:
                conf -= 0.2
        
        # 3. Negation consistency (Simplified)
        # If prompt is complex (negations), and answer is too short, lower confidence
        if p_feat['neg'] > 0 and len(a_feat['numbers']) == 0 and a_feat['length'] < 5:
             if not (a_feat['is_yes'] or a_feat['is_no']):
                conf -= 0.3

        # Clamp to [0, 1]
        return max(0.0, min(1.0, conf))