from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Adaptive control + compositional semantics + counterfactual reasoning.
    
    Parses prompts into logical clauses, performs counterfactual simulation by
    flipping clause polarities, and adaptively tunes weights based on constraint
    violations. Includes meta-confidence detection for ambiguous/unanswerable questions.
    """
    
    def __init__(self):
        self.alpha = 0.05
        self.weights = {
            'negation': 1.0, 'comparative': 1.0, 'conditional': 1.0,
            'causal': 1.0, 'numeric': 1.0, 'ordering': 1.0, 'quantifier': 1.0
        }
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_clauses = self._parse_clauses(prompt)
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for candidate in candidates:
            cand_clauses = self._parse_clauses(candidate)
            
            # Compute base structural score
            structural_score = self._structural_match(prompt_clauses, cand_clauses)
            
            # Counterfactual simulation
            cf_cost = self._counterfactual_cost(prompt_clauses, cand_clauses)
            
            # Numeric evaluation
            numeric_score = self._numeric_evaluation(prompt, candidate)
            
            # NCD tiebreaker (max 15%)
            ncd_score = 1.0 - self._ncd(prompt, candidate)
            
            # Weighted combination
            score = (0.50 * structural_score + 
                    0.25 * (1.0 - cf_cost) + 
                    0.15 * numeric_score + 
                    0.10 * ncd_score)
            
            reasoning = f"Structural:{structural_score:.2f} CF:{1-cf_cost:.2f} Numeric:{numeric_score:.2f}"
            if meta_conf < 0.3:
                reasoning = f"[AMBIGUOUS] {reasoning}"
            
            results.append({"candidate": candidate, "score": score, "reasoning": reasoning})
        
        # Adaptive weight update
        self._update_weights(prompt_clauses, results)
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        prompt_clauses = self._parse_clauses(prompt)
        answer_clauses = self._parse_clauses(answer)
        
        if not prompt_clauses:
            return 0.25
        
        structural = self._structural_match(prompt_clauses, answer_clauses)
        cf_cost = self._counterfactual_cost(prompt_clauses, answer_clauses)
        numeric = self._numeric_evaluation(prompt, answer)
        
        base_conf = 0.6 * structural + 0.3 * (1.0 - cf_cost) + 0.1 * numeric
        
        # Never exceed 0.9 unless definitive computation
        if numeric > 0.95:
            return min(0.92, base_conf)
        return min(0.85, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you stop|why did .+ fail|when did .+ quit)', p_lower):
            return 0.20
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an|the) \w+', p_lower) and '?' in prompt:
            return 0.22
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|were|is|are)', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.23
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be .+ or)\b', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.24
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p_lower) and not re.search(r'\b(by|according to|measured)\b', p_lower):
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot determine|insufficient|not enough information)\b', p_lower):
            return 0.21
        
        return 1.0
    
    def _parse_clauses(self, text: str) -> List[Tuple]:
        clauses = []
        t_lower = text.lower()
        
        # Negations
        for m in re.finditer(r'\b(not|never|no|n\'t)\s+(\w+)', t_lower):
            clauses.append(('negation', m.group(2), -1, self.weights['negation']))
        
        # Comparatives with numeric extraction
        for m in re.finditer(r'([\d.]+)\s*(>|<|>=|<=|greater|less|more|fewer)\s*(than\s*)?([\d.]+)?', t_lower):
            val1 = float(m.group(1)) if m.group(1) else None
            val2 = float(m.group(4)) if m.group(4) else None
            op = m.group(2)
            clauses.append(('comparative', (val1, op, val2), 1, self.weights['comparative']))
        
        # Conditionals
        for m in re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)[\.,;]', t_lower):
            clauses.append(('conditional', (m.group(1), m.group(2)), 1, self.weights['conditional']))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in|causes)\s+(\w+)', t_lower):
            clauses.append(('causal', (m.group(1), m.group(3)), 1, self.weights['causal']))
        
        # Ordering
        for m in re.finditer(r'(\w+)\s+(before|after|first|last)\s+(\w+)?', t_lower):
            clauses.append(('ordering', (m.group(1), m.group(2), m.group(3)), 1, self.weights['ordering']))
        
        # Quantifiers
        for m in re.finditer(r'\b(all|some|none|every)\s+(\w+)', t_lower):
            clauses.append(('quantifier', (m.group(1), m.group(2)), 1, self.weights['quantifier']))
        
        return clauses
    
    def _structural_match(self, prompt_clauses: List[Tuple], cand_clauses: List[Tuple]) -> float:
        if not prompt_clauses:
            return 0.5
        
        matches = 0
        for p_clause in prompt_clauses:
            for c_clause in cand_clauses:
                if p_clause[0] == c_clause[0]:
                    matches += 1
                    break
        
        return matches / len(prompt_clauses)
    
    def _counterfactual_cost(self, prompt_clauses: List[Tuple], cand_clauses: List[Tuple]) -> float:
        if not prompt_clauses:
            return 0.0
        
        total_violation = 0.0
        for c_clause in cand_clauses:
            # Flip polarity
            flipped_polarity = -c_clause[2]
            
            # Check violations against prompt clauses
            for p_clause in prompt_clauses:
                if c_clause[0] == p_clause[0]:
                    if flipped_polarity != p_clause[2]:
                        total_violation += p_clause[3]
        
        return min(1.0, total_violation / (len(prompt_clauses) + 1))
    
    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        # Extract numbers from both
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5
        
        # Check comparative statements
        comp_match = re.search(r'([\d.]+)\s*(>|<|>=|<=)\s*([\d.]+)', prompt)
        if comp_match:
            v1, op, v2 = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
            expected = self._eval_comparison(v1, op, v2)
            
            # Check if candidate confirms
            if (expected and re.search(r'\b(yes|true|correct)\b', candidate.lower())) or \
               (not expected and re.search(r'\b(no|false|incorrect)\b', candidate.lower())):
                return 1.0
        
        # Numeric overlap
        overlap = len(set(p_nums) & set(c_nums))
        return overlap / max(len(p_nums), len(c_nums)) if max(len(p_nums), len(c_nums)) > 0 else 0.5
    
    def _eval_comparison(self, v1: float, op: str, v2: float) -> bool:
        if '>' in op:
            return v1 > v2
        elif '<' in op:
            return v1 < v2
        return False
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def _update_weights(self, prompt_clauses: List[Tuple], results: List[Dict]):
        if not results:
            return
        
        # Highest score
        best = results[0]
        worst = results[-1] if len(results) > 1 else None
        
        # Increase weights for clause types in best answer
        for clause in prompt_clauses:
            clause_type = clause[0]
            if clause_type in self.weights:
                if best['score'] > 0.7:
                    self.weights[clause_type] = min(2.0, self.weights[clause_type] + self.alpha)
                elif worst and worst['score'] < 0.3:
                    self.weights[clause_type] = max(0.1, self.weights[clause_type] - self.alpha)