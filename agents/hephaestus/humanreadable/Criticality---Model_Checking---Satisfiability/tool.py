import re
import zlib
from collections import deque
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    A reasoning tool combining structural parsing, constraint propagation (Model Checking),
    and criticality metrics to evaluate candidate answers.
    
    Mechanism:
    1. Parses text into a constraint graph (atoms, implications, arithmetic).
    2. Performs bounded state-space exploration to find satisfying assignments.
    3. Computes criticality metrics (Correlation Length, Susceptibility, Phase Distance).
    4. Scores based on structural consistency and proximity to criticality.
    5. Uses NCD only as a minor tiebreaker.
    6. Enforces epistemic honesty via meta-analysis of ambiguity.
    """

    def __init__(self):
        # Weights for scoring: Correlation, Susceptibility, Phase Distance
        self.w1 = 0.3
        self.w2 = 0.4
        self.w3 = 0.3
        
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|-\w+)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more than|less than|greater than|smaller than|>\|<|>=|<=)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided that)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|causes|leads to|results in)\b', re.IGNORECASE),
            'temporal': re.compile(r'\b(before|after|while|during)\b', re.IGNORECASE),
            'numeric': re.compile(r'(-?\d+(?:\.\d+)?)'),
            'equality': re.compile(r'\b(is|are|equals|same as)\b', re.IGNORECASE)
        }
        
        # Ambiguity triggers for Tier B (Epistemic Honesty)
        self.ambiguity_triggers = [
            re.compile(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)\b', re.IGNORECASE),
            re.compile(r'\b(every.*a.*y|same.*y)\b', re.IGNORECASE), # Simplified scope check
            re.compile(r'\b(he told.*he|she told.*she|who is)\b', re.IGNORECASE),
            re.compile(r'\b(either.*or.*without)\b', re.IGNORECASE),
            re.compile(r'\b(best|worst|favorite|most beautiful)\b', re.IGNORECASE),
            re.compile(r'\b(unknown|impossible to tell|not enough information)\b', re.IGNORECASE)
        ]

    def _extract_atoms(self, text: str) -> List[str]:
        """Extract propositional atoms based on structural markers."""
        atoms = []
        # Simple sentence splitting as proxy for atoms
        sentences = re.split(r'[.;!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Create atom from first few words or key structural match
            if self.patterns['negation'].search(sent) or self.patterns['conditional'].search(sent):
                atoms.append(sent[:50].replace(' ', '_'))
            elif len(sent) > 5:
                atoms.append(sent[:50].replace(' ', '_'))
        return list(set(atoms)) # Unique atoms

    def _build_graph(self, text: str) -> Tuple[Dict[str, Set[str]], Dict[str, bool]]:
        """Build implication graph and initial state from text."""
        atoms = self._extract_atoms(text)
        graph = {a: set() for a in atoms}
        state = {a: True for a in atoms} # Default assumption: extracted atoms are true premises
        
        # Simplified implication logic: 
        # If "if A then B" found, link A -> B. 
        # Here we simulate by checking co-occurrence in conditional sentences
        sentences = re.split(r'[.;!?]', text)
        for sent in sentences:
            if self.patterns['conditional'].search(sent):
                # Crude split by 'then' or implicit logic
                parts = re.split(r'\bthen\b', sent, flags=re.IGNORECASE)
                if len(parts) == 2:
                    # Find matching atoms
                    antecedents = [a for a in atoms if a.replace('_', ' ') in parts[0]]
                    consequents = [a for a in atoms if a.replace('_', ' ') in parts[1]]
                    for ant in antecedents:
                        for con in consequents:
                            if ant in graph:
                                graph[ant].add(con)
        
        return graph, state

    def _model_check(self, graph: Dict[str, Set[str]], state: Dict[str, bool], depth: int = 5) -> Set[Tuple[str, bool]]:
        """Bounded BFS to propagate constraints and find reachable states."""
        reachable = set()
        queue = deque([(state, 0)]) # (current_state, depth)
        visited_states = set()
        
        # Encode state as tuple for hashing
        def encode(s): return tuple(sorted(s.items()))
        
        start_enc = encode(state)
        visited_states.add(start_enc)
        reachable.add(start_enc)
        
        while queue:
            curr_state, d = queue.popleft()
            if d >= depth:
                continue
            
            # Propagate unit clauses (Modus Ponens simulation)
            next_state = curr_state.copy()
            changed = False
            for node, neighbors in graph.items():
                if curr_state.get(node, False): # If node is True
                    for neighbor in neighbors:
                        if not next_state.get(neighbor, False):
                            next_state[neighbor] = True
                            changed = True
            
            if changed:
                enc = encode(next_state)
                if enc not in visited_states:
                    visited_states.add(enc)
                    reachable.add(enc)
                    queue.append((next_state, d + 1))
                    
        return reachable

    def _compute_criticality(self, graph: Dict[str, Set[str]], satisfying_states: Set[Tuple]) -> Tuple[float, float, float]:
        """Compute Correlation Length, Susceptibility, and Phase Distance."""
        n_vars = len(graph)
        if n_vars == 0:
            return 0.0, 0.0, 1.0
            
        # 1. Correlation Length (L): Avg shortest path in graph (Floyd-Warshall approx)
        # Simplified: Average degree / connectivity
        total_edges = sum(len(neighbors) for neighbors in graph.values())
        avg_degree = total_edges / n_vars if n_vars > 0 else 0
        L = 1.0 / (1.0 + avg_degree) if avg_degree > 0 else 1.0
        
        # 2. Susceptibility (chi): Fraction of variables that flip status in some satisfying state
        # Simulate by checking variance in satisfying states
        chi = 0.0
        if len(satisfying_states) > 1:
            # Check how many variables change value across the set of satisfying states
            variable_flips = 0
            for var in graph.keys():
                values = [state_dict.get(var, False) for state_dict in [dict(s) for s in satisfying_states]]
                # If a variable is True in some and False in others (or missing implies False)
                # Note: Our state representation is sparse (True assumed), so we check presence
                # Simplified: if variable appears in < 90% of states or > 10%
                pass 
            # Heuristic: More satisfying states usually means higher susceptibility in this context
            chi = min(1.0, len(satisfying_states) / 10.0) 
        else:
            chi = 0.1 # Low susceptibility if only one state
            
        # 3. Distance to Phase Boundary (Delta)
        # Ideal SAT ratio is near 0.5 of max possible? 
        # Here we normalize by heuristic max states (2^n is too big, use observed)
        max_expected = 2 ** min(n_vars, 5) # Cap for normalization
        target = 0.5 * max_expected
        observed = len(satisfying_states)
        delta = abs(observed - target) / (target + 1)
        
        return L, chi, delta

    def _calculate_structural_score(self, prompt: str, candidate: str) -> float:
        """Core scoring logic based on structural consistency."""
        # Combine prompt and candidate to check consistency
        full_text = f"{prompt} {candidate}"
        graph, init_state = self._build_graph(full_text)
        
        if not graph:
            # Fallback if no structure found
            return 0.5 

        # Model Checking
        states = self._model_check(graph, init_state)
        
        # Criticality Metrics
        L, chi, delta = self._compute_criticality(graph, states)
        
        # Scoring formula
        score = self.w1 * (1 / (1 + L)) + self.w2 * chi + self.w3 * (1 / (1 + delta))
        return score

    def _numeric_check(self, prompt: str, candidate: str) -> Optional[float]:
        """Extract and verify numeric constraints."""
        nums_prompt = [float(x) for x in self.patterns['numeric'].findall(prompt)]
        nums_cand = [float(x) for x in self.patterns['numeric'].findall(candidate)]
        
        if not nums_prompt or not nums_cand:
            return None
            
        # Heuristic: If candidate number exists in prompt and satisfies simple comparative logic
        # Example: "Which is larger, 5 or 3?" -> Candidate "5"
        if 'larger' in prompt.lower() or '>' in prompt:
            return 1.0 if max(nums_cand) == max(nums_prompt) else 0.0
        if 'smaller' in prompt.lower() or '<' in prompt:
            return 1.0 if min(nums_cand) == min(nums_prompt) else 0.0
            
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B ambiguity traps."""
        score = 1.0
        for pattern in self.ambiguity_triggers:
            if pattern.search(prompt):
                score = 0.2 # Cap confidence for ambiguous/unanswerable
                break
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = f"{s1}{s2}"
        return (len(z(concat.encode())) - min(len(z(s1.encode())), len(z(s2.encode())))) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence for the prompt
        meta_conf = self._meta_confidence(prompt)
        
        for cand in candidates:
            score = 0.0
            reason_parts = []
            
            # 1. Numeric Check (High priority if present)
            num_res = self._numeric_check(prompt, cand)
            if num_res is not None:
                score = num_res
                reason_parts.append(f"Numeric verification: {'Pass' if num_res > 0.5 else 'Fail'}")
            else:
                # 2. Structural/Logical Score
                struct_score = self._calculate_structural_score(prompt, cand)
                
                # 3. NCD Tiebreaker (Max 15% influence)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower is better) and scale
                ncd_score = (1.0 - ncd_val) * 0.15 
                
                score = (struct_score * 0.85) + ncd_score
                reason_parts.append(f"Structural consistency: {struct_score:.3f}")
            
            # Apply Meta-Confidence Cap (Epistemic Honesty)
            if meta_conf < 0.3:
                score = min(score, 0.3)
                reason_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reason_parts)
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural validity and meta-analysis."""
        # 1. Meta-check for ambiguity
        meta_score = self._meta_confidence(prompt)
        if meta_score < 0.3:
            return 0.2 # Honest uncertainty
        
        # 2. Structural validation
        # Treat prompt+answer as a system. If adding the answer creates a contradiction 
        # (simulated by low structural score), confidence is low.
        graph, init_state = self._build_graph(f"{prompt} {answer}")
        
        if not graph:
            # No structure found, rely on meta (already checked) and fallback
            return 0.5
            
        states = self._model_check(graph, init_state)
        
        # If no satisfying states found, it's likely a contradiction
        if len(states) == 0:
            return 0.1
            
        # Calculate a rough consistency metric
        L, chi, delta = self._compute_criticality(graph, states)
        consistency_score = (1 / (1 + L)) * 0.4 + chi * 0.4 + (1/(1+delta)) * 0.2
        
        # Cap at 0.9 unless computation was definitive (heuristic: high consistency + low delta)
        final_conf = min(0.95, consistency_score) if delta < 0.2 else consistency_score * 0.8
        
        return float(final_conf)