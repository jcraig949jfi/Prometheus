"""
Building-block super-organism: analytic_number_theory.dirichlet_eta -> cmath.tanh
Discovered by M1 tournament (3 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbAnalyticNumberTheoryDirichletEtaCmathTanh(MathematicalOrganism):
    name = "bb_analytic_number_theory_dirichlet_eta__cmath_tanh"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['analytic_number_theory'].execute('dirichlet_eta', x)
    result = _bb_cache['cmath'].execute('tanh', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
