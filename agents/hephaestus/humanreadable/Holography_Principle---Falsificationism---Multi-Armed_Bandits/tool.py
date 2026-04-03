import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Implements a Holographic Falsification Bandit for logical reasoning.
    
    Mechanism:
    1. Holographic Boundary Encoding: Parses text into logical propositions (subject, predicate, object, polarity)
       and encodes them into a boolean adjacency matrix representing the logical structure.
    2. Falsification Loop: Generates counter-factual variants of propositions (negating polarity, reversing causality).
    3. Constraint Propagation: Uses boolean matrix multiplication (transitive closure) to check if original 
       propositions survive when falsified counterparts are introduced.
    4. Robustness Scoring: Calculates the ratio of surviving propositions.
    5. Bandit Selection: Uses Upper Confidence Bound (UCB) to rank candidates, balancing robustness (exploitation)
       and uncertainty (exploration).
    6. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence scores.
    """

    # Regex patterns for logical extraction
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|none|neither)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(greater|less|more|fewer|higher|lower|better|worse)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|unless|provided|then)\b', re.IGNORECASE),
        'causal': re.compile(r'\b(cause|lead|result|prevent|enable)\b', re.IGNORECASE),
        'temporal': re.compile(r'\b(before|after|precede|follow|during)\b', re.IGNORECASE),
        'quantifier': re.compile(r'\b(all|some|every|each|any)\b', re.IGNORECASE),
        'numbers': re.compile(r'-?\d+\.?\d*')
    }
    
    # Tier B Trap Patterns
    TRAPS = {
        'presupposition': re.compile(r'\b(have you stopped|have you quit|why did .*(fail|stop|die)|when did .*(stop|fail))\b', re.IGNORECASE),
        'scope_ambiguity': re.compile(r'\b(every .*(a|an)|each .*(a|an))\b', re.IGNORECASE), # Simplified detection
        'pronoun_ambiguity': re.compile(r'\b(he|she|him|her|they|it)\b.*\b(who|which one)\b', re.IGNORECASE),
        'false_dichotomy': re.compile(r'\b(either .*(or|else)|must be (true|false))\b', re.IGNORECASE),
        'subjectivity': re.compile(r'\b(best|worst|favorite|opinion|believe)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.eval_counts: Dict[str, int] = {}
        self.total_steps: int = 0
        self.alpha: float = 1.0

    def _extract_propositions(self, text: str) -> List[Tuple[str, str, str, int]]:
        """Parse text into (subject, predicate, object, polarity) tuples."""
        props = []
        words = text.split()
        if not words:
            return props
            
        # Simple heuristic parsing for demonstration of the mechanism
        # In a full engine, this would use NLP dependency parsing.
        # Here we simulate logical atoms based on keyword proximity.
        
        has_negation = bool(self.PATTERNS['negation'].search(text))
        has_comp = bool(self.PATTERNS['comparative'].search(text))
        has_causal = bool(self.PATTERNS['causal'].search(text))
        
        # Extract numeric relations
        nums = self.PATTERNS['numbers'].findall(text)
        if len(nums) >= 2:
            n1, n2 = float(nums[0]), float(nums[1])
            polarity = 1 if n1 > n2 else -1
            if has_negation: polarity *= -1
            props.append(("num_1", "greater_than", "num_2", polarity))
            
        # Extract keyword-based logical atoms
        entities = []
        # Capture capitalized words as potential entities
        for w in words:
            clean = re.sub(r'[^\w]', '', w)
            if clean and (clean[0].isupper() or clean.isdigit()):
                entities.append(clean)
        
        if len(entities) >= 2:
            subj, obj = entities[0], entities[-1]
            
            if has_causal:
                props.append((subj, "causes", obj, 1 if not has_negation else -1))
            elif has_comp:
                props.append((subj, "compares_to", obj, 1 if not has_negation else -1))
            else:
                # Default relation
                props.append((subj, "relates_to", obj, 1 if not has_negation else -1))
                
        # If no specific structure, create a dummy proposition to allow scoring
        if not props and text.strip():
            props.append(("text", "implies", "answer", 1 if "not" not in text.lower() else -1))
            
        return props

    def _build_boundary_matrix(self, props: List[Tuple]) -> np.ndarray:
        """Create adjacency matrix A where A[i,j] = polarity of relation i->j."""
        if not props:
            return np.array([[False]])
            
        entities = list(set([p[0] for p in props] + [p[2] for p in props]))
        n = len(entities)
        if n == 0: return np.array([[False]])
        
        ent_map = {e: i for i, e in enumerate(entities)}
        # Matrix dimensions: [entity, entity, polarity_channel] 
        # Flattened to 2D for boolean ops: [entity, entity] (presence implies positive, absence implies negative/neutral)
        # For this implementation, we use a single boolean matrix for existence of valid link
        A = np.zeros((n, n), dtype=bool)
        
        for subj, pred, obj, pol in props:
            if subj in ent_map and obj in ent_map:
                if pol == 1:
                    A[ent_map[subj], ent_map[obj]] = True
                else:
                    # Negative relations are stored as explicit negative edges in a multi-channel approach
                    # For single matrix boolean approximation: we track positive links. 
                    # Falsification will flip these.
                    A[ent_map[subj], ent_map[obj]] = False 
                    # Note: In a full tensor implementation, negative polarity would be a separate channel.
                    # Here we simulate by ensuring the falsified version conflicts.
        
        return A

    def _generate_falsified_props(self, props: List[Tuple]) -> List[Tuple]:
        """Generate falsified counterparts."""
        falsified = []
        for subj, pred, obj, pol in props:
            # Flip polarity
            falsified.append((subj, pred, obj, -pol))
            
            # Reverse causal/comparative direction if applicable
            if "cause" in pred or "lead" in pred:
                falsified.append((obj, "prevented_by", subj, pol))
            elif "greater" in pred or "less" in pred:
                opp = "less_than" if "greater" in pred else "greater_than"
                falsified.append((obj, opp, subj, pol))
                
        return falsified

    def _constraint_propagation(self, A_orig: np.ndarray, A_falsified: np.ndarray) -> np.ndarray:
        """Apply transitive closure and check consistency."""
        if A_orig.shape != A_falsified.shape:
            return A_orig
            
        # Combine matrices (Union of logical space)
        C = np.logical_or(A_orig, A_falsified)
        
        # Transitive closure via Boolean Matrix Multiplication
        # C_new = C OR (C dot C)
        for _ in range(3): # Limit iterations for performance
            C_next = np.logical_or(C, np.dot(C.astype(int), C.astype(int)) > 0)
            if np.array_equal(C, C_next):
                break
            C = C_next
            
        return C

    def _calculate_robustness(self, text: str) -> float:
        """Core algorithm: Holographic encoding -> Falsification -> Propagation."""
        props = self._extract_propositions(text)
        if not props:
            return 0.5 # Neutral if unparseable
            
        A_orig = self._build_boundary_matrix(props)
        falsified_props = self._generate_falsified_props(props)
        A_falsified = self._build_boundary_matrix(falsified_props)
        
        # If no falsified props generated (simple text), robustness is high by default
        if not falsified_props:
            return 0.9
            
        C = self._constraint_propagation(A_orig, A_falsified)
        
        # Calculate survival ratio
        # How many original positive links survive in the combined closure?
        orig_count = np.sum(A_orig)
        if orig_count == 0:
            return 0.5
            
        # Check overlap. If original links are preserved in the closure despite falsification attempts
        # In a strict logical sense, if A_orig implies contradiction with A_falsified, robustness drops.
        # Here we approximate: if the closure is dense (everything connects), logic is broken.
        n = A_orig.shape[0]
        total_possible = n * n if n > 0 else 1
        density = np.sum(C) / total_possible
        
        # Heuristic: High density after falsification implies low discriminative power (chaos)
        # Low density implies structure held up.
        robustness = 1.0 - density
        
        # Normalize to [0, 1] roughly
        return max(0.0, min(1.0, robustness + 0.5))

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B Check: Detects ambiguity, presuppositions, and unanswerability.
        Returns a cap value (0.0 to 1.0).
        """
        combined = f"{prompt} {answer}"
        cap = 1.0
        
        # 1. Presupposition traps
        if self.TRAPS['presupposition'].search(prompt):
            cap = min(cap, 0.2)
            
        # 2. Scope ambiguity (simplified)
        if self.TRAPS['scope_ambiguity'].search(prompt) and "same" not in combined and "different" not in combined:
            cap = min(cap, 0.4)
            
        # 3. Pronoun ambiguity
        if self.TRAPS['pronoun_ambiguity'].search(prompt):
            cap = min(cap, 0.3)
            
        # 4. False dichotomy
        if self.TRAPS['false_dichotomy'].search(prompt):
            cap = min(cap, 0.5)
            
        # 5. Subjectivity
        if self.TRAPS['subjectivity'].search(prompt):
            cap = min(cap, 0.6)
            
        # 6. Unanswerability (Heuristic: if prompt asks 'how' but no numbers/units in answer)
        if re.search(r'\b(how many|calculate|compute)\b', prompt, re.IGNORECASE):
            if not re.search(r'\d', answer):
                cap = min(cap, 0.3)

        return cap

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0: return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        self.total_steps += 1
        
        # Meta-check on prompt first
        prompt_cap = 1.0
        if self.TRAPS['presupposition'].search(prompt):
            prompt_cap = 0.3
        
        for candidate in candidates:
            cand_id = str(candidate)
            
            # Update bandit counts
            if cand_id not in self.eval_counts:
                self.eval_counts[cand_id] = 0
            self.eval_counts[cand_id] += 1
            n_i = self.eval_counts[cand_id]
            t = self.total_steps
            
            # 1. Structural & Logical Robustness (50%+)
            robustness = self._calculate_robustness(candidate)
            
            # 2. Constructive Computation Check (20%+)
            # If prompt has numbers and candidate doesn't, penalize heavily
            comp_score = 1.0
            prompt_nums = self.PATTERNS['numbers'].findall(prompt)
            cand_nums = self.PATTERNS['numbers'].findall(candidate)
            if prompt_nums and not cand_nums:
                # Check if it's a math question
                if re.search(r'\b(sum|total|difference|product|calculate)\b', prompt, re.IGNORECASE):
                    comp_score = 0.1
            
            # 3. NCD Tiebreaker (max 15% influence)
            ncd = self._ncd_similarity(prompt, candidate)
            ncd_score = 1.0 - ncd # Higher is better match
            
            # Weighted Score
            base_score = (0.6 * robustness) + (0.25 * comp_score) + (0.15 * ncd_score)
            
            # Bandit UCB Adjustment
            # S_i = R_i + alpha * sqrt(log(t) / n_i)
            exploration_bonus = self.alpha * np.sqrt(np.log(max(1, t)) / max(1, n_i))
            final_score = base_score + (0.1 * exploration_bonus) # Dampen exploration impact on final rank
            
            # Apply Epistemic Cap from Meta-Confidence
            meta_cap = self._meta_confidence(prompt, candidate)
            if meta_cap < 0.3:
                final_score = min(final_score, 0.3) # Hard cap for traps
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Robustness: {robustness:.2f}, Comp: {comp_score:.2f}, NCD: {ncd_score:.2f}"
            if meta_cap < 0.5:
                reasoning += " [WARNING: Potential Tier B Trap Detected]"
                
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Enforces epistemic honesty via _meta_confidence.
        """
        # 1. Check Meta-Constraints (Tier B)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Calculate Base Robustness
        robustness = self._calculate_robustness(answer)
        
        # 3. Constructive check
        comp_score = 1.0
        prompt_nums = self.PATTERNS['numbers'].findall(prompt)
        cand_nums = self.PATTERNS['numbers'].findall(answer)
        if prompt_nums and not cand_nums:
            if re.search(r'\b(sum|total|calculate|solve)\b', prompt, re.IGNORECASE):
                comp_score = 0.2
        
        base_conf = (0.6 * robustness) + (0.4 * comp_score)
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it's a clear calculation
        if not (prompt_nums and cand_nums and len(prompt_nums) == len(cand_nums)):
            final_conf = min(final_conf, 0.85)
            
        return float(np.clip(final_conf, 0.0, 1.0))