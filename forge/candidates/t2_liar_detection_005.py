import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    solve_sat,
    modus_ponens,
    track_beliefs,
    confidence_from_agreement,
    entropy,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """Game theory x SAT/Constraint solving - liar_detection"""

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
        """Extract agents, statements, and truth-telling policies from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy (e.g., "always lies", "always tells truth")
        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear as subjects)
        for line in lines:
            # Look for patterns like "Alice says", "Bob claims", etc.
            agent_matches = re.findall(r'([A-Z][a-z]+)\s+(?:says|claims|states|asserts|tells)', line)
            agents.extend(agent_matches)
            
            # Extract truth policies
            if "always tells the truth" in line.lower() or "always truthful" in line.lower():
                for agent in agent_matches:
                    truth_policies[agent] = "truthful"
            elif "always lies" in line.lower() or "always false" in line.lower():
                for agent in agent_matches:
                    truth_policies[agent] = "liar"
            elif "random" in line.lower() or "sometimes lies" in line.lower():
                for agent in agent_matches:
                    truth_policies[agent] = "random"
            
            # Extract statements (content after "says" or similar)
            if agent_matches:
                statement_match = re.search(r'says|claims|states|asserts|tells[:\s]+["\']?([^"\'.]+)', line)
                if statement_match:
                    statements.append({
                        "agent": agent_matches[0],
                        "content": statement_match.group(1).strip()
                    })
        
        # Remove duplicates
        agents = list(set(agents))
        
        # Extract propositional variables (simple facts mentioned)
        facts = set()
        for line in lines:
            # Look for simple factual statements
            fact_matches = re.findall(r'([A-Z][a-z]+\s+(?:is|are|has|have|was|were)\s+[^\.]+)', line)
            facts.update([f.lower() for f in fact_matches])
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "facts": list(facts),
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use game-theoretic reasoning with SAT and constraint solving to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        question = structure["question"]
        
        # Game theory: Model as a signaling game where agents' truthfulness affects credibility
        # We'll use SAT to find consistent truth assignments
        
        # Phase 1: Encode statements as propositional logic
        # Create variables for each statement's truth value
        statement_vars = {}
        var_counter = 1
        
        for i, stmt in enumerate(statements):
            statement_vars[f"S{i}"] = var_counter
            var_counter += 1
        
        # Create variables for each agent's actual truthfulness (if not given)
        agent_truth_vars = {}
        for agent in agents:
            if agent not in truth_policies:
                agent_truth_vars[f"A_{agent}_truthful"] = var_counter
                var_counter += 1
        
        # Build SAT clauses based on truth policies
        clauses = []
        
        for i, stmt in enumerate(statements):
            agent = stmt["agent"]
            policy = truth_policies.get(agent, "unknown")
            stmt_var = statement_vars[f"S{i}"]
            
            if policy == "truthful":
                # If agent is truthful, statement must be true
                clauses.append([stmt_var])  # S_i must be true
            elif policy == "liar":
                # If agent always lies, statement must be false
                clauses.append([-stmt_var])  # S_i must be false
            elif policy == "random":
                # Random: no constraint (both true and false possible)
                pass
            else:  # unknown policy
                # Create implication: if agent is truthful, statement is true
                # A_agent_truthful -> S_i
                agent_var = agent_truth_vars[f"A_{agent}_truthful"]
                clauses.append([-agent_var, stmt_var])
                # If agent is liar, statement is false
                # ¬A_agent_truthful -> ¬S_i
                clauses.append([agent_var, -stmt_var])
        
        # Add consistency constraints: statements about each other
        # Look for statements that reference other agents' truthfulness
        for i, stmt in enumerate(statements):
            content = stmt["content"].lower()
            for other_agent in agents:
                if other_agent.lower() in content:
                    # Check if statement is about other agent's truthfulness
                    if "truthful" in content or "tells the truth" in content:
                        # "X says Y is truthful"
                        if f"A_{other_agent}_truthful" in agent_truth_vars:
                            other_var = agent_truth_vars[f"A_{other_agent}_truthful"]
                            stmt_var = statement_vars[f"S{i}"]
                            # S_i ↔ A_Y_truthful
                            clauses.append([-stmt_var, other_var])  # S_i -> A_Y_truthful
                            clauses.append([stmt_var, -other_var])  # ¬S_i -> ¬A_Y_truthful
                    elif "liar" in content or "lies" in content:
                        # "X says Y is a liar"
                        if f"A_{other_agent}_truthful" in agent_truth_vars:
                            other_var = agent_truth_vars[f"A_{other_agent}_truthful"]
                            stmt_var = statement_vars[f"S{i}"]
                            # S_i ↔ ¬A_Y_truthful
                            clauses.append([-stmt_var, -other_var])  # S_i -> ¬A_Y_truthful
                            clauses.append([stmt_var, other_var])    # ¬S_i -> A_Y_truthful
        
        # Use SAT solving to find consistent assignments
        n_vars = var_counter - 1
        
        # T1 PRIMITIVE 1: solve_sat - critical for finding consistent truth assignments
        sat_assignment = solve_sat(clauses, n_vars)
        
        if sat_assignment is None:
            # No consistent assignment found - use constraint solving fallback
            return self._fallback_reasoning(structure)
        
        # T1 PRIMITIVE 2: modus_ponens - apply logical inference
        # Convert SAT assignment to facts for modus_ponens
        premises = []
        facts_set = set()
        
        for i, stmt in enumerate(statements):
            stmt_var = statement_vars[f"S{i}"]
            if sat_assignment.get(stmt_var, False):
                # Statement is true
                content = stmt["content"]
                # Create simple implication if possible
                if "if" in content.lower() and "then" in content.lower():
                    parts = content.lower().split("then")
                    if len(parts) == 2:
                        antecedent = parts[0].replace("if", "").strip()
                        consequent = parts[1].strip()
                        premises.append((antecedent, consequent))
                facts_set.add(content)
        
        # Apply modus ponens
        inferred_facts = modus_ponens(premises, facts_set)
        
        # T1 PRIMITIVE 3: track_beliefs - track what each agent believes
        # Based on their statements and truth policies
        observations = []
        for stmt in statements:
            agent = stmt["agent"]
            content = stmt["content"]
            stmt_var = statement_vars[f"S{statements.index(stmt)}"]
            is_true = sat_assignment.get(stmt_var, False)
            observations.append((agent, content, is_true))
        
        agent_beliefs = track_beliefs(agents, observations)
        
        # Determine which agent(s) are actually truthful based on SAT assignment
        truthful_agents = []
        for agent in agents:
            if f"A_{agent}_truthful" in agent_truth_vars:
                agent_var = agent_truth_vars[f"A_{agent}_truthful"]
                if sat_assignment.get(agent_var, False):
                    truthful_agents.append(agent)
            elif truth_policies.get(agent) == "truthful":
                truthful_agents.append(agent)
        
        # AMINO ACID: check_entailment - critical for determining logical consequences
        # Check what the question entails from the premises
        question_clauses = []
        # Encode question as a clause (simplified)
        if "who" in question.lower() and "truthful" in question.lower():
            # Question about who is truthful
            for agent in agents:
                if f"A_{agent}_truthful" in agent_truth_vars:
                    agent_var = agent_truth_vars[f"A_{agent}_truthful"]
                    # Create clause for "agent is truthful"
                    question_clauses.append([agent_var])
        
        if question_clauses:
            # Check if premises entail each possible answer
            entailment_results = []
            for q_clause in question_clauses:
                result = check_entailment(clauses, q_clause)
                entailment_results.append(result)
            
            # T1 PRIMITIVE 4: confidence_from_agreement - measure agreement among entailment results
            confidence_scores = [1.0 if r else 0.0 for r in entailment_results]
            if confidence_scores:
                confidence = confidence_from_agreement(confidence_scores)
            else:
                confidence = 0.5
        else:
            confidence = 0.5
        
        # Determine the answer based on game-theoretic equilibrium
        # In signaling games, truthful agents' statements are credible
        computed_answer = ""
        if truthful_agents:
            # If we can identify truthful agents, their statements reveal the truth
            # Find statements by truthful agents
            truthful_statements = [
                stmt["content"] for stmt in statements 
                if stmt["agent"] in truthful_agents
            ]
            
            if truthful_statements:
                # Use the most informative statement
                # T1 PRIMITIVE 5: entropy - measure information content
                statement_probs = [0.5] * len(truthful_statements)  # Simplified
                info_content = entropy(statement_probs) if len(statement_probs) > 1 else 0.0
                
                # Select statement with highest information (simplified)
                computed_answer = truthful_statements[0]
                
                # Extract entity from statement if possible
                entities = re.findall(r'([A-Z][a-z]+)', computed_answer)
                if entities:
                    computed_answer = entities[0]
            else:
                # No statements from truthful agents
                computed_answer = "Cannot determine"
        else:
            # No truthful agents identified
            computed_answer = "Inconsistent"
        
        # If we have a specific question about an agent, use that
        if "who" in question.lower():
            for agent in agents:
                if agent.lower() in question.lower():
                    if agent in truthful_agents:
                        computed_answer = f"{agent} is truthful"
                    else:
                        computed_answer = f"{agent} is not truthful"
                    break
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "truthful_agents": truthful_agents,
            "sat_assignment": sat_assignment,
            "agent_beliefs": agent_beliefs,
            "reasoning": f"Game-theoretic analysis with {len(truthful_agents)} truthful agents identified"
        }

    def _fallback_reasoning(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning using constraint solving when SAT fails."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        
        # Create CSP variables
        variables = []
        domains = {}
        constraints = []
        
        # Variables for each statement's truth value
        for i, stmt in enumerate(statements):
            var_name = f"S{i}"
            variables.append(var_name)
            domains[var_name] = [True, False]
        
        # Variables for each agent's truthfulness (if unknown)
        for agent in agents:
            if agent not in truth_policies:
                var_name = f"A_{agent}"
                variables.append(var_name)
                domains[var_name] = [True, False]  # True = truthful, False = liar
        
        # Constraints based on truth policies
        for i, stmt in enumerate(statements):
            agent = stmt["agent"]
            policy = truth_policies.get(agent, "unknown")
            stmt_var = f"S{i}"
            
            if policy == "truthful":
                # Constraint: statement must be true
                constraints.append(([stmt_var], lambda s: s[0] == True))
            elif policy == "liar":
                # Constraint: statement must be false
                constraints.append(([stmt_var], lambda s: s[0] == False))
            elif policy == "unknown":
                # Link agent truthfulness to statement truth
                agent_var = f"A_{agent}"
                if agent_var in variables:
                    # Constraint: agent truthful ↔ statement true
                    constraints.append(([stmt_var, agent_var], 
                                      lambda vals: vals[0] == vals[1]))
        
        # AMINO ACID: solve_first - find a consistent assignment
        solution = solve_first(domains, constraints)
        
        if solution is None:
            # Still no solution - use topological analysis
            # T1 PRIMITIVE: topological_sort - analyze dependency structure
            edges = []
            for i, stmt in enumerate(statements):
                content = stmt["content"].lower()
                for other_agent in agents:
                    if other_agent.lower() in content:
                        # Statement by agent i references other_agent
                        edges.append((stmt["agent"], other_agent))
            
            sorted_agents = topological_sort(edges) if edges else agents
            
            computed_answer = sorted_agents[0] if sorted_agents else "Unknown"
            confidence = 0.3
        else:
            # Extract answer from solution
            truthful_agents = []
            for agent in agents:
                agent_var = f"A_{agent}"
                if agent_var in solution and solution[agent_var]:
                    truthful_agents.append(agent)
                elif agent in truth_policies and truth_policies[agent] == "truthful":
                    truthful_agents.append(agent)
            
            computed_answer = truthful_agents[0] if truthful_agents else "No truthful agents"
            confidence = 0.7
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "truthful_agents": truthful_agents if 'truthful_agents' in locals() else [],
            "reasoning": "Constraint solving fallback"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        scored = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * confidence
            
            scored.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": confidence
            })
        
        return scored

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score > min_score:
            for item in scored:
                item["score"] = (item["score"] - min_score) / (max_score - min_score)
        else:
            # All scores equal
            for item in scored:
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