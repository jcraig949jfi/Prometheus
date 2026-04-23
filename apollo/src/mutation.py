"""
mutation.py — Four mutation operators for Organism DAGs.

1. Route mutation (40%): LLM modifies router_logic
2. Parameter mutation (25%): Gaussian noise on parameters (AST-only, no LLM)
3. Wiring mutation (20%): LLM rewires primitive connections
4. Primitive swap (15%): LLM replaces one primitive with a different one

v2c additions:
- mutate_batch(): batched mutation with AOS integration
- Groups LLM mutations by type and batches the prompts
"""

import random
import ast
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed

from genome import Organism, PrimitiveCall, Lineage, ALL_PRIMITIVES, get_primitive_signature
from logger import log_info, log_debug, log_warning


def mutate(organism: Organism, population: list, generation: int,
           config: dict, llm_mutator=None, annealing_tasks=None) -> Organism:
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

    is_structural = not (roll >= route_rate and roll < route_rate + param_rate)

    if is_structural and annealing_tasks:
        result = mutate_with_annealing(
            organism, population, generation, config,
            llm_mutator, annealing_tasks
        )
    elif roll < route_rate:
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
# Batch mutation (v2c)
# ---------------------------------------------------------------------------

def mutate_batch(organisms, population, generation, config,
                 llm_mutator=None, aos=None, annealing_tasks=None):
    """Batch mutation with AOS integration.

    Collects all organisms, determines mutation type (via AOS or fixed rates),
    groups LLM mutations by type, batches prompts, applies results.

    Args:
        organisms: list of Organism to mutate
        population: current population (for context)
        generation: current generation
        config: config dict
        llm_mutator: LLMMutator instance (with _generate_batch support)
        aos: AdaptiveOperatorSelector instance (optional)

    Returns:
        list of (mutated_child, operator_name) tuples
    """
    # During warmup, parameter-only
    if generation < config.get('params_only_until_gen', 50):
        results = []
        for org in organisms:
            child = parameter_mutation(org)
            child.lineage.generation = generation
            results.append((child, 'parameter'))
        return results

    rates = config.get('mutation_rates', {})
    route_rate = rates.get('route', 0.40)
    param_rate = rates.get('parameter', 0.25)
    wiring_rate = rates.get('wiring', 0.20)

    # Assign operator to each organism
    assignments = []  # (index, operator_name, organism)
    for i, org in enumerate(organisms):
        if aos is not None:
            op = aos.select()
        else:
            roll = random.random()
            if roll < route_rate:
                op = 'route'
            elif roll < route_rate + param_rate:
                op = 'parameter'
            elif roll < route_rate + param_rate + wiring_rate:
                op = 'wiring'
            else:
                op = 'swap'
        assignments.append((i, op, org))

    # Separate parameter mutations (no LLM needed)
    param_indices = [(i, org) for i, op, org in assignments if op == 'parameter']
    llm_groups = {}  # op -> [(i, org)]
    for i, op, org in assignments:
        if op != 'parameter':
            llm_groups.setdefault(op, []).append((i, org))

    results = [None] * len(organisms)

    # Handle parameter mutations inline
    for i, org in param_indices:
        child = parameter_mutation(org)
        child.lineage.generation = generation
        results[i] = (child, 'parameter')

    # Handle LLM mutations in batches
    if llm_mutator and llm_mutator.is_loaded:
        for op, items in llm_groups.items():
            if op == 'route':
                _batch_route_mutation(items, results, llm_mutator, generation)
            elif op == 'wiring':
                _batch_wiring_mutation(items, results, llm_mutator, generation)
            elif op == 'swap':
                _batch_swap_mutation(items, results, llm_mutator, generation)
            else:
                # Unknown op — fall back to parameter mutation
                for i, org in items:
                    child = parameter_mutation(org)
                    child.lineage.generation = generation
                    results[i] = (child, 'parameter')
    else:
        # No LLM available — fall back to parameter/random for all
        for op, items in llm_groups.items():
            for i, org in items:
                if op == 'route':
                    child = route_mutation(org, None)
                elif op == 'wiring':
                    child = wiring_mutation(org, None)
                elif op == 'swap':
                    child = primitive_swap_mutation(org, None)
                else:
                    child = parameter_mutation(org)
                child.lineage.generation = generation
                results[i] = (child, op)

    # Fill any None entries (shouldn't happen, but safety)
    for i in range(len(results)):
        if results[i] is None:
            child = parameter_mutation(organisms[i])
            child.lineage.generation = generation
            results[i] = (child, 'parameter')

    # Post-mutation annealing for structural mutations (parallel)
    if annealing_tasks:
        # Collect indices needing annealing
        anneal_indices = [i for i in range(len(results))
                          if results[i][1] != 'parameter']
        if anneal_indices:
            # ThreadPool (not Process) — annealing calls _quick_score which
            # already fans out to ProcessPoolExecutor internally.
            # max_workers=4 to avoid oversubscribing with nested parallelism.
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                for i in anneal_indices:
                    child, op_name = results[i]
                    fut = executor.submit(_anneal_child, child,
                                          annealing_tasks, generation)
                    futures[fut] = (i, op_name)
                for future in as_completed(futures):
                    i, op_name = futures[future]
                    try:
                        annealed = future.result()
                        results[i] = (annealed, op_name)
                    except Exception:
                        pass  # Keep original unannealed child

    # Log each mutation outcome
    for child, op_name in results:
        mutation_label = child.lineage.mutations_applied[-1] if child.lineage.mutations_applied else op_name
        log_debug(
            f"Mutation: {mutation_label} on {child.lineage.parent_ids[0][:8] if child.lineage.parent_ids else '?'} -> {child.genome_id[:8]}",
            stage="mutation", generation=generation,
            data={
                "parent_id": child.lineage.parent_ids[0] if child.lineage.parent_ids else None,
                "child_id": child.genome_id,
                "mutation_type": mutation_label,
                "child_primitives": child.primitive_count,
            }
        )

    return results


