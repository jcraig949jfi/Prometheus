"""
mutation.py — Mutation operators for whole-tool organisms.
"""

import random
import re
import copy
from compiler import extract_parameters, extract_methods, apply_parameter_mutation, swap_method


def point_mutate(genome, sigma: float = 0.1):
    """Gaussian perturbation on a random parameter in __init__."""
    g = genome.clone()
    params = extract_parameters(g.source_code)
    if not params:
        return g

    key = random.choice(list(params.keys()))
    old_val = params[key]
    new_val = old_val + random.gauss(0, sigma * max(abs(old_val), 0.01))
    new_val = round(new_val, 6)

    g.source_code = apply_parameter_mutation(g.source_code, key, old_val, new_val)
    g.parameters[key] = new_val
    g.lineage['mutations_applied'].append('point_mutate')
    return g


def drift(genome, sigma: float = 0.02):
    """Small Gaussian perturbation on ALL parameters."""
    g = genome.clone()
    params = extract_parameters(g.source_code)

    for key, old_val in params.items():
        new_val = old_val + random.gauss(0, sigma * max(abs(old_val), 0.01))
        new_val = round(new_val, 6)
        g.source_code = apply_parameter_mutation(g.source_code, key, old_val, new_val)
        g.parameters[key] = new_val

    g.lineage['mutations_applied'].append('drift')
    return g


def method_swap(genome, donor_population: list):
    """Swap a method from a random donor organism."""
    g = genome.clone()
    if not donor_population:
        return g

    donor = random.choice(donor_population)
    my_methods = extract_methods(g.source_code)
    donor_methods = extract_methods(donor.source_code)

    # Find methods that exist in both (excluding evaluate/confidence/__init__)
    swappable = [m for m in my_methods if m in donor_methods
                 and m not in ('evaluate', 'confidence', '__init__')]

    if not swappable:
        # Try swapping a scorer-like method
        my_private = [m for m in my_methods if m.startswith('_') and m != '__init__']
        donor_private = [m for m in donor_methods if m.startswith('_') and m != '__init__']
        if my_private and donor_private:
            target = random.choice(my_private)
            replacement = random.choice(donor_private)
            # Replace target method with donor's replacement method (renamed)
            old_src = my_methods[target]
            new_src = donor_methods[replacement]
            # Rename the replacement to match the target
            new_src = re.sub(
                rf'def\s+{re.escape(replacement)}\s*\(',
                f'def {target}(',
                new_src, count=1
            )
            g.source_code = g.source_code.replace(old_src, new_src)
            g.lineage['mutations_applied'].append(f'method_swap({replacement}->{target})')
            return g
        return g

    method = random.choice(swappable)
    g.source_code = swap_method(g.source_code, donor.source_code, method)
    g.lineage['mutations_applied'].append(f'method_swap({method})')
    return g


def crossover(parent_a, parent_b):
    """Single-point method crossover between two parents."""
    child = parent_a.clone()
    child.lineage['parent_ids'] = [parent_a.genome_id, parent_b.genome_id]
    child.lineage['mutations_applied'] = ['crossover']

    methods_a = extract_methods(parent_a.source_code)
    methods_b = extract_methods(parent_b.source_code)

    # Find common private methods
    common = [m for m in methods_a if m in methods_b
              and m not in ('evaluate', 'confidence', '__init__')]

    if not common:
        return child

    # Swap a random subset of methods from parent B
    n_swap = random.randint(1, max(1, len(common) // 2))
    to_swap = random.sample(common, min(n_swap, len(common)))

    for method in to_swap:
        child.source_code = swap_method(child.source_code, parent_b.source_code, method)

    return child


def mutate(genome, population: list, generation: int, config: dict,
           llm_mutator=None):
    """Apply graduated mutation schedule. Uses LLM when available."""
    g = genome.clone()
    g.lineage['parent_ids'] = [genome.genome_id]
    g.lineage['generation'] = generation
    g.lineage['mutations_applied'] = []

    rates = config.get('mutation_rates', {})
    params_only = generation < config.get('params_only_until_gen', 10)
    mild_structural = generation < config.get('mild_structural_until_gen', 30)

    # Always apply drift
    g = drift(g, config.get('drift_sigma', 0.02))

    # Point mutation (always available)
    if random.random() < rates.get('point_mutate', 0.4):
        g = point_mutate(g)

    if params_only:
        return g

    # Structural mutations — prefer LLM when available
    if random.random() < rates.get('splice', 0.25):
        if llm_mutator and llm_mutator.is_loaded and random.random() < 0.7:
            # LLM-assisted mutation
            donor = random.choice(population)
            try:
                new_source = llm_mutator.combine(g.source_code, donor.source_code)
                if new_source:
                    g.source_code = new_source
                    g.lineage['mutations_applied'].append('llm_combine')
                else:
                    g = method_swap(g, population)
            except Exception:
                g = method_swap(g, population)
        else:
            g = method_swap(g, population)

    # LLM refactor (occasional)
    if llm_mutator and llm_mutator.is_loaded and random.random() < 0.1:
        try:
            new_source = llm_mutator.refactor(g.source_code)
            if new_source:
                g.source_code = new_source
                g.lineage['mutations_applied'].append('llm_refactor')
        except Exception:
            pass

    return g
