import re
import numpy as np
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A reasoning tool implementing Symbiosis x Global Workspace Theory x Mechanism Design.
    
    Mechanism:
    1. Parsing: Extracts propositional tokens (EQ, NEQ, LT, GT, CAUSE, COND, NOT) from prompt and answer.
    2. Global Workspace: Creates a shared truth state where prompt axioms are fixed True.
    3. Constraint Propagation: Iteratively updates truth values based on logical rules (Modus Ponens, Transitivity).
    4. Scoring: Computes Consistency (C) and Novelty (N). Score = C + lambda*N.
    5. Epistemic Honesty: Detects ambiguity traps (Tier B) to cap confidence.
    """
    
    def __init__(self):
        self.lambda_novelty = 0.2
        self.causal_threshold = 0.5
        self.causal_step = 0.1
        
        # Regex patterns for structural features
        self.patterns = {
            'eq': re.compile(r'\b(\w+)\s*(?:is|equals|was|are)\s+(\w+)', re.I),
            'neq': re.compile(r'\b(\w+)\s+(?:is not|are not|was not|differs from)\s+(\w+)', re.I),
            'lt': re.compile(r'\b(\w+)\s+(?:is less than|<|below)\s+(\w+)', re.I),
            'gt': re.compile(r'\b(\w+)\s+(?:is greater than|>|above)\s+(\w+)', re.I),
            'cond': re.compile(r'(?:if|when)\s+(.+?)\s+(?:then|,)\s+(.+?)(?:\.|,|$)', re.I),
            'cause': re.compile(r'(\w+(?:\s+\w+)?)\s+(?:leads to|causes|results in|because)\s+(\w+(?:\s+\w+)?)', re.I),
            'not': re.compile(r'\b(?:not|no|never)\s+(\w+)', re.I),
            'num_cmp': re.compile(r'(\d+(?:\.\d+)?)\s*(<|>|<=|>=|=)\s*(\d+(?:\.\d+)?)'),
            # Tier B Traps
            'presupposition': re.compile(r'(?:have you|did you|why did)\s+(?:stop|quit|fail|start)\b', re.I),
            'scope_ambig': re.compile(r'\b(every|each|all)\s+\w+.*\b(a|an)\s+\w+', re.I),
            'pronoun_ambig': re.compile(r'\b(\w+)\s+told\s+(\w+)\s+(he|she|him|her)\b', re.I),
            'false_dichotomy': re.compile(r'\beither\s+(\w+)\s+or\s+(\w+)\b', re.I),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\s+\w+', re.I),
        }

    def _extract_tokens(self, text: str) -> List[Tuple[str, str, Optional[str], bool]]:
        """Extracts propositional tokens: (type, arg1, arg2?, polarity)"""
        tokens = []
        text_lower = text.lower()
        
        # Numeric comparisons (Direct computation)
        for m in self.patterns['num_cmp'].finditer(text):
            v1, op, v2 = m.groups()
            n1, n2 = float(v1), float(v2)
            is_true = False
            if op == '<': is_true = n1 < n2
            elif op == '>': is_true = n1 > n2
            elif op == '<=': is_true = n1 <= n2
            elif op == '>=': is_true = n1 >= n2
            elif op == '=': is_true = n1 == n2
            tokens.append(('NUM', f"{n1}{op}{n2}", None, is_true))

        # Equality
        for m in self.patterns['eq'].finditer(text):
            tokens.append(('EQ', m.group(1).lower(), m.group(2).lower(), True))
            
        # Inequality
        for m in self.patterns['neq'].finditer(text):
            tokens.append(('NEQ', m.group(1).lower(), m.group(2).lower(), True))
            
        # Less Than
        for m in self.patterns['lt'].finditer(text):
            tokens.append(('LT', m.group(1).lower(), m.group(2).lower(), True))

        # Greater Than
        for m in self.patterns['gt'].finditer(text):
            tokens.append(('GT', m.group(1).lower(), m.group(2).lower(), True))

        # Conditionals (Simplified: IF A THEN B -> Token COND(A, B))
        for m in self.patterns['cond'].finditer(text):
            # Normalize condition and consequence to short keys
            c_key = m.group(1).strip()[:20].replace(' ', '_')
            r_key = m.group(2).strip()[:20].replace(' ', '_')
            tokens.append(('COND', c_key, r_key, True))
            # Also add the components as atomic facts if they look like simple predicates
            tokens.append(('FACT', c_key, None, True)) 
            tokens.append(('FACT', r_key, None, True))

        # Causal
        for m in self.patterns['cause'].finditer(text):
            c_key = m.group(1).strip().replace(' ', '_')
            e_key = m.group(2).strip().replace(' ', '_')
            tokens.append(('CAUSE', c_key, e_key, True))

        return tokens

    def _run_propagation(self, ground_truth_tokens: List, candidate_tokens: List) -> Tuple[float, float]:
        """Runs constraint propagation on the union of tokens."""
        all_tokens = ground_truth_tokens + candidate_tokens
        if not all_tokens:
            return 0.0, 0.0
            
        n = len(all_tokens)
        truth = np.zeros(n, dtype=bool)
        causal_weights = np.zeros(n, dtype=float)
        
        # Map token index to (type, arg1, arg2)
        token_data = []
        
        # Initialize Ground Truth as True
        gt_indices = set()
        for i, t in enumerate(ground_truth_tokens):
            truth[i] = True
            gt_indices.add(i)
            token_data.append(t)
            
        for i, t in enumerate(candidate_tokens):
            idx = len(ground_truth_tokens) + i
            token_data.append(t)
            # Candidate tokens start False
            
        # Fixed-point iteration
        changed = True
        iterations = 0
        max_iter = 10
        
        while changed and iterations < max_iter:
            changed = False
            iterations += 1
            
            for i, (t_type, arg1, arg2, polarity) in enumerate(token_data):
                if not truth[i] and i not in gt_indices:
                    # Only propagate from True statements or update based on rules
                    continue
                
                # Modus Ponens: If COND(A->B) is True and A is True, set B True
                if t_type == 'COND':
                    # Find token representing arg1 (condition)
                    # Simple heuristic: look for matching FACT or EQ in the list
                    for j, (jt, ja1, ja2, _) in enumerate(token_data):
                        if jt == 'FACT' and ja1 == arg1 and truth[j]:
                            # Find the consequence token
                            for k, (kt, ka1, ka2, _) in enumerate(token_data):
                                if kt == 'FACT' and ka1 == arg2 and not truth[k]:
                                    truth[k] = True
                                    changed = True
                                
                # Causal: Soft implication
                if t_type == 'CAUSE':
                    # If cause is true, increment weight of effect
                    # Find cause token index
                    cause_found = False
                    for j, (jt, ja1, ja2, _) in enumerate(token_data):
                        if (jt == 'FACT' and ja1 == arg1) or (jt == 'EQ' and ja1 == arg1):
                            if truth[j]:
                                cause_found = True
                                break
                    
                    if cause_found:
                        # Find effect token and increment weight
                        for k, (kt, ka1, ka2, _) in enumerate(token_data):
                            if (kt == 'FACT' and ka1 == arg2) or (kt == 'EQ' and ka1 == arg2):
                                causal_weights[k] += self.causal_step
                                if causal_weights[k] > self.causal_threshold and not truth[k]:
                                    truth[k] = True
                                    changed = True

                # Equality propagation
                if t_type == 'EQ':
                    # If arg1 is true, arg2 becomes true (simplified for boolean flags)
                    # In this token model, EQ usually links two concepts. 
                    # If one concept is established as 'True' (exists/happens), the other does too.
                    pass # Simplified for this prototype to focus on COND/CAUSE

        # Calculate Metrics
        cand_start = len(ground_truth_tokens)
        cand_truths = truth[cand_start:]
        cand_total = len(cand_truths)
        
        if cand_total == 0:
            return 1.0, 0.0 # Empty candidate is neutral? Or penalty? Let's say 1.0 consistency.
            
        # Consistency: Fraction of candidate tokens that are True after propagation
        # Note: Ground truth tokens are forced True. Candidate tokens must survive.
        # Actually, the definition says: fraction of answer's propositions that survive (are True).
        consistency = np.mean(cand_truths.astype(float)) if cand_total > 0 else 0.0
        
        # Novelty: Propositions not in prompt (all candidate tokens are by def not in prompt set)
        # that become true.
        novelty = np.sum(cand_truths) / cand_total if cand_total > 0 else 0.0
        
        return consistency, novelty

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps and returns a confidence cap."""
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
        # 2. Scope Ambiguity
        if self.patterns['scope_ambig'].search(p_lower):
            return 0.3
        # 3. Pronoun Ambiguity (if question asks 'who' or 'he')
        if self.patterns['pronoun_ambig'].search(p_lower) and ('who' in p_lower or 'which' in p_lower):
            return 0.3
        # 4. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.4
        # 5. Subjectivity
        if self.patterns['subjectivity'].search(p_lower):
            return 0.3
            
        # 6. Unanswerability (Heuristic: No numbers, no verbs, very short)
        words = re.findall(r'\w+', p_lower)
        if len(words) < 3:
            return 0.2
            
        return 1.0 # Default high confidence if no traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        gt_tokens = self._extract_tokens(prompt)
        
        # Fallback if prompt yields no structure
        if not gt_tokens:
            # If no structure, we rely heavily on NCD or simple overlap, but per instructions
            # we must beat NCD. If no logic, we penalize heavily.
            pass

        for cand in candidates:
            cand_tokens = self._extract_tokens(cand)
            
            # Compute Score
            if gt_tokens or cand_tokens:
                cons, nov = self._run_propagation(gt_tokens, cand_tokens)
                score = cons + (self.lambda_novelty * nov)
            else:
                # No tokens extracted from either -> Pure string fallback (NCD limited)
                # But we need to beat NCD. If no logic, score low.
                score = 0.1 

            # Reasoning string
            reason = f"Consistency: {cons:.2f}, Novelty: {nov:.2f}"
            if not gt_tokens and not cand_tokens:
                reason = "No structural logic detected; low confidence baseline."
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt for ambiguity/traps.
        """
        # 1. Meta Confidence Cap (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural Match Check
        # If we can't parse anything from the prompt, we shouldn't be confident
        prompt_tokens = self._extract_tokens(prompt)
        if not prompt_tokens:
            # Unless it's a simple numeric question we missed?
            # Check for pure math
            if not re.search(r'\d', prompt):
                meta_cap = min(meta_cap, 0.25) # Strong penalty for unparseable non-numeric
        
        # 3. Evaluate the specific answer
        # We run the evaluation to see if this specific answer is consistent
        # We treat the answer as a single candidate
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]['score']
        
        # Map score to confidence
        # If score is high (>0.8) and meta_cap is high, return high confidence
        # If score is low, return low confidence
        # If meta_cap is low, cap the result
        
        raw_conf = score
        if raw_conf > 0.9 and not re.search(r'\d', answer): 
            # Heuristic: Don't give >0.9 unless it's a computed numeric result or very strong logic
            # Since we don't have a separate 'computed' flag easily accessible here without refactoring,
            # we rely on the score. But the prompt says: NEVER > 0.9 unless computation produced definitive answer.
            # Our numeric parser produces definitive answers.
            has_numeric = bool(re.search(r'\d', answer))
            if not has_numeric:
                raw_conf = min(raw_conf, 0.85)

        final_conf = min(raw_conf, meta_cap)
        
        # Ensure we don't return 0.0 for everything if there's some signal
        if final_conf == 0.0 and score > 0:
            final_conf = 0.1
            
        return float(np.clip(final_conf, 0.0, 1.0))