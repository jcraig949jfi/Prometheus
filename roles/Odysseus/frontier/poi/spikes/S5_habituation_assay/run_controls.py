"""Run the S5 habituation assay on negative, positive, cheat controls and the
random-nonlinear null. Stdlib only, fixed seeds.

    python3 run_controls.py [results.json]
"""
import hashlib
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from assay import FROZEN, run_assay, rate_sensitivity, wilson  # noqa: E402

relu = lambda z: z if z > 0 else 0.0  # noqa: E731


# ---------------------------------------------------------------- systems
class LTI:
    """x' = A x + B u ; y = C x + D u. Stable by inf-norm(A) < 1."""
    n_inputs = 2

    def __init__(self, rng, n=None, diagonal=False):
        n = n or rng.randint(1, 6)
        self.n = n
        if diagonal:  # separated timescales, e.g. fast + slow leaky modes
            A = [[0.0] * n for _ in range(n)]
            for i in range(n):
                A[i][i] = 1.0 - 10 ** rng.uniform(-2.5, 0)
        else:
            A = [[rng.gauss(0, 1) for _ in range(n)] for _ in range(n)]
            nrm = max(sum(abs(v) for v in row) for row in A)
            rho = rng.uniform(0.3, 0.99)
            A = [[v * rho / nrm for v in row] for row in A]
        self.A = A
        self.B = [[rng.gauss(0, 1) for _ in range(2)] for _ in range(n)]
        self.C = [rng.gauss(0, 1) for _ in range(n)]
        self.D = [rng.gauss(0, 0.3) for _ in range(2)]

    def reset(self):
        self.x = [0.0] * self.n

    def get_state(self):
        return tuple(self.x)

    def set_state(self, s):
        self.x = list(s)

    def step(self, u):
        x = self.x
        A, B = self.A, self.B
        nx = [sum(A[i][j] * x[j] for j in range(self.n)) + B[i][0] * u[0] + B[i][1] * u[1]
              for i in range(self.n)]
        self.x = nx
        return sum(self.C[i] * nx[i] for i in range(self.n)) + self.D[0] * u[0] + self.D[1] * u[1]


class TwoTimescaleHab:
    """POSITIVE control: per-channel linear fading memory on a fast and a slow
    timescale, static ReLU output: y = sum_c relu(u_c - xf_c - xs_c).
    Set gf=0 or gs=0 for single-timescale ablations."""
    n_inputs = 2

    def __init__(self, tau_f=5.0, tau_s=100.0, gf=0.15, gs=0.04):
        self.af, self.as_ = 1.0 / tau_f, 1.0 / tau_s
        self.gf, self.gs = gf, gs

    def reset(self):
        self.xf = [0.0, 0.0]
        self.xs = [0.0, 0.0]

    def get_state(self):
        return (tuple(self.xf), tuple(self.xs))

    def set_state(self, s):
        self.xf, self.xs = list(s[0]), list(s[1])

    def step(self, u):
        y = 0.0
        for c in range(2):
            y += relu(u[c] - self.xf[c] - self.xs[c])
            self.xf[c] += -self.af * self.xf[c] + self.gf * u[c]
            self.xs[c] += -self.as_ * self.xs[c] + self.gs * u[c]
        return y


class GainDrift:
    """CHEAT C1: LTI response times a gain that decays with time, input-blind."""
    n_inputs = 2

    def __init__(self, rng, T=150.0):
        self.lti = LTI(rng)
        self.T = T

    def reset(self):
        self.lti.reset()
        self.t = 0

    def get_state(self):
        return (self.lti.get_state(), self.t)

    def set_state(self, s):
        self.lti.set_state(s[0])
        self.t = s[1]

    def step(self, u):
        y = self.lti.step(u) * math.exp(-self.t / self.T)
        self.t += 1
        return y


class GlobalFatigue:
    """CHEAT C2: one shared output resource R, depleted by ANY stimulus,
    recovering with tau_r. y = R * (u0 + u1). Habituation-like but not
    stimulus-specific (classic motor fatigue)."""
    n_inputs = 2

    def __init__(self, k=0.08, tau_r=80.0):
        self.k, self.ar = k, 1.0 / tau_r

    def reset(self):
        self.R = 1.0

    def get_state(self):
        return self.R

    def set_state(self, s):
        self.R = s

    def step(self, u):
        s = u[0] + u[1]
        y = self.R * s
        self.R += self.ar * (1.0 - self.R) - self.k * self.R * s
        return y


