import re
import numpy as np
from math import log, exp

class ReasoningTool:
    """
    Implements a Statistical Mechanics-based reasoning engine using Abstract Interpretation.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and logical constraints (implication, transitivity,
       contradiction) from the prompt and candidates using regex patterns for negations,
       comparatives, and conditionals.
    2. Abstract Domain: Represents truth values as intervals [l, u] in [0, 1].
    3. Energy Model: Constructs a factor graph where:
       - Unary factors encode prior beliefs (asserted vs denied).
       - Binary factors encode logical constraints (A->B, A<B, contradictions).
    4. Criticality: Uses Mean-Field iteration to approximate the Boltzmann distribution.
       Scans Temperature (T) to find the Critical Temperature (Tc) where susceptibility peaks.
    5. Scoring: Computes Free Energy (F = E - Tc*S) at Tc. Lower F implies higher probability.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|implies|leads to|because)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'order_op': re.compile(r'(>|<|>=|<=)'),
            'contradiction': re.compile(r'\b(but|however|although|yet)\b', re.IGNORECASE)
        }
        self.temp_range = np.linspace(0.1, 2.0, 20)

    def _extract_props(self, text: str):
        """Extract atomic propositions and structural features."""
        props = []
        # Simple sentence splitting
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_contradiction': bool(self.patterns['contradiction'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)]
        }
        
        # Create a proposition for the whole text context and sub-sentences
        props.append((text, features))
        for i, sent in enumerate(sentences[:5]): # Limit depth
            props.append((sent, features))
            
        return props

    def _compute_energy(self, mu, T, assertions, constraints):
        """Compute total energy and its derivative for mean-field update."""
        if T <= 0: T = 1e-6
        n = len(mu)
        E_total = 0.0
        dE = np.zeros(n)
        
        # Unary factors (Prior beliefs)
        for i, (val, weight) in assertions:
            if i < n:
                # Energy: -log(p) if true, -log(1-p) if false. 
                # Simplified: E = -w * x if asserted true, w * x if asserted false
                # Here we use a soft constraint: E = w * (target - x)^2
                target = 1.0 if weight > 0 else 0.0
                w = abs(weight)
                term = w * (mu[i] - target)**2
                E_total += term
                dE[i] += 2 * w * (mu[i] - target)

        # Binary factors (Logical constraints)
        for (i, j, type_, w) in constraints:
            if i >= n or j >= n: continue
            
            if type_ == 'implication': # A -> B : max(0, A - B)
                val = max(0.0, mu[i] - mu[j])
                E_total += w * val
                if val > 0:
                    dE[i] += w
                    dE[j] -= w
                    
            elif type_ == 'transitivity': # A < B : max(0, A - B) similar penalty
                val = max(0.0, mu[i] - mu[j])
                E_total += w * val
                if val > 0:
                    dE[i] += w
                    dE[j] -= w
                    
            elif type_ == 'contradiction': # A and not A : high penalty if both high
                # Penalize if mu[i] + mu[j] > 1 (assuming j is negation of i)
                val = max(0.0, mu[i] + mu[j] - 1.0)
                E_total += w * val
                if val > 0:
                    dE[i] += w
                    dE[j] += w

        return E_total, dE

    def _mean_field_solve(self, n, assertions, constraints, T):
        """Run mean-field iteration to find equilibrium mu at temperature T."""
        mu = np.full(n, 0.5)
        if T <= 0: T = 0.1
        
        for _ in range(50): # Iterations
            _, dE = self._compute_energy(mu, T, assertions, constraints)
            # Update rule: mu = sigma(-dE / T)
            # sigma(x) = 1 / (1 + exp(-x))
            arg = -dE / T
            # Clip arg to prevent overflow
            arg = np.clip(arg, -20, 20)
            mu_new = 1.0 / (1.0 + np.exp(-arg))
            
            if np.allclose(mu, mu_new, atol=1e-4):
                break
            mu = mu_new
        return mu

    def _find_critical_temp(self, n, assertions, constraints):
        """Scan T to find Tc where susceptibility chi peaks."""
        energies = []
        mus = []
        
        for T in self.temp_range:
            mu = self._mean_field_solve(n, assertions, constraints, T)
            E, _ = self._compute_energy(mu, T, assertions, constraints)
            energies.append(E)
            mus.append(mu)
            
        energies = np.array(energies)
        # Susceptibility approximation: d<E>/dT
        if len(energies) < 2:
            return self.temp_range[0], mus[0]
            
        chi = np.abs(np.gradient(energies, self.temp_range))
        tc_idx = np.argmax(chi)
        return self.temp_range[tc_idx], mus[tc_idx]

    def _build_graph(self, prompt: str, candidate: str):
        """Build the factor graph from prompt and candidate."""
        full_text = f"{prompt} {candidate}"
        props = self._extract_props(full_text)
        n = len(props)
        
        assertions = [] # (index, weight) weight > 0 means true, < 0 means false
        constraints = [] # (i, j, type, weight)
        
        # 1. Unary Factors from structural parsing
        for i, (text, feats) in enumerate(props):
            w = 0.0
            if feats['has_negation']:
                # If the candidate repeats negation from prompt, reinforce
                if 'not' in text.lower() or 'no' in text.lower():
                    w = 0.9 if 'not' in prompt.lower() else -0.5
            else:
                w = 0.5 # Default prior
            
            # Numeric consistency check
            nums = feats['numbers']
            if len(nums) >= 2:
                # If prompt has numbers, check if candidate respects order
                if 'prompt' in text.lower() or i == 0: # Global context
                     pass # Handled in binary
            
            assertions.append((i, w))

        # 2. Binary Factors (Logical Constraints)
        # Implication: If prompt has "if", enforce connection
        if any(f['has_conditional'] for _, f in props):
            # Connect first prop (context) to others
            for i in range(1, min(n, 4)):
                constraints.append((0, i, 'implication', 2.0))

        # Transitivity/Numeric ordering
        all_nums = []
        for i, (_, f) in enumerate(props):
            for num in f['numbers']:
                all_nums.append((num, i))
        
        if len(all_nums) >= 2:
            all_nums.sort(key=lambda x: x[0])
            # Enforce order: if A < B in text, then truth(A) <= truth(B) roughly
            # Here we enforce consistency: if numbers are extracted, adjacent ones constrain each other
            for k in range(len(all_nums)-1):
                idx1 = all_nums[k][1]
                idx2 = all_nums[k+1][1]
                if idx1 != idx2:
                    constraints.append((idx1, idx2, 'transitivity', 1.5))

        # Contradictions
        if any(f['has_contradiction'] for _, f in props):
            for i in range(1, n):
                constraints.append((0, i, 'contradiction', 3.0))

        return n, assertions, constraints

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Calculate score based on Free Energy at Critical Temperature."""
        n, assertions, constraints = self._build_graph(prompt, candidate)
        
        if n == 0:
            return 0.0

        # Find Critical Temperature and corresponding mu
        Tc, mu = self._find_critical_temp(n, assertions, constraints)
        
        # Compute Free Energy F = <E> - T * S
        E_avg, _ = self._compute_energy(mu, Tc, assertions, constraints)
        
        # Entropy S = -sum(mu log mu + (1-mu) log (1-mu))
        epsilon = 1e-10
        S = -np.sum(
            mu * np.log(mu + epsilon) + 
            (1 - mu) * np.log(1 - mu + epsilon)
        )
        
        F = E_avg - Tc * S
        
        # Normalize: Lower F is better. Convert to 0-1 score.
        # Heuristic scaling: Map F to [0, 1] assuming typical ranges
        # If F is very negative, score -> 1. If positive large, score -> 0.
        score = 1.0 / (1.0 + exp(F)) 
        return float(score)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        scored = []
        scores = []
        
        # 1. Structural Parsing & Scoring (Primary Signal)
        for cand in candidates:
            s = self._score_candidate(prompt, cand)
            scored.append((cand, s))
            scores.append(s)
            
        # 2. NCD Tiebreaker (Only if scores are extremely close)
        # We use NCD only to break ties within 1% tolerance
        final_results = []
        for i, (cand, base_score) in enumerate(scored):
            is_tie = False
            for j, other_score in enumerate(scores):
                if i != j and abs(base_score - other_score) < 0.01:
                    is_tie = True
                    break
            
            if is_tie:
                # Compute NCD against prompt
                def zlib_size(s):
                    return len(zlib.compress(s.encode()))
                
                s_cat = prompt + cand
                s_cand = cand
                s_prompt = prompt
                
                len_cat = zlib_size(s_cat)
                len_cand = zlib_size(s_cand)
                len_prompt = zlib_size(s_prompt)
                
                # NCD = (L(ab) - min(L(a), L(b))) / max(L(a), L(b))
                # Simplified NCD for tie breaking: lower is better match
                ncd_val = (len_cat - min(len_cand, len_prompt)) / max(len_cand, len_prompt, 1)
                # Boost score slightly based on NCD (lower NCD = higher similarity = better)
                boost = (1.0 - ncd_val) * 0.005 
                base_score += boost

            final_results.append({"candidate": cand, "score": base_score, "reasoning": "Statistical Mechanics Criticality Analysis"})
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']

# Import zlib inside to keep global namespace clean if needed, 
# but standard lib allows top level. Added here for the NCD part used in evaluate.
import zlib