import math
import zlib
from collections import defaultdict
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Graph-Bandit Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Energy): Extracts logical constraints (negations, comparatives, 
       conditionals) and numeric evaluations. Matches candidates against these hard constraints.
       Violations increase "Energy" (E).
    2. Network Science (Entropy): Treats candidate tokens as nodes in a similarity network.
       Candidates sharing structural tokens with the prompt form dense communities.
       Entropy (S) rewards candidates that align with the prompt's structural topology.
    3. Statistical Mechanics (Free Energy): Computes F = E - T*S.
       - Early stage (high T): Exploration favored via entropy term.
       - Late stage (low T): Exploitation favored via energy minimization.
       Since this is a single-shot evaluation, we use a fixed inverse-temperature beta
       tuned to prioritize structural adherence (low energy) while using entropy as a tie-breaker.
    4. Scoring: Score = exp(-beta * F), normalized.
    """

    def __init__(self):
        # Inverse temperature: higher beta = more exploitation of low-energy (high logic) states
        self.beta = 2.5 
        # Entropy weight factor
        self.entropy_weight = 0.5
        
        # Logical keywords for structural parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'unless', 'only if', 'provided'}
        self.booleans = {'true', 'false', 'yes', 'no'}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        nums = []
        current = ""
        has_dot = False
        for char in text:
            if char.isdigit():
                current += char
            elif char == '.' and not has_dot:
                current += char
                has_dot = True
            else:
                if current and current != '.':
                    try:
                        nums.append(float(current))
                    except ValueError:
                        pass
                current = ""
                has_dot = False
        if current and current != '.':
            try:
                nums.append(float(current))
            except ValueError:
                pass
        return nums

    def _compute_structural_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Energy (E) based on logical constraint satisfaction.
        Lower energy = better match.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        energy = 0.0

        # 1. Negation Consistency
        # If prompt has negation context, candidate should reflect it or not contradict
        p_has_neg = any(n in p_low.split() for n in self.negations)
        c_has_neg = any(n in c_low.split() for n in self.negations)
        
        # Simple heuristic: if prompt asks "which is NOT", candidate lacking negation might be penalized
        # depending on the question type. Here we penalize contradiction if obvious.
        if "not" in p_low and "not" not in c_low and any(b in c_low for b in self.booleans):
             # If prompt says "not" and candidate is a boolean "yes/true", high energy
             if "yes" in c_low or "true" in c_low:
                 energy += 5.0
        elif "not" not in p_low and "not" in c_low and any(b in c_low for b in self.booleans):
             if "yes" in c_low or "true" in c_low:
                 energy += 5.0

        # 2. Numeric Evaluation
        p_nums = self._extract_numbers(p_low)
        c_nums = self._extract_numbers(c_low)
        
        if p_nums and c_nums:
            # Check if candidate numbers satisfy simple comparative logic in prompt
            # E.g., Prompt: "greater than 5", Candidate: "6" -> Good. Candidate: "4" -> Bad.
            if "greater" in p_low or "more" in p_low or "larger" in p_low:
                threshold = p_nums[-1] # simplistic assumption of last number being threshold
                if c_nums and c_nums[0] <= threshold:
                    energy += 10.0 # High penalty for violating numeric constraint
            elif "less" in p_low or "fewer" in p_low or "smaller" in p_low:
                threshold = p_nums[-1]
                if c_nums and c_nums[0] >= threshold:
                    energy += 10.0
            
            # Exact match bonus (energy reduction) if numbers match exactly
            if abs(c_nums[0] - p_nums[-1]) < 1e-6:
                energy -= 2.0

        # 3. Keyword Overlap Penalty (Lack of semantic proximity increases energy)
        # Simplified: count shared significant words
        p_words = set(p_low.replace('.', ' ').replace(',', ' ').split())
        c_words = set(c_low.replace('.', ' ').replace(',', ' ').split())
        significant_p = p_words - self.negations - self.conditionals - {'is', 'are', 'the', 'a', 'an', 'it', 'that'}
        
        if significant_p:
            overlap = len(significant_p & c_words)
            # Energy decreases with overlap
            energy -= (overlap * 0.5)
            
        return energy

    def _compute_network_entropy(self, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        """
        Compute Entropy (S) based on network topology of tokens.
        Nodes = tokens. Edges = co-occurrence in prompt/candidates.
        High entropy = candidate shares structural tokens with prompt community.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        p_words = set(p_low.split())
        c_words = set(c_low.split())
        
        # Build local adjacency: how many candidates share words with the prompt?
        # This simulates the "density" of the community around the prompt's concepts.
        shared_count = 0
        total_connections = 0
        
        for cand in all_candidates:
            cand_low = self._normalize(cand)
            cand_words = set(cand_low.split())
            
            # Connection strength to prompt
            p_conn = len(p_words & cand_words)
            # Connection strength of candidate to current candidate (similarity)
            c_conn = len(c_words & cand_words)
            
            if p_conn > 0:
                total_connections += p_conn
                if c_conn > 0:
                    shared_count += c_conn * p_conn # Weighted by prompt relevance

        # Entropy approximation: log of effective connections
        # If candidate is isolated from prompt-related cluster, entropy is low
        if total_connections == 0:
            return 0.0
            
        # Normalized entropy measure
        entropy_val = math.log(shared_count + 1.0) / (math.log(len(all_candidates) + 1) + 1e-6)
        return entropy_val

    def _compute_free_energy(self, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        E = self._compute_structural_energy(prompt, candidate)
        S = self._compute_network_entropy(prompt, candidate, all_candidates)
        
        # F = E - T*S  (Here T is implicit in entropy_weight, effectively 1/beta scaling)
        # We want to minimize F. 
        # High S (good network fit) reduces F.
        F = E - (self.entropy_weight * S)
        return F

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        free_energies = []
        
        # Phase 1: Compute Free Energy for all candidates
        for cand in candidates:
            F = self._compute_free_energy(prompt, cand, candidates)
            free_energies.append(F)
        
        # Phase 2: Boltzmann Distribution for Scores
        # p_i = exp(-beta * F_i) / Z
        max_F = max(free_energies) # Shift for numerical stability
        exp_terms = [math.exp(-self.beta * (f - max_F)) for f in free_energies]
        Z = sum(exp_terms)
        
        if Z == 0:
            Z = 1e-9
            
        for i, cand in enumerate(candidates):
            score = exp_terms[i] / Z
            # Generate reasoning string
            E = self._compute_structural_energy(prompt, cand)
            S = self._compute_network_entropy(prompt, cand, candidates)
            reason = f"Energy(E):{E:.2f}, Entropy(S):{S:.2f}, FreeEnergy(F=E-TS):{free_energies[i]:.2f}"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate against a dummy set containing the answer and a known bad answer
        # to gauge relative confidence.
        # Since we don't have other candidates, we simulate a baseline comparison.
        # We compare the answer to a "null" hypothesis (empty string or "unknown")
        
        candidates = [answer, "unknown", "none of the above"]
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        top = ranked[0]
        if top["candidate"] == answer:
            # Map score to 0-1 confidence. 
            # If score is > 0.5, it's likely correct relative to dummies.
            # Boost if score is very high.
            conf = min(1.0, top["score"] * 2.0) 
            return conf
        else:
            # If answer isn't top, confidence is low
            # Find its score
            score = next((r["score"] for r in ranked if r["candidate"] == answer), 0.0)
            return score * 0.5

# Example usage logic (not part of class, for demonstration of thought process)
# tool = ReasoningTool()
# res = tool.evaluate("Which number is greater than 5?", ["4", "6", "2"])
# Should rank "6" highest due to numeric constraint satisfaction (low energy).