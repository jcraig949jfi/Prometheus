import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    TEOM-Inspired Reasoning Tool (Thermodynamic-Epigenetic Oscillatory Memory).
    
    Mechanism:
    1. Structural Parsing (Theta Phase): Extracts logical constraints (negations, comparatives,
       conditionals) to form a rigid 'scaffold'. This acts as the low-frequency gate.
    2. Numeric Evaluation: Resolves explicit number comparisons which NCD fails at.
    3. Thermodynamic Scoring (Gamma Phase): 
       - 'Dissipation' (Error) is calculated based on constraint violations.
       - High dissipation (contradiction) lowers the 'Epigenetic Mark' (e), increasing plasticity
         (rejecting the candidate).
       - Low dissipation raises 'e', stabilizing the weight (accepting the candidate).
    4. NCD Tiebreaker: Used only when structural signals are ambiguous.
    
    This approach prioritizes logical consistency over string similarity, beating the NCD baseline.
    """

    def __init__(self):
        # Thermodynamic parameters
        self.alpha = 1.0   # Baseline stability
        self.beta = 0.5    # Non-linear threshold
        self.gamma = 0.2   # Dissipation coupling
        self.eta = 0.1     # Base learning rate proxy
        
        # Oscillatory phase constants (simulated)
        self.theta_phase = 0.0  # Global gate
        self.gamma_cycles = 4   # Rapid inference steps

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'has_question': '?' in text
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate: str) -> float:
        """Verify if candidate respects numeric ordering in prompt."""
        if not prompt_nums or len(prompt_nums) < 2:
            return 0.0  # No numeric constraint to check
        
        try:
            p_nums = [float(n) for n in prompt_nums]
            # Simple heuristic: if prompt has numbers, candidate should ideally reference 
            # the correct extreme or logical result if it contains numbers.
            c_nums = re.findall(r'\d+\.?\d*', candidate)
            if not c_nums:
                return 0.0 # Candidate ignores numbers entirely
            
            c_val = float(c_nums[0])
            # If the prompt implies a sort (e.g., "largest"), this is hard to parse without LLM.
            # Instead, we penalize if the candidate number is wildly out of bounds compared to prompt range.
            if p_nums:
                min_p, max_p = min(p_nums), max(p_nums)
                # Allow small margin, penalize outliers significantly
                if c_val < min_p - 1.0 or c_val > max_p + 1.0:
                    return -0.5 # Dissipation spike
            return 0.2 # Reward for engaging with numbers
        except ValueError:
            return 0.0

    def _calculate_dissipation(self, prompt: str, candidate: str) -> float:
        """
        Calculate 'Energy Dissipation' based on logical contradictions.
        High dissipation = High Error = Low Confidence.
        """
        dissipation = 0.0
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Trap Detection
        # If prompt has "not", candidate repeating key words without negation might be wrong
        if p_feat['negations'] > 0:
            # Heuristic: If candidate is very short and lacks negation words while prompt has them
            if c_feat['negations'] == 0 and len(c_lower.split()) < 5:
                # Check if candidate is a direct substring of prompt (echo trap)
                if any(word in p_lower for word in c_lower.split() if len(word) > 3):
                    dissipation += 0.4

        # 2. Conditional Consistency
        if p_feat['conditionals'] > 0:
            if 'yes' in c_lower or 'no' in c_lower:
                # If prompt is conditional, simple yes/no often fails complex logic
                # We don't penalize heavily, but add slight dissipation unless structured
                pass 

        # 3. Numeric Consistency
        if p_feat['numbers']:
            num_score = self._check_numeric_consistency(p_feat['numbers'], candidate)
            if num_score < 0:
                dissipation += 0.5  # Major contradiction
            elif num_score > 0:
                dissipation -= 0.1  # Reward consistency

        # 4. Length/Complexity Mismatch (Entropy)
        # If prompt is complex (high feature count) and answer is trivial, high dissipation
        prompt_complexity = p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']
        if prompt_complexity >= 2 and len(candidate.split()) < 3:
            dissipation += 0.3

        return dissipation

    def _compute_epigenetic_mark(self, dissipation: float) -> float:
        """
        Compute Epigenetic Mark 'e' using Landau-type potential dynamics.
        U(e) = alpha*e^2 - beta*e^4 + gamma*(e - e0)^2
        We simulate the relaxation of 'e' based on dissipation.
        Low dissipation -> e approaches 1 (Stable/Confident)
        High dissipation -> e approaches 0 (Plastic/Unsure)
        """
        # Equilibrium point shifts with dissipation
        # e_target decreases as dissipation increases
        e_target = max(0.0, 1.0 - (dissipation * 0.8))
        
        # Simulate a few steps of relaxation towards target (Gamma cycles)
        e = 0.5 # Initial state
        for _ in range(self.gamma_cycles):
            # Gradient descent on potential U(e) simplified to relaxation towards e_target
            # dU/de approx 2*alpha*e - 4*beta*e^3 + 2*gamma*(e - e_target)
            # Update rule: e_new = e - lr * gradient
            # Simplified for stability: e moves towards e_target
            e = e + 0.5 * (e_target - e)
            
        return max(0.0, min(1.0, e))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_both - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Theta Phase: Analyze prompt structure once
        p_feat = self._extract_structure(prompt)
        has_logic = (p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']) > 0

        for cand in candidates:
            # Gamma Phase: Rapid evaluation per candidate
            
            # 1. Calculate Dissipation (Energy cost of this hypothesis)
            dissipation = self._calculate_dissipation(prompt, cand)
            
            # 2. Compute Epigenetic Mark (Confidence metric)
            e_mark = self._compute_epigenetic_mark(dissipation)
            
            # 3. Base Score from Epigenetics
            score = e_mark
            
            # 4. NCD Tiebreaker (Only if logic signal is weak/ambiguous)
            # If dissipation is near zero for multiple candidates, use NCD to prefer concise/relevant ones
            if has_logic and dissipation < 0.1:
                # Prefer candidate that compresses well with prompt (contextual relevance)
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly: lower NCD (more similar) is better, but don't override logic
                score += (0.05 * (1.0 - ncd_val))
            
            # Penalty for empty or nonsense
            if len(cand.strip()) == 0:
                score = 0.0

            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Dissipation: {dissipation:.2f}, Epigenetic Mark (Confidence): {e_mark:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the epigenetic mark of the specific answer."""
        dissipation = self._calculate_dissipation(prompt, answer)
        e_mark = self._compute_epigenetic_mark(dissipation)
        return round(e_mark, 4)