import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Chaos Compositional Reservoir (C3R) Approximation.
    
    Mechanism:
    1. Compositionality (Structural Parsing): Decomposes prompts into logical atoms 
       (negations, comparatives, conditionals, numbers) to build a symbolic representation.
    2. Chaos Theory (Sensitivity): Uses small structural differences (e.g., "not", swapped operands) 
       to induce large divergences in scoring vectors via non-linear amplification.
    3. Self-Organized Criticality (Avalanche Search): Simulates an avalanche process where 
       candidate scores are perturbed. If a candidate violates a hard logical constraint 
       (e.g., negative number where positive expected), it triggers an "avalanche" (massive penalty),
       redistributing probability mass to valid candidates. This mimics the sandpile model's 
       power-law distribution of errors/corrections.
    
    This hybrid approach prioritizes structural logic over string similarity (NCD), using NCD 
    only as a final tiebreaker for semantically identical strings.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _extract_structure(self, text: str) -> Dict:
        """Compositional parsing: Extracts logical primitives."""
        text_lower = text.lower()
        structure = {
            "negations": len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            "numbers": [],
            "length": len(text),
            "hash": hash(text) # Deterministic seed for chaos
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        if nums:
            structure["numbers"] = [float(n) for n in nums]
        return structure

    def _chaotic_amplify(self, base_score: float, struct_diff: float, seed: int) -> float:
        """
        Chaos Theory: Amplifies tiny structural differences.
        Uses a logistic map-like iteration to sensitize the score to initial conditions.
        """
        if struct_diff == 0:
            return base_score
        
        # Normalize diff to (0, 1)
        x = abs(math.sin(struct_diff * seed)) 
        r = 3.99 # Edge of chaos (logistic map parameter)
        
        # Iterate a few times to amplify sensitivity
        for _ in range(4):
            x = r * x * (1 - x)
            
        # Map chaotic output to a modifier (-0.5 to 0.5)
        modifier = (x - 0.5) * 1.0 
        return base_score + modifier

    def _soc_avalanche_check(self, candidate_struct: Dict, prompt_struct: Dict, base_score: float) -> float:
        """
        Self-Organized Criticality: Avalanches trigger on logical violations.
        Mimics sandpile toppling: if a constraint is violated, score drops precipitously.
        """
        score = base_score
        
        # Rule 1: Negation mismatch (Modus Tollens approximation)
        # If prompt has negation and candidate doesn't (or vice versa), potential avalanche
        neg_diff = abs(candidate_struct.get('negations', 0) - prompt_struct.get('negations', 0))
        if neg_diff > 0 and prompt_struct.get('negations', 0) > 0:
            # Avalanche trigger: heavy penalty for missing negation in negative context
            score *= 0.2 

        # Rule 2: Numeric consistency (Constraint propagation)
        p_nums = prompt_struct.get('numbers', [])
        c_nums = candidate_struct.get('numbers', [])
        
        if p_nums and c_nums:
            # Simple transitivity check: if prompt implies A > B, candidate shouldn't say B > A
            # Here we just check if numbers are wildly off-scale compared to prompt context
            try:
                p_max = max(p_nums)
                c_max = max(c_nums)
                if p_max > 0 and c_max > p_max * 10: # Heuristic avalanche
                    score *= 0.1
            except:
                pass

        # Rule 3: Conditional logic presence
        if prompt_struct.get('conditionals', 0) > 0 and candidate_struct.get('conditionals', 0) == 0:
            # Candidate ignores conditional structure of prompt
            score *= 0.6
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        results = []
        
        # Baseline scoring based on structural alignment
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Compositional Overlap Score (Base)
            # Reward matching logical operators
            logic_match = 0
            logic_match += 1.0 if (p_struct['negations'] > 0) == (c_struct['negations'] > 0) else -0.5
            logic_match += 1.0 if (p_struct['conditionals'] > 0) == (c_struct['conditionals'] > 0) else 0.0
            
            # Numeric heuristic: if prompt has numbers, reward candidates with numbers
            if p_struct['numbers']:
                logic_match += 0.5 if c_struct['numbers'] else -0.5
            
            base_score = 0.5 + (logic_match * 0.2)
            
            # 2. Chaos Sensitivity
            # Use length difference and hash diff as initial condition delta
            delta = abs(len(prompt) - len(cand)) / (len(prompt) + 1) + abs(hash(prompt) - hash(cand)) * 1e-10
            chaotic_score = self._chaotic_amplify(base_score, delta, p_struct['hash'])
            
            # 3. SOC Avalanche Check
            final_score = self._soc_avalanche_check(c_struct, p_struct, chaotic_score)
            
            # Clamp score
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_match:.2f}, Chaos mod: {chaotic_score:.2f}, SOC adj: {final_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are too close (within epsilon)
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < self.epsilon:
                ncd_i = self._ncd(prompt, results[i]['candidate'])
                ncd_next = self._ncd(prompt, results[i+1]['candidate'])
                if ncd_i < ncd_next:
                    # Swap if current is less similar (higher NCD) than next
                    # Actually, we want LOWER NCD (more similar) to win ties usually, 
                    # but per instructions NCD is tiebreaker. 
                    # Let's prefer lower NCD (more compressed together = more similar)
                    pass 
                # Re-order based on NCD for ties
                if ncd_i > ncd_next:
                    results[i], results[i+1] = results[i+1], results[i]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency."""
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        conf = 0.5
        
        # Check negation consistency
        if p_struct['negations'] > 0:
            if a_struct['negations'] > 0:
                conf += 0.3
            else:
                conf -= 0.4 # Penalty for missing negation
        
        # Check conditional consistency
        if p_struct['conditionals'] > 0:
            if a_struct['conditionals'] > 0:
                conf += 0.1
            else:
                conf -= 0.1
                
        # Numeric sanity check
        if p_struct['numbers'] and a_struct['numbers']:
            conf += 0.1
            
        # Chaos sensitivity check (deterministic noise)
        delta = abs(len(prompt) - len(answer))
        if delta > len(prompt) * 0.5:
            conf -= 0.2
            
        return max(0.0, min(1.0, conf))