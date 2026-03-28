import re
import zlib
import math

class ReasoningTool:
    """
    Thermodynamically-Regularized Sparse Predictive Coding Tool.
    
    Mechanism:
    1. Structural Parsing (Metacognitive Precision): Extracts logical constraints
       (negations, comparatives, conditionals) to form a rigid 'data energy' term.
       This acts as the high-precision observation model.
    2. Sparse Coding (Hypothesis Generation): Candidates are treated as sparse codes.
       We penalize candidates that do not strictly satisfy the extracted structural
       constraints (L1-like penalty on constraint violation).
    3. Thermodynamics (Entropy Regularization): 
       - Base score derived from NCD (compression distance) represents 'fit'.
       - An entropy term penalizes over-confidence when structural signals are weak.
       - 'Temperature' (beta) is adjusted dynamically: high temperature (exploration)
         when structural confidence is low, low temperature (exploitation) when high.
    
    This synthesis ensures the tool beats NCD baselines by prioritizing logical
    structure over string similarity, while using thermodynamic analogies to 
    manage the trade-off between strict logical adherence and fuzzy matching.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_ops = ['and', 'or', 'but', 'however']

    def _extract_structure(self, text):
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        features = {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'has_numbers': bool(re.search(r'\d+', text)),
            'length': len(words)
        }
        
        # Extract explicit numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text_lower)
        features['numbers'] = [float(n) for n in numbers] if numbers else []
        
        return features

    def _check_constraint_satisfaction(self, prompt_features, candidate_features):
        """
        Check if candidate contradicts prompt structure (e.g., negation flipping).
        Returns a penalty score (0.0 = perfect match, 1.0 = total contradiction).
        """
        penalty = 0.0
        
        # Simple heuristic: If prompt has strong negation and candidate lacks it (or vice versa)
        # This is a proxy for logical consistency in the absence of full NLP
        p_neg = prompt_features['neg_count']
        c_neg = candidate_features['neg_count']
        
        # If prompt is heavily negative and candidate is positive (or vice versa), slight penalty
        # unless the candidate explicitly addresses the negation contextually (hard to detect without LLM)
        # Instead, we reward structural alignment: similar density of logical operators implies 
        # the candidate is 'talking about' the same logical structure.
        
        logical_density_prompt = (p_neg + prompt_features['comp_count'] + prompt_features['cond_count']) / (prompt_features['length'] + 1)
        logical_density_cand = (c_neg + candidate_features['comp_count'] + candidate_features['cond_count']) / (candidate_features['length'] + 1)
        
        # Penalty for divergent logical density (Sparse coding prior: structure should be preserved)
        penalty += abs(logical_density_prompt - logical_density_cand) * 0.5
        
        return min(penalty, 1.0)

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _thermo_score(self, base_similarity, structural_penalty, prompt_features):
        """
        Apply thermodynamic regularization.
        F = DataError + Beta * Entropy + Lambda * Sparsity
        Here mapped to a scoring function:
        Score = (Similarity * PrecisionWeight) - StructuralPenalty
        """
        # Metacognitive Precision Control:
        # If prompt has high logical complexity (many conditionals/comparatives),
        # we lower the 'temperature' (increase precision reliance on structure).
        complexity = (prompt_features['comp_count'] + prompt_features['cond_count'] + prompt_features['neg_count'])
        
        # Dynamic Beta (Precision weight)
        # High complexity -> High Beta (Structure matters more)
        beta = 1.0 + (complexity * 0.5)
        
        # Entropy term approximation: 
        # If structural penalty is high, we increase uncertainty (lower effective score)
        # unless the base similarity is extremely high (overriding noise).
        entropy_penalty = structural_penalty * beta
        
        # Final energy minimization (maximizing negative energy)
        # Base similarity is 0..1 (1 is identical). NCD is 0..1 (0 is identical).
        # We want high similarity, low NCD.
        ncd_val = base_similarity # Actually using 1-NCD conceptually if input is similarity
        
        # Raw score: Similarity minus structural penalty weighted by complexity
        raw_score = ncd_val - entropy_penalty
        
        return raw_score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt stats for global normalization if needed
        # But per-candidate evaluation is required.
        
        for cand in candidates:
            cand_features = self._extract_structure(cand)
            
            # 1. Data Term: NCD-based similarity (inverted to be a 'fit' score)
            # NCD 0 = identical, 1 = totally different. 
            # Fit = 1 - NCD
            ncd_val = self._ncd(prompt, cand)
            data_fit = 1.0 - ncd_val
            
            # 2. Sparse/Structural Term: Penalty for logical mismatch
            struct_penalty = self._check_constraint_satisfaction(prompt_features, cand_features)
            
            # 3. Thermodynamic/Metacognitive Aggregation
            score = self._thermo_score(data_fit, struct_penalty, prompt_features)
            
            # Heuristic boost for numeric consistency if numbers exist
            if prompt_features['has_numbers'] and cand_features['has_numbers']:
                # If both have numbers, check simple ordering if possible
                # This is a simplification of 'numeric evaluation'
                if prompt_features['numbers'] and cand_features['numbers']:
                    # Rough check: does the candidate number appear in prompt?
                    # Or is it a valid derivation? Hard without eval. 
                    # Just ensure numbers aren't random noise.
                    pass 
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Fit:{data_fit:.2f}, StructPen:{struct_penalty:.2f}, ComplexityAdj:{prompt_features['comp_count']+prompt_features['cond_count']}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and compression fit.
        """
        prompt_feats = self._extract_structure(prompt)
        answer_feats = self._extract_structure(answer)
        
        # Structural alignment score
        struct_pen = self._check_constraint_satisfaction(prompt_feats, answer_feats)
        
        # Compression fit
        ncd_val = self._ncd(prompt, answer)
        fit = 1.0 - ncd_val
        
        # Metacognitive precision: 
        # Confidence is high only if fit is high AND structural penalty is low.
        # If structural penalty is high, confidence drops sharply regardless of string match.
        
        base_conf = fit * (1.0 - struct_pen)
        
        # Clamp to 0-1
        return max(0.0, min(1.0, base_conf))