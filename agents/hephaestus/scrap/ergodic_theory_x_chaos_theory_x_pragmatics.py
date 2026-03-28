import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool integrating Ergodic Theory, Chaos Theory, and Pragmatics.
    
    Mechanism:
    1. LOGIC (Ergodic/State Space): Parses prompts into atomic propositions (vectors).
       Builds an adjacency matrix of constraints and computes transitive closure via
       Boolean matrix multiplication. Scores candidates based on logical consistency
       with the derived closure.
    2. CHAOS (Sensitivity): Perturbs numeric values and negations in the prompt slightly.
       Recomputes logical violations to estimate a Lyapunov-like exponent. Low sensitivity
       (stable reasoning) yields higher scores.
    3. PRAGMATICS (Context): Evaluates Gricean maxims (Quantity, Quality, Relevance, Manner)
       using heuristic feature overlap and syntactic depth.
       
    Final Score: Weighted sum of Logic, Chaos stability, and Pragmatic adherence.
    """

    def __init__(self):
        # Weights for the final score
        self.alpha = 0.5  # Logic
        self.beta = 0.3   # Chaos Stability
        self.gamma = 0.2  # Pragmatics
        self.epsilon_steps = 3
        self.delta = 0.1

    def _parse_features(self, text: str) -> Tuple[List[Dict], List[str]]:
        """Extract atomic propositions and features using regex."""
        features = []
        atoms = []
        text_lower = text.lower()
        
        # Patterns
        neg_pat = re.compile(r'\b(not|no|never|none)\b')
        num_pat = re.compile(r'-?\d+\.?\d*')
        comp_pat = re.compile(r'(greater|less|more|fewer|before|after|first|last)')
        cond_pat = re.compile(r'\b(if|then|unless|provided)\b')
        quant_pat = re.compile(r'\b(all|some|most|every|each)\b')
        
        # Simple tokenization by splitting on common delimiters but keeping structure
        # We treat sentences/clauses as potential atoms
        clauses = re.split(r'[.,;!?]', text)
        
        for clause in clauses:
            if not clause.strip():
                continue
            c_lower = clause.lower()
            
            # Feature vector: [negation, comparative, conditional, quantifier, has_number]
            vec = [
                1 if neg_pat.search(c_lower) else 0,
                1 if comp_pat.search(c_lower) else 0,
                1 if cond_pat.search(c_lower) else 0,
                1 if quant_pat.search(c_lower) else 0,
                0.0 # Numeric slot
            ]
            
            nums = num_pat.findall(c_lower)
            if nums:
                vec[4] = float(nums[0])
            
            features.append(vec)
            atoms.append(clause.strip())
            
        return features, atoms

    def _build_constraint_matrix(self, atoms: List[str], features: List[List]) -> np.ndarray:
        """Build adjacency matrix A where A[i,j]=1 if i implies j."""
        n = len(atoms)
        if n == 0:
            return np.zeros((0, 0), dtype=bool)
            
        A = np.zeros((n, n), dtype=bool)
        np.fill_diagonal(A, True)
        
        # Heuristic constraint propagation based on feature overlap and ordering
        # If atom i has a number and atom j has a number, check ordering
        nums = [f[4] for f in features]
        
        for i in range(n):
            for j in range(i + 1, n):
                # Transitivity hint: if i and j share high feature similarity, link them
                fi = np.array(features[i][:4])
                fj = np.array(features[j][:4])
                
                # If features match significantly, assume logical flow (simplified)
                if np.sum(fi == fj) >= 3:
                    A[i, j] = True
                    A[j, i] = True # Bidirectional for same-type assertions
                
                # Numeric consistency
                if nums[i] > 0 and nums[j] > 0:
                    if features[i][1] == 1 and features[j][1] == 1: # Both comparative
                         # Simplified: assume sorted order implies consistency
                        if nums[i] < nums[j]:
                            A[i, j] = True
                        else:
                            A[j, i] = True
                            
        # Transitive closure via Boolean Matrix Multiplication
        # T = A OR (A @ A) ... until convergence
        T = A.copy()
        for _ in range(n): # Max steps
            old_T = T.copy()
            # Boolean matrix multiplication
            T = T | (T @ T)
            if np.array_equal(T, old_T):
                break
        return T

    def _compute_logic_score(self, prompt: str, candidate: str) -> float:
        """Compute logic score based on constraint violations."""
        full_text = f"{prompt} {candidate}"
        feats, atoms = self._parse_features(full_text)
        
        if len(atoms) < 2:
            return 0.5 # Neutral if insufficient data
            
        T = self._build_constraint_matrix(atoms, feats)
        n = len(atoms)
        
        # Count violations: In a consistent system, implied relations should hold.
        # We approximate violations by checking if the candidate contradicts the prompt's closure
        # Simplified: Ratio of connected components vs expected
        # Here we use a heuristic: Density of the closure matrix as a proxy for coherence
        # Higher density in relevant areas = better logic
        
        # Alternative: Check if candidate atoms are reachable from prompt atoms
        prompt_len = len(self._parse_features(prompt)[0])
        if prompt_len == 0: return 0.5
        
        # Assume first prompt_len atoms are prompt, rest are candidate
        # Check if candidate atoms are reachable from prompt atoms
        reachable = 0
        total_candidate_atoms = len(atoms) - prompt_len
        if total_candidate_atoms == 0:
            return 0.5
            
        for i in range(prompt_len):
            for j in range(prompt_len, len(atoms)):
                if T[i, j] or T[j, i]:
                    reachable += 1
                    
        # Normalize
        max_links = prompt_len * total_candidate_atoms
        if max_links == 0: return 0.5
        return min(1.0, reachable / max_links + 0.5) # Base boost

    def _compute_chaos_score(self, prompt: str, candidate: str) -> float:
        """Perturb input and measure stability of logic score."""
        base_score = self._compute_logic_score(prompt, candidate)
        if base_score == 0: return 0.0
        
        scores = []
        perturbations = []
        
        # Perturb numbers in prompt
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        if not nums:
            return 1.0 # Stable if no numbers to perturb
            
        for _ in range(self.epsilon_steps):
            mod_prompt = prompt
            val = float(nums[0])
            # Perturb
            new_val = val + (np.random.rand() - 0.5) * self.delta
            mod_prompt = mod_prompt.replace(nums[0], str(new_val), 1)
            
            s = self._compute_logic_score(mod_prompt, candidate)
            scores.append(s)
            perturbations.append(abs(new_val - val))
            
        if len(scores) < 2:
            return 1.0
            
        # Approximate Lyapunov exponent: lambda ~ avg(log(|delta_score| / |delta_input|))
        # If score doesn't change, lambda is very negative -> high stability
        lyap_sum = 0
        count = 0
        for i in range(len(scores)-1):
            ds = abs(scores[i] - scores[i+1])
            di = perturbations[i] if perturbations[i] != 0 else 1e-6
            if ds > 1e-9:
                lyap_sum += np.log(ds / di)
                count += 1
                
        if count == 0:
            return 1.0 # Perfectly stable
            
        lambda_avg = lyap_sum / count
        # Map to 0-1: lower lambda (more negative) is better
        # S_chaos = exp(-lambda). If lambda is negative, exp(positive) > 1, clamp to 1.
        return float(np.exp(-lambda_avg)) if lambda_avg < 10 else 0.0

    def _compute_pragmatics_score(self, prompt: str, candidate: str) -> float:
        """Evaluate Gricean maxims via heuristics."""
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        if not p_words or not c_words:
            return 0.0
            
        # Quantity: Overlap ratio
        quantity = len(p_words & c_words) / len(p_words | c_words)
        
        # Quality: Heuristic - if candidate contains "maybe" but prompt is definite, penalty
        quality = 1.0
        if re.search(r'\b(maybe|perhaps|guess)\b', candidate.lower()):
            if re.search(r'\b(must|is|are|fact)\b', prompt.lower()):
                quality = 0.5
                
        # Relevance: Cosine similarity of word counts (simplified to Jaccard for speed/no-deps)
        relevance = len(p_words & c_words) / max(1, len(p_words))
        
        # Manner: Inverse of syntactic depth (approximated by sentence length variance)
        # Shorter, direct answers often score higher on manner in this context
        manner = 1.0 / (1.0 + 0.1 * len(candidate.split()))
        
        return (quantity + quality + relevance + manner) / 4.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            s_log = self._compute_logic_score(prompt, cand)
            s_cha = self._compute_chaos_score(prompt, cand)
            s_pra = self._compute_pragmatics_score(prompt, cand)
            
            score = self.alpha * s_log + self.beta * s_cha + self.gamma * s_pra
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Logic:{s_log:.2f}, Chaos:{s_cha:.2f}, Prag:{s_pra:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        res = self.evaluate(prompt, [answer])
        return res[0]["score"] if res else 0.0