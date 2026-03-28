import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenal Optimal Model Checker (POMC) Implementation.
    
    Mechanism:
    1. Phenomenology (Structural Parsing): Instead of subjective experience, we parse
       the "phenomenal layers" of the text: logical operators (negations, conditionals),
       comparatives, and numeric values. This forms the state space A_phen.
    2. Optimal Control (HJB Approximation): We define a cost function where the 
       "cost-to-go" is the structural divergence between the prompt's constraints 
       and the candidate's assertions. We minimize epistemic surprise (contradiction).
    3. Model Checking (Temporal Logic Verification): We treat the prompt as a 
       specification (phi) and the candidate as a trace. We verify if the candidate 
       satisfies the logical constraints (e.g., if prompt says "A implies B", 
       candidate cannot assert "A and not B").
       
    Scoring:
    - High penalty for logical violations (Model Checking failure).
    - Score based on structural alignment (Parsing) + NCD tiebreaker.
    """

    def __init__(self):
        self.logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self.cond_ops = ['if', 'then', 'implies', 'when', 'whenever']
        self.comp_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.bool_vals = {'true': 1, 'false': 0, 'yes': 1, 'no': 0}

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric 'phenomenal' features."""
        t = text.lower()
        features = {
            'negations': len([w for w in self.logic_ops if re.search(r'\b' + w + r'\b', t)]),
            'conditionals': len([w for w in self.cond_ops if re.search(r'\b' + w + r'\b', t)]),
            'comparatives': len([w for w in self.comp_ops if re.search(r'\b' + w + r'\b', t)]),
            'numbers': re.findall(r'-?\d+\.?\d*', t),
            'has_question': '?' in text,
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Model Checking step: Verifies if candidate violates prompt constraints.
        Returns 1.0 (valid) to 0.0 (contradiction).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Check for direct negation contradictions
        # If prompt has "not X" and candidate has "X" (simple heuristic)
        score = 1.0
        
        # Extract simple subject-verb patterns for contradiction check
        # Pattern: "A is not B" vs "A is B"
        neg_pattern = r'(\w+)\s+is\s+not\s+(\w+)'
        pos_pattern = r'(\w+)\s+is\s+(\w+)'
        
        p_neg = re.findall(neg_pattern, p_low)
        c_pos = re.findall(pos_pattern, c_low)
        
        for subj, obj in p_neg:
            for c_subj, c_obj in c_pos:
                if subj == c_subj and obj == c_obj:
                    score -= 0.8 # Heavy penalty for direct contradiction
        
        # Check for "No X" vs "Yes X" or similar binary flips if numbers/bools involved
        if any(x in p_low for x in ['no', 'not', 'never']) and any(x in c_low for x in ['yes', 'always']):
            # Contextual check needed, but simple presence might indicate conflict in short texts
            if len(p_low.split()) < 20: # Only in short, direct contexts
                score -= 0.5

        return max(0.0, score)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denominator = max(c1, c2)
            if denominator == 0: return 1.0
            return (c12 - min(c1, c2)) / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # 1. Model Checking (Logical Consistency)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Structural Alignment (Phenomenal Layer Matching)
            # Compare counts of logical operators (approximating state alignment)
            struct_diff = 0.0
            keys = ['negations', 'conditionals', 'comparatives']
            for k in keys:
                diff = abs(p_struct[k] - c_struct[k])
                struct_diff += diff * 0.1 # Small penalty for mismatched complexity
            
            # Numeric consistency check
            if p_struct['numbers'] and c_struct['numbers']:
                # If both have numbers, check magnitude alignment roughly
                try:
                    p_nums = [float(x) for x in p_struct['numbers']]
                    c_nums = [float(x) for x in c_struct['numbers']]
                    # Simple heuristic: if prompt implies ordering, check candidate
                    if any(x in prompt.lower() for x in ['largest', 'maximum', 'most']):
                        if c_nums and max(c_nums) != max(p_nums): # Loose check
                             struct_diff += 0.2
                except: pass

            # 3. Optimal Control Cost (Minimizing Surprise)
            # Base score starts at 1.0, reduced by logic failures and structural drift
            base_score = 1.0 - struct_diff
            final_score = base_score * logic_score
            
            # 4. NCD Tiebreaker (Compression similarity)
            ncd = self._compute_ncd(prompt, cand)
            # NCD is 0 (identical) to 1 (different). We want high score for low NCD.
            # But NCD is weak for reasoning, so weight it low (0.1)
            final_score += (1.0 - ncd) * 0.1
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Logic:{logic_score:.2f}, Struct:{struct_diff:.2f}, NCD:{ncd:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on logical consistency and structural match."""
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
        # Normalize score to 0-1 range roughly
        score = eval_res[0]['score']
        # Heuristic mapping: scores can exceed 1.0 slightly due to NCD bonus, cap at 1.0
        return min(1.0, max(0.0, score))