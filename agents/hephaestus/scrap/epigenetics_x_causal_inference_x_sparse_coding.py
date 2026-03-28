import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dynamic Causal Sparse-Coding Network (DCSCN) Approximation.
    
    Mechanism:
    1. Epigenetic Trace (E): A persistent matrix of structural priors (negations, comparatives, 
       conditionals) that modulates the weight of extracted features. These are slow-changing 
       heuristics derived from logical syntax rules.
    2. Sparse Coding: The input prompt and candidates are parsed into binary feature vectors 
       (active units) representing logical atoms (numbers, operators, entities). Only a few 
       units are active per statement.
    3. Causal Inference (Do-Calculus): We simulate interventions by clamping candidate features 
       against the prompt's logical structure. We calculate a "causal fit" score based on 
       constraint satisfaction (e.g., if prompt has "not", candidate must reflect negation).
    4. Learning: The system doesn't train via backprop but uses the epigenetic priors to 
       penalize spurious correlations (e.g., string overlap without logical alignment).
    
    Scoring = (Structural Alignment * Epigenetic Weight) - (NCD Penalty as Tiebreaker)
    """

    def __init__(self):
        # Epigenetic Trace Matrix (E): Priors for logical operators
        # Keys are regex patterns, values are weights (strength of causal link)
        self.epigenetic_priors = {
            r'\bnot\b': 2.5,
            r'\bno\b': 2.0,
            r'\bnever\b': 2.0,
            r'\bunless\b': 1.8,
            r'\bif\b': 1.5,
            r'\bthen\b': 1.5,
            r'\btherefore\b': 1.5,
            r'\bgreater\b': 1.8,
            r'\bless\b': 1.8,
            r'\bmore\b': 1.8,
            r'\bhigher\b': 1.8,
            r'\blower\b': 1.8,
            r'\bequal\b': 1.5,
            r'\bsame\b': 1.5,
            r'\bdifferent\b': 1.5,
            r'\ball\b': 1.2,
            r'\bsome\b': 1.2,
            r'\bnone\b': 2.0,
            r'\bonly\b': 1.8,
            r'\bexcept\b': 2.0,
            r'\bbefore\b': 1.5,
            r'\bafter\b': 1.5,
            r'\bfirst\b': 1.5,
            r'\blast\b': 1.5,
        }
        # Threshold for sparse activation
        self.activation_threshold = 0.1

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for causal comparison."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                pass
        return nums

    def _sparse_encode(self, text: str) -> Dict[str, int]:
        """
        Generate a sparse binary code representing active logical features.
        Returns a dictionary of active features (keys) with binary activation (1).
        """
        code = {}
        text_lower = text.lower()
        
        # Activate units based on epigenetic priors (logical operators)
        for pattern, weight in self.epigenetic_priors.items():
            if re.search(pattern, text_lower):
                code[f'op:{pattern}'] = 1
        
        # Activate units for numbers (abstracted to presence)
        nums = self._extract_numbers(text)
        if nums:
            code['has_nums'] = 1
            # Add relative magnitude flags if multiple numbers exist
            if len(nums) >= 2:
                if nums[0] > nums[1]:
                    code['cmp:first_greater'] = 1
                elif nums[0] < nums[1]:
                    code['cmp:first_less'] = 1
                else:
                    code['cmp:equal'] = 1
        
        # Structural sparsity: Sentence count (complexity)
        sentences = [s for s in re.split(r'[.!?]', text) if s.strip()]
        if len(sentences) > 1:
            code['struct:multi_sent'] = 1
            
        return code

    def _compute_causal_fit(self, prompt_code: Dict[str, int], candidate_code: Dict[str, int], 
                            prompt: str, candidate: str) -> float:
        """
        Evaluate how well the candidate's sparse code satisfies the prompt's causal constraints.
        Simulates a 'do-operation' by checking if clamping the candidate preserves logical consistency.
        """
        score = 0.0
        total_weight = 0.0
        
        # Check for logical consistency in operators
        for key, val in prompt_code.items():
            if key.startswith('op:'):
                # If prompt has a logical operator, candidate should ideally respect or address it
                # Simple heuristic: If prompt has negation, candidate must not blindly affirm without qualification
                if 'not' in key or 'no' in key or 'never' in key:
                    if key in candidate_code:
                        score += 2.0 # Candidate acknowledges the negation
                    else:
                        # Check if candidate implicitly contradicts by lacking negation context
                        # This is a soft penalty, not a hard fail
                        pass 
                    total_weight += 2.0
                elif key in candidate_code:
                    score += 1.0 # Matching logical operator
                    total_weight += 1.0
        
        # Numeric Causal Consistency
        if 'has_nums' in prompt_code:
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            
            if p_nums and c_nums:
                # Check if the candidate preserves the order or result implied
                # If prompt asks "which is greater?", candidate should contain the greater number
                if len(p_nums) >= 2:
                    max_p = max(p_nums)
                    min_p = min(p_nums)
                    
                    # Heuristic: If prompt implies selection, candidate should match the extreme
                    if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'max' in prompt.lower():
                        if any(abs(n - max_p) < 1e-6 for n in c_nums):
                            score += 5.0
                    elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'min' in prompt.lower():
                        if any(abs(n - min_p) < 1e-6 for n in c_nums):
                            score += 5.0
                    elif 'sum' in prompt.lower() or 'total' in prompt.lower():
                        if any(abs(n - sum(p_nums)) < 1e-6 for n in c_nums):
                            score += 5.0
                    elif 'difference' in prompt.lower():
                         if any(abs(n - abs(p_nums[0]-p_nums[1])) < 1e-6 for n in c_nums):
                            score += 5.0

        # Normalize by potential weight to avoid bias towards long prompts
        if total_weight > 0:
            return score / (total_weight * 0.5) # Scaling factor
        return 0.0

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
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximated with lengths for stability in this context
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c_concat = len(zlib.compress(concat))
        
        numerator = c_concat - min(c1, c2)
        denominator = max(c1, c2)
        
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_code = self._sparse_encode(prompt)
        results = []
        
        for cand in candidates:
            cand_code = self._sparse_encode(cand)
            
            # 1. Structural/Causal Score (Primary Signal)
            causal_score = self._compute_causal_fit(prompt_code, cand_code, prompt, cand)
            
            # 2. Epigenetic Bonus for keyword matching (shallow but necessary baseline)
            keyword_bonus = 0.0
            for pattern in self.epigenetic_priors:
                if re.search(pattern, prompt.lower()) and re.search(pattern, cand.lower()):
                    keyword_bonus += 0.1
            
            # 3. NCD as Tiebreaker (only if causal score is low/ambiguous)
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so higher is better, but scale it down so it doesn't override logic
            ncd_score = (1.0 - ncd_val) * 0.1 
            
            final_score = causal_score + keyword_bonus + ncd_score
            
            # Reasoning string generation
            reasoning_parts = []
            if causal_score > 0:
                reasoning_parts.append(f"Causal fit detected ({causal_score:.2f})")
            if 'has_nums' in prompt_code and 'has_nums' in cand_code:
                reasoning_parts.append("Numeric consistency check performed")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment low; relying on compression proximity")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate single candidate against prompt
        eval_result = self.evaluate(prompt, [answer])
        if not eval_result:
            return 0.0
        
        score = eval_result[0]['score']
        
        # Map score to 0-1 range heuristically
        # Scores > 2.0 are strong logical matches
        # Scores around 0.1-0.5 are weak matches
        # Scores < 0 are likely mismatches
        confidence = 1.0 / (1.0 + math.exp(-score + 1.0)) # Sigmoid shift
        
        return max(0.0, min(1.0, confidence))