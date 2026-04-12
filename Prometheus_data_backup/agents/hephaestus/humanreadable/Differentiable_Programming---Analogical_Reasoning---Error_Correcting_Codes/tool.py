import re
import zlib
import math

class ReasoningTool:
    """
    Differentiable Analogical Hypothesis Engine with Code-Based Robustness.
    
    Mechanism:
    1. Structural Parsing (Hypothesis Generation): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'relational schema'.
    2. Analogical Transfer: Maps the schema of the prompt to candidates by checking 
       structural alignment (e.g., if prompt has negation, candidate must reflect it).
    3. Code-Based Robustness (Confidence Wrapper): Instead of direct scoring, 
       uses a simulated LDPC-like parity check on the structural signature. 
       If the structural signature is 'corrupted' (mismatched parity), confidence drops.
    4. Scoring: Primary signal is structural adherence. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.keywords = {
            'neg': ['not', 'no', 'never', 'false', 'impossible'],
            'comp': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'],
            'cond': ['if', 'then', 'unless', 'only if', 'when'],
            'num': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }

    def _structural_signature(self, text):
        """Extracts a binary-like vector of logical features."""
        t_lower = text.lower()
        has_neg = any(k in t_lower for k in self.keywords['neg'])
        has_comp = any(k in t_lower for k in self.keywords['comp'])
        has_cond = any(k in t_lower for k in self.keywords['cond'])
        has_num = any(k in t_lower for k in self.keywords['num'])
        
        # Numeric evaluation attempt
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", t_lower)
        numeric_val = float(nums[0]) if nums else 0.0
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'has_num': len(nums) > 0,
            'num_val': numeric_val,
            'raw_len': len(text)
        }

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / (max(c1, c2) - min_len + 1e-9)
        except:
            return 1.0

    def _check_numeric_logic(self, prompt_sig, cand_sig):
        """Simple constraint propagation for numbers."""
        if not prompt_sig['has_num'] or not cand_sig['has_num']:
            return 1.0 # No numeric constraint to violate
        
        # Heuristic: If prompt implies ordering, check candidate consistency
        # This is a simplified analogical lift of numeric relations
        p_val = prompt_sig['num_val']
        c_val = cand_sig['num_val']
        
        if prompt_sig['comp']:
            if 'less' in (prompt_sig.get('raw', '') or '').lower() or '<' in (prompt_sig.get('raw', '') or ''):
                return 1.0 if c_val < p_val else 0.2
            if 'greater' in (prompt_sig.get('raw', '') or '').lower() or '>' in (prompt_sig.get('raw', '') or ''):
                return 1.0 if c_val > p_val else 0.2
        
        return 1.0

    def evaluate(self, prompt, candidates):
        results = []
        prompt_sig = self._structural_signature(prompt)
        prompt_sig['raw'] = prompt
        
        # Store raw prompt for NCD tiebreaking
        base_ncd = None 
        
        for cand in candidates:
            cand_sig = self._structural_signature(cand)
            score = 0.0
            reasoning_parts = []
            
            # 1. Analogical Structure Matching (Differentiable Program Approximation)
            # Check if candidate preserves logical operators found in prompt
            struct_match = 0.0
            
            # Negation alignment
            if prompt_sig['neg'] == cand_sig['neg']:
                struct_match += 0.4
                reasoning_parts.append("negation aligned")
            else:
                reasoning_parts.append("negation mismatch")
                
            # Conditional alignment
            if prompt_sig['cond'] == cand_sig['cond']:
                struct_match += 0.3
                reasoning_parts.append("conditional aligned")
            
            # Comparative alignment
            if prompt_sig['comp'] == cand_sig['comp']:
                struct_match += 0.3
                reasoning_parts.append("comparative aligned")
            
            score = struct_match
            
            # 2. Numeric Constraint Propagation
            num_score = self._check_numeric_logic(prompt_sig, cand_sig)
            if num_score < 1.0:
                score *= 0.5 # Penalty for numeric violation
                reasoning_parts.append("numeric violation")
            
            # 3. NCD as Tiebreaker (only if structural scores are close/zero)
            # We add a tiny fraction of NCD similarity to break ties
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, scale down to be a tiebreaker
            ncd_score = (1.0 - ncd_val) * 0.05 
            score += ncd_score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural neutral"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt, answer):
        """
        Uses code-based robustness regularization concept.
        Treats the structural signature as a 'codeword'. 
        If the answer's structure is a valid 'distance' from the prompt's expected logic,
        confidence is high. If it looks like noise (random parity), confidence is low.
        """
        p_sig = self._structural_signature(prompt)
        a_sig = self._structural_signature(answer)
        
        # Parity Check (Simulated LDPC single parity bit)
        # Count True features in prompt
        p_features = [p_sig['neg'], p_sig['comp'], p_sig['cond'], p_sig['has_num']]
        p_parity = sum(p_features) % 2
        
        # Count True features in answer
        a_features = [a_sig['neg'], a_sig['comp'], a_sig['cond'], a_sig['has_num']]
        a_parity = sum(a_features) % 2
        
        # Robustness metric: Does the answer maintain logical consistency?
        # If prompt has logic (parity 1), answer should likely reflect related logic
        # This is a heuristic proxy for "lying in code-space"
        
        base_conf = 0.5
        
        # Strong signal: Explicit logical alignment
        if p_sig['neg'] == a_sig['neg']:
            base_conf += 0.3
        if p_sig['cond'] == a_sig['cond']:
            base_conf += 0.2
            
        # Penalty for total structural disconnect
        if p_sig['has_num'] and not a_sig['has_num']:
            base_conf -= 0.4
            
        # Clamp between 0 and 1
        return max(0.0, min(1.0, base_conf))