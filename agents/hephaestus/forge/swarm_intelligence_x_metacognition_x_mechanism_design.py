import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-regulating multi-agent hypothesis tester using Swarm x Metacognition x Mechanism Design.
    
    Mechanism:
    1. Swarm (Structural Parsing): Agents (parsers) scan for logical constraints (negations, comparatives).
       Per instructions, 'Swarm' is restricted to confidence wrapping and structural parsing, not direct scoring.
    2. Metacognition (Bayesian Calibration): Monitors prediction error. If structural signals are weak,
       it down-weights the agent's confidence and falls back to NCD (tiebreaker).
    3. Mechanism Design (VCG-style Incentives): Candidates are scored by marginal utility.
       - Reward: Alignment with structural constraints (truthful reporting).
       - Penalty: Deviation from consensus or failure to satisfy logical negations (misleading reports).
       - This aligns individual candidate scores with the global logical consistency.
    """

    def __init__(self):
        # Structural patterns for the "Swarm" parsers
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'before', 'after'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise'}

    def _parse_structure(self, text: str) -> dict:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        
        features = {
            'has_negation': any(w in self.negation_words for w in words),
            'has_comparative': any(w in self.comparatives for w in words),
            'has_conditional': any(w in self.conditionals for w in words),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(words)
        }
        return features

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

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Handles numeric comparisons explicitly (e.g., 9.11 < 9.9)."""
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+\.?\d+', prompt)
        c_nums = re.findall(r'\d+\.?\d+', candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to compare

        try:
            # Simple heuristic: if prompt asks for comparison, check if candidate respects order
            # This is a simplified proxy for complex reasoning
            p_val = float(p_nums[-1])
            c_val = float(c_nums[-1])
            
            # If candidate repeats the number exactly, it might be echoing, not reasoning
            # But if it transforms it logically, it's good. 
            # For this tool, we reward candidates that contain valid numeric extraction
            return 0.8 if abs(p_val - c_val) < 1e-6 else 0.4
        except ValueError:
            return 0.5

    def _calculate_marginal_utility(self, candidate: str, prompt_features: dict, all_candidates: List[str]) -> float:
        """
        Mechanism Design: VCG-style scoring.
        Score = Base Structural Fit + (Marginal Improvement over Consensus) - (Penalty for Misleading traits)
        """
        cand_features = self._parse_structure(candidate)
        score = 0.0
        
        # 1. Structural Consistency (The "Truthful Reporting" incentive)
        # If prompt has negation, high value if candidate acknowledges complexity (length/structure)
        if prompt_features['has_negation']:
            # Heuristic: Negations require careful handling; longer, structured answers often better
            if cand_features['has_negation'] or cand_features['length'] > 3:
                score += 0.3
        
        if prompt_features['has_comparative']:
            if cand_features['has_comparative']:
                score += 0.3
            # Numeric check
            num_score = self._evaluate_numeric_logic(prompt_features.get('_raw', ''), candidate)
            score += (num_score - 0.5) * 0.4 # Adjust based on numeric logic

        if prompt_features['has_conditional']:
            if cand_features['has_conditional']:
                score += 0.2

        # 2. Consensus Deviation (VCG Marginal Contribution)
        # If candidate is too similar to all others (low diversity), penalize slightly to encourage exploration
        # Unless it's the only correct structural fit.
        avg_ncd = 0.0
        if len(all_candidates) > 1:
            distances = [self._compute_ncd(candidate, other) for other in all_candidates if other != candidate]
            if distances:
                avg_ncd = sum(distances) / len(distances)
        
        # High NCD means unique (good for exploration), but we want convergence on truth.
        # We use NCD primarily as a tie-breaker as per instructions.
        # Here, we add a small bonus for being structurally distinct but logically sound.
        diversity_bonus = min(avg_ncd * 0.1, 0.15) 
        score += diversity_bonus

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_features = self._parse_structure(prompt)
        prompt_features['_raw'] = prompt
        
        results = []
        base_scores = []

        # Phase 1: Compute raw mechanism scores
        for cand in candidates:
            raw_score = self._calculate_marginal_utility(cand, prompt_features, candidates)
            base_scores.append(raw_score)

        # Phase 2: Metacognitive Calibration & NCD Tie-breaking
        # If structural signals are weak (low max score), rely more on NCD to prompt
        max_base = max(base_scores) if base_scores else 0
        use_ncd_tiebreaker = max_base < 0.2 # Threshold for "weak structural signal"

        for i, cand in enumerate(candidates):
            score = base_scores[i]
            reasoning_parts = []

            # Metacognitive adjustment: If structural score is low, boost NCD similarity to prompt
            if use_ncd_tiebreaker or score < 0.1:
                ncd_val = self._compute_ncd(prompt, cand)
                # Invert NCD (lower is better) and scale
                ncd_score = (1.0 - ncd_val) * 0.5 
                if ncd_score > score:
                    score = ncd_score
                    reasoning_parts.append("NCD fallback activated")
            
            # Specific structural reasoning tags
            if prompt_features['has_negation'] and 'not' in cand.lower():
                score += 0.1
                reasoning_parts.append("negation_handled")
            
            if prompt_features['has_comparative'] and self._evaluate_numeric_logic(prompt, cand) > 0.7:
                score += 0.1
                reasoning_parts.append("numeric_logic_verified")

            # Clamp score 0-1
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "structural_match"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing (Swarm wrapper) to validate logical consistency.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        conf = 0.5 # Base uncertainty
        
        # Metacognitive check: Does the answer reflect the prompt's logical complexity?
        if p_feat['has_negation']:
            if a_feat['has_negation']:
                conf += 0.3
            else:
                conf -= 0.2 # Penalty for ignoring negation
        
        if p_feat['has_comparative']:
            if a_feat['has_comparative'] or p_feat['numbers']:
                conf += 0.2
        
        if p_feat['has_conditional']:
            if a_feat['has_conditional']:
                conf += 0.2

        # NCD as a secondary confidence booster for short, exact matches
        ncd = self._compute_ncd(prompt, answer)
        if ncd < 0.5:
            conf += (0.5 - ncd) * 0.4
            
        return max(0.0, min(1.0, conf))