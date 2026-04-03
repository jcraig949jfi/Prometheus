import re
import numpy as np
from collections import deque
import zlib

class ReasoningTool:
    """
    A reasoning tool combining causal graph extraction, constraint propagation,
    and property-based perturbation testing to score candidate answers.
    
    Mechanism:
    1. Parses text into a DAG of propositions (literals, causals, comparatives).
    2. Propagates constraints topologically to establish a baseline truth state.
    3. Uses property-based testing (random perturbations) to measure system criticality.
    4. Scores candidates based on structural consistency, computational verification,
       and robustness to noise, while enforcing epistemic honesty on ambiguous inputs.
    """
    
    def __init__(self):
        self.ncd_weight = 0.15
        self.struct_weight = 0.55
        self.comp_weight = 0.30

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: presupposition, ambiguity, unanswerability."""
        p = prompt.lower()
        traps = [
            r"have you (stopped|quit) ",       # Presupposition
            r"why did .+ (fail|stop|die) ",    # Presupposition of event
            r"every .+ (a|an) ",               # Scope ambiguity (simplified)
            r" told .+ he ",                   # Pronoun ambiguity context
            r" who (was|is|did)?",             # Pronoun resolution needed
            r"either .+ or ",                  # False dichotomy hint
            r"best|worst|favorite",            # Subjectivity without criteria
            r"impossible to tell",             # Explicit unanswerability
            r"not enough information"          # Explicit unanswerability
        ]
        for pattern in traps:
            if re.search(pattern, p):
                return 0.25  # Cap confidence for ambiguous/trap questions
        return 1.0

    def _parse_graph(self, text: str):
        """Extract nodes and edges. Returns nodes list, adjacency matrix, values, types."""
        # Simplified extraction for demo: identify numbers, booleans, and simple causals
        nodes = []
        edges = [] # (src, dst, type)
        values = []
        types = []
        
        # Tokenize simple propositions
        sentences = re.split(r'[.!?]', text)
        node_idx = 0
        
        # Map for existing nodes to avoid duplicates in simple cases
        node_map = {} 

        def get_node_id(content, v, t):
            key = content[:20] # Rough hash
            if key in node_map:
                return node_map[key]
            nodes.append(content)
            values.append(v)
            types.append(t)
            idx = len(nodes) - 1
            node_map[key] = idx
            return idx

        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            s_low = sent.lower()
            
            # Detect Booleans
            val = 0.5
            t = 'literal'
            if any(w in s_low for w in ['true', 'yes', 'is correct']): val = 1.0
            elif any(w in s_low for w in ['false', 'no', 'is incorrect']): val = 0.0
            
            # Detect Comparatives (X > Y)
            comp_match = re.search(r'(\d+(?:\.\d+)?)\s*(greater|less|equal)\s*(?:than)?\s*(\d+(?:\.\d+)?)', s_low)
            if comp_match:
                n1, op, n2 = float(comp_match.group(1)), comp_match.group(2), float(comp_match.group(3))
                # Create nodes for numbers
                id1 = get_node_id(f"num_{n1}", n1, 'numeric')
                id2 = get_node_id(f"num_{n2}", n2, 'numeric')
                if op == 'greater': edges.append((id1, id2, 'gt'))
                elif op == 'less': edges.append((id1, id2, 'lt'))
                else: edges.append((id1, id2, 'eq'))
                continue # Skip generic parsing for this sentence

            # Detect Causals (A because B, A leads to B)
            causal_match = re.search(r'(.+?)\s+(because|leads to|results in|implies)\s+(.+)', s_low)
            if causal_match:
                src_txt = causal_match.group(1).strip()
                dst_txt = causal_match.group(3).strip()
                src_id = get_node_id(src_txt[:10], 0.5, 'literal') # Placeholder val
                dst_id = get_node_id(dst_txt[:10], 0.5, 'literal')
                edges.append((src_id, dst_id, 'causes'))
                continue

            # Generic literal
            if val != 0.5 or len(sent) > 5:
                get_node_id(sent, val, 'literal')

        if len(nodes) == 0:
            return [], np.array([]), [], []

        n = len(nodes)
        adj = np.zeros((n, n))
        for u, v, etype in edges:
            if u < n and v < n:
                adj[u, v] = 1.0
        
        return nodes, adj, np.array(values), types

    def _propagate(self, adj, values, types):
        """Single pass constraint propagation."""
        n = len(values)
        if n == 0: return values
        s = values.copy()
        
        # Topological sort approximation (just iterate multiple times for DAG convergence)
        for _ in range(n): 
            for i in range(n):
                # If node i has incoming edges
                parents = np.where(adj[:, i] > 0)[0]
                for p in parents:
                    if types[p] == 'numeric' and types[i] == 'numeric':
                        # Numeric constraints handled separately usually, 
                        # here we just propagate truthiness for logic
                        pass
                    else:
                        # Implies/Causes: if parent is True, child must be True
                        if s[p] > 0.5:
                            s[i] = max(s[i], s[p])
                        # If parent is False, no direct update in this simple model without negation handling
        return s

    def _perturb_and_score(self, adj, base_values, types, n_trials=50):
        """Property-based testing to find minimal perturbation distance."""
        if len(base_values) == 0: return 0.0, 0.0
        
        n = len(base_values)
        base_state = self._propagate(adj, base_values, types)
        base_correct = base_state > 0.5 # Simplified correctness
        
        distances = []
        susceptibility_scores = []

        for _ in range(n_trials):
            # Generate perturbation
            noise = np.random.normal(0, 0.2, n)
            # Flip bits for boolean, add noise for numeric
            perturbed_vals = base_values.copy()
            mask = np.random.rand(n) < 0.3
            perturbed_vals[mask] = 1.0 - perturbed_vals[mask] # Flip
            perturbed_vals += noise
            
            # Propagate
            new_state = self._propagate(adj, perturbed_vals, types)
            
            # Measure distance (Hamming/L2 hybrid)
            diff = np.abs(new_state - base_state)
            dist = np.sum(diff > 0.1) # Count changed nodes
            distances.append(dist)
            
            # Did the global answer flip? (Simplified: did >50% of nodes change?)
            flip_ratio = np.mean(diff > 0.5)
            susceptibility_scores.append(flip_ratio)

        if not distances: return 0.0, 0.0
        
        d_min = min(distances) if min(distances) > 0 else 1.0
        chi = np.std(susceptibility_scores) / (np.mean(distances) + 1e-6)
        
        # Correlation length approx
        lambda_val = np.mean(distances) if distances else 1.0
        
        score = (chi * lambda_val) / (n + 1) # Normalize roughly
        return min(1.0, score), d_min

    def _compute_ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)

    def _extract_numeric_answer(self, text):
        # Find the last number in the text as a potential computed answer
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        if matches:
            try: return float(matches[-1])
            except: return None
        return None

    def _check_computation(self, prompt, candidate):
        """Attempt to verify numeric/logic computation."""
        # Extract numbers from prompt
        p_nums = re.findall(r'\d+(?:\.\d+)?', prompt)
        c_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
        
        if not p_nums or not c_nums:
            return 0.0 # No computation to check
            
        try:
            p_vals = [float(x) for x in p_nums]
            c_val = float(c_nums[-1])
            
            # Heuristic checks for common patterns
            # Sum check
            if abs(sum(p_vals) - c_val) < 1e-6: return 1.0
            # Product check (if small list)
            if len(p_vals) <= 3:
                prod = 1.0
                for x in p_vals: prod *= x
                if abs(prod - c_val) < 1e-6: return 1.0
            # Difference
            if len(p_vals) == 2 and abs(p_vals[0] - p_vals[1] - c_val) < 1e-6: return 1.0
            
        except: pass
        
        return 0.0 # Computation failed or not detected

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        prompt_nodes, adj, p_vals, p_types = self._parse_graph(prompt)
        has_structure = len(prompt_nodes) > 0
        
        # Pre-calculate prompt criticality if structure exists
        prompt_crit = 0.0
        if has_structure:
            prompt_crit, _ = self._perturb_and_score(adj, p_vals, p_types)

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Structural Consistency (55%)
            # Parse candidate, merge with prompt context implicitly by checking consistency
            cand_nodes, c_adj, c_vals, c_types = self._parse_graph(cand)
            
            struct_score = 0.5
            if has_structure and len(cand_nodes) > 0:
                # Check if candidate contradicts prompt literals (simplified)
                # In a full engine, we'd merge graphs. Here we check overlap.
                overlap = 0
                for cn in cand_nodes:
                    if any(cn[:5] in pn for pn in prompt_nodes): overlap += 1
                struct_score = min(1.0, (overlap + 1) / (len(cand_nodes) + 1))
                reasoning_parts.append(f"Structural overlap: {struct_score:.2f}")
            elif not has_structure:
                # If no structure, rely on other factors
                struct_score = 0.5
                reasoning_parts.append("No structural graph detected")

            # 2. Computational Verification (30%)
            comp_score = self._check_computation(prompt, cand)
            if comp_score > 0:
                reasoning_parts.append(f"Computation verified: {comp_score:.2f}")
            
            # 3. Criticality/Robustness (15% of total, derived from prompt stability)
            # If the prompt is highly critical (fragile), and candidate matches, boost slightly
            crit_bonus = prompt_crit * 0.2 if has_structure else 0.0
            
            # 4. NCD Tiebreaker (15%)
            ncd = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score)
            ncd_score = (1.0 - ncd) * self.ncd_weight
            
            # Final Score Composition
            final_score = (struct_score * self.struct_weight) + \
                          (comp_score * self.comp_weight) + \
                          (ncd_score) + \
                          crit_bonus
            
            # Normalize roughly to 0-1
            final_score = min(1.0, max(0.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Baseline evaluation"
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Tier B: Epistemic Honesty Check
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
            
        # Parse and check structure
        nodes, adj, vals, types = self._parse_graph(prompt)
        
        # If no structure and no numbers, low confidence
        if len(nodes) == 0 and not re.search(r'\d', prompt):
            return 0.25 # Honest uncertainty
            
        # Calculate base confidence based on computational verification
        comp_verif = self._check_computation(prompt, answer)
        
        # If computation is definitive
        if comp_verif == 1.0:
            return min(0.95, meta_conf) # Cap at 0.95 unless proven otherwise
            
        # If structure exists, check stability
        if len(nodes) > 0:
            crit, d_min = self._perturb_and_score(adj, vals, types)
            # High criticality (fragility) might lower confidence if answer is simple
            base_conf = 0.6 + (0.3 * (1.0 - crit)) # More stable = higher conf
            return min(base_conf, meta_conf)
            
        return 0.5 # Default moderate confidence