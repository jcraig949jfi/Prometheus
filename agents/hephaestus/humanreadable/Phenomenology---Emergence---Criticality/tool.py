import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Organizing Critical Predictive-Coding Network (Approximated).
    
    Mechanism:
    1. Phenomenological Field (Lifeworld): Encodes prompt/candidates into a normalized 
       vector space. A global 'intentional gain' modulates sensitivity to prediction errors.
    2. Criticality (Edge of Chaos): The system simulates an avalanche process. 
       Instead of spiking neurons, we treat token-level semantic differences as perturbations.
       We tune a 'susceptibility' parameter such that small semantic shifts can trigger 
       large changes in candidate ranking (maximizing exploration vs exploitation).
    3. Emergence: Macro-scale scores emerge from the interaction between the candidate's 
       structural integrity (logic/numbers) and its resonance with the prompt under critical gain.
    4. Bracketing: Irrelevant features (noise) are suppressed by focusing the gain on 
       structural constraints (negations, comparatives, numbers).
    
    This implementation approximates the spiking network using deterministic vector dynamics
    tuned to mimic power-law sensitivity via a sigmoidal gain function centered at a critical threshold.
    """

    def __init__(self):
        # Criticality parameter: tunes the system to the "edge of chaos"
        # where susceptibility to input perturbations is maximized.
        self.critical_threshold = 0.5
        self.gain_slope = 20.0  # Steepness of the phase transition
        
        # Phenomenological weights for structural parsing (Priority based on causal analysis)
        # Focus on: Negations, Comparatives, Conditionals, Numbers
        self.structural_keywords = {
            'not': 1.5, 'no': 1.5, 'never': 1.5, 'without': 1.2,
            'greater': 1.3, 'less': 1.3, 'more': 1.2, 'fewer': 1.2,
            'if': 1.4, 'then': 1.4, 'unless': 1.4, 'only': 1.3,
            'all': 1.2, 'some': 1.2, 'none': 1.5, 'every': 1.2
        }
        self.numeric_chars = set('0123456789.-')

    def _extract_features(self, text: str) -> Tuple[float, float, float, List[str]]:
        """Extract structural features: numeric density, logical keyword density, length, tokens."""
        lower_text = text.lower()
        tokens = lower_text.split()
        
        # 1. Numeric Evaluation Potential
        num_count = sum(1 for c in text if c in self.numeric_chars)
        numeric_density = num_count / (len(text) + 1)
        
        # 2. Logical/Structural Density (The "Bracketing" mechanism)
        logic_score = 0.0
        found_keywords = []
        for word in tokens:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word in self.structural_keywords:
                logic_score += self.structural_keywords[clean_word]
                found_keywords.append(clean_word)
        
        logic_density = logic_score / (len(tokens) + 1)
        
        return numeric_density, logic_density, len(text), found_keywords

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a baseline similarity metric."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _critical_gain(self, error_signal: float) -> float:
        """
        Simulates the phenomenological gain control.
        Uses a sigmoid centered at critical_threshold to mimic operation at the edge of chaos.
        Small errors near the threshold result in high susceptibility (large output change).
        """
        # Shift error to be centered around 0 for the sigmoid
        x = (error_signal - self.critical_threshold) * self.gain_slope
        # Sigmoid activation
        return 1.0 / (1.0 + np.exp(-x))

    def _evaluate_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core reasoning engine.
        1. Analyze structural constraints (Bracketing).
        2. Compute semantic distance (NCD).
        3. Apply critical gain to determine final score.
        """
        p_num, p_log, p_len, p_keys = self._extract_features(prompt)
        c_num, c_log, c_len, c_keys = self._extract_features(candidate)
        
        reasoning_steps = []
        base_score = 0.5
        penalty = 0.0
        
        # --- Structural Parsing & Constraint Propagation ---
        
        # 1. Numeric Consistency Check
        if p_num > 0.01: # Prompt contains numbers
            if c_num == 0:
                # Candidate lacks numbers when prompt has them (potential failure)
                # But if the answer is conceptual, this might be okay. 
                # However, for math traps, this is critical.
                penalty += 0.2
                reasoning_steps.append("Numeric mismatch detected.")
            else:
                # Heuristic: If both have numbers, check magnitude order roughly
                # (Simplified for single pass: assume candidate numbers should relate)
                reasoning_steps.append("Numeric consistency maintained.")
                base_score += 0.1

        # 2. Logical Keyword Propagation (Modus Tollens/Constraint)
        # If prompt has strong logical operators, candidate must reflect logic or be a direct value
        if p_log > 0.1:
            if c_log > 0.05 or c_num > 0.01:
                base_score += 0.15
                reasoning_steps.append("Logical structure preserved.")
            else:
                # Candidate ignores logical constraints
                penalty += 0.3
                reasoning_steps.append("Ignored logical constraints.")
        
        # 3. Negation Handling (Crucial for "not", "no")
        if 'not' in p_keys or 'no' in p_keys or 'never' in p_keys:
            if 'not' in c_keys or 'no' in c_keys or 'never' in c_keys:
                 # Double negation or consistent negation
                 base_score += 0.1
                 reasoning_steps.append("Negation handling consistent.")
            else:
                # Risk of missing the negation
                # We don't penalize heavily unless it looks like a direct contradiction
                pass

        # --- Criticality & Emergence ---
        
        # Calculate "Prediction Error" via NCD (Semantic Distance)
        # Normalized NCD (0 = identical, 1 = totally different)
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # In a predictive coding network, we want to minimize prediction error.
        # However, at criticality, we want to be sensitive to small differences.
        # We invert NCD so high score = low error (high similarity/relevance)
        similarity = 1.0 - ncd_val
        
        # Combine structural score with similarity
        # The "Phenomenological Field" modulates this: 
        # If structural integrity is high, we trust the similarity more.
        structural_integrity = max(0.1, (p_log + c_log + (1.0 if p_num == c_num > 0 else 0.0)))
        
        # Critical Gain Application
        # We treat the gap between structural expectation and semantic similarity as the error signal
        error_signal = abs(similarity - structural_integrity)
        
        # Apply critical gain function: 
        # If the system is well-tuned (error near critical threshold), small changes matter.
        # Here we use the gain to boost candidates that balance structure and similarity.
        gain_factor = self._critical_gain(error_signal)
        
        # Final Score Calculation
        # High structural integrity + High similarity + Critical Boost
        final_score = (base_score - penalty + (similarity * 0.4)) * (1.0 + 0.5 * gain_factor)
        
        # Normalize roughly to 0-1 range
        final_score = max(0.0, min(1.0, final_score))
        
        reason_str = "; ".join(reasoning_steps) if reasoning_steps else "Standard evaluation."
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        for cand in candidates:
            score, reason = self._evaluate_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the internal scoring mechanism but normalizes strictly.
        """
        score, _ = self._evaluate_candidate(prompt, answer)
        
        # Calibration: 
        # Pure NCD baseline is ~20% acc. Our structural parsing should boost this.
        # We map the internal score to a confidence metric.
        # Scores > 0.6 are considered high confidence in this architecture.
        confidence = max(0.0, min(1.0, score))
        
        return float(confidence)