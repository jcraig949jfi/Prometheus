"""W2-T step 3: combined light-cone + WAKE bound (W2-O Q2), analytic, no engine runs.

H-PLANT lightcone.py semantics (fastest transport: no loss/caps/energy, jitter 0, every neighbour reachable, a site
relays at its first awake tick, inbox latches while asleep -- engine.py step 1 accumulates Acc_sum/Acc_cnt and only
clears them on an awake tick), with ONE change: the wake schedule is the engine's exact per-site per-tick WAKE mask
(rng.WAKE hash, the same recomputation W2-O verified against engine stats["awake"]), instead of "async could wake
any tick". SENSE is never latched (engine step 2 writes `sense` for the current tick only), so a cue is picked up
only on an awake tick that carries a non-zero cue value.

Per trial: information from sensor s reaches actuator a iff the earliest processing tick at a <= readout tick.
  RELAY/FLIP: sensor 0 (FLIP teacher ignored -> still an upper bound);  HOLD: sensor == actuator;
  XOR: both sensors;  MAJ: r = number of sensors in reach, Bayes ceiling of majority-of-received under flip_p
  (y = x, independent flips; ties -> .5).  MAJ "any" (W2-O's looser rule) is reported too.
Cell bound = mean over worlds of (.5 + .5 * frac_scored_in_reach)  (MAJ: mean Bayes value).
Modes: opt = H-PLANT wake rule (sync periodic, async always awake);  exact = engine wake mask.
Self-check: mode opt on H-PLANT's own seeds (SCORE_NS, M=64) must reproduce lc_census.json bounds exactly.
Usage: python lcwake.py selfcheck | python lcwake.py run|signal <bi> <nb>"""
import os, sys, json, gzip, pathlib, time, math
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import torch  # noqa: E402
assert not torch.cuda.is_available()
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, topology, rng  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402

SCORE_NS = 0x48504C54   # H-PLANT hp_common.SCORE_NS
INF = 10 ** 9
ROWS = {}
for _l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    _r = json.loads(_l)
    ROWS[_r["cell_id"]] = _r


def edges(ph):
    N = ph.n_sites
    nbr, dist = topology.build(ph)
    if nbr is None:
        U, V = np.nonzero(1 - np.eye(N, dtype=np.int64))
        D = np.ones_like(U)
    else:
        U = np.repeat(np.arange(N), nbr.shape[1])
        V = nbr.reshape(-1)
        D = dist.reshape(-1)
    delay = np.maximum(1, ph.lat_base + ph.lat_hop * D)
    o = np.argsort(V, kind="stable")
    return U[o], V[o], delay[o]


def wake(ph, lead_seeds, T, mode):
    """[W, T, N] bool."""
    W, N = len(lead_seeds), ph.n_sites
    if ph.update_mode == "sync":
        a = (np.arange(T) % ph.update_period == 0)
        return np.broadcast_to(a[None, :, None], (W, T, N)).copy()
    if mode == "opt":
        return np.ones((W, T, N), dtype=bool)
    ws = torch.as_tensor(np.asarray(lead_seeds, dtype=np.int64))
    st = torch.as_tensor(np.arange(N, dtype=np.int64))
    p = ph.p16(ph.update_p)
    out = np.zeros((W, T, N), dtype=bool)
    for t in range(T):
        hw = rng.chain(rng.site_base(ws, rng.WAKE, t, st), 0)
        out[:, t] = ((hw & 0xFFFF) < p).numpy()
    return out


def next_awake_table(aw):
    """nxt[w, t, v] = smallest t' >= t with aw[w, t', v], else INF; t in [0, T] (row T = INF)."""
    W, T, N = aw.shape
    nxt = np.full((W, T + 1, N), INF, dtype=np.int64)
    for t in range(T - 1, -1, -1):
        nxt[:, t] = np.where(aw[:, t], t, nxt[:, t + 1])
    return nxt


def maj_bayes(r, p):
    """P(correct) of the majority of r received noisy copies (each correct w.p. 1-p), ties -> .5."""
    q = 1 - p
    s = 0.0
    for j in range(r + 1):
        pr = math.comb(r, j) * q ** j * p ** (r - j)
        s += pr * (1.0 if 2 * j > r else 0.5 if 2 * j == r else 0.0)
    return s


