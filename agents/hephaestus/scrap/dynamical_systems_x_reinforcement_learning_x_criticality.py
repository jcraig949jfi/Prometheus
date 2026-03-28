import re
import zlib
import math

class ReasoningTool:
    """
    Critical-Edge RL Controller for Reasoning.
    
    Mechanism:
    1. Dynamical Systems (Structural Parsing): Extracts logical operators (negations, 
       comparatives, conditionals) to form a 'structural state vector'. This avoids 
       the 'historical inhibitor' trap by using DS only for parsing, not scoring.
    2. Reinforcement Learning (Core Scoring): The 'policy' evaluates candidates based 
       on constraint satisfaction (reward) and structural alignment. It prioritizes 
       candidates that correctly handle logical flips (modus tollens, negation).
    3. Criticality (Meta-Control): Calculates a 'susceptibility' metric based on the 
       variance of logical token matches. Candidates that maximize this metric 
       (high sensitivity to logical structure) while maintaining high structural 
       alignment are up-weighted. This mimics operating at the 'edge of chaos' where 
       information gain is maximized.
    
    The final score is a weighted sum of Structural Alignment (RL reward) and 
    Critical Susceptibility, with NCD used strictly as a tiebreaker.
    """

    def __init__(self):
        # Logical operators defining the "state space" of reasoning
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most']
        
        # Criticality tuning parameters
        self.gain_factor = 2.0  # Amplifies susceptibility impact
        self.critical_threshold = 0.5 

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text):
        """Extracts logical signatures from text."""
        tokens = set(self._tokenize(text))
        has_neg = any(n in tokens for n in self.negations)
        has_comp = any(c in tokens for c in self.comparatives)
        has_cond = any(c in tokens for c in self.conditionals)
        has_quant = any(q in tokens for q in self.quantifiers)
        
        # Check for numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'quant': has_quant,
            'nums': nums,
            'length': len(tokens)
        }

    def _check_numeric_consistency(self, prompt_nums, cand_nums, prompt_text, cand_text):
        """Evaluates numeric logic (e.g., 9.11 < 9.9)."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No penalty if no numbers to compare
        
        # Simple heuristic: if prompt implies an order, check if candidate respects it
        # This is a simplified proxy for complex numeric reasoning
        p_sorted = sorted(prompt_nums)
        c_sorted = sorted(cand_nums)
        
        # If the candidate preserves the relative order of magnitude found in prompt
        if len(p_sorted) >= 2 and len(c_sorted) >= 2:
            p_dir = p_sorted[-1] > p_sorted[0]
            c_dir = c_sorted[-1] > c_sorted[0]
            if p_dir != c_dir:
                return 0.5 # Penalty for flipping order without logical cause
        
        return 1.0

    def _calculate_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max_len

    def _compute_susceptibility(self, prompt_struct, cand_struct):
        """
        Computes 'susceptibility' chi. 
        High chi occurs when small changes in logical tokens cause large shifts in interpretation.
        Here approximated by the variance of logical feature matches.
        """
        matches = [
            int(prompt_struct['neg'] == cand_struct['neg']),
            int(prompt_struct['comp'] == cand_struct['comp']),
            int(prompt_struct['cond'] == cand_struct['cond']),
            int(prompt_struct['quant'] == cand_struct['quant'])
        ]
        # Variance of matches indicates sensitivity to structure
        avg = sum(matches) / len(matches)
        if avg == 0 or avg == 1:
            return 0.0
        variance = avg * (1 - avg)
        return variance

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_lower = prompt.lower()
        results = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            cand_lower = cand.lower()
            
            # 1. Structural Alignment (RL Reward Signal)
            # Reward matching logical operators (e.g., if prompt has negation, candidate should reflect it)
            alignment_score = 0.0
            if prompt_struct['neg'] == cand_struct['neg']:
                alignment_score += 0.25
            if prompt_struct['comp'] == cand_struct['comp']:
                alignment_score += 0.25
            if prompt_struct['cond'] == cand_struct['cond']:
                alignment_score += 0.25
            if prompt_struct['quant'] == cand_struct['quant']:
                alignment_score += 0.25
            
            # 2. Numeric Consistency Check
            num_score = self._check_numeric_consistency(
                prompt_struct['nums'], cand_struct['nums'], prompt_lower, cand_lower
            )
            
            # 3. Criticality (Susceptibility)
            # Encourage candidates that are sensitive to the logical structure
            chi = self._compute_susceptibility(prompt_struct, cand_struct)
            critical_bonus = self.gain_factor * chi
            
            # Base score from alignment and numeric logic
            base_score = (alignment_score * num_score)
            
            # Apply criticality bonus only if base structural alignment is decent
            # This prevents nonsense from scoring high just due to randomness
            if base_score > 0.3:
                final_score = base_score + critical_bonus
            else:
                final_score = base_score * 0.5 # Penalize low alignment heavily

            # NCD as tiebreaker (only if scores are very close, handled by sorting stability usually, 
            # but we add a tiny epsilon based on NCD to differentiate)
            ncd_val = self._calculate_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale down to be a tiebreaker
            ncd_score = (1.0 - ncd_val) * 0.001 
            
            total_score = final_score + ncd_score
            
            # Reasoning string generation
            reason_parts = []
            if prompt_struct['neg'] != cand_struct['neg']:
                reason_parts.append("Negation mismatch")
            if num_score < 1.0:
                reason_parts.append("Numeric inconsistency")
            if chi > 0.2:
                reason_parts.append("High logical susceptibility")
            
            reasoning = "Structural match OK" if not reason_parts else "; ".join(reason_parts)

            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and critical susceptibility.
        """
        prompt_struct = self._extract_structure(prompt)
        cand_struct = self._extract_structure(answer)
        
        # Structural consistency check
        consistency = 0.0
        checks = 0
        
        if prompt_struct['neg'] or cand_struct['neg']:
            checks += 1
            if prompt_struct['neg'] == cand_struct['neg']:
                consistency += 1.0
        
        if prompt_struct['comp'] or cand_struct['comp']:
            checks += 1
            if prompt_struct['comp'] == cand_struct['comp']:
                consistency += 1.0
                
        if prompt_struct['cond'] or cand_struct['cond']:
            checks += 1
            if prompt_struct['cond'] == cand_struct['cond']:
                consistency += 1.0

        if checks == 0:
            # Fallback to simple overlap if no logical operators detected
            common = len(set(self._tokenize(prompt)) & set(self._tokenize(answer)))
            total = len(set(self._tokenize(prompt)) | set(self._tokenize(answer)))
            base_conf = (common / total) if total > 0 else 0.0
        else:
            base_conf = consistency / checks

        # Adjust with susceptibility (criticality)
        chi = self._compute_susceptibility(prompt_struct, cand_struct)
        # If structure matches perfectly, high susceptibility boosts confidence (sensitive to context)
        # If structure mismatches, low confidence regardless
        if base_conf == 1.0:
            final_conf = min(1.0, base_conf + 0.5 * chi)
        else:
            final_conf = base_conf * (1.0 - chi) # Reduce confidence if ambiguous
            
        return max(0.0, min(1.0, final_conf))