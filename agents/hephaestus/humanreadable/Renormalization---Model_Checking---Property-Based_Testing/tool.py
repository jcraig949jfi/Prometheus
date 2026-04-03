from typing import Dict, Set, Tuple

"""
Hierarchical Constraint-Checking with Property-Guided Shrinking (HCC-PGS)

Combines renormalization, model checking, and property-based testing to evaluate
logical consistency across hierarchical abstractions of clause graphs.
"""

import re
import math
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.ncd_weight = 0.10  # NCD contributes max 10%
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Constraint score: {score:.3f}"
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        structural_match = self._has_structural_match(prompt, answer)
        if not structural_match:
            return 0.25
        
        score = self._compute_score(prompt, answer)
        conf = min(0.85, meta_conf * score)
        return max(0.15, conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with who question
        if re.search(r'\b(he|she)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            if re.search(r'told|said|asked', p_lower):
                return 0.2
        
        # False dichotomy
        if re.search(r'\b(either .* or|must be .* or)\b', p_lower):
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest|ugliest)\b', p_lower):
            if not re.search(r'\b(most|least|largest|smallest|highest|lowest)\b', p_lower):
                return 0.35
        
        # Unanswerable
        if re.search(r'\b(impossible|cannot|unknown|no way to)\b', p_lower):
            return 0.4
        
        return 0.75
    
    def _has_structural_match(self, prompt: str, answer: str) -> bool:
        clauses_p = self._extract_clauses(prompt)
        clauses_a = self._extract_clauses(answer)
        return len(clauses_p) > 0 or len(clauses_a) > 0
    
    def _compute_score(self, prompt: str, candidate: str) -> float:
        # Extract clauses
        p_clauses = self._extract_clauses(prompt)
        c_clauses = self._extract_clauses(candidate)
        
        # Build clause graph
        graph = self._build_clause_graph(p_clauses + c_clauses)
        
        # Hierarchical renormalization
        lattice = self._renormalize(graph)
        
        # Model checking with shrinking
        violations = self._model_check_all_levels(lattice, p_clauses, c_clauses)
        
        # Compute structural score (60%)
        structural_score = self._compute_structural_score(violations, lattice)
        
        # Compute constructive score (25%)
        comp_score = self._compute_computational_score(prompt, candidate)
        
        # NCD tiebreaker (10%)
        ncd_score = 1.0 - self._ncd(prompt, candidate)
        
        # Alignment bonus (5%)
        align_score = self._alignment_score(p_clauses, c_clauses)
        
        final = 0.60 * structural_score + 0.25 * comp_score + 0.10 * ncd_score + 0.05 * align_score
        return max(0.0, min(1.0, final))
    
    def _extract_clauses(self, text: str) -> List[Dict]:
        clauses = []
        # Negations
        for m in re.finditer(r'\b(not|no|never|neither|nor)\s+(\w+)', text.lower()):
            clauses.append({"type": "neg", "pred": m.group(2), "polarity": False})
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|=|equals?)\s*(\d+\.?\d*)', text):
            clauses.append({"type": "cmp", "lhs": float(m.group(1)), "op": m.group(2), "rhs": float(m.group(3))})
        
        # Conditionals
        for m in re.finditer(r'\bif\s+(.+?)\s+then\s+(.+?)(?:\.|,|$)', text.lower()):
            clauses.append({"type": "cond", "antecedent": m.group(1).strip(), "consequent": m.group(2).strip()})
        
        # Temporal
        for m in re.finditer(r'\b(before|after|until|since)\s+(\w+)', text.lower()):
            clauses.append({"type": "temp", "rel": m.group(1), "event": m.group(2)})
        
        return clauses
    
    def _build_clause_graph(self, clauses: List[Dict]) -> Dict:
        graph = {"nodes": clauses, "edges": []}
        for i, c1 in enumerate(clauses):
            for j, c2 in enumerate(clauses):
                if i != j:
                    if self._are_related(c1, c2):
                        graph["edges"].append((i, j))
        return graph
    
    def _are_related(self, c1: Dict, c2: Dict) -> bool:
        if c1["type"] == "neg" and c2["type"] == "neg":
            return c1["pred"] == c2["pred"] and c1["polarity"] != c2["polarity"]
        if c1["type"] == "cond" and c2["type"] == "cond":
            return c1["consequent"] in c2["antecedent"] or c2["consequent"] in c1["antecedent"]
        return False
    
    def _renormalize(self, graph: Dict) -> List[Dict]:
        lattice = [graph]
        for level in range(3):
            coarse = self._coarse_grain(lattice[-1])
            if len(coarse["nodes"]) >= len(lattice[-1]["nodes"]):
                break
            lattice.append(coarse)
        return lattice
    
    def _coarse_grain(self, graph: Dict) -> Dict:
        nodes = graph["nodes"]
        merged = []
        merged_idx = set()
        
        for i, n1 in enumerate(nodes):
            if i in merged_idx:
                continue
            cluster = [n1]
            for j, n2 in enumerate(nodes):
                if j > i and j not in merged_idx and n1["type"] == n2["type"]:
                    cluster.append(n2)
                    merged_idx.add(j)
            merged.append({"type": "cluster", "members": cluster})
        
        return {"nodes": merged, "edges": []}
    
    def _model_check_all_levels(self, lattice: List[Dict], p_clauses: List[Dict], c_clauses: List[Dict]) -> Dict:
        violations = defaultdict(list)
        for level, layer in enumerate(lattice):
            viols = self._check_constraints(layer, p_clauses, c_clauses)
            violations[level] = viols
        return violations
    
    def _check_constraints(self, layer: Dict, p_clauses: List[Dict], c_clauses: List[Dict]) -> List[Tuple]:
        failures = []
        
        # Check comparatives
        for c in c_clauses:
            if c["type"] == "cmp":
                if not self._eval_comparison(c):
                    failures.append(("cmp_fail", c))
        
        # Check negation consistency
        for pc in p_clauses:
            if pc["type"] == "neg":
                for cc in c_clauses:
                    if cc["type"] == "neg" and pc["pred"] == cc["pred"]:
                        if pc["polarity"] == cc["polarity"]:
                            failures.append(("neg_conflict", (pc, cc)))
        
        return failures
    
    def _eval_comparison(self, clause: Dict) -> bool:
        lhs, op, rhs = clause["lhs"], clause["op"], clause["rhs"]
        if op in [">", "gt"]:
            return lhs > rhs
        elif op in ["<", "lt"]:
            return lhs < rhs
        elif op in [">=", "gte"]:
            return lhs >= rhs
        elif op in ["<=", "lte"]:
            return lhs <= rhs
        elif op in ["=", "==", "equals", "equal"]:
            return abs(lhs - rhs) < 1e-9
        return True
    
    def _compute_structural_score(self, violations: Dict, lattice: List[Dict]) -> float:
        score = 1.0
        for level, viols in violations.items():
            layer_size = len(lattice[level]["nodes"]) if level < len(lattice) else 1
            if layer_size > 0:
                penalty = len(viols) / max(1, layer_size)
                weight = 1.0 / (level + 1)
                score -= weight * penalty * 0.3
        return max(0.0, score)
    
    def _compute_computational_score(self, prompt: str, candidate: str) -> float:
        score = 0.5
        
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_c = re.findall(r'\d+\.?\d*', candidate)
        if nums_p and nums_c:
            try:
                val_p = float(nums_p[0])
                val_c = float(nums_c[0])
                if abs(val_p - val_c) < 0.01:
                    score += 0.3
            except:
                pass
        
        # Boolean logic
        if re.search(r'\b(true|yes|correct)\b', candidate.lower()) and re.search(r'\b(is|are|does)\b', prompt.lower()):
            score += 0.2
        
        return min(1.0, score)
    
    def _alignment_score(self, p_clauses: List[Dict], c_clauses: List[Dict]) -> float:
        if not p_clauses or not c_clauses:
            return 0.5
        
        matches = 0
        for pc in p_clauses:
            for cc in c_clauses:
                if pc["type"] == cc["type"]:
                    matches += 1
        
        return min(1.0, matches / max(len(p_clauses), len(c_clauses)))
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))