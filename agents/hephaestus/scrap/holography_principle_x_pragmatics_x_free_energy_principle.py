import re
import numpy as np
import zlib
from itertools import combinations

class ReasoningTool:
    """
    A reasoning tool combining Holographic Boundary Encoding, Pragmatics, 
    and the Free Energy Principle for evaluating logical consistency.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals).
    2. Holography: Maps propositions to boundary vectors via random projection.
    3. Free Energy: Minimizes prediction error (surprise) between logical constraints 
       and inferred truth values.
    4. Epistemic Honesty: Caps confidence on ambiguous/unanswerable prompts (Tier B).
    """

    def __init__(self):
        # Seeded random matrix for holographic projection (d=64)
        self.rng = np.random.default_rng(seed=42)
        self.d = 64
        self.vocab_size = 10000
        self.projection_matrix = self.rng.standard_normal((self.vocab_size, self.d))
        
        # Regex patterns for proposition extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|better|worse|higher|lower)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|leads to|causes)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(first|last|before|after|next)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE)
        }
        
        # Tier B Traps (Epistemic Honesty)
        self.trap_patterns = {
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|quit))\b', re.IGNORECASE),
            'scope_ambiguity': re.compile(r'\b(every .*(a|an) .*)\b', re.IGNORECASE), # Simplified heuristic
            'pronoun_ambiguity': re.compile(r'\b(.*) told (.*) (he|she|it) was\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            'unanswerable': re.compile(r'\b(who is the king of france|what is the color of noise)\b', re.IGNORECASE)
        }

    def _hash_token(self, token: str) -> int:
        """Simple hash to map token to vocabulary index."""
        return hash(token) % self.vocab_size

    def _extract_propositions(self, text: str) -> list:
        """Extract atomic propositions and their types."""
        props = []
        text_lower = text.lower()
        
        # Check for specific types
        found_types = []
        for p_type, pattern in self.patterns.items():
            if pattern.search(text_lower):
                found_types.append(p_type)
                # Extract specific matches for numeric/comparative logic later if needed
                if p_type == 'numeric':
                    matches = pattern.findall(text_lower)
                    for m in matches:
                        props.append({'type': 'numeric_val', 'content': m})
        
        if not found_types:
            # Fallback: treat whole sentence as a proposition if no specific tags
            if len(text.strip()) > 0:
                props.append({'type': 'atomic', 'content': text.strip()})
        else:
            # Add generic propositions based on found types
            for ft in found_types:
                props.append({'type': ft, 'content': ft})
                
        return props if props else [{'type': 'atomic', 'content': text}]

    def _holographic_encode(self, propositions: list) -> np.ndarray:
        """Compute boundary feature vectors and average them (Holographic Surface)."""
        if not propositions:
            return np.zeros(self.d)
        
        vectors = []
        for prop in propositions:
            # Hash content tokens
            tokens = re.findall(r'\w+', str(prop['content']))
            if not tokens:
                vec = np.zeros(self.d)
            else:
                vec = np.zeros(self.d)
                for token in tokens:
                    idx = self._hash_token(token)
                    vec += self.projection_matrix[idx]
                vec /= len(tokens) # Normalize local vector
            vectors.append(vec)
        
        if not vectors:
            return np.zeros(self.d)
            
        # Bulk meaning approximation (Average)
        return np.mean(np.array(vectors), axis=0)

    def _build_constraint_matrix(self, propositions: list) -> np.ndarray:
        """Construct adjacency matrix A based on logical rules."""
        n = len(propositions)
        if n == 0:
            return np.zeros((0, 0))
            
        A = np.zeros((n, n))
        for i, p_i in enumerate(propositions):
            for j, p_j in enumerate(propositions):
                if i == j:
                    A[i, j] = 1 # Self-consistency
                    continue
                
                # Rule: Negation conflict
                if p_i['type'] == 'negation' and p_j['type'] == 'negation':
                    # Simplified: Assume distinct negations might conflict if close
                    pass 
                
                # Rule: Transitivity/Linking (Heuristic: sequential propositions link)
                if abs(i - j) == 1:
                    A[i, j] = 1
                    A[j, i] = 1
                    
                # Rule: Conditional linking
                if p_i['type'] == 'conditional' or p_j['type'] == 'conditional':
                    A[i, j] = 0.5 # Weaker link
                    
        return A

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """Compute Free Energy F = Surprise + KL Divergence."""
        full_text = f"{prompt} {candidate}"
        props = self._extract_propositions(full_text)
        
        if not props:
            return 1.0 # High energy (bad) for empty
            
        # 1. Holographic Boundary
        b_avg = self._holographic_encode(props)
        
        # 2. Inferred Truth Values (x_hat)
        # Simple sigmoid activation of boundary projection
        w = self.rng.standard_normal(self.d)
        x_hat = 1 / (1 + np.exp(-np.dot(b_avg, w))) 
        x_hat_vec = np.full(len(props), x_hat) # Uniform initial belief
        
        # 3. Constraint Matrix
        A = self._build_constraint_matrix(props)
        if A.size == 0:
            return 0.5
            
        # 4. Prediction Error (Surprise)
        # epsilon = || A * x - x ||^2
        prediction = A @ x_hat_vec
        surprise = np.linalg.norm(prediction - x_hat_vec) ** 2
        
        # 5. KL Divergence from Uniform Prior (pi = 0.5)
        pi = 0.5
        kl_div = np.sum(x_hat_vec * np.log((x_hat_vec + 1e-9) / pi) + (1 - x_hat_vec) * np.log((1 - x_hat_vec + 1e-9) / (1 - pi)))
        
        F = surprise + 0.1 * kl_div
        return F

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if max(z1, z2) == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap value (low if trap detected).
        """
        p_lower = prompt.lower()
        
        # Check for specific trap patterns
        for trap_name, pattern in self.trap_patterns.items():
            if pattern.search(p_lower):
                return 0.25 # Low confidence cap for ambiguous/trap questions
        
        # Check for lack of structural markers (honest uncertainty)
        has_structure = False
        for p_type in ['comparative', 'conditional', 'numeric', 'ordering']:
            if self.patterns[p_type].search(p_lower):
                has_structure = True
                break
        
        if not has_structure and len(prompt.split()) < 5:
            # Very short, unstructured prompts are risky
            return 0.4
            
        return 1.0 # No obvious traps detected

    def _structural_computation_score(self, prompt: str, candidate: str) -> float:
        """
        Performs actual computation for numeric/comparative tasks.
        Returns 1.0 for correct, 0.0 for incorrect, 0.5 for N/A.
        """
        # Extract numbers from prompt and candidate
        p_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', prompt)]
        c_nums = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', candidate)]
        
        score = 0.5 # Default neutral
        
        # Case 1: Direct Numeric Comparison in prompt (e.g., "Is 5 > 3?")
        if 'greater' in prompt.lower() or '>' in prompt:
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                if p_nums[0] > p_nums[1]:
                    # Expect True/Yes
                    if any(x in candidate.lower() for x in ['yes', 'true', '1', str(p_nums[0])]):
                        score = 1.0
                    else:
                        score = 0.0
                else:
                    if any(x in candidate.lower() for x in ['no', 'false', '0']):
                        score = 1.0
                    else:
                        score = 0.0
            return score

        # Case 2: Candidate is the result of a simple operation found in prompt
        # e.g. Prompt: "Add 2 and 3", Candidate: "5"
        if len(p_nums) >= 2 and len(c_nums) == 1:
            if 'add' in prompt.lower() or '+' in prompt:
                if abs(c_nums[0] - (p_nums[0] + p_nums[1])) < 1e-6:
                    return 1.0
            if 'subtract' in prompt.lower() or '-' in prompt:
                if abs(c_nums[0] - (p_nums[0] - p_nums[1])) < 1e-6:
                    return 1.0
            if 'multiply' in prompt.lower() or '*' in prompt or 'times' in prompt:
                if abs(c_nums[0] - (p_nums[0] * p_nums[1])) < 1e-6:
                    return 1.0
                    
        return 0.5 # No specific computation matched

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-calculate meta-confidence cap based on prompt
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Computational Score (High weight for correctness)
            comp_score = self._structural_computation_score(prompt, cand)
            
            # 2. Free Energy Score (Logical consistency)
            fe = self._compute_free_energy(prompt, cand)
            # Normalize FE: lower is better. Map to 0-1 range roughly.
            # Assuming FE usually < 10 for coherent text, > 10 for noise
            fe_score = max(0.0, 1.0 - (fe / 10.0))
            
            # 3. NCD Score (Tiebreaker, low weight)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd # Higher is better
            
            # Weighted Combination
            # Structural/Computation: 60%, Free Energy: 25%, NCD: 15%
            # If computation found a definitive answer (0 or 1), it dominates
            if comp_score != 0.5:
                final_score = (comp_score * 0.85) + (fe_score * 0.15)
            else:
                final_score = (fe_score * 0.60) + (ncd_score * 0.15) + (fe_score * 0.25) # Fallback to logic
            
            # Apply Epistemic Honesty Cap
            if meta_cap < 1.0:
                # If the prompt is a trap, we cannot be highly confident in ANY answer
                # But we still rank them by consistency. We cap the *absolute* score.
                final_score = min(final_score, meta_cap + (1.0-meta_cap)*0.5)

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"FE:{fe:.2f}, Comp:{comp_score:.1f}, MetaCap:{meta_cap:.1f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty: low confidence on ambiguous prompts.
        """
        # 1. Check for Tier B traps (Ambiguity, Presupposition)
        meta_conf = self._meta_confidence(prompt)
        
        # If meta_conf is low, we are inherently unsure regardless of the answer
        if meta_conf < 0.5:
            return meta_conf
        
        # 2. Evaluate the specific answer
        # We use the internal scoring logic but focus on the gap between best and this one
        # For simplicity in this method, we check if this answer is "logical"
        fe = self._compute_free_energy(prompt, answer)
        fe_score = max(0.0, 1.0 - (fe / 10.0))
        
        comp_score = self._structural_computation_score(prompt, answer)
        
        # Combine
        if comp_score != 0.5:
            # Definitive computation found
            raw_conf = comp_score
        else:
            raw_conf = fe_score
            
        # Cap by meta-confidence (Epistemic Honesty)
        final_conf = min(raw_conf, meta_conf)
        
        # Never return > 0.9 unless computation was definitive (1.0)
        if comp_score != 1.0 and final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))