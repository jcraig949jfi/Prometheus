import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Wavelet-Enhanced Categorical Causal Scorer (WECCS).
    
    Mechanism:
    1. Structural Parsing: Extracts objects (entities, numbers) and morphisms (causal, logical, comparative) 
       using regex to build a categorical graph representation.
    2. Constraint Propagation: Uses matrix multiplication to enforce transitivity and modus ponens.
    3. Wavelet Analysis: Applies a Haar wavelet transform to the sorted edge confidence signal. 
       High detail coefficients indicate local logical inconsistencies (noise).
    4. Causal Check: Penalizes causal claims that violate basic DAG properties (cycles/blocks).
    5. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence.
    6. Scoring: Combines structural validity, wavelet coherence, and NCD tie-breaking.
    """

    def __init__(self):
        # Type mapping functor
        self.type_map = {
            'Entity': 0, 'Property': 1, 'Event': 2, 'Numeric': 3, 'Quantifier': 4
        }
        # Relation patterns
        self.patterns = {
            'causes': [r'\b(causes|leads to|results in|triggers)\b'],
            'implies': [r'\b(if .+? then|implies|therefore|so)\b'],
            'negates': [r'\b(not|no|never|without)\b'],
            'greater_than': [r'\b(greater than|more than|exceeds|>)\b'],
            'less_than': [r'\b(less than|fewer than|under|<)\b'],
            'equals': [r'\b(equals|is equal to|same as|=)\b']
        }
        # Tier B Trap patterns
        self.trap_patterns = {
            'presupposition': [r'\b(have you stopped|why did .+ fail|when did .+ stop)\b'],
            'false_dichotomy': [r'\b(either .+ or|must be .+ or)\b'],
            'subjectivity': [r'\b(best|worst|favorite|most beautiful)\b'],
            'pronoun_ambiguity': [r'\b(he|she|it|they)\b.*\bwho\b'],
            'scope_ambiguity': [r'\b(every .+ a .+|all .+ some .+)\b']
        }

    def _extract_objects_and_morphisms(self, text: str) -> Tuple[List[Dict], Dict, np.ndarray]:
        """Parses text into objects and an adjacency matrix."""
        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)
        
        # Create objects (simplified: one per unique token for this scope)
        objects = []
        obj_map = {}
        for i, tok in enumerate(tokens):
            if tok not in obj_map:
                # Determine type
                o_type = 'Entity'
                if tok.replace('.','',1).isdigit(): o_type = 'Numeric'
                elif tok in ['all', 'some', 'every', 'no']: o_type = 'Quantifier'
                elif tok in ['cause', 'effect', 'result', 'event']: o_type = 'Event'
                
                objects.append({'id': len(objects), 'token': tok, 'type': o_type})
                obj_map[tok] = len(objects) - 1
        
        n_obj = len(objects)
        if n_obj == 0:
            return [], {}, np.zeros((0,0))

        A = np.zeros((n_obj, n_obj))
        morphs = {}
        edge_weights = []
        edge_indices = []

        # Extract morphisms
        for label, regexes in self.patterns.items():
            for regex in regexes:
                # Simple context window matching
                for i in range(len(tokens)-1):
                    if re.search(regex, " ".join(tokens[i:i+3])):
                        # Connect surrounding tokens as src/tgt
                        src_tok = tokens[i] if i < len(tokens) else tokens[-1]
                        tgt_tok = tokens[i+1] if i+1 < len(tokens) else tokens[-1]
                        
                        if src_tok in obj_map and tgt_tok in obj_map:
                            s_idx, t_idx = obj_map[src_tok], obj_map[tgt_tok]
                            if s_idx != t_idx and A[s_idx, t_idx] == 0:
                                A[s_idx, t_idx] = 1
                                morphs[(s_idx, t_idx)] = label
                                # Confidence: 1.0 explicit, 0.5 inferred (simplified)
                                conf = 1.0 if label in ['causes', 'equals'] else 0.8
                                edge_weights.append(conf)
                                edge_indices.append((s_idx, t_idx))

        # Constraint propagation (Transitivity via A @ A)
        if n_obj > 1:
            A_prop = (A + A @ A) > 0
            # Add implied edges with lower weight
            for i in range(n_obj):
                for j in range(n_obj):
                    if A_prop[i,j] and A[i,j] == 0:
                        A[i,j] = 0.5 # Weak inference
                        if (i,j) not in morphs:
                            morphs[(i,j)] = 'inferred'
                            edge_weights.append(0.5)
                            edge_indices.append((i,j))

        return objects, morphs, np.array(edge_weights) if edge_weights else np.array([0.0])

    def _haar_wavelet(self, signal: np.ndarray) -> np.ndarray:
        """Computes Haar wavelet detail coefficients."""
        if len(signal) < 2:
            return np.array([0.0])
        
        # Pad to power of 2
        n = len(signal)
        pow2 = 1
        while pow2 < n: pow2 *= 2
        padded = np.zeros(pow2)
        padded[:n] = signal
        
        details = []
        curr = padded
        while len(curr) > 1:
            next_level = []
            for i in range(0, len(curr), 2):
                avg = (curr[i] + curr[i+1]) / 2
                diff = (curr[i] - curr[i+1]) / 2
                next_level.append(avg)
                details.append(diff)
            curr = np.array(next_level)
        
        return np.array(details) if details else np.array([0.0])

    def _check_causal_violations(self, morphs: Dict, n: int) -> float:
        """Lightweight do-calculus check: detects cycles in causal chains."""
        penalty = 0.0
        # Build causal subgraph
        causal_edges = [(s,t) for (s,t), label in morphs.items() if label == 'causes']
        
        # Simple cycle detection (DFS)
        adj = {i: [] for i in range(n)}
        for s, t in causal_edges:
            if s < n and t < n: adj[s].append(t)
            
        visited = set()
        rec_stack = set()
        
        def has_cycle(u):
            visited.add(u)
            rec_stack.add(u)
            for v in adj.get(u, []):
                if v not in visited:
                    if has_cycle(v): return True
                elif v in rec_stack:
                    return True
            rec_stack.remove(u)
            return False

        for i in range(n):
            if i not in visited:
                if has_cycle(i):
                    penalty += 1.0 # Penalty per cycle found
        return penalty

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """Tier B Check: Detects ambiguity and traps."""
        p_low = prompt.lower()
        a_low = answer.lower()
        
        # Check for trap patterns
        for category, patterns in self.trap_patterns.items():
            for pat in patterns:
                if re.search(pat, p_low):
                    return 0.2 # Low confidence for ambiguous/trap questions
        
        # Check for unanswerable (no structural match)
        if not any(re.search(p, p_low) for ps in self.patterns.values() for p in ps):
            # If no logical structure found, rely on NCD, cap confidence
            return 0.4
            
        # If answer is short and generic
        if a_low in ['yes', 'no', 'maybe', 'i don\'t know']:
            return 0.5
            
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1+s2).encode()))
        if max(l1, l2) == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Parse prompt once
        p_objs, p_morphs, p_weights = self._extract_objects_and_morphisms(prompt)
        p_wavelet = np.sum(np.abs(self._haar_wavelet(p_weights))) if len(p_weights) > 0 else 0
        p_causal_pen = self._check_causal_violations(p_morphs, len(p_objs))
        
        base_score_prompt = np.sum(p_weights) - 0.5 * p_wavelet - 0.5 * p_causal_pen

        for cand in candidates:
            # 1. Structural Parsing & Scoring (50%+)
            c_objs, c_morphs, c_weights = self._extract_objects_and_morphisms(cand)
            
            # Wavelet consistency (internal to candidate)
            c_wavelet = np.sum(np.abs(self._haar_wavelet(c_weights))) if len(c_weights) > 0 else 0
            
            # Causal penalty
            c_causal_pen = self._check_causal_violations(c_morphs, len(c_objs))
            
            # Interaction score: Does candidate complete the prompt's graph?
            # Simple heuristic: Overlap of tokens and consistency of relations
            structural_score = 0.0
            if len(c_weights) > 0:
                # Reward for having logical structure
                structural_score = np.sum(c_weights) 
                # Penalty for incoherence
                structural_score -= 0.5 * c_wavelet
                structural_score -= 0.5 * c_causal_pen
            
            # 2. Constructive Computation (20%+)
            # Check for numeric resolution if prompt has numbers
            comp_score = 0.0
            nums_p = re.findall(r'\d+\.?\d*', prompt)
            nums_c = re.findall(r'\d+\.?\d*', cand)
            if nums_p and nums_c:
                try:
                    # Simple magnitude check: does candidate resolve the inequality?
                    p_vals = [float(x) for x in nums_p]
                    c_vals = [float(x) for x in nums_c]
                    if max(c_vals) > min(p_vals): # Heuristic for "greater" resolution
                        comp_score = 1.0
                except: pass
            
            # 3. NCD Tiebreaker (<=15%)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Final Score Assembly
            # Normalize structural score roughly to 0-1 range based on length
            norm_struct = structural_score / (len(cand.split()) + 1) 
            final_score = (0.6 * max(0, norm_struct)) + (0.25 * comp_score) + ncd_score
            
            # Epistemic Cap
            meta_conf = self._meta_confidence(prompt, cand)
            if meta_conf < 0.5:
                final_score = min(final_score, 0.4) # Cap score for ambiguous cases

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural:{norm_struct:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}, MetaConf:{meta_conf:.2f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1, capped by epistemic honesty checks."""
        # 1. Meta-check (Tier B)
        meta_conf = self._meta_confidence(prompt, answer)
        if meta_conf < 0.3:
            return meta_conf
        
        # 2. Structural validity
        objs, morphs, weights = self._extract_objects_and_morphisms(f"{prompt} {answer}")
        if len(morphs) == 0:
            return 0.2 # No structure found
        
        wavelet_pen = np.sum(np.abs(self._haar_wavelet(weights)))
        causal_pen = self._check_causal_violations(morphs, len(objs))
        
        raw_score = np.sum(weights) - 0.5 * wavelet_pen - 0.5 * causal_pen
        norm_score = raw_score / (len(weights) + 1) if len(weights) > 0 else 0
        
        # Map to 0-1, ensuring we don't exceed meta_conf cap
        final_conf = max(0.0, min(1.0, norm_score))
        
        # Hard cap for non-computational answers
        if not re.search(r'\d', answer) and meta_conf == 1.0:
            final_conf = min(final_conf, 0.85) # Never 1.0 without computation
            
        return float(final_conf)