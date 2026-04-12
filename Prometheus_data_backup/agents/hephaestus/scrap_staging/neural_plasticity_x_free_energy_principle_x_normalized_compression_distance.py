import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Neural Plasticity, Free Energy Principle, and Structural Parsing.
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions with features (negation, causal, numeric).
    2. Neural Plasticity (Hebbian): Builds a co-occurrence graph from the prompt. Weights update 
       based on candidate activation (synaptic strengthening).
    3. Free Energy Principle: Computes prediction error as the delta between expected description 
       length (graph entropy) and actual compressed length.
    4. Scoring: Prioritizes structural constraint satisfaction (logic/numeric checks). Uses 
       Free Energy error as a secondary signal. NCD is restricted to tie-breaking only.
    """
    
    # Regex patterns for structural features
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|higher|lower)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(because|therefore|leads to|causes|due to)\b', re.IGNORECASE),
        'numeric': re.compile(r'\d+(?:\.\d+)?'),
        'ordering': re.compile(r'\b(first|last|before|after|next|previous)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.tau = 0.001  # Pruning threshold
        self.eta = 0.01   # Learning rate
        self.lambda_fep = 0.5 # FEP weight

    def _extract_propositions(self, text: str) -> List[Dict]:
        """Parse text into atomic propositions with structural labels."""
        props = []
        text_lower = text.lower()
        
        # Check for presence of structural features
        features = {}
        for key, pattern in self.PATTERNS.items():
            if key != 'numeric':
                features[key] = bool(pattern.search(text_lower))
        
        # Extract numeric values for direct comparison logic
        numbers = [float(n) for n in self.PATTERNS['numeric'].findall(text)]
        
        # Create a node for the whole text context and specific features
        # Node 0: Global context
        props.append({'id': 0, 'text': 'global', 'features': features, 'numbers': numbers})
        
        # Create nodes for specific structural hits to allow graph connectivity
        node_id = 1
        for key, exists in features.items():
            if exists:
                props.append({'id': node_id, 'text': key, 'features': {key: True}, 'numbers': []})
                node_id += 1
                
        return props

    def _build_graph(self, prompt: str) -> Tuple[np.ndarray, List[str]]:
        """Initialize adjacency matrix based on co-occurrence (PMI approximation)."""
        props = self._extract_propctions(prompt)
        n = len(props)
        if n == 0:
            return np.array([]), []
            
        # Initialize weights with structural priors (stronger edges for logic markers)
        W = np.zeros((n, n))
        labels = [p['text'] for p in props]
        
        # Hebbian-like initialization: co-occurrence in the same sentence/window
        # Since we parsed the whole prompt, we assume high connectivity for structural elements
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Base connectivity
                    W[i, j] = 0.1 
                    # Boost if both are logical operators
                    if 'causal' in props[i]['features'] or 'conditional' in props[i]['features']:
                        if 'causal' in props[j]['features'] or 'conditional' in props[j]['features']:
                            W[i, j] = 0.5
        
        return W, labels

    def _hebbian_update(self, W: np.ndarray, prompt_props: List[Dict], answer_props: List[Dict]) -> np.ndarray:
        """Update edge weights based on candidate answer activation."""
        if W.size == 0:
            return W
            
        n = W.shape[0]
        # Activation vector: 1 if proposition type exists in answer, else 0
        # We map answer features back to the prompt's proposition indices by feature type
        a = np.zeros(n)
        
        # Map answer features to indices
        answer_features = set()
        for p in answer_props:
            for k, v in p['features'].items():
                if v: answer_features.add(k)
                
        for i, prop in enumerate(prompt_props):
            # Check if global or if specific feature matches
            if prop['text'] == 'global':
                a[i] = 1.0
            else:
                if prop['text'] in answer_features:
                    a[i] = 1.0
        
        # Hebbian update: W_ij += eta * a_i * a_j
        outer_product = np.outer(a, a)
        W_new = W + self.eta * outer_product
        
        # Synaptic pruning
        W_new[W_new < self.tau] = 0
        return W_new

    def _compute_fep_error(self, W: np.ndarray, prompt: str, answer: str) -> float:
        """Compute Free Energy-like prediction error."""
        if W.size == 0:
            return 1.0
            
        # Expected Description Length (Entropy of the graph)
        # Normalize weights to probability distribution
        w_sum = np.sum(W)
        if w_sum == 0:
            L_exp = 0.0
        else:
            P = W / w_sum
            # Avoid log(0)
            P_safe = P[P > 0]
            L_exp = -np.sum(P_safe * np.log(P_safe + 1e-9))
        
        # Actual Description Length (Compression)
        text = (prompt + " " + answer).encode('utf-8')
        L_act = len(zlib.compress(text))
        
        # Prediction Error
        # Scale L_act to be comparable to L_exp (rough heuristic)
        epsilon = abs(L_act * 0.01 - L_exp)
        return epsilon

    def _check_structural_logic(self, prompt: str, answer: str) -> float:
        """
        Primary scoring signal: Check if answer respects structural constraints.
        Returns a score boost (0.0 to 1.0).
        """
        score = 0.0
        p_low = prompt.lower()
        a_low = answer.lower()
        
        # 1. Negation Check
        if self.PATTERNS['negation'].search(p_low):
            # If prompt has negation, answer should ideally reflect it or be short (denial)
            # Heuristic: If prompt says "not X", and answer says "X", penalize.
            # This is hard without NLP, so we check for contradiction patterns.
            if re.search(r'\byes\b', a_low) and re.search(r'\bnot\b', p_low):
                # Ambiguous, but let's assume explicit confirmation of negative is good
                pass 
            score += 0.2 # Reward detecting negation context

        # 2. Numeric Consistency
        p_nums = [float(n) for n in self.PATTERNS['numeric'].findall(p_low)]
        a_nums = [float(n) for n in self.PATTERNS['numeric'].findall(a_low)]
        
        if len(p_nums) >= 2 and len(a_nums) >= 1:
            # Simple comparative check
            if "more than" in p_low or "greater than" in p_low:
                if a_nums[0] > p_nums[0]: # Rough heuristic
                    score += 0.3
            elif "less than" in p_low:
                if a_nums[0] < p_nums[0]:
                    score += 0.3
        
        # 3. Conditional/Logical Flow
        if self.PATTERNS['conditional'].search(p_low):
            # Reward answers that contain logical connectors or are concise
            if len(a_low.split()) < 10 or any(k in a_low for k in ['if', 'then', 'because', 'yes', 'no']):
                score += 0.2

        return min(score, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_props = self._extract_propositions(prompt)
        base_graph, _ = self._build_graph(prompt)
        
        results = []
        
        for cand in candidates:
            cand_props = self._extract_propositions(cand)
            
            # 1. Structural Logic Score (Primary Signal)
            logic_score = self._check_structural_logic(prompt, cand)
            
            # 2. Neural Plasticity Update
            if base_graph.size > 0:
                W_updated = self._hebbian_update(base_graph.copy(), prompt_props, cand_props)
            else:
                W_updated = base_graph
            
            # 3. Free Energy Prediction Error
            fep_error = self._compute_fep_error(W_updated, prompt, cand)
            
            # 4. NCD (Tiebreaker)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Final Score Construction
            # Higher is better. 
            # Logic provides the base. FEP error is subtracted (lower error = better).
            # NCD is used minimally as a tiebreaker for similar logic scores.
            base_score = logic_score * 10.0  # Scale up logic importance
            fep_penalty = fep_error * self.lambda_fep
            
            # Invert FEP error: lower error -> higher score
            # Normalize fep roughly: assume error < 5.0 is typical range
            fep_component = max(0, 2.0 - (fep_error * 0.2)) 
            
            total_score = base_score + fep_component - (ncd_val * 0.1)
            
            reasoning = f"Logic:{logic_score:.2f} FEP:{fep_component:.2f} NCD:{ncd_val:.2f}"
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and FEP."""
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        # Normalize score to 0-1 range heuristically
        # Logic score maxes around 1.0 * 10 = 10. FEP adds ~2.
        # So max theoretical ~12. 
        conf = min(1.0, max(0.0, score / 12.0))
        return conf