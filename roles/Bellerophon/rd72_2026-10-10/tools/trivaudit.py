"""BEL-RD-72 B2 triviality audit (measurement only; no world is run).   python3 trivaudit.py OUT.json [N_RANDOM]
Per task (CONST, ECHO, INC, COND_ONE, COND_MULTI, SUM2), under the v3 competence check (tasks.verify_exact, 16-input panel,
read gate ABR, budget 256) and FUNC (belinst.Func):
  density      fraction of N uniform-random 64-byte tapes, and of N SPARSE random tapes (random first 16 bytes, rest 0),
               that are competent / competent AND FUNC (random success, constant / accidental outputs)
  ladder       one-step routes (SUB / MOVE / INS / DEL, geometry.scan_operators) from the copier+task hybrid of every OTHER
               task (and from the bare copier) to a competent FUNC tape: single-mutation solvability and the
               task-to-task distance graph
  witness      the shortest known solver (instruction bytes after IN) -- a program-length floor
  const        does any constant-output tape (LD A,k; OUT) pass the panel (k = 0..255)?"""
import json, random, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from belinst import Func
from prometheus.z80atlas import vm, geometry, tasks, coupling_campaign as CC
from prometheus.z80atlas.world import Config
TASKS = ("CONST", "ECHO", "INC", "COND_ONE", "COND_MULTI", "SUM2")
W = {"CONST": vm.witness_const(42), "ECHO": vm.witness_echo(), "INC": vm.witness_inc(), "COND_ONE": vm.witness_cond_one(),
     "COND_MULTI": vm.witness_cond_multi(), "SUM2": vm.witness_sum2()}
L = 64


def pad(b):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


def main(outp, N=20000):
    d = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); d.update(coupling="ON", budget=256); cfg = Config(**d); func = Func(cfg)
    rng = random.Random(7206); out = {}
    rand = [bytes(rng.randrange(256) for _ in range(L)) for _ in range(N)]
    sparse = [pad(bytes(rng.randrange(256) for _ in range(16))) for _ in range(N)]
    rep = pad(vm.replicator(L))
    for t in TASKS:
        task = tasks.Task(t)
        comp = lambda x: tasks.verify_exact(x, L, task, "ABR", budget=256)
        both = lambda x: comp(x) and func(x)
        r = {"witness_bytes": len(W[t]) - 1, "density": {}}
        for name, pool in (("uniform", rand), ("sparse16", sparse)):
            c = [x for x in pool if comp(x)]
            r["density"][name] = {"n": N, "competent": len(c), "competent_func": sum(1 for x in c if func(x))}
        r["const_passes"] = [k for k in range(256) if comp(pad(vm.witness_const(k)))]
        lad = {}
        srcs = {"COPIER": rep, **{s: pad(vm.hybrid_relocated(vm.replicator(L), W[s])) for s in TASKS if s != t}}
        for s, tape in srcs.items():
            assert func(tape), s
            lad[s] = {op: v["routes"] for op, v in geometry.scan_operators(tape, L, both, ops=("SUB", "MOVE", "INS", "DEL")).items()}
        r["ladder_from"] = lad
        out[t] = r; print(t, json.dumps(r), flush=True)
    json.dump(out, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20000)
