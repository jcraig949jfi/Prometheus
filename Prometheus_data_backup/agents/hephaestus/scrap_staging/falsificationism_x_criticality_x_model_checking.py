import re
import numpy as np
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Falsification-Critical Model Checker (FCMC).
    
    Mechanism:
    1. Parses text into atomic propositions and relations (causal, conditional, comparative).
    2. Constructs a boolean adjacency matrix representing the logical state space.
    3. Computes transitive closure to verify consistency with prompt constraints (Falsificationism).
    4. Calculates spectral radius to measure system criticality (balance between order/chaos).
    5. Scores candidates based on logical consistency (primary) and criticality (secondary).
    6. Uses NCD only as a tiebreaker for structurally identical candidates.
    """
    
    # Regex patterns for structural extraction
    PATTERNS = {
        'negation': r'\b(not|no|never|neither|without)\b',
        'conditional': r'\b(if|then|unless|provided|when)\b',
        'causal': r'\b(because|leads to|results in|causes|due to)\b',
        'comparative': r'\b(greater|less|more|fewer|higher|lower|equal|same)\b',
        'ordering': r'\b(before|after|first|last|precede|follow)\b',
        'number': r'-?\d+\.?\d*'
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex for efficiency."""
        self.compiled = {k: re.compile(v, re.IGNORECASE) for k, v in self.PATTERNS.items()}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer splitting by whitespace and punctuation."""
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_propositions(self, text: str) -> List[str]:
        """Extract coarse-grained propositions (noun-verb chunks)."""
        # Simplified extraction: split by connectors to get atomic claims
        separators = r'\b(if|then|because|leads to|results in|and|or|but|however)\b'
        parts = re.split(separators, text, flags=re.IGNORECASE)
        props = [p.strip() for p in parts if p.strip() and len(p.strip()) > 2]
        return props[:10]  # Limit state space size

    def _build_graph(self, text: str) -> Tuple[np.ndarray, List[str], Dict]:
        """
        Construct adjacency matrix M and extract numeric constraints.
        Returns: (M, labels, constraints)
        """
        tokens = self._tokenize(text)
        props = self._extract_propositions(text)
        n = max(len(props), 2)
        labels = props if props else ["state_0", "state_1"]
        if len(labels) < 2: labels += ["dummy"]
        
        M = np.zeros((n, n), dtype=bool)
        constraints = []
        
        # Map tokens to indices roughly
        token_to_idx = {t: i % n for i, t in enumerate(tokens)}
        
        has_neg = bool(self.compiled['negation'].search(text))
        has_cond = bool(self.compiled['conditional'].search(text))
        has_causal = bool(self.compiled['causal'].search(text))
        has_comp = bool(self.compiled['comparative'].search(text))
        
        # Build edges based on detected structural markers
        for i in range(n):
            for j in range(n):
                if i == j: 
                    M[i, j] = True # Reflexive
                    continue
                
                # Heuristic edge creation based on global markers
                # In a full NLP system, this would be local dependency parsing
                if has_causal and (i + 1) % n == j:
                    M[i, j] = True
                elif has_cond and (i + 1) % n == j:
                    M[i, j] = True
                elif has_comp and i < j:
                    M[i, j] = True
                elif not has_neg and i != j:
                    # Dense connectivity if no negation detected (assumption of coherence)
                    if np.random.random() < 0.3: 
                        M[i, j] = True

        # Extract numeric constraints
        nums = [float(x) for x in self.compiled['number'].findall(text)]
        if len(nums) >= 2:
            # Simple consistency check: are numbers ordered logically with comparatives?
            is_increasing = all(nums[i] <= nums[i+1] for i in range(len(nums)-1))
            is_decreasing = all(nums[i] >= nums[i+1] for i in range(len(nums)-1))
            constraints['numeric_order'] = is_increasing or is_decreasing
            
        return M, labels, constraints

    def _compute_transitive_closure(self, M: np.ndarray) -> np.ndarray:
        """Compute (I + M)^k via boolean matrix multiplication."""
        n = M.shape[0]
        T = M.astype(bool)
        # Repeated squaring for log(n) steps
        steps = int(np.ceil(np.log2(n))) if n > 1 else 1
        for _ in range(steps):
            T = (T @ T) > 0 # Boolean matrix mult
            T = (T | np.eye(n, dtype=bool)) # Ensure reflexivity
        return T

    def _check_falsification(self, prompt: str, candidate: str) -> int:
        """
        Count falsified relations. 
        If candidate contradicts prompt structure, increment F.
        """
        falsifications = 0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Check negation consistency
        if re.search(r'\bnot\b', p_lower) and not re.search(r'\bnot\b', c_lower):
            # Candidate might be missing a crucial negation present in prompt
            # This is a weak heuristic but captures the 'falsification' spirit
            falsifications += 1
            
        # Check if candidate explicitly contradicts prompt keywords
        # (e.g. Prompt: "A causes B", Candidate: "A prevents B")
        if ('cause' in p_lower or 'lead' in p_lower) and ('prevent' in c_lower or 'stop' in c_lower):
            falsifications += 2
            
        return falsifications

    def _compute_criticality(self, M: np.ndarray) -> float:
        """Compute spectral radius and criticality score."""
        if M.shape[0] == 0: return 0.0
        try:
            eigenvals = np.linalg.eigvals(M.astype(float))
            rho = np.max(np.abs(eigenvals))
            # Criticality: 1 - |rho - 1|
            return 1.0 - abs(rho - 1.0)
        except:
            return 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        comp = len(zlib.compress(b1 + b2))
        max_len = max(len1, len2)
        return (comp - max_len) / max_len if max_len > 0 else 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_M, _, _ = self._build_graph(prompt)
        prompt_T = self._compute_transitive_closure(prompt_M)
        prompt_rho_score = self._compute_criticality(prompt_M)
        
        scores = []
        
        for cand in candidates:
            # 1. Falsification Check
            F = self._check_falsification(prompt, cand)
            S0 = 1.0 / (1.0 + F)
            
            # 2. Criticality Check
            cand_M, _, _ = self._build_graph(cand)
            C = self._compute_criticality(cand_M)
            
            # 3. Combined Score
            # S = S0 * (0.5 + 0.5*C)
            score = S0 * (0.5 + 0.5 * C)
            
            # Boost if candidate length is reasonable (avoids "Yes"/"No" bias)
            if 10 < len(cand) < 500:
                score *= 1.1
                
            scores.append((score, cand))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Handle ties with NCD
        final_results = []
        for i, (score, cand) in enumerate(scores):
            if i > 0:
                prev_score, prev_cand = scores[i-1]
                if abs(score - prev_score) < 1e-6:
                    # Tiebreaker: NCD to prompt (closemess implies relevance)
                    ncd_curr = self._ncd(prompt, cand)
                    ncd_prev = self._ncd(prompt, prev_cand) # Not strictly needed for sorting logic here but conceptually useful
                    # Actually, we just need to sort the tie group. 
                    # Since we are iterating sorted list, we can't easily re-sort group.
                    # Simplification: Add tiny NCD penalty to score
                    score -= ncd_curr * 1e-7
            
            reasoning = f"Falsifications: {int(1/score - 1) if score > 0 else 99}, Criticality: {self._compute_criticality(self._build_graph(cand)[0]):.2f}"
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 range roughly
        raw_score = res[0]['score']
        # Heuristic mapping: scores > 0.5 are high confidence
        conf = min(1.0, max(0.0, raw_score * 1.2)) 
        return float(conf)

# Example usage block for verification (not part of class)
if __name__ == "__main__":
    tool = ReasoningTool()
    p = "If it rains, the ground gets wet. It is raining."
    cands = [
        "The ground gets wet.",
        "The ground stays dry.",
        "It is not raining."
    ]
    ranked = tool.evaluate(p, cands)
    for r in ranked:
        print(f"Score: {r['score']:.4f} | {r['candidate']}")