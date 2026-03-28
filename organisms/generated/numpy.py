"""Auto-generated organism wrapping 203 functions from numpy."""

import numpy as np
from organisms.base import MathematicalOrganism


class NumpyOrganism(MathematicalOrganism):
    name = "numpy"
    operations = {
        "abs": {
            "code": "def abs(x):\n    import numpy\n    result = numpy.abs(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "absolute": {
            "code": "def absolute(x):\n    import numpy\n    result = numpy.absolute(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "acosh": {
            "code": "def acosh(x):\n    import numpy\n    result = numpy.acosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "all": {
            "code": "def all(x):\n    import numpy\n    result = numpy.all(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "amax": {
            "code": "def amax(x):\n    import numpy\n    result = numpy.amax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "amin": {
            "code": "def amin(x):\n    import numpy\n    result = numpy.amin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "angle": {
            "code": "def angle(x):\n    import numpy\n    result = numpy.angle(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "any": {
            "code": "def any(x):\n    import numpy\n    result = numpy.any(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "arange": {
            "code": "def arange(x):\n    import numpy\n    result = numpy.arange(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "arccosh": {
            "code": "def arccosh(x):\n    import numpy\n    result = numpy.arccosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "arcsinh": {
            "code": "def arcsinh(x):\n    import numpy\n    result = numpy.arcsinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "arctan": {
            "code": "def arctan(x):\n    import numpy\n    result = numpy.arctan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "argmax": {
            "code": "def argmax(x):\n    import numpy\n    result = numpy.argmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "argmin": {
            "code": "def argmin(x):\n    import numpy\n    result = numpy.argmin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "argsort": {
            "code": "def argsort(x):\n    import numpy\n    result = numpy.argsort(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "argwhere": {
            "code": "def argwhere(x):\n    import numpy\n    result = numpy.argwhere(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "around": {
            "code": "def around(x):\n    import numpy\n    result = numpy.around(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "asarray_chkfinite": {
            "code": "def asarray_chkfinite(x):\n    import numpy\n    result = numpy.asarray_chkfinite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "asinh": {
            "code": "def asinh(x):\n    import numpy\n    result = numpy.asinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "atan": {
            "code": "def atan(x):\n    import numpy\n    result = numpy.atan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "average": {
            "code": "def average(x):\n    import numpy\n    result = numpy.average(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "bartlett": {
            "code": "def bartlett(x):\n    import numpy\n    result = numpy.bartlett(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "blackman": {
            "code": "def blackman(x):\n    import numpy\n    result = numpy.blackman(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "cbrt": {
            "code": "def cbrt(x):\n    import numpy\n    result = numpy.cbrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ceil": {
            "code": "def ceil(x):\n    import numpy\n    result = numpy.ceil(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "clip": {
            "code": "def clip(x):\n    import numpy\n    result = numpy.clip(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "column_stack": {
            "code": "def column_stack(x):\n    import numpy\n    result = numpy.column_stack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "conj": {
            "code": "def conj(x):\n    import numpy\n    result = numpy.conj(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "conjugate": {
            "code": "def conjugate(x):\n    import numpy\n    result = numpy.conjugate(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "corrcoef": {
            "code": "def corrcoef(x):\n    import numpy\n    result = numpy.corrcoef(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "cos": {
            "code": "def cos(x):\n    import numpy\n    result = numpy.cos(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "cosh": {
            "code": "def cosh(x):\n    import numpy\n    result = numpy.cosh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "count_nonzero": {
            "code": "def count_nonzero(x):\n    import numpy\n    result = numpy.count_nonzero(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "cumprod": {
            "code": "def cumprod(x):\n    import numpy\n    result = numpy.cumprod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "cumsum": {
            "code": "def cumsum(x):\n    import numpy\n    result = numpy.cumsum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "cumulative_prod": {
            "code": "def cumulative_prod(x):\n    import numpy\n    result = numpy.cumulative_prod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "cumulative_sum": {
            "code": "def cumulative_sum(x):\n    import numpy\n    result = numpy.cumulative_sum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "deg2rad": {
            "code": "def deg2rad(x):\n    import numpy\n    result = numpy.deg2rad(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "degrees": {
            "code": "def degrees(x):\n    import numpy\n    result = numpy.degrees(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "diag": {
            "code": "def diag(x):\n    import numpy\n    result = numpy.diag(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "diag_indices": {
            "code": "def diag_indices(x):\n    import numpy\n    result = numpy.diag_indices(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "diagflat": {
            "code": "def diagflat(x):\n    import numpy\n    result = numpy.diagflat(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "diff": {
            "code": "def diff(x):\n    import numpy\n    result = numpy.diff(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "dstack": {
            "code": "def dstack(x):\n    import numpy\n    result = numpy.dstack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ediff1d": {
            "code": "def ediff1d(x):\n    import numpy\n    result = numpy.ediff1d(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "exp": {
            "code": "def exp(x):\n    import numpy\n    result = numpy.exp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "exp2": {
            "code": "def exp2(x):\n    import numpy\n    result = numpy.exp2(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "expm1": {
            "code": "def expm1(x):\n    import numpy\n    result = numpy.expm1(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "eye": {
            "code": "def eye(x):\n    import numpy\n    result = numpy.eye(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "fabs": {
            "code": "def fabs(x):\n    import numpy\n    result = numpy.fabs(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "fix": {
            "code": "def fix(x):\n    import numpy\n    result = numpy.fix(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "flatnonzero": {
            "code": "def flatnonzero(x):\n    import numpy\n    result = numpy.flatnonzero(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "flip": {
            "code": "def flip(x):\n    import numpy\n    result = numpy.flip(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "integer",
        },
        "floor": {
            "code": "def floor(x):\n    import numpy\n    result = numpy.floor(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "format_float_positional": {
            "code": "def format_float_positional(x):\n    import numpy\n    result = numpy.format_float_positional(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "format_float_scientific": {
            "code": "def format_float_scientific(x):\n    import numpy\n    result = numpy.format_float_scientific(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "frexp": {
            "code": "def frexp(x):\n    import numpy\n    result = numpy.frexp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "from_dlpack": {
            "code": "def from_dlpack(x):\n    import numpy\n    result = numpy.from_dlpack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "gradient": {
            "code": "def gradient(x):\n    import numpy\n    result = numpy.gradient(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hamming": {
            "code": "def hamming(x):\n    import numpy\n    result = numpy.hamming(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "hanning": {
            "code": "def hanning(x):\n    import numpy\n    result = numpy.hanning(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "histogram": {
            "code": "def histogram(x):\n    import numpy\n    result = numpy.histogram(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "histogram_bin_edges": {
            "code": "def histogram_bin_edges(x):\n    import numpy\n    result = numpy.histogram_bin_edges(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "histogramdd": {
            "code": "def histogramdd(x):\n    import numpy\n    result = numpy.histogramdd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hstack": {
            "code": "def hstack(x):\n    import numpy\n    result = numpy.hstack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "i0": {
            "code": "def i0(x):\n    import numpy\n    result = numpy.i0(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "imag": {
            "code": "def imag(x):\n    import numpy\n    result = numpy.imag(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "iscomplex": {
            "code": "def iscomplex(x):\n    import numpy\n    result = numpy.iscomplex(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "iscomplexobj": {
            "code": "def iscomplexobj(x):\n    import numpy\n    result = numpy.iscomplexobj(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "isfinite": {
            "code": "def isfinite(x):\n    import numpy\n    result = numpy.isfinite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isfortran": {
            "code": "def isfortran(x):\n    import numpy\n    result = numpy.isfortran(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "isinf": {
            "code": "def isinf(x):\n    import numpy\n    result = numpy.isinf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isnan": {
            "code": "def isnan(x):\n    import numpy\n    result = numpy.isnan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isneginf": {
            "code": "def isneginf(x):\n    import numpy\n    result = numpy.isneginf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isposinf": {
            "code": "def isposinf(x):\n    import numpy\n    result = numpy.isposinf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isreal": {
            "code": "def isreal(x):\n    import numpy\n    result = numpy.isreal(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "isrealobj": {
            "code": "def isrealobj(x):\n    import numpy\n    result = numpy.isrealobj(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "isscalar": {
            "code": "def isscalar(x):\n    import numpy\n    result = numpy.isscalar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "iterable": {
            "code": "def iterable(x):\n    import numpy\n    result = numpy.iterable(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "lexsort": {
            "code": "def lexsort(x):\n    import numpy\n    result = numpy.lexsort(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "log": {
            "code": "def log(x):\n    import numpy\n    result = numpy.log(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "log10": {
            "code": "def log10(x):\n    import numpy\n    result = numpy.log10(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "log1p": {
            "code": "def log1p(x):\n    import numpy\n    result = numpy.log1p(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "log2": {
            "code": "def log2(x):\n    import numpy\n    result = numpy.log2(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "logical_not": {
            "code": "def logical_not(x):\n    import numpy\n    result = numpy.logical_not(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "max": {
            "code": "def max(x):\n    import numpy\n    result = numpy.max(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mean": {
            "code": "def mean(x):\n    import numpy\n    result = numpy.mean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "median": {
            "code": "def median(x):\n    import numpy\n    result = numpy.median(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "min": {
            "code": "def min(x):\n    import numpy\n    result = numpy.min(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "min_scalar_type": {
            "code": "def min_scalar_type(x):\n    import numpy\n    result = numpy.min_scalar_type(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mintypecode": {
            "code": "def mintypecode(x):\n    import numpy\n    result = numpy.mintypecode(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "modf": {
            "code": "def modf(x):\n    import numpy\n    result = numpy.modf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "nan_to_num": {
            "code": "def nan_to_num(x):\n    import numpy\n    result = numpy.nan_to_num(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "nanargmax": {
            "code": "def nanargmax(x):\n    import numpy\n    result = numpy.nanargmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "nanargmin": {
            "code": "def nanargmin(x):\n    import numpy\n    result = numpy.nanargmin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "nancumprod": {
            "code": "def nancumprod(x):\n    import numpy\n    result = numpy.nancumprod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "nancumsum": {
            "code": "def nancumsum(x):\n    import numpy\n    result = numpy.nancumsum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "nanmax": {
            "code": "def nanmax(x):\n    import numpy\n    result = numpy.nanmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanmean": {
            "code": "def nanmean(x):\n    import numpy\n    result = numpy.nanmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanmedian": {
            "code": "def nanmedian(x):\n    import numpy\n    result = numpy.nanmedian(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanmin": {
            "code": "def nanmin(x):\n    import numpy\n    result = numpy.nanmin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanprod": {
            "code": "def nanprod(x):\n    import numpy\n    result = numpy.nanprod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanstd": {
            "code": "def nanstd(x):\n    import numpy\n    result = numpy.nanstd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nansum": {
            "code": "def nansum(x):\n    import numpy\n    result = numpy.nansum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "nanvar": {
            "code": "def nanvar(x):\n    import numpy\n    result = numpy.nanvar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "ndim": {
            "code": "def ndim(x):\n    import numpy\n    result = numpy.ndim(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "negative": {
            "code": "def negative(x):\n    import numpy\n    result = numpy.negative(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "nonzero": {
            "code": "def nonzero(x):\n    import numpy\n    result = numpy.nonzero(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "permute_dims": {
            "code": "def permute_dims(x):\n    import numpy\n    result = numpy.permute_dims(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "poly": {
            "code": "def poly(x):\n    import numpy\n    result = numpy.poly(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "polyder": {
            "code": "def polyder(x):\n    import numpy\n    result = numpy.polyder(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "polyint": {
            "code": "def polyint(x):\n    import numpy\n    result = numpy.polyint(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "positive": {
            "code": "def positive(x):\n    import numpy\n    result = numpy.positive(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "prod": {
            "code": "def prod(x):\n    import numpy\n    result = numpy.prod(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "ptp": {
            "code": "def ptp(x):\n    import numpy\n    result = numpy.ptp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "rad2deg": {
            "code": "def rad2deg(x):\n    import numpy\n    result = numpy.rad2deg(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "radians": {
            "code": "def radians(x):\n    import numpy\n    result = numpy.radians(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ravel": {
            "code": "def ravel(x):\n    import numpy\n    result = numpy.ravel(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "real": {
            "code": "def real(x):\n    import numpy\n    result = numpy.real(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "real_if_close": {
            "code": "def real_if_close(x):\n    import numpy\n    result = numpy.real_if_close(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "reciprocal": {
            "code": "def reciprocal(x):\n    import numpy\n    result = numpy.reciprocal(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "require": {
            "code": "def require(x):\n    import numpy\n    result = numpy.require(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "rint": {
            "code": "def rint(x):\n    import numpy\n    result = numpy.rint(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "roots": {
            "code": "def roots(x):\n    import numpy\n    result = numpy.roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "round": {
            "code": "def round(x):\n    import numpy\n    result = numpy.round(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "row_stack": {
            "code": "def row_stack(x):\n    import numpy\n    result = numpy.row_stack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "shape": {
            "code": "def shape(x):\n    import numpy\n    result = numpy.shape(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "sign": {
            "code": "def sign(x):\n    import numpy\n    result = numpy.sign(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "signbit": {
            "code": "def signbit(x):\n    import numpy\n    result = numpy.signbit(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sin": {
            "code": "def sin(x):\n    import numpy\n    result = numpy.sin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sinc": {
            "code": "def sinc(x):\n    import numpy\n    result = numpy.sinc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sinh": {
            "code": "def sinh(x):\n    import numpy\n    result = numpy.sinh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "size": {
            "code": "def size(x):\n    import numpy\n    result = numpy.size(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "sort": {
            "code": "def sort(x):\n    import numpy\n    result = numpy.sort(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sort_complex": {
            "code": "def sort_complex(x):\n    import numpy\n    result = numpy.sort_complex(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "spacing": {
            "code": "def spacing(x):\n    import numpy\n    result = numpy.spacing(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sqrt": {
            "code": "def sqrt(x):\n    import numpy\n    result = numpy.sqrt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "square": {
            "code": "def square(x):\n    import numpy\n    result = numpy.square(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "squeeze": {
            "code": "def squeeze(x):\n    import numpy\n    result = numpy.squeeze(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "stack": {
            "code": "def stack(x):\n    import numpy\n    result = numpy.stack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "std": {
            "code": "def std(x):\n    import numpy\n    result = numpy.std(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "sum": {
            "code": "def sum(x):\n    import numpy\n    result = numpy.sum(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tan": {
            "code": "def tan(x):\n    import numpy\n    result = numpy.tan(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "tanh": {
            "code": "def tanh(x):\n    import numpy\n    result = numpy.tanh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "transpose": {
            "code": "def transpose(x):\n    import numpy\n    result = numpy.transpose(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "trapezoid": {
            "code": "def trapezoid(x):\n    import numpy\n    result = numpy.trapezoid(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tri": {
            "code": "def tri(x):\n    import numpy\n    result = numpy.tri(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "tril_indices": {
            "code": "def tril_indices(x):\n    import numpy\n    result = numpy.tril_indices(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "trim_zeros": {
            "code": "def trim_zeros(x):\n    import numpy\n    result = numpy.trim_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "triu_indices": {
            "code": "def triu_indices(x):\n    import numpy\n    result = numpy.triu_indices(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "integer",
            "output_type": "array",
        },
        "trunc": {
            "code": "def trunc(x):\n    import numpy\n    result = numpy.trunc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "unique": {
            "code": "def unique(x):\n    import numpy\n    result = numpy.unique(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "unique_all": {
            "code": "def unique_all(x):\n    import numpy\n    result = numpy.unique_all(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "unique_counts": {
            "code": "def unique_counts(x):\n    import numpy\n    result = numpy.unique_counts(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "unique_inverse": {
            "code": "def unique_inverse(x):\n    import numpy\n    result = numpy.unique_inverse(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "unique_values": {
            "code": "def unique_values(x):\n    import numpy\n    result = numpy.unique_values(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "unstack": {
            "code": "def unstack(x):\n    import numpy\n    result = numpy.unstack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "unwrap": {
            "code": "def unwrap(x):\n    import numpy\n    result = numpy.unwrap(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "vander": {
            "code": "def vander(x):\n    import numpy\n    result = numpy.vander(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "var": {
            "code": "def var(x):\n    import numpy\n    result = numpy.var(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "vstack": {
            "code": "def vstack(x):\n    import numpy\n    result = numpy.vstack(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "where": {
            "code": "def where(x):\n    import numpy\n    result = numpy.where(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "cholesky": {
            "code": "def cholesky(x):\n    import numpy.linalg\n    result = numpy.linalg.cholesky(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "det": {
            "code": "def det(x):\n    import numpy.linalg\n    result = numpy.linalg.det(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "eig": {
            "code": "def eig(x):\n    import numpy.linalg\n    result = numpy.linalg.eig(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigh": {
            "code": "def eigh(x):\n    import numpy.linalg\n    result = numpy.linalg.eigh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigvals": {
            "code": "def eigvals(x):\n    import numpy.linalg\n    result = numpy.linalg.eigvals(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigvalsh": {
            "code": "def eigvalsh(x):\n    import numpy.linalg\n    result = numpy.linalg.eigvalsh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "inv": {
            "code": "def inv(x):\n    import numpy.linalg\n    result = numpy.linalg.inv(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "matrix_rank": {
            "code": "def matrix_rank(x):\n    import numpy.linalg\n    result = numpy.linalg.matrix_rank(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "norm": {
            "code": "def norm(x):\n    import numpy.linalg\n    result = numpy.linalg.norm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "pinv": {
            "code": "def pinv(x):\n    import numpy.linalg\n    result = numpy.linalg.pinv(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "qr": {
            "code": "def qr(x):\n    import numpy.linalg\n    result = numpy.linalg.qr(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "slogdet": {
            "code": "def slogdet(x):\n    import numpy.linalg\n    result = numpy.linalg.slogdet(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "svd": {
            "code": "def svd(x):\n    import numpy.linalg\n    result = numpy.linalg.svd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "svdvals": {
            "code": "def svdvals(x):\n    import numpy.linalg\n    result = numpy.linalg.svdvals(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "vector_norm": {
            "code": "def vector_norm(x):\n    import numpy.linalg\n    result = numpy.linalg.vector_norm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "fft": {
            "code": "def fft(x):\n    import numpy.fft\n    result = numpy.fft.fft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "fftn": {
            "code": "def fftn(x):\n    import numpy.fft\n    result = numpy.fft.fftn(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "fftshift": {
            "code": "def fftshift(x):\n    import numpy.fft\n    result = numpy.fft.fftshift(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hfft": {
            "code": "def hfft(x):\n    import numpy.fft\n    result = numpy.fft.hfft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ifft": {
            "code": "def ifft(x):\n    import numpy.fft\n    result = numpy.fft.ifft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ifftn": {
            "code": "def ifftn(x):\n    import numpy.fft\n    result = numpy.fft.ifftn(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ifftshift": {
            "code": "def ifftshift(x):\n    import numpy.fft\n    result = numpy.fft.ifftshift(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "ihfft": {
            "code": "def ihfft(x):\n    import numpy.fft\n    result = numpy.fft.ihfft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "irfft": {
            "code": "def irfft(x):\n    import numpy.fft\n    result = numpy.fft.irfft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "irfftn": {
            "code": "def irfftn(x):\n    import numpy.fft\n    result = numpy.fft.irfftn(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "rfft": {
            "code": "def rfft(x):\n    import numpy.fft\n    result = numpy.fft.rfft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "rfftn": {
            "code": "def rfftn(x):\n    import numpy.fft\n    result = numpy.fft.rfftn(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "bytes": {
            "code": "def bytes(x):\n    import numpy.random\n    result = numpy.random.bytes(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "chisquare": {
            "code": "def chisquare(x):\n    import numpy.random\n    result = numpy.random.chisquare(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "choice": {
            "code": "def choice(x):\n    import numpy.random\n    result = numpy.random.choice(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "dirichlet": {
            "code": "def dirichlet(x):\n    import numpy.random\n    result = numpy.random.dirichlet(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "gamma": {
            "code": "def gamma(x):\n    import numpy.random\n    result = numpy.random.gamma(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "pareto": {
            "code": "def pareto(x):\n    import numpy.random\n    result = numpy.random.pareto(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "permutation": {
            "code": "def permutation(x):\n    import numpy.random\n    result = numpy.random.permutation(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "power": {
            "code": "def power(x):\n    import numpy.random\n    result = numpy.random.power(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "randint": {
            "code": "def randint(x):\n    import numpy.random\n    result = numpy.random.randint(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "random_integers": {
            "code": "def random_integers(x):\n    import numpy.random\n    result = numpy.random.random_integers(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "integer",
        },
        "standard_gamma": {
            "code": "def standard_gamma(x):\n    import numpy.random\n    result = numpy.random.standard_gamma(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "standard_t": {
            "code": "def standard_t(x):\n    import numpy.random\n    result = numpy.random.standard_t(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "weibull": {
            "code": "def weibull(x):\n    import numpy.random\n    result = numpy.random.weibull(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "zipf": {
            "code": "def zipf(x):\n    import numpy.random\n    result = numpy.random.zipf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "integer",
        },
    }
