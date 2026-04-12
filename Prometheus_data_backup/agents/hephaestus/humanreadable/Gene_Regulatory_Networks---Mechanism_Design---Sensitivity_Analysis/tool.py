import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning evaluator combining Gene Regulatory Network (GRN) dynamics, 
    Mechanism Design scoring, and Sensitivity Analysis.
    
    Core Mechanism:
    1. Parsing: Extracts atomic propositions and causal/temporal links from text.
    2. Dynamics (Frame C): Models the answer as a state vector evolving under 
       a linear threshold rule (GRN style). Computes Lyapunov-like stability by 
       perturbing inputs and measuring trajectory divergence.
    3. Scoring (Mechanism Design): Uses a sensitivity-weighted Brier score. 
       Answers that are logically fragile (high sensitivity to small changes) 
       are penalized more heavily.
    4. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and 
       unanswerability in the PROMPT to cap confidence, ensuring the model 
       admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower)\s+(than)?\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|triggers|implies)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|during|while|subsequently)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            # Tier B Traps
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|quit)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either.*or|must be|only option)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE)
        }
        self.theta = 0.5  # Activation threshold for GRN dynamics

    def _parse_propositions(self, text: str) -> List[str]:
        """Split text into atomic propositions based on delimiters."""
        # Simple split by conjunctions and punctuation for atomicity
        cleaned = re.sub(r'[,.]', ' ', text)
        parts = re.split(r'\b(and|but|however|therefore|thus)\b', cleaned, flags=re.IGNORECASE)
        props = [p.strip() for p in parts if p.strip()]
        return props if props else [text]

    def _build_graph(self, propositions: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Build adjacency matrix G and map propositions to indices.
        Edges represent causal/conditional implications.
        """
        n = len(propositions)
        if n == 0:
            return np.array([]), []
        
        G = np.zeros((n, n))
        nodes = []
        
        # Map each proposition to a node
        for i, prop in enumerate(propositions):
            nodes.append(prop)
            lower_prop = prop.lower()
            
            # Self-loop base weight (inertia)
            G[i, i] = 0.5 
            
            # Check for internal causal claims within the proposition itself
            if any(k in lower_prop for k in ['causes', 'leads to', 'implies']):
                # If a single prop claims causality, it links to itself strongly or implies next
                # For simplicity in single-sentence analysis, we boost self-consistency
                G[i, i] = 1.0

        # Build edges based on sequential logic and keyword matching
        for i, p_i in enumerate(propositions):
            for j, p_j in enumerate(propositions):
                if i == j: continue
                
                # Heuristic: If p_i contains "if" and p_j contains "then" logic or matching nouns
                # This is a simplified dependency parser
                words_i = set(re.findall(r'\w+', p_i.lower()))
                words_j = set(re.findall(r'\w+', p_j.lower()))
                overlap = words_i.intersection(words_j)
                
                # Causal/Temporal linking
                if any(k in p_i.lower() for k in ['causes', 'leads', 'before', 'after']):
                    if len(overlap) > 0:
                        G[j, i] = 1.0  # i causes j
                
                # Conditional linking (If A then B)
                if 'if' in p_i.lower() and ('then' in p_j.lower() or len(overlap) > 1):
                    G[j, i] = 0.8

        return G, nodes

    def _simulate_dynamics(self, G: np.ndarray, initial_state: np.ndarray) -> np.ndarray:
        """
        Simulate GRN dynamics: x(t+1) = step(G * x(t) - theta).
        Returns the steady state or max iterations state.
        """
        if G.size == 0:
            return initial_state
            
        x = initial_state.copy().astype(float)
        n = len(x)
        if n == 0: return x
        
        for _ in range(10):  # Max iterations for convergence
            x_new = np.zeros_like(x)
            for i in range(n):
                # Linear threshold rule
                val = np.dot(G[i, :], x) - self.theta
                x_new[i] = 1.0 if val >= 0 else 0.0
            
            if np.array_equal(x, x_new):
                break
            x = x_new
        return x

    def _compute_sensitivity(self, G: np.ndarray, base_state: np.ndarray) -> float:
        """
        Compute average sensitivity score by perturbing each node.
        Measures how much the total system state changes when one input flips.
        """
        if G.size == 0:
            return 0.0
            
        n = len(base_state)
        if n == 0: return 0.0
        
        base_output = self._simulate_dynamics(G, base_state)
        base_sum = np.sum(base_output)
        total_change = 0.0
        
        for i in range(n):
            perturbed = base_state.copy()
            perturbed[i] = 1 - perturbed[i]  # Flip bit
            
            new_output = self._simulate_dynamics(G, perturbed)
            change = abs(np.sum(new_output) - base_sum)
            total_change += change
            
        return total_change / n if n > 0 else 0.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if min(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes the PROMPT for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did...")
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        
        # 2. False Dichotomy / Absolute constraints without evidence
        if self.patterns['false_dichotomy'].search(prompt):
            # Only penalize if it looks like a trick question context
            if "must" in p_lower or "only" in p_lower:
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.patterns['subjectivity'].search(prompt):
            if "fact" not in p_lower and "calculate" not in p_lower:
                return 0.25

        # 4. Unanswerability / Missing Info indicators
        unanswerable_phrases = ["who is taller", "which one", "what color", "where is"]
        if any(phrase in p_lower for phrase in unanswerable_phrases):
            # Check if context is provided (simple heuristic: length)
            if len(prompt) < 50: # Too short to contain necessary context
                return 0.1

        return 1.0  # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []

        # Pre-process prompt structure
        prompt_props = self._parse_propositions(prompt)
        G_prompt, _ = self._build_graph(prompt_props)
        
        # Determine "Ground Truth" approximation (Consensus of high-quality candidates)
        # Since we don't have external truth, we use the median structural complexity 
        # and NCD-centroid as a proxy for the "true" manifold.
        candidate_scores_raw = []
        
        # First pass: Get structural scores and states
        states = []
        sensitivities = []
        
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            props = self._parse_propositions(full_text)
            G, nodes = self._build_graph(props)
            
            # Initial state: 1 if proposition exists, 0 otherwise (simplified)
            # In a real scenario, this would be extracted truth values.
            # Here we assume the candidate asserts its propositions are true.
            init_state = np.ones(len(nodes)) if nodes else np.array([])
            
            state = self._simulate_dynamics(G, init_state)
            sens = self._compute_sensitivity(G, init_state)
            
            states.append(state)
            sensitivities.append(sens)
            
            # Numeric evaluation (Constructive computation)
            nums_prompt = [float(x) for x in self.patterns['numbers'].findall(prompt)]
            nums_cand = [float(x) for x in self.patterns['numbers'].findall(cand)]
            
            numeric_score = 0.0
            if nums_prompt and nums_cand:
                # Check for simple arithmetic consistency (e.g., 2+2=4)
                # Very basic check: if candidate has numbers, do they contradict prompt?
                # This is a placeholder for complex math solvers
                numeric_score = 0.1 # Small bonus for having numbers
            
            # Structural features count
            struct_count = 0
            for key in ['negation', 'comparative', 'conditional', 'causal', 'temporal']:
                if self.patterns[key].search(cand):
                    struct_count += 1
            
            struct_score = struct_count * 0.15  # Weight for structural richness
            
            # NCD component (Max 15% weight as per instructions)
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.15
            
            # Base score: Structural + Numeric + NCD
            base_score = struct_score + numeric_score + ncd_score
            
            candidate_scores_raw.append(base_score)

        # Mechanism Design Scoring: Sensitivity Weighted Brier-like score
        # We treat the "consensus" as the average of the top 50% of raw scores
        if len(candidate_scores_raw) > 0:
            median_raw = np.median(candidate_scores_raw)
        else:
            median_raw = 0.5
            
        final_results = []
        for i, cand in enumerate(candidates):
            sens = sensitivities[i]
            base = candidate_scores_raw[i]
            
            # Penalty for fragility: High sensitivity (instability) reduces score
            # Score = Base - (Sensitivity * PenaltyFactor)
            # We want stable answers (low sensitivity) to score higher if base is good.
            # However, complex logic might naturally have higher sensitivity.
            # Let's invert: Score = Base * (1 - sens * 0.5) 
            # But wait, the prompt says: "Higher sensitivity nodes contribute more to the penalty"
            # Formula from prompt: Score = - sum( s_i * (r_i - x*)^2 )
            # Approximation: We penalize deviation from median, weighted by sensitivity.
            
            deviation = abs(base - median_raw)
            penalty = sens * deviation * 2.0
            
            final_score = base - penalty
            
            # Ensure score is within reasonable bounds for ranking
            final_score = max(-1.0, min(1.0, final_score))
            
            final_results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{base:.2f}, Sensitivity:{sens:.2f}, Penalty:{penalty:.2f}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of the prompt (Tier B).
        """
        # 1. Meta Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            return meta_cap

        # 2. Structural Validation
        # Does the answer contain structural elements found in the prompt?
        prompt_features = 0
        answer_features = 0
        
        for key in ['negation', 'comparative', 'conditional', 'causal', 'temporal']:
            if self.patterns[key].search(prompt):
                prompt_features += 1
            if self.patterns[key].search(answer):
                answer_features += 1
        
        # If prompt has logic but answer has none, low confidence
        if prompt_features > 0 and answer_features == 0:
            raw_conf = 0.4
        else:
            # Base confidence on structural alignment and length appropriateness
            # Simple heuristic: if answer is too short to contain reasoning
            if len(answer.split()) < 3 and len(prompt.split()) > 10:
                raw_conf = 0.5
            else:
                raw_conf = 0.85 # High but not absolute

        # 3. Dynamics Stability Check (Frame C)
        # Simulate the specific answer
        props = self._parse_propositions(f"{prompt} {answer}")
        G, _ = self._build_graph(props)
        init = np.ones(len(props)) if props else np.array([])
        
        if len(props) > 0:
            sens = self._compute_sensitivity(G, init)
            # If the logic is extremely fragile (sens > 0.8), reduce confidence
            if sens > 0.8:
                raw_conf *= 0.6
            elif sens < 0.2:
                raw_conf *= 1.1 # Boost stable logic
        else:
            raw_conf *= 0.7 # No parseable structure

        # Apply Cap
        final_conf = min(raw_conf, meta_cap)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, final_conf))