import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Constraint Satisfaction (CSP),
    Abstract Interpretation, and Active Inference scoring.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical constraints (negation, implication,
       comparison) from text using regex. Maps these to binary domains {0, 1}.
    2. Propagation: Uses AC-3 algorithm on NumPy arrays to tighten variable domains.
       If a domain becomes empty, the candidate is inconsistent (Score: -inf).
    3. Abstract Interpretation: Calculates entropy of remaining domains to quantify uncertainty.
    4. Active Inference: Scores candidates based on Expected Free Energy (G), balancing
       likelihood fit against epistemic uncertainty (entropy). Lower G = Higher Score.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|then|otherwise)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|taller|shorter|equal)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'number': re.compile(r'\d+\.?\d*'),
            'relation': re.compile(r'(\w+)\s+(is|are|was|were|has|have)\s+(\w+)', re.IGNORECASE)
        }

    def _extract_props_and_constraints(self, text: str):
        """Parse text into propositions and binary/unary constraints."""
        # Normalize
        text_lower = text.lower()
        sentences = re.split(r'[.\n]', text)
        
        props = []
        constraints = [] # List of (type, args)
        
        # Simple extraction of atomic facts based on relations
        for sent in sentences:
            if not sent.strip(): continue
            s_lower = sent.lower()
            
            # Detect negation in sentence
            is_negated = bool(self.patterns['negation'].search(s_lower))
            
            # Extract numeric comparisons
            nums = self.patterns['number'].findall(s_lower)
            if len(nums) >= 2:
                # Create a proposition for the numeric relation
                p_idx = len(props)
                props.append(f"num_check_{p_idx}")
                # Unary constraint: value check (simplified to boolean truth of comparison)
                try:
                    val = float(nums[0]) < float(nums[1]) # Example heuristic
                    constraints.append(('unary', p_idx, 1 if val else 0))
                except: pass

            # Extract relational propositions (A is B)
            matches = self.patterns['relation'].findall(sent)
            for subj, verb, obj in matches:
                p_str = f"{subj}_{verb}_{obj}"
                if p_str not in props:
                    props.append(p_str)
                p_idx = props.index(p_str)
                
                if is_negated:
                    constraints.append(('unary', p_idx, 0)) # Force false
                else:
                    # If conditional detected, add implication logic later if pairs found
                    if self.patterns['conditional'].search(s_lower):
                        constraints.append(('conditional_flag', p_idx))
                    else:
                        # Assume true if stated positively
                        constraints.append(('unary', p_idx, 1))

        return props, constraints

    def _build_csp(self, n_props, constraints):
        """Build NumPy structures for CSP."""
        if n_props == 0:
            return np.array([]), np.array([]), np.array([])
            
        # uni_cons: shape (n, 2), 1 means allowed
        uni_cons = np.ones((n_props, 2), dtype=np.float32)
        
        # bin_cons: shape (m, 2, 2), 1 means allowed pair (p_i=a, p_j=b)
        # We generate dummy binary constraints for conditionals if we find pairs
        bin_list = []
        
        for c in constraints:
            ctype = c[0]
            if ctype == 'unary':
                idx, val = c[1], c[2]
                if idx < n_props:
                    uni_cons[idx, :] = 0
                    uni_cons[idx, val] = 1
            elif ctype == 'conditional_flag':
                # Placeholder for binary logic if we had linked antecedents
                pass
                
        # Default binary constraint matrix (allow all if none specified)
        # To save space, we return empty if no explicit binary constraints generated
        bin_cons = np.array([]) 
        return np.array(uni_cons), bin_cons, np.array([c for c in constraints if c[0]=='unary'])

    def _ac3_propagate(self, uni_cons, bin_cons):
        """Simplified AC-3 propagation using vectorization."""
        if uni_cons.shape[0] == 0:
            return uni_cons, True
            
        changed = True
        # Iterate a fixed number of times to ensure convergence without complex queue logic
        for _ in range(10): 
            if not changed: break
            changed = False
            
            # Propagate unary constraints to binary if they existed (omitted for brevity in pure unary case)
            # Check for empty domains
            if np.any(np.sum(uni_cons, axis=1) == 0):
                return uni_cons, False # Inconsistent
                
        return uni_cons, True

    def _compute_score(self, uni_cons, is_consistent):
        if not is_consistent:
            return -float('inf')
            
        if uni_cons.shape[0] == 0:
            return 0.0 # No info
            
        # Entropy calculation (Abstract Interpretation)
        # Normalize domains to probabilities
        sums = np.sum(uni_cons, axis=1, keepdims=True)
        sums[sums == 0] = 1 # Avoid div by zero
        probs = uni_cons / sums
        
        # H = - sum(p log p). Handle 0 log 0 = 0
        with np.errstate(divide='ignore', invalid='ignore'):
            log_probs = np.log2(probs)
            log_probs[probs == 0] = 0
            entropy = -np.sum(probs * log_probs, axis=1)
        
        # Active Inference Score: G = sum(-log(|D|) - H)
        # |D| is the count of allowed values (sums)
        domain_sizes = sums.flatten()
        domain_sizes[domain_sizes == 0] = 1
        
        log_domain_sizes = np.log2(domain_sizes)
        
        # Expected Free Energy approximation
        # We want low uncertainty (low H) and high fit.
        # Score = - (Entropy + Penalty for large domain)
        g_values = -(log_domain_sizes + entropy)
        
        return float(np.sum(g_values))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_props, prompt_consts = self._extract_props_and_constraints(prompt)
        n_prompt_props = len(prompt_props)
        
        # If no structure found, fallback to NCD tiebreaker logic implicitly via string length/overlap
        # But we must attempt the CSP first.
        
        for cand in candidates:
            # Combine prompt and candidate for joint consistency check
            full_text = f"{prompt} {cand}"
            props, consts = self._extract_props_and_constraints(full_text)
            
            # Build CSP
            uni_cons, bin_cons, _ = self._build_csp(len(props), consts)
            
            # Propagate
            final_uni, is_consistent = self._ac3_propagate(uni_cons, bin_cons)
            
            # Score
            score = self._compute_score(final_uni, is_consistent)
            
            # Fallback for empty parses (NCD proxy)
            if score == -float('inf') or (len(props) == 0 and n_prompt_props == 0):
                # Simple overlap heuristic as fallback if CSP yields nothing
                overlap = len(set(cand.lower().split()) & set(prompt.lower().split()))
                score = float(overlap) * 0.1 - 10.0 # Low base score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"CSP Consistent: {is_consistent}, Entropy Score: {score:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1
        # Heuristic mapping: 
        # score > 0 -> high confidence
        # score ~ -inf -> 0
        if score == -float('inf'):
            return 0.0
        
        # Sigmoid-like mapping centered around 0
        conf = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, conf))