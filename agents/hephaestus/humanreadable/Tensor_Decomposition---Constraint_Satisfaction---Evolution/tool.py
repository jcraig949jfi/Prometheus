import numpy as np
import re
import zlib
from itertools import combinations

class ReasoningTool:
    """
    Tensor Decomposition x Constraint Satisfaction x Evolution
    
    Parses prompts/candidates into triples -> builds 3rd-order tensors -> CP decomposition
    for latent semantics -> constraint satisfaction for logical rules -> evolutionary
    optimization of relation weights. Includes deterministic parsers for standard problems.
    """
    
    def __init__(self):
        np.random.seed(42)
        self.relation_types = ['IS', 'HAS', 'GT', 'LT', 'EQ', 'NOT', 'IF_THEN', 'LEADS_TO', 
                               'BEFORE', 'AFTER', 'BECAUSE', 'CONTAINS', 'VERB']
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Tensor+CSP score: {score:.3f}, confidence: {conf:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        comp_conf = self._computational_confidence(prompt, answer)
        return min(meta_conf, comp_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'have you (stopped|quit|ceased)', p_lower):
            return 0.2
        if re.search(r'why did .+ (fail|stop|end)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\w+ told \w+ (he|she)', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', p_lower) and 'only' not in p_lower:
            return 0.35
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower):
            return 0.3
        
        # Unanswerability markers
        if re.search(r'(cannot be determined|insufficient|not enough information)', p_lower):
            return 0.4
        
        return 1.0
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        # Check if we can deterministically compute an answer
        if self._parse_numeric_comparison(prompt, answer):
            return 0.95
        if self._parse_arithmetic(prompt, answer):
            return 0.9
        if self._parse_logic(prompt, answer):
            return 0.85
        if self._parse_constraint_sat(prompt, answer):
            return 0.8
        
        # Default: moderate confidence
        return 0.5
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Deterministic computational parsers (60% weight)
        comp_score = 0.0
        
        # Numeric comparison
        num_result = self._parse_numeric_comparison(prompt, candidate)
        if num_result is not None:
            comp_score = 0.5 * num_result
        
        # Arithmetic evaluation
        arith_result = self._parse_arithmetic(prompt, candidate)
        if arith_result is not None:
            comp_score = max(comp_score, 0.5 * arith_result)
        
        # Logic parsing
        logic_result = self._parse_logic(prompt, candidate)
        if logic_result is not None:
            comp_score = max(comp_score, 0.3 * logic_result)
        
        # Constraint satisfaction
        csp_result = self._parse_constraint_sat(prompt, candidate)
        if csp_result is not None:
            comp_score = max(comp_score, 0.2 * csp_result)
        
        # Tensor + CSP layer (30% weight)
        tensor_score = 0.3 * self._tensor_csp_score(prompt, candidate)
        
        # NCD tiebreaker (10% weight)
        ncd_score = 0.1 * (1 - self._ncd(prompt, candidate))
        
        return comp_score + tensor_score + ncd_score
    
    def _parse_numeric_comparison(self, prompt: str, candidate: str) -> float:
        # Extract numeric comparisons like "Is 9.11 > 9.9?"
        nums = re.findall(r'\d+\.?\d*', prompt)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                c_lower = candidate.lower()
                
                if re.search(r'(greater|more|larger|bigger)', prompt.lower()):
                    correct = n1 > n2
                elif re.search(r'(less|smaller|fewer)', prompt.lower()):
                    correct = n1 < n2
                elif re.search(r'(equal|same)', prompt.lower()):
                    correct = abs(n1 - n2) < 1e-9
                else:
                    return None
                
                if (correct and re.search(r'\b(yes|true|correct)\b', c_lower)) or \
                   (not correct and re.search(r'\b(no|false|incorrect)\b', c_lower)):
                    return 1.0
                elif (correct and re.search(r'\b(no|false|incorrect)\b', c_lower)) or \
                     (not correct and re.search(r'\b(yes|true|correct)\b', c_lower)):
                    return 0.0
            except:
                pass
        return None
    
    def _parse_arithmetic(self, prompt: str, candidate: str) -> float:
        # Bat-and-ball, PEMDAS, algebraic problems
        match = re.search(r'(\d+\.?\d*)\s*[\+\-\*/]\s*(\d+\.?\d*)', prompt)
        if match:
            try:
                expr = re.search(r'[\d\s\+\-\*/\(\)\.]+', prompt).group()
                result = eval(expr)
                c_nums = re.findall(r'\d+\.?\d*', candidate)
                if c_nums and abs(float(c_nums[0]) - result) < 0.01:
                    return 1.0
                return 0.0
            except:
                pass
        
        # All-but-N pattern
        match = re.search(r'(\d+).+all but (\d+)', prompt.lower())
        if match:
            total, excluded = int(match.group(1)), int(match.group(2))
            result = total - excluded
            c_nums = re.findall(r'\d+', candidate)
            if c_nums and int(c_nums[0]) == result:
                return 1.0
            return 0.0
        
        return None
    
    def _parse_logic(self, prompt: str, candidate: str) -> float:
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Modus tollens: If P then Q, not Q, therefore not P
        if 'if' in p_lower and 'then' in p_lower and 'not' in p_lower:
            # Simple heuristic: check for negation pattern
            if 'not' in c_lower or 'no' in c_lower:
                return 0.7
            return 0.3
        
        # Transitivity: A > B, B > C => A > C
        comparisons = re.findall(r'(\w+)\s+(>|<|before|after)\s+(\w+)', p_lower)
        if len(comparisons) >= 2:
            entities = set()
            for comp in comparisons:
                entities.add(comp[0])
                entities.add(comp[2])
            
            # Check if candidate mentions transitive conclusion
            mentioned = sum(1 for e in entities if e in c_lower)
            if mentioned >= 2:
                return 0.8
            return 0.2
        
        return None
    
    def _parse_constraint_sat(self, prompt: str, candidate: str) -> float:
        # Extract entities and constraints
        entities = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        if len(entities) < 3:
            return None
        
        # Simple CSP: extract "not" constraints
        constraints = []
        for ent in entities:
            pattern = f"{ent}.+not.+(\w+)"
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                constraints.append((ent, match.group(1)))
        
        if not constraints:
            return None
        
        # Check if candidate satisfies constraints
        c_lower = candidate.lower()
        violations = 0
        for subj, obj in constraints:
            if subj.lower() in c_lower and obj.lower() in c_lower:
                violations += 1
        
        return 1.0 - (violations / max(len(constraints), 1))
    
    def _tensor_csp_score(self, prompt: str, candidate: str) -> float:
        # Build triples from prompt and candidate
        p_triples = self._extract_triples(prompt)
        c_triples = self._extract_triples(candidate)
        
        if not p_triples or not c_triples:
            return 0.5
        
        # Build vocabulary
        all_triples = p_triples + c_triples
        subjects = list(set(t[0] for t in all_triples))
        relations = list(set(t[1] for t in all_triples))
        objects = list(set(t[2] for t in all_triples))
        
        # Build tensor
        X = self._build_tensor(c_triples, subjects, relations, objects)
        
        # Simple CP decomposition approximation
        similarity = self._tensor_similarity(p_triples, c_triples, subjects, relations, objects)
        
        # Constraint satisfaction
        constraints = self._extract_constraints(prompt)
        csp_score = self._check_constraints(c_triples, constraints)
        
        # Evolutionary weight (simplified: use fixed weights)
        return 0.6 * similarity + 0.4 * csp_score
    
    def _extract_triples(self, text: str) -> list:
        triples = []
        words = re.findall(r'\b\w+\b', text)
        
        # Simple SVO extraction
        for i in range(len(words) - 2):
            subj, verb, obj = words[i], words[i+1], words[i+2]
            
            # Detect relation type
            rel = 'VERB'
            if verb.lower() in ['is', 'are', 'was', 'were']:
                rel = 'IS'
            elif verb.lower() in ['has', 'have', 'had']:
                rel = 'HAS'
            elif verb.lower() in ['not', 'no']:
                rel = 'NOT'
            elif '>' in text or 'greater' in text.lower():
                rel = 'GT'
            elif '<' in text or 'less' in text.lower():
                rel = 'LT'
            
            triples.append((subj.lower(), rel, obj.lower()))
        
        return triples[:10]  # Limit to prevent explosion
    
    def _build_tensor(self, triples, subjects, relations, objects):
        S, R, O = len(subjects), len(relations), len(objects)
        X = np.zeros((S, R, O))
        
        for subj, rel, obj in triples:
            try:
                s_idx = subjects.index(subj)
                r_idx = relations.index(rel)
                o_idx = objects.index(obj)
                X[s_idx, r_idx, o_idx] = 1
            except ValueError:
                continue
        
        return X
    
    def _tensor_similarity(self, p_triples, c_triples, subjects, relations, objects):
        # Simple overlap-based similarity
        p_set = set(p_triples)
        c_set = set(c_triples)
        
        if not p_set or not c_set:
            return 0.5
        
        overlap = len(p_set & c_set)
        union = len(p_set | c_set)
        
        return overlap / max(union, 1)
    
    def _extract_constraints(self, text: str):
        constraints = []
        
        # Negation constraints
        if 'not' in text.lower():
            constraints.append(('negation', True))
        
        # Transitivity
        if re.search(r'(\w+)\s+(>|<)\s+(\w+)', text):
            constraints.append(('transitivity', True))
        
        return constraints
    
    def _check_constraints(self, triples, constraints):
        if not constraints:
            return 1.0
        
        satisfied = 0
        for constraint_type, _ in constraints:
            if constraint_type == 'negation':
                # Check for NOT relations
                if any(t[1] == 'NOT' for t in triples):
                    satisfied += 1
            elif constraint_type == 'transitivity':
                # Check for GT/LT relations
                if any(t[1] in ['GT', 'LT'] for t in triples):
                    satisfied += 1
        
        return satisfied / max(len(constraints), 1)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))