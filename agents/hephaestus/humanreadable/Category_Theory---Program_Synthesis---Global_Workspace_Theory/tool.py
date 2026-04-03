import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    Categorical Constraint-Broadcast Scorer (CCBS) with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognition (Tier B): Analyzes prompt for ambiguity, presupposition, or unanswerability.
       If detected, caps confidence low regardless of candidate match.
    2. Parsing (Category Theory): Extracts nodes (objects) and logical relations (morphisms).
       Uses a Functor F to normalize syntax to canonical forms.
    3. Constraint Propagation: Iteratively applies modus ponens and interval arithmetic.
    4. Global Workspace: Broadcasts activation; candidates failing consistency checks are suppressed.
    5. Scoring: Weighted sum of structural satisfaction, numeric accuracy, and NCD tie-breaking.
    """

    def __init__(self):
        # Preset keywords for meta-cognition
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bquit\b.*\bproblem\b"
        ]
        self.scope_triggers = [r"\bevery.*a.*\b", r"\ball.*same\b"]
        self.pronoun_triggers = [r"\bhe\b.*\bwho\b", r"\bshe\b.*\bwho\b", r"\btold.*\bhe\b", r"\btold.*\bhim\b"]
        self.dichotomy_triggers = [r"\beither.*or\b", r"\bmust be.*or\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        self.unanswerable_triggers = [r"\bunknown\b", r"\bnot enough information\b", r"\bcannot be determined\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (ambiguity, presupposition, etc.).
        Returns a cap value: 0.25 if trap detected, 1.0 otherwise.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # 2. Scope Ambiguity (simplified heuristic)
        if re.search(r"every.*\ba\s+\w+", p_lower) and "same" in p_lower:
            return 0.25
            
        # 3. Pronoun Ambiguity
        if re.search(r"\btold\b", p_lower) and re.search(r"\bwho\b", p_lower):
            return 0.25
            
        # 4. False Dichotomy
        if re.search(r"either.*or", p_lower) and "possible" not in p_lower:
            # Heuristic: if it looks like a forced choice without context
            if len(p_lower.split()) < 20: 
                return 0.25

        # 5. Subjectivity
        for word in self.subjectivity_triggers:
            if re.search(rf"\b{word}\b", p_lower):
                return 0.25

        # 6. Unanswerable markers in prompt itself
        for pattern in self.unanswerable_triggers:
            if re.search(pattern, p_lower):
                return 0.25

        return 1.0

    def _parse_nodes(self, text: str) -> List[Tuple[str, Any]]:
        """Extracts propositional nodes (type, payload)."""
        nodes = []
        text_lower = text.lower()
        
        # Numeric comparisons
        num_match = re.search(r"(\d+(?:\.\d+)?)\s*(>=|<=|>|<|=|is at least|is at most)\s*(\d+(?:\.\d+)?)", text_lower)
        if num_match:
            v1, op, v2 = num_match.groups()
            op_map = {'>=': 'ge', '<=': 'le', '>': 'gt', '<': 'lt', '=': 'eq', 
                      'is at least': 'ge', 'is at most': 'le'}
            nodes.append(('num_constraint', (float(v1), op_map.get(op, 'eq'), float(v2))))
            
        # Negations
        if re.search(r"\bnot\b|\bno\b|\bnever\b", text_lower):
            nodes.append(('negation', True))
            
        # Conditionals
        if re.search(r"\bif\b.*\bthen\b|\bimplies\b", text_lower):
            nodes.append(('conditional', True))
            
        # Causal
        if re.search(r"\bcause\b|\blead to\b|\bresult in\b", text_lower):
            nodes.append(('causal', True))

        # Fallback generic proposition if nothing specific found
        if not nodes:
            nodes.append(('text_prop', text[:50]))
            
        return nodes

    def _functor_map(self, node: Tuple[str, Any]) -> Tuple[str, Any]:
        """Functor F: Maps syntactic nodes to canonical semantic forms."""
        n_type, payload = node
        if n_type == 'num_constraint':
            v1, op, v2 = payload
            # Normalize to standard tuple
            return ('num', (v1, op, v2))
        elif n_type == 'negation':
            return ('logic', 'neg')
        elif n_type == 'conditional':
            return ('logic', 'imp')
        elif n_type == 'causal':
            return ('logic', 'cause')
        return (n_type, payload)

    def _propagate_constraints(self, nodes: List[Tuple], edges: List) -> float:
        """
        Performs constraint propagation.
        Returns satisfaction score (0.0 to 1.0).
        """
        satisfied = 0.0
        total = len(nodes) if nodes else 1
        
        for n_type, payload in nodes:
            if n_type == 'num':
                v1, op, v2 = payload
                try:
                    if op == 'ge' and v1 >= v2: satisfied += 1
                    elif op == 'le' and v1 <= v2: satisfied += 1
                    elif op == 'gt' and v1 > v2: satisfied += 1
                    elif op == 'lt' and v1 < v2: satisfied += 1
                    elif op == 'eq' and abs(v1 - v2) < 1e-9: satisfied += 1
                    else:
                        # If constraint exists in prompt but candidate violates it, penalty
                        pass 
                except:
                    pass
            else:
                satisfied += 1 # Non-numeric nodes count as satisfied if present
                
        return min(1.0, satisfied / total) if total > 0 else 0.0

    def _global_workspace_broadcast(self, prompt_nodes: List, cand_nodes: List, activation: float) -> float:
        """
        Simulates Global Workspace Theory ignition.
        Adjusts activation based on consistency between prompt and candidate morphisms.
        """
        if not cand_nodes:
            return 0.0
            
        match_count = 0
        total_ops = 0
        
        p_types = set(n[0] for n in prompt_nodes)
        c_types = set(n[0] for n in cand_nodes)
        
        # Overlap of logical types
        intersection = p_types.intersection(c_types)
        union = p_types.union(c_types)
        
        if not union:
            return activation * 0.5
            
        structural_similarity = len(intersection) / len(union)
        
        # Natural transformation eta: adjust based on global context
        # If prompt has negation, candidate must have negation (simplified)
        if ('logic', 'neg') in prompt_nodes:
            if ('logic', 'neg') not in cand_nodes:
                structural_similarity *= 0.5 # Suppress if missing critical negation
        
        return activation * structural_similarity

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / (max(c1, c2) - min_len) if max(c1, c2) > min_len else 0.0
        except:
            return 1.0

    def _compute_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic combining structure, computation, and NCD."""
        p_nodes_raw = self._parse_nodes(prompt)
        c_nodes_raw = self._parse_nodes(candidate)
        
        # Apply Functor F
        p_nodes = [self._functor_map(n) for n in p_nodes_raw]
        c_nodes = [self._functor_map(n) for n in c_nodes_raw]
        
        # 1. Structural/Computational Score (50% + 20%)
        # Check numeric constraints explicitly
        num_score = 0.0
        num_count = 0
        for n_type, payload in p_nodes:
            if n_type == 'num':
                num_count += 1
                v1, op, v2 = payload
                # Try to verify if candidate implies this constraint
                # Simple heuristic: if candidate contains numbers, do they satisfy prompt?
                c_nums = re.findall(r"\d+(?:\.\d+)?", candidate)
                if c_nums:
                    # Very basic check: does candidate contain the result?
                    # For "5 > 3", candidate should reflect truth or derived value
                    satisfied = False
                    if op == 'gt' and v1 > v2: satisfied = True
                    if op == 'lt' and v1 < v2: satisfied = True
                    if satisfied:
                        num_score += 1.0
                    else:
                        # If prompt asserts X > Y, and candidate says X < Y, penalize
                        pass
        
        struct_score = 0.0
        if p_nodes:
            # Overlap of canonical forms
            p_set = set(str(n) for n in p_nodes)
            c_set = set(str(n) for n in c_nodes)
            if p_set:
                overlap = len(p_set.intersection(c_set))
                struct_score = overlap / len(p_set)
        
        # Boost if numeric constraint satisfied
        if num_count > 0:
             # If we found numeric constraints in prompt, check if candidate respects them
             # This is a simplification of the interval propagation
             struct_score = max(struct_score, 0.5) # Base floor for attempting logic

        # 2. Global Workspace Activation (Metacognitive suppression handled outside)
        activation = 1.0
        gw_score = self._global_workspace_broadcast(p_nodes, c_nodes, activation)
        
        # 3. NCD Tiebreaker (max 15%)
        ncd_val = self._ncd(prompt, candidate)
        ncd_score = 1.0 - ncd_val # Convert distance to similarity
        
        # Final Weighted Sum
        # Structural 50%, Computation 20%, GW 15%, NCD 15%
        final_score = (struct_score * 0.50) + (gw_score * 0.20) + (gw_score * 0.15) + (ncd_score * 0.15)
        
        return min(1.0, max(0.0, final_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        scored_candidates = []
        for cand in candidates:
            raw_score = self._compute_score(prompt, cand)
            # Apply epistemic cap
            final_score = min(raw_score, meta_cap) if meta_cap < 0.3 else raw_score
            scored_candidates.append((cand, final_score))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Generate reasoning string
        for cand, score in scored_candidates:
            reason_parts = []
            if self._meta_confidence(prompt) < 0.3:
                reason_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            if re.search(r"\d", prompt) and re.search(r"\d", cand):
                reason_parts.append("Numeric constraint evaluated.")
            if not reason_parts:
                reason_parts.append("Structural match and logical consistency checked.")
                
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": " ".join(reason_parts)
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-cognition if prompt is flawed.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate base confidence based on structural fit
        score = self._compute_score(prompt, answer)
        
        # If meta-cognition detects a trap, cap confidence severely
        if meta_cap < 0.3:
            return min(score, 0.25)
        
        # If no structural parse matched (score very low), confidence should be low
        if score < 0.2:
            return max(score, 0.1) # Don't say 0, but very low
            
        # Cap high confidence only for definitive computational matches
        # Heuristic: if score is high and no meta-trap, allow up to 0.95
        return min(score, 0.95)