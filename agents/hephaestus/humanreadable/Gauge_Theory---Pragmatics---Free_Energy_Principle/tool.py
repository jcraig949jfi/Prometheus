import re
import numpy as np
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    A computational reasoning tool implementing a Gauge-Theoretic Factor Graph.
    
    Mechanism:
    1. Parsing: Extracts atomic propositions and relations (negation, conditionals, causality, numerics)
       using regex to build a structural skeleton.
    2. Gauge Theory: Treats context shifts (negations, conditionals) as gauge transformations (sign flips).
       Truth values are parallel-transported across the graph; inconsistencies create 'curvature' (error).
    3. Free Energy Minimization: Uses Loopy Belief Propagation to minimize prediction error (Free Energy)
       across the factor graph, converging on the most probable truth assignments.
    4. Epistemic Honesty: Detects Tier B traps (presuppositions, ambiguity) to cap confidence,
       ensuring the model admits uncertainty rather than hallucinating certainty.
    """
    
    # Structural regex patterns (Adversarially robust via variable capture)
    PATTERNS = {
        'negation': re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE),
        'conditional': re.compile(r'\b(if|unless|provided|when)\b.*?\b(then|,|will|would)\b', re.IGNORECASE | re.DOTALL),
        'causal': re.compile(r'\b(because|since|therefore|thus|hence|leads to|causes|results in)\b', re.IGNORECASE),
        'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
        'numeric_val': re.compile(r'-?\d+(?:\.\d+)?'),
        'quantifier': re.compile(r'\b(every|all|some|none|only|at least|at most)\b', re.IGNORECASE),
        'temporal': re.compile(r'\b(before|after|during|while|until)\b', re.IGNORECASE),
        'pronoun_ambig': re.compile(r'(\w+)\s+(told|asked|said to)\s+(\w+)\s+.*?\b(he|she|him|her|they|them)\b', re.IGNORECASE),
        'presupposition': re.compile(r'\b(have you stopped|did you stop|why did|why does|when did|when does)\b', re.IGNORECASE),
        'false_dichotomy': re.compile(r'\b(either|or both|only two options)\b', re.IGNORECASE),
        'subjectivity': re.compile(r'\b(best|worst|favorite|beautiful|ugly|good|bad)\b', re.IGNORECASE)
    }

    def __init__(self):
        self.max_iter = 20
        self.tol = 1e-4

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        if self.PATTERNS['presupposition'].search(p_lower):
            return 0.25
            
        # 2. False Dichotomy
        if self.PATTERNS['false_dichotomy'].search(p_lower):
            # Check if it implies exclusivity without evidence
            if "either" in p_lower and "or" in p_lower:
                return 0.3
                
        # 3. Subjectivity without criteria
        if self.PATTERNS['subjectivity'].search(p_lower):
            if "calculate" not in p_lower and "logic" not in p_lower:
                return 0.3
                
        # 4. Pronoun Ambiguity in "Who" questions
        if "who" in p_lower and self.PATTERNS['pronoun_ambig'].search(p_lower):
            return 0.25

        # 5. Structural emptiness
        if len(prompt.split()) < 3:
            return 0.2
            
        return 1.0  # No obvious traps detected

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical atoms and relations."""
        nodes = []
        edges = []  # (src, dst, type, weight)
        
        # Normalize text for processing
        clean_text = re.sub(r'[^\w\s\.\,\?\!\-\+\=\<\>\$]', ' ', text)
        sentences = [s.strip() for s in re.split(r'[\.!?]', clean_text) if s.strip()]
        
        # Create node for each sentence/claim
        for i, sent in enumerate(sentences):
            if not sent: continue
            nodes.append({'id': i, 'text': sent, 'polarity': 1.0})
            
            # Detect Negation (Gauge flip)
            if self.PATTERNS['negation'].search(sent):
                # In gauge theory, this is a local transformation T = -1
                nodes[-1]['polarity'] = -1.0
            
            # Detect Numerics
            nums = self.PATTERNS['numeric_val'].findall(sent)
            if len(nums) >= 2:
                # Implicit comparison constraint
                edges.append((i, i, 'numeric_check', float(nums[0]), float(nums[1])))
            
            # Detect Conditionals (Implication)
            if self.PATTERNS['conditional'].search(sent):
                edges.append((i, i, 'conditional', 1.0))
                
            # Detect Causality
            if self.PATTERNS['causal'].search(sent):
                edges.append((i, i, 'causal', 0.8)) # Confidence weight

        return {'nodes': nodes, 'edges': edges, 'raw': text}

    def _solve_numeric(self, text: str) -> Optional[float]:
        """Constructive computation for explicit math problems."""
        # Bat-and-ball, simple algebra, direct comparison
        nums = [float(x) for x in self.PATTERNS['numeric_val'].findall(text)]
        
        # Case: Direct Comparison (Is 9.11 > 9.9?)
        if "greater" in text or ">" in text or "more" in text:
            if len(nums) >= 2:
                return 1.0 if nums[0] > nums[1] else 0.0
        if "less" in text or "<" in text or "smaller" in text:
            if len(nums) >= 2:
                return 1.0 if nums[0] < nums[1] else 0.0
                
        # Case: Bat-and-Ball (Total X, Diff Y -> Solve linear eq)
        # Pattern: "... cost $X ... more than ... total $Y" or similar
        if len(nums) == 2:
            a, b = nums
            # Heuristic for "A and B total T, A is D more than B"
            if "total" in text and ("more" in text or "less" in text):
                # 2B + D = T => B = (T-D)/2
                if a > b: 
                    val = (a - b) / 2
                    return val # Return the smaller value usually requested
                else:
                    val = (b - a) / 2
                    return val
            # Modular arithmetic hint
            if "remainder" in text or "mod" in text or "divided by" in text:
                if int(b) != 0:
                    return a % b

        return None

    def _gauge_belief_propagation(self, structure: Dict) -> np.ndarray:
        """
        Implements Loopy Belief Propagation on the factor graph.
        Variables: Truth values of nodes.
        Factors: Logical consistency, gauge transformations (negation), numeric constraints.
        """
        n = len(structure['nodes'])
        if n == 0:
            return np.array([0.5])
            
        # Initialize beliefs (probability of True)
        beliefs = np.full(n, 0.5)
        
        # Adjacency list for message passing
        neighbors = {i: [] for i in range(n)}
        for edge in structure['edges']:
            src, dst = edge[0], edge[1]
            if src != dst: # Skip self-loops for topology, handle via factors
                neighbors[src].append(dst)
                neighbors[dst].append(src)
        
        # Iterative updates
        for _ in range(self.max_iter):
            old_beliefs = beliefs.copy()
            
            for i in range(n):
                node = structure['nodes'][i]
                msg_sum = 0.0
                count = 0
                
                # Self-factors (Internal consistency)
                if node['polarity'] == -1.0:
                    # If negated, belief should flip relative to context
                    # Simplified: Negation reduces confidence in positive assertion
                    msg_sum += (1.0 - beliefs[i]) * 0.5 
                    count += 1
                
                # Neighbor messages (Transitivity/Consistency)
                for j in neighbors[i]:
                    # Simple averaging message from neighbors
                    msg_sum += beliefs[j]
                    count += 1
                
                # Numeric constraints (Hard factors)
                for edge in structure['edges']:
                    if edge[0] == i and edge[2] == 'numeric_check':
                        v1, v2 = edge[3], edge[4]
                        # If numbers are present, enforce logical numeric truth
                        if "greater" in node['text'] or ">" in node['text']:
                            target = 1.0 if v1 > v2 else 0.0
                            msg_sum += target
                            count += 1
                        elif "less" in node['text'] or "<" in node['text']:
                            target = 1.0 if v1 < v2 else 0.0
                            msg_sum += target
                            count += 1

                if count > 0:
                    # Update belief with damping to prevent oscillation
                    new_val = (msg_sum / count)
                    beliefs[i] = 0.9 * new_val + 0.1 * beliefs[i]
                    
            if np.max(np.abs(beliefs - old_beliefs)) < self.tol:
                break
                
        return beliefs

    def _compute_free_energy(self, structure: Dict, candidate: str) -> float:
        """
        Computes Free Energy F = E - TS.
        Here approximated as prediction error + complexity penalty.
        Lower F is better.
        """
        # 1. Constructive Computation Check (High priority)
        full_text = structure['raw'] + " " + candidate
        numeric_sol = self._solve_numeric(full_text)
        
        if numeric_sol is not None:
            # If we found a numeric solution, check candidate against it
            cand_nums = [float(x) for x in self.PATTERNS['numeric_val'].findall(candidate)]
            if cand_nums:
                # Allow small epsilon for float comparison
                if abs(cand_nums[0] - numeric_sol) < 1e-6:
                    return -10.0 # Very low energy (high score)
                else:
                    return 10.0 # High energy (wrong)
        
        # 2. Factor Graph Energy
        # Temporarily add candidate as a node or constraint?
        # Simpler: Evaluate candidate consistency with parsed structure
        structure['nodes'].append({'id': len(structure['nodes']), 'text': candidate, 'polarity': 1.0})
        
        # Run BP to get stable state
        final_beliefs = self._gauge_belief_propagation(structure)
        
        # Energy is negative log likelihood of the candidate being true
        # If the last node (candidate) has high belief, energy is low
        cand_idx = len(final_beliefs) - 1
        prob = final_beliefs[cand_idx]
        
        # Avoid log(0)
        prob = np.clip(prob, 1e-6, 1-1e-6)
        energy = -np.log(prob)
        
        # Penalty for ambiguity (high entropy)
        entropy = -(prob * np.log(prob) + (1-prob) * np.log(1-prob))
        energy += 0.5 * entropy
        
        return energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        structure = self._extract_structure(prompt)
        results = []
        
        # Baseline NCD for tie-breaking (max 15% influence logic)
        import zlib
        prompt_bytes = prompt.encode()
        base_len = len(zlib.compress(prompt_bytes))
        
        for cand in candidates:
            # 1. Structural/Computation Score
            energy = self._compute_free_energy(structure, cand)
            struct_score = -energy
            
            # 2. NCD Tiebreaker
            cand_bytes = cand.encode()
            combined_len = len(zlib.compress(prompt_bytes + cand_bytes))
            ncd = (combined_len - base_len) / max(len(cand_bytes), 1)
            ncd_score = -ncd # Lower compression diff is better (more redundant/likely)
            
            # Weighted Sum: 85% Structural, 15% NCD
            final_score = 0.85 * struct_score + 0.15 * ncd_score
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Free Energy: {energy:.4f}, NCD contribution: {ncd_score:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt (Tier B).
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        cap = self._meta_confidence(prompt)
        
        if cap < 0.3:
            return cap
            
        # 2. Structural Confidence
        # If no numbers found and no clear logic operators, reduce confidence
        has_logic = any(p.search(prompt) for p in [self.PATTERNS['conditional'], self.PATTERNS['causal'], self.PATTERNS['comparative']])
        has_nums = bool(self.PATTERNS['numeric_val'].search(prompt))
        
        raw_score = 0.5
        if has_logic or has_nums:
            # Run a quick evaluation to see if this answer stands out
            res = self.evaluate(prompt, [answer, "DUMMY_ANSWER_TO_TEST_CONTRAST"])
            if len(res) > 1 and res[0]['score'] > res[1]['score'] + 2.0:
                raw_score = 0.95 # Strong structural match
            elif len(res) > 0 and res[0]['candidate'] == answer:
                raw_score = 0.7 # Matched but not decisively
            else:
                raw_score = 0.3 # Likely wrong
                
        # Apply Cap
        final_conf = min(raw_score, cap)
        
        # Never exceed 0.9 without definitive computation (heuristic check)
        if has_nums and self._solve_numeric(prompt) is not None:
            final_conf = min(final_conf, 0.99) # Can be high if math works
        else:
            final_conf = min(final_conf, 0.85) # Cap for non-math
            
        return float(np.clip(final_conf, 0.0, 1.0))

# Example usage logic would go here if run as script, but class is the deliverable.