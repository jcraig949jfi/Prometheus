"""Auto-generated organism wrapping 62 functions from scipy.special."""

import numpy as np
from organisms.base import MathematicalOrganism


class ScipySpecialOrganism(MathematicalOrganism):
    name = "scipy_special"
    operations = {
        "ai_zeros": {
            "code": "def ai_zeros(x):\n    import scipy.special\n    result = scipy.special.ai_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "bei_zeros": {
            "code": "def bei_zeros(x):\n    import scipy.special\n    result = scipy.special.bei_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "beip_zeros": {
            "code": "def beip_zeros(x):\n    import scipy.special\n    result = scipy.special.beip_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "ber_zeros": {
            "code": "def ber_zeros(x):\n    import scipy.special\n    result = scipy.special.ber_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "bernoulli": {
            "code": "def bernoulli(x):\n    import scipy.special\n    result = scipy.special.bernoulli(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "berp_zeros": {
            "code": "def berp_zeros(x):\n    import scipy.special\n    result = scipy.special.berp_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "bi_zeros": {
            "code": "def bi_zeros(x):\n    import scipy.special\n    result = scipy.special.bi_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "c_roots": {
            "code": "def c_roots(x):\n    import scipy.special\n    result = scipy.special.c_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "chebyc": {
            "code": "def chebyc(x):\n    import scipy.special\n    result = scipy.special.chebyc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "chebys": {
            "code": "def chebys(x):\n    import scipy.special\n    result = scipy.special.chebys(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "chebyt": {
            "code": "def chebyt(x):\n    import scipy.special\n    result = scipy.special.chebyt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "chebyu": {
            "code": "def chebyu(x):\n    import scipy.special\n    result = scipy.special.chebyu(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "erf_zeros": {
            "code": "def erf_zeros(x):\n    import scipy.special\n    result = scipy.special.erf_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "euler": {
            "code": "def euler(x):\n    import scipy.special\n    result = scipy.special.euler(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "factorial": {
            "code": "def factorial(x):\n    import scipy.special\n    result = scipy.special.factorial(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "fresnel_zeros": {
            "code": "def fresnel_zeros(x):\n    import scipy.special\n    result = scipy.special.fresnel_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "fresnelc_zeros": {
            "code": "def fresnelc_zeros(x):\n    import scipy.special\n    result = scipy.special.fresnelc_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "fresnels_zeros": {
            "code": "def fresnels_zeros(x):\n    import scipy.special\n    result = scipy.special.fresnels_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "h_roots": {
            "code": "def h_roots(x):\n    import scipy.special\n    result = scipy.special.h_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "he_roots": {
            "code": "def he_roots(x):\n    import scipy.special\n    result = scipy.special.he_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "hermite": {
            "code": "def hermite(x):\n    import scipy.special\n    result = scipy.special.hermite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "hermitenorm": {
            "code": "def hermitenorm(x):\n    import scipy.special\n    result = scipy.special.hermitenorm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "jnjnp_zeros": {
            "code": "def jnjnp_zeros(x):\n    import scipy.special\n    result = scipy.special.jnjnp_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "kei_zeros": {
            "code": "def kei_zeros(x):\n    import scipy.special\n    result = scipy.special.kei_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "keip_zeros": {
            "code": "def keip_zeros(x):\n    import scipy.special\n    result = scipy.special.keip_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "kelvin_zeros": {
            "code": "def kelvin_zeros(x):\n    import scipy.special\n    result = scipy.special.kelvin_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "ker_zeros": {
            "code": "def ker_zeros(x):\n    import scipy.special\n    result = scipy.special.ker_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "kerp_zeros": {
            "code": "def kerp_zeros(x):\n    import scipy.special\n    result = scipy.special.kerp_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "l_roots": {
            "code": "def l_roots(x):\n    import scipy.special\n    result = scipy.special.l_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "laguerre": {
            "code": "def laguerre(x):\n    import scipy.special\n    result = scipy.special.laguerre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "lambertw": {
            "code": "def lambertw(x):\n    import scipy.special\n    result = scipy.special.lambertw(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "legendre": {
            "code": "def legendre(x):\n    import scipy.special\n    result = scipy.special.legendre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "log_softmax": {
            "code": "def log_softmax(x):\n    import scipy.special\n    result = scipy.special.log_softmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "logsumexp": {
            "code": "def logsumexp(x):\n    import scipy.special\n    result = scipy.special.logsumexp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "p_roots": {
            "code": "def p_roots(x):\n    import scipy.special\n    result = scipy.special.p_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "ps_roots": {
            "code": "def ps_roots(x):\n    import scipy.special\n    result = scipy.special.ps_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_chebyc": {
            "code": "def roots_chebyc(x):\n    import scipy.special\n    result = scipy.special.roots_chebyc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_chebys": {
            "code": "def roots_chebys(x):\n    import scipy.special\n    result = scipy.special.roots_chebys(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_chebyt": {
            "code": "def roots_chebyt(x):\n    import scipy.special\n    result = scipy.special.roots_chebyt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_chebyu": {
            "code": "def roots_chebyu(x):\n    import scipy.special\n    result = scipy.special.roots_chebyu(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_hermite": {
            "code": "def roots_hermite(x):\n    import scipy.special\n    result = scipy.special.roots_hermite(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_hermitenorm": {
            "code": "def roots_hermitenorm(x):\n    import scipy.special\n    result = scipy.special.roots_hermitenorm(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_laguerre": {
            "code": "def roots_laguerre(x):\n    import scipy.special\n    result = scipy.special.roots_laguerre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_legendre": {
            "code": "def roots_legendre(x):\n    import scipy.special\n    result = scipy.special.roots_legendre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_sh_chebyt": {
            "code": "def roots_sh_chebyt(x):\n    import scipy.special\n    result = scipy.special.roots_sh_chebyt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_sh_chebyu": {
            "code": "def roots_sh_chebyu(x):\n    import scipy.special\n    result = scipy.special.roots_sh_chebyu(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "roots_sh_legendre": {
            "code": "def roots_sh_legendre(x):\n    import scipy.special\n    result = scipy.special.roots_sh_legendre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "s_roots": {
            "code": "def s_roots(x):\n    import scipy.special\n    result = scipy.special.s_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "sh_chebyt": {
            "code": "def sh_chebyt(x):\n    import scipy.special\n    result = scipy.special.sh_chebyt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sh_chebyu": {
            "code": "def sh_chebyu(x):\n    import scipy.special\n    result = scipy.special.sh_chebyu(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sh_legendre": {
            "code": "def sh_legendre(x):\n    import scipy.special\n    result = scipy.special.sh_legendre(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "sinc": {
            "code": "def sinc(x):\n    import scipy.special\n    result = scipy.special.sinc(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "softmax": {
            "code": "def softmax(x):\n    import scipy.special\n    result = scipy.special.softmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "softplus": {
            "code": "def softplus(x):\n    import scipy.special\n    result = scipy.special.softplus(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "t_roots": {
            "code": "def t_roots(x):\n    import scipy.special\n    result = scipy.special.t_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "ts_roots": {
            "code": "def ts_roots(x):\n    import scipy.special\n    result = scipy.special.ts_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "u_roots": {
            "code": "def u_roots(x):\n    import scipy.special\n    result = scipy.special.u_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "us_roots": {
            "code": "def us_roots(x):\n    import scipy.special\n    result = scipy.special.us_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "y0_zeros": {
            "code": "def y0_zeros(x):\n    import scipy.special\n    result = scipy.special.y0_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "y1_zeros": {
            "code": "def y1_zeros(x):\n    import scipy.special\n    result = scipy.special.y1_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "y1p_zeros": {
            "code": "def y1p_zeros(x):\n    import scipy.special\n    result = scipy.special.y1p_zeros(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "zeta": {
            "code": "def zeta(x):\n    import scipy.special\n    result = scipy.special.zeta(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
    }
