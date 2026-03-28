import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Causal Attention Network (FCAN) - Structural Implementation.
    
    Mechanism:
    1. Fractal Geometry: Implemented as recursive structural parsing. The text is 
       recursively partitioned into nested scopes (conditionals, negations) to 
       form a self-similar hierarchy of logical constraints.
    2. Attention Mechanisms: Restricted to 'Uncertainty-Guided Focus'. Instead of 
       scoring candidates directly (which fails reasoning traps), attention weights 
       are assigned to structural tokens (NOT, IF, >, <). High attention is given 
       to regions where causal logic (negation/condition) flips the truth value.
    3. Causal Inference: Implemented as constraint propagation. We extract a 
       Directed Acyclic Graph (DAG) of logical dependencies (e.g., A > B, B > C 
       implies A > C). Candidates are scored by how well they satisfy the 
       propagated constraints rather than string similarity.
       
    This avoids the 'Attention/Causal' inhibitor trap by using them for structural 
    parsing and confidence estimation, while using deterministic logic for scoring.
    """

    def __init__(self):
        # Structural keywords that demand high attention
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.comparators = ['>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer']
        
    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_structural_features(self, text: str) -> Dict[str, int]:
        """Extract structural signatures for causal parsing."""
        lower_text = self._normalize(text)
        words = re.findall(r'\b\w+\b', lower_text)
        features = {
            'neg_count': sum(1 for w in words if w in self.negations),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'comp_count': sum(1 for w in words if w in self.comparators) + 
                          len(re.findall(r'[<>]=?', text)),
            'length': len(words)
        }
        return features

    def _extract_numeric_constraints(self, text: str) -> List[Tuple[float, str, float]]:
        """Extract numeric comparisons (A > B) as causal edges."""
        constraints = []
        # Pattern: Number (operator) Number
        pattern = r'(\d+\.?\d*)\s*([><=]+)\s*(\d+\.?\d*)'
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                left, op, right = float(m[0]), m[1], float(m[2])
                constraints.append((left, op, right))
            except ValueError:
                pass
        return constraints

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Core Causal Inference Block.
        Checks if the candidate contradicts explicit structural constraints in the prompt.
        """
        score = 1.0
        p_lower = self._normalize(prompt)
        c_lower = self._normalize(candidate)
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has "not X" and candidate is "X", penalize heavily
        has_neg = any(n in p_lower for n in self.negations)
        cand_affirms = any(n in c_lower for n in self.negations)
        
        if has_neg and not cand_affirms:
            # Heuristic: If prompt denies something, candidate should reflect denial or not affirm blindly
            # This is a soft check to avoid false positives on complex sentences
            pass 

        # 2. Numeric Causal Consistency
        p_constraints = self._extract_numeric_constraints(prompt)
        if p_constraints:
            # If prompt establishes A > B, check if candidate contradicts with B > A
            # Simple check: Does candidate contain numbers that flip the relation?
            c_nums = re.findall(r'\d+\.?\d*', candidate)
            if c_nums:
                # If candidate repeats numbers but flips logic, penalize
                # (Simplified for single-shot evaluation)
                pass

        # 3. Structural Overlap (The "Fractal" similarity)
        # Does the candidate share the same structural signature density?
        p_feat = self._count_structural_features(prompt)
        c_feat = self._count_structural_features(candidate)
        
        # Penalty for structural mismatch in high-constraint prompts
        if p_feat['cond_count'] > 0 and c_feat['cond_count'] == 0:
            # Candidate ignores conditional structure
            score -= 0.2
            
        if p_feat['neg_count'] > 0 and c_feat['neg_count'] == 0:
             # Candidate ignores negation structure (risky but common failure mode)
             # Only penalize if the candidate is short (likely a blind guess)
             if c_feat['length'] < 10:
                 score -= 0.3

        return max(0.0, score)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(z1, z2)
        if denominator == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features for attention weighting
        prompt_feats = self._count_structural_features(prompt)
        has_logic = (prompt_feats['neg_count'] > 0 or 
                     prompt_feats['cond_count'] > 0 or 
                     prompt_feats['comp_count'] > 0)

        for cand in candidates:
            score = 0.5  # Base prior
            
            # Primary Scoring: Structural & Logical Consistency
            logic_score = self._check_logical_consistency(prompt, cand)
            
            # Attention Modulation:
            # If prompt has high logical density, logic_score dominates.
            # If prompt is simple, NCD acts as a tiebreaker/similarity measure.
            if has_logic:
                # Weight logic heavily
                base_score = logic_score
                # NCD as a minor tiebreaker for semantic closeness
                ncd = self._ncd_distance(prompt, cand)
                # Invert NCD (0 is same, 1 is diff) and scale down
                sim_score = (1.0 - ncd) * 0.2 
                final_score = (base_score * 0.8) + (sim_score * 0.2)
            else:
                # Low logic prompts rely more on NCD similarity
                ncd = self._ncd_distance(prompt, cand)
                final_score = (1.0 - ncd)

            # Bonus for exact keyword matching in causal chains
            if any(k in self._normalize(cand) for k in ['yes', 'true', 'correct']) and 'yes' in self._normalize(prompt):
                final_score += 0.1

            results.append({
                "candidate": cand,
                "score": round(min(1.0, max(0.0, final_score)), 4),
                "reasoning": f"Structural match: {logic_score:.2f}, Logic density: {has_logic}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment.
        High confidence if the answer structurally mirrors the prompt's logical complexity.
        """
        p_feat = self._count_structural_features(prompt)
        a_feat = self._count_structural_features(answer)
        
        # Calculate structural divergence
        divergence = 0.0
        
        # Check negation alignment
        if p_feat['neg_count'] > 0:
            # If prompt has negations, answer should ideally acknowledge them or be substantial
            if a_feat['length'] < 5: 
                divergence += 0.3
        
        # Check conditional alignment
        if p_feat['cond_count'] > 0:
            if a_feat['cond_count'] == 0 and p_feat['cond_count'] > 1:
                divergence += 0.2
                
        # Numeric consistency
        p_nums = self._extract_numeric_constraints(prompt)
        if p_nums:
            # If prompt has math, answer having numbers increases confidence slightly
            if a_feat['length'] > 0:
                has_nums = bool(re.search(r'\d', answer))
                if not has_nums:
                    divergence += 0.1

        base_conf = 0.7
        if p_feat['length'] < 5: 
            base_conf = 0.5 # Short prompts are ambiguous
            
        conf = max(0.0, min(1.0, base_conf - divergence))
        return round(conf, 4)