"""W-A condition table shared by the model predictions and the engine runs."""
import dataclasses
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
from prometheus.ananke import c1b_run  # noqa: E402
import echo_model as em  # noqa: E402

GAPS = list(range(2, 17))
SPEC = "4ab2ba014aac967e"


def base():
    ph, env, g, _ = c1b_run.load(SPEC)
    ch = json.loads((REPO / "roles/Ananke/research/spikes/out/champions_m2.json").read_text())
    genomes = {k: np.asarray(v, dtype=np.int64) for k, v in ch.items()}
    assert np.array_equal(genomes["4ab2ba01"], g)
    return ph, env, genomes


def pipe(g, name):
    """S0 := S1 at line 0; the echo line writes S1 instead of S0 (2 field edits)."""
    g = g.copy()
    g[0, 0] = [1, 0, 1, 0, 0]
    line = {"4ab2ba01": 9, "fresh3": 15}[name]
    g[0, line, 1] = 1
    return g


def canon(ph, specimen_route: bool):
    """Minimal echo genome: EMIT const, PAY0 := SENSE, PAY1 := IN0_0, S0 := IN0_1."""
    L = ph.prog_len
    g = np.zeros((1, L, 5), dtype=np.int64)
    rows = [(6, 6, 0, 1, 62), (1, 10, 15, 0, 0), (1, 11, 12, 0, 0), (1, 0, 13, 0, 0)]
    if specimen_route:
        rows += [(6, 8, 0, 6, -112), (6, 9, 0, 0, -1)]
    for i, r in enumerate(rows):
        g[0, i] = r
    return g


def conditions():
    """-> list of (cond, champ, physics, env, genome, Prog)."""
    ph, env, G = base()
    out = []
    phys = {
        "base": {}, "lb0": {"lat_base": 0}, "lb2": {"lat_base": 2}, "lh2": {"lat_hop": 2},
        "j0": {"lat_jitter": 0}, "j2": {"lat_jitter": 2}, "up1": {"update_period": 1},
        "up3": {"update_period": 3}, "r2": {"radius": 2}, "pr0": {"plastic_route": 0},
    }
    for cond, kw in phys.items():
        p2 = ph.replace(**kw)
        for name, g in G.items():
            prog = em.PROGS[name]
            if cond == "pr0":
                prog = dataclasses.replace(prog, route="uniform")
            out.append((cond, name, p2, env, g, prog))
    for name, g in G.items():
        out.append(("ad0", name, ph, dataclasses.replace(env, amp_dist=0), g, em.PROGS[name]))
    for name in ("4ab2ba01", "fresh3"):
        pg = pipe(G[name], name)
        out.append(("pipe", name, ph, env, pg, dataclasses.replace(em.PROGS[name], pipeline=1)))
        out.append(("pipe_lb0", name, ph.replace(lat_base=0), env, pg,
                    dataclasses.replace(em.PROGS[name], pipeline=1)))
    out.append(("canon", "uniform", ph, env, canon(ph, False), em.Prog()))
    out.append(("canon", "specimen", ph, env, canon(ph, True), em.Prog(route="specimen")))
    return out
