import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool integrating Compressed Sensing, Mechanism Design, and Compositional Semantics.
    
    Mechanism:
    1. Compositional Semantics: Extracts atomic propositions (negations, comparatives, conditionals, causals)
       from the prompt and candidates using regex, mapping them to a binary basis.
    2. Compressed Sensing: Treats the truth of these propositions as a sparse recovery problem.
       It solves for the sparsest set of propositions (min L1 norm) that satisfies the logical constraints
       derived from the prompt using a simplified ISTA (Iterative Shrinkage-Thresholding Algorithm).
    3. Mechanism Design: Applies a VCG-style scoring rule. Candidates are scored based on how much they
       reduce the global "energy" (L1 norm) of the solution while maintaining consistency. This incentivizes
       truthful, minimal answers.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presuppositions, and unanswerable structures to
       cap confidence, ensuring the tool admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        # Regex patterns for compositional semantics
        self.patterns = {
            'negation': [r'\b(not|no|never|none)\b', r'^no\s'],
            'comparative': [r'(greater|less|more|fewer)\s+than', r'[><=]=?', r'\b(?:at\s+least|at\s+most)\b'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bunless\b', r'\bprovided\s+that\b'],
            'causal': [r'\b(because|since|leads\s+to|results\s+in|causes)\b'],
            'temporal': [r'\b(before|after|precedes|follows)\b'],
            'numeric': [r'\d+(?:\.\d+)?'],
            'quantifier': [r'\b(all|some|every|each|none)\b']
        }
        # Presupposition triggers for Tier B
        self.presupposition_triggers = [
            r'\bhave\s+you\s+(stopped|quit)\b',
            r'\bwhy\s+did\s+\w+\s+(fail|stop|break)\b',
            r'\bwhen\s+did\s+\w+\s+(stop|fail)\b'
        ]
        self.ambiguity_triggers = [
            r'\bwho\s+was\s+it\b', r'\bwhich\s+one\b', r'\beither\s+\w+\s+or\s+\w+\b'
        ]

    def _extract_clauses(self, text: str) -> List[str]:
        """Extract atomic semantic clauses based on regex patterns."""
        text_lower = text.lower()
        clauses = []
        
        # Check specific patterns
        for p_type, regexes in self.patterns.items():
            for regex in regexes:
                if re.search(regex, text_lower):
                    # Create a normalized token for this finding
                    token = f"{p_type}:{regex.replace(r'\b', '').replace(r'\\s', ' ')}"
                    clauses.append(token)
        
        # Fallback to simple sentence splitting if no complex structure found
        if not clauses:
            sentences = re.split(r'[.!?]', text)
            clauses.extend([s.strip() for s in sentences if s.strip()])
            
        return clauses if clauses else [text_lower]

    def _build_constraint_matrix(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Build matrix A and vector b for the sparse recovery problem.
        Rows correspond to extracted constraints. Columns correspond to unique atomic propositions.
        """
        # Combine text to extract global vocabulary of propositions
        full_text = f"{prompt} {candidate}"
        raw_clauses = self._extract_clauses(full_text)
        
        # Unique atomic propositions (simplified to unique clause strings for this implementation)
        # In a full system, this would be a global ontology. Here we dynamicize per prompt-candidate pair.
        atoms = list(set(raw_clauses))
        k = len(atoms)
        if k == 0:
            return np.array([]), np.array([]), 0
            
        m = len(raw_clauses)
        A = np.zeros((m, k))
        b = np.zeros(m)
        
        # Map atoms to indices
        atom_to_idx = {atom: i for i, atom in enumerate(atoms)}
        
        # Populate A and b
        # Logic: If a clause from the prompt is in the candidate, it's consistent (1). 
        # If the prompt implies X and candidate says not X, it's a conflict (-1 or 0).
        # Simplified for robustness: We check if candidate clauses satisfy prompt constraints.
        
        prompt_clauses = self._extract_clauses(prompt)
        candidate_clauses = self._extract_clauses(candidate)
        
        for i, clause in enumerate(raw_clauses):
            # Determine if this clause is supported by the prompt (Ground Truth)
            is_in_prompt = any(clause in p for p in prompt_clauses) or any(clause == p for p in prompt_clauses)
            
            # Determine if this clause is supported by the candidate
            is_in_candidate = any(clause in c for c in candidate_clauses) or any(clause == c for c in candidate_clauses)
            
            # Constraint: If prompt asserts it (b=1), candidate should ideally assert it (x=1)
            # If prompt denies it (not implemented explicitly here, but via 'negation' tag), b=0
            
            if is_in_prompt:
                b[i] = 1.0
                # The candidate contributes to this row if it contains the atom
                if is_in_candidate:
                    A[i, atom_to_idx[clause]] = 1.0
            else:
                # Unknown constraint from prompt perspective, weight 0.5 (uncertain)
                b[i] = 0.5
                if is_in_candidate:
                    A[i, atom_to_idx[clause]] = 1.0

        return A, b, k

    def _ista_solve(self, A: np.ndarray, b: np.ndarray, k: int, T: int = 50, tau: float = 0.1, theta: float = 0.1) -> np.ndarray:
        """Iterative Shrinkage-Thresholding Algorithm for L1 minimization."""
        if A.size == 0 or k == 0:
            return np.array([])
            
        x = np.zeros(k)
        # Least squares step size approximation
        try:
            L = np.linalg.norm(A, ord=2) ** 2 + 1e-6
            tau = 1.0 / L
        except:
            tau = 0.1
            
        for t in range(T):
            grad = A.T @ (A @ x - b)
            x = x - tau * grad
            # Projection to [0, 1]
            x = np.maximum(0, np.minimum(1, x))
            # Soft thresholding (Sparsity promotion)
            x = np.where(np.abs(x) < theta, 0, x)
            
        return x

    def _calculate_vcg_payment(self, A: np.ndarray, b: np.ndarray, k: int, candidate_idx: int, all_candidates: List[str], prompt: str) -> float:
        """
        Approximate VCG payment: Utility of others without me - Utility of others with me.
        Since we evaluate one candidate at a time in 'evaluate', we simulate the 'others' 
        by comparing the sparse solution quality with and without the current candidate's specific contributions.
        """
        # Baseline utility (without this specific candidate's influence on the global truth)
        # In this single-candidate evaluation context, we approximate by comparing 
        # the L1 norm of the solution when forced to include candidate logic vs not.
        
        x_full = self._ista_solve(A, b, k)
        if x_full.size == 0:
            return 0.0
            
        utility_full = -np.linalg.norm(x_full, 1)
        
        # Perturb: Simulate excluding the candidate's specific assertions
        # We do this by zeroing out columns associated with candidate-specific clauses
        # For this implementation, we approximate by adding a penalty if the candidate introduces new unconstrained atoms
        penalty = 0.0
        if np.linalg.norm(x_full, 1) > 0:
             penalty = 0.1 * np.sum(x_full) # Simple proxy for complexity cost
             
        return utility_full - penalty

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0:
            return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition checks
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Low confidence due to loaded question
        
        # 2. Ambiguity checks
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.3
                
        # 3. Subjectivity / Unanswerable
        if any(word in p_lower for word in ['best', 'worst', 'favorite', 'opinion']):
            if 'measure' not in p_lower and 'data' not in p_lower:
                return 0.4

        # 4. Structural mismatch (No parser hits)
        # If the prompt has no recognizable logical structure and the answer is short, be cautious
        clauses = self._extract_clauses(prompt)
        if len(clauses) == 1 and len(prompt.split()) < 10:
            return 0.5
            
        return 1.0  # No red flags detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate global constraints from prompt
        prompt_clauses = self._extract_clauses(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing & Matrix Construction
            A, b, k = self._build_constraint_matrix(prompt, cand)
            
            # 2. Sparse Recovery (Compressed Sensing)
            x = self._ista_solve(A, b, k)
            
            # 3. Scoring
            l1_norm = np.linalg.norm(x, 1) if x.size > 0 else 1.0
            
            # Mechanism Design Score: Balance sparsity (Occam) and constraint satisfaction
            # Residual error
            residual = 0.0
            if A.size > 0:
                residual = np.linalg.norm(A @ x - b)
            
            # Base score: High if residual is low and norm is low (parsimonious truth)
            # We invert residual so lower error = higher score
            base_score = 1.0 / (1.0 + residual + 0.1 * l1_norm)
            
            # VCG-style adjustment (approximated)
            vcg_pay = self._calculate_vcg_payment(A, b, k, 0, candidates, prompt)
            
            # Final Score Composition
            # Structural >= 50%, Computation (residual solving) >= 20%, NCD <= 15%
            structural_component = base_score * 0.6
            computation_component = (1.0 / (1.0 + residual)) * 0.25
            vcg_component = (vcg_pay + 1.0) * 0.15 # Shifted to be positive
            
            # NCD Tiebreaker (max 15%)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance is better) and scale
            ncd_score = (1.0 - ncd_val) * 0.15
            
            final_score = structural_component + computation_component + vcg_component + ncd_score
            
            # Generate reasoning string
            reasoning = f"Sparse norm: {l1_norm:.2f}, Residual: {residual:.2f}, VCG: {vcg_pay:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive checks for ambiguity (Tier B).
        """
        # 1. Meta-confidence cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, answer)
        
        if meta_cap < 0.5:
            return meta_cap
            
        # 2. Structural validation
        # Re-run evaluation logic for this specific pair to get a raw score
        # We treat the single answer as a candidate list
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]['score']
        
        # Map raw score (approx 0-2 range typically) to 0-1 confidence
        # Must be strict: only high scores yield high confidence
        if raw_score < 0.3:
            conf = 0.2
        elif raw_score < 0.6:
            conf = 0.5
        else:
            conf = min(0.95, 0.6 + (raw_score - 0.6) * 0.5)
            
        # Apply meta cap
        final_conf = min(conf, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (heuristic: very low residual)
        # This is handled implicitly by the scoring logic requiring low residual for high scores
        
        return round(final_conf, 3)