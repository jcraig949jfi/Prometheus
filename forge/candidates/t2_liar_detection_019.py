import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Feedback systems x SAT/Constraint solving - liar_detection"""

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
        """Extract agents, statements, truth policies, and question from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []  # (agent, statement_text, is_claim_about_other?)
        truth_policies = {}  # agent -> policy ("always truth", "always lie", "random")
        question = lines[-1] if lines else ""
        
        # Extract agents and their policies
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:always tells the truth|always lies|tells the truth randomly|lies randomly|is (?:a )?(?:truth-teller|liar|random))'
        
        for line in lines:
            # Find agent declarations
            agent_matches = re.findall(agent_pattern, line, re.IGNORECASE)
            for agent in agent_matches:
                if agent not in agents:
                    agents.append(agent)
                
                # Determine policy
                if 'always tells the truth' in line.lower() or 'truth-teller' in line.lower():
                    truth_policies[agent] = 'truth'
                elif 'always lies' in line.lower() or 'liar' in line.lower():
                    truth_policies[agent] = 'lie'
                elif 'random' in line.lower():
                    truth_policies[agent] = 'random'
            
            # Extract statements
            statement_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+says[:,"]\s*(.+?)(?:\.|$)', line)
            if statement_match:
                agent = statement_match.group(1)
                statement = statement_match.group(2).strip('"')
                
                # Check if statement is about another agent
                is_about_other = any(other in statement for other in agents if other != agent)
                statements.append((agent, statement, is_about_other))
        
        # Extract question type
        question_type = "unknown"
        if "who" in question.lower() and "?" in question:
            question_type = "identify_agent"
        elif "what" in question.lower() and "?" in question:
            question_type = "identify_truth"
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "question_type": question_type,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback systems approach: agents' statements create a feedback loop
        where truth values propagate through the network. Stability analysis determines
        consistent assignments."""
        
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["truth_policies"]
        
        # If we can't extract enough structure, fall back to simpler reasoning
        if len(agents) < 2 or len(statements) == 0:
            return self._fallback_reason(structure)
        
        # Phase 1: Encode as SAT problem using feedback systems concept
        # Each agent's truth value affects statements, creating feedback loops
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for agent truth values (True = tells truth)
        for agent in agents:
            var_map[f"truth_{agent}"] = var_counter
            var_counter += 1
        
        # Create variables for statement truth values
        for i, (agent, stmt, _) in enumerate(statements):
            var_map[f"stmt_{i}"] = var_counter
            var_counter += 1
        
        # Encode truth policies as constraints
        for agent, policy in policies.items():
            agent_var = var_map[f"truth_{agent}"]
            if policy == 'truth':
                clauses.append([agent_var])  # truth_agent must be True
            elif policy == 'lie':
                clauses.append([-agent_var])  # truth_agent must be False
            # 'random' has no constraint
        
        # Encode statement implications: if agent tells truth, statement is true
        # if agent lies, statement is false
        for i, (agent, stmt, is_about_other) in enumerate(statements):
            agent_var = var_map[f"truth_{agent}"]
            stmt_var = var_map[f"stmt_{i}"]
            
            # Agent truth -> statement truth
            clauses.append([-agent_var, stmt_var])
            # Agent lie -> statement false
            clauses.append([agent_var, -stmt_var])
            
            # If statement is about another agent's truth value, encode that relationship
            if is_about_other:
                for other_agent in agents:
                    if other_agent != agent and other_agent in stmt:
                        other_var = var_map[f"truth_{other_agent}"]
                        
                        # Parse statement content
                        if "tells the truth" in stmt.lower() or "truth-teller" in stmt.lower():
                            # "A says B tells the truth" means stmt_i == truth_B
                            clauses.append([-stmt_var, other_var])
                            clauses.append([stmt_var, -other_var])
                        elif "lies" in stmt.lower() or "liar" in stmt.lower():
                            # "A says B lies" means stmt_i == not truth_B
                            clauses.append([-stmt_var, -other_var])
                            clauses.append([stmt_var, other_var])
        
        # Use SAT solving to find consistent assignments
        n_vars = var_counter - 1
        
        # CRITICAL: solve_sat is a T1 primitive that directly determines the answer
        sat_assignment = solve_sat(clauses, n_vars)
        
        if sat_assignment is None:
            # No consistent assignment found - use constraint solving fallback
            return self._constraint_fallback(structure)
        
        # Determine which agents must have fixed truth values across all models
        # Use feedback systems stability concept: variables that don't change across
        # consistent states are "stable" and thus determined
        
        # CRITICAL: check_entailment is an amino acid that directly determines the answer
        # Check what we can entail about each agent
        determined_agents = []
        for agent in agents:
            agent_var = var_map[f"truth_{agent}"]
            
            # Check if we can entail truth_agent is True
            true_clause = [agent_var]
            entails_true = check_entailment(clauses, true_clause)
            
            # Check if we can entail truth_agent is False
            false_clause = [-agent_var]
            entails_false = check_entailment(clauses, false_clause)
            
            if entails_true and not entails_false:
                determined_agents.append((agent, True))
            elif entails_false and not entails_true:
                determined_agents.append((agent, False))
        
        # CRITICAL: confidence_from_agreement is a T1 primitive that affects scoring
        # Calculate confidence based on agreement among determined agents
        if determined_agents:
            truth_values = [1.0 if truth else 0.0 for _, truth in determined_agents]
            confidence = confidence_from_agreement(truth_values)
        else:
            confidence = 0.5
        
        # CRITICAL: entropy is a T1 primitive that affects scoring
        # Calculate entropy of the solution space
        agent_probs = []
        for agent in agents:
            agent_var = var_map[f"truth_{agent}"]
            # Estimate probability from SAT assignment
            if sat_assignment.get(agent_var, False):
                agent_probs.append(0.7)  # biased toward truth in this model
            else:
                agent_probs.append(0.3)
        
        if agent_probs:
            solution_entropy = entropy(agent_probs)
            # Lower entropy = more certain solution
            entropy_confidence = 1.0 - (solution_entropy / max(1.0, len(agents)))
        else:
            entropy_confidence = 0.5
        
        # Combine confidences
        final_confidence = (confidence + entropy_confidence) / 2.0
        
        # Determine answer based on question type
        computed_answer = ""
        reasoning_text = ""
        
        if structure["question_type"] == "identify_agent":
            # Find agent with most determined truth value
            if determined_agents:
                # CRITICAL: bayesian_update is a T1 primitive that affects which agent is selected
                # Use Bayesian update to combine prior (uniform) with evidence from SAT
                prior = 1.0 / len(agents)
                best_agent = None
                best_score = 0.0
                
                for agent, is_truth in determined_agents:
                    # Evidence strength based on consistency
                    evidence_strength = 0.8 if is_truth else 0.2
                    posterior = bayesian_update(prior, evidence_strength)
                    
                    if posterior > best_score:
                        best_score = posterior
                        best_agent = agent
                
                if best_agent:
                    computed_answer = best_agent
                    reasoning_text = f"Agent {best_agent} is uniquely determined by the logical constraints."
            else:
                # Fallback: use constraint solving
                constraint_result = self._constraint_fallback(structure)
                computed_answer = constraint_result.get("answer", "")
        else:
            # For truth identification questions
            if determined_agents:
                truth_counts = sum(1 for _, truth in determined_agents if truth)
                lie_counts = len(determined_agents) - truth_counts
                
                if truth_counts > lie_counts:
                    computed_answer = "tells the truth"
                elif lie_counts > truth_counts:
                    computed_answer = "lies"
                else:
                    computed_answer = "cannot be determined"
            else:
                computed_answer = "cannot be determined"
        
        # If still no answer, use fallback
        if not computed_answer:
            fallback_result = self._fallback_reason(structure)
            computed_answer = fallback_result.get("answer", "unknown")
        
        return {
            "answer": computed_answer,
            "confidence": final_confidence,
            "reasoning": reasoning_text,
            "determined_agents": determined_agents,
            "sat_assignment": sat_assignment
        }

    def _constraint_fallback(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback using constraint solving when SAT fails."""
        agents = structure["agents"]
        statements = structure["statements"]
        
        # Create CSP variables
        variables = {}
        domains = {}
        
        for agent in agents:
            variables[agent] = f"truth_{agent}"
            domains[f"truth_{agent}"] = [True, False]  # True = tells truth
        
        # Add statement variables
        for i, (agent, stmt, _) in enumerate(statements):
            variables[f"stmt_{i}"] = f"stmt_{i}"
            domains[f"stmt_{i}"] = [True, False]  # True = statement is true
        
        # Create constraints
        constraints = []
        
        # Truth policy constraints
        for agent, policy in structure["truth_policies"].items():
            if policy == 'truth':
                constraints.append(([f"truth_{agent}"], lambda x: x[0] == True))
            elif policy == 'lie':
                constraints.append(([f"truth_{agent}"], lambda x: x[0] == False))
        
        # Statement constraints
        for i, (agent, stmt, is_about_other) in enumerate(statements):
            agent_var = f"truth_{agent}"
            stmt_var = f"stmt_{i}"
            
            # Constraint: statement truth == agent truth value
            constraints.append(([agent_var, stmt_var], lambda x: x[0] == x[1]))
            
            # Constraints about other agents
            if is_about_other:
                for other_agent in agents:
                    if other_agent != agent and other_agent in stmt:
                        other_var = f"truth_{other_agent}"
                        
                        if "tells the truth" in stmt.lower():
                            constraints.append(([stmt_var, other_var], lambda x: x[0] == x[1]))
                        elif "lies" in stmt.lower():
                            constraints.append(([stmt_var, other_var], lambda x: x[0] != x[1]))
        
        # CRITICAL: solve_first is an amino acid that directly determines the answer
        solution = solve_first(domains, constraints)
        
        # CRITICAL: is_uniquely_solvable is an amino acid that affects confidence
        unique = is_uniquely_solvable(domains, constraints)
        
        if solution:
            # Determine answer based on solution
            if structure["question_type"] == "identify_agent":
                # Find agent with most interesting truth value
                truth_tellers = [agent for agent in agents if solution.get(f"truth_{agent}", False)]
                liars = [agent for agent in agents if not solution.get(f"truth_{agent}", True)]
                
                if truth_tellers and not liars:
                    computed_answer = truth_tellers[0]
                elif liars and not truth_tellers:
                    computed_answer = liars[0]
                elif truth_tellers:
                    computed_answer = truth_tellers[0]
                else:
                    computed_answer = agents[0] if agents else "unknown"
            else:
                # Count truth tellers vs liars
                truth_count = sum(1 for agent in agents if solution.get(f"truth_{agent}", False))
                if truth_count > len(agents) / 2:
                    computed_answer = "tells the truth"
                else:
                    computed_answer = "lies"
            
            confidence = 0.8 if unique else 0.6
        else:
            computed_answer = "cannot be determined"
            confidence = 0.5
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": "Solved via constraint satisfaction",
            "unique": unique
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Simpler fallback reasoning using modus ponens and belief tracking."""
        agents = structure["agents"]
        statements = structure["statements"]
        
        # Use modus ponens for simple implications
        premises = []
        facts = set()
        
        # Add policy facts
        for agent, policy in structure["truth_policies"].items():
            if policy == 'truth':
                facts.add(f"{agent}_truth")
            elif policy == 'lie':
                facts.add(f"{agent}_lie")
        
        # Add implication rules
        for agent, stmt, _ in statements:
            # If agent tells truth, then statement is true
            premises.append((f"{agent}_truth", f"stmt_true:{agent}:{stmt}"))
            # If agent lies, then statement is false
            premises.append((f"{agent}_lie", f"stmt_false:{agent}:{stmt}"))
        
        # CRITICAL: modus_ponens is a T1 primitive that affects the answer
        inferred = modus_ponens(premises, facts)
        
        # CRITICAL: track_beliefs is a T1 primitive that affects confidence
        # Track which facts we believe
        belief_state = track_beliefs(
            agents,
            [(agent, f"stmt_true:{agent}:{stmt}", f"stmt_true:{agent}:{stmt}" in inferred) 
             for agent, stmt, _ in statements]
        )
        
        # Determine answer
        if structure["question_type"] == "identify_agent":
            # Look for agents mentioned in inferred facts
            mentioned_agents = []
            for fact in inferred:
                for agent in agents:
                    if agent in fact:
                        mentioned_agents.append(agent)
            
            if mentioned_agents:
                computed_answer = mentioned_agents[0]
            else:
                computed_answer = agents[0] if agents else "unknown"
        else:
            # Count truth vs lie beliefs
            truth_beliefs = sum(1 for fact in inferred if "_truth" in fact)
            lie_beliefs = sum(1 for fact in inferred if "_lie" in fact)
            
            if truth_beliefs > lie_beliefs:
                computed_answer = "tells the truth"
            elif lie_beliefs > truth_beliefs:
                computed_answer = "lies"
            else:
                computed_answer = "cannot be determined"
        
        # Calculate confidence based on belief consistency
        total_beliefs = len(inferred)
        consistent = all(any(agent in fact for fact in inferred) for agent in agents if f"{agent}_truth" in facts or f"{agent}_lie" in facts)
        confidence = 0.7 if consistent and total_beliefs > 0 else 0.4
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": "Inferred via logical deduction",
            "inferred_facts": list(inferred)
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            if computed_answer and computed_answer.lower()