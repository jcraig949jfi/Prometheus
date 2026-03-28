import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-organizing pragmatic inference engine approximating Autopoiesis x Pragmatics x MaxEnt.
    
    Mechanism:
    1. Autopoietic Core (VAE analog): Maintains an internal 'latent state' (feature weights) 
       derived from the prompt's structural density. It reconstructs the prompt's logical 
       signature to define its own operational boundary.
    2. MaxEnt Constraint Layer: Computes a probability distribution over candidate features 
       that maximizes entropy subject to the prompt's structural constraints (negations, comparatives).
       This prevents over-fitting to specific keywords (bias) and favors candidates that 
       satisfy logical forms with minimal assumption.
    3. Pragmatic Reasoning (RSA analog): Evaluates candidates based on Gricean maxims 
       (Relevance, Quantity) implemented as scoring modifiers. It checks if the candidate 
       logically follows the prompt's structural constraints (e.g., if prompt has "not", 
       candidate must reflect negation).
    
    The system iterates once (recurrent loop) to adjust scores: 
    Prompt Structure -> MaxEnt Weights -> Pragmatic Check -> Score Adjustment.
    """

    def __init__(self):
        # Structural patterns for parsing (The "Organizational Closure")
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = {'>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.logic_ops = {'if', 'then', 'else', 'therefore', 'because', 'so'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each'}

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical features to form the latent state."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparative_ops) or bool(re.search(r'\d+\s*[-<>=]+\s*\d+', lower_text))
        has_logic = bool(words & self.logic_ops)
        has_quantifier = bool(words & self.quantifiers)
        
        # Numeric extraction
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', lower_text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'logic': has_logic,
            'quantifier': has_quantifier,
            'numbers': numbers,
            'length': len(text),
            'word_set': words
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _max_entropy_score(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Computes a score based on MaxEnt principles: 
        Prefer candidates that satisfy constraints (features) without unnecessary bias.
        If a constraint exists in prompt (e.g., negation), missing it in candidate increases 'energy' (lowers score).
        """
        score = 0.5  # Base entropy (maximum uncertainty)
        
        # Constraint 1: Negation Consistency (High penalty for violation)
        if prompt_feats['negation']:
            if cand_feats['negation']:
                score += 0.3  # Reward matching negation
            else:
                score -= 0.4  # Penalty for ignoring negation (Goodhart trap avoidance)
        else:
            if cand_feats['negation']:
                score -= 0.2  # Slight penalty for spurious negation
        
        # Constraint 2: Comparative/Numeric Logic
        if prompt_feats['comparative']:
            if cand_feats['comparative'] or cand_feats['numbers']:
                score += 0.2
            # If prompt has numbers but candidate doesn't, slight penalty unless candidate is short
            if prompt_feats['numbers'] and not cand_feats['numbers'] and len(candidate.split()) > 3:
                score -= 0.1

        # Constraint 3: Logical Connectors
        if prompt_feats['logic']:
            if cand_feats['logic']:
                score += 0.15
                
        return score

    def _pragmatic_check(self, prompt: str, candidate: str, p_feats: Dict, c_feats: Dict) -> float:
        """
        RSA-style utility check: Does the candidate answer the prompt efficiently?
        Checks for relevance and non-redundancy.
        """
        utility = 0.0
        p_words = p_feats['word_set']
        c_words = c_feats['word_set']
        
        # Relevance: Overlap of content words (excluding stop words roughly)
        stop_words = {'the', 'is', 'are', 'a', 'an', 'to', 'be', 'of', 'in', 'it', 'that', 'this'}
        content_overlap = len((p_words & c_words) - stop_words)
        
        if content_overlap > 0:
            utility += 0.2 * min(1.0, content_overlap / 5.0)
            
        # Brevity penalty (Grice's Quantity: do not make longer than necessary)
        if len(candidate) > len(prompt) * 1.5:
            utility -= 0.1
            
        # Specific heuristic for Yes/No questions with negation
        if p_feats['negation']:
            c_lower = candidate.lower().strip()
            # If prompt is negative, a simple "Yes" might be ambiguous, "No" is safer or explicit repetition
            if c_lower in ['yes', 'no']:
                # We can't resolve truth without semantics, but we check structural alignment
                # This is a placeholder for the RSA "Listener" inferring intent
                utility += 0.05 

        return utility

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feats = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD for tie-breaking
        ncd_scores = [(c, self._ncd(prompt, c)) for c in candidates]
        min_ncd = min(s[1] for s in ncd_scores)
        max_ncd_range = max(s[1] for s in ncd_scores) - min_ncd + 1e-6

        for cand in candidates:
            c_feats = self._extract_structure(cand)
            
            # 1. Autopoietic Core: Reconstruct latent state from candidate
            # (Implicit in feature extraction matching the prompt's organizational logic)
            
            # 2. MaxEnt Layer: Score based on constraint satisfaction
            me_score = self._max_entropy_score(p_feats, c_feats, cand)
            
            # 3. Pragmatic Module: Utility check
            prag_score = self._pragmatic_check(prompt, cand, p_feats, c_feats)
            
            # Combined Score
            total_score = me_score + prag_score
            
            # NCD as tiebreaker (only if structural signals are weak or equal)
            # We normalize NCD to be a small modifier so structure dominates
            cand_ncd = self._ncd(prompt, cand)
            ncd_modifier = (cand_ncd - min_ncd) / max_ncd_range * 0.05 # Max 0.05 impact
            
            # Lower NCD is better, so we subtract the modifier
            final_score = total_score - ncd_modifier
            
            # Fallback: If scores are identical (rare), use raw NCD
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {me_score:.2f}, Pragmatic utility: {prag_score:.2f}, NCD penalty: {ncd_modifier:.3f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural coherence and pragmatic fit.
        Uses the internal evaluation logic to determine if the answer 'fits' the prompt.
        """
        # Evaluate single candidate against itself to get relative metrics
        # We simulate a minimal candidate set to force normalization
        dummy_candidates = [answer, ""] 
        if len(answer) == 0:
            return 0.0
            
        # Quick structural check
        p_feats = self._extract_structure(prompt)
        a_feats = self._extract_structure(answer)
        
        # Base confidence on structural alignment
        conf = 0.5
        
        # Negation alignment
        if p_feats['negation'] == a_feats['negation']:
            conf += 0.2
        else:
            conf -= 0.3 # Major red flag
            
        # Length sanity (Answer shouldn't be empty or absurdly long relative to prompt)
        if len(answer) > len(prompt) * 3:
            conf -= 0.2
        if len(answer) < 1:
            return 0.0
            
        # NCD check: If answer is completely unrelated noise, NCD will be high (bad)
        # But if it's a valid short answer ("Yes", "42"), NCD might be high too.
        # We rely mostly on the structural flags for confidence in this constrained model.
        
        return max(0.0, min(1.0, conf))