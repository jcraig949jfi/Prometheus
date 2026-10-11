"""C-016-T030 native assay: one Ensorain lifetime -> one row of integers, with the external declared-memory check
and a recompute of the native accuracies (PREREGISTRATION.md s4-s5).

Read-only against ensorain/: tape.lifetime (ensorain/wtp5/tape.py:298) runs every life. Two observers are attached
for the duration of a life and change nothing it computes: world.block (worlds.py:254) is wrapped to keep each
block's episodes, and tape.run_block (tape.py:166) is called with a `record` dict (its native per-step working-state
record) to keep the actions and the working state at step 0 of every block.

    python -m rso.ensorain.assay dev <out.json>                       development seeds only
    python -m rso.ensorain.assay confirm <out.json> --subjects <SUBJECTS.json> --n N --cleared-by <ref>
                                                                      refuses unless the freeze manifest matches
"""
import argparse
import json
import platform
import sys
from contextlib import contextmanager
from unittest import mock

import numpy as np

from ensorain.wtp5 import tape
from ensorain.wtp5.worlds import make
from rso.slice001.receipt import sha256_hex
from rso.ensorain import subjects as S

SPEC = "C-R2-desert"
K = 64                                   # episodes per block, as certify.py:72 and T020
ARMS = ("full", "frozen", "shuffle", "newlife")
FIELDS = ("v", "M", "u", "w")


@contextmanager
def _observe(world, log):
    real_block, real_run = world.block, tape.run_block

    def block(K_, rng, b=0):
        ep = real_block(K_, rng, b)
        log.append(dict(ep=ep))
        return ep

    def run_block(g, obs, rng=None, eps_scale=None, pmap=None, mod_pmaps=None, record=None, ws_reset=False):
        rec = {} if record is None else record
        acts = real_run(g, obs, rng, eps_scale, pmap, mod_pmaps, rec, ws_reset)
        log[-1].update(acts=acts, z0_zero=bool(np.all(rec["z"][:, 0] == 0)))
        return acts

    world.block = block
    try:
        with mock.patch.object(tape, "run_block", run_block):
            yield
    finally:
        del world.block


def _declared(g, plastic):
    on = plastic and g.get("eta", 0) > 0 and g.get("sigma", 0) > 0          # tape.py:305
    return set(tape.plastic_keys(g)) if on else set()


def memory_check(g_in, g_out, plastic):
    """True iff the genome after the life differs from the input only at its declared plastic keys, which stay
    within PLASTIC_BOUND and keep their shape. Returns (ok, number of floats allowed to cross the block boundary)."""
    keys = _declared(g_in, plastic)
    if set(g_in) != set(g_out) or len(g_in["modules"]) != len(g_out["modules"]):
        return False, 0
    if any(g_in[k] != g_out[k] for k in g_in if k not in ("nodes", "modules")):
        return False, 0
    graphs = [(-1, g_in["nodes"], g_out["nodes"])]
    graphs += [(mi, a["nodes"], b["nodes"]) for mi, (a, b) in enumerate(zip(g_in["modules"], g_out["modules"]))]
    for mi, (a, b) in enumerate(zip(g_in["modules"], g_out["modules"])):
        if {k: v for k, v in a.items() if k != "nodes"} != {k: v for k, v in b.items() if k != "nodes"}:
            return False, 0
    for where, na, nb in graphs:
        if len(na) != len(nb):
            return False, 0
        for i, (x, y) in enumerate(zip(na, nb)):
            if set(x) != set(y):
                return False, 0
            for f in x:
                xa, ya = x[f], y[f]
                if f in FIELDS and (where, i, f) in keys:
                    ya = np.asarray(ya)
                    if ya.shape != np.shape(xa) or np.any(np.abs(ya) > tape.PLASTIC_BOUND):
                        return False, 0
                elif isinstance(xa, np.ndarray) or isinstance(ya, np.ndarray):
                    if not (isinstance(xa, np.ndarray) and isinstance(ya, np.ndarray) and np.array_equal(xa, ya)):
                        return False, 0
                elif xa != ya:
                    return False, 0
    return True, int(sum(np.asarray(tape._param(g_in, *k)).size for k in keys))


def _one(g, seed, plastic, shuffle):
    rng = np.random.default_rng(seed)
    w = make(SPEC)
    w.new_life(rng)
    log = []
    with _observe(w, log):
        out = tape.lifetime(g, w, rng, plasticity=plastic, K=K, history_shuffle=shuffle)
    return w.sw, log, out


