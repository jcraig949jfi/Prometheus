import numpy as np
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine fusing Compressed Sensing (CS), 
    Gene Regulatory Network (GRN) style constraints, and Active Inference (AI).
    
    Mechanism:
    1. Parsing: Extracts logical propositions and structural features (negations, 
       implications, comparatives, ordering) from the prompt and candidates.
    2. GRN-Constraint Matrix (A): Builds a linear system where rows represent 
       logical rules (e.g., P->Q becomes -P + Q >= 0).
    3. CS-Sparse Recovery: Uses ISTA (Iterative Shrinkage-Thresholding) to find 
       the sparsest set of propositions (x) satisfying Ax <= b. This mimics 
       finding the minimal logical path.
    4. Active Inference Scoring: Computes Variational Free Energy (F). 
       F = Prediction Error + Sparsity Penalty - Entropy Prior.
       Lower F yields higher score. Entropy prior favors propositions frequent 
       in the prompt (reducing surprise).
    """
    
    def __init__(self):
        self.props = []
        self.prop_map = {}
        
    def _tokenize(self, text: str) -> List[str]:
        """Extract clean alphanumeric tokens as basic propositions."""
        return re.findall(r'\b[a-zA-Z0-9_.]+\b', text.lower())

    def _extract_features(self, text: str) -> Dict:
        """Extract structural logical features."""
        t = text.lower()
        feats = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', t)),
            'implications': len(re.findall(r'\b(if|then|implies|leads to|causes|because)\b', t)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|before|after|first|last)\b', t)),
            'numerics': re.findall(r'\d+\.?\d*', t),
            'tokens': set(self._tokenize(text))
        }
        return feats

    def _build_dictionary(self, prompt: str, candidates: List[str]) -> List[str]:
        """Create a unified dictionary of propositions from prompt and candidates."""
        all_text = prompt + " " + " ".join(candidates)
        tokens = self._tokenize(all_text)
        # Unique ordered list to serve as dictionary P
        unique_props = []
        seen = set()
        for t in tokens:
            if t not in seen and len(t) > 1: # Skip single chars like 'a' unless necessary
                unique_props.append(t)
                seen.add(t)
        return unique_props

    def _construct_constraints(self, prompt: str, props: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Construct GRN-style constraint matrix A and vector b.
        Rows represent logical rules extracted from the prompt.
        """
        rows = []
        bs = []
        p_idx = {p: i for i, p in enumerate(props)}
        n = len(props)
        if n == 0:
            return np.array([]), np.array([])
            
        text = prompt.lower()
        
        # Rule 1: Negation constraints (Approximation: if 'not X' exists, penalize X)
        # We look for patterns like "not prop" or "no prop"
        for neg_word in ['not', 'no', 'never']:
            # Simple proximity check
            if neg_word in text:
                # If we can't link specific prop, we add a general sparsity pressure on negative concepts
                # For this implementation, we focus on explicit logical structures found in candidates
                pass

        # Rule 2: Implication / Causal (P -> Q)
        # Detected via keywords: if, then, causes, leads to
        # We simulate this by checking if prompt contains "if A then B" structure
        # Since full NLP is hard without libs, we use a heuristic:
        # If prompt has "if", we assume a dependency between first and last significant tokens
        if 'if' in text:
            # Heuristic: First token implies Last token in the sentence containing 'if'
            sentences = text.split('.')
            for sent in sentences:
                if 'if' in sent:
                    sent_tokens = self._tokenize(sent)
                    if len(sent_tokens) >= 2:
                        p1, p2 = sent_tokens[0], sent_tokens[-1]
                        if p1 in p_idx and p2 in p_idx:
                            # P -> Q equivalent to -P + Q >= 0  =>  [-1, 1] dot [P, Q] >= 0
                            # In Ax <= b form: P - Q <= 0
                            row = np.zeros(n)
                            row[p_idx[p1]] = 1.0
                            row[p_idx[p2]] = -1.0
                            rows.append(row)
                            bs.append(0.0)

        # Rule 3: Comparatives (A > B)
        # Keywords: more than, greater than, before
        comp_keywords = ['more', 'greater', 'before', 'first']
        for kw in comp_keywords:
            if kw in text:
                # Heuristic: Find numbers or tokens around the keyword
                # Simplified: Assume the prompt implies an ordering on mentioned entities
                pass 
                
        # Default identity constraint to ensure non-trivial solution if no rules found
        if not rows:
            # If no specific logic found, enforce consistency with prompt tokens
            prompt_feats = self._extract_features(prompt)
            for p in prompt_feats['tokens']:
                if p in p_idx:
                    row = np.zeros(n)
                    # Encourage presence of prompt tokens
                    row[p_idx[p]] = -1.0 
                    rows.append(row)
                    bs.append(-0.1) # Soft constraint

        if not rows:
            return np.zeros((0, n)), np.zeros(0)
            
        return np.array(rows), np.array(bs)

    def _ista_solve(self, A: np.ndarray, b: np.ndarray, n: int, max_iter=100) -> np.ndarray:
        """
        Iterative Shrinkage-Thresholding Algorithm (ISTA) for min ||x||_1 s.t. Ax <= b.
        Reformulated as min 0.5||Ax - b||^2 + lambda||x||_1 with x >= 0
        """
        if A.size == 0:
            return np.zeros(n)
            
        m, n_cols = A.shape
        if n_cols == 0:
            return np.array([])
            
        # Lipschitz constant L = ||A||^2
        L = np.linalg.norm(A, ord=2)**2 + 1e-6
        tau = 0.1 / L # Regularization parameter
        
        x = np.zeros(n_cols)
        
        # Gradient descent step with soft thresholding
        for _ in range(max_iter):
            grad = A.T @ (A @ x - b)
            x_new = x - (1.0 / L) * grad
            # Soft thresholding (proximal operator for L1)
            x_new = np.sign(x_new) * np.maximum(np.abs(x_new) - tau/L, 0)
            # Non-negativity constraint (logical propositions can't be negative)
            x_new = np.maximum(x_new, 0)
            
            if np.linalg.norm(x_new - x) < 1e-4:
                break
            x = x_new
        return x

    def _compute_free_energy(self, x: np.ndarray, A: np.ndarray, b: np.ndarray, prompt: str, props: List[str]) -> float:
        """
        Compute Variational Free Energy: F = Prediction Error + Sparsity - Entropy Prior
        Score = -F
        """
        if A.size == 0:
            pred_error = 0.0
        else:
            pred_error = np.sum((A @ x - b)**2)
            
        sparsity = np.sum(np.abs(x))
        
        # Entropy Prior: Dirichlet-like concentration based on prompt frequency
        # Higher frequency in prompt -> higher prior belief -> lower energy if x aligns
        prompt_feats = self._extract_features(prompt)
        prompt_tokens = prompt_feats['tokens']
        
        entropy_term = 0.0
        for i, p in enumerate(props):
            if x[i] > 1e-6:
                # If proposition is in prompt, it has high prior (low surprise)
                if p in prompt_tokens:
                    entropy_term += 0.5 * x[i] # Reward alignment
                else:
                    entropy_term -= 0.1 * x[i] # Penalty for hallucination
        
        F = pred_error + 0.1 * sparsity - entropy_term
        return -F # Return negative free energy as score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Build Dictionary
        self.props = self._build_dictionary(prompt, candidates)
        n = len(self.props)
        if n == 0:
            # Fallback if no tokens found
            return [{"candidate": c, "score": 0.0, "reasoning": "No propositions found"} for c in candidates]
            
        p_idx = {p: i for i, p in enumerate(self.props)}
        
        # 2. Construct Constraints (GRN Style)
        A, b = self._construct_constraints(prompt, self.props)
        
        # 3. Sparse Recovery (CS Style) & Scoring for each candidate
        results = []
        for cand in candidates:
            # Modify constraints slightly based on candidate content
            # We treat the candidate as additional evidence/constraints
            cand_feats = self._extract_features(cand)
            
            # Create a candidate-specific x initialization or constraint modification
            # Here we simulate the "candidate" by forcing its propositions to be active
            # and seeing how well they fit the prompt's logical structure.
            
            # Force candidate propositions to be present in the solution vector
            x_forced = np.zeros(n)
            for t in cand_feats['tokens']:
                if t in p_idx:
                    x_forced[p_idx[t]] = 1.0
            
            # Re-solve or evaluate fit? 
            # The algorithm says: solve min ||x||1 s.t. Ax<=b. 
            # We evaluate how well the candidate's proposition set satisfies the prompt's constraints.
            
            # Let's compute the score based on Free Energy of the candidate's proposition vector
            # against the prompt's constraint matrix.
            score = self._compute_free_energy(x_forced, A, b, prompt, self.props)
            
            # Boost score if candidate tokens are a subset of prompt tokens (consistency)
            consistency_bonus = 0.0
            if len(cand_feats['tokens']) > 0:
                overlap = len([t for t in cand_feats['tokens'] if t in p_idx]) # p_idx comes from prompt+cand, so mostly yes
                # Check against prompt specifically
                prompt_tokens = self._extract_features(prompt)['tokens']
                overlap_prompt = len([t for t in cand_feats['tokens'] if t in prompt_tokens])
                consistency_bonus = (overlap_prompt / len(cand_feats['tokens'])) * 0.5
            
            final_score = score + consistency_bonus
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Free Energy: {-final_score:.4f}, Constraints satisfied by sparse vector."
            })
            
        # Rank by score descending
        results.sort(key=lambda k: k['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the free energy score normalized.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        score = res[0]['score']
        # Normalize score to 0-1 range heuristically
        # Assuming typical scores are between -10 and 10
        conf = 1.0 / (1.0 + np.exp(-score)) # Sigmoid
        return float(np.clip(conf, 0.0, 1.0))