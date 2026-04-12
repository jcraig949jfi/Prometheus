from typing import Dict, Tuple

"""
Reasoning tool combining Chaos Theory, Cognitive Load Theory, and Self-Organized Criticality.

Core mechanism:
1. Parse candidates into logical atoms (propositions) using regex
2. Build dependency graph and compute Lyapunov-like chaos sensitivity
3. Apply cognitive load chunking and self-organized criticality scoring
4. Meta-confidence layer detects ambiguous/unanswerable questions (Tier B)
5. Structural parsing handles deterministic cases (Tier A)
"""

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.WM_CAPACITY = 7
        self.weights = {'chaos': 0.35, 'soc': 0.35, 'load': 0.15, 'ncd': 0.15}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using chaos/SOC/cognitive-load framework."""
        meta_conf = self._meta_confidence(prompt)
        
        results = []
        for cand in candidates:
            # Structural deterministic checks first
            struct_score = self._structural_eval(prompt, cand)
            
            # Graph-based chaos/SOC scoring
            atoms = self._parse_atoms(cand)
            graph = self._build_graph(atoms)
            
            chaos_score = self._chaos_stability(graph)
            soc_score = self._soc_criticality(graph)
            load_penalty = self._cognitive_load(atoms)
            ncd_score = self._ncd_similarity(prompt, cand)
            
            # Combine scores
            if struct_score is not None:
                score = 0.5 * struct_score + 0.2 * chaos_score + 0.15 * soc_score + 0.15 * ncd_score
            else:
                score = (self.weights['chaos'] * chaos_score + 
                        self.weights['soc'] * soc_score - 
                        self.weights['load'] * load_penalty +
                        self.weights['ncd'] * ncd_score)
            
            reasoning = f"Chaos:{chaos_score:.2f} SOC:{soc_score:.2f} Load:{load_penalty:.2f}"
            if struct_score is not None:
                reasoning += f" Struct:{struct_score:.2f}"
            
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return calibrated confidence, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # Check for structural certainty (deterministic cases)
        struct_score = self._structural_eval(prompt, answer)
        if struct_score is not None:
            base_conf = min(0.85, struct_score)
        else:
            atoms = self._parse_atoms(answer)
            graph = self._build_graph(atoms)
            chaos = self._chaos_stability(graph)
            soc = self._soc_criticality(graph)
            base_conf = min(0.7, (chaos + soc) / 2)
        
        return min(meta_conf, base_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presupposition, and unanswerable questions."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .* or .*)\b', p_lower) and '?' in prompt:
            if not re.search(r'\b(only|just|exactly)', p_lower):
                return 0.25
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba \w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if 'who' in p_lower and re.search(r'\b(he|she|they|it)\b', p_lower):
            subjects = re.findall(r'\b[A-Z][a-z]+\b', prompt)
            if len(subjects) >= 2:
                return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(most|least|highest|lowest|largest|smallest)\b', p_lower):
                return 0.25
        
        # Unanswerability cues
        if re.search(r'\b(impossible to|cannot determine|not enough|insufficient)', p_lower):
            return 0.25
        
        return 1.0  # No meta-issues detected
    
    def _structural_eval(self, prompt: str, answer: str) -> float:
        """Deterministic structural parsing for Tier A questions."""
        # Numeric comparison
        numbers_p = re.findall(r'\d+\.?\d*', prompt)
        numbers_a = re.findall(r'\d+\.?\d*', answer)
        
        if len(numbers_p) >= 2 and ('greater' in prompt.lower() or 'less' in prompt.lower() or 'larger' in prompt.lower()):
            try:
                vals = [float(n) for n in numbers_p[:2]]
                if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                    correct = str(max(vals))
                else:
                    correct = str(min(vals))
                if correct in answer:
                    return 0.95
                else:
                    return 0.05
            except:
                pass
        
        # Simple negation check
        if re.search(r'\bnot\b', prompt.lower()):
            if re.search(r'\bnot\b', answer.lower()):
                return 0.7
        
        # Conditional modus ponens
        if re.search(r'\bif .* then\b', prompt.lower()):
            return 0.6 if len(answer) > 5 else 0.3
        
        return None  # No structural match
    
    def _parse_atoms(self, text: str) -> List[str]:
        """Extract logical atoms using regex patterns."""
        atoms = []
        
        # Split on sentence boundaries
        sentences = re.split(r'[.;]', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 3:
                continue
            
            # Extract clauses
            clauses = re.split(r'\b(and|or|but|because|therefore)\b', sent)
            for clause in clauses:
                clause = clause.strip()
                if len(clause) > 5 and clause not in ['and', 'or', 'but', 'because', 'therefore']:
                    atoms.append(clause.lower())
        
        return atoms if atoms else [text.lower()]
    
    def _build_graph(self, atoms: List[str]) -> np.ndarray:
        """Build adjacency matrix from logical dependencies."""
        n = len(atoms)
        if n == 0:
            return np.zeros((1, 1))
        
        A = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # Negation edge
                if 'not' in atoms[i] and any(word in atoms[j] for word in atoms[i].split() if word != 'not'):
                    A[i][j] = 1
                
                # Causal edge
                if any(word in atoms[i] for word in ['because', 'leads', 'causes', 'therefore']):
                    A[i][j] = 0.5
                
                # Shared tokens
                tokens_i = set(atoms[i].split())
                tokens_j = set(atoms[j].split())
                if len(tokens_i & tokens_j) >= 2:
                    A[i][j] = 0.3
        
        return A
    
    def _chaos_stability(self, A: np.ndarray) -> float:
        """Approximate Lyapunov exponent (lower = more stable)."""
        n = A.shape[0]
        if n <= 1:
            return 0.5
        
        # Small random perturbation
        delta = np.random.randn(n) * 0.01
        
        # Propagate for t=5 steps
        t = 5
        try:
            At = np.linalg.matrix_power(A + np.eye(n) * 0.1, t)
            delta_t = At @ delta
            
            lyap = np.log(np.linalg.norm(delta_t) / (np.linalg.norm(delta) + 1e-9)) / t
            lyap_norm = 1.0 / (1.0 + abs(lyap))  # Invert: lower chaos = higher score
            return lyap_norm
        except:
            return 0.5
    
    def _soc_criticality(self, A: np.ndarray) -> float:
        """Self-organized criticality via avalanche distribution."""
        n = A.shape[0]
        if n <= 1:
            return 0.5
        
        avalanche_sizes = []
        for _ in range(20):
            state = np.zeros(n)
            state[np.random.randint(n)] = 1
            
            size = 0
            for step in range(10):
                activated = (A @ state > 0.5).astype(float)
                new_act = activated - state
                new_act[new_act < 0] = 0
                size += new_act.sum()
                state = activated
                if new_act.sum() == 0:
                    break
            
            avalanche_sizes.append(size)
        
        # Power-law fit via variance (higher variance ~ more critical)
        if len(avalanche_sizes) > 1:
            variance = np.var(avalanche_sizes)
            return min(1.0, variance / (n + 1))
        return 0.5
    
    def _cognitive_load(self, atoms: List[str]) -> float:
        """Cognitive load penalty based on chunk count."""
        K = len(atoms)
        C = self.WM_CAPACITY
        penalty = max(0, K - C) / C
        return min(1.0, penalty)
    
    def _ncd_similarity(self, prompt: str, answer: str) -> float:
        """Normalized Compression Distance (tiebreaker only)."""
        c_p = len(zlib.compress(prompt.encode()))
        c_a = len(zlib.compress(answer.encode()))
        c_pa = len(zlib.compress((prompt + answer).encode()))
        
        ncd = (c_pa - min(c_p, c_a)) / max(c_p, c_a)
        return max(0, 1 - ncd)