class IrreversibleDepletion:
    """CHEAT C3: per-channel resource that stimuli deplete and nothing restores."""
    n_inputs = 2

    def __init__(self, k=0.08):
        self.k = k

    def reset(self):
        self.R = [1.0, 1.0]

    def get_state(self):
        return tuple(self.R)

    def set_state(self, s):
        self.R = list(s)

    def step(self, u):
        y = 0.0
        for c in range(2):
            y += self.R[c] * u[c]
            self.R[c] -= self.k * self.R[c] * u[c]
        return y


class BaselineDrift:
    """CHEAT C4: LTI plus a downward, input-blind baseline drift."""
    n_inputs = 2

    def __init__(self, rng, slope=-0.01):
        self.lti = LTI(rng)
        self.slope = slope

    def reset(self):
        self.lti.reset()
        self.t = 0

    def get_state(self):
        return (self.lti.get_state(), self.t)

    def set_state(self, s):
        self.lti.set_state(s[0])
        self.t = s[1]

    def step(self, u):
        y = self.lti.step(u) + self.slope * self.t
        self.t += 1
        return y


class RandomNet:
    """NULL: leaky random recurrent net, every unit is an output.
    x_i' = (1-a_i) x_i + a_i f(sum_j W_ij x_j + B_i . u + b_i)
    f = tanh ('tanh') or clip(z, 0, 1) ('thresh'). a_i log-uniform [0.005, 1]."""
    n_inputs = 2

    def __init__(self, rng, n, kind):
        self.n, self.kind = n, kind
        g = rng.uniform(0.5, 3.0)
        self.W = [[rng.gauss(0, g / math.sqrt(n)) for _ in range(n)] for _ in range(n)]
        self.B = [[rng.gauss(0, 1) for _ in range(2)] for _ in range(n)]
        self.b = [rng.gauss(0, 0.5) for _ in range(n)]
        self.a = [10 ** rng.uniform(math.log10(0.005), 0) for _ in range(n)]
        self.ts_ratio = max(self.a) / min(self.a)

    def reset(self):
        self.x = [0.0] * self.n

    def get_state(self):
        return tuple(self.x)

    def set_state(self, s):
        self.x = list(s)

    def step(self, u):
        x, n = self.x, self.n
        nx = []
        for i in range(n):
            Wi = self.W[i]
            z = self.b[i] + self.B[i][0] * u[0] + self.B[i][1] * u[1]
            for j in range(n):
                z += Wi[j] * x[j]
            if self.kind == "tanh":
                f = math.tanh(z)
            else:
                f = 0.0 if z < 0 else (1.0 if z > 1 else z)
            nx.append((1 - self.a[i]) * x[i] + self.a[i] * f)
        self.x = nx
        return nx


class RandomQuadMap:
    """NULL: random 2-variable quadratic map, both variables are outputs.
    x' = A x + B u + Q [x1^2, x1 x2, x2^2]; A with inf-norm < 1."""
    n_inputs = 2

    def __init__(self, rng):
        A = [[rng.gauss(0, 1) for _ in range(2)] for _ in range(2)]
        nrm = max(sum(abs(v) for v in row) for row in A)
        rho = rng.uniform(0.3, 0.99)
        self.A = [[v * rho / nrm for v in row] for row in A]
        self.B = [[rng.gauss(0, 1) for _ in range(2)] for _ in range(2)]
        self.Q = [[rng.gauss(0, 0.3) for _ in range(3)] for _ in range(2)]
        self.c = [rng.gauss(0, 0.1) for _ in range(2)]

    def reset(self):
        self.x = [0.0, 0.0]

    def get_state(self):
        return tuple(self.x)

    def set_state(self, s):
        self.x = list(s)

    def step(self, u):
        x1, x2 = self.x
        m = (x1 * x1, x1 * x2, x2 * x2)
        nx = []
        for i in range(2):
            v = (self.c[i] + self.A[i][0] * x1 + self.A[i][1] * x2
                 + self.B[i][0] * u[0] + self.B[i][1] * u[1]
                 + self.Q[i][0] * m[0] + self.Q[i][1] * m[1] + self.Q[i][2] * m[2])
            nx.append(v)
        self.x = nx
        return nx


# ---------------------------------------------------------------- helpers
def summarize(outs):
    keys = ["r1", "dec_ratio", "tau", "sham_ratio", "dec_vs_sham", "rec_frac",
            "spec_ratio", "H1", "H2", "H3", "H4", "pass_core", "pass_full"]
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in outs.items() if k in keys}


