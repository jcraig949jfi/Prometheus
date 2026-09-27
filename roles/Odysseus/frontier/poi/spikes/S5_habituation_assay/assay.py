"""Substrate-agnostic habituation assay (spike S5, stdlib only).

A system to be assayed must expose:
    n_inputs            int >= 1 (>= 2 for the stimulus-specificity gate H4)
    reset()             return to a fixed initial state (deterministic)
    step(u) -> y        u: tuple of n_inputs floats; y: float or list of floats
    get_state()/set_state(s)   snapshot/restore (optional; copy.deepcopy of the
                        object is used otherwise). Stepping must be
                        deterministic given the snapshot (seed any RNG inside it).

Core idea: the evoked response to a stimulus is measured COUNTERFACTUALLY --
the stimulated continuation minus the unstimulated continuation from the same
snapshot. For an LTI system that difference is the impulse response, whatever
the history, so an LTI system can never show a decrement. A naive
"peak minus pre-stimulus value" metric is also provided (metric='prestim')
only to demonstrate how it produces false positives.

Gates (thresholds in FROZEN, fixed before any run; see RECEIPT.md section 1):
    H1 decrement, H2 stimulus-caused (vs time-matched sham), H3 recovery after
    rest (vs time-matched sham), H4 stimulus specificity (channel B).
    PASS_CORE = valid & responsive & H1 & H2 & H3 ; PASS_FULL = PASS_CORE & H4.

Usage:
    from assay import run_assay
    res = run_assay(system)            # dict; res['outputs'][i]['pass_full']
"""
import copy
import math

FROZEN = dict(
    T0=200, N=10, ISI=10, WIDTH=2, AMP=1.0, WINDOW=10, REST=300,
    EPS_RESP=1e-6, DIVERGE=1e6,
    DEC_MAX=0.70, TAU_MAX=-0.60,          # H1
    SHAM_MIN=0.80, DEC_VS_SHAM_MAX=0.70,  # H2
    REC_FRAC_MIN=0.50,                    # H3
    B_RESP_MIN=0.10, SPEC_MIN=0.80,       # H4
)


class _Diverged(Exception):
    pass


def kendall_tau(xs, ys):
    """Kendall tau-a between two equal-length sequences."""
    n = len(xs)
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            a = (xs[j] - xs[i]) * (ys[j] - ys[i])
            s += (a > 0) - (a < 0)
    return s / (n * (n - 1) / 2.0)


