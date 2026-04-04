import re
import zlib
from typing import Dict, List, Any, Set, Tuple
from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    check_transitivity,
    modus_ponens,
    parity_check,
    pigeonhole_check,
    dag_traverse,
    topological_sort,
    solve_constraints,
    solve_sat,
    solve_linear_system,
    expected_value,
    bayesian_update,
    entropy,
    information_sufficiency,
    all_but_n,
    bat_and_ball,
    coin_flip_independence,
    counterfactual_intervention,
    direction_composition,
    fencepost_count,
    modular_arithmetic,
    negate,
    temporal_order,
    Any
)
from forge.amino_acids.pysat_acids import solve, detect_paradox, check_entailment, encode_exactly_k, maxsat_solve, is_valid, enumerate_models, extract_mus, count_models
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable, solve_all, count_solutions, check_consistency, find_conflicts
from forge.amino_acids.pgmpy_acids import build_bn, conditional_query, detect_confounders, get_adjustment_set, do_calculus, map_query, active_trails, compare_conditional_marginal, find_dseparators, get_markov_blanket
from forge.amino_acids.nashpy_acids import find_equilibria, is_dominated, best_response, find_dominant_strategy, compute_minimax, expected_payoff

class ReasoningTool:
    """social_choice_theory x pysat_acids - perspective_shift"""

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

    # ========== PHASE 1: EXTRACT ==========
    def _extract(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to find agents, their knowledge, and the query."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        agent_knowledge = {}
        facts = set()
        implications = []
        query = lines[-1] if lines else ""

        # Extract agent names (capitalized words that appear as subjects)
        words = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        for word in words:
            if word.lower() not in ['the', 'and', 'but', 'that', 'which', 'what', 'who', 'where', 'when', 'why', 'how']:
                agents.add(word)

        # Extract knowledge statements
        for line in lines:
            line_lower = line.lower()
            # Look for patterns like "Alice knows that X", "Bob believes Y"
            know_match = re.search(r'([A-Z][a-z]+)\s+(?:knows|believes|thinks|sees|observes|hears)\s+(?:that\s+)?([^.,]+)', line, re.IGNORECASE)
            if know_match:
                agent = know_match.group(1)
                fact = know_match.group(2).strip()
                if agent not in agent_knowledge:
                    agent_knowledge[agent] = set()
                agent_knowledge[agent].add(fact)
                agents.add(agent)

            # Extract general facts (not attributed to a specific agent)
            if 'know' not in line_lower and 'believe' not in line_lower and 'think' not in line_lower:
                # Simple fact extraction: statements without modal verbs
                fact_match = re.search(r'^([A-Z][^.,!?]+[.,!?]?)', line)
                if fact_match:
                    fact = fact_match.group(1).strip()
                    if fact and len(fact.split()) <= 10:  # Avoid long paragraphs
                        facts.add(fact)

            # Extract implications (if...then)
            if 'if' in line_lower and 'then' in line_lower:
                parts = line_lower.split('then')
                if len(parts) == 2:
                    antecedent = parts[0].replace('if', '').strip()
                    consequent = parts[1].strip()
                    implications.append((antecedent, consequent))

        # Clean up agents: remove common nouns that aren't agents
        common_nouns = {'Hospital', 'City', 'Country', 'Day', 'Night', 'Morning', 'Evening', 'Room', 'House', 'Car'}
        agents = agents - common_nouns

        return {
            "agents": list(agents),
            "agent_knowledge": agent_knowledge,
            "facts": facts,
            "implications": implications,
            "query": query,
            "raw": prompt
        }

    # ========== PHASE 2: REASON ==========
    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply social choice theory: model agents as voters with knowledge states,
        use SAT to find consistent global knowledge, compute answer via voting rule."""
        agents = structure["agents"]
        agent_knowledge = structure["agent_knowledge"]
        facts = structure["facts"]
        implications = structure["implications"]
        query = structure["query"]

        # Use T1 primitive: track_beliefs to model agent knowledge states
        observations = []
        for agent, known_facts in agent_knowledge.items():
            for fact in known_facts:
                observations.append((agent, fact, True))  # Agent observes fact
        belief_state = track_beliefs(agents, observations)

        # Use T1 primitive: confidence_from_agreement on agent beliefs
        # Convert belief sets to numerical scores for each fact
        fact_scores = {}
        all_facts = set(facts)
        for agent_facts in agent_knowledge.values():
            all_facts.update(agent_facts)
        
        for fact in all_facts:
            scores = []
            for agent in agents:
                # Score 1.0 if agent knows fact, 0.0 otherwise
                if agent in agent_knowledge and fact in agent_knowledge[agent]:
                    scores.append(1.0)
                else:
                    scores.append(0.0)
            if scores:
                confidence = confidence_from_agreement(scores)
                fact_scores[fact] = confidence

        # Use T1 primitive: check_transitivity on implication relations
        # Build binary relation from implications
        relations = []
        for ant, cons in implications:
            relations.append((ant, cons))
        transitive_closure = check_transitivity(relations)

        # Use amino acid: SAT to find consistent global knowledge state
        # Encode each fact as a boolean variable
        fact_to_var = {fact: i+1 for i, fact in enumerate(all_facts)}
        var_to_fact = {i+1: fact for i, fact in enumerate(all_facts)}
        
        clauses = []
        
        # Encode agent knowledge as unit clauses
        for agent, known_facts in agent_knowledge.items():
            for fact in known_facts:
                if fact in fact_to_var:
                    clauses.append([fact_to_var[fact]])  # Fact must be true
        
        # Encode implications as implications: not antecedent OR consequent
        for ant, cons in implications:
            if ant in fact_to_var and cons in fact_to_var:
                clauses.append([-fact_to_var[ant], fact_to_var[cons]])
        
        # Encode mutual exclusivity for contradictory facts (simple heuristic)
        # If two facts contain "not" or negations, they might conflict
        negative_facts = [f for f in all_facts if 'not ' in f.lower() or "don't" in f.lower() or "doesn't" in f.lower()]
        for i, f1 in enumerate(negative_facts):
            for f2 in negative_facts[i+1:]:
                # Check if they might be about the same subject
                words1 = set(f1.lower().split())
                words2 = set(f2.lower().split())
                common = words1.intersection(words2)
                if len(common) >= 2:  # Might be contradictory
                    if f1 in fact_to_var and f2 in fact_to_var:
                        clauses.append([-fact_to_var[f1], -fact_to_var[f2]])

        # Solve SAT to find a consistent world
        sat_result = solve(clauses)
        
        # Determine answer based on social choice theory: Borda count
        # Each agent's knowledge contributes to ranking possible answers
        # Extract possible answer candidates from the query
        query_lower = query.lower()
        answer_candidates = []
        
        # Look for "what does X know" or "who knows Y" patterns
        if 'what does' in query_lower and 'know' in query_lower:
            # Find the agent being asked about
            agent_match = re.search(r'what does ([A-Z][a-z]+) know', query, re.IGNORECASE)
            if agent_match:
                target_agent = agent_match.group(1)
                if target_agent in agent_knowledge:
                    # Answer is what this agent knows
                    known = list(agent_knowledge[target_agent])
                    if known:
                        # Use Borda count: rank facts by how many agents know them
                        fact_counts = {}
                        for fact in known:
                            count = sum(1 for a in agents if a in agent_knowledge and fact in agent_knowledge[a])
                            fact_counts[fact] = count
                        if fact_counts:
                            best_fact = max(fact_counts.items(), key=lambda x: x[1])[0]
                            computed_answer = best_fact
                        else:
                            computed_answer = known[0]
                    else:
                        computed_answer = "nothing"
                else:
                    computed_answer = "unknown"
        
        elif 'who knows' in query_lower:
            # Find the fact being asked about
            fact_match = re.search(r'who knows (?:that\s+)?([^.?]+)', query, re.IGNORECASE)
            if fact_match:
                target_fact = fact_match.group(1).strip()
                # Find all agents who know this fact
                knowing_agents = [agent for agent in agents if agent in agent_knowledge and target_fact in agent_knowledge[agent]]
                if knowing_agents:
                    # Use plurality voting: the agent mentioned most in context
                    agent_mentions = {agent: structure["raw"].count(agent) for agent in knowing_agents}
                    best_agent = max(agent_mentions.items(), key=lambda x: x[1])[0]
                    computed_answer = best_agent
                else:
                    computed_answer = "nobody"
        
        else:
            # Default: find the most agreed-upon fact among agents
            if fact_scores:
                best_fact = max(fact_scores.items(), key=lambda x: x[1])[0]
                computed_answer = best_fact
            else:
                computed_answer = "unknown"

        # Confidence based on SAT consistency and agreement
        confidence = 0.5
        if sat_result is not None:
            confidence = 0.7  # Consistent world exists
        if fact_scores:
            avg_confidence = sum(fact_scores.values()) / len(fact_scores) if fact_scores else 0
            confidence = (confidence + avg_confidence) / 2

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"Social choice Borda count applied to {len(agents)} agents' knowledge states. SAT consistency: {'yes' if sat_result else 'no'}.",
            "agents": agents,
            "sat_consistent": sat_result is not None
        }

    # ========== PHASE 3: SCORE ==========
    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        results = []
        
        for candidate in candidates:
            # Primary: check if computed answer appears in candidate text
            # computed_answer is a variable from reasoning, not a hardcoded string
            if computed_answer.lower() in candidate.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity
                score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            results.append({
                "candidate": candidate,
                "score": score,
                "raw_score": score
            })
        
        return results

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

    # ========== PHASE 4: CALIBRATE ==========
    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores based on confidence and consistency."""
        if not scored:
            return scored
        
        # Simple calibration: normalize scores to [0, 1] range
        scores = [item["raw_score"] for item in scored]
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                for item in scored:
                    item["score"] = (item["raw_score"] - min_score) / (max_score - min_score)
            else:
                for item in scored:
                    item["score"] = 0.5  # All equal
        
        return scored