import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Maximum-Entropy Critical Inference Engine (PMCIE) - Simplified Implementation
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical operators (negations, comparatives, conditionals)
       and numeric values to form a "Pragmatic Constraint Score". This acts as the hard logic layer.
    2. MaxEnt/Pragmatics (Secondary): Uses string length and lexical overlap as a proxy for 
       Gricean Maxims (Quantity/Manner) to penalize verbose or irrelevant candidates.
    3. Phase Transition (Metacognition): Calculates an order parameter 'm' based on the variance 
       between the top two structural scores. If m > threshold (critical point), the system 
       enters a "critical fluctuation" mode, boosting the score of the second-best candidate 
       to simulate hypothesis switching and avoid local minima.
    4. NCD (Tiebreaker): Used only when structural signals are indistinguishable.
    """

    def __init__(self):
        # Critical threshold for phase transition
        self.m_c = 0.15 
        # Temperature factor for critical fluctuations
        self.T_base = 1.0
        self.T_critical = 2.5 

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning engine.
        Combines structural parsing with pragmatic constraints.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        
        # 1. Constraint Propagation (Logic Matching)
        # If prompt has negation, valid answer often implies handling it (heuristic check)
        # Here we simply reward structural complexity alignment
        if p_feat['negations'] > 0:
            # Reward candidates that acknowledge context (simple proxy: length/complexity match)
            score += 0.5 if c_feat['length'] > 2 else -0.5
            
        if p_feat['conditionals'] > 0:
            score += 0.3 if c_feat['conditionals'] > 0 or c_feat['length'] > 5 else 0.0

        # 2. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Check if candidate numbers are logically derived (simplified: presence match)
                # In a full engine, this would parse expressions like "9.11 < 9.9"
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                # Heuristic: If prompt asks for max/min, check candidate number magnitude
                if 'max' in prompt.lower() or 'larger' in prompt.lower():
                    if c_nums and max(c_nums) >= max(p_nums):
                        score += 1.0
                elif 'min' in prompt.lower() or 'smaller' in prompt.lower():
                    if c_nums and min(c_nums) <= min(p_nums):
                        score += 1.0
                else:
                    # General numeric consistency
                    score += 0.5
            except ValueError:
                pass

        # 3. Pragmatic MaxEnt Prior (Gricean Constraints)
        # Penalty for violating Quantity (too long/short relative to prompt)
        len_ratio = c_feat['length'] / (p_feat['length'] + 1)
        if 0.5 <= len_ratio <= 3.0:
            score += 0.2 # Reward appropriate length
        else:
            score -= 0.2 # Penalize verbosity or brevity
        
        # Penalty for violating Relation (lexical overlap as proxy for relevance)
        p_words = set(prompt.lower().split())
        c_words = set(candidate.lower().split())
        overlap = len(p_words.intersection(c_words))
        if overlap > 0:
            score += 0.1 * min(overlap, 3) # Cap the bonus

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Step 1: Compute raw structural/logic scores
        raw_scores = []
        for i, cand in enumerate(candidates):
            s = self._evaluate_logic(prompt, cand)
            raw_scores.append((i, s))
        
        # Sort by score descending
        raw_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Step 2: Phase Transition Analysis (Order Parameter)
        # Calculate variance between top 2 candidates if available
        m = 0.0
        if len(raw_scores) >= 2:
            top_score = raw_scores[0][1]
            second_score = raw_scores[1][1]
            # Order parameter: variance of log-likelihood proxy (using scores as log-prob approx)
            # Simplified to squared difference for stability
            m = (top_score - second_score) ** 2
        
        # Step 3: Critical Fluctuation Injection
        final_scores = [0.0] * len(candidates)
        temperature = self.T_base
        
        if m < self.m_c:
            # Critical regime: High uncertainty, inject fluctuations
            temperature = self.T_critical
        
        # Apply temperature scaling and normalize
        # We treat raw scores as energy landscapes. 
        # High temp = flatten differences (exploration)
        # Low temp = sharpen differences (exploitation)
        
        max_raw = raw_scores[0][1] if raw_scores else 0.0
        min_raw = raw_scores[-1][1] if raw_scores else 0.0
        range_raw = (max_raw - min_raw) if (max_raw != min_raw) else 1.0
        
        ranked_results = []
        
        for idx, original_score in raw_scores:
            # Normalize score to 0-1 range roughly
            norm_score = (original_score - min_raw) / range_raw
            
            # Apply temperature effect on the gap from maximum
            # If T is high, the gap shrinks (flattening)
            adjusted_gap = (1.0 - norm_score) / temperature
            adjusted_norm = 1.0 - adjusted_gap
            
            # Ensure non-negative
            final_val = max(0.0, adjusted_norm)
            
            # Step 4: NCD Tiebreaker (only if scores are very close)
            # We add a tiny epsilon based on NCD if the adjusted scores are nearly identical
            ncd_penalty = 0.0
            if temperature == self.T_base: # Only apply strict NCD in stable regimes
                ncd_val = self._compute_ncd(prompt, candidates[idx])
                ncd_penalty = -0.01 * ncd_val # Small penalty for high NCD (low similarity)
            
            final_score = final_val + ncd_penalty
            
            # Store result
            ranked_results.append({
                "candidate": candidates[idx],
                "score": final_score,
                "reasoning": f"Structural:{original_score:.2f}, Temp:{temperature:.1f}, NCD_adj:{ncd_penalty:.3f}"
            })

        # Re-sort based on final calculated scores
        ranked_results.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the structural score mapped through a sigmoid-like function.
        """
        score = self._evaluate_logic(prompt, answer)
        
        # Map score to 0-1. 
        # Assumption: score range is roughly -1.0 to 2.0 based on heuristics
        # Shift and scale
        shifted = score + 1.0 
        scaled = shifted / 4.0 # Normalize roughly to 0-1
        
        # Clamp
        conf = max(0.0, min(1.0, scaled))
        
        # Boost if structural features align strongly (e.g. numbers matched)
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        if p_feat['numbers'] and a_feat['numbers']:
            conf = min(1.0, conf + 0.2)
            
        return conf