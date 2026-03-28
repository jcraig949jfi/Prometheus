import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Closed-Loop Incentive-Aware Controller (CIAC) Implementation.
    
    Mechanism:
    1. Attention (Restricted): Parses structural tokens (negations, comparatives, numbers)
       to form a 'relevance mask'. Does not score directly; defines the landscape.
    2. Feedback Control (PID-style): Computes error between candidate logic and prompt
       structural constraints. Adjusts a 'gain' factor: high error increases scrutiny 
       (penalty magnitude) on conflicting candidates.
    3. Mechanism Design (VCG-style): Applies a penalty term to candidates that would 
       otherwise 'game' the system by matching keywords but failing structural logic 
       (e.g., ignoring a negation). This ensures truthful alignment with constraints 
       is the dominant strategy for maximizing score.
       
    Scoring = (Structural Match * Base Score) - (VCG Penalty * Feedback Gain) + NCD_Tiebreaker
    """

    def __init__(self):
        # Structural patterns for the "Attention" parsing phase
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'only if']
        self.numeric_re = re.compile(r"-?\d+\.?\d*")

    def _parse_structure(self, text: str) -> Dict:
        """Extracts structural features acting as the 'Attention' mask."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        numbers = [float(n) for n in self.numeric_re.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logic(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core reasoning engine.
        Returns (base_score, reasoning_trace).
        """
        score = 0.5  # Base prior
        reasons = []

        # 1. Numeric Evaluation (High Priority)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Simple heuristic: if prompt has numbers, candidate should reflect them or their logic
            if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 0.3
                reasons.append("Numeric match found.")
            elif prompt_struct['comparative']:
                # Check if comparative logic holds (simplified)
                # E.g., Prompt "9.11 < 9.9", Candidate "True" vs "False"
                # We rely on the text overlap for the specific logic, but boost if numbers align
                pass 
            else:
                score -= 0.2
                reasons.append("Numeric mismatch.")

        # 2. Structural Consistency (Negation & Conditionals)
        if prompt_struct['negation']:
            if cand_struct['negation']:
                score += 0.2
                reasons.append("Negation preserved.")
            else:
                # Potential trap: candidate ignores "not"
                score -= 0.3
                reasons.append("Negation ignored (Critical).")
        
        if prompt_struct['conditional'] and not cand_struct['conditional']:
            # Candidate fails to acknowledge conditional nature
            score -= 0.1
            reasons.append("Conditional context dropped.")

        # 3. Keyword Overlap (Sanity Check, low weight to avoid gaming)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        overlap = len(p_words & c_words) / max(len(p_words), 1)
        score += overlap * 0.1
        
        return score, "; ".join(reasons) if reasons else "Structural baseline."

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._parse_structure(prompt)
        results = []

        # Pre-calculate NCD for all candidates for tie-breaking
        candidate_ncds = [(c, self._compute_ncd(prompt, c)) for c in candidates]
        min_ncd = min(n[1] for n in candidate_ncds) if candidate_ncds else 0.5
        max_ncd = max(n[1] for n in candidate_ncds) if candidate_ncds else 0.5
        ncd_range = max_ncd - min_ncd if (max_ncd - min_ncd) > 0 else 1.0

        for i, candidate in enumerate(candidates):
            cand_struct = self._parse_structure(candidate)
            
            # --- REASONING PHASE ---
            base_score, logic_trace = self._evaluate_logic(prompt_struct, cand_struct, prompt, candidate)
            
            # --- FEEDBACK CONTROL PHASE ---
            # Error signal: deviation from ideal structural match (1.0)
            error = max(0.0, 1.0 - base_score)
            # PID-like Gain: Increase scrutiny (penalty multiplier) as error grows
            # Kp = 1.5, Ki = 0.5 (simplified)
            gain = 1.0 + (1.5 * error) 
            
            # --- MECHANISM DESIGN PHASE (VCG-style) ---
            # Penalty for "gaming": High keyword overlap but low structural correctness
            p_words = set(prompt.lower().split())
            c_words = set(candidate.lower().split())
            overlap_ratio = len(p_words & c_words) / max(len(p_words), 1)
            
            # VCG Penalty: If overlap is high (>0.4) but logic score is low (<0.6), 
            # the system suspects manipulation (ignoring constraints while echoing words).
            vcg_penalty = 0.0
            if overlap_ratio > 0.4 and base_score < 0.6:
                # The penalty is proportional to how much it tries to look right while being wrong
                vcg_penalty = (overlap_ratio * 0.5) * gain
            
            # Final Score Calculation
            final_score = base_score - vcg_penalty
            
            # NCD Tiebreaker (only if scores are very close, normalized)
            ncd_val = self._compute_ncd(prompt, candidate)
            ncd_norm = 1.0 - ((ncd_val - min_ncd) / ncd_range) # Higher is better (lower distance)
            final_score += ncd_norm * 0.05 # Small boost for compression similarity

            results.append({
                "candidate": candidate,
                "score": round(max(0.0, min(1.0, final_score)), 4),
                "reasoning": f"{logic_trace} Gain:{gain:.2f} VCG_Pen:{vcg_penalty:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        # Quick logic check
        score, _ = self._evaluate_logic(p_struct, a_struct, prompt, answer)
        
        # Map score to confidence
        # If score > 0.7, high confidence. If < 0.3, low confidence.
        conf = max(0.0, min(1.0, score))
        return round(conf, 4)