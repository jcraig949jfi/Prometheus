import numpy as np
import re
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning tool implementing Gene Regulatory Network (GRN) dynamics with 
    Epigenetic biasing and Metamorphic Testing for answer validation.
    
    Mechanism:
    1. Parsing: Extracts propositions (nodes) and causal/logical relations (edges) 
       from text using regex. Nodes have binary states (0/1) and epigenetic markers.
    2. Dynamics: Models reasoning as a dynamical system s(t+1) = step(W*s(t) + b).
       The system iterates to an attractor (stable state), representing the 
       consistent interpretation of the text.
    3. Epigenetics: Bias vector 'b' is modulated by linguistic markers (negation, 
       modals) acting as methylation, repressing specific nodes.
    4. Metamorphic Testing: Generates perturbed versions of the candidate (e.g., 
       negating premises, swapping order) and checks if the GRN output remains 
       logically consistent with the transformation.
    5. Confidence: Derived from trajectory stability (Lyapunov-like) and 
       meta-cognitive checks for ambiguity/presupposition.
    """

    def __init__(self):
        self.max_steps = 10
        self.tolerance = 1e-6

    def _tokenize_and_parse(self, text: str) -> Tuple[List[str], np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Parses text into nodes and constructs the weight matrix W and bias b.
        Returns nodes, W, b, and metadata.
        """
        text_lower = text.lower()
        # Simple sentence splitting
        sentences = re.split(r'[.;]', text_lower)
        
        # Extract potential nodes (keywords/concepts)
        # We treat unique lowercase words > 3 chars as potential nodes for simplicity in this demo
        # In a full system, this would be NLP entity extraction
        raw_words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        # Filter stopwords
        stopwords = {'that', 'this', 'with', 'have', 'been', 'were', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'than', 'then', 'when', 'where', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'too', 'very', 'can', 'just', 'now', 'here', 'there', 'also', 'back', 'into', 'from', 'out', 'off', 'over', 'under', 'again', 'further', 'once', 'any', 'about', 'after', 'before', 'between', 'through', 'during', 'above', 'below', 'up', 'down', 'to', 'from', 'on', 'at', 'in', 'for', 'of', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'although', 'though', 'after', 'before', 'since', 'unless', 'lest', 'provided', 'assuming', 'given'}
        
        concepts = []
        seen = set()
        for w in raw_words:
            if w not in stopwords and w not in seen:
                concepts.append(w)
                seen.add(w)
        
        n = len(concepts)
        if n == 0:
            return [], np.array([[]]), np.array([]), {}

        W = np.zeros((n, n))
        b = np.zeros(n)
        e = np.zeros(n) # Epigenetic markers (0=active, 1=repressed)
        node_map = {c: i for i, c in enumerate(concepts)}
        
        # Parse relations
        for sent in sentences:
            if not sent.strip(): continue
            
            # Detect Negation (Epigenetic repression)
            is_negated = bool(re.search(r'\b(not|no|never|neither|nobody|nothing)\b', sent))
            
            # Detect Conditionals/Causals
            has_if = 'if' in sent or 'because' in sent or 'leads to' in sent or 'causes' in sent
            has_then = 'then' in sent or 'therefore' in sent or 'so' in sent
            
            # Detect Comparatives
            has_greater = 'greater' in sent or 'more' in sent or 'increases' in sent
            has_lesser = 'less' in sent or 'decreases' in sent
            
            # Simple heuristic: If sentence has two known concepts, link them
            sent_concepts = [c for c in concepts if c in sent]
            
            for i, c1 in enumerate(sent_concepts):
                idx1 = node_map[c1]
                
                # Apply epigenetic bias if negation is present near this concept
                if is_negated:
                    e[idx1] = 1.0 
                
                for j, c2 in enumerate(sent_concepts):
                    if i == j: continue
                    idx2 = node_map[c2]
                    
                    # Directionality heuristics
                    weight = 0.0
                    if has_if or has_then or has_greater:
                        weight = 1.0 # Activation
                    elif has_lesser:
                        weight = -0.5 # Inhibition
                    
                    if weight != 0:
                        # If c1 appears before c2, assume c1 -> c2
                        if sent.index(c1) < sent.index(c2):
                            W[idx2, idx1] += weight
                        else:
                            W[idx1, idx2] += weight

        # Normalize weights to prevent explosion
        if n > 0:
            col_sum = np.sum(np.abs(W), axis=0)
            col_sum[col_sum == 0] = 1
            W = W / col_sum
            
        # Bias from epigenetic markers
        b = -1.0 * e 
        
        meta = {'concepts': concepts, 'node_map': node_map}
        return concepts, W, b, meta

    def _run_dynamics(self, W: np.ndarray, b: np.ndarray, s0: np.ndarray) -> Tuple[np.ndarray, float, List[np.ndarray]]:
        """
        Runs the GRN state update: s' = step(W*s + b)
        Returns final state, stability score, and trajectory.
        """
        if W.size == 0:
            return s0, 1.0, [s0]
            
        s = s0.copy()
        trajectory = [s.copy()]
        oscillations = 0
        stable_steps = 0
        
        for step in range(self.max_steps):
            s_new = np.where(W @ s + b >= 0, 1, 0).astype(float)
            
            # Check convergence
            if np.array_equal(s, s_new):
                stable_steps += 1
                if stable_steps >= 2: # Stable for 2 steps
                    break
            else:
                stable_steps = 0
                # Count flips for oscillation penalty
                flips = np.sum(s != s_new)
                if flips > 0:
                    oscillations += 1
            
            s = s_new
            trajectory.append(s.copy())
            
        # Stability score: 1.0 if converged quickly, 0.0 if oscillating
        stability = 1.0 - (oscillations / self.max_steps)
        return s, stability, trajectory

    def _generate_metamorphs(self, text: str) -> List[str]:
        """Generates transformed versions of the text for testing."""
        variants = [text]
        
        # MR1: Double numbers (if any)
        def double_num(match):
            val = float(match.group())
            return str(val * 2)
        
        if re.search(r'\d+\.?\d*', text):
            variants.append(re.sub(r'\d+\.?\d*', double_num, text))
            
        # MR2: Negate key verbs (simple swap for testing robustness)
        # This is a placeholder for more complex logical inversion
        if 'increases' in text:
            variants.append(text.replace('increases', 'decreases'))
        elif 'decreases' in text:
            variants.append(text.replace('decreases', 'increases'))
            
        return variants

    def _check_metamorphic_relations(self, original_score: float, variants_scores: List[float]) -> float:
        """
        Checks if the model behavior is consistent under transformation.
        For this simplified model, we expect some variance but not total collapse.
        """
        if not variants_scores:
            return 1.0
        
        # Heuristic: If original is high, variants should not be randomly low unless transformation invalidates logic
        # Here we simply penalize high variance in scores as "unstable reasoning"
        all_scores = [original_score] + variants_scores
        variance = np.var(all_scores)
        
        # Map variance to a score (low variance = high MR score)
        # Assuming max variance is ~0.25 for binary-like scores
        mr_score = max(0.0, 1.0 - (variance * 4)) 
        return mr_score

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Checks for ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        presupposition_triggers = ['have you stopped', 'have you quit', 'why did', 'when did', 'how often did']
        for trigger in presupposition_triggers:
            if trigger in p_lower:
                return 0.2 # High risk of presupposition
        
        # 2. Scope/Pronoun Ambiguity
        if re.search(r'every.*a\s+\w+', p_lower) and 'same' not in p_lower:
            return 0.4 # Potential scope ambiguity
        if re.search(r'(he|she|it|they)\s+(was|is|were|are)\s+(wrong|right|told)', p_lower):
             if 'who' in p_lower or 'which' in p_lower:
                return 0.3 # Pronoun ambiguity resolution required

        # 3. False Dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', p_lower) and 'option' not in p_lower:
            return 0.5
            
        # 4. Subjectivity
        subjective_words = ['best', 'worst', 'favorite', 'beautiful', 'ugly', 'good', 'bad']
        if any(w in p_lower for w in subjective_words) and 'measure' not in p_lower:
            return 0.4
            
        return 1.0 # No obvious traps detected

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Parse prompt to get global context/constraints if any
        # For this implementation, we treat prompt + candidate as the full text to reason over
        # or use prompt as the "system state" and candidate as a "hypothesis" to test.
        # Strategy: Concatenate prompt and candidate to form the full proposition set.
        
        for cand in candidates:
            full_text = f"{prompt} {cand}"
            concepts, W, b, meta = self._tokenize_and_parse(full_text)
            
            if len(concepts) == 0:
                # Fallback for empty parse
                results.append({"candidate": cand, "score": 0.0, "reasoning": "No logical structure parsed."})
                continue
            
            n = len(concepts)
            # Initial state: All active (optimistic) or based on prompt bias
            s0 = np.ones(n) 
            
            # Run Dynamics
            final_state, stability, trajectory = self._run_dynamics(W, b, s0)
            
            # Calculate Base Score from State
            # Score is proportion of "True" (1) nodes in the final attractor
            # Weighted by stability of the convergence
            activation_ratio = np.mean(final_state)
            base_score = activation_ratio * stability
            
            # Metamorphic Testing
            variants = self._generate_metamorphs(full_text)
            variant_scores = []
            for v in variants:
                _, W_v, b_v, _ = self._tokenize_and_parse(v)
                if W_v.size > 0:
                    fs_v, stab_v, _ = self._run_dynamics(W_v, b_v, np.ones(len(W_v)))
                    variant_scores.append(np.mean(fs_v) * stab_v)
                else:
                    variant_scores.append(0.0)
            
            mr_score = self._check_metamorphic_relations(base_score, variant_scores)
            
            # Final Score Composition
            # Structural/Dynamics (60%) + Metamorphic (25%) + NCD Tiebreaker (15%)
            # Note: NCD is minimized as per instructions, used only as tiebreaker
            import zlib
            def ncd(a, b):
                if not a or not b: return 0.5
                comp_ab = len(zlib.compress((a+b).encode()))
                comp_a = len(zlib.compress(a.encode()))
                comp_b = len(zlib.compress(b.encode()))
                return comp_ab / max(comp_a, comp_b, 1)
            
            # NCD between prompt and candidate (lower is better match, invert for score)
            ncd_val = ncd(prompt, cand)
            ncd_score = 1.0 - min(1.0, ncd_val) # Invert so high similarity = high score
            
            final_score = (base_score * 0.60) + (mr_score * 0.25) + (ncd_score * 0.15)
            
            # Cap score if meta-confidence is low (Tier B)
            meta_cap = self._meta_confidence(full_text)
            if final_score > meta_cap:
                final_score = meta_cap
                
            reasoning = f"Convergence stability: {stability:.2f}. Activation: {activation_ratio:.2f}. MR Consistency: {mr_score:.2f}."
            if meta_cap < 1.0:
                reasoning += " [Warning: Potential ambiguity or presupposition detected]"
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive checks for ambiguity.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Run a quick dynamic check
        full_text = f"{prompt} {answer}"
        concepts, W, b, _ = self._tokenize_and_parse(full_text)
        
        if len(concepts) == 0:
            return 0.1 # Cannot parse, low confidence
            
        s0 = np.ones(len(concepts))
        final_state, stability, _ = self._run_dynamics(W, b, s0)
        
        # Base confidence on stability and activation
        # If the system is unstable (oscillating), confidence should be low
        base_conf = stability * np.mean(final_state)
        
        # Apply meta cap
        final_conf = min(base_conf, meta_cap)
        
        # Hard cap for non-computational answers unless very stable
        if meta_cap == 1.0 and stability < 0.8:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))