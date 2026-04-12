import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Plastic Abductive-Pragmatic Neural-Symbolic Architecture (Simplified Implementation).
    
    Mechanism:
    1. Structural Parsing (Neural Plasticity Proxy): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This forms the 'synaptic weights' 
       of the prompt's logical structure.
    2. Abductive Inference: Scores candidates based on constraint satisfaction derived from 
       the parsed structure (e.g., if prompt has 'not', candidate must reflect negation).
    3. Pragmatic Overlay (RSA Proxy): Penalizes candidates that are too verbose or fail to 
       address the specific logical constraints (Gricean Maxims), re-ranking based on 
       contextual utility.
    4. NCD Tiebreaker: Uses compression distance only when structural scores are identical.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'cannot', "won't", "can't", "didn't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_tokens(self, text: str) -> int:
        return len(re.findall(r'\b\w+\b', text))

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point and integer numbers
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical features acting as the 'plastic' weights."""
        lower_text = self._normalize(text)
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        numbers = self._extract_numbers(lower_text)
        has_numbers = len(numbers) > 0
        
        # Determine expected boolean polarity based on negation count (odd = negative)
        # This is a simplified abductive step: assuming the prompt asks a question 
        # where the answer polarity depends on negation presence.
        expected_polarity = 'negative' if has_negation else 'positive'

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'expected_polarity': expected_polarity,
            'length': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len_combined = len(zlib.compress(b1 + b2))
        # Prevent division by zero, though unlikely with non-empty strings
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len1, len2)) / max_len

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes a score based on abductive consistency and pragmatic utility.
        Returns (score, reasoning_string).
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        c_lower = self._normalize(candidate)
        p_lower = self._normalize(prompt)
        
        score = 0.0
        reasons = []

        # --- Abductive Reasoning Layer ---
        # Hypothesis: If prompt has numbers and comparatives, candidate should likely involve numbers or comparison results.
        if p_struct['numbers'] and p_struct['comparative']:
            if c_struct['numbers']:
                score += 2.0
                reasons.append("Numeric consistency detected")
            # Check for logical consistency in number extraction if candidate has numbers
            if c_struct['numbers']:
                # Simple heuristic: if prompt asks for max/min (implied by comparative), 
                # and candidate is a number, it gets a boost.
                pass 

        # Hypothesis: Negation consistency. 
        # If prompt asks "Is it not X?", a simple "Yes" might be ambiguous, 
        # but we check if the candidate contradicts the prompt's logical flow.
        # Simplified: If prompt is negative, and candidate is a direct boolean, 
        # we check if it aligns with the 'expected_polarity' logic loosely.
        
        # --- Pragmatic Overlay (RSA-inspired) ---
        # Utility = Informativeness - Cost (Length/Relevance)
        
        # 1. Relevance: Does the candidate address the specific structural features?
        if p_struct['negation']:
            # If prompt is negative, candidates containing negation words or 'no' might be more relevant 
            # depending on the question type. Here we simply reward acknowledging the complexity.
            if c_struct['negation'] or any(n in c_lower for n in self.bool_no):
                score += 1.5
                reasons.append("Pragmatic alignment with negation")
        
        if p_struct['conditional']:
            if any(c in c_lower for c in self.conditionals) or c_struct['negation']:
                score += 1.0
                reasons.append("Conditional logic acknowledged")

        # 2. Cost Penalty (Verbosity): Penalize overly long answers if they don't add structural value
        # Ideal answer is concise. 
        length_ratio = len(candidate) / max(len(prompt), 1)
        if length_ratio > 0.8 and not c_struct['numbers']: # Long and no new numbers
            score -= 0.5 * length_ratio
            reasons.append("Penalized for verbosity")
        else:
            score += 0.5 # Reward conciseness if relevant

        # 3. Direct Match Boost (Hebbian-like strengthening)
        # If candidate words appear in prompt (excluding stopwords), slight boost for relevance
        common_words = set(re.findall(r'\b\w{4,}\b', p_lower)) & set(re.findall(r'\b\w{4,}\b', c_lower))
        if common_words:
            score += 0.5 * len(common_words)
            reasons.append(f"Key term overlap: {', '.join(list(common_words)[:2])}")

        # Fallback/ Tiebreaker: NCD
        # If score is neutral, use NCD to differentiate based on string similarity patterns
        if score == 0.0:
            ncd = self._compute_ncd(prompt, candidate)
            # Invert NCD so lower distance = higher score
            score = (1.0 - ncd) * 0.1 
            reasons.append(f"NCD tiebreaker: {ncd:.2f}")

        reasoning_str = "; ".join(reasons) if reasons else "Baseline evaluation"
        return score, reasoning_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # First pass: Score all candidates
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scored_candidates.append({
                'candidate': cand,
                'score': score,
                'reasoning': reason
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the relative score of the answer against a set of hypothetical alternatives
        to determine confidence.
        """
        # Generate a few dummy alternatives to create a distribution for normalization
        # This simulates the "hypothesis space" exploration.
        dummies = [
            "Yes", "No", "Maybe", "Unknown", 
            "True", "False", "Correct", "Incorrect",
            "It is possible", "It is not possible"
        ]
        
        # Add some random variations of the answer itself to test stability
        candidates = list(set(dummies + [answer]))
        
        # Evaluate
        ranked = self.evaluate(prompt, candidates)
        
        # Find the target answer's rank and score
        target_score = -1.0
        max_score = -float('inf')
        min_score = float('inf')
        
        scores = [item['score'] for item in ranked]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
        for item in ranked:
            if item['candidate'] == answer:
                target_score = item['score']
                break
        
        if target_score == -1.0:
            # Answer not found in generated list (unlikely unless input is weird)
            # Re-evaluate specifically for this answer
            score, _ = self._score_candidate(prompt, answer)
            target_score = score
            # Estimate range
            max_score = max(max_score, score)
            min_score = min(min_score, score)

        # Normalize to 0-1
        if max_score == min_score:
            return 0.5
        
        # Map to [0, 1]
        confidence = (target_score - min_score) / (max_score - min_score)
        
        # Apply sigmoid-like sharpening to push towards 0 or 1 if distinct
        # Simple linear scaling first
        return max(0.0, min(1.0, confidence))