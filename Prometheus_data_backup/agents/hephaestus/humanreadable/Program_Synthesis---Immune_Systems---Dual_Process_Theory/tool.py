class ReasoningTool:
    """
    A computational reasoning tool integrating Program Synthesis, Immune Systems, and Dual Process Theory.
    
    Mechanism:
    1. Fast Stage (System 1): Parses text into a typed predicate graph (entities, relations, logic ops).
    2. Slow Stage (System 2): Synthesizes logical programs (DSL) constrained by types.
    3. Immune Optimization: Uses clonal selection to evolve programs that satisfy graph constraints.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    
    Scoring = Structural Match (50%) + Computed Result Match (35%) + NCD Tiebreaker (15%)
    """

    def __init__(self):
        self.memory_set = []  # Stores high-affinity program templates
        self.dsl_ops = ['and', 'or', 'not', 'if', 'gt', 'lt', 'eq', 'add', 'sub', 'mul', 'div']
        
    # --- SYSTEM 1: FAST PARSING (Predicate Graph Extraction) ---
    
    def _parse_graph(self, text: str) -> np.ndarray:
        """Extracts entities and relations into a structured NumPy array."""
        records = []
        text_lower = text.lower()
        
        # 1. Entity Extraction (NUM, DATE, ENTITY)
        entities = {}
        # Numbers
        for m in re.finditer(r'(-?\d+(?:\.\d+)?)', text):
            val = m.group(1)
            entities[val] = 'NUM'
            records.append((val, 'IS_NUM', 'TRUE'))
            
        # Dates (Simple)
        for m in re.finditer(r'\b(\d{1,2}/\d{1,2}/\d{2,4}|\w+\s\d{1,2},?\s\d{4})\b', text):
            entities[m.group(1)] = 'DATE'
            records.append((m.group(1), 'IS_DATE', 'TRUE'))

        # 2. Relation Extraction (Predicates)
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(?:is greater than|>|exceeds)\s+(\w+)', text_lower):
            records.append((m.group(1), 'gt', m.group(2)))
        for m in re.finditer(r'(\w+)\s+(?:is less than|<|under)\s+(\w+)', text_lower):
            records.append((m.group(1), 'lt', m.group(2)))
            
        # Logic/Negation
        if re.search(r'\b(not|no|never|without)\b', text_lower):
            records.append(('global', 'has_negation', 'true'))
            
        # Conditionals
        if re.search(r'\b(if|unless|provided)\b', text_lower):
            records.append(('global', 'is_conditional', 'true'))
            
        # Causal
        if re.search(r'\b(because|therefore|leads to|causes)\b', text_lower):
            records.append(('global', 'is_causal', 'true'))

        # SVO Parsing (Simplified for Subject-Verb-Object)
        # Pattern: Word Word Word (Noun Verb Noun approx)
        # This is a heuristic fallback for structure
        verbs = ['has', 'have', 'is', 'are', 'owns', 'kills', 'eats', 'sees', 'told', 'said']
        for v in verbs:
            pattern = r'(\w+)\s+' + v + r'\s+(\w+)'
            for m in re.finditer(pattern, text_lower):
                records.append((m.group(1), v, m.group(2)))

        if not records:
            # Fallback empty structure
            return np.array([], dtype=[('subj', 'U20'), ('pred', 'U20'), ('obj', 'U20')])
            
        return np.array(records, dtype=[('subj', 'U20'), ('pred', 'U20'), ('obj', 'U20')])

    # --- SYSTEM 2: PROGRAM SYNTHESIS & IMMUNE OPTIMIZATION ---

    def _generate_initial_population(self, graph: np.ndarray, size: int = 10) -> List[Dict]:
        """Generates random DSL programs that type-check against the graph."""
        population = []
        constants = list(set(graph['subj'])) if len(graph) > 0 else ['val']
        
        for _ in range(size):
            # Randomly construct a simple logic chain
            depth = np.random.randint(1, 3)
            program = []
            for _ in range(depth):
                op = np.random.choice(self.dsl_ops)
                if op in ['gt', 'lt', 'eq']:
                    if len(constants) >= 2:
                        c1, c2 = np.random.choice(constants, 2, replace=False)
                        program.append(f"{op}({c1},{c2})")
                elif op == 'not':
                    if constants:
                        c = np.random.choice(constants)
                        program.append(f"not({c})")
                else:
                    if constants:
                        c = np.random.choice(constants)
                        program.append(f"{op}({c},1)") # Dummy arg for math ops
            
            if not program: program = ["eq(1,1)"] # Fallback
            
            population.append({
                'code': ' && '.join(program),
                'length': len(program),
                'predicates': set(re.findall(r'\b(' + '|'.join(self.dsl_ops) + r')\b', ' '.join(program)))
            })
        return population

    def _evaluate_program(self, program_code: str, graph: np.ndarray) -> Tuple[bool, float]:
        """
        Executes the DSL program against the graph constraints.
        Returns (is_valid, satisfaction_rate).
        """
        if not program_code: return False, 0.0
        
        satisfied = 0
        total_checks = 0
        
        # Extract constraints from graph for evaluation
        # We simulate execution by checking if program logic aligns with graph facts
        try:
            # Simple interpreter for the specific DSL generated
            # Format: "op(a,b) && op(c,d)"
            clauses = program_code.split(' && ')
            for clause in clauses:
                clause = clause.strip()
                if not clause: continue
                
                # Parse op(args)
                match = re.match(r'(\w+)\(([^)]+)\)', clause)
                if not match: continue
                op, args_str = match.groups()
                args = [a.strip() for a in args_str.split(',')]
                
                total_checks += 1
                
                # Check against graph
                if op == 'gt':
                    # Try to find numeric values or compare strings as proxies
                    # If both are in graph as numbers, compare them
                    found = False
                    for r in graph:
                        if r['subj'] == args[0] and r['pred'] == 'gt' and r['obj'] == args[1]:
                            satisfied += 1; found = True; break
                        # Heuristic: if args are numbers, compare directly
                        try:
                            if float(args[0]) > float(args[1]):
                                satisfied += 1; found = True; break
                        except: pass
                    if not found: 
                        # Soft match: does the graph imply this?
                        pass 
                        
                elif op == 'not':
                    # Check if negation exists in graph
                    has_neg = any(graph['pred'] == 'has_negation') if len(graph) > 0 else False
                    if has_neg: satisfied += 1
                    
                elif op == 'eq':
                     try:
                        if float(args[0]) == float(args[1]):
                            satisfied += 1
                     except:
                        if args[0] == args[1]: satisfied += 1
                else:
                    # Default assume partial satisfaction for complex ops to avoid zeroing out
                    satisfied += 0.5 

            return True, (satisfied / total_checks) if total_checks > 0 else 0.0
        except:
            return False, 0.0

    def _clonal_selection(self, graph: np.ndarray, generations: int = 5) -> List[Dict]:
        """Evolves programs to maximize constraint satisfaction."""
        pop = self._generate_initial_population(graph)
        
        for _ in range(generations):
            # Affinity Calculation
            scored_pop = []
            for p in pop:
                valid, sat = self._evaluate_program(p['code'], graph)
                # Affinity = w1*sat - w2*len + w3*nov
                nov = 1.0 # Simplified novelty
                aff = 0.6 * sat - 0.2 * p['length'] + 0.2 * nov
                scored_pop.append((p, aff))
            
            # Sort by affinity
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            
            # Selection (Top K)
            top_k = scored_pop[:len(scored_pop)//2 + 1]
            if not top_k: top_k = scored_pop[:1]
            
            # Cloning and Mutation
            new_pop = [x[0] for x in top_k]
            for p, _ in top_k:
                # Mutate: swap predicate or add node
                mutant = p.copy()
                if np.random.random() < 0.5 and len(self.dsl_ops) > 0:
                    # Swap op
                    new_op = np.random.choice(self.dsl_ops)
                    mutant['code'] = re.sub(r'\b\w+\(', new_op + '(', mutant['code'], count=1)
                    mutant['length'] += 1
                new_pop.append(mutant)
            
            pop = new_pop[:10] # Keep population size fixed
            
        return pop

    # --- EPISTEMIC HONESTY (Tier B) ---

    def _meta_confidence(self, prompt: str) -> float:
        """Checks prompt for ambiguity, presupposition, and unanswerability."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'\b(have you stopped|why did .*(?:fail|stop|quit)|when did .*(?:stop|fail))\b', p):
            score -= 0.8
        # 2. Scope Ambiguity
        if re.search(r'\b(every .*(?:did|has) a|same .*(?:for|with))\b', p):
            score -= 0.4
        # 3. Pronoun Ambiguity
        if re.search(r'\b(told .*(?:he|she|it|they)|who is .*(?:he|she|it|they))\b', p):
            score -= 0.5
        # 4. False Dichotomy
        if re.search(r'\b(either .*(?:or|else)|must be (?:a|b|true|false))\b', p):
            score -= 0.3
        # 5. Subjectivity
        if re.search(r'\b(best|worst|favorite|beautiful|ugly)\b', p) and not re.search(r'\b(data|statistic|number)\b', p):
            score -= 0.6
        # 6. Unanswerability markers
        if re.search(r'\b(insufficient|missing|unknown|cannot be determined)\b', p):
            score -= 0.9
            
        return max(0.0, min(1.0, score))

    def _compute_answer(self, prompt: str) -> Optional[Any]:
        """
        Attempts to computationally solve the problem based on parsed structure.
        Returns the computed value or None if unsolvable.
        """
        graph = self._parse_graph(prompt)
        p_lower = prompt.lower()
        
        # 1. Numeric Comparison / Math
        nums = re.findall(r'(-?\d+(?:\.\d+)?)', prompt)
        if len(nums) >= 2:
            floats = [float(n) for n in nums]
            # Bat-and-ball or simple algebra heuristics
            if 'sum' in p_lower or 'total' in p_lower:
                return sum(floats)
            if 'difference' in p_lower:
                return max(floats) - min(floats)
            if 'greater' in p_lower or '>' in prompt:
                return max(floats)
            if 'less' in p_lower or '<' in prompt:
                return min(floats)
            # Modular arithmetic check
            if 'mod' in p_lower or 'remainder' in p_lower:
                if len(floats) == 2: return int(floats[0]) % int(floats[1])
        
        # 2. Logic / Constraint Satisfaction
        # If graph has 'gt' relations, try to sort entities
        if len(graph) > 0:
            # Extract ordering
            try:
                # Simple transitivity check for small sets
                entities = list(set(graph['subj']))
                if len(entities) <= 5:
                    # Try to order based on 'gt'
                    order = []
                    for e in entities:
                        count = 0
                        for r in graph:
                            if r['pred'] == 'gt' and r['subj'] == e: count += 1
                        order.append((e, count))
                    order.sort(key=lambda x: x[1], reverse=True)
                    if order: return order[0][0] # Return top entity
            except: pass

        # 3. Boolean Logic
        if 'true' in p_lower or 'false' in p_lower:
            if 'not' in p_lower and 'true' in p_lower: return 'false'
            if 'not' in p_lower and 'false' in p_lower: return 'true'
            if 'true' in p_lower: return 'true'
            if 'false' in p_lower: return 'false'

        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_graph = self._parse_graph(prompt)
        computed_val = self._compute_answer(prompt)
        
        # Run immune optimization to get best reasoning program
        best_programs = self._clonal_selection(prompt_graph)
        best_prog = best_programs[0] if best_programs else None
        
        results = []
        for cand in candidates:
            cand_graph = self._parse_graph(cand)
            score = 0.0
            reasoning = ""
            
            # 1. Structural Score (50%)
            # Does the candidate share predicates with the prompt's best program?
            struct_score = 0.0
            if best_prog:
                # Check if candidate contains keywords from the program
                matches = 0
                for op in self.dsl_ops:
                    if op in best_prog['code'] and op in cand.lower():
                        matches += 1
                struct_score = min(1.0, matches / 2.0) # Normalize
            
            # 2. Computational Score (35%)
            comp_score = 0.0
            if computed_val is not None:
                # Check if candidate string represents the computed value
                cand_nums = re.findall(r'(-?\d+(?:\.\d+)?)', cand)
                if cand_nums:
                    try:
                        if float(cand_nums[0]) == float(computed_val):
                            comp_score = 1.0
                        elif abs(float(cand_nums[0]) - float(computed_val)) < 1e-6:
                            comp_score = 1.0
                    except: pass
                # String match for boolean/logic
                elif str(computed_val).lower() in cand.lower():
                    comp_score = 1.0
            
            # 3. NCD Tiebreaker (15%) - Only if others are close
            ncd_score = 0.0
            if abs(struct_score + comp_score) < 0.1:
                # Fallback to similarity if no logic hits
                s1 = prompt + cand
                s2 = prompt
                try:
                    c1 = len(s1.encode('utf-8')) - len(re.sub(r'(.)(?=.)', r'\1', s1).encode('utf-8')) # Rough compression proxy
                    c2 = len(s2.encode('utf-8')) - len(re.sub(r'(.)(?=.)', r'\1', s2).encode('utf-8'))
                    # Simplified NCD approximation
                    ncd_score = 1.0 - (len(s1) / (len(s1) + len(s2))) if len(s1)+len(s2) > 0 else 0
                except: pass

            final_score = (0.50 * struct_score) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Construct reasoning string
            reason_parts = []
            if comp_score > 0: reason_parts.append(f"Computed value match ({computed_val})")
            if struct_score > 0: reason_parts.append(f"Structural alignment with DSL")
            if not reason_parts: reason_parts.append("Heuristic match")
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": "; ".join(reason_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check Meta-Confidence (Epistemic Honesty)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # 2. Evaluate specific answer
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        base_score = eval_results[0]['score']
        
        # Cap confidence based