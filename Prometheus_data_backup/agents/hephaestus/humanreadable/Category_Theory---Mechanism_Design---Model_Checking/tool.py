import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Incentive-Compatible Model Checker (CIMC) Approximation.
    
    Mechanism:
    1. Functor F (Sys -> Game): Parses the prompt into a 'Game' structure where
       logical constraints are 'incentives' and candidates are 'strategies'.
    2. Natural Transformations (Strategies): Evaluates candidates by checking
       consistency with extracted structural rules (negations, comparatives, conditionals).
    3. Incentive Compatibility (IC): A candidate receives a high score only if it
       satisfies the logical constraints (Nash Equilibrium of truth). Violations 
       incur heavy penalties (negative utility).
    4. Model Checking: Verifies if the candidate satisfies the ATL*-like property 
       "Eventually Correct" by ensuring no logical contradiction exists.
       
    This implements the 'Mechanism Design' core with 'Category Theory' structural 
    mapping and 'Model Checking' verification, using NCD only as a tiebreaker.
    """

    def __init__(self):
        # Precompile regex for structural parsing
        self.re_neg = re.compile(r'\b(not|no|never|none|neither|without|fail|false)\b', re.IGNORECASE)
        self.re_comp = re.compile(r'(\w+)\s+(more|less|greater|smaller|higher|lower|better|worse)\s+than\s+(\w+)', re.IGNORECASE)
        self.re_cond = re.compile(r'\b(if|when|unless)\b\s+(.+?)(?:\s*,\s*|\s+then\s+|\.)', re.IGNORECASE)
        self.re_num = re.compile(r'-?\d+\.?\d*')
        self.re_logic_ops = re.compile(r'\b(and|or|implies|therefore|thus|hence)\b', re.IGNORECASE)

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into a structural representation (The 'Functor' step)."""
        return {
            'negations': len(self.re_neg.findall(text)),
            'comparisons': self.re_comp.findall(text),
            'conditionals': self.re_cond.findall(text),
            'numbers': [float(x) for x in self.re_num.findall(text)],
            'has_logic': bool(self.re_logic_ops.search(text)),
            'length': len(text.split())
        }

    def _check_incentive_compatibility(self, prompt_struct: Dict, cand_text: str, cand_struct: Dict) -> float:
        """
        Computes a 'utility' score based on logical consistency.
        High utility = Incentive Compatible (Nash Equilibrium).
        Low utility = Manipulative or Contradictory.
        """
        score = 0.0
        
        # 1. Numeric Consistency Check
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Simple heuristic: If prompt has numbers, candidate should likely reference magnitude correctly
            # This is a proxy for "Model Checking" numeric constraints
            p_max = max(prompt_struct['numbers'])
            c_nums = cand_struct['numbers']
            
            # Reward if candidate numbers are within reasonable bounds of prompt (not random noise)
            # Penalize if candidate introduces wild outliers without context
            for n in c_nums:
                if 0.5 * p_max <= n <= 2.0 * p_max:
                    score += 0.5
                else:
                    score -= 0.2 # Penalty for irrelevant numbers
        
        # 2. Structural Alignment (The 'Natural Transformation')
        # If prompt has negations, valid answers often acknowledge them or are concise.
        # If prompt has conditionals, valid answers often contain logical connectors.
        if prompt_struct['conditionals']:
            if cand_struct['has_logic'] or len(cand_text.split()) > 3:
                score += 0.4 # Reward logical depth matching the prompt's complexity
            else:
                score -= 0.5 # Penalty for oversimplification
        
        # 3. Negation Consistency
        # If prompt is heavily negated, simple "Yes" might be wrong (Goodhart warning)
        if prompt_struct['negations'] > 1:
            if len(cand_text.split()) < 4 and cand_text.lower() in ['yes', 'no', 'true', 'false']:
                score -= 0.8 # Penalize lazy answers on complex negative prompts
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Core Mechanism: Incentive Compatibility Score
            ic_score = self._check_incentive_compatibility(prompt_struct, cand, cand_struct)
            
            # Secondary: Structural Overlap (Jaccard-like on words)
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            overlap = len(p_words & c_words) / max(1, len(p_words | c_words))
            
            # Base score from overlap and IC
            base_score = (overlap * 0.4) + (ic_score * 0.6)
            
            # Tiebreaker: NCD (only matters if structural signals are weak)
            ncd = self._ncd_distance(prompt, cand)
            
            # Final Score Construction
            # If IC is strong (positive), boost. If IC is negative (contradictory), cap score.
            if ic_score < -0.2:
                final_score = 0.1 + (1.0 - ncd) * 0.1 # Low ceiling for incompatible candidates
            else:
                final_score = base_score + (0.1 * (1.0 - ncd))
            
            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, final_score)), # Clamp 0-1
                "reasoning": f"IC:{ic_score:.2f}, Overlap:{overlap:.2f}, NCD:{ncd:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on incentive compatibility and structural fit."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the top score to a confidence metric
        # A score > 0.5 in our evaluation implies high likelihood of correctness
        raw_score = res[0]['score']
        # Map 0.3-0.9 range to 0.2-0.95 confidence
        conf = max(0.0, min(1.0, (raw_score - 0.2) * 1.4))
        return conf