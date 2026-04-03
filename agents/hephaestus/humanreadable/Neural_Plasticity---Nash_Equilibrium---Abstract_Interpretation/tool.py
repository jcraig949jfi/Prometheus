from collections import defaultdict

class ReasoningTool:
    """
    Neural Plasticity x Nash Equilibrium x Abstract Interpretation
    
    Parses prompts into typed clauses (negation, conditional, comparative, causal, numeric, ordering).
    Uses abstract interpretation (constraint propagation via primitives) to derive definite/possible literals.
    Models candidates as Nash game players - each toggles literals to minimize constraint violations.
    Applies Hebbian plasticity to adjust clause-type weights based on equilibrium coherence.
    """
    
    def __init__(self):
        # Plasticity weights for each clause type (initially uniform)
        self.weights = {
            'negation': 1.0,
            'conditional': 1.0,
            'comparative': 1.0,
            'causal': 1.0,
            'numeric': 1.0,
            'ordering': 1.0
        }
        self.eta = 0.05  # Learning rate for plasticity
        
    def _parse_clauses(self, text):
        """Extract typed clauses from text using regex patterns."""
        clauses = defaultdict(list)
        
        # Negation: not, no, none, never
        neg_pattern = r'\b(not|no|none|never)\s+(\w+)'
        for m in re.finditer(neg_pattern, text.lower()):
            clauses['negation'].append(('NOT', m.group(2)))
        
        # Conditional: if...then, when...
        cond_pattern = r'\b(?:if|when)\s+([^,\.]+?)(?:\s+then\s+|\s*,\s*)([^,\.]+)'
        for m in re.finditer(cond_pattern, text.lower()):
            clauses['conditional'].append((m.group(1).strip(), m.group(2).strip()))
        
        # Comparative: greater/less than, >, <
        comp_pattern = r'(\w+)\s+((?:greater|less|more|fewer)\s+than|>|<)\s+(\w+)'
        for m in re.finditer(comp_pattern, text.lower()):
            clauses['comparative'].append((m.group(1), m.group(2), m.group(3)))
        
        # Causal: because, leads to, results in, causes
        causal_pattern = r'(\w+)\s+(because|leads?\s+to|results?\s+in|causes?)\s+(\w+)'
        for m in re.finditer(causal_pattern, text.lower()):
            clauses['causal'].append((m.group(1), m.group(3)))
        
        # Numeric values
        num_pattern = r'\b(\d+(?:\.\d+)?)\b'
        for m in re.finditer(num_pattern, text):
            clauses['numeric'].append(float(m.group(1)))
        
        # Ordering: first, second, before, after
        order_pattern = r'(\w+)\s+(before|after|first|second|precedes?|follows?)\s+(\w+)'
        for m in re.finditer(order_pattern, text.lower()):
            clauses['ordering'].append((m.group(1), m.group(2), m.group(3)))
        
        return clauses
    
    def _abstract_interpret(self, clauses):
        """Use primitives to propagate constraints and find definite/possible literals."""
        definite = set()
        possible = set()
        
        # Process conditionals with modus_ponens
        if clauses['conditional']:
            premises = [f"{a}->{b}" for a, b in clauses['conditional']]
            facts = list(clauses['negation']) if clauses['negation'] else []
            try:
                derived = modus_ponens(premises[:3], facts[:3])  # Limit for safety
                definite.update(derived if isinstance(derived, list) else [])
            except:
                pass
        
        # Process ordering with transitivity check
        if clauses['ordering']:
            relations = [(a, c) for a, op, c in clauses['ordering']]
            try:
                if check_transitivity(relations[:5]):
                    definite.add('TRANSITIVE_ORDER')
            except:
                pass
        
        # Process comparatives as numeric constraints
        if clauses['numeric'] and len(clauses['numeric']) >= 2:
            nums = sorted(clauses['numeric'])
            for i in range(len(nums) - 1):
                if nums[i] < nums[i+1]:
                    definite.add(f'NUM_{i}_LT_{i+1}')
        
        # Add all parsed elements as possible
        for clause_type, items in clauses.items():
            if items:
                possible.add(clause_type.upper())
        
        return definite, possible
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerable patterns (Tier B epistemic honesty)."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you|did you)\s+(stop|quit|cease)', p):
            return 0.2
        if re.search(r'\bwhy (did|does|is)\s+\w+\s+(fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\s+\w+.*?\ba\s+\w+', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it)\s+(was|is|said)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\s+\w+\s+or\s+\w+', p) and '?' in p:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|score|rank)\b', p):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _nash_equilibrium(self, prompt_clauses, candidate_clauses_list, max_iter=5):
        """Run best-response dynamics to Nash equilibrium."""
        n = len(candidate_clauses_list)
        # Truth vectors: 1 if candidate asserts clause type, 0 otherwise
        truth_vecs = []
        for cand_clauses in candidate_clauses_list:
            vec = {k: 1 if cand_clauses[k] else 0 for k in self.weights.keys()}
            truth_vecs.append(vec)
        
        definite, possible = self._abstract_interpret(prompt_clauses)
        
        for _ in range(max_iter):
            improved = False
            for i in range(n):
                best_utility = self._utility(truth_vecs[i], prompt_clauses, definite)
                best_vec = truth_vecs[i].copy()
                
                # Try flipping each clause type
                for clause_type in self.weights.keys():
                    new_vec = truth_vecs[i].copy()
                    new_vec[clause_type] = 1 - new_vec[clause_type]
                    new_utility = self._utility(new_vec, prompt_clauses, definite)
                    
                    if new_utility > best_utility:
                        best_utility = new_utility
                        best_vec = new_vec
                        improved = True
                
                truth_vecs[i] = best_vec
            
            if not improved:
                break
        
        return truth_vecs
    
    def _utility(self, truth_vec, prompt_clauses, definite):
        """Compute utility = -weighted_violations."""
        violations = 0
        for clause_type, weight in self.weights.items():
            # Violation if candidate asserts type but prompt has none
            if truth_vec[clause_type] == 1 and not prompt_clauses[clause_type]:
                violations += weight
            # Violation if candidate omits type but prompt has it
            if truth_vec[clause_type] == 0 and prompt_clauses[clause_type]:
                violations += weight * 0.5
        return -violations
    
    def _plasticity_update(self, truth_vecs, prompt_clauses):
        """Hebbian update: increase weights for coherent clause types."""
        coherence = {k: 0 for k in self.weights.keys()}
        n = len(truth_vecs)
        
        for clause_type in self.weights.keys():
            satisfied = sum(1 for tv in truth_vecs if tv[clause_type] == (1 if prompt_clauses[clause_type] else 0))
            coherence[clause_type] = satisfied / max(n, 1)
        
        for clause_type in self.weights.keys():
            self.weights[clause_type] += self.eta * coherence[clause_type]
            self.weights[clause_type] = max(0.1, min(2.0, self.weights[clause_type]))  # Clamp
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by Nash equilibrium utility + structural match."""
        prompt_clauses = self._parse_clauses(prompt)
        candidate_clauses_list = [self._parse_clauses(c) for c in candidates]
        
        # Nash equilibrium
        truth_vecs = self._nash_equilibrium(prompt_clauses, candidate_clauses_list)
        
        # Plasticity update
        self._plasticity_update(truth_vecs, prompt_clauses)
        
        results = []
        definite, possible = self._abstract_interpret(prompt_clauses)
        
        for i, cand in enumerate(candidates):
            # Structural score from equilibrium utility
            struct_score = -self._utility(truth_vecs[i], prompt_clauses, definite)
            struct_score = 1.0 / (1.0 + struct_score)  # Normalize
            
            # Numeric computation score
            comp_score = self._numeric_eval(prompt, cand)
            
            # NCD tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Combine: 60% structural, 25% computation, 15% NCD
            final_score = 0.6 * struct_score + 0.25 * comp_score + 0.15 * ncd_score
            
            reasoning = f"Nash-equilibrium utility, {len(definite)} definite literals, plasticity-adjusted"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _numeric_eval(self, prompt, candidate):
        """Extract and compare numeric values."""
        p_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5
        
        # Check if numeric ordering matches
        if len(c_nums) == 1 and len(p_nums) >= 2:
            if min(p_nums) <= c_nums[0] <= max(p_nums):
                return 0.8
        
        return 0.5
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1, capped by meta-confidence check."""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and check structural match
        p_clauses = self._parse_clauses(prompt)
        a_clauses = self._parse_clauses(answer)
        
        # No structural match -> low confidence
        if not any(p_clauses.values()):
            return min(0.25, meta_conf)
        
        # Count matching clause types
        matches = sum(1 for k in self.weights.keys() if bool(p_clauses[k]) == bool(a_clauses[k]))
        struct_conf = matches / len(self.weights)
        
        # Numeric agreement
        p_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', prompt)]
        a_nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', answer)]
        
        num_conf = 0.5
        if p_nums and a_nums:
            num_conf = 0.8 if any(pn in a_nums for pn in p_nums) else 0.3
        
        # Combine and cap by meta-confidence
        raw_conf = 0.6 * struct_conf + 0.4 * num_conf
        return min(raw_conf, meta_conf, 0.85)  # Never exceed 0.85 for epistemic honesty