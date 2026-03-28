import re
import numpy as np
from typing import List, Dict, Any

class ReasoningTool:
    """
    Implements a reasoning scorer based on Gene Regulatory Networks (GRN), 
    Symbiotic Mutualism, and Falsificationism.
    
    Mechanism:
    1. Proposition Extraction: Parses text for atomic claims with polarity and type.
    2. GRN Dynamics: Builds an influence matrix (W) based on logical consistency 
       between propositions. Iterates activation vector a = tanh(W*a) to find 
       stable attractor states representing logical coherence.
    3. Symbiosis: Measures cosine similarity between candidate and reference attractors.
    4. Falsification: Penalizes candidates that directly contradict negated constraints in the prompt.
    5. Scoring: Weighted sum of Coherence (GRN), Mutualism (Symbiosis), and Truthfulness (Falsification).
    """
    
    # Structural patterns for parsing
    NEGATION_CUES = ['not', 'no', 'never', 'without', 'none', 'neither']
    COMPARATIVES = ['more than', 'less than', 'greater', 'fewer', 'higher', 'lower']
    CONDITIONALS = ['if', 'provided that', 'unless', 'then']
    CAUSALS = ['because', 'leads to', 'results in', 'causes', 'due to']
    ORDERING = ['before', 'after', 'precedes', 'follows', 'first', 'last']
    
    def __init__(self):
        self.alpha = 0.4  # GRN weight
        self.beta = 0.4   # Symbiosis weight
        self.gamma = 0.2  # Falsification weight

    def _extract_props(self, text: str) -> List[Dict[str, Any]]:
        """Extract atomic propositions with polarity and type tags."""
        props = []
        text_lower = text.lower()
        sentences = re.split(r'[.\n]', text)
        
        for sent in sentences:
            if not sent.strip():
                continue
            
            # Determine polarity
            polarity = 1
            has_negation = any(re.search(r'\b' + cue + r'\b', text_lower) for cue in self.NEGATION_CUES)
            if has_negation:
                polarity = -1
            
            # Determine type
            p_type = 'declarative'
            if any(c in text_lower for c in self.COMPARATIVES): p_type = 'comparative'
            elif any(c in text_lower for c in self.CONDITIONALS): p_type = 'conditional'
            elif any(c in text_lower for c in self.CAUSALS): p_type = 'causal'
            elif any(c in text_lower for c in self.ORDERING): p_type = 'ordering'
            
            # Simple numeric extraction for potential validation
            nums = re.findall(r'-?\d+\.?\d*', sent)
            
            props.append({
                'text': sent.strip(),
                'polarity': polarity,
                'type': p_type,
                'has_negation': has_negation,
                'nums': nums
            })
            
        return props

    def _build_grn_matrix(self, props: List[Dict]) -> np.ndarray:
        """Construct influence matrix W based on proposition relationships."""
        n = len(props)
        if n == 0:
            return np.array([[0.0]])
            
        W = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                pi, pj = props[i], props[j]
                w_ij = 0.0
                
                # Logic: Same polarity + causal/conditional -> Activation
                if pi['type'] in ['causal', 'conditional'] and pj['type'] in ['causal', 'conditional']:
                    if pi['polarity'] == pj['polarity']:
                        w_ij = 0.2
                    else:
                        w_ij = -0.2
                
                # Negation flip
                if pi['has_negation'] or pj['has_negation']:
                    w_ij = -w_ij
                    
                W[i, j] = w_ij
                
        return W

    def _compute_attractor(self, W: np.ndarray, initial_polarity: np.ndarray) -> np.ndarray:
        """Iterate GRN dynamics to find stable attractor state."""
        if W.shape[0] == 0:
            return np.array([])
            
        a = initial_polarity.astype(float)
        if np.all(a == 0):
            a = np.ones_like(a) * 0.1
            
        for _ in range(20):
            a_new = np.tanh(np.dot(W, a))
            if np.linalg.norm(a_new - a) < 1e-3:
                break
            a = a_new
        return a

    def _check_falsification(self, prompt_props: List[Dict], cand_props: List[Dict]) -> float:
        """Calculate falsification penalty based on contradictory predicates."""
        if not cand_props:
            return 1.0
            
        falsifications = 0
        # Extract negated constraints from prompt
        prompt_negations = [p for p in prompt_props if p['has_negation']]
        
        for pn in prompt_negations:
            # Simple keyword overlap check for contradiction
            pn_words = set(re.findall(r'\w+', pn['text'].lower()))
            for pc in cand_props:
                pc_words = set(re.findall(r'\w+', pc['text'].lower()))
                # If candidate shares significant vocabulary with a negated prompt statement
                # but has opposite polarity, it's a falsification risk.
                overlap = len(pn_words & pc_words)
                if overlap > 2 and pc['polarity'] != pn['polarity']:
                    falsifications += 1
                    
        total = len(cand_props)
        if total == 0: return 1.0
        return 1.0 - (falsifications / total)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_props = self._extract_props(prompt)
        prompt_W = self._build_grn_matrix(prompt_props)
        prompt_polarity = np.array([p['polarity'] for p in prompt_props]) if prompt_props else np.array([])
        
        # Compute reference attractor if prompt has structure
        r_star = np.array([])
        if len(prompt_props) > 0 and prompt_W.size > 0:
            r_star = self._compute_attractor(prompt_W, prompt_polarity)

        for cand in candidates:
            cand_props = self._extract_props(cand)
            cand_W = self._build_grn_matrix(cand_props)
            cand_polarity = np.array([p['polarity'] for p in cand_props]) if cand_props else np.array([])
            
            # 1. GRN Score (Internal Coherence)
            s_grn = 0.0
            if len(cand_props) > 0 and cand_W.size > 0:
                a_star = self._compute_attractor(cand_W, cand_polarity)
                if a_star.size > 0:
                    s_grn = float(np.mean(np.abs(a_star)))
            
            # 2. Symbiosis Score (Alignment with Prompt Logic)
            s_sym = 0.0
            if r_star.size > 0 and a_star.size > 0:
                # Align dimensions by min length or resize (simple truncation/padding for demo)
                min_len = min(len(r_star), len(a_star))
                if min_len > 0:
                    r_sub = r_star[:min_len]
                    a_sub = a_star[:min_len]
                    norm_r = np.linalg.norm(r_sub)
                    norm_a = np.linalg.norm(a_sub)
                    if norm_r > 0 and norm_a > 0:
                        s_sym = float(np.dot(r_sub, a_sub) / (norm_r * norm_a))
            
            # 3. Falsification Penalty
            s_fal = self._check_falsification(prompt_props, cand_props)
            
            # Final Score
            score = (self.alpha * s_grn) + (self.beta * s_sym) + (self.gamma * s_fal)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"GRN:{s_grn:.2f} Sym:{s_sym:.2f} Fal:{s_fal:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score roughly to 0-1 range assuming max theoretical score ~1.0
        conf = max(0.0, min(1.0, res[0]['score']))
        return conf