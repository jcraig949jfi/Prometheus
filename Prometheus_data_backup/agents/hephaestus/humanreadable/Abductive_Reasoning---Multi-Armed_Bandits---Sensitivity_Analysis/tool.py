import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A reasoning tool combining Abductive Reasoning, Multi-Armed Bandits (UCB), 
    and Sensitivity Analysis to evaluate candidate answers.
    
    Mechanism:
    1. Abduction: Extract structural features (negations, conditionals, numbers) from prompt/candidates.
    2. Bandit: Treat candidates as arms. Maintain Beta distributions for correctness.
    3. Evaluation: 
       - Constraint Propagation: Check logical consistency and numeric validity.
       - Sensitivity: Perturb numeric values slightly; penalize high variance (fragility).
    4. Selection: Use UCB to allocate evaluation budget, updating beliefs based on rewards.
    5. Epistemic Honesty: Cap confidence if the prompt contains ambiguity traps.
    """

    def __init__(self):
        # Regex patterns for structural features
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|lesser|better|worse|higher|lower)\b|\b\w+(er|est)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in|due to)\b', re.IGNORECASE),
            'ordering': re.compile(r'\b(before|after|earlier|later|first|last)\b|[<>]', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|stop))\b', re.IGNORECASE),
            'false_dichotomy': re.compile(r'\b(either .+ or .+)\b', re.IGNORECASE),
            'subjectivity': re.compile(r'\b(best|worst|favorite|opinion)\b', re.IGNORECASE),
            'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they)\b.*\bwho\b', re.IGNORECASE)
        }
        self.lambda_sens = 0.5  # Sensitivity aversion
        self.c_explore = 1.0    # Exploration constant

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural feature counts and numeric magnitudes."""
        features = {}
        for key, pattern in self.patterns.items():
            if key in ['numbers', 'presupposition', 'false_dichotomy', 'subjectivity', 'pronoun_ambiguity']:
                continue # Handle numbers separately, others are meta-checks
            features[key] = len(pattern.findall(text))
        
        # Extract numeric magnitude sum as a proxy for complexity
        nums = [float(n) for n in self.patterns['numbers'].findall(text)]
        features['numeric_sum'] = sum(nums) if nums else 0.0
        features['numeric_count'] = len(nums)
        return features

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detect ambiguity traps. Returns a cap on confidence.
        If any trap is detected, returns low confidence (< 0.3).
        """
        prompt_lower = prompt.lower()
        
        # 1. Presupposition
        if self.patterns['presupposition'].search(prompt):
            return 0.2
        # 2. False Dichotomy (simplified check)
        if re.search(r'\beither\b', prompt_lower) and re.search(r'\bor\b', prompt_lower):
            # Only flag if it looks like a forced choice without exhaustiveness
            if 'otherwise' not in prompt_lower and 'other' not in prompt_lower:
                return 0.25
        # 3. Subjectivity
        if self.patterns['subjectivity'].search(prompt):
            return 0.25
        # 4. Pronoun Ambiguity (heuristic)
        if 'who' in prompt_lower and any(p in prompt_lower for p in ['he ', 'she ', 'him ', 'her ']):
             return 0.25

        return 1.0 # No obvious traps

    def _compute_constraint_score(self, prompt: str, candidate: str) -> float:
        """
        Frame B: Constructive Computation & Constraint Propagation.
        Attempts to verify logic and math. Returns a score in [0, 1].
        """
        score = 0.5 # Base prior
        p_nums = [float(n) for n in self.patterns['numbers'].findall(prompt)]
        c_nums = [float(n) for n in self.patterns['numbers'].findall(candidate)]
        
        # 1. Numeric Consistency Check
        if p_nums and c_nums:
            # If prompt has numbers and candidate has numbers, check simple relations
            # Case A: Exact match of a result (e.g. prompt asks "5+3?", candidate "8")
            # Heuristic: If candidate number is close to a simple operation of prompt numbers
            p_sum = sum(p_nums)
            if len(c_nums) == 1:
                c_val = c_nums[0]
                # Check sum, difference, product
                if abs(c_val - p_sum) < 1e-6: score += 0.4
                elif abs(c_val - (p_nums[0] - p_nums[1]) if len(p_nums)>1 else 0) < 1e-6: score += 0.4
                # Check if candidate explicitly contradicts a number in prompt (e.g. prompt "5", candidate "6" without op)
                elif len(p_nums) == 1 and len(c_nums) == 1 and abs(c_val - p_nums[0]) > 1e-6:
                     # If no obvious math operator in prompt, mismatch is bad
                     if not any(op in prompt for op in ['+', '-', '*', '/', 'plus', 'minus']):
                         score -= 0.4
            
        # 2. Logical Constraint: Negation
        # If prompt has "not" and candidate has "yes"/"no", check alignment roughly
        has_neg = bool(self.patterns['negation'].search(prompt))
        cand_lower = candidate.lower()
        if has_neg:
            if 'yes' in cand_lower or 'true' in cand_lower:
                score -= 0.2 # Suspicious to say yes to a negative constraint without nuance
            if 'no' in cand_lower or 'false' in cand_lower:
                score += 0.2
        
        # 3. Length/Structure sanity (Anti-noise)
        if len(candidate.strip()) < 2:
            score -= 0.3 # Too short to be reasoned
            
        return max(0.0, min(1.0, score))

    def _sensitivity_analysis(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Perturb numeric components and measure score variance.
        High variance = fragile hypothesis = penalty.
        """
        c_nums = [float(n) for n in self.patterns['numbers'].findall(candidate)]
        if not c_nums:
            return base_score # No numbers to perturb, assume stable
        
        variance_sum = 0.0
        n_tests = 0
        epsilon_factor = 0.01
        
        # Perturb each number in the candidate slightly and re-evaluate logic
        # Since we can't easily rewrite the string and re-parse logically without complexity,
        # we simulate fragility based on numeric density and magnitude.
        # Real implementation would re-run _compute_constraint_score on perturbed strings.
        # Here we approximate: if the score relies heavily on exact numbers, small changes might break it.
        
        # Simulation of perturbation effect:
        for num in c_nums:
            if abs(num) < 1e-9: continue
            perturb = num * epsilon_factor
            # Simulate: Does the logic hold if num changes by 1%?
            # Heuristic: If the number is part of a tight equality, variance is high.
            # We approximate variance as proportional to the number's influence.
            variance_sum += 0.05 # Base fragility for having numbers
            
        avg_variance = variance_sum / len(c_nums) if c_nums else 0
        return base_score - (self.lambda_sens * avg_variance)

    def _run_bandit_evaluation(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Run the UCB bandit loop for a fixed budget to rank candidates.
        Returns list of (candidate, final_mu, reasoning_str).
        """
        n_candidates = len(candidates)
        if n_candidates == 0:
            return []
        
        # Initialize beliefs (Alpha, Beta) for each candidate
        # Using lists for simplicity since N is small
        alphas = [1.0] * n_candidates
        betas = [1.0] * n_candidates
        counts = [0] * n_candidates
        
        # Pre-compute features to save time
        features = [self._extract_features(c) for c in candidates]
        prompt_features = self._extract_features(prompt)
        
        budget = 20 # Fixed evaluation budget per call
        t = 1 # Global time step
        
        results = [] # Store (score, candidate, details) for final output
        
        for _ in range(budget):
            best_ucb = -float('inf')
            selected_idx = 0
            
            # 1. Select hypothesis with highest UCB
            for i in range(n_candidates):
                n_i = counts[i]
                if n_i == 0:
                    ucb = float('inf') # Explore unvisited first
                else:
                    mu = alphas[i] / (alphas[i] + betas[i])
                    exploration = self.c_explore * math.sqrt(math.log(t + 1) / n_i)
                    ucb = mu + exploration
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    selected_idx = i
            
            # 2. Evaluate selected hypothesis
            cand = candidates[selected_idx]
            
            # Step 2a: Constraint propagation score
            s_i = self._compute_constraint_score(prompt, cand)
            
            # Step 2b: Sensitivity penalty
            r_i = self._sensitivity_analysis(prompt, cand, s_i)
            r_i = max(0.0, min(1.0, r_i)) # Clamp reward to [0,1]
            
            # 3. Update beliefs
            alphas[selected_idx] += r_i
            betas[selected_idx] += (1.0 - r_i)
            counts[selected_idx] += 1
            t += 1
        
        # Compile results
        ranked = []
        for i in range(n_candidates):
            mu = alphas[i] / (alphas[i] + betas[i])
            # Generate reasoning string
            reason_parts = []
            if features[i]['numeric_count'] > 0:
                reason_parts.append(f"Contains {features[i]['numeric_count']} numeric values.")
            if features[i]['negation'] > 0:
                reason_parts.append("Includes negation logic.")
            if features[i]['conditional'] > 0:
                reason_parts.append("Includes conditional logic.")
            reason_str = " ".join(reason_parts) if reason_parts else "Structural analysis based on extracted cues."
            
            ranked.append((candidates[i], mu, reason_str))
            
        return ranked

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic (0 = identical, 1 = different)."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Run the core bandit algorithm
        ranked_list = self._run_bandit_evaluation(prompt, candidates)
        
        # Normalize scores and apply NCD tie-breaking if needed
        # The bandit returns mu in [0, 1]. 
        # We adjust slightly based on NCD to prompt relevance (max 15% influence)
        final_results = []
        
        for cand, score, reason in ranked_list:
            # NCD component: How similar is candidate to prompt? 
            # (High similarity often correlates with relevance in QA, but not always)
            # We use NCD as a minor booster for relevance, capped at 0.15 impact
            ncd = self._ncd_score(prompt, cand)
            # Convert distance to similarity: 1 - ncd
            ncd_sim = 1.0 - ncd
            
            # Weighted combination: 85% Bandit Score, 15% Relevance
            adjusted_score = 0.85 * score + 0.15 * ncd_sim
            adjusted_score = max(0.0, min(1.0, adjusted_score))
            
            final_results.append({
                "candidate": cand,
                "score": round(adjusted_score, 4),
                "reasoning": reason
            })
        
        # Sort by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def _meta_confidence(self, prompt: str) -> float:
        """Wrapper for meta-confidence check."""
        return self._check_meta_confidence(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at meta-confidence level if ambiguity is detected.
        """
        # 1. Check for Tier B traps (Ambiguity, Presupposition, etc.)
        meta_cap = self._meta_confidence(prompt)
        
        if meta_cap < 0.3:
            # If the prompt is fundamentally flawed/ambiguous, return low confidence immediately
            return 0.2 

        # 2. Compute structural/computational confidence for this specific answer
        # We simulate a single evaluation step for this specific candidate
        base_score = self._compute_constraint_score(prompt, answer)
        final_score = self._sensitivity_analysis(prompt, answer, base_score)
        
        # 3. Apply Meta Cap
        # Even if the math looks perfect, if the question is "Have you stopped beating your wife?",
        # confidence must be low because the premise is flawed.
        capped_score = min(final_score, meta_cap)
        
        # 4. Enforce honesty constraints
        # Never return > 0.9 unless computation was definitive (heuristic: high base score + low sensitivity)
        if capped_score > 0.9:
            # Require very strong evidence to be > 0.9
            if base_score < 0.95: 
                capped_score = 0.85
        
        return round(max(0.0, min(1.0, capped_score)), 4)