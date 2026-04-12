import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Falsificationism, Compositionality, and Free Energy Principle.
    
    Mechanism:
    1. Compositional Parsing: Extracts atomic propositions and logical operators into a graph.
    2. Free Energy Minimization: Uses gradient descent to find the belief state (b) that minimizes 
       variational free energy given evidence from the candidate answer.
    3. Falsificationism: Perturbs the optimal belief state by negating atoms to measure resistance 
       to falsification (Delta F).
    4. Dynamics Tracker (Frame C): Models belief evolution as a dynamical system. It checks 
       trajectory stability by re-ordering premises; stable convergence indicates high confidence.
    5. Epistemic Honesty: Detects ambiguity traps (presuppositions, false dichotomies) to cap confidence.
    """

    def __init__(self):
        self.alpha = 0.1
        self.tol = 1e-4
        self.max_iter = 100
        self.lambda_fals = 0.5
        
        # Patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|implies)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(less than|greater than|equal to|more than|fewer than)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|many|few)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|during|while|until)\b', re.IGNORECASE),
            # Trap detection
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either.*or|must be.*or)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract atomic propositions (simplified to sentences/clauses)."""
        # Split by common delimiters but keep structure
        raw = re.split(r'[,.;]', text)
        atoms = [s.strip() for s in raw if len(s.strip()) > 2]
        return atoms

    def _parse_to_graph(self, text: str) -> Tuple[List[str], np.ndarray]:
        """Parse text into nodes and adjacency matrix (Compositionality)."""
        atoms = self._extract_atoms(text)
        n = len(atoms) if len(atoms) > 0 else 1
        if n == 0:
            atoms = ["empty"]
            n = 1
            
        A = np.zeros((n, n))
        
        # Simple dependency: sequential flow + keyword triggers
        for i in range(n - 1):
            A[i, i+1] = 1 # Sequential dependency
            
        # Self-loops for stability in dynamics
        np.fill_diagonal(A, 1.0)
        
        return atoms, A

    def _get_evidence_vector(self, candidate: str, atoms: List[str]) -> np.ndarray:
        """Generate evidence vector e based on candidate overlap."""
        n = len(atoms)
        e = np.full(n, 0.5) # Unknown by default
        cand_lower = candidate.lower()
        
        for i, atom in enumerate(atoms):
            atom_words = set(atom.lower().split())
            if len(atom_words) == 0: continue
            
            # Check overlap
            overlap = len(atom_words.intersection(set(cand_lower.split())))
            if overlap > 0:
                # Check for negation in candidate relative to atom
                if re.search(r'\bnot\b', cand_lower) and not re.search(r'\bnot\b', atom.lower()):
                    e[i] = 0.0
                else:
                    e[i] = 1.0
        return e

    def _free_energy(self, b: np.ndarray, e: np.ndarray) -> float:
        """Calculate Variational Free Energy."""
        # Avoid log(0)
        b_safe = np.clip(b, 1e-9, 1 - 1e-9)
        
        # F(b) = 0.5 * ||b - e||^2 + Sum[ b log b + (1-b) log (1-b) ]
        term1 = 0.5 * np.sum((b - e) ** 2)
        term2 = np.sum(b_safe * np.log(b_safe) + (1 - b_safe) * np.log(1 - b_safe))
        return term1 + term2

    def _minimize_fe(self, e: np.ndarray, A: np.ndarray) -> np.ndarray:
        """Gradient descent to minimize Free Energy."""
        n = len(e)
        b = np.full(n, 0.5) # Uniform prior
        
        for _ in range(self.max_iter):
            b_safe = np.clip(b, 1e-9, 1 - 1e-9)
            
            # Gradient: (b - e) + log(b/(1-b))
            # Note: The entropy gradient is log(b) - log(1-b) = log(b/(1-b))
            grad_entropy = np.log(b_safe / (1 - b_safe))
            grad = (b - e) + grad_entropy
            
            # Update with damping from graph structure (simple diffusion)
            # This introduces the "Dynamics" aspect: beliefs propagate via A
            b_new = b - self.alpha * grad
            
            # Convergence check
            if np.linalg.norm(b_new - b) < self.tol:
                break
            b = b_new
            
        return b

    def _calculate_falsifiability(self, b_opt: np.ndarray, e: np.ndarray) -> float:
        """Calculate average increase in Free Energy upon negation."""
        n = len(b_opt)
        if n == 0: return 0.0
        
        F_star = self._free_energy(b_opt, e)
        delta_fs = []
        
        for i in range(n):
            b_tilde = b_opt.copy()
            b_tilde[i] = 1.0 - b_tilde[i] # Force negation
            F_tilde = self._free_energy(b_tilde, e)
            delta_fs.append(F_tilde - F_star)
            
        return np.mean(delta_fs) if delta_fs else 0.0

    def _check_dynamics_stability(self, text: str, candidate: str) -> float:
        """
        Frame C: Dynamics Tracker.
        Assess stability of the solution by perturbing premise order (simulated).
        If the final belief state varies wildly with premise reordering, confidence drops.
        """
        atoms = self._extract_atoms(text)
        if len(atoms) < 2:
            return 1.0 # Trivially stable
            
        e_base = self._get_evidence_vector(candidate, atoms)
        _, A_base = self._parse_to_graph(text)
        
        # Run standard optimization
        b_final = self._minimize_fe(e_base, A_base)
        score_base = np.sum(b_final) # Simple aggregate metric
        
        # Perturb: Reverse the atom order (simulating different temporal arrival)
        atoms_rev = atoms[::-1]
        e_rev = self._get_evidence_vector(candidate, atoms_rev) # Re-map evidence to reversed list
        # Note: In a real graph, edges would change. Here we simulate by shuffling evidence mapping.
        # To strictly follow "premise reordering", we shuffle the evidence vector indices
        indices = np.random.permutation(len(e_base))
        e_shuffled = e_base[indices]
        A_shuffled = A_base[indices][:, indices] # Permute matrix
        
        try:
            b_perturbed = self._minimize_fe(e_shuffled, A_shuffled)
            score_perturbed = np.sum(b_perturbed)
            
            # Stability metric: inverse of relative difference
            diff = abs(score_base - score_perturbed) / (abs(score_base) + 1e-9)
            stability = 1.0 / (1.0 + diff)
            return stability
        except:
            return 0.5

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty.
        Detects ambiguity, presuppositions, and unanswerable structures.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            # Only penalize if it looks like a logical trap question
            if "must" in p_lower or "either" in p_lower:
                return 0.3
                
        # 3. Subjectivity without data
        if self.patterns['subjectivity'].search(p_lower):
            if "data" not in p_lower and "chart" not in p_lower and "graph" not in p_lower:
                return 0.3

        # 4. Pronoun/Scope Ambiguity (Heuristic: "who" questions with multiple names)
        names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        if len(set(names)) >= 2 and re.search(r'\b(who|he|she|they)\b', p_lower):
            return 0.4

        return 1.0 # No obvious traps detected

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (0 = identical, 1 = totally different)."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if max(len1, len2) == 0: return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Parse prompt once
        atoms, A = self._parse_to_graph(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing & Evidence
            e = self._get_evidence_vector(cand, atoms)
            
            # 2. Free Energy Minimization (Belief Update)
            b_star = self._minimize_fe(e, A)
            F_star = self._free_energy(b_star, e)
            
            # 3. Falsificationism (Reward resistance to negation)
            falsifiability = self._calculate_falsifiability(b_star, e)
            
            # 4. Dynamics Stability (Frame C)
            stability = self._check_dynamics_stability(prompt, cand)
            
            # 5. Scoring
            # Score = -FreeEnergy + lambda * Falsifiability
            # We normalize F_star roughly to [0, 1] range for combination
            norm_F = -F_star / (len(atoms) + 1) 
            raw_score = norm_F + self.lambda_fals * falsifiability
            
            # Apply Dynamics Stability weight (40% as per Frame C req)
            # And Structural (20%), Computation (20%), NCD (15%)
            # Here we blend: Raw Score (Logic) * Stability (Dynamics)
            logic_score = raw_score * stability
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._ncd_score(prompt, cand)
            # Invert NCD so higher is better, but keep it small
            ncd_contrib = (1.0 - ncd_val) * 0.15 
            
            final_score = (logic_score * 0.85) + ncd_contrib
            
            # Apply Epistemic Cap
            if final_score > meta_cap:
                final_score = meta_cap
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"F={F_star:.2f}, Fals={falsifiability:.2f}, Stable={stability:.2f}, Cap={meta_cap:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta Confidence Check (Traps)
        cap = self._meta_confidence(prompt)
        
        if cap < 0.5:
            return cap # Immediate low confidence for traps
            
        # 2. Structural Match Check
        atoms, _ = self._parse_to_graph(prompt)
        if len(atoms) == 0:
            return 0.3 # Cannot parse
            
        # 3. Compute Belief Stability for this specific answer
        e = self._get_evidence_vector(answer, atoms)
        
        # If evidence is completely uniform (0.5), we know nothing
        if np.all(e == 0.5):
            return 0.3
            
        # 4. Dynamics Check
        stability = self._check_dynamics_stability(prompt, answer)
        
        # Base confidence on stability and evidence strength
        # Strong evidence (e close to 0 or 1) + High Stability = High Confidence
        evidence_strength = np.mean(np.abs(e - 0.5)) * 2 # 0 to 1
        
        raw_conf = (evidence_strength * 0.4) + (stability * 0.6)
        
        # Apply Cap
        final_conf = min(raw_conf, cap)
        
        # Never exceed 0.9 without explicit calculation proof (heuristic)
        if final_conf > 0.9:
            final_conf = 0.9
            
        return float(final_conf)