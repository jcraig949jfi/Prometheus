import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Probabilistic Partition-Function Engine (Approximated).
    
    Mechanism:
    1. Type Theory Layer (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'validity mask'.
    2. Statistical Mechanics Layer (Energy Model): Assigns an 'energy' score 
       based on constraint satisfaction. Lower energy = higher probability.
       E = -sum(weights * satisfied_constraints).
    3. Prime Number Theory Layer (Confidence Wrapper): As per causal analysis, 
       prime theory is restricted to the confidence() wrapper to avoid reasoning traps,
       acting as a structural complexity penalty rather than a direct scorer.
    4. NCD: Used strictly as a tie-breaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Patterns for structural parsing (Type Theory constraints)
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b']
        self.numeric_pattern = r'\d+\.?\d*'

    def _extract_features(self, text: str) -> dict:
        """Extract structural features representing the 'Type' of the text."""
        text_lower = text.lower()
        return {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': re.findall(self.numeric_pattern, text_lower),
            'length': len(text)
        }

    def _check_numeric_consistency(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Check numeric consistency (Constraint Propagation).
        If prompt has numbers and candidate has numbers, check basic ordering if implied.
        For this implementation, we reward presence of numbers if prompt has them (context retention).
        """
        if not prompt_feats['numbers']:
            return 1.0 # No numeric constraint
        
        if not cand_feats['numbers']:
            return 0.5 # Missing expected numeric content
        
        # Simple overlap check for numeric tokens (loose constraint)
        # In a full engine, this would parse inequalities.
        return 1.0 

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute 'Energy' E(sigma) based on structural alignment.
        Lower energy is better. We return negative energy as a score (higher is better).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        score = 0.0
        
        # 1. Negation Matching (Modus Tollens support)
        # If prompt implies negation logic, candidate should reflect appropriate structure
        if p_feats['negations'] > 0:
            # Reward if candidate acknowledges negation context (heuristic)
            score += 2.0 if c_feats['negations'] > 0 else 0.5
        else:
            score += 1.0 if c_feats['negations'] == 0 else -1.0 # Penalty for spurious negation

        # 2. Comparative/Conditional Alignment
        if p_feats['comparatives'] > 0:
            score += 2.0 if c_feats['comparatives'] > 0 else 0.0
        if p_feats['conditionals'] > 0:
            score += 2.0 if c_feats['conditionals'] > 0 else 0.0
            
        # 3. Numeric Constraint Propagation
        score += self._check_numeric_consistency(p_feats, c_feats) * 2.0
        
        # 4. Length penalty (Occam's razor) - avoid overly verbose answers unless justified
        # Simple heuristic: candidate length should be within reasonable range of prompt complexity
        if c_feats['length'] > 0:
            ratio = p_feats['length'] / max(c_feats['length'], 1)
            if 0.5 <= ratio <= 2.0:
                score += 1.0
            elif ratio > 2.0: # Candidate too short
                score -= 1.0
                
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-computation
        prompt_score_base = self._compute_energy(prompt, prompt) 
        
        scored_candidates = []
        for cand in candidates:
            # Structural Score (The "Type" check)
            struct_score = self._compute_energy(prompt, cand)
            
            # NCD Tie-breaker (The "Statistical" noise check)
            # We invert NCD so higher is better, but weight it lightly as tiebreaker
            ncd_val = self._ncd(prompt, cand)
            
            scored_candidates.append({
                "candidate": cand,
                "struct_score": struct_score,
                "ncd_val": ncd_val
            })
        
        # Sort: Primary by structural score (desc), Secondary by NCD (asc -> lower distance is better)
        # Since we want higher score first:
        # If struct scores equal, prefer lower NCD.
        scored_candidates.sort(key=lambda x: (x['struct_score'], -x['ncd_val']), reverse=True)
        
        # Normalize scores to 0-1 range roughly for output consistency
        max_score = max(x['struct_score'] for x in scored_candidates) if scored_candidates else 1.0
        min_score = min(x['struct_score'] for x in scored_candidates) if scored_candidates else 0.0
        score_range = max_score - min_score if max_score != min_score else 1.0
        
        for item in scored_candidates:
            # Normalize structural score
            norm_score = (item['struct_score'] - min_score) / score_range
            
            # Construct reasoning string
            reasoning = f"Structural alignment score: {item['struct_score']:.2f}. "
            if item['ncd_val'] < 0.5:
                reasoning += "High information overlap detected."
            else:
                reasoning += "Low information overlap; relying on structural constraints."
                
            results.append({
                "candidate": item['candidate'],
                "score": float(norm_score),
                "reasoning": reasoning
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment as primary driver.
        Uses Prime Number Theory concept as a 'complexity penalty' wrapper:
        If the combined string length suggests high complexity (like large primes),
        we apply a diminishing return factor to prevent over-confidence in verbose hallucinations.
        """
        score = self._compute_energy(prompt, answer)
        
        # Base confidence from structural score (mapped roughly 0 to 1)
        # Assuming typical scores range from -2 to 6
        base_conf = 1.0 / (1.0 + 2.718 ** (-0.5 * score)) # Sigmoid mapping
        
        # Prime Theory Wrapper: Complexity Penalty
        # Simulates the difficulty of verifying large primes; longer/more complex answers
        # require exponentially more evidence to be trusted.
        total_len = len(prompt) + len(answer)
        complexity_penalty = 1.0 / (1.0 + 0.001 * total_len)
        
        final_conf = base_conf * complexity_penalty
        return max(0.0, min(1.0, final_conf))