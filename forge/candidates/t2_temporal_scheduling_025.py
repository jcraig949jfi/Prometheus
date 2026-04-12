import re
import zlib
from typing import Dict, List, Any, Tuple, Optional

from forge_primitives import topological_sort, information_sufficiency, solve_constraints
from forge.amino_acids.constraint_acids import solve_first


class ReasoningTool:
    """Network engineering x constraint_acids - temporal_scheduling"""

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
        """Extract events, constraints, and question from scheduling prompt."""
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        
        events = []
        constraints = []
        question = ""
        
        # Find events (capitalized words or phrases that appear in constraints)
        event_pattern = r'\b([A-Z][a-zA-Z]+)\b'
        all_words = re.findall(event_pattern, prompt)
        # Filter to plausible event names (not common words)
        common_words = {'The', 'A', 'An', 'And', 'Or', 'But', 'If', 'Then', 'Before', 'After', 
                       'Must', 'Cannot', 'Same', 'Time', 'Day', 'Hour', 'Minute', 'Schedule'}
        events = sorted(set([w for w in all_words if w not in common_words]))
        
        # Extract temporal constraints
        for line in lines:
            line_lower = line.lower()
            # Look for "A before B", "A after B", "A and B same time" patterns
            if 'before' in line_lower or 'after' in line_lower or 'same time' in line_lower:
                # Find event pairs
                words = re.findall(event_pattern, line)
                if len(words) >= 2:
                    ev1, ev2 = words[0], words[1]
                    if 'before' in line_lower:
                        constraints.append((ev1, ev2, 'before'))
                    elif 'after' in line_lower:
                        constraints.append((ev1, ev2, 'after'))
                    elif 'same time' in line_lower:
                        constraints.append((ev1, ev2, 'same'))
        
        # Extract question (usually last sentence)
        sentences = [s.strip() for s in re.split(r'[.!?]', prompt) if s.strip()]
        if sentences:
            question = sentences[-1]
        
        # Extract any numerical time constraints
        time_constraints = []
        time_pattern = r'(\d+)\s*(?:hour|minute|day)s?\s*(?:apart|between|duration)'
        time_matches = re.findall(time_pattern, prompt.lower())
        if time_matches:
            time_constraints = [int(t) for t in time_matches]
        
        return {
            "events": events,
            "constraints": constraints,
            "question": question,
            "time_constraints": time_constraints,
            "raw": prompt
        }

    def _reason(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Use network engineering concepts to resolve scheduling conflicts."""
        events = structure["events"]
        constraints = structure["constraints"]
        
        # Build constraint graph for topological analysis
        edges = []
        for ev1, ev2, rel in constraints:
            if rel == 'before':
                edges.append((ev1, ev2))
            elif rel == 'after':
                edges.append((ev2, ev1))
            # 'same' constraints handled separately
        
        # CRITICAL PRIMITIVE 1: topological_sort - determines feasible order
        try:
            topological_order = topological_sort(edges)
            if topological_order is None:
                # Cycle detected - inconsistent constraints
                topological_order = []
        except Exception:
            topological_order = []
        
        # CRITICAL PRIMITIVE 2: information_sufficiency - check if system is determined
        n_events = len(events)
        n_constraints = len(constraints)
        sufficiency = information_sufficiency(n_events, n_constraints)
        
        # Build CSP for exact scheduling
        variables = events
        domains = {ev: list(range(n_events)) for ev in events}  # Time slots 0..n-1
        
        csp_constraints = []
        
        # Convert constraints to CSP format
        for ev1, ev2, rel in constraints:
            if rel == 'before':
                def before_constraint(t1, t2):
                    return t1 < t2
                csp_constraints.append(([ev1, ev2], before_constraint))
            elif rel == 'after':
                def after_constraint(t1, t2):
                    return t1 > t2
                csp_constraints.append(([ev1, ev2], after_constraint))
            elif rel == 'same':
                def same_constraint(t1, t2):
                    return t1 == t2
                csp_constraints.append(([ev1, ev2], same_constraint))
        
        # CRITICAL AMINO ACID: solve_first - finds first valid schedule
        solution = None
        if variables and csp_constraints:
            try:
                solution = solve_first(variables_domains=domains, constraints=csp_constraints)
            except Exception:
                solution = None
        
        # CRITICAL PRIMITIVE 3: solve_constraints - alternative solver
        backup_solution = None
        if not solution and variables and csp_constraints:
            try:
                backup_solution = solve_constraints(variables, domains, csp_constraints)
            except Exception:
                backup_solution = None
        
        # Determine which event to schedule (answer to question)
        computed_answer = ""
        reasoning_text = ""
        
        # Analyze question to determine what's being asked
        question = structure["question"].lower()
        
        if solution is not None:
            # Use CSP solution
            schedule = solution
            reasoning_text = "CSP solution found"
        elif backup_solution is not None:
            # Use backup solution
            schedule = backup_solution
            reasoning_text = "Backup constraint solution found"
        elif topological_order:
            # Use topological order
            schedule = {ev: i for i, ev in enumerate(topological_order)}
            reasoning_text = "Topological order used"
        else:
            # Fallback: assign arbitrary order
            schedule = {ev: i for i, ev in enumerate(events)}
            reasoning_text = "Arbitrary ordering"
        
        # Determine answer based on question type
        if 'first' in question or 'earliest' in question:
            # Find event with smallest time slot
            if schedule:
                earliest_event = min(schedule.items(), key=lambda x: x[1])[0]
                computed_answer = earliest_event
        elif 'last' in question or 'latest' in question:
            # Find event with largest time slot
            if schedule:
                latest_event = max(schedule.items(), key=lambda x: x[1])[0]
                computed_answer = latest_event
        elif 'conflict' in question or 'impossible' in question:
            # Check if constraints are inconsistent
            if topological_order is None or sufficiency == "overconstrained":
                computed_answer = "Yes"  # There is a conflict
            else:
                computed_answer = "No"   # No conflict
        elif 'which event' in question:
            # Extract event name from question
            question_events = re.findall(r'\b([A-Z][a-zA-Z]+)\b', structure["question"])
            if question_events:
                # Return first event mentioned in question that's in our schedule
                for ev in question_events:
                    if ev in schedule:
                        computed_answer = ev
                        break
        
        # Default: if no specific answer determined, use topological order info
        if not computed_answer and topological_order:
            computed_answer = topological_order[0] if topological_order else events[0] if events else ""
        
        # Confidence based on solution quality and sufficiency
        confidence = 0.5
        if solution is not None:
            confidence = 0.9
        elif backup_solution is not None:
            confidence = 0.7
        elif topological_order:
            confidence = 0.6
        
        # Adjust confidence based on information sufficiency
        if sufficiency == "determined":
            confidence = min(confidence + 0.2, 1.0)
        elif sufficiency == "overconstrained":
            confidence = max(confidence - 0.3, 0.1)
        
        return {
            "answer": computed_answer,
            "confidence": confidence,
            "reasoning": f"{reasoning_text}. Sufficiency: {sufficiency}. Topological order: {topological_order}",
            "schedule": schedule,
            "topological_order": topological_order,
            "sufficiency": sufficiency
        }

    def _score(self, candidates: List[str], reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates based on similarity to computed answer."""
        computed_answer = reasoning_result["answer"]
        confidence = reasoning_result["confidence"]
        
        results = []
        
        for candidate in candidates:
            # Primary scoring: exact match or substring match
            if computed_answer and computed_answer.lower() in candidate.lower():
                base_score = 1.0
            elif computed_answer and candidate.lower() in computed_answer.lower():
                base_score = 0.8
            else:
                # Fallback: NCD similarity
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
        """Calibrate scores to ensure proper distribution."""
        if not scored:
            return scored
        
        # Normalize scores to 0-1 range
        scores = [item["score"] for item in scored]
        if scores:
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