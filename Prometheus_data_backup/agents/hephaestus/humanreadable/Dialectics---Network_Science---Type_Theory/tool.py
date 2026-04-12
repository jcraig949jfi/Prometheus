import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Type-Theoretic Graph Neural Network (DT-GNN) Simulator.
    
    Mechanism:
    1. Thesis (Structural Parsing): Extracts logical constraints (negations, comparatives, 
       conditionals, numbers) from the prompt. This forms the 'dependent type' of the query.
    2. Antithesis (Candidate Evaluation): Evaluates candidates against these constraints.
       Conflicts generate 'dialectical tension' (penalty).
    3. Synthesis (Scoring): Combines structural adherence (primary) with NCD similarity (tiebreaker)
       to produce a validated hypothesis score.
       
    This implements the requested triad by mapping:
    - Dependent Types -> Logical constraint sets derived from grammar.
    - Dialectical Tension -> Penalty score from constraint violation.
    - Proof Assistant -> Deterministic rule-based validator (Modus Tollens/Transitivity).
    """

    def __init__(self):
        self._keywords_neg = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self._keywords_comp = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self._keywords_cond = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self._num_regex = re.compile(r"-?\d+(?:\.\d+)?")

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features representing the 'Dependent Type' of the text."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # 1. Negation flags
        has_negation = bool(words & self._keywords_neg)
        
        # 2. Comparative flags
        has_comparative = bool(words & self._keywords_comp)
        
        # 3. Conditional flags
        has_conditional = bool(words & self._keywords_cond)
        
        # 4. Numeric extraction for evaluation
        numbers = [float(n) for n in self._num_regex.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'word_set': words
        }

    def _check_logical_consistency(self, prompt_feats: Dict, candidate_feats: Dict) -> float:
        """
        Simulates the 'Proof Assistant' checking if the candidate inhabits the type.
        Returns a penalty (0.0 = perfect, 1.0 = contradiction).
        """
        penalty = 0.0
        
        # Modus Tollens / Negation Check
        # If prompt asserts negation, candidate should not assert positive certainty of negated concept
        if prompt_feats['negation']:
            # Heuristic: If prompt denies something, candidate repeating strong affirmations might be wrong
            # This is a simplified simulation of contradiction detection
            if candidate_feats['negation'] and prompt_feats['word_set'] & candidate_feats['word_set']:
                pass # Agreement on negation is good
            elif not candidate_feats['negation'] and len(prompt_feats['word_set'] & candidate_feats['word_set']) > 2:
                penalty += 0.2 # Potential contradiction

        # Numeric Consistency (Transitivity/Comparison)
        if prompt_feats['numbers'] and candidate_feats['numbers']:
            p_nums = prompt_feats['numbers']
            c_nums = candidate_feats['numbers']
            
            # Check if candidate numbers logically follow prompt trends (simplified)
            # If prompt has 'less', candidate number should ideally be smaller or consistent
            if 'less' in prompt_feats['word_set'] or 'fewer' in prompt_feats['word_set']:
                if c_nums and p_nums:
                    # Rough check: does the candidate maintain the direction? 
                    # Since we don't have full semantic parse, we check magnitude consistency
                    if max(c_nums) > max(p_nums) * 1.5: # Arbitrary threshold for "antithesis"
                        penalty += 0.3
            
            elif 'more' in prompt_feats['word_set'] or 'greater' in prompt_feats['word_set']:
                if c_nums and p_nums:
                    if min(c_nums) < min(p_nums) * 0.5:
                        penalty += 0.3

        return min(penalty, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_features(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # 1. Dialectical Tension (Logical Penalty)
            tension = self._check_logical_consistency(prompt_feats, cand_feats)
            
            # 2. Structural Overlap (Thesis Alignment)
            # Jaccard similarity of structural keywords as a base score
            common_words = prompt_feats['word_set'] & cand_feats['word_set']
            union_words = prompt_feats['word_set'] | cand_feats['word_set']
            jaccard = len(common_words) / len(union_words) if union_words else 0.0
            
            # Base score from structural alignment
            base_score = jaccard
            
            # Apply tension penalty (Antithesis reduces score)
            adjusted_score = base_score * (1.0 - tension)
            
            # NCD Tiebreaker (Synthesis refinement)
            # If scores are close, NCD decides. We add a tiny fraction of NCD inverse.
            ncd_val = self._ncd(prompt, cand)
            final_score = adjusted_score + (0.001 * (1.0 - ncd_val))

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural match: {jaccard:.2f}, Tension: {tension:.2f}, NCD: {ncd_val:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural consistency and NCD."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the top score to 0-1 range roughly based on our internal logic
        # Since max theoretical jaccard is 1.0 and penalty max 1.0, score is bounded.
        score = res[0]['score']
        return float(max(0.0, min(1.0, score)))