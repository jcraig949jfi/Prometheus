import re
import zlib
import math

class ReasoningTool:
    """
    Pragmatic Compositional Minimum Description Length (PC-MDL) Tool.
    
    Mechanism:
    1. Structural Parsing (Pragmatism): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt. This acts as the 'reward' signal 
       for how well a candidate fits the pragmatic structure of the query.
    2. Compositional Grammar (Compositionality): Evaluates candidates based on the 
       presence of key structural tokens found in the prompt.
    3. MDL Surrogate (Kolmogorov): Uses NCD only as a tie-breaker to penalize 
       unnecessary complexity when structural scores are equal.
       
    The final score balances structural adherence (high reward) against description 
    length (complexity penalty), implementing the L = description_length - lambda * reward 
    objective via a normalized scoring function.
    """

    def __init__(self):
        # Structural keywords for pragmatic parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['less', 'fewer', 'smaller', 'shorter', 'lower', 'before', 'earlier']
        self.maximals = ['most', 'largest', 'greatest', 'highest', 'longest', 'after', 'latest', 'max']
        self.minimals = ['least', 'smallest', 'lowest', 'shortest', 'min']
        self.conditionals = ['if', 'then', 'unless', 'except']
        self.booleans = ['yes', 'no', 'true', 'false']

    def _normalize(self, text):
        return text.lower().strip()

    def _extract_numbers(self, text):
        # Extract floating point numbers for numeric evaluation
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structure(self, prompt, candidate):
        """
        Pragmatic Truth Value: Measures how well the candidate satisfies 
        structural constraints extracted from the prompt.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.0
        checks = 0

        # 1. Negation Consistency
        has_negation = any(n in p_low.split() for n in self.negations)
        candidate_negated = any(n in c_low.split() for n in self.negations)
        
        if has_negation:
            checks += 1
            # If prompt implies negation, candidate should ideally reflect it or answer appropriately
            # Heuristic: If prompt asks "What is not X", and candidate contains negation, boost.
            # More robust: If prompt is a negative constraint, ensure candidate doesn't violate it.
            # Simplified for this tool: Reward matching negation status if the prompt is a negative query.
            if any(q in p_low for q in ['not', 'no ', 'never']):
                if candidate_negated:
                    score += 1.0
                else:
                    # Penalty for missing negation in a negative context (risky but pragmatic)
                    score -= 0.5 
            else:
                score += 0.5 # Neutral boost if negation exists but context is complex

        # 2. Comparative/Ordinal Logic
        if any(c in p_low for c in self.comparatives + self.minimals):
            checks += 1
            # If prompt asks for "least/smallest", prefer candidates with smaller numbers
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            if p_nums and c_nums:
                # Heuristic: If prompt implies minimization, smaller number in candidate is better
                if min(c_nums) <= min(p_nums): 
                    score += 1.0
            elif any(w in c_low for w in self.minimals + self.comparatives):
                score += 0.8 # Verbal match for minimization

        if any(c in p_low for c in self.maximals):
            checks += 1
            p_nums = self._extract_numbers(prompt)
            c_nums = self._extract_numbers(candidate)
            if p_nums and c_nums:
                if max(c_nums) >= max(p_nums):
                    score += 1.0
            elif any(w in c_low for w in self.maximals):
                score += 0.8

        # 3. Conditional/Constraint Propagation
        if any(c in p_low for c in self.conditionals):
            checks += 1
            # Reward candidates that acknowledge conditions or provide definitive boolean answers
            if any(b in c_low for b in self.booleans) or len(c_low.split()) > 3:
                score += 0.5

        # Default boost for non-empty, coherent answers
        if len(candidate.strip()) > 0:
            score += 0.1
            
        return score / (checks + 1) if checks > 0 else 0.5

    def _ncd(self, s1, s2):
        """Normalized Compression Distance as a complexity tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_len = len(prompt)
        
        # Pre-calculate prompt structural features
        p_struct_score = 0.0 
        # (Internal baseline not strictly needed, we compare candidates relative to prompt)

        for cand in candidates:
            # 1. Pragmatic Reward (Structural Fit)
            # How well does the candidate fit the logical structure of the prompt?
            pragmatic_reward = self._check_structure(prompt, cand)
            
            # 2. Description Length Penalty (Complexity)
            # Shorter is generally better (MDL), but we normalize by prompt length
            # to avoid penalizing necessary verbosity.
            cand_len = len(cand)
            complexity_penalty = cand_len / (prompt_len + 1) 
            
            # 3. Combined Score (PC-MDL Objective)
            # Score = Reward - Lambda * Complexity
            # Lambda tuned to ensure structural fit dominates, length is tiebreaker
            lambda_val = 0.1
            base_score = pragmatic_reward - (lambda_val * complexity_penalty)
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Pragmatic fit: {pragmatic_reward:.2f}, Complexity penalty: {complexity_penalty:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are extremely close (floating point epsilon)
        # This implements the "NCD as tiebreaker" requirement strictly
        final_results = []
        if len(results) > 1:
            # Group by rounded score to find ties
            current_group = []
            last_score = None
            
            # Simple bubble sort for tie-breaking within groups if needed, 
            # but here we just apply NCD as a secondary sort key for the whole list
            # to ensure deterministic ordering where primary scores match.
            # Since we need to beat NCD baseline, we only use NCD to break ties.
            
            # Refining sort: Primary = Score, Secondary = -NCD (lower NCD is better similarity to prompt logic)
            # Actually, for reasoning, lower NCD between Prompt+Candidate often implies 
            # the candidate is a direct continuation or logical subset.
            
            def ncd_key(item):
                # Lower is better for NCD
                return self._ncd(prompt, item["candidate"])

            # Stable sort: First by NCD (ascending), then by Score (descending)
            # But we want Score to dominate. 
            # Python sort is stable. Sort by NCD first (least important), then Score (most important).
            results.sort(key=lambda x: ncd_key(x)) 
            results.sort(key=lambda x: x["score"], reverse=True)

        for r in results:
            # Format reasoning string to be concise
            r["reasoning"] = f"Structural match and MDL balance. {r['reasoning']}"
            final_results.append(r)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and compression.
        """
        # 1. Structural Check
        struct_score = self._check_structure(prompt, answer)
        
        # 2. Complexity Check (Is the answer absurdly long compared to prompt?)
        len_ratio = len(answer) / (len(prompt) + 1)
        complexity_factor = 1.0 if len_ratio < 2.0 else 1.0 / len_ratio
        
        # 3. NCD Check (Similarity to prompt context)
        ncd_val = self._ncd(prompt, answer)
        # NCD is 0 (identical) to ~2 (very different). 
        # We want low NCD for high confidence in 'continuation' tasks, 
        # but for QA, low NCD might just mean echoing. 
        # We rely mostly on struct_score.
        
        # Combine: Weighted average favoring structural logic
        confidence = (0.7 * struct_score) + (0.3 * complexity_factor * (1.0 - min(ncd_val, 1.0)))
        
        return max(0.0, min(1.0, confidence))