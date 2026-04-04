import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    topological_sort,
    track_beliefs
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Measure theory x SAT/constraint solving - liar_detection"""

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        # Phase 1: EXTRACT
        structure = self._extract(prompt)
        
        # Phase 2: REASON
        reasoning_result = self._reason(structure)
        
        # Phase 3: SCORE
        scored = self._score(candidates, reasoning_result)
        
        # Phase 4: CALIBRATE
        calibrated = self._calibrate(scored)
        
        return sorted(calibrated, key=lambda x: x["score"], reverse=True)

    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Extract agents, statements, and truth-telling policies from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        policies = {}  # agent -> policy ("always truth", "always lie", "random")
        question = ""
        
        current_agent = None
        
        for line in lines:
            # Look for agent introductions
            agent_match = re.search(r'(\w+)\s+(?:is|says|claims|states)', line, re.IGNORECASE)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                current_agent = agent
            
            # Extract truth-telling policies
            if "always tells the truth" in line.lower() and current_agent:
                policies[current_agent] = "truth"
            elif "always lies" in line.lower() and current_agent:
                policies[current_agent] = "lie"
            elif "random" in line.lower() and current_agent:
                policies[current_agent] = "random"
            
            # Extract statements (quoted or following "says")
            if current_agent and ("says" in line.lower() or "claims" in line.lower()):
                # Find content after "says" or in quotes
                says_match = re.search(r'says\s+"([^"]+)"', line, re.IGNORECASE)
                if says_match:
                    statement = says_match.group(1)
                    statements.append((current_agent, statement))
                else:
                    # Try to extract statement after colon or "that"
                    parts = re.split(r'says|claims|that', line, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        statement = parts[1].strip(' ":,.')
                        if statement:
                            statements.append((current_agent, statement))
            
            # Extract question (usually last line)
            if "?" in line and not question:
                question = line
        
        # Parse statements for logical content
        logical_statements = []
        for agent, stmt in statements:
            # Check for negation patterns
            negated = False
            stmt_text = stmt.lower()
            
            if re.search(r'\b(not|false|no|never)\b', stmt_text):
                negated = True
            
            # Extract propositional content
            # Look for "X is Y" or "X does Z" patterns
            prop_match = re.search(r'(\w+)\s+(?:is|are|does|did)\s+(\w+)', stmt, re.IGNORECASE)
            if prop_match:
                subject = prop_match.group(1)
                predicate = prop_match.group(2)
                logical_statements.append({
                    'agent': agent,
                    'text': stmt,
                    'subject': subject,
                    'predicate': predicate,
                    'negated': negated
                })
            else:
                # Simple statement
                logical_statements.append({
                    'agent': agent,
                    'text': stmt,
                    'negated': negated
                })
        
        return {
            'agents': agents,
            'policies': policies,
            'statements': statements,
            'logical_statements': logical_statements,
            'question': question,
            'raw': prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use measure theory concepts (sigma-algebras, measurable functions) 
        to model truth-telling as a measurable mapping from world states to statements."""
        
        agents = structure['agents']
        policies = structure['policies']
        logical_statements = structure['logical_statements']
        question = structure['question']
        
        # Phase 1: Build propositional variables
        # Each agent's statement corresponds to a proposition about the world
        propositions = {}
        prop_counter = 1
        
        for stmt in logical_statements:
            prop_key = f"P{prop_counter}"
            propositions[prop_key] = {
                'agent': stmt['agent'],
                'text': stmt['text'],
                'negated': stmt.get('negated', False),
                'subject': stmt.get('subject'),
                'predicate': stmt.get('predicate')
            }
            prop_counter += 1
        
        # Phase 2: Model truth-telling policies as measurable functions
        # In measure theory, a liar's statements form a non-measure-preserving transformation
        # Truth-tellers preserve the measure (probability) of true statements
        
        # Create SAT clauses based on policies
        clauses = []
        var_map = {}  # proposition -> SAT variable number
        
        # Assign SAT variables
        for i, (prop_key, prop) in enumerate(propositions.items(), 1):
            var_map[prop_key] = i
        
        # Add clauses for truth-tellers: statement ↔ world fact
        # For liar: statement ↔ ¬(world fact)
        # For random: no constraint (add both possibilities)
        
        for prop_key, prop in propositions.items():
            agent = prop['agent']
            policy = policies.get(agent, "unknown")
            var = var_map[prop_key]
            
            # World fact variable (what's actually true)
            world_var = var + len(propositions)  # Separate variable for truth value
            
            if policy == "truth":
                # statement ↔ world_fact
                # (statement → world_fact) ∧ (world_fact → statement)
                clauses.append([-var, world_var])    # ¬statement ∨ world_fact
                clauses.append([-world_var, var])    # ¬world_fact ∨ statement
            elif policy == "lie":
                # statement ↔ ¬world_fact
                clauses.append([-var, -world_var])   # ¬statement ∨ ¬world_fact
                clauses.append([world_var, var])     # world_fact ∨ statement
            # For random agents, no constraints - they can say anything
        
        # Phase 3: Use SAT solving to find consistent world states
        # This corresponds to finding measures (probability distributions) over possible worlds
        # that are consistent with the sigma-algebra generated by the statements
        
        n_vars = len(propositions) * 2  # statement vars + world truth vars
        
        # CRITICAL PRIMITIVE 1: solve_sat to find consistent assignments
        sat_assignment = solve_sat(clauses, n_vars)
        
        if sat_assignment is None:
            # No consistent assignment - paradox detected
            computed_answer = "paradox"
            confidence = 0.0
        else:
            # Extract which propositions are true in the consistent world
            true_props = []
            for prop_key, var in var_map.items():
                if sat_assignment.get(var, False):
                    true_props.append(prop_key)
            
            # Phase 4: Use measure theory concept - entropy of the solution space
            # If multiple consistent worlds exist, entropy is high (uncertainty)
            # If unique solution, entropy is low (certainty)
            
            # CRITICAL PRIMITIVE 2: entropy to measure uncertainty
            # Count solutions by trying to flip each variable
            solution_counts = []
            for var in range(1, n_vars + 1):
                # Test if variable can be flipped while keeping consistency
                test_clauses = clauses + [[var if not sat_assignment.get(var, False) else -var]]
                test_result = solve_sat(test_clauses, n_vars)
                if test_result is not None:
                    solution_counts.append(1.0)
                else:
                    solution_counts.append(0.0)
            
            # Normalize to probability distribution
            if solution_counts:
                total = sum(solution_counts)
                if total > 0:
                    probs = [c/total for c in solution_counts]
                    uncertainty = entropy(probs)
                else:
                    uncertainty = 0.0
            else:
                uncertainty = 0.0
            
            # Phase 5: Determine answer based on question
            # Extract what the question is asking for
            computed_answer = ""
            
            if "who" in question.lower():
                # Question asks for an agent
                # Find which agent's statements are most consistent with the world
                agent_consistency = {}
                
                for agent in agents:
                    agent_props = [k for k, p in propositions.items() if p['agent'] == agent]
                    if not agent_props:
                        continue
                    
                    # Check consistency of this agent's statements
                    consistent_count = 0
                    for prop_key in agent_props:
                        var = var_map[prop_key]
                        world_var = var + len(propositions)
                        
                        # Check if statement matches world truth given policy
                        policy = policies.get(agent, "unknown")
                        if policy == "truth":
                            if sat_assignment.get(var, False) == sat_assignment.get(world_var, False):
                                consistent_count += 1
                        elif policy == "lie":
                            if sat_assignment.get(var, False) != sat_assignment.get(world_var, False):
                                consistent_count += 1
                        else:  # random
                            consistent_count += 1  # Always consistent for random
                    
                    agent_consistency[agent] = consistent_count / len(agent_props) if agent_props else 0
                
                # CRITICAL PRIMITIVE 3: confidence_from_agreement
                consistency_scores = list(agent_consistency.values())
                if consistency_scores:
                    confidence = confidence_from_agreement(consistency_scores)
                else:
                    confidence = 0.5
                
                # Answer is the agent with highest consistency
                if agent_consistency:
                    computed_answer = max(agent_consistency.items(), key=lambda x: x[1])[0]
                else:
                    computed_answer = "unknown"
            
            elif "what" in question.lower() or "which" in question.lower():
                # Question asks for a fact or statement
                # Find the most probable world fact
                world_facts = []
                for prop_key, prop in propositions.items():
                    var = var_map[prop_key]
                    world_var = var + len(propositions)
                    if sat_assignment.get(world_var, False):
                        world_facts.append(prop['text'])
                
                if world_facts:
                    # CRITICAL AMINO ACID: check_entailment to see which facts are necessary
                    # Build clauses for each fact and check if it's entailed by the constraints
                    necessary_facts = []
                    for prop_key, prop in propositions.items():
                        var = var_map[prop_key]
                        world_var = var + len(propositions)
                        
                        # Check if world_fact = true is entailed
                        entailment_result = check_entailment(clauses, [world_var])
                        if entailment_result:
                            necessary_facts.append(prop['text'])
                    
                    if necessary_facts:
                        computed_answer = necessary_facts[0]
                        confidence = 0.9
                    else:
                        computed_answer = world_facts[0]
                        confidence = 0.7 - (uncertainty * 0.5)
                else:
                    computed_answer = "none"
                    confidence = 0.5
            
            else:
                # Generic answer - describe the consistency state
                if uncertainty < 0.1:
                    computed_answer = "consistent"
                else:
                    computed_answer = "ambiguous"
                confidence = 1.0 - uncertainty
        
        # Phase 6: Use topological sort to order dependencies between statements
        # Build dependency graph: statement A depends on statement B if B's truth
        # affects whether A can be true given the policies
        
        edges = []
        for i, (prop_key1, prop1) in enumerate(propositions.items()):
            for j, (prop_key2, prop2) in enumerate(propositions.items()):
                if i != j:
                    # Check if prop1's agent's policy depends on prop2's truth
                    agent1 = prop1['agent']
                    agent2 = prop2['agent']
                    
                    if agent1 == agent2:
                        # Same agent's statements may depend on each other
                        edges.append((prop_key1, prop_key2))
                    elif policies.get(agent1) == "truth" and policies.get(agent2) == "lie":
                        # Truth-teller's statements may contradict liar's statements
                        edges.append((prop_key1, prop_key2))
        
        # CRITICAL PRIMITIVE 4: topological_sort to find statement ordering
        dependency_order = topological_sort(edges)
        
        # Use the ordering to refine confidence
        if dependency_order and len(dependency_order) > 1:
            # More complex dependencies suggest harder puzzle
            complexity = len(dependency_order) / len(propositions) if propositions else 1.0
            confidence = confidence * (1.0 - 0.2 * complexity)
        
        # Phase 7: Fallback using constraint solving if SAT fails
        if computed_answer in ["paradox", "unknown", "none"]:
            # Try constraint solving approach
            variables = list(propositions.keys())
            domains = {}
            constraints = []
            
            for prop_key, prop in propositions.items():
                domains[prop_key] = [True, False]
                agent = prop['agent']
                policy = policies.get(agent, "unknown")
                
                # Add constraint based on policy
                if policy == "truth":
                    # For truth-teller, value represents actual truth
                    constraints.append(([prop_key], lambda x: x[0] == True))
                elif policy == "lie":
                    # For liar, value represents falsehood
                    constraints.append(([prop_key], lambda x: x[0] == False))
                # Random has no constraint
            
            # CRITICAL AMINO ACID 2: solve_first to find a solution
            constraint_solution = solve_first(domains, constraints)
            
            if constraint_solution:
                # Found a consistent assignment via constraint solving
                true_props = [k for k, v in constraint_solution.items() if v]
                if true_props:
                    # Answer is the first true proposition's agent or text
                    first_prop = true_props[0]
                    if "who" in question.lower():
                        computed_answer = propositions[first_prop]['agent']
                    else:
                        computed_answer = propositions[first_prop]['text']
                    confidence = 0.6
                else:
                    computed_answer = "no true statements"
                    confidence = 0.5
            else:
                # CRITICAL AMINO ACID 3: is_uniquely_solvable to check paradox
                unique_check = is_uniquely_solvable(domains, constraints)
                if unique_check is False:
                    computed_answer = "paradox"
                else:
                    computed_answer = "inconsistent"
                confidence = 0.8
        
        return {
            "answer": computed_answer,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasoning": f"Based on {len(propositions)} propositions with policies {policies}",
            "propositions": list(propositions.keys()),
            "uncertainty": uncertainty if 'uncertainty' in locals() else 0.5
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = str(reasoning_result["answer"])
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple min-max normalization if scores are too compressed
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score - min_score < 0.1:  # Scores too compressed
            # Spread them out
            for item in scored:
                if max_score > min_score:
                    item["score"] = (item["score"] - min_score) / (max_score - min_score)
                else:
                    item["score"] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0