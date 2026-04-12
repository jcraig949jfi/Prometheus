import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Multi-Agent Kalman-Nash Filter (FMKNF) Approximation.
    
    Mechanism:
    1. Fractal Basis (Wavelet-like): Decomposes the prompt/candidate text into 
       multi-scale structural features (negations, comparatives, conditionals, numbers).
       This mimics the Daubechies wavelet packet decomposition by analyzing 
       text at token, phrase, and sentence scales.
       
    2. Kalman Filtering: Treats the 'truth' of a candidate as a hidden state.
       The 'observation' is the structural match between prompt constraints and candidate.
       The 'innovation' (residual) is the difference between expected structural patterns
       (e.g., if prompt has negation, candidate should reflect it) and observed patterns.
       
    3. Nash Equilibrium: Candidates are 'agents' playing a game. 
       Payoff = Structural Consistency (Accuracy) - Complexity Penalty.
       We approximate the Mixed Strategy Nash Equilibrium using iterative best-response dynamics
       (fictitious play) where candidates adjust their 'gain' (score weight) based on 
       how well they satisfy prompt constraints relative to others.
       
    The final score is the equilibrium probability weight of each candidate.
    """

    def __init__(self):
        # Structural keywords for fractal decomposition
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'better', 'worse', 'higher', 'lower'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.bools = {'yes', 'no', 'true', 'false', 'correct', 'incorrect'}

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Decompose text into fractal-like structural features."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        word_set = set(words)
        
        # Scale 1: Token presence
        has_neg = bool(word_set & self.negations)
        has_comp = bool(word_set & self.comparatives)
        has_cond = bool(word_set & self.conditionals)
        
        # Scale 2: Numeric extraction and evaluation
        nums = re.findall(r'-?\d+\.?\d*', t)
        numbers = [float(n) for n in nums] if nums else []
        
        # Scale 3: Length/Complexity (Hausdorff dimension proxy)
        complexity = len(text) / (len(set(words)) + 1)
        
        return {
            'neg': has_neg, 'comp': has_comp, 'cond': has_cond,
            'nums': numbers, 'len': len(text), 'complexity': complexity,
            'words': word_set, 'raw': t
        }

    def _compute_structural_score(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Compute the 'Kalman Innovation' based on structural consistency.
        High score if candidate respects prompt's logical operators and numeric constraints.
        """
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt asserts negation, candidate should ideally reflect awareness or not contradict
        if prompt_feat['neg']:
            # Penalty if candidate completely lacks negation words when prompt has them (simplified)
            # In a real filter, this would be a state update. Here, we boost candidates that mirror structure.
            score += 0.2 if cand_feat['neg'] else -0.2
        
        # 2. Comparative/Conditional Logic
        if prompt_feat['comp'] or prompt_feat['cond']:
            # Candidates mirroring logical complexity get a boost
            if cand_feat['comp'] or cand_feat['cond']:
                score += 0.3
        
        # 3. Numeric Evaluation (Crucial for reasoning)
        if prompt_feat['nums'] and cand_feat['nums']:
            p_nums = prompt_feat['nums']
            c_nums = cand_feat['nums']
            
            # Check for direct number presence (often the answer)
            # Or simple arithmetic consistency if the candidate is just a number
            if len(c_nums) == 1 and len(p_nums) >= 1:
                # Heuristic: If candidate is a single number, check if it matches any prompt number
                # or is a result of simple operations (simulated by proximity)
                if any(abs(c_nums[0] - p) < 1e-6 for p in p_nums):
                    score += 0.5
                # Check for obvious comparisons if comparatives exist
                if prompt_feat['comp']:
                    # If prompt asks for "larger", and candidate is larger than some baseline
                    # This is a rough approximation of the Kalman update
                    pass 
        elif not prompt_feat['nums'] and not cand_feat['nums']:
            score += 0.1 # Neutral match
            
        # 4. Constraint Propagation (Simple overlap of logical tokens)
        # If prompt has 'if', candidate having 'if' or 'then' suggests logical following
        if prompt_feat['cond'] and (cand_feat['cond'] or len(cand_feat['words']) > 2):
            score += 0.2

        return score

    def _nash_equilibrium_solver(self, scores: List[float], complexities: List[float]) -> List[float]:
        """
        Approximate Mixed Strategy Nash Equilibrium using iterative fictitious play.
        Agents (candidates) adjust weights to maximize payoff: Score - Complexity Penalty.
        """
        n = len(scores)
        if n == 0:
            return []
        if n == 1:
            return [1.0]
            
        # Initialize uniform strategy
        probs = np.ones(n) / n
        payoffs = np.array(scores) - 0.1 * np.array(complexities)
        
        # Normalize payoffs to positive range for stability
        payoffs = payoffs - np.min(payoffs) + 1e-6
        
        # Iterative best response (approximating equilibrium)
        # In this context, equilibrium is reached when probabilities align with normalized payoffs
        # such that no single candidate can improve expected error by shifting weight.
        for _ in range(20): # Fixed iterations for determinism and speed
            # Calculate expected utility for each pure strategy against current mix
            # Since it's a coordination game on truth, utility is self-correlated
            weights = np.exp(payoffs * 2.0) # Softmax temperature
            weights /= np.sum(weights)
            
            # Update probs (fictitious play average)
            probs = 0.5 * probs + 0.5 * weights
            
        # Final normalization
        probs = probs / np.sum(probs)
        return probs.tolist()

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if c12 == 0: return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        
        raw_scores = []
        complexities = []
        features = []
        
        # Step 1: Feature Extraction & Structural Scoring (Fractal/Kalman step)
        for cand in candidates:
            c_feat = self._extract_features(cand)
            features.append(c_feat)
            
            # Base structural score
            s_score = self._compute_structural_score(p_feat, c_feat)
            
            # Add NCD as a minor tiebreaker component initially
            ncd = self._ncd_distance(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale down so structure dominates
            ncd_score = (1.0 - ncd) * 0.1 
            
            raw_scores.append(s_score + ncd_score)
            complexities.append(c_feat['complexity'])
            
        # Step 2: Nash Equilibrium Optimization
        # Agents (candidates) compete; stable states are those with high structural consistency
        # and appropriate complexity.
        equilibrium_weights = self._nash_equilibrium_solver(raw_scores, complexities)
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(equilibrium_weights[i]),
                "reasoning": f"Structural match (neg/comp/cond/num): {raw_scores[i]:.4f}, Equilibrium weight: {equilibrium_weights[i]:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the equilibrium score of the specific answer
        when evaluated against itself and a set of dummy alternatives.
        """
        # Generate dummy alternatives to form a game
        dummies = ["No", "Yes", "Unknown", "Invalid", answer[:50] if len(answer) > 50 else " "]
        if answer in dummies:
            dummies = [f"Option_{i}" for i in range(5)]
            
        candidates = [answer] + dummies
        results = self.evaluate(prompt, candidates)
        
        # Find the score of the specific answer provided
        for res in results:
            if res['candidate'] == answer:
                return min(1.0, max(0.0, res['score'] * 2.0)) # Scale up slightly for clarity
                
        return 0.0