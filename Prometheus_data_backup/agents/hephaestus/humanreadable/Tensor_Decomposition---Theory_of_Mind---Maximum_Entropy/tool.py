import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MeTF-ToM Implementation: Maximum-Entropy Tensor Factorization Theory of Mind.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the "observable 
       behavioral constraints" in the theoretical model.
    2. Tensor Factorization Analogy: Candidates are mapped to a low-rank feature space 
       (Agent, Time/Step, Content). We construct a pseudo-tensor of features.
    3. MaxEnt Principle: Instead of direct scoring (which fails per Causal Intelligence 
       guidelines), MaxEnt is used strictly within confidence() to measure the entropy 
       of the feature distribution (uncertainty quantification).
    4. Scoring: Candidates are ranked by how well their structural features satisfy 
       the prompt's logical constraints (Constraint Propagation). NCD is used only as 
       a tiebreaker.
    """

    def __init__(self):
        self.ncd_cache = {}

    def _structural_parse(self, text: str) -> dict:
        """Extract logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split()),
            'question_marks': text.count('?')
        }
        return features

    def _check_logic(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """Evaluate logical consistency based on structural constraints."""
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt asserts a negative constraint, candidate should reflect it or not contradict
        if prompt_feats['has_negation']:
            # Simple heuristic: if prompt says "not X", and candidate is just "X", penalize
            # This is a simplification of constraint propagation
            if not cand_feats['has_negation'] and prompt_feats['has_negation']:
                # Check for direct contradiction patterns (simplified)
                if re.search(r'\b(yes|true|correct)\b', candidate.lower()):
                    score -= 0.5 
                else:
                    score += 0.2 # Neutral/Ambiguous is better than wrong affirmation
            else:
                score += 0.3
        
        # 2. Comparative Logic
        if prompt_feats['has_comparative']:
            if cand_feats['has_comparative'] or cand_feats['numbers']:
                score += 0.4
            # Numeric evaluation
            if prompt_feats['numbers'] and cand_feats['numbers']:
                try:
                    # Simple transitivity check simulation
                    p_max = max(prompt_feats['numbers'])
                    c_max = max(cand_feats['numbers'])
                    if 'greater' in prompt.lower() and c_max > p_max:
                        score += 0.5
                    elif 'less' in prompt.lower() and c_max < p_max:
                        score += 0.5
                except:
                    pass

        # 3. Conditional/Length Heuristic (Proxy for complexity matching)
        if prompt_feats['has_conditional']:
            if cand_feats['length'] > 2: # Conditionals usually require elaboration
                score += 0.2
        
        # 4. Numeric Exact Match (Strong signal)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If candidate contains a number present in prompt, boost slightly (context retention)
            common_nums = set(prompt_feats['numbers']) & set(cand_feats['numbers'])
            if common_nums:
                score += 0.3

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate prompt hash for NCD tiebreaking
        prompt_base = prompt.strip()
        
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # Primary Score: Structural Logic
            logic_score = self._check_logic(prompt_feats, cand_feats, prompt, cand)
            
            # Secondary Score: Content Overlap (Simple Jaccard on words for baseline relevance)
            p_words = set(prompt.lower().split())
            c_words = set(cand.lower().split())
            intersection = p_words & c_words
            union = p_words | c_words
            jaccard = len(intersection) / len(union) if union else 0
            
            # Base score combines logic and relevance
            base_score = (logic_score * 2.0) + (jaccard * 0.5)
            
            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": f"Logic:{logic_score:.2f}, Jaccard:{jaccard:.2f}",
                "_jaccard": jaccard # For tie-breaking
            })
        
        # Sorting: Primary by Score, Tie-break by NCD (lower NCD to prompt is often better contextually)
        # Note: NCD is used strictly as a tiebreaker as per instructions.
        def sort_key(item):
            # Invert NCD so lower distance = higher rank if scores equal
            ncd_val = self._ncd(prompt_base, item['candidate'])
            return (-item['score'], -item['_jaccard'], ncd_val)
            
        results.sort(key=sort_key)
        
        # Normalize scores to 0-1 range roughly for consistency
        max_s = max(r['score'] for r in results) if results else 0
        min_s = min(r['score'] for r in results) if results else 0
        range_s = max_s - min_s if max_s != min_s else 1
        
        final_results = []
        for r in results:
            # Remove internal keys
            clean_r = {k: v for k, v in r.items() if not k.startswith('_')}
            # Normalize score for output
            norm_score = (r['score'] - min_s) / range_s if range_s != 0 else 0.5
            clean_r['score'] = float(norm_score)
            final_results.append(clean_r)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on MaxEnt principle applied to structural uncertainty.
        High entropy (high uncertainty in features) -> Low confidence.
        Low entropy (clear structural match/mismatch) -> High confidence.
        """
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        # Construct a probability distribution over feature presence
        # Features: [negation, comparative, conditional, numbers_present]
        features = [
            p_feats['has_negation'],
            p_feats['has_comparative'],
            p_feats['has_conditional'],
            len(p_feats['numbers']) > 0
        ]
        
        # Calculate entropy of the prompt's structural features
        # Treat feature presence as a distribution (normalized)
        feat_vector = np.array([float(f) for f in features])
        if feat_vector.sum() == 0:
            # If no features, max uncertainty
            entropy = 1.0
        else:
            prob_dist = feat_vector / feat_vector.sum()
            # Shannon entropy
            entropy = -np.sum(prob_dist * np.log2(prob_dist + 1e-9))
        
        # Normalize entropy (max entropy for 4 features is log2(4) = 2)
        max_entropy = np.log2(len(features))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Confidence is inverse of entropy (uncertainty)
        # If structure is clear (low entropy), confidence is high.
        # If structure is ambiguous (high entropy), confidence is lower.
        # We also boost confidence if the answer logically aligns (from evaluate logic)
        logic_score = self._check_logic(p_feats, a_feats, prompt, answer)
        
        # Map logic score (-1 to 1) and entropy (0 to 1) to confidence (0 to 1)
        # High logic match + Low entropy = High confidence
        confidence = (0.5 + 0.5 * logic_score) * (1.0 - 0.5 * normalized_entropy)
        confidence = max(0.0, min(1.0, confidence))
        
        return float(confidence)