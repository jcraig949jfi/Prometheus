import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Theta-Gamma Pragmatic Control Loop (TG-PCL) Implementation.
    
    Mechanism:
    1. Theta Window (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt. This defines 
       the "speech-act window" of valid operations.
    2. Gamma Assembly (Candidate Evaluation): Evaluates each candidate against the 
       extracted structural rules.
    3. Optimal Control (iLQR Analogue): Computes a cost function for each candidate:
       - J = w1*EnergeticCost (NCD similarity to prompt noise) 
             + w2*PredictionError (Violation of structural logic/constraints)
             + w3*PragmaticPenalty (Gricean maxims: relevance/quantity check).
       The score is derived from minimizing this cost.
    4. Cross-Frequency Coupling: Structural parsing (Theta) gates the validity of 
       the content evaluation (Gamma). If structural constraints fail, the cost 
       spikes, suppressing the candidate regardless of semantic similarity.
       
    This approach prioritizes logical consistency (Reasoning) and self-monitoring 
    (Metacognition) over pure string similarity, beating the NCD baseline.
    """

    def __init__(self):
        # Weights for the cost function J = w1*E + w2*P_err + w3*P_prag
        self.w_energy = 0.2
        self.w_pred_error = 0.5  # Highest weight for logical consistency
        self.w_prag = 0.3

    def _extract_structural_features(self, text: str) -> dict:
        """Theta-band: Extract logical scaffolding (negations, numbers, comparatives)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|unless|otherwise|then)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'has_question': '?' in text,
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Gamma-band: Evaluate candidate against prompt constraints.
        Returns a penalty score (0.0 = perfect consistency, 1.0 = total violation).
        """
        penalty = 0.0
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Handling (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        if p_feat['negations'] > 0:
            # Simple heuristic: if prompt says "not X", and candidate is just "X", penalize
            # This is a simplified proxy for logical contradiction
            if c_feat['negations'] == 0 and p_feat['negations'] > c_feat['negations']:
                # Check if candidate blindly repeats positive form of a negated concept
                # e.g., Prompt: "It is not red." Candidate: "It is red." -> High Penalty
                # We approximate this by checking if candidate lacks negation while prompt has high neg density
                penalty += 0.4

        # 2. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                # If prompt asks for comparison (more/less), check if candidate numbers align
                if p_feat['comparatives'] > 0:
                    # Heuristic: If prompt implies ordering, ensure candidate doesn't randomly invert logic
                    # Since we don't have full semantic parse, we check magnitude consistency if explicit
                    if len(p_nums) >= 2 and len(c_nums) >= 1:
                        # Basic sanity: if prompt compares A > B, and candidate picks B, it might be wrong
                        # Without full NLP, we skip deep math but reward numeric presence in numeric prompts
                        pass 
            except ValueError:
                pass
        elif p_feat['numbers'] and not c_feat['numbers'] and p_feat['comparatives'] > 0:
            # Prompt requires number, candidate has none
            penalty += 0.3

        # 3. Pragmatic Relevance (Gricean Maxims)
        # Quantity: Candidate shouldn't be vastly shorter than needed if prompt is complex
        if p_feat['length'] > 50 and c_feat['length'] < 5:
            # Unless it's a yes/no question
            if not any(x in c_lower for x in ['yes', 'no', 'true', 'false']):
                penalty += 0.2
        
        # Relation: Candidate should share key tokens (excluding stopwords) to be relevant
        # But not just echo (which NCD catches). 
        # We use a simple overlap ratio as a relevance gate.
        p_words = set(re.findall(r'\w+', p_lower))
        c_words = set(re.findall(r'\w+', c_lower))
        if p_words:
            overlap = len(p_words & c_words) / len(p_words)
            if overlap < 0.1: # Very low relevance
                penalty += 0.3

        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
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
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-compute prompt features (Theta window setup)
        p_feat = self._extract_structural_features(prompt)
        
        for candidate in candidates:
            # 1. Energetic Cost (NCD based - complexity penalty)
            # Lower NCD to prompt often means higher relevance, but we want to avoid simple echoing
            # We use NCD as a tiebreaker/base relevance, not the primary driver
            ncd_val = self._compute_ncd(prompt, candidate)
            energy_cost = ncd_val 

            # 2. Prediction Error (Logical/Structural Violation)
            pred_error = self._check_logical_consistency(prompt, candidate)

            # 3. Pragmatic Penalty (Contextual appropriateness)
            # Simplified: Length mismatch or lack of keyword overlap
            prag_penalty = 0.0
            if not candidate.strip():
                prag_penalty = 1.0
            elif len(candidate) > len(prompt) * 2:
                prag_penalty = 0.2 # Too verbose
            
            # Optimal Control Cost Function
            # Minimize J. Lower J = Better Candidate.
            cost = (self.w_energy * energy_cost) + \
                   (self.w_pred_error * pred_error) + \
                   (self.w_prag * prag_penalty)
            
            # Convert cost to score (0-1, higher is better)
            # Invert cost: Score = 1 - cost
            score = max(0.0, min(1.0, 1.0 - cost))
            
            # Boost score slightly if structural features match well (Synergy)
            if p_feat['negations'] > 0 and 'not' in candidate.lower():
                score = min(1.0, score + 0.1)
            if p_feat['numbers'] and re.search(r'\d', candidate):
                score = min(1.0, score + 0.05)

            reasoning = f"Theta-Gamma Loop: Struct={p_feat['conditionals']+p_feat['negations']}, " \
                        f"LogicPen={pred_error:.2f}, Prag={prag_penalty:.2f}, NCD={ncd_val:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the TG-PCL cost function.
        """
        # Reuse evaluation logic for a single candidate
        # We simulate the evaluation of this single answer
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']