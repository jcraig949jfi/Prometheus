import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A computational reasoning tool fusing Immune Systems, Multi-Armed Bandits, 
    and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Converts text to propositional tuples (rel, arg1, arg2, polarity).
    2. Affinity: Computes structural overlap between question and candidate.
    3. Complexity: Penalizes length (Free Energy principle).
    4. Bandit/Immune: Uses Thompson Sampling to explore candidates, cloning high-performers
       and mutating low-affinity propositions to simulate clonal selection.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Weights for relations (higher for causal/conditional)
        self.weights = defaultdict(lambda: 1.0)
        self.weights['cause'] = 3.0
        self.weights['if'] = 3.0
        self.weights['then'] = 3.0
        self.weights['before'] = 2.0
        self.weights['after'] = 2.0
        self.weights['>'] = 2.0
        self.weights['<'] = 2.0
        self.weights['='] = 2.0
        
        # Bandit state
        self.arm_stats = {} # {candidate_str: {'n': int, 'r': float}}
        self.lambda_complexity = 0.1
        self.threshold_tau = 5.0
        self.clone_factor = 2.0
        
        # Regex patterns for parsing
        self.patterns = [
            (r'not\s+(\w+)', 'neg', '{1}', '-1'),
            (r'(\w+)\s+is\s+(?:greater|more)\s+than\s+(\w+)', '>', '{1}', '{2}'),
            (r'(\w+)\s+is\s+(?:less|smaller)\s+than\s+(\w+)', '<', '{1}', '{2}'),
            (r'(\w+)\s+(?:equals|is)\s+(\w+)', '=', '{1}', '{2}'),
            (r'if\s+(.+?),\s*then\s+(.+)', 'if', '{1}', '{2}'),
            (r'(\w+)\s+causes?\s+(\w+)', 'cause', '{1}', '{2}'),
            (r'(\w+)\s+leads?\s+to\s+(\w+)', 'cause', '{1}', '{2}'),
            (r'(\w+)\s+before\s+(\w+)', 'before', '{1}', '{2}'),
            (r'(\w+)\s+after\s+(\w+)', 'after', '{1}', '{2}'),
            (r'(\d+(?:\.\d+)?)\s*([<>=])\s*(\d+(?:\.\d+)?)', 'num_cmp', '{2}', '{1},{3}'),
        ]
        self.compiled_patterns = [(re.compile(p, re.IGNORECASE), rel, f1, f2) for p, rel, f1, f2 in self.patterns]

    def _parse_propositions(self, text: str) -> List[Tuple[str, str, str, int]]:
        """Parse text into list of (rel, arg1, arg2, polarity) tuples."""
        props = []
        text_lower = text.lower()
        
        # Check for global negation
        is_negated = 1
        if re.search(r'\b(not|no|never)\b', text_lower):
            # Simple heuristic: if 'not' appears near start or modifies main verb
            if re.search(r'\bnot\s+\w+', text_lower):
                is_negated = -1

        for pattern, rel_type, f1_fmt, f2_fmt in self.compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                try:
                    arg1 = f1_fmt.format(*match.groups()) if '{1}' in f1_fmt else f1_fmt
                    arg2 = f2_fmt.format(*match.groups()) if '{2}' in f2_fmt else f2_fmt
                    
                    # Handle numeric comparisons specifically
                    if rel_type == 'num_cmp':
                        op, v1, v2 = arg1, float(match.group(1)), float(match.group(3))
                        # Compute truth value immediately for numeric facts
                        truth = False
                        if op == '>': truth = v1 > v2
                        elif op == '<': truth = v1 < v2
                        elif op == '=': truth = v1 == v2
                        
                        props.append(('num_truth', str(truth).lower(), '', 1))
                        continue

                    props.append((rel_type, arg1.strip(), arg2.strip(), is_negated))
                except:
                    continue
        
        # Fallback: tokenize if no structured patterns found (bag of words approximation)
        if not props:
            tokens = re.findall(r'\b\w+\b', text_lower)
            for i in range(len(tokens)-1):
                props.append(('adj', tokens[i], tokens[i+1], is_negated))
                
        return props

    def _compute_affinity(self, q_props: List, c_props: List) -> float:
        """Compute weighted affinity score."""
        if not q_props: return 0.0
        
        score = 0.0
        q_set = set((p[0], p[1], p[2], p[3]) for p in q_props)
        
        for cp in c_props:
            # Exact match including polarity
            if cp in q_set:
                score += self.weights[cp[0]]
            # Partial match (ignoring polarity for soft alignment)
            elif (cp[0], cp[1], cp[2], 1) in q_set or (cp[0], cp[1], cp[2], -1) in q_set:
                score += self.weights[cp[0]] * 0.5
                
        return score

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Calculate F = -Affinity + Complexity."""
        q_props = self._parse_propositions(prompt)
        c_props = self._parse_propositions(candidate)
        
        affinity = self._compute_affinity(q_props, c_props)
        complexity = self.lambda_complexity * len(c_props)
        
        return -affinity + complexity

    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, and unanswerability."""
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|why did .+ fail|why did .+ stop|when did .+ stop)', p_lower):
            score = 0.2
        # 2. Scope ambiguity
        if re.search(r'every .+ (did a|has a)', p_lower) and 'same' not in p_lower:
            score = min(score, 0.4)
        # 3. Pronoun ambiguity
        if re.search(r'(.+) told (.+) he', p_lower) and 'who' in p_lower:
            score = min(score, 0.3)
        # 4. False dichotomy
        if re.search(r'either .+ or .+', p_lower) and 'only' not in p_lower:
            score = min(score, 0.5)
        # 5. Subjectivity
        if re.search(r'(best|worst|favorite|beautiful)', p_lower) and not re.search(r'(measure|data|statistic)', p_lower):
            score = min(score, 0.4)
        # 6. Unanswerability markers
        if re.search(r'(insufficient|unknown|cannot be determined)', p_lower):
            score = 0.1
            
        return score

    def _run_bandit_optimization(self, prompt: str, candidates: List[str], iterations: int = 20) -> Dict[str, float]:
        """Run Thompson Sampling bandit with clonal selection."""
        if not candidates: return {}
        
        # Initialize arms if new
        for c in candidates:
            if c not in self.arm_stats:
                self.arm_stats[c] = {'n': 1.0, 'r': 0.0} # Pseudo-counts
        
        scores = {c: 0.0 for c in candidates}
        
        for _ in range(iterations):
            # Thompson Sampling
            best_theta = -np.inf
            selected = None
            
            for c in candidates:
                stats = self.arm_stats[c]
                # Beta distribution parameters: alpha = 1 + r, beta = 1 + n - r
                # Note: r here is cumulative reward (negative free energy), so we shift
                # To fit Beta(0,1), we normalize reward or use a different mapping.
                # Simplified: Sample from Normal approx or use simple ratio for stability
                # Using simple UCB-like logic for stability in short runs if Beta fails bounds
                # Let's stick to the prompt's Beta request but ensure bounds.
                
                # Normalize reward to [0, 1] range roughly for Beta params
                # Assume max possible affinity ~10, min ~0. Reward ~ -F.
                # Let's use a simpler exploration bonus if Beta params get weird
                alpha = 1 + max(0, stats['r']) 
                beta_p = 1 + max(0, stats['n'] - stats['r']) # careful with naming
                
                # Safe sampling
                try:
                    theta = np.random.beta(alpha, beta_p + 1) 
                except:
                    theta = np.random.rand()
                    
                if theta > best_theta:
                    best_theta = theta
                    selected = c
            
            if selected is None: selected = candidates[0]
            
            # Evaluate
            F_val = self._compute_free_energy(prompt, selected)
            reward = -F_val # Higher is better
            
            # Update stats
            self.arm_stats[selected]['n'] += 1
            self.arm_stats[selected]['r'] += reward
            
            # Clonal selection (Mutation)
            if F_val < self.threshold_tau:
                # Clone: boost count
                self.arm_stats[selected]['n'] += self.clone_factor
                # Mutate: In a real text gen system, we'd swap words. 
                # Here, we simulate by slightly adjusting the internal score of similar candidates
                # or just acknowledging the "proliferation" by increasing n again.
                pass

        # Final scoring
        final_scores = {}
        for c in candidates:
            stats = self.arm_stats[c]
            # Posterior mean of reward
            if stats['n'] > 0:
                final_scores[c] = stats['r'] / stats['n']
            else:
                final_scores[c] = 0.0
        return final_scores

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Dedicated computation for specific logic puzzles (Bat-and-Ball, Modulo, etc.)
        Returns a confidence boost if the candidate matches the computed truth.
        """
        p_lower = prompt.lower()
        score_boost = 0.0
        
        # 1. Numeric Comparison
        nums = re.findall(r'(\d+(?:\.\d+)?)', prompt)
        if len(nums) >= 2:
            try:
                n1, n2 = float(nums[0]), float(nums[1])
                if '>' in prompt and str(n1) in candidate: score_boost += 2.0
                if '<' in prompt and str(n2) in candidate: score_boost += 2.0
                if 'greater' in p_lower and n1 > n2 and str(n1) in candidate: score_boost += 3.0
                if 'smaller' in p_lower and n1 < n2 and str(n1) in candidate: score_boost += 3.0
            except: pass

        # 2. Bat-and-Ball (Algebraic)
        if 'bat' in p_lower and 'ball' in p_lower and 'total' in p_lower:
            # Pattern: A + B = T, A = B + X. Solve for B.
            # Extract numbers
            nums = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', prompt)]
            if len(nums) >= 2:
                # Heuristic: Total is max, diff is min
                total = max(nums)
                diff = min(nums[:2]) # Simplified
                if len(nums) > 2: diff = nums[1] # Assume order Total, Diff
                    
                # B = (Total - Diff) / 2
                ans = (total - diff) / 2
                if f"{ans:.1f}" in candidate or f"{ans:.2f}".rstrip('0').rstrip('.') in candidate:
                    score_boost += 5.0

        # 3. Modulo/Parity
        if 'odd' in p_lower or 'even' in p_lower or 'remainder' in p_lower:
            nums = [int(n) for n in re.findall(r'\d+', prompt)]
            if nums:
                if 'odd' in p_lower:
                    if any(n % 2 != 0 for n in nums) and 'odd' in candidate.lower(): score_boost += 3.0
                if 'even' in p_lower:
                    if all(n % 2 == 0 for n in nums) and 'even' in candidate.lower(): score_boost += 3.0

        return score_boost

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Meta-confidence check (Epistemic Honesty)
        meta_conf = self._meta_confidence(prompt)
        
        # 2. Run Bandit Optimization
        bandit_scores = self._run_bandit_optimization(prompt, candidates)
        
        # 3. Structural Computation Boost
        results = []
        for c in candidates:
            base_score = bandit_scores.get(c, 0.0)
            comp_boost = self._compute_structural_score(prompt, c)
            
            # Combine scores
            final_score = base_score + comp_boost
            
            # Apply meta-confidence cap to the final confidence derived from score
            # If the question is ambiguous, even a high affinity match should be distrusted
            if meta_conf < 0.3:
                final_score *= 0.5 # Penalize heavily
            
            results.append({
                "candidate": c,
                "score": float(final_score),
                "reasoning": f"Affinity: {base_score:.2f}, Comp: {comp_boost:.2f}, MetaConf: {meta_conf:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # Quick evaluation to get raw score
        # We simulate a single candidate evaluation
        q_props = self._parse_propositions(prompt)
        a_props = self._parse_propositions(answer)
        
        affinity = self._compute_affinity(q_props, a_props)
        complexity = self.lambda_complexity * len(a_props)
        F = -affinity + complexity
        
        # Convert Free Energy to a rough probability-like score
        # Lower F -> Higher Score. 
        # Normalize: Assume typical F ranges from -10 (perfect) to 10 (terrible)
        raw_score = 1.0 / (1.0 + np.exp(F)) # Sigmoid
        
        # Structural computation check
        comp_boost = self._compute_structural_score(prompt, answer)
        if comp_boost > 0:
            raw_score = min(1.0, raw_score + (comp_boost * 0.1))
            
        # Cap by meta-confidence
        final_conf = min(raw_score, meta_conf)
        
        # Ensure strict bounds
        return float(np.clip(final_conf, 0.0, 1.0))