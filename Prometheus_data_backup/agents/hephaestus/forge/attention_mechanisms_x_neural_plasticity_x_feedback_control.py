import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Attentive Controller (AAC) for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Attention Focus): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This acts as the "fast feedback" 
       loop, sharply weighting candidates that satisfy explicit structural constraints.
    2. Hebbian Plasticity (Consolidation): Simulates weight consolidation by reinforcing 
       candidates that share semantic n-grams with the prompt's key logical terms, 
       mimicking the "slow plasticity" of wiring in successful patterns.
    3. PID-like Error Modulation: Candidates violating hard constraints (e.g., "not" 
       appearing in answer when required) receive a massive penalty (integral error), 
       while partial matches get proportional scoring.
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when structural 
       scores are indistinguishable.
    """

    def __init__(self):
        # Logical keywords for structural attention
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['true', 'false', 'yes', 'no']
        
        # Plasticity decay factor (simulating slow consolidation)
        self.plasticity_rate = 0.1

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical constraints and numeric values (Fast Feedback Loop)."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        # Extract numbers
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text_lower)]
        
        # Extract boolean targets
        booleans = [b for b in self.booleans if b in words]

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'booleans': booleans,
            'length': len(words)
        }

    def _check_numeric_logic(self, prompt_struct: Dict, candidate: str) -> float:
        """Evaluate numeric consistency (Constraint Propagation)."""
        candidate_lower = candidate.lower()
        score = 0.0
        
        # If prompt has numbers, check if candidate respects order if implied
        if len(prompt_struct['numbers']) >= 2:
            nums = sorted(prompt_struct['numbers'])
            # Simple heuristic: if candidate mentions a number, does it fit the range?
            c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate_lower)]
            if c_nums:
                # Reward if candidate number exists within prompt's numeric context
                if any(min(nums) <= n <= max(nums) for n in c_nums):
                    score += 0.2
                else:
                    score -= 0.5 # Penalty for out-of-bounds numbers
        
        # Check boolean consistency if prompt asks a yes/no question structure
        if 'true' in prompt_struct['booleans'] or 'false' in prompt_struct['booleans']:
            if 'true' in candidate_lower or 'false' in candidate_lower:
                score += 0.1
                
        return score

    def _hebbian_update(self, prompt: str, candidate: str) -> float:
        """
        Simulate Hebbian plasticity: Strengthen connections between 
        prompt tokens and candidate tokens (Semantic Overlap).
        """
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        if not p_words or not c_words:
            return 0.0
            
        # Intersection over Union (Jaccard) as a proxy for Hebbian strengthening
        intersection = len(p_words & c_words)
        union = len(p_words | c_words)
        
        if union == 0:
            return 0.0
            
        return (intersection / union) * self.plasticity_rate

    def _pid_error_modulation(self, prompt_struct: Dict, candidate: str) -> float:
        """
        PID-like controller: 
        P (Proportional): Structural match.
        I (Integral): Accumulated constraint violation (hard penalties).
        D (Derivative): Change in logic (not directly applicable statically, 
                        so we use it to sharpen focus on negation flips).
        """
        score = 0.0
        c_lower = candidate.lower()
        c_words = re.findall(r'\b\w+\b', c_lower)
        
        # Proportional: Match structural expectations
        if prompt_struct['negation']:
            # If prompt has negation, correct answers often contain negation or antonyms
            has_neg = any(n in c_words for n in self.negations)
            score += 0.3 if has_neg else -0.3
            
        if prompt_struct['comparative']:
            has_comp = any(c in c_words for c in self.comparatives)
            score += 0.2 if has_comp else 0.0
            
        # Integral (Hard Constraints): Massive penalty for logical contradictions
        # Example: Prompt says "Which is NOT...", Candidate says "It is..." (without negation)
        if prompt_struct['negation'] and not any(n in c_words for n in self.negations):
            # Check if the candidate is a simple affirmation that ignores the negation
            if any(b in c_words for b in self.booleans) and not any(n in c_words for n in self.negations):
                score -= 1.0 # Strong integral error term
                
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            c12 = len(zlib.compress(b1 + b2))
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            numerator = c12 - min(c1, c2)
            denominator = max(c1, c2)
            return numerator / denominator if denominator > 0 else 1.0
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking if needed
        # Note: NCD is computationally expensive, so we rely on structural scores first.
        
        for cand in candidates:
            # 1. Fast Feedback (Structural/PID)
            pid_score = self._pid_error_modulation(prompt_struct, cand)
            numeric_score = self._check_numeric_logic(prompt_struct, cand)
            
            # 2. Slow Plasticity (Hebbian)
            hebbian_score = self._hebbian_update(prompt, cand)
            
            # Combine scores: Structural logic dominates, plasticity refines
            # Weighting: PID (0.5) + Numeric (0.3) + Hebbian (0.2)
            total_score = (0.5 * pid_score) + (0.3 * numeric_score) + (0.2 * hebbian_score)
            
            # Base confidence boost for length appropriateness (avoiding empty strings)
            if len(cand.strip()) == 0:
                total_score -= 10.0
                
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"PID:{pid_score:.2f}, Num:{numeric_score:.2f}, Heb:{hebbian_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD tie-breaking for top candidates if scores are very close
        if len(results) > 1:
            top_score = results[0]['score']
            # Check if top 2 are within 0.01 threshold
            if len(results) > 1 and abs(results[0]['score'] - results[1]['score']) < 0.01:
                # Re-rank based on NCD to prompt (lower NCD = more similar/relevant usually)
                # But strictly, we want the one that compresses best WITH the prompt context
                for i in range(len(results) - 1):
                    if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                        ncd1 = self._ncd_distance(prompt, results[i]['candidate'])
                        ncd2 = self._ncd_distance(prompt, results[i+1]['candidate'])
                        if ncd1 > ncd2: # Lower NCD is better
                            results[i], results[i+1] = results[i+1], results[i]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score to 0-1 range
        # Heuristic: Scores > 0.5 are high confidence, < -0.5 are low
        # Sigmoid-like mapping
        confidence = 1.0 / (1.0 + np.exp(-2 * raw_score))
        return float(np.clip(confidence, 0.0, 1.0))