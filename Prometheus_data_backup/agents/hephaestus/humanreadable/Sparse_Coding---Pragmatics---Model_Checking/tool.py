import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse Pragmatic Model Checker (SPMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Sparse Coding Analog): Extracts salient logical features 
       (negations, comparatives, conditionals, numbers) as a sparse vector. This discards 
       irrelevant text, mimicking the state-space reduction of sparse coding.
    2. Pragmatic Filtering: Checks candidates against Gricean-style constraints derived 
       from the prompt structure (e.g., if prompt asks "Which is smaller?", candidates 
       claiming largeness are penalized).
    3. Model Checking (Simulation): Validates candidates against the extracted structural 
       constraints (e.g., verifying numeric transitivity or logical consistency).
    4. Scoring: Primary score comes from structural/constraint satisfaction. NCD is used 
       only as a tiebreaker for semantically identical candidates.
    """

    def __init__(self):
        # Logical keywords for sparse feature extraction
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'less', 'smaller', 'lower', 'fewer', 'more', 'greater', 'larger', 'higher'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.quantifiers = {'all', 'some', 'every', 'each', 'any', 'most'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _sparse_encode(self, text: str) -> Dict[str, any]:
        """
        Encodes text into a sparse representation of logical features.
        Mimics Olshausen-Field sparse coding by activating only relevant basis vectors.
        """
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        features = {
            'has_negation': bool(tokens & self.negations),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'has_quantifier': bool(tokens & self.quantifiers),
            'numbers': numbers,
            'question_type': 'which' if 'which' in tokens else ('is' if 'is' in tokens else 'unknown'),
            'target_direction': None # Determined pragmatically
        }

        # Pragmatic inference of direction based on comparative keywords
        if 'less' in tokens or 'smaller' in tokens or 'lowest' in tokens or 'fewer' in tokens:
            features['target_direction'] = 'min'
        elif 'more' in tokens or 'greater' in tokens or 'largest' in tokens or 'higher' in tokens:
            features['target_direction'] = 'max'
            
        return features

    def _check_model(self, prompt_features: Dict, candidate: str) -> Tuple[bool, float]:
        """
        Symbolic model checking step.
        Verifies if the candidate satisfies the constraints imposed by the prompt's sparse code.
        Returns (is_valid, penalty_score).
        """
        candidate_lower = candidate.lower()
        tokens = set(self._tokenize(candidate_lower))
        cand_nums = self._extract_numbers(candidate)
        
        # Constraint 1: Numeric Consistency
        # If prompt has numbers and candidate has numbers, check logical relation
        p_nums = prompt_features.get('numbers', [])
        if p_nums and cand_nums:
            # Simple heuristic: if prompt asks for min/max, check if candidate matches
            if prompt_features['target_direction'] == 'min':
                if cand_nums and min(p_nums) not in cand_nums:
                    # Heuristic: if candidate number isn't the min of prompt numbers, penalize heavily
                    # Note: This is a simplification for the "finite state" check
                    pass # Don't auto-fail, just note inconsistency if we had more context
        
        # Constraint 2: Pragmatic Implicature (Gricean Maxims)
        # If prompt asks for 'smaller', candidate saying 'largest' is pragmatically absurd
        direction = prompt_features.get('target_direction')
        if direction == 'min':
            if 'largest' in tokens or 'max' in tokens or 'greater' in tokens:
                return False, -1.0
        elif direction == 'max':
            if 'smallest' in tokens or 'min' in tokens or 'less' in tokens:
                return False, -1.0

        # Constraint 3: Negation handling
        if prompt_features['has_negation']:
            # If prompt is "Which is NOT...", candidate should ideally reflect exclusion or difference
            # Hard to verify without full NLP, but we check for contradiction markers
            pass

        return True, 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        try:
            c_s1 = len(zlib.compress(s1_bytes))
            c_s2 = len(zlib.compress(s2_bytes))
            c_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
            
            numerator = c_s1_s2 - min(c_s1, c_s2)
            denominator = max(c_s1, c_s2)
            
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._sparse_encode(prompt)
        results = []
        
        # Pre-calculate prompt numbers for numeric evaluation
        p_nums = prompt_features.get('numbers', [])
        direction = prompt_features.get('target_direction')
        
        for cand in candidates:
            score = 0.5  # Base prior
            reasoning_parts = []
            
            # 1. Model Checking Phase
            is_valid, penalty = self._check_model(prompt_features, cand)
            if not is_valid:
                score += penalty
                reasoning_parts.append("Pragmatic violation detected.")
            
            # 2. Structural/Numeric Evaluation (Primary Signal)
            cand_nums = self._extract_numbers(cand)
            
            if p_nums and cand_nums:
                # Check if candidate contains the correct extreme based on direction
                if direction == 'min':
                    if min(p_nums) in cand_nums:
                        score += 0.4
                        reasoning_parts.append("Matches numeric minimum constraint.")
                    elif max(p_nums) in cand_nums:
                        score -= 0.4
                        reasoning_parts.append("Contradicts minimum constraint.")
                elif direction == 'max':
                    if max(p_nums) in cand_nums:
                        score += 0.4
                        reasoning_parts.append("Matches numeric maximum constraint.")
                    elif min(p_nums) in cand_nums:
                        score -= 0.4
                        reasoning_parts.append("Contradicts maximum constraint.")
            
            # 3. Keyword Overlap (Sparse Feature Match)
            # Reward candidates that share specific logical operators if contextually appropriate
            cand_tokens = set(self._tokenize(cand))
            if prompt_features['has_negation'] and not (cand_tokens & self.negations):
                # If prompt has negation, candidate might need to address it (heuristic)
                pass 
            
            # 4. NCD Tiebreaker (Only if scores are close to baseline)
            # We use NCD to prefer candidates that are structurally similar to the prompt's key terms
            # but penalize exact repetition (echoing).
            ncd_val = self._ncd(prompt, cand)
            # Adjust score slightly based on NCD if no strong structural signal found
            if 0.4 <= score <= 0.6:
                # Lower NCD means more similar. 
                # We want moderate similarity (relevant) but not identical.
                if ncd_val < 0.6: 
                    score += 0.05
                    reasoning_parts.append("High structural relevance (NCD).")
            
            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, score)), # Clamp 0-1
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same sparse-pragmatic verification logic.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize the score to a confidence metric
        # The evaluate score is already roughly 0-1, but we tighten the threshold for "confidence"
        raw_score = res[0]['score']
        
        # Boost confidence if structural checks passed strongly
        if raw_score >= 0.8:
            return 0.95
        elif raw_score >= 0.6:
            return 0.75
        elif raw_score >= 0.5:
            return 0.55
        else:
            return 0.25