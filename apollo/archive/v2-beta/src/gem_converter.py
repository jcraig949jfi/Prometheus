"""
gem_converter.py — Convert existing Frame H gems into Apollo v2 Organisms.

Strategy: For each gem that imports forge_primitives, create an Organism where:
1. primitive_sequence = the primitives it imports (in order)
2. input_mapping = generic (prompt/candidates + chained outputs)
3. router_logic = extracted from the gem's scoring pattern, or a
   category-aware template based on which primitives are used
4. parameters = defaults for each primitive's inputs

This is seed-quality conversion. The organisms don't need to exactly
replicate the gem's behavior — they just need to start with the right
primitive palette. Evolution refines from there.
"""

import ast
import random
from pathlib import Path

from genome import (
    Organism, PrimitiveCall, Lineage, ALL_PRIMITIVES,
    get_primitive_signature, PRIMITIVE_TO_CATEGORY,
)


def convert_gem_to_organism(filepath: str) -> Organism | None:
    """Convert a gem file into an Organism.

    Extracts which primitives the gem imports from forge_primitives
    and builds a DAG with category-aware routing.
    """
    source = Path(filepath).read_text(encoding='utf-8')

    # Extract imported primitives via AST
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    primitives = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'forge_primitives':
            for alias in node.names:
                if alias.name in ALL_PRIMITIVES:
                    primitives.append(alias.name)

    if not primitives:
        return None

    # Deduplicate preserving order
    seen = set()
    unique_prims = []
    for p in primitives:
        if p not in seen:
            unique_prims.append(p)
            seen.add(p)

    # Cap at 10 primitives to avoid bloat (parsimony pressure will trim further)
    if len(unique_prims) > 10:
        # Keep diverse category coverage
        unique_prims = _select_diverse(unique_prims, 10)

    # Build DAG nodes
    nodes = []
    parameters = {}
    for i, prim_name in enumerate(unique_prims):
        node_id = f"n{i}"
        sig = get_primitive_signature(prim_name)
        input_mapping = _build_input_mapping(prim_name, sig, i, nodes, parameters)
        nodes.append(PrimitiveCall(
            node_id=node_id,
            primitive_name=prim_name,
            input_mapping=input_mapping,
        ))

    # Build wiring
    wiring = {}
    for node in nodes:
        for param, source_ref in node.input_mapping.items():
            if source_ref.startswith("n") and ".output" in source_ref:
                wiring[source_ref] = f"{node.node_id}.{param}"

    # Generate category-aware router logic
    categories = set(PRIMITIVE_TO_CATEGORY.get(p, 'unknown') for p in unique_prims)
    router_logic = _generate_router(unique_prims, categories)

    tool_name = Path(filepath).stem

    org = Organism(
        primitive_sequence=nodes,
        wiring=wiring,
        parameters=parameters,
        router_logic=router_logic,
        lineage=Lineage(
            parent_ids=[f"gem:{tool_name}"],
            mutations_applied=["gem_conversion"],
        ),
    )

    return org


def _select_diverse(primitives: list, max_count: int) -> list:
    """Select up to max_count primitives with maximum category diversity."""
    by_cat = {}
    for p in primitives:
        cat = PRIMITIVE_TO_CATEGORY.get(p, 'unknown')
        by_cat.setdefault(cat, []).append(p)

    selected = []
    # Round-robin across categories
    cats = list(by_cat.keys())
    idx = {cat: 0 for cat in cats}
    while len(selected) < max_count:
        added = False
        for cat in cats:
            if idx[cat] < len(by_cat[cat]) and len(selected) < max_count:
                selected.append(by_cat[cat][idx[cat]])
                idx[cat] += 1
                added = True
        if not added:
            break

    return selected


