"""C4 v0.3 SYSID: LOCAL, decoder-free physical coordinates behind a restricted probe interface (R-MECH F1 repair).

Why local. F1 showed that a guard-compliant coordinate (probe decodability after h steps) restates the
certificate once a law indexes it at h = q. Blacklisting that expression is not enough: any coordinate that
OBSERVES how far input information propagates over many steps measures the phenomenon itself. So the C4 v0.3
coordinate vocabulary may observe the dynamics for AT MOST ONE controlled step from a stationary state. A law
that predicts k-step usability must then COMPOSE one-step physics into a k-step prediction. That is a physical
claim that can fail; it cannot be a remeasurement, because nothing in the vocabulary has seen k steps of input
propagation.

Enforcement (G7 LOCALITY). Coordinates receive a LocalProbe, never the System:
- stationary(n): n states reached after a burn-in of i.i.d. drive; the burn-in inputs and noise are NOT exposed,
  so no label about past inputs exists to decode;
- step1(states, obs, noise): ONE step from a stationary state. Each state carries a generation tag, and a
  state that already took a controlled step is refused (HorizonError);
- full(states), readout(states): the two views;
- noise(n): fresh noise draws; kick(states, scale): a whitened random kick on the float state arrays.
The probe uses its own RNG namespace (G2) and imports numpy only (G1).

Coordinates (all in whitened stationary units, hence invariant to invertible re-encodings of either view, G5):
  rho    one-step contraction: |d full| after one step / |d full| before, for a small random state kick
         (same input, same noise); median ratio
  lam    SPECTRAL contraction: spectral radius of the one-step response matrix J, fitted by ridge regression of
         d full(after) on d full(before) over RESAMPLE perturbations (each state element replaced, with prob
         Q_RESAMPLE, by the same element of another stationary episode). Works for float and integer state
         alike; for Boolean networks it is the Derrida damage-spreading slope's matrix version. lam governs
         the slowest local mode, which rho (a median over all directions) does not
  eta    noise injection: |d full|^2 after one step for twins differing only in their noise draw
  gamma  input injection: |d full|^2 after one step for twins differing only in their input symbol (uniform over
         the probe alphabet; never the task cue, never at a task time)
  vis    readout visibility: |d readout| / |d full| for a state kick, zero steps
Each is a world property: one value per world, identical across k (G3).
"""
from __future__ import annotations

from typing import Dict

import numpy as np

BURN = 64           # burn-in steps for stationary states (frozen)
KICK = 1e-2         # kick scale in whitened units (frozen)
Q_RESAMPLE = 0.05   # per-element resample probability for the lam perturbation (frozen)
N_JAC = 2048        # perturbed states for the lam regression (frozen)
N_STAT = 512        # stationary states per coordinate (frozen)
SEED_NS = 0x5C05_10CA


class HorizonError(RuntimeError):
    pass


class _Tagged:
    __slots__ = ("st", "gen")

    def __init__(self, st, gen):
        self.st, self.gen = st, gen


def _whitener(F):
    mu = F.mean(0)
    C = np.cov(F - mu, rowvar=False)
    C = np.atleast_2d(C)
    w, U = np.linalg.eigh(C)
    keep = w > max(w.max(), 1e-12) * 1e-9
    W = U[:, keep] / np.sqrt(w[keep])
    return mu, W


