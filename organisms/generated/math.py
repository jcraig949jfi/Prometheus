"""Auto-generated organism wrapping 36 functions from math."""

import numpy as np
from organisms.base import MathematicalOrganism


class MathOrganism(MathematicalOrganism):
    name = "math"
    operations = {
        "acosh": {
            "code": "def acosh(x):\n    import math\n    result = math.acosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "asinh": {
            "code": "def asinh(x):\n    import math\n    result = math.asinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "atan": {
            "code": "def atan(x):\n    import math\n    result = math.atan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "cbrt": {
            "code": "def cbrt(x):\n    import math\n    result = math.cbrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "ceil": {
            "code": "def ceil(x):\n    import math\n    result = math.ceil(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "integer",
        },
        "cos": {
            "code": "def cos(x):\n    import math\n    result = math.cos(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "cosh": {
            "code": "def cosh(x):\n    import math\n    result = math.cosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "degrees": {
            "code": "def degrees(x):\n    import math\n    result = math.degrees(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "erf": {
            "code": "def erf(x):\n    import math\n    result = math.erf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "erfc": {
            "code": "def erfc(x):\n    import math\n    result = math.erfc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "exp": {
            "code": "def exp(x):\n    import math\n    result = math.exp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "exp2": {
            "code": "def exp2(x):\n    import math\n    result = math.exp2(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "expm1": {
            "code": "def expm1(x):\n    import math\n    result = math.expm1(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "fabs": {
            "code": "def fabs(x):\n    import math\n    result = math.fabs(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "floor": {
            "code": "def floor(x):\n    import math\n    result = math.floor(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "integer",
        },
        "frexp": {
            "code": "def frexp(x):\n    import math\n    result = math.frexp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "fsum": {
            "code": "def fsum(x):\n    import math\n    result = math.fsum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "gamma": {
            "code": "def gamma(x):\n    import math\n    result = math.gamma(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "isfinite": {
            "code": "def isfinite(x):\n    import math\n    result = math.isfinite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "isinf": {
            "code": "def isinf(x):\n    import math\n    result = math.isinf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "isnan": {
            "code": "def isnan(x):\n    import math\n    result = math.isnan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "lgamma": {
            "code": "def lgamma(x):\n    import math\n    result = math.lgamma(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "log10": {
            "code": "def log10(x):\n    import math\n    result = math.log10(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "log1p": {
            "code": "def log1p(x):\n    import math\n    result = math.log1p(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "log2": {
            "code": "def log2(x):\n    import math\n    result = math.log2(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "modf": {
            "code": "def modf(x):\n    import math\n    result = math.modf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "perm": {
            "code": "def perm(x):\n    import math\n    result = math.perm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "integer",
        },
        "prod": {
            "code": "def prod(x):\n    import math\n    result = math.prod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "radians": {
            "code": "def radians(x):\n    import math\n    result = math.radians(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sin": {
            "code": "def sin(x):\n    import math\n    result = math.sin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sinh": {
            "code": "def sinh(x):\n    import math\n    result = math.sinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sqrt": {
            "code": "def sqrt(x):\n    import math\n    result = math.sqrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "tan": {
            "code": "def tan(x):\n    import math\n    result = math.tan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "tanh": {
            "code": "def tanh(x):\n    import math\n    result = math.tanh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "trunc": {
            "code": "def trunc(x):\n    import math\n    result = math.trunc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "integer",
        },
        "ulp": {
            "code": "def ulp(x):\n    import math\n    result = math.ulp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
    }
