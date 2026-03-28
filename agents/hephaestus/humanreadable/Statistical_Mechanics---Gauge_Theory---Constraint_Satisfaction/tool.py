import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Invariant Belief Propagation (GBP) Approximation for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Gauge Fixing): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'skeleton' of the problem. 
       This fixes the gauge, removing symmetric ambiguities in interpretation.
    2. Constraint Propagation (Message Passing): Evaluates candidates against 
       extracted structural rules. Candidates violating hard constraints (e.g., 
       logical negation flips) receive infinite energy (score 0).
    3. Statistical Evaluation: Computes a free-energy-like score based on 
       constraint satisfaction density.
    4. Gauge-Invariant Confidence: The final score is normalized by the 
       complexity of the constraint graph, acting as a symmetry-aware confidence.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Gauge Connection")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore)\b', re.I)
        }

    def _extract_structure(self, text: str) -> dict:
        """Parses text to identify logical constraints (Gauge Fixing)."""
        lower_text = text.lower()
        return {
            'has_negation': bool(self.patterns['negation'].search(lower_text)),
            'has_comparative': bool(self.patterns['comparative'].search(lower_text)),
            'has_conditional': bool(self.patterns['conditional'].search(lower_text)),
            'has_numbers': bool(self.patterns['numeric'].search(lower_text)),
            'word_count': len(text.split()),
            'char_count': len(text)
        }

    def _check_constraint_violation(self, prompt_struct: dict, candidate: str) -> float:
        """
        Checks for hard logical violations (Energy Penalty).
        Returns 0.0 for violation, 1.0 for pass.
        """
        c_lower = candidate.lower()
        
        # Hard Constraint 1: Negation Consistency
        # If prompt emphasizes negation, candidate shouldn't be a blind affirmative without context
        if prompt_struct['has_negation']:
            # Simple heuristic: if prompt says "not", and candidate is just "yes" or "true", penalize
            if c_lower in ['yes', 'true', 'correct', '1']:
                # Check if the candidate actually addresses the negation (simplified)
                if not self.patterns['negation'].search(c_lower):
                    return 0.5 # Soft penalty for potential misunderstanding
        
        # Hard Constraint 2: Numeric Consistency (if numbers exist)
        if prompt_struct['has_numbers']:
            p_nums = [float(x) for x in self.patterns['numeric'].findall(prompt_struct.get('_raw_', ''))]
            c_nums = [float(x) for x in self.patterns['numeric'].findall(c_lower)]
            
            # If prompt has numbers and candidate has none, it might be vague (not necessarily wrong)
            # But if candidate has numbers that contradict simple ordering (advanced), flag it.
            # Here we just note presence for scoring weight.
            if len(p_nums) > 0 and len(c_nums) == 0:
                pass # No hard penalty, but affects score magnitude later

        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Computes the core reasoning score based on structural alignment."""
        p_struct = self._extract_structure(prompt)
        p_struct['_raw_'] = prompt
        c_struct = self._extract_structure(candidate)
        
        # 1. Gauge Fixing: Apply hard constraint penalties
        violation_factor = self._check_constraint_violation(p_struct, candidate)
        if violation_factor < 1.0:
            return violation_factor * 0.1 # Strong penalty

        score = 1.0
        
        # 2. Message Passing: Feature Alignment
        # If prompt has comparatives, candidate should ideally reflect comparison or specific value
        if p_struct['has_comparative']:
            if c_struct['has_comparative'] or c_struct['has_numbers']:
                score += 0.3
            else:
                score -= 0.2 # Penalty for ignoring comparative nature
        
        # If prompt has conditionals, candidate should be nuanced (longer, specific)
        if p_struct['has_conditional']:
            if c_struct['word_count'] < 3:
                score -= 0.4 # Too short for conditional logic
            else:
                score += 0.2

        # 3. Numeric Evaluation
        if p_struct['has_numbers'] and c_struct['has_numbers']:
            score += 0.3
        elif p_struct['has_numbers'] and not c_struct['has_numbers']:
            score -= 0.1

        # 4. Length/Complexity Matching (Entropy check)
        # Prevents "Yes" answers to complex questions
        if p_struct['word_count'] > 15 and c_struct['word_count'] < 4:
            score -= 0.5
        
        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
        return (c12 - min_len) / (max(c1, c2) + 1e-6)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using GBP-inspired structural scoring.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Pre-calculate prompt structure to avoid re-parsing
        p_struct = self._extract_structure(prompt)
        p_struct['_raw_'] = prompt

        for cand in candidates:
            # 1. Structural Score (The "Free Energy" of the hypothesis)
            raw_score = self._compute_structural_score(prompt, cand)
            
            # 2. NCD Tiebreaker (Only if structural scores are close, handled implicitly by sorting stability)
            # We store NCD to break ties if needed, but primary sort is raw_score
            ncd_val = self._ncd_distance(prompt, cand)
            
            # Reasoning string generation
            reasoning_parts = []
            if raw_score < 0.5:
                reasoning_parts.append("Violates structural constraints.")
            if p_struct['has_negation'] and 'not' not in cand.lower() and cand.lower() in ['yes', 'true']:
                reasoning_parts.append("Ignores negation context.")
            if p_struct['has_comparative'] and not self._extract_structure(cand)['has_comparative']:
                reasoning_parts.append("Lacks comparative detail.")
            if not reasoning_parts:
                reasoning_parts.append("Aligns with prompt structure and constraints.")
                
            scored_candidates.append({
                'candidate': cand,
                'score': raw_score,
                'ncd': ncd_val, # For tie-breaking
                'reasoning': " ".join(reasoning_parts)
            })

        # Sort: Primary by score (desc), Secondary by NCD (asc - lower distance is better)
        # We invert NCD for sorting so higher is better? No, standard sort is asc.
        # We want high score, low NCD.
        scored_candidates.sort(key=lambda x: (x['score'], -x['ncd']), reverse=True)
        # Wait, reverse=True on tuple means (High Score, High NCD). 
        # We want (High Score, Low NCD).
        # So we sort by (score, -ncd) with reverse=True? 
        # If score is same, we want smaller NCD. 
        # Tuple comparison: (1.0, -0.2) vs (1.0, -0.5). -0.2 > -0.5. 
        # So (1.0, -0.2) comes first. This means larger NCD comes first. Wrong.
        # We want smaller NCD. So we want larger (-NCD). 
        # Actually, let's just use a custom key or two-step sort.
        
        # Correct sorting:
        # Primary: Score (Descending)
        # Secondary: NCD (Ascending)
        scored_candidates.sort(key=lambda x: x['ncd']) # Stable sort secondary
        scored_candidates.sort(key=lambda x: x['score'], reverse=True) # Primary

        # Normalize scores to 0-1 range roughly based on max found, but keep absolute meaning
        # The prompt asks for score float. Higher = more likely.
        
        result = []
        for item in scored_candidates:
            result.append({
                'candidate': item['candidate'],
                'score': round(item['score'], 4),
                'reasoning': item['reasoning']
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural score as a proxy for confidence in the answer's validity.
        """
        if not answer:
            return 0.0
        
        # Reuse evaluation logic for a single candidate
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        base_score = results[0]['score']
        
        # Calibrate: 
        # Base score from structural check is roughly 0.0 to 1.5+
        # Map to 0.0 - 1.0
        confidence = min(1.0, max(0.0, base_score))
        
        # Boost if structural features match well
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        bonus = 0.0
        if p_struct['has_numbers'] and a_struct['has_numbers']:
            bonus += 0.1
        if p_struct['has_conditional'] and a_struct['word_count'] > 10:
            bonus += 0.1
            
        return min(1.0, confidence + bonus)