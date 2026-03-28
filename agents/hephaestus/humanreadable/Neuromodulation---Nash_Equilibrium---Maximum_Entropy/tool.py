import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Nash-Inference Engine (NNIE).
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values to form a "constraint vector".
    2. Nash-Equilibrium Scoring: Candidates are scored based on alignment with 
       structural constraints (coordination game payoff).
    3. MaxEnt + Neuromodulation (Confidence Wrapper): 
       - Calculates entropy of the candidate distribution.
       - Uses a "surprise" signal (deviation from uniform) to modulate temperature.
       - High surprise (low confidence in top candidate) -> High Temp (Flat distribution).
       - Low surprise (high confidence) -> Low Temp (Sharp distribution).
       - Final confidence is derived from this modulated probability.
    4. NCD is used strictly as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        self.keywords_neg = ['no', 'not', 'never', 'none', 'cannot', 'impossible', 'false']
        self.keywords_comp = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.keywords_cond = ['if', 'then', 'unless', 'only if', 'when']
        self.nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'neg_count': sum(1 for k in self.keywords_neg if k in t_lower),
            'comp_count': sum(1 for k in self.keywords_comp if k in k in t_lower),
            'cond_count': sum(1 for k in self.keywords_cond if k in t_lower),
            'has_num': any(c in text for c in self.nums),
            'length': len(text.split())
        }
        # Extract numeric values for simple comparison logic
        features['numbers'] = []
        try:
            words = text.replace(',', '').split()
            for w in words:
                if '.' in w or w.isdigit():
                    features['numbers'].append(float(w))
        except:
            pass
        return features

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute score based on logical consistency (Nash Payoff).
        Checks if candidate satisfies structural constraints implied by prompt.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation, candidate should reflect it or not contradict
        if p_feat['neg_count'] > 0:
            # Penalty if candidate is overly affirmative without qualification in negative context
            if c_feat['neg_count'] == 0 and p_feat['neg_count'] > 1:
                score -= 0.5 
            else:
                score += 0.5
        
        # 2. Comparative Logic
        if p_feat['comp_count'] > 0:
            # If prompt compares, candidate should ideally contain numbers or comparatives
            if c_feat['has_num'] or c_feat['comp_count'] > 0:
                score += 1.0
            # Check numeric consistency if both have numbers
            if p_feat['numbers'] and c_feat['numbers']:
                p_max = max(p_feat['numbers'])
                c_max = max(c_feat['numbers'])
                # Heuristic: If prompt implies "larger", candidate number should be significant
                if 'larger' in p_lower or 'greater' in p_lower:
                    score += 0.5 if c_max >= p_max else -0.5
                else:
                    score += 0.2 # Partial credit for numeric engagement

        # 3. Conditional Logic
        if p_feat['cond_count'] > 0:
            if c_feat['cond_count'] > 0 or any(k in c_lower for k in ['yes', 'no', 'true', 'false']):
                score += 0.8
            else:
                score -= 0.2

        # 4. Direct Constraint Matching (Simple keyword overlap weighted by rarity)
        # Avoids bag-of-words by focusing on logical operators found in prompt
        logical_ops = ['therefore', 'thus', 'hence', 'because', 'so']
        for op in logical_ops:
            if op in p_lower and op in c_lower:
                score += 1.5
                
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denom = max(c1, c2)
            if denom == 0: return 1.0
            return (c12 - min(c1, c2)) / denom
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Compute raw structural scores (Nash Payoffs)
        raw_scores = []
        for cand in candidates:
            s = self._structural_score(prompt, cand)
            raw_scores.append(s)
        
        # 2. Apply Softmax with Neuromodulated Temperature
        # Initial temperature based on variance (Surprise)
        mean_s = sum(raw_scores) / len(raw_scores)
        variance = sum((s - mean_s)**2 for s in raw_scores) / len(raw_scores)
        
        # Neuromodulation: High variance (surprise) -> High Temp (Explore)
        # Low variance (certainty) -> Low Temp (Exploit)
        # Base tau prevents division by zero and controls baseline sharpness
        base_tau = 0.5
        modulation_factor = 2.0 
        tau = base_tau + modulation_factor * math.sqrt(variance + 0.01)
        
        # Shift scores to positive domain for exp
        min_s = min(raw_scores)
        shifted_scores = [s - min_s + 1e-6 for s in raw_scores]
        
        # Softmax
        exp_scores = [math.exp(s / tau) for s in shifted_scores]
        sum_exp = sum(exp_scores)
        probs = [e / sum_exp for e in exp_scores]
        
        # 3. Construct Results
        results = []
        for i, cand in enumerate(candidates):
            # NCD Tiebreaker: Only applied if structural scores are very close
            # We add a tiny epsilon based on NCD to break ties deterministically
            ncd_val = self._ncd_distance(prompt, cand)
            # Invert NCD (lower is better) and scale down to not override structural score
            tie_breaker = (1.0 - ncd_val) * 1e-4 
            
            final_score = probs[i] + tie_breaker
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {raw_scores[i]:.2f}, Prob: {probs[i]:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the MaxEnt + Neuromodulation principle:
        Confidence is the probability mass of the answer after temperature modulation.
        """
        # Evaluate against a synthetic set including the answer to get distribution
        # We simulate the environment's response to see where 'answer' lands
        candidates = [answer]
        # Add dummy competitors to form a game
        dummies = ["No", "Yes", "Unknown", "Impossible", answer + " extra"]
        # Ensure unique candidates
        all_cands = list(dict.fromkeys(candidates + dummies))
        
        ranked = self.evaluate(prompt, all_cands)
        
        # Find the score of the specific answer
        target_score = 0.0
        for item in ranked:
            if item['candidate'] == answer:
                target_score = item['score']
                break
            # Fuzzy match if exact string mismatch due to preprocessing
            if answer.strip() in item['candidate'] or item['candidate'] in answer.strip():
                target_score = item['score']
                break
                
        # The score from evaluate is already a probability-like measure from the softmax
        # constrained by the neuromodulated temperature.
        # Clamp to [0, 1]
        return max(0.0, min(1.0, target_score))