import re
import numpy as np
import zlib


class ReasoningTool:
    """
    Judgment Calibrator using Measure Theory x Network Science x Adaptive Control.
    
    Parses logical structure into a graph, assigns belief measures, propagates
    constraints via network dynamics, and tunes beliefs with adaptive control.
    Prioritizes epistemic honesty: detects ambiguity and caps confidence on
    unanswerable/ambiguous questions.
    """
    
    def __init__(self):
        self.epsilon = 1e-4
        self.max_iter = 20
        self.eta = 0.05
    
    def _meta_confidence(self, prompt: str) -> float:
        """Evaluate prompt for ambiguity/unanswerability. Returns cap on confidence."""
        p = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you|did you|has|had).*(stop|quit|cease)', p):
            return 0.25
        if re.search(r'\bwhy (did|does|is|was).*(fail|wrong|bad)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p) and '?' in p:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p) and not re.search(r'\bonly\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better|worse)\b', p):
            if not re.search(r'\b(most|least|more|less|than|number|percent|count)\b', p):
                return 0.3
        
        # Unanswerable signals
        if re.search(r'\b(impossible|cannot determine|insufficient|not enough)\b', p):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _extract_numbers(self, text: str):
        """Extract numeric values with context."""
        nums = []
        for match in re.finditer(r'(\d+\.?\d*)', text):
            nums.append((float(match.group(1)), match.start()))
        return nums
    
    def _parse_logical_graph(self, prompt: str, candidate: str):
        """Parse text into logical graph with belief measures."""
        text = (prompt + " " + candidate).lower()
        
        # Extract atomic propositions (simplified: sentences/clauses)
        sentences = re.split(r'[.;]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        n = max(len(sentences), 1)
        
        # Feature matrix and adjacency
        A = np.zeros((n, n))
        beliefs = np.full(n, 0.5)  # Uniform prior
        
        for i, sent in enumerate(sentences):
            # Negation reduces belief
            if re.search(r'\b(not|no|never|neither|nor)\b', sent):
                beliefs[i] = 0.3
            
            # Conditional edges (if i then j)
            if re.search(r'\bif\b', sent):
                beliefs[i] = 0.6
                for j in range(i+1, n):
                    A[i, j] = 1.0  # Implication edge
            
            # Causal edges
            if re.search(r'\b(because|since|therefore|thus|so)\b', sent):
                if i > 0:
                    A[i-1, i] = 1.0
            
            # Comparative edges
            if re.search(r'\b(more|greater|higher|larger)\b', sent):
                for j in range(i+1, n):
                    A[i, j] = 0.5
            if re.search(r'\b(less|fewer|lower|smaller)\b', sent):
                for j in range(i+1, n):
                    A[i, j] = -0.5
        
        return A, beliefs, sentences
    
    def _propagate_beliefs(self, A, beliefs):
        """Constraint propagation via network dynamics."""
        n = len(beliefs)
        if n == 0:
            return beliefs
        
        for _ in range(self.max_iter):
            old_beliefs = beliefs.copy()
            
            # Network update: b_j += sum_i A_ij * b_i
            update = A.T @ beliefs
            beliefs = beliefs + 0.1 * update
            beliefs = np.clip(beliefs, 0, 1)
            
            if np.linalg.norm(beliefs - old_beliefs, 1) < self.epsilon:
                break
        
        return beliefs
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Deterministic structural scoring (50%+ of final score)."""
        score = 0.5  # Baseline
        p = prompt.lower()
        c = candidate.lower()
        
        # Numeric comparison
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            if re.search(r'\b(greater|more|larger|higher)\b', p):
                if c_nums[0][0] > p_nums[0][0]:
                    score += 0.3
            elif re.search(r'\b(less|fewer|smaller|lower)\b', p):
                if c_nums[0][0] < p_nums[0][0]:
                    score += 0.3
            elif re.search(r'\b(equal|same)\b', p):
                if abs(c_nums[0][0] - p_nums[0][0]) < 0.01:
                    score += 0.3
        
        # Negation handling
        p_neg = bool(re.search(r'\b(not|no|never|false)\b', p))
        c_neg = bool(re.search(r'\b(not|no|never|false)\b', c))
        if p_neg == c_neg:
            score += 0.1
        
        # Yes/No questions
        if re.search(r'\b(is|are|does|do|can|will)\b.*\?', p):
            if re.search(r'\b(yes|true|correct)\b', c) and not p_neg:
                score += 0.15
            elif re.search(r'\b(no|false|incorrect)\b', c) and p_neg:
                score += 0.15
        
        # Conditional reasoning
        if re.search(r'\bif\b.*\bthen\b', p):
            # Check modus ponens
            if_clause = re.search(r'if\s+([^,]+)', p)
            then_clause = re.search(r'then\s+([^.]+)', p)
            if if_clause and then_clause and if_clause.group(1).lower() in c:
                score += 0.2
        
        return min(score, 1.0)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (max 15% of score)."""
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by integrated belief measure."""
        results = []
        
        for cand in candidates:
            # Structural score (50%)
            struct_score = self._structural_score(prompt, cand)
            
            # Graph-based belief propagation (30%)
            A, beliefs, sents = self._parse_logical_graph(prompt, cand)
            beliefs = self._propagate_beliefs(A, beliefs)
            belief_score = np.mean(beliefs) if len(beliefs) > 0 else 0.5
            
            # NCD tiebreaker (15%)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Adaptive combination
            final_score = 0.55 * struct_score + 0.3 * belief_score + 0.15 * ncd_score
            
            # Generate reasoning
            reasoning = f"Structural: {struct_score:.2f}, Belief: {belief_score:.2f}, NCD: {ncd_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence [0,1] based on prompt properties and answer quality."""
        # First check meta-confidence (prompt ambiguity)
        meta_cap = self._meta_confidence(prompt)
        
        # Structural confidence
        struct_score = self._structural_score(prompt, answer)
        
        # Graph-based confidence
        A, beliefs, sents = self._parse_logical_graph(prompt, answer)
        beliefs = self._propagate_beliefs(A, beliefs)
        belief_score = np.mean(beliefs) if len(beliefs) > 0 else 0.5
        
        # Variance as uncertainty signal
        belief_var = np.var(beliefs) if len(beliefs) > 0 else 0.25
        uncertainty_penalty = min(belief_var * 2, 0.3)
        
        # Combine
        base_conf = 0.6 * struct_score + 0.4 * belief_score - uncertainty_penalty
        base_conf = np.clip(base_conf, 0, 1)
        
        # Apply meta-cap (epistemic honesty)
        final_conf = min(base_conf, meta_cap)
        
        # Never exceed 0.9 unless very high structural match
        if struct_score < 0.85:
            final_conf = min(final_conf, 0.85)
        
        return float(final_conf)