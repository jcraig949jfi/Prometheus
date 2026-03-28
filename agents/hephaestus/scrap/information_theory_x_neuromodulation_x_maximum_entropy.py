import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Maximum-Entropy Inference Engine (Approximated).
    
    Mechanism:
    1. Structural Parsing (MaxEnt Constraint): Extracts logical features (negations, 
       comparatives, conditionals, numeric values) to form the "sufficient statistics" 
       of the prompt-candidate pair. This defines the base energy landscape.
    
    2. Dopaminergic Modulator (Prediction Error): Calculates the Mutual Information 
       gain between the prompt's logical structure and the candidate's structure. 
       High overlap in logical operators (e.g., both have negation) reduces prediction 
       error, increasing the score. Mismatched logic (e.g., prompt has "not", candidate 
       lacks it) generates high error, lowering the score.
       
    3. Serotonergic Gain Control (Entropy/Temperature): Estimates the uncertainty 
       (entropy) of the candidate set based on structural diversity. 
       - Low diversity (all candidates look similar) -> Low entropy -> High gain (sharp scores).
       - High diversity -> High entropy -> Low gain (flattened scores, encouraging exploration).
       
    4. Scoring: Final score = Base Structural Match + (Dopamine * Serotonin Gain).
       NCD is used strictly as a tiebreaker when structural signals are weak.
    """

    def __init__(self):
        self.logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self.cond_ops = ['if', 'then', 'else', 'when', 'unless', 'provided']
        self.comp_ops = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<', '>=', '<=']
        
    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural sufficient statistics from text."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Boolean features
        has_negation = any(op in t_lower for op in self.logic_ops)
        has_conditional = any(op in t_lower for op in self.cond_ops)
        has_comparative = any(op in t_lower for op in self.comp_ops)
        
        # Numeric extraction
        numbers = []
        for w in words:
            try:
                # Handle basic floats/integers
                if '.' in w or w.isdigit():
                    numbers.append(float(w))
            except ValueError:
                continue
        
        # Length as a proxy for complexity
        length = len(words)
        
        return {
            'neg': has_negation,
            'cond': has_conditional,
            'comp': has_comparative,
            'nums': numbers,
            'len': length,
            'raw': text
        }

    def _compute_structural_match(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Computes compatibility based on logical consistency (MaxEnt constraints).
        Returns a base score [0, 1].
        """
        score = 0.5 # Base prior
        
        # Negation consistency: If prompt has negation, candidate should ideally reflect it 
        # or be a direct contradiction. Here we assume valid answers respect the logical frame.
        # Simple heuristic: Matching negation status adds stability.
        if p_feat['neg'] == c_feat['neg']:
            score += 0.2
            
        # Conditional consistency
        if p_feat['cond'] == c_feat['cond']:
            score += 0.1
            
        # Comparative consistency
        if p_feat['comp'] == c_feat['comp']:
            score += 0.1
            
        # Numeric logic check (simplified)
        if p_feat['nums'] and c_feat['nums']:
            # If both have numbers, check if they are in similar magnitude range or order
            # This is a crude approximation of numeric reasoning
            p_avg = sum(p_feat['nums']) / len(p_feat['nums'])
            c_avg = sum(c_feat['nums']) / len(c_feat['nums'])
            if abs(p_avg - c_avg) < (p_avg * 0.5 + 0.1): # Within 50% tolerance
                score += 0.2
            else:
                score -= 0.1 # Penalty for magnitude mismatch
                
        return min(1.0, max(0.0, score))

    def _compute_dopamine(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Dopaminergic signal: Estimates Mutual Information gain.
        High value if candidate resolves logical constraints imposed by prompt.
        """
        mi_gain = 0.0
        
        # Reward for matching specific logical operators (Information Gain)
        if p_feat['neg'] and c_feat['neg']:
            mi_gain += 0.3
        elif p_feat['neg'] and not c_feat['neg']:
            mi_gain -= 0.2 # Prediction error
            
        if p_feat['cond'] and c_feat['cond']:
            mi_gain += 0.2
            
        if p_feat['comp'] and c_feat['comp']:
            mi_gain += 0.2
            
        # Numeric precision bonus
        if p_feat['nums'] and c_feat['nums']:
             mi_gain += 0.1
             
        return mi_gain

    def _compute_serotonin_gain(self, candidates: List[str]) -> float:
        """
        Serotonergic gain: Scales output based on entropy of the candidate set.
        High entropy (diverse candidates) -> Lower gain (flatten distribution).
        Low entropy (similar candidates) -> Higher gain (sharpen distribution).
        """
        if len(candidates) < 2:
            return 1.0
            
        # Compute pairwise structural diversity
        feats = [self._extract_features(c) for c in candidates]
        
        # Simple entropy proxy: Count unique structural signatures
        signatures = set()
        for f in feats:
            sig = (f['neg'], f['cond'], f['comp'], len(f['nums']) > 0)
            signatures.add(sig)
            
        diversity = len(signatures) / len(candidates) # 0 to 1
        
        # Inverse relationship: High diversity -> Lower gain (Temperature > 1)
        # Low diversity -> Higher gain (Temperature < 1)
        # Gain = 1.0 + (1.0 - diversity) 
        # If diverse (1.0), gain = 1.0. If uniform (0.0), gain = 2.0.
        # Actually, let's make it: High uncertainty (diversity) -> Reduce confidence magnitude
        gain = 1.0 + (1.0 - diversity) 
        return gain

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z1 = zlib.compress(s1.encode())
        z2 = zlib.compress(s2.encode())
        z12 = zlib.compress((s1 + s2).encode())
        
        len1 = len(z1)
        len2 = len(z2)
        len12 = len(z12)
        
        if len12 == 0: return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        serotonin_gain = self._compute_serotonin_gain(candidates)
        
        scored_candidates = []
        
        for cand in candidates:
            c_feat = self._extract_features(cand)
            
            # 1. Base structural match (MaxEnt core)
            base_score = self._compute_structural_match(p_feat, c_feat)
            
            # 2. Dopamine modulation (MI gain)
            dopamine = self._compute_dopamine(p_feat, c_feat)
            
            # 3. Apply Serotonin gain
            final_score = base_score + (dopamine * serotonin_gain)
            
            # NCD Tiebreaker (only if structural score is ambiguous/close to prior)
            # We add a tiny epsilon based on NCD to break ties deterministically
            ncd_val = self._ncd(prompt, cand)
            # Invert NCD so lower distance = higher score contribution
            ncd_bonus = (1.0 - ncd_val) * 0.001 
            
            total_score = final_score + ncd_bonus
            
            reasoning = f"Structural Match: {base_score:.2f}, Dopamine(MI): {dopamine:.2f}, Gain: {serotonin_gain:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": reasoning
            })
            
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and logical consistency.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        # Base alignment
        base = self._compute_structural_match(p_feat, a_feat)
        
        # Dopamine boost
        dop = self._compute_dopamine(p_feat, a_feat)
        
        # Raw score
        raw = base + dop
        
        # Clamp to 0-1
        conf = max(0.0, min(1.0, raw))
        return round(conf, 4)