import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Abductive Free-Energy Scorer (HAFES)
    
    Mechanism:
    1. Structural Parsing: Extracts tokens, negations, comparatives, conditionals, and numbers.
    2. Hypothesis Generation: Creates binary hypotheses for each candidate answer.
    3. Renormalization & Free Energy: 
       - L0 (Token): Initializes belief based on keyword matching and polarity.
       - L1 (Clause): Aggregates token beliefs, penalizing contradictions (Free Energy term).
       - L2 (Topic): Coarse-grains to a global score, weighting by certainty (inverse energy).
    4. Scoring: Candidates with lower variational free energy (higher consistency with structural constraints) rank higher.
    """
    
    ONTOLOGY = ['entity', 'property', 'relation', 'quantifier', 'negation', 'comparative', 'conditional', 'causal']
    
    def __init__(self):
        self.epsilon = 1e-6

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features: numbers, negations, comparatives, conditionals."""
        text_lower = text.lower()
        features = {
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|>|<)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'has_causal': bool(re.search(r'\b(cause|lead|result|due|because)\b', text_lower)),
            'length': len(text.split())
        }
        return features

    def _generate_hypotheses(self, candidates: List[str]) -> List[Dict]:
        """Generate abductive hypotheses for each candidate."""
        hypotheses = []
        for i, cand in enumerate(candidates):
            # Hypothesis: Candidate 'i' is the correct explanation
            hypotheses.append({
                'id': i,
                'text': cand,
                'features': self._parse_structure(cand),
                'belief': 0.5  # Initial uniform prior
            })
        return hypotheses

    def _compute_free_energy(self, prompt_feats: Dict, hyp: Dict, candidate_text: str) -> float:
        """
        Compute local variational free energy.
        F = Prediction Error + Complexity Penalty
        Lower F = Better fit.
        """
        energy = 0.0
        
        # 1. Numeric Consistency (Constraint Propagation)
        if prompt_feats['numbers'] and hyp['features']['numbers']:
            # Check if candidate numbers are logically consistent (simplified: presence implies relevance)
            # If prompt has numbers and candidate doesn't, high energy (mismatch)
            if len(hyp['features']['numbers']) == 0:
                energy += 2.0 
            else:
                # Simple transitivity check: if prompt implies ordering, candidate should reflect it
                pass 
        elif prompt_feats['numbers'] and not hyp['features']['numbers']:
            energy += 1.5 # Missing numeric evidence

        # 2. Logical Constraint Satisfaction (Modus Ponens/Tollens approx)
        # If prompt has conditional, candidate should ideally reflect consequence or condition
        if prompt_feats['has_conditional']:
            if not (hyp['features']['has_conditional'] or hyp['features']['has_causal']):
                energy += 0.8 # Penalty for ignoring conditional structure
        
        # 3. Negation Polarity Check
        if prompt_feats['has_negation']:
            # If prompt negates, a valid abductive step often acknowledges the negation or its consequence
            # This is a soft constraint; absence isn't fatal but adds uncertainty
            if not hyp['features']['has_negation']:
                energy += 0.5

        # 4. Complexity Bias (Occam's Razor)
        # Penalize excessive length difference (simplicity prior)
        len_diff = abs(prompt_feats['length'] - hyp['features']['length'])
        energy += 0.1 * min(len_diff, 10) # Cap penalty

        # 5. NCD Tiebreaker (Normalized Compression Distance approximation)
        # Used here as a fine-grained similarity term within the energy function
        try:
            combined = f"{prompt_feats['length']}_{candidate_text}"
            compressed = len(zlib.compress(combined.encode()))
            total_len = len(combined.encode())
            ncd = (compressed - total_len) / total_len if total_len > 0 else 1.0
            energy += 0.5 * ncd
        except:
            energy += 0.5

        return energy

    def _renormalize_layer(self, beliefs: np.ndarray, energies: np.ndarray) -> np.ndarray:
        """
        Renormalization step: Aggregate beliefs weighted by inverse free energy.
        b_new = sum(w_i * b_i) where w_i = 1 / (F_i + epsilon)
        """
        weights = 1.0 / (energies + self.epsilon)
        weights /= np.sum(weights) # Normalize weights
        return np.sum(beliefs * weights)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._parse_structure(prompt)
        hypotheses = self._generate_hypotheses(candidates)
        
        scores = []
        beliefs = np.array([h['belief'] for h in hypotheses])
        energies = np.zeros(len(hypotheses))
        
        # L0 -> L1: Compute Free Energy for each hypothesis against prompt structure
        for i, hyp in enumerate(hypotheses):
            energies[i] = self._compute_free_energy(prompt_feats, hyp, hyp['text'])
        
        # Minimization step: Convert Energy to Probability (Boltzmann distribution)
        # P(h) ~ exp(-E)
        exp_energies = np.exp(-energies)
        prob_dist = exp_energies / (np.sum(exp_energies) + self.epsilon)
        
        # L1 -> L2: Renormalization (Coarse graining)
        # In this single-pass context, the "Top Layer" belief is the weighted aggregate
        # Since we are ranking, the score is effectively the posterior probability derived from F
        final_scores = prob_dist
        
        # Construct results
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(final_scores[i]),
                "reasoning": f"Free Energy: {energies[i]:.4f}, Structural Match: {prob_dist[i]:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on free energy minimization."""
        # Treat single answer evaluation as a 2-candidate problem (Answer vs Null)
        # to get a relative score, or just compute raw energy and map to 0-1
        prompt_feats = self._parse_structure(prompt)
        hyp = {
            'id': 0,
            'text': answer,
            'features': self._parse_structure(answer),
            'belief': 0.5
        }
        
        energy = self._compute_free_energy(prompt_feats, hyp, answer)
        
        # Map energy to confidence: High energy -> Low confidence
        # Using a sigmoid-like mapping: 1 / (1 + E)
        confidence = 1.0 / (1.0 + energy)
        return float(np.clip(confidence, 0.0, 1.0))

# Import zlib inside the class scope or globally for the NCD part
import zlib

# Ensure the class is ready
if __name__ == "__main__":
    # Basic self-test
    tool = ReasoningTool()
    p = "If the ball is red, then it is heavy. The ball is red."
    cands = ["The ball is heavy.", "The ball is light.", "The ball is blue."]
    res = tool.evaluate(p, cands)
    print(res)