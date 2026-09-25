"""WTP operator registry (directive s3-s7, s35): world-building atoms with
metadata. Atoms act on a FIELD tensor (world law), on a sensed VECTOR
(sensory law), or on an organism's MEMORY (hazard law). Every atom is a
pure function of (array, params, rng) and is deterministic given rng.

Metadata per op: family, domain, in/out signature, invertible,
differentiable, flops(shape), bytes(shape), workspace(shape), precision,
sparsity, and the parameter ranges mutation may draw from."""
from dataclasses import dataclass, field
from typing import Callable
import numpy as np


@dataclass
class Op:
    op_id: str
    family: str          # TENSOR | TN | LINALG | SPECTRAL | STOCH | SPARSE | ELEMENT
    domain: str          # field | vector | memory
    fn: Callable
    params: dict = field(default_factory=dict)   # name -> (kind, lo, hi)
    in_sig: str = "T[n1..nd]"
    out_sig: str = "T[n1..nd]"
    invertible: bool = False
    differentiable: bool = True
    precision: str = "fp64|fp32|fp16"
    sparsity: str = "dense"
    changes_shape: bool = False

    def flops(self, shape):
        n = int(np.prod(shape))
        return {"TN": 8 * n * max(shape), "LINALG": 4 * n * max(shape), "SPECTRAL": 5 * n * np.log2(max(n, 2))}.get(self.family, 2 * n)

    def bytes(self, shape):
        return 16 * int(np.prod(shape))

    def workspace(self, shape):
        return int(np.prod(shape)) if self.family in ("TN", "LINALG", "SPECTRAL") else 0


REG = {}


def op(op_id, family, domain, params=None, **meta):
    def deco(fn):
        REG[op_id] = Op(op_id, family, domain, fn, params or {}, **meta)
        return fn
    return deco


def _std(x):
    s = x.std()
    return (x - x.mean()) / s if s > 1e-12 else x


# ------------------------------------------------------------------ field atoms (world laws)

@op("f_permute", "TENSOR", "field", invertible=True, changes_shape=True)
def f_permute(x, p, rng):
    return np.transpose(x, rng.permutation(x.ndim))


@op("f_contract_mode", "TENSOR", "field", {"mode": ("mode",)}, invertible=False, changes_shape=True)
def f_contract_mode(x, p, rng):
    if x.ndim <= 2:
        return x
    m = p["mode"] % x.ndim
    w = rng.normal(size=x.shape[m])
    return np.tensordot(x, w, axes=([m], [0]))


@op("f_reduce_max", "TENSOR", "field", {"mode": ("mode",)}, differentiable=False, changes_shape=True)
def f_reduce_max(x, p, rng):
    return x.max(axis=p["mode"] % x.ndim) if x.ndim > 2 else x


@op("f_reduce_norm", "TENSOR", "field", {"mode": ("mode",)}, changes_shape=True)
def f_reduce_norm(x, p, rng):
    return np.sqrt((x ** 2).sum(axis=p["mode"] % x.ndim)) if x.ndim > 2 else x


@op("f_merge_modes", "TENSOR", "field", {"mode": ("mode",)}, invertible=True, changes_shape=True)
def f_merge_modes(x, p, rng):
    if x.ndim <= 2:
        return x
    m = p["mode"] % (x.ndim - 1)
    s = list(x.shape)
    return x.reshape(s[:m] + [s[m] * s[m + 1]] + s[m + 2:])


