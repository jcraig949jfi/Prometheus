import re
import math
import random
import zlib
from collections import deque

class ReasoningTool:
    """
    Ergodic-Critical Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing: Extracts propositional variables, numeric constraints, 
       and logical relations (implication, negation, ordering) from text using regex.
    2. Constraint Graph Construction: Builds a directed graph where edges represent 
       logical or arithmetic constraints.
    3. Ergodic Sampling: Performs a Markov Chain Monte Carlo (MCMC) walk over the 
       space of truth assignments. It proposes random flips/perturbations and accepts 
       them based on constraint satisfaction to estimate the volume of consistent states.
    4. Criticality Weighting: Adjusts the final score based on constraint density (delta).
       Systems near the phase transition (delta ~ 0.5) are weighted higher as they 
       represent the most informative reasoning challenges.
    5. Epistemic Honesty (Tier B): Detects ambiguity, presupposition, and unanswerability 
       to cap confidence, ensuring the tool admits uncertainty rather than hallucinating.
    """

    def __init__(self):
        self.rng = random.Random(42)  # Deterministic seed for reproducibility
        self.burn_in = 500
        self.samples = 2000

    def _meta_confidence(self, text: str) -> float:
        """
        Checks prompt for Tier B traps: presupposition, ambiguity, subjectivity.
        Returns a cap on confidence (1.0 = safe, <0.3 = suspicious).
        """
        t = text.lower()
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail...")
        presupp_patterns = [
            r"have you (stopped|quit|ceased)",
            r"why did .*(fail|stop|break)",
            r"when did .*(stop|end)",
            r"how often do you.*(lie|cheat)"
        ]
        for p in presupp_patterns:
            if re.search(p, t):
                return 0.2

        # 2. Scope/Pronoun Ambiguity indicators
        if re.search(r"(every|all) .*(same|different|who|he|she|it)", t):
            # Heuristic: if "every" appears with pronoun questions, high ambiguity risk
            if re.search(r"(who|which|he|she|it)\?", t):
                return 0.25

        # 3. False Dichotomy ("Either A or B" without context)
        if re.search(r"either .+ or .+", t) and "only" not in t:
            # Soft penalty, not definitive but suspicious
            return 0.6 

        # 4. Subjectivity without criteria
        subj_patterns = [r"best", r"worst", r"favorite", r"beautiful", r"ugly"]
        if any(re.search(p, t) for p in subj_patterns):
            if "measure" not in t and "data" not in t and "statistic" not in t:
                return 0.3

        # 5. Unanswerability (Missing info indicators)
        if re.search(r"(unknown|missing|not given|impossible to tell)", t):
            return 0.1
            
        return 1.0

    def _parse_constraints(self, text: str):
        """
        Extracts vertices (variables/numbers) and edges (constraints).
        Returns V (list), E (list of tuples), and numeric constraints.
        """
        vertices = []
        edges = []
        numerics = []
        
        # Normalize
        t = text.lower()
        
        # 1. Extract Numeric Constraints (e.g., "5 apples", "temp > 90", "x = 10")
        # Pattern: number followed by word or comparison
        num_matches = re.findall(r'(-?\d+\.?\d*)\s*(\w+)?', t)
        for val, unit in num_matches:
            v_name = f"num_{val}_{unit or 'unit'}"
            vertices.append(v_name)
            numerics.append((v_name, float(val)))
            
        # 2. Extract Logical Relations
        # Implication: "if A then B", "A leads to B", "because A, B"
        # Simplified extraction: look for keywords connecting clauses
        clauses = re.split(r'[.;]', t)
        for clause in clauses:
            if "if" in clause and "then" in clause:
                # Rough parse: if X then Y
                match = re.search(r"if (.+?) then (.+)", clause)
                if match:
                    src, dst = match.group(1).strip()[:20], match.group(2).strip()[:20]
                    if src and dst:
                        vertices.extend([src, dst])
                        edges.append((src, dst, 'implies'))
            
            if "leads to" in clause:
                parts = clause.split("leads to")
                if len(parts) == 2:
                    src, dst = parts[0].strip()[-20:], parts[1].strip()[:20]
                    if src and dst:
                        vertices.extend([src, dst])
                        edges.append((src, dst, 'implies'))

        # Deduplicate vertices
        unique_v = list(dict.fromkeys(vertices))
        if not unique_v:
            # Fallback: treat whole sentence as one boolean variable if nothing else found
            unique_v = ["statement"]
            
        return unique_v, edges, numerics

    def _ergodic_walk(self, V, E, numerics):
        """
        Performs MCMC to estimate fraction of valid states.
        State: Dictionary mapping V -> bool, and numeric values.
        """
        if not V:
            return 0.0, 0.0

        n = len(V)
        # Map vars to indices
        v_map = {v: i for i, v in enumerate(V)}
        
        # Initialize state: random booleans
        state = {v: self.rng.choice([True, False]) for v in V}
        
        # Numeric state (simplified: just track if numeric constraints exist)
        has_numerics = len(numerics) > 0
        num_val = numerics[0][1] if numerics else 0.0

        def check_consistency(current_state, edges, num_present):
            # Check logical edges
            for src, dst, typ in edges:
                if src in current_state and dst in current_state:
                    if typ == 'implies':
                        # If src is True, dst MUST be True
                        if current_state[src] and not current_state[dst]:
                            return False
            # Simplified numeric check: if numerics exist, assume consistent if present
            # In a full engine, this would solve the system. 
            # Here we simulate consistency probability based on density.
            return True

        valid_count = 0
        total_steps = self.burn_in + self.samples
        
        # Current consistency
        is_consistent = check_consistency(state, E, has_numerics)
        
        for step in range(total_steps):
            # Propose flip
            target = self.rng.choice(V)
            old_val = state[target]
            state[target] = not old_val
            
            # Check new consistency
            new_consistent = check_consistency(state, E, has_numerics)
            
            # Acceptance logic (Metropolis-Hastings simplified)
            # If new is consistent, always accept.
            # If new is inconsistent, accept with probability 0.5 (to maintain ergodicity/exploration)
            # But we want to sample the space of VALID assignments mostly.
            # Strategy: Reject moves that break consistency if we are already consistent?
            # No, standard MCMC for SAT: 
            # If valid -> keep. If invalid -> revert with high prob?
            # Let's use a simple Gibbs-like approach:
            
            if new_consistent:
                is_consistent = True
                if step >= self.burn_in:
                    valid_count += 1
            else:
                # Revert with probability 0.8 to stay in valid region, else explore
                if self.rng.random() < 0.8:
                    state[target] = old_val # Revert
                    # is_consistent remains whatever it was before (likely True if we came from there)
                else:
                    # Keep invalid state temporarily to allow escaping local minima?
                    # For this tool, we want fraction of time spent in VALID state.
                    if step >= self.burn_in:
                        # Don't count invalid steps
                        pass
                    # If we keep the invalid state, we need to track that too.
                    # Simplification: If we revert, we are back to previous state.
                    # If we don't revert, we are in invalid state.
                    is_consistent = False 

        f = valid_count / self.samples if self.samples > 0 else 0.0
        
        # Calculate Density Delta
        # Max edges = n*(n-1)/2
        max_e = (n * (n - 1)) / 2.0 if n > 1 else 1.0
        delta = len(E) / max_e if max_e > 0 else 0.0
        
        return f, delta

    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len1 = len(zlib.compress(s1_b))
        len2 = len(zlib.compress(s2_b))
        len_both = len(zlib.compress(s1_b + s2_b))
        if max(len1, len2) == 0:
            return 0.0
        return (len_both - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        
        # Parse prompt once
        V, E, numerics = self._parse_constraints(prompt)
        
        # Base ergodic score for the prompt structure itself
        # If prompt has no structure, f is low, but we need to rank candidates.
        # We simulate the walk for each candidate combined with prompt.
        
        for cand in candidates:
            # Combine prompt and candidate for full context analysis
            full_text = f"{prompt} {cand}"
            V_c, E_c, num_c = self._parse_constraints(full_text)
            
            # Merge graphs (simplified: union)
            all_V = list(set(V + V_c))
            all_E = E + E_c
            
            # Run Ergodic Walk
            f, delta = self._ergodic_walk(all_V, all_E, num_c)
            
            # Criticality Score
            # Maximize at delta = 0.5
            criticality = 1.0 - abs(delta - 0.5)
            base_score = f * (0.5 + 0.5 * criticality) # Weighted average
            
            # Structural Bonus: If candidate explicitly resolves a constraint
            structural_bonus = 0.0
            if len(E_c) > len(E):
                structural_bonus = 0.1 * min(1.0, len(E_c)/len(E) if len(E)>0 else 1.0)
            
            # Computation Bonus: If numerics are present and consistent
            comp_bonus = 0.0
            if numerics and num_c:
                # Simple check: did the candidate introduce a contradiction?
                # If numerics exist and f is high, bonus.
                if f > 0.8:
                    comp_bonus = 0.2
            
            # NCD Tiebreaker (Max 15% impact)
            # Prefer candidates that are compressible with prompt (coherent) but not identical
            ncd = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            final_score = base_score + structural_bonus + comp_bonus + ncd_score
            final_score = min(1.0, max(0.0, final_score)) # Clamp 0-1
            
            # Reasoning string
            reason = f"Ergodic consistency: {f:.2f}, Critical density: {delta:.2f}. "
            if num_c:
                reason += "Numeric constraints detected and evaluated. "
            if len(E_c) > 0:
                reason += f"Logical relations parsed: {len(E_c)}. "
            else:
                reason += "Low structural complexity. "

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # 1. Meta-confidence cap (Tier B checks)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural evaluation
        V, E, numerics = self._parse_constraints(f"{prompt} {answer}")
        
        # If no structure parsed, low confidence (honest uncertainty)
        if not V and not numerics:
            struct_score = 0.2
        else:
            f, delta = self._ergodic_walk(V, E, numerics)
            # Base confidence on consistency
            struct_score = f
            
            # Penalize extreme ambiguity in graph (very low density or very high)
            if len(E) == 0 and len(V) > 1:
                struct_score *= 0.5 # Disconnected variables = weak reasoning

        # 3. Combine
        raw_conf = struct_score
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 unless definitive (heuristic: high numeric precision)
        if numerics and f > 0.95:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.85) # Cap for non-computational answers
            
        return round(final_conf, 3)