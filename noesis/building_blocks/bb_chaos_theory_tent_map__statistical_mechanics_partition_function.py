"""
Building-block super-organism: chaos_theory.tent_map -> statistical_mechanics.partition_function
Discovered by M1 tournament (4 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbChaosTheoryTentMapStatisticalMechanicsPartitionFunction(MathematicalOrganism):
    name = "bb_chaos_theory_tent_map__statistical_mechanics_partition_function"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['chaos_theory'].execute('tent_map', x)
    result = _bb_cache['statistical_mechanics'].execute('partition_function', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