def _build_input_mapping(prim_name: str, sig: list[str], node_idx: int,
                         prior_nodes: list, parameters: dict) -> dict:
    """Build input mapping for a primitive based on its signature and position."""
    mapping = {}

    for param in sig:
        # Heuristic: wire based on param name semantics
        if param in ('prompt', 'statement'):
            mapping[param] = "prompt"
        elif param == 'candidates':
            mapping[param] = "candidates"
        elif param == 'facts':
            mapping[param] = "prompt"  # Will be parsed by primitive
        elif param == 'agents':
            mapping[param] = "prompt"
        elif param in ('edges', 'relations', 'premises', 'events',
                        'observations', 'clauses', 'directions'):
            # Structured inputs — chain from prior node if available, else default
            if node_idx > 0 and random.random() < 0.6:
                mapping[param] = f"n{node_idx - 1}.output"
            else:
                param_key = f"{prim_name}_{param}"
                mapping[param] = f"param.{param_key}"
                parameters[param_key] = 0.5
        elif param in ('prior', 'likelihood', 'false_positive'):
            param_key = f"{prim_name}_{param}"
            mapping[param] = f"param.{param_key}"
            parameters[param_key] = 0.5 if param == 'prior' else \
                                    0.7 if param == 'likelihood' else 0.1
        elif param in ('scores',):
            # Meta primitives — chain from earlier numeric outputs
            if node_idx > 0:
                mapping[param] = f"n{node_idx - 1}.output"
            else:
                mapping[param] = "param.default_scores"
                parameters['default_scores'] = 0.5
        elif param in ('total', 'difference', 'a', 'b', 'n', 'mod',
                        'n_flips', 'target_heads', 'items', 'containers',
                        'n_segments', 'n_unknowns', 'n_constraints',
                        'numbers'):
            param_key = f"{prim_name}_{param}"
            mapping[param] = f"param.{param_key}"
            # Sensible defaults
            defaults = {'total': 10.0, 'difference': 1.0, 'a': 0, 'b': 1,
                        'n': 2, 'mod': 10, 'n_flips': 3, 'target_heads': 1,
                        'items': 3, 'containers': 2, 'n_segments': 5,
                        'n_unknowns': 2, 'n_constraints': 2, 'numbers': 1}
            parameters[param_key] = defaults.get(param, 1.0)
        else:
            # Default: chain from prior node or use parameter
            if node_idx > 0 and random.random() < 0.4:
                mapping[param] = f"n{node_idx - 1}.output"
            else:
                param_key = f"{prim_name}_{param}"
                mapping[param] = f"param.{param_key}"
                parameters[param_key] = 0.5

    return mapping


def _generate_router(primitives: list, categories: set) -> str:
    """Generate category-aware router logic based on which primitives are available."""

    # Build node references for the router
    node_refs = ", ".join(f"'{p}': outputs.get('n{i}')"
                          for i, p in enumerate(primitives))

    if 'logic' in categories and 'probability' in categories:
        return _BAYESIAN_LOGIC_ROUTER.format(node_refs=node_refs, n=len(primitives))
    elif 'constraints' in categories:
        return _CONSTRAINT_ROUTER.format(node_refs=node_refs, n=len(primitives))
    elif 'belief_tracking' in categories:
        return _BELIEF_ROUTER.format(node_refs=node_refs, n=len(primitives))
    else:
        return _MULTI_SIGNAL_ROUTER.format(node_refs=node_refs, n=len(primitives))


# Router templates — each scores candidates using the available primitive outputs

_MULTI_SIGNAL_ROUTER = """\
# Multi-signal fusion: aggregate numeric outputs, penalize None
import re as _re
node_data = {{{node_refs}}}
scores = []
for cand in candidates:
    signal = 0.0
    weight = 0.0
    for name, val in node_data.items():
        if val is None:
            continue
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            signal += float(val)
            weight += 1.0
        elif isinstance(val, bool):
            signal += 1.0 if val else -0.5
            weight += 1.0
        elif isinstance(val, dict):
            signal += len(val) * 0.1
            weight += 1.0
        elif isinstance(val, (list, tuple)):
            signal += len(val) * 0.1
            weight += 1.0
        elif isinstance(val, set):
            signal += len(val) * 0.1
            weight += 1.0
        elif isinstance(val, str):
            # Check if candidate contains keywords from the output
            if val.lower() in cand.lower():
                signal += 2.0
            weight += 0.5
    # Candidate-specific: prefer shorter, more precise answers
    nums_in_cand = _re.findall(r'-?\\d+\\.?\\d*', str(cand))
    if nums_in_cand:
        signal += 0.5  # Bonus for numeric specificity
    scores.append(signal / max(weight, 1.0))
return scores
"""

