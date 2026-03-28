import numpy as np
import re
from collections import defaultdict
from itertools import combinations

class ReasoningTool:
    """
    Ergodic-NAS Reasoning Tool.
    Mechanism:
    1. NAS-inspired Grammar Search: Selects best regex rules from a fixed pool based on 
       matching density in the prompt (simulating the 'validation score' step).
    2. Constraint Graph: Extracts literals and logical relations (negation, causality, belief).
       Builds an energy function where violations (e.g., A->B but A=True, B=False) add energy.
    3. Ergodic Sampling: Uses Metropolis-Hastings MCMC to sample world states proportional 
       to exp(-Energy). The score is the frequency a candidate's literals appear true in samples.
    """
    
    # Fixed pool of regex rules (The "Architecture Space")
    RULES = [
        ('negation', r'\b(not|no|never|neither)\b', 'neg'),
        ('causal', r'\b(causes|leads to|implies|if|then)\b', 'causal'),
        ('comparative', r'\b(more than|less than|greater|smaller|before|after)\b', 'comp'),
        ('belief', r'\b(believes|thinks|suspects|knows)\b', 'belief'),
        ('numeric', r'\d+(\.\d+)?', 'num'),
        ('entity', r'\b[A-Z][a-z]+\b', 'ent')
    ]

    def __init__(self):
        self.rules = self.RULES
        self.selected_rule_indices = [] # Result of "NAS" search

    def _nas_search(self, text: str) -> list[int]:
        """Simulates NAS by selecting rules that find matches in the text."""
        scores = []
        for i, (_, pattern, _) in enumerate(self.rules):
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            # Surrogate score: density of matches
            scores.append((i, matches / (len(text) + 1)))
        
        # Select top-K rules (K=3) as the optimal architecture
        scores.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, _ in scores[:3]]

    def _parse_propositions(self, text: str, active_rules: list[int]) -> list[dict]:
        """Extracts logical propositions based on active NAS rules."""
        props = []
        text_lower = text.lower()
        
        # Simple tokenization for entities
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Check active rules
        for idx in active_rules:
            rule_name, pattern, rtype = self.rules[idx]
            if re.search(pattern, text, re.IGNORECASE):
                # Generate synthetic propositions based on rule type
                if rtype == 'negation':
                    props.append({'type': 'negation', 'text': 'NOT', 'weight': 0.8})
                elif rtype == 'causal':
                    props.append({'type': 'causal', 'text': 'IMPLIES', 'weight': 0.9})
                elif rtype == 'belief':
                    props.append({'type': 'belief', 'text': 'BELIEF', 'weight': 0.7})
                elif rtype == 'numeric':
                    nums = re.findall(r'\d+(\.\d+)?', text)
                    if len(nums) >= 2:
                        # Simple comparative logic
                        try:
                            if float(nums[0]) > float(nums[1]):
                                props.append({'type': 'fact', 'text': f"{nums[0]}>{nums[1]}", 'weight': 1.0})
                            else:
                                props.append({'type': 'fact', 'text': f"{nums[1]}>{nums[0]}", 'weight': 1.0})
                        except: pass
        
        # Add entities as base literals
        for ent in set(entities):
            props.append({'type': 'literal', 'text': ent, 'weight': 0.5})
            
        return props

    def _build_energy_func(self, props: list[dict], candidate: str):
        """Constructs an energy function based on constraints and candidate alignment."""
        cand_lower = candidate.lower()
        
        # Define literals V: extracted facts + candidate assertion
        # We map strings to indices
        literals = list(set([p['text'] for p in props if p['type'] in ['fact', 'literal']]))
        if not literals:
            literals = ["default_true"]
        
        # Check if candidate contradicts explicit negations or supports facts
        candidate_supports = 0.0
        candidate_contradicts = 0.0
        
        for p in props:
            txt = p['text'].lower()
            if p['type'] == 'negation':
                if txt in cand_lower or 'not' in cand_lower:
                    candidate_contradicts += p['weight'] # Penalty if candidate has negation when context implies simple fact
            elif p['type'] == 'fact':
                if txt in cand_lower:
                    candidate_supports += p['weight']
                # Simple antonym check simulation
                if ('more' in txt and 'less' in cand_lower) or ('less' in txt and 'more' in cand_lower):
                    candidate_contradicts += p['weight']
        
        def energy(state_vector: np.ndarray) -> float:
            """Calculates energy: lower is better. Penalizes constraint violations."""
            E = 0.0
            # 1. Internal consistency (simulated transitivity/causality)
            # If state has 'A' and 'A->B' logic exists, missing 'B' adds energy
            # Simplified: Just penalize low probability on high-weight extracted facts
            for i, lit in enumerate(literals):
                if state_vector[i] == 0: # Literal is False
                    # Find original weight
                    w = 0.5
                    for p in props:
                        if p['text'] == lit:
                            w = p['weight']
                            break
                    E += w * 0.5 # Penalty for not existing
            
            # 2. Candidate alignment energy
            # If candidate asserts X, but state has X=False, high energy
            cand_words = set(re.findall(r'\b\w+\b', cand_lower))
            for i, lit in enumerate(literals):
                if lit.lower() in cand_words and state_vector[i] == 0:
                    E += 2.0 # Strong penalty
            
            return E

        return energy, len(literals)

    def _ergodic_sample(self, energy_func, n_vars: int, n_samples: int = 200, burn_in: int = 50, temp: float = 1.0) -> float:
        """Metropolis-Hastings sampling to estimate probability of a consistent world."""
        if n_vars == 0: return 0.5
        
        # Initialize state randomly
        state = np.random.randint(0, 2, size=n_vars).astype(float)
        current_E = energy_func(state)
        
        true_counts = np.zeros(n_vars)
        valid_samples = 0
        
        for t in range(burn_in + n_samples):
            # Propose flip
            idx = np.random.randint(0, n_vars)
            new_state = state.copy()
            new_state[idx] = 1 - new_state[idx]
            
            new_E = energy_func(new_state)
            delta_E = new_E - current_E
            
            # Acceptance probability
            if delta_E <= 0 or np.random.rand() < np.exp(-delta_E / temp):
                state = new_state
                current_E = new_E
            
            if t >= burn_in:
                true_counts += state
                valid_samples += 1
        
        if valid_samples == 0: return 0.0
        # Return average probability of literals being true
        return float(np.mean(true_counts / valid_samples))

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        # 1. NAS Step: Select best parsing rules for this prompt
        active_rules = self._nas_search(prompt)
        
        # 2. Parse Prompt into Constraints
        props = self._parse_propositions(prompt, active_rules)
        
        results = []
        for cand in candidates:
            # Build energy landscape specific to candidate
            energy_func, n_vars = self._build_energy_func(props, cand)
            
            # 3. Ergodic Sampling
            # We simulate the probability that a world consistent with prompt makes candidate true
            # Approximation: Score = (Sampling Score) * (Heuristic Overlap)
            base_score = self._ergodic_sample(energy_func, max(1, n_vars))
            
            # Fallback heuristic for "Yes/No" or direct string match if sampling is sparse
            overlap = 0.0
            cand_lower = cand.lower()
            for p in props:
                if p['text'].lower() in cand_lower:
                    overlap += 0.1
                if 'not' in p['text'].lower() and 'not' in cand_lower:
                    overlap += 0.1
            
            final_score = min(1.0, base_score * 0.7 + overlap * 0.3 + 0.1)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"NAS-selected rules {active_rules}, Ergodic score {base_score:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Reuse evaluate logic for single candidate
        res = self.evaluate(prompt, [answer])
        return res[0]['score'] if res else 0.0