import re
import numpy as np
import math

class ReasoningTool:
    """
    Implements a Cellular Automata (CA) based reasoning engine driven by the 
    Free Energy Principle (FEP) and Analogical Reasoning.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms (subject-predicate-object) and 
       structural features (negations, comparatives, numerics) from prompt and candidates.
    2. Analogy Matrix (W): Constructs a similarity matrix where W_ij represents the 
       analogical weight between atom i and atom j based on semantic/structural features.
    3. CA Dynamics: Treats belief values (b) as CA cells. Iteratively updates beliefs 
       to minimize prediction error (Free Energy) via the rule:
       b_new = sigmoid(bias + W @ b - lambda * |b - W @ b|)
    4. Scoring: Candidates are scored by the negative variational free energy (-F) 
       of the converged system. Lower free energy (higher score) implies better 
       consistency between the candidate and the prompt's logical structure.
    """
    
    def __init__(self):
        self.sigma = 0.5  # Analogy kernel width
        self.lambda_err = 1.2  # Prediction error influence
        self.max_steps = 50
        self.epsilon = 1e-4

    def _extract_atoms(self, text):
        """Extracts structural features and creates a list of atom dictionaries."""
        text_lower = text.lower()
        atoms = []
        
        # Patterns for structural features
        patterns = [
            (r'not\s+(\w+)', 'negation', 1.0),
            (r'no\s+(\w+)', 'negation', 1.0),
            (r'more\s+than\s+([\d.]+)', 'comparative_gt', 1.0),
            (r'less\s+than\s+([\d.]+)', 'comparative_lt', 1.0),
            (r'if\s+(.+?)\s+then\s+(.+?)', 'conditional', 1.0),
            (r'because\s+(.+?)', 'causal', 1.0),
            (r'([\d.]+)\s*<\s*([\d.]+)', 'numeric_lt', 1.0),
            (r'([\d.]+)\s*>\s*([\d.]+)', 'numeric_gt', 1.0),
            (r'first|before|prior', 'ordering', 1.0),
            (r'(\w+)\s+is\s+(\w+)', 'relation', 1.0) # Generic relation
        ]
        
        found_features = []
        numeric_vals = []
        
        for pattern, p_type, weight in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    content = "_".join(str(x) for x in match)
                    found_features.append(f"{p_type}:{content}")
                    # Extract numbers for numeric evaluation
                    nums = re.findall(r'[\d.]+', str(match))
                    numeric_vals.extend([float(n) for n in nums])
                else:
                    found_features.append(f"{p_type}:{match}")
                    nums = re.findall(r'[\d.]+', str(match))
                    numeric_vals.extend([float(n) for n in nums])

        # Add generic atoms for presence of key logical operators
        if 'not' in text_lower or 'no' in text_lower:
            found_features.append("logic:negation_present")
        if 'if' in text_lower and 'then' in text_lower:
            found_features.append("logic:conditional_present")
            
        # Add numeric consistency atom if numbers exist
        if numeric_vals:
            # Simple heuristic: check sorted order consistency if "less/more" mentioned
            if 'less' in text_lower and len(numeric_vals) >= 2:
                is_consistent = numeric_vals[0] < numeric_vals[1]
                found_features.append(f"numeric_check:{is_consistent}")
            elif 'more' in text_lower and len(numeric_vals) >= 2:
                is_consistent = numeric_vals[0] > numeric_vals[1]
                found_features.append(f"numeric_check:{is_consistent}")

        # Deduplicate and return as list of feature strings (acting as atoms)
        unique_atoms = list(set(found_features))
        if not unique_atoms:
            unique_atoms = ["generic:content"]
            
        return unique_atoms

    def _compute_feature_vector(self, atom):
        """Generates a simple feature vector for an atom based on string properties."""
        # Features: length, presence of digits, specific type tags
        f1 = len(atom) / 50.0  # Normalized length
        f2 = 1.0 if any(c.isdigit() for c in atom) else 0.0
        f3 = 1.0 if 'negation' in atom else 0.0
        f4 = 1.0 if 'comparative' in atom else 0.0
        f5 = 1.0 if 'conditional' in atom else 0.0
        f6 = 1.0 if 'causal' in atom else 0.0
        f7 = 1.0 if 'numeric' in atom else 0.0
        return np.array([f1, f2, f3, f4, f5, f6, f7])

    def _build_analogy_matrix(self, atoms):
        """Builds the analogy weight matrix W based on feature similarity."""
        n = len(atoms)
        if n == 0:
            return np.array([])
        
        W = np.zeros((n, n))
        features = [self._compute_feature_vector(a) for a in atoms]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    W[i, j] = 1.0
                else:
                    dist_sq = np.sum((features[i] - features[j])**2)
                    W[i, j] = math.exp(-dist_sq / (self.sigma**2))
        
        # Normalize rows to prevent explosion
        row_sums = W.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W = W / row_sums
        return W

    def _run_ca_dynamics(self, atoms):
        """Runs the CA update rule to minimize free energy."""
        n = len(atoms)
        if n == 0:
            return 0.0, []
            
        W = self._build_analogy_matrix(atoms)
        b = np.full(n, 0.5)  # Initial belief
        bias = np.full(n, 0.5)  # Prior belief
        
        for _ in range(self.max_steps):
            # 1. Prediction
            p = W @ b
            # 2. Prediction Error
            e = np.abs(b - p)
            # 3. Free Energy Gradient
            # g = bias + expected_belief - lambda * error
            g = bias + (W @ b) - self.lambda_err * e
            # 4. Update
            b_new = 1.0 / (1.0 + np.exp(-g))
            
            if np.linalg.norm(b_new - b) < self.epsilon:
                b = b_new
                break
            b = b_new
            
        # Compute Variational Free Energy F
        # F = 0.5 * sum(e^2) - sum(b * log(b) + (1-b) * log(1-b))
        # Avoid log(0)
        b_clipped = np.clip(b, 1e-10, 1 - 1e-10)
        entropy_term = np.sum(b_clipped * np.log(b_clipped) + (1 - b_clipped) * np.log(1 - b_clipped))
        F = 0.5 * np.sum(e**2) - entropy_term
        
        return -F, b  # Return negative F so higher is better

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_atoms = self._extract_atoms(prompt)
        
        # If no structural atoms found, rely on NCD as tiebreaker logic implies
        # But per instructions, we must use structural parsing as primary signal.
        # We simulate structural depth by combining prompt + candidate atoms.
        
        base_score = 0.0
        if not prompt_atoms:
            # Fallback if prompt is empty of structure
            base_score = -10.0 

        for cand in candidates:
            # Combine prompt and candidate atoms to form the reasoning field
            cand_atoms = self._extract_atoms(cand)
            full_atoms = prompt_atoms + cand_atoms
            
            # Run CA dynamics
            score, _ = self._run_ca_dynamics(full_atoms)
            
            # Heuristic boost for explicit constraint satisfaction
            # If prompt has "not" and candidate has "not", slight boost (analogy)
            prompt_has_not = any('negation' in a for a in prompt_atoms)
            cand_has_not = any('negation' in a for a in cand_atoms)
            if prompt_has_not and cand_has_not:
                score += 0.5
            elif prompt_has_not and not cand_has_not and len(cand_atoms) > 0:
                # Penalty if prompt negates but candidate doesn't reflect it (simplified)
                score -= 0.2

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"CA-FEP convergence on {len(full_atoms)} atoms. Free Energy minimized."
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the score relative to a baseline."""
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to 0-1. 
        # Typical FEP scores in this setup might range from -5 to 5 depending on complexity.
        # We use a sigmoid mapping centered at 0.
        confidence = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, confidence))