_BAYESIAN_LOGIC_ROUTER = """\
# Bayesian-logic fusion: use probability outputs as priors, logic as filters
import re as _re
node_data = {{{node_refs}}}
scores = []
for cand in candidates:
    prob_signal = 0.0
    logic_signal = 0.0
    meta_signal = 0.0
    for name, val in node_data.items():
        if val is None:
            continue
        if isinstance(val, float) and 0.0 <= val <= 1.0:
            prob_signal += val
        elif isinstance(val, bool):
            logic_signal += 1.0 if val else -1.0
        elif isinstance(val, dict):
            logic_signal += 0.5
        elif isinstance(val, set):
            logic_signal += len(val) * 0.2
    combined = prob_signal * 0.6 + logic_signal * 0.3 + 0.1
    nums = _re.findall(r'-?\\d+\\.?\\d*', str(cand))
    if nums:
        combined += 0.3
    scores.append(combined)
return scores
"""

_CONSTRAINT_ROUTER = """\
# Constraint-driven: satisfaction signals dominate
import re as _re
node_data = {{{node_refs}}}
scores = []
for cand in candidates:
    sat_signal = 0.0
    other_signal = 0.0
    for name, val in node_data.items():
        if val is None:
            other_signal -= 0.5
            continue
        if isinstance(val, dict) and val:
            sat_signal += 1.0  # Constraint satisfied
        elif isinstance(val, bool):
            sat_signal += 1.0 if val else -0.5
        elif isinstance(val, (int, float)) and not isinstance(val, bool):
            other_signal += float(val) * 0.1
    scores.append(sat_signal + other_signal * 0.3)
return scores
"""

_BELIEF_ROUTER = """\
# Belief-tracking: perspective and theory-of-mind outputs drive scoring
import re as _re
node_data = {{{node_refs}}}
scores = []
for cand in candidates:
    belief_signal = 0.0
    other_signal = 0.0
    for name, val in node_data.items():
        if val is None:
            continue
        if isinstance(val, dict):
            # Check if candidate matches any belief
            for agent, belief in val.items():
                if isinstance(belief, str) and belief.lower() in cand.lower():
                    belief_signal += 2.0
                elif isinstance(belief, set):
                    for b in belief:
                        if str(b).lower() in cand.lower():
                            belief_signal += 1.0
        elif isinstance(val, (int, float)) and not isinstance(val, bool):
            other_signal += float(val) * 0.1
        elif isinstance(val, bool):
            other_signal += 0.5 if val else -0.3
    scores.append(belief_signal + other_signal)
return scores
"""


def load_gem_seeds(gem_dirs: list[str] = None, max_gems: int = 25) -> list[Organism]:
    """Load and convert gem files into seed organisms.

    Args:
        gem_dirs: List of glob patterns for gem files (must be provided by caller).
        max_gems: Maximum number of gems to convert.

    Returns:
        List of Organism seeds.
    """
    import glob

    if not gem_dirs:
        return []

    all_gems = []
    for pattern in gem_dirs:
        all_gems.extend(sorted(glob.glob(pattern)))

    converted = []
    for filepath in all_gems:
        if len(converted) >= max_gems:
            break
        org = convert_gem_to_organism(filepath)
        if org and not org.has_cycles():
            converted.append(org)

    return converted


def create_mixed_seed_population(pop_size: int = 50,
                                  gem_dirs: list[str] = None) -> list[Organism]:
    """Create seed population: gems + random organisms.

    Args:
        pop_size: Target population size.
        gem_dirs: Resolved glob patterns for gem files.
    """
    from genome import random_organism
    from logger import log_info

    gems = load_gem_seeds(gem_dirs=gem_dirs, max_gems=25)
    log_info(f"Converted {len(gems)} gems to organisms", stage="bootstrap")

    # Fill remaining with random organisms
    n_random = pop_size - len(gems)
    randoms = []
    for _ in range(n_random):
        org = random_organism(3, 8)
        if not org.has_cycles():
            randoms.append(org)

    log_info(f"Created {len(randoms)} random organisms", stage="bootstrap")

    population = gems + randoms
    random.shuffle(population)
    return population[:pop_size]
