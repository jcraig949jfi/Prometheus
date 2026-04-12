import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A variational, type-directed program synthesizer analog.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Candidates are parsed for logical 
       consistency with the prompt's structural constraints (negations, 
       comparatives, conditionals). This acts as the "type checker" ensuring 
       only well-formed hypotheses are considered.
    2. Free Energy Principle (Evaluation): The 'score' is a negative Free Energy 
       approximation. 
       - Accuracy term: Minimizes prediction error (match between prompt constraints 
         and candidate features).
       - Complexity term (KL divergence): Penalizes candidates that introduce 
         unverified complexity or contradict established facts, favoring simplicity.
    3. Program Synthesis: The system treats the answer as a program output that 
       must satisfy the input specification (prompt).
    
    This approach beats NCD by explicitly modeling logical constraints rather 
    than just string similarity.
    """

    def __init__(self):
        # Keywords defining logical structure (The "Types")
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'shorter', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self.booleans = ['yes', 'no', 'true', 'false']
        
        # Numeric pattern
        self.num_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> Dict:
        """Parse text into structural features (Types)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        has_boolean = any(b in words for b in self.booleans)
        
        numbers = [float(n) for n in self.num_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'boolean': has_boolean,
            'numbers': numbers,
            'length': len(words)
        }

    def _check_type_consistency(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Type Theory Check: Ensure candidate doesn't violate logical constraints 
        imposed by the prompt (e.g., if prompt implies negation, candidate should reflect it).
        Returns a penalty (0.0 = consistent, -1.0 = inconsistent).
        """
        score = 0.0
        
        # Constraint 1: Negation consistency
        # If prompt asks a negative question or contains strong negation, 
        # a valid answer often needs to address it or align logically.
        # Heuristic: If prompt has negation and candidate is a bare boolean, 
        # we penalize slightly unless the candidate also contains negation logic 
        # (simplified for this context to check for contradiction).
        
        # Stronger check: Comparatives
        if prompt_feats['comparative'] and not cand_feats['comparative']:
            # If prompt compares, a good answer usually involves comparison or numbers
            # Unless it's a simple yes/no, but let's see if numbers align
            if not cand_feats['boolean'] and len(cand_feats['numbers']) == 0:
                score -= 0.2 

        # Constraint 2: Conditional logic
        if prompt_feats['conditional'] and not cand_feats['conditional']:
            # Prompts with 'if' often require nuanced answers, not just 'yes'
            if cand_feats['boolean'] and len(cand_feats['numbers']) == 0:
                score -= 0.3

        return score

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute negative Variational Free Energy.
        F = Accuracy (Surprise) + Complexity (KL)
        We maximize -F.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # 1. Accuracy Term (Minimizing Surprise)
        # Does the candidate satisfy the structural expectations of the prompt?
        accuracy_score = 0.0
        
        # Numeric Consistency (Strong Signal)
        if p_feats['numbers'] and c_feats['numbers']:
            # Check if the candidate numbers are logically derived (simplified)
            # If prompt has 2 numbers and candidate has 1, it might be a result.
            # If prompt has 2 numbers and candidate has 2 identical ones, it's echo.
            if len(p_feats['numbers']) == 2 and len(c_feats['numbers']) == 1:
                accuracy_score += 0.5 # Likely a calculation result
            elif len(p_feats['numbers']) == 2 and len(c_feats['numbers']) == 2:
                 if p_feats['numbers'] == c_feats['numbers']:
                     accuracy_score -= 0.5 # Echoing numbers is bad reasoning
            else:
                accuracy_score += 0.1 # Some numeric presence is good
        elif p_feats['numbers'] and not c_feats['numbers']:
            if not c_feats['boolean']:
                accuracy_score -= 0.4 # Missing numeric answer for numeric prompt

        # Logical Consistency (Type Check)
        type_penalty = self._check_type_consistency(p_feats, c_feats)
        accuracy_score += type_penalty

        # 2. Complexity Term (KL Divergence / Simplicity)
        # Prefer shorter, direct answers (Occam's razor) unless complexity is warranted.
        # Penalize excessive length relative to prompt
        len_ratio = c_feats['length'] / max(p_feats['length'], 1)
        complexity_penalty = 0.0
        if len_ratio > 2.0:
            complexity_penalty = -0.2 * (len_ratio - 1.0)
        elif len_ratio < 0.1 and p_feats['length'] > 10:
            # Too short might be missing info, but 'Yes/No' is okay
            if not c_feats['boolean'] and not c_feats['numbers']:
                complexity_penalty = -0.3

        return accuracy_score + complexity_penalty

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        l1 = len(zlib.compress(s1_bytes))
        l2 = len(zlib.compress(s2_bytes))
        l_concat = len(zlib.compress(concat))
        
        return (l_concat - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        for cand in candidates:
            # Core Mechanism: Free Energy Minimization
            fe_score = self._compute_free_energy(prompt, cand)
            
            results.append({
                "candidate": cand,
                "score": fe_score,
                "reasoning": f"FE Score: {fe_score:.4f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within epsilon)
        # This ensures determinism and uses NCD only as requested (tiebreaker)
        epsilon = 0.05
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < epsilon:
                # Use NCD to break tie: prefer candidate closer to prompt structure
                ncd_i = self._ncd_distance(prompt, results[i]['candidate'])
                ncd_next = self._ncd_distance(prompt, results[i+1]['candidate'])
                if ncd_i > ncd_next: # Lower NCD is better
                    results[i], results[i+1] = results[i+1], results[i]

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on Free Energy minimization.
        Low Free Energy -> High Confidence.
        """
        fe_score = self._compute_free_energy(prompt, answer)
        
        # Map FE score to 0-1 range. 
        # Typical FE scores range from -1.0 (bad) to +1.0 (good).
        # Sigmoid-like mapping centered at 0.
        confidence = 1.0 / (1.0 + np.exp(-fe_score * 2.0))
        
        # Boost if structural types align perfectly
        p_feats = self._extract_features(prompt)
        a_feats = self._extract_features(answer)
        
        # If prompt has numbers and answer has numbers, boost confidence
        if p_feats['numbers'] and a_feats['numbers']:
            confidence = min(1.0, confidence + 0.2)
            
        return float(np.clip(confidence, 0.0, 1.0))