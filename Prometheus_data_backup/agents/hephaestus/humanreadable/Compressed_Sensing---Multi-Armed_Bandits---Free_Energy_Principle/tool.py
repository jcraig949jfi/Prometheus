import re
import numpy as np
from collections import defaultdict
import zlib

class ReasoningTool:
    """
    Combines Compressed Sensing (ISTA sparse recovery), Multi-Armed Bandits (UCB),
    and Free Energy Principle to evaluate reasoning via sparse proposition matching.
    
    Core mechanism:
    1. Parse text into binary proposition vectors (negations, comparatives, conditionals, numerics)
    2. Solve min ||Aw - b||^2 + lambda*||w||_1 via ISTA with bandit-guided coordinate selection
    3. Score = -FreeEnergy (lower prediction error + sparsity = higher score)
    """
    
    def __init__(self):
        self.lambda_sparsity = 0.1
        self.eta_step = 0.05
        self.beta_ucb = 0.5
        self.num_iterations = 50
    
    def _extract_propositions(self, text):
        """Extract structured propositions from text as binary features."""
        text_lower = text.lower()
        props = {}
        
        # Negations
        props['neg_not'] = 1 if re.search(r'\b(not|no|never|neither|none)\b', text_lower) else 0
        
        # Comparatives
        props['comp_greater'] = 1 if re.search(r'\b(greater|more|larger|higher|above|exceed)\b', text_lower) else 0
        props['comp_less'] = 1 if re.search(r'\b(less|fewer|smaller|lower|below|under)\b', text_lower) else 0
        props['comp_equal'] = 1 if re.search(r'\b(equal|same|identical)\b', text_lower) else 0
        
        # Conditionals
        props['cond_if'] = 1 if re.search(r'\bif\b', text_lower) else 0
        props['cond_then'] = 1 if re.search(r'\bthen\b', text_lower) else 0
        props['cond_unless'] = 1 if re.search(r'\bunless\b', text_lower) else 0
        
        # Causality
        props['causal'] = 1 if re.search(r'\b(because|due to|leads to|results in|causes)\b', text_lower) else 0
        
        # Temporal
        props['temp_before'] = 1 if re.search(r'\b(before|prior|earlier)\b', text_lower) else 0
        props['temp_after'] = 1 if re.search(r'\b(after|later|following)\b', text_lower) else 0
        
        # Extract numeric values
        numbers = re.findall(r'\d+\.?\d*', text)
        for i, num in enumerate(numbers[:5]):  # Cap at 5 numbers
            props[f'num_{i}'] = float(num)
        
        # Boolean indicators
        props['bool_yes'] = 1 if re.search(r'\b(yes|true|correct)\b', text_lower) else 0
        props['bool_no'] = 1 if re.search(r'\b(no|false|incorrect)\b', text_lower) else 0
        
        return props
    
    def _soft_threshold(self, x, threshold):
        """Soft thresholding operator for ISTA."""
        return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)
    
    def _ista_with_bandit(self, A, b, T):
        """ISTA with UCB-guided coordinate selection."""
        p = len(b)
        w = np.zeros(p)
        n_pulls = np.ones(p)  # Pull counts for each arm
        
        for t in range(1, T + 1):
            # Compute residual
            residual = A.T @ (A @ w - b)
            
            # UCB selection
            ucb_scores = np.abs(residual) + self.beta_ucb * np.sqrt(np.log(t + 1) / n_pulls)
            i_t = np.argmax(ucb_scores)
            
            # ISTA update for selected coordinate
            gradient = residual[i_t]
            w[i_t] = self._soft_threshold(w[i_t] - self.eta_step * gradient, 
                                          self.lambda_sparsity * self.eta_step)
            n_pulls[i_t] += 1
        
        return w
    
    def _free_energy(self, A, w, b):
        """Compute variational free energy: prediction error + complexity."""
        prediction_error = 0.5 * np.sum((A @ w - b) ** 2)
        complexity = self.lambda_sparsity * np.sum(np.abs(w))
        return prediction_error + complexity
    
    def _compute_numeric_comparison(self, prompt, candidate):
        """Parse and evaluate numeric comparisons."""
        # Extract numbers from prompt and candidate
        prompt_nums = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
        
        if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
            # Check if candidate correctly compares prompt numbers
            a, b = prompt_nums[0], prompt_nums[1]
            result = cand_nums[0] if cand_nums else None
            
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                expected = max(a, b)
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                expected = min(a, b)
            elif 'sum' in prompt.lower() or 'total' in prompt.lower():
                expected = a + b
            elif 'difference' in prompt.lower():
                expected = abs(a - b)
            else:
                return 0
            
            if result is not None and abs(result - expected) < 0.01:
                return 1.0
        
        return 0
    
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity, presupposition, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .+ fail|when did .+ stop)\b', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ a \b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', prompt_lower) and re.search(r'\bwho\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', prompt_lower) and 'neither' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', prompt_lower) and 'most' not in prompt_lower:
            return 0.25
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot determine|insufficient|not enough)\b', prompt_lower):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def _ncd(self, s1, s2):
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def evaluate(self, prompt, candidates):
        """Evaluate and rank candidates using sparse proposition matching."""
        # Extract prompt propositions as target
        prompt_props = self._extract_propositions(prompt)
        all_keys = set(prompt_props.keys())
        
        # Collect all proposition keys from candidates
        cand_props_list = []
        for cand in candidates:
            cp = self._extract_propositions(cand)
            all_keys.update(cp.keys())
            cand_props_list.append(cp)
        
        # Build unified feature space
        all_keys = sorted(all_keys)
        p = len(all_keys)
        
        # Target vector from prompt
        b = np.array([prompt_props.get(k, 0) for k in all_keys], dtype=float)
        
        # Normalize numeric features
        for i, k in enumerate(all_keys):
            if k.startswith('num_'):
                max_val = max(abs(b[i]), max(abs(cp.get(k, 0)) for cp in cand_props_list))
                if max_val > 0:
                    b[i] /= max_val
        
        results = []
        for idx, (cand, cand_props) in enumerate(zip(candidates, cand_props_list)):
            # Candidate observation vector
            x = np.array([cand_props.get(k, 0) for k in all_keys], dtype=float)
            
            # Normalize numeric features
            for i, k in enumerate(all_keys):
                if k.startswith('num_'):
                    max_val = max(abs(b[i]), abs(x[i]))
                    if max_val > 0:
                        x[i] /= max_val
            
            # Identity matrix (A = I, so Aw = w)
            A = np.eye(p)
            
            # Run ISTA with bandit
            T = max(10, int(np.sqrt(p) * 10))
            w = self._ista_with_bandit(A, x, T)
            
            # Free energy score (negate for higher = better)
            fe = self._free_energy(A, w, b)
            struct_score = -fe
            
            # Computational score
            comp_score = self._compute_numeric_comparison(prompt, cand)
            
            # NCD tiebreaker (invert so lower NCD = higher score)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: 60% structural, 25% computational, 15% NCD
            final_score = 0.6 * struct_score + 0.25 * comp_score + 0.15 * ncd_score
            
            reasoning = f"FE={fe:.3f}, struct={struct_score:.3f}, comp={comp_score:.3f}, ncd={ncd_score:.3f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1 based on meta-analysis and answer quality."""
        # Meta-confidence check (prompt properties)
        meta_conf = self._meta_confidence(prompt)
        
        # If prompt has issues, cap confidence
        if meta_conf < 0.5:
            return meta_conf
        
        # Evaluate answer against prompt
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        score = results[0]["score"]
        
        # Map score to confidence with conservative bounds
        # Never return > 0.9 unless very strong signal
        base_conf = 1.0 / (1.0 + np.exp(-score))  # Sigmoid
        base_conf = min(base_conf, 0.85)  # Cap at 0.85
        
        # Check if computational match
        comp_score = self._compute_numeric_comparison(prompt, answer)
        if comp_score > 0.9:
            base_conf = min(base_conf + 0.1, 0.9)
        
        # Final confidence = meta_conf * base_conf
        return meta_conf * base_conf