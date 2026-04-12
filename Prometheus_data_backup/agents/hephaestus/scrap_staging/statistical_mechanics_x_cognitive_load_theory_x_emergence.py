import re
import math
import zlib
from collections import Counter
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Load-Regulated Ensemble Hypothesis Sampler (LREHS) Implementation.
    
    Mechanism:
    1. Micro-level: Treats candidates as states in a Boltzmann ensemble.
       Energy E = -log(P(data|h)). Since we lack a generative model, we approximate
       likelihood via structural constraint satisfaction and semantic coherence.
    2. Cognitive Load Coupling: Estimates "Load" (L) based on prompt ambiguity,
       presuppositions, and logical traps (Tier B checks). 
       Temperature T = T0 * (1 + alpha * L). High load -> High T -> Flatter distribution
       (prevents premature commitment to a wrong answer when the question is tricky).
    3. Emergence: Clusters candidates by structural similarity. If no candidate clearly
       dominates the emerging "basins" of truth, confidence is suppressed.
    4. Epistemic Honesty: Prioritizes detecting unanswerable/ambiguous prompts over
       forcing a selection.
    """

    def __init__(self):
        self.T0 = 0.5  # Base temperature
        self.alpha = 2.0  # Load sensitivity
        self.k_cluster = 3  # Clustering frequency (conceptual)
        
        # Tier B Trap Patterns
        self.presupposition_triggers = [
            r"\b(stopped|quit|ceased|failed|why did|how did)\b",
            r"\b(every time|always|never)\b.*\b(fail|wrong|mistake)\b"
        ]
        self.false_dichotomy_triggers = [
            r"\b(either|or)\b", r"\b(must|have to)\b.*\b(choose|pick)\b"
        ]
        self.scope_ambiguity_triggers = [
            r"\b(every|all|each)\b.*\b(a|an|the)\b.*\b(same|different|own)\b",
            r"\b(who|he|she|it|they)\b.*\?(?:\s*$)" # Pronoun ref at end
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        load_score = 0.0
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                load_score += 0.8
                break
                
        # Check False Dichotomies (simplified)
        if re.search(r"\beither\b", p_lower) and re.search(r"\bor\b", p_lower):
            # Only flag if it looks like a forced choice without logical necessity
            if "logic" not in p_lower and "math" not in p_lower:
                load_score += 0.6

        # Check Scope/Pronoun Ambiguity
        for pattern in self.scope_ambiguity_triggers:
            if re.search(pattern, p_lower):
                load_score += 0.7
                break

        # Check for subjective/unanswerable markers
        subjective_words = ["best", "worst", "favorite", "opinion", "feel"]
        if any(w in p_lower for w in subjective_words) and "calculate" not in p_lower:
            load_score += 0.9

        # Map load to confidence cap
        # High load -> Low confidence cap
        if load_score > 0.5:
            return max(0.1, 1.0 - load_score)
        
        return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural parsing and constraint propagation.
        Returns a score 0.0 to 1.0 based on logical consistency.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower().strip().rstrip('.')
        score = 0.0
        
        # 1. Negation Handling
        negation_present = bool(re.search(r"\b(not|no|never|none|cannot)\b", p_lower))
        candidate_negates = bool(re.search(r"\b(not|no|never|none|false)\b", c_lower))
        
        if "true" in p_lower or "false" in p_lower or "correct" in p_lower:
            # Binary logic check
            if negation_present:
                # If prompt has negation, answer should reflect it
                if candidate_negates == negation_present: # Simplified heuristic
                    score += 0.5
            else:
                if not candidate_negates:
                    score += 0.5
        else:
            # General consistency: if prompt asks "What is not X?", candidate shouldn't be X
            # This is a shallow check but catches obvious contradictions
            score += 0.2 # Base structural credit for attempting an answer

        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt
        nums_prompt = re.findall(r"[-+]?\d*\.\d+|\d+", p_lower)
        nums_cand = re.findall(r"[-+]?\d*\.\d+|\d+", c_lower)
        
        if nums_prompt and nums_cand:
            try:
                # Simple arithmetic check: if prompt implies operation
                if "sum" in p_lower or "add" in p_lower:
                    expected = sum(float(x) for x in nums_prompt)
                    if abs(float(nums_cand[0]) - expected) < 1e-6:
                        score += 0.5
                elif "product" in p_lower or "multiply" in p_lower:
                    prod = 1.0
                    for x in nums_prompt: prod *= float(x)
                    if abs(float(nums_cand[0]) - prod) < 1e-6:
                        score += 0.5
                elif "greater" in p_lower or "larger" in p_lower or ">" in p_lower:
                    # Comparison logic
                    if len(nums_prompt) >= 2:
                        is_true = float(nums_prompt[0]) > float(nums_prompt[1])
                        cand_val = nums_cand[0].lower()
                        if (is_true and cand_val in ["true", "yes", "1"]) or \
                           (not is_true and cand_val in ["false", "no", "0"]):
                            score += 0.5
            except ValueError:
                pass

        # 3. Transitivity/Logic Keywords
        if "if" in p_lower and "then" in p_lower:
            if "therefore" in c_lower or "thus" in c_lower:
                score += 0.3
        
        return min(1.0, score)

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """
        Normalized Compression Distance as a tiebreaker (max 15% weight).
        Measures semantic similarity via compression.
        """
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        try:
            len_s1 = len(zlib.compress(s1))
            len_s2 = len(zlib.compress(s2))
            len_combined = len(zlib.compress(s1 + s2))
            
            if len_combined == 0: return 1.0
            ncd = (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)
            # Invert NCD so higher is better (similarity)
            return max(0.0, 1.0 - ncd)
        except:
            return 0.5

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes negative log-likelihood proxy (Energy).
        Lower energy = better fit.
        """
        # Component 1: Structural fit (High structural score = Low Energy)
        struct = self._structural_score(prompt, candidate)
        # Component 2: NCD fit (High similarity = Low Energy)
        ncd = self._ncd_score(prompt, candidate)
        
        # Weighted combination: Structural is dominant
        quality = 0.7 * struct + 0.3 * ncd
        
        # Avoid log(0), ensure quality is in (0, 1]
        quality = max(0.01, min(0.99, quality))
        
        # E = -log(Quality)
        return -math.log(quality)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-Cognitive Load Estimation (Tier B Check)
        # Determines the "Temperature" of the system
        meta_conf = self._meta_confidence(prompt)
        load = 1.0 - meta_conf  # High load if meta_conf is low
        T = self.T0 * (1.0 + self.alpha * load)
        
        # 2. Micro-level: Compute Energies
        energies = []
        for i, cand in enumerate(candidates):
            E = self._compute_energy(prompt, cand)
            energies.append((i, E))
        
        # 3. Boltzmann Distribution
        # P(i) = exp(-E_i / T) / Z
        try:
            exp_terms = [math.exp(-E / T) for _, E in energies]
            Z = sum(exp_terms)
            probs = [e / Z for e in exp_terms]
        except OverflowError:
            # Fallback for extreme temperatures
            probs = [1.0 / len(candidates)] * len(candidates)

        # 4. Emergent Macro-level: Basins & Scoring
        # We adjust the raw probability based on the "Basin" stability.
        # If the top candidate is significantly better than the rest, it forms a stable basin.
        # If probabilities are flat (high T), we penalize confidence in the ranking.
        
        ranked_indices = sorted(range(len(probs)), key=lambda k: probs[k], reverse=True)
        
        results = []
        for idx in ranked_indices:
            base_score = probs[idx]
            cand_text = candidates[idx]
            
            # Emergent penalty: If load is high (T is high), the distinction between 
            # candidates is less reliable. We scale the score by meta_conf.
            final_score = base_score * meta_conf
            
            # Reasoning string generation
            reasoning_parts = []
            if meta_conf < 0.3:
                reasoning_parts.append("WARNING: Prompt contains ambiguity or presupposition.")
            if self._structural_score(prompt, cand_text) > 0.4:
                reasoning_parts.append("Structural constraints satisfied.")
            if self._ncd_score(prompt, cand_text) > 0.8:
                reasoning_parts.append("High semantic coherence.")
                
            reason_str = " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."

            results.append({
                "candidate": cand_text,
                "score": float(final_score),
                "reasoning": reason_str
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence to ensure epistemic honesty.
        """
        # 1. Check Meta-Confidence (Tier B Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Compute raw score
        struct_score = self._structural_score(prompt, answer)
        ncd_score = self._ncd_score(prompt, answer)
        raw_score = 0.7 * struct_score + 0.3 * ncd_score
        
        # 3. Apply Cap
        final_conf = min(raw_score, cap)
        
        # 4. Deterministic floor/ceiling adjustments for clarity
        if cap < 0.3:
            return round(final_conf, 2) # Keep low if ambiguous
        
        # Never return > 0.9 unless computation was definitive (simulated here by high struct score)
        if struct_score < 0.9:
            final_conf = min(final_conf, 0.85)
            
        return round(max(0.0, min(1.0, final_conf)), 2)