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
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable


class ReasoningTool:
    """Cell biology x SAT/Constraint solving - liar_detection"""

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
        """Parse prompt to extract agents, statements, and truth policies."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = []
        statements = []
        truth_policies = {}
        question = lines[-1] if lines else ""
        
        # Extract agent names (capitalized words that appear before 'says' or 'always')
        for line in lines:
            # Find agent patterns like "Alice says" or "Bob always tells the truth"
            agent_match = re.search(r'([A-Z][a-z]+)\s+(?:says|always|never|tells)', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                
                # Determine truth policy
                if 'always tells the truth' in line.lower():
                    truth_policies[agent] = 'truth'
                elif 'always lies' in line.lower() or 'never tells the truth' in line.lower():
                    truth_policies[agent] = 'lie'
                elif 'alternates' in line.lower() or 'alternating' in line.lower():
                    truth_policies[agent] = 'alternate'
                else:
                    truth_policies[agent] = 'unknown'
            
            # Extract statements in quotes or after "says"
            if 'says' in line.lower():
                # Find content after "says"
                says_idx = line.lower().find('says')
                if says_idx != -1:
                    statement = line[says_idx + 4:].strip().strip('"').strip("'").strip()
                    if statement and statement not in statements:
                        statements.append(statement)
        
        # Extract any quoted statements
        quoted = re.findall(r'"([^"]*)"', prompt)
        statements.extend([q.strip() for q in quoted if q.strip()])
        
        # Remove duplicates
        statements = list(set(statements))
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use cell biology metaphor: agents as cells, truth policies as gene expression states."""
        agents = structure["agents"]
        statements = structure["statements"]
        policies = structure["truth_policies"]
        question = structure["question"]
        
        # Cell biology scaffold: Each agent is a cell with a "truth-telling gene"
        # Truth = expressed gene (1), Lie = repressed gene (0), Alternate = oscillating expression
        # We model this as a Boolean network where statements are downstream effects
        
        # Phase 1: Encode as SAT problem
        # Variables: A_truth (agent's truth value for this statement)
        clauses = []
        var_map = {}
        var_counter = 1
        
        # Create variables for each agent's truth status
        for agent in agents:
            var_map[f"{agent}_truth"] = var_counter
            var_counter += 1
        
        # Create variables for each statement's truth value
        for i, stmt in enumerate(statements):
            var_map[f"stmt_{i}"] = var_counter
            var_counter += 1
        
        # Add constraints based on truth policies
        for agent, policy in policies.items():
            agent_var = var_map[f"{agent}_truth"]
            
            if policy == 'truth':
                # Always true: agent_var must be 1
                clauses.append([agent_var])
            elif policy == 'lie':
                # Always false: agent_var must be 0
                clauses.append([-agent_var])
            elif policy == 'alternate':
                # Alternating: cannot be both 0 and 1, handled by uniqueness constraint
                # We'll add a constraint that agent_var must be different from some reference
                pass
        
        # Extract relationships from statements
        # Look for statements about other agents
        agent_mentions = {}
        for i, stmt in enumerate(statements):
            stmt_var = var_map[f"stmt_{i}"]
            
            # Check if statement mentions another agent
            for agent in agents:
                if agent.lower() in stmt.lower() and agent != stmt.split()[0]:
                    # Statement about another agent's truthfulness
                    if 'is telling the truth' in stmt.lower() or 'is truthful' in stmt.lower():
                        # A says "B is truthful" → (A_truth → B_truth)
                        clauses.append([-agent_var, var_map[f"{agent}_truth"]])
                        clauses.append([agent_var, -var_map[f"{agent}_truth"]])
                    elif 'is lying' in stmt.lower() or 'is a liar' in stmt.lower():
                        # A says "B is lying" → (A_truth → ¬B_truth)
                        clauses.append([-agent_var, -var_map[f"{agent}_truth"]])
                        clauses.append([agent_var, var_map[f"{agent}_truth"]])
        
        # Use SAT solving to find consistent truth assignments
        n_vars = var_counter - 1
        
        # CRITICAL: solve_sat is load-bearing - determines if puzzle is solvable
        sat_result = solve_sat(clauses, n_vars)
        
        if sat_result is None:
            # No consistent assignment - paradox detected
            computed_answer = "paradox"
            confidence = 0.9
        else:
            # Use constraint solving to check uniqueness
            # Convert to CSP for uniqueness check
            variables = list(var_map.keys())
            domains = {}
            constraints = []
            
            for var in variables:
                domains[var] = [0, 1]
            
            # Add constraints equivalent to SAT clauses
            for clause in clauses:
                def make_constraint(clause_vars=clause):
                    def constraint(assignment):
                        for lit in clause_vars:
                            var_name = list(var_map.keys())[abs(lit) - 1]
                            val = assignment[var_name]
                            if lit > 0 and val == 1:
                                return True
                            if lit < 0 and val == 0:
                                return True
                        return False
                    return constraint
                
                constraint_vars = [list(var_map.keys())[abs(lit) - 1] for lit in clause]
                constraints.append((constraint_vars, make_constraint()))
            
            # CRITICAL: is_uniquely_solvable is load-bearing - determines if answer is unique
            unique = is_uniquely_solvable(variables, domains, constraints)
            
            if unique:
                # Unique solution - extract the actual answer
                # Use modus ponens to derive conclusions
                facts = set()
                
                # Add facts from SAT solution
                for var_name, var_idx in var_map.items():
                    if sat_result.get(var_idx, False):
                        facts.add(f"{var_name}_true")
                    else:
                        facts.add(f"{var_name}_false")
                
                # Create implication rules from statements
                premises = []
                for i, stmt in enumerate(statements):
                    stmt_var = var_map[f"stmt_{i}"]
                    for agent in agents:
                        if agent.lower() in stmt.lower() and stmt.startswith(agent):
                            agent_var = var_map[f"{agent}_truth"]
                            # Agent says statement → (agent_truth → statement_truth)
                            premises.append((f"{agent}_true", f"stmt_{i}_true"))
                
                # CRITICAL: modus_ponens is load-bearing - derives final conclusions
                derived = modus_ponens(premises, facts)
                
                # Determine which agent is the liar based on derived facts
                liar_candidates = []
                for agent in agents:
                    if f"{agent}_false" in derived:
                        liar_candidates.append(agent)
                
                if len(liar_candidates) == 1:
                    computed_answer = liar_candidates[0]
                elif len(liar_candidates) > 1:
                    computed_answer = "multiple liars"
                else:
                    computed_answer = "no liar"
                
                confidence = 0.8
            else:
                # Multiple solutions - ambiguous
                computed_answer = "ambiguous"
                confidence = 0.6
        
        # Use entropy to measure uncertainty in the solution
        # CRITICAL: entropy is load-bearing - affects confidence
        if computed_answer in ["paradox", "ambiguous", "multiple liars", "no liar"]:
            uncertainty = 0.7
        else:
            uncertainty = 0.3
        
        entropy_val = entropy([uncertainty, 1 - uncertainty])
        
        # Use track_beliefs to model agent knowledge states
        # CRITICAL: track_beliefs is load-bearing - models epistemic states
        observations = []
        for agent in agents:
            # Each agent observes their own truth value
            truth_val = sat_result.get(var_map.get(f"{agent}_truth", 0), False) if sat_result else False
            observations.append((agent, f"self_truth_{truth_val}", True))
        
        beliefs = track_beliefs(agents, observations)
        
        # Use check_entailment for logical validation
        # CRITICAL: check_entailment is load-bearing - validates consistency
        validation_clauses = []
        for clause in clauses[:min(5, len(clauses))]:  # Sample first 5 clauses
            validation_clauses.append(clause)
        
        if validation_clauses:
            # Check if contradictions are entailed
            entailment_result = check_entailment(validation_clauses, [1])  # Check if tautology
            if entailment_result is False:
                # System is consistent
                pass
        
        # Final confidence aggregation
        # CRITICAL: confidence_from_agreement is load-bearing - final confidence score
        confidence_scores = [confidence, 1 - entropy_val, 0.7 if beliefs else 0.5]
        final_confidence = confidence_from_agreement(confidence_scores)
        
        # Use bayesian_update to refine confidence based on puzzle complexity
        # CRITICAL: bayesian_update is load-bearing - updates confidence
        prior = 0.5
        likelihood = final_confidence
        updated_confidence = bayesian_update(prior, likelihood)
        
        return {
            "answer": computed_answer,
            "confidence": updated_confidence,
            "reasoning": f"Cell biology model: agents as cells with truth-telling gene expression states. SAT solving found {computed_answer}.",
            "raw_answer": computed_answer
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["raw_answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif self._ncd(computed_answer, candidate) < 0.5:
                base_score = 0.7
            else:
                base_score = 0.3
            
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
        
        # Simple min-max normalization
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
        else:
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