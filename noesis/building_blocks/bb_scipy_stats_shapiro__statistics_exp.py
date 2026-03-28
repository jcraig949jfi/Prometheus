"""
Building-block super-organism: scipy_stats.shapiro -> statistics.exp
Discovered by M1 tournament (4 appearances in high-quality chains).
"""

from organisms.base import MathematicalOrganism


class BbScipyStatsShapiroStatisticsExp(MathematicalOrganism):
    name = "bb_scipy_stats_shapiro__statistics_exp"
    operations = {
        "chain": {
            "code": """
_bb_cache = {}
def chain(x):
    if not _bb_cache:
        from organisms import ALL_ORGANISMS
        _bb_cache.update({cls().name: cls() for cls in ALL_ORGANISMS})
    result = _bb_cache['scipy_stats'].execute('shapiro', x)
    result = _bb_cache['statistics'].execute('exp', result)
    return result
""",
            "input_type": "any",
            "output_type": "any",
        },
    }
