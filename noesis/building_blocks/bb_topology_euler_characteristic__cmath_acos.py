"""
Building-block super-organism: topology.euler_characteristic -> cmath.acos
Discovered by M1 tournament (3 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbTopologyEulerCharacteristicCmathAcos(MathematicalOrganism):
    name = "bb_topology_euler_characteristic__cmath_acos"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['topology'].execute('euler_characteristic', x)
    result = _bb_cache['cmath'].execute('acos', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
