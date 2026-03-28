"""
Building-block super-organism: topology.euler_characteristic -> math.cos
Discovered by M1 tournament (4 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbTopologyEulerCharacteristicMathCos(MathematicalOrganism):
    name = "bb_topology_euler_characteristic__math_cos"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['topology'].execute('euler_characteristic', x)
    result = _bb_cache['math'].execute('cos', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
