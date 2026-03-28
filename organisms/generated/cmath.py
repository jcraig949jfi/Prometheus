"""Auto-generated organism wrapping 20 functions from cmath."""

import numpy as np
from organisms.base import MathematicalOrganism


class CmathOrganism(MathematicalOrganism):
    name = "cmath"
    operations = {
        "acos": {
            "code": "def acos(x):\n    import cmath\n    result = cmath.acos(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "acosh": {
            "code": "def acosh(x):\n    import cmath\n    result = cmath.acosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "asin": {
            "code": "def asin(x):\n    import cmath\n    result = cmath.asin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "asinh": {
            "code": "def asinh(x):\n    import cmath\n    result = cmath.asinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "atan": {
            "code": "def atan(x):\n    import cmath\n    result = cmath.atan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "atanh": {
            "code": "def atanh(x):\n    import cmath\n    result = cmath.atanh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "cos": {
            "code": "def cos(x):\n    import cmath\n    result = cmath.cos(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "cosh": {
            "code": "def cosh(x):\n    import cmath\n    result = cmath.cosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "exp": {
            "code": "def exp(x):\n    import cmath\n    result = cmath.exp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "isfinite": {
            "code": "def isfinite(x):\n    import cmath\n    result = cmath.isfinite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "isinf": {
            "code": "def isinf(x):\n    import cmath\n    result = cmath.isinf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "isnan": {
            "code": "def isnan(x):\n    import cmath\n    result = cmath.isnan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "log10": {
            "code": "def log10(x):\n    import cmath\n    result = cmath.log10(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "phase": {
            "code": "def phase(x):\n    import cmath\n    result = cmath.phase(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "polar": {
            "code": "def polar(x):\n    import cmath\n    result = cmath.polar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sin": {
            "code": "def sin(x):\n    import cmath\n    result = cmath.sin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "sinh": {
            "code": "def sinh(x):\n    import cmath\n    result = cmath.sinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "sqrt": {
            "code": "def sqrt(x):\n    import cmath\n    result = cmath.sqrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "matrix",
        },
        "tan": {
            "code": "def tan(x):\n    import cmath\n    result = cmath.tan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "tanh": {
            "code": "def tanh(x):\n    import cmath\n    result = cmath.tanh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
    }
