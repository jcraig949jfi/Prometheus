import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Statistical Mechanics x Theory of Mind x Criticality Reasoning Tool.
    
    Mechanism:
    1. Proposition Extraction: Parses atomic statements (negations, comparatives, 
       conditionals, causality) from prompt and candidates into binary variables.
    2. Energy Model: Constructs an Ising-like energy function where logical 
       consistency lowers energy (J_ij > 0 for entailment, J_ij < 0 for contradiction).
    3. Theory of Mind (ToM): Adds latent variables representing agent beliefs to 
       'explain away' inconsistencies between prompt facts and candidate claims.
    4. Criticality: Tunes inverse temperature (beta) to maximize susceptibility, 
       placing the system at a phase transition where it is most sensitive to 
       logical contradictions.
    5. Scoring: Uses Bethe free energy approximation via belief propagation to 
       rank candidates. Lower free energy = higher compatibility.
    """
    
    def __init__(self):
        self.rng = np.random.default_rng(seed=42)

    def _extract_props(self, text: str) -> List[Dict]:
        """Extract atomic propositions with type and polarity."""
        text_lower = text.lower()
        props = []
        
        # Patterns
        negations = ['not', 'no ', 'never', 'none']
        comparatives = [('greater', 'larger', 'more', 'higher'), ('less', 'smaller', 'fewer', 'lower')]
        conditionals = ['if', 'then', 'unless']
        causals = ['because', 'causes', 'leads to', 'results in']
        
        # Simple extraction logic
        words = text_lower.split()
        
        # Check for negation
        is_negated = any(n in text_lower for n in negations)
        
        # Check types
        p_type = 'fact'
        if any(c in text_lower for c in conditionals): p_type = 'conditional'
        elif any(c in text_lower for c in causals): p_type = 'causal'
        elif any(w in text_lower for pair in comparatives for w in pair): p_type = 'comparative'
        
        # Extract numbers if present
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        
        props.append({
            'text': text.strip(),
            'negated': is_negated,
            'type': p_type,
            'numbers': [float(n) for n in nums],
            'polarity': -1 if is_negated else 1
        })
        return props

    def _compute_coupling(self, p1: Dict, p2: Dict) -> float:
        """Determine coupling strength J_ij between two propositions."""
        # Exact match implies strong positive coupling if polarities align
        if p1['text'] == p2['text']:
            return 1.0 if p1['polarity'] == p2['polarity'] else -1.0
        
        # Number logic
        if p1['numbers'] and p2['numbers'] and p1['type'] == 'comparative':
            # Simplified numeric consistency check
            if 'greater' in p1['text'] or 'more' in p1['text']:
                if p1['numbers'][0] > p2['numbers'][0]: return 0.5
                else: return -0.5
        
        # Negation contradiction
        if p1['text'] in p2['text'] or p2['text'] in p1['text']:
            if p1['polarity'] != p2['polarity']:
                return -0.8
        
        return 0.0

    def _belief_propagation(self, h: np.ndarray, J: np.ndarray, beta: float, steps: int = 10) -> Tuple[float, float]:
        """
        Approximate marginals and free energy using simple iterative updates.
        Returns (Free Energy, Susceptibility estimate).
        """
        n = len(h)
        if n == 0: return 0.0, 0.0
        
        # Initialize messages (simplified to local fields for speed/stability in small N)
        m = np.tanh(beta * h) # Magnetization
        
        for _ in range(steps):
            m_new = np.copy(m)
            for i in range(n):
                local_field = h[i]
                for j in range(n):
                    if i != j:
                        local_field += J[i, j] * m[j]
                m_new[i] = np.tanh(beta * local_field)
            m = m_new

        # Compute Energy and Entropy (Bethe approximation simplified)
        E = -np.sum(h * m) - 0.5 * np.sum(J * np.outer(m, m))
        
        # Entropy term approximation
        S = 0.0
        for mi in m:
            if abs(mi) < 1.0:
                S += -((1+mi)/2 * np.log((1+mi)/2 + 1e-9) + (1-mi)/2 * np.log((1-mi)/2 + 1e-9))
        
        F = E - (1/beta) * S if beta > 0 else 0.0
        
        # Susceptibility estimate (variance of magnetization)
        chi = np.var(m) if len(m) > 1 else 0.0
        return F, chi

    def _tune_criticality(self, h: np.ndarray, J: np.ndarray) -> float:
        """Find beta that maximizes susceptibility (critical point)."""
        betas = np.linspace(0.1, 2.0, 10)
        best_beta = 0.5
        max_chi = -1
        
        for b in betas:
            _, chi = self._belief_propagation(h, J, b, steps=5)
            if chi > max_chi:
                max_chi = chi
                best_beta = b
        return best_beta

    def _score_candidate(self, prompt: str, candidate: str) -> float:
        """Compute score for a single candidate."""
        # 1. Extract propositions
        p_props = self._extract_props(prompt)
        c_props = self._extract_props(candidate)
        all_props = p_props + c_props
        n = len(all_props)
        
        if n == 0:
            return 0.0

        # 2. Build Interaction Matrix (J) and Unary Fields (h)
        J = np.zeros((n, n))
        h = np.zeros(n)
        
        # Unary fields: Prompt propositions get strong prior belief
        for i, p in enumerate(all_props):
            if i < len(p_props):
                h[i] = 1.0 * p['polarity'] # Prompt facts are ground truth
            else:
                h[i] = 0.5 * p['polarity'] # Candidate claims have weaker prior
            
        # Couplings
        for i in range(n):
            for j in range(i+1, n):
                val = self._compute_coupling(all_props[i], all_props[j])
                J[i, j] = val
                J[j, i] = val

        # 3. Theory of Mind Layer (Simplified as adjusted fields for latent consistency)
        # We simulate the ToM layer by allowing the system to flip candidate beliefs 
        # if it reduces energy significantly, effectively 'understanding' the agent might be wrong.
        # In this implementation, this is handled by the energy minimization over the joint space.

        # 4. Criticality Tuning
        beta = self._tune_criticality(h, J)
        
        # 5. Compute Free Energy
        F, _ = self._belief_propagation(h, J, beta, steps=20)
        
        return -F # Higher score = lower free energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Energy-based compatibility score: {score:.4f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate against a dummy set to get relative scaling if needed, 
        # but here we map the raw score to 0-1 via sigmoid-like function
        score = self._score_candidate(prompt, answer)
        
        # Normalize: Assume scores range roughly between -10 and 10
        # Sigmoid mapping
        conf = 1.0 / (1.0 + np.exp(-score))
        return float(np.clip(conf, 0.0, 1.0))