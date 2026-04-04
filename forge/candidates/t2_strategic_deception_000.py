import re
import zlib
from typing import Dict, List, Any, Tuple, Set

from forge_primitives import (
    bayesian_update,
    entropy,
    confidence_from_agreement,
    track_beliefs,
    modus_ponens,
    solve_constraints
)
from forge.amino_acids.pysat_acids import check_entailment
from forge.amino_acids.constraint_acids import is_uniquely_solvable
from forge.amino_acids.nashpy_acids import find_equilibria


class ReasoningTool:
    """Immunology x SAT/Game Theory - strategic_deception"""

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
        """Parse prompt to extract agents, statements, goals, and relationships."""
        lines = [line.strip() for line in prompt.split('.') if line.strip()]
        agents = set()
        statements = []  # (agent, statement, is_public)
        goals = {}       # agent -> goal description
        relationships = []  # (agent1, agent2, relationship)
        question = lines[-1] if lines else ""

        current_agent = None
        for line in lines:
            # Extract agent names (capitalized proper nouns)
            agent_matches = re.findall(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b', line)
            for agent in agent_matches:
                if agent not in ["The", "They", "He", "She", "It"]:
                    agents.add(agent)
                    current_agent = agent

            # Extract goals
            if "wants" in line.lower() or "goal" in line.lower() or "intends" in line.lower():
                if current_agent:
                    goal_match = re.search(r'wants to (.+?)(?:\.|,| but| however|$)', line.lower())
                    if goal_match:
                        goals[current_agent] = goal_match.group(1).strip()

            # Extract statements
            if "says" in line.lower() or "claims" in line.lower() or "states" in line.lower():
                if current_agent:
                    # Find the statement content
                    quote_match = re.search(r'["\'](.+?)["\']', line)
                    if quote_match:
                        statement = quote_match.group(1)
                        is_public = "public" in line.lower() or "announces" in line.lower()
                        statements.append((current_agent, statement, is_public))

            # Extract relationships
            if "trusts" in line.lower() or "distrusts" in line.lower() or "allies" in line.lower():
                rel_match = re.search(r'(\w+) (trusts|distrusts|is allies with) (\w+)', line.lower())
                if rel_match:
                    a1, rel, a2 = rel_match.groups()
                    relationships.append((a1.capitalize(), rel, a2.capitalize()))

        return {
            "agents": list(agents),
            "statements": statements,
            "goals": goals,
            "relationships": relationships,
            "question": question,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Immunology-inspired reasoning: model deception as pathogen evasion."""
        agents = structure["agents"]
        statements = structure["statements"]
        goals = structure["goals"]
        relationships = structure["relationships"]
        question = structure["question"]

        if not agents:
            return {"answer": "Unknown", "confidence": 0.0, "reasoning": "No agents found"}

        # 1. IMMUNOLOGY FRAMEWORK: Model statements as antigens
        # High entropy = diverse deceptive strategies (like pathogen variability)
        statement_texts = [stmt[1] for stmt in statements]
        statement_words = [len(text.split()) for text in statement_texts]
        if statement_words:
            # Normalize word counts to probabilities
            total_words = sum(statement_words)
            probs = [w/total_words for w in statement_words] if total_words > 0 else [1.0/len(statement_words)]*len(statement_words)
            strategy_entropy = entropy(probs)  # T1 PRIMITIVE 1
        else:
            strategy_entropy = 0.0

        # 2. Track belief propagation (immune memory)
        # Map statements to boolean facts
        facts = set()
        observations = []
        for agent, stmt, is_public in statements:
            fact_id = f"{agent}_said_{hash(stmt) % 1000}"
            facts.add(fact_id)
            # All agents observe public statements
            if is_public:
                for obs_agent in agents:
                    observations.append((obs_agent, fact_id, True))
            else:
                # Only the speaker knows their own statement
                observations.append((agent, fact_id, True))

        belief_state = track_beliefs(agents, observations)  # T1 PRIMITIVE 2

        # 3. SAT analysis for logical consistency (immune system checking for foreign patterns)
        clauses = []
        var_map = {}
        next_var = 1

        # Create variables for each statement
        for agent, stmt, _ in statements:
            key = f"{agent}:{stmt}"
            if key not in var_map:
                var_map[key] = next_var
                next_var += 1

        # Add constraints based on goals and relationships
        # If agent A distrusts B, then B's statements are likely false
        for a1, rel, a2 in relationships:
            if rel == "distrusts":
                for agent, stmt, _ in statements:
                    if agent == a2:
                        var = var_map.get(f"{agent}:{stmt}")
                        if var:
                            clauses.append([-var])  # Distrusted agent's statements are false

        # Check if statements entail contradictions
        if clauses and var_map:
            # Create a simple entailment check: if any statement contradicts common knowledge
            premise_clauses = clauses[:]
            # Assume at least one statement must be true (someone is telling truth)
            conclusion_clause = [var_map[list(var_map.keys())[0]]] if var_map else [1]
            
            entailment_result = check_entailment(premise_clauses, conclusion_clause)  # AMINO ACID 1
            has_contradiction = entailment_result is not None and not entailment_result
        else:
            has_contradiction = False

        # 4. Game theory: find Nash equilibria in deception game
        # Simple 2x2 payoff matrix based on entropy and contradictions
        if len(agents) >= 2:
            # Payoff for deception vs truth-telling
            payoff_a = [[strategy_entropy, -strategy_entropy], 
                       [0.5, 0.5]]  # Player A payoffs
            payoff_b = [[-strategy_entropy, strategy_entropy],
                       [0.5, 0.5]]  # Player B payoffs
            
            equilibria = find_equilibria(payoff_a, payoff_b)  # AMINO ACID 2
            has_equilibrium = bool(equilibria)
        else:
            has_equilibrium = False

        # 5. Constraint solving for most likely true statement
        variables = list(var_map.keys())
        domains = {var: [0, 1] for var in variables}  # 0=false, 1=true
        
        def truth_constraint(assignment):
            # At least one statement must be true
            return sum(assignment.values()) >= 1
        
        constraints = [(variables, truth_constraint)]
        
        solution = solve_constraints(variables, domains, constraints)  # T1 PRIMITIVE 3
        
        # 6. Bayesian update on deception probability
        prior_deception = 0.3  # Base rate of deception in strategic scenarios
        likelihood = strategy_entropy if strategy_entropy > 0 else 0.1
        deception_prob = bayesian_update(prior_deception, likelihood, false_positive=0.1)  # T1 PRIMITIVE 4
        
        # 7. Determine which agent is most deceptive
        agent_scores = {}
        for agent in agents:
            score = 0.0
            # Agent's statements that might be false
            agent_stmts = [stmt for (a, stmt, _) in statements if a == agent]
            if agent_stmts:
                # More statements = more opportunity for deception
                score += len(agent_stmts) * 0.1
            
            # Distrusted by others
            distrust_count = sum(1 for (a1, rel, a2) in relationships 
                               if rel == "distrusts" and a2 == agent)
            score += distrust_count * 0.2
            
            # Goals that conflict with others
            agent_goal = goals.get(agent, "")
            conflicting_goals = sum(1 for other, g in goals.items() 
                                  if other != agent and self._goals_conflict(agent_goal, g))
            score += conflicting_goals * 0.15
            
            agent_scores[agent] = score * deception_prob

        if agent_scores:
            most_deceptive = max(agent_scores.items(), key=lambda x: x[1])
            computed_answer = most_deceptive[0]
            
            # Confidence from multiple indicators
            confidence_scores = [
                deception_prob,
                most_deceptive[1] / (max(agent_scores.values()) + 0.001),
                0.7 if has_contradiction else 0.3,
                0.8 if has_equilibrium else 0.2
            ]
            confidence = confidence_from_agreement(confidence_scores)  # T1 PRIMITIVE 5
        else:
            computed_answer = agents[0] if agents else "Unknown"
            confidence = 0.5

        reasoning_text = (
            f"Immunology model: deception entropy={strategy_entropy:.2f}, "
            f"deception probability={deception_prob:.2f}. "
            f"SAT contradiction detected: {has_contradiction}. "
            f"Nash equilibrium exists: {has_equilibrium}. "
            f"Most deceptive agent: {computed_answer}."
        )

        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": reasoning_text,
            "deception_prob": deception_prob,
            "strategy_entropy": strategy_entropy,
            "has_contradiction": has_contradiction,
            "has_equilibrium": has_equilibrium
        }

    def _goals_conflict(self, goal1: str, goal2: str) -> bool:
        """Check if two goals conflict."""
        goal1_lower = goal1.lower()
        goal2_lower = goal2.lower()
        
        conflict_pairs = [
            ("win", "lose"), ("take", "keep"), ("attack", "defend"),
            ("increase", "decrease"), ("help", "harm"), ("support", "oppose")
        ]
        
        for a, b in conflict_pairs:
            if (a in goal1_lower and b in goal2_lower) or (b in goal1_lower and a in goal2_lower):
                return True
        return False

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        reasoning_text = reasoning_result["reasoning"]
        
        results = []
        for candidate in candidates:
            # Primary: exact match or substring match of computed answer
            if computed_answer.lower() in candidate.lower():
                base_score = 1.0
            else:
                # Fallback: NCD similarity to reasoning text
                base_score = 1.0 / (1.0 + self._ncd(computed_answer, candidate))
            
            # Adjust by confidence
            adjusted_score = base_score * reasoning_result["confidence"]
            
            results.append({
                "candidate": candidate,
                "score": adjusted_score,
                "base_score": base_score,
                "confidence": reasoning_result["confidence"]
            })
        
        return results

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

    def _calibrate(self, scored: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calibrate scores to ensure proper ranking."""
        if not scored:
            return scored
        
        # Simple normalization to [0, 1] range
        scores = [item["score"] for item in scored]
        if max(scores) > min(scores):
            for item in scored:
                item["score"] = (item["score"] - min(scores)) / (max(scores) - min(scores))
        else:
            for item in scored:
                item["score"] = 0.5
        
        return scored