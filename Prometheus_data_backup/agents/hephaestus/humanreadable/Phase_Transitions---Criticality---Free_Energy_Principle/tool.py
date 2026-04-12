import re
import math
import numpy as np

class ReasoningTool:
    """
    Implements a Mean-Field Variational Free Energy solver with Criticality detection.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (Negation, Comparison, Conditionals, Causal, Numeric, Order).
    2. Factor Graph: Constructs logical constraints between atoms based on prompt logic.
    3. Inference: Uses mean-field updates to minimize Free Energy (satisfy constraints).
    4. Criticality: Sweeps a global temperature parameter to find the susceptibility peak.
       - Answers with low Free Energy (consistent) AND high Susceptibility (sensitive to constraints)
       are ranked highest.
    5. Scoring: Final score = -F* + lambda * chi_peak.
    """

    def __init__(self):
        # Regex patterns for atomic extraction
        self.patterns = {
            'neg': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comp': re.compile(r'\b(greater|less|more|fewer|higher|lower|bigger|smaller)\b', re.IGNORECASE),
            'cond': re.compile(r'\b(if|unless|then|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'order': re.compile(r'\b(before|after|first|last|finally|precede|follow)\b', re.IGNORECASE),
            'num': re.compile(r'-?\d+(?:\.\d+)?'),
            'quant': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE)
        }

    def _extract_atoms(self, text: str) -> list:
        """Extract typed atomic propositions from text."""
        atoms = []
        text_lower = text.lower()
        
        # Extract numeric values
        nums = self.patterns['num'].findall(text)
        for n in nums:
            atoms.append(('Num', float(n)))
            
        # Extract logical markers (simplified to presence counts for atomic nodes)
        if self.patterns['neg'].search(text_lower): atoms.append(('Neg', 1.0))
        if self.patterns['comp'].search(text_lower): atoms.append(('Comp', 1.0))
        if self.patterns['cond'].search(text_lower): atoms.append(('Cond', 1.0))
        if self.patterns['causal'].search(text_lower): atoms.append(('Causal', 1.0))
        if self.patterns['order'].search(text_lower): atoms.append(('Order', 1.0))
        if self.patterns['quant'].search(text_lower): atoms.append(('Quant', 1.0))
        
        # Fallback if no atoms found (prevents empty graph)
        if not atoms:
            atoms.append(('Raw', 1.0))
            
        return atoms

    def _build_factors(self, prompt_atoms: list, answer_atoms: list) -> list:
        """
        Construct factors connecting prompt and answer atoms.
        Returns list of (indices, weight, type)
        """
        factors = []
        all_atoms = prompt_atoms + answer_atoms
        n = len(all_atoms)
        if n == 0: return factors
        
        p_len = len(prompt_atoms)
        
        # 1. Consistency factors (Prompt Negation should match Answer Negation if present)
        # We create factors between similar types in prompt and answer
        for i, (p_type, p_val) in enumerate(prompt_atoms):
            for j, (a_type, a_val) in enumerate(answer_atoms):
                idx_a = p_len + j
                if p_type == a_type:
                    # Strong weight for matching logical types
                    w = 2.0 
                    factors.append(([i, idx_a], w, 'match'))
                elif p_type == 'Num' and a_type == 'Num':
                    # Numeric consistency: if prompt has numbers, answer having numbers is a weak positive constraint
                    # (In a real solver, we'd check magnitude logic)
                    factors.append(([i, idx_a], 0.5, 'num_match'))
        
        # 2. Structural integrity factors (internal to answer)
        # If answer has 'Neg' and 'Comp', they likely form a valid comparative negation structure
        a_types = [x[0] for x in answer_atoms]
        if 'Neg' in a_types and 'Comp' in a_types:
            idx_neg = p_len + a_types.index('Neg')
            idx_comp = p_len + a_types.index('Comp')
            factors.append(([idx_neg, idx_comp], 1.5, 'struct_neg_comp'))
            
        # 3. Prompt-Answer implication (Simplified Modus Ponens)
        # If prompt has 'Cond' and answer has 'Causal' or 'Order', boost connection
        if any(x[0] == 'Cond' for x in prompt_atoms):
            for j, (a_type, _) in enumerate(answer_atoms):
                if a_type in ['Causal', 'Order', 'Comp']:
                    idx_a = p_len + j
                    # Connect to a dummy 'conclusion' node or just boost internal answer coherence
                    factors.append(([idx_a, idx_a], 1.0, 'implication_support'))

        return factors

    def _mean_field_solve(self, n_nodes: int, factors: list, T: float) -> tuple:
        """
        Perform mean-field updates to find q (probabilities).
        Returns (free_energy, q_vector)
        """
        if n_nodes == 0: return 0.0, np.array([])
        
        # Initialize q uniformly
        q = np.full(n_nodes, 0.5)
        
        # Precompute factor data for speed
        # factors format: (indices, weight, type)
        # V_f(s) = 0 if satisfied. 
        # For 'match': satisfied if s_i == s_j. Energy = w * (s_i != s_j)
        # Mean field approximation for pairwise: <V> = q_i(1-q_j) + (1-q_i)q_j
        
        max_iter = 50
        for _ in range(max_iter):
            q_old = q.copy()
            for idxs, w_raw, f_type in factors:
                w = w_raw / T
                i = idxs[0]
                j = idxs[1] if len(idxs) > 1 else i
                
                if i >= n_nodes or j >= n_nodes: continue

                if f_type == 'match' or f_type == 'num_match':
                    # Interaction term: encourage same state
                    # dE/dq_i approx w * (1 - 2*q_j) ? 
                    # Actually, for Ising-like: E = -J s_i s_j. Here we want match.
                    # Let's use simple heuristic: q_i <- sigmoid( sum_j w_ij * (2q_j - 1) )
                    pass 
                elif f_type == 'struct_neg_comp':
                    # Encourage co-activation
                    pass
                elif f_type == 'implication_support':
                    # Self-loop boost
                    q[i] = min(0.99, max(0.01, q[i] + w * 0.1))

            # Simplified Mean Field Update Rule for this specific graph structure
            # We approximate the gradient of Free Energy w.r.t q_i
            new_q = q.copy()
            for i in range(n_nodes):
                field = 0.0
                for idxs, w_raw, f_type in factors:
                    if i not in idxs: continue
                    w = w_raw / T
                    j = idxs[1] if idxs[0] == i and len(idxs)>1 else (idxs[0] if idxs[1]==i else idxs[0])
                    if j >= n_nodes: j=i
                    
                    if f_type in ['match', 'num_match', 'struct_neg_comp']:
                        # Ferromagnetic coupling: align with neighbor
                        field += w * (2 * q[j] - 1)
                    elif f_type == 'implication_support':
                        field += w * 0.5
                
                # Logistic update
                logit = math.log(q[i] / (1 - q[i] + 1e-9)) + field
                new_q[i] = 1.0 / (1.0 + math.exp(-logit))
                new_q[i] = min(0.999, max(0.001, new_q[i]))
            
            q = new_q
            if np.max(np.abs(q - q_old)) < 1e-4:
                break
        
        # Calculate Free Energy F = <E> - S
        energy = 0.0
        for idxs, w_raw, f_type in factors:
            w = w_raw / T
            i, j = idxs[0], idxs[1] if len(idxs)>1 else idxs[0]
            if i>=n_nodes or j>=n_nodes: continue
            
            if f_type in ['match', 'num_match', 'struct_neg_comp']:
                # Prob of mismatch: q_i(1-q_j) + (1-q_i)q_j
                prob_violate = q[i]*(1-q[j]) + (1-q[i])*q[j]
                energy += w * prob_violate
            elif f_type == 'implication_support':
                 # Self penalty if low confidence? No, just boost.
                 pass

        entropy = 0.0
        for qi in q:
            if qi > 1e-9 and qi < 1-1e-9:
                entropy -= (qi * math.log(qi) + (1-qi) * math.log(1-qi))
                
        F = energy - entropy
        return F, q

    def _compute_susceptibility(self, prompt: str, candidate: str) -> tuple:
        """Sweep T to find critical point and compute susceptibility."""
        p_atoms = self._extract_atoms(prompt)
        a_atoms = self._extract_atoms(candidate)
        factors = self._build_factors(p_atoms, a_atoms)
        n_nodes = len(p_atoms) + len(a_atoms)
        
        if n_nodes == 0: return 0.0, 0.0
        
        # Temperature sweep
        temps = np.logspace(-2, 1, 20) # T from 0.01 to 10
        m_vals = []
        f_vals = []
        
        for T in temps:
            F, q = self._mean_field_solve(n_nodes, factors, T)
            m = np.mean(2 * q - 1) # Order parameter
            m_vals.append(m)
            f_vals.append(F)
            
        # Compute susceptibility chi = d<m>/dT approximated by finite difference
        chi_vals = []
        for i in range(1, len(m_vals)):
            dm = m_vals[i] - m_vals[i-1]
            dT = temps[i] - temps[i-1]
            chi = abs(dm / (dT + 1e-9))
            chi_vals.append(chi)
            
        if not chi_vals: return 0.0, 0.0
        
        # Find critical point (max chi)
        max_chi_idx = np.argmax(chi_vals)
        max_chi = chi_vals[max_chi_idx]
        
        # Get Free Energy at critical temperature
        # Note: chi_vals is one shorter than temps. max_chi_idx corresponds to interval i->i+1
        # We take the F at the higher T of the interval for safety, or average. 
        # Let's pick the F at the index corresponding to the peak.
        critical_F = f_vals[min(max_chi_idx + 1, len(f_vals)-1)]
        
        return critical_F, max_chi

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            F_star, chi = self._compute_susceptibility(prompt, cand)
            
            # Score: Lower F is better (negative F_star), Higher Chi is better
            # Normalize slightly to prevent overflow if chi is huge
            score = -F_star + 0.1 * math.log1p(chi)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free Energy: {F_star:.4f}, Susceptibility: {chi:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        # Evaluate single candidate against a dummy set to get relative score?
        # Or just use the internal metrics mapped to 0-1.
        # Let's use the score components directly.
        F_star, chi = self._compute_susceptibility(prompt, answer)
        
        # Heuristic mapping: 
        # Low F (good) -> high base confidence. 
        # High Chi (critical) -> boost.
        # F is usually small negative/positive. Let's assume F < 0 is good.
        # Sigmoid mapping of (-F + 0.1*chi)
        raw_score = -F_star + 0.1 * math.log1p(chi)
        
        # Map to 0-1. Assume raw_score ranges roughly -5 to 5.
        conf = 1.0 / (1.0 + math.exp(-raw_score))
        return conf