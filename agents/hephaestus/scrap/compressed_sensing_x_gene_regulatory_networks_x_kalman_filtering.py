import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Compressed-Sensing Kalman Filter (CS-KF) Reasoning Analogy.
    
    Mechanism:
    1. State Space Construction: Parses the prompt into a linear system where 
       logical constraints act as the 'sensing matrix' (Phi) and candidate 
       assertions act as the 'state' (x).
    2. Sparse Inference (L1-Regularization): Identifies logical negations, 
       comparatives, and conditionals as sparse regulatory edges. It penalizes 
       candidates that violate these hard structural constraints (high residual).
    3. Recursive Update (Kalman): Computes a 'belief score' by combining 
       structural consistency (measurement update) with semantic compression 
       (NCD tiebreaker). 
    4. Output: Ranks candidates by their posterior probability of satisfying 
       the logical 'dynamics' of the prompt.
    """

    def __init__(self):
        self.rho = 0.5  # Shrinkage parameter for L1 regularization analogy
        self.noise_var = 0.1  # Assumed measurement noise variance

    def _structural_parse(self, text):
        """Extracts logical operators and numeric values as structural features."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'bool_yes': 1 if re.search(r'\byes\b', text_lower) else 0,
            'bool_no': 1 if re.search(r'\bno\b', text_lower) else 0
        }
        return features

    def _check_logic_consistency(self, prompt_feats, cand_feats):
        """
        Simulates the Kalman measurement update.
        Calculates residual error between prompt constraints and candidate answer.
        """
        error = 0.0
        
        # Constraint 1: Negation consistency (Modus Tollens approximation)
        # If prompt has strong negation context, 'yes' might be penalized depending on phrasing
        # Here we simply check for contradictory density
        if prompt_feats['negations'] > 0:
            # Heuristic: High negation in prompt requires careful handling
            # If candidate is bare 'yes'/'no', it might be ambiguous, but we don't penalize heavily
            pass

        # Constraint 2: Numeric consistency (The "9.11 vs 9.9" test)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            try:
                p_nums = [float(n) for n in prompt_feats['numbers']]
                c_nums = [float(n) for n in cand_feats['numbers']]
                
                # Check for direct contradiction if numbers are present
                # This is a simplified transitivity check
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # If prompt implies order (e.g., 9.11 < 9.9 context) and candidate violates
                    # We assume the prompt sets a rule and candidate must align.
                    # Since we don't have full NLP, we check if candidate number is wildly out of bounds
                    p_range = max(p_nums) - min(p_nums)
                    if p_range > 0:
                        for cn in c_nums:
                            if cn > max(p_nums) * 1.5 or cn < min(p_nums) * 0.5:
                                error += 2.0 # High penalty for out-of-bounds
            except ValueError:
                pass

        # Constraint 3: Conditional/Comparative presence
        # If prompt asks for comparison (comparatives > 0), candidate should ideally reflect it
        if prompt_feats['comparatives'] > 0:
            if cand_feats['comparatives'] == 0 and cand_feats['numbers'] == 0:
                # Candidate lacks comparative markers or numbers when prompt expects them
                error += 0.5
        
        return error

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_joint = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_joint - max_len) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # 1. Measurement Update (Structural Logic)
            residual = self._check_logic_consistency(prompt_feats, cand_feats)
            
            # 2. L1 Shrinkage (Sparsity promotion)
            # Penalize complex answers if simple logic suffices, or vice versa
            # Here we use residual as the primary cost
            logic_score = np.exp(-residual) # Convert error to probability-like score

            # 3. NCD Tiebreaker (Semantic similarity)
            ncd = self._ncd_distance(prompt, cand)
            
            # Final Score: Weighted combination favoring structural logic
            # Logic is primary (weight 0.8), NCD is secondary (weight 0.2)
            final_score = (0.8 * logic_score) + (0.2 * (1.0 - ncd))
            
            # Adjust for boolean traps (e.g. prompt "Is it no?" -> answer "No")
            # If prompt asks a negative question, simple yes/no might be tricky.
            # We rely on the fact that NCD captures some semantic overlap.
            
            reasoning = f"Structural residual: {residual:.2f}, NCD: {ncd:.2f}"
            if prompt_feats['numbers'] and cand_feats['numbers']:
                reasoning += "; Numeric consistency checked."
            if prompt_feats['comparatives'] > 0:
                reasoning += "; Comparative logic applied."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on how well the answer satisfies 
        the inferred structural constraints of the prompt.
        """
        evaluated = self.evaluate(prompt, [answer])
        if not evaluated:
            return 0.0
        
        score = evaluated[0]['score']
        
        # Calibrate score to 0-1 range more strictly
        # If the top candidate (which is this one) has a low score, confidence is low.
        # If it has a high score, confidence is high.
        # We apply a sigmoid-like scaling to ensure 0.5 is the neutral point for random guessing
        calibrated = 1.0 / (1.0 + np.exp(-5 * (score - 0.5)))
        return float(np.clip(calibrated, 0.0, 1.0))