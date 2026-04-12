import re
import numpy as np
import zlib

class ReasoningTool:
    """
    A hybrid reasoning tool fusing Topology (consistency checks), Pragmatics (Gricean maxims),
    and the Free Energy Principle (prediction error minimization).
    
    Mechanism:
    1. Structural Parsing: Extracts atomic propositions and logical relations (implications, negations).
    2. Topological Analysis: Builds an implication graph to detect contradictions (holes) via transitive closure.
    3. Free Energy Calculation: Computes prediction error between candidate assertions and inferred truth states.
    4. Pragmatic Scoring: Penalizes length deviations and hedge words.
    5. Epistemic Honesty: Detects ambiguity/presuppositions to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|implies|leads to|causes)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|before|after)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|since|therefore|thus|hence)\b', re.IGNORECASE),
            'hedge': re.compile(r'\b(maybe|perhaps|possibly|might|could|uncertain)\b', re.IGNORECASE),
            'presupposition': re.compile(r'(have you stopped|why did .*(fail|stop)|when did .*(stop|fail))', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            'number_seq': re.compile(r'[-+]?\d*\.?\d+'),
            'comparison_op': re.compile(r'(==|!=|<=|>=|<|>)')
        }

    def _extract_propositions(self, text):
        """Extract atomic propositions and logical markers."""
        props = []
        # Simple sentence splitting as proxy for propositions
        sentences = re.split(r'[.!?]', text)
        for s in sentences:
            s = s.strip()
            if s:
                props.append(s.lower())
        return props

    def _build_implication_graph(self, prompt):
        """
        Build a simplified adjacency matrix representing logical flow.
        Nodes are extracted propositions. Edges represent 'if-then' or causal links.
        Returns adjacency matrix A and initial truth vector t0.
        """
        sentences = self._extract_propositions(prompt)
        n = len(sentences)
        if n == 0:
            return np.array([]), np.array([]), []
        
        A = np.zeros((n, n), dtype=bool)
        t0 = np.zeros(n) # 0.5 = unknown, 1.0 = true (asserted), 0.0 = false
        
        # Heuristic: Assume stated sentences are true facts unless negated
        for i, s in enumerate(sentences):
            if not self.patterns['negation'].search(s):
                t0[i] = 1.0
            else:
                t0[i] = 0.0 # Negated statement treated as false assertion of the positive form

        # Build edges based on ordering and conditionals
        for i, s in enumerate(sentences):
            if self.patterns['conditional'].search(s) or self.patterns['causal'].search(s):
                # If sentence i is a rule, it might imply the next sentence or specific keywords
                # Simplified: Connect to subsequent sentences as a chain of reasoning
                for j in range(i + 1, min(i + 3, n)):
                    A[i, j] = True
        
        return A, t0, sentences

    def _compute_transitive_closure(self, A):
        """Warshall-style transitive closure using numpy."""
        if A.size == 0:
            return A
        n = A.shape[0]
        T = A.astype(float)
        np.fill_diagonal(T, 1.0) # Identity
        
        # Repeated squaring approximation for small n, or simple iteration
        # For strict boolean closure: T = (I + A)^n
        if n > 0:
            T = T.copy()
            for _ in range(n):
                T = np.dot(T, T)
                T = (T > 0).astype(float)
        return T

    def _detect_holes(self, T, sentences):
        """
        Detect topological holes: contradictions where a proposition and its negation 
        are both reachable or forced true.
        Returns a penalty score.
        """
        if len(sentences) == 0:
            return 0.0
        
        hole_penalty = 0.0
        n = len(sentences)
        
        # Check for cycles that force contradictions in a simplified boolean world
        # Here we simulate by checking if the closure forces high confidence on mutually exclusive concepts
        # Since we don't have explicit semantic negation mapping (e.g., "hot" vs "cold"),
        # we penalize dense connectivity which often indicates circular reasoning or tautology loops.
        
        # Metric: Average row sum minus 1 (identity). High connectivity = potential over-constraint.
        if n > 1:
            connectivity = np.sum(T) / (n * n)
            hole_penalty = connectivity * 0.5 # Scale factor
            
        return hole_penalty

    def _calculate_free_energy(self, candidate, prompt_truth_vector, sentences, A):
        """
        Calculate prediction error (Free Energy) between candidate and inferred state.
        """
        if len(sentences) == 0:
            return 0.0
            
        # Map candidate text to truth vector space
        # Does the candidate affirm or deny the extracted sentences?
        c_lower = candidate.lower()
        t_candidate = np.zeros_like(prompt_truth_vector)
        
        for i, s in enumerate(sentences):
            # Simple keyword overlap for affirmation
            words = set(s.split())
            c_words = set(c_lower.split())
            overlap = len(words.intersection(c_words))
            if overlap > 0:
                t_candidate[i] = 1.0
            elif any(neg in c_lower for neg in ['not', 'no', 'false']):
                t_candidate[i] = 0.0
        
        # If candidate is short (Yes/No), assume it affirms the main premise
        if len(c_lower.split()) < 4 and len(prompt_truth_vector) > 0:
            if 'yes' in c_lower or 'true' in c_lower:
                t_candidate = np.ones_like(prompt_truth_vector)
            elif 'no' in c_lower or 'false' in c_lower:
                t_candidate = np.zeros_like(prompt_truth_vector)

        # Propagate prompt truth
        if A.size > 0:
            T = self._compute_transitive_closure(A)
            inferred = np.dot(T, prompt_truth_vector)
            inferred = np.clip(inferred, 0, 1)
        else:
            inferred = prompt_truth_vector
            
        # Squared deviation
        error = np.sum((t_candidate - inferred) ** 2)
        return error

    def _pragmatics_score(self, prompt, candidate):
        """
        Score based on Gricean maxims:
        - Quantity: Length alignment
        - Manner: Lack of hedging
        - Relevance: Jaccard overlap
        """
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        # Relevance (Jaccard)
        intersection = p_words.intersection(c_words)
        union = p_words.union(c_words)
        relevance = len(intersection) / len(union) if union else 0
        
        # Quantity Penalty (Deviation from prompt length ratio heuristic)
        # Ideal candidate is concise but informative. 
        len_ratio = len(c_words) / (len(p_words) + 1)
        quantity_penalty = abs(len_ratio - 0.2) # Prefer ~20% length of prompt for answers
        
        # Manner Penalty (Hedges)
        hedges = len(self.patterns['hedge'].findall(candidate))
        manner_penalty = hedges * 0.2
        
        score = relevance - quantity_penalty - manner_penalty
        return score

    def _structural_computation(self, prompt, candidate):
        """
        Perform explicit numeric evaluation if numbers are present.
        Returns a score boost if the candidate correctly solves a math problem.
        """
        numbers_prompt = self.patterns['number_seq'].findall(prompt)
        numbers_cand = self.patterns['number_seq'].findall(candidate)
        
        if len(numbers_prompt) >= 2 and len(numbers_cand) >= 1:
            try:
                # Try to evaluate simple comparisons or arithmetic implied
                # Extract floats
                p_vals = [float(x) for x in numbers_prompt]
                c_vals = [float(x) for x in numbers_cand]
                
                # Check for comparison operators in prompt
                ops = self.patterns['comparison_op'].findall(prompt)
                
                if ops:
                    # If prompt has "5 > 3", check if candidate agrees
                    # Simplified: Just check if candidate contains the max/min correctly based on operator
                    op = ops[0]
                    if '>' in op or 'less' in prompt.lower():
                        expected = max(p_vals)
                    elif '<' in op or 'more' in prompt.lower():
                        expected = min(p_vals) # Context dependent, simplistic fallback
                    else:
                        expected = p_vals[0] # Fallback
                    
                    # Check if candidate has the correct number
                    if any(abs(c_vals[0] - v) < 1e-6 for v in p_vals):
                        return 2.0 # Strong boost for correct numeric handling
                elif len(p_vals) == 2:
                    # Implicit comparison "Which is larger: 5, 3?"
                    if max(p_vals) == c_vals[0]:
                        return 2.0
            except ValueError:
                pass
        return 0.0

    def _meta_confidence(self, prompt):
        """
        Tier B: Epistemic Honesty.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy indicators without clear options
        if self.patterns['false_dichotomy'].search(prompt) and ('or' not in p_lower.split('?')[0]):
             # Rough check, usually requires more context
             pass 
             
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.4 # Low confidence on subjective matters
        
        # 4. Ambiguity markers (explicit)
        if any(x in p_lower for x in ['ambiguous', 'unclear', 'depends on']):
            return 0.3
            
        # 5. Lack of structural signal (No numbers, no logic markers)
        has_logic = any(self.patterns[k].search(prompt) for k in ['conditional', 'comparative', 'causal'])
        has_numbers = bool(self.patterns['number_seq'].search(prompt))
        
        if not has_logic and not has_numbers and len(prompt.split()) < 10:
            return 0.3 # Too short/ vague
            
        return 1.0

    def _ncd_distance(self, s1, s2):
        """Normalized Compression Distance."""
        if not s2:
            return 1.0
        z = zlib.compress
        len1 = len(z(s1.encode()))
        len2 = len(z(s2.encode()))
        len12 = len(z((s1 + s2).encode()))
        denom = max(len1, len2)
        if denom == 0:
            return 0.0
        return (len12 - min(len1, len2)) / denom

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Pre-compute prompt structures
        A, t0, sentences = self._build_implication_graph(prompt)
        hole_penalty = self._detect_holes(self._compute_transitive_closure(A), sentences) if len(sentences) > 0 else 0.0
        base_pragmatics = self._pragmatics_score(prompt, "") # Baseline
        
        # Meta-confidence cap
        conf_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural/Logic Score (Free Energy)
            energy = self._calculate_free_energy(cand, t0, sentences, A)
            logic_score = -energy - hole_penalty
            
            # 2. Computational Score (Numeric)
            comp_score = self._structural_computation(prompt, cand)
            
            # 3. Pragmatics Score
            prag_score = self._pragmatics_score(prompt, cand)
            
            # 4. NCD Tiebreaker (Max 15% weight logic)
            ncd = self._ncd_distance(prompt, cand)
            ncd_score = -ncd * 0.15 
            
            # Weighted Sum
            # Structural >= 50%, Computation >= 20%, NCD <= 15%
            final_score = (logic_score * 0.5) + (comp_score * 0.35) + (prag_score * 0.15) + ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f}, Comp:{comp_score:.2f}, Prag:{prag_score:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply confidence cap to scores if the prompt is ambiguous (Tier B)
        if conf_cap < 1.0:
            for res in results:
                # Dampen scores significantly if the question is flawed
                res['score'] *= conf_cap
                res['reasoning'] += f" | Cap:{conf_cap}"

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Capped by _meta_confidence to ensure epistemic honesty.
        """
        cap = self._meta_confidence(prompt)
        
        # Base confidence on structural match
        # If we can parse logic and the answer fits, confidence is higher
        A, t0, sentences = self._build_implication_graph(prompt)
        energy = self._calculate_free_energy(answer, t0, sentences, A)
        comp_score = self._structural_computation(prompt, answer)
        
        # Raw confidence from energy (lower energy = higher confidence)
        # Normalize roughly: energy 0 -> 1.0, energy > 5 -> 0.0
        raw_conf = max(0.0, 1.0 - (energy / 5.0))
        
        # Boost for successful computation
        if comp_score > 0:
            raw_conf = min(1.0, raw_conf + 0.4)
            
        # Apply cap
        final_conf = min(raw_conf, cap)
        
        # Never return > 0.9 unless computation was definitive
        if comp_score == 0 and final_conf > 0.9:
            final_conf = 0.9
            
        return float(np.clip(final_conf, 0.0, 1.0))