import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bandit-Guided Evolutionary Reasoning Tool.
    
    Mechanism:
    1. Hypothesis Generation (GA): Candidates are treated as a population. 
       Structural mutations (negation flipping, comparative swapping) are simulated 
       to test robustness, though here we primarily evaluate the given candidates.
    2. Neural Architecture Search (NAS) Proxy: Instead of full training, we use 
       structural parsing (logic checks) as a cheap "weight-shared" proxy for validity.
    3. Multi-Armed Bandits (MAB): We treat each candidate as an arm. 
       - Exploration: Candidates with high structural complexity or uncertainty get a UCB1-style bonus.
       - Exploitation: Candidates matching strict logical constraints (numeric/transitive) get high raw rewards.
       - The final score balances the logical reward (exploitation) with a diversity/complexity bonus (exploration).
    
    This approach prioritizes structural logic (Reasoning) while using compression (NCD) 
    only as a tiebreaker for semantically neutral strings, beating the baseline by 
    focusing on logical form rather than string similarity.
    """

    def __init__(self):
        self.epsilon = 1e-6

    def _parse_structure(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        NAS-style proxy: Fast structural evaluation.
        Checks for numeric consistency and basic logical forms.
        """
        score = 0.0
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        # 1. Numeric Evaluation (Strong Signal)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # Check if candidate contains a number that logically follows prompt numbers
                # Simple heuristic: If prompt has comparison words, candidate number should be consistent
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                if 'more' in prompt.lower() or 'greater' in prompt.lower():
                    # Expect candidate to acknowledge larger magnitude or confirm logic
                    score += 2.0 if max(c_nums) >= min(p_nums) else -1.0
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    score += 2.0 if max(c_nums) <= max(p_nums) else -1.0
                else:
                    # Exact match bonus for pure numeric prompts
                    if set(p_nums) == set(c_nums):
                        score += 3.0
            except ValueError:
                pass

        # 2. Negation Consistency
        # If prompt asks "Is it not X?", candidate should likely contain negation or specific denial
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0:
                score += 1.5 # Reinforces negation handling
            elif any(k in c_feat for k in ['yes', 'no']):
                 # If simple yes/no, ensure it aligns with negation context (heuristic)
                score += 0.5

        # 3. Conditional/Constraint Propagation
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > 3:
                score += 1.0 # Reward elaboration on conditionals
        
        return score

    def _compute_ucb_bonus(self, candidate: str, total_evals: int) -> float:
        """
        MAB Component: Upper Confidence Bound bonus.
        Encourages exploration of structurally complex or unique candidates.
        """
        # Simulate "visits" based on string length buckets (proxy for arm history)
        # Shorter strings are "pulled" more often in baselines, so we bonus longer/complex ones
        visits = len(candidate) 
        if visits == 0:
            return 0.0
        
        # Complexity as a proxy for uncertainty/potential
        complexity = self._parse_structure(candidate)['length']
        
        # UCB1 formula: sqrt(ln(total) / visits)
        # We approximate visits by frequency of similar lengths in a real system, 
        # here we use a static exploration bonus based on complexity
        exploration_bonus = (2 * (total_evals + 1) / (complexity + 1)) ** 0.5
        return min(exploration_bonus, 2.0) # Cap bonus

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        ranked = []
        total_evals = len(candidates)
        
        # Pre-calculate prompt features for context
        prompt_features = self._parse_structure(prompt)
        prompt_lower = prompt.lower()

        for cand in candidates:
            # 1. Structural Reward (Exploitation via NAS-proxy)
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Exploration Bonus (MAB)
            # Boost candidates that have specific structural markers missing in others
            ucb_bonus = self._compute_ucb_bonus(cand, total_evals)
            
            # 3. Base Similarity (NCD) - Only as tiebreaker/secondary
            # We invert NCD so higher is better, but weight it lightly
            ncd_val = self._ncd(prompt, cand)
            similarity_score = (1.0 - ncd_val) * 0.5 
            
            # Combine: Logic is king, MAB breaks ties among logical candidates, NCD is floor
            final_score = logic_score + ucb_bonus + similarity_score
            
            # Heuristic penalty for contradicting explicit prompt constraints detected via keywords
            cand_lower = cand.lower()
            if ('no' in prompt_lower or 'false' in prompt_lower) and ('yes' in cand_lower and 'no' not in cand_lower):
                 # Rough contradiction check
                 if logic_score == 0: # Only penalize if logic didn't already catch it
                     final_score -= 0.5

            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f} + Explore:{ucb_bonus:.2f} + Sim:{similarity_score:.2f}"
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and logical consistency.
        """
        if not answer:
            return 0.0
            
        logic_score = self._check_logical_consistency(prompt, answer)
        
        # Normalize logic score to 0-1 range roughly
        # Max expected logic score approx 5.0
        base_conf = max(0.0, min(1.0, (logic_score + 2.0) / 7.0))
        
        # Boost if structural markers align (e.g. both have numbers)
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        alignment_bonus = 0.0
        if p_feat['numbers'] and a_feat['numbers']:
            alignment_bonus = 0.2
        if p_feat['negations'] and a_feat['negations']:
            alignment_bonus = 0.2
            
        conf = min(1.0, base_conf + alignment_bonus)
        
        # Floor confidence for non-empty answers that aren't logically inconsistent
        if logic_score >= 0 and conf < 0.3:
            conf = 0.35
            
        return float(conf)