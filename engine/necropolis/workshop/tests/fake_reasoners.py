"""NECROPOLIS VALIDATION: adversarial reasoners fed to the grading oracle.

Each is a candidate under the oracle's own contract (callable probe -> (answer,
trace)).  None reasons.  They exist to measure the oracle, not to pass it.
"""


def constant(p):
    return "0", {"operations_used": ["constant"]}


def constant_string_trace(p):
    """CORRUPT_INPUT: a candidate that violates the trace contract (str, not dict)."""
    return "0", "constant"


def crash(p):
    raise RuntimeError("deliberate crash")


def gt_reader(p):
    """CHEAT: return whatever ground truth the probe object carries."""
    gt = getattr(p, "ground_truth", None)
    if gt is None and isinstance(p, dict):
        gt = p.get("ground_truth")
    return gt, {"operations_used": ["read probe.ground_truth"]}


def r6_truth_reader(p):
    """CHEAT: the R6 probe ships `truth` inside its data payload."""
    data = getattr(p, "data", None) or (p.get("data") if isinstance(p, dict) else None) or {}
    return (data.get("truth") if isinstance(data, dict) else None), {"operations_used": ["read probe.data.truth"]}
