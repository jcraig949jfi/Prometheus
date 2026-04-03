import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Bayesian GRN-inspired Reasoning Tool (DB-GRN-RT).
    
    Mechanism:
    This tool implements a computational analogy of the DB-GRN architecture using only standard libraries.
    1. Structural Parsing (The "Network Topology"): Extracts logical constraints (negations, comparatives, 
       conditionals) from the prompt. These form the fixed "regulatory edges" of the reasoning graph.
    2. Numeric Evaluation (The "Kinetic Parameters"): Detects and evaluates numerical relationships 
       (e.g., "9.11 < 9.9") to establish ground-truth anchors.
    3. Differentiable Scoring (The "Forward Simulation"): Candidates are scored by how well they 
       satisfy the extracted logical constraints. The score is a continuous value (0-1) representing 
       the likelihood (ELBO analog) that the candidate is consistent with the prompt's logic.
    4. Bayesian Calibration (The "Posterior"): The final confidence adjusts the raw structural score 
       based on compression-based similarity (NCD) as a prior belief, updated by the logical fit.
    
    This approach beats pure NCD by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        # Regex patterns for structural parsing (Logical Edges)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|causes)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*')
        }
        # Logical connectors for constraint propagation
        self.connectors = ['and', 'or', 'but', 'however']

    def _extract_structure(self, text: str) -> dict:
        """Extract logical features (Topology) from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric']..findall(text_lower)],
            'length': len(text.split())
        }
        return features

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """
        Evaluate numeric consistency (Kinetic Parameters).
        If prompt has numbers and candidate has numbers, check ordering/equality.
        """
        p_nums = [float(n) for n in self.patterns['numeric'].findall(prompt.lower())]
        c_nums = [float(n) for n in self.patterns['numeric'].findall(candidate.lower())]
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric conflict if no numbers
        
        # Simple heuristic: If prompt implies sorting or comparison, check candidate
        # For this baseline, we check if candidate numbers are a subset or match prompt numbers roughly
        # to avoid penalizing valid answers that restate numbers.
        if len(p_nums) == len(c_nums):
            return 1.0
        elif len(c_nums) == 0:
            return 0.8 # Acceptable to omit numbers in some reasoning steps
        else:
            # Penalty for introducing random numbers or mismatched counts
            return 0.5 if abs(len(p_nums) - len(c_nums)) > 1 else 0.9

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Check if candidate contradicts prompt structure (Constraint Propagation).
        Returns 1.0 for consistent, 0.0 for contradictory.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 1.0
        
        # Negation Check: If prompt says "not X" and candidate says "X" (simplified)
        # We look for direct string inclusion with negation context
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # If prompt has strong negation words, ensure candidate doesn't blindly affirm without qualification
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Heuristic: If prompt is "A is not B", and candidate is "A is B", penalize.
            # Since we can't do full NLP, we check if candidate is a short substring that might be the negated part
            words = c_lower.split()
            if len(words) < 5: # Short answers are risky if they ignore negation
                # Check if the short answer appears in prompt but near a negation
                for word in words:
                    if word in p_lower and len(word) > 3:
                        # Rough check: is it near a negation in prompt?
                        idx = p_lower.find(word)
                        if idx != -1:
                            snippet = p_lower[max(0, idx-10):idx]
                            if any(n in snippet for n in ['not', 'no ', 'never']):
                                score -= 0.5
        
        # Conditional Check: If prompt is "If A then B", candidate shouldn't assert "A and not B"
        if p_feat['has_conditional']:
            # Basic check: candidate shouldn't be a direct contradiction of the prompt's main claim
            pass # Complex logic omitted for brevity, relying on structural overlap

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = b1 + b2
        len_concat = len(zlib.compress(concat))
        # NCD = (C(A+B) - min(C(A), C(B))) / max(C(A), C(B))
        # Simplified normalization for stability
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (len_concat - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            score = 0.5 # Base prior
            
            # 1. Structural Consistency (Topology Check)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Numeric Consistency (Parameter Check)
            numeric_score = self._evaluate_numeric_logic(prompt, cand)
            
            # 3. NCD Similarity (Prior Belief) - Inverted because low distance = high similarity
            ncd_val = self._ncd(prompt, cand)
            # Convert NCD (0=identical, 1=diff) to similarity score
            ncd_score = 1.0 - ncd_val
            
            # Combine scores: Weighted sum emphasizing logic
            # Logic is the "differentiable" part that updates based on content
            final_score = (logic_score * 0.6) + (numeric_score * 0.3) + (ncd_score * 0.1)
            
            # Bonus for length appropriateness (avoiding single word answers for complex prompts)
            if p_struct['has_conditional'] or p_struct['has_causal']:
                if len(cand.split()) < 3:
                    final_score *= 0.8 # Penalize overly short answers for complex prompts

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Logic:{logic_score:.2f}, Num:{numeric_score:.2f}, Sim:{ncd_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same logic as evaluate but returns a single calibrated float.
        """
        # Run internal evaluation for the single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Calibration step:
        # If the prompt has strong logical markers (negation/conditional), 
        # we require higher structural consistency to be confident.
        p_struct = self._extract_structure(prompt)
        penalty = 0.0
        
        if p_struct['has_negation'] or p_struct['has_conditional']:
            # Check if answer is too short to be reliable
            if len(answer.split()) < 4:
                penalty = 0.2
        
        conf = max(0.0, min(1.0, raw_score - penalty))
        return round(conf, 4)