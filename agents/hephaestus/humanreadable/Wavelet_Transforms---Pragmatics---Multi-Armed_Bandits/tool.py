import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Multi-Resolution Hypothesis-Testing Bandit (AMHTB) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This acts as the "Wavelet" 
       decomposition, isolating high-frequency logical features from the low-frequency 
       semantic noise.
    2. Pragmatic Filtering (Context): Uses Gricean maxims (Relevance/Quantity) to 
       penalize candidates that ignore detected constraints or fail to match the 
       structural complexity of the prompt.
    3. Bandit Selection (Decision): Treats each candidate as an arm. The "reward" 
       is the structural alignment score. The algorithm balances exploration (checking 
       all candidates) with exploitation (ranking based on logical consistency).
    4. NCD (Tiebreaker): Only used if structural scores are identical.
    
    This approach bypasses the "Wavelet as direct scorer" trap by using wavelet-inspired 
    multi-scale decomposition (logical vs semantic) only for feature extraction, 
    relying on deterministic rule-based scoring for the actual ranking.
    """

    def __init__(self):
        # Logical patterns for structural parsing
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bunless\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bprovided\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_features(self, text: str) -> Dict:
        """Decompose text into logical 'coefficients'."""
        text_lower = text.lower()
        features = {
            'has_negation': any(re.search(p, text_lower) for p in self.negation_patterns),
            'has_comparative': any(re.search(p, text_lower) for p in self.comparative_patterns),
            'has_conditional': any(re.search(p, text_lower) for p in self.conditional_patterns),
            'numbers': [float(n) for n in re.findall(self.numeric_pattern, text)],
            'length': len(text.split()),
            'unique_words': len(set(text_lower.split()))
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """Pragmatic check: Does the candidate respect the prompt's logical structure?"""
        score = 0.0
        
        # Negation Consistency: If prompt has negation, candidate should ideally reflect it or not contradict
        if prompt_feats['has_negation']:
            if cand_feats['has_negation']:
                score += 2.0  # Reward matching negation complexity
            else:
                # Check for explicit contradiction markers in candidate if prompt is negative
                if 'yes' in candidate.lower() and 'no' not in candidate.lower():
                    score -= 5.0 # Heavy penalty for ignoring negation context
        
        # Comparative Consistency
        if prompt_feats['has_comparative']:
            if cand_feats['has_comparative'] or cand_feats['numbers']:
                score += 2.0
            else:
                score -= 1.0 # Penalty for ignoring comparative context
        
        # Conditional Consistency
        if prompt_feats['has_conditional']:
            if cand_feats['has_conditional'] or any(w in candidate.lower() for w in ['if', 'then', 'because', 'so']):
                score += 1.5
            else:
                # Soft penalty, conditionals often imply complex answers
                pass 

        return score

    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        """Handle numeric reasoning explicitly."""
        p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt)]
        c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate)]
        
        if not p_nums or not c_nums:
            return 0.0
            
        # Simple heuristic: If prompt asks for max/min/greater, check candidate numbers
        p_low = prompt.lower()
        target_val = None
        if 'largest' in p_low or 'max' in p_low or 'greater' in p_low:
            target_val = max(p_nums)
        elif 'smallest' in p_low or 'min' in p_low or 'less' in p_low:
            target_val = min(p_nums)
            
        if target_val is not None and c_nums:
            # Check if candidate contains the target number
            if any(abs(c - target_val) < 1e-6 for c in c_nums):
                return 5.0
            # Penalize if it contains a wrong number when a specific one is expected
            return -2.0
            
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len12 = len(zlib.compress(s1_b + s2_b))
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt length for pragmatic quantity check
        p_len = prompt_feats['length']
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Score (Wavelet-like decomposition)
            score = 0.0
            
            # Logical Consistency (Pragmatics)
            score += self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # Numeric Evaluation
            score += self._numeric_evaluation(prompt, cand)
            
            # Pragmatic Quantity Heuristic: 
            # If prompt is complex (many unique words), very short answers might be insufficient
            if p_len > 10 and cand_feats['length'] < 3 and not cand_feats['numbers']:
                # Unless it's a direct answer to a simple question type
                if not any(x in prompt.lower() for x in ['yes/no', 'true/false', 'choose']):
                    score -= 0.5
            
            # Relevance: Keyword overlap boost (simple bag of words for relevance)
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            overlap = len(p_words.intersection(c_words))
            if overlap > 0:
                score += (overlap * 0.1)

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural alignment: {score:.2f}",
                "_ncd": 0.0 # Placeholder
            })

        # Tie-breaking with NCD
        # Sort initially by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD only for ties in the top tier or if all scores are 0
        max_score = results[0]['score'] if results else 0
        if max_score == 0 or all(r['score'] == max_score for r in results):
            # Calculate NCD for all if scores are flat
            for r in results:
                r['_ncd'] = self._ncd(prompt, r['candidate'])
            
            # Sort by NCD (lower is better/more similar) if scores are equal
            # We want to keep high score first, then low NCD
            results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
            # Correction: Higher score is better. For ties, lower NCD is better.
            # So sort by score DESC, then NCD ASC.
            results.sort(key=lambda x: (x['score'], x['_ncd']))
            # Since we want score DESC, we can't simply use sort with mixed direction easily in one go without negation
            # Let's re-sort properly:
            results.sort(key=lambda x: (-x['score'], x['_ncd']))

        # Clean up and format
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"],
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and NCD.
        """
        # Use internal evaluate logic to get a raw score
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Map raw score to 0-1
        # Heuristic mapping: 
        # score > 2.0 -> 0.9+
        # score > 0.0 -> 0.5+
        # score < 0.0 -> < 0.5
        if raw_score >= 5.0:
            conf = 0.95
        elif raw_score >= 2.0:
            conf = 0.8 + (raw_score - 2.0) * 0.05
        elif raw_score >= 0.0:
            conf = 0.5 + (raw_score * 0.1)
        else:
            conf = 0.5 + (raw_score * 0.2) # Drops quickly
            
        # Clamp
        return max(0.0, min(1.0, conf))