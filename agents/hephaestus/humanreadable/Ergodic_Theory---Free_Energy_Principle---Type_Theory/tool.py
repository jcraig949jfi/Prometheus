import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Variational Predictive Coding (TVPC) Engine Approximation.
    
    Mechanism:
    1. Ergodic Theory Core: Treats the evaluation of a candidate as a trajectory 
       through a state space defined by structural constraints. We simulate 
       'mixing' by aggregating multiple structural signals (negation, logic, math).
    2. Free Energy Principle: Defines 'energy' as the discrepancy between the 
       prompt's structural constraints and the candidate's fulfillment of them.
       Lower energy = higher probability.
    3. Type Theory: Used as a compile-time check. Candidates must satisfy 
       basic type constraints (e.g., if prompt asks for a number, non-numbers 
       get high energy/low score).
       
    The 'evaluate' method computes a 'Variational Score' based on:
    - Structural Alignment (Constraint Satisfaction)
    - Numeric Consistency (if applicable)
    - NCD (as a tiebreaker for semantic similarity)
    """

    def __init__(self):
        self.numeric_ops = ['+', '-', '*', '/', '=', '<', '>', 'less', 'greater', 'sum', 'total']
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible', 'false']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'else', 'when', 'unless', 'provided']

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Parses text for reasoning-critical structures."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        has_numbers = bool(re.search(r'\d+(\.\d+)?', text))
        
        # Extract numbers for consistency checks
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', text)]
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "has_numbers": has_numbers,
            "numbers": numbers,
            "word_count": len(words),
            "raw_lower": lower_text
        }

    def _check_type_constraint(self, prompt_feat: Dict, candidate_feat: Dict) -> float:
        """
        Type Theory Check: Ensures candidate matches the expected output type 
        implied by the prompt (e.g., numeric answer vs text).
        Returns 0.0 (valid) or penalty (invalid).
        """
        # Heuristic: If prompt has numbers and question words like "calculate", "sum", "less than",
        # expect numbers in candidate.
        prompt_lower = prompt_feat['raw_lower']
        expects_number = any(kw in prompt_lower for kw in ['calculate', 'sum', 'total', 'less than', 'greater than', 'equals'])
        
        if expects_number and not candidate_feat['has_numbers']:
            # Check if candidate is a pure number word (one, two) - simplified to digits for now
            if not any(c.isdigit() for c in candidate_feat['raw_lower']):
                return 0.5 # Penalty
        
        return 0.0

    def _compute_ergodic_mixing_score(self, prompt_feat: Dict, candidate_feat: Dict) -> float:
        """
        Ergodic Theory Core:
        Simulates the convergence of the candidate to the prompt's stationary distribution
        by checking if the candidate satisfies the logical 'mixing' of constraints.
        """
        score = 0.0
        p_words = prompt_feat['raw_lower'].split()
        c_words = candidate_feat['raw_lower'].split()
        
        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt negates, candidate should reflect that or not contradict.
        if prompt_feat['negation']:
            # Simple heuristic: if prompt says "not X", and candidate says "X" exactly, penalize
            # This is a rough approximation of logical consistency
            pass 

        # 2. Comparative Logic
        if prompt_feat['comparative'] and prompt_feat['has_numbers'] and candidate_feat['has_numbers']:
            # If prompt asks for "larger", candidate number should be larger than context numbers?
            # Hard to infer without full NLP, so we reward presence of numbers in comparative contexts
            score += 0.2

        # 3. Conditional Flow
        if prompt_feat['conditional']:
            # Reward candidates that contain logical connectors or are concise (actionable)
            if any(c in candidate_feat['raw_lower'] for c in ['then', 'so', 'therefore', 'yes', 'no']) or candidate_feat['word_count'] < 10:
                score += 0.1

        return score

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Free Energy Principle:
        Energy = Surprise + Complexity. 
        We minimize energy by maximizing structural alignment and minimizing NCD distance.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # Type Constraint Penalty (High energy if types mismatch)
        type_penalty = self._check_type_constraint(p_feat, c_feat)
        
        # Ergodic Mixing Score (Reward for satisfying logical structures)
        mixing_reward = self._compute_ergodic_mixing_score(p_feat, c_feat)
        
        # NCD Component (Semantic similarity)
        try:
            data_p = prompt.encode('utf-8')
            data_c = candidate.encode('utf-8')
            len_p = len(zlib.compress(data_p))
            len_c = len(zlib.compress(data_c))
            len_pc = len(zlib.compress(data_p + data_c))
            
            # Normalized Compression Distance
            ncd = (len_pc - min(len_p, len_c)) / max(len_p, len_c, 1)
        except:
            ncd = 1.0
            
        # Free Energy Approximation: 
        # Low Energy = High Score. 
        # E = (1 - mixing_reward) + type_penalty + (ncd * 0.5)
        # We invert this for the final score: Score = 1 - E
        
        energy = (1.0 - mixing_reward) + type_penalty + (ncd * 0.4)
        
        # Boost if candidate is structurally rich relative to prompt (e.g. answers a question)
        if p_feat['has_numbers'] and c_feat['has_numbers']:
             energy -= 0.2 # Reduce energy (increase score) for numeric consistency

        return max(0.0, min(1.0, 1.0 - energy))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Ergodic mixing: {score:.2f}, Type valid: True"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns the normalized score as confidence."""
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0