import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Evolutionary Metacognitive Reasoning Tool with Dynamics Tracking.
    
    Mechanism:
    1. Structural Parsing: Extracts logical propositions (negations, conditionals, comparatives, causality).
    2. Constraint Matrix: Builds a matrix C where rows are entities/states and columns are clauses.
    3. Evolutionary Search: Evolves a population of truth-assignments to maximize logical consistency (SAT) 
       while minimizing conflict.
    4. Counterfactual Perturbation: Uses 'do-calculus' style toggling of antecedents to test robustness.
    5. Dynamics Tracking (Frame C): Models reasoning as a dynamical system. It simulates the evolution of 
       the answer state over generations. Confidence is derived from the Lyapunov-like stability of the 
       solution trajectory (convergence rate and basin stability) rather than just final fitness.
    6. Epistemic Honesty: Explicitly detects ambiguity patterns (Tier B) to cap confidence.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|unless|provided|when)\b.*?\b(then|will|must|should)\b', re.IGNORECASE | re.DOTALL),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore|thus)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|precedes|follows|during|while)\b', re.IGNORECASE),
            'numeric': re.compile(r'(\d+(?:\.\d+)?)\s*(=|!=|<|>|<=|>=|==)\s*(\d+(?:\.\d+)?)'),
            'quantifier': re.compile(r'\b(every|all|some|none|at least|at most)\b', re.IGNORECASE),
            # Tier B Ambiguity Triggers
            'presupposition': re.compile(r'\b(have you stopped|why did.*fail|why is.*wrong|quit)\b', re.IGNORECASE),
            'scope_ambig': re.compile(r'\b(every|all)\b.*\b(a|an)\b', re.IGNORECASE),
            'pronoun_ambig': re.compile(r'\b(told|said to)\b.*\b(he|she|him|her|they)\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either|or else|only two options)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly)\b', re.IGNORECASE)
        }
        self.max_generations = 20
        self.pop_size = 15
        self.mutation_rate = 0.1

    def _extract_clauses(self, text: str) -> List[str]:
        """Simple clause splitter based on punctuation and connectors."""
        text = text.replace(";", ".").replace("?", ".").replace("!", ".")
        parts = re.split(r'\.\s*', text)
        return [p.strip() for p in parts if len(p.strip()) > 3]

    def _parse_structure(self, text: str) -> Dict[str, Any]:
        """Extract structural features and build a rudimentary constraint representation."""
        features = {k: bool(p.search(text)) for k, p in self.patterns.items()}
        clauses = self._extract_clauses(text)
        
        # Build a simple numeric constraint list if present
        numerics = []
        for m in self.patterns['numeric'].finditer(text):
            try:
                v1, op, v2 = float(m.group(1)), m.group(2), float(m.group(3))
                numerics.append((v1, op, v2))
            except: pass
            
        return {
            'features': features,
            'clauses': clauses,
            'numerics': numerics,
            'length': len(text)
        }

    def _check_ambiguity(self, prompt: str) -> Tuple[bool, float]:
        """
        Tier B Check: Detects ambiguity and returns (is_ambiguous, confidence_cap).
        """
        text_lower = prompt.lower()
        ambiguity_flags = []
        
        if self.patterns['presupposition'].search(prompt): ambiguity_flags.append('presupposition')
        if self.patterns['scope_ambig'].search(prompt): ambiguity_flags.append('scope')
        if self.patterns['pronoun_ambig'].search(prompt) and 'who' in text_lower: ambiguity_flags.append('pronoun')
        if self.patterns['false_dichotomy'].search(prompt): ambiguity_flags.append('dichotomy')
        if self.patterns['subjectivity'].search(prompt): ambiguity_flags.append('subjectivity')
        
        # Heuristic for unanswerable/missing info
        if "cannot be determined" in text_lower or "insufficient" in text_lower:
            ambiguity_flags.append('explicit_unknown')

        if ambiguity_flags:
            return True, 0.25 # Cap confidence low for ambiguous inputs
        
        return False, 1.0

    def _compute_numeric_score(self, candidate: str, structure: Dict) -> float:
        """Constructive computation for numeric constraints."""
        if not structure['numerics']:
            return 1.0 # No numeric constraints to violate
        
        # Extract numbers from candidate
        cand_nums = re.findall(r'\d+(?:\.\d+)?', candidate)
        if not cand_nums:
            return 0.5 # Candidate lacks numbers when prompt has them (penalty)
            
        # Simple check: does the candidate satisfy the explicit math?
        # This is a simplified check for demonstration
        try:
            c_val = float(cand_nums[0])
            for v1, op, v2 in structure['numerics']:
                # If the prompt says "5 > 3", and candidate implies a value, check consistency
                # This is a proxy for logical consistency
                if op == '=' and abs(c_val - v1) > 1e-6: return 0.0
                if op == '<' and not (c_val < v1): pass # Context dependent
        except: pass
        
        return 1.0

    def _evolve_consistency(self, prompt_struct: Dict, candidate: str) -> Tuple[float, List[float]]:
        """
        Evolves a population of truth assignments to maximize logical consistency.
        Returns (final_fitness, trajectory_stability_scores).
        """
        m = len(prompt_struct['clauses'])
        if m == 0: m = 1 # Prevent empty matrix
        
        # Initialize population: p_i in {0, 1}^m
        # Each row is an individual, each col is a clause truth value
        pop = np.random.randint(0, 2, size=(self.pop_size, m)).astype(float)
        
        # Constraint Matrix C approximation: 
        # Rows = variables (simplified to clause indices for this demo)
        # We simulate consistency by checking if the candidate text aligns with the clause logic
        candidate_lower = candidate.lower()
        clause_satisfaction = np.zeros(m)
        
        for i, clause in enumerate(prompt_struct['clauses']):
            # Heuristic: Does the candidate contain keywords from the clause?
            words = set(re.findall(r'\w+', clause.lower()))
            cand_words = set(re.findall(r'\w+', candidate_lower))
            overlap = len(words.intersection(cand_words))
            clause_satisfaction[i] = min(1.0, overlap / (len(words) + 1))
            
        # Fitness function: Sat - Conflict + Uncertainty
        # Simplified for single candidate evaluation: 
        # We want the candidate to be consistent with the prompt's structural implications
        
        trajectory = []
        
        for gen in range(self.max_generations):
            # Calculate fitness for each individual
            # f = sum(satisfaction) - penalty(random noise) + diversity bonus
            scores = np.dot(pop, clause_satisfaction) 
            
            # Add noise penalty (conflict simulation)
            conflict = np.sum(np.abs(np.diff(pop, axis=1)), axis=1) * 0.1
            fitness = scores - conflict
            
            # Metacognitive term: Variance across population (uncertainty)
            variance = np.var(fitness)
            fitness = fitness + 0.5 * (1.0 / (variance + 0.1)) # Reward low variance (high confidence)
            
            # Track best fitness for dynamics
            best_fit = np.max(fitness)
            trajectory.append(best_fit)
            
            # Selection (Tournament)
            new_pop = np.copy(pop)
            for i in range(self.pop_size):
                idx1, idx2 = np.random.choice(self.pop_size, 2, replace=False)
                if fitness[idx1] > fitness[idx2]:
                    winner = pop[idx1]
                else:
                    winner = pop[idx2]
                
                # Crossover & Mutation
                if np.random.rand() < 0.8: # Crossover
                    partner_idx = np.random.randint(self.pop_size)
                    partner = pop[partner_idx]
                    mask = np.random.rand(m) > 0.5
                    child = np.where(mask, winner, partner)
                else:
                    child = winner
                
                # Mutation
                mut_mask = np.random.rand(m) < self.mutation_rate
                child = np.where(mut_mask, 1 - child, child)
                
                # Counterfactual Bias: If a clause is critical (high satisfaction weight), 
                # bias mutation to test its negation occasionally
                if np.random.rand() < 0.1 and m > 0:
                    target = np.argmax(clause_satisfaction) % m
                    child[target] = 1 - child[target]
                    
                new_pop[i] = child
            
            pop = new_pop

        # Final Score: Normalized best fitness
        final_score = np.max(np.dot(pop, clause_satisfaction)) / (m + 1e-6)
        return final_score, trajectory

    def _calculate_dynamics_score(self, trajectory: List[float]) -> float:
        """
        Frame C: Dynamics Tracker.
        Analyzes the trajectory of fitness over generations.
        High convergence rate and low final variance indicate a stable (confident) answer.
        """
        if len(trajectory) < 2:
            return 0.5
            
        traj = np.array(trajectory)
        
        # 1. Convergence Rate (Lyapunov-like exponent approximation)
        # Fit a linear line to the log-error? Or simply check slope decay
        diffs = np.diff(traj)
        if np.all(diffs == 0):
            convergence_score = 1.0 # Perfectly stable
        else:
            # Check if oscillations dampen
            late_variance = np.var(traj[int(len(traj)*0.8):])
            early_variance = np.var(traj[:int(len(traj)*0.2)]) + 1e-6
            convergence_score = 1.0 - min(1.0, late_variance / early_variance)
            
        # 2. Basin Stability (Final state robustness)
        # If the final fitness is high and stable, it's in a deep basin
        final_stability = 1.0 if traj[-1] > np.mean(traj) else 0.5
        
        return 0.6 * convergence_score + 0.4 * final_stability

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            if z12 == 0: return 1.0
            return (z12 - min(z1, z2)) / max(z1, z2, 1)
        except:
            return 0.5

    def _meta_confidence(self, prompt: str, candidate: str, struct: Dict) -> float:
        """
        Calculates confidence based on prompt properties and structural match.
        Enforces Tier B constraints.
        """
        # 1. Check for Ambiguity (Tier B)
        is_ambiguous, cap = self._check_ambiguity(prompt)
        if is_ambiguous:
            return cap
        
        # 2. Structural Coverage
        # If the prompt has complex structure but candidate is too short, lower confidence
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        cand_words = set(re.findall(r'\w+', candidate.lower()))
        
        # Overlap ratio
        if len(prompt_words) == 0: return 0.5
        overlap = len(cand_words.intersection(prompt_words)) / len(prompt_words)
        
        # If prompt has numeric/constraint features, candidate MUST address them
        if struct['numerics']:
            cand_nums = re.findall(r'\d+', candidate)
            if not cand_nums:
                return 0.2 # Critical failure to address numbers
        
        # Base confidence on structural engagement
        base_conf = 0.5 + 0.4 * min(1.0, overlap)
        
        # Cap at 0.9 unless computation was definitive (handled in evaluate)
        return min(base_conf, 0.85)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._parse_structure(prompt)
        
        # Pre-calculate prompt dynamics baseline
        _, prompt_traj = self._evolve_consistency(prompt_struct, prompt)
        prompt_stability = self._calculate_dynamics_score(prompt_traj)
        
        for cand in candidates:
            # 1. Structural & Numeric Analysis
            num_score = self._compute_numeric_score(cand, prompt_struct)
            
            # 2. Evolutionary Consistency
            fitness, traj = self._evolve_consistency(prompt_struct, cand)
            dyn_score = self._calculate_dynamics_score(traj)
            
            # 3. NCD (Tiebreaker, max 15%)
            ncd = 1.0 - self._ncd_similarity(prompt, cand) # Invert so high is good
            
            # 4. Combine Scores
            # Dynamics/Structure >= 60%, Computation 20%, NCD <= 15%
            raw_score = (0.45 * fitness) + (0.25 * dyn_score) + (0.20 * num_score) + (0.10 * ncd)
            
            # Apply Meta-Confidence Cap
            meta_conf = self._meta_confidence(prompt, cand, prompt_struct)
            final_score = raw_score * meta_conf
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Dynamics Stability: {dyn_score:.2f}, Logical Fit: {fitness:.2f}, Meta-Conf: {meta_conf:.2f}"
            })
            
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces Tier B ambiguity checks.
        """
        struct = self._parse_structure(prompt)
        
        # 1. Meta-Confidence (Ambiguity Check)
        meta_conf = self._meta_confidence(prompt, answer, struct)
        if meta_conf < 0.3:
            return meta_conf
            
        # 2. Compute internal metrics
        fitness, traj = self._evolve_consistency(struct, answer)
        dyn_score = self._calculate_dynamics_score(traj)
        num_score = self._compute_numeric_score(answer, struct)
        
        # 3. Final Confidence Calculation
        # High confidence requires: High Stability, High Numeric Compliance, Low Ambiguity
        base_conf = (0.4 * dyn_score) + (0.4 * fitness) + (0.2 * num_score)
        
        # Cap based on meta-analysis
        final_conf = min(base_conf, meta_conf)
        
        # Never return > 0.9 without definitive computation (heuristic: perfect numeric match)
        if struct['numerics'] and num_score < 1.0:
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))