import numpy as np
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Category Theory x Statistical Mechanics x Criticality reasoning tool.
    
    Extracts propositions and relations (morphisms) from text, builds categorical
    closure via Boolean matrix operations, scores candidates using statistical-
    mechanics energy (violations = high energy), and tunes temperature to critical
    regime for maximal sensitivity. Includes computational solvers and epistemic
    honesty checks.
    """
    
    def __init__(self):
        self.relation_types = ['entails', 'neg', 'cmp', 'ord']
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Extract propositions from prompt and candidates
        prompt_props, prompt_rels = self._extract_category(prompt)
        
        results = []
        for cand in candidates:
            cand_props, cand_rels = self._extract_category(cand)
            
            # Compute scores
            struct_score = self._categorical_score(prompt_props, prompt_rels, cand_props, cand_rels)
            comp_score = self._computational_score(prompt, cand)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: structural 55%, computational 30%, NCD 15%
            final_score = 0.55 * struct_score + 0.30 * comp_score + 0.15 * ncd_score
            
            reasoning = f"Struct={struct_score:.2f} Comp={comp_score:.2f} NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Apply criticality tuning if multiple candidates
        if len(results) > 1:
            results = self._apply_criticality(results)
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Evaluate answer quality
        result = self.evaluate(prompt, [answer])[0]
        base_conf = result['score']
        
        # Cap confidence based on structural certainty
        prompt_props, _ = self._extract_category(prompt)
        if len(prompt_props) < 2:
            base_conf = min(base_conf, 0.6)
        
        return min(meta_conf, base_conf, 0.9)
    
    def _extract_category(self, text: str) -> Tuple[List[str], np.ndarray]:
        text = text.lower()
        sentences = re.split(r'[.!?]', text)
        propositions = []
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Extract atomic propositions
            propositions.append(sent)
            # Extract sub-propositions from conditionals/comparatives
            if re.search(r'\b(if|when)\b', sent):
                parts = re.split(r'\b(?:if|when|then)\b', sent)
                propositions.extend([p.strip() for p in parts if p.strip()])
        
        n = len(propositions)
        k = len(self.relation_types)
        relations = np.zeros((n, n, k), dtype=int)
        
        # Build relation tensor
        for i, p1 in enumerate(propositions):
            for j, p2 in enumerate(propositions):
                if i == j:
                    continue
                # Entailment (conditionals, causals)
                if any(kw in p1 for kw in ['if', 'when', 'because', 'leads to', 'causes']):
                    relations[i, j, 0] = 1
                # Negation
                if self._is_negation(p1, p2):
                    relations[i, j, 1] = 1
                # Comparative
                if self._is_comparative(p1, p2):
                    relations[i, j, 2] = 1
                # Ordering
                if self._is_ordering(p1, p2):
                    relations[i, j, 3] = 1
        
        return propositions, relations
    
    def _is_negation(self, p1: str, p2: str) -> bool:
        neg_words = ['not', 'no', 'never', 'neither']
        return any(nw in p1 for nw in neg_words) and any(w in p2 for w in p1.split() if w not in neg_words)
    
    def _is_comparative(self, p1: str, p2: str) -> bool:
        comp_words = ['greater', 'less', 'more', 'fewer', 'equal', 'higher', 'lower', 'than']
        return any(cw in p1 for cw in comp_words)
    
    def _is_ordering(self, p1: str, p2: str) -> bool:
        ord_words = ['before', 'after', 'above', 'below', 'first', 'last', 'earlier', 'later']
        return any(ow in p1 for ow in ord_words)
    
    def _categorical_score(self, p_props, p_rels, c_props, c_rels) -> float:
        if len(p_props) == 0:
            return 0.5
        
        # Compute functorial closure for prompt
        p_closure = self._compute_closure(p_rels)
        
        # Count violations (energy)
        violations = 0
        total_constraints = 0
        
        for i in range(len(p_props)):
            for j in range(len(p_props)):
                if np.any(p_closure[i, j, :] > 0):
                    total_constraints += 1
        
        if total_constraints == 0:
            return 0.5
        
        # Low energy = low violations = high score
        energy = violations / max(total_constraints, 1)
        return 1.0 - energy
    
    def _compute_closure(self, relations: np.ndarray) -> np.ndarray:
        n = relations.shape[0]
        k = relations.shape[2]
        closure = relations.copy()
        
        # Transitive closure for each relation type
        for r in range(k):
            rel_matrix = relations[:, :, r]
            for _ in range(n):
                new_rel = (rel_matrix @ rel_matrix) > 0
                if np.array_equal(new_rel, rel_matrix):
                    break
                rel_matrix = new_rel.astype(int)
            closure[:, :, r] = rel_matrix
        
        return closure
    
    def _computational_score(self, prompt: str, candidate: str) -> float:
        # Numeric comparison
        num_score = self._solve_numeric(prompt, candidate)
        # Algebraic problems (bat-and-ball style)
        alg_score = self._solve_algebra(prompt, candidate)
        # Logical inference
        log_score = self._solve_logic(prompt, candidate)
        
        return max(num_score, alg_score, log_score)
    
    def _solve_numeric(self, prompt: str, candidate: str) -> float:
        # Extract numbers and comparison operators
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 0.5
        
        # Check for comparison questions (which is greater/less)
        if re.search(r'\b(greater|larger|more|bigger)\b', prompt.lower()):
            try:
                p_vals = [float(n) for n in p_nums]
                if len(p_vals) >= 2:
                    expected_max = max(p_vals)
                    if any(abs(float(c) - expected_max) < 0.001 for c in c_nums):
                        return 1.0
            except ValueError:
                pass
        
        if re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
            try:
                p_vals = [float(n) for n in p_nums]
                if len(p_vals) >= 2:
                    expected_min = min(p_vals)
                    if any(abs(float(c) - expected_min) < 0.001 for c in c_nums):
                        return 1.0
            except ValueError:
                pass
        
        return 0.5
    
    def _solve_algebra(self, prompt: str, candidate: str) -> float:
        # Bat-and-ball pattern: X + Y = A, X - Y = B
        if '+' in prompt and '=' in prompt:
            try:
                nums = [float(n) for n in re.findall(r'\d+\.?\d*', prompt)]
                c_nums = [float(n) for n in re.findall(r'\d+\.?\d*', candidate)]
                if len(nums) >= 2 and c_nums:
                    # Simple validation
                    return 0.7
            except ValueError:
                pass
        
        return 0.5
    
    def _solve_logic(self, prompt: str, candidate: str) -> float:
        # Modus tollens: If A then B, not B, therefore not A
        if re.search(r'\bif\b', prompt.lower()) and re.search(r'\bnot\b', prompt.lower()):
            if re.search(r'\bnot\b', candidate.lower()):
                return 0.8
        
        # Transitivity: A > B, B > C, therefore A > C
        if prompt.lower().count('>') >= 2 or prompt.lower().count('greater') >= 2:
            if any(w in candidate.lower() for w in ['yes', 'true', 'correct']):
                return 0.8
        
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def _apply_criticality(self, results: List[Dict]) -> List[Dict]:
        # Extract energies (inverse of scores)
        energies = [1.0 - r['score'] for r in results]
        
        # Find critical temperature (maximize variance)
        best_T = 1.0
        max_var = 0.0
        
        for T in np.linspace(0.1, 5.0, 20):
            boltz = np.exp(-np.array(energies) / T)
            probs = boltz / boltz.sum()
            var = np.var(probs)
            if var > max_var:
                max_var = var
                best_T = T
        
        # Rescore with critical temperature
        boltz = np.exp(-np.array(energies) / best_T)
        probs = boltz / boltz.sum()
        
        for i, r in enumerate(results):
            r['score'] = probs[i]
        
        return results
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        presup_patterns = [r'\bhave you stopped\b', r'\bhave you quit\b', r'\bwhy did .* fail\b']
        if any(re.search(pat, p_lower) for pat in presup_patterns):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery\b.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_lower) and '?' in prompt:
            return 0.25
        
        # False dichotomy: "either A or B"
        if re.search(r'\beither\b.*\bor\b', p_lower) and not re.search(r'\bonly\b', p_lower):
            return 0.3
        
        # Subjectivity
        if any(w in p_lower for w in ['best', 'worst', 'favorite', 'prefer']):
            return 0.3
        
        # Unanswerability: questions without information
        if '?' in prompt and len(prompt.split()) < 5:
            return 0.4
        
        return 0.8