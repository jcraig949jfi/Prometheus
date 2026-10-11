"""WTP-05 world families (PREREG_WTP05 s2). Episodic POMDPs with LOCAL observations only (no global address).

Observation channels (W = 8):
  0-3  payload       4  f1: event flag (1 = cue / factor / bit / stimulus / mode, 0 = corridor)
  5    f2: tag       6  fG: gate (decision step)                                7  bias (= 1)
Corridor steps carry random +-1 payload on every channel 0-3, so nothing can be read off a fixed channel
without gating on the flags. Gate observations are locally identical whatever the hidden context is.

Actions are +-1 at every step; only gate steps are scored. Per block, world.block(K, rng, b) returns:
  obs (K,T,W), tgt (K,T) in {-1,0,+1}, wt (K,T) reward weight, role (K,T):
    1 final composed gate, 2 stepping-stone A, 3 stepping-stone B, 4 yoked (unrelated) gate,
    5 unrelated-competence trial (family C, the law that never switches)
  lat: {name: (values (K,), t_decode (K,))} hidden variables for state-decoding certification.

Families and rungs:
  A  delayed-context maze        R0 latch cA; R1 cA and cB; R2 cA*b (FLIP / XOR); R3 cA*cB*b (parity-3)
  B  rank-1 tensor lock          R2 sign(u.a) sign(v.b); R3 also * sign(w.c)    (a, b, c in R^2, Gaussian)
  N  hidden finite-state stream  R2 parity of a variable-length bit stream; R3 mode m selects parity of
     (non-tensor-native)          stream 0 or stream 1 ("context(A) selects operation(B)")
  C  law-switch                  type-1 law s -> s flips sign at an unannounced block; type-2 law never
                                 changes (unrelated competence). Working state resets every episode, so only
                                 lifetime plasticity can track the switch.
A carries 3 tag-0 distractor events per episode (structured ambiguity).
Conditions (A, B, N; s15): DESERT = only the final gate is scored; STEPPING = extra gates whose answers
are legitimate sub-skills (A, N: final-format gates with fewer live factors or a shorter history; B: the
primitives sign(u.a) and sign(v.b)); YOKED = the same number, timing and weight of extra gates, scored on
an unrelated reactive behaviour (the sign of a random payload channel at that gate).
Family C uses the analogous conditions defined in PREREG_WTP05 s2.4.
"""
import numpy as np

W = 8
P0, P1, P2, P3, F1, F2, FG, BIAS = range(8)


def _pm(rng, shape):
    return np.where(rng.random(shape) < 0.5, -1.0, 1.0)


def _ev(obs, ks, ts, tag, payload):
    """Vectorised event write: payload {channel: values}."""
    obs[ks, ts, :4] = 0.0
    for ch, v in payload.items():
        obs[ks, ts, ch] = v
    obs[ks, ts, F1], obs[ks, ts, F2], obs[ks, ts, FG] = 1.0, tag, 0.0


def _gt(obs, ks, ts, tag=0.0, payload=None):
    """Vectorised gate write: payload {channel: values} (others 0)."""
    obs[ks, ts, :4] = 0.0
    for ch, v in (payload or {}).items():
        obs[ks, ts, ch] = v
    obs[ks, ts, F1], obs[ks, ts, F2], obs[ks, ts, FG] = 0.0, tag, 1.0


def _unit(seed, k):
    r = np.random.default_rng(seed)
    out = []
    for _ in range(k):
        x = r.standard_normal(2)
        out.append(x / np.linalg.norm(x))
    return out


class World:
    family = rung = cond = None
    T = 16
    L = 8          # blocks per lifetime
    K = 32         # episodes per block
    chance = 0.5

    def __init__(self, rung, cond="desert", **kw):
        self.rung, self.cond = rung, cond
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def name(self):
        return f"{self.family}-{self.rung}-{self.cond}"

    def new_life(self, rng):
        pass

    def _base(self, K, rng):
        T = self.T
        obs = np.zeros((K, T, W))
        obs[:, :, :4] = _pm(rng, (K, T, 4))
        obs[:, :, BIAS] = 1.0
        return obs, np.zeros((K, T)), np.zeros((K, T)), np.zeros((K, T), int)


# ---------------------------------------------------------------------------------------------- family A

