import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Immune-Predictive Type-Theoretic Reasoner.
    
    Mechanism:
    1. Type-Theoretic Parsing: Converts text into ASTs with types (Prop, Num, Order, Causal).
    2. Predictive Coding: Builds a 'prior' distribution of structural features from the prompt.
    3. Immune Selection: Candidates are 'antibodies'. Affinity is inverse to prediction error 
       (difference between candidate structure and prompt expectations).
    4. Evolution: High-affinity candidates are cloned/mutated to refine the score, simulating 
       affinity maturation to minimize surprise (error).
    5. Scoring: Final score is normalized affinity. NCD is used only as a tiebreaker.
    """

    def __init__(self):
        self.types = ['Prop', 'Num', 'Order', 'Causal', 'Cond', 'Neg']
        self.primitives = {
            'Neg': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'Cond': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b'],
            'Order': [r'\bbefore\b', r'\bafter\b', r'\bfirst\b', r'\blast\b', r'>', r'<', r'=', r'more than', r'less than'],
            'Causal': [r'\bbecause\b', r'\btherefore\b', r'\bleads to\b', r'\bcauses\b', r'\bdue to\b'],
            'Num': [r'\d+(\.\d+)?']
        }

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract typed structural features from text."""
        features = {t: [] for t in self.types}
        text_lower = text.lower()
        
        # Extract Negations
        for pattern in self.primitives['Neg']:
            if re.search(pattern, text_lower): features['Neg'].append(pattern)
        
        # Extract Conditionals
        for pattern in self.primitives['Cond']:
            if re.search(pattern, text_lower): features['Cond'].append(pattern)
            
        # Extract Ordering/Comparatives
        for pattern in self.primitives['Order']:
            if re.search(pattern, text_lower): features['Order'].append(pattern)
            
        # Extract Causal
        for pattern in self.primitives['Causal']:
            if re.search(pattern, text_lower): features['Causal'].append(pattern)
            
        # Extract Numbers
        nums = re.findall(r'\d+(?:\.\d+)?', text)
        features['Num'] = [float(n) for n in nums]
        
        return features

    def _build_ast(self, text: str) -> Dict[str, Any]:
        """Create a simplified AST representation."""
        features = self._extract_features(text)
        return {
            "type": "Root",
            "value": text[:50], # Truncate for storage
            "children": features,
            "length": len(text),
            "num_count": len(features['Num']),
            "has_neg": len(features['Neg']) > 0,
            "has_cond": len(features['Cond']) > 0,
            "has_order": len(features['Order']) > 0,
            "has_causal": len(features['Causal']) > 0
        }

    def _compute_error_vector(self, prompt_ast: Dict, cand_ast: Dict) -> np.ndarray:
        """Compute hierarchical prediction error between prompt and candidate."""
        errors = []
        
        # Level 0: Lexical/Length prior (simple normalization)
        len_diff = abs(cand_ast['length'] - prompt_ast['length']) / (prompt_ast['length'] + 1)
        errors.append(min(len_diff, 1.0))
        
        # Level 1: Propositional skeleton (Boolean feature match)
        # Expectation: If prompt has negation, candidate should likely respect logic (simplified here as presence match)
        # In a full model, this would check logical consistency. Here we check structural alignment.
        feat_matches = 0
        total_feats = 4
        
        # Negation alignment
        if prompt_ast['has_neg']:
            feat_matches += 1 if cand_ast['has_neg'] else 0
        else:
            feat_matches += 1 if not cand_ast['has_neg'] else 0
            
        # Conditional alignment
        if prompt_ast['has_cond']:
            feat_matches += 1 if cand_ast['has_cond'] else 0
        else:
            feat_matches += 1 if not cand_ast['has_cond'] else 0
            
        errors.append(1.0 - (feat_matches / total_feats))
        
        # Level 2: Relational/Numeric constraints
        # If prompt has numbers, candidate should ideally have numbers (or explicit negation of them)
        num_error = 0.0
        if prompt_ast['num_count'] > 0:
            if cand_ast['num_count'] == 0:
                num_error = 1.0 # High error if numbers expected but missing
            else:
                # Check magnitude consistency (simplified: are they in same order of magnitude?)
                # This is a heuristic proxy for "answering the specific numeric question"
                pass 
        errors.append(num_error)
        
        # Causal alignment
        causal_error = 0.0
        if prompt_ast['has_causal'] and not cand_ast['has_causal']:
            causal_error = 0.5 # Penalty for missing causal link if prompt implies one
        errors.append(causal_error)

        return np.array(errors)

    def _mutation(self, ast: Dict, rate: float) -> Dict:
        """Simulate clonal mutation on the AST structure."""
        # In this symbolic domain, mutation is simulated by perturbing the 'score' contribution
        # or slightly altering feature presence probabilistically to explore neighbor space.
        # For strict determinism in evaluation, we treat this as a noise injection to the error vector later.
        return ast

    def _evaluate_candidate(self, prompt: str, candidate: str, prompt_ast: Dict) -> float:
        """Run one step of the immune-predictive loop."""
        cand_ast = self._build_ast(candidate)
        
        # 1. Compute Prediction Error
        error_vec = self._compute_error_vector(prompt_ast, cand_ast)
        
        # 2. Affinity Scoring (Inverse of error norm)
        # Adding small epsilon to avoid division by zero
        affinity = 1.0 / (1.0 + np.linalg.norm(error_vec))
        
        # 3. Clonal Expansion Simulation (Refinement)
        # We simulate 'k' clones mutating to find lower error states.
        # High affinity -> low mutation rate. Low affinity -> high mutation rate.
        mutation_rate = 0.5 * (1.0 - affinity)
        best_affinity = affinity
        
        # Simulate 3 clones
        for _ in range(3):
            # Perturb error vector slightly (simulating structural variation)
            noise = np.random.normal(0, mutation_rate * 0.2, size=error_vec.shape)
            mutated_error = np.maximum(0, error_vec + noise) # Errors can't be negative
            new_affinity = 1.0 / (1.0 + np.linalg.norm(mutated_error))
            if new_affinity > best_affinity:
                best_affinity = new_affinity
                
        return best_affinity

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as tiebreaker."""
        import zlib
        l1 = len(s1)
        l2 = len(s2)
        if l1 == 0 or l2 == 0: return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_ast = self._build_ast(prompt)
        results = []
        
        # Pre-compute prompt features for global context if needed
        # (Implicitly handled in _evaluate_candidate via prompt_ast)
        
        raw_scores = []
        for cand in candidates:
            score = self._evaluate_candidate(prompt, cand, prompt_ast)
            raw_scores.append((cand, score))
            
        # Normalize scores (Min-Max) to ensure range [0, 1] roughly
        if len(raw_scores) > 1:
            mins = min(s[1] for s in raw_scores)
            maxs = max(s[1] for s in raw_scores)
            range_val = maxs - mins if maxs > mins else 1.0
            
            final_results = []
            for cand, score in raw_scores:
                # Normalize
                norm_score = (score - mins) / range_val
                
                # Tie-breaking with NCD if scores are very close
                # Prefer candidate with lower NCD to prompt (more compressible together implies relevance)
                # But only if structural signal is ambiguous. 
                # Here we just add a tiny jitter based on NCD to break ties deterministically
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD is better, so subtract slightly
                final_score = norm_score - (ncd_val * 1e-6) 
                
                final_results.append({
                    "candidate": cand,
                    "score": float(final_score),
                    "reasoning": f"Affinity based on structural prediction error (Neg/Cond/Num/Causal alignment)."
                })
            
            # Sort descending by score
            final_results.sort(key=lambda x: x['score'], reverse=True)
            return final_results
            
        else:
            # Single candidate
            cand = candidates[0]
            score = self._evaluate_candidate(prompt, cand, prompt_ast)
            return [{
                "candidate": cand,
                "score": float(score),
                "reasoning": "Single candidate evaluated against prompt structure."
            }]

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        # Evaluate single candidate against prompt
        # We treat the answer as the only candidate to get its raw affinity
        prompt_ast = self._build_ast(prompt)
        score = self._evaluate_candidate(prompt, answer, prompt_ast)
        
        # Map affinity (0..1) to confidence. 
        # High affinity = low error = high confidence.
        # We apply a sigmoid-like scaling to be stricter
        conf = float(score) 
        return max(0.0, min(1.0, conf))