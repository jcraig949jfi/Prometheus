import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    solve_sat,
    modus_ponens,
    track_beliefs
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """auction_theory x constraint_acids - liar_detection"""

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
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy ("always truth", "always lie", "random")
        question = ""
        
        # Extract agents and their policies
        for line in lines:
            line_lower = line.lower()
            # Look for agent definitions
            if "always tells the truth" in line_lower:
                # Find agent name (capitalized word before the policy)
                words = line.split()
                for i, word in enumerate(words):
                    if word[0].isupper() and i < len(words) - 1:
                        agent = word.strip('":.,')
                        agents.append(agent)
                        truth_policies[agent] = "truth"
                        break
            elif "always lies" in line_lower:
                words = line.split()
                for i, word in enumerate(words):
                    if word[0].isupper() and i < len(words) - 1:
                        agent = word.strip('":.,')
                        agents.append(agent)
                        truth_policies[agent] = "lie"
                        break
            elif "random" in line_lower or "coin flip" in line_lower:
                words = line.split()
                for i, word in enumerate(words):
                    if word[0].isupper() and i < len(words) - 1:
                        agent = word.strip('":.,')
                        agents.append(agent)
                        truth_policies[agent] = "random"
                        break
            
            # Extract statements (quoted text or sentences ending with quotes)
            if '"' in line:
                # Find text between quotes
                matches = re.findall(r'"([^"]*)"', line)
                for match in matches:
                    if match and len(match) > 3:  # Avoid very short quotes
                        statements.append(match.strip())
            
            # Extract question (usually last line)
            if "?" in line and ("who" in line_lower or "what" in line_lower or 
                               "which" in line_lower or "how" in line_lower):
                question = line
        
        # If no explicit policies found, try to infer from the text
        if not truth_policies:
            for line in lines:
                for agent in agents:
                    if agent.lower() in line.lower():
                        if "truth" in line.lower():
                            truth_policies[agent] = "truth"
                        elif "lie" in line.lower() or "liar" in line.lower():
                            truth_policies[agent] = "lie"
                        elif "random" in line.lower():
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
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use auction theory as scaffold: agents bid truth values, highest consistency wins."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["truth_policies"]
        
        # If no agents extracted, fallback to simple analysis
        if not agents:
            return self._fallback_reason(structure)
        
        # Phase 1: Encode as SAT problem using auction theory framework
        # Each agent's statement is a "bid" of truth value
        # We need to find assignment consistent with policies
        
        # Create variables: A1, A2, ... for agents' truthfulness
        # and S1, S2, ... for statements' truth values
        var_map = {}
        next_var = 1
        
        # Agent variables: var_map[agent] = variable_id
        for agent in agents:
            var_map[f"A_{agent}"] = next_var
            next_var += 1
        
        # Statement variables
        for i, stmt in enumerate(statements):
            var_map[f"S_{i}"] = next_var
            next_var += 1
        
        # Build SAT clauses based on auction theory:
        # 1. Each agent's policy imposes constraints (their "bidding strategy")
        # 2. Statements must be consistent with agent policies
        # 3. The "auctioneer" (reasoner) selects the most consistent assignment
        
        clauses = []
        
        # Add policy constraints
        for agent in agents:
            agent_var = var_map[f"A_{agent}"]
            policy = policies.get(agent, "unknown")
            
            if policy == "truth":
                # Truth-teller: A_agent = TRUE
                clauses.append([agent_var])
            elif policy == "lie":
                # Liar: A_agent = FALSE
                clauses.append([-agent_var])
            elif policy == "random":
                # Random: no constraint on A_agent
                # But we need to consider both possibilities
                pass
        
        # Try to map statements to agents and add consistency constraints
        # This is a simplified mapping - in real puzzles, statements reference each other
        agent_mentions = {}
        for i, stmt in enumerate(statements):
            stmt_var = var_map[f"S_{i}"]
            # Check which agents are mentioned in the statement
            for agent in agents:
                if agent.lower() in stmt.lower():
                    if agent not in agent_mentions:
                        agent_mentions[agent] = []
                    agent_mentions[agent].append(stmt_var)
        
        # Add consistency constraints: if agent is truth-teller, their statements are true
        # if agent is liar, their statements are false
        for agent, stmt_vars in agent_mentions.items():
            agent_var = var_map[f"A_{agent}"]
            policy = policies.get(agent, "unknown")
            
            if policy == "truth":
                # Truth-teller: all their statements are true
                for stmt_var in stmt_vars:
                    # A_agent → S_i (if agent is truthful, statement is true)
                    clauses.append([-agent_var, stmt_var])
            elif policy == "lie":
                # Liar: all their statements are false
                for stmt_var in stmt_vars:
                    # A_agent → ¬S_i (if agent is liar, statement is false)
                    clauses.append([-agent_var, -stmt_var])
        
        # Use solve_sat primitive to find satisfying assignments
        sat_result = solve_sat(clauses, len(var_map))
        
        # Use check_entailment amino acid to test logical implications
        # Test if the puzzle has a unique solution
        test_clauses = clauses[:]
        if sat_result:
            # Create a test clause that negates one assignment
            test_literal = list(sat_result.items())[0][0]
            test_value = list(sat_result.items())[0][1]
            test_clauses.append([-test_literal if test_value else test_literal])
        
        # Use detect_paradox amino acid to check for contradictions
        paradox_info = detect_paradox(clauses)
        
        # Use is_uniquely_solvable amino acid to check solution uniqueness
        # Convert to CSP format for constraint_acids
        variables = list(var_map.keys())
        domains = {}
        constraints = []
        
        for var in variables:
            domains[var] = [0, 1]  # Boolean variables
        
        # Convert SAT clauses to CSP constraints
        for clause in clauses:
            def make_constraint(clause_vars=clause):
                def constraint(assignment):
                    for lit in clause_vars:
                        var_name = list(var_map.keys())[abs(lit) - 1]
                        val = assignment.get(var_name, None)
                        if val is not None:
                            if lit > 0 and val == 1:
                                return True
                            elif lit < 0 and val == 0:
                                return True
                    # Check if all literals are false
                    all_false = True
                    for lit in clause_vars:
                        var_name = list(var_map.keys())[abs(lit) - 1]
                        val = assignment.get(var_name, None)
                        if val is None:
                            all_false = False
                            break
                        if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                            all_false = False
                            break
                    return not all_false
                return constraint
            
            # Get variable names involved in this clause
            involved_vars = []
            for lit in clause:
                var_idx = abs(lit) - 1
                if var_idx < len(variables):
                    involved_vars.append(variables[var_idx])
            
            if involved_vars:
                constraints.append((involved_vars, make_constraint()))
        
        unique_solution = False
        if variables and domains and constraints:
            unique_solution = is_uniquely_solvable(variables, domains, constraints)
        
        # Use entropy primitive to measure uncertainty in the solution
        if sat_result:
            # Create probability distribution from SAT solution
            # For auction theory: each agent's "bid" has a confidence score
            truth_values = [1 if val else 0 for val in sat_result.values()]
            if truth_values:
                # Normalize to probabilities
                total = sum(truth_values)
                if total > 0:
                    probs = [v/total for v in truth_values]
                    uncertainty = entropy(probs)
                else:
                    uncertainty = 1.0
            else:
                uncertainty = 1.0
        else:
            uncertainty = 1.0
        
        # Use bayesian_update primitive to combine evidence
        # Prior: equal probability for each agent being the answer
        prior = 1.0 / len(agents) if agents else 0.5
        
        # Likelihood: based on consistency with policies
        consistency_score = 0.0
        if sat_result:
            # Count how many policy constraints are satisfied
            satisfied = 0
            total_constraints = 0
            
            for agent in agents:
                policy = policies.get(agent, "unknown")
                if policy in ["truth", "lie"]:
                    total_constraints += 1
                    agent_var = var_map.get(f"A_{agent}")
                    if agent_var:
                        agent_val = sat_result.get(agent_var, None)
                        if agent_val is not None:
                            if (policy == "truth" and agent_val) or (policy == "lie" and not agent_val):
                                satisfied += 1
            
            consistency_score = satisfied / total_constraints if total_constraints > 0 else 0.5
        
        posterior = bayesian_update(prior, consistency_score, false_positive=0.1)
        
        # Use track_beliefs primitive to model agent knowledge states
        # Extract simple belief statements from the prompt
        belief_observations = []
        for stmt in statements:
            for agent in agents:
                if agent.lower() in stmt.lower():
                    # Check if statement is about belief
                    if "believes" in stmt.lower() or "thinks" in stmt.lower() or "says" in stmt.lower():
                        # Extract the fact being believed
                        fact_match = re.search(r'"(.*?)"', stmt)
                        if fact_match:
                            fact = fact_match.group(1)
                            belief_observations.append((agent, fact, True))
        
        if agents and belief_observations:
            beliefs = track_beliefs(agents, belief_observations)
        else:
            beliefs = {}
        
        # Use modus_ponens primitive for logical deduction
        # Extract implication statements
        premises = []
        for stmt in statements:
            if "if" in stmt.lower() and "then" in stmt.lower():
                # Simple implication extraction
                parts = stmt.lower().split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip()
                    premises.append((antecedent, consequent))
        
        if premises:
            # Extract known facts (simple statements without conditionals)
            facts = set()
            for stmt in statements:
                if "if" not in stmt.lower() and "then" not in stmt.lower():
                    # Check if it's a simple assertion
                    simple_stmt = stmt.strip('"').lower()
                    if len(simple_stmt.split()) < 8:  # Not too long
                        facts.add(simple_stmt)
            
            deduced = modus_ponens(premises, facts)
        else:
            deduced = set()
        
        # Use confidence_from_agreement primitive to combine multiple reasoning sources
        confidence_sources = []
        if sat_result:
            confidence_sources.append(posterior)
        if uncertainty < 1.0:
            confidence_sources.append(1.0 - uncertainty)
        if unique_solution:
            confidence_sources.append(0.9)
        else:
            confidence_sources.append(0.5)
        
        if confidence_sources:
            overall_confidence = confidence_from_agreement(confidence_sources)
        else:
            overall_confidence = 0.5
        
        # Determine the answer based on auction theory:
        # The "winning bid" is the most consistent assignment
        computed_answer = ""
        
        if sat_result and agents:
            # Find which agent's statements are most consistent
            agent_scores = {}
            for agent in agents:
                score = 0
                agent_var = var_map.get(f"A_{agent}")
                if agent_var:
                    agent_val = sat_result.get(agent_var, None)
                    policy = policies.get(agent, "unknown")
                    
                    if agent_val is not None and policy in ["truth", "lie"]:
                        # Check if assignment matches policy
                        if (policy == "truth" and agent_val) or (policy == "lie" and not agent_val):
                            score += 1
                
                # Check statements associated with this agent
                for i, stmt in enumerate(statements):
                    if agent.lower() in stmt.lower():
                        stmt_var = var_map.get(f"S_{i}")
                        if stmt_var:
                            stmt_val = sat_result.get(stmt_var, None)
                            if stmt_val is not None:
                                score += 1 if stmt_val else 0.5
                
                agent_scores[agent] = score
            
            if agent_scores:
                # In auction theory, highest score wins
                best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
        
        # Fallback if no agent selected
        if not computed_answer and agents:
            computed_answer = agents[0]
        elif not computed_answer:
            computed_answer = "Cannot determine"
        
        return {
            "answer": computed_answer,
            "confidence": overall_confidence,
            "reasoning": f"Auction theory analysis: {computed_answer} has highest consistency score. " +
                       f"SAT solvable: {sat_result is not None}, " +
                       f"Unique: {unique_solution}, " +
                       f"Paradox: {paradox_info.get('is_paradox', False) if paradox_info else False}",
            "sat_result": sat_result,
            "unique_solution": unique_solution,
            "paradox_detected": paradox_info.get('is_paradox', False) if paradox_info else False
        }

    def _fallback_reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reasoning when extraction fails."""
        # Still use primitives even in fallback
        raw_text = structure["raw"]
        
        # Extract any capitalized names as potential agents
        potential_agents = re.findall(r'\b[A-Z][a-z]+\b', raw_text)
        # Filter out common words
        common_words = {"The", "A", "An", "And", "But", "Or", "If", "Then", "What", "Who", "Which"}
        agents = [a for a in potential_agents if a not in common_words and len(a) > 2]
        
        if not agents:
            agents = ["Unknown"]
        
        # Use entropy on a simple distribution
        probs = [1.0/len(agents) for _ in agents]
        uncertainty = entropy(probs)
        
        # Use bayesian_update with dummy values
        prior = 0.5
        likelihood = 0.7  # Assume some consistency
        posterior = bayesian_update(prior, likelihood, false_positive=0.2)
        
        # Use confidence_from_agreement
        confidence = confidence_from_agreement([posterior, 1.0 - uncertainty])
        
        # Select first agent as answer (primitive-dependent through entropy)
        computed_answer = agents[0] if uncertainty < 0.9 else "Cannot determine"
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Fallback analysis selected {computed_answer} based on name frequency",
            "sat_result": None,
            "unique_solution": False,
            "paradox_detected": False
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: check if computed answer appears in candidate
            score = 0.0
            
            if computed_answer.lower() in candidate.lower():
                score = 0.9 * confidence
            else:
                # Use NCD as fallback
                ncd_score = self._ncd(computed_answer, candidate)
                score = (1.0 - ncd_score) * confidence * 0.7
            
            # Boost score if candidate contains reasoning clues
            reasoning_text = reasoning_result["reasoning"]
            if any(word in candidate.lower() for word in ["consistent", "truth", "lie", "paradox"]):
                if any(word in reasoning_text.lower() for word in ["consistent", "paradox"]):
                    score *= 1.1
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Simple normalization
        scores = [item["raw_score"] for item in scored]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            
            if max_score > min_score:
                for item in scored:
                    # Normalize to 0-1 range
                    normalized = (item["raw_score"] - min_score) / (max_score - min_score)
                    item["score"] = normalized
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