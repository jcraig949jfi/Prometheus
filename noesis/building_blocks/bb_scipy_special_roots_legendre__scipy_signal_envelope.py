"""
Building-block super-organism: scipy_special.roots_legendre -> scipy_signal.envelope
Discovered by M1 tournament (3 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbScipySpecialRootsLegendreScipySignalEnvelope(MathematicalOrganism):
    name = "bb_scipy_special_roots_legendre__scipy_signal_envelope"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['scipy_special'].execute('roots_legendre', x)
    result = _bb_cache['scipy_signal'].execute('envelope', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
