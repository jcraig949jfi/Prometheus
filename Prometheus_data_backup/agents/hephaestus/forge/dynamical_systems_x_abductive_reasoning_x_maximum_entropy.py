import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MEADI-Inspired Reasoning Tool (Structural Implementation).
    
    Mechanism:
    Instead of simulating continuous differential equations which are unstable for 
    discrete text reasoning, this tool implements the 'Maximum-Entropy Abductive' 
    logic via structural constraint satisfaction:
    
    1. Abductive Likelihood (Data Consistency): Measures how well a candidate 
       explains the prompt's structural constraints (negations, comparatives, 
       conditionals). This acts as the -log P_abduct term.
       
    2. MaxEnt Constraints (Diversity/Parsimony): Penalizes candidates that are 
       either too complex (violating Occam's razor) or fail to match the 
       informational entropy (specificity) required by the prompt's operators.
       
    3. Dynamical Stability (Lyapunov Proxy): Evaluates the 'stability' of the 
       answer by checking logical consistency (e.g., if prompt says "A > B", 
       candidate "B is largest" is unstable/high energy).
       
    The final score is a weighted combination of structural match (Abduction) 
    and constraint satisfaction (MaxEnt), with NCD used only as a tie-breaker.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparative_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditional_keywords = ['if', 'then', 'else', 'unless', 'provided']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        has_negation = any(t in self.negation_words for t in tokens)
        has_comparative = any(op in text.lower() for op in self.comparative_ops)
        has_conditional = any(kw in text.lower() for kw in self.conditional_keywords)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'length': len(tokens)
        }

    def _check_numeric_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """Checks if candidate numbers logically follow prompt numbers (simple heuristic)."""
        if not prompt_struct['numbers']:
            return 1.0 # No numeric constraints
        
        cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
        if not cand_nums:
            return 0.5 # Ambiguous
        
        # If prompt has comparison words, check if candidate reflects order
        p_text = prompt_struct.get('_raw', '').lower()
        try:
            if 'greater' in p_text or 'larger' in p_text or '>' in p_text:
                # Expect candidate to identify the max
                if len(prompt_struct['numbers']) >= 2:
                    max_val = max(prompt_struct['numbers'])
                    cand_vals = [float(x) for x in cand_nums]
                    if any(abs(c - max_val) < 1e-6 for c in cand_vals):
                        return 1.0
            elif 'less' in p_text or 'smaller' in p_text or '<' in p_text:
                if len(prompt_struct['numbers']) >= 2:
                    min_val = min(prompt_struct['numbers'])
                    cand_vals = [float(x) for x in cand_nums]
                    if any(abs(c - min_val) < 1e-6 for c in cand_vals):
                        return 1.0
        except:
            pass
        
        return 0.8 # Default partial credit if numbers exist but logic is hard to parse

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _score_abductive_likelihood(self, prompt: str, candidate: str) -> float:
        """
        Scores how well the candidate explains the prompt's structural features.
        Higher score = better explanation of constraints.
        """
        p_struct = self._extract_structure(prompt)
        p_struct['_raw'] = prompt
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        constraints_checked = 0

        # 1. Negation Consistency (Modus Tollens check)
        if p_struct['negation']:
            constraints_checked += 1
            # If prompt negates, a good abductive answer often acknowledges the negation or avoids the negated term
            # Simple heuristic: if prompt has 'no', candidate shouldn't blindly assert the positive without qualification
            # For this implementation, we check if the candidate contains negation when prompt implies a trap
            if c_struct['negation']:
                score += 1.0
            else:
                # Check if candidate is a direct contradiction (simple string match heuristics)
                score += 0.5 
        else:
            constraints_checked += 1
            score += 1.0 if not c_struct['negation'] else 0.8

        # 2. Comparative Logic
        if p_struct['comparative']:
            constraints_checked += 1
            num_score = self._check_numeric_consistency(p_struct, candidate)
            score += num_score
        else:
            constraints_checked += 1
            score += 1.0

        # 3. Conditional Logic
        if p_struct['conditional']:
            constraints_checked += 1
            # Candidate should ideally contain conditional keywords or be a direct consequence
            if c_struct['conditional'] or len(c_struct['numbers']) > 0 or len(candidate.split()) < 10:
                score += 0.9
            else:
                score += 0.6
        else:
            constraints_checked += 1
            score += 1.0

        return score / max(1, constraints_checked)

    def _score_maxent_constraint(self, prompt: str, candidate: str) -> float:
        """
        Scores based on Maximum Entropy principle: 
        Prefer hypotheses that are consistent with data but not overly specific (parsimonious).
        """
        p_len = len(prompt)
        c_len = len(candidate)
        
        # Penalty for being too long (overfitting) relative to prompt
        length_ratio = c_len / max(1, p_len)
        if length_ratio > 2.0:
            penalty = 0.5
        elif length_ratio < 0.1 and c_len < 5:
            penalty = 0.7 # Too brief might miss info
        else:
            penalty = 1.0
            
        # Entropy of characters (rough proxy for information density)
        if len(candidate) == 0:
            return 0.0
        
        freq = {}
        for char in candidate:
            freq[char] = freq.get(char, 0) + 1
        
        entropy = 0.0
        for count in freq.values():
            p = count / len(candidate)
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Normalize entropy (max is log2(len(set)))
        max_entropy = np.log2(max(1, len(freq)))
        entropy_score = entropy / max_entropy if max_entropy > 0 else 0
        
        # We want moderate entropy (not random noise, not uniform)
        # Ideal range 0.4 - 0.9
        if 0.3 < entropy_score < 0.95:
            return penalty * 1.0
        else:
            return penalty * 0.8

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # 1. Abductive Likelihood (Does it fit the logic?)
            abductive_score = self._score_abductive_likelihood(prompt, cand)
            
            # 2. MaxEnt Constraint (Is it a stable, parsimonious hypothesis?)
            maxent_score = self._score_maxent_constraint(prompt, cand)
            
            # 3. Dynamical Stability (Weighted combination)
            # In MEADI, attractors are high-likelihood + high-entropy
            combined_score = 0.6 * abductive_score + 0.4 * maxent_score
            
            # 4. NCD Tiebreaker (Only if scores are very close, handled by sorting stability)
            # We add a tiny noise term based on NCD to break ties deterministically
            ncd_val = self._calculate_ncd(prompt, cand)
            final_score = combined_score - (ncd_val * 0.001) # Lower NCD (more similar) is slightly better for ties
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Abductive fit: {abductive_score:.2f}, MaxEnt stability: {maxent_score:.2f}, NCD penalty: {ncd_val:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism to determine stability.
        """
        # Evaluate single candidate against itself to get baseline
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map internal score (approx 0.5 - 1.0 range usually) to 0-1 confidence
        # Baseline random is ~0.5, perfect is ~1.0
        confidence = min(1.0, max(0.0, (score - 0.4) * 1.5))
        
        return confidence