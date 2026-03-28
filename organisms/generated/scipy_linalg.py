"""Auto-generated organism wrapping 48 functions from scipy.linalg."""

import numpy as np
from organisms.base import MathematicalOrganism


class ScipyLinalgOrganism(MathematicalOrganism):
    name = "scipy_linalg"
    operations = {
        "bandwidth": {
            "code": "def bandwidth(x):\n    import scipy.linalg\n    result = scipy.linalg.bandwidth(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "integer",
        },
        "cho_factor": {
            "code": "def cho_factor(x):\n    import scipy.linalg\n    result = scipy.linalg.cho_factor(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "cholesky": {
            "code": "def cholesky(x):\n    import scipy.linalg\n    result = scipy.linalg.cholesky(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "cholesky_banded": {
            "code": "def cholesky_banded(x):\n    import scipy.linalg\n    result = scipy.linalg.cholesky_banded(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "circulant": {
            "code": "def circulant(x):\n    import scipy.linalg\n    result = scipy.linalg.circulant(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "companion": {
            "code": "def companion(x):\n    import scipy.linalg\n    result = scipy.linalg.companion(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "coshm": {
            "code": "def coshm(x):\n    import scipy.linalg\n    result = scipy.linalg.coshm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "cosm": {
            "code": "def cosm(x):\n    import scipy.linalg\n    result = scipy.linalg.cosm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "det": {
            "code": "def det(x):\n    import scipy.linalg\n    result = scipy.linalg.det(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "dft": {
            "code": "def dft(x):\n    import scipy.linalg\n    result = scipy.linalg.dft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "eig": {
            "code": "def eig(x):\n    import scipy.linalg\n    result = scipy.linalg.eig(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eig_banded": {
            "code": "def eig_banded(x):\n    import scipy.linalg\n    result = scipy.linalg.eig_banded(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigh": {
            "code": "def eigh(x):\n    import scipy.linalg\n    result = scipy.linalg.eigh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigvals": {
            "code": "def eigvals(x):\n    import scipy.linalg\n    result = scipy.linalg.eigvals(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigvals_banded": {
            "code": "def eigvals_banded(x):\n    import scipy.linalg\n    result = scipy.linalg.eigvals_banded(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "eigvalsh": {
            "code": "def eigvalsh(x):\n    import scipy.linalg\n    result = scipy.linalg.eigvalsh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "expm": {
            "code": "def expm(x):\n    import scipy.linalg\n    result = scipy.linalg.expm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "expm_cond": {
            "code": "def expm_cond(x):\n    import scipy.linalg\n    result = scipy.linalg.expm_cond(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "fiedler": {
            "code": "def fiedler(x):\n    import scipy.linalg\n    result = scipy.linalg.fiedler(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "fiedler_companion": {
            "code": "def fiedler_companion(x):\n    import scipy.linalg\n    result = scipy.linalg.fiedler_companion(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "hankel": {
            "code": "def hankel(x):\n    import scipy.linalg\n    result = scipy.linalg.hankel(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hessenberg": {
            "code": "def hessenberg(x):\n    import scipy.linalg\n    result = scipy.linalg.hessenberg(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "inv": {
            "code": "def inv(x):\n    import scipy.linalg\n    result = scipy.linalg.inv(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "ishermitian": {
            "code": "def ishermitian(x):\n    import scipy.linalg\n    result = scipy.linalg.ishermitian(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "issymmetric": {
            "code": "def issymmetric(x):\n    import scipy.linalg\n    result = scipy.linalg.issymmetric(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "ldl": {
            "code": "def ldl(x):\n    import scipy.linalg\n    result = scipy.linalg.ldl(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "logm": {
            "code": "def logm(x):\n    import scipy.linalg\n    result = scipy.linalg.logm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "lu": {
            "code": "def lu(x):\n    import scipy.linalg\n    result = scipy.linalg.lu(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "lu_factor": {
            "code": "def lu_factor(x):\n    import scipy.linalg\n    result = scipy.linalg.lu_factor(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "matrix_balance": {
            "code": "def matrix_balance(x):\n    import scipy.linalg\n    result = scipy.linalg.matrix_balance(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "norm": {
            "code": "def norm(x):\n    import scipy.linalg\n    result = scipy.linalg.norm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "null_space": {
            "code": "def null_space(x):\n    import scipy.linalg\n    result = scipy.linalg.null_space(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "orth": {
            "code": "def orth(x):\n    import scipy.linalg\n    result = scipy.linalg.orth(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "pinv": {
            "code": "def pinv(x):\n    import scipy.linalg\n    result = scipy.linalg.pinv(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "pinvh": {
            "code": "def pinvh(x):\n    import scipy.linalg\n    result = scipy.linalg.pinvh(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "polar": {
            "code": "def polar(x):\n    import scipy.linalg\n    result = scipy.linalg.polar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "qr": {
            "code": "def qr(x):\n    import scipy.linalg\n    result = scipy.linalg.qr(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "rq": {
            "code": "def rq(x):\n    import scipy.linalg\n    result = scipy.linalg.rq(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "schur": {
            "code": "def schur(x):\n    import scipy.linalg\n    result = scipy.linalg.schur(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "signm": {
            "code": "def signm(x):\n    import scipy.linalg\n    result = scipy.linalg.signm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "sinhm": {
            "code": "def sinhm(x):\n    import scipy.linalg\n    result = scipy.linalg.sinhm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "sinm": {
            "code": "def sinm(x):\n    import scipy.linalg\n    result = scipy.linalg.sinm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "sqrtm": {
            "code": "def sqrtm(x):\n    import scipy.linalg\n    result = scipy.linalg.sqrtm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "svd": {
            "code": "def svd(x):\n    import scipy.linalg\n    result = scipy.linalg.svd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "svdvals": {
            "code": "def svdvals(x):\n    import scipy.linalg\n    result = scipy.linalg.svdvals(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "tanhm": {
            "code": "def tanhm(x):\n    import scipy.linalg\n    result = scipy.linalg.tanhm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "tanm": {
            "code": "def tanm(x):\n    import scipy.linalg\n    result = scipy.linalg.tanm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "toeplitz": {
            "code": "def toeplitz(x):\n    import scipy.linalg\n    result = scipy.linalg.toeplitz(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
    }
