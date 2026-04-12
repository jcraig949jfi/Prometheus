import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    solve_sat,
    modus_ponens,
    check_transitivity,
    entropy,
    confidence_from_agreement,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Number theory x SAT solving - liar_detection"""

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
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> "always_truth", "always_lie", or "random"
        question = ""
        
        # Extract agents and their policies
        for line in lines:
            line_lower = line.lower()
            # Look for agent definitions
            if "always tells the truth" in line_lower:
                name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                if name_match:
                    agent = name_match.group(1)
                    agents.append(agent)
                    truth_policies[agent] = "always_truth"
            elif "always lies" in line_lower:
                name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                if name_match:
                    agent = name_match.group(1)
                    agents.append(agent)
                    truth_policies[agent] = "always_lie"
            elif "random" in line_lower or "coin flip" in line_lower:
                name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                if name_match:
                    agent = name_match.group(1)
                    agents.append(agent)
                    truth_policies[agent] = "random"
            
            # Extract statements (quoted or following "says")
            if 'says' in line_lower or 'said' in line_lower:
                # Find the agent
                agent_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                if agent_match:
                    agent = agent_match.group(1)
                    # Extract the statement content
                    if '"' in line:
                        statement_match = re.search(r'"([^"]+)"', line)
                    elif "'" in line:
                        statement_match = re.search(r"'([^']+)'", line)
                    else:
                        # Try to extract after "says" or "said"
                        says_idx = line_lower.find('says')
                        if says_idx == -1:
                            says_idx = line_lower.find('said')
                        if says_idx != -1:
                            statement_text = line[says_idx + 4:].strip()
                            statement_match = type('obj', (object,), {'group': lambda x: statement_text})()
                    
                    if statement_match:
                        statement = statement_match.group(1).strip()
                        statements.append((agent, statement))
            
            # Extract question (usually last line)
            if line.endswith('?') and not any(word in line_lower for word in ['says', 'said', 'tells', 'lies']):
                question = line
        
        # If no explicit policies found, infer from statements
        if not truth_policies:
            for agent in agents:
                # Check if agent makes statements about truth-telling
                for stmt_agent, stmt in statements:
                    if stmt_agent == agent:
                        if "always tells the truth" in stmt.lower():
                            truth_policies[agent] = "always_truth"
                        elif "always lies" in stmt.lower():
                            truth_policies[agent] = "always_lie"
                        elif "random" in stmt.lower():
                            truth_policies[agent] = "random"
        
        # Ensure all agents have a policy
        for agent in agents:
            if agent not in truth_policies:
                truth_policies[agent] = "unknown"
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use number-theoretic SAT encoding to resolve liar puzzles."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        
        # Phase 1: Encode as SAT using number theory concepts
        # Each agent gets a truth value variable (True if actually truthful)
        # Each statement gets a propositional variable for its truth content
        
        # Map agents to SAT variables
        agent_vars = {agent: i+1 for i, agent in enumerate(agents)}
        n_agents = len(agents)
        
        clauses = []
        
        # Encode truth-telling policies as constraints
        for agent, policy in truth_policies.items():
            var = agent_vars[agent]
            if policy == "always_truth":
                # Agent's variable must be True
                clauses.append([var])
            elif policy == "always_lie":
                # Agent's variable must be False
                clauses.append([-var])
            elif policy == "random":
                # No constraint - variable can be True or False
                pass
        
        # Encode statements
        statement_clauses = []
        for speaker, statement in statements:
            speaker_var = agent_vars[speaker]
            
            # Parse statement for content
            # Check if statement is about another agent's truthfulness
            for other_agent in agents:
                if other_agent in statement and other_agent != speaker:
                    other_var = agent_vars[other_agent]
                    
                    if "tells the truth" in statement.lower() or "is truthful" in statement.lower():
                        # Speaker says: other_agent is truthful
                        # If speaker is truthful (speaker_var True), then other_var must be True
                        # If speaker is liar (speaker_var False), then other_var must be False
                        # Encoding: (speaker_var → other_var) ∧ (¬speaker_var → ¬other_var)
                        # Which simplifies to: speaker_var ≡ other_var
                        statement_clauses.append([speaker_var, -other_var])
                        statement_clauses.append([-speaker_var, other_var])
                    
                    elif "lies" in statement.lower() or "is a liar" in statement.lower():
                        # Speaker says: other_agent is liar
                        # If speaker is truthful, then other_var must be False
                        # If speaker is liar, then other_var must be True
                        # Encoding: speaker_var ≡ ¬other_var
                        statement_clauses.append([speaker_var, other_var])
                        statement_clauses.append([-speaker_var, -other_var])
            
            # Check if statement is self-referential
            if "I " in statement and ("tells the truth" in statement.lower() or "lies" in statement.lower()):
                # Self-reference: "I tell the truth" or "I lie"
                if "tells the truth" in statement.lower():
                    # Speaker says: I tell the truth
                    # This creates a paradox unless consistent
                    # Encoding: speaker_var ≡ speaker_var (tautology, adds no constraint)
                    pass
                elif "lies" in statement.lower():
                    # Speaker says: I lie
                    # This is the liar paradox: speaker_var ≡ ¬speaker_var
                    # Which is unsatisfiable
                    statement_clauses.append([speaker_var, speaker_var])  # Always True
                    statement_clauses.append([-speaker_var, -speaker_var])  # Always True
        
        # Add statement clauses to main clauses
        clauses.extend(statement_clauses)
        
        # Use T1 primitive: solve_sat to find satisfying assignment
        sat_result = solve_sat(clauses, n_agents)
        
        # Use amino acid: check_entailment to see if question is entailed
        # First, encode the question if it asks about a specific agent
        question = structure["question"]
        question_agent = None
        for agent in agents:
            if agent in question:
                question_agent = agent
                break
        
        entailment_result = None
        if question_agent and sat_result:
            # Create clause for the question
            # If question asks "Who is telling the truth?", we check each agent
            question_var = agent_vars[question_agent]
            question_clause = [question_var]  # Assume question asks if this agent is truthful
            
            # Check if the model entails this agent being truthful
            entailment_result = check_entailment(clauses, question_clause)
        
        # Use amino acid: detect_paradox to check for contradictions
        paradox_result = detect_paradox(clauses)
        
        # Use T1 primitive: modus_ponens to derive conclusions
        # Create implication rules from statements
        premises = []
        facts = set()
        
        if sat_result:
            # Add facts based on SAT solution
            for agent, var in agent_vars.items():
                if sat_result.get(var, False):
                    facts.add(f"{agent}_truthful")
                else:
                    facts.add(f"{agent}_liar")
        
        # Add implication rules from statements
        for speaker, statement in statements:
            for other_agent in agents:
                if other_agent in statement and other_agent != speaker:
                    if "tells the truth" in statement.lower():
                        # speaker_truthful → other_truthful
                        premises.append((f"{speaker}_truthful", f"{other_agent}_truthful"))
                    elif "lies" in statement.lower():
                        # speaker_truthful → other_liar
                        premises.append((f"{speaker}_truthful", f"{other_agent}_liar"))
        
        # Apply modus_ponens
        derived_facts = modus_ponens(premises, facts)
        
        # Use T1 primitive: check_transitivity on truth relationships
        # Build relations from statements
        relations = []
        for speaker, statement in statements:
            for other_agent in agents:
                if other_agent in statement and other_agent != speaker:
                    if "tells the truth" in statement.lower():
                        relations.append((speaker, other_agent))
        
        transitive_closure = check_transitivity(relations)
        
        # Use T1 primitive: entropy to measure uncertainty
        # Create probability distribution over possible truth assignments
        if sat_result:
            # Count how many agents are truthful in the solution
            truthful_count = sum(1 for var in agent_vars.values() if sat_result.get(var, False))
            p_truthful = truthful_count / n_agents if n_agents > 0 else 0.5
            probs = [p_truthful, 1 - p_truthful]
            uncertainty = entropy(probs)
        else:
            uncertainty = 1.0  # Maximum entropy if no solution
        
        # Use T1 primitive: topological_sort on implication graph
        # Build DAG from implications
        implication_edges = []
        for speaker, statement in statements:
            for other_agent in agents:
                if other_agent in statement and other_agent != speaker:
                    if "tells the truth" in statement.lower():
                        implication_edges.append((speaker, other_agent))
        
        topological_order = topological_sort(implication_edges)
        
        # Use T1 primitive: confidence_from_agreement
        # Create multiple scoring methods and check agreement
        scores = []
        
        # Method 1: SAT-based
        if sat_result:
            sat_score = sum(1 for var in agent_vars.values() if sat_result.get(var, False)) / n_agents
            scores.append(sat_score)
        
        # Method 2: Transitive closure size
        if transitive_closure:
            trans_score = sum(len(reachable) for reachable in transitive_closure.values()) / (n_agents * n_agents)
            scores.append(trans_score)
        
        # Method 3: Derived facts count
        derived_score = len(derived_facts) / (2 * n_agents)  # Each agent has 2 possible states
        scores.append(derived_score)
        
        confidence = confidence_from_agreement(scores) if scores else 0.5
        
        # Determine the answer using amino acid: is_uniquely_solvable
        # Encode as CSP to check uniqueness
        if agents:
            variables = list(agent_vars.keys())
            domains = {agent: [True, False] for agent in variables}
            
            csp_constraints = []
            # Add constraints from policies
            for agent, policy in truth_policies.items():
                if policy == "always_truth":
                    csp_constraints.append(([agent], lambda a: a[0] == True))
                elif policy == "always_lie":
                    csp_constraints.append(([agent], lambda a: a[0] == False))
            
            # Add constraints from statements
            for speaker, statement in statements:
                for other_agent in agents:
                    if other_agent in statement and other_agent != speaker:
                        if "tells the truth" in statement.lower():
                            csp_constraints.append(([speaker, other_agent], 
                                                   lambda vals: vals[0] == vals[1]))
                        elif "lies" in statement.lower():
                            csp_constraints.append(([speaker, other_agent],
                                                   lambda vals: vals[0] != vals[1]))
            
            unique_solution = is_uniquely_solvable(variables, domains, csp_constraints)
        else:
            unique_solution = False
        
        # Compute the final answer
        computed_answer = ""
        
        if paradox_result and paradox_result.get("is_paradox", False):
            computed_answer = "paradox"
        elif not sat_result:
            computed_answer = "contradiction"
        elif question_agent:
            # Answer the specific question
            if sat_result.get(agent_vars[question_agent], False):
                computed_answer = f"{question_agent} tells the truth"
            else:
                computed_answer = f"{question_agent} lies"
        elif topological_order:
            # Use topological order to determine most reliable agent
            computed_answer = topological_order[0] if topological_order else agents[0]
        elif agents:
            # Default: agent with most derived facts about them
            agent_truth_counts = {}
            for fact in derived_facts:
                for agent in agents:
                    if agent in fact:
                        agent_truth_counts[agent] = agent_truth_counts.get(agent, 0) + 1
            
            if agent_truth_counts:
                best_agent = max(agent_truth_counts.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
            else:
                computed_answer = agents[0]
        else:
            computed_answer = "unknown"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "sat_solution": sat_result,
            "paradox_detected": paradox_result.get("is_paradox", False) if paradox_result else False,
            "entailment": entailment_result,
            "unique_solution": unique_solution,
            "topological_order": topological_order,
            "derived_facts": list(derived_facts),
            "reasoning": f"SAT solution: {sat_result}, Paradox: {paradox_result}, Entailment: {entailment_result}, Unique: {unique_solution}"
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or containment
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif candidate.lower() in computed_answer.lower():
                base_score = 0.8
            else:
                # Use NCD as fallback
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
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if len(scores) > 1:
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
        
        if max(ca, cb) == 0:
            return 1.0
        
        return (cab - min(ca, cb)) / max(ca, cb)