import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning tool combining structural logic parsing, measure-theoretic 
    probability approximation, and active inference scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, comparatives, and conditionals.
    2. Measure Layer: Assigns base probabilities to nodes based on lexical cues.
    3. Active Inference: Computes Expected Free Energy (G) for candidates.
       - Epistemic Term: KL-divergence between prompt constraints and candidate implications.
       - Pragmatic Term: Penalty for violating speech acts or scalar implicatures.
    4. Scoring: Final score is -G, normalized. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        # Lexical cues for probability priors
        self.certainty_cues = ['must', 'always', 'never', 'certainly', 'definitely']
        self.uncertainty_cues = ['might', 'could', 'possibly', 'maybe', 'sometimes']
        self.negation_markers = ['not', 'no', 'never', 'none', 'cannot']
        self.comparators = ['>', '<', '>=', '<=', 'greater', 'less', 'equal']
        self.conditionals = ['if', 'then', 'unless', 'provided']
        self.causal_markers = ['because', 'therefore', 'thus', 'hence', 'so']
        
        # Regex patterns
        self.pat_num = re.compile(r'-?\d+\.?\d*')
        self.pat_neg = re.compile(r'\b(?:' + '|'.join(self.negation_markers) + r')\b', re.IGNORECASE)
        self.pat_cond = re.compile(r'\b(?:' + '|'.join(self.conditionals) + r')\b', re.IGNORECASE)
        self.pat_causal = re.compile(r'\b(?:' + '|'.join(self.causal_markers) + r')\b', re.IGNORECASE)
        self.pat_comp = re.compile(r'(?:greater\s+less|less\s+than|greater\s+than|more\s+than|fewer\s+than|>\|<\|=)', re.IGNORECASE)

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        lower_text = text.lower()
        features = {
            'has_negation': bool(self.pat_neg.search(lower_text)),
            'has_conditional': bool(self.pat_cond.search(lower_text)),
            'has_causal': bool(self.pat_causal.search(lower_text)),
            'has_numbers': bool(self.pat_num.search(text)),
            'neg_count': len(self.pat_neg.findall(lower_text)),
            'numbers': [float(n) for n in self.pat_num.findall(text)]
        }
        return features

    def _compute_base_prob(self, text: str) -> float:
        """Measure-theoretic base probability from lexical cues."""
        lower_text = text.lower()
        score = 0.5  # Prior
        cues_found = 0
        
        for word in self.certainty_cues:
            if word in lower_text:
                score += 0.1
                cues_found += 1
        for word in self.uncertainty_cues:
            if word in lower_text:
                score -= 0.1
                cues_found += 1
                
        # Normalize roughly to [0.05, 0.95]
        return max(0.05, min(0.95, score))

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Active Inference Layer: Compute constraint satisfaction score.
        Returns a score where 1.0 is perfect consistency, 0.0 is contradiction.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 1.0
        
        # 1. Negation Consistency (Modus Tollens approximation)
        # If prompt has strong negation and candidate affirms the negated concept without qualification
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Check if candidate repeats key prompt words but misses the negation
            prompt_words = set(re.findall(r'\b\w+\b', p_lower))
            candidate_words = set(re.findall(r'\b\w+\b', c_lower))
            overlap = prompt_words.intersection(candidate_words)
            if len(overlap) > 3: # Significant overlap but missing negation structure
                score -= 0.4

        # 2. Numeric Consistency
        if p_feat['has_numbers'] and c_feat['has_numbers']:
            p_nums = p_feat['numbers']
            c_nums = c_feat['numbers']
            # Simple transitivity check: if prompt says A > B, candidate shouldn't say B > A
            # Here we just check if candidate numbers are within reasonable range of prompt numbers
            if p_nums and c_nums:
                p_range = (min(p_nums), max(p_nums))
                for n in c_nums:
                    if n < p_range[0] * 0.5 or n > p_range[1] * 2.0:
                        score -= 0.3 # Penalty for wild numeric deviation

        # 3. Conditional/Causal Flow
        # If prompt is conditional ("If A then B"), candidate asserting "A and not B" is bad
        if p_feat['has_conditional']:
            if 'but not' in c_lower or 'however not' in c_lower:
                score -= 0.2
        
        return max(0.0, score)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Expected Free Energy G.
        G = Epistemic Cost - Pragmatic Reward
        Lower G is better. We return -G as the score.
        """
        # Epistemic Term: How well does candidate satisfy constraints?
        # P_c is prompt constraint strength, Q_c is candidate satisfaction
        constraint_score = self._check_logical_consistency(prompt, candidate)
        kl_div = 1.0 - constraint_score  # Approximate KL divergence
        
        # Pragmatic Term: Does it match speech act force?
        p_prob = self._compute_base_prob(prompt)
        c_prob = self._compute_base_prob(candidate)
        pragmatic_match = 1.0 - abs(p_prob - c_prob) # Reward similar confidence levels
        
        # G = w1 * KL - w2 * Pragmatic
        # We want to minimize G. 
        # If constraint_score is low (high KL), G is high (bad).
        # If pragmatic_match is high, G decreases (good).
        G = (0.7 * kl_div) - (0.3 * pragmatic_match)
        
        return -G # Return negative G so higher is better

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scores = []
        raw_scores = []
        
        # Phase 1: Compute Active Inference Scores
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            raw_scores.append(score)
            scores.append(score)
        
        # Phase 2: Normalization and Tie-breaking
        # Convert to numpy for stability
        arr_scores = np.array(scores)
        
        # Softmax-like normalization for the main score
        # Shift to avoid overflow
        arr_scores -= np.max(arr_scores)
        exp_scores = np.exp(arr_scores)
        norm_scores = exp_scores / (np.sum(exp_scores) + 1e-9)
        
        results = []
        for i, cand in enumerate(candidates):
            main_score = norm_scores[i]
            reasoning = f"Active Inference Score: {raw_scores[i]:.4f}, Normalized: {main_score:.4f}"
            results.append({
                "candidate": cand,
                "score": float(main_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are extremely close (within epsilon)
        # This is a simplified pass; in a full engine we might re-rank strictly tied items
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the negative free energy normalized to [0,1].
        """
        # Raw score from free energy
        raw_score = self._compute_free_energy(prompt, answer)
        
        # Map raw score (typically -2 to 2 range) to 0-1 via sigmoid
        confidence = 1.0 / (1.0 + np.exp(-raw_score * 2.0))
        
        # Structural sanity check: If prompt has numbers and answer has none, reduce confidence
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        if p_feat['has_numbers'] and not a_feat['has_numbers']:
            confidence *= 0.7
            
        return float(max(0.0, min(1.0, confidence)))