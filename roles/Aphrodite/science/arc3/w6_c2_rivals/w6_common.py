"""ARC3 W6 -- shared helpers (forensic; frozen C2 data read-only).
Extensional cover: schema S COVERS family F=(init, body, final) iff some W5
instance b of S, some init i in H1_SPACE and some final f in FINAL_SPACE give a
program ('fold', i, b, f) equal to F's witness on every input of a fixed
task-domain battery (100 inputs drawn exactly as a17.Prov.task draws them:
xs of length SEARCH_LENGTHS=(4,9), values 2..30, query 3..97) where F's
witness is defined. This is what an entry [schema_entry(S)] can express."""
import json
import os
import random
import sys
from pathlib import Path

os.environ["A17_FASTEVAL"] = "1"
os.environ["A18_FASTCOST"] = "1"
os.environ.setdefault("A18_TAG", "A19")
HERE = Path(__file__).resolve().parent
ROLE = HERE.parents[2]
ENG = ROLE / "engine"
C2 = ENG / "A19_C2"
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(ENG / "accel"))
sys.path.insert(0, str(ROLE / "science" / "compounding" / "rb1"))
import a18                      # noqa: E402
a18.worker_init()
from a18 import a17, G, FR, I, T3D   # noqa: E402
import fasteval as FE           # noqa: E402

FAIL = FE._FAIL


def battery(n=100, seed="ARC3/W6/BATTERY/v1", lr=G.SEARCH_LENGTHS):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        xs = [rng.randint(2, 30) for _ in range(rng.randint(*lr))]
        out.append(xs + [rng.randint(3, 97)])
    return out


BAT = battery()
PINFO = [(n[:-1], n[0], n[-1], n[:-1][-1]) for n in BAT]
FINALS = list(G.FINAL_SPACE)
FFN = [(f, FE.fn(f)) for f in FINALS]
_ACC = {}


def accvec(init, body):
    k = (init, body)
    r = _ACC.get(k)
    if r is None:
        ifn, bfn = FE.fn(init), FE.fn(body)
        r = tuple(FE._fold_acc(ifn, bfn, vals, f, l) for vals, f, l, _vl in PINFO)
        _ACC[k] = r
    return r


class Fam:
    def __init__(self, name, body, final, init):
        self.name, self.spec = name, (body, final, init)
        prog = ("fold", init, body, final)
        g = [FE.run_program(prog, n, True) for n in BAT]
        self.idx = [k for k, x in enumerate(g) if x is not None]
        self.gold = [g[k] for k in self.idx]
        self.memo = {}

    def match_acc(self, av):
        """Some final maps this acc vector to the gold on every defined input."""
        key = tuple(av[k] for k in self.idx)
        r = self.memo.get(key)
        if r is not None:
            return r
        r = False
        if not any(a is FAIL for a in key):
            for f, ffn in FFN:
                ok = True
                for a, k, gd in zip(key, self.idx, self.gold):
                    _v, fs, ls, vl = PINFO[k]
                    if FE._final(ffn, a, vl, fs, ls) != gd:
                        ok = False
                        break
                if ok:
                    r = f
                    break
        self.memo[key] = r
        return r

    def covered_by_bodies(self, bodies):
        for b in bodies:
            for i in G.H1_SPACE:
                f = self.match_acc(accvec(i, b))
                if f:
                    return ("fold", i, b, f)
        return None


def covers(schema, fam):
    return fam.covered_by_bodies(T3D.instantiate(schema))


def rd_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def c2_data():
    roles = json.load(open(C2 / "A18_ROLES_2026-09-28.json", encoding="utf-8"))
    panel = json.load(open(C2 / "A18_PANEL_2026-09-28.json", encoding="utf-8"))["panel"]
    donors = rd_jsonl(C2 / "A18_DONORS_2026-09-28.jsonl")
    trans = rd_jsonl(C2 / "A18_TRANSFER_2026-09-28.jsonl")
    return roles, panel, donors, trans


def wr(name, obj):
    (HERE / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
