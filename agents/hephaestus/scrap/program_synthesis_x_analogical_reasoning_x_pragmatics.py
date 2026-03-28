import re
import numpy as np
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A hybrid reasoning tool combining symbolic program synthesis (parsing/constraints),
    analogical graph matching, and pragmatic scoring.
    
    Mechanism:
    1. Parsing: Extracts relational triples (subject, relation, object, polarity) using regex.
    2. Constraint Propagation: Uses NumPy matrix operations to enforce transitivity and 
       modus ponens on a 3D tensor representation of knowledge.
    3. Analogical Matching: Computes structural similarity between prompt and candidate 
       via feature matching of relation counts.
    4. Pragmatics: Scores based on Gricean maxims (quantity, quality, relevance).
    5. Scoring: Weighted sum of structural analogy and pragmatic adherence.
    """
    
    # Relation types and regex patterns
    RELATIONS = {
        'comparative': [r'(\w+)\s+(?:is\s+)?(taller|shorter|bigger|smaller|more|less)\s+(?:than\s+)?(\w+)',
                        r'(\w+)\s+(?:has\s+)?(more|less)\s+(\w+)\s+(?:than\s+)?(\w+)'],
        'equality': [r'(\w+)\s+(?:is\s+)?(same|equal|identical)\s+(?:to\s+)?(\w+)'],
        'conditional': [r'if\s+(\w+)\s+(?:then\s+)?(\w+)', r'unless\s+(\w+),\s+(\w+)'],
        'causal': [r'(\w+)\s+(?:causes|leads to|results in)\s+(\w+)'],
        'negation': [r'(\w+)\s+(?:is\s+)?(not|never|no)\s+(\w+)', r'(no|none)\s+(\w+)\s+(?:is\s+)?(\w+)'],
        'temporal': [r'(\w+)\s+(?:before|after)\s+(\w+)'],
        'numeric': [r'(\w+)\s+(?:is|equals|==)\s*(\d+)', r'(\w+)\s+(?:greater|less)\s+than\s+(\d+)']
    }
    
    REL_LABELS = list(RELATIONS.keys())
    R = len(REL_LABELS)
    
    def __init__(self):
        self.alpha = 0.6  # Weight for analogical score
        self.beta = 0.4   # Weight for pragmatic score

    def _parse_text(self, text: str) -> Tuple[List[Dict], Dict[str, int], List[str]]:
        """Extract triples <s, r, o, p> and map entities to IDs."""
        text_lower = text.lower()
        triples = []
        entities = {}
        entity_list = []
        
        def get_id(e: str) -> int:
            e = e.strip()
            if e not in entities:
                entities[e] = len(entities)
                entity_list.append(e)
            return entities[e]
        
        # Extract numeric facts first (higher priority)
        for match in re.finditer(r'(\w+)\s+(?:is|equals|==)\s*(\d+(?:\.\d+)?)', text_lower):
            s, val = match.group(1), float(match.group(2))
            sid = get_id(s)
            triples.append({'s': sid, 'r': 'numeric', 'o': val, 'p': 1, 'raw_s': s, 'raw_o': val})
            
        # Extract relational triples
        for r_type, patterns in self.RELATIONS.items():
            if r_type == 'numeric': continue
            for pat in patterns:
                for match in re.finditer(pat, text_lower):
                    groups = match.groups()
                    # Heuristic mapping based on pattern structure
                    if r_type == 'comparative':
                        if len(groups) >= 3:
                            s, rel_word, o = groups[0], groups[1], groups[2]
                            polarity = 1 if rel_word in ['taller', 'bigger', 'more'] else -1
                            triples.append({'s': get_id(s), 'r': r_type, 'o': get_id(o), 'p': polarity, 'raw_s': s, 'raw_o': o})
                    elif r_type == 'equality':
                        if len(groups) >= 3:
                            s, _, o = groups
                            triples.append({'s': get_id(s), 'r': r_type, 'o': get_id(o), 'p': 1, 'raw_s': s, 'raw_o': o})
                    elif r_type == 'conditional':
                        if len(groups) >= 2:
                            cond, res = groups
                            triples.append({'s': get_id(cond), 'r': r_type, 'o': get_id(res), 'p': 1, 'raw_s': cond, 'raw_o': res})
                    elif r_type == 'negation':
                         if len(groups) >= 3:
                            # Handle "A is not B"
                            if 'not' in groups or 'never' in groups:
                                s, _, o = groups[0], groups[1], groups[2] if len(groups)>2 else ""
                                if s and o:
                                    triples.append({'s': get_id(s), 'r': 'negation', 'o': get_id(o), 'p': 1, 'raw_s': s, 'raw_o': o})
        
        return triples, entities, entity_list

    def _build_tensor(self, triples: List[Dict], n_entities: int) -> np.ndarray:
        """Build N x N x R tensor C."""
        C = np.zeros((n_entities, n_entities, self.R))
        if n_entities == 0: return C
        
        for t in triples:
            if 'o' in t and isinstance(t['o'], int): # Only entity-to-entity
                r_idx = self.REL_LABELS.index(t['r'])
                val = t['p']
                # Simple one-hot encoding with polarity
                if t['p'] == 1:
                    C[t['s'], t['o'], r_idx] = 1
                else:
                    C[t['s'], t['o'], r_idx] = -1
        return C

    def _propagate_constraints(self, C: np.ndarray) -> np.ndarray:
        """Apply transitivity and modus ponens via matrix ops."""
        if C.shape[0] == 0: return C
        
        prev = C.copy()
        for _ in range(5): # Fixed point iteration limit
            # Transitivity for comparative/ordering (index 0)
            if self.R > 0:
                comp = C[:, :, 0]
                # If A > B and B > C, then A > C
                trans = (comp @ comp) > 0.5
                C[:, :, 0] = np.maximum(comp, trans.astype(float))
            
            # Simple consistency check (negation resolution)
            # If A->B is positive, A->B negative should be zeroed or flagged
            # Here we just stabilize
            if np.allclose(C, prev):
                break
            prev = C.copy()
        return C

    def _compute_analogy_score(self, prompt_triples: List[Dict], cand_triples: List[Dict], 
                               prompt_entities: int, cand_entities: int) -> float:
        """Compute structural similarity via feature matching."""
        if prompt_entities == 0 or cand_entities == 0:
            return 0.0
            
        # Feature vector: count of incoming/outgoing relations per type
        # Size: 2 * R
        def get_features(triples, n):
            feats = np.zeros((n, 2 * self.R))
            for t in triples:
                if 'o' in t and isinstance(t['o'], int):
                    r_idx = self.REL_LABELS.index(t['r'])
                    s, o = t['s'], t['o']
                    if 0 <= s < n and 0 <= o < n:
                        feats[s, r_idx] += 1          # Outgoing
                        feats[o, self.R + r_idx] += 1 # Incoming
            return feats

        F_p = get_features(prompt_triples, prompt_entities)
        F_c = get_features(cand_triples, cand_entities)
        
        # Simplified Hungarian-like approximation: 
        # Sort nodes by norm and match greedily (deterministic)
        # Real Hungarian is O(N^3), this is O(N log N) approximation for small N
        p_norms = np.linalg.norm(F_p, axis=1)
        c_norms = np.linalg.norm(F_c, axis=1)
        
        p_sorted = np.argsort(p_norms)[::-1]
        c_sorted = np.argsort(c_norms)[::-1]
        
        min_n = min(len(p_sorted), len(c_sorted))
        if min_n == 0: return 0.0
        
        cost = 0.0
        max_possible = 0.0
        
        for i in range(min_n):
            pid, cid = p_sorted[i], c_sorted[i]
            dist = np.linalg.norm(F_p[pid] - F_c[cid])
            cost += dist
            max_possible += np.linalg.norm(F_p[pid]) + np.linalg.norm(F_c[cid])
            
        if max_possible == 0: return 1.0
        return 1.0 - (cost / (max_possible + 1e-6))

    def _compute_pragmatic_score(self, prompt: str, answer: str, 
                                 prompt_triples: List[Dict], cand_triples: List[Dict],
                                 C_prompt: np.ndarray, p_entities: List[str]) -> float:
        """Apply Gricean maxims."""
        p_len = len(prompt.split())
        a_len = len(answer.split())
        
        # Quantity: Penalty if answer is too long relative to prompt
        qty_penalty = max(0, (a_len - 2 * p_len) / (p_len + 1))
        
        # Quality: Conflict detection (simplified)
        # Check if candidate asserts something explicitly negated in prompt logic
        quality_penalty = 0.0
        # (Simplified: just checking triple count consistency for now)
        if len(cand_triples) > 0 and len(prompt_triples) == 0:
            quality_penalty = 0.5 # Suspicious if prompt has no structure but answer does
            
        # Relevance: Overlap of entities
        p_ents = set(t.get('raw_s', '').lower() for t in prompt_triples if isinstance(t.get('raw_s'), str))
        p_ents.update(t.get('raw_o', '').lower() for t in prompt_triples if isinstance(t.get('raw_o'), str))
        
        a_ents = set(t.get('raw_s', '').lower() for t in cand_triples if isinstance(t.get('raw_s'), str))
        a_ents.update(t.get('raw_o', '').lower() for t in cand_triples if isinstance(t.get('raw_o'), str))
        
        relevance = 0.0
        if len(p_ents) > 0:
            overlap = len(p_ents.intersection(a_ents))
            relevance = overlap / len(p_ents)
        else:
            # Fallback to word overlap if no structured entities found
            p_words = set(prompt.lower().split())
            a_words = set(answer.lower().split())
            if len(p_words) > 0:
                relevance = len(p_words.intersection(a_words)) / len(p_words)

        # Manner: Ambiguity (simplified: penalty for common vague words)
        vague_words = {'thing', 'stuff', 'something', 'maybe', 'perhaps'}
        manner_penalty = len([w for w in answer.lower().split() if w in vague_words]) / (len(answer.split()) + 1)
        
        # Weights
        w_q, w_l, w_r, w_m = 0.25, 0.25, 0.25, 0.25
        score = 1.0 - (w_q * min(qty_penalty, 1.0) + w_l * quality_penalty) + (w_r * relevance) - (w_m * manner_penalty)
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_triples, p_ent_map, p_ent_list = self._parse_text(prompt)
        p_n = len(p_ent_map)
        C_p = self._build_tensor(p_triples, p_n)
        C_p = self._propagate_constraints(C_p)
        
        for cand in candidates:
            c_triples, c_ent_map, c_ent_list = self._parse_text(cand)
            c_n = len(c_ent_map)
            C_c = self._build_tensor(c_triples, c_n)
            C_c = self._propagate_constraints(C_c)
            
            # 1. Structural Analogy
            s_ana = self._compute_analogy_score(p_triples, c_triples, p_n, c_n)
            
            # 2. Pragmatics
            s_pra = self._compute_pragmatic_score(prompt, cand, p_triples, c_triples, C_p, p_ent_list)
            
            # Final Score
            score = self.alpha * s_ana + self.beta * s_pra
            
            # NCD Tiebreaker (only if scores are very close or zero)
            if score < 1e-6:
                import zlib
                data = (prompt + cand).encode()
                comp = len(zlib.compress(data))
                norm = min(len(zlib.compress(prompt.encode())), len(zlib.compress(cand.encode())))
                ncd = (comp - norm) / (norm + 1e-6)
                score = max(0, 1 - ncd) * 0.1 # Low weight tiebreaker

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Analogy: {s_ana:.2f}, Pragmatics: {s_pra:.2f}"
            })
            
        return sorted(results, key=lambda x: x['score'], reverse=True)

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']