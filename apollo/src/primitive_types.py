"""primitive_types.py — Type signatures for Frame H reasoning primitives.

2026-05-22 — added in response to baseline-matrix falsification at gen 2960.
The dominant elite recipe was `fencepost_count -> bayesian_update`, wiring
fencepost's integer output into bayesian_update's probability inputs. The
type mismatch was silent. This module makes such mismatches visible.

Each primitive has a typed signature: input param names with expected types,
plus an output type. Types are coarse semantic categories:

  - int             — integer (count, index, etc.)
  - float           — any real number
  - probability     — float in [0, 1]
  - bool            — boolean
  - str             — string (e.g., prompt fragment)
  - list_str        — list of strings (e.g., candidates)
  - list_num        — list of floats
  - graph           — adjacency-list / dict representation of a graph
  - dict_anything   — generic dict
  - any             — escape hatch when we don't know

Two types are "compatible" if equal, or both in the numeric family
{int, float, probability}, with `probability` being narrower than `float`.
A flow from float→probability is FLAGGED (potential range violation);
int→probability and float→int are also FLAGGED.
"""

from typing import Optional


# Coarse semantic types
_NUMERIC = {"int", "float", "probability"}
_STRING_LIKE = {"str", "prompt"}


# Hand-curated type registry for the 27 Frame H primitives.
# Format: primitive_name -> (param_types: dict[str, str], output_type: str)
PRIMITIVE_TYPES: dict[str, tuple[dict[str, str], str]] = {
    # Logic
    "solve_sat": ({"clauses": "any"}, "bool"),
    "modus_ponens": ({"premise": "bool", "implication": "bool"}, "bool"),
    "check_transitivity": ({"relations": "any"}, "bool"),
    "negate": ({"value": "bool"}, "bool"),

    # Probability
    "bayesian_update": ({"prior": "probability", "likelihood": "probability",
                         "false_positive": "probability"}, "probability"),
    "expected_value": ({"values": "list_num", "probabilities": "list_num"}, "float"),
    "entropy": ({"probabilities": "list_num"}, "float"),
    "coin_flip_independence": ({"n_flips": "int", "target_heads": "int"}, "probability"),

    # Graph/Causal
    "dag_traverse": ({"graph": "graph"}, "list_str"),
    "topological_sort": ({"graph": "graph"}, "list_str"),
    "counterfactual_intervention": ({"graph": "graph", "intervention": "any"}, "any"),

    # Constraints
    "solve_constraints": ({"constraints": "any"}, "any"),
    "pigeonhole_check": ({"items": "int", "boxes": "int"}, "bool"),
    "fencepost_count": ({"items": "int", "include_endpoints": "bool"}, "int"),

    # Arithmetic
    "bat_and_ball": ({"total": "float", "diff": "float"}, "float"),
    "modular_arithmetic": ({"a": "int", "b": "int", "modulus": "int"}, "int"),
    "all_but_n": ({"items": "int", "exception": "int"}, "int"),
    "solve_linear_system": ({"a": "any", "b": "any"}, "any"),

    # Temporal
    "temporal_order": ({"events": "any"}, "list_str"),
    "direction_composition": ({"sequence": "any"}, "str"),

    # Belief
    "track_beliefs": ({"beliefs": "any"}, "any"),
    "sally_anne_test": ({"scenario": "any"}, "str"),

    # Meta/Calibration
    "confidence_from_agreement": ({"agreements": "any"}, "probability"),
    "information_sufficiency": ({"evidence": "any"}, "bool"),
    "parity_check": ({"sequence": "any"}, "bool"),
}


def get_param_type(primitive_name: str, param_name: str) -> Optional[str]:
    """Return the declared type for one param of a primitive, or None if unknown."""
    entry = PRIMITIVE_TYPES.get(primitive_name)
    if not entry:
        return None
    param_types, _ = entry
    return param_types.get(param_name)


def get_output_type(primitive_name: str) -> Optional[str]:
    """Return the declared output type for a primitive, or None if unknown."""
    entry = PRIMITIVE_TYPES.get(primitive_name)
    if not entry:
        return None
    _, out = entry
    return out


def is_compatible(source_type: Optional[str], target_type: Optional[str]) -> bool:
    """True if source_type can be wired into target_type without semantic mismatch."""
    if source_type is None or target_type is None:
        return True  # unknown -> can't flag
    if source_type == target_type:
        return True
    if target_type == "any" or source_type == "any":
        return True
    # Numeric widening: int can go into float, probability can go into float
    if source_type in _NUMERIC and target_type == "float":
        return True
    if source_type in _STRING_LIKE and target_type == "str":
        return True
    # Hard mismatches:
    #  - int -> probability (range violation: integers outside [0,1])
    #  - float -> probability (range violation possible)
    #  - probability -> int (lossy truncation)
    #  - int -> bool (zero-equals-false is a hack)
    return False


def check_organism_wiring(organism) -> list[dict]:
    """Inspect an organism's wiring; return a list of type-mismatch warnings.

    Each warning is a dict with: node_id, param_name, source, source_type,
    target_type, severity.
    """
    warnings = []
    node_outputs = {}
    for pc in organism.primitive_sequence:
        out_type = get_output_type(pc.primitive_name)
        node_outputs[pc.node_id] = out_type

    for pc in organism.primitive_sequence:
        for param_name, source in pc.input_mapping.items():
            target_type = get_param_type(pc.primitive_name, param_name)
            source_type = None
            if isinstance(source, str):
                if source == "prompt":
                    source_type = "str"
                elif source == "candidates":
                    source_type = "list_str"
                elif "." in source and source.startswith("n"):
                    src_node = source.split(".")[0]
                    source_type = node_outputs.get(src_node)
                elif source.startswith("param."):
                    source_type = "float"

            if not is_compatible(source_type, target_type):
                warnings.append({
                    "node_id": pc.node_id,
                    "primitive": pc.primitive_name,
                    "param_name": param_name,
                    "source": source,
                    "source_type": source_type,
                    "target_type": target_type,
                    "severity": "warn",
                })
    return warnings
