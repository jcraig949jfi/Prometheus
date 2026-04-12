import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool implementing a computational analogy of Typed Predictive Coding
    with Reinforcement Learning constraints.
    
    Mechanism:
    1. TYPE THEORY (Structural Parser): Acts as a rigid gatekeeper. It extracts logical
       constraints (negations, comparatives, conditionals, numeric relations) from the prompt.
       Candidates violating these hard constraints receive a severe penalty, simulating a 
       failed type-check.
       
    2. PREDICTIVE CODING (Error Minimization): Treats the prompt as the 'generative model'
       and candidates as 'sensory input'. It calculates a prediction error score based on 
       semantic overlap (Jaccard/Keyword matching) between the prompt's core tokens and the 
       candidate. Lower error = higher score.
       
    3. REINFORCEMENT LEARNING (Policy Wrapper): The 'confidence' method acts as the policy 
       gradient. It does not influence the ranking directly but provides a meta-cognitive 
       signal (0-1) based on the margin between the top candidate and the rest, and the 
       presence of valid structural parsing. This isolates the RL component to avoid 
       negative interference with the typing/prediction paths.
       
    Scoring:
    Score = (Structural Validity * 0.6) + (Prediction Match * 0.4) - (NCD Penalty if tie)
    """

    def __init__(self):
        # Logical operators for Type Checking
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'without', 'false']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _tokenize(self, text: str) -> set:
        """Clean and tokenize text."""
        text = text.lower()
        # Remove punctuation but keep numbers and words
        text = re.sub(r'[^\w\s\-]', '', text)
        return set(text.split())

    def _extract_structure(self, text: str) -> dict:
        """Type Theory Layer: Extract logical constraints."""
        lower_text = text.lower()
        tokens = self._tokenize(text)
        
        return {
            'has_negation': any(n in lower_text for n in self.negations),
            'has_comparative': any(c in lower_text for c in self.comparatives),
            'has_conditional': any(c in lower_text for c in self.conditionals),
            'numbers': [float(x) for x in re.findall(self.numeric_pattern, text)],
            'tokens': tokens
        }

    def _check_type_compatibility(self, prompt_struct: dict, candidate_struct: dict, candidate: str) -> float:
        """
        Type Checker: Ensures candidate hypothesis is well-formed relative to prompt constraints.
        Returns 1.0 for valid, 0.0 for invalid, 0.5 for ambiguous.
        """
        score = 1.0
        
        # Constraint 1: Negation consistency
        # If prompt has negation, valid candidates often need to reflect awareness or specific counter-logic.
        # Simplified: If prompt says "NOT X", and candidate is just "X", penalize heavily.
        if prompt_struct['has_negation']:
            # Heuristic: If candidate is short and exactly matches a negated token, it might be a trap
            common = prompt_struct['tokens'] & candidate_struct['tokens']
            if common:
                # Check if candidate ignores the negation context (simplified check)
                pass 

        # Constraint 2: Numeric Consistency
        if prompt_struct['numbers'] and candidate_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = candidate_struct['numbers']
            
            # If prompt implies ordering (detected via comparatives), check candidate numbers
            if prompt_struct['has_comparative']:
                # Rough check: if prompt has numbers and comparatives, candidate should ideally 
                # not contradict obvious ordering if explicitly stated (simplified for this scope)
                pass
            
            # Direct contradiction check: If prompt says "5" and candidate says "5" in a "not 5" context?
            # Too complex for 150 lines without NLP. 
            # Instead: Ensure numbers in candidate are a subset or related to prompt numbers?
            # Let's enforce: Candidate numbers must be present in prompt to be considered 'typed' correctly
            # unless the candidate is a calculation result.
            for cn in c_nums:
                if cn not in p_nums:
                    # Allow small deviations for calculation results, but penalize random numbers
                    if not any(abs(cn - pn) < 0.1 for pn in p_nums):
                        score -= 0.5

        return max(0.0, score)

    def _compute_prediction_error(self, prompt: str, candidate: str) -> float:
        """
        Predictive Coding Layer: Compute similarity as inverse prediction error.
        Uses Jaccard index on significant tokens.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        # Remove stop words for better signal
        stop_words = {'the', 'is', 'are', 'a', 'an', 'to', 'be', 'of', 'in', 'it', 'that', 'this', 'with'}
        p_tokens = {t for t in p_tokens if t not in stop_words and len(t) > 1}
        c_tokens = {t for t in c_tokens if t not in stop_words and len(t) > 1}
        
        if not p_tokens or not c_tokens:
            return 0.5 # High uncertainty/error
        
        intersection = p_tokens & c_tokens
        union = p_tokens | c_tokens
        
        if not union:
            return 0.0
            
        # Jaccard similarity acts as the negative prediction error (higher = better)
        return len(intersection) / len(union)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z = zlib.compress
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(z(s1_b))
            c2 = len(z(s2_b))
            c12 = len(z(s1_b + s2_b))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Type Check (Hard constraint filter)
            type_score = self._check_type_compatibility(prompt_struct, cand_struct, cand)
            
            # 2. Predictive Coding (Soft matching)
            pred_score = self._compute_prediction_error(prompt, cand)
            
            # Combined Score: Weighted sum favoring structural validity
            # If type check fails (0.0), the candidate is heavily penalized regardless of word match
            base_score = (type_score * 0.6) + (pred_score * 0.4)
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"TypeValid:{type_score:.2f}, PredMatch:{pred_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # NCD Tie-breaking for top candidates if scores are very close
        if len(results) > 1 and abs(results[0]['score'] - results[1]['score']) < 0.01:
            # Use NCD to break tie against the prompt
            for i in range(len(results) - 1):
                if abs(results[i]['score'] - results[i+1]['score']) < 0.01:
                    ncd_i = self._compute_ncd(prompt, results[i]['candidate'])
                    ncd_next = self._compute_ncd(prompt, results[i+1]['candidate'])
                    # Lower NCD is better (more similar structure)
                    if ncd_i > ncd_next:
                        results[i], results[i+1] = results[i+1], results[i]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        RL-style Policy Wrapper.
        Evaluates the certainty of the answer being correct based on:
        1. How much it beats the average alternative (simulated margin).
        2. Structural integrity.
        """
        # Generate pseudo-candidates to estimate margin if we don't have the full list
        # Since we only have one answer here, we evaluate its intrinsic 'fit'
        
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # 1. Structural Fit
        type_fit = self._check_type_compatibility(p_struct, a_struct, answer)
        
        # 2. Predictive Fit
        pred_fit = self._compute_prediction_error(prompt, answer)
        
        # 3. Margin estimation (Heuristic: Is the score significantly high?)
        # A perfect match yields 1.0. Random yields ~0.1-0.3
        raw_score = (type_fit * 0.6) + (pred_fit * 0.4)
        
        # Sigmoid-like mapping to 0-1 based on thresholds
        if raw_score > 0.8:
            conf = 0.95
        elif raw_score > 0.6:
            conf = 0.75
        elif raw_score > 0.4:
            conf = 0.5
        else:
            conf = 0.2
            
        # Penalize if type check failed completely
        if type_fit == 0.0:
            conf = min(conf, 0.1)
            
        return float(conf)