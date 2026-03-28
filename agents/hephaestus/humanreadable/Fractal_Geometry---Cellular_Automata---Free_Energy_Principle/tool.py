import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine based on the Free Energy Principle (FEP) 
    with Fractal Geometry constraints, while restricting Cellular Automata (CA) 
    to structural parsing roles as per causal intelligence guidelines.
    
    Mechanism:
    1. FEP Core (evaluate): Treats the prompt as 'sensory input' and candidates 
       as 'internal models'. Minimizes 'variational free energy' by calculating 
       a cost function based on structural consistency (logic, negation, math) 
       and semantic alignment (NCD). Lower energy = higher score.
    2. Fractal Constraint: Applies self-similar scoring weights. If a candidate 
       resolves high-level logical constraints (global scale), it receives a 
       multiplicative boost similar to fractal dimension scaling.
    3. CA Structural Parser: Uses local rule-based scanning (mimicking CA local 
       updates) to detect logical operators (NOT, IF, >, <) without using CA 
       for the actual reasoning derivation, avoiding known failure modes.
    """

    def __init__(self):
        # Logical operators for structural parsing (CA-like local rules)
        self.negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        self.comparators = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        
        # Fractal scaling factor (self-similarity weight)
        self.fractal_scale = 1.44 

    def _structural_parse(self, text: str) -> dict:
        """
        Extracts logical features using local pattern matching (CA-analog).
        Returns a feature dictionary for energy calculation.
        """
        lower_text = text.lower()
        features = {
            'has_negation': any(n in lower_text for n in self.negations),
            'has_comparator': any(c in lower_text for c in self.comparators),
            'has_conditional': any(c in lower_text for c in self.conditionals),
            'numeric_count': len(re.findall(r'\d+\.?\d*', text)),
            'length': len(text)
        }
        return features

    def _compute_logic_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes 'prediction error' (energy) based on structural consistency.
        Low energy = high consistency between prompt constraints and candidate.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        energy = 0.0
        
        # Constraint 1: Negation Consistency
        # If prompt demands negation logic, candidate should reflect it or be concise
        if p_feat['has_negation']:
            # Penalty if candidate is too short to express negation logic properly
            if c_feat['length'] < 3:
                energy += 2.0
            # Bonus if candidate also acknowledges negation context (heuristic)
            if c_feat['has_negation']:
                energy -= 1.5
                
        # Constraint 2: Numeric/Comparator Consistency
        if p_feat['has_comparator'] and p_feat['numeric_count'] > 0:
            # Extract numbers from prompt and candidate to check order magnitude
            p_nums = re.findall(r'\d+\.?\d*', prompt)
            c_nums = re.findall(r'\d+\.?\d*', candidate)
            
            if c_nums:
                # Simple consistency check: does the candidate contain numbers?
                # If prompt has math, candidate without numbers is high energy
                energy -= 2.0 
            else:
                # Prompt implies math/comparison, candidate has no numbers -> High Error
                energy += 3.0

        # Constraint 3: Conditional Logic
        if p_feat['has_conditional']:
            if not c_feat['has_conditional'] and c_feat['length'] < 10:
                # Short answers to conditional prompts often miss nuance
                energy += 1.5
                
        return energy

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing Free Energy.
        Score = (Fractal_Scale * Structural_Consistency) - NCD_Distance
        """
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        p_feat = self._structural_parse(prompt)
        base_penalty = 0.0
        if p_feat['has_negation'] or p_feat['has_comparator']:
            base_penalty = 1.0 # Baseline complexity cost

        for cand in candidates:
            # 1. Compute Structural Energy (FEP: Prediction Error)
            logic_energy = self._compute_logic_energy(prompt, cand)
            
            # 2. Compute Semantic Distance (NCD as tiebreaker/refiner)
            # We invert NCD because lower distance = higher similarity = better
            ncd_val = self._ncd(prompt, cand)
            
            # 3. Fractal Scaling Application
            # If structural logic is sound (low energy), apply fractal boost
            structural_score = max(0, 5.0 - logic_energy)
            
            # Apply fractal dimension scaling if structural integrity is high
            if structural_score > 3.0:
                final_score = (structural_score * self.fractal_scale) - (ncd_val * 0.5)
            else:
                # If logic fails, fractal scaling doesn't help; rely on base similarity
                final_score = structural_score - (ncd_val * 2.0)
                
            # Generate reasoning string
            reason = f"Logic Energy: {logic_energy:.2f}, NCD: {ncd_val:.2f}. "
            if logic_energy < 1.0:
                reason += "High structural consistency detected."
            elif p_feat['has_comparator'] and logic_energy > 2.0:
                reason += "Failed numeric/comparator consistency check."
            else:
                reason += "Standard evaluation."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on free energy minimization.
        1.0 = Minimal prediction error (High logic match, Low NCD).
        0.0 = Maximal prediction error.
        """
        # Get the evaluation score for this specific pair
        # We simulate a single-candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map raw score to 0-1 range using a sigmoid-like clamp
        # Assuming typical scores range between -2 and 8
        # Normalized: (score + 2) / 10 -> clamped 0 to 1
        confidence = (raw_score + 2.0) / 10.0
        confidence = max(0.0, min(1.0, confidence))
        
        return round(confidence, 4)