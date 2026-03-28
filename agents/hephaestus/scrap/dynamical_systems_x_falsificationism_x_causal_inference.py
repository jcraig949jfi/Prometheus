import re
import zlib
import math

class ReasoningTool:
    """
    Lyapunov-Guided Falsification Tool (Approximated for Static Constraints).
    
    Mechanism:
    1. Structural Parsing (The "ODE State"): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a structural vector.
    2. Falsification Loss (The "Lyapunov Exponent"): Instead of simulating trajectories,
       we measure the "divergence" between the prompt's logical constraints and the 
       candidate's structural signature. 
       - High divergence on key logical operators (e.g., prompt says "not", candidate omits) 
         yields a high "lambda" (instability), penalizing the score.
       - Candidates that preserve structural constraints (low lambda) are "stable" 
         and receive higher weights.
    3. Causal Intervention: We treat specific keywords (not, less, greater, if) as 
       intervention points. If a candidate fails to reflect the negation/comparison 
       direction specified in the prompt, it is "falsified" (score reduced).
    4. NCD Tiebreaker: Used only when structural scores are identical.
    """

    def __init__(self):
        # Logical operators acting as "intervention" points
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['less', 'greater', 'more', 'fewer', 'higher', 'lower', 'smaller', 'larger']
        self.conditionals = ['if', 'then', 'unless', 'otherwise']
        self.booleans = ['true', 'false', 'yes', 'no']
        
    def _normalize(self, text):
        return text.lower().strip()

    def _extract_numbers(self, text):
        # Extract floats/integers for numeric evaluation
        pattern = r"-?\d+\.?\d*"
        return [float(x) for x in re.findall(pattern, text)]

    def _count_keywords(self, text, keyword_list):
        words = re.findall(r'\w+', text.lower())
        return sum(words.count(k) for k in keyword_list)

    def _structural_signature(self, text):
        """
        Extracts a structural vector representing the logical 'dynamics' of the text.
        Returns a dict with counts and extracted numbers.
        """
        lower_text = text.lower()
        return {
            'neg': self._count_keywords(text, self.negations),
            'comp': self._count_keywords(text, self.comparatives),
            'cond': self._count_keywords(text, self.conditionals),
            'nums': self._extract_numbers(text),
            'len': len(text.split())
        }

    def _compute_divergence(self, prompt_sig, cand_sig):
        """
        Computes a 'Lyapunov-like' divergence score.
        High divergence = Instability = Falsification (Low Score).
        Low divergence = Stability = Survives Falsification (High Score).
        """
        divergence = 0.0
        
        # 1. Negation Stability: If prompt has negation, candidate should likely have it too
        # unless the candidate is explicitly contradicting (hard to detect statically), 
        # so we penalize missing negations heavily as a 'false hypothesis'.
        if prompt_sig['neg'] > 0 and cand_sig['neg'] == 0:
            divergence += 2.0 * prompt_sig['neg']
            
        # 2. Comparative Consistency: Check if comparative density matches roughly
        # This is a heuristic proxy for maintaining logical direction
        if prompt_sig['comp'] > 0:
            if cand_sig['comp'] == 0:
                divergence += 1.5
            else:
                divergence += 0.2 * abs(prompt_sig['comp'] - cand_sig['comp'])

        # 3. Numeric Transitivity Check (Simplified)
        # If both have numbers, check if the order of magnitude or count matches expectation
        # Here we just penalize huge discrepancies in number count as 'divergence'
        if len(prompt_sig['nums']) > 0:
            if len(cand_sig['nums']) == 0:
                divergence += 1.0
            else:
                # Check if the candidate numbers are wildly different (proxy for wrong calculation)
                # Since we don't know the operation, we check set overlap or proximity
                p_nums = set(prompt_sig['nums'])
                c_nums = set(cand_sig['nums'])
                if not p_nums.intersection(c_nums) and len(p_nums) > 0 and len(c_nums) > 0:
                     # If no numbers match, high divergence
                    divergence += 1.0

        return divergence

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        if min(len1, len2) == 0:
            return 1.0
        return (len_combined - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        prompt_sig = self._structural_signature(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization if needed
        prompt_complexity = prompt_sig['neg'] + prompt_sig['comp'] + prompt_sig['cond'] + len(prompt_sig['nums'])
        
        scores = []
        for cand in candidates:
            cand_sig = self._structural_signature(cand)
            
            # Calculate Divergence (Falsification metric)
            divergence = self._compute_divergence(prompt_sig, cand_sig)
            
            # Convert divergence to a stability score (0 to 1 range roughly)
            # Using exp(-alpha * divergence) as per the theoretical framework
            alpha = 0.5
            stability_score = math.exp(-alpha * divergence)
            
            # Heuristic boost for exact substring matches of numbers (strong causal link)
            p_nums = prompt_sig['nums']
            c_nums = cand_sig['nums']
            if p_nums and c_nums:
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    stability_score = min(1.0, stability_score + 0.2)

            scores.append((cand, stability_score))
        
        # Normalize scores to ensure ranking works well
        max_score = max(s[1] for s in scores) if scores else 1.0
        min_score = min(s[1] for s in scores) if scores else 0.0
        score_range = max_score - min_score if (max_score - min_score) > 1e-9 else 1.0
        
        ranked_results = []
        # Sort by stability score (descending)
        sorted_candidates = sorted(scores, key=lambda x: x[1], reverse=True)
        
        for i, (cand, raw_score) in enumerate(sorted_candidates):
            # Refine ranking with NCD only if structural scores are very close (tie-breaking)
            final_score = raw_score
            reasoning = f"Stability: {raw_score:.4f}. "
            
            if i < len(sorted_candidates) - 1:
                next_score = sorted_candidates[i+1][1]
                if abs(raw_score - next_score) < 0.01:
                    # Tie-breaker: NCD
                    ncd_val = self._ncd(prompt, cand)
                    # Lower NCD is better (more similar), so we add (1-ncd) as a tiny bonus
                    tie_break_bonus = (1.0 - ncd_val) * 0.001
                    final_score += tie_break_bonus
                    reasoning += f"NCD tie-break applied. "
            
            # Normalize final score to 0-1 range relative to the batch
            norm_score = (final_score - min_score) / score_range if score_range > 0 else 0.5
            
            ranked_results.append({
                "candidate": cand,
                "score": float(norm_score),
                "reasoning": reasoning
            })
            
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural stability.
        1.0 = Highly stable (matches logical constraints).
        0.0 = Highly unstable (diverges from constraints).
        """
        prompt_sig = self._structural_signature(prompt)
        answer_sig = self._structural_signature(answer)
        
        divergence = self._compute_divergence(prompt_sig, answer_sig)
        
        # Base confidence from stability
        alpha = 0.5
        base_conf = math.exp(-alpha * divergence)
        
        # Penalty for length mismatch if prompt is long (indicates missing reasoning)
        if prompt_sig['len'] > 20 and answer_sig['len'] < 5:
            base_conf *= 0.5
            
        # Boost if numbers match
        p_nums = set(prompt_sig['nums'])
        a_nums = set(answer_sig['nums'])
        if p_nums and a_nums and p_nums.intersection(a_nums):
            base_conf = min(1.0, base_conf + 0.3)
            
        return float(max(0.0, min(1.0, base_conf)))