def _counts(sw, log, out):
    c = dict(c_pre=0, n_pre=0, c_early=0, n_early=0, c_late=0, n_late=0, c5=0, n5=0, c5_post=0, n5_post=0)
    ok = len(log) == len(out["blocks"]) and all("acts" in x for x in log)
    tot = {}
    for b, (x, nat) in enumerate(zip(log, out["blocks"])):
        ep, acts = x["ep"], x["acts"]
        corr = (acts == ep["tgt"]) & (ep["tgt"] != 0)
        for rl in np.unique(ep["role"]):
            if rl == 0:
                continue
            m = ep["role"] == rl
            ok &= nat["acc"].get(int(rl)) == float(corr[m].mean())                   # tape.py:341, recomputed
            t = tot.setdefault(int(rl), [0, 0])
            t[0], t[1] = t[0] + int(corr[m].sum()), t[1] + int(m.sum())
        m1, m5 = ep["role"] == 1, ep["role"] == 5
        win = "pre" if b < sw else ("early" if b < sw + 3 else "late")
        c["c_" + win] += int(corr[m1].sum())
        c["n_" + win] += int(m1.sum())
        c["c5"], c["n5"] = c["c5"] + int(corr[m5].sum()), c["n5"] + int(m5.sum())
        if b >= sw:
            c["c5_post"], c["n5_post"] = c["c5_post"] + int(corr[m5].sum()), c["n5_post"] + int(m5.sum())
    ok &= all(out["role_n"].get(k) == v[1] and out["roles"].get(k) == v[0] / max(1, v[1]) for k, v in tot.items())
    return c, bool(ok), all(x.get("z0_zero", False) for x in log)


def life(g, arm, seed):
    """One lifetime of genome g under an arm -> a row of ints / bools / strings (receipt-canonical)."""
    plastic, shuffle = arm in ("full", "shuffle", "newlife"), arm == "shuffle"
    g_in = g
    if arm == "newlife":                     # a NEW life from the learned parameters; not a resume (none exists)
        _, log0, out0 = _one(g, seed, True, False)
        ok0, _ = memory_check(g, out0["learned"], True)
        g_in = out0["learned"]
    sw, log, out = _one(g_in, seed, plastic, shuffle)
    c, rec_ok, z_ok = _counts(sw, log, out)
    mem_ok, n_car = memory_check(g_in, out["learned"], plastic)
    if arm == "newlife":
        mem_ok &= ok0 and all(x.get("z0_zero", False) for x in log0)
    return dict(arm=arm, seed=int(seed), sw=int(sw), subject_hash=tape.ghash(g), n_carried=n_car,
                memory_ok=bool(mem_ok and z_ok), recompute_ok=rec_ok, **c)


def run(subs, arms, seeds):
    return [dict(subject=name, **life(g, arm, s)) for name, g in subs.items() for arm in arms for s in seeds]


def preflight(subs, seeds):
    """Instrument checks only, for subjects whose endpoint must stay unobserved before the freeze: the rows are
    built and discarded; only memory_ok and recompute_ok leave this function."""
    out = {}
    for name, g in subs.items():
        rows = [life(g, arm, s) for arm in ARMS for s in seeds]
        out[name] = dict(memory_ok=all(r["memory_ok"] for r in rows), recompute_ok=all(r["recompute_ok"] for r in rows))
    return out


def rows_sha256(rows):
    return sha256_hex(rows)


def environment():
    return dict(host=platform.node(), python=platform.python_version(), numpy=np.__version__)


def controls():
    """Instrument controls that run beside every subject set (PREREGISTRATION.md s3)."""
    return {"reference": S.reference(), "smuggler": S.smuggler(), "smuggler_decorative": S.smuggler_decorative(),
            "memoryless_plus": S.memoryless(+1), "constant_plus": S.constant(+1), "constant_minus": S.constant(-1)}


def main(argv=None):
    from rso.ensorain import analysis, freeze
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("dev", "confirm"))
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--subjects")
    ap.add_argument("--cleared-by")
    a = ap.parse_args(argv)
    subs = controls()
    extra = {}
    if a.mode == "dev":
        from ensorain.wtp5.nulls import ladder
        seeds = [S.DEV[0] + i for i in range(a.n)]
        extra["ladder"] = ladder(make(SPEC), S.LADDER)          # N1-N4 on role 1 / role 5 (development only)
    else:
        bad = freeze.mismatches() + freeze.env_mismatches(environment())
        if bad or not a.cleared_by or not a.subjects or a.n != S.N_CONFIRM:
            sys.exit("REFUSED: %s" % (bad or "confirm needs --subjects, --cleared-by and --n %d" % S.N_CONFIRM))
        subs.update(S.load_searched(a.subjects))
        seeds = [S.CONFIRM0 + i for i in range(a.n)]
    rows = run(subs, ARMS, seeds)
    res = dict(schema="prometheus.rso.ensorain.assay.v1", mode=a.mode, spec=SPEC, K=K, seeds=[seeds[0], seeds[-1]],
               environment=environment(), cleared_by=a.cleared_by, rows_sha256=rows_sha256(rows), rows=rows,
               verdicts=analysis.report(rows, a.n, searched=[n for n in subs if n.startswith("searched_")]), **extra)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    for name, v in res["verdicts"].items():
        print(name, v["verdict"])


if __name__ == "__main__":
    main()
