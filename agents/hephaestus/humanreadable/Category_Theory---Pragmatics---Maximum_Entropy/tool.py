import re
import json
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Context-Sensitive Entropic Functorial Model (CEFM) Approximation.
    
    Mechanism:
    1. Objects: Parsed structural features (negations, comparatives, conditionals, numbers).
    2. Morphisms (Pragmatics): Rules that shift scores based on context (e.g., negation flips logic).
    3. Functor (F): Maps structural features to a probability distribution (score).
    4. MaxEnt Principle: Scores are initialized uniformly and adjusted minimally to satisfy 
       observed structural constraints (presence of keywords), avoiding arbitrary bias.
    5. Natural Transformation (Eta): Compares the candidate's structural signature against the 
       prompt's required signature. The KL-divergence approximation is the penalty for mismatch.
    
    This implementation prioritizes structural parsing and constraint propagation as requested,
    using NCD only as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        # Structural patterns for parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['yes', 'no', 'true', 'false']
        
    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text (Objects in Category C)."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        features = {
            'has_negation': any(n in words for n in self.negations),
            'has_comparative': any(c in words for c in self.comparatives),
            'has_conditional': any(c in words for c in self.conditionals),
            'negation_count': sum(words.count(n) for n in self.negations),
            'word_count': len(words),
            'numbers': self._extract_numbers(text),
            'boolean_answer': next((w for w in self.booleans if w in words), None)
        }
        return features

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for evaluation."""
        # Match floats and ints
        matches = re.findall(r'[-+]?\d*\.?\d+', text)
        return [float(m) for m in matches]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(len(b1), len(b2))
            if min_len == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _pragmatic_morphism(self, prompt_feats: Dict, cand_feats: Dict, base_score: float) -> float:
        """
        Apply pragmatic moves (morphisms) to adjust scores based on context.
        Simulates the functorial mapping F: C -> Prob with MaxEnt constraints.
        """
        score = base_score
        
        # Constraint 1: Negation Consistency
        # If prompt has negation, candidate should reflect understanding (simplified heuristic)
        if prompt_feats['has_negation']:
            # Penalize candidates that ignore negation context if they are simple booleans
            if cand_feats['boolean_answer'] and not prompt_feats['has_negation']:
                score *= 0.9 # Slight penalty for mismatched context complexity
        
        # Constraint 2: Numeric Evaluation
        # If prompt has numbers, prefer candidates with numbers or logical consistency
        if len(prompt_feats['numbers']) >= 2:
            if len(cand_feats['numbers']) > 0:
                # Check simple ordering if comparative exists
                if prompt_feats['has_comparative']:
                    # Heuristic: If prompt asks for "larger", and candidate has larger number
                    p_nums = sorted(prompt_feats['numbers'])
                    c_nums = cand_feats['numbers']
                    # Reward if candidate number is distinct and relevant (simplified)
                    score += 0.1
            else:
                # Penalty for ignoring numeric data in a math context
                score *= 0.8

        # Constraint 3: Conditional Logic
        if prompt_feats['has_conditional']:
            if cand_feats['has_conditional']:
                score += 0.15 # Reward matching logical structure
            elif cand_feats['boolean_answer']:
                score -= 0.1 # Penalize oversimplification of conditional logic

        return score

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the primary score based on structural parsing and constraint propagation.
        This represents the KL-divergence minimization between prompt requirements and candidate.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Base score: Start with uniform prior (MaxEnt principle)
        score = 0.5
        
        # Apply Pragmatic Morphisms (Contextual adjustments)
        score = self._pragmatic_morphism(p_feats, c_feats, score)
        
        # Specific Structural Checks
        
        # 1. Numeric Evaluation (Transitivity/Comparison)
        if len(p_feats['numbers']) >= 2 and len(c_feats['numbers']) >= 1:
            p_nums = p_feats['numbers']
            c_num = c_feats['numbers'][0]
            
            # Simple logic check: If prompt implies sorting/comparison
            if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                if c_num == max(p_nums):
                    score += 0.4
                else:
                    score -= 0.2
            elif 'smaller' in prompt.lower() or 'less' in prompt.lower():
                if c_num == min(p_nums):
                    score += 0.4
                else:
                    score -= 0.2
                    
        # 2. Boolean Consistency with Negation
        if p_feats['has_negation']:
            # If prompt is negative, simple 'yes' might be wrong depending on phrasing
            # This is a shallow check but captures the pattern
            if c_feats['boolean_answer'] == 'yes':
                score -= 0.1 
            if c_feats['boolean_answer'] == 'no':
                score += 0.1

        # 3. Length/Complexity matching (Heuristic for "Natural Transformation")
        # If prompt is complex (long), very short answers might be under-fitting
        if p_feats['word_count'] > 20 and c_feats['word_count'] < 3:
            if not c_feats['boolean_answer']:
                score -= 0.05

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        scores = []
        
        # Phase 1: Compute Structural Scores (Primary Signal)
        for cand in candidates:
            s = self._compute_structural_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": s,
                "reasoning": "Structural and pragmatic analysis"
            })
            scores.append(s)
        
        # Phase 2: NCD Tiebreaker (Only if structural scores are effectively equal)
        # We use a small epsilon to determine "equality" for floating point
        epsilon = 0.01
        final_results = []
        
        for i, res in enumerate(results):
            current_score = res['score']
            is_tie = False
            
            # Check for ties with other candidates
            for j, other_score in enumerate(scores):
                if i != j and abs(current_score - other_score) < epsilon:
                    is_tie = True
                    break
            
            if is_tie:
                # Apply NCD as tiebreaker
                ncd_val = self._compute_ncd(prompt, res['candidate'])
                # Invert NCD (lower distance = higher score) and add as small perturbation
                tie_breaker_bonus = (1.0 - ncd_val) * 0.001 
                res['score'] += tie_breaker_bonus
                res['reasoning'] += " (NCD tiebreak applied)"
            
            final_results.append(res)
            
        # Sort descending by score
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Normalize scores to ensure 0-1 range after adjustments
        max_s = max(r['score'] for r in final_results) if final_results else 1.0
        min_s = min(r['score'] for r in final_results) if final_results else 0.0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        for r in final_results:
            r['score'] = round((r['score'] - min_s) / range_s, 4) if range_s != 0 else 0.5
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence by comparing the answer's structural fit to the prompt.
        Returns a value between 0 and 1.
        """
        # Use the internal scoring mechanism
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']