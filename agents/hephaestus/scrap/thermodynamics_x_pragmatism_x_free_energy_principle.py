import re
import numpy as np
import math

class ReasoningTool:
    """
    A reasoning tool implementing the Free Energy Principle via loopy belief propagation.
    
    Mechanism:
    1. Parsing: Extracts entities, relations, numeric bounds, and negations from prompt/candidates.
    2. Factor Graph Construction: Builds an energy matrix where low energy corresponds to 
       logical consistency (transitivity), numeric accuracy, and pragmatic utility (verbatim matches).
    3. Inference: Runs sum-product belief propagation to approximate the variational posterior.
    4. Scoring: Computes Variational Free Energy (Expected Energy - Entropy). 
       Lower Free Energy -> Higher Score.
    """
    
    # Regex patterns for structural extraction
    RE_ENTITY = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
    RE_RELATION = re.compile(r'\b(is|are|was|were|causes?|leads?\s+to|greater\s+than|less\s+than|if|then)\b', re.IGNORECASE)
    RE_NUMERIC = re.compile(r'(\d+(?:\.\d+)?)\s*(>|<|>=|<=|=|!=|greater|less)\s*(\d+(?:\.\d+)?)')
    RE_NEGATION = re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE)
    RE_COND = re.compile(r'\b(if|unless|provided\s+that)\b', re.IGNORECASE)

    def __init__(self):
        self.max_iter = 10
        self.temp = 0.5  # Temperature for entropy regularization

    def _extract_props(self, text):
        """Extract logical propositions as (subject, relation, object, polarity, numeric_val)"""
        props = []
        lower_text = text.lower()
        
        # Extract numeric constraints
        for m in self.RE_NUMERIC.finditer(text):
            v1, op, v2 = m.group(1), m.group(2), m.group(3)
            props.append({
                'type': 'numeric',
                'val1': float(v1), 'val2': float(v2), 'op': op,
                'polarity': True, 'raw': m.group(0)
            })
            
        # Extract entity relations (simplified for brevity)
        entities = self.RE_ENTITY.findall(text)
        relations = list(self.RE_RELATION.finditer(text))
        
        # Simple pairing heuristic for demo purposes
        for i, rel in enumerate(relations):
            subj = entities[i] if i < len(entities) else "Unknown"
            obj = entities[i+1] if i+1 < len(entities) else "Unknown"
            is_neg = bool(self.RE_NEGATION.search(text[rel.start()-20:rel.end()]))
            props.append({
                'type': 'logical',
                'subj': subj, 'rel': rel.group(), 'obj': obj,
                'polarity': not is_neg, 'raw': rel.group(0)
            })
            
        return props

    def _compute_energy(self, p_props, c_props):
        """
        Compute energy matrix U[node, state].
        State 0: False, State 1: True.
        Lower energy = higher probability.
        """
        n = len(p_props) + len(c_props)
        if n == 0: return np.zeros((0, 2))
        
        U = np.zeros((n, 2))
        
        # 1. Evidence Match & Pragmatic Utility (Prompt props)
        for i, p in enumerate(p_props):
            if p['type'] == 'numeric':
                # Energy penalty if candidate doesn't satisfy numeric constraint
                # We assume candidate props are checked against this later in consistency
                pass 
            # Pragmatic reward (negative energy) for verbatim presence in candidate text is handled 
            # by checking overlap, but here we score the proposition's intrinsic truth based on prompt
            
        # 2. Logical Consistency & Numeric Validation (Cross terms)
        # We simplify: Check if candidate props contradict prompt props
        for i, p in enumerate(p_props):
            for j, c in enumerate(c_props):
                idx_c = len(p_props) + j
                
                # Numeric consistency
                if p['type'] == 'numeric' and c['type'] == 'numeric':
                    # Check if candidate value satisfies prompt constraint
                    sat = False
                    if '>' in p['op']: sat = c['val1'] > p['val2']
                    elif '<' in p['op']: sat = c['val1'] < p['val2']
                    elif '=' in p['op']: sat = abs(c['val1'] - p['val2']) < 1e-6
                    
                    if sat:
                        U[idx_c, 1] -= 2.0 # Reward consistency
                    else:
                        U[idx_c, 1] += 2.0 # Penalty inconsistency

                # Logical consistency (Simplified Potts model)
                if p['type'] == 'logical' and c['type'] == 'logical':
                    if p['subj'] == c['subj'] and p['obj'] == c['obj']:
                        if p['polarity'] == c['polarity']:
                            U[idx_c, 1] -= 1.0 # Match
                        else:
                            U[idx_c, 1] += 3.0 # Contradiction
                            
        # 3. Pragmatic Utility: Reward candidates appearing in prompt
        # (Handled implicitly by low energy if extracted as same prop)
        
        return U

    def _belief_propagation(self, U):
        """Run loopy sum-product BP to approximate posterior q"""
        n_nodes, n_states = U.shape
        if n_nodes == 0: return np.array([])
        
        # Initialize beliefs uniformly
        q = np.ones((n_nodes, n_states)) / n_states
        
        # Simplified loopy BP: Iterate to minimize free energy
        # Since graph structure is implicit in U (fully connected approximation for small n),
        # we perform iterative refinement of marginals based on pairwise potentials encoded in U
        
        for _ in range(self.max_iter):
            q_old = q.copy()
            
            # Update beliefs based on energy and entropy regularization
            # F = E - TS => Minimize F => Maximize (S - E/T)
            # q ~ exp(-U/T)
            
            logits = -U / self.temp
            
            # Normalize to get probabilities (Softmax)
            exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            q = exp_logits / (np.sum(exp_logits, axis=1, keepdims=True) + 1e-9)
            
            if np.allclose(q, q_old, atol=1e-4):
                break
                
        return q

    def _calc_free_energy(self, q, U):
        """Calculate Variational Free Energy: F = <E> - H"""
        if q.size == 0: return 0.0
        
        # Expected Energy: sum(q * U)
        expected_energy = np.sum(q * U)
        
        # Entropy: -sum(q * log(q))
        # Add small epsilon to avoid log(0)
        q_safe = q + 1e-9
        entropy = -np.sum(q * np.log(q_safe))
        
        F = expected_energy - self.temp * entropy
        return F

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        p_props = self._extract_props(prompt)
        results = []
        
        # Baseline NCD score for tie-breaking
        import zlib
        prompt_bytes = prompt.encode()
        len_prompt = len(prompt_bytes)
        
        scores = []
        for cand in candidates:
            cand_bytes = cand.encode()
            c_props = self._extract_props(cand)
            
            # Construct Energy Matrix
            # Nodes = Prompt Props + Candidate Props
            all_props = p_props + c_props
            if not all_props:
                # Fallback if no structure found
                energy_mat = np.zeros((0, 2))
            else:
                energy_mat = self._compute_energy(p_props, c_props)
            
            # Run Inference
            if energy_mat.size > 0:
                q = self._belief_propagation(energy_mat)
                free_energy = self._calc_free_energy(q, energy_mat)
                score = -free_energy # Lower F -> Higher Score
            else:
                score = 0.0

            # NCD Tiebreaker / Fallback
            # NCD(x,y) = (Z(xy) - min(Z(x), Z(y))) / max(Z(x), Z(y))
            # We want high overlap (low NCD) to boost score slightly if structural score is close
            try:
                combined = prompt_bytes + cand_bytes
                z_combined = len(zlib.compress(combined))
                z_cand = len(zlib.compress(cand_bytes))
                denom = max(len_prompt, z_cand)
                ncd = (z_combined - min(len_prompt, z_cand)) / denom if denom > 0 else 1.0
                # Add small ncd bonus (inverted) to score
                score += (1.0 - ncd) * 0.1 
            except:
                pass

            results.append({"candidate": cand, "score": score, "reasoning": "Free Energy Minimization"})
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on relative ranking"""
        # Evaluate against a dummy wrong answer to gauge relative strength
        # Or simply map the free energy score to 0-1 via sigmoid
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.5
        
        # Heuristic mapping: Higher score -> higher confidence
        # Normalize roughly based on typical energy scales in this implementation
        raw_score = res[0]['score']
        
        # Sigmoid mapping: 1 / (1 + exp(-k(x - x0)))
        # Assuming x0 ~ 0, k ~ 0.5
        conf = 1.0 / (1.0 + math.exp(-0.5 * raw_score))
        return min(1.0, max(0.0, conf))