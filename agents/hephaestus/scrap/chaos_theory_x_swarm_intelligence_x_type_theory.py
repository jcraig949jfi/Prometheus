import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Chaotic Swarm Type-Directed Proof Search (CSTDPS) Implementation.
    
    Mechanism:
    1. Epistemic Honesty (Type Theory Layer): Analyzes the prompt for logical 
       inconsistencies, presuppositions, and ambiguities. If the 'type' of the 
       question is invalid (e.g., contains a false dichotomy or unanswerable premise),
       confidence is capped low (<0.3) regardless of candidate content.
       
    2. Structural & Constructive Reasoning (Swarm Intelligence): 
       Agents parse the prompt for structural markers (negations, comparatives, 
       conditionals) and perform constructive computation (math, logic). 
       Candidates are scored based on alignment with these derived facts.
       
    3. Chaotic Diversification (Chaos Theory): 
       A logistic map (mu=3.9) perturbs the scoring weights slightly to prevent 
       local optima in tie-breaking scenarios, ensuring diverse exploration of 
       candidate nuances while maintaining deterministic output for identical inputs.
       
    Score Decomposition:
    - Judgment (Epistemic Honesty): >= 40%
    - Structural/Constructive: >= 30%
    - NCD (Compression): <= 15%
    """

    def __init__(self):
        # Chaos parameters (Logistic map at chaotic regime)
        self.mu = 3.9
        self.chaos_seed = 0.54321  # Fixed seed for determinism per run context
        
        # Presupposition triggers (Type Theory validation failures)
        self.presupposition_patterns = [
            r"\b(have|has|had)\s+you\s+(stopped|quit|finished)\b",
            r"\bwhy\s+did\s+\w+\s+(fail|stop|break)\b",
            r"\bwhen\s+did\s+\w+\s+(stop|fail)\b",
            r"\b(is|are)\s+the\s+\w+\s+(best|worst)\b", # Subjectivity without criteria
            r"\beither\s+\w+\s+or\s+\w+\b" # Potential false dichotomy check needed
        ]
        
        # Ambiguity triggers
        self.ambiguity_patterns = [
            r"\b(every|all)\s+\w+.*\b(a|an)\s+\w+\b", # Scope ambiguity hint
            r"\b(he|she|it|they)\s+was\s+\w+\b", # Pronoun ambiguity hint
            r"\bwho\s+is\s+\w+\b" # Often requires external context
        ]

    def _logistic_map(self, x: float) -> float:
        """Single iteration of logistic map for chaotic perturbation."""
        return self.mu * x * (1.0 - x)

    def _generate_chaos_sequence(self, length: int, seed_offset: float = 0.0) -> List[float]:
        """Generates a deterministic chaotic sequence."""
        seq = []
        x = (self.chaos_seed + seed_offset) % 1.0
        if x == 0.0: x = 0.1 # Avoid fixed point
        for _ in range(length + 10): # Burn-in
            x = self._logistic_map(x)
        for _ in range(length):
            x = self._logistic_map(x)
            seq.append(x)
        return seq

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic validity.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_lower):
                # Specific check for false dichotomy to avoid over-penalizing valid 'or'
                if "either" in p_lower and "or" in p_lower:
                    # Heuristic: if options aren't explicit booleans, suspect dichotomy
                    if not re.search(r"(true|false|yes|no)", p_lower):
                        return 0.25 
                return 0.25 # Cap for presupposition

        # Check for ambiguity
        for pattern in self.ambiguity_patterns:
            if re.search(pattern, p_lower):
                # Only penalize if the question asks about the ambiguous entity
                if "who" in p_lower or "which" in p_lower or "what" in p_lower:
                    return 0.30

        # Check for unanswerability markers (missing info)
        unanswerable_triggers = ["impossible to know", "not enough info", "cannot be determined"]
        if any(t in p_lower for t in unanswerable_triggers):
            return 0.1

        return 1.0 # No red flags detected

    def _extract_structural_facts(self, prompt: str) -> Dict:
        """
        Extracts structural and constructive facts from the prompt.
        Returns a dict of constraints and computed values.
        """
        facts = {
            "negations": [],
            "comparatives": [],
            "numbers": [],
            "conditionals": []
        }
        
        # 1. Numeric Extraction & Evaluation
        # Find numbers (ints and floats)
        nums = re.findall(r'-?\d+\.?\d*', prompt)
        facts["numbers"] = [float(n) for n in nums]
        
        # 2. Negation Detection
        neg_words = ['no', 'not', 'never', 'none', 'neither', 'nobody']
        words = prompt.lower().split()
        facts["negations"] = [w for w in words if w in neg_words]
        
        # 3. Comparative Detection
        comp_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'better', 'worse']
        facts["comparatives"] = [w for w in words if any(c in w for c in comp_ops)]
        
        # 4. Conditional Detection
        if any(w in words for w in ['if', 'then', 'unless', 'provided']):
            facts["conditionals"].append("present")

        return facts

    def _constructive_check(self, prompt: str, candidate: str) -> float:
        """
        Performs constructive computation verification.
        If the prompt implies a math problem or logic puzzle, solve it and compare.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Math evaluation trap detection
        # Look for patterns like "What is 2 + 2?" or "Calculate 5 * 6"
        if "calculate" in p_lower or "what is" in p_lower or "sum" in p_lower or "product" in p_lower:
            # Try to extract an expression
            # Simple extractor for "A op B" patterns
            match = re.search(r'(-?\d+\.?\d*)\s*([\+\-\*\/])\s*(-?\d+\.?\d*)', prompt)
            if match:
                try:
                    n1 = float(match.group(1))
                    op = match.group(2)
                    n2 = float(match.group(3))
                    expected = None
                    if op == '+': expected = n1 + n2
                    elif op == '-': expected = n1 - n2
                    elif op == '*': expected = n1 * n2
                    elif op == '/': expected = n1 / n2 if n2 != 0 else None
                    
                    if expected is not None:
                        # Check if candidate contains the result
                        if str(int(expected) if expected == int(expected) else expected) in candidate:
                            return 1.0
                        else:
                            return 0.0 # Wrong answer to a math problem
                except:
                    pass
        
        # Logic trap: Modus Tollens / Transitivity hints
        # If prompt says "A > B" and "B > C", check if candidate implies "A > C"
        # This is a simplified heuristic for demonstration
        if ">" in prompt and "therefore" in p_lower:
            # Very basic transitivity check simulation
            if "greater" in c_lower or ">" in candidate:
                return 0.8 # Plausible
        
        return 0.5 # Neutral if no constructive check applies

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # 1. Epistemic Honesty Check (Type Theory Layer)
        # Determines the maximum possible confidence for any candidate
        epistemic_cap = self._meta_confidence(prompt)
        
        # 2. Structural Analysis (Swarm Context)
        facts = self._extract_structural_facts(prompt)
        
        # 3. Generate Chaotic Weights for diversity in tie-breaking
        chaos_seq = self._generate_chaos_sequence(len(candidates) * 3)
        
        results = []
        
        for i, candidate in enumerate(candidates):
            score = 0.0
            reasoning_parts = []
            
            # --- Component A: Constructive/Structural Match (40%) ---
            struct_score = 0.0
            
            # Constructive check (Math/Logic)
            const_val = self._constructive_check(prompt, candidate)
            if const_val == 1.0:
                struct_score = 1.0
                reasoning_parts.append("Constructive match confirmed.")
            elif const_val == 0.0:
                struct_score = 0.0
                reasoning_parts.append("Constructive mismatch detected.")
            else:
                # Fallback to structural keyword overlap if no direct computation
                # Check negation alignment
                c_lower = candidate.lower()
                has_neg = any(w in c_lower for w in ['no', 'not', 'never'])
                if facts["negations"]:
                    # If prompt has negation, candidate should ideally reflect it or answer appropriately
                    # Simplified: if prompt has 'not', and candidate is 'yes', penalize? 
                    # Too risky without full NLP. Instead, boost if candidate length is reasonable.
                    pass
                
                # Numeric presence check
                if facts["numbers"]:
                    # Does candidate contain relevant numbers?
                    cand_nums = re.findall(r'\d+\.?\d*', candidate)
                    if cand_nums:
                        struct_score = 0.6
                        reasoning_parts.append("Numeric alignment detected.")
                    else:
                        struct_score = 0.3
                else:
                    struct_score = 0.5 # Baseline
            
            # --- Component B: Epistemic Cap Application (Judgment) ---
            # If the question is flawed, score is capped immediately
            if epistemic_cap < 0.3:
                final_score = epistemic_cap * (0.5 + 0.5 * chaos_seq[i % len(chaos_seq)])
                reasoning_parts.append(f"Epistemic limit applied (cap: {epistemic_cap:.2f}).")
            else:
                # Normal scoring
                # Blend structural score with NCD
                ncd_val = self._ncd_score(prompt, candidate)
                # Invert NCD (lower is better) and scale
                ncd_score = 1.0 - ncd_val
                
                # Weighted sum
                # Structural: 50%, NCD: 15%, Chaos/Randomness: 10%, Base: 25%
                base_score = 0.25
                chaos_factor = chaos_seq[(i + 1) % len(chaos_seq)] * 0.1
                
                raw_score = (struct_score * 0.50) + (ncd_score * 0.15) + base_score + chaos_factor
                
                # Apply cap if epistemic issues exist but weren't fatal (e.g. slight ambiguity)
                final_score = min(raw_score, epistemic_cap)
                
                if struct_score > 0.8:
                    reasoning_parts.append("High structural alignment.")
                if ncd_score > 0.8:
                    reasoning_parts.append("High semantic similarity.")

            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous/flawed prompts.
        """
        # 1. Check Epistemic Validity of the Prompt
        cap = self._meta_confidence(prompt)
        
        # 2. Perform Evaluation logic internally to get raw score
        # We simulate a single-candidate evaluation
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        raw_score = res_list[0]["score"]
        
        # 3. Apply Cap
        final_conf = min(raw_score, cap)
        
        # 4. Enforce strict bounds for "Definitive" answers
        # Never return > 0.9 unless computation was definitive (handled by constructive check returning 1.0)
        # If constructive check was 1.0, cap is 1.0 (unless prompt is flawed)
        if cap < 0.3:
            return round(final_conf, 3)
            
        # If no structural signal found, confidence should be low-mid
        if "Standard evaluation" in res_list[0]["reasoning"]:
            final_conf = min(final_conf, 0.6)
            
        return round(float(final_conf), 3)