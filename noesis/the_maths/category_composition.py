"""
Category Composition — Composable abstractions (category theory light)

Connects to: [representation_converters, invariant_extractors, constraint_feasibility, compression_metrics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "category_composition"
OPERATIONS = {}


def function_compose(x):
    """Compose two transformations: square then cumulative sum. Input: array. Output: array."""
    # Demonstrates composition: g(f(x)) where f=square, g=cumsum
    return np.cumsum(x ** 2)


OPERATIONS["function_compose"] = {
    "fn": function_compose,
    "input_type": "array",
    "output_type": "array",
    "description": "Compose square and cumulative sum as f;g"
}


def functor_map(x):
    """Apply a structure-preserving map: normalize then apply element-wise nonlinearity. Input: array. Output: array."""
    # Functor: maps objects (arrays) while preserving structure (ordering)
    normalized = (x - np.mean(x)) / (np.std(x) + 1e-10)
    return np.tanh(normalized)


OPERATIONS["functor_map"] = {
    "fn": functor_map,
    "input_type": "array",
    "output_type": "array",
    "description": "Structure-preserving map: normalize then tanh"
}


def product_construction(x):
    """Categorical product: pair each element with its index. Input: array. Output: matrix."""
    n = len(x)
    indices = np.arange(n, dtype=float)
    return np.column_stack([x, indices])


OPERATIONS["product_construction"] = {
    "fn": product_construction,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Product object: pair elements with indices (A x B)"
}


def coproduct_construction(x):
    """Categorical coproduct (disjoint union): interleave with tag bits. Input: array. Output: array."""
    n = len(x)
    # Split into two halves and tag each: [val, 0] for first half, [val, 1] for second
    h = n // 2
    first = x[:h]
    second = x[h:]
    tagged = np.zeros(2 * n)
    tagged[0:2 * h:2] = first
    tagged[1:2 * h:2] = 0  # tag for first component
    offset = 2 * h
    s = len(second)
    tagged[offset:offset + 2 * s:2] = second
    tagged[offset + 1:offset + 2 * s:2] = 1  # tag for second component
    return tagged[:2 * n]


OPERATIONS["coproduct_construction"] = {
    "fn": coproduct_construction,
    "input_type": "array",
    "output_type": "array",
    "description": "Coproduct (disjoint union) with tag bits"
}


def identity_morphism(x):
    """Identity morphism: returns input unchanged. Input: array. Output: array."""
    return x.copy()


OPERATIONS["identity_morphism"] = {
    "fn": identity_morphism,
    "input_type": "array",
    "output_type": "array",
    "description": "Identity morphism (id)"
}


def projection_first(x):
    """Project to first half (pi_1 of product). Input: array. Output: array."""
    return x[:len(x) // 2].copy()


OPERATIONS["projection_first"] = {
    "fn": projection_first,
    "input_type": "array",
    "output_type": "array",
    "description": "First projection from product (pi_1)"
}


def projection_second(x):
    """Project to second half (pi_2 of product). Input: array. Output: array."""
    return x[len(x) // 2:].copy()


OPERATIONS["projection_second"] = {
    "fn": projection_second,
    "input_type": "array",
    "output_type": "array",
    "description": "Second projection from product (pi_2)"
}


def diagonal_morphism(x):
    """Diagonal morphism: duplicate into product. Input: array. Output: array."""
    return np.concatenate([x, x])


OPERATIONS["diagonal_morphism"] = {
    "fn": diagonal_morphism,
    "input_type": "array",
    "output_type": "array",
    "description": "Diagonal morphism Delta: x -> (x, x)"
}


def constant_morphism(x, value=0.0):
    """Constant morphism: map everything to fixed value. Input: array. Output: array."""
    return np.full_like(x, value)


OPERATIONS["constant_morphism"] = {
    "fn": constant_morphism,
    "input_type": "array",
    "output_type": "array",
    "description": "Constant morphism mapping all elements to zero"
}


def natural_transformation_components(x):
    """Natural transformation between two functors (normalize vs. rank-transform). Input: array. Output: array."""
    # Functor F: normalize to [0,1]
    x_min, x_max = x.min(), x.max()
    if x_max == x_min:
        F_x = np.full_like(x, 0.5)
    else:
        F_x = (x - x_min) / (x_max - x_min)
    # Functor G: rank transform to [0,1]
    ranks = np.argsort(np.argsort(x)).astype(float)
    G_x = ranks / (len(x) - 1) if len(x) > 1 else ranks
    # Natural transformation component: the difference measures
    # how the two functors relate on this object
    return G_x - F_x


OPERATIONS["natural_transformation_components"] = {
    "fn": natural_transformation_components,
    "input_type": "array",
    "output_type": "array",
    "description": "Components of natural transformation between normalize and rank functors"
}


def monad_unit(x):
    """Monad unit (eta): embed value into computational context (wrap in singleton structure). Input: array. Output: array."""
    # Unit wraps: x -> [mean, std, len, x...]
    meta = np.array([np.mean(x), np.std(x), float(len(x))])
    return np.concatenate([meta, x])


OPERATIONS["monad_unit"] = {
    "fn": monad_unit,
    "input_type": "array",
    "output_type": "array",
    "description": "Monad unit: embed array into enriched context"
}


def monad_join(x):
    """Monad join (mu): flatten nested context. Input: array. Output: array."""
    # Assumes input was double-wrapped by monad_unit:
    # [meta1(3), meta2(3), data...]
    # Join flattens by extracting the inner data
    if len(x) > 6:
        inner_len = int(x[5]) if x[5] > 0 and x[5] < len(x) else len(x) - 6
        inner_len = min(inner_len, len(x) - 6)
        data = x[6:6 + int(inner_len)]
        meta = np.array([np.mean(data), np.std(data), float(len(data))])
        return np.concatenate([meta, data])
    # If not double-wrapped, just return normalized
    return x / (np.linalg.norm(x) + 1e-10)


OPERATIONS["monad_join"] = {
    "fn": monad_join,
    "input_type": "array",
    "output_type": "array",
    "description": "Monad join: flatten nested enriched context"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
