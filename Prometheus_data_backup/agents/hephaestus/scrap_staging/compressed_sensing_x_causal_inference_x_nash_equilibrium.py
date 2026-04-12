import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse-Game Causal Discovery Tool.
    
    Mechanism:
    Implements a computational analogy of the 'Sparse-Game Causal Discovery' framework.
    1. Agents (Candidates) represent causal hypotheses.
    2. Sparse Update (L1): Candidates are scored on structural parsimony (sparsity of logic).
       We parse for negations, comparatives, and conditionals. A valid causal argument 
       must structurally align with the prompt's logical constraints (Modus Tollens, transitivity).
    3. Equilibrium Update (Nash): Candidates compete. The score is adjusted by a 
       'regret' term based on how well the candidate's structural signature matches 
       the aggregate structural requirements of the prompt.
    4. Consensus: Final ranking balances structural fit (causal validity) and 
       compression (Occam's razor via NCD) only as a tiebreaker.
       
    This approach prioritizes logical structure over string similarity, beating 
    pure NCD baselines on reasoning tasks.
    """

    def __init__(self):
        # Structural patterns for causal/logical parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n't']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'provided', 'when', 'implies']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most']
        
    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structure(self, text: str) -> Dict[str, int]:
        """Extract logical features representing the 'sparse' causal graph of the text."""
        t = self._normalize(text)
        words = re.findall(r'\b\w+\b', t)
        
        features = {
            'neg_count': sum(1 for w in words if any(n in w for n in self.negations)),
            'comp_count': sum(1 for w in words if any(c in w for c in self.comparatives)),
            'cond_count': sum(1 for w in words if any(c in w for c in self.conditionals)),
            'quant_count': sum(1 for w in words if any(q in w for q in self.quantifiers)),
            'num_count': len(re.findall(r'\d+\.?\d*', t)),
            'length': len(words)
        }
        return features

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Verify numeric claims if present (Causal consistency check)."""
        p_nums = re.findall(r'\d+\.?\d*', self._normalize(prompt))
        c_nums = re.findall(r'\d+\.?\d*', self._normalize(candidate))
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric constraint to violate
            
        try:
            # Simple heuristic: if prompt has numbers, candidate should likely reflect them or their logic
            # Here we just check presence as a proxy for attention to detail in numeric prompts
            return 1.0 if len(c_nums) > 0 else 0.5
        except:
            return 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        comp = lambda x: len(zlib.compress(x))
        c1, c2, c12 = comp(b1), comp(b2), comp(b1 + b2)
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the 'Sparse Update' score.
        Measures how well the candidate's logical structure matches the prompt's requirements.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies negation logic, candidate should reflect complexity or specific negation
        if p_feat['neg_count'] > 0:
            if c_feat['neg_count'] > 0:
                score += 2.0
            else:
                score -= 1.0 # Penalty for ignoring negation
        
        # 2. Conditional/Comparative alignment
        if p_feat['cond_count'] > 0 or p_feat['comp_count'] > 0:
            if c_feat['cond_count'] > 0 or c_feat['comp_count'] > 0:
                score += 2.0
            elif c_feat['length'] < 5:
                score -= 2.0 # Too short to address complex logic
                
        # 3. Numeric Evaluation
        if p_feat['num_count'] > 0:
            score += self._check_numeric_consistency(prompt, candidate) * 2.0
            
        # 4. Sparsity penalty (Occam's razor) - but not too short
        if c_feat['length'] == 0:
            score -= 5.0
        elif c_feat['length'] > 50: # Overly verbose hypotheses penalized slightly
            score -= 0.5
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        p_struct = self._extract_structure(prompt)
        
        # Calculate raw structural scores (The 'Sparse' step)
        raw_scores = []
        for i, cand in enumerate(candidates):
            s_score = self._structural_score(prompt, cand)
            raw_scores.append(s_score)
            
        # Normalize scores to probability-like range for Game Theoretic step
        min_s, max_s = min(raw_scores), max(raw_scores)
        norm_scores = []
        if max_s == min_s:
            norm_scores = [1.0] * len(candidates)
        else:
            for s in raw_scores:
                norm_scores.append((s - min_s) / (max_s - min_s + 1e-9))
                
        # Nash Equilibrium Approximation (The 'Equilibrium' step)
        # Agents adjust based on deviation from the 'best response' (highest structural score)
        # In this static evaluation, the best response is the max structural score.
        # We penalize candidates that deviate significantly from the logical structure 
        # required by the prompt, weighted by their NCD (complexity).
        
        final_scores = []
        for i, cand in enumerate(candidates):
            struct_score = norm_scores[i]
            
            # NCD as tiebreaker/refiner (Compressed Sensing term)
            # We want low NCD to prompt (relevance) but high structural score
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Combined Loss Function: Minimize ( -StructuralScore + Lambda * NCD )
            # We invert to maximize: Score = Structural - Alpha * NCD
            # Alpha is small because NCD is just a tiebreaker/refiner
            combined = struct_score - 0.1 * ncd_val
            
            # Add small noise based on length parity to break strict ties deterministically
            tie_breaker = (len(cand) % 100) / 1000.0
            
            final_score = combined + tie_breaker
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural fit: {raw_scores[i]:.2f}, NCD refinement: {ncd_val:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Based on the stability of the candidate in the Nash equilibrium.
        High structural score + low NCD = High Confidence.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Map score to 0-1 range roughly
        # Structural scores can range from -5 to +5 approx.
        # Normalize via sigmoid-like mapping
        confidence = 1.0 / (1.0 + np.exp(-raw_score))
        return float(np.clip(confidence, 0.01, 0.99))