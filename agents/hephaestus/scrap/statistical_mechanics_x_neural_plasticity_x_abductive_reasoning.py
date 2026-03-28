import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Energy-Based Plasticity-Driven Abductive Inference Engine.
    
    Mechanism:
    1. Structural Parsing (Wake Phase): Extracts logical constraints (negations, comparatives,
       conditionals) to define an energy landscape E(x). Candidates violating hard constraints
       receive infinite energy (rejected).
    2. Free-Energy Minimization: Scores candidates based on constraint satisfaction density
       and semantic overlap (heuristic for low-energy attractors).
    3. Fluctuation-Dissipation Test (Sleep Phase): Injects noise into the candidate string
       (character shuffling/deletion). Robust hypotheses (low free-energy basins) maintain
       high similarity to the original under perturbation; fragile ones degrade rapidly.
    4. Ranking: Final score combines structural adherence, baseline energy, and robustness.
    """

    def __init__(self):
        self.temp = 0.5  # Simulation temperature for noise injection

    def _structural_parse(self, prompt: str) -> Dict:
        """Extracts logical constraints from the prompt."""
        p_lower = prompt.lower()
        constraints = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', p_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|before|after|larger|higher|lower)\b', p_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', p_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', p_lower)
        }
        # Detect explicit negative constraints (e.g., "not A", "exclude B")
        constraints['excluded'] = []
        for match in re.finditer(r'(?:not|exclude|except|without)\s+([a-zA-Z0-9]+)', p_lower):
            constraints['excluded'].append(match.group(1))
            
        return constraints

    def _compute_energy(self, prompt: str, candidate: str, constraints: Dict) -> float:
        """
        Computes energy E(x). Lower is better.
        Hard constraints yield infinity. Soft constraints add to energy.
        """
        c_lower = candidate.lower()
        energy = 0.0
        
        # Hard Constraint: Excluded terms
        for exc in constraints['excluded']:
            if exc in c_lower:
                return float('inf')
        
        # Soft Constraint: Penalty for missing prompt keywords (simplified abductive match)
        # We expect valid answers to reference specific entities or logic from prompt
        prompt_words = set(re.findall(r'[a-z0-9]+', prompt.lower()))
        candidate_words = set(re.findall(r'[a-z0-9]+', c_lower))
        
        # Intersection over Union heuristic for relevance (inverse energy)
        if len(prompt_words) == 0:
            return 1.0
            
        overlap = len(prompt_words & candidate_words)
        union = len(prompt_words | candidate_words)
        relevance = overlap / union if union > 0 else 0
        
        # Base energy inversely proportional to relevance
        energy += (1.0 - relevance) * 10.0
        
        # Numeric consistency check (simplified)
        if constraints['numbers']:
            # If prompt has numbers, candidate ideally should too (heuristic for numeric problems)
            cand_nums = re.findall(r'\d+(?:\.\d+)?', c_lower)
            if not cand_nums and len(constraints['numbers']) > 0:
                # Not a hard fail, but adds energy
                energy += 2.0

        return energy

    def _perturb(self, text: str) -> str:
        """Injects noise (Langevin-like fluctuation) into the candidate."""
        if len(text) < 2:
            return text
        chars = list(text)
        # Swap two random adjacent characters or delete one
        if np.random.rand() < 0.5 and len(chars) > 2:
            idx = np.random.randint(0, len(chars) - 1)
            chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        else:
            idx = np.random.randint(0, len(chars))
            chars.pop(idx)
        return "".join(chars)

    def _dissipation_metric(self, candidate: str, iterations: int = 5) -> float:
        """
        Estimates robustness via fluctuation-dissipation.
        Measures how much the 'meaning' (approximated by NCD) degrades under noise.
        Stable hypotheses resist degradation.
        """
        if len(candidate) == 0:
            return 0.0
            
        original_comp = zlib.compress(candidate.encode())
        stability_scores = []
        
        for _ in range(iterations):
            perturbed = self._perturb(candidate)
            if not perturbed:
                stability_scores.append(0.0)
                continue
            
            # NCD-like distance between original and perturbed
            # If candidate is robust, small perturbation != large semantic shift
            # Here we approximate semantic shift by string compression distance
            try:
                p_comp = zlib.compress(perturbed.encode())
                combined = zlib.compress((candidate + perturbed).encode())
                ncd = (len(combined) - min(len(original_comp), len(p_comp))) / max(len(original_comp), len(p_comp), 1)
                stability_scores.append(1.0 - ncd) # Higher is more stable
            except:
                stability_scores.append(0.0)
                
        return np.mean(stability_scores) if stability_scores else 0.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = zlib.compress(s1.encode())
            c2 = zlib.compress(s2.encode())
            c12 = zlib.compress((s1 + s2).encode())
            return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2), 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        constraints = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate prompt compression for NCD tiebreaking
        prompt_comp_len = len(zlib.compress(prompt.encode()))

        for cand in candidates:
            # 1. Compute Energy (Constraint Satisfaction)
            energy = self._compute_energy(prompt, cand, constraints)
            
            if energy == float('inf'):
                score = 0.0
                reasoning = "Violates hard logical constraints (exclusion)."
            else:
                # 2. Compute Robustness (Fluctuation-Dissipation)
                # Deterministic seed for evaluation consistency within a run
                np.random.seed(hash(cand) % (2**32)) 
                robustness = self._dissipation_metric(cand, iterations=3)
                
                # 3. Combine into Free Energy Score
                # Score = Robustness * (1 / (1 + Energy))
                base_score = robustness / (1.0 + energy)
                
                # Tie-breaking with NCD relative to prompt
                ncd_val = self._ncd_distance(prompt, cand)
                final_score = base_score * 0.9 + (1.0 - ncd_val) * 0.1
                
                score = max(0.0, min(1.0, final_score))
                reasoning = f"Energy: {energy:.2f}, Robustness: {robustness:.2f}"

            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on energy and robustness."""
        constraints = self._structural_parse(prompt)
        energy = self._compute_energy(prompt, answer, constraints)
        
        if energy == float('inf'):
            return 0.0
            
        np.random.seed(hash(answer) % (2**32))
        robustness = self._dissipation_metric(answer, iterations=5)
        
        # Map energy and robustness to 0-1 confidence
        # Low energy + High robustness = High confidence
        confidence = robustness * (1.0 / (1.0 + energy))
        return float(np.clip(confidence, 0.0, 1.0))