def _batch_route_mutation(items, results, llm_mutator, generation):
    """Batch route mutations via LLM."""
    prompts = []
    for i, org in items:
        node_info = ", ".join(
            f"{pc.node_id}={pc.primitive_name}" for pc in org.primitive_sequence
        )
        prompt = llm_mutator.mutate_route_prompt(
            org.router_logic, node_info, list(org.parameters.keys())
        )
        prompts.append(prompt)

    # Batch generate
    outputs = llm_mutator._generate_batch(prompts)

    for idx, ((i, org), output) in enumerate(zip(items, outputs)):
        child = org.clone()
        child.lineage.parent_ids = [org.genome_id]
        child.lineage.generation = generation

        code = llm_mutator._extract_code_body(output)
        if code and llm_mutator._validate_router_code(code):
            child.router_logic = code
            child.lineage.mutations_applied = ['route_mutation_llm_batch']
            log_debug(f"Batch route LLM success for {org.genome_id[:8]}", stage="mutation", generation=generation)
        else:
            # Fallback: parameter mutation
            child = parameter_mutation(org)
            child.lineage.mutations_applied = ['route_mutation_fallback']
            child.lineage.generation = generation
            log_debug(f"Batch route LLM fallback for {org.genome_id[:8]}", stage="mutation", generation=generation)

        results[i] = (child, 'route')


def _batch_wiring_mutation(items, results, llm_mutator, generation):
    """Batch wiring mutations via LLM."""
    prompts = []
    for i, org in items:
        org_desc = _organism_to_desc(org)
        prompt = llm_mutator.mutate_wiring_prompt(org_desc)
        prompts.append(prompt)

    outputs = llm_mutator._generate_batch(prompts)

    for idx, ((i, org), output) in enumerate(zip(items, outputs)):
        child = org.clone()
        child.lineage.parent_ids = [org.genome_id]
        child.lineage.generation = generation

        import re
        match = re.search(r'\{[^{}]+\}', output)
        if match:
            try:
                new_mappings = _parse_wiring_response(match.group(0), org)
                if new_mappings is not None:
                    child = _apply_wiring_change(child, new_mappings)
                    if not child.has_cycles():
                        child.lineage.mutations_applied = ['wiring_mutation_llm_batch']
                        results[i] = (child, 'wiring')
                        continue
            except Exception:
                pass

        # Fallback: random rewire
        child = _random_rewire(org)
        child.lineage.generation = generation
        results[i] = (child, 'wiring')


