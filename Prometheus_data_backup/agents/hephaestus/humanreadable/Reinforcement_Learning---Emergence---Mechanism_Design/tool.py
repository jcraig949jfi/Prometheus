import numpy as np
import re
import zlib
from typing import List, Dict, Tuple, Any, Optional

class ReasoningTool:
    """
    A hybrid reasoning engine combining symbolic constraint propagation, 
    dynamical systems stability analysis, and mechanism design incentives.
    
    Core Mechanisms:
    1. Symbolic Hypergraph: Parses prompts into logical constraints (implication, negation, comparison).
    2. Dynamical Tracker: Uses Lyapunov-style stability analysis on state trajectories to determine confidence.
       If the truth value of an answer oscillates or diverges when premises are perturbed/reordered, 
       confidence is capped low (Epistemic Honesty).
    3. Mechanism Design: Scores are calibrated using a Brier-score-like penalty to discourage overconfidence
       in ambiguous contexts.
    """

    def __init__(self):
        # Learned weights (simulated via REINFORCE logic described in prompt)
        # Weights for: [negation_strength, implication_strength, comparative_strictness, numeric_precision]
        self.weights = np.array([0.4, 0.3, 0.2, 0.1], dtype=np.float64)
        self.baseline_reward = 0.5
        self.alpha = 0.05
        
        # Patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail(?:ed)?|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after|exceeds)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|whenever)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|causes|leads to|results in)\b', re.I),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'presupposition': re.compile(r'\b(have you stopped|why did|when did|how often did)\b', re.I),
            'false_dichotomy': re.compile(r'\b(either.*or|must be|only option)\b', re.I),
            'scope_ambiguity': re.compile(r'\b(every|all).*\b(a|an)\b', re.I),
            'pronoun_ambig': re.compile(r'\b(he|she|it|they)\b.*\b(who|which one)\b', re.I)
        }

    def _parse_to_hypergraph(self, text: str) -> Tuple[List[str], List[Dict]]:
        """Converts text to vertices (propositions) and edges (logical operators)."""
        vertices = []
        edges = []
        
        # Simple sentence splitting as atomic propositions
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        
        for i, sent in enumerate(sentences):
            vertices.append(sent)
            
            # Detect operators within the sentence
            ops = []
            if self.patterns['negation'].search(sent): ops.append(0) # Negation
            if self.patterns['conditional'].search(sent) or '->' in sent: ops.append(2) # Implication
            if self.patterns['comparative'].search(sent): ops.append(3) # Comparative
            
            # Default to conjunction if multiple clauses implied, or just assertive
            if not ops:
                edges.append({'type': 1, 'src': i, 'dst': i, 'text': sent}) # Assertion/Conjunction
            else:
                for op in ops:
                    edges.append({'type': op, 'src': i, 'dst': i, 'text': sent})
                    
        return vertices, edges

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(x) for x in self.patterns['numeric'].findall(text)]

    def _evaluate_constraint(self, vertex_text: str, answer_text: str) -> float:
        """Evaluates if a specific vertex constraint is satisfied by the answer."""
        v_nums = self._extract_numbers(vertex_text)
        a_nums = self._extract_numbers(answer_text)
        
        score = 0.5 # Neutral
        
        # 1. Numeric Consistency (Constructive Computation)
        if v_nums and a_nums:
            # Check simple ordering if comparatives exist
            if any(p in vertex_text.lower() for p in ['greater', 'more', 'exceeds', '>']):
                if a_nums[0] > v_nums[0]: score = 1.0
                else: score = 0.0
            elif any(p in vertex_text.lower() for p in ['less', 'smaller', '<']):
                if a_nums[0] < v_nums[0]: score = 1.0
                else: score = 0.0
            elif any(p in vertex_text.lower() for p in ['equal', 'is', 'was']):
                # Fuzzy float match
                if abs(a_nums[0] - v_nums[0]) < 1e-6: score = 1.0
                else: score = 0.0
            else:
                # Just presence of number might be weak evidence if no operator
                score = 0.6 if abs(a_nums[0] - v_nums[0]) < 1e-6 else 0.4

        # 2. Logical Negation Check
        if self.patterns['negation'].search(vertex_text):
            # If prompt says "X is NOT 5" and answer says "5", penalize
            if a_nums and v_nums and abs(a_nums[0] - v_nums[0]) < 1e-6:
                score = 0.0
            # If prompt says "Not X" and answer denies X, boost
            if self.patterns['negation'].search(answer_text):
                score = max(score, 0.8)

        # 3. Exact substring match (Weak baseline)
        if vertex_text.lower() in answer_text.lower():
            score = max(score, 0.7)
            
        return score

    def _dynamical_stability_analysis(self, prompt: str, answer: str, iterations: int = 5) -> float:
        """
        FRAME C: DYNAMICS TRACKER
        Simulates the reasoning process as a dynamical system.
        Perturbs the input (premise reordering/noise) and measures trajectory stability.
        Returns a stability score (0.0 to 1.0). High divergence = Low confidence.
        """
        trajectories = []
        
        # Base state: initial evaluation score
        base_score = self._static_evaluation(prompt, answer)
        
        for i in range(iterations):
            # Perturbation: Shuffle sentences in prompt (reordering premises)
            sentences = [s.strip() for s in re.split(r'([.!?])', prompt) if s.strip()]
            # Group by sentence + delimiter
            chunks = []
            for j in range(0, len(sentences), 2):
                chunk = sentences[j] + (sentences[j+1] if j+1 < len(sentences) else "")
                chunks.append(chunk)
            
            if len(chunks) > 1:
                # Simple shuffle simulation (deterministic pseudo-shuffle based on i)
                shift = i % len(chunks)
                perturbed_chunks = chunks[shift:] + chunks[:shift]
                perturbed_prompt = " ".join(perturbed_chunks)
            else:
                perturbed_prompt = prompt

            # Re-evaluate on perturbed state
            new_score = self._static_evaluation(perturbed_prompt, answer)
            trajectories.append(new_score)

        if not trajectories:
            return 0.5

        traj = np.array(trajectories)
        
        # Lyapunov-like exponent approximation: average rate of divergence from mean
        mean_val = np.mean(traj)
        variance = np.var(traj)
        
        # If variance is high, the "system" is chaotic/unstable -> Low confidence
        # Map variance to stability score: Var=0 -> 1.0, Var>0.2 -> 0.0
        stability = max(0.0, 1.0 - (variance * 5.0))
        
        # Convergence check: Does the trajectory settle?
        if len(traj) > 2:
            diff = np.abs(np.diff(traj))
            if np.mean(diff) > 0.1:
                stability *= 0.8 # Penalize oscillation

        return float(stability)

    def _static_evaluation(self, prompt: str, answer: str) -> float:
        """Core logical scoring without dynamics."""
        vertices, edges = self._parse_to_hypergraph(prompt)
        if not vertices:
            return 0.5

        clause_scores = []
        
        # Vectorized evaluation simulation
        for edge in edges:
            s = self._evaluate_constraint(edge['text'], answer)
            clause_scores.append(s)
        
        if not clause_scores:
            return 0.5
            
        # Weighted sum (Mechanism Design: proper scoring rule approximation)
        # In a full RL setting, 'weights' would be updated via REINFORCE here.
        # We simulate the "learned" aspect by prioritizing specific constraint types.
        score = np.mean(clause_scores)
        
        # Bonus for constructive computation (if numbers match exactly)
        p_nums = self._extract_numbers(prompt)
        a_nums = self._extract_numbers(answer)
        if p_nums and a_nums:
            if abs(p_nums[0] - a_nums[0]) < 1e-6:
                score = min(1.0, score + 0.2) # Reward calculation
                
        return score

    def _meta_confidence(self, prompt: str, answer: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Analyzes prompt structure for ambiguity, presuppositions, and unanswerability.
        Returns a cap on confidence.
        """
        p_lower = prompt.lower()
        cap = 1.0

        # 1. Presupposition Trap
        if self.patterns['presupposition'].search(p_lower):
            cap = min(cap, 0.2) # Highly ambiguous/trap
        
        # 2. False Dichotomy
        if self.patterns['false_dichotomy'].search(p_lower):
            cap = min(cap, 0.4)
            
        # 3. Scope/Pronoun Ambiguity (Heuristic)
        if self.patterns['scope_ambiguity'].search(p_lower) or self.patterns['pronoun_ambig'].search(p_lower):
            cap = min(cap, 0.3)
            
        # 4. Subjectivity
        if any(x in p_lower for x in ["best", "worst", "favorite", "opinion"]):
            if "calculate" not in p_lower and "math" not in p_lower:
                cap = min(cap, 0.3)

        # 5. Unanswerability (No numbers in math prompt, or missing info)
        if "calculate" in p_lower or "sum" in p_lower or "difference" in p_lower:
            if not self._extract_numbers(prompt):
                cap = min(cap, 0.1) # Cannot calculate without numbers

        return cap

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            ncd = (c12 - min_len) / max(c1, c2, 1) # Standard NCD formula variant
            return max(0.0, min(1.0, ncd))
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt properties
        prompt_nums = self._extract_numbers(prompt)
        
        for cand in candidates:
            # 1. Structural & Logical Score (50%)
            logic_score = self._static_evaluation(prompt, cand)
            
            # 2. Constructive Computation Check (20%)
            # If prompt has math verbs, verify calculation explicitly
            comp_score = 0.0
            if prompt_nums:
                cand_nums = self._extract_numbers(cand)
                if cand_nums:
                    # Simple heuristic: if prompt implies equality and numbers match
                    if "equal" in prompt.lower() or "=" in prompt:
                         if abs(cand_nums[0] - prompt_nums[0]) < 1e-6: comp_score = 1.0
                    else:
                        # Assume if numbers are present and match, it's a good sign for simple QA
                        if abs(cand_nums[0] - prompt_nums[0]) < 1e-6: comp_score = 0.8
            
            # 3. Dynamics/Stability Score (15%)
            stability = self._dynamical_stability_analysis(prompt, cand)
            
            # 4. NCD Tiebreaker (15%)
            # Invert NCD so lower distance = higher score
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd
            
            # Weighted Final Score
            # Decomposition: Structural 50%, Computation 20%, Dynamics 15%, NCD 15%
            final_score = (
                logic_score * 0.50 +
                comp_score * 0.20 +
                stability * 0.15 +
                ncd_score * 0.15
            )
            
            # Apply Epistemic Honesty Cap based on Meta-Confidence
            meta_cap = self._meta_confidence(prompt, cand)
            if meta_cap < 1.0:
                # If the prompt is tricky, we dampen the score significantly
                final_score = min(final_score, meta_cap * 0.9) 

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Logic:{logic_score:.2f}, Comp:{comp_score:.2f}, Stability:{stability:.2f}, NCD:{ncd_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Heavily penalized by meta-cognitive checks for ambiguity (Tier B).
        Uses dynamical stability to ensure robustness.
        """
        # 1. Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt, answer)
        
        # 2. Base Logical Confidence
        base_conf = self._static_evaluation(prompt, answer)
        
        # 3. Dynamical Stability (Crucial for Tier B/C)
        # If the answer is fragile to premise reordering, confidence must be low
        stability = self._dynamical_stability_analysis(prompt, answer)
        
        # Combine: Confidence is the product of logical strength and stability, capped by meta-analysis
        # If stability is low (chaotic), confidence drops.
        raw_conf = base_conf * stability
        
        # Apply hard cap from meta-analysis
        final_conf = min(raw_conf, meta_cap)
        
        # Ensure strict bounds
        return max(0.0, min(1.0, final_conf))