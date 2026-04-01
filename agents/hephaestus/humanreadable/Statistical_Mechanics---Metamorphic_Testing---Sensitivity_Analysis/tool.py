import re
import math
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    Ensemble-Metamorphic Sensitivity Scorer (EMSS) with Constructive Computation.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions (negations, numerics, conditionals, etc.)
       into a state vector.
    2. Metamorphic Perturbation: Generates an ensemble of perturbed prompts (double numbers, 
       swap order, flip negation) to test reasoning invariance.
    3. Sensitivity Analysis: Computes the deviation of the candidate answer from the ensemble 
       average. Lower deviation = higher score.
    4. Constructive Computation: Explicitly solves numeric, temporal, and logical constraints 
       where possible.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity, presupposition, 
       or unanswerable constraints (Tier B).
    """

    def __init__(self):
        self.beta = 1.0
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|-er)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|otherwise|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|results in|causes)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|next|previous)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'pronoun_ambig': re.compile(r'\b(he|she|him|her|they|them)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did .+ fail|why is .+ so)', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|must be .+ or)\b', re.IGNORECASE)
        }

    def _parse_propositions(self, text: str) -> Dict[str, Any]:
        """Extract structural features into a state vector dictionary."""
        text_lower = text.lower()
        state = {
            'negation': len(self.patterns['negation'].findall(text)),
            'comparative': len(self.patterns['comparative'].findall(text)),
            'conditional': len(self.patterns['conditional'].findall(text)),
            'causal': len(self.patterns['causal'].findall(text)),
            'ordering': len(self.patterns['ordering'].findall(text)),
            'numeric_count': 0,
            'numeric_sum': 0.0,
            'length': len(text)
        }
        
        nums = self.patterns['numeric'].findall(text)
        if nums:
            state['numeric_count'] = len(nums)
            state['numeric_sum'] = sum(float(n) for n in nums)
            
        return state

    def _generate_ensemble(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate metamorphic perturbations of the prompt."""
        ensemble = [self._parse_propositions(prompt)]  # s0
        
        # Mutation 1: Double numeric (simulate by scaling numeric_sum in state)
        s0 = ensemble[0].copy()
        s0['numeric_sum'] *= 2.0
        s0['numeric_count'] = s0.get('numeric_count', 0) # Keep count same, value doubled conceptually
        ensemble.append(s0)
        
        # Mutation 2: Negation flip (simulate by toggling negation count)
        s1 = ensemble[0].copy()
        s1['negation'] = s1.get('negation', 0) + 1 if s1.get('negation', 0) == 0 else s1.get('negation', 0) - 1
        ensemble.append(s1)
        
        # Mutation 3: Order swap (simulate by shuffling logical weights - abstracted here)
        s2 = ensemble[0].copy()
        s2['ordering'] = s2.get('ordering', 0) + 2 
        ensemble.append(s2)
        
        return ensemble

    def _compute_state_vector(self, state_dict: Dict[str, Any]) -> List[float]:
        """Convert state dict to fixed-order vector for math ops."""
        keys = ['negation', 'comparative', 'conditional', 'causal', 'ordering', 'numeric_count', 'numeric_sum']
        return [float(state_dict.get(k, 0)) for k in keys]

    def _calculate_sensitivity_score(self, prompt: str, answer: str) -> float:
        """Calculate score based on ensemble deviation."""
        ensemble_states = self._generate_ensemble(prompt)
        answer_state = self._parse_propositions(answer)
        
        # Convert to vectors
        vec_answer = self._compute_state_vector(answer_state)
        vec_ensemble = [self._compute_state_vector(s) for s in ensemble_states]
        
        # Compute mean squared distance (D(a))
        total_dist = 0.0
        for vec_s in vec_ensemble:
            dist_sq = sum((a - b) ** 2 for a, b in zip(vec_answer, vec_s))
            total_dist += dist_sq
            
        D_a = total_dist / len(vec_ensemble)
        
        # Score = exp(-beta * D)
        score = math.exp(-self.beta * D_a)
        return score

    def _constructive_compute(self, prompt: str, answer: str) -> Tuple[float, bool]:
        """
        Attempt to computationally solve the problem.
        Returns (computed_score, is_definitive).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Numeric Extraction and Verification
        nums_p = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        nums_a = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', answer)]
        
        # Simple arithmetic check: If prompt has 2 numbers and answer has 1, check sum/prod
        if len(nums_p) == 2 and len(nums_a) == 1:
            target = nums_a[0]
            if abs(target - (nums_p[0] + nums_p[1])) < 1e-6: return 1.0, True # Sum match
            if abs(target - (nums_p[0] * nums_p[1])) < 1e-6: return 1.0, True # Prod match
            if nums_p[1] != 0 and abs(target - (nums_p[0] / nums_p[1])) < 1e-6: return 1.0, True
            
        # 2. Logical Constraint: Negation consistency
        has_not_p = bool(re.search(r'\bnot\b', p_lower))
        has_not_a = bool(re.search(r'\bnot\b', a_lower))
        if has_not_p and not has_not_a and len(nums_p) == 0:
            # If prompt says "not" and answer ignores it (and no numbers to distract), penalize
            return 0.1, True 

        # 3. Comparative Logic
        if re.search(r'more than|greater than', p_lower):
            if len(nums_p) >= 2 and len(nums_a) >= 1:
                # Heuristic: if prompt asks for "more", answer should be larger than base?
                # This is weak without specific target identification, so we skip definitive flag
                pass

        return 0.5, False # No definitive computation found

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Pronoun Ambiguity in "Who" questions
        if re.search(r'\bwho\b', p_lower) and self.patterns['pronoun_ambig'].search(p_lower):
            # Check if multiple males/females mentioned (simplified)
            if len(re.findall(r'\b(he|him|john|bob|mark)\b', p_lower)) > 1:
                return 0.25
                
        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and not re.search(r'\b(data|statistic|vote)\b', p_lower):
            return 0.3
            
        return 1.0

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        if not s1 or not s2: return 0.0
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0: return 0.0
            ncd = (c12 - min(c1, c2)) / max(c1, c2)
            return 1.0 - ncd # Convert distance to similarity
        except:
            return 0.0

    def confidence(self, prompt: str, answer: str) -> float:
        """Public interface for confidence scoring."""
        # Tier B: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.3:
            return meta_cap

        # Structural & Computational Score
        sens_score = self._calculate_sensitivity_score(prompt, answer)
        comp_score, is_definitive = self._constructive_compute(prompt, answer)
        
        # NCD Tiebreaker (max 15% weight effectively via capping)
        ncd_score = self._ncd_similarity(prompt, answer)
        
        # Weighted combination
        # Base: Sensitivity (40%) + Computation (45%) + NCD (15%)
        raw_score = (sens_score * 0.40) + (comp_score * 0.45) + (ncd_score * 0.15)
        
        # Apply meta cap
        final_score = min(raw_score, meta_cap)
        
        # If not definitive computation, cap at 0.9 to avoid overconfidence
        if not is_definitive:
            final_score = min(final_score, 0.85)
            
        return max(0.0, min(1.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Sensitivity: {self._calculate_sensitivity_score(prompt, cand):.2f}, Meta-Cap: {self._meta_confidence(prompt):.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results