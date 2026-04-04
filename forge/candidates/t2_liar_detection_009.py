import re
import zlib
from typing import Dict, List, Any, Tuple, Set
from forge_primitives import (
    modus_ponens,
    track_beliefs,
    confidence_from_agreement,
    solve_sat,
    topological_sort
)
from forge.amino_acids.pysat_acids import detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """fluid_dynamics x pysat_acids - liar_detection"""

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
        """Extract agents, statements, and truth policies from prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []
        truth_policies = {}
        question = lines[-1] if lines else ""

        # Fluid dynamics inspired: treat agents as particles with truth-telling "vorticity"
        # Vorticity = 1 for always truthful, -1 for always lying, 0 for unknown/random
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        policy_keywords = {
            'always tells the truth': 1,
            'always lies': -1,
            'never tells the truth': -1,
            'never lies': 1,
            'random': 0
        }

        for line in lines:
            # Find agent names (capitalized phrases)
            found_agents = re.findall(agent_pattern, line)
            for agent in found_agents:
                if agent.lower() not in ['who', 'what', 'where', 'when', 'why', 'how']:
                    agents.add(agent)

            # Detect truth policies
            lower_line = line.lower()
            for keyword, vorticity in policy_keywords.items():
                if keyword in lower_line:
                    # Find the agent this policy applies to
                    for agent in found_agents:
                        if agent in line:
                            truth_policies[agent] = vorticity
                            break

            # Extract declarative statements (containing "says" or "claims")
            if ' says ' in line or ' claims ' in line:
                parts = re.split(r' says | claims ', line, maxsplit=1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    content = parts[1].strip().rstrip('.,')
                    if speaker in agents:
                        statements.append({
                            'speaker': speaker,
                            'content': content,
                            'raw': line
                        })

        # Fluid conservation: total vorticity in closed system should be conserved
        # We'll use this as a consistency check later
        total_vorticity = sum(truth_policies.get(agent, 0) for agent in agents)

        return {
            'agents': list(agents),
            'statements': statements,
            'truth_policies': truth_policies,
            'question': question,
            'total_vorticity': total_vorticity,
            'raw_prompt': prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fluid dynamics principles to resolve truth-telling puzzles."""
        agents = structure['agents']
        statements = structure['statements']
        truth_policies = structure['truth_policies']
        question = structure['question']

        # Fluid dynamics scaffold: treat truth as a conserved quantity flowing through
        # a network of agents. Truth-tellers (vorticity +1) act as sources,
        # liars (vorticity -1) as sinks, unknowns create turbulence.
        # The system reaches equilibrium when all statements are consistent.

        # Step 1: Build logical constraints from statements
        # Each statement becomes a propositional variable
        prop_vars = {}
        clauses = []
        var_counter = 1

        for idx, stmt in enumerate(statements):
            speaker = stmt['speaker']
            content = stmt['content']
            var_name = f"S{idx}"
            prop_vars[var_name] = {
                'speaker': speaker,
                'content': content,
                'truth_value': None
            }

            # Fluid pressure: truth value depends on speaker's vorticity
            vorticity = truth_policies.get(speaker, 0)

            # If vorticity is known, add constraint
            if vorticity == 1:  # Always truthful
                # Statement must be true
                clauses.append([var_counter])  # S_idx = TRUE
            elif vorticity == -1:  # Always lying
                # Statement must be false
                clauses.append([-var_counter])  # S_idx = FALSE

            var_counter += 1

        # Step 2: Add inter-statement logical relationships
        # Parse statement content for logical connections
        for var_name, info in prop_vars.items():
            content = info['content'].lower()
            speaker = info['speaker']

            # Check for negations
            if ' not ' in content or " doesn't " in content or " don't " in content:
                # This creates a negative relationship with other statements
                pass  # Handled in next step

            # Check for implications
            if ' if ' in content or ' then ' in content or ' implies ' in content:
                # Extract antecedent and consequent
                # Simplified parsing for common patterns
                if ' then ' in content:
                    parts = content.split(' then ')
                    if len(parts) == 2:
                        # Find which statement corresponds to antecedent
                        for other_var, other_info in prop_vars.items():
                            if other_info['speaker'] != speaker:
                                other_content = other_info['content'].lower()
                                if parts[0] in other_content:
                                    # A -> B becomes (-A ∨ B)
                                    # Map to variable indices
                                    var_idx = int(var_name[1:]) + 1
                                    other_idx = int(other_var[1:]) + 1
                                    clauses.append([-other_idx, var_idx])

        # Step 3: Use T1 primitives for logical reasoning
        # First, use modus_ponens on extracted implications
        premises = []
        facts = set()
        
        for clause in clauses:
            if len(clause) == 1:
                var_idx = clause[0]
                if var_idx > 0:
                    facts.add(f"S{var_idx-1}")
        
        mp_result = modus_ponens(premises, facts)
        if mp_result:
            # Convert back to propositional assignments
            for fact in mp_result:
                if fact.startswith('S'):
                    idx = int(fact[1:])
                    if 0 <= idx < len(statements):
                        prop_vars[f"S{idx}"]['truth_value'] = True

        # Step 4: Use SAT solving to find consistent assignments
        n_vars = len(prop_vars)
        sat_result = solve_sat(clauses, n_vars)
        
        if sat_result:
            # Apply the SAT assignment
            for var_name in prop_vars.keys():
                idx = int(var_name[1:]) + 1
                if idx in sat_result:
                    prop_vars[var_name]['truth_value'] = sat_result[idx]
                elif -idx in sat_result:
                    prop_vars[var_name]['truth_value'] = not sat_result.get(-idx, False)

        # Step 5: Track beliefs using fluid-like propagation
        # Agents' beliefs flow through the statement network
        observations = []
        for stmt in statements:
            speaker = stmt['speaker']
            content = stmt['content']
            # Determine if this observation should be believed
            # Based on speaker's vorticity and statement consistency
            vorticity = truth_policies.get(speaker, 0)
            is_credible = (vorticity == 1)  # Only always-truthful are initially credible
            
            for agent in agents:
                # Each agent observes the statement
                observations.append((agent, content, is_credible))
        
        belief_result = track_beliefs(agents, observations)
        
        # Step 6: Use amino acids for advanced logical analysis
        # Check for paradoxes in the statement set
        paradox_info = detect_paradox(clauses)
        
        # Check entailment for the question
        # Convert question to a clause (simplified)
        question_clause = []
        if 'who' in question.lower():
            # Find agent mentioned in question
            for agent in agents:
                if agent.lower() in question.lower():
                    # Check which statements about this agent are true
                    true_stmts = [v for v in prop_vars.values() 
                                 if v['truth_value'] is True and agent in v['content']]
                    if true_stmts:
                        # The answer is likely this agent
                        computed_answer = agent
                        break
            else:
                # Default to first agent if none found
                computed_answer = agents[0] if agents else "Unknown"
        else:
            # For other question types, use the most consistent agent
            computed_answer = agents[0] if agents else "Unknown"

        # Step 7: Use constraint solving to verify uniqueness
        # Build a CSP for agent truth assignments
        variables = list(agents)
        domains = {agent: [True, False] for agent in agents}  # True = truthful
        
        constraints = []
        for stmt in statements:
            speaker = stmt['speaker']
            content = stmt['content']
            
            # Constraint: if speaker is truthful, content must be consistent
            # Simplified: check if content refers to another agent's truthfulness
            for other_agent in agents:
                if other_agent != speaker and other_agent in content:
                    # Create a constraint linking speaker and other_agent
                    def make_constraint(s, o):
                        return lambda vars: (not vars[s]) or (vars[o] == ('truthful' in content.lower()))
                    
                    constraints.append(([speaker, other_agent], make_constraint(speaker, other_agent)))
        
        # Check if solution is unique
        unique = is_uniquely_solvable(variables, domains, constraints)
        
        # Step 8: Compute confidence using agreement between methods
        confidence_sources = []
        
        # Confidence from SAT consistency
        if sat_result:
            confidence_sources.append(0.8)
        
        # Confidence from paradox detection
        if paradox_info is not None:
            # No paradox found is good
            confidence_sources.append(0.7)
        
        # Confidence from uniqueness
        if unique:
            confidence_sources.append(0.9)
        else:
            confidence_sources.append(0.5)
        
        # Confidence from belief tracking consistency
        if belief_result and len(belief_result) > 0:
            confidence_sources.append(0.6)
        
        # Use T1 primitive to combine confidence
        if confidence_sources:
            confidence = confidence_from_agreement(confidence_sources)
        else:
            confidence = 0.5

        # Fluid dynamics final state: system reaches equilibrium
        # The answer emerges from the consistent flow of truth
        return {
            'answer': computed_answer,
            'confidence': float(confidence),
            'reasoning': f"Fluid dynamics analysis: vorticity sum = {structure['total_vorticity']}, "
                        f"SAT consistent: {sat_result is not None}, "
                        f"Paradox detected: {paradox_info is not None}, "
                        f"Unique solution: {unique}",
            'prop_vars': prop_vars,
            'sat_result': sat_result
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result['answer']
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                'candidate': candidate,
                'score': score,
                'raw_score': score
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using fluid dynamics principles."""
        # Bernoulli's principle: pressure decreases as velocity increases
        # Here, interpret as confidence adjustment based on score variance
        
        if not scored:
            return scored
        
        scores = [item['raw_score'] for item in scored]
        max_score = max(scores) if scores else 1.0
        min_score = min(scores) if scores else 0.0
        
        # Fluid pressure adjustment: normalize and apply confidence
        for item in scored:
            raw = item['raw_score']
            if max_score > min_score:
                # Normalize to [0, 1]
                normalized = (raw - min_score) / (max_score - min_score)
                # Apply Bernoulli-like adjustment: sqrt transformation
                adjusted = normalized ** 0.5
            else:
                adjusted = 0.5  # Uniform pressure
            
            item['score'] = float(adjusted)
        
        return scored

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance."""
        if not a or not b:
            return 1.0
        
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0