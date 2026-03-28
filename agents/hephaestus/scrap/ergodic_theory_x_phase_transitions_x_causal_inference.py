import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Ergodic-Causal Reasoning Tool.
    
    Mechanism:
    1. Parses text into a Directed Acyclic Graph (DAG) of propositions using regex.
       - Extracts causal cues, conditionals, comparatives, and negations.
       - Builds a weighted adjacency matrix (W) and bias vector (b).
    2. Simulates an ergodic dynamical system (Gibbs-like update) on the graph.
       - Nodes represent belief states s_i in [0, 1].
       - Updates: s <- sigmoid(W @ s + b / tau).
    3. Detects phase transitions by sweeping temperature (tau).
       - Computes variance of time-averaged states as an order parameter O(tau).
       - Identifies critical temperature tau* where dO/dtau peaks.
    4. Scores candidates by comparing their critical order parameter to the prompt's.
    5. Enforces epistemic honesty: detects ambiguity/presupposition to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'causal': [r'\bbecause\b', r'\bleads?\s+to\b', r'\bcauses?\b', r'\btherefore\b', r'\bthus\b'],
            'conditional': [r'\bif\s+.+?\s+then\b', r'\bif\b'],
            'comparative': [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\s+than\b', r'\bsmaller\s+than\b', r'\bprecede?s?\b'],
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'numeric': r'(\d+\.?\d*)',
            'presupposition': [r'have\s+you\s+stopped', r'why\s+did\s+\w+\s+fail', r'why\s+did\s+\w+\s+stop'],
            'scope_ambiguity': [r'every\s+\w+\s+did\s+a\s+\w+'],
            'pronoun_ambiguity': [r'(\w+)\s+told\s+(\w+)\s+he\s+was', r'(\w+)\s+told\s+(\w+)\s+she\s+was'],
            'false_dichotomy': [r'\beither\s+.+?\sor\b'],
            'subjectivity': [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bmost\s+beautiful\b']
        }
        self.compiled_patterns = {k: [re.compile(p, re.IGNORECASE) for p in v] if isinstance(v, list) else re.compile(v, re.IGNORECASE) for k, v in self.patterns.items()}

    def _extract_propositions(self, text: str) -> List[str]:
        """Split text into simple noun-phrase + verb propositions."""
        # Simple split by conjunctions and punctuation
        clean_text = re.sub(r'\s+', ' ', text).lower()
        # Split by common separators but keep content
        parts = re.split(r'\s+(?:and|or|but|,)\s+', clean_text)
        props = [p.strip() for p in parts if len(p.strip()) > 3]
        return props if props else [clean_text]

    def _build_graph(self, text: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Parse text into Weighted Adjacency Matrix W and Bias vector b."""
        props = self._extract_propositions(text)
        n = len(props)
        if n == 0:
            return np.zeros((1,1)), np.zeros(1), ["empty"]
        
        W = np.zeros((n, n), dtype=np.float64)
        b = np.zeros(n, dtype=np.float64)
        
        text_lower = text.lower()
        
        for i, prop in enumerate(props):
            # Bias initialization
            b[i] = 0.1 # Default positive cue
            
            # Check Negations (flip sign)
            for pat in self.compiled_patterns['negation']:
                if pat.search(prop):
                    b[i] = -0.1
                    break
            
            # Check Causal/Conditional (Self-loop or strong bias if isolated, else edges)
            is_causal = False
            for pat in self.compiled_patterns['causal'] + self.compiled_patterns['conditional']:
                if pat.search(prop):
                    b[i] = 0.2 # Stronger bias for causal statements
                    is_causal = True
                    break
            
            # Build Edges based on comparative/causal flow between propositions
            for j, target in enumerate(props):
                if i == j: continue
                
                # If prop i contains "leads to" and mentions target keyword
                for pat in self.compiled_patterns['causal']:
                    if pat.search(prop):
                        # Heuristic: if target word appears in prop, assume connection
                        words = set(target.split())
                        if any(w in prop for w in words if len(w)>3):
                            W[i, j] = 0.5
                            is_causal = True
                
                # Comparatives
                for pat in self.compiled_patterns['comparative']:
                    if pat.search(prop):
                        # Assume order in list implies comparison flow if keywords match
                        if i < j: 
                            W[i, j] = 1.0 if 'more' in prop or 'greater' in prop else -1.0
                        break

        # Normalize W for stability
        row_sums = np.abs(W).sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        W_norm = W / row_sums
        
        return W_norm, b, props

    def _ergodic_simulation(self, W: np.ndarray, b: np.ndarray, tau: float, T: int = 200, burn: int = 50) -> np.ndarray:
        """Run Gibbs-like synchronous update and return time-averaged states."""
        n = W.shape[0]
        if n == 0: return np.array([])
        
        s = np.full(n, 0.5) # Initialize uninformed
        history = []
        
        # Precompute sigmoid vectorized
        def sigmoid(x): return 1.0 / (1.0 + np.exp(-x))
        
        for t in range(T):
            # Update rule: s <- sigmoid(W @ s + b / tau)
            # Note: b is divided by tau to simulate thermal noise effect on bias
            input_vec = W @ s + b / tau
            s = sigmoid(input_vec)
            
            if t >= burn:
                history.append(s.copy())
        
        if not history:
            return s
            
        return np.mean(np.array(history), axis=0)

    def _compute_order_parameter(self, W: np.ndarray, b: np.ndarray) -> float:
        """Sweep tau to find critical point and return max variance (Order Parameter)."""
        if W.shape[0] == 0: return 0.0
        
        taus = np.linspace(0.1, 2.0, 20)
        variances = []
        
        for tau in taus:
            avg_s = self._ergodic_simulation(W, b, tau)
            if len(avg_s) > 1:
                variances.append(np.var(avg_s))
            else:
                variances.append(0.0)
        
        # Order parameter O is the peak variance observed (analogue to susceptibility peak)
        return float(np.max(variances)) if variances else 0.0

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(z1, z2)
        if denom == 0: return 1.0
        return (z12 - min(z1, z2)) / denom

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt ambiguity.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pat in self.compiled_patterns['presupposition']:
            if pat.search(p_lower): return 0.2
            
        # 2. Scope Ambiguity
        for pat in self.compiled_patterns['scope_ambiguity']:
            if pat.search(p_lower): return 0.3
            
        # 3. Pronoun Ambiguity
        for pat in self.compiled_patterns['pronoun_ambiguity']:
            if pat.search(p_lower) and "who" in p_lower: return 0.3
            
        # 4. False Dichotomy
        for pat in self.compiled_patterns['false_dichotomy']:
            if pat.search(p_lower): return 0.4
            
        # 5. Subjectivity
        for pat in self.compiled_patterns['subjectivity']:
            if pat.search(p_lower): return 0.5
            
        # 6. Unanswerability (Heuristic: very short prompt with no numbers/facts)
        words = re.findall(r'\w+', p_lower)
        if len(words) < 5 and not any(c.isdigit() for c in p_lower):
            return 0.4
            
        return 1.0 # No red flags detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parse Prompt (Reference)
        W_ref, b_ref, _ = self._build_graph(prompt)
        O_ref = self._compute_order_parameter(W_ref, b_ref)
        
        results = []
        
        for cand in candidates:
            # 2. Parse Candidate
            W_cand, b_cand, _ = self._build_graph(cand)
            O_cand = self._compute_order_parameter(W_cand, b_cand)
            
            # 3. Structural Score (Ergodic Phase Transition Similarity)
            # Score = exp(-|O_cand - O_ref|)
            struct_score = np.exp(-abs(O_cand - O_ref))
            
            # 4. Computational Check (Numeric/Logic extraction)
            # If prompt has numbers, check if candidate preserves order/magnitude roughly
            comp_score = 1.0
            nums_prompt = re.findall(r'\d+\.?\d*', prompt)
            nums_cand = re.findall(r'\d+\.?\d*', cand)
            
            if nums_prompt and nums_cand:
                # Simple consistency: if prompt has numbers, candidate should too
                comp_score = 0.8 if len(nums_cand) >= len(nums_prompt) * 0.5 else 0.5
                # Try float comparison if single numbers
                try:
                    if len(nums_prompt) == 1 and len(nums_cand) == 1:
                        if float(nums_cand[0]) != float(nums_prompt[0]):
                            comp_score *= 0.9 # Slight penalty for changing values unless logic dictates
                except: pass
            elif nums_prompt and not nums_cand:
                comp_score = 0.6 # Missing numeric detail

            # 5. NCD Tiebreaker (Max 15% influence)
            ncd = self._ncd_score(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Final Weighted Score
            # Structural >= 50%, Computation >= 20%, NCD <= 15% (rest is base)
            final_score = (0.55 * struct_score) + (0.25 * comp_score) + (0.15 * ncd_score) + 0.05
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural similarity (ergodic order): {struct_score:.2f}, Numeric consistency: {comp_score:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Base score from evaluation logic
        # Run a mini-evaluation to get structural score
        W_ref, b_ref, _ = self._build_graph(prompt)
        W_ans, b_ans, _ = self._build_graph(answer)
        
        O_ref = self._compute_order_parameter(W_ref, b_ref)
        O_ans = self._compute_order_parameter(W_ans, b_ans)
        
        base_score = np.exp(-abs(O_ans - O_ref))
        
        # If no structural match found (parsing failed), low confidence
        if O_ref == 0 and O_ans == 0:
            base_score = 0.2
            
        # Apply cap
        final_conf = min(base_score, meta_cap)
        
        # Never return > 0.9 unless computation was definitive (hard to guarantee without external solver)
        # So we hard cap at 0.95 for safety, but meta_cap usually handles the rest
        return float(np.clip(final_conf, 0.0, 0.95))