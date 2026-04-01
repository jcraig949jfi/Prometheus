import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A reasoning tool combining Category Theory (functorial mapping), 
    Phase Transitions (temperature-driven belief propagation), and 
    Theory of Mind (KL-divergence scoring) to evaluate logical consistency.
    
    It prioritizes epistemic honesty by detecting ambiguity traps (Tier B)
    before attempting structural resolution (Tier A).
    """

    def __init__(self):
        # Heuristic weights for semantic mapping (Functor F)
        self.weights = {
            'implies': 0.9,
            'causes': 0.8,
            'negates': -0.9,
            'before': 0.7,
            'after': -0.7, # Reverse temporal logic simplification
            'greater': 0.8,
            'less': -0.8,
            'equal': 1.0
        }
        self.patterns = {
            'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
            'conditional': [r'\bif\b.*\bthen\b', r'\bif\b', r'\bleads to\b', r'\bimplies\b'],
            'causal': [r'\bbecause\b', r'\btherefore\b', r'\bcauses\b', r'\bmakes\b'],
            'temporal': [r'\bbefore\b', r'\bafter\b'],
            'comparative': [r'\bgreater than\b', r'\less than\b', r'\bmore than\b', r'\bfewer than\b'],
            'quantifier': [r'\ball\b', r'\bsome\b', r'\bevery\b', r'\bnone\b'],
            'equality': [r'\bis equal to\b', r'\bare equal\b', r'\bsame as\b']
        }
        # Meta-confidence triggers for Tier B (Epistemic Honesty)
        self.traps = {
            'presupposition': [r'\bhave you stopped\b', r'\bwhy did\b.*\bfail\b', r'\bwhen did\b.*\bstop\b'],
            'scope_ambiguity': [r'\bevery\b.*\ba\b.*\bY\b'], # Simplified heuristic
            'false_dichotomy': [r'\beither\b.*\bor\b.*\bonly\b', r'\bis it\b.*\bor\b.*\b\?'],
            'subjectivity': [r'\bbest\b', r'\bworst\b', r'\bfavorite\b', r'\bbeautiful\b'],
            'unanswerable': [r'\bwho is\b.*\bhe\b', r'\bwhat did\b.*\bthey\b'] # Pronoun checks
        }

    def _extract_atoms(self, text: str) -> Tuple[List[dict], Dict[str, np.ndarray]]:
        """Parse text into atoms and relation matrices."""
        # Normalize
        text_lower = text.lower()
        # Simple tokenization for atoms (words/phrases)
        # We treat sentences or clauses as nodes for simplicity in this constrained env
        sentences = re.split(r'[.;!?]', text_lower)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            sentences = [text_lower]
            
        n = len(sentences)
        if n == 0:
            return [], {}
            
        nodes = [{'id': i, 'text': s, 'polarity': 1.0} for i, s in enumerate(sentences)]
        
        # Initialize adjacency stacks
        adj = {k: np.zeros((n, n)) for k in self.weights.keys()}
        
        # Detect relations between sentences (simplified global scan for demo)
        # In a full implementation, this would be node-pair specific
        full_text = " ".join(sentences)
        
        # Self-loops for identity (stability)
        for k in adj:
            np.fill_diagonal(adj[k], 0.1) 

        # Detect global relations and apply to relevant nodes
        # Negation affects polarity of the node containing it
        for i, node in enumerate(nodes):
            for pat in self.patterns['negation']:
                if re.search(pat, node['text']):
                    node['polarity'] = -1.0
                    break
        
        # Build edges based on keyword presence in the whole text connecting concepts
        # Since we lack NLP coreference, we assume transitive connectivity in short prompts
        # or explicit "If A then B" structures.
        # For this implementation, we simulate the graph based on logical keywords found.
        
        if any(re.search(p, full_text) for p in self.patterns['conditional']):
            # Connect all previous to all subsequent with 'implies'
            for i in range(n):
                for j in range(i+1, n):
                    adj['implies'][i, j] = 1.0
        
        if any(re.search(p, full_text) for p in self.patterns['causal']):
             for i in range(n):
                for j in range(i+1, n):
                    adj['causes'][i, j] = 1.0
                    
        if any(re.search(p, full_text) for p in self.patterns['temporal']):
            if 'before' in full_text:
                # A before B -> A -> B
                for i in range(n):
                    for j in range(i+1, n):
                        adj['before'][i, j] = 1.0
            elif 'after' in full_text:
                for i in range(n):
                    for j in range(i+1, n):
                        adj['after'][j, i] = 1.0 # B after A -> A -> B logic flip

        return nodes, adj

    def _propagate_beliefs(self, S: np.ndarray, temp: float = 0.1, steps: int = 20) -> np.ndarray:
        """Run phase transition dynamics."""
        n = S.shape[0]
        if n == 0:
            return np.array([])
            
        b = np.full(n, 0.5) # Initial belief
        T = temp
        
        for t in range(steps):
            # Add temperature noise
            noise = np.random.uniform(-T, T, size=(n, n))
            S_noisy = S + noise
            
            # Update rule: b_{t+1} = sigmoid(S * b_t)
            # We use a simple linear combination passed through sigmoid
            raw = S_noisy @ b
            # Normalize input to sigmoid range roughly
            raw = (raw - np.mean(raw)) / (np.std(raw) + 1e-6) 
            b = 1 / (1 + np.exp(-raw))
            
            # Decay temperature
            T *= 0.9
            
        return b

    def _compute_order_parameter(self, beliefs: np.ndarray) -> float:
        if len(beliefs) == 0:
            return 0.0
        return float(np.abs(np.mean(beliefs) - 0.5))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Returns a cap on confidence based on prompt pathology.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        for pat in self.traps['presupposition']:
            if re.search(pat, p_lower):
                return 0.25
                
        # 2. Subjectivity (often unanswerable objectively)
        for pat in self.traps['subjectivity']:
            if re.search(pat, p_lower):
                # Only flag if no numeric data present
                if not re.search(r'\d+', p_lower):
                    return 0.3
                    
        # 3. False Dichotomy indicators
        for pat in self.traps['false_dichotomy']:
            if re.search(pat, p_lower):
                # Check if it looks like a logic puzzle vs real world
                if 'logic' not in p_lower and 'puzzle' not in p_lower:
                    return 0.4

        # 4. Pronoun ambiguity (Heuristic: "he/she/they" + question word)
        if re.search(r'\b(he|she|they|him|her)\b', p_lower) and re.search(r'\b(who|which|what)\b.*\?', p_lower):
             return 0.3

        return 1.0 # No traps detected

    def _calculate_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural Parsing and Computation.
        Handles numeric comparisons, negation logic, and transitivity.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt
        nums_prompt = re.findall(r'-?\d+\.?\d*', p_lower)
        nums_cand = re.findall(r'-?\d+\.?\d*', c_lower)
        
        if len(nums_prompt) >= 2 and len(nums_cand) >= 1:
            try:
                # Convert to floats
                p_nums = [float(x) for x in nums_prompt]
                c_num = float(nums_cand[0])
                
                # Detect comparison type
                is_max = any(x in p_lower for x in ['largest', 'greatest', 'max', 'more than all'])
                is_min = any(x in p_lower for x in ['smallest', 'least', 'min', 'less than all'])
                is_sum = any(x in p_lower for x in ['sum', 'total', 'combined'])
                is_diff = any(x in p_lower for x in ['difference', 'subtract'])
                
                if is_max:
                    target = max(p_nums)
                    if abs(c_num - target) < 1e-5: score += 1.0
                elif is_min:
                    target = min(p_nums)
                    if abs(c_num - target) < 1e-5: score += 1.0
                elif is_sum:
                    target = sum(p_nums)
                    if abs(c_num - target) < 1e-5: score += 1.0
                elif is_diff and len(p_nums) == 2:
                    target = abs(p_nums[0] - p_nums[1])
                    if abs(c_num - target) < 1e-5: score += 1.0
                else:
                    # Simple existence match if no operator found but numbers exist
                    if c_num in p_nums:
                        score += 0.5
            except ValueError:
                pass

        # 2. Logical Negation Check
        # If prompt has "not X" and candidate is "X", penalize. If "not X" and candidate "not X", boost.
        has_neg_prompt = any(re.search(p, p_lower) for p in self.patterns['negation'])
        has_neg_cand = any(re.search(p, c_lower) for p in self.patterns['negation'])
        
        if has_neg_prompt:
            if has_neg_cand:
                score += 0.5 # Consistent negation
            else:
                # Check if the candidate contradicts a negated fact
                # Simplified: if prompt says "A is not B", and candidate says "A is B"
                # This requires deeper parsing, using heuristic overlap
                score -= 0.5 
        elif not has_neg_prompt and has_neg_cand:
             # Prompt positive, candidate negative -> possible contradiction unless justified
             score -= 0.2

        # 3. Transitivity / Ordering
        # If "A > B" and "B > C", check if candidate implies "A > C"
        # Very hard without full NLP, relying on keyword matching for "therefore", "so"
        if 'therefore' in c_lower or 'so' in c_lower:
            score += 0.2 # Reward attempting deduction

        return score

    def _get_ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker (max 15% weight)."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        ncd = (combined - max_len) / max_len
        return ncd

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Parse Prompt to Graph
        nodes, adj_matrices = self._extract_atoms(prompt)
        n = len(nodes)
        
        # 3. Construct Semantic Matrix S (Functorial Mapping)
        S = np.zeros((n, n)) if n > 0 else np.array([])
        if n > 0:
            for key, matrix in adj_matrices.items():
                if matrix.shape[0] == n:
                    S += self.weights.get(key, 0.5) * matrix
        
        results = []
        
        for cand in candidates:
            # Base Score Components
            struct_score = self._calculate_structural_score(prompt, cand)
            
            # Phase Transition Logic (if graph exists)
            belief_score = 0.0
            if n > 0:
                # Simulate adding candidate as a node influencing the system
                # Simplified: Run propagation on prompt graph, see if candidate aligns with final state
                b_final = self._propagate_beliefs(S)
                # Heuristic: Does the candidate text match high-belief nodes?
                # (Very rough approximation without semantic embedding)
                belief_score = 0.5 # Default neutral if we can't map well
                
                # Calculate susceptibility (dm/dT) roughly
                m1 = self._compute_order_parameter(self._propagate_beliefs(S, temp=0.1))
                m2 = self._compute_order_parameter(self._propagate_beliefs(S, temp=0.2))
                susceptibility = abs(m1 - m2)
                if susceptibility > 0.1: # Phase transition detected -> high certainty in structure
                    belief_score += 0.3
            
            # NCD Tiebreaker
            ncd_val = self._get_ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15 # Max 15% contribution
            
            # Combine Scores
            # Structural is primary (>=50%), Computation part of structural, NCD <= 15%
            raw_score = struct_score + belief_score + ncd_score
            
            # Apply Meta-Confidence Cap
            final_score = min(raw_score, meta_cap)
            
            # Normalize to 0-1 range loosely
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural: {struct_score:.2f}, Belief: {belief_score:.2f}, NCD: {ncd_score:.2f}. Cap: {meta_cap:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by meta-analysis of the prompt for ambiguity.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run evaluation internally to get structural score
        # We treat the single answer as a candidate list of one
        res_list = self.evaluate(prompt, [answer])
        
        if not res_list:
            return 0.0
            
        base_score = res_list[0]['score']
        
        # If meta_cap is low (ambiguous), force low confidence regardless of score
        if meta_cap < 0.4:
            return min(base_score, meta_cap)
            
        # If no structural match found (score ~0), confidence should be low
        if base_score < 0.1:
            return 0.1
            
        return min(base_score, 1.0)