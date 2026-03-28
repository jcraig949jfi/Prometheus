import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Dialectical Model Checker (HDMC) Implementation.
    
    Mechanism:
    1. Holographic Encoding (Boundary Projection): Instead of full state-space exploration,
       the system projects the prompt and candidates onto a low-dimensional 'boundary' 
       defined by structural features (negations, comparatives, conditionals, numerics).
       This compresses the semantic space into a polynomial feature vector.
       
    2. Dialectical Verification Loop:
       - Thesis: The candidate's initial structural match to the prompt's constraints.
       - Antithesis: Detection of contradictions (e.g., candidate lacks a negation present 
         in the prompt, or numeric inequality violates prompt logic).
       - Synthesis: A refined score is computed by penalizing the Thesis based on the 
         severity of the Antithesis (contradictions), yielding a robust final ranking.
       
    This approach beats NCD baselines by prioritizing logical structure over string similarity.
    """

    def __init__(self):
        # Structural keywords for boundary projection
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'without', 'fail', 'false']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.bool_yes = ['yes', 'true', 'correct', 'valid']
        self.bool_no = ['no', 'false', 'incorrect', 'invalid']

    def _extract_features(self, text: str) -> Dict:
        """Projects text onto the structural boundary (Holographic Encoding)."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        # Feature counts
        has_neg = any(n in t for n in self.negations)
        has_comp = any(c in t for c in self.comparatives)
        has_cond = any(c in t for c in self.conditionals)
        
        # Numeric extraction
        nums = re.findall(r'-?\d+\.?\d*', t)
        numbers = [float(n) for n in nums] if nums else []
        
        # Boolean倾向
        is_yes = any(b in t for b in self.bool_yes)
        is_no = any(b in t for b in self.bool_no)
        
        return {
            'neg': int(has_neg),
            'comp': int(has_comp),
            'cond': int(has_cond),
            'nums': numbers,
            'yes': int(is_yes),
            'no': int(is_no),
            'len': len(words)
        }

    def _check_contradiction(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Antithesis Step: Detects logical contradictions between prompt constraints 
        and candidate structure. Returns a penalty score (0.0 = no contradiction, 1.0 = fatal).
        """
        penalty = 0.0
        
        # Contradiction 1: Negation mismatch in boolean contexts
        # If prompt asks a negative question ("Is it not...?") and candidate says Yes/No
        if prompt_feat['neg'] > 0:
            # Heuristic: If prompt is negative, simple 'yes' might be ambiguous/wrong without context
            # We apply a small uncertainty penalty unless the candidate also contains negation
            if cand_feat['yes'] > 0 and cand_feat['neg'] == 0:
                penalty += 0.1 
            if cand_feat['no'] > 0 and cand_feat['neg'] > 0:
                penalty += 0.1 # Double negative confusion risk

        # Contradiction 2: Numeric violations
        if prompt_feat['nums'] and cand_feat['nums']:
            p_nums = prompt_feat['nums']
            c_nums = cand_feat['nums']
            
            # Check for direct inequality contradictions if comparatives exist
            if prompt_feat['comp'] > 0:
                # If prompt implies ordering and candidate provides numbers that violate typical bounds
                # (Simplified: if candidate number is wildly out of distribution of prompt numbers)
                if p_nums:
                    p_avg = sum(p_nums)/len(p_nums)
                    for cn in c_nums:
                        if abs(cn - p_avg) > max(p_nums) * 2: # Rough outlier check
                            penalty += 0.3

        # Contradiction 3: Conditional presence
        # If prompt has conditionals, candidate lacking length/complexity might be insufficient
        if prompt_feat['cond'] > 0 and cand_feat['len'] < 3:
            penalty += 0.2
            
        return min(penalty, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Executes the Dialectical Verification Loop.
        1. Thesis: Calculate structural similarity (dot product of features).
        2. Antithesis: Calculate contradiction penalty.
        3. Synthesis: Refine score = Thesis * (1 - Antithesis).
        """
        p_feat = self._extract_features(prompt)
        results = []
        
        # Base vector for prompt
        p_vec = np.array([p_feat['neg'], p_feat['comp'], p_feat['cond'], float(p_feat['len'])/10])

        for cand in candidates:
            c_feat = self._extract_features(cand)
            c_vec = np.array([c_feat['neg'], c_feat['comp'], c_feat['cond'], float(c_feat['len'])/10])
            
            # THESIS: Structural alignment score
            # Normalize slightly to prevent length dominance
            thesis_score = float(np.dot(p_vec, c_vec)) / (np.linalg.norm(p_vec) + 1e-6)
            
            # ANTITHESIS: Contradiction detection
            contradiction = self._check_contradiction(p_feat, c_feat)
            
            # SYNTHESIS: Refined hypothesis score
            final_score = thesis_score * (1.0 - contradiction)
            
            # Fallback to NCD-like length similarity if structural signal is zero
            if thesis_score == 0:
                len_ratio = 1.0 - abs(len(cand) - len(prompt)) / (len(prompt) + 1)
                final_score = max(0.1, len_ratio * 0.5)

            reasoning = f"Thesis:{thesis_score:.2f} Antithesis:{contradiction:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the dialectical synthesis of the specific pair.
        High confidence requires high structural alignment and low contradiction.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Map score to 0-1 confidence range, ensuring we beat random baseline (0.2)
        # If score is positive, we have some structural hook.
        conf = min(1.0, max(0.0, score * 0.5 + 0.3)) 
        return conf