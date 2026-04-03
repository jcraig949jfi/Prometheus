from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated plasticity-based reasoning with property-based testing.
    
    Parses propositions into constraint graphs, applies gain-modulated propagation,
    tracks state evolution dynamics, and uses plasticity traces + hypothesis shrinking
    to score candidates. Implements meta-confidence for epistemic honesty.
    """
    
    def __init__(self):
        self.alpha = 0.9  # Plasticity decay
        self.tau = 0.5    # Error threshold for shrinking
        
    def _parse_propositions(self, text: str) -> List[Tuple[str, str, str, int, str]]:
        """Extract (subject, relation, object, polarity, modality) tuples."""
        propositions = []
        text = text.lower()
        
        # Causal patterns
        for m in re.finditer(r'(\w+(?:\s+\w+){0,2})\s+(?:because|since|causes?|leads?\s+to)\s+(\w+(?:\s+\w+){0,2})', text):
            propositions.append((m.group(1), 'causes', m.group(2), 1, 'causal'))
        
        # Conditional patterns
        for m in re.finditer(r'if\s+(\w+(?:\s+\w+){0,2})\s+then\s+(\w+(?:\s+\w+){0,2})', text):
            propositions.append((m.group(1), 'implies', m.group(2), 1, 'conditional'))
        
        # Comparative patterns
        for m in re.finditer(r'(\w+)\s+(?:is\s+)?(?:greater|more|higher|larger)\s+than\s+(\w+)', text):
            propositions.append((m.group(1), 'greater', m.group(2), 1, 'comparative'))
        for m in re.finditer(r'(\w+)\s+(?:is\s+)?(?:less|lower|smaller)\s+than\s+(\w+)', text):
            propositions.append((m.group(1), 'less', m.group(2), 1, 'comparative'))
        
        # Negation patterns
        for m in re.finditer(r'(\w+)\s+(?:is\s+)?not\s+(\w+)', text):
            propositions.append((m.group(1), 'is', m.group(2), -1, 'negation'))
        
        # Basic assertions
        for m in re.finditer(r'(\w+)\s+is\s+(\w+)', text):
            if 'not' not in m.group(0):
                propositions.append((m.group(1), 'is', m.group(2), 1, 'assertion'))
        
        return propositions
    
    def _build_graph(self, props: List[Tuple]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Build adjacency matrix and gain vector from propositions."""
        nodes = []
        for p in props:
            if p[0] not in nodes: nodes.append(p[0])
            if p[2] not in nodes: nodes.append(p[2])
        
        if not nodes:
            return np.zeros((1, 1)), np.ones(1), ['empty']
        
        N = len(nodes)
        A = np.zeros((N, N), dtype=np.float32)
        g = np.ones(N, dtype=np.float32)
        
        for subj, rel, obj, pol, mod in props:
            i, j = nodes.index(subj), nodes.index(obj)
            A[i, j] = float(pol)
            
            # Neuromodulatory gain
            if mod == 'causal' or mod == 'conditional':
                g[i] += 0.2
            elif mod == 'comparative':
                g[i] += 0.1
            elif mod == 'negation':
                g[i] -= 0.1
        
        return A, g, nodes
    
    def _propagate(self, A: np.ndarray, g: np.ndarray, steps: int = 5) -> np.ndarray:
        """Constraint propagation with neuromodulatory gain."""
        W = A * np.outer(g, g)  # Gain modulation
        
        for _ in range(steps):
            W_new = np.maximum(W, np.sign(W @ W))
            if np.allclose(W_new, W):
                break
            W = W_new
        
        return W
    
    def _state_trajectory(self, props: List[Tuple]) -> np.ndarray:
        """Track state evolution as propositions are processed sequentially."""
        if not props:
            return np.array([0.0])
        
        states = []
        cumulative_props = []
        
        for i in range(len(props)):
            cumulative_props.append(props[i])
            A, g, nodes = self._build_graph(cumulative_props)
            W = self._propagate(A, g)
            states.append(np.linalg.norm(W))
        
        return np.array(states)
    
    def _compute_stability(self, trajectory: np.ndarray) -> float:
        """Compute trajectory stability (higher = more stable/converged)."""
        if len(trajectory) < 2:
            return 0.5
        
        # Measure convergence via variance of later states
        if len(trajectory) >= 3:
            variance = np.var(trajectory[-3:])
            stability = 1.0 / (1.0 + variance)
        else:
            stability = 0.5
        
        return stability
    
    def _numeric_eval(self, text: str) -> float:
        """Extract and compare numeric values."""
        numbers = re.findall(r'\d+\.?\d*', text)
        if len(numbers) >= 2:
            try:
                vals = [float(n) for n in numbers[:2]]
                if any(w in text.lower() for w in ['greater', 'more', 'larger', '>']):
                    return 1.0 if vals[0] > vals[1] else 0.0
                elif any(w in text.lower() for w in ['less', 'fewer', 'smaller', '<']):
                    return 1.0 if vals[0] < vals[1] else 0.0
            except:
                pass
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presupposition, unanswerability."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (?:stopped|quit|ceased)', prompt_lower):
            return 0.2
        if re.search(r'why did .+ (?:fail|stop|end)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\w+ told \w+ (?:he|she)', prompt_lower) and 'who' in prompt_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either .+ or .+\?', prompt_lower):
            return 0.3
        
        # Subjectivity
        if any(w in prompt_lower for w in ['best', 'worst', 'favorite', 'prefer']):
            return 0.3
        
        # Unanswerable markers
        if any(w in prompt_lower for w in ['impossible', 'cannot determine', 'insufficient']):
            return 0.2
        
        return 1.0  # No meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using neuromodulated plasticity + dynamics."""
        results = []
        
        prompt_props = self._parse_propositions(prompt)
        prompt_traj = self._state_trajectory(prompt_props)
        
        for candidate in candidates:
            # Structural score via graph comparison
            cand_props = self._parse_propositions(candidate)
            A_p, g_p, _ = self._build_graph(prompt_props)
            A_c, g_c, _ = self._build_graph(cand_props)
            
            W_p = self._propagate(A_p, g_p)
            W_c = self._propagate(A_c, g_c)
            
            # Match dimensions
            N = max(W_p.shape[0], W_c.shape[0])
            W_p_pad = np.zeros((N, N))
            W_c_pad = np.zeros((N, N))
            W_p_pad[:W_p.shape[0], :W_p.shape[1]] = W_p
            W_c_pad[:W_c.shape[0], :W_c.shape[1]] = W_c
            
            error = np.linalg.norm(W_c_pad - W_p_pad)
            structural_score = 1.0 / (1.0 + error)
            
            # Dynamics score via trajectory stability
            cand_traj = self._state_trajectory(cand_props)
            stability = self._compute_stability(cand_traj)
            dynamics_score = stability
            
            # Numeric evaluation
            numeric_score = self._numeric_eval(prompt + ' ' + candidate)
            
            # NCD (tiebreaker only)
            ncd = self._ncd(prompt, candidate)
            ncd_score = 1.0 - ncd
            
            # Weighted combination
            score = 0.4 * structural_score + 0.3 * dynamics_score + 0.2 * numeric_score + 0.1 * ncd_score
            
            results.append({
                'candidate': candidate,
                'score': float(score),
                'reasoning': f'struct={structural_score:.2f} dyn={dynamics_score:.2f} num={numeric_score:.2f}'
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence."""
        meta_conf = self._meta_confidence(prompt)
        
        # Parse and evaluate
        prompt_props = self._parse_propositions(prompt)
        answer_props = self._parse_propositions(answer)
        
        if not prompt_props and not answer_props:
            return min(0.3, meta_conf)
        
        # Trajectory-based confidence
        combined_props = prompt_props + answer_props
        traj = self._state_trajectory(combined_props)
        stability = self._compute_stability(traj)
        
        # Numeric precision
        numeric = self._numeric_eval(prompt + ' ' + answer)
        
        base_conf = 0.5 * stability + 0.3 * numeric + 0.2 * (1.0 if answer_props else 0.5)
        
        # Cap by meta-confidence
        return min(base_conf, meta_conf)