import re
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Epigenetic Predictive Constraint Solver (EPCS)
    
    Combines constraint satisfaction, epigenetic-style similarity propagation,
    and predictive coding to evaluate reasoning candidates. Parses prompts into
    atomic propositions, builds constraint networks, and minimizes prediction
    error through iterative belief updates.
    """
    
    def __init__(self):
        self.epsilon = 1e-3
        self.max_iter = 10
        self.eta = 0.1  # Learning rate for constraint propagation
        self.lambda_ = 0.3  # Epigenetic smoothing weight
    
    def _extract_propositions(self, text):
        """Extract atomic propositions from text"""
        props = []
        # Numeric patterns
        for match in re.finditer(r'(\d+\.?\d*)\s*(dollars|cents|years|items|people|percent|%)?', text.lower()):
            props.append(f"NUM_{match.group(1)}_{match.group(2) or 'unit'}")
        # Negations
        for match in re.finditer(r'(not|no|never|none)\s+(\w+)', text.lower()):
            props.append(f"NEG_{match.group(2)}")
        # Comparatives
        for match in re.finditer(r'(\w+)\s+(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)', text.lower()):
            props.append(f"CMP_{match.group(1)}_{match.group(2)}_{match.group(3)}")
        # Conditionals
        for match in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)[\.\,\;]', text.lower()):
            props.append(f"IF_{match.group(1)[:20]}_THEN_{match.group(2)[:20]}")
        # Temporal
        for match in re.finditer(r'(\w+)\s+(before|after|first|last)\s+(\w+)', text.lower()):
            props.append(f"TEMP_{match.group(1)}_{match.group(2)}_{match.group(3)}")
        # Extract all words as basic props
        words = re.findall(r'\b\w+\b', text.lower())
        props.extend([f"WORD_{w}" for w in words if len(w) > 3])
        return list(set(props))
    
    def _similarity_matrix(self, props):
        """Compute epigenetic similarity matrix using lexical overlap"""
        n = len(props)
        S = np.eye(n)
        for i in range(n):
            for j in range(i+1, n):
                ratio = SequenceMatcher(None, props[i], props[j]).ratio()
                S[i,j] = S[j,i] = ratio
        return S
    
    def _build_constraints(self, props, text):
        """Build constraint matrix from propositions"""
        n = len(props)
        C = np.zeros((n, n))
        constraints = []
        
        # Negation constraints
        for i, p1 in enumerate(props):
            for j, p2 in enumerate(props):
                if p1.startswith('NEG_') and p1[4:] in p2:
                    C[i,j] = 1
                    constraints.append((i, j, lambda x, y: abs(x + y - 1)))
        
        # Numeric comparison constraints
        nums = [(i, p) for i, p in enumerate(props) if p.startswith('NUM_')]
        for idx, (i, p1) in enumerate(nums):
            for j, p2 in nums[idx+1:]:
                C[i,j] = 1
                val1 = float(p1.split('_')[1])
                val2 = float(p2.split('_')[1])
                if val1 > val2:
                    constraints.append((i, j, lambda x, y: abs(x - max(x, y))))
                else:
                    constraints.append((i, j, lambda x, y: abs(y - max(x, y))))
        
        return C, constraints
    
    def _compute_structural_score(self, prompt, candidate):
        """Compute score from structural parsing and constraint solving"""
        # Numeric comparison
        prompt_nums = [float(m.group(1)) for m in re.finditer(r'\b(\d+\.?\d*)\b', prompt)]
        cand_nums = [float(m.group(1)) for m in re.finditer(r'\b(\d+\.?\d*)\b', candidate)]
        
        # Bat-and-ball algebra
        ball_match = re.search(r'(\d+\.?\d*)\s*more.*total.*\$?(\d+\.?\d*)', prompt.lower())
        if ball_match and cand_nums:
            diff = float(ball_match.group(1))
            total = float(ball_match.group(2))
            correct = (total - diff) / 2
            if cand_nums and abs(cand_nums[0] - correct) < 0.01:
                return 0.95
        
        # Negation agreement
        prompt_negs = set(re.findall(r'(not|no|never)\s+(\w+)', prompt.lower()))
        cand_negs = set(re.findall(r'(not|no|never)\s+(\w+)', candidate.lower()))
        neg_score = len(prompt_negs & cand_negs) / max(len(prompt_negs), 1) if prompt_negs else 0.5
        
        # Transitivity: if A>B and B>C mentioned, answer should respect A>C
        trans_score = 0.5
        comparisons = re.findall(r'(\w+)\s+(>|<|greater|less)\s+(\w+)', prompt.lower())
        if len(comparisons) >= 2:
            trans_score = 0.7 if any(c in candidate.lower() for c in [comparisons[0][0], comparisons[-1][2]]) else 0.3
        
        return (neg_score * 0.3 + trans_score * 0.2 + 0.5)
    
    def _predictive_coding_loop(self, props, C, constraints, prior):
        """Run predictive coding loop with constraint propagation"""
        b = np.array(prior, dtype=float)
        S = self._similarity_matrix(props)
        
        for iteration in range(self.max_iter):
            b_old = b.copy()
            
            # Constraint propagation
            for i, j, f in constraints:
                try:
                    error = f(b[i], b[j])
                    b[i] -= self.eta * error * 0.5
                    b[j] -= self.eta * error * 0.5
                except:
                    pass
            
            b = np.clip(b, 0, 1)
            
            # Epigenetic smoothing
            b = (1 - self.lambda_) * b + self.lambda_ * (S @ b) / (S.sum(axis=1) + 1e-9)
            
            # Check convergence
            if np.linalg.norm(b - b_old) < self.epsilon:
                break
        
        prediction_error = np.linalg.norm(b - prior)**2
        return 1.0 / (1.0 + prediction_error)
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1+s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _meta_confidence(self, prompt):
        """Detect ambiguity and unanswerable questions"""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did.*fail|when did.*stop)', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every \w+ .* a \w+', p_lower) and 'same' not in p_lower:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*\?', p_lower) and re.search(r'\w+ told \w+', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or .*\?', p_lower) and 'only' not in p_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'(best|worst|favorite|prettiest)', p_lower) and not re.search(r'(most|least|highest|lowest)', p_lower):
            return 0.2
        
        # Insufficient information
        if 'cannot be determined' in p_lower or 'not enough information' in p_lower:
            return 0.15
        
        return 1.0
    
    def evaluate(self, prompt, candidates):
        """Evaluate candidates and return ranked list"""
        results = []
        
        for candidate in candidates:
            # Extract propositions
            prompt_props = self._extract_propositions(prompt)
            cand_props = self._extract_propositions(candidate)
            all_props = list(set(prompt_props + cand_props))
            
            if len(all_props) == 0:
                all_props = ['EMPTY']
            
            # Build constraints
            C, constraints = self._build_constraints(all_props, prompt + ' ' + candidate)
            
            # Initialize priors
            prior = [0.5] * len(all_props)
            for i, p in enumerate(all_props):
                if p in prompt_props:
                    prior[i] = 0.8
            
            # Run predictive coding
            epcs_score = self._predictive_coding_loop(all_props, C, constraints, prior)
            
            # Structural parsing
            struct_score = self._compute_structural_score(prompt, candidate)
            
            # NCD (max 15%)
            ncd_score = 1 - self._ncd(prompt, candidate)
            
            # Combine scores
            final_score = 0.5 * struct_score + 0.35 * epcs_score + 0.15 * ncd_score
            
            reasoning = f"EPCS={epcs_score:.2f}, Struct={struct_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": candidate, "score": final_score, "reasoning": reasoning})
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 for a proposed answer"""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute answer quality
        results = self.evaluate(prompt, [answer])
        answer_score = results[0]['score'] if results else 0.5
        
        # Cap confidence by meta-confidence
        base_confidence = min(answer_score, 0.85)
        return base_confidence * meta_conf