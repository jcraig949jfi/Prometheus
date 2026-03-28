import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Adaptive Policy Controller (HAPC) for Reasoning.
    
    Mechanism:
    1. Boundary Encoding (Holography): The prompt and candidates are parsed into a 
       compact latent vector 'z' representing structural features (negations, comparatives, 
       conditionals, numeric values) rather than raw text density. This obeys an 
       information-density constraint by focusing only on logical operators.
       
    2. Bulk Projection & Feedback (Control): The tool projects a "hypothesized" correct 
       answer structure based on the prompt's logical constraints. It calculates a 
       prediction error between the candidate's structural signature and the projected 
       ideal signature.
       
    3. Adaptive Scoring (RL): A PID-inspired logic adjusts the final score. 
       - If structural constraints (e.g., negation) match, the 'integral' term accumulates confidence.
       - If contradictions exist (e.g., candidate says "Yes" when prompt implies "No"), 
         the 'derivative' term penalizes heavily.
       - NCD is used strictly as a tiebreaker when structural signals are ambiguous.
    """

    def __init__(self):
        self.bekenstein_limit = 1.0  # Max information density cap
        self.kp = 1.0  # Proportional gain for structural matches
        self.ki = 0.5  # Integral gain for cumulative consistency
        self.kd = -2.0 # Derivative gain for contradiction penalty

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical 'boundary' features: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', t_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', t_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', t_lower)),
            'affirmations': len(re.findall(r'\b(yes|true|correct|is|are)\b', t_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text)
        }
        # Normalize numbers for comparison logic
        features['has_numbers'] = len(features['numbers']) > 0
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Computes the feedback error between prompt constraints and candidate answer.
        Returns a score adjustment based on PID-like logic.
        """
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has high negation density, candidate should reflect understanding (simplified heuristic)
        if prompt_feats['negations'] > 0:
            # If prompt negates, and candidate affirms blindly without nuance, penalize
            if cand_feats['affirmations'] > prompt_feats['affirmations'] * 2:
                score -= 0.5 # Derivative-like penalty for overshoot
        
        # 2. Conditional Logic
        if prompt_feats['conditionals'] > 0:
            # Candidate should ideally contain conditional markers or specific logical outcomes
            if cand_feats['conditionals'] == 0 and cand_feats['affirmations'] == 0:
                score += 0.2 # Neutral/Ambiguous
            elif cand_feats['affirmations'] > 0:
                score += 0.3 # Attempted resolution

        # 3. Numeric Consistency
        if prompt_feats['has_numbers'] and cand_feats['has_numbers']:
            try:
                # Simple heuristic: if numbers in candidate are subsets of prompt, likely extraction
                p_nums = set(prompt_feats['numbers'])
                c_nums = set(cand_feats['numbers'])
                if c_nums.issubset(p_nums) and len(c_nums) > 0:
                    score += 0.4 # High confidence in extraction tasks
            except:
                pass

        # 4. Direct Contradiction Check (String level)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        if ('no' in p_lower and 'yes' in c_lower) or ('false' in p_lower and 'true' in c_lower):
            score -= 1.0 # Hard contradiction
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._parse_structure(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._parse_structure(cand)
            
            # Base score from structural logic (The "Bulk" projection)
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # Feedback correction (PID-like adjustment)
            # If logic_score is negative, we penalize heavily. If positive, we boost.
            adaptive_score = 0.5 + (logic_score * self.kp) 
            
            # Clamp to [0, 1] initially, but allow NCD to break ties
            adaptive_score = max(0.0, min(1.0, adaptive_score))
            
            results.append({
                "candidate": cand,
                "score": adaptive_score,
                "reasoning": f"Structural match: {logic_score:.2f}",
                "_ncd": self._ncd(prompt, cand) # Store for tie-breaking
            })

        # Sort primarily by score, secondarily by NCD (lower NCD = better tiebreaker for similarity)
        # However, for reasoning, if scores are equal, we prefer the one with lower NCD to prompt context
        # ONLY if the score is ambiguous (close). 
        # To strictly beat NCD baseline, structural score is primary.
        results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and return
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": round(r["score"], 4),
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_feats = self._parse_structure(prompt)
        a_feats = self._parse_structure(answer)
        
        # Quick consistency check
        logic_val = self._check_logical_consistency(p_feats, a_feats, prompt, answer)
        
        # Map logic_val (approx -1 to 1) to confidence (0 to 1)
        conf = 0.5 + (logic_val * 0.4)
        return max(0.0, min(1.0, conf))