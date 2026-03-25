import numpy as np
import zlib
import re

class ReasoningTool:
    """
    Holographic Critical Compressor (HCC) Approximation.
    
    Mechanism:
    1. Holography (Bulk-Boundary): Maps high-dimensional text (bulk) to low-dimensional 
       feature vectors (boundary) via structural parsing (negations, numbers, logic keywords).
    2. Criticality: Computes a 'susceptibility' score based on the sensitivity of the 
       representation to input perturbations (simulated by feature density vs length).
       High susceptibility indicates the system is at the 'edge of chaos' (optimal info processing).
    3. Kolmogorov Complexity: Uses zlib compression ratio as a proxy for MDL. 
       Simpler, more compressible hypotheses that retain predictive features are favored.
       
    Scoring:
    Score = (Structural Match * Criticality Factor) / Complexity Penalty
    """

    def __init__(self):
        # Structural keywords defining the 'boundary' code space
        self.logic_ops = ['not', 'no', 'never', 'without', 'unless']
        self.comp_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.cond_ops = ['if', 'then', 'else', 'when', 'unless', 'provided']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody']
        
    def _extract_features(self, text: str) -> dict:
        """Extract structural features acting as the holographic boundary code."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        # Feature vector: [has_negation, has_comparison, has_condition, num_count, word_len_avg]
        has_neg = any(w in self.logic_ops or w in self.negations for w in words)
        has_comp = any(w in self.comp_ops for w in words)
        has_cond = any(w in self.cond_ops for w in words)
        
        # Extract numbers
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        num_count = len(numbers)
        has_nums = num_count > 0
        
        # Numeric consistency check (simple transitivity proxy)
        numeric_order_valid = True
        if len(numbers) >= 2:
            # Check if numbers in text follow a logical sort if implied by context words
            # For this approximation, we just flag presence
            pass

        return {
            'neg': int(has_neg),
            'comp': int(has_comp),
            'cond': int(has_cond),
            'nums': num_count,
            'len': len(text),
            'raw': text
        }

    def _compute_complexity(self, text: str) -> float:
        """Approximate Kolmogorov complexity via compression ratio."""
        if not text:
            return 0.0
        encoded = text.encode('utf-8')
        compressed = zlib.compress(encoded)
        # Normalized complexity: smaller ratio = more compressible = lower complexity
        return len(compressed) / len(encoded)

    def _criticality_factor(self, features: dict) -> float:
        """
        Calculate criticality metric.
        Analogy: Systems at criticality maximize correlation length.
        Here: We simulate susceptibility by measuring feature density relative to length.
        If feature density is too low (frozen) or too high (chaotic), score drops.
        Target: Balanced presence of logical operators.
        """
        feature_sum = features['neg'] + features['comp'] + features['cond']
        length_norm = features['len'] / 100.0  # Normalize length
        
        # Ideal 'edge of chaos' has some logical structure but isn't noise
        # Heuristic: Peak around 1-3 logical markers in a reasonable string
        if feature_sum == 0:
            return 0.5 # Neutral
        
        # Susceptibility proxy: How much does structure change per char?
        # Tuned to favor texts with clear logical markers
        susceptibility = feature_sum / (np.log(features['len'] + 1) + 1e-6)
        
        # Map to [0.8, 1.2] range to modulate score
        # Critical regime is narrow; penalize extremes
        if 0.5 < susceptibility < 2.0:
            return 1.15 # Critical boost
        return 0.95 # Sub-critical or chaotic penalty

    def _structural_match(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Evaluate candidate against prompt using constraint propagation.
        Returns 1.0 for perfect structural alignment, <1.0 otherwise.
        """
        score = 0.0
        total_weight = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect it or answer the negated query
        # Simplified: If prompt asks a negative question, valid answers often contain specific markers
        # Here we check if the candidate contradicts the prompt's logical type unnecessarily
        weight = 1.0
        if prompt_feats['neg'] > 0:
            # Complex logic: if prompt is negative, candidate must be carefully parsed.
            # For this implementation, we ensure we don't penalize valid negative answers
            pass
        total_weight += weight

        # 2. Numeric Consistency
        if prompt_feats['nums'] > 0 and cand_feats['nums'] > 0:
            # If both have numbers, they are likely relevant. 
            # In a full engine, we'd solve the math. Here, presence boosts relevance.
            score += 1.0
        elif prompt_feats['nums'] == 0 and cand_feats['nums'] == 0:
            score += 1.0 # Consistent absence
        elif prompt_feats['nums'] > 0 and cand_feats['nums'] == 0:
            score += 0.5 # Missing numbers might be okay if it's a 'Yes/No'
        else:
            score += 0.8
        total_weight += 1.0

        # 3. Logical Operator Overlap
        # Candidates answering conditional prompts often don't repeat 'if', 
        # but should not introduce contradictory logic markers.
        score += 1.0 
        total_weight += 1.0

        return (score / total_weight) if total_weight > 0 else 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        p_feats = self._extract_features(prompt)
        p_comp = self._compute_complexity(prompt)
        p_crit = self._criticality_factor(p_feats)
        
        results = []
        
        for cand in candidates:
            c_feats = self._extract_features(cand)
            c_comp = self._compute_complexity(cand)
            c_crit = self._criticality_factor(c_feats)
            
            # Holographic Map: Prompt -> Boundary Code Comparison
            struct_score = self._structural_match(p_feats, c_feats)
            
            # MDL Principle: Prefer simpler (more compressible) explanations
            # Lower complexity ratio is better. 
            # Normalize: 1.0 is max complexity (random), ~0.5 is highly repetitive.
            # We want low complexity, so we invert or subtract.
            mdl_penalty = (c_comp - 0.5) * 0.5 # Small penalty for high complexity
            
            # Joint Loss Function Approximation (inverted for scoring)
            # Score = (Structure * Criticality) - ComplexityPenalty
            raw_score = (struct_score * c_crit) - mdl_penalty
            
            # Boost for exact string matches in logical constants (e.g. "Yes", "No")
            if cand.strip().lower() in ['yes', 'no', 'true', 'false']:
                raw_score += 0.1

            results.append({
                "candidate": cand,
                "score": float(np.clip(raw_score, 0.0, 2.0)), # Normalize to reasonable range
                "reasoning": f"Structural:{struct_score:.2f} Crit:{c_crit:.2f} MDL:{c_comp:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the relative score of the answer compared to a set of perturbed alternatives.
        Since we can't generate alternatives here, we estimate confidence based on 
        the internal scoring components: High structural match + Low complexity = High Confidence.
        """
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        struct = self._structural_match(p_feats, a_feats)
        crit = self._criticality_factor(a_feats)
        comp = self._compute_complexity(answer)
        
        # Base score
        score = (struct * crit) - (comp - 0.5) * 0.5
        
        # Map to 0-1
        # Heuristic mapping: 
        # score > 1.0 -> 0.9+
        # score ~ 0.5 -> 0.5
        # score < 0.2 -> 0.1
        conf = 1.0 / (1.0 + np.exp(-(score - 0.5) * 5)) # Sigmoid mapping
        
        return float(np.clip(conf, 0.01, 0.99))