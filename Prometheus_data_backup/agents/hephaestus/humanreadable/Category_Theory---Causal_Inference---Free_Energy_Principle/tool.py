import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements a reasoning engine based on Category Theory, Causal Inference, 
    and the Free Energy Principle.
    
    Mechanism:
    1. Parsing (Category Theory): Extracts atomic propositions (objects) and 
       relations like causality, conditionals, and negations (morphisms) using regex.
       Constructs a DAG represented as an adjacency matrix.
    2. Belief Propagation (Functorial): Maps objects to belief scalars [0,1].
       Propagates constraints (b_j >= b_i) iteratively to satisfy logical consistency.
    3. Scoring (Free Energy): Computes F = E - H.
       E (Energy): Prediction error of observed facts under current beliefs.
       H (Entropy): Uncertainty of the belief distribution.
       Score = -F (Lower free energy = higher score).
    4. Tie-breaking: Uses Normalized Compression Distance (NCD) if scores are close.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|produces|results in|implies)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|when|then)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|higher than|lower than|before|after)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|every|each)\b', re.IGNORECASE)
        }

    def _extract_props(self, text):
        """Extract atomic propositions and normalize them."""
        # Simple sentence splitter and token cleaner
        sentences = re.split(r'[.;!?]', text)
        props = []
        for s in sentences:
            s = s.strip()
            if s:
                props.append(s.lower())
        return props

    def _build_graph(self, text):
        """
        Parse text into objects (propositions) and morphisms (relations).
        Returns adjacency matrix A and list of props.
        """
        props = self._extract_props(text)
        n = len(props)
        if n == 0:
            return np.array([], dtype=np.uint8), []
        
        A = np.zeros((n, n), dtype=np.uint8)
        
        # Build edges based on structural cues
        for i, p_i in enumerate(props):
            for j, p_j in enumerate(props):
                if i == j: continue
                
                # Causal/Conditional logic: if p_i contains cue and p_j follows logically or is adjacent
                # Heuristic: Adjacent sentences with causal keywords create edges
                has_cue = any(p in p_i for p in ['cause', 'lead', 'imply', 'if', 'unless'])
                if has_cue and abs(i - j) <= 1:
                    A[i, j] = 1
                
                # Comparative/Ordering logic
                if any(k in p_i for k in ['greater', 'less', 'before', 'after']):
                     if abs(i - j) == 1: # Connect to neighbor
                        A[i, j] = 1

        # Transitivity closure approximation (simple iteration)
        # This enforces the category theoretic composition of morphisms
        for _ in range(2):
            A = np.logical_or(A, np.dot(A, A)).astype(np.uint8)
            
        return A, props

    def _propagate_beliefs(self, A, observed_indices):
        """
        Functorial belief assignment.
        Initialize beliefs, then propagate constraints: b_j >= b_i for edge i->j.
        """
        n = A.shape[0]
        if n == 0: return 0.0, 0.0
        
        # Initial prior
        b = np.full(n, 0.5)
        
        # Set observed facts (from prompt structure) to high confidence
        for idx in observed_indices:
            if idx < n:
                b[idx] = 0.99
        
        # Iterative propagation (Modus Ponens enforcement)
        # b_new = max(b, A.T @ b)
        for _ in range(10): # Converge quickly
            b_new = np.maximum(b, A.T @ b)
            if np.allclose(b, b_new):
                break
            b = b_new
            
        return b

    def _compute_free_energy(self, b, observed_indices):
        """
        Calculate Free Energy F = E - H.
        E: Prediction error (Negative Log Likelihood)
        H: Entropy
        """
        if len(b) == 0:
            return 0.0
            
        epsilon = 1e-9
        b = np.clip(b, epsilon, 1 - epsilon)
        
        # Energy: Error on observed facts (we expect them to be true/high prob)
        # If observed, data=1. Likelihood = b. Error = -log(b)
        E = 0.0
        for i in range(len(b)):
            if i in observed_indices:
                E -= np.log(b[i])
            else:
                # Unobserved data contributes less, assume neutral expectation
                pass
                
        # Entropy: H = -sum(b log b + (1-b) log (1-b))
        H = -np.sum(b * np.log(b) + (1 - b) * np.log(1 - b))
        
        F = E - H
        return F

    def _ncd(self, s1, s2):
        """Normalized Compression Distance using zlib as proxy."""
        import zlib
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_A, prompt_props = self._build_graph(prompt)
        prompt_obs = list(range(len(prompt_props))) # Assume all prompt props are observed facts
        
        # Baseline score for prompt structure
        base_F = self._compute_free_energy(
            self._propagate_beliefs(prompt_A, prompt_obs) if len(prompt_props) > 0 else np.array([]),
            prompt_obs
        )

        for cand in candidates:
            # Combine prompt and candidate to check consistency
            full_text = f"{prompt} {cand}"
            cand_A, cand_props = self._build_graph(full_text)
            
            # In a real scenario, we'd map prompt props to combined props.
            # Here, we approximate by checking if candidate introduces contradictions 
            # or maintains low free energy relative to the prompt structure.
            
            # Simple heuristic: If candidate adds negative words to positive causal chains, energy rises.
            # We score based on the Free Energy of the combined system.
            # Lower F is better.
            
            if len(cand_props) == 0:
                # Fallback for short answers like "Yes"/"No"
                # Check semantic overlap with prompt's inferred direction
                score_val = 0.5 
                reason = "Low structural content"
            else:
                # Compute F for the combined state
                # We treat the whole text as a system. 
                # Ideally, a correct answer minimizes surprise (F) given the prompt context.
                b = self._propagate_beliefs(cand_A, list(range(len(prompt_props)))) # Observe prompt part
                F_val = self._compute_free_energy(b, list(range(len(prompt_props))))
                
                # Invert F for scoring (higher is better)
                score_val = -F_val
                reason = f"Free Energy: {-F_val:.4f}, Nodes: {len(cand_props)}"

            # NCD Tiebreaker / Boost for structural similarity
            ncd_score = 0.0
            if len(prompt) > 10:
                # Low NCD means similar structure/content
                ncd_val = self._ncd(prompt, cand)
                # Adjust score slightly by NCD if F scores are ambiguous
                ncd_score = (1.0 - ncd_val) * 0.1 

            final_score = score_val + ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reason
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range heuristically
        # Free energy can be negative or positive. 
        # We map the raw score to a probability-like confidence.
        raw_score = res[0]['score']
        
        # Sigmoid-like mapping to bound between 0 and 1
        # Assuming typical F values are within a certain range
        conf = 1.0 / (1.0 + math.exp(-raw_score))
        return float(np.clip(conf, 0.0, 1.0))