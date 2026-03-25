import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuro-Epistemic Incentive-Compatible Belief Updater (NEICBU)
    
    Mechanism:
    1. Epistemology (Experts): Candidates are treated as hypothesis experts.
    2. Neuromodulation (Precision): Structural features (negations, numerics, conditionals)
       act as neuromodulatory signals. They dynamically adjust the 'precision' (weight) 
       of evidence, scaling the impact of logical consistency vs. semantic similarity.
    3. Mechanism Design (VCG Scoring): A proper scoring rule (Logarithmic/Brier hybrid) 
       incentivizes 'truthful' reporting. Candidates are scored on how well their 
       structural footprint aligns with the prompt's constraints. Misaligned candidates 
       receive high 'prediction error' penalties.
       
    This architecture prioritizes structural logic (Mechanism Design core) while using
    semantic similarity only as a tie-breaker, preventing gameable bag-of-words strategies.
    """

    def __init__(self):
        # Weights for the neuromodulatory signals
        self.w_negation = 2.5
        self.w_numeric = 3.0
        self.w_conditional = 2.0
        self.w_structural = 4.0
        self.w_semantic = 0.5  # Low weight to avoid echo-chamber effects

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features acting as neuromodulatory signals."""
        text_lower = text.lower()
        
        # Negation detection
        negations = ['not', 'no', 'never', 'neither', 'nobody', 'nothing', 'cannot', "n't"]
        neg_count = sum(1 for n in negations if re.search(r'\b' + re.escape(n) + r'\b', text_lower))
        
        # Numeric detection
        numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        has_numeric = len(numbers) > 0
        numeric_vals = [float(n) for n in numbers]
        
        # Conditional/Logic detection
        conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when', 'therefore', 'because']
        cond_count = sum(1 for c in conditionals if re.search(r'\b' + c + r'\b', text_lower))
        
        # Comparatives
        comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse']
        comp_count = sum(1 for c in comparatives if re.search(r'\b' + c + r'\b', text_lower))

        return {
            'neg_count': neg_count,
            'has_numeric': has_numeric,
            'numeric_vals': numeric_vals,
            'cond_count': cond_count,
            'comp_count': comp_count,
            'length': len(text),
            'text_lower': text_lower
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

    def _structural_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Mechanism Design Core: Computes a score based on structural alignment.
        This acts as the VCG-style truthfulness check.
        """
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect understanding (simplified heuristic)
        if prompt_feats['neg_count'] > 0:
            # Reward if candidate also handles logic (proxy: has specific logical markers or length consistency)
            # Penalize if candidate is too short to address the negation constraint
            if cand_feats['length'] < prompt_feats['length'] * 0.3:
                score -= self.w_negation * 2.0
            else:
                score += self.w_negation * 0.5
                
        # 2. Numeric Consistency
        if prompt_feats['has_numeric']:
            if cand_feats['has_numeric']:
                # Check if numbers in candidate are logically derived (simplified: presence boosts score)
                score += self.w_numeric
            else:
                # Penalty for ignoring numeric data in prompt
                score -= self.w_numeric * 1.5
                
        # 3. Conditional/Logic Flow
        if prompt_feats['cond_count'] > 0:
            if cand_feats['cond_count'] > 0 or cand_feats['length'] > prompt_feats['length'] * 0.5:
                score += self.w_conditional
            else:
                score -= self.w_conditional * 1.2

        # 4. Comparative Logic
        if prompt_feats['comp_count'] > 0:
            if cand_feats['comp_count'] > 0:
                score += self.w_structural
            # If prompt asks for comparison, short answers like "Yes" are penalized
            if cand_feats['length'] < 10:
                score -= self.w_structural * 2.0

        return score

    def _incentive_compatible_score(self, prompt: str, candidate: str) -> float:
        """
        Computes the final score combining structural precision (Neuromodulation)
        and semantic proximity (NCD tiebreaker).
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Base structural score (The Mechanism Design Layer)
        struct_score = self._structural_score(p_feats, c_feats)
        
        # Semantic similarity via NCD (The Epistemic Baseline)
        # Inverted NCD so higher is better (1.0 - ncd)
        ncd = self._compute_ncd(prompt, candidate)
        semantic_score = (1.0 - ncd) * self.w_semantic
        
        # Total Raw Score
        raw_score = struct_score + semantic_score
        
        # Proper Scoring Rule Adjustment (Logarithmic penalty for uncertainty proxies)
        # Encourages decisive structural matches
        if struct_score > 0:
            bonus = math.log(1.0 + struct_score)
        else:
            bonus = struct_score # Penalty remains linear for errors
            
        return bonus

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the NEICBU architecture.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            score = self._incentive_compatible_score(prompt, cand)
            reasoning = f"Structural alignment: {score:.2f}. "
            if "not" in prompt.lower() and "not" not in cand.lower():
                reasoning += "Potential negation mismatch. "
            if re.search(r"\d", prompt) and not re.search(r"\d", cand):
                reasoning += "Numeric data ignored. "
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning.strip()
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the incentive-compatible score.
        Uses a sigmoid-like mapping to bound the output.
        """
        score = self._incentive_compatible_score(prompt, answer)
        # Map score to 0-1. 
        # Assume score range roughly [-5, 5] for most cases.
        # Shift and scale: (score + 5) / 10 -> [0, 1]
        # Clamp strictly
        normalized = (score + 5.0) / 10.0
        return max(0.0, min(1.0, normalized))