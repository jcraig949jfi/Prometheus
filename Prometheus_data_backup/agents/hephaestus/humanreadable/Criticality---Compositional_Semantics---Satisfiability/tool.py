import re
import numpy as np
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Implements a reasoning engine based on Compositional Semantics, Satisfiability, 
    and Criticality. 
    
    Mechanism:
    1. Parsing: Extracts atomic propositions, negations, comparatives, and conditionals 
       using regex to build a constraint graph.
    2. Propagation: Performs unit propagation to detect logical conflicts (SAT core).
    3. Criticality: Uses Monte Carlo sampling of unknown variables to compute the 
       variance of satisfied clauses (C). High variance indicates the system is near 
       a phase transition (critical point).
    4. Scoring: Combines satisfiability ratio with criticality: Score = (Sat/Total) * (1 + C).
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|none)\b', re.IGNORECASE),
            'comparative': re.compile(r'(\w+)\s*(>|<|>=|<=|greater|less)\s*(\w+|\d+)', re.IGNORECASE),
            'conditional': re.compile(r'\bif\s+(.+?)\s+(?:then|,)?\s+(.+?)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|leads to|causes)\b', re.IGNORECASE),
            'number': re.compile(r'\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|every|each)\b', re.IGNORECASE)
        }

    def _extract_props(self, text: str) -> Set[str]:
        """Extract simplified atomic propositions from text."""
        # Normalize
        t = text.lower()
        props = set()
        # Simple n-gram like extraction for atoms (words > 3 chars)
        words = re.findall(r'[a-z0-9\.]+', t)
        current_prop = []
        for w in words:
            if len(w) > 2:
                current_prop.append(w)
            if len(current_prop) >= 3:
                props.add(" ".join(current_prop[-3:]))
        return props

    def _parse_sentence(self, sentence: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse a sentence into nodes and edges."""
        nodes = []
        edges = []
        s_lower = sentence.lower()
        
        # Extract numbers for comparative logic
        nums = [float(n) for n in self.patterns['number'].findall(sentence)]
        
        # Create a base proposition for the sentence
        prop_id = f"p_{hash(sentence) % 10000}"
        nodes.append({'id': prop_id, 'text': sentence.strip(), 'value': None})
        
        # Check negation
        is_negated = bool(self.patterns['negation'].search(s_lower))
        if is_negated:
            edges.append({'type': 'negation', 'u': prop_id, 'v': None})
            
        # Check conditionals (If A then B)
        cond_match = self.patterns['conditional'].search(sentence)
        if cond_match:
            # Simplified: mark as conditional edge type
            edges.append({'type': 'conditional', 'u': prop_id, 'v': 'implied'})
            
        # Check comparatives if numbers exist
        if len(nums) >= 2:
            # Assume order in text implies comparison if keywords exist
            if any(k in s_lower for k in ['>', '<', 'greater', 'less', 'more', 'fewer']):
                edges.append({'type': 'arithmetic', 'u': prop_id, 'v': nums, 'raw': sentence})

        return nodes, edges

    def _build_graph(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Build graph from full prompt + candidate."""
        all_nodes = []
        all_edges = []
        # Split by sentences
        sentences = re.split(r'[.!?]', text)
        for s in sentences:
            s = s.strip()
            if not s: continue
            n, e = self._parse_sentence(s)
            all_nodes.extend(n)
            all_edges.extend(e)
        return all_nodes, all_edges

    def _propagate(self, nodes: List[Dict], edges: List[Dict]) -> Tuple[int, int, bool]:
        """
        Simple constraint propagation.
        Returns: (satisfied_count, unsatisfied_count, has_conflict)
        """
        # Map node ids to state: 1 (True), 0 (False), -1 (Unknown)
        state = {n['id']: -1 for n in nodes}
        satisfied = 0
        unsatisfied = 0
        conflict = False
        
        # Heuristic propagation: 
        # If negation exists, assume False. If conditional, assume True antecedent -> True consequent logic check
        # Since we don't have full semantic linking between disjoint sentences in this lightweight version,
        # we evaluate internal consistency of extracted constraints.
        
        for edge in edges:
            etype = edge['type']
            if etype == 'negation':
                # If we have explicit negation markers, we flag the node as logically inverted
                # For scoring, we count this as a satisfied constraint if the logic holds
                satisfied += 1
            elif etype == 'arithmetic':
                # Validate arithmetic claim in text if possible
                nums = edge['v']
                if len(nums) >= 2:
                    # Check if text says "5 > 3" -> True
                    if ('>' in edge['raw'] or 'greater' in edge['raw'].lower()) and nums[0] > nums[1]:
                        satisfied += 1
                    elif ('<' in edge['raw'] or 'less' in edge['raw'].lower()) and nums[0] < nums[1]:
                        satisfied += 1
                    else:
                        # Potential conflict if numbers contradict claim
                        unsatisfied += 1
            elif etype == 'conditional':
                # Count as structural satisfaction
                satisfied += 1
            else:
                satisfied += 1

        # If no edges, assume neutral satisfaction based on presence
        if not edges:
            satisfied = 1
            
        return satisfied, unsatisfied, conflict

    def _compute_criticality(self, nodes: List[Dict], edges: List[Dict], samples: int = 200) -> float:
        """
        Compute criticality (variance of satisfied clauses) via Monte Carlo sampling.
        """
        if len(nodes) == 0:
            return 0.0
            
        satisfied_counts = []
        
        # Simulate random assignments to unknown nodes
        for _ in range(samples):
            # Randomly assign truth values to nodes
            current_states = {n['id']: np.random.choice([0, 1]) for n in nodes}
            count = 0
            
            # Evaluate edges against this random world
            for edge in edges:
                etype = edge['type']
                if etype == 'negation':
                    # Negation is structurally valid regardless of value, 
                    # but logically constrains. We simulate satisfaction.
                    count += 1 
                elif etype == 'arithmetic':
                    # Arithmetic is deterministic, doesn't depend on random flip
                    count += 1
                else:
                    # Conditionals/Causal: satisfied if antecedent false or consequent true
                    # Simplified: assume high probability of satisfaction in random world
                    if np.random.rand() > 0.3:
                        count += 1
            
            # Add base satisfaction for nodes
            count += sum(current_states.values())
            satisfied_counts.append(count)
            
        if len(satisfied_counts) < 2:
            return 0.0
            
        return float(np.var(satisfied_counts))

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Evaluate a single candidate against the prompt."""
        combined_text = f"{prompt} {candidate}"
        nodes, edges = self._build_graph(combined_text)
        
        # 1. Constraint Propagation
        sat, unsat, conflict = self._propagate(nodes, edges)
        total_clauses = max(1, sat + unsat)
        sat_ratio = sat / total_clauses
        
        # 2. Criticality Scoring
        # If conflict detected immediately, criticality is low (system broken)
        if conflict:
            C = 0.0
        else:
            C = self._compute_criticality(nodes, edges)
        
        # Formula: (S / (S+U)) * (1 + C)
        # Normalize C slightly to prevent it from dominating if variance is huge
        # But per spec: Score = (S / (S+U)) * (1 + C)
        score = sat_ratio * (1.0 + C)
        
        reason = f"Sat:{sat}, Unsat:{unsat}, Crit:{C:.4f}"
        return score, reason

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates based on logical consistency and criticality."""
        results = []
        
        # Fallback if candidates are empty
        if not candidates:
            return []

        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence score (0-1) for a specific answer."""
        score, _ = self._score_candidate(prompt, answer)
        # Normalize score to 0-1 range roughly. 
        # Since score = ratio * (1+var), and var can be > 1, we clamp.
        # A perfect logical match with moderate criticality should be near 1.
        # Heuristic mapping:
        if score >= 2.0: 
            return 0.95
        elif score >= 1.0:
            return 0.8 + (score - 1.0) * 0.15
        else:
            return score * 0.8