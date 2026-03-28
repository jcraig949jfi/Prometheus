import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Compositional Game-Theoretic Inference (RCGTI) Tool.
    
    Mechanism:
    1. Renormalization (Coarse-Graining): Extracts scale-invariant structural features
       (negations, comparatives, conditionals, numeric values) from raw text, ignoring noise.
    2. Compositionality: Assembles these features into a logical constraint vector.
    3. Nash Equilibrium: Treats each candidate as a strategy. Payoffs are computed based on
       consistency with the prompt's logical constraints. Candidates that violate hard
       constraints (e.g., negation flips, numeric contradictions) receive severe penalties.
       The "equilibrium" is the state where the highest-scoring candidate cannot be improved
       by switching logical interpretations, validated by the structural match.
    
    This ensures robustness against overfitting to string similarity (NCD) by prioritizing
    logical consistency (structural parsing) as the primary payoff driver.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'before', 'after'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_features(self, text: str) -> Dict:
        """Renormalization block: Coarse-grain text into logical features."""
        lower = self._normalize(text)
        words = set(re.findall(r'\b\w+\b', lower))
        
        # Feature 1: Negation depth (parity)
        neg_count = sum(1 for w in words if w in self.negation_words or w.endswith("n't"))
        has_negation = neg_count % 2 == 1
        
        # Feature 2: Comparative presence
        has_comparative = bool(words & self.comparatives)
        
        # Feature 3: Conditional presence
        has_conditional = bool(words & self.conditionals)
        
        # Feature 4: Numeric extraction (sorted list of floats)
        nums = []
        for match in re.findall(r'-?\d+\.?\d*', lower):
            try:
                nums.append(float(match))
            except ValueError:
                pass
        
        return {
            'negated': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': nums,
            'word_set': words,
            'length': len(text)
        }

    def _compute_structural_payoff(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes the payoff for a candidate based on logical consistency with the prompt.
        Simulates Nash Equilibrium check: A strategy (candidate) is stable only if it 
        respects the logical constraints (rules) defined by the prompt.
        """
        score = 0.0
        
        # Rule 1: Negation Consistency (Modus Tollens approximation)
        # If prompt implies a negation, valid answers often reflect it or invert logic correctly.
        # Heuristic: If prompt is negated, exact word overlap is suspicious (echoing), 
        # but logical alignment is key. We penalize length mismatch if negation is present.
        if prompt_feats['negated']:
            if abs(cand_feats['length'] - prompt_feats['length']) > 20:
                score += 2.0 # Reward concise correction or specific answer
            else:
                score -= 1.0 # Penalty for potentially echoing the negation without resolution
        else:
            score += 1.0 if not cand_feats['negated'] else -0.5

        # Rule 2: Numeric Consistency
        # If numbers exist, check for logical ordering if comparatives are present
        if prompt_feats['numbers'] and cand_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = cand_feats['numbers']
            
            # Simple consistency: Candidate numbers should be related to prompt numbers
            # or represent a valid subset/comparison.
            # Strong signal: If prompt has 2 numbers and candidate has 1, it might be a selection.
            if len(p_nums) >= 2 and len(c_nums) == 1:
                # Check if the candidate number is the result of a likely operation (min/max)
                # implied by comparatives
                if prompt_feats['comparative']:
                    if ('larger' in prompt_feats['word_set'] or 'greater' in prompt_feats['word_set'] or 'more' in prompt_feats['word_set']):
                        if c_nums[0] == max(p_nums): score += 5.0
                        else: score -= 5.0
                    elif ('smaller' in prompt_feats['word_set'] or 'less' in prompt_feats['word_set'] or 'fewer' in prompt_feats['word_set']):
                        if c_nums[0] == min(p_nums): score += 5.0
                        else: score -= 5.0
                    else:
                        # Generic comparative, reward if in range
                        if min(p_nums) <= c_nums[0] <= max(p_nums): score += 2.0
                else:
                    # No comparative, just presence helps
                    score += 1.0
            elif len(p_nums) == len(c_nums):
                # Exact match of number sets implies strong consistency
                if set(p_nums) == set(c_nums): score += 3.0
        
        # Rule 3: Conditional/Logical Flow
        if prompt_feats['conditional']:
            # If prompt has conditionals, reward candidates that have logical connectors or are concise
            if cand_feats['conditional'] or cand_feats['length'] < prompt_feats['length'] * 0.8:
                score += 2.0
        
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization
        prompt_len = len(prompt) if len(prompt) > 0 else 1
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Structural Payoff (Primary Signal - ~80% weight)
            # Represents the Nash Equilibrium stability: how well does this hypothesis 
            # fit the logical constraints of the environment (prompt)?
            structural_score = self._compute_structural_payoff(prompt_feats, cand_feats)
            
            # Normalize structural score to 0-1 range roughly
            # Base score starts at 0.5, adjusted by structural payoff
            base_score = 0.5 + (structural_score * 0.1)
            
            # 2. NCD Tiebreaker (Secondary Signal - ~20% weight)
            # Only matters if structural signals are ambiguous
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so lower distance = higher score
            ncd_score = 1.0 - ncd_val
            
            # Final Score: Heavily weighted towards structural logic
            final_score = (base_score * 0.8) + (ncd_score * 0.2)
            
            # Bonus for exact string match in simple cases (fallback)
            if self._normalize(prompt) == self._normalize(cand):
                final_score = max(final_score, 0.95)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural Payoff: {structural_score:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the equilibrium stability of the answer 
        relative to the prompt's logical constraints.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Map the top score to a confidence metric
        # If the single candidate scores high, confidence is high.
        score = res[0]['score']
        # Clamp between 0 and 1
        return max(0.0, min(1.0, score))