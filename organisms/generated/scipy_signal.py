"""Auto-generated organism wrapping 27 functions from scipy.signal."""

import numpy as np
from organisms.base import MathematicalOrganism


class ScipySignalOrganism(MathematicalOrganism):
    name = "scipy_signal"
    operations = {
        "argrelmax": {
            "code": "def argrelmax(x):\n    import scipy.signal\n    result = scipy.signal.argrelmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "argrelmin": {
            "code": "def argrelmin(x):\n    import scipy.signal\n    result = scipy.signal.argrelmin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "besselap": {
            "code": "def besselap(x):\n    import scipy.signal\n    result = scipy.signal.besselap(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "buttap": {
            "code": "def buttap(x):\n    import scipy.signal\n    result = scipy.signal.buttap(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "array",
        },
        "cspline1d": {
            "code": "def cspline1d(x):\n    import scipy.signal\n    result = scipy.signal.cspline1d(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "czt": {
            "code": "def czt(x):\n    import scipy.signal\n    result = scipy.signal.czt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "detrend": {
            "code": "def detrend(x):\n    import scipy.signal\n    result = scipy.signal.detrend(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "envelope": {
            "code": "def envelope(x):\n    import scipy.signal\n    result = scipy.signal.envelope(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "find_peaks": {
            "code": "def find_peaks(x):\n    import scipy.signal\n    result = scipy.signal.find_peaks(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "freqresp": {
            "code": "def freqresp(x):\n    import scipy.signal\n    result = scipy.signal.freqresp(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "freqz": {
            "code": "def freqz(x):\n    import scipy.signal\n    result = scipy.signal.freqz(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "gausspulse": {
            "code": "def gausspulse(x):\n    import scipy.signal\n    result = scipy.signal.gausspulse(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hilbert": {
            "code": "def hilbert(x):\n    import scipy.signal\n    result = scipy.signal.hilbert(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hilbert2": {
            "code": "def hilbert2(x):\n    import scipy.signal\n    result = scipy.signal.hilbert2(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "kaiser_beta": {
            "code": "def kaiser_beta(x):\n    import scipy.signal\n    result = scipy.signal.kaiser_beta(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "scalar",
            "output_type": "scalar",
        },
        "medfilt": {
            "code": "def medfilt(x):\n    import scipy.signal\n    result = scipy.signal.medfilt(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "minimum_phase": {
            "code": "def minimum_phase(x):\n    import scipy.signal\n    result = scipy.signal.minimum_phase(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "periodogram": {
            "code": "def periodogram(x):\n    import scipy.signal\n    result = scipy.signal.periodogram(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "qspline1d": {
            "code": "def qspline1d(x):\n    import scipy.signal\n    result = scipy.signal.qspline1d(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "qspline2d": {
            "code": "def qspline2d(x):\n    import scipy.signal\n    result = scipy.signal.qspline2d(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sawtooth": {
            "code": "def sawtooth(x):\n    import scipy.signal\n    result = scipy.signal.sawtooth(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "spectrogram": {
            "code": "def spectrogram(x):\n    import scipy.signal\n    result = scipy.signal.spectrogram(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "square": {
            "code": "def square(x):\n    import scipy.signal\n    result = scipy.signal.square(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "stft": {
            "code": "def stft(x):\n    import scipy.signal\n    result = scipy.signal.stft(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "unique_roots": {
            "code": "def unique_roots(x):\n    import scipy.signal\n    result = scipy.signal.unique_roots(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "welch": {
            "code": "def welch(x):\n    import scipy.signal\n    result = scipy.signal.welch(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "wiener": {
            "code": "def wiener(x):\n    import scipy.signal\n    result = scipy.signal.wiener(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
    }
