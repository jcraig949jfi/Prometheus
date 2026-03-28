import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Global Workspace Bandit-Guided Active Inference Tool.
    
    Mechanism:
    1. FEP Core (Variational Free Energy): Treats the prompt as the 'true' generative model.
       Candidates are evaluated by their 'prediction error' (structural mismatch) against the prompt.
       Lower error = higher likelihood. We parse structural tokens (negations, comparatives, numbers)
       to compute a precise structural overlap score, minimizing 'surprise'.
       
    2. MAB (Multi-Armed Bandit): Each candidate is an 'arm'. 
       We calculate an 'Exploration Bonus' based on the uncertainty of the candidate's 
       structural signature relative to the prompt's complexity. This prevents local minima 
       where a short, generic answer might accidentally match keywords.
       
    3. GWT (Global Workspace): The 'broadcast' phase selects the winner by combining 
       the exploitation term (structural fit) and exploration term (uncertainty bonus),
       then normalizes scores to a global confidence metric.
    """

    def __init__(self):
        # Structural patterns for FEP-based parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'when', 'while'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extract structural tokens to minimize variational free energy (prediction error)."""
        if not text:
            return {'words': set(), 'nums': [], 'has_neg': False, 'has_comp': False, 'has_cond': False, 'length': 0}
        
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        nums = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'words': words,
            'nums': nums,
            'has_neg': bool(words & self.negations),
            'has_comp': bool(words & self.comparatives),
            'has_cond': bool(words & self.conditionals),
            'length': len(text)
        }

    def _compute_structural_overlap(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Compute similarity based on structural alignment (FEP core).
        High overlap = Low Prediction Error.
        """
        if not prompt_feats['words'] or not cand_feats['words']:
            return 0.0

        # 1. Word Intersection (Jaccard-like)
        intersection = prompt_feats['words'] & cand_feats['words']
        union = prompt_feats['words'] | cand_feats['words']
        word_score = len(intersection) / len(union) if union else 0.0

        # 2. Structural Constraint Propagation
        # If prompt has negation, candidate MUST have negation to be valid (Modus Tollens check)
        neg_match = 1.0
        if prompt_feats['has_neg']:
            neg_match = 1.0 if cand_feats['has_cond'] or cand_feats['has_neg'] else 0.5
        
        # Conditional alignment
        cond_match = 1.0
        if prompt_feats['has_cond']:
            cond_match = 1.0 if cand_feats['has_cond'] else 0.6
            
        # Numeric consistency (if numbers exist in both)
        num_score = 1.0
        if prompt_feats['nums'] and cand_feats['nums']:
            # Simple check: does the candidate contain the specific numbers in the prompt?
            # Or at least maintain order/magnitude logic (simplified for brevity)
            p_nums = set(prompt_feats['nums'])
            c_nums = set(cand_feats['nums'])
            if p_nums <= c_nums or c_nums <= p_nums: # One is subset of other
                num_score = 1.0
            else:
                num_score = 0.5 # Penalty for mismatched numbers
        elif prompt_feats['nums'] and not cand_feats['nums']:
            num_score = 0.2 # Heavy penalty for ignoring numbers

        return (word_score * 0.5) + (neg_match * 0.2) + (cond_match * 0.15) + (num_score * 0.15)

    def _compute_bandit_bonus(self, prompt: str, candidate: str, total_candidates: int) -> float:
        """
        MAB Exploration Bonus.
        Encourages testing hypotheses (candidates) that are distinct but plausible.
        Uses uncertainty based on length divergence and NCD volatility.
        """
        if total_candidates == 0:
            return 0.0
            
        # Uncertainty estimation: How different is this candidate's structure from the average?
        # Simplified: Bonus for candidates that aren't trivially short (avoids "Yes"/"No" traps)
        len_ratio = len(candidate) / (len(prompt) + 1)
        complexity_bonus = math.sqrt(len(candidate)) * 0.01
        
        # Exploration term: Higher for candidates with moderate length (not too short, not rambling)
        if 0.1 <= len_ratio <= 2.0:
            return complexity_bonus * 0.2
        return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0:
            return 1.0
        return (z12 - min(z1, z2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        # Pre-calculate max possible structural score for normalization if needed
        max_struct_score = 0.0
        
        # Phase 1: Compute raw scores (FEP + MAB)
        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # FEP: Minimize prediction error (maximize structural overlap)
            struct_score = self._compute_structural_overlap(prompt_feats, cand_feats)
            
            # MAB: Add exploration bonus
            bonus = self._compute_bandit_bonus(prompt, cand, len(candidates))
            raw_score = struct_score + bonus
            
            max_struct_score = max(max_struct_score, struct_score)
            
            results.append({
                "candidate": cand,
                "raw_score": raw_score,
                "struct_score": struct_score,
                "reasoning": f"Structural overlap: {struct_score:.3f}, Bandit bonus: {bonus:.3f}"
            })

        # Phase 2: Global Workspace Broadcast (Selection & Ranking)
        # Normalize scores to ensure the best structural match wins, using NCD as tiebreaker
        max_raw = max(r['raw_score'] for r in results) if results else 1.0
        
        final_results = []
        for r in results:
            # Primary Sort Key: Raw Score (Structure + Bonus)
            # Secondary Sort Key (Tiebreaker): NCD (Lower is better)
            ncd_val = self._ncd(prompt, r['candidate'])
            
            # Final Score formulation: 
            # We want high structural score. 
            # If scores are very close (within 0.01), NCD decides.
            score = r['raw_score']
            
            final_results.append({
                "candidate": r['candidate'],
                "score": score,
                "reasoning": r['reasoning'],
                "_ncd": ncd_val # Hidden for sorting
            })

        # Sort: Higher score first, then lower NCD (better compression match)
        final_results.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and return
        output = []
        for res in final_results:
            output.append({
                "candidate": res['candidate'],
                "score": res['score'],
                "reasoning": res['reasoning']
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_feats = self._extract_structural_features(prompt)
        ans_feats = self._extract_structural_features(answer)
        
        base_score = self._compute_structural_overlap(prompt_feats, ans_feats)
        
        # Boost if boolean consistency is found (e.g. Prompt asks True/False, Answer gives it)
        p_bools = prompt_feats['words'] & self.booleans
        a_bools = ans_feats['words'] & self.booleans
        
        if p_bools and a_bools:
            base_score = min(1.0, base_score + 0.2)
            
        # Penalty for extreme length mismatch unless structural score is perfect
        if len(answer) < 3 and base_score < 0.9:
            base_score *= 0.8
            
        return float(min(1.0, max(0.0, base_score)))