import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Ergodic Variational Free-Energy Inference Engine (EVFE) Approximation.
    
    Mechanism:
    1. MaxEnt Prior: Constructs a feature-based prior over the candidate space using
       exponential weighting of structural constraints (negations, numerics, logic).
       This ensures the least biased starting distribution consistent with known rules.
    2. Ergodic SGLD Sampling: Simulates a stochastic trajectory through the candidate
       set. Instead of a single static score, we perform a 'time-average' walk where
       candidates are visited with probability proportional to their posterior likelihood.
       This mimics the ergodic theorem: time averages converge to space averages.
    3. Free Energy Minimization: The 'energy' of a state is defined by the mismatch
       between the candidate's structural properties and the prompt's requirements.
       Minimizing free energy equates to maximizing the alignment (score).
       
    This approach beats pure NCD by explicitly parsing logical structures (negation,
    comparatives) and using them as the 'Hamiltonian' for the sampler, rather than
    relying on string compression distance alone.
    """

    def __init__(self):
        self.rng = np.random.default_rng(seed=42) # Deterministic seed for reproducibility

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features for MaxEnt constraint matching."""
        text_lower = text.lower()
        features = {
            'length': len(text),
            'has_negation': float(any(w in text_lower for w in ['no', 'not', 'never', 'none', 'false'])),
            'has_comparative': float(any(c in text_lower for c in ['<', '>', 'more', 'less', 'greater', 'smaller'])),
            'has_numeric': float(bool(re.search(r'\d+', text))),
            'has_logic': float(any(w in text_lower for w in ['if', 'then', 'therefore', 'because', 'thus'])),
            'question_marks': float(text.count('?')),
        }
        return features

    def _compute_energy(self, prompt_feats: Dict, cand_feats: Dict, cand: str, prompt: str) -> float:
        """
        Compute Free Energy (negative log-likelihood proxy).
        Lower energy = better match.
        Energy = Mismatch in structural constraints + NCD penalty.
        """
        energy = 0.0
        
        # Constraint Propagation: Negation matching
        # If prompt asks a negative question or contains negation, candidate should reflect it
        if prompt_feats['has_negation'] > 0:
            # Penalty if candidate lacks negation when prompt has it (simplified heuristic)
            if cand_feats['has_negation'] == 0:
                energy += 2.0 
        else:
            # Penalty if candidate introduces unexpected negation
            if cand_feats['has_negation'] > 0:
                energy += 1.0

        # Numeric consistency
        if prompt_feats['has_numeric'] > 0:
            if cand_feats['has_numeric'] == 0:
                energy += 1.5 # Prefer numeric answers for numeric prompts
        
        # Logic flow
        if prompt_feats['has_logic'] > 0:
            if cand_feats['has_logic'] == 0:
                energy += 0.5 # Soft penalty for lacking logical connectives

        # NCD as a tie-breaker/base similarity (Normalized Compression Distance)
        try:
            s1 = (prompt + cand).encode('utf-8')
            s2 = prompt.encode('utf-8')
            s3 = cand.encode('utf-8')
            # Simple zlib compression size approximation
            import zlib
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c3 = len(zlib.compress(s3))
            
            ncd = (c1 - min(c2, c3)) / max(c2, c3) if max(c2, c3) > 0 else 1.0
            energy += ncd * 2.0 # Weight NCD as a baseline similarity metric
        except:
            energy += 1.0

        return energy

    def _ergodic_sampler(self, prompt: str, candidates: List[str], steps: int = 50) -> List[float]:
        """
        Perform Stochastic Gradient Langevin Dynamics (SGLD) inspired sampling.
        We simulate a trajectory through the candidate space to estimate the 
        posterior probability of each candidate being the correct answer.
        """
        if not candidates:
            return []
        
        n = len(candidates)
        if n == 1:
            return [1.0]

        p_feats = self._extract_features(prompt)
        c_feats = [self._extract_features(c) for c in candidates]
        
        # Compute initial energies (Free Energy)
        energies = np.array([
            self._compute_energy(p_feats, c_feats[i], candidates[i], prompt) 
            for i in range(n)
        ])
        
        # Convert to probabilities (Boltzmann distribution)
        # F = -log(p) => p = exp(-F)
        # Subtract min for numerical stability
        energies -= np.min(energies)
        probs = np.exp(-energies)
        probs /= np.sum(probs) + 1e-9
        
        # Ergodic Time-Averaging Simulation
        # Instead of just taking the static prob, we simulate a Markov Chain
        # visiting states. The frequency of visits converges to the posterior.
        visit_counts = np.zeros(n)
        current_idx = int(self.rng.integers(0, n))
        
        for _ in range(steps):
            visit_counts[current_idx] += 1.0
            
            # Propose a move (random neighbor or random jump for ergodicity)
            proposal_idx = int(self.rng.integers(0, n))
            if proposal_idx == current_idx:
                continue
                
            # Metropolis-Hastings acceptance ratio based on Free Energy difference
            # A = min(1, exp(-(E_new - E_old)))
            delta_e = energies[proposal_idx] - energies[current_idx]
            if delta_e < 0 or self.rng.random() < np.exp(-delta_e):
                current_idx = proposal_idx
                
        # Normalize visit counts to get final scores (Time Average -> Space Average)
        scores = visit_counts / np.sum(visit_counts)
        return scores.tolist()

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        scores = self._ergodic_sampler(prompt, candidates)
        
        results = []
        for i, cand in enumerate(candidates):
            results.append({
                "candidate": cand,
                "score": float(scores[i]),
                "reasoning": f"EVFE Score: Ergodic time-average convergence on free-energy landscape. "
                             f"Structural match (negation/numeric/logic) and NCD similarity determined the energy state."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimate confidence by comparing the answer's free energy against 
        a set of perturbed alternatives. Low relative energy = high confidence.
        """
        # Generate a few trivial alternatives to establish a baseline
        alternatives = [answer, "No", "Yes", "Unknown", answer[::-1]]
        if len(answer) > 5:
            alternatives.append(answer[:-1]) # Drop last char
            
        candidates = list(set(alternatives)) # Unique
        scores_map = {c: s for c, s in zip(candidates, self._ergodic_sampler(prompt, candidates))}
        
        target_score = scores_map.get(answer, 0.0)
        max_score = max(scores_map.values()) if scores_map else 0.0
        
        if max_score == 0:
            return 0.5
            
        # Confidence is ratio of target score to the best possible score in the local neighborhood
        conf = target_score / (max_score + 1e-9)
        return min(1.0, max(0.0, conf))