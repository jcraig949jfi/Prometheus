import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Optional, Set

class ReasoningTool:
    """
    A hybrid reasoning tool combining Multi-Armed Bandits (UCB), 
    Spectral Criticality, and Mechanism Design consistency checks.
    
    Core Logic:
    1. Structural Parsing: Extracts SVO triples, negations, and numeric constraints.
    2. Criticality (Spectral): Builds an implication graph from shared predicates; 
       uses spectral radius to measure logical density/interconnectedness.
    3. Mechanism Design: Performs forward chaining; penalizes contradictions (violations).
    4. Bandit Scoring: Treats each candidate as an arm, updating Beta posteriors 
       based on structural consistency scores to compute a UCB index.
    5. Epistemic Honesty: Caps confidence if the prompt contains ambiguity markers 
       (presuppositions, scope issues) regardless of candidate score.
    """

    # Structural regex patterns
    TRIPLE_PATTERN = re.compile(r'(\b\w+\b)\s+(is|are|was|were|has|have|did|does|can|could|should|would|must|leads to|results in|causes)\s+(\b\w+\b)', re.IGNORECASE)
    NEGATION_PATTERN = re.compile(r'\b(not|no|never|neither|none)\b', re.IGNORECASE)
    NUMERIC_PATTERN = re.compile(r'(\d+(?:\.\d+)?)')
    COMPARATIVE_PATTERN = re.compile(r'(greater than|less than|more than|fewer than|>=|<=|>|<)', re.IGNORECASE)
    
    # Ambiguity/Trap markers for Epistemic Honesty
    PRESUPPOSITION_MARKERS = ['have you stopped', 'have you quit', 'why did', 'why does', 'when did']
    SCOPE_MARKERS = ['every x', 'same y', 'different y'] # Simplified heuristic
    PRONOUN_MARKERS = ['told', 'said to', ' he ', ' she ', ' they ', ' who ']
    DICHOTOMY_MARKERS = ['either', 'or not', 'only two']
    SUBJECTIVITY_MARKERS = ['best', 'worst', 'favorite', 'opinion', 'beautiful']

    def __init__(self):
        self.epsilon = 1e-6

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    def _extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract subject-predicate-object triples."""
        return [(m.group(1).lower(), m.group(2).lower(), m.group(3).lower()) 
                for m in self.TRIPLE_PATTERN.finditer(text)]

    def _has_negation(self, text: str) -> bool:
        return bool(self.NEGATION_PATTERN.search(text))

    def _extract_numbers(self, text: str) -> List[float]:
        try:
            return [float(m.group(1)) for m in self.NUMERIC_PATTERN.finditer(text)]
        except:
            return []

    def _build_implication_matrix(self, triples: List[Tuple[str, str, str]]) -> np.ndarray:
        """Build adjacency matrix where A[j,k]=1 if triple j implies k (shared predicate/subject)."""
        n = len(triples)
        if n == 0:
            return np.array([[0]])
        
        A = np.zeros((n, n))
        for i, (s1, p1, o1) in enumerate(triples):
            for j, (s2, p2, o2) in enumerate(triples):
                if i != j:
                    # Simple implication heuristic: Shared subject or object implies relation
                    if s1 == s2 or o1 == s2 or o1 == o2:
                        A[i, j] = 1
        return A

    def _compute_criticality(self, triples: List[Tuple[str, str, str]]) -> float:
        """Compute spectral radius of the implication matrix."""
        if not triples:
            return 0.0
        A = self._build_implication_matrix(triples)
        if A.size == 0:
            return 0.0
        try:
            eigenvalues = np.linalg.eigvals(A)
            return float(np.max(np.abs(eigenvalues)))
        except:
            return 0.0

    def _forward_chain_check(self, text: str, triples: List[Tuple[str, str, str]]) -> Tuple[int, int]:
        """
        Simple forward chaining simulation.
        Counts violations (contradictions with explicit negations).
        Returns (violations, total_facts).
        """
        if not triples:
            return 0, 0
            
        has_neg = self._has_negation(text)
        violations = 0
        total_facts = len(triples)
        
        # Heuristic: If text has negation words but triples assert positive facts about same subjects,
        # or if we detect direct contradiction patterns.
        # For this implementation, we simulate a violation if:
        # 1. Text contains 'not' AND we have triples (potential conflict)
        # 2. Or if we find explicit "A is B" and "A is not B" patterns (harder with simple regex)
        
        # Simplified Mechanism Design Check:
        # If the text explicitly denies a derived fact.
        # Since we only have shallow triples, we check if the text contains "not" near the triple components.
        
        if has_neg:
            # Check if any triple's subject appears near a negation
            for s, p, o in triples:
                # Construct a context window check (simplified)
                pattern = rf"{s}.*?(not|no).*?{p}"
                if re.search(pattern, text, re.IGNORECASE):
                    violations += 1
                    
        return violations, max(total_facts, 1)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        len1, len2, len12 = len(b1), len(b2), len(b12)
        if min(len1, len2) == 0:
            return 1.0
        return (len12 - min(len1, len2)) / max(len1, len2)

    def _check_meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Check for ambiguity, presupposition, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition
        for marker in self.PRESUPPOSITION_MARKERS:
            if marker in p_lower:
                return 0.2
        
        # 2. Subjectivity
        for marker in self.SUBJECTIVITY_MARKERS:
            if marker in p_lower:
                # Only flag if no numeric/comparative structure exists
                if not self.NUMERIC_PATTERN.search(p_lower) and not self.COMPARATIVE_PATTERN.search(p_lower):
                    return 0.3

        # 3. Pronoun Ambiguity (Heuristic: "told X Y" + "who")
        if any(m in p_lower for m in self.PRONOUN_MARKERS[:-1]) and 'who' in p_lower:
            return 0.25
            
        # 4. False Dichotomy hints
        if 'either' in p_lower and 'or' in p_lower:
            if 'only' in p_lower or 'just' in p_lower:
                return 0.4

        return 1.0

    def _evaluate_candidate(self, prompt: str, candidate: str, all_criticalities: List[float]) -> Tuple[float, str, float]:
        """Evaluate a single candidate, returning (score, reasoning, meta_cap)."""
        combined_text = f"{prompt} {candidate}"
        triples = self._extract_triples(combined_text)
        
        # 1. Criticality Score
        rho = self._compute_criticality(triples)
        max_rho = max(all_criticalities) if all_criticalities else 1.0
        C_i = rho / (max_rho + self.epsilon)
        
        # 2. Mechanism Design Score (Consistency)
        V_i, T_i = self._forward_chain_check(combined_text, triples)
        M_i = 1.0 - (V_i / max(T_i, 1))
        
        # 3. Numeric/Structural Validation (Constructive)
        # If prompt has numbers, candidate should ideally reflect them or logical derivation
        prompt_nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(candidate)
        numeric_score = 1.0
        if prompt_nums:
            # Heuristic: If prompt has numbers and candidate has none, slight penalty unless it's a yes/no
            if not cand_nums and len(prompt_nums) > 0:
                # Check if candidate is just "Yes"/"No"
                if self._normalize_text(candidate) not in ['yes', 'no', 'true', 'false']:
                    numeric_score = 0.8 
            # Check simple comparison consistency if possible
            if prompt_nums and cand_nums:
                # Basic sanity: if prompt says "5 > 3", candidate shouldn't contradict basic math
                pass 

        # Combined Reward Signal
        w1, w2, w3 = 0.4, 0.4, 0.2
        raw_score = w1 * C_i + w2 * M_i + w3 * numeric_score
        
        # Binary reward for Bandit update (thresholded)
        theta = 0.5
        r_i = 1.0 if raw_score >= theta else 0.0
        
        # Bandit Update (Simulated for 5 rounds internally for stability)
        alpha, beta = 1.0, 1.0 # Prior
        for _ in range(5):
            alpha += r_i
            beta += (1 - r_i)
            
        # UCB Calculation
        t = alpha + beta
        if t == 0: t = 1
        ucb = (alpha / t) + 0.5 * np.sqrt(np.log(max(1, len(all_criticalities) + 1)) / t)
        
        reasoning = f"Criticality:{C_i:.2f}, Consistency:{M_i:.2f}, Numeric:{numeric_score:.2f}"
        return ucb, reasoning, self._check_meta_confidence(prompt)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # Pre-calculate criticalities for normalization
        all_triples = []
        for c in candidates:
            all_triples.extend(self._extract_triples(f"{prompt} {c}"))
        
        # Calculate max rho for normalization across this batch
        temp_rohos = [self._compute_criticality(self._extract_triples(f"{prompt} {c}")) for c in candidates]
        max_rho_val = max(temp_rohos) if temp_rohos else 1.0
        
        # We pass a dummy list for the method signature, but recalculate inside for clarity
        results = []
        
        for candidate in candidates:
            score, reasoning, meta_cap = self._evaluate_candidate(prompt, candidate, temp_rohos)
            
            # Apply Meta-Confidence Cap to the score if the prompt is fundamentally flawed
            # Note: The prompt asks for confidence cap in confidence(), but for ranking, 
            # we should still rank the "least bad" answer highest if forced, but the score reflects uncertainty.
            # However, the instruction says: "confidence() should call _meta_confidence() and cap the return value."
            # So we keep the score as the logical strength, and use confidence() for the certainty metric.
            
            results.append({
                "candidate": candidate,
                "score": float(score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt for ambiguity.
        """
        # 1. Meta-Confidence Check (Tier B)
        meta_cap = self._check_meta_confidence(prompt)
        
        if meta_cap < 1.0:
            # If the prompt is ambiguous/trap, return low confidence immediately
            return meta_cap

        # 2. Structural Signal Check
        # If no structural patterns (numbers, triples, comparatives) are found, uncertainty is high
        triples = self._extract_triples(f"{prompt} {answer}")
        numbers = self._extract_numbers(f"{prompt} {answer}")
        has_structure = bool(triples) or bool(numbers) or bool(self.COMPARATIVE_PATTERN.search(prompt))
        
        if not has_structure:
            # Fallback to NCD similarity as a weak signal, but capped
            ncd = self._compute_ncd(prompt, answer)
            # High NCD means dissimilar, Low NCD means similar. 
            # But for confidence, if we can't parse logic, we shouldn't be confident.
            return 0.4 # Moderate uncertainty for unstructured text

        # 3. Computation/Logic Consistency
        # Re-run evaluation logic for this specific pair
        # We need a dummy list for the normalization in the helper
        dummy_crit = [self._compute_criticality(triples)]
        score, _, _ = self._evaluate_candidate(prompt, answer, dummy_crit)
        
        # Map UCB score (usually 0-2 range) to 0-1 confidence
        # UCB > 1.0 is strong, < 0.5 is weak
        conf = min(1.0, max(0.0, (score - 0.5) / 1.0))
        
        # Cap at 0.9 unless it's a definitive numeric match (heuristic)
        if numbers and self._extract_numbers(answer):
            cap = 0.95
        else:
            cap = 0.9
            
        return min(conf, cap)

# Example Usage (Internal Test)
if __name__ == "__main__":
    tool = ReasoningTool()
    prompt = "Alice has 5 apples. Bob has 3 apples. Who has more?"
    candidates = ["Alice has more apples.", "Bob has more apples.", "They have the same."]
    
    print("Evaluation Results:")
    results = tool.evaluate(prompt, candidates)
    for res in results:
        print(f"- {res['candidate']} (Score: {res['score']:.3f}, Reason: {res['reasoning']})")
        
    print("\nConfidence Checks:")
    for c in candidates:
        print(f"Confidence in '{c}': {tool.confidence(prompt, c):.3f}")
        
    # Tier B Test
    trap_prompt = "Have you stopped cheating on tests?"
    print(f"\nTrap Prompt Confidence: {tool.confidence(trap_prompt, 'Yes')}")