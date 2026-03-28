import re
import numpy as np

class ReasoningTool:
    """
    Implements an Ising-model based reasoning engine.
    Mechanism:
    1. Parses prompt into binary propositions (spins) based on logical markers.
    2. Constructs a Causal Coupling Matrix (J) from conditional/causal patterns.
    3. Constructs a Pragmatic Field Vector (h) from Gricean maxims (negation, quantity).
    4. Evaluates candidate answers by fixing spins and computing Negative Free Energy.
    5. Uses Mean-Field Approximation near Criticality (T ~ Tc) to maximize sensitivity.
    """
    
    def __init__(self):
        self.causal_patterns = [
            (r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)', 1.0),
            (r'(.+?)\s+causes?\s+(.+?)', 1.0),
            (r'(.+?)\s+leads?\s+to\s+(.+?)', 1.0),
            (r'unless\s+(.+?)\s+(.+?)', -1.0), # Unless A then B ~ If not A then B
        ]
        self.negation_words = ['not', "n't", 'no', 'never', 'none']
        self.quantifiers = ['all', 'every', 'some', 'few', 'most']

    def _tokenize(self, text):
        # Simple sentence splitting and lowercasing
        sentences = re.split(r'[.\?!]', text.lower())
        return [s.strip() for s in sentences if s.strip()]

    def _extract_features(self, text):
        """Extracts spins, J matrix components, and h vector components."""
        sentences = self._tokenize(text)
        n = max(len(sentences), 1)
        
        # Initialize structures
        # We map each sentence to a spin. +1 = true, -1 = false.
        h = np.zeros(n)
        J = np.zeros((n, n))
        
        # Map sentences to indices for causal links
        sent_map = {s: i for i, s in enumerate(sentences)}
        
        for i, sent in enumerate(sentences):
            # Pragmatic Field (h)
            # Quality: Negation penalty/reward heuristic
            if any(neg in sent for neg in self.negation_words):
                h[i] += 0.3 # Reward truth-likeness of negated statements if context fits
            
            # Quantity: "some" implies not "all"
            if 'some' in sent:
                h[i] -= 0.4 
            if 'all' in sent:
                h[i] += 0.2
                
            # Relation: Off-topic is hard to detect without context, 
            # but we assume prompt sentences are relevant.
            
        # Causal Coupling (J)
        for pattern, weight in self.causal_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                # Try to find corresponding sentences
                s1, s2 = match[0].strip(), match[1].strip()
                idx1, idx2 = -1, -1
                
                # Fuzzy match to existing sentences
                for s, idx in sent_map.items():
                    if s1 in s: idx1 = idx
                    if s2 in s: idx2 = idx
                
                if idx1 != -1 and idx2 != -1:
                    J[idx1, idx2] += weight
                    J[idx2, idx1] += weight # Symmetrize immediately for undirected energy

        # Normalize J
        if n > 1:
            J = (J + J.T) / 2
            
        return sentences, h, J, n

    def _compute_free_energy(self, h, J, fixed_spins=None):
        """
        Computes negative free energy using Mean-Field Approximation.
        fixed_spins: dict {index: value} for candidate answer constraints.
        """
        n = len(h)
        if n == 0: return 0.0
        
        # Initialize magnetization m
        m = np.tanh(h) + 1e-6 
        
        # Apply fixed spins from candidate answer if provided
        if fixed_spins:
            for idx, val in fixed_spins.items():
                if 0 <= idx < n:
                    m[idx] = val

        # Critical Temperature Estimation
        Tc = np.mean(np.sum(np.abs(J), axis=1)) if n > 1 else 1.0
        if Tc == 0: Tc = 1.0
        T = Tc * 1.01 # Slightly above critical point
        
        # Iterate Mean-Field Equation: m_i = tanh((sum(J_ij * m_j) + h_i) / T)
        for _ in range(50): # Converge quickly
            m_old = m.copy()
            field = np.dot(J, m) + h
            
            # Apply fixed constraints during iteration
            if fixed_spins:
                for idx, val in fixed_spins.items():
                    if 0 <= idx < n:
                        field[idx] = np.arctanh(val) * T # Force the value
            
            m = np.tanh(field / T)
            
            if np.allclose(m, m_old, atol=1e-4):
                break

        # Free Energy F = E - TS
        # E = -0.5 * sum(J_ij * m_i * m_j) - sum(h_i * m_i)
        energy = -0.5 * np.sum(J * np.outer(m, m)) - np.sum(h * m)
        
        # Entropy S = -sum( (1+m)/2 * ln((1+m)/2) + (1-m)/2 * ln((1-m)/2) )
        # Avoid log(0)
        eps = 1e-9
        s_plus = (1 + m) / 2 + eps
        s_minus = (1 - m) / 2 + eps
        entropy = -np.sum(s_plus * np.log(s_plus) + s_minus * np.log(s_minus))
        
        F = energy - T * entropy
        return -F # Return Negative Free Energy (higher is better)

    def _parse_candidate(self, candidate, sentences):
        """
        Maps a candidate string to fixed spins.
        Returns dict {index: +1/-1}.
        """
        fixed = {}
        cand_lower = candidate.lower()
        
        # Heuristic: If candidate matches a sentence or keyword, fix that spin.
        # If candidate is "True"/"False", it applies to the main conclusion.
        
        is_true = any(x in cand_lower for x in ['true', 'yes', 'correct', 'does', 'is'])
        is_false = any(x in cand_lower for x in ['false', 'no', 'incorrect', 'not', "n't"])
        
        # If explicit boolean, apply to all extracted sentences as a consistency check?
        # Better: Apply to the last sentence (often the query) or specific matches.
        
        for i, sent in enumerate(sentences):
            # If candidate contains the sentence text
            if sent in cand_lower or cand_lower in sent:
                fixed[i] = 1.0 if is_true else (-1.0 if is_false else 1.0)
            
            # If candidate is a simple "Yes/No", we assume it affirms/denies the logical flow
            # We simulate this by checking if the candidate contradicts the sentence content
            if is_true and any(neg in sent for neg in self.negation_words):
                 # Affirming a negative statement -> Spin +1 (statement is true)
                 fixed[i] = 1.0
            elif is_false and not any(neg in sent for neg in self.negation_words):
                 # Denying a positive statement -> Spin -1 (statement is false)
                 fixed[i] = -1.0
                 
        # If no specific mapping found, default to global consistency check
        if not fixed:
            # Assume the candidate asserts the truth of the whole prompt logic
            if is_true:
                fixed = {i: 1.0 for i in range(len(sentences))}
            elif is_false:
                fixed = {i: -1.0 for i in range(len(sentences))}
                
        return fixed

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        sentences, h, J, n = self._extract_features(prompt)
        results = []
        
        # Baseline score using just prompt energy
        base_energy = self._compute_free_energy(h, J)
        
        for cand in candidates:
            fixed_spins = self._parse_candidate(cand, sentences)
            # Compute energy with candidate constraints
            score = self._compute_free_energy(h, J, fixed_spins)
            
            # Normalize slightly against base to prevent magnitude bias
            # Higher score = lower free energy = more stable state
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Ising Free Energy: {score:.4f} (Base: {base_energy:.4f})"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on relative energy gap."""
        # Generate a dummy opposite to compare against if possible, 
        # or use absolute energy magnitude.
        # Here we use the score relative to a randomized baseline approximation.
        
        # 1. Get score for the answer
        res = self.evaluate(prompt, [answer])
        if not res: return 0.5
        score_ans = res[0]['score']
        
        # 2. Get score for a null/neutral hypothesis (approximated by empty constraint)
        # Actually, let's compare against the "False" version of the answer
        opposite = "False" if "true" in answer.lower() else "True"
        res_opp = self.evaluate(prompt, [opposite])
        score_opp = res_opp[0]['score'] if res_opp else score_ans
        
        # 3. Softmax-like normalization
        diff = score_ans - score_opp
        conf = 1.0 / (1.0 + np.exp(-diff)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))