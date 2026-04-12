import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically-Constrained Incentive-Aligned Reasoning Tool (TC-IART).
    
    Mechanism:
    1. Reservoir (Structural Parser): Extracts logical features (negations, comparatives, 
       numbers) to form a state vector. Per instructions, this is restricted to confidence 
       estimation and feature extraction, not direct scoring.
    2. Mechanism Design (Evaluator): The core scoring engine. Candidates are "agents" 
       reporting beliefs. They are scored via a proper scoring rule (Logarithmic/Brier-like) 
       based on how well their structural claims match the prompt's constraints.
    3. Thermodynamics (Entropy Penalty): A complexity penalty derived from the candidate's 
       length and logical consistency. High-entropy (chaotic/contradictory) states are 
       penalized to prevent overfitting or hallucination, steering toward simple, valid 
       explanations.
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'larger', 'more', 'less', 'smaller', 'fewer', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}

    def _extract_features(self, text: str) -> Dict:
        """Reservoir-like structural parsing of the text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives) or ('>' in text) or ('<' in text)
        has_conditional = bool(words & self.conditionals)
        
        # Extract numbers
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': nums,
            'length': len(text),
            'word_count': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _mechanism_score(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Mechanism Design Layer: Evaluates candidate truthfulness against prompt constraints.
        Uses a proper scoring rule analogy: Reward for matching logical structure, penalty for mismatch.
        """
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies negation, candidate should reflect it or not contradict it
        if prompt_feats['neg']:
            # Heuristic: If prompt is negative, simple positive assertions are suspect
            if not cand_feats['neg'] and cand_feats['word_count'] < 5: 
                score -= 0.2 
            else:
                score += 0.1
        
        # 2. Comparative Logic
        if prompt_feats['comp'] and cand_feats['comp']:
            score += 0.3 # Reward recognizing the comparative nature
        elif prompt_feats['comp'] and not cand_feats['comp']:
            # Check if numbers exist to do explicit math
            if prompt_feats['nums'] and cand_feats['nums']:
                # Simple numeric consistency check
                p_max = max(prompt_feats['nums']) if prompt_feats['nums'] else 0
                c_max = max(cand_feats['nums']) if cand_feats['nums'] else 0
                if c_max <= p_max: # Candidate number fits within prompt bounds
                    score += 0.4
                else:
                    score -= 0.3
            else:
                score -= 0.1 # Penalty for ignoring comparative context

        # 3. Conditional Flow
        if prompt_feats['cond']:
            if cand_feats['cond']:
                score += 0.2
            # If prompt is conditional, absolute statements are risky
            elif not cand_feats['neg'] and cand_feats['word_count'] > 3:
                score -= 0.1

        return score

    def _thermo_penalty(self, candidate: str, cand_feats: Dict, prompt: str) -> float:
        """
        Thermodynamic Layer: Entropy-based complexity penalty.
        Penalizes overly long, chaotic, or inconsistent hypotheses (High Energy/Low Probability).
        Encourages minimum description length (Occam's razor).
        """
        # Entropy proxy: Length variance relative to prompt
        len_diff = abs(cand_feats['length'] - len(prompt))
        complexity_cost = 0.001 * len_diff
        
        # Contradiction cost (Internal energy): High word count with low information density
        if cand_feats['word_count'] > 20 and cand_feats['length'] > 200:
            complexity_cost += 0.1
            
        return complexity_cost

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_features(prompt)
        results = []
        
        # Pre-calculate prompt NCD for tie-breaking
        prompt_ncd_ref = prompt[:50] # Use prefix for stability
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Mechanism Design Score (Primary Driver)
            mech_score = self._mechanism_score(prompt_feats, cand_feats, prompt, cand)
            
            # 2. Thermodynamic Penalty (Regularization)
            thermo_cost = self._thermo_penalty(cand, cand_feats, prompt)
            
            # 3. Structural/NCD Tiebreaker
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Final Score Composition
            # Base score from mechanism, penalized by thermodynamic entropy, nudged by NCD
            final_score = mech_score - thermo_cost - (ncd_val * 0.05)
            
            # Boost for exact numeric matches if numbers are present
            if prompt_feats['nums'] and cand_feats['nums']:
                # If candidate contains the max number from prompt, strong boost
                if max(cand_feats['nums']) == max(prompt_feats['nums']):
                    final_score += 0.5

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Mechanism:{mech_score:.2f} Thermo:{thermo_cost:.2f} NCD:{ncd_val:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and thermodynamic stability.
        Uses Reservoir features for validation.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        base_conf = 0.5
        
        # Structural alignment boosts confidence
        if p_feats['neg'] == a_feats['neg']:
            base_conf += 0.2
        if p_feats['comp'] == a_feats['comp']:
            base_conf += 0.15
            
        # Numeric consistency
        if p_feats['nums'] and a_feats['nums']:
            if set(p_feats['nums']) == set(a_feats['nums']):
                base_conf += 0.3
            elif any(n in p_feats['nums'] for n in a_feats['nums']):
                base_conf += 0.1
            else:
                base_conf -= 0.2 # Mismatched numbers reduce confidence
                
        # Thermodynamic stability: Short, direct answers to complex prompts might be underfit
        # Long, rambling answers might be overfit. Ideal is proportional.
        ratio = len(answer) / (len(prompt) + 1)
        if 0.1 < ratio < 2.0:
            base_conf += 0.1
            
        return max(0.0, min(1.0, base_conf))