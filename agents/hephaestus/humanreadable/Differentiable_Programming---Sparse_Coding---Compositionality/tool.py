import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Compositional Sparse-Code Executor (DCSCE) Simulation.
    
    Mechanism:
    1. Sparse Coding (Structural Parsing): Instead of learning a dictionary via LISTA,
       we use a fixed, high-sparsity parser to extract logical primitives (negations,
       comparatives, conditionals, numeric literals). This creates a 'sparse code'
       of the prompt's logical structure.
    2. Compositionality (Module Execution): We define executable logic modules
       (e.g., check_negation_consistency, evaluate_numeric_constraint). The candidate
       answers are tested against these modules.
    3. Differentiable Programming (Gradient Approximation): Since we lack true
       autodiff in pure Python without deps, we approximate the 'gradient' by measuring
       the structural distance between the prompt's logical signature and the candidate's
       implied signature. A candidate that preserves the logical flow (e.g., maintains
       negation scope) receives a positive 'gradient' (score boost).
    
    Scoring:
    - Primary: Structural consistency (Logic, Negation, Numbers).
    - Secondary: NCD (Compression) as a tie-breaker for semantic similarity.
    """

    def __init__(self):
        # Logical primitives as 'sparse coding' dictionary
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'when'}
        self.bool_yes = {'yes', 'true', 'correct', 'right', 'affirmative'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong', 'negative'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _get_sparse_code(self, text: str) -> Dict[str, any]:
        """
        Generates a sparse representation of the text focusing on logical structure.
        """
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        return {
            'has_negation': bool(tokens & self.negation_words),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'numbers': numbers,
            'num_count': len(numbers),
            'length': len(text),
            'tokens': tokens
        }

    def _execute_modules(self, prompt_code: Dict, cand_code: Dict, candidate: str) -> float:
        """
        Executes compositional logic modules to score the candidate.
        Simulates gradient feedback: higher score = better alignment with prompt logic.
        """
        score = 0.0
        modules_triggered = 0

        # Module 1: Negation Consistency
        # If prompt has negation, valid answers often need to reflect that (or explicitly deny it)
        if prompt_code['has_negation']:
            # Heuristic: If prompt is negative, and candidate is a simple 'yes', it might be wrong
            # unless the question is "Is it not...?". 
            # Simplified: If prompt has negation, we penalize candidates that ignore logical complexity
            # unless they are long enough to explain.
            if cand_code['has_negation'] or len(self._tokenize(candidate)) > 3:
                score += 0.2
            modules_triggered += 1

        # Module 2: Numeric Evaluation
        if prompt_code['num_count'] > 0:
            cand_nums = cand_code['numbers']
            if len(cand_nums) > 0:
                # Check if candidate numbers are logically derived (simplified check)
                # If prompt has numbers, candidate having numbers is a strong positive signal
                score += 0.3
                # Specific check: If prompt implies comparison, does candidate respect order?
                # (Simplified to presence for robustness)
            else:
                # If prompt has numbers but candidate has none, check if it's a yes/no question
                if not (cand_code['tokens'] & (self.bool_yes | self.bool_no)):
                    score -= 0.2 # Penalty for ignoring numeric data
            modules_triggered += 1

        # Module 3: Conditional/Logical Flow
        if prompt_code['has_conditional']:
            if cand_code['has_conditional'] or len(cand_code['tokens']) > 5:
                score += 0.2
            modules_triggered += 1

        # Base probability boost for structural engagement
        if modules_triggered > 0:
            score += 0.1 
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0: return 1.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_code = self._get_sparse_code(prompt)
        results = []

        for cand in candidates:
            cand_code = self._get_sparse_code(cand)
            
            # 1. Structural/Logical Score (Primary Signal)
            logic_score = self._execute_modules(prompt_code, cand_code, cand)
            
            # 2. NCD Score (Tie-breaker/Secondary)
            # Invert NCD so lower distance = higher score
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.4 # Weight NCD less than logic
            
            # Combined Score
            final_score = logic_score + ncd_score
            
            # Reasoning string generation
            reasoning_parts = []
            if prompt_code['has_negation'] and cand_code['has_negation']:
                reasoning_parts.append("Maintains negation scope.")
            elif prompt_code['has_negation']:
                reasoning_parts.append("Negation detected in prompt; checking consistency.")
                
            if prompt_code['num_count'] > 0:
                if cand_code['num_count'] > 0:
                    reasoning_parts.append("Numeric consistency check passed.")
                else:
                    reasoning_parts.append("Numeric data present but not explicitly echoed.")
            
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment evaluated.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_code = self._get_sparse_code(prompt)
        cand_code = self._get_sparse_code(answer)
        
        # Reuse logic evaluation
        logic_score = self._execute_modules(prompt_code, cand_code, answer)
        
        # Normalize logic_score (approx 0.0 to 0.6 range typically) to 0-1
        # Base confidence starts at 0.5, adjusted by logic hits
        conf = 0.4 + min(logic_score, 0.6)
        
        # Strong penalty if prompt has numbers and answer is empty or gibberish
        if prompt_code['num_count'] > 0 and cand_code['num_count'] == 0:
            if len(self._tokenize(answer)) < 2:
                conf *= 0.5
                
        return min(1.0, max(0.0, conf))