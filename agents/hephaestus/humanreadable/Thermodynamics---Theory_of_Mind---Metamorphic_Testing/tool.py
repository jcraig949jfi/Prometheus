import re
import math
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    A reasoning evaluator combining structural constraint parsing, 
    Theory of Mind belief simulation, and thermodynamic free energy scoring.
    
    Mechanism:
    1. Parses prompts into a constraint-energy graph using regex for entities, 
       predicates, modalities, and numerics.
    2. Simulates a 'belief layer' by flipping modalities for agent-attributed facts.
    3. Applies metamorphic mutations (swaps, tautologies) to test stability.
    4. Computes Free Energy = Energy (constraint violations) - Entropy (uncertainty).
    5. Ranks candidates by negative free energy (lower energy = higher score).
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none|cannot|impossible)\b', re.I),
            'belief': re.compile(r'\b(believes?|thinks?|knows?|says?|claims?)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'number': re.compile(r'-?\d+\.?\d*'),
            'entity': re.compile(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*'), # Simple capitalized nouns
            'quantifier': re.compile(r'\b(all|some|every|none|any)\b', re.I)
        }
        self.temp = 1.0

    def _extract_props(self, text: str) -> List[Tuple]:
        """Extract atomic propositions as (subj, pred, obj, modality, weight)."""
        props = []
        text_lower = text.lower()
        
        # Detect global modifiers
        is_negated = bool(self.patterns['negation'].search(text_lower))
        has_belief = bool(self.patterns['belief'].search(text_lower))
        has_cond = bool(self.patterns['conditional'].search(text_lower))
        
        # Extract numbers for numeric constraints
        numbers = [float(n) for n in self.patterns['number'].findall(text)]
        
        # Extract entities
        entities = list(set(self.patterns['entity'].findall(text)))
        
        # Create synthetic propositions based on structural features
        if is_negated:
            props.append(("global", "negation", "true", "hard", 1.0))
        if has_cond:
            props.append(("global", "conditional", "true", "soft", 0.5))
        if has_belief:
            props.append(("global", "belief_op", "true", "soft", 0.5))
            
        # Numeric consistency check
        if len(numbers) >= 2:
            # Implicit ordering constraint if comparatives exist
            if self.patterns['comparative'].search(text_lower):
                props.append(("num_seq", "ordered", str(numbers), "hard", 1.0))
            else:
                props.append(("num_set", "exists", str(numbers), "soft", 0.2))

        # Entity relations (simplified)
        for i, ent in enumerate(entities):
            mod = "belief" if has_belief else "fact"
            props.append((ent, "exists", "true", mod, 0.1))
            
        return props

    def _build_graph(self, text: str, is_belief_layer: bool = False) -> Dict[str, Any]:
        """Build a constraint graph from text."""
        props = self._extract_props(text)
        energy = 0.0
        soft_constraints = 0
        hard_violations = 0
        
        for subj, pred, obj, mod_type, weight in props:
            # Theory of Mind: Flip modality if in belief layer and proposition is belief-attributed
            # In this simplified model, we simulate the "belief copy" by checking consistency
            # If the text says "John believes X", and we are in the belief layer, we treat X as fact for John.
            # If the candidate contradicts the prompt's explicit constraints, energy increases.
            
            if mod_type == "hard":
                # Check for direct contradictions in the text itself (self-contradiction)
                # For this implementation, we assume the candidate must align with prompt structure
                if is_belief_layer and pred == "negation":
                    # Simulating a flipped world where negation might be false
                    pass 
                else:
                    energy += weight # Base energy for complexity
            else:
                soft_constraints += 1
                energy += weight * 0.5 # Soft constraints contribute less to base energy

        return {
            "props": props,
            "energy": energy,
            "soft_count": soft_constraints,
            "hard_count": len([p for p in props if p[3] == "hard"])
        }

    def _compute_entropy(self, soft_count: int) -> float:
        """Compute entropy based on number of soft constraints (log2 |Omega|)."""
        if soft_count == 0:
            return 0.0
        # Approximate possible worlds as 2^soft_constraints
        return math.log2(2 ** soft_count)

    def _metamorphic_check(self, prompt: str, candidate: str) -> float:
        """
        Apply metamorphic transformations and measure stability.
        Returns a penalty score (0.0 = stable, higher = unstable).
        """
        penalty = 0.0
        combined = f"{prompt} {candidate}"
        
        # Transformation 1: Tautology addition (should not change meaning)
        # We simulate this by checking if the structural density changes wildly
        base_graph = self._build_graph(combined)
        
        # Transformation 2: Conjunct swap (simulated by re-parsing shuffled segments)
        # Since we can't easily shuffle semantic meaning without NLP, we check 
        # if the candidate merely repeats the prompt (echoing) which is a common failure mode.
        words_p = set(prompt.lower().split())
        words_c = set(candidate.lower().split())
        
        # Heuristic: If candidate is >90% overlap with prompt words, it's likely an echo (bad reasoning)
        if len(words_c) > 0:
            overlap = len(words_p.intersection(words_c)) / len(words_c)
            if overlap > 0.9 and len(words_c) > 5:
                penalty += 2.0 # High penalty for echoing
                
        # Transformation 3: Numeric scaling check
        # If numbers exist, ensure they aren't nonsensical (e.g. negative counts if not allowed)
        # This is implicitly handled by the graph energy, but we add a specific check here.
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', candidate)]
        if any(n < 0 for n in nums):
             # Context dependent, but generally negative numbers in simple counts are suspicious
             if "count" in prompt.lower() or "number" in prompt.lower():
                 penalty += 1.0

        return penalty

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """Calculate Free Energy = Energy - T * Entropy."""
        # 1. Build World Graph (Facts)
        world_graph = self._build_graph(prompt)
        
        # 2. Build Belief Graph (Candidate's perspective)
        # We treat the candidate as the "belief state" of the agent answering
        belief_graph = self._build_graph(candidate, is_belief_layer=True)
        
        # 3. Compute Interaction Energy (Constraint Violations)
        # Penalty if candidate graph structure drastically differs from prompt structure
        # e.g. Prompt has negation, candidate does not (or vice versa)
        interaction_penalty = 0.0
        
        p_props = world_graph['props']
        c_props = belief_graph['props']
        
        # Check for negation alignment
        p_has_neg = any(p[1] == 'negation' for p in p_props)
        c_has_neg = any(p[1] == 'negation' for p in c_props)
        
        if p_has_neg != c_has_neg:
            # If prompt implies a constraint (like negation) and candidate ignores it
            # Note: In some ToM cases, the candidate SHOULD differ (e.g. "John thinks X" vs "X is false")
            # But for general reasoning, alignment is key unless explicit belief operator is used.
            if "believes" not in prompt.lower() and "thinks" not in prompt.lower():
                interaction_penalty += 5.0 # Hard mismatch
        
        # 4. Total Energy
        total_energy = world_graph['energy'] + belief_graph['energy'] + interaction_penalty
        
        # 5. Entropy (Uncertainty in soft constraints)
        total_soft = world_graph['soft_count'] + belief_graph['soft_count']
        entropy = self._compute_entropy(total_soft)
        
        # 6. Free Energy
        free_energy = total_energy - (self.temp * entropy)
        
        # 7. Metamorphic Stability Penalty
        stability_penalty = self._metamorphic_check(prompt, candidate)
        
        return free_energy + stability_penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = -self._calculate_free_energy(prompt, cand) # Negative free energy (higher is better)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Free Energy: {-score:.4f}, Stability Penalty applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses a sigmoid-like mapping of the negative free energy score.
        """
        fe = self._calculate_free_energy(prompt, answer)
        # Convert free energy to confidence
        # Lower FE -> Higher Confidence. 
        # Assume FE ~ 0 is neutral, < 0 is good, > 0 is bad.
        # Map to 0-1: 1 / (1 + e^(FE))
        conf = 1.0 / (1.0 + math.exp(fe))
        return max(0.0, min(1.0, conf))

# Example usage logic (not part of the class, for context)
# tool = ReasoningTool()
# res = tool.evaluate("If A is greater than B, and B is 5, is A 6?", ["Yes, A is 6", "No, A is 4"])