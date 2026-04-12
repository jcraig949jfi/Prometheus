import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Adaptive Plasticity-Guided Graph Neural Network (AP-GNN) Approximation.
    
    Mechanism:
    1. Graph Construction: Nodes are tokens from the prompt + candidates. 
       Edges represent co-occurrence and semantic similarity (approximated by NCD).
    2. Plasticity (Hebbian/Pruning): Weights update based on activation correlation.
       Stronger co-activation strengthens edges; decay prunes weak ones.
    3. Metacognitive Monitor: Computes entropy of the activation distribution.
       If confidence is low, it simulates 'rewiring' by boosting structural 
       constraints (negations, numerics) before final scoring.
    4. Scoring: Candidates are scored by their final activation strength after 
       plasticity updates and potential metacognitive correction.
    """

    def __init__(self):
        self.tau = 0.1  # Decay rate for plasticity
        self.lr = 0.5   # Learning rate
        self.conf_threshold = 0.7 # Metacognitive trigger

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lower case, split by non-alphanumeric."""
        clean = "".join(c.lower() if c.isalnum() else " " for c in text)
        return [t for t in clean.split() if len(t) > 1]

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        s1b = s1.encode('utf-8')
        s2b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1b))
        c2 = len(zlib.compress(s2b))
        c12 = len(zlib.compress(s1b + s2b))
        min_len = min(c1, c2)
        if min_len == 0: return 1.0
        return (c12 - min_len) / max(c1, c2, 1)

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract numeric and logical constraints (Constraint Propagation)."""
        features = {
            'has_negation': 1.0 if any(w in text.lower() for w in ['not', 'no', 'never', 'false']) else 0.0,
            'has_comparative': 1.0 if any(w in text.lower() for w in ['more', 'less', 'greater', 'smaller', '>', '<']) else 0.0,
            'numeric_val': 0.0
        }
        # Simple numeric extraction
        try:
            words = text.replace(',', '').split()
            for w in words:
                if w.replace('.', '').replace('-', '').isdigit():
                    features['numeric_val'] = float(w)
                    break
        except:
            pass
        return features

    def _build_graph(self, prompt: str, candidates: List[str]) -> Tuple[List[str], np.ndarray, Dict[int, str]]:
        """Build adjacency matrix based on NCD similarity."""
        all_texts = [prompt] + candidates
        tokens = list(set(self._tokenize(" ".join(all_texts))))
        if not tokens: 
            tokens = ["default"]
            
        n = len(tokens)
        W = np.zeros((n, n))
        
        # Initialize weights with inverse NCD (similarity)
        for i, t1 in enumerate(tokens):
            for j, t2 in enumerate(tokens):
                if i == j:
                    W[i, j] = 1.0
                else:
                    sim = 1.0 - self._ncd(t1, t2)
                    W[i, j] = max(0.0, sim)
        
        # Map tokens to indices
        token_map = {t: i for i, t in enumerate(tokens)}
        return tokens, W, token_map

    def _plasticity_update(self, W: np.ndarray, activations: np.ndarray) -> np.ndarray:
        """Apply Hebbian rule with decay: dw = eta * (ai * aj - lambda * wij)."""
        # Outer product for co-activation
        co_activation = np.outer(activations, activations)
        delta = self.lr * (co_activation - self.tau * W)
        new_W = W + delta
        np.clip(new_W, 0.0, 1.0, out=new_W) # Stabilize
        return new_W

    def _metacognitive_rewire(self, W: np.ndarray, tokens: List[str], prompt: str, candidates: List[str]) -> np.ndarray:
        """Simulate rewiring based on structural constraints if confidence is low."""
        p_feats = self._extract_structural_features(prompt)
        
        # Identify indices for critical tokens
        neg_idx = -1
        for t in tokens:
            if t in ['not', 'no', 'never']:
                neg_idx = tokens.index(t)
                break
        
        # Rewire strategy: If prompt has negation, suppress candidates with high similarity 
        # to negation tokens unless they are logically consistent (simplified here as weight reduction)
        if p_feats['has_negation'] > 0 and neg_idx != -1:
            # Reduce weights connecting negation to positive assertions roughly
            for i, t in enumerate(tokens):
                if any(c in t for c in candidates) and t != 'not':
                    W[neg_idx, i] *= 0.5
                    W[i, neg_idx] *= 0.5
        
        # Numeric consistency check (Constraint Propagation)
        if p_feats['numeric_val'] != 0:
            for i, t in enumerate(tokens):
                try:
                    val = float(t)
                    # Simple heuristic: if candidate number contradicts prompt logic (e.g. < vs >)
                    # Since we don't parse full logic, we boost exact matches or close values
                    if abs(val - p_feats['numeric_val']) < 0.01:
                        W[i, :] *= 1.2 # Boost consistent numeric nodes
                        W[:, i] *= 1.2
                except:
                    pass
        return W

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Graph Construction
        tokens, W, token_map = self._build_graph(prompt, candidates)
        n = len(tokens)
        
        # Initial activations: Prompt tokens get 1.0, others 0
        a = np.zeros(n)
        p_tokens = self._tokenize(prompt)
        for t in p_tokens:
            if t in token_map:
                a[token_map[t]] = 1.0
        
        # Add small noise to break symmetry
        a += np.random.uniform(0, 0.01, n)

        # 2. Plasticity Loop (Reasoning Steps)
        for _ in range(3): # 3 reasoning steps
            # Propagate activation
            a_new = np.dot(W, a)
            a_new = np.clip(a_new, 0, 1)
            
            # Update weights (Plasticity)
            W = self._plasticity_update(W, a)
            
            # Normalize activations
            if np.max(a_new) > 0:
                a = a_new / np.max(a_new)
            else:
                a = a_new

        # 3. Metacognitive Check
        # Calculate entropy of candidate activations to determine confidence
        cand_indices = []
        cand_acts = []
        for c in candidates:
            c_tokens = self._tokenize(c)
            act_sum = 0
            for t in c_tokens:
                if t in token_map:
                    act_sum += a[token_map[t]]
            cand_acts.append(act_sum if act_sum > 0 else 1e-6)
            cand_indices.append(c)
        
        total_act = sum(cand_acts) + 1e-9
        probs = np.array(cand_acts) / total_act
        entropy = -np.sum(probs * np.log2(probs + 1e-9))
        max_entropy = np.log2(len(candidates)) if len(candidates) > 1 else 1
        confidence_score = 1.0 - (entropy / max_entropy if max_entropy > 0 else 0)

        # If confidence low, trigger rewiring (Hypothesis testing)
        if confidence_score < self.conf_threshold:
            W = self._metacognitive_rewire(W, tokens, prompt, candidates)
            # Re-run propagation briefly after rewiring
            a = np.zeros(n)
            for t in p_tokens:
                if t in token_map: a[token_map[t]] = 1.0
            
            for _ in range(2):
                a = np.dot(W, a)
                a = np.clip(a, 0, 1)
                if np.max(a) > 0: a /= np.max(a)
            
            # Recalculate scores
            cand_acts = []
            for c in candidates:
                c_tokens = self._tokenize(c)
                act_sum = 0
                for t in c_tokens:
                    if t in token_map: act_sum += a[token_map[t]]
                cand_acts.append(act_sum)

        # 4. Final Scoring & Ranking
        results = []
        max_score = max(cand_acts) if cand_acts else 1
        for i, c in enumerate(candidates):
            # Normalize score 0-1
            score = cand_acts[i] / max_score if max_score > 0 else 0
            
            # Tie-breaking with NCD if scores are very close (structural tie-breaker)
            if len(results) > 0 and abs(score - results[-1]['score']) < 0.01:
                ncd_prompt = self._ncd(prompt, c)
                # Lower NCD to prompt is better
                if ncd_prompt < 0.5: 
                    score += 0.005 
            
            results.append({
                "candidate": c,
                "score": float(score),
                "reasoning": f"Activation strength after plasticity update and metacognitive check."
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        # Use evaluate to get the score for the specific answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # The score from evaluate is already normalized 0-1 relative to the set
        # Here we treat the single candidate's score as confidence
        return results[0]['score']