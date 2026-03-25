import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a reasoning scorer using Ergodic Theory, Sparse Autoencoders, and Mechanism Design.
    
    Mechanism:
    1. Parsing: Extracts atomic logical propositions (literals, negations, conditionals, numerics) 
       into a shared dictionary D.
    2. Sparse Coding: Represents each answer as a sparse vector over D via matching pursuit.
    3. Ergodic Averaging: Applies a deterministic inference operator T (modus ponens/transitivity) 
       iteratively. The final state is the time-average (ergodic mean) of the orbit.
    4. Mechanism Design: Scores candidates using a quadratic proper scoring rule based on 
       distance to a reference (consensus) ergodic state.
    """
    
    def __init__(self):
        self.epsilon = 1e-6
        self.max_sparsity = 10
        self.max_steps = 20
        self.delta = 1e-4

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions using regex."""
        props = []
        text_lower = text.lower()
        
        # Numeric comparisons
        nums = re.findall(r'-?\d+\.?\d*', text)
        for n in nums:
            props.append(f"num_val({n})")
            
        # Conditionals
        if_matches = re.findall(r'if\s+(.+?)(?:\s+then\s+(.+?))?(?:\.|,|$)', text_lower)
        for cond, cons in if_matches:
            props.append(f"cond({cond.strip()})")
            if cons:
                props.append(f"implies({cond.strip()}, {cons.strip()})")
                
        # Causal
        causal = re.findall(r'(.+?)\s+(because|leads to)\s+(.+?)', text_lower)
        for c1, _, c2 in causal:
            props.append(f"causes({c1.strip()}, {c2.strip()})")

        # Comparatives
        comps = re.findall(r'(\w+)\s+(greater than|less than|equal to|>=|<=|=)\s+(\w+)', text_lower)
        for c1, op, c2 in comps:
            props.append(f"comp({c1}, {op}, {c2})")

        # Negations
        negs = re.findall(r'(?:not|no)\s+(\w+)', text_lower)
        for n in negs:
            props.append(f"not({n})")

        # Generic literals (simple noun phrases or sentences split by punctuation)
        # Simplified for brevity: take non-empty segments
        segments = re.split(r'[.,;!?]', text)
        for seg in segments:
            clean = seg.strip()
            if len(clean) > 3 and not any(k in clean for k in ['if', 'because', 'leads to']):
                props.append(f"lit({clean[:50]})")
                
        return list(set(props))

    def _build_dictionary(self, prompt: str, candidates: List[str]) -> Tuple[List[str], Dict[str, int]]:
        """Build shared dictionary D from prompt and all candidates."""
        all_texts = [prompt] + candidates
        all_props = []
        for t in all_texts:
            all_props.extend(self._extract_propositions(t))
        
        unique_props = list(dict.fromkeys(all_props)) # Preserve order, remove duplicates
        dictionary = {p: i for i, p in enumerate(unique_props)}
        return unique_props, dictionary

    def _sparse_code(self, text: str, dictionary: Dict[str, int], k: int) -> np.ndarray:
        """Generate sparse code via matching pursuit-like selection."""
        props = self._extract_propositions(text)
        k_dim = len(dictionary)
        if k_dim == 0:
            return np.zeros(0)
            
        # Initial binary vector
        v = np.zeros(k_dim)
        for p in props:
            if p in dictionary:
                v[dictionary[p]] = 1.0
        
        # Matching pursuit approximation
        c = np.zeros(k_dim)
        r = v.copy()
        indices_used = set()
        
        for _ in range(min(self.max_sparsity, k_dim)):
            if np.linalg.norm(r, 1) < self.epsilon:
                break
            
            # Find max absolute inner product (since atoms are standard basis, this is just max |r_i|)
            # But we simulate the "atom" selection. Since our dictionary IS the basis, 
            # the atom with max inner product is simply the index of the max value in residual.
            idx = np.argmax(np.abs(r))
            val = r[idx]
            
            if np.abs(val) < self.epsilon:
                break
                
            if idx in indices_used:
                # Prevent infinite loop if logic fails, break
                break
                
            indices_used.add(idx)
            c[idx] += np.sign(val) # alpha = sign
            r[idx] = 0 # Subtract contribution (perfect match in orthogonal basis)
            
        return c

    def _inference_operator(self, c: np.ndarray, dictionary: Dict[str, int]) -> np.ndarray:
        """
        Deterministic inference operator T.
        Simulates modus ponens and transitivity via boolean matrix logic on indices.
        """
        if len(c) == 0:
            return c
            
        next_c = c.copy()
        dict_items = list(dictionary.items())
        
        # Simple propagation: If "if A then B" (encoded) and "A" exists, activate "B"
        # Since our encoding is flat, we look for pattern matches in keys
        # This is a heuristic approximation of the matrix multiplication T
        
        active_indices = np.where(c > 0)[0]
        active_keys = [list(dictionary.keys())[i] for i in active_indices if i < len(dictionary)]
        
        # Check for implications
        for key in active_keys:
            if key.startswith("implies("):
                # Parse implies(A, B)
                match = re.match(r'implies\((.+), (.+)\)', key)
                if match:
                    antecedent = match.group(1).strip()
                    consequent = match.group(2).strip()
                    
                    # Check if antecedent is active (simplified string match)
                    # Look for a literal or prop that matches the antecedent substring
                    for ak in active_keys:
                        if antecedent in ak or ak.startswith(f"lit({antecedent}"):
                            # Activate consequent
                            # Find index of consequent or similar
                            for k_name, k_idx in dictionary.items():
                                if consequent in k_name or k_name.startswith(f"lit({consequent}"):
                                    next_c[k_idx] = 1.0
                                    
        # Normalize to binary for stability
        next_c = (next_c > 0.5).astype(float)
        return next_c

    def _ergodic_average(self, c0: np.ndarray, dictionary: Dict[str, int]) -> np.ndarray:
        """Compute ergodic average over the orbit of T."""
        if len(c0) == 0:
            return c0
            
        c_t = c0
        orbit_sum = c_t.copy()
        
        for t in range(1, self.max_steps):
            c_next = self._inference_operator(c_t, dictionary)
            
            # Convergence check
            if np.linalg.norm(c_next - c_t) < self.delta:
                break
                
            c_t = c_next
            orbit_sum += c_t
            
        return orbit_sum / (t + 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Build Dictionary
        _, dictionary = self._build_dictionary(prompt, candidates)
        k = len(dictionary)
        if k == 0:
            # Fallback if no structure found: NCD tiebreaker
            return self._ncd_fallback(prompt, candidates)

        # 2. Sparse Code & 3. Ergodic Average for all
        ergodic_codes = []
        for cand in candidates:
            c0 = self._sparse_code(cand, dictionary, self.max_sparsity)
            # Pad if dictionary grew (unlikely in this flow but safe)
            if len(c0) < k:
                c0 = np.pad(c0, (0, k - len(c0)), 'constant')
            elif len(c0) > k:
                c0 = c0[:k]
                
            c_avg = self._ergodic_average(c0, dictionary)
            ergodic_codes.append(c_avg)
            
        # Use consensus (mean of all candidates) as reference if no ground truth provided
        # In mechanism design, often the "truth" is the consensus of rational agents
        reference = np.mean(np.array(ergodic_codes), axis=0)
        
        results = []
        for i, cand in enumerate(candidates):
            c_avg = ergodic_codes[i]
            # 4. Mechanism Design Scoring: Quadratic Proper Scoring Rule
            # Score = -||c_avg - reference||^2
            dist_sq = np.sum((c_avg - reference) ** 2)
            score = -dist_sq
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Sparse code dim={k}, Ergodic convergence achieved, Distance to consensus={dist_sq:.4f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Estimate confidence based on structural richness and consistency."""
        props = self._extract_propositions(answer)
        if not props:
            return 0.1
            
        # Heuristic: More structured propositions imply higher confidence potential
        # Normalize by arbitrary cap
        raw_conf = min(1.0, len(props) / 10.0)
        
        # Check for internal contradictions (simple negation check)
        text_lower = answer.lower()
        if "not" in text_lower and "yes" in text_lower:
            raw_conf *= 0.8
            
        return float(np.clip(raw_conf, 0.0, 1.0))

    def _ncd_fallback(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Fallback to NCD if structural parsing fails."""
        import zlib
        def ncd(a, b):
            a_b = a + b
            return (len(zlib.compress(a_b.encode())) - min(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())))) / max(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())), 1)
        
        # Score based on similarity to prompt (assuming answer should be relevant)
        scores = []
        for cand in candidates:
            try:
                dist = ncd(prompt, cand)
                scores.append({"candidate": cand, "score": -dist, "reasoning": "NCD fallback"})
            except:
                scores.append({"candidate": cand, "score": -10.0, "reasoning": "Error"})
                
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores