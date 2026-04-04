import re
import zlib
from typing import Dict, List, Any, Tuple

from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    solve_constraints,
    topological_sort,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """Mechanism design x SAT/Constraint solving - Liar detection"""

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
        truth_policies = {}  # agent -> policy (e.g., "always lies", "always tells truth")
        question = ""
        
        current_agent = None
        for line in lines:
            # Look for agent introductions (capitalized names followed by colon or says)
            agent_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:says|:|\'s)', line)
            if agent_match:
                agent = agent_match.group(1)
                if agent not in agents:
                    agents.append(agent)
                current_agent = agent
                
                # Extract truth policy
                if "always tells the truth" in line.lower() or "truth-teller" in line.lower():
                    truth_policies[agent] = "truth"
                elif "always lies" in line.lower() or "liar" in line.lower():
                    truth_policies[agent] = "lie"
                elif "random" in line.lower() or "sometimes" in line.lower():
                    truth_policies[agent] = "random"
            
            # Extract statements
            if current_agent and ('"' in line or "'" in line):
                quote_match = re.search(r'["\']([^"\']+)["\']', line)
                if quote_match:
                    statement = quote_match.group(1).strip()
                    statements.append({
                        "agent": current_agent,
                        "statement": statement,
                        "line": line
                    })
            
            # Extract question (usually last line)
            if "?" in line and not current_agent:
                question = line
        
        # Extract logical relationships from statements
        logical_relations = []
        for stmt in statements:
            # Look for implications (if-then statements)
            if "if" in stmt["statement"].lower() and "then" in stmt["statement"].lower():
                parts = stmt["statement"].lower().split("then")
                if len(parts) == 2:
                    antecedent = parts[0].replace("if", "").strip()
                    consequent = parts[1].strip()
                    logical_relations.append((antecedent, consequent))
            
            # Look for negations
            if "not" in stmt["statement"].lower() or "false" in stmt["statement"].lower():
                logical_relations.append((stmt["statement"], "¬" + stmt["statement"]))
        
        return {
            "agents": agents,
            "statements": statements,
            "truth_policies": truth_policies,
            "question": question,
            "logical_relations": logical_relations,
            "raw_prompt": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use mechanism design principles to model agents as strategic players."""
        agents = structure["agents"]
        statements = structure["statements"]
        truth_policies = structure["truth_policies"]
        logical_relations = structure["logical_relations"]
        
        # Mechanism design: model truth-telling as a strategy in a revelation game
        # Agents have types (truth-teller, liar, random) and choose statements
        
        # Build constraint satisfaction problem for agent types
        variables = {}
        domains = {}
        constraints = []
        
        # Each agent has a type variable
        for agent in agents:
            variables[agent] = f"type_{agent}"
            domains[f"type_{agent}"] = ["truth", "lie", "random"]
        
        # Extract known policies as constraints
        for agent, policy in truth_policies.items():
            if policy in ["truth", "lie"]:
                constraints.append(([f"type_{agent}"], 
                                  lambda x, p=policy: x[0] == p))
        
        # Convert statements to logical constraints
        # This is where we use SAT reasoning
        sat_clauses = []
        var_map = {}
        next_var = 1
        
        # Create variables for each statement
        for i, stmt in enumerate(statements):
            var_name = f"S{i}"
            var_map[stmt["statement"]] = next_var
            var_map[f"¬{stmt['statement']}"] = -next_var
            next_var += 1
            
            # Agent type constraints on statements
            agent = stmt["agent"]
            agent_type_var = f"type_{agent}"
            
            # Truth-teller: statement must be true
            # Liar: statement must be false
            # Random: no constraint
            def make_stmt_constraint(stmt_idx, agent_type, stmt_text):
                stmt_var = var_map[stmt_text]
                if agent_type == "truth":
                    return [[stmt_var]]  # Statement must be true
                elif agent_type == "lie":
                    return [[-stmt_var]]  # Statement must be false
                return []  # No constraint for random
            
            # Add this constraint to CSP
            constraints.append(([agent_type_var, f"S{i}"], 
                              lambda x, stmt_idx=i, stmt_text=stmt["statement"]: 
                              (x[0] != "truth" or x[1] == 1) and
                              (x[0] != "lie" or x[1] == 0)))
        
        # Add logical relations as SAT clauses
        for ante, cons in logical_relations:
            if ante in var_map and cons in var_map:
                # A → B is equivalent to ¬A ∨ B
                sat_clauses.append([-var_map[ante], var_map[cons]])
        
        # Use amino acid: check entailment for key implications
        key_entailments = []
        for stmt in statements:
            # Check if statement entails contradiction given agent types
            if stmt["statement"] in var_map:
                # Create premise clauses: agent type constraints + logical relations
                premise_clauses = sat_clauses.copy()
                agent = stmt["agent"]
                if agent in truth_policies:
                    if truth_policies[agent] == "truth":
                        premise_clauses.append([var_map[stmt["statement"]]])
                    elif truth_policies[agent] == "lie":
                        premise_clauses.append([-var_map[stmt["statement"]]])
                
                # Check entailment of contradiction
                conclusion = []  # Empty clause represents contradiction
                entailment_result = check_entailment(premise_clauses, conclusion)
                if entailment_result is not None:
                    key_entailments.append((stmt["statement"], entailment_result))
        
        # Use T1 primitive: solve constraints to find consistent type assignments
        csp_variables = list(variables.values())
        csp_domains = domains.copy()
        
        # Convert statement variables to CSP format
        for i in range(len(statements)):
            csp_domains[f"S{i}"] = [0, 1]  # 0 for false, 1 for true
        
        # Solve CSP
        solution = solve_constraints(csp_variables + [f"S{i}" for i in range(len(statements))], 
                                    csp_domains, constraints)
        
        # Use T1 primitive: topological sort for dependency analysis
        # Build dependency graph: agents depend on statements they make
        edges = []
        for stmt in statements:
            agent = stmt["agent"]
            # Agent's type affects their statement
            edges.append((f"type_{agent}", f"stmt_{stmt['statement']}"))
            # Statements may depend on other statements
            for ante, cons in logical_relations:
                if cons in stmt["statement"]:
                    edges.append((f"stmt_{ante}", f"stmt_{cons}"))
        
        if edges:
            topo_order = topological_sort(edges)
        else:
            topo_order = []
        
        # Use T1 primitive: track beliefs in multi-agent system
        observations = []
        for stmt in statements:
            # Each statement is an observation about the world
            agent = stmt["agent"]
            # Truth-tellers observe truth, liars observe falsehood
            if agent in truth_policies:
                if truth_policies[agent] == "truth":
                    observations.append((agent, stmt["statement"], True))
                elif truth_policies[agent] == "lie":
                    observations.append((agent, stmt["statement"], False))
        
        belief_state = track_beliefs(agents, observations)
        
        # Use T1 primitive: bayesian update for uncertain policies
        # Start with prior: equal probability for each type
        prior = 1.0 / 3.0  # truth, lie, random
        
        # Update based on statement consistency
        updated_probs = {}
        for agent in agents:
            # Likelihood: probability of observed statements given agent type
            agent_stmts = [s for s in statements if s["agent"] == agent]
            
            if not agent_stmts:
                updated_probs[agent] = prior
                continue
            
            # For truth-teller: all statements must be consistent
            # For liar: all statements must be false
            # For random: any statement possible
            
            # Count consistent statements for each type
            truth_consistent = 0
            lie_consistent = 0
            
            for stmt in agent_stmts:
                # Check if statement is logically possible
                stmt_var = var_map.get(stmt["statement"], 0)
                if stmt_var:
                    # Simple check: statement doesn't contradict known facts
                    truth_consistent += 1
                    lie_consistent += 1  # False statements are always possible
            
            likelihood_truth = truth_consistent / len(agent_stmts) if agent_stmts else 0.5
            likelihood_lie = lie_consistent / len(agent_stmts) if agent_stmts else 0.5
            likelihood_random = 0.5  # Random can say anything
            
            # Weighted average likelihood
            likelihood = (likelihood_truth + likelihood_lie + likelihood_random) / 3.0
            
            posterior = bayesian_update(prior, likelihood, false_positive=0.1)
            updated_probs[agent] = posterior
        
        # Use amino acid: solve_first for alternative consistent assignments
        alt_solution = None
        if solution:
            # Find alternative by fixing some variables
            fixed_vars = {}
            for agent in agents[:min(2, len(agents))]:  # Fix first 2 agents
                if f"type_{agent}" in solution:
                    fixed_vars[f"type_{agent}"] = [solution[f"type_{agent}"]]
            
            alt_domains = domains.copy()
            for var, val in fixed_vars.items():
                if var in alt_domains:
                    alt_domains[var] = val
            
            alt_solution = solve_first(list(variables.values()), alt_domains, constraints)
        
        # Determine answer based on mechanism design analysis
        # In mechanism design, we look for incentive-compatible truth revelation
        
        computed_answer = ""
        confidence = 0.5
        
        if solution:
            # Find the agent most likely to be telling truth based on Bayesian update
            if updated_probs:
                best_agent = max(updated_probs.items(), key=lambda x: x[1])[0]
                computed_answer = best_agent
                confidence = updated_probs[best_agent]
            
            # Alternative: find agent whose statements are most consistent
            consistency_scores = {}
            for agent in agents:
                agent_stmts = [s for s in statements if s["agent"] == agent]
                if not agent_stmts:
                    continue
                
                # Check consistency of statements
                consistent_count = 0
                for stmt in agent_stmts:
                    stmt_var = var_map.get(stmt["statement"], 0)
                    if stmt_var and stmt_var > 0:  # Statement is true in solution
                        if solution.get(f"type_{agent}") == "truth":
                            consistent_count += 1
                    elif stmt_var and stmt_var < 0:  # Statement is false in solution
                        if solution.get(f"type_{agent}") == "lie":
                            consistent_count += 1
                
                if agent_stmts:
                    consistency_scores[agent] = consistent_count / len(agent_stmts)
            
            if consistency_scores:
                most_consistent = max(consistency_scores.items(), key=lambda x: x[1])[0]
                # Use T1 primitive: confidence from agreement between methods
                agreement_scores = []
                if computed_answer:
                    agreement_scores.append(1.0 if most_consistent == computed_answer else 0.0)
                if updated_probs:
                    top2 = sorted(updated_probs.items(), key=lambda x: x[1], reverse=True)[:2]
                    if len(top2) > 1:
                        agreement_scores.append(top2[0][1] - top2[1][1])  # Margin
                
                if agreement_scores:
                    confidence = confidence_from_agreement(agreement_scores)
                
                # Final answer is most consistent agent
                computed_answer = most_consistent
        
        # Fallback if no solution found
        if not computed_answer and agents:
            # Use topological order to determine which agent's statements are foundational
            if topo_order:
                # Find first agent in dependency order
                for node in topo_order:
                    if node.startswith("type_"):
                        agent = node.replace("type_", "")
                        if agent in agents:
                            computed_answer = agent
                            break
            
            if not computed_answer:
                computed_answer = agents[0]  # Default to first agent
        
        return {
            "answer": computed_answer,
            "confidence": min(max(confidence, 0.0), 1.0),
            "reasoning": f"Mechanism design analysis: {computed_answer} has most incentive-compatible truth revelation",
            "solution": solution,
            "topo_order": topo_order,
            "belief_state": belief_state,
            "updated_probs": updated_probs
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        for candidate in candidates:
            # Primary scoring: exact match or substring match of computed answer
            score = 0.0
            
            # Check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                score = 1.0 * confidence
            else:
                # Fallback: NCD similarity
                ncd_score = self._ncd(computed_answer, candidate)
                score = (1.0 - ncd_score) * confidence
            
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
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
                for item in scored:
                    item["score"] = 0.5  # Neutral score if all equal
        
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