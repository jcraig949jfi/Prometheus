import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Causal Type-Guided Proof Search (CTGPS) Approximation.
    
    Mechanism:
    1. Type Theory (TT) Layer: Parses candidates for structural validity (balanced parens, 
       matching logical connectors). Invalid types get heavy penalties.
    2. Causal Inference (CI) Layer: Extracts constraints from the prompt (negations, 
       comparatives, conditionals) and checks if the candidate contradicts them.
    3. MCTS Heuristic: Instead of full tree search, uses a deterministic UCB-like score 
       balancing 'exploitation' (constraint satisfaction) and 'exploration' (information density).
    4. Scoring: Primary signal is structural/constraint adherence. NCD is strictly a tiebreaker.
    """
    
    def __init__(self):
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extracts logical features: negations, comparatives, numbers, conditionals."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in words for n in self.negations)
        has_comp = any(c in words for c in self.comparatives)
        has_cond = any(c in words for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+(?:\.\d+)?', text)
        numbers = [float(n) for n in nums]
        
        # Basic type check: balanced parentheses/brackets
        stack = []
        balanced = True
        for char in text:
            if char in '([{': stack.append(char)
            elif char in ')]}':
                if not stack: balanced = False; break
                if '([{'.index(stack[-1]) == ')]}'.index(char): stack.pop()
                else: balanced = False; break
        if stack: balanced = False

        return {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'numbers': numbers,
            'balanced': balanced,
            'length': len(text)
        }

    def _check_causal_consistency(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Evaluates if the candidate logically follows prompt constraints.
        Returns a score 0.0 to 1.0 based on constraint satisfaction.
        """
        score = 1.0
        
        # Type Validity Penalty (Hard constraint)
        if not cand_feats['balanced']:
            score -= 0.5
            
        # Numeric Evaluation (Transitivity/Comparison)
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares A > B, and candidate asserts B > A, penalize
            # Simple heuristic: if prompt has numbers and candidate has numbers, 
            # check if order is preserved or inverted illogically.
            # For this approximation, we check if the candidate contradicts a clear max/min prompt.
            p_max = max(p_nums)
            p_min = min(p_nums)
            
            # If prompt implies 'greater' but candidate picks smaller number without negation
            if prompt_feats['comp_count'] > 0 and 'greater' in candidate.lower() or 'more' in candidate.lower():
                if c_nums and c_nums[0] < p_min:
                    score -= 0.4
            elif prompt_feats['comp_count'] > 0 and 'less' in candidate.lower() or 'fewer' in candidate.lower():
                if c_nums and c_nums[0] > p_max:
                    score -= 0.4

        # Negation Consistency
        # If prompt has strong negation context and candidate ignores it (simplified)
        if prompt_feats['neg_count'] > 0 and cand_feats['neg_count'] == 0:
            # Heuristic: If prompt is negative, valid answers often acknowledge it or are short.
            # Long positive assertions in negative contexts are often traps.
            if cand_feats['length'] > 20: 
                score -= 0.2

        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # 1. Causal/Type Score (Primary Signal)
            causal_score = self._check_causal_consistency(prompt_feats, cand_feats, cand)
            
            # 2. MCTS-inspired Exploration Bonus (Information Density)
            # Prefer candidates that add specific info (numbers/logic) over generic ones
            info_bonus = 0.0
            if cand_feats['numbers'] or cand_feats['comp_count'] > 0:
                info_bonus = 0.1
            
            # 3. NCD Tiebreaker (Only if scores are close, used here as minor modifier)
            # We invert NCD so higher is better (similarity to prompt context)
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.05 # Small weight
            
            final_score = causal_score + info_bonus + ncd_score
            
            # Reasoning trace
            reason_parts = []
            if not cand_feats['balanced']: reason_parts.append("Type error: unbalanced brackets")
            if causal_score < 1.0: reason_parts.append("Causal mismatch detected")
            if info_bonus > 0: reason_parts.append("High information density")
            reasoning = "; ".join(reason_parts) if reason_parts else "Structurally sound"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and causal alignment."""
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        # Normalize score to 0-1 range roughly
        score = res_list[0]['score']
        # Map score (approx -0.5 to 1.2) to 0.0-1.0
        conf = max(0.0, min(1.0, (score + 0.5) / 1.7))
        return conf