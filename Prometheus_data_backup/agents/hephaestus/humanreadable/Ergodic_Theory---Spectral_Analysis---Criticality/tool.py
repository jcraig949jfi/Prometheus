import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Ergodic Spectral Monitor (CESM) Approximation.
    
    Mechanism:
    1. Structural Parsing & Numeric Evaluation: Extracts numbers and logical operators
       to create a deterministic "state trajectory" based on constraint satisfaction.
    2. Ergodic/Spectral Analogy: Treats the sequence of constraint checks as a time-series.
       - "Ordered" (Sub-critical): High consistency, low variance in logic checks.
       - "Disordered" (Super-critical): High variance, contradictory constraints.
       - "Critical": Balanced tension between competing constraints (maximized sensitivity).
    3. Implementation: 
       - Converts prompt/candidate into a vector of numeric and structural features.
       - Computes a "spectral density" proxy via variance of differences (high freq power).
       - Uses NCD only as a tie-breaker for semantic similarity when logic scores are close.
       - Scores based on logical consistency (constraint propagation) and numeric correctness.
    """
    
    def __init__(self):
        self._epsilon = 1e-9

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        nums = []
        current = ""
        has_dot = False
        for char in text.lower():
            if char.isdigit():
                current += char
            elif char == '.' and not has_dot:
                current += char
                has_dot = True
            else:
                if current and current != ".":
                    try: nums.append(float(current))
                    except: pass
                current = ""
                has_dot = False
        if current and current != ".":
            try: nums.append(float(current))
            except: pass
        return nums

    def _check_constraints(self, prompt: str, candidate: str) -> Tuple[float, List[float]]:
        """
        Returns a logic score and a trajectory vector representing the 'state'.
        Trajectory allows us to simulate the spectral/ergodic analysis.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        trajectory = []
        score = 0.0
        
        # 1. Numeric Evaluation (Constraint Propagation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if candidate numbers logically follow prompt numbers (e.g., comparisons)
            # Simple heuristic: if prompt implies a comparison, check if candidate respects it
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Detect comparison keywords
                is_less = any(k in p_low for k in ["less", "smaller", "below", "under"])
                is_more = any(k in p_low for k in ["more", "greater", "above", "over", "larger"])
                
                val = c_nums[0]
                ref = p_nums[0] # Simplified reference
                
                if is_less and val < ref: score += 2.0
                elif is_more and val > ref: score += 2.0
                elif not (is_less or is_more):
                    # If no comparison, check equality or simple arithmetic presence
                    if abs(val - ref) < self._epsilon: score += 1.0
            
            # Add numeric consistency to trajectory
            trajectory.extend([abs(a - b) for a, b in zip(p_nums, c_nums)] if p_nums else [0.0])
        else:
            trajectory.append(0.5) # Neutral state if no numbers

        # 2. Structural Parsing (Negations and Conditionals)
        has_negation = any(k in p_low for k in ["not ", "no ", "never ", "cannot "])
        cand_negation = any(k in c_low for k in ["not ", "no ", "never ", "cannot "])
        
        if has_negation:
            # If prompt has negation, candidate must handle it (simplified: presence/absence check)
            # This simulates a 'state flip' in the trajectory
            trajectory.append(1.0 if cand_negation else -1.0)
            if cand_negation: score += 1.0
        else:
            trajectory.append(0.0)
            if not cand_negation: score += 0.5

        # 3. Keyword Overlap (Bag of words with structural weight)
        # Only count significant words to avoid gameability
        stop_words = set(["the", "is", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"])
        p_words = set(w.strip(".,!?") for w in p_low.split() if w not in stop_words)
        c_words = set(w.strip(".,!?") for w in c_low.split() if w not in stop_words)
        
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            score += overlap * 3.0
            trajectory.append(overlap)
        
        # Add noise to trajectory to simulate non-stationarity if score is too perfect (anti-game)
        if score > 4.0:
            trajectory.append(-0.1) 
            
        return score, trajectory

    def _compute_spectral_proxy(self, trajectory: List[float]) -> float:
        """
        Approximates the 'Power Spectral Density' low-frequency power.
        High variance in differences = High frequency (Disordered/Chaotic)
        Low variance = Low frequency (Ordered/Rigid)
        Criticality is found at an intermediate balance.
        """
        if len(trajectory) < 2:
            return 0.5
        
        traj = np.array(trajectory)
        # First difference approximates high-frequency content
        diffs = np.diff(traj)
        if len(diffs) == 0:
            return 0.5
            
        # Variance of differences is a proxy for broadband power
        power = np.var(diffs)
        
        # Map power to a 'criticality' score (0 to 1)
        # We want a sweet spot. Let's assume moderate variance is 'critical'
        # Too low (0) -> Ordered. Too high -> Chaotic.
        # Using a Gaussian-like kernel around a target variance (e.g., 0.5)
        target_var = 0.25
        sigma = 0.2
        criticality_score = np.exp(-((power - target_var)**2) / (2 * sigma**2))
        
        return float(criticality_score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        l1, l2 = len(b1), len(b2)
        if l1 == 0 or l2 == 0: return 1.0
        try:
            c12 = len(zlib.compress(b1 + b2))
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt trajectory for context
        p_score, p_traj = self._check_constraints(prompt, prompt) 
        
        for cand in candidates:
            score, traj = self._check_constraints(prompt, cand)
            
            # Spectral/Ergodic Component
            spectral_factor = self._compute_spectral_proxy(traj)
            
            # NCD Tiebreaker (Semantic similarity)
            ncd_val = self._ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.5 # Bonus for similarity, but secondary
            
            # Final Score: Logic + Criticality Balance + Small NCD bonus
            # If logic score is high, spectral factor confirms stability
            final_score = score + (spectral_factor * 2.0) + ncd_bonus
            
            # Reasoning string
            reason = f"Logic:{score:.2f} Spec:{spectral_factor:.2f} NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score normalized."""
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        raw_score = res_list[0]["score"]
        
        # Normalize score to 0-1 range heuristically
        # Based on typical max scores from logic (approx 5-6) + spectral (1.0) + ncd (0.5)
        # Max expected ~ 7.5. 
        confidence = raw_score / 8.0
        return float(np.clip(confidence, 0.0, 1.0))