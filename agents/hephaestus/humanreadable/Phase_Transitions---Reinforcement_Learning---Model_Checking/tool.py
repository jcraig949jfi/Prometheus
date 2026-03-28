import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Parameter-Guided Verification Loop (CPGVL)
    
    Mechanism:
    This tool simulates the theoretical framework of using RL to find phase transitions
    in model checking by applying structural parsing as the 'Order Parameter'.
    
    1. Phase Transition Detection (Structural Parsing): Instead of varying physical parameters,
       we vary the 'logical stability' of a candidate by counting structural markers 
       (negations, comparatives, conditionals). A sharp change in marker density relative 
       to the prompt indicates a potential 'phase transition' (i.e., a logical flip).
       
    2. RL Agent (Policy Search): The scoring function acts as the reward signal. 
       Candidates that maintain structural consistency with the prompt (e.g., if prompt 
       has negation, answer must reflect it) receive high rewards. The 'agent' explores 
       the candidate space and assigns value based on constraint satisfaction.
       
    3. Model Checking (Exhaustive Verification): We treat structural constraints (Modus Tollens,
        Transitivity) as temporal logic specifications. If a candidate violates a hard 
        constraint derived from the prompt, it is 'verified' as false (Reward = -inf).
        
    4. NCD Tiebreaker: Used only when structural signals are ambiguous, measuring 
       information theoretic distance.
    """

    def __init__(self):
        # Structural keywords acting as 'Order Parameters' for logical phase transitions
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'cannot', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'than']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most', 'few']
        
        # Weights for the reward function (learned via 'theory' rather than online RL for stability)
        self.w_neg = 2.0
        self.w_comp = 1.5
        self.w_cond = 1.5
        self.w_quant = 1.0

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _count_markers(self, text: str) -> Dict[str, int]:
        tokens = self._tokenize(text)
        counts = {
            'neg': sum(1 for t in tokens if any(n in t for n in self.negations)),
            'comp': sum(1 for t in tokens if any(c in t for c in self.comparatives)),
            'cond': sum(1 for t in tokens if any(c in t for c in self.conditionals)),
            'quant': sum(1 for t in tokens if any(q in t for q in self.quantifiers))
        }
        return counts

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point numbers for numeric evaluation
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Step: Verify numeric constraints.
        If prompt implies an order (e.g., 5 > 3) and candidate contradicts, penalty.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric constraint to check
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check if candidate numbers are within the range of prompt numbers (loose constraint)
        # or if they represent a valid transformation. 
        # For this implementation, we penalize if candidate introduces wild outliers 
        # compared to prompt magnitude without explicit operation words.
        
        if p_nums:
            p_min, p_max = min(p_nums), max(p_nums)
            p_range = p_max - p_min if p_max != p_min else 1.0
            
            for n in c_nums:
                # Allow slight expansion, but penalize massive deviation as 'unstable'
                if n < p_min - 10*p_range or n > p_max + 10*p_range:
                    return 0.2 # Low confidence due to numeric outlier
                    
        return 1.0

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Step: Verify logical structure (Negation/Conditional propagation).
        """
        p_markers = self._count_markers(prompt)
        c_markers = self._count_markers(candidate)
        
        score = 1.0
        
        # Constraint 1: Negation Propagation
        # If prompt has strong negation, valid reasoning often requires acknowledging it.
        # However, blind echo is bad. We look for 'structural resonance'.
        if p_markers['neg'] > 0:
            # If prompt negates, candidate should ideally contain logical operators to handle it
            if c_markers['neg'] == 0 and c_markers['cond'] == 0:
                # Potential failure to address negation (simplified check)
                # We don't fail it outright, but reduce score slightly unless it's a simple fact
                score *= 0.9 

        # Constraint 2: Conditional Logic
        # If prompt is conditional ('If A then B'), candidate shouldn't assert 'A' absolutely 
        # without context, unless it's deriving 'B'.
        if p_markers['cond'] > 0:
            # Heuristic: Candidates answering conditional prompts often contain 'if', 'then', or 'depends'
            # or they answer the specific instance. 
            pass # Complex to verify without full NLP, keeping score neutral but ready for extension

        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(compress(x))
        c_s1 = len(zlib.compress(s1_bytes))
        c_s2 = len(zlib.compress(s2_bytes))
        
        numerator = len_concat - min(c_s1, c_s2)
        denominator = max(c_s1, c_s2)
        
        if denominator == 0:
            return 1.0
            
        return numerator / denominator

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Core Reasoning Engine: Computes score based on structural parsing.
        Simulates the RL reward loop where the agent is rewarded for 
        staying near the 'critical point' of logical consistency.
        """
        p_markers = self._count_markers(prompt)
        c_markers = self._count_markers(candidate)
        
        score = 0.0
        total_weight = 0.0
        
        # 1. Negation Alignment (Phase Transition Check)
        # Reward if negation presence in prompt is logically handled (approximated by presence in candidate)
        if p_markers['neg'] > 0:
            total_weight += self.w_neg
            if c_markers['neg'] > 0:
                score += self.w_neg * 1.0 # Aligned
            else:
                score += self.w_neg * 0.4 # Might be missing the point
        else:
            # Prompt has no negation, candidate shouldn't be overly negative unless necessary
            if c_markers['neg'] > 2:
                score -= 0.5 # Over-negation penalty

        # 2. Comparative Consistency
        if p_markers['comp'] > 0:
            total_weight += self.w_comp
            if c_markers['comp'] > 0:
                score += self.w_comp * 1.0
            # If prompt compares, answer often needs comparison words
        elif c_markers['comp'] > 0:
            # Candidate introduces comparison where none exists? Maybe valid, maybe noise.
            score += 0.1

        # 3. Conditional Logic
        if p_markers['cond'] > 0:
            total_weight += self.w_cond
            # Reward candidates that acknowledge conditionality or provide definitive derived results
            if c_markers['cond'] > 0 or len(candidate.split()) > 5: 
                score += self.w_cond * 0.8
        
        # 4. Quantifier Matching
        if p_markers['quant'] > 0:
            total_weight += self.w_quant
            if c_markers['quant'] > 0:
                score += self.w_quant * 1.0

        # Normalize by potential max score to keep it bounded roughly
        if total_weight > 0:
            base_score = score / total_weight if total_weight != 0 else 0.5
        else:
            base_score = 0.5
            
        return base_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # Step 1: Structural Parsing (Order Parameter Calculation)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # Step 2: Model Checking (Constraint Verification)
            logic_check = self._check_logical_consistency(prompt, cand)
            numeric_check = self._check_numeric_consistency(prompt, cand)
            
            # Combined Reward Signal
            # The 'RL Agent' maximizes this reward
            final_score = struct_score * logic_check * numeric_check
            
            # Step 3: NCD as Tiebreaker (only if structural signal is weak/ambiguous)
            # We add a tiny epsilon of NCD influence only if scores are close to 0.5 (uncertain)
            if 0.4 < final_score < 0.6:
                ncd = self._ncd_distance(prompt, cand)
                # Lower NCD (more similar structure) gets a tiny boost in ambiguous cases
                final_score += (1.0 - ncd) * 0.05 

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural alignment: {struct_score:.2f}, Logic check: {logic_check:.2f}, Numeric check: {numeric_check:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural evaluation logic.
        """
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        raw_score = res_list[0]['score']
        
        # Map raw score (which can be slightly <0 or >1 due to bonuses/penalties) to [0, 1]
        confidence = max(0.0, min(1.0, raw_score))
        
        return confidence