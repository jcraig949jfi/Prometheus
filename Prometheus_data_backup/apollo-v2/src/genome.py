"""
genome.py — Genome representation for Apollo v2.

Organisms are primitive routing DAGs over 25 Frame H primitives.
Evolution searches routing strategies; primitives are fixed atoms.
"""

import uuid
import hashlib
import json
import copy
import random
import inspect
from dataclasses import dataclass, field
from typing import Any

# Flat catalog of all 25 Frame H primitives
PRIMITIVE_CATALOG = {
    "logic": ["solve_sat", "modus_ponens", "check_transitivity", "negate"],
    "probability": ["bayesian_update", "expected_value", "entropy", "coin_flip_independence"],
    "graph_causal": ["dag_traverse", "topological_sort", "counterfactual_intervention"],
    "constraints": ["solve_constraints", "pigeonhole_check", "fencepost_count"],
    "arithmetic": ["bat_and_ball", "modular_arithmetic", "all_but_n", "solve_linear_system"],
    "temporal": ["temporal_order", "direction_composition"],
    "belief_tracking": ["track_beliefs", "sally_anne_test"],
    "meta": ["confidence_from_agreement", "information_sufficiency", "parity_check"],
}

ALL_PRIMITIVES = []
PRIMITIVE_TO_CATEGORY = {}
for _cat, _names in PRIMITIVE_CATALOG.items():
    for _name in _names:
        ALL_PRIMITIVES.append(_name)
        PRIMITIVE_TO_CATEGORY[_name] = _cat

# Primitive function signatures (param names) — populated lazily
_PRIMITIVE_SIGNATURES: dict[str, list[str]] = {}


def get_primitive_signature(name: str) -> list[str]:
    """Return parameter names for a primitive function."""
    if not _PRIMITIVE_SIGNATURES:
        _load_signatures()
    return _PRIMITIVE_SIGNATURES.get(name, [])


def _load_signatures():
    """Load function signatures from forge_primitives module."""
    try:
        import sys
        from pathlib import Path
        primitives_dir = str(Path(__file__).parent.parent.parent / "agents" / "hephaestus" / "src")
        if primitives_dir not in sys.path:
            sys.path.insert(0, primitives_dir)
        import forge_primitives as fp
        for name in ALL_PRIMITIVES:
            fn = getattr(fp, name, None)
            if fn:
                sig = inspect.signature(fn)
                _PRIMITIVE_SIGNATURES[name] = list(sig.parameters.keys())
    except Exception as e:
        print(f"Warning: could not load primitive signatures: {e}")
        # Fallback: empty signatures
        for name in ALL_PRIMITIVES:
            _PRIMITIVE_SIGNATURES[name] = []


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PrimitiveCall:
    """One node in the routing DAG."""
    node_id: str                        # e.g. "n0", "n1"
    primitive_name: str                 # Must be in ALL_PRIMITIVES
    input_mapping: dict[str, str] = field(default_factory=dict)
    # Maps primitive param names to sources:
    #   "prompt"          — the task prompt string
    #   "candidates"      — the candidate list
    #   "n2.output"       — output of node n2
    #   "param.threshold"  — value from organism.parameters


@dataclass
class Lineage:
    parent_ids: list[str] = field(default_factory=list)
    mutations_applied: list[str] = field(default_factory=list)
    generation: int = 0


