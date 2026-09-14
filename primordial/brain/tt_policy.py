"""Lane C (BRAIN): a tensor-train policy over observation digits.

Each uint16 observation feature is split into 4 base-16 digits (most
significant first). With d = 4*obs_dim digits x_0..x_{d-1}, a policy is
(alpha [r], G [d,16,r,r], W [r,A]) and

    logits(x) = alpha^T  G[0,x_0] G[1,x_1] ... G[d-1,x_{d-1}]  W

One act costs d*r^2 + r*A flops per observation. Hot path: uint16 obs in,
int32 actions out; no str.

Backends compute the same function; C1 measures where each one wins.
  np_gather            numpy: gather G[k,x_k] per sample, batched matmul (chunked)
  np_bucket            numpy: sort samples by digit, 16 dense matmuls per core
  numba_par            numba prange over sample chunks (NUMBA_NUM_THREADS)
  numba_1              the same kernel on one thread
  torch_cpu            torch bmm over gathered cores on CPU
  torch_gpu_e2e        obs host->device, contract, int32 actions device->host
  torch_gpu_graph_e2e  the same inside a captured CUDA graph, pinned staging
  torch_gpu_resident   obs already on device, actions stay there (a GPU world)
Cheats (controls: the C1 instrument must catch them; never on the board):
  cheat_skip_half      contracts only every other core (fast and wrong)
  cheat_gpu_nosync     resident GPU path that returns before its kernels finish
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

try:
    from numba import prange
except ImportError:  # pragma: no cover
    prange = range

CHUNK_FLOATS = 1 << 22        # CPU gather chunk: <= 16 MB of float32 per core
GPU_CHUNK_FLOATS = 1 << 26    # GPU gather chunk: <= 256 MB of float32 per core
_SH = np.array([12, 8, 4, 0], np.uint16)


def digits(obs: np.ndarray) -> np.ndarray:
    """uint16 [..., obs_dim] -> uint8 [B, 4*obs_dim], most significant digit first."""
    o = np.ascontiguousarray(obs, dtype=np.uint16).reshape(-1, obs.shape[-1])
    return ((o[:, :, None] >> _SH) & 15).astype(np.uint8).reshape(o.shape[0], -1)


@dataclass
class TTPolicy:
    alpha64: np.ndarray   # [r]
    G64: np.ndarray       # [d,16,r,r]
    W64: np.ndarray       # [r,A]
    alpha: np.ndarray = field(init=False)
    G: np.ndarray = field(init=False)
    W: np.ndarray = field(init=False)

    def __post_init__(self):
        self.alpha = self.alpha64.astype(np.float32)
        self.G = np.ascontiguousarray(self.G64, dtype=np.float32)
        self.W = np.ascontiguousarray(self.W64, dtype=np.float32)

    d = property(lambda s: s.G.shape[0])
    r = property(lambda s: s.G.shape[2])
    A = property(lambda s: s.W.shape[1])
    obs_dim = property(lambda s: s.G.shape[0] // 4)


def random_policy(obs_dim: int, r: int, A: int, seed: int) -> TTPolicy:
    """Orthogonal cores keep ||v|| = ||alpha|| = 1 through any depth, so float32
    backends stay comparable to the float64 reference at d = 64."""
    rng = np.random.default_rng(seed)
    d = 4 * obs_dim
    q, rr = np.linalg.qr(rng.standard_normal((d, 16, r, r)))
    q *= np.sign(np.diagonal(rr, axis1=-2, axis2=-1))[..., None, :]
    alpha = rng.standard_normal(r)
    return TTPolicy(alpha / np.linalg.norm(alpha), q, rng.standard_normal((r, A)))


def additive_policy(f: np.ndarray, r: int) -> TTPolicy:
    """Positive control: an exact rank-(A+1) TT for logits = sum_k f[k, x_k].
    State row vector [1, s_1..s_A]; G[k,j] adds f[k,j] to s. Integer f keeps
    float32 exact, so every honest backend must match to the last bit."""
    d, base, A = f.shape
    assert base == 16 and r >= A + 1
    G = np.broadcast_to(np.eye(r), (d, 16, r, r)).copy()
    G[:, :, 0, 1:A + 1] = f
    alpha = np.zeros(r); alpha[0] = 1.0
    W = np.zeros((r, A)); W[1:A + 1, :] = np.eye(A)
    return TTPolicy(alpha, G, W)


def additive_logits(f: np.ndarray, obs: np.ndarray) -> np.ndarray:
    dig = digits(obs)
    return f[np.arange(f.shape[0]), dig].sum(axis=1)


def ref64_logits(p: TTPolicy, obs: np.ndarray) -> np.ndarray:
    """The oracle: float64, one sample and one matvec at a time, no batching tricks."""
    dig = digits(obs)
    out = np.empty((len(dig), p.A))
    for i in range(len(dig)):
        v = p.alpha64
        for k in range(p.d):
            v = v @ p.G64[k, dig[i, k]]
        out[i] = v @ p.W64
    return out


# ------------------------------------------------------------------ backends

class Backend:
    name = ""
    device = "cpu"
    cheat = False

    def __init__(self, p: TTPolicy):
        self.p = p

    def prepare(self, obs: np.ndarray):
        return np.ascontiguousarray(obs, dtype=np.uint16).reshape(-1, obs.shape[-1])

    def run(self, x):
        return self.logits(x).argmax(1).astype(np.int32)

    def logits(self, obs: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def to_numpy(self, a) -> np.ndarray:
        return np.array(a, dtype=np.int32, copy=True)

    def sync(self) -> None:
        pass

    def close(self) -> None:
        pass


class NpGather(Backend):
    name = "np_gather"

    def logits(self, obs):
        p, dig = self.p, digits(obs)
        B = len(dig)
        out = np.empty((B, p.A), np.float32)
        ch = max(1, CHUNK_FLOATS // (p.r * p.r))
        for lo in range(0, B, ch):
            x = dig[lo:lo + ch]
            v = np.broadcast_to(p.alpha, (len(x), 1, p.r))
            for k in range(p.d):
                v = np.matmul(v, p.G[k][x[:, k]])
            out[lo:lo + ch] = v[:, 0, :] @ p.W
        return out


class NpBucket(Backend):
    name = "np_bucket"

    def _cores(self):
        return range(self.p.d)

    def logits(self, obs):
        p, dig = self.p, digits(obs)
        B = len(dig)
        v = np.empty((B, p.r), np.float32)
        v[:] = p.alpha
        for k in self._cores():
            col = dig[:, k]
            order = np.argsort(col, kind="stable")
            ends = np.cumsum(np.bincount(col, minlength=16))
            vs = v[order]
            lo = 0
            for j in range(16):
                hi = ends[j]
                if hi > lo:
                    vs[lo:hi] = vs[lo:hi] @ p.G[k, j]
                lo = hi
            v[order] = vs
        return v @ p.W


class CheatSkipHalf(NpBucket):
    name = "cheat_skip_half"
    cheat = True

    def _cores(self):
        return range(0, self.p.d, 2)


def _nb_kernel(dig, alpha, GT, W, out, nchunks):
    B = dig.shape[0]
    d = dig.shape[1]
    r = alpha.shape[0]
    A = W.shape[1]
    step = (B + nchunks - 1) // nchunks
    for c in prange(nchunks):
        lo = c * step
        hi = min(B, lo + step)
        buf = np.empty((2, r), dtype=np.float32)
        for i in range(lo, hi):
            for a in range(r):
                buf[0, a] = alpha[a]
            src = 0
            for k in range(d):
                x = dig[i, k]
                dst = 1 - src
                for b in range(r):
                    s = np.float32(0.0)
                    for a in range(r):
                        s += buf[src, a] * GT[k, x, b, a]
                    buf[dst, b] = s
                src = dst
            for c2 in range(A):
                s = np.float32(0.0)
                for b in range(r):
                    s += buf[src, b] * W[b, c2]
                out[i, c2] = s


_NB = {}


def _nb(parallel: bool):
    if parallel not in _NB:
        import numba
        _NB[parallel] = numba.njit(parallel=parallel, nogil=True, fastmath=True,
                                   boundscheck=False)(_nb_kernel)
    return _NB[parallel]


class NumbaPar(Backend):
    name = "numba_par"
    parallel = True

    def __init__(self, p):
        super().__init__(p)
        import numba
        self.kernel = _nb(self.parallel)
        self.GT = np.ascontiguousarray(p.G.transpose(0, 1, 3, 2))
        self.nchunks = numba.get_num_threads() * 8 if self.parallel else 1
        self.logits(np.zeros((1, p.obs_dim), np.uint16))   # compile outside timing

    def logits(self, obs):
        dig = digits(obs)
        out = np.empty((len(dig), self.p.A), np.float32)
        self.kernel(dig, self.p.alpha, self.GT, self.p.W, out, self.nchunks)
        return out


class Numba1(NumbaPar):
    name = "numba_1"
    parallel = False


class NumbaParC3(NumbaPar):
    """numba_par with 3 sample chunks instead of threads*8 (C1b: is load sensitivity chunk count?)."""
    name = "numba_par_c3"

    def __init__(self, p):
        super().__init__(p)
        self.nchunks = 3


class _Torch(Backend):
    def __init__(self, p, device):
        super().__init__(p)
        import torch
        self.t = torch
        self.dev = torch.device(device)
        self.device = device
        if self.dev.type == "cuda":
            torch.backends.cuda.matmul.allow_tf32 = False
        self.alpha = torch.from_numpy(p.alpha).to(self.dev)
        self.Gk = [torch.from_numpy(p.G[k]).to(self.dev) for k in range(p.d)]
        self.W = torch.from_numpy(p.W).to(self.dev)
        self.sh = torch.tensor([12, 8, 4, 0], dtype=torch.int32, device=self.dev)
        cap = GPU_CHUNK_FLOATS if self.dev.type == "cuda" else CHUNK_FLOATS
        self.chunk = max(1, cap // (p.r * p.r))

    def _logits_dev(self, x16):
        t = self.t
        x = x16.to(t.int32) & 0xFFFF
        dig = ((x.unsqueeze(-1) >> self.sh) & 15).reshape(x.shape[0], -1).to(t.int64)
        outs = []
        for lo in range(0, dig.shape[0], self.chunk):
            idx = dig[lo:lo + self.chunk]
            v = self.alpha.expand(idx.shape[0], 1, -1)
            for k, g in enumerate(self.Gk):
                v = t.bmm(v, g[idx[:, k]])
            outs.append(v.squeeze(1) @ self.W)
        return outs[0] if len(outs) == 1 else t.cat(outs)

    def _act_dev(self, x16):
        return self._logits_dev(x16).argmax(1).to(self.t.int32)

    def _host(self, obs):
        return super().prepare(obs).view(np.int16)

    def logits(self, obs):
        x = self.t.from_numpy(self._host(obs)).to(self.dev)
        return self._logits_dev(x).cpu().numpy()

    def sync(self):
        if self.dev.type == "cuda":
            self.t.cuda.synchronize()

    def close(self):
        if self.dev.type == "cuda":
            self.t.cuda.empty_cache()


class TorchCPU(_Torch):
    name = "torch_cpu"

    def __init__(self, p, threads: int = 3):
        super().__init__(p, "cpu")
        self.t.set_num_threads(threads)

    def prepare(self, obs):
        return self.t.from_numpy(self._host(obs))

    def run(self, x):
        return self._act_dev(x).numpy()


class TorchGpuE2E(_Torch):
    name = "torch_gpu_e2e"

    def __init__(self, p):
        super().__init__(p, "cuda")

    def prepare(self, obs):
        return self._host(obs)

    def run(self, x):
        return self._act_dev(self.t.from_numpy(x).to(self.dev)).cpu().numpy()


class TorchGpuResident(_Torch):
    name = "torch_gpu_resident"

    def __init__(self, p):
        super().__init__(p, "cuda")

    def prepare(self, obs):
        x = self.t.from_numpy(self._host(obs)).to(self.dev)
        self.sync()
        return x

    def run(self, x):
        a = self._act_dev(x)
        self.t.cuda.synchronize()
        return a

    def to_numpy(self, a):
        return a.cpu().numpy().astype(np.int32)


class CheatGpuNoSync(TorchGpuResident):
    name = "cheat_gpu_nosync"
    cheat = True

    def run(self, x):
        return self._act_dev(x)      # returns while the kernels are still queued


class TorchGpuGraphE2E(_Torch):
    """Captured CUDA graph per batch size; pinned host buffers both ways."""
    name = "torch_gpu_graph_e2e"

    def __init__(self, p):
        super().__init__(p, "cuda")
        self.B = None

    def _capture(self, B):
        t = self.t
        self.graph = None
        t.cuda.empty_cache()
        self.s_in = t.zeros((B, self.p.obs_dim), dtype=t.int16, device=self.dev)
        self.pin_in = t.empty((B, self.p.obs_dim), dtype=t.int16).pin_memory()
        self.pin_out = t.empty((B,), dtype=t.int32).pin_memory()
        self.pin_in_np, self.pin_out_np = self.pin_in.numpy(), self.pin_out.numpy()
        side = t.cuda.Stream()
        with t.cuda.stream(side):
            for _ in range(3):
                self._act_dev(self.s_in)
        t.cuda.current_stream().wait_stream(side)
        self.graph = t.cuda.CUDAGraph()
        with t.cuda.graph(self.graph):
            self.s_out = self._act_dev(self.s_in)
        self.B = B

    def prepare(self, obs):
        x = self._host(obs)
        if self.B != len(x):
            self._capture(len(x))
        return x

    def run(self, x):
        t = self.t
        self.pin_in_np[:] = x
        self.s_in.copy_(self.pin_in, non_blocking=True)
        self.graph.replay()
        self.pin_out.copy_(self.s_out, non_blocking=True)
        t.cuda.current_stream().synchronize()
        return self.pin_out_np

    def logits(self, obs):
        raise NotImplementedError("graph backend is validated on actions")

    def close(self):
        self.graph = self.s_in = self.s_out = self.pin_in = self.pin_out = None
        self.B = None
        super().close()


BACKENDS = {b.name: b for b in (NpGather, NpBucket, NumbaPar, Numba1, TorchCPU,
                                TorchGpuE2E, TorchGpuGraphE2E, TorchGpuResident,
                                CheatSkipHalf, CheatGpuNoSync)}
CPU_HONEST = ("np_gather", "np_bucket", "numba_par", "numba_1", "torch_cpu")
GPU_HONEST = ("torch_gpu_e2e", "torch_gpu_graph_e2e", "torch_gpu_resident")
CHEATS = ("cheat_skip_half", "cheat_gpu_nosync")


def make(name: str, p: TTPolicy) -> Backend:
    return BACKENDS[name](p)


class TTPolicyBrain:
    """contract.Brain over a TT policy. adapt() is C2's (plastic rank)."""

    def __init__(self, p: TTPolicy, backend: str = "numba_par"):
        self.p, self.be = p, make(backend, p)

    def act(self, obs, msg_in=None):
        n_envs, n_slots = obs.shape[0], obs.shape[1]
        a = self.be.to_numpy(self.be.run(self.be.prepare(obs)))
        return a.reshape(n_envs, n_slots, 1), None

    def adapt(self, signal):
        pass

    def cost(self):
        p = self.p
        return {"params": p.alpha.size + p.G.size + p.W.size,
                "flops_per_act": p.d * p.r * p.r + p.r * p.A,
                "state_bytes": p.alpha.nbytes + p.G.nbytes + p.W.nbytes}