class LocalProbe:
    def __init__(self, system, n_in: int, seed: int = 0, drive=None):
        self._sys = system
        self._n_in = int(n_in)
        self._rng = np.random.default_rng([SEED_NS, int(seed)])
        self._drive = drive            # alphabet of i.i.d. drive symbols; default: all symbols

    # -- views -------------------------------------------------------------------------------------
    def full(self, t: _Tagged) -> np.ndarray:
        return np.asarray(self._sys.full_state(t.st), float)

    def readout(self, t: _Tagged) -> np.ndarray:
        return np.asarray(self._sys.readout_features(t.st), float)

    # -- states ------------------------------------------------------------------------------------
    def stationary(self, n: int) -> _Tagged:
        st = self._sys.init(n)
        alpha = np.arange(self._n_in) if self._drive is None else np.asarray(self._drive)
        for _ in range(BURN):
            o = alpha[self._rng.integers(0, len(alpha), n)]
            st = self._sys.step(st, o, self._sys.noise(n, self._rng))
        return _Tagged(st, 0)

    def noise(self, n: int) -> Dict[str, np.ndarray]:
        return self._sys.noise(n, self._rng)

    def symbols(self, n: int) -> np.ndarray:
        return self._rng.integers(0, self._n_in, n)

    def step1(self, t: _Tagged, obs, noise) -> _Tagged:
        if t.gen >= 1:
            raise HorizonError("LOCALITY: a state that already took a controlled step cannot step again")
        st = {k: v.copy() for k, v in t.st.items()}
        return _Tagged(self._sys.step(st, np.asarray(obs), noise), t.gen + 1)

    def kick(self, t: _Tagged, scale: float, W_full=None) -> _Tagged:
        """Random kick on every float array of the state, scaled per array by its stationary SD."""
        if t.gen >= 1:
            raise HorizonError("LOCALITY: kicks only on stationary states")
        out = {}
        for k, v in t.st.items():
            if np.issubdtype(v.dtype, np.floating):
                sd = v.std(0, keepdims=True) + 1e-12
                out[k] = v + scale * sd * self._rng.standard_normal(v.shape)
            else:
                out[k] = v.copy()
        return _Tagged(out, t.gen)

    def resample(self, t: _Tagged, q: float) -> _Tagged:
        """Replace each state element, with probability q, by the same element of a random other episode."""
        if t.gen >= 1:
            raise HorizonError("LOCALITY: perturbations only on stationary states")
        out = {}
        for k, v in t.st.items():
            n = v.shape[0]
            donor = v[self._rng.integers(0, n, n)]
            m = self._rng.random(v.shape) < q
            out[k] = np.where(m, donor, v)
        return _Tagged(out, t.gen)

    @staticmethod
    def copy(t: _Tagged) -> _Tagged:
        return _Tagged({k: v.copy() for k, v in t.st.items()}, t.gen)


def coordinates(probe: LocalProbe, n: int = N_STAT) -> Dict[str, float]:
    s0 = probe.stationary(n)
    F0 = probe.full(s0)
    R0 = probe.readout(s0)
    mf, Wf = _whitener(F0)
    mr, Wr = _whitener(R0)

    def wf(F):
        return (F - mf) @ Wf

    def wr(R):
        return (R - mr) @ Wr

    dims = max(1, Wf.shape[1])
    obs = probe.symbols(n)
    nz = probe.noise(n)

    # rho: kick, then one step with identical input and noise
    sk = probe.kick(s0, KICK)
    d0 = np.linalg.norm(wf(probe.full(sk)) - wf(F0), axis=1)
    a = probe.step1(s0, obs, nz)
    b = probe.step1(sk, obs, nz)
    d1 = np.linalg.norm(wf(probe.full(b)) - wf(probe.full(a)), axis=1)
    ok = d0 > 0
    rho = float(np.median(d1[ok] / d0[ok])) if ok.any() else float("nan")

    # vis: readout change per full-state change for the same kick (zero steps)
    dr = np.linalg.norm(wr(probe.readout(sk)) - wr(R0), axis=1)
    vis = float(np.median(dr[ok] / d0[ok])) if ok.any() else float("nan")

    # eta: twins differing only in the noise draw
    a2 = probe.step1(s0, obs, probe.noise(n))
    eta = float(np.mean(np.sum((wf(probe.full(a2)) - wf(probe.full(a))) ** 2, 1)) / (2 * dims))

    # gamma: twins differing only in the input symbol, same noise
    obs2 = probe.symbols(n)
    diff = obs2 != obs
    b2 = probe.step1(s0, obs2, nz)
    dg = np.sum((wf(probe.full(b2)) - wf(probe.full(a))) ** 2, 1)
    gamma = float(np.mean(dg[diff]) / (2 * dims)) if diff.any() else float("nan")
    return {"rho": rho, "eta": eta, "gamma": gamma, "vis": vis, "lam": spectral_contraction(probe)}


