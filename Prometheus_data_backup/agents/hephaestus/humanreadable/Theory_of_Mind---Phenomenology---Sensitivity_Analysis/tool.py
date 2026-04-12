import numpy as np
from typing import Dict, List

class ReasoningTool:
    """
    Theory of Mind x Phenomenology x Sensitivity Analysis reasoning tool.
    
    Extracts mental-state tuples (agent, attitude, proposition, polarity, phenomenology),
    propagates constraints through a belief graph, performs sensitivity analysis via
    perturbations, and tracks state dynamics for trajectory stability.
    
    Score = w1*mean_confidence - w2*sensitivity + w3*phen_ratio + w4*stability
    """
    
    def __init__(self):
        self.w1, self.w2, self.w3, self.w4 = 0.35, 0.2, 0.15, 0.3
        
        # ToM attitude patterns
        self.tom_patterns = [
            (r'\b(believe[sd]?|think[s]?|thought)\b', 'belief'),
            (r'\b(want[s]?|desire[sd]?|wish|hope[sd]?)\b', 'desire'),
            (r'\b(intend[sd]?|plan[s]?|will|going to)\b', 'intention'),
        ]
        
        # Phenomenology markers (first-person experiential)
        self.phen_patterns = [
            r'\bI (feel|experience|perceive|sense|observe)\b',
            r'\bas I (feel|experience|perceive|see)\b',
            r'\bsetting aside\b',
            r'\bfrom my perspective\b',
            r'\bin my view\b',
        ]
        
        # Negation, conditional, causal patterns
        self.neg_pattern = r'\b(not|never|no|none|nothing)\b'
        self.cond_pattern = r'\b(if|unless|when|whenever)\b.*\b(then|,)\b'
        self.causal_pattern = r'\b(because|since|leads to|causes|due to)\b'
        
    def _extract_tuples(self, text: str) -> np.ndarray:
        """Extract mental-state tuples: (agent_id, att_type, prop_hash, polarity, phen_flag, confidence)"""
        tuples = []
        sentences = re.split(r'[.!?]', text.lower())
        
        for sent in sentences:
            if len(sent.strip()) < 3:
                continue
                
            # Detect agent (simple heuristic: first noun phrase or "self" for I/my)
            agent_id = 0 if re.search(r'\b(i|my|me)\b', sent) else 1
            
            # Detect ToM attitude
            att_type = 0  # default: belief
            for pattern, att_name in self.tom_patterns:
                if re.search(pattern, sent):
                    att_type = {'belief': 0, 'desire': 1, 'intention': 2}[att_name]
                    break
            
            # Proposition hash (simple: hash of content words)
            prop_hash = hash(re.sub(r'\b(the|a|an|is|was|are)\b', '', sent)) % 10000
            
            # Polarity (negation detection)
            polarity = -1 if re.search(self.neg_pattern, sent) else 1
            
            # Phenomenology flag
            phen_flag = 1 if any(re.search(p, sent) for p in self.phen_patterns) else 0
            
            tuples.append([agent_id, att_type, prop_hash, polarity, phen_flag, 1.0])
        
        return np.array(tuples) if tuples else np.zeros((1, 6))
    
    def _build_constraint_graph(self, states: np.ndarray) -> np.ndarray:
        """Build rule matrix R for constraint propagation"""
        n = len(states)
        R = np.eye(n)  # Identity base
        
        # Add inference rules (simple: same agent + compatible attitudes reinforce)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Same agent, compatible polarity -> strengthen
                if states[i, 0] == states[j, 0] and states[i, 3] * states[j, 3] > 0:
                    R[i, j] = 0.2
                # Contradictory polarity -> weaken
                elif states[i, 0] == states[j, 0] and states[i, 3] * states[j, 3] < 0:
                    R[i, j] = -0.1
        
        return R
    
    def _propagate_confidence(self, states: np.ndarray, R: np.ndarray, max_iter=10) -> np.ndarray:
        """Iteratively propagate confidence until convergence"""
        C = states[:, 5].copy()
        
        for _ in range(max_iter):
            C_new = np.clip(R @ C, 0, 1)
            if np.sum(np.abs(C_new - C)) < 1e-3:
                break
            C = C_new
        
        return C
    
    def _sensitivity_analysis(self, states: np.ndarray, R: np.ndarray, C_baseline: np.ndarray) -> float:
        """Perturb literals and measure confidence divergence"""
        if len(states) < 2:
            return 0.0
        
        sensitivities = []
        for i in range(min(len(states), 5)):  # Limit perturbations
            states_pert = states.copy()
            # Flip polarity
            states_pert[i, 3] *= -1
            C_pert = self._propagate_confidence(states_pert, R)
            sensitivities.append(np.linalg.norm(C_baseline - C_pert))
        
        return np.mean(sensitivities) if sensitivities else 0.0
    
    def _track_dynamics(self, text: str) -> float:
        """Track state evolution as sentences are processed sequentially"""
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 3]
        if len(sentences) < 2:
            return 0.5
        
        # Build cumulative states
        states_history = []
        for i in range(1, len(sentences) + 1):
            partial_text = '. '.join(sentences[:i])
            states = self._extract_tuples(partial_text)
            R = self._build_constraint_graph(states)
            C = self._propagate_confidence(states, R)
            states_history.append(np.mean(C))
        
        # Measure convergence stability
        trajectory = np.array(states_history)
        if len(trajectory) < 2:
            return 0.5
        
        # Stability = 1 - variance in later states (converged trajectories are stable)
        stability = 1.0 - min(np.var(trajectory[-3:]), 1.0) if len(trajectory) >= 3 else 0.5
        return stability
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect judgment traps and return confidence cap"""
        prompt_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'\b(have you stopped|did you stop|why did.*fail|why did.*stop)', prompt_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', prompt_lower):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they)\b.*\bwho\b', prompt_lower):
            return 0.3
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', prompt_lower) and 'neither' not in prompt_lower:
            return 0.35
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|greatest)\b', prompt_lower) and not re.search(r'\b(most|least|highest|lowest)\b', prompt_lower):
            return 0.35
        
        # Unanswerable markers
        if re.search(r'\b(impossible to|cannot determine|insufficient|ambiguous)\b', prompt_lower):
            return 0.25
        
        return 1.0  # No trap detected
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2, c12 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode())), len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by ToM + phenomenology + sensitivity + dynamics score"""
        results = []
        
        for cand in candidates:
            combined = prompt + " " + cand
            
            # Extract mental states
            states = self._extract_tuples(combined)
            R = self._build_constraint_graph(states)
            C = self._propagate_confidence(states, R)
            
            # Sensitivity analysis
            sensitivity = self._sensitivity_analysis(states, R, C)
            
            # Phenomenology ratio
            phen_ratio = np.mean(states[:, 4]) if len(states) > 0 else 0.0
            
            # Mean confidence (focus on self-attributed states)
            self_states = states[states[:, 0] == 0]
            mean_conf = np.mean(C[states[:, 0] == 0]) if len(self_states) > 0 else np.mean(C)
            
            # Dynamics stability
            stability = self._track_dynamics(combined)
            
            # NCD tiebreaker (max 15% weight)
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Final score
            score = (self.w1 * mean_conf - self.w2 * sensitivity + 
                    self.w3 * phen_ratio + self.w4 * stability + 0.1 * ncd_score)
            
            reasoning = f"conf={mean_conf:.2f} sens={sensitivity:.2f} phen={phen_ratio:.2f} stab={stability:.2f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 with epistemic honesty"""
        # Check for judgment traps first
        meta_cap = self._meta_confidence(prompt)
        
        combined = prompt + " " + answer
        states = self._extract_tuples(combined)
        
        if len(states) == 0 or np.sum(states[:, 5]) < 0.1:
            return min(0.2, meta_cap)
        
        R = self._build_constraint_graph(states)
        C = self._propagate_confidence(states, R)
        
        # Sensitivity (lower is better)
        sensitivity = self._sensitivity_analysis(states, R, C)
        
        # Dynamics stability
        stability = self._track_dynamics(combined)
        
        # Base confidence on mean propagated confidence and stability
        base_conf = 0.4 * np.mean(C) + 0.4 * stability + 0.2 * (1.0 - min(sensitivity, 1.0))
        
        # Apply meta-confidence cap
        return min(base_conf, meta_cap)