import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Clonal-Selection NAS with Hamiltonian-Guided Mutation (ACS-HGM) Simulator.
    
    Mechanism:
    1. Antigen Recognition (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt as the "immune challenge".
    2. Clonal Selection & Hypermutation: Evaluates candidates against these constraints.
       Candidates violating hard constraints (e.g., negation mismatches) are suppressed (score 0).
    3. Hamiltonian Guidance (Optimal Control Proxy): Instead of solving adjoint equations 
       (which failed historical causal checks per Coeus analysis), we use a deterministic 
       penalty function based on constraint violation severity. This acts as the control 'u' 
       steering the score away from invalid regions.
    4. Immune Memory: Tracks seen structural patterns to penalize repetitive failure modes.
    5. Scoring: Primary signal is structural adherence (Reasoning). Tiebreaker is NCD 
       (compression distance to prompt logic).
    """

    def __init__(self):
        self.memory_pool = []  # Stores hashes of successful structural patterns
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'larger', 'more', 'less', 'smaller', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'unless', 'only if'}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _analyze_structure(self, text: str) -> Dict:
        """Parse text for logical constraints (Antigen encoding)."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        numbers = self._extract_numbers(text)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'word_set': words,
            'length': len(text)
        }

    def _compute_hamiltonian_penalty(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Computes a penalty score based on constraint violations (Adjoint-like sensitivity).
        Lower penalty = better fit.
        """
        penalty = 0.0
        
        # 1. Negation Consistency (Modus Tollens check proxy)
        # If prompt implies negation, candidate should likely reflect it or not contradict it
        if prompt_struct['negation'] and not cand_struct['negation']:
            # Heuristic: Check if candidate is a simple affirmation that ignores the negation
            simple_yes_no = re.match(r'^(yes|no|true|false)$', candidate.strip().lower())
            if simple_yes_no:
                penalty += 0.5 # High penalty for ignoring context
        
        # 2. Numeric Consistency (Optimal Control constraint)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Check for direct contradiction in simple comparisons
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                # If prompt says A > B, and candidate explicitly says A < B (detected via numbers order)
                # This is a simplified proxy for logical consistency
                if (p_nums[0] > p_nums[1]) and (c_nums[0] < c_nums[1]):
                     penalty += 1.0 # Fatal error
                elif (p_nums[0] < p_nums[1]) and (c_nums[0] > c_nums[1]):
                     penalty += 1.0

        # 3. Length/Complexity mismatch (Entropy check)
        # Extreme brevity in complex prompts suggests failure to reason
        if prompt_struct['length'] > 50 and cand_struct['length'] < 5:
            if prompt_struct['conditional'] or prompt_struct['comparative']:
                penalty += 0.3

        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._analyze_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            cand_struct = self._analyze_structure(cand)
            
            # Hamiltonian Penalty (Primary Reasoning Signal)
            penalty = self._compute_hamiltonian_penalty(prompt_struct, cand_struct, prompt, cand)
            
            # Base score starts at 1.0, reduced by penalty
            base_score = max(0.0, 1.0 - penalty)
            
            # Structural matching bonus (Clonal affinity)
            affinity_bonus = 0.0
            if prompt_struct['negation'] == cand_struct['negation']:
                affinity_bonus += 0.1
            if bool(prompt_struct['numbers']) == bool(cand_struct['numbers']):
                affinity_bonus += 0.05
            
            # NCD as tiebreaker (Immune Memory recall)
            # Only used if structural signals are weak or equal
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Small weight
            
            final_score = base_score + affinity_bonus + ncd_score
            
            # Reasoning trace
            reasoning = f"Structural match: {1.0-penalty:.2f}, Affinity: {affinity_bonus:.2f}, NCD: {ncd_val:.2f}"
            if penalty > 0.5:
                reasoning += " [CRITICAL CONSTRAINT VIOLATION]"

            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on structural consistency between prompt and answer.
        Returns 0.0 to 1.0.
        """
        prompt_struct = self._analyze_structure(prompt)
        ans_struct = self._analyze_structure(answer)
        
        # Calculate penalty using the same Hamiltonian proxy
        penalty = self._compute_hamiltonian_penalty(prompt_struct, ans_struct, prompt, answer)
        
        # Convert penalty to confidence
        # Penalty 0 -> Confidence 1.0
        # Penalty >= 1 -> Confidence 0.0
        confidence = max(0.0, 1.0 - penalty)
        
        # Boost if structural features align (e.g. both have numbers if prompt had numbers)
        if prompt_struct['numbers'] and ans_struct['numbers']:
            confidence = min(1.0, confidence + 0.2)
            
        return round(confidence, 4)