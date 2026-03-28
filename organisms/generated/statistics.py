"""Auto-generated organism wrapping 20 functions from statistics."""

import numpy as np
from organisms.base import MathematicalOrganism


class StatisticsOrganism(MathematicalOrganism):
    name = "statistics"
    operations = {
        "erf": {
            "code": "def erf(x):\n    import statistics\n    result = statistics.erf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "exp": {
            "code": "def exp(x):\n    import statistics\n    result = statistics.exp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "fabs": {
            "code": "def fabs(x):\n    import statistics\n    result = statistics.fabs(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "fmean": {
            "code": "def fmean(x):\n    import statistics\n    result = statistics.fmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "fsum": {
            "code": "def fsum(x):\n    import statistics\n    result = statistics.fsum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "geometric_mean": {
            "code": "def geometric_mean(x):\n    import statistics\n    result = statistics.geometric_mean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "harmonic_mean": {
            "code": "def harmonic_mean(x):\n    import statistics\n    result = statistics.harmonic_mean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mean": {
            "code": "def mean(x):\n    import statistics\n    result = statistics.mean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "median": {
            "code": "def median(x):\n    import statistics\n    result = statistics.median(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "median_grouped": {
            "code": "def median_grouped(x):\n    import statistics\n    result = statistics.median_grouped(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "median_high": {
            "code": "def median_high(x):\n    import statistics\n    result = statistics.median_high(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "median_low": {
            "code": "def median_low(x):\n    import statistics\n    result = statistics.median_low(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mode": {
            "code": "def mode(x):\n    import statistics\n    result = statistics.mode(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "multimode": {
            "code": "def multimode(x):\n    import statistics\n    result = statistics.multimode(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "pstdev": {
            "code": "def pstdev(x):\n    import statistics\n    result = statistics.pstdev(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "pvariance": {
            "code": "def pvariance(x):\n    import statistics\n    result = statistics.pvariance(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "quantiles": {
            "code": "def quantiles(x):\n    import statistics\n    result = statistics.quantiles(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "sqrt": {
            "code": "def sqrt(x):\n    import statistics\n    result = statistics.sqrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "stdev": {
            "code": "def stdev(x):\n    import statistics\n    result = statistics.stdev(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "variance": {
            "code": "def variance(x):\n    import statistics\n    result = statistics.variance(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
    }
