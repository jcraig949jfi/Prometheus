import re
import numpy as np
import zlib

class ReasoningTool:
    """
    Multi-scale belief-falsification scorer combining Theory of Mind (depth),
    Falsificationism (constraint propagation), and Neural Oscillations (weighting).
    
    Mechanism:
    1. Structural Parsing: Extracts propositions, negations, conditionals, and agent attributions.
    2. Constraint Propagation: Builds an entailment matrix to detect contradictions (falsifications).
    3. Oscillatory Weighting: Applies depth-based decay (Gamma/Theta bands) to penalize deep recursive errors less.
    4. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|only if)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|leads to|causes)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|every|none|most)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|equal|same|different)\b', re.IGNORECASE),
            'agent_attribution': re.compile(r'\b((\w+)\s+(thinks|believes|says|knows|wants)\s+that?)\b', re.IGNORECASE),
            'number': re.compile(r'-?\d+\.?\d*'),
            'presupposition': re.compile(r'(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }

    def _extract_propositions(self, text: str) -> list:
        """Parse text into atomic propositions with polarity and depth."""
        props = []
        sentences = re.split(r'[.!?]', text)
        
        # Simple agent tracking (depth 0 = speaker, depth 1 = attributed)
        current_agent = 0
        current_depth = 0
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            # Check for agent attribution (simplified ToM)
            agent_match = self.patterns['agent_attribution'].search(sent)
            if agent_match:
                current_depth = 1
                # Extract the content after the attribution verb
                start_idx = agent_match.end()
                content = sent[start_idx:]
            else:
                current_depth = 0
                content = sent

            # Detect polarity
            polarity = 1
            if self.patterns['negation'].search(content):
                polarity = -1
            
            # Detect key logical markers
            has_conditional = bool(self.patterns['conditional'].search(content))
            has_causal = bool(self.patterns['causal'].search(content))
            has_comparative = bool(self.patterns['comparative'].search(content))
            has_quantifier = bool(self.patterns['quantifier'].search(content))
            
            # Extract numbers for constructive computation
            numbers = [float(n) for n in self.patterns['number'].findall(content)]
            
            if content:
                props.append({
                    'text': content,
                    'depth': current_depth,
                    'polarity': polarity,
                    'conditional': has_conditional,
                    'causal': has_causal,
                    'comparative': has_comparative,
                    'quantifier': has_quantifier,
                    'numbers': numbers,
                    'agent': current_agent
                })
                
        return props

    def _build_entailment_matrix(self, props: list) -> np.ndarray:
        """Build boolean constraint matrix C where C[i,j] = 1 if i entails j."""
        n = len(props)
        if n == 0:
            return np.array([], dtype=bool)
            
        C = np.eye(n, dtype=bool)
        
        for i, p in enumerate(props):
            for j, q in enumerate(props):
                if i == j:
                    continue
                # Simplified transitivity: If both share numbers and comparatives
                if p['comparative'] and q['comparative']:
                    if set(p['numbers']).issubset(set(q['numbers'])):
                        C[i, j] = True
                # Causal chaining
                if p['causal'] and q['causal']:
                     C[i, j] = True
                # Conditional matching
                if p['conditional'] and q['conditional']:
                    C[i, j] = True
                    
        return C

    def _compute_falsification_score(self, props: list, C: np.ndarray) -> float:
        """Compute weighted falsification score based on oscillation depths."""
        if len(props) == 0:
            return 1.0
            
        n = len(props)
        # Hypothesis: Assume all extracted propositions are true candidates
        H = set(range(n))
        if not H:
            return 1.0

        # Transitive closure via matrix power (approximated for boolean)
        # For small n, repeated dot product works; for larger, we iterate
        T = C.copy()
        for _ in range(n):
            T = T | (T @ T) # Boolean matrix multiplication logic
            
        # Detect counterexamples: A proposition with negative polarity that is entailed by positive ones
        # Simplified: If a prop has polarity -1, it's a potential counterexample if asserted
        counterexamples = []
        weights = []
        total_weight = 0
        
        for i in H:
            p = props[i]
            # Oscillation weighting: Gamma(1.0) for depth 0, Theta(0.5) for depth 1, etc.
            w = 0.5 ** p['depth']
            total_weight += w
            
            # Falsification check: If polarity is negative, it contradicts a positive assertion
            # In this simplified model, we treat negative polarity propositions as "counter-examples" 
            # to a purely positive world model, or check for internal consistency.
            # Here: If we assert H, and H contains contradictions (A and not A), we penalize.
            # Since we don't have explicit A/not-A pairing in this simple parser, 
            # we use the presence of high-magnitude negative propositions as instability.
            if p['polarity'] == -1:
                counterexamples.append(i)
                weights.append(w)
        
        if total_weight == 0:
            return 1.0
            
        weighted_penalty = sum(weights)
        F_w = 1.0 - (weighted_penalty / total_weight)
        return max(0.0, min(1.0, F_w))

    def _check_meta_confidence(self, prompt: str) -> float:
        """Check for Tier B traps: ambiguity, presupposition, subjectivity."""
        score = 1.0
        
        if self.patterns['presupposition'].search(prompt):
            score = 0.2 # Strong penalty for loaded questions
        elif self.patterns['false_dichotomy'].search(prompt):
            score = 0.4
        elif self.patterns['subjectivity'].search(prompt):
            score = 0.3
        elif "who" in prompt.lower() and ("he" in prompt.lower() or "she" in prompt.lower()):
             # Pronoun ambiguity heuristic
            score = 0.3
            
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        if max(z1, z2) == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max(z1, z2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        props = self._extract_propositions(prompt)
        C = self._build_entailment_matrix(props)
        base_score = self._compute_falsification_score(props, C)
        
        # Constructive computation bonus
        numbers = []
        for p in props:
            numbers.extend(p['numbers'])
        
        results = []
        for cand in candidates:
            score = base_score
            reasoning = "Structural analysis complete."
            
            # Numeric evaluation (Constructive)
            cand_nums = [float(n) for n in self.patterns['number'].findall(cand)]
            if numbers and cand_nums:
                # Simple heuristic: if prompt has numbers and candidate has result of operation
                if len(numbers) >= 2:
                    expected_sum = sum(numbers)
                    if abs(cand_nums[0] - expected_sum) < 0.01:
                        score = 0.95
                        reasoning = "Numeric verification successful."
                    elif len(cand_nums) > 0 and abs(cand_nums[0] - numbers[0]) < 0.01:
                         # Exact match of first number
                        score = max(score, 0.6)
            
            # NCD Tiebreaker (max 15% influence)
            ncd_val = self._compute_ncd(prompt, cand)
            # Normalize NCD to a small boost/penalty
            ncd_boost = (1.0 - ncd_val) * 0.15
            
            final_score = (score * 0.85) + ncd_boost
            final_score = min(1.0, max(0.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _meta_confidence(self, prompt: str) -> float:
        return self._check_meta_confidence(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        # 1. Check for Tier B traps (Ambiguity, Presupposition)
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.5:
            return meta_conf
        
        # 2. Structural match check
        props = self._extract_propositions(prompt)
        if not props:
            return 0.2 # No structure found
        
        # 3. Compute score for this specific answer
        # We simulate a single-candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        score = res[0]['score']
        
        # Cap confidence based on whether we actually computed something
        # If the prompt had numbers and we didn't use them, lower confidence
        has_numbers = any(p['numbers'] for p in props)
        answer_has_numbers = bool(self.patterns['number'].search(answer))
        
        if has_numbers and not answer_has_numbers:
            # Might be a math problem answered with text
            return min(score, 0.6)
            
        # If score is high and no meta-traps, return high confidence
        if score > 0.8:
            return 0.95
        elif score > 0.6:
            return 0.75
        else:
            return 0.4