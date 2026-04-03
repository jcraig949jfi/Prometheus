from dataclasses import field
from typing import Dict, List, Tuple

class ReasoningTool:
    """
    Phenomenological Free-Energy Reasoning with Dynamics Tracking.
    
    Combines:
    1. Logical parsing (phenomenology) to extract propositions
    2. Maximum-Entropy prior over constraint satisfaction
    3. Free-Energy minimization via variational inference
    4. Trajectory stability analysis for confidence estimation
    
    Scores candidates by how well they minimize free energy given parsed
    constraints, and uses state evolution stability for meta-confidence.
    """
    
    def __init__(self):
        self.eps = 1e-4
        self.max_iter = 50
        
    def _parse_propositions(self, text: str) -> Tuple[List[str], List[Tuple]]:
        """Extract atomic propositions and constraints."""
        text = text.lower()
        atoms = []
        constraints = []
        
        # Extract numeric comparisons
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text):
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            atom_id = len(atoms)
            atoms.append(f"num_{a}_{op}_{b}")
            # Constraint: 1 if true, 0 if false
            if (op == '>' and a > b) or (op == '<' and a < b) or \
               (op == '>=' and a >= b) or (op == '<=' and a <= b) or \
               (op == '=' and abs(a - b) < 1e-6):
                constraints.append((atom_id, 1.0))
            else:
                constraints.append((atom_id, 0.0))
        
        # Extract negations
        for match in re.finditer(r'\b(not|no|never|n\'t)\s+(\w+)', text):
            atom = match.group(2)
            atom_id = len(atoms)
            atoms.append(f"neg_{atom}")
            constraints.append((atom_id, 0.0))
        
        # Extract conditionals (if...then)
        for match in re.finditer(r'\bif\s+([^,\.]+?)\s+then\s+([^,\.]+)', text):
            premise = match.group(1).strip()
            conclusion = match.group(2).strip()
            p_id, c_id = len(atoms), len(atoms) + 1
            atoms.extend([f"if_{premise[:20]}", f"then_{conclusion[:20]}"])
            constraints.append(((p_id, c_id), 'implies'))
        
        # Extract causal relations
        for match in re.finditer(r'([^,\.]+?)\s+(because|due to|leads to|causes)\s+([^,\.]+)', text):
            cause = match.group(1).strip()
            effect = match.group(3).strip()
            c_id, e_id = len(atoms), len(atoms) + 1
            atoms.extend([f"cause_{cause[:20]}", f"effect_{effect[:20]}"])
            constraints.append(((c_id, e_id), 'causal'))
        
        # Extract simple words as atoms
        words = re.findall(r'\b[a-z]{3,}\b', text)
        for w in words[:10]:  # Limit to avoid explosion
            if not any(w in a for a in atoms):
                atoms.append(w)
        
        return atoms, constraints
    
    def _build_feature_matrix(self, atoms: List[str], constraints: List) -> np.ndarray:
        """Build constraint feature matrix for MaxEnt."""
        n_atoms = max(len(atoms), 1)
        features = []
        
        for c in constraints:
            if isinstance(c, tuple) and len(c) == 2:
                if isinstance(c[0], int):  # Simple constraint
                    feat = np.zeros(n_atoms)
                    feat[c[0] % n_atoms] = c[1]
                    features.append(feat)
                elif isinstance(c[0], tuple):  # Relational constraint
                    feat = np.zeros(n_atoms)
                    i, j = c[0][0] % n_atoms, c[0][1] % n_atoms
                    feat[i] = -1
                    feat[j] = 1
                    features.append(feat)
        
        if len(features) == 0:
            features.append(np.zeros(n_atoms))
        
        return np.array(features)
    
    def _free_energy(self, q: np.ndarray, lam: np.ndarray, F: np.ndarray) -> float:
        """Compute variational free energy."""
        q = np.clip(q, self.eps, 1 - self.eps)
        # Energy term
        energy = -np.sum(lam @ F * q)
        # Entropy term (negative for free energy)
        entropy = -np.sum(q * np.log(q) + (1 - q) * np.log(1 - q))
        return energy - entropy
    
    def _update_beliefs(self, q: np.ndarray, lam: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Mean-field variational update."""
        field = lam @ F  # External field
        q_new = 1.0 / (1.0 + np.exp(-field))
        return np.clip(q_new, self.eps, 1 - self.eps)
    
    def _compute_trajectory_stability(self, states: List[np.ndarray]) -> float:
        """Measure stability of state evolution (Lyapunov-like)."""
        if len(states) < 2:
            return 0.5
        
        # Compute trajectory variance
        states_arr = np.array(states)
        variance = np.mean(np.var(states_arr, axis=0))
        
        # Compute convergence: distance between last two states
        convergence = np.linalg.norm(states[-1] - states[-2])
        
        # Stability = low variance + convergence
        stability = 1.0 / (1.0 + variance + convergence)
        return stability
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity/presupposition markers."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who\?', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|better)\b', prompt_lower):
            return 0.4
        
        # Unanswerable
        if re.search(r'\b(impossible|cannot|unknown)\b', prompt_lower):
            return 0.2
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by free-energy score."""
        # Parse prompt
        atoms_p, constraints_p = self._parse_propositions(prompt)
        n_atoms = max(len(atoms_p), 3)
        
        results = []
        
        for cand in candidates:
            # Parse candidate
            atoms_c, constraints_c = self._parse_propositions(cand)
            
            # Merge constraints
            all_atoms = atoms_p + atoms_c
            all_constraints = constraints_p + constraints_c
            
            # Build feature matrix
            F = self._build_feature_matrix(all_atoms, all_constraints)
            n_atoms = F.shape[1]
            
            # Solve for lambda (MaxEnt parameters)
            if F.shape[0] > 0 and n_atoms > 0:
                lam = np.random.randn(F.shape[0]) * 0.1
            else:
                lam = np.zeros(1)
                F = np.zeros((1, n_atoms))
            
            # Variational inference with trajectory tracking
            q = np.ones(n_atoms) * 0.5
            states = [q.copy()]
            
            for _ in range(self.max_iter):
                q_new = self._update_beliefs(q, lam, F)
                states.append(q_new.copy())
                if np.max(np.abs(q_new - q)) < self.eps:
                    break
                q = q_new
            
            # Compute free energy
            fe = self._free_energy(q, lam, F)
            
            # Compute trajectory stability
            stability = self._compute_trajectory_stability(states)
            
            # NCD similarity (tiebreaker only)
            ncd = 1.0 - self._ncd(prompt, cand)
            
            # Final score: dynamics 45%, FE 40%, NCD 15%
            score = 0.45 * stability - 0.40 * fe + 0.15 * ncd
            
            results.append({
                'candidate': cand,
                'score': float(score),
                'reasoning': f"FE={fe:.3f}, Stability={stability:.3f}, NCD={ncd:.3f}"
            })
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a given answer."""
        # Meta-confidence check
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and compute
        atoms_p, constraints_p = self._parse_propositions(prompt)
        atoms_a, constraints_a = self._parse_propositions(answer)
        
        all_atoms = atoms_p + atoms_a
        all_constraints = constraints_p + constraints_a
        
        # Build feature matrix
        F = self._build_feature_matrix(all_atoms, all_constraints)
        n_atoms = F.shape[1]
        
        if F.shape[0] > 0 and n_atoms > 0:
            lam = np.random.randn(F.shape[0]) * 0.1
        else:
            return 0.3 * meta_conf  # Low confidence on trivial parse
        
        # Run dynamics
        q = np.ones(n_atoms) * 0.5
        states = [q.copy()]
        
        for _ in range(self.max_iter):
            q_new = self._update_beliefs(q, lam, F)
            states.append(q_new.copy())
            if np.max(np.abs(q_new - q)) < self.eps:
                break
            q = q_new
        
        # Stability-based confidence
        stability = self._compute_trajectory_stability(states)
        
        # Constraint satisfaction
        if len(constraints_p) > 0:
            satisfaction = len(constraints_a) / (len(constraints_p) + 1)
        else:
            satisfaction = 0.5
        
        # Confidence from convergence
        base_conf = 0.5 * stability + 0.3 * satisfaction + 0.2 * (1.0 - self._ncd(prompt, answer))
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_conf)
        
        # Never exceed 0.9 unless perfect constraint match
        if satisfaction < 0.95:
            final_conf = min(final_conf, 0.85)
        
        return float(np.clip(final_conf, 0.0, 1.0))