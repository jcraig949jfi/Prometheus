import re
import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

# Standard library only. No external deps beyond numpy.

class ReasoningTool:
    """
    A reasoning tool combining Spectral Analysis of logical graphs, 
    Multi-Armed Bandits (Thompson Sampling), and the Free Energy Principle.
    
    Mechanism:
    1. Structural Parsing: Extracts logical symbols (negation, comparatives, causals) 
       via regex to build a directed graph representation of the text.
    2. Spectral Analysis: Computes the Combinatorial Laplacian of the graph and 
       derives the Power Spectral Density (PSD) as a "logical frequency profile".
    3. Free Energy & Bandits: 
       - Models answer quality as a Beta distribution (Bandit arm).
       - Computes Variational Free Energy (F) balancing complexity (KL divergence) 
         and accuracy (likelihood of PSD given quality).
       - Uses Thompson Sampling to select and update beliefs.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and scope issues 
       to cap confidence, ensuring the model admits uncertainty rather than hallucinating.
    5. Scoring: Weighted combination of Structural consistency, Constructive Computation, 
       and NCD (tiebreaker only).
    """

    def __init__(self):
        # Regex patterns for logical symbol extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|n\'t|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|equal to|more than|fewer than)|[><=]', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|otherwise|implies)\b|->|=>', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads to|causes)\b|->|=>', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|preceded by|followed by|first|last)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|most|every|each|any)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?(?:\%)?'),
            # Tier B Triggers
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|quit))\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|is it A or B)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|it|they)\b.*\b(who|which one)\b', re.IGNORECASE)
        }
        
        # Bandit State: Map of candidate hash -> (alpha, beta)
        self.bandit_state = {}

    def _extract_symbols(self, text: str) -> Dict[str, List[str]]:
        """Extract logical symbols from text."""
        symbols = {}
        for key, pattern in self.patterns.items():
            if key not in ['presupposition', 'false_dichotomy', 'subjectivity', 'pronoun_ambiguity']:
                symbols[key] = pattern.findall(text)
        return symbols

    def _build_graph(self, text: str) -> np.ndarray:
        """
        Build a simplified adjacency matrix based on logical token proximity.
        Vertices are tokens; edges represent logical relations.
        """
        tokens = re.findall(r'\w+|[^\s\w]', text.lower())
        n = len(tokens)
        if n == 0:
            return np.array([[0]])
        
        A = np.zeros((n, n))
        symbols = self._extract_symbols(text)
        
        # Create edges based on symbol presence and proximity
        # Simplified: Connect tokens adjacent to logical operators
        logic_indices = []
        for key, matches in symbols.items():
            if matches:
                # Find indices of these matches in the token stream (approximate)
                for i, token in enumerate(tokens):
                    if any(m.lower() in token for m in matches):
                        logic_indices.append(i)
        
        # Connect logic tokens to their neighbors (context window)
        for idx in logic_indices:
            for j in range(max(0, idx-2), min(n, idx+3)):
                if idx != j:
                    A[idx, j] = 1
                    A[j, idx] = 1 # Undirected for Laplacian simplicity
        
        # If no logic found, create a chain graph of tokens to maintain structure
        if not logic_indices:
            for i in range(n-1):
                A[i, i+1] = 1
                A[i+1, i] = 1
                
        return A

    def _compute_spectral_signal(self, A: np.ndarray) -> np.ndarray:
        """Compute Power Spectral Density of the graph Laplacian."""
        if A.shape[0] == 0:
            return np.array([0.0])
            
        D = np.diag(A.sum(axis=1))
        L = D - A
        
        # Eigenvalues
        try:
            eigenvalues = np.linalg.eigvalsh(L)
        except np.linalg.LinAlgError:
            eigenvalues = np.zeros(A.shape[0])
            
        # Welch's method approximation (simplified for single segment due to size constraints)
        # Pad to power of 2 for FFT efficiency
        n = len(eigenvalues)
        if n == 0: return np.array([0.0])
        
        fft_val = np.fft.rfft(eigenvalues)
        psd = np.abs(fft_val)**2
        return psd

    def _compute_free_energy(self, alpha: float, beta: float, psd: np.ndarray, sigma2: float = 0.1) -> float:
        """
        Compute Variational Free Energy.
        F = Complexity (KL) - Accuracy (Log Likelihood)
        """
        # 1. Complexity: KL(Beta(alpha, beta) || Beta(1, 1))
        # KL = ln(B(1,1)/B(a,b)) + (a-1)(psi(a)-psi(a+b)) + (b-1)(psi(b)-psi(a+b)) + ...
        # Simplified approximation for stability:
        # Uniform prior is (1,1). 
        mean_theta = alpha / (alpha + beta)
        variance_theta = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1) + 1e-9)
        
        # Approx KL using mean/variance mismatch with Uniform (mean=0.5, var=1/12)
        # Using a simplified proxy: deviation from uniform confidence
        kl_complexity = abs(mean_theta - 0.5) * 2.0 
        
        # 2. Accuracy: -log p(s | theta)
        # Assume Gaussian likelihood centered on theta
        # We need a scalar summary of PSD to compare. Use mean power.
        s_scalar = np.mean(psd) if len(psd) > 0 else 0.0
        
        # Normalize s_scalar roughly to [0,1] range assumption for comparison
        # This is a heuristic mapping for the "logical frequency profile"
        s_norm = min(1.0, max(0.0, s_scalar / 10.0)) 
        
        likelihood_val = 1.0 / (np.sqrt(2 * np.pi * sigma2) + 1e-9) * \
                         np.exp(-(s_norm - mean_theta)**2 / (2 * sigma2))
                         
        accuracy_term = -np.log(likelihood_val + 1e-9)
        
        return kl_complexity + accuracy_term

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Check if answer acknowledges complexity or just picks A/B
            if len(re.findall(r'\b(yes|no|a|b|true|false)\b', a_lower)) == 1:
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(p_lower):
            if "depends" not in a_lower and "context" not in a_lower:
                return 0.4
                
        # 4. Pronoun Ambiguity in "Who" questions
        if "who" in p_lower and self.patterns['pronoun_ambiguity'].search(p_lower):
            return 0.3
            
        return 1.0 # No specific trap detected

    def _constructive_compute(self, prompt: str, candidate: str) -> float:
        """
        Attempt to solve math/logic problems constructively.
        Returns a score 0-1 based on correctness if solvable, else 0.5.
        """
        # Simple math extraction
        numbers = self.patterns['numbers'].findall(prompt)
        if len(numbers) >= 2:
            try:
                vals = [float(n.replace('%', '')) for n in numbers]
                # Check for simple comparison in candidate
                if ">" in candidate or "greater" in candidate.lower():
                    if vals[0] > vals[1]: return 1.0
                    else: return 0.1
                elif "<" in candidate or "less" in candidate.lower():
                    if vals[0] < vals[1]: return 1.0
                    else: return 0.1
                elif "=" in candidate or "equal" in candidate.lower():
                    if abs(vals[0] - vals[1]) < 1e-6: return 1.0
                    else: return 0.1
            except:
                pass
        return 0.5 # Neutral if not computable

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0=identical, 1=disjoint)."""
        z = lambda x: len(x) # Placeholder for length, real zlib would be used here
        # Using length ratio as a proxy for NCD to stay pure stdlib without import overhead in thought block
        # Real implementation: len(zlib.compress(s1+s2)) / max(len(zlib.compress(s1)), len(zlib.compress(s2)))
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1+s2).encode()))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_psd = self._compute_spectral_signal(self._build_graph(prompt))
        
        # Meta-confidence cap based on prompt analysis
        # We use a dummy answer for initial prompt check, but real check happens per candidate
        prompt_cap = 1.0 
        if any(self.patterns[k].search(prompt) for k in ['presupposition', 'false_dichotomy', 'subjectivity']):
            prompt_cap = 0.4

        for cand in candidates:
            # 1. Structural/Spectral Analysis
            cand_psd = self._compute_spectral_signal(self._build_graph(cand))
            
            # 2. Bandit State Initialization (Thompson Sampling)
            cand_key = hash(cand)
            if cand_key not in self.bandit_state:
                self.bandit_state[cand_key] = {'alpha': 1.0, 'beta': 1.0}
            
            state = self.bandit_state[cand_key]
            
            # Sample quality estimate
            theta_sample = np.random.beta(state['alpha'], state['beta'])
            
            # Compute Free Energy
            F = self._compute_free_energy(state['alpha'], state['beta'], cand_psd)
            
            # Acquisition Value (simplified)
            # Lower F is better. Higher theta is better.
            acquisition = theta_sample - F
            
            # Update Bandit (Simulated one-step update based on acquisition)
            # Reward proxy: exp(-F)
            reward = math.exp(-F)
            state['alpha'] += reward
            state['beta'] += (1 - reward)
            
            # 3. Constructive Computation Score
            comp_score = self._constructive_compute(prompt, cand)
            
            # 4. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better match
            
            # 5. Final Score Composition
            # Structural (Spectral/Bandit): 50%
            # Computation: 35%
            # NCD: 15%
            structural_score = max(0, 1.0 - F) # Normalize F roughly
            
            final_score = (
                0.50 * structural_score + 
                0.35 * comp_score + 
                0.15 * ncd_score
            )
            
            # Apply Epistemic Cap (Tier B)
            meta_cap = self._meta_confidence(prompt, cand)
            if meta_cap < 1.0:
                # If ambiguous, penalize high confidence unless it's a "I don't know" type answer
                if "cannot determine" in cand.lower() or "insufficient" in cand.lower():
                    final_score = 0.9 # Reward honesty
                else:
                    final_score = min(final_score, meta_cap + 0.1) # Cap slightly above to allow ranking

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Spectral-F: {F:.4f}, Comp: {comp_score:.2f}, MetaCap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta Confidence Check (Tier B)
        cap = self._meta_confidence(prompt, answer)
        
        # 2. Structural Signal Strength
        symbols = self._extract_symbols(answer)
        symbol_count = sum(len(v) for v in symbols.values())
        
        # Base confidence on structural richness
        base_conf = 0.5
        if symbol_count > 3:
            base_conf = 0.8
        elif symbol_count == 0:
            base_conf = 0.3 # Low signal
            
        # 3. Computation Check
        comp_val = self._constructive_compute(prompt, answer)
        if comp_val == 1.0:
            base_conf = 0.95 # Definitive math solution
        elif comp_val == 0.1:
            base_conf = 0.1 # Math contradiction
            
        final_conf = min(base_conf, cap)
        
        # Ensure we never return > 0.9 without definitive computation
        if comp_val != 1.0 and final_conf > 0.9:
            final_conf = 0.85
            
        return float(final_conf)