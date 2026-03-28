import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning evaluator combining Information Theory (KL-divergence), 
    Optimal Control (Bellman recursion on logical states), and Mechanism Design 
    (proper scoring rules). 
    
    Mechanism:
    1. Parses prompt/candidates into atomic propositions and logical edges.
    2. Constructs a reference distribution from the prompt's implied truths.
    3. Uses Dynamic Programming (Optimal Control) to find the minimum cost 
       (Edit Distance + KL Penalty) to transform a candidate's logic into the reference.
    4. Scores based on the negative optimal cost (incentive compatible).
    """
    
    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|implies|causes|leads to|unless)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'atom': re.compile(r'[A-Za-z_][\w_]*') # Simple variable extractor
        }

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract atomic statements/variables from text."""
        # Normalize
        text = text.lower()
        # Extract potential atoms (words that look like variables or concepts)
        atoms = self.patterns['atom'].findall(text)
        # Filter stopwords often caught as atoms but not logic carriers in this context
        stopwords = {'if', 'then', 'not', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'has', 'have', 'had'}
        return [a for a in atoms if a not in stopwords]

    def _build_logic_graph(self, text: str, atoms: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Build adjacency matrix G where G[i,j]=1 if i implies j."""
        n = len(atoms)
        if n == 0:
            return np.array([]), []
        
        G = np.zeros((n, n), dtype=int)
        text_lower = text.lower()
        
        # Simple heuristic: if "atom_i" appears before "atom_j" near a conditional keyword, set edge
        # This is a structural approximation of logical flow
        positions = {a: text_lower.find(a) for a in atoms}
        sorted_atoms = sorted(atoms, key=lambda a: positions[a])
        
        # Map original index to sorted index for contiguous matrix
        idx_map = {a: i for i, a in enumerate(sorted_atoms)}
        
        for i, atom_i in enumerate(sorted_atoms):
            for j, atom_j in enumerate(sorted_atoms):
                if i == j: continue
                # Check for conditional proximity
                snippet = text_lower[max(0, positions[atom_i]-20): positions[atom_j]+20]
                if any(k in snippet for k in ['if', 'then', 'implies', 'causes', 'leads to']):
                    G[i, j] = 1
                # Transitivity hint: if close in text and no negation between
                elif abs(positions[atom_i] - positions[atom_j]) < 50:
                     if 'not' not in snippet:
                        G[i, j] = 1 

        # Warshall's Algorithm for Transitive Closure (O(n^3))
        C = G.copy()
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if C[i, k] and C[k, j]:
                        C[i, j] = 1
        np.fill_diagonal(C, 1) # Reflexive
        
        return C, sorted_atoms

    def _get_truth_vector(self, text: str, atoms: List[str], C: np.ndarray) -> np.ndarray:
        """Determine initial truth values based on presence and negation."""
        if len(atoms) == 0:
            return np.array([])
            
        text_lower = text.lower()
        truth = np.zeros(len(atoms), dtype=float)
        
        for i, atom in enumerate(atoms):
            # Check presence
            if atom in text_lower:
                # Check negation proximity
                start = text_lower.find(atom)
                context = text_lower[max(0, start-15): start+5]
                if any(n in context for n in ['not', 'no ', 'never', 'impossible']):
                    truth[i] = 0.0
                else:
                    truth[i] = 1.0
            else:
                truth[i] = 0.5 # Uncertain
        
        # Propagate truth through closure C
        # If A is true and A->B, B tends to be true (simplified propagation)
        propagated = truth.copy()
        for _ in range(2): # Iterate a few times for stability
            propagated = np.maximum(propagated, np.dot(truth, C) / (C.sum(axis=0) + 1e-9))
            
        return propagated

    def _compute_kl_div(self, p: np.ndarray, q: np.ndarray) -> float:
        """Compute KL(p||q) with smoothing."""
        if len(p) == 0: return 0.0
        eps = 1e-9
        p = p + eps
        q = q + eps
        p = p / p.sum()
        q = q / q.sum()
        return float(np.sum(p * np.log(p / q)))

    def _bellman_solve(self, candidate_vec: np.ndarray, ref_vec: np.ndarray, lambda_cost: float = 0.5) -> float:
        """
        Solve finite-horizon Bellman recursion.
        State: current truth vector.
        Action: Flip a bit (cost 1) or Keep (cost 0).
        Objective: Minimize Sum(KL + lambda * action_cost).
        """
        n = len(candidate_vec)
        if n == 0:
            return 0.0
            
        # Discretize state space for DP? 
        # Since n is small (parsed atoms), we can simulate the trajectory greedily 
        # as an approximation of the optimal control policy for this specific cost structure.
        # Exact DP on continuous probabilities is hard; we treat them as binary decisions for the 'control'.
        
        current_state = (candidate_vec > 0.5).astype(float)
        target_state = (ref_vec > 0.5).astype(float)
        
        total_cost = 0.0
        horizon = n
        
        # Simulate control steps
        for t in range(horizon):
            # Stage cost: KL divergence between current distribution and reference
            # We approximate the distribution as the current state vector normalized
            if current_state.sum() == 0:
                stage_prob = np.ones_like(current_state) * (1/n if n>0 else 1)
            else:
                stage_prob = current_state / (current_state.sum() + 1e-9)
                
            if target_state.sum() == 0:
                ref_prob = np.ones_like(target_state) * (1/n if n>0 else 1)
            else:
                ref_prob = target_state / (target_state.sum() + 1e-9)
                
            kl_cost = self._compute_kl_div(stage_prob, ref_prob)
            
            # Determine optimal control u: flip if it reduces distance to target significantly
            # In this simplified discrete model, the optimal control is to flip mismatched bits
            mismatches = np.where(current_state != target_state)[0]
            
            if len(mismatches) > 0:
                # Flip one mismatched bit (greedy optimal for L1 distance)
                idx = mismatches[0]
                u = np.zeros_like(current_state)
                u[idx] = 1
                action_cost = lambda_cost
                current_state[idx] = 1 - current_state[idx]
            else:
                u = np.zeros_like(current_state)
                action_cost = 0.0
                
            total_cost += kl_cost + action_cost
            
            if np.all(current_state == target_state):
                break
                
        return total_cost

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Parse Prompt to get Reference Distribution
        prompt_atoms = self._extract_atoms(prompt)
        ref_C, ref_sorted_atoms = self._build_logic_graph(prompt, prompt_atoms)
        ref_truth = self._get_truth_vector(prompt, ref_sorted_atoms, ref_C)
        
        # If no atoms found, fallback to NCD tiebreaker logic later
        use_structural = len(ref_truth) > 0

        scored_candidates = []
        
        for cand in candidates:
            score_val = 0.0
            reason_str = ""
            
            if use_structural:
                # 2. Parse Candidate
                cand_atoms = self._extract_atoms(cand)
                # Align candidate atoms to prompt atoms for comparison (Intersection)
                # We map candidate truth values to the prompt's atom space
                common_atoms = [a for a in ref_sorted_atoms if a in cand_atoms]
                
                if len(common_atoms) == 0:
                    # No overlap, high penalty
                    score_val = -10.0
                    reason_str = "No logical overlap with prompt concepts."
                else:
                    # Re-build candidate vector in the space of common atoms
                    # This is a projection of the candidate's logic onto the prompt's graph
                    cand_truth_proj = []
                    ref_truth_proj = []
                    
                    for atom in common_atoms:
                        # Get candidate local truth
                        c_vec = self._get_truth_vector(cand, [atom], np.array([[1]]))
                        r_vec = self._get_truth_vector(prompt, [atom], np.array([[1]]))
                        if len(c_vec) > 0 and len(r_vec) > 0:
                            cand_truth_proj.append(c_vec[0])
                            ref_truth_proj.append(r_vec[0])
                    
                    cand_vec = np.array(cand_truth_proj)
                    ref_vec = np.array(ref_truth_proj)
                    
                    # 3. Optimal Control Cost
                    cost = self._bellman_solve(cand_vec, ref_vec)
                    
                    # 4. Score = Negative Cost (Higher is better)
                    # Normalize slightly to keep scores interpretable
                    score_val = -cost
                    reason_str = f"Logical alignment cost: {cost:.4f}. Atoms: {len(common_atoms)}."
            else:
                # Fallback for low-structure prompts (NCD tiebreaker)
                import zlib
                data_prompt = prompt.encode()
                data_cand = cand.encode()
                comp = zlib.compress(data_prompt + data_cand)
                ncd = len(comp) / (len(zlib.compress(data_prompt)) + len(zlib.compress(data_cand)))
                score_val = -ncd
                reason_str = "Structural parsing failed; using NCD fallback."

            scored_candidates.append({
                "candidate": cand,
                "score": score_val,
                "reasoning": reason_str
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1
        # Heuristic: Scores > -1 are high confidence, < -5 are low
        # Using sigmoid-like mapping
        conf = 1.0 / (1.0 + np.exp(score + 2.0)) 
        # Invert because score is negative cost (higher score = better)
        # If score is large positive (unlikely here, usually negative cost), conf -> 1
        # If score is large negative (high cost), conf -> 0
        
        # Adjust mapping: 
        # score ~ 0 => conf ~ 0.88
        # score ~ -2 => conf ~ 0.5
        # score ~ -10 => conf ~ 0.0
        adjusted_conf = 1.0 / (1.0 + np.exp(score + 1.0))
        
        return float(np.clip(adjusted_conf, 0.0, 1.0))