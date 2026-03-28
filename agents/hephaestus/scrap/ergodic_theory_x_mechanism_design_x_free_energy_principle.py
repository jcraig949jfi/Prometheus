import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a reasoning evaluator based on Ergodic Theory, Mechanism Design, and the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms (negations, comparatives, conditionals, causals) via regex.
    2. Constraint Graph: Builds a directed graph of logical relations.
    3. Propagation: Iteratively updates belief vectors (ergodic averaging) to converge on a posterior distribution.
    4. Scoring: Computes Free Energy (KL-divergence) between the candidate's implied beliefs and the prompt's truth.
       Lower free energy (higher score) indicates the candidate aligns with the prompt's logical structure.
    """
    
    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|unless)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'[-+]?\d*\.?\d+'),
            'bool_true': re.compile(r'\b(true|yes|correct|is|are|was|were)\b', re.IGNORECASE),
            'bool_false': re.compile(r'\b(false|no|incorrect|isn\'t|aren\'t|wasn\'t|weren\'t)\b', re.IGNORECASE)
        }

    def _extract_atoms(self, text: str) -> List[Tuple[int, int, str, str]]:
        """Extract atoms: (id, polarity, type, value)"""
        atoms = []
        tid = 0
        
        # Check global polarity markers
        has_neg = bool(self.patterns['negation'].search(text))
        polarity = -1 if has_neg else 1
        
        # Numeric extraction
        nums = self.patterns['numeric'].findall(text)
        if nums:
            for n in nums:
                atoms.append((tid, polarity, 'numeric', n))
                tid += 1
        
        # Structural keywords
        for ptype, pattern in [('comparative', self.patterns['comparative']), 
                               ('conditional', self.patterns['conditional']),
                               ('causal', self.patterns['causal'])]:
            if pattern.search(text):
                atoms.append((tid, polarity, ptype, pattern.search(text).group(0)))
                tid += 1
                
        # Boolean assertions
        if self.patterns['bool_true'].search(text):
            atoms.append((tid, 1, 'categorical', 'TRUE'))
            tid += 1
        if self.patterns['bool_false'].search(text):
            atoms.append((tid, -1, 'categorical', 'FALSE'))
            tid += 1
            
        # Fallback if nothing specific found
        if not atoms:
            atoms.append((0, polarity, 'categorical', text[:20]))
            
        return atoms

    def _build_graph(self, atoms: List) -> Dict[int, List[int]]:
        """Build adjacency list for constraint propagation."""
        graph = {a[0]: [] for a in atoms}
        # Simple transitivity/heuristic edges based on order and type
        for i, atom in enumerate(atoms):
            aid, pol, atype, val = atom
            # Connect to next atom (sequential logic)
            if i < len(atoms) - 1:
                next_id = atoms[i+1][0]
                graph[aid].append(next_id)
            # Causal/Conditional specific: stronger forward link
            if atype in ['causal', 'conditional']:
                if i < len(atoms) - 1:
                    # Ensure edge exists
                    if next_id not in graph[aid]:
                        graph[aid].append(next_id)
        return graph

    def _propagate(self, atoms: List, graph: Dict, initial_beliefs: np.ndarray) -> np.ndarray:
        """Ergodic propagation of beliefs until convergence."""
        if len(atoms) == 0:
            return initial_beliefs
            
        b = initial_beliefs.copy()
        n = len(b)
        if n == 0: return b
        
        # Map atom id to index
        id_to_idx = {a[0]: i for i, a in enumerate(atoms)}
        
        for _ in range(50): # Max iterations for ergodic convergence
            b_new = b.copy()
            changed = False
            for u_id, neighbors in graph.items():
                if u_id not in id_to_idx: continue
                u_idx = id_to_idx[u_id]
                u_val = b[u_idx]
                
                for v_id in neighbors:
                    if v_id not in id_to_idx: continue
                    v_idx = id_to_idx[v_id]
                    
                    # Modus ponens / Noisy-OR approximation
                    # If u is true, v becomes more likely. If u is false, v is uncertain.
                    # Simple diffusion: b[v] = max(b[v], b[u] * weight)
                    weight = 0.9 if atoms[u_idx][2] in ['causal', 'conditional'] else 0.5
                    propagated = u_val * weight
                    if propagated > b_new[v_idx]:
                        b_new[v_idx] = propagated
                        changed = True
            
            if not changed:
                break
            b = b_new
            
        return b

    def _get_reference_distribution(self, prompt_atoms: List) -> np.ndarray:
        """Derive the 'true' distribution from the prompt structure."""
        if not prompt_atoms:
            return np.array([0.5])
        
        # Assume prompt assertions are initially true (1.0) unless negated
        beliefs = []
        for atom in prompt_atoms:
            _, pol, atype, _ = atom
            # Base belief on polarity
            val = 1.0 if pol == 1 else 0.1 
            beliefs.append(val)
        
        return np.array(beliefs) if beliefs else np.array([0.5])

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Compute score based on Free Energy (KL Divergence)."""
        p_atoms = self._extract_atoms(prompt)
        c_atoms = self._extract_atoms(candidate)
        
        # If no structure, rely on NCD tiebreaker logic (simplified here as length match + keyword overlap)
        if not p_atoms or not c_atoms:
            # Fallback for empty parses
            p_low = prompt.lower()
            c_low = candidate.lower()
            if p_low == c_low: return 1.0
            # Simple overlap
            common = len(set(p_low.split()) & set(c_low.split()))
            return common / (len(set(p_low.split())) + 1) * 0.5

        # Build graphs
        p_graph = self._build_graph(p_atoms)
        c_graph = self._build_graph(c_atoms)
        
        # Initial beliefs: Prompt is ground truth (1.0 for positive, 0.0 for negative)
        # Candidate starts with its own polarity, then we see how well it matches prompt propagation
        r_init = np.array([1.0 if a[1] == 1 else 0.0 for a in p_atoms])
        b_init = np.array([1.0 if a[1] == 1 else 0.0 for a in c_atoms])
        
        # Propagate prompt truths (Reference distribution r)
        # We propagate the prompt's own logic to see what implies what
        r_dist = self._propagate(p_atoms, p_graph, r_init)
        
        # Propagate candidate's logic
        # To compare, we need same dimensionality. 
        # Strategy: Map candidate atoms to prompt atoms by type similarity or just compare aggregate statistics
        # Rigorous approach: Project candidate beliefs onto prompt structure.
        # Simplified for robustness: Compare the "energy" of the candidate relative to prompt constraints.
        
        if len(r_dist) == 0 or len(b_init) == 0:
            return 0.0

        # Resize/Interpolate to match lengths for KL divergence
        # We treat the prompt's propagated beliefs as the "True" distribution P
        # We treat the candidate's propagated beliefs as Q, mapped to P's space
        
        # Mapping strategy: If types match, map. Else, uniform penalty.
        m = len(r_dist)
        n = len(b_init)
        
        # Resample candidate beliefs to match prompt length (Ergodic assumption: time avg = space avg)
        if n > 0:
            indices = np.linspace(0, n-1, m).astype(int)
            # Clamp indices
            indices = np.clip(indices, 0, n-1)
            b_mapped = b_init[indices]
        else:
            b_mapped = np.ones(m) * 0.5
            
        # Add small epsilon to avoid log(0)
        eps = 1e-10
        p_norm = r_dist + eps
        q_norm = b_mapped + eps
        
        # Normalize to probability distributions
        p_norm /= np.sum(p_norm)
        q_norm /= np.sum(q_norm)
        
        # KL Divergence: Sum(P * log(P/Q))
        # Free Energy minimization -> Minimize KL -> Maximize Score
        kl_div = np.sum(p_norm * np.log(p_norm / q_norm))
        
        # Convert to score: Higher is better. 
        # KL is 0 if identical. Large if different.
        # Score = -KL (bounded roughly -inf to 0). 
        # Transform to 0-1 range: exp(-KL)
        score = np.exp(-kl_div)
        
        return float(score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free-energy score based on structural alignment and constraint propagation."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        score = self._compute_score(prompt, answer)
        # Normalize score to 0-1 range more aggressively for confidence
        # Scores near 1.0 are high confidence, < 0.2 low.
        conf = max(0.0, min(1.0, score))
        return conf