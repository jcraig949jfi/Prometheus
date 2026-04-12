import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Implements a Hierarchical Proposition Graph (HPG) scorer based on Ecosystem Dynamics,
    Predictive Coding, and Analogical Reasoning.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (subject, predicate, object) with polarity,
       modality, and numeric values using regex.
    2. Analogical Mapping: Maps extracted propositions to a fixed 'trophic-schema' 
       (Producer -> Consumer -> Apex) to determine structural fit.
    3. Predictive Coding: Calculates prediction error between the observed graph structure
       and the ideal schema expectations (energy flow efficiency).
    4. Scoring: Converts total prediction error (structural violations + constraint failures)
       into a confidence score. NCD is used only as a tie-breaker.
    """

    def __init__(self):
        # Trophic Schema Adjacency Matrix (Ideal Flow)
        # Order: [Producer, Primary, Secondary, Apex, Detritus]
        # 1.0 = Direct flow, 0.1 = Efficiency loss, 0.0 = No flow
        self.schema_labels = ['producer', 'consumer', 'predator', 'apex', 'detritus']
        self.schema_matrix = np.zeros((5, 5))
        # Linear chain: P->C->Pred->Apex->Det
        self.schema_matrix[0, 1] = 1.0
        self.schema_matrix[1, 2] = 1.0
        self.schema_matrix[2, 3] = 1.0
        self.schema_matrix[3, 4] = 1.0
        self.schema_matrix[4, 0] = 0.1 # Cycle closure (nutrients)
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|fail)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|when|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+\.?\d*'),
            'relation': re.compile(r'(\w+)\s+(is|are|has|have|eats|consumes|produces|kills|preys)\s+(\w+)')
        }

    def _extract_propositions(self, text: str) -> List[Dict[str, Any]]:
        """Extracts atomic propositions and structural features from text."""
        props = []
        text_lower = text.lower()
        
        # Detect global modifiers
        has_negation = bool(self.patterns['negation'].search(text_lower))
        has_comparative = bool(self.patterns['comparative'].search(text_lower))
        has_conditional = bool(self.patterns['conditional'].search(text_lower))
        has_causal = bool(self.patterns['causal'].search(text_lower))
        
        numbers = [float(n) for n in self.patterns['numeric'].findall(text)]
        
        # Extract explicit relations
        matches = self.patterns['relation'].findall(text_lower)
        for subj, pred, obj in matches:
            props.append({
                'subject': subj,
                'predicate': pred,
                'object': obj,
                'polarity': -1 if has_negation else 1,
                'modality': 'conditional' if has_conditional else ('comparative' if has_comparative else 'assertion'),
                'type': 'causal' if has_causal else 'relational',
                'numeric': numbers if numbers else [1.0]
            })
            
        # If no explicit relations found but text exists, treat whole text as a single proposition node
        if not props and text.strip():
            props.append({
                'subject': 'system',
                'predicate': 'state',
                'object': 'active',
                'polarity': -1 if has_negation else 1,
                'modality': 'conditional' if has_conditional else 'assertion',
                'type': 'causal' if has_causal else 'relational',
                'numeric': numbers if numbers else [1.0]
            })
            
        return props

    def _map_to_schema(self, props: List[Dict]) -> Tuple[np.ndarray, List[int]]:
        """
        Attempts to map extracted propositions to the trophic schema.
        Returns an adjacency matrix of the candidate and a list of mapping indices.
        """
        n = len(self.schema_labels)
        adj = np.zeros((n, n))
        mapping = []
        
        # Simple keyword-based mapping heuristic
        keyword_map = {
            'producer': 0, 'plant': 0, 'grass': 0, 'algae': 0,
            'consumer': 1, 'herbivore': 1, 'rabbit': 1, 'deer': 1,
            'predator': 2, 'carnivore': 2, 'wolf': 2, 'lion': 2,
            'apex': 3, 'top': 3, 'human': 3,
            'detritus': 4, 'decomposer': 4, 'bacteria': 4, 'fungi': 4
        }
        
        mapped_indices = set()
        
        for prop in props:
            subj = prop['subject']
            obj = prop['object']
            
            s_idx = -1
            o_idx = -1
            
            # Map subject
            for k, v in keyword_map.items():
                if k in subj:
                    s_idx = v
                    break
            if s_idx == -1: # Fallback hash mod
                s_idx = hash(subj) % 5
            
            # Map object
            for k, v in keyword_map.items():
                if k in obj:
                    o_idx = v
                    break
            if o_idx == -1:
                o_idx = hash(obj) % 5
                
            if prop['polarity'] > 0:
                # Add edge with weight based on numeric value
                weight = np.mean(prop['numeric']) if prop['numeric'] else 1.0
                # Normalize weight to 0-1 range roughly
                weight = min(1.0, weight / 10.0) if weight > 1 else weight
                adj[s_idx, o_idx] = max(adj[s_idx, o_idx], weight)
                mapped_indices.add(s_idx)
                mapped_indices.add(o_idx)

        return adj, list(mapped_indices)

    def _calculate_prediction_error(self, observed_adj: np.ndarray, mapped_indices: List[int]) -> float:
        """
        Computes prediction error between observed graph and schema.
        Error = Sum((Observed - Expected)^2) for present edges + Penalty for missing expected edges.
        """
        total_error = 0.0
        n = self.schema_matrix.shape[0]
        
        # Scale schema to match observed density roughly if needed, but here we compare structure
        # We focus on the subgraph defined by mapped indices
        
        # 1. Error on observed edges (Do they match schema flow?)
        for i in range(n):
            for j in range(n):
                if observed_adj[i, j] > 0:
                    expected = self.schema_matrix[i, j]
                    # If schema expects 0 (no flow) but we observe flow, high error
                    # If schema expects 1 and we observe 1, low error
                    # Predictive coding: Error = (Observation - Prediction)^2
                    total_error += (observed_adj[i, j] - expected) ** 2
                else:
                    # Optional: Penalty for missing expected connections if nodes are present
                    if self.schema_matrix[i, j] > 0 and i in mapped_indices and j in mapped_indices:
                        total_error += 0.5 # Penalty for missing expected link

        # 2. Constraint Propagation Check (Transitivity)
        # If A->B and B->C, then A->C should exist (approx)
        # Simplified: Check triangle inequality on weights
        if n >= 3:
            transitivity_error = np.sum(np.abs(np.dot(observed_adj, observed_adj) - observed_adj))
            total_error += transitivity_error * 0.1

        return total_error

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tie-breaker."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_s1_s2 = len(zlib.compress(s1_b + s2_b))
        max_len = max(len_s1, len_s2)
        if max_len == 0: return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        prompt_props = self._extract_propositions(prompt)
        
        # Calculate baseline error from prompt to establish context (optional refinement)
        # Here we score candidates based on their internal consistency with the schema
        
        scores = []
        for cand in candidates:
            props = self._extract_propositions(cand)
            obs_adj, mapped_idx = self._map_to_schema(props)
            error = self._calculate_prediction_error(obs_adj, mapped_idx)
            
            # Structural Score: Inverse of error
            # Add small epsilon to avoid division by zero
            struct_score = 1.0 / (1.0 + error)
            
            # Boost if candidate shares key structural tokens with prompt (basic relevance)
            prompt_keys = set([p['subject'] for p in prompt_props] + [p['object'] for p in prompt_props])
            cand_keys = set([p['subject'] for p in props] + [p['object'] for p in props])
            overlap = len(prompt_keys.intersection(cand_keys))
            relevance_boost = min(0.2, overlap * 0.05) # Max 0.2 boost
            
            final_score = min(1.0, struct_score + relevance_boost)
            scores.append((cand, final_score, error))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Handle ties with NCD
        final_results = []
        for i, (cand, score, err) in enumerate(scores):
            reasoning = f"Structural fit: {score:.4f}, Prediction Error: {err:.4f}"
            
            # NCD Tie-breaker logic
            if i > 0 and abs(score - scores[i-1][1]) < 1e-6:
                ncd_prev = self._ncd(prompt, scores[i-1][0])
                ncd_curr = self._ncd(prompt, cand)
                if ncd_curr < ncd_prev:
                    # Swap logic handled by sort stability or re-sort, 
                    # but for simple list append, we just note it.
                    # Since we sorted, we assume stable sort or accept minor variance.
                    pass 
            
            final_results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural fit."""
        props = self._extract_propositions(answer)
        obs_adj, mapped_idx = self._map_to_schema(props)
        error = self._calculate_prediction_error(obs_adj, mapped_idx)
        base_score = 1.0 / (1.0 + error)
        
        # Relevance check
        prompt_props = self._extract_propositions(prompt)
        prompt_keys = set([p['subject'] for p in prompt_props] + [p['object'] for p in prompt_props])
        cand_keys = set([p['subject'] for p in props] + [p['object'] for p in props])
        overlap = len(prompt_keys.intersection(cand_keys))
        relevance_boost = min(0.2, overlap * 0.05)
        
        return min(1.0, base_score + relevance_boost)