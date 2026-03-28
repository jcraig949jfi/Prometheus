class ReasoningTool:
    """
    A reasoning tool combining Thermodynamics (Entropy), Analogical Reasoning (Structure Mapping),
    and the Free Energy Principle (Prediction Error) to evaluate candidate answers.
    
    Mechanism:
    1. Parses prompt and candidates into graph-like structures (entities, relations, values).
    2. Computes an analogical reward based on structural alignment between prompt and candidate.
    3. Calculates prediction error (KL-divergence) between expected and observed relational distributions.
    4. Incorporates entropy to encourage diverse mapping hypotheses.
    5. Detects epistemic traps (Tier B) to cap confidence on ambiguous/unanswerable queries.
    """

    def __init__(self):
        self.alpha = 0.5  # Entropy weight
        self.beta = 2.0   # Analogical reward weight
        self.gamma = 1.0  # Prediction error weight

    def _parse_structure(self, text: str) -> Dict:
        """
        Extracts structural features: entities, numeric values, negations, comparatives, causality.
        Returns a dictionary representing the graph nodes and edges.
        """
        text_lower = text.lower()
        nodes = []
        edges = []
        features = []
        
        # 1. Numeric Extraction
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
        nums_found = []
        for n in numbers:
            val = float(n)
            nodes.append(f"NUM_{val}")
            features.append({'type': 'number', 'value': val, 'polarity': 1.0})
            nums_found.append(val)
        
        # 2. Entity Extraction (Simple noun phrase approximation)
        # Split by common delimiters but keep words
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        stopwords = {'the', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'that', 'this', 'these', 'those', 'it', 'its', 'a', 'an'}
        
        entity_idx = 0
        for w in words:
            if w not in stopwords:
                nodes.append(f"ENT_{w}")
                # Check polarity (negation)
                polarity = 1.0
                if re.search(rf'\b(not|no|never|without)\s+{w}\b', text_lower) or re.search(rf'\b{w}\s+(not|no)\b', text_lower):
                    polarity = -1.0
                
                features.append({'type': 'entity', 'value': 0.0, 'polarity': polarity})
                entity_idx += 1

        # 3. Relation Extraction (Edges)
        # Comparatives
        if '>' in text or 'greater' in text_lower or 'more' in text_lower:
            edges.append(('relation', 'greater_than', 1.0))
        if '<' in text or 'less' in text_lower or 'fewer' in text_lower:
            edges.append(('relation', 'less_than', 1.0))
            
        # Causality
        if 'cause' in text_lower or 'because' in text_lower or 'therefore' in text_lower or 'leads to' in text_lower:
            edges.append(('relation', 'causes', 1.0))
            
        # Conditionals
        if 'if' in text_lower or 'implies' in text_lower:
            edges.append(('relation', 'implies', 1.0))
            
        # Negation global flag
        has_negation = bool(re.search(r'\b(not|no|never)\b', text_lower))
        if has_negation:
             edges.append(('relation', 'negation', 1.0))

        return {
            'nodes': nodes,
            'edges': edges,
            'features': features,
            'raw_counts': Counter(words),
            'has_numbers': len(nums_found) > 0,
            'numbers': nums_found
        }

    def _compute_analogical_reward(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Computes similarity matrix S and solves for soft matching M.
        Reward = trace(M^T S)
        """
        p_nodes = p_struct['nodes']
        c_nodes = c_struct['nodes']
        
        if not p_nodes or not c_nodes:
            return 0.0

        # Build feature vectors (simplified to type + polarity + normalized value)
        def get_vecs(struct):
            vecs = []
            types = []
            for i, f in enumerate(struct['features']):
                # Encode type: entity=0, number=1
                t_val = 0.0 if f['type'] == 'entity' else 1.0
                vecs.append([t_val, f['polarity'], f['value']])
                types.append(f['type'])
            return np.array(vecs), types

        p_vecs, p_types = get_vecs(p_struct)
        c_vecs, c_types = get_vecs(c_struct)

        # Pad if necessary to match dimensions for matrix ops (though Hungarian handles rectangular)
        # Calculate Similarity Matrix S
        # S_ij = exp(-||fi - gj||^2 / sigma^2) * delta(type_i, type_j)
        sigma = 1.0
        S = np.zeros((len(p_vecs), len(c_vecs)))
        
        for i, pv in enumerate(p_vecs):
            for j, cv in enumerate(c_vecs):
                if p_types[i] == c_types[j]:
                    dist_sq = np.sum((pv - cv) ** 2)
                    S[i, j] = np.exp(-dist_sq / (sigma ** 2))
                else:
                    S[i, j] = 0.0

        if S.size == 0:
            return 0.0

        # Soft Matching via Sinkhorn (approximating Hungarian for soft reward)
        M = hungarian_soft(S)
        
        # Reward is the sum of element-wise product of M and S
        reward = np.sum(M * S)
        return reward

    def _compute_prediction_error(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        KL-Divergence between edge type distributions P (prompt) and Q (candidate).
        D_kl(Q || P)
        """
        # Count edge types
        p_edges = [e[1] for e in p_struct['edges']]
        c_edges = [e[1] for e in c_struct['edges']]
        
        # If no edges, assume uniform prior over a small set of possible relations to avoid log(0)
        all_types = ['greater_than', 'less_than', 'causes', 'implies', 'negation', 'none']
        
        p_counts = Counter(p_edges)
        c_counts = Counter(c_edges)
        
        # Add smoothing
        P = np.array([p_counts.get(t, 0) + 1 for t in all_types], dtype=float)
        Q = np.array([c_counts.get(t, 0) + 1 for t in all_types], dtype=float)
        
        # Normalize to distributions
        P = P / P.sum()
        Q = Q / Q.sum()
        
        # KL Divergence: sum(Q * log(Q/P))
        # Add small epsilon to avoid log(0)
        kl = np.sum(Q * np.log((Q + 1e-9) / (P + 1e-9)))
        return kl

    def _compute_entropy(self, p_struct: Dict, c_struct: Dict) -> float:
        """
        Entropy of the matching matrix M.
        """
        p_nodes = p_struct['nodes']
        c_nodes = c_struct['nodes']
        if not p_nodes or not c_nodes:
            return 0.0
            
        # Re-calculate S and M for entropy
        # (In a production system, we'd cache this from the reward step)
        def get_vecs(struct):
            vecs = []
            types = []
            for i, f in enumerate(struct['features']):
                t_val = 0.0 if f['type'] == 'entity' else 1.0
                vecs.append([t_val, f['polarity'], f['value']])
                types.append(f['type'])
            return np.array(vecs), types

        p_vecs, p_types = get_vecs(p_struct)
        c_vecs, c_types = get_vecs(c_struct)
        
        sigma = 1.0
        S = np.zeros((len(p_vecs), len(c_vecs)))
        for i, pv in enumerate(p_vecs):
            for j, cv in enumerate(c_vecs):
                if p_types[i] == c_types[j]:
                    dist_sq = np.sum((pv - cv) ** 2)
                    S[i, j] = np.exp(-dist_sq / (sigma ** 2))
        
        if S.size == 0:
            return 0.0
            
        M = hungarian_soft(S)
        
        # Entropy H = - sum(M_ij * log(M_ij))
        M_flat = M.flatten()
        M_flat = M_flat[M_flat > 1e-9] # Filter zeros
        if len(M_flat) == 0:
            return 0.0
        H = -np.sum(M_flat * np.log(M_flat))
        return H

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt properties.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ['have you stopped', 'have you quit', 'why did', 'why does', 'when did', 'when does']
        if any(t in p_lower for t in presupposition_triggers):
            return 0.2
            
        # 2. Scope/Pronoun ambiguity (Heuristic: "who" questions often imply ambiguity in simple parsers)
        if re.search(r'\bwho\s+(is|was|told|said)\b', p_lower):
            return 0.4 # Lower confidence, but not zero
            
        # 3. False Dichotomy
        if re.search(r'\beither\s+.+\s+or\b', p_lower) and 'else' not in p_lower:
            return 0.5
            
        # 4. Subjectivity
        subjective_terms = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'opinion']
        if any(t in p_lower for t in subjective_terms):
            return 0.3
            
        # 5. Unanswerability (Missing info heuristics)
        if 'cannot be determined' in p_lower or 'insufficient information' in p_lower:
            return 0.9 # The prompt itself admits uncertainty
            
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        
        if len_both == 0: return 0.0
        return (len_both - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)

    def _constructive_computation(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempt to solve math/logic problems directly.
        Returns the computed answer if solvable, else None.
        """
        # Simple arithmetic extraction
        # Pattern: "What is 2 + 2?" or "Calculate 5 * 6"
        match = re.search(r'(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)', prompt)
        if match:
            try:
                n1 = float(match.group(1))
                op = match.group(2)
                n2 = float(match.group(3))
                res = 0
                if op == '+': res = n1 + n2
                elif op == '-': res = n1 - n2
                elif op == '*': res = n1 * n2
                elif op == '/': res = n1 / n2 if n2 != 0 else float('inf')
                
                # Check if candidate contains the result
                if str(res) in candidate or f"{res:.2f}" in candidate or f"{res:.4f}" in candidate:
                    return 1.0 # Perfect match
                else:
                    return 0.0 # Wrong answer
            except:
                pass
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        p_struct = self._parse_structure(prompt)
        results = []
        
        # Meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            c_struct = self._parse_structure(cand)
            
            # 1. Constructive Computation (High priority)
            comp_score = self._constructive_computation(prompt, cand)
            if comp_score is not None:
                # If we computed an answer, trust it heavily, but respect meta_cap slightly
                final_score = comp_score * meta_cap
                results.append({
                    "candidate": cand,
                    "score": final_score,
                    "reasoning": f"Constructive computation yielded {comp_score}. Meta-cap: {meta_cap:.2f}"
                })
                continue

            # 2. Energy-Based Scoring
            R_a = self._compute_analogical_reward(p_struct, c_struct)
            D_kl = self._compute_prediction_error(p_struct, c_struct)
            H = self._compute_entropy(p_struct, c_struct)
            
            # Energy E = D_kl + alpha*H - beta*R_a
            energy = self.gamma * D_kl + self.alpha * H - self.beta * R_a
            
            # Score is negative energy (higher is better)
            raw_score = -energy
            
            # 3. NCD Tiebreaker (Max 15% influence)
            # Normalize NCD to be a similarity (1 - distance)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 
            
            # Combine: Structural (85%) + NCD (15%)
            # Normalize raw_score roughly to 0-1 range for combination? 
            # Instead, let's keep raw_score dominant and add NCD as a small boost
            combined_score = raw_score + ncd_score
            
            # Apply meta-confidence cap
            final_score = min(combined_score, meta_cap)
            
            # If no structural match and low NCD, penalize
            if R_a < 0.5 and ncd_val > 0.8:
                final_score = -10.0 # Strong penalty

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Energy: {energy:.2f} (KL: {D_kl:.2f}, Ent: {H:.2f}, Rew: {R_a:.2f}). Meta-cap: {meta_cap:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(answer)
        
        # If no numbers in prompt but answer has numbers, or vice versa, might be low confidence
        # unless it's a math problem.
        if not p_struct['has_numbers'] and c_struct['has_numbers']:
             # Heuristic: if prompt isn't asking for math, random numbers are suspicious
             if not re.search(r'calculate|sum|total|difference|product', prompt.lower()):
                 meta_cap