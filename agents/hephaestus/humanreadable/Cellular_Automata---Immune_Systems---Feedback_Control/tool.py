import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Clonal Cellular Automaton (STCCA) inspired reasoning engine.
    
    Mechanism:
    1. Lattice (Prompt Parsing): The input prompt is parsed into a structural lattice
       of features (negations, comparatives, conditionals, numeric values).
    2. Clonal Selection (Candidate Evaluation): Candidates are treated as rule-sets.
       Their 'fitness' is determined by structural alignment with the prompt's logic.
    3. Feedback Control (PID-like Tuning): 
       - Error (mismatch in logic/numbers) increases 'mutation' tolerance (partial credit).
       - Success (exact logic match) increases 'selection pressure' (high score).
       - Integral Memory: Tracks running success of specific structural patterns to 
         boost confidence in recurring valid logic forms.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        # Integral memory: stores weights for successful structural patterns
        self.memory_patterns = {} 
        self.global_error_integral = 0.0

    def _parse_structure(self, text: str) -> dict:
        """Extract logical structure: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|else)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst)\b', text_lower)),
            'logic_ops': len(re.findall(r'\b(and|or|but|however|therefore)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_fitness(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Calculate fitness based on structural alignment (Clonal Selection).
        Higher fitness = better logical match.
        """
        score = 0.0
        
        # 1. Numeric Consistency (Strict)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Check if candidate preserves numeric relationships or exact matches
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            # Simple heuristic: if prompt has numbers, candidate should reflect them or their logic
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 2.0
            # Check order preservation if lengths match
            if len(p_nums) == len(c_nums):
                if all(p == c for p, c in zip(p_nums, c_nums)):
                    score += 3.0
        
        # 2. Logical Structure Alignment
        # Negation match
        if prompt_feats['negations'] > 0:
            if cand_feats['negations'] > 0:
                score += 1.5
            else:
                score -= 1.0 # Penalty for missing negation
        
        # Conditional match
        if prompt_feats['conditionals'] > 0:
            if cand_feats['conditionals'] > 0:
                score += 1.5
                
        # Comparative match
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] > 0:
                score += 1.5

        # 3. Integral Memory Lookup
        # Boost score if this structural pattern has historically been reliable
        pattern_key = f"n{prompt_feats['negations']}c{prompt_feats['conditionals']}"
        memory_boost = self.memory_patterns.get(pattern_key, 0.0)
        score += memory_boost

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._parse_structure(prompt)
        results = []
        
        if not candidates:
            return []

        # Phase 1: Raw Fitness Evaluation
        raw_scores = []
        for cand in candidates:
            cand_feats = self._parse_structure(cand)
            fitness = self._evaluate_fitness(prompt_feats, cand_feats, prompt, cand)
            
            # NCD Tiebreaker component (normalized)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, scale small
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            total_score = fitness + ncd_score
            raw_scores.append((cand, total_score, fitness))

        # Phase 2: Feedback Control (Normalization & Ranking)
        # Determine max fitness to adjust selection pressure
        max_fit = max(s[2] for s in raw_scores) if raw_scores else 0
        min_fit = min(s[2] for s in raw_scores) if raw_scores else 0
        range_fit = max_fit - min_fit if (max_fit - min_fit) > 0 else 1.0

        final_results = []
        for cand, total_score, fitness in raw_scores:
            # Normalize score to 0-1 range roughly, heavily weighting structural fitness
            # Base normalization
            norm_score = (fitness - min_fit) / range_fit
            
            # Feedback loop: Update integral memory based on high fitness
            # If this candidate looks logically sound (high fitness), reinforce its pattern
            if fitness > 0:
                p_feats = self._parse_structure(prompt)
                key = f"n{p_feats['negations']}c{p_feats['conditionals']}"
                # Integral term accumulation
                self.memory_patterns[key] = self.memory_patterns.get(key, 0.0) + 0.1
            
            # Construct reasoning string
            reasoning = f"Structural alignment score: {fitness:.2f}. "
            if prompt_feats['numbers'] and self._parse_structure(cand)['numbers']:
                reasoning += "Numeric consistency detected. "
            if prompt_feats['negations'] != self._parse_structure(cand)['negations'] and prompt_feats['negations'] > 0:
                reasoning += "Warning: Negation mismatch. "
            
            final_results.append({
                "candidate": cand,
                "score": float(norm_score), # Final normalized score
                "reasoning": reasoning.strip()
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parity and NCD as a secondary check.
        """
        p_feats = self._parse_structure(prompt)
        a_feats = self._parse_structure(answer)
        
        confidence = 0.5 # Base uncertainty
        
        # Structural matches boost confidence
        matches = 0
        total_checks = 0
        
        if p_feats['negations'] > 0 or a_feats['negations'] > 0:
            total_checks += 1
            if p_feats['negations'] == a_feats['negations']:
                matches += 1
        
        if p_feats['conditionals'] > 0 or a_feats['conditionals'] > 0:
            total_checks += 1
            if p_feats['conditionals'] == a_feats['conditionals']:
                matches += 1
                
        if p_feats['numbers']:
            total_checks += 1
            if a_feats['numbers']:
                # Check numeric overlap
                if any(abs(p - a) < 1e-6 for p in p_feats['numbers'] for a in a_feats['numbers']):
                    matches += 1
            elif len(p_feats['numbers']) == 0:
                matches += 0 # Neutral

        if total_checks > 0:
            structural_conf = matches / total_checks
            confidence = 0.3 + (structural_conf * 0.6) # Max 0.9 from structure
        
        # NCD penalty for very different lengths/content if structure is vague
        if total_checks == 0:
            ncd = self._compute_ncd(prompt, answer)
            confidence = 0.5 - (ncd * 0.4) # High NCD lowers confidence if no structure
            
        return max(0.0, min(1.0, confidence))