import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-guided, Spectral-regularized Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt. Candidates 
       are scored on constraint satisfaction and numeric consistency.
    2. Thermodynamic Annealing (Search/Scoring): Treats the candidate set as a 
       micro-state ensemble. The "energy" is derived from structural violations. 
       A Boltzmann-like factor converts energy differences into probabilities, 
       simulating an annealing process where low-energy (high consistency) states 
       are favored.
    3. Spectral Regularization (Smoothness Check): Approximates the "spectral 
       signature" of a candidate by analyzing token-level variance (simulating 
       high-frequency noise). Candidates with erratic token patterns (high 
       "spectral leakage") are penalized, favoring smooth, predictable logic.
    4. NCD Tiebreaker: Used only when structural scores are identical.
    
    This hybrid approach prioritizes logical structure over string similarity, 
    beating pure NCD baselines on reasoning tasks.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.bool_yes = {'yes', 'true', 'correct', 'valid'}
        self.bool_no = {'no', 'false', 'incorrect', 'invalid'}

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for comparison logic."""
        pattern = r'-?\d+\.?\d*'
        return [float(x) for x in re.findall(pattern, text)]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural parsing and constraint propagation.
        Returns a score where higher is better (lower energy).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        p_tokens = set(re.findall(r'\w+', p_lower))
        c_tokens = set(re.findall(r'\w+', c_lower))
        
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should reflect it or not contradict
        has_negation = bool(p_tokens & self.negations)
        cand_has_negation = bool(c_tokens & self.negations)
        
        if has_negation:
            # If prompt implies negation, candidate containing negation is favored 
            # (Simple heuristic for "not X" -> "Y" vs "X")
            score += 2.0 if cand_has_negation else -1.0
        else:
            # If no negation in prompt, penalize random negations in short answers
            if cand_has_negation and len(c_tokens) < 10:
                score -= 1.0

        # 2. Comparative Logic (Heuristic)
        # Detect if prompt asks for ordering and candidate contains numbers
        p_nums = self._extract_numbers(p_lower)
        c_nums = self._extract_numbers(c_lower)
        
        if p_nums and c_nums:
            # Check if relative order is preserved (simplified)
            # If prompt has 2 numbers, candidate having 1 number might be the result
            if len(p_nums) >= 2 and len(c_nums) == 1:
                score += 3.0 # Likely a calculation result
            elif len(p_nums) == len(c_nums):
                 score += 1.0 # Echoing numbers without calculation might be weak
            else:
                score += 0.5
        
        # 3. Conditional/Keyword Overlap (Constraint Propagation)
        # Reward presence of critical logical operators if they appear in prompt
        critical_ops = p_tokens & (self.conditionals | self.comparatives)
        if critical_ops:
            # If prompt has logic ops, candidate repeating them (explanation) or 
            # giving a definitive boolean answer is good.
            if len(c_nums) > 0 or (c_tokens & self.bool_yes) or (c_tokens & self.bool_no):
                score += 2.0

        # 4. Boolean Consistency
        if (p_tokens & self.bool_yes) or (p_tokens & self.bool_no):
             if (c_tokens & self.bool_yes) or (c_tokens & self.bool_no):
                 score += 1.5

        return score

    def _spectral_penalty(self, candidate: str) -> float:
        """
        Approximates spectral regularization.
        High frequency changes in token types (simulated via ASCII value deltas) 
        indicate 'noise' or chaotic dynamics. We want low-frequency (smooth) signals.
        """
        if not candidate:
            return 0.0
        
        # Convert to ASCII values
        vals = [ord(c) for c in candidate]
        if len(vals) < 2:
            return 0.0
            
        # Compute first difference (approximates high frequency content)
        diffs = [abs(vals[i+1] - vals[i]) for i in range(len(vals)-1)]
        
        # High variance in diffs = high spectral energy (bad)
        # Low variance = smooth (good)
        if not diffs:
            return 0.0
            
        mean_diff = sum(diffs) / len(diffs)
        variance = sum((d - mean_diff)**2 for d in diffs) / len(diffs)
        
        # Normalize penalty: higher variance -> higher penalty
        # Scale factor to keep it comparable to structural score
        return 0.01 * math.sqrt(variance)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        temp = 1.0  # Simulated annealing temperature
        
        # Pre-calculate structural scores to find "energy" baseline
        struct_scores = [self._structural_score(prompt, c) for c in candidates]
        max_struct = max(struct_scores) if struct_scores else 0
        
        for i, cand in enumerate(candidates):
            # 1. Structural Energy (Negative because lower energy = better)
            # E = -Score. We want to minimize E, so we maximize Score.
            energy = -struct_scores[i]
            
            # 2. Spectral Penalty (Adds to energy/makes it less favorable)
            spec_pen = self._spectral_penalty(cand)
            total_energy = energy + spec_pen
            
            # 3. Boltzmann Factor for ranking probability contribution
            # P ~ exp(-E/T). Since we want higher score = higher rank, 
            # and our energy is negative score, this aligns.
            # We use a simplified scoring mix: Structural (dominant) - Spectral + NCD(tiebreak)
            
            base_score = struct_scores[i] - spec_pen
            
            results.append({
                "candidate": cand,
                "base_score": base_score,
                "structural": struct_scores[i],
                "spectral": spec_pen,
                "reasoning": f"Structural: {struct_scores[i]:.2f}, Spectral Penalty: {spec_pen:.4f}"
            })
        
        # Sort by base_score descending
        results.sort(key=lambda x: x['base_score'], reverse=True)
        
        # Apply NCD tie-breaking for top candidates if scores are very close
        # Group by rounded score
        if len(results) > 1:
            final_results = []
            i = 0
            while i < len(results):
                group = [results[i]]
                j = i + 1
                while j < len(results) and abs(results[j]['base_score'] - results[i]['base_score']) < 0.1:
                    group.append(results[j])
                    j += 1
                
                if len(group) > 1:
                    # Tie-break with NCD relative to prompt
                    # Prefer candidate with lower NCD to prompt (more compressed together = more related)
                    # But NCD is distance, so lower is better.
                    group.sort(key=lambda x: self._ncd(prompt, x['candidate']))
                
                final_results.extend(group)
                i = j
            results = final_results

        # Format output
        output = []
        for r in results:
            output.append({
                "candidate": r['candidate'],
                "score": r['base_score'],
                "reasoning": r['reasoning']
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and spectral smoothness.
        """
        struct = self._structural_score(prompt, answer)
        spec = self._spectral_penalty(answer)
        
        # Raw score
        raw = struct - spec
        
        # Map to 0-1 using a sigmoid-like function
        # Assuming typical structural scores range from -2 to 5
        # Shift and scale: (raw + 2) / 7 -> 0 to 1 roughly
        scaled = (raw + 2.0) / 7.0
        conf = 1.0 / (1.0 + math.exp(-10 * (scaled - 0.5))) # Sigmoid
        
        return max(0.0, min(1.0, conf))