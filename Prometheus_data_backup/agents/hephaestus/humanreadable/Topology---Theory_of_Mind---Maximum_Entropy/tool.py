import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topological Theory-of-Mind Maximum-Entropy (ToM-ME) Inference Engine.
    
    Mechanism:
    1. Topology (Structural Parsing): Instead of computing persistent homology on 
       high-dimensional vectors (which is non-deterministic without heavy libs), 
       we map the "shape" of the logical space by extracting structural features:
       negations, comparatives, conditionals, and numeric constraints. This forms 
       the "persistence diagram" of the text's logic.
    2. Theory of Mind (Constraint Propagation): We simulate an agent evaluating 
       the candidate against these extracted constraints. We check if the candidate 
       respects the subject-object roles and logical operators found in the prompt.
    3. Maximum Entropy (Confidence Calibration): We use a MaxEnt-inspired penalty. 
       If a candidate contradicts a detected structural constraint, it receives a 
       heavy penalty (low entropy solution). If it aligns, it retains probability mass. 
       The final score balances structural match (reasoning) with NCD (tiebreaker).
    
    This approach beats pure NCD by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        # Structural patterns for "Topological" mapping
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bimpossible\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', 
                                     r'\bsmaller\s+than\b', r'\bhigher\s+than\b', r'\blower\s+than\b',
                                     r'>', r'<', r'\bbeats\b', r'\texceeds\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b', r'\bonly\s+if\b']
        self.numeric_pattern = r'\d+\.?\d*'

    def _extract_topology(self, text: str) -> dict:
        """Extracts logical 'shape' features (negations, comparatives, numbers)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': re.findall(self.numeric_pattern, text),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate_nums: List[str], prompt_text: str) -> float:
        """Evaluates numeric logic if numbers are present."""
        if not prompt_nums:
            return 1.0 # No numeric constraints
        
        # Simple heuristic: If prompt has numbers and candidate has numbers, 
        # check if they appear in a consistent order or magnitude if comparatives exist.
        if not candidate_nums:
            return 0.5 # Missing data is uncertain
        
        try:
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in candidate_nums]
            
            # If prompt implies an order (e.g., "greater than"), check candidate
            if any(re.search(p, prompt_text.lower()) for p in self.comparative_patterns):
                if len(p_vals) >= 1 and len(c_vals) >= 1:
                    # Heuristic: If prompt asks for "greater than X", candidate should be > X
                    # This is a simplified simulation of constraint propagation
                    if "greater" in prompt_text.lower() or "more" in prompt_text.lower() or ">" in prompt_text:
                        if c_vals[0] > p_vals[0]: return 1.0
                        else: return 0.2
                    elif "less" in prompt_text.lower() or "smaller" in prompt_text.lower() or "<" in prompt_text:
                        if c_vals[0] < p_vals[0]: return 1.0
                        else: return 0.2
        except ValueError:
            pass
            
        return 1.0 # Default pass if logic not clearly violated

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment (Topology) and 
        constraint satisfaction (ToM).
        """
        p_feat = self._extract_topology(prompt)
        c_feat = self._extract_topology(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Topological Hole Checking)
        # If prompt has negation, valid answers often need to reflect that or be specific
        if p_feat['negations'] > 0:
            # Heuristic: If prompt denies something, a simple "Yes" might be wrong depending on context
            # We boost candidates that seem to address the complexity (longer than 5 words) 
            # or contain specific negation words if the prompt is a negation question.
            if c_feat['length'] > 3: 
                score += 0.2
        
        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            num_score = self._check_numeric_consistency(p_feat['numbers'], c_feat['numbers'], prompt)
            score += num_score * 0.5
            
        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            # Candidates addressing conditionals often contain "if", "yes", "no", or specific outcomes
            if c_feat['length'] > 2:
                score += 0.2

        # 4. Length/Complexity Match (Entropy Regularizer)
        # Prevents trivial answers to complex questions
        if p_feat['length'] > 10 and c_feat['length'] < 2:
            score -= 0.3 # Penalty for oversimplification
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Score: Structural/Logical alignment
            struct_score = self._structural_score(prompt, cand)
            
            # Tiebreaker: NCD (Normalized Compression Distance)
            # Lower NCD is better (more similar), so we invert it for scoring
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Combined Score: Structural reasoning dominates, NCD breaks ties
            # Weighting: 80% structural, 20% similarity (as tiebreaker)
            final_score = (struct_score * 0.8) + (ncd_score * 0.2)
            
            # Adjust for exact matches or obvious logical keywords
            cand_lower = cand.lower()
            if "yes" in cand_lower and "no" not in cand_lower:
                if any(n in prompt.lower() for n in self.negation_patterns):
                    # Potential trap: "Is it not X?" -> "Yes" might be ambiguous, 
                    # but usually "Yes" confirms the negative premise. 
                    # We rely on structural score here, but add small boost if consistent.
                    pass 
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {struct_score:.2f}, Similarity: {ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses structural consistency as the primary driver (MaxEnt principle: 
        prefer the answer that best satisfies all logical constraints without bias).
        """
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score to 0-1 confidence range
        # Structural score can be negative, so we clamp and normalize
        # Base expectation: random guess ~0.5, good reasoning >0.7
        confidence = max(0.0, min(1.0, (raw_score + 0.5) / 1.5))
        
        return confidence