def rate(k, n):
    lo, hi = wilson(k, n)
    return dict(k=k, n=n, rate=(k / n if n else None), ci95=[round(lo, 5), round(hi, 5)])


def main(out_path):
    t_start = time.time()
    with open(os.path.join(HERE, "assay.py"), "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    R = dict(assay_sha256=sha, frozen=FROZEN)

    # NEGATIVE: random LTI (dense and diagonal separated-timescale)
    rng = random.Random(20260927)
    neg = dict(counterfactual=dict(pass_full=0, pass_core=0, H1=0, valid=0),
               prestim=dict(pass_full=0, pass_core=0, H1=0, valid=0), n=0,
               max_abs_dec_dev=0.0)
    n_lti = 1000
    for i in range(n_lti):
        sysm = LTI(rng, diagonal=(i % 2 == 1))
        neg["n"] += 1
        for metric in ("counterfactual", "prestim"):
            a = run_assay(sysm, metric=metric)
            if not a["valid"]:
                continue
            o = a["outputs"][0]
            d = neg[metric]
            d["valid"] += 1
            d["H1"] += o["H1"]
            d["pass_core"] += o["pass_core"]
            d["pass_full"] += o["pass_full"]
            if metric == "counterfactual" and o["responsive"]:
                neg["max_abs_dec_dev"] = max(neg["max_abs_dec_dev"], abs(o["dec_ratio"] - 1))
    for metric in ("counterfactual", "prestim"):
        d = neg[metric]
        d["pass_full_rate"] = rate(d["pass_full"], d["valid"])
        d["H1_rate"] = rate(d["H1"], d["valid"])
        d["pass_core_rate"] = rate(d["pass_core"], d["valid"])
    R["negative_LTI"] = neg
    print("NEG", json.dumps(neg)[:400], flush=True)

    # POSITIVE: canonical + randomized family + single-timescale ablations
    pos = {}
    canon = TwoTimescaleHab()
    a = run_assay(canon)
    pos["canonical"] = summarize(a["outputs"][0])
    pos["canonical"]["rate_sensitivity"] = rate_sensitivity(canon)
    pos["ablation_slow_only"] = summarize(run_assay(TwoTimescaleHab(gf=0.0, gs=0.06))["outputs"][0])
    pos["ablation_slow_only"]["rate_sensitivity"] = rate_sensitivity(TwoTimescaleHab(gf=0.0, gs=0.06))
    pos["ablation_fast_only"] = summarize(run_assay(TwoTimescaleHab(gf=0.3, gs=0.0))["outputs"][0])
    pos["ablation_linear_output"] = "see note: removing ReLU makes it LTI -> covered by NEG theorem"
    rngp = random.Random(7)
    k = 0
    fails = []
    NP = 200
    for _ in range(NP):
        pr = dict(tau_f=rngp.uniform(2, 8), tau_s=rngp.uniform(50, 200),
                  gf=rngp.uniform(0.05, 0.3), gs=rngp.uniform(0.02, 0.08))
        o = run_assay(TwoTimescaleHab(**pr))["outputs"][0]
        if o["pass_full"]:
            k += 1
        elif len(fails) < 10:
            fails.append(dict(params={x: round(y, 3) for x, y in pr.items()}, **summarize(o)))
    pos["family"] = dict(pass_full=rate(k, NP), example_fails=fails)
    R["positive"] = pos
    print("POS", json.dumps(pos["canonical"]), pos["family"]["pass_full"], flush=True)

    # CHEATS
    rngc = random.Random(99)
    cheats = {}
    for name, factory in (("C1_gain_drift", lambda: GainDrift(rngc)),
                          ("C2_global_fatigue", lambda: GlobalFatigue()),
                          ("C3_irreversible_depletion", lambda: IrreversibleDepletion()),
                          ("C4_baseline_drift", lambda: BaselineDrift(rngc))):
        reps = 50 if name in ("C1_gain_drift", "C4_baseline_drift") else 1
        cnt = dict(pass_full=0, pass_core=0, H1=0, H2=0, H3=0, H4=0, valid=0)
        example = None
        for _ in range(reps):
            a = run_assay(factory())
            if not a["valid"]:
                continue
            o = a["outputs"][0]
            cnt["valid"] += 1
            for g in ("pass_full", "pass_core", "H1", "H2", "H3", "H4"):
                cnt[g] += bool(o[g])
            if example is None:
                example = summarize(o)
        cheats[name] = dict(counts=cnt, n=reps, example=example)
        print("CHEAT", name, cnt, flush=True)
    R["cheats"] = cheats

    # NULL: random nonlinear systems
    rngn = random.Random(314159)
    classes = []
    for kind in ("tanh", "thresh"):
        for n in (2, 3, 4, 6):
            classes.append((f"{kind}_n{n}", lambda kind=kind, n=n: RandomNet(rngn, n, kind), 500))
    classes.append(("quadmap_2var", lambda: RandomQuadMap(rngn), 1000))
    null = {}
    tot = dict(primary=0, primary_core=0, best_of_k=0, n=0, valid=0, responsive=0)
    strat = {}  # timescale-ratio strata for nets
    passers = []
    for cname, factory, NN in classes:
        c = dict(n=NN, valid=0, responsive=0, primary=0, primary_core=0, best_of_k=0,
                 gate_counts=dict(H1=0, H2=0, H3=0, H4=0), k_tests=0)
        t0 = time.time()
        for idx in range(NN):
            sysm = factory()
            a01 = run_assay(sysm, ch_a=0, ch_b=1)
            if not a01["valid"]:
                continue
            c["valid"] += 1
            o = a01["outputs"][0]
            c["responsive"] += o["responsive"]
            for g in ("H1", "H2", "H3", "H4"):
                c["gate_counts"][g] += bool(o[g])
            c["primary"] += o["pass_full"]
            c["primary_core"] += o["pass_core"]
            a10 = run_assay(sysm, ch_a=1, ch_b=0)
            outs = list(a01["outputs"]) + (list(a10["outputs"]) if a10["valid"] else [])
            c["k_tests"] = max(c["k_tests"], len(outs))
            anyp = any(x["pass_full"] for x in outs)
            c["best_of_k"] += anyp
            if hasattr(sysm, "ts_ratio"):
                sk = "ts_ratio<10" if sysm.ts_ratio < 10 else ("10-100" if sysm.ts_ratio < 100 else ">=100")
                s = strat.setdefault(sk, dict(n=0, primary=0))
                s["n"] += 1
                s["primary"] += o["pass_full"]
            if o["pass_full"] and len(passers) < 15:
                passers.append(dict(cls=cname, idx=idx, **summarize(o)))
        c["primary_rate"] = rate(c["primary"], c["valid"])
        c["primary_core_rate"] = rate(c["primary_core"], c["valid"])
        c["best_of_k_rate"] = rate(c["best_of_k"], c["valid"])
        c["primary_rate_among_responsive"] = rate(c["primary"], c["responsive"])
        c["seconds"] = round(time.time() - t0, 1)
        null[cname] = c
        for key in ("primary", "primary_core", "best_of_k", "valid", "responsive"):
            tot[key] += c[key]
        tot["n"] += NN
        print("NULL", cname, c["valid"], c["responsive"], c["primary"], c["primary_core"],
              c["best_of_k"], c["seconds"], flush=True)
    for s in strat.values():
        s["rate"] = rate(s["primary"], s["n"])
    R["null"] = dict(per_class=null, pooled=dict(
        primary_full=rate(tot["primary"], tot["valid"]),
        primary_core=rate(tot["primary_core"], tot["valid"]),
        best_of_k_full=rate(tot["best_of_k"], tot["valid"]),
        primary_full_among_responsive=rate(tot["primary"], tot["responsive"]),
        n=tot["n"], valid=tot["valid"], responsive=tot["responsive"]),
        net_timescale_strata=strat, example_passers=passers)
    print("POOLED", json.dumps(R["null"]["pooled"]), flush=True)

    # NULL ISI sweep (secondary): first 150 systems of each net class, regenerated
    sweep = {}
    for isi in (5, 20):
        rs = random.Random(271828)
        k = n = 0
        for kind in ("tanh", "thresh"):
            for nn in (2, 3, 4, 6):
                for _ in range(150):
                    a = run_assay(RandomNet(rs, nn, kind), ISI=isi)
                    if a["valid"]:
                        n += 1
                        k += a["outputs"][0]["pass_full"]
        sweep[f"ISI={isi}"] = rate(k, n)
    R["null"]["isi_sweep_nets"] = sweep
    print("SWEEP", sweep, flush=True)

    R["seconds_total"] = round(time.time() - t_start, 1)
    with open(out_path, "w") as f:
        json.dump(R, f, indent=1)
    print("wrote", out_path, R["seconds_total"], "s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results.json"))
