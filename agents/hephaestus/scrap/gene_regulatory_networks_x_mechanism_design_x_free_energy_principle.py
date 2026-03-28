import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining Gene Regulatory Network (GRN) dynamics,
    Mechanism Design incentives, and the Free Energy Principle (FEP).
    
    Mechanism:
    1. Parsing: Extracts propositional atoms from prompt/candidates using regex.
       Identifies relations (support, contradict, imply) to build a weight matrix W.
    2. GRN Dynamics: Iteratively updates atom activations via sigmoid(W*a + b).
    3. Mechanism Design: Penalizes simultaneous activation of contradictory atoms.
    4. Free Energy: Scores candidates based on prediction error (alignment with prompt priors)
       minus the penalty for logical inconsistencies.
    5. Epistemic Honesty: Detects ambiguity/traps in the prompt to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit|failed to)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or both|must choose between)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|they|him|her)\b.*\bwho\b', re.IGNORECASE)
        }
        self.epsilon = 1e-4
        self.max_iter = 50
        self.lambda_penalty = 2.0  # Mechanism design penalty weight

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization into words."""
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract propositional atoms (simplified as normalized phrases/clauses)."""
        # Split by common delimiters to find atomic claims
        raw_atoms = re.split(r'[,.;]', text)
        atoms = []
        for chunk in raw_atoms:
            clean = chunk.strip()
            if len(clean) > 2:
                atoms.append(clean)
        return atoms if atoms else [text[:50]] # Fallback

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, List[str], np.ndarray]:
        """
        Construct the graph G=(V, E) and bias vector b.
        Nodes V are atoms from both prompt and candidate.
        """
        full_text = f"{prompt} {candidate}"
        atoms = self._extract_atoms(full_text)
        n = len(atoms)
        if n == 0:
            return np.array([]), [], np.array([])
            
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        # 1. Encode Priors (Bias b) from Prompt
        prompt_atoms = self._extract_atoms(prompt)
        for i, atom in enumerate(atoms):
            # If atom comes from prompt, it has prior expectation
            if any(atom in p for p in prompt_atoms) or any(p in atom for p in prompt_atoms):
                b[i] = 1.0 
            # Check for negation in prompt affecting this atom
            if re.search(self.patterns['negation'], atom):
                b[i] = -1.0

        # 2. Encode Edges (W) based on structural cues
        for i, atom_i in enumerate(atoms):
            for j, atom_j in enumerate(atoms):
                if i == j: continue
                
                # Support/Imply (Positive Edge)
                if any(k in atom_i for k in ['if', 'leads to']) and atom_j in atom_i:
                    W[i, j] = 0.8
                if any(k in atom_j for k in ['because', 'due to']) and atom_i in atom_j:
                    W[j, i] = 0.8
                
                # Contradiction/Negation (Negative Edge)
                # If atom_i contains "not X" and atom_j is "X"
                if re.search(self.patterns['negation'], atom_i):
                    # Simple overlap check for contradiction
                    words_i = set(atom_i.split())
                    words_j = set(atom_j.split())
                    if len(words_i.intersection(words_j)) > 1:
                        W[i, j] = -1.0
                        W[j, i] = -1.0

        return W, atoms, b

    def _run_grn_dynamics(self, W: np.ndarray, b: np.ndarray, initial_state: np.ndarray) -> np.ndarray:
        """Iterate activation until convergence or max steps."""
        if W.size == 0:
            return initial_state
            
        a = initial_state.copy()
        for _ in range(self.max_iter):
            a_new = 1.0 / (1.0 + np.exp(-(np.dot(W, a) + b)))
            if np.linalg.norm(a_new - a, 1) < self.epsilon:
                break
            a = a_new
        return a

    def _calculate_free_energy(self, a: np.ndarray, b: np.ndarray, W: np.ndarray) -> float:
        """
        Calculate Variational Free Energy F.
        F = Prediction Error + Mechanism Design Penalty
        Score = -F
        """
        if a.size == 0:
            return 0.0
            
        # Term 1: Prediction error (Alignment with prompt priors)
        prediction_error = 0.5 * np.sum((a - b) ** 2)
        
        # Term 2: Mechanism Design Penalty (Incentive Compatibility)
        # Penalize simultaneous activation of contradictory pairs (W_ij < 0)
        penalty = 0.0
        neg_indices = np.where(W < 0)
        for i, j in zip(neg_indices[0], neg_indices[1]):
            # Penalty if both are highly active (a_i + a_j > 1)
            violation = max(0, a[i] + a[j] - 1.0)
            penalty += self.lambda_penalty * violation
            
        F = prediction_error + penalty
        return -F # Return negative free energy as score (higher is better)

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, traps, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.patterns['presupposition'].search(prompt):
            return 0.2
            
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            # Only flag if it looks like a forced choice without "or neither"
            if "or neither" not in p_lower and "or none" not in p_lower:
                return 0.3
                
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.4
            
        # 4. Pronoun Ambiguity (simplified check)
        if self.patterns['pronoun_ambiguity'].search(prompt) and "who" in p_lower:
            return 0.3
            
        # 5. Scope/Quantifier ambiguity (heuristic: "every" + "same"?)
        if "every" in p_lower and ("same" in p_lower or "different" in p_lower):
            return 0.5
            
        return 1.0 # No obvious traps detected

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        if len12 == 0: return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt atoms for baseline comparison
        prompt_atoms = self._extract_atoms(prompt)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural & GRN/FEP Analysis (Primary Signal ~70%)
            W, atoms, b = self._build_graph(prompt, cand)
            
            if len(atoms) > 0:
                # Initial activation: 1 if in candidate, 0 otherwise (simplified)
                # In a real scenario, we'd map candidate atoms to indices precisely.
                # Here we assume the concatenated text forms the universe.
                initial_a = np.zeros(len(atoms))
                # Heuristic: Activate nodes present in candidate
                cand_atoms = self._extract_atoms(cand)
                for i, atom in enumerate(atoms):
                    if any(ca in atom for ca in cand_atoms) or any(atom in ca for ca in cand_atoms):
                        initial_a[i] = 1.0
                
                final_a = self._run_grn_dynamics(W, b, initial_a)
                fep_score = self._calculate_free_energy(final_a, b, W)
                
                # Normalize score roughly to 0-1 range for combination
                # FEP is negative error, so less negative (closer to 0) is better.
                # We shift it: raw score might be -5 to 0. Let's map -10->0, 0->1
                structural_score = max(0, min(1, (fep_score + 5) / 5.0))
                score += structural_score * 0.70
                reasoning_parts.append(f"GRN-FEP alignment: {structural_score:.2f}")
            else:
                reasoning_parts.append("No structural atoms found.")

            # 2. Constructive/Numeric Check (Secondary Signal ~15%)
            nums_prompt = [float(x) for x in self.patterns['numeric'].findall(prompt)]
            nums_cand = [float(x) for x in self.patterns['numeric'].findall(cand)]
            
            if nums_prompt and nums_cand:
                # Simple heuristic: Does candidate number match prompt logic?
                # E.g., if prompt has "5 + 3", does candidate have "8"?
                expected = sum(nums_prompt) # Very rough constructive check
                if any(abs(n - expected) < 0.01 for n in nums_cand):
                    score += 0.15
                    reasoning_parts.append("Numeric consistency verified.")
                else:
                    # Penalty for numeric mismatch if counts differ wildly
                    if len(nums_cand) != len(nums_prompt):
                        score -= 0.1
                        reasoning_parts.append("Numeric mismatch detected.")

            # 3. NCD Tiebreaker (Max 15%)
            # Only use if structural signal is weak or as a tiebreaker
            ncd_val = self._compute_ncd(prompt, cand)
            # Lower NCD (more similar) is generally better for relevance, 
            # but we want reasoning, so we weight it lightly.
            ncd_score = (1.0 - ncd_val) * 0.15
            score += ncd_score
            
            # Normalize final score to reasonable range
            final_score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._check_meta_confidence(prompt)
        
        # 2. Structural Confidence
        # If we can't parse any structure, confidence should be low
        atoms = self._extract_atoms(prompt + " " + answer)
        if len(atoms) < 2:
            struct_conf = 0.2
        else:
            # Run a quick evaluation to see if the answer scores well
            # We simulate a binary choice: this answer vs a garbage string
            res = self.evaluate(prompt, [answer, "N/A"])
            if res and res[0]['candidate'] == answer:
                struct_conf = res[0]['score']
            else:
                struct_conf = 0.3
        
        # Combine: Confidence cannot exceed the meta-cap
        final_conf = min(struct_conf, meta_cap)
        
        # Never return > 0.9 unless it's a definitive computation (hard to guarantee here)
        # So we hard cap at 0.95 max to maintain humility
        return min(final_conf, 0.95)