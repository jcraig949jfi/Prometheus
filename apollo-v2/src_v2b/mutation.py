"""
mutation.py — Four mutation operators for Organism DAGs.

1. Route mutation (40%): LLM modifies router_logic
2. Parameter mutation (25%): Gaussian noise on parameters (AST-only, no LLM)
3. Wiring mutation (20%): LLM rewires primitive connections
4. Primitive swap (15%): LLM replaces one primitive with a different one
"""

import random
import ast
import copy

from genome import Organism, PrimitiveCall, Lineage, ALL_PRIMITIVES, get_primitive_signature
from logger import log_info, log_debug, log_warning


def mutate(organism: Organism, population: list, generation: int,
           config: dict, llm_mutator=None) -> Organism:
    """Apply one mutation operator based on configured weights."""
    roll = random.random()
    rates = config.get('mutation_rates', {})
    route_rate = rates.get('route', 0.40)
    param_rate = rates.get('parameter', 0.25)
    wiring_rate = rates.get('wiring', 0.20)
    # swap = remainder

    # During warmup, parameter-only
    if generation < config.get('params_only_until_gen', 50):
        return parameter_mutation(organism)

    if roll < route_rate:
        result = route_mutation(organism, llm_mutator)
    elif roll < route_rate + param_rate:
        result = parameter_mutation(organism)
    elif roll < route_rate + param_rate + wiring_rate:
        result = wiring_mutation(organism, llm_mutator)
    else:
        result = primitive_swap_mutation(organism, llm_mutator)

    result.lineage.generation = generation
    log_debug(
        f"Mutation: {result.lineage.mutations_applied[-1]} on {organism.genome_id[:8]} -> {result.genome_id[:8]}",
        stage="mutation", generation=generation,
        data={
            "parent_id": organism.genome_id,
            "child_id": result.genome_id,
            "mutation_type": result.lineage.mutations_applied[-1],
            "parent_primitives": organism.primitive_count,
            "child_primitives": result.primitive_count,
        }
    )
    return result


# ---------------------------------------------------------------------------
# 1. Parameter mutation (AST-only, always safe)
# ---------------------------------------------------------------------------

def parameter_mutation(organism: Organism, sigma: float = 0.1) -> Organism:
    """Gaussian perturbation on random parameters."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['parameter_mutation']

    if not child.parameters:
        return child

    # Mutate 1-3 parameters
    n_mutate = min(random.randint(1, 3), len(child.parameters))
    keys = random.sample(list(child.parameters.keys()), n_mutate)

    for key in keys:
        old_val = child.parameters[key]
        noise = random.gauss(0, sigma * max(abs(old_val), 0.01))
        new_val = old_val + noise
        # Clamp to reasonable range
        new_val = max(-10.0, min(10.0, new_val))
        child.parameters[key] = round(new_val, 6)

    return child


def drift(organism: Organism, sigma: float = 0.02) -> Organism:
    """Small Gaussian perturbation on ALL parameters."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['drift']

    for key, old_val in child.parameters.items():
        noise = random.gauss(0, sigma * max(abs(old_val), 0.01))
        child.parameters[key] = round(old_val + noise, 6)

    return child


# ---------------------------------------------------------------------------
# 2. Route mutation (LLM-assisted)
# ---------------------------------------------------------------------------

def route_mutation(organism: Organism, llm_mutator=None) -> Organism:
    """Modify the router_logic code. Uses LLM if available, else random tweak."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['route_mutation']

    if llm_mutator and llm_mutator.is_loaded:
        node_info = ", ".join(
            f"{pc.node_id}={pc.primitive_name}" for pc in organism.primitive_sequence
        )
        new_router = llm_mutator.mutate_route(
            organism.router_logic, node_info, list(organism.parameters.keys())
        )
        if new_router and _validate_router(new_router):
            child.router_logic = new_router
            child.lineage.mutations_applied = ['route_mutation_llm']
            log_debug(f"LLM route_mutation succeeded", stage="mutation",
                      data={"parent_id": organism.genome_id, "mutation_type": "route_mutation_llm"})
            return child
        else:
            log_debug(f"LLM route_mutation failed, falling back to AST", stage="mutation")

    # Fallback: random parameter injection into router
    child = parameter_mutation(organism)
    child.lineage.mutations_applied = ['route_mutation_fallback']
    return child


# ---------------------------------------------------------------------------
# 3. Wiring mutation (LLM-assisted)
# ---------------------------------------------------------------------------

def wiring_mutation(organism: Organism, llm_mutator=None) -> Organism:
    """Rewire one connection between primitives."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['wiring_mutation']

    if llm_mutator and llm_mutator.is_loaded:
        import json
        org_desc = _organism_to_desc(organism)
        new_wiring_json = llm_mutator.mutate_wiring(org_desc)
        if new_wiring_json:
            try:
                new_mappings = _parse_wiring_response(new_wiring_json, organism)
                if new_mappings is not None:
                    child = _apply_wiring_change(child, new_mappings)
                    if not child.has_cycles():
                        child.lineage.mutations_applied = ['wiring_mutation_llm']
                        log_debug(f"LLM wiring_mutation succeeded", stage="mutation",
                                  data={"parent_id": organism.genome_id, "mutation_type": "wiring_mutation_llm"})
                        return child
            except Exception:
                pass

        log_debug(f"LLM wiring_mutation failed, falling back to AST", stage="mutation")

    # Fallback: random rewire
    child = _random_rewire(organism)
    return child


