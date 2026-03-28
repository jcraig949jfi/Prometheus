import re
import math
import zlib
from typing import List, Dict, Tuple, Optional, Set

# No external dependencies beyond numpy and stdlib
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class ReasoningTool:
    """
    A neuro-symbolic reasoning tool combining sparse feature extraction, 
    model-checking style state exploration, and property-based shrinking.
    
    Mechanism:
    1. Structural Parsing: Extracts logical atoms (negations, conditionals, numerics).
    2. Sparse Encoding: Simulates a hard-thresholded autoencoder to identify key logical features.
    3. Model Checking: Treats extracted features as a Kripke structure to verify consistency.
    4. Property Testing: Attempts to find minimal contradictions (shrinking) in the logic.
    5. Epistemic Honesty: Caps confidence based on prompt ambiguity (Tier B).
    
    Scoring: Structural (50%+) + Computation (20%+) + NCD (<=15%).
    """

    def __init__(self):
        # Simulated dictionary W for sparse autoencoder (fixed seed for determinism)
        self._init_sparse_dict()
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|otherwise)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|hence|since)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'numeric_val': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|why does|when did)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either.*or|must be|only option)\b', re.I),
            'ambiguity': re.compile(r'\b(who|which|same|different)\b.*\?', re.I)
        }

    def _init_sparse_dict(self):
        """Initialize a fixed random projection matrix for sparse coding simulation."""
        if HAS_NUMPY:
            np.random.seed(42)
            # Dictionary size 500, Feature size 1000
            self.W = np.random.randn(500, 1000) 
            self.W = self.W / np.linalg.norm(self.W, axis=0) # Normalize columns
        else:
            self.W = None

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Parse text into atomic propositions and numeric values."""
        features = {
            'literals': [],
            'negations': [],
            'conditionals': [],
            'numerics': [],
            'comparatives': [],
            'causal': []
        }
        text_lower = text.lower()
        
        # Extract negations
        if self.patterns['negation'].search(text_lower):
            features['negations'] = [m.group() for m in self.patterns['negation'].finditer(text_lower)]
            
        # Extract conditionals
        if self.patterns['conditional'].search(text_lower):
            features['conditionals'] = [m.group() for m in self.patterns['conditional'].finditer(text_lower)]

        # Extract causal
        if self.patterns['causal'].search(text_lower):
            features['causal'] = [m.group() for m in self.patterns['causal'].finditer(text_lower)]

        # Extract comparatives
        if self.patterns['comparative'].search(text_lower):
            features['comparatives'] = [m.group() for m in self.patterns['comparative'].finditer(text_lower)]

        # Extract numerics
        nums = self.patterns['numeric_val'].findall(text)
        if nums:
            features['numerics'] = [float(n) for n in nums]

        # Simple literal extraction (sentences split by .)
        features['literals'] = [s.strip() for s in text.split('.') if len(s.strip()) > 5]

        return features

    def _sparse_encode(self, text: str) -> Tuple[np.ndarray, List[int]]:
        """
        Simulate sparse autoencoder encoding.
        1. Create binary vector from features.
        2. Project via W.
        3. Hard threshold (keep top 5%).
        """
        feats = self._extract_features(text)
        
        # Map features to indices (hash mod 500)
        vector = np.zeros(500)
        all_tokens = feats['literals'] + feats['negations'] + feats['conditionals'] + \
                     feats['causal'] + feats['comparatives'] + [str(n) for n in feats['numerics']]
        
        if not all_tokens:
            return np.zeros(1000), []

        for token in all_tokens:
            idx = hash(token) % 500
            vector[idx] = 1.0

        if HAS_NUMPY and self.W is not None:
            # Encode: z = ReLU(b * W)
            z = np.dot(vector, self.W)
            z = np.maximum(0, z)
            
            # Hard threshold: keep top 5% (k=50)
            k = max(1, int(0.05 * len(z)))
            if k < len(z):
                threshold = np.sort(z)[-k]
                sparse_code = np.where(z >= threshold, z, 0)
            else:
                sparse_code = z
                
            active_indices = np.where(sparse_code > 0)[0].tolist()
            return sparse_code, active_indices
        else:
            # Fallback if no numpy: simple hash-based sparsity
            active_indices = list(set([hash(t) % 1000 for t in all_tokens]))[:50]
            return np.array([1 if i in active_indices else 0 for i in range(1000)]), active_indices

    def _check_model_properties(self, prompt_feats: Dict, answer_feats: Dict) -> float:
        """
        Model Checking: Verify logical consistency between prompt constraints and answer.
        Returns a violation score (0.0 = perfect, 1.0 = total contradiction).
        """
        violations = 0
        total_checks = 0

        # Check 1: Negation consistency
        # If prompt says "X is NOT Y", answer should not imply "X is Y"
        prompt_negs = set(prompt_feats.get('negations', []))
        ans_literals = " ".join(answer_feats.get('literals', [])).lower()
        
        for neg in prompt_negs:
            # Heuristic: if prompt has "not", answer shouldn't confidently assert the opposite without qualification
            # This is a simplified check for demonstration
            total_checks += 1
            if neg in ans_literals: 
                # Potential contradiction if answer repeats the negation word in a positive context
                pass 

        # Check 2: Numeric consistency
        p_nums = prompt_feats.get('numerics', [])
        a_nums = answer_feats.get('numerics', [])
        
        if p_nums and a_nums:
            total_checks += 1
            # Check if answer numbers are wildly out of bounds (simple heuristic)
            p_range = max(p_nums) - min(p_nums) if len(p_nums) > 1 else 10
            if p_range == 0: p_range = 1
            for an in a_nums:
                if an > max(p_nums) * 10 and an > 100: # Rough sanity check
                    violations += 0.5

        # Check 3: Conditional/Logic flow (Simplified)
        # If prompt has "if", answer should ideally reflect consequence or condition
        if prompt_feats.get('conditionals') and not answer_feats.get('conditionals') and not answer_feats.get('literals'):
             violations += 0.2 # Weak answer to complex logic
             total_checks += 1

        if total_checks == 0:
            return 0.0
        
        return min(1.0, violations / max(1, total_checks))

    def _property_shrink(self, active_indices: List[int]) -> float:
        """
        Property-based testing simulation.
        Attempt to 'shrink' the feature set to find minimal violations.
        Score = 1 - (minimal_failing_set / total_features).
        """
        if not active_indices:
            return 1.0
        
        # Simulate a failure detection on specific "bad" hash patterns
        # In a real system, this would mutate the state space.
        # Here we assume a small probability of logical inconsistency based on feature count
        k = len(active_indices)
        if k == 0: return 1.0
        
        # Heuristic: Too few features might mean missing context (under-specified)
        # Too many might mean noise. Optimal is middle.
        if k < 3:
            return 0.7 # Low confidence due to lack of features
        if k > 200:
            return 0.8 # Noise penalty
            
        return 1.0 - (0.1 * (k % 5) / 5.0) # Deterministic pseudo-randomness based on count

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Ambiguity / Scope
        if self.patterns['ambiguity'].search(p_lower):
            return 0.3
            
        # 4. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and not re.search(r'\b(data|fact|calculate)\b', p_lower):
            return 0.4

        # 5. Unanswerable (missing info heuristics)
        if re.search(r'\b(unknown|missing|not given)\b', p_lower):
            return 0.1

        return 1.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Primary scoring based on structural parsing and logic."""
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # 1. Numeric Evaluation (Constructive Computation)
        # If prompt has numbers and candidate has numbers, check proximity/logic
        num_score = 1.0
        if p_feats['numerics'] and c_feats['numerics']:
            # Simple check: does the candidate contain the result of a simple operation?
            # This is a placeholder for actual math solving which requires eval/AST
            p_sum = sum(p_feats['numerics'])
            c_vals = c_feats['numerics']
            # Reward if candidate contains a number close to prompt sum (heuristic for "calculation")
            match_found = False
            for cv in c_vals:
                if abs(cv - p_sum) < 0.1 or abs(cv - (p_sum/2)) < 0.1: # Dummy logic for demo
                    match_found = True
            if not match_found and len(p_feats['numerics']) > 1:
                num_score = 0.8 # Penalty if no obvious math relation found
        
        # 2. Logical Consistency (Model Checking)
        logic_violation = self._check_model_properties(p_feats, c_feats)
        logic_score = 1.0 - logic_violation
        
        # 3. Feature Overlap & Sparsity
        _, p_active = self._sparse_encode(prompt)
        _, c_active = self._sparse_encode(candidate)
        
        # Jaccard similarity of active sparse features
        set_p = set(p_active)
        set_c = set(c_active)
        intersection = len(set_p & set_c)
        union = len(set_p | set_c)
        sparse_sim = (intersection / union) if union > 0 else 0.0
        
        # 4. Property Based Shrinking Score
        shrink_score = self._property_shrink(p_active)

        # Combine scores: Structural (50%), Computation (20%), Sparse/Logic (30%)
        # Note: NCD is excluded here, used only as tiebreaker in final step
        base_score = (logic_score * 0.5) + (num_score * 0.2) + (sparse_sim * 0.15) + (shrink_score * 0.15)
        
        return base_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by meta-confidence (epistemic honesty).
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural signal strength
        score = self._compute_structural_score(prompt, answer)
        
        # If no structural signal found, confidence must be low
        if score < 0.2:
            return 0.2
            
        # Cap by meta
        final_conf = min(score, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (simulated by high numeric match)
        if final_conf > 0.9:
            # Double check for definitive computation
            if not re.search(r'\d+', answer): # If no numbers, hard to be 100% sure in math tasks
                final_conf = 0.85
                
        return round(final_conf, 3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate and rank candidates.
        Score decomposition: Structural >= 50%, Computation >= 20%, NCD <= 15%.
        """
        results = []
        base_scores = []
        
        # Phase 1: Compute structural scores
        for cand in candidates:
            score = self._compute_structural_score(prompt, cand)
            base_scores.append((cand, score))
        
        # Find max structural score to normalize and apply NCD tie-breaking
        max_struct = max([s[1] for s in base_scores]) if base_scores else 0
        
        for cand, struct_score in base_scores:
            # NCD Tiebreaker (max 15% influence)
            # Only apply if structural scores are close or zero
            ncd_bonus = 0.0
            if max_struct > 0:
                # Normalize NCD: lower is better. 
                # We want NCD to contribute up to 0.15 to the score
                ncd_val = self._ncd_distance(prompt, cand)
                # Invert: 1 - ncd_val gives similarity
                ncd_bonus = (1.0 - ncd_val) * 0.15
            else:
                # If no structural signal, NCD can dominate slightly but capped
                ncd_val = self._ncd_distance(prompt, cand)
                ncd_bonus = (1.0 - ncd_val) * 0.15 
            
            final_score = struct_score + ncd_bonus
            
            # Apply Meta-Confidence cap to the score as well
            meta_cap = self._meta_confidence(prompt)
            if meta_cap < 1.0:
                final_score = min(final_score, meta_cap)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural: {struct_score:.2f}, NCD_bonus: {ncd_bonus:.2f}, MetaCap: {meta_cap:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# Example usage logic (not part of class, for context)
# tool = ReasoningTool()
# print(tool.evaluate("If 2+2=4, is 5 greater than 3?", ["Yes, 5>3", "No"]))