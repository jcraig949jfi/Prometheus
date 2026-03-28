"""
Building-block super-organism: topology.euler_characteristic -> probabilistic_number_theory.random_integer_gcd_probability
Discovered by M1 tournament (13 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbTopologyEulerCharacteristicProbabilisticNumberTheoryRandomIntegerGcdProbability(MathematicalOrganism):
    name = "bb_topology_euler_characteristic__probabilistic_number_theory_random_integer_gcd_probability"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['topology'].execute('euler_characteristic', x)
    result = _bb_cache['probabilistic_number_theory'].execute('random_integer_gcd_probability', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
