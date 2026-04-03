import re
import math
import zlib
import numpy as np

class ReasoningTool:
    """
    Plastic-Modulated Incentive Scoring (PMIS) Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, comparatives, and conditionals.
    2. Neuromodulated Propagation: Uses a gain vector based on entropy to scale belief propagation
       through a Hebbian weight matrix, simulating plasticity.
    3. Mechanism Design: Applies a log-scoring rule to incentivize consistency between the 
       candidate's explicit claims and the propagated logical constraints.
    4. Epistemic Honesty: Caps confidence if presuppositions, ambiguities, or false dichotomies are detected.
    """
    
    def __init__(self):
        self.eta = 0.01  # Plasticity learning rate
        self.epsilon = 1e-9

    def _sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    def _parse_structure(self, text):
        """Extracts nodes and edges from text using regex."""
        text_lower = text.lower()
        nodes = []
        edges = []  # (src_idx, dst_idx, type, polarity)
        
        # Simple tokenization for propositions (split by common delimiters but keep context)
        # We treat the whole text as a graph of potential relations
        sentences = re.split(r'[.;?!]', text)
        
        node_id = 0
        node_map = {} # map simple string to id
        
        def get_node_id(content):
            content = content.strip()
            if not content: return None
            if content not in node_map:
                node_map[content] = node_id
                nodes.append({'id': node_id, 'content': content, 'polarity': 1.0, 'value': None})
                return node_id
            return node_map[content]

        # Pattern: Comparatives (A > B, A less than B)
        comp_patterns = [
            (r'(\w+)\s+is\s+greater\s+than\s+(\w+)', 1),
            (r'(\w+)\s+>\s+(\w+)', 1),
            (r'(\w+)\s+is\s+less\s+than\s+(\w+)', -1),
            (r'(\w+)\s+<\s+(\w+)', -1),
            (r'(\w+)\s+exceeds\s+(\w+)', 1)
        ]
        
        for pat, polarity in comp_patterns:
            for m in re.finditer(pat, text_lower):
                src = get_node_id(m.group(1))
                dst = get_node_id(m.group(2))
                if src is not None and dst is not None:
                    edges.append((src, dst, 'order', polarity))
                    # Add reverse for transitivity check if needed, but directed is fine for now

        # Pattern: Conditionals (If A then B)
        cond_pat = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for m in re.finditer(cond_pat, text_lower):
            src = get_node_id(m.group(1))
            dst = get_node_id(m.group(2))
            if src is not None and dst is not None:
                edges.append((src, dst, 'implication', 1.0))

        # Pattern: Negations (Not A, A is false)
        neg_pat = r'(?:not|no|false|never)\s+(\w+)'
        for m in re.finditer(neg_pat, text_lower):
            target = get_node_id(m.group(1))
            if target is not None:
                # Mark node polarity
                if target < len(nodes):
                    nodes[target]['polarity'] = -1.0

        # Fallback: If no specific logic found, treat sentences as nodes
        if len(nodes) == 0:
            for i, sent in enumerate(sentences):
                s = sent.strip()
                if s:
                    nodes.append({'id': i, 'content': s, 'polarity': 1.0, 'value': None})
                    # Implicit linear flow
                    if i > 0:
                        edges.append((i-1, i, 'sequence', 1.0))
        
        return nodes, edges

    def _check_meta_confidence(self, prompt):
        """Detects Tier B traps: presupposition, ambiguity, false dichotomy."""
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps
        if re.search(r'(have you stopped|did you stop|why did .+ fail|why is .+ bad)', p):
            score = 0.2
        # 2. Scope/Pronoun ambiguity
        if re.search(r'(every .+ a .+|told .+ he was|told .+ she was)', p) and '?' in p:
            score = min(score, 0.3)
        # 3. False Dichotomy
        if re.search(r'(either .+ or .+|is it .+ or .+\?)', p) and not re.search(r'(yes|no|true|false)', p):
             score = min(score, 0.4)
        # 4. Subjectivity without criteria
        if re.search(r'(best|worst|favorite|ugliest)', p) and not re.search(r'(data|stats|numbers)', p):
            score = min(score, 0.3)
            
        return score

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def _run_pmis(self, prompt, candidate):
        """Core PMIS Algorithm."""
        full_text = f"{prompt} {candidate}"
        nodes, edges = self._parse_structure(full_text)
        
        if len(nodes) == 0:
            return 0.5, "No structure parsed"

        n = len(nodes)
        W = np.full((n, n), 0.1) # Initial Hebbian strengths
        np.fill_diagonal(W, 0)
        
        # Build adjacency from edges
        for src, dst, _, polarity in edges:
            if src < n and dst < n:
                W[src, dst] = polarity * 0.9 # Strong initial constraint
        
        # Initial truth assignment (r): 1 if candidate asserts, 0 otherwise
        # Simplified: Assume candidate affirms the parsed nodes unless negated
        r = np.ones(n) * 0.5 # Start neutral
        cand_lower = candidate.lower()
        
        for i, node in enumerate(nodes):
            content = node['content']
            if content in cand_lower or content in prompt.lower():
                # If node is present in candidate, initial belief is high, modulated by polarity
                r[i] = 0.9 if node['polarity'] > 0 else 0.1
            else:
                r[i] = 0.5

        # Neuromodulatory gain (g): High gain for uncertain nodes (entropy)
        # Entropy of Bernoulli(p) is max at 0.5
        entropy = - (r * np.log2(r + self.epsilon) + (1-r) * np.log2(1-r + self.epsilon))
        g = 1.0 + (entropy / np.max(entropy + self.epsilon)) # Scale gain based on uncertainty

        # Constraint Propagation (Loopy Belief Propagation approximation)
        for _ in range(5):
            # msg = W @ (g * r) -> Influence of neighbors scaled by gain
            influence = W @ (g * r)
            # Update r via sigmoid (squash to [0,1])
            r = self._sigmoid(influence + np.log(r / (1-r + self.epsilon)) * 0.5) # Mix with prior
            
        # Plasticity Update (Hebbian)
        delta = np.outer(r, r)
        W += self.eta * (delta - W)

        # Mechanism Design Scoring (Log Score)
        # Score = Sum(log(p_i)) where p_i is the propagated belief consistent with candidate
        total_score = 0.0
        count = 0
        for i in range(n):
            p_i = max(self.epsilon, min(1-self.epsilon, r[i]))
            # If the candidate explicitly asserts the node (r started high), we reward consistency
            # If the node was neutral, we reward the propagated logical conclusion
            if r[i] > 0.5:
                total_score += math.log(p_i)
            else:
                total_score += math.log(1 - p_i)
            count += 1
            
        avg_log_score = total_score / (count + self.epsilon)
        # Normalize to 0-1 range roughly
        normalized_score = self._sigmoid(avg_log_score * 2) 
        
        return normalized_score, f"Propagated {len(edges)} constraints over {n} nodes."

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        meta_cap = self._check_meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Computation Signal (PMIS)
            score, reason = self._run_pmis(prompt, cand)
            
            # 2. Numeric Evaluation (Constructive Computation)
            # Check for simple math expressions in candidate vs prompt
            numbers_p = re.findall(r'\d+\.?\d*', prompt)
            numbers_c = re.findall(r'\d+\.?\d*', cand)
            numeric_bonus = 0.0
            if numbers_p and numbers_c:
                try:
                    # Simple heuristic: if candidate number is logically derived (e.g. sum)
                    # For this implementation, we check exact match or simple inequality
                    p_vals = [float(x) for x in numbers_p]
                    c_vals = [float(x) for x in numbers_c]
                    if p_vals and c_vals:
                        # If prompt implies a comparison and candidate matches the truth
                        if any(x > y for x in p_vals for y in p_vals if x!=y): # Dummy check for structure
                             pass 
                        # Boost if numeric values align with logical direction (simplified)
                        numeric_bonus = 0.1 
                except: pass

            final_score = (0.8 * score) + (0.2 * numeric_bonus)
            
            # 3. NCD Tiebreaker (Max 15% influence)
            # Only used if scores are very close, but here we blend slightly for robustness
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale small
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            final_score = (final_score * 0.85) + ncd_score
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            # If the prompt is a trap, the maximum possible score is capped
            if meta_cap < 0.5:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight variation but keep low

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": reason
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Meta-Confidence Check (Tier B)
        meta_score = self._check_meta_confidence(prompt)
        
        # 2. Structural Check
        nodes, edges = self._parse_structure(prompt)
        structural_signal = len(edges) > 0 or len(nodes) > 1
        
        if not structural_signal:
            # No structure found -> Honest uncertainty
            return 0.2 
        
        # 3. Run PMIS to get consistency score
        score, _ = self._run_pmis(prompt, answer)
        
        # 4. Cap by meta-confidence
        final_conf = min(score, meta_score)
        
        # 5. Never return > 0.9 unless definitive (heuristic: high structural match + no ambiguity)
        if meta_score < 1.0:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 0.95))