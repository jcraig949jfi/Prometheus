import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a reasoning engine based on Neural Plasticity (similarity weights),
    Falsificationism (contradiction penalty), and Sensitivity Analysis (perturbation variance).
    
    Mechanism:
    1. Parses prompt into atomic propositions (subject, relation, object, polarity, numeric).
    2. Builds a weighted graph where edge weights reflect semantic similarity and polarity alignment.
    3. Propagates confidence via Floyd-Warshall to infer support strength.
    4. Calculates base support for each candidate answer.
    5. Perturbs the answer (negation, numeric shift, etc.) to measure sensitivity (brittleness).
    6. Penalizes direct logical contradictions (Falsification).
    7. Scores: Base - Lambda*Sensitivity - Beta*Contradiction.
    """
    
    # Regex patterns for parsing
    PATTERNS = {
        'negation': r'\b(not|no|never|cannot|won\'t|don\'t|doesn\'t|didn\'t)\b',
        'comparative': r'\b(more than|less than|greater than|smaller than|>=|<=|>|<)\b',
        'causal': r'\b(cause|lead to|result in|trigger|produce)\b',
        'conditional': r'\b(if|unless|then)\b',
        'number': r'-?\d+\.?\d*',
        'ordering': r'\b(before|after|first|last)\b'
    }

    def __init__(self):
        self.lambda_s = 0.5
        self.beta_f = 0.5
        self.epsilon = 0.01

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Parse text into (subj, rel, obj, polarity, numeric_flag)"""
        props = []
        sentences = re.split(r'[.\n]', text)
        words = self._tokenize(text)
        
        has_neg = bool(re.search(self.PATTERNS['negation'], text, re.IGNORECASE))
        has_num = bool(re.search(self.PATTERNS['number'], text))
        
        # Simple extraction: look for keyword contexts or default to whole sentence chunk
        # This is a heuristic approximation for the "atomic proposition" requirement
        for sent in sentences:
            if not sent.strip(): continue
            s_lower = sent.lower()
            subj, rel, obj = "generic", "is", "generic"
            
            # Extract specific relations if found
            if re.search(self.PATTERNS['comparative'], s_lower):
                match = re.search(r'(\w+)\s+(more than|less than|greater than|smaller than|>=|<=|>|<)\s+(\w+)', s_lower)
                if match: subj, rel, obj = match.group(1), match.group(2), match.group(3)
            elif re.search(self.PATTERNS['causal'], s_lower):
                match = re.search(r'(\w+)\s+(cause|lead to|result in|trigger|produce)\s+(\w+)', s_lower)
                if match: subj, rel, obj = match.group(1), match.group(2), match.group(3)
            elif re.search(self.PATTERNS['ordering'], s_lower):
                match = re.search(r'(\w+)\s+(before|after)\s+(\w+)', s_lower)
                if match: subj, rel, obj = match.group(1), match.group(2), match.group(3)
            else:
                # Fallback: Subject-Verb-Object approximation using first/last nouns
                nouns = [w for w in words if len(w) > 3] # Crude noun heuristic
                if len(nouns) >= 2:
                    subj, obj = nouns[0], nouns[-1]
                    rel = "relates_to"
                elif len(nouns) == 1:
                    subj, obj = nouns[0], "state"
                    rel = "is"

            props.append((subj, rel, obj, not has_neg, has_num))
            
        if not props:
            props.append(("input", "is", "valid", True, False))
            
        return props

    def _jaccard_similarity(self, set1: Set, set2: Set) -> float:
        if not set1 and not set2: return 0.0
        if not set1 or not set2: return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _get_lemmas(self, p: Tuple) -> Set[str]:
        # p = (subj, rel, obj, polarity, numeric_flag)
        return {p[0], p[1], p[2]}

    def _compute_base_confidence(self, prompt_props: List[Tuple], answer_prop: Tuple) -> float:
        if not prompt_props:
            return 0.0
            
        n = len(prompt_props) + 1
        nodes = prompt_props + [answer_prop]
        
        # Build Adjacency Matrix W
        W = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j: 
                    W[i, j] = 1.0
                    continue
                
                set_i = self._get_lemmas(nodes[i])
                set_j = self._get_lemmas(nodes[j])
                jacc = self._jaccard_similarity(set_i, set_j)
                
                # Polarity factor
                pol_i = nodes[i][3]
                pol_j = nodes[j][3]
                pol_factor = 1.0 if pol_i == pol_j else -1.0
                
                W[i, j] = jacc * pol_factor

        # Floyd-Warshall for Transitive Closure of Confidence
        # Using max for path combination, min for path aggregation (standard variation for confidence)
        # Here we adapt: C[i,j] = max(C[i,j], min(C[i,k], C[k,j])) doesn't fit negative weights well.
        # Instead, we use matrix multiplication logic adapted for max-path:
        # Let's use a simplified propagation: C = W, then iterate to propagate
        C = W.copy()
        
        # Standard Floyd Warshall for "strongest path" where strength is limited by weakest link
        # But since we have negative weights (contradictions), we treat this as support flow.
        # We want to maximize support. 
        # Implementation: C[i,j] = max(C[i,j], C[i,k] * C[k,j])? 
        # Given the constraints and numpy, let's do a simple power iteration or direct FW variant.
        # To handle negative edges correctly in this specific theoretical framework:
        # We treat it as finding the maximum support path.
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # Path strength is limited by the weakest link (min), 
                    # but we want the strongest such path (max).
                    # However, with negative weights, min/max gets tricky.
                    # Approximation: C_new = max(C_old, C_ik + C_kj) -> No, that's sum.
                    # Let's stick to the prompt's instruction: 
                    # "minimum for path aggregation and maximum for combining paths"
                    # This implies: strength(path) = min(edges), score(i,j) = max(strength(all_paths))
                    
                    path_strength = min(C[i, k], C[k, j]) if (i!=k and k!=j) else C[i,j]
                    if i == k or k == j: 
                         path_strength = C[i,k] if k==j else C[k,j] # Handle direct edges
                    
                    # Actually, standard FW for max-min path:
                    val = min(C[i,k], C[k,j])
                    if val > C[i,j]:
                        C[i,j] = val
                        
        # Base confidence: Sum of support from all prompt propositions to the answer (last node)
        ans_idx = n - 1
        base = 0.0
        for i in range(n-1):
            base += C[i, ans_idx]
            
        return base

    def _generate_perturbations(self, answer: str) -> List[str]:
        perturbations = []
        props = self._parse_propositions(answer)
        if not props:
            return [answer + " not"]

        base_p = props[0]
        subj, rel, obj, pol, has_num = base_p
        
        # 1. Flip polarity
        perturbations.append(f"{subj} {rel} {obj}" if pol else f"not {subj} {rel} {obj}")
        perturbations.append(f"not {subj} {rel} {obj}" if pol else f"{subj} {rel} {obj}")
        
        # 2. Reverse comparative (heuristic string replace)
        rev_map = {'more than': 'less than', 'less than': 'more than', 
                   'greater than': 'smaller than', 'smaller than': 'greater than',
                   '>': '<', '<': '>'}
        pert_ans = answer
        for k, v in rev_map.items():
            if k in answer:
                perturbations.append(answer.replace(k, v))
                break
        
        # 3. Numeric shift (if detected)
        nums = re.findall(r'-?\d+\.?\d*', answer)
        if nums:
            try:
                val = float(nums[0])
                perturbations.append(answer.replace(nums[0], str(val + self.epsilon)))
                perturbations.append(answer.replace(nums[0], str(val - self.epsilon)))
            except: pass
            
        # Ensure at least some perturbations exist
        if len(perturbations) == 0:
            perturbations = [answer + " extra", "not " + answer]
            
        return perturbations[:5] # Limit k

    def _check_falsification(self, prompt_props: List[Tuple], answer_prop: Tuple) -> float:
        """Check for direct logical negation"""
        max_contra = 0.0
        a_subj, a_rel, a_obj, a_pol, _ = answer_prop
        
        for p in prompt_props:
            p_subj, p_rel, p_obj, p_pol, _ = p
            # Check if same subject/object/relation but opposite polarity
            if (p_subj == a_subj or p_subj in a_subj or a_subj in p_subj) and \
               (p_obj == a_obj or p_obj in a_obj or a_obj in p_obj) and \
               (p_rel == a_rel):
                if p_pol != a_pol:
                    # Contradiction found
                    # Weight by similarity
                    sim = self._jaccard_similarity(self._get_lemmas(p), self._get_lemmas(answer_prop))
                    if sim > max_contra:
                        max_contra = sim
        return max_contra

    def confidence(self, prompt: str, answer: str) -> float:
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        # Take the primary proposition of the answer
        ans_prop = answer_props[0] if answer_props else ("answer", "is", "true", True, False)
        
        # 1. Base Confidence
        b = self._compute_base_confidence(prompt_props, ans_prop)
        
        # 2. Sensitivity Analysis
        perturbations = self._generate_perturbations(answer)
        b_scores = []
        for p_ans in perturbations:
            p_props = self._parse_propositions(p_ans)
            p_prop = p_props[0] if p_props else ans_prop
            b_scores.append(self._compute_base_confidence(prompt_props, p_prop))
        
        s = float(np.var(b_scores)) if len(b_scores) > 1 else 0.0
        
        # 3. Falsification Check
        f = self._check_falsification(prompt_props, ans_prop)
        
        # 4. Final Score
        score = b - (self.lambda_s * s) - (self.beta_f * f)
        
        # Normalize roughly to 0-1 range using sigmoid-like scaling for interpretability
        # Since b can be negative or >1, we map it. 
        # Heuristic: Assume raw scores are around -2 to 2.
        normalized = 1 / (1 + np.exp(-score)) 
        return float(normalized)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": conf,
                "reasoning": f"Base support adjusted by sensitivity ({self.lambda_s}) and falsification ({self.beta_f}) penalties."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results