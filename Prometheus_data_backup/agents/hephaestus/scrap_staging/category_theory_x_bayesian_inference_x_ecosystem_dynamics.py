import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Category Theory x Bayesian Inference reasoning engine.
    
    Mechanism:
    1. Parsing (Objects): Extracts atomic clauses via regex into a category C.
    2. Functor (Feature Space): Maps clauses to vectors (polarity, causality, magnitude).
       Morphisms (implications) become transformation matrices.
    3. Belief Propagation: Iteratively updates node probabilities using matrix ops
       until convergence, simulating MCMC on the constructed graph.
    4. Scoring: The posterior probability of the answer-node determines the score.
    
    Structural features (negation, comparatives, conditionals) drive the logic.
    NCD is used strictly as a tiebreaker for low-signal scenarios.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unless)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|higher|lower|more|fewer)\s+(than)?\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|inhibits)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|when|unless)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|most|every|none)\b', re.IGNORECASE)
        }
        self._zlib = __import__('zlib')

    def _extract_clauses(self, text: str) -> List[str]:
        """Split text into atomic propositions based on delimiters."""
        # Simple split by conjunctions to simulate object extraction
        clean_text = re.sub(r'\s+', ' ', text).strip()
        # Split by common logical connectors but keep them for context if needed
        parts = re.split(r'\s*(?:\.|,|;|and|or|but)\s+', clean_text)
        return [p.strip() for p in parts if len(p.strip()) > 2]

    def _vectorize_clause(self, clause: str) -> np.ndarray:
        """
        Functor F: Clause -> Vector.
        Dimensions: [Polarity, Causal_Sign, Magnitude, Conditional_Depth, Quantifier_Strength]
        """
        vec = np.zeros(5, dtype=float)
        
        # 1. Polarity (Negation)
        if self.patterns['negation'].search(clause):
            vec[0] = -1.0
        else:
            vec[0] = 1.0
            
        # 2. Causal Sign
        c_match = self.patterns['causal'].search(clause)
        if c_match:
            word = c_match.group(0).lower()
            vec[1] = -1.0 if 'inhibit' in word else 1.0
            
        # 3. Numeric Magnitude (scaled)
        nums = self.patterns['number'].findall(clause)
        if nums:
            try:
                val = float(nums[0])
                vec[2] = np.tanh(val / 10.0) # Scale to [-1, 1] roughly
            except ValueError:
                vec[2] = 0.0
                
        # 4. Conditional Depth
        if self.patterns['conditional'].search(clause):
            vec[3] = 1.0
            
        # 5. Quantifier Strength
        q_match = self.patterns['quantifier'].search(clause)
        if q_match:
            q_word = q_match.group(0).lower()
            if q_word == 'all': vec[4] = 1.0
            elif q_word == 'most': vec[4] = 0.8
            elif q_word == 'some': vec[4] = 0.5
            else: vec[4] = 0.2
            
        return vec

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Construct the categorical graph and initialize belief states.
        Returns nodes (vectors) and initial probability distribution.
        """
        # Combine prompt and candidate to check consistency
        full_text = f"{prompt} {candidate}"
        clauses = self._extract_clauses(full_text)
        
        if not clauses:
            return [], np.array([])
            
        nodes = [self._vectorize_clause(c) for c in clauses]
        n = len(nodes)
        
        # Initialize priors based on structural richness (lexical cues)
        priors = np.zeros(n)
        for i, clause in enumerate(clauses):
            score = 1.0
            if self.patterns['number'].search(clause): score += 0.5
            if self.patterns['causal'].search(clause): score += 0.3
            if self.patterns['conditional'].search(clause): score += 0.2
            priors[i] = score
            
        # Normalize to get initial probability distribution (softmax-like)
        exp_p = np.exp(priors - np.max(priors))
        p0 = exp_p / np.sum(exp_p)
        
        return nodes, p0

    def _propagate_beliefs(self, nodes: List[np.ndarray], p0: np.ndarray, steps: int = 10) -> np.ndarray:
        """
        Perform synchronous message passing (Bayesian core).
        Simulates M_ij transformations to update beliefs.
        """
        if len(nodes) == 0:
            return np.array([])
            
        n = len(nodes)
        p = p0.copy()
        
        # Construct adjacency/transition matrix W based on vector similarity/logic
        # M_ij transforms source i toward target j
        W = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 1.0 # Self-loop
                else:
                    # Logical implication strength: dot product similarity adjusted by causality
                    # If node i causes something and j is consistent, strong link
                    sim = np.dot(nodes[i], nodes[j])
                    # Normalize slightly to prevent explosion
                    W[i, j] = max(0, sim / 5.0) 
        
        # Normalize columns of W to represent conditional probabilities
        col_sums = W.sum(axis=0)
        col_sums[col_sums == 0] = 1.0
        W = W / col_sums
        
        # Iterative update: p_new = softmax(W^T * p_old)
        # Using a bias from original priors to prevent drift
        b = p0 / np.sum(p0) 
        
        for _ in range(steps):
            p_new = np.dot(W.T, p) + 0.1 * b
            # Softmax normalization
            p_new = np.exp(p_new - np.max(p_new))
            p_new = p_new / np.sum(p_new)
            
            if np.linalg.norm(p_new - p) < 1e-4:
                break
            p = p_new
            
        return p

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(self._zlib.compress(s1_b))
        len_s2 = len(self._zlib.compress(s2_b))
        len_both = len(self._zlib.compress(s1_b + s2_b))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_both - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt nodes to ensure consistent graph structure context
        prompt_clauses = self._extract_clauses(prompt)
        prompt_vecs = [self._vectorize_clause(c) for c in prompt_clauses]
        prompt_coherence = 0.0
        if len(prompt_vecs) > 1:
            # Check internal consistency of prompt
            for i in range(len(prompt_vecs)-1):
                prompt_coherence += np.dot(prompt_vecs[i], prompt_vecs[i+1])
            prompt_coherence /= (len(prompt_vecs) - 1)

        for cand in candidates:
            nodes, p0 = self._build_graph(prompt, cand)
            
            if len(nodes) == 0:
                score = 0.0
                reason = "No structural clauses detected."
            else:
                posteriors = self._propagate_beliefs(nodes, p0)
                # The score is the maximum posterior probability achieved in the graph
                # representing the stability of the logical system formed by P+C
                score = float(np.max(posteriors)) if len(posteriors) > 0 else 0.0
                
                # Boost score if the candidate reinforces prompt coherence (causal alignment)
                if len(prompt_vecs) > 0 and len(nodes) > len(prompt_clauses):
                    # Check last node (candidate part) against prompt average
                    cand_vec = nodes[-1]
                    alignment = np.dot(cand_vec, np.mean(prompt_vecs, axis=0))
                    score = min(1.0, score * (1.0 + 0.1 * alignment))

                reason = f"Converged posterior: {score:.4f}"

            # Tiebreaker: If scores are very close or low, use NCD to prefer concise, relevant answers
            if score < 0.5 or len(set([r['score'] for r in results])) == 1:
                ncd = self._ncd_score(prompt, cand)
                # Lower NCD is better (more similar/compressible together)
                # Invert and scale NCD to [0, 1] range roughly, higher is better
                ncd_bonus = (1.0 - ncd) * 0.1 
                score += ncd_bonus
                reason += f" (NCD adjusted)"

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the posterior probability of the 
        combined prompt+answer graph.
        """
        nodes, p0 = self._build_graph(prompt, answer)
        if len(nodes) == 0:
            return 0.0
            
        posteriors = self._propagate_beliefs(nodes, p0)
        if len(posteriors) == 0:
            return 0.0
            
        # Confidence is the stability (max posterior) of the system
        conf = float(np.max(posteriors))
        
        # Penalty for contradictions detected via negation patterns in both
        full_text = f"{prompt} {answer}"
        neg_count = len(self.patterns['negation'].findall(full_text))
        if neg_count > 2:
            # Heuristic: Too many negations might imply complex/contradictory logic
            conf *= 0.8
            
        return min(1.0, max(0.0, conf))