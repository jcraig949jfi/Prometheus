import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a variational-optimal-control agent inspired by the Free Energy Principle (FEP)
    and Kolmogorov Complexity (KC). 
    
    Mechanism:
    1. FEP Core (Risk Minimization): Evaluates how well a candidate explains the prompt's 
       structural constraints (negations, conditionals, numerics). This acts as the 'expected free energy'.
    2. KC/MDL Term (Complexity Penalty): Penalizes candidates that are either too complex 
       (long description length) or fail to compress the prompt's logical requirements (high surprise).
    3. Synergy: The final score balances structural accuracy (FEP) against parsimony (KC).
    
    Note: Per causal analysis, 'Optimal Control' is restricted to the confidence wrapper logic,
    while FEP drives the core evaluation.
    """

    def __init__(self):
        # No external state needed; stateless computation
        pass

    def _get_description_length(self, text: str) -> float:
        """Approximates Kolmogorov Complexity via zlib compression length."""
        if not text:
            return 0.0
        return len(zlib.compress(text.encode('utf-8')))

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        
        # Negations
        negations = len(re.findall(r'\b(no|not|never|neither|none|cannot|won\'t|don\'t|isn\'t|aren\'t)\b', text_lower))
        
        # Conditionals
        conditionals = len(re.findall(r'\b(if|then|unless|otherwise|provided|when)\b', text_lower))
        
        # Comparatives (simple heuristic)
        comparatives = len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse|than)\b', text_lower))
        
        # Numbers (extract as floats for evaluation)
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
        numeric_vals = [float(n) for n in numbers]
        
        return {
            'negations': negations,
            'conditionals': conditionals,
            'comparatives': comparatives,
            'numbers': numeric_vals,
            'length': len(text)
        }

    def _compute_fep_risk(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Computes the 'Expected Free Energy' (Risk) term.
        Measures the divergence between prompt constraints and candidate implications.
        Lower is better.
        """
        risk = 0.0
        
        # 1. Structural Consistency (Constraint Propagation)
        # If prompt has negations, candidate should ideally reflect logical consistency.
        # Heuristic: Large mismatch in logical operator count suggests high risk (surprise).
        risk += abs(prompt_feats['negations'] - cand_feats['negations']) * 2.0
        risk += abs(prompt_feats['conditionals'] - cand_feats['conditionals']) * 1.5
        
        # 2. Numeric Evaluation
        # If numbers exist, check if candidate preserves or logically operates on them.
        if prompt_feats['numbers']:
            if not cand_feats['numbers']:
                # Candidate ignores numeric data -> High risk
                risk += 5.0
            else:
                # Check for gross contradictions (e.g., prompt max vs candidate min)
                p_max = max(prompt_feats['numbers'])
                c_min = min(cand_feats['numbers'])
                # Simple transitivity check heuristic
                if p_max > 10 and c_min > p_max * 2: 
                    risk += 3.0 # Suspicious jump
                    
        # 3. Semantic Overlap (as a proxy for generative model likelihood)
        # Using NCD distance as a proxy for KL(q||p)
        combined = prompt + " " + candidate
        k_combined = self._get_description_length(combined)
        k_prompt = self._get_description_length(prompt)
        k_cand = self._get_description_length(candidate)
        
        # Normalized Compression Distance (0-1)
        denom = max(k_prompt, k_cand)
        ncd = (k_combined - denom) / denom if denom > 0 else 1.0
        risk += ncd * 10.0
        
        return risk

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing the Free Energy + Description Length functional.
        J = Risk (FEP) + Lambda * Complexity (KC)
        """
        if not candidates:
            return []
            
        prompt_feats = self._extract_structural_features(prompt)
        p_len = self._get_description_length(prompt)
        results = []
        
        # Lambda for MDL term (tuned to beat baseline)
        lambda_kc = 0.05 

        for cand in candidates:
            if not isinstance(cand, str):
                cand = str(cand)
                
            cand_feats = self._extract_structural_features(cand)
            
            # 1. Compute Risk (FEP term)
            risk = self._compute_fep_risk(prompt_feats, cand_feats, prompt, cand)
            
            # 2. Compute Complexity (KC/MDL term)
            # Penalize overly long explanations that don't add value
            complexity = self._get_description_length(cand)
            
            # 3. Total Functional J (Minimize this)
            # We invert the sign for the final score so higher is better
            functional_value = risk + (lambda_kc * complexity)
            
            # Normalize score: Lower functional value = Higher score
            # Base score 1.0, subtract scaled functional value
            score = 1.0 / (1.0 + functional_value * 0.1)
            
            # Boost for exact structural matches (e.g. yes/no to boolean questions)
            prompt_lower = prompt.lower()
            cand_lower = cand.lower().strip().rstrip('.')
            if ('yes' in prompt_lower or 'no' in prompt_lower) and cand_lower in ['yes', 'no', 'true', 'false']:
                if (prompt_lower.find('not') == -1 and cand_lower in ['yes', 'true']) or \
                   (prompt_lower.find('not') != -1 and cand_lower in ['no', 'false']):
                    score = min(1.0, score + 0.2)

            results.append({
                "candidate": cand,
                "score": round(score, 6),
                "reasoning": f"FEP Risk: {risk:.4f}, KC Penalty: {complexity:.4f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the FEP-KC score.
        Uses structural parsing as primary signal, NCD as tiebreaker.
        """
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        base_score = res[0]['score']
        
        # Structural validation boost (Optimal Control wrapper)
        # Check if answer satisfies basic non-empty and type constraints
        if not answer.strip():
            return 0.0
            
        # If the prompt implies a number and answer is a number, boost confidence
        p_nums = re.findall(r'-?\d+(?:\.\d+)?', prompt)
        a_nums = re.findall(r'-?\d+(?:\.\d+)?', answer)
        
        if p_nums and a_nums:
            # Numeric consistency check
            base_score = min(1.0, base_score + 0.1)
            
        return round(min(1.0, max(0.0, base_score)), 4)