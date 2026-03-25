"""Minimal failing case finder via iterative simplification.

When an adversarial task breaks a tool, shrink it to the simplest
mutation that still causes the failure. The minimal case is far more
informative for Coeus than the full complex task.
"""

import re
import logging

log = logging.getLogger("nemesis.shrink")


def _simplification_passes(prompt: str, candidates: list[str], correct: str
                           ) -> list[tuple[str, list[str], str, str]]:
    """Generate candidate simplifications of a task.

    Returns list of (new_prompt, new_candidates, new_correct, description).
    Each is a simpler version that should have the same correct answer.
    """
    simplifications = []

    # Remove parenthetical/aside clauses
    stripped = re.sub(r"\s*\([^)]*\)\s*", " ", prompt)
    if stripped != prompt:
        simplifications.append((stripped.strip(), candidates, correct, "remove_parentheticals"))

    # Remove "Note that..." / "Consider that..." / "Interestingly..." sentences
    stripped = re.sub(
        r"\s*(?:Note|Consider|Interestingly|Think|Remember|Importantly)[^.!?]*[.!?]",
        "", prompt, flags=re.IGNORECASE
    )
    if stripped.strip() != prompt.strip():
        simplifications.append((stripped.strip(), candidates, correct, "remove_distractors"))

    # Remove adjective clauses ("who is a teacher", "incidentally a baker")
    stripped = re.sub(r",?\s*(?:who|which|that)\s+(?:is|are|was|were)\s+[^,.)]+", "", prompt)
    if stripped.strip() != prompt.strip():
        simplifications.append((stripped.strip(), candidates, correct, "remove_adjective_clauses"))

    # Remove appositive phrases ("Alice, a teacher,")
    stripped = re.sub(r",\s*(?:a|an|the)\s+\w+(?:\s+\w+)?,", ",", prompt)
    if stripped.strip() != prompt.strip():
        simplifications.append((stripped.strip(), candidates, correct, "remove_appositives"))

    # Shorten transitivity chains (remove middle elements)
    comp_matches = list(re.finditer(
        r"(\w+)\s+is\s+(?:taller|larger|greater|heavier|older)\s+than\s+(\w+)",
        prompt, re.IGNORECASE
    ))
    if len(comp_matches) >= 3:
        # Remove the middle comparison
        mid = len(comp_matches) // 2
        m = comp_matches[mid]
        shortened = prompt[:m.start()].rstrip(". ,") + prompt[m.end():]
        shortened = re.sub(r"\.\s*\.", ".", shortened)
        simplifications.append((shortened.strip(), candidates, correct, "shorten_chain"))

    # Remove extra candidates (keep only correct + one wrong)
    if len(candidates) > 2:
        wrong = [c for c in candidates if c != correct]
        if wrong:
            minimal_cands = [correct, wrong[0]]
            simplifications.append((prompt, minimal_cands, correct, "reduce_candidates"))

    # Replace passive with active
    m = re.search(r"[Tt]he\s+(\w+)\s+was\s+(\w+)\s+by\s+the\s+(\w+)", prompt)
    if m:
        patient, verb, agent = m.group(1), m.group(2), m.group(3)
        active = f"The {agent} {verb} the {patient}"
        active_prompt = prompt[:m.start()] + active + prompt[m.end():]
        simplifications.append((active_prompt, candidates, correct, "passive_to_active"))

    return simplifications


def shrink(prompt: str, candidates: list[str], correct: str,
           tool_fn, max_rounds: int = 5) -> tuple[str, list[str], str, list[str]]:
    """Find the minimal failing case for a tool.

    Args:
        prompt: the adversarial prompt that broke the tool
        candidates: the candidate answers
        correct: the correct answer
        tool_fn: callable(prompt, candidates) -> top_candidate (the tool's answer)
        max_rounds: maximum simplification rounds

    Returns:
        (minimal_prompt, minimal_candidates, correct, simplifications_applied)
    """
    current_prompt = prompt
    current_candidates = list(candidates)
    applied = []

    for round_num in range(max_rounds):
        simplifications = _simplification_passes(current_prompt, current_candidates, correct)
        if not simplifications:
            break

        improved = False
        for new_prompt, new_cands, new_correct, desc in simplifications:
            # Check if the tool still fails on the simplified version
            try:
                top = tool_fn(new_prompt, new_cands)
                if top != new_correct:
                    # Still fails — accept the simplification
                    current_prompt = new_prompt
                    current_candidates = new_cands
                    applied.append(desc)
                    improved = True
                    log.debug("Shrink round %d: applied %s", round_num, desc)
                    break  # restart with the simpler version
            except Exception:
                continue  # simplification caused an error, skip it

        if not improved:
            break  # no simplification preserves the failure

    if applied:
        log.info("Shrunk task through %d simplifications: %s",
                 len(applied), " -> ".join(applied))

    return current_prompt, current_candidates, correct, applied
