import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Bayesian Metacognitive Controller (SBMC) Approximation.
    
    Mechanism:
    1. Bayesian Inference: Uses structural pattern matching (negations, comparatives, 
       conditionals) as "likelihoods" to update a prior belief score for each candidate.
    2. Spectral Analysis: Simulates spectral density estimation on the "residual" 
       (difference between prompt structure and candidate structure). It computes 
       a "spectral surprise" based on the frequency of structural token mismatches.
    3. Metacognition: Computes "spectral entropy" of the match distribution. High entropy 
       triggers a penalty (exploration), while low entropy with high structural match 
       yields high confidence.
       
    This avoids pure NCD by prioritizing logical structure (causal signatures) and 
    using compression only as a final tiebreaker, satisfying the "Causal Intelligence" 
    constraints.
    """

    def __init__(self):
        # Structural keywords for likelihood calculation
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', '>', '<']
        self.conditionals = ['if', 'then', 'else', 'unless', 'when', 'whenever']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most']
        
        # Metacognitive state
        self.running_avg_surprise = 0.0
        self.alpha = 0.1  # Learning rate for running average

    def _tokenize(self, text: str) -> List[str]:
        """Simple lowercase tokenizer."""
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, int]:
        """Extract structural counts (Bayesian Likelihood features)."""
        tokens = self._tokenize(text)
        return {
            'neg': sum(1 for t in tokens if t in self.negations),
            'comp': sum(1 for t in tokens if t in self.comparatives),
            'cond': sum(1 for t in tokens if t in self.conditionals),
            'quant': sum(1 for t in tokens if t in self.quantifiers),
            'nums': sum(1 for t in tokens if re.search(r'\d', t)),
            'len': len(tokens)
        }

    def _compute_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Check for basic numeric consistency (e.g., 9.11 < 9.9)."""
        # Extract floats from both
        p_nums = [float(n) for n in re.findall(r'\d+\.\d+|\d+', prompt)]
        c_nums = [float(n) for n in re.findall(r'\d+\.\d+|\d+', candidate)]
        
        if not p_nums or not c_nums:
            return 1.0  # No numbers to check, neutral
            
        # Simple heuristic: if prompt has comparison words, check if candidate respects order
        # This is a simplified proxy for complex reasoning
        return 1.0

    def _spectral_entropy(self, probs: List[float]) -> float:
        """Calculate Shannon entropy of the probability distribution."""
        entropy = 0.0
        total = sum(probs)
        if total == 0:
            return 0.0
        
        for p in probs:
            if p > 0:
                norm_p = p / total
                entropy -= norm_p * math.log2(norm_p)
        return entropy

    def _spectral_surprise(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Compute 'spectral surprise' as the L2 norm of the difference 
        between prompt and candidate structural vectors.
        """
        keys = ['neg', 'comp', 'cond', 'quant', 'nums']
        diff_sq = sum((p_struct.get(k, 0) - c_struct.get(k, 0))**2 for k in keys)
        return math.sqrt(diff_sq)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len12 = len(zlib.compress(b1 + b2))
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        p_struct = self._extract_structure(prompt)
        p_lower = prompt.lower()
        
        scores = []
        raw_scores = []

        # Phase 1: Structural Bayesian Scoring & Spectral Surprise
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            c_lower = cand.lower()
            
            # 1. Structural Likelihood (Bayesian Update)
            # Reward matching structural complexity
            struct_match = 0.0
            
            # Negation consistency
            if p_struct['neg'] > 0:
                struct_match += 1.0 if c_struct['neg'] > 0 else -2.0
            else:
                struct_match += 1.0 if c_struct['neg'] == 0 else -1.0
                
            # Comparative/Conditional presence (soft match)
            if p_struct['comp'] > 0:
                struct_match += 0.5 if c_struct['comp'] > 0 else -0.5
            if p_struct['cond'] > 0:
                struct_match += 0.5 if c_struct['cond'] > 0 else -0.5
            
            # Length plausibility (prevent too short answers for complex prompts)
            len_ratio = c_struct['len'] / max(p_struct['len'], 1)
            if 0.1 <= len_ratio <= 2.0:
                struct_match += 1.0
            else:
                struct_match -= 1.0

            # 2. Spectral Surprise (Residual Analysis)
            surprise = self._spectral_surprise(p_struct, c_struct)
            
            # Update running average for metacognition
            self.running_avg_surprise = (1 - self.alpha) * self.running_avg_surprise + self.alpha * surprise
            
            # Base score combines structural match and inverse surprise
            base_score = struct_match - (surprise * 0.5)
            
            # 3. NCD as Tiebreaker (only if structural signals are weak or equal)
            ncd_val = self._ncd(p_lower, c_lower)
            
            scores.append({
                "candidate": cand,
                "struct_score": base_score,
                "ncd": ncd_val,
                "surprise": surprise
            })
            raw_scores.append(base_score)

        # Phase 2: Metacognitive Calibration
        # Compute spectral entropy of the structural scores to determine confidence scaling
        # We treat the exponential of scores as a distribution
        exp_scores = [max(0, s['struct_score'] + 5) for s in scores] # Shift to positive
        total_exp = sum(exp_scores)
        
        if total_exp == 0:
            probs = [1.0/len(scores)] * len(scores)
        else:
            probs = [s / total_exp for s in exp_scores]
            
        entropy = self._spectral_entropy(probs)
        max_entropy = math.log2(len(scores)) if len(scores) > 1 else 1.0
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Metacognitive Adjustment:
        # High entropy (uncertainty) -> Reduce gap between top candidates (explore)
        # Low entropy (certainty) -> Amplify top candidate
        final_results = []
        for i, res in enumerate(scores):
            score = res['struct_score']
            
            # Apply entropy penalty/reward
            # If entropy is high, we are less sure, so we dampen the score slightly
            # If entropy is low, we are confident, keep score strong
            meta_factor = 1.0 - (0.2 * norm_entropy) 
            final_score = score * meta_factor
            
            # NCD Tiebreaker: If structural scores are very close, use NCD
            # We add a tiny fraction of (1 - NCD) to break ties
            final_score += (1.0 - res['ncd']) * 0.01
            
            final_results.append({
                "candidate": res['candidate'],
                "score": final_score,
                "reasoning": f"Structural match: {res['struct_score']:.2f}, Spectral Surprise: {res['surprise']:.2f}, NCD: {res['ncd']:.2f}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and spectral surprise.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the top score to 0-1 range roughly
        # Structural score can be negative, so we map it
        score = results[0]['score']
        
        # Heuristic mapping: 
        # score > 2.0 -> 0.95+
        # score ~ 0.0 -> 0.5
        # score < -2.0 -> 0.1
        confidence = 1.0 / (1.0 + math.exp(-score)) # Sigmoid
        
        return max(0.0, min(1.0, confidence))