@dataclass
class Organism:
    genome_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    primitive_sequence: list[PrimitiveCall] = field(default_factory=list)
    wiring: dict[str, str] = field(default_factory=dict)
    # Maps "nX.output" -> "nY.param_name" for DAG edges beyond input_mapping
    parameters: dict[str, float] = field(default_factory=dict)
    router_logic: str = ""  # Python code body for def route(prompt, candidates, outputs, params)
    lineage: Lineage = field(default_factory=Lineage)

    @property
    def primitive_count(self) -> int:
        return len(self.primitive_sequence)

    @property
    def primitive_names(self) -> list[str]:
        return [pc.primitive_name for pc in self.primitive_sequence]

    @property
    def node_ids(self) -> list[str]:
        return [pc.node_id for pc in self.primitive_sequence]

    def wiring_hash(self) -> str:
        content = json.dumps({
            'seq': [(pc.node_id, pc.primitive_name) for pc in self.primitive_sequence],
            'wiring': self.wiring,
            'router': self.router_logic,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def clone(self) -> 'Organism':
        return Organism(
            genome_id=str(uuid.uuid4())[:12],
            primitive_sequence=[
                PrimitiveCall(
                    node_id=pc.node_id,
                    primitive_name=pc.primitive_name,
                    input_mapping=dict(pc.input_mapping),
                )
                for pc in self.primitive_sequence
            ],
            wiring=dict(self.wiring),
            parameters=dict(self.parameters),
            router_logic=self.router_logic,
            lineage=copy.deepcopy(self.lineage),
        )

    def get_node(self, node_id: str) -> PrimitiveCall | None:
        for pc in self.primitive_sequence:
            if pc.node_id == node_id:
                return pc
        return None

    def has_cycles(self) -> bool:
        """Check for cycles in the DAG via topological sort."""
        adj: dict[str, list[str]] = {pc.node_id: [] for pc in self.primitive_sequence}
        for pc in self.primitive_sequence:
            for source in pc.input_mapping.values():
                if source.startswith("n") and ".output" in source:
                    src_node = source.split(".")[0]
                    if src_node in adj:
                        adj[src_node].append(pc.node_id)

        # Kahn's algorithm
        in_degree = {nid: 0 for nid in adj}
        for nid, neighbors in adj.items():
            for nb in neighbors:
                in_degree[nb] = in_degree.get(nb, 0) + 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited = 0
        while queue:
            node = queue.pop(0)
            visited += 1
            for nb in adj.get(node, []):
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    queue.append(nb)

        return visited != len(adj)

    def topological_order(self) -> list[str]:
        """Return node_ids in topological order. Returns [] if cycle."""
        adj: dict[str, list[str]] = {pc.node_id: [] for pc in self.primitive_sequence}
        for pc in self.primitive_sequence:
            for source in pc.input_mapping.values():
                if source.startswith("n") and ".output" in source:
                    src_node = source.split(".")[0]
                    if src_node in adj:
                        adj[src_node].append(pc.node_id)

        in_degree = {nid: 0 for nid in adj}
        for nid, neighbors in adj.items():
            for nb in neighbors:
                in_degree[nb] = in_degree.get(nb, 0) + 1

        queue = sorted([nid for nid, deg in in_degree.items() if deg == 0])
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for nb in sorted(adj.get(node, [])):
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    queue.append(nb)

        return result if len(result) == len(adj) else []


# ---------------------------------------------------------------------------
# Seed population builders
# ---------------------------------------------------------------------------

# Default router logic templates for random organisms
_TRIVIAL_ROUTER = """\
# Score each candidate by averaging numeric outputs from the DAG
scores = []
for cand in candidates:
    score = 0.0
    count = 0
    for key, val in outputs.items():
        if isinstance(val, (int, float)):
            score += float(val)
            count += 1
        elif isinstance(val, bool):
            score += 1.0 if val else 0.0
            count += 1
    scores.append(score / max(count, 1))
return scores
"""

_COMPARISON_ROUTER = """\
# Use primitive outputs to score candidates by structural comparison
import re as _re
scores = []
for cand in candidates:
    # Extract numbers from candidate
    nums = [float(x) for x in _re.findall(r'-?\\d+\\.?\\d*', str(cand))]
    base = sum(float(v) for v in outputs.values() if isinstance(v, (int, float)))
    # Candidates with numbers closer to DAG output score higher
    if nums and base != 0:
        scores.append(1.0 / (1.0 + abs(nums[0] - base)))
    else:
        scores.append(0.5)
return scores
"""

_ROUTER_TEMPLATES = [_TRIVIAL_ROUTER, _COMPARISON_ROUTER]


def random_organism(min_primitives: int = 3, max_primitives: int = 8) -> Organism:
    """Create a random organism with linear DAG wiring and trivial router."""
    n_prims = random.randint(min_primitives, max_primitives)
    selected = random.sample(ALL_PRIMITIVES, min(n_prims, len(ALL_PRIMITIVES)))

    nodes = []
    for i, prim_name in enumerate(selected):
        node_id = f"n{i}"
        input_mapping = {}
        sig = get_primitive_signature(prim_name)

        for param in sig:
            # Wire inputs: first node gets prompt/candidates, others chain
            if i == 0:
                if param in ('prompt', 'statement', 'facts', 'agents'):
                    input_mapping[param] = "prompt"
                elif param in ('candidates',):
                    input_mapping[param] = "candidates"
                else:
                    # Use a random parameter
                    param_key = f"param.{prim_name}_{param}"
                    input_mapping[param] = param_key
            else:
                if param in ('prompt', 'statement'):
                    input_mapping[param] = "prompt"
                elif param in ('candidates',):
                    input_mapping[param] = "candidates"
                else:
                    # Chain from previous node or use parameter
                    if random.random() < 0.5 and i > 0:
                        input_mapping[param] = f"n{i-1}.output"
                    else:
                        param_key = f"param.{prim_name}_{param}"
                        input_mapping[param] = param_key

        nodes.append(PrimitiveCall(
            node_id=node_id,
            primitive_name=prim_name,
            input_mapping=input_mapping,
        ))

    # Generate default parameters for any param.* references
    parameters = {}
    for node in nodes:
        for source in node.input_mapping.values():
            if source.startswith("param."):
                param_name = source[6:]  # strip "param."
                parameters[param_name] = random.uniform(0.1, 2.0)

    # Build wiring dict from input_mappings
    wiring = {}
    for node in nodes:
        for param, source in node.input_mapping.items():
            if source.startswith("n") and ".output" in source:
                wiring[source] = f"{node.node_id}.{param}"

    router_logic = random.choice(_ROUTER_TEMPLATES)

    return Organism(
        primitive_sequence=nodes,
        wiring=wiring,
        parameters=parameters,
        router_logic=router_logic,
        lineage=Lineage(parent_ids=["random"], mutations_applied=["seed"]),
    )


def create_seed_population(pop_size: int = 50) -> list[Organism]:
    """Create seed population from random primitive compositions.

    Starts with random organisms. Legacy gem conversion can be added
    once the compiler is verified.
    """
    seeds = []
    for _ in range(pop_size):
        org = random_organism(min_primitives=3, max_primitives=8)
        if not org.has_cycles():
            seeds.append(org)
        else:
            # Retry once
            org = random_organism(min_primitives=3, max_primitives=5)
            seeds.append(org)

    return seeds[:pop_size]
