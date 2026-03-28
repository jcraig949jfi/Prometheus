"""
Building-block super-organism: numpy.chisquare -> immune_systems.danger_signal
Discovered by M1 tournament (5 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbNumpyChisquareImmuneSystemsDangerSignal(MathematicalOrganism):
    name = "bb_numpy_chisquare__immune_systems_danger_signal"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['numpy'].execute('chisquare', x)
    result = _bb_cache['immune_systems'].execute('danger_signal', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
