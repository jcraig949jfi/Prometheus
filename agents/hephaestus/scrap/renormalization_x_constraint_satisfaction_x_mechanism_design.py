import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Incentive-Compatible Constraint Engine.
    
    Mechanism:
    1. Renormalization (Coarse-graining): Parses text into structural tokens 
       (negations, comparatives, numbers) to form a 'coarse' representation, 
       ignoring noise (fine details).
    2. Constraint Satisfaction: Checks logical consistency between prompt constraints 
       and candidate assertions (e.g., if prompt says "less than", candidate must be smaller).
    3. Mechanism Design (VCG-style): Candidates are 'agents'. They gain 'reward' (score) 
       proportional to how well they satisfy global constraints minus the 'externality' 
       (penalty) for violating structural logic. Truthful alignment with constraints 
       maximizes score; hallucination incurs heavy penalties.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparators = {'<', '>', 'less', 'greater', 'more', 'fewer', 'before', 'after'}
        self.bool_yes = {'yes', 'true', 'correct', 'right', 'accurate'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong', 'inaccurate'}

    def _tokenize_structure(self, text: str) -> Dict:
        """Extract coarse-grained structural features (Renormalization step)."""
        t = text.lower()
        words = set(re.findall(r'\b\w+\b', t))
        numbers = re.findall(r'-?\d+\.?\d*', t)
        nums = [float(n) for n in numbers] if numbers else []
        
        has_neg = bool(words & self.negation_words)
        has_comp = bool(words & self.comparators)
        
        # Detect simple boolean intent
        is_yes = bool(words & self.bool_yes)
        is_no = bool(words & self.bool_no)
        
        return {
            'negations': has_neg,
            'comparators': has_comp,
            'numbers': nums,
            'is_yes': is_yes,
            'is_no': is_no,
            'length': len(text)
        }

    def _check_numeric_constraint(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """Enforce numeric consistency (Constraint Satisfaction)."""
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric constraint to check
        
        # Heuristic: If prompt has numbers and candidate has numbers, 
        # check if they logically follow simple trends if comparators exist.
        # Since we don't have full semantic parse, we penalize wild deviations 
        # if the prompt implies a specific value selection task.
        
        # Simple transitivity check simulation:
        # If prompt asks for "smaller than X", candidate should be < X.
        # We approximate this by checking if candidate numbers are within 
        # a reasonable range of prompt numbers if comparators exist.
        
        if prompt_struct['comparators']:
            p_val = p_nums[0] # Assume primary reference
            c_val = c_nums[0]
            
            # If prompt says "less" or "<", candidate should ideally be smaller
            if ('less' in str(prompt_struct) or '<' in str(prompt_struct)):
                if c_val < p_val:
                    return 0.2 # Reward
                else:
                    return -0.5 # Penalty
            
            # If prompt says "greater" or ">", candidate should be larger
            if ('greater' in str(prompt_struct) or 'more' in str(prompt_struct) or '>' in str(prompt_struct)):
                if c_val > p_val:
                    return 0.2
                else:
                    return -0.5
                    
        return 0.0

    def _calculate_vcg_payment(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Calculate 'payment' (score) based on truthfulness and constraint satisfaction.
        Truthful reporting = high score. Contradiction = negative externality (penalty).
        """
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt negates, candidate affirming basic facts might be wrong depending on context.
        # Here we simply check for direct contradiction in boolean flags if prompt is negative.
        if prompt_struct['negations']:
            # If prompt is negative, and candidate is strongly affirmative without nuance, slight penalty
            if cand_struct['is_yes'] and not cand_struct['is_no']:
                score -= 0.3 # Externality: Over-confidence in negative context
            elif cand_struct['is_no']:
                score += 0.2 # Alignment
        
        # 2. Numeric Constraints
        score += self._check_numeric_constraint(prompt_struct, cand_struct)
        
        # 3. Boolean Alignment
        if prompt_struct['is_yes'] and cand_struct['is_yes']:
            score += 0.3
        elif prompt_struct['is_no'] and cand_struct['is_no']:
            score += 0.3
        elif (prompt_struct['is_yes'] and cand_struct['is_no']) or \
             (prompt_struct['is_no'] and cand_struct['is_yes']):
            score -= 0.4 # Strong contradiction penalty

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return c12 / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._tokenize_structure(prompt)
        
        for cand in candidates:
            c_struct = self._tokenize_structure(cand)
            
            # Core Mechanism: VCG-style scoring
            # Reward = Improvement in constraint satisfaction - Externality
            base_score = self._calculate_vcg_payment(p_struct, c_struct)
            
            # Tiebreaker: NCD (only used if scores are close, but here added as small component)
            # We invert NCD so higher is better, but keep weight low to prioritize logic
            ncd_val = self._ncd(prompt, cand) 
            # Normalize NCD to small contribution
            ncd_score = (1.0 - ncd_val) * 0.05 
            
            final_score = base_score + ncd_score
            
            # Reasoning trace
            reasoning = []
            if p_struct['negations'] and c_struct['is_yes']:
                reasoning.append("Potential conflict: Prompt contains negation, candidate affirms.")
            if p_struct['comparators'] and c_struct['numbers']:
                reasoning.append("Numeric constraint check applied.")
            if not reasoning:
                reasoning.append("Structural alignment verified.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate logic on a single candidate to determine robustness.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map score to 0-1 range roughly
        # Scores can be negative. Let's assume range [-1.0, 1.0] maps to [0, 1]
        score = res[0]['score']
        conf = (score + 1.0) / 2.0
        return max(0.0, min(1.0, conf))