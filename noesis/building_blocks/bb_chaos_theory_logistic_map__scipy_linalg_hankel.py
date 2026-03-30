"""
Building-block super-organism: chaos_theory.logistic_map -> scipy_linalg.hankel
Discovered by M1 tournament (4 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbChaosTheoryLogisticMapScipyLinalgHankel(MathematicalOrganism):
    name = "bb_chaos_theory_logistic_map__scipy_linalg_hankel"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['chaos_theory'].execute('logistic_map', x)
    result = _bb_cache['scipy_linalg'].execute('hankel', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
