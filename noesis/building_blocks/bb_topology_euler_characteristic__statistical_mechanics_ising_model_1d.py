"""
Building-block super-organism: topology.euler_characteristic -> statistical_mechanics.ising_model_1d
Discovered by M1 tournament (13 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbTopologyEulerCharacteristicStatisticalMechanicsIsingModel1d(MathematicalOrganism):
    name = "bb_topology_euler_characteristic__statistical_mechanics_ising_model_1d"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['topology'].execute('euler_characteristic', x)
    result = _bb_cache['statistical_mechanics'].execute('ising_model_1d', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
