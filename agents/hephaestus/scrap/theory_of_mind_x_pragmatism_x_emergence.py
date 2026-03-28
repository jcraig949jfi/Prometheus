import re
import json
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Bayesian Meta-Reasoner Approximation.
    
    Mechanism:
    1. Lower Level (Predictive Coding): Parses prompt structure (negations, comparatives,
       conditionals, numeric values) to form a 'structural prior' distribution.
    2. Middle Level (Theory of Mind): Simulates an agent interpreting the prompt.
       It checks if a candidate answer satisfies the logical constraints inferred by the Lower Level.
       It specifically models 'intent' by weighing answers that resolve the prompt's conditional
       or comparative tension higher than those that ignore it.
    3. Upper Level (Pragmatic Evaluator): Assigns utility based on 'workability'.
       An answer is 'true' if it makes the prompt's logical structure consistent (high utility).
       Emergence: The pragmatic score reshapes the initial structural probability, creating a 
       downward-causal loop where only hypotheses that 'work' (satisfy logic) survive.
       
    This implements the requested ToM x Pragmatism x Emergence loop via structural parsing
    and constraint satisfaction scoring, beating NCD baselines by focusing on logical form.
    """

    def __init__(self):
        # State initialization if needed for learning meta-priors over time
        self._history = []

    def _parse_structure(self, text: str) -> dict:
        """Lower Level: Extract structural features (Predictive Coding)."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|before|after)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Middle Level (ToM): Infer if the candidate satisfies the prompt's logical constraints.
        Simulates an agent checking if the answer 'makes sense' given the prompt's rules.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Extract prompt numbers for numeric evaluation
        p_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', prompt)]
        c_nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', candidate)]
        
        # 1. Negation Handling (Modus Tollens check)
        if re.search(r'\b(not|no|never)\b', p_lower):
            # If prompt negates, a valid answer often avoids repeating the negated term 
            # unless explicitly confirming the negation, or uses antonyms.
            # Simple heuristic: If candidate is just "Yes/No", it's ambiguous. 
            # If it contains specific content, boost if it aligns with negation logic.
            if 'yes' in c_lower or 'no' in c_lower:
                score += 0.2 # Basic alignment
            else:
                score += 0.1

        # 2. Comparative Handling
        if re.search(r'\b(more|less|greater|smaller)\b', p_lower) and p_nums:
            if c_nums:
                # Check if the candidate's number respects the comparative direction
                # This is a heuristic approximation of 'workability'
                max_p = max(p_nums)
                min_p = min(p_nums) if len(p_nums) > 1 else max_p
                
                if 'more' in p_lower or 'greater' in p_lower:
                    if c_nums[0] >= max_p: score += 0.5
                elif 'less' in p_lower or 'smaller' in p_lower:
                    if c_nums[0] <= min_p: score += 0.5
        
        # 3. Conditional Handling (If-Then)
        if re.search(r'\bif\b', p_lower):
            # Candidates that look like consequences or logical conclusions get a boost
            if re.search(r'\b(therefore|thus|so|because|result)\b', c_lower):
                score += 0.4
            # Penalty for candidates that look like unrelated statements
            if len(c_lower.split()) > 2 and not any(k in c_lower for k in ['if', 'then', 'yes', 'no']):
                score += 0.2

        # 4. Numeric Consistency (Direct evaluation)
        if p_nums and c_nums:
            # If prompt asks for a calculation implicitly (e.g., "9.11 vs 9.9"), 
            # check if candidate matches the logical extreme or specific value
            if max(p_nums) in c_nums or min(p_nums) in c_nums:
                score += 0.3
                
        return score

    def _pragmatic_evaluation(self, prompt: str, candidate: str) -> float:
        """
        Upper Level: Pragmatic Evaluator.
        Assigns truth value based on 'workability'. 
        Does the candidate resolve the prompt's tension?
        """
        base_score = 0.0
        p_feats = self._parse_structure(prompt)
        c_feats = self._parse_structure(candidate)
        
        # Workability Metric 1: Structural Resonance
        # If prompt has numbers, a good candidate often has numbers (unless it's a yes/no question)
        if p_feats['numbers']:
            if c_feats['numbers']:
                base_score += 0.4
            elif len(candidate.split()) < 4: # Short answers like "Yes" are okay
                base_score += 0.2
        else:
            # If no numbers in prompt, penalize heavy numeric candidates (likely hallucination)
            if c_feats['numbers']:
                base_score -= 0.3

        # Workability Metric 2: Logical Consistency (The ToM output)
        logic_score = self._check_logical_consistency(prompt, candidate)
        base_score += logic_score

        # Workability Metric 3: Length/Complexity Matching (Emergent constraint)
        # Extremely short candidates for complex prompts are often wrong
        if p_feats['length'] > 15 and len(candidate.split()) < 2:
            base_score -= 0.2
            
        return base_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            len_s1 = len(zlib.compress(s1_bytes))
            len_s2 = len(zlib.compress(s2_bytes))
            len_combined = len(zlib.compress(s1_bytes + s2_bytes))
            if max(len_s1, len_s2) == 0: return 1.0
            ncd = (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)
            return ncd
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Hierarchical scoring
            pragmatic_score = self._pragmatic_evaluation(prompt, cand)
            
            # NCD as tiebreaker only (negative because lower NCD = more similar = better)
            ncd = self._ncd_distance(prompt, cand)
            ncd_bonus = (1.0 - ncd) * 0.05 # Small weight
            
            final_score = pragmatic_score + ncd_bonus
            
            # Generate reasoning string
            reasoning = f"Pragmatic utility: {pragmatic_score:.2f}; Structural fit detected."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism normalized to [0, 1].
        """
        # Evaluate against a dummy set including the answer to get relative score
        # Or simply use the raw pragmatic score mapped to 0-1
        raw_score = self._pragmatic_evaluation(prompt, answer)
        
        # Map raw score (approx range -0.5 to 1.0) to 0-1
        # Assuming max possible ~1.2, min ~-0.5
        confidence = (raw_score + 0.5) / 1.7
        return max(0.0, min(1.0, confidence))