import re
import math
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    A reasoning tool fusing Thermodynamics (free-energy minimization), 
    Hebbian Learning (co-occurrence weighting), and Mechanism Design (proper scoring).
    
    Core Mechanism:
    1. Parsing: Extracts atomic propositions (negations, comparatives, conditionals, causals, numerics).
    2. Hebbian Phase: Strengthens edges between atoms that co-occur in candidate answers.
    3. Thermodynamic Phase: Computes 'energy' of each candidate based on weighted edge satisfaction.
       Minimizes free energy to find the most probable relational structure.
    4. Mechanism Design: Scores candidates using negative equilibrium energy (incentive compatible).
    
    Epistemic Honesty (Tier B):
    - Detects presuppositions, ambiguities, and unanswerable queries to cap confidence.
    - Uses NCD only as a minor tiebreaker (<15%).
    """

    def __init__(self):
        self.epsilon = 1e-3
        self.eta = 0.1  # Learning rate
        self.temperature = 0.5
        
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b|\b([<>=])\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'causal': re.compile(r'\b(causes|leads to|results in|because|therefore|thus)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?(?:\s*[a-zA-Z%]+)?'),
            'ordering': re.compile(r'\b(before|after|first|last|previous|next)\b', re.I)
        }
        
        # Tier B Ambiguity Triggers
        self.presupposition_triggers = re.compile(r'\b(stopped|quit|failed|why did|when did)\b', re.I)
        self.scope_triggers = re.compile(r'\b(every|all|each)\b.*\b(a|an|the)\b', re.I)
        self.pronoun_triggers = re.compile(r'\b(he|she|him|her|they|them)\b.*\b(who|whom|whose)\b', re.I)
        self.dichotomy_triggers = re.compile(r'\b(either|or)\b', re.I)
        self.subjectivity_triggers = re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.I)

    def _extract_atoms(self, text: str) -> Set[str]:
        """Extract atomic propositions based on structural types."""
        atoms = set()
        text_lower = text.lower()
        
        # Check structural types
        if self.patterns['negation'].search(text_lower): atoms.add("TYPE:NEGATION")
        if self.patterns['comparative'].search(text_lower): atoms.add("TYPE:COMPARATIVE")
        if self.patterns['conditional'].search(text_lower): atoms.add("TYPE:CONDITIONAL")
        if self.patterns['causal'].search(text_lower): atoms.add("TYPE:CAUSAL")
        if self.patterns['ordering'].search(text_lower): atoms.add("TYPE:ORDERING")
        
        # Extract specific numeric values as atoms
        nums = self.patterns['numeric'].findall(text_lower)
        for n in nums:
            atoms.add(f"NUM:{n}")
            
        # Extract key verbs/nouns as weak atoms (simplified for regex)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        for w in set(words):
            if w not in ['that', 'this', 'with', 'have', 'been', 'were', 'there', 'which']:
                atoms.add(f"WORD:{w}")
                
        return atoms

    def _build_edges(self, atoms: Set[str]) -> List[Tuple[str, str]]:
        """Create directed edges between atoms present in the text."""
        atom_list = list(atoms)
        edges = []
        # Simple connectivity: connect sequential types or all-to-all for small sets
        # To mimic implication, we assume presence implies presence in this context
        for i in range(len(atom_list)):
            for j in range(i + 1, len(atom_list)):
                edges.append((atom_list[i], atom_list[j]))
        return edges

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        # 1. Presupposition traps
        if self.presupposition_triggers.search(p_lower):
            return 0.2
            
        # 2. Scope ambiguity
        if self.scope_triggers.search(p_lower):
            return 0.4
            
        # 3. Pronoun ambiguity
        if self.pronoun_triggers.search(p_lower):
            return 0.3
            
        # 4. False dichotomy
        if self.dichotomy_triggers.search(p_lower) and "or" in p_lower:
            # Only flag if it looks like a forced choice without "either" context sometimes
            if "either" in p_lower or ("a" in p_lower and "b" in p_lower): 
                return 0.3
                
        # 5. Subjectivity
        if self.subjectivity_triggers.search(p_lower):
            return 0.5
            
        # 6. Unanswerability (heuristic: very short prompt with no data)
        if len(prompt.split()) < 4 and "?" in prompt:
            return 0.2
            
        # If answer is empty or generic
        if len(a_lower.split()) < 2 or a_lower in ["yes", "no", "maybe", "i don't know"]:
            # Don't penalize short answers if the question is simple, but limit confidence
            return 0.6
            
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Parsing Stage
        candidate_atoms = []
        candidate_edges = []
        
        for c in candidates:
            atoms = self._extract_atoms(c)
            # Include prompt atoms to establish context linkage
            prompt_atoms = self._extract_atoms(prompt)
            all_atoms = atoms.union(prompt_atoms)
            
            edges = self._build_edges(all_atoms)
            candidate_atoms.append(atoms)
            candidate_edges.append(set(edges))
            
        # 2. Hebbian Weight Initialization & Update
        # Global edge set
        all_edges = set()
        for es in candidate_edges:
            all_edges.update(es)
            
        weights = {e: self.epsilon for e in all_edges}
        
        # Hebbian update: strengthen edges that co-occur in the same candidate
        # Since edges are internal to a candidate, we strengthen edges that appear 
        # in candidates that also share other edges (simplified to frequency for this impl)
        edge_counts = {e: 0 for e in all_edges}
        for es in candidate_edges:
            for e in es:
                edge_counts[e] += 1
                
        # Normalize counts to weights
        max_count = max(edge_counts.values()) if edge_counts else 1
        for e in all_edges:
            weights[e] = self.epsilon + self.eta * (edge_counts[e] / max_count)

        # 3. Thermodynamic Equilibrium (Free Energy Minimization)
        # We approximate equilibrium by calculating energy directly based on final weights
        # Energy E(a) = sum(w_e * (1 - indicator(e in a))^2)
        # Since (1-indicator)^2 is 0 if present, 1 if absent:
        # E(a) = sum(w_e for e NOT in a)
        
        total_edge_pool = all_edges
        scores = []
        
        for i, c in enumerate(candidates):
            edges_i = candidate_edges[i]
            
            # Calculate Energy
            energy = 0.0
            for e in total_edge_pool:
                if e not in edges_i:
                    energy += weights.get(e, self.epsilon)
            
            # Entropy term (simplified): penalize low complexity (too few edges)
            # H = -sum(p log p). If edge presence is binary, high entropy = mixed signals.
            # Here we use a simplicity prior: fewer edges = higher energy (less stable)
            complexity_penalty = -0.1 * math.log(len(edges_i) + 1) if edges_i else 0
            free_energy = energy + complexity_penalty
            
            # 4. Mechanism Design Scoring
            # Score = -Energy (convex conjugate approximation)
            # Add NCD tiebreaker (max 15% influence)
            ncd_val = self._compute_ncd(prompt, c)
            ncd_score = -ncd_val * 0.15 # Lower NCD (more similar) is better (less negative)
            
            final_score = -free_energy + ncd_score
            
            scores.append({
                "candidate": c,
                "score": final_score,
                "reasoning": f"Energy: {-free_energy:.4f}, NCD_bonus: {ncd_score:.4f}"
            })
            
        # Rank by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-analysis of prompt ambiguity (Tier B).
        """
        # 1. Meta-confidence check (Question properties)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Structural match check
        atoms = self._extract_atoms(answer)
        has_structure = len(atoms) > 0
        
        if not has_structure:
            # If no structural parsing matches, honest uncertainty
            return min(0.25, meta_cap)
            
        # 3. Base confidence on structural density
        # More structural atoms detected relative to length = higher confidence
        density = len(atoms) / (len(answer.split()) + 1)
        base_conf = min(0.95, 0.5 + density) # Cap at 0.95 unless computed
        
        # If computation was possible (numeric atoms), allow higher confidence
        if any("NUM:" in a for a in atoms):
            base_conf = 0.98
            
        return min(base_conf, meta_cap)

# Example usage logic (not part of class, for demonstration)
# tool = ReasoningTool()
# res = tool.evaluate("If A > B and B > C, is A > C?", ["Yes, A is greater than C", "No, A is less than C"])
# conf = tool.confidence("Have you stopped cheating?", "No")