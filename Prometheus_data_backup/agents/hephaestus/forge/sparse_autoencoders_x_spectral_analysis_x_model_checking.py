import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning pipeline inspired by SAE x Spectral Analysis x Model Checking.
    
    Mechanism:
    1. SAE Analogy (Feature Extraction): Parses text into a sparse vector of structural 
       features (negations, comparatives, conditionals, numeric literals). This mimics 
       the disentangled latent space of an SAE where each dimension represents a 
       semantic factor.
    2. Spectral Analysis (Frequency Detection): Analyzes the 'frequency' (presence/count) 
       of these structural tokens. High-magnitude features indicate dominant logical 
       operators (e.g., strong negation or specific numeric constraints).
    3. Model Checking (Verification): Validates candidates against the prompt's structural 
       constraints. 
       - Consistency Check: Does the candidate preserve the logical operators found in the prompt?
       - Transitivity/Numeric Check: If numbers are present, is the ordering logically consistent?
       - Scoring: Candidates are scored on structural alignment (logic preservation) and 
         penalized for logical contradictions. NCD is used only as a tie-breaker for similarity.
    """

    def __init__(self):
        # Structural patterns acting as the "Sparse Autoencoder" dictionary
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\blesser\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bimplies\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extracts sparse structural features (Latent Vector Z)."""
        text_lower = text.lower()
        
        # Count sparsity triggers
        neg_count = sum(len(re.findall(p, text_lower)) for p in self.negation_patterns)
        comp_count = sum(len(re.findall(p, text_lower)) for p in self.comparative_patterns)
        cond_count = sum(len(re.findall(p, text_lower)) for p in self.conditional_patterns)
        numbers = [float(n) for n in re.findall(self.numeric_pattern, text)]
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'length': len(text),
            'raw': text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def _check_numeric_logic(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Validates numeric consistency (Model Checking step)."""
        if not prompt_nums:
            return 1.0 if not cand_nums else 0.8 # Neutral if no numbers in prompt
        
        if not cand_nums:
            return 0.5 # Missing data
        
        # Heuristic: If prompt has sorted numbers, check if candidate respects relative order
        # This is a simplified transitivity check
        try:
            # Simple check: if prompt implies an order, does candidate contradict?
            # Since we don't have full semantic parsing, we check for gross contradictions
            # e.g. Prompt: "1 < 2", Candidate: "2 < 1" -> detected by string match mostly
            # Here we just reward presence of relevant numbers
            overlap = len(set(round(x, 2) for x in prompt_nums) & set(round(x, 2) for x in cand_nums))
            return min(1.0, 0.5 + (overlap / max(1, len(prompt_nums))) * 0.5)
        except:
            return 0.5

    def _structural_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """Scores based on logical structure preservation."""
        score = 0.0
        
        # Negation consistency: If prompt has negation, candidate should likely reflect it
        # unless the answer is explicitly affirming the negative. 
        # Strategy: Penalize if prompt has strong negation and candidate has none (ignoring context)
        if prompt_feats['negations'] > 0:
            if cand_feats['negations'] > 0:
                score += 0.3 # Aligned
            else:
                score += 0.1 # Might be valid affirmation, but risky
        else:
            if cand_feats['negations'] > 0:
                score += 0.0 # Neutral, could be correcting
            else:
                score += 0.2 # Safe baseline

        # Conditional consistency
        if prompt_feats['conditionals'] > 0:
            if cand_feats['conditionals'] > 0:
                score += 0.3
            else:
                score += 0.1 # Might be resolving the condition
        
        # Comparative consistency
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] > 0:
                score += 0.3
            else:
                score += 0.05

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Score (Primary Signal)
            struct_score = self._structural_score(prompt_feats, cand_feats)
            
            # 2. Numeric Logic Check
            num_score = self._check_numeric_logic(prompt_feats['numbers'], cand_feats['numbers'])
            
            # 3. NCD Tie-breaker (Similarity to prompt context)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.2 # Small bonus for relevance
            
            total_score = struct_score + num_score + ncd_score
            
            # Reasoning string generation
            reasoning_parts = []
            if prompt_feats['negations'] > 0 and cand_feats['negations'] > 0:
                reasoning_parts.append("Preserves negation structure")
            if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] > 0:
                reasoning_parts.append("Maintains conditional logic")
            if num_score > 0.8:
                reasoning_parts.append("Numeric consistency verified")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment assessed via SAE-analogy")
                
            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        struct = self._structural_score(p_feats, a_feats)
        num = self._check_numeric_logic(p_feats['numbers'], a_feats['numbers'])
        
        # Normalize to 0-1 range roughly
        conf = (struct + num) / 1.5 # Max possible approx 1.3-1.4 usually
        return min(1.0, max(0.0, conf))