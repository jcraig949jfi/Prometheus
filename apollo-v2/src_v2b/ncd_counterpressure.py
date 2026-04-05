"""
ncd_counterpressure.py — Prevent NCD takeover.

Three mechanisms:
1. Discrimination test at compilation: organism must differ from NCD on >= 3/10 tasks
2. Phased NCD decay: NCD baseline contribution decays over generations
3. Trace-based independence: track which primitive produced the output
"""

from fitness import NCDBaseline
from sandbox import safe_evaluate


def discrimination_test(source_code: str, reference_tasks: list[dict],
                        min_differ: int = 3, max_tasks: int = 10,
                        timeout: float = 0.5) -> bool:
    """At compilation time: organism must produce different outputs from NCD.

    Args:
        source_code: Compiled organism source
        reference_tasks: Tasks to test on
        min_differ: Minimum number of tasks where output must differ
        max_tasks: Maximum tasks to test (for speed)
        timeout: Per-task timeout

    Returns:
        True if organism passes (is NOT NCD-equivalent).
    """
    ncd = NCDBaseline()
    sample = reference_tasks[:max_tasks]
    differ_count = 0

    for task in sample:
        # NCD output
        ncd_results = ncd.evaluate(task['prompt'], task['candidates'])
        ncd_top = ncd_results[0]['candidate'] if ncd_results else ""

        # Organism output
        org_result = safe_evaluate(source_code, task['prompt'],
                                   task['candidates'], timeout)
        org_results = org_result.get('results', [])
        org_top = org_results[0]['candidate'] if org_results else ""

        if org_top != ncd_top:
            differ_count += 1

        # Early exit if already passing
        if differ_count >= min_differ:
            return True

    return differ_count >= min_differ


def ncd_decay_weight(generation: int) -> float:
    """Phased NCD baseline weight for margin computation.

    Gen 0-100:   1.0 (full NCD baseline subtracted)
    Gen 100-500: 0.5 (half credit for beating NCD)
    Gen 500+:    0.0 (raw accuracy, no NCD credit)

    This forces organisms to develop genuine accuracy over time,
    not just beat a weak baseline.
    """
    if generation <= 100:
        return 1.0
    elif generation <= 500:
        return 0.5
    else:
        return 0.0


def ncd_independence_score(task_results: list[dict]) -> float:
    """Compute NCD independence from task result traces.

    Checks gene_trace for NCD-like patterns. Returns 0-1 where
    1.0 = fully independent of NCD, 0.0 = pure NCD.
    """
    if not task_results:
        return 0.0

    n_tasks = len(task_results)
    n_ncd = 0

    for r in task_results:
        trace = str(r.get('gene_trace', '')).lower()
        # Check for NCD indicators in trace
        if 'ncd' in trace or 'zlib' in trace or 'compress' in trace:
            n_ncd += 1

    return 1.0 - (n_ncd / n_tasks) if n_tasks > 0 else 0.0
