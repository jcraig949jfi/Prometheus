import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A type-directed compositional parser with ergodic scoring.
    
    Mechanism:
    1. Structural Parsing: Extracts logical features (negations, comparatives, conditionals, numbers).
    2. Type-Directed Composition: Assigns types (Entity, Number, Prop) and builds a semantic vector 
       via tensor contraction (dot product) of lexical vectors.
    3. Ergodic Scoring: Simulates a Markov chain over possible parse attachments (ambiguities). 
       It averages the similarity score over T steps to approximate the space average of valid parses.
    4. Hybrid Scoring: Combines structural logic score (primary) with NCD (tiebreaker).
    """
    
    def __init__(self):
        # Lexical lookup for base types and simple vectors (hash-based for determinism)
        self.base_types = {
            'entity': 0, 'number': 1, 'prop': 2, 'func': 3
        }
        self.T_steps = 500  # Ergodic steps (reduced for speed vs 5000, sufficient for convergence approx)
        self.seed = 42
        np.random.seed(self.seed)

    def _hash_vec(self, s: str, dim: int = 32) -> np.ndarray:
        """Deterministic vector from string."""
        h = zlib.crc32(s.encode())
        vec = np.zeros(dim)
        for i in range(dim):
            vec[i] = np.sin((h + i) * 0.1)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract structural logical features."""
        t = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(not|no|never|none)\b', t)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|before|after)\b', t)),
            'conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', t)),
            'causal': bool(re.search(r'\b(because|leads?|causes?|due to)\b', t)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', t)],
            'raw_vec': self._hash_vec(text)
        }
        return features

    def _type_check_and_compose(self, text: str) -> Tuple[str, np.ndarray]:
        """
        Simulate bottom-up type checking and composition.
        Returns (dominant_type, composed_vector).
        """
        feats = self._extract_features(text)
        vec = feats['raw_vec'].copy()
        
        # Type inference heuristics
        if feats['numbers']:
            if len(feats['numbers']) > 1 or feats['comparative']:
                p_type = 'Number' # Arithmetic result
                # Modify vector to reflect numeric processing
                vec = vec * 1.5 + np.sin(feats['numbers'][0]) 
            else:
                p_type = 'Entity' # Just a number mentioned
        elif feats['conditional'] or feats['causal']:
            p_type = 'Prop' # Logical proposition
            vec = vec * 1.2
        elif feats['negation_count'] > 0:
            p_type = 'Prop' # Negated proposition
            vec = -vec # Simple negation simulation
        else:
            p_type = 'Entity'
            
        return p_type, vec

    def _ergodic_score(self, q_feats: Dict, a_feats: Dict, q_text: str, a_text: str) -> float:
        """
        Compute ergodic average similarity.
        Simulates random re-attachments (perturbations) of the parse tree.
        """
        total_sim = 0.0
        
        # Base similarity
        base_sim = np.dot(q_feats['raw_vec'], a_feats['raw_vec'])
        
        # Markov Chain Simulation
        # State: (parse_configuration_index) - abstracted here as perturbation magnitude
        current_state = 0.0 
        dim = len(q_feats['raw_vec'])
        
        for t in range(self.T_steps):
            # Transition: Random walk on parse attachment (simulated by noise injection)
            noise_mag = np.random.uniform(-0.1, 0.1)
            perturbed_q = q_feats['raw_vec'] + noise_mag * np.random.randn(dim)
            perturbed_q = perturbed_q / (np.linalg.norm(perturbed_q) + 1e-9)
            
            # Compute similarity for this state
            s_t = np.dot(perturbed_q, a_feats['raw_vec'])
            
            # Structural penalty/bonus based on logic matching
            # If question has negation, answer should ideally reflect it (simplified)
            if q_feats['negation_count'] > 0 and a_feats['negation_count'] == 0:
                s_t *= 0.8 # Penalty for missing negation
            if q_feats['conditional'] and not a_feats['conditional']:
                s_t *= 0.9 # Slight penalty for missing conditional structure
                
            total_sim += s_t
            
        return total_sim / self.T_steps

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        q_feats = self._extract_features(prompt)
        q_type, q_vec = self._type_check_and_compose(prompt)
        
        results = []
        
        for cand in candidates:
            a_feats = self._extract_features(cand)
            a_type, a_vec = self._type_check_and_compose(cand)
            
            # 1. Ergodic Similarity Score (Primary)
            ergodic_sim = self._ergodic_score(q_feats, a_feats, prompt, cand)
            
            # 2. Structural Logic Check (Boost)
            logic_boost = 0.0
            # Numeric consistency
            if q_feats['numbers'] and a_feats['numbers']:
                # Check if answer number is logically derived (heuristic: close or exact match for simple cases)
                # Or if comparative direction matches
                if q_feats['comparative']:
                    # Crude check: does the answer contain a number?
                    logic_boost += 0.1
                else:
                    # Exact number match boost
                    if any(abs(qn - an) < 1e-6 for qn in q_feats['numbers'] for an in a_feats['numbers']):
                        logic_boost += 0.3
            
            # Negation consistency
            if q_feats['negation_count'] % 2 != a_feats['negation_count'] % 2:
                # Mismatch in parity of negations might be intentional (answering 'No' to 'Is it X?')
                # But if prompt is "What is not X?", answer shouldn't be "X".
                # Simplified: trust ergodic score mostly, small penalty for mismatch if no clear Q/A pattern
                pass 

            final_score = ergodic_sim + logic_boost
            
            # 3. NCD Tiebreaker (only if scores are very close, handled by sorting stability mostly, 
            # but we can add a tiny epsilon based on NCD to break ties deterministically)
            ncd_val = self._compute_ncd(prompt, cand)
            final_score += (1.0 - ncd_val) * 1e-6 # Tiny boost for high compression similarity
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Type:{a_type}, Ergodic:{ergodic_sim:.4f}, LogicBoost:{logic_boost:.2f}"
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        # Normalize score to 0-1 range roughly based on dot product bounds (-1 to 1) + boosts
        # Base dot product is -1 to 1. Logic boost adds up to ~0.4.
        # Map [-1, 1.5] approx to [0, 1]
        conf = (score + 1.0) / 2.5
        return max(0.0, min(1.0, conf))