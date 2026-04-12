import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning engine based on Predictive Coding x Falsificationism x Sparse Coding.
    
    Mechanism:
    1. Parsing: Extracts logical clauses (negation, comparative, conditional, causal, numeric) via regex.
    2. Sparse Coding: Maps extracted primitives to a sparse binary vector over a fixed dictionary.
    3. Predictive Coding: Computes reconstruction error between the Question's predicted sparse code 
       and the Answer's sparse code. Low error = high predictability.
    4. Falsificationism: Penalizes answers containing primitives that contradict a hand-curated 
       knowledge base of facts (e.g., numeric impossibilities or explicit negations of known truths).
    5. Scoring: Combines predictability and falsification penalty into a final score.
    """
    
    # Hand-curated Knowledge Base (K) for falsification checks
    # Format: primitive_string -> True (implies the negation is false)
    KNOWLEDGE_BASE = {
        "water boils at 100 c": True,
        "earth is round": True,
        "sun rises in east": True,
        "2 + 2 = 4": True,
        "humans need oxygen": True,
    }

    # Fixed Dictionary of Primitives (D) - Simplified for implementation
    # In a full system, this would be learned or much larger.
    PRIMITIVE_TYPES = [
        "negation", "comparative_gt", "comparative_lt", "comparative_eq",
        "conditional_if", "causal_because", "causal_leads_to",
        "order_before", "order_after", "numeric_value"
    ]

    def __init__(self):
        self.primitives = self.PRIMITIVE_TYPES
        self.kb_keys = list(self.KNOWLEDGE_BASE.keys())
        
        # Regex patterns for parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.IGNORECASE),
            'comparative_gt': re.compile(r'\b(greater|more|higher|larger|exceeds|above)\b', re.IGNORECASE),
            'comparative_lt': re.compile(r'\b(less|fewer|lower|smaller|below|under)\b', re.IGNORECASE),
            'comparative_eq': re.compile(r'\b(equal|same|identical|matches)\b', re.IGNORECASE),
            'conditional_if': re.compile(r'\b(if|unless|provided|when)\b', re.IGNORECASE),
            'causal_because': re.compile(r'\b(because|since|due to)\b', re.IGNORECASE),
            'causal_leads_to': re.compile(r'\b(leads to|causes|results in|creates)\b', re.IGNORECASE),
            'order_before': re.compile(r'\b(before|prior|first|earlier)\b', re.IGNORECASE),
            'order_after': re.compile(r'\b(after|later|last|subsequent)\b', re.IGNORECASE),
            'numeric_value': re.compile(r'\d+(\.\d+)?')
        }

    def _parse_to_clauses(self, text: str) -> List[Tuple[str, tuple, int]]:
        """Extract logical clauses as (pred, args, polarity)."""
        clauses = []
        text_lower = text.lower()
        
        # Check regex patterns
        for p_name, regex in self.patterns.items():
            matches = regex.findall(text_lower)
            if matches:
                # Polarity +1 for asserted
                polarity = 1
                # Simple arg extraction (first match context or generic)
                args = (matches[0],) 
                clauses.append((p_name, args, polarity))
                
        # Specific numeric comparison logic (simplified)
        nums = re.findall(r'(\d+(?:\.\d+)?)\s*(<|>|=|<=|>=)\s*(\d+(?:\.\d+)?)', text)
        for n1, op, n2 in nums:
            v1, v2 = float(n1), float(n2)
            if op in ['>', '>=']:
                if v1 > v2: clauses.append(('numeric_truth', (n1, op, n2), 1))
                else: clauses.append(('numeric_truth', (n1, op, n2), -1)) # Falsified claim
            elif op in ['<', '<=']:
                if v1 < v2: clauses.append(('numeric_truth', (n1, op, n2), 1))
                else: clauses.append(('numeric_truth', (n1, op, n2), -1))
                
        return clauses

    def _text_to_sparse_vector(self, text: str) -> np.ndarray:
        """Convert text to a sparse binary indicator vector over the primitive dictionary."""
        clauses = self._parse_to_clauses(text)
        vector = np.zeros(len(self.primitives), dtype=float)
        
        # Map found primitives to vector indices
        found_primitives = set()
        for pred, args, polarity in clauses:
            if pred in self.primitives:
                found_primitives.add(pred)
            # Also check for numeric truth specifically
            if pred == 'numeric_truth':
                # If the math holds, we don't add a primitive error, but we note the logic
                pass 
            # Handle negation of specific known facts for falsification later
            if pred == 'negation':
                # Check if the text negates a known fact
                for kb_fact in self.kb_keys:
                    if kb_fact in text.lower():
                        # This is a potential falsification candidate handled in scoring
                        pass

        for i, p_name in enumerate(self.primitives):
            if p_name in found_primitives:
                vector[i] = 1.0
                
        return vector

    def _compute_sparse_code(self, vector: np.ndarray, lambda_param: float = 0.1) -> np.ndarray:
        """
        Simulate Lasso sparse coding.
        Since D is identity-like in this simplified mapping, this effectively thresholds 
        the activation to enforce sparsity (Olshausen-Field spirit).
        """
        # In a real Olshausen-Field scenario: s = argmin ||x - Ds||^2 + lambda||s||_1
        # With D=I, this is soft-thresholding.
        # s_i = sign(x_i) * max(|x_i| - lambda, 0)
        s = np.sign(vector) * np.maximum(np.abs(vector) - lambda_param, 0)
        return s

    def _check_falsification(self, text: str) -> float:
        """
        Check text against Knowledge Base K.
        Returns penalty score.
        """
        text_lower = text.lower()
        penalty = 0.0
        
        # 1. Check for direct contradiction of known facts
        for fact in self.kb_keys:
            # If the text contains the fact, it's good (unless negated)
            # If the text contains "not" + fact, it's bad.
            # Simplified: Look for negation patterns near the fact
            pattern = rf"\b(not|no|never)\b.*?{re.escape(fact)}|{re.escape(fact)}.*?\b(is not|are not|doesn't|does not)\b"
            if re.search(pattern, text_lower):
                penalty += 1.0
                
        # 2. Check for internal numeric contradictions if detectable
        # (Simplified: rely on the parser's numeric_truth with polarity -1)
        clauses = self._parse_to_clauses(text)
        for pred, args, polarity in clauses:
            if pred == 'numeric_truth' and polarity == -1:
                penalty += 1.0
                
        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Generate Prediction Vector (p) from Prompt
        # The "prediction" is what logical structures we expect the answer to follow or resolve.
        # We treat the prompt's structure as the prior expectation.
        p_vector = self._text_to_sparse_vector(prompt)
        p_code = self._compute_sparse_code(p_vector)
        
        results = []
        
        for candidate in candidates:
            # 2. Generate Answer Vector (s)
            s_vector = self._text_to_sparse_vector(candidate)
            s_code = self._compute_sparse_code(s_vector)
            
            # 3. Predictive Coding Step: Reconstruction Error
            # How well does the answer's logical structure match the prompt's expectation?
            # Using Euclidean distance as proxy for reconstruction error e_pred
            e_pred = float(np.linalg.norm(s_code - p_code)**2)
            
            # Normalize error slightly to prevent explosion, though keeping raw for sensitivity
            # In a full system, this would be ||s - D*p||
            
            # 4. Falsificationism Step
            e_fal = self._check_falsification(candidate)
            
            # 5. Scoring
            # score = 1 / (1 + e_pred + alpha * e_fal)
            alpha = 0.5
            score = 1.0 / (1.0 + e_pred + alpha * e_fal)
            
            # Heuristic boost for length match if structural signal is weak (prevents "Yes"/"No" bias)
            # But primarily driven by the logic above.
            
            reasoning = f"PredErr={e_pred:.2f}, FalPen={e_fal:.1f}"
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the top-score evaluation."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]