@op("f_split_mode", "TENSOR", "field", {"mode": ("mode",)}, invertible=True, changes_shape=True)
def f_split_mode(x, p, rng):
    m = p["mode"] % x.ndim
    n = x.shape[m]
    for f in range(2, int(np.sqrt(n)) + 1):
        if n % f == 0:
            s = list(x.shape)
            return x.reshape(s[:m] + [f, n // f] + s[m + 1:])
    return x


@op("f_hadamard_self", "ELEMENT", "field")
def f_hadamard_self(x, p, rng):
    return x * np.roll(x, 1, axis=int(rng.integers(x.ndim)))


@op("f_outer_marginals", "TENSOR", "field")
def f_outer_marginals(x, p, rng):
    out = np.zeros_like(x)
    for m in range(x.ndim):
        marg = x.mean(axis=tuple(i for i in range(x.ndim) if i != m))
        sh = [1] * x.ndim
        sh[m] = -1
        out = out + marg.reshape(sh)
    return x + p.get("a", 1.0) * out


@op("f_unary", "ELEMENT", "field", {"kind": ("choice", ["tanh", "abs", "sign", "square", "relu", "sin", "cube"])},
    differentiable=False)
def f_unary(x, p, rng):
    z = _std(x)
    return {"tanh": np.tanh, "abs": np.abs, "sign": np.sign, "square": np.square, "relu": lambda v: np.maximum(v, 0),
            "sin": lambda v: np.sin(3 * v), "cube": lambda v: v ** 3}[p["kind"]](z)


@op("f_binary_field", "ELEMENT", "field", {"kind": ("choice", ["mul", "add", "max"])})
def f_binary_field(x, p, rng):
    y = rng.normal(size=x.shape)
    return {"mul": x * y, "add": x + y, "max": np.maximum(x, y)}[p["kind"]]


@op("f_tt_round", "TN", "field", {"rank": ("int", 1, 6)}, invertible=False)
def f_tt_round(x, p, rng):
    from ensorain.e0.tt import tt_svd
    cores, _ = tt_svd(x, max_rank=p["rank"])
    t = cores[0]
    for c in cores[1:]:
        t = np.tensordot(t, c, axes=([-1], [0]))
    return t.reshape(x.shape)


@op("f_svd_power", "LINALG", "field", {"power": ("float", 0.0, 3.0)})
def f_svd_power(x, p, rng):
    """Unfold at the middle cut, raise singular values to a power (flatten or sharpen the spectrum)."""
    k = max(1, x.ndim // 2)
    M = x.reshape(int(np.prod(x.shape[:k])), -1)
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    s2 = (s / (s[0] + 1e-12)) ** p["power"]
    return ((U * s2) @ Vt).reshape(x.shape)


@op("f_qr_mode", "LINALG", "field", {"mode": ("mode",)})
def f_qr_mode(x, p, rng):
    m = p["mode"] % x.ndim
    M = np.moveaxis(x, m, 0).reshape(x.shape[m], -1).T
    Q, _ = np.linalg.qr(M)
    out = Q.T.reshape((min(M.shape),) + tuple(np.delete(x.shape, m)))
    if out.shape[0] != x.shape[m]:
        return x
    return np.moveaxis(out, 0, m)


@op("f_gemv_mode", "LINALG", "field", {"mode": ("mode",)})
def f_gemv_mode(x, p, rng):
    m = p["mode"] % x.ndim
    A = rng.normal(size=(x.shape[m], x.shape[m])) / np.sqrt(x.shape[m])
    return np.moveaxis(np.tensordot(A, np.moveaxis(x, m, 0), axes=([1], [0])), 0, m)


@op("f_fft_abs", "SPECTRAL", "field", {"mode": ("mode",)}, invertible=False)
def f_fft_abs(x, p, rng):
    return np.abs(np.fft.fft(x, axis=p["mode"] % x.ndim))


@op("f_lowpass", "SPECTRAL", "field", {"mode": ("mode",), "keep": ("float", 0.1, 0.7)})
def f_lowpass(x, p, rng):
    m = p["mode"] % x.ndim
    F = np.fft.fft(x, axis=m)
    n = x.shape[m]
    k = max(1, int(p["keep"] * n))
    mask = np.zeros(n)
    mask[:k] = 1
    mask[-k + 1:] = 1 if k > 1 else mask[-k + 1:]
    sh = [1] * x.ndim
    sh[m] = n
    return np.real(np.fft.ifft(F * mask.reshape(sh), axis=m))


@op("f_phase_scramble", "SPECTRAL", "field", {"mode": ("mode",)}, invertible=False)
def f_phase_scramble(x, p, rng):
    m = p["mode"] % x.ndim
    F = np.fft.fft(x, axis=m)
    ph = np.exp(1j * rng.uniform(0, 2 * np.pi, size=F.shape))
    return np.real(np.fft.ifft(np.abs(F) * ph, axis=m))


@op("f_noise", "STOCH", "field", {"sd": ("float", 0.05, 1.0), "dist": ("choice", ["normal", "laplace", "lognormal"])})
def f_noise(x, p, rng):
    z = {"normal": rng.normal(size=x.shape), "laplace": rng.laplace(size=x.shape),
         "lognormal": rng.lognormal(size=x.shape) - 1.6}[p["dist"]]
    return _std(x) + p["sd"] * z


@op("f_rare_spikes", "STOCH", "field", {"rate": ("float", 0.001, 0.05)})
def f_rare_spikes(x, p, rng):
    z = _std(x)
    m = rng.random(x.shape) < p["rate"]
    return z + m * rng.normal(0, 8, size=x.shape)


@op("f_correlated_noise", "STOCH", "field", {"sd": ("float", 0.1, 1.0), "mode": ("mode",)})
def f_correlated_noise(x, p, rng):
    m = p["mode"] % x.ndim
    z = rng.normal(size=x.shape)
    z = np.cumsum(z, axis=m) / np.sqrt(x.shape[m])
    return _std(x) + p["sd"] * _std(z)


@op("f_topk_sparsify", "SPARSE", "field", {"keep": ("float", 0.05, 0.5)}, sparsity="sparse", differentiable=False)
def f_topk_sparsify(x, p, rng):
    z = _std(x)
    t = np.quantile(np.abs(z), 1 - p["keep"])
    return np.where(np.abs(z) >= t, z, 0.0)


@op("f_mask", "SPARSE", "field", {"keep": ("float", 0.2, 0.9)}, sparsity="masked")
def f_mask(x, p, rng):
    return _std(x) * (rng.random(x.shape) < p["keep"])


# ------------------------------------------------------------------ vector atoms (sensory laws)

@op("v_fft_abs", "SPECTRAL", "vector", in_sig="v[n]", out_sig="v[n]")
def v_fft_abs(v, p, rng):
    return np.abs(np.fft.fft(v))


@op("v_sign", "ELEMENT", "vector", in_sig="v[n]", out_sig="v[n]", differentiable=False)
def v_sign(v, p, rng):
    return np.sign(v)


@op("v_quantize", "ELEMENT", "vector", {"levels": ("int", 2, 8)}, in_sig="v[n]", out_sig="v[n]", differentiable=False,
    precision="int")
def v_quantize(v, p, rng):
    q = p["levels"]
    return np.round(np.clip(v, -2, 2) * (q / 4)) / (q / 4)


@op("v_sort", "TENSOR", "vector", in_sig="v[n]", out_sig="v[n]", differentiable=False)
def v_sort(v, p, rng):
    return np.sort(v)


@op("v_cumsum", "TENSOR", "vector", in_sig="v[n]", out_sig="v[n]", invertible=True)
def v_cumsum(v, p, rng):
    return np.cumsum(v)


@op("v_tanh", "ELEMENT", "vector", in_sig="v[n]", out_sig="v[n]", invertible=True)
def v_tanh(v, p, rng):
    return np.tanh(v)


# ------------------------------------------------------------------ memory hazards (applied to an organism)

HAZARDS = ("svd_trunc", "permute", "scramble", "quantize2", "reset_part", "rank_inflate")


def registry_table():
    """Machine-readable registry (op metadata) for the observatory."""
    rows = []
    for k, o in REG.items():
        sh = (8, 8, 8)
        rows.append(dict(op_id=k, family=o.family, domain=o.domain, in_sig=o.in_sig, out_sig=o.out_sig,
                         invertible=o.invertible, differentiable=o.differentiable, flops_8x8x8=int(o.flops(sh)),
                         bytes_8x8x8=o.bytes(sh), workspace_8x8x8=o.workspace(sh), precision=o.precision,
                         sparsity=o.sparsity, changes_shape=o.changes_shape, params=o.params))
    for h in HAZARDS:
        rows.append(dict(op_id=f"hazard_{h}", family="MEMORY", domain="memory"))
    return rows


FIELD_OPS = [k for k, o in REG.items() if o.domain == "field"]
VECTOR_OPS = [k for k, o in REG.items() if o.domain == "vector"]


def sample_params(o, rng):
    p = {}
    for name, spec in o.params.items():
        if spec[0] == "mode":
            p[name] = int(rng.integers(0, 16))
        elif spec[0] == "int":
            p[name] = int(rng.integers(spec[1], spec[2] + 1))
        elif spec[0] == "float":
            p[name] = float(rng.uniform(spec[1], spec[2]))
        elif spec[0] == "choice":
            p[name] = str(rng.choice(spec[1]))
    return p