def _random_rewire(organism: Organism) -> Organism:
    """Randomly change one input mapping to point to a different node."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['wiring_mutation_random']

    if len(child.primitive_sequence) < 2:
        return child

    # Pick a random non-first node
    target_idx = random.randint(1, len(child.primitive_sequence) - 1)
    target_node = child.primitive_sequence[target_idx]

    if not target_node.input_mapping:
        return child

    # Pick a random input to rewire
    param = random.choice(list(target_node.input_mapping.keys()))

    # Available sources: earlier nodes, prompt, candidates, params
    sources = ["prompt", "candidates"]
    for i in range(target_idx):
        sources.append(f"n{i}.output")
    for pk in child.parameters:
        sources.append(f"param.{pk}")

    target_node.input_mapping[param] = random.choice(sources)

    # Update wiring dict
    child.wiring = _rebuild_wiring(child)

    if child.has_cycles():
        return organism.clone()  # Revert if cycle introduced

    return child


# ---------------------------------------------------------------------------
# 4. Primitive swap (LLM-assisted)
# ---------------------------------------------------------------------------

def primitive_swap_mutation(organism: Organism, llm_mutator=None) -> Organism:
    """Replace one primitive with a different one."""
    child = organism.clone()
    child.lineage.parent_ids = [organism.genome_id]
    child.lineage.mutations_applied = ['primitive_swap']

    if not child.primitive_sequence:
        return child

    # Pick a random node to swap
    idx = random.randint(0, len(child.primitive_sequence) - 1)
    old_node = child.primitive_sequence[idx]
    old_prim = old_node.primitive_name

    if llm_mutator and llm_mutator.is_loaded:
        node_context = _organism_to_desc(organism)
        new_prim = llm_mutator.swap_primitive(
            old_prim, old_node.node_id, node_context
        )
        if new_prim and new_prim in ALL_PRIMITIVES and new_prim != old_prim:
            child = _do_swap(child, idx, new_prim)
            child.lineage.mutations_applied = ['primitive_swap_llm']
            log_debug(f"LLM primitive_swap succeeded", stage="mutation",
                      data={"parent_id": organism.genome_id, "mutation_type": "primitive_swap_llm",
                            "old_primitive": old_prim, "new_primitive": new_prim})
            return child
        else:
            log_debug(f"LLM primitive_swap failed, falling back to AST", stage="mutation")

    # Fallback: random swap
    available = [p for p in ALL_PRIMITIVES if p != old_prim]
    new_prim = random.choice(available)
    child = _do_swap(child, idx, new_prim)
    child.lineage.mutations_applied = ['primitive_swap_random']
    return child


def _do_swap(organism: Organism, node_idx: int, new_prim: str) -> Organism:
    """Swap the primitive at node_idx, rebuilding input mapping for new signature."""
    child = organism.clone()
    old_node = child.primitive_sequence[node_idx]
    new_sig = get_primitive_signature(new_prim)

    # Build new input mapping
    new_mapping = {}
    old_mapping = old_node.input_mapping

    for param in new_sig:
        if param in old_mapping:
            # Same param name exists — keep the wiring
            new_mapping[param] = old_mapping[param]
        else:
            # New param — wire to prompt, candidates, or a default parameter
            if param in ('prompt', 'statement', 'facts'):
                new_mapping[param] = "prompt"
            elif param in ('candidates',):
                new_mapping[param] = "candidates"
            elif node_idx > 0 and random.random() < 0.5:
                new_mapping[param] = f"n{node_idx - 1}.output"
            else:
                param_key = f"{new_prim}_{param}"
                new_mapping[param] = f"param.{param_key}"
                child.parameters[param_key] = random.uniform(0.1, 2.0)

    child.primitive_sequence[node_idx] = PrimitiveCall(
        node_id=old_node.node_id,
        primitive_name=new_prim,
        input_mapping=new_mapping,
    )

    child.wiring = _rebuild_wiring(child)
    return child


# ---------------------------------------------------------------------------
# Crossover
# ---------------------------------------------------------------------------

def crossover(parent_a: Organism, parent_b: Organism) -> Organism:
    """Single-point crossover: take prefix from A, suffix from B."""
    child = parent_a.clone()
    child.lineage.parent_ids = [parent_a.genome_id, parent_b.genome_id]
    child.lineage.mutations_applied = ['crossover']

    if not parent_b.primitive_sequence:
        return child

    # Crossover point
    cut_a = random.randint(1, max(1, len(parent_a.primitive_sequence) - 1))
    cut_b = random.randint(1, max(1, len(parent_b.primitive_sequence) - 1))

    # Take first cut_a nodes from A, remaining from B
    prefix = parent_a.primitive_sequence[:cut_a]
    suffix = parent_b.primitive_sequence[cut_b:]

    # Renumber suffix nodes to avoid collisions
    new_nodes = []
    for pc in prefix:
        new_nodes.append(PrimitiveCall(
            node_id=pc.node_id,
            primitive_name=pc.primitive_name,
            input_mapping=dict(pc.input_mapping),
        ))

    for i, pc in enumerate(suffix):
        new_id = f"n{len(prefix) + i}"
        new_mapping = {}
        for param, source in pc.input_mapping.items():
            # Fix references to point to valid nodes
            if source.startswith("n") and ".output" in source:
                src_idx = int(source.split(".")[0][1:])
                if src_idx >= cut_b:
                    new_src_idx = src_idx - cut_b + len(prefix)
                    new_mapping[param] = f"n{new_src_idx}.output"
                elif src_idx < cut_a:
                    new_mapping[param] = source  # Points to prefix node
                else:
                    new_mapping[param] = f"n{len(prefix) - 1}.output"
            else:
                new_mapping[param] = source

        new_nodes.append(PrimitiveCall(
            node_id=new_id,
            primitive_name=pc.primitive_name,
            input_mapping=new_mapping,
        ))

    child.primitive_sequence = new_nodes

    # Merge parameters from both parents
    child.parameters = dict(parent_a.parameters)
    child.parameters.update(parent_b.parameters)

    # Use parent A's router (could also be crossover point)
    child.router_logic = parent_a.router_logic

    child.wiring = _rebuild_wiring(child)

    if child.has_cycles():
        return parent_a.clone()

    return child


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_router(router_code: str) -> bool:
    """Check if router code is valid Python."""
    try:
        test = f"def _route(prompt, candidates, outputs, params):\n"
        for line in router_code.strip().split('\n'):
            test += f"    {line}\n"
        ast.parse(test)
        return True
    except SyntaxError:
        return False


def _organism_to_desc(organism: Organism) -> str:
    """Create a text description of an organism for LLM prompts."""
    lines = []
    lines.append("Primitive DAG:")
    for pc in organism.primitive_sequence:
        sig = get_primitive_signature(pc.primitive_name)
        inputs = ", ".join(f"{k}={v}" for k, v in pc.input_mapping.items())
        lines.append(f"  {pc.node_id}: {pc.primitive_name}({inputs})")
    lines.append(f"Parameters: {list(organism.parameters.keys())}")
    lines.append(f"Router logic:\n{organism.router_logic}")
    return "\n".join(lines)


def _rebuild_wiring(organism: Organism) -> dict:
    """Rebuild wiring dict from input_mappings."""
    wiring = {}
    for pc in organism.primitive_sequence:
        for param, source in pc.input_mapping.items():
            if source.startswith("n") and ".output" in source:
                wiring[source] = f"{pc.node_id}.{param}"
    return wiring


def _parse_wiring_response(response: str, organism: Organism) -> dict | None:
    """Parse LLM wiring mutation response. Returns new input_mapping updates or None."""
    try:
        import json
        data = json.loads(response)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def _apply_wiring_change(organism: Organism, new_mappings: dict) -> Organism:
    """Apply wiring changes from LLM response."""
    child = organism.clone()
    for node_id, mappings in new_mappings.items():
        node = child.get_node(node_id)
        if node and isinstance(mappings, dict):
            for param, source in mappings.items():
                node.input_mapping[param] = source
    child.wiring = _rebuild_wiring(child)
    return child
