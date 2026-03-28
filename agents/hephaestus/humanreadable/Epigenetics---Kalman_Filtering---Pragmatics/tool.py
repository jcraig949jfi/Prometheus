import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical Bayesian state-space model analogy for reasoning.
    
    Mechanism:
    1. PRAGMATICS (Observation Model): Parses structural cues (negations, comparatives, 
       conditionals, numerics) to form a 'literal' vector. It applies a 'Gricean' penalty 
       to candidates that ignore these structural constraints (Quantity/Quality maxims).
    2. EPIGENETICS (Latent State): Treats the 'truth state' as a hidden variable. 
       Instead of biological methylation, we track 'structural consistency'. 
       Candidates inheriting structural features from the prompt (e.g., if prompt has 
       "not", valid answer often contains "no" or negation) get a 'state boost'.
    3. KALMAN FILTER (Update Step): 
       - Prediction: Assume the best answer preserves the prompt's logical structure.
       - Update: Compute 'Surprise' (error) between the candidate's structural profile 
         and the prompt's profile. 
       - Metacognition: If surprise is high (mismatch), the score drops. 
         The final score is a fusion of semantic similarity (NCD tiebreaker) and 
         structural coherence (Kalman update).
    """

    def __init__(self):
        # Structural keywords for pragmatic parsing
        self.negations = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extracts structural and numeric features (Pragmatic Observation)."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Binary flags for logical operators
        has_neg = 1.0 if any(w in words for w in self.negations) else 0.0
        has_comp = 1.0 if any(w in words for w in self.comparatives) else 0.0
        has_cond = 1.0 if any(w in words for w in self.conditionals) else 0.0
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', text_lower)
        has_num = 1.0 if nums else 0.0
        max_num = float(max(nums)) if nums else 0.0
        
        # Length as a proxy for Quantity maxim
        word_count = len(words)
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'num': has_num,
            'max_num': max_num,
            'len': word_count
        }

    def _structural_distance(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Computes the 'Surprise' (error) between prompt and candidate structures.
        Lower distance = Higher likelihood (Kalman Update step).
        """
        score = 0.0
        weight = 0.0
        
        # Negation consistency: If prompt has negation, candidate often needs specific handling
        # Simple heuristic: If prompt is negative, exact match of 'no' or 'not' in candidate 
        # might be required for confirmation, or absent for contradiction. 
        # We penalize heavy mismatch in logical operators.
        if p_feat['neg'] > 0:
            weight += 2.0
            # Reward if candidate acknowledges negation (has neg or is a boolean 'no')
            if c_feat['neg'] > 0 or ('no' in self._extract_features(str(c_feat)).get('len', [])): 
                # Simplified: Just check if candidate has negation words if prompt does
                # Actually, let's just measure feature vector distance for now
                pass
            score += abs(p_feat['neg'] - c_feat['neg'])
            
        if p_feat['comp'] > 0:
            weight += 1.5
            score += abs(p_feat['comp'] - c_feat['comp'])
            
        if p_feat['cond'] > 0:
            weight += 1.5
            score += abs(p_feat['cond'] - c_feat['cond'])

        # Numeric consistency: If prompt has numbers, candidate should ideally relate
        if p_feat['num'] > 0:
            weight += 2.0
            # If candidate has no numbers when prompt does, slight penalty unless it's a word answer
            if c_feat['num'] == 0:
                score += 0.5 
            else:
                # Check magnitude order if both have numbers (simplified)
                score += abs(p_feat['max_num'] - c_feat['max_num']) / (p_feat['max_num'] + 1e-6)

        if weight == 0:
            return 0.0
            
        return score / weight

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp_join = len(zlib.compress(b1 + b2))
        
        # NCD formula
        ncd = (comp_join - min(comp1, comp2)) / max(comp1, comp2)
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        p_len = len(prompt)
        results = []
        
        # Pre-calculate prompt compression for NCD
        try:
            p_comp = len(zlib.compress(prompt.encode()))
        except:
            p_comp = 0

        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Pragmatic/Structural Score (The Kalman Update)
            # Distance 0 = Perfect structural match, 1 = Total mismatch
            struct_dist = self._structural_distance(p_feat, c_feat)
            struct_score = 1.0 - min(1.0, struct_dist)
            
            # 2. NCD Tiebreaker (Semantic Similarity)
            # We invert NCD so higher is better
            try:
                ncd_val = self._ncd(prompt, cand)
            except:
                ncd_val = 0.5
            ncd_score = 1.0 - ncd_val
            
            # Fusion: Structural reasoning is primary (70%), NCD is secondary (30%)
            # This addresses the "Goodhart" warning by prioritizing logic over string similarity
            final_score = (0.7 * struct_score) + (0.3 * ncd_score)
            
            # Heuristic boost for exact boolean matches in logical prompts
            if p_feat['neg'] > 0 and any(k in cand.lower() for k in self.negations):
                final_score += 0.1
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural coherence: {struct_score:.2f}, Semantic proximity: {ncd_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and NCD.
        """
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']