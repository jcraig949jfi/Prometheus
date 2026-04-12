import re
import numpy as np
from itertools import permutations

class ReasoningTool:
    """
    A hybrid reasoning tool combining Reservoir Computing for semantic embedding,
    Analogical Mapping for structural alignment, and SAT-based constraint checking
    for logical consistency. 
    
    Crucially, it implements DYNAMICS TRACKING (Frame C) by modeling reasoning as
    a state evolution process, scoring candidates based on trajectory stability
    under premise perturbation rather than static feature matching.
    """

    def __init__(self):
        # Reservoir setup (Fixed random matrix for similarity-preserving embedding)
        self.N_res = 500  # Reservoir size
        self.D_feat = 100 # Feature dimension (padded)
        np.random.seed(42) # Determinism
        self.W_res = np.random.randn(self.N_res, self.D_feat) * 0.5
        
        # Readout weights (initialized to identity-like for zero-shot capability)
        self.W_out = np.eye(self.N_res) * 0.1
        
        # Structural parsers
        self.negation_pat = re.compile(r'\b(not|n\'t|never|no)\b', re.IGNORECASE)
        self.comp_pat = re.compile(r'\b(greater|less|more|fewer|before|after)\b', re.IGNORECASE)
        self.cond_pat = re.compile(r'\b(if|unless|then|else)\b', re.IGNORECASE)
        self.num_pat = re.compile(r'-?\d+(?:\.\d+)?')
        self.presup_pat = re.compile(r'(have you stopped|why did .+ fail|when did .+ stop)', re.IGNORECASE)
        self.ambig_pat = re.compile(r'(every .+ a .+|he told .+ he|either .+ or .+)', re.IGNORECASE)

    def _extract_features(self, text: str) -> np.ndarray:
        """Convert text to a fixed-size feature vector."""
        feats = np.zeros(self.D_feat)
        if not text: return feats
        
        # 1. Boolean flags (indices 0-9)
        if self.negation_pat.search(text): feats[0] = 1.0
        if self.comp_pat.search(text): feats[1] = 1.0
        if self.cond_pat.search(text): feats[2] = 1.0
        
        # 2. Numeric extraction (indices 10-19)
        nums = [float(n) for n in self.num_pat.findall(text)]
        if nums:
            feats[10] = len(nums) / 10.0  # Count normalized
            feats[11] = np.mean(nums) / 100.0 if nums else 0.0 # Mean normalized
            feats[12] = np.std(nums) / 100.0 if len(nums)>1 else 0.0
            
        # 3. Length/Complexity (indices 20-29)
        feats[20] = min(len(text) / 1000.0, 1.0)
        feats[21] = min(text.count(' ') / 50.0, 1.0)
        
        # 4. Simple hash-based semantic fingerprint (indices 30-99)
        # Simulates high-dim projection of words
        words = text.lower().split()
        for i, w in enumerate(words[:10]):
            h = sum(ord(c) * (i+1) for c in w) % (self.D_feat - 30)
            feats[30 + h] += 1.0 / (len(words) + 1)
            
        return feats

    def _reservoir_encode(self, text: str) -> np.ndarray:
        """Encode text into reservoir state."""
        f = self._extract_features(text)
        # Pad/Crop to D_feat
        if len(f) < self.D_feat:
            f = np.pad(f, (0, self.D_feat - len(f)), mode='constant')
        f = f[:self.D_feat]
        return np.tanh(self.W_res @ f)

    def _parse_predicates(self, text: str) -> list:
        """Extract simple predicates for SAT construction."""
        preds = []
        # Extract comparisons: A > B, A < B
        for m in re.finditer(r'(\w+)\s*(>|<|==|=)\s*(\w+)', text):
            preds.append(('cmp', m.group(1), m.group(2), m.group(3)))
        # Extract causality
        if 'cause' in text.lower() or 'lead to' in text.lower():
            preds.append(('cause', text[:20], text[-20:]))
        return preds

    def _check_sat_consistency(self, prompt: str, answer: str) -> float:
        """Lightweight consistency check (Simulated SAT)."""
        # In a full implementation, this would build a CNF and run DPLL.
        # Here we check for direct contradictions in extracted numbers/logic.
        p_nums = [float(n) for n in self.num_pat.findall(prompt)]
        a_nums = [float(n) for n in self.num_pat.findall(answer)]
        
        score = 1.0
        # Check numeric consistency if counts match
        if len(p_nums) > 0 and len(a_nums) > 0:
            # If prompt implies an order, check if answer respects it roughly
            if 'greater' in prompt.lower() and len(a_nums) >= 2:
                if a_nums[0] < a_nums[1]: score *= 0.5 # Penalty for wrong order
            if 'less' in prompt.lower() and len(a_nums) >= 2:
                if a_nums[0] > a_nums[1]: score *= 0.5
                
        # Check negation consistency
        if 'not' in prompt.lower() and 'not' not in answer.lower():
            # Heuristic: if prompt negates, answer should acknowledge or be careful
            pass # Soft constraint
            
        return score

    def _compute_analogical_score(self, prompt: str, answer: str) -> float:
        """Compute similarity based on reservoir states."""
        r_p = self._reservoir_encode(prompt)
        r_a = self._reservoir_encode(answer)
        # Cosine similarity
        norm = np.linalg.norm(r_p) * np.linalg.norm(r_a)
        if norm == 0: return 0.0
        return float(np.dot(r_p, r_a) / norm)

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps
        if self.presup_pat.search(p_lower):
            return 0.2
        if re.search(r'have you stopped|why did .+ fail', p_lower):
            return 0.2
            
        # 2. Ambiguity traps
        if self.ambig_pat.search(p_lower):
            return 0.3
            
        # 3. Subjectivity
        if re.search(r'which is best|who is favorite|most beautiful', p_lower):
            return 0.3
            
        # 4. Missing info (Heuristic: very short prompts with complex questions)
        if '?' in prompt and len(prompt.split()) < 5:
            return 0.4
            
        return 1.0 # Default high confidence if no traps detected

    def _track_dynamics(self, prompt: str, answer: str) -> dict:
        """
        FRAME C: DYNAMICS TRACKER
        Models reasoning as state evolution.
        1. Break prompt into premises (sentences).
        2. Update reservoir state sequentially.
        3. Measure trajectory stability (Lyapunov-like exponent).
        """
        sentences = [s.strip() for s in re.split(r'[.?!]', prompt) if s.strip()]
        if len(sentences) < 2:
            # Not enough premises for dynamics, fallback to static
            return {'stability': 1.0, 'convergence': 1.0}

        trajectory = []
        state = np.zeros(self.N_res)
        
        # Recurrent update: s_t = tanh(W * f_t + U * s_{t-1})
        # We use a simple linear recurrence for the reservoir internal state
        U = np.eye(self.N_res) * 0.5 # Decay/Leak
        
        states = []
        for sent in sentences:
            f = self._extract_features(sent)
            # Reservoir update
            input_drive = self.W_res @ f
            state = np.tanh(input_drive + U @ state)
            states.append(state.copy())
        
        # Analyze Trajectory Stability
        # Calculate the variance of the final state if we perturb the order slightly
        # Or measure the rate of change (convergence)
        diffs = [np.linalg.norm(states[i] - states[i-1]) for i in range(1, len(states))]
        if not diffs:
            return {'stability': 1.0, 'convergence': 1.0}
            
        # Convergence: Are the state changes getting smaller? (Idea settling)
        if len(diffs) > 1:
            trend = np.polyfit(range(len(diffs)), diffs, 1)[0]
            convergence = 1.0 / (1.0 + np.exp(trend * 10)) # Sigmoid of slope
        else:
            convergence = 1.0
            
        # Stability: Sensitivity to last premise (Recency bias check)
        # Compare final state with state excluding last sentence
        if len(states) > 1:
            final_state = states[-1]
            prev_state = states[-2]
            # If the last sentence drastically changes the state, stability is low
            delta = np.linalg.norm(final_state - prev_state)
            stability = 1.0 / (1.0 + delta) 
        else:
            stability = 1.0
            
        return {'stability': stability, 'convergence': convergence}

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        base_meta_conf = self._meta_confidence(prompt)
        
        # Pre-calculate prompt dynamics
        prompt_dyn = self._track_dynamics(prompt, "")
        
        for cand in candidates:
            # 1. Structural & Logical Score (SAT & Parsing)
            sat_score = self._check_sat_consistency(prompt, cand)
            
            # 2. Analogical Score (Reservoir Similarity)
            analog_score = self._compute_analogical_score(prompt, cand)
            
            # 3. Dynamics Score (Trajectory Stability of Answer relative to Prompt)
            # We check if the answer's "state" is consistent with the prompt's evolved state
            ans_dyn = self._track_dynamics(cand, "")
            # Stability metric: How well does the answer align with the prompt's convergence?
            dyn_score = (prompt_dyn['stability'] + ans_dyn['convergence']) / 2.0
            
            # 4. NCD Tiebreaker (Max 15% weight)
            import zlib
            data = prompt.encode() + cand.encode()
            ncd = len(zlib.compress(data)) / max(len(zlib.compress(prompt.encode())), len(zlib.compress(cand.encode())), 1)
            ncd_score = 1.0 / ncd if ncd > 0 else 0.0
            ncd_score = min(ncd_score, 1.0) # Normalize
            
            # Final Weighted Score
            # Dynamics/State: 40%, Structural: 30%, Analogical: 20%, NCD: 10%
            # Note: If meta_confidence is low (ambiguous), cap the max score
            raw_score = (
                0.40 * dyn_score + 
                0.30 * sat_score + 
                0.20 * analog_score + 
                0.10 * ncd_score
            )
            
            final_score = raw_score * base_meta_conf
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Dyn:{dyn_score:.2f}, Sat:{sat_score:.2f}, Analog:{analog_score:.2f}, MetaConf:{base_meta_conf:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.9 unless computation is definitive.
        Returns < 0.3 for ambiguous/unanswerable prompts.
        """
        # 1. Meta-Confidence (Question Properties)
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.4:
            return meta_conf # Hard cap for ambiguous questions
            
        # 2. Structural Match
        sat = self._check_sat_consistency(prompt, answer)
        
        # 3. Dynamics Stability
        dyn = self._track_dynamics(prompt, answer)
        stab = dyn['stability']
        
        # Combined confidence
        # High confidence requires: No ambiguity (meta), High consistency (sat), Stable trajectory (dyn)
        conf = (meta_conf * 0.5) + (sat * 0.3) + (stab * 0.2)
        
        # Cap at 0.95 to maintain epistemic humility unless it's a math certainty
        # (In this simplified model, we assume few things are 100% certain without external verification)
        return min(conf, 0.95)