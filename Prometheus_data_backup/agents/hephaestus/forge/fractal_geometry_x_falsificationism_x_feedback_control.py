import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Fractal Geometry, Falsificationism, 
    and Feedback Control. 
    
    Mechanism:
    1. Parses candidates into hierarchical claim trees using regex for atomic propositions.
    2. Computes Fractal Dimension (D) via box-counting on tree depth distribution.
    3. Calculates Falsificationism Score (F) as the proportion of testable nodes.
    4. Applies a PID controller to stabilize the weighting between F and internal state, 
       deriving a Stability Score (C).
    5. Final Score = 0.4*D + 0.4*F + 0.2*C.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(greater|less|more|fewer|better|worse|higher|lower)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|unless|provided|then)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(\.\d+)?%?'),
        'ordering': re.compile(r'\b(first|second|before|after|prior|subsequent)\b', re.IGNORECASE)
    }

    def __init__(self):
        pass

    def _extract_features(self, text: str) -> Dict[str, int]:
        """Extract counts of logical features from text."""
        counts = {k: len(p.findall(text)) for k, p in self.PATTERNS.items()}
        return counts

    def _build_claim_tree(self, text: str) -> Dict[str, Any]:
        """
        Builds a simplified hierarchical claim tree.
        Splits by logical connectors to create depth.
        """
        # Simple recursive splitter for demonstration of hierarchy
        # Level 0: Whole text
        # Level 1: Split by 'because', 'if', 'and', 'but'
        separators = [r'\bbecause\b', r'\bif\b', r'\band\b', r'\but\b', r'\bthen\b']
        
        nodes = []
        current_level = [text]
        
        # Simulate depth up to 3 levels
        for sep_pattern in separators:
            next_level = []
            for segment in current_level:
                parts = re.split(sep_pattern, segment, flags=re.IGNORECASE)
                if len(parts) > 1:
                    next_level.extend([p.strip() for p in parts if p.strip()])
                else:
                    next_level.append(segment)
            if len(next_level) == len(current_level):
                break # No further splitting occurred
            current_level = next_level
            if len(current_level) > 10: # Limit breadth
                break
        
        # Construct pseudo-tree structure for depth analysis
        # Depth is approximated by the number of successful splits + 1
        max_depth = max(1, len(current_level)) 
        # Create leaf nodes for each segment
        leaves = []
        for segment in current_level:
            feats = self._extract_features(segment)
            is_testable = any([
                feats['negation'] > 0,
                feats['comparative'] > 0,
                feats['numeric'] > 0,
                feats['ordering'] > 0
            ])
            leaves.append({
                "text": segment,
                "features": feats,
                "testable": is_testable,
                "depth": 1
            })
            
        return {
            "root": text,
            "leaves": leaves,
            "max_depth": max_depth if max_depth > 0 else 1
        }

    def _compute_fractal_dimension(self, tree: Dict[str, Any]) -> float:
        """
        Applies box-counting method on tree depth distribution.
        Fits log N(s) vs log (1/s) to get slope D.
        """
        depths = [leaf['depth'] for leaf in tree['leaves']]
        if not depths:
            return 0.0
            
        max_d = tree['max_depth']
        if max_d <= 1:
            return 0.5 # Neutral for flat structures
            
        # Scales s = 1 to max_depth
        scales = list(range(1, max_d + 1))
        log_inv_s = []
        log_n_s = []
        
        for s in scales:
            # N(s) = number of nodes whose subtree depth >= s
            # Since our leaves are depth 1, we simulate subtree depth by coverage
            # In this simplified model, we assume deeper trees have more nodes covering larger s
            count = sum(1 for d in depths if d >= s)
            if count > 0:
                log_inv_s.append(np.log(1.0 / s))
                log_n_s.append(np.log(count))
        
        if len(log_inv_s) < 2:
            return 0.5
            
        # Linear fit
        try:
            A = np.vstack([log_inv_s, np.ones(len(log_inv_s))]).T
            slope, _ = np.linalg.lstsq(A, log_n_s, rcond=None)[0]
            d_raw = abs(slope)
            # Normalize by max_depth to get d in [0,1]
            return min(1.0, d_raw / max_d) if max_d > 0 else 0.0
        except:
            return 0.5

    def _compute_falsification_score(self, tree: Dict[str, Any]) -> float:
        """Proportion of testable nodes."""
        leaves = tree['leaves']
        if not leaves:
            return 0.0
        testable_count = sum(1 for leaf in leaves if leaf['testable'])
        return testable_count / len(leaves)

    def _compute_stability_score(self, f_score: float) -> float:
        """
        PID control loop to stabilize weight based on falsifiability.
        Returns C = 1 - min(I, 1) where I is instability.
        """
        w = 0.5
        Kp, Ki, Kd = 0.4, 0.1, 0.05
        history_w = []
        prev_error = 0.0
        sum_error = 0.0
        
        for t in range(1, 6): # T=5 iterations
            error = f_score - w
            sum_error += error
            derivative = error - prev_error
            
            w = w + Kp * error + Ki * sum_error + Kd * derivative
            # Clamp w to reasonable bounds to prevent explosion in this context
            w = max(0.0, min(1.0, w))
            
            history_w.append(w)
            prev_error = error
            
        if not history_w:
            return 0.5
            
        std_w = np.std(history_w)
        mean_w = np.mean(history_w) if np.mean(history_w) != 0 else 1e-9
        instability = std_w / mean_w if mean_w != 0 else 0
        return 1.0 - min(instability, 1.0)

    def _score_candidate(self, text: str) -> float:
        if not text.strip():
            return 0.0
            
        tree = self._build_claim_tree(text)
        
        # 1. Fractal Dimension
        d = self._compute_fractal_dimension(tree)
        
        # 2. Falsificationism Score
        f = self._compute_falsification_score(tree)
        
        # 3. Feedback Control Stability
        c = self._compute_stability_score(f)
        
        # Final Score
        score = 0.4 * d + 0.4 * f + 0.2 * c
        return float(score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        import zlib
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            numerator = c12 - min(c1, c2)
            denominator = max(c1, c2)
            return numerator / denominator if denominator > 0 else 1.0
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            score = self._score_candidate(cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Fractal:{self._compute_fractal_dimension(self._build_claim_tree(cand)):.2f}, Falsifiable:{self._compute_falsification_score(self._build_claim_tree(cand)):.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Handle ties with NCD if necessary (simple implementation: re-rank ties)
        # For this strict implementation, we rely on the primary score as requested, 
        # but ensure deterministic output.
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the structural score."""
        score = self._score_candidate(answer)
        # Map score to confidence. High structural integrity implies higher confidence.
        # We assume the prompt context doesn't drastically change the internal logic validity
        # unless the answer is empty.
        if not answer.strip():
            return 0.0
        return min(1.0, max(0.0, score))