def spectral_contraction(probe: LocalProbe, n: int = N_JAC, q: float = Q_RESAMPLE) -> float:
    s0 = probe.stationary(n)
    F0 = probe.full(s0)
    mf, Wf = _whitener(F0)
    if Wf.shape[1] == 0:
        return float("nan")
    sp = probe.resample(s0, q)
    X = (probe.full(sp) - F0) @ Wf
    obs, nz = probe.symbols(n), probe.noise(n)
    a = probe.step1(s0, obs, nz)
    b = probe.step1(sp, obs, nz)
    Y = (probe.full(b) - probe.full(a)) @ Wf
    act = np.abs(X).sum(1) > 0
    X, Y = X[act], Y[act]
    if len(X) < 8:
        return float("nan")
    D = X.shape[1]
    J = np.linalg.solve(X.T @ X + 1e-3 * len(X) * np.eye(D), X.T @ Y).T
    return float(np.max(np.abs(np.linalg.eigvals(J))))


def local_lgss(probe: LocalProbe, n: int = N_JAC, q: float = Q_RESAMPLE, ridge: float = 1e-3) -> Dict[str, np.ndarray]:
    """The full LOCAL linear-Gaussian description, all from one controlled step (G7), in whitened units:
      J  (D, D)       one-step response to resample perturbations (regressed)
      B  (n_in, D)    one-step input injection per symbol, centred over symbols (same states, same noise)
      Q  (D, D)       one-step noise injection covariance (noise twins, halved)
      C  (Dr, D)      zero-step readout map (regressed d readout on d full)
    A law may compose these into a k-step prediction; nothing here observed more than one step."""
    s0 = probe.stationary(n)
    F0, R0 = probe.full(s0), probe.readout(s0)
    mf, Wf = _whitener(F0)
    mr, Wr = _whitener(R0)
    D = Wf.shape[1]
    sp = probe.resample(s0, q)
    X = (probe.full(sp) - F0) @ Wf
    Xr = (probe.readout(sp) - R0) @ Wr
    obs, nz = probe.symbols(n), probe.noise(n)
    a = probe.step1(s0, obs, nz)
    b = probe.step1(sp, obs, nz)
    Y = (probe.full(b) - probe.full(a)) @ Wf
    act = np.abs(X).sum(1) > 0
    G = X[act].T @ X[act] + ridge * act.sum() * np.eye(D)
    J = np.linalg.solve(G, X[act].T @ Y[act]).T
    C = np.linalg.solve(G, X[act].T @ Xr[act]).T
    a2 = probe.step1(s0, obs, probe.noise(n))
    Dn = (probe.full(a2) - probe.full(a)) @ Wf
    Q = (Dn.T @ Dn) / (2 * n)
    Bm = []
    for o in range(probe._n_in):
        so = probe.step1(s0, np.full(n, o), nz)
        Bm.append(((probe.full(so) - mf) @ Wf).mean(0))
    Bm = np.array(Bm)
    return {"J": J, "B": Bm - Bm.mean(0), "Q": Q, "C": C}


def lgss_discriminability(L: Dict[str, np.ndarray], V: int, k: int, ridge: float = 1e-6) -> float:
    """C4-L-0003 score: mean pairwise Mahalanobis discriminability (d^2) of the cue at the readout after the query,
    composing the one-step description: cue injected at step 0, k distractor steps, one identical query step."""
    J, B, Q, C = L["J"], L["B"], L["Q"], L["C"]
    D = J.shape[0]
    Jp = [np.eye(D)]
    for _ in range(k + 1):
        Jp.append(J @ Jp[-1])
    dist = B[V:2 * V]
    SB = np.cov(dist.T) if len(dist) > 1 else np.zeros((D, D))
    Sx = sum(Jp[i] @ Q @ Jp[i].T for i in range(k + 2)) + sum(Jp[i] @ SB @ Jp[i].T for i in range(1, k + 1))
    Sr = C @ Sx @ C.T
    Sr = Sr + ridge * max(np.trace(Sr) / max(len(Sr), 1), 1e-12) * np.eye(len(Sr))
    Si = np.linalg.pinv(Sr)
    d2 = []
    for c1 in range(V):
        for c2 in range(c1 + 1, V):
            dl = C @ Jp[k + 1] @ (B[c1] - B[c2])
            d2.append(float(dl @ Si @ dl))
    return float(np.mean(d2))
