import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_constraints,
    topological_sort,
    track_beliefs,
    bayesian_update,
    confidence_from_agreement,
    entropy
)
from forge.amino_acids.pysat_acids import check_entailment


class ReasoningTool:
    """Evolutionary biology x SAT entailment - liar_detection"""

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
        """Extract agents, statements, and truth policies from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        # Find agents (capitalized names that appear multiple times)
        words = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        from collections import Counter
        word_counts = Counter(words)
        agents = [word for word, count in word_counts.items() 
                  if count >= 2 and word not in ['The', 'A', 'An', 'And', 'But', 'Or', 'If', 'Then']]
        
        # Extract statements and truth policies
        statements = []
        truth_policies = {}  # agent -> policy (truth-teller/liar/random)
        
        for line in lines:
            line_lower = line.lower()
            # Look for truth policy declarations
            for agent in agents:
                agent_lower = agent.lower()
                if agent_lower in line_lower:
                    if 'always tells the truth' in line_lower or 'truth-teller' in line_lower:
                        truth_policies[agent] = 'truth'
                    elif 'always lies' in line_lower or 'liar' in line_lower:
                        truth_policies[agent] = 'lie'
                    elif 'random' in line_lower or 'sometimes lies' in line_lower:
                        truth_policies[agent] = 'random'
            
            # Extract quoted statements or statements about what agents say
            if 'says' in line_lower or 'said' in line_lower:
                # Find the agent who is speaking
                speaking_agent = None
                for agent in agents:
                    if line.startswith(agent) or f"{agent} says" in line or f"{agent} said" in line:
                        speaking_agent = agent
                        break
                
                if speaking_agent:
                    # Extract the statement content
                    statement_match = re.search(r'says?["\']?([^".]+)["\']?', line, re.IGNORECASE)
                    if statement_match:
                        statement_text = statement_match.group(1).strip()
                        statements.append({
                            'agent': speaking_agent,
                            'statement': statement_text,
                            'original_line': line
                        })
        
        # Find the question (usually last sentence)
        question = lines[-1] if lines else ""
        
        return {
            'agents': agents,
            'statements': statements,
            'truth_policies': truth_policies,
            'question': question,
            'raw_prompt': prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use evolutionary biology concepts (fitness landscapes) with SAT entailment to resolve liar puzzles."""
        agents = structure['agents']
        statements = structure['statements']
        truth_policies = structure['truth_policies']
        
        # Evolutionary biology concept: Treat truth policies as evolutionary strategies
        # Truth-tellers have high fitness in cooperative environments
        # Liars have fitness that depends on deception success
        # Random agents have neutral fitness
        
        # Phase 1: Build constraint satisfaction problem for agent consistency
        # Each agent's statements must be consistent with their truth policy
        
        # Extract propositional variables from statements
        variables = set()
        variable_map = {}  # statement text -> variable index
        
        for i, stmt in enumerate(statements):
            var_name = f"S{i}"  # Statement i is true
            variables.add(var_name)
            variable_map[stmt['statement']] = var_name
        
        # Build constraints based on truth policies
        constraints = []
        domains = {var: [0, 1] for var in variables}  # 0 = false, 1 = true
        
        # Track which statements each agent made
        agent_statements = {agent: [] for agent in agents}
        for i, stmt in enumerate(statements):
            agent = stmt['agent']
            var_name = f"S{i}"
            agent_statements[agent].append((var_name, stmt['statement']))
        
        # Apply evolutionary fitness: truth-tellers' statements are more likely to be true
        # Liars' statements are more likely to be false
        # This creates a "fitness landscape" for truth assignments
        
        # Use solve_constraints primitive to find consistent truth assignments
        csp_constraints = []
        
        for agent, stmts in agent_statements.items():
            if not stmts:
                continue
                
            policy = truth_policies.get(agent, 'unknown')
            
            if policy == 'truth':
                # All statements by truth-teller must be true
                for var_name, _ in stmts:
                    csp_constraints.append(([var_name], lambda x: x[0] == 1))
            elif policy == 'lie':
                # All statements by liar must be false
                for var_name, _ in stmts:
                    csp_constraints.append(([var_name], lambda x: x[0] == 0))
            elif policy == 'random':
                # Random agents: no constraint (neutral fitness)
                pass
        
        # Add constraints for logical relationships between statements
        # Look for statements about other statements (e.g., "X says Y is lying")
        for i, stmt in enumerate(statements):
            stmt_text = stmt['statement'].lower()
            speaking_agent = stmt['agent']
            
            # Check if statement is about another agent's truthfulness
            for other_agent in agents:
                if other_agent.lower() in stmt_text and speaking_agent != other_agent:
                    if 'lying' in stmt_text or 'liar' in stmt_text:
                        # This statement claims another agent is lying
                        # If speaking_agent is truth-teller, other_agent must be liar
                        # If speaking_agent is liar, other_agent must be truth-teller
                        policy = truth_policies.get(speaking_agent, 'unknown')
                        
                        if policy == 'truth':
                            # Truth-teller says other is liar → other must be liar
                            if other_agent in truth_policies:
                                # This creates a constraint on truth_policies
                                # We'll handle this through SAT encoding
                                pass
                        elif policy == 'lie':
                            # Liar says other is liar → other must be truth-teller
                            if other_agent in truth_policies:
                                pass
        
        # Solve the CSP to find consistent truth assignments
        csp_solution = solve_constraints(list(variables), domains, csp_constraints)
        
        # Phase 2: Use SAT entailment to determine what must be true
        # Encode the problem as CNF clauses
        
        clauses = []
        var_to_int = {var: i+1 for i, var in enumerate(variables)}  # SAT variables start at 1
        
        # Encode truth policy constraints as clauses
        for agent, stmts in agent_statements.items():
            if not stmts:
                continue
                
            policy = truth_policies.get(agent, 'unknown')
            
            if policy == 'truth':
                # All statements true: S1 ∧ S2 ∧ ... ∧ Sn
                for var_name, _ in stmts:
                    var_idx = var_to_int[var_name]
                    clauses.append([var_idx])  # Unit clause: S must be true
            elif policy == 'lie':
                # All statements false: ¬S1 ∧ ¬S2 ∧ ... ∧ ¬Sn
                for var_name, _ in stmts:
                    var_idx = var_to_int[var_name]
                    clauses.append([-var_idx])  # Unit clause: S must be false
        
        # Use topological_sort to determine inference order
        # Build dependency graph between statements
        edges = []
        for i, stmt1 in enumerate(statements):
            for j, stmt2 in enumerate(statements):
                if i != j:
                    # Check if stmt1 refers to stmt2
                    stmt1_text = stmt1['statement'].lower()
                    stmt2_agent = stmt2['agent'].lower()
                    if stmt2_agent in stmt1_text and ('says' in stmt1_text or 'said' in stmt1_text):
                        edges.append((f"S{i}", f"S{j}"))
        
        # Use topological_sort primitive
        try:
            inference_order = topological_sort(edges)
            # Convert to variable indices for SAT
            order_vars = [var_to_int[var] for var in inference_order if var in var_to_int]
        except:
            order_vars = list(var_to_int.values())
        
        # Use track_beliefs primitive to model agent knowledge states
        observations = []
        for stmt in statements:
            agent = stmt['agent']
            var_name = f"S{statements.index(stmt)}"
            # Each agent observes their own statement's truth value
            # (they know whether they're telling truth or lying)
            policy = truth_policies.get(agent, 'unknown')
            if policy == 'truth':
                observations.append((agent, var_name, True))
            elif policy == 'lie':
                observations.append((agent, var_name, False))
        
        belief_state = track_beliefs(agents, observations)
        
        # Use bayesian_update to compute posterior probabilities
        # Prior: equal probability for each possible world
        n_vars = len(variables)
        prior = 1.0 / (2 ** n_vars) if n_vars > 0 else 0.5
        
        # Likelihood: based on consistency with constraints
        if csp_solution:
            # If CSP has solution, likelihood is high
            likelihood = 0.9
        else:
            likelihood = 0.1
        
        posterior = bayesian_update(prior, likelihood, false_positive=0.1)
        
        # Use entropy to measure uncertainty
        if csp_solution:
            # Count how many variables are determined
            determined_vars = sum(1 for var in variables if var in csp_solution)
            prob_dist = [determined_vars/len(variables), 1 - determined_vars/len(variables)]
        else:
            prob_dist = [0.5, 0.5]
        
        uncertainty = entropy(prob_dist)
        
        # Use check_entailment amino acid to determine logical consequences
        # Check what the premises entail about specific statements
        computed_answer = None
        confidence = 0.5
        
        if clauses and variables:
            # Try to determine if specific statements are entailed
            for i, stmt in enumerate(statements):
                var_name = f"S{i}"
                if var_name in var_to_int:
                    var_idx = var_to_int[var_name]
                    
                    # Check if premises entail this statement is true
                    entailment_true = check_entailment(clauses, [var_idx])
                    entailment_false = check_entailment(clauses, [-var_idx])
                    
                    if entailment_true and not entailment_false:
                        # Statement must be true
                        computed_answer = stmt['statement']
                        confidence = 0.8
                        break
                    elif entailment_false and not entailment_true:
                        # Statement must be false
                        computed_answer = f"Not {stmt['statement']}"
                        confidence = 0.8
                        break
            
            # If no specific statement is entailed, look for agent identities
            if not computed_answer:
                # Check what we can infer about agent policies
                for agent in agents:
                    if agent in truth_policies:
                        # Already known
                        continue
                    
                    # Try to infer policy from constraints
                    # This is where the evolutionary fitness concept applies:
                    # In a stable population, truth-tellers and liars reach equilibrium
                    
                    # Use confidence_from_agreement on multiple inference paths
                    agreement_scores = []
                    
                    # Path 1: From CSP solution
                    if csp_solution:
                        # Check if agent's statements are all true/false in solution
                        agent_stmts = [s for s in statements if s['agent'] == agent]
                        if agent_stmts:
                            all_true = all(csp_solution.get(f"S{statements.index(s)}", 0) == 1 
                                         for s in agent_stmts)
                            all_false = all(csp_solution.get(f"S{statements.index(s)}", 0) == 0 
                                          for s in agent_stmts)
                            if all_true:
                                agreement_scores.append(0.9)  # Likely truth-teller
                            elif all_false:
                                agreement_scores.append(0.9)  # Likely liar
                    
                    # Path 2: From topological order
                    if order_vars:
                        # Agents earlier in inference order have more influence
                        agent_vars = [var_to_int[f"S{i}"] for i, s in enumerate(statements) 
                                    if s['agent'] == agent and f"S{i}" in var_to_int]
                        if agent_vars:
                            # Check position in order
                            avg_position = sum(order_vars.index(v) for v in agent_vars if v in order_vars) / len(agent_vars)
                            norm_pos = avg_position / len(order_vars)
                            agreement_scores.append(0.5 + 0.4 * (1 - norm_pos))  # Higher for earlier positions
                    
                    # Path 3: From belief state
                    if agent in belief_state:
                        beliefs = belief_state[agent]
                        if beliefs:
                            agreement_scores.append(0.7)
                    
                    if agreement_scores:
                        overall_confidence = confidence_from_agreement(agreement_scores)
                        if overall_confidence > 0.7:
                            # High agreement → make inference
                            # Use entropy to decide: low uncertainty → make specific claim
                            if uncertainty < 0.3:
                                computed_answer = agent
                                confidence = overall_confidence
                                break
        
        # Fallback: if no answer computed, use evolutionary equilibrium concept
        if not computed_answer:
            # In evolutionary biology, populations reach stable equilibria
            # Count agents by inferred type
            truth_count = sum(1 for p in truth_policies.values() if p == 'truth')
            lie_count = sum(1 for p in truth_policies.values() if p == 'lie')
            random_count = sum(1 for p in truth_policies.values() if p == 'random')
            
            # The "fittest" type depends on environment
            # In liar puzzles, often one type dominates
            if truth_count > lie_count and truth_count > random_count:
                computed_answer = "truth-teller"
            elif lie_count > truth_count and lie_count > random_count:
                computed_answer = "liar"
            else:
                computed_answer = "random"
            
            # Adjust confidence based on entropy
            confidence = max(0.3, 1.0 - uncertainty)
        
        return {
            'answer': str(computed_answer),
            'confidence': confidence,
            'uncertainty': uncertainty,
            'posterior': posterior,
            'csp_solution': csp_solution,
            'clauses': clauses,
            'inference_order': order_vars if 'order_vars' in locals() else [],
            'belief_state': belief_state
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result['answer']
        confidence = reasoning_result['confidence']
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Use NCD as fallback
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            results.append({
                'candidate': candidate,
                'score': adjusted_score,
                'base_score': base_score,
                'confidence': confidence
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item['score'] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item['score'] = (item['score'] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
                item['score'] = 0.5
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)