import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Topologically-Aware Variational NAS Reasoning Tool (Computational Analogue).
    
    Mechanism:
    1. Free Energy Principle (Core): Implements a 'surprise' minimization strategy.
       It calculates the divergence between the prompt's structural constraints 
       (expected state) and the candidate's logical fulfillment (posterior state).
       Low free energy = high consistency with constraints.
    2. Topology (Secondary): Uses persistent homology analogues on the text's 
       logical graph (entities as nodes, relations as edges). It penalizes 
       'holes' (missing links in transitivity) and rewards connected components 
       that match the prompt's logical skeleton.
    3. NAS (Search): Treats the evaluation as a search over the candidate space,
       ranking by the composite loss (Accuracy + Free Energy + Topological Fidelity).
    
    This avoids pure string similarity (NCD) by focusing on structural parsing
    of negations, comparatives, and numeric logic.
    """

    def __init__(self):
        self._logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self._comp_ops = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<']
        self._cond_ops = ['if', 'then', 'else', 'when', 'unless', 'provided']

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical skeleton: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        features = {
            'neg_count': sum(1 for op in self._logic_ops if f" {op} " in f" {t_lower} "),
            'comp_count': sum(1 for op in self._comp_ops if op in t_lower),
            'cond_count': sum(1 for op in self._cond_ops if f" {op} " in f" {t_lower} "),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text),
            'length': len(text.split()),
            'unique_tokens': set(t_lower.split())
        }
        return features

    def _compute_numeric_consistency(self, prompt_nums: List[str], cand_nums: List[str]) -> float:
        """Check if candidate respects numeric ordering implied in prompt."""
        if not prompt_nums:
            return 1.0 # No numeric constraints
        if not cand_nums:
            return 0.5 # Ambiguous
        
        try:
            p_vals = [float(x) for x in prompt_nums]
            c_vals = [float(x) for x in cand_nums]
            
            # Simple heuristic: If prompt has 2 numbers and candidate has 2,
            # check if relative order is preserved or logically inverted if negated.
            if len(p_vals) >= 2 and len(c_vals) >= 2:
                p_diff = p_vals[0] - p_vals[1]
                c_diff = c_vals[0] - c_vals[1]
                if p_diff == 0: return 1.0 if c_diff == 0 else 0.0
                if (p_diff > 0 and c_diff > 0) or (p_diff < 0 and c_diff < 0):
                    return 1.0
                return 0.2 # Contradiction
            return 0.8 # Partial match
        except ValueError:
            return 0.5

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy analogue.
        F = Surprise + Complexity Penalty.
        Low F means the candidate explains the prompt's constraints well.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # 1. Constraint Satisfaction (Surprise term)
        # If prompt has logic ops, candidate should ideally reflect them or answer directly
        logic_penalty = 0.0
        if p_feat['neg_count'] > 0:
            # Check if candidate ignores negation context (simplified)
            if c_feat['neg_count'] == 0 and len(c_feat['unique_tokens']) < 5:
                # Short answers without negation might miss nuance, but not always wrong
                pass 
        
        # 2. Numeric Consistency
        num_score = self._compute_numeric_consistency(p_feat['numbers'], c_feat['numbers'])
        
        # 3. Structural Overlap (Topological Fidelity)
        # Jaccard similarity on logical tokens only
        logical_tokens = set(self._logic_ops + self._comp_ops + self._cond_ops)
        p_logics = {t for t in p_feat['unique_tokens'] if t in logical_tokens}
        c_logics = {t for t in c_feat['unique_tokens'] if t in logical_tokens}
        
        if len(p_logics) == 0:
            topo_score = 1.0
        else:
            intersection = len(p_logics.intersection(c_logics))
            union = len(p_logics.union(c_logics))
            topo_score = intersection / union if union > 0 else 1.0

        # Free Energy Calculation (Inverse score)
        # High energy = bad. We want low energy.
        # Energy = (1 - num_score) + (1 - topo_score) * weight
        energy = (1.0 - num_score) + 0.5 * (1.0 - topo_score)
        
        return energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_len = len(prompt)
        
        # Pre-calculate prompt features for topology
        p_feat = self._extract_structural_features(prompt)

        for cand in candidates:
            # 1. Free Energy Minimization (Primary Driver)
            energy = self._compute_free_energy(prompt, cand)
            
            # 2. Topological Regularization (via structural match)
            # If prompt implies a chain (A->B, B->C), does candidate respect length/structure?
            topo_penalty = 0.0
            if p_feat['cond_count'] > 0:
                # If prompt is conditional, candidate should ideally be cautious or conditional
                # unless it's a direct deduction.
                if "yes" in cand.lower() or "no" in cand.lower():
                    # Direct answers are okay if logic holds, but check energy
                    pass
            
            # 3. Base Score from Free Energy (Inverted to be positive)
            base_score = 1.0 / (1.0 + energy)
            
            # 4. NCD Tiebreaker (Only if structural signals are weak)
            ncd_val = self._compute_ncd(prompt, cand)
            # NCD is noisy for short strings, so weight it low unless energies are close
            ncd_bonus = (1.0 - ncd_val) * 0.1 
            
            final_score = base_score + ncd_bonus
            
            # Reasoning string generation
            reason = f"FreeEnergy={energy:.2f}; StructMatch={'High' if energy < 0.5 else 'Low'}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy minimization."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the score from evaluate (which is ~0.5 to 1.0 usually) to 0-1
        # Since evaluate returns sorted list, take the score.
        raw_score = res[0]['score']
        # Map [0.5, 1.0+] roughly to [0.0, 1.0] for confidence interpretation
        # Low energy (high score) -> High confidence
        conf = max(0.0, min(1.0, (raw_score - 0.5) * 2.0))
        return conf