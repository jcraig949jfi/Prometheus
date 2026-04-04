import re
import zlib
from typing import Dict, List, Any, Tuple
from forge_primitives import (
    bayesian_update,
    confidence_from_agreement,
    entropy,
    solve_sat,
    track_beliefs,
    modus_ponens
)
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """signal_processing x pysat_acids - liar_detection"""

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
        question = lines[-1] if lines else ""
        
        agents = []
        statements = []
        truth_policies = {}  # agent -> policy ("always truth", "always lie", "alternate", etc.)
        
        # Extract agent names (capitalized words that appear before "says" or "states")
        agent_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:says|states|claims|asserts)'
        for line in lines:
            agent_matches = re.findall(agent_pattern, line)
            for agent in agent_matches:
                if agent not in agents:
                    agents.append(agent)
        
        # Extract statements and associate with agents
        for line in lines:
            for agent in agents:
                if agent in line and ('says' in line or 'states' in line or 'claims' in line or 'asserts' in line):
                    # Extract the quoted statement or the clause after "that"
                    quote_match = re.search(r'["“]([^"”]+)["”]', line)
                    that_match = re.search(r'that\s+(.+?)(?:\.|$)', line)
                    if quote_match:
                        stmt = quote_match.group(1).strip()
                    elif that_match:
                        stmt = that_match.group(1).strip()
                    else:
                        # Fallback: take text after "says" until period
                        says_idx = line.find('says')
                        if says_idx != -1:
                            stmt = line[says_idx+4:].strip().rstrip('.')
                        else:
                            stmt = ""
                    if stmt:
                        statements.append((agent, stmt))
        
        # Extract truth policies from prompt descriptions
        policy_keywords = {
            'always tells the truth': 'truth',
            'always lies': 'lie',
            'alternates': 'alternate',
            'random': 'random',
            'truth-teller': 'truth',
            'liar': 'lie'
        }
        for line in lines:
            for agent in agents:
                if agent in line:
                    for keyword, policy in policy_keywords.items():
                        if keyword in line.lower():
                            truth_policies[agent] = policy
        
        return {
            'agents': agents,
            'statements': statements,
            'policies': truth_policies,
            'question': question,
            'raw_prompt': prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use signal processing concepts (noise filtering, SNR) to resolve liar puzzles."""
        agents = structure['agents']
        statements = structure['statements']
        policies = structure['policies']
        question = structure['question']
        
        # Signal Processing Scaffold:
        # Treat truth-tellers as high-SNR signals, liars as inverted signals,
        # alternators as periodic signals, random as noise.
        # Use Bayesian filtering to update belief states.
        
        # Initialize belief priors: uniform over possible worlds
        # A "world" is an assignment of truth values to base facts
        # We'll extract base facts from statements
        base_facts = set()
        for _, stmt in statements:
            # Simple extraction: look for atomic propositions
            # Remove negations for base fact extraction
            clean_stmt = re.sub(r'\b(not|never|no)\s+', '', stmt, flags=re.IGNORECASE)
            # Take first few words as fact identifier
            words = clean_stmt.split()[:3]
            if words:
                base_facts.add(' '.join(words).lower())
        
        base_facts = list(base_facts)
        if not base_facts:
            base_facts = ['default_fact']
        
        # Create possible worlds (2^n combinations)
        n_facts = len(base_facts)
        possible_worlds = []
        for i in range(2**n_facts):
            world = {}
            for j in range(n_facts):
                world[base_facts[j]] = bool((i >> j) & 1)
            possible_worlds.append(world)
        
        # Initial prior: uniform
        prior = 1.0 / len(possible_worlds) if possible_worlds else 0.0
        
        # Use T1 primitive: entropy of initial distribution
        init_probs = [prior] * len(possible_worlds) if possible_worlds else [1.0]
        initial_entropy_val = entropy(init_probs)
        
        # Process each statement as evidence
        current_belief = prior
        likelihoods = []
        
        for agent, stmt in statements:
            policy = policies.get(agent, 'unknown')
            
            # Determine reliability (SNR) based on policy
            if policy == 'truth':
                reliability = 0.95  # High SNR
                false_positive = 0.05
            elif policy == 'lie':
                reliability = 0.05  # Inverted signal (low effective SNR)
                false_positive = 0.95
            elif policy == 'alternate':
                reliability = 0.5  # Periodic, average SNR
                false_positive = 0.5
            else:
                reliability = 0.5  # Unknown, assume noisy
                false_positive = 0.5
            
            # Use T1 primitive: Bayesian update
            # Simplified: update belief that statement is true
            updated = bayesian_update(current_belief, reliability, false_positive)
            if updated is not None:
                current_belief = updated
                likelihoods.append(reliability)
        
        # Use T1 primitive: confidence from agreement among likelihoods
        if likelihoods:
            confidence_val = confidence_from_agreement(likelihoods)
        else:
            confidence_val = 0.5
        
        # Use amino acid: SAT solving to check consistency
        # Encode statements as logical constraints
        clauses = []
        var_map = {}
        var_counter = 1
        
        for agent, stmt in statements:
            policy = policies.get(agent, 'unknown')
            
            # Create variable for the statement truth
            if stmt not in var_map:
                var_map[stmt] = var_counter
                var_counter += 1
            stmt_var = var_map[stmt]
            
            # Encode policy constraints
            if policy == 'truth':
                # Agent says X → X is true
                clauses.append([-stmt_var, stmt_var])  # Actually: stmt_var must be positive
                # Simpler: stmt_var is true
                clauses.append([stmt_var])
            elif policy == 'lie':
                # Agent says X → X is false
                clauses.append([-stmt_var, -stmt_var])  # Actually: stmt_var must be negative
                # Simpler: not stmt_var
                clauses.append([-stmt_var])
            elif policy == 'alternate':
                # For alternators, need context - simplify to either true or false
                # We'll use a fresh variable to represent alternator state
                alt_var = var_counter
                var_counter += 1
                # stmt_var ↔ alt_var (statement true if alternator in truth phase)
                clauses.append([-stmt_var, alt_var])
                clauses.append([stmt_var, -alt_var])
        
        # Use amino acid: solve SAT to find consistent assignment
        sat_result = None
        if clauses and var_map:
            sat_result = solve(clauses)
        
        # Determine answer based on question
        computed_answer = ""
        
        # Extract target from question
        if 'who' in question.lower():
            # Find agent that satisfies conditions
            if sat_result:
                # Check which agents' statements are consistent with their policies
                consistent_agents = []
                for agent in agents:
                    agent_statements = [stmt for a, stmt in statements if a == agent]
                    if agent_statements:
                        # Check if all statements have consistent truth values
                        consistent = True
                        for stmt in agent_statements:
                            if stmt in var_map:
                                var = var_map[stmt]
                                if var in sat_result:
                                    # For truth-teller: sat_result[var] should be True
                                    # For liar: sat_result[var] should be False
                                    policy = policies.get(agent, 'unknown')
                                    if policy == 'truth' and not sat_result[var]:
                                        consistent = False
                                        break
                                    elif policy == 'lie' and sat_result[var]:
                                        consistent = False
                                        break
                        if consistent:
                            consistent_agents.append(agent)
                
                if consistent_agents:
                    # Use T1 primitive: track_beliefs to see which agent knows the answer
                    observations = []
                    for agent, stmt in statements:
                        if stmt in var_map:
                            var = var_map[stmt]
                            truth_val = sat_result.get(var, False)
                            observations.append((agent, stmt, truth_val))
                    
                    belief_state = track_beliefs(agents, observations)
                    
                    # Agent with most consistent beliefs is likely answer
                    best_agent = max(agents, key=lambda a: len(belief_state.get(a, set())))
                    computed_answer = best_agent
                else:
                    # Fallback: first agent
                    computed_answer = agents[0] if agents else "Unknown"
            else:
                computed_answer = agents[0] if agents else "Unknown"
        
        elif 'what' in question.lower() or 'which' in question.lower():
            # Answer is likely a fact or statement
            if sat_result and var_map:
                # Find the fact that is true in all consistent worlds
                true_facts = []
                for stmt, var in var_map.items():
                    if sat_result.get(var, False):
                        true_facts.append(stmt)
                
                if true_facts:
                    # Use signal processing analogy: fact with highest "signal strength"
                    # Measured by how many agents (weighted by reliability) support it
                    fact_scores = {}
                    for fact in true_facts:
                        score = 0
                        for agent, stmt in statements:
                            if stmt == fact:
                                policy = policies.get(agent, 'unknown')
                                if policy == 'truth':
                                    score += 1.0
                                elif policy == 'lie':
                                    score -= 1.0
                                elif policy == 'alternate':
                                    score += 0.5
                        fact_scores[fact] = score
                    
                    best_fact = max(fact_scores.items(), key=lambda x: x[1])[0]
                    computed_answer = best_fact
                else:
                    computed_answer = "None"
            else:
                computed_answer = "Cannot determine"
        
        else:
            # Generic fallback
            computed_answer = agents[0] if agents else "Unknown"
        
        # Use amino acid: detect paradox to check if puzzle is self-contradictory
        paradox_detected = False
        if clauses:
            paradox_check = detect_paradox(clauses)
            if paradox_check is not None:
                paradox_detected = paradox_check
        
        # Final confidence adjustment based on paradox detection and entropy
        if paradox_detected:
            confidence_val *= 0.5  # Lower confidence if paradoxical
        
        # Use T1 primitive: modus_ponens for logical deduction
        premises = []
        for agent, stmt in statements:
            policy = policies.get(agent, 'unknown')
            if policy == 'truth':
                # Agent says P → P
                premises.append((f"{agent}_says_{stmt}", stmt))
        
        facts = set()
        if sat_result:
            for stmt, var in var_map.items():
                if sat_result.get(var, False):
                    facts.add(stmt)
        
        deduced = modus_ponens(premises, facts)
        
        # If we deduced something specific, use it as answer
        if deduced and 'who' in question.lower():
            # Look for agent names in deduced facts
            for fact in deduced:
                for agent in agents:
                    if agent.lower() in fact.lower():
                        computed_answer = agent
                        break
        
        return {
            'answer': computed_answer,
            'confidence': min(max(confidence_val, 0.0), 1.0),
            'reasoning': f"Signal processing analysis: initial entropy={initial_entropy_val:.3f}, "
                        f"SAT consistent={sat_result is not None}, "
                        f"paradox detected={paradox_detected}",
            'deduced_facts': list(deduced),
            'consistent_assignment': sat_result
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result['answer']
        confidence = reasoning_result['confidence']
        reasoning_text = reasoning_result['reasoning']
        
        results = []
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Secondary: also check reasoning text similarity
            reasoning_sim = 1.0 / (1.0 + self._ncd(reasoning_text, candidate))
            
            # Combined score weighted by confidence
            final_score = (base_score * 0.7 + reasoning_sim * 0.3) * confidence
            
            results.append({
                'candidate': candidate,
                'score': final_score,
                'base_score': base_score,
                'reasoning_sim': reasoning_sim
            })
        
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        scores = [item['score'] for item in scored]
        if max(scores) - min(scores) < 0.01:
            # All scores too close, differentiate
            for i, item in enumerate(scored):
                item['score'] = item['base_score'] * 0.9 + (i * 0.01)
        
        # Ensure scores are in [0, 1]
        for item in scored:
            item['score'] = max(0.0, min(1.0, item['score']))
        
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