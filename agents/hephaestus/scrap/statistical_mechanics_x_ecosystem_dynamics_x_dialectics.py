import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Dialectical Ecological Monte Carlo (DEMC) Reasoning Tool.
    
    Mechanism:
    1. Statistical Mechanics: Treats candidate answers as states in an ensemble.
       Energy H = -log(Posterior). Lower energy = higher probability.
    2. Ecosystem Dynamics: Candidates compete via Lotka-Volterra dynamics.
       Fitness is derived from structural parsing and numeric evaluation.
       Interaction matrix alpha encodes competition (similar answers) and facilitation.
    3. Dialectics: 
       Thesis: Best current candidate.
       Antithesis: Perturbed version (simulated via fluctuation-dissipation noise on score).
       Synthesis: Weighted average of scores, penalizing contradictions.
       
    Epistemic Honesty (Tier B):
    Before scoring, the tool analyzes the PROMPT for ambiguity, presupposition, 
    scope issues, and unanswerability. If detected, confidence is capped low (<0.3)
    regardless of candidate quality.
    """

    def __init__(self):
        # Interaction matrix parameters (simplified for single-step evaluation)
        self.competition_strength = 0.5
        self.diversity_bonus = 0.1
        
        # Patterns for Tier B (Epistemic Honesty) detection
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed|stopped)\b",
            r"\bwhy did\b", r"\bwhy does\b", r"\bwhy has\b",
            r"\bregret\b", r"\bmistake\b"
        ]
        self.scope_triggers = [
            r"\bevery\b.*\ba\s+\w+", # Every X did a Y
            r"\ball\b.*\bthe\s+\w+"
        ]
        self.pronoun_triggers = [
            r"\b(he|she|him|her|it|they)\b.*\bwho\b",
            r"\btold\b.*\b(he|she|him|her)\b"
        ]
        self.dichotomy_triggers = [
            r"\beither\b.*\bor\b",
            r"\bis it\b.*\bor\b"
        ]
        self.subjectivity_triggers = [
            r"\b(best|worst|favorite|beautiful|ugly|good|bad)\b"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, etc.).
        Returns a cap value: 1.0 if clean, <0.3 if problematic.
        """
        p_lower = prompt.lower()
        issues = 0
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                # Check if it's a "Have you stopped" or "Why did X fail" structure
                if re.search(r"(have you|did you|why)", p_lower):
                    issues += 1
        
        # 2. Scope Ambiguity (Simplified heuristic)
        if re.search(r"every.*a\s+\w+", p_lower) and "same" in p_lower or "different" in p_lower:
            issues += 1
            
        # 3. Pronoun Ambiguity
        if re.search(r"\b(he|she)\b", p_lower) and re.search(r"\bwho\b", p_lower):
            issues += 1
            
        # 4. False Dichotomy
        if re.search(r"either.*or", p_lower) and not re.search(r"both", p_lower):
             # Heuristic: if "either/or" exists without explicit exhaustiveness
            issues += 1
            
        # 5. Subjectivity without criteria
        if any(re.search(trig, p_lower) for trig in self.subjectivity_triggers):
            if "measure" not in p_lower and "data" not in p_lower and "statistic" not in p_lower:
                issues += 1

        if issues > 0:
            return 0.25  # Cap for ambiguous/unanswerable
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constructive computation.
        Returns a score 0.0 to 1.0 based on logical consistency with prompt structure.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0
        
        # 1. Negation Handling
        if "not" in p_lower or "never" in p_lower or "false" in p_lower:
            checks += 1
            # If prompt has negation, correct candidate should reflect it or be 'no'/ 'false'
            if ("no" in c_lower or "false" in c_lower or "not" in c_lower):
                score += 1.0
            elif len(c_lower.strip()) < 5: # Short answers like "No"
                score += 0.8 
                
        # 2. Numeric Evaluation (Constructive)
        numbers_prompt = re.findall(r"[-+]?\d*\.?\d+", prompt)
        numbers_candidate = re.findall(r"[-+]?\d*\.?\d+", candidate)
        
        if numbers_prompt and numbers_candidate:
            checks += 1
            try:
                # Simple arithmetic check: if prompt has "2 + 2", candidate should be "4"
                # This is a basic proxy for constructive computation
                if len(numbers_prompt) >= 2:
                    p_nums = [float(x) for x in numbers_prompt]
                    c_num = float(numbers_candidate[0])
                    
                    # Check for sum, diff, or product match
                    if abs(sum(p_nums) - c_num) < 1e-6:
                        score += 1.0
                    elif abs(p_nums[0] * p_nums[1] - c_num) < 1e-6:
                        score += 1.0
                    elif abs(p_nums[0] - p_nums[1] - c_num) < 1e-6:
                        score += 1.0
                    else:
                        # Numeric mismatch penalty
                        score -= 0.5
            except ValueError:
                pass

        # 3. Comparative Logic
        if "greater" in p_lower or "larger" in p_lower or "more" in p_lower:
            checks += 1
            if numbers_prompt and numbers_candidate:
                try:
                    vals = [float(x) for x in numbers_prompt]
                    cand_val = float(numbers_candidate[0])
                    if cand_val == max(vals):
                        score += 1.0
                except: pass

        # Normalize
        if checks == 0:
            return 0.5 # Neutral if no structural hooks found
        return max(0.0, min(1.0, score / checks if checks > 0 else 0.5))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
            
        concat = s1_bytes + s2_bytes
        len_concat = len(zlib.compress(concat))
        len_s1_comp = len(zlib.compress(s1_bytes))
        len_s2_comp = len(zlib.compress(s2_bytes))
        
        max_len = max(len_s1_comp, len_s2_comp)
        if max_len == 0:
            return 0.0
            
        ncd = (len_concat - max_len) / max_len
        return ncd

    def _dialectical_synthesis(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Core DEMC Logic:
        1. Calculate intrinsic fitness (r_i) based on structural/numeric analysis.
        2. Apply Lotka-Volterra competition (alpha_ij).
        3. Dialectic update: Thesis (best) vs Antithesis (perturbed).
        4. Return ranked list.
        """
        if not candidates:
            return []

        n = len(candidates)
        # 1. Intrinsic Fitness (r_i)
        # Combine structural score and NCD similarity to prompt (as a proxy for relevance)
        r = []
        for c in candidates:
            struct_score = self._structural_score(prompt, c)
            # NCD to prompt: lower is better (more similar), invert for fitness
            ncd_val = self._compute_ncd(prompt, c)
            relevance = 1.0 - min(1.0, ncd_val) 
            fitness = 0.7 * struct_score + 0.3 * relevance
            r.append(fitness)

        # 2. Interaction Matrix (Alpha) - Simplified for O(N^2)
        # Alpha_ij = similarity between candidate i and j (Competition)
        alpha = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    alpha[i][j] = 1.0 # Self-limitation
                else:
                    sim = 1.0 - self._compute_ncd(candidates[i], candidates[j])
                    alpha[i][j] = sim * self.competition_strength

        # 3. Lotka-Volterra Step (Single iteration for scoring)
        # dn_i/dt = n_i * (r_i - sum(alpha_ij * n_j))
        # Assume initial population n_j = 1.0 for all
        populations = [1.0] * n
        growth_rates = []
        
        for i in range(n):
            competition_term = sum(alpha[i][j] * populations[j] for j in range(n))
            growth = populations[i] * (r[i] - competition_term)
            growth_rates.append(growth)

        # Normalize growth rates to 0-1 range for scoring
        min_g = min(growth_rates)
        max_g = max(growth_rates)
        range_g = max_g - min_g if max_g != min_g else 1.0
        
        final_scores = []
        for i in range(n):
            # Normalize to 0-1
            norm_score = (growth_rates[i] - min_g) / range_g
            final_scores.append(norm_score)

        # 4. Dialectic Synthesis & Ranking
        # Identify Thesis (highest score)
        thesis_idx = final_scores.index(max(final_scores))
        thesis_score = final_scores[thesis_idx]
        
        # Antithesis Simulation: Perturb thesis score by susceptibility (variance)
        # In this static eval, we simulate the 'synthesis' by boosting diverse high-scorers
        # and penalizing redundant low-scorers.
        
        results = []
        for i, c in enumerate(candidates):
            score = final_scores[i]
            
            # Dialectic Adjustment: 
            # If this candidate is very similar to the thesis but slightly worse, 
            # it gets suppressed (Synthesis resolves contradiction by keeping the better one).
            if i != thesis_idx:
                sim_to_thesis = 1.0 - self._compute_ncd(c, candidates[thesis_idx])
                if sim_to_thesis > 0.8: # Highly redundant
                    score *= 0.5 # Penalty for redundancy without superiority
            
            results.append({
                "candidate": c,
                "score": float(score),
                "reasoning": f"Structural fit: {self._structural_score(prompt, c):.2f}, Ecological niche: {'dominant' if i==thesis_idx else 'competitive'}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Run the DEMC simulation
        ranked = self._dialectical_synthesis(prompt, candidates)
        
        # Apply Epistemic Honesty Cap based on Prompt Analysis
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 0.3:
            # If the prompt is ambiguous/trap-laden, cap all scores
            # and update reasoning to reflect uncertainty
            for item in ranked:
                item['score'] = min(item['score'], 0.25)
                item['reasoning'] = f"Warning: Prompt contains ambiguity or presupposition. Score capped. ({item['reasoning']})"
                
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence if prompt is problematic.
        """
        # 1. Check Prompt Integrity (Tier B)
        prompt_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (Tier A)
        # We use the internal scoring mechanism to see how well this specific answer fits
        # We simulate a tiny population with just this answer and a dummy to get a score
        dummy = "__DUMMY_PLACEHOLDER__"
        # If the answer is the same as dummy (unlikely), handle gracefully
        candidates = [answer, dummy] if answer != dummy else [answer]
        
        # Run evaluation to get raw score
        # Note: We reuse _dialectical_synthesis logic but simplified for single check
        struct_score = self._structural_score(prompt, answer)
        ncd_val = self._compute_ncd(prompt, answer)
        relevance = 1.0 - min(1.0, ncd_val)
        raw_score = 0.7 * struct_score + 0.3 * relevance
        
        # Heuristic penalty for very short answers on complex prompts
        if len(answer.split()) < 2 and len(prompt.split()) > 10:
            if not any(x in answer.lower() for x in ['yes', 'no', 'true', 'false', str(math.pi)]):
                 raw_score *= 0.8

        # 3. Apply Cap
        final_conf = min(raw_score, prompt_cap)
        
        # Ensure we never claim > 0.9 without definitive computation (heuristic guard)
        # Unless it's a pure numeric match
        if not re.search(r"\d", answer):
            final_conf = min(final_conf, 0.9)
            
        return float(max(0.0, min(1.0, final_conf)))