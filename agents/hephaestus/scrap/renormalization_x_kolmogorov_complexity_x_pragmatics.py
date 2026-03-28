import re
import zlib
import math

class ReasoningTool:
    """
    Renormalized MDL-Pragmatic Inference (RMPI) Approximation.
    
    Mechanism:
    1. Renormalization (Coarse-graining): Extracts structural invariants (negations, 
       comparatives, conditionals, numeric values) from the prompt and candidates, 
       ignoring surface-level noise. This represents the hierarchy of hypothesis spaces.
    2. Kolmogorov Complexity (L_model): Approximated via zlib compression length of the 
       candidate. Shorter, non-redundant answers are preferred (Occam's razor).
    3. Pragmatics (C_prag): Scores candidates based on Gricean maxims:
       - Relevance: Overlap of structural tokens with the prompt.
       - Quantity: Penalty for being too short (under-specified) or too long (over-specified).
       - Manner: Penalty for logical contradictions (e.g., repeating negations oddly).
    4. Integration: Computes a total score L = DataFit + lambda * (Complexity + PragmaticCost).
       The system selects the candidate minimizing this description length.
    """

    def __init__(self):
        # Structural patterns for "Renormalization" step
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', "n't"}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self.bool_yes = {'yes', 'true', 'correct', 'right'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong'}

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text):
        """Renormalization step: Extract high-level logical features."""
        tokens = set(self._tokenize(text))
        nums = re.findall(r'-?\d+\.?\d*', text)
        has_neg = bool(tokens & self.negation_words)
        has_comp = bool(tokens & self.comparatives)
        has_cond = bool(tokens & self.conditionals)
        return {
            'tokens': tokens,
            'nums': nums,
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'raw_len': len(text)
        }

    def _compute_kolmogorov_approx(self, text):
        """Approximate Kolmogorov complexity using zlib compression."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _pragmatic_score(self, prompt_struct, cand_struct, cand_text):
        """
        Compute pragmatic cost C_prag.
        Lower is better. Based on Gricean maxims.
        """
        cost = 0.0
        
        # 1. Relevance: Does it share structural features?
        # If prompt has numbers, candidate should ideally have numbers or be a direct boolean answer
        prompt_nums = prompt_struct['nums']
        cand_nums = cand_struct['nums']
        
        if prompt_nums:
            if not cand_nums:
                # Check if it's a boolean answer (acceptable simplification)
                cand_tokens = cand_struct['tokens']
                if not (cand_tokens & self.bool_yes) and not (cand_tokens & self.bool_no):
                    cost += 2.0  # Penalty for ignoring numeric context
        
        # 2. Quantity: Is the length appropriate?
        # Heuristic: If prompt is complex (many tokens), very short answers might be under-specified
        # unless they are boolean.
        if len(prompt_struct['tokens']) > 10 and cand_struct['raw_len'] < 3:
            cand_tokens = cand_struct['tokens']
            if not (cand_tokens & self.bool_yes) and not (cand_tokens & self.bool_no):
                cost += 1.5 # Too brief for complex prompt

        # 3. Manner/Consistency: Negation alignment
        # If prompt implies negation logic, ensure candidate doesn't contradict structurally
        # (Simplified check: if prompt is negative, and candidate is positive without context)
        if prompt_struct['neg'] and not cand_struct['neg']:
            # Soft penalty, as "No" is a valid negative response to a negative premise
            if 'yes' in cand_struct['tokens'] or 'true' in cand_struct['tokens']:
                cost += 1.0

        return cost

    def _structural_match_score(self, prompt_struct, cand_struct):
        """
        Primary scoring signal based on structural parsing.
        Returns a score where higher is better (to be negated in MDL).
        """
        score = 0.0
        p_tokens = prompt_struct['tokens']
        c_tokens = cand_struct['tokens']
        
        # 1. Numeric Consistency
        if prompt_struct['nums'] and cand_struct['nums']:
            # If both have numbers, reward presence. 
            # (Detailed arithmetic validation is hard without eval, but presence is a strong signal)
            score += 5.0
        elif not prompt_struct['nums'] and not cand_struct['nums']:
            score += 1.0 # Neutral
            
        # 2. Logical Operator Alignment
        if prompt_struct['neg'] and cand_struct['neg']:
            score += 2.0 # Reinforces negation logic
        elif prompt_struct['neg'] and not cand_struct['neg']:
            # Candidate lacks negation when prompt has it. 
            # Check if it's a direct denial ("No") which is valid, or an affirmation ("Yes") which might be wrong
            if 'yes' in c_tokens or 'true' in c_tokens:
                score -= 3.0 # Potential contradiction
        
        if prompt_struct['comp'] and cand_struct['comp']:
            score += 2.0
            
        if prompt_struct['cond'] and cand_struct['cond']:
            score += 1.5

        # 3. Keyword Overlap (Weighted)
        # Focus on content words, stop words less important
        common = p_tokens & c_tokens
        # Boost if common tokens include specific logical markers
        logic_overlap = common & (self.negation_words | self.comparatives | self.conditionals)
        score += len(logic_overlap) * 3.0
        score += len(common) * 0.5
        
        return score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD baseline for tie-breaking context
        # We won't use raw NCD, but the logic of compression difference
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Data Fit (Structural Match) -> Negative because we minimize L
            # We invert the match score: L_data = -Score
            data_fit_score = self._structural_match_score(prompt_struct, cand_struct)
            L_data = -data_fit_score
            
            # 2. Model Complexity (Kolmogorov)
            # L_model approximated by compressed size
            L_model = self._compute_kolmogorov_approx(cand) / 10.0 # Scale down
            
            # 3. Pragmatic Cost
            C_prag = self._pragmatic_score(prompt_struct, cand_struct, cand)
            
            # Total Description Length (Minimize this)
            # Lambda balances syntax vs pragmatics
            lambda_val = 1.5
            total_L = L_data + L_model + (lambda_val * C_prag)
            
            # Convert to a "score" where higher is better for the user
            # Invert and shift to positive domain
            final_score = 100.0 - total_L
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{data_fit_score:.1f}, Complexity:{L_model:.1f}, Pragmatic:{C_prag:.1f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the gap between the top candidate (the answer itself) and a theoretical 'bad' baseline.
        """
        # Evaluate against itself and a dummy wrong answer to gauge separation
        candidates = [answer, ""]
        if answer.lower() == "yes":
            candidates.append("no")
        elif answer.lower() == "no":
            candidates.append("yes")
        else:
            # Add a random perturbation as a competitor
            candidates.append(answer + " not")
            
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        top = ranked[0]
        if top['candidate'] != answer:
            # The answer provided isn't even the top choice among trivial variations
            return 0.1
            
        # Normalize score to 0-1 range heuristically
        # Base score around 100. 
        # If score > 120 -> 1.0, If score < 80 -> 0.0
        raw_score = top['score']
        confidence_val = (raw_score - 80.0) / 40.0
        return max(0.0, min(1.0, confidence_val))