class FamilyA(World):
    family = "A"
    T = 16
    n_distract = 3

    def block(self, K, rng, b=0):
        obs, tgt, wt, role = self._base(K, rng)
        T, ar = self.T, np.arange(K)
        cA, cB, bb = _pm(rng, K), _pm(rng, K), _pm(rng, K)
        two = self.rung in ("R1", "R3")
        tB = rng.integers(2, 6, K)
        lat = {"cA": (cA, np.full(K, T - 1))}
        _ev(obs, ar, 0, +1.0, {P0: cA})
        if two:
            lat["cB"] = (cB, np.full(K, T - 1))
            _ev(obs, ar, tB, -1.0, {P0: cB})
        if self.rung == "R1":
            ask = _pm(rng, K)
            for t, a in ((T - 2, ask), (T - 1, -ask)):
                _gt(obs, ar, t, tag=a)
                obs[ar, t, F2] = a
                tgt[:, t], wt[:, t], role[:, t] = np.where(a > 0, cA, cB), 1.0, 1
        else:
            final = {"R0": cA, "R2": cA * bb, "R3": cA * cB * bb}[self.rung]
            _gt(obs, ar, T - 1, payload={P2: bb} if self.rung in ("R2", "R3") else None)
            tgt[:, T - 1], wt[:, T - 1], role[:, T - 1] = final, 1.0, 1
            if self.rung in ("R2", "R3") and self.cond != "desert":
                if self.cond == "yoked":
                    for t in (8, 12):
                        y = obs[:, t, P1].copy()
                        _gt(obs, ar, t, tag=-1.0, payload={P1: y})
                        tgt[:, t], wt[:, t], role[:, t] = y, 1.0, 4
                else:
                    third = cB if self.rung == "R3" else 1.0
                    _gt(obs, ar, 8, payload={P2: np.ones(K)})                 # (i) b = +1: only the context is live
                    tgt[:, 8], wt[:, 8], role[:, 8] = cA * third, 1.0, 2
                    _ev(obs, ar, 10, +1.0, {P0: cA})                         # (ii) cues re-shown before the gate
                    if self.rung == "R3":
                        _ev(obs, ar, 11, -1.0, {P0: cB})
                    b2 = _pm(rng, K)
                    _gt(obs, ar, 12, payload={P2: b2})
                    tgt[:, 12], wt[:, 12], role[:, 12] = cA * b2 * third, 1.0, 3
        # structured ambiguity: tag-0 distractor events on free corridor steps (defeats "remember the last event")
        free = (obs[:, :, F1] == 0) & (obs[:, :, FG] == 0)
        free[:, :-1] &= obs[:, 1:, FG] == 0
        free[:, 0] = free[:, T - 1] = False
        keys = np.where(free, rng.random((K, T)), 2.0)
        pick = np.argsort(keys, 1)[:, :self.n_distract]
        for j in range(self.n_distract):
            ok = keys[ar, pick[:, j]] < 2
            _ev(obs, ar[ok], pick[ok, j], 0.0, {P0: _pm(rng, ok.sum()), P1: _pm(rng, ok.sum())})
        return dict(obs=obs, tgt=tgt, wt=wt, role=role, lat=lat)


# ---------------------------------------------------------------------------------------------- family B

class FamilyB(World):
    family = "B"
    T = 12
    law_seed = 50_501

    def __init__(self, rung, cond="desert", **kw):
        super().__init__(rung, cond, **kw)
        self.u, self.v, self.w = _unit(self.law_seed, 3)

    def block(self, K, rng, b=0):
        obs, tgt, wt, role = self._base(K, rng)
        T, ar = self.T, np.arange(K)
        A_, B_, C_ = rng.standard_normal((K, 2)), rng.standard_normal((K, 2)), rng.standard_normal((K, 2))
        sa, sb, sc = (np.where(X @ d >= 0, 1.0, -1.0) for X, d in ((A_, self.u), (B_, self.v), (C_, self.w)))
        tb, tc = rng.integers(3, 6, K), rng.integers(7, 9, K)
        lat = {"ua": (sa, np.full(K, T - 1)), "vb": (sb, np.full(K, T - 1))}
        ta, tg = (-1.0, +1.0) if getattr(self, "swap_tags", False) else (+1.0, -1.0)   # transfer: factor tags swapped
        _ev(obs, ar, 0, ta, {P0: A_[:, 0], P1: A_[:, 1]})
        _ev(obs, ar, tb, tg, {P0: B_[:, 0], P1: B_[:, 1]})
        final = sa * sb
        if self.rung == "R3":
            lat["wc"] = (sc, np.full(K, T - 1))
            _ev(obs, ar, tc, 0.0, {P0: C_[:, 0], P1: C_[:, 1]})
            final = final * sc
        _gt(obs, ar, T - 1)
        tgt[:, T - 1], wt[:, T - 1], role[:, T - 1] = final, 1.0, 1
        if self.cond != "desert":
            for t, tag, val, rl in ((np.ones(K, int), +1.0, sa, 2), (tb + 1, -1.0, sb, 3)):
                if self.cond == "yoked":
                    y = _pm(rng, K)
                    _gt(obs, ar, t, tag=tag, payload={P2: y})
                    tgt[ar, t], role[ar, t] = y, 4
                else:
                    _gt(obs, ar, t, tag=tag)
                    tgt[ar, t], role[ar, t] = val, rl
                wt[ar, t] = 1.0
        return dict(obs=obs, tgt=tgt, wt=wt, role=role, lat=lat)


