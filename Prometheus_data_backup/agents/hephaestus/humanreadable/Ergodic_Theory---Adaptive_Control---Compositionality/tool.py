import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Compositional Adaptive Ergodic Estimator (CAEE) - Computational Approximation
    
    Mechanism:
    1. Compositional Parsing (Syntax): Decomposes prompt/candidates into logical atoms 
       (negations, comparatives, numerics, conditionals) acting as modular sub-hypotheses.
    2. Ergodic Estimation (Statistics): Treats the character/word sequence as a trajectory.
       Computes "invariant measures" (n-gram frequency distributions) to estimate 
       statistical convergence between prompt constraints and candidate answers.
    3. Adaptive Control (Feedback): Implements a Model Reference Adaptive Control (MRAC) 
       loop where the "reference model" is the structural signature of the prompt.
       The "gain" is adjusted dynamically based on the mismatch between the candidate's
       logical structure and the prompt's required structure (error signal).
    
    This avoids pure string similarity by prioritizing structural/logical alignment 
    (Adaptive/Compositional) and statistical distribution matching (Ergodic).
    """

    def __init__(self):
        # MRAC Gain parameter (adaptive learning rate)
        self.gamma = 0.5 
        # Reference model weights for structural components
        self.struct_weights = {
            'negation': 2.0,
            'comparative': 2.0,
            'numeric': 3.0,
            'conditional': 2.0,
            'lexical': 1.0
        }

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Compositional parsing: Extracts logical atoms as modular features."""
        text_lower = text.lower()
        features = {}
        
        # Negation module
        negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        features['negation'] = sum(1 for w in negations if re.search(r'\b' + w + r'\b', text_lower))
        
        # Comparative module
        comparatives = ['more', 'less', 'greater', 'smaller', 'better', 'worse', 'higher', 'lower', 'than']
        features['comparative'] = sum(1 for w in comparatives if re.search(r'\b' + w + r'\b', text_lower))
        
        # Numeric module
        numbers = re.findall(r'\d+\.?\d*', text)
        features['numeric'] = len(numbers)
        
        # Conditional module
        conditionals = ['if', 'then', 'else', 'when', 'unless', 'provided']
        features['conditional'] = sum(1 for w in conditionals if re.search(r'\b' + w + r'\b', text_lower))
        
        # Lexical density (proxy for complexity)
        words = re.findall(r'\b\w+\b', text_lower)
        features['lexical'] = len(words)
        
        return features

    def _ergodic_measure(self, text: str, n: int = 2) -> Dict[str, float]:
        """
        Ergodic Theory approximation: 
        Estimates invariant measures via n-gram frequency distributions.
        Assumes the text is a trajectory through a state space of characters.
        """
        if len(text) < n:
            return {}
        
        # Generate trajectory (n-grams)
        trajectory = [text[i:i+n] for i in range(len(text) - n + 1)]
        if not trajectory:
            return {}
            
        # Count occurrences (empirical measure)
        counts = {}
        for state in trajectory:
            counts[state] = counts.get(state, 0) + 1
            
        # Normalize to probability distribution (invariant measure estimate)
        total = len(trajectory)
        return {k: v/total for k, v in counts.items()}

    def _kl_divergence(self, p: Dict[str, float], q: Dict[str, float]) -> float:
        """Computes KL Divergence between two ergodic measures (p || q)."""
        keys = set(p.keys()) | set(q.keys())
        kl = 0.0
        epsilon = 1e-9
        for k in keys:
            pk = p.get(k, epsilon)
            qk = q.get(k, epsilon)
            if pk > 0:
                kl += pk * math.log(pk / qk)
        return kl

    def _structural_mismatch(self, p_struct: Dict, c_struct: Dict) -> float:
        """Calculates weighted error signal for MRAC update."""
        error = 0.0
        for key in p_struct:
            diff = abs(p_struct[key] - c_struct[key])
            # Normalize by prompt magnitude to avoid scale issues
            norm = p_struct[key] + 1 
            error += self.struct_weights.get(key, 1.0) * (diff / norm)
        return error

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_ergodic = self._ergodic_measure(prompt.lower())
        
        # Reference model: Ideal candidate should match prompt structure perfectly
        # In MRAC terms, this is the desired trajectory.
        
        scored = []
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            cand_ergodic = self._ergodic_measure(cand.lower())
            
            # 1. Structural Error Signal (Compositional)
            struct_error = self._structural_mismatch(prompt_struct, cand_struct)
            
            # 2. Ergodic Divergence (Statistical)
            # Measure how far the candidate's distribution is from the prompt's context
            ergodic_dist = self._kl_divergence(prompt_ergodic, cand_ergodic)
            
            # 3. MRAC Update Law (Adaptive Control)
            # Control law: u = -K * e, where K adapts to minimize error
            # Here we simulate the steady-state error reduction.
            # High structural match reduces the penalty significantly.
            structural_penalty = struct_error * self.gamma
            
            # Combine: Low divergence + Low structural error = High Score
            # We invert distance to score. 
            raw_score = 1.0 / (1.0 + structural_penalty + ergodic_dist)
            
            # NCD Tiebreaker (only if scores are very close, handled by sorting stability)
            # But we add a small NCD component to break ties implicitly
            ncd_val = self._compute_ncd(prompt, cand)
            final_score = raw_score * 0.9 + (1.0 - ncd_val) * 0.1
            
            scored.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural Error: {struct_error:.2f}, Ergodic Dist: {ergodic_dist:.2f}, NCD: {ncd_val:.2f}"
            })
            
        # Rank by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and ergodic consistency.
        Uses the internal MRAC error signal as a proxy for confidence.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Calculate mismatch
        error = self._structural_mismatch(p_struct, a_struct)
        
        # Calculate ergodic divergence
        p_erg = self._ergodic_measure(prompt.lower())
        a_erg = self._ergodic_measure(answer.lower())
        divergence = self._kl_divergence(p_erg, a_erg)
        
        # MRAC Confidence Law: Confidence decays exponentially with error
        # C = exp(-lambda * (struct_error + divergence))
        lambda_param = 0.5
        conf = math.exp(-lambda_param * (error + min(divergence, 2.0)))
        
        return max(0.0, min(1.0, conf))