def _batch_swap_mutation(items, results, llm_mutator, generation):
    """Batch primitive swap mutations via LLM."""
    prompts = []
    swap_info = []  # (idx_in_sequence, old_prim)
    for i, org in items:
        if not org.primitive_sequence:
            swap_info.append((0, None))
            prompts.append("")
            continue
        node_idx = random.randint(0, len(org.primitive_sequence) - 1)
        old_node = org.primitive_sequence[node_idx]
        org_desc = _organism_to_desc(org)
        prompt = llm_mutator.swap_primitive_prompt(
            old_node.primitive_name, old_node.node_id, org_desc
        )
        prompts.append(prompt)
        swap_info.append((node_idx, old_node.primitive_name))

    # Filter out empty prompts
    non_empty = [(idx, p) for idx, p in enumerate(prompts) if p]
    if non_empty:
        batch_prompts = [p for _, p in non_empty]
        outputs = llm_mutator._generate_batch(batch_prompts)
        output_map = {}
        for (orig_idx, _), out in zip(non_empty, outputs):
            output_map[orig_idx] = out
    else:
        output_map = {}

    for idx, (i, org) in enumerate(items):
        child = org.clone()
        child.lineage.parent_ids = [org.genome_id]
        child.lineage.generation = generation

        node_idx, old_prim = swap_info[idx]
        if old_prim is None:
            results[i] = (child, 'swap')
            continue

        output = output_map.get(idx, "").strip()
        new_prim = None
        for prim in ALL_PRIMITIVES:
            if prim in output:
                new_prim = prim
                break

        if new_prim and new_prim != old_prim:
            child = _do_swap(child, node_idx, new_prim)
            child.lineage.mutations_applied = ['primitive_swap_llm_batch']
        else:
            # Fallback: random swap
            available = [p for p in ALL_PRIMITIVES if p != old_prim]
            new_prim = random.choice(available)
            child = _do_swap(child, node_idx, new_prim)
            child.lineage.mutations_applied = ['primitive_swap_random']

        child.lineage.generation = generation
        results[i] = (child, 'swap')


# ---------------------------------------------------------------------------
# Post-mutation parameter annealing
# ---------------------------------------------------------------------------

def mutate_with_annealing(organism, population, generation, config,
                          llm_mutator, annealing_tasks, n_rounds=10, sigma=0.15):
    """Structural LLM mutation + parameter annealing.

    After the LLM changes the structure, run n_rounds of parameter-only
    drift evaluated on easy tasks. This gives the new structure a fair
    chance to tune its parameters before competing.
    """
    from compiler import compile_organism

    # Step 1: Apply structural mutation (route, wiring, or swap — NOT parameter)
    rates = config.get('mutation_rates', {})
    route_rate = rates.get('route', 0.20)
    wiring_rate = rates.get('wiring', 0.35)
    # swap = remainder

    roll = random.random()
    if roll < route_rate:
        child = route_mutation(organism, llm_mutator)
    elif roll < route_rate + wiring_rate:
        child = wiring_mutation(organism, llm_mutator)
    else:
        child = primitive_swap_mutation(organism, llm_mutator)

    child.lineage.generation = generation

    # Step 2: Compile and check
    cr = compile_organism(child)
    if not cr.success:
        log_debug(f"Annealing: structural mutation failed compilation",
                  stage="mutation", generation=generation)
        return child  # Return uncompiled — caller will handle

    # Step 3: Anneal — run parameter drift rounds, keep best
    # Preserve original mutation history (e.g., 'route_mutation_llm_batch')
    original_mutations = list(child.lineage.mutations_applied)

    best_child = child
    best_source = cr.source_code
    best_score = _quick_score(best_source, annealing_tasks)

    for round_num in range(n_rounds):
        variant = parameter_mutation(best_child, sigma=sigma)
        var_cr = compile_organism(variant)
        if not var_cr.success:
            continue
        var_score = _quick_score(var_cr.source_code, annealing_tasks)
        if var_score > best_score:
            best_child = variant
            best_source = var_cr.source_code
            best_score = var_score

    # Restore original lineage + mark as annealed
    best_child.lineage.mutations_applied = original_mutations + ['annealed']
    log_debug(
        f"Annealing: {n_rounds} rounds, score {best_score:.3f}",
        stage="mutation", generation=generation,
        data={"annealing_rounds": n_rounds, "final_score": best_score,
              "mutation_type": original_mutations[0] if original_mutations else 'unknown'}
    )
    return best_child


