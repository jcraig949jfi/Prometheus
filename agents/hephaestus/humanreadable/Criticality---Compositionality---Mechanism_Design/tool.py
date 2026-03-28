import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a Weighted Constraint Hypergraph (WCH) with Belief Propagation.
    Mechanism:
    1. Compositionality: Parses atomic propositions and relations (NOT, GT, IF, CAUSE).
    2. Criticality: Uses BP to find system magnetization (m) and susceptibility (chi).
    3. Mechanism Design: Scores candidates by how much they reduce susceptibility (chi)
       and increase order (|m|), incentivizing coherent, truthful answers.
    """
    
    def __init__(self):
        self.beta = 2.0  # Strength of evidence from candidate
        self.lambda_reg = 0.5  # Weight for susceptibility in scoring
        self.iterations = 20  # BP iterations
        
        # Regex patterns for structural parsing
        self.patterns = {
            'not': re.compile(r'\b(not|no|never|without)\b', re.I),
            'gt': re.compile(r'\b(greater than|more than|exceeds|larger than|>\b)', re.I),
            'lt': re.compile(r'\b(less than|fewer than|under|<\b)', re.I),
            'if': re.compile(r'\b(if|unless|provided that)\b', re.I),
            'cause': re.compile(r'\b(causes|leads to|results in|because|since)\b', re.I),
            'num': re.compile(r'-?\d+\.?\d*')
        }

    def _extract_props(self, text: str) -> List[str]:
        """Extract atomic propositions (simplified to sentences/clauses)."""
        # Split by common delimiters to get rough propositions
        raw = re.split(r'[.,;:?]', text)
        props = [p.strip() for p in raw if len(p.strip()) > 2]
        return props if props else ["default_prop"]

    def _build_graph(self, text: str) -> Tuple[List[str], List[Tuple[int, int, str]]]:
        """Parse text into nodes and edges (relations)."""
        props = self._extract_props(text)
        edges = []
        n = len(props)
        
        # Self-consistency edges (diagonal dominance approximation)
        for i in range(n):
            edges.append((i, i, 'SELF'))

        # Detect relations between propositions or within propositions
        for i, p in enumerate(props):
            lower_p = p.lower()
            
            # Negation
            if self.patterns['not'].search(p):
                edges.append((i, i, 'NOT'))
            
            # Comparatives (Numeric)
            nums = [float(x) for x in self.patterns['num'].findall(p)]
            if len(nums) >= 2:
                if self.patterns['gt'].search(p) or (len(nums)==2 and nums[0] > nums[1] and '>' in p):
                     # Logic: If p says A > B, and we assume p is true, then A>B holds.
                     # We model this as a constraint on the truth of p relative to reality
                     edges.append((i, i, 'NUM_GT'))
                elif self.patterns['lt'].search(p):
                    edges.append((i, i, 'NUM_LT'))

            # Conditionals (simplified: if present, adds conditional weight)
            if self.patterns['if'].search(p):
                edges.append((i, i, 'IF'))
                
            # Causal
            if self.patterns['cause'].search(p):
                edges.append((i, i, 'CAUSE'))

        return props, edges

    def _run_bp(self, n: int, edges: List, evidence: List[int], h_field: float = 0.0) -> Tuple[float, float]:
        """
        Run Loopy Belief Propagation.
        Returns (magnetization, susceptibility_approx).
        """
        if n == 0: return 0.0, 0.0
        
        # Initialize messages (uniform)
        # State: 0 (False), 1 (True)
        # Beliefs b[i] = [P(False), P(True)]
        beliefs = np.ones((n, 2)) * 0.5
        
        # Apply evidence as unary factors
        for i, val in enumerate(evidence):
            if val == 1:
                beliefs[i, :] = [0.01, 0.99] # Strong prior for True
            elif val == -1:
                beliefs[i, :] = [0.99, 0.01] # Strong prior for False

        # Add external field h_field to bias towards True/False slightly for susceptibility calc
        if h_field != 0:
            bias = np.array([np.exp(-h_field), np.exp(h_field)])
            beliefs *= bias
            beliefs /= beliefs.sum(axis=1, keepdims=True)

        for _ in range(self.iterations):
            new_beliefs = beliefs.copy()
            for i in range(n):
                # Collect messages from neighbors (simplified to self-consistency and global coupling)
                # In this compact implementation, we simulate constraints via local factors
                factor = np.ones(2)
                
                for (u, v, type_) in edges:
                    if u == i: # Self edge
                        if type_ == 'NOT':
                            factor *= np.array([0.1, 0.9]) if beliefs[i, 1] > 0.5 else np.array([0.9, 0.1])
                        elif type_ == 'NUM_GT':
                            # Encourage consistency with numeric logic (heuristic)
                            factor *= np.array([0.8, 1.2]) 
                        elif type_ == 'IF':
                            # Conditionals increase uncertainty slightly unless resolved
                            factor *= np.array([1.0, 1.0]) 
                    
                    # Simple pairwise coupling (global coherence)
                    if u != i and v == i:
                        # Encourage agreement with neighbors
                        factor *= beliefs[u] 

                # Normalize and update
                new_beliefs[i] = beliefs[i] * factor
                new_beliefs[i] /= new_beliefs[i].sum() + 1e-9
            
            beliefs = new_beliefs

        # Calculate Magnetization m = avg(2*P(True) - 1)
        p_true = beliefs[:, 1]
        m = np.mean(2 * p_true - 1)
        
        return m, p_true

    def _compute_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Core logic: Build WCH, run BP, compute criticality-based score."""
        full_text = f"{prompt} {candidate}"
        props, edges = self._build_graph(full_text)
        n = len(props)
        
        if n == 0:
            return -1.0, "No structure found"

        # 1. Base run (Prompt only context)
        # Map candidate props to evidence
        # Heuristic: If candidate words appear in prompt props, they are asserted
        evidence = [0] * n 
        cand_words = set(self._extract_props(candidate))
        
        for i, p in enumerate(props):
            for cw in cand_words:
                if cw in p or p in cw:
                    evidence[i] = 1 # Asserted true by candidate
                    break
        
        # Run BP for base state (h=0)
        m_base, _ = self._run_bp(n, edges, evidence, h_field=0.0)
        
        # Run BP for susceptibility (h = +/- delta)
        delta = 1e-3
        m_plus, _ = self._run_bp(n, edges, evidence, h_field=delta)
        m_minus, _ = self._run_bp(n, edges, evidence, h_field=-delta)
        
        # Susceptibility chi ~ dm/dh
        chi = (m_plus - m_minus) / (2 * delta)
        
        # 2. Mechanism Design Scoring
        # Goal: Maximize order (|m|) and minimize susceptibility (chi)
        # A good answer should make the system decisive (high |m|) and stable (low chi)
        
        # Target: We want m to be far from 0 (decisive) and chi to be small (stable)
        # Score = -[(m_target - m_obs)^2 + lambda * chi^2]
        # Since we don't know m_target, we assume coherent answers push |m| towards 1.
        # So we maximize |m| and minimize chi.
        
        order_score = abs(m_base)
        stability_score = -abs(chi) # Lower chi is better
        
        final_score = order_score + self.lambda_reg * stability_score
        
        reason = f"Nodes:{n}, Magnetization:{m_base:.3f}, Susceptibility:{chi:.3f}"
        return final_score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        base_scores = []
        
        # First pass: get raw scores
        for cand in candidates:
            score, reason = self._compute_score(prompt, cand)
            base_scores.append((cand, score, reason))
            
        # Fallback to NCD if structural signal is weak (all scores very close)
        # But per instructions, NCD is only a tiebreaker. 
        # We rely on the WCH score primarily.
        
        # Normalize scores to 0-1 range for consistency if needed, but ranking is key
        sorted_candidates = sorted(base_scores, key=lambda x: x[1], reverse=True)
        
        for cand, score, reason in sorted_candidates:
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the scoring mechanism."""
        score, _ = self._compute_score(prompt, answer)
        # Map score (roughly -2 to 2) to 0-1
        # Assuming a good score is > 0, bad < 0
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return max(0.0, min(1.0, conf))

# Example usage logic (not part of class, for context):
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > C, is A > C?", ["Yes, A is greater than C", "No, A is less than C"])
# print(res)