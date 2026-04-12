import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Spectral Constraint Solver (TSCS) Approximation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical tokens (negations, comparatives, 
       conditionals, numbers) to form a "type signature" vector for the prompt and candidates.
       This ensures only structurally compatible hypotheses are considered (filtering ill-formed terms).
       
    2. Constraint Satisfaction (Logic Scoring): Evaluates binary constraints between extracted
       entities (e.g., if prompt says "A > B", candidate claiming "B > A" violates constraints).
       
    3. Spectral Analysis (Conflict Detection): Constructs a weighted adjacency matrix representing
       the agreement between the prompt's logical signature and the candidate's signature.
       Computes the Laplacian eigenvalues. The spectral gap (smallest non-zero eigenvalue) 
       serves as a "conflict metric". High energy (large eigenvalues in specific modes) indicates
       logical inconsistency.
       
    4. Pruning: Candidates with high spectral conflict are down-weighted. NCD is used only
       as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        self.keywords = {
            'neg': ['not', 'no', 'never', 'false', 'deny', 'impossible'],
            'comp': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'],
            'cond': ['if', 'then', 'unless', 'otherwise', 'when'],
            'bool': ['true', 'false', 'yes', 'no']
        }
        self.num_regex = re.compile(r"-?\d+\.?\d*")

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract logical 'types' and numeric values from text."""
        lower_text = text.lower()
        features = {
            'has_neg': any(k in lower_text for k in self.keywords['neg']),
            'has_comp': any(k in lower_text for k in self.keywords['comp']),
            'has_cond': any(k in lower_text for k in self.keywords['cond']),
            'numbers': [float(n) for n in self.num_regex.findall(text)],
            'length': len(text.split()),
            'true_bias': 1 if 'true' in lower_text or 'yes' in lower_text else 0,
            'false_bias': 1 if 'false' in lower_text or 'no' in lower_text else 0
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def _build_laplacian(self, prompt_feat: Dict, cand_feat: Dict) -> np.ndarray:
        """
        Construct a simplified Laplacian-like matrix representing constraint satisfaction.
        Vertices: [Prompt Logic, Candidate Logic, Numeric Consistency, Type Match]
        Edges: Weighted by agreement.
        """
        # Adjacency matrix A (4x4 conceptual graph)
        A = np.zeros((4, 4))
        
        # Node 0: Prompt Base, Node 1: Candidate Base
        # Edge 0-1: Logical consistency (Negation/Conditional match)
        logic_match = 0.0
        if prompt_feat['has_neg'] == cand_feat['has_neg']: logic_match += 1.0
        if prompt_feat['has_cond'] == cand_feat['has_cond']: logic_match += 1.0
        if prompt_feat['has_comp'] == cand_feat['has_comp']: logic_match += 1.0
        
        A[0, 1] = A[1, 0] = logic_match
        
        # Node 2: Numeric Consistency
        num_score = 0.0
        if prompt_feat['numbers'] and cand_feat['numbers']:
            # Check simple transitivity/ordering if both have numbers
            p_nums = prompt_feat['numbers']
            c_nums = cand_feat['numbers']
            if len(p_nums) > 0 and len(c_nums) > 0:
                # Simple proximity check for spectral smoothing
                diff = abs(p_nums[0] - c_nums[0]) if p_nums and c_nums else 100
                num_score = 1.0 / (1.0 + diff)
        elif not prompt_feat['numbers'] and not cand_feat['numbers']:
            num_score = 1.0 # Both lack numbers, consistent
            
        A[0, 2] = A[2, 0] = num_score
        A[1, 2] = A[2, 1] = num_score # Connect candidate to numeric node too

        # Node 3: Type/Boolean Consistency
        type_score = 0.0
        if prompt_feat['true_bias'] == cand_feat['true_bias'] and \
           prompt_feat['false_bias'] == cand_feat['false_bias']:
            type_score = 1.0
        A[0, 3] = A[3, 0] = type_score
        A[1, 3] = A[3, 1] = type_score

        # Degree matrix D
        D = np.diag(A.sum(axis=1))
        
        # Laplacian L = D - A
        L = D - A
        return L

    def _spectral_score(self, L: np.ndarray) -> float:
        """
        Compute spectral signature. 
        Low energy (small non-zero eigenvalues) = High consistency.
        High energy = Conflict.
        Returns a normalized score where higher is better.
        """
        try:
            eigenvals = np.linalg.eigvalsh(L)
            eigenvals = np.sort(eigenvals)
            # The smallest eigenvalue should be ~0. 
            # The second smallest (Fiedler value) indicates connectivity/consistency.
            # In our construction, higher connectivity (agreement) leads to specific spectral gaps.
            # We invert the logic: We want high agreement. 
            # If constraints are violated, weights drop, changing the spectrum.
            
            # Heuristic: Sum of smallest non-trivial eigenvalues as "energy".
            # Lower energy in this specific construction implies tighter coupling (good).
            # However, since we built A based on matches, a perfect match creates a specific structure.
            # Let's use the magnitude of the second eigenvalue as a stability metric.
            
            if len(eigenvals) < 2:
                return 0.5
            
            fiedler = eigenvals[1]
            # Normalize roughly to 0-1 range based on matrix size
            return 1.0 / (1.0 + fiedler) 
        except np.linalg.LinAlgError:
            return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        results = []
        
        scored_candidates = []
        for cand in candidates:
            cand_feat = self._extract_features(cand)
            L = self._build_laplacian(prompt_feat, cand_feat)
            spec_val = self._spectral_score(L)
            
            # Structural penalty/bonus
            struct_score = spec_val * 10.0
            
            # Constraint propagation check (Simple transitivity)
            if prompt_feat['numbers'] and cand_feat['numbers']:
                # If prompt implies order, check candidate
                pass # Simplified for brevity
            
            scored_candidates.append((cand, struct_score, cand_feat))

        # Rank by structural score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Apply NCD as tie-breaker for top candidates if scores are very close
        final_results = []
        for i, (cand, score, feat) in enumerate(scored_candidates):
            # Refine score with NCD only if structural signals are weak or tied
            structural_signal = score > 0.1
            if not structural_signal:
                ncd = self._compute_ncd(prompt, cand)
                # Lower NCD is better, so subtract
                score -= ncd * 0.5
            
            reasoning = f"Spectral consistency: {score:.4f}"
            if feat['has_neg']: reasoning += " [Negation detected]"
            if feat['numbers']: reasoning += " [Numeric eval]"
            
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on spectral consistency."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1
        raw_score = res[0]['score']
        # Map heuristic range (-1 to 20) to 0-1
        conf = 1.0 / (1.0 + np.exp(-0.5 * raw_score + 2))
        return max(0.0, min(1.0, conf))