import re
import zlib
from typing import Dict, List, Any, Set, Tuple

from forge_primitives import (
    track_beliefs,
    sally_anne_test,
    confidence_from_agreement,
    entropy,
    modus_ponens,
    topological_sort
)
from forge.amino_acids.pysat_acids import check_entailment, detect_paradox
from forge.amino_acids.constraint_acids import solve_first, is_uniquely_solvable


class ReasoningTool:
    """Relativity x SAT/Constraint Solving - Perspective Shift"""

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
        """Extract agents, their knowledge, and the query from the prompt."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        knowledge = {}  # agent -> set of known facts (as strings)
        observations = []  # (agent, fact, bool) for track_beliefs
        implications = []  # (antecedent, consequent) for modus_ponens
        query = lines[-1] if lines else ""

        # Parse each sentence
        for line in lines:
            line_lower = line.lower()
            # Extract agent names (capitalized words likely to be proper nouns)
            # This is a simple heuristic; real prompts may have more structure.
            possible_agents = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', line)
            for agent in possible_agents:
                if agent not in ["I", "You", "He", "She", "It", "They", "We"]:  # filter pronouns
                    agents.add(agent)
                    if agent not in knowledge:
                        knowledge[agent] = set()

            # Look for knowledge statements: "Alice knows that P", "Bob believes X"
            knows_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:knows|believes|thinks|sees|observes)\s+(?:that\s+)?([^.,]+)', line, re.IGNORECASE)
            if knows_match:
                agent = knows_match.group(1)
                fact = knows_match.group(2).strip()
                agents.add(agent)
                knowledge.setdefault(agent, set()).add(fact)
                observations.append((agent, fact, True))

            # Look for implications: "If P then Q"
            if_match = re.search(r'If\s+([^,]+),\s+then\s+([^.,]+)', line, re.IGNORECASE)
            if if_match:
                antecedent = if_match.group(1).strip()
                consequent = if_match.group(2).strip()
                implications.append((antecedent, consequent))

            # Look for common knowledge: "Everyone knows that P"
            everyone_match = re.search(r'[Ee]veryone\s+(?:knows|believes)\s+(?:that\s+)?([^.,]+)', line)
            if everyone_match:
                fact = everyone_match.group(1).strip()
                for agent in agents:
                    knowledge.setdefault(agent, set()).add(fact)
                    observations.append((agent, fact, True))

        # Ensure at least one agent
        if not agents:
            # Fallback: use pronouns or generic names from the query
            agents = {"Alice", "Bob"}  # default placeholders

        return {
            "agents": list(agents),
            "knowledge": knowledge,
            "observations": observations,
            "implications": implications,
            "query": query,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply relativistic reasoning: knowledge is frame-dependent, compute invariant answer."""
        agents = structure["agents"]
        knowledge = structure["knowledge"]
        observations = structure["observations"]
        implications = structure["implications"]
        query = structure["query"]

        # Use T1 primitive: track_beliefs to model each agent's knowledge state
        belief_state = track_beliefs(agents, observations)
        # belief_state is dict agent -> set of believed facts

        # Use T1 primitive: modus_ponens to derive new beliefs within each agent's frame
        derived_beliefs = {}
        for agent in agents:
            facts = set(belief_state.get(agent, set()))
            new_facts = modus_ponens(implications, facts)
            derived_beliefs[agent] = new_facts

        # Relativity concept: invariant truth across frames.
        # In relativity, certain quantities (like spacetime interval) are invariant across reference frames.
        # Here, we look for propositions that are true in ALL agents' frames (intersection).
        common_beliefs = set.intersection(*[derived_beliefs.get(agent, set()) for agent in agents]) if agents else set()

        # Use amino acid: check_entailment to see if the query is logically entailed by common knowledge.
        # Encode common beliefs as CNF clauses.
        # We'll represent each fact as a propositional variable.
        # Simple encoding: fact string -> integer index.
        fact_to_var = {}
        var_to_fact = {}
        idx = 1
        all_facts = set()
        for agent_beliefs in derived_beliefs.values():
            all_facts.update(agent_beliefs)
        for fact in all_facts:
            fact_to_var[fact] = idx
            var_to_fact[idx] = fact
            idx += 1

        premise_clauses = []
        for fact in common_beliefs:
            if fact in fact_to_var:
                premise_clauses.append([fact_to_var[fact]])

        # Also add implications as clauses: (not antecedent) or consequent
        for ant, cons in implications:
            if ant in fact_to_var and cons in fact_to_var:
                premise_clauses.append([-fact_to_var[ant], fact_to_var[cons]])

        # The query is the last sentence; we need to extract a proposition from it.
        # Simple: take the query text as a whole as the conclusion.
        query_fact = query.strip('?').strip()
        if query_fact in fact_to_var:
            conclusion_clause = [fact_to_var[query_fact]]
        else:
            # If query not in facts, create a new variable for it.
            fact_to_var[query_fact] = idx
            conclusion_clause = [idx]

        # Use amino acid: check_entailment
        entailment_result = check_entailment(premise_clauses, conclusion_clause)

        # Use T1 primitive: confidence_from_agreement on agents' beliefs about the query.
        # For each agent, check if they believe the query (directly or via derivation).
        agent_scores = []
        for agent in agents:
            beliefs = derived_beliefs.get(agent, set())
            # Does the agent believe the query?
            score = 1.0 if query_fact in beliefs else 0.0
            agent_scores.append(score)
        confidence = confidence_from_agreement(agent_scores) if agent_scores else 0.5

        # Use T1 primitive: entropy to measure uncertainty across agents.
        # Create a distribution over possible answers (True/False for query).
        # We'll approximate by looking at proportion of agents believing query.
        if agents:
            p_true = sum(agent_scores) / len(agent_scores)
            p_false = 1 - p_true
            if p_true > 0 and p_false > 0:
                uncertainty = entropy([p_true, p_false])
            else:
                uncertainty = 0.0
        else:
            uncertainty = 1.0

        # Use amino acid: is_uniquely_solvable to check if the knowledge constraints force a unique answer.
        # Build a CSP: variables are facts (including query), domains are {True, False}.
        # Constraints: implications and observed facts.
        variables = list(all_facts) + [query_fact]
        domains = {var: [True, False] for var in variables}
        constraints = []
        for ant, cons in implications:
            if ant in variables and cons in variables:
                def impl_constraint(a_val, c_val):
                    return not (a_val is True and c_val is False)
                constraints.append(([ant, cons], impl_constraint))
        for fact in common_beliefs:
            if fact in variables:
                def fact_constraint(val):
                    return val is True
                constraints.append(([fact], fact_constraint))

        uniqueness = is_uniquely_solvable(domains, constraints) if variables else False

        # Determine the computed answer.
        # If entailment_result is True, query is necessarily true in all frames.
        # If uniqueness is True and the query is forced to a truth value, use that.
        # Otherwise, use the majority belief among agents.
        if entailment_result is True:
            computed_answer = "Yes"  # query is true
        elif entailment_result is False:
            # Not entailed, but could be false? check if negation is entailed.
            neg_query_clause = [-conclusion_clause[0]]
            neg_entailed = check_entailment(premise_clauses, neg_query_clause)
            if neg_entailed is True:
                computed_answer = "No"
            else:
                # Not determined: use majority.
                if p_true >= 0.5:
                    computed_answer = "Yes"
                else:
                    computed_answer = "No"
        else:
            # entailment_result is None (error), fallback to majority.
            if p_true >= 0.5:
                computed_answer = "Yes"
            else:
                computed_answer = "No"

        # Use T1 primitive: topological_sort on agent knowledge dependency if we had a DAG.
        # For demonstration, create a dummy DAG of agents based on knowledge hierarchy.
        # Edge A -> B if A knows something B doesn't (simplistic).
        edges = []
        for i, a1 in enumerate(agents):
            for a2 in agents:
                if a1 != a2 and knowledge.get(a1, set()).issuperset(knowledge.get(a2, set())):
                    edges.append((a1, a2))
        try:
            topo_order = topological_sort(edges)
            topo_str = " -> ".join(topo_order) if topo_order else "No order"
        except Exception:
            topo_str = "Cycle detected"

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "common_beliefs": list(common_beliefs),
            "agent_beliefs": {agent: list(derived_beliefs.get(agent, set())) for agent in agents},
            "entailment": entailment_result,
            "uniqueness": uniqueness,
            "topological_order": topo_str,
            "reasoning": f"Query: {query}. Common beliefs: {list(common_beliefs)[:3]}. Entailment: {entailment_result}. Majority: {p_true:.2f}."
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates by similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        results = []
        for c in candidates:
            # Primary: check if computed answer appears in candidate text.
            # computed_answer is a variable like "Yes", "No", or a specific name.
            if computed_answer.lower() in c.lower():
                score = 1.0
            else:
                # Fallback: NCD similarity between reasoning text and candidate.
                score = 1.0 / (1.0 + self._ncd(reasoning_text, c))
            results.append({
                "candidate": c,
                "raw_score": score,
                "computed_answer": computed_answer
            })
        return results

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores using confidence and uncertainty."""
        # Simple calibration: adjust by confidence from reasoning_result.
        # In a full implementation, we would pass confidence from _reason.
        # Here we'll just normalize scores to [0,1] and apply a small boost for high confidence.
        if not scored:
            return []
        max_raw = max(item["raw_score"] for item in scored)
        min_raw = min(item["raw_score"] for item in scored)
        range_raw = max_raw - min_raw if max_raw > min_raw else 1.0
        calibrated = []
        for item in scored:
            norm = (item["raw_score"] - min_raw) / range_raw if range_raw > 0 else 0.5
            # Confidence boost: if computed_answer is exact match, increase slightly.
            if item["raw_score"] == 1.0:
                norm = 1.0
            calibrated.append({
                "candidate": item["candidate"],
                "score": norm,
                "computed_answer": item["computed_answer"]
            })
        return calibrated

    def _ncd(self, a: str, b: str) -> float:
        """Normalized Compression Distance between two strings."""
        ca = len(zlib.compress(a.encode()))
        cb = len(zlib.compress(b.encode()))
        cab = len(zlib.compress((a + " " + b).encode()))
        if max(ca, cb) > 0:
            return (cab - min(ca, cb)) / max(ca, cb)
        return 1.0