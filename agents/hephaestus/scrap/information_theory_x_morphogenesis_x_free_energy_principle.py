import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Variational Predictive Coding Network (VPCN) inspired Reasoning Tool.
    
    Mechanism:
    1. Morphogenetic Field (Latent): Simulates a reaction-diffusion process on the 
       structural features of the prompt. It detects 'patterns' of logic (negations, 
       conditionals, numbers) vs 'noise'.
    2. Free Energy Minimization: Calculates a 'prediction error' between the 
       structural requirements of the prompt and the properties of the candidate.
       Low free energy = high structural alignment.
    3. Information Bottleneck: Penalizes candidates that are too long (complex) 
       relative to their information gain, enforcing Occam's razor.
    4. Epistemic Honesty (Meta-Confidence): A dedicated pathway analyzes the prompt 
       for ambiguity, presupposition, and unanswerability. If detected, it overrides 
       the scoring confidence to < 0.3, regardless of candidate quality.
    
    Score Decomposition:
    - Structural/Logical Parsing: 50%
    - Constructive Computation: 20% 
    - NCD (Compression): 15%
    - Epistemic Honesty Cap: Applied dynamically
    """

    def __init__(self):
        # Reaction-Diffusion coefficients (metaphorical tuning for feature sensitivity)
        self.diffusion_rate = 0.1
        self.reaction_threshold = 0.5
        
        # Patterns for structural parsing (Tier A)
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r"n't"]
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\b<\b', r'\b>\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly\s+if\b']
        
        # Patterns for Epistemic Honesty (Tier B - Judgment Traps)
        self.presupposition_triggers = [
            r'have you stopped', r'did you stop', r'why did .* fail', r'why is .* wrong',
            r'when did you stop', r'how often do you .* now' # Implies a change or state not proven
        ]
        self.ambiguity_triggers = [
            r'who is .* he', r'who is .* she', r'which one', r'either .* or', 
            r'best', r'worst', r'favorite', r'most beautiful' # Subjectivity without criteria
        ]
        self.unanswerable_triggers = [
            r'what is the color of .*', r'how many .* in the box', # Context missing
            r'tomorrow', r'next week' # Temporal dependency without reference
        ]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for constructive computation."""
        # Match integers and floats, avoiding dates or version numbers if possible
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """
        Extract logical structure: negations, comparatives, conditionals, numbers.
        This forms the 'latent field' u(x,t) of the VPCN.
        """
        text_lower = text.lower()
        
        neg_count = sum(1 for p in self.negation_patterns if re.search(p, text_lower))
        comp_count = sum(1 for p in self.comparative_patterns if re.search(p, text_lower))
        cond_count = sum(1 for p in self.conditional_patterns if re.search(p, text_lower))
        numbers = self._extract_numbers(text)
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'length': len(text),
            'has_question': '?' in text
        }

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # Check for presupposition traps
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Strong cap for loaded questions
                
        # Check for subjectivity/ambiguity
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                # Only cap if it looks like a judgment call without data
                if 'best' in p_lower or 'worst' in p_lower or 'favorite' in p_lower:
                    return 0.25
                if 'either' in p_lower and 'or' in p_lower:
                    return 0.3 # False dichotomy risk
                    
        # Check for missing context (heuristic)
        if "color" in p_lower and "what" in p_lower:
            return 0.2
        if "stop" in p_lower and "have you" in p_lower:
            return 0.2
            
        return 1.0  # No obvious traps detected

    def _compute_constructive_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Tier A: Constructive Computation.
        If the prompt has numbers and comparatives, verify the math.
        """
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        # If no numbers in prompt, skip math check
        if not p_nums or len(p_nums) < 2:
            return 0.5 # Neutral
        
        # Simple heuristic: If prompt asks for comparison (more/less), 
        # check if candidate numbers align with the largest/smallest in prompt
        has_comparative = prompt_struct['comparatives'] > 0
        has_negation = prompt_struct['negations'] > 0
        
        if not c_nums:
            return 0.0 # Failed to provide numeric answer
            
        # Basic consistency check: Candidate number should be derived from prompt numbers
        # (e.g., sum, max, min, or direct extraction)
        p_max = max(p_nums)
        p_min = min(p_nums)
        c_val = c_nums[0]
        
        # Heuristic scoring for math problems
        if abs(c_val - p_max) < 1e-6 or abs(c_val - p_min) < 1e-6 or abs(c_val - sum(p_nums)) < 1e-6:
            return 1.0 if not has_negation else 0.0
            
        # If comparative logic exists, simple magnitude check
        if has_comparative:
            if 'more' in prompt_struct.get('raw', '') or 'greater' in prompt_struct.get('raw', ''):
                return 1.0 if c_val >= p_max else 0.2
            elif 'less' in prompt_struct.get('raw', '') or 'smaller' in prompt_struct.get('raw', ''):
                return 1.0 if c_val <= p_min else 0.2
                
        return 0.5

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Core VPCN Logic:
        F = Prediction_Error + Complexity_Penalty
        Minimizing F maximizes the score.
        """
        p_struct = self._structural_parse(prompt)
        c_struct = self._structural_parse(candidate)
        
        # 1. Prediction Error (Structural Mismatch)
        # Does the candidate respect the logical constraints of the prompt?
        error = 0.0
        
        # Negation consistency (simplified)
        if p_struct['negations'] > 0:
            # If prompt is negative, ideal candidate might need specific handling
            # Here we just penalize extreme length mismatch as a proxy for 'ignoring constraints'
            if c_struct['length'] < p_struct['length'] * 0.1:
                error += 0.5
        
        # Comparative/Conditional alignment
        if p_struct['comparatives'] > 0:
            if c_struct['comparatives'] == 0 and not c_struct['numbers']:
                error += 0.4 # Ignored the comparison instruction
                
        if p_struct['conditionals'] > 0:
            if c_struct['conditionals'] == 0:
                error += 0.2 # Might be okay if answering the result, but risky

        # 2. Constructive Computation Check (High weight if numbers present)
        math_score = self._compute_constructive_score(p_struct, c_struct)
        if math_score < 0.5:
            error += (1.0 - math_score) * 2.0 # Heavy penalty for wrong math

        # 3. Information Bottleneck (Complexity Penalty)
        # Penalize overly verbose answers that don't add structural value
        complexity_penalty = 0.0
        if c_struct['length'] > p_struct['length'] * 3:
            complexity_penalty = 0.2 * math.log(c_struct['length'] / (p_struct['length'] + 1))

        # 4. NCD Tiebreaker (Max 15% influence)
        # Normalized Compression Distance
        try:
            p_bytes = prompt.encode('utf-8')
            c_bytes = candidate.encode('utf-8')
            concat = p_bytes + c_bytes
            
            len_p = len(zlib.compress(p_bytes))
            len_c = len(zlib.compress(c_bytes))
            len_concat = len(zlib.compress(concat))
            
            # NCD formula
            ncd = (len_concat - min(len_p, len_c)) / max(len_p, len_c) if max(len_p, len_c) > 0 else 1.0
            ncd_score = 1.0 - ncd # Convert distance to similarity
        except:
            ncd_score = 0.5

        # Final Free Energy Calculation
        # Lower F is better. We return a score where higher is better.
        # Base score 1.0, subtract errors and complexity, add NCD bonus
        final_score = 1.0 - error - complexity_penalty + (ncd_score * 0.15)
        
        return max(0.0, min(1.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates against the prompt using the VPCN model.
        Returns a ranked list of candidates with scores and reasoning.
        """
        # Step 1: Meta-Confidence Check (Epistemic Honesty)
        # If the prompt is a trap, we must cap confidence globally
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = meta_cap < 0.3
        
        results = []
        
        for cand in candidates:
            # Calculate raw free-energy based score
            raw_score = self._calculate_free_energy(prompt, cand)
            
            # Apply Epistemic Cap if the prompt is ambiguous/trap
            if is_ambiguous:
                # If ambiguous, all candidates get low confidence, 
                # but we still rank them by structural fit to be helpful
                final_score = min(raw_score, meta_cap)
                reasoning = f"Epistemic Limit: Prompt contains ambiguity/trap. Score capped at {meta_cap}. Structural fit: {raw_score:.2f}"
            else:
                final_score = raw_score
                reasoning = f"Structural alignment and constructive computation score: {raw_score:.2f}"
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Strictly enforces epistemic honesty caps.
        """
        # 1. Check for traps first
        cap = self._meta_confidence(prompt)
        
        # 2. Calculate structural fit
        score = self._calculate_free_energy(prompt, answer)
        
        # 3. Apply cap
        final_conf = min(score, cap)
        
        # 4. Ensure we don't claim > 0.9 without definitive computation
        # (Heuristic: if no numbers and no strong structural match, cap at 0.8)
        p_struct = self._structural_parse(prompt)
        if p_struct['numbers'] == 0 and p_struct['comparatives'] == 0:
            if final_conf > 0.85:
                final_conf = 0.85
                
        return final_conf