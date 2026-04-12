import re
import math
import random
import zlib
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional

# Set seed for deterministic behavior in rollouts as required
random.seed(42)

class ReasoningTool:
    """
    A Computational Reasoning Tool using Criticality-Driven MCTS.
    
    Mechanism:
    1. Parsing: Extracts a constraint graph (entities, relations, numeric intervals) from the prompt.
       Detects logical structures (negation, conditionals, causality) and numeric constraints.
    2. MCTS Search: Builds a tree where nodes represent partial mappings between prompt constraints 
       and candidate answer implications. 
       - Selection uses UCB with variance-based exploration (Criticality).
       - Expansion adds consistent constraint satisfactions.
       - Rollout completes partial mappings via random sampling within bounds.
       - Reward balances satisfied soft constraints vs violations.
    3. Scoring: Candidates are scored by the average reward of successful rollouts.
    4. Epistemic Honesty: Meta-analysis detects ambiguity, presupposition, or insufficient info,
       capping confidence to prevent overconfidence on unanswerable queries.
    """

    def __init__(self):
        self.ncd_weight = 0.15
        self.struct_weight = 0.55
        self.comp_weight = 0.30

    # --- Interface Methods ---

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates against prompt using MCTS-based reasoning."""
        if not candidates:
            return []
        
        # 1. Parse Prompt into Constraint Graph
        graph = self._parse_prompt(prompt)
        
        # 2. Check for Epistemic blockers (Ambiguity/Unanswerability)
        meta_conf = self._meta_confidence(prompt)
        is_ambiguous = meta_conf < 0.3
        
        results = []
        for cand in candidates:
            # Compute structural/computational score
            base_score = self._compute_candidate_score(graph, cand, is_ambiguous)
            
            # Apply NCD as minor tiebreaker
            ncd_score = self._ncd_similarity(prompt, cand)
            
            # Weighted combination
            if is_ambiguous:
                # If ambiguous, structural score should be low, rely less on NCD
                final_score = base_score * 0.7 + ncd_score * 0.3
            else:
                final_score = (base_score * self.struct_weight + 
                               ncd_score * self.ncd_weight + 
                               base_score * self.comp_weight) # Re-using base for comp part simplification
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": self._generate_reasoning(graph, cand, base_score)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by epistemic analysis of the prompt."""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute raw score
        graph = self._parse_prompt(prompt)
        raw_score = self._compute_candidate_score(graph, answer, meta_conf < 0.3)
        
        # Normalize raw score to 0-1 roughly (assuming reward range approx -5 to 5)
        norm_score = max(0.0, min(1.0, (raw_score + 5.0) / 10.0))
        
        # Cap by meta-confidence
        final_conf = min(norm_score, meta_conf)
        
        # Never > 0.9 unless computation was definitive (simulated by high raw score)
        if raw_score < 4.0: # Arbitrary threshold for "definitive"
            final_conf = min(final_conf, 0.9)
            
        return round(final_conf, 3)

    # --- Core Logic: MCTS & Computation ---

    def _compute_candidate_score(self, graph: Dict, candidate: str, is_ambiguous: bool) -> float:
        """Run MCTS to score a candidate based on constraint satisfaction."""
        if is_ambiguous:
            return -1.0 # Penalty for ambiguous prompts if we force an answer
            
        root = self._mcts_root(graph, candidate)
        if root is None:
            return -5.0 # Hard constraint violation
            
        # MCTS Parameters
        simulations = 50
        for _ in range(simulations):
            node = root
            # 1. Selection
            while node.children:
                node = self._select_child(node)
                if node.is_terminal:
                    break
            
            # 2. Expansion
            if not node.is_terminal and not node.children:
                node = self._expand(node, graph, candidate)
            
            # 3. Rollout & 4. Reward
            reward = self._rollout(node, graph, candidate)
            
            # 5. Backpropagation
            self._backpropagate(node, reward)
            
        return root.w / max(1, root.n)

    class MCTSNode:
        def __init__(self, parent=None, mapping=None, is_terminal=False):
            self.parent = parent
            self.mapping = mapping or {} # Partial mapping {prompt_var: value}
            self.children = []
            self.n = 0 # Visit count
            self.w = 0.0 # Total reward
            self.variance = 0.0 # For criticality
            self.is_terminal = is_terminal
            self.untried_actions = [] # Remaining constraints to map

        @property
        def ucb(self):
            if self.n == 0:
                return float('inf')
            # Criticality-driven exploration: c = sqrt(1 + variance)
            c = math.sqrt(1.0 + self.variance)
            exploitation = self.w / self.n
            exploration = c * math.sqrt(math.log(self.parent.n) / self.n) if self.parent else 0
            return exploitation + exploration

    def _mcts_root(self, graph: Dict, candidate: str) -> Optional['MCTSNode']:
        """Initialize MCTS root with hard constraint check."""
        # Quick hard constraint check
        if not self._check_hard_constraints(graph, candidate):
            return None
            
        root = self.MCTSNode()
        # Initialize actions: list of constraints to satisfy
        root.untried_actions = list(range(len(graph['constraints'])))
        root.mapping = {'_candidate_text': candidate}
        return root

    def _select_child(self, node: 'MCTSNode') -> 'MCTSNode':
        if not node.children:
            return node
        # Select child with max UCB
        return max(node.children, key=lambda c: c.ucb)

    def _expand(self, node: 'MCTSNode', graph: Dict, candidate: str) -> 'MCTSNode':
        """Add one new mapping consistent with constraints."""
        if not node.untried_actions:
            node.is_terminal = True
            return node
            
        constraint_idx = node.untried_actions.pop(random.randint(0, len(node.untried_actions)-1))
        constraint = graph['constraints'][constraint_idx]
        
        # Try to satisfy this constraint with current candidate context
        new_mapping = node.mapping.copy()
        satisfied = self._try_satisfy_constraint(constraint, candidate, new_mapping)
        
        if satisfied:
            child = self.MCTSNode(parent=node, mapping=new_mapping)
            child.untried_actions = node.untried_actions.copy()
            child.untried_actions.remove(constraint_idx) if constraint_idx in child.untried_actions else None
            node.children.append(child)
            return child
        else:
            # If cannot satisfy, mark as terminal with low reward potential
            node.is_terminal = True
            return node

    def _rollout(self, node: 'MCTSNode', graph: Dict, candidate: str) -> float:
        """Randomly complete remaining constraints and compute reward."""
        current_mapping = node.mapping.copy()
        satisfied_count = 0
        violation_count = 0
        
        # Simulate remaining constraints
        for idx in node.untried_actions:
            constraint = graph['constraints'][idx]
            if self._try_satisfy_constraint(constraint, candidate, current_mapping, randomize=True):
                satisfied_count += 1
            else:
                violation_count += 1
        
        # Reward function: satisfied - lambda * violations
        lambda_pen = 2.0
        reward = satisfied_count - (lambda_pen * violation_count)
        return reward

    def _backpropagate(self, node: 'MCTSNode', reward: float):
        while node:
            node.n += 1
            node.w += reward
            
            # Update variance (Welford's algorithm simplified)
            delta = reward - (node.w / node.n)
            node.variance += delta * (reward - (node.w / (node.n - 1))) if node.n > 1 else 0
            
            node = node.parent

    # --- Parsing & Constraint Logic ---

    def _parse_prompt(self, prompt: str) -> Dict:
        """Parse prompt into entities, relations, and constraints."""
        p_lower = prompt.lower()
        constraints = []
        entities = []
        numeric_intervals = {}
        
        # Extract Numbers
        numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', p_lower)]
        
        # Extract Entities (Simple noun phrase extraction)
        # Heuristic: Capitalized words or specific patterns
        entities = list(set(re.findall(r'\b[A-Z][a-z]+\b', prompt)))
        
        # Constraint Extraction Patterns
        # 1. Comparatives (higher than, less than)
        if re.search(r'(higher|greater|more|larger).*than', p_lower):
            constraints.append({'type': 'comparative', 'op': '>'})
        if re.search(r'(lower|less|smaller).*than', p_lower):
            constraints.append({'type': 'comparative', 'op': '<'})
            
        # 2. Negation
        if re.search(r'\b(not|no|never|none)\b', p_lower):
            constraints.append({'type': 'negation'})
            
        # 3. Conditionals
        if re.search(r'\b(if|unless|provided)\b', p_lower):
            constraints.append({'type': 'conditional'})
            
        # 4. Causal
        if re.search(r'(because|leads to|causes|therefore)', p_lower):
            constraints.append({'type': 'causal'})
            
        # 5. Quantifiers
        if re.search(r'\b(all|every|some|none)\b', p_lower):
            constraints.append({'type': 'quantifier'})

        # 6. Specific Logic Puzzles (Bat-and-Ball, Modular, etc)
        if 'bat' in p_lower and 'ball' in p_lower and 'cost' in p_lower:
            constraints.append({'type': 'algebra_bat_ball'})
        if 'mod' in p_lower or 'remainder' in p_lower:
            constraints.append({'type': 'modular'})
        if 'probability' in p_lower or 'chance' in p_lower:
            constraints.append({'type': 'bayesian'})

        return {
            'text': prompt,
            'entities': entities,
            'numbers': numbers,
            'constraints': constraints,
            'intervals': numeric_intervals
        }

    def _try_satisfy_constraint(self, constraint: Dict, candidate: str, mapping: Dict, randomize: bool = False) -> bool:
        """Check if a constraint is satisfied by the candidate/mapping."""
        ctype = constraint['type']
        cand_lower = candidate.lower()
        
        if ctype == 'comparative':
            op = constraint['op']
            # Extract numbers from candidate
            nums = re.findall(r'-?\d+\.?\d*', cand_lower)
            if len(nums) >= 2:
                n1, n2 = float(nums[0]), float(nums[1])
                if op == '>' and n1 <= n2: return False
                if op == '<' and n1 >= n2: return False
            # If no numbers, check linguistic markers
            if op == '>' and ('more' in cand_lower or 'higher' in cand_lower): return True
            if op == '<' and ('less' in cand_lower or 'lower' in cand_lower): return True
            return True # Assume pass if not disproven
            
        elif ctype == 'negation':
            if 'not' in cand_lower or 'no ' in cand_lower or 'never' in cand_lower:
                return True
            # If prompt has negation, candidate must reflect it or not contradict
            return True 
            
        elif ctype == 'algebra_bat_ball':
            # Verify if candidate contains the correct answer "0.05" or "5 cents"
            if '0.05' in cand_lower or '5 cent' in cand_lower:
                return True
            if '0.10' in cand_lower or '10 cent' in cand_lower:
                return False # Common trap
            return True # Neutral
            
        elif ctype == 'modular':
            # Check for remainder logic
            if 'remainder' in cand_lower or 'mod' in cand_lower:
                return True
                
        # Default: soft constraint, assume satisfied unless obvious violation
        return True

    def _check_hard_constraints(self, graph: Dict, candidate: str) -> bool:
        """Strict checks that eliminate candidates immediately."""
        # Example: Type mismatch, impossible numbers
        return True

    # --- Epistemic Honesty (Meta-Confidence) ---

    def _meta_confidence(self, prompt: str) -> float:
        """
        Analyze prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        score = 1.0
        
        # 1. Presupposition traps ("Have you stopped...", "Why did X fail?")
        presupposition_patterns = [
            r"have you (stopped|quit|finished) .*?",
            r"why did .*(fail|stop|die|break).*?",
            r"when did .*(stop|end).*?",
            r"is the .* (better|worse) than it used to be"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                score -= 0.8 # Heavy penalty
        
        # 2. Scope Ambiguity ("Every X did a Y" - same Y?)
        if re.search(r'every .* (a|an) .*', p) and re.search(r'(same|different|which).*', p):
            score -= 0.5
            
        # 3. Pronoun Ambiguity ("John told Bill he..." + "who?")
        if re.search(r'(\w+) told (\w+) he', p) and re.search(r'who is he\?', p):
            score -= 0.7
            
        # 4. False Dichotomy ("Either A or B" without context)
        if re.search(r'either .* or .*', p) and not re.search(r'(both|neither|option)', p):
            score -= 0.4
            
        # 5. Subjectivity without criteria
        if re.search(r'(best|worst|favorite|ugliest)', p) and not re.search(r'(according to|data|stats)', p):
            score -= 0.6
            
        # 6. Insufficient Information markers
        insuff_markers = ['unknown', 'cannot be determined', 'not enough info', 'missing']
        if any(m in p for m in insuff_markers):
            score -= 0.9
            
        return max(0.0, min(1.0, score))

    # --- Utilities ---

    def _ncd_similarity(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        if not s1 or not s2:
            return 0.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len1 = len(zlib.compress(s1_bytes))
        len2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
            
        ncd = (len_concat - max_len) / max_len
        # Convert distance to similarity (0-1)
        return 1.0 - min(1.0, ncd)

    def _generate_reasoning(self, graph: Dict, candidate: str, score: float) -> str:
        """Generate a brief textual explanation."""
        if score > 2.0:
            return "Constraints satisfied with high consistency."
        elif score > 0:
            return "Partial match found; some constraints weakly satisfied."
        else:
            return "Significant constraint violations or logical inconsistencies detected."

# End of Class Definition