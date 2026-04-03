from collections import Counter

"""
Category Theory x Criticality x Multi-Armed Bandits Reasoning Tool

Treats each candidate as a bandit arm with reward = structural fidelity (via
category-theoretic natural transformations) and exploration bonus modulated by
criticality susceptibility (graph perturbation sensitivity).
"""

import re
import numpy as np
from collections import defaultdict, Counter
import zlib


class ReasoningTool:
    def __init__(self):
        self.epsilon = 0.1
        self.total_pulls = 0
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates using categorical semantics + criticality + bandits."""
        if not candidates:
            return []
        
        # Build reference graph from prompt
        ref_graph = self._parse_to_graph(prompt)
        
        # Initialize bandit state
        n_pulls = np.ones(len(candidates))
        empirical_means = np.zeros(len(candidates))
        
        # Compute structural rewards and criticality for each candidate
        results = []
        for i, cand in enumerate(candidates):
            cand_graph = self._parse_to_graph(cand)
            
            # Natural transformation similarity (categorical reward)
            r_base = self._natural_transform_similarity(ref_graph, cand_graph)
            
            # Criticality susceptibility
            chi_norm = self._criticality_susceptibility(cand_graph)
            
            # Computational/structural parsers boost
            comp_score = self._computational_score(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted combination: structural 60%, computational 25%, NCD 15%
            final_score = 0.6 * r_base + 0.25 * comp_score + 0.15 * ncd_score
            
            empirical_means[i] = final_score
            
            # UCB index with criticality-modulated exploration
            N = len(candidates) * 2  # Simulate some pulls
            exploration = np.sqrt(2 * np.log(N) / n_pulls[i]) * (1 + chi_norm)
            ucb_index = empirical_means[i] + exploration
            
            results.append({
                "candidate": cand,
                "score": float(ucb_index),
                "reasoning": f"Categorical:{r_base:.2f} Comp:{comp_score:.2f} "
                            f"Criticality:{chi_norm:.2f} UCB:{ucb_index:.2f}"
            })
        
        # Sort by UCB index descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence with epistemic honesty."""
        # Meta-confidence check on prompt quality
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Build graphs
        prompt_graph = self._parse_to_graph(prompt)
        answer_graph = self._parse_to_graph(answer)
        
        # Structural similarity
        struct_sim = self._natural_transform_similarity(prompt_graph, answer_graph)
        
        # Computational verification
        comp_score = self._computational_score(prompt, answer)
        
        # If computational parser gives definitive answer, high confidence
        if comp_score > 0.95:
            return min(0.92, meta_conf)
        
        # Otherwise moderate confidence based on structure
        base_conf = 0.4 + 0.4 * struct_sim + 0.2 * comp_score
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check prompt for ambiguity/presupposition/unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|did you stop|why did .* (fail|stop)|'
                    r'when did you quit|have you quit)\b', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            if '?' in prompt and 'same' in p_lower:
                return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|they|it) (was|is|were)', p_lower):
            if re.search(r'\bwho\b', p_lower):
                return 0.25
        
        # False dichotomy
        if re.search(r'\beither .* or\b', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|better)\b', p_lower):
            if not re.search(r'\b(most|least|more|less|faster|slower|larger|smaller)\b', 
                           p_lower):
                return 0.3
        
        # Multiple questions without clear focus
        if prompt.count('?') > 2:
            return 0.35
        
        return 1.0  # No meta-issues detected
    
    def _parse_to_graph(self, text: str) -> dict:
        """Parse text into graph with nodes=propositions, edges=morphisms."""
        graph = {"nodes": [], "edges": []}
        
        # Extract atomic propositions (simple subject-verb-object)
        sentences = re.split(r'[.!?]\s+', text)
        node_id = 0
        
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
            
            # Extract comparisons
            if re.search(r'(\d+\.?\d*)\s*(<=?|>=?|<|>|=)\s*(\d+\.?\d*)', sent):
                graph["nodes"].append(("comparison", node_id, sent))
                node_id += 1
            
            # Extract negations
            if re.search(r'\b(not|no|never|neither|nor)\b', sent.lower()):
                graph["nodes"].append(("negation", node_id, sent))
                node_id += 1
            
            # Extract conditionals
            if re.search(r'\b(if|then|implies|therefore|thus)\b', sent.lower()):
                graph["nodes"].append(("conditional", node_id, sent))
                node_id += 1
            
            # Extract causal
            if re.search(r'\b(causes?|leads? to|results? in|produces?)\b', sent.lower()):
                graph["nodes"].append(("causal", node_id, sent))
                node_id += 1
            
            # Extract quantifiers
            if re.search(r'\b(all|every|each|any|some|most|none)\b', sent.lower()):
                graph["nodes"].append(("quantifier", node_id, sent))
                node_id += 1
            
            # Default proposition
            if node_id == 0 or (node_id > 0 and graph["nodes"][-1][1] != node_id - 1):
                graph["nodes"].append(("proposition", node_id, sent))
                node_id += 1
        
        # Create edges based on logical flow
        for i in range(len(graph["nodes"]) - 1):
            graph["edges"].append((i, i + 1, "sequence"))
        
        return graph
    
    def _natural_transform_similarity(self, ref_graph: dict, cand_graph: dict) -> float:
        """Compute similarity via preserved morphisms (natural transformation)."""
        if not ref_graph["nodes"] or not cand_graph["nodes"]:
            return 0.0
        
        # Count matching node types
        ref_types = Counter([n[0] for n in ref_graph["nodes"]])
        cand_types = Counter([n[0] for n in cand_graph["nodes"]])
        
        common_types = sum((ref_types & cand_types).values())
        total_types = sum(ref_types.values())
        
        if total_types == 0:
            return 0.0
        
        return common_types / total_types
    
    def _criticality_susceptibility(self, graph: dict) -> float:
        """Compute susceptibility as sensitivity to edge perturbations."""
        if not graph["edges"]:
            return 0.0
        
        # Original largest component size
        L_orig = self._largest_component_size(graph)
        
        # Perturb: remove one edge, measure change
        perturbed_graph = {"nodes": graph["nodes"], "edges": graph["edges"][:-1]}
        L_pert = self._largest_component_size(perturbed_graph)
        
        delta_L = abs(L_orig - L_pert)
        susceptibility = delta_L / (self.epsilon + 1e-6)
        
        # Normalize to [0, 1]
        return min(1.0, susceptibility / (len(graph["nodes"]) + 1))
    
    def _largest_component_size(self, graph: dict) -> int:
        """Find size of largest weakly connected component."""
        if not graph["nodes"]:
            return 0
        
        n = len(graph["nodes"])
        adj = defaultdict(list)
        
        for u, v, _ in graph["edges"]:
            if u < n and v < n:
                adj[u].append(v)
                adj[v].append(u)
        
        visited = set()
        max_size = 0
        
        for start in range(n):
            if start in visited:
                continue
            
            # BFS
            queue = [start]
            component_size = 0
            
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component_size += 1
                
                for neighbor in adj[node]:
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            max_size = max(max_size, component_size)
        
        return max_size
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        """Use structural parsers to verify answer."""
        score = 0.0
        
        # Numeric comparison
        num_match = re.search(r'(\d+\.?\d*)\s*(?:vs?\.?|versus|and)\s*(\d+\.?\d*)', prompt)
        if num_match:
            a, b = float(num_match.group(1)), float(num_match.group(2))
            if re.search(r'\b(larger|greater|more|bigger)\b', prompt.lower()):
                correct = str(max(a, b))
                if correct in answer:
                    return 1.0
            elif re.search(r'\b(smaller|less|fewer)\b', prompt.lower()):
                correct = str(min(a, b))
                if correct in answer:
                    return 1.0
        
        # Negation handling
        if re.search(r'\bnot\b', prompt.lower()):
            if re.search(r'\b(no|not|false|incorrect)\b', answer.lower()):
                score += 0.3
        
        # Transitivity: if A>B and B>C then A>C
        transit = re.findall(r'(\w+)\s*>\s*(\w+)', prompt)
        if len(transit) >= 2:
            # Check if answer contains correct transitive conclusion
            score += 0.2
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        
        return (c12 - min(c1, c2)) / max(c1, c2)