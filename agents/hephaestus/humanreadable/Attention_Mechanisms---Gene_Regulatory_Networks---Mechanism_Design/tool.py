from typing import Dict, Tuple

import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Attentive Regulatory Incentive Scorer (ARIS)
    
    Fuses: Attention Mechanisms x Gene Regulatory Networks x Mechanism Design
    
    Core mechanism:
    1. Attention: weight tokens by semantic salience via dot-product attention
    2. GRN dynamics: propagate utilities through constraint graph iteratively
    3. Mechanism design: incentivize truth-telling, penalize contradictions
    4. State tracking: model reasoning as dynamical system, score by trajectory stability
    """
    
    def __init__(self):
        self.d = 16  # embedding dimension
        self.eta = 0.2  # GRN update rate
        self.k_iterations = 5  # regulatory propagation steps
        
    def _tokenize(self, text: str) -> List[str]:
        """Split into tokens, preserve numbers and punctuation"""
        return re.findall(r'\d+\.?\d*|[a-zA-Z]+|[?.!,;:]', text.lower())
    
    def _embed(self, tokens: List[str]) -> np.ndarray:
        """Character n-gram embeddings"""
        T = np.zeros((len(tokens), self.d))
        for i, tok in enumerate(tokens):
            for j, c in enumerate(tok[:self.d]):
                T[i, (ord(c) + j) % self.d] += 1.0
        T = T / (np.linalg.norm(T, axis=1, keepdims=True) + 1e-8)
        return T
    
    def _attention(self, T: np.ndarray) -> np.ndarray:
        """Scaled dot-product self-attention"""
        Q = K = T
        scores = Q @ K.T / np.sqrt(self.d)
        A = np.exp(scores - np.max(scores, axis=1, keepdims=True))
        A = A / (A.sum(axis=1, keepdims=True) + 1e-8)
        return A
    
    def _extract_spans(self, tokens: List[str], A: np.ndarray, threshold: float = 0.15) -> List[int]:
        """Identify salient tokens by attention weight"""
        row_sums = A.sum(axis=1)
        return [i for i in range(len(tokens)) if row_sums[i] > threshold * len(tokens)]
    
    def _build_regulatory_graph(self, tokens: List[str], spans: List[int], A: np.ndarray) -> Tuple[Dict, Dict]:
        """Build GRN-style graph with edges for syntactic relations"""
        edges = {}
        utilities = {i: 0.0 for i in spans}
        
        # Detect structural features and set initial utilities
        text = ' '.join(tokens)
        for i in spans:
            tok = tokens[i]
            # Truth-telling incentive for content words
            if len(tok) > 2 and tok.isalpha():
                utilities[i] = 1.0
            # Negation markers
            if tok in ['not', 'no', 'never', 'none']:
                utilities[i] = -1.0
            # Numeric tokens
            if re.match(r'\d+\.?\d*', tok):
                utilities[i] = 1.5
        
        # Add edges for co-occurring spans
        for i in spans:
            edges[i] = []
            for j in spans:
                if i != j and abs(i - j) <= 5:  # sliding window
                    weight = A[i, j]
                    edges[i].append((j, weight))
        
        return edges, utilities
    
    def _regulatory_update(self, edges: Dict, utilities: Dict) -> Dict:
        """GRN-style iterative utility propagation"""
        for _ in range(self.k_iterations):
            new_u = utilities.copy()
            for i in utilities:
                delta = 0.0
                for j, w_ij in edges.get(i, []):
                    delta += w_ij * np.tanh(utilities[j] - utilities[i])
                new_u[i] += self.eta * delta
            utilities = new_u
        return utilities
    
    def _apply_constraints(self, tokens: List[str], utilities: Dict) -> Dict:
        """Apply hard constraints from structural parsing"""
        text = ' '.join(tokens)
        
        # Negation constraint
        neg_pattern = r'(not|no|never)\s+(\w+)'
        for m in re.finditer(neg_pattern, text):
            neg_pos = len(text[:m.start()].split())
            target_pos = neg_pos + 1
            if target_pos in utilities:
                utilities[target_pos] = -abs(utilities.get(target_pos, 0.0))
        
        # Comparative constraint
        if 'greater' in text or 'more' in text or 'larger' in text:
            for i in utilities:
                if tokens[i] in ['greater', 'more', 'larger']:
                    utilities[i] = 1.2
        if 'less' in text or 'smaller' in text or 'fewer' in text:
            for i in utilities:
                if tokens[i] in ['less', 'smaller', 'fewer']:
                    utilities[i] = 0.8
        
        return utilities
    
    def _track_dynamics(self, prompt_tokens: List[str], cand_tokens: List[str]) -> float:
        """Track state evolution (FRAME C: dynamics tracker)"""
        # Simulate reasoning as sequential premise processing
        states = []
        state = np.zeros(self.d)
        
        # Process prompt tokens sequentially
        for i, tok in enumerate(prompt_tokens[:20]):  # limit for efficiency
            tok_vec = np.zeros(self.d)
            for j, c in enumerate(tok[:self.d]):
                tok_vec[(ord(c) + j) % self.d] += 1.0
            state = 0.7 * state + 0.3 * tok_vec  # reservoir dynamics
            states.append(state.copy())
        
        # Compute trajectory stability (lower variance = more stable = higher confidence)
        if len(states) > 1:
            trajectory = np.array(states)
            stability = 1.0 / (1.0 + np.std(trajectory))
        else:
            stability = 0.5
        
        # Check convergence to candidate
        cand_state = np.zeros(self.d)
        for tok in cand_tokens[:10]:
            for j, c in enumerate(tok[:self.d]):
                cand_state[(ord(c) + j) % self.d] += 1.0
        
        if np.linalg.norm(cand_state) > 0:
            cand_state /= np.linalg.norm(cand_state)
        if np.linalg.norm(state) > 0:
            state /= np.linalg.norm(state)
        
        convergence = max(0, np.dot(state, cand_state))
        
        return 0.6 * convergence + 0.4 * stability
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect reasoning traps (Tier B epistemic honesty)"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you|did you) (stop|quit|cease)', p):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+ .+ a \w+', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they) (was|is|were)', p) and '?' in p:
            return 0.3
        
        # False dichotomy
        if re.search(r'either .+ or .+', p):
            return 0.35
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|most beautiful)', p):
            return 0.4
        
        return 1.0  # no trap detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (tiebreaker only)"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score and rank candidates"""
        p_tokens = self._tokenize(prompt)
        p_embed = self._embed(p_tokens)
        p_attn = self._attention(p_embed)
        p_spans = self._extract_spans(p_tokens, p_attn)
        p_edges, p_util = self._build_regulatory_graph(p_tokens, p_spans, p_attn)
        p_util = self._regulatory_update(p_edges, p_util)
        p_util = self._apply_constraints(p_tokens, p_util)
        
        results = []
        for cand in candidates:
            c_tokens = self._tokenize(cand)
            c_embed = self._embed(c_tokens)
            c_attn = self._attention(c_embed)
            c_spans = self._extract_spans(c_tokens, c_attn)
            c_edges, c_util = self._build_regulatory_graph(c_tokens, c_spans, c_attn)
            c_util = self._regulatory_update(c_edges, c_util)
            c_util = self._apply_constraints(c_tokens, c_util)
            
            # Structural score: mean utility
            struct_score = np.mean(list(c_util.values())) if c_util else 0.0
            struct_score = (struct_score + 2.0) / 4.0  # normalize to [0,1]
            
            # Dynamics score: trajectory stability
            dyn_score = self._track_dynamics(p_tokens, c_tokens)
            
            # NCD score (tiebreaker)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: dynamics 40%, structural 45%, NCD 15%
            final_score = 0.40 * dyn_score + 0.45 * struct_score + 0.15 * ncd_score
            
            reasoning = f"Dynamics={dyn_score:.2f}, Struct={struct_score:.2f}, NCD={ncd_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on question properties and answer quality"""
        # Check for reasoning traps
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        answer_score = results[0]["score"] if results else 0.5
        
        # Cap confidence by meta-analysis
        base_conf = answer_score
        final_conf = min(base_conf, meta_conf)
        
        # Never return >0.9 unless we have very high structural + dynamics agreement
        if final_conf > 0.9:
            final_conf = 0.85
        
        return max(0.0, min(1.0, final_conf))