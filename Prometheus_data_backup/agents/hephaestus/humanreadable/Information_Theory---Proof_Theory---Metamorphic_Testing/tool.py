import re
import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A hybrid reasoning engine combining Proof Theory (transitive reduction), 
    Information Theory (entropy), and Metamorphic Testing (consistency checks).
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, numeric constraints, and logical implications.
    2. Proof Normalization: Builds an adjacency matrix and computes transitive reduction 
       to measure logical compactness (fewer redundant edges = higher score).
    3. Information Scoring: Calculates Shannon entropy of the proposition stream.
    4. Metamorphic Consistency: Perturbs inputs (negation, scaling, reordering) and 
       measures KL-divergence to penalize brittle reasoning.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>=|<=|>|<|=|is greater than|is less than|equals)\s*(\w+|\d+(?:\.\d+)?)', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|when|unless)\b.*?\b(then|,|\.)', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|first|last|next)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'(have you stopped|why did .*(?:fail|stop)|when did .*(?:stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+|choose between)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract atomic propositions (simplified to sentences/clauses)."""
        # Split by common delimiters but keep structure
        raw = re.split(r'[.,;!?]', text)
        props = [p.strip() for p in raw if p.strip()]
        return props if props else [text]

    def _build_graph(self, text: str) -> Tuple[np.ndarray, List[str], float]:
        """
        Build adjacency matrix A and extract propositions.
        Returns A, prop_list, and base confidence from cues.
        """
        props = self._extract_propositions(text)
        n = len(props)
        if n == 0:
            return np.array([]), [], 0.0
        
        A = np.zeros((n, n), dtype=int)
        cue_strength = 0.0
        
        # Map props to indices
        prop_map = {i: p.lower() for i, p in enumerate(props)}
        
        for i, p in prop_map.items():
            # Check for internal logic within a proposition
            if self.patterns['conditional'].search(p) or self.patterns['causal'].search(p):
                # Implication: if text has conditional, assume structure implies flow
                # Simplified: connect to next prop if exists, or self-loop for logic weight
                if i < n - 1:
                    A[i, i+1] = 1
                cue_strength += 0.5
            
            if self.patterns['temporal'].search(p):
                cue_strength += 0.3
                
            if self.patterns['negation'].search(p):
                cue_strength += 0.2 # Negation adds complexity

        # Fill comparatives as edges if multiple numbers found
        nums = self.patterns['numbers'].findall(text)
        if len(nums) >= 2:
            # Assume ordering implies sequence
            for i in range(n-1):
                A[i, i+1] = 1
        
        return A, props, min(cue_strength, 1.0)

    def _transitive_reduction(self, A: np.ndarray) -> int:
        """Compute transitive reduction size (proof length)."""
        if A.size == 0:
            return 0
        n = A.shape[0]
        if n == 0:
            return 0
            
        # Transitive closure via repeated squaring (simplified for boolean)
        T = A.astype(float)
        # Power method approximation for closure
        for _ in range(n):
            T = np.sign(T @ T + T) 
            
        # Reduction: Remove edge i->j if path i->k->j exists
        A_red = A.copy()
        for i in range(n):
            for j in range(n):
                if A[i, j] == 1:
                    # Check for intermediate k
                    for k in range(n):
                        if k != i and k != j:
                            if T[i, k] > 0 and T[k, j] > 0:
                                # Check if direct edge is redundant via k
                                # Note: In boolean matrix, if T[i,k] and T[k,j] are true, 
                                # and we have i->j, it might be redundant.
                                # Strict reduction requires checking original graph reachability.
                                # Simplified: If T[i,j] can be formed by others, remove.
                                if (T[i, k] > 0) and (T[k, j] > 0):
                                     # Heuristic: if path length > 1 exists, mark for removal check
                                     pass 
                    # Rigorous check for this specific implementation:
                    # If there exists k such that A[i,k]=1 and A[k,j]=1 (or reachable), remove A[i,j]
                    has_intermediate = False
                    for k in range(n):
                        if k != i and k != j:
                            if (A[i, k] == 1 or T[i,k] > 0) and (A[k, j] == 1 or T[k,j] > 0):
                                # Verify connectivity in closure
                                if T[i,k] > 0 and T[k,j] > 0:
                                    has_intermediate = True
                                    break
                    if has_intermediate:
                        A_red[i, j] = 0
                        
        return int(np.sum(A_red))

    def _compute_entropy(self, props: List[str]) -> float:
        """Compute Shannon entropy of proposition frequencies."""
        if not props:
            return 0.0
        n = len(props)
        if n == 1:
            return 0.0
        
        # Treat each unique proposition as a symbol
        counts = {}
        for p in props:
            counts[p] = counts.get(p, 0) + 1
        
        entropy = 0.0
        for count in counts.values():
            p_i = count / n
            if p_i > 0:
                entropy -= p_i * math.log2(p_i)
        return entropy

    def _metamorphic_transform(self, text: str, mode: int) -> str:
        """Apply metamorphic transformation."""
        if mode == 1:
            # MR1: Swap first two sentences/conjuncts
            parts = re.split(r'(,| and | but )', text, maxsplit=1)
            if len(parts) > 2:
                return parts[2] + parts[1] + parts[0] + "".join(parts[3:])
            return text
        elif mode == 2:
            # MR2: Negate a non-essential word (insert 'not')
            if ' is ' in text:
                return text.replace(' is ', ' is not ', 1)
            return text + " not."
        elif mode == 3:
            # MR3: Scale numbers
            def scale(match):
                val = float(match.group())
                return str(val * 2.0)
            return self.patterns['numbers'].sub(scale, text)
        return text

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(prompt):
            return 0.3
            
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.4
            
        # 4. Pronoun/Scope Ambiguity (Heuristic: "he/she/they" with multiple names)
        names = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        pronouns = re.findall(r'\b(he|she|they|him|her)\b', p_lower)
        if len(set(names)) > 1 and len(pronouns) > 0:
            # Potential ambiguity
            return 0.5

        # Default high confidence if structural cues are present
        return 1.0

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic."""
        # 1. Parse Prompt
        A_prompt, props_p, _ = self._build_graph(prompt)
        n_p = len(props_p)
        if n_p == 0:
            return 0.0
            
        # 2. Parse Candidate
        A_cand, props_c, _ = self._build_graph(candidate)
        n_c = len(props_c)
        
        # 3. Proof Compactness (Normalized)
        # We evaluate the "combined" logic graph to see if candidate fits prompt structure
        # Simplified: Score based on candidate's own logical compactness relative to prompt length
        E_red = self._transitive_reduction(A_cand) if A_cand.size > 0 else 0
        compactness = 1.0 / (E_red + 1) if n_c > 0 else 0.0
        
        # 4. Information Content
        H = self._compute_entropy(props_c)
        max_H = math.log2(n_c) if n_c > 1 else 1.0
        norm_entropy = H / max_H if max_H > 0 else 0.0
        
        # 5. Metamorphic Consistency
        kl_divs = []
        orig_props = props_c
        if not orig_props:
            orig_props = ["empty"]
            
        # Calculate distribution of original
        total_orig = len(orig_props)
        freq_orig = {}
        for p in orig_props:
            freq_orig[p] = freq_orig.get(p, 0) + 1
        p_dist = {k: v/total_orig for k, v in freq_orig.items()}

        for mode in [1, 2, 3]:
            trans_text = self._metamorphic_transform(candidate, mode)
            _, t_props, _ = self._build_graph(trans_text)
            if not t_props:
                t_props = ["empty"]
            
            # Calculate q distribution
            total_t = len(t_props)
            freq_t = {}
            for p in t_props:
                freq_t[p] = freq_t.get(p, 0) + 1
            q_dist = {k: v/total_t for k, v in freq_t.items()}
            
            # KL Divergence (smoothing)
            kl = 0.0
            all_keys = set(p_dist.keys()) | set(q_dist.keys())
            for k in all_keys:
                p_val = p_dist.get(k, 1e-6)
                q_val = q_dist.get(k, 1e-6)
                if p_val > 0:
                    kl += p_val * math.log(p_val / (q_val + 1e-9))
            kl_divs.append(kl)
            
        M = np.mean(kl_divs) if kl_divs else 0.0
        
        # Final Score Formula
        # S = Compactness + Normalized Entropy - Lambda * Metamorphic Penalty
        score = compactness + norm_entropy - 0.5 * M
        
        # Structural Alignment Bonus (Simple overlap check for key terms)
        # Ensures candidate is actually about the prompt
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        cand_words = set(re.findall(r'\w+', candidate.lower()))
        overlap = len(prompt_words & cand_words) / (len(prompt_words) + 1)
        
        final_score = 0.7 * score + 0.3 * overlap
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Compactness: {1/(self._transitive_reduction(self._build_graph(cand)[0])+1):.2f}, Entropy: {self._compute_entropy(self._extract_propositions(cand)):.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Caps based on epistemic honesty (Tier B).
        """
        # 1. Check Meta-Confidence (Ambiguity/Traps)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Compute raw score
        raw_score = self._compute_score(prompt, answer)
        
        # 3. Normalize raw score to 0-1 range roughly
        # Scores can be negative or >1, clamp for probability interpretation
        prob = 1.0 / (1.0 + math.exp(-raw_score * 5)) # Sigmoid scaling
        
        # 4. Apply Cap
        final_conf = min(prob, meta_cap)
        
        # 5. Ensure low confidence if no structural match found (empty props)
        if len(self._extract_propositions(prompt)) == 0 or len(self._extract_propositions(answer)) == 0:
            return 0.1
            
        return round(final_conf, 4)

# Example usage logic (not executed here, but demonstrates interface)
# tool = ReasoningTool()
# print(tool.evaluate("If A then B. A is true.", ["B is true", "B is false"]))
# print(tool.confidence("Have you stopped cheating?", "Yes")) # Should be low due to presupposition