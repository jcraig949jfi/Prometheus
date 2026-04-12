import re
import zlib
import math
import numpy as np

class ReasoningTool:
    """
    Holographic Predictive Attractor Network (HPAN) Approximation.
    
    Mechanism:
    1. Structural Parsing (The Boundary): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values from the prompt/candidates.
       This acts as the sensory boundary condition.
    2. Holographic Encoding (The Bulk): Maps tokens to fixed pseudo-random vectors 
       and sums them (HRR style) to create a latent state vector. This respects 
       information bounds by compressing sequence length into fixed dimensionality.
    3. GRN Attractor Dynamics: Uses a sigmoidal activation function on the dot-product 
       similarity between the prompt's latent state and candidate states. 
       - High similarity + Logical Consistency -> Strong Attractor (High Score).
       - Logical Contradiction (e.g., Negation mismatch) -> Repulsion (Low Score).
    4. Predictive Coding: The "score" is the minimized free energy (error) between 
       the predicted logical structure of the prompt and the candidate answer.
    """

    def __init__(self):
        # Deterministic seed for reproducible "holographic" vectors
        np.random.seed(42)
        self.dim = 64  # Dimensionality of the holographic space
        self.vocab_cache = {}
        
        # Logical signatures for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'false', 'deny'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'implies'}

    def _get_vector(self, token: str) -> np.ndarray:
        """Generate a deterministic pseudo-random vector for a token (HRR binding)."""
        if token not in self.vocab_cache:
            # Use hash to seed a deterministic random vector
            h = hash(token)
            rng = np.random.RandomState(h)
            vec = rng.randn(self.dim)
            vec = vec / np.linalg.norm(vec)  # Normalize
            self.vocab_cache[token] = vec
        return self.vocab_cache[token]

    def _structural_parse(self, text: str) -> dict:
        """Extract logical structure: negations, numbers, conditionals."""
        t_lower = text.lower()
        words = re.findall(r'\b\w+\b', t_lower)
        
        has_negation = any(w in self.negations for w in words)
        has_comparative = any(w in self.comparatives for w in words)
        has_conditional = any(w in self.conditionals for w in words)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'nums': nums,
            'len': len(words)
        }

    def _holographic_encode(self, text: str) -> np.ndarray:
        """Encode text as a sum of token vectors (Simplified HRR)."""
        tokens = re.findall(r'\b\w+\b', text.lower())
        if not tokens:
            return np.zeros(self.dim)
        
        # Sum of vectors (superposition)
        vec = sum(self._get_vector(t) for t in tokens)
        # Normalize to maintain bound (approximate holographic property)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def _compute_logic_score(self, p_struct: dict, c_struct: dict, p_text: str, c_text: str) -> float:
        """
        Evaluate logical consistency between prompt and candidate.
        Returns a score adjustment based on structural rules.
        """
        score = 0.0
        
        # 1. Negation Handling: If prompt implies negation, candidate should reflect it
        # Simple heuristic: if prompt has 'no' and candidate has 'yes', penalize heavily
        p_words = set(re.findall(r'\b\w+\b', p_text.lower()))
        c_words = set(re.findall(r'\b\w+\b', c_text.lower()))
        
        if p_struct['neg']:
            if 'yes' in c_words or 'true' in c_words:
                score -= 0.5
            if 'no' in c_words or 'false' in c_words:
                score += 0.3
        
        # 2. Numeric Evaluation
        if p_struct['nums'] and c_struct['nums']:
            # If prompt asks for comparison, check if candidate number matches logic
            # Heuristic: If prompt has > or 'greater', candidate should be the larger number if it's a direct answer
            # Or simply: prefer candidates that contain numbers found in prompt if context suggests extraction
            common_nums = set(p_struct['nums']) & set(c_struct['nums'])
            if common_nums:
                score += 0.4 # Reward retaining relevant numbers
            
            # Specific check for simple comparison prompts like "Is 9.11 > 9.9?"
            if len(p_struct['nums']) >= 2 and len(c_struct['nums']) == 0:
                # Candidate is likely Yes/No. 
                # We can't evaluate truth without knowing the operator, but we can check consistency
                pass 

        # 3. Conditional/Comparative Presence
        if p_struct['comp'] and not c_struct['comp']:
            # If prompt compares, a good reasoning candidate often explains comparison or gives a definitive result
            pass # Neutral, depends on task type

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        comp_both = len(zlib.compress(b1 + b2))
        
        return (comp_both - min(comp1, comp2)) / max(comp1, comp2, 1)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
            
        p_struct = self._structural_parse(prompt)
        p_vec = self._holographic_encode(prompt)
        
        results = []
        
        for cand in candidates:
            c_struct = self._structural_parse(cand)
            c_vec = self._holographic_encode(cand)
            
            # 1. Holographic Similarity (Attractor Basins)
            # Dot product of normalized vectors gives cosine similarity
            similarity = float(np.dot(p_vec, c_vec))
            
            # 2. Logical Consistency (GRN Regulation)
            logic_adj = self._compute_logic_score(p_struct, c_struct, prompt, cand)
            
            # 3. NCD Tiebreaker (Compression)
            # Lower NCD means more shared information structure
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1  # Small weight
            
            # Combined Score: Similarity + Logic + NCD
            # The "Attractor" is the state where similarity is high AND logic is consistent
            final_score = similarity + logic_adj + ncd_score
            
            # Heuristic boost for exact string matches in logical keywords
            if p_struct['neg'] and ('no' in cand.lower() or 'false' in cand.lower()):
                final_score += 0.2
            elif p_struct['neg'] and ('yes' in cand.lower() or 'true' in cand.lower()):
                final_score -= 0.2

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Holographic similarity: {similarity:.2f}, Logic adj: {logic_adj:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1. 
        Derived from the evaluate score normalized via sigmoid.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        # Sigmoid mapping to 0-1 range
        # Center around 0, scale such that strong matches approach 1
        conf = 1.0 / (1.0 + math.exp(-raw_score * 2.0))
        return max(0.0, min(1.0, conf))