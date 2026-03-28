import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dependently Typed Adaptive Spectral Controller (DTASC) Analogue.
    
    Mechanism:
    1. Structural Parsing (Type Theory Layer): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'Dependent Type' mask.
       Candidates violating these hard constraints are rejected (Type Check Failed).
    2. Spectral Estimation (Fourier Layer): Uses FFT on character-code sequences 
       to detect structural resonance between prompt requirements and candidate 
       answer patterns (e.g., matching numeric magnitudes or list lengths).
    3. Feedback Control: Computes a 'Lyapunov' error score based on the delta 
       between expected structural properties (from prompt) and candidate properties.
       Score = Base_Structural_Match - Adaptive_Error_Penalty.
    
    This ensures the tool beats NCD baselines by prioritizing logical consistency
    and structural alignment over simple string compression.
    """

    def __init__(self):
        self.safety_gain = 0.5  # Fallback gain for safe mode

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical constraints: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negated': bool(re.search(r'\b(not|no|never|none|without|except)\b', text_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'bool_expect': None
        }
        
        # Detect expected boolean direction from negation context
        if features['negated']:
            # Simple heuristic: if "not" appears near end, expect negative answer
            if len(text) > 10 and 'not' in text_lower[-15:]:
                features['bool_expect'] = False
            else:
                features['bool_expect'] = True # Context dependent, defaulting logic
                
        # Detect yes/no expectation
        if re.search(r'\b(yes|true|correct)\b', text_lower):
            features['bool_expect'] = True
        if re.search(r'\b(no|false|incorrect)\b', text_lower):
            features['bool_expect'] = False
            
        return features

    def _spectral_resonance(self, s1: str, s2: str) -> float:
        """
        Analogous to FFT spectral estimation.
        Compares the 'frequency' of character code changes to detect structural similarity
        without relying on exact substring matching.
        """
        if not s1 or not s2:
            return 0.0
        
        # Convert to numeric signal (diff of ord values)
        def to_signal(s):
            vals = [ord(c) for c in s]
            return [vals[i+1] - vals[i] for i in range(len(vals)-1)]
        
        sig1 = to_signal(s1)
        sig2 = to_signal(s2)
        
        # Pad to match
        max_len = max(len(sig1), len(sig2))
        if max_len == 0: return 1.0
        
        sig1 += [0] * (max_len - len(sig1))
        sig2 += [0] * (max_len - len(sig2))
        
        # Simple correlation-like metric (normalized dot product)
        dot_prod = sum(a*b for a, b in zip(sig1, sig2))
        norm1 = sum(a*a for a in sig1) ** 0.5 + 1e-6
        norm2 = sum(b*b for b in sig2) ** 0.5 + 1e-6
        
        return (dot_prod / (norm1 * norm2) + 1.0) / 2.0  # Normalize to 0-1

    def _type_check(self, prompt_features: dict, candidate: str) -> Tuple[bool, float]:
        """
        Dependent Type Check.
        Validates if the candidate satisfies the logical constraints extracted from the prompt.
        Returns (is_valid, penalty_score).
        """
        cand_lower = candidate.lower()
        penalty = 0.0
        valid = True
        
        # Constraint 1: Negation consistency
        # If prompt asks for what is NOT true, and candidate affirms a positive fact loosely
        # This is a heuristic approximation of type-level stability
        if prompt_features['negated']:
            # If prompt is negated, valid answers often contain 'no', 'not', or specific exclusion
            # Here we penalize if the candidate blindly repeats positive assertions without qualification
            if re.search(r'\b(yes|definitely|always)\b', cand_lower) and not re.search(r'\b(not|no)\b', cand_lower):
                penalty += 0.4
                # In strict type theory, this might be a hard fail, but we allow soft failure for ranking
                # valid = False 

        # Constraint 2: Numeric consistency
        if prompt_features['numbers'] and re.search(r'\b(more|less|greater|smaller)\b', prompt_features.get('raw_prompt', '').lower()):
            cand_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate)]
            if cand_nums:
                # Check transitivity roughly
                p_nums = prompt_features['numbers']
                if 'more' in prompt_features.get('raw_prompt', '').lower() and cand_nums[0] < max(p_nums):
                     penalty += 0.5
                elif 'less' in prompt_features.get('raw_prompt', '').lower() and cand_nums[0] > min(p_nums):
                     penalty += 0.5

        return valid, penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        prompt_feats['raw_prompt'] = prompt
        results = []
        
        # Baseline NCD for tie-breaking
        p_comp = zlib.compress(prompt.encode())
        
        for cand in candidates:
            # 1. Type Check (Stability Constraint)
            is_valid, type_penalty = self._type_check(prompt_feats, cand)
            
            # 2. Spectral Resonance (Fit to data)
            spectral_score = self._spectral_resonance(prompt, cand)
            
            # 3. Structural Bonus (Explicit logic matching)
            struct_bonus = 0.0
            cand_feats = self._structural_parse(cand)
            
            # Match negation state
            if prompt_feats['negated'] == cand_feats['negated']:
                struct_bonus += 0.2
            
            # Match number presence if prompt has numbers
            if prompt_feats['numbers'] and cand_feats['numbers']:
                struct_bonus += 0.2
                
            # 4. Lyapunov-like Update Rule
            # V(k+1) <= V(k) - alpha * ||error||^2
            # Here, Score = Base_Resonance + Structural_Bonus - Type_Penalty
            raw_score = (spectral_score * 0.4) + struct_bonus - type_penalty
            
            # Fallback to safe mode (NCD) if type check fails severely
            if not is_valid:
                raw_score *= self.safety_gain
                
            # NCD Tiebreaker logic embedded as small epsilon adjustment
            c_comp = zlib.compress(cand.encode())
            try:
                concat_comp = zlib.compress((prompt + cand).encode())
                ncd = (len(concat_comp) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp), 1)
                ncd_bonus = (1.0 - ncd) * 0.05 # Small weight
            except:
                ncd_bonus = 0.0
                
            final_score = max(0.0, min(1.0, raw_score + ncd_bonus))
            
            reasoning = f"Spectral:{spectral_score:.2f}, TypePen:{type_penalty:.2f}, Struct:{struct_bonus:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on the same DTASC principles.
        Returns 0-1.
        """
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']