# ---------------------------------------------------------------------------------------------- family N

class FamilyN(World):
    """Non-tensor-native: a hidden finite-state process (running parity), not a TT/CP/low-rank target."""
    family = "N"
    T = 16
    p_bit = 0.45

    def block(self, K, rng, b=0):
        obs, tgt, wt, role = self._base(K, rng)
        T, ar = self.T, np.arange(K)
        par = np.ones((K, 2))
        mode, tmode = _pm(rng, K), rng.integers(1, 5, K)
        mids = (6, 10) if self.cond != "desert" else ()
        r3 = self.rung == "R3"
        for t in range(T - 1):
            if t in mids:
                if self.cond == "yoked":
                    y = _pm(rng, K)
                    _gt(obs, ar, t, tag=-1.0, payload={P1: y})
                    tgt[:, t], role[:, t] = y, 4
                else:
                    _gt(obs, ar, t)
                    tgt[:, t], role[:, t] = (np.where(mode > 0, par[:, 0], par[:, 1]) if r3 else par[:, 0]), 2
                wt[:, t] = 1.0
                continue
            is_mode = (tmode == t) if r3 else np.zeros(K, bool)
            if is_mode.any():
                _ev(obs, ar[is_mode], t, 0.0, {P1: mode[is_mode]})
            bit_on = (rng.random(K) < self.p_bit) & ~is_mode
            stream = (rng.random(K) < 0.5).astype(int) if r3 else np.zeros(K, int)
            bit = _pm(rng, K)
            ks = ar[bit_on]
            if len(ks):
                obs[ks, t, :4] = 0.0
                obs[ks, t, P0] = bit[ks]
                obs[ks, t, F1], obs[ks, t, F2], obs[ks, t, FG] = 1.0, np.where(stream[ks] == 0, 1.0, -1.0), 0.0
                par[ks, stream[ks]] *= bit[ks]
        final = np.where(mode > 0, par[:, 0], par[:, 1]) if r3 else par[:, 0]
        _gt(obs, ar, T - 1)
        tgt[:, T - 1], wt[:, T - 1], role[:, T - 1] = final, 1.0, 1
        lat = {"par0": (par[:, 0].copy(), np.full(K, T - 1))}
        if r3:
            lat["par1"] = (par[:, 1].copy(), np.full(K, T - 1))
            lat["mode"] = (mode, np.full(K, T - 1))
        return dict(obs=obs, tgt=tgt, wt=wt, role=role, lat=lat)


# ---------------------------------------------------------------------------------------------- family C

class FamilyC(World):
    """Law switch. Lifetime state: the switch block (drawn by new_life)."""
    family = "C"
    T = 2
    L = 12

    def new_life(self, rng):
        self.sw = int(rng.integers(4, 9))

    def law(self, b):
        sw = getattr(self, "sw", 6)
        if self.cond == "stepping" and b == 2:
            return -1.0                      # practice reversal (reverts at block 3)
        return -1.0 if b >= sw else 1.0

    def block(self, K, rng, b=0):
        obs, tgt, wt, role = self._base(K, rng)
        ar = np.arange(K)
        typ = rng.random(K) < 0.5
        s = _pm(rng, K)
        Lb = self.law(b)
        t3 = typ & (self.cond == "yoked" and b == 2)          # type-3: unrelated reactive behaviour
        t1 = typ & ~t3
        t2 = ~typ
        _gt(obs, ar[t3], 0, tag=0.0, payload={P2: s[t3]})
        _gt(obs, ar[t1], 0, tag=+1.0, payload={P0: s[t1]})
        _gt(obs, ar[t2], 0, tag=-1.0, payload={P1: s[t2]})
        tgt[:, 0] = np.where(t1, s * Lb, s)
        role[:, 0] = np.where(t3, 4, np.where(t1, 1, 5))
        wt[:, 0] = 1.0
        return dict(obs=obs, tgt=tgt, wt=wt, role=role, lat={}, law=Lb)


FAMILIES = dict(A=FamilyA, B=FamilyB, N=FamilyN, C=FamilyC)


def make(spec):
    """spec 'A-R2-desert' -> World."""
    fam, rung, cond = spec.split("-")
    return FAMILIES[fam](rung, cond)
