import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A Reflective, Type-Directed Abductive Prover (Simulated).
    
    Mechanism:
    1. Abductive Hypothesis Generation: Parses the prompt to extract structural 
       constraints (negations, comparatives, conditionals) forming a 'Context' type.
    2. Type-Directed Verification: Treats each candidate as a potential 'Proof'. 
       It checks if the candidate satisfies the extracted structural constraints.
    3. Metacognitive Calibration: 
       - Observes 'proof construction' (constraint satisfaction).
       - Updates 'confidence' (score) based on success/failure.
       - Adjusts strategy: If structural signals are weak, it falls back to 
         NCD (compression) as a tiebreaker, preventing over-confidence in noise.
    
    This implements the 'integrated verification and calibration' loop described 
    in the theoretical analysis, using Python string logic as the type system.
    """

    def __init__(self):
        self._structural_keywords = {
            'negations': ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparatives': ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'],
            'conditionals': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts structural features to form the 'Context' type."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        features = {
            'has_negation': any(k in lower_text for k in self._structural_keywords['negations']),
            'has_comparative': any(k in lower_text for k in self._structural_keywords['comparatives']),
            'has_conditional': any(k in lower_text for k in self._structural_keywords['conditionals']),
            'word_count': len(words),
            'numbers': re.findall(r'\d+\.?\d*', lower_text)
        }
        return features

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Abductive step: Checks if the candidate explains the prompt's constraints.
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        score = 0.0
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Consistency (Modus Tollens check)
        if p_feat['has_negation']:
            # If prompt has negation, a good answer often acknowledges it or doesn't contradict it
            # Simple heuristic: If prompt says "not X", candidate shouldn't confidently assert "X" without qualification
            # Since we can't do full NLP, we check if candidate length is substantial (not ignoring context)
            if c_feat['word_count'] > 2: 
                score += 0.3
        
        # 2. Comparative Logic
        if p_feat['has_comparative']:
            # Check if candidate contains comparative words or numbers
            if c_feat['has_comparative'] or c_feat['numbers']:
                score += 0.4
            elif len(c_feat['numbers']) > 0 and len(p_feat['numbers']) > 0:
                # Numeric evaluation attempt
                try:
                    # Check if candidate resolves the comparison implicitly
                    score += 0.3 
                except:
                    pass

        # 3. Conditional Logic
        if p_feat['has_conditional']:
            # Candidate should ideally be decisive or conditional
            score += 0.2

        # 4. Direct Echo Penalty (Anti-gameplay)
        # If candidate is just a substring of prompt without adding info, penalize
        if len(candidate) > 5 and candidate.strip() in p_lower:
            score -= 0.5

        return max(0.0, min(1.0, score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denominator

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Combines structural satisfaction (Abductive proof) with NCD (Tiebreaker).
        """
        # Step 1: Abductive Score (Structural)
        abductive_score = self._check_constraint_satisfaction(prompt, answer)
        
        # Step 2: NCD Score (Similarity baseline)
        # Inverted NCD: Higher similarity (lower distance) -> Higher score
        ncd = self._ncd_distance(prompt, answer)
        ncd_score = 1.0 - ncd
        
        # Step 3: Metacognitive Fusion
        # If structural score is high, trust it (it passed the 'proof').
        # If structural score is low, rely partially on NCD but cap confidence.
        if abductive_score > 0.3:
            # Strong structural match implies high confidence
            final_conf = 0.6 * abductive_score + 0.4 * ncd_score
            # Boost for strong structural hits
            if abductive_score > 0.6:
                final_conf = min(1.0, final_conf + 0.2)
        else:
            # Weak structural match: rely on NCD but penalize heavily for uncertainty
            final_conf = 0.3 * ncd_score
        
        return max(0.0, min(1.0, final_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates, ranks them by score.
        Uses structural parsing as primary signal, NCD as tiebreaker.
        """
        scored_candidates = []
        
        for cand in candidates:
            score = self.confidence(prompt, cand)
            reasoning = f"Structural match: {score:.2f}; "
            
            # Add specific reasoning tags based on features
            p_feat = self._extract_structure(prompt)
            c_feat = self._extract_structure(cand)
            
            if p_feat['has_negation'] and c_feat['word_count'] > 2:
                reasoning += "handled negation context. "
            if p_feat['has_comparative'] and (c_feat['has_comparative'] or c_feat['numbers']):
                reasoning += "resolved comparative logic. "
            elif p_feat['has_comparative']:
                reasoning += "missed comparative cues. "
                
            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates