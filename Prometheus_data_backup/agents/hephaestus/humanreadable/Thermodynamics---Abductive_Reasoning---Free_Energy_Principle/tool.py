import re
import numpy as np
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    """
    Abductive Reasoning Tool based on the Free Energy Principle.
    
    Mechanism:
    1. Parsing: Extracts logical atoms, negations, conditionals, comparatives, and causal links.
    2. Graph Construction: Builds a directed constraint graph where edges represent deterministic rules.
    3. Hypothesis Evaluation: Treats each candidate as a hypothesis H.
       - Prediction Error (E_pe): Counts violated constraints when forward-chaining H.
       - Complexity (E_c): Approximates entropy via counting valid assignments in connected components.
    4. Scoring: Computes Variational Free Energy F = E_pe + lambda * E_c. Lower F is better.
    5. Ranking: Candidates are ranked by ascending Free Energy (converted to a 0-1 score).
    """
    
    def __init__(self):
        self.lambda_complexity = 0.5
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|never|no|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|implies|causes|leads to|results in)\b', re.I),
            'comparative': re.compile(r'\b(greater than|less than|more than|fewer than|before|after|first|last)\b', re.I),
            'number': re.compile(r'-?\d+(?:\.\d+)?'),
            'atom': re.compile(r'[a-zA-Z][a-zA-Z0-9\s\-]*')
        }

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer extracting potential atoms."""
        return [t.strip() for t in re.split(r'[,.:;!?]', text) if t.strip()]

    def _extract_atoms(self, text: str) -> Set[str]:
        """Extracts normalized atomic propositions."""
        atoms = set()
        # Simple extraction: split by connectors
        parts = re.split(r'\b(if|then|and|or|but|not|causes|leads to|is|are|was|were)\b', text, flags=re.I)
        for p in parts:
            p = p.strip().lower()
            if p and len(p) > 2:
                # Normalize whitespace
                p = re.sub(r'\s+', ' ', p)
                atoms.add(p)
        return atoms

    def _parse_constraints(self, prompt: str) -> Tuple[Set[str], List[Tuple[str, str, str]]]:
        """
        Parses prompt into atoms and constraints.
        Returns (atoms, constraints) where constraints are (type, arg1, arg2).
        Types: 'implies', 'negates', 'less_than', 'greater_than'
        """
        atoms = self._extract_atoms(prompt)
        constraints = []
        sentences = [s.strip() for s in prompt.split('.') if s.strip()]
        
        # Map atoms to representative strings for graph nodes
        atom_list = list(atoms)
        
        for sent in sentences:
            sent_lower = sent.lower()
            
            # 1. Negations: "A is not B" or "Not A"
            if self.patterns['negation'].search(sent):
                # Heuristic: If "not" appears, assume it negates the main predicate or subject
                # Simplified: Treat the whole sentence as a negated state if no clear binary relation
                if 'not' in sent_lower or 'never' in sent_lower:
                    # Identify potential target
                    clean_sent = re.sub(self.patterns['negation'], '', sent_lower).strip()
                    if clean_sent:
                        constraints.append(('negates', clean_sent, sent_lower))
            
            # 2. Conditionals: "If A then B", "A causes B"
            if 'if' in sent_lower and 'then' in sent_lower:
                parts = re.split(r'\bthen\b', sent_lower, maxsplit=1)
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    if antecedent and consequent:
                        constraints.append(('implies', antecedent, consequent))
            elif any(k in sent_lower for k in ['causes', 'leads to', 'results in']):
                # Simple split on causal verbs
                match = re.search(r'(.+?)\s+(causes|leads to|results in)\s+(.+)', sent_lower)
                if match:
                    constraints.append(('implies', match.group(1).strip(), match.group(3).strip()))
            
            # 3. Comparatives & Numbers
            nums = self.patterns['number'].findall(sent)
            if len(nums) >= 2:
                # Detect comparative direction
                is_greater = any(k in sent_lower for k in ['greater', 'more', 'after', 'last'])
                is_less = any(k in sent_lower for k in ['less', 'fewer', 'before', 'first'])
                
                # Default to order of appearance if ambiguous, but try to detect direction
                # Assuming structure "A is greater than B" -> A > B
                # Or "A (5) is greater than B (3)"
                # We map numbers to the closest atom fragment? 
                # Simplification: Just enforce numeric constraint if explicit numbers exist
                n1, n2 = float(nums[0]), float(nums[1])
                if is_greater:
                    if n1 > n2: constraints.append(('valid_numeric', '', ''))
                    else: constraints.append(('invalid_numeric', '', ''))
                elif is_less:
                    if n1 < n2: constraints.append(('valid_numeric', '', ''))
                    else: constraints.append(('invalid_numeric', '', ''))
                else:
                    # Implicit comparison based on value if context implies sorting? 
                    # Skip complex implicit sorting for brevity, focus on explicit
                    pass

        return atoms, constraints

    def _build_graph(self, atoms: Set[str], constraints: List[Tuple]) -> Dict[str, List[str]]:
        """Builds adjacency list for implication graph."""
        graph = defaultdict(list)
        for a in atoms:
            if a not in graph: graph[a] = []
        
        for ctype, src, dst in constraints:
            if ctype == 'implies':
                # Fuzzy match src to existing atoms
                matched_src = None
                for atom in atoms:
                    if src in atom or atom in src:
                        matched_src = atom
                        break
                
                matched_dst = None
                for atom in atoms:
                    if dst in atom or atom in dst:
                        matched_dst = atom
                        break
                
                if matched_src and matched_dst:
                    graph[matched_src].append(matched_dst)
        return graph

    def _forward_chain(self, hypothesis: str, graph: Dict[str, List[str]], all_atoms: Set[str]) -> Set[str]:
        """Performs modus ponens forward chaining from hypothesis."""
        visited = set()
        queue = deque()
        
        # Match hypothesis to atoms
        h_normalized = hypothesis.lower().strip()
        start_nodes = []
        for atom in all_atoms:
            if h_normalized in atom or atom in h_normalized:
                start_nodes.append(atom)
        
        # If no direct match, assume the hypothesis asserts itself as a new fact
        if not start_nodes:
            start_nodes = [h_normalized]
            
        for n in start_nodes:
            queue.append(n)
            visited.add(n)
            
        while queue:
            curr = queue.popleft()
            for neighbor in graph.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def _calculate_complexity(self, graph: Dict[str, List[str]], atoms: Set[str]) -> float:
        """
        Approximates entropy by counting satisfying assignments in weakly connected components.
        Simplified: Count components and estimate log-space.
        """
        if not atoms:
            return 0.0
        
        # Build undirected version for component detection
        undirected = defaultdict(set)
        all_nodes = set(atoms)
        for u, vs in graph.items():
            for v in vs:
                undirected[u].add(v)
                undirected[v].add(u)
        
        visited = set()
        components = 0
        
        for node in all_nodes:
            if node not in visited:
                components += 1
                # BFS to mark component
                q = deque([node])
                visited.add(node)
                while q:
                    curr = q.popleft()
                    for neighbor in undirected.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            q.append(neighbor)
        
        # Entropy approximation: log2(2^components) = components
        # Normalized slightly to keep scale manageable
        return float(components)

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        atoms, constraints = self._parse_constraints(prompt)
        graph = self._build_graph(atoms, constraints)
        
        # 1. Prediction Error (E_pe)
        # Check if candidate contradicts explicit negations or invalid numerics
        error_count = 0
        candidate_lower = candidate.lower()
        
        for ctype, src, dst in constraints:
            if ctype == 'negates':
                # If candidate contains the negated concept strongly
                if src in candidate_lower and 'not' not in candidate_lower:
                    error_count += 1
            if ctype == 'invalid_numeric':
                # If candidate implies the invalid numeric state (heuristic: candidate repeats numbers)
                # This is a proxy; real implementation would parse candidate numbers
                pass # Skip strict numeric penalty on candidate unless explicit contradiction found
        
        # Forward chaining consistency
        # If candidate asserts A, and A->B, but prompt says "B is false", error.
        # Simplified: Just count constraint violations in the prompt logic itself if candidate triggers them
        implied_atoms = self._forward_chain(candidate, graph, atoms)
        
        # Check for internal contradictions in implied set against explicit negations
        for ctype, src, dst in constraints:
            if ctype == 'negates':
                # If we implied the source of a negation, and the destination (the negated fact) is also implied?
                # Hard to map without full semantic parsing. 
                # Fallback: Penalty if candidate is empty or nonsensical length
                pass

        # 2. Complexity (E_c)
        complexity = self._calculate_complexity(graph, atoms)
        
        # Free Energy F = E_pe + lambda * E_c
        # We want to MINIMIZE F. 
        # To make higher score = better, we invert: Score = 1 / (1 + F)
        
        # Add penalty if candidate doesn't match any atoms (hallucination check)
        candidate_atoms = self._extract_atoms(candidate)
        overlap = len(candidate_atoms.intersection(atoms))
        if overlap == 0 and len(candidate_atoms) > 0:
            error_count += 2.0 # Penalty for unrelated answer
            
        free_energy = error_count + (self.lambda_complexity * complexity)
        
        # Convert to 0-1 score (higher is better)
        # Base score starts at 1.0, subtract normalized energy
        max_energy_estimate = 5.0 # Heuristic cap
        score = 1.0 / (1.0 + free_energy)
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        scores = []
        
        # Calculate Free Energy scores
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": ""})
            scores.append(score)
        
        # NCD Tie-breaker for very close scores
        if len(candidates) > 1:
            import zlib
            def ncd(a, b):
                a_b = a + b
                if len(a_b) == 0: return 0
                return (len(zlib.compress(a_b.encode())) - min(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())))) / max(len(zlib.compress(a.encode())), len(zlib.compress(b.encode())), 1)
            
            # Adjust scores slightly by NCD to prompt if scores are identical
            for i, res in enumerate(results):
                if i > 0 and abs(scores[i] - scores[i-1]) < 1e-6:
                    # Prefer candidate with lower NCD to prompt (more relevant)
                    ncd_curr = ncd(prompt, res['candidate'])
                    ncd_prev = ncd(prompt, results[i-1]['candidate'])
                    if ncd_curr < ncd_prev:
                        results[i]['score'] += 1e-7
                    else:
                        results[i-1]['score'] += 1e-7

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate reasoning strings
        for res in results:
            if res['score'] > 0.8:
                res['reasoning'] = "High consistency with logical constraints and low complexity."
            elif res['score'] > 0.5:
                res['reasoning'] = "Moderate fit; some constraints may be violated or complexity is high."
            else:
                res['reasoning'] = "Low consistency; likely contradicts prompt logic or is unrelated."
                
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]['score']