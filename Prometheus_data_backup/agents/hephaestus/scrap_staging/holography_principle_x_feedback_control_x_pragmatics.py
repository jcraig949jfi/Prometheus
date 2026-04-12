import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning evaluator combining Holographic Principle (boundary extraction),
    Feedback Control (PID weight adaptation), and Pragmatics (Gricean maxims).
    
    Mechanism:
    1. Parsing: Extracts atomic propositions (negations, relations, causals) via regex.
    2. Holographic Bulk: Constructs adjacency matrices and computes transitive closure
       to infer implicit constraints (bulk information) from explicit boundaries.
    3. Feedback Control: Calculates error between candidate and reference closures,
       using a discrete PID controller to dynamically weight feature importance.
    4. Pragmatics: Scores based on Quantity, Relation, and Manner heuristics.
    5. Epistemic Honesty: Detects ambiguity/traps to cap confidence appropriately.
    """

    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05
        
        # State for PID
        self._integral = 0.0
        self._prev_error = 0.0
        self._dt = 1.0
        
        # Weights (Negation, Relational, Pragmatic) - initialized equal
        self.weights = np.array([0.33, 0.33, 0.34])
        
        # Regex Patterns
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|nor|without)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|because|therefore|thus|since)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.I),
            'numeric': re.compile(r'-?\d+\.?\d*')
        }
        
        # Trap indicators for Tier B
        self.trap_patterns = [
            re.compile(r'\b(stopped|quit|failed)\s+(you|he|she|it)\b', re.I), # Presupposition
            re.compile(r'\bevery\s+\w+\s+...\s+a\s+\w+\b', re.I), # Scope (simplified)
            re.compile(r'\b(either\s+\w+\s+or\s+\w+)\b', re.I), # False dichotomy
            re.compile(r'\b(best|worst|favorite|opinion)\b', re.I), # Subjectivity
            re.compile(r'\b(who|he|she|him|her)\s+was\s+it\b', re.I), # Pronoun ambiguity
            re.compile(r'\bwhy\s+did\s+\w+\s+(fail|stop)\b', re.I) # Presupposition
        ]

    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities (nouns/proper nouns) as boundaries."""
        # Simple heuristic: Capitalized words or quoted strings
        entities = set()
        entities.update(re.findall(r'\b[A-Z][a-z]+\b', text))
        entities.update(re.findall(r'"([^"]+)"', text))
        entities.update(re.findall(r"'([^']+)'", text))
        # Fallback to numeric values as entities
        entities.update(self.patterns['numeric'].findall(text))
        return list(entities) if entities else ["entity"]

    def _parse_propositions(self, text: str) -> List[Tuple]:
        """Parse text into atomic propositions (subject, predicate, object, polarity, type)."""
        props = []
        lower_text = text.lower()
        entities = self._extract_entities(text)
        n_ents = len(entities)
        if n_ents == 0: entities = ["entity"]
        
        # Check global polarity
        has_neg = bool(self.patterns['negation'].search(text))
        
        # Type detection
        p_type = 'statement'
        if self.patterns['comparative'].search(text): p_type = 'comparative'
        elif self.patterns['causal'].search(text): p_type = 'causal'
        elif self.patterns['conditional'].search(text): p_type = 'conditional'
        
        # Generate synthetic relations based on detected types to populate matrix
        # In a full system, this would be strict linguistic parsing. 
        # Here we simulate the "Holographic Boundary" by mapping detected features to entity pairs.
        for i, sub in enumerate(entities):
            for j, obj in enumerate(entities):
                if i != j:
                    # If text contains comparative cues, assume ordered relation
                    if p_type == 'comparative':
                        props.append((sub, '>', obj, not has_neg, p_type))
                    elif p_type == 'causal':
                        props.append((sub, 'causes', obj, not has_neg, p_type))
                    else:
                        props.append((sub, 'is', obj, not has_neg, p_type))
                        
        # If no specific entities found but text exists, create a self-relation
        if not props and text.strip():
            props.append(("self", "is", "self", not has_neg, p_type))
            
        return props

    def _build_closure(self, props: List[Tuple], entities: List[str]) -> np.ndarray:
        """Build adjacency matrix and compute transitive closure (Bulk Inference)."""
        n = len(entities)
        if n == 0: return np.zeros((1,1))
        
        # Map entities to indices
        e_map = {e: i for i, e in enumerate(entities)}
        A = np.zeros((n, n), dtype=bool)
        
        for sub, pred, obj, polarity, p_type in props:
            if sub in e_map and obj in e_map:
                if polarity: # Only map if positive assertion
                    A[e_map[sub], e_map[obj]] = True
        
        # Transitive Closure (Warshall's algorithm simplified for boolean)
        reach = A.copy()
        # Approximate log2(n) iterations for speed, or fixed small number for small n
        steps = max(1, int(np.ceil(np.log2(max(n, 2)))))
        
        for _ in range(steps):
            # Boolean matrix multiplication: reach = reach OR (reach dot reach)
            # Using numpy broadcasting for logical_and then reducing
            step_matrix = np.logical_and(reach[:, :, None], reach[None, :, :])
            reach = np.logical_or(reach, np.any(step_matrix, axis=1))
            
        return reach

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        if l1 + l2 == 0: return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def _pragmatic_score(self, prompt: str, answer: str) -> float:
        """Compute Gricean pragmatic heuristics."""
        p_len = len(prompt.split())
        a_len = len(answer.split())
        
        # Quantity: Ratio of info density (penalize extreme verbosity or brevity)
        qty_ratio = a_len / (p_len + 1)
        quantity = 1.0 / (1.0 + abs(qty_ratio - 1.0)) # Peak at 1:1 ratio
        
        # Relation: Overlap of key terms (simple intersection)
        p_words = set(re.findall(r'\w+', prompt.lower()))
        a_words = set(re.findall(r'\w+', answer.lower()))
        intersection = len(p_words & a_words)
        relation = intersection / (len(p_words) + 1)
        
        # Manner: Uniformity (inverse variance of sentence length)
        sentences = [len(s.split()) for s in re.split(r'[.!?]', answer) if s.strip()]
        if len(sentences) > 1:
            variance = np.var(sentences)
            manner = 1.0 / (1.0 + variance)
        else:
            manner = 1.0
            
        return (0.33 * quantity) + (0.33 * relation) + (0.34 * manner)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity, presuppositions, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # Check for trap patterns
        for pattern in self.trap_patterns:
            if pattern.search(p_lower):
                return 0.25 # High uncertainty due to potential trap
        
        # Check for lack of structural content
        if len(re.findall(r'\w+', prompt)) < 3:
            return 0.2
            
        return 1.0 # No obvious traps detected

    def _compute_numeric_answer(self, prompt: str) -> float:
        """Attempt to constructively solve math problems in the prompt."""
        # Very basic extractor for "X + Y", "X - Y", "X * Y", "X / Y"
        ops = [
            (r'(\d+)\s*\+\s*(\d+)', lambda x,y: x+y),
            (r'(\d+)\s*-\s*(\d+)', lambda x,y: x-y),
            (r'(\d+)\s*\*\s*(\d+)', lambda x,y: x*y),
            (r'(\d+)\s*/\s*(\d+)', lambda x,y: x/y),
        ]
        for pat, func in ops:
            m = re.search(pat, prompt)
            if m:
                return func(float(m.group(1)), float(m.group(2)))
        return None

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        entities = self._extract_entities(prompt + " " + " ".join(candidates))
        ref_props = self._parse_propositions(prompt)
        ref_closure = self._build_closure(ref_props, entities)
        
        # Compute reference pragmatic score (idealized)
        # We assume the prompt itself or a hypothetical perfect answer has max pragmatics
        # For this implementation, we compare candidates relative to each other and the prompt
        
        best_score = -np.inf
        scores = []
        
        # Pre-calculate numeric target if exists
        numeric_target = self._compute_numeric_answer(prompt)

        for cand in candidates:
            # 1. Structural Parsing & Holographic Closure
            cand_props = self._parse_propositions(cand)
            cand_closure = self._build_closure(cand_props, entities)
            
            # Ensure shapes match for comparison (pad if necessary, though logic above tries to align)
            min_dim = min(ref_closure.shape[0], cand_closure.shape[0])
            if min_dim == 0: min_dim = 1
            
            # Truncate or pad to common size for comparison
            r_sub = ref_closure[:min_dim, :min_dim]
            c_sub = cand_closure[:min_dim, :min_dim]
            
            # 2. Error Signal (Feedback Control)
            # Element-wise XOR to find mismatches
            E = np.logical_xor(r_sub, c_sub).astype(float)
            error = E.mean() if E.size > 0 else 1.0
            
            # PID Update (simulated per candidate evaluation step)
            self._integral += error * self._dt
            derivative = (error - self._prev_error) / self._dt if self._dt > 0 else 0
            self._prev_error = error
            
            # Adjust weights (projected onto simplex roughly by normalization)
            delta = -self.Kp*error - self.Ki*self._integral - self.Kd*derivative
            self.weights += delta * np.array([0.5, 0.3, 0.2]) # Bias towards structure
            self.weights = np.maximum(self.weights, 0.01) # Prevent negative weights
            self.weights /= self.weights.sum() # Normalize to sum=1
            
            # 3. Pragmatic Layer
            prag = self._pragmatic_score(prompt, cand)
            
            # 4. Final Score Composition
            # Decomposition: Structural (1-error) + Computation + NCD
            struct_score = 1.0 - error
            
            # Computation Score (if numeric)
            comp_score = 0.0
            if numeric_target is not None:
                try:
                    # Try to extract number from candidate
                    cand_nums = re.findall(r'-?\d+\.?\d*', cand)
                    if cand_nums:
                        val = float(cand_nums[-1])
                        diff = abs(val - numeric_target)
                        comp_score = 1.0 / (1.0 + diff) # High score if close
                    else:
                        comp_score = 0.0
                except:
                    comp_score = 0.0
            
            # NCD Score (Tiebreaker, max 15% influence)
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted Sum
            # Weights: w_neg (mapped to struct), w_rel (mapped to comp), w_prag
            # Mapping PID weights to our components:
            # w[0] -> Structure, w[1] -> Computation, w[2] -> Pragmatics/NCD mix
            
            final_score = (
                self.weights[0] * struct_score +
                self.weights[1] * (comp_score if numeric_target else struct_score) +
                self.weights[2] * ((0.8 * prag) + (0.2 * ncd_score))
            )
            
            # NCD cap: NCD should not exceed 15% of total influence effectively
            # By keeping ncd_score weight low in the formula above, we satisfy this.
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, Comp: {comp_score:.2f}, Prag: {prag:.2f}"
            })
            
            if final_score > best_score:
                best_score = final_score

        # Sort descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 for ambiguous/trap prompts.
        Caps at 0.9 unless computation is definitive.
        """
        # Tier B: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap # Return low confidence for traps
        
        # Evaluate structural alignment
        entities = self._extract_entities(prompt + " " + answer)
        ref_closure = self._build_closure(self._parse_propositions(prompt), entities)
        cand_closure = self._build_closure(self._parse_propositions(answer), entities)
        
        min_dim = min(ref_closure.shape[0], cand_closure.shape[0])
        if min_dim == 0: 
            base_conf = 0.2 # Low confidence if no structure found
        else:
            r_sub = ref_closure[:min_dim, :min_dim]
            c_sub = cand_closure[:min_dim, :min_dim]
            error = np.logical_xor(r_sub, c_sub).mean()
            base_conf = 1.0 - error
            
        # Check for definitive computation
        numeric_target = self._compute_numeric_answer(prompt)
        is_definitive = False
        if numeric_target is not None:
            try:
                cand_nums = re.findall(r'-?\d+\.?\d*', answer)
                if cand_nums and abs(float(cand_nums[-1]) - numeric_target) < 1e-6:
                    is_definitive = True
            except: pass
            
        final_conf = base_conf
        
        # Cap logic
        if not is_definitive:
            final_conf = min(final_conf, 0.9)
            
        # Apply meta cap (Tier B)
        final_conf = min(final_conf, meta_cap)
        
        return max(0.0, min(1.0, final_conf))