def bound(r, seeds, mode):
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    fam = env.family
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    sval = ep.schedule.sense_val.numpy()
    T = sval.shape[0]
    B = len(seeds)
    lead = list(range(0, B, 2))                           # mirror twins share positions and wake seeds
    aw = wake(ph, [seeds[b] for b in lead], T, mode)
    nxt = next_awake_table(aw)
    U, V, Dl = edges(ph)
    Kneed = {"RELAY": 1, "FLIP": 1, "HOLD": 1, "XOR": 2, "MAJ": env.n_maj}[fam]
    Pd = env.period()
    tr = env.trials
    # queries: (pair w, trial k, sensor j)
    qw, qk, qj, qs, qt = [], [], [], [], []
    for wi, b in enumerate(lead):
        for k in range(tr):
            t0 = k * Pd
            for j in range(Kneed):
                s = int(sidx[b, j])
                ts = np.arange(t0, min(t0 + env.cue_len, T))
                live = ts[sval[ts, b, j] != 0]
                aws = live[aw[wi, live, s]]
                qw.append(wi); qk.append(k); qj.append(j); qs.append(s)
                qt.append(int(aws[0]) if aws.size else INF)
    qw = np.asarray(qw); qs = np.asarray(qs); qt = np.asarray(qt)
    Q, N = len(qw), ph.n_sites
    best = np.full((Q, N), INF, dtype=np.int64)
    best[np.arange(Q), qs] = qt
    cap = T                                                 # nxt row T is INF
    bounds_v = np.r_[0, np.flatnonzero(np.diff(V)) + 1]     # V sorted: segment starts
    Vu = V[bounds_v]
    CH = max(1, 2_000_000 // len(U))                        # query chunk (memory)
    for c0 in range(0, Q, CH):
        sl = slice(c0, min(Q, c0 + CH))
        bq, wq = best[sl], qw[sl]
        for _ in range(4 * N + 8):
            arr = np.minimum(bq[:, U] + Dl[None, :], cap)
            cand = nxt[wq[:, None], arr, V[None, :]]
            cmin = np.minimum.reduceat(cand, bounds_v, axis=1)
            newv = np.minimum(bq[:, Vu], cmin)
            if np.array_equal(newv, bq[:, Vu]):
                break
            bq[:, Vu] = newv
        else:
            raise RuntimeError("no convergence")
        best[sl] = bq
    a_q = ridx[np.asarray(lead)[qw]]
    ro_q = ep.ro_tick[np.asarray(lead)[qw], np.asarray(qk)]
    ok = best[np.arange(Q), a_q] <= ro_q                    # [Q]
    ok = ok.reshape(len(lead), tr, Kneed)
    sc = ep.scored[lead]
    out = {}
    if fam == "MAJ":
        nr = ok.sum(-1)
        bay = np.vectorize(lambda x: maj_bayes(int(x), env.flip_p))(nr)
        out["bound"] = float(((bay * sc).sum(1) / sc.sum(1)).mean())
        fany = (ok.any(-1) & sc).sum(1) / sc.sum(1)
        out["bound_any"] = float((0.5 + 0.5 * fany).mean())
        out["bayes_full_info"] = maj_bayes(env.n_maj, env.flip_p)
        out["mean_sensors_in_reach"] = float((nr * sc).sum() / sc.sum())
    else:
        f = (ok.all(-1) & sc).sum(1) / sc.sum(1)
        out["bound"] = float((0.5 + 0.5 * f).mean())
    return out


def selfcheck():
    lc = json.load(open(ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))["rows"]
    g = np.random.default_rng(7)
    pick = [lc[i] for i in g.choice(len(lc), 40, replace=False)]
    pick += [x for x in lc if x["bound"] < 0.9][:20]
    seeds = assays.world_seeds(SCORE_NS, 64)
    bad = 0
    for x in pick:
        b = bound(ROWS[x["cell"]], seeds, "opt")["bound"]
        okk = abs(b - x["bound"]) < 1e-12
        bad += not okk
        if not okk:
            print("MISMATCH", x["cell"], x["family"], x["update_mode"], x["bound"], b)
    print(f"selfcheck: {len(pick) - bad}/{len(pick)} exact")
    return bad


def run(bi=0, nb=1, signal=False):
    t0 = time.process_time()
    if signal:   # negative control: recorded SIGNAL evolve cells must satisfy held acc <= bound
        cells = [{"cell": k, "family": v["env"]["family"]} for k, v in sorted(ROWS.items())
                 if v["kind"] == "evolve" and v["result"]["held"]["lo99"] > 0.55]
    else:
        cells = json.load(open(HERE / "out/cells.json"))
    cells = cells[bi::nb]
    lc = {x["cell"]: x["bound"] for x in json.load(open(
        ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))["rows"]}
    sseeds = assays.world_seeds(SCORE_NS, 64)
    out = []
    for c in cells:
        r = ROWS[c["cell"]]
        hseeds = assays.world_seeds(H_int(r["search_seed"], HELD_NS), r["search"]["M_held"])
        o = {"cell": c["cell"], "family": c["family"], "update_mode": r["physics"]["update_mode"],
             "update_p": r["physics"]["update_p"], "topology": r["physics"]["topology"],
             "lc_census": lc.get(c["cell"]), "held_acc": r["result"]["held"]["acc"],
             "held_opt": bound(r, hseeds, "opt"), "held_exact": bound(r, hseeds, "exact"),
             "score_exact": bound(r, sseeds, "exact")}
        out.append(o)
        print(json.dumps(o), flush=True)
    (HERE / f"out/lcwake_{'sig' if signal else 'null'}_b{bi}of{nb}.json").write_text(json.dumps({"rows": out, "cpu_s": round(time.process_time() - t0, 1)},
                                                     indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "selfcheck":
        selfcheck()
    else:
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[1] == "signal")
