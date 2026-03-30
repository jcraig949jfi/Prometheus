"""
Building-block super-organism: numpy.randint -> signal_processing.autocorrelation
Discovered by M1 tournament (7 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbNumpyRandintSignalProcessingAutocorrelation(MathematicalOrganism):
    name = "bb_numpy_randint__signal_processing_autocorrelation"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['numpy'].execute('randint', x)
    result = _bb_cache['signal_processing'].execute('autocorrelation', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