def _anneal_child(child, annealing_tasks, generation, n_rounds=10, sigma=0.15):
    """Anneal an already-mutated child's parameters on easy tasks."""
    from compiler import compile_organism

    cr = compile_organism(child)
    if not cr.success:
        return child

    # Preserve original mutation history before annealing overwrites it
    original_mutations = list(child.lineage.mutations_applied)

    best_child = child
    best_source = cr.source_code
    best_score = _quick_score(best_source, annealing_tasks)

    for round_num in range(n_rounds):
        variant = parameter_mutation(best_child, sigma=sigma)
        var_cr = compile_organism(variant)
        if not var_cr.success:
            continue
        var_score = _quick_score(var_cr.source_code, annealing_tasks)
        if var_score > best_score:
            best_child = variant
            best_source = var_cr.source_code
            best_score = var_score

    # Restore original lineage + mark as annealed
    best_child.lineage.mutations_applied = original_mutations + ['annealed']
    best_child.lineage.generation = generation
    log_debug(
        f"Batch annealing: {n_rounds} rounds, score {best_score:.3f}",
        stage="mutation", generation=generation,
        data={"annealing_rounds": n_rounds, "final_score": best_score,
              "mutation_type": original_mutations[0] if original_mutations else 'unknown'}
    )
    return best_child


def _quick_score(source_code, tasks):
    """Quick accuracy on a small task set."""
    from sandbox import evaluate_organism_on_tasks
    try:
        results = evaluate_organism_on_tasks(source_code, tasks, timeout=0.5)
        if not results:
            return 0.0
        return sum(1 for r in results if r.get('correct', False)) / len(results)
    except Exception:
        return 0.0


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
            log_debug(f"Route mutation LLM success for {organism.genome_id[:8]}", stage="mutation")
            return child
        log_debug(f"Route mutation LLM fallback for {organism.genome_id[:8]}", stage="mutation")

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
                        return child
            except Exception:
                pass

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

    target_idx = random.randint(1, len(child.primitive_sequence) - 1)
    target_node = child.primitive_sequence[target_idx]

    if not target_node.input_mapping:
        return child

    param = random.choice(list(target_node.input_mapping.keys()))

    sources = ["prompt", "candidates"]
    for i in range(target_idx):
        sources.append(f"n{i}.output")
    for pk in child.parameters:
        sources.append(f"param.{pk}")

    target_node.input_mapping[param] = random.choice(sources)
    child.wiring = _rebuild_wiring(child)

    if child.has_cycles():
        return organism.clone()

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
            return child

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

    new_mapping = {}
    old_mapping = old_node.input_mapping

    for param in new_sig:
        if param in old_mapping:
            new_mapping[param] = old_mapping[param]
        else:
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

    cut_a = random.randint(1, max(1, len(parent_a.primitive_sequence) - 1))
    cut_b = random.randint(1, max(1, len(parent_b.primitive_sequence) - 1))

    prefix = parent_a.primitive_sequence[:cut_a]
    suffix = parent_b.primitive_sequence[cut_b:]

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
            if source.startswith("n") and ".output" in source:
                src_idx = int(source.split(".")[0][1:])
                if src_idx >= cut_b:
                    new_src_idx = src_idx - cut_b + len(prefix)
                    new_mapping[param] = f"n{new_src_idx}.output"
                elif src_idx < cut_a:
                    new_mapping[param] = source
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
    child.parameters = dict(parent_a.parameters)
    child.parameters.update(parent_b.parameters)
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
    """Parse LLM wiring mutation response."""
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