def wilson(k, n, z=1.959964):
    """Wilson score 95% interval for k successes out of n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


class _Runner:
    """Wraps a system: snapshot/restore, vector outputs, divergence check."""

    def __init__(self, system, p):
        self.s = system
        self.p = p
        self.nin = system.n_inputs
        self.has_state = hasattr(system, "get_state") and hasattr(system, "set_state")
        self.last_y = None

    def snap(self):
        st = self.s.get_state() if self.has_state else copy.deepcopy(self.s)
        return (st, self.last_y)

    def load(self, snap):
        st, ly = snap
        if self.has_state:
            self.s.set_state(copy.deepcopy(st) if not isinstance(st, tuple) else st)
        else:
            self.s = copy.deepcopy(st)
        self.last_y = ly

    def step(self, u):
        y = self.s.step(u)
        if not isinstance(y, (list, tuple)):
            y = [y]
        for v in y:
            if v != v or abs(v) > self.p["DIVERGE"]:
                raise _Diverged()
        self.last_y = list(y)
        return self.last_y

    def zeros(self, k):
        z = tuple([0.0] * self.nin)
        for _ in range(k):
            self.step(z)

    def stim_input(self, ch, t):
        if ch is None or t >= self.p["WIDTH"]:
            return tuple([0.0] * self.nin)
        u = [0.0] * self.nin
        u[ch] = self.p["AMP"]
        return tuple(u)

    def evoked(self, snap, ch, metric):
        """Evoked amplitude per output from snapshot at onset.
        Returns (list of r per output, snapshot after the stimulated window)."""
        W = self.p["WINDOW"]
        self.load(snap)
        pre = self.last_y
        ys = [self.step(self.stim_input(ch, t)) for t in range(W)]
        after = self.snap()
        if metric == "counterfactual":
            self.load(snap)
            ys0 = [self.step(self.stim_input(None, t)) for t in range(W)]
        elif metric == "prestim":
            ys0 = [pre] * W
        else:
            raise ValueError(metric)
        nout = len(ys[0])
        r = [max(abs(ys[t][i] - ys0[t][i]) for t in range(W)) for i in range(nout)]
        return r, after

    def advance(self, snap, k):
        self.load(snap)
        self.zeros(k)
        return self.snap()


def _gates(r, r_sham_N, r_sham_rec, r_rec, rB_after, rB_naive, p, has_b):
    N = len(r)
    late = sum(r[-3:]) / 3.0
    r1 = r[0]
    out = dict(r=r, r1=r1, late=late, r_sham_N=r_sham_N, r_sham_rec=r_sham_rec,
               r_rec=r_rec, rB_after=rB_after, rB_naive=rB_naive)
    out["responsive"] = r1 >= p["EPS_RESP"]
    if not out["responsive"]:
        out.update(dec_ratio=None, tau=None, H1=False, H2=False, H3=False,
                   H4=False, pass_core=False, pass_full=False)
        return out
    out["dec_ratio"] = late / r1
    out["tau"] = kendall_tau(list(range(N)), r)
    out["H1"] = out["dec_ratio"] <= p["DEC_MAX"] and out["tau"] <= p["TAU_MAX"]
    out["sham_ratio"] = r_sham_N / r1
    out["dec_vs_sham"] = late / r_sham_N if r_sham_N > 0 else float("inf")
    out["H2"] = out["sham_ratio"] >= p["SHAM_MIN"] and out["dec_vs_sham"] <= p["DEC_VS_SHAM_MAX"]
    if r_sham_rec > late:
        out["rec_frac"] = (r_rec - late) / (r_sham_rec - late)
    else:
        out["rec_frac"] = None
    out["H3"] = out["rec_frac"] is not None and out["rec_frac"] >= p["REC_FRAC_MIN"]
    if has_b and rB_naive >= p["B_RESP_MIN"] * r1 and rB_naive > 0:
        out["spec_ratio"] = rB_after / rB_naive
        out["H4"] = out["spec_ratio"] >= p["SPEC_MIN"]
    else:
        out["spec_ratio"] = None
        out["H4"] = False
    out["pass_core"] = out["H1"] and out["H2"] and out["H3"]
    out["pass_full"] = out["pass_core"] and out["H4"]
    return out


def run_assay(system, ch_a=0, ch_b=1, metric="counterfactual", **overrides):
    """Run the frozen protocol. Returns dict with 'valid' and per-output gate
    results in 'outputs'. Protocol parameters may be overridden (e.g. ISI=5)
    for secondary sweeps only; the headline verdict uses FROZEN."""
    p = dict(FROZEN)
    p.update(overrides)
    if p["WINDOW"] > p["ISI"]:
        p["WINDOW"] = p["ISI"]
    run = _Runner(system, p)
    has_b = run.nin >= 2 and ch_b is not None
    N, ISI, W, REST = p["N"], p["ISI"], p["WINDOW"], p["REST"]
    try:
        run.s.reset()
        run.last_y = None
        run.zeros(p["T0"])
        S0 = run.snap()
        # TRAIN
        rs = []
        s = S0
        for k in range(N):
            rk, s = run.evoked(s, ch_a, metric)
            if ISI > W:
                s = run.advance(s, ISI - W)
            rs.append(rk)
        SN = s  # at t_{N+1}
        rB_after = run.evoked(SN, ch_b, metric)[0] if has_b else None
        r_rec = run.evoked(run.advance(SN, REST), ch_a, metric)[0]
        # SHAM
        sh = run.advance(S0, (N - 1) * ISI)            # t_N
        r_sham_N = run.evoked(sh, ch_a, metric)[0]
        sh = run.advance(sh, ISI)                       # t_{N+1}
        rB_naive = run.evoked(sh, ch_b, metric)[0] if has_b else None
        sh = run.advance(sh, REST)                      # t_rec
        r_sham_rec = run.evoked(sh, ch_a, metric)[0]
    except _Diverged:
        return dict(valid=False, outputs=[])
    nout = len(rs[0])
    outs = []
    for i in range(nout):
        outs.append(_gates([rk[i] for rk in rs], r_sham_N[i], r_sham_rec[i],
                           r_rec[i], rB_after[i] if has_b else None,
                           rB_naive[i] if has_b else None, p, has_b))
    return dict(valid=True, outputs=outs, protocol=p, metric=metric,
                ch_a=ch_a, ch_b=ch_b)


def rate_sensitivity(system, ch_a=0, out=0, short_isi=5, long_isi=20, rest=100):
    """Secondary diagnostic (not a gate): Thompson-Spencer rate sensitivity.
    Returns decrement ratio and recovery fraction after a short rest for
    short- vs long-ISI training. Two-timescale systems are expected to show
    deeper-but-faster-recovering habituation at the short ISI."""
    res = {}
    for name, isi in (("short", short_isi), ("long", long_isi)):
        a = run_assay(system, ch_a=ch_a, ch_b=None, ISI=isi, REST=rest)
        o = a["outputs"][out] if a["valid"] else {}
        res[name] = dict(isi=isi, dec_ratio=o.get("dec_ratio"), rec_frac=o.get("rec_frac"))
    return res
