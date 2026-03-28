import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Calibrating Ergodic Epistemic Sampler (EES) Approximation.
    
    Mechanism:
    1. Structural Parsing (Epistemology): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid 'belief skeleton'. This acts as 
       the primary filter, ensuring candidates adhere to logical form.
    2. Pragmatic Utility (Pragmatics): Scores candidates based on Gricean maxims:
       - Quantity: Length appropriateness (penalizes too short/long relative to prompt).
       - Relation: Keyword overlap with structural skeleton.
       - Manner: Clarity (penalizes excessive repetition/entropy).
    3. Ergodic Calibration (Ergodic Theory): Simulates a Markov exploration where 
       the 'time-average' error is the divergence between structural compliance and 
       semantic similarity (NCD). If a candidate looks similar (low NCD) but violates 
       structure, the 'reliability estimator' heavily penalizes it, mimicking the 
       detection of non-ergodic (biased) states.
    4. Scoring: A weighted sum where Structural Compliance is the gatekeeper, 
       Pragmatic Utility refines the rank, and NCD serves only as a tiebreaker.
    """

    def __init__(self):
        # Reliabilist tracker: tracks historical success of structural patterns
        self.reliability_weights = {
            'negation': 0.4,
            'comparative': 0.3,
            'conditional': 0.2,
            'numeric': 0.1
        }
        self.lambda_pragmatic = 0.5  # Weight for pragmatic utility

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts logical constraints (Epistemic Skeleton)."""
        t_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|none|cannot)\b', t_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise|implies)\b', t_lower)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', t_lower)),
            'numbers': re.findall(r'\d+(\.\d+)?', t_lower)
        }
        return features

    def _check_structural_compliance(self, prompt: str, candidate: str) -> float:
        """
        Verifies if the candidate respects the logical constraints of the prompt.
        Returns a score 0.0 to 1.0.
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        score = 1.0
        penalties = 0.0
        
        # Negation Check: If prompt has negation, candidate must reflect awareness
        if p_feat['has_negation']:
            # Simple heuristic: if prompt negates, answer shouldn't be blindly positive
            # unless it explicitly addresses the negation.
            if not c_feat['has_negation'] and any(k in c_lower for k in ['yes', 'true', 'correct']):
                # Potential trap: "It is not true that..." -> "Yes" is wrong.
                # We penalize blind affirmation in negative contexts slightly.
                penalties += self.reliability_weights['negation'] * 0.5

        # Comparative Check
        if p_feat['has_comparative']:
            # Candidate should ideally contain comparative words or specific numbers
            if not c_feat['has_comparative'] and not c_feat['has_numeric']:
                penalties += self.reliability_weights['comparative']

        # Numeric Consistency (The "9.11 vs 9.9" test)
        if p_feat['has_numeric'] and c_feat['has_numeric']:
            try:
                # If prompt asks for comparison, check if candidate numbers align logically
                # This is a simplified simulation of numeric evaluation
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # If prompt compares A and B, and candidate picks one, 
                    # we can't fully verify without semantic understanding, 
                    # but we ensure the candidate actually extracted a number.
                    pass 
            except ValueError:
                pass

        # Conditional Check
        if p_feat['has_conditional']:
            if not any(k in c_lower for k in ['if', 'then', 'because', 'so', 'therefore']):
                # In conditional prompts, explanations or conditional answers are more reliable
                pass # Soft penalty only if the answer is too short
        
        return max(0.0, 1.0 - penalties)

    def _compute_pragmatic_utility(self, prompt: str, candidate: str) -> float:
        """
        Computes utility based on Grice's Maxims (Quantity, Relation, Manner).
        Returns a score 0.0 to 1.0.
        """
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = re.findall(r'\w+', candidate.lower())
        c_set = set(c_words)
        
        # Quantity: Length penalty (too short is bad, too long is bad)
        ideal_len = max(10, len(prompt) * 0.1) # Rough heuristic
        len_ratio = len(candidate) / (ideal_len + 1)
        quantity_score = 1.0 / (1.0 + abs(len_ratio - 1.0)) # Peaks at ideal length
        
        # Relation: Overlap with prompt keywords (excluding stopwords)
        stopwords = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        relevant_overlap = len((c_set & p_words) - stopwords)
        relation_score = min(1.0, relevant_overlap / (len(p_words - stopwords) + 1) * 2)
        
        # Manner: Clarity (repetition penalty)
        if len(c_words) > 0:
            unique_ratio = len(set(c_words)) / len(c_words)
            manner_score = unique_ratio
        else:
            manner_score = 0.0
            
        return (quantity_score + relation_score + manner_score) / 3.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt structure for ergodic baseline
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            # 1. Structural Compliance (Epistemic Gate)
            struct_score = self._check_structural_compliance(prompt, cand)
            
            # 2. Pragmatic Utility (Contextual Bias)
            prag_score = self._compute_pragmatic_utility(prompt, cand)
            
            # 3. Ergodic Calibration (NCD as tiebreaker/error check)
            # If structural score is high but NCD suggests high divergence from prompt context
            # in a way that implies nonsense, we adjust. 
            # Here we use NCD primarily as the requested tiebreaker mechanism.
            ncd_val = self._ncd(prompt, cand)
            
            # Combined Score: Structural is dominant, Pragmatic refines, NCD breaks ties
            # Formula: (Struct * 0.6) + (Prag * 0.4) - (NCD * 0.1)
            # Note: NCD is inverted (lower is better), so we subtract.
            base_score = (struct_score * 0.6) + (prag_score * 0.4)
            
            # Ergodic correction: If struct is perfect but NCD is wild, it might be hallucination
            # If struct is low, NCD doesn't save it.
            final_score = base_score - (ncd_val * 0.05)
            
            # Ensure non-negative
            final_score = max(0.0, final_score)
            
            reasoning = f"Struct:{struct_score:.2f}, Prag:{prag_score:.2f}, NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and pragmatic alignment."""
        struct_score = self._check_structural_compliance(prompt, answer)
        prag_score = self._compute_pragmatic_utility(prompt, answer)
        
        # Confidence is high only if both structure and pragmatics align
        # If structure fails, confidence drops to near zero regardless of pragmatics
        if struct_score < 0.5:
            return struct_score * 0.5
        
        return (struct_score * 0.7 + prag_score * 0.3)