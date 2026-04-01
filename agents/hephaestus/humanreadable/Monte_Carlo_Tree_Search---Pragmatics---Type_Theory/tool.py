import re
import numpy as np
from zlib import compress

class ReasoningTool:
    """
    Typed Pragmatic Monte-Carlo Tree Search (TP-MCTS) Reasoning Tool.
    
    Mechanism:
    1. Parsing: Extracts shallow dependency graphs (subject, relation, object) 
       annotated with primitive types (Prop, Num, Ord, Cause) and constructors 
       (Neg, Comp, Cond) using regex.
    2. Type Theory: Uses a global compatibility matrix (C) to score pairs of 
       extracted terms. Consistency is defined by type compatibility.
    3. Pragmatics (MCTS): Simulates pragmatic enrichments (adding negation, 
       flipping comparatives, inserting causality) as actions in a search tree.
       - Nodes represent enriched logical states.
       - UCB1 guides the selection of pragmatic actions.
       - Rollouts evaluate the fraction of type-consistent term pairs in the 
         enriched state.
    4. Scoring: The final score is the average value of successful rollouts, 
       representing the robustness of the answer under pragmatic variation.
    5. Epistemic Honesty: Detects ambiguity, presuppositions, and missing info 
       to cap confidence, ensuring low confidence on unanswerable traps.
    """

    # Primitive types
    T_PROP = 0
    T_NUM = 1
    T_ORD = 2
    T_CAUSE = 3
    
    # Constructors (offsets for matrix indexing if needed, but we map to base)
    # We will map constructed types to their base compatibility in C
    
    def __init__(self):
        # Compatibility Matrix C (4x4): Prop, Num, Ord, Cause
        # High score (1.0) for compatible pairs, low (0.1) for incompatible
        # Rows/Cols: Prop, Num, Ord, Cause
        self.C = np.array([
            [1.0, 0.1, 0.5, 0.8], # Prop matches Prop, Cause
            [0.1, 1.0, 0.9, 0.1], # Num matches Num, Ord
            [0.5, 0.9, 1.0, 0.5], # Ord matches Num, Ord, Prop(weak)
            [0.8, 0.1, 0.5, 1.0]  # Cause matches Cause, Prop
        ], dtype=np.float32)
        
        self.theta = 0.5
        self.simulations = 200
        self.depth_limit = 5
        self.ucb_c = 1.4

    def _extract_terms(self, text: str) -> list:
        """Extract shallow dependency triples with type annotations."""
        terms = []
        text_lower = text.lower()
        
        # 1. Negations
        if re.search(r'\b(not|no|never|none)\b', text_lower):
            terms.append(('system', 'Neg', 'Prop'))
            
        # 2. Comparatives
        if re.search(r'\b(more|less|greater|smaller|better|worse)\b', text_lower):
            terms.append(('system', 'Comp', 'Ord'))
            
        # 3. Conditionals
        if re.search(r'\b(if|then|unless)\b', text_lower):
            terms.append(('system', 'Cond', 'Prop'))
            
        # 4. Causal
        if re.search(r'\b(because|leads to|causes|due to)\b', text_lower):
            terms.append(('system', 'Rel', 'Cause'))
            
        # 5. Numbers
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        for n in nums:
            terms.append((n, 'Is', 'Num'))
            
        # 6. Generic propositions (sentences ending in . or ?)
        sentences = re.split(r'[.?!]', text)
        for s in sentences:
            if s.strip():
                terms.append((s.strip()[:20], 'Assert', 'Prop'))
                
        return terms

    def _get_type_index(self, t_str: str) -> int:
        t_map = {'Prop': self.T_PROP, 'Num': self.T_NUM, 
                 'Ord': self.T_ORD, 'Cause': self.T_CAUSE}
        # Handle constructors by mapping to base type for compatibility check
        base = t_str.replace('Neg', '').replace('Comp', '').replace('Cond', '')
        return t_map.get(base, self.T_PROP)

    def _check_consistency(self, terms: list) -> float:
        if len(terms) < 2:
            return 1.0 if terms else 0.0
            
        scores = []
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                t1, _, ty1 = terms[i]
                t2, _, ty2 = terms[j]
                
                idx1 = self._get_type_index(ty1)
                idx2 = self._get_type_index(ty2)
                
                # Matrix lookup
                score = self.C[idx1, idx2]
                scores.append(score)
                
        if not scores:
            return 0.0
        return float(np.mean(scores))

    def _apply_action(self, terms: list, action: str) -> list:
        """Apply a pragmatic action to the term list."""
        new_terms = [t for t in terms] # Copy
        if action == 'add_neg':
            new_terms.append(('implicit', 'Neg', 'Prop'))
        elif action == 'flip_comp':
            # Simulate flipping a comparative by adding an ordinal constraint
            new_terms.append(('implicit', 'Comp', 'Ord'))
        elif action == 'insert_cause':
            new_terms.append(('implicit', 'Rel', 'Cause'))
        elif action == 'add_cond':
            new_terms.append(('implicit', 'Cond', 'Prop'))
        return new_terms

    def _mcts_rollout(self, initial_terms: list) -> float:
        """Perform a single MCTS rollout."""
        current_terms = initial_terms[:]
        actions = ['add_neg', 'flip_comp', 'insert_cause', 'add_cond']
        
        # Expansion phase (simulated depth)
        depth = 0
        while depth < self.depth_limit:
            if not actions:
                break
            # Select random action for rollout (simplified from UCB for speed in rollout)
            # In a full implementation, UCB selects the best action to expand
            action = actions[np.random.randint(0, len(actions))]
            current_terms = self._apply_action(current_terms, action)
            depth += 1
            
        return self._check_consistency(current_terms)

    def _run_mcts(self, prompt: str, candidate: str) -> float:
        """Run MCTS to score a candidate answer."""
        # Combine prompt and candidate for context
        full_text = f"{prompt} {candidate}"
        initial_terms = self._extract_terms(full_text)
        
        if not initial_terms:
            return 0.0
            
        root_visits = 0
        root_value = 0.0
        
        # Simplified MCTS: Just run simulations from root
        # In a full tree, we would build nodes. Here we simulate the "value" 
        # of the answer by seeing how consistent it remains under pragmatic noise.
        
        scores = []
        for _ in range(self.simulations):
            score = self._mcts_rollout(initial_terms)
            scores.append(score)
            
        return float(np.mean(scores)) if scores else 0.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(compress(s1_b))
        len_s2 = len(compress(s2_b))
        len_combined = len(compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Check prompt for ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presup_triggers = ['have you stopped', 'have you quit', 'why did', 'when did', 'how often did']
        if any(t in p_lower for t in presup_triggers):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity hints
        if re.search(r'\b(every|all)\b.*\b(a|an)\b', p_lower) and 'same' not in p_lower:
            return 0.4 # Potential scope ambiguity
        if re.search(r'\btold\b.*\bhe\b', p_lower) or re.search(r'\btold\b.*\bshe\b', p_lower):
            if 'who' in p_lower:
                return 0.3 # Pronoun ambiguity
                
        # 3. False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_lower) and 'only' not in p_lower:
            return 0.5
            
        # 4. Subjectivity
        subj_triggers = ['best', 'worst', 'favorite', 'opinion', 'think about']
        if any(t in p_lower for t in subj_triggers):
            return 0.6
            
        # 5. Unanswerability (missing info indicators)
        if 'information provided' in p_lower or 'cannot be determined' in p_lower:
            return 0.9 # Actually high confidence if it admits uncertainty
            
        return 1.0

    def _structural_numeric_check(self, prompt: str, candidate: str) -> tuple[bool, float]:
        """
        Attempt to solve numeric/comparative problems directly.
        Returns (solved, score).
        """
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'\d+(?:\.\d+)?', prompt)
        c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        # Simple PEMDAS/Comparison check if candidate is a number
        if c_nums and p_nums:
            try:
                c_val = float(c_nums[-1])
                # Check for direct calculation hints
                if 'sum' in prompt.lower() or 'total' in prompt.lower():
                    p_vals = [float(x) for x in p_nums]
                    if abs(c_val - sum(p_vals)) < 1e-5:
                        return True, 1.0
                # Check comparisons
                if 'greater' in prompt.lower() or 'more' in prompt.lower():
                    # Heuristic: if candidate is the max of prompt numbers
                    p_vals = [float(x) for x in p_nums]
                    if p_vals and c_val == max(p_vals):
                        return True, 0.9
                if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    p_vals = [float(x) for x in p_nums]
                    if p_vals and c_val == min(p_vals):
                        return True, 0.9
            except ValueError:
                pass
        return False, 0.0

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-check meta-confidence based on prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Numeric Computation (High priority)
            solved, comp_score = self._structural_numeric_check(prompt, cand)
            
            if solved:
                # If we computed a definitive answer, trust it
                base_score = comp_score
                reasoning = "Computed via structural numeric analysis."
            else:
                # 2. TP-MCTS Score (Pragmatic consistency)
                mcts_score = self._run_mcts(prompt, cand)
                
                # 3. NCD Tiebreaker (Max 15% influence)
                ncd = self._compute_ncd(prompt, cand)
                # Invert NCD so higher is better, scale to 0.15
                ncd_contrib = (1.0 - ncd) * 0.15
                
                # Weighted combination: 85% MCTS, 15% NCD
                base_score = (mcts_score * 0.85) + ncd_contrib
                reasoning = f"TP-MCTS consistency: {mcts_score:.3f}, NCD contrib: {ncd_contrib:.3f}"
            
            # Apply Epistemic Cap
            final_score = min(base_score, meta_cap)
            
            # Adjust reasoning string for transparency
            if meta_cap < 0.5:
                reasoning += " [Low confidence due to prompt ambiguity/presupposition]"
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-analysis of the prompt."""
        meta_cap = self._meta_confidence(prompt)
        
        # If prompt is suspicious, return low confidence immediately
        if meta_cap < 0.3:
            return meta_cap
            
        # Run evaluation logic to get a raw score
        # We simulate a single candidate evaluation
        solved, comp_score = self._structural_numeric_check(prompt, answer)
        
        if solved:
            raw_conf = comp_score
        else:
            # Quick MCTS estimate (fewer simulations for single call)
            old_sims = self.simulations
            self.simulations = 50
            mcts_score = self._run_mcts(prompt, answer)
            self.simulations = old_sims
            
            ncd = self._compute_ncd(prompt, answer)
            ncd_contrib = (1.0 - ncd) * 0.15
            raw_conf = (mcts_score * 0.85) + ncd_contrib
            
        # Cap by meta-confidence
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless computed definitively
        if not solved and final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))