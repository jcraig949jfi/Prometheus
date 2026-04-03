import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool combining Chaos Theory (stability analysis), Renormalization (coarse-graining),
    and Theory of Mind (second-order beliefs) to evaluate candidate answers.
    
    Mechanism:
    1. Parsing: Extracts propositions, logical relations, and numeric facts into a belief graph.
    2. ToM Layer: Adds second-order nodes representing "agent believes X".
    3. Renormalization: Iteratively collapses densely connected subgraphs into super-nodes.
    4. Chaos Analysis: Perturbs initial beliefs and measures divergence (Lyapunov exponent) across scales.
    5. Scoring: Combines structural consistency, computational verification, and stability metrics.
    6. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|results in|causes|due to)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|equal to|bigger|smaller)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|first|last|preceding|following)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
            'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or|must be|only option)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'pronoun_ambig': re.compile(r'\b(he|she|him|her|it|they)\b', re.IGNORECASE)
        }

    def _tokenize_and_parse(self, text: str) -> List[Dict]:
        """Extract propositions and assign initial belief scalars."""
        nodes = []
        text_lower = text.lower()
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]', text)
        
        for i, sent in enumerate(sentences):
            if not sent.strip():
                continue
            
            belief = 0.5
            relations = []
            
            # Lexical cues for initial belief
            if self.patterns['negation'].search(sent):
                belief = 0.2 # Negated statements start low unless context implies otherwise
            elif re.search(r'\b(true|correct|yes|indeed)\b', text_lower):
                belief = 0.9
            elif re.search(r'\b(false|wrong|no|incorrect)\b', text_lower):
                belief = 0.1
            else:
                belief = 0.6 # Default affirmative bias

            # Extract numeric values for computation later
            nums = [float(n) for n in self.patterns['numbers'].findall(sent)]
            
            nodes.append({
                'id': f"n_{i}",
                'text': sent.strip(),
                'belief': belief,
                'relations': relations,
                'nums': nums,
                'has_negation': bool(self.patterns['negation'].search(sent)),
                'has_conditional': bool(self.patterns['conditional'].search(sent)),
                'has_causal': bool(self.patterns['causal'].search(sent)),
                'has_comparative': bool(self.patterns['comparative'].search(sent)),
                'has_ordering': bool(self.patterns['ordering'].search(sent)),
            })
            
        return nodes

    def _build_graph(self, prompt: str, candidate: str) -> Tuple[np.ndarray, np.ndarray, int]:
        """Construct belief graph and weight matrix."""
        full_text = f"{prompt} {candidate}"
        nodes = self._tokenize_and_parse(full_text)
        
        n = len(nodes)
        if n == 0:
            return np.array([]), np.array([]), 0
            
        # Initialize belief vector b
        b = np.array([node['belief'] for node in nodes])
        
        # Initialize weight matrix W
        W = np.zeros((n, n))
        
        for i, node in enumerate(nodes):
            # Self-loop for stability
            W[i, i] = 0.5
            
            for j, other in enumerate(nodes):
                if i == j:
                    continue
                
                # Logical relations
                if node['has_conditional'] and other['id'] in node['text']:
                    W[i, j] = 0.9 # Implication
                elif node['has_causal']:
                    W[i, j] = 0.8 # Causal
                elif node['has_comparative']:
                    W[i, j] = 0.7 # Comparative
                elif node['has_ordering']:
                    W[i, j] = 0.6 # Ordering
                
                # Negation propagation
                if node['has_negation'] and other['has_negation']:
                    W[i, j] = -0.5 # Double negation reinforcement or cancellation logic simplified

        # Add Theory of Mind layer (Second order nodes)
        # n_i -> n_i* (Agent believes n_i)
        tom_nodes = []
        for node in nodes:
            tom_nodes.append({
                'id': f"{node['id']}*",
                'belief': 0.5, # Initial uncertainty about agent's belief
                'parent_idx': nodes.index(node)
            })
        
        n_tom = len(tom_nodes)
        total_n = n + n_tom
        
        # Expand matrices
        b_exp = np.zeros(total_n)
        b_exp[:n] = b
        b_exp[n:] = [t['belief'] for t in tom_nodes]
        
        W_exp = np.zeros((total_n, total_n))
        W_exp[:n, :n] = W
        
        # Connect n_i -> n_i* with weight 0.5
        for k, t_node in enumerate(tom_nodes):
            idx = n + k
            parent_idx = t_node['parent_idx']
            W_exp[parent_idx, idx] = 0.5
            # Feedback loop for recursive mentalizing (depth 2 effectively)
            W_exp[idx, parent_idx] = 0.3
            
        return b_exp, W_exp, n

    def _renormalize(self, b: np.ndarray, W: np.ndarray, threshold: float = 0.6) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Coarse-grain the graph by collapsing densely connected nodes."""
        history = [(b.copy(), W.copy())]
        current_b = b
        current_W = W
        
        while current_W.shape[0] > 5: # Stop if too small
            n = current_W.shape[0]
            merged_indices = set()
            new_nodes_map = [] # Map old indices to new super-node indices
            
            # Identify clusters based on mutual weight > threshold
            # Simplified: Find pairs with high mutual weight
            clusters = []
            visited = set()
            
            for i in range(n):
                if i in visited:
                    continue
                cluster = {i}
                for j in range(i+1, n):
                    if j in visited:
                        continue
                    if abs(current_W[i, j]) > threshold and abs(current_W[j, i]) > threshold:
                        cluster.add(j)
                        visited.add(j)
                visited.add(i)
                if len(cluster) > 1:
                    clusters.append(cluster)
                else:
                    # Singleton cluster
                    clusters.append({i})
            
            if len(clusters) == n: # No merging possible
                break
                
            # Build new graph
            new_n = len(clusters)
            new_b = np.zeros(new_n)
            new_W = np.zeros((new_n, new_n))
            
            for new_idx, cluster in enumerate(clusters):
                # Weighted average of beliefs
                cluster_list = list(cluster)
                weights = [sum(abs(current_W[i, :])) for i in cluster_list] # Strength as weight
                total_w = sum(weights) + 1e-9
                
                if total_w == 0:
                    new_b[new_idx] = np.mean([current_b[i] for i in cluster_list])
                else:
                    new_b[new_idx] = sum(current_b[i] * w for i, w in zip(cluster_list, weights)) / total_w
                
                # Map old to new
                for old_idx in cluster:
                    new_nodes_map.append((old_idx, new_idx))
            
            # Aggregate edges
            for i, cluster_i in enumerate(clusters):
                for j, cluster_j in enumerate(clusters):
                    if i == j:
                        new_W[i, j] = 0.5 # Self loop
                        continue
                    
                    weight_sum = 0.0
                    count = 0
                    for old_i in cluster_i:
                        for old_j in cluster_j:
                            weight_sum += current_W[old_i, old_j]
                            count += 1
                    if count > 0:
                        new_W[i, j] = weight_sum # Summing weights as per algo
                    
            current_b = new_b
            current_W = new_W
            history.append((current_b.copy(), current_W.copy()))
            
            if len(history) > 10: # Prevent infinite loops
                break
                
        return history

    def _chaos_stability(self, b: np.ndarray, W: np.ndarray) -> float:
        """Calculate Lyapunov-like exponent."""
        epsilon = 0.01
        b_pert = b.copy()
        
        # Perturb random subset
        perturb_mask = np.random.rand(len(b)) > 0.5
        b_pert[perturb_mask] += epsilon
        b_pert[perturb_mask] = np.clip(b_pert[perturb_mask], 0, 1)
        
        history = self._renormalize(b, W)
        history_pert = self._renormalize(b_pert, W)
        
        if len(history) != len(history_pert):
            return 1.0 # Instability in structure
            
        lyap_sum = 0.0
        L = len(history)
        if L == 0:
            return 0.0
            
        for t in range(L):
            b_t = history[t][0]
            b_pt = history_pert[t][0]
            
            dist = np.linalg.norm(b_pt - b_t)
            if dist > 0:
                lyap_sum += np.log(dist / epsilon + 1e-9)
            else:
                lyap_sum += 0 # No divergence
                
        return lyap_sum / L if L > 0 else 0.0

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Score based on explicit structural matches and numeric consistency."""
        score = 0.0
        count = 0
        
        # Numeric evaluation
        p_nums = [float(x) for x in self.patterns['numbers'].findall(prompt)]
        c_nums = [float(x) for x in self.patterns['numbers'].findall(candidate)]
        
        # Check for direct numeric contradiction or confirmation
        if p_nums and c_nums:
            # Simple heuristic: if candidate number exists in prompt, it's likely consistent
            # If candidate introduces new numbers that contradict prompt logic (hard to detect without full NLP)
            # We reward finding numbers that match prompt numbers
            matches = sum(1 for n in c_nums if any(abs(n - p) < 1e-6 for p in p_nums))
            if matches > 0:
                score += 0.5 * (matches / len(c_nums))
                count += 1
        
        # Structural keyword presence
        if self.patterns['negation'].search(candidate) and self.patterns['negation'].search(prompt):
            score += 0.2
            count += 1
            
        if self.patterns['conditional'].search(candidate) and self.patterns['conditional'].search(prompt):
            score += 0.2
            count += 1
            
        # Length penalty for gibberish
        if len(candidate.split()) < 2:
            score -= 0.1
            
        return score / (count + 1) if count > 0 else 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detect ambiguity, presupposition, and unanswerability.
        Returns a cap for confidence.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(p_lower):
            return 0.2
            
        # 2. False Dichotomy indicators
        if self.patterns['false_dichotomy'].search(p_lower):
            return 0.3
            
        # 3. Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_lower) and not re.search(r'\b(data|fact|metric)\b', p_lower):
            return 0.4
            
        # 4. Pronoun Ambiguity check (heuristic: multiple males/females + "who")
        if re.search(r'\bwho\b', p_lower) and len(self.patterns['pronoun_ambig'].findall(p_lower)) > 1:
            return 0.3
            
        # 5. Unanswerable/Insufficient info keywords
        if re.search(r'\b(unknown|missing|cannot be determined|insufficient)\b', p_lower):
            return 0.1
            
        return 1.0 # No red flags detected

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1+s2).encode()))
        if max(len1, len2) == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural & Computation Score (Primary)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Graph Construction
            b, W, n_orig = self._build_graph(prompt, cand)
            
            if n_orig == 0:
                # Fallback for empty parse
                final_score = 0.1
                reasoning = "Parsing failed; fallback to low score."
            else:
                # 3. Renormalization & Chaos Stability
                try:
                    lyap = self._chaos_stability(b, W)
                    # Stability metric: lower (more negative) is better
                    stability_score = np.exp(-max(lyap, 0))
                except Exception:
                    stability_score = 0.5
                    lyap = 0.0

                # 4. Consistency (Simplified truth-value check)
                # If candidate contradicts explicit negation in prompt
                consistency = 1.0
                if self.patterns['negation'].search(prompt) and not self.patterns['negation'].search(cand):
                    # Potential contradiction if topics align (simplified)
                    if any(k in cand.lower() for k in ['all', 'every', 'always']):
                        consistency = 0.5
                
                # Final Score Calculation
                # S = exp(-max(lambda, 0)) * C
                # Augmented with structural score
                base_score = stability_score * consistency
                final_score = 0.6 * base_score + 0.4 * struct_score
                
                # Cap by meta-confidence (Epistemic Honesty)
                if final_score > meta_cap:
                    final_score = meta_cap
                    
                reasoning = f"Stability(λ={lyap:.2f}), Struct={struct_score:.2f}, MetaCap={meta_cap:.2f}"

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural signal
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Apply meta cap
        final_conf = min(raw_score, meta_cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))