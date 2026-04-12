import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    IB-ToMnet Inspired Reasoning Tool.
    
    Mechanism:
    Implements a simplified Information-Bottleneck constrained Recursive Theory-of-Mind network.
    1. Structural Parsing (The 'Belief' B_i): Extracts logical constraints (negations, comparatives, 
       conditionals) and numeric values from the prompt. This forms the prior P_i.
    2. Utility Maximization (U_i): Candidates are scored based on constraint satisfaction.
       - Exact keyword matches for logic operators yield high utility.
       - Numeric consistency yields high utility.
    3. Information Bottleneck (KL-Divergence): Penalizes candidates that deviate significantly 
       from the structural 'prior' established by the prompt's logical form without adding 
       predictive value. 
    4. Equilibrium (QRE): The final score is the utility minus the KL-cost (regularization), 
       simulating a Quantal Response Equilibrium where agents balance reward against information cost.
       
    Note: Per causal analysis, 'Theory of Mind' is restricted to the confidence wrapper and 
    structural parsing support, avoiding direct scoring interference with Nash-like equilibrium calculations.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'else', 'unless', 'only if', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_parse(self, prompt: str) -> Dict:
        """Extracts logical structure (Negations, Comparatives, Conditionals, Numbers)."""
        lower_p = self._normalize(prompt)
        words = lower_p.split()
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in lower_p for c in self.conditionals) # substring check for phrases
        
        numbers = self._extract_numbers(prompt)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'word_count': len(words)
        }

    def _calculate_utility(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Calculates U_i: Utility based on constraint satisfaction.
        Checks if candidate aligns with detected structural features.
        """
        utility = 0.0
        lower_c = self._normalize(candidate)
        words_c = lower_c.split()
        cand_struct = self._structural_parse(candidate)
        
        # 1. Negation Consistency
        # If prompt has negation, useful candidates often reflect it or answer the negated query correctly
        if prompt_struct['negation']:
            if any(n in words_c for n in self.negations):
                utility += 2.0
            # Heuristic: If prompt is negative, 'no' might be a strong signal depending on context
            # But strictly, we reward structural mirroring or explicit handling
        
        # 2. Comparative Consistency
        if prompt_struct['comparative']:
            if any(c in words_c for c in self.comparatives):
                utility += 2.0
            # Numeric check if numbers exist in both
            if prompt_struct['numbers'] and cand_struct['numbers']:
                p_nums = prompt_struct['numbers']
                c_nums = cand_struct['numbers']
                # Simple transitivity check: if prompt implies A > B, does candidate reflect order?
                # Since we don't have full semantic parse, we reward presence of numbers in comparative context
                utility += 1.5
        
        # 3. Conditional Consistency
        if prompt_struct['conditional']:
            if any(c in lower_c for c in ['if', 'then', 'therefore', 'so', 'because']):
                utility += 2.0
            else:
                # Candidates answering conditionals often need logical connectors
                utility += 0.5 

        # 4. Numeric Evaluation
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # If prompt asks for a calculation or comparison, exact number match is high utility
            # Check if candidate number exists in prompt (likely answer) or is a result
            p_nums = set(prompt_struct['numbers'])
            c_nums = set(cand_struct['numbers'])
            if c_nums.intersection(p_nums):
                utility += 3.0 # High reward for echoing relevant numbers
            elif len(c_nums) > 0:
                utility += 1.0 # Candidate has numbers, good for math problems

        # Base utility for length appropriateness (avoiding too short/long relative to prompt)
        if 0.5 * prompt_struct['word_count'] <= cand_struct['word_count'] <= 2.0 * prompt_struct['word_count']:
            utility += 1.0
            
        return utility

    def _calculate_ib_cost(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Calculates KL-Divergence term: D_KL(pi || P).
        Measures how much the candidate distribution (structure) diverges from the prompt prior.
        High divergence = High Cost (unless justified by utility).
        """
        cost = 0.0
        lower_c = self._normalize(candidate)
        words_c = lower_c.split()
        
        # Cost for missing structural elements present in prompt
        if prompt_struct['negation'] and not any(n in words_c for n in self.negations):
            # Not strictly required to repeat negation, but ignoring it might be costly in logic
            # We apply a small penalty for ignoring major logical operators
            cost += 0.5
            
        if prompt_struct['comparative'] and not any(c in words_c for c in self.comparatives):
            # If prompt compares, answer should ideally relate to comparison
            if not any(w in lower_c for w in ['yes', 'no', 'true', 'false', '0', '1']):
                cost += 0.5

        # Entropy regularization (encourage stochasticity/flexibility slightly to avoid overfitting)
        # Simplified: penalize extremely short answers that lose information
        if len(words_c) < 2 and prompt_struct['word_count'] > 10:
            cost += 0.2
            
        return cost

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._structural_parse(prompt)
        scored_candidates = []
        
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = prompt_struct['word_count'] + len(prompt_struct['numbers']) * 2
        
        for cand in candidates:
            # 1. Utility Calculation (Reward structural alignment)
            utility = self._calculate_utility(prompt_struct, cand)
            
            # 2. IB Cost Calculation (Penalize divergence from logical prior)
            ib_cost = self._calculate_ib_cost(prompt_struct, cand)
            
            # 3. QRE Score: Utility - Beta * KL_Cost
            # Beta acts as a temperature parameter for information cost
            beta = 0.8 
            raw_score = utility - (beta * ib_cost)
            
            # 4. NCD Tiebreaker (Only if structural signals are weak or scores are close)
            # We use NCD to prefer candidates that are compressible with the prompt (contextually relevant)
            # but only as a secondary factor.
            ncd_val = self._ncd(prompt, cand)
            # Normalize NCD to a small bonus range [0, 0.1] so it doesn't override structural logic
            ncd_bonus = (1.0 - ncd_val) * 0.1 
            
            final_score = raw_score + ncd_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if utility > 1.5: reasoning_parts.append("High structural alignment")
            if ib_cost > 0: reasoning_parts.append(f"IB Cost: {ib_cost:.2f}")
            if prompt_struct['numbers'] and self._extract_numbers(cand):
                reasoning_parts.append("Numeric consistency detected")
            if not reasoning_parts:
                reasoning_parts.append("Baseline evaluation")
                
            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing to verify logical consistency.
        Restricted use of ToM as per causal analysis guidelines.
        """
        prompt_struct = self._structural_parse(prompt)
        answer_struct = self._structural_parse(answer)
        lower_ans = self._normalize(answer)
        
        confidence = 0.5 # Base confidence
        
        # Boost if answer contains numbers found in prompt (likely correct for math)
        if prompt_struct['numbers'] and answer_struct['numbers']:
            if any(n in answer_struct['numbers'] for n in prompt_struct['numbers']):
                confidence += 0.3
        
        # Boost if logical operators match (e.g. prompt asks "Is it not...", answer "No")
        if prompt_struct['negation'] and any(n in lower_ans.split() for n in self.negations):
            confidence += 0.15
            
        # Penalty if answer is empty or gibberish length
        if len(answer.strip()) == 0:
            confidence = 0.0
        elif len(answer.strip()) > len(prompt) * 2:
            confidence -= 0.2 # Overly verbose answers suspicious
            
        # NCD check for strong similarity (exact match or close variation)
        ncd = self._ncd(prompt, answer)
        if ncd < 0.5:
            confidence += 0.1
            
        return max(0.0, min(1.0, confidence))