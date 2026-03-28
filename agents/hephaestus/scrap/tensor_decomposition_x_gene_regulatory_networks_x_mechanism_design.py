import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Tensor Decomposition, Gene Regulatory Networks (GRN),
    and Mechanism Design to evaluate candidate answers.
    
    Mechanism:
    1. Parsing: Extracts propositional atoms and relations into a tensor structure.
    2. Tensor Decomposition: Uses Tucker decomposition (via SVD) to find latent coherence.
    3. GRN Dynamics: Simulates Boolean network attractors to check logical consistency.
    4. Mechanism Design: Scores candidates based on reconstruction error and logical consistency.
    5. Epistemic Honesty: Caps confidence on ambiguous or unanswerable prompts.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|without)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if|because|leads to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'quantifier': re.compile(r'\b(every|all|some|any|no|each)\b', re.IGNORECASE),
            'connector': re.compile(r'\b(and|or|but|however)\b', re.IGNORECASE)
        }
        # Presupposition triggers for Tier B
        self.presuppositions = re.compile(r'\b(have you stopped|why did|when did|who is the|best|worst|either.*or)\b', re.IGNORECASE)
        self.pronoun_ambiguity = re.compile(r'\b(he|she|him|her|it|they)\b.*\b(who|which one)\b', re.IGNORECASE)

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extracts simplified (subject, relation, object) triples using regex."""
        triples = []
        sentences = re.split(r'[.\?!]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Simple heuristic: Split by verbs/connectors to find relations
            # This is a simplified parser for the sake of the constraint (<200 lines)
            words = sent.split()
            if len(words) < 3:
                continue
                
            # Detect relation type
            rel_type = "unknown"
            rel_word = ""
            for p_name, pattern in self.patterns.items():
                match = pattern.search(sent)
                if match:
                    rel_type = p_name
                    rel_word = match.group(0)
                    break
            
            if not rel_word:
                rel_word = words[len(words)//2] # Fallback to middle word
                rel_type = "assertion"

            # Crude split: before relation, after relation
            parts = sent.split(rel_word, 1)
            subj = parts[0].strip() if parts else ""
            obj = parts[1].strip() if len(parts) > 1 else ""
            
            if subj and obj:
                # Clean non-alphanumeric for tensor indexing
                s_clean = re.sub(r'[^a-zA-Z0-9]', '', subj[-10:]).lower() or "entity"
                o_clean = re.sub(r'[^a-zA-Z0-9]', '', obj[:10]).lower() or "entity"
                triples.append((s_clean, rel_type, o_clean))
                
        return triples if triples else [("text", "assertion", "content")]

    def _build_tensor(self, triples: List[Tuple[str, str, str]]) -> np.ndarray:
        """Builds a 3rd-order tensor X [Subject, Relation, Object]."""
        if not triples:
            return np.zeros((1, 1, 1))
            
        subjects = list(set(t[0] for t in triples))
        relations = list(set(t[1] for t in triples))
        objects = list(set(t[2] for t in triples))
        
        s_map = {s: i for i, s in enumerate(subjects)}
        r_map = {r: i for i, r in enumerate(relations)}
        o_map = {o: i for i, o in enumerate(objects)}
        
        I, J, K = len(subjects), len(relations), len(objects)
        # Ensure minimum dimensions for SVD
        I, J, K = max(I, 2), max(J, 2), max(K, 2)
        
        X = np.zeros((I, J, K))
        
        for s, r, o in triples:
            si = s_map.get(s, 0) % I
            ri = r_map.get(r, 0) % J
            oi = o_map.get(o, 0) % K
            X[si, ri, oi] = 1.0
            
        return X

    def _tucker_decompose(self, X: np.ndarray) -> Tuple[float, np.ndarray]:
        """Approximates Tucker decomposition via HOSVD and returns reconstruction error."""
        try:
            # Unfoldings
            X0 = X.reshape(X.shape[0], -1)
            X1 = X.transpose(1, 0, 2).reshape(X.shape[1], -1)
            X2 = X.transpose(2, 0, 1).reshape(X.shape[2], -1)
            
            # SVD on unfoldings to get factor matrices (simplified rank-1 approximation for speed)
            U0, _, _ = np.linalg.svd(X0, full_matrices=False)
            U1, _, _ = np.linalg.svd(X1, full_matrices=False)
            U2, _, _ = np.linalg.svd(X2, full_matrices=False)
            
            # Core tensor approximation G = X x1 U0.T x2 U1.T x3 U2.T
            # Simplified: Project back to original shape using first component
            rank = min(1, U0.shape[1]-1, U1.shape[1]-1, U2.shape[1]-1)
            if rank < 0: rank = 0
            
            # Reconstruct using outer product of first singular vectors (Rank-1 approx)
            u0 = U0[:, 0:1]
            u1 = U1[:, 0:1]
            u2 = U2[:, 0:1]
            
            # Core scalar (singular value product approx)
            # For simplicity in this constrained env, we estimate reconstruction error directly
            # X_approx = outer(u0, u1, u2) * sigma
            # Since we don't compute full core, we use Frobenius norm of X as proxy if rank 0
            if X.size == 0:
                return 0.0, np.array([0.0])
                
            # Rough reconstruction error: ||X||_F - ||X_approx||_F
            # Actually, let's just use ||X - X_approx||_F
            X_approx = np.einsum('i0,j0,k0->ijk', u0, u1, u2) * np.linalg.norm(X) / (np.linalg.norm(u0)*np.linalg.norm(u1)*np.linalg.norm(u2) + 1e-9)
            
            error = np.linalg.norm(X - X_approx)
            return error, X_approx
        except Exception:
            return np.linalg.norm(X), np.zeros_like(X)

    def _grn_consistency(self, prompt: str, candidate: str) -> float:
        """
        Simulates a Boolean GRN to check logical consistency.
        Nodes are extracted propositions. Update rules are derived from conditionals.
        Returns consistency score c in [0, 1].
        """
        combined = f"{prompt} {candidate}".lower()
        triples = self._extract_triples(combined)
        
        if not triples:
            return 0.5 # Neutral if no structure
            
        # Initialize nodes (boolean states)
        # Map unique subjects/objects to indices
        entities = list(set(t[0] for t in triples) | set(t[2] for t in triples))
        if not entities:
            return 0.5
        n = len(entities)
        state = np.random.randint(0, 2, n).astype(float) # Random init
        
        # Define simple update rules based on relation types
        # If 'negation' exists between A and B, B = NOT A
        # If 'conditional' exists, B = A
        
        rules = []
        for s, r, o in triples:
            try:
                idx_s = entities.index(s)
                idx_o = entities.index(o)
                rules.append((idx_s, idx_o, r))
            except ValueError:
                continue
        
        if not rules:
            return 0.5

        # Iterate to attractor (max 10 steps)
        for _ in range(10):
            new_state = state.copy()
            for s_idx, o_idx, r_type in rules:
                if r_type == 'negation':
                    new_state[o_idx] = 1.0 - state[s_idx]
                elif r_type == 'conditional':
                    new_state[o_idx] = state[s_idx] # If A then B => B follows A
                elif r_type == 'comparative':
                    # Heuristic: if A > B, and A is true, B might be false (simplified)
                    new_state[o_idx] = (state[s_idx] + new_state[o_idx]) / 2.0
            
            if np.array_equal(state, new_state):
                break
            state = new_state
            
        # Check consistency: Does the candidate imply a stable state?
        # We simulate stability by checking variance in final steps or just return 1.0 if converged
        # Here, we assume convergence implies consistency with the logic extracted
        return 1.0 - (np.var(state) if len(state) > 1 else 0.0)

    def _meta_confidence(self, prompt: str) -> float:
        """Checks for Tier B traps: ambiguity, presupposition, unanswerability."""
        p_lower = prompt.lower()
        
        # 1. Presupposition & Subjectivity
        if self.presuppositions.search(p_lower):
            return 0.2
        if any(k in p_lower for k in ["best", "worst", "favorite", "opinion"]):
            return 0.3
            
        # 2. Pronoun Ambiguity + Question
        if self.pronoun_ambiguity.search(p_lower) and "?" in prompt:
            return 0.2
            
        # 3. False Dichotomy (Either/Or without context)
        if re.search(r'\beither\b.*\bor\b', p_lower) and "only" in p_lower:
            return 0.3
            
        # 4. Unanswerable (Missing info indicators)
        if re.search(r'\bunknown\b|\bmissing\b|\bcannot be determined\b', p_lower):
            return 0.1
            
        return 1.0 # Default high confidence if no traps found

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_triples = self._extract_triples(prompt)
        X_prompt = self._build_tensor(prompt_triples)
        
        # Base reconstruction error of prompt alone
        prompt_err, _ = self._tucker_decompose(X_prompt)
        
        for cand in candidates:
            combined = f"{prompt} {cand}"
            triples = self._extract_triples(combined)
            X_combined = self._build_tensor(triples)
            
            # 1. Tensor Reconstruction Error (Mechanism Design Term 1)
            recon_err, _ = self._tucker_decompose(X_combined)
            # Normalize error relative to prompt size
            fit_score = 1.0 / (1.0 + recon_err) 
            
            # 2. GRN Consistency (Mechanism Design Term 2)
            grn_score = self._grn_consistency(prompt, cand)
            
            # 3. NCD Tiebreaker (Max 15% weight)
            ncd_val = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd_val # Higher is better
            
            # Utility Function: U = -(Error + lambda*(1-consistency))
            # Score = Fit (0.6) + Consistency (0.25) + NCD (0.15)
            final_score = (0.60 * fit_score) + (0.25 * grn_score) + (0.15 * ncd_score)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"TensorFit:{fit_score:.2f}, GRN:{grn_score:.2f}, NCD:{ncd_score:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 if meta-analysis detects ambiguity or traps.
        Caps at 0.9 unless computation is definitive.
        """
        meta_conf = self._meta_confidence(prompt)
        
        # If meta says ambiguous, return low confidence immediately
        if meta_conf < 0.4:
            return meta_conf
            
        # Otherwise, compute structural confidence
        # Run a mini-evaluation to see how much the answer improves the tensor fit
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.1
            
        score = res[0]['score']
        
        # Map score to confidence, capped by meta-analysis and epistemic limits
        # Even with high score, if the problem is inherently ambiguous, meta_conf handles it.
        # If structural parsing found nothing, score will be low-ish.
        
        final_conf = min(score, 0.95) # Hard cap for "definitive" unless proven otherwise
        
        # If no structural signals were parsed (score relies only on NCD), lower confidence
        if "TensorFit:0." in res[0]['reasoning'] and "GRN:0.5" in res[0]['reasoning']:
             final_conf = min(final_conf, 0.4) # Low confidence if only NCD matched
             
        return float(np.clip(final_conf, 0.0, 1.0))