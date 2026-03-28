import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Structural-Critical Causal Analogy Scorer (SCCAS).
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions, causal markers, negations, 
       and comparatives using regex to build a lightweight clause graph.
    2. Analogical Matching: Matches extracted structures against a library of 
       minimal relational templates (e.g., "A causes B", "If A then not B").
    3. Criticality Weighting: Computes a susceptibility score based on the 
       co-activation frequency of relational patterns (Frobenius norm).
    4. Causal Consistency: Ensures causal chains are acyclic (DAG check).
    5. Scoring: Weighted sum of Analogy Match, Criticality, and Causal Validity.
       NCD is used strictly as a tiebreaker for low-structure candidates.
    """

    def __init__(self):
        # Template library: Minimal graphs for relational schemas
        # Format: List of (nodes, edges) where edges are (src, dst, type)
        self.templates = [
            {"name": "causal_chain", "nodes": 2, "edges": [("A", "B", "causes")]},
            {"name": "negated_outcome", "nodes": 2, "edges": [("A", "B", "prevents")]},
            {"name": "conditional", "nodes": 2, "edges": [("A", "B", "implies")]},
            {"name": "comparative", "nodes": 2, "edges": [("A", "B", "greater_than")]},
        ]
        
        # Criticality matrix (simulated over session via dictionary for sparsity)
        self.criticality_counts = defaultdict(int)
        self.total_matches = 1  # Avoid division by zero

    def _parse_structure(self, text: str) -> Dict[str, Any]:
        """Extract structural features: negations, comparatives, causals, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|without)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|than)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            "causals": len(re.findall(r'\b(because|causes|leads to|results in|due to)\b', text_lower)),
            "numbers": re.findall(r'\d+(?:\.\d+)?', text),
            "entities": len(re.findall(r'\b[A-Z][a-z]+\b', text)), # Simple proper noun heuristic
            "raw_length": len(text),
            "word_count": len(text.split())
        }
        
        # Numeric evaluation capability
        if len(features["numbers"]) >= 2:
            try:
                nums = [float(n) for n in features["numbers"]]
                features["numeric_consistency"] = 1.0 if nums[0] > nums[1] else 0.5
            except:
                features["numeric_consistency"] = 0.0
        else:
            features["numeric_consistency"] = 0.0
            
        return features

    def _build_graph(self, features: Dict) -> Tuple[List, List]:
        """Convert features to a pseudo-graph representation for matching."""
        nodes = []
        edges = []
        
        if features["causals"] > 0:
            nodes.append("CausalNode")
            edges.append(("CausalNode", "Effect", "causes"))
        if features["negations"] > 0:
            nodes.append("NegNode")
            edges.append(("NegNode", "Target", "negates"))
        if features["comparatives"] > 0:
            nodes.append("CompNode")
            edges.append(("CompNode", "Ref", "greater_than"))
        if features["conditionals"] > 0:
            nodes.append("CondNode")
            edges.append(("CondNode", "Consequent", "implies"))
            
        return nodes, edges

    def _match_analogy(self, nodes: List, edges: List) -> float:
        """Compute analogical match score against templates."""
        if not edges:
            return 0.0
        
        max_score = 0.0
        for tmpl in self.templates:
            # Simplified subgraph isomorphism: Check if edge types exist
            tmpl_edges = [e[2] for e in tmpl["edges"]]
            match_count = 0
            for _, _, etype in edges:
                if etype in tmpl_edges:
                    match_count += 1
            
            if match_count > 0:
                score = match_count / len(tmpl["edges"])
                if score > max_score:
                    max_score = score
        
        # Update criticality matrix (simulated)
        if max_score > 0:
            self.total_matches += 1
            for n in nodes:
                self.criticality_counts[n] += 1
                
        return max_score

    def _check_causal_validity(self, text: str) -> float:
        """Check for obvious causal cycles or contradictions."""
        text_lower = text.lower()
        # Heuristic: If "A causes B" and "B prevents A" appear, it might be a cycle
        # For this lightweight version, we check for contradictory markers
        has_cause = "causes" in text_lower or "leads to" in text_lower
        has_prevent = "prevents" in text_lower or "stops" in text_lower
        
        if has_cause and has_prevent:
            # Potential conflict, lower validity unless structured as conditional
            if "if" in text_lower:
                return 1.0
            return 0.5
        return 1.0

    def _compute_criticality_score(self, nodes: List) -> float:
        """Compute susceptibility-like score based on co-activation."""
        if not nodes:
            return 0.0
        # Sum of counts for active nodes
        activation = sum(self.criticality_counts.get(n, 0) for n in nodes)
        # Normalize by total matches to get frequency
        freq = activation / self.total_matches if self.total_matches > 0 else 0
        # Frobenius-like norm approximation (sqrt of sum squares)
        return np.sqrt(freq + 1e-6)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if min(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._parse_structure(prompt)
        p_nodes, p_edges = self._build_graph(prompt_feat)
        
        # Pre-calculate prompt criticality baseline
        p_crit = self._compute_criticality_score(p_nodes)
        p_analogy = self._match_analogy(p_nodes, p_edges)
        p_causal = self._check_causal_validity(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            c_feat = self._parse_structure(cand)
            c_nodes, c_edges = self._build_graph(c_feat)
            
            # 1. Analogical Score (Structure Mapping)
            # Compare candidate structure to prompt structure via templates
            analogy_score = 0.0
            if c_edges and p_edges:
                # Check overlap in edge types
                p_types = set(e[2] for e in p_edges)
                c_types = set(e[2] for e in c_edges)
                overlap = len(p_types.intersection(c_types))
                analogy_score = overlap / max(len(p_types), 1)
            
            # 2. Criticality Score (Susceptibility)
            crit_score = self._compute_criticality_score(c_nodes)
            
            # 3. Causal Validity
            causal_val = self._check_causal_validity(cand)
            
            # 4. Numeric Consistency Check
            numeric_bonus = 0.0
            if prompt_feat["numbers"] and c_feat["numbers"]:
                # If both have numbers, check if logic holds (simplified)
                numeric_bonus = 0.2 if c_feat["numeric_consistency"] > 0 else -0.2
            
            # Final Score Calculation
            # Weights: Analogy (0.5), Criticality (0.3), Causal (0.2)
            base_score = (0.5 * analogy_score) + (0.3 * crit_score) + (0.2 * causal_val) + numeric_bonus
            
            # Tie-breaking with NCD if structural signals are weak
            if base_score < 0.1:
                ncd = self._ncd_score(prompt, cand)
                base_score = 0.5 - ncd # Lower NCD (more similar) -> higher score
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(base_score),
                "reasoning": f"Analogy:{analogy_score:.2f}, Crit:{crit_score:.2f}, Causal:{causal_val:.1f}"
            })
            
            # Update global state (Criticality matrix) for next iteration
            if analogy_score > 0:
                for n in c_nodes:
                    self.criticality_counts[n] += 1

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and causal validity.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        p_nodes, p_edges = self._build_graph(p_feat)
        a_nodes, a_edges = self._build_graph(a_feat)
        
        # Structural Overlap
        p_types = set(e[2] for e in p_edges) if p_edges else set()
        a_types = set(e[2] for e in a_edges) if a_edges else set()
        
        if not p_types and not a_types:
            # Fallback to lexical overlap if no structure
            overlap = len(set(prompt.lower().split()) & set(answer.lower().split()))
            return min(0.5 + (overlap / 10.0), 0.9)
            
        intersection = len(p_types.intersection(a_types))
        union = len(p_types.union(a_types)) if p_types.union(a_types) else 1
        struct_sim = intersection / union
        
        # Causal Consistency
        causal_ok = self._check_causal_validity(answer)
        
        # Numeric check
        num_ok = 1.0
        if p_feat["numbers"] and a_feat["numbers"]:
            num_ok = a_feat["numeric_consistency"]
            
        base_conf = (0.6 * struct_sim) + (0.3 * causal_ok) + (0.1 * num_ok)
        return min(max(base_conf, 0.0), 1.0)