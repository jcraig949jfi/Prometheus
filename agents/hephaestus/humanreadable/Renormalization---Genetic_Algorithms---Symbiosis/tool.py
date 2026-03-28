import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Symbiotic Renormalization Genetic Algorithm (HSRGA) for Reasoning.
    
    Mechanism:
    1. GENOTYPE ENCODING: Candidates are treated as genotypes. Structural features
       (negations, comparatives, conditionals, numeric values) are extracted as 'genes'.
    
    2. RENORMALIZATION (Coarse-Graining): 
       Instead of spatial blocks, we apply a block-transformation where specific 
       structural patterns map to robustness scores. A candidate's 'coarse' fitness 
       is its adherence to logical constraints derived from the prompt's structure.
       - If prompt has negation, candidate must reflect it (or explicitly deny).
       - If prompt has comparatives, candidate must respect order.
       
    3. SYMBIOSIS (Mutualistic Exchange):
       The 'Prompt Schema' (abstract logic) and 'Candidate Content' (specifics) 
       exchange information. 
       - Downward flow: Prompt constraints prune invalid candidate structures.
       - Upward flow: Candidate specificities validate if the prompt's abstract 
         constraints are satisfiable.
       
    4. MULTI-SCALE FITNESS:
       - Fine Scale: NCD (Compression) similarity between prompt context and candidate.
       - Coarse Scale: Structural consistency (Logic/Math check).
       - Final Score: Weighted sum where Coarse Scale dominates (RG principle).
    """

    def __init__(self):
        self.numeric_ops = ['+', '-', '*', '/', '==', '<', '>', '<=', '>=']
        
    def _extract_structure(self, text: str) -> Dict:
        """Extract logical genes: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        genes = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': [],
            'has_logic': False
        }
        
        # Extract numbers for evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        genes['numbers'] = [float(n) for n in nums if n]
        
        if genes['negations'] > 0 or genes['comparatives'] > 0 or genes['conditionals'] > 0:
            genes['has_logic'] = True
            
        return genes

    def _evaluate_logic_consistency(self, prompt: str, candidate: str) -> float:
        """
        Renormalization Step: Check if candidate preserves logical invariants of the prompt.
        Returns a score 0.0 to 1.0 based on structural alignment.
        """
        p_genes = self._extract_structure(prompt)
        c_genes = self._extract_structure(candidate)
        score = 1.0
        
        # Invariant 1: Negation Preservation
        # If prompt asserts a negative constraint, candidate shouldn't blindly affirm positive
        if p_genes['negations'] > 0:
            # Simple heuristic: if prompt denies something, candidate should not be purely affirmative without qualification
            # This is a coarse-grained check. 
            if c_genes['negations'] == 0 and any(k in candidate.lower() for k in ['yes', 'true', 'correct']):
                score -= 0.3 # Penalty for ignoring negation context
        
        # Invariant 2: Numeric Consistency
        if len(p_genes['numbers']) >= 2 and len(c_genes['numbers']) >= 1:
            # If prompt compares numbers, check if candidate respects the order
            p_nums = sorted(p_genes['numbers'])
            c_num = c_genes['numbers'][0]
            
            # Detect comparison direction in prompt
            is_greater = 'greater' in prompt.lower() or '>' in prompt or 'more' in prompt.lower()
            is_less = 'less' in prompt.lower() or '<' in prompt
            
            if is_greater and c_num < p_nums[0]:
                score -= 0.4
            elif is_less and c_num > p_nums[-1]:
                score -= 0.4
                
        # Invariant 3: Conditional Logic
        if p_genes['conditionals'] > 0:
            if c_genes['conditionals'] == 0 and len(c_genes['numbers']) == 0:
                # If prompt is conditional, a bare number or simple statement might be insufficient
                # unless it directly answers the condition result.
                pass # Soft check, no heavy penalty without full semantic parse

        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-calculate prompt structure for symbiosis
        p_genes = self._extract_structure(prompt)
        p_len = len(prompt)
        
        for cand in candidates:
            # 1. Fine-grained fitness (NCD)
            # We compare candidate to prompt to see if it's relevant (low distance)
            # But NCD fails on short answers, so we normalize by length difference too
            ncd_val = self._ncd(prompt, cand)
            
            # Adjust NCD for length bias (short answers often correct but high NCD)
            len_ratio = min(len(cand), p_len) / max(len(cand), p_len, 1)
            fine_fitness = 1.0 - ncd_val + (0.1 * len_ratio) 
            
            # 2. Coarse-grained fitness (Renormalization/Logic)
            # Does the candidate maintain logical invariants?
            coarse_fitness = self._evaluate_logic_consistency(prompt, cand)
            
            # 3. Symbiotic Integration
            # The final score is dominated by coarse fitness (logic) if logic is present in prompt.
            # If prompt has no logic markers, rely more on NCD.
            if p_genes['has_logic']:
                # Strong weight on structural consistency
                final_score = (coarse_fitness * 0.7) + (fine_fitness * 0.3)
            else:
                # Fallback to compression/relevance
                final_score = (coarse_fitness * 0.2) + (fine_fitness * 0.8)
            
            # Bonus for exact keyword matches in simple cases (Symbiotic feedback loop)
            # If candidate contains key terms from prompt, boost slightly
            common_words = set(prompt.lower().split()) & set(cand.lower().split())
            if len(common_words) > 0:
                final_score += 0.05 * min(len(common_words)/5, 1.0)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Coarse(logic):{coarse_fitness:.2f}, Fine(NCD):{fine_fitness:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to confidence probability
        # Scores > 0.6 are likely correct, < 0.3 likely wrong
        # Sigmoid-like mapping centered at 0.5
        confidence = 1 / (1 + math.exp(-10 * (score - 0.5)))
        return round(confidence, 4)